"""Fixed transverse take-up delta_free (spec 2026-07-08).

slip = max(0, delta - delta_free - F_slip/k_tr): a preload-INDEPENDENT part of the
stroke is absorbed by engaged hole clearance + fixture compliance. Signatures it
must produce (read from data): N_fail ~ 1/(amp - d0) grading (Liu2025) and
N_fail ~flat across preload (Lu fig20). Default 0 = bit-identical."""
import numpy as np
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    resolve_transverse_slip)


def _geom(grip_mm=20.0, d2=7.19e-3):
    return JointGeometry(A_s=36.6e-6, L_eff=grip_mm * 1e-3, d_2=d2,
                         pitch=1.25e-3, r_bearing=6e-3, A_contact=60e-6)


def test_default_inert():
    assert JointMaterial().delta_free == 0.0
    m0 = JointMaterial(k_tr_mode="bending", c_bend=0.7)
    m1 = JointMaterial(k_tr_mode="bending", c_bend=0.7, delta_free=0.0)
    st = SlowState(F_0=12e3, F_0_init=12e3)
    s0 = resolve_transverse_slip(st, m0, 5e3, np.pi / 2, 0.5e-3, geom=_geom())
    s1 = resolve_transverse_slip(st, m1, 5e3, np.pi / 2, 0.5e-3, geom=_geom())
    assert s0 == s1


def test_takeup_reduces_slip_and_protects_below():
    m = JointMaterial(k_tr_mode="bending", c_bend=5.0, delta_free=0.30e-3)
    st = SlowState(F_0=60e3, F_0_init=60e3)
    g = _geom(40.0, 14.7e-3)
    s_above = resolve_transverse_slip(st, m, 24e3, np.pi / 2, 0.5e-3, geom=g)
    s_below = resolve_transverse_slip(st, m, 24e3, np.pi / 2, 0.25e-3, geom=g)
    assert s_below == 0.0                                  # below d0: protected
    assert 0.0 < s_above < 0.5e-3                          # above: excess only


def test_threshold_floor_is_F0_independent():
    # as F0 falls, the frictional part vanishes but delta_free remains:
    m = JointMaterial(k_tr_mode="bending", c_bend=5.0, delta_free=0.30e-3)
    g = _geom(40.0, 14.7e-3)
    hi = resolve_transverse_slip(SlowState(F_0=60e3, F_0_init=60e3), m, 0, np.pi / 2, 0.5e-3, geom=g)
    lo = resolve_transverse_slip(SlowState(F_0=3e3, F_0_init=60e3), m, 0, np.pi / 2, 0.5e-3, geom=g)
    assert lo <= 0.5e-3 - 0.30e-3 + 1e-9                   # capped at delta - d0
    assert lo >= hi                                        # frictional part shrank


def _slip(F0, delta_free, c_bend):
    m = JointMaterial(k_tr_mode="bending", c_bend=c_bend, delta_free=delta_free,
                      mu_thread=0.15, mu_bearing=0.15)
    return resolve_transverse_slip(SlowState(F_0=F0, F_0_init=F0), m,
                                   0.4 * F0, np.pi / 2, 0.5e-3, geom=_geom())


def test_slip_flattens_across_preload():
    # Frictional-only threshold (~F0): slip varies strongly across a 3x preload
    # sweep. With delta_free dominating: slip ~preload-flat (Lu fig20 signature:
    # N_fail flat vs torque). Ratio slip(6kN)/slip(18kN):
    lo_f, hi_f = _slip(6e3, 0.0, 1.0), _slip(18e3, 0.0, 1.0)
    lo_d, hi_d = _slip(6e3, 0.30e-3, 5.0), _slip(18e3, 0.30e-3, 5.0)
    assert hi_f < lo_f                                     # frictional: shrinks with F0
    spread_f = lo_f / max(hi_f, 1e-12)
    spread_d = lo_d / max(hi_d, 1e-12)
    assert spread_d < spread_f                             # take-up flattens the spread
    assert spread_d < 1.5                                  # ~flat across 3x preload
