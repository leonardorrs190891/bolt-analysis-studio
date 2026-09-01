"""DockTitleBar — barra de título de dock lateral com dois controles:
colapsar (▾/▸, encolhe a largura a uma faixa fina) e fechar (✕, esconde o dock;
reabre em Exibir > Painéis). Espelha o padrão do cabeçalho da área de mensagens."""
from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QToolButton, QWidget

_MAX = 16777215   # QWIDGETSIZE_MAX


class DockTitleBar(QWidget):
    def __init__(self, dock, title, parent=None):
        super().__init__(parent)
        self.setObjectName("dockTitle")
        self._dock = dock
        self._collapsed = False

        h = QHBoxLayout(self)
        h.setContentsMargins(6, 2, 4, 2)
        h.setSpacing(2)

        self._collapse = QToolButton()
        self._collapse.setObjectName("dockCollapse")
        self._collapse.setText("▾")
        self._collapse.setToolTip("Colapsar/expandir o painel")
        self._collapse.clicked.connect(self.toggle_collapsed)

        self._label = QLabel(title)
        self._label.setObjectName("dockTitleLabel")

        self._close = QToolButton()
        self._close.setObjectName("dockClose")
        self._close.setText("✕")
        self._close.setToolTip("Fechar o painel (reabra em Exibir > Painéis)")
        self._close.clicked.connect(dock.close)

        h.addWidget(self._collapse)
        h.addWidget(self._label)
        h.addStretch(1)
        h.addWidget(self._close)

    def toggle_collapsed(self) -> None:
        self._collapsed = not self._collapsed
        self._apply()

    def _apply(self) -> None:
        # Colapsado: esconde o CONTEÚDO (nada de sliver recortado) e o dock vira
        # uma faixa fina só com o botão ▸; expandido: reexibe e libera a largura.
        w = self._dock.widget()
        if w is not None:
            w.setVisible(not self._collapsed)
        self._label.setVisible(not self._collapsed)
        self._close.setVisible(not self._collapsed)
        self._collapse.setText("▸" if self._collapsed else "▾")
        self._dock.setMaximumWidth(24 if self._collapsed else _MAX)

    def reapply(self) -> None:
        """Reaplica o estado (o dock trocou de widget e o novo veio visível)."""
        self._apply()

    def is_collapsed(self) -> bool:
        return self._collapsed
