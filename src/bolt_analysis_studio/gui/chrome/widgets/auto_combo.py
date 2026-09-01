"""AutoComboBox — combo com opção 'Auto (<inferido>)' + override (spec §3.B)."""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox


class AutoComboBox(QComboBox):
    value_changed = pyqtSignal(str)

    def __init__(self, options, inference_fn=None, parent=None):
        super().__init__(parent)
        self._options = list(options)
        self._inference_fn = inference_fn
        self._context = {}
        self._is_auto = True
        self._rebuild()
        self.currentIndexChanged.connect(self._on_index_changed)

    # --- estado ---
    @property
    def is_auto(self) -> bool:
        return self._is_auto

    def set_context(self, ctx: dict) -> None:
        self._context = dict(ctx or {})
        if self._is_auto:
            self._rebuild()

    def _inferred(self) -> str:
        if self._inference_fn is not None:
            try:
                val = self._inference_fn(self._context)
                if val in self._options:
                    return val
            except Exception:
                pass
        return self._options[0] if self._options else ""

    def current_resolved_value(self) -> str:
        if self._is_auto:
            return self._inferred()
        return self.currentText()

    # --- ações ---
    def set_value(self, value: str) -> None:
        if value not in self._options:
            return
        self._is_auto = False
        self._rebuild()
        self.setCurrentText(value)  # dispara _on_index_changed -> value_changed

    def reset_to_auto(self) -> None:
        self._is_auto = True
        self._rebuild()
        self.value_changed.emit(self.current_resolved_value())

    # --- interno ---
    def _rebuild(self) -> None:
        self.blockSignals(True)
        self.clear()
        if self._is_auto:
            self.addItem(f"Auto ({self._inferred()})")
        else:
            for opt in self._options:
                self.addItem(opt)
        self.blockSignals(False)

    def _on_index_changed(self, _idx: int) -> None:
        if not self._is_auto:
            self.value_changed.emit(self.currentText())
