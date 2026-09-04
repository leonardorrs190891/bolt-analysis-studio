# Bolt Analysis Studio v4.0 — Software Architecture

**Institution:** internal reference — Tribology and Wear Technology Laboratory, Federal University of Uberlândia
**Project:** Petrobras R&D — Bolted Flange Joint Integrity
**Authors:** L. Ribeiro, D. Carvalho, S.C. Naves, T. Santos, V. Marques, G. Arruda

---

## 1. Overview

Bolt Analysis Studio (BAS) v4.0 is a 4-layer scientific engineering application for bolted flange joint self-loosening analysis. It provides a unified time-stepping framework coupling:

- **Preload evolution** (embedding, creep, relaxation, wear, rotational loosening)
- **Friction dynamics** (Coulomb, LuGre, Dahl, Iwan, three-phase evolution)
- **Structural dynamics** (14-DOF MSD system with Newmark-β, HHT-α, and other integrators)
- **Similitude analysis** (Buckingham Π groups for multi-bolt reduction and geometric scaling)

Target applications: API 6A wellhead connections, ASME B16.5 flanges, subsea equipment under 0–100 Hz cyclic loading.

Applicable standards: VDI 2230 Part 1 (2015), EN 1591-1, ISO 16130, DIN 65151, API 6A, ASME PCC-1.

---

## 2. Four-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: GUI (PyQt6)                                                       │
│                                                                             │
│  gui/main_window.py        — 6-tab application shell (Project, Model,      │
│                              Solver, Results, Similitude, Reports)          │
│  gui/msd_builder.py        — Visual drag-drop schematic editor              │
│  gui/matrix_viewer.py      — [M][K][C]{F} matrix visualization             │
│  gui/similitude_tab.py     — Enhanced similitude analysis interface         │
│  gui/contact_builder_dialog.py — Contact property editor                   │
│  gui/fbd_viewer.py         — Free body diagram (experimental, unused)      │
│  gui/theme.py              — Catppuccin Mocha dark theme (Theme class)     │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ Qt signals (PyQt6)
┌────────────────────────────────▼────────────────────────────────────────────┐
│  LAYER 2: VISUALIZATION                                                     │
│                                                                             │
│  visualization/loosening_plots.py — 6 plotter classes, 16+ plot methods   │
│  visualization/contact_plots.py   — Contact force and state plots          │
│  visualization/plot_manager.py    — Plot lifecycle and export management   │
│  core/similitude/similitude_plots.py — Π-group and scaling charts         │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│  LAYER 3: NUMERICAL                                                         │
│                                                                             │
│  numerical/preload_loss_models.py  — 8 phenomenological decay models       │
│  numerical/friction_models.py      — 6 friction models (Coulomb→LuGre)    │
│  numerical/time_integration.py     — 6 integrators with contact evolution  │
│  numerical/coupled_loosening_analyzer.py — Coupled friction-wear-loosening │
│  core/solver_worker.py             — QThread worker for analysis runs      │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│  LAYER 4: DATA / CORE                                                       │
│                                                                             │
│  core/models/element.py     — MSDElementData dataclasses (16 types)       │
│  core/models/model.py       — MSDModel with [M][K][C] assembly             │
│  core/contacts/             — Contact class hierarchy + tribology          │
│  core/similitude/           — Buckingham Π + geometric scaling             │
│  core/app_state.py          — AppState, ProjectInfo, result dataclasses    │
│  core/databases/            — ASTM/ISO materials + thread geometry JSON    │
│  core/assembly/             — CompleteMSDMatrixAssembler                   │
│  core/state/                — PreloadTracker, StateManager                 │
│  core/loosening/            — JunkerModel analytical loosening             │
│  core/load_distribution.py  — Thread load distribution laws               │
│  core/load_propagation.py   — Load propagation through joint              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. MSD Hierarchical Model — Three Layers

### Layer 1: Component Elements

Physical parts with **bulk material properties only** — no tribology.

| Element Type | Key Properties | Stiffness Formula |
|---|---|---|
| `HEAD` | m, J (rotational inertia), E, ν, ρ | k_head = E·A/L_head |
| `SHANK` | m, k_axial, k_torsional | k_shank = E·A/L_shank |
| `THREAD` | m, k_axial, k_torsional, n_threads | k_thread = E·A_t/L_thread |
| `NUT` | m, J, E, ν | k_nut = E·A/L_nut |
| `WASHER` | m, k_axial | k_washer = E·A/t_washer |
| `FLANGE` | m, k_axial, k_transverse | Rötscher cone model |
| `GASKET` | m, k_axial(δ) **nonlinear** | k_g(δ) = dk/dδ tangent |
| `GROUND` | Fixed reference, zero mass | — |

**CRITICAL RULE:** Component elements have NO friction, NO wear, NO surface roughness. These belong exclusively to contact elements (Layer 2/3).

### Layer 2: Contact Elements

Mechanical interfaces between components:

| Contact Type | Nodes Connected | Phenomenology |
|---|---|---|
| `THREAD_CONTACT` | Stud ↔ Nut (n parallel) | Helix coupling, parallel thread array, per-thread stiffness/friction |
| `BEARING_HEAD` | Head/Stud ↔ Washer/Flange | Rotational friction torque (resists loosening) |
| `BEARING_NUT` | Nut ↔ Washer/Flange | Rotational friction torque (resists loosening) |
| `WASHER_FLANGE` | Washer ↔ Flange | Load spreading, embedding, fretting |
| `FLANGE_FLANGE` | Flange 1 ↔ Flange 2 | Metal-to-metal, high stiffness, fretting |
| `FLANGE_GASKET` | Flange ↔ Gasket | Nonlinear k(δ), viscoelastic, creep/relaxation |
| `HEAD_FLANGE` | Head direct ↔ Flange | No-washer configuration |
| `NUT_FLANGE` | Nut direct ↔ Flange | No-washer configuration |

### Layer 3: Tribological Layer

Surface physics **attached to contact elements**:

- **Friction Models:** Coulomb, Stribeck, LuGre, Dahl, Iwan, CoulombViscous
- **Wear Models:** Archard, Energy-Based, Fretting, Oxidative
- **Lubrication:** Dry, Boundary, Mixed (Stribeck λ-ratio), Hydrodynamic
- **Coatings:** Zinc, Phosphate, PTFE, MoS₂, DLC (with degradation)

---

## 4. Governing Equation of Motion

```
[M]{ü} + [C]{u̇} + [K]{u} = {F_ext(t)} + {F_tribo(u, u̇, state)}
```

**[M]** — Global mass matrix (diagonal, lumped masses + rotational inertia)
**[C]** — Global damping matrix (Rayleigh: α[M] + β[K] + contact damping)
**[K]** — Global stiffness matrix (component + contact contributions; helix off-diagonals for threads)
**{F_ext(t)}** — External force vector (preload, axial, transverse, thermal)
**{F_tribo}** — Tribological force vector from contacts (friction torques, wear-induced preload loss)

### DOF System

The full analysis uses a **14-DOF configuration**:

| Index | Symbol | Type | Phenomenon |
|---|---|---|---|
| 1 | x_bh | Axial | Bolt head |
| 2 | x_ws1 | Axial | Washer 1 embedding |
| 3 | x_fl1 | Axial | Flange 1 Rötscher cone |
| 4 | x_g | Axial | Gasket creep/nonlinear |
| 5 | x_fl2 | Axial | Flange 2 |
| 6 | x_ws2 | Axial | Washer 2 |
| 7 | x_nut | Axial | Nut thread engagement |
| 8 | x_stud | Axial | **Preload storage** |
| 9 | θ_stud | Torsional | Stud rotation |
| 10 | θ_nut | Torsional | **Self-loosening DOF** |
| 11 | y_fl1 | Transverse Y | **Junker mechanism driver** |
| 12 | z_fl1 | Transverse Z | Junker mechanism driver |
| 13 | y_fl2 | Transverse Y | Junker mechanism driver |
| 14 | z_fl2 | Transverse Z | Junker mechanism driver |

**Reduced configurations:**
- 6-DOF: Axial only (preload/embedding analysis)
- 8-DOF: Axial + torsional (rotational loosening without transverse)
- 10-DOF: Standard Junker test simulation
- 14-DOF: Full analysis (all phenomena)

---

## 5. Thread Contact — The Key to Self-Loosening

### Thread Array

For n engaged threads, each thread element i has:
- **Stiffness:** k_i = φ_i × k_base  (from load distribution law)
- **Individual friction:** μ_i(N, p, wear)
- **Wear state:** w_i accumulated
- **Slip state:** stick / partial slip / gross slip

### Helix Coupling — Axial-Torsional Coupling in [K]

```
Δx_axial = (p/2π) × Δθ_rotation

[K_thread] = k_th × | 1     -λ      λ  |   where λ = p/(2π)
                     | -λ    λ²    -λ²  |
                     |  λ   -λ²     λ²  |

DOFs: x_nut ↔ θ_stud ↔ θ_nut
```

This kinematic constraint creates **off-diagonal terms in [K]** that convert axial preload into a loosening torque — the fundamental mechanism of self-loosening.

### Load Distribution Laws (5 models)

| Model | Formula | φ_i Characteristics |
|---|---|---|
| Equal | φ_i = 1/n | Idealized uniform |
| Linear | φ_i = 2(n-i+1)/(n(n+1)) | First thread carries most |
| Power Law | φ_i = (n-i+1)^β / Σ | β=1.5–2.0 typical |
| Exponential | φ_i = e^(-λ(i-1)) / Σ | λ=0.3–0.5 typical |
| Yamamoto | φ_i = sinh(γ(n-i+0.5)) / Σ | Most physically accurate |

For n=8 threads with Power Law (β=2): Thread 1 carries 19.0%, Thread 8 carries 5.7%.

---

## 6. Matrix Contribution Rules

### [K] Stiffness Contributions

| Contact | DOFs | Contribution |
|---|---|---|
| Thread (axial) | x_nut, x_stud | k_thread diagonal terms |
| Thread (helix) | θ_stud, θ_nut, x_nut | Off-diagonal k×(p/2π) terms |
| Bearing | x_i, x_j | Contact stiffness k_c |
| Washer | x_washer, x_flange | k_contact |
| Flange-Flange | x_fl, y_fl, z_fl | k_axial + k_transverse |
| Gasket | x_fl, x_g | k_tangent(δ) **nonlinear**, updated each step |

### [C] Damping Contributions

- Material damping: c = 2ζ√(km) at all contact DOFs
- Viscous friction: c_visc at thread/bearing torsional DOFs
- Gasket viscoelastic: c_visco (high, captures energy dissipation)
- Rayleigh: α[M] + β[K] (optional global)

### {F} Force Vector — WHERE FRICTION AND WEAR ENTER

**CRITICAL DESIGN PRINCIPLE:** Friction and wear do NOT modify [K] or [C]. They contribute ONLY through {F}.

**Thread friction torque (resists loosening):**
```
T_thread = μ_t × F_p × d₂ / (2·cos α)    applied at θ_nut DOF
```

**Thread helix torque (CAUSES loosening when slip occurs):**
```
T_helix = F_p × (p/2π)    applied at θ_nut DOF, loosening direction
```

**Bearing friction torque (resists loosening):**
```
T_bearing = μ_b × F_p × r_eff    applied at θ_nut DOF (from head bearing)
                                   and θ_stud DOF (from nut bearing)
```

**Transverse interface friction:**
```
F_trans_friction = μ × F_p    at y_fl, z_fl DOFs
```

**Wear-induced preload loss (indirect):**
```
h_wear = K_archard × F_n × s / (H × A)
ΔF_wear = k_sys × h_wear
```

---

## 7. Time-Stepping Solution Algorithm

For each time step n (9-step process from Part I):

```
Step 1: Compute {F_ext}(t_n) = {F_preload} + {F_axial} + {F_trans} + {F_thermal}
Step 2: Compute {F_tribo} from all contacts (friction torques, wear forces)
Step 3: Check matrix updates (gasket k_g, contact separation, if nonlinear)
Step 4: Solve [M]{ü} + [C]{u̇} + [K]{u} = {F_ext} + {F_tribo}  (Newmark-β)
Step 5: Update contact states (slip state, friction evolution, wear accumulation)
Step 6: Compute self-loosening (Junker check: T_pitch > T_thread + T_bearing?)
Step 7: Update preload F_p = F_p0 - ΔF_rotation - ΔF_embedding - ΔF_relaxation
                             - ΔF_creep - ΔF_wear - ΔF_thermal
Step 8: Cycle counting (detect zero-crossings, update N-dependent quantities)
Step 9: Convergence check (if nonlinear: Newton-Raphson within step)
```

---

## 8. Data Flow — GUI to Solver

```
PropertyInspector (MSD Builder)
       │
       │ loading_changed signal
       ▼
MSDBuilderWindow.export_to_msd_model()
       │
       │ Creates MSDModel with global_loading + friction fields
       ▼
BoltAnalysisStudio._on_msd_builder_model_changed()
       │
       ├─► solver_tab.update_loading_summary()   (read-only display)
       ├─► app_state.model = msd_model           (stores model)
       └─► matrix_viewer refresh (if open)
       │
       │ User clicks "Run Analysis"
       ▼
SolverWorker (QThread)
       │
       ├─► _run_preload_analysis()
       ├─► _run_time_integration()
       ├─► _run_coupled_loosening_analysis()
       └─► Emits results_ready signal
       │
       ▼
ResultsTab._on_results_changed()
       │
       └─► Plots via CoupledLooseningResultsPlotter / inline methods
```

### Signal Architecture (PyQt6)

| Signal | From | To | Payload |
|---|---|---|---|
| `loading_changed` | PropertyInspector | MSDBuilderWindow | dict |
| `model_changed` | MSDBuilderWindow | MainWindow | dict |
| `element_selected` | SchematicView | PropertyInspector | element_id |
| `results_ready` | SolverWorker | ResultsTab | AnalysisResult |
| `similitude_changed` | AppState | ReportsTab | similitude_result |
| `scaling_computed` | ScalingPanel | MainWindow | ScalingResult |
| `progress_update` | SolverWorker | SolverTab | (int, str) |

---

## 9. Serialization Format (.msd files)

Models serialize to JSON via `MSDModel.to_dict()` / `from_dict()`:

```json
{
  "elements": [...],
  "contacts": [...],
  "global_loading": {
    "type": "TRANSVERSE",
    "F_preload": 50000,
    "F_transverse": 10000,
    "delta_amplitude": 0.65,
    "frequency": 12.5,
    "n_cycles": 2000
  },
  "friction_bolt": {
    "mu_initial": 0.12,
    "lubricated": true,
    "bolt_diameter": 16.0,
    "pitch": 2.0
  }
}
```

**Backward compatibility:** All `from_dict()` methods handle missing fields gracefully with defaults.

---

## 10. File Inventory

### Source (50 Python files)

```
src/bolt_analysis_studio/
├── __init__.py
├── core/
│   ├── app_state.py              — AppState, ProjectInfo, AnalysisResult dataclasses
│   ├── project_io.py             — Save/load .msd project files
│   ├── solver_worker.py          — QThread for async analysis runs
│   ├── load_distribution.py      — Thread load distribution computations
│   ├── load_propagation.py       — Load path through joint elements
│   ├── validation_cases.py       — Built-in validation case loader
│   ├── models/
│   │   ├── element.py            — MSDElementData (16 ElementType, 14 dataclasses)
│   │   └── model.py              — MSDModel + matrix assembly
│   ├── contacts/
│   │   ├── base.py               — Abstract Contact class + property dataclasses
│   │   ├── thread_contact.py     — ThreadContact (parallel array, helix coupling)
│   │   ├── bearing_contact.py    — BearingContact (head/nut friction torque)
│   │   ├── gasket_contact.py     — FlangeGasketContact (nonlinear, creep)
│   │   ├── flange_contact.py     — FlangeFlangeContact (fretting)
│   │   ├── washer_contact.py     — WasherFlangeContact (embedding)
│   │   └── factory.py            — ContactFactory (type dispatch)
│   ├── similitude/
│   │   ├── similitude.py         — Buckingham Π analysis
│   │   ├── loosening_similitude.py — Loosening-specific Π groups
│   │   └── similitude_plots.py   — Scaling charts
│   ├── assembly/
│   │   └── matrix_assembler.py   — CompleteMSDMatrixAssembler
│   ├── state/
│   │   └── preload_tracker.py    — PreloadTracker (cycle-by-cycle preload)
│   ├── loosening/
│   │   └── junker_model.py       — Analytical Junker model
│   └── databases/
│       └── materials_database.py — ASTM/ISO material properties
│
├── numerical/
│   ├── preload_loss_models.py    — 8 decay models (Exponential→Combined)
│   ├── friction_models.py        — 6 friction models (Coulomb→Iwan)
│   ├── time_integration.py       — 6 integrators (Newmark, HHT, RK4...)
│   └── coupled_loosening_analyzer.py — Coupled friction-wear-loosening
│
├── visualization/
│   ├── loosening_plots.py        — PreloadLossPlotter, CoupledLooseningResultsPlotter...
│   ├── contact_plots.py          — Contact force/state plots
│   └── plot_manager.py           — Plot lifecycle management
│
└── gui/
    ├── main_window.py            — BoltAnalysisStudio (6-tab main window)
    ├── msd_builder.py            — MSDBuilderWindow + SchematicView + PropertyInspector
    ├── matrix_viewer.py          — MatrixViewerDialog
    ├── similitude_tab.py         — EnhancedSimilitudeTab
    ├── contact_builder_dialog.py — ContactBuilderDialog
    ├── fbd_viewer.py             — FBDViewer (EXPERIMENTAL — not wired to UI)
    ├── load_bc_elements.py       — Load/BC visual elements
    ├── documentation_tab.py      — In-app documentation viewer
    └── theme.py                  — Theme (Catppuccin Mocha)
```

---

## 11. Theming

All UI uses **Catppuccin Mocha** dark theme via `gui/theme.py`:

```python
class Theme:
    BLUE       = "#89b4fa"   # Primary accent, selected elements
    GREEN      = "#a6e3a1"   # Valid state, success
    RED        = "#f38ba8"   # Error state, loosening warning
    YELLOW     = "#f9e2af"   # Selection highlight
    SURFACE0   = "#313244"   # Minor grid, subtle backgrounds
    SURFACE1   = "#45475a"   # Major grid, card borders
    OVERLAY    = "#6c7086"   # Muted text, status bar
    BASE       = "#1e1e2e"   # Main background
    TEXT       = "#cdd6f4"   # Primary text
```

Matplotlib uses `dark_background` style with theme colors injected via `setup_plot_style()`.

---

## 12. Key Design Patterns

1. **Single Source of Truth:** All loading/friction parameters live ONLY in the MSD Builder `PropertyInspector`. The Solver Tab is read-only display.

2. **Lazy Matrix Caching:** `MSDModel._mark_dirty()` invalidates the matrix cache. Matrices are recalculated only when elements change, cached between solver runs.

3. **Solver Factory:** `create_integrator(method_name)` dispatches to appropriate integrator class.

4. **Dataclass Fields:** New parameters are added as proper `@dataclass` fields with type hints, never as runtime attributes. All fields have defaults for backward compatibility.

5. **Signal-Based Updates:** Cross-component communication uses Qt signals. No direct coupling between GUI components.

6. **Contact-to-Matrix Mapping:** Each contact implements `get_stiffness_contribution()`, `get_damping_contribution()`, `get_force_contribution()`. The assembler calls these uniformly.

---

*See also: NUMERICAL_MODELS.md, CONTACTS.md, CALIBRATION_AND_VALIDATION.md, API_REFERENCE.md, COUPLING_AUDIT.md*
