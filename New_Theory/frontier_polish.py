"""POLIMENTO DA FRONTEIRA — fits per-rig de curva-completa, fonte a fonte
(diretiva do professor 2026-07-08: todos os casos com erro baixo; playbook do
ground-fit axial §4.14a-rev aplicado ao transversal).

Por fonte: descida-de-coordenada sobre o SEU conjunto declarado de constantes
(starts pinados por feature), objetivo = MAE de curva completa média da fonte.
Adota so se a mediana melhorar. Pisos de scatter permanecem o limite declarado.

Run: python New_Theory/frontier_polish.py   (~60-90 min, roda fonte a fonte)
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
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)
from library_common import geometry_for, emb_depth_vdi, frozen_constants, load_full_curve  # noqa: E402

PACK = dict(conform_driver="effective", slip_regime_mode="cattaneo_mindlin",
            slip_regime_sharpness=1.0, k_tr_mode="bending",
            loose_torsion_mode="bolt_torsion", eta_loose=15.0, loose_arrest_floor=0.08)
LEGACY = dict(conform_driver="effective", slip_regime_mode="cattaneo_mindlin",
              slip_regime_sharpness=1.0, k_tr_mode="bending",
              loose_torsion_mode="legacy", loose_arrest_floor=0.0)


def simulate(case, kw):
    kw = dict(kw)
    consts, _ = frozen_constants()
    consts.update(kw.pop("_consts", {}))
    emb = kw.pop("emb_um", None)
    inp = tv.inputs_for(case)
    emb_m = (emb * 1e-6) if emb is not None else emb_depth_vdi(inp["rz"]["value"], 1)[0]
    geom = geometry_for(case.bolt_size, grip_mm=inp["grip_mm"]["value"])
    mu = inp["mu"]["value"]
    mat = JointMaterial(emb_depth=emb_m, mu_thread=mu, mu_bearing=mu, **kw, **consts)
    F0 = case.initial_preload_N
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    cyc, ratio = load_full_curve(case.reference_csv_path)
    keep = ratio >= tv.FLOOR_TRIM
    cyc_d = cyc[keep]
    n0, r_al = cyc_d[0], ratio[keep] / ratio[keep][0]
    n_max = int(cyc_d[-1])
    delta = case.transverse_displacement_mm * 1e-3
    F_amp = inp["F_amp_N"]["value"]
    r = np.empty(n_max + 1); r[0] = 1.0
    for n in range(1, n_max + 1):
        ana.step_cycle(F_amp, np.pi / 2, case.frequency_Hz, delta_amp=delta)
        r[n] = max(ana.state.F_0, 0.0) / F0
    r_alm = r / max(np.interp(n0, np.arange(n_max + 1), r), 1e-9)
    pred = np.interp(cyc_d, np.arange(n_max + 1), r_alm)
    return float(np.mean(np.abs(pred - r_al)))


def src_mae(cases, base, over):
    kw = dict(base); kw.update(over)
    return float(np.mean([simulate(c, kw) for c in cases])), kw


def coord_descent(cases, base, params, passes=2, label=""):
    cur = {k: v[0] for k, v in params.items()}          # starts
    grids = {k: v[1] for k, v in params.items()}
    best_mae, _ = src_mae(cases, base, cur)
    print(f"  [{label}] start meanMAE={best_mae:.3f} {cur}", flush=True)
    for p in range(passes):
        for k, grid in grids.items():
            for v in grid:
                if v == cur[k]:
                    continue
                trial = dict(cur); trial[k] = v
                m, _ = src_mae(cases, base, trial)
                if m < best_mae - 1e-4:
                    best_mae, cur = m, trial
                    print(f"    {k}={v} -> {m:.3f}", flush=True)
    print(f"  [{label}] FINAL meanMAE={best_mae:.3f} {cur}", flush=True)
    return best_mae, cur


def main():
    cases, _ = tv.select_cases()
    by = {}
    for c in cases:
        by.setdefault(c.source.name, []).append(c)
    results = {}

    # ---- LIU_2025 (pior familia; incubacao = timing; agora os NIVEIS juntos) ----
    print("== LIU_2025 joint fit (emb, W_onset, k_ratchet) ==", flush=True)
    base = dict(LEGACY, c_bend=50.0, delta_free=0.30e-3, k_wear_scale_tr=0.0,
                _consts=dict(W_conf_ref=0.0))
    mae, cfg = coord_descent(
        by["LIU_2025"], base,
        dict(emb_um=(11.0, [8.0, 11.0, 14.0, 17.0]),
             slip_onset_W=(1.5e5, [7e4, 1.5e5, 2.5e5, 4e5]),
             k_ratchet=(5e-5, [3e-5, 5e-5, 8e-5, 1.2e-4])),
        passes=2, label="LIU_2025")
    results["LIU_2025"] = dict(mae=mae, cfg=cfg, prev=0.126)

    # ---- LU_2024 (cliff timing ok; shape/level juntos) ----
    print("\n== LU_2024 joint fit (emb, delta_free, k_ratchet) ==", flush=True)
    base = dict(PACK, c_bend=5.0)
    mae, cfg = coord_descent(
        by["LU_2024"], base,
        dict(emb_um=(11.0, [5.0, 8.0, 11.0]),
             delta_free=(0.28e-3, [0.25e-3, 0.28e-3, 0.31e-3]),
             k_ratchet=(0.02, [0.01, 0.02, 0.04])),
        passes=2, label="LU_2024")
    results["LU_2024"] = dict(mae=mae, cfg=cfg, prev=0.196)

    # ---- YANG_2019 (level-bias mid-curve) ----
    print("\n== YANG_2019 joint fit (emb, c_bend, slip_onset_W) ==", flush=True)
    base = dict(PACK)
    mae, cfg = coord_descent(
        by["YANG_2019"], base,
        dict(emb_um=(11.0, [6.0, 11.0, 16.0]),
             c_bend=(0.3, [0.3, 0.8, 2.0]),
             slip_onset_W=(0.0, [0.0, 2e4, 8e4])),
        passes=2, label="YANG_2019")
    results["YANG_2019"] = dict(mae=mae, cfg=cfg, prev=0.149)

    # ---- BAUER (centering dentro do piso 0.115: emb/c_bend leves) ----
    print("\n== BAUER_2024 centering (emb, c_bend) ==", flush=True)
    base = dict(conform_driver="effective")
    mae, cfg = coord_descent(
        by["BAUER_2024"], base,
        dict(emb_um=(11.0, [8.0, 11.0, 14.0]),
             c_bend=(1.0, [0.5, 1.0])),
        passes=1, label="BAUER_2024")
    results["BAUER_2024"] = dict(mae=mae, cfg=cfg, prev=0.116, floor=0.115)

    (ROOT / "New_Theory" / "frontier_polish.json").write_text(
        json.dumps(results, indent=1, default=float), encoding="utf-8")
    print("\n== RESUMO ==")
    for s, r in results.items():
        print(f"  {s:14s} {r['prev']:.3f} -> {r['mae']:.3f}  {r['cfg']}")
    print("Artefato: frontier_polish.json")


if __name__ == "__main__":
    main()
