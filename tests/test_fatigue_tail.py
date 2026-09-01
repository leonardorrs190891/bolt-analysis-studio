"""Tests for the opt-in fatigue-fracture tail (spec 2026-07-08).

FatigueLoss: Miner's D over a bilinear Su-N (Yang) + Goodman mean-stress; cliff at
D>=1 drops F_0 -> fatigue_residual_frac*F_0_init. fatigue_enabled=False (default)
=> zero exact (bit-identical)."""
import numpy as np
import pytest
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    FatigueLoss, sun_life)


def _geom(grip_mm=30.0):
    return JointGeometry(A_s=84.3e-6, L_eff=grip_mm * 1e-3, d_2=10.86e-3,
                         pitch=1.75e-3, r_bearing=9e-3, A_contact=117.6e-6)


def test_defaults_inert():
    m = JointMaterial()
    assert m.fatigue_enabled is False
    assert m.fat_Kt == 3.5 and m.fatigue_residual_frac == 0.0
    assert SlowState(F_0=1.0).D_fatigue == 0.0


def test_sun_life_bilinear_and_endurance():
    m = JointMaterial()
    assert sun_life(5e6, m) == float("inf")                    # below endurance limit
    hi, lo = sun_life(200e6, m), sun_life(80e6, m)
    assert 0.0 < hi < lo                                       # higher stress -> shorter life


def test_goodman_mean_stress_shortens_life():
    # higher preload (mean stress) -> higher sigma_ar -> shorter N_f (more dD)
    m = JointMaterial(fatigue_enabled=True)
    g = _geom()
    r_lo = FatigueLoss().rate(SlowState(F_0=5e3, F_0_init=5e3), g, m, 10e3, 0.0, 30.0, 1)
    r_hi = FatigueLoss().rate(SlowState(F_0=60e3, F_0_init=60e3), g, m, 10e3, 0.0, 30.0, 1)
    assert r_hi["ds"]["D_fatigue"] > r_lo["ds"]["D_fatigue"]


def test_fatigue_off_is_zero():
    r = FatigueLoss().rate(SlowState(F_0=2e4, F_0_init=2e4), _geom(), JointMaterial(),
                           10e3, 0.0, 30.0, 1)
    assert r["dF_0"] == 0.0 and r["dE_dissipated"] == 0.0 and r["ds"] == {}


def test_fatigue_cliff_fires_and_drops_preload():
    # small C1/knee -> N_f small -> D crosses 1 fast -> cliff
    m = JointMaterial(fatigue_enabled=True, fat_C1=1e3, fat_m1=1.0,
                      fat_sigma_knee=1.0, fat_sigma_endurance=1.0)
    ana = DynamicStiffnessAnalyzer(_geom(), m, 20e3)
    fired = False
    for _ in range(1000):
        ana.step_cycle(10e3, 0.0, 30.0)                        # axial force-mode
        if ana.state.F_0 <= 1.0:
            fired = True
            break
    assert fired and ana.state.D_fatigue >= 1.0


def test_fatigue_residual_frac():
    m = JointMaterial(fatigue_enabled=True, fat_C1=1e3, fat_m1=1.0,
                      fat_sigma_knee=1.0, fat_sigma_endurance=1.0,
                      fatigue_residual_frac=0.2)
    ana = DynamicStiffnessAnalyzer(_geom(), m, 20e3)
    for _ in range(1000):
        ana.step_cycle(10e3, 0.0, 30.0)
        if ana.state.D_fatigue >= 1.0:
            break
    assert abs(ana.state.F_0 / 20e3 - 0.2) < 0.02              # settles near residual frac


def _final(mat_kw, disp):
    ana = DynamicStiffnessAnalyzer(_geom(), JointMaterial(**mat_kw), 20e3)
    for _ in range(400):
        if disp:
            ana.step_cycle(0.4 * 20e3, np.pi / 2, 1.0, delta_amp=0.5e-3)
        else:
            ana.step_cycle(10e3, 0.0, 30.0)
    return max(ana.state.F_0, 0.0)


def test_off_bit_identical():
    base = dict(emb_depth=3.5e-6, mu_thread=0.15, mu_bearing=0.15, k_thread_fret=0.3)
    for disp in (True, False):
        assert _final(base, disp) == _final(dict(base, fatigue_enabled=False), disp)
