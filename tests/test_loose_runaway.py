# -*- coding: utf-8 -*-
"""Invariantes do RUNAWAY DE PORCA SOLTA (2026-08-20, zhang2006_fig3 sec9).

Transicao lei-de-potencia -> runaway no ramo graded: abaixo de uma fracao
critica de F0 (`loose_runaway_frac`) o auto-travamento residual deixa de
segurar o backoff e a taxa ganha um boost Hill ate (1+gain). Motivo medido:
o traco theta digitalizado da Fig. 3 do Zhang 2006 dispara 10->42 deg
(razao de taxas ~14x) onde a lei F^fe LIDA (fe=5,80 do theta = 5,93 do P)
desacelera por construcao. Ancoras de leitura: r_c=0,25 (o paper define o
fim do Estagio II em P=25%), gain ~ razao de taxas - 1.
Default frac=0 (ou gain=0) = OFF EXATO.
"""
import math

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)

GEOM = JointGeometry(A_s=84.3e-6, L_eff=0.035, d_2=10.8634e-3, pitch=1.25e-3,
                     r_bearing=9e-3, A_contact=150e-6)
GRADED = dict(loose_rate_mode="graded_scrit", k_loose_graded=0.02,
              s_crit_loose=0.0, loose_arrest_floor=0.0, loose_amp_exp=0.0,
              loose_F_exp=4.0)


def _run(mat, n=400, delta=0.35e-3, f0=20000.0):
    ana = DynamicStiffnessAnalyzer(GEOM, mat, f0)
    for _ in range(n):
        ana.step_cycle(F_amp=0.0, theta_load=math.pi / 2, freq=0.5,
                       delta_amp=delta)
    return ana


def test_default_off_bit_identico():
    # frac=0 (default) e gain>0 com frac=0: ambos BIT-identicos ao baseline.
    a = _run(JointMaterial(**GRADED))
    b = _run(JointMaterial(**GRADED, loose_runaway_frac=0.0,
                           loose_runaway_gain=13.0))
    assert [s.F_0 for s in a.history] == [s.F_0 for s in b.history]


def test_gain_zero_off_exato():
    # frac>0 mas gain=0: OFF exato (o multiplicador nem e' computado).
    a = _run(JointMaterial(**GRADED))
    b = _run(JointMaterial(**GRADED, loose_runaway_frac=0.25,
                           loose_runaway_gain=0.0))
    assert [s.F_0 for s in a.history] == [s.F_0 for s in b.history]


def test_dispara_abaixo_do_limiar_e_quase_inerte_acima():
    # Com o boost, a curva tem de terminar MAIS BAIXA (o disparo drena mais)
    # e o trecho ACIMA do limiar tem de ficar quase intacto (boost suave
    # ~(r_c/r)^k). Compara ciclo-a-ciclo: enquanto F/F0 > 2*r_c, o desvio
    # relativo fica < 2%.
    a = _run(JointMaterial(**GRADED))
    b = _run(JointMaterial(**GRADED, loose_runaway_frac=0.25,
                           loose_runaway_gain=13.0))
    ra = [s.F_0 / 20000.0 for s in a.history]
    rb = [s.F_0 / 20000.0 for s in b.history]
    assert rb[-1] < ra[-1] - 0.01, (rb[-1], ra[-1])
    for x, y in zip(ra, rb):
        if x > 0.50:
            assert abs(y - x) / max(x, 1e-9) < 0.02, (x, y)


def test_monotonia_no_gain():
    # gain maior => final mais baixo (monotonia da alavanca).
    fins = []
    for g in (3.0, 13.0, 40.0):
        b = _run(JointMaterial(**GRADED, loose_runaway_frac=0.25,
                               loose_runaway_gain=g))
        fins.append(b.state.F_0)
    assert fins[0] > fins[1] > fins[2], fins


def test_inerte_no_kernel_torque():
    # Os campos SO sao lidos no ramo graded — no kernel default (torque)
    # nao podem mudar nada.
    base = dict(loose_arrest_floor=0.0)
    a = _run(JointMaterial(**base))
    b = _run(JointMaterial(**base, loose_runaway_frac=0.25,
                           loose_runaway_gain=13.0))
    assert [s.F_0 for s in a.history] == [s.F_0 for s in b.history]
