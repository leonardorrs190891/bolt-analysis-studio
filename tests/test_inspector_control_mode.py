"""PropertyInspector control_mode (displacement vs force) — Bug 5 completion.

The selector must round-trip through get/set_loading_data and grey out the
input that isn't the control driver."""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PyQt6.QtWidgets")


@pytest.fixture(scope="module")
def qapp():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_control_mode_roundtrip_and_enable(qapp):
    from bolt_analysis_studio.gui.msd_builder import PropertyInspector
    insp = PropertyInspector()

    # default = displacement → δ editable, F greyed
    d = insp.get_loading_data()
    assert d["control_mode"] == "displacement"
    assert insp.transverse_disp_spin.isEnabled()
    assert not insp.transverse_force_spin.isEnabled()

    # switch to force → F editable, δ greyed; survives a get/set round-trip
    insp.set_loading_data({"control_mode": "force"})
    assert insp.get_loading_data()["control_mode"] == "force"
    assert insp.transverse_force_spin.isEnabled()
    assert not insp.transverse_disp_spin.isEnabled()
