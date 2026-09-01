# -*- coding: utf-8 -*-
"""Contrato do `loose_arrest_residual` — taxa residual sub-arresto.

A capacidade fica no engine DEFAULT-INERTE (padrão do `gth`): o prereg
`2026-08-15-lei-de-taxa-rotacional` **não passou** os gates de adoção (G2/G3:
fechar as 3 alvo do ICMEZ custa 2 protegidas), mas o MECANISMO foi validado —
a taxa tardia do modelo sobe de 0,20 para 0,47 da taxa de meio, dentro da banda
do dado (0,48–0,57). Estes testes fixam o contrato para quando a campanha
retomá-la (e impedem que o default deixe de ser inerte em silêncio).
"""
import pytest

import bolt_analysis_studio.numerical.dynamic_stiffness_analyzer as dsa


def _estado(f0, f0i=100000.0):
    return dsa.SlowState(F_0=f0, F_0_init=f0i)


def test_default_e_bit_identico():
    """residual=0 (default) tem de devolver EXATAMENTE a expressão anterior.

    Não basta "quase": o G0 do prereg exige zero diferença, e o early-return
    explícito é o que garante isso sem depender de `max(0.0, x) == x`."""
    st = _estado(30000.0)
    mat = dsa.JointMaterial(loose_arrest_floor=0.308)
    assert dsa.JointMaterial().loose_arrest_residual == 0.0
    # F_0 = 0,30·F_0_init < piso 0,308 ⇒ o gate antigo MORRE
    assert dsa.self_locking_gate(st, mat) == 0.0


def test_residual_poe_piso_na_taxa():
    """Abaixo do limiar o canal retém `residual · g0`, com g0 = 1 − floor.

    Forma fechada (sem estado): é isso que torna o campo uma constante e não
    um acumulador — e é o que o dado do ICMEZ pede (o joelho continua a cair)."""
    st = _estado(30000.0)
    for r in (0.1, 0.3, 0.6):
        mat = dsa.JointMaterial(loose_arrest_floor=0.308, loose_arrest_residual=r)
        assert dsa.self_locking_gate(st, mat) == pytest.approx(r * (1 - 0.308),
                                                              rel=1e-12)


def test_longe_do_piso_o_residual_nao_morde():
    """O residual é PISO, não offset: onde o gate normal já é maior, nada muda.

    Sem isto o campo viraria um multiplicador global e mexeria no início da
    curva — exatamente o que o diagnóstico diz que NÃO está errado."""
    st = _estado(90000.0)                      # bem acima do piso
    a = dsa.self_locking_gate(st, dsa.JointMaterial(loose_arrest_floor=0.308))
    b = dsa.self_locking_gate(st, dsa.JointMaterial(loose_arrest_floor=0.308,
                                                    loose_arrest_residual=0.3))
    assert a == b


def test_compoe_com_o_expoente_de_aproximacao():
    """`arrest_approach_exp` molda a aproximação; o residual põe o piso DEPOIS.

    A ordem importa: expoente primeiro (mata a taxa perto do piso), residual
    por último (garante o mínimo). Invertida, o expoente comeria o piso."""
    st = _estado(35000.0)
    base = dsa.JointMaterial(loose_arrest_floor=0.308, arrest_approach_exp=2.0)
    g_exp = dsa.self_locking_gate(st, base)
    comb = dsa.JointMaterial(loose_arrest_floor=0.308, arrest_approach_exp=2.0,
                             loose_arrest_residual=0.3)
    assert dsa.self_locking_gate(st, comb) == pytest.approx(
        max(0.3 * (1 - 0.308), g_exp), rel=1e-12)


def test_sem_piso_o_campo_e_inerte():
    """floor=0 ⇒ gate 1.0 exato, com ou sem residual (o canal não arresta)."""
    st = _estado(30000.0)
    for r in (0.0, 0.5):
        mat = dsa.JointMaterial(loose_arrest_floor=0.0, loose_arrest_residual=r)
        assert dsa.self_locking_gate(st, mat) == 1.0
