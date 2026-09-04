# Similitude Tab (Tab 5) — Comprehensive Study

**Bolt Analysis Studio v4.0** — internal reference / Petrobras R&D
**Date:** 2026-02-18
**Scope:** Complete audit of the Similitude tab architecture, workflow, layout, responsiveness, visual design, integration with the rest of the application, and all bugs found during code review.

---

## Table of Contents

1. [System Overview — What Exists](#1-system-overview--what-exists)
2. [Architecture Bugs — Critical Defects](#2-architecture-bugs--critical-defects)
3. [Workflow Analysis](#3-workflow-analysis)
4. [Layout & Navigation Issues](#4-layout--navigation-issues)
5. [Visual Design Issues](#5-visual-design-issues)
6. [Responsiveness Issues](#6-responsiveness-issues)
7. [Integration with Other Tabs](#7-integration-with-other-tabs)
8. [Backend Engine Assessment](#8-backend-engine-assessment)
9. [Proposed Workflow Redesign](#9-proposed-workflow-redesign)
10. [Proposed Layout Architecture](#10-proposed-layout-architecture)
11. [New Integration Signals](#11-new-integration-signals)
12. [Implementation Priority Matrix](#12-implementation-priority-matrix)
13. [Code Snippets for Key Fixes](#13-code-snippets-for-key-fixes)

---

## 1. System Overview — What Exists

### 1.1 Two Parallel Implementations (Design Problem)

The application has **two completely separate Similitude Tab implementations** that are switched at runtime:

```python
# main_window.py line 1647
if HAS_ENHANCED_SIMILITUDE:
    self.similitude_tab = create_similitude_tab()  # similitude_tab.py
else:
    self.similitude_tab = SimilitudeTab()           # main_window.py (fallback)
```

| Aspect | `SimilitudeTab` (fallback) | `EnhancedSimilitudeTab` (main) |
|--------|---------------------------|-------------------------------|
| Location | `main_window.py:1165` | `similitude_tab.py:1591` |
| Data | All hardcoded/fake | Computed from real analysis |
| Pi table | 5 rows, static strings | Live from `PiGroupDisplayPanel` |
| Comparison table | 7 rows, hardcoded values | `ComparisonPlotsPanel` with matplotlib |
| Compute btn | Not connected to anything | Connected to `_compute_reduction()` / `_compute_scaling()` |
| Transfer btn | Not connected | Connected via `transfer_to_builder` signal |
| Condition | `HAS_SIMILITUDE = False` | `HAS_SIMILITUDE = True` |

**The fallback `SimilitudeTab` must never be shown to users.** It creates a false impression that analysis has been done when no computation occurred at all.

### 1.2 Enhanced Similitude Tab Architecture

When active, the Enhanced tab has this nesting structure:

```
EnhancedSimilitudeTab (QWidget, VBoxLayout)
├── analysis_tabs (QTabWidget, 2 tabs)
│   ├── Tab 0: "Multi-Bolt"  ← MultiBoltReductionPanel
│   │   └── sub_tabs (QTabWidget, 4 sub-tabs)
│   │       ├── Sub 0: "Parameters"       ← Input spinboxes
│   │       ├── Sub 1: "Results"          ← Table + [Compute] button
│   │       ├── Sub 2: "Transfer"         ← Summary card + [Transfer] button
│   │       ├── Sub 3: "Pi Groups"        ← PiGroupDisplayPanel (injected from outside)
│   │       └── Sub 4: "Comparison Plots" ← ComparisonPlotsPanel (injected from outside)
│   │
│   └── Tab 1: "Scaling"  ← GeometricScalingPanel
│       └── sub_tabs (QTabWidget, 5 sub-tabs)
│           ├── Sub 0: "Prototype"        ← Prototype params + scale factor
│           ├── Sub 1: "Results"          ← Table + [Compute] button
│           ├── Sub 2: "Corrections"      ← Scale effect labels + [Transfer]
│           ├── Sub 3: "Suggested Model"  ← SuggestedConfigPanel (injected)
│           ├── Sub 4: "Error Analysis"   ← ErrorAnalysisPanel (injected)
│           └── Sub 5: "Comparison Plots" ← ComparisonPlotsPanel (injected)
│
└── export_layout (QHBoxLayout, bottom bar)
    ├── [Export Report]
    ├── [Export JSON]
    ├── [Export Plot]
    └── [Transfer to Builder]  ← Only works if ScaledLooseningModel is available
```

**Total nesting depth: 3 levels.** Requires 2 tab-clicks to reach results from the top level.

### 1.3 Backend Classes

| Class | File | Purpose |
|-------|------|---------|
| `ScaleFactors` | `similitude.py:55` | 20 derived scale factor properties (λ, λ², λ³...) |
| `PiGroup` | `similitude.py:229` | Buckingham-Π group with prototype/model comparison |
| `ScaleEffect` | `similitude.py:309` | Scale corrections: roughness, friction, embedding, thread |
| `PrototypeData` | `similitude.py:539` | Full prototype parameter set (geometry, material, loading, friction) |
| `SimilitudeAnalysis` | `similitude.py:689` | Main analysis class combining all above |
| `ScaledLooseningModel` | `loosening_similitude.py` | Output of `create_scaled_loosening_model()` |
| `EquivalentSingleBolt` | `loosening_similitude.py` | Output of `reduce_multi_bolt_to_single()` |
| `LooseningSimlitudeAnalysis` | `loosening_similitude.py` | Orchestrator (partially used) |

---

## 2. Architecture Bugs — Critical Defects

### BUG-01 — Tab Index Hardcoded Wrong (Critical)

**Location:** `main_window.py:4336`

```python
def _go_to_similitude_tab(self, sub_tab_index: int = 0):
    similitude_tab_index = 5  # "6. Similitude" tab   ← WRONG INDEX
    self.tab_widget.setCurrentIndex(similitude_tab_index)
```

**Problem:** The actual `addTab` order is:
```
Index 0: "1. 📁 Project"
Index 1: "2. 🔧 Model Builder"
Index 2: "3. ⚙️ Solver"
Index 3: "4. 📈 Results"
Index 4: "5. ⚖️ Similitude"   ← CORRECT INDEX IS 4
Index 5: "6. 📋 Reports"
Index 6: "7. 📖 Documentation"
```

**Effect:** Every toolbar click "⚖️ Similitude" and every menu action under "Similitude Analysis" navigates to the **Reports tab** instead of Similitude. The comment even contradicts itself ("6. Similitude tab" when the label says "5.").

**Fix:**
```python
similitude_tab_index = 4  # "5. ⚖️ Similitude" tab (0-indexed)
```

---

### BUG-02 — Transfer to MSD Builder Does Nothing (Critical)

**Location:** `main_window.py:4393`

```python
def _on_similitude_transfer(self, elements: dict):
    """Handle transfer of model from similitude analysis to MSD Builder."""
    self._open_msd_builder()   # Opens MSD Builder with CURRENT model
    self._on_status_message("Similitude model transferred to MSD Builder")
    # 'elements' parameter is NEVER used!
```

**Problem:** The `elements` dict (containing MSD element parameters from the scaled/equivalent model) is received but completely ignored. The MSD Builder is opened but loaded with whatever model already exists, not the transferred elements. The user receives a success message for a transfer that didn't happen.

**Fix:** Pass `elements` to the MSD Builder:
```python
def _on_similitude_transfer(self, elements: dict):
    self._open_msd_builder()
    if self.msd_builder_window and elements:
        self.msd_builder_window.load_from_elements_dict(elements)
    self._on_status_message("Similitude model transferred to MSD Builder")
```

---

### BUG-03 — LooseningSimlitudeAnalysis Created Empty (High)

**Location:** `similitude_tab.py:1703, 1742`

```python
def _on_reduction_computed(self, equivalent):
    if HAS_SIMILITUDE:
        self.analysis = LooseningSimlitudeAnalysis()  # Created empty!
        # equivalent data is NEVER passed to self.analysis

def _on_scaling_computed(self, scaled):
    if HAS_SIMILITUDE:
        self.analysis = LooseningSimlitudeAnalysis()  # Created empty!
        # scaled data is NEVER passed to self.analysis
```

**Effect:** When `_export_report()` calls `self.analysis.generate_report()`, the report returns empty Π-group data. The exported Markdown report's "## Π-Groups" section is always blank.

---

### BUG-04 — Loosening Curves Use Hardcoded Parameters (High)

**Location:** `similitude_tab.py:1752-1774`

```python
# Two-stage decay parameters (Jiang 2003) — HARDCODED!
lambda1, lambda2 = 0.012, 0.003
N_trans = 200
```

**Problem:** The comparison plots always show the same Jiang decay curve regardless of the actual model parameters (bolt size, preload, frequency, friction coefficient). The `scaled.scale_factor` is used for axis scaling, but the curve shape never changes. This makes the comparison plots scientifically misleading — they appear to show computed results but are actually illustrative placeholders.

---

### BUG-05 — Fallback SimilitudeTab Has Disconnected Compute Button (High)

**Location:** `main_window.py:1342-1354`

```python
self.compute_btn = QPushButton("Compute")
self.compute_btn.setObjectName("primary")
# ...
# No .clicked.connect() call anywhere
```

**Effect:** In the fallback tab (when `HAS_SIMILITUDE = False`), the primary "Compute" button does nothing. Users may repeatedly click it without any feedback.

---

### BUG-06 — Compute Button in Wrong Sub-Tab (Usability)

**Location:** `similitude_tab.py:214-218` (MultiBoltReductionPanel) and `similitude_tab.py:569-572` (GeometricScalingPanel)

```python
# In Results sub-tab (sub-tab 1), NOT in Parameters sub-tab (sub-tab 0)
compute_btn = QPushButton("Compute Equivalent Single Bolt")
compute_btn.clicked.connect(self._compute_reduction)
results_vlayout.addWidget(compute_btn)
```

**Problem:** The user sets parameters in sub-tab 0 ("Parameters") but must navigate to sub-tab 1 ("Results") to trigger computation. This breaks the natural input→compute→results flow. The user must context-switch between panels to operate the tool.

---

### BUG-07 — Pi-Groups Panel Default State Is Misleading (Medium)

**Location:** `similitude_tab.py:806-814`

```python
pi_data = [
    ("Π₁", "Slip Parameter", "F_t / (μ_b × F_p)", "0.500", "✓"),
    ("Π₂", "Helix Parameter", "tan(λ) / (μ_t × sec(α))", "0.285", "✓"),
    ...
]
```

**Problem:** The Π-group panel initializes with hardcoded values and all "✓" status. Before any analysis, the user sees a fully populated table with green checkmarks, creating the impression that similitude has already been verified. This is analogous to a voltmeter that always shows "12V" before being connected to anything.

---

### BUG-08 — Transfer Panel sub-tab (Sub 2) and Corrections Panel (Sub 2) Both Named Differently But Serve Same Purpose (Low)

In `MultiBoltReductionPanel`, Sub 2 is "Transfer" with a transfer button.
In `GeometricScalingPanel`, Sub 2 is "Corrections" with a transfer button AND scale effect labels.

The transfer functionality is duplicated across: Sub 2 transfer buttons in each panel + the global "Transfer to Builder" button in the bottom export bar. Three separate mechanisms for the same action, with inconsistent conditions.

---

## 3. Workflow Analysis

### 3.1 Intended Workflow (from code)

The intended workflow can be reconstructed from the code:

```
WORKFLOW A: Multi-Bolt Reduction
  Sub-tab "Parameters" → Set n, d, p, L, F_p, F_t, BCD, μ, pattern
  Sub-tab "Results"    → Click [Compute] → table fills → auto-switches tab
  Sub-tab "Transfer"   → Click [Transfer to MSD Builder]
  Sub-tab "Pi Groups"  → View Π-group match status (auto-updates)
  Sub-tab "Comparison Plots" → View loosening curves

WORKFLOW B: Geometric Scaling
  Sub-tab "Prototype"  → Set d_p, p_p, L_p, F_p, f_p, λ, cycle_mode, standard
  Sub-tab "Results"    → Click [Compute] → table fills → auto-switches to "Suggested Model"
  Sub-tab "Corrections" → View C_mu, C_e, C_pitch, C_total; click [Transfer]
  Sub-tab "Suggested Model" → View M×× bolt, preload, frequency, interpretation
  Sub-tab "Error Analysis"  → View parameter-by-parameter error table
  Sub-tab "Comparison Plots" → View F/F₀ vs N curves
```

### 3.2 Actual User Experience (Problems)

| Step | Expected | Actual |
|------|---------|--------|
| Open Tab 5 from toolbar | Navigate to Similitude | Navigate to **Reports** (BUG-01) |
| Enter parameters | One panel, clear flow | Fragmented across 2 panels in parallel with no linking |
| Click "Compute" | Trigger from parameter panel | Must first switch to "Results" sub-tab (BUG-06) |
| View Π-groups before compute | See empty / placeholder | See pre-filled fake data (BUG-07) |
| Transfer to MSD Builder | Parameters appear in Builder | MSD Builder opens with old model (BUG-02) |
| View comparison plots | See computed loosening curves | See hardcoded Jiang curves (BUG-04) |
| Export report | Get report with Π-groups | Get Π-group section always blank (BUG-03) |
| Import model from Tab 2 | Auto-populate Similitude params | Requires manual re-entry |

### 3.3 Missing Workflow: Two-Stage Analysis Sequence

The natural workflow for a real laboratory test campaign is:

```
STAGE 1 — Test Design (BEFORE building the physical model)
  └─ Define prototype joint parameters
  └─ Choose scale factor (λ)
  └─ Compute scale effects and corrections
  └─ Find nearest standard bolt size
  └─ Compute target preload and frequency for the model
  └─ Export test setup document

STAGE 2 — Analysis (AFTER running the model test)
  └─ Import model test data (CSV)
  └─ Apply scale effect corrections to model data
  └─ Compare corrected model results to prototype prediction
  └─ Evaluate similitude quality (Π-group deviations)
  └─ Export validated results

STAGE 3 — Multi-bolt generalization (if needed)
  └─ Use single-bolt results to predict n-bolt assembly behavior
  └─ Compare with multi-bolt FEA or test data
```

Currently there is **no clear distinction** between Stage 1 (pre-test design) and Stage 2 (post-test validation). The tab mixes both without guidance.

---

## 4. Layout & Navigation Issues

### 4.1 Navigation Depth Problem

```
Current: 3 levels deep
Main tabs → Analysis type tab → Sub-tab

User clicks to reach "Error Analysis":
1. Click "5. ⚖️ Similitude" tab
2. Click "Scaling" analysis type tab
3. Click "Error Analysis" sub-tab
```

This is excessive for what is essentially a side panel within one workflow.

### 4.2 Sub-tab Auto-Switch on Compute

When compute completes, the code auto-switches to the Results sub-tab:
```python
self.sub_tabs.setCurrentIndex(1)  # MultiBoltReduction
self.scaling_panel.sub_tabs.setCurrentIndex(3)  # GeometricScaling → Suggested Model
```

This jumps the user away from their parameters, making it awkward to adjust and recompute.

### 4.3 Fallback Tab Layout Issues

In the fallback `SimilitudeTab`:
- Pi-group table has `setMaximumHeight(180)` — clips rows beyond 5 entries
- Scale factor spinboxes have no label explaining what they affect
- The vertical splitter puts the tiny "Actions" group in a sizable drag handle, making it hard to use
- No `QScrollArea` — clips on small screens

### 4.4 EnhancedSimilitudeTab Missing QScrollArea

Neither the `MultiBoltReductionPanel` nor the `GeometricScalingPanel` sub-tabs are wrapped in `QScrollArea`. On small monitors (< 900px tall), the parameter forms get clipped.

### 4.5 Export Bar Always Enabled

The bottom export bar buttons (Export Report, Export JSON, Export Plot) are always visible and clickable. Clicking them before any analysis shows a `QMessageBox.warning`. Better: disable buttons initially, enable them after first successful compute.

### 4.6 No Status Indicator

There is no indication of:
- Whether Multi-Bolt analysis has been run
- Whether Scaling analysis has been run
- Quality of last result at a glance
- Whether transfer was successful

### 4.7 "Transfer to Builder" at Bottom Bar vs. In Each Sub-Panel

The global "Transfer to Builder" button at the bottom always transfers the **scaling** result (from `self.last_scaled_model`). But each panel also has its own "Transfer to MSD Builder" button in its sub-tabs. This creates confusion:
- Which transfer action does what?
- Can you transfer from Multi-Bolt reduction independently?
- What if both analyses have been run — which result gets transferred?

---

## 5. Visual Design Issues

### 5.1 Inconsistent Panel Header Colors

| Panel | Header Color | Rationale |
|-------|-------------|-----------|
| `MultiBoltReductionPanel` | `Theme.BLUE` | None — arbitrary |
| `GeometricScalingPanel` | `Theme.MAUVE` | None — arbitrary |
| `PiGroupDisplayPanel` | `Theme.TEAL` | None — arbitrary |
| `SuggestedConfigPanel` | `Theme.GREEN` | Possibly "success" |
| `ErrorAnalysisPanel` | `Theme.RED` | Possibly "warning/error" |
| `ComparisonPlotsPanel` | `Theme.PEACH` | None — arbitrary |

There is no visual system. Each panel was colored independently. No color communicates meaning consistently.

**Proposed color system:**
- Blue → Inputs / Configuration
- Mauve → Computation / Analysis
- Green → Validated results / Suggestions
- Yellow → Warnings / Corrections
- Teal → Dimensionless groups / Theory
- Red → Errors / Critical deviations only

### 5.2 Interpretation Text Box Too Small

`SuggestedConfigPanel.interpretation_text` has `setMaximumHeight(100)` — exactly the same problem found in Tab 1's description field.

### 5.3 Pi Group Table — 5-Column Layout Too Wide

The 5-column Pi table (Symbol | Name | Expression | Value | Status) creates columns that are individually too narrow to read. At typical window widths (1200-1400px), the "Expression" column shows truncated formulas.

**Proposed:** Replace with 4-column table: Symbol | Expression | Value | Match%. Remove "Name" column and add it as tooltip on Symbol cell.

### 5.4 No Loading Indicator During Compute

Both `_compute_reduction()` and `_compute_scaling()` run synchronously on the main thread. For large parameter sweeps or sensitivity analyses this can freeze the UI. No `QProgressBar` or `QLabel("Computing...")` indicator exists.

### 5.5 Quality Badge Not Visible at Top Level

The quality score (Excellent/Good/Acceptable/Poor) is only visible inside sub-tabs. At the top level of `EnhancedSimilitudeTab`, there is no overall quality indicator. A user cannot tell at a glance whether the similitude is valid.

---

## 6. Responsiveness Issues

### 6.1 No QSplitter Between Analysis Type Tabs and Content

The main `analysis_tabs` QTabWidget takes all available space with no splitter. The user cannot resize the parameter panel vs. the results view.

### 6.2 Sub-Tab Header Overflow

`setElideMode(Qt.TextElideMode.ElideNone)` on sub-tabs prevents text truncation but causes layout overflow when the panel is narrow. Sub-tab labels start overlapping at widths below ~600px.

### 6.3 Parameter Forms Have No Minimum Width

The `QFormLayout` in parameter panels has no `setMinimumWidth()`. On narrow monitors, spinbox labels and values compress into unreadable layout.

### 6.4 Comparison Plots Fixed Figure Height

```python
fig_h = 9 if self.mode == "scaling" else 6
self.plot_widget = PlotWidget(toolbar=True, width=10, height=fig_h)
self.plot_widget.setMinimumHeight(400)
```

The plot widget uses a fixed-height matplotlib figure. On tall monitors, the plot doesn't expand to fill available space. On small monitors, `setMinimumHeight(400)` may occupy most of the tab height, pushing the controls off-screen.

### 6.5 EnhancedSimilitudeTab Has No Maximum Width for Left Panels

Parameter sub-tabs in both panels can expand to fill the full window width, making spinbox inputs uncomfortably wide. Maximum widths should be set on form containers.

---

## 7. Integration with Other Tabs

### 7.1 Tab 2 (MSD Builder) → Similitude: One-Way (and Manual)

**Current state:** No automatic data flow from MSD Builder to Similitude.

When the user has a model in the MSD Builder with a bolt diameter of M24, grip length 100mm, preload 160kN — they must manually retype all these values into the Similitude panels.

**Required:** "Import from current model" functionality that reads `AppState.current_model` and populates:
- `MultiBoltReductionPanel`: diameter, pitch, grip length, preload, mu_thread, mu_bearing
- `GeometricScalingPanel`: prototype diameter, pitch, grip length, preload (prototype parameters)

### 7.2 Similitude → Tab 2 (MSD Builder): Broken (BUG-02)

**Current state:** Transfer signal emitted, received in `BoltAnalysisStudio._on_similitude_transfer()`, `elements` dict silently discarded.

**Required:** `load_from_elements_dict(elements)` method in `MSDBuilderWindow` that converts the `elements` dict from `create_msd_elements_from_scaled()` / `create_msd_elements_from_equivalent()` into actual model elements.

### 7.3 Similitude → Tab 3 (Solver): No Connection

**Current state:** No data flows from Similitude to Solver.

**Missing feature:** After computing the scaled model, the user should be able to push the scaled parameters (frequency, cycles, preload) directly to the Solver tab's configuration, in addition to transferring to the MSD Builder.

**Required:** A "Send to Solver" button that calls `solver_tab.update_loading_summary()` with the scaled model parameters:
```python
loading_data = {
    "F_preload": scaled.model_preload,
    "frequency": scaled.model_frequency,
    "n_cycles": int(N_model_max),
    ...
}
```

### 7.4 Similitude → Tab 4 (Results): No Connection

**Current state:** After running a solver analysis (Tab 3), the actual F/F₀ vs N curve from Tab 4 cannot be overlaid on the Similitude comparison plots.

**Missing feature:** `ComparisonPlotsPanel` should have an "Import from Solver Results" option that loads the `CoupledLooseningResult` time series and overlays it on the comparison plots as a third series alongside the Prototype and Model predictions.

### 7.5 Similitude → Tab 6 (Reports): Manual File Export Only

**Current state:** Similitude export goes to a user-chosen `.md` file via `_export_report()`. The Reports tab (Tab 6) generates its own report independently, with no similitude section.

**Missing feature:** The Reports tab's `_generate_report_html()` method should include a similitude section that reads `AppState.similitude_result` (a new state field) and generates the appropriate HTML/PDF section.

### 7.6 No AppState Field for Similitude Results

**Current state:** `AppState` (in `core/app_state.py`) has fields for `model`, `analysis_results`, etc., but no field for `similitude_result` or `scaled_model`.

**Required:**
```python
@dataclass
class AppState:
    ...
    similitude_scaled_model: Optional[ScaledLooseningModel] = None
    similitude_equivalent_bolt: Optional[EquivalentSingleBolt] = None
    similitude_quality: float = 0.0
```

This allows other tabs (Reports, Results) to access similitude results without re-computation.

---

## 8. Backend Engine Assessment

### 8.1 `ScaleFactors` — Well Implemented

20 derived properties computed from `geometric`, `elastic_modulus_ratio`, and `density_ratio`. The math is physically correct for elastic similitude. The `to_table()` method is useful for display.

**Gap:** `ScaleFactors.__post_init__` rejects `geometric > 1` (upscaling). This is scientifically valid but unnecessarily restrictive — some tests use larger scale models (e.g., λ=2 for sub-millimeter bolts).

### 8.2 `PrototypeData` — Complete but Not Used by UI

`PrototypeData` is a comprehensive dataclass (25+ fields: geometry, material, loading, friction, surface). However, the GUI panels (`GeometricScalingPanel`) only expose 5 fields (d, p, L, F_p, f) — the remaining 20+ fields are never exposed to the user.

**Gap:** Material properties (E_b, σ_y, ρ), friction (μ_t, μ_b), and surface roughness (Rz) are all in `PrototypeData` but not in the GUI. The backend can compute richer scale effects if these were exposed.

### 8.3 `SimilitudeAnalysis` — Not Used by GUI

`SimilitudeAnalysis` (in `similitude.py`) is the richest analysis class. It computes Pi groups, scale effects, and combined corrections. However, **the GUI never instantiates `SimilitudeAnalysis`**. The GUI uses `create_scaled_loosening_model()` from `loosening_similitude.py` instead, which is a simpler, less complete analysis.

**Gap:** The full `SimilitudeAnalysis` with its 5 `ScaleEffect` types (roughness, friction, embedding, thread tolerance, stress concentration) and proper Buckingham-Π analysis is available but completely bypassed by the GUI.

### 8.4 `ScaleEffect` Classifications — Good but Hidden

5 `ScaleEffect` classmethod constructors:
- `surface_roughness()` — Rz/d ratio increase
- `friction_coefficient()` — contact pressure effect
- `embedding_loss()` — constant absolute embedding per interface
- `thread_form_tolerance()` — ISO tolerance grade effect
- `stress_concentration()` — Kt preservation (always negligible)

Each produces a severity classification (NEGLIGIBLE/LOW/MEDIUM/HIGH/CRITICAL). This rich information is computed but never displayed in the GUI — only summary correction factors are shown.

### 8.5 Loosening Curves — Placeholder Implementation

The Jiang two-stage model is hardcoded in `EnhancedSimilitudeTab._on_scaling_computed()` with fixed parameters (λ1=0.012, λ2=0.003, N_trans=200). These represent a "typical" loosening curve but have no connection to the actual analysis parameters.

**Gap:** The loosening curves should be generated by passing the scaled model parameters to the `CoupledLooseningAnalyzer` (from `numerical/coupled_loosening_analyzer.py`) and simulating the loosening rate at both prototype and model scales. This would produce scientifically meaningful comparison curves.

---

## 9. Proposed Workflow Redesign

### 9.1 Guided Two-Stage Workflow with Status Bar

Replace the opaque nested-tab structure with a guided workflow using a visible status progression:

```
┌────────────────────────────────────────────────────────────────────────┐
│ WORKFLOW STATUS BAR                                                     │
│ [1. Prototype ✔] → [2. Scale & Method ✔] → [3. Results ○] → [4. Transfer ○]│
└────────────────────────────────────────────────────────────────────────┘
```

Each step lights up as it's completed. Clicking a completed step navigates there.

### 9.2 Proposed Workflow Steps

**Step 1 — Prototype Configuration**
- Import from MSD Builder (one-click, reads AppState.model)
- Or enter manually: geometry, material, loading, friction, surface
- Validation: all required fields filled, no contradictions

**Step 2 — Scale & Method**
- Choose analysis type: Multi-Bolt Reduction, Geometric Scaling, or Both
- If Geometric: Choose λ, cycle scaling mode, bolt standard
- If Multi-Bolt: Choose n, bolt circle, loading pattern
- Preview: show immediate λ → M×× bolt size lookup

**Step 3 — Compute & Results**
- Single "Run Analysis" button (not hidden in sub-tab)
- Live progress indicator
- Left panel: Π-group table (updates after compute)
- Right panel: Scale effects table with severity color coding
- Center/bottom: Comparison plots

**Step 4 — Transfer & Export**
- "Apply to Solver" → sends frequency, preload, cycles to Solver tab
- "Transfer to MSD Builder" → sends scaled element parameters
- "Export Report" → sends to Reports tab AND optionally saves to file
- Quality badge prominently displayed

### 9.3 Proposed Alternative: QSplitter with Persistent Side Panel

Rather than a wizard, use a persistent 3-column layout similar to the MSD Builder:

```
┌──────────────────┬──────────────────────────┬─────────────────────────┐
│ LEFT (30%)       │ CENTER (40%)             │ RIGHT (30%)             │
│ QScrollArea      │                          │                         │
│                  │                          │                         │
│ ┌──────────────┐ │  ANALYSIS TYPE TABS      │  RESULTS PANEL          │
│ │ Prototype    │ │  ┌──────┬──────┐         │                         │
│ │ Parameters   │ │  │Multi │Scale │         │  Π-Groups Table         │
│ │              │ │  │Bolt  │ing   │         │  ────────────────        │
│ │ d, p, L, Fp  │ │  └──────┴──────┘         │  Scale Effects          │
│ │ f, μ_t, μ_b │ │                          │  (severity color)       │
│ │ E, σ_y, ρ   │ │  ┌─────────────────────┐ │  ────────────────        │
│ └──────────────┘ │  │ ACTIVE PANEL        │ │  Quality Badge          │
│                  │  │                     │ │  ────────────────        │
│ ┌──────────────┐ │  │ (params + results   │ │  Suggested Config       │
│ │ Scale Setup  │ │  │  in one view)       │ │  ────────────────        │
│ │              │ │  │                     │ │  Actions                │
│ │ λ: [0.25]    │ │  └─────────────────────┘ │  [Run ▶]               │
│ │ Mode: [...]  │ │                          │  [Send to Solver →]     │
│ │ Standard:[..] │  Comparison Plots       │  [Transfer to MSD →]    │
│ └──────────────┘ │  (matplotlib inline)    │  [Export Report ↓]      │
│                  │                          │                         │
│ [Import from     │                          │                         │
│  MSD Builder]    │                          │                         │
└──────────────────┴──────────────────────────┴─────────────────────────┘
```

**Pros:** Mirrors the MSD Builder layout that the team already uses.
**Cons:** Parameter inputs + results in same view means less space for each.

**RECOMMENDATION:** 3-column layout (Option B above). This:
1. Eliminates the deep tab nesting
2. Keeps parameters visible while viewing results
3. Follows established UX pattern from MSD Builder
4. Leaves comparison plots in the center where they're most visible

---

## 10. Proposed Layout Architecture

### 10.1 Revised `EnhancedSimilitudeTab._setup_ui()` Skeleton

```python
def _setup_ui(self):
    main_layout = QVBoxLayout(self)
    main_layout.setContentsMargins(8, 8, 8, 8)
    main_layout.setSpacing(8)

    # ─── Workflow status bar (new) ────────────────────────────────────
    self.status_bar = WorkflowStatusBar(steps=["Prototype", "Scale", "Results", "Transfer"])
    main_layout.addWidget(self.status_bar)

    # ─── 3-column splitter ────────────────────────────────────────────
    main_splitter = QSplitter(Qt.Orientation.Horizontal)
    main_splitter.setHandleWidth(6)
    main_splitter.setChildrenCollapsible(False)

    # LEFT: Prototype & Scale configuration (QScrollArea)
    left_scroll = QScrollArea()
    left_scroll.setWidgetResizable(True)
    left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    left_scroll.setMaximumWidth(360)
    left_scroll.setMinimumWidth(240)
    left_widget = self._create_left_panel()
    left_scroll.setWidget(left_widget)
    main_splitter.addWidget(left_scroll)

    # CENTER: Analysis type selector + active computation panel + plots
    center_widget = self._create_center_panel()
    main_splitter.addWidget(center_widget)

    # RIGHT: Results, Π-groups, quality, actions (QScrollArea)
    right_scroll = QScrollArea()
    right_scroll.setWidgetResizable(True)
    right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    right_scroll.setMaximumWidth(320)
    right_scroll.setMinimumWidth(200)
    right_widget = self._create_right_panel()
    right_scroll.setWidget(right_widget)
    main_splitter.addWidget(right_scroll)

    # Initial split: 28% / 42% / 30%
    main_splitter.setSizes([280, 420, 300])

    main_layout.addWidget(main_splitter, stretch=1)
```

### 10.2 Left Panel Content

```
LEFT PANEL
├── [Import from MSD Builder] button  ← one-click population
│
├── GroupBox: "Prototype Parameters"
│   ├── Bolt diameter (d_p)    QDoubleSpinBox
│   ├── Thread pitch (p_p)     QDoubleSpinBox
│   ├── Grip length (L_p)      QDoubleSpinBox
│   ├── Preload (F_p)          QDoubleSpinBox
│   ├── Test frequency (f_p)   QDoubleSpinBox
│   ├── μ_thread               QDoubleSpinBox  ← exposed from PrototypeData
│   ├── μ_bearing              QDoubleSpinBox  ← exposed from PrototypeData
│   └── Surface roughness (Rz) QDoubleSpinBox  ← exposed from PrototypeData
│
├── GroupBox: "Multi-Bolt Configuration"
│   ├── Number of bolts (n)    QSpinBox
│   ├── Bolt circle (BCD)      QDoubleSpinBox
│   └── Loading pattern        QComboBox
│
└── GroupBox: "Geometric Scale"
    ├── Scale factor λ         QDoubleSpinBox
    ├── [1:2] [1:4] [1:8] [1:10] quick presets
    ├── Bolt standard          QComboBox
    └── Cycle scaling mode     QComboBox
```

### 10.3 Center Panel Content

```
CENTER PANEL
├── Analysis type tabs (2 tabs, at top)
│   ├── "Multi-Bolt Reduction"
│   └── "Geometric Scaling"
│
├── [▶ Run Analysis]  ← PRIMARY ACTION (always visible, center/top)
│
├── Results table (Prototype | Scaled | Factor columns)
│
└── Comparison plots (PlotWidget, expands to fill remaining space)
```

### 10.4 Right Panel Content

```
RIGHT PANEL
├── Quality Badge (large, colored)
│   "EXCELLENT 96.3%"  or  "POOR 43.1%"
│
├── GroupBox: "Π-Group Match"
│   └── QTableWidget (Symbol | Value | Deviation | Status)
│       4 columns instead of 5
│
├── GroupBox: "Scale Effects"
│   ├── Friction:   C_mu = 1.08  [LOW ◐]
│   ├── Embedding:  C_e  = 1.25  [MEDIUM ◑]
│   ├── Pitch:      C_p  = 1.01  [NEGLIGIBLE ●]
│   └── Combined:   C    = 1.35  [MEDIUM ◑]
│
├── GroupBox: "Suggested Config"
│   ├── Bolt: M16
│   ├── Preload: 48 250 N
│   ├── Frequency: 100 Hz
│   └── Cycles: 5 000 → × λ = 20 000 prototype
│
└── GroupBox: "Actions"
    ├── [▶ Run Analysis]          (duplicated for convenience)
    ├── [→ Send to Solver]
    ├── [→ Transfer to Builder]
    ├── [↓ Export Report]
    └── [↓ Export JSON]
```

---

## 11. New Integration Signals

### 11.1 Signals to Add to `EnhancedSimilitudeTab`

```python
class EnhancedSimilitudeTab(QWidget):
    transfer_to_builder = pyqtSignal(dict)      # EXISTING (but broken)
    send_to_solver = pyqtSignal(dict)           # NEW: scaled params to solver
    analysis_completed = pyqtSignal(object)    # NEW: emits ScaledLooseningModel
    import_from_model_requested = pyqtSignal() # NEW: requests current model from AppState
```

### 11.2 Connections to Add in `BoltAnalysisStudio._setup_ui()`

```python
# Fix existing broken connection
self.similitude_tab.transfer_to_builder.connect(self._on_similitude_transfer)

# New connections
self.similitude_tab.send_to_solver.connect(self._on_similitude_send_to_solver)
self.similitude_tab.analysis_completed.connect(self._on_similitude_analysis_done)
self.similitude_tab.import_from_model_requested.connect(self._on_similitude_import_model)
```

### 11.3 New Handler: Import Current Model

```python
def _on_similitude_import_model(self):
    """Push current MSD model parameters to Similitude tab."""
    model = self.app_state.model
    if model is None:
        return

    params = {
        "bolt_diameter": getattr(model, "bolt_diameter", 16.0),
        "pitch": getattr(model, "pitch", 2.0),
        "mu_initial": getattr(model, "mu_initial", 0.12),
    }

    if hasattr(model, "global_loading") and model.global_loading:
        params["preload"] = model.global_loading.F_preload / 1000.0  # kN
        params["frequency"] = model.global_loading.frequency

    self.similitude_tab.populate_from_model(params)
```

### 11.4 New Handler: Send to Solver

```python
def _on_similitude_send_to_solver(self, scaled_params: dict):
    """Apply scaled model parameters to solver configuration."""
    self.solver_tab.update_loading_summary(scaled_params)
    self.tab_widget.setCurrentIndex(2)  # Switch to Solver
    self._on_status_message(
        f"Scaled model parameters applied to Solver: "
        f"f={scaled_params.get('frequency', 0):.1f} Hz, "
        f"F_p={scaled_params.get('F_preload', 0)/1000:.1f} kN"
    )
```

### 11.5 New Handler: Store Similitude Result

```python
def _on_similitude_analysis_done(self, result: object):
    """Store similitude result in AppState for Reports tab."""
    self.app_state.similitude_scaled_model = result
    # Mark Reports tab as stale so it regenerates
    if hasattr(self.reports_tab, 'mark_stale'):
        self.reports_tab.mark_stale()
```

---

## 12. Implementation Priority Matrix

### P0 — Bug Fixes (Must Fix Before Use)

| # | Issue | File | Fix |
|---|-------|------|-----|
| B1 | Tab index hardcoded 5 → should be 4 | `main_window.py:4336` | Change `5` to `4` |
| B2 | Transfer to Builder ignores `elements` | `main_window.py:4393` | Pass to `load_from_elements_dict()` |
| B3 | Fallback Compute button not connected | `main_window.py:1342` | Connect or disable |
| B4 | Pi Group default state shows fake ✓ | `similitude_tab.py:806` | Initialize with empty/placeholder rows |

### P1 — Critical Usability

| # | Feature | Impact | Effort |
|---|---------|--------|--------|
| U1 | Move Compute button to Parameters sub-tab (or always show) | High | Low |
| U2 | "Import from MSD Builder" one-click button | High | Medium |
| U3 | Quality badge visible at top level | High | Low |
| U4 | Disable export buttons until analysis run | Medium | Low |
| U5 | Fix `LooseningSimlitudeAnalysis` not being populated | High | Medium |
| U6 | Add "Send to Solver" button and handler | High | Medium |

### P2 — Layout & Responsiveness

| # | Feature | Impact | Effort |
|---|---------|--------|--------|
| L1 | Replace deep nested tabs with 3-column splitter | High | High |
| L2 | Add `QScrollArea` to parameter panels | Medium | Low |
| L3 | Workflow status bar widget | Medium | Medium |
| L4 | Fix sub-tab elide mode for narrow windows | Low | Low |
| L5 | Export bar: disable until first compute | Medium | Low |

### P3 — Integration

| # | Feature | Impact | Effort |
|---|---------|--------|--------|
| I1 | `AppState.similitude_scaled_model` field | High | Low |
| I2 | Reports tab includes similitude section | High | High |
| I3 | Overlay solver results on comparison plots | Medium | Medium |
| I4 | Expose full `PrototypeData` fields in GUI | Medium | Medium |
| I5 | Use `SimilitudeAnalysis` (full engine) in GUI | High | High |

### P4 — Scientific Accuracy

| # | Feature | Impact | Effort |
|---|---------|--------|--------|
| S1 | Replace hardcoded Jiang curves with real computation | High | High |
| S2 | Display scale effect breakdown (5 types) with severity | High | Medium |
| S3 | Allow λ > 1 for upscaling cases | Low | Low |
| S4 | Expose μ_t, μ_b, Rz fields in GUI | Medium | Low |

---

## 13. Code Snippets for Key Fixes

### 13.1 Fix BUG-01 — Tab Index

```python
# main_window.py:4336
# BEFORE:
similitude_tab_index = 5  # "6. Similitude" tab

# AFTER:
similitude_tab_index = 4  # "5. ⚖️ Similitude" tab (0-indexed)
```

### 13.2 Fix BUG-02 — Transfer Actually Uses Elements

```python
# main_window.py
def _on_similitude_transfer(self, elements: dict):
    """Handle transfer of model from similitude analysis to MSD Builder."""
    self._open_msd_builder()

    if elements and self.msd_builder_window:
        try:
            self.msd_builder_window.load_from_elements_dict(elements)
            self._on_status_message(
                f"Similitude model transferred to MSD Builder "
                f"({len(elements)} elements)"
            )
        except Exception as e:
            self._on_status_message(f"Transfer warning: {e}")
    else:
        self._on_status_message("Similitude tab opened (no elements to transfer)")
```

### 13.3 Fix BUG-04 — Pi Groups Initialize Empty

```python
# similitude_tab.py — PiGroupDisplayPanel._setup_ui()
# BEFORE: Initialize with hardcoded fake data
pi_data = [
    ("Π₁", "Slip Parameter", ..., "0.500", "✓"),
    ...
]

# AFTER: Initialize with placeholder state
self.pi_table.setRowCount(0)  # Empty until analysis runs
self.summary_label.setText("Run analysis to compute Π-groups")
self.summary_label.setStyleSheet(f"color: {Theme.OVERLAY};")
```

### 13.4 Fix BUG-06 — Compute Button Always Visible

```python
# In MultiBoltReductionPanel._setup_ui()
# Add compute button to the PARAMETERS sub-tab (sub-tab 0), not Results

compute_btn = QPushButton("▶ Compute Equivalent Single Bolt")
compute_btn.setObjectName("primary")
compute_btn.setMinimumHeight(40)
compute_btn.clicked.connect(self._compute_reduction)
params_layout.addWidget(compute_btn)  # In params_layout, not results_vlayout

# Also keep it in Results for discoverability, or replace with
# a status label: "Click Compute in Parameters to generate results"
```

### 13.5 New: Import from MSD Builder

```python
# In EnhancedSimilitudeTab or left panel
def populate_from_model(self, params: dict):
    """Populate parameter fields from MSD model data."""
    d = params.get("bolt_diameter", 16.0)
    p = params.get("pitch", 2.0)
    fp_kn = params.get("preload", 160.0)  # kN
    freq = params.get("frequency", 25.0)
    mu = params.get("mu_initial", 0.12)

    # Update GeometricScalingPanel
    self.scaling_panel.proto_diameter_spin.setValue(d)
    self.scaling_panel.proto_pitch_spin.setValue(p)
    self.scaling_panel.proto_preload_spin.setValue(fp_kn)
    self.scaling_panel.proto_freq_spin.setValue(freq)

    # Update MultiBoltReductionPanel
    self.multi_bolt_panel.diameter_spin.setValue(d)
    self.multi_bolt_panel.pitch_spin.setValue(p)
    self.multi_bolt_panel.preload_spin.setValue(fp_kn)
    self.multi_bolt_panel.mu_thread_spin.setValue(mu)
    self.multi_bolt_panel.mu_bearing_spin.setValue(mu)

    # Update scale preview
    self.scaling_panel._update_scale_preview()
```

### 13.6 Quality Badge Widget

```python
class SimilitudeQualityBadge(QFrame):
    """Large quality indicator badge for top of Similitude tab."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 4)

        self._icon = QLabel("⚖")
        self._icon.setStyleSheet("font-size: 24px;")
        self._label = QLabel("Similitude Not Yet Computed")
        self._label.setStyleSheet(f"color: {Theme.OVERLAY}; font-size: 12pt;")
        self._score = QLabel("")
        self._score.setStyleSheet("font-size: 14pt; font-weight: bold;")

        layout.addWidget(self._icon)
        layout.addWidget(self._label)
        layout.addStretch()
        layout.addWidget(self._score)

    def update(self, quality: float, label: str):
        thresholds = [
            (0.90, Theme.GREEN, "EXCELLENT"),
            (0.75, Theme.BLUE, "GOOD"),
            (0.60, Theme.YELLOW, "ACCEPTABLE"),
            (0.00, Theme.RED, "POOR"),
        ]
        color, text = Theme.OVERLAY, label
        for threshold, c, t in thresholds:
            if quality >= threshold:
                color, text = c, t
                break

        self._label.setText(text)
        self._label.setStyleSheet(f"color: {color}; font-size: 12pt; font-weight: bold;")
        self._score.setText(f"{quality*100:.1f}%")
        self._score.setStyleSheet(f"color: {color}; font-size: 14pt; font-weight: bold;")
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.MANTLE};
                border-bottom: 2px solid {color};
                border-radius: 4px;
            }}
        """)
```

---

## Summary of Key Findings

### Bugs That Must Be Fixed Before the Tab Is Usable

1. **BUG-01**: Tab navigation goes to Reports, not Similitude (index off by 1)
2. **BUG-02**: "Transfer to MSD Builder" opens Builder with old model, not scaled result
3. **BUG-04**: Pi-group table shows fake ✓ before any analysis
4. **BUG-05**: Fallback compute button does nothing (no `.connect()`)
5. **BUG-06**: Compute button hidden in sub-tab the user must navigate to find

### Highest-Impact Improvements

1. **Replace nested tabs with 3-column layout** — eliminates 3-level navigation depth
2. **"Import from MSD Builder" button** — eliminates manual parameter duplication
3. **"Send to Solver" connection** — closes the Similitude → Solver data gap
4. **Quality badge at top level** — provides instant status without drilling into sub-tabs
5. **Use full `SimilitudeAnalysis` engine** — the richer analysis class (`similitude.py`) is never called by the GUI, leaving most of the backend computation unused

### Integration Architecture (Required)

```
AppState                         (shared state)
    ├── model                    (MSD Builder → Similitude via "Import")
    ├── similitude_scaled_model  (NEW — Similitude → Reports, Results)
    └── analysis_results         (Results → Similitude overlay)

Tab signals
    Similitude.analysis_completed → AppState.similitude_scaled_model
    Similitude.send_to_solver    → SolverTab.update_loading_summary()
    Similitude.transfer_to_builder → MSDBuilderWindow.load_from_elements_dict()
    AppState.model_changed       → Similitude.populate_from_model() (optional auto-populate)
```

---

*Document prepared by Claude Code for internal reference — Bolt Analysis Studio v4.0*
*Date: 2026-02-18*
