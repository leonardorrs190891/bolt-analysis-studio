# -*- coding: utf-8 -*-
"""Invariantes do exportador das exceções para o artigo (2026-08-07).

O risco que estes testes perseguem não é o TeX malformado — é a LISTA
divergir: um export que mantivesse cópia própria das exceções envelheceria a
cada retratação da campanha (houve 4 só em 2026-08-07, P-10/P-11/P-12) e o
professor levaria para o artigo uma tabela que o documento mestre já não
afirma. Por isso o teste central compara o export com `_EXCECOES` VIVO.
"""
import csv
import importlib.util
import pathlib
import sys

import pytest

from bolt_analysis_studio.validation import report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.store import ValidationStore


def _mod():
    gen = (pathlib.Path(__file__).resolve().parents[1] / "New_Theory"
           / "export_excecoes_artigo.py")
    spec = importlib.util.spec_from_file_location("export_excecoes", gen)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def saida(tmp_path_factory):
    if not ValidationStore().all_ids():
        pytest.skip("store vazio")
    out = tmp_path_factory.mktemp("artigo")
    r = _mod().build(out)
    return out, r


def _vivas():
    return [rec.case_id for rec in all_records()
            if rec.case_id in rh._EXCECOES
            and rh.caso_no_documento(rec.source, rec.case_id)]


def test_export_cobre_exatamente_as_excecoes_vivas(saida):
    """Nem uma a mais (retratada que voltou), nem uma a menos (assinada nova).

    O CSV é a leitura de máquina; comparar por conjunto pega os dois lados."""
    out, _ = saida
    rows = list(csv.DictReader((out / "excecoes.csv").open(encoding="utf-8")))
    assert {r["case_id"] for r in rows} == set(_vivas())


def test_tex_escapa_e_carrega_procedencia(saida):
    """O `.tex` compila de verdade: `_` cru dentro de texto quebra o LaTeX,
    e os case_ids têm `_` aos montes. E a procedência (fingerprint) tem de
    estar no arquivo — uma tabela sem carimbo não se audita."""
    out, r = saida
    tex = (out / "tabela_excecoes.tex").read_text(encoding="utf-8")
    # só as linhas de DADO: a janela midrule→bottomrule — o cabeçalho também
    # termina em \\ e tem &, e a 1ª versão deste filtro o contava (23 == 22+1)
    linhas = tex.splitlines()
    corpo = linhas[linhas.index(r"\midrule") + 1:linhas.index(r"\bottomrule")]
    assert len(corpo) == r["n"]
    for l in corpo:
        # todo `_` de dado tem de estar escapado
        assert "\\_" in l or "_" not in l.split("%")[0], f"underscore cru: {l[:80]}"
    assert r["fp"] in tex, "fingerprint ausente do .tex"
    assert "booktabs" in tex


def test_classe_bate_com_os_dicts_de_assinatura(saida):
    out, r = saida
    rows = list(csv.DictReader((out / "excecoes.csv").open(encoding="utf-8")))
    n_f5 = sum(1 for x in rows if x["classe"].startswith("replicas"))
    assert n_f5 == sum(1 for c in _vivas() if c in rh._F5_EXCECOES)
    assert n_f5 == r["n_f5"]


def test_readme_documenta_regeneracao(saida):
    """Quem achar a pasta daqui a meses precisa saber COMO regerar e de onde
    os dados vieram — export sem README vira dado órfão de procedência."""
    out, _ = saida
    md = (out / "README_artigo_excecoes.md").read_text(encoding="utf-8")
    assert "export_excecoes_artigo.py" in md
    assert "_EXCECOES" in md and "fingerprint" in md
