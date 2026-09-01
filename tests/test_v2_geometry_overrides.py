"""Canal aditivo _v2_geometry_overrides no Run V2 (Plano B).

O gui_bridge anexa a geometria com proveniencia do caso ao modelo; o
_compute_v2_history a aplica sobre a geometria do config. Ausente/invalido =
comportamento anterior bit-identico.
"""

import os
import types

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="module")
def qapp():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _worker():
    from bolt_analysis_studio.core.solver_worker import SolverWorker
    return SolverWorker.__new__(SolverWorker)


def _cfg():
    return types.SimpleNamespace(initial_preload=50000.0, transverse_force=12000.0,
                                 bolt_diameter_mm=16.0, pitch_mm=2.0)


def _model(geom_overrides=None):
    gl = types.SimpleNamespace(control_mode="displacement", delta_amplitude=0.5,
                               frequency=0.5, type="TRANSVERSE")
    return types.SimpleNamespace(global_loading=gl, _v2_tuner_overrides=None,
                                 _v2_geometry_overrides=geom_overrides)


def test_geometry_overrides_change_the_run(qapp):
    w = _worker()
    w._current_model = _model()
    base = w._compute_v2_history(_cfg(), 800)["ratio"]
    w._current_model = _model({"L_eff": 0.080, "A_contact": 3.2e-4})
    over = w._compute_v2_history(_cfg(), 800)["ratio"]
    assert not np.allclose(base, over)          # geometria do caso muda o Run


def test_absent_or_invalid_overrides_are_noop(qapp):
    w = _worker()
    w._current_model = _model()
    base = w._compute_v2_history(_cfg(), 400)["ratio"]
    w._current_model = _model({})               # vazio = no-op
    assert np.allclose(base, w._compute_v2_history(_cfg(), 400)["ratio"])
    w._current_model = _model({"nao_existe": 9.9, "L_eff": "lixo"})
    r = w._compute_v2_history(_cfg(), 400)["ratio"]   # invalido ignorado, nao crasha
    assert np.allclose(base, r)
