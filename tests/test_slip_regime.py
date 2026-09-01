"""Tests for the Cattaneo-Mindlin slip-regime law (spec 2026-07-07).

g_gross = (slip/(slip+delta_t))^k sharpens the loosening gross-slip fraction
(Rousseau onset); partial_slip_gate = 1-(1-min(r,1))^m grades wear/fretting by
r=Q/(mu*F0*kappa) (Liu2017 pressure slope). Default slip_regime_mode="off" =>
bit-identical. Opt-in F_amp<=mu*F0 Coulomb cap via couple_famp_slip (#4)."""
import numpy as np
import pytest
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    partial_slip_gate, loosening_slip_gate, F_slip_transverse, k_tr_transverse,
)


def _geom(grip_mm=25.0):
    return JointGeometry(A_s=84.3e-6, L_eff=grip_mm * 1e-3, d_2=10.86e-3,
                         pitch=1.75e-3, r_bearing=9e-3, A_contact=117.6e-6)


# ---- Task 1: fields default-inert ----
def test_defaults_inert():
    m = JointMaterial()
    assert m.slip_regime_mode == "off"
    assert m.slip_regime_sharpness == 1.0
    assert m.slip_capacity_coeff == 1.0
    assert m.partial_slip_exp == 1.5
    assert m.couple_famp_slip is False


# ---- Task 2: partial_slip_gate ----
def test_partial_slip_gate_off_is_one():
    m = JointMaterial()  # off
    g = partial_slip_gate(SlowState(F_0=1e4, F_0_init=1e4), _geom(), m,
                          10e3, 0.0, "fret", None)
    assert g == 1.0


def test_partial_slip_gate_grades_below_onset():
    m = JointMaterial(slip_regime_mode="cattaneo_mindlin",
                      slip_capacity_coeff=6.0, partial_slip_exp=1.5, mu_thread=0.15)
    lo = partial_slip_gate(SlowState(F_0=15e3, F_0_init=15e3), _geom(), m,
                           10e3, 0.0, "fret", None)   # r larger
    hi = partial_slip_gate(SlowState(F_0=21e3, F_0_init=21e3), _geom(), m,
                           10e3, 0.0, "fret", None)   # r smaller
    assert 0.0 < hi < lo <= 1.0                        # more preload -> less fret


def test_partial_slip_gate_saturates_gross():
    m = JointMaterial(slip_regime_mode="cattaneo_mindlin",
                      slip_capacity_coeff=1.0, mu_thread=0.15)
    # r = 10e3/(0.15*5e3*1) = 13.3 >> 1 -> gross -> 1.0
    g = partial_slip_gate(SlowState(F_0=5e3, F_0_init=5e3), _geom(), m,
                          10e3, 0.0, "fret", None)
    assert g == 1.0


# ---- Task 3: g_gross branch ----
def test_g_gross_k1_matches_current_fraction():
    geom = _geom()
    base = JointMaterial(k_tr_mode="bending", loosening_slip_coupling="gross_fraction")
    cm1 = JointMaterial(k_tr_mode="bending", slip_regime_mode="cattaneo_mindlin",
                        slip_regime_sharpness=1.0)
    st, slip = SlowState(F_0=1e4, F_0_init=1e4), 0.3e-3
    dt = F_slip_transverse(st, base) / k_tr_transverse(geom, base)
    frac = slip / (slip + dt)
    assert loosening_slip_gate(st, geom, cm1, slip) == pytest.approx(frac, rel=1e-9)
    # and equals the current gross_fraction branch exactly at k=1
    assert loosening_slip_gate(st, geom, cm1, slip) == pytest.approx(
        loosening_slip_gate(st, geom, base, slip), rel=1e-9)


def test_g_gross_sharpens_with_k():
    geom, st, slip = _geom(), SlowState(F_0=1e4, F_0_init=1e4), 0.3e-3
    soft = JointMaterial(k_tr_mode="bending", slip_regime_mode="cattaneo_mindlin",
                         slip_regime_sharpness=1.0)
    hard = JointMaterial(k_tr_mode="bending", slip_regime_mode="cattaneo_mindlin",
                         slip_regime_sharpness=6.0)
    assert loosening_slip_gate(st, geom, hard, slip) < loosening_slip_gate(st, geom, soft, slip)


def test_g_gross_zero_below_onset():
    geom = _geom()
    m = JointMaterial(k_tr_mode="bending", slip_regime_mode="cattaneo_mindlin",
                      slip_regime_sharpness=6.0)
    assert loosening_slip_gate(SlowState(F_0=1e4, F_0_init=1e4), geom, m, 0.0) == 0.0


def test_g_gross_force_mode_inert():
    geom = _geom()
    m = JointMaterial(k_tr_mode="bending", slip_regime_mode="cattaneo_mindlin")
    assert loosening_slip_gate(SlowState(F_0=1e4, F_0_init=1e4), geom, m, None) == 1.0


# ---- Task 4: wiring into wear / thread-fretting ----
def _fret_final(F0, mode, kfret=1.0):
    geom = _geom(30.0)
    kw = dict(emb_depth=3.5e-6, mu_thread=0.15, mu_bearing=0.15, k_thread_fret=kfret)
    if mode:
        kw.update(slip_regime_mode="cattaneo_mindlin", slip_capacity_coeff=6.0)
    ana = DynamicStiffnessAnalyzer(geom, JointMaterial(**kw), F0)
    for _ in range(3000):
        ana.step_cycle(10e3, 0.0, 30.0)                # axial force-mode
    return max(ana.state.F_0, 0.0) / F0


def test_fret_pressure_dependence_steepens():
    on = _fret_final(21e3, True) - _fret_final(15e3, True)
    off = _fret_final(21e3, False) - _fret_final(15e3, False)
    assert on > off                                    # gate steepens d(final)/dP0


# ---- Task 5: bit-identical guard ----
def _run(mat_kw, disp):
    geom = _geom(30.0)
    ana = DynamicStiffnessAnalyzer(geom, JointMaterial(**mat_kw), 20e3)
    for _ in range(500):
        if disp:
            ana.step_cycle(0.4 * 20e3, np.pi / 2, 1.0, delta_amp=0.5e-3)
        else:
            ana.step_cycle(10e3, 0.0, 30.0)
    return max(ana.state.F_0, 0.0)


def test_off_bit_identical():
    base = dict(emb_depth=3.5e-6, mu_thread=0.15, mu_bearing=0.15, k_thread_fret=0.3)
    for disp in (True, False):
        assert _run(base, disp) == _run(dict(base, slip_regime_mode="off"), disp)


# ---- Task 6: F_amp<->delta_amp Coulomb cap (#4) ----
def test_famp_cap_off_default():
    assert JointMaterial().couple_famp_slip is False


def test_famp_cap_limits_drive():
    geom = _geom(30.0)
    common = dict(k_tr_mode="bending", slip_regime_mode="cattaneo_mindlin",
                  loose_torsion_mode="bolt_torsion", eta_loose=15.0,
                  mu_thread=0.15, mu_bearing=0.15, emb_depth=2.5e-6)
    a_on = DynamicStiffnessAnalyzer(geom, JointMaterial(couple_famp_slip=True, **common), 20e3)
    a_off = DynamicStiffnessAnalyzer(geom, JointMaterial(couple_famp_slip=False, **common), 20e3)
    for _ in range(300):
        a_on.step_cycle(50e3, np.pi / 2, 1.0, delta_amp=0.5e-3)   # F_amp >> mu*F0
        a_off.step_cycle(50e3, np.pi / 2, 1.0, delta_amp=0.5e-3)
    assert a_on.state.F_0 >= a_off.state.F_0                       # capped drive loosens no more
