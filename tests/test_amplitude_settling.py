"""Fator de amplitude relativa do assentamento (estudo de variaveis item 1).

S_rho = min(1,(rho/rho_ref)^q), rho = F_ax_amp/F_0_init. Unifica os dois sweeps
do Liu2017 (fast-loss ~ rho^3.4). Default emb_amp_exp=0 => bit-identical;
transversal (F_ax~0) => inerte por construcao."""
import numpy as np
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    settling_amplitude_factor)


def _geom():
    return JointGeometry(A_s=84.3e-6, L_eff=30e-3, d_2=10.86e-3, pitch=1.75e-3,
                         r_bearing=9e-3, A_contact=117.6e-6)


def test_default_inert():
    m = JointMaterial()
    assert m.emb_amp_exp == 0.0
    assert settling_amplitude_factor(SlowState(F_0=18e3, F_0_init=18e3), m,
                                     10e3, 0.0) == 1.0


def test_transverse_inert():
    m = JointMaterial(emb_amp_exp=3.4)
    # theta=pi/2 => F_ax ~ 0 => S=1 exato (settling transversal intocado)
    assert settling_amplitude_factor(SlowState(F_0=18e3, F_0_init=18e3), m,
                                     10e3, np.pi / 2) == 1.0


def test_rho_power_law():
    m = JointMaterial(emb_amp_exp=3.4, rho_ref_emb=0.8)   # ref alto: sem clamp no par
    st = SlowState(F_0=18e3, F_0_init=18e3)
    s1 = settling_amplitude_factor(st, m, 7.5e3, 0.0)
    s2 = settling_amplitude_factor(st, m, 12.5e3, 0.0)
    assert abs(s2 / s1 - (12.5 / 7.5) ** 3.4) < 1e-9


def test_clamped_at_one_beyond_ref():
    m = JointMaterial(emb_amp_exp=3.4, rho_ref_emb=0.5)
    st = SlowState(F_0=10e3, F_0_init=10e3)
    assert settling_amplitude_factor(st, m, 8e3, 0.0) == 1.0   # rho=0.8 > ref


def test_unifies_both_sweeps_in_engine():
    # fast settling loss must scale ~rho^q in BOTH directions:
    # (a) A_F sweep at fixed F0; (b) P0 sweep at fixed A_F.
    def fast_loss(F0, F_amp):
        m = JointMaterial(emb_depth=15e-6, N_emb=15.0, emb_amp_exp=3.4,
                          rho_ref_emb=0.667, mu_thread=0.15, mu_bearing=0.15,
                          C_creep=0.0)                        # isola o settling
        ana = DynamicStiffnessAnalyzer(_geom(), m, F0)
        for _ in range(200):
            ana.step_cycle(F_amp, 0.0, 30.0)
        return 1.0 - ana.state.F_0 / F0
    q = 3.4
    # (a) amplitude sweep
    la, lb = fast_loss(18e3, 7.5e3), fast_loss(18e3, 12.5e3)
    assert abs(np.log(lb / la) / np.log(12.5 / 7.5) - q) < 0.3
    # (b) preload sweep (fixed A_F): loss ~ S(rho)/F0 ~ F0^-(q+1)
    lc, ld = fast_loss(15e3, 10e3), fast_loss(21e3, 10e3)
    assert abs(np.log(lc / ld) / np.log(21.0 / 15.0) - (q + 1)) < 0.3
