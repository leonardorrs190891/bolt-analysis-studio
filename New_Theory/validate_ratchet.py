"""Validacao do ratcheting cinematico contra o modo collapse-missed (28/46).

Config: pack §4.12 + c_bend PER-RIG (proveniencia declarada — Lu: bracketado pelo
proprio amp-sweep fig18 [0.25 nao colapsa, 0.5 colapsa => delta_t~0.3mm => c~0.7];
Karlsen: 1mm colapsa => delta_t<1mm => c~2.5, dentro da banda de viga; demais: 0.3
do probe §4.12) + k_ratchet calibrado em UMA curva (lu fig20_T22) e CONGELADO.
Reavalia as 46 curvas, reclassifica modos, compara com library_error_modes.json.

Run: python New_Theory/validate_ratchet.py   (~5 min)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
import transfer_validation as tv  # noqa: E402
from library_error_modes import classify  # noqa: E402
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)
from library_common import geometry_for, emb_depth_vdi, frozen_constants, load_full_curve  # noqa: E402

C_BEND_RIG = {"LU_2024": 0.7, "KARLSEN_2022": 2.5}     # per-rig c/ proveniencia; default 0.3
CAL_STEM = "lu2024_M8_fig20_T22Nm"                      # curva de calibracao do k_ratchet


def simulate(case, k_ratchet):
    inp = tv.inputs_for(case)
    consts, _ = frozen_constants()
    emb_m, _ = emb_depth_vdi(inp["rz"]["value"], 1)
    geom = geometry_for(case.bolt_size, grip_mm=inp["grip_mm"]["value"])
    mu = inp["mu"]["value"]
    mat = JointMaterial(emb_depth=emb_m, mu_thread=mu, mu_bearing=mu,
                        conform_driver="effective",
                        slip_regime_mode="cattaneo_mindlin", slip_regime_sharpness=1.0,
                        k_tr_mode="bending",
                        c_bend=C_BEND_RIG.get(case.source.name, 0.30),
                        loose_torsion_mode="bolt_torsion", eta_loose=15.0,
                        loose_arrest_floor=0.08, k_ratchet=k_ratchet, **consts)
    F0 = case.initial_preload_N
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    cyc, ratio = load_full_curve(case.reference_csv_path)
    keep = ratio >= tv.FLOOR_TRIM
    cyc_d, r_d = cyc[keep], ratio[keep]
    n0, r_al = cyc_d[0], (ratio[keep] / ratio[keep][0])
    n_max = int(cyc_d[-1])
    delta = case.transverse_displacement_mm * 1e-3
    F_amp = inp["F_amp_N"]["value"]
    r = np.empty(n_max + 1); r[0] = 1.0
    for n in range(1, n_max + 1):
        ana.step_cycle(F_amp, np.pi / 2, case.frequency_Hz, delta_amp=delta)
        r[n] = max(ana.state.F_0, 0.0) / F0
    r_alm = r / max(np.interp(n0, np.arange(n_max + 1), r), 1e-9)
    pred = np.interp(cyc_d, np.arange(n_max + 1), r_alm)
    mae = float(np.mean(np.abs(pred - r_al)))
    return mae, cyc_d, r_al, pred


def main():
    cases, _ = tv.select_cases()
    by_stem = {Path(c.reference_csv_path).stem: c for c in cases}

    # calibra k_ratchet numa UNICA curva e congela
    cal = by_stem[CAL_STEM]
    best = None
    print(f"calibrando k_ratchet em {CAL_STEM}:")
    for k in [0.0, 0.005, 0.01, 0.02, 0.05, 0.1]:
        mae, _, _, _ = simulate(cal, k)
        print(f"  k_ratchet={k:5.3f} MAE={mae:.3f}", flush=True)
        if best is None or mae < best[1]:
            best = (k, mae)
    K = best[0]
    print(f"k_ratchet CONGELADO = {K}\n")

    prev = {r["csv"]: r for r in json.loads(
        (ROOT / "New_Theory" / "library_error_modes.json").read_text(encoding="utf-8"))}
    rows = []
    for case in cases:
        csv = Path(case.reference_csv_path).name
        mae, cyc_d, r_al, pred = simulate(case, K)
        cl = classify(cyc_d, r_al, pred, mae)
        pv = prev.get(csv, {})
        rows.append(dict(csv=csv, source=case.source.name, mae=mae,
                         mae_prev_best=min(pv.get("mae_base", 9), pv.get("mae_pack", 9)),
                         mode=cl["mode"], mode_prev=pv.get("mode_best", "?"),
                         e_final=cl["e_final"]))
        print(f"  {csv:44s} MAE={mae:.3f} (antes {rows[-1]['mae_prev_best']:.3f}) "
              f"{cl['mode']:15s} e_fim={cl['e_final']:+.3f}", flush=True)

    print("\n== POR FONTE: antes(best) -> agora ==")
    by_src = {}
    for r in rows:
        by_src.setdefault(r["source"], []).append(r)
    n_cm_before = sum(1 for r in rows if r["mode_prev"] == "collapse-missed")
    n_cm_after = sum(1 for r in rows if r["mode"] == "collapse-missed")
    for src, rs in sorted(by_src.items()):
        med_b = float(np.median([r["mae_prev_best"] for r in rs]))
        med_a = float(np.median([r["mae"] for r in rs]))
        print(f"  {src:15s} n={len(rs):2d} medianMAE {med_b:.3f} -> {med_a:.3f}")
    med_g_b = float(np.median([r["mae_prev_best"] for r in rows]))
    med_g_a = float(np.median([r["mae"] for r in rows]))
    print(f"  GLOBAL          n={len(rows)} medianMAE {med_g_b:.3f} -> {med_g_a:.3f}")
    print(f"  collapse-missed: {n_cm_before} -> {n_cm_after}")
    (ROOT / "New_Theory" / "ratchet_validation.json").write_text(
        json.dumps(dict(k_ratchet=K, c_bend_rig=C_BEND_RIG, rows=rows), indent=1),
        encoding="utf-8")
    print("Artefato: ratchet_validation.json")


if __name__ == "__main__":
    main()
