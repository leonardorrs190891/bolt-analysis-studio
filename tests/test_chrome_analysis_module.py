"""Fase 4: módulo Analysis embrulha a SolverTab (V1) via janela oculta."""
import pytest
from PyQt6.QtWidgets import QMessageBox


@pytest.fixture(autouse=True)
def _auto_confirm_close(monkeypatch):
    # A BoltAnalysisStudio oculta tem closeEvent com QMessageBox modal.
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    yield


def test_analysis_controller_exposes_solver_widget(qapp):
    from bolt_analysis_studio.gui.chrome.controllers.analysis_controller import AnalysisController
    ac = AnalysisController()
    w = ac.viewport_widget()
    assert w is not None
    assert hasattr(ac, "run") and hasattr(ac, "stop")


def test_analysis_controller_relays_log(qapp):
    from bolt_analysis_studio.gui.chrome.controllers.analysis_controller import AnalysisController
    ac = AnalysisController()
    seen = []
    ac.log_message.connect(seen.append)
    ac._on_log("preflight ok")
    assert "preflight ok" in seen


def test_chrome_analysis_module_hosts_solver(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        win.switch_module("Analysis")
        assert win.analysis_controller.viewport_widget() is not None
        assert win.module_bar._run_btn.isEnabled()
    finally:
        win.close()
