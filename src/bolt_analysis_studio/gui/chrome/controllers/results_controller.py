"""ResultsController — módulo Results (Run) do chrome, embrulha a ResultsTab (V1).

Usa a MESMA janela V1 oculta (V1Host) do AnalysisController, de modo que um Run
disparado no módulo Analysis atualiza a ResultsTab aqui exibida (mesma instância,
mesmo app_state, atualizada por `_on_results_changed` da janela).
"""
from __future__ import annotations

from PyQt6.QtCore import QObject

from ....core.app_state import get_app_state
from .v1_host import V1Host


class ResultsController(QObject):
    def __init__(self, app_state=None, host=None, parent=None):
        super().__init__(parent)
        self.app_state = app_state or get_app_state()
        self._host = host or V1Host(self.app_state)

    def viewport_widget(self):
        return self._host.window.results_tab

    def refresh(self) -> None:
        # Re-plota a partir do app_state.results, se a ResultsTab expõe um hook.
        tab = self._host.window.results_tab
        for hook in ("refresh_plots", "_refresh", "update_results"):
            fn = getattr(tab, hook, None)
            if callable(fn):
                try:
                    fn()
                except Exception:
                    pass
                return
