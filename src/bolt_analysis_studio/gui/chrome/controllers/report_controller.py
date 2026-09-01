"""ReportController — módulo Report do chrome, embrulha a ReportsTab (V1).

Re-hospeda a `reports_tab` da MESMA janela V1 oculta (V1Host) usada por
Analysis/Results, de modo que o relatório enxerga os mesmos resultados de Run.
"""
from __future__ import annotations

from PyQt6.QtCore import QObject

from ....core.app_state import get_app_state
from .v1_host import V1Host


class ReportController(QObject):
    def __init__(self, app_state=None, host=None, parent=None):
        super().__init__(parent)
        self.app_state = app_state or get_app_state()
        self._host = host or V1Host(self.app_state)

    def viewport_widget(self):
        return self._host.window.reports_tab
