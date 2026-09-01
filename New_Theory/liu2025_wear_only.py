"""Liu2025 shallow: hipotese final — colapso GRADUAL dirigido por WEAR
(rotacao suprimida per-rig). O wear ∝F0·slip auto-desacelera (exponencial) e
grada com a amplitude — a classe de forma do dado (declinio gradual a 0.33 em
38k ciclos). Gate aberto (c=2.0, onset-bracketado), loose_torsion_mode=legacy
(k_torsional ~2e7 => rotacao ~inerte), k_wear_tr varrido.

Run: python New_Theory/liu2025_wear_only.py   (~10 min)
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


def simulate(case, k_wear, w_conf):
    inp = tv.inputs_for(case)
    consts, _ = frozen_constants()
    consts["W_conf_ref"] = w_conf                       # conformacao per-rig (0 = off)
    emb_m, _ = emb_depth_vdi(inp["rz"]["value"], 1)
    geom = geometry_for(case.bolt_size, grip_mm=inp["grip_mm"]["value"])
    mu = inp["mu"]["value"]
    mat = JointMaterial(emb_depth=emb_m, mu_thread=mu, mu_bearing=mu,
                        conform_driver="effective",
                        slip_regime_mode="cattaneo_mindlin", slip_regime_sharpness=1.0,
                        k_tr_mode="bending", c_bend=2.0,
                        loose_torsion_mode="legacy",     # rotacao ~inerte (per-rig)
                        k_wear_scale_tr=k_wear, **consts)
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
    cs = [c for c in cases if c.source.name == "LIU_2025"]
    best = None
    for k_wear, w_conf in [(0.05, 0.0), (0.1, 0.0), (0.2, 0.0), (0.4, 0.0), (0.1, 7671.0)]:
        res = [(c,) + simulate(c, k_wear, w_conf) for c in cs]
        med = float(np.median([x[1] for x in res]))
        print(f"  k_wear={k_wear:4.2f} W_conf={w_conf:6.0f} medianMAE={med:.3f}", flush=True)
        if best is None or med < best[0]:
            best = (med, k_wear, w_conf, res)
    med, kw, wc, res = best
    print(f"\nBEST k_wear={kw} W_conf={wc}: medianMAE={med:.3f} (frontier anterior 0.126)")
    rows = []
    for c, mae, cyc_d, r_al, pred in res:
        cl = classify(cyc_d, r_al, np.asarray(pred), mae)
        rows.append(dict(csv=Path(c.reference_csv_path).name, mae=mae, mode=cl["mode"],
                         e_final=cl["e_final"]))
        print(f"  {rows[-1]['csv']:34s} MAE={mae:.3f} {cl['mode']:15s} e_fim={cl['e_final']:+.3f}")
    (ROOT / "New_Theory" / "liu2025_wear_only.json").write_text(
        json.dumps(dict(k_wear=kw, w_conf=wc, median=med, rows=rows), indent=1),
        encoding="utf-8")


if __name__ == "__main__":
    main()
