# Bolt Analysis Studio v4.0 — Coupling Audit

**Date:** 2026-02-19
**Scope:** Complete audit of all layer-to-layer coupling across GUI↔Core↔Numerical↔Visualization.
**Source:** MODEL_COUPLING_STUDY.md (previous sessions), IMPROVEMENT_ANALYSIS_Code_vs_Reference.md

---

## 1. Coupling Status Summary

### Verified Working ✅

| Coupling | Location | Status |
|---|---|---|
| MSD Builder → MSDModel | `msd_builder.py:export_to_msd_model()` | ✅ Exports elements + loading + friction |
| MSDModel → [M][K][C] assembly | `model.py:assemble_matrices()` | ✅ Includes all contact stiffness |
| Contacts → [K] matrix | All contact classes `get_stiffness_contribution()` | ✅ All 8 contact types implemented |
| Contacts → [C] matrix | All contact classes `get_damping_contribution()` | ✅ All 8 contact types implemented |
| Contacts → {F} vector | All contact classes `get_force_contribution()` | ✅ All 8 contact types implemented |
| 9 preload loss models | `preload_loss_models.py` | ✅ All 9 verified (incl. LogarithmicModel) |
| 6 integrators solve_with_contacts() | `time_integration.py` | ✅ All 6 have method (incl. AdaptiveRK45) |
| Helix coupling off-diagonals | `thread_contact.py:get_stiffness_contribution()` | ✅ Lines 268-305, includes (axial,torsional) DOFs |
| assemble_force_vector() tribological | `model.py:assemble_force_vector()` | ✅ Lines 595-655, handles tuple returns from ThreadContact |
| update_contact_states() per timestep | `model.py:update_contact_states()` | ✅ Lines 657-683, called by solver |
| compute_tribological_forces() | `model.py:compute_tribological_forces()` | ✅ Lines 685-716, convenience for solver |
| FrictionEvolutionParams M9 fields | `coupled_loosening_analyzer.py:91-92` | ✅ mu_thread_initial + mu_bearing_initial defined |
| LoadingData all fields | `element.py:1003-1079` | ✅ 15 fields incl. integration_time, phase_axial/transverse |
| ContactInterface serialization | `element.py:416-451` | ✅ to_dict/from_dict with type conversions |
| ThreadFilletModel (5 distributions) | `element.py:458-572` | ✅ Equal/Linear/Power/Exponential/Yamamoto |
| CoupledLooseningResultsPlotter (8 methods) | `visualization/loosening_plots.py` | ✅ All 8 plot methods verified |
| CoupledLooseningResultsPlotter export | `visualization/__init__.py` | ✅ Exported in __all__ |
| Contact type dispatch map | `model.py:_init_contact_type_map()` | ✅ All washer variants added |
| Matrix Viewer live update | `msd_builder.py` + `matrix_viewer.py` | ✅ Connected via model_changed signal |
| Similitude result storage | `app_state.py:similitude_result` | ✅ Property + signal added |
| k_transverse auto-extraction | `main_window.py:_on_msd_builder_model_changed()` | ✅ From assembled [K] |
| Results persistence (from_dict) | `app_state.py` | ✅ All 4 result classes have from_dict() |
| Stiffness from assembled [K] | `coupled_loosening_analyzer.py` | ✅ Series combination method |
| Rich plotter for results | `main_window.py:_get_rich_plotter_and_raw()` | ✅ Falls back to inline |
| Similitude import from model | `similitude_tab.py` + `main_window.py` | ✅ populate_from_model() |
| Hidden spinbox signals blocked | `main_window.py:update_loading_summary()` | ✅ blockSignals + single recalc |
| 5-level friction hierarchy | `coupled_loosening_analyzer.py:create_analyzer_from_msd_model()` | ✅ |

---

## 2. Known Gaps / Outstanding Issues

### CRITICAL Issues

| ID | Description | Impact | Status |
|---|---|---|---|
| **CRITICAL-01** | `solve_with_contacts()` not called in `_run_time_integration()` | Contact states DO NOT EVOLVE during time integration | ⚠️ SKIPPED — requires CompleteMSDMatrixAssembler infrastructure not yet constructed in worker |
| **C1** | Thread stiffness formula wrong in `ThreadContact` | k_total incorrect for parallel array | ❌ Open |
| **C2** | Head stiffness factor 0.4 vs 0.5 inconsistency | 20% bolt stiffness error | ❌ Open |
| **C3** | Stress area uses d₃ instead of d₁ (ISO 262) | ~3% A_t error | ✅ Fixed in BUG-07 (msd_builder.py) |
| **C5** | Contact system not fully wired into solver | Calibration of contact-based models blocked | ⚠️ Partial |

### HIGH Priority

| ID | Description | Impact | Status |
|---|---|---|---|
| **H2** | System stiffness uses `trace(K)` (old path) | 5–10× k_sys overestimate | ✅ Fixed (series method) |
| **H3** | CoupledLooseningAnalyzer uses independent friction | Ignores per-contact friction evolution | ⚠️ Partially addressed via hierarchy |
| **M1** | K-factor oversimplified | 22% torque-preload error | ❌ Open |
| **M8** | C_loosening hardcoded at 0.3 | Cannot tune to experimental data | ❌ Open (needs calibration plan) |
| **M9** | Thread ≠ bearing friction (M9 feature) | Partially addressed via `mu_thread_initial`/`mu_bearing_initial` | ✅ Params added |

### MEDIUM Priority

| ID | Description | Impact | Status |
|---|---|---|---|
| Force vector shape validation | No check that {F} shape matches DOF count | Silent shape mismatch bugs possible | ❌ Open |
| Contact export verification | Contacts exported from msd_builder but rarely populated by wizard | Wizard models have no contacts | ✅ Fixed (BUG-01, BUG-04, BUG-05, BUG-06) |
| **NEW-01** | `create_analyzer_from_msd_model()` not verified to extract mu_thread_initial/mu_bearing_initial separately (M9 feature) | Thread and bearing friction always equal despite separate params existing | ❌ Open — verify M9 extraction |
| **NEW-02** | `SchematicView.export_to_model()` exports `ContactInterface` dataclasses, not `Contact` objects | Contact states (slip, wear depth) not preserved across save/load | ❌ Needs audit |
| **NEW-03** | `BEARING_NUT` and `BEARING_HEAD` both map to `BearingContact` — no internal differentiation | May not correctly assign head vs nut DOF indices | ❌ Verify BearingContact uses correct dof_axial |
| **NEW-04** | Friction model dispatch (Coulomb vs LuGre vs Stribeck) in solver not verified | Friction model selection may be ignored; Coulomb always used | ❌ Open — verify `friction_models.py` dispatch |
| **NEW-05** | Wear model integration in `time_integration.py` not verified | `WearModelParams` defined but wear may not accumulate during dynamic analysis | ❌ Open — verify contact.get_wear_contribution() call |
| **CB3** | `applied_loads` and `constraints` per-element not serialized/deserialized | `AppliedLoad` and `Constraint` dataclasses exist in element.py but `to_dict()`/`from_dict()` stub at lines 1422–1425 | ❌ Open — affects validation case round-trips |

---

## 3. Detailed Coupling Analysis by Layer

### 3.1 GUI → Core Coupling

```
✅ MSD Builder PropertyInspector
       ├── loading_changed → model.global_loading ✅
       ├── element changed → SchematicView.get_model_data() → export_to_msd_model() ✅
       └── contact changed → contact objects added to model ✅

✅ Solver Tab
       ├── update_loading_summary() reads model.global_loading ✅
       ├── blockSignals() prevents spurious dt recalculation ✅
       └── _run_analysis() reads hidden spinboxes ✅

✅ Matrix Viewer
       ├── Shows [M], [K], [C] from model.assemble_matrices() ✅
       ├── Shows {F} force vector from model ✅
       └── Refreshes on model_changed signal ✅

✅ Similitude Tab
       ├── import_from_model_requested → populate_from_model() ✅
       ├── scaling_computed → app_state.similitude_result ✅
       └── send_to_solver → _on_similitude_send_to_solver() ✅
```

### 3.2 Core → Numerical Coupling

```
✅ MSDModel
       ├── assemble_matrices() → (M, K, C) numpy arrays ✅
       │       includes all contact stiffness contributions ✅
       │       includes helix coupling off-diagonals ✅
       ├── assemble_force_vector() → {F} numpy array ✅
       │       includes external loads ✅
       │       includes tribological forces from contacts ✅
       └── update_contact_states() called per time step ✅

❌ SolverWorker._run_time_integration()
       └── Calls integrator.integrate() not solve_with_contacts()
           → contacts DO NOT update during time integration
           → friction evolution, wear accumulation do not occur
```

**Fix needed for CRITICAL-01:**
```python
# In solver_worker.py _run_time_integration():
if model and model.contacts and hasattr(integrator, 'solve_with_contacts'):
    result = integrator.solve_with_contacts(
        time_params, F_func, model.contacts, preload, u0, v0
    )
else:
    result = integrator.integrate(time_params, F_func, u0, v0)
```

### 3.3 Numerical → Visualization Coupling

```
✅ CoupledLooseningResult._raw_loosening_results
       └── Stores raw LooseningResults from solver
           Used by CoupledLooseningResultsPlotter ✅

✅ CoupledLooseningResultsPlotter
       └── Exported from visualization/__init__.py ✅

✅ main_window._get_rich_plotter_and_raw()
       ├── Returns (plotter, raw_results) if available ✅
       └── Falls back to inline methods if not ✅

⚠️ Plot method dispatch
       └── ResultsTab._plot_with_settings() has all 12 branches ✅
           but some delegate to inline methods (not rich plotter) ⚠️
```

### 3.4 Contact Factory Dispatch

All washer contact types now have explicit entries (BATCH 1 fix):

```python
_CONTACT_TYPE_MAP = {
    "THREAD_CONTACT":    ThreadContact,
    "BEARING_HEAD":      BearingContact,
    "BEARING_NUT":       BearingContact,
    "WASHER_FLANGE":     WasherFlangeContact,   ✅ ADDED
    "WASHER_PLAIN":      WasherFlangeContact,   ✅ ADDED
    "WASHER_BELLEVILLE": WasherFlangeContact,   ✅ ADDED
    "WASHER_SPRING":     WasherFlangeContact,   ✅ ADDED
    "WASHER_NORDLOCK":   WasherFlangeContact,   ✅ ADDED
    "FLANGE_FLANGE":     FlangeFlangeContact,
    "FLANGE_GASKET":     FlangeGasketContact,
    "HEAD_FLANGE":       BearingContact,
    "NUT_FLANGE":        BearingContact,
}
```

---

## 4. All Implemented Fixes (Sessions 1–7)

### BATCH 1 — Instant Wins ✅
- **MED-04**: `_go_to_similitude_tab()` tab index fixed: 5→4
- **LOW-01**: Contact dispatch map — added explicit WASHER_FLANGE variants

### BATCH 2 — Small Fixes ✅
- **LOW-02**: Coulomb stuck returns static friction (uses `accumulated_slip` sign)
- **LOW-03**: Reports HTML includes method, dt, t_end for time integration results
- **LOW-04**: Matrix Viewer live update — `model_changed` signal connected

### BATCH 3 — Medium Fixes ✅
- **HIGH-04**: Hidden spinboxes `blockSignals()` during `update_loading_summary()`
- **HIGH-01**: 5-level friction hierarchy in `create_analyzer_from_msd_model()`
- **HIGH-03**: `from_dict()` added to all 4 result classes; `AppState.from_dict()` restores results
- **MED-01**: k_transverse auto-extracted from assembled [K] → PropertyInspector
- **MED-03**: `AppState.similitude_result` property + `similitude_changed` signal

### BATCH 4 — Larger Refactoring ✅/⚠️
- **CRITICAL-02**: `CoupledLooseningResult._raw_loosening_results` field; helper `_get_rich_plotter_and_raw()`
- **CRITICAL-01** ⚠️ SKIPPED: Full implementation requires CompleteMSDMatrixAssembler, StateManager, PreloadTracker infrastructure

### BATCH 5 — Complex ✅
- **CRITICAL-03**: `_on_similitude_scaling_computed()` stores result in `app_state.similitude_result`
- **HIGH-02**: Stiffness from assembled [K] uses series combination (1/k_sys = Σ1/k_i)

### Study File 6 — Similitude Tab ✅
- **BUG-01** to **BUG-07**: All similitude tab connectivity issues resolved
- **U2**: "Import from MSD Builder" bar added to EnhancedSimilitudeTab
- **U4**: Export/Transfer buttons enabled only after successful compute
- **U6**: "Send to Solver" button wired to solver

### Study File 3 — MSD Builder UX Phase 1 ✅
- `_fmt_eng()` helper for engineering notation display
- Rounded corners, softer grid
- Enhanced context menu (element and canvas)
- Status bar with preload + validation indicators
- `keyPressEvent()` (Escape, Ctrl+A, Ctrl+R, Ctrl+D)
- Inspector tabs (Element/Loading/Contact) via QTabWidget

### Study File 2 — Project Tab ✅
- `ProjectInfo` extended with institution, project_number, revision, notes
- `RecentProjectsManager` backed by QSettings
- `PROJECT_TEMPLATES` (4 presets)
- `ProjectTab` rewritten with hero bar + splitter

### Study File 5 — Solver Tab ✅
- `SolverTab.refresh_theme()` guarded with `hasattr()` (crash fix)
- `summary_cycles_spin` set to `setReadOnly(True)`
- `method_map` off-by-one fixed

### Study File 4 — MSD Builder Contacts ✅
- `export_to_msd_model()` contact export loop added
- `get_thread_contacts()`, `get_bearing_contacts()` accept `ContactInterface`
- Presets (flanged_joint, single_bolt, junker_test) fixed with correct contact types
- Wizard `_build_from_wizard()` fixed for proper contact chain
- Stress area formula: d₃→d₁ (ISO 262)

### Study File 7 — Results Tab ✅
- Stats reset to "—" before populate
- Canvas axes reset after multi-axes dashboard
- Frequency reads from `model.global_loading.frequency` (not hardcoded 25 Hz)
- Contact Forces shows thread/bearing friction separately
- All 12 missing `_plot_with_settings` dispatch branches added

---

## 5. Open Issues Requiring Future Work

### Priority 1 — Critical (Calibration Blocked)

1. **CRITICAL-01 (Full implementation):** `solve_with_contacts()` needs to be wired in `_run_time_integration()`. Requires proper construction of CompleteMSDMatrixAssembler, StateManager, and PreloadTracker objects within the solver worker. These are in `core/assembly/`, `core/state/` but not yet integrated into SolverWorker.

2. **C1 Thread stiffness formula:** The parallel thread array stiffness formula in `thread_contact.py` needs verification against ISO 68 / VDI 2230 formulas.

3. **C2 Head stiffness factor:** Inconsistency between 0.4 and 0.5 in `element.py` head stiffness calculation. Should be 0.5 per Bickford (2008).

4. **M8 C_loosening:** Must be made configurable (not hardcoded 0.3) to enable calibration.

### Priority 2 — High (Accuracy Concerns)

5. **M1 K-factor:** Current formula `K = 0.16 + 0.5×μ` should use full VDI 2230 formula:
   ```
   K = (d₂/(2d))·tan(λ + ρ') + μ_b·r_eff/d
   where ρ' = arctan(μ_t/cosα)    (effective thread friction angle)
   ```

6. **H3 Contact friction in CoupledLooseningAnalyzer:** The analyzer creates its own friction model from global parameters rather than using per-contact friction/wear states from the MSD model's contact objects.

### Priority 3 — Medium (Usability)

7. **Force vector shape validation:** Add assertion `len(F) == model.n_dof` at assembly time.

8. **Thread count validation:** The contact builder dialog should enforce `n_ThreadContacts >= n_Nuts` with a clear error message.

9. **Matrix viewer force vector completeness:** The {F} tab should compute tribological forces (not just external forces) by calling `model.assemble_force_vector()`.

### Priority 3b — New Findings (Deep Audit — 2026-02-20)

10. **NEW-01 M9 friction extraction in `create_analyzer_from_msd_model()`:** `FrictionEvolutionParams` has `mu_thread_initial` and `mu_bearing_initial` fields (lines 91-92) but it is not verified that `create_analyzer_from_msd_model()` populates these separately from model contacts (ThreadContact vs BearingContact). Should extract: `mu_thread_initial` from ThreadContact friction properties, `mu_bearing_initial` from BearingContact friction properties.

11. **NEW-02 Contact export type:** `SchematicView.export_to_model()` needs verification that it exports `Contact` subclass objects (ThreadContact, BearingContact, etc.) rather than the `ContactInterface` dataclasses. Only `Contact` objects participate in matrix assembly. `ContactInterface` is a GUI-layer data holder; it must be converted to a Contact object before assembly.

12. **NEW-03 BEARING_HEAD vs BEARING_NUT DOF assignment:** Both types map to `BearingContact` class. Need to confirm the DOF indices `node_i`/`node_j` are assigned correctly at construction time (head-side vs nut-side of the joint), so that torque contributions from head bearing friction appear at the correct DOF row in the force vector.

13. **NEW-04 Friction model dispatch in solver:** The `friction_models.py` module implements Coulomb, LuGre, Dahl, Iwan, and Bouc-Wen models, but it is not verified that `create_analyzer_from_msd_model()` or `SolverWorker` reads the user's selected friction model type from `FrictionProperties.model` field and creates the corresponding `FrictionModel` object. Default (Coulomb) may always be used.

14. **NEW-05 Wear model accumulation in time integration:** `WearModelParams` defines Archard and Fouvry models. It is not verified that `contact.update_state()` calls into these models to accumulate `wear_depth` at each time step, and that this depth is then fed back to preload loss calculation. Risk: wear model parameters are stored but wear is not accumulated during integration.

### Priority 4 — Low (Documentation / Testing)

15. **Unit tests for loading flow:** `test_loading_export()`, `test_loading_import()`, `test_loading_persistence()`.

16. **Integration tests:** Run each preset → analysis → verify results in expected range.

---

## 6. Verification Checklist

Use this checklist after any significant code change:

```bash
# Basic import checks
python -c "from bolt_analysis_studio.core.models.element import *; print('elements OK')"
python -c "from bolt_analysis_studio.core.contacts.base import *; print('contacts OK')"
python -c "from bolt_analysis_studio.visualization.loosening_plots import CoupledLooseningResultsPlotter; print('plotter OK')"
python -c "from bolt_analysis_studio.core.app_state import AppState, AnalysisResult; AppState.from_dict({'project': {}}); print('appstate OK')"

# Run application
python run_app.py                    # Must launch without errors

# Run tests
python -m pytest tests/ -v          # All tests must pass

# Manual workflow tests:
# 1. Open MSD Builder → change loading params → verify Solver Tab updates (no spurious dt recalc)
# 2. Run coupled loosening analysis → verify plots use rich CoupledLooseningResultsPlotter
# 3. Save project → close → reopen → verify results restored
# 4. Navigate to Similitude tab → verify index is correct (not opening Reports)
# 5. Open Matrix Viewer → change element in Builder → verify viewer refreshes
# 6. Test junker_test preset → all contacts should be present in model
# 7. Run time integration → check that results are non-trivial (not all zeros)
```

---

*Source: MODEL_COUPLING_STUDY.md (all batches), IMPROVEMENT_ANALYSIS_Code_vs_Reference.md*
*See also: ARCHITECTURE.md, NUMERICAL_MODELS.md, CONTACTS.md*
