"""Fase 6: estados vazios orientam a próxima ação."""


def test_empty_model_prompts_wizard(qapp):
    from bolt_analysis_studio.core.app_state import get_app_state
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    st = get_app_state()
    st._model = None
    win = ChromeWindow(app_state=st)
    try:
        win.refresh_empty_state()
        assert "Ctrl+Shift+N" in win.prompt._prompt.text()
    finally:
        win.close()
