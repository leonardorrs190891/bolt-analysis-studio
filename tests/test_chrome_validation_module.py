import pytest
from PyQt6.QtWidgets import QMessageBox, QTabWidget

from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
from bolt_analysis_studio.core.app_state import get_app_state


@pytest.fixture(autouse=True)
def _auto_confirm_close(monkeypatch):
    # Módulos Analysis/Results constroem a BoltAnalysisStudio oculta (closeEvent modal).
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    yield


def test_results_module_shows_validation_browser(qapp):
    # Fase 4: Results agora é um QTabWidget [Run | Validation]; o browser vive
    # dentro da aba Validation (antes era o widget central direto).
    w = ChromeWindow()
    w.switch_module("Results")
    cur = w._center.currentWidget()
    assert isinstance(cur, QTabWidget)
    widgets = [cur.widget(i) for i in range(cur.count())]
    assert w.validation_controller.browser in widgets
    assert not w._palette_dock.isVisibleTo(w)


def test_leaving_results_switches_central_widget(qapp):
    # Fase 4: sair de Results troca o widget central (Analysis vira SolverTab real,
    # não mais o placeholder MultiViewport).
    w = ChromeWindow()
    w.switch_module("Results")
    results_widget = w._center.currentWidget()
    w.switch_module("Model")
    assert w._center.currentWidget() is not results_widget
    assert w._center.currentWidget() is w.model_controller.viewport_widget()


def test_open_in_model_switches_module_and_loads(qapp):
    st = get_app_state(); st.new_project()
    w = ChromeWindow(app_state=st)
    w.switch_module("Results")
    w.validation_controller.open_in_model("liu2025_M16_amp0p25")
    assert w.current_module == "Model"
    assert len(w.model_controller.schematic.elements) > 0
    assert st.model._v2_geometry_overrides["L_eff"] > 0
    st.new_project()
