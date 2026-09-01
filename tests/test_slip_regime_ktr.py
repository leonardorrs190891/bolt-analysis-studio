"""Slip regime k_tr fix (spec 2026-07-05): bending k_tr, opt-in."""
import numpy as np
import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    k_tr_transverse, resolve_transverse_slip,
)

M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)


def test_ktr_axial_frac_is_default_and_current():
    m = JointMaterial()  # k_tr_mode default "axial_frac"
    assert m.k_tr_mode == "axial_frac"
    assert k_tr_transverse(M16, m) == max(m.k_j_init * 0.3, 1.0)   # current


def test_ktr_bending_is_much_softer_and_per_rig():
    m = JointMaterial(k_tr_mode="bending", c_bend=3.0)
    k_bend = k_tr_transverse(M16, m)
    assert k_bend < 1e8                       # ~1e7, ~100x softer than axial 1.2e9
    # per-rig: k ~ d^4/L^3. M8 has smaller d AND shorter L; the d^4 drop
    # dominates the L^3 change (net ~0.26x), so M8 ends up softer.
    M8 = JointGeometry(A_s=36.6e-6, L_eff=0.030, d_2=7.188e-3, pitch=1.25e-3,
                       r_bearing=6e-3, A_contact=52e-6)
    assert k_tr_transverse(M8, m) < k_bend    # d^4 dominates => M8 softer


def test_ktr_bending_without_geom_falls_back_to_axial():
    """bending mode needs geom; geom=None => axial_frac fallback (the AND gate)."""
    m = JointMaterial(k_tr_mode="bending")
    assert k_tr_transverse(None, m) == max(m.k_j_init * 0.3, 1.0)


def test_ktr_bending_gives_realistic_delta_t():
    """delta_t = F_slip/k_tr ~ 0.1-0.5mm (not ~0.001mm) at M16 nominal."""
    m = JointMaterial(k_tr_mode="bending", c_bend=3.0)
    st = SlowState(F_0=50e3)
    slip_lo = resolve_transverse_slip(st, m, 20e3, np.pi / 2, delta_amp=0.1e-3, geom=M16)
    slip_hi = resolve_transverse_slip(st, m, 20e3, np.pi / 2, delta_amp=0.6e-3, geom=M16)
    assert slip_lo == 0.0                      # partial slip (below delta_t)
    assert slip_hi > 0.0                       # gross slip (above delta_t)


def test_backward_compat_axial_frac_slip_unchanged():
    """Default mode: slip identical whether or not geom is passed (geom unused)."""
    m = JointMaterial()
    st = SlowState(F_0=50e3)
    s_no = resolve_transverse_slip(st, m, 20e3, np.pi / 2, delta_amp=0.5e-3)
    s_ge = resolve_transverse_slip(st, m, 20e3, np.pi / 2, delta_amp=0.5e-3, geom=M16)
    assert s_no == s_ge                        # geom ignored in axial_frac
