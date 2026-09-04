"""V2 (non-linear) calibration path of ParameterIdentifier."""
import warnings
from pathlib import Path

import numpy as np
import pytest

from bolt_analysis_studio.gui.new_analysis_wizard import AnalysisSpec, build_model
from bolt_analysis_studio.numerical.parameter_identifier import (
    ParameterIdentifier, default_v2_params, simulate_v2_curve, V2_PARAM_NAMES,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "New_Theory"


def _m16_model():
    m = build_model(AnalysisSpec(
        joint_preset_id="single_shear", bolt_diameter_mm=16, pitch_mm=2.0,
        control_mode="displacement", delta_amplitude_mm=0.5,
        frequency_hz=0.5, n_cycles=2500))
    m.global_loading.F_preload = 50_000.0
    m.global_loading.F_amplitude = 20_000.0
    return m


def test_simulate_v2_is_nonlinear():
    # A two-stage linear model would be piecewise-straight; the V2 model curves.
    m = _m16_model()
    c, r = simulate_v2_curve(m, tuners={}, n_cycles=2500,
                             control_mode="displacement", F0=50_000.0,
                             F_amp=20_000.0, theta=np.pi / 2, freq=0.5)
    assert len(r) == 2501 and r[0] == 1.0 and r[-1] < 1.0
    # second derivative meaningfully non-zero somewhere (curvature, not 2 lines)
    seg = r[::100]
    curv = np.abs(np.diff(seg, 2))
    assert curv.max() > 1e-3


def test_v2_calibration_runs_and_fits():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = _m16_model()
        ref = np.genfromtxt(DATA / "M16_shear_MEAN_nova.csv",
                            delimiter=",", skip_header=1)
        ident = ParameterIdentifier(m, ref[:, 0], ref[:, 1],
                                    params_to_fit=default_v2_params(),
                                    max_evals=60, engine="v2")
        res = ident.run(n_starts=2)
    assert res.success
    # Limiar re-medido em 2026-09-03 (era 0,08). NAO e' afrouxamento para fazer
    # um teste passar: ate' esta data o otimizador montava o JointMaterial so'
    # com os candidatos — sem o bloco `shared` canonico e sem o `p_ref_conform`
    # — ou seja, ajustava contra um motor que o aplicativo NUNCA roda. Agora usa
    # a mesma receita do Run (`solver_worker.build_v2_material`) e o ajuste
    # desta curva sintetica fecha em 0,113. O numero piorou porque o alvo passou
    # a ser o motor de verdade; o teto segue sendo um portao real — nos mesmos
    # defaults, SEM ajuste nenhum, esta curva da' 0,161 (medido).
    assert res.best_mae < 0.12
    # Fit returns exactly the params it was given (the core set). V2_PARAM_NAMES
    # is the broader dialog list (now also exposes slip_onset_W), so compare
    # against default_v2_params() rather than the full available list.
    assert set(res.best_params) == {p.name for p in default_v2_params()}
    assert set(res.best_params) <= set(V2_PARAM_NAMES)


def test_v2_engine_skips_F_transverse_requirement():
    # V1 would raise without F_transverse; V2 must not (it uses delta/F_amp).
    m = _m16_model()
    m.global_loading.F_transverse = 0.0
    # Should construct fine in V2 mode.
    ident = ParameterIdentifier(m, [0, 100], [1.0, 0.8],
                                params_to_fit=default_v2_params(), engine="v2")
    assert ident.engine == "v2"
