# -*- coding: utf-8 -*-
"""O split held-out mecânico (calibration/holdout.py).

O que estes testes prendem: as regras que carregaram a honestidade dos preregs
do YANG (2026-07-30) e que, à mão, dependiam de disciplina — held-out vazio é
erro, o critério tem nome, o objeto é imutável, e o veredito de generalização
julga SÓ o held-out. O caso de calibração dos números é o próprio trio: reads
{0.25,0.30,0.35,0.45}, held {0.50,0.55,0.65}, 2 de 3 pioraram ⇒ não generaliza.
"""
import pytest

from bolt_analysis_studio.calibration.holdout import (HoldoutSplit,
                                                      split_por_criterio,
                                                      veredicto_generalizacao)


def test_split_grava_o_criterio_e_particiona_completo():
    s = split_por_criterio([1, 2, 3, 4], lambda x: x % 2 == 0,
                           "joelho: 1o ponto <0,95 ainda >=0,85")
    assert s.criterio.startswith("joelho")
    assert set(s.reads) | set(s.held) == {1, 2, 3, 4}
    assert set(s.reads) & set(s.held) == set()


def test_held_vazio_e_ERRO_nao_aviso():
    """A regra central: sem generalização, fit 'que funcionou' é sobreajuste
    não testado. O trio só matou o W único porque as 3 mal-amostradas viraram
    held-out em vez de leitura."""
    with pytest.raises(ValueError, match="held-out VAZIO"):
        split_por_criterio([1, 2], lambda x: True, "resolve tudo")


def test_leitura_vazia_e_erro():
    with pytest.raises(ValueError, match="LEITURA vazio"):
        split_por_criterio([1, 2], lambda x: False, "estrito demais")


def test_criterio_anonimo_e_erro():
    with pytest.raises(ValueError, match="NOMEADO"):
        split_por_criterio([1, 2], lambda x: x == 1, "  ")


def test_split_e_imutavel():
    s = split_por_criterio([1, 2], lambda x: x == 1, "c")
    with pytest.raises(Exception):
        s.reads = (2,)                     # frozen dataclass


def test_veredicto_do_trio_reproduzido():
    """Os números reais da execução do trio: das held-out, 0,50 e 0,65 pioram
    e 0,55 melhora ⇒ 2 de 3 pioram, generaliza=False (foi o F5)."""
    s = HoldoutSplit(criterio="joelho resolvido (trio)",
                     reads=(0.25, 0.30, 0.35, 0.45),
                     held=(0.50, 0.55, 0.65))
    antes = {0.50: 0.3913, 0.55: 0.3243, 0.65: 0.0906}
    depois = {0.50: 0.5811, 0.55: 0.1867, 0.65: 0.3131}
    v = veredicto_generalizacao(antes, depois, s)
    assert v["pioras_held"] == (0.50, 0.65)
    assert v["generaliza"] is False


def test_veredicto_exige_metrica_de_todo_held():
    s = HoldoutSplit(criterio="c", reads=(1,), held=(2, 3))
    with pytest.raises(KeyError):
        veredicto_generalizacao({2: 0.1}, {2: 0.1, 3: 0.1}, s)


def test_piora_dentro_da_tolerancia_nao_conta():
    """A tolerância é a MESMA dos gates (+0,01): ruído numérico não reprova."""
    s = HoldoutSplit(criterio="c", reads=(1,), held=(2, 3))
    antes = {2: 0.100, 3: 0.200}
    depois = {2: 0.108, 3: 0.195}          # +0,008 <= tol
    v = veredicto_generalizacao(antes, depois, s)
    assert v["pioras_held"] == ()
    assert v["generaliza"] is True
