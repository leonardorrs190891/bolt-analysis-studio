"""
Application State Manager
Central state management for Bolt Analysis Studio v4.0

Prof. Leonardo Rosa Ribeiro da Silva, PhD
January 2026

This singleton holds the application state and emits signals when state changes.
All tabs and windows communicate through this central state.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import copy
import numpy as np

from PyQt6.QtCore import QObject, pyqtSignal

# Import core data types
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from bolt_analysis_studio.core.models.model import MSDModel
from bolt_analysis_studio.core.models.element import MSDElementData


# =============================================================================
# PROJECT INFO DATACLASS
# =============================================================================

@dataclass
class ProjectInfo:
    """Project metadata and configuration."""
    name: str = "Untitled Project"
    description: str = ""
    author: str = ""
    company: str = ""
    institution: str = "BAS"
    project_number: str = ""
    revision: str = "A"
    notes: str = ""

    # Standards
    standard: str = "VDI 2230"
    material_standard: str = "ASTM A320"
    flange_standard: str = "API 6A"

    # Units
    length_unit: str = "mm"
    force_unit: str = "N"
    pressure_unit: str = "MPa"
    temperature_unit: str = "C"

    # Timestamps
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    modified: str = field(default_factory=lambda: datetime.now().isoformat())

    # File path
    filepath: Optional[str] = None
    template_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "company": self.company,
            "institution": self.institution,
            "project_number": self.project_number,
            "revision": self.revision,
            "notes": self.notes,
            "standard": self.standard,
            "material_standard": self.material_standard,
            "flange_standard": self.flange_standard,
            "length_unit": self.length_unit,
            "force_unit": self.force_unit,
            "pressure_unit": self.pressure_unit,
            "temperature_unit": self.temperature_unit,
            "created": self.created,
            "modified": self.modified,
            "filepath": self.filepath,
            "template_name": self.template_name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectInfo':
        """Create from dictionary. Uses .get() for backward compatibility with old files."""
        return cls(
            name=data.get("name", "Untitled Project"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            company=data.get("company", ""),
            institution=data.get("institution", "BAS"),
            project_number=data.get("project_number", ""),
            revision=data.get("revision", "A"),
            notes=data.get("notes", ""),
            standard=data.get("standard", "VDI 2230"),
            material_standard=data.get("material_standard", "ASTM A320"),
            flange_standard=data.get("flange_standard", "API 6A"),
            length_unit=data.get("length_unit", "mm"),
            force_unit=data.get("force_unit", "N"),
            pressure_unit=data.get("pressure_unit", "MPa"),
            temperature_unit=data.get("temperature_unit", "C"),
            created=data.get("created", datetime.now().isoformat()),
            modified=data.get("modified", datetime.now().isoformat()),
            filepath=data.get("filepath"),
            template_name=data.get("template_name", ""),
        )

    def touch(self):
        """Update the modified timestamp."""
        self.modified = datetime.now().isoformat()


# =============================================================================
# ANALYSIS RESULT DATACLASSES
# =============================================================================

@dataclass
class PreloadAnalysisResult:
    """Results from preload loss analysis."""
    # Cycle array
    cycles: Any = None  # np.ndarray

    # Results by model name
    results: Dict[str, Any] = field(default_factory=dict)  # model_name -> preload array

    # Statistics
    final_preload_ratio: float = 1.0
    preload_loss_percent: float = 0.0
    cycles_to_50_percent_loss: Optional[float] = None

    # Configuration
    initial_preload: float = 0.0
    n_cycles: int = 0
    selected_models: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        results_dict = {}
        for name, arr in self.results.items():
            if hasattr(arr, 'tolist'):
                results_dict[name] = arr.tolist()
            else:
                results_dict[name] = arr

        return {
            "cycles": self.cycles.tolist() if hasattr(self.cycles, 'tolist') else self.cycles,
            "results": results_dict,
            "final_preload_ratio": self.final_preload_ratio,
            "preload_loss_percent": self.preload_loss_percent,
            "cycles_to_50_percent_loss": self.cycles_to_50_percent_loss,
            "initial_preload": self.initial_preload,
            "n_cycles": self.n_cycles,
            "selected_models": self.selected_models
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PreloadAnalysisResult':
        """Restore from dictionary."""
        results = {}
        for name, arr in data.get("results", {}).items():
            results[name] = np.array(arr) if arr is not None else None
        cycles_data = data.get("cycles")
        return cls(
            cycles=np.array(cycles_data) if cycles_data is not None else None,
            results=results,
            final_preload_ratio=data.get("final_preload_ratio", 1.0),
            preload_loss_percent=data.get("preload_loss_percent", 0.0),
            cycles_to_50_percent_loss=data.get("cycles_to_50_percent_loss"),
            initial_preload=data.get("initial_preload", 0.0),
            n_cycles=data.get("n_cycles", 0),
            selected_models=data.get("selected_models", [])
        )


@dataclass
class TimeIntegrationResult:
    """Results from time integration analysis."""
    # Time array
    time: Any = None  # np.ndarray

    # State arrays [n_steps, n_dof]
    displacement: Any = None
    velocity: Any = None
    acceleration: Any = None

    # Force arrays
    force: Any = None
    internal_force: Any = None

    # Energy
    energy_kinetic: Any = None
    energy_potential: Any = None
    energy_dissipated: Any = None

    # Statistics
    max_displacement: float = 0.0
    max_velocity: float = 0.0
    max_acceleration: float = 0.0

    # Configuration
    method: str = "Newmark"
    dt: float = 0.001
    t_end: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        def to_list(arr):
            if arr is None:
                return None
            if hasattr(arr, 'tolist'):
                return arr.tolist()
            return arr

        return {
            "time": to_list(self.time),
            "displacement": to_list(self.displacement),
            "velocity": to_list(self.velocity),
            "acceleration": to_list(self.acceleration),
            "max_displacement": self.max_displacement,
            "max_velocity": self.max_velocity,
            "max_acceleration": self.max_acceleration,
            "method": self.method,
            "dt": self.dt,
            "t_end": self.t_end
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeIntegrationResult':
        """Restore from dictionary. Arrays > 5000 points are downsampled to save memory."""
        def _restore_arr(d):
            if d is None:
                return None
            arr = np.array(d)
            # Downsample large arrays (> 5000 points) to cap JSON size
            if arr.ndim >= 1 and arr.shape[0] > 5000:
                step = arr.shape[0] // 5000
                arr = arr[::step]
            return arr

        return cls(
            time=_restore_arr(data.get("time")),
            displacement=_restore_arr(data.get("displacement")),
            velocity=_restore_arr(data.get("velocity")),
            acceleration=_restore_arr(data.get("acceleration")),
            max_displacement=data.get("max_displacement", 0.0),
            max_velocity=data.get("max_velocity", 0.0),
            max_acceleration=data.get("max_acceleration", 0.0),
            method=data.get("method", "Newmark"),
            dt=data.get("dt", 0.001),
            t_end=data.get("t_end", 1.0)
        )


@dataclass
class CoupledLooseningResult:
    """Results from coupled friction-wear-loosening analysis."""
    # Cycle array
    cycles: Any = None  # np.ndarray

    # Time series results
    preload: Any = None  # np.ndarray - preload over cycles
    preload_ratio: Any = None  # np.ndarray - F/F0
    mu_thread: Any = None  # np.ndarray - thread friction
    mu_bearing: Any = None  # np.ndarray - bearing friction
    total_wear_um: Any = None  # np.ndarray - wear depth in micrometers
    loosening_angle_deg: Any = None  # np.ndarray - cumulative loosening angle
    loosening_rate: Any = None  # np.ndarray - deg/cycle
    torque_margin: Any = None  # np.ndarray - T_resistance/T_pitch
    friction_margin: Any = None  # np.ndarray - mu_avg/mu_critical

    # Summary statistics
    final_preload_ratio: float = 1.0
    total_loosening_deg: float = 0.0
    cycles_to_50_percent: int = 0
    cycles_to_loosening_onset: int = 0
    max_loosening_rate: float = 0.0
    phase_at_end: str = "stable"  # stable, non_rotational, transition, rotational, runaway

    # Critical parameters
    mu_critical: float = 0.0
    initial_preload: float = 0.0
    transverse_force: float = 0.0
    n_cycles: int = 0

    # Detailed per-cycle state history (from LooseningState objects)
    states: Optional[List[Any]] = None  # List of LooseningState objects

    # Rich plotter data (not serialized) — CRITICAL-02
    _raw_loosening_results: Optional[Any] = field(default=None, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        def to_list(arr):
            if arr is None:
                return None
            if hasattr(arr, 'tolist'):
                return arr.tolist()
            return arr

        return {
            "cycles": to_list(self.cycles),
            "preload": to_list(self.preload),
            "preload_ratio": to_list(self.preload_ratio),
            "mu_thread": to_list(self.mu_thread),
            "mu_bearing": to_list(self.mu_bearing),
            "total_wear_um": to_list(self.total_wear_um),
            "loosening_angle_deg": to_list(self.loosening_angle_deg),
            "loosening_rate": to_list(self.loosening_rate),
            "torque_margin": to_list(self.torque_margin),
            "friction_margin": to_list(self.friction_margin),
            "final_preload_ratio": self.final_preload_ratio,
            "total_loosening_deg": self.total_loosening_deg,
            "cycles_to_50_percent": self.cycles_to_50_percent,
            "cycles_to_loosening_onset": self.cycles_to_loosening_onset,
            "max_loosening_rate": self.max_loosening_rate,
            "phase_at_end": self.phase_at_end,
            "mu_critical": self.mu_critical,
            "initial_preload": self.initial_preload,
            "transverse_force": self.transverse_force,
            "n_cycles": self.n_cycles
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CoupledLooseningResult':
        """Restore from dictionary."""
        def _arr(key):
            v = data.get(key)
            return np.array(v) if v is not None else None

        return cls(
            cycles=_arr("cycles"),
            preload=_arr("preload"),
            preload_ratio=_arr("preload_ratio"),
            mu_thread=_arr("mu_thread"),
            mu_bearing=_arr("mu_bearing"),
            total_wear_um=_arr("total_wear_um"),
            loosening_angle_deg=_arr("loosening_angle_deg"),
            loosening_rate=_arr("loosening_rate"),
            torque_margin=_arr("torque_margin"),
            friction_margin=_arr("friction_margin"),
            final_preload_ratio=data.get("final_preload_ratio", 1.0),
            total_loosening_deg=data.get("total_loosening_deg", 0.0),
            cycles_to_50_percent=data.get("cycles_to_50_percent", 0),
            cycles_to_loosening_onset=data.get("cycles_to_loosening_onset", 0),
            max_loosening_rate=data.get("max_loosening_rate", 0.0),
            phase_at_end=data.get("phase_at_end", "stable"),
            mu_critical=data.get("mu_critical", 0.0),
            initial_preload=data.get("initial_preload", 0.0),
            transverse_force=data.get("transverse_force", 0.0),
            n_cycles=data.get("n_cycles", 0)
        )


@dataclass
class AnalysisAudit:
    """Metadata record for a completed analysis run (audit trail)."""
    run_id: str = ""                    # UUID for this run
    timestamp_start: str = ""           # ISO timestamp
    timestamp_end: str = ""             # ISO timestamp
    duration_s: float = 0.0             # Wall-clock seconds
    analysis_type: str = ""             # "coupled_loosening", "all", etc.
    method: str = ""                    # Integration method
    n_cycles: int = 0                   # Cycles simulated
    n_dof: int = 0                      # Model DOF count
    n_elements: int = 0                 # Model element count
    solver_version: str = "4.0"         # Software version
    convergence_note: str = ""          # "Steady state", "Full loosening", "Completed"
    preflight_warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "timestamp_start": self.timestamp_start,
            "timestamp_end": self.timestamp_end,
            "duration_s": self.duration_s,
            "analysis_type": self.analysis_type,
            "method": self.method,
            "n_cycles": self.n_cycles,
            "n_dof": self.n_dof,
            "n_elements": self.n_elements,
            "solver_version": self.solver_version,
            "convergence_note": self.convergence_note,
            "preflight_warnings": self.preflight_warnings,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisAudit':
        return cls(
            run_id=data.get("run_id", ""),
            timestamp_start=data.get("timestamp_start", ""),
            timestamp_end=data.get("timestamp_end", ""),
            duration_s=data.get("duration_s", 0.0),
            analysis_type=data.get("analysis_type", ""),
            method=data.get("method", ""),
            n_cycles=data.get("n_cycles", 0),
            n_dof=data.get("n_dof", 0),
            n_elements=data.get("n_elements", 0),
            solver_version=data.get("solver_version", "4.0"),
            convergence_note=data.get("convergence_note", ""),
            preflight_warnings=data.get("preflight_warnings", []),
        )


@dataclass
class AnalysisResult:
    """Combined analysis results container."""
    # Analysis type
    analysis_type: str = "none"  # "preload", "time_integration", "modal", "static", "coupled_loosening"

    # Sub-results
    preload_result: Optional[PreloadAnalysisResult] = None
    time_result: Optional[TimeIntegrationResult] = None
    coupled_loosening_result: Optional[CoupledLooseningResult] = None

    # Natural frequencies (modal analysis)
    natural_frequencies: Optional[List[float]] = None
    mode_shapes: Any = None

    # Static analysis
    static_displacement: Any = None
    static_stress: Any = None
    safety_factor: float = 0.0

    # Timestamps
    started: str = ""
    completed: str = ""

    # Audit trail
    audit: Optional['AnalysisAudit'] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "analysis_type": self.analysis_type,
            "preload_result": self.preload_result.to_dict() if self.preload_result else None,
            "time_result": self.time_result.to_dict() if self.time_result else None,
            "coupled_loosening_result": self.coupled_loosening_result.to_dict() if self.coupled_loosening_result else None,
            "natural_frequencies": self.natural_frequencies,
            "safety_factor": self.safety_factor,
            "started": self.started,
            "completed": self.completed,
            "audit": self.audit.to_dict() if self.audit else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """Restore from dictionary."""
        obj = cls(
            analysis_type=data.get("analysis_type", "none"),
            natural_frequencies=data.get("natural_frequencies"),
            safety_factor=data.get("safety_factor", 0.0),
            started=data.get("started", ""),
            completed=data.get("completed", "")
        )
        pr_data = data.get("preload_result")
        if pr_data:
            try:
                obj.preload_result = PreloadAnalysisResult.from_dict(pr_data)
            except Exception:
                pass
        tr_data = data.get("time_result")
        if tr_data:
            try:
                obj.time_result = TimeIntegrationResult.from_dict(tr_data)
            except Exception:
                pass
        cl_data = data.get("coupled_loosening_result")
        if cl_data:
            try:
                obj.coupled_loosening_result = CoupledLooseningResult.from_dict(cl_data)
            except Exception:
                pass
        audit_data = data.get("audit")
        if audit_data:
            try:
                obj.audit = AnalysisAudit.from_dict(audit_data)
            except Exception:
                pass
        return obj


# =============================================================================
# APPLICATION STATE SINGLETON
# =============================================================================

class AppState(QObject):
    """
    Central application state manager (singleton pattern).

    Holds:
    - current_project: ProjectInfo
    - current_model: MSDModel
    - current_results: AnalysisResult

    Emits signals when state changes to notify all listeners.
    """

    # Signals
    project_changed = pyqtSignal(object)    # Emits ProjectInfo
    model_changed = pyqtSignal(object)      # Emits MSDModel
    results_changed = pyqtSignal(object)    # Emits AnalysisResult
    similitude_changed = pyqtSignal(object) # Emits similitude result (MED-03)
    status_changed = pyqtSignal(str)        # Status message
    error_occurred = pyqtSignal(str)        # Error message

    # Singleton instance. Cache slot APENAS — quem materializa e' o getter
    # `get_app_state()`, la' embaixo. `tests/conftest.py` tambem le daqui para
    # desconectar receivers de `model_changed` entre testes.
    #
    # NAO reintroduzir `__new__` aqui (medido em 2026-07-28). Sob PyQt6 6.11.0,
    # um `__new__` de subclasse de QObject que devolve instancia pre-existente
    # recursiona no nivel C e mata o processo com STATUS_STACK_OVERFLOW
    # (0xC00000FD, rc=3221225725), sem traceback Python alem do frame de
    # `super().__init__()`. Repro minimo: QObject puro passa, subclasse com
    # pyqtSignal passa, o `__new__` mata — com ou sem QApplication, e igual com
    # `super().__new__`, `QObject.__new__` ou `super(C, cls).__new__`. Vitimas:
    # `get_app_state()` e, com ele, TODA a GUI (`run_app.py` e `--v2`) mais 4
    # arquivos de teste.
    #
    # A guarda `_init_done` saiu no mesmo movimento, e tem de continuar fora:
    # sem `__new__`, uma segunda construcao direta cria um objeto NOVO, e a
    # guarda faria `__init__` retornar antes de `super().__init__()` — um QObject
    # meio-construido, com sinais mortos, pior que o bug original.
    _instance: Optional["AppState"] = None

    def __init__(self):
        super().__init__()

        # State
        self._project: ProjectInfo = ProjectInfo()
        self._model: Optional[MSDModel] = None
        self._results: Optional[AnalysisResult] = None
        self._similitude_result: Optional[Any] = None  # MED-03
        self._pinned_results: List[AnalysisResult] = []  # 3.1 pinned runs

        # Undo/redo stacks
        self._undo_stack: List[Dict[str, Any]] = []
        self._redo_stack: List[Dict[str, Any]] = []
        self._max_undo = 50

        # Dirty flag
        self._dirty = False

    # -------------------------------------------------------------------------
    # Project
    # -------------------------------------------------------------------------

    @property
    def project(self) -> ProjectInfo:
        """Get current project info."""
        return self._project

    @project.setter
    def project(self, value: ProjectInfo):
        """Set project info and emit signal."""
        self._project = value
        self._dirty = True
        self.project_changed.emit(value)

    def new_project(self):
        """Create a new empty project."""
        self._project = ProjectInfo()
        self._model = None
        self._results = None
        self._similitude_result = None
        self._pinned_results = []
        self._dirty = False
        self._undo_stack.clear()
        self._redo_stack.clear()

        self.project_changed.emit(self._project)
        self.model_changed.emit(None)
        self.results_changed.emit(None)
        self.status_changed.emit("New project created")

    # -------------------------------------------------------------------------
    # Model
    # -------------------------------------------------------------------------

    @property
    def model(self) -> Optional[MSDModel]:
        """Get current MSD model."""
        return self._model

    @model.setter
    def model(self, value: Optional[MSDModel]):
        """Set model and emit signal."""
        # Save for undo
        if self._model is not None:
            self._push_undo("model", self._model.to_dict())

        self._model = value
        self._dirty = True
        self._project.touch()
        self.model_changed.emit(value)

        # Clear results when model changes
        if self._results is not None:
            self._results = None
            self.results_changed.emit(None)

    def update_model(self, model: MSDModel):
        """Update the model (same as setter but more explicit)."""
        self.model = model

    def get_model_statistics(self) -> Dict[str, Any]:
        """Get statistics about the current model."""
        if self._model is None:
            return {
                "n_elements": 0,
                "n_dof": 0,
                "total_mass": 0.0,
                "k_eq": 0.0,
                "c_eq": 0.0,
                "f_n": 0.0,
                "phi": 0.0
            }
        return self._model.get_statistics()

    # -------------------------------------------------------------------------
    # Results
    # -------------------------------------------------------------------------

    @property
    def results(self) -> Optional[AnalysisResult]:
        """Get current analysis results."""
        return self._results

    @results.setter
    def results(self, value: Optional[AnalysisResult]):
        """Set results and emit signal."""
        self._results = value
        self._dirty = True
        self._project.touch()
        self.results_changed.emit(value)

    def has_results(self) -> bool:
        """Check if there are analysis results."""
        return self._results is not None

    # 3.1 — Pinned results (session-only, up to 5 comparison snapshots)

    @property
    def pinned_results(self) -> List[AnalysisResult]:
        """List of pinned analysis result snapshots."""
        return self._pinned_results

    def pin_results(self) -> bool:
        """
        Pin a copy of the current results for comparison overlays.
        Returns True if pinned successfully, False if already at cap or no results.
        """
        if self._results is None:
            return False
        if len(self._pinned_results) >= 5:
            return False
        pinned = copy.deepcopy(self._results)
        pinned._label = f"Run {len(self._pinned_results) + 1}"  # type: ignore[attr-defined]
        self._pinned_results.append(pinned)
        return True

    def clear_pinned(self):
        """Remove all pinned result snapshots."""
        self._pinned_results.clear()

    # -------------------------------------------------------------------------
    # Similitude results (MED-03)
    # -------------------------------------------------------------------------

    @property
    def similitude_result(self) -> Optional[Any]:
        """Get current similitude analysis result."""
        return self._similitude_result

    @similitude_result.setter
    def similitude_result(self, value: Optional[Any]):
        """Set similitude result and emit signal."""
        self._similitude_result = value
        self.similitude_changed.emit(value)

    # -------------------------------------------------------------------------
    # Dirty state
    # -------------------------------------------------------------------------

    @property
    def is_dirty(self) -> bool:
        """Check if project has unsaved changes."""
        return self._dirty

    def mark_clean(self):
        """Mark project as saved (not dirty)."""
        self._dirty = False

    def mark_dirty(self):
        """Mark project as having unsaved changes."""
        self._dirty = True

    # -------------------------------------------------------------------------
    # Undo/Redo
    # -------------------------------------------------------------------------

    def _push_undo(self, state_type: str, state_data: Dict[str, Any]):
        """Push state to undo stack."""
        self._undo_stack.append({
            "type": state_type,
            "data": state_data,
            "timestamp": datetime.now().isoformat()
        })

        # Limit stack size
        if len(self._undo_stack) > self._max_undo:
            self._undo_stack.pop(0)

        # Clear redo stack on new action
        self._redo_stack.clear()

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0

    def undo(self):
        """Undo last action."""
        if not self.can_undo():
            return

        state = self._undo_stack.pop()

        # Save current state to redo
        if state["type"] == "model" and self._model is not None:
            self._redo_stack.append({
                "type": "model",
                "data": self._model.to_dict(),
                "timestamp": datetime.now().isoformat()
            })

        # Restore state
        if state["type"] == "model":
            self._model = MSDModel.from_dict(state["data"])
            self.model_changed.emit(self._model)

    def redo(self):
        """Redo last undone action."""
        if not self.can_redo():
            return

        state = self._redo_stack.pop()

        # Save current to undo
        if state["type"] == "model" and self._model is not None:
            self._undo_stack.append({
                "type": "model",
                "data": self._model.to_dict(),
                "timestamp": datetime.now().isoformat()
            })

        # Restore state
        if state["type"] == "model":
            self._model = MSDModel.from_dict(state["data"])
            self.model_changed.emit(self._model)

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialize entire application state."""
        return {
            "project": self._project.to_dict(),
            "model": self._model.to_dict() if self._model else None,
            "results": self._results.to_dict() if self._results else None
        }

    def from_dict(self, data: Dict[str, Any]):
        """Restore application state from dictionary."""
        # Restore project
        if "project" in data and data["project"]:
            self._project = ProjectInfo.from_dict(data["project"])

        # Restore model
        if "model" in data and data["model"]:
            self._model = MSDModel.from_dict(data["model"])
        else:
            self._model = None

        # Restore results if available (HIGH-03)
        results_data = data.get("results")
        if results_data:
            try:
                self._results = AnalysisResult.from_dict(results_data)
            except Exception:
                self._results = None
        else:
            self._results = None

        # Emit signals
        self.project_changed.emit(self._project)
        self.model_changed.emit(self._model)
        self.results_changed.emit(self._results)

        self._dirty = False
        self._undo_stack.clear()
        self._redo_stack.clear()


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def get_app_state() -> AppState:
    """Get the application state singleton.

    O singleton vive AQUI, no getter, e nao num `__new__` da classe — ver a nota
    em `AppState._instance`: `__new__` em subclasse de QObject estoura a pilha no
    PyQt6 6.11.0. Este e' o unico caminho de acesso no repo (16 arquivos; zero
    construcoes diretas de `AppState()` em `src/` ou `tests/`), entao a
    identidade que a GUI depende — todos os widgets ligados ao MESMO
    `model_changed` — fica preservada.
    """
    inst = AppState._instance
    if inst is None:
        inst = AppState._instance = AppState()
    return inst
