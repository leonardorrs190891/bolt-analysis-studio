from bolt_analysis_studio.gui.chrome.widgets.module_bar import ModuleBar, MODULES
from bolt_analysis_studio.gui.chrome.widgets.context_bar import ContextBar
from bolt_analysis_studio.gui.chrome.widgets.prompt_area import PromptArea


def test_modulebar_lists_six_modules(qapp):
    mb = ModuleBar()
    assert MODULES == ["Model", "Contacts", "Loads", "Analysis", "Results", "Report"]
    assert len(mb._btns) == 6                       # trilha de 6 passos numerados


def test_modulebar_module_change_emits(qapp):
    seen = []
    mb = ModuleBar()
    mb.module_changed.connect(seen.append)
    mb.set_module("Loads")
    assert seen == ["Loads"]


def test_modulebar_run_stop_signals(qapp):
    ran = []
    mb = ModuleBar()
    mb.run_requested.connect(lambda: ran.append("run"))
    mb._run_btn.click()
    assert ran == ["run"]


def test_contextbar_switches_button_set_per_module(qapp):
    cb = ContextBar()
    cb.set_module("Loads")
    loads_actions = cb._action_names()
    cb.set_module("Results")
    results_actions = cb._action_names()
    assert loads_actions != results_actions
    assert any("Load" in a for a in loads_actions)


def test_contextbar_action_emits(qapp):
    seen = []
    cb = ContextBar()
    cb.action_triggered.connect(seen.append)
    cb.set_module("Loads")
    cb._trigger_first()
    assert len(seen) == 1


def test_prompt_area_sets_text(qapp):
    p = PromptArea()
    p.set_prompt("Selecione um elemento")
    p.set_coords("N=412")
    assert "Selecione" in p._prompt.text()
    assert "412" in p._coords.text()
