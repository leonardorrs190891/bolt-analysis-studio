"""Adocao HDPE (sec4.20): k_member_shear (serie) + INPUT FIX F_eff=min(0.4F0,
k_serie*delta) — a pilha polimerica limita a forca transmissivel (F_amp era
input ASSUMIDO; item 4 da agenda). Config candidata do refit 2026-07-08.

Gates: G-B2 ordem de espessura do dado restaurada (t14 mais retido) [PASS
esperado]; G-B3 campanha: media melhora E nenhum caso piora >0.02. G-B1
estrito (todos<=0.100) reportado AS-IS (t14 ~0.136 = separatriz t12/t14,
janela ~15% na forca transmitida). Adota se G-B2 E G-B3.

Run: python -u New_Theory/hdpe_adopt.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)
from library_common import geometry_for, frozen_constants, load_full_curve  # noqa: E402

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"
PACK = dict(conform_driver="effective", slip_regime_mode="cattaneo_mindlin",
            slip_regime_sharpness=1.0, k_tr_mode="bending",
            loose_torsion_mode="bolt_torsion", eta_loose=15.0)
CFG = dict(GA=1.2e5, c_bend=4.0, k_creep=1.0, floor=0.22, emb_um=2.0, mu=0.20, fs=1.0)
CASES = [("t10", 25.0, 10250.0, 0.010), ("t12", 29.0, 10250.0, 0.012),
         ("t14", 33.0, 10350.0, 0.014)]
DELTA = 0.5e-3
LABEL = (f"CALIB MULTI-OBJETIVO rev-b (preload+theta+energia, priors ancorados): mu=0.20 free_spin=1 GA={CFG['GA']:.0f} "
         f"c_bend={CFG['c_bend']} k_creep={CFG['k_creep']} floor={CFG['floor']}")


def run(name, grip, F0, t_m):
    consts, _ = frozen_constants()
    geom = geometry_for("M12x1.75", grip)
    k_m = CFG["GA"] / t_m
    I = np.pi * geom.d_2 ** 4 / 64
    k_ser = 1.0 / (1.0 / max(CFG["c_bend"] * geom.E * I / geom.L_eff ** 3, 1.0) + 1.0 / k_m)
    F_eff = min(0.4 * F0, k_ser * DELTA)
    cyc_d, r_d = load_full_curve(f"{DIG}/rousseau2025_hdpe_{name}.csv")
    r_d = r_d / r_d[0]
    mat = JointMaterial(emb_depth=CFG["emb_um"] * 1e-6, mu_thread=CFG["mu"], mu_bearing=CFG["mu"], free_spin=CFG["fs"],
                        k_j_init=2.0e7, k_member_shear=k_m, k_creep_scale=CFG["k_creep"],
                        c_bend=CFG["c_bend"], loose_arrest_floor=CFG["floor"],
                        **PACK, **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    r = np.empty(401); r[0] = 1.0
    for n in range(1, 401):
        ana.step_cycle(F_eff, np.pi / 2, 1.0, delta_amp=DELTA)
        r[n] = max(ana.state.F_0, 0.0) / F0
    pred = np.interp(cyc_d, np.arange(401), r)
    return (float(np.mean(np.abs(pred - r_d))), float(pred[-1]), float(r_d[-1]),
            np.arange(401), r)


def main():
    with open(ROOT / "New_Theory" / "report_data.json", encoding="utf-8") as fh:
        rd = json.load(fh)
    ents = {c["csv"]: c for c in rd["gallery"] if c["source"] == "ROUSSEAU_HDPE"}
    rows, fins = [], []
    for name, grip, F0, t in CASES:
        mae, fin, dfin, mx, my = run(name, grip, F0, t)
        key = f"rousseau2025_hdpe_{name}"
        old = float(ents[key]["mae"])
        rows.append((key, mae, old, mx, my)); fins.append((fin, dfin))
        print(f"{key:26s} MAE {mae:.3f} (era {old:.3f})  fim mod {fin:.2f} dado {dfin:.2f}")
    g_b2 = fins[2][0] > fins[1][0] > fins[0][0] - 0.02
    mean_new = float(np.mean([r[1] for r in rows]))
    mean_old = float(np.mean([r[2] for r in rows]))
    worse = [r[0] for r in rows if r[1] > r[2] + 0.02]
    g_b3 = mean_new < mean_old and not worse
    g_b1 = all(r[1] <= 0.100 for r in rows)
    print(f"\nG-B1 todos<=0.100: {g_b1} (t14 separatriz — AS-IS)")
    print(f"G-B2 ordem restaurada: {g_b2}   G-B3 media {mean_old:.3f}->{mean_new:.3f}, "
          f"piora: {worse or 'nenhuma'}: {g_b3}")
    if g_b2 and g_b3:
        for key, mae, old, mx, my in rows:
            e = ents[key]
            e["model"] = {"x": [int(v) for v in mx[::4]] + [400],
                          "y": [round(float(v), 5) for v in my[::4]] + [round(float(my[-1]), 5)]}
            e["mae"] = mae
            e["label"] = LABEL
        (ROOT / "New_Theory" / "report_data.json").write_text(
            json.dumps(rd, indent=1, default=float), encoding="utf-8")
        print("ADOTADO: report_data.json atualizado (ROUSSEAU_HDPE).")
    else:
        print("NAO adotado — registrar AS-IS.")


if __name__ == "__main__":
    main()
