"""Reference-curve trimming in the calibration dialog ("remove a part").

The user can crop an imported case-study curve to a cycle window so the fit and
the error metric (MAE/RMSE) use only the kept cycles. ``_active_reference``
masks every array-valued field consistently; an empty/invalid window is ignored.
"""

import os

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="module")
def qapp():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _dialog_with_ref(ref):
    from bolt_analysis_studio.gui.main_window import CalibrationDialog
    dlg = CalibrationDialog.__new__(CalibrationDialog)
    dlg._reference = ref
    dlg._trim_lo = dlg._trim_hi = None
    return dlg


def _ref():
    return {
        "cycle": np.arange(0, 11, dtype=float),
        "F_ratio": np.linspace(1.0, 0.0, 11),
        "F_kN": np.linspace(50.0, 0.0, 11),
    }


def test_no_trim_returns_full_curve(qapp):
    dlg = _dialog_with_ref(_ref())
    out = dlg._active_reference()
    assert len(out["cycle"]) == 11


def test_trim_window_crops_all_arrays_consistently(qapp):
    dlg = _dialog_with_ref(_ref())
    dlg._trim_lo, dlg._trim_hi = 3.0, 7.0
    out = dlg._active_reference()
    assert out["cycle"].tolist() == [3.0, 4.0, 5.0, 6.0, 7.0]
    assert len(out["cycle"]) == len(out["F_ratio"]) == len(out["F_kN"])
    assert out["F_ratio"][0] == pytest.approx(0.7)
    assert out["F_ratio"][-1] == pytest.approx(0.3)


def test_lower_bound_only(qapp):
    dlg = _dialog_with_ref(_ref())
    dlg._trim_lo, dlg._trim_hi = 6.0, None
    out = dlg._active_reference()
    assert out["cycle"].min() == 6.0 and out["cycle"].max() == 10.0


def test_empty_window_keeps_full_curve(qapp):
    dlg = _dialog_with_ref(_ref())
    dlg._trim_lo, dlg._trim_hi = 100.0, 200.0   # no cycles in range
    out = dlg._active_reference()
    assert len(out["cycle"]) == 11               # safe fallback


def test_none_reference_returns_none(qapp):
    dlg = _dialog_with_ref(None)
    assert dlg._active_reference() is None
