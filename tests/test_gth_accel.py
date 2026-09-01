# -*- coding: utf-8 -*-
"""Invariantes da ACELERACAO PROGRESSIVA do gth (`gth_accel_p`, 2026-08-20).

Motivada pela `yang2019_M10_amp0p4_5Hz`: o dado e' plano por ~4700 ciclos e
depois ACELERA (taxa 11,6x para N-efetivo 3,8x ⇒ p~2 no log-log) — e nenhum
canal do engine acelera em stick (o damage nao cresce: driver e' slip macro).
p=0 (default) = OFF EXATO (taxa constante pos-onset, caminho antigo).
"""
import math

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)

GEOM = JointGeometry(A_s=58e-6, L_eff=0.03, d_2=9.03e-3, pitch=1.5e-3,
                     r_bearing=8e-3, A_contact=120e-6)
# O gth so age em STICK — e stick exige mu*F/k_tr >= delta. Neste GEOM isso
# da ~1,2 um com mu=0,15; o teste sobe mu para 3,0 (invariante de CODIGO, nao
# fisica) e usa delta=20 um => mu*F/k_tr ~24 um > delta = stick garantido.
# rq = (0.02/0.5)^3.8 = 4.9e-6 => onset (A0=2e-3) em ~410 ciclos. A 1a versao
# deste teste rodava em SLIP e media os canais macro no lugar do gth.
GTH = dict(gth_k=2000.0, gth_A0=2e-3, emb_depth=0.0, C_creep=0.0,
           K_archard=0.0, k_wear_spec=0.0, mu_bearing=3.0, mu_thread=3.0)


def _run(mat, n=2000, delta=0.02e-3, f0=20000.0):
    ana = DynamicStiffnessAnalyzer(GEOM, mat, f0)
    out = []
    for _ in range(n):
        ana.step_cycle(F_amp=0.0, theta_load=math.pi / 2, freq=5.0,
                       delta_amp=delta)
        out.append(ana.state.F_0)
    return ana, out


def test_p_zero_off_bit_identico():
    a, fa = _run(JointMaterial(**GTH))
    b, fb = _run(JointMaterial(**GTH, gth_accel_p=0.0))
    assert fa == fb


def test_aceleracao_pos_onset():
    # com p>0 a taxa CRESCE com o acumulado: a perda no 2o trecho pos-onset
    # tem de ser maior que no 1o (no caminho antigo e' igual).
    _, f = _run(JointMaterial(**GTH, gth_accel_p=2.0), n=3000)
    # achar onset real (1a queda)
    i_on = next(i for i in range(1, len(f)) if f[i] < f[i - 1] - 1e-9)
    seg = (len(f) - i_on) // 2
    d1 = f[i_on] - f[i_on + seg]
    d2 = f[i_on + seg] - f[i_on + 2 * seg - 1]
    assert d2 > 1.5 * d1


def test_suave_no_onset():
    # com p>0 a taxa no ciclo do onset e' ~zero (fator (~0)^p), sem degrau.
    _, f0 = _run(JointMaterial(**GTH), n=1500)
    _, fp = _run(JointMaterial(**GTH, gth_accel_p=2.0), n=1500)
    i_on = next(i for i in range(1, len(f0)) if f0[i] < f0[i - 1] - 1e-9)
    passo_antigo = f0[i_on - 1] - f0[i_on + 1]
    passo_novo = fp[i_on - 1] - fp[i_on + 1]
    assert passo_novo < passo_antigo
