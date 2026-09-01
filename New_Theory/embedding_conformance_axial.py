"""Validacao: saturacao de embedding dependente de pressao fecha o slope axial?
(spec 2026-07-08; a forma que o slip-regime NAO conseguiu — MODEL_LEGITIMACY §4.12.)

Anchor p_ref_emb = p(F0_min) (input da matriz, nao fit) e VARRE so emb_conform_exp;
reporta d(final)/dP0 do modelo vs dado 2.63e-5/N. Zero-refit (frozen Stage-A + Rz<4).

Run: python New_Theory/embedding_conformance_axial.py [--quick]
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)
from library_common import (  # noqa: E402
    geometry_for, frozen_constants, emb_depth_vdi, load_full_curve)

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"
P0 = [("15kN", 15e3), ("16p5kN", 16.5e3), ("18kN", 18e3), ("19p5kN", 19.5e3), ("21kN", 21e3)]
GRIP, FREQ, MU, F_AMP = 30.0, 30.0, 0.15, 10e3


def final(F0, emb, consts, exp, p_ref, cap, exp_slow=0.0):
    geom = geometry_for("M12x1.75", GRIP)
    mat = JointMaterial(emb_depth=emb, mu_thread=MU, mu_bearing=MU,
                        emb_conform_exp=exp, creep_conform_exp=exp_slow,
                        p_ref_emb=p_ref, **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    for _ in range(cap):
        ana.step_cycle(F_AMP, 0.0, FREQ)                     # axial force-mode
    return max(ana.state.F_0, 0.0) / F0


def slope(F0s, finals):
    return float(np.polyfit([f / 1e3 for f in F0s], finals, 1)[0]) / 1e3   # per N


def main():
    quick = "--quick" in sys.argv
    consts, _ = frozen_constants()
    emb, _ = emb_depth_vdi("Rz<4", 1)
    geom = geometry_for("M12x1.75", GRIP)
    p_ref = 15e3 / geom.A_contact                            # anchor: p(F0_min), input
    F0s = [f for _, f in P0]
    data = {}
    for tag, F0 in P0:
        cyc, r = load_full_curve(f"{DIG}/liu2017_axial_F0_{tag}.csv")
        data[F0] = (int(min(1_000_000, cyc[-1])), float(r[-1] / r[0]))
    d_finals = [data[f][1] for f in F0s]
    d_slope = slope(F0s, d_finals)
    print(f"emb Rz<4={emb*1e6:.1f}um  p_ref=p(15kN)={p_ref:.2e} Pa  cap={'2e4' if quick else 'n_max'}")
    print(f"data   finals {[round(x,3) for x in d_finals]} slope={d_slope:.2e}/N\n")

    # Decomposicao fast/slow do DADO (feature que pina n_slow independente do fast):
    # fast = queda ate ciclo<=30; slow = resto. Perda lenta ABSOLUTA ~F0^-1.
    print("decomposicao do dado (fast<=30cyc / slow):")
    for tag, F0 in P0:
        cyc, r = load_full_curve(f"{DIG}/liu2017_axial_F0_{tag}.csv")
        r = r / r[0]
        fast = float(1.0 - r[cyc <= 30][-1]) if (cyc <= 30).any() else float("nan")
        slow = float((1.0 - r[-1]) - fast)
        print(f"  F0={F0/1e3:4.1f}kN fast={fast:.3f} slow={slow:.3f} "
              f"slow_abs={slow*F0:.0f}N")

    best = None
    print("\nGrid exp_fast=4.0 (pinado pelo fast-drop), exp_slow varrido:")
    for exp_slow in [0.0, 1.0, 2.0, 3.0]:
        finals = []
        for f in F0s:
            cap = 20_000 if quick else data[f][0]
            finals.append(final(f, emb, consts, 4.0, p_ref, cap, exp_slow=exp_slow))
        s = slope(F0s, finals)
        mae = float(np.mean(np.abs(np.array(finals) - np.array(d_finals))))
        frac = s / d_slope if d_slope else float("nan")
        print(f"  exp_slow={exp_slow:.1f} finals {[round(x,3) for x in finals]} "
              f"slope={s:.2e}/N ({frac*100:.0f}% of data) MAE={mae:.3f}")
        if best is None or abs(s - d_slope) < abs(best[1] - d_slope):
            best = (exp_slow, s, mae, finals)
    exp_slow, s, mae, finals = best
    print(f"\nBEST exp_fast=4.0 exp_slow={exp_slow}: slope={s:.2e}/N "
          f"({s/d_slope*100:.0f}% of data 2.63e-5) MAE={mae:.3f}")
    print(f"  level @15kN kept: model {finals[0]:.3f} vs data {d_finals[0]:.3f} (anchor => S=1 at min)")
    print("AS-IS: FORMA (pre-conformacao dos reservatorios rapido E lento) — capability;")
    print("exp_fast pinado pelo fast-drop, exp_slow pela decomposicao lenta (features")
    print("independentes do MESMO sweep); p_ref ancorado (input). Liu2017 e' o unico")
    print("P0-sweep => fit, nao cross-valida (NAO adotar no shared).")


if __name__ == "__main__":
    main()
