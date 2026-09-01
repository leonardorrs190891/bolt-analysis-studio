"""Fase 3: toolbar de viewport + bloco de contexto."""


def test_context_block_formats(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.context_block import ContextBlock
    cb = ContextBlock()
    cb.set_context("Model", "M16_junker", "Coupled-Loosening")
    txt = cb._label.text()
    assert "Model" in txt and "M16_junker" in txt and "Coupled-Loosening" in txt


def test_viewport_toolbar_actions(qapp):
    from PyQt6.QtWidgets import QGraphicsView
    from bolt_analysis_studio.gui.chrome.widgets.viewport_toolbar import ViewportToolbar
    view = QGraphicsView()
    tb = ViewportToolbar(lambda: view)
    labels = [a.text() for a in tb.actions() if a.text()]
    assert {"Fit", "Zoom In", "Zoom Out", "Screenshot"}.issubset(set(labels))


def test_chrome_updates_context_block_on_switch(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        win.switch_module("Loads")
        assert "Loads" in win.context_block._label.text()
    finally:
        win.close()
