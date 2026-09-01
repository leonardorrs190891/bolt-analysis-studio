"""#8: readout de coordenadas do cursor sobre o schematic no prompt."""
import pytest
from PyQt6.QtCore import QEvent, QPointF, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QMessageBox


@pytest.fixture(autouse=True)
def _auto_confirm_close(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    yield


def test_cursor_readout_updates_coords(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        sv = win.model_controller.viewport_widget()
        ev = QMouseEvent(QEvent.Type.MouseMove, QPointF(50, 50), QPointF(50, 50),
                         Qt.MouseButton.NoButton, Qt.MouseButton.NoButton,
                         Qt.KeyboardModifier.NoModifier)
        win.eventFilter(sv.viewport(), ev)
        txt = win.prompt._coords.text()
        assert "x=" in txt and "y=" in txt
    finally:
        win.close()
