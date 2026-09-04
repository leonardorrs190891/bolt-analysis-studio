"""
Solver Worker Module
QThread-based solver execution for Bolt Analysis Studio v4.0

Prof. Leonardo Rosa Ribeiro da Silva, PhD
January 2026

Provides background execution of:
- Preload loss analysis (cycle-based loosening)
- Time integration (dynamic analysis)
- Modal analysis

All computations run in a separate thread to keep the GUI responsive.
"""

import numpy as np
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import time as _time
import uuid as _uuid

from PyQt6.QtCore import QObject, QThread, pyqtSignal

# Import numerical models
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from bolt_analysis_studio.core.models.model import MSDModel
from bolt_analysis_studio.numerical.preload_loss_models import (
    BoltParameters, JointParameters, PreloadConditions, LoadingType,
    SingleExponentialModel, DoubleExponentialModel, StretchedExponentialModel,
    VDI2230EmbeddingModel
)
from bolt_analysis_studio.numerical.time_integration import (
    TimeParams, NewmarkParams, HHTParams,
    NewmarkIntegrator, HHTIntegrator, CentralDifferenceIntegrator,
    ModalSuperposition, RungeKutta4, AdaptiveRK45,
    IntegrationResult, create_integrator, IntegratorType,
    harmonic_force, biased_harmonic_force, step_force, pulse_force
)
from bolt_analysis_studio.core.app_state import (
    PreloadAnalysisResult, TimeIntegrationResult, AnalysisResult,
    CoupledLooseningResult, AnalysisAudit
)
from bolt_analysis_studio.numerical.coupled_loosening_analyzer import (
    CoupledLooseningAnalyzer, LooseningResults,
    FrictionEvolutionParams, WearModelParams,
    ThreadGeometryParams, BearingGeometryParams,
    create_m16_analyzer, create_analyzer_from_bolt_size,
    create_analyzer_from_msd_model  # NEW: MSD model integration
)


# =============================================================================
# CONFIGURATION DATACLASSES
# =============================================================================

@dataclass
class PreloadAnalysisConfig:
    """Configuration for preload loss analysis."""
    # Cycle parameters
    n_cycles: int = 10000
    n_points: int = 500

    # Initial preload (0 = compute from % yield at runtime)
    initial_preload: float = 0.0  # N
    preload_percent_yield: float = 70.0

    # Selected models to run
    selected_models: List[str] = field(default_factory=lambda: [
        "single_exponential",
        "double_exponential",
        "stretched_exponential",
        "vdi2230_embedding"
    ])

    # Bolt parameters
    bolt_diameter: float = 12.0  # mm
    bolt_pitch: float = 1.75  # mm
    bolt_length: float = 60.0  # mm
    thread_length: float = 25.0  # mm

    # Joint parameters
    mu_thread: float = 0.12
    mu_bearing: float = 0.14
    bolt_stiffness: float = 5e5  # N/mm
    member_stiffness: float = 1.5e6  # N/mm

    # Loading parameters
    loading_type: str = "axial"
    displacement_amplitude: float = 0.5  # mm
    frequency: float = 25.0  # Hz

    # Model-specific parameters
    lambda_decay: float = 0.005  # Single exponential
    F_inf_ratio: float = 0.6    # Plateau ratio
    N0: float = 500.0           # Stretched exp characteristic cycles
    beta: float = 0.5           # Stretching exponent


@dataclass
class TimeIntegrationConfig:
    """Configuration for time integration analysis."""
    # Time parameters
    t_start: float = 0.0
    t_end: float = 1.0
    dt: float = 0.001
    output_interval: int = 1

    # Integration method
    method: str = "newmark"  # newmark, hht, central_diff, modal, rk4

    # Newmark parameters
    newmark_beta: float = 0.25
    newmark_gamma: float = 0.5

    # HHT parameters
    hht_alpha: float = -0.05

    # Convergence tolerances (for iterative methods)
    force_tolerance: float = 1e-6
    displacement_tolerance: float = 1e-8
    max_iterations: int = 20

    # Modal superposition
    n_modes: int = 10

    # Loading
    load_type: str = "harmonic"  # harmonic, step, pulse, custom
    load_amplitude: float = 10000.0  # N
    load_frequency: float = 25.0  # Hz
    load_dof: int = 0  # DOF where load is applied

    # VDI 2230 / Phase-A load factors
    R_factor: float = 0.0              # Stress ratio R = F_min/F_max (0=zero-to-max, -1=fully reversed)
    dynamic_factor: float = 1.0        # Dynamic amplification φ (>1 for vibration/shock)
    load_waveform: str = "sinusoidal"  # Waveform: "sinusoidal" | "square" | "sawtooth"
    Phi_load: Optional[float] = None   # Force-introduction factor (None = auto from model geometry)
    n_load_plane: float = 0.5          # Load-plane factor n ∈ [0, 1]

    # Initial conditions
    u0: Optional[np.ndarray] = None
    v0: Optional[np.ndarray] = None


@dataclass
class CoupledLooseningConfig:
    """Configuration for coupled friction-wear-loosening analysis.

    For large cycle counts (up to 5 million), use sample_interval to reduce
    output points while still computing all cycles internally.
    """
    # Cycle parameters
    n_cycles: int = 2000
    output_interval: int = 1  # Deprecated, use sample_interval

    # Sampling for large cycle counts
    sample_interval: int = 1  # Store result every N cycles (1 = every cycle)
    target_output_points: int = 10000  # Target number of output points
    sample_percentage: float = 1.0  # Alternative: sample this % of cycles

    # Initial conditions (0 = compute from % yield at runtime)
    initial_preload: float = 0.0  # N
    transverse_force: float = 8000.0  # N - drives Junker loosening
    temperature: float = 20.0  # Celsius

    # Thread geometry (metric)
    bolt_diameter_mm: float = 16.0
    pitch_mm: float = 2.0
    grip_length_mm: float = 48.0  # 3 * diameter default
    flank_angle_deg: float = 30.0
    num_engaged_threads: int = 8

    # Bearing geometry
    bearing_inner_diameter_mm: float = 17.0
    bearing_outer_diameter_mm: float = 24.0

    # Friction parameters (three-phase model)
    mu_initial: float = 0.12
    mu_peak: float = 0.15
    mu_steady: float = 0.08
    mu_minimum: float = 0.03
    N1_running_in: int = 50
    N2_transition: int = 200
    N3_steady: int = 2000

    # Wear parameters (Archard model)
    K_archard: float = 1e-6
    K_running_in: float = 5e-6
    K_steady: float = 1e-6
    hardness: float = 2e9  # Pa
    contact_area: float = 1e-4  # m^2

    # Stiffness
    k_bolt: float = 500e6  # N/m
    k_member: float = 1500e6  # N/m

    # Degradation effects
    wear_degradation_rate: float = 0.01  # mu reduction per um wear
    temperature_factor: float = 0.001  # mu reduction per degree above 20C

    # Use preset bolt size
    use_preset: bool = True  # If True, use M16 preset
    lubricated: bool = True

    # VDI 2230 / Phase-A load factors
    R_factor: float = 0.0              # Stress ratio R = F_min/F_max
    dynamic_factor: float = 1.0        # Dynamic amplification φ
    load_waveform: str = "sinusoidal"  # Waveform: "sinusoidal" | "square" | "sawtooth"
    Phi_load: Optional[float] = None   # Force-introduction factor (None = auto)
    n_load_plane: float = 0.5          # Load-plane factor n ∈ [0, 1]

    # Pai-Hess slip onset correction (Phase C)
    slip_onset_factor: float = 0.46    # Fraction of µ×N at which gross slip begins

    # NEW: Use MSD Model (overrides use_preset)
    use_msd_model: bool = False  # If True, extract parameters from MSD model


@dataclass
class AnalysisConfig:
    """Combined analysis configuration."""
    # Analysis type: "preload", "time_integration", "modal", "static",
    #                "coupled_loosening", or "all" to run all analyses
    analysis_type: str = "all"

    # Run ALL analyses (comprehensive analysis)
    run_all: bool = True

    # Individual analysis configs
    preload_config: PreloadAnalysisConfig = field(default_factory=PreloadAnalysisConfig)
    time_config: TimeIntegrationConfig = field(default_factory=TimeIntegrationConfig)
    coupled_loosening_config: CoupledLooseningConfig = field(default_factory=CoupledLooseningConfig)


# =============================================================================
# SOLVER WORKER
# =============================================================================

# Structured error catalogue for solver diagnostics (7.2)
SOLVER_ERRORS: Dict[str, str] = {
    "singular matrix": (
        "The stiffness matrix is singular. "
        "Check that the model has at least one GROUND element and all elements are connected."
    ),
    "nan in solution": (
        "NaN detected in time integration. "
        "Reduce dt or switch to an implicit method (Newmark-β or HHT-α)."
    ),
    "negative preload": (
        "Computed preload became negative. "
        "Increase the initial preload or reduce the loading amplitude."
    ),
    "convergence failed": (
        "Newton-Raphson did not converge. "
        "Reduce dt or loosen the solver tolerance."
    ),
    "zero degrees of freedom": (
        "Model has no degrees of freedom. "
        "Add elements to the MSD model before running analysis."
    ),
    "no elements": (
        "Model contains no elements. "
        "Build a model in the MSD Builder tab first."
    ),
    "eigenvalue": (
        "Eigenvalue computation failed. "
        "Check that the mass and stiffness matrices are positive-definite."
    ),
    "memory": (
        "Out of memory during analysis. "
        "Reduce n_cycles or increase sample_interval to limit output size."
    ),
}


def coerce_v2_overrides(ov, valid):
    """Filtra ``_v2_tuner_overrides`` p/ campos validos de JointMaterial,
    type-aware (spec 2026-07-08 — adocao das formas validadas no Run):
      - campo str  (slip_regime_mode, loose_torsion_mode, conform_driver, k_tr_mode) -> str
      - campo bool (couple_famp_slip, fatigue_enabled) -> bool  (antes virava float 0/1;
        funcionalmente truthy, mas agora tipado)
      - campo numerico -> float
    Chaves desconhecidas sao descartadas (nunca quebram o Run). ``valid`` =
    ``JointMaterial.__dataclass_fields__`` (passado pelo caller, que importa
    JointMaterial localmente)."""
    out = {}
    if not isinstance(ov, dict):
        return out
    for k, v in ov.items():
        if k not in valid:
            continue
        default = valid[k].default
        if isinstance(default, bool):          # bool ANTES de numerico (bool subclasse de int)
            out[k] = bool(v)
        elif isinstance(default, str):
            out[k] = str(v)
        else:
            try:
                out[k] = float(v)
            except (TypeError, ValueError):
                pass
    return out


def build_v2_material(overrides, F0: float, A_contact: float,
                      pct_yield: float = 70.0):
    """JointMaterial do Run V2: bloco `shared` canonico + overrides do modelo.

    Extraida de `_compute_v2_history` em 2026-09-03 para ser FONTE UNICA. O
    otimizador de parametros montava o material com `JointMaterial(**tuners)`,
    isto e', so' com os overrides e sem o bloco compartilhado nem o
    `p_ref_conform` — que e' calculado por Run e nao existe em nenhum arquivo.
    Resultado medido: para o mesmo modelo, a curva do otimizador divergia da
    curva do Run (5,2e-4 em F/F0 no LU2024, crescente com o ciclo). Ajuste
    medido num motor que nao e' o que roda depois nao quer dizer nada, e a
    diferenca era pequena o bastante para nunca ser notada.

    A extracao e' de comportamento identico bit a bit — conferido nos 6 casos
    de `tests/test_v2_material_unica.py` antes e depois.

    Parametros
    ----------
    overrides : dict | None    `model._v2_tuner_overrides`
    F0 : float                 pre-carga do Run [N]
    A_contact : float          area de contato da geometria EFETIVA [m^2]
    pct_yield : float          % do escoamento do Run (gate de sobretorque)
    """
    from bolt_analysis_studio.calibration.profiles import load_shared_material
    from bolt_analysis_studio.calibration.tuner_shim import (
        translate_legacy_tuners)
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        JointMaterial)

    # Conformacao dependente de pressao ADOTADA (2026-07-04, bloco canonico) —
    # LIGADA POR DEFAULT no Run, driver auto-limitante 'effective'. Eh
    # PRESSURE-GATED: p_ref = pre-carga nominal (70% do escoamento) deste
    # parafuso, entao o SOBRETORQUE (pct acima de 70%) excita mais o plato.
    # Como p e p_ref dividem pelo mesmo A_contact, o gate reduz a (p/p_ref) =
    # pct/70 (independe de A_contact/A_s/proof) => a SEPARACAO por sobretorque
    # vale em qualquer F0. W_conf_ref=7671 eh o valor da âncora interna por-par (default; sem
    # ancora p/ outros pares — MODEL_LEGITIMACY §4.9 strand 3). Overrides
    # explicitos em _v2_tuner_overrides VENCEM; W_conf_ref=0 desliga.
    # CAVEAT DE ESCALA (medido): a inercia no nominal so vale ~na escala da âncora interna
    # (F0~50 kN => delta~0.014); em F0 alto o trabalho de slip (proporcional a
    # F0) enche o W_conf_ref FIXO e o gate morde tb no nominal (F0=120 kN =>
    # delta~0.09). Consequencia de "aplica W_conf_ref âncora interna por-par a qualquer
    # junta" (o flag aprovado): calibrado na escala da âncora interna, aproximado fora dela.
    pct = float(pct_yield or 70.0)
    if pct <= 0.0:
        pct = 70.0
    rated = 0.7 * (float(F0) / (pct / 100.0))   # 0.7 * pre-carga de escoamento
    # ESTAGIO B Fase 2 (spec 2026-07-02 §3.3, plano 2026-07-08 §3): o Run le as
    # constantes fisicas do bloco `shared` canonico via o LOADER UNICO em vez
    # da copia hardcoded — "o bloco shared vira o que a GUI le". Fallbacks
    # preservam os valores antigos se o arquivo/bloco faltar. p_ref_conform
    # segue COMPUTADO (fisica por-run, roadmap 11f: gate = pct/70); emb_depth e
    # input por junta (excluido no loader). Overrides explicitos VENCEM.
    conf_defaults = load_shared_material()
    conf_defaults.setdefault("W_conf_ref", 7671.0)
    conf_defaults.setdefault("conform_pressure_exp", 2.0)
    conf_defaults["conform_driver"] = "effective"
    conf_defaults["p_ref_conform"] = max(rated, 1.0) / float(A_contact)
    # ESTAGIO B Fase 3 (spec §3.3): SHIM na fronteira de consumo — tuners
    # legados (k_emb_scale, k_wear_scale_tr, ...) sao traduzidos p/ constantes
    # fisicas AQUI (uma vez), multiplicando sobre a base do shared. Fold exato
    # p/ emb/creep/Phi_tr/damage; ratio-exato p/ wear dano-off. Depois coerce a
    # campos validos de JointMaterial.
    ov_folded = (translate_legacy_tuners(dict(overrides), base=conf_defaults)
                 if overrides else {})
    tuners = coerce_v2_overrides(ov_folded, JointMaterial.__dataclass_fields__)
    return JointMaterial(**{**conf_defaults, **tuners})


def _v2_cycle_cap(overrides) -> int:
    """Teto de ciclos do bloco V2 do Run (resolucao 2026-07-28, delegada).

    100k e' o teto historico (custo por-ciclo na GUI). Sobe para 400k SOMENTE
    quando o override pede fadiga com RAMPA (fatigue_enabled e fat_ramp_D_on<1)
    — as curvas de fratura longas do Liu 2025 precisam de 250k/330k ciclos, e
    truncar cortaria exatamente o estagio que a config existe para mostrar. A
    memoria que motivava o teto foi resolvida junto (poda da history no loop:
    o engine nunca a le; o Run usa o snap retornado). Valores invalidos caem
    no teto conservador.
    """
    ov = overrides or {}
    try:
        ramp = bool(ov.get("fatigue_enabled")) and \
            float(ov.get("fat_ramp_D_on", 1.0)) < 1.0
    except (TypeError, ValueError):
        ramp = False
    return 400_000 if ramp else 100_000


class SolverWorker(QObject):
    """
    Worker object for running analysis computations in a background thread.

    Signals:
        progress: (int, str) - Progress percentage and status message
        finished: (object) - Analysis result when complete
        error: (str) - Error message if analysis fails
    """

    progress = pyqtSignal(int, str)      # percent, message
    finished = pyqtSignal(object)         # AnalysisResult
    error = pyqtSignal(str)               # error message
    log = pyqtSignal(str)                 # log message
    live_state = pyqtSignal(dict)         # live contact state during loosening analysis

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = False
        self._is_paused = False
        self._stop_requested = False
        self._current_model = None  # Store current MSD model for integration

    # -------------------------------------------------------------------------
    # Control methods
    # -------------------------------------------------------------------------

    def request_stop(self):
        """Request the solver to stop."""
        self._stop_requested = True

    def request_pause(self):
        """Request the solver to pause."""
        self._is_paused = True

    def request_resume(self):
        """Resume from pause."""
        self._is_paused = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    def _check_stop(self) -> bool:
        """Check if stop was requested."""
        if self._stop_requested:
            self.log.emit("Analysis stopped by user")
            return True
        return False

    def _wait_if_paused(self):
        """Wait while paused."""
        while self._is_paused and not self._stop_requested:
            QThread.msleep(100)

    def _categorize_error(self, exc: Exception) -> tuple:
        """Return (short_key, remedy_str) for a solver exception (7.2)."""
        msg = str(exc).lower()
        for key, remedy in SOLVER_ERRORS.items():
            if key in msg:
                return key, remedy
        return "unknown error", str(exc)

    def _preflight_check(self, model, config) -> List[str]:
        """
        Physics sanity checks before dispatching an analysis (7.1).
        Returns a (possibly empty) list of warning strings.
        """
        warnings: List[str] = []
        if model is None:
            return warnings

        loading = getattr(model, 'global_loading', None)

        # 1. Loading frequency near fundamental natural frequency (resonance risk)
        try:
            freqs, _ = model.compute_natural_frequencies()
            if len(freqs) > 0:
                fn = float(freqs[0])
                freq = float(getattr(loading, 'frequency', 0.0) or 0.0)
                if fn > 0 and freq > 0:
                    if freq > 0.8 * fn:
                        warnings.append(
                            f"Loading frequency ({freq:.1f} Hz) is near the fundamental "
                            f"natural frequency (fn = {fn:.1f} Hz). "
                            "Risk of resonance / numerical instability."
                        )
        except Exception:
            pass  # Modal analysis not critical for pre-flight

        if loading is not None:
            # 2. Preload over 90% yield (VDI 2230 limit)
            pct = float(getattr(loading, 'preload_percent_yield', 0.0) or 0.0)
            if pct > 90:
                warnings.append(
                    f"Preload at {pct:.0f}% yield exceeds the VDI 2230 "
                    "recommended maximum of 90%."
                )

            # 3. Time-step coarseness check
            time_cfg = getattr(config, 'time_config', None)
            freq = float(getattr(loading, 'frequency', 0.0) or 0.0)
            if time_cfg and freq > 0:
                T = 1.0 / freq
                dt = float(getattr(time_cfg, 'dt', 0.0) or 0.0)
                if dt > 0 and dt > T / 10:
                    warnings.append(
                        f"Time step dt = {dt:.4g} s gives fewer than 10 steps/cycle "
                        f"at {freq:.1f} Hz. Consider dt < {T/20:.4g} s."
                    )

            # 4. Friction coefficient outside typical bolted-joint range
            mu = (float(getattr(loading, 'mu_initial', 0.0) or 0.0)
                  or float(getattr(model, 'mu_initial', 0.0) or 0.0))
            if 0 < mu < 0.05 or mu > 0.40:
                warnings.append(
                    f"Friction coefficient μ = {mu:.3f} is outside the typical "
                    "range [0.05, 0.40] for bolted joints."
                )

        return warnings

    # -------------------------------------------------------------------------
    # Main run method
    # -------------------------------------------------------------------------

    def run_analysis(self, model: Optional[MSDModel], config: AnalysisConfig):
        """
        Run the configured analysis.

        Args:
            model: MSDModel (may be None for preload analysis)
            config: AnalysisConfig with analysis settings
        """
        self._is_running = True
        self._stop_requested = False
        self._is_paused = False
        self._current_model = model  # Store model for MSD integration

        try:
            self.log.emit(f"Starting {config.analysis_type} analysis...")
            self.progress.emit(0, "Initializing...")

            # Physics sanity checks (7.1)
            pre_warnings = self._preflight_check(model, config)
            for w in pre_warnings:
                self.log.emit(f"[PRE-FLIGHT] ⚠ {w}")

            _t0 = _time.monotonic()
            _run_id = str(_uuid.uuid4())[:8]
            result = AnalysisResult(
                analysis_type=config.analysis_type,
                started=datetime.now().isoformat()
            )

            # Determine if we should run all analyses
            run_all = config.run_all or config.analysis_type == "all"

            if run_all:
                # Run ALL analyses for comprehensive results
                self.log.emit("Running comprehensive analysis (all types)...")

                # 1. Modal analysis first (if model available)
                if model is not None:
                    self.log.emit("1/5: Modal analysis...")
                    self.progress.emit(10, "Modal analysis...")
                    try:
                        freqs, modes = self._run_modal_analysis(model)
                        result.natural_frequencies = freqs.tolist()
                        result.mode_shapes = modes
                    except Exception as e:
                        self.log.emit(f"Modal analysis skipped: {e}")

                # 2. Static analysis (if model available)
                if model is not None:
                    self.log.emit("2/5: Static analysis...")
                    self.progress.emit(20, "Static analysis...")
                    try:
                        result.static_displacement = self._run_static_analysis(model, config.time_config)
                    except Exception as e:
                        self.log.emit(f"Static analysis skipped: {e}")

                # 3. Preload loss analysis
                self.log.emit("3/5: Preload loss analysis...")
                self.progress.emit(40, "Preload loss analysis...")
                try:
                    result.preload_result = self._run_preload_analysis(config.preload_config)
                except Exception as e:
                    self.log.emit(f"Preload analysis error: {e}")

                # 4. Coupled friction-wear-loosening analysis
                self.log.emit("4/5: Coupled loosening analysis...")
                self.progress.emit(60, "Coupled loosening analysis...")
                try:
                    result.coupled_loosening_result = self._run_coupled_loosening_analysis(
                        config.coupled_loosening_config
                    )
                except Exception as e:
                    self.log.emit(f"Coupled loosening analysis error: {e}")

                # 5. Time integration (if model available)
                if model is not None:
                    self.log.emit("5/5: Time integration...")
                    self.progress.emit(80, "Time integration...")
                    try:
                        result.time_result = self._run_time_integration(model, config.time_config)
                    except Exception as e:
                        self.log.emit(f"Time integration skipped: {e}")

                result.analysis_type = "all"

            elif config.analysis_type == "preload":
                result.preload_result = self._run_preload_analysis(config.preload_config)

            elif config.analysis_type == "time_integration":
                if model is None:
                    raise ValueError("Model required for time integration")
                result.time_result = self._run_time_integration(model, config.time_config)

            elif config.analysis_type == "modal":
                if model is None:
                    raise ValueError("Model required for modal analysis")
                freqs, modes = self._run_modal_analysis(model)
                result.natural_frequencies = freqs.tolist()
                result.mode_shapes = modes

            elif config.analysis_type == "static":
                if model is None:
                    raise ValueError("Model required for static analysis")
                result.static_displacement = self._run_static_analysis(model, config.time_config)

            elif config.analysis_type == "coupled_loosening":
                result.coupled_loosening_result = self._run_coupled_loosening_analysis(
                    config.coupled_loosening_config
                )

            else:
                raise ValueError(f"Unknown analysis type: {config.analysis_type}")

            result.completed = datetime.now().isoformat()

            # Build audit trail
            _n_dof = 0
            _n_elem = 0
            _method = getattr(config.time_config, 'method', 'n/a') if hasattr(config, 'time_config') else 'n/a'
            _n_cyc = getattr(config.coupled_loosening_config, 'n_cycles', 0) if hasattr(config, 'coupled_loosening_config') else 0
            if model is not None:
                try:
                    _n_elem = len(model.elements)
                    M, _, _ = model.assemble_matrices()
                    _n_dof = M.shape[0]
                except Exception:
                    pass
            result.audit = AnalysisAudit(
                run_id=_run_id,
                timestamp_start=result.started,
                timestamp_end=result.completed,
                duration_s=round(_time.monotonic() - _t0, 3),
                analysis_type=result.analysis_type,
                method=_method,
                n_cycles=_n_cyc,
                n_dof=_n_dof,
                n_elements=_n_elem,
                solver_version="4.0",
                preflight_warnings=pre_warnings,
            )
            self.log.emit(
                f"[INFO] Audit #{_run_id}: {result.analysis_type} — "
                f"{result.audit.duration_s:.1f}s, {_n_dof} DOF, {_n_elem} elements"
            )

            if not self._stop_requested:
                self.progress.emit(100, "Analysis complete")
                self.finished.emit(result)
            else:
                self.log.emit("Analysis was stopped")

        except Exception as e:
            _key, _remedy = self._categorize_error(e)
            self.log.emit(f"[ERROR] {type(e).__name__}: {e}")
            self.log.emit(f"[REMEDY] {_remedy}")
            self.error.emit(f"{type(e).__name__}: {e}\n\nSuggested fix: {_remedy}")

        finally:
            self._is_running = False

    # -------------------------------------------------------------------------
    # Preload Analysis
    # -------------------------------------------------------------------------

    def _run_preload_analysis(self, config: PreloadAnalysisConfig) -> PreloadAnalysisResult:
        """Run preload loss analysis with multiple models."""

        self.log.emit("Setting up preload loss models...")

        # Create parameter objects
        bolt = BoltParameters(
            diameter=config.bolt_diameter,
            pitch=config.bolt_pitch,
            length=config.bolt_length,
            thread_length=config.thread_length
        )

        joint = JointParameters(
            bolt_stiffness=config.bolt_stiffness,
            member_stiffness=config.member_stiffness,
            mu_thread=config.mu_thread,
            mu_bearing=config.mu_bearing
        )

        loading_type_map = {
            "axial": LoadingType.AXIAL,
            "transverse": LoadingType.TRANSVERSE,
            "combined": LoadingType.COMBINED,
            "torsional": LoadingType.TORSIONAL
        }

        conditions = PreloadConditions(
            initial_preload=config.initial_preload,
            yield_utilization=config.preload_percent_yield / 100.0,
            loading_type=loading_type_map.get(config.loading_type, LoadingType.AXIAL),
            displacement_amplitude=config.displacement_amplitude,
            frequency=config.frequency
        )

        # Cycle array
        N = np.linspace(0, config.n_cycles, config.n_points)

        # Run each selected model
        results = {}
        n_models = len(config.selected_models)

        for i, model_name in enumerate(config.selected_models):
            if self._check_stop():
                break

            self._wait_if_paused()

            progress = int(10 + 80 * i / n_models)
            self.progress.emit(progress, f"Running {model_name}...")
            self.log.emit(f"Computing {model_name} model...")

            try:
                if model_name == "single_exponential":
                    model = SingleExponentialModel(
                        bolt, joint, conditions,
                        lambda_decay=config.lambda_decay,
                        F_inf_ratio=config.F_inf_ratio
                    )
                    results[model_name] = model.normalized_preload(N)

                elif model_name == "double_exponential":
                    model = DoubleExponentialModel(
                        bolt, joint, conditions,
                        F_inf_ratio=config.F_inf_ratio
                    )
                    results[model_name] = model.normalized_preload(N)

                elif model_name == "stretched_exponential":
                    model = StretchedExponentialModel(
                        bolt, joint, conditions,
                        N0=config.N0,
                        beta=config.beta
                    )
                    results[model_name] = model.normalized_preload(N)

                elif model_name == "vdi2230_embedding":
                    model = VDI2230EmbeddingModel(
                        bolt, joint, conditions
                    )
                    results[model_name] = model.normalized_preload(N)

                else:
                    self.log.emit(f"Unknown model: {model_name}, skipping")

            except Exception as e:
                self.log.emit(f"Error in {model_name}: {e}")
                continue

        # Compute statistics
        final_ratios = [arr[-1] for arr in results.values() if len(arr) > 0]
        avg_final_ratio = np.mean(final_ratios) if final_ratios else 1.0

        # Find cycles to 50% loss (if applicable)
        cycles_to_50 = None
        for name, arr in results.items():
            if "exponential" in name:
                idx = np.where(arr <= 0.5)[0]
                if len(idx) > 0:
                    cycles_to_50 = N[idx[0]]
                    break

        self.progress.emit(95, "Finalizing results...")

        return PreloadAnalysisResult(
            cycles=N,
            results=results,
            final_preload_ratio=avg_final_ratio,
            preload_loss_percent=100.0 * (1.0 - avg_final_ratio),
            cycles_to_50_percent_loss=cycles_to_50,
            initial_preload=config.initial_preload,
            n_cycles=config.n_cycles,
            selected_models=list(results.keys())
        )

    # -------------------------------------------------------------------------
    # Time Integration Analysis
    # -------------------------------------------------------------------------

    def _run_time_integration(
        self,
        model: MSDModel,
        config: TimeIntegrationConfig
    ) -> TimeIntegrationResult:
        """Run time integration analysis."""

        self.log.emit("Assembling system matrices...")
        self.progress.emit(10, "Assembling matrices...")

        # Get matrices from model
        M, K, C = model.assemble_matrices()
        n_dof = M.shape[0]

        if n_dof == 0:
            raise ValueError("Model has no degrees of freedom")

        self.log.emit(f"System: {n_dof} DOF")
        self.log.emit(f"Mass matrix: {M.shape}")

        # Create time parameters
        time_params = TimeParams(
            t_start=config.t_start,
            t_end=config.t_end,
            dt=config.dt,
            output_interval=config.output_interval
        )

        # Create force function
        self.log.emit("Setting up loading...")
        self.progress.emit(20, "Setting up loading...")

        F_amplitude = np.zeros(n_dof)
        load_dof = min(config.load_dof, n_dof - 1)
        F_amplitude[load_dof] = config.load_amplitude

        if config.load_type == "harmonic":
            # Use biased_harmonic_force when VDI 2230 load factors are non-trivial
            _use_biased = (
                config.R_factor != 0.0
                or config.dynamic_factor != 1.0
                or config.load_waveform != "sinusoidal"
            )
            if _use_biased:
                # Convert R-ratio and amplitude to mean + alternating components
                # R = F_min/F_max, F_alt = F_amp/(1 - R)×(1 + R)/2  (exact VDI 2230 §5)
                _R = config.R_factor
                _alt = F_amplitude  # alternating amplitude
                _mean = _alt * (1.0 + _R) / (1.0 - _R) if _R != 1.0 else np.zeros_like(F_amplitude)
                F_func = biased_harmonic_force(
                    _mean, _alt, config.load_frequency,
                    waveform=config.load_waveform,
                    dynamic_factor=config.dynamic_factor
                )
            else:
                F_func = harmonic_force(F_amplitude, config.load_frequency)
        elif config.load_type == "step":
            F_func = step_force(F_amplitude, t_start=0.0, rise_time=0.01)
        elif config.load_type == "pulse":
            F_func = pulse_force(F_amplitude, t_start=0.0, duration=0.01)
        else:
            # Default to harmonic
            F_func = harmonic_force(F_amplitude, config.load_frequency)

        # Create integrator
        self.log.emit(f"Creating {config.method} integrator...")
        self.progress.emit(30, f"Creating {config.method} integrator...")

        if config.method == "newmark":
            params = NewmarkParams(beta=config.newmark_beta, gamma=config.newmark_gamma)
            integrator = NewmarkIntegrator(M, C, K, params)

        elif config.method == "hht":
            params = HHTParams(alpha=config.hht_alpha)
            integrator = HHTIntegrator(M, C, K, params)

        elif config.method == "central_diff":
            integrator = CentralDifferenceIntegrator(M, C, K)
            # Stability: dt must be < dt_critical for explicit Central Difference (7.3)
            dt_crit = integrator.get_critical_timestep()
            if dt_crit and config.dt > 0.9 * dt_crit:
                safe_dt = 0.8 * dt_crit
                self.log.emit(
                    f"WARNING: dt={config.dt:.4g} s approaches critical "
                    f"dt_crit={dt_crit:.4g} s for Central Difference. "
                    f"Reducing dt to {safe_dt:.4g} s for stability."
                )
                time_params = TimeParams(
                    t_start=time_params.t_start,
                    t_end=time_params.t_end,
                    dt=safe_dt,
                    output_interval=time_params.output_interval,
                )
            elif dt_crit and config.dt > dt_crit:
                self.log.emit(
                    f"WARNING: dt={config.dt:.4g} s exceeds critical "
                    f"dt_crit={dt_crit:.4g} s. Solution may be unstable."
                )

        elif config.method == "modal":
            integrator = ModalSuperposition(M, C, K, n_modes=config.n_modes)
            self.log.emit(f"Modal frequencies: {integrator.freq[:min(5, len(integrator.freq))]} Hz")

        elif config.method == "rk4":
            integrator = RungeKutta4(M, C, K)
            # 7.3: RK4 stability — same CFL condition as Central Difference
            if hasattr(integrator, 'get_critical_timestep'):
                dt_crit_rk4 = integrator.get_critical_timestep()
                if dt_crit_rk4 and config.dt > 0.9 * dt_crit_rk4:
                    safe_dt_rk4 = 0.8 * dt_crit_rk4
                    self.log.emit(
                        f"[WARN] dt={config.dt:.4g} s approaches critical "
                        f"dt_crit={dt_crit_rk4:.4g} s for RK4. "
                        f"Reducing dt to {safe_dt_rk4:.4g} s."
                    )
                    time_params = TimeParams(
                        t_start=time_params.t_start,
                        t_end=time_params.t_end,
                        dt=safe_dt_rk4,
                        output_interval=time_params.output_interval,
                    )
                elif dt_crit_rk4 and config.dt > dt_crit_rk4:
                    self.log.emit(
                        f"[WARN] dt={config.dt:.4g} s exceeds critical "
                        f"dt_crit={dt_crit_rk4:.4g} s for RK4. May be unstable."
                    )

        elif config.method == "adaptive_rk45":
            integrator = AdaptiveRK45(M, C, K, atol=1e-6, rtol=1e-3)
            self.log.emit(
                "[INFO] Adaptive RK45 (Dormand-Prince): step size auto-adjusted "
                f"(atol=1e-6, rtol=1e-3, dt_initial={config.dt:.4g} s)"
            )

        else:
            # Default to Newmark
            integrator = NewmarkIntegrator(M, C, K)

        # Initial conditions
        u0 = config.u0 if config.u0 is not None else np.zeros(n_dof)
        v0 = config.v0 if config.v0 is not None else np.zeros(n_dof)

        # Run integration
        self.log.emit("Running time integration...")
        self.progress.emit(40, "Integrating...")

        # Integration with progress updates
        n_steps = time_params.n_steps

        # CRITICAL-01: solve_with_contacts() requires CompleteMSDMatrixAssembler,
        # StateManager, and PreloadTracker objects that are not yet constructed here.
        # Contact-aware integration is available via _run_coupled_loosening_analysis()
        # when model contacts should influence the analysis.
        if (model and hasattr(model, 'contacts') and model.contacts):
            self.log.emit(
                f"Note: Model has {len(model.contacts)} contact(s). "
                "Contact states are tracked in Coupled Loosening analysis. "
                "Time integration uses linear matrices (contact forces via {F} vector)."
            )

        result = integrator.integrate(time_params, F_func, u0, v0)

        self.progress.emit(90, "Computing statistics...")

        # Compute statistics
        max_disp = np.max(np.abs(result.displacement))
        max_vel = np.max(np.abs(result.velocity))
        max_acc = np.max(np.abs(result.acceleration))

        self.log.emit(f"Max displacement: {max_disp:.6e}")
        self.log.emit(f"Max velocity: {max_vel:.6e}")
        self.log.emit(f"Max acceleration: {max_acc:.6e}")

        return TimeIntegrationResult(
            time=result.time,
            displacement=result.displacement,
            velocity=result.velocity,
            acceleration=result.acceleration,
            force=result.force,
            max_displacement=max_disp,
            max_velocity=max_vel,
            max_acceleration=max_acc,
            method=config.method,
            dt=config.dt,
            t_end=config.t_end
        )

    # -------------------------------------------------------------------------
    # Modal Analysis
    # -------------------------------------------------------------------------

    def _run_modal_analysis(self, model: MSDModel) -> tuple:
        """Run modal analysis to get natural frequencies and mode shapes."""

        self.log.emit("Running modal analysis...")
        self.progress.emit(20, "Computing natural frequencies...")

        M, K, C = model.assemble_matrices()
        n_dof = M.shape[0]

        if n_dof == 0:
            return np.array([]), np.array([])

        # Solve generalized eigenvalue problem K*phi = omega^2*M*phi
        from scipy import linalg

        try:
            eigenvalues, eigenvectors = linalg.eigh(K, M)

            # Sort by frequency (ascending)
            idx = np.argsort(eigenvalues)
            eigenvalues = eigenvalues[idx]
            eigenvectors = eigenvectors[:, idx]

            # Convert to frequencies (Hz)
            omega = np.sqrt(np.maximum(eigenvalues, 0))
            frequencies = omega / (2 * np.pi)

            self.progress.emit(80, "Normalizing mode shapes...")

            # Normalize mode shapes
            for i in range(n_dof):
                norm = np.sqrt(eigenvectors[:, i] @ M @ eigenvectors[:, i])
                if norm > 0:
                    eigenvectors[:, i] /= norm

            self.log.emit(f"Found {len(frequencies)} natural frequencies")
            for i, f in enumerate(frequencies[:5]):
                self.log.emit(f"  Mode {i+1}: {f:.2f} Hz")

            return frequencies, eigenvectors

        except Exception as e:
            self.log.emit(f"Modal analysis error: {e}")
            return np.array([]), np.array([])

    # -------------------------------------------------------------------------
    # Static Analysis
    # -------------------------------------------------------------------------

    def _run_static_analysis(
        self,
        model: MSDModel,
        config: TimeIntegrationConfig
    ) -> np.ndarray:
        """Run static analysis (K*u = F)."""

        self.log.emit("Running static analysis...")
        self.progress.emit(20, "Assembling matrices...")

        M, K, C = model.assemble_matrices()
        n_dof = K.shape[0]

        if n_dof == 0:
            return np.array([])

        # Build force vector
        F = np.zeros(n_dof)
        load_dof = min(config.load_dof, n_dof - 1)
        F[load_dof] = config.load_amplitude

        self.progress.emit(50, "Solving linear system...")

        # Solve K*u = F
        try:
            from scipy import linalg
            u = linalg.solve(K, F, assume_a='pos')

            self.log.emit(f"Static displacement at DOF {load_dof}: {u[load_dof]:.6e}")

            return u

        except Exception as e:
            self.log.emit(f"Static analysis error: {e}")
            return np.zeros(n_dof)

    # -------------------------------------------------------------------------
    # Coupled Loosening Analysis
    # -------------------------------------------------------------------------

    def _compute_v2_history(self, config, n_run):
        """Full per-cycle history from the V2 energy engine.

        Runs ``DynamicStiffnessAnalyzer`` (the V2 main engine) and returns a
        dict of numpy arrays indexed by cycle ``0..n_run`` so every secondary
        plot can be drawn from the *same* model that produces the preload
        curve (coherence). Returns ``None`` for degenerate inputs (no preload /
        no cycles). Keys:

        - ``ratio``      F_0(c) / F_0(0)              (preload ratio, ->1.0 at 0)
        - ``wear_um``    delta_wear                    (um, cumulative)
        - ``angle_deg``  theta_loose                   (deg, cumulative)
        - ``rate_deg``   d(angle_deg)/dcycle           (deg/cycle, loosening rate)
        - ``D``          surface_damage                (0..1)
        - ``mu_bearing`` mu_bearing_eff(state)         (damage-modulated)
        - ``mu_thread``  mat.mu_thread                 (constant in V2)
        - ``cum``        {mech: cumulative preload loss in kN} for the 4
                         mechanisms (embedding/creep/wear/rotational_loosening);
                         their sum equals the total loss F0*(1-ratio).
        - ``F0``         initial preload (N)

        Everything is intrinsically non-linear (Greenwood-Williamson softening
        + 4 parallel loss mechanisms). Calibrated tuner overrides on the model
        (``_v2_tuner_overrides``) are honoured; otherwise the physically-
        calibrated ``JointMaterial`` defaults are used.
        """
        import math
        import numpy as _np
        from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
            DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
            mu_bearing_eff,
        )

        F0 = float(getattr(config, 'initial_preload', 0.0) or 0.0)
        if F0 <= 0.0 or n_run < 1:
            return None

        # Geometry from the run config (authoritative bolt size for this Run).
        d_mm = float(getattr(config, 'bolt_diameter_mm', 16.0) or 16.0)
        p_mm = float(getattr(config, 'pitch_mm', 2.0) or 2.0)
        d, p = d_mm * 1e-3, p_mm * 1e-3
        d2 = d - 0.6495 * p          # ISO 724 pitch diameter
        d1 = d - 1.0825 * p          # ISO 724 minor diameter
        A_s = math.pi / 4.0 * ((d2 + d1) / 2.0) ** 2
        geom = JointGeometry(
            A_s=A_s, L_eff=max(3.0 * d, 0.02), d_2=d2, pitch=p,
            r_bearing=0.75 * d, A_contact=1.0e-4,
        )

        # Geometria com proveniencia do caso (gui_bridge, Plano B 2026-07-10):
        # canal ADITIVO — presente, sobrepoe campos de JointGeometry (L_eff do
        # grip real, A_contact do anel §4.9-11g); ausente/invalido = geometria
        # do config (comportamento anterior bit-identico).
        _m0 = getattr(self, '_current_model', None)
        gov = getattr(_m0, '_v2_geometry_overrides', None) if _m0 is not None else None
        if isinstance(gov, dict) and gov:
            # d_hole/d_washer (F1 2026-07-21): geometria adotada do kj_mode —
            # aditivo; ausentes/0.0 = fallback silencioso p/ k_j_init.
            gfields = ('E', 'A_s', 'L_eff', 'd_2', 'pitch', 'r_bearing',
                       'A_contact', 'd_hole', 'd_washer')
            base_g = {f: getattr(geom, f) for f in gfields}
            for k, v in gov.items():
                if k in gfields:
                    try:
                        base_g[k] = float(v)
                    except (TypeError, ValueError):
                        pass                    # valor invalido: ignora o campo
            geom = JointGeometry(**base_g)

        # Calibrated V2 tuners from the model, if a calibration was applied.
        # Filter to valid JointMaterial fields so a stray key never crashes the
        # Run (backward-compat pattern; tuner keys are e.g. 'k_emb_scale').
        # Type-aware: str-typed fields (e.g. conform_driver) pass through;
        # numeric fields are coerced to float (numeric behaviour unchanged).
        m = getattr(self, '_current_model', None)
        ov = getattr(m, '_v2_tuner_overrides', None) if m is not None else None

        # Conformacao dependente de pressao ADOTADA (2026-07-04, bloco canonico)
        # — LIGADA POR DEFAULT no Run, driver auto-limitante 'effective'. Eh
        # PRESSURE-GATED: p_ref = pre-carga nominal (70% do escoamento) deste
        # parafuso, entao o SOBRETORQUE (pct acima de 70%) excita mais o plato.
        # Como p e p_ref dividem pelo mesmo A_contact, o gate reduz a
        # (p/p_ref) = pct/70 (independe de A_contact/A_s/proof) => a SEPARACAO por
        # sobretorque vale em qualquer F0. W_conf_ref=7671 eh o valor da âncora interna por-par
        # (default; sem ancora p/ outros pares — MODEL_LEGITIMACY §4.9 strand 3).
        # Overrides explicitos em _v2_tuner_overrides VENCEM; W_conf_ref=0 desliga.
        # CAVEAT DE ESCALA (medido): a inercia no nominal so vale ~na escala da âncora interna
        # (F0~50 kN => delta~0.014); em F0 alto o trabalho de slip (proporcional a
        # F0) enche o W_conf_ref FIXO e o gate morde tb no nominal (F0=120 kN =>
        # delta~0.09). Consequencia de "aplica W_conf_ref âncora interna por-par a qualquer
        # junta" (o flag aprovado): calibrado na escala da âncora interna, aproximado fora dela.
        pct = float(getattr(config, 'preload_percent_yield', 70.0) or 70.0)
        mat = build_v2_material(ov, F0, geom.A_contact, pct)

        # Loading: control mode + amplitude + frequency from the model.
        gl = getattr(m, 'global_loading', None) if m is not None else None
        control_mode = str(getattr(gl, 'control_mode', 'displacement')
                           or 'displacement')
        freq = float(getattr(gl, 'frequency', 0.5) or 0.5) if gl is not None else 0.5
        delta = (float(getattr(gl, 'delta_amplitude', 0.0) or 0.0) * 1e-3
                 if gl is not None else 0.0)
        if delta <= 0.0:
            delta = 0.5e-3          # default Junker stroke +/- 0.5 mm
        F_amp = float(getattr(config, 'transverse_force', 0.0) or 0.0)
        if F_amp <= 0.0:
            F_amp = 0.4 * F0
        theta = math.pi / 2.0       # transverse default
        if gl is not None:
            t = str(getattr(getattr(gl, 'type', None), 'name',
                            getattr(gl, 'type', ''))).upper()
            theta = {'AXIAL': 0.0, 'TRANSVERSE': math.pi / 2.0,
                     'COMBINED': math.pi / 4.0}.get(t, math.pi / 2.0)

        ana = DynamicStiffnessAnalyzer(geom, mat, F0)
        dd = delta if control_mode.lower().startswith('disp') else None
        N = int(n_run)
        ratio = _np.empty(N + 1, dtype=float); ratio[0] = 1.0
        wear_um = _np.zeros(N + 1, dtype=float)
        angle_deg = _np.zeros(N + 1, dtype=float)
        D_arr = _np.empty(N + 1, dtype=float); D_arr[0] = float(ana.state.D)
        mu_brg = _np.empty(N + 1, dtype=float)
        mu_brg[0] = float(mu_bearing_eff(ana.state, mat))
        MECHS = ('embedding', 'creep', 'wear', 'rotational_loosening',
                 'thread_fretting')
        cum = {k: _np.zeros(N + 1, dtype=float) for k in MECHS}
        acc = {k: 0.0 for k in MECHS}
        for c in range(1, N + 1):
            snap = ana.step_cycle(F_amp, theta, freq, delta_amp=dd)
            # Memoria O(1) (resolucao 2026-07-28): o engine faz
            # history.append(snap) por ciclo mas NUNCA le a propria history
            # (verificado: so consumidores externos leem), e este loop usa o
            # snap RETORNADO — a lista era peso morto de ~centenas de MB em
            # curvas de fratura longas (330k CycleSnapshot), o motivo real de
            # o _CAP existir. Podar aqui nao muda NENHUM numero (nada le).
            ana.history.clear()
            ratio[c] = max(float(ana.state.F_0), 0.0) / F0
            wear_um[c] = float(ana.state.delta_wear) * 1e6
            angle_deg[c] = math.degrees(float(ana.state.theta_loose))
            D_arr[c] = float(ana.state.D)
            mu_brg[c] = float(mu_bearing_eff(ana.state, mat))
            for k in MECHS:
                # dF_0_by_mech is negative (loss); store cumulative loss as +kN.
                acc[k] += -float(snap.dF_0_by_mech.get(k, 0.0))
                cum[k][c] = acc[k] / 1000.0
        rate_deg = _np.zeros(N + 1, dtype=float)
        if N >= 1:
            rate_deg[1:] = _np.diff(angle_deg)
        return {
            'F0': F0,
            'ratio': ratio,
            'wear_um': wear_um,
            'angle_deg': angle_deg,
            'rate_deg': rate_deg,
            'D': D_arr,
            'mu_bearing': mu_brg,
            'mu_thread': _np.full(N + 1, float(mat.mu_thread), dtype=float),
            'cum': cum,
        }

    def _compute_v2_preload_curve(self, config, n_run):
        """Backward-compat shim: the preload ratio array from the V2 history."""
        h = self._compute_v2_history(config, n_run)
        return None if h is None else h['ratio']

    def _run_coupled_loosening_analysis(
        self,
        config: CoupledLooseningConfig
    ) -> CoupledLooseningResult:
        """
        Run coupled friction-wear-loosening analysis.

        This integrates:
        - Three-phase friction evolution
        - Archard wear model
        - Junker loosening mechanism
        - Torque balance and preload loss
        """

        self.log.emit("Setting up coupled loosening analysis...")
        self.progress.emit(5, "Creating analyzer...")

        try:
            # Create analyzer based on configuration
            # Priority: use_msd_model > use_preset > custom

            if config.use_msd_model and self._current_model is not None:
                # NEW: Extract parameters from MSD model
                self.log.emit("Extracting parameters from MSD model...")

                analyzer, extraction_info = create_analyzer_from_msd_model(
                    model=self._current_model,
                    mu_initial=config.mu_initial if config.mu_initial != 0.12 else None,
                    lubricated=config.lubricated,
                    transverse_displacement_mm=0.65,
                    friction_evolution_model=getattr(
                        self._current_model, 'friction_evolution_model', None),
                )

                # Log extraction info
                self.log.emit(f"=== MSD Model Integration ===")
                self.log.emit(f"Model: {extraction_info.get('model_name', 'Unknown')}")
                self.log.emit(f"Bolt diameter: {extraction_info.get('bolt_diameter_mm', 0):.1f} mm (from {extraction_info.get('diameter_source', 'unknown')})")
                self.log.emit(f"Pitch: {extraction_info.get('pitch_mm', 0):.2f} mm")
                self.log.emit(f"Grip length: {extraction_info.get('grip_length_mm', 0):.1f} mm (from {extraction_info.get('grip_source', 'unknown')})")
                self.log.emit(f"Preload: {extraction_info.get('preload_N', 0):.0f} N (from {extraction_info.get('preload_source', 'unknown')})")
                self.log.emit(f"Transverse: {extraction_info.get('transverse_force_N', 0):.0f} N (from {extraction_info.get('transverse_source', 'unknown')})")
                self.log.emit(f"Friction: {extraction_info.get('mu_initial', 0):.3f} (from {extraction_info.get('friction_source', 'unknown')})")
                self.log.emit(f"Friction model: {extraction_info.get('friction_evolution_model', 'Three-Phase')}")
                self.log.emit(f"k_bolt: {extraction_info.get('k_bolt', 0):.2e} N/m (from {extraction_info.get('k_bolt_source', 'unknown')})")
                self.log.emit(f"k_member: {extraction_info.get('k_member', 0):.2e} N/m (from {extraction_info.get('k_member_source', 'unknown')})")

                # Report any warnings
                for warning in extraction_info.get('warnings', []):
                    self.log.emit(f"WARNING: {warning}")

                self.log.emit(f"=== End MSD Integration ===")

                # Override config values with extracted values for analysis
                config.initial_preload = extraction_info.get('preload_N', config.initial_preload)
                config.transverse_force = extraction_info.get('transverse_force_N', config.transverse_force)
                config.bolt_diameter_mm = extraction_info.get('bolt_diameter_mm', config.bolt_diameter_mm)
                config.pitch_mm = extraction_info.get('pitch_mm', config.pitch_mm)
                config.mu_initial = extraction_info.get('mu_initial', config.mu_initial)

            elif config.use_preset:
                # Use M16 preset with customizations
                analyzer = create_m16_analyzer(
                    mu_initial=config.mu_initial,
                    lubricated=config.lubricated
                )
                self.log.emit(f"Using M16 preset (lubricated={config.lubricated})")
            else:
                # Create custom analyzer
                thread_geometry = ThreadGeometryParams(
                    pitch=config.pitch_mm * 1e-3,
                    pitch_diameter=(config.bolt_diameter_mm - 0.6495 * config.pitch_mm) * 1e-3,
                    major_diameter=config.bolt_diameter_mm * 1e-3,
                    flank_angle=np.radians(config.flank_angle_deg),
                    num_engaged_threads=config.num_engaged_threads
                )

                bearing_geometry = BearingGeometryParams(
                    inner_diameter=config.bearing_inner_diameter_mm * 1e-3,
                    outer_diameter=config.bearing_outer_diameter_mm * 1e-3
                )

                friction_params = FrictionEvolutionParams(
                    mu_initial=config.mu_initial,
                    mu_peak=config.mu_peak,
                    mu_steady=config.mu_steady,
                    mu_minimum=config.mu_minimum,
                    N1=config.N1_running_in,
                    N2=config.N2_transition,
                    N3=config.N3_steady,
                    wear_degradation_rate=config.wear_degradation_rate,
                    temperature_factor=config.temperature_factor
                )

                wear_params = WearModelParams(
                    K_archard=config.K_archard,
                    K_running_in=config.K_running_in,
                    K_steady=config.K_steady,
                    hardness=config.hardness,
                    contact_area=config.contact_area
                )

                analyzer = CoupledLooseningAnalyzer(
                    thread_geometry=thread_geometry,
                    bearing_geometry=bearing_geometry,
                    friction_params=friction_params,
                    wear_params=wear_params,
                    k_bolt=config.k_bolt,
                    k_member=config.k_member
                )

                self.log.emit(f"Custom analyzer: M{config.bolt_diameter_mm}x{config.pitch_mm}")

            # Log analysis parameters
            mu_crit = analyzer.compute_critical_friction()
            self.log.emit(f"Critical friction coefficient: μ_crit = {mu_crit:.4f}")
            self.log.emit(f"Initial friction: μ_0 = {config.mu_initial:.4f}")
            self.log.emit(f"Initial preload: F_p0 = {config.initial_preload:.0f} N")
            self.log.emit(f"Transverse force: F_trans = {config.transverse_force:.0f} N")

            if config.mu_initial < mu_crit:
                self.log.emit("WARNING: Initial friction below critical - loosening likely!")

            self.progress.emit(10, "Running analysis...")

            # Calculate sample interval for large cycle counts
            # Priority: explicit sample_interval > target_output_points > sample_percentage
            n_cycles = config.n_cycles
            sample_interval = config.sample_interval

            if sample_interval <= 1:
                # Calculate from target points or percentage
                points_from_pct = int(n_cycles * config.sample_percentage / 100.0)
                points_from_target = config.target_output_points

                # Use smaller value (more efficient) but ensure minimum 100 points
                target_points = max(100, min(points_from_pct, points_from_target))
                sample_interval = max(1, n_cycles // target_points)

            # For very large cycle counts, adjust progress update frequency
            progress_update_freq = max(1, n_cycles // 500)  # Max 500 progress updates

            self.log.emit(f"Cycle count: {n_cycles:,}")
            self.log.emit(f"Sample interval: {sample_interval} (1 point per {sample_interval} cycles)")
            self.log.emit(f"Expected output points: ~{n_cycles // sample_interval:,}")

            # Progress callback for the analyzer
            def progress_callback(current: int, total: int):
                if self._check_stop():
                    return
                self._wait_if_paused()
                percent = int(10 + 85 * current / total)
                if current % progress_update_freq == 0:
                    self.progress.emit(percent, f"Cycle {current:,}/{total:,}")
                # Live state update every 100 cycles (matches analyzer callback frequency)
                try:
                    st = analyzer.state
                    self.live_state.emit({
                        "cycle": current,
                        "total": total,
                        "preload_ratio": float(st.preload_ratio),
                        "mu_thread": float(st.mu_thread),
                        "mu_bearing": float(st.mu_bearing),
                        "loosening_deg": float(st.loosening_angle_deg),
                        "torque_margin": float(st.torque_margin),
                        "friction_margin": float(st.friction_margin),
                    })
                except Exception:
                    pass

            # Run analysis
            results: LooseningResults = analyzer.run_analysis(
                preload_initial=config.initial_preload,
                F_transverse=config.transverse_force,
                n_cycles=n_cycles,
                temperature=config.temperature,
                output_interval=sample_interval,
                progress_callback=progress_callback
            )

            if self._check_stop():
                self.log.emit("Analysis stopped by user")
                return CoupledLooseningResult()

            self.progress.emit(95, "Finalizing results...")

            # Log summary
            self.log.emit(f"--- Analysis Complete ---")
            self.log.emit(f"Final preload ratio: {results.final_preload_ratio * 100:.1f}%")
            self.log.emit(f"Total loosening: {results.total_loosening_deg:.2f}°")
            self.log.emit(f"Max loosening rate: {results.max_loosening_rate:.4f}°/cycle")
            self.log.emit(f"Phase at end: {results.phase_at_end.value}")

            if results.cycles_to_loosening_onset > 0:
                self.log.emit(f"Loosening onset at cycle: {results.cycles_to_loosening_onset}")

            if results.cycles_to_50_percent > 0:
                self.log.emit(f"50% preload loss at cycle: {results.cycles_to_50_percent}")

            # --- V2 COHERENT RESULTS ----------------------------------------
            # Every preload/mechanism curve is produced by the validated
            # energy-based V2 engine (DynamicStiffnessAnalyzer), so the whole
            # Run is internally consistent: the non-linear preload decay AND
            # the secondary plots (wear, loosening angle/rate, friction) come
            # from the *same* model. The V2 history is sampled onto the existing
            # V1 cycle grid so all arrays stay aligned (downstream downsampling
            # and plotting are untouched). The per-mechanism preload-loss
            # decomposition is stored self-contained for the new decomposition
            # plot. V1 still computes the values that V2 does not model
            # (phase tagging, torque/friction margins).
            try:
                import numpy as _np2
                _cyc = _np2.asarray(results.cycles, dtype=float)
                if _cyc.size > 1:
                    _CAP = _v2_cycle_cap(getattr(
                        self._current_model, "_v2_tuner_overrides", None))
                    _nmax = int(_cyc.max())
                    _nrun = min(_nmax, _CAP)
                    _h = self._compute_v2_history(config, _nrun)
                    if _h is not None and _h['ratio'].size > 1:
                        _idx = _np2.clip(_np2.rint(_cyc).astype(int),
                                         0, _h['ratio'].size - 1)
                        _F0 = float(config.initial_preload)
                        results.preload_ratio = _h['ratio'][_idx]
                        results.preload = results.preload_ratio * _F0
                        results.final_preload_ratio = float(results.preload_ratio[-1])
                        results.total_wear_um = _h['wear_um'][_idx]
                        results.loosening_angle_deg = _h['angle_deg'][_idx]
                        results.loosening_rate = _h['rate_deg'][_idx]
                        results.mu_bearing = _h['mu_bearing'][_idx]
                        results.mu_thread = _h['mu_thread'][_idx]
                        results.total_loosening_deg = float(_h['angle_deg'][-1])
                        results.max_loosening_rate = float(_h['rate_deg'].max())
                        # Self-contained decomposition (own cycle grid so the
                        # later downsampling of results.cycles can't desync it).
                        results._v2_mech_decomp = {
                            'cycles': _cyc.copy(),
                            'embedding': _h['cum']['embedding'][_idx],
                            'creep': _h['cum']['creep'][_idx],
                            'wear': _h['cum']['wear'][_idx],
                            'rotational_loosening':
                                _h['cum']['rotational_loosening'][_idx],
                            'thread_fretting':
                                _h['cum']['thread_fretting'][_idx],
                            'total_kN': (1.0 - _h['ratio'][_idx]) * _F0 / 1000.0,
                        }
                        results._v2_damage = _h['D'][_idx]
                        if _nmax > _CAP:
                            self.log.emit(
                                f"V2 engine capped at {_CAP} cycles "
                                f"(saturated beyond)")
                        self.log.emit(
                            "Preload + mechanism curves: V2 non-linear engine "
                            "(DynamicStiffnessAnalyzer)")
            except Exception as _v2err:
                self.log.emit(f"V2 override skipped ({_v2err}); V1 curves kept")
            # ----------------------------------------------------------------

            # 8.4: Enforce max 5000 output points to prevent memory issues
            MAX_OUTPUT_POINTS = 5000
            _cycles_arr = results.cycles
            if hasattr(_cycles_arr, '__len__') and len(_cycles_arr) > MAX_OUTPUT_POINTS:
                import numpy as _np
                _idx = _np.linspace(0, len(_cycles_arr) - 1, MAX_OUTPUT_POINTS, dtype=int)
                def _ds(arr):
                    if arr is None:
                        return arr
                    try:
                        a = _np.asarray(arr)
                        return a[_idx] if len(a) == len(_cycles_arr) else arr
                    except Exception:
                        return arr
                results.cycles               = _ds(results.cycles)
                results.preload              = _ds(results.preload)
                results.preload_ratio        = _ds(results.preload_ratio)
                results.mu_thread            = _ds(results.mu_thread)
                results.mu_bearing           = _ds(results.mu_bearing)
                results.total_wear_um        = _ds(results.total_wear_um)
                results.loosening_angle_deg  = _ds(results.loosening_angle_deg)
                results.loosening_rate       = _ds(results.loosening_rate)
                results.torque_margin        = _ds(results.torque_margin)
                results.friction_margin      = _ds(results.friction_margin)
                # Downsample states list to match the same indices
                if results.states and len(results.states) > MAX_OUTPUT_POINTS:
                    results.states = [results.states[i] for i in _idx
                                      if i < len(results.states)]
                self.log.emit(
                    f"[INFO] Output downsampled to {MAX_OUTPUT_POINTS} points "
                    f"(memory management)")

            # Convert to app state result (CRITICAL-02: also store raw results for rich plotter)
            cl_result = CoupledLooseningResult(
                cycles=results.cycles,
                preload=results.preload,
                preload_ratio=results.preload_ratio,
                mu_thread=results.mu_thread,
                mu_bearing=results.mu_bearing,
                total_wear_um=results.total_wear_um,
                loosening_angle_deg=results.loosening_angle_deg,
                loosening_rate=results.loosening_rate,
                torque_margin=results.torque_margin,
                friction_margin=results.friction_margin,
                final_preload_ratio=results.final_preload_ratio,
                total_loosening_deg=results.total_loosening_deg,
                cycles_to_50_percent=results.cycles_to_50_percent,
                cycles_to_loosening_onset=results.cycles_to_loosening_onset,
                max_loosening_rate=results.max_loosening_rate,
                phase_at_end=results.phase_at_end.value,
                mu_critical=results.mu_critical,
                initial_preload=config.initial_preload,
                transverse_force=config.transverse_force,
                n_cycles=config.n_cycles,
                states=results.states,   # per-cycle LooseningState list for phase coloring
            )
            # Store raw LooseningResults for CoupledLooseningResultsPlotter access
            cl_result._raw_loosening_results = results
            # Store analyzer for diagnostics plots (§2.4/§4.6/§6.7)
            cl_result._analyzer = analyzer
            # Carry the V2 per-mechanism decomposition + damage onto the result
            # the plots actually read (set by the V2 override block above).
            cl_result._v2_mech_decomp = getattr(results, '_v2_mech_decomp', None)
            cl_result._v2_damage = getattr(results, '_v2_damage', None)
            return cl_result

        except Exception as e:
            self.log.emit(f"Coupled loosening analysis error: {e}")
            raise


# =============================================================================
# THREAD MANAGER
# =============================================================================

class SolverThread(QThread):
    """Thread wrapper for SolverWorker."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = SolverWorker()
        self._model = None
        self._config = None

    def setup(self, model: Optional[MSDModel], config: AnalysisConfig):
        """Setup the analysis parameters."""
        self._model = model
        self._config = config

    def run(self):
        """Run the analysis in this thread."""
        if self._config is not None:
            self.worker.run_analysis(self._model, self._config)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_default_preload_config() -> PreloadAnalysisConfig:
    """Create default preload analysis configuration."""
    return PreloadAnalysisConfig()


def create_default_time_config() -> TimeIntegrationConfig:
    """Create default time integration configuration."""
    return TimeIntegrationConfig()


def create_analysis_config(
    analysis_type: str = "preload",
    **kwargs
) -> AnalysisConfig:
    """Create analysis configuration with custom parameters."""
    config = AnalysisConfig(analysis_type=analysis_type)

    # Apply kwargs to appropriate sub-config
    if analysis_type == "preload":
        for key, value in kwargs.items():
            if hasattr(config.preload_config, key):
                setattr(config.preload_config, key, value)
    elif analysis_type in ("time_integration", "modal", "static"):
        for key, value in kwargs.items():
            if hasattr(config.time_config, key):
                setattr(config.time_config, key, value)

    return config
