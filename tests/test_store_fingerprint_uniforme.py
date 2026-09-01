# -*- coding: utf-8 -*-
"""O STORE tem de estar carimbado por INTEIRO com o fingerprint ATUAL.

Motivado por um incidente medido em 2026-08-10: o store estava PARCIALMENTE
carimbado — 209 registros num fingerprint antigo e 1 (o sintetico) noutro —
porque uma sessao adotou, sincronizou os DOCUMENTOS e nao concluiu o re-stamp.
Consequencia: um gate de censo congelado num prereg saiu NAO-AVALIAVEL, porque a
linha de base mudou sem que nada denunciasse.

O CLAUDE.md ja registra por que o hash sozinho nao basta: `engine_fingerprint()`
hasheia o bloco `shared` + configs adotadas, NAO o codigo nem os inputs — "um
store escrito por sessao interrompida so se valida RE-SIMULANDO; o hash nao
denuncia divergencia de input".

Este teste cobre a metade que E' detectavel: divergencia DENTRO do store, e entre
o store e a config vigente. Nao cobre (nem promete) divergencia de INPUT/CSV, que
exige re-simular.

## Quando falhar

    py -3.12 New_Theory/parallel_batch.py --workers 6 --store

mais a re-simulacao direta do `exemplo_m12_sintetico`, que fica FORA do batch.
Falhar aqui NAO e' bug do teste: e' o store desatualizado em relacao a config que
o proprio repositorio carrega. Rode o batch antes de publicar qualquer numero.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
STORE = RAIZ / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"


@pytest.fixture(scope="module")
def store():
    if not STORE.exists():
        pytest.skip("store canonico ausente (clone sem os dados)")
    return json.loads(STORE.read_text(encoding="utf-8"))


def _fps(st: dict) -> Counter:
    return Counter(v.get("engine_fingerprint") for v in st.values())


def test_store_carimbado_por_inteiro(store):
    """UNIFORMIDADE — um unico fingerprint em todos os registros.

    Foi exatamente isto que faltou em 2026-08-10 (209 + 1)."""
    c = _fps(store)
    assert len(c) == 1, (
        "store PARCIALMENTE carimbado: %d fingerprints distintos %s "
        "— uma adocao mexeu na config e o re-stamp nao terminou. Rode "
        "`parallel_batch.py --workers 6 --store` e re-simule o "
        "`exemplo_m12_sintetico`, que fica FORA do batch." % (len(c), dict(c)))


def test_store_reflete_a_config_vigente(store):
    """ATUALIDADE — o carimbo do store == fingerprint da config commitada.

    Pega o caso em que alguem adota, sincroniza documentos e NAO re-carimba: o
    store segue internamente uniforme, mas descreve uma config que ja nao e' a do
    repositorio. Foi assim que o censo publicado ficou 3 curvas atras da config."""
    sys.path.insert(0, str(RAIZ / "src"))
    from bolt_analysis_studio.validation.runner import engine_fingerprint
    atual = engine_fingerprint()
    c = _fps(store)
    no_store = max(c, key=lambda k: c[k])
    assert no_store == atual, (
        "store carimbado com `%s` mas a config vigente da `%s` — alguem adotou e "
        "nao re-carimbou, entao os numeros publicados descrevem uma config que "
        "nao e' mais a do repositorio. Rode o batch." % (no_store, atual))
