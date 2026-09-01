"""#2: smart defaults — inference_fns puras + AutoComboBox no inspector do Analysis."""
import pytest
from PyQt6.QtWidgets import QMessageBox


@pytest.fixture(autouse=True)
def _auto_confirm_close(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    yield


def test_inference_functions_pure():
    from bolt_analysis_studio.gui.chrome.inference import (
        infer_integrator, infer_control_mode, infer_friction_model)
    assert infer_control_mode({"delta_amplitude": 0.5}) == "Displacement"
    assert infer_control_mode({"delta_amplitude": None}) == "Force"
    assert infer_integrator({"damping": True}) == "HHT-α"
    assert infer_integrator({"damping": False}) == "Newmark-β"
    assert infer_friction_model({"lubricated": True}) == "Stribeck"
    assert infer_friction_model({"lubricated": False}) == "Coulomb"


def test_analysis_inspector_has_autocombos(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    from bolt_analysis_studio.gui.chrome.widgets.auto_combo import AutoComboBox
    win = ChromeWindow()
    try:
        win.switch_module("Analysis")
        combos = win.inspector.findChildren(AutoComboBox)
        assert combos, "inspector do Analysis sem AutoComboBox"
        # o valor resolvido é uma das opções (auto funciona)
        assert combos[0].current_resolved_value()
    finally:
        win.close()
