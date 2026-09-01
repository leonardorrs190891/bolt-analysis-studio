"""Parameter identification for MSD self-loosening models.

Given a reference preload-decay curve (cycle → F/F₀) and an MSD model, this
module fits a user-selected subset of model parameters so that the BAS
simulation best matches the reference. Uses scipy Nelder-Mead with multiple
random starts for robustness against local minima.

Usage:
    from bolt_analysis_studio.numerical.parameter_identifier import (
        ParameterIdentifier, mu_initial_param, C_loosening_param,
    )
    identifier = ParameterIdentifier(
        model, ref_cycle, ref_ratio,
        params_to_fit=[mu_initial_param(), C_loosening_param()],
    )
    result = identifier.run(n_starts=3)
    print(result.best_params, result.best_mae)
"""

from __future__ import annotations

import copy
import math
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import minimize


# =============================================================================
# Fittable-parameter schema
# =============================================================================

@dataclass
class FittableParam:
    """A model parameter exposed to the optimiser.

    `target` is a dotted path identifying where to apply the value:
      - 'mu_initial'            → passed as mu_initial= to create_analyzer_from_msd_model
      - 'two_stage.<field>'     → written onto the TwoStageLooseningParams override
    """
    name: str
    default: float
    lo: float
    hi: float
    target: str = ''
    log_scale: bool = False
    integer: bool = False

    def normalise(self, value: float) -> float:
        """Map a real value in [lo, hi] to [0, 1]."""
        if self.log_scale:
            return (math.log(value) - math.log(self.lo)) / (
                math.log(self.hi) - math.log(self.lo))
        return (value - self.lo) / (self.hi - self.lo)

    def denormalise(self, x: float) -> float:
        """Map a normalised x (unclamped) back to real scale within bounds."""
        x = max(0.0, min(1.0, float(x)))
        if self.log_scale:
            v = math.exp(math.log(self.lo) + x * (math.log(self.hi) - math.log(self.lo)))
        else:
            v = self.lo + x * (self.hi - self.lo)
        return int(round(v)) if self.integer else v


# -----------------------------------------------------------------------------
# Preset factories for the most useful parameters
# -----------------------------------------------------------------------------

def mu_initial_param(lo: float = 0.06, hi: float = 0.25) -> FittableParam:
    return FittableParam("mu_initial", default=0.12,
                         lo=lo, hi=hi, target="mu_initial")


# -----------------------------------------------------------------------------
# V2 (non-linear) tuner params — target the JointMaterial multipliers of the
# DynamicStiffnessAnalyzer. Used when ParameterIdentifier(engine="v2").
# -----------------------------------------------------------------------------

# ESTAGIO B (2026-07-09): os tuners adimensionais (k_emb_scale, k_creep_scale,
# k_wear_scale_tr, k_loose_scale_tr, Phi_tr_correction) foram REMOVIDOS do
# engine. O identificador agora fita as CONSTANTES FISICAS diretamente (com
# unidade e bounds de literatura). .msd/payloads legados com tuners sao
# traduzidos por calibration.tuner_shim na fronteira de consumo.

def jm_emb_depth_param(lo: float = 1e-6, hi: float = 5e-5) -> FittableParam:
    """Profundidade de assentamento f_Z [m] (era k_emb_scale·emb_depth)."""
    return FittableParam("emb_depth", 30e-6, lo, hi, target="jm.emb_depth")

def jm_C_creep_param(lo: float = 1e-12, hi: float = 1e-10) -> FittableParam:
    """Coeficiente de Norton C_creep (era k_creep_scale·C_creep)."""
    return FittableParam("C_creep", 1.8667e-11, lo, hi, target="jm.C_creep")

def jm_tr_loose_gain_param(lo: float = 0.5, hi: float = 6.0) -> FittableParam:
    """Ganho transversal do loosening (absorveu Phi_tr_correction·k_loose_tr)."""
    return FittableParam("tr_loose_gain", 2.0, lo, hi, target="jm.tr_loose_gain")

def jm_slip_onset_param(lo: float = 0.0, hi: float = 10000.0) -> FittableParam:
    """Incubacao do estagio 1: limiar de slip acumulado [J] que libera o
    colapso slip-driven (wear+loosening). 0 = sem incubacao. Da o plato
    inicial dos 3 estagios."""
    return FittableParam("slip_onset_W", 500.0, lo, hi, target="jm.slip_onset_W")

def jm_k_wear_spec_param(lo: float = 1e-15, hi: float = 1e-12) -> FittableParam:
    """Razao de wear especifica k_wear_spec = K/H [1/Pa] — o parametro de wear
    IDENTIFICAVEL (merge §4.42a; K_archard/hardness so aparecem como razao).
    Start 5e-14 = 1e-4/2e9 (par legado default). 0 = usa a via legada."""
    return FittableParam("k_wear_spec", 5e-14, lo, hi, target="jm.k_wear_spec")

def default_v2_params() -> List[FittableParam]:
    """Constantes fisicas nucleares p/ uma calibracao de shear transversal
    (Estagio B: era a camada de 5 tuners; agora sao as proprias constantes,
    com unidade e bounds de literatura)."""
    return [jm_emb_depth_param(), jm_C_creep_param(),
            jm_k_wear_spec_param(), jm_tr_loose_gain_param()]


def _geom_from_model(model):
    """Build a JointGeometry for the V2 engine from the model's bolt size."""
    from .dynamic_stiffness_analyzer import JointGeometry
    gl = model.global_loading
    d_mm = float(getattr(gl, 'bolt_diameter', 0) or getattr(model, 'bolt_diameter', 0) or 16.0)
    p_mm = float(getattr(gl, 'pitch', 0) or getattr(model, 'pitch', 0) or 2.0)
    d, p = d_mm * 1e-3, p_mm * 1e-3
    d2 = d - 0.6495 * p
    d1 = d - 1.0825 * p
    A_s = math.pi / 4.0 * ((d2 + d1) / 2.0) ** 2          # m²
    return JointGeometry(
        A_s=A_s, L_eff=max(3.125 * d, 0.02), d_2=d2, pitch=p,
        r_bearing=0.75 * d, A_contact=1e-4)


def simulate_v2_curve(model, tuners: dict, n_cycles: int, control_mode: str,
                      F0: float, F_amp: float, theta: float, freq: float):
    """Run the non-linear DynamicStiffnessAnalyzer and return (cycle, ratio).

    control_mode 'displacement' imposes delta_amplitude (disp-controlled);
    'force' runs force-controlled (delta_amp=None).
    """
    from .dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer, JointMaterial,
    )
    geom = _geom_from_model(model)
    mat = JointMaterial(**{k: float(v) for k, v in tuners.items()})
    ana = DynamicStiffnessAnalyzer(geom, mat, float(F0))
    delta = None
    if control_mode == "displacement":
        delta = float(getattr(model.global_loading, 'delta_amplitude', 0.5) or 0.5) * 1e-3
    ratio = [1.0]
    for _ in range(int(n_cycles)):
        ana.step_cycle(float(F_amp), float(theta), float(freq), delta_amp=delta)
        ratio.append(max(ana.state.F_0, 0.0) / float(F0))
    return np.arange(int(n_cycles) + 1, dtype=float), np.array(ratio)

def C_loosening_param(lo: float = 0.05, hi: float = 1.5) -> FittableParam:
    return FittableParam("C_loosening", default=0.3,
                         lo=lo, hi=hi, target="two_stage.C_loosening")

def N_stage1_param(lo: int = 50, hi: int = 800) -> FittableParam:
    return FittableParam("N_stage1", default=200.0,
                         lo=float(lo), hi=float(hi), integer=True,
                         target="two_stage.N_stage1")

def delta_F1_ratio_param(lo: float = 0.05, hi: float = 0.40) -> FittableParam:
    return FittableParam("delta_F1_ratio", default=0.15,
                         lo=lo, hi=hi, target="two_stage.delta_F1_ratio")

def N_stage2_param(lo: int = 200, hi: int = 10000) -> FittableParam:
    return FittableParam("N_stage2", default=2000.0,
                         lo=float(lo), hi=float(hi), integer=True,
                         target="two_stage.N_stage2")

def k_stage2_param(lo: float = 1e-6, hi: float = 1e-3) -> FittableParam:
    return FittableParam("k_stage2", default=3e-5,
                         lo=lo, hi=hi, log_scale=True,
                         target="two_stage.k_stage2")

def transition_sharpness_param(lo: float = 1.0, hi: float = 10.0) -> FittableParam:
    return FittableParam("transition_sharpness", default=3.0,
                         lo=lo, hi=hi, target="two_stage.transition_sharpness")


# -----------------------------------------------------------------------------
# Curve-shape Stage II tuning (2026-04-23)
# -----------------------------------------------------------------------------

def F_infinity_ratio_param(lo: float = 0.05, hi: float = 1.0) -> FittableParam:
    return FittableParam("F_infinity_ratio", default=0.20,
                         lo=lo, hi=hi, target="two_stage.F_infinity_ratio")

def friction_recovery_gain_param(lo: float = 0.5, hi: float = 10.0) -> FittableParam:
    return FittableParam("friction_recovery_gain", default=1.0,
                         lo=lo, hi=hi, target="two_stage.friction_recovery_gain")

def creep_coefficient_param(lo: float = 1e-9, hi: float = 1e-4) -> FittableParam:
    return FittableParam("creep_coefficient", default=1e-7,
                         lo=lo, hi=hi, log_scale=True,
                         target="two_stage.creep_coefficient")

def noise_amplitude_param(lo: float = 0.0, hi: float = 0.20) -> FittableParam:
    return FittableParam("noise_amplitude", default=0.0,
                         lo=lo, hi=hi, target="two_stage.noise_amplitude")


# -----------------------------------------------------------------------------
# Fixture stiffness, friction split, damping (2026-04-23)
# -----------------------------------------------------------------------------
# Bounds chosen so the optimiser can move ±50 % around analytical defaults
# (E·A/L for a typical M16 grip). Override per-row via the GUI for other sizes.

def k_bolt_param(lo: float = 1e8, hi: float = 1e10) -> FittableParam:
    return FittableParam("k_bolt", default=5e8,
                         lo=lo, hi=hi, log_scale=True, target="k_bolt")

def k_member_param(lo: float = 1e8, hi: float = 1e10) -> FittableParam:
    return FittableParam("k_member", default=1.5e9,
                         lo=lo, hi=hi, log_scale=True, target="k_member")

def k_transverse_ratio_param(lo: float = 0.05, hi: float = 1.0) -> FittableParam:
    return FittableParam("k_transverse_ratio", default=0.3,
                         lo=lo, hi=hi, target="k_transverse_ratio")

def mu_thread_param(lo: float = 0.06, hi: float = 0.30) -> FittableParam:
    return FittableParam("mu_thread", default=0.12,
                         lo=lo, hi=hi, target="mu_thread")

def mu_bearing_param(lo: float = 0.06, hi: float = 0.30) -> FittableParam:
    return FittableParam("mu_bearing", default=0.12,
                         lo=lo, hi=hi, target="mu_bearing")

def slip_onset_factor_param(lo: float = 0.30, hi: float = 1.0) -> FittableParam:
    """Pai-Hess slip-onset factor (multiplier on µ·N for stick→slip transition).
    Default 0.46 (Pai-Hess 2003); set to 1.0 to revert to classical Coulomb."""
    return FittableParam("slip_onset_factor", default=0.46,
                         lo=lo, hi=hi, target="slip_onset_factor")

def mu_steady_ratio_param(lo: float = 0.3, hi: float = 1.0) -> FittableParam:
    """Steady-state µ as a fraction of initial µ (mu_steady = ratio · mu_initial).
    Lower values → faster Stage II decay rate."""
    return FittableParam("mu_steady_ratio", default=0.83,
                         lo=lo, hi=hi, target="friction.mu_steady_ratio")

def mu_peak_ratio_param(lo: float = 0.9, hi: float = 1.8) -> FittableParam:
    """Peak (run-in) µ as a fraction of initial µ (mu_peak = ratio · mu_initial)."""
    return FittableParam("mu_peak_ratio", default=1.5,
                         lo=lo, hi=hi, target="friction.mu_peak_ratio")


def damping_zeta_param(lo: float = 0.005, hi: float = 0.15) -> FittableParam:
    """Rayleigh damping ratio. Stored on analyzer for downstream time-integration
    use; has minimal effect on quasi-static preload-decay over thousands of
    cycles, so this is mostly a placeholder for fixture-profile completeness."""
    return FittableParam("damping_zeta", default=0.02,
                         lo=lo, hi=hi, target="damping_zeta")


# -----------------------------------------------------------------------------
# Per-element MSD parameters (2026-04-25)
# Lets the user select an individual schematic element and calibrate its
# k / c / m. Target syntax: 'element.<id>.<kind>' where kind in {k,c,m}.
# Bounds default to ±50 % of the element's current value.
# -----------------------------------------------------------------------------

def element_msd_param(element_id: int,
                      kind: str,
                      default: float,
                      lo: Optional[float] = None,
                      hi: Optional[float] = None,
                      element_name: str = "") -> FittableParam:
    """Calibrate the k / c / m of a specific element by id."""
    if kind not in ("k", "c", "m"):
        raise ValueError(f"kind must be one of k,c,m — got {kind!r}")
    d = float(default) if default and default > 0 else 1.0
    lo = float(lo) if lo is not None else d * 0.5
    hi = float(hi) if hi is not None else d * 2.0
    if hi <= lo:
        hi = lo * 2.0 + 1e-12
    label = f"elem{element_id}.{kind}"
    if element_name:
        label = f"{element_name}#{element_id}.{kind}"
    return FittableParam(label, default=d, lo=lo, hi=hi,
                         log_scale=True,
                         target=f"element.{element_id}.{kind}")


# Map from display-name → factory, so the GUI dialog can offer checkboxes.
# Order matters: this is the row order in CalibrationDialog.
PRESET_PARAMS: dict = {
    # Friction
    "mu_initial":           mu_initial_param,
    "mu_thread":            mu_thread_param,
    "mu_bearing":           mu_bearing_param,
    "mu_peak_ratio":        mu_peak_ratio_param,
    "mu_steady_ratio":      mu_steady_ratio_param,
    "slip_onset_factor":    slip_onset_factor_param,
    # Stiffness (fixture/joint)
    "k_bolt":               k_bolt_param,
    "k_member":             k_member_param,
    "k_transverse_ratio":   k_transverse_ratio_param,
    # Damping (placeholder)
    "damping_zeta":         damping_zeta_param,
    # Two-stage Jiang/Yang
    "C_loosening":          C_loosening_param,
    "N_stage1":             N_stage1_param,
    "delta_F1_ratio":       delta_F1_ratio_param,
    "N_stage2":             N_stage2_param,
    "k_stage2":             k_stage2_param,
    "transition_sharpness": transition_sharpness_param,
    # Curve-shape Stage II
    "F_infinity_ratio":      F_infinity_ratio_param,
    "friction_recovery_gain": friction_recovery_gain_param,
    "creep_coefficient":     creep_coefficient_param,
    "noise_amplitude":       noise_amplitude_param,
    # V2 physical constants (engine="v2") — Estagio B: constantes, nao tuners
    "emb_depth":             jm_emb_depth_param,
    "C_creep":               jm_C_creep_param,
    "k_wear_spec":           jm_k_wear_spec_param,
    "tr_loose_gain":         jm_tr_loose_gain_param,
    "slip_onset_W":          jm_slip_onset_param,
}

# Names of the V2 physical constants+states, for the dialog engine switch.
V2_PARAM_NAMES = ("emb_depth", "C_creep", "k_wear_spec", "tr_loose_gain",
                  "slip_onset_W")


# =============================================================================
# Calibration result
# =============================================================================

@dataclass
class CalibrationResult:
    """Outcome of a parameter identification run."""
    best_params: dict                     # name → real value
    best_mae: float
    best_rmse: float
    n_evals: int
    duration_s: float
    success: bool
    message: str = ""
    trace: List[dict] = field(default_factory=list)
    # Best simulated curve, so the GUI can overlay it without re-running.
    sim_cycle: Optional[np.ndarray] = None
    sim_ratio: Optional[np.ndarray] = None


# =============================================================================
# Identifier
# =============================================================================

class _CancelException(Exception):
    """Raised from the objective to short-circuit scipy's inner loop."""


class ParameterIdentifier:
    """Fit a subset of MSD-model parameters to a reference preload-decay curve.

    Parameters
    ----------
    model : MSDModel
        Must have non-zero ``global_loading.F_preload``. ``F_transverse`` is
        required OR will be derived from ``delta_amplitude`` + ``k_transverse``.
    reference_cycle, reference_ratio : array-like
        The lab curve. ``reference_ratio`` should be F/F₀ (≈1.0 at cycle 0).
    params_to_fit : list of FittableParam
    objective : {'mae', 'rmse'}
    max_evals : int
        Hard upper bound on total analyzer runs across all multi-starts.
    seed : int
        RNG seed for multi-start positions — results are reproducible.
    """

    def __init__(self,
                 model,
                 reference_cycle: Sequence[float],
                 reference_ratio: Sequence[float],
                 params_to_fit: Sequence[FittableParam],
                 objective: str = "mae",
                 max_evals: int = 150,
                 seed: int = 42,
                 transverse_stiffness: Optional[float] = None,
                 engine: str = "v1"):
        self.model = model
        self.ref_cycle = np.asarray(reference_cycle, dtype=float)
        self.ref_ratio = np.asarray(reference_ratio, dtype=float)
        self.params = list(params_to_fit)
        if objective not in ("mae", "rmse"):
            raise ValueError(f"objective must be 'mae' or 'rmse', got {objective!r}")
        if engine not in ("v1", "v2"):
            raise ValueError(f"engine must be 'v1' or 'v2', got {engine!r}")
        self.objective_name = objective
        self.engine = engine
        self.max_evals = int(max_evals)
        self.seed = int(seed)

        self._eval_count = 0
        self._cancel = False
        self._trace: List[dict] = []
        self._best: Optional[dict] = None
        self._progress_cb: Optional[Callable[[int, int, float], None]] = None

        # Extract baseline loading from the model (preload, transverse, n_cycles)
        gl = model.global_loading
        self.preload_initial = float(getattr(gl, 'F_preload', 0.0) or 0.0)
        F_trans = float(getattr(gl, 'F_transverse', 0.0) or 0.0)
        if F_trans <= 0 and transverse_stiffness and transverse_stiffness > 0:
            # Derive from delta_amplitude × k_trans (mm → m)
            delta_mm = float(getattr(gl, 'delta_amplitude', 0.0) or 0.0)
            F_trans = (delta_mm * 1e-3) * float(transverse_stiffness)
        self.F_transverse = F_trans
        self.n_cycles = int(getattr(gl, 'n_cycles', 500) or 500)

        # V2 (non-linear) loading: the DynamicStiffnessAnalyzer is driven by
        # F_amplitude + delta_amplitude in the model's control_mode, so it does
        # NOT need F_transverse.
        self.control_mode = str(getattr(gl, 'control_mode', 'displacement') or 'displacement')
        self.F_amp = float(getattr(gl, 'F_amplitude', 0.0) or 0.0)
        self.freq = float(getattr(gl, 'frequency', 0.5) or 0.5)
        _gl_type = getattr(gl, 'type', None)
        _type_name = getattr(_gl_type, 'name', str(_gl_type)).upper()
        self.theta = {"AXIAL": 0.0, "TRANSVERSE": math.pi / 2.0,
                      "COMBINED": math.pi / 4.0}.get(_type_name, math.pi / 2.0)

        if self.preload_initial <= 0:
            raise ValueError("model.global_loading.F_preload must be > 0 to calibrate")
        if self.engine == "v1" and self.F_transverse <= 0:
            raise ValueError(
                "F_transverse could not be determined. Set "
                "global_loading.F_transverse (N) or pass transverse_stiffness "
                "so it can be derived from delta_amplitude.")
        if self.engine == "v2" and self.F_amp <= 0 and self.control_mode == "force":
            raise ValueError(
                "Force-controlled V2 calibration needs global_loading.F_amplitude > 0.")
        if len(self.params) == 0:
            raise ValueError("No parameters to fit")

    # ---- progress + cancellation ----------------------------------------

    def cancel(self) -> None:
        self._cancel = True

    def set_progress_callback(self,
                              cb: Callable[[int, int, float], None]) -> None:
        """cb(n_evals_done, n_evals_max, best_objective_so_far)."""
        self._progress_cb = cb

    # ---- main entry point ------------------------------------------------

    def run(self, n_starts: int = 3) -> CalibrationResult:
        """Run multi-start Nelder-Mead; returns the best across all starts."""
        t0 = time.time()
        rng = np.random.default_rng(self.seed)
        dim = len(self.params)

        # Start 1 = defaults; remaining starts = uniform in the interior
        starts: List[np.ndarray] = [
            np.array([p.normalise(p.default) for p in self.params], dtype=float)
        ]
        for _ in range(max(0, n_starts - 1)):
            starts.append(rng.uniform(0.1, 0.9, size=dim))

        per_start_budget = max(8, self.max_evals // max(1, len(starts)))
        for start_vec in starts:
            if self._cancel or self._eval_count >= self.max_evals:
                break
            try:
                minimize(
                    self._objective, start_vec, method="Nelder-Mead",
                    options={
                        "maxiter": per_start_budget,
                        "maxfev": per_start_budget,
                        "xatol": 0.005,
                        "fatol": 1e-5,
                        "adaptive": True,
                    },
                )
            except _CancelException:
                break
            except Exception:
                # Non-fatal: scipy sometimes throws on degenerate simplices.
                continue

        dt = time.time() - t0
        if self._best is None:
            return CalibrationResult(
                best_params={p.name: p.default for p in self.params},
                best_mae=float("inf"), best_rmse=float("inf"),
                n_evals=self._eval_count, duration_s=dt,
                success=False,
                message="No valid evaluation produced",
                trace=self._trace,
            )
        return CalibrationResult(
            best_params=dict(self._best["params"]),
            best_mae=self._best["mae"],
            best_rmse=self._best["rmse"],
            n_evals=self._eval_count,
            duration_s=dt,
            success=True,
            message=("Cancelled — returning best so far"
                     if self._cancel else "OK"),
            trace=self._trace,
            sim_cycle=self._best["sim_cycle"],
            sim_ratio=self._best["sim_ratio"],
        )

    # ---- objective -------------------------------------------------------

    def _objective(self, x_norm: np.ndarray) -> float:
        if self._cancel or self._eval_count >= self.max_evals:
            raise _CancelException()
        real = {p.name: p.denormalise(float(xn))
                for p, xn in zip(self.params, x_norm)}
        try:
            sim_cycle, sim_ratio = self._simulate(real)
        except Exception:
            return 1e6
        if sim_cycle.size < 2:
            return 1e6

        interp = np.interp(self.ref_cycle, sim_cycle, sim_ratio,
                           left=sim_ratio[0], right=sim_ratio[-1])
        err = interp - self.ref_ratio
        mae = float(np.mean(np.abs(err)))
        rmse = float(np.sqrt(np.mean(err ** 2)))
        obj = mae if self.objective_name == "mae" else rmse

        self._eval_count += 1
        self._trace.append({"eval": self._eval_count,
                            "params": dict(real), "mae": mae, "rmse": rmse})
        if (self._best is None
                or obj < (self._best["mae"] if self.objective_name == "mae"
                          else self._best["rmse"])):
            self._best = {"params": dict(real), "mae": mae, "rmse": rmse,
                          "sim_cycle": sim_cycle, "sim_ratio": sim_ratio}
        if self._progress_cb is not None:
            try:
                self._progress_cb(self._eval_count, self.max_evals,
                                  self._best["mae"])
            except Exception:
                pass
        return obj

    # ---- simulation ------------------------------------------------------

    def _simulate(self, real: dict) -> Tuple[np.ndarray, np.ndarray]:
        """Build a fresh analyzer with the candidate params applied, run it."""
        if self.engine == "v2":
            return self._simulate_v2(real)
        from bolt_analysis_studio.numerical.coupled_loosening_analyzer import (
            create_analyzer_from_msd_model, TwoStageLooseningParams,
        )
        # Sort params into buckets: TwoStage overrides, scalar analyzer attrs,
        # friction overrides, per-element MSD overrides, and the special
        # mu_initial constructor kwarg.
        two_stage = TwoStageLooseningParams()
        mu_override: Optional[float] = None
        attr_overrides: dict = {}      # plain attrs on analyzer (k_bolt, etc.)
        friction_overrides: dict = {}  # fields on analyzer.friction
        # Friction ratios applied AFTER mu_initial is set on the analyzer.
        # (mu_peak / mu_steady = ratio · mu_initial)
        friction_ratio_overrides: dict = {}
        # element_overrides[(elem_id, kind)] = new_value
        element_overrides: dict = {}

        for p in self.params:
            v = real[p.name]
            tgt = p.target
            if tgt == "mu_initial":
                mu_override = float(v)
            elif tgt.startswith("two_stage."):
                attr = tgt.split(".", 1)[1]
                setattr(two_stage, attr, v)
            elif tgt in ("k_bolt", "k_member"):
                attr_overrides[tgt] = float(v)
            elif tgt == "k_transverse_ratio":
                attr_overrides["_k_transverse_ratio"] = float(v)
            elif tgt == "damping_zeta":
                attr_overrides["_damping_zeta"] = float(v)
            elif tgt == "slip_onset_factor":
                attr_overrides["slip_onset_factor"] = float(v)
            elif tgt == "mu_thread":
                friction_overrides["mu_thread_initial"] = float(v)
            elif tgt == "mu_bearing":
                friction_overrides["mu_bearing_initial"] = float(v)
            elif tgt == "friction.mu_steady_ratio":
                friction_ratio_overrides["mu_steady"] = float(v)
            elif tgt == "friction.mu_peak_ratio":
                friction_ratio_overrides["mu_peak"] = float(v)
            elif tgt.startswith("element."):
                # element.<id>.<kind>
                _, eid_s, kind = tgt.split(".", 2)
                element_overrides[(int(eid_s), kind)] = float(v)

        # Per-element MSD overrides: temporarily mutate model.elements before
        # building the analyzer (matrix assembly picks up the new values), then
        # restore originals. try/finally guards against analyzer construction
        # raising mid-iteration.
        saved: dict = {}
        if element_overrides:
            ix = {e.id: e for e in self.model.elements}
            for (eid, kind), val in element_overrides.items():
                el = ix.get(eid)
                if el is None or not hasattr(el, "msd"):
                    continue
                saved[(eid, kind)] = getattr(el.msd, kind, 0.0)
                setattr(el.msd, kind, val)

        try:
            analyzer, _info = create_analyzer_from_msd_model(
                self.model, mu_initial=mu_override)
        finally:
            for (eid, kind), orig in saved.items():
                el = next((e for e in self.model.elements if e.id == eid), None)
                if el is not None and hasattr(el, "msd"):
                    setattr(el.msd, kind, orig)

        # Two-stage override: assign in full (CLAUDE.md gotcha)
        analyzer.two_stage = copy.deepcopy(two_stage)

        # Stiffness / damping overrides on the analyzer instance
        for attr, val in attr_overrides.items():
            setattr(analyzer, attr, val)
        if any(k in attr_overrides for k in ("k_bolt", "k_member")):
            analyzer.recompute_k_system()

        # Friction split overrides (fields already exist on FrictionEvolutionParams)
        for attr, val in friction_overrides.items():
            if hasattr(analyzer.friction, attr):
                setattr(analyzer.friction, attr, val)

        # Friction ratios are applied as multiples of the (post-override) mu_initial.
        # Done after mu_override propagated through the analyzer constructor.
        if friction_ratio_overrides and hasattr(analyzer, "friction"):
            mu_init = getattr(analyzer.friction, "mu_initial", None)
            if mu_init and mu_init > 0:
                for fld, ratio in friction_ratio_overrides.items():
                    if hasattr(analyzer.friction, fld):
                        setattr(analyzer.friction, fld, mu_init * ratio)

        result = analyzer.run_analysis(
            preload_initial=self.preload_initial,
            F_transverse=self.F_transverse,
            n_cycles=self.n_cycles,
            output_interval=max(1, self.n_cycles // 500),
        )
        sim_cycle = np.asarray(result.cycles, dtype=float)
        sim_ratio = np.asarray(result.preload_ratio, dtype=float)
        return sim_cycle, sim_ratio

    def _simulate_v2(self, real: dict) -> Tuple[np.ndarray, np.ndarray]:
        """Non-linear simulation via DynamicStiffnessAnalyzer. Candidate params
        target 'jm.<tuner>' (JointMaterial multipliers)."""
        tuners = {}
        for p in self.params:
            if p.target.startswith("jm."):
                tuners[p.target.split(".", 1)[1]] = real[p.name]
        return simulate_v2_curve(
            self.model, tuners, self.n_cycles, self.control_mode,
            F0=self.preload_initial, F_amp=self.F_amp,
            theta=self.theta, freq=self.freq)
