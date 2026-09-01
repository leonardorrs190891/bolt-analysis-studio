from types import SimpleNamespace

from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
from bolt_analysis_studio.gui.chrome.widgets.module_bar import MODULES


def test_boots_with_three_zones(qapp):
    w = ChromeWindow()
    assert w.tree is not None
    assert w.inspector is not None
    assert w.viewport is not None
    assert w.current_module == "Model"          # default


def test_switch_module_updates_context_and_tree(qapp):
    w = ChromeWindow()
    w.switch_module("Loads")
    assert w.current_module == "Loads"
    assert any("Load" in a for a in w.context_bar._action_names())


def test_module_bar_drives_switch(qapp):
    w = ChromeWindow()
    w.module_bar.set_module("Results")
    assert w.current_module == "Results"


def test_all_modules_switch_without_error(qapp):
    w = ChromeWindow()
    for m in MODULES:
        w.switch_module(m)
        assert w.current_module == m


def test_appstate_model_populates_tree(qapp):
    from bolt_analysis_studio.core.app_state import get_app_state
    st = get_app_state()
    st.new_project()                              # isola o singleton (model=None)
    w = ChromeWindow(app_state=st)
    st.model = SimpleNamespace(elements=[SimpleNamespace(element_type="HEAD", id=1)])
    assert w.tree._element_count() == 1           # via sinal model_changed
    st.new_project()                              # cleanup
