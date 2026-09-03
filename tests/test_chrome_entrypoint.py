def test_chrome_window_factory_importable(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    w = ChromeWindow()
    # sem "V2" desde 2026-09-02: e' a primeira versao publicada
    assert w.windowTitle().startswith("Bolt Analysis Studio")
    assert "V2" not in w.windowTitle()


def test_run_app_declares_v2_flag():
    # a flag --v2 existe no parser do launcher (sem instanciar a GUI)
    import ast
    src = open("run_app.py", encoding="utf-8").read()
    assert "--v2" in src
    ast.parse(src)   # launcher continua sintaticamente valido
