"""Gera os cases TRANSVERSAIS do Liu2022 fig5 (primeiro aperto, dry x2 + oil x2)
para a galeria — ZERO-REFIT das constantes sec4.10/4.11 (emb Rz<4, k_wear 0.06,
dano PER-LUBE c_D dry 0.5 / oil 0.03, starters fisicos k_dmg_mu=1 k_dmg_wear=4
W_ref=1e4); mu DERIVADO do F0 medido de cada caso (Motosh, harness de origem
validate_retightening). Gate pre-declarado: MAE <= 0.10 por caso (fonte sem
piso de repeticao); adota os que passarem como fonte LIU_2022.

Run: python -u New_Theory/liu2022_fig5_cases.py [--adopt]
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "New_Theory"))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointMaterial, THREAD_FLANK_ANGLE)
from library_common import frozen_constants, geometry_for, emb_depth_vdi, load_full_curve

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"
GRIP, DELTA, FREQ, TORQUE = 50.0, 0.3e-3, 12.5, 80.0
CASES = [("liu2022_fig5_dry_F19p78kN", 19.78e3, "dry"),
         ("liu2022_fig5_dry_F21p50kN", 21.50e3, "dry"),
         ("liu2022_fig5_oil_F26p00kN", 26.00e3, "oil"),
         ("liu2022_fig5_oil_F28p18kN", 28.18e3, "oil")]
C_D = {"dry": 0.5, "oil": 0.03}


def mu_from_f0(F0, geom):
    lead = geom.pitch / (2 * np.pi)
    arm = geom.d_2 / (2 * np.cos(THREAD_FLANK_ANGLE)) + geom.r_bearing
    return max((TORQUE / F0 - lead) / arm, 0.0)


def run(F0, lube):
    consts, _ = frozen_constants()
    geom = geometry_for("M12x1.75", GRIP)
    emb_m, _ = emb_depth_vdi("Rz<4", 1)
    mu = mu_from_f0(F0, geom)
    mat = JointMaterial(mu_thread=mu, mu_bearing=mu, emb_depth=emb_m,
                        k_wear_scale_tr=0.06, c_D=C_D[lube], W_ref=1e4,
                        k_dmg_mu=1.0, k_dmg_wear=4.0,
                        k_wear_running=5.0, N_wear_run=100.0, **consts)
    return geom, mat, mu


def main():
    adopt = "--adopt" in sys.argv
    rows = []
    for key, F0, lube in CASES:
        cyc, rr = load_full_curve(f"{DIG}/{key}.csv"); rr = rr / rr[0]
        n_max = int(cyc[-1])
        geom, mat, mu = run(F0, lube)
        ana = DynamicStiffnessAnalyzer(geom, mat, F0)
        r = np.empty(n_max + 1); r[0] = 1.0
        for n in range(1, n_max + 1):
            ana.step_cycle(5e3, np.pi / 2, FREQ, delta_amp=DELTA)
            r[n] = max(ana.state.F_0, 0.0) / F0
        pred = np.interp(cyc, np.arange(n_max + 1), r)
        mae = float(np.mean(np.abs(pred - rr)))
        rows.append((key, mae, cyc, rr, r, n_max, mu, lube))
        print(f"{key:28s} mu={mu:.3f} MAE {mae:.3f} fim mod {r[-1]:.3f} dado {rr[-1]:.3f}")
    ok = [r for r in rows if r[1] <= 0.10]
    print(f"\nGate MAE<=0.10: {len(ok)}/4 passam")
    if adopt and ok:
        rd = json.loads((ROOT / "New_Theory" / "report_data.json").read_text(encoding="utf-8"))
        for key, mae, cyc, rr, r, n_max, mu, lube in ok:
            xs = np.unique(np.round(np.linspace(0, n_max, 120)).astype(int))
            rd["gallery"].append(dict(
                csv=key, source="LIU_2022", mae=mae,
                label=f"REFEITO sec4.29: running-in wear k=5/N=100 (Zhang2019 N^0.53) + mu={mu:.3f} "
                      f"(Motosh), emb Rz<4, k_wear 0.06, c_D per-lube {C_D[lube]}",
                amp_mm=0.3, n_max=n_max,
                data={"x": [float(v) for v in cyc], "y": [round(float(v), 4) for v in rr]},
                model={"x": [int(v) for v in xs],
                       "y": [round(float(np.interp(v, np.arange(n_max + 1), r)), 5) for v in xs]}))
        (ROOT / "New_Theory" / "report_data.json").write_text(
            json.dumps(rd, indent=1, default=float), encoding="utf-8")
        print(f"ADOTADO: {len(ok)} casos LIU_2022 na galeria.")


if __name__ == "__main__":
    main()
