"""SharedCalibrator: UMA fisica, N estados — spec 2026-07-02 §2.5.

Testes sinteticos rapidos (n_cycles=300, poucas constantes livres): geram
curvas do proprio modelo com constantes conhecidas + ruido e verificam
recuperacao / estimacao de F0 / LOCO.
"""
import numpy as np
import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)
from bolt_analysis_studio.calibration.shared_calibrator import (
    ConditionSpec, SharedCalibrationConfig, SharedCalibrator,
)

M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)
N_CYC = 300
NOISE = 0.005


def _synth_curve(name, k_wear, F0_true, seed):
    """Gera uma curva F/F0 do proprio modelo (constante de wear conhecida)."""
    mat = JointMaterial(k_wear_spec=k_wear)
    ana = DynamicStiffnessAnalyzer(M16, mat, F0_true)
    ratio = [1.0]
    for _ in range(N_CYC):
        ana.step_cycle(20e3, np.pi / 2, 0.5, delta_amp=0.5e-3)
        ratio.append(max(ana.state.F_0, 0.0) / F0_true)
    cycles = np.linspace(0.0, N_CYC, 15)
    ref = np.interp(cycles, np.arange(N_CYC + 1), np.array(ratio))
    rng = np.random.default_rng(seed)
    return {"name": name, "cycles": cycles,
            "ratio": ref + rng.normal(0.0, NOISE, ref.shape)}


def _cond(name, k_wear, F0_true=50e3, F0_declared=None, seed=0):
    return ConditionSpec(
        name=name,
        curves=[_synth_curve(name, k_wear, F0_true, seed)],
        F0_init=F0_declared if F0_declared is not None else F0_true,
        F_amp=20e3, delta_amp=0.5e-3)


def _config(conds, bounds, estimate_F0=None):
    return SharedCalibrationConfig(
        geom=M16, conditions=conds, theta=np.pi / 2, freq=0.5,
        n_cycles=N_CYC, bounds=bounds,
        estimate_F0=estimate_F0 or {}, max_nfev=25)


def test_shared_fit_recovers_wear_constant_across_two_conditions():
    K_true = 8e-14   # 1.6x o prior k_wear_spec (5e-14) = K/H de 1.6e-4/2e9
    conds = [_cond("c0", K_true, seed=0), _cond("c1", K_true, seed=1)]
    cal = SharedCalibrator(_config(conds, {"k_wear_spec": (5e-15, 5e-13)}))
    res = cal.fit_parsimonious(tol=0.002, max_constants=2)
    assert "k_wear_spec" in res["free_constants"]
    assert res["constants"]["k_wear_spec"] == pytest.approx(K_true, rel=0.3)
    assert res["mae_global"] <= 4 * NOISE
    # tuners nunca entram: so constantes fisicas no resultado
    assert all(not k.endswith("_scale") for k in res["constants"])


def test_estimate_F0_improves_fit_and_moves_toward_truth():
    # curva gerada a 90 kN mas declarada a 50 kN
    cond = _cond("sobre", 5e-14, F0_true=90e3, F0_declared=50e3, seed=2)

    cal_fixed = SharedCalibrator(_config([cond], {}))
    mae_fixed = cal_fixed.global_mae()

    cal_est = SharedCalibrator(_config([cond], {},
                                       estimate_F0={"sobre": (40e3, 120e3)}))
    # baseline PRE-fit: o chute inicial (media geometrica dos bounds ~69.3 kN)
    # ja melhora sobre 50 kN — as assercoes exigem que o FIT va alem do chute,
    # senao um _fit_subset no-op passaria despercebido (achado de review).
    mae_guess = cal_est.global_mae()
    cal_est._fit_subset([])           # so o estado F0 (nenhuma constante)
    mae_est = cal_est.global_mae()

    assert mae_est < mae_fixed - 0.005   # estimar F0 melhora o fit
    assert mae_est < mae_guess - 0.005   # ...e o fit supera o chute inicial
    assert cal_est.F0_estimates["sobre"] == pytest.approx(90e3, rel=0.05)


def test_loco_predicts_held_out_condition_with_shared_physics():
    K_true = 8e-14
    conds = [_cond(f"c{i}", K_true, seed=i) for i in range(3)]
    cal = SharedCalibrator(_config(conds, {"k_wear_spec": (5e-15, 5e-13)}))
    res = cal.fit_parsimonious(tol=0.002, max_constants=1)
    loco = cal.loco(res["free_constants"])
    assert set(loco) == {"c0", "c1", "c2"}
    for name, r in loco.items():
        # fisica compartilhada: predicao da condicao retida ~ nivel do ruido
        assert r["MAE_pred"] <= 6 * NOISE, name
        assert r["state_F0_from_full_fit"] is False


def test_fit_is_deterministic():
    conds = [_cond("c0", 7.5e-14, seed=3)]
    cfg = _config(conds, {"k_wear_spec": (5e-15, 5e-13)})
    a = SharedCalibrator(cfg).fit_parsimonious(tol=0.002, max_constants=1)
    b = SharedCalibrator(cfg).fit_parsimonious(tol=0.002, max_constants=1)
    assert a["constants"] == b["constants"]


def test_loco_mae_stays_near_fit_mae_generalizes():
    """Regressao do claim central do Estagio A: a predicao leave-one-out nao
    degrada muito vs o fit (fisica compartilhada GENERALIZA, nao decora)."""
    K_true = 8e-14
    conds = [_cond(f"c{i}", K_true, seed=i) for i in range(3)]
    cal = SharedCalibrator(_config(conds, {"k_wear_spec": (5e-15, 5e-13)}))
    res = cal.fit_parsimonious(tol=0.002, max_constants=1)
    fit_by = res["mae_by_condition"]
    loco = cal.loco(res["free_constants"])
    for name in loco:
        # LOCO ~ fit: nunca pior que fit + 3*NOISE por condicao
        assert loco[name]["MAE_pred"] <= fit_by[name] + 3 * NOISE, name


def test_material_carries_conform_driver_and_constants_stay_numeric():
    """conform_driver flui via config (NAO via priors) -> material recebe a
    string; self.constants segue 100% numerico (line ~204 float(v) safe)."""
    conds = [_cond("c0", 1.6e-4)]
    # default = raw
    cal_raw = SharedCalibrator(_config(conds, {"k_wear_spec": (5e-15, 5e-13)}))
    assert cal_raw._material(conds[0]).conform_driver == "raw"
    # modo explicito flui ao material
    cfg = _config(conds, {"k_wear_spec": (5e-15, 5e-13)})
    cfg.conform_driver = "effective"
    cal = SharedCalibrator(cfg)
    assert cal._material(conds[0]).conform_driver == "effective"
    assert all(isinstance(v, (int, float)) for v in cal.constants.values())
