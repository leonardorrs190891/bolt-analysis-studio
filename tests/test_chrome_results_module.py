"""Fase 4: Results tem sub-modo Run (ResultsTab) + Validation (browser)."""
import pytest
from PyQt6.QtWidgets import QMessageBox, QTabWidget


@pytest.fixture(autouse=True)
def _auto_confirm_close(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    yield


def test_results_controller_wraps_results_tab(qapp):
    from bolt_analysis_studio.gui.chrome.controllers.results_controller import ResultsController
    rc = ResultsController()
    assert rc.viewport_widget() is not None
    assert hasattr(rc, "refresh")


def test_chrome_results_has_run_and_validation_submodes(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        win.switch_module("Results")
        w = win._center.currentWidget()
        tabs = w if isinstance(w, QTabWidget) else w.findChild(QTabWidget)
        labels = [tabs.tabText(i) for i in range(tabs.count())]
        assert "Run" in labels and "Validation" in labels
    finally:
        win.close()
