"""
Free Body Diagram Viewer for MSD Elements

    ⚠ EXPERIMENTAL / NÃO CONECTADO À UI ⚠
    This module is NOT wired into the application. Neither ``FBDViewer`` nor
    ``show_fbd_for_element`` is called anywhere in ``src/`` — it is dead code
    kept only so latent imports don't break. Worse, ``show_fbd_for_element``
    feeds the dialog HARDCODED placeholder forces (25 kN — see the block near
    the ``# For now, use placeholder values`` comment), NOT values extracted
    from the assembled force vector. Do not present its numbers as real
    analysis output and do not use in production.

Displays forces and moments acting on selected element with
visual arrows and numerical values.

Features:
- Force vector visualization
- Moment/torque representation
- Propagated forces from LoadPropagator
- Boundary reactions
- Export as image

Author: Bolt Analysis Studio Team
Date: February 2026
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QFormLayout, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Arc, Circle

from bolt_analysis_studio.gui.theme import Theme


class FBDViewer(QDialog):
    """
    Free Body Diagram viewer dialog.

    Shows all forces and moments acting on an element with
    visual representation and numerical values.
    """

    def __init__(self, element_data: dict, parent=None):
        """
        Initialize FBD viewer.

        Args:
            element_data: Dict with element properties and forces
                {
                    'element_id': int,
                    'element_type': str,
                    'forces': {'F_left': float, 'F_right': float, ...},
                    'moments': {'M_x': float, 'M_y': float, ...},
                    'position': (x, y, z),
                    'length': float,
                    'diameter': float
                }
            parent: Parent widget
        """
        super().__init__(parent)
        self.element_data = element_data
        self._setup_ui()

    def _setup_ui(self):
        """Setup the viewer UI."""
        elem_id = self.element_data.get('element_id', 0)
        elem_type = self.element_data.get('element_type', 'Unknown')

        self.setWindowTitle(f"Free Body Diagram - {elem_type} #{elem_id}")
        self.resize(900, 700)

        layout = QVBoxLayout(self)

        # Header
        header = QLabel(f"Free Body Diagram: {elem_type} Element #{elem_id}")
        header.setFont(QFont(Theme.FONT_SANS, 14, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {Theme.BLUE}; padding: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Matplotlib figure
        self.figure = Figure(figsize=(9, 6), facecolor=Theme.BASE)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

        # Force summary panel
        summary_group = QGroupBox("Force Summary")
        summary_layout = QFormLayout(summary_group)

        forces = self.element_data.get('forces', {})
        moments = self.element_data.get('moments', {})

        # Display forces
        for force_name, value in forces.items():
            label = QLabel(f"{value:+.1f} N")
            label.setStyleSheet(f"color: {Theme.TEXT}; font-weight: bold;")
            summary_layout.addRow(f"{force_name}:", label)

        # Display moments
        for moment_name, value in moments.items():
            label = QLabel(f"{value:+.2f} N·m")
            label.setStyleSheet(f"color: {Theme.TEXT}; font-weight: bold;")
            summary_layout.addRow(f"{moment_name}:", label)

        layout.addWidget(summary_group)

        # Button panel
        button_layout = QHBoxLayout()

        export_btn = QPushButton("💾 Export Image")
        export_btn.clicked.connect(self._export_image)
        button_layout.addWidget(export_btn)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._draw_fbd)
        button_layout.addWidget(refresh_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        # Draw the FBD
        self._draw_fbd()

    def _draw_fbd(self):
        """Draw the free body diagram."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Get element geometry
        length = self.element_data.get('length', 0.05)  # Default 50mm
        diameter = self.element_data.get('diameter', 0.016)  # Default 16mm

        # Scale for drawing
        scale = max(length, diameter) * 1.5

        # Draw element as rectangle (simplified)
        element_width = length * 0.8
        element_height = diameter * 0.3

        # Element center at origin
        rect = mpatches.Rectangle(
            (-element_width/2, -element_height/2),
            element_width,
            element_height,
            linewidth=2,
            edgecolor=Theme.BLUE,
            facecolor=Theme.SURFACE0,
            label='Element'
        )
        ax.add_patch(rect)

        # Get forces
        forces = self.element_data.get('forces', {})
        moments = self.element_data.get('moments', {})

        # Draw forces
        arrow_scale = scale * 0.001  # Scale factor for force arrows

        # Left force (compression/tension)
        F_left = forces.get('F_left', 0)
        if abs(F_left) > 1e-6:
            self._draw_force_arrow(
                ax,
                x_start=-element_width/2,
                y_start=0,
                force=F_left,
                direction='left',
                scale=arrow_scale,
                label=f'F_L = {F_left:.1f} N'
            )

        # Right force
        F_right = forces.get('F_right', 0)
        if abs(F_right) > 1e-6:
            self._draw_force_arrow(
                ax,
                x_start=element_width/2,
                y_start=0,
                force=F_right,
                direction='right',
                scale=arrow_scale,
                label=f'F_R = {F_right:.1f} N'
            )

        # Top force (transverse)
        F_top = forces.get('F_transverse', 0)
        if abs(F_top) > 1e-6:
            self._draw_force_arrow(
                ax,
                x_start=0,
                y_start=element_height/2,
                force=F_top,
                direction='up',
                scale=arrow_scale,
                label=f'F_trans = {F_top:.1f} N'
            )

        # Draw moments
        M_center = moments.get('M_center', 0)
        if abs(M_center) > 1e-6:
            self._draw_moment_arc(
                ax,
                x=0,
                y=0,
                moment=M_center,
                radius=element_width * 0.3,
                label=f'M = {M_center:.2f} N·m'
            )

        # Formatting
        ax.set_xlim(-scale, scale)
        ax.set_ylim(-scale*0.6, scale*0.6)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.2, color=Theme.SURFACE1)
        ax.set_facecolor(Theme.BASE)
        ax.tick_params(colors=Theme.TEXT)

        # Labels
        elem_type = self.element_data.get('element_type', 'Element')
        elem_id = self.element_data.get('element_id', 0)
        ax.set_title(
            f'Free Body Diagram: {elem_type} #{elem_id}',
            color=Theme.TEXT,
            fontweight='bold',
            fontsize=12
        )
        ax.set_xlabel('Position (m)', color=Theme.TEXT)
        ax.set_ylabel('Position (m)', color=Theme.TEXT)

        # Legend
        ax.legend(loc='upper right', facecolor=Theme.SURFACE0,
                 edgecolor=Theme.SURFACE1, framealpha=0.9)

        # Style spines
        for spine in ax.spines.values():
            spine.set_color(Theme.SURFACE1)

        self.figure.tight_layout()
        self.canvas.draw()

    def _draw_force_arrow(self, ax, x_start, y_start, force, direction,
                         scale, label):
        """
        Draw force arrow on diagram.

        Args:
            ax: Matplotlib axes
            x_start, y_start: Arrow start position
            force: Force magnitude [N]
            direction: 'left', 'right', 'up', 'down'
            scale: Arrow length scale
            label: Label text
        """
        arrow_length = abs(force) * scale

        # Direction vectors
        directions = {
            'left': (-1, 0),
            'right': (1, 0),
            'up': (0, 1),
            'down': (0, -1)
        }

        dx, dy = directions.get(direction, (1, 0))

        # Color based on tension/compression
        if force > 0:
            color = Theme.RED  # Tension
        else:
            color = Theme.BLUE  # Compression

        # Draw arrow
        arrow = FancyArrowPatch(
            (x_start, y_start),
            (x_start + dx * arrow_length, y_start + dy * arrow_length),
            arrowstyle='->,head_width=0.4,head_length=0.8',
            color=color,
            linewidth=2,
            label=label
        )
        ax.add_patch(arrow)

        # Add magnitude label
        text_offset = arrow_length * 1.2
        ax.text(
            x_start + dx * text_offset,
            y_start + dy * text_offset,
            f'{abs(force):.1f} N',
            ha='center',
            va='center',
            color=color,
            fontsize=9,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=Theme.SURFACE0,
                     edgecolor=color, alpha=0.8)
        )

    def _draw_moment_arc(self, ax, x, y, moment, radius, label):
        """
        Draw moment/torque as curved arrow.

        Args:
            ax: Matplotlib axes
            x, y: Center position
            moment: Moment magnitude [N·m]
            radius: Arc radius
            label: Label text
        """
        # Color based on direction
        color = Theme.MAUVE if moment > 0 else Theme.PINK

        # Draw circular arc
        arc_angle = 270
        start_angle = 45 if moment > 0 else -45

        arc = Arc(
            (x, y),
            2 * radius,
            2 * radius,
            angle=0,
            theta1=start_angle,
            theta2=start_angle + arc_angle,
            color=color,
            linewidth=2,
            label=label
        )
        ax.add_patch(arc)

        # Arrow head at end
        end_angle_rad = np.radians(start_angle + arc_angle)
        arrow_x = x + radius * np.cos(end_angle_rad)
        arrow_y = y + radius * np.sin(end_angle_rad)

        # Tangent direction for arrow
        tangent_angle = end_angle_rad + np.pi/2 if moment > 0 else end_angle_rad - np.pi/2
        arrow_dx = np.cos(tangent_angle) * radius * 0.1
        arrow_dy = np.sin(tangent_angle) * radius * 0.1

        arrow = FancyArrowPatch(
            (arrow_x - arrow_dx, arrow_y - arrow_dy),
            (arrow_x, arrow_y),
            arrowstyle='->,head_width=0.3,head_length=0.6',
            color=color,
            linewidth=2
        )
        ax.add_patch(arrow)

        # Label
        ax.text(
            x,
            y + radius * 1.5,
            f'{abs(moment):.2f} N·m',
            ha='center',
            va='center',
            color=color,
            fontsize=9,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=Theme.SURFACE0,
                     edgecolor=color, alpha=0.8)
        )

    def _export_image(self):
        """Export FBD as image file."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Free Body Diagram",
            f"FBD_element_{self.element_data.get('element_id', 0)}.png",
            "PNG Image (*.png);;PDF Document (*.pdf);;SVG Vector (*.svg)"
        )

        if filename:
            try:
                self.figure.savefig(
                    filename,
                    dpi=300,
                    bbox_inches='tight',
                    facecolor=Theme.BASE
                )
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Free body diagram saved to:\n{filename}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to export image:\n{str(e)}"
                )


# Helper function to show FBD for an element
def show_fbd_for_element(element_item, model=None, parent=None):
    """
    Show FBD dialog for a given element.

    Args:
        element_item: ElementGraphicsItem to analyze
        model: MSDModel (optional, for force calculation)
        parent: Parent widget

    Returns:
        FBDViewer dialog instance
    """
    # Extract element data
    element_data = {
        'element_id': element_item.element_id,
        'element_type': element_item.element_type,
        'length': getattr(element_item, 'length', 0.05),
        'diameter': getattr(element_item, 'diameter', 0.016),
        'forces': {},
        'moments': {}
    }

    # Get forces from model if available
    if model is not None:
        # ⚠ EXPERIMENTAL / NÃO CONECTADO À UI: these are HARDCODED placeholder
        # forces (25 kN), NOT extracted from the assembled force vector. This
        # helper is dead code (never called in src/) — do not use in production
        # and do not treat these numbers as real analysis output.
        # TODO: Extract forces from assembled force vector
        # For now, use placeholder values
        element_data['forces'] = {
            'F_left': 25000.0,  # Example: 25 kN compression
            'F_right': 25000.0,
            'F_transverse': 0.0
        }
        element_data['moments'] = {
            'M_center': 0.0
        }
    else:
        # Placeholder values
        element_data['forces'] = {
            'F_left': element_item.k * 0.001,  # Estimate from stiffness
            'F_right': element_item.k * 0.001,
            'F_transverse': 0.0
        }
        element_data['moments'] = {
            'M_center': 0.0
        }

    # Create and show dialog
    dialog = FBDViewer(element_data, parent=parent)
    dialog.exec()

    return dialog
