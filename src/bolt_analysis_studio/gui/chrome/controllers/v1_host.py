"""V1Host — constrói (lazy) uma BoltAnalysisStudio oculta e expõe suas abas.

Mesmo padrão do ModelController (que embrulha um MSDBuilderWindow oculto): os
módulos Analysis/Results/Report do chrome re-hospedam as abas solver/results/
reports desta janela oculta, reusando TODA a orquestração de Run/resultados/
relatório da V1 sem duplicação. Construção adiada até o primeiro acesso — chrome
que fica no módulo Model nunca paga o custo (~2s).
"""
from __future__ import annotations

from ....core.app_state import get_app_state


class V1Host:
    def __init__(self, app_state=None):
        self.app_state = app_state or get_app_state()
        self._win = None

    @property
    def window(self):
        if self._win is None:
            from ...main_window import BoltAnalysisStudio
            self._win = BoltAnalysisStudio()
            self._win.hide()               # nunca exibida; só fonte das abas
        return self._win

    @property
    def built(self) -> bool:
        return self._win is not None
