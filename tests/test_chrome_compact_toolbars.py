"""#4: toolbars compactas (ícones menores, viewport toolbar na faixa do contexto)."""
import pytest
from PyQt6.QtWidgets import QMessageBox


@pytest.fixture(autouse=True)
def _auto_confirm_close(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    yield


def test_toolbars_have_compact_icon_size(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        for bar in (win.module_bar, win.context_bar, win.viewport_toolbar):
            assert bar.iconSize().width() <= 16, f"{bar.objectName()} não compacto"
    finally:
        win.close()
