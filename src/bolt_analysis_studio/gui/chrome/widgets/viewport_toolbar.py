"""ViewportToolbar — fit/zoom/screenshot sobre o QGraphicsView ativo (Abaqus §5)."""
from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QGraphicsView, QToolBar

from ...icons import icon


class ViewportToolbar(QToolBar):
    def __init__(self, get_view: Callable[[], QGraphicsView], parent=None):
        super().__init__("Viewport", parent)
        self.setMovable(False)
        self._get_view = get_view
        self.addAction(icon("fit"), "Fit", self._fit)
        self.addAction(icon("zoom-in"), "Zoom In", lambda: self._zoom(1.25))
        self.addAction(icon("zoom-out"), "Zoom Out", lambda: self._zoom(0.8))
        self.addAction(icon("camera"), "Screenshot", self._screenshot)

    def _fit(self) -> None:
        view = self._get_view()
        scene = view.scene() if view is not None else None
        if scene is not None:
            view.fitInView(scene.itemsBoundingRect(),
                           Qt.AspectRatioMode.KeepAspectRatio)

    def _zoom(self, factor: float) -> None:
        view = self._get_view()
        if view is not None:
            view.scale(factor, factor)

    def _screenshot(self) -> None:
        view = self._get_view()
        if view is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salvar imagem", "viewport.png",
                                              "PNG (*.png)")
        if path:
            view.grab().save(path, "PNG")
