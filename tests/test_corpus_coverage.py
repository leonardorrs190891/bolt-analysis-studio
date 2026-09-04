"""Cobertura do corpus DENTRO do software (2026-09-01).

O pedido foi "todas as analises de cada artigo e cada curva pre-carregadas e
analisaveis no software". Na data em que este arquivo foi escrito isso ja era
verdade, medido: 207 casos em 28 fontes, todos com analise no store canonico e
todos abrindo no modelo. O teste existe para que continue sendo verdade. Uma
curva nova que entre no corpus e nao chegue ao store, ou um caso que pare de
abrir no Model/Run, quebra aqui em vez de sumir da arvore da GUI em silencio.

A contagem da GUI e' medida na ARVORE, nao no registry: o que interessa e' o
que o usuario ve. E o marcador de ausencia na arvore nao e' string vazia, e' o
travessao (sem analise) ou "erro" (simulacao falhou), que e' o que se afere.
"""
import pytest

from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.store import ValidationStore


@pytest.fixture(scope="module")
def registry():
    recs = all_records()
    assert recs, "registry vazio: o corpus nao foi encontrado"
    return recs


@pytest.fixture(scope="module")
def store():
    st = ValidationStore()
    assert st.all_ids(), f"store canonico vazio em {st.path}"
    return st


def test_todo_caso_do_registry_tem_analise_pre_carregada(registry, store):
    ids_reg = {r.case_id for r in registry}
    ids_store = set(store.all_ids())
    sem_analise = sorted(ids_reg - ids_store)
    orfaos = sorted(ids_store - ids_reg)
    assert not sem_analise, f"{len(sem_analise)} casos sem analise: {sem_analise[:5]}"
    assert not orfaos, f"{len(orfaos)} analises orfas no store: {orfaos[:5]}"


def test_toda_analise_traz_as_tres_pernas_do_criterio(registry, store):
    """MAE, residuo maximo e dispersao do residuo: as tres pernas que o artigo
    usa para decidir se uma curva atende. Faltando uma, o caso aparece na
    arvore mas nao pode ser julgado."""
    incompletos = [
        r.case_id for r in registry
        if any(getattr(store.get(r.case_id), k, None) is None
               for k in ("mae", "maxerr", "resid_std"))
    ]
    assert not incompletos, (
        f"{len(incompletos)} casos com analise incompleta: {incompletos[:5]}")


def test_todo_caso_abre_no_modelo(registry):
    """"Abrir no Model/Run" e' o caminho pelo qual o usuario RE-analisa uma
    curva. Se build_case_model levanta, aquele artigo fica so' de leitura."""
    from bolt_analysis_studio.validation.gui_bridge import build_case_model

    falhas = []
    for r in registry:
        try:
            if build_case_model(r) is None:
                falhas.append((r.case_id, "retornou None"))
        except Exception as exc:                       # noqa: BLE001
            falhas.append((r.case_id, f"{type(exc).__name__}: {exc}"))
    assert not falhas, f"{len(falhas)} casos nao abrem no modelo: {falhas[:5]}"


def test_a_arvore_da_gui_mostra_o_corpus_inteiro(qapp, registry, store):
    from bolt_analysis_studio.gui.chrome.widgets.validation_browser import (
        ValidationBrowser)

    br = ValidationBrowser(store=store)
    br.populate()
    tree = br.tree

    n_fontes = tree.topLevelItemCount()
    casos = [tree.topLevelItem(i).child(j)
             for i in range(n_fontes)
             for j in range(tree.topLevelItem(i).childCount())]

    assert n_fontes == len({r.source for r in registry})
    assert len(casos) == len(registry)

    vazios = [c.text(0) for c in casos if c.text(1).strip() in ("", "—")]
    com_erro = [c.text(0) for c in casos if c.text(1).strip() == "erro"]
    assert not vazios, f"{len(vazios)} casos sem analise na arvore: {vazios[:5]}"
    assert not com_erro, f"{len(com_erro)} casos com erro: {com_erro[:5]}"
