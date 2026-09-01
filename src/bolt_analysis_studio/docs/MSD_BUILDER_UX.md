# MSD Builder — UI/UX Reference
## Bolt Analysis Studio v4.0

**Date:** 2026-02-19
**File:** `src/bolt_analysis_studio/gui/msd_builder.py`
**Scope:** Complete UI/UX reference for the MSD Model Builder (Tab 2).

---

## 1. Overview

The MSD Builder is a visual drag-and-drop schematic editor for constructing bolted joint models
as Mass-Spring-Damper (MSD) systems. It is a standalone PyQt6 window (`MSDBuilderWindow`) that
can be embedded inside the main 6-tab application or launched independently via:

```bash
python run_app.py --builder
```

The MSD Builder is the **single source of truth** for all model geometry, loading parameters,
friction coefficients, and contact definitions. The Solver Tab (Tab 3) and Matrix Viewer are
read-only consumers of the data exported from the Builder.

---

## 2. Window Layout

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ Toolbar: [Undo][Redo] | [Zoom+][Zoom-][Fit] | [New Preset ▼] | [Settings]      │
├──────────────┬──────────────────────────────────────────┬───────────────────────┤
│              │                                          │                       │
│  ELEMENT     │         SCHEMATIC VIEW                   │   PROPERTY INSPECTOR  │
│  PALETTE     │         (SchematicView)                  │   (PropertyInspector) │
│  (left)      │                                          │   (right)             │
│              │   20×20 grid with MSD elements           │                       │
│  ─ Wizard    │   Springs, masses, dampers               │   Tab 0: Element      │
│  ─ Presets   │   Color-coded by type                    │   Tab 1: Loading      │
│  ─ Validation│   Connected in series/parallel           │   Tab 2: Contact      │
│  ─ Bolt Elems│                                          │                       │
│  ─ Members   │                                          │   ─ Properties form   │
│  ─ Contacts  │                                          │   ─ Material selector │
│  ─ Boundary  │                                          │   ─ Loading spinboxes │
│              │                                          │   ─ Contact config    │
├──────────────┴──────────────────────────────────────────┴───────────────────────┤
│ Status bar: Elements: 7 │ Parallel groups: 2 │ DOF: 10 │ F₀: 50.0 kN │ ⬪ Valid │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Panel Toggle Shortcuts

| Shortcut   | Action                           |
|------------|----------------------------------|
| `Ctrl+[`   | Toggle Element Palette (left)    |
| `Ctrl+]`   | Toggle Property Inspector (right)|

---

## 3. Element Palette (Left Panel)

**Class:** `ElementPalette` (lines 4678–4843)

**Signals emitted:**

```python
element_selected = pyqtSignal(str)               # Element type key string
preset_requested = pyqtSignal(str)               # Preset name
wizard_requested = pyqtSignal()
validation_case_requested = pyqtSignal(str)
open_paper_requested = pyqtSignal()
```

### 3.1 Joint Configuration Wizard

At the top of the palette is a single blue "Configure Joint..." button. Clicking it opens the
`JointConfigWizard` dialog which walks the user through a multi-page wizard to configure:
- Joint type (single bolt, flanged, double-nut, Junker test)
- Bolt size and material
- Number of engaged threads
- Gasket or metal-to-metal interface
- Contact types to include

The wizard calls `MSDBuilderWindow._build_from_wizard()` upon completion.

### 3.2 Quick Presets

Three preset buttons immediately populate the schematic with a complete reference model:

| Button | Preset Key | Contents |
|--------|-----------|----------|
| "Single Bolt Joint" | `single_bolt` | HEAD + SHANK + THREAD + NUT + FLANGE×2, ThreadContact + BearingContact×2 |
| "Basic Flanged Joint" | `flanged_joint` | Full flanged joint with gasket, all contacts populated |
| "Junker Test Setup" | `junker_test` | Junker transverse vibration fixture with 14-DOF chain |

### 3.3 Validation Cases

A combo box exposes 9 pre-configured test cases from the calibration/validation plan:

| Case Label | Source | Conditions |
|------------|--------|-----------|
| Jiang Low | Jiang 2003 | M12×1.75, F₀=30 kN, f=12.5 Hz |
| Jiang High | Jiang 2003 | M12×1.75, F₀=45 kN, f=12.5 Hz |
| Junker Std | Junker 1969 | Standard Junker transverse vibration |
| Nassar Low | Nassar 2007 | M8, δ=0.3 mm, f=12.5 Hz |
| Nassar High | Nassar 2007 | M8, δ=0.5 mm, f=12.5 Hz |
| Yang High | Yang 2009 | High torque tightening |
| Yang Low | Yang 2009 | Low torque tightening |
| Severe | Combined | High δ, high f, low F₀ |
| Lu2024 | Lu 2024 | M8×1.25, 7 loading levels |

Buttons below the combo:
- **Load Case** → emits `validation_case_requested` → populates model + loading params
- **Paper** → emits `open_paper_requested` → opens associated literature PDF

### 3.4 Element Type Buttons

Elements are organized into 4 categories. Each button shows `{symbol} {name}`.

#### 🔩 Bolt Elements
| Button | Key | Symbol | Color |
|--------|-----|--------|-------|
| Bolt Head | `HEAD` | ⬡ | Blue |
| Shank | `SHANK` | ⬜ | Gray |
| Nut | `NUT` | ⬡ | Orange |
| Washer | `WASHER` | ○ | Yellow |

#### ⚙️ Member Elements
| Button | Key | Symbol | Color |
|--------|-----|--------|-------|
| Flange | `FLANGE` | ▬ | Cyan |
| Gasket | `GASKET` | ≈ | Purple |

#### 🔗 Contact Elements
| Button | Key | Symbol | Color |
|--------|-----|--------|-------|
| Bearing (Head) | `BEARING_HEAD` | ↕ | Green |
| Bearing (Nut) | `BEARING_NUT` | ↕ | Green |
| Flange-Flange | `FLANGE_FLANGE` | ⇔ | Red |
| Washer Contact | `WASHER_CONTACT` | ≡ | Green |
| Gasket Contact | `GASKET_CONTACT` | ~ | Green |
| Generic Contact | `GENERIC_CONTACT` | ✕ | Green |

#### ↕️ Boundary
| Button | Key | Symbol |
|--------|-----|--------|
| Ground | `GROUND` | ▼ |

---

## 4. Schematic View (Centre)

**Class:** `SchematicView` (lines 909–3326)

A `QGraphicsView` containing a 20×20 grid of cells where MSD elements are placed.

### 4.1 Grid Rendering

**Method:** `_draw_grid()` (lines 1056–1101)

The grid is drawn in the background layer (z-value = −10) using two line styles:

```python
pen_major = QPen(QColor(Theme.SURFACE1), 0.75, Qt.PenStyle.SolidLine)   # Every 5th line
pen_minor = QPen(QColor(Theme.SURFACE0), 0.5, Qt.PenStyle.DotLine)      # Between lines
```

Row numbers (series position) are labeled on the left; column numbers (parallel position) are labeled
along the top, in `Consolas 9pt` and `Consolas 8pt` respectively.

### 4.2 Element Placement

- Each element occupies one cell in the 20×20 grid.
- Elements can be dragged from the palette (click button → click grid cell to place).
- Elements can be re-positioned by dragging within the grid.
- Dropped elements snap to the nearest grid cell.
- Multiple elements in the same column → **parallel** configuration.
- Elements in adjacent rows → **series** configuration.

### 4.3 Signals

```python
element_selected = pyqtSignal(object)            # Single click → updates PropertyInspector
elements_multi_selected = pyqtSignal(list)       # Shift+click → multi-select for contacts
model_changed = pyqtSignal()                     # Any structural change
grid_position_changed = pyqtSignal(int, int, int) # (element_id, new_row, new_col)
context_delete_requested = pyqtSignal(int)       # Right-click Delete
context_duplicate_requested = pyqtSignal(int)    # Right-click Duplicate
context_apply_load_requested = pyqtSignal(int)   # Right-click Apply Load
context_recalculate_requested = pyqtSignal(int)  # Right-click Recalculate
context_expand_requested = pyqtSignal(int)       # NUT → expand to thread array
context_expand_contacts_requested = pyqtSignal(int) # THREAD → expand contact chain
```

### 4.4 Context Menus

**Right-click on empty canvas area:**

```
Add Element ►   HEAD | SHANK | NUT | WASHER | FLANGE | GASKET | GROUND
─────────────────────────────────────────────────────────
Fit to View
Select All
─────────────────────────────────────────────────────────
Clear Canvas…    (shows confirmation dialog before clearing)
```

**Right-click on an element:**

```
🔩 Bolt Head #3                      (header, disabled — shows element info)
─────────────────────────────────────
Edit Properties                       → selects element + switches to Element tab
Copy k, c, m                         → stores to SchematicView._clipboard_props
Paste k, c, m                        → (greyed if clipboard empty)
─────────────────────────────────────
Duplicate
Delete                                → context_delete_requested signal
─────────────────────────────────────
Apply Load/Constraint…               → context_apply_load_requested signal
Recalculate MSD                      → context_recalculate_requested signal

[NUT only]:  Expand Threads…         → context_expand_requested signal
[THREAD only]: Expand Thread Contacts… → context_expand_contacts_requested signal
[2 selected]: Define Contact…        → elements_multi_selected signal
```

### 4.5 Copy/Paste k, c, m Values

A class-level clipboard (`SchematicView._clipboard_props: Optional[dict] = None`) stores the
stiffness, damping, and mass values from the last "Copy k, c, m" operation.

**Copy** stores `{"k": msd.k, "c": msd.c, "m": msd.m}` — all in SI units (N/m, N·s/m, kg).

**Paste** writes those values to the target element's `msd` data and calls `update_display()`.

The clipboard is shared across all `SchematicView` instances in the application.

### 4.6 Keyboard Shortcuts (SchematicView / MSDBuilderWindow)

| Key | Action |
|-----|--------|
| `Escape` | Clear all selections |
| `Ctrl+A` | Select all elements |
| `Ctrl+D` | Duplicate selected element |
| `Ctrl+R` | Recalculate MSD for selected element |
| `Delete` | Delete selected element |

### 4.7 Toolbar Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Undo (QUndoStack) |
| `Ctrl+Y` | Redo (QUndoStack) |
| `Ctrl++` | Zoom in |
| `Ctrl+-` | Zoom out |
| `Ctrl+0` | Fit schematic to view |
| `F1` | Show help |

---

## 5. Element Graphics Item

**Class:** `ElementGraphicsItem` (lines 405–906)

Each element in the schematic is drawn as a `QGraphicsRectItem` with child text labels.

### 5.1 Visual Layout

```
┌──────────────────────────────────────────────┐
│ ⬡ Bolt Head                     ↓F₀  [80%] │  ← Type label + force arrows
│ k=15.2 MN/m                                  │  ← Stiffness label (Consolas 8pt)
│ #3                                            │  ← Element ID (Consolas 8pt, gray)
│                                               │
└──────────────────────────────────────────────┘
```

### 5.2 Color Scheme

Each element type has a defined `color` in `ELEMENT_VISUALS`. The cell background is drawn
with that color at **40% opacity**, and the border uses the full color at 2pt width.

This gives a soft, semi-transparent appearance that distinguishes types while keeping the grid
visible underneath.

### 5.3 Engineering Notation Helper

**Function:** `_fmt_eng(value: float, unit: str = "") -> str` (lines 103–117)

Formats numeric values with SI unit prefixes for compact display in element labels:

```python
_fmt_eng(15_200_000, "N/m")  →  "15.2 MN/m"
_fmt_eng(1_540, "N/m")       →  "1.54 kN/m"
_fmt_eng(0.0015, "kg")       →  "1.50e-03 kg"
_fmt_eng(0, "N/m")           →  "0 N/m"
```

**Thresholds:**
- `|value| >= 1e9` → GigaUnits (G prefix)
- `|value| >= 1e6` → MegaUnits (M prefix)
- `|value| >= 1e3` → KiloUnits (k prefix)
- `|value| >= 1` → standard notation
- `|value| < 1` → scientific notation (`e` format)

### 5.4 Force/Load Arrows

When loading parameters are set, visual force arrows appear on elements at the loading
application point:

- **Downward arrow (↓)** — axial preload
- **Sideways arrow (→)** — transverse force
- **Circular arrow (↻)** — torque
- **Temperature indicator (△T)** — thermal loading

Arrows are `ForceArrowItem` children of `ElementGraphicsItem`, positioned at `(width−12, 4)`.

---

## 6. Property Inspector (Right Panel)

**Class:** `PropertyInspector` (lines 3328–4676)

A scrollable three-tab panel on the right side of the Builder window.

### 6.1 Tab Structure

| Tab Index | Tab Name | Contents |
|-----------|----------|----------|
| **0** | Element | Grid position, MSD parameters, material, preload, thread geometry, contact groups, actions |
| **1** | Loading | Global loading configuration (single source of truth for all analysis params) |
| **2** | Contact | Contact interface properties, thread contact, bearing contact, gasket contact params |

### 6.2 Tab 0: Element Properties

When an element is selected on the schematic, Tab 0 shows its editable properties:

**Grid Position group:**
- Row spinbox, Column spinbox

**MSD Parameters group:**
- Stiffness k [N/m]: double spinbox, 0 → 1e12
- Damping c [N·s/m]: double spinbox, 0 → 1e9
- Mass m [kg]: double spinbox, 0 → 1e6

**Material group:**
- Young's modulus E [GPa]
- Yield strength Sy [MPa]
- Ultimate strength Su [MPa]
- Density ρ [kg/m³]
- Material combo (auto-fills from database when selected)

**Geometry group:**
- Diameter d [mm]
- Length L [mm]
- Pitch p [mm] (thread pitch, for NUT/THREAD/SHANK)

**Preload group:** (for FLANGE, GROUND elements)
- Preload flag checkbox
- Preload value override

**Actions group:**
- [Duplicate element], [Delete element], [Apply Load...], [Expand Threads...] buttons

**Signals emitted from Tab 0:**
```python
property_changed = pyqtSignal(int, str, object)     # (element_id, field_name, new_value)
delete_requested = pyqtSignal()
duplicate_requested = pyqtSignal()
type_change_requested = pyqtSignal(str)
apply_load_requested = pyqtSignal()
expand_threads_requested = pyqtSignal()
```

### 6.3 Tab 1: Global Loading (Single Source of Truth)

Tab 1 contains all loading and friction parameters. This is the only place in the application
where these parameters can be edited.

**Global Loading Configuration group:**

| Widget | Range | Default | Unit |
|--------|-------|---------|------|
| `load_type_combo` | Axial / Transverse / Combined / Torsional / Bending | Transverse | — |
| `preload_spin` | 0 → 1e9 | 50 000 | N |
| `loading_yield_pct_spin` | 0 → 100 | 70 | % of yield |
| `loading_Sy_spin` | 100 → 2000 | 640 | MPa |
| `transverse_force_spin` | 0 → 1e6 | 10 000 | N |
| `transverse_disp_spin` | 0 → 10 | 0.65 | mm |
| `frequency_spin` | 0.001 → 1000 | 12.5 | Hz |
| `integration_time_spin` | 0.01 → 100 000 | 160 | s |
| `cycles_label` | read-only display | N = 2000 cycles | — |
| `external_force_spin` | −1e9 → 1e9 | 0 | N |
| `torque_spin` | 0 → 1e6 | 0 | N·m |
| `delta_T_spin` | −500 → 500 | 0 | °C |

**Friction / Bolt group:**

| Widget | Range | Default | Unit |
|--------|-------|---------|------|
| `mu_initial_spin` | 0.01 → 0.50 | 0.12 | — |
| `lubricated_check` | True / False | True | — |
| `bolt_diameter_spin` | 4 → 100 | 16 | mm |
| `bolt_pitch_spin` | 0.5 → 10 | 2.0 | mm |

**Hidden backward-compatibility spinboxes** (not visible in UI):

```python
self.cycles_spin        # Synced from freq × integration_time; read by _run_analysis()
self.amplitude_spin     # Alias for transverse_force_spin
self.trans_disp_spin    # Alias for transverse_disp_spin
self.mu_initial_spin    # (also visible in friction group)
self.bolt_diameter_spin # (also visible in friction group)
self.pitch_spin         # (also visible in friction group)
```

These hidden spinboxes are written to by `SolverTab.update_loading_summary()` so that
`_run_analysis()` can read them without knowing about the MSD Builder structure.

**`blockSignals()` pattern:**
When `update_loading_summary()` sets hidden spinbox values in batch, it wraps all setValue
calls with `blockSignals(True)` / `blockSignals(False)` to prevent spurious
`_auto_calculate_timestep()` calls. One explicit `_auto_calculate_timestep()` is called
at the end of the batch update.

### 6.4 Cycles Auto-Calculation

When frequency or integration time changes, cycles is auto-computed:

```python
n_cycles = max(1, int(frequency_spin.value() × integration_time_spin.value()))
cycles_label.setText(f"N = {n_cycles:,} cycles")
```

The `cycles_spin` (hidden) is also updated for backward compatibility.

**Example:** 12.5 Hz × 160 s = 2 000 cycles.

### 6.5 Transverse Force ↔ Displacement Auto-Conversion

The inspector maintains bidirectional conversion between transverse force (N) and
transverse displacement (mm) using the joint transverse stiffness `_k_transverse`.

**Force → Displacement:**

```python
def _on_transverse_force_changed(self, value: float):
    if self._updating: return
    self._updating = True
    disp_m = value / self._k_transverse     # N / (N/m) = m
    self.transverse_disp_spin.setValue(disp_m * 1000)   # display in mm
    self._updating = False
    self.loading_changed.emit(self.get_loading_data())
```

**Displacement → Force:**

```python
def _on_transverse_disp_changed(self, value: float):
    if self._updating: return
    self._updating = True
    force = (value / 1000) * self._k_transverse  # mm→m then × k
    self.transverse_force_spin.setValue(force)
    self._updating = False
    self.loading_changed.emit(self.get_loading_data())
```

The `_updating` boolean flag prevents infinite signal recursion.

**Default value:** `_k_transverse = 1.54e7 N/m` (typical M16 flanged joint).

**Update from model:** When the MSD model changes, `_on_msd_builder_model_changed()` in
`main_window.py` extracts the joint transverse stiffness from the assembled [K] matrix and
calls `inspector.set_transverse_stiffness(k_trans)`.

### 6.6 Preload % Yield Calculation

When `loading_yield_pct_spin` or `loading_Sy_spin` changes, the preload is auto-computed if
the explicit `preload_spin` value is zero:

```python
# In set_loading_data() and _on_yield_pct_changed():
if F_preload == 0.0 and pct_yield > 0.0:
    A_s = _get_global_stress_area()   # π/4 × ((d2+d1)/2)²
    Sy = loading_Sy_spin.value()      # MPa
    F_preload = (pct / 100.0) * A_s * Sy * 1e6
    preload_spin.setValue(F_preload)
```

Where `A_s` is the ISO 262 stress area computed from bolt diameter and pitch.

### 6.7 `get_loading_data()` Method

Returns a complete dictionary snapshot of all loading and friction parameters:

```python
{
    "type": "Transverse",           # Load type string
    "F_preload": 50000.0,           # N
    "preload_percent_yield": 70.0,  # %
    "F_transverse": 10000.0,        # N
    "delta_amplitude": 0.65,        # mm (transverse displacement amplitude)
    "frequency": 12.5,              # Hz
    "n_cycles": 2000,               # Auto-computed: freq × integration_time
    "integration_time": 160.0,      # s
    "F_external": 0.0,              # N
    "T_applied": 0.0,               # N·m
    "delta_T": 0.0,                 # °C
    "mu_initial": 0.12,             # friction coefficient
    "lubricated": True,
    "bolt_diameter": 16.0,          # mm
    "pitch": 2.0,                   # mm
    "Sy": 640.0,                    # MPa (bolt yield strength)
}
```

### 6.8 `set_loading_data()` — Backward Compatibility

When loading a saved project (`.msd` file), `set_loading_data()` handles legacy formats:

```python
# Legacy: only n_cycles was stored (no integration_time)
if "integration_time" not in data and "n_cycles" in data:
    freq = frequency_spin.value()
    if freq > 0:
        integration_time = n_cycles / freq
        integration_time_spin.setValue(integration_time)
```

During loading, `self._updating = True` suppresses all intermediate `loading_changed` signals.
A single `loading_changed` is emitted at the end.

### 6.9 Tab 2: Contact Properties

Tab 2 shows contact-specific parameters when a contact element is selected or when
configuring the active contact at a joint interface.

**Contact Interface group:**
- Contact type combo (THREAD, BEARING_HEAD, BEARING_NUT, WASHER_FLANGE, FLANGE_FLANGE, FLANGE_GASKET, HEAD_FLANGE, NUT_FLANGE)
- Node i (combo: element at interface top)
- Node j (combo: element at interface bottom)
- Friction model combo (Coulomb, Stribeck, LuGre, Dahl, Iwan)
- μ_static, μ_kinetic inputs
- Wear model combo (None, Archard, Fretting, Energy-Based)
- Wear coefficient K input

**Thread Contact params:** (visible when THREAD type selected)
- n_engaged_threads spinbox
- Load distribution model (Equal, Linear, Power, Exponential, Yamamoto)
- Power β or Yamamoto γ input

**Bearing Contact params:** (visible when BEARING type selected)
- Inner radius r_i [mm]
- Outer radius r_o [mm]
- Effective radius r_eff = (r_i + r_o)/2

**Gasket Contact params:** (visible when FLANGE_GASKET selected)
- Gasket type (spiral wound, RTJ, sheet, Kammprofile)
- Stiffness model (LINEAR, NONLINEAR, VISCOELASTIC)
- Creep coefficient

---

## 7. Status Bar

**Method:** `_update_status()` (lines 8193–8228)

The status bar at the bottom of the MSD Builder window shows 5 live indicators:

```
Elements: 7 │ Parallel groups: 2 │ DOF: 10 │ F₀: 50.0 kN │ ⬪ Valid
```

| Field | Content | Update Trigger |
|-------|---------|----------------|
| `elements_label` | "Elements: {n}" | Any structural change |
| `parallel_label` | "Parallel groups: {n}" | Any structural change |
| `dof_label` | "DOF: {n}" | Model re-exported |
| `preload_label` | "F₀: {value} {N/kN/MN}" | Loading changed |
| `validation_label` | "⬪ {status}" | Model exported |

**Preload display logic:**
```python
if preload >= 1e6:   "F₀: {preload/1e6:.1f} MN"
elif preload >= 1e3: "F₀: {preload/1e3:.1f} kN"
elif preload > 0:    "F₀: {preload:.0f} N"
else:                "F₀: —"
```

**Validation indicator colors:**
```python
if n_elements == 0:  "⬪ Empty"   (Theme.OVERLAY — gray)
elif n_dof > 0:      "⬪ Valid"   (Theme.GREEN — green)
else:                "⬪ Error"   (Theme.RED — red)
```

---

## 8. Signal Flow — Loading Parameters

### 8.1 Edit Flow (User changes value)

```
PropertyInspector (Tab 1 spinboxes)
    ↓ valueChanged / currentTextChanged
_on_loading_param_changed()
    ↓ updates cycles_label, cycles_spin
    ↓ loading_changed.emit(get_loading_data())
         ↓
MSDBuilderWindow._on_loading_changed(data: dict)
    ↓ stores in self._cached_loading_data
    ↓ calls schematic.update_load_overlays(data)
    ↓ model_changed.emit({"source": "loading", "loading_data": data})
         ↓
BoltAnalysisStudio._on_msd_builder_model_changed(data: dict)
    ↓ calls msd_builder_window.export_to_msd_model()
    ↓ calls app_state.set_msd_model(model)
    ↓ calls solver_tab.update_loading_summary(model)
    ↓ updates k_transverse from assembled [K]
    ↓ refreshes matrix_viewer if open
```

### 8.2 Load Flow (Opening saved project)

```
BoltAnalysisStudio._open_project()
    ↓ reads .msd JSON
    ↓ calls MSDModel.from_dict(data)
         ↓
MSDBuilderWindow.load_from_msd_model(model)
    ↓ clears schematic
    ↓ adds elements from model.elements
    ↓ calls inspector.set_loading_data(loading_dict)
    ↓ caches loading data
    ↓ calls schematic.update_load_overlays()
    ↓ emits model_changed
         ↓
(same as edit flow from here)
```

### 8.3 Transverse Force ↔ Displacement Sync

```
transverse_force_spin.valueChanged
    → _on_transverse_force_changed(value)
        → _updating = True
        → transverse_disp_spin.setValue(value / k_transverse * 1000)
        → _updating = False
        → loading_changed.emit(...)

transverse_disp_spin.valueChanged
    → _on_transverse_disp_changed(value)
        → _updating = True
        → transverse_force_spin.setValue(value / 1000 * k_transverse)
        → _updating = False
        → loading_changed.emit(...)
```

The `_updating` flag is checked at the top of each handler to break the circular dependency.

---

## 9. `export_to_msd_model()` — GUI → Core Coupling

**Method:** `MSDBuilderWindow.export_to_msd_model()` (lines 7889–7941)

This is the critical bridge from the visual schematic to the numerical model.

**Steps:**

1. Call `self.schematic.export_to_model()` → returns base `MSDModel` with elements
2. Get loading data: `data = self._cached_loading_data or self.inspector.get_loading_data()`
3. Map type string → `LoadingType` enum:
   ```python
   type_map = {
       "Axial": LoadingType.AXIAL,
       "Transverse": LoadingType.TRANSVERSE,
       "Combined": LoadingType.COMBINED,
       "Torsional": LoadingType.TORSIONAL,
       "Bending": LoadingType.BENDING,
   }
   ```
4. Set `model.global_loading.*` fields from data dict
5. Set `model.mu_initial`, `model.lubricated`, `model.bolt_diameter`, `model.pitch`
6. Auto-compute preload if `F_preload == 0` but `% yield > 0`
7. Export contacts from `schematic.get_contacts()` → append to `model.contacts`
8. Return completed `MSDModel`

**After export**, `main_window.py` calls `model.assemble_matrices()` to get `(M, K, C)` and
extracts the transverse stiffness from `K` to update `inspector._k_transverse`.

---

## 10. `load_from_msd_model()` — Core → GUI Coupling

**Method:** `MSDBuilderWindow.load_from_msd_model(model: MSDModel)` (lines 7943–8092)

Reconstructs the visual schematic from a saved `MSDModel`.

**Steps:**

1. `self.schematic.clear_all()` — removes all elements and connections
2. For each element in `model.elements`:
   - Get grid position from `elem_data.grid_position` (row, col)
   - Add element via `schematic.add_element(type, row, col)`
   - Copy MSD properties: `item.element_data.msd.k/c/m`
   - Copy geometry: `diameter`, `length`, `pitch`
   - Copy material: `E`, `Sy`, `Su`, `rho`
   - Copy thread fillet model if present
   - Call `item.update_display()` to refresh labels and arrows
3. Build loading dict from `model.global_loading` fields
4. Call `inspector.set_loading_data(loading_dict)` to populate Tab 1
5. Cache: `self._cached_loading_data = inspector.get_loading_data()`
6. `schematic.update_load_overlays(loading_data)` — refreshes force arrows
7. Emit `model_changed` to notify downstream consumers

**Error handling:**
- Each element is wrapped in try/except; failures are counted and reported
- A warning dialog shows successful/failed element counts if any failures occur
- A critical error dialog is shown if the entire model load fails

---

## 11. Planned UX Improvements (Future Phases)

### Phase 2: Element Palette Reorganization (CLAUDE.md §4.1)

Add categorized sections with icons:

```
📦 COMPONENTS   → HEAD, SHANK, NUT, WASHER, FLANGE, GASKET
🔗 CONTACTS     → ThreadContact, BearingContact, Interface
⚡ LOADS & BCs  → PreloadArrow, ExternalForce, Transverse, Torque, DispBC
📐 PRESETS      → SingleBolt, FlangedJoint, JunkerTest, MultiPattern
```

### Phase 2: Load and BC Visual Elements (CLAUDE.md §4.2)

New `ElementType` values for visual-only force indicators:

| Element | Symbol | Links to |
|---------|--------|---------|
| `FORCE_AXIAL` | ↓F | `global_loading.F_external` |
| `FORCE_TRANSVERSE` | →F | `global_loading.F_transverse` |
| `TORQUE` | ↻T | `global_loading.T_applied` |
| `FIXED_BC` | ▼ | GROUND element |
| `DISP_BC` | ⇔δ | Prescribed displacement |

These auto-update their displayed value when loading parameters change.

### Phase 3: Drag-and-Drop Improvements (CLAUDE.md §4.3)

- Smart snapping: elements snap to valid connection points
- Connection preview: dotted line while dragging
- Auto-routing: springs auto-route around elements
- Quick-connect: double-click to auto-connect to chain
- Alignment guides

### Phase 4: Property Inspector Enhancements (CLAUDE.md §4.4)

- Quick-edit mode: Tab key cycles through fields
- Unit conversion toggle: N/kN/lbf, mm/m/in
- Calculator popup: built-in k = E×A/L formula
- Copy/paste properties between elements
- Batch edit: same property across multiple selected elements
- History dropdown: recent values per field

### Phase 5: Undo/Redo for Loading Changes (CLAUDE.md §6.4)

Extend the existing `QUndoStack` to cover loading parameter changes using the Command pattern:

```python
class SetLoadingParamCommand(QUndoCommand):
    def __init__(self, inspector, field, old_value, new_value):
        ...
    def redo(self):
        inspector.set_field(field, new_value)
    def undo(self):
        inspector.set_field(field, old_value)
```

---

## 12. Key Implementation Files

| File | Class | Purpose |
|------|-------|---------|
| `gui/msd_builder.py` | `MSDBuilderWindow` | Main builder window, export/load |
| `gui/msd_builder.py` | `SchematicView` | Grid canvas, drag-drop, signals |
| `gui/msd_builder.py` | `PropertyInspector` | 3-tab property editor |
| `gui/msd_builder.py` | `ElementPalette` | Element/preset/validation buttons |
| `gui/msd_builder.py` | `ElementGraphicsItem` | Visual cell representation |
| `gui/msd_builder.py` | `_fmt_eng()` | SI prefix formatting helper |
| `gui/main_window.py` | `BoltAnalysisStudio` | Handles `model_changed` signal |
| `core/models/model.py` | `MSDModel` | Core data model with matrix assembly |

---

*See also: ARCHITECTURE.md (data flow), API_REFERENCE.md (class APIs), COUPLING_AUDIT.md (all signal connections)*
