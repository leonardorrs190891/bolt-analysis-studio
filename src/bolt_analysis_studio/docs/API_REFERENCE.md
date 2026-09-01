# Bolt Analysis Studio v4.0 — API Reference

**Scope:** Key classes, methods, signals, and data structures across all layers.

---

## 1. Core Data Models

### 1.1 MSDElementData (core/models/element.py)

The fundamental building block of the MSD system. All 16 element types map to this or a subclass.

```python
@dataclass
class MSDElementData:
    id: str                       # Unique identifier
    element_type: ElementType     # HEAD, SHANK, THREAD, NUT, WASHER, FLANGE, GASKET, GROUND...
    label: str                    # Human-readable name
    msd: MSDProperties            # Mass, stiffness, damping

    # Optional fields (type-specific)
    material: Optional[MaterialData] = None
    geometry: Optional[GeometryData] = None
    bolt_data: Optional[BoltData] = None
    contact_interface: Optional[ContactInterface] = None
```

**ElementType enum (16 values):**
HEAD, SHANK, THREAD, NUT, WASHER_FLAT, WASHER_SPRING, WASHER_BELLEVILLE, WASHER_NORDLOCK,
FLANGE_WELD_NECK, FLANGE_SLIP_ON, FLANGE_BLIND, GASKET, GROUND, CONTACT_THREAD,
CONTACT_BEARING, CONTACT_INTERFACE

**Factory functions:**
```python
create_bolt_head(diameter, material_name) → MSDElementData
create_washer(inner_d, outer_d, thickness, washer_type) → MSDElementData
create_flange(nominal_bore, class_rating, flange_type) → MSDElementData
create_gasket(nominal_bore, gasket_type) → MSDElementData
create_nut(diameter, nut_type) → MSDElementData
create_stud(diameter, length, material_name) → MSDElementData
create_spring_washer(diameter) → MSDElementData
create_nordlock_washer(diameter) → MSDElementData
```

### 1.2 MSDModel (core/models/model.py)

The assembled joint model with matrix assembly.

```python
@dataclass
class MSDModel:
    elements: List[MSDElementData]
    contacts: List[Contact]
    global_loading: LoadingData
    mu_initial: float = 0.12
    lubricated: bool = True
    bolt_diameter: float = 16.0   # mm
    pitch: float = 2.0             # mm

    # Matrix assembly (lazy cached)
    def assemble_matrices(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns (M, K, C) numpy arrays. Caches result until _mark_dirty()."""

    def assemble_force_vector(self, x, v, t, F_external) -> np.ndarray:
        """Assembles total force vector including tribological contributions."""

    def update_contact_states(self, x, v, dt, preload) -> None:
        """Updates all contact states for current time step."""

    def _mark_dirty(self) -> None:
        """Invalidates matrix cache."""

    def to_dict(self) -> dict:
        """Serializes to JSON-compatible dict."""

    @classmethod
    def from_dict(cls, data: dict) -> "MSDModel":
        """Deserializes from dict. Missing fields use defaults."""
```

**LoadingData:**
```python
@dataclass
class LoadingData:
    type: LoadingType             # AXIAL, TRANSVERSE, COMBINED, TORSIONAL, BENDING
    F_preload: float = 0.0       # Bolt preload [N]
    preload_percent_yield: float = 0.0  # % of yield
    F_amplitude: float = 0.0     # Dynamic force amplitude [N]
    F_transverse: float = 0.0    # Transverse force [N]
    delta_amplitude: float = 0.0 # Transverse displacement amplitude [mm]
    frequency: float = 10.0      # Loading frequency [Hz]
    n_cycles: int = 1000         # Number of cycles
    F_external: float = 0.0      # External axial force [N]
    T_applied: float = 0.0       # Applied torque [N·m]
    delta_T: float = 0.0         # Temperature change [°C]
    mu_initial: float = 0.12     # Friction coefficient (also on MSDModel)
```

### 1.3 AppState (core/app_state.py)

Application state shared across all GUI components via Qt signals.

```python
class AppState(QObject):
    # Signals
    model_changed = pyqtSignal(object)            # MSDModel changed
    results_changed = pyqtSignal(object)          # AnalysisResult updated
    similitude_changed = pyqtSignal(object)       # Similitude result updated
    project_info_changed = pyqtSignal(object)     # Project metadata changed

    # Properties
    @property
    def model(self) -> Optional[MSDModel]: ...
    @model.setter
    def model(self, value): ...

    @property
    def results(self) -> Optional[AnalysisResult]: ...
    @results.setter
    def results(self, value): ...

    @property
    def similitude_result(self) -> Optional[Any]: ...
    @similitude_result.setter
    def similitude_result(self, value): ...

    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> "AppState": ...
```

**Result dataclasses:**

```python
@dataclass
class PreloadAnalysisResult:
    cycles: np.ndarray
    preload: np.ndarray
    preload_ratio: np.ndarray
    model_name: str
    parameters: dict

    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> "PreloadAnalysisResult": ...

@dataclass
class TimeIntegrationResult:
    time: np.ndarray
    displacement: np.ndarray    # shape (n_steps, n_dof)
    velocity: np.ndarray
    acceleration: np.ndarray
    natural_frequencies: Optional[np.ndarray]
    method: str
    dt: float
    t_end: float

    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> "TimeIntegrationResult": ...

@dataclass
class CoupledLooseningResult:
    preload_vs_cycles: np.ndarray
    loosening_angle_vs_cycles: np.ndarray
    friction_vs_cycles: np.ndarray
    wear_vs_cycles: np.ndarray
    loosening_rate: float
    cycles_to_50pct_loss: int
    _raw_loosening_results: Optional[Any] = None  # LooseningResults for rich plotter

    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> "CoupledLooseningResult": ...

@dataclass
class AnalysisResult:
    preload_result: Optional[PreloadAnalysisResult] = None
    time_result: Optional[TimeIntegrationResult] = None
    coupled_result: Optional[CoupledLooseningResult] = None
    run_timestamp: str = ""
    config_snapshot: dict = field(default_factory=dict)

    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisResult": ...
```

### 1.4 Element Sub-Dataclasses (core/models/element.py)

All sub-dataclasses support `to_dict()` / `from_dict()` for JSON serialization.

**GeometryData:**
```python
@dataclass
class GeometryData:
    diameter: float             # Nominal bolt diameter d [mm]
    length: float               # Element length L [mm]
    pitch: float = 2.0          # Thread pitch p [mm]
    d1: float = 0.0             # Minor diameter (d - 1.0825p) [mm]
    d2: float = 0.0             # Pitch diameter (d - 0.6495p) [mm]
    d3: float = 0.0             # Root diameter (d - 1.2268p) [mm]
    At: float = 0.0             # Tensile stress area: π/4·((d2+d1)/2)² [mm²]
    As: float = 0.0             # Shear stress area [mm²]
    head_diameter: float = 0.0  # Across-flats for hex [mm]

    def get_cross_section_area(self) -> float: ...  # Returns At for threaded, πd²/4 for plain
```

**MaterialData:**
```python
@dataclass
class MaterialData:
    E: float           # Young's modulus [MPa]
    G: float           # Shear modulus [MPa]
    nu: float          # Poisson's ratio
    Sy: float          # Yield strength [MPa]
    Su: float          # Ultimate tensile strength [MPa]
    Sf: float          # Fatigue limit (R=-1) [MPa]
    alpha: float       # Thermal expansion [1/K]
    rho: float         # Density [kg/m³]

    def get_E_at_temperature(self, T_celsius: float) -> float: ...   # Linear interpolation
    def get_Sy_at_temperature(self, T_celsius: float) -> float: ...  # Linear interpolation
```

**MATERIAL_GRADE_PROPERTIES — 13 Hardcoded Grades:**

| Grade | Sy (MPa) | Su (MPa) | Use Case |
|-------|----------|----------|---------|
| `A193_B7` | 862 | 1000 | Standard high-temp bolting |
| `A193_B7M` | 724 | 862 | Low-hardness (H2S service) |
| `A193_B16` | 862 | 1000 | High-temp Cr-Mo |
| `A193_B8` | 207 | 517 | Austenitic SS, low strength |
| `A193_B8M` | 207 | 517 | Mo-SS (sea water) |
| `A320_L7` | 862 | 1000 | Low-temperature service |
| `A320_L7M` | 724 | 862 | Low-temp, low-hardness |
| `A320_L43` | 862 | 1000 | Ni-Cr-Mo low-temp |
| `A354_BC` | 896 | 1034 | Structural, medium strength |
| `A354_BD` | 1034 | 1172 | Structural, high strength |
| `Steel_8_8` | 640 | 800 | ISO 898-1 Class 8.8 |
| `Steel_10_9` | 940 | 1040 | ISO 898-1 Class 10.9 |
| `Steel_12_9` | 1100 | 1220 | ISO 898-1 Class 12.9 |

**FrictionData:**
```python
@dataclass
class FrictionData:
    model: FrictionModel           # COULOMB, COULOMB_REGULARIZED, LUGRE, DAHL, IWAN
    mu_thread: float = 0.12       # Thread friction coefficient
    mu_bearing: float = 0.12      # Bearing surface friction coefficient
    sigma_0: float = 1e5          # LuGre bristle stiffness [N/m]
    sigma_1: float = 300.0        # LuGre micro-damping [N·s/m]
    sigma_2: float = 0.1          # LuGre viscous term [N·s/m]
    v_s: float = 0.001            # Stribeck velocity [m/s]

    def get_stribeck_function(self, v: float) -> float: ...
    def get_friction_force_coulomb(self, F_n: float, v: float) -> float: ...
    def get_friction_evolution(self, N_cycles: int) -> float: ...  # Three-phase model
```

**MSDParameters:**
```python
@dataclass
class MSDParameters:
    k: float = 1e6            # Stiffness [N/m]
    c: float = 100.0          # Damping [N·s/m]
    m: float = 0.1            # Mass [kg]
    auto_calculate_k: bool = True   # Auto from geometry/material
    auto_calculate_m: bool = True
    damping_ratio: float = 0.02     # ζ = 2% default

    def calculate_from_geometry_material(self, geom: GeometryData,
                                         mat: MaterialData,
                                         elem_type: ElementType) -> None: ...
```

**VDI 2230 stiffness formulas per element type:**

| Element | Formula | Constants |
|---------|---------|-----------|
| Shank | `k = E·(πd²/4) / L` | Full shank cross-section |
| Thread | `k = E·At / L_thread` | Tensile stress area At |
| Head | `k = 0.5·E·d` | **0.5** per Bickford (2008); C2 bug used 0.4 |
| Nut | `k = 0.5·E·d` | Same as head |
| Flange | VDI frustum cone model | Complex integration of clamped zone |
| Gasket | `k = (27.5 GPa/mm)·A / t` | Metallic gasket, nonlinear |
| Washer | `k = E·A / t` | Thin plate assumption |

**Damping:** `c = 2·ζ·√(k·m)` where ζ = 0.02 (default 2% critical)

**Additional dataclasses:**
```python
@dataclass
class GridPosition:
    row: int      # Series position (0 = top)
    col: int      # Parallel position (0 = left)

@dataclass
class AppliedLoad:
    magnitude: float
    direction: str           # "axial", "transverse", "torsional", "thermal"
    time_variation: TimeVariation   # STATIC, HARMONIC, TRANSIENT
    frequency: float = 0.0
    phase: float = 0.0

    def get_value_at_time(self, t: float) -> float: ...

@dataclass
class Constraint:
    constraint_type: ConstraintType   # FIXED, PRESCRIBED, SPRING
    dof: str                          # "x", "y", "theta"
    value: float = 0.0               # Prescribed displacement or spring stiffness
    time_variation: TimeVariation = TimeVariation.STATIC
```

**Key enumerations in element.py:**

```python
class ThreadStandard(Enum):
    ISO_METRIC, ISO_METRIC_FINE, UNC, UNF, ACME, WHITWORTH

class FrictionModel(Enum):           # For element-level friction settings
    COULOMB, COULOMB_REGULARIZED, LUGRE, DAHL, IWAN

class TimeVariation(Enum):
    STATIC, HARMONIC, TRANSIENT

class ConstraintType(Enum):
    FIXED, PRESCRIBED, SPRING

class LoadingType(Enum):
    AXIAL, TRANSVERSE, COMBINED, TORSIONAL, BENDING
```

---

## 2. Contact System API

### 2.1 Contact Base Class (core/contacts/base.py)

```python
class Contact(ABC):
    contact_id: str
    contact_type: ContactType
    node_i: int              # Global DOF index for node i
    node_j: int              # Global DOF index for node j
    geometry: ContactGeometry
    friction: FrictionProperties
    wear: WearProperties
    stiffness: StiffnessProperties
    damping: float

    # State
    normal_force: float = 0.0
    slip_state: SlipState = SlipState.STICK
    relative_displacement: float = 0.0
    accumulated_slip: float = 0.0

    @abstractmethod
    def get_stiffness_contribution(self) -> List[Tuple[int, int, float]]:
        """Returns list of (row, col, value) triplets for K matrix assembly."""

    @abstractmethod
    def get_damping_contribution(self) -> List[Tuple[int, int, float]]:
        """Returns list of (row, col, value) triplets for C matrix assembly."""

    @abstractmethod
    def get_force_contribution(self, x: np.ndarray, x_dot: np.ndarray,
                               t: float) -> np.ndarray:
        """Returns force vector array of size n_dof."""

    def update_state(self, x: np.ndarray, x_dot: np.ndarray,
                     dt: float, preload: float) -> None:
        """Updates friction evolution, wear accumulation, slip state."""
```

### 2.2 ThreadContact (core/contacts/thread_contact.py)

```python
class ThreadContact(Contact):
    n_threads: int              # Number of engaged threads
    pitch: float                # Thread pitch [m]
    d2: float                   # Pitch diameter [m]
    flank_angle: float          # Half flank angle [rad] (π/6 for metric)
    helix_angle: float          # Helix angle [rad]
    load_dist: LoadDistribution # EQUAL, LINEAR, POWER_LAW, EXPONENTIAL, YAMAMOTO

    # Per-thread state arrays
    thread_loads: np.ndarray        # φ_i load fractions
    thread_stiffness: np.ndarray    # k_i values
    thread_friction: np.ndarray     # μ_i current values
    thread_wear: np.ndarray         # h_i wear depths
    thread_slip: np.ndarray         # SlipState per thread

    def get_stiffness_contribution(self):
        """Includes axial AND helix coupling (off-diagonal) terms."""

    def compute_torque_balance(self, F_p: float) -> dict:
        """Returns {'T_pitch': ..., 'T_thread': ..., 'T_bearing': ..., 'margin': ...}"""

    def compute_loosening_angle(self, F_trans: float, F_p: float, dt: float) -> float:
        """Returns incremental loosening angle per time step [rad]."""
```

### 2.3 BearingContact (core/contacts/bearing_contact.py)

```python
class BearingContact(Contact):
    r_inner: float   # Inner bearing radius [m]
    r_outer: float   # Outer bearing radius [m]
    r_eff: float     # Effective (centroid) radius = (2/3)(r_o³-r_i³)/(r_o²-r_i²)
    is_head: bool    # True = head bearing, False = nut bearing

    def get_friction_torque(self, F_p: float) -> float:
        """Returns bearing friction torque [N·m] opposing loosening."""
```

### 2.4 FlangeGasketContact (core/contacts/gasket_contact.py)

```python
class FlangeGasketContact(Contact):
    k_loading: Callable    # Nonlinear k(δ) during loading
    k_unloading: Callable  # Nonlinear k(δ) during unloading
    C_creep: float         # Gasket creep coefficient
    t_ref: float           # Reference time for creep

    def get_tangent_stiffness(self, delta: float) -> float:
        """Returns current tangent stiffness k_g(δ) for matrix update."""

    def get_creep_loss(self, t: float) -> float:
        """Returns creep-induced preload loss [N] at time t."""
```

---

## 3. Numerical Methods API

### 3.1 Preload Loss Models (numerical/preload_loss_models.py)

All models follow a common interface:

```python
class PreloadLossModel(Protocol):
    def compute(self, N: np.ndarray, F0: float, **params) -> np.ndarray:
        """Returns F(N) array of preload values [N]."""

    def fit(self, N_data: np.ndarray, F_data: np.ndarray) -> dict:
        """Returns fitted parameters dict."""
```

**Available models:**

```python
SingleExponentialModel()         # F = F_inf + (F0-F_inf)*exp(-λN)
DoubleExponentialModel()         # F = F_inf + A1*exp(-λ1*N) + A2*exp(-λ2*N)
StretchedExponentialModel()      # F = F_inf + (F0-F_inf)*exp(-(λN)^β)
PowerLawModel()                  # F = F0 * (N/N_ref)^(-b)   [Lu 2024]
LogarithmicModel()               # F = F0 - A*ln(1 + N/N0)
VDI2230EmbeddingModel()          # ΔF = k_sys * f_z * L * (1-exp(-N/N_c))
JiangTwoStageModel()             # Stage I (non-rotational) + Stage II (rotational)
JiangThreeStageModel()           # + Stage III (fatigue acceleration)
NortonBaileyCreepModel()         # ΔF = k_sys * L * A * (F0/At)^n * t^m
CombinedMechanismModel()         # Superposition of selected models
```

### 3.2 Friction Models (numerical/friction_models.py)

```python
class CoulombFriction:
    def compute_force(self, velocity: float, normal_force: float) -> float:
        """Returns F_f = -μ(v)*F_n*tanh(v/v_reg)"""

class LuGreFriction:
    def __init__(self, sigma0, sigma1, sigma2, Fs, Fc, vs, alpha):
    def update(self, velocity: float, dt: float) -> float:
        """Updates bristle state z and returns friction force."""

class DahlFriction:
    def __init__(self, sigma, Fc, alpha):
    def update(self, displacement: float) -> float:
        """Updates friction force state (displacement-driven)."""

class IwanFriction:
    def __init__(self, KT, Fs, chi, R, n_elements):
    def compute_force(self, displacement: float) -> float:
        """Returns backbone or unloading curve force."""

class ThreePhaseFrictionEvolution:
    def compute_mu(self, N: int) -> float:
        """Returns μ(N) from three-phase equation."""
```

### 3.3 Time Integration (numerical/time_integration.py)

```python
@dataclass
class TimeParams:
    t_start: float = 0.0
    t_end: float = 1.0
    dt: float = 0.001
    n_steps: int = 0     # Computed from dt if 0

class NewmarkIntegrator:
    def __init__(self, M, K, C, beta=0.25, gamma=0.5):

    def integrate(self, time_params: TimeParams,
                  F_func: Callable,
                  u0: np.ndarray,
                  v0: np.ndarray) -> IntegrationResult:
        """Standard Newmark-β integration (no contact update)."""

    def solve_with_contacts(self, time_params: TimeParams,
                             F_func: Callable,
                             contacts: List[Contact],
                             preload: float,
                             u0: np.ndarray,
                             v0: np.ndarray) -> IntegrationResult:
        """Newmark-β with contact state updates at each step."""

# Same interface for: HHTIntegrator, CentralDifferenceIntegrator,
#                     ModalSuperpositionIntegrator, RungeKutta4Integrator

def create_integrator(method_name: str, M, K, C) -> BaseIntegrator:
    """Factory: 'newmark' | 'hht' | 'central_diff' | 'modal' | 'rk4'"""
```

### 3.4 Coupled Loosening Analyzer (numerical/coupled_loosening_analyzer.py)

```python
@dataclass
class FrictionEvolutionParams:
    model: str = "three_phase"
    mu_initial: float = 0.15
    mu_peak: float = 0.18
    mu_steady: float = 0.10
    mu_minimum: float = 0.03
    N_phase1: int = 50
    N_phase2: int = 500
    mu_thread_initial: Optional[float] = None   # M9: separate thread μ
    mu_bearing_initial: Optional[float] = None  # M9: separate bearing μ

@dataclass
class WearModelParams:
    model: str = "archard"
    K_wear: float = 1e-7
    H_surface: float = 2500e6    # Pa
    fretting_threshold: float = 50e-6  # m

class CoupledLooseningAnalyzer:
    def __init__(self, bolt_geometry, loading_params,
                 friction_params: FrictionEvolutionParams,
                 wear_params: WearModelParams):

    def analyze(self, n_cycles: int) -> LooseningResults: ...

    @classmethod
    def create_analyzer_from_msd_model(cls, model: MSDModel,
                                        **overrides) -> "CoupledLooseningAnalyzer":
        """Creates analyzer from MSD model with 5-level friction hierarchy."""
```

---

## 4. GUI API

### 4.1 MSDBuilderWindow (gui/msd_builder.py)

```python
class MSDBuilderWindow(QMainWindow):
    # Signals
    model_changed = pyqtSignal(dict)     # When any element/contact/loading changes

    # Core methods
    def export_to_msd_model(self) -> MSDModel:
        """Creates MSDModel from current schematic state."""

    def load_from_msd_model(self, model: MSDModel) -> None:
        """Populates builder from existing MSDModel."""

    def load_preset(self, preset_name: str) -> None:
        """Loads built-in preset: 'single_bolt', 'flanged_joint', 'junker_test'."""
```

**SchematicView methods:**
```python
def get_model_data(self) -> List[dict]:
    """Returns current element list as list of dicts."""

def clear_canvas(self) -> None:
    """Removes all elements from scene."""

def select_all(self) -> None:
    """Selects all elements in scene."""
```

**PropertyInspector:**
```python
def get_loading_data(self) -> dict:
    """Returns all loading + friction parameters as dict."""

def set_loading_data(self, data: dict) -> None:
    """Populates inspector from dict (used when loading project)."""

def set_element(self, element: MSDElementData) -> None:
    """Shows element properties and auto-switches to correct inspector tab."""

def set_transverse_stiffness(self, k_trans: float) -> None:
    """Updates k_transverse for force↔displacement auto-conversion."""
```

### 4.2 BoltAnalysisStudio (gui/main_window.py)

Main window with 6-tab interface.

**Tab indices:**
- 0: Project Tab
- 1: Model (MSD Builder)
- 2: Solver
- 3: Results
- 4: Similitude  ← (fixed from 5 in BATCH 1)
- 5: Reports

**Key methods:**
```python
def _on_msd_builder_model_changed(self, model_data: dict) -> None:
    """Triggered when builder model changes. Exports model, updates all dependents."""

def _run_analysis(self) -> None:
    """Starts SolverWorker for selected analysis type."""

def _generate_report_html(self) -> str:
    """Generates HTML report from current model + results."""

def _on_results_changed(self, results: AnalysisResult) -> None:
    """Updates ResultsTab when analysis completes."""

def _on_similitude_scaling_computed(self, scaling_result) -> None:
    """Stores similitude result in AppState."""
```

### 4.3 MatrixViewerDialog (gui/matrix_viewer.py)

```python
class MatrixViewerDialog(QDialog):
    def show_model(self, model: MSDModel) -> None:
        """Populates all tabs from model matrices."""

    def refresh_from_model(self) -> None:
        """Re-reads current AppState.model and updates display."""
```

Tabs: [M] Mass | [K] Stiffness | [C] Damping | {F} Force | Loading Config | Friction

---

## 5. Visualization API

### 5.1 Plotter Classes (visualization/loosening_plots.py)

```python
class PreloadLossPlotter:
    def plot_preload_vs_cycles(self, result: PreloadAnalysisResult,
                               ax=None) -> Figure: ...
    def plot_all_models_comparison(self, results: List[PreloadAnalysisResult],
                                   ax=None) -> Figure: ...

class CoupledLooseningResultsPlotter:
    """Rich plotter for coupled friction-wear-loosening results."""
    def plot_preload_friction_evolution(self, results: LooseningResults) -> Figure: ...
    def plot_phase_diagram(self, results: LooseningResults) -> Figure: ...
    def plot_torque_balance(self, results: LooseningResults) -> Figure: ...
    def plot_wear_accumulation(self, results: LooseningResults) -> Figure: ...
    def plot_loosening_rate_evolution(self, results: LooseningResults) -> Figure: ...
    def plot_comprehensive_dashboard(self, results: LooseningResults) -> Figure: ...

class FrictionEvolutionPlotter:
    def plot_friction_vs_cycles(self, mu_array, N_array, ax=None) -> Figure: ...
    def plot_stribeck_curve(self, friction_params, ax=None) -> Figure: ...

class WearEvolutionPlotter:
    def plot_wear_depth(self, wear_array, N_array, ax=None) -> Figure: ...

class DNPlotter:
    def plot_dn_curve(self, displacements, life_cycles, ax=None) -> Figure: ...

class CoupledAnalysisPlotter:
    def plot_coupled_evolution(self, result: CoupledLooseningResult,
                               quantity: str, ax=None) -> Figure: ...
```

### 5.2 Helper Functions

```python
def setup_plot_style() -> None:
    """Applies Catppuccin Mocha dark theme to matplotlib."""

def create_comprehensive_dashboard(results: LooseningResults) -> Figure:
    """Creates 6-panel summary figure."""

def quick_preload_loss_plot(cycles, preload, F0) -> Figure:
    """One-line convenience for rapid preload plots."""

def quick_friction_plot(N, mu_array) -> Figure:
    """One-line convenience for friction evolution plots."""
```

---

## 6. Key Enumerations

```python
# core/models/element.py
class ElementType(Enum):
    HEAD = "HEAD"; SHANK = "SHANK"; THREAD = "THREAD"; NUT = "NUT"
    WASHER_FLAT = "WASHER_FLAT"; WASHER_SPRING = "WASHER_SPRING"
    WASHER_BELLEVILLE = "WASHER_BELLEVILLE"; WASHER_NORDLOCK = "WASHER_NORDLOCK"
    FLANGE_WELD_NECK = "FLANGE_WELD_NECK"; FLANGE_SLIP_ON = "FLANGE_SLIP_ON"
    FLANGE_BLIND = "FLANGE_BLIND"; GASKET = "GASKET"; GROUND = "GROUND"
    CONTACT_THREAD = "CONTACT_THREAD"; CONTACT_BEARING = "CONTACT_BEARING"
    CONTACT_INTERFACE = "CONTACT_INTERFACE"

# core/contacts/base.py
class ContactType(Enum):
    THREAD_CONTACT = "THREAD_CONTACT"
    BEARING_HEAD = "BEARING_HEAD"; BEARING_NUT = "BEARING_NUT"
    WASHER_FLANGE = "WASHER_FLANGE"; FLANGE_FLANGE = "FLANGE_FLANGE"
    FLANGE_GASKET = "FLANGE_GASKET"; HEAD_FLANGE = "HEAD_FLANGE"
    NUT_FLANGE = "NUT_FLANGE"

class SlipState(Enum):
    STICK = "STICK"; PARTIAL = "PARTIAL"; GROSS_SLIP = "GROSS_SLIP"

class WearModel(Enum):
    ARCHARD = "ARCHARD"; ENERGY_BASED = "ENERGY_BASED"
    FRETTING = "FRETTING"; OXIDATIVE = "OXIDATIVE"

class StiffnessModel(Enum):
    LINEAR = "LINEAR"; NONLINEAR = "NONLINEAR"
    ELASTOPLASTIC = "ELASTOPLASTIC"; VISCOELASTIC = "VISCOELASTIC"

# core/models/model.py
class LoadingType(Enum):
    AXIAL = "AXIAL"; TRANSVERSE = "TRANSVERSE"; COMBINED = "COMBINED"
    TORSIONAL = "TORSIONAL"; BENDING = "BENDING"

# numerical/coupled_loosening_analyzer.py
class LoadDistribution(Enum):
    EQUAL = "EQUAL"; LINEAR = "LINEAR"; POWER_LAW = "POWER_LAW"
    EXPONENTIAL = "EXPONENTIAL"; YAMAMOTO = "YAMAMOTO"
```

---

## 7. Project I/O

```python
# core/project_io.py
def save_project(app_state: AppState, file_path: str) -> None:
    """Saves complete project (model + results + metadata) to .msd JSON file."""

def load_project(file_path: str) -> AppState:
    """Loads project from .msd file. Handles version migration."""

def export_report_pdf(app_state: AppState, file_path: str) -> None:
    """Exports PDF report via Qt print."""

def export_report_html(app_state: AppState, file_path: str) -> None:
    """Exports HTML report with embedded CSS."""

def export_report_csv(app_state: AppState, file_path: str) -> None:
    """Exports data tables as CSV."""
```

---

## 8. Similitude API

```python
# core/similitude/similitude.py
class SimilitudeAnalysis:
    pi_groups: List[PiGroup]    # Buckingham Π groups
    scale_factors: dict         # Geometric scale factors
    correction_factors: dict    # Load correction factors

    def compute(self, reference_joint: MSDModel,
                target_joint: MSDModel) -> SimilitudeResult: ...

    def get_pi_groups(self) -> List[PiGroup]: ...

# core/similitude/loosening_similitude.py
class LooseningSimilitudeAnalysis:
    def reduce_multi_bolt(self, bolt_pattern: List[MSDModel]) -> MSDModel:
        """Reduces multi-bolt pattern to equivalent single-bolt model."""

    def apply_geometric_scaling(self, model: MSDModel,
                                scale: float) -> MSDModel:
        """Scales model by geometric scale factor."""

# gui/similitude_tab.py
class EnhancedSimilitudeTab(QWidget):
    import_from_model_requested = pyqtSignal()
    scaling_computed = pyqtSignal(object)   # SimilitudeResult
    send_to_solver = pyqtSignal(object)     # Scaled MSDModel

    def populate_from_model(self, model: MSDModel) -> None:
        """Imports bolt geometry from MSD model."""

    def compute_similitude(self) -> None:
        """Runs full Buckingham Π analysis and updates UI."""
```

---

## 9. Utility Functions

```python
# gui/msd_builder.py
def _fmt_eng(value: float, unit: str = "") -> str:
    """Format value with SI prefix: 1.85e9 N/m → '1.85 GN/m'"""

# gui/theme.py
class Theme:
    BLUE = "#89b4fa"; GREEN = "#a6e3a1"; RED = "#f38ba8"
    YELLOW = "#f9e2af"; SURFACE0 = "#313244"; SURFACE1 = "#45475a"
    OVERLAY = "#6c7086"; BASE = "#1e1e2e"; TEXT = "#cdd6f4"
    MAUVE = "#cba6f7"; TEAL = "#94e2d5"; PEACH = "#fab387"
    SAPPHIRE = "#74c7ec"; SKY = "#89dceb"; FLAMINGO = "#f2cdcd"
```

---

*See also: ARCHITECTURE.md, NUMERICAL_MODELS.md, CONTACTS.md, COUPLING_AUDIT.md*
