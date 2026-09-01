def _fake_result(case_id, with_decomp=True):
    from bolt_analysis_studio.validation.runner import CaseResult
    decomp = ({"embedding": [0, 0.03, 0.05], "wear": [0, 0.01, 0.04],
               "creep": [0, 0.0, 0.01]} if with_decomp else {})
    return CaseResult(case_id=case_id, ok=True, cycles=[0, 500, 1000],
                      ratio=[1.0, 0.96, 0.90], mae=0.031, rmse=0.04,
                      maxerr=0.06, maxerr_at=800, final_pred=0.90,
                      final_data=0.88, decomp=decomp,
                      generated_at="2026-07-10T12:00:00",
                      engine_fingerprint="abc123")




def _synthetic_record(case_class="final_ratio", family="other"):
    # registro sintetico p/ cobrir a degradacao honesta (as classes
    # nao-comparaveis foram REMOVIDAS do registry em 2026-07-11)
    from bolt_analysis_studio.validation.case_registry import CaseRecord, all_records
    base = all_records()[0]
    return CaseRecord(case_id="sintetico_degrade", name="Sintetico",
                      source=base.source, family=family, case_class=case_class,
                      caveats=[], validation_case=base.validation_case,
                      csv_path=None, apparatus_note_path=None,
                      gallery_entry=None)

def test_case_report_sections_full_curve():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.report_html import case_report_html
    rec = next(r for r in all_records()
               if r.case_class == "full_curve" and r.family == "transverse")
    html = case_report_html(rec, _fake_result(rec.case_id))
    assert "Condições de contorno" in html          # utf-8 intacto
    assert "Modelo MSD" in html
    assert "Decomposição por mecanismo" in html     # §4 nova (pedido do professor)
    assert "embedding" in html and "wear" in html
    assert "MAE" in html and "0.031" in html
    assert 'charset="utf-8"' in html


def test_case_report_degrades_without_decomp_and_curve():
    from bolt_analysis_studio.validation.report_html import case_report_html
    rec = _synthetic_record(case_class="final_ratio", family="transverse")
    html = case_report_html(rec, _fake_result(rec.case_id, with_decomp=False))
    assert "re-simule" in html.lower()              # aviso do seed sem decomposicao
    assert "sem curva digitalizada" in html.lower() or "ratio final" in html.lower()


def test_case_report_shows_error_result():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.report_html import case_report_html
    from bolt_analysis_studio.validation.runner import CaseResult
    rec = all_records()[0]
    res = CaseResult(case_id=rec.case_id, ok=False, error="sem proveniência X",
                     generated_at="t", engine_fingerprint="f")
    html = case_report_html(rec, res)
    assert "sem proveniência X" in html


def test_error_section_has_signed_residual_and_narrative():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.report_html import case_report_html
    rec = next(r for r in all_records()
               if r.case_class == "full_curve" and r.family == "transverse"
               and r.gallery_entry is not None)
    html = case_report_html(rec, _fake_result(rec.case_id))
    assert "residual" in html                       # painel dedicado
    assert "sobre-prediz" in html or "sub-prediz" in html
    assert "pontos percentuais" in html             # narrativa interpretada
    assert "Estágio I" in html                      # MAE por estagio


def test_stage_maes_windows():
    import numpy as np
    from bolt_analysis_studio.validation.report_html import _stage_maes
    cd = np.linspace(0, 1000, 101)
    rd = np.ones(101)
    pred = np.ones(101); pred[:10] += 0.1           # erro so no estagio I (frac < 0.10)
    st = _stage_maes(cd, rd, pred)
    assert st["I"] > 0.05 and st["II"] < 1e-9 and st["III"] < 1e-9


def test_msd_section_lists_real_elements_and_loading(qapp):
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.report_html import _msd_section
    html = _msd_section(record("liu2025_M16_amp0p25"))
    assert "GROUND" in html                          # cadeia real do build_case_model
    assert "k [N/m]" in html                         # tabela de elementos
    assert "Carregamento global" in html
    assert "Para refazer no software" in html
    assert "Glossário" in html and "C_creep" in html


def test_msd_section_degrades_for_other_family(qapp):
    from bolt_analysis_studio.validation.report_html import _msd_section
    rec = _synthetic_record(family="other")
    html = _msd_section(rec)                         # nao levanta
    assert "não montável" in html


def test_report_sections_numbered_and_print_css(qapp):
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.report_html import case_report_html
    rec = next(r for r in all_records()
               if r.case_class == "full_curve" and r.family == "transverse")
    html = case_report_html(rec, _fake_result(rec.case_id))
    for h in ("1. Condições de contorno", "2. Modelo MSD",
              "3. Resultado e erro", "4. Decomposição por mecanismo",
              "5. Constantes usadas", "6. Caveats"):
        assert h in html, h
    assert "@media print" in html


def test_reports_have_theme_toggle(qapp):
    # opcao de tema escuro (pedido do professor): botao auto/escuro/claro
    # persistido em localStorage, aplicado via data-theme (tokens ja existem)
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.report_html import (case_report_html,
                                                             caso_no_documento,
                                                             master_report_html)
    rec = next(r for r in all_records() if r.case_class == "full_curve"
            and caso_no_documento(r.source, r.case_id))
    html = case_report_html(rec, _fake_result(rec.case_id))
    for m in ("bas_report_theme", "dataset.theme", "thbtn", "escuro"):
        assert m in html, m
    master = master_report_html([rec], {rec.case_id: _fake_result(rec.case_id)})
    assert "bas_report_theme" in master and "thbtn" in master


def test_report_v3_interactive_charts_and_toc(qapp):
    # report v3 (spec 2026-07-10-report-v3): graficos interativos JS-puro
    # (dados embutidos em data-chart), TOC, recursos (CSV/imprimir/colapso)
    import html as hmod
    import json
    import re
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.report_html import case_report_html
    rec = next(r for r in all_records()
               if r.case_class == "full_curve" and r.family == "transverse")
    html = case_report_html(rec, _fake_result(rec.case_id))
    payloads = [json.loads(hmod.unescape(m))
                for m in re.findall(r'data-chart="([^"]+)"', html)]
    assert len(payloads) >= 3                     # curvas, residuo, decomp
    lines = [p for p in payloads if p["type"] == "lines"]
    names = [s["name"] for p in lines for s in p["series"]]
    assert any("modelo" in n for n in names) and any("dado" in n for n in names)
    stack = [p for p in payloads if p["type"] == "stack"]
    assert stack and "embedding" in [s["name"] for s in stack[0]["series"]]
    assert html.count("BASCHART v1") == 1         # renderer embutido 1x
    for i in range(1, 7):                          # TOC com as 6 secoes
        assert f'href="#sec{i}"' in html, i
    assert "Baixar dados" in html                 # botao CSV (no renderer)
    assert "window.print()" in html               # botao imprimir
    assert "<noscript>" in html


def test_master_v3_filter_sort_chips(qapp):
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.report_html import (
        caso_no_documento, master_report_html)
    rec = next(r for r in all_records() if r.case_class == "full_curve"
            and caso_no_documento(r.source, r.case_id))
    master = master_report_html([rec], {rec.case_id: _fake_result(rec.case_id)})
    assert 'id="filtro"' in master                # busca instantanea
    assert "BASMASTER v2" in master               # js de filtro+sort+filtros rapidos
    assert 'class="chip"' in master               # chips de resumo


def test_master_has_budget_and_ledger_sections(qapp, tmp_path, monkeypatch):
    from bolt_analysis_studio.validation import error_budget as eb
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.report_html import (
        caso_no_documento, master_report_html)
    monkeypatch.setattr(eb, "BUDGET_PATH", tmp_path / "eb.json")
    eb.error_budget()                              # gera o JSON que o mestre le
    monkeypatch.setattr(
        "bolt_analysis_studio.validation.report_html._budget_path",
        lambda: tmp_path / "eb.json")
    rec = next(r for r in all_records() if r.case_class == "full_curve"
            and caso_no_documento(r.source, r.case_id))
    master = master_report_html([rec], {rec.case_id: _fake_result(rec.case_id)})
    assert "Orçamento de erro" in master
    assert "gap_adocao" in master
    assert "Convergência (ledger)" in master       # painel do ledger
    assert master.count("BASCHART v1") == 1        # mestre agora carrega o renderer


def test_write_reports_all_cases(tmp_path):
    from bolt_analysis_studio.validation.report_html import write_reports
    out = write_reports(out_dir=tmp_path,           # resultados: store/seed/None
                        store_path=tmp_path / "store.json")
    reports = list((tmp_path / "reports").glob("*.html"))
    assert len(reports) >= 114                      # 114 comparaveis + USER
    master = (tmp_path / "validation_report.html").read_text(encoding="utf-8")
    assert "casos de valida" in master              # cabecalho com contagem
    assert "curva completa" in master               # coluna de classe
    assert "gerado em" in master.lower()


def test_ensure_reports_generates_master(tmp_path):
    from bolt_analysis_studio.validation import report as cli
    master = cli.ensure_reports(out_dir=tmp_path,
                                store_path=tmp_path / "store.json")
    assert master.name == "validation_report.html" and master.exists()


def test_cli_single_case(tmp_path):
    import os
    import subprocess
    import sys
    from pathlib import Path
    from bolt_analysis_studio.validation.case_registry import all_records
    rec = min((r for r in all_records() if r.case_class == "full_curve"),
              key=lambda r: r.validation_case.n_cycles)
    src_dir = str(Path(__file__).resolve().parents[1] / "src")
    env = {**os.environ,
           "PYTHONPATH": src_dir + os.pathsep + os.environ.get("PYTHONPATH", "")}
    out = subprocess.run(
        [sys.executable, "-m", "bolt_analysis_studio.validation.report",
         "--case", rec.case_id, "--cap", "300", "--out", str(tmp_path),
         "--store", str(tmp_path / "store.json")],
        capture_output=True, text=True, env=env)
    assert out.returncode == 0, out.stderr
    assert (tmp_path / "reports" / f"{rec.case_id}.html").exists()


# ---------------------------------------------------------------------------
# Defeito 2026-07-27: a pagina por caso mostrava QUATRO numeros discordantes —
# cabecalho (MAE do runner: alinhado + trimado) sobre grafico cru e integral,
# com MAE-por-estagio e residuo recomputados crus, sem trim e reinterpolados na
# grade AMOSTRADA. No li2022ti_axial_10Hz_full dava 0.0317 no topo contra
# 0.19/0.30/0.28 nos estagios do mesmo documento. Estes testes prendem as duas
# metades do conserto: (1) o report LE os vetores da metrica em vez de
# recomputar; (2) o que ele plota e' a curva alinhada.
# ---------------------------------------------------------------------------

def _aligned_result(case_id):
    from bolt_analysis_studio.validation.runner import CaseResult
    # modelo cai a 0.60 antes do 1o ponto do dado (assentamento): align=0.60
    return CaseResult(
        case_id=case_id, ok=True,
        cycles=[0.0, 100.0, 500.0, 1000.0, 2000.0],
        ratio=[1.0, 0.60, 0.58, 0.56, 0.54],
        align=0.60,
        metric_x=[100.0, 500.0, 1000.0],
        metric_pred=[1.0, 0.9667, 0.9333],
        metric_data=[1.0, 0.97, 0.94],
        mae=0.005, rmse=0.005, resid_std=0.001, maxerr=0.007, maxerr_at=1000,
        final_pred=0.54, final_data=0.94,
        config_used={"trim_n_max": 1000.0},
        generated_at="2026-07-27T00:00:00", engine_fingerprint="deadbeef")


def test_report_plots_the_curve_the_metric_measures():
    """A serie 'modelo' do grafico principal e' a ALINHADA (ancorada em 1.0 no
    1o ciclo do dado), nao a crua — senao o grafico contradiz o cabecalho."""
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.report_html import case_report_html
    rec = next(r for r in all_records() if r.case_class == "full_curve")
    html = case_report_html(rec, _aligned_result(rec.case_id))
    assert "alinhado" in html, "a serie alinhada precisa estar rotulada"
    assert "modelo cru" in html, "a curva crua segue visivel (tracejada)"
    # o divisor aparece explicito na nota de convencao
    assert "0.6000" in html or "÷0.60" in html


def test_report_reads_metric_vectors_instead_of_reinterpolating():
    """Com metric_* gravados, o residuo/estagios saem DELES. Reinterpolar na
    grade amostrada daria ~0.46 de erro no transiente de assentamento."""
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.report_html import case_report_html
    rec = next(r for r in all_records() if r.case_class == "full_curve")
    res = _aligned_result(rec.case_id)
    html = case_report_html(rec, res)
    # nenhum MAE por estagio pode explodir p/ a ordem do erro de reinterpolacao
    import re
    vals = [float(m) for m in re.findall(r'>(0\.\d{3,5})<', html)]
    big = [v for v in vals if v > 0.3]
    assert not big, f"MAE por estagio inconsistente c/ o cabecalho: {big}"


def test_trim_window_is_visible_on_the_page():
    """Trim recorta a METRICA — a pagina precisa dizer isso e quanto custa."""
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.report_html import case_report_html
    rec = next(r for r in all_records() if r.case_class == "full_curve")
    html = case_report_html(rec, _aligned_result(rec.case_id))
    assert "Trim em N" in html
    assert "fora-do-modelo" in html or "fora da métrica" in html
