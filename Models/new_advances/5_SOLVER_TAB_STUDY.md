# Solver Tab (Tab 3) Study & Improvement Recommendations

**Bolt Analysis Studio v4.0**
**Date:** 2026-02-18
**Purpose:** Audit the Solver Tab for redundancies with Tab 2 (MSD Builder), data flow issues, sync problems, and UX improvement opportunities.

---

## Table of Contents

1. [Current State Analysis](#1-current-state-analysis)
2. [Parameter Redundancy Map](#2-parameter-redundancy-map)
3. [Data Flow Issues](#3-data-flow-issues)
4. [Bugs Found](#4-bugs-found)
5. [Hidden Spinbox Architecture Problem](#5-hidden-spinbox-architecture-problem)
6. [Layout & UX Issues](#6-layout--ux-issues)
7. [Improvement Recommendations](#7-improvement-recommendations)
8. [Implementation Plan](#8-implementation-plan)

---

## 1. Current State Analysis

### 1.1 Solver Tab Layout (2-Panel Splitter)

```
+------------------------------------------------------------------------+
| SOLVER TAB (Tab 3)                                                      |
+-------------------------------+----------------------------------------+
| LEFT PANEL (40%, scroll)      | RIGHT PANEL (60%)                      |
|                               |                                        |
| Loading Summary (read-only)   | Run Analysis                           |
|  Type: Transverse (Junker)    |  [======= RUN ANALYSIS =======]       |
|  Preload: 50,000 N            |  [==== progress bar ====] 0%          |
|  Trans Disp: 0.650 mm         |  Status: Ready                        |
|  Frequency: 12.5 Hz           |  [Pause]  [Stop]                      |
|  Cycles: [2000    ]  <-EDIT   |                                        |
|  Friction: u=0.120 (lub.)     | Output Log                             |
|  Bolt: M16 x 2.0              |  +----------------------------------+  |
|  Stiffness: k_b=... k_m=...   |  | Bolt Analysis Studio v4.0       |  |
|  [Edit in MSD Builder]        |  | Ready to run analysis.          |  |
|                               |  |                                  |  |
| Time Integration              |  |                                  |  |
|  Method: [Newmark-B v]  [?]   |  |                                  |  |
|  Duration: [1.0    ] s  [?]   |  |                                  |  |
|  Step: [0.001  ] s [Auto] [?] |  |                                  |  |
|                               |  |                                  |  |
| Output Sampling               |  |                                  |  |
|  Sample %: [1.0   ] %  [?]   |  |                                  |  |
|  Max Points: [10000 ]   [?]   |  |                                  |  |
|  Interval: [1     ]     [?]   |  |                                  |  |
|                               |  |                                  |  |
| Convergence (Advanced)        |  |                                  |  |
|  Force Tol: [1e-6  ]   [?]   |  |                                  |  |
|  Disp Tol: [1e-8   ]   [?]   |  |                                  |  |
|  Max Iter: [20     ]   [?]   |  |                                  |  |
+-------------------------------+----------------------------------------+
```

### 1.2 Complete Widget Inventory

**Visible Widgets (Left Panel):**

| Group | Widget | Type | Default | Range | Editable |
|-------|--------|------|---------|-------|----------|
| Loading Summary | summary_load_type | QLabel | "Transverse (Junker)" | - | No |
| | summary_preload | QLabel | "50,000 N" | - | No |
| | summary_trans_disp | QLabel | "0.650 mm" | - | No |
| | summary_frequency | QLabel | "12.5 Hz" | - | No |
| | **summary_cycles_spin** | **QSpinBox** | **2000** | **1-10M** | **YES** |
| | summary_friction | QLabel | "u=0.120 (lubricated)" | - | No |
| | summary_bolt | QLabel | "M16 x 2.0" | - | No |
| | summary_stiffness | QLabel | "" | - | No |
| | edit_loading_btn | QPushButton | "Edit in MSD Builder" | - | - |
| Time Integration | method_combo | QComboBox | "Newmark-B" | 5 methods | Yes |
| | t_end_spin | QDoubleSpinBox | 1.0 s | 0.001-1M | Yes |
| | dt_spin | QDoubleSpinBox | 0.001 s | 1e-6 - 100 | Yes |
| | suggest_dt_btn | QPushButton | "Auto" | - | - |
| Output Sampling | sample_pct_spin | QDoubleSpinBox | 1.0% | 0.001-100 | Yes |
| | target_points_spin | QSpinBox | 10000 | 100-1M | Yes |
| | output_spin | QSpinBox | 1 | 1-1000 | Yes |
| Convergence | force_tol_spin | QDoubleSpinBox | 1e-6 | 1e-12 - 1e-3 | Yes |
| | disp_tol_spin | QDoubleSpinBox | 1e-8 | 1e-12 - 1e-3 | Yes |
| | max_iter_spin | QSpinBox | 20 | 1-100 | Yes |

**Visible Widgets (Right Panel):**

| Widget | Type | Purpose |
|--------|------|---------|
| run_btn | QPushButton | "RUN ANALYSIS" (50px tall, green) |
| progress_bar | QProgressBar | 0-100% |
| status_label | QLabel | "Ready" |
| pause_btn | QPushButton | Pause/Resume |
| stop_btn | QPushButton | Stop (red/danger) |
| console_output | QTextEdit | Monospace log output |

**Hidden Compatibility Spinboxes (9 widgets, never visible):**

| Widget | Type | Default | Synced From |
|--------|------|---------|-------------|
| amplitude_spin | QDoubleSpinBox | 0 | MSD Builder F_preload |
| trans_disp_spin | QDoubleSpinBox | 0.65 | MSD Builder delta_amplitude |
| frequency_spin | QDoubleSpinBox | 12.5 | MSD Builder frequency |
| n_cycles_spin | QSpinBox | 2000 | summary_cycles_spin + MSD Builder |
| load_type_combo | QComboBox | index 1 | MSD Builder load_type |
| mu_initial_spin | QDoubleSpinBox | 0.12 | MSD Builder mu_initial |
| lubricated_check | QCheckBox | True | MSD Builder lubricated |
| bolt_diameter_spin | QDoubleSpinBox | 16.0 | MSD Builder bolt_diameter |
| pitch_spin | QDoubleSpinBox | 2.0 | MSD Builder pitch |

---

## 2. Parameter Redundancy Map

### 2.1 The Three Redundant Parameters

The user correctly identified **three parameters that are redundant** between Tab 2 and Tab 3:

#### A. FREQUENCY

| Location | Widget | Value | Editable | Synced |
|----------|--------|-------|----------|--------|
| **Tab 2** MSD Builder | `frequency_spin` | 12.5 Hz | YES (source) | Source of truth |
| **Tab 3** Solver (visible) | `summary_frequency` | "12.5 Hz" | No (label) | One-way from Tab 2 |
| **Tab 3** Solver (hidden) | `frequency_spin` | 12.5 Hz | No (hidden) | One-way from Tab 2 |

**Problem:** Frequency appears 3 times. The Tab 3 hidden `frequency_spin` is used by `_auto_calculate_timestep()` and `_run_analysis()` but is just a copy of Tab 2.

#### B. NUMBER OF CYCLES

| Location | Widget | Value | Editable | Synced |
|----------|--------|-------|----------|--------|
| **Tab 2** MSD Builder | `cycles_label` | "N = 2000 cycles" | No (auto-calc) | From freq x time |
| **Tab 2** MSD Builder | `cycles_spin` (hidden) | 2000 | No (hidden) | From freq x time |
| **Tab 3** Solver (visible) | `summary_cycles_spin` | 2000 | **YES** | **ONE-WAY from Tab 2** |
| **Tab 3** Solver (hidden) | `n_cycles_spin` | 2000 | No (hidden) | From summary_cycles_spin |

**CRITICAL PROBLEM:** The user CAN edit `summary_cycles_spin` in Tab 3, but this change **does NOT propagate back to Tab 2**. If user changes cycles from 2000 to 5000 in the solver tab, Tab 2 still shows "N = 2000 cycles" and integration_time=160s. This is a **one-way sync bug**.

#### C. INTEGRATION TIME / DURATION

| Location | Widget | Value | Editable | Synced |
|----------|--------|-------|----------|--------|
| **Tab 2** MSD Builder | `integration_time_spin` | 160.0 s | YES (source) | Source of truth |
| **Tab 3** Solver | `t_end_spin` | 1.0 s (default) | YES | **Auto-calculated from n_cycles/freq** |

**Problem:** `integration_time` (Tab 2) and `t_end` (Tab 3) are **mathematically identical**:
```
integration_time = n_cycles / frequency
t_end = n_cycles / frequency
```
Both equal 160.0 s for the default (2000 cycles / 12.5 Hz). But:
- Tab 2 shows `integration_time_spin = 160.0 s` (user enters this)
- Tab 3 shows `t_end_spin = 160.0 s` (auto-calculated)
- They are the same number with different names
- Editing one does NOT update the other

### 2.2 Full Redundancy Matrix

```
                        Tab 2 (MSD Builder)     Tab 3 (Solver)          Sync Direction
Parameter               PropertyInspector        SolverTab
---------------------------------------------------------------------------------------
Load Type               load_type_combo          summary_load_type       Tab2 -> Tab3 (label)
                                                 load_type_combo (hid)   Tab2 -> Tab3 (hidden)

F_preload               preload_spin             summary_preload         Tab2 -> Tab3 (label)
                                                 amplitude_spin (hid)    Tab2 -> Tab3 (hidden)

Trans. Displacement     transverse_disp_spin     summary_trans_disp      Tab2 -> Tab3 (label)
                                                 trans_disp_spin (hid)   Tab2 -> Tab3 (hidden)

FREQUENCY               frequency_spin           summary_frequency       Tab2 -> Tab3 (label)
                                                 frequency_spin (hid)    Tab2 -> Tab3 (hidden)

INTEGRATION TIME        integration_time_spin    t_end_spin              NOT SYNCED!
                        (160.0 s)                (auto from cycles/freq)

N_CYCLES                cycles_label (auto)      summary_cycles_spin     Tab2 -> Tab3 ONLY
                        cycles_spin (hidden)     n_cycles_spin (hid)     Tab3 editable but
                                                                         does NOT sync back!

Friction (mu)           mu_initial_spin          (not visible)           Tab2 -> Tab3 (hidden)
                                                 mu_initial_spin (hid)

Lubricated              lubricated_check         (not visible)           Tab2 -> Tab3 (hidden)
                                                 lubricated_check (hid)

Bolt Diameter           bolt_diameter_spin       (not visible)           Tab2 -> Tab3 (hidden)
                                                 bolt_diameter_spin (hid)

Pitch                   bolt_pitch_spin          (not visible)           Tab2 -> Tab3 (hidden)
                                                 pitch_spin (hid)

Integration Method      ---                      method_combo            Tab3 only (correct)
Time Step (dt)          ---                      dt_spin                 Tab3 only (correct)
Sample %                ---                      sample_pct_spin         Tab3 only (correct)
Target Points           ---                      target_points_spin      Tab3 only (correct)
Output Interval         ---                      output_spin             Tab3 only (correct)
Force Tolerance         ---                      force_tol_spin          Tab3 only (correct)
Disp Tolerance          ---                      disp_tol_spin           Tab3 only (correct)
Max Iterations          ---                      max_iter_spin           Tab3 only (correct)
```

### 2.3 Where Parameters Are Actually Read During Analysis

In `_run_analysis()` (main_window.py line 2287), the code reads from:

| Parameter | Read From | Should Read From |
|-----------|-----------|-----------------|
| n_cycles | `solver_tab.n_cycles_spin` (hidden) | `model.global_loading.n_cycles` |
| F_preload | `model.global_loading.F_preload` (correct!) | Same |
| F_transverse | `model.global_loading.F_transverse` (correct!) | Same |
| mu_initial | `solver_tab.mu_initial_spin` (hidden) | `model.mu_initial` |
| bolt_diameter | `solver_tab.bolt_diameter_spin` (hidden) | `model.bolt_diameter` |
| pitch | `solver_tab.pitch_spin` (hidden) | `model.pitch` |
| frequency | `solver_tab.frequency_spin` (hidden) | `model.global_loading.frequency` |
| t_end | `solver_tab.t_end_spin` (visible) | OK (solver-specific) |
| dt | `solver_tab.dt_spin` (visible) | OK (solver-specific) |
| method | `solver_tab.method_combo` (visible) | OK (solver-specific) |

**Issue:** Half the parameters are read from hidden spinboxes when they should be read directly from `model.global_loading` and `model` attributes.

---

## 3. Data Flow Issues

### 3.1 One-Way Sync: Tab 2 -> Tab 3 Only

```
Tab 2 (MSD Builder)                         Tab 3 (Solver)
+-------------------+                       +-------------------+
| frequency: 12.5   |  ---- sync ---->     | freq label: 12.5  |
| integ_time: 160.0 |                       | t_end: 160.0      |
| cycles: auto 2000 |  ---- sync ---->     | cycles: [2000]    |
+-------------------+                       +-------------------+
                                                    |
                                            User edits cycles
                                            to 5000
                                                    |
                                            NO SYNC BACK!
                                                    v
+-------------------+                       +-------------------+
| frequency: 12.5   |  <-- NOT UPDATED     | cycles: [5000]    |
| integ_time: 160.0 |                       | t_end: auto 400s  |
| cycles: 2000      |  <-- STALE!          | n_cycles_hid: 5000|
+-------------------+                       +-------------------+
```

**Impact:** If user edits cycles in Tab 3 and then goes back to Tab 2, Tab 2 still shows old values. If Tab 2 emits `loading_changed`, it will overwrite Tab 3's edit with the stale value.

### 3.2 t_end Disconnect

Tab 2's `integration_time_spin` (160.0 s) and Tab 3's `t_end_spin` are the same value but:
- `integration_time` is NEVER sent to `update_loading_summary()`
- `t_end_spin` is auto-calculated from cycles/frequency via `_auto_calculate_timestep()`
- So they end up at the same value, but through different code paths
- If user edits `t_end_spin` directly in Tab 3, Tab 2 is unaware

### 3.3 The Auto-Calculate Cascade

When `summary_cycles_spin` changes in Tab 3:
```
summary_cycles_spin.valueChanged
    --> n_cycles_spin.setValue()      (sync hidden spin)
    --> _auto_calculate_timestep()   (recalculate t_end, dt, sample%)
        --> t_end_spin.setValue()     (updates duration)
        --> dt_spin.setValue()        (updates timestep)
        --> sample_pct_spin.setValue() (updates sampling)
```

This cascade works internally but **never propagates back to Tab 2**.

---

## 4. Bugs Found

### Bug 1: `case_info_label` AttributeError (CRITICAL)

**File:** main_window.py, line 928
**Code:**
```python
def refresh_theme(self):
    self.summary_load_type.setStyleSheet(...)
    self.case_info_label.setStyleSheet(...)  # <-- CRASH!
```
**Problem:** `case_info_label` is referenced in `refresh_theme()` but is **never created** in `_setup_ui()`. Calling `refresh_theme()` (e.g., when switching themes) will raise `AttributeError`.

**Fix:** Either remove the reference or add `self.case_info_label = QLabel("")` in `_setup_ui()`.

### Bug 2: Default t_end = 1.0 s Does Not Match

**File:** main_window.py, line 530
**Code:**
```python
self.t_end_spin.setValue(1.0)  # Default: 1.0 s
```
**Problem:** Default integration time in Tab 2 is 160.0 s (= 2000 cycles / 12.5 Hz), but Tab 3's `t_end_spin` defaults to 1.0 s. Until `update_loading_summary()` is called, these are mismatched. If the user runs analysis before any sync, `t_end` = 1.0 s instead of 160.0 s.

**Fix:** Either default `t_end_spin` to 160.0 s, or trigger `_auto_calculate_timestep()` on tab construction.

### Bug 3: Editable summary_cycles_spin Without Back-Sync

**File:** main_window.py, line 465-467
**Problem:** `summary_cycles_spin` is editable (QSpinBox, not QLabel), but editing it does not update Tab 2. The user may think they changed the analysis cycles, but Tab 2 retains the old value and will overwrite on next model change.

**Fix:** Either make it a read-only label (like the other summary fields), or add a signal to sync back to Tab 2.

### Bug 4: Method Combo Mapping Error

**File:** main_window.py, line 2360-2365
**Code:**
```python
method_map = {
    0: "newmark", 1: "newmark", 2: "hht",
    3: "central_diff", 4: "modal", 5: "rk4"
}
```
**Problem:** The combo has 5 items: `["Newmark-B", "HHT-a", "Central Diff", "Modal", "RK4"]` (indices 0-4). But the map has indices 0-5 and maps both 0 and 1 to "newmark", meaning:
- Index 0 (Newmark-B) -> "newmark" (correct)
- Index 1 (HHT-a) -> "newmark" (WRONG! Should be "hht")
- Index 2 (Central Diff) -> "hht" (WRONG!)
- Index 3 (Modal) -> "central_diff" (WRONG!)
- Index 4 (RK4) -> "modal" (WRONG!)

**Fix:** Correct mapping should be:
```python
method_map = {0: "newmark", 1: "hht", 2: "central_diff", 3: "modal", 4: "rk4"}
```

### Bug 5: Sample % and Target Points Conflict

When both `sample_pct_spin` and `target_points_spin` trigger `_auto_calculate_timestep()`, they can overwrite each other's values in a confusing loop (signals are blocked, but the logic uses `min(pct, target)` which means whichever is smaller wins, making the other control seem unresponsive).

---

## 5. Hidden Spinbox Architecture Problem

### 5.1 Current Architecture (Problematic)

```
Tab 2 (Source)  --->  update_loading_summary()  --->  Hidden Spinboxes  --->  _run_analysis()
     |                                                     |
     |                            _run_analysis() reads from hidden spinboxes
     |                            instead of from model.global_loading
     v
model.global_loading (correct source)
     |
     +--> _run_analysis() reads F_preload, F_transverse from HERE (correct)
     +--> but reads mu, bolt_dia, pitch, frequency from HIDDEN SPINBOXES (redundant)
```

### 5.2 Why This is Bad

1. **Double source of truth**: `_run_analysis()` reads some params from `model.global_loading` and others from hidden spinboxes. Both should come from the same source.
2. **Sync bugs**: If hidden spinboxes get out of sync (e.g., `update_loading_summary()` not called), analysis uses stale values.
3. **Maintenance burden**: 9 hidden widgets that exist only as a data relay. Any change to loading params requires updating the relay logic.
4. **Confusion**: Developers see `solver_tab.frequency_spin` and assume it's an editable solver parameter, when it's actually a hidden relay.

### 5.3 Correct Architecture (Proposed)

```
Tab 2 (Source)  --->  model.global_loading (stored in MSDModel)
                               |
                               v
                      _run_analysis() reads ALL params from model
                               |
                               v
                      Tab 3 displays read-only summary
```

**Remove all 9 hidden spinboxes.** Have `_run_analysis()` read directly from `self.app_state.model.global_loading` and `self.app_state.model` attributes.

---

## 6. Layout & UX Issues

### 6.1 Right Panel Wastes Space Before Analysis

The right panel (60% width) shows only:
- A "RUN ANALYSIS" button (50px)
- An empty progress bar
- An empty console

Before analysis runs, 60% of the tab is **blank** with just a large empty QTextEdit. This is wasted space.

### 6.2 Left Panel Too Narrow for Content

The loading summary, time integration, sampling, and convergence groups are packed into 40% width (min 280px, max 500px). On a standard 1200px window, that's 480px - barely enough for the form layout with help buttons.

### 6.3 Help Buttons ("?") Clutter

Every input field has a tiny 20x20 "?" help button next to it. That's 9 help buttons in the left panel alone. While well-intentioned, they:
- Add visual noise
- Take horizontal space from input fields
- Could be replaced by richer tooltips

### 6.4 Console Output Not Useful Until Running

The console shows "Bolt Analysis Studio v4.0 / Ready to run analysis." and nothing else until analysis starts. It should show useful pre-analysis information:
- Model summary (elements, DOF, materials)
- Loading configuration summary
- Estimated computation time
- Validation status

### 6.5 No Pre-Run Validation

The "RUN ANALYSIS" button runs immediately without checking if the model is valid. Should show warning if:
- No model loaded
- F_preload = 0
- No elements in model
- Model validation fails

### 6.6 Progress Bar Lacks Detail

Current progress is a single 0-100% bar. It could show:
- Which analysis phase is running (Modal/Static/Preload/Coupled/Time)
- Phase-specific progress within each phase
- Estimated time remaining

---

## 7. Improvement Recommendations

### 7.1 CRITICAL: Fix the Redundancy

**Recommendation: Remove frequency/cycles/time redundancy by making Tab 3 fully derived from model.**

**Option A (Recommended): Remove editable cycles from Tab 3, display-only**
```python
# Replace summary_cycles_spin (editable QSpinBox) with QLabel (read-only)
self.summary_cycles = QLabel("2,000")  # Not a spinbox!

# Display integration time alongside
self.summary_time = QLabel("160.0 s")

# Add "Edit in MSD Builder" for ALL loading params
```

If the user needs to change cycles, they go to Tab 2 (which is the single source of truth). Tab 3 only displays what Tab 2 configured.

**Option B: Bidirectional sync (more complex)**
```python
# If summary_cycles_spin must stay editable, sync back to Tab 2:
self.summary_cycles_spin.valueChanged.connect(self._sync_cycles_to_builder)

def _sync_cycles_to_builder(self, n_cycles):
    """Propagate cycle count change back to MSD Builder."""
    freq = self.solver_tab.frequency_spin.value()
    if freq > 0:
        integration_time = n_cycles / freq
        self.msd_builder_window.inspector.integration_time_spin.setValue(integration_time)
```

### 7.2 Remove Hidden Spinbox Layer

Replace the 9 hidden spinboxes with direct model access in `_run_analysis()`:

```python
def _run_analysis(self):
    model = self.app_state.model
    gl = model.global_loading  # All loading params from here

    config.coupled_loosening_config.n_cycles = gl.n_cycles
    config.coupled_loosening_config.initial_preload = gl.F_preload
    config.coupled_loosening_config.transverse_force = gl.F_transverse
    config.coupled_loosening_config.mu_initial = model.mu_initial
    config.coupled_loosening_config.bolt_diameter_mm = model.bolt_diameter
    config.coupled_loosening_config.pitch_mm = model.pitch

    config.preload_config.n_cycles = gl.n_cycles
    config.preload_config.initial_preload = gl.F_preload
    config.preload_config.frequency = gl.frequency

    config.time_config.t_end = gl.n_cycles / gl.frequency
    config.time_config.load_amplitude = gl.F_preload
    config.time_config.load_frequency = gl.frequency

    # Solver-specific params stay on solver tab (correct):
    config.time_config.method = method_map[self.solver_tab.method_combo.currentIndex()]
    config.time_config.dt = self.solver_tab.dt_spin.value()
    # ... convergence, sampling, etc.
```

### 7.3 Redesign Layout: 3-Section Vertical

Replace the 2-panel (40/60) split with a cleaner vertical layout:

```
+------------------------------------------------------------------------+
| SOLVER TAB                                                              |
+------------------------------------------------------------------------+
| LOADING SUMMARY (horizontal bar, compact, read-only)                   |
| Type: Transverse | F0: 79,128 N | d: 0.65mm | f: 12.5Hz | N: 2,000  |
| u: 0.12 (lub) | M16x2.0 | kb: 505k N/mm  km: 1,522k N/mm            |
|                                           [Edit in MSD Builder]        |
+------------------------------------------------------------------------+
| SOLVER CONFIGURATION                          | RUN & MONITOR          |
| +-------------------------------------------+ | +--------------------+ |
| | Time Integration  | Output Sampling       | | | [= RUN ANALYSIS =] | |
| | Method: [Newmark] | Sample: [1.0]%        | | | [===== 45% =====]  | |
| | dt:  [0.001] s    | Points: [10000]       | | | Phase: Coupled     | |
| | t_end: [160.0] s  | Interval: [1]         | | | ETA: ~30s          | |
| |                    |                       | | | [Pause] [Stop]     | |
| | Convergence        |                       | | +--------------------+ |
| | F tol: [1e-6]     |                       | |                        |
| | d tol: [1e-8]     |                       | | Validation:            |
| | Iter:  [20]       |                       | | [*] Model valid        |
| +-------------------------------------------+ | [*] Preload > 0        |
|                                                | [*] Elements: 4        |
|                                                | [ ] Contacts OK        |
+------------------------------------------------------------------------+
| OUTPUT LOG (collapsible, shows on run)                                  |
| --- Starting full analysis suite ---                                    |
| Load Type: Transverse (Junker)                                          |
| Preload: 79,128 N | Transverse: 10,000 N                              |
| Cycles: 2,000 | Sample interval: 20 | Output points: ~100             |
+------------------------------------------------------------------------+
```

### 7.4 Compact Loading Summary Bar

Replace the form-based loading summary with a single horizontal info bar:

```python
class LoadingSummaryBar(QWidget):
    """Compact horizontal bar showing loading configuration."""

    def update(self, loading_data):
        # Single-line format:
        # "Transverse | F0=79.1 kN | d=0.65mm | f=12.5Hz | N=2,000 | u=0.12 (lub) | M16x2.0"
        parts = [
            f"<b>{load_type}</b>",
            f"F<sub>0</sub>={preload/1000:.1f} kN",
            f"d={trans_disp:.2f}mm",
            f"f={freq:.1f}Hz",
            f"N={cycles:,}",
            f"u={mu:.3f} ({'lub' if lubricated else 'dry'})",
            f"M{bolt_dia:.0f}x{pitch:.1f}",
        ]
        self.label.setText("  |  ".join(parts))
```

This saves ~120px vertical space compared to the current form layout.

### 7.5 Pre-Run Validation Checklist

Add a validation checklist that updates in real-time:

```python
class PreRunChecklist(QWidget):
    """Shows readiness indicators before running analysis."""

    def update_from_model(self, model):
        checks = [
            ("Model loaded", model is not None),
            ("Elements present", model and len(model.elements) > 0),
            ("Preload > 0", model and model.global_loading.F_preload > 0),
            ("Contacts defined", model and len(model.contacts) > 0),
            ("Model validated", self._last_validation_passed),
        ]
        for label, check_widget, (name, passed) in zip(...):
            check_widget.setText("OK" if passed else "!")
            check_widget.setStyleSheet(
                f"color: {Theme.GREEN}" if passed else f"color: {Theme.RED}"
            )
```

### 7.6 Replace "?" Help Buttons with Rich Tooltips

Remove the 9 tiny "?" buttons and use rich HTML tooltips instead:

```python
# Instead of:
dt_spin + help_btn("Time Step: Too large -> instability")

# Use:
dt_spin.setToolTip(f"""
    <b>Time Step (dt)</b><br>
    Integration step size in seconds.<br><br>
    <b>Rules of thumb:</b><br>
    - dt &lt; T<sub>min</sub>/10 for stability<br>
    - dt &lt; T<sub>min</sub>/20 for accuracy<br><br>
    <span style='color:{Theme.OVERLAY}'>
    Too large: instability<br>
    Too small: slow computation
    </span>
""")
```

This saves ~60px horizontal space per row and reduces visual clutter.

### 7.7 Console Shows Pre-Analysis Info

Before analysis runs, populate the console with useful context:

```python
def _update_pre_analysis_info(self):
    self.console_output.clear()
    self.console_output.append("Bolt Analysis Studio v4.0\n")

    if model:
        self.console_output.append(f"Model: {len(model.elements)} elements, {model.n_dof} DOF")
        self.console_output.append(f"Loading: {model.global_loading.type}")
        self.console_output.append(f"  F_preload = {model.global_loading.F_preload:,.0f} N")
        self.console_output.append(f"  F_trans   = {model.global_loading.F_transverse:,.0f} N")
        self.console_output.append(f"  frequency = {model.global_loading.frequency} Hz")
        self.console_output.append(f"  n_cycles  = {model.global_loading.n_cycles:,}")

        # Estimated computation time
        est_time = self._estimate_computation_time()
        self.console_output.append(f"\nEstimated runtime: ~{est_time:.0f}s")
    else:
        self.console_output.append("No model loaded. Build model in Tab 2.")

    self.console_output.append("\nReady to run analysis.")
```

### 7.8 Progress Bar with Phase Indicator

```python
# Instead of a single progress bar:
self.progress_bar.setValue(45)
self.status_label.setText("Running coupled loosening analysis...")

# Show phase-specific progress:
self.phase_label.setText("Phase 3/5: Coupled Loosening")
self.phase_progress.setValue(60)  # 60% within this phase
self.overall_progress.setValue(45)  # 45% overall
self.eta_label.setText("ETA: ~30s remaining")
```

### 7.9 Fix Method Combo Mapping

```python
# CURRENT (WRONG):
method_map = {0: "newmark", 1: "newmark", 2: "hht", 3: "central_diff", 4: "modal", 5: "rk4"}

# CORRECT:
method_map = {0: "newmark", 1: "hht", 2: "central_diff", 3: "modal", 4: "rk4"}
```

### 7.10 Auto-Calculate t_end from Tab 2 Integration Time

When `update_loading_summary()` is called, also set `t_end_spin`:

```python
def update_loading_summary(self, loading_data):
    # ... existing label updates ...

    # Sync t_end from integration_time (they are the same thing)
    integration_time = loading_data.get("integration_time", 0)
    if integration_time > 0:
        self.t_end_spin.blockSignals(True)
        self.t_end_spin.setValue(integration_time)
        self.t_end_spin.blockSignals(False)
```

---

## 8. Implementation Plan

### Phase 1: Fix Critical Bugs (Immediate)

| # | Fix | Severity | File | Lines |
|---|-----|----------|------|-------|
| 1 | Fix `case_info_label` AttributeError | CRITICAL | main_window.py | 928 |
| 2 | Fix method_combo mapping (0,1 both -> newmark) | CRITICAL | main_window.py | 2360-2365 |
| 3 | Sync `t_end_spin` from `integration_time` | HIGH | main_window.py | 864-923 |
| 4 | Default `t_end_spin` to 160.0 (match Tab 2) | HIGH | main_window.py | ~530 |

### Phase 2: Remove Redundancy (High Priority)

| # | Change | Impact | File |
|---|--------|--------|------|
| 5 | Make `summary_cycles_spin` read-only (QLabel) | Eliminates one-way sync bug | main_window.py |
| 6 | Add `integration_time` display to summary | Clarifies t_end = integration_time | main_window.py |
| 7 | Remove 9 hidden spinboxes | Simplifies architecture | main_window.py |
| 8 | Read all params from model in `_run_analysis()` | Single source of truth | main_window.py |

### Phase 3: Layout Improvements (Medium Priority)

| # | Change | Impact | File |
|---|--------|--------|------|
| 9 | Compact loading summary bar (horizontal) | Saves vertical space | main_window.py |
| 10 | Replace "?" buttons with rich tooltips | Cleaner UI, more space | main_window.py |
| 11 | Add pre-run validation checklist | Prevents failed runs | main_window.py |
| 12 | Pre-populate console with model info | Better UX before run | main_window.py |

### Phase 4: Polish (Low Priority)

| # | Change | Impact | File |
|---|--------|--------|------|
| 13 | Phase-specific progress bar | Better feedback | main_window.py |
| 14 | Estimated time remaining | User expectation | main_window.py |
| 15 | Collapsible console (hidden until run) | Less empty space | main_window.py |
| 16 | Solver-specific presets (dt, method, convergence) | Faster setup | main_window.py |

---

## Summary

The Solver Tab has **4 critical bugs** and **3 fundamental redundancy problems** with the MSD Builder:

1. **Frequency** exists in 3 places (Tab 2 source, Tab 3 label, Tab 3 hidden spin)
2. **Cycles** is editable in Tab 3 but never syncs back to Tab 2
3. **Integration time** (Tab 2) and **t_end** (Tab 3) are mathematically identical but disconnected
4. **9 hidden spinboxes** relay data that should be read directly from `model.global_loading`
5. **Method combo mapping is wrong** - HHT, Central Diff, Modal, RK4 are all mapped to the wrong solver
6. **`case_info_label`** referenced but never created (crashes on theme switch)

The core recommendation: **Tab 3 should ONLY contain solver-specific parameters** (method, dt, convergence, sampling) and display everything else as read-only from Tab 2's model. Remove the hidden spinbox relay layer entirely.
