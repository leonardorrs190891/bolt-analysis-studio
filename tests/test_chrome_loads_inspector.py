"""#1 (parcial): inspector chrome-nativo (CollapsibleGroup) para o módulo Loads.

Model/Contacts seguem no inspector rico (feature-complete); Loads passa ao
paradigma unificado do chrome com edição in-place dos campos de carregamento.
"""
import pytest
from PyQt6.QtWidgets import QMessageBox


@pytest.fixture(autouse=True)
def _auto_confirm_close(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    yield


def test_loads_uses_chrome_inspector(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    from bolt_analysis_studio.gui.new_analysis_wizard import build_model, AnalysisSpec
    win = ChromeWindow()
    try:
        win.app_state.model = build_model(AnalysisSpec())
        win.switch_module("Loads")
        assert win._center.currentWidget() is win.model_controller.schematic
        assert win._inspector_dock.widget() is win.inspector   # chrome, não a rica
        assert win._loads_widgets, "sem widgets de carregamento"
    finally:
        win.close()


def test_loads_inspector_edit_writes_back(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    from bolt_analysis_studio.gui.new_analysis_wizard import build_model, AnalysisSpec
    win = ChromeWindow()
    try:
        m = build_model(AnalysisSpec())
        win.app_state.model = m
        win.switch_module("Loads")
        sp = win._loads_widgets.get("F_preload")
        assert sp is not None
        sp.setValue(88888.0)
        assert float(m.global_loading.F_preload) == pytest.approx(88888.0)
    finally:
        win.close()
