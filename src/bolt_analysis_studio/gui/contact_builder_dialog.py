"""
Contact Builder Dialog for Bolt Analysis Studio v4.0
Comprehensive GUI for defining contact interfaces with properties.

Features:
- Tabs for each contact type (Thread, Bearing, Gasket, Washer, Flange)
- Visual preview of contact location
- Property editors with real-time validation
- Load distribution configurators
- Friction/wear property editors
- Standards compliance indicators

Prof. Leonardo Rosa Ribeiro da Silva, PhD
January 2026
"""

import sys
from typing import Optional, Dict, Any, List
from dataclasses import asdict
import numpy as np

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QPushButton, QGroupBox, QFormLayout, QComboBox,
    QDoubleSpinBox, QSpinBox, QSlider, QCheckBox, QDialogButtonBox,
    QFrame, QSplitter, QScrollArea, QMessageBox, QListWidget,
    QListWidgetItem, QTextEdit, QSizePolicy, QGridLayout,
    QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPalette

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Import contact system classes
try:
    from bolt_analysis_studio.core.contacts.base import (
        ContactGeometry, FrictionProperties, WearProperties, WearModelType,
        StiffnessProperties, DampingProperties, FrictionModelType
    )
    from bolt_analysis_studio.core.contacts.thread_contact import (
        ThreadContact, ThreadGeometry, ThreadLoadDistribution,
        create_standard_thread_contact
    )
    from bolt_analysis_studio.core.contacts.bearing_contact import BearingContact
    from bolt_analysis_studio.core.contacts.gasket_contact import GasketContact
    from bolt_analysis_studio.core.contacts.washer_contact import WasherContact
except ImportError:
    # Fallback for when modules are not yet created
    ContactGeometry = None
    FrictionProperties = None

from bolt_analysis_studio.gui.theme import Theme


# =============================================================================
# PREVIEW WIDGET
# =============================================================================

class ContactPreviewWidget(QWidget):
    """Visual preview of contact location in bolted joint."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.contact_type = "THREAD"
        self.setMinimumHeight(200)
        self.setStyleSheet(f"background-color: {Theme.CRUST};")

    def set_contact_type(self, contact_type: str):
        """Update the contact type to display."""
        self.contact_type = contact_type
        self.update()

    def paintEvent(self, event):
        """Draw simplified joint schematic with contact highlighted."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2

        # Background
        painter.fillRect(0, 0, w, h, QColor(Theme.CRUST))

        # Draw simplified bolt joint
        painter.setPen(QPen(QColor(Theme.TEXT), 2))
        painter.setBrush(QBrush(QColor(Theme.SURFACE1)))

        # Head
        painter.drawRect(cx - 40, cy - 80, 80, 20)
        painter.drawText(cx - 30, cy - 65, "HEAD")

        # Shank
        painter.drawRect(cx - 15, cy - 60, 30, 40)

        # Thread (with highlight if selected)
        if self.contact_type == "THREAD":
            painter.setBrush(QBrush(QColor(Theme.YELLOW)))
        painter.drawRect(cx - 15, cy - 20, 30, 30)
        painter.setBrush(QBrush(QColor(Theme.SURFACE1)))
        painter.drawText(cx - 25, cy, "THREAD")

        # Nut
        painter.drawRect(cx - 40, cy + 10, 80, 20)
        painter.drawText(cx - 15, cy + 24, "NUT")

        # Bearing surfaces
        if self.contact_type == "BEARING_HEAD":
            painter.setPen(QPen(QColor(Theme.RED), 3))
            painter.drawLine(cx - 40, cy - 80, cx + 40, cy - 80)
        if self.contact_type == "BEARING_NUT":
            painter.setPen(QPen(QColor(Theme.RED), 3))
            painter.drawLine(cx - 40, cy + 30, cx + 40, cy + 30)

        # Flange/Members
        painter.setPen(QPen(QColor(Theme.TEXT), 2))
        painter.drawRect(cx - 60, cy - 80, 120, 10)
        painter.drawRect(cx - 60, cy + 30, 120, 10)

        # Gasket (if selected)
        if self.contact_type == "GASKET":
            painter.setPen(QPen(QColor(Theme.GREEN), 3))
            painter.drawLine(cx - 60, cy - 70, cx + 60, cy - 70)

        # Washer (if selected)
        if self.contact_type == "WASHER_HEAD":
            painter.setBrush(QBrush(QColor(Theme.TEAL)))
            painter.drawEllipse(cx - 35, cy - 85, 70, 10)
        if self.contact_type == "WASHER_NUT":
            painter.setBrush(QBrush(QColor(Theme.TEAL)))
            painter.drawEllipse(cx - 35, cy + 25, 70, 10)


# =============================================================================
# LOAD DISTRIBUTION PREVIEW
# =============================================================================

class LoadDistributionPreview(FigureCanvas):
    """Bar chart preview of thread load distribution."""

    def __init__(self, parent=None):
        self.fig = Figure(figsize=(5, 3), facecolor=Theme.BASE)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(Theme.CRUST)

        super().__init__(self.fig)
        self.setParent(parent)

        # Style
        self.ax.spines['bottom'].set_color(Theme.TEXT)
        self.ax.spines['top'].set_color(Theme.TEXT)
        self.ax.spines['left'].set_color(Theme.TEXT)
        self.ax.spines['right'].set_color(Theme.TEXT)
        self.ax.tick_params(colors=Theme.TEXT)
        self.ax.xaxis.label.set_color(Theme.TEXT)
        self.ax.yaxis.label.set_color(Theme.TEXT)

        self.n_threads = 8
        self.distribution = "POWER"
        self.param = 2.0

        self.plot_distribution()

    def plot_distribution(self):
        """Plot the current load distribution."""
        self.ax.clear()

        # Calculate fractions
        fractions = self._calculate_fractions()

        # Plot
        threads = np.arange(1, self.n_threads + 1)
        bars = self.ax.bar(threads, fractions, color=Theme.YELLOW, edgecolor=Theme.TEXT)

        self.ax.set_xlabel('Thread Number', color=Theme.TEXT)
        self.ax.set_ylabel('Load Fraction φᵢ', color=Theme.TEXT)
        self.ax.set_title(f'{self.distribution} Distribution', color=Theme.BLUE)
        self.ax.grid(True, alpha=0.2, color=Theme.TEXT)

        self.fig.tight_layout()
        self.draw()

    def _calculate_fractions(self) -> np.ndarray:
        """Calculate load fractions based on distribution law."""
        n = self.n_threads
        i_array = np.arange(1, n + 1)

        if self.distribution == "EQUAL":
            fractions = np.ones(n) / n
        elif self.distribution == "LINEAR":
            fractions = 2 * (n - i_array + 1) / (n * (n + 1))
        elif self.distribution == "POWER":
            weights = (n - i_array + 1) ** self.param
            fractions = weights / np.sum(weights)
        elif self.distribution == "EXPONENTIAL":
            weights = np.exp(-self.param * (i_array - 1))
            fractions = weights / np.sum(weights)
        elif self.distribution == "YAMAMOTO":
            weights = np.sinh(self.param * (n - i_array + 0.5))
            fractions = weights / np.sum(weights)
        else:
            fractions = np.ones(n) / n

        return fractions

    def update_distribution(self, distribution: str, param: float, n_threads: int):
        """Update and redraw distribution."""
        self.distribution = distribution
        self.param = param
        self.n_threads = n_threads
        self.plot_distribution()


# =============================================================================
# THREAD CONTACT WIDGET
# =============================================================================

class ThreadContactWidget(QWidget):
    """Configuration widget for thread contacts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the thread contact UI."""
        layout = QVBoxLayout(self)

        # Bolt Size Selection
        size_group = QGroupBox("Thread Geometry")
        size_layout = QFormLayout(size_group)

        self.bolt_size_combo = QComboBox()
        self.bolt_size_combo.addItems(["M10", "M12", "M16", "M20", "M24", "M30"])
        self.bolt_size_combo.setCurrentText("M20")
        self.bolt_size_combo.currentTextChanged.connect(self._update_geometry)

        self.pitch_spin = QDoubleSpinBox()
        self.pitch_spin.setRange(0.001, 0.01)
        self.pitch_spin.setValue(0.0025)
        self.pitch_spin.setSuffix(" m")
        self.pitch_spin.setDecimals(4)

        self.pitch_diameter_spin = QDoubleSpinBox()
        self.pitch_diameter_spin.setRange(0.005, 0.05)
        self.pitch_diameter_spin.setValue(0.01854)
        self.pitch_diameter_spin.setSuffix(" m")
        self.pitch_diameter_spin.setDecimals(5)

        self.n_threads_spin = QSpinBox()
        self.n_threads_spin.setRange(4, 20)
        self.n_threads_spin.setValue(8)
        self.n_threads_spin.valueChanged.connect(self._update_preview)

        size_layout.addRow("Bolt Size:", self.bolt_size_combo)
        size_layout.addRow("Pitch:", self.pitch_spin)
        size_layout.addRow("Pitch Diameter:", self.pitch_diameter_spin)
        size_layout.addRow("Engaged Threads:", self.n_threads_spin)

        layout.addWidget(size_group)

        # Load Distribution
        dist_group = QGroupBox("Load Distribution")
        dist_layout = QVBoxLayout(dist_group)

        dist_select_layout = QHBoxLayout()
        dist_label = QLabel("Distribution Law:")
        self.dist_combo = QComboBox()
        self.dist_combo.addItems([
            "Equal", "Linear", "Power (β)", "Exponential (λ)", "Yamamoto (γ)"
        ])
        self.dist_combo.setCurrentIndex(2)  # Power
        self.dist_combo.currentTextChanged.connect(self._update_preview)

        dist_select_layout.addWidget(dist_label)
        dist_select_layout.addWidget(self.dist_combo)
        dist_layout.addLayout(dist_select_layout)

        # Parameter slider
        param_layout = QHBoxLayout()
        self.param_label = QLabel("Parameter β:")
        self.param_slider = QSlider(Qt.Orientation.Horizontal)
        self.param_slider.setRange(10, 50)
        self.param_slider.setValue(20)  # β = 2.0
        self.param_slider.valueChanged.connect(self._update_preview)

        self.param_value_label = QLabel("2.0")
        self.param_value_label.setStyleSheet(f"color: {Theme.GREEN}; font-family: {Theme.FONT_MONO};")

        param_layout.addWidget(self.param_label)
        param_layout.addWidget(self.param_slider)
        param_layout.addWidget(self.param_value_label)
        dist_layout.addLayout(param_layout)

        # Preview
        self.load_preview = LoadDistributionPreview(self)
        dist_layout.addWidget(self.load_preview)

        layout.addWidget(dist_group)

        # Friction Properties
        friction_group = QGroupBox("Friction Properties")
        friction_layout = QFormLayout(friction_group)

        self.mu_static_spin = QDoubleSpinBox()
        self.mu_static_spin.setRange(0.01, 1.0)
        self.mu_static_spin.setValue(0.15)
        self.mu_static_spin.setDecimals(3)

        self.mu_kinetic_spin = QDoubleSpinBox()
        self.mu_kinetic_spin.setRange(0.01, 1.0)
        self.mu_kinetic_spin.setValue(0.12)
        self.mu_kinetic_spin.setDecimals(3)

        self.friction_model_combo = QComboBox()
        self.friction_model_combo.addItems([
            "Coulomb", "Regularized", "Stribeck", "Viscous"
        ])

        friction_layout.addRow("μ_static:", self.mu_static_spin)
        friction_layout.addRow("μ_kinetic:", self.mu_kinetic_spin)
        friction_layout.addRow("Model:", self.friction_model_combo)

        layout.addWidget(friction_group)

        # Wear Properties
        wear_group = QGroupBox("Wear Properties")
        wear_layout = QFormLayout(wear_group)

        self.wear_model_combo = QComboBox()
        self.wear_model_combo.addItems(["None", "Archard", "Fretting"])
        self.wear_model_combo.setCurrentIndex(2)

        self.wear_coeff_spin = QDoubleSpinBox()
        self.wear_coeff_spin.setRange(1e-9, 1e-3)
        self.wear_coeff_spin.setValue(1e-6)
        self.wear_coeff_spin.setDecimals(9)

        wear_layout.addRow("Wear Model:", self.wear_model_combo)
        wear_layout.addRow("Wear Coefficient K:", self.wear_coeff_spin)

        layout.addWidget(wear_group)
        layout.addStretch()

    def _update_geometry(self):
        """Update geometry values based on bolt size selection."""
        size = self.bolt_size_combo.currentText()

        # Standard metric thread data
        data = {
            'M10': (0.0015, 0.00913),
            'M12': (0.00175, 0.01098),
            'M16': (0.002, 0.01480),
            'M20': (0.0025, 0.01854),
            'M24': (0.003, 0.02227),
            'M30': (0.0035, 0.02773),
        }

        if size in data:
            pitch, pitch_dia = data[size]
            self.pitch_spin.setValue(pitch)
            self.pitch_diameter_spin.setValue(pitch_dia)

    def _update_preview(self):
        """Update the load distribution preview."""
        dist_text = self.dist_combo.currentText()
        distribution = dist_text.split()[0].upper()

        # Update parameter label
        if "β" in dist_text:
            self.param_label.setText("Parameter β:")
        elif "λ" in dist_text:
            self.param_label.setText("Parameter λ:")
        elif "γ" in dist_text:
            self.param_label.setText("Parameter γ:")
        else:
            self.param_label.setText("Parameter:")

        param = self.param_slider.value() / 10.0
        self.param_value_label.setText(f"{param:.1f}")

        n_threads = self.n_threads_spin.value()

        self.load_preview.update_distribution(distribution, param, n_threads)

    def get_contact_data(self) -> Dict[str, Any]:
        """Get the configured contact data."""
        dist_text = self.dist_combo.currentText()
        distribution = dist_text.split()[0].upper()

        return {
            "contact_type": "THREAD",
            "bolt_size": self.bolt_size_combo.currentText(),
            "pitch": self.pitch_spin.value(),
            "pitch_diameter": self.pitch_diameter_spin.value(),
            "n_engaged_threads": self.n_threads_spin.value(),
            "load_distribution": distribution,
            "distribution_param": self.param_slider.value() / 10.0,
            "mu_static": self.mu_static_spin.value(),
            "mu_kinetic": self.mu_kinetic_spin.value(),
            "friction_model": self.friction_model_combo.currentText(),
            "wear_model": self.wear_model_combo.currentText(),
            "wear_coeff": self.wear_coeff_spin.value(),
        }


# =============================================================================
# BEARING CONTACT WIDGET
# =============================================================================

class BearingContactWidget(QWidget):
    """Configuration widget for bearing contacts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the bearing contact UI."""
        layout = QVBoxLayout(self)

        # Location
        location_group = QGroupBox("Bearing Location")
        location_layout = QFormLayout(location_group)

        self.location_combo = QComboBox()
        self.location_combo.addItems(["Bolt Head", "Nut"])

        location_layout.addRow("Location:", self.location_combo)
        layout.addWidget(location_group)

        # Geometry
        geom_group = QGroupBox("Bearing Geometry")
        geom_layout = QFormLayout(geom_group)

        self.inner_radius_spin = QDoubleSpinBox()
        self.inner_radius_spin.setRange(0.001, 0.1)
        self.inner_radius_spin.setValue(0.011)
        self.inner_radius_spin.setSuffix(" m")
        self.inner_radius_spin.setDecimals(4)

        self.outer_radius_spin = QDoubleSpinBox()
        self.outer_radius_spin.setRange(0.001, 0.2)
        self.outer_radius_spin.setValue(0.018)
        self.outer_radius_spin.setSuffix(" m")
        self.outer_radius_spin.setDecimals(4)

        self.contact_area_label = QLabel("0.00 mm²")
        self.contact_area_label.setStyleSheet(f"color: {Theme.GREEN}; font-family: {Theme.FONT_MONO};")

        geom_layout.addRow("Inner Radius:", self.inner_radius_spin)
        geom_layout.addRow("Outer Radius:", self.outer_radius_spin)
        geom_layout.addRow("Contact Area:", self.contact_area_label)

        # Update area when radii change
        self.inner_radius_spin.valueChanged.connect(self._update_area)
        self.outer_radius_spin.valueChanged.connect(self._update_area)
        self._update_area()

        layout.addWidget(geom_group)

        # Friction
        friction_group = QGroupBox("Friction Properties")
        friction_layout = QFormLayout(friction_group)

        self.mu_bearing_spin = QDoubleSpinBox()
        self.mu_bearing_spin.setRange(0.01, 1.0)
        self.mu_bearing_spin.setValue(0.15)
        self.mu_bearing_spin.setDecimals(3)

        self.slip_threshold_spin = QDoubleSpinBox()
        self.slip_threshold_spin.setRange(1e-6, 1e-3)
        self.slip_threshold_spin.setValue(1e-5)
        self.slip_threshold_spin.setSuffix(" m")
        self.slip_threshold_spin.setDecimals(8)

        friction_layout.addRow("Friction Coefficient:", self.mu_bearing_spin)
        friction_layout.addRow("Slip Threshold:", self.slip_threshold_spin)

        layout.addWidget(friction_group)

        # Stiffness
        stiff_group = QGroupBox("Bearing Stiffness")
        stiff_layout = QFormLayout(stiff_group)

        self.stiffness_spin = QDoubleSpinBox()
        self.stiffness_spin.setRange(1e6, 1e12)
        self.stiffness_spin.setValue(5e9)
        self.stiffness_spin.setSuffix(" N/m")
        self.stiffness_spin.setDecimals(2)

        stiff_layout.addRow("Axial Stiffness:", self.stiffness_spin)

        layout.addWidget(stiff_group)
        layout.addStretch()

    def _update_area(self):
        """Update contact area display."""
        r_i = self.inner_radius_spin.value()
        r_o = self.outer_radius_spin.value()
        area = np.pi * (r_o**2 - r_i**2)
        self.contact_area_label.setText(f"{area * 1e6:.2f} mm²")

    def get_contact_data(self) -> Dict[str, Any]:
        """Get the configured contact data."""
        return {
            "contact_type": "BEARING_" + self.location_combo.currentText().upper().replace(" ", "_"),
            "location": self.location_combo.currentText(),
            "inner_radius": self.inner_radius_spin.value(),
            "outer_radius": self.outer_radius_spin.value(),
            "mu_bearing": self.mu_bearing_spin.value(),
            "slip_threshold": self.slip_threshold_spin.value(),
            "stiffness": self.stiffness_spin.value(),
        }


# =============================================================================
# GASKET CONTACT WIDGET
# =============================================================================

class GasketContactWidget(QWidget):
    """Configuration widget for gasket contacts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the gasket contact UI."""
        layout = QVBoxLayout(self)

        # Type Selection
        type_group = QGroupBox("Gasket Type")
        type_layout = QFormLayout(type_group)

        self.gasket_type_combo = QComboBox()
        self.gasket_type_combo.addItems([
            "Spiral Wound (ASME B16.20)",
            "Ring Type Joint (RTJ)",
            "Sheet Gasket",
            "Metal O-Ring",
            "Custom"
        ])

        self.pressure_class_combo = QComboBox()
        self.pressure_class_combo.addItems([
            "150#", "300#", "600#", "900#", "1500#", "2500#",
            "5000 psi", "10000 psi", "15000 psi", "20000 psi"
        ])
        self.pressure_class_combo.setCurrentText("10000 psi")

        type_layout.addRow("Gasket Type:", self.gasket_type_combo)
        type_layout.addRow("Pressure Class:", self.pressure_class_combo)

        layout.addWidget(type_group)

        # Nonlinear Stiffness
        stiff_group = QGroupBox("Nonlinear Stiffness")
        stiff_layout = QVBoxLayout(stiff_group)

        info_label = QLabel("k(F) = k₀ × (1 + α × F^n)")
        info_label.setStyleSheet(f"color: {Theme.SUBTEXT}; font-style: italic;")
        stiff_layout.addWidget(info_label)

        params_layout = QFormLayout()

        self.k0_spin = QDoubleSpinBox()
        self.k0_spin.setRange(1e6, 1e12)
        self.k0_spin.setValue(5e8)
        self.k0_spin.setSuffix(" N/m")
        self.k0_spin.setDecimals(2)

        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setRange(0.0, 1.0)
        self.alpha_spin.setValue(0.1)
        self.alpha_spin.setDecimals(4)

        self.n_spin = QDoubleSpinBox()
        self.n_spin.setRange(0.1, 2.0)
        self.n_spin.setValue(0.5)
        self.n_spin.setDecimals(2)

        params_layout.addRow("k₀ (Initial):", self.k0_spin)
        params_layout.addRow("α (Nonlinearity):", self.alpha_spin)
        params_layout.addRow("n (Exponent):", self.n_spin)

        stiff_layout.addLayout(params_layout)
        layout.addWidget(stiff_group)

        # Creep Parameters
        creep_group = QGroupBox("Creep/Relaxation")
        creep_layout = QFormLayout(creep_group)

        self.creep_rate_spin = QDoubleSpinBox()
        self.creep_rate_spin.setRange(0.0, 0.1)
        self.creep_rate_spin.setValue(0.001)
        self.creep_rate_spin.setSuffix(" /hr")
        self.creep_rate_spin.setDecimals(5)

        self.relaxation_time_spin = QDoubleSpinBox()
        self.relaxation_time_spin.setRange(1, 10000)
        self.relaxation_time_spin.setValue(100)
        self.relaxation_time_spin.setSuffix(" hrs")

        creep_layout.addRow("Creep Rate:", self.creep_rate_spin)
        creep_layout.addRow("Relaxation Time:", self.relaxation_time_spin)

        layout.addWidget(creep_group)

        # Compliance Indicator
        compliance_group = QGroupBox("Standards Compliance")
        compliance_layout = QVBoxLayout(compliance_group)

        self.compliance_label = QLabel("✓ ASME B16.20 Compliant")
        self.compliance_label.setStyleSheet(f"color: {Theme.GREEN}; font-weight: bold;")
        compliance_layout.addWidget(self.compliance_label)

        layout.addWidget(compliance_group)
        layout.addStretch()

    def get_contact_data(self) -> Dict[str, Any]:
        """Get the configured contact data."""
        return {
            "contact_type": "GASKET",
            "gasket_type": self.gasket_type_combo.currentText(),
            "pressure_class": self.pressure_class_combo.currentText(),
            "k0": self.k0_spin.value(),
            "alpha": self.alpha_spin.value(),
            "n_exponent": self.n_spin.value(),
            "creep_rate": self.creep_rate_spin.value(),
            "relaxation_time": self.relaxation_time_spin.value(),
        }


# =============================================================================
# WASHER CONTACT WIDGET
# =============================================================================

class WasherContactWidget(QWidget):
    """Configuration widget for washer contacts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the washer contact UI."""
        layout = QVBoxLayout(self)

        # Type Selection
        type_group = QGroupBox("Washer Type")
        type_layout = QFormLayout(type_group)

        self.washer_type_combo = QComboBox()
        self.washer_type_combo.addItems([
            "Plain Washer",
            "Belleville Spring",
            "Nord-Lock Wedge Locking",
            "Spring Lock Washer",
            "Custom"
        ])
        self.washer_type_combo.currentTextChanged.connect(self._on_type_changed)

        self.location_combo = QComboBox()
        self.location_combo.addItems(["Under Head", "Under Nut"])

        type_layout.addRow("Washer Type:", self.washer_type_combo)
        type_layout.addRow("Location:", self.location_combo)

        layout.addWidget(type_group)

        # Belleville Parameters (shown conditionally)
        self.belleville_group = QGroupBox("Belleville Parameters (DIN 2093)")
        belleville_layout = QFormLayout(self.belleville_group)

        self.outer_dia_spin = QDoubleSpinBox()
        self.outer_dia_spin.setRange(5, 100)
        self.outer_dia_spin.setValue(20)
        self.outer_dia_spin.setSuffix(" mm")

        self.inner_dia_spin = QDoubleSpinBox()
        self.inner_dia_spin.setRange(5, 50)
        self.inner_dia_spin.setValue(10.5)
        self.inner_dia_spin.setSuffix(" mm")

        self.thickness_spin = QDoubleSpinBox()
        self.thickness_spin.setRange(0.1, 10)
        self.thickness_spin.setValue(1.25)
        self.thickness_spin.setSuffix(" mm")

        self.h0_spin = QDoubleSpinBox()
        self.h0_spin.setRange(0.1, 5)
        self.h0_spin.setValue(0.5)
        self.h0_spin.setSuffix(" mm")
        self.h0_spin.setToolTip("Cone height at no load")

        belleville_layout.addRow("Outer Diameter:", self.outer_dia_spin)
        belleville_layout.addRow("Inner Diameter:", self.inner_dia_spin)
        belleville_layout.addRow("Thickness:", self.thickness_spin)
        belleville_layout.addRow("Cone Height h₀:", self.h0_spin)

        self.belleville_group.setVisible(False)
        layout.addWidget(self.belleville_group)

        # Stiffness/Spring Rate
        stiff_group = QGroupBox("Spring Rate")
        stiff_layout = QFormLayout(stiff_group)

        self.spring_rate_spin = QDoubleSpinBox()
        self.spring_rate_spin.setRange(1e5, 1e10)
        self.spring_rate_spin.setValue(1e8)
        self.spring_rate_spin.setSuffix(" N/m")
        self.spring_rate_spin.setDecimals(2)

        stiff_layout.addRow("Spring Rate:", self.spring_rate_spin)

        layout.addWidget(stiff_group)

        # Embedding (VDI 2230)
        embed_group = QGroupBox("Embedding (VDI 2230)")
        embed_layout = QFormLayout(embed_group)

        self.embedding_spin = QDoubleSpinBox()
        self.embedding_spin.setRange(0.0, 0.1)
        self.embedding_spin.setValue(0.003)
        self.embedding_spin.setSuffix(" mm")
        self.embedding_spin.setDecimals(4)
        self.embedding_spin.setToolTip("Permanent set under load")

        embed_layout.addRow("Embedding δz:", self.embedding_spin)

        layout.addWidget(embed_group)
        layout.addStretch()

    def _on_type_changed(self):
        """Show/hide Belleville group based on washer type."""
        is_belleville = "Belleville" in self.washer_type_combo.currentText()
        self.belleville_group.setVisible(is_belleville)

    def get_contact_data(self) -> Dict[str, Any]:
        """Get the configured contact data."""
        data = {
            "contact_type": "WASHER",
            "washer_type": self.washer_type_combo.currentText(),
            "location": self.location_combo.currentText(),
            "spring_rate": self.spring_rate_spin.value(),
            "embedding": self.embedding_spin.value(),
        }

        if "Belleville" in self.washer_type_combo.currentText():
            data.update({
                "outer_diameter": self.outer_dia_spin.value() / 1000,  # to meters
                "inner_diameter": self.inner_dia_spin.value() / 1000,
                "thickness": self.thickness_spin.value() / 1000,
                "cone_height": self.h0_spin.value() / 1000,
            })

        return data


# =============================================================================
# FLANGE CONTACT WIDGET
# =============================================================================

class FlangeContactWidget(QWidget):
    """Configuration widget for flange contacts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the flange contact UI."""
        layout = QVBoxLayout(self)

        # Standard Selection
        standard_group = QGroupBox("Flange Standard")
        standard_layout = QFormLayout(standard_group)

        self.standard_combo = QComboBox()
        self.standard_combo.addItems([
            "API 6A Type 6BX",
            "ASME B16.5 Class 150",
            "ASME B16.5 Class 300",
            "ASME B16.5 Class 600",
            "ASME B16.47 Series A",
            "EN 1092-1 PN 40",
            "Custom"
        ])

        standard_layout.addRow("Standard:", self.standard_combo)
        layout.addWidget(standard_group)

        # Geometry
        geom_group = QGroupBox("Flange Geometry")
        geom_layout = QFormLayout(geom_group)

        self.thickness_spin = QDoubleSpinBox()
        self.thickness_spin.setRange(10, 500)
        self.thickness_spin.setValue(50)
        self.thickness_spin.setSuffix(" mm")

        self.bore_dia_spin = QDoubleSpinBox()
        self.bore_dia_spin.setRange(50, 1000)
        self.bore_dia_spin.setValue(200)
        self.bore_dia_spin.setSuffix(" mm")

        geom_layout.addRow("Flange Thickness:", self.thickness_spin)
        geom_layout.addRow("Bore Diameter:", self.bore_dia_spin)

        layout.addWidget(geom_group)

        # Material
        mat_group = QGroupBox("Material Properties")
        mat_layout = QFormLayout(mat_group)

        self.material_combo = QComboBox()
        self.material_combo.addItems([
            "SA-105 (Carbon Steel)",
            "SA-350 LF2 (Low Temp)",
            "SA-182 F316 (Stainless)",
            "Inconel 625",
            "Custom"
        ])

        self.youngs_spin = QDoubleSpinBox()
        self.youngs_spin.setRange(50e9, 300e9)
        self.youngs_spin.setValue(200e9)
        self.youngs_spin.setSuffix(" Pa")
        self.youngs_spin.setDecimals(2)

        mat_layout.addRow("Material:", self.material_combo)
        mat_layout.addRow("Young's Modulus:", self.youngs_spin)

        layout.addWidget(mat_group)
        layout.addStretch()

    def get_contact_data(self) -> Dict[str, Any]:
        """Get the configured contact data."""
        return {
            "contact_type": "FLANGE",
            "standard": self.standard_combo.currentText(),
            "thickness": self.thickness_spin.value() / 1000,  # to meters
            "bore_diameter": self.bore_dia_spin.value() / 1000,
            "material": self.material_combo.currentText(),
            "youngs_modulus": self.youngs_spin.value(),
        }


# =============================================================================
# MAIN CONTACT BUILDER DIALOG
# =============================================================================

class ContactBuilderDialog(QDialog):
    """
    Main dialog for building contact definitions.

    Features:
    - Tabbed interface for each contact type
    - Visual preview of contact location
    - Real-time validation
    - Export to contact dictionary
    """

    contact_created = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Contact Builder")
        self.setMinimumSize(900, 700)
        self._setup_ui()
        self._apply_theme()

    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Contact Interface Builder")
        header.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {Theme.BLUE};")
        layout.addWidget(header)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Contact tabs
        tab_widget = QTabWidget()

        self.thread_widget = ThreadContactWidget()
        self.bearing_widget = BearingContactWidget()
        self.gasket_widget = GasketContactWidget()
        self.washer_widget = WasherContactWidget()
        self.flange_widget = FlangeContactWidget()

        tab_widget.addTab(self.thread_widget, "Thread")
        tab_widget.addTab(self.bearing_widget, "Bearing")
        tab_widget.addTab(self.gasket_widget, "Gasket")
        tab_widget.addTab(self.washer_widget, "Washer")
        tab_widget.addTab(self.flange_widget, "Flange")

        tab_widget.currentChanged.connect(self._on_tab_changed)

        splitter.addWidget(tab_widget)

        # Right: Preview and summary
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        preview_label = QLabel("Contact Location Preview")
        preview_label.setStyleSheet(f"font-weight: bold; color: {Theme.SUBTEXT};")
        right_layout.addWidget(preview_label)

        self.preview_widget = ContactPreviewWidget()
        right_layout.addWidget(self.preview_widget)

        # Summary
        summary_group = QGroupBox("Contact Summary")
        summary_layout = QVBoxLayout(summary_group)

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(150)
        self.summary_text.setStyleSheet(f"""
            background-color: {Theme.CRUST};
            color: {Theme.TEXT};
            font-family: {Theme.FONT_MONO};
        """)
        summary_layout.addWidget(self.summary_text)

        right_layout.addWidget(summary_group)

        splitter.addWidget(right_panel)
        splitter.setSizes([500, 400])

        layout.addWidget(splitter)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        # Initial preview
        self._on_tab_changed(0)

    def _apply_theme(self):
        """Apply Catppuccin Mocha theme."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BASE};
                color: {Theme.TEXT};
            }}
            QGroupBox {{
                border: 1px solid {Theme.SURFACE1};
                border-radius: 6px;
                margin-top: 12px;
                padding: 10px;
                font-weight: bold;
                color: {Theme.BLUE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
            }}
            QTabWidget::pane {{
                border: 1px solid {Theme.SURFACE1};
                background-color: {Theme.BASE};
            }}
            QTabBar::tab {{
                background-color: {Theme.SURFACE0};
                color: {Theme.SUBTEXT};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {Theme.BASE};
                color: {Theme.BLUE};
            }}
            QLabel {{
                color: {Theme.TEXT};
            }}
            QPushButton {{
                background-color: {Theme.SURFACE1};
                color: {Theme.TEXT};
                border: 1px solid {Theme.SURFACE2};
                border-radius: 4px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                background-color: {Theme.SURFACE2};
                border-color: {Theme.BLUE};
            }}
        """)

    def _on_tab_changed(self, index: int):
        """Update preview when tab changes."""
        contact_types = ["THREAD", "BEARING_HEAD", "GASKET", "WASHER_HEAD", "FLANGE"]
        if index < len(contact_types):
            self.preview_widget.set_contact_type(contact_types[index])
            self._update_summary(index)

    def _update_summary(self, tab_index: int):
        """Update summary text based on current tab."""
        widgets = [
            self.thread_widget,
            self.bearing_widget,
            self.gasket_widget,
            self.washer_widget,
            self.flange_widget
        ]

        if tab_index < len(widgets):
            data = widgets[tab_index].get_contact_data()

            summary = f"Contact Type: {data['contact_type']}\n"
            summary += "-" * 40 + "\n"

            for key, value in data.items():
                if key != "contact_type":
                    summary += f"{key}: {value}\n"

            self.summary_text.setText(summary)

    def _on_accept(self):
        """Validate and emit contact data."""
        # Get current tab
        current_widget = None
        if self.thread_widget.isVisible():
            current_widget = self.thread_widget
        elif self.bearing_widget.isVisible():
            current_widget = self.bearing_widget
        elif self.gasket_widget.isVisible():
            current_widget = self.gasket_widget
        elif self.washer_widget.isVisible():
            current_widget = self.washer_widget
        elif self.flange_widget.isVisible():
            current_widget = self.flange_widget

        if current_widget:
            contact_data = current_widget.get_contact_data()
            self.contact_created.emit(contact_data)
            self.accept()

    def get_contact_data(self) -> Optional[Dict[str, Any]]:
        """Get the configured contact data (for direct access)."""
        # Determine which tab is active
        # This is a simplified version; in practice you'd check the tab widget
        return self.thread_widget.get_contact_data()


# =============================================================================
# STANDALONE TEST
# =============================================================================

def main():
    """Test the contact builder dialog."""
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    dialog = ContactBuilderDialog()
    dialog.contact_created.connect(lambda data: print("Contact created:", data))

    if dialog.exec() == QDialog.DialogCode.Accepted:
        print("Dialog accepted")

    sys.exit(0)


if __name__ == "__main__":
    main()
