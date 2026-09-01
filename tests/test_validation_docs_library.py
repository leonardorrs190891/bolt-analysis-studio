"""Os reports de validacao fazem parte da biblioteca de documentacao do
software (pedido do professor 2026-07-10: 'ao final devemos ter isso na
biblioteca de documentacao do software')."""


def test_docs_library_has_validation_reports_index():
    from pathlib import Path
    p = Path("src/bolt_analysis_studio/docs/VALIDATION_CASE_REPORTS.md")
    assert p.exists()
    txt = p.read_text(encoding="utf-8")
    assert "114" in txt
    assert "validation_report.html" in txt          # ponto de entrada
    assert "bolt_analysis_studio.validation.report" in txt   # CLI de regeneracao


def test_documentation_tab_has_validation_section():
    from bolt_analysis_studio.gui.documentation_tab import DOCUMENTATION
    key = next((k for k in DOCUMENTATION
                if "validation" in k.lower()), None)
    assert key is not None
    sec = DOCUMENTATION[key]
    assert "17." in sec["title"]
    assert "114" in sec["content"]


def test_methodology_doc_exists():
    from pathlib import Path
    md = Path("src/bolt_analysis_studio/docs/METHODOLOGY.md").read_text(encoding="utf-8")
    for termo in ("Orçamento de erro", "gap_adocao", "lido-do-dado",
                  "falsificação", "piso", "error_budget"):
        assert termo in md, termo


def test_documentation_tab_has_methodology_section():
    from bolt_analysis_studio.gui.documentation_tab import DOCUMENTATION
    key = next((k for k in DOCUMENTATION if "methodology" in k.lower()
                or "metodolog" in k.lower()), None)
    assert key is not None and "18." in DOCUMENTATION[key]["title"]


def test_chrome_help_menu_opens_validation_docs(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    w = ChromeWindow()
    help_menu = next(a.menu() for a in w.menuBar().actions()
                     if a.text() == "Ajuda")
    labels = [a.text() for a in help_menu.actions()]
    assert any("Valida" in t for t in labels)       # entrada da biblioteca
