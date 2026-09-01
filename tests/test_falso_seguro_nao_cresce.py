"""FALSO SEGURO não pode crescer — gate de adoção, não 4ª perna.

## O que é falso seguro, e por que ele merece um gate próprio

O modelo diz que a junta **retém** acima do limiar da norma e o ensaio diz que
**afrouxou**. É o único erro do modelo com consequência de engenharia: falso
**alarme** (diz que afrouxa e não afrouxou) custa dinheiro; falso **SEGURO** custa a
junta. Os dois não são simétricos, e o tripé não distingue nenhum dos dois — ele mede
fidelidade de curva.

## ⚠️ O achado que motivou o gate (2026-08-25)

Medido nas 205 comparáveis, no limiar da ISO 16130 (85 %): **7 falsos seguros, e 3
deles PASSAM o tripé**.

| curva | dado | modelo | MAE |
|---|---:|---:|---:|
| `rousseau2025_hdpe_t10_amp0p2` | 0,799 | **0,869** | **0,0260** |
| `liu2022_fig8_multi_t4` | 0,845 | **0,924** | 0,0380 |
| `sun2025efa109235_axial_F17.5kN_standard` | 0,814 | **0,861** | 0,0330 |

A primeira tem MAE 0,0260 — fidelidade excelente — e informaria *"87 % de retenção"*
onde o ensaio mede **80 %**. **Não é defeito do tripé:** é uma pergunta que a régua
não faz.

## Por que GATE e não 4ª perna

Promover falso seguro a 4ª perna **mudaria o censo publicado**, e trocar a régua é
decisão do professor — a sessão de 2026-07-29 mostrou como uma perna nova cascateia
por todo documento vivo. Um gate custa **zero** ao censo e pega a direção perigosa:
*nenhuma adoção pode aumentar o número de falsos seguros*.

⚠️ Este teste **não** proíbe que o número mude — ele proíbe que **cresça sem
registro**. Se uma adoção legitimamente o aumentar (por exemplo, corrigindo uma curva
que estava otimista pelo lado errado), o baseline é atualizado no mesmo commit, com a
razão. É o mesmo desenho de `_COLISOES_CONHECIDAS` e do `parada_baseline.json`: a
dívida pode encolher em silêncio, nunca crescer.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import bolt_analysis_studio.validation.report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.runner import CaseResult

RAIZ = Path(__file__).resolve().parents[1]

# ⚠️ BASELINE DECLARADO, medido em 2026-08-25 sobre as 205 comparáveis.
# Pode ENCOLHER livremente; para CRESCER, atualize aqui no mesmo commit com a
# razão — é isso que torna o gate um gate e não um número decorativo.
_BASE = {0.85: 7, 0.80: 6}

# As que hoje passam o tripé E são falso seguro. Esta lista é a mais sensível do
# arquivo: uma curva entrar aqui significa que a régua aprova um caso em que o
# software informaria "seguro" contra o ensaio.
_FS_NO_TRIPE = {
    "rousseau2025_hdpe_t10_amp0p2",
    "liu2022_fig8_multi_t4",
    "sun2025efa109235_axial_F17.5kN_standard",
}


@pytest.fixture(scope="module")
def dados():
    p = RAIZ / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"
    if not p.exists():
        pytest.skip("store canônico ausente")
    store = json.loads(p.read_text(encoding="utf-8"))
    recs = store.get("cases", store)
    comp = [r for r in all_records()
            if r.case_id in recs and rh.caso_comparavel(r.source, r.case_id)]
    res = {}
    for r in comp:
        try:
            res[r.case_id] = CaseResult.from_dict(recs[r.case_id])
        except Exception:
            pass
    pisos = rh._pisos_medidos([(r.source, res[r.case_id]) for r in comp
                               if r.case_id in res])
    return comp, res, pisos


def _falsos(comp, res, lim):
    return [r.case_id for r in comp
            if res.get(r.case_id) is not None
            and rh.falso_seguro(res[r.case_id], lim)]


@pytest.mark.parametrize("lim,esperado", sorted(_BASE.items()))
def test_falso_seguro_nao_CRESCE(dados, lim, esperado):
    """O gate. Pode encolher; crescer exige atualizar o baseline com a razão."""
    comp, res, _pisos = dados
    fs = _falsos(comp, res, lim)
    assert len(fs) <= esperado, (
        f"falsos seguros no limiar {lim:.0%}: {esperado} -> {len(fs)}. Uma adoção "
        f"AUMENTOU o número de curvas em que o modelo diz 'retém' e o ensaio diz "
        f"que afrouxou — é o único erro com consequência de engenharia.\n"
        f"Novas: {sorted(set(fs))}\n"
        f"Se o aumento for legítimo, atualize `_BASE` neste commit COM A RAZÃO.")
    if len(fs) < esperado:
        pytest.fail(
            f"falsos seguros CAÍRAM de {esperado} para {len(fs)} no limiar "
            f"{lim:.0%} — notícia boa. Atualize `_BASE[{lim}]` = {len(fs)} e "
            f"registre o que resolveu, no idioma das outras guardas.")


def test_as_que_passam_o_tripe_sao_AS_MESMAS(dados):
    """Curva nova aprovada pela régua E falso seguro = a régua ficou mais frouxa
    exatamente onde ela não deveria.

    Este é o invariante mais sensível do arquivo, e é por isso que a lista é
    explícita: `_FS_NO_TRIPE` não é perdão, é o conjunto que o professor viu ao
    decidir que a marca seria informacional (ITEM AB, 2026-08-25).
    """
    comp, res, pisos = dados
    agora = {r.case_id for r in comp
             if res.get(r.case_id) is not None
             and rh.falso_seguro(res[r.case_id], 0.85)
             and rh._tripe_ok(res[r.case_id], rh.limite_sres(r.source, pisos))}
    novas = agora - _FS_NO_TRIPE
    assert not novas, (
        f"curva(s) NOVA(s) aprovada(s) pelo tripé E falso seguro: {sorted(novas)}. "
        f"O software passaria a informar 'retém' contra o ensaio numa curva que a "
        f"régua aprova. Se for real, entra em `_FS_NO_TRIPE` com a razão.")
    saíram = _FS_NO_TRIPE - agora
    if saíram:
        pytest.fail(
            f"{sorted(saíram)} deixaram de ser falso seguro aprovado — notícia "
            f"boa. Retire de `_FS_NO_TRIPE` e registre o que resolveu.")


def test_o_helper_le_os_VETORES_DA_METRICA(dados):
    """`falso_seguro` tem de ler `metric_*`, não a curva crua.

    A curva crua é pré-alinhamento e pré-`FLOOR_TRIM`: o último ponto dela pode
    estar abaixo de 0,10 (fora da métrica) ou num ciclo que o modelo nem simulou.
    Ler dali produziria falso seguro fantasma — a armadilha do `metric_data`
    documentada no `CLAUDE.md`, na direção oposta.
    """
    import inspect
    src = inspect.getsource(rh.falso_seguro)
    assert "metric_data" in src and "metric_pred" in src
    assert "ratio" not in src, (
        "`falso_seguro` passou a ler `ratio` (curva crua, integral) — ela não é "
        "o que a métrica compara")


def test_a_secao_do_report_NOMEIA_as_curvas(dados):
    """Contar falso seguro sem nomear não deixa ninguém agir."""
    html = rh._decisao_html(*dados)
    assert html, "a seção de decisão saiu vazia"
    for cid in _FS_NO_TRIPE:
        assert cid in html, f"{cid} não aparece nomeada na seção"
    assert "não é defeito do tripé" in html, (
        "sumiu a explicação de que o tripé não faz esta pergunta — sem ela a "
        "seção lê como acusação à régua")
    assert "informacional" in html, (
        "sumiu a marca de que é informacional; sem isso alguém lê como 4ª perna")
