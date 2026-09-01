"""ContextBar — botoes que mudam por modulo ativo (spec abaqus §3.3)."""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QToolBar

from ...icons import icon

# Conjunto de acoes por modulo (rotulo do botao).
_ACTIONS = {
    "Model":    ["+ Element", "+ Material", "Assembly", "Locking Device"],
    "Contacts": ["+ Thread", "+ Bearing", "+ Flange", "Friction/Wear"],
    "Loads":    ["+ Global Load", "+ Per-Element", "+ Thermal", "+ Locking"],
    "Analysis": ["+ Static-Preload", "+ Coupled-Loosening", "Solver", "Jobs"],
    "Results":  ["Preload", "Friction", "Phase", "Miner", "Layout", "Overlay", "Export"],
    "Report":   ["Template", "Sections", "Format", "Preview"],
}

# Ícone por rótulo de ação (nomes do set em resources/icons/).
_ICON_FOR = {
    "+ Element": "element", "+ Material": "new", "Assembly": "element",
    "+ Thread": "contact", "+ Bearing": "contact", "+ Flange": "element",
    "Friction/Wear": "settings",
    "+ Global Load": "load", "+ Per-Element": "load", "+ Thermal": "load",
    "+ Locking": "load",
    "+ Static-Preload": "step", "+ Coupled-Loosening": "step",
    "Solver": "settings", "Jobs": "job",
    "Preload": "validation", "Friction": "validation", "Phase": "validation",
    "Miner": "validation", "Export": "save",
    "Template": "report", "Sections": "report", "Format": "settings",
    "Preview": "validation",
}


class ContextBar(QToolBar):
    action_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__("Context", parent)
        self.setMovable(False)
        self._module = None
        self._actions = []

    def set_module(self, name: str) -> None:
        self.clear()
        self._actions = []
        for label in _ACTIONS.get(name, []):
            act = QAction(label, self)
            ic = _ICON_FOR.get(label)
            if ic:
                act.setIcon(icon(ic, size=16))
            act.triggered.connect(lambda _c, L=label: self.action_triggered.emit(L))
            self.addAction(act)
            self._actions.append(act)
        self._module = name

    def _action_names(self):
        return [a.text() for a in self._actions]

    def _trigger_first(self):
        if self._actions:
            self._actions[0].trigger()
