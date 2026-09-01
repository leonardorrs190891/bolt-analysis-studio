"""Fase 3: Run/Stop desabilitados até a Fase 4; prompt de contexto instrucional."""


def test_run_disabled_with_reason(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.module_bar import ModuleBar
    bar = ModuleBar()
    bar.set_run_enabled(False, "Analysis chega na Fase 4")
    assert not bar._run_btn.isEnabled()
    assert "Fase 4" in bar._run_btn.toolTip()


def test_context_action_sets_instructional_prompt(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        win.switch_module("Contacts")
        win._on_context_action("+ Thread")
        txt = win.prompt._prompt.text()
        assert txt != "Acao: + Thread"     # instrução, não eco
        assert len(txt) > 12
    finally:
        win.close()


def test_model_view_enables_stamp(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        win.switch_module("Model")
        sv = win.model_controller.viewport_widget()
        assert sv._stamp_enabled is True
    finally:
        win.close()
