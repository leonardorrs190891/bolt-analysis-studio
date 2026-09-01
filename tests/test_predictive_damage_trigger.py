"""Predictive damage-onset trigger (spec 2026-07-05). W_crit gate on D-growth."""
import numpy as np
import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    damage_onset_gate,
)

M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)


def _run(mat, F0, n, delta=0.5e-3):
    ana = DynamicStiffnessAnalyzer(M16, mat, F0)
    for _ in range(n):
        ana.step_cycle(20e3, np.pi / 2, 0.5, delta_amp=delta)
    return ana


def test_gate_transparent_when_W_crit_nonpositive():
    mat = JointMaterial()  # W_crit default 0.0
    for w in (0.0, 1e3, 1e9):
        assert damage_onset_gate(SlowState(F_0=50e3, W_slip_acc=w), mat) == 1.0


def test_gate_hill_shape():
    mat = JointMaterial(W_crit=1e4, dmg_onset_sharpness=4.0)
    g_lo = damage_onset_gate(SlowState(F_0=50e3, W_slip_acc=1e3), mat)   # below
    g_at = damage_onset_gate(SlowState(F_0=50e3, W_slip_acc=1e4), mat)   # at
    g_hi = damage_onset_gate(SlowState(F_0=50e3, W_slip_acc=1e6), mat)   # above
    assert g_lo < 0.05
    assert g_at == pytest.approx(0.5)
    assert g_hi > 0.95
    assert g_lo < g_at < g_hi


def test_W_crit_default_transparent_but_can_suppress():
    """W_crit=0 (default) => dano UNGATED (D cresce como antes do gate); W_crit
    alto => o gate suprime (D=0). Contrasta os dois (nao tautologico): prova que
    o default e transparente E que o gate age quando setado."""
    common = dict(c_D=2.0, k_dmg_wear=4.0, k_dmg_mu=1.0)
    d_default = _run(JointMaterial(**common), 120e3, 200).state.D       # W_crit=0 default
    d_suppressed = _run(JointMaterial(**common, W_crit=1e9), 120e3, 200).state.D
    assert d_default > 0.0            # default (W_crit=0) => dano cresceu (ungated)
    assert d_suppressed < 1e-6        # W_crit alto => gate suprime (Hill assintotico, ~0)
    assert d_default > d_suppressed   # o gate faz diferenca (nao tautologico)


def test_default_inert_no_damage_regardless_of_W_crit():
    """c_D=0 (default) => D stays 0 even with W_crit set."""
    d = _run(JointMaterial(W_crit=1e4), 120e3, 200).state.D
    assert d == 0.0


def test_onset_delays_then_grows_damage():
    """With c_D>0 and W_crit>0: D stays ~0 until the dose crosses W_crit, then grows."""
    common = dict(c_D=2.0, k_dmg_wear=4.0, k_dmg_mu=1.0)
    d_gated = _run(JointMaterial(**common, W_crit=5e4), 120e3, 2000).state.D
    d_ungated = _run(JointMaterial(**common, W_crit=0.0), 120e3, 2000).state.D
    assert d_gated < d_ungated                        # onset delayed the growth
    assert d_gated > 0.0                              # but eventually grows (dose crossed)
