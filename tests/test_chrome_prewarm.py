"""#10: pré-aquecimento da janela V1 oculta (remove o hitch do 1º Analysis)."""
import pytest
from PyQt6.QtWidgets import QMessageBox


@pytest.fixture(autouse=True)
def _auto_confirm_close(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    yield


def test_prewarm_builds_v1_host(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        assert win._v1_host.built is False     # lazy: ainda não construído
        win._prewarm_v1()
        assert win._v1_host.built is True       # construído após prewarm
    finally:
        win.close()
