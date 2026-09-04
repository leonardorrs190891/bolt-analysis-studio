"""V2 non-linear preload routing in the solver.

The Run (coupled loosening analysis) must emit a physically non-linear preload
decay from the first simulation, produced by the validated V2 energy engine
(DynamicStiffnessAnalyzer), instead of the V1 two-stage straight lines.
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


def _cfg(**kw):
    base = dict(initial_preload=50000.0, transverse_force=12000.0,
                bolt_diameter_mm=16.0, pitch_mm=2.0)
    base.update(kw)
    return types.SimpleNamespace(**base)


def _model(control_mode="displacement", tuners=None, delta=0.5, freq=0.5,
           ltype="TRANSVERSE"):
    gl = types.SimpleNamespace(control_mode=control_mode, delta_amplitude=delta,
                               frequency=freq, type=ltype)
    return types.SimpleNamespace(global_loading=gl, _v2_tuner_overrides=tuners)


def _curvature(r):
    seg = r[:: max(1, len(r) // 40)]
    return float(np.abs(np.diff(seg, 2)).max()) if len(seg) > 2 else 0.0


def test_preload_curve_is_nonlinear_and_monotonic(qapp):
    w = _worker()
    w._current_model = _model()
    r = w._compute_v2_preload_curve(_cfg(), 2000)
    assert r is not None and r.size == 2001
    assert r[0] == pytest.approx(1.0)
    # strictly non-increasing (preload can only be lost)
    assert np.all(np.diff(r) <= 1e-9)
    # genuinely curved, not two straight lines
    assert _curvature(r) > 0.01
    # decay decelerates: early slope steeper than late slope
    assert abs(np.diff(r)[:5].mean()) > abs(np.diff(r)[-5:].mean())


def test_force_mode_runs_without_delta(qapp):
    w = _worker()
    w._current_model = _model(control_mode="force", delta=0.0)
    r = w._compute_v2_preload_curve(_cfg(), 1000)
    assert r is not None and r[0] == pytest.approx(1.0)
    assert _curvature(r) > 0.01


def test_stray_tuner_key_does_not_crash(qapp):
    w = _worker()
    # mu_initial is not a JointMaterial field -> must be filtered out
    w._current_model = _model(tuners={"k_emb_scale": 1.26, "k_wear_scale_tr": 0.54,
                                       "mu_initial": 0.1, "bogus": 9.0})
    r = w._compute_v2_preload_curve(_cfg(), 800)
    assert r is not None and r.size == 801


def test_degenerate_inputs_return_none(qapp):
    w = _worker()
    w._current_model = _model()
    assert w._compute_v2_preload_curve(_cfg(initial_preload=0.0), 100) is None
    assert w._compute_v2_preload_curve(_cfg(), 0) is None


def test_history_has_all_aligned_channels(qapp):
    w = _worker()
    w._current_model = _model()
    h = w._compute_v2_history(_cfg(), 1500)
    assert h is not None
    n = h["ratio"].size
    assert n == 1501
    for key in ("ratio", "wear_um", "angle_deg", "rate_deg", "D",
                "mu_bearing", "mu_thread"):
        assert h[key].size == n, f"{key} length mismatch"
    for mech in ("embedding", "creep", "wear", "rotational_loosening"):
        assert h["cum"][mech].size == n


def test_decomposition_sums_to_total_loss(qapp):
    """The 4 mechanism contributions must exactly account for the preload
    loss F0*(1-ratio) at every cycle (energy/force coherence)."""
    w = _worker()
    w._current_model = _model()
    h = w._compute_v2_history(_cfg(), 1500)
    s = (h["cum"]["embedding"] + h["cum"]["creep"]
         + h["cum"]["wear"] + h["cum"]["rotational_loosening"])
    total_kN = (1.0 - h["ratio"]) * h["F0"] / 1000.0
    assert np.allclose(s, total_kN, atol=1e-6)


def test_damage_modulates_friction(qapp):
    """With surface_damage active, mu_bearing falls as D grows."""
    w = _worker()
    w._current_model = _model(tuners={"c_D": 2.0, "k_dmg_mu": 1.0,
                                      "k_dmg_wear": 4.0, "W_ref": 1e4})
    h = w._compute_v2_history(_cfg(), 1500)
    assert h["D"][-1] > 0.0
    assert h["mu_bearing"][-1] < h["mu_bearing"][0]
    assert np.all(np.diff(h["D"]) >= -1e-12)            # damage only grows
    assert np.all(np.diff(h["mu_bearing"]) <= 1e-12)    # friction only falls


def test_end_to_end_secondary_arrays_are_v2_coherent(qapp):
    from bolt_analysis_studio.core.solver_worker import (
        SolverWorker, CoupledLooseningConfig)
    from bolt_analysis_studio.core.models.model import MSDModel
    from bolt_analysis_studio.core.models.element import LoadingData

    cfg = CoupledLooseningConfig(
        use_preset=True, use_msd_model=False, initial_preload=50000.0,
        transverse_force=12000.0, bolt_diameter_mm=16.0, pitch_mm=2.0,
        n_cycles=2000, mu_initial=0.12, lubricated=False)
    m = MSDModel(name="t")
    gl = LoadingData()
    gl.control_mode = "displacement"
    gl.delta_amplitude = 0.5
    gl.frequency = 0.5
    m.global_loading = gl

    w = SolverWorker()
    w._current_model = m
    res = w._run_coupled_loosening_analysis(cfg)

    wear = np.asarray(res.total_wear_um, dtype=float)
    angle = np.asarray(res.loosening_angle_deg, dtype=float)
    assert np.all(np.diff(wear) >= -1e-9)      # wear accumulates
    assert np.all(np.diff(angle) >= -1e-9)     # angle accumulates
    # decomposition is attached and self-consistent
    d = res._v2_mech_decomp
    assert d is not None
    s = (np.asarray(d["embedding"]) + np.asarray(d["creep"])
         + np.asarray(d["wear"]) + np.asarray(d["rotational_loosening"]))
    assert np.allclose(s, np.asarray(d["total_kN"]), atol=1e-6)
    assert res._v2_damage is not None


def test_end_to_end_override_fires(qapp):
    from bolt_analysis_studio.core.solver_worker import (
        SolverWorker, CoupledLooseningConfig)
    from bolt_analysis_studio.core.models.model import MSDModel
    from bolt_analysis_studio.core.models.element import LoadingData

    cfg = CoupledLooseningConfig(
        use_preset=True, use_msd_model=False, initial_preload=50000.0,
        transverse_force=12000.0, bolt_diameter_mm=16.0, pitch_mm=2.0,
        n_cycles=2000, mu_initial=0.12, lubricated=False)
    m = MSDModel(name="t")
    gl = LoadingData()
    gl.control_mode = "displacement"
    gl.delta_amplitude = 0.5
    gl.frequency = 0.5
    m.global_loading = gl

    w = SolverWorker()
    w._current_model = m
    logs = []
    w.log.connect(lambda s: logs.append(s))
    res = w._run_coupled_loosening_analysis(cfg)

    r = np.asarray(res.preload_ratio, dtype=float)
    assert r.size > 1
    assert np.all(np.diff(r) <= 1e-6)              # monotone decay
    assert _curvature(r) > 0.01                    # non-linear
    assert any("V2 non-linear" in s for s in logs)  # routed through V2


def test_conformation_default_on_arrests_overtorque(qapp):
    """Conformacao LIGADA por default no Run: em sobretorque (pct alto) o driver
    effective arresta a perda slip-driven -> pre-carga final MAIOR que off."""
    w = _worker()
    cfg = _cfg(initial_preload=120000.0, preload_percent_yield=95.0)
    w._current_model = _model()                       # default: conformacao ON
    r_on = w._compute_v2_history(cfg, 2000)["ratio"]
    w._current_model = _model(tuners={"W_conf_ref": 0.0})   # override: OFF
    r_off = w._compute_v2_history(cfg, 2000)["ratio"]
    assert r_on[-1] > r_off[-1] + 0.01                # segura mais pre-carga


def ancora_interna(qapp):
    """Na ESCALA âncora interna (F0~50 kN) e pre-carga nominal (70% escoamento) a
    conformacao eh ~inerte (curva ~= off). NB: a inercia no nominal eh
    escala-dependente (o W_conf_ref fixo eh calibrado na escala da âncora interna); em F0 alto
    o gate morde tb no nominal — ver caveat em solver_worker._compute_v2_history."""
    w = _worker()
    cfg = _cfg(initial_preload=50000.0, preload_percent_yield=70.0)
    w._current_model = _model()                       # default ON
    r_on = w._compute_v2_history(cfg, 2000)["ratio"]
    w._current_model = _model(tuners={"W_conf_ref": 0.0})   # OFF
    r_off = w._compute_v2_history(cfg, 2000)["ratio"]
    assert abs(r_on[-1] - r_off[-1]) < 0.03           # ~inerte no nominal


def test_conform_driver_string_override_flows(qapp):
    """Filtro type-aware deixa a STRING conform_driver fluir: em sobretorque,
    override 'raw' difere do default 'effective' => a string passou (o filtro
    float antigo a descartaria e as curvas seriam identicas)."""
    w = _worker()
    cfg = _cfg(initial_preload=120000.0, preload_percent_yield=95.0)
    w._current_model = _model(tuners={"conform_driver": "effective"})
    r_eff = w._compute_v2_history(cfg, 2000)["ratio"]
    w._current_model = _model(tuners={"conform_driver": "raw"})
    r_raw = w._compute_v2_history(cfg, 2000)["ratio"]
    assert abs(r_eff[-1] - r_raw[-1]) > 1e-6
