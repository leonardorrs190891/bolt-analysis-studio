# -*- coding: utf-8 -*-
"""Invariantes da RETIRADA de uma fonte do documento (decisão 2026-07-31).

`_SRC_RETIRADO` responde a uma pergunta diferente de `_SRC_NAO_COMPARAVEL`:

  · `_SRC_NAO_COMPARAVEL` — a fonte APARECE e fica fora do censo. É afirmação
    sobre a MÉTRICA (o `exemplo_m12_sintetico` é útil de ver, não é evidência).
  · `_SRC_RETIRADO` — a fonte NÃO aparece. É afirmação sobre o CORPUS: deixou
    de ser prova de validação.

O modo de falha que estes testes perseguem é o **vazamento**: a fonte sai da
tabela principal e sobrevive num painel que lê de OUTRA origem. Aconteceu de
verdade — o `_budget_section` lê do `error_budget.json`, não de `records`, e a
fonte continuou lá depois de retirada de todo o resto. O sintoma era o rótulo
sair cru em vez de passar pelo mapa `NICE`.

DESDE 2026-09-04 `_SRC_RETIRADO` está VAZIO: a única fonte que estava nele saiu
do projeto por inteiro, e um caso removido não vaza para lugar nenhum. O
arquivo fica, e pula sozinho, porque retirar uma fonte já foi decisão tomada
uma vez: no dia em que voltar a ser, a rede de vazamento tem de estar de pé —
escrevê-la de novo depois do vazamento é tarde.
"""
import re

import pytest

from bolt_analysis_studio.validation import report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.store import ValidationStore

pytestmark = pytest.mark.skipif(
    not rh._SRC_RETIRADO,
    reason="nenhuma fonte retirada; os invariantes de vazamento são vazios")


@pytest.fixture(scope="module")
def docs():
    store = ValidationStore()
    records = all_records()
    if not store.all_ids():
        pytest.skip("store vazio — rode `report --all` antes")
    results = {r.case_id: store.get(r.case_id) for r in records}
    return (rh.master_report_html(records, results),
            rh.all_plots_html(records, results), records)


def _ids_retirados(records):
    return [r.case_id for r in records if r.source in rh._SRC_RETIRADO]


def test_ha_fonte_retirada_para_testar(docs):
    """Guarda do próprio teste: sem fonte retirada ele não prova nada."""
    _m, _p, records = docs
    assert rh._SRC_RETIRADO, "nenhuma fonte retirada — os testes abaixo são vazios"
    assert _ids_retirados(records), (
        "`_SRC_RETIRADO` nomeia fontes que não existem no registry")


def test_nenhum_caso_retirado_aparece_no_mestre(docs):
    mestre, _p, records = docs
    vazou = [c for c in _ids_retirados(records) if c in mestre]
    assert not vazou, f"casos retirados ainda no documento mestre: {vazou}"


def test_nenhum_caso_retirado_aparece_na_galeria_de_graficos(docs):
    """`all_plots.html` é linkada do mestre; deixar a fonte só lá seria pior
    que não retirar — a contradição ficaria a um clique."""
    _m, plots, records = docs
    vazou = [c for c in _ids_retirados(records) if c in plots]
    assert not vazou, f"casos retirados ainda na galeria de gráficos: {vazou}"


def test_nenhuma_LINHA_de_fonte_retirada_em_tabela_alguma(docs):
    """Pega o vazamento por painel de OUTRA origem (o defeito real do budget).

    Procura a fonte como célula de tabela, que é como ela aparece quando um
    painel a lista por conta própria."""
    mestre, plots, _r = docs
    for doc, nome in ((mestre, "mestre"), (plots, "all_plots")):
        for src in rh._SRC_RETIRADO:
            assert f"<td>{src}</td>" not in doc, (
                f"{nome}: fonte retirada {src} ainda tem linha de tabela — "
                f"algum painel lê de outra origem que não `records`")


def test_retirada_e_declarada_no_rodape(docs):
    """Retirar em silêncio é apagar. O documento tem de dizer o que saiu."""
    mestre, _p, _r = docs
    assert "Fontes retiradas deste documento" in mestre
    for src in rh._SRC_RETIRADO:
        nice = rh.NICE.get(src, src)
        assert nice in mestre, f"a nota não nomeia a fonte retirada {src}"


def test_fonte_retirada_tambem_esta_fora_do_censo(docs):
    """Coerência entre os dois filtros.

    Uma fonte que não aparece não pode contar no censo — seria evidência
    invisível. O inverso é permitido (o `USER` aparece e não conta)."""
    _m, _p, records = docs
    incoerentes = [r.case_id for r in records
                   if r.source in rh._SRC_RETIRADO
                   and rh.caso_comparavel(r.source, r.case_id)]
    assert not incoerentes, (
        f"retiradas do documento mas ainda no censo: {incoerentes} — "
        f"acrescente a fonte a `_SRC_NAO_COMPARAVEL` também")


def test_explorador_descarta_fonte_retirada_e_CONTA_o_descarte():
    """O Explorador é outro gerador — o filtro tem de valer lá também.

    E o descarte precisa ser CONTADO, não silencioso: o próprio build carrega
    essa disciplina desde 2026-07-27, quando 73 curvas de 11 fontes sumiram da
    galeria por semanas sem ninguém notar. Uma fonte que desaparece sem
    contagem é indistinguível de um defeito de leitura — por isso a retirada
    entra como mais um balde de `drop`, e não como um `if` mudo."""
    import importlib.util
    import pathlib
    import sys as _sys

    if not rh._SRC_RETIRADO:
        pytest.skip("nenhuma fonte retirada")
    gen = (pathlib.Path(__file__).resolve().parents[1] / "New_Theory"
           / "build_variable_explorer.py")
    if not gen.exists():
        pytest.skip("build_variable_explorer.py ausente")
    spec = importlib.util.spec_from_file_location("build_variable_explorer", gen)
    mod = importlib.util.module_from_spec(spec)
    _sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)

    casos = mod._validation_cases()
    if not casos:
        pytest.skip("store/galeria indisponível neste checkout")
    vazadas = sorted({c["source"] for c in casos} & set(rh._SRC_RETIRADO))
    assert not vazadas, f"fonte retirada ainda na galeria do Explorador: {vazadas}"
    # e os estudos de caso saem junto, porque bebem do mesmo funil
    estudos = {s["source"] for s in mod._study_sources()}
    assert not (estudos & set(rh._SRC_RETIRADO)), (
        "fonte retirada ainda tem página de estudo de caso")


def test_write_reports_nao_gera_pagina_para_fonte_retirada(tmp_path):
    """O ESCRITOR tem de recusar a página e APAGAR a que existir.

    Só deixar de escrever não basta: o arquivo antigo continua no disco (e no
    git) servindo um report que nenhum documento linka. Foi o estado real em
    2026-08-01 — os 3 `reports/ancora_interna*.html` tinham sido REGERADOS naquele mesmo
    dia, então eram órfãos vivos, não resíduo velho.

    O `orfao` plantado é o coração do teste: prova a remoção, não só a omissão.
    ~15 s porque escreve os 200+ reports — é o preço de testar o escritor de
    verdade em vez de uma função extraída que ninguém chama."""
    from bolt_analysis_studio.validation.report_html import write_reports

    if not rh._SRC_RETIRADO:
        pytest.skip("nenhuma fonte retirada")
    records = all_records()
    alvos = [r.case_id for r in records if r.source in rh._SRC_RETIRADO]
    if not alvos:
        pytest.skip("nenhum caso de fonte retirada no registry")
    rep = tmp_path / "reports"
    rep.mkdir(parents=True)
    orfao = rep / f"{alvos[0]}.html"
    orfao.write_text("<html>orfao de antes da retirada</html>", encoding="utf-8")

    write_reports(out_dir=tmp_path)

    assert not orfao.exists(), (
        f"{orfao.name}: o escritor deixou de gerar mas NÃO apagou a página "
        f"antiga — o órfão sobrevive no disco e no git")
    sobraram = [c for c in alvos if (rep / f"{c}.html").exists()]
    assert not sobraram, f"páginas geradas para fonte retirada: {sobraram}"
    assert list(rep.glob("*.html")), "não gerou report nenhum — teste inócuo"


def test_totais_do_orcamento_batem_com_as_linhas_mostradas(docs):
    """O rodapé do orçamento não pode somar o que a tabela não mostra.

    Era o segundo defeito do vazamento: filtrar a LINHA e manter o total do
    JSON deixaria a coluna somando 182 com 179 visíveis."""
    import json

    mestre, _p, _r = docs
    m = re.search(r"no_piso: <b>(\d+)</b>", mestre)
    if m is None:
        pytest.skip("painel de orçamento ausente (error_budget.json não gerado)")
    exibido = int(m.group(1))
    # Fonte da verdade: o próprio JSON, menos as fontes retiradas. Comparar
    # contra ele (e não contra o HTML re-parseado) testa a MESMA invariante sem
    # depender da ordem em que o template emite tabela e rodapé — foi essa
    # suposição de ordem que quebrou a 1ª versão deste teste.
    b = json.loads(rh._budget_path().read_text(encoding="utf-8"))
    bys = b.get("by_source", {})
    esperado = sum(d.get("no_piso", 0) for s, d in bys.items()
                   if s not in rh._SRC_RETIRADO)
    bruto = sum(d.get("no_piso", 0) for d in bys.values())
    assert exibido == esperado, (
        f"orçamento: rodapé diz {exibido}, mas as fontes mostradas somam "
        f"{esperado} (total bruto com as retiradas: {bruto})")
    if any(s in bys for s in rh._SRC_RETIRADO):
        assert exibido != bruto, (
            "o total não mudou ao retirar a fonte — o rodapé ainda vem do "
            "JSON bruto em vez das linhas mostradas")
