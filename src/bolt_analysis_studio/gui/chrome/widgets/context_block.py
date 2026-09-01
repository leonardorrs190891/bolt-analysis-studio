"""ContextBlock — faixa 'Module · Model · Step' abaixo do ModuleBar (Abaqus §3)."""
from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget


class ContextBlock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 2, 8, 2)
        self._label = QLabel("Module: — · Model: — · Step: —")
        lay.addWidget(self._label)
        lay.addStretch(1)

    def set_context(self, module: str, model: str, step: str) -> None:
        self._label.setText(
            f"Module: {module or '—'} · Model: {model or '—'} · Step: {step or '—'}")
