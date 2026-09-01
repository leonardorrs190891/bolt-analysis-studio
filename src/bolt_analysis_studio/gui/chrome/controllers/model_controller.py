"""ModelController — embrulha um MSDBuilderWindow oculto e expoe seus filhos
cablados (schematic/palette/inspector) para o chrome V2 re-hospedar. Delega
load/export ao metodo da janela. Sincroniza schematic<->AppState com guarda de
reentrancia (sem loop). Ver docs/superpowers/plans/2026-07-10-chrome-v2-model-module.md."""
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from ...msd_builder import MSDBuilderWindow
from ....core.app_state import get_app_state
from ....core.models.model import MSDModel

# Abas do PropertyInspector rico (mesmos indices que a V1 usa em main_window).
_TAB_INDEX = {"element": 0, "loading": 1, "contact": 2}


class ModelController(QObject):
    model_edited = pyqtSignal()   # emitido apos uma edicao estrutural do schematic

    def __init__(self, app_state=None, parent=None):
        super().__init__(parent)
        self.app_state = app_state or get_app_state()
        self._builder = MSDBuilderWindow()
        self._builder.hide()                      # nunca exibida; so fonte das pecas
        self.schematic = self._builder.schematic
        self.palette = self._builder.palette
        self.inspector = self._builder.inspector
        self.undo_stack = self._builder.undo_stack
        self._syncing = False
        # edicao estrutural do schematic -> propaga p/ o AppState
        self.schematic.model_changed.connect(self._on_schematic_changed)
        # canal de loading: PropertyInspector.loading_changed -> (builder oculto)
        # _on_loading_changed -> model_changed({"source": "loading"}) -> push.
        self._builder.model_changed.connect(self._on_builder_changed)

    # --- pecas p/ o chrome hospedar ---
    def viewport_widget(self):
        return self.schematic

    def show_inspector_tab(self, kind: str) -> None:
        idx = _TAB_INDEX.get(kind)
        if idx is not None:
            self.inspector.inspector_tabs.setCurrentIndex(idx)

    # --- carga/exportacao (delegadas a janela) ---
    def load_model(self, model) -> None:
        # So carrega um MSDModel real: um payload malformado (ex.: fake de teste
        # ou lixo num model_changed) trava/quebra load_from_msd_model. Guarda de
        # robustez — no app real app_state.model e sempre MSDModel ou None.
        if not isinstance(model, MSDModel):
            return
        self._syncing = True                      # nao re-sincroniza durante a carga
        try:
            self._builder.load_from_msd_model(model)
        finally:
            self._syncing = False
        # Modelo novo → reabilita o auto-fit (enquadra no próximo show do Model).
        if hasattr(self.schematic, "_auto_fit"):
            self.schematic._auto_fit = True

    def export_model(self) -> Optional[object]:
        return self._builder.export_to_msd_model()

    # --- sincronizacao ---
    def sync_from_app_state(self) -> None:
        if self._syncing:
            return
        model = getattr(self.app_state, "model", None)
        if model is not None:
            self.load_model(model)

    def _push_to_app_state(self) -> None:
        if self._syncing:
            return
        model = self.export_model()
        if model is None:
            return
        self._syncing = True
        try:
            self.app_state.model = model          # emite model_changed (guardado)
        finally:
            self._syncing = False
        self.model_edited.emit()

    def _on_schematic_changed(self) -> None:
        self._push_to_app_state()

    def _on_builder_changed(self, payload) -> None:
        # So o canal de loading: edicoes estruturais ja fluem por
        # schematic.model_changed (evita export duplo no mesmo evento).
        if isinstance(payload, dict) and payload.get("source") == "loading":
            self._push_to_app_state()
