"""Fase 4: módulo Report embrulha a ReportsTab (não é mais placeholder)."""
import pytest
from PyQt6.QtWidgets import QLabel, QMessageBox


@pytest.fixture(autouse=True)
def _auto_confirm_close(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    yield


def test_report_controller_wraps_reports_tab(qapp):
    from bolt_analysis_studio.gui.chrome.controllers.report_controller import ReportController
    rc = ReportController()
    assert rc.viewport_widget() is not None


def test_chrome_report_not_placeholder(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        win.switch_module("Report")
        w = win._center.currentWidget()
        assert not (isinstance(w, QLabel) and "viewport" in w.text())
        assert win._center.currentWidget() is win.report_controller.viewport_widget()
    finally:
        win.close()
