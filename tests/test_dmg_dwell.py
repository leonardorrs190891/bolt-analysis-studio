"""Fator de dwell do dano (dmg_dwell_exp, par Yang 5/10Hz): dD *= (f_ref/f)^p.
Fretting-corrosao — dose de oxido ∝ tempo de contato. Default 0 = bit-identical."""
import numpy as np
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)


def _geom():
    return JointGeometry(A_s=84.3e-6, L_eff=30e-3, d_2=10.86e-3, pitch=1.75e-3,
                         r_bearing=9e-3, A_contact=117.6e-6)


def _D(freq, p, n=300):
    m = JointMaterial(c_D=0.5, W_ref=1e3, k_dmg_mu=1.0, k_dmg_wear=4.0,
                      dmg_dwell_exp=p, f_ref_dmg=10.0, emb_depth=0.0,
                      C_creep=0.0, mu_thread=0.15, mu_bearing=0.15)
    ana = DynamicStiffnessAnalyzer(_geom(), m, 20e3)
    for _ in range(n):
        ana.step_cycle(5e3, np.pi / 2, freq, delta_amp=1.0e-3)
    return ana.state.D


def test_default_inert():
    assert JointMaterial().dmg_dwell_exp == 0.0
    assert abs(_D(5.0, 0.0) - _D(10.0, 0.0)) < 1e-12   # p=0: freq nao entra em D


def test_lower_freq_more_damage():
    assert _D(5.0, 1.0) > _D(10.0, 1.0) * 1.2          # dwell 2x => dose maior


def test_ref_freq_unchanged():
    assert abs(_D(10.0, 1.0) - _D(10.0, 0.0)) < 1e-12  # em f_ref o fator e 1
