"""CollapsibleGroup — grupo colapsavel do Property Inspector (spec abaqus §6)."""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFormLayout, QToolButton, QVBoxLayout, QWidget


class CollapsibleGroup(QWidget):
    toggled = pyqtSignal(bool)  # True = colapsado

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self._collapsed = False
        self._title = title
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._header = QToolButton()
        self._header.setText(f"▼  {title}")   # triangulo para baixo
        self._header.setCheckable(True)
        self._header.setChecked(True)
        self._header.setStyleSheet(
            "QToolButton { border: none; text-align: left; font-weight: 600; }")
        self._header.clicked.connect(lambda _: self.set_collapsed(not self._collapsed))
        outer.addWidget(self._header)

        self._body = QWidget()
        self._form = QFormLayout(self._body)
        self._form.setContentsMargins(12, 2, 4, 6)
        self._form.setVerticalSpacing(3)
        outer.addWidget(self._body)

    def add_row(self, label: str, widget: QWidget, help_key: str = "") -> None:
        if help_key:
            widget.setProperty("help_key", help_key)
        self._form.addRow(label, widget)

    def row_count(self) -> int:
        return self._form.rowCount()

    def is_collapsed(self) -> bool:
        return self._collapsed

    def set_collapsed(self, collapsed: bool) -> None:
        collapsed = bool(collapsed)
        if collapsed == self._collapsed:
            return
        self._collapsed = collapsed
        self._body.setVisible(not collapsed)
        arrow = "▶" if collapsed else "▼"   # direita / baixo
        self._header.setText(f"{arrow}  {self._title}")
        self.toggled.emit(collapsed)
