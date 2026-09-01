"""#11: chrome unificado em português (menus PT; módulo/step em inglês = Abaqus)."""
import pytest
from PyQt6.QtWidgets import QMessageBox


@pytest.fixture(autouse=True)
def _auto_confirm_close(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    yield


def test_menu_bar_is_portuguese(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        labels = [a.text() for a in win.menuBar().actions()]
        assert "Arquivo" in labels and "Ajuda" in labels and "Exibir" in labels
        assert "File" not in labels and "Help" not in labels and "View" not in labels
    finally:
        win.close()


def test_wizard_action_has_ptbr_accent(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        file_menu = next(m.menu() for m in win.menuBar().actions()
                         if m.text() == "Arquivo")
        labels = [a.text() for a in file_menu.actions() if a.text()]
        assert any("Análise" in L for L in labels)
    finally:
        win.close()


def test_prompts_nonempty(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import _PROMPTS
    assert all(_PROMPTS.values())


def test_splash_rebranded_v2():
    import bolt_analysis_studio.gui.splash as m
    src = open(m.__file__, encoding="utf-8").read()
    assert "v4.0" not in src
