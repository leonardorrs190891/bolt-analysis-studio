# -*- coding: utf-8 -*-
"""Guarda AUTO-REFERENTE: piso que diz "lido-do-dado" nao pode exceder a curva.

## O defeito que motivou (medido 2026-08-16)

Dois grupos do `ECCLES_2010` traziam

    prov.loose_arrest_floor = "lido-do-dado (assintota final crua >=0.03; ...)"
    cfg.loose_arrest_floor  = 0.137   (fig7d)  /  0.059   (fig8a)

e a leitura L24 do CSV **cru** dava **0.0000** e **0.0122**. Na `fig7d` a cauda
crua e' `... 0.033 · 0.007 · 0.000 · 0.000` -- a curva COLAPSA A ZERO. O 0.137
corresponde a `tail_frac ~ 0.40`, faixa em que o proprio helper devolve
`plateau=False`: e' a media de uma RAMPA EM QUEDA, nao uma assintota.

O numero nao era gratuito -- ele imitava uma DESACELERACAO DE CAUDA real (o dado
leva 1643 ciclos de 0.25 a 0.10 e o modelo 16), e `loose_arrest_floor` e' a
unica alavanca anti-runaway do engine. O que estava errado era a AFIRMACAO.
Consertado pela adocao R2 (prereg 1f1a16d): os dois grupos passaram a declarar
`proxy-de-desaceleracao-de-cauda (fitado-this-rig...)`.

## Por que a guarda e' possivel SEM ancora de literatura

Porque a referencia e' A PROPRIA CURVA. `arrest_floor_from_curve` le o plato
final do CSV cru; se o rotulo diz que o numero veio dali, ele tem de bater com o
que esta la. Isso torna falsificavel **1 das 29** constantes que a medicao do
item S apontou como infalsificaveis (85% das afirmacoes de procedencia nao podem
ser contraditas por instrumento nenhum).

## A regra e' UNILATERAL, e isso e' deliberado

Piso ABAIXO da leitura e' escolha CONSERVADORA: o piso segura menos do que o
dado permitiria, e nao infla metrica. So o EXCESSO mente, porque so o excesso
compra metrica. Medido: ha grupos legitimamente muito abaixo da leitura.

## O que este teste NAO faz

Nao julga o VALOR (piso pode ser fitado, e ai o rotulo tem de dizer isso), nao
toca config, nao mexe no censo. Ele so' exige que a AFIRMACAO e o NUMERO
concordem.

## Nasce com ZERO violacoes -- por isso ha teste de PERTURBACAO aqui

O R2 ja consertou as duas que existiam. Guarda que passa por merito no dia em
que nasce nao esta validada; `test_a_guarda_pega_o_defeito_do_R2` reconstroi o
caso historico e exige que ela dispare.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

TOL = 0.02          # folga de digitalizacao; abaixo disso nao se acusa ninguem
_ALEGA = "lido-do-dado"


def _leitura_l24(rec):
    """Piso implicito do plato final do CSV **CRU** da propria curva.

    ⚠️ CRU, nunca `metric_data`: aquele e' o dado DEPOIS do FLOOR_TRIM=0.10, e
    foi le-lo que produziu o defeito de origem desta guarda (um "plato em 0.165"
    que era o piso da JANELA DA METRICA, nao do dado).
    """
    from library_common import load_full_curve
    from bolt_analysis_studio.calibration.provenance import arrest_floor_from_curve
    try:
        rel = rec.csv_path.relative_to(pathlib.Path(".").resolve()).as_posix()
    except (ValueError, AttributeError):
        rel = str(rec.csv_path)
    _, ratio = load_full_curve(rel)
    piso, _br = arrest_floor_from_curve(ratio)
    return float(piso)


def _alegacoes(cfg_override=None):
    """[(case_id, grupo, piso, leitura_l24)] p/ toda curva cujo grupo GOVERNANTE
    afirma `lido-do-dado` no `loose_arrest_floor`.

    ⚠️ O grupo sai de `runner._adopted_for` -- o MESMO resolvedor que o runner
    usa. Casar por prefixo da fonte INFLA a lista: uma fonte com 8 grupos, dos
    quais 1 alega, traria as 8. Foi esse atalho que me fez publicar "9 grupos /
    21 curvas" quando sao 5.
    """
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation import runner as rn
    from bolt_analysis_studio.calibration import knowledge_base as kb

    out = []
    for rec in sorted(all_records(), key=lambda z: z.case_id):
        key = rn._adopted_for(rec.source, rec.case_id,
                              rec.validation_case.bolt_size)
        if not key:
            continue
        blk = (cfg_override or {}).get(key) or kb.adopted_config(key) or {}
        lab = (blk.get("prov") or {}).get("loose_arrest_floor")
        if not lab or _ALEGA not in str(lab).lower():
            continue
        # ⚠️ PONTO CEGO CONSERTADO 2026-08-19: o piso pode viver no cfg do
        # GRUPO **ou** em `cfg.per_case[token]`, e a 1a versao lia so o
        # primeiro. Medido: 25 pisos de grupo (que a guarda via) contra **8 em
        # per_case que ela NAO via** — e os 8 estao em grupos que alegam
        # `lido-do-dado`, ou seja, exatamente a populacao que ela existe para
        # checar (SUN_2025_REASSY x5, SUN_2025_CRIMP x2, CHU_2026_test1).
        #
        # A validacao original nao pegou porque as 5 alegacoes VIVAS eram todas
        # de grupo (ECCLES) — teste validado por perturbacao ainda pode ter
        # ponto cego na SELECAO, e a perturbacao nao o revela: ela confirma que
        # a regra dispara no que a selecao entrega, nao que a selecao esteja
        # completa. Quem denunciou foi um prereg da sessao paralela citando um
        # piso desta fonte que a guarda nunca tinha olhado.
        #
        # Token de `per_case` casa por SUBSTRING do case_id (convencao do
        # CLAUDE.md); o mais LONGO vence, para nao deixar "_grease_standard"
        # perder de um token generico.
        cfg = blk.get("cfg") or {}
        piso = cfg.get("loose_arrest_floor")
        if piso is None:
            cands = [(len(tok), d["loose_arrest_floor"])
                     for tok, d in (cfg.get("per_case") or {}).items()
                     if isinstance(d, dict) and "loose_arrest_floor" in d
                     and tok.lower() in rec.case_id.lower()]
            if cands:
                piso = max(cands)[1]
        if piso is None or float(piso) <= 0:
            continue
        try:
            l24 = _leitura_l24(rec)
        except Exception:                                   # noqa: BLE001
            continue          # curva sem CSV legivel nao e' evidencia de nada
        out.append((rec.case_id, key, float(piso), l24))
    return out


@pytest.fixture(scope="module")
def alegacoes():
    return _alegacoes()


def test_ha_alegacoes_a_checar(alegacoes):
    """Se ninguem mais alega `lido-do-dado`, a guarda vira no-op SILENCIOSA.

    Sem isto, apagar o rotulo de todos os grupos faria o teste "passar" sem
    checar nada -- ausencia tem de ser visivel.
    """
    assert alegacoes, (
        "NENHUM grupo alega `lido-do-dado` para `loose_arrest_floor`.\n"
        "Ou a convencao de rotulo mudou, ou o resolvedor de grupo quebrou. "
        "Nos dois casos esta guarda deixou de guardar — investigue antes de "
        "relaxar este assert.")


def test_piso_que_diz_ler_o_dado_nao_excede_o_dado(alegacoes):
    """A regra. Unilateral: so' o EXCESSO acusa."""
    ruins = [(c, k, p, l) for c, k, p, l in alegacoes if p - l > TOL]
    assert not ruins, (
        "Piso rotulado `lido-do-dado` ACIMA da leitura L24 do CSV cru:\n"
        + "\n".join(
            f"  {c}\n"
            f"     grupo {k} · piso adotado {p:.4f} · leitura do cru {l:.4f} "
            f"· excesso {p - l:+.4f}"
            for c, k, p, l in ruins)
        + "\n\nDuas saidas legitimas, e a escolha e' de FISICA, nao de estilo:\n"
          "  (a) corrigir o VALOR para a leitura do cru — honesto, mas pode\n"
          "      deixar a curva pior e sem alavanca;\n"
          "  (b) corrigir o ROTULO, se o numero faz trabalho fisico real que\n"
          "      nao e' leitura do dado (foi o que a adocao R2 fez: o piso\n"
          "      imitava uma DESACELERACAO DE CAUDA medida, e passou a\n"
          "      declarar `proxy-de-desaceleracao-de-cauda (fitado-this-rig)`).\n"
          "Adotar qualquer das duas exige assinatura.")


def test_a_regra_e_unilateral_piso_abaixo_da_leitura_nao_acusa(alegacoes):
    """Piso ABAIXO da leitura e' conservador e NAO deve disparar.

    Guarda contra alguem "endurecer" a regra para |piso - l24| > TOL, o que
    acusaria escolhas legitimas: ha grupos bem abaixo da leitura de proposito.
    """
    # ⚠️ POR PERTURBACAO, e nao sobre o dado vivo. Hoje as 5 alegacoes estao
    # todas LEVEMENTE ACIMA (+0.0004 a +0.0035), entao a lista "abaixo" e'
    # VAZIA e um teste que iterasse sobre ela nao assertaria NADA — foi assim
    # que a 1a versao deste teste nasceu vazia. Teste que nao pode falhar nao
    # e' teste.
    from bolt_analysis_studio.calibration import knowledge_base as kb
    k = "ECCLES_2010_fig3"
    blk = kb.adopted_config(k)
    assert blk, "grupo %s sumiu do config adotado" % k
    # piso MUITO abaixo da leitura (~0.194): escolha conservadora legitima
    baixo = {k: {"cfg": dict(blk.get("cfg", {}), loose_arrest_floor=0.01),
                 "prov": dict(blk.get("prov", {}),
                              loose_arrest_floor="lido-do-dado (teste)")}}
    alv = [a for a in _alegacoes(cfg_override=baixo) if a[1] == k]
    assert alv, ("a perturbacao nao produziu alegacao — teste vazio, ramo "
                 "INCONCLUSIVO")
    _cid, _k, piso, l24 = alv[0]
    assert l24 - piso > TOL, ("a perturbacao nao ficou ABAIXO da leitura "
                              f"(piso {piso:.4f}, L24 {l24:.4f}) — nao testa "
                              "unilateralidade")
    assert piso - l24 <= TOL, (
        f"{_cid}: piso {piso:.4f} ABAIXO da leitura {l24:.4f} seria acusado.\n"
        "A regra e' UNILATERAL de proposito — piso abaixo e' escolha "
        "conservadora (segura menos do que o dado permitiria) e nao infla "
        "metrica. So' o EXCESSO mente, porque so' o excesso compra metrica.")

    # e o dado VIVO tambem nao pode ter ninguem acusado por ficar abaixo
    acusadas = [c for c, _kk, p, l in alegacoes if l - p > TOL and p - l > TOL]
    assert not acusadas, acusadas


def test_a_guarda_pega_o_defeito_do_R2():
    """PERTURBACAO: reconstroi o caso historico e exige que a guarda dispare.

    A guarda nasce com ZERO violacoes (o R2 consertou as duas que existiam),
    entao ela precisa ser vista FALHANDO ao menos uma vez, senao nao esta
    validada. Reconstroi o estado pre-R2 da `ECCLES_2010_fig7d` em memoria --
    **sem tocar o arquivo de config**.
    """
    from bolt_analysis_studio.calibration import knowledge_base as kb
    k = "ECCLES_2010_fig7d"
    blk = kb.adopted_config(k)
    assert blk, "grupo %s sumiu do config adotado" % k
    pre_r2 = {k: {
        "cfg": dict(blk.get("cfg", {}), loose_arrest_floor=0.137),
        "prov": dict(blk.get("prov", {}),
                     loose_arrest_floor="lido-do-dado (assintota final crua "
                                        ">=0.03; fisica=torque de prevalencia)"),
    }}
    alv = [a for a in _alegacoes(cfg_override=pre_r2) if a[1] == k]
    assert alv, ("a perturbacao nao produziu alegacao nenhuma — o teste nao "
                 "testou nada (ramo INCONCLUSIVO)")
    _cid, _k, piso, l24 = alv[0]
    assert piso == pytest.approx(0.137)
    assert l24 == pytest.approx(0.0, abs=1e-6), (
        "a leitura L24 do cru da fig7d deixou de ser 0.0000 (era: a cauda "
        f"colapsa a zero). Veio {l24:.4f} — o CSV mudou?")
    assert piso - l24 > TOL, (
        "a guarda NAO dispararia no defeito historico do R2 — perturbacao "
        "invalida, ramo INCONCLUSIVO")


def test_a_guarda_le_o_CRU_e_nunca_a_janela_da_metrica():
    """Estrutural: `metric_data` nao pode aparecer neste arquivo.

    Foi ler `metric_data` (o dado DEPOIS do FLOOR_TRIM=0.10) e chamar o ultimo
    valor de "piso de arresto" que produziu o defeito de origem — uma afirmacao
    de que o dado "arresta em 0.165" quando o cru colapsa a 0.02-0.06. Uma
    guarda contra esse defeito que usasse a mesma fonte errada seria inutil.
    """
    # ⚠️ Procura o ACESSO A ATRIBUTO (`.metric_data`), nao o token solto: a 1a
    # versao buscava a string crua e o teste ACUSAVA A SI MESMO, porque a
    # propria mensagem de erro a continha. Codigo que de fato leia a janela da
    # metrica faz `res.metric_data` / `r.metric_data`; prosa nao.
    alvo = "." + "metric_data"
    txt = pathlib.Path(__file__).read_text(encoding="utf-8")
    linhas = [ln for ln in txt.splitlines()
              if alvo in ln and not ln.lstrip().startswith("#")]
    assert not linhas, (
        "este arquivo passou a LER a janela da metrica:\n  "
        + "\n  ".join(linhas)
        + "\nA leitura tem de vir do CSV CRU (`load_full_curve`), senao a "
          "guarda herda o proprio defeito que existe para pegar — um 'plato' "
          "que e' so' o FLOOR_TRIM=0.10 aparecendo.")
