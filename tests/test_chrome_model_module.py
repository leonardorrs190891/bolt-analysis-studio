import pytest
from PyQt6.QtWidgets import QMessageBox

from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
from bolt_analysis_studio.gui.chrome.widgets.module_bar import MODULES
from bolt_analysis_studio.gui.msd_builder import SchematicView, PropertyInspector
from bolt_analysis_studio.gui.new_analysis_wizard import build_model, AnalysisSpec
from bolt_analysis_studio.core.app_state import get_app_state


@pytest.fixture(autouse=True)
def _auto_confirm_close(monkeypatch):
    # Analysis/Report constroem a BoltAnalysisStudio oculta (closeEvent modal).
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    yield


def test_model_module_shows_schematic_in_center(qapp):
    w = ChromeWindow()
    w.switch_module("Model")
    assert w._center.currentWidget() is w.model_controller.schematic
    assert isinstance(w._center.currentWidget(), SchematicView)


def test_model_module_swaps_inspector_to_rich(qapp):
    w = ChromeWindow()
    w.switch_module("Model")
    assert isinstance(w._inspector_dock.widget(), PropertyInspector)
    assert w._palette_dock.isVisibleTo(w)          # palette aparece no Model


def test_leaving_model_restores_chrome_inspector(qapp):
    w = ChromeWindow()
    w.switch_module("Model")
    w.switch_module("Report")      # Report agora e a ReportsTab real (Fase 4.3)
    assert w._center.currentWidget() is w.report_controller.viewport_widget()
    assert w._inspector_dock.widget() is w.inspector    # ChromeInspector de volta
    assert not w._palette_dock.isVisibleTo(w)


def test_appstate_model_loads_into_schematic(qapp):
    st = get_app_state(); st.new_project()
    w = ChromeWindow(app_state=st)
    st.model = build_model(AnalysisSpec())
    assert len(w.model_controller.schematic.elements) == 11   # via sync externo
    assert w.tree._element_count() == 11                       # tree tambem popula
    st.new_project()


def test_all_modules_still_switch(qapp):
    w = ChromeWindow()
    for m in MODULES:
        w.switch_module(m)
        assert w.current_module == m


def test_contacts_module_shows_schematic_and_contact_tab(qapp):
    w = ChromeWindow()
    w.switch_module("Contacts")
    assert w._center.currentWidget() is w.model_controller.schematic
    assert isinstance(w._inspector_dock.widget(), PropertyInspector)
    assert w.model_controller.inspector.inspector_tabs.currentIndex() == 2
    assert not w._palette_dock.isVisibleTo(w)      # paleta so no Model


def test_loads_module_shows_schematic_and_chrome_inspector(qapp):
    # #1: Loads passou ao inspector chrome-nativo (CollapsibleGroup), mantendo
    # o schematic no centro (Model/Contacts seguem no inspector rico).
    w = ChromeWindow()
    w.switch_module("Loads")
    assert w._center.currentWidget() is w.model_controller.schematic
    assert w._inspector_dock.widget() is w.inspector
    assert not w._palette_dock.isVisibleTo(w)


def test_model_module_selects_element_tab_and_palette(qapp):
    w = ChromeWindow()
    w.switch_module("Loads")
    w.switch_module("Model")
    assert w.model_controller.inspector.inspector_tabs.currentIndex() == 0
    assert w._palette_dock.isVisibleTo(w)


def test_leaving_schematic_family_switches_to_analysis(qapp):
    w = ChromeWindow()
    w.switch_module("Contacts")
    w.switch_module("Analysis")    # Analysis agora e a SolverTab real (Fase 4.1)
    assert w._center.currentWidget() is w.analysis_controller.viewport_widget()
    assert w._inspector_dock.widget() is w.inspector
    assert not w._palette_dock.isVisibleTo(w)
