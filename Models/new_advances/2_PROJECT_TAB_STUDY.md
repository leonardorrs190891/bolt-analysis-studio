# Project Tab (Tab 1) — Design & Usability Study

**Bolt Analysis Studio v4.0** — LTAD/UFU / Petrobras R&D
**Date:** 2026-02-18
**Scope:** Complete audit of Tab 1 (ProjectTab), with layout, responsiveness, usability, visual design, and data-integrity improvement plans.

---

## Table of Contents

1. [Current State Analysis](#1-current-state-analysis)
2. [Issues Found — Categorised](#2-issues-found--categorised)
3. [Layout Architecture Proposals](#3-layout-architecture-proposals)
4. [Information Architecture Improvements](#4-information-architecture-improvements)
5. [Visual Design Refinements](#5-visual-design-refinements)
6. [Responsiveness Strategy](#6-responsiveness-strategy)
7. [Usability Improvements](#7-usability-improvements)
8. [Missing Data Fields](#8-missing-data-fields)
9. [New Components to Add](#9-new-components-to-add)
10. [ProjectInfo Dataclass Extension](#10-projectinfo-dataclass-extension)
11. [Signal & Data-Flow Improvements](#11-signal--data-flow-improvements)
12. [Implementation Priority Matrix](#12-implementation-priority-matrix)
13. [PyQt6 Code Snippets](#13-pyqt6-code-snippets)

---

## 1. Current State Analysis

### 1.1 Current Layout (as-coded)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  QHBoxLayout  (margins: 16px, spacing: 16px)                           │
├──────────────────────────────┬──────────────────────────────────────────┤
│  LEFT PANEL  (stretch=1)     │  RIGHT PANEL  (stretch=1)               │
│  QVBoxLayout                 │  QVBoxLayout                             │
│                              │                                          │
│  ┌──────────────────────┐    │  ┌────────────────────────────────────┐  │
│  │ 📁 Project Info       │    │  │ 📐 Units Configuration             │  │
│  │  QFormLayout          │    │  │  QFormLayout                       │  │
│  │  - Project Name       │    │  │  - Length  (combo)                │  │
│  │  - Description        │    │  │  - Force   (combo)                │  │
│  │    QTextEdit h=80px   │    │  │  - Pressure(combo)                │  │
│  │  - Author             │    │  │  - Temperature (combo)             │  │
│  │  - Company            │    │  └────────────────────────────────────┘  │
│  └──────────────────────┘    │                                          │
│                              │  ┌────────────────────────────────────┐  │
│  ┌──────────────────────┐    │  │ ⚡ Quick Actions                    │  │
│  │ 📋 Standards & Codes  │    │  │  QVBoxLayout                       │  │
│  │  QFormLayout          │    │  │  - New Project                    │  │
│  │  - Analysis Std       │    │  │  - Open Project                   │  │
│  │  - Material Std       │    │  │  - Save Project (primary)         │  │
│  │  - Flange Std         │    │  │  - Export Report                  │  │
│  └──────────────────────┘    │  └────────────────────────────────────┘  │
│                              │                                          │
│  addStretch()                │  ┌────────────────────────────────────┐  │
│                              │  │ 🕐 Recent Projects                  │  │
│                              │  │  QListWidget                       │  │
│                              │  │  (HARDCODED 3 FAKE ITEMS)          │  │
│                              │  └────────────────────────────────────┘  │
│                              │                                          │
│                              │  addStretch()                            │
└──────────────────────────────┴──────────────────────────────────────────┘
```

### 1.2 Current Code Metrics

| Item | Value |
|------|-------|
| Lines of code (ProjectTab._setup_ui) | ~135 lines |
| Widgets used | 14 |
| GroupBoxes | 4 |
| Signal connections | 0 (no live signals) |
| Real data bindings | 0 (all static) |
| Recent projects persistence | None — hardcoded strings |
| QSplitter used | No |
| ScrollArea used | No |

---

## 2. Issues Found — Categorised

### 2.1 Layout Issues

| # | Issue | Severity | Location |
|---|-------|----------|----------|
| L1 | Fixed 50/50 stretch — cannot be resized by user | High | `layout.addWidget(..., stretch=1)` |
| L2 | Standards and Units groups have no logical visual link | Medium | Left vs Right panels |
| L3 | Quick Actions group stacks 4 buttons vertically — wastes width | Medium | Right panel |
| L4 | Description field locked at `maxHeight=80` — too small | High | `setMaximumHeight(80)` |
| L5 | No welcome / branding banner at the top of the tab | Medium | Tab root |
| L6 | `addStretch()` at bottom of each panel causes floating groups | Low | Both panels |
| L7 | Standards group on LEFT, Units on RIGHT — no rationale for split | Low | Panel assignment |

### 2.2 Responsiveness Issues

| # | Issue | Severity | Note |
|---|-------|----------|------|
| R1 | No `QSplitter` — panels cannot be resized | High | Fixed 50/50 |
| R2 | No `QScrollArea` — content clips on small monitors (<900px tall) | High | Small screens |
| R3 | Buttons in Quick Actions have no minimum size — collapse at small widths | Medium | QPushButton |
| R4 | GroupBoxes have no `setMinimumHeight` — can become invisible | Medium | All QGroupBox |
| R5 | No adaptive column count — always 2 columns regardless of window width | Medium | Future: grid layout |

### 2.3 Usability Issues

| # | Issue | Severity | Note |
|---|-------|----------|------|
| U1 | **Recent Projects list is FAKE** — hardcoded, no persistence, no signals | Critical | `QListWidget` |
| U2 | No double-click handler to open a recent project | Critical | `QListWidget` |
| U3 | No project status indicator — user cannot tell if unsaved | High | Tab header |
| U4 | No file path display — user cannot see where project is saved | High | Missing widget |
| U5 | "Export Report" in Quick Actions opens wrong tab context | Medium | Button semantics |
| U6 | No validation — empty Project Name is allowed silently | Medium | `name_edit` |
| U7 | Units combos have no warning when model already exists | Medium | `combo.currentIndex` |
| U8 | Standards selection has no tooltips explaining what they affect | Medium | `QComboBox` |
| U9 | No keyboard shortcut or tab-order defined for form fields | Low | Focus traversal |
| U10 | Author/Company have no pre-fill from OS user settings | Low | OS integration |

### 2.4 Data & Functionality Gaps

| # | Issue | Severity | Note |
|---|-------|----------|------|
| D1 | Missing field: Institution / Laboratory (UFU/LTAD context) | High | `ProjectInfo` |
| D2 | Missing field: Project Number / Document Number | Medium | Engineering DCC |
| D3 | Missing field: Revision letter/number | Medium | Version control |
| D4 | Missing field: Notes / Comments (separate from description) | Low | Traceability |
| D5 | `created` and `modified` timestamps in `ProjectInfo` but not displayed | Medium | Transparency |
| D6 | No project "completeness" indicator | Low | UX polish |
| D7 | No project template / quick-start preset system | Medium | Onboarding |
| D8 | No model summary card (element count, DOF, k_sys) | Medium | Context |

### 2.5 Visual Design Issues

| # | Issue | Severity | Note |
|---|-------|----------|------|
| V1 | No application branding visible in Tab 1 | Low | First impression |
| V2 | All `QPushButton` same size/color — no visual hierarchy | High | Actions group |
| V3 | `QListWidget` items are plain text with no icons or dates | Medium | Recent list |
| V4 | GroupBox emoji headers: inconsistent padding across platforms | Low | Cross-platform |
| V5 | No color-coded status badge (New / Modified / Saved) | Medium | State feedback |
| V6 | Form labels align left with no column-width control | Low | QFormLayout |

---

## 3. Layout Architecture Proposals

### Option A — 3-Column Grid (Recommended)

Replaces 2-panel split with a true 3-column layout using a `QSplitter` for resizability.

```
┌────────────────────────────────────────────────────────────────────────────┐
│  STATUS BAR (compact, full-width)                                          │
│  [● BAS v4.0]  [Project: My Project]  [Status: UNSAVED ●]  [Path: …]     │
├──────────────────────┬──────────────────────┬──────────────────────────────┤
│  COL 1 (38%)         │  COL 2 (27%)         │  COL 3 (35%)                │
│  PROJECT IDENTITY    │  CONFIGURATION       │  WORKSPACE                  │
│                      │                      │                             │
│  ┌────────────────┐  │  ┌────────────────┐  │  ┌─────────────────────┐   │
│  │ Project Info   │  │  │ Standards      │  │  │ ⚡ Quick Actions     │   │
│  │ - Name         │  │  │ - Analysis Std │  │  │ [◆ New] [◆ Open]   │   │
│  │ - Description  │  │  │ - Material Std │  │  │     [◆ Save]        │   │
│  │   (tall field) │  │  │ - Flange Std   │  │  └─────────────────────┘   │
│  │ - Author       │  │  └────────────────┘  │                            │
│  │ - Company      │  │                      │  ┌─────────────────────┐   │
│  │ - Institution  │  │  ┌────────────────┐  │  │ 🕐 Recent Projects  │   │
│  │ - Proj. No.    │  │  │ Units System   │  │  │ (real, with dates)  │   │
│  │ - Revision     │  │  │ 2x2 grid       │  │  │ (double-click open) │   │
│  └────────────────┘  │  └────────────────┘  │  └─────────────────────┘   │
│                      │                      │                            │
│  ┌────────────────┐  │  ┌────────────────┐  │  ┌─────────────────────┐   │
│  │ Timestamps     │  │  │ Notes          │  │  │ 📐 Templates        │   │
│  │ Created: …     │  │  │ (small editor) │  │  │ [Junker Test]       │   │
│  │ Modified: …    │  │  └────────────────┘  │  │ [API 6A Flange]    │   │
│  └────────────────┘  │                      │  │ [ISO Flange]        │   │
│                      │                      │  └─────────────────────┘   │
│                      │                      │                            │
│                      │                      │  ┌─────────────────────┐   │
│                      │                      │  │ 📊 Model Summary    │   │
│                      │                      │  │ Elements: —         │   │
│                      │                      │  │ DOF: —              │   │
│                      │                      │  │ k_sys: — N/m        │   │
│                      │                      │  └─────────────────────┘   │
└──────────────────────┴──────────────────────┴──────────────────────────────┘
```

**Pros:** Clear separation of identity / config / workspace. Each column has a single responsibility.
**Cons:** 3-column may feel dense on 1280px-wide windows.

---

### Option B — Top Banner + 2-Column Split with QSplitter (Simpler)

Keeps the 2-panel concept but adds a fixed-height hero bar, uses `QSplitter`, and extends the left panel.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  HERO BANNER (fixed 56px)                                                   │
│  [BAS v4.0 | LTAD/UFU]  ·····  [● My Project  —  UNSAVED]  [Open] [Save]  │
├──────────────────────────────────┬──────────────────────────────────────────┤
│  LEFT PANEL (QScrollArea, 55%)   │  RIGHT PANEL (40%)                      │
│                                  │                                          │
│  ┌──────────────────────────┐    │  ┌──────────────────────────────────┐   │
│  │ 📁 Project Information    │    │  │ ⚡ Quick Actions                  │   │
│  │ Name, Description (tall)  │    │  │  2×2 button grid, styled         │   │
│  │ Author, Company           │    │  └──────────────────────────────────┘   │
│  │ Institution, Proj. No.    │    │                                          │
│  │ Revision                  │    │  ┌──────────────────────────────────┐   │
│  └──────────────────────────┘    │  │ 🕐 Recent Projects (real list)   │   │
│                                  │  │  item: name + date + path tooltip │   │
│  ┌──────────────────────────┐    │  └──────────────────────────────────┘   │
│  │ 📋 Standards & Codes      │    │                                          │
│  │ (3 combos + tooltips)     │    │  ┌──────────────────────────────────┐   │
│  └──────────────────────────┘    │  │ 📐 Units System (2×2 grid)       │   │
│                                  │  └──────────────────────────────────┘   │
│  ┌──────────────────────────┐    │                                          │
│  │ 🕒 Timestamps             │    │  ┌──────────────────────────────────┐   │
│  │  Created  Modified        │    │  │ 📐 Templates & Presets           │   │
│  └──────────────────────────┘    │  └──────────────────────────────────┘   │
│                                  │                                          │
│  ┌──────────────────────────┐    │  ┌──────────────────────────────────┐   │
│  │ 📝 Notes                  │    │  │ 📊 Model Summary (live)          │   │
│  │  (small free-text area)   │    │  └──────────────────────────────────┘   │
│  └──────────────────────────┘    │                                          │
└──────────────────────────────────┴──────────────────────────────────────────┘
```

**Pros:** Evolutionary change from current code — reduces regression risk. Hero bar solves branding and status in one stroke.
**Cons:** Left panel can get tall — mitigated by QScrollArea.

**RECOMMENDATION: Option B** — better balance between improvement scope and implementation risk. The existing left/right mental model is preserved, but every specific issue is addressed.

---

## 4. Information Architecture Improvements

### 4.1 Content Priority (F-pattern reading order)

Users read top-left first. The most important action (New / Open / Save) must be visible immediately without scrolling. Current layout buries Quick Actions at right-middle.

**Priority Map:**
```
TIER 1 — Always Visible:
  Hero bar: project name, status badge, primary Save/Open buttons

TIER 2 — Above the Fold (first viewport):
  Left:  Project Name, Description, Author, Company
  Right: Quick Actions (2×2 grid), Recent Projects

TIER 3 — Scrollable:
  Left:  Institution, Project No, Revision, Timestamps, Notes
  Right: Standards, Units, Templates, Model Summary
```

### 4.2 Logical Grouping Rationale

| Group | Content | Panel | Why |
|-------|---------|-------|-----|
| Project Identity | Name, Description, Author, Company, Institution, Proj. No., Revision | Left | Who / What — define project context |
| Analysis Config | Standards, Units | Right (mid) | How — define calculation rules |
| Workspace | Actions, Recent, Templates, Model Summary | Right | Do — workspace operations |
| Metadata | Timestamps, Notes | Left (bottom) | Reference only — de-emphasised |

---

## 5. Visual Design Refinements

### 5.1 Hero Status Bar

A fixed 48–56px bar at the top of the tab (outside the scrollable content area). Styled with `Theme.MANTLE` background.

```
╔═══════════════════════════════════════════════════════════════════════╗
║  [BAS ICON]  Bolt Analysis Studio v4.0       ● UNSAVED  model.msd  ║
║  LTAD/UFU — Petrobras R&D                    [Open ▼]  [Save ■]    ║
╚═══════════════════════════════════════════════════════════════════════╝
```

**Status Badge Colors** (using Theme palette):
- `NEW` → `Theme.TEAL` background
- `MODIFIED (unsaved)` → `Theme.PEACH` background
- `SAVED` → `Theme.GREEN` background
- `ERROR` → `Theme.RED` background

### 5.2 Quick Actions Button Grid

Replace vertical button stack with a **2×2 grid** of styled buttons:

```
┌──────────────┬──────────────┐
│ ◆ New        │ 📂 Open      │
│  Project     │  Project     │
├──────────────┼──────────────┤
│ 💾 Save      │ 📤 Export    │
│  [PRIMARY]   │  Report      │
└──────────────┴──────────────┘
```

- "Save" uses `objectName="primary"` — Theme.BLUE styled
- All buttons use `setMinimumHeight(48)` for touch-friendliness
- Icon + two-line label text for clarity

### 5.3 Recent Projects List Upgrade

Current: `QListWidget` with plain text.
Proposed: Custom delegate `QStyledItemDelegate` for rich items:

```
┌─────────────────────────────────────────────────────┐
│ 📁  Example_Flanged_Joint.msd                       │
│     C:\Users\…\BAS\Models\  ·  Modified: 2026-02-17 │
├─────────────────────────────────────────────────────┤
│ 📁  API_6A_15000psi.msd                             │
│     C:\Users\…\BAS\Models\  ·  Modified: 2026-02-12 │
├─────────────────────────────────────────────────────┤
│ 📁  Junker_Test_Simulation.msd                      │
│     C:\Users\…\BAS\Models\  ·  Modified: 2026-02-10 │
└─────────────────────────────────────────────────────┘
```

- Stored in `QSettings` as JSON list `[{path, name, modified}, …]`
- Max 10 items, FIFO eviction
- Double-click → load project
- Right-click context menu: `Open | Remove from list | Open folder`
- Missing files shown grayed-out with `[File not found]` suffix

### 5.4 Status Indicator in Tab Label

Update tab label dynamically:

```python
# Unsaved
self.tab_widget.setTabText(0, "1. 📁 Project ●")

# Saved
self.tab_widget.setTabText(0, "1. 📁 Project")
```

### 5.5 Field Validation Indicators

Required fields (Project Name) show a subtle red left-border when empty:

```python
# On name_edit textChanged:
if not text.strip():
    self.name_edit.setStyleSheet(f"border-left: 3px solid {Theme.RED};")
else:
    self.name_edit.setStyleSheet("")
```

---

## 6. Responsiveness Strategy

### 6.1 Replace Fixed Stretch with QSplitter

```python
# CURRENT (fixed)
layout.addWidget(left_panel, stretch=1)
layout.addWidget(right_panel, stretch=1)

# PROPOSED
splitter = QSplitter(Qt.Orientation.Horizontal)
splitter.addWidget(left_scroll)   # QScrollArea wrapping left panel
splitter.addWidget(right_panel)
splitter.setSizes([550, 450])     # 55/45 initial split
splitter.setCollapsible(0, False)
splitter.setCollapsible(1, False)
layout.addWidget(splitter)
```

### 6.2 Left Panel in QScrollArea

```python
left_scroll = QScrollArea()
left_scroll.setWidget(left_panel)
left_scroll.setWidgetResizable(True)
left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
left_scroll.setFrameShape(QFrame.Shape.NoFrame)
```

### 6.3 Description Field Height

```python
# CURRENT
self.description_edit.setMaximumHeight(80)

# PROPOSED
self.description_edit.setMinimumHeight(100)
self.description_edit.setMaximumHeight(180)
self.description_edit.setSizePolicy(
    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
)
```

### 6.4 Minimum Window Handling

Set `setMinimumSize` on `ProjectTab`:

```python
self.setMinimumSize(720, 480)
```

### 6.5 Breakpoint Behaviour (via resizeEvent)

Override `resizeEvent` to collapse right panel to tabs or hide optional groups below 900px width:

```python
def resizeEvent(self, event):
    super().resizeEvent(event)
    narrow = event.size().width() < 900
    self.model_summary_group.setVisible(not narrow)
    self.templates_group.setVisible(not narrow)
```

---

## 7. Usability Improvements

### 7.1 Recent Projects — Full Implementation

**Storage:** `QSettings("LTAD-UFU", "BoltAnalysisStudio")`
**Key:** `"recent_projects"` → JSON list of `{path, name, modified_iso}` dicts
**Capacity:** 10 items, FIFO

```python
class RecentProjectsManager:
    MAX_ITEMS = 10
    SETTINGS_KEY = "recent_projects"

    @staticmethod
    def get() -> list[dict]:
        s = QSettings("LTAD-UFU", "BoltAnalysisStudio")
        raw = s.value(RecentProjectsManager.SETTINGS_KEY, "[]")
        return json.loads(raw)

    @staticmethod
    def add(path: str):
        items = RecentProjectsManager.get()
        items = [i for i in items if i["path"] != path]  # remove duplicate
        items.insert(0, {
            "path": path,
            "name": Path(path).stem,
            "modified_iso": datetime.now().isoformat()
        })
        items = items[:RecentProjectsManager.MAX_ITEMS]
        s = QSettings("LTAD-UFU", "BoltAnalysisStudio")
        s.setValue(RecentProjectsManager.SETTINGS_KEY, json.dumps(items))
```

**Signals:**
- `QListWidget.itemDoubleClicked` → emit `open_recent_requested(path)`
- Connect in `BoltAnalysisStudio._connect_tab_buttons()` to `_open_project(path=path)`

### 7.2 Units System Warning

When a unit combo changes and the model has elements already, show an inline warning:

```python
def _on_unit_changed(self):
    model = get_app_state().current_model
    if model and len(model.elements) > 0:
        self._units_warning_label.setText(
            "⚠ Unit changes do not auto-convert existing model values."
        )
        self._units_warning_label.setVisible(True)
    else:
        self._units_warning_label.setVisible(False)
```

### 7.3 Standards Tooltips

```python
self.standard_combo.setToolTip(
    "VDI 2230: German engineering standard for bolted joints.\n"
    "Affects: safety factor calculation, tightening torque, load case definitions."
)
self.material_combo.setToolTip(
    "Material standard used for bolt grade lookup in the materials database.\n"
    "Affects: yield strength, proof load, allowable stress values."
)
self.flange_combo.setToolTip(
    "Flange design standard.\n"
    "Affects: seating stress, gasket factors (m, y), pressure ratings."
)
```

### 7.4 Auto-Fill from OS

```python
import getpass
if not self.author_edit.text():
    self.author_edit.setText(getpass.getuser())
```

### 7.5 Project Name Validation

```python
self.name_edit.textChanged.connect(self._validate_name)

def _validate_name(self, text: str):
    is_valid = bool(text.strip())
    color = "transparent" if is_valid else Theme.RED
    self.name_edit.setStyleSheet(
        f"border-left: 3px solid {color};" if not is_valid else ""
    )
    self._save_btn.setEnabled(is_valid)
```

### 7.6 Tab-Order

```python
QWidget.setTabOrder(self.name_edit, self.description_edit)
QWidget.setTabOrder(self.description_edit, self.author_edit)
QWidget.setTabOrder(self.author_edit, self.company_edit)
QWidget.setTabOrder(self.company_edit, self.institution_edit)
QWidget.setTabOrder(self.institution_edit, self.project_no_edit)
QWidget.setTabOrder(self.project_no_edit, self.revision_edit)
```

### 7.7 Keyboard Shortcuts in Tab

```python
save_btn.setShortcut(QKeySequence("Ctrl+S"))
open_btn.setShortcut(QKeySequence("Ctrl+O"))
new_btn.setShortcut(QKeySequence("Ctrl+N"))
```

---

## 8. Missing Data Fields

### 8.1 New Fields for `ProjectInfo`

| Field | Type | Default | UI Widget | Purpose |
|-------|------|---------|-----------|---------|
| `institution` | `str` | `"LTAD/UFU"` | `QLineEdit` | Laboratory / university name |
| `project_number` | `str` | `""` | `QLineEdit` | Engineering document control number |
| `revision` | `str` | `"A"` | `QLineEdit` (max 5) | Revision letter/number |
| `notes` | `str` | `""` | `QTextEdit` (small) | Free-text notes separate from description |
| `template_name` | `str` | `""` | Read-only label | Which template was applied |

### 8.2 Updated `ProjectInfo` Dataclass

```python
@dataclass
class ProjectInfo:
    # Identification
    name: str = "Untitled Project"
    description: str = ""
    author: str = ""
    company: str = "Petrobras"
    institution: str = "LTAD/UFU"          # NEW
    project_number: str = ""               # NEW
    revision: str = "A"                    # NEW
    notes: str = ""                        # NEW

    # Standards
    standard: str = "VDI 2230"
    material_standard: str = "ASTM A320"
    flange_standard: str = "API 6A"

    # Units
    length_unit: str = "mm"
    force_unit: str = "N"
    pressure_unit: str = "MPa"
    temperature_unit: str = "°C"

    # Timestamps
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    modified: str = field(default_factory=lambda: datetime.now().isoformat())

    # File
    filepath: Optional[str] = None
    template_name: str = ""                # NEW
```

**`to_dict()` / `from_dict()`:** Add all new fields, with `from_dict()` using `.get()` with defaults for backward compatibility:

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'ProjectInfo':
    return cls(
        name=data.get("name", "Untitled Project"),
        description=data.get("description", ""),
        author=data.get("author", ""),
        company=data.get("company", "Petrobras"),
        institution=data.get("institution", "LTAD/UFU"),          # NEW — safe default
        project_number=data.get("project_number", ""),            # NEW
        revision=data.get("revision", "A"),                       # NEW
        notes=data.get("notes", ""),                              # NEW
        standard=data.get("standard", "VDI 2230"),
        material_standard=data.get("material_standard", "ASTM A320"),
        flange_standard=data.get("flange_standard", "API 6A"),
        length_unit=data.get("length_unit", "mm"),
        force_unit=data.get("force_unit", "N"),
        pressure_unit=data.get("pressure_unit", "MPa"),
        temperature_unit=data.get("temperature_unit", "°C"),
        created=data.get("created", datetime.now().isoformat()),
        modified=data.get("modified", datetime.now().isoformat()),
        filepath=data.get("filepath"),
        template_name=data.get("template_name", ""),              # NEW
    )
```

---

## 9. New Components to Add

### 9.1 Hero Status Bar Widget

A `QFrame` with fixed height (48px) added as the first widget in the tab's `QVBoxLayout` (above the splitter).

```
ProjectTab (QVBoxLayout)
  ├── HeroBar (QFrame, fixedHeight=48)
  └── QSplitter
        ├── Left QScrollArea
        └── Right QWidget
```

**HeroBar content:**
- Left: App icon (16px) + "Bolt Analysis Studio v4.0" label + " — LTAD/UFU"
- Center: Project name (auto-updates via signal)
- Right: Status badge (`QLabel` with colored background) + [Save] button

### 9.2 Model Summary Card

A `QGroupBox("📊 Model Summary")` in the right panel, bottom area. Shows live statistics from `AppState.current_model` — updated via `model_changed` signal.

```
┌──────────────────────────────────┐
│ 📊 Model Summary                 │
│  Elements:  12     DOF:  36      │
│  k_sys:   1.23e8  N/m            │
│  Contacts:  8     Threads: 2     │
│  Status:  ✔ Valid                │
└──────────────────────────────────┘
```

**Update method:**
```python
def update_model_summary(self, model):
    if model is None:
        self._summary_elements.setText("—")
        ...
        return
    n_el = len(model.elements)
    n_dof = model.get_dof_count() if hasattr(model, 'get_dof_count') else "—"
    self._summary_elements.setText(str(n_el))
    self._summary_dof.setText(str(n_dof))
```

### 9.3 Project Templates

A `QGroupBox("📐 Templates")` with 4 preset buttons. Each applies a `ProjectInfo` template:

| Template | Standard | Bolt Std | Flange Std | Typical Use |
|----------|----------|----------|------------|-------------|
| Junker Test | VDI 2230 | ISO 898-1 | — | Self-loosening vibration test |
| API 6A Flange | VDI 2230 | ASTM A193 | API 6A | High-pressure oil & gas |
| ISO Metric Flange | EN 1591-1 | ISO 898-1 | EN 1092-1 | European pressure vessels |
| ASME Flange | ASME PCC-1 | ASTM A193 | ASME B16.5 | US pressure vessels |

```python
TEMPLATES = {
    "Junker Test": {
        "standard": "VDI 2230 Part 1 (2015)",
        "material_standard": "ISO 898-1:2013",
        "flange_standard": "—",
        "template_name": "Junker Test",
    },
    "API 6A Flange": {
        "standard": "VDI 2230 Part 1 (2015)",
        "material_standard": "ASTM A193/A193M",
        "flange_standard": "API 6A (2018)",
        "template_name": "API 6A Flange",
    },
    ...
}
```

### 9.4 Timestamps Display

A compact `QGroupBox("🕒 Project History")` or embedded as two read-only labels in the Project Info group:

```
Created:   2026-02-10  14:32:17
Modified:  2026-02-18  09:15:44
```

Use `datetime.fromisoformat(ts).strftime("%Y-%m-%d  %H:%M:%S")` for formatting.

---

## 10. ProjectInfo Dataclass Extension

### 10.1 Serialization Round-Trip Check

All new fields must be tested for save/load round-trip. Verify `.msd` JSON file integrity after adding fields:

```python
# In tests/test_project_info.py
def test_project_info_round_trip():
    info = ProjectInfo(
        name="Test", institution="UFU", project_number="P-001", revision="B"
    )
    d = info.to_dict()
    info2 = ProjectInfo.from_dict(d)
    assert info2.institution == "UFU"
    assert info2.project_number == "P-001"
    assert info2.revision == "B"

def test_project_info_backward_compatible():
    # Old file without new fields
    old_dict = {"name": "OldProject", "author": "Alice", "company": "ACME"}
    info = ProjectInfo.from_dict(old_dict)
    assert info.institution == "LTAD/UFU"   # uses default
    assert info.revision == "A"             # uses default
```

---

## 11. Signal & Data-Flow Improvements

### 11.1 New Signals in ProjectTab

```python
class ProjectTab(QWidget):
    # NEW signals
    project_info_changed = pyqtSignal(dict)    # fires on any field change
    open_recent_requested = pyqtSignal(str)    # fires on recent-item double-click
    template_requested = pyqtSignal(str)       # fires when template button clicked
    save_requested = pyqtSignal()              # fires when hero-bar Save clicked
```

### 11.2 `BoltAnalysisStudio` Connections (in `_connect_tab_buttons`)

```python
self.project_tab.open_recent_requested.connect(self._open_project_path)
self.project_tab.template_requested.connect(self._apply_project_template)
self.project_tab.save_requested.connect(self._save_project)
self.project_tab.project_info_changed.connect(self._mark_project_modified)
```

### 11.3 Project Status Tracking

```python
def _mark_project_modified(self, _=None):
    """Called whenever ProjectInfo or model changes."""
    state = get_app_state()
    state.is_modified = True
    self.project_tab.set_status("MODIFIED")
    self.tab_widget.setTabText(0, "1. 📁 Project ●")

def _mark_project_saved(self, path: str):
    state = get_app_state()
    state.is_modified = False
    self.project_tab.set_status("SAVED", path)
    self.tab_widget.setTabText(0, "1. 📁 Project")
```

### 11.4 Model Summary Live Updates

In `BoltAnalysisStudio._on_msd_builder_model_changed()`, after updating the solver tab, also call:

```python
self.project_tab.update_model_summary(self._current_model)
```

---

## 12. Implementation Priority Matrix

| # | Improvement | Impact | Effort | Risk | Priority |
|---|------------|--------|--------|------|----------|
| U1 | Fix fake Recent Projects — real persistence via QSettings | High | Medium | Low | **P0** |
| U2 | Double-click recent to open | High | Low | Low | **P0** |
| L4 | Expand description field (remove maxHeight=80) | High | Trivial | None | **P0** |
| R1 | Wrap panels in QSplitter | High | Low | Low | **P0** |
| R2 | Add QScrollArea to left panel | High | Low | Low | **P0** |
| V5 | Project status badge (New/Modified/Saved) | High | Medium | Low | **P1** |
| D1 | Add Institution field | Medium | Low | None | **P1** |
| D2 | Add Project Number field | Medium | Trivial | None | **P1** |
| D3 | Add Revision field | Medium | Trivial | None | **P1** |
| D5 | Display timestamps (Created / Modified) | Medium | Low | None | **P1** |
| U3 | Status badge in hero bar | Medium | Medium | Low | **P1** |
| U8 | Add tooltips to Standards combos | Medium | Trivial | None | **P1** |
| V1 | Hero/branding bar | Low | Medium | Low | **P2** |
| V2 | 2×2 Quick Actions grid | Medium | Low | None | **P2** |
| D7 | Project Templates section | Medium | Medium | Low | **P2** |
| D8 | Model Summary card (live) | Medium | Medium | Low | **P2** |
| U6 | Project Name validation | Medium | Low | None | **P2** |
| U7 | Units change warning | Low | Low | None | **P2** |
| V3 | Rich recent list (delegate) | Low | Medium | None | **P3** |
| D4 | Notes field | Low | Trivial | None | **P3** |
| U9 | Tab-order definition | Low | Trivial | None | **P3** |
| U10 | Auto-fill author from OS | Low | Trivial | None | **P3** |
| L7 | Move Units to same panel as Standards | Low | Low | None | **P3** |

---

## 13. PyQt6 Code Snippets

### 13.1 Hero Bar Frame

```python
def _create_hero_bar(self) -> QFrame:
    bar = QFrame()
    bar.setFixedHeight(52)
    bar.setObjectName("hero_bar")
    bar.setStyleSheet(f"""
        QFrame#hero_bar {{
            background-color: {Theme.MANTLE};
            border-bottom: 1px solid {Theme.SURFACE1};
        }}
    """)

    bar_layout = QHBoxLayout(bar)
    bar_layout.setContentsMargins(16, 0, 16, 0)
    bar_layout.setSpacing(12)

    # Left: branding
    app_label = QLabel("Bolt Analysis Studio v4.0")
    app_label.setStyleSheet(f"color: {Theme.SUBTEXT}; font-size: 12px;")

    # Center: project name
    self._hero_project_name = QLabel("Untitled Project")
    self._hero_project_name.setStyleSheet(
        f"color: {Theme.TEXT}; font-size: 14px; font-weight: bold;"
    )
    self._hero_project_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # Right: status badge + save
    self._status_badge = QLabel("NEW")
    self._status_badge.setFixedSize(80, 24)
    self._status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self._status_badge.setStyleSheet(f"""
        background-color: {Theme.TEAL};
        color: {Theme.BASE};
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    """)

    save_btn = QPushButton("Save")
    save_btn.setObjectName("primary")
    save_btn.setFixedWidth(80)
    save_btn.clicked.connect(self.save_requested.emit)

    bar_layout.addWidget(app_label)
    bar_layout.addStretch()
    bar_layout.addWidget(self._hero_project_name)
    bar_layout.addStretch()
    bar_layout.addWidget(self._status_badge)
    bar_layout.addWidget(save_btn)

    return bar

def set_status(self, status: str, path: str = ""):
    """Update hero bar status badge."""
    colors = {
        "NEW":      (Theme.TEAL, "NEW"),
        "MODIFIED": (Theme.PEACH, "UNSAVED"),
        "SAVED":    (Theme.GREEN, "SAVED"),
        "ERROR":    (Theme.RED,  "ERROR"),
    }
    bg, label = colors.get(status, (Theme.OVERLAY, status))
    self._status_badge.setText(label)
    self._status_badge.setStyleSheet(f"""
        background-color: {bg};
        color: {Theme.BASE};
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    """)
    if path:
        self._status_badge.setToolTip(path)
```

### 13.2 Quick Actions 2×2 Grid

```python
def _create_actions_group(self) -> QGroupBox:
    group = QGroupBox("⚡ Quick Actions")
    grid = QGridLayout(group)
    grid.setSpacing(8)

    new_btn  = QPushButton("New\nProject")
    open_btn = QPushButton("Open\nProject")
    save_btn = QPushButton("Save\nProject")
    exp_btn  = QPushButton("Export\nReport")

    new_btn.setIcon(QIcon.fromTheme("document-new"))
    open_btn.setIcon(QIcon.fromTheme("document-open"))
    save_btn.setIcon(QIcon.fromTheme("document-save"))
    exp_btn.setIcon(QIcon.fromTheme("document-export"))

    for btn in (new_btn, open_btn, save_btn, exp_btn):
        btn.setMinimumHeight(52)
        btn.setIconSize(QSize(20, 20))

    save_btn.setObjectName("primary")

    grid.addWidget(new_btn,  0, 0)
    grid.addWidget(open_btn, 0, 1)
    grid.addWidget(save_btn, 1, 0)
    grid.addWidget(exp_btn,  1, 1)

    return group
```

### 13.3 Recent Projects with QSettings

```python
def _load_recent_projects(self):
    """Populate list from QSettings."""
    self.recent_list.clear()
    s = QSettings("LTAD-UFU", "BoltAnalysisStudio")
    raw = s.value("recent_projects", "[]")
    items = json.loads(raw) if isinstance(raw, str) else []

    for entry in items:
        path = entry.get("path", "")
        name = entry.get("name", Path(path).stem if path else "Unknown")
        mod  = entry.get("modified_iso", "")
        try:
            mod_str = datetime.fromisoformat(mod).strftime("%Y-%m-%d")
        except Exception:
            mod_str = "Unknown date"

        item = QListWidgetItem(f"  {name}")
        item.setData(Qt.ItemDataRole.UserRole, path)
        item.setToolTip(f"{path}\nModified: {mod_str}")

        if path and not Path(path).exists():
            item.setForeground(QColor(Theme.OVERLAY))
            item.setText(f"  {name}  [not found]")

        self.recent_list.addItem(item)

    self.recent_list.itemDoubleClicked.connect(self._on_recent_double_click)

def _on_recent_double_click(self, item: QListWidgetItem):
    path = item.data(Qt.ItemDataRole.UserRole)
    if path and Path(path).exists():
        self.open_recent_requested.emit(path)
    else:
        QMessageBox.warning(self, "File Not Found",
                            f"Could not find:\n{path}")
```

### 13.4 Timestamps Display

```python
def _create_timestamps_widget(self) -> QWidget:
    w = QWidget()
    layout = QFormLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)

    self._created_label  = QLabel("—")
    self._modified_label = QLabel("—")

    for lbl in (self._created_label, self._modified_label):
        lbl.setStyleSheet(f"color: {Theme.SUBTEXT}; font-size: 11px;")

    layout.addRow("Created:",  self._created_label)
    layout.addRow("Modified:", self._modified_label)
    return w

def _update_timestamps(self, info: ProjectInfo):
    fmt = "%Y-%m-%d  %H:%M"
    try:
        c = datetime.fromisoformat(info.created).strftime(fmt)
        m = datetime.fromisoformat(info.modified).strftime(fmt)
    except Exception:
        c = m = "—"
    self._created_label.setText(c)
    self._modified_label.setText(m)
```

---

## Summary of Key Recommendations

1. **P0 — Fix Recent Projects immediately.** The fake hardcoded list is a significant UX defect that damages trust in the application.

2. **P0 — Add QSplitter + QScrollArea.** The fixed layout breaks on screens below 1400px wide or 800px tall — a common laptop resolution.

3. **P0 — Expand description field.** 80px max-height is insufficient. Users cannot read or write meaningful descriptions.

4. **P1 — Status badge.** Engineers need immediate visual confirmation of "is my work saved?" — this is a basic data-safety concern.

5. **P1 — Add Institution, Project Number, Revision fields.** These are standard in engineering document control and are expected by the Petrobras/UFU user base.

6. **P1 — Display timestamps.** The data is already in `ProjectInfo` — show it.

7. **P2 — 2×2 Quick Actions grid + hero bar.** Low effort, high polish.

8. **P2 — Project templates.** Dramatically speeds up onboarding new users.

9. **P2 — Model Summary card.** Provides contextual awareness without switching tabs.

---

*Document prepared by Claude Code for LTAD/UFU — Bolt Analysis Studio v4.0*
*Date: 2026-02-18*
