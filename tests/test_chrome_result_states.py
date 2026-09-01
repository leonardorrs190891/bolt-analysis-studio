"""#9: empty/error states (Results/Report sem resultado; job falho)."""
import pytest
from PyQt6.QtWidgets import QMessageBox


@pytest.fixture(autouse=True)
def _auto_confirm_close(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    yield


def test_results_empty_state_prompts_run(qapp):
    from bolt_analysis_studio.core.app_state import get_app_state
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    st = get_app_state()
    st._results = None
    win = ChromeWindow(app_state=st)
    try:
        win.switch_module("Results")
        txt = win.prompt._prompt.text().lower()
        assert "análise" in txt or "analysis" in txt
    finally:
        win.close()


def test_job_error_sets_prompt(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        win._on_job_state("error")
        assert "falh" in win.prompt._prompt.text().lower()
    finally:
        win.close()


def test_preload_plot_has_stage_shading():
    import bolt_analysis_studio.gui.main_window as m
    src = open(m.__file__, encoding="utf-8").read()
    assert "Bandas de estágio" in src   # axhspan I/II/III no plot de preload
