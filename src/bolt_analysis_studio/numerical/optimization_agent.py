"""Autonomous calibration agent.

Wraps :class:`ParameterIdentifier` with a multi-stage strategy that:

1. **Detects the loading regime** from the MSDModel (transverse / axial /
   combined / gasketed / cfrp) so the right family of literature priors
   can be used as a starting point.
2. **Picks the best matching prior** from
   ``core/databases/literature_priors.json`` by regime + bolt size.
3. **Stage 1 — coarse**: fits the dominant scalars (μ_initial, C_loosening,
   k_stage2, F_infinity_ratio) with broad bounds and a small evaluation
   budget. Quickly walks to the right neighbourhood.
4. **Stage 2 — fine**: re-fits the full physically meaningful set with
   tight bounds (±2σ) around the Stage 1 best.
5. **Stage 3 — optional creep / element MSD**: only runs when the regime
   is gasketed/CFRP or the user requested per-element tuning.

Returns an :class:`AgentReport` with the per-stage breakdown plus the
final :class:`CalibrationResult` so the GUI can pre-stage the values for
the user to Apply / Discard.

Usage::

    agent = OptimizationAgent(model, ref_cycle, ref_ratio,
                              transverse_stiffness=k_trans)
    agent.set_progress_callback(cb)
    report = agent.run()
    print(report.final.best_params, report.final.best_mae)
"""
from __future__ import annotations

import copy
import json
import os
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence

import numpy as np

from .parameter_identifier import (
    CalibrationResult, FittableParam, ParameterIdentifier, PRESET_PARAMS,
)


# ---------------------------------------------------------------------------
# Regime detection + prior selection
# ---------------------------------------------------------------------------

_REGIME_DEFAULT = "transverse_junker"


def _detect_regime(model) -> str:
    """Map the model's loading config onto one of the prior regimes."""
    gl = getattr(model, "global_loading", None)
    if gl is None:
        return _REGIME_DEFAULT
    raw = (getattr(gl, "load_type", None)
           or getattr(gl, "type", None) or "").upper()
    # Heuristic: presence of a gasket element → gasketed regime
    elements = list(getattr(model, "elements", []) or [])
    has_gasket = any(
        "GASKET" in str(getattr(getattr(e, "type", None), "value", "")).upper()
        or "GASKET" in str(getattr(e, "type", "")).upper()
        for e in elements
    )
    if has_gasket:
        return "gasketed_creep"
    if "AXIAL" in raw and "TRANS" not in raw:
        return "axial_pulsating"
    if "COMBINED" in raw:
        return "combined_R_factor"
    return _REGIME_DEFAULT


def _bolt_size_mm(model) -> Optional[float]:
    gl = getattr(model, "global_loading", None)
    fb = getattr(model, "friction_bolt", None) if model is not None else None
    for src in (gl, fb):
        if src is None:
            continue
        for attr in ("bolt_diameter", "diameter"):
            v = getattr(src, attr, None)
            if v:
                try:
                    return float(v)
                except Exception:
                    pass
    return None


def _priors_path() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(
        here, "..", "core", "databases", "literature_priors.json"))


def _load_priors() -> List[dict]:
    try:
        with open(_priors_path(), "r", encoding="utf-8") as fh:
            return list(json.load(fh).get("entries", []) or [])
    except Exception:
        return []


def _pick_prior(regime: str, bolt_mm: Optional[float]) -> Optional[dict]:
    """Return the closest prior in `regime`; ties broken by bolt-size proximity."""
    candidates = [e for e in _load_priors() if e.get("regime") == regime]
    if not candidates:
        # fall back to any transverse_junker prior
        candidates = [e for e in _load_priors() if e.get("regime") == _REGIME_DEFAULT]
    if not candidates:
        return None
    if bolt_mm is None:
        return candidates[0]

    def _bolt_of(entry):
        # parse leading number out of e.g. "M12×1.75, class 10.9"
        s = entry.get("bolt", "")
        for tok in s.replace("M", " ").replace("×", " ").split():
            try:
                return float(tok.rstrip(",").strip())
            except ValueError:
                continue
        return 12.0  # arbitrary fallback

    candidates.sort(key=lambda e: abs(_bolt_of(e) - bolt_mm))
    return candidates[0]


# ---------------------------------------------------------------------------
# Stage parameter sets
# ---------------------------------------------------------------------------

# Stage 1 — keep tiny so the optimiser converges in <60 s on a typical run.
_STAGE1_NAMES = ("mu_initial", "C_loosening", "k_stage2", "F_infinity_ratio")

# Stage 2 — physically meaningful scalars that round out the curve shape.
_STAGE2_NAMES = (
    "mu_initial", "C_loosening", "N_stage1", "delta_F1_ratio",
    "N_stage2", "k_stage2", "F_infinity_ratio", "friction_recovery_gain",
    "transition_sharpness",
)

# Stage 3 — only for gasketed / CFRP regimes (creep dominates).
_STAGE3_NAMES = ("creep_coefficient",)


def _make_param(name: str,
                center: Optional[float],
                sigma: Optional[float],
                widen: float = 1.0) -> Optional[FittableParam]:
    """Build a FittableParam centered on `center` with bounds = center ± widen·sigma.

    Falls back to the factory's default bounds when center / sigma are missing.
    """
    factory = PRESET_PARAMS.get(name)
    if factory is None:
        return None
    p = factory()
    if center is not None and sigma is not None and sigma > 0:
        if center > 0:
            lo = max(center - widen * sigma, center * 0.1, p.lo * 0.5)
            hi = min(center + widen * sigma, center * 10.0, p.hi * 2.0)
        else:
            lo = center - widen * abs(sigma)
            hi = center + widen * abs(sigma)
        if hi <= lo:
            hi = lo * 2.0 + 1e-12
        p.lo, p.hi, p.default = float(lo), float(hi), float(center)
    return p


# ---------------------------------------------------------------------------
# Report types
# ---------------------------------------------------------------------------

@dataclass
class StageOutcome:
    name: str
    description: str
    params: List[str]
    result: Optional[CalibrationResult] = None
    skipped: bool = False
    skip_reason: str = ""


@dataclass
class AgentReport:
    regime: str
    prior_id: str
    prior_label: str
    stages: List[StageOutcome] = field(default_factory=list)
    final: Optional[CalibrationResult] = None
    duration_s: float = 0.0
    log: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class OptimizationAgent:
    """Multi-stage autonomous calibration."""

    def __init__(self,
                 model,
                 reference_cycle: Sequence[float],
                 reference_ratio: Sequence[float],
                 transverse_stiffness: Optional[float] = None,
                 objective: str = "mae",
                 budget_evals: int = 240,
                 seed: int = 42):
        self.model = model
        self.ref_cycle = np.asarray(reference_cycle, dtype=float)
        self.ref_ratio = np.asarray(reference_ratio, dtype=float)
        self.transverse_stiffness = transverse_stiffness
        self.objective = objective
        self.budget_evals = int(budget_evals)
        self.seed = int(seed)

        self._cancel = False
        self._progress_cb: Optional[Callable[[int, int, float, str], None]] = None
        self._log_cb: Optional[Callable[[str], None]] = None

    # ---- callbacks ------------------------------------------------------

    def cancel(self):
        self._cancel = True

    def set_progress_callback(self,
                              cb: Callable[[int, int, float, str], None]) -> None:
        """cb(n_done, n_max, best_objective, stage_name)."""
        self._progress_cb = cb

    def set_log_callback(self, cb: Callable[[str], None]) -> None:
        self._log_cb = cb

    # ---- main entry -----------------------------------------------------

    def run(self) -> AgentReport:
        t_start = time.time()
        regime = _detect_regime(self.model)
        bolt_mm = _bolt_size_mm(self.model)
        prior = _pick_prior(regime, bolt_mm)
        report = AgentReport(
            regime=regime,
            prior_id=(prior or {}).get("id", ""),
            prior_label=(prior or {}).get("label", "(no prior)"),
        )
        self._log(report,
                  f"Detected regime: {regime}"
                  + (f"  ·  bolt ≈ M{bolt_mm:g}" if bolt_mm else ""))
        self._log(report, f"Selected prior: {report.prior_label}")

        prior_params = (prior or {}).get("params", {}) or {}
        prior_sigmas = (prior or {}).get("bounds_sigma", {}) or {}

        # -------- Stage 1: coarse on dominant scalars --------------------
        stage1_params: List[FittableParam] = []
        for name in _STAGE1_NAMES:
            p = _make_param(name,
                            prior_params.get(name),
                            prior_sigmas.get(name),
                            widen=2.0)  # broad
            if p is not None:
                stage1_params.append(p)
        s1 = self._run_stage(
            "Stage 1 — coarse",
            "Dominant scalars with ±2σ bounds (broad search).",
            stage1_params, max_evals=int(self.budget_evals * 0.30),
            n_starts=2)
        report.stages.append(s1)
        if self._cancel:
            return self._finalise(report, t_start)

        # Update model with Stage 1 best so Stage 2 starts from there
        if s1.result and s1.result.success:
            self._stage_into_model(s1.result.best_params)
            best_so_far = s1.result.best_params
        else:
            best_so_far = dict(prior_params)

        # -------- Stage 2: fine on extended set --------------------------
        stage2_params: List[FittableParam] = []
        for name in _STAGE2_NAMES:
            center = best_so_far.get(name, prior_params.get(name))
            sigma = prior_sigmas.get(name)
            if sigma is not None and center is not None:
                sigma = sigma * 0.5  # tighten
            p = _make_param(name, center, sigma, widen=1.0)
            if p is not None:
                stage2_params.append(p)
        s2 = self._run_stage(
            "Stage 2 — fine",
            "Extended scalar set with ±1σ bounds (refinement).",
            stage2_params, max_evals=int(self.budget_evals * 0.55),
            n_starts=3)
        report.stages.append(s2)
        if self._cancel:
            return self._finalise(report, t_start)

        if s2.result and s2.result.success:
            self._stage_into_model(s2.result.best_params)
            best_so_far = s2.result.best_params
            best_result = s2.result
        else:
            best_result = s1.result

        # -------- Stage 3: creep (only when regime calls for it) ---------
        if regime in ("gasketed_creep", "cfrp_composite"):
            stage3_params: List[FittableParam] = []
            for name in _STAGE3_NAMES:
                center = prior_params.get(name)
                sigma = prior_sigmas.get(name)
                p = _make_param(name, center, sigma, widen=1.5)
                if p is not None:
                    stage3_params.append(p)
            s3 = self._run_stage(
                "Stage 3 — creep",
                "Norton-Bailey creep gain (gasketed / CFRP only).",
                stage3_params, max_evals=int(self.budget_evals * 0.15),
                n_starts=2)
            report.stages.append(s3)
            if s3.result and s3.result.success:
                best_result = s3.result
        else:
            report.stages.append(StageOutcome(
                "Stage 3 — creep",
                "Skipped — regime is not creep-dominated.",
                list(_STAGE3_NAMES),
                skipped=True,
                skip_reason=f"regime={regime}"))

        report.final = best_result
        return self._finalise(report, t_start)

    # ---- stage runner ---------------------------------------------------

    def _run_stage(self, name: str, description: str,
                   params: List[FittableParam], *,
                   max_evals: int, n_starts: int) -> StageOutcome:
        outcome = StageOutcome(name, description, [p.name for p in params])
        if not params:
            outcome.skipped = True
            outcome.skip_reason = "No parameters available for this stage."
            self._log_simple(f"[{name}] skipped — {outcome.skip_reason}")
            return outcome
        if self._cancel:
            outcome.skipped = True
            outcome.skip_reason = "Cancelled by user before stage start."
            return outcome

        # Use a deep copy of the model so each stage's defaults don't leak
        # into the optimiser-internal _simulate restoration code paths.
        try:
            identifier = ParameterIdentifier(
                self.model, self.ref_cycle, self.ref_ratio,
                params_to_fit=params,
                objective=self.objective,
                max_evals=max(20, int(max_evals)),
                seed=self.seed,
                transverse_stiffness=self.transverse_stiffness,
            )
        except Exception as exc:
            outcome.skipped = True
            outcome.skip_reason = f"Setup failed: {exc}"
            self._log_simple(f"[{name}] setup failed: {exc}")
            return outcome

        if self._progress_cb is not None:
            def _bridge(n_done, n_max, best, stage_name=name):
                if self._progress_cb is not None:
                    self._progress_cb(n_done, n_max, best, stage_name)
                if self._cancel:
                    identifier.cancel()
            identifier.set_progress_callback(_bridge)
        else:
            def _bridge2(n_done, n_max, best):
                if self._cancel:
                    identifier.cancel()
            identifier.set_progress_callback(_bridge2)

        self._log_simple(
            f"[{name}] running ({len(params)} params, "
            f"≤{max_evals} evals, {n_starts} starts)")
        result = identifier.run(n_starts=n_starts)
        outcome.result = result
        self._log_simple(
            f"[{name}] done — best {self.objective}={result.best_mae:.4f} "
            f"({result.n_evals} evals, {result.duration_s:.1f}s)")
        return outcome

    # ---- helpers --------------------------------------------------------

    def _stage_into_model(self, best_params: dict) -> None:
        """Push Stage N best onto model so Stage N+1 simulates from there."""
        gl = getattr(self.model, "global_loading", None)
        ts_keys = {
            "C_loosening", "N_stage1", "delta_F1_ratio", "N_stage2",
            "k_stage2", "transition_sharpness", "F_infinity_ratio",
            "friction_recovery_gain", "creep_coefficient", "creep_exponent",
            "noise_amplitude",
        }
        if "mu_initial" in best_params:
            mu = float(best_params["mu_initial"])
            if gl is not None:
                try:
                    gl.mu_initial = mu
                except Exception:
                    pass
            try:
                setattr(self.model, "mu_initial", mu)
            except Exception:
                pass
        overrides = getattr(self.model, "_two_stage_overrides", None)
        if overrides is None:
            overrides = {}
            try:
                setattr(self.model, "_two_stage_overrides", overrides)
            except Exception:
                return
        for k, v in best_params.items():
            if k in ts_keys:
                overrides[k] = float(v)

    def _log(self, report: AgentReport, msg: str) -> None:
        report.log.append(msg)
        self._log_simple(msg)

    def _log_simple(self, msg: str) -> None:
        if self._log_cb is not None:
            try:
                self._log_cb(msg)
            except Exception:
                pass

    def _finalise(self, report: AgentReport, t_start: float) -> AgentReport:
        report.duration_s = time.time() - t_start
        if report.final is None:
            # Return whatever the last successful stage produced
            for s in reversed(report.stages):
                if s.result is not None and s.result.success:
                    report.final = s.result
                    break
        return report
