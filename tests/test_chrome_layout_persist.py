"""#5: persistência de layout de docks (QSettings) — requer objectNames."""
import pytest
from PyQt6.QtCore import QByteArray
from PyQt6.QtWidgets import QDockWidget, QMessageBox, QToolBar


@pytest.fixture(autouse=True)
def _auto_confirm_close(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    yield


def test_docks_and_bars_have_objectnames(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        for d in win.findChildren(QDockWidget):
            assert d.objectName(), f"dock sem objectName: {d.windowTitle()!r}"
        named_bars = [b for b in win.findChildren(QToolBar) if b.windowTitle()]
        assert named_bars and all(b.objectName() for b in named_bars)
    finally:
        win.close()


def test_layout_save_restore_roundtrip(qapp, monkeypatch):
    # não polui as prefs reais do usuário
    store = {}
    from PyQt6.QtCore import QSettings
    monkeypatch.setattr(QSettings, "setValue",
                        lambda self, k, v: store.__setitem__(k, v))
    monkeypatch.setattr(QSettings, "value",
                        lambda self, k, d=None: store.get(k, d))
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        win._save_layout()
        assert "chrome/windowState" in store
        win._restore_layout()   # não crasha
        assert isinstance(win.saveState(), QByteArray)
    finally:
        win.close()
