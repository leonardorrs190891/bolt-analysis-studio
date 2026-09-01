# -*- coding: utf-8 -*-
"""Invariantes do FREE-SPIN CINEMATICO (sec4.56, 2026-08-19).

`free_spin_kin` = fracao da rotacao RELATIVA porca-parafuso do kernel
graded_scrit que NAO drena preload. Fisica: a rigidez de dreno real do laco
(serie parafuso+membro+interfaces) e' menor que o k_b puro que a helice usa;
o dado publica a lei (Rousseau 2025 Fig. 5: dF/dtheta = 920/894 N/deg em
t10/t12, r2 0.9997/0.9969, contra k_b*lead = 3278). Default 0.0 = OFF exato.
"""
import math

import numpy as np

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)

GEOM = JointGeometry(A_s=84.3e-6, L_eff=0.035, d_2=10.8634e-3, pitch=1.75e-3,
                     r_bearing=9e-3, A_contact=150e-6)
GRADED = dict(loose_rate_mode="graded_scrit", k_loose_graded=0.05,
              s_crit_loose=0.0, loose_arrest_floor=0.0)


def _run(mat, n=120, delta=0.05e-3, f0=10250.0):
    ana = DynamicStiffnessAnalyzer(GEOM, mat, f0)
    for _ in range(n):
        ana.step_cycle(F_amp=0.0, theta_load=math.pi / 2, freq=1.0,
                       delta_amp=delta)
    return ana


def test_default_off_bit_identico():
    # fsk=0.0 (default) tem de ser BIT-identico a nao passar o campo.
    a = _run(JointMaterial(**GRADED))
    b = _run(JointMaterial(**GRADED, free_spin_kin=0.0))
    ra = [s.F_0 for s in a.history]
    rb = [s.F_0 for s in b.history]
    assert ra == rb


def test_inerte_no_kernel_torque():
    # O campo SO e' lido no ramo graded_scrit — no kernel default (torque)
    # fsk>0 nao pode mudar nada.
    base = dict(loose_arrest_floor=0.0)
    a = _run(JointMaterial(**base))
    b = _run(JointMaterial(**base, free_spin_kin=0.75))
    assert [s.F_0 for s in a.history] == [s.F_0 for s in b.history]


def test_fsk_reduz_dreno_sem_tocar_theta_no_1o_ciclo():
    # No 1o ciclo (mesmo estado inicial), dF_0 escala por (1-fsk) e o
    # theta_loose e' IDENTICO — fsk fraciona o dreno, nao a rotacao.
    a = _run(JointMaterial(**GRADED), n=1)
    b = _run(JointMaterial(**GRADED, free_spin_kin=0.75), n=1)
    th_a = a.state.theta_loose
    th_b = b.state.theta_loose
    assert th_a > 0.0
    assert abs(th_b - th_a) < 1e-15
    dfa = 10250.0 - a.state.F_0
    dfb = 10250.0 - b.state.F_0
    # a perda ROTACIONAL escala 4x; ha' perda nao-rotacional (emb/creep) comum
    rot_a = a.history[0].dF_0_by_mech.get("rotational_loosening", 0.0)
    rot_b = b.history[0].dF_0_by_mech.get("rotational_loosening", 0.0)
    assert rot_a < 0.0
    assert abs(rot_b - 0.25 * rot_a) < 1e-9
    assert dfb < dfa


def _trajetoria(mat, n=400, f0=10250.0):
    ana = DynamicStiffnessAnalyzer(GEOM, mat, f0)
    ratios, thetas = [], []
    for _ in range(n):
        ana.step_cycle(F_amp=0.0, theta_load=math.pi / 2, freq=1.0,
                       delta_amp=0.05e-3)
        ratios.append(ana.state.F_0 / f0)
        thetas.append(math.degrees(ana.state.theta_loose))
    return np.array(ratios), np.array(thetas)


def test_mais_theta_para_a_mesma_perda():
    # Com fsk=0.75, para drenar a MESMA pre-carga o kernel precisa ~4x mais
    # rotacao — a assinatura Rousseau (theta medido >> perda/(k_b*lead)).
    # Setup rotacional-PURO (emb/creep mortos) para a razao ser limpa.
    puro = dict(GRADED, emb_depth=0.0, C_creep=0.0)
    ra, tha = _trajetoria(JointMaterial(**puro), n=1200)
    rb, thb = _trajetoria(JointMaterial(**puro, free_spin_kin=0.75), n=1200)
    alvo = 0.60
    if ra.min() > alvo or rb.min() > alvo:
        raise AssertionError("dose da sonda nao alcancou o alvo de 0.60")
    th_a = tha[int(np.argmax(ra <= alvo))]
    th_b = thb[int(np.argmax(rb <= alvo))]
    assert th_b > 3.0 * th_a


def test_clamp_nao_zera_o_dreno():
    # fsk fora de [0,1) e' clampado a 0.999 — o dreno nunca vira 0 exato.
    b = _run(JointMaterial(**GRADED, free_spin_kin=5.0), n=200)
    rot = sum(s.dF_0_by_mech.get("rotational_loosening", 0.0)
              for s in b.history)
    assert rot < 0.0


def test_loose_amp_exp_age_no_graded():
    # PR-21 no graded (2026-08-19): a docstring prometia o exp no termo
    # graded_scrit e o ramo nao o lia (medido inerte). Agora: exp=1 e'
    # bit-identico; exp=0 da taxa CONSTANTE (quantum por ciclo) — com slip
    # abaixo de LOOSE_AMP_REF a taxa constante e' MAIOR que a linear.
    a = _run(JointMaterial(**GRADED), n=60)
    b = _run(JointMaterial(**GRADED, loose_amp_exp=1.0), n=60)
    assert [s.F_0 for s in a.history] == [s.F_0 for s in b.history]
    c = _run(JointMaterial(**GRADED, loose_amp_exp=0.0), n=60)
    rot_a = sum(s.dF_0_by_mech.get("rotational_loosening", 0.0)
                for s in a.history)
    rot_c = sum(s.dF_0_by_mech.get("rotational_loosening", 0.0)
                for s in c.history)
    assert rot_c < rot_a < 0.0


def test_conservacao_com_fsk_ativo():
    # dE fica com a rotacao TOTAL (suprido por W_ext) — fsk nao pode DEGRADAR
    # o residual de conservacao alem de +1 ponto percentual sobre o baseline
    # graded (que ja carrega ~2.9% neste setup sintetico; medido 2026-08-19).
    a = _run(JointMaterial(**GRADED), n=300)
    b = _run(JointMaterial(**GRADED, free_spin_kin=0.72), n=300)
    razao_a = abs(a.energy.conservation_residual) / max(abs(a.energy.W_ext), 1.0)
    razao_b = abs(b.energy.conservation_residual) / max(abs(b.energy.W_ext), 1.0)
    assert razao_b < razao_a + 0.01


def test_loose_F_exp_default_off_e_desacelera():
    # P-13 (2026-08-20): fe=0 = OFF bit-identico; fe>0 DESACELERA o decay
    # (a taxa cai com F/F0 — o meio-termo entre runaway e arresto).
    a = _run(JointMaterial(**GRADED), n=300)
    b = _run(JointMaterial(**GRADED, loose_F_exp=0.0), n=300)
    assert [s.F_0 for s in a.history] == [s.F_0 for s in b.history]
    c = _run(JointMaterial(**GRADED, loose_F_exp=1.5), n=300)
    rot_a = sum(s.dF_0_by_mech.get("rotational_loosening", 0.0)
                for s in a.history)
    rot_c = sum(s.dF_0_by_mech.get("rotational_loosening", 0.0)
                for s in c.history)
    assert rot_a < rot_c < 0.0
