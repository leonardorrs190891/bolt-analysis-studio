# -*- coding: utf-8 -*-
"""ValidationController — orquestra o modulo Validation do chrome V2 (Plano B):
browser <-> store/runner/reports, re-simulacao em QThread, e "Abrir no
Model/Run" (requisito do professor: casos rodaveis livremente no software)."""
from __future__ import annotations

import webbrowser

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from ....core.app_state import get_app_state
from ....validation.case_registry import record
from ....validation.gui_bridge import build_case_model
from ....validation.report import ensure_reports
from ....validation.report_html import write_reports
from ....validation.runner import simulate_case
from ....validation.store import ValidationStore
from ..widgets.validation_browser import ValidationBrowser


class _ResimWorker(QThread):
    case_done = pyqtSignal(str)
    all_done = pyqtSignal()

    def __init__(self, case_ids, store, n_cap=None, parent=None):
        super().__init__(parent)
        self._ids = list(case_ids)
        self._store = store
        self._n_cap = n_cap

    def run(self):
        for cid in self._ids:
            rec = record(cid)
            if rec is None:
                continue
            self._store.put(simulate_case(rec, n_cap=self._n_cap))
            self._store.save()
            self.case_done.emit(cid)
        self.all_done.emit()


class ValidationController(QObject):
    case_opened_in_model = pyqtSignal(str)
    import_failed = pyqtSignal(str)

    def __init__(self, app_state=None, parent=None, store=None):
        """`store` existe para poder ser INJETADO (mesma costura que
        `ValidationBrowser` já tinha). Sem ele o controller abre o store
        CANÔNICO — que é o desenho em produção (o store é o cache do app), mas
        significa que `import_case()` escreve no arquivo versionado do repo.
        Em teste isso vazava: `test_validation_browser` gravava
        `ensaio_teste_m12` no store canônico, e o vazamento era INVISÍVEL
        quando o caso importado era real (o registro sai byte-idêntico).
        Medido em 2026-07-28; quem constrói em teste deve passar `store`."""
        super().__init__(parent)
        self.app_state = app_state or get_app_state()
        self.store = store or ValidationStore()
        if not self.store.all_ids():
            self.store.seed_from_gallery()
            self.store.save()
        self.browser = ValidationBrowser(store=self.store)
        self._worker = None
        b = self.browser
        b.open_in_model_requested.connect(self.open_in_model)
        b.resim_case_requested.connect(lambda cid: self.resimulate([cid]))
        b.resim_all_requested.connect(self._resim_all)
        b.open_report_requested.connect(self._open_case_report)
        b.save_msd_requested.connect(self._save_msd_dialog)
        b.master_report_requested.connect(self._open_master)
        b.import_case_requested.connect(self._import_dialog)
        b.copy_prompt_requested.connect(self.copy_prompt)
        b.save_prompt_requested.connect(self._save_prompt_dialog)

    def viewport_widget(self):
        return self.browser

    # --- acoes ---
    def open_in_model(self, case_id: str) -> None:
        rec = record(case_id)
        if rec is None:
            return
        try:
            self.app_state.model = build_case_model(rec)
        except ValueError:
            return                                # familia 'other': sem proveniencia
        self.case_opened_in_model.emit(case_id)

    def resimulate(self, case_ids, n_cap=None) -> None:
        if self._worker is not None and self._worker.isRunning():
            return
        self._worker = _ResimWorker(case_ids, self.store, n_cap=n_cap)
        self._worker.case_done.connect(self.browser.refresh_case)
        self._worker.start()

    def _resim_all(self) -> None:
        from ....validation.case_registry import all_records
        self.resimulate([r.case_id for r in all_records() if r.family != "other"])

    def _open_case_report(self, case_id: str) -> None:
        master = write_reports()                  # regenera do store (rapido)
        target = master.parent / "reports" / f"{case_id}.html"
        if target.exists():
            webbrowser.open(target.as_uri())

    def _save_msd_dialog(self, case_id: str) -> None:
        """Salva o caso como .msd com a configuracao adotada E a citacao.

        Os 210 ja' vem prontos em Models/SAVED_CASES; este botao existe
        para quem quer o arquivo em outro lugar, ou depois de editar. A
        citacao sai de validation.provenance, a mesma que o gerador em
        lote usa: o arquivo carrega curva digitalizada de publicacao de
        terceiro e nao pode sair sem dizer de onde veio.
        """
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from ....validation.case_registry import record
        from ....validation.provenance import citation_block

        rec = record(case_id)
        if rec is None:
            return
        caminho, _ = QFileDialog.getSaveFileName(
            self.browser, "Salvar caso como .msd",
            f"{case_id}.msd", "Modelo MSD (*.msd);;Todos os arquivos (*)")
        if not caminho:
            return
        try:
            model = build_case_model(rec)
            model.name = rec.name or case_id
            model.description = citation_block(rec)
            model.save(caminho)
        except Exception as exc:                          # noqa: BLE001
            QMessageBox.warning(self.browser, "Salvar caso",
                                f"Nao foi possivel salvar:\n{exc}")
            return
        self.browser.set_intake_status(f"Caso salvo em {caminho}")

    def _open_master(self) -> None:
        webbrowser.open(ensure_reports().as_uri())

    # --- intake de casos do usuario (prompt de IA + .bascase.json) ---
    def import_case(self, path, prefit: bool = True):
        from ....validation.case_registry import refresh_records
        from ....validation.prefit import prefit_user_case
        from ....validation.user_cases import import_user_case
        try:
            rec = import_user_case(path)
        except (ValueError, OSError) as exc:
            self.import_failed.emit(str(exc))
            return None
        if prefit:
            try:
                prefit_user_case(rec)
            except Exception as exc:              # prefit degrada, import fica
                self.import_failed.emit(f"prefit degradado: {exc}")
        refresh_records()
        self.store.put(simulate_case(rec))
        self.store.save()
        self.browser.refresh_case(rec.case_id)
        return rec.case_id

    def copy_prompt(self) -> None:
        from PyQt6.QtWidgets import QApplication
        from ....validation.intake_prompt import INTAKE_PROMPT
        QApplication.clipboard().setText(INTAKE_PROMPT)
        self.browser.set_intake_status(
            "✓ Prompt copiado — cole em qualquer IA junto com sua curva.")

    def _import_dialog(self) -> None:
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self.browser, "Importar caso do usuário", "",
            "Caso BAS (*.bascase.json);;JSON (*.json)")
        if path:
            self.import_case(path)

    def _save_prompt_dialog(self) -> None:
        from PyQt6.QtWidgets import QFileDialog
        from ....validation.intake_prompt import INTAKE_PROMPT
        path, _ = QFileDialog.getSaveFileName(
            self.browser, "Salvar prompt de intake", "BAS_intake_prompt.txt",
            "Texto (*.txt)")
        if path:
            from pathlib import Path
            Path(path).write_text(INTAKE_PROMPT, encoding="utf-8")
