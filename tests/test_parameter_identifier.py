"""Round-trip test for ParameterIdentifier.

Generates a synthetic preload-decay curve by running CoupledLooseningAnalyzer
with a known mu_initial, then asks ParameterIdentifier to recover it from a
different starting point. Verifies the recovered mu is close to ground truth.
"""

import sys
import os
import warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np

warnings.filterwarnings("ignore", message="Preload retention")

from bolt_analysis_studio.core.models.model import MSDModel
from bolt_analysis_studio.core.models.element import LoadingData, LoadingType


def _build_test_model(mu_initial: float) -> MSDModel:
    """Minimal model that create_analyzer_from_msd_model can consume."""
    model = MSDModel()
    # Use a transverse force high enough that mu_initial materially shapes
    # the decay curve (otherwise the parameter is unidentifiable).
    model.global_loading = LoadingData(
        type=LoadingType.TRANSVERSE,
        F_preload=30_000.0,
        F_transverse=12_000.0,
        delta_amplitude=0.5,
        frequency=1.0,
        n_cycles=600,
    )
    # mu_initial is the Level-3 persistent path read by create_analyzer_from_msd_model
    model.mu_initial = mu_initial
    model.lubricated = True
    return model


def test_recover_mu_initial():
    from bolt_analysis_studio.numerical.coupled_loosening_analyzer import (
        create_analyzer_from_msd_model,
    )
    from bolt_analysis_studio.numerical.parameter_identifier import (
        ParameterIdentifier, mu_initial_param,
    )

    TRUE_MU = 0.14
    model_truth = _build_test_model(TRUE_MU)
    analyzer, _info = create_analyzer_from_msd_model(model_truth)
    truth = analyzer.run_analysis(
        preload_initial=30_000.0, F_transverse=12_000.0,
        n_cycles=600, output_interval=4,
    )
    ref_cycle = np.asarray(truth.cycles, dtype=float)
    ref_ratio = np.asarray(truth.preload_ratio, dtype=float)
    assert ref_cycle.size >= 10, "truth curve too short"
    assert abs(ref_ratio[0] - 1.0) < 0.05

    # Now give the identifier a fresh model with a different mu_initial
    # and ask it to recover TRUE_MU.
    model_fit = _build_test_model(mu_initial=0.10)
    ident = ParameterIdentifier(
        model_fit, ref_cycle, ref_ratio,
        params_to_fit=[mu_initial_param(lo=0.06, hi=0.25)],
        objective="mae", max_evals=40, seed=1,
    )
    result = ident.run(n_starts=2)
    print(f"True mu={TRUE_MU:.4f}, recovered={result.best_params['mu_initial']:.4f}, "
          f"MAE={result.best_mae:.4f}, n_evals={result.n_evals}, dt={result.duration_s:.1f}s")
    assert result.success, result.message
    recovered = result.best_params["mu_initial"]
    assert abs(recovered - TRUE_MU) < 0.02, (
        f"mu recovery off: got {recovered:.4f}, expected {TRUE_MU:.4f}")
    assert result.best_mae < 0.02, f"best MAE too high: {result.best_mae:.4f}"


def test_two_stage_overrides_roundtrip():
    """Ensure calibrated Stage I/II overrides survive save/load + reach analyzer."""
    from bolt_analysis_studio.numerical.coupled_loosening_analyzer import (
        create_analyzer_from_msd_model,
    )

    model = _build_test_model(mu_initial=0.12)
    model._two_stage_overrides = {"C_loosening": 0.77, "N_stage1": 321}

    # Round-trip through dict
    d = model.to_dict()
    assert d.get("two_stage_overrides") == {"C_loosening": 0.77, "N_stage1": 321}, d.get("two_stage_overrides")
    restored = MSDModel.from_dict(d)
    assert getattr(restored, '_two_stage_overrides', None) == {"C_loosening": 0.77, "N_stage1": 321}

    # Analyzer picks them up
    analyzer, info = create_analyzer_from_msd_model(restored)
    assert abs(analyzer.two_stage.C_loosening - 0.77) < 1e-9, analyzer.two_stage.C_loosening
    assert analyzer.two_stage.N_stage1 == 321, analyzer.two_stage.N_stage1
    assert info.get('two_stage_overrides_applied') == {"C_loosening": 0.77, "N_stage1": 321}
    print(f"overrides applied: {info['two_stage_overrides_applied']}")


if __name__ == "__main__":
    test_recover_mu_initial()
    test_two_stage_overrides_roundtrip()
    print("PASS")
