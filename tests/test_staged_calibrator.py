from pathlib import Path
import numpy as np
import pytest

# ESTAGIO B (2026-07-09): StagedCalibrator APOSENTADO (fitava a camada de tuners
# removida do engine). Calibracao canonica = SharedCalibrator
# (test_shared_calibrator) / ParameterIdentifier(engine='v2', default_v2_params).
pytest.skip("Estagio B: StagedCalibrator aposentado (tuners removidos)",
            allow_module_level=True)

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointGeometry
from bolt_analysis_studio.calibration.segmentation import StageSegmentation
from bolt_analysis_studio.calibration.staged_calibrator import (
    CalibrationConfig, StagedCalibrator,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "New_Theory"
M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)
BOUNDS = {
    "k_emb_scale": (1e-3, 5.0), "k_creep_scale": (1e-3, 5.0),
    "k_wear_scale_tr": (1e-3, 5.0), "k_loose_scale_tr": (1e-3, 5.0),
    "Phi_tr_correction": (0.05, 5.0), "k_damage_scale": (1e-3, 5.0),
}


def _load(name):
    d = np.genfromtxt(DATA / f"M16_shear_{name}.csv", delimiter=",", skip_header=1)
    return {"name": name, "cycles": d[:, 0], "ratio": d[:, 1]}


def _config(fit_damage=False):
    return CalibrationConfig(
        geom=M16, F0_init=50_000.0, F_amp=20_000.0, theta=np.pi / 2,
        freq=0.5, n_cycles=2500, delta_amp=0.5e-3,
        segmentation=StageSegmentation(100, 1000, 2500),
        lambda_reg=0.001, bounds=BOUNDS, fit_damage=fit_damage,
    )


def test_nova_fit_quality_and_no_saturation():
    # Alvo "interpretavel" (lambda_reg=0.001): tuners perto de 1, sem saturar.
    # MAE ~0.04 e' o melhor com tuners criveis (o 0.022 antigo exigia
    # Phi_tr=0.10, pouco interpretavel) -- trade-off escolhido pelo usuario.
    curves = [_load(n) for n in ("TP3_nova", "TP8_nova", "TP11_nova", "MEAN_nova")]
    res = StagedCalibrator(_config(), curves).fit(n_passes=3)
    assert res["mae_global"] <= 0.045
    for name, mae in res["mae_per_segment"].items():
        if mae is not None:
            assert mae <= 0.07, f"segmento {name} MAE={mae}"
    assert res["bounds_saturated"] == []   # nenhum tuner colado no bound


def test_reaperto_fits_via_damage_without_saturation():
    # Dano amplifica wear => colapso do TP7 sem saturar k_loose (era 10.0).
    curves = [_load("TP7_reaperto")]
    res = StagedCalibrator(_config(fit_damage=True), curves).fit(n_passes=3)
    assert res["mae_global"] <= 0.04
    # k_loose NAO saturado (antes ficava colado em 10.0)
    assert res["tuners"]["k_loose_scale_tr"] < 4.5
    assert "k_loose_scale_tr" not in res["bounds_saturated"]


def test_deterministic():
    curves = [_load("MEAN_nova")]
    a = StagedCalibrator(_config(), curves).fit(n_passes=1)
    b = StagedCalibrator(_config(), curves).fit(n_passes=1)
    assert a["tuners"] == b["tuners"]


def test_parsimonious_uses_few_tuners():
    # Forward selection should justify only ~2 tuners for nova (not all 5),
    # operationalizing the identifiability finding. wear dominates disp-mode.
    curves = [_load("MEAN_nova")]
    res = StagedCalibrator(_config(), curves).fit_parsimonious(tol=0.005,
                                                               max_tuners=4)
    assert len(res["free_tuners"]) <= 3
    assert "k_wear_scale_tr" in res["free_tuners"]
    assert res["mae_global"] <= 0.05
    # unselected tuners stay at the physical default 1.0
    for t, v in res["tuners"].items():
        if t not in res["free_tuners"]:
            assert v == 1.0
