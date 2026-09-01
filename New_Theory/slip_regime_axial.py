"""Validacao do regime de slip no eixo AXIAL (Liu2017, spec 2026-07-07 §7).

Sucesso = SLOPE: d(final)/dP0 sobe de 5.6e-6 (report) rumo ao dado 2.6e-5 /N.
Mecanismo: o fretting de flanco sozinho da' perda fracional F0-INDEPENDENTE
(ΔF0 ~ F0*A_F => frac ~ A_F). O partial_slip_gate (CM) multiplica d_fret por
g=1-(1-min(r,1))^m, r=A_F/(mu*F0*kappa): F0 maior -> r menor -> menos fret ->
frac DECRESCE com F0 -> slope inclina. Zero-refit (frozen Stage-A + emb Rz<4).

Tres configs: (i) gate OFF k_fret=0 (= report), (ii) fret ON sem gate (~flat),
(iii) fret ON + CM (inclina). Run: python New_Theory/slip_regime_axial.py [--quick]
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
K_FRET, KAPPA = 1.0, 6.0   # config where CM visibly bites (shows capability; over-loses level => Fouvry Wave 2)


def simulate(F0, emb, consts, k_fret, cm, cap):
    geom = geometry_for("M12x1.75", GRIP)
    kw = dict(emb_depth=emb, mu_thread=MU, mu_bearing=MU, k_thread_fret=k_fret, **consts)
    if cm:
        kw.update(slip_regime_mode="cattaneo_mindlin", slip_capacity_coeff=KAPPA)
    ana = DynamicStiffnessAnalyzer(geom, JointMaterial(**kw), F0)
    for _ in range(cap):
        ana.step_cycle(F_AMP, 0.0, FREQ)                  # axial force-mode
    return max(ana.state.F_0, 0.0) / F0


def slope(F0s, finals):
    return float(np.polyfit([f / 1e3 for f in F0s], finals, 1)[0]) / 1e3  # per N


def main():
    quick = "--quick" in sys.argv
    consts, _ = frozen_constants()
    emb, _ = emb_depth_vdi("Rz<4", 1)
    data = {}
    for tag, F0 in P0:
        cyc, r = load_full_curve(f"{DIG}/liu2017_axial_F0_{tag}.csv")
        data[F0] = (int(min(1_000_000, cyc[-1])), float(r[-1] / r[0]))
    F0s = [f for _, f in P0]
    d_finals = [data[f][1] for f in F0s]
    d_slope = slope(F0s, d_finals)
    print(f"emb Rz<4={emb*1e6:.1f}um k_fret={K_FRET} kappa={KAPPA}  (cap={'2e4' if quick else '1e6'})")
    print(f"data   finals {[round(x,3) for x in d_finals]} slope={d_slope:.2e}/N\n")

    configs = [("gate OFF (report)", 0.0, False),
               ("fret ON, no gate", K_FRET, False),
               ("fret ON + CM", K_FRET, True)]
    for label, kf, cm in configs:
        finals = []
        for f in F0s:
            cap = min(20_000 if quick else data[f][0], data[f][0])
            finals.append(simulate(f, emb, consts, kf, cm, cap))
        s = slope(F0s, finals)
        mae = float(np.mean(np.abs(np.array(finals) - np.array(d_finals))))
        frac = s / d_slope if d_slope else float("nan")
        print(f"{label:20s} finals {[round(x,3) for x in finals]} "
              f"slope={s:.2e}/N ({frac*100:.0f}% of data) MAE={mae:.3f}")
    print("\nAS-IS: o CM inclina o slope (capability). O NIVEL de k_fret e' per-par"
          " (ancora Fouvry, Wave 2). emb Rz<4 = proveniencia. slope alvo 2.6e-5/N.")


if __name__ == "__main__":
    main()
