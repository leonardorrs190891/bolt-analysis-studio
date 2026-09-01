"""AnalysisController — módulo Analysis do chrome (embrulha a SolverTab da V1).

Re-hospeda a `solver_tab` de uma BoltAnalysisStudio oculta (V1Host) e dirige o
Run/Stop clicando nos botões dela (que a janela conecta a `_run_analysis`/
`_stop_analysis`). Relança log/progresso do SolverWorker como sinais que o chrome
liga à message area. Não reimplementa o solver.
"""
from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

from ....core.app_state import get_app_state
from .v1_host import V1Host


class AnalysisController(QObject):
    log_message = pyqtSignal(str)
    progress = pyqtSignal(int, str)
    job_state = pyqtSignal(str)          # running | done | error | idle

    def __init__(self, app_state=None, host=None, parent=None):
        super().__init__(parent)
        self.app_state = app_state or get_app_state()
        self._host = host or V1Host(self.app_state)

    def viewport_widget(self):
        return self._host.window.solver_tab

    def run(self) -> None:
        win = self._host.window
        self.job_state.emit("running")
        win.solver_tab.run_btn.click()             # dispara _run_analysis (cria worker+thread)
        worker = getattr(win, "solver_worker", None)
        if worker is not None:
            # Worker é recriado a cada run; conectar o fresh a cada vez é seguro.
            try:
                worker.log.connect(self._on_log)
                worker.progress.connect(self._on_progress)
                worker.finished.connect(lambda _r: self.job_state.emit("done"))
                worker.error.connect(lambda _e: self.job_state.emit("error"))
            except (TypeError, RuntimeError):
                pass

    def stop(self) -> None:
        win = self._host.window
        win.solver_tab.stop_btn.click()            # dispara _stop_analysis
        self.job_state.emit("idle")

    def _on_log(self, text: str) -> None:
        self.log_message.emit(text)

    def _on_progress(self, pct: int, msg: str) -> None:
        self.progress.emit(pct, msg)
