# -*- coding: utf-8 -*-
"""Invariantes da HISTERESE DE STICK (`mu_kinetic_frac`, 2026-08-20).

Fisica de livro: mu estatico > mu cinetico — a 1a abertura do slip transversal
rompe o travamento (interlock/oxido) e o mu de bearing cai ao cinetico, SEM
volta (latch `SlowState.stick_broken`). Motivada pela `yang2019_amp0p4`: o
modelo alcanca a transicao no joelho real do dado (F=0,916*F0) mas o [K(s)]
re-trava e o sistema congela onde a junta real colapsa. Default 1.0 = OFF
EXATO (nem o latch e' escrito).
"""
import math

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, mu_bearing_eff)

GEOM = JointGeometry(A_s=58e-6, L_eff=0.03, d_2=9.03e-3, pitch=1.5e-3,
                     r_bearing=8e-3, A_contact=120e-6)


def _run(mat, n=200, delta=0.2e-3, f0=20000.0):
    ana = DynamicStiffnessAnalyzer(GEOM, mat, f0)
    for _ in range(n):
        ana.step_cycle(F_amp=0.0, theta_load=math.pi / 2, freq=5.0,
                       delta_amp=delta)
    return ana


def test_default_off_bit_identico_e_sem_latch():
    a = _run(JointMaterial())
    b = _run(JointMaterial(mu_kinetic_frac=1.0))
    assert [s.F_0 for s in a.history] == [s.F_0 for s in b.history]
    assert b.state.stick_broken == 0.0        # default nunca escreve o latch


def test_latch_seta_e_mu_cai():
    # delta=0.2mm neste GEOM abre slip desde cedo => o latch seta no 1o ciclo
    # e o mu efetivo cai pela fracao.
    ana = _run(JointMaterial(mu_kinetic_frac=0.8), n=5)
    assert ana.state.stick_broken == 1.0
    mu = mu_bearing_eff(ana.state, ana.mat)
    assert abs(mu - ana.mat.mu_bearing * 0.8) < 1e-12


def test_latch_nao_reverte():
    # o latch persiste mesmo se o slip re-fechar (a ruptura nao re-trava).
    ana = _run(JointMaterial(mu_kinetic_frac=0.8), n=50)
    assert ana.state.stick_broken == 1.0
    ana.state.F_0 = ana.state.F_0_init       # restaura F na mao (re-aperto)
    ana.step_cycle(F_amp=0.0, theta_load=math.pi / 2, freq=5.0,
                   delta_amp=1e-6)           # stick certo
    assert ana.state.stick_broken == 1.0
