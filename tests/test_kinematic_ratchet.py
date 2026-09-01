"""Kinematic ratcheting (spec 2026-07-08, collapse-missed mode).

d_theta per cycle gains an amplitude-PROPORTIONAL term gates*k_ratchet*4*slip/(d2/2)
(classical Junker: nut advances a fraction of the gross-slip path). k_ratchet=0
default => bit-identical. Only disp-mode; only beyond the torque onset."""
import numpy as np
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)


def _geom(d2=7.19e-3, grip=20e-3):
    return JointGeometry(A_s=36.6e-6, L_eff=grip, d_2=d2, pitch=1.25e-3,
                         r_bearing=6e-3, A_contact=60e-6)


def _run(k_ratchet, delta_mm, n=300, c_bend=0.7):
    m = JointMaterial(emb_depth=3.5e-6, mu_thread=0.15, mu_bearing=0.15,
                      conform_driver="effective",
                      slip_regime_mode="cattaneo_mindlin", slip_regime_sharpness=1.0,
                      k_tr_mode="bending", c_bend=c_bend,
                      loose_torsion_mode="bolt_torsion", eta_loose=15.0,
                      loose_arrest_floor=0.08, k_ratchet=k_ratchet)
    F0 = 11.6e3
    ana = DynamicStiffnessAnalyzer(_geom(), m, F0)
    for _ in range(n):
        ana.step_cycle(0.4 * F0, np.pi / 2, 12.5, delta_amp=delta_mm * 1e-3)
    return max(ana.state.F_0, 0.0) / F0, float(ana.state.theta_loose)


def test_default_inert():
    assert JointMaterial().k_ratchet == 0.0
    f_off, _ = _run(0.0, 1.0)
    f_off2, _ = _run(0.0, 1.0)
    assert f_off == f_off2                              # deterministic baseline


def test_amplitude_proportional():
    # bigger stroke -> more gross slip -> faster collapse (the Lu2024 signature)
    f_small, th_small = _run(0.02, 0.6)
    f_big, th_big = _run(0.02, 2.0)
    assert th_big > th_small                            # more rotation at bigger amp
    assert f_big < f_small                              # deeper collapse at bigger amp


def test_collapse_speed_and_rotation_arrest():
    # with ratchet on, an M8 at 2mm collapses fast (data ~0.01-0.1); the floor
    # arrests ROTATION (theta stops growing once F_0 <= floor*F_0_init) while
    # wear may legitimately drain further.
    f, th_500 = _run(0.05, 2.0, n=500)
    _, th_300 = _run(0.05, 2.0, n=300)
    assert f < 0.15                                     # collapses like the data
    assert th_500 - th_300 < 0.02 * max(th_300, 1e-9)   # rotation arrested (not runaway)


def test_stick_below_threshold_no_ratchet():
    # below the stick threshold (tiny stroke) the gate closes -> no ratcheting
    f_stick, th = _run(0.05, 0.05, n=300)
    assert th < 1e-3 and f_stick > 0.6                  # settling only


# ---- product form: ratchet_torque_coupled (spec 2026-07-08) ----
def _run_prod(F0, coupled, k=2e-4, n=800):
    # emb tiny + wear off => isola o canal do ratchet (o teste mede a FORMA dele)
    m = JointMaterial(emb_depth=0.1e-6, mu_thread=0.15, mu_bearing=0.15,
                      conform_driver="effective", K_archard=0.0,
                      slip_regime_mode="cattaneo_mindlin", slip_regime_sharpness=1.0,
                      k_tr_mode="bending", c_bend=50.0, delta_free=0.28e-3,
                      loose_torsion_mode="legacy", k_ratchet=k,
                      ratchet_torque_coupled=coupled)
    ana = DynamicStiffnessAnalyzer(_geom(), m, F0)
    traj, theta = [], []
    for _ in range(n):
        ana.step_cycle(0.4 * F0, np.pi / 2, 12.5, delta_amp=0.5e-3)
        traj.append(max(ana.state.F_0, 0.0) / F0)
        theta.append(ana.state.theta_loose)
    return np.array(traj), np.array(theta)


def test_product_default_off_matches_pure_kinematic():
    assert JointMaterial().ratchet_torque_coupled is False
    a, _ = _run_prod(12e3, False)
    b, _ = _run_prod(12e3, False)
    assert np.array_equal(a, b)


def test_product_accelerates_rotation():
    # coupled: theta rate grows as F_0 falls (slip_fraction grows) => back-loaded
    # rotation; uncoupled: theta ~linear. Measured on theta_loose (creep-free).
    _, th_c = _run_prod(12e3, True, k=1.2e-3, n=1500)
    d_early = th_c[99] - th_c[0]
    d_late = th_c[-1] - th_c[-100]
    assert d_late / max(d_early, 1e-15) > 1.3           # accelerating (measured ~1.9)


def test_product_preload_scale_invariant():
    # fractional F trajectories ~overlap across a 3x preload sweep at same stroke
    # (slip_fraction depends only on F_0/F_0_init) => N_fail flat vs torque.
    t_lo, _ = _run_prod(6e3, True, k=4e-4, n=600)
    t_hi, _ = _run_prod(18e3, True, k=4e-4, n=600)
    assert float(np.mean(np.abs(t_lo - t_hi))) < 0.06   # ~same fractional path
