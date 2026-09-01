"""Tests for the re-tightening operation + damage-coupled embedding renewal
(spec/plan 2026-07-07)."""
import numpy as np
import pytest
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    tightening_torque, THREAD_FLANK_ANGLE,
)


def _m12_geom():
    # M12x1.75: A_s=84.3 mm^2, d2=10.86 mm, pitch=1.75 mm, r_bearing=9 mm, grip=30 mm
    return JointGeometry(A_s=84.3e-6, L_eff=30e-3, d_2=10.86e-3,
                         pitch=1.75e-3, r_bearing=9e-3, A_contact=117.6e-6)


# ---- Task 1: tightening_torque (Motosh torque<->preload) --------------------

def test_tightening_torque_roundtrip():
    geom = _m12_geom()
    mat = JointMaterial(mu_thread=0.2, mu_bearing=0.2)
    st = SlowState(F_0=20000.0, F_0_init=20000.0)
    T = tightening_torque(20000.0, st, geom, mat)
    coeff = tightening_torque(1.0, st, geom, mat)
    assert abs(T / coeff - 20000.0) < 1e-6                 # linear inversion
    assert 15e3 < 80.0 / coeff < 30e3                      # M12 dry: 80 Nm -> ~20-28 kN


def test_tightening_torque_zero_damage_no_mu_coupling():
    # Frozen physics has k_dmg_mu=0 -> damage must NOT change the coeff (flat recovery).
    geom = _m12_geom()
    mat = JointMaterial(mu_thread=0.2, mu_bearing=0.2)   # k_dmg_mu default 0.0
    c0 = tightening_torque(1.0, SlowState(F_0=2e4, F_0_init=2e4, D=0.0), geom, mat)
    cD = tightening_torque(1.0, SlowState(F_0=2e4, F_0_init=2e4, D=0.3), geom, mat)
    assert abs(cD - c0) < 1e-15                            # flat: D has no effect at k_dmg_mu=0


def test_tightening_torque_kdmgmu_raises_recovery():
    # If k_dmg_mu>0 were set, damage lowers mu_bearing_eff -> lower coeff -> MORE recovery.
    geom = _m12_geom()
    mat = JointMaterial(mu_thread=0.2, mu_bearing=0.2, k_dmg_mu=1.0)
    c0 = tightening_torque(1.0, SlowState(F_0=2e4, F_0_init=2e4, D=0.0), geom, mat)
    cD = tightening_torque(1.0, SlowState(F_0=2e4, F_0_init=2e4, D=0.3), geom, mat)
    assert cD < c0
    assert 80.0 / cD > 80.0 / c0                           # pre-registered wrong sign


# ---- Task 2: retighten() + k_emb_renew --------------------------------------

def test_retighten_new_F0_sets_preload_and_resets_theta():
    ana = DynamicStiffnessAnalyzer(_m12_geom(), JointMaterial(), 20000.0)
    ana.state.theta_loose = 0.05
    ana.state.F_0 = 15000.0
    f0_init = ana.state.F_0_init
    ana.retighten(new_F0=19000.0)
    assert ana.state.F_0 == 19000.0
    assert ana.state.theta_loose == 0.0
    assert ana.state.F_0_init == f0_init            # GW reference unchanged


def test_retighten_default_keeps_delta_emb_backward_compat():
    ana = DynamicStiffnessAnalyzer(_m12_geom(), JointMaterial(), 20000.0)  # k_emb_renew=0
    ana.state.delta_emb = 5e-6
    ana.state.D = 0.3
    ana.retighten(new_F0=19000.0)
    assert ana.state.delta_emb == 5e-6              # inert: no renewal


def test_retighten_renews_delta_emb_with_damage():
    ana = DynamicStiffnessAnalyzer(_m12_geom(), JointMaterial(k_emb_renew=1.0), 20000.0)
    ana.state.delta_emb = 6e-6
    ana.state.D = 0.3
    ana.retighten(new_F0=19000.0)
    assert abs(ana.state.delta_emb - 6e-6 * (1.0 - 1.0 * 0.3)) < 1e-15   # 4.2e-6


def test_retighten_renewal_clamped_nonnegative():
    ana = DynamicStiffnessAnalyzer(_m12_geom(), JointMaterial(k_emb_renew=5.0), 20000.0)
    ana.state.delta_emb = 6e-6
    ana.state.D = 0.9                                # k*D=4.5 > 1 -> would go negative
    ana.retighten(new_F0=19000.0)
    assert ana.state.delta_emb == 0.0               # clamped


def test_retighten_persists_damage_creep_wear_and_clock():
    # Seed non-zero damage (default c_D=0 keeps it constant) so the D-persistence
    # check is meaningful, not the tautology 0.0 == 0.0.
    ana = DynamicStiffnessAnalyzer(_m12_geom(), JointMaterial(), 20000.0,
                                   initial_damage=0.3)
    for _ in range(10):
        ana.step_cycle(5000.0, np.pi / 2, 12.5, delta_amp=0.3e-3)
    cc, D, dc, dw = (ana._cycle_counter, ana.state.D,
                     ana.state.delta_creep, ana.state.delta_wear)
    assert D == 0.3                                 # non-trivial damage going in
    ana.retighten(new_F0=19000.0)
    assert ana._cycle_counter == cc                 # creep clock persists
    assert ana.state.D == D                         # damage persists (0.3, not reset)
    assert ana.state.delta_creep == dc
    assert ana.state.delta_wear == dw


def test_retighten_torque_predicts_flat_recovery_at_kdmgmu0():
    geom = _m12_geom()
    mat = JointMaterial(mu_thread=0.2, mu_bearing=0.2)     # k_dmg_mu=0
    ana = DynamicStiffnessAnalyzer(geom, mat, 20000.0)
    ana.state.F_0 = 12000.0
    ana.state.D = 0.3
    ana.retighten(applied_torque=80.0)
    coeff = tightening_torque(1.0, ana.state, geom, mat)
    assert abs(ana.state.F_0 - 80.0 / coeff) < 1e-6
    assert 15e3 < ana.state.F_0 < 30e3


def test_retighten_rebases_energy_budget():
    ana = DynamicStiffnessAnalyzer(_m12_geom(), JointMaterial(), 20000.0)
    for _ in range(50):
        ana.step_cycle(5000.0, np.pi / 2, 12.5, delta_amp=0.3e-3)
    ana.retighten(new_F0=19000.0)
    assert ana.energy.W_ext == 0.0
    assert ana.energy.W_diss_total == 0.0
    assert abs(ana.energy.U_released) < 1e-9        # U_stored == U_stored_init (fresh baseline)
    assert abs(ana.energy.conservation_residual) < 1e-9


def test_retighten_requires_exactly_one_arg():
    ana = DynamicStiffnessAnalyzer(_m12_geom(), JointMaterial(), 20000.0)
    with pytest.raises(ValueError):
        ana.retighten()
    with pytest.raises(ValueError):
        ana.retighten(applied_torque=80.0, new_F0=19000.0)


def test_retighten_rejects_negative_preload():
    ana = DynamicStiffnessAnalyzer(_m12_geom(), JointMaterial(), 20000.0)
    with pytest.raises(ValueError):
        ana.retighten(new_F0=-1.0)


def test_retighten_renewal_upper_clamped_to_target():
    # Defensive upper clamp: if delta_emb somehow exceeds target, renewal caps it.
    mat = JointMaterial(k_emb_renew=0.0)            # no renewal -> renewed == delta_emb
    ana = DynamicStiffnessAnalyzer(_m12_geom(), mat, 20000.0)
    target = mat.emb_depth        # Estagio B: k_emb_scale removido
    ana.state.delta_emb = target * 2.0              # artificially above target
    ana.retighten(new_F0=19000.0)
    assert ana.state.delta_emb == target            # clamped down to target
