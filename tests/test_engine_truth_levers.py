# -*- coding: utf-8 -*-
"""VERDADES-DE-ENGINE das alavancas que a calibração vai tocar.

Por que este arquivo existe: na sequência YANG_2023_IJPEM (2026-07-29/30),
TRÊS preregs reprovaram pelo MESMO erro de classe — assumir a forma de uma
quantidade sem ler a definição dela no engine:

  · v1 do `delta_free`: tratei o onset de slip como ESTÁTICO; o termo elástico
    `F_slip/k_tr = µ·F₀/k_tr` DECAI com F₀, então o onset desce ao longo do
    ensaio e a borda da janela admissível é instável.
  · F4 do par: tratei `loose_arrest_floor` como CLAMP GLOBAL do ratio; o
    `self_locking_gate` multiplica `d_theta` e arresta SÓ o canal rotacional —
    wear/creep/embedding seguem drenando e o ratio total passa abaixo do piso.
  · Beco 2 (D1b): tratei a FRAÇÃO do canal como cota de inércia de uma alavanca
    de LEI DE TAXA; fração a posteriori de uma parametrização não limita o que
    outra lei faz — mudar a lei é o que muda a fração.

O padrão dos registry-truth tests (parameter_registry) é o certo: prender o
predicado à física do engine para a leitura não envelhecer. Aqui, o mesmo para
as alavancas de calibração. Cada teste nomeia o prereg que teria salvado.
"""
import math

import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, F_slip_transverse, JointGeometry, JointMaterial,
    SlowState, k_tr_transverse, loosening_slip_gate, resolve_transverse_slip,
    self_locking_gate,
)


def _geom():
    d, p = 16e-3, 2e-3
    d2 = d - 0.6495 * p
    d1 = d - 1.0825 * p
    A_s = math.pi / 4 * ((d2 + d1) / 2) ** 2
    return JointGeometry(A_s=A_s, L_eff=0.05, d_2=d2, pitch=p,
                         r_bearing=0.75 * d, A_contact=1e-4)


def _run(n, F0=50000.0, delta_mm=0.5, **mat_kw):
    mat = JointMaterial(**mat_kw)
    ana = DynamicStiffnessAnalyzer(_geom(), mat, F0)
    for _ in range(n):
        ana.step_cycle(12000.0, math.pi / 2, 0.5, delta_amp=delta_mm * 1e-3)
    return ana


def _cum_rot(ana) -> float:
    return float(sum(abs(s.dF_0_by_mech.get("rotational_loosening", 0.0))
                     for s in ana.history))


# ---------------------------------------------------------------- fato 1
def test_onset_de_slip_decai_com_F0():
    """O onset cinemático `delta_free + F_slip/k_tr` é FUNÇÃO DO ESTADO, não
    constante: `F_slip = µ·F₀` cai quando F₀ cai. Consequência operacional (a
    que o prereg v1 do delta_free ignorou e reprovou por isso): sub-criticidade
    é condição PARA TODO t, governada pelo elástico MÍNIMO — uma amplitude em
    stick no ciclo 1 pode destravar depois. Nunca derivar janela de onset de um
    instantâneo."""
    geom, mat = _geom(), JointMaterial(delta_free=100e-6)
    alto = SlowState(F_0=50000.0)
    baixo = SlowState(F_0=30000.0)
    on_alto = mat.delta_free + F_slip_transverse(alto, mat) / k_tr_transverse(geom, mat)
    on_baixo = mat.delta_free + F_slip_transverse(baixo, mat) / k_tr_transverse(geom, mat)
    assert on_baixo < on_alto, "o onset tem de DESCER quando F_0 cai"
    # e a consequência: um delta entre os dois onsets fica em stick com F_0
    # alto e escorrega com F_0 baixo — o 'destrava depois' medido no v1
    delta = 0.5 * (on_alto + on_baixo)
    assert resolve_transverse_slip(alto, mat, 12000.0, math.pi / 2,
                                   delta_amp=delta, geom=geom) == 0.0
    assert resolve_transverse_slip(baixo, mat, 12000.0, math.pi / 2,
                                   delta_amp=delta, geom=geom) > 0.0


# ---------------------------------------------------------------- fato 2
def test_arresto_e_por_canal_nao_clamp_global():
    """`self_locking_gate` = max(0, 1 − F_min/F₀)^exp MULTIPLICA d_theta: o piso
    faz promessa sobre o canal ROTACIONAL, não sobre o ratio. Com wear ativo o
    ratio final PODE terminar abaixo do piso — é comportamento documentado, e
    foi o que o F4 do prereg do par especificou errado (falsificou 5 de 6 por
    engano de leitura, não por defeito do modelo)."""
    mat = JointMaterial(loose_arrest_floor=0.5)
    # a função em si: soft gate, com os dois extremos exatos
    assert self_locking_gate(SlowState(F_0=50000.0, F_0_init=50000.0),
                             JointMaterial(loose_arrest_floor=0.0)) == 1.0
    g_meio = self_locking_gate(SlowState(F_0=40000.0, F_0_init=50000.0), mat)
    assert 0.0 < g_meio < 1.0
    assert self_locking_gate(SlowState(F_0=25000.0, F_0_init=50000.0),
                             mat) == pytest.approx(0.0, abs=1e-12)
    # a consequência integrada: wear forte + piso alto => ratio termina ABAIXO
    # do piso (os outros canais seguem drenando), MAS o canal rotacional
    # respeita o teto F0*(1-piso)
    ana = _run(400, loose_arrest_floor=0.5, K_archard=3e-4)
    ratio_fim = max(ana.state.F_0, 0.0) / 50000.0
    assert ratio_fim < 0.5, (
        "com wear ativo o ratio TEM de poder passar abaixo do piso — se isto "
        "falhar, o gate virou clamp global e TODO consumidor precisa re-ler")
    assert _cum_rot(ana) <= 50000.0 * (1 - 0.5) * 1.01


# ---------------------------------------------------------------- fato 3
def test_gate_de_gross_slip_e_zero_em_stick():
    """`loosening_slip_gate` = slip/(slip+delta_t): vale EXATAMENTE 0 em stick.
    Corolário de diagnóstico (usado no v2): se o canal rotacional cresceu, o
    slip NÃO era zero — procurar onde o onset destravou, não desconfiar do
    gate. E None/'off' => 1.0 (force-mode/backward-compat)."""
    geom = _geom()
    st = SlowState(F_0=50000.0)
    cm = JointMaterial(slip_regime_mode="cattaneo_mindlin")
    assert loosening_slip_gate(st, geom, cm, 0.0) == pytest.approx(0.0)
    assert loosening_slip_gate(st, geom, cm, None) == 1.0
    gf = JointMaterial(loosening_slip_coupling="gross_fraction")
    assert loosening_slip_gate(st, geom, gf, 0.0) == pytest.approx(0.0)
    assert loosening_slip_gate(st, geom, JointMaterial(), 1e-4) == 1.0


# ---------------------------------------------------------------- fato 4
def test_lei_de_taxa_nova_muda_a_fracao_do_canal():
    """A fração de um canal na decomposição é atribuição A POSTERIORI de UMA
    parametrização — não é cota do que outra LEI DE TAXA pode fazer (Beco 2 da
    D1b: 'graded_scrit inerte em 18 das 53' era falso). Aqui: ligar o modo
    graduado multiplica o canal rotacional a partir do mesmo estado; e os dois
    desligamentos documentados (mode default, k=0) são BIT-idênticos."""
    base = _run(150)
    des1 = _run(150, loose_rate_mode="graded_scrit", s_crit_loose=50e-6,
                k_loose_graded=0.0)                     # k=0 => branch nunca roda
    assert _cum_rot(des1) == _cum_rot(base)
    assert des1.state.F_0 == base.state.F_0             # bit-identico
    lig = _run(150, loose_rate_mode="graded_scrit", s_crit_loose=50e-6,
               k_loose_graded=1.0)
    assert _cum_rot(lig) > _cum_rot(base) * 1.5, (
        "a lei graduada tem de poder CRESCER o canal — se isto falhar, "
        "verificar se o branch está sendo gateado por modo")


# ---------------------------------------------------------------- fato 5
def test_incubacao_nao_congela_o_relogio_de_trabalho():
    """`W_slip_acc` acumula o trabalho de slip CRU (tuner-independente) mesmo com
    o gate de incubação ~fechado — senão o onset nunca chegaria (deadlock). Foi
    o relógio usado para ler o joelho no trio; se ele passasse a ser gateado, a
    leitura de `slip_onset_W` mudaria de significado em silêncio."""
    ana = _run(50, slip_onset_W=1e9)      # limiar altíssimo: gate ~0 o tempo todo
    assert ana.state.W_slip_acc > 0.0
