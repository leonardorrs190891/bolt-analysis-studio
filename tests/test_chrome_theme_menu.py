"""Fase 1: chrome expõe menu de tema (paridade com a V1)."""


def test_chrome_has_view_theme_menu(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        view = next((m.menu() for m in win.menuBar().actions()
                     if m.text() == "Exibir"), None)
        assert view is not None, "menu Exibir ausente"
        theme_menu = next((a.menu() for a in view.actions()
                           if a.text() == "Tema"), None)
        assert theme_menu is not None, "submenu Tema ausente"
        labels = [a.text() for a in theme_menu.actions()]
        assert any("Engineering" in L for L in labels)
    finally:
        win.close()


def test_apply_theme_updates_current(qapp, monkeypatch):
    from bolt_analysis_studio.gui.theme import Theme
    # Protege a preferência real do usuário do side-effect de save.
    monkeypatch.setattr(Theme, "save_theme_preference", lambda *a, **k: None)
    win = ChromeWindow_or_none()
    if win is None:
        return
    try:
        win._apply_theme("engineering")
        assert Theme.current_name() == "engineering"
    finally:
        win.close()
        Theme.set_theme("dark")


def ChromeWindow_or_none():
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    return ChromeWindow()
