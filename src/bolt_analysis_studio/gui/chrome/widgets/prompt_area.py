"""PromptArea — instruções contextuais. Emite `prompted` para que o chrome as
encaminhe à área de mensagens (em vez de uma faixa separada)."""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget


class PromptArea(QWidget):
    prompted = pyqtSignal(str)     # texto de instrução → área de mensagens

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("promptArea")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 3, 8, 3)
        self._prompt = QLabel("Pronto.")
        self._coords = QLabel("")
        lay.addWidget(self._prompt)
        lay.addStretch(1)
        lay.addWidget(self._coords)

    def set_prompt(self, text: str) -> None:
        self._prompt.setText(text)
        self.prompted.emit(text)

    def set_coords(self, text: str) -> None:
        self._coords.setText(text)
