"""Fase 5: apenas Newmark-β e HHT-α expostos na UI (spec §3.A)."""
import pytest
from PyQt6.QtWidgets import QComboBox, QMessageBox


@pytest.fixture(autouse=True)
def _auto_confirm_close(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    yield


def test_solver_integrator_combos_have_two(qapp):
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    win = BoltAnalysisStudio()
    try:
        combos = win.findChildren(QComboBox)
        integ = [c for c in combos
                 if any("Newmark" in (c.itemText(i) or "") for i in range(c.count()))]
        assert integ, "combo de integrador não encontrado"
        for c in integ:
            items = [c.itemText(i) for i in range(c.count())]
            assert "Central Diff" not in items
            assert "RK4" not in items
            assert "Modal" not in items
            assert "Adaptive RK45" not in items
            assert "Newmark-β" in items and "HHT-α" in items
    finally:
        win.close()
