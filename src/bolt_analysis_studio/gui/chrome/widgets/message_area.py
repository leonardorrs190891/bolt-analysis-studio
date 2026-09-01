"""MessageArea — área de mensagens/log do chrome (paridade Abaqus §3).

Cabeçalho com botão de colapso (▼/▶) que encolhe a área para uma faixa fina —
hide/unhide direto, sem caçar no menu. Abas Messages / Job Log; fonte reduzida
para ocupar menos espaço. Recebe também os avisos de contexto ("Modelo criado…").
"""
from __future__ import annotations

from PyQt6.QtWidgets import (QHBoxLayout, QPlainTextEdit, QTabWidget, QToolButton,
                             QVBoxLayout, QWidget)

_CHANNELS = [("messages", "Messages"), ("job", "Job Log")]
_MAX = 16777215   # QWIDGETSIZE_MAX


class MessageArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._collapsed = False
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        hdr = QHBoxLayout()
        hdr.setContentsMargins(6, 2, 6, 2)
        self._toggle = QToolButton()
        self._toggle.setObjectName("msgCollapse")
        self._toggle.setText("▼  Mensagens")
        self._toggle.setToolTip("Colapsar/expandir a área de mensagens")
        self._toggle.clicked.connect(self.toggle_collapsed)
        hdr.addWidget(self._toggle)
        hdr.addStretch(1)
        lay.addLayout(hdr)

        self._tabs = QTabWidget()
        self._views = {}
        for key, label in _CHANNELS:
            view = QPlainTextEdit()
            view.setReadOnly(True)
            view.setMaximumBlockCount(5000)
            f = view.font()
            f.setPointSize(8)                 # fonte menor → ocupa menos espaço
            view.setFont(f)
            self._views[key] = view
            self._tabs.addTab(view, label)
        lay.addWidget(self._tabs)

    def toggle_collapsed(self) -> None:
        self._collapsed = not self._collapsed
        self._tabs.setVisible(not self._collapsed)
        self._toggle.setText("▶  Mensagens" if self._collapsed else "▼  Mensagens")
        # Encolhe/expande o dock: com maximumHeight na altura do header, colapsa.
        self.setMaximumHeight(self._toggle.sizeHint().height() + 10
                              if self._collapsed else _MAX)

    def is_collapsed(self) -> bool:
        return self._collapsed

    def append(self, text: str, channel: str = "messages") -> None:
        view = self._views.get(channel)
        if view is not None:
            view.appendPlainText(text)

    def clear_channel(self, channel: str) -> None:
        view = self._views.get(channel)
        if view is not None:
            view.clear()
