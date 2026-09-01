"""Shallow-collapse, tentativa 2: gate aberto (c_bend bracketado) + WEAR per-rig.

A varredura c_bend pura FALSIFICOU o gate como unico bloqueador: aberto com
k_wear_tr=1 (nivel UFU) over-colapsa (Liu2025 0.126->0.711). Precedente §4.8:
k_wear e' per-rig (UFU 0.44, Liu2022 0.06). Grid: c_bend fixo no bracket de
onset + k_wear_scale_tr x loose_arrest_floor per-rig. O wear ∝F0·slip
auto-desacelera => plateau/finais dependentes de amplitude (assinatura Liu2025).

Run: python New_Theory/shallow_wear_grid.py   (~25 min)
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

# c_bend fixo (bracket de onset do proprio rig); grid em (k_wear_tr, floor)
CFG = {"BAUER_2024": dict(c_bend=0.5, grid=[(0.05, 0.08), (0.15, 0.08), (0.4, 0.08),
                                            (0.05, 0.25), (0.15, 0.25)]),
       "ICMEZ_2025": dict(c_bend=0.6, grid=[(0.05, 0.08), (0.15, 0.08), (0.4, 0.08),
                                            (0.15, 0.25)]),
       "LIU_2025":   dict(c_bend=2.0, grid=[(0.02, 0.08), (0.05, 0.08), (0.15, 0.08),
                                            (0.05, 0.25)])}


def simulate(case, c_bend, k_wear, floor):
    inp = tv.inputs_for(case)
    consts, _ = frozen_constants()
    emb_m, _ = emb_depth_vdi(inp["rz"]["value"], 1)
    geom = geometry_for(case.bolt_size, grip_mm=inp["grip_mm"]["value"])
    mu = inp["mu"]["value"]
    mat = JointMaterial(emb_depth=emb_m, mu_thread=mu, mu_bearing=mu,
                        conform_driver="effective",
                        slip_regime_mode="cattaneo_mindlin", slip_regime_sharpness=1.0,
                        k_tr_mode="bending", c_bend=c_bend,
                        loose_torsion_mode="bolt_torsion", eta_loose=15.0,
                        loose_arrest_floor=floor, k_wear_scale_tr=k_wear, **consts)
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
    return float(np.mean(np.abs(pred - r_al))), cyc_d, r_al, pred


def main():
    cases, _ = tv.select_cases()
    by_src = {}
    for c in cases:
        if c.source.name in CFG:
            by_src.setdefault(c.source.name, []).append(c)
    prev = {r["csv"]: r for r in json.loads(
        (ROOT / "New_Theory" / "library_error_modes.json").read_text(encoding="utf-8"))}
    chosen, rows = {}, []
    for src, cs in sorted(by_src.items()):
        cb = CFG[src]["c_bend"]
        best = None
        for kw, fl in CFG[src]["grid"]:
            res = [(case,) + simulate(case, cb, kw, fl) for case in cs]
            med = float(np.median([x[1] for x in res]))
            print(f"  {src:12s} c={cb} k_wear={kw:4.2f} floor={fl:4.2f} medianMAE={med:.3f}",
                  flush=True)
            if best is None or med < best[0]:
                best = (med, kw, fl, res)
        med, kw, fl, res = best
        chosen[src] = dict(c_bend=cb, k_wear_tr=kw, floor=fl, median=med)
        for case, mae, cyc_d, r_al, pred in res:
            csv = Path(case.reference_csv_path).name
            cl = classify(cyc_d, r_al, np.asarray(pred), mae)
            pv = prev.get(csv, {})
            rows.append(dict(csv=csv, source=src, mae=mae, mode=cl["mode"],
                             mae_prev_best=min(pv.get("mae_base", 9), pv.get("mae_pack", 9)),
                             mode_prev=pv.get("mode_best", "?"), e_final=cl["e_final"]))
    print("\n== RESULTADO (frontier anterior -> wear per-rig) ==")
    for src in sorted(by_src):
        rs = [r for r in rows if r["source"] == src]
        med_b = float(np.median([r["mae_prev_best"] for r in rs]))
        print(f"  {src:12s} {chosen[src]} medianMAE {med_b:.3f} -> {chosen[src]['median']:.3f}")
    n_cm = sum(1 for r in rows if r["mode"] == "collapse-missed")
    n_cm_b = sum(1 for r in rows if r["mode_prev"] == "collapse-missed")
    print(f"  collapse-missed nestas fontes: {n_cm_b} -> {n_cm}")
    (ROOT / "New_Theory" / "shallow_wear_grid.json").write_text(
        json.dumps(dict(chosen=chosen, rows=rows), indent=1), encoding="utf-8")
    print("Artefato: shallow_wear_grid.json")


if __name__ == "__main__":
    main()
