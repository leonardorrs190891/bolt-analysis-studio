"""MultiViewport — layouts fixos 1 / 1x2 / 2x1 / 2x2 (spec abaqus §5)."""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

_LAYOUTS = {
    "1":   [(0, 0, 1, 1)],
    "1x2": [(0, 0, 1, 1), (0, 1, 1, 1)],
    "2x1": [(0, 0, 1, 1), (1, 0, 1, 1)],
    "2x2": [(0, 0, 1, 1), (0, 1, 1, 1), (1, 0, 1, 1), (1, 1, 1, 1)],
}


class _Slot(QFrame):
    def __init__(self, index, on_focus):
        super().__init__()
        self.setObjectName("viewportSlot")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._index = index
        self._on_focus = on_focus
        lay = QVBoxLayout(self)
        lay.setContentsMargins(1, 1, 1, 1)
        self._content = QLabel(f"[ viewport {index + 1} ]")
        self._content.setMinimumSize(80, 60)
        lay.addWidget(self._content)

    def mousePressEvent(self, ev):
        self._on_focus(self._index)
        super().mousePressEvent(ev)

    def set_content(self, w):
        lay = self.layout()
        old = lay.takeAt(0)
        if old is not None and old.widget() is not None:
            old.widget().deleteLater()
        self._content = w
        lay.addWidget(w)

    def set_active(self, active):
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)


class MultiViewport(QWidget):
    active_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(2)
        self._slots = []
        self._active = 0
        self._layout_name = "1"
        self.set_layout("1")

    def layout_name(self) -> str:
        return self._layout_name

    def slot_count(self) -> int:
        return len(self._slots)

    @property
    def active_index(self) -> int:
        return self._active

    def set_layout(self, name: str) -> None:
        if name not in _LAYOUTS:
            raise ValueError(f"layout desconhecido: {name!r}")
        for s in self._slots:
            self._grid.removeWidget(s)
            s.deleteLater()
        self._slots = []
        for i, (r, c, rs, cs) in enumerate(_LAYOUTS[name]):
            slot = _Slot(i, self.set_active)
            self._grid.addWidget(slot, r, c, rs, cs)
            self._slots.append(slot)
        self._layout_name = name
        self._active = 0
        self._refresh_active()

    def set_widget(self, index: int, w: QWidget) -> None:
        if 0 <= index < len(self._slots):
            self._slots[index].set_content(w)

    def set_active(self, index: int) -> None:
        if 0 <= index < len(self._slots) and index != self._active:
            self._active = index
            self._refresh_active()
            self.active_changed.emit(index)

    def _refresh_active(self) -> None:
        for i, s in enumerate(self._slots):
            s.set_active(i == self._active)
