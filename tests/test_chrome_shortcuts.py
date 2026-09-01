"""Fase 6: atalhos de módulo/run/fit registrados."""
from PyQt6.QtGui import QShortcut


def test_module_and_run_shortcuts_registered(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        seqs = {s.key().toString() for s in win.findChildren(QShortcut)}
        assert "Ctrl+1" in seqs
        assert "Ctrl+6" in seqs
        assert "Ctrl+R" in seqs
        assert "Shift+F" in seqs   # fit (não 'F' puro, que engoliria digitação)
    finally:
        win.close()
