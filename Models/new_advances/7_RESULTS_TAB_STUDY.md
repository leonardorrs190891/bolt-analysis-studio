# Results Tab (Tab 4) - Functional & UX Study

## Bolt Analysis Studio v4.0 - LTAD/UFU - Petrobras R&D

**Date**: 2026-02-18
**Scope**: Complete audit of the Results Tab (Tab 4) layout, data flow, plot architecture, dashboard, export, and improvement recommendations.

---

## 1. Current State Analysis

### 1.1 Layout Hierarchy

```
ResultsTab (QWidget)
├── Header (QHBoxLayout)
│   ├── Title: "Analysis Results"
│   ├── [Export Data] button
│   └── [Dashboard] button (primary)
│
└── Main Splitter (QSplitter, Horizontal, 200:600)
    ├── Left: Results Tree (QTreeWidget)
    │   └── 5 categories, 17 plot items
    │
    └── Right: Results Display
        └── Vertical Splitter (80:500)
            ├── Summary Statistics (QGroupBox, QGridLayout)
            │   ├── Max Displacement  |  Max Velocity
            │   ├── Final Preload     |  Preload Loss
            │   └── Min Safety Factor |  Fundamental Freq
            │
            └── Plot View (QGroupBox)
                ├── Toolbar (QHBoxLayout)
                │   ├── [Open in Editor] button (primary)
                │   ├── [Quick Export] button
                │   ├── [Refresh] button
                │   └── Current plot label (italic)
                │
                └── QStackedWidget
                    ├── Index 0: Placeholder label (dashed border)
                    └── Index 1: PlotWidget (MplCanvas + NavigationToolbar)
```

### 1.2 Results Tree Structure (17 Plot Items)

| Category | Plot Items | Data Source |
|----------|-----------|-------------|
| **Time History** | Displacement, Velocity, Acceleration, Preload vs Time | `time_result` (TimeIntegrationResult) |
| **Preload Decay** | Clamped Force Decay, Preload Loss Models, Stage Analysis | `coupled_loosening_result` / `preload_result` |
| **Friction & Wear** | Friction Evolution, Wear Accumulation, Friction-Wear Correlation | `coupled_loosening_result` |
| **Loosening** | Loosening Rate, Torque Balance, Torque Margin, Cumulative Angle | `coupled_loosening_result` |
| **Joint Forces** | Joint Forces Diagram, Contact Forces, Phase Diagram | `coupled_loosening_result` |

### 1.3 Key Metrics

- **6 KPI statistics labels** in the Summary Statistics panel
- **17 selectable plot items** across 5 categories
- **9-panel embedded dashboard** (3x3 GridSpec)
- **PlotEditorWindow** with 40+ customization controls (separate window)
- **3 export formats**: PNG, PDF, SVG (+ CSV for data)

---

## 2. Bugs Found

### Bug 1: Statistics Not Cleared on New Analysis (MODERATE)

**Location**: `main_window.py:4288` (`_on_results_changed`)

**Problem**: When a new analysis runs and certain result types are missing (e.g., no `time_result`), the statistics labels retain stale values from the previous run. There is no reset-to-defaults before populating.

```python
# Current: only overwrites stats that have data
def _on_results_changed(self, results):
    if results:
        if results.preload_result:
            stats["Final Preload"].setText(...)  # Updated
        # But if results.preload_result is None, the old value persists!
```

**Fix**: Add a reset step at the beginning:
```python
def _on_results_changed(self, results):
    # Reset all stats to defaults first
    for label in self.results_tab.stats_labels.values():
        label.setText("--")
    if results:
        ...
```

### Bug 2: Dashboard Overwrites Single Plot with No Return (MODERATE)

**Location**: `main_window.py:3631` (`_show_embedded_dashboard`)

**Problem**: Clicking "Dashboard" calls `fig.clear()` on the PlotWidget's canvas figure and draws 9 subplots on it. After this, clicking a tree item replaces the dashboard with a single plot (expected). But:
1. There is no "Back to Dashboard" button to return
2. The `canvas.axes` reference (single axes) is invalidated after `fig.clear()` creates 9 new axes via `fig.add_subplot()`. Subsequent single-plot rendering uses `canvas.axes` which is now stale.

**Impact**: After viewing the dashboard and then clicking a tree item, the first click may render on the wrong axes or silently fail.

### Bug 3: Preload vs Time Uses Hardcoded Frequency (LOW)

**Location**: `main_window.py:2846`

```python
frequency = 25.0  # Default frequency
time = cl.cycles / frequency
```

The "Preload vs Time" plot converts cycles to seconds using a hardcoded 25 Hz, ignoring the actual analysis frequency from `model.global_loading.frequency`. This produces incorrect time axes.

### Bug 4: Joint Forces Diagram Is a Placeholder (LOW)

**Location**: `main_window.py:2713` (`_plot_joint_forces`)

The "Joint Forces Diagram" uses a hardcoded list of components (`['Bolt Head', 'Washer', 'Flange 1', 'Gasket', 'Flange 2', 'Washer', 'Nut']`) that doesn't reflect the actual model. It plots the same force value for every component (initial preload / final preload), which is physically incorrect -- different components carry different forces depending on the load path.

### Bug 5: Contact Forces Plot Shows Identical Lines (LOW)

**Location**: `main_window.py:2745` (`_plot_contact_forces`)

Thread Contact, Bearing Contact, and Flange Contact all plot `preload / 1000` -- three identical overlapping lines. This is a placeholder that provides no useful information.

### Bug 6: `_show_comprehensive_dashboard` Creates + Closes Figure Immediately (MINOR)

**Location**: `main_window.py:3344-3629`

`_show_comprehensive_dashboard()` creates a separate `plt.figure()`, draws 9 plots, calls `plt.close(fig)`, then calls `_show_embedded_dashboard()` which redraws everything. The separate figure is never displayed -- it's created and destroyed pointlessly.

### Bug 7: `_plot_with_settings` Incomplete Dispatch (MODERATE)

**Location**: `main_window.py:3286-3342`

`_plot_with_settings()` handles only 5 of the 17 plot types (Clamped Force Decay, Friction Evolution, Wear Accumulation, Loosening Rate, Torque Margin). The other 12 types fall through with no plot drawn. The "Refresh" button calls this method, so refresh is broken for most plots.

```python
# Line 3321: After Torque Margin, nothing else is handled
# Add other plot types...  ← comment says it all
```

---

## 3. Data Flow Analysis

### 3.1 Results Pipeline

```
SolverWorker (QThread)
    │
    │  5 sequential analyses:
    │  1. Modal Analysis → natural_frequencies, mode_shapes
    │  2. Static Analysis → static_displacement, safety_factor
    │  3. Preload Loss → PreloadAnalysisResult
    │  4. Coupled Loosening → CoupledLooseningResult
    │  5. Time Integration → TimeIntegrationResult
    │
    ▼
_on_solver_finished(result: AnalysisResult)
    │
    ├── app_state.results = result
    ├── _on_results_changed(result)  → Updates 6 statistics labels
    └── Switch to Tab 4, show placeholder
        │
        ▼
User clicks tree item
    │
    ▼
_on_result_category_selected(item, column)
    │
    ├── String-match routing: "Clamped Force Decay" in text → dispatch
    ├── Show plot_stack index 1 (PlotWidget)
    └── Call appropriate plot method
```

### 3.2 Plot Rendering Pathways (Inconsistent)

The codebase uses **three different rendering patterns**, which is confusing:

| Pattern | Used By | How It Renders |
|---------|---------|----------------|
| **PlotManager static methods** | Displacement, Velocity, Acceleration, Preload Loss Models | `PlotManager.plot_*(widget, data)` -- clean API |
| **`_plot_coupled_loosening()` multiplex** | Clamped Force Decay, Friction, Wear, Loosening Rate, Torque Margin | Single method with `plot_type` string switch |
| **Individual `_plot_*()` methods** | Torque Balance, Cumulative Angle, Joint Forces, Contact Forces, Friction-Wear Correlation, Phase Diagram, Preload vs Time | Direct canvas manipulation in main_window.py |

**Problem**: Maintenance nightmare. Plot code is scattered between `plot_manager.py` (reusable) and `main_window.py` (one-off methods). 11 of 17 plot types are implemented as custom methods in `main_window.py` (600+ lines).

### 3.3 Plot Dispatch Routing (Fragile)

**Location**: `_on_result_category_selected()` uses substring matching:

```python
if "Clamped Force Decay" in text:    # OK, unique
elif "Preload Loss Models" in text:   # OK, unique
elif "Stage Analysis" in text:        # OK, unique
elif "Friction Evolution" in text:    # OK
elif text == "Displacement":          # Exact match (different style!)
elif text == "Velocity":              # Exact match
```

**Issues**:
- Mix of `"X" in text` (substring) and `text == "X"` (exact match)
- No fallback/error for unrecognized text -- silently does nothing
- Adding/renaming plot items requires changes in both the tree definition AND the dispatch chain

---

## 4. Dashboard Analysis

### 4.1 Architecture

Two dashboard implementations exist:

| Implementation | Location | Status |
|---|---|---|
| `_show_comprehensive_dashboard()` | Line 3344 | **Dead code** - creates figure, closes it immediately, delegates to embedded |
| `_show_embedded_dashboard()` | Line 3631 | **Active** - 3x3 GridSpec on the existing PlotWidget canvas |

### 4.2 Dashboard Layout (3x3)

```
┌───────────────────┬────────────────────┬──────────────────┐
│ 1. Clamped Force  │ 2. Coupled Preload │ 3. Wear          │
│    Decay          │    & Friction      │    Accumulation   │
├───────────────────┼────────────────────┼──────────────────┤
│ 4. LOOSENING RATE │ 5. Torque Balance  │ 6. Torque Margin │
│    (highlighted)  │                    │                  │
├───────────────────┼────────────────────┼──────────────────┤
│ 7. Friction vs    │ 8. Joint Forces    │ 9. Cumulative    │
│    Wear           │    Diagram         │    Loosening     │
└───────────────────┴────────────────────┴──────────────────┘
```

### 4.3 Dashboard Issues

1. **Axes invalidation**: `fig.clear()` destroys `canvas.axes` (the original single axes). After dashboard, `canvas.axes` references a stale object. Single-plot methods that use `canvas.axes` may break.

2. **tight_layout silently fails**:
   ```python
   try:
       fig.tight_layout(pad=1.5)
   except Exception:
       pass  # tight_layout can fail on complex GridSpec layouts
   ```
   When it fails, subplot titles/labels overlap, producing unreadable plots.

3. **No way back**: After switching from dashboard to single plot (by clicking tree), no "Dashboard" indicator shows which plot is selected. The tree selection and dashboard are conceptually in conflict -- the tree implies "show one", the dashboard shows all nine.

4. **Missing plots from tree**: The dashboard shows 9 plots, but the tree has 17 items. Dashboard doesn't include: Displacement, Velocity, Acceleration, Preload vs Time, Preload Loss Models, Stage Analysis, Contact Forces, Phase Diagram.

---

## 5. PlotEditorWindow Analysis

### 5.1 Capabilities

The `PlotEditorWindow` (plot_manager.py:614) opens a plot in a separate window with:

| Group | Controls |
|-------|----------|
| **Labels & Title** | Title, X Label, Y Label (QLineEdit) |
| **Line Style** | Width (0.5-10), Style (solid/dashed/dotted/dash-dot), Marker (7 types), Marker Size |
| **Font Settings** | Title font (8-24), Label font (6-20), Tick font (6-16) |
| **Display Options** | Grid toggle + alpha, Legend toggle + position (8 locations) |
| **Axis Limits** | Auto/Manual toggle, X min/max, Y min/max, Apply button |
| **Export** | DPI selector (72-600), PNG/PDF/SVG/CSV buttons |

### 5.2 PlotEditorWindow Issues

1. **Figure reference copy, not live link**: `_copy_figure()` copies line data from the source figure. It only copies `get_lines()`, so scatter plots, fill_between patches, bar charts, colorbars, twin axes, and annotations are all **lost**.

2. **Data cache limited**: Only line data is cached for CSV export. Scatter plots, bar charts, and other non-line artists have no export path.

3. **Global line style changes**: Changing line width/style/markers applies to **all** lines simultaneously. No per-line editing.

4. **No undo**: Changes in the editor are immediate and irreversible.

---

## 6. Statistics Panel Analysis

### 6.1 Current KPIs (6 labels)

| KPI | Source | Color | Issue |
|-----|--------|-------|-------|
| Max Displacement | `time_result.max_displacement` | BLUE | Overwritten by coupled loosening to show `total_loosening_deg` in degrees |
| Max Velocity | `time_result.max_velocity` | BLUE | Only from time integration |
| Final Preload | `preload_result` or `coupled_loosening_result` | GREEN | Two different sources, different units (% vs kN) |
| Preload Loss | `preload_result.preload_loss_percent` | YELLOW | |
| Min Safety Factor | `coupled_loosening_result.torque_margin` min | RED | Not actually safety factor per VDI 2230 |
| Fundamental Freq | `natural_frequencies[0]` | MAUVE | OK |

### 6.2 Statistics Issues

1. **"Max Displacement" is overloaded**: `_update_coupled_loosening_stats()` (line 3135) overwrites "Max Displacement" with `total_loosening_deg` displayed as degrees. The label says "Max Displacement" but shows loosening angle.

2. **"Min Safety Factor" is mislabeled**: It shows the minimum torque margin (T_resistance/T_pitch), not the actual VDI 2230 safety factor. These are different concepts.

3. **"Final Preload" inconsistent units**: From `preload_result` it shows as percentage (e.g., "85.0%"), from `coupled_loosening_result` it shows as kN (e.g., "42.50 kN"). The label doesn't change.

4. **Missing KPIs**: No statistics for:
   - Loosening onset cycle
   - Max loosening rate
   - Phase at end of analysis
   - Total wear depth
   - Cycles to 50% preload loss

---

## 7. Export Functionality Analysis

### 7.1 Export Pathways

| Export Method | Trigger | Format | Data |
|---|---|---|---|
| `_export_plot("png")` | Quick Export button | PNG/PDF/SVG | Current figure image |
| `_export_plot_data_csv()` | Within `_export_results` | CSV | Coupled loosening columns only |
| PlotEditor export | Editor window buttons | PNG/PDF/SVG/CSV | Copied line data only |
| `_export_results()` | Export Data button | CSV | Delegates to `ProjectIO.export_results_csv()` |

### 7.2 Export Issues

1. **"Export Data" button** connects to `_export_results()` which uses `ProjectIO.export_results_csv()`. This is fine but **only exports coupled loosening data**. Time history (displacement/velocity/acceleration), preload loss models, and modal results are not included.

2. **Quick Export** saves PNG of whatever is currently displayed, including the placeholder label if no plot is selected. Should disable when no plot is showing.

3. **No batch export**: Cannot export all 17 plots at once (e.g., to a folder).

---

## 8. Improvement Recommendations

### 8.1 CRITICAL: Fix Axes Invalidation After Dashboard

**Problem**: `_show_embedded_dashboard()` calls `fig.clear()` which destroys `canvas.axes`. All subsequent single-plot renders access the stale reference.

**Solution**: After `fig.clear()` for dashboard, restore `canvas.axes` when switching back to single plot mode:

```python
def _render_single_plot(self):
    """Prepare canvas for a single plot after dashboard or fresh."""
    canvas = self.results_tab.plot_widget.canvas
    fig = canvas.figure
    fig.clear()
    canvas.axes = fig.add_subplot(111)
    canvas._apply_theme()
```

Call this at the start of every single-plot render, OR at the start of `_on_result_category_selected()`.

### 8.2 CRITICAL: Complete `_plot_with_settings` Dispatch

Add the missing 12 plot types to `_plot_with_settings()` so the Refresh button works for all plots. Alternatively, refactor to reuse `_on_result_category_selected()` logic:

```python
def _refresh_current_plot(self):
    if self.results_tab.current_plot_type and self.app_state.results:
        # Create a fake tree item to reuse the dispatch logic
        for i in range(self.results_tab.results_tree.topLevelItemCount()):
            cat = self.results_tab.results_tree.topLevelItem(i)
            for j in range(cat.childCount()):
                child = cat.child(j)
                if child.text(0) == self.results_tab.current_plot_type:
                    self._on_result_category_selected(child, 0)
                    return
```

### 8.3 HIGH: Unify Plot Rendering Architecture

Move all 17 plot implementations into `PlotManager` or a new `ResultsPlotter` class. Each plot type becomes a static method. The dispatch table becomes a simple dict:

```python
PLOT_DISPATCH = {
    "Displacement": ("time_result", PlotManager.plot_displacement),
    "Velocity": ("time_result", PlotManager.plot_velocity),
    "Clamped Force Decay": ("coupled_loosening", ResultsPlotter.plot_clamped_force_decay),
    "Torque Balance": ("coupled_loosening", ResultsPlotter.plot_torque_balance),
    # ... all 17
}
```

**Benefits**: Eliminates 600+ lines from `main_window.py`. Makes plot functions reusable for reports and batch export. Centralizes plot styling.

### 8.4 HIGH: Fix Statistics Panel

1. **Reset before update**: Clear all stats to "--" before populating with new results
2. **Fix label overloading**: Rename "Max Displacement" to something context-aware, or add separate "Total Loosening Angle" stat
3. **Fix "Min Safety Factor"**: Rename to "Min Torque Margin" or compute actual VDI 2230 safety factor
4. **Consistent units**: Always show preload in kN (or make it configurable)
5. **Add missing KPIs**: Loosening onset cycle, max rate, phase, total wear

**Proposed expanded statistics layout** (3 columns x 4 rows):

```
┌──────────────────────────────────────────────────────────────────────┐
│ Final Preload: 42.5 kN    │ Preload Loss: 15.0%   │ Onset: Cycle 450│
│ Loosening Angle: 0.124°   │ Max Rate: 0.0005°/cyc │ Phase: Stable   │
│ Total Wear: 8.3 um        │ Min Torque Margin: 1.8│ Fund. Freq: 125 Hz│
│ Max Displacement: 1.2e-4 m│ Max Velocity: 0.05 m/s│ Safety Factor: 2.1│
└──────────────────────────────────────────────────────────────────────┘
```

### 8.5 HIGH: Improve Dashboard Architecture

1. **Restore axes after dashboard**: When user clicks a tree item, reset figure to single-axes mode first
2. **Add "Dashboard" pseudo-item to tree**: Add a top-level item "9-Panel Dashboard" at the top of the tree. This makes it part of the tree navigation instead of a separate button
3. **Remove dead code**: Delete `_show_comprehensive_dashboard()` entirely
4. **Handle tight_layout failure gracefully**: Use `constrained_layout=True` instead, or use explicit subplot positioning

### 8.6 MEDIUM: Improve Tree Interaction

1. **Disable unavailable plots**: Grey out plot items that have no data. Check `results.time_result is None` to grey out Time History items, etc.

```python
def _update_tree_availability(self, results):
    """Grey out tree items that have no data."""
    has_time = results.time_result is not None
    has_coupled = results.coupled_loosening_result is not None
    has_preload = results.preload_result is not None

    # Time History category
    for i in range(time_cat.childCount()):
        child = time_cat.child(i)
        child.setDisabled(not has_time)
```

2. **Show plot thumbnail on hover**: Use tooltip with a miniature version of the plot
3. **Bold the currently selected item**: Visual indicator of which plot is shown
4. **Double-click to open in editor**: Instead of requiring the toolbar button

### 8.7 MEDIUM: Fix Real Data in Placeholder Plots

**Joint Forces Diagram**: Should read actual elements from the model and display the force through each one, not a hardcoded list. When the model has 5 elements, show 5 bars.

**Contact Forces**: Should differentiate between thread contact, bearing contact, and flange contact forces using the actual contact model data, not plot identical lines.

**Preload vs Time**: Read frequency from `model.global_loading.frequency` instead of hardcoded 25 Hz.

### 8.8 MEDIUM: PlotEditorWindow Improvements

1. **Copy all artists**: Extend `_copy_figure()` to handle scatter plots, fill_between patches, bar charts, colorbars, and text annotations
2. **Per-line editing**: Add a line selector dropdown. User picks which line to modify
3. **Add comparison mode**: Allow loading a second dataset (e.g., validation case) onto the same plot
4. **Add annotation tool**: Let user add text, arrows, and markers to the plot

### 8.9 LOW: Batch Export

Add a "Export All Plots" button that:
1. Creates a folder (user-selected)
2. Renders all 17 plots sequentially
3. Saves each as PNG (300 DPI) with descriptive filename
4. Optionally generates a summary HTML page with all plots embedded

### 8.10 LOW: Plot Right-Click Context Menu

Add right-click on the plot area:
- Copy to clipboard
- Save as PNG/PDF/SVG
- Open in Editor
- Reset zoom
- Toggle grid
- Toggle legend

---

## 9. Visual Design Improvements

### 9.1 Summary Statistics Panel

**Current**: Plain QGridLayout with colored labels, no visual hierarchy.

**Proposed**:
- Use card-style stat widgets (rounded, slightly elevated background)
- Color-code the value with a small icon indicator (arrow up/down for trends)
- Add a small sparkline (mini inline chart) showing the trend
- Collapse to a single summary row when maximizing the plot

### 9.2 Results Tree

**Current**: QTreeWidget with emoji prefixes, always expanded, no visual feedback.

**Proposed**:
- Replace emoji with small colored dots indicating data availability (green = has data, grey = no data)
- Add item count badge on each category ("Time History (4)")
- Highlight the currently displayed plot item with a colored left border
- Add icons for each plot type (line chart, bar chart, scatter, etc.)

### 9.3 Plot Area

**Current**: PlotWidget with NavigationToolbar (matplotlib default toolbar styling).

**Proposed**:
- Replace matplotlib NavigationToolbar with custom Qt toolbar matching the application theme
- Add "Zoom to fit" button alongside existing toolbar
- Add plot title banner above the plot area (outside matplotlib) for consistent typography
- Show a subtle watermark "BAS v4.0 - LTAD/UFU" in exported plots

### 9.4 Dashboard View

**Current**: 3x3 GridSpec crammed into the PlotWidget canvas. Small fonts, overlapping labels.

**Proposed**:
- Use Qt's QGridLayout with individual PlotWidgets per cell instead of matplotlib GridSpec
- Each cell has a small title bar with the plot name and a "maximize" button
- Clicking a cell maximizes it to full view (replacing the tree-click interaction)
- Better font sizing (auto-scale based on cell size)

---

## 10. Implementation Priority

### Tier 1: Bug Fixes (Do First)

| # | Fix | Lines | Effort |
|---|-----|-------|--------|
| 1 | Reset statistics on new analysis | ~5 lines in `_on_results_changed` | 15 min |
| 2 | Restore `canvas.axes` after dashboard | ~10 lines | 30 min |
| 3 | Complete `_plot_with_settings` dispatch | ~40 lines | 30 min |
| 4 | Fix Preload vs Time hardcoded frequency | 1 line | 5 min |
| 5 | Delete dead `_show_comprehensive_dashboard` code | Delete ~280 lines | 10 min |

### Tier 2: Data Correctness (High Impact)

| # | Improvement | Effort |
|---|-------------|--------|
| 6 | Fix statistics labels (overloaded, mislabeled) | 1 hour |
| 7 | Implement real Joint Forces from model data | 2 hours |
| 8 | Implement real Contact Forces differentiation | 2 hours |
| 9 | Disable unavailable tree items (grey out) | 1 hour |

### Tier 3: Architecture (Reduces Tech Debt)

| # | Improvement | Effort |
|---|-------------|--------|
| 10 | Move 11 plot methods from main_window.py to PlotManager | 4 hours |
| 11 | Replace string dispatch with enum/dict dispatch table | 2 hours |
| 12 | Expand statistics panel (12 KPIs) | 2 hours |

### Tier 4: UX Polish (Nice to Have)

| # | Improvement | Effort |
|---|-------------|--------|
| 13 | Right-click context menu on plot | 2 hours |
| 14 | Batch export all plots | 3 hours |
| 15 | PlotEditor: support scatter/bar/fill artists | 4 hours |
| 16 | Qt-based dashboard (individual widgets per cell) | 8 hours |
| 17 | Per-line editing in PlotEditor | 3 hours |

---

## 11. Code Metrics

| Metric | Value |
|--------|-------|
| `ResultsTab._setup_ui()` lines | ~215 (line 958-1163) |
| Plot methods in `main_window.py` | ~560 lines (2480-3029 + specialized methods) |
| Dashboard code in `main_window.py` | ~510 lines (3149-3854, including dead code) |
| `PlotManager` static methods | 9 methods (~370 lines) |
| `PlotEditorWindow` | ~540 lines |
| Total Results-related code | ~2,200 lines spread across 2 files |

### Code Distribution Issue

~1,120 lines of plot-rendering code live in `main_window.py` instead of `plot_manager.py`. This makes `main_window.py` the largest file in the project (~4,800 lines) and makes plot functions non-reusable for the Reports Tab.

**Recommendation**: Move all plot rendering to `plot_manager.py` (or a new `results_plotter.py`). `main_window.py` should only contain dispatch logic and UI wiring (~50 lines total for results).

---

## Appendix A: Plot Type Reference

| # | Tree Item | Method | File | Axes Type |
|---|-----------|--------|------|-----------|
| 1 | Displacement | `PlotManager.plot_displacement()` | plot_manager.py | Line |
| 2 | Velocity | `PlotManager.plot_velocity()` | plot_manager.py | Line |
| 3 | Acceleration | `PlotManager.plot_acceleration()` | plot_manager.py | Line |
| 4 | Preload vs Time | `_plot_preload_vs_time()` | main_window.py | Line |
| 5 | Clamped Force Decay | `_plot_coupled_loosening("preload")` | main_window.py | Line + thresholds |
| 6 | Preload Loss Models | `PlotManager.plot_preload_loss()` | plot_manager.py | Multi-line |
| 7 | Stage Analysis | `_plot_phase_diagram()` | main_window.py | Regions + twin axis |
| 8 | Friction Evolution | `_plot_coupled_loosening("friction")` | main_window.py | Multi-line + threshold |
| 9 | Wear Accumulation | `_plot_coupled_loosening("wear")` | main_window.py | Line + fill |
| 10 | Friction-Wear Correlation | `_plot_friction_wear_correlation()` | main_window.py | Scatter + fit |
| 11 | Loosening Rate | `_plot_coupled_loosening("loosening")` | main_window.py | Line + fill |
| 12 | Torque Balance | `_plot_torque_balance()` | main_window.py | Multi-line + fill_between |
| 13 | Torque Margin | `_plot_coupled_loosening("torque")` | main_window.py | Line + fill_between |
| 14 | Cumulative Angle | `_plot_cumulative_angle()` | main_window.py | Line + fill + phase regions |
| 15 | Joint Forces Diagram | `_plot_joint_forces()` | main_window.py | Horizontal bar |
| 16 | Contact Forces | `_plot_contact_forces()` | main_window.py | Multi-line (identical) |
| 17 | Phase Diagram | `_plot_phase_diagram()` | main_window.py | Regions + twin axis |

## Appendix B: Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                        SolverWorker (QThread)                        │
│                                                                      │
│  1. Modal Analysis ──────► natural_frequencies: List[float]          │
│                            mode_shapes: np.ndarray                   │
│                                                                      │
│  2. Static Analysis ─────► static_displacement: np.ndarray           │
│                            safety_factor: float                      │
│                                                                      │
│  3. Preload Loss ────────► PreloadAnalysisResult                     │
│     (4 decay models)       ├── cycles: np.ndarray                    │
│                            ├── results: Dict[str, ndarray]           │
│                            └── final_preload_ratio: float            │
│                                                                      │
│  4. Coupled Loosening ───► CoupledLooseningResult                    │
│     (per-cycle sim)        ├── cycles, preload_ratio, mu_thread      │
│                            ├── mu_bearing, total_wear_um             │
│                            ├── loosening_angle_deg, loosening_rate    │
│                            ├── torque_margin, friction_margin        │
│                            ├── states: List[LooseningState]          │
│                            └── summary: final_ratio, phase, mu_crit  │
│                                                                      │
│  5. Time Integration ────► TimeIntegrationResult                     │
│     (Newmark-beta etc.)    ├── time, displacement, velocity, accel   │
│                            └── max_displacement, max_velocity        │
│                                                                      │
│  All wrapped in: AnalysisResult                                      │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼ finished signal
                ┌───────────────────────────────┐
                │   _on_solver_finished()        │
                │   ├── app_state.results = ...  │
                │   ├── _on_results_changed()    │───► Stats labels (6 KPIs)
                │   └── Switch to Tab 4          │
                └───────────────┬───────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   User clicks tree     │
                    │   item or Dashboard    │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  _on_result_category_  │
                    │  selected() dispatch   │───► PlotWidget.canvas renders
                    │  (string matching)     │     single matplotlib figure
                    └────────────────────────┘
```
