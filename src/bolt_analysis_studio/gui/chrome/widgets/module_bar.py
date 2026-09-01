"""ModuleBar — passos de workflow numerados + Step/Run/Stop/badge (Abaqus §3.2).

Os módulos viram uma trilha horizontal de botões numerados (1 Model → 2 Contacts
→ … → 6 Report), com o passo atual destacado e um botão "Próximo →" que avança —
para o usuário nunca se perder sobre qual é o próximo passo. Preenche a faixa
superior (antes um dropdown curto deixava o topo-direito vazio).
"""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (QButtonGroup, QComboBox, QLabel, QPushButton,
                             QToolBar, QToolButton)

from ...icons import icon

MODULES = ["Model", "Contacts", "Loads", "Analysis", "Results", "Report"]


class ModuleBar(QToolBar):
    module_changed = pyqtSignal(str)
    step_changed = pyqtSignal(str)
    run_requested = pyqtSignal()
    stop_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Module", parent)
        self.setMovable(False)

        # Trilha de passos numerados (checkable, exclusivos).
        self._btns = {}
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        for i, m in enumerate(MODULES, 1):
            b = QToolButton()
            b.setObjectName("moduleStep")
            b.setText(f"{i}  {m}")
            b.setCheckable(True)
            b.setAutoRaise(True)
            b.clicked.connect(lambda _c=False, name=m: self.module_changed.emit(name))
            self._group.addButton(b)
            self._btns[m] = b
            self.addWidget(b)
        self._btns[MODULES[0]].setChecked(True)

        self._next_btn = QToolButton()
        self._next_btn.setObjectName("nextStep")
        self._next_btn.setText("Próximo →")
        self._next_btn.setToolTip("Avança para o próximo passo do fluxo")
        self._next_btn.clicked.connect(self._go_next)
        self.addWidget(self._next_btn)

        self.addSeparator()
        self.addWidget(QLabel("  Step: "))
        self._step_combo = QComboBox()
        self._step_combo.addItems(["Static-Preload", "Coupled-Loosening"])
        self._step_combo.currentTextChanged.connect(self.step_changed.emit)
        self.addWidget(self._step_combo)

        self.addSeparator()
        self._run_btn = QPushButton("Run")
        self._run_btn.setObjectName("runButton")
        self._run_btn.setIcon(icon("run", size=16))
        self._run_btn.clicked.connect(lambda: self.run_requested.emit())
        self.addWidget(self._run_btn)
        self._stop_btn = QPushButton("Stop")
        self._stop_btn.setIcon(icon("stop", size=16))
        self._stop_btn.clicked.connect(lambda: self.stop_requested.emit())
        self.addWidget(self._stop_btn)

        self.addSeparator()
        self._badge = QLabel("")
        self.addWidget(self._badge)

    # --- navegação de módulo ---
    def set_module(self, name: str) -> None:
        """Marca o módulo e EMITE module_changed (uso externo/teste)."""
        if name not in self._btns:
            return
        self.mark_module(name)
        self.module_changed.emit(name)

    def mark_module(self, name: str) -> None:
        """Marca o botão do módulo SEM emitir (sincroniza a UI com switch_module)."""
        b = self._btns.get(name)
        if b is not None and not b.isChecked():
            b.setChecked(True)     # grupo exclusivo desmarca os outros; sem clicked

    def current_module(self) -> str:
        for m, b in self._btns.items():
            if b.isChecked():
                return m
        return MODULES[0]

    def _go_next(self) -> None:
        cur = self.current_module()
        nxt = MODULES[min(MODULES.index(cur) + 1, len(MODULES) - 1)]
        if nxt != cur:
            self.mark_module(nxt)
            self.module_changed.emit(nxt)

    # --- badge / run ---
    def set_badge(self, text: str, kind: str = "info") -> None:
        names = {"pass": "badgePass", "warn": "badgeWarn",
                 "fail": "badgeFail", "info": "badgeInfo"}
        self._badge.setText(f"  {text}  " if text else "")
        self._badge.setObjectName(names.get(kind, "badgeInfo") if text else "")
        self._badge.style().unpolish(self._badge)
        self._badge.style().polish(self._badge)

    def rebuild_icons(self) -> None:
        self._run_btn.setIcon(icon("run", size=16))
        self._stop_btn.setIcon(icon("stop", size=16))

    def set_run_enabled(self, enabled: bool, reason: str = "") -> None:
        self._run_btn.setEnabled(enabled)
        self._stop_btn.setEnabled(enabled)
        self._run_btn.setToolTip(reason if not enabled else "Rodar a análise")
