"""
Plot Manager Module
Matplotlib-Qt integration for Bolt Analysis Studio v4.0

Prof. Leonardo Rosa Ribeiro da Silva, PhD
January 2026

Provides:
- Embedded matplotlib figures in Qt widgets
- Standard plot types for analysis results
- Theme integration (Catppuccin Mocha)
- Export functionality
"""

import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt

import matplotlib
matplotlib.use('QtAgg')

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


# =============================================================================
# THEME CONFIGURATION (dynamic from central Theme)
# =============================================================================

from bolt_analysis_studio.gui.theme import Theme as _Theme


class _ThemeDictProxy(dict):
    """Dict-like object that always reads from Theme.get_theme_dict()."""
    def __getitem__(self, key):
        return _Theme.get_theme_dict()[key]
    def get(self, key, default=None):
        return _Theme.get_theme_dict().get(key, default)
    def __contains__(self, key):
        return key in _Theme.get_theme_dict()
    def values(self):
        return _Theme.get_theme_dict().values()
    def keys(self):
        return _Theme.get_theme_dict().keys()
    def items(self):
        return _Theme.get_theme_dict().items()

THEME = _ThemeDictProxy()


class _PlotStyleProxy(dict):
    """Dict-like that returns fresh rcParams from Theme."""
    def __getitem__(self, key):
        return _Theme.get_plot_style()[key]
    def get(self, key, default=None):
        return _Theme.get_plot_style().get(key, default)
    def items(self):
        return _Theme.get_plot_style().items()
    def keys(self):
        return _Theme.get_plot_style().keys()
    def values(self):
        return _Theme.get_plot_style().values()
    def __contains__(self, key):
        return key in _Theme.get_plot_style()
    def __iter__(self):
        return iter(_Theme.get_plot_style())
    def __len__(self):
        return len(_Theme.get_plot_style())

PLOT_STYLE = _PlotStyleProxy()


class _LineColorsProxy(list):
    """List-like that returns fresh line colors from Theme."""
    def __getitem__(self, index):
        return _Theme.get_line_colors()[index]
    def __iter__(self):
        return iter(_Theme.get_line_colors())
    def __len__(self):
        return len(_Theme.get_line_colors())

LINE_COLORS = _LineColorsProxy()


# =============================================================================
# MATPLOTLIB CANVAS WIDGET
# =============================================================================

class MplCanvas(FigureCanvas):
    """Matplotlib canvas embedded in Qt widget."""

    def __init__(self, parent=None, width=8, height=6, dpi=100):
        # Apply style
        plt.rcParams.update(PLOT_STYLE)

        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor=THEME["BASE"])
        self.axes = self.fig.add_subplot(111)

        super().__init__(self.fig)
        self.setParent(parent)

        # Set size policy
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.updateGeometry()

    def clear(self):
        """Clear the axes."""
        self.axes.clear()
        self._apply_theme()
        self.draw()

    def _apply_theme(self):
        """Apply theme to axes."""
        self.axes.set_facecolor(THEME["SURFACE0"])
        self.axes.tick_params(colors=THEME["SUBTEXT"])
        self.axes.xaxis.label.set_color(THEME["TEXT"])
        self.axes.yaxis.label.set_color(THEME["TEXT"])
        self.axes.title.set_color(THEME["TEXT"])
        for spine in self.axes.spines.values():
            spine.set_color(THEME["SURFACE2"])


class PlotWidget(QWidget):
    """Widget containing matplotlib canvas and toolbar."""

    def __init__(self, parent=None, width=8, height=6, dpi=100, toolbar=True):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create canvas
        self.canvas = MplCanvas(self, width, height, dpi)

        # Optionally add toolbar
        if toolbar:
            self.toolbar = NavigationToolbar(self.canvas, self)
            self.toolbar.setStyleSheet(f"""
                QToolBar {{
                    background-color: {THEME["MANTLE"]};
                    border: none;
                    spacing: 4px;
                }}
                QToolButton {{
                    background-color: {THEME["SURFACE1"]};
                    color: {THEME["TEXT"]};
                    border: none;
                    padding: 4px;
                    border-radius: 4px;
                }}
                QToolButton:hover {{
                    background-color: {THEME["SURFACE2"]};
                }}
            """)
            layout.addWidget(self.toolbar)
        else:
            self.toolbar = None

        layout.addWidget(self.canvas)

    @property
    def axes(self):
        """Get the axes."""
        return self.canvas.axes

    @property
    def figure(self):
        """Get the figure."""
        return self.canvas.fig

    def draw(self):
        """Redraw the canvas."""
        self.canvas.draw()

    def clear(self):
        """Clear the plot."""
        self.canvas.clear()

    def save_figure(self, path: str, dpi: int = 150):
        """Save figure to file."""
        self.canvas.fig.savefig(
            path,
            dpi=dpi,
            facecolor=THEME["BASE"],
            edgecolor='none',
            bbox_inches='tight'
        )


# =============================================================================
# PLOT MANAGER
# =============================================================================

class PlotManager:
    """
    Manager for creating and updating plots in the application.

    Provides standard plot types:
    - Preload loss curves
    - Time history plots
    - Frequency response
    - Mode shapes
    """

    @staticmethod
    def plot_preload_loss(
        widget: PlotWidget,
        cycles: np.ndarray,
        results: Dict[str, np.ndarray],
        title: str = "Preload Loss Curves",
        xlabel: str = "Cycles (N)",
        ylabel: str = "Normalized Preload (F/F₀)"
    ):
        """
        Plot preload loss curves for multiple models.

        Args:
            widget: PlotWidget to draw on
            cycles: Array of cycle counts
            results: Dict mapping model name to preload ratio arrays
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
        """
        ax = widget.axes
        ax.clear()

        # Plot each model
        for i, (name, data) in enumerate(results.items()):
            color = LINE_COLORS[i % len(LINE_COLORS)]
            label = name.replace("_", " ").title()
            ax.plot(cycles, data, color=color, label=label, linewidth=2)

        # Styling
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)

        # Set axis limits
        ax.set_xlim(0, cycles[-1] if len(cycles) > 0 else 1)
        ax.set_ylim(0, 1.05)

        # Add reference lines
        ax.axhline(y=0.5, color=THEME["YELLOW"], linestyle='--', alpha=0.5, label='50% loss')
        ax.axhline(y=0.75, color=THEME["GREEN"], linestyle='--', alpha=0.5, label='25% loss')

        widget.canvas._apply_theme()
        widget.draw()

    @staticmethod
    def plot_time_history(
        widget: PlotWidget,
        time: np.ndarray,
        data: np.ndarray,
        labels: Optional[List[str]] = None,
        title: str = "Time History",
        xlabel: str = "Time (s)",
        ylabel: str = "Response"
    ):
        """
        Plot time history data.

        Args:
            widget: PlotWidget to draw on
            time: Time array
            data: Response data [n_steps] or [n_steps, n_dof]
            labels: Optional labels for each DOF
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
        """
        ax = widget.axes
        ax.clear()

        # Handle 1D and 2D data
        if len(data.shape) == 1:
            data = data.reshape(-1, 1)

        n_dof = data.shape[1]

        for i in range(n_dof):
            color = LINE_COLORS[i % len(LINE_COLORS)]
            label = labels[i] if labels and i < len(labels) else f"DOF {i+1}"
            ax.plot(time, data[:, i], color=color, label=label, linewidth=1.5)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)

        widget.canvas._apply_theme()
        widget.draw()

    @staticmethod
    def plot_displacement(
        widget: PlotWidget,
        time: np.ndarray,
        displacement: np.ndarray,
        labels: Optional[List[str]] = None
    ):
        """Plot displacement time history."""
        PlotManager.plot_time_history(
            widget, time, displacement, labels,
            title="Displacement Time History",
            xlabel="Time (s)",
            ylabel="Displacement (m)"
        )

    @staticmethod
    def plot_velocity(
        widget: PlotWidget,
        time: np.ndarray,
        velocity: np.ndarray,
        labels: Optional[List[str]] = None
    ):
        """Plot velocity time history."""
        PlotManager.plot_time_history(
            widget, time, velocity, labels,
            title="Velocity Time History",
            xlabel="Time (s)",
            ylabel="Velocity (m/s)"
        )

    @staticmethod
    def plot_acceleration(
        widget: PlotWidget,
        time: np.ndarray,
        acceleration: np.ndarray,
        labels: Optional[List[str]] = None
    ):
        """Plot acceleration time history."""
        PlotManager.plot_time_history(
            widget, time, acceleration, labels,
            title="Acceleration Time History",
            xlabel="Time (s)",
            ylabel="Acceleration (m/s²)"
        )

    @staticmethod
    def plot_phase_portrait(
        widget: PlotWidget,
        displacement: np.ndarray,
        velocity: np.ndarray,
        dof: int = 0,
        title: str = "Phase Portrait"
    ):
        """
        Plot phase portrait (velocity vs displacement).

        Args:
            widget: PlotWidget to draw on
            displacement: Displacement data [n_steps] or [n_steps, n_dof]
            velocity: Velocity data [n_steps] or [n_steps, n_dof]
            dof: DOF index to plot (if multi-DOF)
            title: Plot title
        """
        ax = widget.axes
        ax.clear()

        # Extract single DOF data
        if len(displacement.shape) > 1:
            u = displacement[:, dof]
            v = velocity[:, dof]
        else:
            u = displacement
            v = velocity

        ax.plot(u, v, color=THEME["BLUE"], linewidth=1.0, alpha=0.8)
        ax.scatter(u[0], v[0], color=THEME["GREEN"], s=50, zorder=5, label='Start')
        ax.scatter(u[-1], v[-1], color=THEME["RED"], s=50, zorder=5, label='End')

        ax.set_xlabel("Displacement (m)")
        ax.set_ylabel("Velocity (m/s)")
        ax.set_title(title)
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)

        widget.canvas._apply_theme()
        widget.draw()

    @staticmethod
    def plot_frequency_spectrum(
        widget: PlotWidget,
        frequencies: np.ndarray,
        amplitudes: np.ndarray,
        title: str = "Frequency Spectrum"
    ):
        """
        Plot frequency spectrum (FFT).

        Args:
            widget: PlotWidget to draw on
            frequencies: Frequency array (Hz)
            amplitudes: Amplitude array
            title: Plot title
        """
        ax = widget.axes
        ax.clear()

        ax.plot(frequencies, amplitudes, color=THEME["BLUE"], linewidth=1.5)
        ax.fill_between(frequencies, amplitudes, alpha=0.3, color=THEME["BLUE"])

        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Amplitude")
        ax.set_title(title)
        ax.grid(True, alpha=0.3)

        widget.canvas._apply_theme()
        widget.draw()

    @staticmethod
    def plot_natural_frequencies(
        widget: PlotWidget,
        frequencies: List[float],
        title: str = "Natural Frequencies"
    ):
        """
        Plot bar chart of natural frequencies.

        Args:
            widget: PlotWidget to draw on
            frequencies: List of natural frequencies (Hz)
            title: Plot title
        """
        ax = widget.axes
        ax.clear()

        n = len(frequencies)
        modes = list(range(1, n + 1))

        bars = ax.bar(modes, frequencies, color=THEME["BLUE"], alpha=0.8)

        # Add value labels on bars
        for bar, freq in zip(bars, frequencies):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(frequencies) * 0.02,
                f'{freq:.1f}',
                ha='center',
                va='bottom',
                color=THEME["TEXT"],
                fontsize=9
            )

        ax.set_xlabel("Mode Number")
        ax.set_ylabel("Frequency (Hz)")
        ax.set_title(title)
        ax.set_xticks(modes)
        ax.grid(True, alpha=0.3, axis='y')

        widget.canvas._apply_theme()
        widget.draw()

    @staticmethod
    def plot_mode_shape(
        widget: PlotWidget,
        mode_shape: np.ndarray,
        mode_number: int = 1,
        frequency: Optional[float] = None
    ):
        """
        Plot mode shape.

        Args:
            widget: PlotWidget to draw on
            mode_shape: Mode shape vector
            mode_number: Mode number for title
            frequency: Optional frequency for title
        """
        ax = widget.axes
        ax.clear()

        n_dof = len(mode_shape)
        dofs = list(range(1, n_dof + 1))

        # Plot mode shape as a line
        ax.plot(dofs, mode_shape, 'o-', color=THEME["BLUE"], linewidth=2, markersize=8)
        ax.axhline(y=0, color=THEME["SURFACE2"], linestyle='-', linewidth=1)

        # Fill between zero and mode shape
        ax.fill_between(dofs, mode_shape, 0, alpha=0.3, color=THEME["BLUE"])

        title = f"Mode Shape {mode_number}"
        if frequency is not None:
            title += f" (f = {frequency:.2f} Hz)"

        ax.set_xlabel("DOF")
        ax.set_ylabel("Normalized Amplitude")
        ax.set_title(title)
        ax.set_xticks(dofs)
        ax.grid(True, alpha=0.3)

        widget.canvas._apply_theme()
        widget.draw()

    @staticmethod
    def plot_energy(
        widget: PlotWidget,
        time: np.ndarray,
        kinetic: np.ndarray,
        potential: np.ndarray,
        dissipated: Optional[np.ndarray] = None,
        title: str = "Energy Time History"
    ):
        """
        Plot energy components over time.

        Args:
            widget: PlotWidget to draw on
            time: Time array
            kinetic: Kinetic energy array
            potential: Potential energy array
            dissipated: Optional dissipated energy array
            title: Plot title
        """
        ax = widget.axes
        ax.clear()

        ax.plot(time, kinetic, color=THEME["BLUE"], label="Kinetic", linewidth=1.5)
        ax.plot(time, potential, color=THEME["GREEN"], label="Potential", linewidth=1.5)
        ax.plot(time, kinetic + potential, color=THEME["MAUVE"],
                label="Total", linewidth=2, linestyle='--')

        if dissipated is not None:
            ax.plot(time, dissipated, color=THEME["RED"], label="Dissipated", linewidth=1.5)

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Energy (J)")
        ax.set_title(title)
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)

        widget.canvas._apply_theme()
        widget.draw()

    @staticmethod
    def plot_comparison(
        widget: PlotWidget,
        x_data: np.ndarray,
        y_datasets: Dict[str, np.ndarray],
        xlabel: str = "X",
        ylabel: str = "Y",
        title: str = "Comparison"
    ):
        """
        Plot multiple datasets for comparison.

        Args:
            widget: PlotWidget to draw on
            x_data: Common X array
            y_datasets: Dict mapping label to Y array
            xlabel: X-axis label
            ylabel: Y-axis label
            title: Plot title
        """
        ax = widget.axes
        ax.clear()

        for i, (label, y) in enumerate(y_datasets.items()):
            color = LINE_COLORS[i % len(LINE_COLORS)]
            ax.plot(x_data, y, color=color, label=label, linewidth=1.5)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)

        widget.canvas._apply_theme()
        widget.draw()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_plot_widget(parent=None, toolbar=True) -> PlotWidget:
    """Create a plot widget with standard settings."""
    return PlotWidget(parent, toolbar=toolbar)


def apply_dark_theme():
    """Apply dark theme to matplotlib globally."""
    plt.rcParams.update(PLOT_STYLE)


# =============================================================================
# PLOT EDITOR WINDOW
# =============================================================================

from PyQt6.QtWidgets import (
    QMainWindow, QDockWidget, QGroupBox, QFormLayout, QHBoxLayout,
    QDoubleSpinBox, QSpinBox, QComboBox, QCheckBox, QPushButton,
    QLineEdit, QColorDialog, QFileDialog, QLabel, QScrollArea,
    QFrame, QSlider, QTabWidget, QTextEdit, QMessageBox
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import pyqtSignal
import csv


class PlotEditorWindow(QMainWindow):
    """
    Standalone window for displaying and editing plots.

    Features:
    - Large plot canvas with navigation toolbar
    - Side panel with comprehensive editing options
    - Export to PNG, PDF, SVG, CSV
    - Real-time plot updates
    """

    # Signal emitted when window is closed
    closed = pyqtSignal()

    def __init__(self, figure=None, title="Plot Editor", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Plot Editor - {title}")
        self.setMinimumSize(1200, 800)

        # Store the original figure or create new one
        self._original_figure = figure
        self._plot_title = title
        self._data_cache = {}  # Store data for CSV export

        self._setup_ui()
        self._apply_theme()

        # If figure provided, copy it to our canvas
        if figure is not None:
            self._copy_figure(figure)

    def _setup_ui(self):
        """Setup the window UI."""
        # Central widget - plot canvas
        self.plot_widget = PlotWidget(self, width=10, height=8, dpi=100, toolbar=True)
        self.setCentralWidget(self.plot_widget)

        # Right dock - editing panel
        self._setup_editor_dock()

    def _setup_editor_dock(self):
        """Setup the editor dock widget with all options."""
        dock = QDockWidget("Plot Editor", self)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        dock.setMinimumWidth(280)
        dock.setMaximumWidth(400)

        # Scroll area for editor content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(8, 8, 8, 8)
        editor_layout.setSpacing(8)

        # === LABELS GROUP ===
        labels_group = QGroupBox("Labels && Title")
        labels_layout = QFormLayout(labels_group)
        labels_layout.setSpacing(6)

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Plot title")
        self.title_edit.textChanged.connect(self._update_title)

        self.xlabel_edit = QLineEdit()
        self.xlabel_edit.setPlaceholderText("X-axis label")
        self.xlabel_edit.textChanged.connect(self._update_xlabel)

        self.ylabel_edit = QLineEdit()
        self.ylabel_edit.setPlaceholderText("Y-axis label")
        self.ylabel_edit.textChanged.connect(self._update_ylabel)

        labels_layout.addRow("Title:", self.title_edit)
        labels_layout.addRow("X Label:", self.xlabel_edit)
        labels_layout.addRow("Y Label:", self.ylabel_edit)

        editor_layout.addWidget(labels_group)

        # === LINE STYLE GROUP ===
        line_group = QGroupBox("Line Style")
        line_layout = QFormLayout(line_group)
        line_layout.setSpacing(6)

        self.linewidth_spin = QDoubleSpinBox()
        self.linewidth_spin.setRange(0.5, 10.0)
        self.linewidth_spin.setValue(2.0)
        self.linewidth_spin.setSingleStep(0.5)
        self.linewidth_spin.valueChanged.connect(self._update_linewidth)

        self.linestyle_combo = QComboBox()
        self.linestyle_combo.addItems([
            "Solid (-)", "Dashed (--)", "Dotted (:)", "Dash-dot (-.)"
        ])
        self.linestyle_combo.currentIndexChanged.connect(self._update_linestyle)

        self.marker_combo = QComboBox()
        self.marker_combo.addItems([
            "None", "Circle (o)", "Square (s)", "Triangle (^)",
            "Diamond (D)", "Plus (+)", "Cross (x)"
        ])
        self.marker_combo.currentIndexChanged.connect(self._update_markers)

        self.markersize_spin = QDoubleSpinBox()
        self.markersize_spin.setRange(1, 20)
        self.markersize_spin.setValue(6)
        self.markersize_spin.valueChanged.connect(self._update_markersize)

        line_layout.addRow("Width:", self.linewidth_spin)
        line_layout.addRow("Style:", self.linestyle_combo)
        line_layout.addRow("Marker:", self.marker_combo)
        line_layout.addRow("Marker Size:", self.markersize_spin)

        editor_layout.addWidget(line_group)

        # === FONT GROUP ===
        font_group = QGroupBox("Font Settings")
        font_layout = QFormLayout(font_group)
        font_layout.setSpacing(6)

        self.title_fontsize = QSpinBox()
        self.title_fontsize.setRange(8, 24)
        self.title_fontsize.setValue(14)
        self.title_fontsize.valueChanged.connect(self._update_fonts)

        self.label_fontsize = QSpinBox()
        self.label_fontsize.setRange(6, 20)
        self.label_fontsize.setValue(12)
        self.label_fontsize.valueChanged.connect(self._update_fonts)

        self.tick_fontsize = QSpinBox()
        self.tick_fontsize.setRange(6, 16)
        self.tick_fontsize.setValue(10)
        self.tick_fontsize.valueChanged.connect(self._update_fonts)

        font_layout.addRow("Title:", self.title_fontsize)
        font_layout.addRow("Labels:", self.label_fontsize)
        font_layout.addRow("Ticks:", self.tick_fontsize)

        editor_layout.addWidget(font_group)

        # === GRID & LEGEND GROUP ===
        display_group = QGroupBox("Display Options")
        display_layout = QFormLayout(display_group)
        display_layout.setSpacing(6)

        self.grid_check = QCheckBox("Show Grid")
        self.grid_check.setChecked(True)
        self.grid_check.stateChanged.connect(self._update_grid)

        self.legend_check = QCheckBox("Show Legend")
        self.legend_check.setChecked(True)
        self.legend_check.stateChanged.connect(self._update_legend)

        self.legend_loc_combo = QComboBox()
        self.legend_loc_combo.addItems([
            "Best", "Upper Right", "Upper Left", "Lower Right",
            "Lower Left", "Center", "Right", "Center Right"
        ])
        self.legend_loc_combo.currentIndexChanged.connect(self._update_legend)

        self.grid_alpha = QDoubleSpinBox()
        self.grid_alpha.setRange(0, 1)
        self.grid_alpha.setValue(0.3)
        self.grid_alpha.setSingleStep(0.1)
        self.grid_alpha.valueChanged.connect(self._update_grid)

        display_layout.addRow("", self.grid_check)
        display_layout.addRow("Grid Alpha:", self.grid_alpha)
        display_layout.addRow("", self.legend_check)
        display_layout.addRow("Legend Pos:", self.legend_loc_combo)

        editor_layout.addWidget(display_group)

        # === AXIS LIMITS GROUP ===
        limits_group = QGroupBox("Axis Limits")
        limits_layout = QFormLayout(limits_group)
        limits_layout.setSpacing(6)

        self.auto_limits_check = QCheckBox("Auto Limits")
        self.auto_limits_check.setChecked(True)
        self.auto_limits_check.stateChanged.connect(self._toggle_auto_limits)

        self.xmin_spin = QDoubleSpinBox()
        self.xmin_spin.setRange(-1e12, 1e12)
        self.xmin_spin.setDecimals(4)
        self.xmin_spin.setEnabled(False)

        self.xmax_spin = QDoubleSpinBox()
        self.xmax_spin.setRange(-1e12, 1e12)
        self.xmax_spin.setDecimals(4)
        self.xmax_spin.setEnabled(False)

        self.ymin_spin = QDoubleSpinBox()
        self.ymin_spin.setRange(-1e12, 1e12)
        self.ymin_spin.setDecimals(4)
        self.ymin_spin.setEnabled(False)

        self.ymax_spin = QDoubleSpinBox()
        self.ymax_spin.setRange(-1e12, 1e12)
        self.ymax_spin.setDecimals(4)
        self.ymax_spin.setEnabled(False)

        self.apply_limits_btn = QPushButton("Apply")
        self.apply_limits_btn.clicked.connect(self._apply_limits)
        self.apply_limits_btn.setEnabled(False)

        limits_layout.addRow("", self.auto_limits_check)
        limits_layout.addRow("X Min:", self.xmin_spin)
        limits_layout.addRow("X Max:", self.xmax_spin)
        limits_layout.addRow("Y Min:", self.ymin_spin)
        limits_layout.addRow("Y Max:", self.ymax_spin)
        limits_layout.addRow("", self.apply_limits_btn)

        editor_layout.addWidget(limits_group)

        # === EXPORT GROUP ===
        export_group = QGroupBox("Export")
        export_layout = QVBoxLayout(export_group)
        export_layout.setSpacing(6)

        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 600)
        self.dpi_spin.setValue(150)
        self.dpi_spin.setSuffix(" DPI")

        dpi_row = QHBoxLayout()
        dpi_row.addWidget(QLabel("Resolution:"))
        dpi_row.addWidget(self.dpi_spin)
        export_layout.addLayout(dpi_row)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)

        self.export_png_btn = QPushButton("PNG")
        self.export_png_btn.clicked.connect(lambda: self._export("png"))
        self.export_pdf_btn = QPushButton("PDF")
        self.export_pdf_btn.clicked.connect(lambda: self._export("pdf"))
        self.export_svg_btn = QPushButton("SVG")
        self.export_svg_btn.clicked.connect(lambda: self._export("svg"))
        self.export_csv_btn = QPushButton("CSV")
        self.export_csv_btn.clicked.connect(self._export_csv)

        btn_layout.addWidget(self.export_png_btn)
        btn_layout.addWidget(self.export_pdf_btn)
        btn_layout.addWidget(self.export_svg_btn)
        btn_layout.addWidget(self.export_csv_btn)

        export_layout.addLayout(btn_layout)

        editor_layout.addWidget(export_group)

        # Stretch at bottom
        editor_layout.addStretch()

        scroll.setWidget(editor_widget)
        dock.setWidget(scroll)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def _apply_theme(self):
        """Apply dark theme to the window."""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {THEME["BASE"]};
            }}
            QDockWidget {{
                background-color: {THEME["MANTLE"]};
                color: {THEME["TEXT"]};
                font-size: 10pt;
            }}
            QDockWidget::title {{
                background-color: {THEME["SURFACE0"]};
                padding: 6px;
            }}
            QGroupBox {{
                background-color: {THEME["SURFACE0"]};
                border: 1px solid {THEME["SURFACE1"]};
                border-radius: 6px;
                margin-top: 8px;
                padding: 8px;
                color: {THEME["TEXT"]};
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }}
            QLabel {{
                color: {THEME["SUBTEXT"]};
            }}
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                background-color: {THEME["SURFACE1"]};
                color: {THEME["TEXT"]};
                border: 1px solid {THEME["SURFACE2"]};
                border-radius: 4px;
                padding: 4px;
            }}
            QCheckBox {{
                color: {THEME["TEXT"]};
            }}
            QPushButton {{
                background-color: {THEME["SURFACE1"]};
                color: {THEME["TEXT"]};
                border: 1px solid {THEME["SURFACE2"]};
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {THEME["SURFACE2"]};
            }}
            QScrollArea {{
                border: none;
                background-color: {THEME["MANTLE"]};
            }}
        """)

    def _copy_figure(self, source_fig):
        """Copy content from source figure to our canvas."""
        # Get data from source figure
        ax = self.plot_widget.axes
        ax.clear()

        # Copy each line from source
        for src_ax in source_fig.get_axes():
            for line in src_ax.get_lines():
                xdata = line.get_xdata()
                ydata = line.get_ydata()
                label = line.get_label()
                color = line.get_color()
                linestyle = line.get_linestyle()
                linewidth = line.get_linewidth()

                ax.plot(xdata, ydata, label=label, color=color,
                       linestyle=linestyle, linewidth=linewidth)

                # Cache for CSV export
                if not label.startswith('_'):
                    self._data_cache[label] = {'x': xdata, 'y': ydata}

            # Copy title and labels
            self.title_edit.setText(src_ax.get_title())
            self.xlabel_edit.setText(src_ax.get_xlabel())
            self.ylabel_edit.setText(src_ax.get_ylabel())

            # Copy axis limits
            xlim = src_ax.get_xlim()
            ylim = src_ax.get_ylim()
            self.xmin_spin.setValue(xlim[0])
            self.xmax_spin.setValue(xlim[1])
            self.ymin_spin.setValue(ylim[0])
            self.ymax_spin.setValue(ylim[1])

        ax.legend()
        ax.grid(True, alpha=0.3)
        self.plot_widget.canvas._apply_theme()
        self.plot_widget.draw()

    def set_data(self, x_data, y_datasets, xlabel="X", ylabel="Y", title="Plot"):
        """
        Set plot data directly.

        Args:
            x_data: X array
            y_datasets: Dict mapping label to Y array
            xlabel: X-axis label
            ylabel: Y-axis label
            title: Plot title
        """
        ax = self.plot_widget.axes
        ax.clear()

        self._data_cache = {}

        for i, (label, ydata) in enumerate(y_datasets.items()):
            color = LINE_COLORS[i % len(LINE_COLORS)]
            ax.plot(x_data, ydata, label=label, color=color, linewidth=2)
            self._data_cache[label] = {'x': x_data, 'y': ydata}

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

        self.title_edit.setText(title)
        self.xlabel_edit.setText(xlabel)
        self.ylabel_edit.setText(ylabel)

        self.plot_widget.canvas._apply_theme()
        self.plot_widget.draw()

    def _update_title(self, text):
        self.plot_widget.axes.set_title(text, fontsize=self.title_fontsize.value())
        self.plot_widget.draw()

    def _update_xlabel(self, text):
        self.plot_widget.axes.set_xlabel(text, fontsize=self.label_fontsize.value())
        self.plot_widget.draw()

    def _update_ylabel(self, text):
        self.plot_widget.axes.set_ylabel(text, fontsize=self.label_fontsize.value())
        self.plot_widget.draw()

    def _update_linewidth(self, value):
        for line in self.plot_widget.axes.get_lines():
            line.set_linewidth(value)
        self.plot_widget.draw()

    def _update_linestyle(self, index):
        styles = ['-', '--', ':', '-.']
        style = styles[index] if index < len(styles) else '-'
        for line in self.plot_widget.axes.get_lines():
            line.set_linestyle(style)
        self.plot_widget.draw()

    def _update_markers(self, index):
        markers = ['', 'o', 's', '^', 'D', '+', 'x']
        marker = markers[index] if index < len(markers) else ''
        for line in self.plot_widget.axes.get_lines():
            line.set_marker(marker)
        self.plot_widget.draw()

    def _update_markersize(self, value):
        for line in self.plot_widget.axes.get_lines():
            line.set_markersize(value)
        self.plot_widget.draw()

    def _update_fonts(self):
        ax = self.plot_widget.axes
        ax.title.set_fontsize(self.title_fontsize.value())
        ax.xaxis.label.set_fontsize(self.label_fontsize.value())
        ax.yaxis.label.set_fontsize(self.label_fontsize.value())
        ax.tick_params(labelsize=self.tick_fontsize.value())
        self.plot_widget.draw()

    def _update_grid(self):
        ax = self.plot_widget.axes
        ax.grid(self.grid_check.isChecked(), alpha=self.grid_alpha.value())
        self.plot_widget.draw()

    def _update_legend(self):
        ax = self.plot_widget.axes
        if self.legend_check.isChecked():
            loc_map = {
                0: 'best', 1: 'upper right', 2: 'upper left',
                3: 'lower right', 4: 'lower left', 5: 'center',
                6: 'right', 7: 'center right'
            }
            loc = loc_map.get(self.legend_loc_combo.currentIndex(), 'best')
            ax.legend(loc=loc)
        else:
            legend = ax.get_legend()
            if legend:
                legend.remove()
        self.plot_widget.draw()

    def _toggle_auto_limits(self, state):
        enabled = not state
        self.xmin_spin.setEnabled(enabled)
        self.xmax_spin.setEnabled(enabled)
        self.ymin_spin.setEnabled(enabled)
        self.ymax_spin.setEnabled(enabled)
        self.apply_limits_btn.setEnabled(enabled)

        if state:  # Auto limits enabled
            self.plot_widget.axes.autoscale()
            self.plot_widget.draw()

    def _apply_limits(self):
        ax = self.plot_widget.axes
        ax.set_xlim(self.xmin_spin.value(), self.xmax_spin.value())
        ax.set_ylim(self.ymin_spin.value(), self.ymax_spin.value())
        self.plot_widget.draw()

    def _export(self, fmt):
        """Export figure to file."""
        filter_map = {
            'png': 'PNG Image (*.png)',
            'pdf': 'PDF Document (*.pdf)',
            'svg': 'SVG Vector (*.svg)'
        }
        filepath, _ = QFileDialog.getSaveFileName(
            self, f"Export as {fmt.upper()}",
            f"plot.{fmt}", filter_map.get(fmt, f"{fmt.upper()} (*.{fmt})")
        )
        if filepath:
            self.plot_widget.figure.savefig(
                filepath,
                dpi=self.dpi_spin.value(),
                facecolor=THEME["BASE"],
                edgecolor='none',
                bbox_inches='tight'
            )
            QMessageBox.information(self, "Export Complete", f"Saved to:\n{filepath}")

    def _export_csv(self):
        """Export plot data to CSV."""
        if not self._data_cache:
            QMessageBox.warning(self, "No Data", "No data available for export.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Data as CSV", "plot_data.csv", "CSV Files (*.csv)"
        )
        if filepath:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                # Header
                headers = ['X']
                for label in self._data_cache.keys():
                    headers.append(label)
                writer.writerow(headers)

                # Data rows
                first_key = list(self._data_cache.keys())[0]
                x_data = self._data_cache[first_key]['x']
                for i, x in enumerate(x_data):
                    row = [x]
                    for label, data in self._data_cache.items():
                        if i < len(data['y']):
                            row.append(data['y'][i])
                        else:
                            row.append('')
                    writer.writerow(row)

            QMessageBox.information(self, "Export Complete", f"Data saved to:\n{filepath}")

    def closeEvent(self, event):
        """Handle window close event."""
        self.closed.emit()
        super().closeEvent(event)
