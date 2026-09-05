"""MessageArea — área de mensagens/log do chrome (paridade Abaqus §3).

Cabeçalho com botão de colapso (▼/▶) que encolhe a área para uma faixa fina —
hide/unhide direto, sem caçar no menu. Abas Messages / Job Log; fonte reduzida
para ocupar menos espaço. Recebe também os avisos de contexto ("Modelo criado…").
"""
from __future__ import annotations

from PyQt6.QtWidgets import (QHBoxLayout, QPlainTextEdit, QTabWidget, QToolButton,
                             QVBoxLayout, QWidget)

_CHANNELS = [("messages", "Mensagens", "Messages"),
             ("job", "Log do job", "Job Log")]
_MAX = 16777215   # QWIDGETSIZE_MAX


class MessageArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._collapsed = False
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        from ...i18n import Lang, TrGroup
        self._tr = TrGroup()
        hdr = QHBoxLayout()
        hdr.setContentsMargins(6, 2, 6, 2)
        self._toggle = QToolButton()
        self._toggle.setObjectName("msgCollapse")
        # O texto do botao depende do estado (▼/▶) E do idioma: um setter que
        # recompoe os dois, registrado no grupo para retraduzir ao vivo.
        self._tr.add(lambda _s: self._refresh_toggle(), "", "")
        self._tr.add(self._toggle.setToolTip,
                     "Colapsar/expandir a área de mensagens",
                     "Collapse/expand the message area")
        self._toggle.clicked.connect(self.toggle_collapsed)
        hdr.addWidget(self._toggle)
        hdr.addStretch(1)
        lay.addLayout(hdr)

        self._tabs = QTabWidget()
        self._views = {}
        for idx, (key, pt, en) in enumerate(_CHANNELS):
            view = QPlainTextEdit()
            view.setReadOnly(True)
            view.setMaximumBlockCount(5000)
            f = view.font()
            f.setPointSize(8)                 # fonte menor → ocupa menos espaço
            view.setFont(f)
            self._views[key] = view
            self._tabs.addTab(view, Lang.tr(pt, en))
            self._tr.add(lambda s, i=idx: self._tabs.setTabText(i, s), pt, en)
        lay.addWidget(self._tabs)

    def _refresh_toggle(self) -> None:
        from ...i18n import Lang
        seta = "▶" if self._collapsed else "▼"
        self._toggle.setText(f"{seta}  " + Lang.tr("Mensagens", "Messages"))

    def toggle_collapsed(self) -> None:
        self._collapsed = not self._collapsed
        self._tabs.setVisible(not self._collapsed)
        self._refresh_toggle()
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
