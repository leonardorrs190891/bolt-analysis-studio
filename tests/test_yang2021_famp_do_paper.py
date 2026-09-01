# -*- coding: utf-8 -*-
"""O F_amp do YANG_2021 vem da Tabela 1 do paper — e não pode regredir calado.

## O defeito que isto fixa (prereg 2026-08-19-yang2021-famp-proveniencia)

As 8 curvas rodavam com `F_amp_N = 0,4·F₀ = 5640` e proveniência
*"literature (Pai&Hess 2002)"* — enquanto a Tabela 1 do paper (transcrita na
nota de aparato, e presente no próprio `validation_cases.py` como `axkn` que só
ia para a *string* da nota) publica a carga axial POR ENSAIO. O input do paper
existia no repositório em dois lugares e nunca chegava ao engine.

## Por que a correção é DOCUMENTAL (e este teste também fixa isso)

Medido com instrumento validado (gancho em `settling_amplitude_factor`
confirmando o valor recebido): o F_amp é **estruturalmente inerte** em fonte
transversal-pura — θ=90° ⇒ `F_ax = |F_amp·cos θ| = 0` ⇒ guard 1,0. O G2 do
prereg re-simulou as 8 com os valores do paper e deu **bit-a-bit** contra o
store. Se um dia o F_amp deixar de ser inerte aqui (excitação composta
implementada, θ passar a carregar a fase axial), `test_inercia_do_famp_na_fonte`
falha — e isso é DESEJADO: significa que os valores do paper passaram a agir, e
as métricas da fonte têm de ser re-baselinadas conscientemente.
"""
from __future__ import annotations

import pytest

from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.inputs import inputs_for

# Tabela 1 do paper (Yang 2021, Shock and Vibration 1441122) — kN → N.
TABELA_1 = {
    "yang2021_amp1p0mm_ax2kN": 2000.0,
    "yang2021_amp0p8mm_ax6kN": 6000.0,
    "yang2021_amp0p5mm_ax8kN": 8000.0,
    "yang2021_amp0p6mm_ax8kN_r1": 8000.0,
    "yang2021_amp0p6mm_ax8kN_r2": 8000.0,
    "yang2021_amp0p6mm_ax8kN_r3": 8000.0,
    "yang2021_amp0p7mm_ax11p2kN": 11200.0,
}


def _casos():
    return {r.case_id: r for r in all_records() if r.source == "YANG_2021"}


def test_famp_vem_do_paper_com_proveniencia():
    """Valor E proveniência, por curva — o rótulo errado era metade do defeito."""
    casos = _casos()
    for cid, esperado in TABELA_1.items():
        fa = inputs_for(casos[cid].validation_case)["F_amp_N"]
        assert fa["value"] == esperado, f"{cid}: F_amp {fa['value']} != {esperado}"
        assert "paper" in fa["prov"], (
            f"{cid}: proveniência voltou a {fa['prov']!r} — o paper PUBLICA o valor")


def test_fig2_fica_no_fallback_honesto():
    """A `fig2_typical` não tem condição fixada na nota — inventar valor seria
    o defeito espelhado. Ela fica no fallback com a proveniência de literatura."""
    casos = _casos()
    fa = inputs_for(casos["yang2021_fig2_typical"].validation_case)["F_amp_N"]
    assert fa["prov"].startswith("literature"), fa
    assert fa["value"] == pytest.approx(0.4 * 14100)


def test_inercia_do_famp_na_fonte():
    """O F_amp é estruturalmente inerte aqui (θ=90° ⇒ cos=0 ⇒ guard 1,0).

    Fixado por UMA simulação barata: dobrar o F_amp da curva mais sensível não
    move nenhuma métrica. Se este teste falhar, a excitação axial passou a agir
    — re-baselinar a fonte conscientemente (as métricas do store foram medidas
    sob inércia).
    """
    import bolt_analysis_studio.validation.runner as rn
    import bolt_analysis_studio.validation.inputs as vi
    casos = _casos()
    rec = casos["yang2021_amp1p0mm_ax2kN"]
    base = rn.simulate_case(rec)
    _i = vi.inputs_for
    def dobrado(case):
        d = _i(case)
        d = dict(d)
        d["F_amp_N"] = dict(value=2 * d["F_amp_N"]["value"], prov="teste")
        return d
    vi.inputs_for = dobrado
    try:
        dob = rn.simulate_case(rec)
    finally:
        vi.inputs_for = _i
    assert dob.mae == base.mae and dob.maxerr == base.maxerr, (
        "o F_amp DEIXOU de ser inerte no YANG_2021 — a excitação axial passou a "
        "agir; re-baseline a fonte antes de confiar nas métricas do store")
