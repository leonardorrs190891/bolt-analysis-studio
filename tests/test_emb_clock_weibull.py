# -*- coding: utf-8 -*-
"""Invariantes do RELOGIO SIGMOIDE do embedding (`emb_clock_m`, 2026-08-21).

Weibull m>1 no relogio de Estagio I: plato inicial + joelho + saturacao —
a forma que o exponencial nao faz. Motivada pela `lu2024_fig14_amp0p25_long`
(stick TOTAL medido; plato de 27-56 ciclos publicado). Implementacao
state-based exata via N implicito. m=1 (default) = ramo antigo BIT-IDENTICO.
"""
import math

import numpy as np

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)

GEOM = JointGeometry(A_s=36.6e-6, L_eff=0.02, d_2=7.188e-3, pitch=1.25e-3,
                     r_bearing=6.5e-3, A_contact=90e-6)
BASE = dict(emb_depth=20e-6, N_emb=300.0, C_creep=0.0, K_archard=0.0,
            k_wear_spec=0.0, loose_arrest_floor=0.9)


def _traj(mat, n=900, delta=0.25e-3, f0=10500.0):
    ana = DynamicStiffnessAnalyzer(GEOM, mat, f0)
    out = []
    for _ in range(n):
        ana.step_cycle(F_amp=0.0, theta_load=math.pi / 2, freq=1.0,
                       delta_amp=delta)
        out.append(ana.state.delta_emb)
    return np.array(out)


def test_default_off_bit_identico():
    a = _traj(JointMaterial(**BASE))
    b = _traj(JointMaterial(**BASE, emb_clock_m=1.0))
    assert np.array_equal(a, b)


def test_m1_reproduz_closed_form_norton():
    # sanity: o caminho default segue a forma fechada de Norton.
    d = _traj(JointMaterial(**BASE))
    alvo = d[-1] / (1.0 - math.exp(-900.0 / 300.0))
    for N in (100, 300, 600):
        esperado = alvo * (1.0 - math.exp(-N / 300.0))
        assert abs(d[N - 1] - esperado) / esperado < 0.02, (N, d[N - 1], esperado)


def test_m2_reproduz_weibull_closed_form():
    # a implementacao state-based tem de seguir o closed-form Weibull para
    # trajetoria virgem (erro < 2% nos pontos de controle).
    d = _traj(JointMaterial(**BASE, emb_clock_m=2.0))
    alvo = d[-1] / (1.0 - math.exp(-((900.0 / 300.0) ** 2)))
    for N in (60, 150, 300, 600):
        esperado = alvo * (1.0 - math.exp(-((N / 300.0) ** 2)))
        assert abs(d[N - 1] - esperado) / max(esperado, 1e-12) < 0.02, (
            N, d[N - 1], esperado)


def test_m_maior_faz_plato_inicial():
    # Em N = N_emb/10, o Weibull m=2 consumiu MUITO menos que o exponencial
    # (o plato); em N = 3*N_emb ambos saturaram (mesma assintota).
    a = _traj(JointMaterial(**BASE))
    b = _traj(JointMaterial(**BASE, emb_clock_m=2.0))
    assert b[29] < 0.35 * a[29], (b[29], a[29])
    assert abs(b[-1] - a[-1]) / a[-1] < 0.06, (b[-1], a[-1])
