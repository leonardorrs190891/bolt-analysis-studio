"""Tests for thread-galling recovery decline (spec 2026-07-07, §4.10 G4).

mu_thread_tighten_eff(D) = mu_thread*(1+k_gall*D), used ONLY in tightening_torque:
a damaged joint recovers less preload at fixed torque. Default k_gall=0 = bit-identical.
Scoped to the re-torque event => step_cycle / T_resistance (the collapse physics) untouched."""
import numpy as np
import pytest
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    tightening_torque, mu_thread_tighten_eff,
)


def _m12_geom():
    return JointGeometry(A_s=84.3e-6, L_eff=50e-3, d_2=10.86e-3,
                         pitch=1.75e-3, r_bearing=9e-3, A_contact=117.6e-6)


def test_default_k_gall_zero():
    assert JointMaterial().k_gall == 0.0


def test_galling_inert_at_D0_or_kgall0():
    geom = _m12_geom()
    m0 = JointMaterial(mu_thread=0.2, k_gall=0.0)
    m5 = JointMaterial(mu_thread=0.2, k_gall=5.0)
    stD = SlowState(F_0=2e4, F_0_init=2e4, D=0.3)
    st0 = SlowState(F_0=2e4, F_0_init=2e4, D=0.0)
    assert mu_thread_tighten_eff(stD, m0) == 0.2          # k_gall=0 -> inert even at D>0
    assert mu_thread_tighten_eff(st0, m5) == 0.2          # D=0 -> inert even at k_gall>0
    # tightening_torque bit-identical when k_gall=0 (vs a plain default material)
    assert (tightening_torque(1.0, stD, geom, m0)
            == tightening_torque(1.0, stD, geom, JointMaterial(mu_thread=0.2)))


def test_galling_raises_nut_factor_lowers_recovery():
    geom = _m12_geom()
    m = JointMaterial(mu_thread=0.2, mu_bearing=0.2, k_gall=2.0)
    c0 = tightening_torque(1.0, SlowState(F_0=2e4, F_0_init=2e4, D=0.0), geom, m)
    c3 = tightening_torque(1.0, SlowState(F_0=2e4, F_0_init=2e4, D=0.3), geom, m)
    c6 = tightening_torque(1.0, SlowState(F_0=2e4, F_0_init=2e4, D=0.6), geom, m)
    assert c0 < c3 < c6                                   # nut factor rises with D
    assert 80.0 / c0 > 80.0 / c3 > 80.0 / c6              # recovered F0 = T/coeff declines


def test_galling_scoped_to_tightening_not_cycling():
    # k_gall must NOT affect step_cycle / T_resistance (only tightening_torque).
    geom = _m12_geom()

    def run(kg):
        m = JointMaterial(mu_thread=0.15, mu_bearing=0.15, k_gall=kg,
                          c_D=0.5, k_dmg_wear=1.0)
        ana = DynamicStiffnessAnalyzer(geom, m, 20000.0, initial_damage=0.3)
        for _ in range(20):
            ana.step_cycle(5000.0, np.pi / 2, 12.5, delta_amp=0.3e-3)
        return ana.state.F_0, ana.state.D

    f0_0, d_0 = run(0.0)
    f0_5, d_5 = run(5.0)
    assert f0_0 == f0_5 and d_0 == d_5                    # cycling identical for any k_gall


def test_retighten_torque_declines_with_damage():
    # End-to-end: same joint, retighten(torque) at higher D recovers less preload.
    geom = _m12_geom()
    m = JointMaterial(mu_thread=0.2, mu_bearing=0.2, k_gall=2.0)
    a_lo = DynamicStiffnessAnalyzer(geom, m, 20000.0, initial_damage=0.1)
    a_hi = DynamicStiffnessAnalyzer(geom, m, 20000.0, initial_damage=0.5)
    a_lo.state.F_0 = 5000.0
    a_hi.state.F_0 = 5000.0
    a_lo.retighten(applied_torque=80.0)
    a_hi.retighten(applied_torque=80.0)
    assert a_hi.state.F_0 < a_lo.state.F_0                # more damage -> less recovery
