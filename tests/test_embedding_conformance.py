"""Preload-dependent embedding saturation (spec 2026-07-08, axial-slope form).

S = min(1, (p_ref_emb/p_init)^emb_conform_exp), p_init = F0_init/A_contact, keyed on
F0_init (constant per run). Default emb_conform_exp=0 => S=1 exact (bit-identical).
Higher preload -> more torque-up pre-conformance -> lower residual embedding -> the
absolute loss falls with F0 -> fractional loss drops faster than 1/F0 -> steeper
d(final)/dP0 (the Liu2017 slope the slip-regime could not close)."""
import numpy as np
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    embedding_conformance_factor, creep_conformance_factor)


def _geom(grip_mm=30.0):
    return JointGeometry(A_s=84.3e-6, L_eff=grip_mm * 1e-3, d_2=10.86e-3,
                         pitch=1.75e-3, r_bearing=9e-3, A_contact=117.6e-6)


def test_default_inert():
    assert JointMaterial().emb_conform_exp == 0.0
    m = JointMaterial()                                   # exp=0
    assert embedding_conformance_factor(SlowState(F_0=20e3, F_0_init=20e3), _geom(), m) == 1.0


def test_factor_clamped_below_pref():
    m = JointMaterial(emb_conform_exp=3.0, p_ref_emb=1e9)   # p_ref >> p_init
    g = embedding_conformance_factor(SlowState(F_0=15e3, F_0_init=15e3), _geom(), m)
    assert g == 1.0                                       # full residual below reference


def test_factor_decreases_with_preload():
    m = JointMaterial(emb_conform_exp=3.0, p_ref_emb=1e8)
    g_lo = embedding_conformance_factor(SlowState(F_0=15e3, F_0_init=15e3), _geom(), m)
    g_hi = embedding_conformance_factor(SlowState(F_0=21e3, F_0_init=21e3), _geom(), m)
    assert g_hi < g_lo <= 1.0                             # more preload -> more conformed


def _final(F0, exp):
    m = JointMaterial(emb_depth=3.5e-6, mu_thread=0.15, mu_bearing=0.15,
                      emb_conform_exp=exp, p_ref_emb=15e3 / 117.6e-6)  # anchor p_ref = p(15kN)
    ana = DynamicStiffnessAnalyzer(_geom(), m, F0)
    for _ in range(2000):
        ana.step_cycle(10e3, 0.0, 30.0)                  # axial force-mode
    return max(ana.state.F_0, 0.0) / F0


def test_steepens_slope():
    off = _final(21e3, 0.0) - _final(15e3, 0.0)          # baseline 1/F0 spread
    on = _final(21e3, 3.0) - _final(15e3, 3.0)           # conformance widens it
    assert on > off


def test_low_end_preserved_when_anchored():
    # p_ref anchored at p(15kN) => S=1 at 15kN => final(15) unchanged vs off (level kept)
    assert abs(_final(15e3, 3.0) - _final(15e3, 0.0)) < 1e-6


# ---- slow-tail: creep conformance (spec 2026-07-08) ----
def test_creep_conformance_default_inert():
    assert JointMaterial().creep_conform_exp == 0.0
    m = JointMaterial(emb_conform_exp=4.0, p_ref_emb=1e8)   # fast on, slow off
    assert creep_conformance_factor(SlowState(F_0=21e3, F_0_init=21e3), _geom(), m) == 1.0


def test_creep_factor_decreases_with_preload():
    m = JointMaterial(creep_conform_exp=2.0, p_ref_emb=1e8)
    g_lo = creep_conformance_factor(SlowState(F_0=15e3, F_0_init=15e3), _geom(), m)
    g_hi = creep_conformance_factor(SlowState(F_0=21e3, F_0_init=21e3), _geom(), m)
    assert g_hi < g_lo <= 1.0


def _final2(F0, exp_fast, exp_slow):
    m = JointMaterial(emb_depth=3.5e-6, mu_thread=0.15, mu_bearing=0.15,
                      emb_conform_exp=exp_fast, creep_conform_exp=exp_slow,
                      p_ref_emb=15e3 / 117.6e-6)
    ana = DynamicStiffnessAnalyzer(_geom(), m, F0)
    for _ in range(3000):
        ana.step_cycle(10e3, 0.0, 30.0)
    return max(ana.state.F_0, 0.0) / F0


def test_slow_tail_steepens_slope_further():
    fast_only = _final2(21e3, 4.0, 0.0) - _final2(15e3, 4.0, 0.0)
    both = _final2(21e3, 4.0, 2.0) - _final2(15e3, 4.0, 2.0)
    assert both > fast_only                       # slow gate adds slope on top


def test_slow_tail_low_end_anchored():
    # S=1 at 15kN for both channels => low end still unchanged
    assert abs(_final2(15e3, 4.0, 2.0) - _final2(15e3, 0.0, 0.0)) < 1e-6
