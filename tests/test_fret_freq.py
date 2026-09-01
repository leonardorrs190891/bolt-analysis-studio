"""Dependencia de FREQUENCIA do fretting axial — fret_freq_exp (sec4.39, #9).

O dado Li2022ti mostra perda por fretting crescendo quando a frequencia cai
(10Hz -17.9% / 20Hz -8.9%). O modelo era freq-CEGO (spread 0.006 vs dado 0.088).
O fator (f_ref/f)^exp supre esse gap. Gates:
  1. fret_freq_exp=0 (default) => BIT-IDENTICAL (freq-independente como antes).
  2. em f=f_ref => fator 1.0 (identico ao freq-independente).
  3. freq menor => MAIS perda (spread na direcao certa).
  4. transversal (F_ax=0) => inerte independente de exp.
  5. k_thread_fret=0 => totalmente inerte independente de exp.
"""
import numpy as np
import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)


def _geom():
    # M10-ish axial
    return JointGeometry(
        E=210e9, A_s=58e-6, L_eff=25e-3, d_2=9.03e-3, pitch=1.5e-3,
        r_bearing=8e-3, A_contact=8e-5,
    )


def _mat(**kw):
    base = dict(emb_depth=9.5e-6, mu_thread=0.15, mu_bearing=0.15,
                k_thread_fret=1.0)
    base.update(kw)
    return JointMaterial(**base)


def _run_axial(mat, freq, n=2000, F0=12.5e3, F_amp=10e3):
    ana = DynamicStiffnessAnalyzer(_geom(), mat, F0)
    for _ in range(n):
        ana.step_cycle(F_amp, 0.0, freq)          # theta=0 => AXIAL
    return max(ana.state.F_0, 0.0) / F0


def test_default_freq_blind_bit_identical():
    """fret_freq_exp=0 (default) => identico a freq-independente (bit-identical)."""
    r_a = _run_axial(_mat(), 10.0)
    r_b = _run_axial(_mat(), 20.0)
    # freq-cego: as duas frequencias dao ~o mesmo (so creep/dwell muda, minimo)
    # o ponto e' que o campo default nao introduz separacao
    assert JointMaterial(emb_depth=9.5e-6).fret_freq_exp == 0.0
    r_exp0 = _run_axial(_mat(fret_freq_exp=0.0), 10.0)
    assert r_a == r_exp0                            # exp=0 == campo ausente


def test_lower_freq_more_loss():
    """Com exp>0, frequencia MENOR => MAIS perda (a assinatura do dado)."""
    m = _mat(fret_freq_exp=1.0, f_ref_fret=15.0)
    r_10 = _run_axial(m, 10.0)
    r_15 = _run_axial(m, 15.0)
    r_20 = _run_axial(m, 20.0)
    # ordem: 10Hz perde mais (menor F0) que 15 que 20
    assert r_10 < r_15 < r_20, f"esperado 10<15<20: {r_10:.3f} {r_15:.3f} {r_20:.3f}"


def test_ref_freq_factor_unity():
    """Em f=f_ref o fator e' 1.0 => identico ao freq-independente."""
    m_exp = _mat(fret_freq_exp=1.0, f_ref_fret=15.0)
    m_flat = _mat(fret_freq_exp=0.0)
    assert _run_axial(m_exp, 15.0) == pytest.approx(_run_axial(m_flat, 15.0), abs=1e-9)


def test_exponent_controls_spread():
    """Expoente maior => spread de frequencia maior (a magnitude e' fitavel/lida)."""
    def spread(exp):
        m = _mat(fret_freq_exp=exp, f_ref_fret=15.0)
        return _run_axial(m, 20.0) - _run_axial(m, 10.0)   # >0 (20Hz retem mais)
    s1 = spread(0.5)
    s2 = spread(1.5)
    assert s2 > s1 > 0, f"spread deveria crescer com exp: {s1:.4f} {s2:.4f}"


def test_transverse_inert():
    """Em transversal (theta=pi/2, F_ax=0) o fretting freq-dep e' inerte."""
    m_flat = JointMaterial(emb_depth=9.5e-6, mu_thread=0.15, mu_bearing=0.15,
                           k_thread_fret=1.0, fret_freq_exp=0.0)
    m_freq = JointMaterial(emb_depth=9.5e-6, mu_thread=0.15, mu_bearing=0.15,
                           k_thread_fret=1.0, fret_freq_exp=1.5, f_ref_fret=15.0)
    a1 = DynamicStiffnessAnalyzer(_geom(), m_flat, 12.5e3)
    a2 = DynamicStiffnessAnalyzer(_geom(), m_freq, 12.5e3)
    for _ in range(500):
        a1.step_cycle(10e3, np.pi / 2, 10.0)       # transversal
        a2.step_cycle(10e3, np.pi / 2, 10.0)
    assert a1.state.F_0 == pytest.approx(a2.state.F_0, abs=1e-6)


def test_k_fret_zero_totally_inert():
    """k_thread_fret=0 => fretting OFF, exp irrelevante (bit-identical)."""
    m_off = JointMaterial(emb_depth=9.5e-6, k_thread_fret=0.0, fret_freq_exp=0.0)
    m_freq = JointMaterial(emb_depth=9.5e-6, k_thread_fret=0.0, fret_freq_exp=2.0)
    assert _run_axial(m_off, 10.0) == _run_axial(m_freq, 10.0)
