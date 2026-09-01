"""Polimento rapido: HDPE (3 curvas x 400 cyc) + sweep A_F axial (4 curvas,
k_thread_fret+kappa per-rig sob o gate CM — o gap §4.6 com nivel per-rig).

Run: python New_Theory/polish_hdpe_af.py   (~15 min, dominado pelo A_F)
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
GF = dict(emb_cap=4.30e-6, n_emb=15.0, c_rig=1.450e-11, exp_f=2.375, exp_s=3.60)
PACK = dict(conform_driver="effective", slip_regime_mode="cattaneo_mindlin",
            slip_regime_sharpness=1.0, k_tr_mode="bending",
            loose_torsion_mode="bolt_torsion", eta_loose=15.0, loose_arrest_floor=0.08)


def hdpe_mae(emb_um, k_creep, c_bend, delta_free=0.0):
    consts, _ = frozen_constants()
    maes = []
    for name, grip in [("t10", 25.0), ("t12", 29.0), ("t14", 33.0)]:
        F0 = 10250.0 if name != "t14" else 10350.0
        cyc_d, r_d = load_full_curve(f"{DIG}/rousseau2025_hdpe_{name}.csv")
        geom = geometry_for("M12x1.75", grip)
        mat = JointMaterial(emb_depth=emb_um * 1e-6, mu_thread=0.15, mu_bearing=0.15,
                            k_j_init=2.0e7, k_creep_scale=k_creep, delta_free=delta_free,
                            **dict(PACK, c_bend=c_bend), **consts)
        ana = DynamicStiffnessAnalyzer(geom, mat, F0)
        r = np.empty(401); r[0] = 1.0
        for n in range(1, 401):
            ana.step_cycle(0.4 * F0, np.pi / 2, 1.0, delta_amp=0.5e-3)
            r[n] = max(ana.state.F_0, 0.0) / F0
        pred = np.interp(cyc_d, np.arange(401), r)
        maes.append(float(np.mean(np.abs(pred - r_d / r_d[0]))))
    return float(np.mean(maes)), maes


def af_mae(k_fret, kappa, cap=300_000):
    consts, _ = frozen_constants()
    consts["C_creep"] = GF["c_rig"]; consts["N_emb"] = GF["n_emb"]
    geom = geometry_for("M12x1.75", 30.0)
    kw = dict(emb_depth=GF["emb_cap"], mu_thread=0.15, mu_bearing=0.15,
              emb_conform_exp=GF["exp_f"], creep_conform_exp=GF["exp_s"],
              p_ref_emb=15e3 / geom.A_contact, k_thread_fret=k_fret,
              slip_regime_mode="cattaneo_mindlin", slip_capacity_coeff=kappa,
              **consts)
    maes = []
    for tag, F_amp in [("7p5kN", 7.5e3), ("8p75kN", 8.75e3),
                       ("11p25kN", 11.25e3), ("12p5kN", 12.5e3)]:
        cyc_d, r_d = load_full_curve(f"{DIG}/liu2017_axial_AF_{tag}.csv")
        r_al = r_d / r_d[0]
        n_max = int(min(cap, cyc_d[-1]))
        keep = cyc_d <= n_max
        ana = DynamicStiffnessAnalyzer(geom, JointMaterial(**kw), 18e3)
        r = np.empty(n_max + 1); r[0] = 1.0
        for n in range(1, n_max + 1):
            ana.step_cycle(F_amp, 0.0, 30.0)
            r[n] = max(ana.state.F_0, 0.0) / 18e3
        n0 = cyc_d[keep][0]
        r_alm = r / max(np.interp(n0, np.arange(n_max + 1), r), 1e-9)
        pred = np.interp(cyc_d[keep], np.arange(n_max + 1), r_alm)
        maes.append(float(np.mean(np.abs(pred - r_al[keep]))))
    return float(np.mean(maes)), maes


def main():
    out = {}
    print("== HDPE polish ==", flush=True)
    best = None
    for emb in [1.0, 2.0, 3.5]:
        for kc in [2.0, 3.0, 5.0]:
            for cb in [0.15, 0.2, 0.3]:
                m, per = hdpe_mae(emb, kc, cb)
                if best is None or m < best[0]:
                    best = (m, dict(emb_um=emb, k_creep=kc, c_bend=cb), per)
                    print(f"  emb={emb} k_creep={kc} c_bend={cb} mean={m:.3f} per={[round(x,3) for x in per]}", flush=True)
    out["HDPE"] = dict(mae=best[0], cfg=best[1], per=best[2], prev=0.136)
    print(f"  BEST HDPE mean={best[0]:.3f} {best[1]}")

    print("\n== A_F sweep polish (cap 3e5; melhor verifica a 1e6 depois) ==", flush=True)
    bestf = None
    for kf in [0.0, 0.05, 0.1, 0.2]:
        for kp in [3.0, 6.0, 10.0]:
            if kf == 0.0 and kp != 6.0:
                continue
            m, per = af_mae(kf, kp)
            print(f"  k_fret={kf} kappa={kp} mean={m:.3f} per={[round(x,3) for x in per]}", flush=True)
            if bestf is None or m < bestf[0]:
                bestf = (m, dict(k_fret=kf, kappa=kp), per)
    out["AF"] = dict(mae=bestf[0], cfg=bestf[1], per=bestf[2], prev=0.040)
    print(f"  BEST AF mean={bestf[0]:.3f} {bestf[1]}")
    (ROOT / "New_Theory" / "polish_hdpe_af.json").write_text(
        json.dumps(out, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
