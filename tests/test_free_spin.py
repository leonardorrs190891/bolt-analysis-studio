"""free_spin (sec4.23): rotacao continua apos o arrest SEM drenar preload.
Default 0 = bit-identical (theta E preload)."""
import numpy as np
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)


def _geom():
    return JointGeometry(A_s=84.3e-6, L_eff=30e-3, d_2=10.86e-3, pitch=1.75e-3,
                         r_bearing=9e-3, A_contact=117.6e-6)


def _run(fs, n=800):
    m = JointMaterial(emb_depth=0.0, C_creep=0.0, mu_thread=0.15, mu_bearing=0.15,
                      k_tr_mode="bending", c_bend=5.0, loose_torsion_mode="bolt_torsion",
                      eta_loose=15.0, loose_arrest_floor=0.5, k_ratchet=0.05,
                      free_spin=fs)
    ana = DynamicStiffnessAnalyzer(_geom(), m, 10e3)
    for _ in range(n):
        ana.step_cycle(4e3, np.pi / 2, 5.0, delta_amp=1.0e-3)
    return ana.state.F_0 / 10e3, np.degrees(ana.state.theta_loose)


def test_default_inert():
    assert JointMaterial().free_spin == 0.0
    r0, t0 = _run(0.0)
    r1, t1 = _run(0.0)
    assert r0 == r1 and t0 == t1


def test_preload_bit_identical_theta_grows():
    r_off, th_off = _run(0.0)
    r_on, th_on = _run(1.0)
    assert abs(r_on - r_off) < 1e-12      # preload identico
    assert th_on > th_off * 1.5           # theta continua no free-spin
    assert r_off < 0.55                   # passou do floor de rotacao (wear segue drenando)
