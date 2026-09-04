# MODEL COUPLING STUDY
## Bolt Analysis Studio v4.0 — Complete Coupling Architecture Audit

**Date:** 2026-02-18
**Scope:** All coupling pathways across GUI, Core, Numerical, and Visualization layers
**Method:** Static analysis of source code + signal tracing + data flow mapping
**Classification System:** CRITICAL / HIGH / MEDIUM / LOW

---

## 1. EXECUTIVE SUMMARY

The software has **4 architectural layers** (GUI → Core → Numerical → Visualization) and is fundamentally well-structured. The primary data flow from MSD Builder → Solver → Results is functional. However, the audit found **16 coupling gaps** across those layers, including 3 CRITICAL issues that affect analysis correctness.

### Severity Matrix

| Severity | Count | Impact |
|----------|-------|--------|
| CRITICAL | 3 | Wrong numerical results or dead code pathways |
| HIGH | 4 | Analysis missing key physical effects |
| MEDIUM | 5 | Incomplete integration between features |
| LOW | 4 | Minor inaccuracies or UX inconsistencies |

### What IS Well-Coupled

- GUI signal chain: `PropertyInspector → MSDBuilderWindow → AppState → SolverTab` ✓
- Matrix assembly: contacts contribute stiffness/damping to [K] and [C] ✓
- `CoupledLooseningAnalyzer` with 3-phase friction + nonlinear wear + Archard/Fouvry ✓
- Per-thread state tracking (friction, wear, slip distance accumulation) ✓
- Per-surface initial friction via M9 feature (mu_thread_initial, mu_bearing_initial) ✓
- MSDModel.to_dict()/from_dict() round-trip persistence for model structure ✓
- Results → ResultsTab plotting for coupled loosening ✓
- Helix coupling in ThreadContact [K] contributions ✓

---

## 2. LAYER ARCHITECTURE OVERVIEW

```
┌──────────────────────────────────────────────────────────────────────┐
│  GUI LAYER                                                           │
│  main_window.py (6 tabs) │ msd_builder.py │ matrix_viewer.py       │
│  similitude_tab.py       │ theme.py                                 │
└──────────────────┬───────────────────────────────────┬──────────────┘
                   │ pyqtSignal chains                  │ AppState signals
                   ▼                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│  CORE LAYER                                                          │
│  core/app_state.py (AppState singleton)                             │
│  core/models/model.py (MSDModel + matrix assembly)                  │
│  core/models/element.py (MSDElementData dataclasses)                │
│  core/contacts/ (Contact ABC + 5 subclasses)                        │
│  core/solver_worker.py (SolverWorker QThread)                       │
└──────────────────┬───────────────────────────────────┬──────────────┘
                   │ function calls                     │ result objects
                   ▼                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│  NUMERICAL LAYER                                                     │
│  numerical/coupled_loosening_analyzer.py (primary solver)           │
│  numerical/preload_loss_models.py (8 decay models)                  │
│  numerical/friction_models.py (6 friction models)                   │
│  numerical/time_integration.py (5 integrators)                      │
│  core/similitude/similitude.py (Pi groups)                          │
└──────────────────┬───────────────────────────────────────────────────┘
                   │ result dataclasses
                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  VISUALIZATION LAYER                                                 │
│  visualization/loosening_plots.py (LooseningPlotter — 16 plot types)│
│  visualization/plot_manager.py (PlotWidget, PlotManager)            │
│  core/similitude/similitude_plots.py (ScaleCharts)                  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. COMPLETE DATA FLOW MAP

### 3.1 GUI → MSDModel (Loading Configuration)

```
PropertyInspector spinboxes (msd_builder.py:3757–3890)
    │ valueChanged → _on_*_changed() → loading_changed.emit(dict)
    ▼
MSDBuilderWindow._on_loading_changed(data) (msd_builder.py:6792)
    │ caches data → updates overlays → model_changed.emit({"source":"loading", ...})
    ▼
BoltAnalysisStudio._on_msd_builder_model_changed(model_data) (main_window.py:4365)
    │ calls export_to_msd_model() → AppState.model = msd_model
    │ calls solver_tab.update_loading_summary(loading_data)
    ▼
SolverTab.update_loading_summary(loading_data) (main_window.py:864)
    │ updates display labels
    │ sets hidden spinboxes (amplitude_spin, trans_disp_spin, n_cycles_spin, etc.)
    ▼ [COUPLING GAP: no reverse signal from Solver → Builder — see HIGH-04]
```

**Payload carried (PropertyInspector.get_loading_data() dict):**
```python
{
    "type": str,               # "Axial" / "Transverse" / "Combined" ...
    "F_preload": float,        # N  (from preload_spin)
    "preload_percent_yield": float,
    "F_transverse": float,     # N
    "delta_amplitude": float,  # mm (auto-converted from force via k_transverse)
    "frequency": float,        # Hz
    "n_cycles": int,           # auto-calculated = freq × integration_time
    "mu_initial": float,       # 0.01–0.50
    "lubricated": bool,
    "bolt_diameter": float,    # mm
    "pitch": float,            # mm
    "F_external": float,
    "T_applied": float,
    "delta_T": float,
}
```

### 3.2 MSDModel → Matrix Assembly (Contact Coupling)

```
MSDModel.assemble_matrices()  (model.py:540–577)
    │
    ├─ For each element: compute bulk M, K, C contributions (series/parallel)
    │
    └─ HAS_CONTACTS guard: if contacts list non-empty:
           For each Contact object:
               contact.get_stiffness_contribution() → list[(row,col,k_val)]
                   ├─ ThreadContact: axial + helix off-diagonal terms
                   │   k_helix = k_thread × (p/2π) at (axial_stud, theta_nut) DOFs
                   ├─ BearingContact: high k at (bolt_head, flange) DOFs
                   └─ FlangeGasketContact: nonlinear k(δ) at (flange, gasket) DOFs
               contact.get_damping_contribution() → list[(row,col,c_val)]
    │
    └─ Returns M, K, C (cached, recomputed when _is_dirty=True)

MSDModel.assemble_force_vector(x, x_dot, t, F_external, preload)  (model.py:579–638)
    │
    └─ For each Contact: contact.get_force_contribution(x, x_dot, t)
           ├─ ThreadContact: helix torque (loosening), per-thread friction
           ├─ BearingContact: rotational friction torque (resisting torque)
           └─ FlangeGasketContact: creep, plastic forces
    │
    └─ Stores tribological contribution in _F_tribo
    └─ Returns F_ext + F_tribo

[CRITICAL GAP-01: assemble_force_vector is NOT called during time integration]
```

### 3.3 MSDModel → CoupledLooseningAnalyzer

```
create_analyzer_from_msd_model(model)  (coupled_loosening_analyzer.py:2289)
    │
    ├─ Scans ElementType: THREAD → diameter, pitch, grip_length
    │                     SHANK  → diameter fallback
    │                     FLANGE → thickness for grip
    │
    ├─ Gets preload from: model.global_loading.F_preload  (primary)
    │
    ├─ Gets transverse from: model.global_loading.F_transverse  (primary)
    │
    ├─ Gets friction from: model.mu_initial  (scalar — ignores contact objects!)
    │   [HIGH GAP-01: ThreadContact.friction.mu_static ignored]
    │
    ├─ Computes stiffness via: compute_contact_stiffnesses(d, p, E, Sy, L)
    │   [HIGH GAP-02: uses VDI formula, not assembled [K] from contacts]
    │
    └─ Returns (CoupledLooseningAnalyzer, extraction_info)
```

### 3.4 SolverWorker → CoupledLooseningAnalyzer (Analysis Execution)

```
SolverWorker.run() (solver_worker.py:295)
    │
    └─ For "run_all" or "coupled":
           _run_coupled_loosening_analysis(config)
               │
               └─ If model available: create_analyzer_from_msd_model(model)
                  Else: use config scalars (bolt_diameter_mm, pitch_mm, ...)
               │
               └─ analyzer.analyze_loosening(n_cycles, sample_interval)
                       For each cycle:
                           FrictionEvolutionParams.compute_mu(N, wear_depth, T)
                           WearModelParams.compute_wear_increment(F_n, slip, N, depth, T)
                           LooseningPhase transition logic
               │
               └─ Returns CoupledLooseningResult
                       cycles[], preload[], mu_thread[], mu_bearing[]
                       wear_um[], loosening_angle_deg[], loosening_rate[]
                       torque_margin[], friction_margin[], phase[]

       _run_time_integration(model, config)
               │
               └─ model.assemble_matrices() → M, K, C  [assembled ONCE]
               └─ Creates F_func (harmonic/step/pulse — fixed amplitude)
               └─ integrator.integrate(time_params, F_func, u0, v0)
               │   [CRITICAL GAP-01: no contact.update_state() per step]
               │   [CRITICAL GAP-01: no assemble_force_vector() per step]
               └─ Returns TimeIntegrationResult
                       time[], displacement[], velocity[], acceleration[]
```

### 3.5 Results → AppState → Visualization

```
SolverWorker.finished.emit(result: AnalysisResult)
    │
    ▼
BoltAnalysisStudio._on_analysis_finished(result)  (main_window.py:2456)
    │ AppState.results = result → results_changed signal
    │
    ▼
BoltAnalysisStudio._on_results_changed(results)  (main_window.py:2466)
    │
    ▼
ResultsTab.results_tree itemClicked → _on_result_category_selected(item)
    │ reads text of selected category
    │
    ├─ "Preload" → results.preload_result or results.coupled_loosening_result
    ├─ "Phase Diagram" → results.coupled_loosening_result
    ├─ "Friction Evolution" → results.coupled_loosening_result
    ├─ "Wear Accumulation" → results.coupled_loosening_result
    ├─ "Loosening" → results.coupled_loosening_result
    ├─ "Torque Balance" → results.coupled_loosening_result
    ├─ "Contact Forces" → results.coupled_loosening_result
    └─ "Time Response" → results.time_result
    │
    └─ Inline plot methods in main_window.py (lines 2593–3040)
       using results_tab.plot_widget.canvas (PlotWidget from plot_manager.py)
       [CRITICAL GAP-02: loosening_plots.LooseningPlotter never called]
```

---

## 4. COUPLING GAPS — DETAILED ANALYSIS

---

### CRITICAL-01: Time Integration Does Not Include Contact Tribology

**Location:** `solver_worker.py:525–639` — `_run_time_integration()`
**Severity:** CRITICAL — Analysis produces incomplete physical results

**What happens:**
```python
# solver_worker.py:536
M, K, C = model.assemble_matrices()  # called ONCE before integration
# ...
result = integrator.integrate(time_params, F_func, u0, v0)  # no contact update!
```

The [M], [K], [C] matrices include contact stiffness and damping contributions (from `get_stiffness_contribution()` and `get_damping_contribution()`). However:

- `assemble_force_vector()` is **never called** during integration steps
- `contact.update_state()` is **never called** at any step
- Friction forces, helix torque, bearing friction, gasket creep — all absent
- Friction evolution, wear accumulation — do not happen
- The F_func passed to integrator is a simple harmonic/step/pulse with fixed amplitude

**Physical consequence:** Time domain response shows pure linear vibration with constant damping. Stick-slip transitions, rotational loosening contribution, and preload decay during the time window are all missing.

**What should happen:**
```python
# At each time step:
F_total = model.assemble_force_vector(x[n], x_dot[n], t[n], F_external[n], current_preload)
for contact in model.contacts:
    contact.update_state(x[n], x_dot[n], dt, current_preload)
current_preload -= sum(c.get_preload_loss(k_system) for c in model.contacts)
```

**Fix approach:** Implement a callback-based integration loop in `SolverWorker._run_time_integration()` that calls `model.assemble_force_vector()` and `contact.update_state()` per step, replacing the single `integrator.integrate()` call.

---

### CRITICAL-02: LooseningPlotter Visualization Module Is Dead Code

**Location:** `visualization/loosening_plots.py` — imported but never called
**Severity:** CRITICAL — 16-plot visualization system unused

**Evidence:**
```python
# visualization/__init__.py:15 — imports LooseningPlotter
from .loosening_plots import (...)

# main_window.py:36 — only imports PlotWidget from plot_manager
from bolt_analysis_studio.visualization.plot_manager import PlotWidget, PlotManager, PlotEditorWindow
```

`main_window.py` has inline plot methods (lines 2593–3040) that directly draw matplotlib figures onto `results_tab.plot_widget.canvas`. The `LooseningPlotter` class with its 16 specialized plot types is never instantiated.

**Impact:**
- Any improvements to `loosening_plots.py` will have no effect on UI
- Duplication: inline methods and LooseningPlotter implement the same charts in two places
- If `loosening_plots.py` was recently improved (e.g., with scientific annotations), those improvements are invisible

**Fix approach:** Replace all inline plot methods in `main_window.py` (lines 2593–3040) with calls to `LooseningPlotter(cl_result).plot_*()` methods using the existing `results_tab.plot_widget`.

---

### CRITICAL-03: SimilitudeAnalysis Engine (similitude.py) Never Called

**Location:** `core/similitude/similitude.py` — `SimilitudeAnalysis` class
**Severity:** CRITICAL — Rich Buckingham-Π analysis is dead code

**Evidence:**
```python
# similitude_tab.py — uses different module
from bolt_analysis_studio.core.similitude.loosening_similitude import (
    create_scaled_loosening_model, EquivalentSingleBolt
)
# similitude.py's SimilitudeAnalysis with 5 Pi groups is never imported in GUI
```

The `SimilitudeAnalysis` class (similitude.py) computes 5 dimensionless Pi groups, 4 scale effect corrections, and 20 derived scale factors. The GUI uses the simpler `create_scaled_loosening_model()` from `loosening_similitude.py`, which bypasses this engine.

Additionally: similitude results are not stored in AppState → Reports tab has no access.

**Fix approach:**
1. Connect `EnhancedSimilitudeTab._on_scaling_computed()` to call `SimilitudeAnalysis.run()`
2. Add `AppState.similitude_result` field
3. Emit `AppState.similitude_changed` signal
4. Reports tab subscribes to this signal

---

### HIGH-01: Contact Friction Parameters Ignored in Coupled Loosening

**Location:** `coupled_loosening_analyzer.py:2289` — `create_analyzer_from_msd_model()`
**Severity:** HIGH — Contact-level friction setup overridden by global scalar

**What happens:**
```python
# create_analyzer_from_msd_model() — uses GLOBAL scalar
mu_initial_used = mu_initial if mu_initial is not None else getattr(model, 'mu_initial', 0.12)
# ThreadContact.friction.mu_static is NEVER read here
```

When the user defines a ThreadContact in MSD Builder with specific `FrictionProperties` (mu_static=0.15, mu_kinetic=0.12, Stribeck model), these values are completely ignored. The analyzer uses only `model.mu_initial` (a single scalar).

**The contact-level data that should be extracted:**
```python
for tc in model.contacts:
    if isinstance(tc, ThreadContact):
        mu_thread = tc.friction.mu_static
    if isinstance(tc, BearingContact):
        mu_bearing = tc.friction.mu_static
```

**Fix approach:** In `create_analyzer_from_msd_model()`, scan contacts for `ThreadContact` and `BearingContact` instances and extract their friction model parameters.

---

### HIGH-02: Assembled [K] Stiffness Not Used for Loosening Analysis

**Location:** `coupled_loosening_analyzer.py:2445` — stiffness extraction
**Severity:** HIGH — Parallel stiffness calculation may diverge from model

**What happens:**
```python
# create_analyzer_from_msd_model() calls VDI formula standalone
stiffnesses = compute_contact_stiffnesses(bolt_d_mm, pitch_mm, E_MPa, Sy_MPa, grip_mm)
k_bolt = stiffnesses['k_bolt']
k_member = stiffnesses['k_members']
```

This calls the standalone `compute_contact_stiffnesses()` function which applies VDI 2230 formulas to the extracted geometry. It does NOT read from the assembled [K] matrix where `ThreadContact.get_stiffness_contribution()` has already placed the helix-coupled stiffness terms.

**Consequence:** If the user modifies contact stiffnesses in the MSD Builder (e.g., adds a FlangeGasketContact with nonlinear k(δ)), those modifications don't reach the coupled loosening analyzer.

**Fix approach:** After `model.assemble_matrices()` is called, extract system stiffness from the assembled [K] by reading the diagonal and off-diagonal entries at the DOFs that correspond to the bolt/member load path.

---

### HIGH-03: Analysis Results Not Restored on Project Load

**Location:** `core/app_state.py:545` — `from_dict()`
**Severity:** HIGH — Loss of results when saving/loading project

**Evidence:**
```python
# app_state.py — from_dict() always clears results
self._results = None  # Results not serialized
```

When a user saves a project (.msd file) and reopens it:
- All elements, contacts, and loading parameters are restored ✓
- All analysis results (preload curves, loosening history, time response) are lost ✗
- ResultsTab shows empty state ✗
- User must re-run analysis after every project open

**Fix approach:**
1. Add `AnalysisResult.to_dict()` / `from_dict()` serialization
2. Include in project .msd file under `"analysis_results"` key
3. Restore in `AppState.from_dict()` with backward-compatibility fallback (results key absent = None)

Note: For large time integration results (displacement arrays), consider separate storage file or optional flag.

---

### HIGH-04: No Reverse Signal Flow (Solver Tab → MSD Builder)

**Location:** `main_window.py:1945–1948` — solver spinbox connections
**Severity:** HIGH — Model state diverges silently from UI state

**What happens:**
```python
# Solver tab hidden spinboxes are updated by update_loading_summary():
self.solver_tab.n_cycles_spin.setValue(cycles)  # triggers valueChanged!

# n_cycles_spin.valueChanged is connected to:
self.solver_tab.n_cycles_spin.valueChanged.connect(self._auto_calculate_timestep)
# → _auto_calculate_timestep() only, NOT → MSD Builder inspector
```

If a user edits `n_cycles_spin` directly in the Solver Tab (or if any validation case resets it), the MSD Builder's PropertyInspector keeps showing the old value. The model stored in AppState and the UI display diverge.

**Fix approach:**
- Remove direct edits to `n_cycles_spin` from the Solver Tab (hide the field completely)
- OR add a reverse signal: when `n_cycles_spin.valueChanged`, push back to PropertyInspector via `msd_builder_window.inspector.set_loading_data()`
- OR enforce read-only on all hidden spinboxes in SolverTab

---

### MEDIUM-01: Transverse Stiffness k_transverse Fixed at Default

**Location:** `msd_builder.py:3238` — PropertyInspector
**Severity:** MEDIUM — Force/displacement auto-conversion inaccurate

**What happens:**
```python
# msd_builder.py:3238
self._k_transverse = 1.54e7  # N/m — HARDCODED DEFAULT
```

The PropertyInspector converts between transverse force and transverse displacement using `_k_transverse`. This value is never updated when the model changes or matrices are assembled. The conversion may be off by orders of magnitude for small bolts or stiff flanges.

**Fix approach:** After `model.assemble_matrices()` returns, extract the joint transverse stiffness from the assembled [K] matrix (the diagonal entry at the flange interface DOF) and call `PropertyInspector.set_transverse_stiffness(k_trans)`.

---

### MEDIUM-02: Preload Not Tracked During Time Integration Contact Updates

**Location:** `model.py:585` — `assemble_force_vector()` parameter
**Severity:** MEDIUM — Contact tribological forces scale with wrong preload

**What happens:**
```python
def assemble_force_vector(self, x, x_dot, t, F_external, preload: float = 0.0):
    # preload defaults to 0.0!
    contact.normal_force = preload  # contact friction scales with this
```

Even if `assemble_force_vector()` were called during integration (it isn't — see CRITICAL-01), the `preload` parameter defaults to 0.0. Contact friction forces (which scale with normal force = preload) would all be zero.

The model has no `current_preload` state variable. Preload loss is tracked in `CoupledLooseningAnalyzer` internally but never fed back to MSDModel.

**Fix approach:** Add `MSDModel.current_preload: float = 0.0` field, initialized from `global_loading.F_preload`. Update it as integration proceeds via preload loss callbacks.

---

### MEDIUM-03: AppState Has No Similitude Field

**Location:** `core/app_state.py` — AppState class
**Severity:** MEDIUM — Similitude results invisible to Reports and other tabs

**What happens:**
```python
class AppState(QObject):
    project_changed = pyqtSignal(object)
    model_changed = pyqtSignal(object)
    results_changed = pyqtSignal(object)
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    # NO similitude_changed signal
    # NO _similitude field
```

Similitude results (`ScaledLooseningModel`, `EquivalentSingleBolt`, `LooseningSimlitudeAnalysis`) are computed within `EnhancedSimilitudeTab` and stored only as local widget state. They cannot reach:
- Reports tab (for PDF/HTML export)
- Results tab (for overlay on loosening curves)
- Project save/load (not in .msd JSON)

**Fix approach:**
```python
# app_state.py additions
similitude_changed = pyqtSignal(object)   # new signal
_similitude_result: Optional[Any] = None  # new field

@property
def similitude_result(self):
    return self._similitude_result
@similitude_result.setter
def similitude_result(self, value):
    self._similitude_result = value
    self.similitude_changed.emit(value)
```

---

### MEDIUM-04: Similitude Tab Index Bug (reproduced from SIMILITUDE_STUDY)

**Location:** `main_window.py:4336`
**Severity:** MEDIUM — Navigation button opens wrong tab

```python
# WRONG: index 5 = Reports tab
similitude_tab_index = 5
# CORRECT: index 4 = Similitude tab
```

---

### MEDIUM-05: nut Inertia Hardcoded in ThreadContact

**Location:** `contacts/thread_contact.py` — ThreadContact constructor
**Severity:** MEDIUM — Torsional DOF inertia inaccurate for non-M16 bolts

```python
# thread_contact.py (approximate location)
J_nut = 0.5 * 0.05 * r_nut**2  # 0.05 kg hardcoded — should be from nut element mass
```

The rotational inertia of the nut at the torsional DOF uses a hardcoded 0.05 kg regardless of bolt size or material. For M8 bolts (1/4 the mass) or alloy nuts, this introduces up to 4× error in modal analysis of torsional modes.

**Fix approach:** Pass `nut_element.mass` from the NUT element when creating ThreadContact. Fall back to `0.5 × rho × π × d^2/4 × L_nut` computed from geometry.

---

### LOW-01: Contact Dispatch Map Missing WasherFlangeContact Key

**Location:** `model.py:100–110` — `_CONTACT_TYPE_MAP`
**Severity:** LOW — Deserialization uses fallback prefix match

```python
# model.py uses prefix match as workaround:
if ct.startswith("WASHER_"):
    ...
# Instead of explicit:
"WASHER_FLANGE": WasherFlangeContact,
```

This works but is fragile. If contact type names change, deserialization silently fails.

**Fix:** Add all contact types explicitly to `_CONTACT_TYPE_MAP`.

---

### LOW-02: Coulomb Model Returns 0 When Stuck (Missing Static Reaction)

**Location:** `contacts/base.py:183` — `FrictionProperties.get_friction_force()`
**Severity:** LOW — Incorrect static friction behavior

```python
# base.py — COULOMB model
if abs(velocity) < v_reg:
    return 0.0  # WRONG: should return static friction up to mu_s*N
```

When the contact is stuck (`|v| < v_reg`), the friction force should be whatever force is needed to maintain equilibrium (bounded by μ_static × N). Returning 0 means the stuck contact provides no force, which may cause erroneous slip detection.

**Fix:** Return `min(applied_tangential_force, mu_static * normal_force) * sign(applied_tangential_force)` when stuck.

---

### LOW-03: Reports Tab Does Not Include Time Integration Results

**Location:** `main_window.py:_generate_report_html()`
**Severity:** LOW — Time response data missing from exported reports

The HTML/PDF report generation reads `AppState.results.coupled_loosening_result` and `preload_result`, but never accesses `results.time_result`. Max displacement, max velocity, natural frequencies are not included in any report section.

**Fix:** Add a "Dynamic Analysis" section to `_generate_report_html()` from `results.time_result`.

---

### LOW-04: Matrix Viewer {F} Tab Is Not Live-Updating

**Location:** `gui/matrix_viewer.py` — `MatrixViewerDialog`
**Severity:** LOW — Users see stale force vector

The Matrix Viewer dialog shows a snapshot of the force vector when opened. If the user changes loading parameters in the MSD Builder while the dialog is open, the {F} tab is not refreshed.

**Fix:** Connect `AppState.model_changed` to `MatrixViewerDialog._refresh_force_tab()` if the dialog is visible.

---

## 5. CONTACT SYSTEM COUPLING STATUS

### Contact Type Coverage

| Contact Type | `get_stiffness_contribution()` | `get_damping_contribution()` | `get_force_contribution()` | `update_state()` | Called in time integration? |
|---|---|---|---|---|---|
| ThreadContact | ✓ with helix coupling | ✓ | ✓ friction + helix torque | ✓ | ✗ CRITICAL-01 |
| BearingContact (Head) | ✓ high k | ✓ friction equiv c | ✓ resisting torque | ✓ | ✗ CRITICAL-01 |
| BearingContact (Nut) | ✓ high k | ✓ friction equiv c | ✓ resisting torque | ✓ | ✗ CRITICAL-01 |
| FlangeGasketContact | ✓ nonlinear k(δ) | ✓ high viscoelastic c | ✓ creep + plastic | ✓ | ✗ CRITICAL-01 |
| FlangeFlangeContact | ✓ very high k_c | ✓ low c (fretting) | ✓ fretting forces | ✓ | ✗ CRITICAL-01 |
| WasherFlangeContact | ✓ contact k | ✓ | ✓ embedding | ✓ | ✗ CRITICAL-01 |

**All 6 contact types** have complete implementations of the 4 abstract methods. The coupling failure is exclusively in the solver layer (CRITICAL-01), not in the contact implementations themselves.

### Helix Coupling Verification

ThreadContact correctly implements the axial-torsional coupling required for Junker loosening:

```python
# Stiffness contributions from ThreadContact
(dof_axial_stud, dof_axial_nut, +k_thread)   # axial stiffness
(dof_axial_stud, dof_axial_nut, -k_thread)
(dof_theta_stud, dof_theta_nut, +k_torsional) # torsional stiffness
# Helix coupling off-diagonal terms:
(dof_axial_stud, dof_theta_nut, +k * lambda)  # λ = p/(2π) [m/rad]
(dof_axial_nut,  dof_theta_stud, +k * lambda)
```

This coupling is assembled into [K] correctly via `assemble_matrices()`. The issue is that this matrix is computed once and integration proceeds without per-step contact force updates (CRITICAL-01).

---

## 6. NUMERICAL MODEL COUPLING STATUS

### Friction Evolution — CoupledLooseningAnalyzer

**Status: FULLY COUPLED within analyzer**

```
FrictionEvolutionParams.compute_mu(cycles, wear_depth_um, temperature)
    ├─ Phase 1 (running-in 0→N1): mu rises from mu_initial to mu_peak
    ├─ Phase 2 (transition N1→N2): mu decays
    ├─ Phase 3 (steady N2→N3): mu approaches mu_steady
    ├─ Wear degradation: -wear_degradation_rate × wear_depth_um
    └─ Temperature: -temperature_factor × max(0, T-20)

compute_mu_for_surface(surface='thread'|'bearing', ...)
    └─ M9 feature: separate mu_thread_initial, mu_bearing_initial overrides
```

**Coupling gap:** This model is self-contained within `CoupledLooseningAnalyzer`. It does NOT read from `contacts/base.py FrictionProperties` objects — see HIGH-01.

### Wear Evolution — WearModelParams (CoupledLooseningAnalyzer)

**Status: FULLY COUPLED within analyzer**

```
WearModelParams.compute_wear_increment(F_n, slip, cycles, depth, T, mu)
    ├─ Generalized Archard: dh = K(cycles,depth,T) × (p/H)^α × v^β × ds
    │   K evolves: K_running_in → K_steady → K_severe → K_catastrophic
    │   Roughening feedback: K × (1 + compliance_rate × depth_um)
    ├─ Fouvry energy wear: V = α_V × max(0, E_d - E_th)
    │   Energy threshold, logarithmic acceleration with accumulated E
    └─ Returns (wear_increment, breakdown_dict)
```

**Coupling gap:** Not connected to `contacts/base.py WearProperties` — two parallel wear implementations exist.

### Preload Loss Models (preload_loss_models.py)

**Status: PARTIALLY COUPLED**

The 8 decay models (SingleExponential, DoubleExponential, StretchedExponential, PowerLaw, Logarithmic, Polynomial, Jiang Two-Stage, Jiang Three-Stage) are used in `_run_preload_analysis()`. Their output (`PreloadAnalysisResult`) goes to the Results tab.

However, the preload decay they compute does NOT feed back into:
- Contact normal forces (friction forces remain constant during time integration)
- ThreadContact helix coupling (loosening angle not accumulated in time integration)
- CoupledLooseningAnalyzer (which has its own internal preload tracking)

**Three parallel preload tracking mechanisms exist (unconnected):**
1. `PreloadAnalysisResult` from preload_loss_models.py (parametric decay curves)
2. `CoupledLooseningResult.preload[]` from CoupledLooseningAnalyzer (physics-based per-cycle)
3. `WearProperties.get_preload_loss(k_system)` in Contact base class (instantaneous wear-based)

---

## 7. VISUALIZATION LAYER COUPLING

### loosening_plots.py (LooseningPlotter)

**Status: IMPORTED but NOT CALLED**

```python
# visualization/__init__.py imports these (correct):
from .loosening_plots import (LooseningPlotter, PlotConfig, PlotType, ...)

# main_window.py only imports (misses LooseningPlotter):
from bolt_analysis_studio.visualization.plot_manager import PlotWidget, ...
```

All 16 plot types in `LooseningPlotter` are re-implemented inline in `main_window.py` methods:

| LooseningPlotter method | main_window.py inline method |
|---|---|
| `plot_preload_decay()` | `_plot_coupled_loosening(cl, "preload")` |
| `plot_friction_evolution()` | `_plot_coupled_loosening(cl, "friction")` |
| `plot_wear_accumulation()` | `_plot_coupled_loosening(cl, "wear")` |
| `plot_loosening_angle()` | `_plot_coupled_loosening(cl, "loosening")` |
| `plot_torque_balance()` | `_plot_torque_balance(cl)` |
| `plot_friction_wear_correlation()` | `_plot_friction_wear_correlation(cl)` |
| `plot_cumulative_angle()` | `_plot_cumulative_angle(cl)` |
| `plot_joint_forces()` | `_plot_joint_forces(cl)` |
| `plot_contact_forces()` | `_plot_contact_forces(cl)` |
| `plot_phase_diagram()` | `_plot_phase_diagram(cl)` |

### similitude_plots.py (ScaleCharts)

**Status: COUPLED within EnhancedSimilitudeTab only**

`similitude_plots.py` is used in `EnhancedSimilitudeTab.ComparisonPlotsPanel`. It correctly renders scale factor charts and Junker comparison plots. This coupling is intact.

---

## 8. CROSS-TAB INTEGRATION GAPS

```
Tab 1 (Project)         ─── (no signals) ──────────────────► Tab 2 (MSD Builder)
Tab 2 (MSD Builder)     ─── model_changed signal ──────────► Tab 3 (Solver)
Tab 3 (Solver)          ─── (no reverse signal) ────────────► Tab 2 (MSD Builder) ✗ HIGH-04
Tab 3 (Solver)          ─── finished(AnalysisResult) ───────► Tab 4 (Results)
Tab 4 (Results)         ─── (no signal) ────────────────────► Tab 5 (Similitude) ✗ MED-03
Tab 4 (Results)         ─── (no signal to overlay) ─────────► Tab 5 (Similitude) ✗ MED-03
Tab 5 (Similitude)      ─── (no AppState field) ────────────► Tab 6 (Reports) ✗ MED-03
Tab 6 (Reports)         ─── (no results restored) ──────────► reads AppState ✗ HIGH-03
```

**Missing cross-tab flows:**

| From | To | Missing | Priority |
|------|-----|---------|----------|
| Tab 4 Results | Tab 5 Similitude | Loosening curve overlay on scale plots | MED |
| Tab 5 Similitude | AppState | Store ScaledLooseningModel for Reports | MED |
| Tab 5 Similitude | Tab 3 Solver | "Send scaled model to solver" | MED |
| Tab 3 Solver | Tab 2 MSD Builder | Reverse param sync | HIGH |
| AppState | Project file | Results persistence | HIGH |

---

## 9. PRIORITY MATRIX

### P0 — Fix Immediately (CRITICAL)

| ID | Issue | File | Lines |
|----|-------|------|-------|
| CRITICAL-01 | Time integration bypasses contact tribology | `solver_worker.py` | 525–639 |
| CRITICAL-02 | LooseningPlotter never used — dual implementations | `main_window.py` | 2593–3040 |
| CRITICAL-03 | SimilitudeAnalysis engine never called | `main_window.py` + `similitude_tab.py` | — |

### P1 — Fix Soon (HIGH)

| ID | Issue | File | Lines |
|----|-------|------|-------|
| HIGH-01 | Contact friction params ignored in coupled loosening | `coupled_loosening_analyzer.py` | 2289+ |
| HIGH-02 | Assembled [K] not used for loosening stiffness | `coupled_loosening_analyzer.py` | ~2445 |
| HIGH-03 | Results not restored on project load | `app_state.py` | ~545 |
| HIGH-04 | No reverse signal Solver → MSD Builder | `main_window.py` | 1945–1948 |

### P2 — Fix When Possible (MEDIUM)

| ID | Issue | File | Lines |
|----|-------|------|-------|
| MED-01 | k_transverse hardcoded | `msd_builder.py` | 3238 |
| MED-02 | Preload not tracked during time integration | `solver_worker.py` + `model.py` | — |
| MED-03 | No AppState similitude field | `app_state.py` | — |
| MED-04 | Tab index bug (similitude) | `main_window.py` | 4336 |
| MED-05 | Nut inertia hardcoded | `contacts/thread_contact.py` | — |

### P3 — Fix Opportunistically (LOW)

| ID | Issue | File | Lines |
|----|-------|------|-------|
| LOW-01 | Contact dispatch map incomplete | `model.py` | 100–110 |
| LOW-02 | Coulomb stuck returns 0 (no static friction) | `contacts/base.py` | 183 |
| LOW-03 | Reports missing time integration data | `main_window.py` | report methods |
| LOW-04 | Matrix Viewer {F} not live | `matrix_viewer.py` | — |

---

## 10. RECOMMENDED IMPLEMENTATION ORDER

### Step 1: CRITICAL-02 (Lowest risk, highest ROI)

Replace inline plot methods with `LooseningPlotter` calls. This is a pure refactoring — no behavior change, but eliminates ~450 lines of duplicate code and activates all 16 plot types.

```python
# main_window.py replacement pattern:
from bolt_analysis_studio.visualization.loosening_plots import LooseningPlotter

def _plot_current(self, cl: CoupledLooseningResult, plot_type: str):
    canvas = self.results_tab.plot_widget.canvas
    plotter = LooseningPlotter(cl, canvas.figure)
    plotter.plot(plot_type)  # dispatches to correct method
    canvas.draw()
```

### Step 2: MED-04 (One-line fix)

```python
# main_window.py:4336
similitude_tab_index = 4  # was 5
```

### Step 3: HIGH-01 (Friction coupling to contacts)

Modify `create_analyzer_from_msd_model()` to scan contacts for friction parameters:

```python
mu_thread = None
mu_bearing = None
for c in model.contacts:
    if isinstance(c, ThreadContact) and mu_thread is None:
        mu_thread = c.friction.mu_static
    if isinstance(c, BearingContact) and mu_bearing is None:
        mu_bearing = c.friction.mu_static
```

### Step 4: HIGH-04 (Reverse signal Solver → Builder)

Add `_updating` guard and emit reverse signal when Solver Tab params change, or mark all Solver hidden spinboxes as truly read-only (no editing, no signal emission).

### Step 5: HIGH-03 (Results persistence)

Implement `AnalysisResult.to_dict()` and `from_dict()`. Store only scalars and cycle-level arrays (not full time integration displacement arrays, which can be MB-scale).

### Step 6: CRITICAL-01 (Contact time integration — highest complexity)

This requires restructuring `_run_time_integration()` to iterate through time steps explicitly rather than delegating to `integrator.integrate()`. Estimated effort: major refactoring.

### Step 7: CRITICAL-03 (Similitude engine coupling)

Wire `SimilitudeAnalysis` into `EnhancedSimilitudeTab` and add AppState field.

---

## 11. COUPLING INVENTORY TABLE

All coupling pathways in the software, verified against source code:

| Pathway | From | To | Mechanism | Status |
|---------|------|-----|-----------|--------|
| A | PropertyInspector loading | MSDModel.global_loading | pyqtSignal chain | ✓ WORKING |
| B | SchematicView elements | MSDModel.elements | export_to_msd_model() | ✓ WORKING |
| C | MSDModel.assemble_matrices() | [K][M][C] from contacts | get_stiffness/damping_contribution() | ✓ WORKING |
| D | MSDModel.assemble_force_vector() | {F} from contacts | get_force_contribution() | ✓ IMPLEMENTED, ✗ NOT CALLED |
| E | model.contacts update | Contact state evolution | contact.update_state() | ✓ IMPLEMENTED, ✗ NOT CALLED |
| F | create_analyzer_from_msd_model | CoupledLooseningAnalyzer | element scan + scalar fields | ✓ PARTIAL (friction ignored) |
| G | CoupledLooseningAnalyzer | FrictionEvolutionParams | internal call | ✓ WORKING |
| H | CoupledLooseningAnalyzer | WearModelParams | internal call | ✓ WORKING |
| I | SolverWorker.finished | AppState.results | pyqtSignal | ✓ WORKING |
| J | AppState.results_changed | ResultsTab plots | pyqtSignal + inline methods | ✓ WORKING |
| K | LooseningPlotter | ResultsTab canvas | — | ✗ NEVER CALLED |
| L | SimilitudeAnalysis | EnhancedSimilitudeTab | — | ✗ NEVER CALLED |
| M | AppState.results | Project .msd file | to_dict()/from_dict() | ✗ NOT IMPLEMENTED |
| N | Solver Tab params | MSD Builder inspector | reverse signal | ✗ MISSING |
| O | Similitude results | AppState | — | ✗ MISSING |
| P | Similitude results | Reports tab | — | ✗ MISSING |
| Q | Assembled [K] stiffness | k_transverse in inspector | — | ✗ MISSING |
| R | Assembled [K] stiffness | CoupledLooseningAnalyzer | — | ✗ MISSING |
| S | Preload decay | Contact normal forces | — | ✗ MISSING |
| T | TimeIntegration result | Reports tab | — | ✗ MISSING |

**Working:** 8 pathways
**Implemented but not called:** 2 pathways (D, E — CRITICAL-01)
**Partially working:** 1 pathway (F — HIGH-01)
**Missing:** 9 pathways (K, L, M, N, O, P, Q, R, S, T)

---

## 12. CONCLUSION

The Bolt Analysis Studio v4.0 has a **solid architectural foundation** with well-designed contact classes, a rich numerical solver, and a clean signal-based GUI. The primary analysis path (MSD Builder → Coupled Loosening → Results) works correctly.

The three critical gaps all share a common root cause: **the time integration solver and the contact physics engine were developed somewhat in parallel and not fully connected at the seams**. The `CoupledLooseningAnalyzer` correctly models friction-wear coupling internally, but the time integration solver (`_run_time_integration`) treats the system as a linear MSD without contact physics. Meanwhile, the `LooseningPlotter` visualization module was developed but wired to nothing in the GUI.

The highest-priority fixes are:
1. **Activate LooseningPlotter** (pure refactoring, immediate gain)
2. **Connect contact friction** to the coupled loosening analyzer (data already available)
3. **Fix results persistence** (model loads but analysis is gone — poor UX)
4. **Build per-step contact evolution** into time integration (the correct physics path)

---

*Prepared by Claude Code (Sonnet 4.6) — internal reference Petrobras R&D Analysis*
*Files analyzed: app_state.py, solver_worker.py, model.py, element.py,*
*contacts/base.py, contacts/thread_contact.py, contacts/bearing_contact.py,*
*coupled_loosening_analyzer.py, preload_loss_models.py, friction_models.py,*
*msd_builder.py, main_window.py, similitude_tab.py, similitude.py,*
*visualization/loosening_plots.py, visualization/plot_manager.py*
