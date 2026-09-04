# -*- coding: utf-8 -*-
"""Contrato do `emb_pressure_exp` — encaixe DIRIGIDO POR PRESSÃO.

O engine já tinha `emb_conform_exp`, que modela **pré-conformação**: apertar
forte gasta aspereza no torque, então sobra menos resíduo cíclico (S cai quando
a pressão SOBE). Este campo é o ramo **complementar e de sinal contrário**: o
achatamento plástico *precisa* de pressão, então abaixo de uma referência o
reservatório de encaixe é mais raso (S cai quando a pressão CAI).

Motivação medida (`New_Theory/lu2024_T10Nm_embedding_sem_pressao_resultado.md`):
sem esta lei o encaixe é uma profundidade quase **absoluta**, e a mesma
profundidade vira fração muito maior de uma pré-carga pequena — no `LU_2024` o
excesso de perda no 1º ciclo vai com **1/F₀ a r = +0,995** sobre uma varredura
de 7×.

Prereg: `docs/superpowers/specs/2026-08-16-lu2024-embedding-dirigido-por-
pressao-prereg.md`. Estes testes fixam o contrato **e impedem que o default
deixe de ser inerte em silêncio**.
"""
import numpy as np
import pytest

import bolt_analysis_studio.numerical.dynamic_stiffness_analyzer as dsa


P_REF = 1.5e8
A = 5.0e-5                      # m² — área de contato de um M8 típico


def _geom():
    return dsa.JointGeometry(A_contact=A)


def _estado(p):
    """Estado cuja pressão inicial é exatamente `p`."""
    F = p * A
    return dsa.SlowState(F_0=F, F_0_init=F)


def test_default_e_inerte_e_exato():
    """0.0 é o default e devolve 1.0 EXATO — não 'aproximadamente 1'.

    O early-return existe para isso: sem ele, `(p/p_ref)**0` daria 1.0 por
    aritmética de ponto flutuante e o G0 do prereg (bit-a-bit em 207 curvas)
    passaria a depender de detalhe de implementação de `pow`.
    """
    assert dsa.JointMaterial().emb_pressure_exp == 0.0
    mat = dsa.JointMaterial()
    for p in (0.1 * P_REF, P_REF, 10 * P_REF):
        assert dsa.embedding_pressure_factor(_estado(p), _geom(), mat) == 1.0


def test_acima_da_referencia_e_UM_exato():
    """p >= p_ref ⇒ 1.0 exato. É o `min(1, ·)`, e ele é load-bearing.

    É esta cláusula que dá ISOLAMENTO ESTRUTURAL: ao ligar a lei numa fonte que
    varre pressão, as juntas mais apertadas ficam bit-idênticas sem depender de
    tolerância. No `LU_2024` são 5 das 7 curvas, incluindo as 3 que passam o
    tripé e não podem piorar.
    """
    mat = dsa.JointMaterial(emb_pressure_exp=1.6)
    for p in (P_REF, 1.07 * P_REF, 1.48 * P_REF, 10 * P_REF):
        assert dsa.embedding_pressure_factor(_estado(p), _geom(), mat) == 1.0


def test_abaixo_da_referencia_segue_a_lei_de_potencia():
    """p < p_ref ⇒ (p/p_ref)^n, sem piso: é a lei, não um clamp."""
    for n in (0.5, 1.6, 3.0):
        mat = dsa.JointMaterial(emb_pressure_exp=n)
        for razao in (0.27, 0.5, 0.76, 0.99):
            got = dsa.embedding_pressure_factor(_estado(razao * P_REF),
                                                _geom(), mat)
            assert got == pytest.approx(razao ** n, rel=1e-12)


def test_expoente_maior_corta_mais_fundo():
    """Monotonicidade no expoente — a direção do slider tem de ser previsível."""
    e = _estado(0.76 * P_REF)
    vals = [dsa.embedding_pressure_factor(
        e, _geom(), dsa.JointMaterial(emb_pressure_exp=n))
        for n in (0.5, 1.0, 1.6, 3.0)]
    assert vals == sorted(vals, reverse=True)


def test_e_o_ramo_OPOSTO_da_pre_conformacao():
    """Os dois fatores têm de andar em direções contrárias na MESMA pressão.

    Sem este teste, alguém poderia 'consertar' um sinal e transformar a lei
    nova numa cópia da antiga — que é exatamente a física que NÃO serve à curva
    que motivou o campo.
    """
    baixa, alta = _estado(0.5 * P_REF), _estado(2.0 * P_REF)
    g = _geom()
    conf = dsa.JointMaterial(emb_conform_exp=1.6)
    press = dsa.JointMaterial(emb_pressure_exp=1.6)
    # pré-conformação: inerte na pressão BAIXA, corta na ALTA
    assert dsa.embedding_conformance_factor(baixa, g, conf) == 1.0
    assert dsa.embedding_conformance_factor(alta, g, conf) < 1.0
    # dirigido por pressão: corta na BAIXA, inerte na ALTA
    assert dsa.embedding_pressure_factor(baixa, g, press) < 1.0
    assert dsa.embedding_pressure_factor(alta, g, press) == 1.0


def test_os_dois_compoem_por_multiplicacao():
    """Física distinta ⇒ fatores ortogonais. Um não pode anular o outro.

    Na mesma pressão os dois nunca mordem juntos (um deles está sempre no
    `min`), então compor é seguro — mas o produto tem de ser o que o alvo do
    encaixe usa, e é isso que se fixa aqui.
    """
    g = _geom()
    mat = dsa.JointMaterial(emb_conform_exp=1.6, emb_pressure_exp=1.6)
    for razao in (0.4, 1.0, 2.5):
        e = _estado(razao * P_REF)
        prod = (dsa.embedding_conformance_factor(e, g, mat)
                * dsa.embedding_pressure_factor(e, g, mat))
        esperado = (min(1.0, (1 / razao) ** 1.6) * min(1.0, razao ** 1.6))
        assert prod == pytest.approx(esperado, rel=1e-12)


def test_chaveado_em_F0_init_e_nao_no_F0_corrente():
    """Sem realimentação: o encaixe não pode reagir ao próprio decaimento.

    Se lesse `F_0`, a assíntota encolheria à medida que a junta perde pré-carga
    e a forma fechada de Norton deixaria de valer — a mesma armadilha que a
    docstring do fator de pré-conformação já registra.
    """
    mat = dsa.JointMaterial(emb_pressure_exp=1.6)
    F_init = 0.76 * P_REF * A
    cheio = dsa.SlowState(F_0=F_init, F_0_init=F_init)
    caido = dsa.SlowState(F_0=0.2 * F_init, F_0_init=F_init)   # perdeu 80 %
    assert (dsa.embedding_pressure_factor(cheio, _geom(), mat)
            == dsa.embedding_pressure_factor(caido, _geom(), mat))


def test_referencia_invalida_e_inerte():
    """p_ref <= 0 não pode virar divisão por zero nem NaN silencioso."""
    mat = dsa.JointMaterial(emb_pressure_exp=1.6, p_ref_emb=0.0)
    assert dsa.embedding_pressure_factor(_estado(1e7), _geom(), mat) == 1.0


def test_junta_sem_pre_carga_e_inerte():
    """F_0_init = 0 ⇒ 1.0 (e não 0.0), senão o encaixe some por acidente."""
    mat = dsa.JointMaterial(emb_pressure_exp=1.6)
    assert dsa.embedding_pressure_factor(
        dsa.SlowState(F_0=0.0, F_0_init=0.0), _geom(), mat) == 1.0


# ------------------------------------------------------------------ G0 do prereg

_GEOM_RUN = dsa.JointGeometry(A_s=157e-6, L_eff=0.05, d_2=14.7e-3,
                              pitch=2.0e-3, r_bearing=11e-3, A_contact=200e-6)


def _historia(mat, n=300):
    ana = dsa.DynamicStiffnessAnalyzer(_GEOM_RUN, mat, 60000.0)
    return np.array([ana.step_cycle(F_amp=0.0, theta_load=np.pi / 2, freq=10.0,
                                    delta_amp=5e-4).F_0 for _ in range(n)])


def test_g0_default_off_e_bit_identico_na_trajetoria():
    """G0 do prereg em nível de unidade: a trajetória inteira, bit-a-bit.

    O fator entra MULTIPLICANDO no meio de uma cadeia de produtos. Como ele
    devolve `1.0` exato quando desligado e `x * 1.0 == x` bit-a-bit em IEEE754
    (inclusive preservando o agrupamento à esquerda), a inércia é demonstrável
    — mas o G0 exige medida, não argumento, e é barato tê-la aqui em vez de
    depender de uma re-simulação de 207 curvas que leva meia hora.
    """
    a = _historia(dsa.JointMaterial())
    b = _historia(dsa.JointMaterial(emb_pressure_exp=0.0))
    assert np.array_equal(a, b)


def test_ligado_a_trajetoria_muda_so_abaixo_da_referencia():
    """E o espelho do G0: ligado, ele TEM de agir — e só onde deve.

    Sem este teste, um `return 1.0` mal colocado passaria no G0 e a capacidade
    seria um no-op silencioso — o modo de falha que esta campanha já registrou
    com `flank_wear_on` e com o Cattaneo-Mindlin.
    """
    p_junta = 60000.0 / 200e-6                          # 3,0e8 Pa
    abaixo = dsa.JointMaterial(emb_pressure_exp=2.0, p_ref_emb=2 * p_junta)
    acima = dsa.JointMaterial(emb_pressure_exp=2.0, p_ref_emb=0.5 * p_junta)
    base = _historia(dsa.JointMaterial())
    assert not np.array_equal(_historia(abaixo), base)   # p < p_ref: age
    assert np.array_equal(_historia(acima), base)        # p > p_ref: inerte
