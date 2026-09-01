# Improvement Analysis: MSD Builder GUI

## Overview

This document analyzes the MSD Builder (`gui/msd_builder.py`, ~4210 lines) for bugs, missing features, UX issues, and architectural gaps. Findings are compared against the intended architecture described in `CLAUDE.md`.

---

## CRITICAL — Bugs and Architectural Violations

### CB1. Loading Configuration Missing from PropertyInspector
**Location**: PropertyInspector class (lines 2362–3107)
**Reference**: CLAUDE.md "Loading and Friction Configuration Architecture" section

Per the documented architecture, the PropertyInspector in the MSD Builder should be the **single source of truth** for all loading and friction parameters:
- Preload F₀, % Yield, Transverse Force/Displacement, Frequency, Cycles
- External Force, Torque, ΔT Temperature
- Initial μ, Lubricated flag, Bolt Diameter, Pitch
- `loading_changed` signal → propagates to Solver Tab

**None of this exists in the current code.** The PropertyInspector only shows element-level mechanical properties (k, c, m, material). There is no loading section, no friction section, no `loading_changed` signal, and no connection to the Solver Tab.

**Impact**: The entire data flow architecture (MSD Builder → MSDModel.global_loading → Solver Tab → Analysis) is broken. Loading parameters have no GUI entry point in the MSD Builder.

---

### CB2. Export/Import Does Not Save Contacts
**Location**: `export_to_model()` (lines ~1068–1078), `load_from_msd_model()` (lines ~4092–4191)

Contacts are stored in `schematic.contacts` dictionary but the export function only serializes elements. When a model is saved and reloaded:
- All ThreadContacts are lost
- All BearingContacts are lost
- All GasketContacts are lost
- All contact friction/wear parameters are lost

The user must re-create every contact manually after loading a saved project.

**Impact**: Contact system cannot persist across sessions — defeats the purpose of building contacts in the MSD Builder.

---

### CB3. Export/Import Does Not Save Element Loads
**Location**: LoadDialog stores loads in `elem_data.applied_loads` and `elem_data.constraints` (lines ~3882–3883)

These fields are set by the LoadDialog but never included in the model export. Loads configured per-element are silently discarded on save.

**Impact**: Any per-element load configuration is lost on save/load cycle.

---

### CB4. FlangeJointWizard Ignores Bolt Size and Material
**Location**: `_build_from_wizard()` (lines ~3981–4086)

The wizard lets the user select:
- Bolt size (M8–M64)
- Bolt grade (8.8, 10.9, 12.9, A193 B7, etc.)
- Gasket type (spiral wound, RTJ, sheet, Kammprofile)

But `_build_from_wizard()` creates elements with **default properties only**. The selected bolt size, material grade, and gasket type are never applied to the generated elements. Generated elements have generic stiffness/mass values unrelated to the wizard configuration.

Additionally, contact elements are created as placeholders, but no actual `ContactInterface` objects are added to the model's contact system.

**Impact**: The wizard creates a visually correct structure but with meaningless mechanical properties. The user must manually edit every element afterward, defeating the purpose of the wizard.

---

### CB5. Thread Model Variable Unused
**Location**: `_build_from_wizard()` (line ~4045)

```python
model = ThreadFilletModel(n_fillets=n_fillets)
factors = model.get_load_factors()
k_base = elem.element_data.msd.k
```

The `factors` variable is computed but never applied to the first thread element. It's only used in the loop for subsequent threads. The first thread element gets the unmodified default stiffness.

**Impact**: First thread in distributed model has wrong stiffness when using wizard presets.

---

## HIGH — Significant Feature Gaps

### HB1. No Drag-and-Drop from Palette to Schematic
**Location**: ElementPalette (lines 3113–3222), SchematicView (lines 494–1079)

The palette only supports click-to-add. The user clicks a button in the palette, then clicks a grid cell in the schematic. There is no drag-and-drop, which is the standard interaction for visual editors.

Missing interactions:
- No drag preview showing element shape during drag
- No connection point highlighting during drag
- No auto-insert into chain at drop position
- No keyboard shortcut for rapid element addition

---

### HB2. No Smart Connection Snapping
**Location**: SchematicView connection generation (lines ~868–963)

Connection lines are generated automatically based on grid adjacency (row-to-row). The algorithm uses "closest column" to determine which elements connect, but this is naive and doesn't consider:
- Logical flow direction
- Valid connection types (bolt head should connect to washer, not directly to gasket)
- User-specified connection overrides
- Connection point previews during element placement

There is no way for the user to manually create, modify, or delete connections.

---

### HB3. PropertyInspector Lacks Organized Navigation
**Location**: PropertyInspector (lines 2362–3107)

All property groups (MSD, Material, Geometry, Thread, Tribological, Thread Contact, Bearing, Gasket, Loading, etc.) are stacked vertically in a single scroll area. For complex elements with many properties, this requires excessive scrolling.

Missing features:
- No tabbed interface to organize properties by category
- No search/filter for properties
- No keyboard navigation (Tab to next field)
- No collapsible section memory (sections don't remember open/closed state)

---

### HB4. No Undo/Redo Support
**Location**: Entire MSD Builder

No undo/redo system exists for any operation:
- Element addition/deletion
- Property changes
- Contact creation/modification
- Wizard operations
- Load configuration changes

A single accidental deletion or wrong value entry has no recovery path.

---

### HB5. No Unit Conversion System
**Location**: PropertyInspector spin boxes

All values are in fixed SI units (MPa, mm, N/m, kg). There is no way to:
- Toggle between SI and Imperial units
- Display values in engineering-friendly units (kN vs N, GPa vs MPa)
- Auto-convert when switching unit systems
- Show unit labels next to spin boxes

For Petrobras engineers working with inch-series bolts (A193 B7, UNC threads), this is a significant workflow friction.

---

### HB6. Material Database Hardcoded
**Location**: PropertyInspector material presets (lines ~2868–2877)

Material properties for presets are hardcoded in the Python source rather than loaded from the materials database (`databases/materials_database.py` or `databases/materials.json`). This means:
- Adding new materials requires code changes
- Material database updates don't propagate to the MSD Builder
- Inconsistency between database and builder presets is possible

---

### HB7. No Bidirectional Sync with Solver Tab
**Location**: MSDBuilderWindow ↔ BoltAnalysisStudio

Per CLAUDE.md architecture:
```
MSD Builder → model_changed signal → main_window → solver_tab.update_loading_summary()
```

This signal chain is partially implemented but:
- Changes in MSD Builder don't fully propagate to Solver Tab
- No `loading_changed` signal exists (see CB1)
- Solver Tab has no "Edit in MSD Builder" button that navigates back
- No visual indication of sync status

---

## MEDIUM — UX and Methodology Improvements

### MB1. ElementGraphicsItem Has No Context Menu
**Location**: ElementGraphicsItem (lines 132–250)

Elements in the schematic have no right-click context menu. Standard actions that should be available:
- Edit Properties
- Apply Load/BC
- Duplicate Element
- Delete Element
- Add Contact To...
- Show in Inspector
- Copy/Paste Properties

Currently the only interaction is click-to-select and drag-to-move.

---

### MB2. No Hover Tooltips on Elements
**Location**: ElementGraphicsItem (lines 132–250)

Hovering over an element shows no information. A tooltip should display:
- Element type and name
- Key properties (k, m, c, material)
- Contact connections
- Applied loads
- Validation status

---

### MB3. ContactIndicator Too Small and Non-Interactive
**Location**: ContactIndicator (lines 380–438)

Contact indicators are 16-pixel circles — difficult to click, especially at normal zoom. They have a tooltip but no click-to-edit functionality. Double-clicking a contact indicator should open the ContactDialog for that contact.

---

### MB4. No Visual Load/Boundary Condition Elements
**Reference**: CLAUDE.md Phase 4.2

Loads and boundary conditions should be visual elements in the schematic:
- Preload Arrow (↓F₀) showing application point and magnitude
- External Force Arrow (↓F_ext) with direction
- Transverse Force Arrow (→F_trans) for Junker loading
- Fixed BC symbol (▼) for ground constraints
- Displacement BC symbol (⇔δ) for prescribed displacement
- Torque symbol (↻T) for applied torque

Currently loads are only configurable through the LoadDialog and have no visual representation.

---

### MB5. Schematic Has No Annotation Capability
**Reference**: CLAUDE.md Phase 4.5

No way to add:
- Free-form text labels
- Dimension lines showing distances
- Force magnitude arrows
- Section markers dividing the model into regions
- Notes attached to elements

For documentation and report generation, annotated schematics are essential.

---

### MB6. LoadDialog is Disconnected from Analysis
**Location**: LoadDialog (lines 1656–1937)

The LoadDialog applies loads to individual elements (`elem.applied_loads`), but:
- These loads are never used by the time integration solvers
- They're not included in model export (see CB3)
- They conflict with the global loading architecture (CLAUDE.md)
- Direction options (X/Y/Z) are meaningless for a 1D MSD model
- Time variation parameters (frequency, phase) duplicate Solver Tab settings

The dialog exists but produces no effect on any analysis.

---

### MB7. FlangeJointWizard Has No Graphical Preview
**Location**: FlangeJointWizard (lines 1943–2356)

The wizard shows a text-based preview of the structure it will generate:
```
HEAD → WASHER → FLANGE → GASKET → FLANGE → WASHER → NUT
```

This should be a graphical schematic preview showing the actual element layout with approximate proportions and contact locations.

---

### MB8. No Multi-Element Selection
**Location**: SchematicView (lines 494–1079)

Only single-element selection is supported. Missing:
- Shift+click to add to selection
- Ctrl+click to toggle selection
- Rubber-band (box) selection
- Select All (Ctrl+A)
- Group drag (move multiple elements together)
- Group property edit (batch modify shared properties)

---

### MB9. Grid System Has Fixed Limits
**Location**: SchematicView (lines ~617–618)

The grid is hardcoded to 20×20 cells. For large models (e.g., per-thread distributed model with 10+ threads), this limit is too restrictive. The grid should expand dynamically based on model size.

---

### MB10. No Element Duplication
**Location**: SchematicView element operations

There is no way to duplicate an element with all its properties. The user must:
1. Add a new element from the palette
2. Manually copy every property from the source element

A "Duplicate" action (Ctrl+D or context menu) would save significant time for repetitive structures.

---

### MB11. Recalculate All Blocks the UI
**Location**: `_recalculate_all()` (lines ~3423–3560)

The recalculation iterates over all elements and updates their properties. For large models, this can take several seconds during which the UI is frozen. This should use a QThread to keep the UI responsive with a progress indicator.

---

### MB12. No Keyboard Shortcuts for Common Actions
**Location**: MSDBuilderWindow (lines 3228–4204)

Missing keyboard shortcuts:
- Ctrl+Z / Ctrl+Y: Undo/Redo
- Ctrl+D: Duplicate element
- Delete: Delete selected element
- Ctrl+A: Select all
- Ctrl+G: Toggle grid
- Ctrl+R: Recalculate all
- F5: Run analysis
- Ctrl+Shift+V: Validate model

---

## LOW — Refinements

### LB1. ElementPalette Button Lambda Capture
**Location**: Lines ~3161, 3174, 3187, 3201

```python
for elem_type in [...]:
    btn.clicked.connect(lambda checked, t=elem_type: self._add_element(t))
```

The lambda capture pattern is correct (using default argument `t=elem_type`), but the element list is hardcoded rather than generated from `ELEMENT_VISUALS`. Adding a new element type requires editing multiple code locations.

---

### LB2. Connection Line Has No Labels
**Location**: ConnectionLine (lines 252–378)

Connection lines show no information about what they represent. Should optionally show:
- Stiffness value on spring connections
- Contact type label on contact connections
- Force flow magnitude during analysis

---

### LB3. No Element Visual State Indicators
**Location**: ElementGraphicsItem visual rendering

Elements have no visual indicators for:
- Has contact attached (should show [C] badge)
- Has load applied (should show [L] badge)
- Has validation error (should show [!] badge with red border)
- Properties auto-calculated vs manual (should show * indicator)
- Part of a parallel group (should have visual grouping)

---

### LB4. Thread Fillet Panel Not Integrated with Thread Properties
**Location**: ThreadFilletPanel (lines ~1390–1655), PropertyInspector thread section

The ThreadFilletPanel appears in the PropertyInspector for thread elements but:
- Its parameters don't auto-populate from the bolt size
- Distribution model selection doesn't affect the displayed stiffness
- No visualization of thread load distribution curve
- No connection to ThreadContact parameters

---

### LB5. No Color Coding for Element Types
**Location**: ELEMENT_VISUALS dict (lines ~66–92)

Each element type has a color defined in `ElementVisual.color`, but the color scheme could be improved:
- Similar colors for functionally different elements
- No legend showing what colors mean
- No user-customizable color scheme

---

### LB6. No Print/Export of Schematic
**Location**: SchematicView

The schematic view cannot be exported as an image (PNG, SVG) or printed. For reports and documentation, the MSD schematic should be exportable in standard image formats.

---

### LB7. No Model Statistics Panel
**Location**: MSDBuilderWindow

Should show a persistent summary panel or status bar with:
- Number of elements by type
- Number of contacts
- Total DOFs
- Estimated system natural frequency
- Memory usage
- Validation status (green/yellow/red indicator)

---

### LB8. Material Preset Dropdown Not Sorted
**Location**: PropertyInspector material combo (lines ~2868–2877)

Material presets are in arbitrary order. Should be sorted by:
- Most common first (e.g., A193 B7, 8.8, 10.9)
- Then by grade/strength
- Grouped by standard (ASTM, ISO, API)

---

## Architecture Gap: CLAUDE.md vs Implementation

### What CLAUDE.md Describes (Phase 4):

| Feature | Status | Notes |
|---|---|---|
| Categorized palette with icons | ❌ Missing | Flat button list |
| Load/BC visual elements | ❌ Missing | No visual loads |
| Drag-drop from palette | ❌ Missing | Click-only |
| Smart connection snapping | ❌ Missing | Auto-connect by adjacency |
| Connection preview during drag | ❌ Missing | No drag feedback |
| Auto-routing around elements | ❌ Missing | Straight lines only |
| Group selection | ❌ Missing | Single-select only |
| Alignment guides | ❌ Missing | Grid-only alignment |
| Quick-edit mode | ❌ Missing | Standard spin boxes |
| Unit conversion | ❌ Missing | Fixed SI units |
| Calculator popups | ❌ Missing | Manual entry only |
| Copy/paste properties | ❌ Missing | No clipboard |
| Batch edit | ❌ Missing | Single-element only |
| Property history | ❌ Missing | No undo/redo |
| Text annotations | ❌ Missing | No annotation layer |
| Dimension lines | ❌ Missing | No measurements |
| Force arrows | ❌ Missing | Text labels only |
| Section markers | ❌ Missing | No sectioning |
| Notes | ❌ Missing | No notes |

### What CLAUDE.md Describes (Loading Architecture):

| Feature | Status | Notes |
|---|---|---|
| Loading section in PropertyInspector | ❌ Missing | No loading UI |
| `loading_changed` signal | ❌ Missing | No signal |
| Transverse force ↔ displacement auto-convert | ❌ Missing | No conversion |
| k_transverse coupling | ❌ Missing | No stiffness link |
| Preload % yield calculation | ❌ Missing | No yield calc |
| Thread geometry auto-population | ❌ Missing | No auto-fill |
| Friction model selector | ❌ Missing | No model choice |
| Single source of truth for analysis params | ❌ Missing | Params scattered |

---

## Prioritized Improvement Roadmap

| Priority | ID | Description | Effort | Impact |
|---|---|---|---|---|
| **1** | CB1 | Add loading configuration to PropertyInspector | HIGH | Enables entire data flow architecture |
| **2** | CB2+CB3 | Fix export/import to include contacts and loads | MEDIUM | Enables persistent models |
| **3** | CB4 | Fix wizard to apply bolt size and material | LOW | Usable wizard presets |
| **4** | HB4 | Add undo/redo system | HIGH | Essential for usability |
| **5** | HB1 | Implement drag-drop from palette | MEDIUM | Standard interaction pattern |
| **6** | HB2 | Add smart connection snapping | MEDIUM | Correct model topology |
| **7** | HB3 | Reorganize PropertyInspector with tabs | MEDIUM | Reduced scrolling |
| **8** | HB6 | Load material database from JSON | LOW | Consistent data |
| **9** | MB1+MB2 | Add context menus and tooltips | LOW | Discoverability |
| **10** | MB4 | Add visual load/BC elements | MEDIUM | Visual completeness |
| **11** | MB6 | Integrate or deprecate LoadDialog | MEDIUM | Remove dead code |
| **12** | MB7 | Add graphical wizard preview | MEDIUM | Better wizard UX |
| **13** | MB8 | Add multi-element selection | MEDIUM | Batch operations |
| **14** | HB5 | Add unit conversion system | MEDIUM | Imperial bolt support |
| **15** | LB6 | Add schematic export (PNG/SVG) | LOW | Report integration |
