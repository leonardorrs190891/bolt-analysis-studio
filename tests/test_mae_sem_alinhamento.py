"""O MAE cru publicado ao lado do alinhado (2026-09-04).

A metrica da campanha divide o modelo pelo proprio valor no primeiro ciclo do
dado antes de pontuar. E' convencao pre-registrada e continua sendo a metrica
primaria, mas em 47 das 207 curvas ela absorve uma diferenca real, e em algumas
essa diferenca e' grande (li2022ti_axialmin_20Hz: MAE 0,0110 alinhado contra
0,3408 cru). A decisao de 2026-09-04 foi publicar os DOIS numeros, no artigo e
em cada report, para o leitor nao ter de acreditar que a divisao e' inocua.

O que estes testes protegem: que o numero cru saia de UMA funcao, que ele nao
seja recomputado por reinterpolacao (a armadilha que ja' custou 46% de erro no
transiente de embedding em 2026-07-27), e que a leitura crua use o MESMO
criterio de tres pernas, nao uma segunda regua.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "New_Theory"))

import pytest                                                    # noqa: E402


@pytest.fixture(scope="module")
def corpus():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.store import ValidationStore
    store = ValidationStore()
    recs = all_records()
    return recs, {r.case_id: store.get(r.case_id) for r in recs}


def test_sem_alinhamento_bate_com_o_calculo_direto(corpus):
    """O numero cru sai de metric_pred * align, e nao de uma reinterpolacao."""
    import numpy as np
    from bolt_analysis_studio.validation.runner import mae_sem_alinhamento

    _recs, res = corpus
    checados = 0
    for cid, r in res.items():
        if r is None or not getattr(r, "metric_pred", None):
            continue
        a = float(getattr(r, "align", None) or 1.0)
        pred = np.asarray(r.metric_pred, float) * a
        esperado = float(np.mean(np.abs(pred - np.asarray(r.metric_data,
                                                          float))))
        assert mae_sem_alinhamento(r) == pytest.approx(esperado, abs=1e-12), cid
        checados += 1
    assert checados > 200, f"so' {checados} casos conferidos"


def test_curva_sem_alinhamento_devolve_o_proprio_mae(corpus):
    """Com align = 1 os dois numeros sao o mesmo; e' o que justifica o report
    nao repetir o cru nessas curvas."""
    from bolt_analysis_studio.validation.runner import mae_sem_alinhamento

    _recs, res = corpus
    iguais = 0
    for r in res.values():
        if r is None or r.mae is None or not getattr(r, "metric_pred", None):
            continue
        if float(getattr(r, "align", None) or 1.0) == 1.0:
            assert mae_sem_alinhamento(r) == pytest.approx(r.mae, abs=1e-9)
            iguais += 1
    assert iguais > 100, "esperava a maioria das curvas sem alinhamento"


def test_o_efeito_no_censo_e_o_que_o_artigo_afirma(corpus):
    """Os numeros do paragrafo do §3.3 saem daqui, nao de digitacao."""
    from bolt_analysis_studio.validation import report_html as rh

    recs, res = corpus
    al = rh.efeito_do_alinhamento(recs, res)
    assert al["n_total"] == 205, "o efeito e' medido sobre o censo do artigo"
    assert al["n_alinhadas"] + (al["n_total"] - al["n_alinhadas"]) == 205
    assert al["atendem"] == 171
    assert al["atendem_cru"] <= al["atendem"], (
        "o alinhamento nunca deveria PIORAR o censo")
    assert al["perdem"] == al["atendem"] - al["atendem_cru"]
    assert al["mae_medio_cru"] >= al["mae_medio"]


def test_o_criterio_cru_usa_a_mesma_regua(corpus):
    """A leitura crua reusa _tripe_ok e _pisos_medidos. Se alguem escrever uma
    segunda regua, as duas divergem no primeiro ajuste."""
    import inspect
    from bolt_analysis_studio.validation import report_html as rh

    fonte = inspect.getsource(rh.efeito_do_alinhamento)
    assert "_tripe_ok" in fonte and "_pisos_medidos" in fonte
    assert "limite_sres" in fonte
    assert "caso_comparavel" in fonte, "tem de ser restrito ao censo"


def test_o_report_mostra_os_dois_numeros():
    """No HTML de cada caso, o cru aparece ao lado do alinhado — e so' quando
    ha' diferenca."""
    import inspect
    from bolt_analysis_studio.validation import report_html as rh

    fonte = inspect.getsource(rh)
    assert "MAE cru" in fonte
    assert "mae_sem_alinhamento" in fonte


def test_a_tabela_3_do_artigo_traz_as_duas_medianas():
    import inspect
    import build_paper_docx as bp

    fonte = inspect.getsource(bp._por_fonte)
    assert "mae_sem_alinhamento" in fonte
    corpo = (RAIZ / "New_Theory" / "build_paper_docx.py").read_text(
        encoding="utf-8")
    assert "median MAE, unaligned" in corpo
    assert "efeito_do_alinhamento" in corpo, (
        "o paragrafo do §3.3 tem de ler os numeros do codigo")
