"""Regression: the literature-priors CalibrationWizardDialog must construct
without crashing. It used to pass the string "currentRowChanged" as the
registerField changedSignal, raising TypeError and closing the whole app."""
import os

import pytest

# Headless Qt — skip cleanly if Qt can't initialise in this environment.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PyQt6.QtWidgets")


@pytest.fixture(scope="module")
def qapp():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_calibration_wizard_constructs(qapp):
    from bolt_analysis_studio.gui.calibration_wizard import CalibrationWizardDialog
    # Would raise TypeError on the registerField call before the fix.
    wiz = CalibrationWizardDialog(None)
    assert len(wiz.pageIds()) >= 1
