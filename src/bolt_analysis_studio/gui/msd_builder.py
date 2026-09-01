"""
MSD Model Builder Beta - Grid-Based Visual Schematic Editor
Bolt Analysis Studio v4.0

Features:
- Grid-based element placement (row=series, column=parallel)
- Contact interface definition dialog
- Thread fillet model with exponential load decay
- Load/constraint application system
- Load flow visualization

Prof. Leonardo Rosa Ribeiro da Silva, PhD
January 2026
"""

import sys
import math
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from collections import defaultdict

import numpy as np

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
    QGraphicsLineItem, QGraphicsTextItem, QGraphicsEllipseItem,
    QGraphicsPathItem, QLabel, QPushButton, QComboBox, QSpinBox,
    QDoubleSpinBox, QGroupBox, QFormLayout, QScrollArea, QSplitter,
    QFrame, QToolBar, QStatusBar, QMessageBox, QDialog, QDialogButtonBox,
    QTabWidget, QSlider, QCheckBox, QToolButton, QButtonGroup,
    QSizePolicy, QLineEdit, QTextEdit, QProgressBar,
    QTreeWidget, QTreeWidgetItem, QRadioButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPointF, QPoint, QLineF, QTimer, QSize
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QPainter, QFont, QAction, QKeySequence,
    QPainterPath, QLinearGradient, QRadialGradient, QScreen,
    QUndoStack, QUndoCommand, QShortcut
)
from PyQt6.QtWidgets import QMenu

# Import from project
from bolt_analysis_studio.core.models.element import (
    ElementType, MSDElementData, GridPosition, ContactInterface, ContactType,
    SpecificContactType, ThreadFilletModel, AppliedLoad, Constraint,
    TimeVariation, ConstraintType, ConnectionType, LoadingType, LoadingData,
    create_bolt_head, create_bolt_shank, create_thread_element,
    create_nut, create_flange, create_gasket, create_washer, create_ground
)
from bolt_analysis_studio.core.models.model import MSDModel
from bolt_analysis_studio.core.databases.materials_database import (
    get_all_grade_names, get_grade_key_from_display,
    get_properties_for_grade, get_stress_area_from_threads,
    get_standard_pitch_for_diameter, get_thread_geometry,
    MATERIALS_DATABASE,
)

from bolt_analysis_studio.gui.theme import Theme


# =============================================================================
# ELEMENT VISUAL CONFIG
# =============================================================================

@dataclass
class ElementVisual:
    """Visual configuration for element types."""
    name: str
    symbol: str
    color: str
    description: str
    default_k: float
    default_c: float
    default_m: float


ELEMENT_VISUALS = {
    # Bolt Elements
    "HEAD": ElementVisual("Bolt Head", "⬡", Theme.BLUE, "Bolt head with bearing surface", 1.85e9, 100, 0.022),
    "SHANK": ElementVisual("Shank", "║", Theme.BLUE, "Unthreaded bolt shank", 2.32e9, 100, 0.019),
    "NUT": ElementVisual("Nut", "⬢", Theme.GREEN, "Nut with thread engagement", 1.5e9, 100, 0.018),
    "WASHER": ElementVisual("Washer", "◯", Theme.MAUVE, "Flat/spring washer", 5e9, 50, 0.005),

    # Member Elements
    "FLANGE": ElementVisual("Flange", "▭", Theme.TEAL, "Clamped flange member", 3e9, 200, 0.5),
    "GASKET": ElementVisual("Gasket", "≋", Theme.PEACH, "Compressible gasket", 5e8, 500, 0.02),

    # Contact Elements (Interface types)
    "THREAD": ElementVisual("Thread", "⫰", Theme.YELLOW, "Threaded portion of bolt (stud)", 6.6e7, 100, 0.005),
    "BEARING_HEAD": ElementVisual("Bearing (Head)", "⊡", Theme.RED, "Bolt head bearing interface", 1e10, 100, 0.001),
    "BEARING_NUT": ElementVisual("Bearing (Nut)", "⊞", Theme.RED, "Nut bearing interface", 1e10, 100, 0.001),
    "FLANGE_FLANGE": ElementVisual("Flange-Flange", "▭▭", Theme.MAUVE, "Metal-to-metal flange contact", 1e10, 100, 0.001),
    "WASHER_CONTACT": ElementVisual("Washer Contact", "◎", Theme.MAUVE, "Washer bearing interface", 8e9, 80, 0.001),
    "GASKET_CONTACT": ElementVisual("Gasket Contact", "≈", Theme.PEACH, "Gasket compression interface", 5e8, 500, 0.02),
    "GENERIC_CONTACT": ElementVisual("Generic Contact", "⋈", Theme.RED, "General interface contact", 1e10, 100, 0.001),

    # Boundary
    "GROUND": ElementVisual("Ground", "⏚", Theme.OVERLAY, "Fixed boundary", 1e15, 100, 0.01),
}


def _fmt_eng(value: float, unit: str = "") -> str:
    """Format value in engineering notation with SI prefix (k/M/G)."""
    if value == 0:
        return f"0 {unit}".strip()
    abs_v = abs(value)
    if abs_v >= 1e9:
        return f"{value/1e9:.2f} G{unit}"
    elif abs_v >= 1e6:
        return f"{value/1e6:.2f} M{unit}"
    elif abs_v >= 1e3:
        return f"{value/1e3:.2f} k{unit}"
    elif abs_v >= 1:
        return f"{value:.2f} {unit}".strip()
    else:
        return f"{value:.2e} {unit}".strip()


# =============================================================================
# UNDO / REDO COMMANDS (QUndoCommand pattern)
# =============================================================================

class AddElementCommand(QUndoCommand):
    """Undoable command for adding an element to the schematic."""

    def __init__(self, schematic: 'SchematicView', element_type: str,
                 row: int = None, col: int = None, description: str = ""):
        super().__init__(description or f"Add {element_type}")
        self._schematic = schematic
        self._element_type = element_type
        self._row = row
        self._col = col
        self._element_id: Optional[int] = None
        self._element_data: Optional[MSDElementData] = None
        self._first_redo = True

    def redo(self):
        if self._first_redo:
            # First execution: add normally and capture the created element
            item = self._schematic.add_element(
                self._element_type, self._row, self._col
            )
            self._element_id = item.element_id
            self._element_data = item.element_data
            self._row = item.grid_row
            self._col = item.grid_col
            self._first_redo = False
        else:
            # Re-do: restore from saved data
            self._schematic.restore_element(self._element_data)

    def undo(self):
        if self._element_id is not None:
            self._schematic.remove_element(self._element_id)


class RemoveElementCommand(QUndoCommand):
    """Undoable command for removing an element from the schematic."""

    def __init__(self, schematic: 'SchematicView', element_id: int,
                 description: str = ""):
        item = schematic.elements.get(element_id)
        label = item.element_data.name if item else str(element_id)
        super().__init__(description or f"Delete {label}")
        self._schematic = schematic
        self._element_id = element_id
        # Snapshot the element data before removal
        self._element_data: Optional[MSDElementData] = None
        if item:
            self._element_data = item.element_data

    def redo(self):
        self._schematic.remove_element(self._element_id)

    def undo(self):
        if self._element_data is not None:
            self._schematic.restore_element(self._element_data)


class MoveElementCommand(QUndoCommand):
    """Undoable command for moving an element to a new grid position."""

    def __init__(self, schematic: 'SchematicView', element_id: int,
                 old_row: int, old_col: int, new_row: int, new_col: int):
        super().__init__(f"Move element #{element_id}")
        self._schematic = schematic
        self._element_id = element_id
        self._old_row = old_row
        self._old_col = old_col
        self._new_row = new_row
        self._new_col = new_col

    def redo(self):
        self._move_to(self._new_row, self._new_col)

    def undo(self):
        self._move_to(self._old_row, self._old_col)

    def _move_to(self, row: int, col: int):
        item = self._schematic.elements.get(self._element_id)
        if item is None:
            return
        # Remove from old grid slot
        old_r, old_c = item.grid_row, item.grid_col
        if old_r in self._schematic.grid and old_c in self._schematic.grid[old_r]:
            del self._schematic.grid[old_r][old_c]
        # Place at new position
        item.set_grid_position(row, col)
        self._schematic.grid[row][col] = self._element_id
        self._schematic._rebuild_connections()
        self._schematic.model_changed.emit()


class ChangePropertyCommand(QUndoCommand):
    """Undoable command for changing an element property.

    The edit is normally *already applied* by the PropertyInspector handler
    that constructs this command; the first ``redo()`` (fired by
    ``QUndoStack.push``) is therefore a no-op so the value is not applied
    twice.  Subsequent ``redo()`` / ``undo()`` (Ctrl+Y / Ctrl+Z) replay the
    new / old value.  When ``inspector`` is given, the inspector spinboxes are
    re-synced on replay — guarded by ``set_element``'s own ``_updating`` flag,
    so the refresh can never re-enter the spinbox handlers (no signal loop).
    """

    def __init__(self, schematic: 'SchematicView', element_id: int,
                 prop_name: str, old_value, new_value, inspector=None):
        super().__init__(f"Change {prop_name} on #{element_id}")
        self._schematic = schematic
        self._element_id = element_id
        self._prop_name = prop_name
        self._old_value = old_value
        self._new_value = new_value
        self._inspector = inspector
        self._first_redo = True
        # Consecutive edits to the SAME (element, property) coalesce into one
        # undo step so typing a multi-digit value in a spinbox (which emits
        # valueChanged per keystroke) is not N separate undos.
        self._merge_id = hash((element_id, prop_name)) & 0x7FFFFFFF

    def id(self):
        return self._merge_id

    def mergeWith(self, other):
        # Guard against hash collisions between different (element, property).
        if (getattr(other, '_element_id', None) != self._element_id
                or getattr(other, '_prop_name', None) != self._prop_name):
            return False
        self._new_value = other._new_value
        return True

    def redo(self):
        # The handler already applied the change on first push; only replay
        # on a genuine redo (Ctrl+Y) after an undo.
        if self._first_redo:
            self._first_redo = False
            return
        self._apply(self._new_value)

    def undo(self):
        self._apply(self._old_value)

    def _apply(self, value):
        item = self._schematic.elements.get(self._element_id)
        if item is None:
            return
        data = item.element_data
        # Navigate dotted property paths like "msd.k"
        parts = self._prop_name.split(".")
        obj = data
        for part in parts[:-1]:
            obj = getattr(obj, part, None)
            if obj is None:
                return
        setattr(obj, parts[-1], value)
        item.update_display()
        # Keep the inspector spinboxes in sync when this element is on screen.
        insp = self._inspector
        if insp is not None:
            cur = getattr(insp, 'current_element', None)
            if cur is not None and cur.element_id == self._element_id:
                insp.set_element(item)
        self._schematic.model_changed.emit()


class ChangePreloadCommand(QUndoCommand):
    """Undoable preload edit — percent-yield and its derived force move together.

    Like :class:`ChangePropertyCommand` the edit is already applied by the
    handler (first redo is a no-op), the inspector is re-synced on replay, and
    consecutive preload edits on the same element coalesce into one undo step.
    """

    def __init__(self, schematic: 'SchematicView', element_id: int,
                 old_pct, new_pct, old_force, new_force, inspector=None):
        super().__init__(f"Change preload on #{element_id}")
        self._schematic = schematic
        self._element_id = element_id
        self._old_pct = old_pct
        self._new_pct = new_pct
        self._old_force = old_force
        self._new_force = new_force
        self._inspector = inspector
        self._first_redo = True
        self._merge_id = hash((element_id, "preload")) & 0x7FFFFFFF

    def id(self):
        return self._merge_id

    def mergeWith(self, other):
        if (not isinstance(other, ChangePreloadCommand)
                or other._element_id != self._element_id):
            return False
        self._new_pct = other._new_pct
        self._new_force = other._new_force
        return True

    def redo(self):
        if self._first_redo:
            self._first_redo = False
            return
        self._apply(self._new_pct, self._new_force)

    def undo(self):
        self._apply(self._old_pct, self._old_force)

    def _apply(self, pct, force):
        item = self._schematic.elements.get(self._element_id)
        if item is None:
            return
        data = item.element_data
        data.preload_percent_yield = pct
        data.preload_force = force
        item.update_display()
        insp = self._inspector
        if insp is not None:
            cur = getattr(insp, 'current_element', None)
            if cur is not None and cur.element_id == self._element_id:
                insp.set_element(item)
        self._schematic.model_changed.emit()


class GridPositionCommand(QUndoCommand):
    """Undoable grid move — restores every element's (row, col) snapshot.

    Faithful for single-element drags *and* multi-element rearrangements
    (port-drag row-gap insertion, series / parallel connect) because it stores
    the full before/after position map rather than a single delta.  The move
    itself is performed by the drag / connect code, so the first ``redo()`` is a
    no-op; ``undo()`` / redo replay the snapshots.
    """

    def __init__(self, schematic: 'SchematicView', before: dict, after: dict,
                 description: str = "Move element"):
        super().__init__(description)
        self._schematic = schematic
        self._before = dict(before)
        self._after = dict(after)
        self._first_redo = True

    def redo(self):
        if self._first_redo:
            self._first_redo = False
            return
        self._apply(self._after)

    def undo(self):
        self._apply(self._before)

    def _apply(self, positions: dict):
        for eid, (row, col) in positions.items():
            item = self._schematic.elements.get(eid)
            if item is not None:
                item.set_grid_position(row, col)
        self._schematic._sync_grid_from_items()
        self._schematic.model_changed.emit()


class DuplicateElementCommand(QUndoCommand):
    """Undoable duplicate — the copy already exists; undo removes it, redo
    restores it (same pattern as :class:`AddElementCommand`)."""

    def __init__(self, schematic: 'SchematicView', new_item,
                 description: str = ""):
        super().__init__(description or f"Duplicate element #{new_item.element_id}")
        self._schematic = schematic
        self._element_id = new_item.element_id
        self._element_data = new_item.element_data
        self._first_redo = True

    def redo(self):
        if self._first_redo:
            self._first_redo = False
            return  # already created by duplicate_element()
        self._schematic.restore_element(self._element_data)

    def undo(self):
        self._schematic.remove_element(self._element_id)


class SchematicStateCommand(QUndoCommand):
    """Undoable whole-schematic state swap (clear-all, expand-threads, ...).

    Stores a *before* and *after* snapshot of the element / contact state and
    replays whichever side is needed.  ``skip_first_redo`` covers the case
    where the caller has already produced the *after* state (e.g. after
    expanding threads), so the initial push must not rebuild it.
    """

    def __init__(self, schematic: 'SchematicView', before: dict, after: dict,
                 description: str, skip_first_redo: bool = False):
        super().__init__(description)
        self._schematic = schematic
        self._before = before
        self._after = after
        self._skip = skip_first_redo

    def redo(self):
        if self._skip:
            self._skip = False
            return
        self._schematic._restore_state(self._after)

    def undo(self):
        self._schematic._restore_state(self._before)


# =============================================================================
# GRID CONFIGURATION (base values, scaled by DPI)
# =============================================================================

def get_grid_scale() -> float:
    """Get DPI scale factor."""
    app = QApplication.instance()
    if app:
        screen = app.primaryScreen()
        if screen:
            return screen.logicalDotsPerInch() / 96.0
    return 1.0

# Base grid dimensions (will be scaled)
_BASE_CELL_WIDTH = 120
_BASE_CELL_HEIGHT = 80
_BASE_MARGIN = 20

def get_grid_cell_width() -> int:
    return int(_BASE_CELL_WIDTH * get_grid_scale())

def get_grid_cell_height() -> int:
    return int(_BASE_CELL_HEIGHT * get_grid_scale())

def get_grid_margin() -> int:
    return int(_BASE_MARGIN * get_grid_scale())

# Legacy constants for compatibility
GRID_CELL_WIDTH = _BASE_CELL_WIDTH
GRID_CELL_HEIGHT = _BASE_CELL_HEIGHT
GRID_MARGIN = _BASE_MARGIN


# =============================================================================
# GRAPHICS ITEMS
# =============================================================================

class ForceArrowItem(QGraphicsPathItem):
    """Visual arrow indicating applied force direction on an element.

    Arrow types:
    - axial:      vertical straight arrow (down/up)
    - transverse: horizontal straight arrow (right/left)
    - torque:     curved circular arrow
    - bending:    angled moment arrow
    - preload:    bold downward arrow (preload force)
    """

    ARROW_SIZE = 8   # arrowhead size
    SHAFT_LEN = 22   # shaft length

    def __init__(self, parent_item, load_type: str = "axial",
                 magnitude: float = 0.0):
        super().__init__(parent_item)
        self.load_type = load_type
        self.magnitude = magnitude
        self._build_arrow()

    def _build_arrow(self):
        """Build the arrow path based on load type."""
        path = QPainterPath()
        a = self.ARROW_SIZE
        s = self.SHAFT_LEN

        if self.load_type in ("axial", "preload"):
            # Vertical arrow pointing down
            path.moveTo(0, 0)
            path.lineTo(0, s)
            # Arrowhead
            path.moveTo(-a / 2, s - a)
            path.lineTo(0, s)
            path.lineTo(a / 2, s - a)

        elif self.load_type == "transverse":
            # Horizontal arrow pointing right
            path.moveTo(0, 0)
            path.lineTo(s, 0)
            # Arrowhead
            path.moveTo(s - a, -a / 2)
            path.lineTo(s, 0)
            path.lineTo(s - a, a / 2)

        elif self.load_type == "torque":
            # Curved arrow (arc with arrowhead)
            r = s * 0.5
            # Draw arc from 30 to 300 degrees
            rect = QRectF(-r, -r, 2 * r, 2 * r)
            path.arcMoveTo(rect, 30)
            path.arcTo(rect, 30, 240)
            # Arrowhead at the end of the arc
            end = path.currentPosition()
            path.moveTo(end.x() - a * 0.6, end.y() - a * 0.5)
            path.lineTo(end)
            path.lineTo(end.x() + a * 0.3, end.y() - a * 0.7)

        elif self.load_type == "bending":
            # Curved moment arc arrow (↷)
            import math as _math
            r = s * 0.45
            rect = QRectF(-r, -r, 2 * r, 2 * r)
            path.arcMoveTo(rect, 150)
            path.arcTo(rect, 150, -240)
            end = path.currentPosition()
            # Small arrowhead at arc end
            tang_angle = _math.radians(150 - 240 - 90)
            path.moveTo(end.x() - a * 0.6 * _math.cos(tang_angle - 0.4),
                        end.y() - a * 0.6 * _math.sin(tang_angle - 0.4))
            path.lineTo(end)
            path.lineTo(end.x() - a * 0.6 * _math.cos(tang_angle + 0.4),
                        end.y() - a * 0.6 * _math.sin(tang_angle + 0.4))

        elif self.load_type == "impact":
            # Zigzag lightning-bolt arrow (⚡) pointing downward
            z = s * 0.35   # zigzag half-width
            path.moveTo(0, 0)
            path.lineTo(z,  s * 0.35)
            path.lineTo(0,  s * 0.45)
            path.lineTo(z * 0.6, s * 0.75)
            path.lineTo(0, s * 0.75)
            # Arrowhead
            path.moveTo(-a / 2, s - a)
            path.lineTo(0, s)
            path.lineTo(a / 2, s - a)

        else:
            # Combined / generic: small cross-arrows
            h = s * 0.5
            # Vertical
            path.moveTo(0, -h)
            path.lineTo(0, h)
            path.moveTo(-a / 2, h - a)
            path.lineTo(0, h)
            path.lineTo(a / 2, h - a)
            # Horizontal
            path.moveTo(-h, 0)
            path.lineTo(h, 0)
            path.moveTo(h - a, -a / 2)
            path.lineTo(h, 0)
            path.lineTo(h - a, a / 2)

        self.setPath(path)
        self._apply_style()

    def _apply_style(self):
        """Apply pen style based on load type."""
        if self.load_type == "preload":
            color = QColor(Theme.GREEN)
            width = 2.5
        elif self.load_type == "torque":
            color = QColor(Theme.MAUVE)
            width = 2.0
        elif self.load_type == "transverse":
            color = QColor(Theme.PEACH)
            width = 2.0
        elif self.load_type == "bending":
            color = QColor(Theme.YELLOW)
            width = 2.0
        elif self.load_type == "impact":
            color = QColor(Theme.RED)
            width = 2.5
        else:
            color = QColor(Theme.RED)
            width = 2.0

        pen = QPen(color)
        pen.setWidth(int(width))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        self.setPen(pen)
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))

    def update_style(self):
        """Refresh colors after theme change."""
        self._apply_style()


class ElementGraphicsItem(QGraphicsRectItem):
    """Graphical representation of an MSD element on the grid."""

    def __init__(self, element_data: MSDElementData, parent=None):
        w = get_grid_cell_width() - 20   # leave margin within grid cell
        h = get_grid_cell_height() - 20
        super().__init__(0, 0, w, h, parent)

        self.element_data = element_data
        self.element_id = element_data.id
        self.element_type = element_data.type.name
        self.visual = ELEMENT_VISUALS.get(self.element_type, ELEMENT_VISUALS["SHANK"])

        # Grid position
        self.grid_row = element_data.grid_position.row
        self.grid_col = element_data.grid_position.column

        # Set position from grid
        self._update_position_from_grid()

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        # Visual setup
        self._setup_visual()

        # Validation state (3.18 — inline badges)
        self._val_errors: List[str] = []
        self._val_warnings: List[str] = []

    def set_validation_state(self, errors: List[str], warnings: List[str]):
        """Set per-element validation messages; triggers repaint (3.18)."""
        self._val_errors = errors
        self._val_warnings = warnings
        # Update tooltip to show first error/warning
        if errors:
            self.setToolTip(f"⚠ {errors[0]}")
        elif warnings:
            self.setToolTip(f"⚑ {warnings[0]}")
        else:
            self.setToolTip(self.visual.description)
        self.update()

    def _update_position_from_grid(self):
        """Update pixel position from grid coordinates."""
        margin = get_grid_margin()
        x = margin + self.grid_col * get_grid_cell_width()
        y = margin + self.grid_row * get_grid_cell_height()
        self.setPos(x, y)

    def set_grid_position(self, row: int, col: int):
        """Set grid position and update visual."""
        self.grid_row = row
        self.grid_col = col
        self.element_data.grid_position.row = row
        self.element_data.grid_position.column = col
        self._update_position_from_grid()

    def _setup_visual(self):
        """Setup visual appearance."""
        # Background
        color = QColor(self.visual.color)
        color.setAlpha(40)
        self.setBrush(QBrush(color))

        # Border
        pen = QPen(QColor(self.visual.color))
        pen.setWidth(2)
        self.setPen(pen)

        # Type label
        self.type_label = QGraphicsTextItem(f"{self.visual.symbol} {self.visual.name}", self)
        self.type_label.setDefaultTextColor(QColor(Theme.TEXT))
        self.type_label.setPos(5, 2)
        font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        self.type_label.setFont(font)

        # Stiffness label
        k = self.element_data.msd.k
        self.k_label = QGraphicsTextItem(f"k={_fmt_eng(k, 'N/m')}", self)
        self.k_label.setDefaultTextColor(QColor(Theme.SUBTEXT))
        self.k_label.setPos(5, 22)
        self.k_label.setFont(QFont("Consolas", 8))

        # ID label
        self.id_label = QGraphicsTextItem(f"#{self.element_id}", self)
        self.id_label.setDefaultTextColor(QColor(Theme.OVERLAY))
        self.id_label.setPos(5, 40)
        self.id_label.setFont(QFont("Consolas", 8))

        # Force arrow indicators (shown when loads applied)
        self.force_arrows: List[ForceArrowItem] = []
        self._update_force_arrows()

        # Yield utilization indicator
        w = self.rect().width()
        h = self.rect().height()
        self.yield_label = QGraphicsTextItem("", self)
        self.yield_label.setPos(w - 40, h - 16)
        self.yield_label.setFont(QFont("Consolas", 7))
        self._update_yield_indicator()

        # Connection ports (visible on hover)
        self.port_top = ConnectionPort(self, "top")
        self.port_bottom = ConnectionPort(self, "bottom")

        self.setAcceptHoverEvents(True)

    def _update_yield_indicator(self):
        """Update the yield % label color based on utilization."""
        pct = self.element_data.preload_percent_yield
        if pct <= 0:
            self.yield_label.setPlainText("")
            return
        self.yield_label.setPlainText(f"{pct:.0f}%")
        if pct < 60:
            self.yield_label.setDefaultTextColor(QColor(Theme.GREEN))
        elif pct < 80:
            self.yield_label.setDefaultTextColor(QColor(Theme.YELLOW))
        else:
            self.yield_label.setDefaultTextColor(QColor(Theme.RED))

    def _update_force_arrows(self):
        """Create/update force arrow indicators based on applied loads and preload."""
        # Remove old arrows
        for arrow in self.force_arrows:
            if arrow.scene():
                arrow.scene().removeItem(arrow)
        self.force_arrows.clear()

        w = self.rect().width()
        h = self.rect().height()
        arrow_x = w - 12   # right side of element
        arrow_y = 4         # top area

        # Show preload arrow if this element has preload force
        if self.element_data.preload_force > 0:
            arrow = ForceArrowItem(self, "preload", self.element_data.preload_force)
            arrow.setPos(arrow_x, arrow_y)
            arrow.setToolTip(f"Preload: {self.element_data.preload_force / 1000:.1f} kN")
            self.force_arrows.append(arrow)
            arrow_x -= 18

        # Show arrows for each applied load
        for load in self.element_data.applied_loads:
            direction = getattr(load, 'direction', 'axial')
            load_type_str = getattr(load, 'load_type', 'force')
            mag = getattr(load, 'magnitude', 0.0)

            if load_type_str in ("torsion", "moment") or direction == "torsional":
                arrow_type = "torque"
            elif load_type_str == "shear" or direction in ("transverse", "y", "z"):
                arrow_type = "transverse"
            elif load_type_str == "bending":
                arrow_type = "bending"
            elif load_type_str == "impact":
                arrow_type = "impact"
            else:
                arrow_type = "axial"

            arrow = ForceArrowItem(self, arrow_type, mag)
            arrow.setPos(arrow_x, arrow_y)
            label = f"{load_type_str.title()}: {mag:.0f}"
            if arrow_type == "torque":
                label += " N.m"
            else:
                label += " N"
            if direction != "axial":
                label += f" ({direction})"
            arrow.setToolTip(label)
            self.force_arrows.append(arrow)
            arrow_x -= 18

    def update_display(self):
        """Update display after data changes."""
        self.type_label.setPlainText(f"{self.visual.symbol} {self.visual.name}")
        self.k_label.setPlainText(f"k={_fmt_eng(self.element_data.msd.k, 'N/m')}")

        # Update force arrows
        self._update_force_arrows()

        # Update yield indicator
        self._update_yield_indicator()

    def hoverEnterEvent(self, event):
        """Show connection ports on hover."""
        self.port_top.show_port()
        self.port_bottom.show_port()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Hide connection ports on hover leave."""
        self.port_top.hide_port()
        self.port_bottom.hide_port()
        super().hoverLeaveEvent(event)

    def itemChange(self, change, value):
        """Handle item changes for snapping to grid."""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            # Snap to grid on move
            new_pos = value
            cw, ch, margin = get_grid_cell_width(), get_grid_cell_height(), get_grid_margin()
            col = round((new_pos.x() - margin) / cw)
            row = round((new_pos.y() - margin) / ch)
            col = max(0, col)
            row = max(0, row)

            snapped_x = margin + col * cw
            snapped_y = margin + row * ch

            self.grid_row = row
            self.grid_col = col

            # Ask the view to expand the scene if near boundaries
            view = self.scene().views()[0] if self.scene().views() else None
            if view and hasattr(view, '_ensure_scene_fits'):
                view._ensure_scene_fits(row, col)

            return QPointF(snapped_x, snapped_y)

        return super().itemChange(change, value)

    def paint(self, painter, option, widget):
        """Custom paint with rounded corners and selection highlight."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect()
        radius = 8.0
        # Fill
        painter.setBrush(self.brush())
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(r, radius, radius)
        # Border
        painter.setPen(self.pen())
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(r, radius, radius)
        if self.isSelected():
            painter.setPen(QPen(QColor(Theme.YELLOW), 3, Qt.PenStyle.DashLine))
            painter.drawRoundedRect(r, radius, radius)

        # 3.5 — Zoom-aware type abbreviation at bottom-centre
        _ABBREV = {
            "HEAD": "HD", "SHANK": "SHK", "THREAD": "THD", "NUT": "NUT",
            "WASHER": "WSH", "FLANGE": "FLG", "GASKET": "GSK", "GROUND": "GND",
            "BEARING_HEAD": "BRG", "BEARING_NUT": "BRN",
            "FLANGE_FLANGE": "F-F", "WASHER_CONTACT": "W-C",
            "GASKET_CONTACT": "G-C", "GENERIC_CONTACT": "CTT",
        }
        views = self.scene().views() if self.scene() else []
        view_scale = views[0].transform().m11() if views else 1.0
        if view_scale >= 0.9:
            abbrev = _ABBREV.get(self.element_type, "")
            if abbrev:
                painter.save()
                painter.setFont(QFont("Monospace", 6))
                painter.setPen(QColor(Theme.SUBTEXT))
                painter.drawText(
                    QRectF(r.left(), r.bottom() - 14, r.width(), 14),
                    Qt.AlignmentFlag.AlignCenter, abbrev
                )
                painter.restore()

        # 3.18 — Per-element validation badge (top-left corner)
        if self._val_errors:
            painter.save()
            badge_r = QRectF(r.left() + 2, r.top() + 2, 14, 14)
            painter.setBrush(QBrush(QColor(Theme.RED)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(badge_r)
            painter.setPen(QColor("white"))
            painter.setFont(QFont("Monospace", 7, QFont.Weight.Bold))
            painter.drawText(badge_r, Qt.AlignmentFlag.AlignCenter, "!")
            painter.restore()
        elif self._val_warnings:
            painter.save()
            badge_r = QRectF(r.left() + 2, r.top() + 2, 14, 14)
            painter.setBrush(QBrush(QColor(Theme.YELLOW)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(badge_r)
            painter.setPen(QColor(Theme.BASE))
            painter.setFont(QFont("Monospace", 7, QFont.Weight.Bold))
            painter.drawText(badge_r, Qt.AlignmentFlag.AlignCenter, "⚑")
            painter.restore()


class ConnectionLine(QGraphicsPathItem):
    """Connection line between elements with series/parallel indication."""

    def __init__(self, start_item: ElementGraphicsItem, end_item: ElementGraphicsItem,
                 is_parallel: bool = False, has_contact: bool = False):
        super().__init__()

        self.start_item = start_item
        self.end_item = end_item
        self.is_parallel = is_parallel
        self.has_contact = has_contact

        self._setup_style()
        self.setZValue(-1)  # Behind elements
        self.update_path()

    def _setup_style(self):
        """Setup line style based on connection type."""
        if self.has_contact:
            # Contact interface - thicker, highlighted
            pen = QPen(QColor(Theme.RED), 3, Qt.PenStyle.SolidLine)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        elif self.is_parallel:
            # Parallel connection - dashed orange
            pen = QPen(QColor(Theme.PEACH), 2.5, Qt.PenStyle.DashLine)
            pen.setDashPattern([6, 3])
        else:
            # Series connection - solid blue with gradient effect
            pen = QPen(QColor(Theme.BLUE), 2.5, Qt.PenStyle.SolidLine)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        self.setPen(pen)

    def set_has_contact(self, has_contact: bool):
        """Update contact status."""
        self.has_contact = has_contact
        self._setup_style()
        self.update()

    def update_path(self):
        """Update the connection path with improved visuals."""
        if not self.start_item or not self.end_item:
            return

        start_rect = self.start_item.sceneBoundingRect()
        end_rect = self.end_item.sceneBoundingRect()

        # Connection points at bottom of start and top of end
        start_pt = QPointF(start_rect.center().x(), start_rect.bottom())
        end_pt = QPointF(end_rect.center().x(), end_rect.top())

        path = QPainterPath()
        path.moveTo(start_pt)

        if self.is_parallel:
            # Parallel: smooth curved path
            mid_y = (start_pt.y() + end_pt.y()) / 2
            ctrl_offset = abs(start_pt.x() - end_pt.x()) * 0.3

            # Bezier curve for smooth transition
            path.cubicTo(
                start_pt.x(), mid_y,
                end_pt.x(), mid_y,
                end_pt.x(), end_pt.y()
            )
        else:
            # Series: smooth vertical connection with slight curve
            mid_y = (start_pt.y() + end_pt.y()) / 2

            if abs(start_pt.x() - end_pt.x()) < 5:
                # Nearly aligned - straight line
                path.lineTo(end_pt)
            else:
                # Offset - use bezier for smooth connection
                path.cubicTo(
                    start_pt.x(), mid_y,
                    end_pt.x(), mid_y,
                    end_pt.x(), end_pt.y()
                )

        self.setPath(path)

        # Add arrow head at end
        self._add_arrow_head(path)

    def _add_arrow_head(self, path: QPainterPath):
        """Add arrow head to indicate flow direction."""
        if path.isEmpty():
            return

        # Get end point and direction
        end_pt = path.currentPosition()
        length = path.length()
        if length < 20:
            return

        # Get point slightly before end to calculate direction
        t = max(0, (length - 15) / length)
        before_pt = path.pointAtPercent(t)

        # Calculate arrow direction
        dx = end_pt.x() - before_pt.x()
        dy = end_pt.y() - before_pt.y()
        angle = math.atan2(dy, dx)

        # Arrow head size
        arrow_size = 8

        # Arrow head points
        p1 = QPointF(
            end_pt.x() - arrow_size * math.cos(angle - math.pi/6),
            end_pt.y() - arrow_size * math.sin(angle - math.pi/6)
        )
        p2 = QPointF(
            end_pt.x() - arrow_size * math.cos(angle + math.pi/6),
            end_pt.y() - arrow_size * math.sin(angle + math.pi/6)
        )

        # Add arrow to path
        arrow_path = QPainterPath(path)
        arrow_path.moveTo(end_pt)
        arrow_path.lineTo(p1)
        arrow_path.moveTo(end_pt)
        arrow_path.lineTo(p2)

        self.setPath(arrow_path)


class ContactIndicator(QGraphicsEllipseItem):
    """Visual indicator for contact interface between elements."""

    def __init__(self, pos: QPointF, contact: ContactInterface, parent=None):
        size = 16
        super().__init__(-size/2, -size/2, size, size, parent)

        self.contact = contact
        self.setPos(pos)
        self.setZValue(5)  # Above connection lines

        # Style based on contact type
        color_map = {
            ContactType.RIGID: Theme.OVERLAY,
            ContactType.ELASTIC: Theme.GREEN,
            ContactType.FRICTIONAL: Theme.YELLOW,
            ContactType.NONLINEAR: Theme.RED
        }
        color = QColor(color_map.get(contact.contact_type, Theme.GREEN))

        self.setBrush(QBrush(color))
        self.setPen(QPen(QColor(Theme.TEXT), 1.5))

        # Tooltip
        self.setToolTip(
            f"Contact: {contact.contact_type.value}\n"
            f"k_n = {contact.k_normal:.2e} N/m\n"
            f"μ = {contact.mu_static:.3f}"
        )

        # Make clickable
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def paint(self, painter, option, widget):
        """Custom paint with symbol."""
        super().paint(painter, option, widget)

        # Draw contact symbol
        painter.setPen(QPen(QColor(Theme.BASE), 2))
        rect = self.rect()
        center = rect.center()

        # Draw "C" for contact or specific symbols
        if self.contact.contact_type == ContactType.RIGID:
            # Solid square
            painter.fillRect(rect.adjusted(4, 4, -4, -4), QColor(Theme.BASE))
        elif self.contact.contact_type == ContactType.FRICTIONAL:
            # Wavy line
            painter.drawLine(
                int(center.x() - 4), int(center.y()),
                int(center.x() + 4), int(center.y())
            )
        else:
            # Spring symbol (zigzag)
            painter.drawLine(
                int(center.x() - 3), int(center.y() - 3),
                int(center.x() + 3), int(center.y() + 3)
            )


class LoadFlowArrow(QGraphicsPathItem):
    """Arrow showing load flow direction and magnitude."""

    def __init__(self, start_pos: QPointF, end_pos: QPointF, load_percent: float):
        super().__init__()

        self.load_percent = load_percent

        # Color based on load percentage
        if load_percent > 80:
            color = Theme.RED
        elif load_percent > 50:
            color = Theme.PEACH
        else:
            color = Theme.GREEN

        pen = QPen(QColor(color), 2)
        self.setPen(pen)
        self.setBrush(QBrush(QColor(color)))

        self._create_arrow(start_pos, end_pos)

    def _create_arrow(self, start: QPointF, end: QPointF):
        """Create arrow path."""
        path = QPainterPath()
        path.moveTo(start)
        path.lineTo(end)

        # Arrow head
        line = QLineF(start, end)
        angle = math.atan2(-line.dy(), line.dx())

        arrow_size = 10
        p1 = end - QPointF(
            math.cos(angle - math.pi/6) * arrow_size,
            -math.sin(angle - math.pi/6) * arrow_size
        )
        p2 = end - QPointF(
            math.cos(angle + math.pi/6) * arrow_size,
            -math.sin(angle + math.pi/6) * arrow_size
        )

        path.moveTo(end)
        path.lineTo(p1)
        path.moveTo(end)
        path.lineTo(p2)

        self.setPath(path)


# =============================================================================
# CONNECTION PORT (DRAG HANDLE)
# =============================================================================

class ConnectionPort(QGraphicsEllipseItem):
    """Small draggable port on element edges for creating connections."""

    PORT_SIZE = 8

    def __init__(self, parent_element: 'ElementGraphicsItem', position: str = "bottom"):
        r = self.PORT_SIZE
        if position == "bottom":
            cx = parent_element.rect().width() / 2 - r / 2
            cy = parent_element.rect().height() - r / 2
        else:  # top
            cx = parent_element.rect().width() / 2 - r / 2
            cy = -r / 2

        super().__init__(cx, cy, r, r, parent_element)
        self.parent_element = parent_element
        self.position = position
        self.setZValue(10)

        # Style: small blue circle, hidden by default
        self.setPen(QPen(QColor(Theme.BLUE), 1.5))
        self.setBrush(QBrush(QColor(Theme.BLUE)))
        self.setOpacity(0.0)  # hidden by default

        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def show_port(self):
        self.setOpacity(0.85)

    def hide_port(self):
        self.setOpacity(0.0)


# =============================================================================
# ANNOTATION ITEM  (3.9)
# =============================================================================

class AnnotationItem(QGraphicsTextItem):
    """Free-form draggable text annotation on the schematic (3.9).

    Double-click to edit.  Serialized to/from MSDModel annotations list.
    """

    def __init__(self, text: str = "Note", pos: QPointF = None):
        super().__init__(text)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setDefaultTextColor(QColor(Theme.YELLOW))
        font = QFont("Monospace", 8)
        self.setFont(font)
        if pos:
            self.setPos(pos)
        self._annotation_id: int = id(self)   # used for serialization

    def mouseDoubleClickEvent(self, event):
        """Start editing on double-click."""
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        """Stop editing when focus leaves."""
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        super().focusOutEvent(event)

    def to_dict(self) -> dict:
        """Serialize to dict for JSON storage."""
        return {
            "annotation_id": self._annotation_id,
            "text": self.toPlainText(),
            "x": self.pos().x(),
            "y": self.pos().y(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AnnotationItem":
        item = cls(text=d.get("text", "Note"),
                   pos=QPointF(d.get("x", 0), d.get("y", 0)))
        item._annotation_id = d.get("annotation_id", id(item))
        return item


# =============================================================================
# MINIMAP OVERVIEW WIDGET  (3.16)
# =============================================================================

class MinimapWidget(QWidget):
    """Bird's-eye thumbnail of the full schematic, with viewport overlay (3.16).

    Place as a floating overlay inside MSDBuilderWindow using a stacked layout
    or as the corner widget of the SchematicView's scroll area.
    Clicking pans the main view to the clicked position.
    """

    def __init__(self, main_view: 'SchematicView', parent=None):
        super().__init__(parent)
        self._view = main_view
        self.setFixedSize(130, 90)
        # Themed bg/border via global QSS (QWidget#minimap) so it re-themes on
        # switch — a per-widget setStyleSheet here froze the startup palette
        # (white when the builder was first opened in the light theme).
        self.setObjectName("minimap")
        self.setToolTip("Minimap — click to pan main view")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Refresh on a timer so we don't repaint on every scene event
        self._timer = QTimer(self)
        self._timer.setInterval(500)   # 2 fps — low CPU
        self._timer.timeout.connect(self.update)
        self._timer.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():        # device sem engine (ex.: durante construção)
            return
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        scene = self._view.scene()
        if scene is None or not scene.items():
            painter.fillRect(self.rect(), QColor(Theme.BASE))
            painter.setPen(QColor(Theme.SUBTEXT))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "empty")
            painter.end()
            return

        w, h = self.width(), self.height()
        scene_rect = scene.itemsBoundingRect().adjusted(-20, -20, 20, 20)

        # Render scene scaled down
        scene.render(painter, QRectF(0, 0, w, h), scene_rect)

        # Viewport rectangle overlay
        vp_rect = self._view.mapToScene(self._view.viewport().rect()).boundingRect()
        if scene_rect.width() > 0 and scene_rect.height() > 0:
            sx = w / scene_rect.width()
            sy = h / scene_rect.height()
            vx = (vp_rect.x() - scene_rect.x()) * sx
            vy = (vp_rect.y() - scene_rect.y()) * sy
            vw = vp_rect.width() * sx
            vh = vp_rect.height() * sy
            painter.setPen(QPen(QColor(Theme.YELLOW), 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(int(vx), int(vy), int(vw), int(vh))

        painter.end()

    def mousePressEvent(self, event):
        """Pan main view to the clicked minimap position."""
        self._pan_to(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._pan_to(event.pos())

    def _pan_to(self, minimap_pos: QPoint):
        scene = self._view.scene()
        if scene is None:
            return
        scene_rect = scene.itemsBoundingRect().adjusted(-20, -20, 20, 20)
        w, h = self.width(), self.height()
        if w == 0 or h == 0 or scene_rect.width() == 0 or scene_rect.height() == 0:
            return
        # Map minimap pixel → scene coordinate
        sx = scene_rect.width() / w
        sy = scene_rect.height() / h
        scene_x = scene_rect.x() + minimap_pos.x() * sx
        scene_y = scene_rect.y() + minimap_pos.y() * sy
        self._view.centerOn(scene_x, scene_y)


# =============================================================================
# SCHEMATIC VIEW (GRID-BASED)
# =============================================================================

class SchematicView(QGraphicsView):
    """Grid-based schematic view for MSD elements."""

    element_selected = pyqtSignal(object)  # Emits ElementGraphicsItem or None
    elements_multi_selected = pyqtSignal(list)  # Emits list of selected items
    model_changed = pyqtSignal()
    grid_position_changed = pyqtSignal(int, int, int)  # element_id, row, col
    context_delete_requested = pyqtSignal(int)        # element_id
    context_duplicate_requested = pyqtSignal(int)     # element_id
    context_apply_load_requested = pyqtSignal(int)    # element_id
    context_recalculate_requested = pyqtSignal(int)   # element_id
    context_expand_requested = pyqtSignal(int)        # element_id (NUT → expand threads)
    context_expand_contacts_requested = pyqtSignal(int) # element_id (THREAD → expand contacts)
    context_edit_contact_props_requested = pyqtSignal(int)  # element_id (contact elements)

    # Class-level clipboard for k/c/m copy-paste
    _clipboard_props: Optional[dict] = None

    def __init__(self, parent=None):
        super().__init__(parent)

        self._scene = QGraphicsScene(self)
        cw, ch = get_grid_cell_width(), get_grid_cell_height()
        self._scene.setSceneRect(0, 0, cw * 16, ch * 18)
        self.setScene(self._scene)

        # Element storage
        self.elements: Dict[int, ElementGraphicsItem] = {}
        self.connections: List[ConnectionLine] = []
        self.parallel_indicators: List[QGraphicsLineItem] = []  # Horizontal lines for parallel elements
        self.contact_indicators: List[ContactIndicator] = []
        self.load_arrows: List[LoadFlowArrow] = []
        self.contacts: Dict[Tuple[int, int], ContactInterface] = {}
        self._load_overlays: List[QGraphicsItem] = []

        # Grid tracking: grid[row][col] = element_id
        self.grid: Dict[int, Dict[int, int]] = defaultdict(dict)

        self._next_id = 1
        self._show_load_flow = False
        self._show_grid = True
        self._grid_items = []

        # Setup view
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setBackgroundBrush(QBrush(QColor(Theme.BASE)))

        # Carimbo ISO 7200 + gradiente de fundo (default inerte p/ backward-compat).
        self._stamp_enabled = False
        self._title_block = {"model": "", "module": "", "step": "", "metric": ""}
        # Auto-fit: enquadra o modelo ao abrir/carregar; desliga no zoom manual.
        self._auto_fit = True

        # Enable scrolling
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Smooth scrolling
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True)

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)

        # Zoom limits
        self._zoom_factor = 1.0
        self._min_zoom = 0.10
        self._max_zoom = 8.0

        # Zoom anchor under mouse for natural feel
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Middle-mouse-held → wheel zooms (in addition to Ctrl+wheel)
        self._middle_held = False

        # Connection drag state
        self._dragging_connection = False
        self._drag_source: Optional[ElementGraphicsItem] = None
        self._drag_port_pos: str = "bottom"  # "top" or "bottom"
        self._temp_arrow: Optional[QGraphicsLineItem] = None

        # Undo/redo (set by the owning MSDBuilder after construction). When
        # None the schematic still works, just without recording grid moves.
        self.undo_stack = None
        # Snapshot of grid positions captured at mouse-press, so a completed
        # drag can be pushed as one GridPositionCommand on release.
        self._move_before: Optional[dict] = None

        # Draw grid
        self._draw_grid()

        # Connect selection changes
        self._scene.selectionChanged.connect(self._on_selection_changed)

    def set_title_block(self, model="", module="", step="", metric="") -> None:
        """Preenche o carimbo ISO 7200 (canto inferior direito do viewport)."""
        self._title_block = {"model": model, "module": module,
                             "step": step, "metric": metric}
        self.viewport().update()

    def set_stamp_enabled(self, enabled: bool) -> None:
        self._stamp_enabled = bool(enabled)
        self.viewport().update()

    def drawBackground(self, painter, rect):
        # Gradiente vertical (assinatura CAE); a grade fina é desenhada por cima
        # como itens da cena (_draw_grid).
        if not painter.isActive():        # device sem engine (ex.: offscreen p/ pintar)
            return
        from PyQt6.QtGui import QLinearGradient
        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0.0, QColor(Theme.SURFACE1))
        grad.setColorAt(1.0, QColor(Theme.CRUST))
        painter.fillRect(rect, grad)

    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)
        if not self._stamp_enabled or not painter.isActive():
            return
        from PyQt6.QtGui import QFont, QPen
        tb = self._title_block
        lines = [f"Modelo  {tb['model'] or '—'}",
                 f"Modulo  {tb['module'] or '—'}   Step  {tb['step'] or '—'}",
                 f"{tb['metric'] or ''}"]
        painter.save()
        painter.resetTransform()          # carimbo em coords de tela, não da cena
        vp = self.viewport().rect()
        w, h = 240, 58
        x, y = vp.right() - w - 12, vp.bottom() - h - 12
        painter.fillRect(x, y, w, h, QColor(Theme.CRUST))
        painter.setPen(QPen(QColor(Theme.SURFACE2), 1))
        painter.drawRect(x, y, w, h)
        painter.setFont(QFont(Theme.FONT_MONO_FAMILY, 8))
        painter.setPen(QColor(Theme.SUBTEXT))
        for i, ln in enumerate(lines):
            painter.drawText(x + 8, y + 16 + i * 15, ln)
        painter.restore()

    def wheelEvent(self, event):
        """Mouse wheel: scroll by default; zoom when Ctrl OR middle button is held."""
        zoom = (event.modifiers() == Qt.KeyboardModifier.ControlModifier
                or self._middle_held)
        if zoom:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._middle_held = True
            self.viewport().setCursor(Qt.CursorShape.SizeAllCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._middle_held = False
            self.viewport().unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def zoom_in(self):
        """Zoom in around the cursor."""
        self._auto_fit = False
        if self._zoom_factor < self._max_zoom:
            self._zoom_factor *= 1.15
            self.scale(1.15, 1.15)

    def zoom_out(self):
        """Zoom out around the cursor."""
        self._auto_fit = False
        if self._zoom_factor > self._min_zoom:
            self._zoom_factor /= 1.15
            self.scale(1 / 1.15, 1 / 1.15)

    def zoom_reset(self):
        """Reset zoom to 100%."""
        self.resetTransform()
        self._zoom_factor = 1.0

    def fit_contents(self):
        """Fit all elements in view."""
        if not self.elements:
            return

        # Calculate bounding rect of all elements
        rect = QRectF()
        for item in self.elements.values():
            rect = rect.united(item.sceneBoundingRect())

        # Add margin
        margin = 50
        rect.adjust(-margin, -margin, margin, margin)

        # Fit in view (+ centraliza o modelo no viewport)
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
        self.centerOn(rect.center())
        self._zoom_factor = self.transform().m11()
        self._auto_fit = True

    def _ensure_scene_fits(self, row: int = 0, col: int = 0):
        """Expand the scene rect when elements approach boundaries."""
        cw, ch, margin = get_grid_cell_width(), get_grid_cell_height(), get_grid_margin()
        needed_w = margin + (col + 2) * cw
        needed_h = margin + (row + 2) * ch
        rect = self._scene.sceneRect()
        changed = False
        if needed_w > rect.width():
            rect.setWidth(needed_w)
            changed = True
        if needed_h > rect.height():
            rect.setHeight(needed_h)
            changed = True
        if changed:
            self._scene.setSceneRect(rect)

    # -----------------------------------------------------------------
    # Annotations  (3.9)
    # -----------------------------------------------------------------

    def _add_annotation(self, scene_pos: QPointF):
        """Add a draggable text annotation at scene_pos."""
        item = AnnotationItem("Note", pos=scene_pos)
        self._scene.addItem(item)
        item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        item.setFocus()

    def get_annotations(self) -> list:
        """Return list of annotation dicts for serialization."""
        result = []
        for item in self._scene.items():
            if isinstance(item, AnnotationItem):
                result.append(item.to_dict())
        return result

    def restore_annotations(self, annotations: list):
        """Recreate annotations from saved dicts (called on model load)."""
        # Remove existing annotations first
        for item in list(self._scene.items()):
            if isinstance(item, AnnotationItem):
                self._scene.removeItem(item)
        for d in annotations:
            item = AnnotationItem.from_dict(d)
            self._scene.addItem(item)

    def toggle_grid(self, show: bool):
        """Show/hide grid lines."""
        self._show_grid = show
        for item in self._grid_items:
            item.setVisible(show)

    def _draw_grid(self):
        """Draw the background grid."""
        self._grid_items.clear()

        # Grid line style (softer weights for readability)
        pen_major = QPen(QColor(Theme.SURFACE1), 0.75, Qt.PenStyle.SolidLine)
        pen_minor = QPen(QColor(Theme.SURFACE0), 0.5, Qt.PenStyle.DotLine)

        # Calculate grid dimensions
        n_cols = 20
        n_rows = 20

        # Vertical lines
        for col in range(n_cols):
            x = GRID_MARGIN + col * GRID_CELL_WIDTH
            pen = pen_major if col % 5 == 0 else pen_minor
            line = self._scene.addLine(x, 0, x, n_rows * GRID_CELL_HEIGHT, pen)
            line.setZValue(-10)
            self._grid_items.append(line)

        # Horizontal lines
        for row in range(n_rows):
            y = GRID_MARGIN + row * GRID_CELL_HEIGHT
            pen = pen_major if row % 5 == 0 else pen_minor
            line = self._scene.addLine(0, y, n_cols * GRID_CELL_WIDTH, y, pen)
            line.setZValue(-10)
            self._grid_items.append(line)

        # Row labels (series position)
        for row in range(n_rows):
            y = GRID_MARGIN + row * GRID_CELL_HEIGHT + GRID_CELL_HEIGHT // 2 - 8
            label = self._scene.addText(f"{row}", QFont("Consolas", 9))
            label.setDefaultTextColor(QColor(Theme.OVERLAY))
            label.setPos(2, y)
            label.setZValue(-5)
            self._grid_items.append(label)

        # Column labels
        for col in range(n_cols):
            x = GRID_MARGIN + col * GRID_CELL_WIDTH + GRID_CELL_WIDTH // 2 - 5
            label = self._scene.addText(f"{col}", QFont("Consolas", 8))
            label.setDefaultTextColor(QColor(Theme.OVERLAY))
            label.setPos(x, 2)
            label.setZValue(-5)
            self._grid_items.append(label)

    def add_element(self, element_type: str, row: int = None, col: int = None) -> ElementGraphicsItem:
        """Add element to the grid."""
        # Auto-find position if not specified
        if row is None:
            row = self._find_next_row()
        if col is None:
            col = self._find_available_column(row)

        # Create element data with error handling
        # Handle deprecated element types
        deprecated_mapping = {
            "CONTACT": "GENERIC_CONTACT",  # Old generic contact
            "MEMBER": "FLANGE",             # Old member type
            "THERMAL": "GENERIC_CONTACT",   # Thermal expansion (not yet implemented as contact)
        }

        if element_type in deprecated_mapping:
            old_type = element_type
            element_type = deprecated_mapping[element_type]
            print(f"Note: Converted deprecated type '{old_type}' to '{element_type}'")

        try:
            elem_type = ElementType[element_type]
        except KeyError:
            # Fallback for unknown types
            print(f"Warning: Unknown element type '{element_type}', using GENERIC_CONTACT")
            elem_type = ElementType.GENERIC_CONTACT
            element_type = "GENERIC_CONTACT"

        visual = ELEMENT_VISUALS.get(element_type, ELEMENT_VISUALS.get("GENERIC_CONTACT", ELEMENT_VISUALS["SHANK"]))

        elem_data = MSDElementData(
            id=self._next_id,
            name=f"{visual.name} #{self._next_id}",
            type=elem_type,
            grid_position=GridPosition(row=row, column=col)
        )

        # Set MSD parameters
        elem_data.msd.k = visual.default_k
        elem_data.msd.c = visual.default_c
        elem_data.msd.m = visual.default_m

        # Auto-compute preload from 70% yield for bolt/member elements
        if element_type in ("HEAD", "SHANK", "NUT", "WASHER", "FLANGE", "GASKET"):
            diameter = elem_data.geometry.diameter
            A_s = get_stress_area_from_threads(diameter)
            if A_s is None:
                # Fallback formula
                p = elem_data.geometry.pitch
                d2 = diameter - 0.6495 * p
                d1 = diameter - 1.0825 * p  # ISO 262 minor diameter
                A_s = math.pi / 4 * ((d2 + d1) / 2) ** 2
            Sy = elem_data.material.Sy  # MPa
            pct = elem_data.preload_percent_yield  # 70.0 by default
            elem_data.preload_force = (pct / 100.0) * A_s * Sy  # N

        # Ensure scene is large enough
        self._ensure_scene_fits(row, col)

        # Create graphics item
        item = ElementGraphicsItem(elem_data)
        self._scene.addItem(item)
        self.elements[self._next_id] = item

        # Update grid tracking
        self.grid[row][col] = self._next_id

        self._next_id += 1

        # Rebuild connections
        self._rebuild_connections()
        self.model_changed.emit()

        return item

    def _find_next_row(self) -> int:
        """Find the next available row."""
        if not self.grid:
            return 0
        return max(self.grid.keys()) + 1

    def _find_available_column(self, row: int) -> int:
        """Find available column in a row."""
        if row not in self.grid or not self.grid[row]:
            return 0
        return max(self.grid[row].keys()) + 1

    def remove_element(self, element_id: int):
        """Remove element from schematic."""
        if element_id not in self.elements:
            return

        item = self.elements[element_id]

        # Remove from grid
        row, col = item.grid_row, item.grid_col
        if row in self.grid and col in self.grid[row]:
            del self.grid[row][col]

        # Remove connections involving this element
        self._remove_connections_for_element(element_id)

        # Remove contacts
        contacts_to_remove = [k for k in self.contacts.keys()
                             if element_id in k]
        for key in contacts_to_remove:
            del self.contacts[key]

        # Remove from scene
        self._scene.removeItem(item)
        del self.elements[element_id]

        self._rebuild_connections()
        self.model_changed.emit()

    def restore_element(self, element_data: MSDElementData) -> 'ElementGraphicsItem':
        """Restore a previously removed element from its saved data.

        Used by the undo system to re-add an element exactly as it was,
        preserving its original id, grid position, and all properties.
        """
        row = element_data.grid_position.row
        col = element_data.grid_position.column

        self._ensure_scene_fits(row, col)

        item = ElementGraphicsItem(element_data)
        self._scene.addItem(item)
        self.elements[element_data.id] = item

        # Update grid tracking
        self.grid[row][col] = element_data.id

        # Ensure _next_id stays ahead of restored ids
        if element_data.id >= self._next_id:
            self._next_id = element_data.id + 1

        self._rebuild_connections()
        self.model_changed.emit()

        return item

    def _remove_connections_for_element(self, element_id: int):
        """Remove all connections involving an element."""
        to_remove = []
        for conn in self.connections:
            if (conn.start_item.element_id == element_id or
                conn.end_item.element_id == element_id):
                to_remove.append(conn)

        for conn in to_remove:
            self._scene.removeItem(conn)
            self.connections.remove(conn)

    def change_element_type(self, element_id: int, new_type: str) -> bool:
        """Change the type of an existing element."""
        if element_id not in self.elements:
            return False

        item = self.elements[element_id]
        old_type = item.element_type

        # Get new visual config
        new_visual = ELEMENT_VISUALS.get(new_type)
        if new_visual is None:
            return False

        # Update element data
        item.element_data.type = ElementType[new_type]
        item.element_data.name = f"{new_visual.name} #{element_id}"

        # Update MSD parameters to new defaults (optional - could preserve old values)
        item.element_data.msd.k = new_visual.default_k
        item.element_data.msd.c = new_visual.default_c
        item.element_data.msd.m = new_visual.default_m

        # Update visual
        item.element_type = new_type
        item.visual = new_visual
        item.update_display()

        self._rebuild_connections()
        self.model_changed.emit()
        return True

    def duplicate_element(self, element_id: int) -> Optional[ElementGraphicsItem]:
        """Duplicate an existing element."""
        if element_id not in self.elements:
            return None

        source = self.elements[element_id]
        source_data = source.element_data

        # Find position for duplicate (same row, next column)
        new_col = self._find_available_column(source.grid_row)

        # Create new element data as copy
        elem_type = source.element_type
        visual = source.visual

        new_data = MSDElementData(
            id=self._next_id,
            name=f"{visual.name} #{self._next_id}",
            type=source_data.type,
            grid_position=GridPosition(row=source.grid_row, column=new_col)
        )

        # Copy MSD parameters
        new_data.msd.k = source_data.msd.k
        new_data.msd.c = source_data.msd.c
        new_data.msd.m = source_data.msd.m
        new_data.msd.auto_calculate_k = source_data.msd.auto_calculate_k
        new_data.msd.auto_calculate_c = source_data.msd.auto_calculate_c
        new_data.msd.auto_calculate_m = source_data.msd.auto_calculate_m

        # Copy geometry
        new_data.geometry.diameter = source_data.geometry.diameter
        new_data.geometry.length = source_data.geometry.length
        new_data.geometry.pitch = source_data.geometry.pitch

        # Copy material
        new_data.material.E = source_data.material.E
        new_data.material.Sy = source_data.material.Sy
        new_data.material.Su = source_data.material.Su
        new_data.material.rho = source_data.material.rho
        new_data.material.alpha = source_data.material.alpha

        # Copy friction
        new_data.friction.mu_thread = source_data.friction.mu_thread
        new_data.friction.mu_bearing = source_data.friction.mu_bearing

        # Copy thread fillet model if present
        if source_data.thread_fillet_model:
            new_data.thread_fillet_model = ThreadFilletModel(
                n_fillets=source_data.thread_fillet_model.n_fillets,
                pitch=source_data.thread_fillet_model.pitch,
                decay_constant=source_data.thread_fillet_model.decay_constant,
                distribution=source_data.thread_fillet_model.distribution,
                power_exponent=source_data.thread_fillet_model.power_exponent,
                connection=source_data.thread_fillet_model.connection
            )

        # Create graphics item
        item = ElementGraphicsItem(new_data)
        self._scene.addItem(item)
        self.elements[self._next_id] = item

        # Update grid tracking
        self.grid[source.grid_row][new_col] = self._next_id

        self._next_id += 1

        self._rebuild_connections()
        self.model_changed.emit()

        return item

    def _rebuild_connections(self):
        """Rebuild connections based on grid layout."""
        # Clear existing connections
        for conn in self.connections:
            self._scene.removeItem(conn)
        self.connections.clear()

        # Clear existing parallel indicators
        for line in self.parallel_indicators:
            self._scene.removeItem(line)
        self.parallel_indicators.clear()

        # Clear existing contact indicators
        for indicator in self.contact_indicators:
            self._scene.removeItem(indicator)
        self.contact_indicators.clear()

        # Get elements sorted by row
        rows = sorted(self.grid.keys())
        if len(rows) < 2:
            return

        # Connect elements in adjacent rows
        # When a row has multiple parallel elements, ALL of them connect
        # to ALL elements in the next row (they share the same series node).
        for i in range(len(rows) - 1):
            current_row = rows[i]
            next_row = rows[i + 1]

            current_elements = list(self.grid[current_row].values())
            next_elements = list(self.grid[next_row].values())

            # Multiple elements in same row = parallel
            is_parallel = len(current_elements) > 1 or len(next_elements) > 1

            # Build unique pairs so we don't duplicate connections
            drawn_pairs = set()

            for elem_id in current_elements:
                start_item = self.elements[elem_id]

                for next_id in next_elements:
                    pair = (min(elem_id, next_id), max(elem_id, next_id))
                    if pair in drawn_pairs:
                        continue
                    drawn_pairs.add(pair)

                    end_item = self.elements[next_id]

                    # Check if there's a contact between these elements
                    contact_key = pair
                    has_contact = contact_key in self.contacts

                    # Create connection line
                    conn = ConnectionLine(start_item, end_item, is_parallel, has_contact)
                    self._scene.addItem(conn)
                    self.connections.append(conn)

                    # Add contact indicator if contact exists
                    if has_contact:
                        contact = self.contacts[contact_key]
                        start_rect = start_item.sceneBoundingRect()
                        end_rect = end_item.sceneBoundingRect()
                        mid_point = QPointF(
                            (start_rect.center().x() + end_rect.center().x()) / 2,
                            (start_rect.bottom() + end_rect.top()) / 2
                        )
                        indicator = ContactIndicator(mid_point, contact)
                        self._scene.addItem(indicator)
                        self.contact_indicators.append(indicator)

        # Also connect parallel elements in same row with horizontal lines
        for row, cols in self.grid.items():
            col_list = sorted(cols.keys())
            if len(col_list) > 1:
                for i in range(len(col_list) - 1):
                    elem_a_id = cols[col_list[i]]
                    elem_b_id = cols[col_list[i + 1]]
                    item_a = self.elements[elem_a_id]
                    item_b = self.elements[elem_b_id]

                    # Draw horizontal connection (parallel indicator)
                    start_pt = item_a.sceneBoundingRect().center()
                    end_pt = item_b.sceneBoundingRect().center()

                    pen = QPen(QColor(Theme.PEACH), 2, Qt.PenStyle.DashDotLine)
                    line = self._scene.addLine(
                        start_pt.x(), start_pt.y(),
                        end_pt.x(), end_pt.y(),
                        pen
                    )
                    line.setZValue(-2)
                    self.parallel_indicators.append(line)

    def _on_selection_changed(self):
        """Handle selection changes."""
        selected = self._scene.selectedItems()
        element_items = [item for item in selected
                        if isinstance(item, ElementGraphicsItem)]

        if len(element_items) == 1:
            self.element_selected.emit(element_items[0])
        elif len(element_items) > 1:
            self.elements_multi_selected.emit(element_items)
        else:
            self.element_selected.emit(None)

    def contextMenuEvent(self, event):
        """Right-click context menu on elements or empty canvas."""
        scene_pos = self.mapToScene(event.pos())
        item_at = self._scene.itemAt(scene_pos, self.transform())

        # Walk up to find an ElementGraphicsItem
        while item_at and not isinstance(item_at, ElementGraphicsItem):
            item_at = item_at.parentItem()

        if not isinstance(item_at, ElementGraphicsItem):
            # === CANVAS EMPTY-AREA MENU ===
            canvas_menu = QMenu(self)

            add_menu = canvas_menu.addMenu("Add Element")
            for _etype, _label in [
                ("HEAD", "Bolt Head"), ("SHANK", "Shank"), ("NUT", "Nut"),
                ("WASHER", "Washer"), ("FLANGE", "Flange"),
                ("GASKET", "Gasket"), ("GROUND", "Ground")
            ]:
                a = add_menu.addAction(_label)
                a.setData(("add_elem", _etype))

            canvas_menu.addSeparator()
            fit_action = canvas_menu.addAction("Fit to View")
            sel_all_action = canvas_menu.addAction("Select All")
            annot_action = canvas_menu.addAction("Add Text Annotation")   # 3.9
            canvas_menu.addSeparator()
            clear_action = canvas_menu.addAction("Clear Canvas...")

            chosen = canvas_menu.exec(event.globalPos())
            if chosen is None:
                return
            data = chosen.data()
            if isinstance(data, tuple) and data[0] == "add_elem":
                col = max(0, int((scene_pos.x() - get_grid_margin()) / get_grid_cell_width()))
                row = max(0, int((scene_pos.y() - get_grid_margin()) / get_grid_cell_height()))
                self.add_element(data[1], row, col)
                self.model_changed.emit(self.get_model_data())
            elif chosen == fit_action:
                br = self._scene.itemsBoundingRect()
                self.fitInView(br.adjusted(-20, -20, 20, 20),
                               Qt.AspectRatioMode.KeepAspectRatio)
            elif chosen == sel_all_action:
                for item in self._scene.items():
                    if isinstance(item, ElementGraphicsItem):
                        item.setSelected(True)
            elif chosen == annot_action:
                self._add_annotation(scene_pos)   # 3.9
            elif chosen == clear_action:
                reply = QMessageBox.question(
                    self, "Clear Canvas", "Remove all elements from the canvas?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    for eid in list(self.elements.keys()):
                        self.remove_element(eid)
                    self.model_changed.emit(self.get_model_data())
            return

        # === ELEMENT CONTEXT MENU ===
        elem_item = item_at
        eid = elem_item.element_id

        menu = QMenu(self)

        # Header (disabled title)
        header_action = menu.addAction(
            f"{elem_item.visual.symbol} {elem_item.visual.name} #{eid}"
        )
        header_action.setEnabled(False)
        menu.addSeparator()

        # Edit / Copy / Paste properties
        edit_action = menu.addAction("Edit Properties")
        copy_action = menu.addAction("Copy k, c, m")
        paste_action = menu.addAction("Paste k, c, m")
        paste_action.setEnabled(SchematicView._clipboard_props is not None)
        menu.addSeparator()

        dup_action = menu.addAction("Duplicate")
        delete_action = menu.addAction("Delete")
        delete_action.setIcon(self.style().standardIcon(
            self.style().StandardPixmap.SP_TrashIcon) if hasattr(self.style().StandardPixmap, 'SP_TrashIcon')
            else self.style().standardIcon(self.style().StandardPixmap.SP_DialogCloseButton))

        menu.addSeparator()

        # Apply Load / Recalculate
        apply_load_action = menu.addAction("Apply Load/Constraint...")
        recalculate_action = menu.addAction("Recalculate MSD")

        # If two items are selected, offer contact definition
        selected = [i for i in self._scene.selectedItems()
                    if isinstance(i, ElementGraphicsItem)]
        contact_action = None
        if len(selected) == 2:
            menu.addSeparator()
            contact_action = menu.addAction("Define Contact...")

        # Edit Contact Properties for contact elements
        _CONTACT_TYPES = ("THREAD", "BEARING_HEAD", "BEARING_NUT",
                          "FLANGE_FLANGE", "WASHER_CONTACT",
                          "GASKET_CONTACT", "GENERIC_CONTACT")
        edit_contact_props_action = None
        if elem_item.element_type in _CONTACT_TYPES:
            menu.addSeparator()
            edit_contact_props_action = menu.addAction("Edit Contact Properties...")

        # Expand Threads for NUT elements
        expand_threads_action = None
        if elem_item.element_type == "NUT":
            menu.addSeparator()
            expand_threads_action = menu.addAction("Expand Threads...")

        # Expand Thread Contacts for THREAD elements
        expand_contacts_action = None
        if elem_item.element_type == "THREAD":
            expand_contacts_action = menu.addAction("Expand Thread Contacts...")

        chosen = menu.exec(event.globalPos())

        if chosen is None:
            return
        elif chosen == edit_action:
            elem_item.setSelected(True)
            self.element_selected.emit(elem_item)
        elif chosen == copy_action:
            msd = elem_item.element_data.msd
            SchematicView._clipboard_props = {"k": msd.k, "c": msd.c, "m": msd.m}
        elif chosen == paste_action:
            if SchematicView._clipboard_props:
                msd = elem_item.element_data.msd
                msd.k = SchematicView._clipboard_props["k"]
                msd.c = SchematicView._clipboard_props["c"]
                msd.m = SchematicView._clipboard_props["m"]
                elem_item.update_display()
                self.model_changed.emit(self.get_model_data())
        elif chosen == delete_action:
            self.context_delete_requested.emit(eid)
        elif chosen == dup_action:
            self.context_duplicate_requested.emit(eid)
        elif chosen == apply_load_action:
            self.context_apply_load_requested.emit(eid)
        elif chosen == recalculate_action:
            self.context_recalculate_requested.emit(eid)
        elif contact_action and chosen == contact_action:
            self.elements_multi_selected.emit(selected)
        elif edit_contact_props_action and chosen == edit_contact_props_action:
            self.context_edit_contact_props_requested.emit(eid)
        elif expand_threads_action and chosen == expand_threads_action:
            self.context_expand_requested.emit(eid)
        elif expand_contacts_action and chosen == expand_contacts_action:
            self.context_expand_contacts_requested.emit(eid)

    def get_parallel_groups(self) -> Dict[int, List[int]]:
        """Get elements grouped by row (parallel groups)."""
        groups = {}
        for row, cols in self.grid.items():
            if cols:
                groups[row] = list(cols.values())
        return groups

    def get_series_chain(self) -> List[List[int]]:
        """Get elements as series chain of parallel groups."""
        groups = self.get_parallel_groups()
        return [groups[row] for row in sorted(groups.keys())]

    def add_contact(self, elem_a_id: int, elem_b_id: int,
                   contact: ContactInterface):
        """Add contact interface between two elements."""
        key = (min(elem_a_id, elem_b_id), max(elem_a_id, elem_b_id))
        self.contacts[key] = contact
        self._rebuild_connections()
        self.model_changed.emit()

    def calculate_load_flow(self, total_load: float) -> Dict[int, float]:
        """Calculate load distribution through the model."""
        flow = {}
        series_chain = self.get_series_chain()

        if not series_chain:
            return flow

        current_load = total_load

        for group in series_chain:
            # Elements in same row split load by stiffness
            if len(group) == 1:
                flow[group[0]] = current_load
            else:
                # Parallel: load splits by stiffness ratio
                total_k = sum(self.elements[eid].element_data.msd.k
                             for eid in group)
                for eid in group:
                    k = self.elements[eid].element_data.msd.k
                    flow[eid] = current_load * (k / total_k) if total_k > 0 else 0

        return flow

    def show_load_flow(self, total_load: float):
        """Display load flow visualization with force propagation annotations."""
        # Clear existing arrows
        for arrow in self.load_arrows:
            self._scene.removeItem(arrow)
        self.load_arrows.clear()

        # Calculate flow
        flow = self.calculate_load_flow(total_load)

        # Create arrows for each element
        for elem_id, load in flow.items():
            item = self.elements[elem_id]
            rect = item.sceneBoundingRect()

            # Arrow from top to bottom of element
            start = rect.topLeft() + QPointF(rect.width()/2, -10)
            end = rect.topLeft() + QPointF(rect.width()/2, 10)

            percent = (load / total_load * 100) if total_load > 0 else 0
            arrow = LoadFlowArrow(start, end, percent)
            self._scene.addItem(arrow)
            self.load_arrows.append(arrow)

            # Add load label
            label = self._scene.addText(f"{load:.0f}N ({percent:.0f}%)",
                                        QFont("Consolas", 7))
            label.setDefaultTextColor(QColor(Theme.YELLOW))
            label.setPos(rect.right() + 5, rect.top())
            self.load_arrows.append(label)

        # --- Force propagation annotations ---
        self._add_propagation_annotations(total_load, flow)

        self._show_load_flow = True

    def _add_propagation_annotations(self, preload: float,
                                     flow: Dict[int, float]):
        """Add force propagation annotations showing how loads transfer.

        For a preloaded bolted joint:
        - Preload F_p creates clamping force through all elements
        - Transverse force at interface causes thread loosening torque
        - Thread helix converts axial force to torque: T = F_p * d2/2 * tan(lambda)
        - Bearing friction resists loosening: T_b = mu_b * F_p * r_eff
        """
        if not self.elements:
            return

        # Collect elements by type for annotation
        thread_elems = []
        bearing_elems = []
        nut_elems = []
        flange_elems = []
        head_elems = []

        for eid, item in self.elements.items():
            etype = item.element_type
            if etype == "THREAD":
                thread_elems.append(item)
            elif etype in ("BEARING_HEAD", "BEARING_NUT"):
                bearing_elems.append(item)
            elif etype == "NUT":
                nut_elems.append(item)
            elif etype == "FLANGE":
                flange_elems.append(item)
            elif etype == "HEAD":
                head_elems.append(item)

        # Default bolt parameters for annotation
        d2 = 10.86e-3   # M12 pitch diameter (m)
        helix_angle = math.atan(1.75e-3 / (math.pi * d2))  # radians
        mu_thread = 0.12
        mu_bearing = 0.14
        r_eff = d2 / 2 * 1.3  # effective bearing radius

        # Thread loosening torque
        for item in thread_elems:
            elem_load = flow.get(item.element_id, preload)
            T_helix = elem_load * (d2 / 2) * math.tan(helix_angle)
            T_thread_fric = mu_thread * elem_load * d2 / (2 * math.cos(math.radians(30)))

            rect = item.sceneBoundingRect()
            ann = self._scene.addText(
                f"T_helix={T_helix:.1f} N.m\n"
                f"T_fric={T_thread_fric:.1f} N.m",
                QFont("Consolas", 7)
            )
            ann.setDefaultTextColor(QColor(Theme.MAUVE))
            ann.setPos(rect.left() - 120, rect.top())
            self.load_arrows.append(ann)

        # Bearing friction resistance
        for item in bearing_elems:
            elem_load = flow.get(item.element_id, preload)
            T_bearing = mu_bearing * elem_load * r_eff

            rect = item.sceneBoundingRect()
            ann = self._scene.addText(
                f"T_bearing={T_bearing:.1f} N.m\n"
                f"(resists loosening)",
                QFont("Consolas", 7)
            )
            ann.setDefaultTextColor(QColor(Theme.TEAL))
            ann.setPos(rect.left() - 130, rect.top())
            self.load_arrows.append(ann)

        # Nut: net torque balance
        for item in nut_elems:
            elem_load = flow.get(item.element_id, preload)
            T_helix = elem_load * (d2 / 2) * math.tan(helix_angle)
            T_fric_total = (mu_thread * elem_load * d2 / (2 * math.cos(math.radians(30)))
                           + mu_bearing * elem_load * r_eff)
            net = T_helix - T_fric_total

            rect = item.sceneBoundingRect()
            status = "SELF-LOCKING" if net < 0 else "LOOSENING RISK"
            color = Theme.GREEN if net < 0 else Theme.RED
            ann = self._scene.addText(
                f"Net torque: {net:.2f} N.m\n"
                f"{status}",
                QFont("Consolas", 7, QFont.Weight.Bold)
            )
            ann.setDefaultTextColor(QColor(color))
            ann.setPos(rect.left() - 140, rect.top())
            self.load_arrows.append(ann)

        # Flange clamping force
        for item in flange_elems:
            elem_load = flow.get(item.element_id, preload)
            rect = item.sceneBoundingRect()
            ann = self._scene.addText(
                f"F_clamp={elem_load / 1000:.1f} kN",
                QFont("Consolas", 7)
            )
            ann.setDefaultTextColor(QColor(Theme.SKY))
            ann.setPos(rect.left() - 110, rect.top() + 5)
            self.load_arrows.append(ann)

    def hide_load_flow(self):
        """Hide load flow visualization."""
        for item in self.load_arrows:
            self._scene.removeItem(item)
        self.load_arrows.clear()
        self._show_load_flow = False

    def clear_all(self):
        """Clear all elements."""
        for elem_id in list(self.elements.keys()):
            self.remove_element(elem_id)
        self.grid.clear()
        self._next_id = 1
        # Clear load overlays
        for item in self._load_overlays:
            self._scene.removeItem(item)
        self._load_overlays.clear()

    def update_load_overlays(self, loading_data: dict):
        """Draw FBD-style load indicators around the element column.

        Implemented with pure Qt primitives so bounding-rect and
        scene-rect issues do not clip or hide any arrows.

        Layout:
          - Preload    : ↓ / ↑ opposing arrows centred on bolt axis
          - Transverse : → arrow to the LEFT pointing at the joint
          - External   : ↑/↓ arrow to the RIGHT of the joint
          - Torque     : circular arc arrow to the RIGHT
          - Bending    : text label to the RIGHT of the bottom element
        """
        # ── cleanup ────────────────────────────────────────────────────
        for item in self._load_overlays:
            self._scene.removeItem(item)
        self._load_overlays.clear()

        if not self.elements:
            return

        # ── element column geometry ────────────────────────────────────
        sorted_items = sorted(self.elements.values(), key=lambda it: it.grid_row)
        cw, ch = get_grid_cell_width(), get_grid_cell_height()
        top_item = sorted_items[0]
        bot_item = sorted_items[-1]

        col_x  = top_item.pos().x()
        col_cx = col_x + cw / 2          # horizontal centre of bolt axis
        top_y  = top_item.pos().y()
        bot_y  = bot_item.pos().y() + ch
        mid_y  = (top_y + bot_y) / 2

        ARROW = 55    # arrow shaft length (px)
        HEAD  = 9     # arrowhead triangle size (px)

        # ── expand scene rect so above/left overlays are visible ───────
        # The scene starts at (0,0); arrows above/left go to negative coords.
        # Compute the minimum top and left we will need, then expand.
        need_left = col_x - ARROW - 110   # transverse arrow tail + labels
        need_top  = top_y - ARROW - 30    # preload top arrow + label
        cur = self._scene.sceneRect()
        exp_l = min(cur.x(),             need_left)
        exp_t = min(cur.y(),             need_top)
        exp_r = max(cur.x() + cur.width(),  col_x + cw + 250)
        exp_b = max(cur.y() + cur.height(), bot_y + ARROW + 20)
        if (exp_l != cur.x() or exp_t != cur.y() or
                exp_r != cur.x() + cur.width() or
                exp_b != cur.y() + cur.height()):
            self._scene.setSceneRect(exp_l, exp_t,
                                     exp_r - exp_l, exp_b - exp_t)

        # ── primitive helpers ──────────────────────────────────────────
        def _add(item):
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,    False)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
            item.setOpacity(0.88)
            self._scene.addItem(item)
            self._load_overlays.append(item)

        def _lbl(text, x, y, color, bold=False):
            t = QGraphicsTextItem(text)
            t.setDefaultTextColor(QColor(color))
            f = QFont()
            f.setPointSize(8)
            if bold:
                f.setWeight(QFont.Weight.Bold)
            t.setFont(f)
            t.setOpacity(0.95)
            t.setPos(x, y)
            t.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,    False)
            t.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
            self._scene.addItem(t)
            self._load_overlays.append(t)

        def _arrow(x1, y1, x2, y2, color, width=2):
            """Shaft line + filled triangular arrowhead at (x2, y2)."""
            pen = QPen(QColor(color), width, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            shaft = QGraphicsLineItem(x1, y1, x2, y2)
            shaft.setPen(pen)
            _add(shaft)

            ang = math.atan2(y2 - y1, x2 - x1)
            hp = QPainterPath()
            hp.moveTo(x2, y2)
            hp.lineTo(x2 - HEAD * math.cos(ang - math.pi / 6),
                      y2 - HEAD * math.sin(ang - math.pi / 6))
            hp.lineTo(x2 - HEAD * math.cos(ang + math.pi / 6),
                      y2 - HEAD * math.sin(ang + math.pi / 6))
            hp.closeSubpath()
            head = QGraphicsPathItem(hp)
            head.setPen(QPen(Qt.PenStyle.NoPen))
            head.setBrush(QBrush(QColor(color)))
            head.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,    False)
            head.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
            head.setOpacity(0.88)
            self._scene.addItem(head)
            self._load_overlays.append(head)

        # ── PRELOAD ────────────────────────────────────────────────────
        preload = loading_data.get("F_preload", 0.0)
        if preload > 0:
            px = col_cx   # centred on bolt axis
            # top arrow: ↓ pointing into joint from above
            _arrow(px, top_y - ARROW, px, top_y, Theme.BLUE)
            # bottom arrow: ↑ pointing into joint from below
            _arrow(px, bot_y + ARROW, px, bot_y, Theme.BLUE)
            # dashed span line along bolt axis
            span = QGraphicsLineItem(px, top_y, px, bot_y)
            dpen = QPen(QColor(Theme.BLUE))
            dpen.setStyle(Qt.PenStyle.DashLine)
            dpen.setWidth(1)
            span.setPen(dpen)
            span.setOpacity(0.25)
            _add(span)
            # label above the top arrow tail
            _lbl(f"F\u2080 = {preload / 1000:.1f} kN",
                 px - 45, top_y - ARROW - 22,
                 Theme.BLUE, bold=True)

        # ── TRANSVERSE / SHEAR ─────────────────────────────────────────
        f_trans   = loading_data.get("F_transverse",   0.0)
        delta_amp = loading_data.get("delta_amplitude", 0.0)
        if f_trans > 0 or delta_amp > 0:
            tx0 = col_x - ARROW - 10   # arrow tail (leftmost)
            tx1 = col_x - 10           # arrow tip  (just left of column)
            _arrow(tx0, mid_y, tx1, mid_y, Theme.GREEN)
            if f_trans > 0:
                _lbl(f"F_T = {f_trans / 1000:.1f} kN",
                     tx0 - 90, mid_y - 20, Theme.GREEN, bold=True)
            if delta_amp > 0:
                _lbl(f"\u21d4 \u03b4 = {delta_amp:.2f} mm",
                     tx0 - 90, mid_y + 4,  Theme.GREEN)

        # ── EXTERNAL AXIAL ─────────────────────────────────────────────
        right_off = 0
        f_ext = loading_data.get("F_external", 0.0)
        if f_ext != 0:
            ex = col_x + cw + 35 + right_off
            if f_ext > 0:
                _arrow(ex, mid_y + ARROW, ex, mid_y - ARROW, Theme.PEACH)
                _lbl(f"\u2191 F_ext\n{f_ext / 1000:.1f} kN",
                     ex - 30, mid_y - ARROW - 30, Theme.PEACH)
            else:
                _arrow(ex, mid_y - ARROW, ex, mid_y + ARROW, Theme.PEACH)
                _lbl(f"\u2193 F_ext\n{abs(f_ext) / 1000:.1f} kN",
                     ex - 30, mid_y + ARROW + 4,  Theme.PEACH)
            right_off += 75

        # ── TORQUE ─────────────────────────────────────────────────────
        t_applied = loading_data.get("T_applied", 0.0)
        if t_applied > 0:
            tx = col_x + cw + 55 + right_off
            ty = mid_y
            r  = 22
            # Arc (CW, 270° sweep starting at 12-o'clock = 90° in Qt convention)
            arc = QPainterPath()
            arc.arcMoveTo(QRectF(tx - r, ty - r, 2 * r, 2 * r), 90)
            arc.arcTo(QRectF(tx - r, ty - r, 2 * r, 2 * r), 90, -270)
            aitem = QGraphicsPathItem(arc)
            aitem.setPen(QPen(QColor(Theme.PINK), 2, Qt.PenStyle.SolidLine,
                              Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            aitem.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            _add(aitem)
            # small arrowhead at the arc end (90° − 270° = −180° → pointing left)
            ae  = math.radians(-180)
            ae_x = tx + r * math.cos(ae)
            ae_y = ty - r * math.sin(ae)   # Qt Y-axis is inverted
            _arrow(ae_x, ae_y - 6, ae_x, ae_y + 6, Theme.PINK, width=1)
            _lbl(f"T = {t_applied:.0f} N\u00b7m",
                 tx - 35, ty + r + 4, Theme.PINK)
            right_off += 75

        # ── BENDING ────────────────────────────────────────────────────
        load_type = str(loading_data.get("type", "")).upper()
        if load_type == "BENDING" and f_trans:
            bx = col_x + cw + 35 + right_off
            by = bot_item.pos().y() + ch / 2
            _lbl(f"\u21b7 M = {f_trans / 1000:.1f} kN",
                 bx, by, Theme.MAUVE, bold=True)

        # ── PER-ELEMENT LOADS (from right-click Apply Load) ────────────
        # Positioned to the LEFT of the column, below the global transverse arrow,
        # one row per element that has applied loads.
        elem_load_x = col_x - ARROW - 115   # left side, slightly further out
        for elem_item in sorted_items:
            loads = getattr(elem_item.element_data, 'applied_loads', [])
            if not loads:
                continue
            ey = elem_item.pos().y() + ch / 2   # y-centre of this element

            for load in loads:
                load_type_str = str(getattr(load, 'load_type', 'axial'))
                mag = float(getattr(load, 'magnitude', 0.0))
                if mag == 0.0:
                    continue

                if load_type_str in ("torsion", "moment"):
                    # Small circular arc to the right of the element
                    tx = col_x + cw + 20
                    r2 = 14
                    arc2 = QPainterPath()
                    arc2.arcMoveTo(QRectF(tx - r2, ey - r2, 2 * r2, 2 * r2), 90)
                    arc2.arcTo(QRectF(tx - r2, ey - r2, 2 * r2, 2 * r2), 90, -270)
                    aitem2 = QGraphicsPathItem(arc2)
                    aitem2.setPen(QPen(QColor(Theme.MAUVE), 2,
                                      Qt.PenStyle.SolidLine,
                                      Qt.PenCapStyle.RoundCap,
                                      Qt.PenJoinStyle.RoundJoin))
                    aitem2.setBrush(QBrush(Qt.BrushStyle.NoBrush))
                    _add(aitem2)
                    _arrow(col_x + cw + 20 + r2, ey - 4,
                           col_x + cw + 20 + r2, ey + 4,
                           Theme.MAUVE, width=1)
                    _lbl(f"T={mag:.0f}N\u00b7m",
                         col_x + cw + 38, ey - 8, Theme.MAUVE)

                elif load_type_str == "shear":
                    # Short horizontal arrow pointing right, at element y
                    tx0 = elem_load_x
                    tx1 = col_x - 10
                    _arrow(tx0, ey, tx1, ey, Theme.TEAL)
                    _lbl(f"V={mag / 1000:.2f}kN",
                         tx0 - 65, ey - 10, Theme.TEAL)

                elif load_type_str == "bending":
                    # Curved moment arrow at element right side
                    bm_x = col_x + cw + 18
                    r3 = 16
                    arc3 = QPainterPath()
                    arc3.arcMoveTo(QRectF(bm_x - r3, ey - r3, 2 * r3, 2 * r3), 150)
                    arc3.arcTo(QRectF(bm_x - r3, ey - r3, 2 * r3, 2 * r3), 150, -240)
                    end3 = arc3.currentPosition()
                    aitem3 = QGraphicsPathItem(arc3)
                    aitem3.setPen(QPen(QColor(Theme.YELLOW), 2,
                                       Qt.PenStyle.SolidLine,
                                       Qt.PenCapStyle.RoundCap,
                                       Qt.PenJoinStyle.RoundJoin))
                    aitem3.setBrush(QBrush(Qt.BrushStyle.NoBrush))
                    _add(aitem3)
                    _arrow(end3.x() - 4, end3.y() - 4,
                           end3.x() + 4, end3.y() + 4,
                           Theme.YELLOW, width=1)
                    _lbl(f"M={mag / 1000:.2f}kN\u00b7m",
                         col_x + cw + 36, ey - 8, Theme.YELLOW)

                elif load_type_str == "impact":
                    # Zigzag downward arrow to the right of the element
                    ix = col_x + cw + 22
                    iy0 = ey - ARROW * 0.55
                    iy1 = ey + ARROW * 0.55
                    zm = 8   # zigzag width
                    zp = QPainterPath()
                    seg = (iy1 - iy0) / 5
                    zp.moveTo(ix, iy0)
                    zp.lineTo(ix + zm, iy0 + seg)
                    zp.lineTo(ix,      iy0 + 2 * seg)
                    zp.lineTo(ix + zm * 0.6, iy0 + 3 * seg)
                    zp.lineTo(ix,      iy0 + 4 * seg)
                    zp.lineTo(ix,      iy1)
                    zitem = QGraphicsPathItem(zp)
                    zitem.setPen(QPen(QColor(Theme.RED), 2,
                                     Qt.PenStyle.SolidLine,
                                     Qt.PenCapStyle.RoundCap,
                                     Qt.PenJoinStyle.RoundJoin))
                    zitem.setBrush(QBrush(Qt.BrushStyle.NoBrush))
                    _add(zitem)
                    # Arrowhead at bottom
                    _arrow(ix - 1, iy1 - 4, ix, iy1, Theme.RED, width=1)
                    _lbl(f"\u26a1{mag:.0f}N",
                         col_x + cw + 34, ey - 8, Theme.RED)

                else:
                    # Axial: short vertical arrow at element right side
                    ax_x = col_x + cw + 22
                    if mag > 0:
                        # Tension (downward into joint)
                        _arrow(ax_x, ey - ARROW * 0.5,
                               ax_x, ey + ARROW * 0.5, Theme.PEACH)
                        _lbl(f"\u2193{mag / 1000:.2f}kN",
                             col_x + cw + 34, ey - 8, Theme.PEACH)
                    else:
                        _arrow(ax_x, ey + ARROW * 0.5,
                               ax_x, ey - ARROW * 0.5, Theme.PEACH)
                        _lbl(f"\u2191{abs(mag) / 1000:.2f}kN",
                             col_x + cw + 34, ey - 8, Theme.PEACH)

    # -----------------------------------------------------------------
    # Connection drag-arrow interaction
    # -----------------------------------------------------------------

    def mousePressEvent(self, event):
        """Start connection drag if clicking on a port."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Snapshot grid positions so a completed drag can be recorded as
            # one undoable move on release.
            self._move_before = self._snapshot_positions()
            scene_pos = self.mapToScene(event.pos())
            item_at = self._scene.itemAt(scene_pos, self.transform())

            if isinstance(item_at, ConnectionPort):
                self._dragging_connection = True
                self._drag_source = item_at.parent_element
                self._drag_port_pos = item_at.position

                # Create temporary arrow
                start_rect = self._drag_source.sceneBoundingRect()
                if self._drag_port_pos == "bottom":
                    start_pt = QPointF(start_rect.center().x(), start_rect.bottom())
                else:
                    start_pt = QPointF(start_rect.center().x(), start_rect.top())

                pen = QPen(QColor(Theme.BLUE), 2, Qt.PenStyle.DashLine)
                self._temp_arrow = self._scene.addLine(
                    start_pt.x(), start_pt.y(),
                    scene_pos.x(), scene_pos.y(), pen
                )
                self._temp_arrow.setZValue(20)
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Update temporary arrow during connection drag."""
        if self._dragging_connection and self._temp_arrow and self._drag_source:
            scene_pos = self.mapToScene(event.pos())
            line = self._temp_arrow.line()
            self._temp_arrow.setLine(line.x1(), line.y1(),
                                     scene_pos.x(), scene_pos.y())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Finish connection drag — rearrange grid."""
        if self._dragging_connection and event.button() == Qt.MouseButton.LeftButton:
            if self._temp_arrow:
                self._scene.removeItem(self._temp_arrow)
                self._temp_arrow = None

            scene_pos = self.mapToScene(event.pos())
            target_item = self._scene.itemAt(scene_pos, self.transform())

            # Walk up to find an ElementGraphicsItem (could hit child)
            while target_item and not isinstance(target_item, ElementGraphicsItem):
                target_item = target_item.parentItem()

            if (isinstance(target_item, ElementGraphicsItem)
                    and target_item is not self._drag_source):
                self._finish_connection_drag(target_item)

            self._dragging_connection = False
            self._drag_source = None
            self._maybe_push_grid_move("Rearrange elements")
            event.accept()
            return

        super().mouseReleaseEvent(event)
        # Record a completed free item drag (if any) as one undoable move.
        self._maybe_push_grid_move("Move element")

    def _finish_connection_drag(self, target: 'ElementGraphicsItem'):
        """Rearrange grid based on drag direction."""
        src = self._drag_source
        if src is None:
            return

        if self._drag_port_pos == "bottom":
            # Series: place target in row after source
            new_row = src.grid_row + 1
            self._insert_row_gap(new_row)
            target.set_grid_position(new_row, 0)
        else:
            # Parallel: place target in same row as source
            new_col = self._find_available_column(src.grid_row)
            target.set_grid_position(src.grid_row, new_col)

        self._update_grid_tracking()
        self._rebuild_connections()
        self.model_changed.emit()

    # -----------------------------------------------------------------
    # Undo/redo helpers (grid moves + whole-schematic state snapshots)
    # -----------------------------------------------------------------

    def _snapshot_positions(self) -> Dict[int, Tuple[int, int]]:
        """Return {element_id: (row, col)} for every element (undo snapshot)."""
        return {eid: (it.grid_row, it.grid_col)
                for eid, it in self.elements.items()}

    def _sync_grid_from_items(self):
        """Rebuild the grid dict from the items' current cells (no row
        compaction), keep each ``element_data.grid_position`` in step, and
        redraw connections.  Reconciles the model after a free item drag, which
        only updates the item's ``grid_row``/``grid_col``."""
        self.grid.clear()
        for eid, it in self.elements.items():
            self.grid[it.grid_row][it.grid_col] = eid
            it.element_data.grid_position.row = it.grid_row
            it.element_data.grid_position.column = it.grid_col
        self._rebuild_connections()

    def _maybe_push_grid_move(self, description: str = "Move element"):
        """If elements moved since the last mouse-press snapshot, reconcile the
        grid and record one undoable :class:`GridPositionCommand`."""
        before = self._move_before
        self._move_before = None
        if before is None or self.undo_stack is None:
            return
        after = self._snapshot_positions()
        if after == before:
            return
        # A free drag leaves the grid dict / connections stale — reconcile so
        # the drop persists and the recorded snapshot is consistent.
        self._sync_grid_from_items()
        self.undo_stack.push(GridPositionCommand(self, before, after, description))

    def _capture_state(self) -> dict:
        """Snapshot element data + contacts for an undoable state swap.

        Holds *references* to the live ``element_data`` objects (safe: they
        outlive graphics-item removal) so an undo can restore them verbatim
        via :meth:`restore_element`."""
        return {
            'elements': [it.element_data for it in self.elements.values()],
            'contacts': dict(self.contacts),
            'next_id': self._next_id,
        }

    def _restore_state(self, state: dict):
        """Restore a snapshot produced by :meth:`_capture_state`."""
        self.clear_all()
        for data in state.get('elements', []):
            self.restore_element(data)
        self.contacts.clear()
        self.contacts.update(state.get('contacts', {}))
        self._next_id = state.get('next_id', self._next_id)
        self._rebuild_connections()
        self.model_changed.emit()

    # -----------------------------------------------------------------
    # Grid tracking maintenance
    # -----------------------------------------------------------------

    def _insert_row_gap(self, at_row: int):
        """Shift all elements at or below `at_row` down by one row."""
        # Process from bottom up so we don't collide
        for elem in sorted(self.elements.values(), key=lambda e: -e.grid_row):
            if elem.grid_row >= at_row:
                elem.set_grid_position(elem.grid_row + 1, elem.grid_col)

    def _update_grid_tracking(self):
        """Rebuild grid dict from current element positions."""
        self.grid.clear()
        for eid, item in self.elements.items():
            row, col = item.grid_row, item.grid_col
            self.grid[row][col] = eid
        self._compact_rows()

    def _compact_rows(self):
        """Renumber rows to be contiguous (0, 1, 2, ...) removing gaps."""
        if not self.grid:
            return
        sorted_rows = sorted(self.grid.keys())
        # Check if already compact
        if sorted_rows == list(range(len(sorted_rows))):
            return

        row_map = {old: new for new, old in enumerate(sorted_rows)}
        new_grid: Dict[int, Dict[int, int]] = defaultdict(dict)
        for old_row, cols in list(self.grid.items()):
            new_row = row_map[old_row]
            for col, eid in cols.items():
                new_grid[new_row][col] = eid
                self.elements[eid].set_grid_position(new_row, col)
        self.grid.clear()
        self.grid.update(new_grid)

    def export_to_model(self) -> Optional[MSDModel]:
        """Export schematic to MSDModel with proper topology from grid."""
        if not self.elements:
            return None

        model = MSDModel(name="Schematic Model")

        # Sort elements by (row, col) for correct series ordering
        sorted_items = sorted(
            self.elements.values(),
            key=lambda item: (item.grid_row, item.grid_col)
        )

        # Identify parallel groups: elements sharing the same row
        from collections import Counter
        row_counts = Counter(item.grid_row for item in sorted_items)

        # Assign connection_type and parallel_group based on grid
        parallel_group_id = 1
        row_to_group = {}
        for item in sorted_items:
            elem = item.element_data
            row = item.grid_row
            col = item.grid_col

            if row_counts[row] > 1:
                # Multiple elements in this row -> parallel
                if row not in row_to_group:
                    row_to_group[row] = parallel_group_id
                    parallel_group_id += 1
                elem.parallel_group = row_to_group[row]
                elem.connection_type = ConnectionType.PARALLEL_MEMBER
            else:
                # Single element in row -> series
                elem.parallel_group = 0
                elem.connection_type = ConnectionType.SERIES

            model.add_element(elem)

        # Set default preload from bolt elements if any have preload_force > 0
        max_preload = 0.0
        for elem in model.elements:
            pf = getattr(elem, 'preload_force', 0.0)
            if pf > max_preload:
                max_preload = pf
        if max_preload > 0:
            model.global_loading.F_preload = max_preload

        # BUG-01 fix: copy ContactInterface objects from schematic to model
        for contact_iface in self.contacts.values():
            model.contacts.append(contact_iface)

        return model


# =============================================================================
# CONTACT DIALOG
# =============================================================================

class ContactDialog(QDialog):
    """
    Context-sensitive dialog for defining contact interface between two elements.

    Automatically detects element pair types and shows appropriate contact
    configuration options:
    - Thread contact (stud-nut): Shows thread fillet model configuration
    - Bearing contacts: Shows friction coefficients for bearing surfaces
    - Gasket contacts: Shows gasket-specific parameters
    """

    # Contact type descriptions for UI
    SPECIFIC_TYPE_DESCRIPTIONS = {
        SpecificContactType.THREAD_CONTACT: "Thread engagement (stud-nut interface with load distribution)",
        SpecificContactType.BOLT_HEAD_WASHER: "Bolt head bearing on washer surface",
        SpecificContactType.BOLT_HEAD_FLANGE: "Bolt head bearing directly on flange",
        SpecificContactType.NUT_WASHER: "Nut bearing on washer surface",
        SpecificContactType.NUT_FLANGE: "Nut bearing directly on flange",
        SpecificContactType.WASHER_FLANGE: "Washer bearing on flange surface",
        SpecificContactType.WASHER_WASHER: "Stacked washers (e.g., flat + lock washer)",
        SpecificContactType.FLANGE_FLANGE: "Flange-to-flange metal seal interface",
        SpecificContactType.FLANGE_GASKET: "Flange bearing on gasket surface",
        SpecificContactType.FLANGE_MEMBER: "Flange bearing on member surface",
        SpecificContactType.GENERIC_CONTACT: "Generic mechanical contact interface",
    }

    def __init__(self, elem_a: ElementGraphicsItem, elem_b: ElementGraphicsItem,
                 existing_contact: Optional[ContactInterface] = None,
                 parent=None):
        super().__init__(parent)

        self.elem_a = elem_a
        self.elem_b = elem_b

        # Determine specific contact type from element pair
        self.specific_type = SpecificContactType.from_element_pair(
            elem_a.element_data.type,
            elem_b.element_data.type
        )

        # Create or use existing contact
        if existing_contact:
            self.contact = existing_contact
        else:
            # Get default friction for this contact type
            default_mu = self.specific_type.default_friction_static
            self.contact = ContactInterface(
                element_a_id=elem_a.element_id,
                element_b_id=elem_b.element_id,
                specific_type=self.specific_type,
                mu_static=default_mu,
                mu_kinetic=default_mu * 0.85  # Kinetic typically 85% of static
            )

        self.setWindowTitle("Define Contact Interface")
        self.setMinimumSize(450, 600 if self.specific_type.requires_thread_model else 520)
        self._setup_ui()

    def _setup_ui(self):
        """Setup dialog UI based on contact type."""
        layout = QVBoxLayout(self)

        # Header with contact type identification
        header_text = f"{self.elem_a.visual.name} ↔ {self.elem_b.visual.name}"
        header = QLabel(header_text)
        header.setStyleSheet(f"font-size: 12pt; font-weight: bold; color: {Theme.BLUE};")
        layout.addWidget(header)

        # Specific contact type indicator
        type_name = self.specific_type.value.replace("_", " ").title()
        type_desc = self.SPECIFIC_TYPE_DESCRIPTIONS.get(self.specific_type, "")
        type_label = QLabel(f"<b>{type_name}</b><br><i>{type_desc}</i>")
        type_label.setStyleSheet(f"color: {Theme.PEACH}; padding: 5px;")
        type_label.setWordWrap(True)
        layout.addWidget(type_label)

        # Contact behavior type
        behavior_group = QGroupBox("Contact Behavior")
        behavior_layout = QVBoxLayout(behavior_group)

        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Rigid (infinite stiffness)",
            "Elastic (linear spring)",
            "Frictional (Coulomb)",
            "Nonlinear (Hertzian)"
        ])
        # Default to frictional for most contacts
        self.type_combo.setCurrentIndex(2)
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        behavior_layout.addWidget(self.type_combo)

        layout.addWidget(behavior_group)

        # Stiffness parameters
        stiffness_group = QGroupBox("Stiffness Parameters")
        stiffness_layout = QFormLayout(stiffness_group)

        self.k_normal_spin = QDoubleSpinBox()
        self.k_normal_spin.setRange(1e6, 1e15)
        self.k_normal_spin.setValue(self.contact.k_normal)
        self.k_normal_spin.setDecimals(2)
        self.k_normal_spin.setSuffix(" N/m")

        self.k_tangent_spin = QDoubleSpinBox()
        self.k_tangent_spin.setRange(1e6, 1e15)
        self.k_tangent_spin.setValue(self.contact.k_tangential)
        self.k_tangent_spin.setDecimals(2)
        self.k_tangent_spin.setSuffix(" N/m")

        stiffness_layout.addRow("k_normal:", self.k_normal_spin)
        stiffness_layout.addRow("k_tangential:", self.k_tangent_spin)

        layout.addWidget(stiffness_group)

        # Friction parameters
        friction_group = QGroupBox("Friction Parameters")
        friction_layout = QFormLayout(friction_group)

        self.mu_static_spin = QDoubleSpinBox()
        self.mu_static_spin.setRange(0.01, 1.0)
        self.mu_static_spin.setValue(self.contact.mu_static)
        self.mu_static_spin.setDecimals(3)
        self.mu_static_spin.setToolTip(f"Default for {type_name}: {self.specific_type.default_friction_static:.3f}")

        self.mu_kinetic_spin = QDoubleSpinBox()
        self.mu_kinetic_spin.setRange(0.01, 1.0)
        self.mu_kinetic_spin.setValue(self.contact.mu_kinetic)
        self.mu_kinetic_spin.setDecimals(3)

        friction_layout.addRow("μ_static:", self.mu_static_spin)
        friction_layout.addRow("μ_kinetic:", self.mu_kinetic_spin)

        # Add default friction button
        default_btn = QPushButton("Reset to Default")
        default_btn.clicked.connect(self._reset_friction_defaults)
        friction_layout.addRow("", default_btn)

        layout.addWidget(friction_group)
        self.friction_group = friction_group

        # Thread fillet model (only for thread contacts)
        self.thread_panel = None
        if self.specific_type.requires_thread_model:
            self._setup_thread_panel(layout)

        # Transfer efficiency
        transfer_group = QGroupBox("Load Transfer")
        transfer_layout = QFormLayout(transfer_group)

        self.transfer_slider = QSlider(Qt.Orientation.Horizontal)
        self.transfer_slider.setRange(0, 100)
        self.transfer_slider.setValue(int(self.contact.transfer_efficiency * 100))
        self.transfer_label = QLabel(f"{self.contact.transfer_efficiency*100:.0f}%")
        self.transfer_slider.valueChanged.connect(
            lambda v: self.transfer_label.setText(f"{v}%"))

        transfer_layout.addRow("Transfer efficiency:", self.transfer_slider)
        transfer_layout.addRow("", self.transfer_label)

        layout.addWidget(transfer_group)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._on_type_changed(self.type_combo.currentIndex())

    def _setup_thread_panel(self, parent_layout: QVBoxLayout):
        """Setup thread fillet model panel for thread contacts."""
        thread_group = QGroupBox("Thread Load Distribution (Fillet Model)")
        thread_layout = QFormLayout(thread_group)

        # Get existing thread model or create default
        thread_model = self.contact.thread_model or ThreadFilletModel()

        # Number of fillets
        self.n_fillets_spin = QSpinBox()
        self.n_fillets_spin.setRange(1, 20)
        self.n_fillets_spin.setValue(thread_model.n_fillets)
        self.n_fillets_spin.setToolTip("Number of engaged thread fillets")
        thread_layout.addRow("Engaged threads:", self.n_fillets_spin)

        # Thread pitch
        self.pitch_spin = QDoubleSpinBox()
        self.pitch_spin.setRange(0.25, 6.0)
        self.pitch_spin.setValue(thread_model.pitch)
        self.pitch_spin.setSuffix(" mm")
        self.pitch_spin.setDecimals(2)
        thread_layout.addRow("Thread pitch:", self.pitch_spin)

        # Distribution model
        self.dist_combo = QComboBox()
        self.dist_combo.addItems([
            "Uniform (equal load)",
            "Linear (decreasing)",
            "Power Law (n^β)",
            "Exponential (Sopwith)",
            "Yamamoto (research)"
        ])
        dist_map = {"uniform": 0, "linear": 1, "power_law": 2, "exponential": 3, "yamamoto": 4}
        self.dist_combo.setCurrentIndex(dist_map.get(thread_model.distribution, 3))
        self.dist_combo.currentIndexChanged.connect(self._on_distribution_changed)
        thread_layout.addRow("Distribution:", self.dist_combo)

        # Decay constant (for exponential)
        self.decay_spin = QDoubleSpinBox()
        self.decay_spin.setRange(0.1, 1.0)
        self.decay_spin.setValue(thread_model.decay_constant)
        self.decay_spin.setDecimals(2)
        self.decay_spin.setToolTip("λ for Sopwith exponential decay (typical 0.2-0.5)")
        self.decay_label = QLabel("Decay λ:")
        thread_layout.addRow(self.decay_label, self.decay_spin)

        # Power exponent (for power law)
        self.power_spin = QDoubleSpinBox()
        self.power_spin.setRange(0.5, 5.0)
        self.power_spin.setValue(thread_model.power_exponent)
        self.power_spin.setDecimals(2)
        self.power_spin.setToolTip("β exponent for power law distribution")
        self.power_label = QLabel("Exponent β:")
        thread_layout.addRow(self.power_label, self.power_spin)

        # Yamamoto gamma (for yamamoto)
        self.gamma_spin = QDoubleSpinBox()
        self.gamma_spin.setRange(0.1, 2.0)
        self.gamma_spin.setValue(thread_model.yamamoto_gamma)
        self.gamma_spin.setDecimals(2)
        self.gamma_spin.setToolTip("γ parameter for Yamamoto distribution")
        self.gamma_label = QLabel("Gamma γ:")
        thread_layout.addRow(self.gamma_label, self.gamma_spin)

        parent_layout.addWidget(thread_group)
        self.thread_panel = thread_group

        # Initial visibility
        self._on_distribution_changed(self.dist_combo.currentIndex())

    def _on_distribution_changed(self, index: int):
        """Update visibility of distribution parameters."""
        if not self.thread_panel:
            return

        # Show/hide based on distribution
        is_exponential = index == 3
        is_power_law = index == 2
        is_yamamoto = index == 4

        self.decay_label.setVisible(is_exponential)
        self.decay_spin.setVisible(is_exponential)
        self.power_label.setVisible(is_power_law)
        self.power_spin.setVisible(is_power_law)
        self.gamma_label.setVisible(is_yamamoto)
        self.gamma_spin.setVisible(is_yamamoto)

    def _on_type_changed(self, index: int):
        """Handle contact behavior type change."""
        is_friction = index == 2
        self.friction_group.setEnabled(is_friction)

    def _reset_friction_defaults(self):
        """Reset friction to default values for this contact type."""
        default_mu = self.specific_type.default_friction_static
        self.mu_static_spin.setValue(default_mu)
        self.mu_kinetic_spin.setValue(default_mu * 0.85)

    def get_contact(self) -> ContactInterface:
        """Get configured contact interface."""
        type_map = {
            0: ContactType.RIGID,
            1: ContactType.ELASTIC,
            2: ContactType.FRICTIONAL,
            3: ContactType.NONLINEAR
        }

        self.contact.contact_type = type_map[self.type_combo.currentIndex()]
        self.contact.specific_type = self.specific_type
        self.contact.k_normal = self.k_normal_spin.value()
        self.contact.k_tangential = self.k_tangent_spin.value()
        self.contact.mu_static = self.mu_static_spin.value()
        self.contact.mu_kinetic = self.mu_kinetic_spin.value()
        self.contact.transfer_efficiency = self.transfer_slider.value() / 100.0

        # Thread model for thread contacts
        if self.specific_type.requires_thread_model and self.thread_panel:
            dist_map = {0: "uniform", 1: "linear", 2: "power_law", 3: "exponential", 4: "yamamoto"}
            self.contact.thread_model = ThreadFilletModel(
                n_fillets=self.n_fillets_spin.value(),
                pitch=self.pitch_spin.value(),
                decay_constant=self.decay_spin.value(),
                distribution=dist_map.get(self.dist_combo.currentIndex(), "exponential"),
                power_exponent=self.power_spin.value(),
                yamamoto_gamma=self.gamma_spin.value()
            )

        return self.contact


# =============================================================================
# THREAD FILLET PANEL
# =============================================================================

class ThreadFilletPanel(QGroupBox):
    """
    Panel for configuring thread fillet model with multiple load distribution laws.

    Based on:
    - Sopwith exponential decay model
    - Yamamoto research-based distribution
    - Linear and power law options
    """

    config_changed = pyqtSignal(ThreadFilletModel)
    expand_requested = pyqtSignal()  # Request to expand to individual fillet elements

    def __init__(self, parent=None):
        super().__init__("Thread Load Distribution", parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup panel UI."""
        layout = QVBoxLayout(self)

        form = QFormLayout()

        # Number of fillets
        self.n_fillets_spin = QSpinBox()
        self.n_fillets_spin.setRange(3, 20)
        self.n_fillets_spin.setValue(6)
        self.n_fillets_spin.setToolTip("Number of engaged thread fillets (typically 5-10)")
        self.n_fillets_spin.valueChanged.connect(self._update_preview)

        # Distribution type
        self.dist_combo = QComboBox()
        self.dist_combo.addItems([
            "Equal (1/n)",
            "Linear",
            "Power Law",
            "Exponential (Sopwith)",
            "Yamamoto"
        ])
        self.dist_combo.setCurrentText("Exponential (Sopwith)")
        self.dist_combo.setToolTip(
            "Load distribution law:\n"
            "- Equal: Uniform load on all threads\n"
            "- Linear: Linearly decreasing from first thread\n"
            "- Power Law: (n-i+1)^β distribution\n"
            "- Exponential (Sopwith): e^(-λi) decay - most common\n"
            "- Yamamoto: sinh-based, matches experiments"
        )
        self.dist_combo.currentTextChanged.connect(self._on_dist_changed)

        form.addRow("Engaged fillets:", self.n_fillets_spin)
        form.addRow("Distribution law:", self.dist_combo)

        layout.addLayout(form)

        # Parameters group (shown/hidden based on distribution)
        self.params_group = QGroupBox("Distribution Parameters")
        params_layout = QFormLayout(self.params_group)

        # Lambda (exponential decay)
        self.lambda_spin = QDoubleSpinBox()
        self.lambda_spin.setRange(0.1, 1.0)
        self.lambda_spin.setValue(0.38)
        self.lambda_spin.setDecimals(2)
        self.lambda_spin.setSingleStep(0.05)
        self.lambda_spin.setToolTip("Decay rate λ (typical 0.3-0.5)\nHigher = more load on first threads")
        self.lambda_spin.valueChanged.connect(self._update_preview)
        self.lambda_label = QLabel("λ (decay rate):")

        # Beta (power law)
        self.beta_spin = QDoubleSpinBox()
        self.beta_spin.setRange(0.5, 4.0)
        self.beta_spin.setValue(2.0)
        self.beta_spin.setDecimals(1)
        self.beta_spin.setSingleStep(0.5)
        self.beta_spin.setToolTip("Power exponent β (typical 1.5-2.0)\nHigher = more load on first threads")
        self.beta_spin.valueChanged.connect(self._update_preview)
        self.beta_label = QLabel("β (exponent):")

        # Gamma (Yamamoto)
        self.gamma_spin = QDoubleSpinBox()
        self.gamma_spin.setRange(0.1, 1.0)
        self.gamma_spin.setValue(0.5)
        self.gamma_spin.setDecimals(2)
        self.gamma_spin.setSingleStep(0.1)
        self.gamma_spin.setToolTip("Yamamoto parameter γ\nDepends on thread/nut stiffness ratio")
        self.gamma_spin.valueChanged.connect(self._update_preview)
        self.gamma_label = QLabel("γ (Yamamoto):")

        params_layout.addRow(self.lambda_label, self.lambda_spin)
        params_layout.addRow(self.beta_label, self.beta_spin)
        params_layout.addRow(self.gamma_label, self.gamma_spin)

        layout.addWidget(self.params_group)

        # Preview
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(180)
        self.preview_text.setStyleSheet(f"""
            background-color: {Theme.SURFACE0};
            color: {Theme.TEXT};
            font-family: {Theme.FONT_MONO};
            font-size: 9pt;
        """)
        layout.addWidget(self.preview_text)

        # Expand button
        self.expand_btn = QPushButton("Expand to Individual Thread Elements")
        self.expand_btn.setToolTip(
            "Create separate MSD elements for each thread fillet.\n"
            "Uses the configured load distribution to set individual stiffnesses.\n"
            "Useful for detailed analysis of thread load sharing."
        )
        self.expand_btn.clicked.connect(self.expand_requested.emit)
        layout.addWidget(self.expand_btn)

        # Initial state
        self._on_dist_changed(self.dist_combo.currentText())
        self._update_preview()

    def _on_dist_changed(self, dist_text: str):
        """Update visible parameters based on distribution law."""
        # Hide all parameter rows initially
        self.lambda_label.setVisible(False)
        self.lambda_spin.setVisible(False)
        self.beta_label.setVisible(False)
        self.beta_spin.setVisible(False)
        self.gamma_label.setVisible(False)
        self.gamma_spin.setVisible(False)

        if "Exponential" in dist_text:
            self.lambda_label.setVisible(True)
            self.lambda_spin.setVisible(True)
            self.params_group.setVisible(True)
        elif "Power" in dist_text:
            self.beta_label.setVisible(True)
            self.beta_spin.setVisible(True)
            self.params_group.setVisible(True)
        elif "Yamamoto" in dist_text:
            self.gamma_label.setVisible(True)
            self.gamma_spin.setVisible(True)
            self.params_group.setVisible(True)
        else:
            # Equal or Linear - no parameters
            self.params_group.setVisible(False)

        self._update_preview()

    def _update_preview(self):
        """Update the load distribution preview."""
        try:
            from bolt_analysis_studio.core.databases import calculate_thread_load_factors, LoadDistributionLaw

            n = self.n_fillets_spin.value()
            dist_text = self.dist_combo.currentText()

            # Map UI text to enum
            law_map = {
                "Equal (1/n)": LoadDistributionLaw.EQUAL,
                "Linear": LoadDistributionLaw.LINEAR,
                "Power Law": LoadDistributionLaw.POWER,
                "Exponential (Sopwith)": LoadDistributionLaw.EXPONENTIAL,
                "Yamamoto": LoadDistributionLaw.YAMAMOTO,
            }
            law = law_map.get(dist_text, LoadDistributionLaw.EXPONENTIAL)

            factors = calculate_thread_load_factors(
                n_threads=n,
                law=law,
                beta=self.beta_spin.value(),
                lam=self.lambda_spin.value(),
                gamma=self.gamma_spin.value()
            )
        except ImportError:
            # Fallback if database not available
            factors = self._calculate_factors_fallback()

        # Calculate stress concentration factor
        uniform_factor = 1.0 / len(factors)
        stress_factor = factors[0] / uniform_factor if factors else 1.0

        lines = [f"Thread Load Distribution ({self.dist_combo.currentText()}):", "-" * 35]
        max_bar = 18

        for i, f in enumerate(factors):
            bar_len = int(f / max(factors) * max_bar) if max(factors) > 0 else 0
            bar = "█" * bar_len + "░" * (max_bar - bar_len)
            lines.append(f"T{i+1:2d} {bar} {f*100:5.1f}%")

        lines.append("-" * 35)
        lines.append(f"First fillet load factor: {factors[0]*100:.1f}%")
        lines.append(f"Stress concentration: {stress_factor:.2f}× uniform")

        self.preview_text.setPlainText("\n".join(lines))

        # Emit the model
        model = self.get_model()
        self.config_changed.emit(model)

    def _calculate_factors_fallback(self) -> List[float]:
        """Fallback calculation if database not available."""
        import math
        n = self.n_fillets_spin.value()
        dist_text = self.dist_combo.currentText()

        if "Equal" in dist_text:
            return [1.0 / n] * n
        elif "Linear" in dist_text:
            return [2 * (n - i) / (n * (n + 1)) for i in range(n)]
        elif "Power" in dist_text:
            beta = self.beta_spin.value()
            raw = [(n - i) ** beta for i in range(n)]
            total = sum(raw)
            return [f / total for f in raw]
        elif "Exponential" in dist_text:
            lam = self.lambda_spin.value()
            raw = [math.exp(-lam * i) for i in range(n)]
            total = sum(raw)
            return [f / total for f in raw]
        elif "Yamamoto" in dist_text:
            gamma = self.gamma_spin.value()
            raw = [math.sinh(gamma * (n - i + 0.5)) for i in range(n)]
            total = sum(raw)
            return [f / total for f in raw]
        return [1.0 / n] * n

    def get_model(self) -> ThreadFilletModel:
        """Get current thread fillet model."""
        dist_map = {
            "Equal (1/n)": "uniform",
            "Linear": "linear",
            "Power Law": "power_law",
            "Exponential (Sopwith)": "exponential",
            "Yamamoto": "yamamoto",
        }

        return ThreadFilletModel(
            n_fillets=self.n_fillets_spin.value(),
            decay_constant=self.lambda_spin.value(),
            distribution=dist_map.get(self.dist_combo.currentText(), "exponential"),
            power_exponent=self.beta_spin.value()
        )

    def set_model(self, model: ThreadFilletModel):
        """Set thread fillet model."""
        self.n_fillets_spin.setValue(model.n_fillets)
        self.lambda_spin.setValue(model.decay_constant)
        self.beta_spin.setValue(model.power_exponent)

        dist_map = {
            "uniform": "Equal (1/n)",
            "linear": "Linear",
            "power_law": "Power Law",
            "exponential": "Exponential (Sopwith)",
            "yamamoto": "Yamamoto",
        }
        self.dist_combo.setCurrentText(dist_map.get(model.distribution, "Exponential (Sopwith)"))


# =============================================================================
# WAVEFORM PREVIEW WIDGET  (3.14)
# =============================================================================

class WaveformPreviewWidget(QWidget):
    """Live QPainter waveform preview for LoadDialog (3.14).

    Shows ~3 cycles of the selected waveform (Static, Harmonic, Impact) as a
    polyline.  No matplotlib dependency — pure Qt drawing.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(64)
        self.setMaximumHeight(80)
        self._mag   = 1.0   # normalised amplitude (always 1 here; we show shape)
        self._freq  = 10.0  # Hz
        self._phase = 0.0   # deg
        self._mode  = "static"    # "static" | "harmonic" | "impact"

    def set_params(self, mag: float, freq: float, phase_deg: float, mode: str):
        self._mag   = abs(mag) if mag != 0 else 1.0
        self._freq  = max(freq, 0.1)
        self._phase = phase_deg
        self._mode  = mode.lower()
        self.update()

    def paintEvent(self, event):
        import math
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        bg = QColor(Theme.BASE)
        painter.fillRect(self.rect(), bg)

        # Axis baseline
        mid_y = h / 2
        painter.setPen(QPen(QColor(Theme.SURFACE0), 1))
        painter.drawLine(0, int(mid_y), w, int(mid_y))

        # Waveform
        N = 300
        mode = self._mode
        ph_r = math.radians(self._phase)

        pts = []
        for i in range(N):
            t_norm = i / (N - 1)        # 0…1 across widget width
            t_cyc  = t_norm * 3.0       # 3 cycles worth

            if mode == "static":
                y_norm = 0.8            # flat positive line
            elif mode == "harmonic":
                y_norm = 0.8 * math.sin(2 * math.pi * t_cyc + ph_r)
            elif mode == "impact":
                # Narrow half-sine bump repeated
                frac = t_cyc % 1.0
                if frac < 0.12:
                    y_norm = 0.8 * math.sin(math.pi * frac / 0.12)
                else:
                    y_norm = 0.0
            else:
                y_norm = 0.8 * math.sin(2 * math.pi * t_cyc + ph_r)

            px = int(t_norm * w)
            py = int(mid_y - y_norm * (mid_y - 6))
            pts.append(QPointF(px, py))

        pen = QPen(QColor(Theme.BLUE), 1.5)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        for i in range(1, len(pts)):
            painter.drawLine(pts[i - 1], pts[i])

        # Label
        lbl_col = QColor(Theme.SUBTEXT)
        painter.setPen(lbl_col)
        painter.setFont(QFont("Monospace", 7))
        lbl = {"static": "STATIC", "harmonic": f"HARM  {self._freq:.1f} Hz",
               "impact": "IMPACT"}.get(mode, mode.upper())
        painter.drawText(4, h - 4, lbl)

        painter.end()


# =============================================================================
# LOAD APPLICATION DIALOG
# =============================================================================

class LoadDialog(QDialog):
    """Dialog for applying loads and constraints."""

    def __init__(self, element: ElementGraphicsItem, parent=None):
        super().__init__(parent)

        self.element = element
        self.setWindowTitle(f"Apply Load/Constraint - {element.visual.name}")
        self.setMinimumSize(450, 550)
        self._setup_ui()
        self._load_existing()

    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)

        # Tabs for loads vs constraints
        tabs = QTabWidget()

        # === LOADS TAB ===
        loads_tab = QWidget()
        loads_layout = QVBoxLayout(loads_tab)

        # External force section
        force_group = QGroupBox("External Load")
        force_layout = QFormLayout(force_group)

        self.force_check = QCheckBox("Apply External Load")

        self.load_type_combo = QComboBox()
        self.load_type_combo.addItems([
            "Axial (tension/compression)",
            "Shear (transverse)",
            "Bending (moment)",
            "Torsion",
            "Impact (impulse)"
        ])
        self.load_type_combo.currentTextChanged.connect(self._on_load_type_changed)
        self.load_type_combo.currentTextChanged.connect(
            lambda _: self._update_waveform_preview() if hasattr(self, '_waveform_preview') else None
        )

        self.force_spin = QDoubleSpinBox()
        self.force_spin.setRange(-1e7, 1e7)
        self.force_spin.setValue(10000)
        self.force_spin.setDecimals(0)

        self.force_unit_label = QLabel("N")

        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["X (axial)", "Y (transverse)", "Z (transverse)"])

        force_layout.addRow(self.force_check)
        force_layout.addRow("Load type:", self.load_type_combo)
        force_layout.addRow("Magnitude:", self.force_spin)
        force_layout.addRow("", self.force_unit_label)
        force_layout.addRow("Direction:", self.direction_combo)

        loads_layout.addWidget(force_group)

        # Time variation section
        time_group = QGroupBox("Time Variation")
        time_layout = QFormLayout(time_group)

        self.time_var_combo = QComboBox()
        self.time_var_combo.addItems(["Static", "Harmonic (sinusoidal)", "Transient (time history)"])
        self.time_var_combo.currentTextChanged.connect(self._on_time_var_changed)

        self.freq_spin = QDoubleSpinBox()
        self.freq_spin.setRange(0.1, 10000)
        self.freq_spin.setValue(100)
        self.freq_spin.setSuffix(" Hz")

        self.phase_spin = QDoubleSpinBox()
        self.phase_spin.setRange(0, 360)
        self.phase_spin.setValue(0)
        self.phase_spin.setSuffix(" deg")

        self.impact_duration_spin = QDoubleSpinBox()
        self.impact_duration_spin.setRange(0.0001, 0.1)
        self.impact_duration_spin.setValue(0.001)
        self.impact_duration_spin.setDecimals(4)
        self.impact_duration_spin.setSuffix(" s")
        self.impact_duration_spin.setVisible(False)

        self.impact_duration_label = QLabel("Impact duration:")
        self.impact_duration_label.setVisible(False)

        # 3.14 — Waveform preview
        self._waveform_preview = WaveformPreviewWidget()
        self._waveform_preview.setToolTip("Live waveform preview (shape only; scale = magnitude)")

        time_layout.addRow("Variation:", self.time_var_combo)
        time_layout.addRow("Frequency:", self.freq_spin)
        time_layout.addRow("Phase:", self.phase_spin)
        time_layout.addRow(self.impact_duration_label, self.impact_duration_spin)
        time_layout.addRow("Preview:", self._waveform_preview)

        # Connect preview updates
        self.force_spin.valueChanged.connect(self._update_waveform_preview)
        self.freq_spin.valueChanged.connect(self._update_waveform_preview)
        self.phase_spin.valueChanged.connect(self._update_waveform_preview)
        self.time_var_combo.currentTextChanged.connect(self._update_waveform_preview)
        self._update_waveform_preview()

        loads_layout.addWidget(time_group)
        loads_layout.addStretch()

        tabs.addTab(loads_tab, "Loads")

        # === CONSTRAINTS TAB ===
        constraints_tab = QWidget()
        constraints_layout = QVBoxLayout(constraints_tab)

        bc_group = QGroupBox("Boundary Conditions")
        bc_layout = QVBoxLayout(bc_group)

        self.fixed_check = QCheckBox("Fixed (u = 0) - All DOFs constrained")

        prescribed_layout = QHBoxLayout()
        self.prescribed_check = QCheckBox("Prescribed displacement:")
        self.prescribed_spin = QDoubleSpinBox()
        self.prescribed_spin.setRange(-0.1, 0.1)
        self.prescribed_spin.setValue(0.001)
        self.prescribed_spin.setDecimals(6)
        self.prescribed_spin.setSuffix(" m")
        prescribed_layout.addWidget(self.prescribed_check)
        prescribed_layout.addWidget(self.prescribed_spin)

        spring_layout = QHBoxLayout()
        self.spring_check = QCheckBox("Spring to ground:")
        self.spring_spin = QDoubleSpinBox()
        self.spring_spin.setRange(1e3, 1e15)
        self.spring_spin.setValue(1e9)
        self.spring_spin.setDecimals(2)
        self.spring_spin.setSuffix(" N/m")
        spring_layout.addWidget(self.spring_check)
        spring_layout.addWidget(self.spring_spin)

        bc_layout.addWidget(self.fixed_check)
        bc_layout.addLayout(prescribed_layout)
        bc_layout.addLayout(spring_layout)

        constraints_layout.addWidget(bc_group)
        constraints_layout.addStretch()

        tabs.addTab(constraints_tab, "Constraints")

        layout.addWidget(tabs)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_load_type_changed(self, text: str):
        """Update UI based on load type."""
        if "Axial" in text:
            self.force_unit_label.setText("N (force)")
            self.direction_combo.setCurrentIndex(0)
        elif "Shear" in text:
            self.force_unit_label.setText("N (force)")
            self.direction_combo.setCurrentIndex(1)
        elif "Bending" in text:
            self.force_unit_label.setText("N·m (moment)")
        elif "Torsion" in text:
            self.force_unit_label.setText("N·m (torque)")
        elif "Impact" in text:
            self.force_unit_label.setText("N (peak force)")
            self.impact_duration_label.setVisible(True)
            self.impact_duration_spin.setVisible(True)
            return

        self.impact_duration_label.setVisible(False)
        self.impact_duration_spin.setVisible(False)

    def _on_time_var_changed(self, text: str):
        """Update UI based on time variation."""
        is_harmonic = "Harmonic" in text
        self.freq_spin.setEnabled(is_harmonic)
        self.phase_spin.setEnabled(is_harmonic)
        self._update_waveform_preview()

    def _update_waveform_preview(self):
        """Refresh waveform preview widget (3.14)."""
        var_text = self.time_var_combo.currentText()
        if "Harmonic" in var_text:
            mode = "harmonic"
        elif "Transient" in var_text:
            mode = "harmonic"   # show sinusoidal shape as placeholder
        else:
            mode = "static"
        # Check load type for impact shape
        if hasattr(self, 'load_type_combo') and "Impact" in self.load_type_combo.currentText():
            mode = "impact"
        self._waveform_preview.set_params(
            mag=self.force_spin.value(),
            freq=self.freq_spin.value(),
            phase_deg=self.phase_spin.value(),
            mode=mode,
        )

    def _load_existing(self):
        """Load existing loads/constraints from element."""
        elem_data = self.element.element_data

        # Load existing loads
        for load in elem_data.applied_loads:
            if load.load_type in ("force", "axial", "shear", "bending", "torsion", "impact"):
                self.force_check.setChecked(True)
                self.force_spin.setValue(load.magnitude)

        # Load existing constraints
        for constraint in elem_data.constraints:
            if constraint.constraint_type == ConstraintType.FIXED:
                self.fixed_check.setChecked(True)
            elif constraint.constraint_type == ConstraintType.PRESCRIBED:
                self.prescribed_check.setChecked(True)
                self.prescribed_spin.setValue(constraint.value)
            elif constraint.constraint_type == ConstraintType.SPRING:
                self.spring_check.setChecked(True)
                self.spring_spin.setValue(constraint.value)

    def get_loads(self) -> List[AppliedLoad]:
        """Get configured loads."""
        loads = []

        time_var_map = {
            "Static": TimeVariation.STATIC,
            "Harmonic (sinusoidal)": TimeVariation.HARMONIC,
            "Transient (time history)": TimeVariation.TRANSIENT
        }
        time_var = time_var_map.get(self.time_var_combo.currentText(), TimeVariation.STATIC)

        load_type_map = {
            "Axial (tension/compression)": "axial",
            "Shear (transverse)": "shear",
            "Bending (moment)": "bending",
            "Torsion": "torsion",
            "Impact (impulse)": "impact"
        }

        if self.force_check.isChecked():
            load_type = load_type_map.get(self.load_type_combo.currentText(), "axial")

            # For impact, use transient
            if load_type == "impact":
                time_var = TimeVariation.TRANSIENT

            loads.append(AppliedLoad(
                element_id=self.element.element_id,
                load_type=load_type,
                magnitude=self.force_spin.value(),
                direction=self.direction_combo.currentText().split()[0].lower(),
                time_variation=time_var,
                frequency=self.freq_spin.value() if time_var == TimeVariation.HARMONIC else 0,
                phase=math.radians(self.phase_spin.value())
            ))

        return loads

    def get_constraints(self) -> List[Constraint]:
        """Get configured constraints."""
        constraints = []

        if self.fixed_check.isChecked():
            constraints.append(Constraint(
                element_id=self.element.element_id,
                constraint_type=ConstraintType.FIXED
            ))

        if self.prescribed_check.isChecked():
            constraints.append(Constraint(
                element_id=self.element.element_id,
                constraint_type=ConstraintType.PRESCRIBED,
                value=self.prescribed_spin.value()
            ))

        if self.spring_check.isChecked():
            constraints.append(Constraint(
                element_id=self.element.element_id,
                constraint_type=ConstraintType.SPRING,
                value=self.spring_spin.value()
            ))

        return constraints


# =============================================================================
# CONTACT PROPERTIES DIALOG
# =============================================================================

class ContactLocationDiagram(QWidget):
    """Miniature bolt cross-section diagram highlighting the active contact (3.13)."""

    # contact_type → (label, highlighted rect as fraction of widget: x, y, w, h)
    _REGIONS = {
        "BEARING_HEAD":    ("Head bearing",     0.3, 0.02, 0.4, 0.14),
        "BEARING_NUT":     ("Nut bearing",      0.3, 0.84, 0.4, 0.14),
        "THREAD":          ("Thread interface", 0.3, 0.50, 0.4, 0.18),
        "WASHER_CONTACT":  ("Washer–Flange",    0.2, 0.18, 0.6, 0.10),
        "GASKET_CONTACT":  ("Gasket interface", 0.1, 0.44, 0.8, 0.12),
        "FLANGE_FLANGE":   ("Flange–Flange",    0.1, 0.44, 0.8, 0.12),
        "GENERIC_CONTACT": ("Contact surface",  0.2, 0.30, 0.6, 0.12),
    }

    def __init__(self, contact_type: str, parent=None):
        super().__init__(parent)
        self._contact_type = contact_type
        self.setFixedHeight(90)
        self.setMinimumWidth(180)
        self.setToolTip(f"Contact location: {contact_type}")

    def paintEvent(self, event):
        import math
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        painter.fillRect(self.rect(), QColor(Theme.BASE))

        # Draw simplified bolt silhouette (shank + flanges)
        bolt_pen = QPen(QColor(Theme.SUBTEXT), 1)
        painter.setPen(bolt_pen)
        shank_x = int(w * 0.42)
        shank_w = int(w * 0.16)
        painter.fillRect(shank_x, int(h * 0.12), shank_w, int(h * 0.76),
                         QColor(Theme.SURFACE0))
        # Head
        head_x = int(w * 0.30)
        head_w = int(w * 0.40)
        painter.fillRect(head_x, int(h * 0.04), head_w, int(h * 0.12),
                         QColor(Theme.SURFACE1))
        # Nut
        painter.fillRect(head_x, int(h * 0.84), head_w, int(h * 0.12),
                         QColor(Theme.SURFACE1))
        # Flanges (thin slabs)
        fl_x, fl_w = int(w * 0.10), int(w * 0.80)
        for fy in [0.18, 0.40, 0.52, 0.74]:
            painter.fillRect(fl_x, int(h * fy), fl_w, int(h * 0.10),
                             QColor(Theme.SURFACE0))

        # Highlight active region
        region = self._REGIONS.get(self._contact_type)
        if region:
            label, rx, ry, rw, rh = region
            highlight = QColor(Theme.YELLOW)
            highlight.setAlpha(120)
            painter.setBrush(QBrush(highlight))
            painter.setPen(QPen(QColor(Theme.YELLOW), 1))
            painter.drawRect(int(rx * w), int(ry * h), int(rw * w), int(rh * h))
            # Label
            painter.setPen(QColor(Theme.YELLOW))
            painter.setFont(QFont("Monospace", 7))
            painter.drawText(4, h - 4, label)

        painter.end()


class ContactPropertiesDialog(QDialog):
    """
    Modal dialog for editing the contact interface properties of a contact element.

    Mirrors the Contact > Per-Element inspector panels but in a standalone dialog,
    consistent with the LoadDialog pattern.  Supports THREAD, BEARING_HEAD/NUT,
    GASKET_CONTACT and all other contact types.

    Properties are persisted on ``element_data.contact_props`` (a plain dict).
    """

    _DEFAULTS: dict = {
        # General contact interface
        "k_normal":       1e10,
        "k_tangential":   5e9,
        "c_normal":       100.0,
        "c_tangential":   50.0,
        # μ_static / μ_kinetic are overridden by mu_initial in __init__ (Phase 2.1)
        "mu_static":      0.12,
        "mu_kinetic":     0.10,
        # Thread-specific
        "pitch":              1.75,
        "mean_radius":        10.0,
        "engagement_length":  20.0,
        # Bearing-specific
        "inner_radius":       6.5,
        "outer_radius":       10.0,
        "surface_roughness":  1.6,
        # Gasket-specific
        "gasket_type":            0,
        "gasket_thickness":       1.5,
        "compression_modulus":  100.0,
        "hertz_exponent":         1.5,
        "creep_coeff":            0.05,
    }

    def __init__(self, element: 'ElementGraphicsItem', parent=None,
                 mu_initial: float = 0.12):
        super().__init__(parent)
        self.element = element
        elem_type = element.element_type

        self.setWindowTitle(
            f"Contact Properties \u2014 {element.visual.name} #{element.element_id}"
        )
        self.setMinimumWidth(380)
        self.setSizeGripEnabled(True)

        # Merge stored props with defaults so every key is always present.
        # μ values default to the global mu_initial (Phase 2.1); stored props
        # on the element override these defaults when the element was edited before.
        self._props = dict(self._DEFAULTS)
        self._props["mu_static"]  = mu_initial
        self._props["mu_kinetic"] = round(mu_initial * 0.85, 4)
        stored = getattr(element.element_data, 'contact_props', None)
        if isinstance(stored, dict):
            self._props.update(stored)

        self._setup_ui(elem_type)

    # ------------------------------------------------------------------
    def _setup_ui(self, elem_type: str):
        outer = QVBoxLayout(self)
        outer.setSpacing(8)
        outer.setContentsMargins(10, 10, 10, 10)

        # 3.13 — Contact location diagram at top
        loc_diag = ContactLocationDiagram(elem_type, parent=self)
        outer.addWidget(loc_diag)

        # ── General Contact Interface ──────────────────────────────────
        gen_grp = QGroupBox("Contact Interface")
        gen_form = QFormLayout(gen_grp)
        gen_form.setSpacing(4)

        self.k_normal_spin = QDoubleSpinBox()
        self.k_normal_spin.setRange(1e4, 1e15)
        self.k_normal_spin.setDecimals(3)
        self.k_normal_spin.setSuffix(" N/m")
        self.k_normal_spin.setValue(self._props["k_normal"])
        self.k_normal_spin.setToolTip("Normal contact stiffness (perpendicular to surface)")

        self.k_tangential_spin = QDoubleSpinBox()
        self.k_tangential_spin.setRange(1e3, 1e14)
        self.k_tangential_spin.setDecimals(3)
        self.k_tangential_spin.setSuffix(" N/m")
        self.k_tangential_spin.setValue(self._props["k_tangential"])
        self.k_tangential_spin.setToolTip("Tangential contact stiffness (along surface)")

        self.c_normal_spin = QDoubleSpinBox()
        self.c_normal_spin.setRange(0, 10000)
        self.c_normal_spin.setDecimals(1)
        self.c_normal_spin.setSuffix(" N\u00b7s/m")
        self.c_normal_spin.setValue(self._props["c_normal"])

        self.c_tangential_spin = QDoubleSpinBox()
        self.c_tangential_spin.setRange(0, 10000)
        self.c_tangential_spin.setDecimals(1)
        self.c_tangential_spin.setSuffix(" N\u00b7s/m")
        self.c_tangential_spin.setValue(self._props["c_tangential"])

        self.mu_static_spin = QDoubleSpinBox()
        self.mu_static_spin.setRange(0.01, 1.0)
        self.mu_static_spin.setDecimals(3)
        self.mu_static_spin.setValue(self._props["mu_static"])
        self.mu_static_spin.setToolTip("\u03bcs — static friction coefficient")

        self.mu_kinetic_spin = QDoubleSpinBox()
        self.mu_kinetic_spin.setRange(0.01, 1.0)
        self.mu_kinetic_spin.setDecimals(3)
        self.mu_kinetic_spin.setValue(self._props["mu_kinetic"])
        self.mu_kinetic_spin.setToolTip("\u03bck — kinetic friction coefficient")

        gen_form.addRow("k normal:", self.k_normal_spin)
        gen_form.addRow("k tangential:", self.k_tangential_spin)
        gen_form.addRow("c normal:", self.c_normal_spin)
        gen_form.addRow("c tangential:", self.c_tangential_spin)
        gen_form.addRow("\u03bc static:", self.mu_static_spin)
        gen_form.addRow("\u03bc kinetic:", self.mu_kinetic_spin)
        outer.addWidget(gen_grp)

        # ── Thread-specific ────────────────────────────────────────────
        if elem_type == "THREAD":
            thread_grp = QGroupBox("Thread Geometry")
            thread_form = QFormLayout(thread_grp)
            thread_form.setSpacing(4)

            self.thread_pitch_spin = QDoubleSpinBox()
            self.thread_pitch_spin.setRange(0.5, 6.0)
            self.thread_pitch_spin.setDecimals(2)
            self.thread_pitch_spin.setSuffix(" mm")
            self.thread_pitch_spin.setValue(self._props["pitch"])
            self.thread_pitch_spin.valueChanged.connect(self._update_helix_angle)

            self.thread_radius_spin = QDoubleSpinBox()
            self.thread_radius_spin.setRange(2, 50)
            self.thread_radius_spin.setDecimals(2)
            self.thread_radius_spin.setSuffix(" mm")
            self.thread_radius_spin.setValue(self._props["mean_radius"])
            self.thread_radius_spin.valueChanged.connect(self._update_helix_angle)

            self.helix_angle_lbl = QLabel("--")
            self.helix_angle_lbl.setToolTip(
                "\u03bb = arctan(p / (2\u03c0 \u00b7 r))")

            self.thread_engage_spin = QDoubleSpinBox()
            self.thread_engage_spin.setRange(5, 100)
            self.thread_engage_spin.setDecimals(1)
            self.thread_engage_spin.setSuffix(" mm")
            self.thread_engage_spin.setValue(self._props["engagement_length"])
            self.thread_engage_spin.setToolTip("Thread engagement length")

            thread_form.addRow("Pitch:", self.thread_pitch_spin)
            thread_form.addRow("Mean radius:", self.thread_radius_spin)
            thread_form.addRow("Helix angle:", self.helix_angle_lbl)
            thread_form.addRow("Engagement:", self.thread_engage_spin)
            outer.addWidget(thread_grp)
            self._update_helix_angle()

        # ── Bearing-specific ───────────────────────────────────────────
        elif elem_type in ("BEARING_HEAD", "BEARING_NUT"):
            bearing_grp = QGroupBox("Bearing Surface")
            bearing_form = QFormLayout(bearing_grp)
            bearing_form.setSpacing(4)

            self.inner_r_spin = QDoubleSpinBox()
            self.inner_r_spin.setRange(2, 30)
            self.inner_r_spin.setDecimals(2)
            self.inner_r_spin.setSuffix(" mm")
            self.inner_r_spin.setValue(self._props["inner_radius"])
            self.inner_r_spin.setToolTip("Inner contact radius (hole radius)")
            self.inner_r_spin.valueChanged.connect(self._update_eff_radius)

            self.outer_r_spin = QDoubleSpinBox()
            self.outer_r_spin.setRange(3, 50)
            self.outer_r_spin.setDecimals(2)
            self.outer_r_spin.setSuffix(" mm")
            self.outer_r_spin.setValue(self._props["outer_radius"])
            self.outer_r_spin.setToolTip("Outer contact radius (bearing surface)")
            self.outer_r_spin.valueChanged.connect(self._update_eff_radius)

            self.eff_radius_lbl = QLabel("--")
            self.eff_radius_lbl.setToolTip(
                "r_eff = (2/3)(r_o\u00b3\u2212r_i\u00b3)/(r_o\u00b2\u2212r_i\u00b2)")

            self.roughness_spin = QDoubleSpinBox()
            self.roughness_spin.setRange(0.1, 25.0)
            self.roughness_spin.setDecimals(2)
            self.roughness_spin.setSuffix(" \u03bcm Ra")
            self.roughness_spin.setValue(self._props["surface_roughness"])
            self.roughness_spin.setToolTip("Surface roughness (Ra)")

            bearing_form.addRow("Inner radius:", self.inner_r_spin)
            bearing_form.addRow("Outer radius:", self.outer_r_spin)
            bearing_form.addRow("Effective r:", self.eff_radius_lbl)
            bearing_form.addRow("Roughness:", self.roughness_spin)
            outer.addWidget(bearing_grp)
            self._update_eff_radius()

        # ── Gasket-specific ────────────────────────────────────────────
        elif elem_type == "GASKET_CONTACT":
            gasket_grp = QGroupBox("Gasket Properties")
            gasket_form = QFormLayout(gasket_grp)
            gasket_form.setSpacing(4)

            self.gasket_type_combo = QComboBox()
            self.gasket_type_combo.addItems([
                "Sheet (Compressed fiber)",
                "Spiral wound (ASME B16.20)",
                "Ring Joint (RTJ \u2014 API 6A)",
                "O-Ring (Elastomer)",
                "Metal-to-metal",
            ])
            self.gasket_type_combo.setCurrentIndex(int(self._props["gasket_type"]))

            self.gasket_thick_spin = QDoubleSpinBox()
            self.gasket_thick_spin.setRange(0.1, 10.0)
            self.gasket_thick_spin.setDecimals(2)
            self.gasket_thick_spin.setSuffix(" mm")
            self.gasket_thick_spin.setValue(self._props["gasket_thickness"])

            self.compress_mod_spin = QDoubleSpinBox()
            self.compress_mod_spin.setRange(1, 10000)
            self.compress_mod_spin.setDecimals(0)
            self.compress_mod_spin.setSuffix(" MPa")
            self.compress_mod_spin.setValue(self._props["compression_modulus"])
            self.compress_mod_spin.setToolTip("Tangent compression modulus")

            self.hertz_exp_spin = QDoubleSpinBox()
            self.hertz_exp_spin.setRange(1.0, 3.0)
            self.hertz_exp_spin.setDecimals(2)
            self.hertz_exp_spin.setValue(self._props["hertz_exponent"])
            self.hertz_exp_spin.setToolTip("Nonlinear exponent (1.5 = Hertzian contact)")

            self.creep_spin = QDoubleSpinBox()
            self.creep_spin.setRange(0, 0.5)
            self.creep_spin.setDecimals(3)
            self.creep_spin.setValue(self._props["creep_coeff"])
            self.creep_spin.setToolTip("Creep coefficient for time-dependent relaxation")

            gasket_form.addRow("Type:", self.gasket_type_combo)
            gasket_form.addRow("Thickness:", self.gasket_thick_spin)
            gasket_form.addRow("Compression E:", self.compress_mod_spin)
            gasket_form.addRow("Hertz exponent:", self.hertz_exp_spin)
            gasket_form.addRow("Creep coeff:", self.creep_spin)
            outer.addWidget(gasket_grp)

        # ── Buttons ────────────────────────────────────────────────────
        outer.addStretch()
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        outer.addWidget(btns)

    # ------------------------------------------------------------------
    def _update_helix_angle(self):
        import math
        p = self.thread_pitch_spin.value()
        r = self.thread_radius_spin.value()
        if r > 0:
            angle = math.degrees(math.atan(p / (2.0 * math.pi * r)))
            self.helix_angle_lbl.setText(f"{angle:.2f}\u00b0")

    def _update_eff_radius(self):
        r_i = self.inner_r_spin.value()
        r_o = self.outer_r_spin.value()
        if r_o > r_i > 0:
            r_eff = (2.0 / 3.0) * (r_o**3 - r_i**3) / (r_o**2 - r_i**2)
            self.eff_radius_lbl.setText(f"{r_eff:.2f} mm")
        else:
            self.eff_radius_lbl.setText("--")

    # ------------------------------------------------------------------
    def get_contact_props(self) -> dict:
        """Return all edited properties as a dict for storage on element_data."""
        elem_type = self.element.element_type
        props = {
            "k_normal":     self.k_normal_spin.value(),
            "k_tangential": self.k_tangential_spin.value(),
            "c_normal":     self.c_normal_spin.value(),
            "c_tangential": self.c_tangential_spin.value(),
            "mu_static":    self.mu_static_spin.value(),
            "mu_kinetic":   self.mu_kinetic_spin.value(),
        }
        if elem_type == "THREAD":
            props.update({
                "pitch":             self.thread_pitch_spin.value(),
                "mean_radius":       self.thread_radius_spin.value(),
                "engagement_length": self.thread_engage_spin.value(),
            })
        elif elem_type in ("BEARING_HEAD", "BEARING_NUT"):
            props.update({
                "inner_radius":     self.inner_r_spin.value(),
                "outer_radius":     self.outer_r_spin.value(),
                "surface_roughness": self.roughness_spin.value(),
            })
        elif elem_type == "GASKET_CONTACT":
            props.update({
                "gasket_type":          self.gasket_type_combo.currentIndex(),
                "gasket_thickness":     self.gasket_thick_spin.value(),
                "compression_modulus":  self.compress_mod_spin.value(),
                "hertz_exponent":       self.hertz_exp_spin.value(),
                "creep_coeff":          self.creep_spin.value(),
            })
        return props


# =============================================================================
# FLANGE JOINT WIZARD
# =============================================================================

class FlangeJointWizard(QDialog):
    """
    Comprehensive wizard for creating flanged bolted joint models.

    Allows configuration of:
    - Number of bolts
    - Bolt/stud configuration (head-nut vs stud with nuts both sides)
    - Washer placement
    - Multiple nuts
    - Contact interfaces
    - Flange and gasket properties
    """

    def __init__(self, parent=None, mu_initial: float = 0.12):
        super().__init__(parent)
        self._mu_initial = mu_initial  # Phase 2.1: seed friction defaults
        self.setWindowTitle("Joint Configuration Wizard")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMinMaxButtonsHint)
        self.setMinimumSize(600, 700)
        self._setup_ui()

    def _setup_ui(self):
        """Setup wizard UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Header
        header = QLabel("Configure Bolted Joint")
        header.setStyleSheet(f"""
            font-size: 14pt;
            font-weight: bold;
            color: {Theme.BLUE};
            padding: 10px;
        """)
        layout.addWidget(header)

        # Main content in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(10)

        # === BOLT CONFIGURATION ===
        bolt_group = QGroupBox("Bolt Configuration")
        bolt_layout = QFormLayout(bolt_group)

        self.n_bolts_spin = QSpinBox()
        self.n_bolts_spin.setRange(1, 100)
        self.n_bolts_spin.setValue(1)
        self.n_bolts_spin.setToolTip("Number of bolts in the joint (for symmetry analysis)")

        self.bolt_type_combo = QComboBox()
        self.bolt_type_combo.addItems([
            "Standard bolt (head + nut)",
            "Stud (nuts both sides)",
            "Through-bolt (heads both sides)"
        ])
        self.bolt_type_combo.currentTextChanged.connect(self._on_bolt_type_changed)

        self.bolt_size_combo = QComboBox()
        self.bolt_size_combo.addItems([
            "M8x1.25", "M10x1.5", "M12x1.75", "M14x2.0", "M16x2.0",
            "M20x2.5", "M24x3.0", "M27x3.0", "M30x3.5", "M36x4.0",
            "M42x4.5", "M48x5.0", "M56x5.5", "M64x6.0"
        ])
        self.bolt_size_combo.setCurrentText("M12x1.75")
        self.bolt_size_combo.currentTextChanged.connect(self._update_preview)

        self.bolt_grade_combo = QComboBox()
        self.bolt_grade_combo.addItems([
            "8.8", "10.9", "12.9",
            "A193 B7", "A193 B7M", "A193 B16",
            "A320 L7", "A354 BC"
        ])
        self.bolt_grade_combo.setCurrentText("10.9")

        bolt_layout.addRow("Number of bolts:", self.n_bolts_spin)
        bolt_layout.addRow("Bolt type:", self.bolt_type_combo)
        bolt_layout.addRow("Bolt size:", self.bolt_size_combo)
        bolt_layout.addRow("Material grade:", self.bolt_grade_combo)

        self.include_shank_check = QCheckBox("Include shank (unthreaded portion)")
        self.include_shank_check.setChecked(False)
        self.include_shank_check.setToolTip(
            "Add a SHANK element between the bolt head and bearing surface.\n"
            "Improves axial stiffness accuracy when shank length > thread engagement.")
        self.include_shank_check.toggled.connect(self._update_preview)
        bolt_layout.addRow("", self.include_shank_check)

        # 3.12 — DB-derived properties label
        self._bolt_info_label = QLabel("–")
        self._bolt_info_label.setStyleSheet(
            f"color: {Theme.SUBTEXT}; font-size: 8pt; padding: 2px 0;"
        )
        bolt_layout.addRow("From DB:", self._bolt_info_label)
        self.bolt_grade_combo.currentTextChanged.connect(self._update_bolt_info)
        self.bolt_size_combo.currentTextChanged.connect(self._update_bolt_info)

        content_layout.addWidget(bolt_group)

        # === TOP SIDE CONFIGURATION ===
        top_group = QGroupBox("Top Side (Load Input)")
        top_layout = QVBoxLayout(top_group)

        self.top_head_radio = QButtonGroup(self)
        top_radio_layout = QHBoxLayout()

        self.top_is_head = QCheckBox("Bolt Head")
        self.top_is_head.setChecked(True)
        self.top_is_nut = QCheckBox("Nut")

        top_radio_layout.addWidget(self.top_is_head)
        top_radio_layout.addWidget(self.top_is_nut)
        top_layout.addLayout(top_radio_layout)

        # Washer options (top)
        self.top_washer_check = QCheckBox("Include washer")
        self.top_washer_check.setChecked(True)
        top_layout.addWidget(self.top_washer_check)

        top_ws_type_layout = QHBoxLayout()
        top_ws_type_layout.addWidget(QLabel("  Washer type:"))
        self.top_washer_type_combo = QComboBox()
        self.top_washer_type_combo.addItems(["Flat", "Spring", "Belleville", "Nord-Lock"])
        self.top_washer_type_combo.setToolTip("Flat: standard washer\nSpring: split-ring lock washer\nBelleville: disc spring washer\nNord-Lock: wedge-lock pair")
        top_ws_type_layout.addWidget(self.top_washer_type_combo)
        top_ws_type_layout.addStretch()
        self.top_washer_check.toggled.connect(self.top_washer_type_combo.setEnabled)
        top_layout.addLayout(top_ws_type_layout)

        # Multiple nuts (top)
        top_nuts_layout = QHBoxLayout()
        self.top_nuts_label = QLabel("Number of nuts:")
        self.top_n_nuts_spin = QSpinBox()
        self.top_n_nuts_spin.setRange(0, 3)
        self.top_n_nuts_spin.setValue(0)
        self.top_n_nuts_spin.setToolTip("0 = no nut (bolt head side), 1+ = jam nuts")
        top_nuts_layout.addWidget(self.top_nuts_label)
        top_nuts_layout.addWidget(self.top_n_nuts_spin)
        top_nuts_layout.addStretch()
        top_layout.addLayout(top_nuts_layout)

        content_layout.addWidget(top_group)

        # === BOTTOM SIDE CONFIGURATION ===
        bottom_group = QGroupBox("Bottom Side (Reaction)")
        bottom_layout = QVBoxLayout(bottom_group)

        bottom_radio_layout = QHBoxLayout()
        self.bottom_is_head = QCheckBox("Bolt Head")
        self.bottom_is_nut = QCheckBox("Nut")
        self.bottom_is_nut.setChecked(True)

        bottom_radio_layout.addWidget(self.bottom_is_head)
        bottom_radio_layout.addWidget(self.bottom_is_nut)
        bottom_layout.addLayout(bottom_radio_layout)

        # Washer options (bottom)
        self.bottom_washer_check = QCheckBox("Include washer")
        self.bottom_washer_check.setChecked(True)
        bottom_layout.addWidget(self.bottom_washer_check)

        bot_ws_type_layout = QHBoxLayout()
        bot_ws_type_layout.addWidget(QLabel("  Washer type:"))
        self.bottom_washer_type_combo = QComboBox()
        self.bottom_washer_type_combo.addItems(["Flat", "Spring", "Belleville", "Nord-Lock"])
        self.bottom_washer_type_combo.setToolTip("Flat: standard washer\nSpring: split-ring lock washer\nBelleville: disc spring washer\nNord-Lock: wedge-lock pair")
        bot_ws_type_layout.addWidget(self.bottom_washer_type_combo)
        bot_ws_type_layout.addStretch()
        self.bottom_washer_check.toggled.connect(self.bottom_washer_type_combo.setEnabled)
        bottom_layout.addLayout(bot_ws_type_layout)

        # Multiple nuts (bottom)
        bottom_nuts_layout = QHBoxLayout()
        self.bottom_nuts_label = QLabel("Number of nuts:")
        self.bottom_n_nuts_spin = QSpinBox()
        self.bottom_n_nuts_spin.setRange(0, 3)
        self.bottom_n_nuts_spin.setValue(1)
        bottom_nuts_layout.addWidget(self.bottom_nuts_label)
        bottom_nuts_layout.addWidget(self.bottom_n_nuts_spin)
        bottom_nuts_layout.addStretch()
        bottom_layout.addLayout(bottom_nuts_layout)

        content_layout.addWidget(bottom_group)

        # === FLANGE CONFIGURATION ===
        flange_group = QGroupBox("Clamped Members")
        flange_layout = QFormLayout(flange_group)

        self.n_flanges_spin = QSpinBox()
        self.n_flanges_spin.setRange(1, 4)
        self.n_flanges_spin.setValue(2)
        self.n_flanges_spin.setToolTip("Number of clamped plates/flanges")

        self.flange_thickness_spin = QDoubleSpinBox()
        self.flange_thickness_spin.setRange(5, 200)
        self.flange_thickness_spin.setValue(25)
        self.flange_thickness_spin.setSuffix(" mm")

        self.include_gasket_check = QCheckBox("Include gasket")
        self.include_gasket_check.setChecked(False)

        self.gasket_type_combo = QComboBox()
        self.gasket_type_combo.addItems([
            "Spiral wound",
            "Ring joint (RTJ)",
            "Flat sheet",
            "PTFE envelope",
            "Metal jacketed"
        ])
        self.gasket_type_combo.setEnabled(False)
        self.include_gasket_check.toggled.connect(self.gasket_type_combo.setEnabled)

        flange_layout.addRow("Number of flanges:", self.n_flanges_spin)
        flange_layout.addRow("Flange thickness:", self.flange_thickness_spin)
        flange_layout.addRow("", self.include_gasket_check)
        flange_layout.addRow("Gasket type:", self.gasket_type_combo)

        content_layout.addWidget(flange_group)

        # === CONTACT INTERFACES ===
        contact_group = QGroupBox("Contact Interfaces")
        contact_layout = QVBoxLayout(contact_group)

        self.add_head_contact = QCheckBox(
            "Add bearing contacts (head/nut bearing + washer–flange)")
        self.add_head_contact.setChecked(True)
        self.add_head_contact.setToolTip(
            "Add frictional contacts at all bearing surfaces:\n"
            "  • BOLT_HEAD_WASHER / BOLT_HEAD_FLANGE\n"
            "  • NUT_WASHER / NUT_FLANGE\n"
            "  • WASHER_FLANGE (washer both sides)")
        self.add_head_contact.toggled.connect(self._update_preview)

        self.add_flange_contact = QCheckBox(
            "Add clamped-member contacts (flange–flange / flange–gasket)")
        self.add_flange_contact.setChecked(True)
        self.add_flange_contact.setToolTip(
            "Add frictional FLANGE_FLANGE contacts (or FLANGE_GASKET when gasket present)")
        self.add_flange_contact.toggled.connect(self._update_preview)

        self.add_thread_contact = QCheckBox("Thread engagement contact (mandatory)")
        self.add_thread_contact.setChecked(True)
        self.add_thread_contact.setEnabled(False)
        self.add_thread_contact.setToolTip("Thread contact is mandatory: every nut must have a ThreadContact")

        self.contact_type_combo = QComboBox()
        self.contact_type_combo.addItems([
            "Elastic (linear spring)",
            "Frictional (Coulomb)",
            "Rigid (bonded)",
            "Nonlinear (Hertzian)"
        ])

        contact_layout.addWidget(self.add_head_contact)
        contact_layout.addWidget(self.add_flange_contact)
        contact_layout.addWidget(self.add_thread_contact)

        contact_type_layout = QHBoxLayout()
        contact_type_layout.addWidget(QLabel("Contact model:"))
        contact_type_layout.addWidget(self.contact_type_combo)
        contact_layout.addLayout(contact_type_layout)

        content_layout.addWidget(contact_group)

        # === THREAD MODEL ===
        thread_group = QGroupBox("Thread Model")
        thread_layout = QVBoxLayout(thread_group)

        self.expand_threads_check = QCheckBox("Expand threads to individual fillets")
        self.expand_threads_check.setChecked(False)
        self.expand_threads_check.setToolTip(
            "Create separate MSD elements for each thread fillet\n"
            "using Sopwith exponential load distribution"
        )

        thread_options_layout = QHBoxLayout()
        thread_options_layout.addWidget(QLabel("Engaged fillets:"))
        self.n_fillets_spin = QSpinBox()
        self.n_fillets_spin.setRange(3, 20)
        self.n_fillets_spin.setValue(6)
        self.n_fillets_spin.setEnabled(False)
        thread_options_layout.addWidget(self.n_fillets_spin)
        thread_options_layout.addStretch()

        self.expand_threads_check.toggled.connect(self.n_fillets_spin.setEnabled)
        self.expand_threads_check.toggled.connect(self._update_preview)
        self.n_fillets_spin.valueChanged.connect(self._update_preview)

        thread_layout.addWidget(self.expand_threads_check)
        thread_layout.addLayout(thread_options_layout)

        content_layout.addWidget(thread_group)

        # Live-preview connections for all other controls that affect structure
        for sig in [
            self.top_is_head.toggled, self.top_is_nut.toggled,
            self.top_washer_check.toggled, self.top_n_nuts_spin.valueChanged,
            self.top_washer_type_combo.currentTextChanged,
            self.bottom_is_head.toggled, self.bottom_is_nut.toggled,
            self.bottom_washer_check.toggled, self.bottom_n_nuts_spin.valueChanged,
            self.bottom_washer_type_combo.currentTextChanged,
            self.n_flanges_spin.valueChanged, self.include_gasket_check.toggled,
            self.bolt_type_combo.currentTextChanged,
            self.add_head_contact.toggled, self.add_flange_contact.toggled,
        ]:
            sig.connect(self._update_preview)

        # === PREVIEW ===
        preview_group = QGroupBox("Model Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setStyleSheet(f"""
            background-color: {Theme.SURFACE0};
            color: {Theme.TEXT};
            font-family: {Theme.FONT_MONO};
            font-size: 9pt;
        """)
        preview_layout.addWidget(self.preview_text)

        # Update preview button
        preview_btn = QPushButton("Update Preview")
        preview_btn.clicked.connect(self._update_preview)
        preview_layout.addWidget(preview_btn)

        content_layout.addWidget(preview_group)
        content_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Initial preview
        self._update_preview()

    def _on_bolt_type_changed(self, text: str):
        """Update UI based on bolt type selection."""
        if "Standard" in text:
            self.top_is_head.setChecked(True)
            self.top_is_nut.setChecked(False)
            self.bottom_is_head.setChecked(False)
            self.bottom_is_nut.setChecked(True)
            self.top_n_nuts_spin.setValue(0)
            self.bottom_n_nuts_spin.setValue(1)
        elif "Stud" in text:
            self.top_is_head.setChecked(False)
            self.top_is_nut.setChecked(True)
            self.bottom_is_head.setChecked(False)
            self.bottom_is_nut.setChecked(True)
            self.top_n_nuts_spin.setValue(1)
            self.bottom_n_nuts_spin.setValue(1)
        elif "Through" in text:
            self.top_is_head.setChecked(True)
            self.top_is_nut.setChecked(False)
            self.bottom_is_head.setChecked(True)
            self.bottom_is_nut.setChecked(False)
            self.top_n_nuts_spin.setValue(0)
            self.bottom_n_nuts_spin.setValue(0)

    def _update_preview(self):
        """Update model preview: full element chain with contact elements shown inline."""
        bearing  = self.add_head_contact.isChecked()
        flange_c = self.add_flange_contact.isChecked()
        top_head = self.top_is_head.isChecked()
        top_nut  = self.top_is_nut.isChecked() and self.top_n_nuts_spin.value() > 0
        top_ws   = self.top_washer_check.isChecked()
        bot_head = self.bottom_is_head.isChecked()
        bot_nut  = self.bottom_is_nut.isChecked()
        bot_ws   = self.bottom_washer_check.isChecked()
        n_fl     = self.n_flanges_spin.value()
        gasket   = self.include_gasket_check.isChecked()
        gask_aft = n_fl // 2 - 1
        expand   = self.expand_threads_check.isChecked()
        n_fil    = self.n_fillets_spin.value()
        bolt_sz  = self.bolt_size_combo.currentText()
        shank    = self.include_shank_check.isChecked()
        top_wt   = self.top_washer_type_combo.currentText()
        bot_wt   = self.bottom_washer_type_combo.currentText()

        SEP = "─" * 48
        lines = [f"Chain for {bolt_sz}  (top → bottom)", SEP]

        def add_elem(name):     lines.append(name)
        def add_ct_elem(name):  lines.append(f"  ◈ {name}")   # contact element in chain
        def add_ct(spec):       lines.append(f"  ├─ {spec}")  # metadata annotation

        add_elem("GROUND  (fixed BC)")

        # ── Top side ──────────────────────────────────────────────────────
        if top_nut:
            if expand:
                add_elem(f"NUT ×{n_fil}  [parallel fillets]")
                add_ct(f"THREAD_CONTACT ×{n_fil}  (mandatory)")
            else:
                for i in range(self.top_n_nuts_spin.value()):
                    add_elem(f"NUT  (top {i+1})")
                    add_ct("THREAD_CONTACT  (mandatory)")
            if bearing:
                if expand:
                    add_ct_elem(f"BEARING_NUT ×{n_fil}  [parallel]")
                else:
                    add_ct_elem("BEARING_NUT  (top)")

        if top_head:
            add_elem("HEAD  (top)")
            if shank:
                add_elem("SHANK  (unthreaded)")
            if bearing:
                add_ct_elem("BEARING_HEAD  (top)")

        if top_ws:
            ws_label = f"WASHER  ({top_wt}, top)" if top_wt != "Flat" else "WASHER  (top)"
            add_elem(ws_label)
            if bearing and n_fl:
                add_ct_elem("WASHER_CONTACT  (top)")

        # ── Clamped members ───────────────────────────────────────────────
        for i in range(n_fl):
            add_elem(f"FLANGE {i+1}")
            if gasket and i == gask_aft:
                if flange_c:
                    add_ct_elem("GASKET_CONTACT  (top face)")
                gtype = self.gasket_type_combo.currentText()
                add_elem(f"GASKET  ({gtype})")
                if flange_c:
                    add_ct_elem("GASKET_CONTACT  (bottom face)")
            elif i < n_fl - 1 and flange_c:
                add_ct_elem(f"FLANGE_FLANGE  ({i+1}→{i+2})")

        # ── Bottom side ───────────────────────────────────────────────────
        if bot_ws:
            if bearing and n_fl:
                add_ct_elem("WASHER_CONTACT  (bottom)")
            ws_label = f"WASHER  ({bot_wt}, bottom)" if bot_wt != "Flat" else "WASHER  (bottom)"
            add_elem(ws_label)

        if bot_nut:
            if bearing:
                if expand:
                    add_ct_elem(f"BEARING_NUT ×{n_fil}  [parallel]")
                else:
                    add_ct_elem("BEARING_NUT  (bottom)")
            n_bot = max(1, self.bottom_n_nuts_spin.value())
            if expand:
                add_elem(f"NUT ×{n_fil}  [parallel fillets]")
                add_ct(f"THREAD_CONTACT ×{n_fil}  (mandatory)")
            else:
                for i in range(n_bot):
                    add_elem(f"NUT  (bottom {i+1})")
                    add_ct("THREAD_CONTACT  (mandatory)")

        if bot_head:
            if bearing:
                add_ct_elem("BEARING_HEAD  (bottom)")
            if shank:
                add_elem("SHANK  (bottom, unthreaded)")
            add_elem("HEAD  (bottom)")

        # ── Summary ───────────────────────────────────────────────────────
        lines.append(SEP)
        # Count physical elements
        n_phys = 1  # GROUND
        n_phys += 1 if top_head else 0
        n_phys += 1 if (top_head and shank) else 0
        n_phys += (n_fil if expand else self.top_n_nuts_spin.value()) if top_nut else 0
        n_phys += 1 if top_ws else 0
        n_phys += n_fl + (1 if gasket else 0)
        n_phys += 1 if bot_ws else 0
        n_phys += (n_fil if expand else max(1, self.bottom_n_nuts_spin.value())) if bot_nut else 0
        n_phys += 1 if (bot_head and shank) else 0
        n_phys += 1 if bot_head else 0
        # Count contact elements added when bearing / flange contacts enabled
        n_ct = 0
        if bearing:
            n_ct += 1 if top_head else 0                    # BEARING_HEAD top
            n_ct += (n_fil if expand else 1) if top_nut else 0  # BEARING_NUT top
            n_ct += 1 if (top_ws and n_fl) else 0           # WASHER_CONTACT top
            n_ct += 1 if (bot_ws and n_fl) else 0           # WASHER_CONTACT bottom
            n_ct += (n_fil if expand else 1) if bot_nut else 0  # BEARING_NUT bottom
            n_ct += 1 if bot_head else 0                    # BEARING_HEAD bottom
        if flange_c:
            if gasket:
                n_ct += 2                                    # two GASKET_CONTACT elements
                n_ct += max(0, n_fl - 2)                    # FLANGE_FLANGE before/after gasket
            else:
                n_ct += max(0, n_fl - 1)                    # FLANGE_FLANGE between pairs
        n_total = n_phys + n_ct
        lines.append(
            f"~{n_total} elements  ({n_phys} physical + {n_ct} contact) "
            f"| {self.n_bolts_spin.value()} bolt(s)"
        )

        self.preview_text.setPlainText("\n".join(lines))

    def _update_bolt_info(self):
        """Update Sy and As display from material/thread DB (3.12)."""
        grade_txt = self.bolt_grade_combo.currentText()
        size_txt  = self.bolt_size_combo.currentText()   # e.g. "M12x1.75"
        parts = []

        # Sy from materials DB
        grade_key = get_grade_key_from_display(grade_txt)
        if grade_key:
            props = get_properties_for_grade(grade_key)
            if props:
                Sy = getattr(props, 'yield_strength', None) or getattr(props, 'Sy', None)
                if Sy:
                    parts.append(f"Sy = {Sy:.0f} MPa")

        # As from thread DB (size_txt like "M12x1.75" or "M12")
        try:
            size_clean = size_txt.lstrip("Mm")
            if "x" in size_clean:
                d_str, p_str = size_clean.split("x", 1)
                d_mm = float(d_str)
                p_mm = float(p_str)
            else:
                d_mm = float(size_clean)
                p_mm = get_standard_pitch_for_diameter(d_mm) or 0.0
            if p_mm > 0:
                As = get_stress_area_from_threads(d_mm, p_mm)
                if As:
                    parts.append(f"As = {As:.1f} mm²")
        except (ValueError, AttributeError):
            pass

        self._bolt_info_label.setText("  |  ".join(parts) if parts else "–")

    def get_configuration(self) -> Dict[str, Any]:
        """Get the wizard configuration as a dictionary."""
        return {
            "n_bolts": self.n_bolts_spin.value(),
            "bolt_type": self.bolt_type_combo.currentText(),
            "bolt_size": self.bolt_size_combo.currentText(),
            "bolt_grade": self.bolt_grade_combo.currentText(),
            "include_shank": self.include_shank_check.isChecked(),

            "top_is_head": self.top_is_head.isChecked(),
            "top_is_nut": self.top_is_nut.isChecked(),
            "top_washer": self.top_washer_check.isChecked(),
            "top_washer_type": self.top_washer_type_combo.currentText(),
            "top_n_nuts": self.top_n_nuts_spin.value(),

            "bottom_is_head": self.bottom_is_head.isChecked(),
            "bottom_is_nut": self.bottom_is_nut.isChecked(),
            "bottom_washer": self.bottom_washer_check.isChecked(),
            "bottom_washer_type": self.bottom_washer_type_combo.currentText(),
            "bottom_n_nuts": self.bottom_n_nuts_spin.value(),

            "n_flanges": self.n_flanges_spin.value(),
            "flange_thickness": self.flange_thickness_spin.value(),
            "include_gasket": self.include_gasket_check.isChecked(),
            "gasket_type": self.gasket_type_combo.currentText(),

            "add_head_contact": self.add_head_contact.isChecked(),
            "add_flange_contact": self.add_flange_contact.isChecked(),
            "add_thread_contact": True,  # Always mandatory
            "contact_type": self.contact_type_combo.currentText(),

            "expand_threads": self.expand_threads_check.isChecked(),
            "n_fillets": self.n_fillets_spin.value()
        }


# =============================================================================
# FORMULA CALCULATOR DIALOG  (3.7)
# =============================================================================

class FormulaCalculatorDialog(QDialog):
    """Mini popup calculator for MSD property formulas (3.7).

    Supported formula_key values:
      "k_shank"   → k = E·π·d²/(4·L)  → N/m
      "k_thread"  → k = E·As/L         → N/m (As = stress area in mm²)
      "c_damping" → c = 2·ζ·√(k·m)    → N·s/m
      "m_solid"   → m = ρ·(π·d²/4)·L  → kg
    """

    value_accepted = pyqtSignal(float)

    _FORMULAS = {
        "k_shank": {
            "label": "Shank stiffness",
            "expr":  "k = E · π · d² / (4 · L)",
            "unit":  "N/m",
            "fields": [
                ("E",  "Young's modulus",  "MPa",  205000.0, 50000, 500000),
                ("d",  "Diameter",         "mm",      16.0,    1,     200),
                ("L",  "Shank length",     "mm",      40.0,    1,    1000),
            ],
        },
        "k_thread": {
            "label": "Thread stiffness",
            "expr":  "k = E · As / L_t",
            "unit":  "N/m",
            "fields": [
                ("E",   "Young's modulus",   "MPa",  205000.0, 50000, 500000),
                ("As",  "Stress area",       "mm²",     157.0,    0.1,  2000),
                ("L_t", "Thread length",     "mm",       24.0,    1,    500),
            ],
        },
        "c_damping": {
            "label": "Viscous damping",
            "expr":  "c = 2 · ζ · √(k · m)",
            "unit":  "N·s/m",
            "fields": [
                ("zeta", "Damping ratio ζ", "–",   0.02,  0.0,  1.0),
                ("k",    "Stiffness",       "N/m", 1e8,   1e3,  1e15),
                ("m",    "Mass",            "kg",  0.5,   1e-6, 1000),
            ],
        },
        "m_solid": {
            "label": "Solid cylinder mass",
            "expr":  "m = ρ · (π · d² / 4) · L",
            "unit":  "kg",
            "fields": [
                ("rho", "Density",   "kg/m³",  7850.0,  100,   20000),
                ("d",   "Diameter",  "mm",       16.0,    1,     500),
                ("L",   "Length",    "mm",       40.0,    1,    2000),
            ],
        },
    }

    def __init__(self, formula_key: str, parent=None):
        super().__init__(parent, Qt.WindowType.Tool)
        self.setWindowTitle("Formula Calculator")
        self.setMinimumWidth(300)
        self._formula_key = formula_key
        self._spins: Dict[str, QDoubleSpinBox] = {}
        self._result_label = QLabel("–")
        self._setup_ui()

    def _setup_ui(self):
        info = self._FORMULAS.get(self._formula_key, {})
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Header
        hdr = QLabel(f"<b>{info.get('label','Calculator')}</b>")
        expr = QLabel(f"<code>{info.get('expr','')}</code>")
        expr.setStyleSheet(f"color: {Theme.SUBTEXT}; font-size: 9pt;")
        layout.addWidget(hdr)
        layout.addWidget(expr)

        # Input fields
        form = QFormLayout()
        form.setSpacing(4)
        for sym, desc, unit, default, lo, hi in info.get("fields", []):
            spin = QDoubleSpinBox()
            spin.setRange(lo, hi)
            spin.setValue(default)
            spin.setDecimals(4)
            spin.setSuffix(f"  {unit}")
            spin.valueChanged.connect(self._recalc)
            self._spins[sym] = spin
            form.addRow(f"{sym} ({desc}):", spin)
        layout.addLayout(form)

        # Result row
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("Result:"))
        self._result_label.setStyleSheet(
            f"color: {Theme.GREEN}; font-weight: bold; font-size: 11pt;"
        )
        res_layout.addWidget(self._result_label)
        res_layout.addStretch()
        unit_lbl = QLabel(info.get("unit", ""))
        unit_lbl.setStyleSheet(f"color: {Theme.SUBTEXT};")
        res_layout.addWidget(unit_lbl)
        layout.addLayout(res_layout)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        self._recalc()

    def _recalc(self):
        import math
        key = self._formula_key
        try:
            v = {k: s.value() for k, s in self._spins.items()}
            if key == "k_shank":
                E  = v["E"] * 1e6       # Pa
                d  = v["d"] * 1e-3      # m
                L  = v["L"] * 1e-3      # m
                result = E * math.pi * d**2 / (4 * L)   # N/m
            elif key == "k_thread":
                E   = v["E"]  * 1e6
                As  = v["As"] * 1e-6    # m²
                L_t = v["L_t"] * 1e-3
                result = E * As / L_t
            elif key == "c_damping":
                result = 2 * v["zeta"] * math.sqrt(v["k"] * v["m"])
            elif key == "m_solid":
                rho = v["rho"]
                d   = v["d"]  * 1e-3
                L   = v["L"]  * 1e-3
                result = rho * math.pi * d**2 / 4 * L
            else:
                result = 0.0
            self._last_result = result
            self._result_label.setText(f"{result:,.2f}")
        except Exception:
            self._result_label.setText("error")
            self._last_result = 0.0

    def _accept(self):
        self.value_accepted.emit(self._last_result)
        self.accept()


# =============================================================================
# PROPERTY INSPECTOR
# =============================================================================

class PropertyInspector(QWidget):
    """Property inspector panel for element configuration."""

    property_changed = pyqtSignal(int, str, object)
    delete_requested = pyqtSignal()
    duplicate_requested = pyqtSignal()
    type_change_requested = pyqtSignal(str)  # new element type
    apply_load_requested = pyqtSignal()
    expand_threads_requested = pyqtSignal()  # expand thread to individual fillets
    loading_changed = pyqtSignal(dict)  # global loading parameters changed

    # 3.6 — unit conversion constants
    _SI_TO_IMP = {
        "k": 0.005711,      # N/m → lbf/in
        "c": 0.005711,      # N·s/m → lbf·s/in
        "m": 2.20462,       # kg → lb
        "force": 0.22481,   # N → lbf
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_element: Optional[ElementGraphicsItem] = None
        self._updating = False
        self._k_transverse = 1.54e7  # Default transverse stiffness (N/m)
        self._imperial: bool = False  # 3.6 — unit mode flag
        self._value_history: Dict[str, List[float]] = {"k": [], "c": [], "m": []}  # 3.17
        self._mu_initial: float = 0.12   # Phase 2.1: default global μ; updated by mu_initial_spin
        # Undo/redo context (wired by the owning MSDBuilder). When either is
        # None the inspector still edits the model directly, just without
        # recording undo steps (keeps the widget usable stand-alone / in tests).
        self._schematic: Optional['SchematicView'] = None
        self._undo_stack = None
        self._setup_ui()
        # Populate d₂/d₃ labels and per-element thread fields for default M16×2 (1.3)
        self._on_bolt_geom_changed()

    def _setup_ui(self):
        """Setup the property inspector UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header row: label + unit toggle (3.6)
        _hdr_row = QWidget()
        _hdr_lay = QHBoxLayout(_hdr_row)
        _hdr_lay.setContentsMargins(0, 0, 0, 0)
        _hdr_lay.setSpacing(4)

        self.header_label = QLabel("No element selected")
        # Styled via global QSS (QLabel#elementHeader) so it re-themes on
        # theme switch — no per-widget setStyleSheet (that would freeze colors).
        self.header_label.setObjectName("elementHeader")
        self.header_label.setWordWrap(True)
        _hdr_lay.addWidget(self.header_label, stretch=1)

        # 3.6 — SI / IMP unit toggle
        self._unit_toggle = QToolButton()
        self._unit_toggle.setText("SI")
        self._unit_toggle.setCheckable(True)
        self._unit_toggle.setToolTip(
            "Toggle SI / Imperial units\n"
            "k: N/m ↔ lbf/in  |  c: N·s/m ↔ lbf·s/in\n"
            "m: kg ↔ lb  |  F: N ↔ lbf\n"
            "Internal storage is always SI."
        )
        self._unit_toggle.setFixedWidth(36)
        self._unit_toggle.setStyleSheet(
            f"QToolButton {{ color: {Theme.SUBTEXT}; font-size: 8pt; border: 1px solid {Theme.SURFACE1}; border-radius: 3px; }}"
            f"QToolButton:checked {{ color: {Theme.YELLOW}; border-color: {Theme.YELLOW}; }}"
        )
        self._unit_toggle.toggled.connect(self._on_unit_mode_changed)
        _hdr_lay.addWidget(self._unit_toggle)

        layout.addWidget(_hdr_row)

        # Element type selector (transform element)
        self.type_group = QGroupBox("Element Type")
        self.type_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        type_layout = QHBoxLayout(self.type_group)
        type_layout.setContentsMargins(4, 4, 4, 4)

        self.type_combo = QComboBox()
        self.type_combo.addItems([
            # Bolt Elements
            "HEAD", "SHANK", "NUT", "WASHER",
            # Member Elements
            "FLANGE", "GASKET",
            # Contact Elements
            "BEARING_HEAD", "BEARING_NUT", "FLANGE_FLANGE",
            "WASHER_CONTACT", "GASKET_CONTACT", "GENERIC_CONTACT",
            # Boundary
            "GROUND"
        ])
        self.type_combo.setToolTip("Change element type")
        self.type_combo.currentTextChanged.connect(self._on_type_combo_changed)

        type_layout.addWidget(QLabel("Type:"))
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()

        self.type_group.setVisible(False)
        layout.addWidget(self.type_group)

        # Tabbed inspector: [Element] [Loading] [Contact]
        self.inspector_tabs = QTabWidget()
        self.inspector_tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.inspector_tabs.setDocumentMode(True)

        # --- Element tab (index 0) ---
        _elem_scroll = QScrollArea()
        _elem_scroll.setWidgetResizable(True)
        _elem_scroll.setFrameShape(QFrame.Shape.NoFrame)
        _elem_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(4)
        _elem_scroll.setWidget(self.scroll_content)
        self.inspector_tabs.addTab(_elem_scroll, "Element")

        # --- Loading tab (index 1): nested Global / Per-Element sub-tabs ---
        self._loading_subtabs = QTabWidget()
        self._loading_subtabs.setTabPosition(QTabWidget.TabPosition.South)
        self._loading_subtabs.setDocumentMode(True)

        # Loading > Global sub-tab (global params, no friction)
        _load_scroll = QScrollArea()
        _load_scroll.setWidgetResizable(True)
        _load_scroll.setFrameShape(QFrame.Shape.NoFrame)
        _load_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._load_content = QWidget()
        self._load_tab_layout = QVBoxLayout(self._load_content)
        self._load_tab_layout.setContentsMargins(0, 0, 0, 0)
        self._load_tab_layout.setSpacing(4)
        _load_scroll.setWidget(self._load_content)
        self._loading_subtabs.addTab(_load_scroll, "Global")

        # Loading > Per-Element sub-tab (dynamic list of element applied loads)
        self._per_elem_load_scroll = QScrollArea()
        self._per_elem_load_scroll.setWidgetResizable(True)
        self._per_elem_load_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._per_elem_load_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._per_elem_load_widget = QWidget()
        self._per_elem_load_layout = QVBoxLayout(self._per_elem_load_widget)
        self._per_elem_load_layout.setContentsMargins(4, 4, 4, 4)
        self._per_elem_load_layout.setSpacing(4)
        self._per_elem_load_scroll.setWidget(self._per_elem_load_widget)
        self._loading_subtabs.addTab(self._per_elem_load_scroll, "Per-Element")

        self.inspector_tabs.addTab(self._loading_subtabs, "Loading")

        # --- Contact tab (index 2): nested Global / Per-Element sub-tabs ---
        self._contact_subtabs = QTabWidget()
        self._contact_subtabs.setTabPosition(QTabWidget.TabPosition.South)
        self._contact_subtabs.setDocumentMode(True)

        # Contact > Global sub-tab (friction & bolt geometry)
        _contact_global_scroll = QScrollArea()
        _contact_global_scroll.setWidgetResizable(True)
        _contact_global_scroll.setFrameShape(QFrame.Shape.NoFrame)
        _contact_global_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._contact_global_content = QWidget()
        self._contact_global_layout = QVBoxLayout(self._contact_global_content)
        self._contact_global_layout.setContentsMargins(0, 0, 0, 4)
        self._contact_global_layout.setSpacing(4)
        _contact_global_scroll.setWidget(self._contact_global_content)
        self._contact_subtabs.addTab(_contact_global_scroll, "Global")

        # Contact > Per-Element sub-tab (contact interface groups)
        _contact_scroll = QScrollArea()
        _contact_scroll.setWidgetResizable(True)
        _contact_scroll.setFrameShape(QFrame.Shape.NoFrame)
        _contact_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._contact_content = QWidget()
        self._contact_tab_layout = QVBoxLayout(self._contact_content)
        self._contact_tab_layout.setContentsMargins(0, 0, 0, 0)
        self._contact_tab_layout.setSpacing(4)
        _contact_scroll.setWidget(self._contact_content)
        self._contact_subtabs.addTab(_contact_scroll, "Per-Element")

        self.inspector_tabs.addTab(self._contact_subtabs, "Contact")

        # === GRID POSITION ===
        self.grid_group = QGroupBox("Grid Position")
        self.grid_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        grid_layout = QFormLayout(self.grid_group)
        grid_layout.setSpacing(4)

        self.row_spin = QSpinBox()
        self.row_spin.setRange(0, 20)
        self.row_spin.valueChanged.connect(self._on_grid_changed)

        self.col_spin = QSpinBox()
        self.col_spin.setRange(0, 10)
        self.col_spin.valueChanged.connect(self._on_grid_changed)

        grid_layout.addRow("Row (series):", self.row_spin)
        grid_layout.addRow("Column (parallel):", self.col_spin)

        self.scroll_layout.addWidget(self.grid_group)

        # === MSD PARAMETERS ===
        self.msd_group = QGroupBox("MSD Parameters")
        self.msd_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        msd_layout = QFormLayout(self.msd_group)
        msd_layout.setSpacing(4)

        self.k_spin = QDoubleSpinBox()
        self.k_spin.setRange(1e3, 1e15)
        self.k_spin.setDecimals(2)
        self.k_spin.valueChanged.connect(self._on_k_changed)

        self.c_spin = QDoubleSpinBox()
        self.c_spin.setRange(0, 1e6)
        self.c_spin.setDecimals(1)
        self.c_spin.valueChanged.connect(self._on_c_changed)

        self.m_spin = QDoubleSpinBox()
        self.m_spin.setRange(0, 100)
        self.m_spin.setDecimals(4)
        self.m_spin.setSuffix(" kg")
        self.m_spin.valueChanged.connect(self._on_m_changed)

        # 3.7 — Calculator popup buttons beside k, c, m
        def _make_calc_row(spin, formula_key, history_key):
            """Build a row with spinbox + [≡] calculator + [▾] history (3.7+3.17)."""
            row = QWidget()
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(2)
            rl.addWidget(spin)
            # Calculator button (3.7)
            calc_btn = QToolButton()
            calc_btn.setText("≡")
            calc_btn.setToolTip("Formula calculator")
            calc_btn.setFixedWidth(20)
            calc_btn.setFixedHeight(spin.sizeHint().height())
            calc_btn.clicked.connect(lambda _, fk=formula_key, s=spin: self._open_calc(fk, s))
            rl.addWidget(calc_btn)
            # History dropdown button (3.17)
            hist_btn = QToolButton()
            hist_btn.setText("▾")
            hist_btn.setToolTip("Recent values")
            hist_btn.setFixedWidth(16)
            hist_btn.setFixedHeight(spin.sizeHint().height())
            hist_btn.clicked.connect(
                lambda _, hk=history_key, s=spin, b=hist_btn: self._show_value_history(hk, s, b)
            )
            rl.addWidget(hist_btn)
            return row

        msd_layout.addRow("k (N/m):", _make_calc_row(self.k_spin, "k_shank", "k"))
        msd_layout.addRow("c (N·s/m):", _make_calc_row(self.c_spin, "c_damping", "c"))
        msd_layout.addRow("m:", _make_calc_row(self.m_spin, "m_solid", "m"))

        self.scroll_layout.addWidget(self.msd_group)

        # === MATERIAL PROPERTIES ===
        self.material_group = QGroupBox("Material Properties")
        self.material_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        mat_layout = QFormLayout(self.material_group)
        mat_layout.setSpacing(4)

        self.material_combo = QComboBox()
        self.material_combo.addItems([
            "A193 B7 (Cr-Mo, HT)",
            "A193 B7M (Cr-Mo, impact)",
            "A193 B16 (Cr-Mo-V)",
            "A320 L7 (Cr-Mo, LT)",
            "A354 BC (Alloy)",
            "Steel 8.8 (ISO)",
            "Steel 10.9 (ISO)",
            "Steel 12.9 (ISO)",
            "Custom..."
        ])
        self.material_combo.currentTextChanged.connect(self._on_material_changed)

        self.E_spin = QDoubleSpinBox()
        self.E_spin.setRange(50000, 250000)
        self.E_spin.setValue(205000)
        self.E_spin.setSuffix(" MPa")
        self.E_spin.setDecimals(0)

        self.Sy_spin = QDoubleSpinBox()
        self.Sy_spin.setRange(100, 2000)
        self.Sy_spin.setValue(720)
        self.Sy_spin.setSuffix(" MPa")
        self.Sy_spin.setDecimals(0)

        self.Su_spin = QDoubleSpinBox()
        self.Su_spin.setRange(200, 2500)
        self.Su_spin.setValue(860)
        self.Su_spin.setSuffix(" MPa")
        self.Su_spin.setDecimals(0)

        self.rho_spin = QDoubleSpinBox()
        self.rho_spin.setRange(1000, 20000)
        self.rho_spin.setValue(7850)
        self.rho_spin.setSuffix(" kg/m³")
        self.rho_spin.setDecimals(0)

        mat_layout.addRow("Grade:", self.material_combo)
        mat_layout.addRow("E (Young's):", self.E_spin)
        mat_layout.addRow("Sy (yield):", self.Sy_spin)
        mat_layout.addRow("Su (ultimate):", self.Su_spin)
        mat_layout.addRow("ρ (density):", self.rho_spin)

        self.scroll_layout.addWidget(self.material_group)

        # === PRELOAD & YIELD ===
        self.preload_group = QGroupBox("Preload & Yield")
        self.preload_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        preload_layout = QFormLayout(self.preload_group)
        preload_layout.setSpacing(4)

        # Input mode selector
        self.preload_mode_combo = QComboBox()
        self.preload_mode_combo.addItems(["% of Yield", "Force (N)"])
        self.preload_mode_combo.setToolTip("Choose how to specify preload")
        self.preload_mode_combo.currentIndexChanged.connect(self._on_preload_mode_changed)

        # % yield input
        self.yield_pct_spin = QDoubleSpinBox()
        self.yield_pct_spin.setRange(0, 100)
        self.yield_pct_spin.setValue(70)
        self.yield_pct_spin.setSuffix(" %")
        self.yield_pct_spin.setDecimals(1)
        self.yield_pct_spin.setSingleStep(5)
        self.yield_pct_spin.setToolTip("Preload as percentage of bolt yield strength")
        self.yield_pct_spin.valueChanged.connect(self._on_percent_yield_changed)

        # Force input (N)
        self.force_spin = QDoubleSpinBox()
        self.force_spin.setRange(0, 1e9)
        self.force_spin.setValue(0)
        self.force_spin.setSuffix(" N")
        self.force_spin.setDecimals(0)
        self.force_spin.setSingleStep(1000)
        self.force_spin.setToolTip("Preload force in Newtons")
        self.force_spin.valueChanged.connect(self._on_force_changed)
        self.force_spin.setVisible(False)  # hidden by default (% mode)

        self.stress_area_label = QLabel("A_s: --")
        self.stress_area_label.setToolTip("Tensile stress area from thread geometry (mm²)")

        self.Sy_display_label = QLabel("Sy: --")
        self.Sy_display_label.setToolTip("Current yield strength (MPa)")

        self.force_display_label = QLabel("F: --")
        self.force_display_label.setToolTip("Computed preload force = (%/100) × A_s × Sy")
        self.force_display_label.setStyleSheet(f"font-weight: bold; color: {Theme.GREEN};")

        preload_layout.addRow("Mode:", self.preload_mode_combo)
        preload_layout.addRow("% Yield:", self.yield_pct_spin)
        preload_layout.addRow("Force:", self.force_spin)
        preload_layout.addRow("", self.stress_area_label)
        preload_layout.addRow("", self.Sy_display_label)
        preload_layout.addRow("Result:", self.force_display_label)

        self.preload_group.setVisible(False)
        self.scroll_layout.addWidget(self.preload_group)

        # === TRIBOLOGICAL PROPERTIES ===
        self.friction_group = QGroupBox("Tribological Properties")
        self.friction_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        fric_layout = QFormLayout(self.friction_group)
        fric_layout.setSpacing(4)

        self.mu_thread_spin = QDoubleSpinBox()
        self.mu_thread_spin.setRange(0.01, 0.5)
        self.mu_thread_spin.setValue(self._mu_initial)        # Phase 2.1: from global
        self.mu_thread_spin.setDecimals(3)
        self.mu_thread_spin.setSingleStep(0.01)
        self.mu_thread_spin.setToolTip(
            "Thread friction coefficient μ — defaults to global μ₀ (Contact > Global)")

        self.mu_bearing_spin = QDoubleSpinBox()
        self.mu_bearing_spin.setRange(0.01, 0.5)
        self.mu_bearing_spin.setValue(self._mu_initial)       # Phase 2.1: from global
        self.mu_bearing_spin.setDecimals(3)
        self.mu_bearing_spin.setSingleStep(0.01)
        self.mu_bearing_spin.setToolTip(
            "Bearing friction coefficient μ — defaults to global μ₀ (Contact > Global)")

        self.surface_combo = QComboBox()
        self.surface_combo.addItems([
            "Bare steel",
            "Zinc plated",
            "Phosphate + oil",
            "PTFE coated",
            "MoS2 lubricated",
            "Cadmium plated"
        ])

        fric_layout.addRow("μ thread:", self.mu_thread_spin)
        fric_layout.addRow("μ bearing:", self.mu_bearing_spin)
        fric_layout.addRow("Surface:", self.surface_combo)

        self.scroll_layout.addWidget(self.friction_group)

        # === THERMAL PROPERTIES ===
        self.thermal_group = QGroupBox("Thermal Properties")
        self.thermal_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        therm_layout = QFormLayout(self.thermal_group)
        therm_layout.setSpacing(4)

        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setRange(5, 25)
        self.alpha_spin.setValue(11.5)
        self.alpha_spin.setDecimals(1)
        self.alpha_spin.setSuffix(" μm/m·K")

        self.T_ref_spin = QDoubleSpinBox()
        self.T_ref_spin.setRange(-200, 600)
        self.T_ref_spin.setValue(20)
        self.T_ref_spin.setSuffix(" °C")
        self.T_ref_spin.setDecimals(0)

        self.T_operating_spin = QDoubleSpinBox()
        self.T_operating_spin.setRange(-200, 600)
        self.T_operating_spin.setValue(20)
        self.T_operating_spin.setSuffix(" °C")
        self.T_operating_spin.setDecimals(0)

        therm_layout.addRow("α (expansion):", self.alpha_spin)
        therm_layout.addRow("T reference:", self.T_ref_spin)
        therm_layout.addRow("T operating:", self.T_operating_spin)

        self.scroll_layout.addWidget(self.thermal_group)

        # === GEOMETRY ===
        self.geometry_group = QGroupBox("Geometry")
        self.geometry_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        geom_layout = QFormLayout(self.geometry_group)
        geom_layout.setSpacing(4)

        self.diameter_spin = QDoubleSpinBox()
        self.diameter_spin.setRange(3, 100)
        self.diameter_spin.setValue(12)
        self.diameter_spin.setSuffix(" mm")
        self.diameter_spin.setDecimals(1)

        self.length_spin = QDoubleSpinBox()
        self.length_spin.setRange(1, 500)
        self.length_spin.setValue(25)
        self.length_spin.setSuffix(" mm")
        self.length_spin.setDecimals(1)

        self.pitch_spin = QDoubleSpinBox()
        self.pitch_spin.setRange(0.5, 6)
        self.pitch_spin.setValue(1.75)
        self.pitch_spin.setSuffix(" mm")
        self.pitch_spin.setDecimals(2)

        geom_layout.addRow("Diameter:", self.diameter_spin)
        geom_layout.addRow("Length:", self.length_spin)
        geom_layout.addRow("Pitch:", self.pitch_spin)

        self.scroll_layout.addWidget(self.geometry_group)

        # === THREAD FILLET PANEL ===
        self.thread_panel = ThreadFilletPanel()
        self.thread_panel.config_changed.connect(self._on_thread_config_changed)
        self.thread_panel.expand_requested.connect(self.expand_threads_requested.emit)
        self.thread_panel.setVisible(False)
        self.scroll_layout.addWidget(self.thread_panel)

        # === CONTACT INTERFACE PROPERTIES ===
        self.contact_group = QGroupBox("Contact Interface Properties")
        self.contact_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        contact_layout = QFormLayout(self.contact_group)
        contact_layout.setSpacing(4)

        # Normal and tangential stiffness
        self.k_normal_spin = QDoubleSpinBox()
        self.k_normal_spin.setRange(1e6, 1e15)
        self.k_normal_spin.setValue(1e10)
        self.k_normal_spin.setDecimals(2)
        self.k_normal_spin.setSuffix(" N/m")
        self.k_normal_spin.setToolTip("Normal stiffness perpendicular to contact surface")

        self.k_tangential_spin = QDoubleSpinBox()
        self.k_tangential_spin.setRange(1e5, 1e14)
        self.k_tangential_spin.setValue(5e9)
        self.k_tangential_spin.setDecimals(2)
        self.k_tangential_spin.setSuffix(" N/m")
        self.k_tangential_spin.setToolTip("Tangential stiffness along contact surface")

        # Contact damping
        self.c_normal_spin = QDoubleSpinBox()
        self.c_normal_spin.setRange(0, 10000)
        self.c_normal_spin.setValue(100)
        self.c_normal_spin.setDecimals(1)
        self.c_normal_spin.setSuffix(" N·s/m")

        self.c_tangential_spin = QDoubleSpinBox()
        self.c_tangential_spin.setRange(0, 10000)
        self.c_tangential_spin.setValue(50)
        self.c_tangential_spin.setDecimals(1)
        self.c_tangential_spin.setSuffix(" N·s/m")

        # Static and kinetic friction
        self.mu_static_spin = QDoubleSpinBox()
        self.mu_static_spin.setRange(0.01, 1.0)
        self.mu_static_spin.setValue(0.15)
        self.mu_static_spin.setDecimals(3)
        self.mu_static_spin.setToolTip("Static friction coefficient (μs)")

        self.mu_kinetic_spin = QDoubleSpinBox()
        self.mu_kinetic_spin.setRange(0.01, 1.0)
        self.mu_kinetic_spin.setValue(0.12)
        self.mu_kinetic_spin.setDecimals(3)
        self.mu_kinetic_spin.setToolTip("Kinetic friction coefficient (μk)")

        contact_layout.addRow("k normal:", self.k_normal_spin)
        contact_layout.addRow("k tangential:", self.k_tangential_spin)
        contact_layout.addRow("c normal:", self.c_normal_spin)
        contact_layout.addRow("c tangential:", self.c_tangential_spin)
        contact_layout.addRow("μ static:", self.mu_static_spin)
        contact_layout.addRow("μ kinetic:", self.mu_kinetic_spin)

        self.contact_group.setVisible(True)
        self._contact_tab_layout.addWidget(self.contact_group)

        # === THREAD CONTACT SPECIFIC ===
        self.thread_contact_group = QGroupBox("Thread Contact Parameters")
        self.thread_contact_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        thread_contact_layout = QFormLayout(self.thread_contact_group)
        thread_contact_layout.setSpacing(4)

        self.pitch_contact_spin = QDoubleSpinBox()
        self.pitch_contact_spin.setRange(0.5, 6.0)
        self.pitch_contact_spin.setValue(1.75)
        self.pitch_contact_spin.setDecimals(2)
        self.pitch_contact_spin.setSuffix(" mm")
        self.pitch_contact_spin.setToolTip("Thread pitch for helix coupling")

        self.helix_angle_spin = QDoubleSpinBox()
        self.helix_angle_spin.setRange(1.0, 10.0)
        self.helix_angle_spin.setValue(3.2)
        self.helix_angle_spin.setDecimals(2)
        self.helix_angle_spin.setSuffix(" °")
        self.helix_angle_spin.setReadOnly(True)
        self.helix_angle_spin.setToolTip("Thread helix angle (auto-calculated)")

        self.mean_radius_spin = QDoubleSpinBox()
        self.mean_radius_spin.setRange(2, 50)
        self.mean_radius_spin.setValue(10.0)
        self.mean_radius_spin.setDecimals(2)
        self.mean_radius_spin.setSuffix(" mm")
        self.mean_radius_spin.setToolTip("Mean thread radius (d2/2)")

        self.engagement_length_spin = QDoubleSpinBox()
        self.engagement_length_spin.setRange(5, 100)
        self.engagement_length_spin.setValue(20)
        self.engagement_length_spin.setDecimals(1)
        self.engagement_length_spin.setSuffix(" mm")
        self.engagement_length_spin.setToolTip("Thread engagement length")

        thread_contact_layout.addRow("Pitch:", self.pitch_contact_spin)
        thread_contact_layout.addRow("Helix angle:", self.helix_angle_spin)
        thread_contact_layout.addRow("Mean radius:", self.mean_radius_spin)
        thread_contact_layout.addRow("Engagement:", self.engagement_length_spin)

        self.thread_contact_group.setVisible(True)
        self._contact_tab_layout.addWidget(self.thread_contact_group)

        # === BEARING CONTACT SPECIFIC ===
        self.bearing_contact_group = QGroupBox("Bearing Contact Parameters")
        self.bearing_contact_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        bearing_contact_layout = QFormLayout(self.bearing_contact_group)
        bearing_contact_layout.setSpacing(4)

        self.inner_radius_spin = QDoubleSpinBox()
        self.inner_radius_spin.setRange(2, 30)
        self.inner_radius_spin.setValue(6.5)
        self.inner_radius_spin.setDecimals(2)
        self.inner_radius_spin.setSuffix(" mm")
        self.inner_radius_spin.setToolTip("Inner contact radius (hole)")

        self.outer_radius_spin = QDoubleSpinBox()
        self.outer_radius_spin.setRange(3, 50)
        self.outer_radius_spin.setValue(10.0)
        self.outer_radius_spin.setDecimals(2)
        self.outer_radius_spin.setSuffix(" mm")
        self.outer_radius_spin.setToolTip("Outer contact radius (bearing surface)")

        self.effective_radius_spin = QDoubleSpinBox()
        self.effective_radius_spin.setRange(2, 40)
        self.effective_radius_spin.setValue(8.25)
        self.effective_radius_spin.setDecimals(2)
        self.effective_radius_spin.setSuffix(" mm")
        self.effective_radius_spin.setReadOnly(True)
        self.effective_radius_spin.setToolTip("Effective friction radius (auto: 2/3(r₃³-r₁³)/(r₃²-r₁²))")

        self.surface_roughness_spin = QDoubleSpinBox()
        self.surface_roughness_spin.setRange(0.1, 25.0)
        self.surface_roughness_spin.setValue(1.6)
        self.surface_roughness_spin.setDecimals(2)
        self.surface_roughness_spin.setSuffix(" μm Ra")
        self.surface_roughness_spin.setToolTip("Surface roughness (Ra)")

        bearing_contact_layout.addRow("Inner radius:", self.inner_radius_spin)
        bearing_contact_layout.addRow("Outer radius:", self.outer_radius_spin)
        bearing_contact_layout.addRow("Effective r:", self.effective_radius_spin)
        bearing_contact_layout.addRow("Roughness:", self.surface_roughness_spin)

        self.bearing_contact_group.setVisible(True)
        self._contact_tab_layout.addWidget(self.bearing_contact_group)

        # === GASKET CONTACT SPECIFIC ===
        self.gasket_contact_group = QGroupBox("Gasket Contact Parameters")
        self.gasket_contact_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        gasket_contact_layout = QFormLayout(self.gasket_contact_group)
        gasket_contact_layout.setSpacing(4)

        self.gasket_type_combo = QComboBox()
        self.gasket_type_combo.addItems([
            "Sheet (Compressed fiber)",
            "Spiral wound (ASME B16.20)",
            "Ring Joint (RTJ - API 6A)",
            "O-Ring (Elastomer)",
            "Metal-to-metal"
        ])
        self.gasket_type_combo.setToolTip("Gasket type determines nonlinear behavior")

        self.gasket_thickness_spin = QDoubleSpinBox()
        self.gasket_thickness_spin.setRange(0.1, 10.0)
        self.gasket_thickness_spin.setValue(1.5)
        self.gasket_thickness_spin.setDecimals(2)
        self.gasket_thickness_spin.setSuffix(" mm")

        self.compression_modulus_spin = QDoubleSpinBox()
        self.compression_modulus_spin.setRange(1, 10000)
        self.compression_modulus_spin.setValue(100)
        self.compression_modulus_spin.setDecimals(0)
        self.compression_modulus_spin.setSuffix(" MPa")
        self.compression_modulus_spin.setToolTip("Tangent compression modulus")

        self.hertz_exponent_spin = QDoubleSpinBox()
        self.hertz_exponent_spin.setRange(1.0, 3.0)
        self.hertz_exponent_spin.setValue(1.5)
        self.hertz_exponent_spin.setDecimals(2)
        self.hertz_exponent_spin.setToolTip("Nonlinear exponent (1.5 for Hertzian contact)")

        self.creep_coeff_spin = QDoubleSpinBox()
        self.creep_coeff_spin.setRange(0, 0.5)
        self.creep_coeff_spin.setValue(0.05)
        self.creep_coeff_spin.setDecimals(3)
        self.creep_coeff_spin.setToolTip("Creep coefficient for time-dependent relaxation")

        gasket_contact_layout.addRow("Gasket type:", self.gasket_type_combo)
        gasket_contact_layout.addRow("Thickness:", self.gasket_thickness_spin)
        gasket_contact_layout.addRow("Compression E:", self.compression_modulus_spin)
        gasket_contact_layout.addRow("Hertz exponent:", self.hertz_exponent_spin)
        gasket_contact_layout.addRow("Creep coeff:", self.creep_coeff_spin)

        self.gasket_contact_group.setVisible(True)
        self._contact_tab_layout.addWidget(self.gasket_contact_group)

        # === EXPERIMENTAL PRESETS (UFU Junker lab) ===
        self.exp_preset_group = QGroupBox("Experimental Preset")
        self.exp_preset_group.setToolTip(
            "<b>Quick-load UFU Junker lab conditions</b><br>"
            "3/4\" UNC L7, ±0.5 mm @ 1 Hz. Selecting a preset overwrites the "
            "loading fields below with the trial's measured values."
        )
        _ep_layout = QFormLayout(self.exp_preset_group)
        _ep_layout.setSpacing(4)
        self.exp_preset_combo = QComboBox()
        self.exp_preset_combo.addItems([
            "— Custom —",
            "UFU 5A (05-03, F0=118.2 kN, μ≈0.08)",
            "UFU 13A 1ª (19-03, F0=120.0 kN, μ≈0.14, interrupted)",
            "UFU 13A def (14-04, F0=116.5 kN, μ≈0.14)",
        ])
        self.exp_preset_combo.currentIndexChanged.connect(self._on_experimental_preset_changed)
        _ep_layout.addRow("Preset:", self.exp_preset_combo)
        self._load_tab_layout.addWidget(self.exp_preset_group)

        # === GLOBAL LOADING ===
        self.loading_group = QGroupBox("Global Loading Configuration")
        self.loading_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        loading_layout = QFormLayout(self.loading_group)
        loading_layout.setSpacing(4)

        # Load type
        self.load_type_combo = QComboBox()
        self.load_type_combo.addItems([
            "Axial", "Transverse", "Combined", "Torsional", "Bending"
        ])
        self.load_type_combo.setCurrentText("Transverse")
        self.load_type_combo.currentTextChanged.connect(self._on_loading_param_changed)
        loading_layout.addRow("Load type:", self.load_type_combo)

        # Friction evolution model (Phase 3.1)
        self.friction_model_combo = QComboBox()
        self.friction_model_combo.addItems([
            "Constant",
            "Exponential Decay",
            "Three-Phase",
            "Stribeck",
            "LuGre",
        ])
        self.friction_model_combo.setCurrentText("Three-Phase")
        self.friction_model_combo.setToolTip(
            "<b>Friction Evolution Model</b><br>"
            "<b>Constant</b>: μ = μ₀ throughout (no evolution)<br>"
            "<b>Exponential Decay</b>: μ decays smoothly from μ₀ → μ_steady<br>"
            "<b>Three-Phase</b>: Running-in rise → transition decay → steady state<br>"
            "<b>Stribeck</b>: Velocity-dependent; rapid initial drop to hydrodynamic μ<br>"
            "<b>LuGre</b>: Dynamic bristle model; high initial stick-slip peak then decay"
        )
        self.friction_model_combo.currentTextChanged.connect(self._on_loading_param_changed)
        loading_layout.addRow("Friction model:", self.friction_model_combo)

        # Preload
        self.preload_spin = QDoubleSpinBox()
        self.preload_spin.setRange(0, 1e9)
        self.preload_spin.setValue(50000.0)
        self.preload_spin.setSuffix(" N")
        self.preload_spin.setDecimals(0)
        self.preload_spin.setSingleStep(1000)
        self.preload_spin.valueChanged.connect(self._on_global_preload_force_changed)
        loading_layout.addRow("Preload F\u2080:", self.preload_spin)

        # % Yield
        self.loading_yield_pct_spin = QDoubleSpinBox()
        self.loading_yield_pct_spin.setRange(0, 100)
        self.loading_yield_pct_spin.setValue(70.0)
        self.loading_yield_pct_spin.setSuffix(" %")
        self.loading_yield_pct_spin.setDecimals(1)
        self.loading_yield_pct_spin.valueChanged.connect(self._on_global_yield_pct_changed)
        loading_layout.addRow("% Yield:", self.loading_yield_pct_spin)

        # Live preload summary label (Phase 1.2) — visible on Loading > Global tab
        self.loading_calc_label = QLabel("A_s: --  ·  F₀: --")
        self.loading_calc_label.setToolTip(
            "Auto-calculated from bolt geometry (Contact > Global):\n"
            "A_s = π/4·((d₂+d₃)/2)²   F₀ = (%/100) × A_s × Sy"
        )
        self.loading_calc_label.setStyleSheet(
            f"color: {Theme.GREEN}; font-weight: bold; font-size: 9pt;"
        )
        self.loading_calc_label.setWordWrap(True)
        loading_layout.addRow("", self.loading_calc_label)

        # Control mode — which transverse input is imposed (drives the test).
        # Maps to LoadingData.control_mode and the V2 engine disp/force modes.
        self.control_mode_combo = QComboBox()
        self.control_mode_combo.addItems([
            "Displacement-controlled (impose δ)",
            "Force-controlled (impose F)",
        ])
        self._control_mode_keys = ["displacement", "force"]
        self.control_mode_combo.setToolTip(
            "Displacement-controlled: impose δ (Junker/crank rig); transverse "
            "force is derived from δ×k.\n"
            "Force-controlled: impose the transverse force F directly "
            "(servo-hydraulic).")
        self.control_mode_combo.currentIndexChanged.connect(
            self._on_control_mode_changed)
        loading_layout.addRow("Control mode:", self.control_mode_combo)

        # Transverse force
        self.transverse_force_spin = QDoubleSpinBox()
        self.transverse_force_spin.setRange(0, 1e6)
        self.transverse_force_spin.setValue(10000.0)
        self.transverse_force_spin.setSuffix(" N")
        self.transverse_force_spin.setDecimals(0)
        self.transverse_force_spin.setSingleStep(500)
        self.transverse_force_spin.valueChanged.connect(self._on_trans_force_changed)
        loading_layout.addRow("Transverse force:", self.transverse_force_spin)

        # Transverse displacement
        self.transverse_disp_spin = QDoubleSpinBox()
        self.transverse_disp_spin.setRange(0, 10.0)
        self.transverse_disp_spin.setValue(0.65)
        self.transverse_disp_spin.setSuffix(" mm")
        self.transverse_disp_spin.setDecimals(3)
        self.transverse_disp_spin.setSingleStep(0.05)
        self.transverse_disp_spin.valueChanged.connect(self._on_trans_disp_changed)
        loading_layout.addRow("Transverse disp.:", self.transverse_disp_spin)
        self._apply_control_mode_enable()   # initial grey-out per default mode

        # Frequency
        self.frequency_spin = QDoubleSpinBox()
        self.frequency_spin.setRange(0.001, 1000)
        self.frequency_spin.setValue(12.5)
        self.frequency_spin.setSuffix(" Hz")
        self.frequency_spin.setDecimals(2)
        self.frequency_spin.valueChanged.connect(self._on_loading_param_changed)
        loading_layout.addRow("Frequency:", self.frequency_spin)

        # Duration mode toggle: N cycles OR test time
        duration_mode_row = QHBoxLayout()
        self._duration_mode_grp = QButtonGroup(self)
        self.cycles_mode_radio = QRadioButton("N cycles")
        self.time_mode_radio = QRadioButton("Test time")
        self.time_mode_radio.setChecked(True)  # default: test time
        self._duration_mode_grp.addButton(self.cycles_mode_radio, 0)
        self._duration_mode_grp.addButton(self.time_mode_radio, 1)
        duration_mode_row.addWidget(self.cycles_mode_radio)
        duration_mode_row.addWidget(self.time_mode_radio)
        loading_layout.addRow("Duration mode:", duration_mode_row)

        # Adaptive primary duration spinbox (adapts to selected mode)
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.01, 100000)
        self.duration_spin.setValue(160.0)
        self.duration_spin.setSuffix(" s")
        self.duration_spin.setDecimals(2)
        self.duration_spin.setSingleStep(1.0)
        self.duration_spin.valueChanged.connect(self._on_loading_param_changed)
        loading_layout.addRow("Duration:", self.duration_spin)

        # Derived value (read-only display)
        self.duration_derived_label = QLabel("N = 2,000 cycles")
        loading_layout.addRow("", self.duration_derived_label)
        self.cycles_label = self.duration_derived_label  # legacy alias

        # Hidden holders updated programmatically — keep solver compatibility
        self.integration_time_spin = QDoubleSpinBox()
        self.integration_time_spin.setRange(0.01, 100000)
        self.integration_time_spin.setValue(160.0)
        self.integration_time_spin.setVisible(False)

        self.cycles_spin = QSpinBox()
        self.cycles_spin.setRange(1, 10000000)
        self.cycles_spin.setValue(2000)
        self.cycles_spin.setVisible(False)

        # Connect mode toggle
        self._duration_mode_grp.buttonClicked.connect(self._on_duration_mode_changed)

        # External force — input mode selector (N or % yield)
        ext_mode_row = QHBoxLayout()
        self.ext_force_mode_combo = QComboBox()
        self.ext_force_mode_combo.addItems(["N", "% Yield"])
        self.ext_force_mode_combo.setFixedWidth(70)
        self.ext_force_mode_combo.currentIndexChanged.connect(self._on_ext_force_mode_changed)

        self.external_force_spin = QDoubleSpinBox()
        self.external_force_spin.setRange(-1e9, 1e9)
        self.external_force_spin.setValue(0.0)
        self.external_force_spin.setSuffix(" N")
        self.external_force_spin.setDecimals(0)
        self.external_force_spin.setSingleStep(500)
        self.external_force_spin.valueChanged.connect(self._on_ext_force_value_changed)

        self.ext_force_pct_spin = QDoubleSpinBox()
        self.ext_force_pct_spin.setRange(-100, 100)
        self.ext_force_pct_spin.setValue(0.0)
        self.ext_force_pct_spin.setSuffix(" %")
        self.ext_force_pct_spin.setDecimals(1)
        self.ext_force_pct_spin.setSingleStep(1.0)
        self.ext_force_pct_spin.valueChanged.connect(self._on_ext_force_pct_changed)
        self.ext_force_pct_spin.setVisible(False)

        ext_mode_row.addWidget(self.external_force_spin)
        ext_mode_row.addWidget(self.ext_force_pct_spin)
        ext_mode_row.addWidget(self.ext_force_mode_combo)
        loading_layout.addRow("External force:", ext_mode_row)

        # Torque
        self.torque_spin = QDoubleSpinBox()
        self.torque_spin.setRange(0, 1e6)
        self.torque_spin.setValue(0.0)
        self.torque_spin.setSuffix(" N\u00b7m")
        self.torque_spin.setDecimals(1)
        self.torque_spin.valueChanged.connect(self._on_loading_param_changed)
        loading_layout.addRow("Torque:", self.torque_spin)

        # Delta T
        self.delta_T_spin = QDoubleSpinBox()
        self.delta_T_spin.setRange(-500, 500)
        self.delta_T_spin.setValue(0.0)
        self.delta_T_spin.setSuffix(" \u00b0C")
        self.delta_T_spin.setDecimals(1)
        self.delta_T_spin.valueChanged.connect(self._on_loading_param_changed)
        loading_layout.addRow("\u0394T:", self.delta_T_spin)

        self.loading_group.setVisible(True)
        self._load_tab_layout.addWidget(self.loading_group)

        # === Locking Device selector (Phase F completion) ===
        self.locking_device_group = QGroupBox("Locking Device")
        self.locking_device_group.setToolTip(
            "<b>Locking Device (VDI 2230 Annex B / ISO 16130)</b><br>"
            "Selecting a device auto-sets the Pai-Hess slip onset factor<br>"
            "and shows the friction increase from the device.<br>"
            "Source: locking_devices.json (ISO 2320, Junker DIN 65151)"
        )
        _ld_layout = QFormLayout(self.locking_device_group)
        _ld_layout.setSpacing(4)

        # Keys match locking_devices.json order
        self._LOCKING_DEVICE_KEYS = [
            "free_running_nut", "prevailing_torque_nut", "all_metal_prevailing_nut",
            "lock_washer_spring", "nord_lock_washer", "belleville_spring_washer",
            "double_nut", "chemical_locking",
        ]
        self.locking_device_combo = QComboBox()
        self.locking_device_combo.addItems([
            "Free-running nut (none)",
            "Prevailing-torque nut (ISO 7042)",
            "All-metal prevailing nut",
            "Spring lock washer (DIN 127)",
            "Nord-Lock® wedge washer",
            "Belleville disc washer (DIN 6796)",
            "Double nut",
            "Thread-locking compound (Loctite)",
        ])
        self.locking_device_combo.setToolTip(
            "Select locking device — auto-fills slip onset factor (Pai-Hess correction)"
        )
        self.locking_device_combo.currentIndexChanged.connect(self._on_locking_device_changed)
        _ld_layout.addRow("Device:", self.locking_device_combo)

        self._locking_slip_lbl = QLabel("0.46 (Pai-Hess default)")
        self._locking_slip_lbl.setToolTip(
            "slip_onset_factor: fraction of µN at which gross slip begins (Pai & Hess 2002)")
        _ld_layout.addRow("Slip onset:", self._locking_slip_lbl)

        self._locking_mu_inc_lbl = QLabel("+0.000")
        self._locking_mu_inc_lbl.setToolTip(
            "Additive Δµ from locking device (informational — add to Contact > Global µ if needed)")
        _ld_layout.addRow("\u0394\u03bc:", self._locking_mu_inc_lbl)

        self._locking_junker_lbl = QLabel("—")
        self._locking_junker_lbl.setToolTip("Junker DIN 65151 effectiveness class")
        _ld_layout.addRow("Junker class:", self._locking_junker_lbl)

        # Internal state for currently selected device
        self._locking_device_slip = 0.46
        self._locking_device_mu_inc = 0.0

        self._load_tab_layout.addWidget(self.locking_device_group)

        # === VDI 2230 Load Factors group (Phase A) ===
        self.vdi2230_group = QGroupBox("VDI 2230 Load Factors")
        self.vdi2230_group.setToolTip(
            "<b>VDI 2230 §5 Load Factor Inputs</b><br>"
            "<b>Stress ratio R</b>: R = F_min / F_max  "
            "(−1 = fully reversed, 0 = zero-to-max, +1 = static)<br>"
            "<b>Dynamic factor φ</b>: amplification for vibration/shock (≥ 1)<br>"
            "<b>Load-plane factor n</b>: 0 = bolt head, 0.5 = mid-plane, 1 = nut<br>"
            "<b>Waveform</b>: time-history shape of the alternating force component"
        )
        vdi_layout = QFormLayout(self.vdi2230_group)
        vdi_layout.setSpacing(4)

        self.R_factor_spin = QDoubleSpinBox()
        self.R_factor_spin.setRange(-1.0, 1.0)
        self.R_factor_spin.setValue(0.0)
        self.R_factor_spin.setDecimals(2)
        self.R_factor_spin.setSingleStep(0.05)
        self.R_factor_spin.setToolTip("Stress ratio R = F_min / F_max  (0 = zero-to-max)")
        self.R_factor_spin.valueChanged.connect(self._on_loading_param_changed)
        vdi_layout.addRow("Stress ratio R:", self.R_factor_spin)

        self.dynamic_factor_spin = QDoubleSpinBox()
        self.dynamic_factor_spin.setRange(1.0, 20.0)
        self.dynamic_factor_spin.setValue(1.0)
        self.dynamic_factor_spin.setDecimals(2)
        self.dynamic_factor_spin.setSingleStep(0.1)
        self.dynamic_factor_spin.setToolTip("Dynamic amplification φ  (1.0 = quasi-static)")
        self.dynamic_factor_spin.valueChanged.connect(self._on_loading_param_changed)
        vdi_layout.addRow("Dyn. factor φ:", self.dynamic_factor_spin)

        self.n_load_plane_spin = QDoubleSpinBox()
        self.n_load_plane_spin.setRange(0.0, 1.0)
        self.n_load_plane_spin.setValue(0.5)
        self.n_load_plane_spin.setDecimals(2)
        self.n_load_plane_spin.setSingleStep(0.05)
        self.n_load_plane_spin.setToolTip(
            "Load-plane factor n\n0 = load at bolt head\n0.5 = mid-grip\n1 = load at nut")
        self.n_load_plane_spin.valueChanged.connect(self._on_loading_param_changed)
        vdi_layout.addRow("Load-plane n:", self.n_load_plane_spin)

        self.load_waveform_combo = QComboBox()
        self.load_waveform_combo.addItems(["sinusoidal", "square", "sawtooth"])
        self.load_waveform_combo.setToolTip("Time-history shape of the alternating load component")
        self.load_waveform_combo.currentTextChanged.connect(self._on_loading_param_changed)
        vdi_layout.addRow("Waveform:", self.load_waveform_combo)

        self._load_tab_layout.addWidget(self.vdi2230_group)

        # === CURVE SHAPE (Stage II tuning) ===
        # Four parameters that shape the per-cycle preload-decay trace.
        # Defaults match the analyzer defaults so behaviour is unchanged
        # unless the user moves a slider here.
        self.curve_shape_group = QGroupBox("Curve Shape (Stage II)")
        self.curve_shape_group.setToolTip(
            "<b>Stage II curve-shape tuning</b><br>"
            "<b>F∞ ratio</b>: asymptotic preload floor F∞/F₀. "
            "Smaller value → longer tail; 1.0 disables damped decay.<br>"
            "<b>μ recovery gain</b>: amplifies friction-wear feedback "
            "(μ↓→slip↑→wear↑). 1.0 = baseline.<br>"
            "<b>Creep ε₀</b>: Norton-Bailey creep coefficient (0 = off). "
            "Use for gasketed/polymer joints.<br>"
            "<b>Noise σ</b>: Gaussian smearing on per-cycle d_θ (0 = deterministic).")
        cs_layout = QFormLayout(self.curve_shape_group)
        cs_layout.setSpacing(4)

        self.curve_F_inf_spin = QDoubleSpinBox()
        self.curve_F_inf_spin.setRange(0.0, 1.0)
        self.curve_F_inf_spin.setValue(0.20)
        self.curve_F_inf_spin.setDecimals(2)
        self.curve_F_inf_spin.setSingleStep(0.05)
        self.curve_F_inf_spin.setToolTip("F∞/F₀ — asymptotic preload floor (1.0 = no damping)")
        self.curve_F_inf_spin.valueChanged.connect(self._on_loading_param_changed)
        cs_layout.addRow("F∞ ratio:", self.curve_F_inf_spin)

        self.curve_mu_gain_spin = QDoubleSpinBox()
        self.curve_mu_gain_spin.setRange(0.0, 20.0)
        self.curve_mu_gain_spin.setValue(1.0)
        self.curve_mu_gain_spin.setDecimals(2)
        self.curve_mu_gain_spin.setSingleStep(0.5)
        self.curve_mu_gain_spin.setToolTip("Friction-wear feedback gain (1 = Jiang baseline; 3–5 = strong curvature)")
        self.curve_mu_gain_spin.valueChanged.connect(self._on_loading_param_changed)
        cs_layout.addRow("μ recovery gain:", self.curve_mu_gain_spin)

        self.curve_creep_spin = QDoubleSpinBox()
        self.curve_creep_spin.setRange(0.0, 1e-3)
        self.curve_creep_spin.setValue(0.0)
        self.curve_creep_spin.setDecimals(7)
        self.curve_creep_spin.setSingleStep(1e-6)
        self.curve_creep_spin.setToolTip("Norton-Bailey ε₀ [m] — log-time creep gain (0 = off)")
        self.curve_creep_spin.valueChanged.connect(self._on_loading_param_changed)
        cs_layout.addRow("Creep ε₀:", self.curve_creep_spin)

        self.curve_noise_spin = QDoubleSpinBox()
        self.curve_noise_spin.setRange(0.0, 0.5)
        self.curve_noise_spin.setValue(0.0)
        self.curve_noise_spin.setDecimals(3)
        self.curve_noise_spin.setSingleStep(0.01)
        self.curve_noise_spin.setToolTip("Gaussian smearing σ on per-cycle d_θ (0 = deterministic; 0.03–0.08 typical)")
        self.curve_noise_spin.valueChanged.connect(self._on_loading_param_changed)
        cs_layout.addRow("Noise σ:", self.curve_noise_spin)

        self._load_tab_layout.addWidget(self.curve_shape_group)
        self._load_tab_layout.addStretch()

        # === FRICTION & BOLT GEOMETRY → Contact > Global sub-tab ===
        self.friction_global_group = QGroupBox("Friction & Bolt Geometry")
        self.friction_global_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        friction_gl = QFormLayout(self.friction_global_group)
        friction_gl.setSpacing(4)

        self.mu_initial_spin = QDoubleSpinBox()
        self.mu_initial_spin.setRange(0.01, 0.50)
        self.mu_initial_spin.setValue(0.12)
        self.mu_initial_spin.setDecimals(3)
        self.mu_initial_spin.setSingleStep(0.01)
        self.mu_initial_spin.valueChanged.connect(self._on_loading_param_changed)
        friction_gl.addRow("Initial \u03bc:", self.mu_initial_spin)

        self.lubricated_check = QCheckBox("Lubricated")
        self.lubricated_check.setChecked(True)
        self.lubricated_check.toggled.connect(self._on_loading_param_changed)
        friction_gl.addRow("", self.lubricated_check)

        self.bolt_diameter_spin = QDoubleSpinBox()
        self.bolt_diameter_spin.setRange(4, 100)
        self.bolt_diameter_spin.setValue(16.0)
        self.bolt_diameter_spin.setSuffix(" mm")
        self.bolt_diameter_spin.setDecimals(1)
        self.bolt_diameter_spin.valueChanged.connect(self._on_bolt_geom_changed)
        friction_gl.addRow("Bolt diameter:", self.bolt_diameter_spin)

        self.bolt_pitch_spin = QDoubleSpinBox()
        self.bolt_pitch_spin.setRange(0.5, 10.0)
        self.bolt_pitch_spin.setValue(2.0)
        self.bolt_pitch_spin.setSuffix(" mm")
        self.bolt_pitch_spin.setDecimals(2)
        self.bolt_pitch_spin.setToolTip("Thread pitch — auto-filled from ISO table on diameter change")
        self.bolt_pitch_spin.valueChanged.connect(self._on_bolt_geom_changed)
        friction_gl.addRow("Pitch:", self.bolt_pitch_spin)

        # Read-only derived geometry labels (auto-updated)
        self.bolt_d2_label = QLabel("d₂: --")
        self.bolt_d2_label.setToolTip("Pitch diameter d₂ = d − 0.6495·P  (ISO 724)")
        self.bolt_d2_label.setStyleSheet(f"color: {Theme.SUBTEXT};")
        friction_gl.addRow("", self.bolt_d2_label)

        self.bolt_d3_label = QLabel("d₃: --")
        self.bolt_d3_label.setToolTip("Minor (root) diameter d₃ = d − 1.0825·P  (ISO 724)")
        self.bolt_d3_label.setStyleSheet(f"color: {Theme.SUBTEXT};")
        friction_gl.addRow("", self.bolt_d3_label)

        # Yield strength (for % yield → preload calculation)
        self.loading_Sy_spin = QDoubleSpinBox()
        self.loading_Sy_spin.setRange(100, 2000)
        self.loading_Sy_spin.setValue(640.0)  # Grade 8.8 default
        self.loading_Sy_spin.setSuffix(" MPa")
        self.loading_Sy_spin.setDecimals(0)
        self.loading_Sy_spin.setSingleStep(10)
        self.loading_Sy_spin.setToolTip("Bolt yield strength for preload calculation")
        self.loading_Sy_spin.valueChanged.connect(self._on_bolt_geom_changed)
        friction_gl.addRow("Sy (yield):", self.loading_Sy_spin)

        # Computed stress area display
        self.loading_As_label = QLabel("A_s: --")
        self.loading_As_label.setToolTip("Tensile stress area from bolt diameter (mm\u00b2)")
        friction_gl.addRow("", self.loading_As_label)

        # Computed preload display
        self.loading_preload_label = QLabel("F\u2080: --")
        self.loading_preload_label.setStyleSheet(f"font-weight: bold; color: {Theme.GREEN};")
        self.loading_preload_label.setToolTip("F\u2080 = (%/100) \u00d7 A_s \u00d7 Sy")
        friction_gl.addRow("", self.loading_preload_label)

        self._contact_global_layout.addWidget(self.friction_global_group)
        self._contact_global_layout.addStretch()
        self._contact_tab_layout.addStretch()

        # === APPLIED LOADS (per-element, shown dynamically) ===
        self.applied_loads_group = QGroupBox("Applied Loads")
        self.applied_loads_group.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self._applied_loads_vbox = QVBoxLayout(self.applied_loads_group)
        self._applied_loads_vbox.setContentsMargins(4, 4, 4, 4)
        self._applied_loads_vbox.setSpacing(2)
        self._applied_loads_list_label = QLabel("No loads applied")
        self._applied_loads_list_label.setWordWrap(True)
        self._applied_loads_list_label.setStyleSheet(f"color: {Theme.SUBTEXT}; font-size: 9pt;")
        self._applied_loads_vbox.addWidget(self._applied_loads_list_label)
        edit_loads_btn = QPushButton("Edit Loads...")
        edit_loads_btn.setToolTip("Open load/constraint dialog for this element")
        edit_loads_btn.clicked.connect(self.apply_load_requested.emit)
        self._applied_loads_vbox.addWidget(edit_loads_btn)
        self.applied_loads_group.setVisible(False)
        self.scroll_layout.addWidget(self.applied_loads_group)

        # === ACTIONS ===
        self.actions_group = QGroupBox("Actions")
        self.actions_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        actions_layout = QVBoxLayout(self.actions_group)
        actions_layout.setSpacing(4)

        self.load_btn = QPushButton("Apply Load/Constraint...")
        self.load_btn.clicked.connect(self.apply_load_requested.emit)

        self.recalc_btn = QPushButton("Recalculate MSD")
        self.recalc_btn.setToolTip("Recalculate k, c, m from geometry and material")
        self.recalc_btn.clicked.connect(self._on_recalculate)

        self.duplicate_btn = QPushButton("Duplicate Element")
        self.duplicate_btn.setToolTip("Create a copy of this element")
        self.duplicate_btn.clicked.connect(self.duplicate_requested.emit)

        self.delete_btn = QPushButton("Delete Element")
        self.delete_btn.setStyleSheet(f"color: {Theme.RED};")
        self.delete_btn.clicked.connect(self.delete_requested.emit)

        actions_layout.addWidget(self.load_btn)
        actions_layout.addWidget(self.recalc_btn)
        actions_layout.addWidget(self.duplicate_btn)
        actions_layout.addWidget(self.delete_btn)

        self.scroll_layout.addWidget(self.actions_group)

        self.scroll_layout.addStretch()

        layout.addWidget(self.inspector_tabs)

    def _on_material_changed(self, text: str):
        """Update material properties based on selection."""
        if self._updating:
            return

        # Material property lookup
        materials = {
            "A193 B7": (205000, 720, 860, 7850),
            "A193 B7M": (205000, 550, 720, 7850),
            "A193 B16": (205000, 690, 860, 7850),
            "A320 L7": (205000, 720, 860, 7850),
            "A354 BC": (205000, 640, 825, 7850),
            "Steel 8.8": (205000, 640, 800, 7850),
            "Steel 10.9": (205000, 900, 1040, 7850),
            "Steel 12.9": (205000, 1080, 1220, 7850),
        }

        for key, (E, Sy, Su, rho) in materials.items():
            if key in text:
                self._updating = True
                self.E_spin.setValue(E)
                self.Sy_spin.setValue(Sy)
                self.Su_spin.setValue(Su)
                self.rho_spin.setValue(rho)
                self._updating = False
                break

    def _on_recalculate(self):
        """Recalculate MSD parameters from geometry and material."""
        if not self.current_element:
            return

        elem = self.current_element.element_data

        # Update geometry
        elem.geometry.diameter = self.diameter_spin.value()
        elem.geometry.length = self.length_spin.value()
        elem.geometry.pitch = self.pitch_spin.value()

        # Update material
        elem.material.E = self.E_spin.value()
        elem.material.Sy = self.Sy_spin.value()
        elem.material.Su = self.Su_spin.value()
        elem.material.rho = self.rho_spin.value()

        # Recalculate MSD
        elem.msd.auto_calculate_k = True
        elem.msd.auto_calculate_c = True
        elem.msd.auto_calculate_m = True
        elem.update_msd_parameters()

        # Update display
        self._updating = True
        self._set_msd_display(elem.msd.k, elem.msd.c, elem.msd.m)
        self._updating = False

        self.current_element.update_display()
        self.property_changed.emit(self.current_element.element_id, "msd", None)

    # -----------------------------------------------------------------
    # Global Loading methods
    # -----------------------------------------------------------------

    def _on_locking_device_changed(self, index: int):
        """
        Phase F: Read locking_devices.json and populate slip onset / μ increase labels.

        Called when user selects a new device from locking_device_combo.
        """
        import json, os as _os
        keys = getattr(self, '_LOCKING_DEVICE_KEYS', [])
        if not (0 <= index < len(keys)):
            return
        key = keys[index]
        slip = 0.46   # Pai-Hess default
        mu_inc = 0.0
        junker = "—"
        try:
            _db = _os.path.normpath(_os.path.join(
                _os.path.dirname(__file__),
                '..', 'core', 'databases', 'locking_devices.json'))
            with open(_db, encoding='utf-8') as _f:
                _db_data = json.load(_f)
            dev = _db_data['locking_devices'][key]
            ret = dev.get('retention', {})
            _override = ret.get('slip_onset_factor_override')
            slip = float(_override) if _override is not None else 0.46
            mu_inc = float(ret.get('friction_increase', 0.0))
            # Junker class from effectiveness table
            _eff = _db_data.get('junker_din65151_effectiveness_class', {})
            junker = _eff.get(key, "—")
            # Keep only the grade letter (first char) for compactness
            junker = junker.split()[0] if junker != "—" else "—"
        except Exception:
            pass
        self._locking_device_slip = slip
        self._locking_device_mu_inc = mu_inc
        override_note = " (device)" if slip != 0.46 else " (Pai-Hess)"
        self._locking_slip_lbl.setText(f"{slip:.2f}{override_note}")
        self._locking_mu_inc_lbl.setText(f"+{mu_inc:.3f}")
        self._locking_junker_lbl.setText(junker)
        if not self._updating:
            self.loading_changed.emit(self.get_loading_data())

    # === UFU experimental presets (Junker 1 Hz shear, 3/4" UNC A320 L7) ===
    # Values from filename "Ensaio{5A,13A}-075_05mm_1Hz_{date}":
    #   075 => ~73-74% yield preload, 05mm => ±0.5 mm stroke, 1 Hz excitation
    # F_transverse is the measured peak actuator force (summary.json
    # actuator_amp_peak_kN); mu_initial is the 2026-04-23 calibration result.
    _UFU_PRESETS = {
        1: {  # 5A
            "label": "UFU 5A",
            "F_preload": 118243.1,   # N
            "F_transverse": 56630.0, # N (measured lab peak)
            "mu_initial": 0.164,
            "n_cycles": 561,
            "delta_amplitude": 0.5,  # mm
            "frequency": 1.0,        # Hz
            "load_type": "Transverse",
            "bolt_diameter": 19.05,  # 3/4"
            "pitch": 2.54,           # UNC 3/4-10
            "reference_csv": "Models/EXPERIMENTAL_UFU/reference_curves/UFU_5A_preload_decay.csv",
        },
        2: {  # 13A 1a tentativa (interrupted)
            "label": "UFU 13A 1a",
            "F_preload": 120038.7,
            "F_transverse": 49900.0,
            "mu_initial": 0.183,
            "n_cycles": 253,
            "delta_amplitude": 0.5,
            "frequency": 1.0,
            "load_type": "Transverse",
            "bolt_diameter": 19.05,
            "pitch": 2.54,
            "reference_csv": "Models/EXPERIMENTAL_UFU/reference_curves/UFU_13A_first_preload_decay.csv",
        },
        3: {  # 13A def
            "label": "UFU 13A def",
            "F_preload": 116497.9,
            "F_transverse": 69270.0,
            "mu_initial": 0.159,
            "n_cycles": 530,
            "delta_amplitude": 0.5,
            "frequency": 1.0,
            "load_type": "Transverse",
            "bolt_diameter": 19.05,
            "pitch": 2.54,
            "reference_csv": "Models/EXPERIMENTAL_UFU/reference_curves/UFU_13A_def_preload_decay.csv",
        },
    }

    def _on_experimental_preset_changed(self, index: int):
        """Apply UFU Junker lab preset to loading + friction widgets."""
        if index <= 0 or self._updating:
            return
        preset = self._UFU_PRESETS.get(index)
        if not preset:
            return
        self._updating = True
        try:
            self.load_type_combo.setCurrentText(preset["load_type"])
            self.preload_spin.setValue(preset["F_preload"])
            self.transverse_disp_spin.setValue(preset["delta_amplitude"])
            self.frequency_spin.setValue(preset["frequency"])
            # duration mode 0 = N cycles
            self._duration_mode_grp.button(0).setChecked(True)
            self.duration_spin.setValue(preset["n_cycles"])
            if hasattr(self, "mu_initial_spin"):
                self.mu_initial_spin.setValue(preset["mu_initial"])
            if hasattr(self, "bolt_diameter_spin"):
                self.bolt_diameter_spin.setValue(preset["bolt_diameter"])
            if hasattr(self, "bolt_pitch_spin"):
                self.bolt_pitch_spin.setValue(preset["pitch"])
            self._experimental_reference_csv = preset["reference_csv"]
        finally:
            self._updating = False
        self.loading_changed.emit(self.get_loading_data())

    def _on_loading_param_changed(self, _=None):
        """Emit loading_changed when any loading parameter changes."""
        if self._updating:
            return
        freq = self.frequency_spin.value()
        if self._duration_mode_grp.checkedId() == 0:
            # N cycles mode: duration_spin holds the cycle count
            n_cycles = max(1, int(self.duration_spin.value()))
            t_int = n_cycles / freq if freq > 0 else 0.0
            self.duration_derived_label.setText(f"t = {t_int:.2f} s")
        else:
            # Test time mode: duration_spin holds seconds
            t_int = self.duration_spin.value()
            n_cycles = max(1, int(freq * t_int))
            self.duration_derived_label.setText(f"N = {n_cycles:,} cycles")
        # Keep hidden holders in sync for solver compatibility
        self.integration_time_spin.setValue(t_int)
        self.cycles_spin.setValue(n_cycles)
        self.loading_changed.emit(self.get_loading_data())

    def _on_duration_mode_changed(self, _=None):
        """Switch the adaptive duration spinbox between N cycles and test time."""
        freq = self.frequency_spin.value()
        if self._duration_mode_grp.checkedId() == 0:
            # Switching TO N cycles: convert current time value to cycles
            t = self.integration_time_spin.value()
            n = max(1, int(freq * t))
            self.duration_spin.blockSignals(True)
            self.duration_spin.setRange(1, 10_000_000)
            self.duration_spin.setDecimals(0)
            self.duration_spin.setSingleStep(100)
            self.duration_spin.setSuffix(" cycles")
            self.duration_spin.setValue(float(n))
            self.duration_spin.blockSignals(False)
            self.duration_derived_label.setText(f"t = {t:.2f} s")
        else:
            # Switching TO test time: convert current cycles to seconds
            n = max(1, int(self.cycles_spin.value()))
            t = n / freq if freq > 0 else 160.0
            self.duration_spin.blockSignals(True)
            self.duration_spin.setRange(0.01, 100_000)
            self.duration_spin.setDecimals(2)
            self.duration_spin.setSingleStep(1.0)
            self.duration_spin.setSuffix(" s")
            self.duration_spin.setValue(t)
            self.duration_spin.blockSignals(False)
            self.duration_derived_label.setText(f"N = {n:,} cycles")
        # Sync hidden holders and emit via shared handler
        self._on_loading_param_changed()

    def _on_trans_force_changed(self, value):
        """Auto-convert transverse force to displacement."""
        if self._updating:
            return
        self._updating = True
        disp_m = value / self._k_transverse  # meters
        self.transverse_disp_spin.setValue(disp_m * 1000)  # mm
        self._updating = False
        self.loading_changed.emit(self.get_loading_data())

    def _on_trans_disp_changed(self, value):
        """Auto-convert transverse displacement to force."""
        if self._updating:
            return
        self._updating = True
        force = (value / 1000) * self._k_transverse  # N
        self.transverse_force_spin.setValue(force)
        self._updating = False
        self.loading_changed.emit(self.get_loading_data())

    def set_transverse_stiffness(self, k_trans: float):
        """Update the transverse stiffness used for force/displacement conversion."""
        if k_trans > 0:
            self._k_transverse = k_trans

    def _get_global_stress_area(self) -> float:
        """Return tensile stress area (mm²) using current diameter and pitch."""
        d_mm = self.bolt_diameter_spin.value()
        p_mm = self.bolt_pitch_spin.value()
        geom = get_thread_geometry(d_mm, p_mm)
        if geom:
            return float(geom["At"] or geom["As"] or 0.0)
        result = get_stress_area_from_threads(d_mm)
        return result if result else 0.0

    def _on_global_yield_pct_changed(self, value):
        """% yield changed in Global Loading → recompute F_preload."""
        if self._updating:
            return
        A_s = self._get_global_stress_area()
        Sy = self.loading_Sy_spin.value()
        F = (value / 100.0) * A_s * Sy  # N (mm² × MPa = N)

        self._updating = True
        self.preload_spin.setValue(F)
        self._updating = False

        self._update_global_preload_display(A_s, Sy, F)
        self.loading_changed.emit(self.get_loading_data())

    def _on_global_preload_force_changed(self, value):
        """F_preload changed directly in Global Loading → recompute % yield."""
        if self._updating:
            return
        A_s = self._get_global_stress_area()
        Sy = self.loading_Sy_spin.value()
        if A_s > 0 and Sy > 0:
            pct = (value / (A_s * Sy)) * 100.0
        else:
            pct = 0.0

        self._updating = True
        self.loading_yield_pct_spin.setValue(min(pct, 100.0))
        self._updating = False

        self._update_global_preload_display(A_s, Sy, value)
        self.loading_changed.emit(self.get_loading_data())

    def _on_bolt_geom_changed(self, _=None):
        """Bolt diameter, pitch, or Sy changed → auto-fill ISO geometry, recompute preload."""
        if self._updating:
            return

        d_mm = self.bolt_diameter_spin.value()

        # When diameter fires: look up coarse pitch and propagate
        if self.sender() is self.bolt_diameter_spin:
            coarse = get_thread_geometry(d_mm)  # coarse entry (pitch_mm=None)
            if coarse:
                self.bolt_pitch_spin.blockSignals(True)
                self.bolt_pitch_spin.setValue(coarse["P"])
                self.bolt_pitch_spin.blockSignals(False)

        # Re-read pitch (possibly just updated above)
        p_mm = self.bolt_pitch_spin.value()

        # Full geometry lookup for current d + p
        geom = get_thread_geometry(d_mm, p_mm)
        if geom:
            d2 = geom["d2"]
            d3 = geom["d3"]
            self.bolt_d2_label.setText(f"d₂: {d2:.3f} mm")
            self.bolt_d3_label.setText(f"d₃: {d3:.3f} mm")

            # Propagate to per-element thread contact widgets (blockSignals to avoid loops)
            self.pitch_contact_spin.blockSignals(True)
            self.pitch_contact_spin.setValue(geom["P"])
            self.pitch_contact_spin.blockSignals(False)

            r2 = d2 / 2.0
            self.mean_radius_spin.blockSignals(True)
            self.mean_radius_spin.setValue(round(r2, 3))
            self.mean_radius_spin.blockSignals(False)

            helix_deg = math.degrees(math.atan(geom["P"] / (2.0 * math.pi * r2)))
            self.helix_angle_spin.blockSignals(True)
            self.helix_angle_spin.setValue(round(helix_deg, 2))
            self.helix_angle_spin.blockSignals(False)

            A_s = float(geom["At"] or geom["As"] or 0.0)
        else:
            self.bolt_d2_label.setText("d₂: --")
            self.bolt_d3_label.setText("d₃: --")
            A_s = self._get_global_stress_area()

        Sy = self.loading_Sy_spin.value()
        pct = self.loading_yield_pct_spin.value()
        F = (pct / 100.0) * A_s * Sy

        self._updating = True
        self.preload_spin.setValue(F)
        self._updating = False

        self._update_global_preload_display(A_s, Sy, F)
        self.loading_changed.emit(self.get_loading_data())

    def _on_ext_force_mode_changed(self, index):
        """Switch external force input between N and % yield."""
        is_pct = (index == 1)
        self.external_force_spin.setVisible(not is_pct)
        self.ext_force_pct_spin.setVisible(is_pct)
        # Sync values when switching
        if is_pct:
            A_s = self._get_global_stress_area()
            Sy = self.loading_Sy_spin.value()
            F = self.external_force_spin.value()
            if A_s > 0 and Sy > 0:
                self.ext_force_pct_spin.setValue((F / (A_s * Sy)) * 100.0)
        else:
            self._on_ext_force_pct_changed(self.ext_force_pct_spin.value())

    def _on_ext_force_value_changed(self, value):
        """External force in N changed."""
        if self._updating:
            return
        self._on_loading_param_changed()

    def _on_ext_force_pct_changed(self, value):
        """External force as % yield changed → compute Newtons."""
        if self._updating:
            return
        A_s = self._get_global_stress_area()
        Sy = self.loading_Sy_spin.value()
        F = (value / 100.0) * A_s * Sy
        self._updating = True
        self.external_force_spin.setValue(F)
        self._updating = False
        self._on_loading_param_changed()

    def _update_global_preload_display(self, A_s: float, Sy: float, F: float):
        """Update the stress area and preload labels in both Loading and Contact panels."""
        # Contact > Global labels
        self.loading_As_label.setText(f"A_s: {A_s:.1f} mm²")
        if F >= 1000:
            self.loading_preload_label.setText(f"F\u2080 = {F/1000:.1f} kN")
        else:
            self.loading_preload_label.setText(f"F\u2080 = {F:.0f} N")

        # Loading > Global summary label (Phase 1.2) — live formula result
        pct = self.loading_yield_pct_spin.value()
        if A_s > 0 and Sy > 0:
            f_kn = F / 1000.0
            self.loading_calc_label.setText(
                f"A_s = {A_s:.1f} mm²  ·  F₀ = {pct:.0f}% × {Sy:.0f} MPa = {f_kn:.2f} kN"
            )
        else:
            self.loading_calc_label.setText("A_s: --  ·  F₀: --  (set bolt size in Contact tab)")

    def _apply_control_mode_enable(self):
        """Grey out the transverse input that isn't the control driver."""
        idx = self.control_mode_combo.currentIndex()
        disp = (self._control_mode_keys[idx] == "displacement")
        self.transverse_disp_spin.setEnabled(disp)
        self.transverse_force_spin.setEnabled(not disp)

    def _on_control_mode_changed(self):
        self._apply_control_mode_enable()
        if not getattr(self, "_updating", False):
            self.loading_changed.emit(self.get_loading_data())

    def get_loading_data(self) -> dict:
        """Return all loading and friction parameters as a dict."""
        return {
            "type": self.load_type_combo.currentText(),
            "control_mode": self._control_mode_keys[
                self.control_mode_combo.currentIndex()],
            "F_preload": self.preload_spin.value(),
            "preload_percent_yield": self.loading_yield_pct_spin.value(),
            "F_transverse": self.transverse_force_spin.value(),
            "delta_amplitude": self.transverse_disp_spin.value(),
            "frequency": self.frequency_spin.value(),
            "n_cycles": self.cycles_spin.value(),
            "integration_time": self.integration_time_spin.value(),
            "duration_mode": "cycles" if self._duration_mode_grp.checkedId() == 0 else "time",
            "F_external": self.external_force_spin.value(),
            "T_applied": self.torque_spin.value(),
            "delta_T": self.delta_T_spin.value(),
            # Friction / bolt geometry
            "mu_initial": self.mu_initial_spin.value(),
            "lubricated": self.lubricated_check.isChecked(),
            "bolt_diameter": self.bolt_diameter_spin.value(),
            "pitch": self.bolt_pitch_spin.value(),
            "Sy": self.loading_Sy_spin.value(),
            # Friction evolution model (Phase 3.1)
            "friction_evolution_model": self.friction_model_combo.currentText(),
            # VDI 2230 load factors (Phase A)
            "R_factor": self.R_factor_spin.value(),
            "dynamic_factor": self.dynamic_factor_spin.value(),
            "n_load_plane": self.n_load_plane_spin.value(),
            "load_waveform": self.load_waveform_combo.currentText(),
            # Locking device (Phase F)
            "locking_device_type": self.locking_device_combo.currentIndex(),
            "locking_device_slip_onset": getattr(self, '_locking_device_slip', 0.46),
            "locking_device_mu_increase": getattr(self, '_locking_device_mu_inc', 0.0),
            # Curve-shape Stage II tuning (2026-04-23)
            "curve_F_infinity_ratio": self.curve_F_inf_spin.value(),
            "curve_friction_recovery_gain": self.curve_mu_gain_spin.value(),
            "curve_creep_coefficient": self.curve_creep_spin.value(),
            "curve_noise_amplitude": self.curve_noise_spin.value(),
        }

    def set_loading_data(self, data: dict):
        """Populate loading UI from a dict (used when loading a project)."""
        self._updating = True
        if "type" in data:
            # Case-insensitive match — UFU .msd files store "TRANSVERSE"
            # (uppercase); the combo has entries like "Transverse (Junker)".
            raw = str(data["type"]).strip().lower()
            key = {
                "axial": "axial",
                "transverse": "transverse",
                "combined": "combined",
                "impulse": "impulse",
                "custom": "custom",
            }.get(raw, raw)
            found_idx = -1
            for i in range(self.load_type_combo.count()):
                if key in self.load_type_combo.itemText(i).lower():
                    found_idx = i
                    break
            if found_idx < 0:
                found_idx = self.load_type_combo.findText(str(data["type"]))
            if found_idx >= 0:
                self.load_type_combo.setCurrentIndex(found_idx)
        if "control_mode" in data:
            cm = str(data["control_mode"]).strip().lower()
            if cm in self._control_mode_keys:
                self.control_mode_combo.setCurrentIndex(
                    self._control_mode_keys.index(cm))
            self._apply_control_mode_enable()
        if "F_preload" in data:
            self.preload_spin.setValue(data["F_preload"])
        if "preload_percent_yield" in data:
            self.loading_yield_pct_spin.setValue(data["preload_percent_yield"])
        if "F_transverse" in data:
            self.transverse_force_spin.setValue(data["F_transverse"])
        if "delta_amplitude" in data:
            self.transverse_disp_spin.setValue(data["delta_amplitude"])
        if "frequency" in data:
            self.frequency_spin.setValue(data["frequency"])
        freq = self.frequency_spin.value()
        mode = data.get("duration_mode", "time")
        if mode == "cycles":
            # Restore N cycles mode
            n = int(data.get("n_cycles", max(1, int(freq * data.get("integration_time", 160.0)))))
            t = n / freq if freq > 0 else 0.0
            self.cycles_mode_radio.setChecked(True)
            self.duration_spin.blockSignals(True)
            self.duration_spin.setRange(1, 10_000_000)
            self.duration_spin.setDecimals(0)
            self.duration_spin.setSingleStep(100)
            self.duration_spin.setSuffix(" cycles")
            self.duration_spin.setValue(float(n))
            self.duration_spin.blockSignals(False)
            self.duration_derived_label.setText(f"t = {t:.2f} s")
            self.integration_time_spin.setValue(t)
            self.cycles_spin.setValue(n)
        else:
            # Restore test time mode (default)
            if "integration_time" in data:
                t = data["integration_time"]
            elif "n_cycles" in data:
                t = int(data["n_cycles"]) / freq if freq > 0 else 160.0
            else:
                t = 160.0
            n = max(1, int(freq * t))
            self.time_mode_radio.setChecked(True)
            self.duration_spin.blockSignals(True)
            self.duration_spin.setRange(0.01, 100_000)
            self.duration_spin.setDecimals(2)
            self.duration_spin.setSingleStep(1.0)
            self.duration_spin.setSuffix(" s")
            self.duration_spin.setValue(t)
            self.duration_spin.blockSignals(False)
            self.duration_derived_label.setText(f"N = {n:,} cycles")
            self.integration_time_spin.setValue(t)
            self.cycles_spin.setValue(n)
        if "F_external" in data:
            self.external_force_spin.setValue(data["F_external"])
        if "T_applied" in data:
            self.torque_spin.setValue(data["T_applied"])
        if "delta_T" in data:
            self.delta_T_spin.setValue(data["delta_T"])
        if "mu_initial" in data:
            self.mu_initial_spin.setValue(data["mu_initial"])
        if "lubricated" in data:
            self.lubricated_check.setChecked(data["lubricated"])
        if "bolt_diameter" in data:
            self.bolt_diameter_spin.setValue(data["bolt_diameter"])
        if "pitch" in data:
            self.bolt_pitch_spin.setValue(data["pitch"])
        if "Sy" in data:
            self.loading_Sy_spin.setValue(data["Sy"])
        if "friction_evolution_model" in data:
            idx = self.friction_model_combo.findText(data["friction_evolution_model"])
            if idx >= 0:
                self.friction_model_combo.setCurrentIndex(idx)
        # VDI 2230 load factors (Phase A)
        if "R_factor" in data:
            self.R_factor_spin.setValue(data["R_factor"])
        if "dynamic_factor" in data:
            self.dynamic_factor_spin.setValue(data["dynamic_factor"])
        if "n_load_plane" in data:
            self.n_load_plane_spin.setValue(data["n_load_plane"])
        if "load_waveform" in data:
            idx = self.load_waveform_combo.findText(data["load_waveform"])
            if idx >= 0:
                self.load_waveform_combo.setCurrentIndex(idx)
        # Locking device (Phase F) — blockSignals so _on_locking_device_changed
        # doesn't emit loading_changed during bulk restore
        if "locking_device_type" in data:
            self.locking_device_combo.blockSignals(True)
            self.locking_device_combo.setCurrentIndex(int(data["locking_device_type"]))
            self.locking_device_combo.blockSignals(False)
            # Restore cached numeric values directly (avoid JSON re-read overhead)
            self._locking_device_slip = float(data.get("locking_device_slip_onset", 0.46))
            self._locking_device_mu_inc = float(data.get("locking_device_mu_increase", 0.0))
            # Update info labels
            override_note = " (device)" if self._locking_device_slip != 0.46 else " (Pai-Hess)"
            self._locking_slip_lbl.setText(f"{self._locking_device_slip:.2f}{override_note}")
            self._locking_mu_inc_lbl.setText(f"+{self._locking_device_mu_inc:.3f}")
        # Curve-shape Stage II tuning (2026-04-23)
        if "curve_F_infinity_ratio" in data:
            self.curve_F_inf_spin.setValue(float(data["curve_F_infinity_ratio"]))
        if "curve_friction_recovery_gain" in data:
            self.curve_mu_gain_spin.setValue(float(data["curve_friction_recovery_gain"]))
        if "curve_creep_coefficient" in data:
            self.curve_creep_spin.setValue(float(data["curve_creep_coefficient"]))
        if "curve_noise_amplitude" in data:
            self.curve_noise_spin.setValue(float(data["curve_noise_amplitude"]))
        self._updating = False

        # Auto-compute F_preload from % yield if F_preload is zero but % yield > 0
        # This handles saved .msd files where F_preload was not stored correctly
        F = self.preload_spin.value()
        pct = self.loading_yield_pct_spin.value()
        if F == 0.0 and pct > 0.0:
            A_s = self._get_global_stress_area()
            Sy = self.loading_Sy_spin.value()
            if A_s > 0 and Sy > 0:
                F = (pct / 100.0) * A_s * Sy
                self.preload_spin.setValue(F)

        # Update display labels after loading all values
        A_s = self._get_global_stress_area()
        Sy = self.loading_Sy_spin.value()
        F = self.preload_spin.value()
        self._update_global_preload_display(A_s, Sy, F)

        # Refresh d₂/d₃ labels and per-element thread contact fields.
        # Keep `_updating = True` during this call so the early guard in
        # `_on_bolt_geom_changed` fires and we DON'T recompute F_preload
        # as pct·A_s·Sy (which would overwrite the authoritative value
        # set from `data["F_preload"]` above — e.g. UFU 5A's 118,243 N
        # getting clobbered to 0.7·157·724 ≈ 79,568 N with the M16
        # defaults + A320-L7 Sy).
        F_preserve = self.preload_spin.value()
        self._updating = True
        try:
            self._on_bolt_geom_changed()
        finally:
            self._updating = False
        # Belt-and-suspenders: if anything managed to mutate the preload
        # during geometry refresh, restore the loaded value.
        if abs(self.preload_spin.value() - F_preserve) > 1e-6:
            self.preload_spin.setValue(F_preserve)

    def set_element(self, element: Optional[ElementGraphicsItem]):
        """Set the element to inspect."""
        self._updating = True

        self.current_element = element

        if element is None:
            self.header_label.setText("Global Loading Configuration")
            self.type_group.setVisible(False)
            self.grid_group.setVisible(False)
            self.msd_group.setVisible(False)
            self.material_group.setVisible(False)
            self.preload_group.setVisible(False)
            self.friction_group.setVisible(False)
            self.thermal_group.setVisible(False)
            self.geometry_group.setVisible(False)
            self.thread_panel.setVisible(False)
            self.actions_group.setVisible(False)
            self.applied_loads_group.setVisible(False)
            # Switch to Loading tab when no element is selected
            self.inspector_tabs.setCurrentIndex(1)
            self._updating = False
            return

        elem_data = element.element_data
        elem_type = element.element_type

        # Header
        self.header_label.setText(
            f"{element.visual.symbol} {element.visual.name} #{element.element_id}"
        )

        # Element type selector
        type_idx = self.type_combo.findText(elem_type)
        if type_idx >= 0:
            self.type_combo.setCurrentIndex(type_idx)

        # Common properties for all elements
        self.type_group.setVisible(True)
        self.grid_group.setVisible(True)
        self.msd_group.setVisible(True)
        self.actions_group.setVisible(True)

        # Grid position
        self.row_spin.setValue(element.grid_row)
        self.col_spin.setValue(element.grid_col)

        # MSD values (unit-aware)
        self._set_msd_display(elem_data.msd.k, elem_data.msd.c, elem_data.msd.m)

        # Determine element category
        is_bolt_element = elem_type in ("HEAD", "SHANK", "NUT", "WASHER")
        is_member_element = elem_type in ("FLANGE", "GASKET")
        is_contact_element = elem_type in ("THREAD", "BEARING_HEAD", "BEARING_NUT",
                                          "FLANGE_FLANGE", "WASHER_CONTACT",
                                          "GASKET_CONTACT", "GENERIC_CONTACT")
        is_boundary = elem_type == "GROUND"

        # Show/hide property groups based on element type
        # Bolt and member elements show material, friction, thermal, geometry
        show_material = is_bolt_element or is_member_element
        show_friction = is_bolt_element  # Only bolts have thread/bearing friction
        show_thermal = is_bolt_element or is_member_element
        show_geometry = is_bolt_element or is_member_element

        self.material_group.setVisible(show_material)
        self.friction_group.setVisible(show_friction)
        self.thermal_group.setVisible(show_thermal)
        self.geometry_group.setVisible(show_geometry)

        # Show preload group for bolt elements; read-only utilization for members
        show_preload = is_bolt_element or is_member_element
        self.preload_group.setVisible(show_preload)
        if show_preload:
            self.yield_pct_spin.setReadOnly(not is_bolt_element)
            # Always default to % of Yield mode
            self.preload_mode_combo.setCurrentIndex(0)
            self.yield_pct_spin.setVisible(True)
            self.force_spin.setVisible(False)
            self.yield_pct_spin.setValue(elem_data.preload_percent_yield)
            self.force_spin.setValue(elem_data.preload_force)
            self._update_preload_display(elem_data)

        if show_material:
            self.E_spin.setValue(elem_data.material.E)
            self.Sy_spin.setValue(elem_data.material.Sy)
            self.Su_spin.setValue(elem_data.material.Su)
            self.rho_spin.setValue(elem_data.material.rho)

        if show_friction:
            self.mu_thread_spin.setValue(elem_data.friction.mu_thread)
            self.mu_bearing_spin.setValue(elem_data.friction.mu_bearing)

        if show_thermal:
            self.alpha_spin.setValue(elem_data.material.alpha * 1e6)
            self.T_ref_spin.setValue(elem_data.material.T_ref)

        if show_geometry:
            self.diameter_spin.setValue(elem_data.geometry.diameter)
            self.length_spin.setValue(elem_data.geometry.length)
            self.pitch_spin.setValue(elem_data.geometry.pitch)

        # Applied Loads summary (per-element)
        applied_loads = getattr(elem_data, 'applied_loads', [])
        constraints = getattr(elem_data, 'constraints', [])
        has_loads = bool(applied_loads or constraints)
        self.applied_loads_group.setVisible(has_loads or not is_contact_element)
        _LOAD_ICONS = {
            "axial": "\u2195", "shear": "\u2194", "bending": "\u21b7",
            "torsion": "\u21ba", "impact": "\u26a1", "moment": "\u21ba",
        }
        _CONSTR_ICONS = {"FIXED": "\u25bc", "PRESCRIBED": "\u21e5", "SPRING": "\u29be"}
        lines = []
        for ld in applied_loads:
            icon = _LOAD_ICONS.get(str(getattr(ld, 'load_type', '')).lower(), "\u25b6")
            mag = getattr(ld, 'magnitude', 0.0)
            ltype = str(getattr(ld, 'load_type', '?')).capitalize()
            lines.append(f"{icon} {ltype}: {mag:.0f} N")
        for cs in constraints:
            ctype = str(getattr(cs, 'constraint_type', '?'))
            icon = _CONSTR_ICONS.get(ctype.upper().split('.')[-1], "\u25cf")
            val = getattr(cs, 'value', None)
            txt = f"{icon} {ctype.split('.')[-1].capitalize()}"
            if val is not None:
                txt += f": {val:.4g}"
            lines.append(txt)
        if lines:
            self._applied_loads_list_label.setText("\n".join(lines))
            self._applied_loads_list_label.setStyleSheet(
                f"color: {Theme.GREEN}; font-size: 9pt;")
        else:
            self._applied_loads_list_label.setText("No loads applied")
            self._applied_loads_list_label.setStyleSheet(
                f"color: {Theme.SUBTEXT}; font-size: 9pt;")

        # Thread panel (not for contacts - those use thread_contact_group)
        is_thread_structural = elem_type in ("NUT",)  # Removed THREAD from here
        self.thread_panel.setVisible(is_thread_structural)

        if is_thread_structural:
            if elem_data.thread_fillet_model:
                self.thread_panel.set_model(elem_data.thread_fillet_model)
            else:
                elem_data.thread_fillet_model = ThreadFilletModel()
                self.thread_panel.set_model(elem_data.thread_fillet_model)

        # Switch to appropriate tab: contact elements → Contact tab, others → Element tab
        if is_contact_element:
            self.inspector_tabs.setCurrentIndex(2)
            self._contact_subtabs.setCurrentIndex(1)  # jump to Per-Element
        else:
            self.inspector_tabs.setCurrentIndex(0)

        # Contact element panels (all visible in Contact tab — filter by specific type)
        self.contact_group.setVisible(is_contact_element)
        self.thread_contact_group.setVisible(elem_type == "THREAD")
        self.bearing_contact_group.setVisible(elem_type in ("BEARING_HEAD", "BEARING_NUT"))
        self.gasket_contact_group.setVisible(elem_type in ("GASKET_CONTACT",))

        # Populate contact properties if applicable
        if is_contact_element:
            # Read from persisted contact_props if available, otherwise use defaults
            import math
            cp = getattr(elem_data, 'contact_props', None) or {}

            # General contact fields (always shown for contact elements)
            self.k_normal_spin.setValue(cp.get("k_normal", 1e10))
            self.k_tangential_spin.setValue(cp.get("k_tangential", 5e9))
            self.c_normal_spin.setValue(cp.get("c_normal", 100.0))
            self.c_tangential_spin.setValue(cp.get("c_tangential", 50.0))
            self.mu_static_spin.setValue(cp.get("mu_static", 0.15))
            self.mu_kinetic_spin.setValue(cp.get("mu_kinetic", 0.12))

            if elem_type == "THREAD":
                pitch_val = cp.get("pitch", 1.75)
                mean_r_val = cp.get("mean_radius", 10.0)
                self.pitch_contact_spin.setValue(pitch_val)
                self.mean_radius_spin.setValue(mean_r_val)
                self.engagement_length_spin.setValue(
                    cp.get("engagement_length", 20.0))
                helix_angle = math.degrees(
                    math.atan(pitch_val / (2.0 * math.pi * mean_r_val))
                ) if mean_r_val > 0 else 0.0
                self.helix_angle_spin.setValue(helix_angle)

            elif elem_type in ("BEARING_HEAD", "BEARING_NUT"):
                r_i = cp.get("inner_radius", 6.5)
                r_o = cp.get("outer_radius", 10.0)
                self.inner_radius_spin.setValue(r_i)
                self.outer_radius_spin.setValue(r_o)
                r_eff = (2.0 / 3.0) * (r_o**3 - r_i**3) / (r_o**2 - r_i**2) \
                    if r_o > r_i > 0 else 0.0
                self.effective_radius_spin.setValue(r_eff)
                self.surface_roughness_spin.setValue(
                    cp.get("surface_roughness", 1.6))

        self._updating = False

    def _on_grid_changed(self):
        """Handle grid position change."""
        if self._updating or not self.current_element:
            return

        before = (self._schematic._snapshot_positions()
                  if self._schematic is not None else None)
        self.current_element.set_grid_position(
            self.row_spin.value(),
            self.col_spin.value()
        )
        self.property_changed.emit(
            self.current_element.element_id, "grid_position",
            (self.row_spin.value(), self.col_spin.value())
        )
        if before is not None:
            self._push_grid_change(before)

    def _open_calc(self, formula_key: str, target_spin: QDoubleSpinBox):
        """Open formula calculator popup and apply result to target_spin (3.7)."""
        dlg = FormulaCalculatorDialog(formula_key, parent=self)
        dlg.value_accepted.connect(target_spin.setValue)
        dlg.exec()

    def _record_value(self, history_key: str, value: float):
        """Record a value in the per-key history list (max 5 entries, no duplicates)."""
        hist = self._value_history.setdefault(history_key, [])
        if value in hist:
            hist.remove(value)
        hist.insert(0, value)
        if len(hist) > 5:
            hist.pop()

    # -----------------------------------------------------------------
    # Undo/redo push helpers
    #
    # These record an edit that the calling handler has ALREADY applied to the
    # model.  ChangePropertyCommand's first redo is a no-op, so there is no
    # double application; on undo/redo it re-syncs the inspector spinboxes via
    # set_element (guarded by _updating → no signal loop).
    # -----------------------------------------------------------------

    def _push_property_change(self, prop_path: str, old_value, new_value):
        """Record a single-attribute property edit (k / c / m / ...)."""
        stack = self._undo_stack
        if (stack is None or self._schematic is None
                or self.current_element is None or old_value == new_value):
            return
        stack.push(ChangePropertyCommand(
            self._schematic, self.current_element.element_id,
            prop_path, old_value, new_value, inspector=self,
        ))

    def _push_preload_change(self, old_pct, new_pct, old_force, new_force):
        """Record a preload edit (percent + derived force) as one command."""
        stack = self._undo_stack
        if (stack is None or self._schematic is None
                or self.current_element is None):
            return
        if old_pct == new_pct and old_force == new_force:
            return
        stack.push(ChangePreloadCommand(
            self._schematic, self.current_element.element_id,
            old_pct, new_pct, old_force, new_force, inspector=self))

    def _push_grid_change(self, before: dict):
        """Record an inspector row/col edit as one undoable grid move."""
        stack = self._undo_stack
        if stack is None or self._schematic is None:
            return
        # Reconcile the grid dict for the just-applied edit, then record it.
        self._schematic._sync_grid_from_items()
        after = self._schematic._snapshot_positions()
        if after == before:
            return
        stack.push(GridPositionCommand(self._schematic, before, after, "Move element"))

    def _show_value_history(self, history_key: str, target_spin: QDoubleSpinBox, btn: QToolButton):
        """Show a dropdown menu of recent values for the spinbox (3.17)."""
        hist = self._value_history.get(history_key, [])
        menu = QMenu(self)
        if hist:
            for v in hist:
                act = menu.addAction(f"{v:,.4g}")
                act.triggered.connect(lambda _, x=v: target_spin.setValue(x))
        else:
            no_act = menu.addAction("No history yet")
            no_act.setEnabled(False)
        menu.exec(btn.mapToGlobal(QPoint(0, btn.height())))

    def _on_unit_mode_changed(self, imperial: bool):
        """Switch display between SI and Imperial units (3.6).

        Internal model values always remain in SI.
        Only display spinboxes are scaled; get/set methods convert back.
        """
        self._imperial = imperial
        self._unit_toggle.setText("IMP" if imperial else "SI")

        # Conversion factors (SI→IMP) or reciprocals (IMP→SI)
        fk = self._SI_TO_IMP["k"]   # N/m → lbf/in
        fc = self._SI_TO_IMP["c"]
        fm = self._SI_TO_IMP["m"]
        ff = self._SI_TO_IMP["force"]

        self._updating = True
        try:
            if imperial:
                # k
                self.k_spin.setValue(self.k_spin.value() * fk)
                self.k_spin.setSuffix(" lbf/in")
                # c
                self.c_spin.setValue(self.c_spin.value() * fc)
                self.c_spin.setSuffix(" lbf·s/in")
                # m
                self.m_spin.setValue(self.m_spin.value() * fm)
                self.m_spin.setSuffix(" lb")
                # preload force (if visible)
                if hasattr(self, 'force_spin') and self.force_spin.isVisible():
                    self.force_spin.setValue(self.force_spin.value() * ff)
                    self.force_spin.setSuffix(" lbf")
            else:
                # Reverse — IMP → SI
                self.k_spin.setValue(self.k_spin.value() / fk)
                self.k_spin.setSuffix("")
                self.c_spin.setValue(self.c_spin.value() / fc)
                self.c_spin.setSuffix("")
                self.m_spin.setValue(self.m_spin.value() / fm)
                self.m_spin.setSuffix(" kg")
                if hasattr(self, 'force_spin') and self.force_spin.isVisible():
                    self.force_spin.setValue(self.force_spin.value() / ff)
                    self.force_spin.setSuffix(" N")
        finally:
            self._updating = False

    def _set_msd_display(self, k_si: float, c_si: float, m_si: float):
        """Populate k/c/m spinboxes converting SI values to current unit mode."""
        if self._imperial:
            self.k_spin.setValue(k_si * self._SI_TO_IMP["k"])
            self.c_spin.setValue(c_si * self._SI_TO_IMP["c"])
            self.m_spin.setValue(m_si * self._SI_TO_IMP["m"])
        else:
            self.k_spin.setValue(k_si)
            self.c_spin.setValue(c_si)
            self.m_spin.setValue(m_si)

    def get_si_k(self) -> float:
        """Return stiffness in SI (N/m) regardless of current unit mode."""
        val = self.k_spin.value()
        return val / self._SI_TO_IMP["k"] if self._imperial else val

    def get_si_c(self) -> float:
        """Return damping in SI (N·s/m)."""
        val = self.c_spin.value()
        return val / self._SI_TO_IMP["c"] if self._imperial else val

    def get_si_m(self) -> float:
        """Return mass in SI (kg)."""
        val = self.m_spin.value()
        return val / self._SI_TO_IMP["m"] if self._imperial else val

    def _on_k_changed(self, value):
        """Handle stiffness change (store always in SI N/m)."""
        if self._updating or not self.current_element:
            return
        si_val = self.get_si_k()
        old_val = self.current_element.element_data.msd.k
        self.current_element.element_data.msd.k = si_val
        self.current_element.update_display()
        self._record_value("k", si_val)  # 3.17 history
        self.property_changed.emit(self.current_element.element_id, "k", si_val)
        self._push_property_change("msd.k", old_val, si_val)

    def _on_c_changed(self, value):
        """Handle damping change (store always in SI N·s/m)."""
        if self._updating or not self.current_element:
            return
        si_val = self.get_si_c()
        old_val = self.current_element.element_data.msd.c
        self.current_element.element_data.msd.c = si_val
        self._record_value("c", si_val)  # 3.17 history
        self.property_changed.emit(self.current_element.element_id, "c", si_val)
        self._push_property_change("msd.c", old_val, si_val)

    def _on_m_changed(self, value):
        """Handle mass change (store always in SI kg)."""
        if self._updating or not self.current_element:
            return
        si_val = self.get_si_m()
        old_val = self.current_element.element_data.msd.m
        self.current_element.element_data.msd.m = si_val
        self._record_value("m", si_val)  # 3.17 history
        self.property_changed.emit(self.current_element.element_id, "m", si_val)
        self._push_property_change("msd.m", old_val, si_val)

    def _on_preload_mode_changed(self, index):
        """Switch between % yield and force input modes."""
        is_percent = (index == 0)
        self.yield_pct_spin.setVisible(is_percent)
        self.force_spin.setVisible(not is_percent)
        # When switching to force mode, sync the force spin to current value
        if not is_percent and self.current_element:
            self._updating = True
            self.force_spin.setValue(self.current_element.element_data.preload_force)
            self._updating = False

    def _on_percent_yield_changed(self, value):
        """% yield changed -> recompute preload force."""
        if self._updating or not self.current_element:
            return
        elem = self.current_element.element_data
        old_pct = elem.preload_percent_yield
        old_force = elem.preload_force
        elem.preload_percent_yield = value

        # Compute force
        A_s = self._get_stress_area()  # mm²
        Sy = elem.material.Sy           # MPa
        F = (value / 100.0) * A_s * Sy  # N (mm² * MPa = N)
        elem.preload_force = F

        # Sync force spin
        self._updating = True
        self.force_spin.setValue(F)
        self._updating = False

        self.force_display_label.setText(f"{F / 1000:.1f} kN")
        self.current_element.update_display()
        self.property_changed.emit(self.current_element.element_id, "preload", value)
        self._push_preload_change(old_pct, value, old_force, F)

    def _on_force_changed(self, value):
        """Force (N) changed -> recompute % yield."""
        if self._updating or not self.current_element:
            return
        elem = self.current_element.element_data
        old_pct = elem.preload_percent_yield
        old_force = elem.preload_force
        elem.preload_force = value

        # Compute % yield from force
        A_s = self._get_stress_area()  # mm²
        Sy = elem.material.Sy           # MPa
        if A_s > 0 and Sy > 0:
            pct = (value / (A_s * Sy)) * 100.0
        else:
            pct = 0.0
        elem.preload_percent_yield = pct

        # Sync % spin
        self._updating = True
        self.yield_pct_spin.setValue(pct)
        self._updating = False

        self.force_display_label.setText(f"{value / 1000:.1f} kN")
        self.current_element.update_display()
        self.property_changed.emit(self.current_element.element_id, "preload", value)
        self._push_preload_change(old_pct, pct, old_force, value)

    def _update_preload_display(self, elem_data):
        """Update preload display labels for current element."""
        A_s = self._get_stress_area()
        Sy = elem_data.material.Sy
        pct = elem_data.preload_percent_yield

        self.stress_area_label.setText(f"A_s: {A_s:.1f} mm²")
        self.Sy_display_label.setText(f"Sy: {Sy:.0f} MPa")

        F = (pct / 100.0) * A_s * Sy
        elem_data.preload_force = F
        self.force_display_label.setText(f"{F / 1000:.1f} kN")

        # Sync force spin if in force mode
        self._updating = True
        self.force_spin.setValue(F)
        self._updating = False

    def _get_stress_area(self) -> float:
        """Get tensile stress area (mm²) for current element's bolt diameter."""
        if not self.current_element:
            return 0.0
        d_mm = self.current_element.element_data.geometry.diameter
        result = get_stress_area_from_threads(d_mm)
        return result if result else 0.0

    def _on_thread_config_changed(self, model: ThreadFilletModel):
        """Handle thread fillet config change."""
        if self._updating or not self.current_element:
            return
        self.current_element.element_data.thread_fillet_model = model
        self.property_changed.emit(
            self.current_element.element_id, "thread_fillet_model", model
        )

    def _on_type_combo_changed(self, new_type: str):
        """Handle element type change request."""
        if self._updating or not self.current_element:
            return
        if new_type != self.current_element.element_type:
            self.type_change_requested.emit(new_type)

    def refresh_per_element_loads(self, elements_dict: dict):
        """Rebuild Loading > Per-Element sub-tab with current element applied loads."""
        # Clear old widgets
        while self._per_elem_load_layout.count():
            item = self._per_elem_load_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        ICONS = {
            "axial": "\u2195", "shear": "\u2194", "bending": "\u21b7",
            "torsion": "\u21ba", "impact": "\u26a1",
        }

        found_any = False
        for elem_id, elem_item in sorted(
            elements_dict.items(),
            key=lambda x: getattr(x[1], 'grid_row', 0)
        ):
            loads = getattr(elem_item.element_data, 'applied_loads', [])
            constraints = getattr(elem_item.element_data, 'constraints', [])
            if not loads and not constraints:
                continue
            found_any = True
            sym = getattr(getattr(elem_item, 'visual', None), 'symbol', '?')
            name = getattr(getattr(elem_item, 'visual', None), 'name', str(elem_id))
            grp = QGroupBox(f"{sym} {name} #{elem_id}")
            grp.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            grp_layout = QFormLayout(grp)
            grp_layout.setSpacing(2)
            grp_layout.setContentsMargins(4, 4, 4, 4)
            for ld in loads:
                icon = ICONS.get(str(getattr(ld, 'load_type', '')).lower(), "\u25b6")
                ltype = str(getattr(ld, 'load_type', '?')).split('.')[-1].capitalize()
                mag = getattr(ld, 'magnitude', 0.0)
                tv = str(getattr(ld, 'time_variation', '')).split('.')[-1].capitalize()
                lbl = QLabel(f"{icon} {ltype}: {mag:.0f} N  [{tv}]")
                lbl.setStyleSheet(f"color: {Theme.GREEN};")
                grp_layout.addRow(lbl)
            for cs in constraints:
                ctype = str(getattr(cs, 'constraint_type', '?')).split('.')[-1].capitalize()
                val = getattr(cs, 'value', None)
                txt = f"\u25aa {ctype}" + (f": {val:.4g}" if val is not None else "")
                lbl = QLabel(txt)
                lbl.setStyleSheet(f"color: {Theme.YELLOW};")
                grp_layout.addRow(lbl)
            self._per_elem_load_layout.addWidget(grp)

        if not found_any:
            lbl = QLabel(
                "No per-element loads defined.\n"
                "Right-click an element \u2192 Apply Load..."
            )
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"color: {Theme.SUBTEXT}; padding: 8px;")
            self._per_elem_load_layout.addWidget(lbl)

        self._per_elem_load_layout.addStretch()


# =============================================================================
# ELEMENT PALETTE
# =============================================================================

class ElementPalette(QWidget):
    """Palette of available MSD elements."""

    element_selected = pyqtSignal(str)
    preset_requested = pyqtSignal(str)
    wizard_requested = pyqtSignal()  # Request to open flange joint wizard
    validation_case_requested = pyqtSignal(str)  # Validation case short name
    open_paper_requested = pyqtSignal()  # Open validation paper

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the palette UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Wizard
        wizard_group = QGroupBox("Joint Wizard")
        wizard_layout = QVBoxLayout(wizard_group)

        wizard_btn = QPushButton("Configure Joint...")
        wizard_btn.setStyleSheet(f"font-weight: bold; color: {Theme.BLUE};")
        wizard_btn.setToolTip("Open the comprehensive joint configuration wizard")
        wizard_btn.clicked.connect(self.wizard_requested.emit)
        wizard_layout.addWidget(wizard_btn)

        layout.addWidget(wizard_group)

        # Presets
        presets_group = QGroupBox("Quick Presets")
        presets_layout = QVBoxLayout(presets_group)

        for name, label in [
            ("single_bolt", "Single Bolt Joint"),
            ("flanged_joint", "Basic Flanged Joint"),
            ("junker_test", "Junker Test Setup")
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, n=name: self.preset_requested.emit(n))
            presets_layout.addWidget(btn)

        layout.addWidget(presets_group)

        # (Validation Cases panel removed — use the 📁 Case Studies toolbar button instead.)

        # Bolt elements
        bolt_group = QGroupBox("Bolt Elements")
        bolt_layout = QVBoxLayout(bolt_group)

        for elem_type in ["HEAD", "SHANK", "NUT", "WASHER"]:
            visual = ELEMENT_VISUALS[elem_type]
            btn = QPushButton(f"{visual.symbol} {visual.name}")
            btn.setToolTip(visual.description)
            btn.clicked.connect(lambda checked, t=elem_type: self.element_selected.emit(t))
            bolt_layout.addWidget(btn)

        layout.addWidget(bolt_group)

        # Member elements
        member_group = QGroupBox("Member Elements")
        member_layout = QVBoxLayout(member_group)

        for elem_type in ["FLANGE", "GASKET"]:
            visual = ELEMENT_VISUALS[elem_type]
            btn = QPushButton(f"{visual.symbol} {visual.name}")
            btn.setToolTip(visual.description)
            btn.clicked.connect(lambda checked, t=elem_type: self.element_selected.emit(t))
            member_layout.addWidget(btn)

        layout.addWidget(member_group)

        # Contact elements - interface types
        contact_group = QGroupBox("Contact Elements")
        contact_layout = QVBoxLayout(contact_group)

        for elem_type in ["BEARING_HEAD", "BEARING_NUT", "FLANGE_FLANGE",
                          "WASHER_CONTACT", "GASKET_CONTACT", "GENERIC_CONTACT"]:
            visual = ELEMENT_VISUALS[elem_type]
            btn = QPushButton(f"{visual.symbol} {visual.name}")
            btn.setToolTip(visual.description)
            btn.clicked.connect(lambda checked, t=elem_type: self.element_selected.emit(t))
            contact_layout.addWidget(btn)

        layout.addWidget(contact_group)

        # Boundary
        boundary_group = QGroupBox("Boundary")
        boundary_layout = QVBoxLayout(boundary_group)

        visual = ELEMENT_VISUALS["GROUND"]
        btn = QPushButton(f"{visual.symbol} {visual.name}")
        btn.setToolTip("Fixed boundary condition")
        btn.clicked.connect(lambda: self.element_selected.emit("GROUND"))
        boundary_layout.addWidget(btn)

        layout.addWidget(boundary_group)

        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)


# =============================================================================


# =============================================================================
# HELP DIALOG — Professional tree-sidebar help viewer
# =============================================================================

class MSDBuilderHelpDialog(QDialog):
    """Professional help dialog with tree navigation sidebar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MSD Model Builder Beta - Help")
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowMinMaxButtonsHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.resize(1060, 760)
        self._build_ui()
        self._populate_tree()
        # Select first item
        first = self.tree.topLevelItem(0)
        if first and first.childCount():
            self.tree.setCurrentItem(first.child(0))
        elif first:
            self.tree.setCurrentItem(first)

    # ── CSS shared by all pages ──────────────────────────────────────
    def _css(self):
        return f"""<style>
body {{ color:{Theme.TEXT}; font-family:'Segoe UI',Arial,sans-serif;
       font-size:10pt; line-height:1.5; }}
h1 {{ color:{Theme.BLUE}; font-size:14pt;
     border-bottom:1px solid {Theme.SURFACE1}; padding-bottom:4px; margin-top:12px; }}
h2 {{ color:{Theme.BLUE}; font-size:12pt; margin-top:14px; }}
h3 {{ color:{Theme.PEACH}; font-size:10.5pt; margin-top:10px; }}
h4 {{ color:{Theme.MAUVE}; margin-top:8px; }}
code {{ background:{Theme.SURFACE0}; padding:1px 4px; border-radius:3px;
       font-family:Consolas,'Courier New',monospace; font-size:9.5pt; }}
pre {{ background:{Theme.SURFACE0}; padding:8px; border-radius:4px;
      font-family:Consolas,monospace; font-size:9pt; white-space:pre-wrap; }}
.ok {{ color:{Theme.GREEN}; font-weight:bold; }}
.warn {{ color:{Theme.YELLOW}; font-weight:bold; }}
.err {{ color:{Theme.RED}; font-weight:bold; }}
.tip {{ color:{Theme.TEAL}; }}
.ref {{ color:{Theme.LAVENDER}; font-style:italic; font-size:9pt; }}
table {{ border-collapse:collapse; margin:6px 0; width:100%; }}
th {{ background:{Theme.SURFACE0}; color:{Theme.BLUE}; padding:4px 8px;
     text-align:left; border:1px solid {Theme.SURFACE1}; }}
td {{ padding:4px 8px; border:1px solid {Theme.SURFACE1}; }}
ul,ol {{ margin-left:18px; }} li {{ margin-bottom:3px; }}
</style>"""

    # ── UI layout ────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter)

        # Left: tree
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setMinimumWidth(240)
        self.tree.setMaximumWidth(320)
        self.tree.setIndentation(16)
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background: {Theme.MANTLE};
                color: {Theme.TEXT};
                border: none;
                font-size: 10pt;
            }}
            QTreeWidget::item {{
                padding: 4px 6px;
            }}
            QTreeWidget::item:selected {{
                background: {Theme.SURFACE0};
                color: {Theme.BLUE};
            }}
            QTreeWidget::item:hover {{
                background: {Theme.SURFACE0};
            }}
            QTreeWidget::branch:has-children:closed {{
                image: none;
                border-image: none;
            }}
        """)
        splitter.addWidget(self.tree)

        # Right: content
        self.content = QTextEdit()
        self.content.setReadOnly(True)
        self.content.setStyleSheet(f"""
            QTextEdit {{
                background: {Theme.BASE};
                color: {Theme.TEXT};
                border: none;
                padding: 12px;
            }}
        """)
        splitter.addWidget(self.content)
        splitter.setSizes([260, 800])

        self.tree.currentItemChanged.connect(self._on_item_changed)

    # ── Tree population ──────────────────────────────────────────────
    def _populate_tree(self):
        self._pages = {}

        def _add(parent, key, label, html):
            item = QTreeWidgetItem(parent, [label])
            item.setData(0, Qt.ItemDataRole.UserRole, key)
            self._pages[key] = html
            return item

        # ── 1. Getting Started ───────────────────────────────────────
        cat = QTreeWidgetItem(self.tree, ["Getting Started"])
        cat.setExpanded(True)
        _add(cat, "gs_overview", "Overview", self._pg_gs_overview())
        _add(cat, "gs_first_model", "Your First Model", self._pg_gs_first_model())
        _add(cat, "gs_presets", "Using Presets", self._pg_gs_presets())
        _add(cat, "gs_workflow", "Validation Workflow", self._pg_gs_workflow())

        # ── 2. Elements ─────────────────────────────────────────────
        cat = QTreeWidgetItem(self.tree, ["Element Reference"])
        _add(cat, "el_ground", "GROUND (Boundary)", self._pg_el_ground())
        _add(cat, "el_bolt", "Bolt Components", self._pg_el_bolt())
        _add(cat, "el_clamped", "Clamped Members", self._pg_el_clamped())
        _add(cat, "el_contacts", "Contact Elements", self._pg_el_contacts())
        _add(cat, "el_materials", "Material Database", self._pg_el_materials())

        # ── 3. Topology ─────────────────────────────────────────────
        cat = QTreeWidgetItem(self.tree, ["Model Topology"])
        _add(cat, "tp_series", "Series Connections", self._pg_tp_series())
        _add(cat, "tp_parallel", "Parallel Connections", self._pg_tp_parallel())
        _add(cat, "tp_grid", "Grid Layout Rules", self._pg_tp_grid())
        _add(cat, "tp_drag", "Connection Ports & Drag", self._pg_tp_drag())

        # ── 4. Loading ───────────────────────────────────────────────
        cat = QTreeWidgetItem(self.tree, ["Loading & Preload"])
        _add(cat, "ld_types", "Load Types", self._pg_ld_types())
        _add(cat, "ld_params", "Loading Parameters", self._pg_ld_params())
        _add(cat, "ld_preload", "Preload Configuration", self._pg_ld_preload())
        _add(cat, "ld_friction", "Friction Settings", self._pg_ld_friction())
        _add(cat, "ld_arrows", "Force Arrows & Load Flow", self._pg_ld_arrows())

        # ── 5. Troubleshooting ───────────────────────────────────────
        cat = QTreeWidgetItem(self.tree, ["Troubleshooting"])
        cat.setExpanded(True)
        sub = QTreeWidgetItem(cat, ["Model Errors"])
        _add(sub, "ts_no_elem", "No Elements", self._pg_ts_no_elem())
        _add(sub, "ts_no_ground", "No Ground Element", self._pg_ts_no_ground())
        _add(sub, "ts_assembly", "Matrix Assembly Failed", self._pg_ts_assembly())

        sub = QTreeWidgetItem(cat, ["Mass Matrix [M]"])
        _add(sub, "ts_m_zero", "Zero / Negative Mass", self._pg_ts_m_zero())
        _add(sub, "ts_m_singular", "Singular Mass Matrix", self._pg_ts_m_singular())
        _add(sub, "ts_m_cond", "Ill-Conditioned [M]", self._pg_ts_m_cond())

        sub = QTreeWidgetItem(cat, ["Stiffness Matrix [K]"])
        _add(sub, "ts_k_neg", "Negative Eigenvalues", self._pg_ts_k_neg())
        _add(sub, "ts_k_semi", "Semi-Definite (Rigid Body)", self._pg_ts_k_semi())
        _add(sub, "ts_k_sing", "Singular [K]", self._pg_ts_k_sing())
        _add(sub, "ts_k_cond", "Ill-Conditioned [K]", self._pg_ts_k_cond())

        sub = QTreeWidgetItem(cat, ["Damping & Symmetry"])
        _add(sub, "ts_c_neg", "Negative Damping", self._pg_ts_c_neg())
        _add(sub, "ts_sym", "Matrix Asymmetry", self._pg_ts_sym())

        sub = QTreeWidgetItem(cat, ["Solver Checks"])
        _add(sub, "ts_keff", "K_eff Singular", self._pg_ts_keff())
        _add(sub, "ts_par", "Parallel Group Warnings", self._pg_ts_par())

        sub = QTreeWidgetItem(cat, ["Runtime Issues"])
        _add(sub, "ts_diverge", "Solver Divergence", self._pg_ts_diverge())
        _add(sub, "ts_flat", "No Preload Loss", self._pg_ts_flat())
        _add(sub, "ts_slow", "Slow / NaN Results", self._pg_ts_slow())

        # ── 6. Theory ────────────────────────────────────────────────
        cat = QTreeWidgetItem(self.tree, ["Theory & Equations"])
        _add(cat, "th_eom", "Equation of Motion", self._pg_th_eom())
        _add(cat, "th_assembly", "Matrix Assembly", self._pg_th_assembly())
        _add(cat, "th_junker", "Junker Loosening", self._pg_th_junker())
        _add(cat, "th_selflock", "Self-Locking Condition", self._pg_th_selflock())
        _add(cat, "th_thread", "Thread Load Distribution", self._pg_th_thread())
        _add(cat, "th_friction", "Friction Models", self._pg_th_friction())
        _add(cat, "th_preload_loss", "Preload Loss Mechanisms", self._pg_th_preload_loss())
        _add(cat, "th_integrators", "Time Integration", self._pg_th_integrators())
        _add(cat, "th_vdi", "VDI 2230 Standard", self._pg_th_vdi())

        # ── 7. References ────────────────────────────────────────────
        cat = QTreeWidgetItem(self.tree, ["References"])
        _add(cat, "ref_pubs", "Key Publications", self._pg_ref_pubs())
        _add(cat, "ref_stds", "Standards", self._pg_ref_stds())

        # ── 8. Shortcuts ─────────────────────────────────────────────
        cat = QTreeWidgetItem(self.tree, ["Keyboard & Mouse"])
        _add(cat, "kb_view", "View Controls", self._pg_kb_view())
        _add(cat, "kb_panels", "Panel Visibility", self._pg_kb_panels())
        _add(cat, "kb_elem", "Element Operations", self._pg_kb_elem())
        _add(cat, "kb_mouse", "Mouse Interactions", self._pg_kb_mouse())

    def _on_item_changed(self, current, _prev):
        if current is None:
            return
        key = current.data(0, Qt.ItemDataRole.UserRole)
        if key and key in self._pages:
            self.content.setHtml(self._css() + self._pages[key])

    # =================================================================
    #  PAGE CONTENT METHODS  — Getting Started
    # =================================================================
    def _pg_gs_overview(self):
        return """
<h1>MSD Model Builder Beta - Overview</h1>
<p>The MSD Model Builder is a visual editor for creating <b>Mass-Spring-Damper</b>
models of bolted joints. Each physical component (bolt head, shank, flange, gasket,
etc.) is represented as a lumped mass with axial stiffness and viscous damping.</p>
<p>The builder has three panels:</p>
<ul>
<li><b>Element Palette</b> (left) — element types and presets to drag onto the schematic</li>
<li><b>Schematic View</b> (center) — grid-based visual layout of your model</li>
<li><b>Property Inspector</b> (right) — edit element properties, loading, friction</li>
</ul>
<p>The model is exported as assembled [M], [K], [C] matrices and a force vector
{F} to the Solver Tab for time-domain loosening analysis.</p>
"""

    def _pg_gs_first_model(self):
        return """
<h1>Creating Your First Model</h1>
<ol>
<li>Click a <b>Preset</b> in the Element Palette (e.g. "Single Bolt" or "Flanged Joint").</li>
<li>The schematic populates with a standard element chain.</li>
<li>Click any element to inspect / edit its properties on the right panel.</li>
<li>Set <b>Loading</b> parameters: preload (70% yield), transverse force, frequency, cycles.</li>
<li>Click <b>Recalculate All</b> to auto-compute k, c, m from geometry and material.</li>
<li>Click <b>Validate</b> — fix any errors shown in the message box.</li>
<li>Click <b>>> Solver</b> to send the model to the Solver Tab and run the analysis.</li>
</ol>
<h2>Typical Element Order (Top to Bottom)</h2>
<pre>Row 0: GROUND        (fixed boundary — always required)
Row 1: HEAD          (bolt head)
Row 2: WASHER        (optional, under head)
Row 3: FLANGE        (upper clamped member)
Row 4: GASKET        (optional, seal element)
Row 5: FLANGE        (lower clamped member)
Row 6: WASHER        (optional, under nut)
Row 7: SHANK         (bolt shank)
Row 8: NUT           (retaining nut — thread engagement modeled here)</pre>
"""

    def _pg_gs_presets(self):
        return """
<h1>Using Presets</h1>
<table>
<tr><th>Preset</th><th>Elements</th><th>Use Case</th></tr>
<tr><td><b>Single Bolt</b></td><td>GROUND + HEAD + SHANK + NUT</td>
    <td>Minimal bolt, 4 DOF, fast analysis</td></tr>
<tr><td><b>Flanged Joint</b></td><td>GROUND + HEAD + SHANK + FLANGE + FLANGE + NUT</td>
    <td>Complete joint with clamped members</td></tr>
<tr><td><b>Junker Test</b></td><td>Standard DIN 65151 configuration</td>
    <td>Transverse vibration loosening test</td></tr>
</table>
<p>After loading a preset, customize element properties as needed. The preset
sets reasonable default values for geometry, material, and MSD parameters.</p>
"""

    def _pg_gs_workflow(self):
        return """
<h1>Validation Workflow</h1>
<ol>
<li><b>Build</b> — Place elements on the schematic and configure properties.</li>
<li><b>Recalculate All</b> — Auto-compute k, c, m from geometry and material.</li>
<li><b>Validate</b> — Runs 13 checks on the model. Results appear in a dialog.</li>
<li><b>Fix</b> — Resolve any <span class="err">ERRORS</span> (mandatory) and
    <span class="warn">WARNINGS</span> (recommended). See Troubleshooting section.</li>
<li><b>Export / >> Solver</b> — Send validated model to the Solver Tab.</li>
</ol>
<h2>The 13 Validation Checks</h2>
<table>
<tr><th>#</th><th>Check</th><th>Severity</th></tr>
<tr><td>1</td><td>Minimum element count</td><td>ERROR</td></tr>
<tr><td>2</td><td>Ground element presence</td><td>WARNING</td></tr>
<tr><td>3</td><td>Per-element k, m, c, geometry</td><td>WARNING / ERROR</td></tr>
<tr><td>4</td><td>Matrix assembly success</td><td>ERROR</td></tr>
<tr><td>5</td><td>Mass diagonal (negative / zero)</td><td>WARNING / ERROR</td></tr>
<tr><td>6</td><td>Mass matrix invertibility</td><td>ERROR</td></tr>
<tr><td>7</td><td>Stiffness positive-definiteness</td><td>ERROR / WARNING</td></tr>
<tr><td>8</td><td>Stiffness invertibility</td><td>WARNING</td></tr>
<tr><td>9</td><td>Damping matrix (negative entries)</td><td>WARNING</td></tr>
<tr><td>10</td><td>Matrix symmetry ([M], [K], [C])</td><td>WARNING</td></tr>
<tr><td>11</td><td>Effective stiffness K_eff (Newmark)</td><td>ERROR</td></tr>
<tr><td>12</td><td>Condition number</td><td>WARNING</td></tr>
<tr><td>13</td><td>Parallel group validation</td><td>WARNING</td></tr>
</table>
"""

    # =================================================================
    #  PAGE CONTENT METHODS  — Element Reference
    # =================================================================
    def _pg_el_ground(self):
        return """
<h1>GROUND — Fixed Boundary</h1>
<p>The GROUND element represents the rigid support / reaction boundary of the
bolted joint. It must be placed at <b>row 0</b> (top of the chain).</p>
<h2>Properties</h2>
<table>
<tr><th>Property</th><th>Typical Value</th><th>Notes</th></tr>
<tr><td>k (stiffness)</td><td>1 x 10<sup>12</sup> N/m</td>
    <td>Very high — acts as rigid wall</td></tr>
<tr><td>m (mass)</td><td>0.01 kg</td>
    <td>Small fictitious mass (required for [M] invertibility)</td></tr>
<tr><td>c (damping)</td><td>100 N-s/m</td><td>Small value</td></tr>
</table>
<h2>Why Is GROUND Required?</h2>
<p>Without a fixed boundary, the stiffness matrix [K] has a zero eigenvalue
(rigid-body mode). This means the entire system can translate freely with no
restoring force — the static solver fails and the dynamic solver gives
meaningless results.</p>
<p class="ref">Bickford (2008), Ch. 2: "The bolted joint always reacts against
a fixed structure."</p>
"""

    def _pg_el_bolt(self):
        return f"""
<h1>Bolt Components</h1>
<h2>HEAD</h2>
<p>The bolt head (hex, socket, etc.). Its stiffness represents the compliance
of the head–bearing surface region.</p>
<table>
<tr><th>Formula</th><th>Value</th></tr>
<tr><td>k<sub>head</sub> = 0.5 x E x d</td><td>VDI 2230 approximation</td></tr>
<tr><td>m = &rho; x V<sub>head</sub></td><td>Hex head volume</td></tr>
</table>

<h2>SHANK</h2>
<p>The unthreaded portion of the bolt.</p>
<table>
<tr><th>Formula</th><th>Notes</th></tr>
<tr><td>k = E x A / L</td><td>A = &pi;d&sup2;/4 (full cross-section)</td></tr>
<tr><td>m = &rho; x A x L</td><td>Cylindrical mass</td></tr>
</table>

<h2>NUT</h2>
<p>The retaining nut. Similar stiffness model to HEAD.</p>
<table>
<tr><th>Formula</th><th>Notes</th></tr>
<tr><td>k = 0.5 x E x d</td><td>Same as head approximation</td></tr>
<tr><td>Must have ThreadContact</td><td>In full contact model</td></tr>
</table>
"""

    def _pg_el_clamped(self):
        return """
<h1>Clamped Members</h1>
<h2>FLANGE</h2>
<p>Clamped plate or flange member. The effective stiffness uses Rotscher's
compression cone model.</p>
<table>
<tr><th>Formula</th><th>Notes</th></tr>
<tr><td>k = E x A<sub>eff</sub> / L</td>
    <td>A<sub>eff</sub> from Rotscher's cone (VDI 2230 sect. 5.2)</td></tr>
<tr><td>Cone half-angle</td><td>30 deg typical for steel-on-steel</td></tr>
</table>

<h2>WASHER</h2>
<p>Flat, spring, or Belleville washer. Distributes bearing load.</p>
<table>
<tr><th>Type</th><th>k Range</th><th>Behavior</th></tr>
<tr><td>Flat</td><td>10<sup>8</sup>–10<sup>9</sup> N/m</td><td>Linear</td></tr>
<tr><td>Spring (lock)</td><td>10<sup>6</sup>–10<sup>8</sup> N/m</td><td>Linear, lower k</td></tr>
<tr><td>Belleville</td><td>Variable</td><td>Nonlinear k(delta)</td></tr>
<tr><td>Nord-Lock</td><td>10<sup>8</sup> N/m</td><td>Wedge-locking action</td></tr>
</table>

<h2>GASKET</h2>
<p>Seal element at the flange interface. Much softer than metal.</p>
<table>
<tr><th>Type</th><th>k Range</th><th>Notes</th></tr>
<tr><td>Spiral Wound</td><td>10<sup>6</sup>–10<sup>8</sup> N/m</td><td>Most common in piping</td></tr>
<tr><td>RTJ (Ring Type)</td><td>10<sup>8</sup>–10<sup>9</sup> N/m</td><td>Metal-to-metal</td></tr>
<tr><td>Sheet</td><td>10<sup>5</sup>–10<sup>7</sup> N/m</td><td>Softest, most creep</td></tr>
<tr><td>Kammprofile</td><td>10<sup>7</sup>–10<sup>8</sup> N/m</td><td>Grooved metal core</td></tr>
</table>
<p>Gaskets have significant creep — preload decays logarithmically over time.</p>
"""

    def _pg_el_contacts(self):
        return """
<h1>Contact Elements</h1>
<p>Contacts represent mechanical interfaces between components. They contribute
stiffness to [K], damping to [C], and tribological forces to {F}.</p>

<h2>CONTACT (Generic)</h2>
<p>A general surface-to-surface contact. Use for bearing surfaces, washer
interfaces, flange-flange joints.</p>

<h2>BEARING_HEAD / BEARING_NUT</h2>
<p>Bearing surface contacts at the bolt head or nut face. Their friction torque
<b>resists</b> loosening:</p>
<pre>T_bearing = mu_b x F_p x r_eff
r_eff = (d_w + d_hole) / 4</pre>

<h2>Thread Contact (Stud–Nut)</h2>
<p>The thread interface between stud and nut. Models n parallel threads with
load distribution. The helix angle creates axial-torsional coupling that
<b>drives</b> loosening:</p>
<pre>T_helix = F_p x d2/2 x tan(lambda)</pre>
<p>Available load distribution models: Equal, Linear, Power, Exponential,
Yamamoto. See Theory > Thread Load Distribution.</p>
"""

    def _pg_el_materials(self):
        return """
<h1>Material Database</h1>
<table>
<tr><th>Material</th><th>Standard</th><th>S<sub>y</sub> (MPa)</th>
    <th>S<sub>u</sub> (MPa)</th><th>E (GPa)</th><th>Application</th></tr>
<tr><td>A193 B7</td><td>ASTM</td><td>720</td><td>860</td><td>205</td>
    <td>High-temp bolting (to 450 C)</td></tr>
<tr><td>A320 L7</td><td>ASTM</td><td>720</td><td>860</td><td>205</td>
    <td>Low-temp bolting (to -100 C)</td></tr>
<tr><td>ISO 898 8.8</td><td>ISO</td><td>640</td><td>800</td><td>205</td>
    <td>General structural</td></tr>
<tr><td>ISO 898 10.9</td><td>ISO</td><td>940</td><td>1040</td><td>205</td>
    <td>High-strength structural</td></tr>
<tr><td>ISO 898 12.9</td><td>ISO</td><td>1100</td><td>1220</td><td>205</td>
    <td>Highest strength class</td></tr>
<tr><td>A105</td><td>ASTM</td><td>250</td><td>485</td><td>200</td>
    <td>Flanges, fittings</td></tr>
<tr><td>SA-516 Gr.70</td><td>ASME</td><td>260</td><td>485</td><td>200</td>
    <td>Pressure vessel plate</td></tr>
</table>
<p class="ref">Values from ASTM A193/A320, ISO 898-1, ASME SA-516.</p>
"""

    # =================================================================
    #  PAGE CONTENT METHODS  — Topology
    # =================================================================
    def _pg_tp_series(self):
        return """
<h1>Series Connections</h1>
<p>Elements in <b>different rows</b> are connected in series. They share no DOF
— each has its own mass and connects to the next through a spring–damper.</p>
<h2>Equivalent Stiffness</h2>
<pre>1/k_total = 1/k_1 + 1/k_2 + ... + 1/k_n</pre>
<p>Series stiffness is always <b>less than</b> the weakest element. This is
the standard bolt model: head, shank, thread, nut in series.</p>
<h2>Matrix Pattern</h2>
<pre>[K] is tridiagonal:
       DOF_i      DOF_i+1
 i  [ +k_i+k_{i-1}   -k_i     ]
i+1 [    -k_i     +k_i+k_{i+1} ]</pre>
"""

    def _pg_tp_parallel(self):
        return """
<h1>Parallel Connections</h1>
<p>Elements in the <b>same row</b> are connected in parallel. They share the
same top and bottom nodes (DOFs), so their stiffnesses add:</p>
<pre>k_total = k_1 + k_2 + ... + k_n</pre>
<h2>When to Use Parallel</h2>
<ul>
<li><b>Thread fillets</b> — each engaged thread carries a fraction of load</li>
<li><b>Multi-bolt joints</b> — N bolts sharing the clamping load</li>
<li><b>Shank + thread</b> — partial engagement (threaded and unthreaded in
    parallel over the same length)</li>
</ul>
<h2>How to Create Parallel</h2>
<ul>
<li>Drag two elements to the same row, or</li>
<li>Select two elements and click <b>Parallel</b> button, or</li>
<li>Drag from one element's bottom port to another</li>
</ul>
"""

    def _pg_tp_grid(self):
        return """
<h1>Grid Layout Rules</h1>
<ul>
<li><b>Same row = parallel</b> (stiffnesses add at shared DOF)</li>
<li><b>Different rows = series</b> (tridiagonal [K] matrix)</li>
<li><b>Row 0 = GROUND</b> (fixed boundary, always first)</li>
<li>Elements snap to grid cells when placed or dragged</li>
<li>Rows are numbered top-to-bottom (0, 1, 2, ...)</li>
<li>Columns within a row are numbered left-to-right (0, 1, 2, ...)</li>
</ul>
<h2>Grid Cell Size</h2>
<p>Cell width and height are DPI-aware and scale with screen resolution.
Each element occupies exactly one grid cell.</p>
"""

    def _pg_tp_drag(self):
        return """
<h1>Connection Ports & Drag</h1>
<p>Each element has small <b>connection ports</b> (circles) at its top and bottom
edges. These appear on hover.</p>
<h2>How Drag-Wiring Works</h2>
<ol>
<li>Hover over an element — top and bottom ports appear.</li>
<li>Click and drag from a port — a dashed blue arrow follows the cursor.</li>
<li>Drop on another element:</li>
<ul>
<li><b>From bottom port</b> — target moves to the row below (series)</li>
<li><b>Same-row drop</b> — target moves to same row (parallel)</li>
</ul>
</ol>
<p>After the drop, the grid is compacted and connections are rebuilt.</p>
"""

    # =================================================================
    #  PAGE CONTENT METHODS  — Loading & Preload
    # =================================================================
    def _pg_ld_types(self):
        return """
<h1>Load Types</h1>
<table>
<tr><th>Type</th><th>Description</th><th>Primary Driver</th></tr>
<tr><td><b>TRANSVERSE</b></td><td>Cyclic shear at joint interface</td>
    <td>Junker loosening — most common</td></tr>
<tr><td><b>AXIAL</b></td><td>Cyclic tension/compression on bolt axis</td>
    <td>Fatigue, preload variation</td></tr>
<tr><td><b>COMBINED</b></td><td>Axial + transverse simultaneously</td>
    <td>Real-world multiaxial loading</td></tr>
<tr><td><b>TORSIONAL</b></td><td>Applied torque cycling</td>
    <td>Direct loosening torque, equipment vibration</td></tr>
<tr><td><b>BENDING</b></td><td>Bending moment at joint</td>
    <td>Non-uniform bolt loading</td></tr>
</table>
<h2>Which Type to Use?</h2>
<p>For self-loosening analysis, <b>TRANSVERSE</b> is the primary choice —
Junker (1969) showed this is the dominant loosening mechanism. Use COMBINED for
more realistic loading scenarios.</p>
"""

    def _pg_ld_params(self):
        return """
<h1>Loading Parameters</h1>
<p>All set in the Property Inspector (right panel), Loading section.</p>
<table>
<tr><th>Parameter</th><th>Unit</th><th>Description</th></tr>
<tr><td>F<sub>transverse</sub></td><td>N</td>
    <td>Transverse shear force amplitude. Auto-converts to/from displacement.</td></tr>
<tr><td>delta (displacement)</td><td>mm</td>
    <td>Transverse displacement amplitude = F / k_trans.</td></tr>
<tr><td>Frequency</td><td>Hz</td>
    <td>Loading frequency. 12.5 Hz = Junker test (DIN 65151).</td></tr>
<tr><td>Cycles</td><td>-</td>
    <td>Number of loading cycles. 1000-5000 typical.</td></tr>
<tr><td>F<sub>external</sub></td><td>N</td>
    <td>External axial force (working load).</td></tr>
<tr><td>Torque</td><td>N-m</td><td>Applied torsional moment.</td></tr>
<tr><td>Delta T</td><td>deg C</td><td>Temperature change for thermal effects.</td></tr>
</table>
<h2>Transverse Force / Displacement Auto-Conversion</h2>
<p>Changing force auto-updates displacement and vice versa, via:</p>
<pre>delta = F / k_transverse
F = delta x k_transverse</pre>
"""

    def _pg_ld_preload(self):
        return """
<h1>Preload Configuration</h1>
<h2>% of Yield Mode (Recommended)</h2>
<p>Set the <b>% yield</b> slider (default 70%). The preload force is computed:</p>
<pre>F_preload = (% / 100) x A_s x S_y</pre>
<p>Where A<sub>s</sub> = tensile stress area, S<sub>y</sub> = material yield strength.</p>
<table>
<tr><th>Guideline</th><th>% Yield</th><th>Application</th></tr>
<tr><td>VDI 2230 (controlled)</td><td>90%</td><td>Precision torque wrench</td></tr>
<tr><td>General practice</td><td>70-75%</td><td>Standard industrial</td></tr>
<tr><td>Conservative</td><td>50-60%</td><td>Uncertainty, seismic</td></tr>
</table>

<h2>Direct Force Mode</h2>
<p>Toggle to "Force (N)" to enter the preload directly in Newtons.
The % yield display updates to show utilization.</p>

<h2>Effect on Loosening</h2>
<p>Higher preload = higher friction resistance = harder to loosen. But the
thread helix torque also increases with preload. The net effect depends on
the friction coefficient:</p>
<ul>
<li>High mu (> 0.15): higher preload always helps</li>
<li>Low mu (< 0.08): loosening rate is roughly independent of preload level</li>
</ul>
<p class="ref">Nassar & Housari (2007), "Effect of Thread Pitch and Initial
Tension on the Self-Loosening of Threaded Fasteners."</p>
"""

    def _pg_ld_friction(self):
        return """
<h1>Friction Settings</h1>
<table>
<tr><th>Parameter</th><th>Range</th><th>Description</th></tr>
<tr><td>mu initial</td><td>0.01 - 0.50</td><td>Initial friction coefficient</td></tr>
<tr><td>Lubricated</td><td>Yes / No</td><td>Reduces effective mu</td></tr>
<tr><td>Bolt diameter</td><td>4 - 100 mm</td><td>For thread geometry lookup</td></tr>
<tr><td>Pitch</td><td>0.5 - 10 mm</td><td>Auto-populated from diameter</td></tr>
</table>
<h2>Typical Friction Coefficients</h2>
<table>
<tr><th>Surface Condition</th><th>mu_thread</th><th>mu_bearing</th></tr>
<tr><td>Dry (as-received)</td><td>0.12 - 0.18</td><td>0.12 - 0.18</td></tr>
<tr><td>Oiled</td><td>0.10 - 0.14</td><td>0.10 - 0.14</td></tr>
<tr><td>MoS2 lubricated</td><td>0.06 - 0.10</td><td>0.06 - 0.10</td></tr>
<tr><td>Waxed</td><td>0.08 - 0.12</td><td>0.08 - 0.12</td></tr>
<tr><td>Zinc-flake coated</td><td>0.09 - 0.14</td><td>0.09 - 0.14</td></tr>
<tr><td>Cadmium plated</td><td>0.06 - 0.10</td><td>0.06 - 0.10</td></tr>
</table>
<p class="ref">VDI 2230 Part 1 (2015), Table A7.</p>
"""

    def _pg_ld_arrows(self):
        return """
<h1>Force Arrows & Load Flow</h1>
<h2>Element Force Arrows</h2>
<p>Each element displays colored arrows indicating applied loads:</p>
<table>
<tr><th>Arrow Shape</th><th>Color</th><th>Load Type</th></tr>
<tr><td>Vertical straight</td><td>Green</td><td>Preload (axial)</td></tr>
<tr><td>Horizontal straight</td><td>Peach</td><td>Transverse</td></tr>
<tr><td>Curved arc</td><td>Mauve</td><td>Torque</td></tr>
<tr><td>L-shaped</td><td>Yellow</td><td>Bending</td></tr>
<tr><td>Vertical straight</td><td>Red</td><td>External axial</td></tr>
</table>

<h2>Load Flow Toggle</h2>
<p>Click <b>Toggle Load Flow</b> in the toolbar to show force propagation:</p>
<ul>
<li><b>Preload path</b> (green arrows) — axial force through the joint</li>
<li><b>Thread helix torque</b> (mauve) — drives loosening</li>
<li><b>Thread friction</b> (mauve) — partially resists</li>
<li><b>Bearing friction</b> (teal) — primary resistance to loosening</li>
<li><b>Net torque balance</b> — green (SELF-LOCKING) or red (LOOSENING RISK)</li>
<li><b>Clamping force</b> (sky) — at flange interfaces</li>
</ul>
"""

    # =================================================================
    #  PAGE CONTENT METHODS  — Troubleshooting
    # =================================================================
    def _pg_ts_no_elem(self):
        return """
<h1>ERROR: Model has no elements</h1>
<p><span class="err">Cause:</span> The schematic is empty — no elements placed.</p>
<p><span class="ok">Fix:</span> Add elements from the Element Palette, or load a
<b>Preset</b> (Single Bolt, Flanged Joint, Junker Test).</p>
"""

    def _pg_ts_no_ground(self):
        return """
<h1>WARNING: No ground element defined</h1>
<p><span class="warn">Cause:</span> The model lacks a fixed boundary. Without GROUND,
the stiffness matrix [K] has a zero eigenvalue (rigid-body mode) and the static
solver will fail.</p>
<h2>Theory</h2>
<p>A free-free system has rigid-body modes where all DOFs translate together.
In bolted joint analysis the base structure is always fixed; the GROUND provides
this constraint.</p>
<p class="ref">Bickford, J.H. (2008). <i>Introduction to the Design and Behavior
of Bolted Joints</i>, 4th ed., Ch. 2.</p>
<h2>Fix</h2>
<ul>
<li>Add a <b>GROUND</b> element at row 0.</li>
<li>Set k = 1e12 N/m, m = 0.01 kg.</li>
<li>The presets include GROUND automatically.</li>
</ul>
"""

    def _pg_ts_assembly(self):
        return """
<h1>ERROR: Matrix assembly failed</h1>
<p><span class="err">Cause:</span> An exception during [M], [K], [C] construction.</p>
<h2>Common Reasons</h2>
<ul>
<li><b>Topology error</b> — parallel elements reference invalid DOFs. Rearrange
    using the grid.</li>
<li><b>Size mismatch</b> — after editing, DOF count changed. Click
    <b>Recalculate All</b>.</li>
<li><b>Zero-element chain</b> — a row has no elements (gap in topology).</li>
</ul>
<h2>Fix</h2>
<ol>
<li>Click <b>Recalculate All</b>.</li>
<li>Ensure no row gaps exist (rows should be contiguous 0, 1, 2, ...).</li>
<li>Delete and re-add any problematic elements.</li>
</ol>
"""

    def _pg_ts_m_zero(self):
        return """
<h1>Zero or Negative Mass</h1>
<h2>WARNING: Zero mass at DOF(s) [...]</h2>
<p>One or more diagonal entries of [M] are zero. Implicit solvers
(Newmark, HHT-alpha) require [M] to be invertible.</p>

<h2>ERROR: Negative mass at DOF(s) [...]</h2>
<p>Negative mass has no physical meaning and causes complex eigenvalues.</p>

<p class="ref">Theory — The mass matrix must be positive definite (Bathe, <i>Finite
Element Procedures</i>, 2nd ed., 2014, sect. 9.2).</p>

<h2>Fix</h2>
<ul>
<li>DOF numbers map to elements: DOF 0 = first non-ground, DOF 1 = second, etc.</li>
<li>Select each flagged element and set <code>m > 0</code>.</li>
<li>For contacts/washers with negligible real mass, use 0.001 kg.</li>
<li>Use <b>Recalculate All</b> to auto-compute m = rho x V.</li>
</ul>
"""

    def _pg_ts_m_singular(self):
        return """
<h1>ERROR: Mass matrix [M] is singular</h1>
<p><span class="err">Cause:</span> The minimum diagonal entry of [M] is zero or
negative, so [M] cannot be inverted.</p>

<h2>Why This Matters</h2>
<p>The equation of motion requires:</p>
<pre>{x_ddot} = [M]^(-1) x ({F} - [C]{x_dot} - [K]{x})</pre>
<p>If [M] is singular, this inversion fails.</p>

<h2>Technical Note</h2>
<p>For lumped-mass (diagonal) matrices, the software checks
<code>min(diag(M)) > 0</code> instead of computing det(M). With many small
masses (contacts at 0.001 kg), det(M) numerically underflows even when the
matrix IS invertible.</p>
<p class="ref">Cook et al. (2001). <i>Concepts and Applications of Finite Element
Analysis</i>, 4th ed., Wiley, sect. 11.2.</p>

<h2>Fix</h2>
<ul>
<li>The error message names the elements with zero mass.</li>
<li>Select each and set m > 0.</li>
<li><b>Recalculate All</b> fills masses from geometry.</li>
</ul>
"""

    def _pg_ts_m_cond(self):
        return """
<h1>WARNING: Mass matrix [M] is ill-conditioned</h1>
<p><span class="warn">Cause:</span> cond([M]) > 10<sup>12</sup>. Large mass ratios
(e.g. 0.001 kg contact next to 50 kg flange) amplify numerical round-off.</p>
<h2>Fix</h2>
<ul>
<li>Increase small fictitious masses. Keep m_max / m_min < 10<sup>6</sup>.</li>
<li>If a contact has m = 0.001 kg and a flange has m = 50 kg, try m = 0.05 kg
    for the contact.</li>
</ul>
"""

    def _pg_ts_k_neg(self):
        return """
<h1>ERROR: Stiffness [K] has negative eigenvalues</h1>
<p><span class="err">Cause:</span> The system has negative strain energy in some
deformation mode — physically impossible for passive mechanical elements.</p>
<h2>Theory</h2>
<p>For a conservative system, the potential energy U = 1/2 {x}^T [K] {x}
must be >= 0 for all {x} != 0. Negative eigenvalues violate this.</p>
<p class="ref">Meirovitch, L. (2001). <i>Fundamentals of Vibrations</i>,
McGraw-Hill, sect. 4.5.</p>
<h2>Fix</h2>
<ul>
<li>Check no element has negative stiffness (k < 0).</li>
<li>Verify parallel/series topology: same row = parallel, different rows = series.</li>
<li>Check connection types are correct after rearranging.</li>
</ul>
"""

    def _pg_ts_k_semi(self):
        return """
<h1>WARNING: Stiffness [K] is semi-definite</h1>
<p><span class="warn">Cause:</span> At least one eigenvalue of [K] is very close to
zero (< 10<sup>-10</sup>). This indicates a <b>rigid-body mode</b> — the system
can translate freely without restoring force.</p>

<h2>Theory</h2>
<p>A semi-definite [K] means the system is not fully constrained. This occurs
when boundary conditions are missing. For bolted joints, the GROUND element
provides the fixed boundary.</p>
<p class="ref">VDI 2230 Part 1 (2015), sect. 3.2.</p>

<h2>Fix</h2>
<ul>
<li><b>Add a GROUND element</b> at row 0 if missing.</li>
<li>Ensure GROUND has very high stiffness (1e12 N/m).</li>
<li>If GROUND exists, check for <b>disconnected elements</b> — every element
    must be in a continuous chain from GROUND.</li>
<li>For parallel elements, ensure they share common nodes above and below.
    Two floating parallel elements create a zero eigenvalue.</li>
<li>Check that no element has k = 0.</li>
</ul>
"""

    def _pg_ts_k_sing(self):
        return """
<h1>WARNING: Stiffness [K] may be singular</h1>
<p><span class="warn">Cause:</span> The minimum eigenvalue of [K] is near zero.
The static solve [K]{x} = {F} may fail or give enormous displacements.</p>
<h2>Fix</h2>
<p>Same as "Semi-Definite" above:</p>
<ul>
<li>Ensure GROUND element at row 0 with k = 1e12 N/m.</li>
<li>All elements connected in continuous chain.</li>
<li>No element with k = 0.</li>
</ul>
"""

    def _pg_ts_k_cond(self):
        return """
<h1>WARNING: Stiffness [K] is ill-conditioned</h1>
<p><span class="warn">Cause:</span> cond([K]) > 10<sup>12</sup>. The ratio
lambda_max / lambda_min is very large, meaning small input perturbations cause
large output changes.</p>

<h2>Theory</h2>
<p>Floating-point arithmetic has ~15 significant digits (IEEE 754 double).
With cond(K) = 10<sup>n</sup>, you lose approximately n digits. At
cond > 10<sup>12</sup>, only ~3 digits remain reliable.</p>
<p class="ref">Golub & Van Loan (2013). <i>Matrix Computations</i>, 4th ed.,
Johns Hopkins, sect. 2.7.</p>

<h2>Fix</h2>
<ul>
<li><b>Reduce extreme stiffness ratios.</b> If GROUND has k = 10<sup>12</sup>
    and a gasket has k = 10<sup>3</sup>, try reducing GROUND to 10x the
    stiffest real element.</li>
<li><b>Use consistent units.</b> Mixing mm and m, or N and kN, causes
    artificial ill-conditioning.</li>
<li><b>Review element stiffnesses</b> for physical reasonableness.</li>
</ul>
"""

    def _pg_ts_c_neg(self):
        return """
<h1>WARNING: Negative damping at DOF(s)</h1>
<p><span class="warn">Cause:</span> One or more diagonal entries of [C] are negative.
This means the system <i>adds</i> energy instead of dissipating it, which can cause
runaway oscillations.</p>
<h2>Theory</h2>
<p>In passive systems, damping is always non-negative. Negative damping occurs only
in self-excited systems (flutter, brake squeal).</p>
<p class="ref">Inman, D.J. (2014). <i>Engineering Vibration</i>, 4th ed.,
Pearson, sect. 1.5.</p>
<h2>Fix</h2>
<ul>
<li>Select the element at the listed DOF and set c >= 0.</li>
<li>Typical: c = 2 x zeta x sqrt(k x m), with zeta = 0.01-0.05.</li>
</ul>
"""

    def _pg_ts_sym(self):
        return """
<h1>WARNING: Matrix is not symmetric</h1>
<p><span class="warn">Cause:</span> [M], [K], or [C] deviates from symmetry.
For standard MSD models, all three matrices should be symmetric.</p>
<h2>Theory</h2>
<p>Symmetry follows from Maxwell's reciprocal theorem. Asymmetric [K] can
appear with gyroscopic coupling (rotating machinery) or follower forces, but
these are not present in standard bolted joint models.</p>
<p class="ref">Geradin & Rixen (2015). <i>Mechanical Vibrations</i>, 3rd ed.,
Wiley, sect. 2.3.</p>
<h2>Fix</h2>
<ul>
<li>Try <b>Recalculate All</b> and re-validate.</li>
<li>If persistent, check for unusual element configurations.</li>
</ul>
"""

    def _pg_ts_keff(self):
        return """
<h1>ERROR: Effective stiffness K_eff is singular</h1>
<p><span class="err">Cause:</span> The Newmark integrator forms:</p>
<pre>K_eff = [K] + (gamma / beta*dt) [C] + (1 / beta*dt^2) [M]</pre>
<p>If this is singular, the time step cannot be solved.</p>

<h2>Theory</h2>
<p>Even if [K] is semi-definite, the mass and damping terms usually regularize
K_eff. A singular K_eff means [M] also has problems.</p>
<p class="ref">Bathe, K.J. (2014). <i>Finite Element Procedures</i>,
sect. 9.3.</p>

<h2>Fix</h2>
<ul>
<li>Fix mass and stiffness issues first (checks 5-8).</li>
<li>Ensure all elements have m > 0.</li>
<li>Reduce time step — smaller dt amplifies the mass contribution.</li>
</ul>
"""

    def _pg_ts_par(self):
        return """
<h1>WARNING: Parallel group has only 1 element</h1>
<p><span class="warn">Cause:</span> An element is marked as parallel but has no sibling.
Parallel groups need >= 2 elements.</p>
<h2>Fix</h2>
<ul>
<li>If the element should be in series, drag it to its own row.</li>
<li>If it should be parallel, drag a partner to the same row.</li>
<li>Use the <b>Parallel</b> button with two elements selected.</li>
</ul>
"""

    def _pg_ts_diverge(self):
        return """
<h1>Solver Divergence</h1>
<p><span class="err">Problem:</span> Results show very large or growing displacements.</p>
<h2>Theory</h2>
<p>The time step dt must be small enough for accuracy. For explicit schemes
(Central Difference), the CFL condition requires dt < 2 / omega_max. Implicit
schemes (Newmark, HHT) are unconditionally stable but suffer amplitude errors
at large dt / T ratios.</p>
<p class="ref">Hughes, T.J.R. (2000). <i>The Finite Element Method</i>,
Dover, sect. 9.2.</p>
<h2>Fix</h2>
<ul>
<li>Use <b>Suggest Timestep</b> in the Solver Tab.</li>
<li>Rule: dt < T_min / 20 where T_min = 2*pi / omega_max.</li>
<li>Balance k/m ratios — very high k with very low m creates
    high-frequency modes requiring tiny dt.</li>
<li>Add damping (c > 0) everywhere.</li>
<li>Switch to implicit solver (Newmark or HHT) if using explicit.</li>
</ul>
"""

    def _pg_ts_flat(self):
        return """
<h1>No Preload Loss (Flat Curve)</h1>
<p><span class="warn">Problem:</span> The preload remains constant — no loosening.</p>
<h2>Theory</h2>
<p>Junker (1969) showed that <b>transverse cyclic loading</b> is the primary
loosening driver. The mechanism requires simultaneous slip at <b>both</b> thread
and bearing surfaces. When both slip, the helix angle creates a net untwisting
torque that reduces preload.</p>
<p class="ref">Junker, G.H. (1969). "New Criteria for Self-Loosening of Fasteners
Under Vibration." <i>SAE 690055</i>.</p>
<h2>Fix</h2>
<ul>
<li><b>Apply transverse loading</b> — set F_trans or displacement in Loading section.</li>
<li><b>Lower friction</b> if mu > 0.20. Typical: 0.08-0.15 lubricated.</li>
<li><b>Check preload</b> — set to 50-80% yield.</li>
<li><b>Run enough cycles</b> — loosening may take 50-500 cycles to start.
    Use 1000-5000 for full decay.</li>
<li><b>Ensure thread and bearing contacts exist.</b></li>
</ul>
"""

    def _pg_ts_slow(self):
        return """
<h1>Slow Performance / NaN Results</h1>
<h2>Slow Solver</h2>
<ul>
<li>Reduce number of cycles or increase dt.</li>
<li>Use fewer elements (5-7 DOF model is usually sufficient).</li>
<li>The coupled loosening analyzer runs per-cycle, not per-step.</li>
</ul>
<h2>NaN or Inf in Results</h2>
<p><span class="err">Cause:</span> Overflow from extreme parameter ratios or
division by zero.</p>
<ul>
<li>Check for zero mass (division by zero in acceleration).</li>
<li>Reduce k/m ratios to below 10<sup>9</sup>.</li>
<li>Ensure damping is positive everywhere.</li>
<li>Switch to implicit solver (Newmark or HHT).</li>
</ul>
"""

    # =================================================================
    #  PAGE CONTENT METHODS  — Theory & Equations
    # =================================================================
    def _pg_th_eom(self):
        return """
<h1>Equation of Motion</h1>
<p>The bolted joint MSD system follows the second-order ODE:</p>
<pre>[M]{x_ddot} + [C]{x_dot} + [K]{x} = {F(t)}</pre>
<h2>Terms</h2>
<table>
<tr><th>Matrix</th><th>Physical Meaning</th><th>Structure</th></tr>
<tr><td>[M]</td><td>Inertia (mass)</td><td>Diagonal (lumped mass)</td></tr>
<tr><td>[C]</td><td>Energy dissipation (damping)</td><td>Similar to [K]</td></tr>
<tr><td>[K]</td><td>Restoring force (stiffness)</td><td>Tridiagonal (series) or banded</td></tr>
<tr><td>{F(t)}</td><td>External + tribological forces</td><td>Vector</td></tr>
</table>
<h2>Force Vector Decomposition</h2>
<pre>{F} = {F_external} + {F_friction} + {F_wear} + {F_preload}</pre>
<p><b>Friction and wear do NOT modify [K] or [C]</b> — they contribute only
through the force vector {F}.</p>
<p class="ref">Meirovitch (2001), Ch. 4-5; Bathe (2014), Ch. 9.</p>
"""

    def _pg_th_assembly(self):
        return """
<h1>Matrix Assembly</h1>
<h2>Series (Tridiagonal)</h2>
<p>For elements e1, e2, ... in series (different rows):</p>
<pre>       DOF_i         DOF_{i+1}
i   [ k_i + k_{i-1}    -k_i      ]
i+1 [    -k_i       k_i + k_{i+1} ]</pre>

<h2>Parallel (Stiffness Addition)</h2>
<p>For elements in the same row sharing DOFs:</p>
<pre>k_parallel = k_1 + k_2 + ... + k_n
m_parallel = m_1 + m_2 + ... + m_n
c_parallel = c_1 + c_2 + ... + c_n</pre>

<h2>Contact Contributions</h2>
<table>
<tr><th>Contact Type</th><th>[K]</th><th>[C]</th><th>{F}</th></tr>
<tr><td>Thread</td><td>k_thread + helix coupling</td><td>c_thread</td>
    <td>Loosening torque</td></tr>
<tr><td>Bearing</td><td>k_bearing</td><td>c_bearing</td>
    <td>Resisting friction torque</td></tr>
<tr><td>Gasket</td><td>k_tangent(delta) nonlinear</td><td>c_visco</td>
    <td>Creep force</td></tr>
</table>
"""

    def _pg_th_junker(self):
        return """
<h1>Junker Self-Loosening Mechanism</h1>
<p>Identified by Gerhard Junker in 1969. The key insight:
<b>transverse cyclic loading</b> causes complete slip at both thread and
bearing surfaces simultaneously, allowing the nut to rotate off.</p>
<h2>The Physics (Step by Step)</h2>
<ol>
<li><b>Transverse displacement</b> creates shear at bolt interfaces.</li>
<li>When shear > mu x F_N at <b>both</b> thread helix and bearing face,
    complete slip occurs.</li>
<li>During slip, the thread helix acts as an <b>inclined plane</b>:
<pre>T_helix = F_p x d2/2 x tan(lambda)</pre></li>
<li>This torque drives the nut in the <b>loosening direction</b>.</li>
<li>Each half-cycle produces a small rotation theta, reducing preload:
<pre>Delta_F = k_bolt x (p / 2*pi) x theta</pre></li>
</ol>
<h2>Critical Conditions for Loosening</h2>
<ul>
<li>Transverse loading must exceed friction at both interfaces</li>
<li>Thread helix torque must exceed bearing friction torque</li>
<li>Multiple cycles accumulate rotation</li>
</ul>
<p class="ref">Junker, G.H. (1969). "New Criteria for Self-Loosening of
Fasteners Under Vibration." <i>SAE Technical Paper 690055</i>.</p>
<p class="ref">Pai, N.G. & Hess, D.P. (2002). "Three-Dimensional FEA of
Threaded Fastener Loosening Due to Dynamic Shear Load." <i>J. Sound Vibration</i>,
253(3), 585-602.</p>
"""

    def _pg_th_selflock(self):
        return """
<h1>Self-Locking Condition</h1>
<p>The bolt is <b>self-locking</b> when bearing friction torque exceeds thread
helix torque:</p>
<pre>T_bearing > T_helix
mu_b x F_p x r_eff > F_p x d2/2 x tan(lambda)</pre>
<p>Simplifying (F_p cancels):</p>
<pre>mu_b x r_eff > d2/2 x tan(lambda)</pre>
<p>For standard M16x2 metric thread:</p>
<ul>
<li>lambda = arctan(p / (pi x d2)) = arctan(2 / (pi x 14.7)) = 2.48 deg</li>
<li>tan(lambda) = 0.0433</li>
<li>d2/2 = 7.35 mm</li>
<li>Self-locking needs: mu_b x r_eff > 0.318 mm</li>
<li>With r_eff = 11 mm: mu_b > 0.029 (almost always satisfied statically)</li>
</ul>
<p>However, during <b>complete transverse slip</b>, friction drops to kinetic
levels and the balance can tip toward loosening.</p>
"""

    def _pg_th_thread(self):
        return """
<h1>Thread Load Distribution</h1>
<p>Load is not evenly distributed across engaged threads. The first thread
(nearest bearing face) carries the most.</p>
<table>
<tr><th>Model</th><th>Formula</th><th>1st Thread (n=6)</th></tr>
<tr><td>Equal</td><td>phi_i = 1/n</td><td>16.7%</td></tr>
<tr><td>Linear</td><td>phi_i = 2(n-i+1) / n(n+1)</td><td>28.6%</td></tr>
<tr><td>Power (p=2)</td><td>phi_i = (n-i+1)^2 / sum</td><td>39.6%</td></tr>
<tr><td>Exponential</td><td>phi_i = e^(-lambda(i-1)) / sum</td><td>35-45%</td></tr>
<tr><td>Yamamoto</td><td>sinh-based</td><td>40-50%</td></tr>
</table>
<h2>Thread Geometry</h2>
<pre>Pitch diameter:  d2 = d - 0.6495 x p  (metric ISO)
Minor diameter:  d1 = d - 1.0825 x p
Stress area:     As = pi/4 x ((d2 + d1)/2)^2
Helix angle:     lambda = arctan(p / (pi x d2))</pre>
<p class="ref">Yamamoto, A. (1980). <i>The Theory and Computation of Threads
Connection</i>. Yokendo, Tokyo.</p>
<p class="ref">Kenny & Patterson (1985). "Load and Stress Distribution in Screw
Threads." <i>Experimental Mechanics</i>, 25(3), 208-213.</p>
"""

    def _pg_th_friction(self):
        return """
<h1>Friction Models</h1>
<h2>Thread Friction Torque</h2>
<pre>T_thread = F_p x d2/2 x
  [tan(lambda) + mu_t/cos(alpha/2)] /
  [1 - mu_t x tan(lambda)/cos(alpha/2)]</pre>
<p>Where alpha = 60 deg (flank angle, metric threads).</p>

<h2>Bearing Friction Torque</h2>
<pre>T_bearing = mu_b x F_p x r_eff
r_eff = (d_w + d_hole) / 4</pre>

<h2>Total Tightening Torque</h2>
<pre>T = T_thread + T_bearing + T_clamp</pre>
<p>Distribution: ~50% bearing, ~40% thread, ~10% clamping (bolt stretch).</p>

<h2>Available Friction Evolution Models</h2>
<table>
<tr><th>Model</th><th>Equation</th><th>Application</th></tr>
<tr><td>Constant</td><td>mu(t) = mu_0</td><td>Short tests</td></tr>
<tr><td>Exponential Decay</td><td>mu = mu_inf + (mu_0 - mu_inf) e^(-lambda N)</td>
    <td>Lubricated contacts</td></tr>
<tr><td>Stribeck</td><td>mu(v) = mu_k + (mu_s - mu_k) e^(-v/v_s)</td>
    <td>Velocity-dependent</td></tr>
</table>
<p class="ref">Bickford (2008), Ch. 7-8.</p>
"""

    def _pg_th_preload_loss(self):
        return """
<h1>Preload Loss Mechanisms</h1>
<p>Total: F_p(t) = F_p0 - Delta_F_total</p>
<table>
<tr><th>Mechanism</th><th>Model</th><th>Key Parameters</th></tr>
<tr><td><b>Rotational loosening</b></td>
    <td>Delta_F = k_bolt x p/(2pi) x theta</td>
    <td>Transverse force, mu, helix angle</td></tr>
<tr><td><b>Embedding</b></td>
    <td>Delta_F = k_sys x f_z x L x (1 - e^(-N/Nc))</td>
    <td>Surface roughness, interfaces</td></tr>
<tr><td><b>Gasket creep</b></td>
    <td>Delta_F = k_sys x d0 x Cr x log(t)</td>
    <td>Gasket type, temperature</td></tr>
<tr><td><b>Stress relaxation</b></td>
    <td>Delta_F = F0 x (1 - e^(-t/tau))</td>
    <td>Temperature, creep rate</td></tr>
<tr><td><b>Thermal</b></td>
    <td>Delta_F = k_sys x Delta_alpha x L x Delta_T</td>
    <td>CTE mismatch, temperature</td></tr>
<tr><td><b>Wear</b></td>
    <td>Delta_F = k_sys x K x F x s / (H x A)</td>
    <td>Wear coefficient, hardness</td></tr>
</table>
"""

    def _pg_th_integrators(self):
        return """
<h1>Time Integration Methods</h1>
<table>
<tr><th>Method</th><th>Type</th><th>Stability</th><th>Best For</th></tr>
<tr><td><b>Newmark-beta</b></td><td>Implicit</td>
    <td>Unconditionally stable (beta=0.25, gamma=0.5)</td>
    <td>General purpose (default)</td></tr>
<tr><td><b>HHT-alpha</b></td><td>Implicit</td>
    <td>Unconditionally stable, numerical dissipation</td>
    <td>Filtering high-frequency noise</td></tr>
<tr><td><b>Central Difference</b></td><td>Explicit</td>
    <td>dt < 2/omega_max (CFL)</td>
    <td>Short-duration impact</td></tr>
<tr><td><b>RK4</b></td><td>Explicit</td>
    <td>Conditionally stable</td>
    <td>High accuracy, smooth forcing</td></tr>
</table>
<h2>Newmark Parameters</h2>
<pre>beta = 0.25, gamma = 0.5   (average acceleration, unconditionally stable)
beta = 1/6, gamma = 0.5     (linear acceleration, conditionally stable)</pre>
<h2>Time Step Selection</h2>
<pre>dt <= T_min / 20   where T_min = 2*pi / omega_max
omega_max = sqrt(max eigenvalue of [M]^(-1) [K])</pre>
<p class="ref">Bathe (2014), Ch. 9; Hilber, Hughes & Taylor (1977).</p>
"""

    def _pg_th_vdi(self):
        return """
<h1>VDI 2230 Standard</h1>
<p>VDI 2230 Part 1 (2015) is the primary European standard for high-strength
bolted joints.</p>
<h2>Key Concepts</h2>
<ul>
<li><b>Load introduction factor (n)</b>: fraction of external force that changes
    bolt load. n = 0 (at bearing face) to 1 (at clamping interface).</li>
<li><b>Stiffness ratio (Phi)</b>:
    <code>Phi = k_bolt / (k_bolt + k_clamp)</code>.
    Lower Phi = bolt sees less external load.</li>
<li><b>Safety factors</b>: against yielding (S > 1.0), against slip, against fatigue.</li>
</ul>
<h2>VDI Tightening Guidelines</h2>
<table>
<tr><th>Tightening Method</th><th>Scatter (alpha_A)</th><th>Typical % Yield</th></tr>
<tr><td>Torque wrench</td><td>1.4 - 1.8</td><td>70%</td></tr>
<tr><td>Yield-point controlled</td><td>1.0 - 1.1</td><td>90%</td></tr>
<tr><td>Angle-controlled</td><td>1.1 - 1.3</td><td>85%</td></tr>
<tr><td>Hydraulic tensioning</td><td>1.05 - 1.2</td><td>80%</td></tr>
</table>
<p class="ref">VDI 2230 Part 1 (2015). "Systematic Calculation of Highly
Stressed Bolted Joints."</p>
"""

    # =================================================================
    #  PAGE CONTENT METHODS  — References
    # =================================================================
    def _pg_ref_pubs(self):
        return """
<h1>Key Publications</h1>
<table>
<tr><th>Author</th><th>Title</th><th>Year</th><th>Topic</th></tr>
<tr><td>Junker, G.H.</td><td>New Criteria for Self-Loosening of Fasteners
    Under Vibration</td><td>1969</td><td>Transverse loosening</td></tr>
<tr><td>Bickford, J.H.</td><td>Introduction to the Design and Behavior of
    Bolted Joints, 4th ed.</td><td>2008</td><td>Comprehensive bolt design</td></tr>
<tr><td>Pai, N.G. & Hess, D.P.</td><td>Three-Dimensional FEA of Threaded
    Fastener Loosening</td><td>2002</td><td>FEA validation</td></tr>
<tr><td>Nassar, S.A. & Housari, B.A.</td><td>Effect of Thread Pitch and
    Initial Tension on Self-Loosening</td><td>2007</td><td>Pitch & preload</td></tr>
<tr><td>Izumi, S. et al.</td><td>Three-Dimensional FEA on Tightening and
    Loosening Mechanism</td><td>2005</td><td>3D FEA</td></tr>
<tr><td>Yamamoto, A.</td><td>The Theory and Computation of Threads
    Connection</td><td>1980</td><td>Thread load distribution</td></tr>
<tr><td>Bathe, K.J.</td><td>Finite Element Procedures, 2nd ed.</td>
    <td>2014</td><td>Time integration</td></tr>
<tr><td>Meirovitch, L.</td><td>Fundamentals of Vibrations</td><td>2001</td>
    <td>Structural dynamics</td></tr>
<tr><td>Inman, D.J.</td><td>Engineering Vibration, 4th ed.</td><td>2014</td>
    <td>Vibration fundamentals</td></tr>
<tr><td>Cook, R.D. et al.</td><td>Concepts and Applications of FEA, 4th ed.</td>
    <td>2001</td><td>Finite element basics</td></tr>
<tr><td>Golub, G.H. & Van Loan, C.F.</td><td>Matrix Computations, 4th ed.</td>
    <td>2013</td><td>Numerical linear algebra</td></tr>
<tr><td>Geradin, M. & Rixen, D.J.</td><td>Mechanical Vibrations, 3rd ed.</td>
    <td>2015</td><td>Structural dynamics</td></tr>
<tr><td>Hilber, H.M. et al.</td><td>Improved Numerical Dissipation for Time
    Integration</td><td>1977</td><td>HHT-alpha method</td></tr>
<tr><td>Hughes, T.J.R.</td><td>The Finite Element Method</td><td>2000</td>
    <td>FEM and stability</td></tr>
</table>
"""

    def _pg_ref_stds(self):
        return """
<h1>Standards</h1>
<table>
<tr><th>Standard</th><th>Title</th><th>Scope</th></tr>
<tr><td>VDI 2230 Part 1</td><td>Systematic Calculation of Highly Stressed
    Bolted Joints</td><td>Bolt sizing, safety factors</td></tr>
<tr><td>DIN 65151</td><td>Vibration Test (Junker Test)</td>
    <td>Transverse vibration loosening</td></tr>
<tr><td>ISO 898-1</td><td>Mechanical Properties of Fasteners — Bolts</td>
    <td>Property classes 8.8, 10.9, 12.9</td></tr>
<tr><td>ASTM A193</td><td>Alloy-Steel Bolting for High Temperature</td>
    <td>Grade B7, B7M, B16</td></tr>
<tr><td>ASTM A320</td><td>Alloy-Steel Bolting for Low Temperature</td>
    <td>Grade L7, L7M, L43</td></tr>
<tr><td>ASME PCC-1</td><td>Guidelines for Pressure Boundary Bolted
    Flange Joint Assembly</td><td>Flange assembly procedures</td></tr>
<tr><td>EN 1591-1</td><td>Flanges and Their Joints — Design Rules</td>
    <td>European flange calculation</td></tr>
<tr><td>NACE MR0175</td><td>Sulfide Stress Cracking Resistant Materials</td>
    <td>Sour service material selection</td></tr>
</table>
"""

    # =================================================================
    #  PAGE CONTENT METHODS  — Keyboard & Mouse
    # =================================================================
    def _pg_kb_view(self):
        return """
<h1>View Controls</h1>
<table>
<tr><th>Shortcut</th><th>Action</th></tr>
<tr><td><code>Ctrl + 0</code></td><td>Fit all elements in view</td></tr>
<tr><td><code>Ctrl + +</code></td><td>Zoom in</td></tr>
<tr><td><code>Ctrl + -</code></td><td>Zoom out</td></tr>
<tr><td><code>Mouse Wheel</code></td><td>Zoom in / out</td></tr>
<tr><td><code>Middle Mouse Drag</code></td><td>Pan the view</td></tr>
</table>
"""

    def _pg_kb_panels(self):
        return """
<h1>Panel Visibility</h1>
<table>
<tr><th>Shortcut</th><th>Action</th></tr>
<tr><td><code>Ctrl + [</code></td><td>Toggle Element Palette (left)</td></tr>
<tr><td><code>Ctrl + ]</code></td><td>Toggle Property Inspector (right)</td></tr>
</table>
"""

    def _pg_kb_elem(self):
        return """
<h1>Element Operations</h1>
<table>
<tr><th>Shortcut / Action</th><th>Result</th></tr>
<tr><td><code>Delete</code></td><td>Delete selected element</td></tr>
<tr><td><code>F1</code></td><td>Show this Help dialog</td></tr>
<tr><td><code>Click element</code></td><td>Select and show properties</td></tr>
<tr><td><code>Ctrl + Click</code></td><td>Multi-select (for Series/Parallel)</td></tr>
<tr><td><code>Drag element</code></td><td>Move to new grid position</td></tr>
<tr><td><code>Right-click</code></td><td>Context menu (delete, duplicate, change type)</td></tr>
</table>
"""

    def _pg_kb_mouse(self):
        return """
<h1>Mouse Interactions</h1>
<table>
<tr><th>Action</th><th>Result</th></tr>
<tr><td>Hover element</td><td>Connection ports appear (top/bottom circles)</td></tr>
<tr><td>Drag from port</td><td>Draw connection arrow to rearrange topology</td></tr>
<tr><td>Drop on element</td><td>Rearrange: bottom port = series, same-row = parallel</td></tr>
<tr><td>Click palette item</td><td>Select element type, then click schematic to place</td></tr>
<tr><td>Double-click element</td><td>Focus Property Inspector on that element</td></tr>
</table>
"""


# MAIN WINDOW
# =============================================================================

class MSDBuilderWindow(QMainWindow):
    """Main MSD Model Builder Beta window."""

    model_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("MSD Model Builder Beta - Bolt Analysis Studio")

        # Undo / Redo stack (QUndoStack)
        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(200)

        # Get screen size for responsive layout
        self._setup_responsive_size()

        # Cached loading data from PropertyInspector
        self._cached_loading_data: Dict[str, Any] = {}

        self._setup_ui()
        self._setup_toolbar()
        self._setup_menubar()
        self._setup_statusbar()
        self._connect_signals()
        self._apply_theme()

        # Register for live theme updates
        Theme.register_callback(self._apply_theme)

    def closeEvent(self, event):
        """Confirm before closing the MSD Builder window."""
        reply = QMessageBox.question(
            self,
            "Close MSD Model Builder",
            "Are you sure you want to close the MSD Model Builder?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def _setup_responsive_size(self):
        """Setup window size based on screen resolution."""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geom = screen.availableGeometry()
            # Use 80% of screen size, with minimum bounds
            width = max(1000, min(int(screen_geom.width() * 0.8), 1600))
            height = max(600, min(int(screen_geom.height() * 0.8), 1000))
            self.resize(width, height)

            # Center on screen
            x = (screen_geom.width() - width) // 2
            y = (screen_geom.height() - height) // 2
            self.move(x, y)
        else:
            self.resize(1200, 700)

        self.setMinimumSize(900, 550)

    def _setup_ui(self):
        """Setup main UI."""
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(True)  # Allow collapsing

        # Store panel visibility states and sizes
        self._left_panel_visible = True
        self._right_panel_visible = True
        self._saved_sizes = None

        # Left - Palette (responsive width)
        self.palette = ElementPalette()
        self.palette.setMinimumWidth(150)
        self.palette.setMaximumWidth(280)
        self.palette.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        # Center - Schematic (takes remaining space)
        self.schematic = SchematicView()
        self.schematic.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # 3.16 — Minimap overlay (bottom-left corner of schematic)
        self._minimap = MinimapWidget(self.schematic, parent=self.schematic)
        self._minimap.move(4, self.schematic.height() - self._minimap.height() - 4)
        self._minimap.raise_()
        # Reposition on resize via resizeEvent override below
        self.schematic.resizeEvent = self._schematic_resize_event

        # Right - Inspector (responsive width)
        self.inspector = PropertyInspector()
        self.inspector.setMinimumWidth(240)
        self.inspector.setMaximumWidth(400)
        self.inspector.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        # Wire the shared undo/redo context so property edits and grid moves
        # made through the inspector / schematic land on the same QUndoStack.
        self.schematic.undo_stack = self.undo_stack
        self.inspector._schematic = self.schematic
        self.inspector._undo_stack = self.undo_stack

        self.splitter.addWidget(self.palette)
        self.splitter.addWidget(self.schematic)
        self.splitter.addWidget(self.inspector)

        # Set stretch factors: palette=1, schematic=4, inspector=2
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 4)
        self.splitter.setStretchFactor(2, 2)

        # Initial sizes based on window width
        total_width = self.width()
        self.splitter.setSizes([
            int(total_width * 0.15),
            int(total_width * 0.55),
            int(total_width * 0.30)
        ])

        main_layout.addWidget(self.splitter)

    def _setup_toolbar(self):
        """Create shared QActions and a compact quick-access toolbar.

        Most actions live in the menu bar (see _setup_menubar); the toolbar
        exposes only the highest-value items so nothing ever hides in overflow.
        """

        # --- Create shared QActions (used by both menu bar and toolbar) ---
        self.toggle_left_action = QAction("Toggle Palette", self)
        self.toggle_left_action.setCheckable(True)
        self.toggle_left_action.setChecked(True)
        self.toggle_left_action.setToolTip("Toggle Element Palette (Ctrl+[)")
        self.toggle_left_action.setShortcut("Ctrl+[")
        self.toggle_left_action.triggered.connect(self._toggle_left_panel)

        self.toggle_right_action = QAction("Toggle Inspector", self)
        self.toggle_right_action.setCheckable(True)
        self.toggle_right_action.setChecked(True)
        self.toggle_right_action.setToolTip("Toggle Property Inspector (Ctrl+])")
        self.toggle_right_action.setShortcut("Ctrl+]")
        self.toggle_right_action.triggered.connect(self._toggle_right_panel)

        self.undo_action = self.undo_stack.createUndoAction(self, "Undo")
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.setToolTip("Undo last action (Ctrl+Z)")

        self.redo_action = self.undo_stack.createRedoAction(self, "Redo")
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.setToolTip("Redo last undone action (Ctrl+Y)")

        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.setToolTip("Zoom In (Ctrl++)")
        self.zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        self.zoom_in_action.triggered.connect(lambda: self.schematic.scale(1.15, 1.15))

        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.setToolTip("Zoom Out (Ctrl+-)")
        self.zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        self.zoom_out_action.triggered.connect(lambda: self.schematic.scale(1/1.15, 1/1.15))

        self.fit_action = QAction("Fit to View", self)
        self.fit_action.setToolTip(
            "Fit to View (Ctrl+0)\n"
            "Zoom: Ctrl+Wheel  •  Middle-click + Wheel\n"
            "Pan: drag scrollbars or arrow keys")
        self.fit_action.setShortcut("Ctrl+0")
        self.fit_action.triggered.connect(self._fit_view)

        self.show_flow_action = QAction("Show Load Flow", self)
        self.show_flow_action.setCheckable(True)
        self.show_flow_action.setToolTip("Show load flow through model")
        self.show_flow_action.triggered.connect(self._toggle_load_flow)

        self.recalc_all_action = QAction("Recalculate All", self)
        self.recalc_all_action.setToolTip(
            "Recalculate k, c, m for ALL elements\n"
            "based on current geometry and materials"
        )
        self.recalc_all_action.triggered.connect(self._recalculate_all_elements)

        self.delete_all_action = QAction("Delete All", self)
        self.delete_all_action.setToolTip("Remove ALL elements, contacts, and overlays from the schematic")
        self.delete_all_action.triggered.connect(self._delete_all)

        self.matrix_action = QAction("Matrices [M][K][C]", self)
        self.matrix_action.setToolTip("View assembled [M], [K], [C] matrices")
        self.matrix_action.triggered.connect(self._show_matrix_viewer)

        self.validate_action = QAction("Validate Model", self)
        self.validate_action.setToolTip("Validate model configuration (F5)")
        self.validate_action.setShortcut("F5")
        self.validate_action.triggered.connect(self._validate_model)

        self.export_action = QAction("Export / Save Model…", self)
        self.export_action.setToolTip("Export model to file")
        self.export_action.setShortcut(QKeySequence.StandardKey.Save)
        self.export_action.triggered.connect(self._export_model)

        self.wizard_action = QAction("Joint Wizard…", self)
        self.wizard_action.setShortcut("Ctrl+J")
        self.wizard_action.setToolTip("Open the Flange Joint Wizard (Ctrl+J)")
        self.wizard_action.triggered.connect(self._show_wizard)

        self.toggle_grid_action = QAction("Toggle Grid", self)
        self.toggle_grid_action.setShortcut("Ctrl+G")
        self.toggle_grid_action.setToolTip("Show/hide background grid (Ctrl+G)")
        self.toggle_grid_action.triggered.connect(
            lambda: self.schematic.toggle_grid(not self.schematic._show_grid)
        )

        self.help_action = QAction("? Help", self)
        self.help_action.setToolTip("Common problems and troubleshooting (F1)")
        self.help_action.setShortcut("F1")
        self.help_action.triggered.connect(self._show_help)

        self.close_action = QAction("Close Builder", self)
        self.close_action.setShortcut("Ctrl+W")
        self.close_action.triggered.connect(self.close)

        # --- Build the compact toolbar (quick-access only) ---
        toolbar = QToolBar("Quick Access")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        # Case Studies — highest-value discoverable entry point
        self.case_studies_btn = QToolButton(self)
        self.case_studies_btn.setText("📁 Case Studies")
        self.case_studies_btn.setToolTip(
            "Load a pre-built case study (UFU lab trials + literature validation cases).\n"
            "Loads the .msd model and applies the loading preset in one step."
        )
        self.case_studies_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.case_studies_btn.setStyleSheet(
            f"QToolButton {{ font-weight: bold; color: {Theme.GREEN}; padding: 4px 10px; }}"
        )
        self._case_studies_menu = QMenu(self.case_studies_btn)
        self._populate_case_studies_menu(self._case_studies_menu)
        self.case_studies_btn.setMenu(self._case_studies_menu)
        toolbar.addWidget(self.case_studies_btn)

        toolbar.addSeparator()
        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)
        toolbar.addSeparator()
        toolbar.addAction(self.zoom_in_action)
        toolbar.addAction(self.zoom_out_action)
        toolbar.addAction(self.fit_action)
        toolbar.addSeparator()

        # Series / Parallel quick buttons (enabled contextually)
        self.series_btn = QPushButton("↕ Series")
        self.series_btn.setToolTip("Connect two selected elements in series (one after another)")
        self.series_btn.setEnabled(False)
        self.series_btn.clicked.connect(self._connect_series)
        toolbar.addWidget(self.series_btn)

        self.parallel_btn = QPushButton("↔ Parallel")
        self.parallel_btn.setToolTip("Connect two selected elements in parallel (same row)")
        self.parallel_btn.setEnabled(False)
        self.parallel_btn.clicked.connect(self._connect_parallel)
        toolbar.addWidget(self.parallel_btn)

        toolbar.addSeparator()
        toolbar.addAction(self.validate_action)
        toolbar.addAction(self.help_action)

    def _setup_menubar(self):
        """Build the menu bar with File / Edit / View / Tools / Help menus.

        All toolbar actions are also accessible here so nothing is hidden
        in toolbar overflow.
        """
        mb = self.menuBar()
        mb.clear()

        # File
        file_menu = mb.addMenu("&File")
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        file_menu.addAction(self.delete_all_action)
        file_menu.addSeparator()
        file_menu.addAction(self.close_action)

        # Edit
        edit_menu = mb.addMenu("&Edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.recalc_all_action)

        # View
        view_menu = mb.addMenu("&View")
        view_menu.addAction(self.toggle_left_action)
        view_menu.addAction(self.toggle_right_action)
        view_menu.addSeparator()
        view_menu.addAction(self.zoom_in_action)
        view_menu.addAction(self.zoom_out_action)
        view_menu.addAction(self.fit_action)
        view_menu.addSeparator()
        view_menu.addAction(self.toggle_grid_action)
        view_menu.addAction(self.show_flow_action)
        view_menu.addSeparator()
        view_menu.addAction(self.matrix_action)

        # Tools
        tools_menu = mb.addMenu("&Tools")
        tools_menu.addAction(self.validate_action)
        tools_menu.addAction(self.wizard_action)

        # Help
        help_menu = mb.addMenu("&Help")
        help_menu.addAction(self.help_action)

        # --- Shortcuts not tied to a menu entry ---
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(
            lambda: self.inspector.inspector_tabs.setCurrentIndex(1)
        )
        QShortcut(QKeySequence("Ctrl+K"), self).activated.connect(
            lambda: self.inspector.inspector_tabs.setCurrentIndex(2)
        )

    def _fit_view(self):
        """Fit schematic to view, then nudge zoom in slightly so content fills the viewport."""
        if self.schematic.elements:
            items_rect = QRectF()
            for item in self.schematic.elements.values():
                items_rect = items_rect.united(item.sceneBoundingRect())
            # Tight margin (10 px scene units) so content fills more of the viewport
            items_rect.adjust(-10, -10, 10, 10)
            target = items_rect
        else:
            target = self.schematic.sceneRect()

        self.schematic.resetTransform()
        self.schematic._zoom_factor = 1.0
        self.schematic.fitInView(target, Qt.AspectRatioMode.KeepAspectRatio)

        # KeepAspectRatio leaves dead space on whichever axis has the wrong ratio;
        # bump zoom up to ~95 % of the smaller dimension so the schematic feels full-size
        # but stops short of clipping.
        try:
            view_rect = self.schematic.viewport().rect()
            scene_rect = self.schematic.transform().mapRect(target)
            if scene_rect.width() > 0 and scene_rect.height() > 0:
                scale_x = view_rect.width() / scene_rect.width()
                scale_y = view_rect.height() / scene_rect.height()
                extra = min(scale_x, scale_y) * 0.95
                if 0.5 < extra < 5.0 and extra != 1.0:
                    self.schematic.scale(extra, extra)
                    self.schematic._zoom_factor *= extra
        except Exception:
            pass

    def _recalculate_all_elements(self):
        """
        Recalculate k, c, m for ALL elements in the model.

        Enhanced version with progress feedback and detailed statistics.
        """
        import math
        from PyQt6.QtWidgets import QProgressDialog

        # Get all element items (values from the dictionary)
        elements = list(self.schematic.elements.values())

        if not elements:
            QMessageBox.information(
                self, "No Elements",
                "Add elements to the schematic first."
            )
            return

        # Show confirmation dialog
        reply = QMessageBox.question(
            self, "Recalculate All Elements",
            f"Recalculate k, c, m for {len(elements)} elements?\n\n"
            "This will update based on current:\n"
            "• Geometry (length, diameter, area)\n"
            "• Material properties (E, ρ, ζ)\n\n"
            "Calculations:\n"
            "• Stiffness: k = EA/L\n"
            "• Mass: m = ρ × V\n"
            "• Damping: c = 2ζ√(km)\n\n"
            "Current values will be overwritten.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Create progress dialog
        progress = QProgressDialog(
            "Recalculating element properties...",
            "Cancel",
            0, len(elements),
            self
        )
        progress.setWindowTitle("Recalculation Progress")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)

        # Statistics
        count_updated = 0
        errors = []
        total_k_old = 0.0
        total_k_new = 0.0
        total_m_old = 0.0
        total_m_new = 0.0

        # Sync bolt geometry from Global Loading before recalculation
        loading_data = self.inspector.get_loading_data()
        bolt_dia = loading_data.get("bolt_diameter", 16.0)
        bolt_pitch = loading_data.get("pitch", 2.0)

        for element_item in elements:
            elem_data = element_item.element_data
            if elem_data.type in (ElementType.HEAD, ElementType.SHANK,
                                  ElementType.NUT):
                # Update bolt element geometry from global settings
                elem_data.geometry.diameter = bolt_dia
                elem_data.geometry.pitch = bolt_pitch
                # Reset derived dimensions so __post_init__ recalculates them
                elem_data.geometry.d2 = None
                elem_data.geometry.d1 = None
                elem_data.geometry.d3 = None
                elem_data.geometry.At = None
                elem_data.geometry.As = None
                elem_data.geometry.__post_init__()

                # Set proper head/nut dimensions if not explicitly set
                if elem_data.type == ElementType.HEAD:
                    if elem_data.geometry.head_diameter == 0:
                        elem_data.geometry.head_diameter = bolt_dia * 1.5
                    if elem_data.geometry.head_height == 0:
                        elem_data.geometry.head_height = bolt_dia * 0.7
                elif elem_data.type == ElementType.NUT:
                    if elem_data.geometry.head_diameter == 0:
                        elem_data.geometry.head_diameter = bolt_dia * 1.8
                    if elem_data.geometry.head_height == 0:
                        elem_data.geometry.head_height = bolt_dia * 0.8

        # Recalculate each element
        for idx, element_item in enumerate(elements):
            # Check for cancellation
            if progress.wasCanceled():
                QMessageBox.information(
                    self, "Cancelled",
                    f"Recalculation cancelled. {count_updated} elements updated."
                )
                return

            # Update progress
            progress.setValue(idx)
            elem_data = element_item.element_data
            progress.setLabelText(
                f"Processing {elem_data.type.value} #{elem_data.id}...\n"
                f"Updated: {count_updated}/{len(elements)}"
            )
            QApplication.processEvents()

            try:
                # Store old values
                k_old = elem_data.msd.k
                m_old = elem_data.msd.m
                total_k_old += k_old
                total_m_old += m_old

                # Enable auto-calculation
                elem_data.msd.auto_calculate_k = True
                elem_data.msd.auto_calculate_c = True
                elem_data.msd.auto_calculate_m = True

                # Recalculate
                elem_data.update_msd_parameters()

                # Get new values
                k_new = elem_data.msd.k
                m_new = elem_data.msd.m
                total_k_new += k_new
                total_m_new += m_new

                # Update visual element
                element_item.update_display()

                count_updated += 1

            except Exception as e:
                import traceback
                error_detail = f"{elem_data.type.value} #{elem_data.id}: {str(e)}"
                print(f"ERROR: {error_detail}")
                print(traceback.format_exc())
                errors.append(error_detail)

        # Close progress
        progress.setValue(len(elements))
        progress.close()

        # Update display
        self.schematic.update()
        self._update_status()

        # Show results
        results_msg = f"Successfully updated {count_updated} of {len(elements)} elements.\n\n"
        results_msg += "=== SUMMARY ===\n"
        results_msg += f"Total system stiffness change: {total_k_old/1e6:.1f} → {total_k_new/1e6:.1f} MN/m\n"
        results_msg += f"Total system mass change: {total_m_old:.3f} → {total_m_new:.3f} kg\n"

        if errors:
            error_msg = "\n".join(f"• {e}" for e in errors[:5])
            if len(errors) > 5:
                error_msg += f"\n... and {len(errors) - 5} more errors"

            QMessageBox.warning(
                self, "Recalculation Completed with Errors",
                f"{results_msg}\n=== ERRORS ===\n{error_msg}"
            )
        else:
            QMessageBox.information(
                self, "Recalculation Complete",
                results_msg + "\nAll properties recalculated successfully!"
            )

    def _show_matrix_viewer(self):
        """Show the matrix visualization dialog with live model update support (LOW-04)."""
        model = self.schematic.export_to_model()
        if model is None or model.n_elements == 0:
            QMessageBox.warning(self, "No Model", "Please add elements to the model first.")
            return

        try:
            from bolt_analysis_studio.gui.matrix_viewer import MatrixViewerDialog
            self._matrix_viewer_dialog = MatrixViewerDialog(model, self)
            # Connect model changes to live-refresh the force vector tab
            self.schematic.model_changed.connect(self._refresh_matrix_viewer_if_open)
            self._matrix_viewer_dialog.finished.connect(
                lambda: self.schematic.model_changed.disconnect(self._refresh_matrix_viewer_if_open)
            )
            self._matrix_viewer_dialog.exec()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open matrix viewer: {e}")

    def _refresh_matrix_viewer_if_open(self):
        """Refresh matrix viewer's force tab when model changes (LOW-04)."""
        dialog = getattr(self, '_matrix_viewer_dialog', None)
        if dialog is None or not dialog.isVisible():
            return
        try:
            model = self.schematic.export_to_model()
            if model is not None:
                dialog.refresh_from_model(model)
        except Exception:
            pass

    def _export_model(self):
        """Export model to file."""
        from PyQt6.QtWidgets import QFileDialog

        model = self.schematic.export_to_model()
        if model is None:
            QMessageBox.warning(self, "No Model", "Please add elements first.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Model", "model.msd",
            "MSD Model Files (*.msd);;JSON Files (*.json);;All Files (*)"
        )

        if filename:
            try:
                model.save(filename)
                QMessageBox.information(self, "Export", f"Model saved to {filename}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save: {e}")

    def _populate_case_studies_menu(self, menu: QMenu):
        """Populate the Case Studies popup menu with registered validation cases.

        Groups cases by ValidationSource; clicking a case loads its .msd model
        (if available) and sets the UFU preset combo for UFU cases.
        """
        try:
            from bolt_analysis_studio.core.validation_cases import (
                ValidationCaseManager, ValidationSource,
            )
        except Exception as e:
            act = menu.addAction(f"(validation cases unavailable: {e})")
            act.setEnabled(False)
            return

        cases = ValidationCaseManager.get_all_cases()
        by_src: Dict[str, List[Any]] = defaultdict(list)
        for c in cases:
            by_src[c.source.value].append(c)

        # UFU lab first, then alphabetical by source
        ufu_key = ValidationSource.UFU_LAB.value if hasattr(ValidationSource, 'UFU_LAB') else None
        ordered_keys = []
        if ufu_key and ufu_key in by_src:
            ordered_keys.append(ufu_key)
        ordered_keys += sorted(k for k in by_src.keys() if k != ufu_key)

        for src_name in ordered_keys:
            submenu = menu.addMenu(src_name)
            for case in by_src[src_name]:
                label = f"{case.name} — {case.bolt_size}, F₀={case.initial_preload_N:.0f} N"
                act = submenu.addAction(label)
                act.setToolTip(case.description or case.name)
                act.triggered.connect(lambda _checked=False, c=case: self._load_case_study(c))

    def _build_model_from_case(self, case) -> MSDModel:
        """Build an MSDModel from a ValidationCase that has no bundled .msd.

        Cases from the literature (Jiang/Junker/Nassar/Yang/...) ship only
        reference data, no geometry. We synthesise a transverse (Junker)
        joint sized to the case's bolt via the wizard's build_model, then
        override loading/friction with the case's measured values so the
        builder gets a populated, runnable model instead of staying empty.
        """
        from bolt_analysis_studio.gui.new_analysis_wizard import (
            AnalysisSpec, build_model,
        )
        spec = AnalysisSpec(
            project_name=case.name,
            joint_preset_id="single_shear",   # cases are transverse vibration
            bolt_diameter_mm=float(case.bolt_diameter_mm),
            pitch_mm=float(case.pitch_mm),
            preload_pct_yield=float(case.preload_percent_yield),
            loading_type="TRANSVERSE",
            delta_amplitude_mm=float(case.transverse_displacement_mm),
            F_amplitude_N=0.0,
            frequency_hz=float(case.frequency_Hz),
            n_cycles=int(case.n_cycles),
        )
        model = build_model(spec)
        model.name = case.name
        # Override computed values with the case's measured ones.
        model.mu_initial = float(case.mu_initial)
        model.lubricated = bool(case.lubricated)
        model.global_loading.F_preload = float(case.initial_preload_N)
        return model

    def _load_case_study(self, case):
        """Load a ValidationCase: parse its .msd file (or synthesise a model
        from its parameters when none is bundled) and apply it to the schematic.

        Also sets the UFU experimental preset combo when applicable so the
        loading widgets reflect the measured lab values.
        """
        import os
        import json

        # Resolve repo root: gui/msd_builder.py → ../.. → package root → ../.. → repo
        repo_root = os.path.normpath(os.path.join(
            os.path.dirname(__file__), '..', '..', '..'
        ))

        # Load the case's .msd if it bundles one; otherwise synthesise a model
        # from the case parameters so the builder is populated either way.
        model_path = getattr(case, 'msd_model_path', '') or ''
        try:
            if model_path:
                abs_model = model_path if os.path.isabs(model_path) else os.path.join(repo_root, model_path)
                if not os.path.isfile(abs_model):
                    QMessageBox.warning(
                        self, "Case Study", f"Model file not found:\n{abs_model}")
                    return
                with open(abs_model, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                loaded = MSDModel.from_dict(data)
            else:
                # No bundled .msd (most literature cases) — build from params.
                loaded = self._build_model_from_case(case)

            self.load_from_msd_model(loaded)
            # Push to app_state so the Solver tab's loading summary
            # (wired to app_state.model_changed) refreshes with the case's
            # loading + μ instead of staying on the Solver-tab defaults.
            main_win = self.parent()
            if main_win is not None and hasattr(main_win, 'app_state'):
                main_win.app_state.model = loaded

            # Directly refresh the Solver-tab summary from the loaded model,
            # bypassing any wiring issues between builder, app_state, solver_tab.
            if main_win is not None and hasattr(main_win, 'solver_tab'):
                gl = loaded.global_loading
                gl_type = gl.type
                type_key = gl_type.name.lower() if hasattr(gl_type, 'name') \
                    else str(gl_type).lower()
                main_win.solver_tab.update_loading_summary({
                    "type": type_key,
                    "F_preload": gl.F_preload,
                    "delta_amplitude": gl.delta_amplitude,
                    "frequency": gl.frequency,
                    "n_cycles": gl.n_cycles,
                    "mu_initial": getattr(loaded, 'mu_initial', 0.12),
                    "lubricated": getattr(loaded, 'lubricated', True),
                    "bolt_diameter": getattr(loaded, 'bolt_diameter', 16.0),
                    "pitch": getattr(loaded, 'pitch', 2.0),
                })
        except Exception as e:
            QMessageBox.warning(
                self, "Case Study", f"Failed to load case '{case.name}':\n{e}")
            return

        # NOTE: do NOT re-apply the exp_preset_combo here — that would overwrite
        # the calibrated mu_initial + two_stage_overrides that were loaded from
        # the .msd file with the hardcoded pre-calibration preset values.

        QMessageBox.information(
            self, "Case Study Loaded",
            f"Loaded: {case.name}\n"
            f"Source: {case.source.value}\n"
            f"{case.description or ''}"
        )

    def _setup_statusbar(self):
        """Setup status bar."""
        statusbar = self.statusBar()

        self.elements_label = QLabel("Elements: 0")
        statusbar.addWidget(self.elements_label)

        self.parallel_label = QLabel("Parallel groups: 0")
        statusbar.addWidget(self.parallel_label)

        self.dof_label = QLabel("DOF: 0")
        statusbar.addWidget(self.dof_label)

        sep = QLabel("\u2502")
        sep.setStyleSheet(f"color: {Theme.OVERLAY};")
        statusbar.addWidget(sep)

        self.loading_type_label = QLabel("Load: —")
        statusbar.addWidget(self.loading_type_label)

        self.preload_label = QLabel("F\u2080: —")
        statusbar.addWidget(self.preload_label)

        self.excitation_label = QLabel("Exc: —")
        statusbar.addWidget(self.excitation_label)

        self.cycles_label = QLabel("Cycles: —")
        statusbar.addWidget(self.cycles_label)

        self.friction_label = QLabel("\u03bc: —")
        statusbar.addWidget(self.friction_label)

        sep2 = QLabel("\u2502")
        sep2.setStyleSheet(f"color: {Theme.OVERLAY};")
        statusbar.addWidget(sep2)

        self.validation_label = QLabel("\u2b24 Empty")
        self.validation_label.setStyleSheet(f"color: {Theme.OVERLAY};")
        statusbar.addWidget(self.validation_label)

    def _connect_signals(self):
        """Connect signals."""
        # Palette
        self.palette.element_selected.connect(self._add_element)
        self.palette.preset_requested.connect(self._add_preset)
        self.palette.wizard_requested.connect(self._show_wizard)
        # Schematic
        self.schematic.element_selected.connect(self._on_single_select)
        self.schematic.elements_multi_selected.connect(self._on_multi_select)
        self.schematic.model_changed.connect(self._update_status)
        self.schematic.context_delete_requested.connect(self._context_delete)
        self.schematic.context_duplicate_requested.connect(self._context_duplicate)
        self.schematic.context_apply_load_requested.connect(self._context_apply_load)
        self.schematic.context_edit_contact_props_requested.connect(
            self._context_edit_contact_props)
        self.schematic.context_recalculate_requested.connect(self._context_recalculate)
        self.schematic.context_expand_requested.connect(self._context_expand_threads)
        self.schematic.context_expand_contacts_requested.connect(self._context_expand_thread_contacts)

        # Inspector
        self.inspector.property_changed.connect(self._on_property_changed)
        self.inspector.delete_requested.connect(self._delete_selected)
        self.inspector.duplicate_requested.connect(self._duplicate_selected)
        self.inspector.type_change_requested.connect(self._change_element_type)
        self.inspector.apply_load_requested.connect(self._show_load_dialog)
        self.inspector.expand_threads_requested.connect(self._expand_threads)
        self.inspector.loading_changed.connect(self._on_loading_changed)

        # Keyboard shortcuts (Delete, Ctrl+D duplicate)
        delete_action = QAction("Delete Selected", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.triggered.connect(self._delete_selected)
        self.addAction(delete_action)

        duplicate_action = QAction("Duplicate Selected", self)
        duplicate_action.setShortcut(QKeySequence("Ctrl+D"))
        duplicate_action.triggered.connect(self._duplicate_selected)
        self.addAction(duplicate_action)

    def _apply_theme(self):
        """Apply application theme. Called on init and on theme change."""
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {Theme.BASE};
                color: {Theme.TEXT};
                font-family: {Theme.FONT_SANS};
            }}
            QGroupBox {{
                border: 1px solid {Theme.SURFACE1};
                border-radius: 6px;
                margin-top: 12px;
                padding: 10px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                color: {Theme.BLUE};
            }}
            QPushButton {{
                background-color: {Theme.SURFACE1};
                color: {Theme.TEXT};
                border: 1px solid {Theme.SURFACE2};
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {Theme.SURFACE2};
                border-color: {Theme.BLUE};
            }}
            QPushButton:checked {{
                background-color: {Theme.BLUE};
                color: {Theme.BUTTON_TEXT};
                border: 1px solid {Theme.BLUE};
            }}
            QPushButton:checked:hover {{
                background-color: {Theme.LAVENDER};
                border-color: {Theme.LAVENDER};
            }}
            QComboBox, QSpinBox, QDoubleSpinBox {{
                background-color: {Theme.SURFACE0};
                color: {Theme.TEXT};
                border: 1px solid {Theme.SURFACE1};
                border-radius: 4px;
                padding: 4px 8px;
            }}
            QScrollArea {{
                border: none;
            }}
            QToolBar {{
                background-color: {Theme.MANTLE};
                border: none;
                spacing: 5px;
                padding: 5px;
            }}
            QStatusBar {{
                background-color: {Theme.MANTLE};
                color: {Theme.SUBTEXT};
            }}
        """)
        # Update scene background and element colors
        if hasattr(self, 'schematic'):
            self.schematic.setBackgroundBrush(QBrush(QColor(Theme.BASE)))
            # Refresh element colors (without recreating child items)
            for item in self.schematic.elements.values():
                visual = ELEMENT_VISUALS.get(item.element_type)
                if visual:
                    item.visual = visual
                    # Update background brush
                    color = QColor(visual.color)
                    color.setAlpha(40)
                    item.setBrush(QBrush(color))
                    # Update border pen
                    pen = QPen(QColor(visual.color))
                    pen.setWidth(2)
                    item.setPen(pen)
                    # Update text colors
                    item.type_label.setDefaultTextColor(QColor(Theme.TEXT))
                    item.k_label.setDefaultTextColor(QColor(Theme.SUBTEXT))
                    item.id_label.setDefaultTextColor(QColor(Theme.OVERLAY))
                    # Refresh force arrows colors
                    for arrow in item.force_arrows:
                        arrow.update_style()
                    item._update_yield_indicator()
            # Rebuild connection lines with new colors
            self.schematic._rebuild_connections()
        # Update force display label color
        if hasattr(self, 'inspector') and hasattr(self.inspector, 'force_display_label'):
            self.inspector.force_display_label.setStyleSheet(
                f"font-weight: bold; color: {Theme.GREEN};"
            )

    def _add_element(self, element_type: str):
        """Add element from palette (undoable)."""
        cmd = AddElementCommand(self.schematic, element_type)
        self.undo_stack.push(cmd)
        self._update_status()

    def _add_preset(self, preset_name: str):
        """Add preset configuration.

        Each preset builds a physically correct MSD chain where CONTACT elements
        (BEARING_HEAD, BEARING_NUT, GASKET_CONTACT, FLANGE_FLANGE) sit between
        every bolt element and member element in the series load path.  These
        contact elements carry the interface stiffness AND damping that the
        solver needs; without them the system is undamped at the interfaces.

        Chain conventions
        -----------------
        single_bolt  : GROUND→HEAD→BEARING_HEAD→FLANGE→BEARING_NUT→NUT
        flanged_joint: GROUND→HEAD→BEARING_HEAD→FLANGE1→GASKET_CONTACT→
                       GASKET→GASKET_CONTACT→FLANGE2→BEARING_NUT→NUT
        junker_test  : GROUND→HEAD→BEARING_HEAD→FLANGE1→FLANGE_FLANGE→
                       FLANGE2→BEARING_NUT→NUT
        """
        self.schematic.clear_all()

        if preset_name == "single_bolt":
            # --- Elements in series load path ---
            # GROUND → HEAD → [bearing] → FLANGE → [bearing] → NUT
            e = {}
            e['ground']       = self.schematic.add_element("GROUND",       0, 0).element_id
            e['head']         = self.schematic.add_element("HEAD",          1, 0).element_id
            e['bearing_head'] = self.schematic.add_element("BEARING_HEAD",  2, 0).element_id
            e['flange']       = self.schematic.add_element("FLANGE",        3, 0).element_id
            e['bearing_nut']  = self.schematic.add_element("BEARING_NUT",   4, 0).element_id
            e['nut']          = self.schematic.add_element("NUT",           5, 0).element_id

            # Thread engagement on the nut
            nut_item = self.schematic.elements[e['nut']]
            nut_item.element_data.thread_fillet_model = ThreadFilletModel(n_fillets=6)

            # --- ContactInterface metadata ---
            # Head bearing surface (HEAD ↔ BEARING_HEAD element)
            self.schematic.add_contact(e['head'], e['bearing_head'],
                ContactInterface(contact_type=ContactType.FRICTIONAL,
                                 specific_type=SpecificContactType.BOLT_HEAD_FLANGE))
            # Nut bearing surface (BEARING_NUT element ↔ NUT)
            self.schematic.add_contact(e['bearing_nut'], e['nut'],
                ContactInterface(contact_type=ContactType.FRICTIONAL,
                                 specific_type=SpecificContactType.NUT_FLANGE))
            # Thread engagement (NUT self-contact marks thread engagement)
            self.schematic.add_contact(e['nut'], e['nut'],
                ContactInterface(contact_type=ContactType.FRICTIONAL,
                                 specific_type=SpecificContactType.THREAD_CONTACT))

        elif preset_name == "flanged_joint":
            # --- Elements in series load path ---
            # GROUND→HEAD→[bearing]→FLANGE1→[gasket]→GASKET→[gasket]→FLANGE2→[bearing]→NUT
            e = {}
            e['ground']       = self.schematic.add_element("GROUND",        0, 0).element_id
            e['head']         = self.schematic.add_element("HEAD",           1, 0).element_id
            e['bearing_head'] = self.schematic.add_element("BEARING_HEAD",   2, 0).element_id
            e['flange1']      = self.schematic.add_element("FLANGE",         3, 0).element_id
            e['gc_top']       = self.schematic.add_element("GASKET_CONTACT", 4, 0).element_id
            e['gasket']       = self.schematic.add_element("GASKET",         5, 0).element_id
            e['gc_bottom']    = self.schematic.add_element("GASKET_CONTACT", 6, 0).element_id
            e['flange2']      = self.schematic.add_element("FLANGE",         7, 0).element_id
            e['bearing_nut']  = self.schematic.add_element("BEARING_NUT",    8, 0).element_id
            e['nut']          = self.schematic.add_element("NUT",            9, 0).element_id

            nut_item = self.schematic.elements[e['nut']]
            nut_item.element_data.thread_fillet_model = ThreadFilletModel(n_fillets=6)

            # --- ContactInterface metadata ---
            # Head bearing (HEAD ↔ BEARING_HEAD)
            self.schematic.add_contact(e['head'], e['bearing_head'],
                ContactInterface(contact_type=ContactType.FRICTIONAL,
                                 specific_type=SpecificContactType.BOLT_HEAD_FLANGE))
            # Top gasket interface (FLANGE1 ↔ GASKET_CONTACT top)
            self.schematic.add_contact(e['flange1'], e['gc_top'],
                ContactInterface(contact_type=ContactType.NONLINEAR,
                                 specific_type=SpecificContactType.FLANGE_GASKET))
            # Bottom gasket interface (GASKET_CONTACT bottom ↔ FLANGE2)
            self.schematic.add_contact(e['gc_bottom'], e['flange2'],
                ContactInterface(contact_type=ContactType.NONLINEAR,
                                 specific_type=SpecificContactType.FLANGE_GASKET))
            # Nut bearing (BEARING_NUT ↔ NUT)
            self.schematic.add_contact(e['bearing_nut'], e['nut'],
                ContactInterface(contact_type=ContactType.FRICTIONAL,
                                 specific_type=SpecificContactType.NUT_FLANGE))
            # Thread engagement
            self.schematic.add_contact(e['nut'], e['nut'],
                ContactInterface(contact_type=ContactType.FRICTIONAL,
                                 specific_type=SpecificContactType.THREAD_CONTACT))

        elif preset_name == "junker_test":
            # Junker test per DIN 65151 — two flanges driven into transverse slip.
            # The FLANGE_FLANGE contact element is the critical sliding interface;
            # it couples the driven plate (FLANGE1) to the base plate (FLANGE2).
            # GROUND→HEAD→[bearing]→FLANGE1→[flange-flange]→FLANGE2→[bearing]→NUT
            e = {}
            e['ground']       = self.schematic.add_element("GROUND",        0, 0).element_id
            e['head']         = self.schematic.add_element("HEAD",           1, 0).element_id
            e['bearing_head'] = self.schematic.add_element("BEARING_HEAD",   2, 0).element_id
            e['flange1']      = self.schematic.add_element("FLANGE",         3, 0).element_id
            e['ff_contact']   = self.schematic.add_element("FLANGE_FLANGE",  4, 0).element_id
            e['flange2']      = self.schematic.add_element("FLANGE",         5, 0).element_id
            e['bearing_nut']  = self.schematic.add_element("BEARING_NUT",    6, 0).element_id
            e['nut']          = self.schematic.add_element("NUT",            7, 0).element_id

            nut_item = self.schematic.elements[e['nut']]
            nut_item.element_data.thread_fillet_model = ThreadFilletModel(n_fillets=6)

            # --- ContactInterface metadata ---
            # Head bearing (HEAD ↔ BEARING_HEAD)
            self.schematic.add_contact(e['head'], e['bearing_head'],
                ContactInterface(contact_type=ContactType.FRICTIONAL,
                                 specific_type=SpecificContactType.BOLT_HEAD_FLANGE))
            # Flange-flange slip interfaces (both sides of the contact element)
            self.schematic.add_contact(e['flange1'], e['ff_contact'],
                ContactInterface(contact_type=ContactType.FRICTIONAL,
                                 specific_type=SpecificContactType.FLANGE_FLANGE))
            self.schematic.add_contact(e['ff_contact'], e['flange2'],
                ContactInterface(contact_type=ContactType.FRICTIONAL,
                                 specific_type=SpecificContactType.FLANGE_FLANGE))
            # Nut bearing (BEARING_NUT ↔ NUT)
            self.schematic.add_contact(e['bearing_nut'], e['nut'],
                ContactInterface(contact_type=ContactType.FRICTIONAL,
                                 specific_type=SpecificContactType.NUT_FLANGE))
            # Thread engagement
            self.schematic.add_contact(e['nut'], e['nut'],
                ContactInterface(contact_type=ContactType.FRICTIONAL,
                                 specific_type=SpecificContactType.THREAD_CONTACT))

        # --- Default loading: M16×2.0, 70% yield, transverse Junker-style ---
        import math as _math
        bolt_dia, bolt_pitch = 16.0, 2.0
        d2 = bolt_dia - 0.6495 * bolt_pitch
        d1 = bolt_dia - 1.0825 * bolt_pitch
        A_s = _math.pi / 4 * ((d2 + d1) / 2) ** 2
        Sy = 720.0
        F_preload = 0.70 * A_s * Sy

        loading_data = {
            "type": "Transverse",
            "F_preload": F_preload,
            "preload_percent_yield": 70.0,
            "F_transverse": 10000.0,
            "delta_amplitude": 0.65,
            "frequency": 12.5,
            "integration_time": 160.0,
            "bolt_diameter": bolt_dia,
            "pitch": bolt_pitch,
            "Sy": Sy,
            "mu_initial": 0.12,
            "lubricated": True,
        }
        self.inspector.set_loading_data(loading_data)

        # Explicitly push load overlays onto the schematic canvas (arrows/symbols)
        # in case set_loading_data() does not emit loading_changed automatically.
        self.schematic.update_load_overlays(loading_data)
        self._cached_loading_data = loading_data

        self._update_status()

    def _on_single_select(self, element):
        """Handle single selection — pass to inspector, disable quick buttons."""
        self.inspector.set_element(element)
        self.series_btn.setEnabled(False)
        self.parallel_btn.setEnabled(False)

    def _on_multi_select(self, items: List[ElementGraphicsItem]):
        """Handle multi-element selection — enable quick buttons."""
        has_pair = len(items) == 2
        self.series_btn.setEnabled(has_pair)
        self.parallel_btn.setEnabled(has_pair)

    def _on_loading_changed(self, data: dict):
        """Handle loading parameter changes from PropertyInspector."""
        self._cached_loading_data = data
        # Update load overlays on schematic
        self.schematic.update_load_overlays(data)
        # Notify parent that model has changed
        self.model_changed.emit({"source": "loading", "loading_data": data})

    def _connect_series(self):
        """Place second selected element in row after first (series, undoable)."""
        selected = self.schematic._scene.selectedItems()
        elem_items = [i for i in selected if isinstance(i, ElementGraphicsItem)]
        if len(elem_items) != 2:
            return
        before = self.schematic._snapshot_positions()
        a, b = sorted(elem_items, key=lambda e: e.grid_row)
        new_row = a.grid_row + 1
        self.schematic._insert_row_gap(new_row)
        b.set_grid_position(new_row, 0)
        self.schematic._update_grid_tracking()
        self.schematic._rebuild_connections()
        self.schematic.model_changed.emit()
        after = self.schematic._snapshot_positions()
        if after != before:
            self.undo_stack.push(GridPositionCommand(
                self.schematic, before, after, "Connect in series"))

    def _connect_parallel(self):
        """Place second selected element in same row as first (parallel, undoable)."""
        selected = self.schematic._scene.selectedItems()
        elem_items = [i for i in selected if isinstance(i, ElementGraphicsItem)]
        if len(elem_items) != 2:
            return
        before = self.schematic._snapshot_positions()
        a, b = sorted(elem_items, key=lambda e: e.grid_row)
        new_col = self.schematic._find_available_column(a.grid_row)
        b.set_grid_position(a.grid_row, new_col)
        self.schematic._update_grid_tracking()
        self.schematic._rebuild_connections()
        self.schematic.model_changed.emit()
        after = self.schematic._snapshot_positions()
        if after != before:
            self.undo_stack.push(GridPositionCommand(
                self.schematic, before, after, "Connect in parallel"))

    def _on_property_changed(self, element_id: int, prop_name: str, value):
        """Handle property changes."""
        self._update_status()
        self.schematic.model_changed.emit()

    def _delete_all(self):
        """Delete all elements after confirmation (undoable via Ctrl+Z)."""
        if not self.schematic.elements:
            return
        n_elements = len(self.schematic.elements)
        n_contacts = len(self.schematic.contacts)
        n_overlays = len(self.schematic._load_overlays)
        reply = QMessageBox.warning(
            self, "Delete All",
            f"WARNING: This will delete ALL {n_elements} elements"
            + (f", {n_contacts} contacts" if n_contacts else "")
            + (f", and {n_overlays} overlays" if n_overlays else "")
            + " from the schematic.\n\n"
            "This can be undone with Ctrl+Z (load overlays are redrawn from "
            "the loading configuration).\n\n"
            "Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            before = self.schematic._capture_state()
            after = {'elements': [], 'contacts': {}, 'next_id': 1}
            self.undo_stack.push(SchematicStateCommand(
                self.schematic, before, after, "Clear all"))
            self.inspector.set_element(None)
            self._update_status()

    def _show_help(self):
        """Show professional help dialog with tree navigation."""
        dlg = MSDBuilderHelpDialog(self)
        dlg.exec()

    # ── Validation Cases (Literature) ──────────────────────────────────

    # Short-name → full-name mapping for validation cases
    _VALIDATION_NAME_MAP = {
        "Jiang Low (M12)": "Jiang Low Load (M12)",
        "Jiang High (M12)": "Jiang High Load (M12)",
        "Junker Std (M16)": "Junker Standard (M16)",
        "Nassar Low \u03bc (M12)": "Nassar Low Friction (M12)",
        "Nassar High \u03bc (M12)": "Nassar High Friction (M12)",
        "Yang High (M16)": "Yang High Amplitude (M16)",
        "Yang Low (M16)": "Yang Low Amplitude (M16)",
        "Severe (M16)": "Severe Transverse (M16)",
    }

    def _load_validation_case(self, combo_name: str):
        """Load a validation case into the MSD Builder loading configuration."""
        from bolt_analysis_studio.core.validation_cases import get_validation_case

        if combo_name == "-- Select Case --":
            QMessageBox.warning(
                self, "No Case Selected",
                "Please select a validation case from the dropdown."
            )
            return

        case_name = self._VALIDATION_NAME_MAP.get(combo_name, combo_name)
        case = get_validation_case(case_name)
        if case is None:
            QMessageBox.warning(
                self, "Case Not Found",
                f"Validation case '{case_name}' not found."
            )
            return

        # Push case parameters into the PropertyInspector's loading UI
        loading_data = {
            "type": "Transverse",
            "F_preload": case.initial_preload_N,
            "preload_percent_yield": case.preload_percent_yield,
            "F_transverse": 0,  # displacement-driven
            "delta_amplitude": case.transverse_displacement_mm,
            "frequency": case.frequency_Hz,
            "n_cycles": case.n_cycles,
            "mu_initial": case.mu_initial,
            "lubricated": case.lubricated,
            "bolt_diameter": case.bolt_diameter_mm,
            "pitch": case.pitch_mm,
        }
        self.inspector.set_loading_data(loading_data)

        # Trigger model update
        self.inspector._on_loading_changed()

        # Store current case for paper button
        self._current_validation_case = case

        self.statusBar().showMessage(
            f"Loaded: {case.name} | "
            f"F_0={case.initial_preload_N/1000:.0f} kN, "
            f"d={case.transverse_displacement_mm:.2f} mm, "
            f"\u03bc={case.mu_initial}",
            8000
        )

    def _on_validation_case_changed(self, index):
        """Update case info label when selection changes."""
        from bolt_analysis_studio.core.validation_cases import get_validation_case

        combo_name = self.palette.validation_combo.currentText()
        if combo_name == "-- Select Case --":
            self.palette.case_info_label.setText("Select a case to see parameters")
            self.palette.open_paper_btn.setEnabled(False)
            return

        case_name = self._VALIDATION_NAME_MAP.get(combo_name, combo_name)
        case = get_validation_case(case_name)
        if case:
            info = (
                f"<b>{case.source.value}</b><br>"
                f"{case.bolt_size} | {case.initial_preload_N/1000:.0f} kN<br>"
                f"d={case.transverse_displacement_mm:.2f} mm | "
                f"\u03bc={case.mu_initial}<br>"
                f"Expected: {case.expected_final_preload_ratio*100:.0f}% "
                f"after {case.n_cycles:,} cyc"
            )
            self.palette.case_info_label.setText(info)
            self.palette.open_paper_btn.setEnabled(bool(case.url or case.doi))
            self._current_validation_case = case
        else:
            self.palette.case_info_label.setText("Case not found")
            self.palette.open_paper_btn.setEnabled(False)

    def _open_validation_paper(self):
        """Open the validation case research paper in browser."""
        import webbrowser

        case = getattr(self, '_current_validation_case', None)
        if case is None:
            QMessageBox.warning(
                self, "No Case", "Please select a validation case first.")
            return

        url = case.url if case.url else (
            f"https://doi.org/{case.doi}" if case.doi else None)

        if url:
            try:
                webbrowser.open(url)
                self.statusBar().showMessage(
                    f"Opening: {case.reference}", 5000)
            except Exception as e:
                QMessageBox.warning(
                    self, "Could Not Open",
                    f"Could not open browser:\n{e}\n\nURL: {url}")
        else:
            QMessageBox.information(
                self, "No URL Available",
                f"No URL or DOI for this case.\n\nRef: {case.reference}")

    def _delete_selected(self):
        """Delete selected element (undoable)."""
        if self.inspector.current_element:
            elem_id = self.inspector.current_element.element_id
            cmd = RemoveElementCommand(self.schematic, elem_id)
            self.undo_stack.push(cmd)
            self.inspector.set_element(None)
            self._update_status()

    def _duplicate_selected(self):
        """Duplicate selected element (undoable)."""
        if self.inspector.current_element:
            new_elem = self.schematic.duplicate_element(
                self.inspector.current_element.element_id
            )
            if new_elem:
                self.undo_stack.push(
                    DuplicateElementCommand(self.schematic, new_elem))
                # Select the new element
                self.inspector.set_element(new_elem)
                self._update_status()

    def _context_delete(self, element_id: int):
        """Delete element by ID (from context menu, undoable)."""
        cmd = RemoveElementCommand(self.schematic, element_id)
        self.undo_stack.push(cmd)
        self.inspector.set_element(None)
        self._update_status()

    def _context_duplicate(self, element_id: int):
        """Duplicate element by ID (from context menu, undoable)."""
        new_elem = self.schematic.duplicate_element(element_id)
        if new_elem:
            self.undo_stack.push(
                DuplicateElementCommand(self.schematic, new_elem))
            self.inspector.set_element(new_elem)
            self._update_status()

    def _context_apply_load(self, element_id: int):
        """Apply load to element by ID (from context menu)."""
        if element_id in self.schematic.elements:
            elem = self.schematic.elements[element_id]
            self.inspector.set_element(elem)
            self._show_load_dialog()

    def _context_edit_contact_props(self, element_id: int):
        """Edit contact properties for a contact element by ID (from context menu)."""
        if element_id not in self.schematic.elements:
            return
        elem = self.schematic.elements[element_id]
        # Phase 2.1: seed μ defaults from global mu_initial so new contacts
        # inherit the friction coefficient configured in Contact > Global.
        mu_initial = self.inspector.mu_initial_spin.value()
        dialog = ContactPropertiesDialog(elem, parent=self, mu_initial=mu_initial)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            props = dialog.get_contact_props()
            elem.element_data.contact_props = props
            # Refresh inspector panel so updated values are visible immediately
            self.inspector.set_element(elem)
            self.schematic.model_changed.emit()

    def _context_recalculate(self, element_id: int):
        """Recalculate MSD for a single element by ID (from context menu)."""
        if element_id in self.schematic.elements:
            elem_item = self.schematic.elements[element_id]
            self.inspector.set_element(elem_item)
            try:
                elem_data = elem_item.element_data
                elem_data.msd.auto_calculate_k = True
                elem_data.msd.auto_calculate_c = True
                elem_data.msd.auto_calculate_m = True
                elem_data.update_msd_parameters()
                elem_item.update_display()
                self._update_status()
                self.statusBar().showMessage(
                    f"Recalculated {elem_data.type.value} #{elem_data.id}: "
                    f"k={elem_data.msd.k:.2e} N/m, m={elem_data.msd.m:.4f} kg", 5000
                )
            except Exception as e:
                QMessageBox.warning(
                    self, "Recalculate Error",
                    f"Failed to recalculate element #{element_id}: {e}"
                )

    def _context_expand_threads(self, element_id: int):
        """Expand threads for NUT element by ID (from context menu)."""
        if element_id in self.schematic.elements:
            elem = self.schematic.elements[element_id]
            self.inspector.set_element(elem)
            self._expand_threads()

    def _context_expand_thread_contacts(self, element_id: int):
        """Expand thread contacts for THREAD element by ID (from context menu)."""
        if element_id in self.schematic.elements:
            elem = self.schematic.elements[element_id]
            self.inspector.set_element(elem)
            self._expand_thread_contacts()

    def _change_element_type(self, new_type: str):
        """Change element type of selected element."""
        if self.inspector.current_element:
            if self.schematic.change_element_type(
                self.inspector.current_element.element_id, new_type
            ):
                # Refresh inspector display
                self.inspector.set_element(self.inspector.current_element)
                self._update_status()

    def _expand_threads(self):
        """Expand NUT element into N parallel NUT elements (thread fillets).

        Replaces the original NUT with N individual NUT elements in parallel
        (same row, different columns). Each fillet-NUT gets its own
        ThreadContact. Stiffness is distributed according to the selected
        load distribution law; mass is equally divided (1/N each).

        Layout (parallel, same row):
            [element above]
             |
           Nut 1  Nut 2  ...  Nut N   (all on same row, columns 0..N-1)
             ┊      ┊           ┊
           TC 1   TC 2   ...  TC N     (one ThreadContact per nut)
             |
           [element below]
        """
        if not self.inspector.current_element:
            return

        elem = self.inspector.current_element
        if elem.element_type != "NUT":
            QMessageBox.information(
                self, "Expand Threads",
                "Select a NUT element to expand into individual threads."
            )
            return

        thread_model = elem.element_data.thread_fillet_model
        if not thread_model:
            QMessageBox.warning(
                self, "No Thread Model",
                "Configure thread fillet parameters first."
            )
            return

        # Get base position and properties of the original NUT
        nut_row = elem.grid_row
        original_id = elem.element_id

        n_fillets = thread_model.n_fillets
        factors = thread_model.get_load_factors()
        k_total = elem.element_data.msd.k
        c_total = elem.element_data.msd.c
        m_total = elem.element_data.msd.m
        fillet_k = thread_model.get_fillet_stiffnesses(k_total)

        # Collect all existing contacts of the original NUT (to reconnect later)
        old_contacts = {}  # partner_id → contact
        for (a_id, b_id), contact in list(self.schematic.contacts.items()):
            if a_id == original_id:
                old_contacts[b_id] = contact
            elif b_id == original_id:
                old_contacts[a_id] = contact

        # Snapshot the pre-expansion state so the whole operation is undoable.
        _before_state = self.schematic._capture_state()

        # Remove original NUT element (also removes its contacts)
        self.schematic.remove_element(original_id)

        # Add N parallel NUT fillet elements on the SAME row, different columns
        new_nut_ids = []
        for i in range(n_fillets):
            new_elem = self.schematic.add_element("NUT", nut_row, i)
            new_elem.element_data.name = f"Thread {i+1}"
            new_elem.element_data.msd.k = float(fillet_k[i])
            new_elem.element_data.msd.c = c_total / n_fillets
            new_elem.element_data.msd.m = m_total / n_fillets
            new_elem.element_data.thread_fillet_model = thread_model
            new_elem.update_display()
            new_nut_ids.append(new_elem.element_id)

        # Create a ThreadContact for each new NUT fillet (self-contact)
        for nut_fillet_id in new_nut_ids:
            tc = ContactInterface(
                contact_type=ContactType.FRICTIONAL,
                specific_type=SpecificContactType.THREAD_CONTACT
            )
            self.schematic.add_contact(nut_fillet_id, nut_fillet_id, tc)

        # Reconnect neighbours: ALL parallel NUTs inherit ALL old contacts
        # (each parallel fillet connects to the same upstream/downstream elements)
        for partner_id, contact in old_contacts.items():
            if partner_id not in self.schematic.elements:
                continue
            # Skip self-contacts from the original NUT (already recreated above)
            if partner_id == original_id:
                continue
            # Connect first parallel nut to the partner (represents the group)
            self.schematic.add_contact(new_nut_ids[0], partner_id, contact)

        self.schematic._update_grid_tracking()
        self.schematic._rebuild_connections()
        # Record the completed expansion as one undoable step.
        _after_state = self.schematic._capture_state()
        self.undo_stack.push(SchematicStateCommand(
            self.schematic, _before_state, _after_state,
            "Expand threads", skip_first_redo=True))
        self.inspector.set_element(None)
        self._update_status()

        dist_name = getattr(thread_model, 'distribution_law',
                           getattr(thread_model, 'distribution', 'exponential'))
        QMessageBox.information(
            self, "Threads Expanded",
            f"Expanded NUT into {n_fillets} parallel NUT elements,\n"
            f"each with its own ThreadContact.\n\n"
            f"Mass per fillet: {m_total/n_fillets:.4f} kg\n\n"
            f"Load distribution ({dist_name}):\n"
            + "\n".join(
                f"  Thread {i+1}: {factors[i]*100:.1f}% "
                f"(k = {fillet_k[i]:.0f} N/m)"
                for i in range(min(n_fillets, 8))
            )
            + (f"\n  ... ({n_fillets - 8} more)" if n_fillets > 8 else "")
        )

    def _expand_thread_contacts(self):
        """Expand a THREAD element's contacts into N individual contact elements.

        Takes the thread fillet model from the THREAD element (or an adjacent NUT)
        and creates N parallel GENERIC_CONTACT elements between the THREAD row
        and adjacent NUT row. Each contact element represents one engaged thread
        fillet with stiffness distributed according to the load distribution law.

        Layout (parallel contact elements inserted between NUT and THREAD):
            [NUT]
              |
            TC 1   TC 2   ...   TC N   (parallel contact elements)
              |
            [THREAD]
        """
        if not self.inspector.current_element:
            return

        elem = self.inspector.current_element
        if elem.element_type != "THREAD":
            QMessageBox.information(
                self, "Expand Thread Contacts",
                "Select a THREAD element to expand its contacts\n"
                "into individual thread fillet contact elements."
            )
            return

        thread_id = elem.element_id
        thread_row = elem.grid_row
        thread_data = elem.element_data

        # Get thread fillet model - check THREAD element first, then adjacent NUTs
        thread_model = thread_data.thread_fillet_model

        # Find adjacent NUT elements that have contacts with this THREAD
        nut_ids = []
        nut_contacts = {}  # nut_id → ContactInterface
        for (a_id, b_id), contact in list(self.schematic.contacts.items()):
            partner_id = None
            if a_id == thread_id:
                partner_id = b_id
            elif b_id == thread_id:
                partner_id = a_id

            if partner_id is not None and partner_id in self.schematic.elements:
                partner_elem = self.schematic.elements[partner_id]
                if partner_elem.element_type == "NUT":
                    nut_ids.append(partner_id)
                    nut_contacts[partner_id] = contact
                    # Try getting thread model from NUT if THREAD doesn't have one
                    if thread_model is None:
                        nut_model = partner_elem.element_data.thread_fillet_model
                        if nut_model is not None:
                            thread_model = nut_model

        if thread_model is None:
            # Create a default thread fillet model
            thread_model = ThreadFilletModel(
                n_fillets=6,
                pitch=thread_data.geometry.pitch or 1.75,
                distribution="exponential",
                decay_constant=0.38
            )

        n_fillets = thread_model.n_fillets
        factors = thread_model.get_load_factors()

        # Determine total contact stiffness from the THREAD element's own k
        # (thread contact stiffness is typically the THREAD element's stiffness)
        k_total = thread_data.msd.k
        c_total = thread_data.msd.c
        m_total = thread_data.msd.m
        fillet_k = thread_model.get_fillet_stiffnesses(k_total)

        # Confirm with user
        reply = QMessageBox.question(
            self, "Expand Thread Contacts",
            f"This will create {n_fillets} parallel contact elements\n"
            f"representing individual thread fillet contacts.\n\n"
            f"Distribution: {thread_model.distribution}\n"
            f"Total k: {k_total:.0f} N/m\n"
            f"First fillet load: {factors[0]*100:.1f}%\n\n"
            "The original THREAD element will remain.\n"
            "Contact elements will be inserted in a new row.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Determine insertion row: between THREAD and adjacent NUT
        # Find the NUT row (if any) to place contacts between NUT and THREAD
        insert_row = thread_row  # default: same as thread

        if nut_ids:
            nut_elem = self.schematic.elements[nut_ids[0]]
            nut_row = nut_elem.grid_row

            if nut_row < thread_row:
                # NUT above THREAD - insert contacts between them
                insert_row = thread_row  # will shift thread down
            else:
                # NUT below THREAD - insert contacts between them
                insert_row = nut_row  # will shift nut down

            # Shift all elements at insert_row and below by 1 row
            # to make room for the new contact row
            elements_to_shift = []
            for eid, eitem in self.schematic.elements.items():
                if eitem.grid_row >= insert_row:
                    elements_to_shift.append((eid, eitem))

            # Sort by row descending to shift from bottom up (avoid collisions)
            elements_to_shift.sort(key=lambda x: x[1].grid_row, reverse=True)

            for eid, eitem in elements_to_shift:
                old_row = eitem.grid_row
                old_col = eitem.grid_col
                new_row = old_row + 1

                # Update grid tracking
                if old_row in self.schematic.grid and old_col in self.schematic.grid[old_row]:
                    del self.schematic.grid[old_row][old_col]
                self.schematic.grid[new_row][old_col] = eid

                # Update element position
                eitem.element_data.grid_position.row = new_row
                eitem.grid_row = new_row
                cw, ch = get_grid_cell_width(), get_grid_cell_height()
                eitem.setPos(old_col * cw + cw // 2, new_row * ch + ch // 2)

        # Remove old contacts between THREAD and NUTs
        for nut_id in nut_ids:
            key = (min(thread_id, nut_id), max(thread_id, nut_id))
            if key in self.schematic.contacts:
                del self.schematic.contacts[key]

        # Create N parallel contact elements on the insert_row
        new_contact_ids = []
        for i in range(n_fillets):
            new_elem = self.schematic.add_element("GENERIC_CONTACT", insert_row, i)
            new_elem.element_data.name = f"Thread Contact {i+1}"
            new_elem.element_data.msd.k = float(fillet_k[i])
            new_elem.element_data.msd.c = c_total / n_fillets
            new_elem.element_data.msd.m = m_total / n_fillets
            new_elem.element_data.thread_fillet_model = thread_model
            new_elem.update_display()
            new_contact_ids.append(new_elem.element_id)

        # Create contacts: NUT ↔ each contact element, and each contact element ↔ THREAD
        for contact_elem_id in new_contact_ids:
            # Contact between each NUT and the contact element
            for nut_id in nut_ids:
                tc_nut = ContactInterface(
                    contact_type=ContactType.FRICTIONAL,
                    specific_type=SpecificContactType.THREAD_CONTACT
                )
                self.schematic.add_contact(nut_id, contact_elem_id, tc_nut)

            # Contact between each contact element and the THREAD
            tc_thread = ContactInterface(
                contact_type=ContactType.FRICTIONAL,
                specific_type=SpecificContactType.THREAD_CONTACT
            )
            self.schematic.add_contact(contact_elem_id, thread_id, tc_thread)

        # Rebuild display
        self.schematic._update_grid_tracking()
        self.schematic._rebuild_connections()
        self.inspector.set_element(None)
        self._update_status()

        dist_name = thread_model.distribution
        QMessageBox.information(
            self, "Thread Contacts Expanded",
            f"Created {n_fillets} parallel thread contact elements\n"
            f"between NUT and THREAD rows.\n\n"
            f"Load distribution ({dist_name}):\n"
            + "\n".join(
                f"  TC {i+1}: {factors[i]*100:.1f}% "
                f"(k = {fillet_k[i]:.0f} N/m)"
                for i in range(min(n_fillets, 8))
            )
            + (f"\n  ... ({n_fillets - 8} more)" if n_fillets > 8 else "")
        )

    def _show_load_dialog(self):
        """Show load application dialog."""
        if not self.inspector.current_element:
            return

        dialog = LoadDialog(self.inspector.current_element, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            loads = dialog.get_loads()
            constraints = dialog.get_constraints()

            elem = self.inspector.current_element.element_data
            elem.applied_loads = loads
            elem.constraints = constraints

            self.inspector.current_element.update_display()

            # Refresh per-element load overlays in the schematic
            loading_data = self._cached_loading_data or self.inspector.get_loading_data()
            self.schematic.update_load_overlays(loading_data)

            # Update inspector Applied Loads section
            self.inspector.set_element(self.inspector.current_element)
            # Refresh Loading > Per-Element sub-tab
            self.inspector.refresh_per_element_loads(self.schematic.elements)

    def _toggle_load_flow(self, checked: bool):
        """Toggle load flow visualization."""
        # Always rebuild connections first so topology is up-to-date
        self.schematic._rebuild_connections()

        if checked:
            # Get total load from first element with load, or use preload
            total_load = 0  # Will be set from element data below
            for item in self.schematic.elements.values():
                if item.element_data.preload_force > 0:
                    total_load = item.element_data.preload_force
                    break
                if item.element_data.applied_loads:
                    total_load = item.element_data.applied_loads[0].magnitude
                    break
            self.schematic.show_load_flow(total_load)
        else:
            self.schematic.hide_load_flow()

    def _validate_model(self):
        """Validate the model with comprehensive checks (parity with v1 builder)."""
        model = self.export_to_msd_model()
        if model is None:
            QMessageBox.warning(self, "Validation", "No elements in model")
            return

        is_valid, messages = model.validate()

        # Also run contact validation
        try:
            c_valid, c_msgs = model.validate_contacts()
            if not c_valid:
                is_valid = False
            messages.extend(c_msgs)
        except Exception:
            pass

        # Categorize messages
        errors = [m for m in messages if m.startswith("ERROR")]
        warnings = [m for m in messages if m.startswith("WARNING")]
        ok_msgs = [m for m in messages if m.startswith("OK")]

        # 3.18 — Distribute per-element validation badges
        # First clear all elements, then mark those referenced in error/warning messages
        for elem_item in self.schematic.elements.values():
            elem_item.set_validation_state([], [])
        for elem_item in self.schematic.elements.values():
            eid_str = f"#{elem_item.element_id}"
            elem_errors = [m for m in errors if eid_str in m]
            elem_warnings = [m for m in warnings if eid_str in m]
            if elem_errors or elem_warnings:
                elem_item.set_validation_state(elem_errors, elem_warnings)

        # Build report
        report_lines = [f"Model: {model.n_elements} elements, {model.n_dof} DOF\n"]
        if ok_msgs:
            report_lines.append("--- Passed Checks ---")
            report_lines.extend(f"  {m}" for m in ok_msgs)
            report_lines.append("")
        if warnings:
            report_lines.append("--- Warnings ---")
            report_lines.extend(f"  {m}" for m in warnings)
            report_lines.append("")
        if errors:
            report_lines.append("--- Errors ---")
            report_lines.extend(f"  {m}" for m in errors)
            report_lines.append("")
        report = "\n".join(report_lines)

        if is_valid and not warnings:
            QMessageBox.information(self, "Validation Passed", report)
        elif is_valid:
            QMessageBox.warning(self, "Validation Passed with Warnings", report)
        else:
            QMessageBox.critical(self, "Validation Failed", report)

    def _toggle_left_panel(self, checked: bool):
        """Toggle visibility of left panel (element palette)."""
        if checked:
            # Show panel
            self.palette.show()
            if self._saved_sizes:
                self.splitter.setSizes(self._saved_sizes)
            self.toggle_left_action.setText("< Palette")
        else:
            # Save current sizes before hiding
            self._saved_sizes = self.splitter.sizes()
            self.palette.hide()
            self.toggle_left_action.setText("> Palette")

    def _toggle_right_panel(self, checked: bool):
        """Toggle visibility of right panel (property inspector)."""
        if checked:
            # Show panel
            self.inspector.show()
            if self._saved_sizes:
                self.splitter.setSizes(self._saved_sizes)
            self.toggle_right_action.setText("Inspector >")
        else:
            # Save current sizes before hiding
            self._saved_sizes = self.splitter.sizes()
            self.inspector.hide()
            self.toggle_right_action.setText("Inspector <")

    def _show_wizard(self):
        """Show the flange joint wizard dialog."""
        # Phase 2.1: seed wizard friction defaults from global mu_initial
        mu_initial = self.inspector.mu_initial_spin.value()
        dialog = FlangeJointWizard(self, mu_initial=mu_initial)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_configuration()
            self._build_from_wizard(config)

    def _build_from_wizard(self, config: Dict[str, Any]):
        """Build joint model from wizard configuration.

        Inserts physical elements (HEAD, SHANK, NUT, WASHER, FLANGE, GASKET) AND
        explicit contact elements (BEARING_HEAD, BEARING_NUT, WASHER_CONTACT,
        FLANGE_FLANGE, GASKET_CONTACT) into the schematic so the full preload
        load path is visible and configurable.
        """
        self.schematic.clear_all()
        row = 0

        # Flags
        expand       = config["expand_threads"]
        n_fillets    = config.get("n_fillets", 6)
        n_flanges    = config["n_flanges"]
        gask_aft_idx = n_flanges // 2 - 1  # gasket inserted after this flange index
        add_head_ct  = config["add_head_contact"]   # bearing + washer contact elements
        add_flange_ct = config["add_flange_contact"] # flange interface contact elements

        # Tracked element IDs
        top_head_id       = None
        top_nut_ids       = []
        top_nut_bear_ids  = []   # BEARING_NUT elements on top side
        top_washer_id     = None
        top_washer_ct_id  = None # WASHER_CONTACT (top)
        flange_ids        = []
        flange_ct_ids     = []   # FLANGE_FLANGE elements
        gasket_id         = None
        gasket_ct_ids     = []   # GASKET_CONTACT elements (up to 2)
        bot_washer_ct_id  = None # WASHER_CONTACT (bottom)
        bot_washer_id     = None
        bot_bear_ids      = []   # BEARING_NUT elements on bottom side
        bot_nut_ids       = []
        bot_head_id       = None
        bot_bear_head_id  = None # BEARING_HEAD on bottom side

        # ── Ground ────────────────────────────────────────────────────────
        self.schematic.add_element("GROUND", row, 0)
        row += 1

        # ── TOP SIDE ──────────────────────────────────────────────────────
        if config["top_is_head"]:
            item = self.schematic.add_element("HEAD", row, 0)
            top_head_id = item.element_id
            row += 1

            if config.get("include_shank", False):
                self.schematic.add_element("SHANK", row, 0)
                row += 1

            if add_head_ct:
                item = self.schematic.add_element("BEARING_HEAD", row, 0)
                item.element_data.name = "Bearing Head (top)"
                item.update_display()
                spec = (SpecificContactType.BOLT_HEAD_WASHER
                        if config["top_washer"] else SpecificContactType.BOLT_HEAD_FLANGE)
                self.schematic.add_contact(
                    item.element_id, item.element_id,
                    ContactInterface(contact_type=ContactType.FRICTIONAL, specific_type=spec))
                row += 1

        if config["top_is_nut"] and config["top_n_nuts"] > 0:
            tfm = ThreadFilletModel(n_fillets=n_fillets)
            if expand:
                factors = tfm.get_load_factors()
                k_base = m_base = c_base = None
                for col in range(n_fillets):
                    nut_item = self.schematic.add_element("NUT", row, col)
                    nut_item.element_data.name = f"Thread {col+1}"
                    if col == 0:
                        k_base = nut_item.element_data.msd.k
                        m_base = nut_item.element_data.msd.m
                        c_base = nut_item.element_data.msd.c
                    nut_item.element_data.msd.k = k_base * factors[col] * n_fillets
                    nut_item.element_data.msd.m = m_base / n_fillets
                    nut_item.element_data.msd.c = c_base / n_fillets
                    nut_item.element_data.thread_fillet_model = tfm
                    nut_item.update_display()
                    top_nut_ids.append(nut_item.element_id)
                row += 1
            else:
                for i in range(config["top_n_nuts"]):
                    nut_item = self.schematic.add_element("NUT", row, 0)
                    nut_item.element_data.thread_fillet_model = tfm
                    top_nut_ids.append(nut_item.element_id)
                    row += 1

            # Thread contact on every top nut (mandatory)
            for nut_id in top_nut_ids:
                self.schematic.add_contact(nut_id, nut_id, ContactInterface(
                    contact_type=ContactType.FRICTIONAL,
                    specific_type=SpecificContactType.THREAD_CONTACT))

            # BEARING_NUT: between top nuts and top washer / first flange
            if add_head_ct:
                spec = (SpecificContactType.NUT_WASHER
                        if config["top_washer"] else SpecificContactType.NUT_FLANGE)
                if expand:
                    for col in range(n_fillets):
                        bn = self.schematic.add_element("BEARING_NUT", row, col)
                        bn.element_data.name = f"Bearing Nut top {col+1}"
                        bn.update_display()
                        self.schematic.add_contact(bn.element_id, bn.element_id,
                            ContactInterface(contact_type=ContactType.FRICTIONAL,
                                             specific_type=spec))
                        top_nut_bear_ids.append(bn.element_id)
                    row += 1
                else:
                    bn = self.schematic.add_element("BEARING_NUT", row, 0)
                    bn.element_data.name = "Bearing Nut (top)"
                    bn.update_display()
                    self.schematic.add_contact(bn.element_id, bn.element_id,
                        ContactInterface(contact_type=ContactType.FRICTIONAL,
                                         specific_type=spec))
                    top_nut_bear_ids.append(bn.element_id)
                    row += 1

        if config["top_washer"]:
            wtype = config.get("top_washer_type", "Flat")
            item = self.schematic.add_element("WASHER", row, 0)
            if wtype != "Flat":
                item.element_data.name = f"{wtype} Washer (top)"
                item.update_display()
            top_washer_id = item.element_id
            row += 1

            if add_head_ct:
                item = self.schematic.add_element("WASHER_CONTACT", row, 0)
                item.element_data.name = "Washer Contact (top)"
                item.update_display()
                top_washer_ct_id = item.element_id
                self.schematic.add_contact(item.element_id, item.element_id,
                    ContactInterface(contact_type=ContactType.FRICTIONAL,
                                     specific_type=SpecificContactType.WASHER_FLANGE))
                row += 1

        # ── CLAMPED MEMBERS ───────────────────────────────────────────────
        for i in range(n_flanges):
            flange_item = self.schematic.add_element("FLANGE", row, 0)
            flange_ids.append(flange_item.element_id)
            row += 1

            if config["include_gasket"] and i == gask_aft_idx:
                # Insert gasket with GASKET_CONTACT elements on both faces
                if add_flange_ct:
                    gc = self.schematic.add_element("GASKET_CONTACT", row, 0)
                    gc.element_data.name = "Gasket Contact (top face)"
                    gc.update_display()
                    self.schematic.add_contact(gc.element_id, gc.element_id,
                        ContactInterface(contact_type=ContactType.NONLINEAR,
                                         specific_type=SpecificContactType.FLANGE_GASKET))
                    gasket_ct_ids.append(gc.element_id)
                    row += 1

                g_item = self.schematic.add_element("GASKET", row, 0)
                gasket_id = g_item.element_id
                row += 1

                if add_flange_ct:
                    gc = self.schematic.add_element("GASKET_CONTACT", row, 0)
                    gc.element_data.name = "Gasket Contact (bottom face)"
                    gc.update_display()
                    self.schematic.add_contact(gc.element_id, gc.element_id,
                        ContactInterface(contact_type=ContactType.NONLINEAR,
                                         specific_type=SpecificContactType.FLANGE_GASKET))
                    gasket_ct_ids.append(gc.element_id)
                    row += 1

            elif i < n_flanges - 1 and add_flange_ct:
                ff = self.schematic.add_element("FLANGE_FLANGE", row, 0)
                ff.element_data.name = f"Flange Contact {i+1}–{i+2}"
                ff.update_display()
                self.schematic.add_contact(ff.element_id, ff.element_id,
                    ContactInterface(contact_type=ContactType.FRICTIONAL,
                                     specific_type=SpecificContactType.FLANGE_FLANGE))
                flange_ct_ids.append(ff.element_id)
                row += 1

        # ── BOTTOM SIDE ───────────────────────────────────────────────────
        if config["bottom_washer"] and add_head_ct:
            item = self.schematic.add_element("WASHER_CONTACT", row, 0)
            item.element_data.name = "Washer Contact (bottom)"
            item.update_display()
            bot_washer_ct_id = item.element_id
            self.schematic.add_contact(item.element_id, item.element_id,
                ContactInterface(contact_type=ContactType.FRICTIONAL,
                                 specific_type=SpecificContactType.WASHER_FLANGE))
            row += 1

        if config["bottom_washer"]:
            wtype = config.get("bottom_washer_type", "Flat")
            item = self.schematic.add_element("WASHER", row, 0)
            if wtype != "Flat":
                item.element_data.name = f"{wtype} Washer (bottom)"
                item.update_display()
            bot_washer_id = item.element_id
            row += 1

        if config["bottom_is_nut"]:
            tfm = ThreadFilletModel(n_fillets=n_fillets)

            # BEARING_NUT: between washer/flange and bottom nuts
            if add_head_ct:
                spec = (SpecificContactType.NUT_WASHER
                        if config["bottom_washer"] else SpecificContactType.NUT_FLANGE)
                if expand:
                    for col in range(n_fillets):
                        bn = self.schematic.add_element("BEARING_NUT", row, col)
                        bn.element_data.name = f"Bearing Nut bot {col+1}"
                        bn.update_display()
                        self.schematic.add_contact(bn.element_id, bn.element_id,
                            ContactInterface(contact_type=ContactType.FRICTIONAL,
                                             specific_type=spec))
                        bot_bear_ids.append(bn.element_id)
                    row += 1
                else:
                    bn = self.schematic.add_element("BEARING_NUT", row, 0)
                    bn.element_data.name = "Bearing Nut (bottom)"
                    bn.update_display()
                    self.schematic.add_contact(bn.element_id, bn.element_id,
                        ContactInterface(contact_type=ContactType.FRICTIONAL,
                                         specific_type=spec))
                    bot_bear_ids.append(bn.element_id)
                    row += 1

            if expand:
                factors = tfm.get_load_factors()
                k_base = m_base = c_base = None
                for col in range(n_fillets):
                    nut_item = self.schematic.add_element("NUT", row, col)
                    nut_item.element_data.name = f"Thread {col+1}"
                    if col == 0:
                        k_base = nut_item.element_data.msd.k
                        m_base = nut_item.element_data.msd.m
                        c_base = nut_item.element_data.msd.c
                    nut_item.element_data.msd.k = k_base * factors[col] * n_fillets
                    nut_item.element_data.msd.m = m_base / n_fillets
                    nut_item.element_data.msd.c = c_base / n_fillets
                    nut_item.element_data.thread_fillet_model = tfm
                    nut_item.update_display()
                    bot_nut_ids.append(nut_item.element_id)
                row += 1
            else:
                for i in range(max(1, config["bottom_n_nuts"])):
                    nut_item = self.schematic.add_element("NUT", row, 0)
                    nut_item.element_data.thread_fillet_model = tfm
                    bot_nut_ids.append(nut_item.element_id)
                    row += 1

            # Thread contact on every bottom nut (mandatory)
            for nut_id in bot_nut_ids:
                self.schematic.add_contact(nut_id, nut_id, ContactInterface(
                    contact_type=ContactType.FRICTIONAL,
                    specific_type=SpecificContactType.THREAD_CONTACT))

        if config["bottom_is_head"]:
            if add_head_ct:
                item = self.schematic.add_element("BEARING_HEAD", row, 0)
                item.element_data.name = "Bearing Head (bottom)"
                item.update_display()
                bot_bear_head_id = item.element_id
                spec = (SpecificContactType.BOLT_HEAD_WASHER
                        if config["bottom_washer"] else SpecificContactType.BOLT_HEAD_FLANGE)
                self.schematic.add_contact(item.element_id, item.element_id,
                    ContactInterface(contact_type=ContactType.FRICTIONAL,
                                     specific_type=spec))
                row += 1

            if config.get("include_shank", False):
                self.schematic.add_element("SHANK", row, 0)
                row += 1

            item = self.schematic.add_element("HEAD", row, 0)
            bot_head_id = item.element_id
            row += 1

        # ── LOADING DEFAULTS ──────────────────────────────────────────────
        import math as _math
        bolt_size = config.get("bolt_size", "M16x2.0")
        try:
            parts = bolt_size.replace("M", "").split("x")
            bolt_dia   = float(parts[0])
            bolt_pitch = float(parts[1]) if len(parts) > 1 else 2.0
        except (ValueError, IndexError):
            bolt_dia, bolt_pitch = 16.0, 2.0

        # Sy from material grade database (fall back to 720 MPa for B7/L7)
        Sy = 720.0
        grade_txt = config.get("bolt_grade", "10.9")
        grade_key = get_grade_key_from_display(grade_txt)
        if grade_key:
            props = get_properties_for_grade(grade_key)
            if props:
                Sy_db = getattr(props, 'yield_strength', None) or getattr(props, 'Sy', None)
                if Sy_db:
                    Sy = float(Sy_db)

        d2 = bolt_dia - 0.6495 * bolt_pitch
        d1 = bolt_dia - 1.0825 * bolt_pitch
        A_s = _math.pi / 4 * ((d2 + d1) / 2) ** 2  # mm²
        F_preload = 0.70 * A_s * Sy                 # N (70 % yield)

        mu_initial = self.inspector.mu_initial_spin.value()

        self.inspector.set_loading_data({
            "type": "Transverse",
            "F_preload": F_preload,
            "preload_percent_yield": 70.0,
            "F_transverse": 10000.0,
            "delta_amplitude": 0.65,
            "frequency": 12.5,
            "integration_time": 160.0,
            "bolt_diameter": bolt_dia,
            "pitch": bolt_pitch,
            "Sy": Sy,
            "mu_initial": mu_initial,
            "lubricated": True,
        })

        self._recalculate_all_elements()
        self._update_status()

        n_contact = (
            (1 if top_head_id and add_head_ct else 0) +           # BEARING_HEAD top
            len(top_nut_bear_ids) +                                 # BEARING_NUT top
            (1 if top_washer_ct_id else 0) +                       # WASHER_CONTACT top
            len(flange_ct_ids) + len(gasket_ct_ids) +              # flange contacts
            (1 if bot_washer_ct_id else 0) +                       # WASHER_CONTACT bottom
            len(bot_bear_ids) +                                     # BEARING_NUT bottom
            (1 if bot_bear_head_id else 0)                         # BEARING_HEAD bottom
        )
        n_total = len(self.schematic.elements)
        QMessageBox.information(
            self, "Joint Created",
            f"Created flanged joint with {n_total} elements "
            f"({n_total - n_contact} physical + {n_contact} contact).\n"
            f"Bolt: {config['bolt_type']}  ·  {config['bolt_size']}  ·  "
            f"Sy = {Sy:.0f} MPa\n"
            f"Default preload: {F_preload/1000:.1f} kN  (70 % yield)"
        )

    def export_to_msd_model(self) -> Optional[MSDModel]:
        """Export schematic to MSDModel. Compatibility method for main window."""
        model = self.schematic.export_to_model()
        if model is None:
            return None

        # Inject cached loading data into model
        data = self._cached_loading_data or self.inspector.get_loading_data()
        if data:
            # Map load type string to LoadingType enum.
            # `data["type"]` may be a short token ("Transverse") or the
            # combo's full display label ("Transverse (Junker)"), so match
            # case-insensitively on a substring.
            raw_type = str(data.get("type", "Transverse")).strip().lower()
            if "axial" in raw_type:
                model.global_loading.type = LoadingType.AXIAL
            elif "transverse" in raw_type or "junker" in raw_type:
                model.global_loading.type = LoadingType.TRANSVERSE
            elif "combined" in raw_type:
                model.global_loading.type = LoadingType.COMBINED
            elif "torsional" in raw_type:
                model.global_loading.type = LoadingType.TORSIONAL
            elif "bending" in raw_type:
                model.global_loading.type = LoadingType.BENDING
            else:
                model.global_loading.type = LoadingType.TRANSVERSE
            model.global_loading.F_preload = data.get("F_preload", 50000.0)
            model.global_loading.preload_percent_yield = data.get("preload_percent_yield", 70.0)
            model.global_loading.F_transverse = data.get("F_transverse", 0.0)
            model.global_loading.delta_amplitude = data.get("delta_amplitude", 0.5)
            model.global_loading.control_mode = data.get("control_mode", "displacement")
            model.global_loading.frequency = data.get("frequency", 12.5)
            model.global_loading.n_cycles = int(data.get("n_cycles", 2000))
            model.global_loading.F_external = data.get("F_external", 0.0)
            model.global_loading.T_applied = data.get("T_applied", 0.0)
            model.global_loading.delta_T = data.get("delta_T", 0.0)
            # Friction / bolt geometry
            model.mu_initial = data.get("mu_initial", 0.12)
            model.lubricated = data.get("lubricated", True)
            model.bolt_diameter = data.get("bolt_diameter", 16.0)
            model.pitch = data.get("pitch", 2.0)
            model.friction_evolution_model = data.get("friction_evolution_model", "Three-Phase")
            # Locking device (Phase F) — store slip onset in global_loading
            model.global_loading.slip_onset_factor = float(
                data.get("locking_device_slip_onset", 0.46))
            model.global_loading.locking_device_type = int(
                data.get("locking_device_type", 0))
            model.global_loading.friction_mu_increase = float(
                data.get("locking_device_mu_increase", 0.0))

            # Curve-shape Stage II tuning — written into model._two_stage_overrides
            # so create_analyzer_from_msd_model() applies them automatically.
            # Only persist non-default values to keep the .msd diff minimal.
            overrides = dict(getattr(model, '_two_stage_overrides', {}) or {})
            curve_keys = {
                "curve_F_infinity_ratio":      ("F_infinity_ratio",      0.20),
                "curve_friction_recovery_gain": ("friction_recovery_gain", 1.0),
                "curve_creep_coefficient":     ("creep_coefficient",     0.0),
                "curve_noise_amplitude":       ("noise_amplitude",       0.0),
            }
            for src, (attr, default) in curve_keys.items():
                val = float(data.get(src, default))
                if abs(val - default) > 1e-12:
                    overrides[attr] = val
                else:
                    overrides.pop(attr, None)
            if overrides:
                model._two_stage_overrides = overrides

            # Persist annotations (3.9)
            try:
                model.annotations = self.schematic.get_annotations()
            except Exception:
                pass

            # Auto-compute preload if still 0 but % yield > 0
            if model.global_loading.F_preload == 0:
                pct = model.global_loading.preload_percent_yield
                d = model.bolt_diameter
                p = model.pitch
                if pct > 0 and d > 0:
                    d2 = d - 0.6495 * p
                    d1 = d - 1.0825 * p  # ISO 262 minor diameter
                    A_s = math.pi / 4 * ((d2 + d1) / 2) ** 2
                    Sy = data.get("Sy", 640.0)
                    # Also check bolt elements for Sy
                    for elem in model.elements:
                        if elem.type.is_bolt_component and elem.material.Sy > 0:
                            Sy = elem.material.Sy
                            break
                    model.global_loading.F_preload = (pct / 100.0) * A_s * Sy

        return model

    def load_from_msd_model(self, model: MSDModel):
        """Load model into schematic. Compatibility method for main window."""
        if model is None:
            return

        try:
            self.schematic.clear_all()

            # Add elements from model
            loaded_count = 0
            failed_elements = []

            # Detect whether the model has meaningful grid positions (not all at 0,0).
            # Models saved without grid_position data (older .msd files) will have all
            # elements at the default (0, 0).  In that case use sequential row assignment
            # so elements are placed as a series chain rather than all piled on top of
            # each other (which would make export_to_model() flag them all as parallel).
            has_grid_positions = any(
                getattr(e, 'grid_position', None) is not None
                and (e.grid_position.row != 0 or e.grid_position.column != 0)
                for e in model.elements
            )

            for seq_idx, elem_data in enumerate(model.elements):
                try:
                    # Get grid position
                    if has_grid_positions:
                        row = elem_data.grid_position.row if elem_data.grid_position else seq_idx
                        col = elem_data.grid_position.column if elem_data.grid_position else 0
                    else:
                        # Fall back to sequential rows (series chain)
                        row = seq_idx
                        col = 0

                    # Get element type name
                    elem_type_name = elem_data.type.name if hasattr(elem_data.type, 'name') else str(elem_data.type)

                    # Add element with error handling
                    item = self.schematic.add_element(elem_type_name, row, col)

                    if item is None:
                        failed_elements.append(f"{elem_data.name} ({elem_type_name})")
                        continue

                    # Copy properties
                    try:
                        item.element_data.msd.k = elem_data.msd.k
                        item.element_data.msd.c = elem_data.msd.c
                        item.element_data.msd.m = elem_data.msd.m
                        item.element_data.name = elem_data.name
                    except Exception as e:
                        print(f"Warning: Failed to copy MSD properties for {elem_data.name}: {e}")

                    # Copy geometry
                    try:
                        if hasattr(elem_data, 'geometry'):
                            item.element_data.geometry.diameter = elem_data.geometry.diameter
                            item.element_data.geometry.length = elem_data.geometry.length
                            item.element_data.geometry.pitch = elem_data.geometry.pitch
                    except Exception as e:
                        print(f"Warning: Failed to copy geometry for {elem_data.name}: {e}")

                    # Copy material
                    try:
                        if hasattr(elem_data, 'material'):
                            item.element_data.material.E = elem_data.material.E
                            item.element_data.material.Sy = elem_data.material.Sy
                            item.element_data.material.Su = elem_data.material.Su
                            item.element_data.material.rho = elem_data.material.rho
                    except Exception as e:
                        print(f"Warning: Failed to copy material for {elem_data.name}: {e}")

                    # Copy preload fields
                    try:
                        if hasattr(elem_data, 'preload_percent_yield'):
                            item.element_data.preload_percent_yield = elem_data.preload_percent_yield
                        if hasattr(elem_data, 'preload_force'):
                            item.element_data.preload_force = elem_data.preload_force
                    except Exception as e:
                        print(f"Warning: Failed to copy preload for {elem_data.name}: {e}")

                    # Copy thread fillet model if present
                    try:
                        if hasattr(elem_data, 'thread_fillet_model') and elem_data.thread_fillet_model:
                            item.element_data.thread_fillet_model = elem_data.thread_fillet_model
                    except Exception as e:
                        print(f"Warning: Failed to copy thread model for {elem_data.name}: {e}")

                    item.update_display()
                    loaded_count += 1

                except Exception as e:
                    elem_name = getattr(elem_data, 'name', 'Unknown')
                    failed_elements.append(f"{elem_name}: {str(e)}")
                    print(f"Error loading element {elem_name}: {e}")
                    continue

            self._update_status()

            # Restore loading data into PropertyInspector
            try:
                type_map = {
                    LoadingType.AXIAL: "Axial",
                    LoadingType.TRANSVERSE: "Transverse",
                    LoadingType.COMBINED: "Combined",
                    LoadingType.TORSIONAL: "Torsional",
                    LoadingType.BENDING: "Bending",
                }
                # Extract Sy from bolt elements if available
                bolt_Sy = 640.0  # default
                for elem in model.elements:
                    if elem.type.is_bolt_component and hasattr(elem, 'material') and elem.material.Sy > 0:
                        bolt_Sy = elem.material.Sy
                        break

                # Pull curve-shape Stage II tuning from _two_stage_overrides
                # (written by export_to_msd_model + persisted in MSDModel.to_dict).
                ts_over = getattr(model, '_two_stage_overrides', {}) or {}
                loading_data = {
                    "type": type_map.get(model.global_loading.type, "Transverse"),
                    "F_preload": model.global_loading.F_preload,
                    "preload_percent_yield": model.global_loading.preload_percent_yield,
                    "F_transverse": model.global_loading.F_transverse,
                    "delta_amplitude": model.global_loading.delta_amplitude,
                    "frequency": model.global_loading.frequency,
                    "n_cycles": model.global_loading.n_cycles,
                    "F_external": model.global_loading.F_external,
                    "T_applied": model.global_loading.T_applied,
                    "delta_T": model.global_loading.delta_T,
                    "mu_initial": model.mu_initial,
                    "lubricated": model.lubricated,
                    "bolt_diameter": model.bolt_diameter,
                    "pitch": model.pitch,
                    "Sy": bolt_Sy,
                    "friction_evolution_model": getattr(model, "friction_evolution_model", "Three-Phase"),
                    # Curve-shape Stage II — fall back to analyzer defaults if absent
                    "curve_F_infinity_ratio":      float(ts_over.get("F_infinity_ratio",      0.20)),
                    "curve_friction_recovery_gain": float(ts_over.get("friction_recovery_gain", 1.0)),
                    "curve_creep_coefficient":     float(ts_over.get("creep_coefficient",     0.0)),
                    "curve_noise_amplitude":       float(ts_over.get("noise_amplitude",       0.0)),
                }
                self.inspector.set_loading_data(loading_data)
                # Re-read loading data after set_loading_data may have auto-computed F_preload
                self._cached_loading_data = self.inspector.get_loading_data()
                self.schematic.update_load_overlays(loading_data)
                self.inspector.refresh_per_element_loads(self.schematic.elements)
                # Propagate to parent (Solver tab loading summary) — set_loading_data
                # suppresses per-widget signals, so we emit the aggregate change here.
                self.model_changed.emit({
                    "source": "loading",
                    "loading_data": self._cached_loading_data,
                })
            except Exception as e:
                print(f"Warning: Failed to restore loading data: {e}")

            # Restore annotations (3.9)
            try:
                annotations = getattr(model, 'annotations', None) or []
                self.schematic.restore_annotations(annotations)
            except Exception as e:
                print(f"Warning: Failed to restore annotations: {e}")

            # Show summary message
            if failed_elements:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    "Model Load Warning",
                    f"Model loaded with warnings:\n\n"
                    f"Successfully loaded: {loaded_count} elements\n"
                    f"Failed: {len(failed_elements)} elements\n\n"
                    f"Failed elements:\n" + "\n".join(failed_elements[:5]) +
                    (f"\n... and {len(failed_elements) - 5} more" if len(failed_elements) > 5 else "")
                )
            else:
                print(f"Successfully loaded {loaded_count} elements from model")

            # Fit the view to the freshly loaded elements so the user sees
            # them immediately. Without this the scene keeps the previous
            # zoom/scroll position and the newly added items may be off
            # screen. Deferred via QTimer so the scene finishes laying out
            # before we compute the bounding rect.
            try:
                if self.schematic.elements:
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(0, self._fit_view)
            except Exception:
                pass

        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Model Load Error",
                f"Failed to load model:\n\n{str(e)}\n\n"
                "The model may be corrupted or incompatible with this version."
            )
            print(f"Critical error loading model: {e}")
            import traceback
            traceback.print_exc()

    def load_from_elements_dict(self, elements: dict):
        """BUG-02 fix: Populate schematic from a similitude elements dict.

        Args:
            elements: Dict with keys 'head', 'shank', 'thread', 'member',
                      'preload', 'transverse_force', 'test_frequency', etc.
                      (as returned by create_msd_elements_from_equivalent/scaled)
        """
        self.schematic.clear_all()

        row = 0
        head_id = None
        flange_id = None
        nut_id = None

        # Ground
        self.schematic.add_element("GROUND", row, 0)
        row += 1

        # Head
        if 'head' in elements:
            item = self.schematic.add_element("HEAD", row, 0)
            head_id = item.element_id
            hd = elements['head']
            if hd.get('diameter'):
                item.element_data.geometry.diameter = float(hd['diameter'])
            if hd.get('length'):
                item.element_data.geometry.length = float(hd['length'])
            if hd.get('stiffness'):
                item.element_data.msd.k = float(hd['stiffness'])
            item.update_display()
            row += 1

        # Shank
        if 'shank' in elements:
            item = self.schematic.add_element("SHANK", row, 0)
            sd = elements['shank']
            if sd.get('diameter'):
                item.element_data.geometry.diameter = float(sd['diameter'])
            if sd.get('length'):
                item.element_data.geometry.length = float(sd['length'])
            if sd.get('stiffness'):
                item.element_data.msd.k = float(sd['stiffness'])
            item.update_display()
            row += 1

        # Flange/member
        if 'member' in elements:
            item = self.schematic.add_element("FLANGE", row, 0)
            flange_id = item.element_id
            md = elements['member']
            if md.get('stiffness'):
                item.element_data.msd.k = float(md['stiffness'])
            if md.get('length'):
                item.element_data.geometry.length = float(md['length'])
            item.update_display()
            row += 1

        # Nut (from thread data)
        if 'thread' in elements:
            item = self.schematic.add_element("NUT", row, 0)
            nut_id = item.element_id
            td = elements['thread']
            if td.get('diameter'):
                item.element_data.geometry.diameter = float(td['diameter'])
            if td.get('pitch'):
                item.element_data.geometry.pitch = float(td['pitch'])
            if td.get('stiffness'):
                item.element_data.msd.k = float(td['stiffness'])
            item.element_data.thread_fillet_model = ThreadFilletModel(n_fillets=6)
            item.update_display()
            row += 1

        # Add contacts
        if nut_id is not None:
            self.schematic.add_contact(nut_id, nut_id, ContactInterface(
                contact_type=ContactType.FRICTIONAL,
                specific_type=SpecificContactType.THREAD_CONTACT))
        if head_id is not None and flange_id is not None:
            self.schematic.add_contact(head_id, flange_id, ContactInterface(
                contact_type=ContactType.FRICTIONAL,
                specific_type=SpecificContactType.BOLT_HEAD_FLANGE))

        # Set loading data into inspector
        td = elements.get('thread', {}) or {}
        loading = {
            "type": "Transverse",
            "F_preload": float(elements.get('preload', 50000.0)),
            "F_transverse": float(elements.get('transverse_force', 10000.0)),
            "frequency": float(elements.get('test_frequency', 12.5)),
            "bolt_diameter": float(td.get('diameter', 16.0) or 16.0),
            "pitch": float(td.get('pitch', 2.0) or 2.0),
            "mu_initial": 0.12,
            "lubricated": True,
        }
        self.inspector.set_loading_data(loading)
        self._cached_loading_data = self.inspector.get_loading_data()
        self._recalculate_all_elements()
        self._update_status()

    def _schematic_resize_event(self, event):
        """Keep minimap anchored to bottom-left of schematic on resize (3.16)."""
        from PyQt6.QtWidgets import QGraphicsView
        QGraphicsView.resizeEvent(self.schematic, event)
        if hasattr(self, '_minimap') and self._minimap:
            mm = self._minimap
            mm.move(4, self.schematic.height() - mm.height() - 4)
            mm.raise_()

    def _update_status(self):
        """Update status bar."""
        n_elements = len(self.schematic.elements)
        n_groups = len(self.schematic.get_parallel_groups())
        n_contacts = len(self.schematic.contacts)

        model = self.schematic.export_to_model()
        n_dof = model.n_dof if model else 0

        self.elements_label.setText(f"Elements: {n_elements}  Contacts: {n_contacts}")
        self.parallel_label.setText(f"Rows (series): {n_groups}")
        self.dof_label.setText(f"DOF: {n_dof}")

        # Preload value from loading config
        preload = 0.0
        gl = getattr(model, 'global_loading', None) if model else None
        if gl is not None:
            preload = getattr(gl, 'F_preload', 0.0)
        if preload >= 1e6:
            preload_str = f"F\u2080: {preload/1e6:.1f} MN"
        elif preload >= 1e3:
            preload_str = f"F\u2080: {preload/1e3:.1f} kN"
        elif preload > 0:
            preload_str = f"F\u2080: {preload:.0f} N"
        else:
            preload_str = "F\u2080: —"
        self.preload_label.setText(preload_str)

        # Loading type, excitation, cycles, friction
        if gl is not None:
            type_raw = getattr(gl, 'type', None)
            if type_raw is not None:
                type_str = getattr(type_raw, 'name', str(type_raw)).upper()
                short = {'TRANSVERSE': 'TRANS', 'AXIAL': 'AXIAL',
                         'COMBINED': 'COMB', 'TORSIONAL': 'TORS',
                         'THERMAL': 'THERM'}.get(type_str, type_str[:5])
                self.loading_type_label.setText(f"Load: {short}")
            else:
                self.loading_type_label.setText("Load: —")

            freq = getattr(gl, 'frequency', 0.0) or 0.0
            delta = getattr(gl, 'delta_amplitude', 0.0) or 0.0
            F_trans = getattr(gl, 'F_transverse', 0.0) or 0.0
            F_amp = getattr(gl, 'F_amplitude', 0.0) or 0.0
            is_trans = type_raw is not None and 'TRANS' in getattr(type_raw, 'name', str(type_raw)).upper()
            if is_trans and delta > 0:
                exc = f"Exc: \u0394={delta:.3f}mm @ {freq:.1f}Hz"
            elif is_trans and F_trans > 0:
                exc = f"Exc: F={F_trans/1000:.1f}kN @ {freq:.1f}Hz"
            elif F_amp > 0:
                exc = f"Exc: F={F_amp/1000:.1f}kN @ {freq:.1f}Hz"
            elif freq > 0:
                exc = f"Exc: @ {freq:.1f}Hz"
            else:
                exc = "Exc: —"
            self.excitation_label.setText(exc)

            n_cy = int(getattr(gl, 'n_cycles', 0) or 0)
            self.cycles_label.setText(f"Cycles: {n_cy:,}" if n_cy > 0 else "Cycles: —")
        else:
            self.loading_type_label.setText("Load: —")
            self.excitation_label.setText("Exc: —")
            self.cycles_label.setText("Cycles: —")

        mu = getattr(model, 'mu_initial', None) if model else None
        if mu is not None and mu > 0:
            self.friction_label.setText(f"\u03bc: {mu:.3f}")
        else:
            self.friction_label.setText("\u03bc: —")

        # Validation indicator
        if n_elements == 0:
            self.validation_label.setText("⬤ Empty")
            self.validation_label.setStyleSheet(f"color: {Theme.OVERLAY};")
        elif model and n_dof > 0:
            self.validation_label.setText("⬤ Valid")
            self.validation_label.setStyleSheet(f"color: {Theme.GREEN};")
        else:
            self.validation_label.setText("⬤ Error")
            self.validation_label.setStyleSheet(f"color: {Theme.RED};")

    def keyPressEvent(self, event):
        """Keyboard shortcuts for MSD Builder."""
        key = event.key()
        mods = event.modifiers()

        if key == Qt.Key.Key_Escape:
            # Deselect all
            self.schematic._scene.clearSelection()
            event.accept()
            return

        if mods == Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_A:
                # Select all elements
                for item in self.schematic._scene.items():
                    if isinstance(item, ElementGraphicsItem):
                        item.setSelected(True)
                event.accept()
                return
            elif key == Qt.Key.Key_R:
                # Trigger recalculate on selected element
                selected = [i for i in self.schematic._scene.selectedItems()
                            if isinstance(i, ElementGraphicsItem)]
                if selected:
                    self.schematic.context_recalculate_requested.emit(selected[0].element_id)
                event.accept()
                return
            elif key == Qt.Key.Key_D:
                # Duplicate selected element
                selected = [i for i in self.schematic._scene.selectedItems()
                            if isinstance(i, ElementGraphicsItem)]
                if selected:
                    self.schematic.context_duplicate_requested.emit(selected[0].element_id)
                event.accept()
                return

        super().keyPressEvent(event)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Run MSD Builder."""
    app = QApplication(sys.argv)

    window = MSDBuilderWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
