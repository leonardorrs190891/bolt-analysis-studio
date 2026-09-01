# MSD Builder UX & Layout Design Study

**Bolt Analysis Studio v4.0** - Tab 2 & MSD Builder Window
**Date:** 2026-02-18
**Purpose:** Comprehensive UI/UX improvement recommendations for a cleaner, more responsive, less polluted design while maintaining scientific rigour.

---

## Table of Contents

1. [Current State Analysis](#1-current-state-analysis)
2. [Layout Architecture Improvements](#2-layout-architecture-improvements)
3. [Toolbar Redesign](#3-toolbar-redesign)
4. [Element Palette Declutter](#4-element-palette-declutter)
5. [Property Inspector Reorganization](#5-property-inspector-reorganization)
6. [Schematic Canvas Improvements](#6-schematic-canvas-improvements)
7. [Context Menu Enhancement (Right-Click)](#7-context-menu-enhancement-right-click)
8. [Left-Click Interaction Improvements](#8-left-click-interaction-improvements)
9. [Visual Design & Theme Refinement](#9-visual-design--theme-refinement)
10. [Grid & Element Graphics](#10-grid--element-graphics)
11. [Responsive Design & Breakpoints](#11-responsive-design--breakpoints)
12. [Graph & Visualization Improvements](#12-graph--visualization-improvements)
13. [Keyboard Shortcuts & Accessibility](#13-keyboard-shortcuts--accessibility)
14. [Implementation Priority](#14-implementation-priority)

---

## 1. Current State Analysis

### 1.1 Current Layout (3-Panel Horizontal Splitter)

```
+--------------------------------------------------------------------+
| TOOLBAR (17 actions, densely packed, text-only labels)              |
+----------+-----------------------------------+---------------------+
|          |                                   |                     |
| PALETTE  |    SCHEMATIC VIEW                 |   PROPERTY          |
| (15%)    |    (55%)                          |   INSPECTOR (30%)   |
| 150-280px|    QGraphicsView                  |   240-400px         |
|          |                                   |                     |
| 7 groups |    120x80px grid                  |   14 QGroupBox      |
| 20 btns  |    Grid snapping                  |   sections          |
| + wizard |    Drag-drop elements             |   ~60 input fields  |
| + presets|                                   |                     |
| + cases  |                                   |                     |
+----------+-----------------------------------+---------------------+
| STATUS: Elements: 0  |  Parallel groups: 0  |  DOF: 0             |
+--------------------------------------------------------------------+
```

### 1.2 Current Problems Identified

| # | Problem | Severity | Area |
|---|---------|----------|------|
| 1 | **Toolbar too dense** - 17 actions with text labels fight for space | HIGH | Toolbar |
| 2 | **Palette too tall** - 7 groups + 20 buttons require excessive scrolling | HIGH | Palette |
| 3 | **Inspector overloaded** - 14 property groups shown simultaneously | HIGH | Inspector |
| 4 | **No visual hierarchy** - All buttons/groups look the same weight | MEDIUM | All panels |
| 5 | **Context menu too sparse** - Only 5 actions on right-click | MEDIUM | Schematic |
| 6 | **No breadcrumb/state indicator** - User doesn't know model completion status | MEDIUM | General |
| 7 | **Series/Parallel buttons always disabled** - Confusing when no selection | LOW | Toolbar |
| 8 | **Status bar underutilized** - Only shows element count, 3 numbers | LOW | Status |
| 9 | **No minimap** - Large models lose spatial context when zoomed | LOW | Schematic |
| 10 | **Validation Cases section too prominent** - Takes 30% of palette height | MEDIUM | Palette |

### 1.3 Current Theme Colors (Catppuccin Mocha)

The existing Catppuccin color system is well-designed. The semantic color mapping is good:
- **BLUE (#89b4fa)**: Bolt components, primary accent
- **GREEN (#a6e3a1)**: Nut, success states, preload
- **RED (#f38ba8)**: Bearing contacts, errors
- **YELLOW (#f9e2af)**: Thread, caution, selection
- **TEAL (#94e2d5)**: Flange
- **PEACH (#fab387)**: Gasket, transverse loads
- **MAUVE (#cba6f7)**: Washer, parallel connections

**Recommendation:** Keep the Catppuccin Mocha palette as-is. It's excellent for scientific software.

---

## 2. Layout Architecture Improvements

### 2.1 Proposed Layout: Adaptive 3-Panel with Collapsible Sections

```
+----------------------------------------------------------------------+
| TOOLBAR (icon-based, grouped, with overflow menu)          [?] [S] [X]|
+------+-----+---------------------------------------------+-----------+
|      |     |                                              |           |
| P    | Q   |   SCHEMATIC CANVAS                          | INSPECTOR |
| A    | U   |                                              |           |
| L    | I   |   Clean grid with snap                      | Tabbed:   |
| E    | C   |   Force arrows, connections                 | [Element] |
| T    | K   |                                              | [Loading] |
| T    |     |                                              | [Contact] |
| E    | A   |                                              |           |
|      | C   |                                              | Only shows|
| Elem | T   |                                              | relevant  |
| ents | I   |                                              | fields    |
|      | O   |                                              |           |
| only | N   |                                              |           |
|      | S   |                                              |           |
+------+-----+---------------------------------------------+-----------+
| STATUS: Model: 4 elements, 4 DOF | Preload: 79.1 kN | Valid: Yes   |
+----------------------------------------------------------------------+
```

### 2.2 Key Layout Changes

**A. Split Palette into two distinct columns:**
1. **Element Palette (narrow, ~120px):** Only element buttons, organized as icon+label vertical list
2. **Quick Actions (collapsible, ~160px):** Wizard, presets, validation cases - collapsed by default

**B. Inspector uses tabs instead of scroll:**
Replace 14 scrollable QGroupBox sections with 3-4 tabs:
- **Element Tab:** Type, position, MSD params, material, geometry
- **Loading Tab:** Global loading config, friction, bolt geometry
- **Contact Tab:** Contact interface props, thread/bearing/gasket specifics
- **Advanced Tab:** Thermal, tribology, thread fillet

**C. Status bar shows model health:**
Rich status bar with: element count, DOF, preload value, validation state (green/yellow/red dot)

### 2.3 Splitter Ratios (Revised)

```python
# Current: 15% / 55% / 30%
# Proposed: 10% / 60% / 30% (more canvas space)
splitter.setSizes([
    int(total_width * 0.10),  # Palette: narrower
    int(total_width * 0.60),  # Canvas: more space
    int(total_width * 0.30)   # Inspector: same
])

# Stretch factors: palette=1, canvas=6, inspector=2
splitter.setStretchFactor(0, 1)
splitter.setStretchFactor(1, 6)  # Was 4, give canvas more priority
splitter.setStretchFactor(2, 2)
```

---

## 3. Toolbar Redesign

### 3.1 Current Toolbar (17 items, all text)

```
[< Palette] [Inspector >] | [Undo] [Redo] | [Zoom+] [Zoom-] [Fit] |
[Load Flow] | [Series] [Parallel] | [Recalculate All] [Delete All] |
[Matrices] | [>> Solver] | [Validate] [Export] | [? Help]
```

**Problems:** Too many items, all text labels, no icons, no grouping cues.

### 3.2 Proposed Toolbar (Icon-first, Grouped)

```
FILE GROUP:         VIEW GROUP:         MODEL GROUP:           ACTION GROUP:
[New][Open][Save]   [Zoom+][Zoom-]     [Recalc][Validate]     [>> Solver]
[Export]            [Fit][Minimap]      [Matrices]             [? Help]
                                        [Load Flow]

EDIT GROUP (contextual):
[Undo][Redo] | [Delete][Duplicate] | [Series][Parallel]
```

### 3.3 Specific Recommendations

**A. Use icons with optional text (icon-only by default, text on hover/tooltip):**

| Action | Icon Suggestion | Shortcut | Tooltip |
|--------|----------------|----------|---------|
| Undo | Curved-left arrow | Ctrl+Z | Undo (Ctrl+Z) |
| Redo | Curved-right arrow | Ctrl+Y | Redo (Ctrl+Y) |
| Zoom In | Magnifier + | Ctrl++ | Zoom In |
| Zoom Out | Magnifier - | Ctrl+- | Zoom Out |
| Fit View | Expand-arrows | Ctrl+0 | Fit All to View |
| Recalculate | Refresh/sync | Ctrl+R | Recalculate All Elements |
| Validate | Checkmark-circle | Ctrl+Shift+V | Validate Model |
| Delete All | Trash with X | - | Delete All (with confirmation) |
| Matrices | Grid/table | Ctrl+M | View [M][K][C] Matrices |
| Load Flow | Flow-arrows | - | Toggle Load Flow Visualization |
| Export | Download-arrow | Ctrl+E | Export Model (.msd) |
| Send to Solver | Play/forward | Ctrl+Enter | Send to Solver Tab |
| Help | Question-mark | F1 | Help & Troubleshooting |

**B. Remove panel toggles from toolbar:**
Panel toggles (Palette/Inspector show/hide) should be in the View menu or use the splitter drag to collapse. This frees 2 toolbar slots.

**C. Group with visual separators and subtle background tints:**
```python
# Add QFrame spacers between groups for visual separation
toolbar.addWidget(_create_toolbar_spacer())  # 8px transparent spacer
```

**D. Move Series/Parallel to context menu:**
These are only useful when 2 elements are selected. They should be:
- In the right-click context menu (when 2 elements selected)
- In a floating toolbar that appears on multi-selection

**E. Overflow menu:**
Add a `>>` overflow button for less-used actions (Export, Help) on narrow screens.

### 3.4 Proposed Toolbar Implementation

```python
def _setup_toolbar(self):
    toolbar = QToolBar("Tools")
    toolbar.setMovable(False)
    toolbar.setIconSize(QSize(22, 22))  # Slightly larger icons
    toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
    self.addToolBar(toolbar)

    # GROUP 1: Edit
    toolbar.addAction(self.undo_action)
    toolbar.addAction(self.redo_action)
    toolbar.addSeparator()

    # GROUP 2: View
    toolbar.addAction(zoom_in_action)
    toolbar.addAction(zoom_out_action)
    toolbar.addAction(fit_action)
    toolbar.addSeparator()

    # GROUP 3: Model
    toolbar.addAction(recalc_action)
    toolbar.addAction(validate_action)
    toolbar.addAction(matrix_action)
    toolbar.addAction(load_flow_action)
    toolbar.addSeparator()

    # GROUP 4: File / Export
    toolbar.addAction(export_action)
    toolbar.addSeparator()

    # GROUP 5: Primary action (right-aligned)
    spacer = QWidget()
    spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    toolbar.addWidget(spacer)
    toolbar.addWidget(send_solver_btn)  # Primary, stands out
    toolbar.addAction(help_action)
```

---

## 4. Element Palette Declutter

### 4.1 Current State: 7 Groups, 20 Buttons, Excessive Scroll

The palette currently has:
1. Joint Wizard (1 btn)
2. Quick Presets (3 btns)
3. Validation Cases (combo + 2 btns + label)
4. Bolt Elements (4 btns: HEAD, SHANK, NUT, WASHER)
5. Member Elements (2 btns: FLANGE, GASKET)
6. Contact Elements (6 btns)
7. Boundary (1 btn: GROUND)

**Total:** 20 element buttons + 6 action buttons + 1 combo = too much for 280px width.

### 4.2 Proposed Palette: Compact Icon Grid

**A. Replace text buttons with icon tiles in a 2-column grid:**

```
+---------------------------+
| BOLT COMPONENTS           |
| [HEAD] [SHANK]           |
| [NUT]  [WASHER]          |
+---------------------------+
| MEMBERS                   |
| [FLANGE] [GASKET]        |
+---------------------------+
| CONTACTS                  |
| [Bear-H] [Bear-N]        |
| [Fl-Fl]  [Wash-C]        |
| [Gas-C]  [Generic]       |
+---------------------------+
| BOUNDARY                  |
| [GROUND]                  |
+---------------------------+
```

Each tile: 52x52px square with:
- Color-coded border (from ELEMENT_VISUALS)
- Unicode symbol centered (large, 16pt)
- Short label below (8pt): "Head", "Shank", etc.

**B. Move Wizard/Presets/Validation to a collapsible top section or a separate "Quick Start" popover button:**

```python
# Collapsible header with arrow toggle
class CollapsibleSection(QWidget):
    def __init__(self, title, parent=None):
        # Click header to expand/collapse
        # Default: collapsed
        # Shows: wizard btn, 3 preset btns, validation combo
```

**C. Reduce palette minimum width from 150px to 120px:**
Icon tiles at 52px fit 2 columns in 120px (with 8px margins).

### 4.3 Element Tile Implementation

```python
class ElementTile(QToolButton):
    """Compact element tile for palette."""

    def __init__(self, elem_type, visual, parent=None):
        super().__init__(parent)
        self.setFixedSize(56, 56)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setText(visual.name.split()[0])  # First word only
        self.setToolTip(f"{visual.name}\n{visual.description}")

        # Color-coded styling
        self.setStyleSheet(f"""
            QToolButton {{
                background: {visual.color}20;
                border: 2px solid {visual.color};
                border-radius: 6px;
                font-size: 8pt;
                color: {Theme.TEXT};
                padding: 2px;
            }}
            QToolButton:hover {{
                background: {visual.color}40;
                border-color: {Theme.LAVENDER};
            }}
        """)
```

### 4.4 Quick Start Panel (Collapsible)

Replace the 3 separate groups (Wizard, Presets, Validation) with one collapsible "Quick Start" panel:

```
+---------------------------+
| > Quick Start             |  (collapsed by default)
+---------------------------+
| v Quick Start             |  (expanded on click)
| [Configure Joint...]     |
| Presets:                  |
| [Single] [Flanged]       |
| [Junker]                 |
| Validation:              |
| [combo: Select case...]  |
| [Load] [Paper]           |
+---------------------------+
```

---

## 5. Property Inspector Reorganization

### 5.1 Current State: 14 Scrollable Groups

All 14 QGroupBox sections stack vertically with a single scroll area. On a 1000px tall window, only ~5 groups are visible at once. User must scroll constantly.

### 5.2 Proposed: Tabbed Inspector with Smart Visibility

```
+-----------------------------------+
| INSPECTOR                          |
+-----------------------------------+
| [Element] [Loading] [Contact]     |  <-- Tabs
+-----------------------------------+
| Tab: Element                       |
|                                    |
| Type: [HEAD v]                    |
| Position: Row [2] Col [0]        |
|                                    |
| -- MSD Parameters --              |
| k: [1.85e+09] N/m                |
| c: [100.0] Ns/m                  |
| m: [0.022] kg                    |
|                                    |
| -- Material --                    |
| Grade: [ASTM A193 B7 v]          |
| E: [205000] MPa                  |
| Sy: [720] MPa                    |
| rho: [7850] kg/m3                |
|                                    |
| -- Geometry --                    |
| d: [16.0] mm                     |
| L: [25.0] mm                     |
| p: [2.0] mm                      |
|                                    |
| -- Preload --                     |
| Mode: [% of Yield v]             |
| Yield: [70.0] %                  |
| F = 79,128 N                     |
+-----------------------------------+
```

### 5.3 Tab Definitions

**Tab 1: Element** (shown when element selected)
- Element Type combo
- Grid Position (row, col)
- MSD Parameters (k, c, m)
- Material Properties (grade, E, Sy, Su, rho)
- Geometry (diameter, length, pitch)
- Preload & Yield

**Tab 2: Loading** (always available, global settings)
- Load Type combo
- Preload (F_preload, % yield)
- Transverse Force / Displacement
- Frequency, Integration Time
- External Force, Torque, Delta T
- Friction & Bolt Geometry (mu, lubricated, bolt_dia, pitch)

**Tab 3: Contact** (shown when contact element selected)
- Contact Interface Properties (k_normal, k_tangential)
- Thread Contact Specific (pitch, helix, mean radius, engagement)
- Bearing Contact Specific (inner/outer radius, roughness)
- Gasket Contact Specific (type, thickness, compression modulus)
- Tribological Properties (mu_thread, mu_bearing, surface)
- Thread Fillet Panel (for THREAD type)

**Tab 4: Thermal** (shown when relevant)
- Thermal Properties (alpha, T_ref, T_operating)

### 5.4 Smart Visibility Rules

```python
def _update_inspector_tabs(self, element_data):
    """Show/hide tabs based on selected element type."""
    elem_type = element_data.type if element_data else None

    # Element tab: always show when element selected
    self.tab_widget.setTabEnabled(0, elem_type is not None)

    # Loading tab: always enabled (global settings)
    self.tab_widget.setTabEnabled(1, True)

    # Contact tab: only for contact elements
    is_contact = elem_type and elem_type.is_contact_interface
    self.tab_widget.setTabEnabled(2, is_contact)

    # Thermal tab: show for all physical elements
    self.tab_widget.setTabEnabled(3, elem_type is not None)

    # Within Element tab, show/hide groups:
    self.geometry_group.setVisible(elem_type and not elem_type.is_contact_interface)
    self.preload_group.setVisible(elem_type and elem_type.is_bolt_component)
```

### 5.5 Compact Form Layout

Replace wide QFormLayout with a tighter layout:

```python
# Current: QFormLayout with full-width labels + inputs
# Proposed: Grid layout with inline labels

# Example: MSD Parameters in compact 2-column grid
grid = QGridLayout()
grid.setSpacing(4)
grid.setContentsMargins(6, 6, 6, 6)

# Row 0: k
grid.addWidget(QLabel("k:"), 0, 0)
grid.addWidget(self.k_spin, 0, 1)
grid.addWidget(QLabel("N/m"), 0, 2)

# Row 1: c
grid.addWidget(QLabel("c:"), 1, 0)
grid.addWidget(self.c_spin, 1, 1)
grid.addWidget(QLabel("Ns/m"), 1, 2)

# Row 2: m
grid.addWidget(QLabel("m:"), 2, 0)
grid.addWidget(self.m_spin, 2, 1)
grid.addWidget(QLabel("kg"), 2, 2)
```

This saves ~30% vertical space by putting units inline instead of in the spinbox suffix.

---

## 6. Schematic Canvas Improvements

### 6.1 Grid Refinements

**A. Softer grid lines:**
Current grid uses SURFACE0 (dotted) and SURFACE1 (solid every 5). The minor grid lines are slightly too visible for a clean design.

```python
# Proposed: Reduce minor grid opacity
minor_pen = QPen(QColor(Theme.SURFACE0))
minor_pen.setStyle(Qt.PenStyle.DotLine)
minor_pen.setWidthF(0.5)  # Was 1.0 - thinner

# Major grid: keep but soften
major_pen = QPen(QColor(Theme.SURFACE1))
major_pen.setWidthF(0.75)  # Was 1.0
```

**B. Show row/column labels only on hover or when dragging:**
Currently row/col labels (R0, R1... C0, C1...) are always visible. They add visual noise. Show them:
- Always at the top-left corner (first row/col)
- On hover near edges
- When dragging an element (for positioning)
- Hide otherwise

**C. Add subtle zone indicators:**
```
+----------------------------------------------+
|  BOLT ZONE           | MEMBER ZONE           |
|  (blue tinted bg)    | (teal tinted bg)      |
|                      |                        |
|  HEAD  SHANK         | FLANGE  GASKET        |
|  NUT   WASHER        | FLANGE                |
|                      |                        |
|  CONTACT ZONE (between bolt and member)       |
|  (red tinted bg)                              |
+----------------------------------------------+
```

Not mandatory, but a very subtle background tint (alpha=5) on zones could guide placement.

### 6.2 Element Graphics Refinements

**A. Rounded corners on element boxes:**
```python
# Current: sharp QGraphicsRectItem
# Proposed: rounded rect
painter.drawRoundedRect(self.rect(), 8, 8)  # 8px corner radius
```

**B. Cleaner internal text layout:**
```
Current element box (100x60px):
+------------------------+
| HEAD            [70%] |
| k=1.85e+09            |
| #42                    |
+------------------------+

Proposed (cleaner hierarchy):
+------------------------+
| HEAD                   |
| k: 1.85 GN/m          |   <- Use engineering notation
| m: 22.0 g    #42      |   <- Combine ID with mass
+------------------------+
```

**C. Engineering notation for k/c/m values:**
```python
def format_engineering(value, unit):
    """Format with SI prefixes: 1.85e9 -> 1.85 GN/m"""
    prefixes = {-9: 'n', -6: 'u', -3: 'm', 0: '', 3: 'k', 6: 'M', 9: 'G', 12: 'T'}
    exp = int(math.floor(math.log10(abs(value)) / 3) * 3) if value != 0 else 0
    exp = max(-9, min(12, exp))
    mantissa = value / (10 ** exp)
    return f"{mantissa:.2f} {prefixes.get(exp, '')}{unit}"

# Example: 1.85e9 N/m -> "1.85 GN/m"
# Example: 0.022 kg -> "22.0 g"
```

**D. Stronger selection indicator:**
```python
# Current: yellow dashed outline
# Proposed: blue glow effect + thicker outline
if self.isSelected():
    # Outer glow
    glow_pen = QPen(QColor(Theme.BLUE))
    glow_pen.setWidth(6)
    glow_color = QColor(Theme.BLUE)
    glow_color.setAlpha(60)
    painter.setPen(QPen(glow_color, 6))
    painter.drawRoundedRect(self.rect().adjusted(-2, -2, 2, 2), 10, 10)
    # Inner selection border
    painter.setPen(QPen(QColor(Theme.BLUE), 2, Qt.PenStyle.SolidLine))
    painter.drawRoundedRect(self.rect(), 8, 8)
```

### 6.3 Connection Lines

**A. Smoother Bezier curves:**
```python
# Use cubic Bezier with control points at 1/3 and 2/3 of distance
# Current: straight or simple curves
# Proposed: smooth S-curves for parallel connections
```

**B. Contact indicators as inline badges:**
Instead of separate floating circles, show contact type as a small inline badge on the connection line:

```
[HEAD] ---[B]--- [WASHER]     B = Bearing contact
[NUT]  ---[T]--- [THREAD]     T = Thread contact
[FL1]  ---[G]--- [GASKET]     G = Gasket contact
```

### 6.4 Minimap (Small Overview)

Add a small minimap in the bottom-right corner of the canvas:

```python
class SchematicMinimap(QGraphicsView):
    """Small overview showing entire model."""
    def __init__(self, main_view, parent=None):
        super().__init__(parent)
        self.setFixedSize(150, 100)
        self.setScene(main_view.scene())
        self.setStyleSheet(f"""
            border: 1px solid {Theme.SURFACE1};
            border-radius: 4px;
            background: {Theme.MANTLE};
        """)
        # Semi-transparent, positioned in bottom-right corner
```

---

## 7. Context Menu Enhancement (Right-Click)

### 7.1 Current Context Menu (Sparse)

Right-click on element shows only:
- Duplicate
- Delete
- (separator)
- Apply Load/Constraint...
- Recalculate MSD
- (if 2 selected) Define Contact...
- (if NUT) Expand Threads...

### 7.2 Proposed Context Menu (Comprehensive)

**A. Right-click on single element:**

```
+----------------------------------+
| HEAD #3                          |  <- Header (non-clickable, shows element info)
+----------------------------------+
| Edit Properties...         F2    |
| Rename...                  F2    |
+----------------------------------+
| Duplicate              Ctrl+D   |
| Delete                 Del      |
+----------------------------------+
| Connect in Series       ↕       |  <- Only if another element selected
| Connect in Parallel     ↔       |  <- Only if another element selected
| Define Contact...               |  <- Only if 2 elements selected
+----------------------------------+
| Apply Load/Constraint...        |
| Recalculate Properties          |
+----------------------------------+
| Set as Anchor Point             |  <- Fix position, others relative
| Move to Row...                  |
| Move to Column...               |
+----------------------------------+
| Expand Threads...               |  <- Only for NUT
| Expand Thread Contacts...       |  <- Only for THREAD
+----------------------------------+
| Copy k/c/m Values               |
| Paste k/c/m Values              |
+----------------------------------+
```

**B. Right-click on empty canvas area:**

```
+----------------------------------+
| Add Element >                    |
|   +----------------------------+ |
|   | HEAD    SHANK  NUT  WASHER | |
|   | FLANGE  GASKET  GROUND     | |
|   | Contacts >                  | |
|   +----------------------------+ |
+----------------------------------+
| Paste Element             Ctrl+V |
+----------------------------------+
| Fit to View               Ctrl+0 |
| Reset Zoom                       |
| Toggle Grid                      |
| Toggle Load Flow                 |
+----------------------------------+
| Select All                Ctrl+A |
| Clear All...                     |
+----------------------------------+
```

**C. Right-click on connection line:**

```
+----------------------------------+
| Connection: HEAD #3 -> WASHER #5 |
+----------------------------------+
| Edit Contact Properties...       |
| Change to Series                 |
| Change to Parallel               |
| Remove Connection                |
+----------------------------------+
```

### 7.3 Context Menu Styling

```python
menu.setStyleSheet(f"""
    QMenu {{
        background: {Theme.SURFACE0};
        border: 1px solid {Theme.SURFACE2};
        border-radius: 6px;
        padding: 4px;
    }}
    QMenu::item {{
        padding: 6px 24px 6px 12px;
        border-radius: 4px;
    }}
    QMenu::item:selected {{
        background: {Theme.BLUE}30;
        color: {Theme.BLUE};
    }}
    QMenu::separator {{
        height: 1px;
        background: {Theme.SURFACE1};
        margin: 4px 8px;
    }}
    QMenu::item:disabled {{
        color: {Theme.OVERLAY};
    }}
""")
```

---

## 8. Left-Click Interaction Improvements

### 8.1 Single Click

| Target | Current | Proposed |
|--------|---------|----------|
| Element | Select + show in inspector | Same + subtle highlight animation |
| Empty canvas | Deselect all | Same + if palette element active, place it |
| Connection line | Nothing | Select connection, show in inspector |
| Contact indicator | Nothing | Select both connected elements |

### 8.2 Double Click

| Target | Current | Proposed |
|--------|---------|----------|
| Element | Nothing | Open inline edit (rename or quick-edit k/c/m) |
| Empty canvas | Nothing | Quick-add menu (popup with element choices) |
| Connection | Nothing | Edit contact properties dialog |
| Contact badge | Nothing | Edit contact dialog |

### 8.3 Click + Drag

| Gesture | Current | Proposed |
|---------|---------|----------|
| Drag element | Move on grid | Same + show ghost at original position |
| Drag from port | Nothing useful | Draw connection line to target |
| Drag on canvas | Rubber band select | Same + cursor change to crosshair |
| Middle-click drag | Nothing | Pan the view |
| Ctrl+click | Nothing | Add to selection (multi-select) |

### 8.4 Quick-Add by Double-Click

When the user double-clicks an empty grid cell, show a compact element picker popup:

```python
class QuickAddPopup(QMenu):
    """Compact popup for adding elements at clicked position."""

    def __init__(self, grid_row, grid_col, parent=None):
        super().__init__(parent)
        self.setTitle("Add Element")

        # Most common elements first
        for elem_type in ["HEAD", "SHANK", "NUT", "WASHER",
                          "FLANGE", "GASKET", "GROUND"]:
            visual = ELEMENT_VISUALS[elem_type]
            action = self.addAction(f"{visual.symbol} {visual.name}")
            action.setData(elem_type)

        self.addSeparator()
        contacts_menu = self.addMenu("Contacts")
        for elem_type in ["BEARING_HEAD", "BEARING_NUT", "FLANGE_FLANGE",
                          "WASHER_CONTACT", "GASKET_CONTACT", "GENERIC_CONTACT"]:
            visual = ELEMENT_VISUALS[elem_type]
            action = contacts_menu.addAction(f"{visual.symbol} {visual.name}")
            action.setData(elem_type)
```

---

## 9. Visual Design & Theme Refinement

### 9.1 Reduce Visual Noise

**A. Softer borders on QGroupBox:**
```css
/* Current */
QGroupBox {
    border: 1px solid #45475a;  /* SURFACE1 */
}

/* Proposed: softer, thinner */
QGroupBox {
    border: 1px solid #313244;  /* SURFACE0 - less contrast */
    border-top: 2px solid #89b4fa20;  /* Subtle blue top accent */
}
```

**B. Reduce padding/spacing in inspector:**
```css
/* Current: 10px padding, 8px spacing */
/* Proposed: tighter */
QGroupBox {
    padding: 6px;
    margin-top: 8px;  /* Was 12px */
}
```

**C. Use subtle dividers instead of group boxes for sections:**
```python
# Instead of QGroupBox for every section, use thin separators:
class SectionDivider(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setStyleSheet(f"""
            background: {Theme.SURFACE1};
            max-height: 1px;
            margin: 8px 0px 4px 0px;
        """)
```

### 9.2 Typography Hierarchy

```
Level 1: Panel headers       - 11pt, Bold, Theme.BLUE
Level 2: Section titles       - 10pt, SemiBold, Theme.TEXT
Level 3: Field labels         - 9pt, Regular, Theme.SUBTEXT
Level 4: Field values/inputs  - 9pt, Regular, Theme.TEXT
Level 5: Hints/units         - 8pt, Regular, Theme.OVERLAY
```

### 9.3 Input Field Sizing

```css
/* Tighter inputs for scientific data */
QDoubleSpinBox, QSpinBox {
    min-height: 22px;  /* Was 24px */
    padding: 2px 6px;  /* Was 4px 8px */
    font-family: 'Consolas', monospace;  /* Monospace for numbers */
}

QComboBox {
    min-height: 22px;
    padding: 2px 6px;
}
```

### 9.4 Consistent Icon Style

If adding icons, use a consistent line-weight:
- **Stroke width:** 1.5px
- **Corner radius:** 2px where applicable
- **Color:** Theme.TEXT (default), Theme.BLUE (active), Theme.OVERLAY (disabled)
- **Size:** 18x18px canvas, 16x16px content

Consider using Qt's built-in `QStyle.StandardPixmap` icons or a lightweight icon font (Lucide, Phosphor) via SVG.

---

## 10. Grid & Element Graphics

### 10.1 Grid Cell Size Optimization

Current: 120x80px per cell. This is good for desktop but can be adjusted:

```python
# Adaptive cell size based on element count
def get_adaptive_cell_size(n_elements):
    if n_elements <= 8:
        return 140, 90   # Larger for simple models
    elif n_elements <= 16:
        return 120, 80   # Default
    else:
        return 100, 65   # Compact for complex models
```

### 10.2 Element Box Redesign

**Current element appearance:**
```
+---------------------------+
| HEAD              [70%]  |
| k=1.85e+09              |
| #42                      |
+---------------------------+
  (flat rect, alpha=40 fill)
```

**Proposed element appearance:**
```
+---+---------------------+---+
|   | HEAD                |   |
|   | 1.85 GN/m  22.0 g  |   |    <- Engineering notation
|   |                 #42 |   |
+---+---------------------+---+
  ^                         ^
  Connection ports          Connection ports
  (visible on hover)        (visible on hover)
```

Key changes:
- **Rounded corners** (8px radius)
- **Engineering notation** for k, m values
- **Connection ports** at left/right (for parallel) and top/bottom (for series)
- **Gradient fill** instead of flat alpha - subtle top-to-bottom gradient
- **Type icon** (larger unicode symbol at left)

### 10.3 Connection Port Improvements

```python
# Current: 8x8 circles at top/bottom only, hidden by default
# Proposed: 4 ports (top, bottom, left, right), shown on hover

class ConnectionPort(QGraphicsEllipseItem):
    RADIUS = 5

    def __init__(self, position, parent=None):
        super().__init__(-self.RADIUS, -self.RADIUS,
                         2*self.RADIUS, 2*self.RADIUS, parent)
        # position: 'top', 'bottom', 'left', 'right'
        self.port_position = position

        self.setBrush(QBrush(QColor(Theme.BLUE)))
        self.setPen(QPen(QColor(Theme.BASE), 1.5))
        self.setOpacity(0.0)
        self.setZValue(10)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def show_animated(self):
        """Fade in on hover."""
        # Animate opacity from 0 to 0.85
        ...
```

### 10.4 Force Arrow Improvements

Current force arrows are small (8px head, 22px shaft). For better visibility:

```python
# Larger, more prominent arrows
ARROW_SIZE = 10   # Was 8
SHAFT_LEN = 28    # Was 22

# Add labels to force arrows
# Show force magnitude on hover: "F = 50.0 kN"
def hoverEnterEvent(self, event):
    self.label.setVisible(True)
    self.label.setText(f"F = {self.magnitude/1000:.1f} kN")
```

---

## 11. Responsive Design & Breakpoints

### 11.1 Window Size Breakpoints

```python
# Define breakpoints for responsive behavior
BREAKPOINT_SMALL = 1000   # Narrow screens
BREAKPOINT_MEDIUM = 1280  # Standard
BREAKPOINT_LARGE = 1600   # Wide screens

def _on_resize(self, event):
    w = event.size().width()

    if w < BREAKPOINT_SMALL:
        # Compact mode:
        # - Collapse palette to icon-only (no labels)
        # - Collapse inspector to single column
        # - Reduce toolbar to essential actions only
        self.palette.set_compact_mode(True)
        self.inspector.set_compact_mode(True)
    elif w < BREAKPOINT_MEDIUM:
        # Standard mode (current behavior)
        self.palette.set_compact_mode(False)
        self.inspector.set_compact_mode(False)
    else:
        # Wide mode:
        # - Show palette with full labels
        # - Show inspector with side-by-side fields
        self.palette.set_wide_mode(True)
        self.inspector.set_wide_mode(True)
```

### 11.2 Panel Auto-Collapse

When the canvas area shrinks below 400px wide:
1. Auto-collapse palette to icon column (50px wide)
2. If still too small, auto-hide inspector (show button to re-open)

```python
def _check_canvas_size(self):
    sizes = self.splitter.sizes()
    canvas_width = sizes[1]

    if canvas_width < 400:
        if self._right_panel_visible:
            self._toggle_right_panel()  # Auto-hide inspector
        elif self._left_panel_visible:
            self.palette.set_icon_only(True)  # Compact palette
```

### 11.3 High-DPI Support

Current DPI scaling is basic (base cell / 96 * screen DPI). Ensure:

```python
def get_grid_scale():
    """Get DPI-aware scaling factor."""
    screen = QApplication.primaryScreen()
    if screen:
        dpi = screen.logicalDotsPerInch()
        return max(0.75, min(2.0, dpi / 96.0))
    return 1.0

# Apply to all fixed sizes:
# - Grid cells: 120 * scale, 80 * scale
# - Element boxes: (cell - 20) * scale
# - Font sizes: base_pt * scale
# - Arrow sizes: 10 * scale
# - Connection port radius: 5 * scale
```

---

## 12. Graph & Visualization Improvements

### 12.1 Matrix Viewer Dialog

Current `MatrixViewerDialog` shows [M], [K], [C] as heatmap tabs. Improvements:

**A. Color scale refinement:**
```python
# Use diverging colormap for [K] (positive/negative values)
# Blue = negative, White = zero, Red = positive
from matplotlib.colors import TwoSlopeNorm

norm = TwoSlopeNorm(vmin=K.min(), vcenter=0, vmax=K.max())
ax.imshow(K, cmap='RdBu_r', norm=norm)
```

**B. Interactive cell hover:**
Show exact value on mouse hover over matrix cell (not just color):
```python
# Add cursor annotation
annot = ax.annotate("", xy=(0,0), xytext=(20,20),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round", fc=Theme.SURFACE0),
                    color=Theme.TEXT)
```

**C. Sparse matrix visualization:**
For large models, show non-zero pattern (spy plot) alongside full heatmap:
```python
# Add "Structure" tab showing sparsity pattern
ax.spy(K_sparse, markersize=3, color=Theme.BLUE)
ax.set_title(f"[K] Structure ({K_sparse.nnz} non-zero / {n*n} total)")
```

### 12.2 Load Flow Visualization

Current load flow uses `LoadFlowArrow` with color-coded percentages. Improvements:

**A. Animated flow:**
```python
# Animate dashed arrows to show direction of load path
# Use QTimeLine for smooth animation
self._flow_animation = QTimeLine(2000)  # 2s cycle
self._flow_animation.setLoopCount(0)    # Infinite
self._flow_animation.valueChanged.connect(self._update_flow_phase)
```

**B. Load magnitude labels:**
Show force magnitude at each connection:
```
[HEAD] --[50.0 kN]--> [BEARING] --[50.0 kN]--> [WASHER]
                                                    |
                                               [48.5 kN]
                                                    |
                                               [FLANGE]
```

### 12.3 Preload Distribution Chart

When multiple bolt elements exist, show a small bar chart in the inspector:

```
Preload Distribution:
HEAD:   ████████████████████ 50.0 kN
SHANK:  ████████████████████ 50.0 kN
NUT:    ████████████████████ 50.0 kN
THREAD: ██████████████       38.2 kN
```

### 12.4 Force Arrow Scale

Force arrows should be proportional to magnitude:

```python
def _compute_arrow_scale(self, force, max_force):
    """Scale arrow length proportional to force magnitude."""
    if max_force == 0:
        return 1.0
    ratio = abs(force) / max_force
    # Minimum 0.4x, maximum 1.5x of base size
    return 0.4 + ratio * 1.1
```

---

## 13. Keyboard Shortcuts & Accessibility

### 13.1 Current Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl++ | Zoom In |
| Ctrl+- | Zoom Out |
| Ctrl+0 | Fit View |
| Ctrl+[ | Toggle Palette |
| Ctrl+] | Toggle Inspector |
| Ctrl+D | Duplicate |
| Delete | Delete |
| F1 | Help |

### 13.2 Proposed Additional Shortcuts

| Shortcut | Action | Rationale |
|----------|--------|-----------|
| **Ctrl+A** | Select All | Standard |
| **Escape** | Deselect All / Cancel | Standard |
| **Ctrl+S** | Export/Save Model | Standard save |
| **Ctrl+R** | Recalculate All | Quick recalculate |
| **Ctrl+Shift+V** | Validate | Quick validate |
| **Ctrl+Enter** | Send to Solver | Primary action |
| **Ctrl+M** | Open Matrix Viewer | Quick matrix access |
| **Tab** | Cycle through elements | Navigate elements |
| **Shift+Tab** | Cycle backwards | Navigate back |
| **Ctrl+G** | Toggle Grid | Grid visibility |
| **Ctrl+L** | Toggle Load Flow | Load flow toggle |
| **Space** | Quick-add at cursor | Quick placement |
| **1-7** | Select element type | Fast palette (1=HEAD, 2=SHANK...) |
| **F2** | Rename selected | Inline rename |
| **Ctrl+Shift+C** | Copy properties | Copy k/c/m |
| **Ctrl+Shift+V** | Paste properties | Paste k/c/m |

### 13.3 Tooltip Improvements

Every interactive element should have a tooltip showing:
1. What it does (1 sentence)
2. Keyboard shortcut (if any)
3. Current state (if toggle)

```python
# Example tooltip formatting
def _format_tooltip(action_name, description, shortcut=None, state=None):
    parts = [f"<b>{action_name}</b>"]
    parts.append(description)
    if shortcut:
        parts.append(f"<span style='color:{Theme.OVERLAY}'>{shortcut}</span>")
    if state:
        parts.append(f"<span style='color:{Theme.GREEN}'>{state}</span>")
    return "<br>".join(parts)
```

### 13.4 Focus Indicators

Ensure all focusable elements have visible focus indicators:

```css
QToolButton:focus,
QPushButton:focus,
QSpinBox:focus,
QComboBox:focus {
    border: 1px solid #89b4fa;  /* Theme.BLUE */
    outline: none;
}
```

---

## 14. Implementation Priority

### Phase 1: Quick Wins (1-2 days each)

| # | Change | Impact | Effort | Files |
|---|--------|--------|--------|-------|
| 1 | **Inspector tabs** (replace scroll with 3 tabs) | HIGH | MEDIUM | msd_builder.py |
| 2 | **Engineering notation** on element labels | HIGH | LOW | msd_builder.py |
| 3 | **Rounded element corners** | MEDIUM | LOW | msd_builder.py |
| 4 | **Enhanced context menu** (right-click) | HIGH | MEDIUM | msd_builder.py |
| 5 | **Softer grid lines** | MEDIUM | LOW | msd_builder.py |
| 6 | **Additional shortcuts** (Ctrl+A, Escape, etc.) | MEDIUM | LOW | msd_builder.py |
| 7 | **Rich status bar** (preload value, validation) | MEDIUM | LOW | msd_builder.py |
| 8 | **Compact form layout** in inspector | MEDIUM | LOW | msd_builder.py |

### Phase 2: Medium Effort (3-5 days each)

| # | Change | Impact | Effort | Files |
|---|--------|--------|--------|-------|
| 9 | **Toolbar icon redesign** | HIGH | MEDIUM | msd_builder.py, icons/ |
| 10 | **Element tile palette** (icon grid) | HIGH | MEDIUM | msd_builder.py |
| 11 | **Quick-add popup** (double-click canvas) | HIGH | MEDIUM | msd_builder.py |
| 12 | **Connection port improvements** (4 ports) | MEDIUM | MEDIUM | msd_builder.py |
| 13 | **Canvas context menu** (empty area right-click) | MEDIUM | MEDIUM | msd_builder.py |
| 14 | **Smart inspector visibility** | MEDIUM | MEDIUM | msd_builder.py |

### Phase 3: Larger Effort (1-2 weeks each)

| # | Change | Impact | Effort | Files |
|---|--------|--------|--------|-------|
| 15 | **Responsive breakpoints** | MEDIUM | HIGH | msd_builder.py |
| 16 | **Matrix viewer improvements** | MEDIUM | HIGH | matrix_viewer.py |
| 17 | **Animated load flow** | LOW | HIGH | msd_builder.py |
| 18 | **Minimap** | LOW | MEDIUM | msd_builder.py |
| 19 | **Inline element editing** (double-click) | MEDIUM | HIGH | msd_builder.py |
| 20 | **Connection line right-click** | LOW | MEDIUM | msd_builder.py |

### Phase 4: Polish

| # | Change | Impact | Effort |
|---|--------|--------|--------|
| 21 | Tooltip formatting with HTML | LOW | LOW |
| 22 | Focus indicators for accessibility | LOW | LOW |
| 23 | Adaptive cell sizing | LOW | MEDIUM |
| 24 | Force arrow proportional scaling | LOW | LOW |
| 25 | Quick Start collapsible panel | LOW | MEDIUM |

---

## Summary of Top 10 Recommendations

1. **Replace scroll inspector with tabbed inspector** - Reduces visual clutter by 60%, shows only relevant fields
2. **Enhanced right-click context menus** - Full actions on elements, canvas, and connections
3. **Engineering notation on elements** - "1.85 GN/m" instead of "k=1.85e+09" is cleaner and more readable
4. **Compact icon-grid palette** - 2-column icon tiles instead of full-width text buttons
5. **Icon-only toolbar** - Replace text labels with icons, group logically, right-align primary action
6. **Rounded element corners** - Modern, softer visual appearance
7. **Softer grid lines** - Reduce minor grid opacity for cleaner canvas
8. **Double-click quick-add** - Double-click empty cell to place elements without palette
9. **Rich status bar** - Show preload, validation state, and model health at a glance
10. **Additional keyboard shortcuts** - Ctrl+A, Escape, Tab navigation, number keys for element types

---

## Design Principles Applied

1. **Progressive Disclosure** - Show only what's needed, hide complexity behind tabs/menus
2. **Direct Manipulation** - Double-click to edit, drag to connect, right-click for full context
3. **Visual Hierarchy** - Clear size/weight/color hierarchy: headers > labels > values > hints
4. **Consistency** - Same interaction patterns everywhere (right-click always shows context menu)
5. **Feedback** - Selection glow, hover effects, status bar updates, connection previews
6. **Efficiency** - Keyboard shortcuts for power users, mouse for discovery
7. **Scientific Rigour** - Engineering notation, proper units, VDI 2230 terminology preserved
8. **Minimal Chrome** - Reduce borders, padding, separators - let the content breathe

---

## Appendix A: Industry CAE/FEA UI Research

Research based on modern engineering software patterns from ANSYS Mechanical, COMSOL Multiphysics, Abaqus/CAE, Siemens NX, Altium Designer, KiCad 8, Blender, Unity, and Figma.

### A.1 Three-Panel Layout (Industry Standard)

All modern CAE tools use the same three-panel layout that BAS already follows:
```
Left (200-280px):  Model tree / Element browser (collapsible)
Center (flexible): Primary viewport / canvas (takes all remaining space)
Right (280-350px): Property inspector / Settings panel (collapsible)
```

**Key improvement from COMSOL:** Add optional bottom panel (150-200px, hideable) for:
- Log/console output during analysis
- Validation messages
- Quick parameter summary

**Splitter best practice:** Use `stretch_factor(0, 0)` for fixed-width sidebars and `stretch_factor(1, 1)` for center (only center stretches on resize).

### A.2 Element Placement Patterns (Simulink/KiCad)

**Ghost element placement (KiCad style):**
1. Click element in palette -- cursor changes to crosshair with ghost preview
2. Transparent element follows cursor over grid
3. Valid cells highlight green, invalid show red
4. Click to place, ESC to cancel
5. Element snaps to nearest grid cell

**Rapid placement mode (Simulink style):**
1. Double-click palette button to enter placement mode
2. Click canvas repeatedly to place multiple elements of same type
3. Right-click or ESC to exit placement mode

### A.3 Property Inspector Patterns (Blender/Unity)

**Collapsible section memory:**
```python
# Remember which sections were expanded per element type
_expanded_sections = {
    "HEAD": {"General": True, "Mechanical": True, "Geometry": False},
    "NUT": {"General": True, "Mechanical": True, "Contact": True},
}
```

**Sticky header:** Element name/type stays pinned at top while scrolling through properties.

**Number scrubbing (Blender pattern):** Click and drag horizontally on a QDoubleSpinBox to scrub the value up/down. Very efficient for parameter exploration.

**Multi-selection editing:** When 2+ elements selected:
- Show only common properties
- Display "Mixed" placeholder when values differ
- Editing applies to all selected elements
- Show "N elements selected" indicator

### A.4 Toolbar Design (ANSYS/COMSOL)

**Icon sizing:**
- 24x24px for toolbar icons
- 16x16px for tab/tree icons
- Line/outline style, 2px stroke, never filled
- Default color: SUBTEXT, Active: BLUE, Disabled: OVERLAY at 50% opacity

**Grouping rules:**
- Max 4-5 groups per toolbar row
- 8-12px visual separator between groups
- Most-used actions on the left
- Destructive actions separated or right-aligned

**Responsive behavior:**
- Icon+text at wide widths, icon-only when narrow
- Use `QToolButton.MenuButtonPopup` for grouped overflow

### A.5 Matplotlib Dark Theme Improvements

**Remove chart chrome for cleaner plots:**
```python
additional_rcparams = {
    'axes.spines.top': False,      # Remove top spine
    'axes.spines.right': False,    # Remove right spine
    'axes.grid': True,
    'grid.linestyle': '--',
    'grid.linewidth': 0.5,
    'lines.linewidth': 1.8,
    'lines.markersize': 5,
    'figure.constrained_layout.use': True,  # Better than tight_layout
}
```

**Diverging colormap for Matrix Viewer:**
- Negative values: RED to MAROON (warm)
- Zero: SURFACE0 (dark neutral)
- Positive values: BLUE to SAPPHIRE (cool)

**Color-blind accessibility:** Pair line colors with different styles:
```python
# Don't rely on color alone
styles = ['-', '--', '-.', ':', '-', '--', '-.', ':']
markers = ['o', 's', '^', 'D', 'v', 'P', '*', 'X']
# Use with the 8-color Catppuccin accent cycle
```

### A.6 Safety Factor Visual Indicators

From VDI 2230 convention, display safety factors as color-coded badges:
```
Factor > 1.5:  GREEN background   "SF = 2.3  OK"
Factor 1.0-1.5: YELLOW background  "SF = 1.2  MARGINAL"
Factor < 1.0:  RED background      "SF = 0.8  FAIL"
```

### A.7 WCAG Contrast Ratios (Catppuccin Mocha)

The Catppuccin Mocha palette has excellent accessibility:
- TEXT on BASE: ~11:1 (exceeds AAA)
- TEXT on SURFACE0: ~8:1 (exceeds AAA)
- SUBTEXT on BASE: ~6.5:1 (exceeds AA)
- BLUE on BASE: ~6:1 (exceeds AA for large text)
- OVERLAY on BASE: ~3.5:1 (AA for large text only -- use for disabled/decorative)

**Rule:** Never use OVERLAY for interactive text; use SUBTEXT minimum.
