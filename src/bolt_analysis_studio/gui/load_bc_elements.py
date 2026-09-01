"""
Load and Boundary Condition Visual Elements for MSD Builder.

Provides graphical representations of loads and boundary conditions
that can be added to the schematic view.

Features:
- Force arrows (axial, transverse, external)
- Moment symbols (bending, torque)
- Boundary condition symbols (fixed, pinned, roller)
- Displacement BC indicators
- Preload indicators

Author: Bolt Analysis Studio Team
Date: February 2026
"""

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPainterPath,
    QPolygonF, QTransform
)
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsEllipseItem

from bolt_analysis_studio.gui.theme import Theme
import math


class LoadElement(QGraphicsItem):
    """
    Base class for load visual elements.

    Loads are visual indicators that don't have mechanical properties
    (k, c, m) but connect to elements to show applied forces/moments.
    """

    def __init__(self, load_type: str, magnitude: float = 0.0):
        super().__init__()
        self.load_type = load_type  # "FORCE_AXIAL", "FORCE_TRANS", "MOMENT", "TORQUE"
        self.magnitude = magnitude
        self.element_type = f"LOAD_{load_type}"

        # Visual properties
        self.color = Theme.YELLOW
        self.width = 60
        self.height = 60

        # Labels
        self.label = f"{magnitude:.0f} N"
        self.label_visible = True

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

    def boundingRect(self) -> QRectF:
        return QRectF(-self.width/2, -self.height/2, self.width, self.height)

    def paint(self, painter: QPainter, option, widget=None):
        """Override in subclasses for specific load type visualization."""
        pass

    def update_magnitude(self, magnitude: float):
        """Update load magnitude and label."""
        self.magnitude = magnitude
        self.label = f"{magnitude:.0f} N"
        self.update()


class ForceArrow(LoadElement):
    """
    Visual representation of a force (arrow).

    Direction controlled by rotation, magnitude by label.
    """

    def __init__(self, magnitude: float = 1000.0, direction: str = "AXIAL"):
        super().__init__(load_type=f"FORCE_{direction}", magnitude=magnitude)
        self.direction = direction
        self.arrow_length = 40
        self.arrow_head_size = 10

        if direction == "AXIAL":
            self.color = Theme.BLUE
        elif direction == "TRANSVERSE":
            self.color = Theme.GREEN
            self.setRotation(90)  # Rotate for transverse
        else:
            self.color = Theme.YELLOW

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw arrow shaft
        pen = QPen(QColor(self.color), 3)
        painter.setPen(pen)

        # Shaft line
        shaft_start = QPointF(0, 0)
        shaft_end = QPointF(0, -self.arrow_length)
        painter.drawLine(shaft_start, shaft_end)

        # Arrow head (triangle)
        head_points = QPolygonF([
            QPointF(0, -self.arrow_length),  # Tip
            QPointF(-self.arrow_head_size/2, -self.arrow_length + self.arrow_head_size),
            QPointF(self.arrow_head_size/2, -self.arrow_length + self.arrow_head_size),
        ])

        brush = QBrush(QColor(self.color))
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(head_points)

        # Label
        if self.label_visible:
            font = QFont(Theme.FONT_SANS, 9)
            painter.setFont(font)
            painter.setPen(QPen(QColor(Theme.TEXT)))
            text_rect = QRectF(-30, 5, 60, 20)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.label)


class MomentSymbol(LoadElement):
    """
    Visual representation of a bending moment (curved arrow).
    """

    def __init__(self, magnitude: float = 100.0):
        super().__init__(load_type="MOMENT", magnitude=magnitude)
        self.color = Theme.MAUVE
        self.radius = 20
        self.label = f"{magnitude:.0f} N·m"

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw curved arrow
        pen = QPen(QColor(self.color), 3)
        painter.setPen(pen)

        # Arc (270 degrees)
        rect = QRectF(-self.radius, -self.radius, 2*self.radius, 2*self.radius)
        start_angle = 30 * 16  # Qt uses 1/16 degree units
        span_angle = 270 * 16
        painter.drawArc(rect, start_angle, span_angle)

        # Arrow head at end of arc
        end_angle_rad = math.radians(30 + 270)
        tip_x = self.radius * math.cos(end_angle_rad)
        tip_y = -self.radius * math.sin(end_angle_rad)

        head_points = QPolygonF([
            QPointF(tip_x, tip_y),
            QPointF(tip_x - 8, tip_y + 5),
            QPointF(tip_x - 5, tip_y - 5),
        ])

        brush = QBrush(QColor(self.color))
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(head_points)

        # Label
        if self.label_visible:
            font = QFont(Theme.FONT_SANS, 9)
            painter.setFont(font)
            painter.setPen(QPen(QColor(Theme.TEXT)))
            text_rect = QRectF(-30, self.radius + 5, 60, 20)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.label)


class TorqueSymbol(LoadElement):
    """
    Visual representation of a torque (circular arrow with double head).
    """

    def __init__(self, magnitude: float = 50.0):
        super().__init__(load_type="TORQUE", magnitude=magnitude)
        self.color = Theme.PINK
        self.radius = 20
        self.label = f"{magnitude:.0f} N·m"

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw circular arc with arrow heads
        pen = QPen(QColor(self.color), 3)
        painter.setPen(pen)

        # Arc
        rect = QRectF(-self.radius, -self.radius, 2*self.radius, 2*self.radius)
        start_angle = 0
        span_angle = 270 * 16
        painter.drawArc(rect, start_angle, span_angle)

        # Arrow heads at both ends
        brush = QBrush(QColor(self.color))
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)

        # Head 1 (at 0 degrees)
        head1 = QPolygonF([
            QPointF(self.radius, 0),
            QPointF(self.radius - 8, 5),
            QPointF(self.radius - 5, -5),
        ])
        painter.drawPolygon(head1)

        # Head 2 (at 270 degrees)
        tip2_x = 0
        tip2_y = -self.radius
        head2 = QPolygonF([
            QPointF(tip2_x, tip2_y),
            QPointF(tip2_x - 5, tip2_y + 8),
            QPointF(tip2_x + 5, tip2_y + 5),
        ])
        painter.drawPolygon(head2)

        # Label
        if self.label_visible:
            font = QFont(Theme.FONT_SANS, 9)
            painter.setFont(font)
            painter.setPen(QPen(QColor(Theme.TEXT)))
            text_rect = QRectF(-30, -5, 60, 15)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.label)


class BoundaryCondition(QGraphicsItem):
    """
    Base class for boundary condition visual elements.
    """

    def __init__(self, bc_type: str):
        super().__init__()
        self.bc_type = bc_type  # "FIXED", "PINNED", "ROLLER", "PRESCRIBED_DISP"
        self.element_type = f"BC_{bc_type}"

        self.color = Theme.RED
        self.width = 40
        self.height = 40

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

    def boundingRect(self) -> QRectF:
        return QRectF(-self.width/2, -self.height/2, self.width, self.height)

    def paint(self, painter: QPainter, option, widget=None):
        pass


class FixedSupport(BoundaryCondition):
    """Fixed boundary condition (triangle with hatching)."""

    def __init__(self):
        super().__init__(bc_type="FIXED")

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Triangle
        triangle = QPolygonF([
            QPointF(0, -15),
            QPointF(-15, 10),
            QPointF(15, 10),
        ])

        pen = QPen(QColor(self.color), 2)
        painter.setPen(pen)
        brush = QBrush(QColor(self.color).lighter(160))
        painter.setBrush(brush)
        painter.drawPolygon(triangle)

        # Ground hatching
        pen_hatch = QPen(QColor(self.color), 1)
        painter.setPen(pen_hatch)
        for x in range(-15, 16, 5):
            painter.drawLine(QPointF(x, 10), QPointF(x + 5, 15))


class PinnedSupport(BoundaryCondition):
    """Pinned boundary condition (circle on triangle)."""

    def __init__(self):
        super().__init__(bc_type="PINNED")

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Circle (pin)
        pen = QPen(QColor(self.color), 2)
        painter.setPen(pen)
        brush = QBrush(QColor(Theme.SURFACE0))
        painter.setBrush(brush)
        painter.drawEllipse(QPointF(0, -10), 5, 5)

        # Triangle base
        triangle = QPolygonF([
            QPointF(0, -5),
            QPointF(-12, 10),
            QPointF(12, 10),
        ])

        brush2 = QBrush(QColor(self.color).lighter(160))
        painter.setBrush(brush2)
        painter.drawPolygon(triangle)

        # Ground hatching
        pen_hatch = QPen(QColor(self.color), 1)
        painter.setPen(pen_hatch)
        for x in range(-12, 13, 4):
            painter.drawLine(QPointF(x, 10), QPointF(x + 4, 15))


class PreloadIndicator(LoadElement):
    """Visual indicator for bolt preload."""

    def __init__(self, preload: float = 50000.0):
        super().__init__(load_type="PRELOAD", magnitude=preload)
        self.color = Theme.BLUE
        self.label = f"F₀ = {preload/1000:.1f} kN"

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Double-headed arrow (compression)
        pen = QPen(QColor(self.color), 3)
        painter.setPen(pen)

        # Vertical line
        painter.drawLine(QPointF(0, -20), QPointF(0, 20))

        # Top arrow head (pointing down)
        top_head = QPolygonF([
            QPointF(0, -20),
            QPointF(-6, -14),
            QPointF(6, -14),
        ])

        # Bottom arrow head (pointing up)
        bottom_head = QPolygonF([
            QPointF(0, 20),
            QPointF(-6, 14),
            QPointF(6, 14),
        ])

        brush = QBrush(QColor(self.color))
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(top_head)
        painter.drawPolygon(bottom_head)

        # Label
        if self.label_visible:
            font = QFont(Theme.FONT_SANS, 9, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(QColor(Theme.TEXT)))
            text_rect = QRectF(-40, -5, 80, 15)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.label)


# Factory functions for creating load/BC elements
def create_force_element(direction: str = "AXIAL", magnitude: float = 1000.0) -> ForceArrow:
    """Create force arrow element."""
    return ForceArrow(magnitude=magnitude, direction=direction)


def create_moment_element(magnitude: float = 100.0) -> MomentSymbol:
    """Create moment symbol element."""
    return MomentSymbol(magnitude=magnitude)


def create_torque_element(magnitude: float = 50.0) -> TorqueSymbol:
    """Create torque symbol element."""
    return TorqueSymbol(magnitude=magnitude)


def create_fixed_support() -> FixedSupport:
    """Create fixed boundary condition."""
    return FixedSupport()


def create_pinned_support() -> PinnedSupport:
    """Create pinned boundary condition."""
    return PinnedSupport()


def create_preload_indicator(preload: float = 50000.0) -> PreloadIndicator:
    """Create preload indicator."""
    return PreloadIndicator(preload=preload)
