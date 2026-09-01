# -*- coding: utf-8 -*-
"""Regressão do bug de RESOLUÇÃO DE CHAVE adotada (YANG_2019 varamp, 2026-07-27).

Bug consertado: `YANG_2019_small_to_large` e `YANG_2019_large_to_small`
EMPATAVAM em score no `_adopted_for` — os tokens de grupo casam por SUBSTRING
do case_id, e as duas permutações de {small, to, large} casam nos DOIS
case_ids, dando o mesmo `pref` e o mesmo `len(extra)`. Como
`kb.adopted_sources()` é `sorted()` e o teste do runner é `>` estrito, o
`large_to_small` vencia AMBOS os casos e o `small_to_large` ficava
INALCANÇÁVEL: o caso small→large era simulado com o espectro da outra
direção (51,4% dos ciclos em 0,8 mm em vez de 97,8% em 0,6 mm).

Conserto: um único grupo `YANG_2019_varamp` com os espectros em `per_case`,
cujos tokens casam por substring PURA (sem split em "_") — mesmo idioma do
`_grease_standard` vs `nogrease_standard` do SUN_2025_CRIMP.

O segundo teste é o INVARIANTE GERAL da classe do bug (CLAUDE.md: "NUNCA
criar chave que EMPATA em score"): nenhum caso do registry pode ter duas
chaves adotadas empatadas no score máximo. Ele replica a aritmética de
`_adopted_for` de propósito (teste registry-truth: se a fórmula do runner
mudar, este teste tem de ser atualizado junto).
"""
import pytest

from bolt_analysis_studio.calibration import knowledge_base as kb
from bolt_analysis_studio.validation.case_registry import all_records, record
from bolt_analysis_studio.validation.inputs import frozen_constants
from bolt_analysis_studio.validation.runner import (_adopted_for,
                                                    _adopted_overrides)

# Inputs-de-paper (Yang 2019, Tabelas 6/7 + Figs. 10/11): blocos [n, delta_m].
ESPECTRO = {
    "yang2019_M10_varamp_small_to_large": [[3730, 0.0006], [85, 0.0008]],
    "yang2019_M10_varamp_large_to_small": [[1546, 0.0008], [1464, 0.0006]],
}
SEM_ESPECTRO = ["yang2019_M10_amp0p4_5Hz", "yang2019_M10_amp0p6_5Hz",
                "yang2019_M10_amp0p6_10Hz"]


def _bolt(rec):
    return getattr(rec.validation_case, "bolt_size", "") or ""


def _overrides(rec):
    consts, _ = frozen_constants()
    return _adopted_overrides(rec.source, consts, rec.case_id, bolt=_bolt(rec))


def _candidatos(source, case_id, bolt):
    """Réplica exata da pontuação de `_adopted_for` (runner.py) — devolve
    [(score, chave), ...] das chaves elegíveis. None = curto-circuito HDPE."""
    cid = (case_id + "|" + bolt).lower() if bolt else case_id.lower()
    if "hpde" in cid or "hdpe" in cid:
        return None
    out, srcl = [], source.lower()
    for s in kb.adopted_sources():
        sl = s.lower()
        if srcl.startswith(sl):
            extra, pref = [], len(sl)
        elif sl.startswith(srcl):
            extra, pref = [t for t in sl[len(srcl):].split("_") if t], len(srcl)
        else:
            continue
        if any(t not in cid for t in extra):
            continue
        out.append((pref * 10 + len(extra), s))
    return out


@pytest.mark.parametrize("cid", sorted(ESPECTRO))
def test_cada_varamp_recebe_o_proprio_espectro(cid):
    rec = record(cid)
    if rec is None:
        pytest.skip("caso %s não registrado neste ambiente" % cid)
    assert _adopted_for(rec.source, rec.case_id, _bolt(rec)) == "YANG_2019_varamp"
    spec = _overrides(rec).get("delta_spectrum")
    assert spec is not None, "o espectro per_case não chegou aos overrides"
    assert [[int(n), float(d)] for n, d in spec] == ESPECTRO[cid]


def test_os_dois_varamp_nao_compartilham_espectro():
    recs = [record(c) for c in ESPECTRO]
    if any(r is None for r in recs):
        pytest.skip("casos varamp não registrados neste ambiente")
    a, b = (_overrides(r).get("delta_spectrum") for r in recs)
    assert a != b, "regressão do bug: as duas direções voltaram ao mesmo espectro"


@pytest.mark.parametrize("cid", SEM_ESPECTRO)
def test_yang2019_amplitude_constante_fica_sem_espectro(cid):
    rec = record(cid)
    if rec is None:
        pytest.skip("caso %s não registrado neste ambiente" % cid)
    assert _adopted_for(rec.source, rec.case_id, _bolt(rec)) == "YANG_2019"
    assert _overrides(rec).get("delta_spectrum") is None


def test_nenhum_empate_de_score_entre_chaves_adotadas():
    """Invariante da classe do bug: no máximo UMA chave no score máximo.
    Empate => quem vence é a ordem alfabética de `adopted_sources()`, e o
    grupo perdedor vira config silenciosamente morta.

    NÃO se testa aqui "toda chave é alcançável": chave-base SOMBREADA por
    chaves mais específicas é padrão legítimo do arquivo (hoje
    BAUER_2024_fig6, LI_2022_MARSTRUC e LIU_2022 nunca vencem porque as
    variantes por figura/protocolo sempre pontuam mais). O que não pode
    existir é chave morta por EMPATE, que é o bug consertado aqui."""
    empates = []
    for rec in all_records():
        cands = _candidatos(rec.source, rec.case_id, _bolt(rec))
        if not cands:                      # None (HDPE) ou nenhuma candidata
            continue
        top = max(s for s, _ in cands)
        no_topo = sorted(k for s, k in cands if s == top)
        if len(no_topo) > 1:
            empates.append("%s -> %s" % (rec.case_id, " == ".join(no_topo)))
    assert not empates, "empate de score (resolução por ordem alfabética):\n" \
                        + "\n".join(empates)
