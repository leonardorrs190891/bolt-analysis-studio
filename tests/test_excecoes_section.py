# -*- coding: utf-8 -*-
"""Invariantes da REESTRUTURAÇÃO do mestre (pedido do professor, 2026-08-07):
sumário de navegação, seção própria das exceções e filtros de estatuto no 3D.

O peso destes testes está nas exceções: o professor declarou que vai
abordá-las **com destaque em um artigo**, então elas deixam de ser só selo e
contagem e viram uma tabela de leitura única (caso + classe da prova + prova
assinada + métricas). O teste central garante que NENHUMA exceção do documento
fica fora da seção — uma exceção que só existe como selo espalhado é
exatamente o estado anterior, que o pedido veio corrigir.
"""
import re

import pytest

from bolt_analysis_studio.validation import report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.store import ValidationStore


@pytest.fixture(scope="module")
def mestre():
    store = ValidationStore()
    records = all_records()
    if not store.all_ids():
        pytest.skip("store vazio — rode `report --all` antes")
    results = {r.case_id: store.get(r.case_id) for r in records}
    return rh.master_report_html(records, results), records, results


def _bloco_excecoes(html):
    i = html.find('id="sec-excecoes"')
    assert i >= 0, "seção de exceções ausente"
    j = html.find("<h2", i + 10)
    return html[i:j if j > 0 else len(html)]


def test_toda_excecao_do_documento_esta_na_secao(mestre):
    """O invariante do artigo: a seção lista TODAS as exceções vivas.

    Membership vem de `_EXCECOES` (o dict-união que os selos usam) filtrado
    por `caso_no_documento` — mesma população, mesmos helpers. Se uma exceção
    nova for assinada e não aparecer aqui, este teste nomeia qual."""
    html, records, _ = mestre
    bloco = _bloco_excecoes(html)
    esperadas = [r.case_id for r in records if r.case_id in rh._EXCECOES
                 and rh.caso_no_documento(r.source, r.case_id)]
    assert esperadas, "nenhuma exceção viva — a seção deveria nem existir"
    faltam = [c for c in esperadas if f'reports/{c}.html' not in bloco]
    assert not faltam, f"exceções fora da seção do artigo: {faltam}"


def test_secao_traz_a_prova_assinada_de_cada_excecao(mestre):
    """A coluna que o artigo precisa: a PROVA, não só o nome do caso.

    Amostra as provas reais do dict (escapadas como o HTML as escreve)."""
    import html as H
    html, records, _ = mestre
    bloco = _bloco_excecoes(html)
    vivas = [r.case_id for r in records if r.case_id in rh._EXCECOES
             and rh.caso_no_documento(r.source, r.case_id)]
    sem_prova = [c for c in vivas
                 if H.escape(rh._EXCECOES[c])[:60] not in bloco]
    assert not sem_prova, (
        f"{len(sem_prova)} exceções sem o texto da prova na tabela: "
        f"{sem_prova[:3]}")


def test_secao_declara_a_intencao_do_artigo(mestre):
    """A decisão de 2026-08-07 fica REGISTRADA na página, não só no chat.

    Quem abrir o documento daqui a um mês precisa saber por que as exceções
    têm seção própria e estrela no sumário."""
    html, _, _ = mestre
    bloco = _bloco_excecoes(html)
    assert "artigo" in bloco, "a seção não declara o destaque planejado"
    assert "resolvidas" in bloco, (
        "a seção tem de repetir o estatuto: exceção conta como resolvida, "
        "nunca como no tripé")


def test_classe_da_prova_vem_dos_dicts_de_assinatura(mestre):
    """F5 vs F7 por membership, não por coluna digitada.

    Se as contagens exibidas divergirem dos dicts, alguém digitou a classe."""
    html, records, _ = mestre
    bloco = _bloco_excecoes(html)
    vivas = [r.case_id for r in records if r.case_id in rh._EXCECOES
             and rh.caso_no_documento(r.source, r.case_id)]
    n_f5 = sum(1 for c in vivas if c in rh._F5_EXCECOES)
    n_f7 = len(vivas) - n_f5
    assert bloco.count("réplicas (F5)") == n_f5
    assert bloco.count("prova de piso (F7)") == n_f7


def test_sumario_aponta_para_ancoras_que_existem(mestre):
    """Sumário com link morto é pior que sem sumário."""
    html, _, _ = mestre
    i = html.find('<nav class="sumario"')
    assert i >= 0, "sumário de navegação ausente"
    nav = html[i:html.find("</nav>", i)]
    alvos = re.findall(r'href="#([^"]+)"', nav)
    assert len(alvos) >= 5, f"sumário raso demais: {alvos}"
    mortos = [a for a in alvos if f'id="{a}"' not in html]
    assert not mortos, f"âncoras do sumário sem alvo na página: {mortos}"
    assert "exceções" in nav and "★" in nav, (
        "as exceções têm de estar destacadas no sumário (material do artigo)")


def test_3d_tem_filtros_de_estatuto_e_declara_ocultas(mestre):
    """Os filtros ◆/■ existem e a ocultação é DECLARADA, nunca silenciosa.

    Tirar da vista sem contar foi o defeito das 6 curvas n<6 (consertado em
    2026-08-07 de manhã); um filtro que esconde sem declarar reintroduziria a
    mesma classe de defeito pela porta do usuário."""
    html, _, _ = mestre
    for ctl in ('id="in-exc"', 'id="in-decl"'):
        assert ctl in html, f"controle {ctl} ausente do painel"
    assert "' ocultas'" in html, (
        "o JS não declara as ocultas na chave — omissão silenciosa")
    # o reset restaura os dois filtros (senão 'restaurar padrão' mente)
    assert "inExc.checked = true" in html and "inDecl.checked = true" in html
