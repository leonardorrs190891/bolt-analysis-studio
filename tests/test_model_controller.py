from bolt_analysis_studio.gui.chrome.controllers.model_controller import ModelController
from bolt_analysis_studio.gui.new_analysis_wizard import build_model, AnalysisSpec
from bolt_analysis_studio.core.app_state import get_app_state


def _model():
    return build_model(AnalysisSpec())


def test_controller_exposes_wired_parts(qapp):
    c = ModelController()
    from bolt_analysis_studio.gui.msd_builder import SchematicView, ElementPalette, PropertyInspector
    assert isinstance(c.schematic, SchematicView)
    assert isinstance(c.palette, ElementPalette)
    assert isinstance(c.inspector, PropertyInspector)
    assert c.undo_stack is not None
    assert c.schematic.undo_stack is c.undo_stack           # injetado pela janela
    assert c.viewport_widget() is c.schematic


def test_load_and_export_round_trip(qapp):
    c = ModelController()
    c.load_model(_model())
    assert len(c.schematic.elements) == 11
    exported = c.export_model()
    assert exported is not None and len(exported.elements) == 11


def test_load_none_is_noop(qapp):
    c = ModelController()
    c.load_model(None)                                       # nao levanta
    assert len(c.schematic.elements) == 0


def test_schematic_change_syncs_to_appstate_no_loop(qapp):
    st = get_app_state(); st.new_project()
    c = ModelController(st)
    c.load_model(_model())
    st._model = None                                         # limpa p/ detectar o sync
    c._on_schematic_changed()                                # simula edicao estrutural
    assert st.model is not None and len(st.model.elements) == 11
    assert c._syncing is False                               # flag restaurada (finally)
    st.new_project()


def test_load_does_not_reentrantly_sync(qapp):
    # carregar um modelo NAO deve disparar _on_schematic_changed -> app_state
    st = get_app_state(); st.new_project()
    c = ModelController(st)
    st._model = None
    c.load_model(_model())                                   # durante load, _syncing=True
    assert st.model is None                                  # load nao re-empurrou p/ app_state
    st.new_project()


def test_show_inspector_tab_selects_index(qapp):
    c = ModelController()
    c.show_inspector_tab("contact")
    assert c.inspector.inspector_tabs.currentIndex() == 2
    c.show_inspector_tab("loading")
    assert c.inspector.inspector_tabs.currentIndex() == 1
    c.show_inspector_tab("element")
    assert c.inspector.inspector_tabs.currentIndex() == 0
    c.show_inspector_tab("nope")                             # desconhecido = no-op
    assert c.inspector.inspector_tabs.currentIndex() == 0


def test_loading_edit_pushes_to_appstate(qapp):
    # Simula a edicao do usuario na aba Loading: set_loading_data (bulk, nao
    # emite) + emissao manual de loading_changed (o que qualquer widget faz).
    st = get_app_state(); st.new_project()
    c = ModelController(st)
    c.load_model(_model())
    st._model = None                                         # p/ detectar o push
    c.inspector.set_loading_data({"F_preload": 77777.0})
    c.inspector.loading_changed.emit(c.inspector.get_loading_data())
    assert st.model is not None
    assert abs(st.model.global_loading.F_preload - 77777.0) < 1e-6
    assert c._syncing is False                               # flag restaurada
    st.new_project()


def test_builder_changed_ignores_non_loading_sources(qapp):
    st = get_app_state(); st.new_project()
    c = ModelController(st)
    c.load_model(_model())
    st._model = None
    c._on_builder_changed({"source": "outra_coisa"})
    assert st.model is None                                  # nao empurrou
    st.new_project()
