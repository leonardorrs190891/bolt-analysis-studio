"""
Enhanced Similitude Tab for Bolt Loosening Analysis
====================================================

Integrates the loosening similitude model into the MSD Builder GUI.

Features:
1. Multi-Bolt to Single-Bolt Reduction
2. Geometric Scaling with Loosening Preservation
3. Π-Group Analysis for Loosening Behavior
4. Loosening Curve Visualization
5. Transfer to MSD Builder

Bolt Analysis Studio v4.0
Prof. Leonardo Rosa Ribeiro da Silva, PhD
January 2026
"""

from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox,
    QFormLayout, QLabel, QPushButton, QSpinBox, QDoubleSpinBox,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QTextEdit, QFrame, QMessageBox,
    QFileDialog, QCheckBox, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush, QFont

# Import visualization
try:
    from bolt_analysis_studio.visualization.plot_manager import PlotWidget, PlotEditorWindow
    HAS_PLOT_WIDGET = True
except ImportError:
    HAS_PLOT_WIDGET = False
    PlotEditorWindow = None

# Import similitude models
try:
    from bolt_analysis_studio.core.similitude.loosening_similitude import (
        MultiBoltConfig, EquivalentSingleBolt, ScaledLooseningModel,
        LooseningPiGroup, LooseningSimlitudeAnalysis,
        reduce_multi_bolt_to_single, create_scaled_loosening_model,
        create_msd_elements_from_equivalent, create_msd_elements_from_scaled,
        LoadingPattern, CycleScalingMode,
        assess_pitch_mismatch, compute_bolt_load_factors,
        get_cycle_scaling_info
    )
    HAS_SIMILITUDE = True
except ImportError:
    HAS_SIMILITUDE = False

# Import expanded bolt database
try:
    from bolt_analysis_studio.core.similitude.similitude import (
        find_standard_bolt_size, get_available_standards,
        scale_factor_sensitivity, verify_dynamic_similitude, PrototypeData
    )
    HAS_BOLT_DB = True
except ImportError:
    HAS_BOLT_DB = False

from bolt_analysis_studio.gui.theme import Theme


PRESET_SCALES: List[Tuple[float, str]] = [
    (0.5, "1:2"),
    (0.25, "1:4"),
    (0.125, "1:8"),
    (0.1, "1:10"),
]


# =============================================================================
# MULTI-BOLT REDUCTION PANEL
# =============================================================================

class MultiBoltReductionPanel(QWidget):
    """Panel for multi-bolt to single-bolt reduction."""

    reduction_computed = pyqtSignal(object)  # Emits EquivalentSingleBolt
    transfer_requested = pyqtSignal(dict)     # Emits MSD element parameters

    def __init__(self, parent=None):
        super().__init__(parent)
        self.equivalent_model: Optional[EquivalentSingleBolt] = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Theme.SPACING_XS, Theme.SPACING_XS, Theme.SPACING_XS, Theme.SPACING_XS)
        layout.setSpacing(Theme.SPACING_XS)

        # Header
        self._header = QLabel("Multi-Bolt to Single-Bolt Reduction")
        self._header.setStyleSheet(f"font-size: {Theme.FONT_SIZE_HEADING}pt; font-weight: bold; color: {Theme.BLUE};")
        layout.addWidget(self._header)

        # Sub-tabs
        self.sub_tabs = QTabWidget()
        self.sub_tabs.setDocumentMode(True)
        self.sub_tabs.setUsesScrollButtons(True)
        self.sub_tabs.setElideMode(Qt.TextElideMode.ElideNone)

        # =================================================================
        # Sub-tab 1: Parameters
        # =================================================================
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        params_layout.setContentsMargins(8, 8, 8, 8)
        params_layout.setSpacing(10)

        self._desc = QLabel("Convert n-bolt flange joint to equivalent single bolt\n"
                            "preserving loosening behavior (same F/F₀ vs N curve)")
        self._desc.setStyleSheet(f"color: {Theme.SUBTEXT};")
        self._desc.setWordWrap(True)
        params_layout.addWidget(self._desc)

        # Input parameters group
        input_group = QGroupBox("Joint Parameters")
        input_layout = QFormLayout(input_group)
        input_layout.setSpacing(6)
        input_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)

        self.n_bolts_spin = QSpinBox()
        self.n_bolts_spin.setRange(2, 128)
        self.n_bolts_spin.setValue(8)
        self.n_bolts_spin.setMinimumWidth(Theme.SPINBOX_MIN_WIDTH)
        self.n_bolts_spin.setToolTip("Number of bolts in the circular pattern")
        input_layout.addRow("Number of bolts (n):", self.n_bolts_spin)

        self.diameter_spin = QDoubleSpinBox()
        self.diameter_spin.setRange(3, 100)
        self.diameter_spin.setValue(24.0)
        self.diameter_spin.setSuffix(" mm")
        self.diameter_spin.setDecimals(1)
        self.diameter_spin.setMinimumWidth(Theme.SPINBOX_MIN_WIDTH)
        input_layout.addRow("Bolt diameter (d):", self.diameter_spin)

        self.pitch_spin = QDoubleSpinBox()
        self.pitch_spin.setRange(0.5, 10)
        self.pitch_spin.setValue(3.0)
        self.pitch_spin.setSuffix(" mm")
        self.pitch_spin.setDecimals(2)
        self.pitch_spin.setMinimumWidth(Theme.SPINBOX_MIN_WIDTH)
        input_layout.addRow("Thread pitch (p):", self.pitch_spin)

        self.grip_spin = QDoubleSpinBox()
        self.grip_spin.setRange(10, 500)
        self.grip_spin.setValue(100.0)
        self.grip_spin.setSuffix(" mm")
        self.grip_spin.setMinimumWidth(Theme.SPINBOX_MIN_WIDTH)
        input_layout.addRow("Grip length (L):", self.grip_spin)

        self.preload_spin = QDoubleSpinBox()
        self.preload_spin.setRange(1, 5000)
        self.preload_spin.setValue(160.0)
        self.preload_spin.setSuffix(" kN")
        self.preload_spin.setDecimals(1)
        self.preload_spin.setMinimumWidth(Theme.SPINBOX_MIN_WIDTH)
        input_layout.addRow("Preload per bolt:", self.preload_spin)

        self.trans_force_spin = QDoubleSpinBox()
        self.trans_force_spin.setRange(0, 500)
        self.trans_force_spin.setValue(15.0)
        self.trans_force_spin.setSuffix(" kN")
        self.trans_force_spin.setDecimals(1)
        self.trans_force_spin.setMinimumWidth(Theme.SPINBOX_MIN_WIDTH)
        input_layout.addRow("Transverse force:", self.trans_force_spin)

        self.bcd_spin = QDoubleSpinBox()
        self.bcd_spin.setRange(50, 2000)
        self.bcd_spin.setValue(200.0)
        self.bcd_spin.setSuffix(" mm")
        self.bcd_spin.setMinimumWidth(Theme.SPINBOX_MIN_WIDTH)
        input_layout.addRow("Bolt circle diameter:", self.bcd_spin)

        self.mu_thread_spin = QDoubleSpinBox()
        self.mu_thread_spin.setRange(0.05, 0.5)
        self.mu_thread_spin.setValue(0.12)
        self.mu_thread_spin.setDecimals(3)
        self.mu_thread_spin.setMinimumWidth(Theme.SPINBOX_MIN_WIDTH)
        input_layout.addRow("μ_thread:", self.mu_thread_spin)

        self.mu_bearing_spin = QDoubleSpinBox()
        self.mu_bearing_spin.setRange(0.05, 0.5)
        self.mu_bearing_spin.setValue(0.15)
        self.mu_bearing_spin.setDecimals(3)
        self.mu_bearing_spin.setMinimumWidth(Theme.SPINBOX_MIN_WIDTH)
        input_layout.addRow("μ_bearing:", self.mu_bearing_spin)

        # LS3: Loading pattern selector (M7/MS1)
        self.loading_pattern_combo = QComboBox()
        for pattern in LoadingPattern if HAS_SIMILITUDE else []:
            self.loading_pattern_combo.addItem(pattern.value.title(), pattern)
        self.loading_pattern_combo.setToolTip(
            "Loading pattern affects bolt load distribution.\n"
            "MOMENT: most-loaded bolt sees 2x average\n"
            "SHEAR: most-loaded bolt sees 1.5x average")
        input_layout.addRow("Loading Pattern:", self.loading_pattern_combo)

        params_layout.addWidget(input_group)

        # LS1: Auto-recompute checkbox
        self.auto_recompute_check = QCheckBox("Auto-recompute on parameter change")
        self.auto_recompute_check.setChecked(False)
        self.auto_recompute_check.setToolTip("Automatically recompute when any parameter changes")
        params_layout.addWidget(self.auto_recompute_check)

        # Connect auto-recompute signals
        for spin in [self.n_bolts_spin, self.diameter_spin, self.pitch_spin,
                     self.grip_spin, self.preload_spin, self.trans_force_spin,
                     self.bcd_spin, self.mu_thread_spin, self.mu_bearing_spin]:
            spin.valueChanged.connect(self._on_param_changed)
        self.loading_pattern_combo.currentIndexChanged.connect(self._on_param_changed)

        # BUG-06/U1 fix: Compute button also in Parameters sub-tab
        compute_btn_params = QPushButton("▶ Compute Equivalent Single Bolt")
        compute_btn_params.setObjectName("primary")
        compute_btn_params.setMinimumHeight(Theme.BUTTON_MIN_HEIGHT_PRIMARY)
        compute_btn_params.clicked.connect(self._compute_reduction)
        params_layout.addWidget(compute_btn_params)

        params_layout.addStretch()

        params_scroll = QScrollArea()
        params_scroll.setWidgetResizable(True)
        params_scroll.setFrameShape(QFrame.Shape.NoFrame)
        params_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        params_scroll.setWidget(params_widget)
        self.sub_tabs.addTab(params_scroll, "Parameters")

        # =================================================================
        # Sub-tab 2: Results
        # =================================================================
        results_widget = QWidget()
        results_vlayout = QVBoxLayout(results_widget)
        results_vlayout.setContentsMargins(8, 8, 8, 8)
        results_vlayout.setSpacing(10)

        # Compute button
        compute_btn = QPushButton("Compute Equivalent Single Bolt")
        compute_btn.setObjectName("primary")
        compute_btn.clicked.connect(self._compute_reduction)
        results_vlayout.addWidget(compute_btn)

        # Results group
        results_group = QGroupBox("Equivalent Single-Bolt Model")
        results_group_layout = QVBoxLayout(results_group)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Parameter", "Original", "Equivalent"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setRowCount(8)

        params = ["Diameter (d)", "Pitch (p)", "Preload (F_p)", "Stress Area (A_t)",
                  "k_bolt", "k_member", "Stiffness Ratio (Phi)", "Pi-Group Quality"]
        self.results_table.setUpdatesEnabled(False)
        self.results_table.blockSignals(True)
        try:
            for i, param in enumerate(params):
                self.results_table.setItem(i, 0, QTableWidgetItem(param))
                self.results_table.setItem(i, 1, QTableWidgetItem("-"))
                self.results_table.setItem(i, 2, QTableWidgetItem("-"))
        finally:
            self.results_table.blockSignals(False)
            self.results_table.setUpdatesEnabled(True)

        results_group_layout.addWidget(self.results_table)
        results_vlayout.addWidget(results_group)

        # Quality indicator
        self.quality_label = QLabel("Quality: -")
        self.quality_label.setStyleSheet(f"font-weight: bold; color: {Theme.SUBTEXT};")
        results_vlayout.addWidget(self.quality_label)

        results_vlayout.addStretch()

        self.sub_tabs.addTab(results_widget, "Results")

        # =================================================================
        # Sub-tab 3: Transfer
        # =================================================================
        transfer_widget = QWidget()
        transfer_vlayout = QVBoxLayout(transfer_widget)
        transfer_vlayout.setContentsMargins(8, 8, 8, 8)
        transfer_vlayout.setSpacing(10)

        transfer_desc = QLabel("Transfer the computed equivalent single-bolt model\n"
                               "to the MSD Builder for further analysis.")
        transfer_desc.setStyleSheet(f"color: {Theme.SUBTEXT};")
        transfer_desc.setWordWrap(True)
        transfer_vlayout.addWidget(transfer_desc)

        # Transfer summary card
        self.transfer_summary = QGroupBox("Model Summary")
        summary_layout = QFormLayout(self.transfer_summary)
        summary_layout.setSpacing(6)

        self.summary_diameter_label = QLabel("-")
        self.summary_diameter_label.setStyleSheet(f"font-weight: bold; color: {Theme.BLUE};")
        summary_layout.addRow("Equiv. Diameter:", self.summary_diameter_label)

        self.summary_preload_label = QLabel("-")
        self.summary_preload_label.setStyleSheet(f"font-weight: bold; color: {Theme.PEACH};")
        summary_layout.addRow("Equiv. Preload:", self.summary_preload_label)

        self.summary_quality_label = QLabel("-")
        summary_layout.addRow("Quality:", self.summary_quality_label)

        transfer_vlayout.addWidget(self.transfer_summary)

        # Transfer button
        transfer_btn = QPushButton("Transfer to MSD Builder")
        transfer_btn.setObjectName("success")
        transfer_btn.clicked.connect(self._transfer_to_builder)
        transfer_vlayout.addWidget(transfer_btn)

        transfer_vlayout.addStretch()

        self.sub_tabs.addTab(transfer_widget, "Transfer")

        layout.addWidget(self.sub_tabs)

    def _on_param_changed(self):
        """Handle parameter change for auto-recompute (LS1)."""
        if self.auto_recompute_check.isChecked():
            self._compute_reduction()

    def _compute_reduction(self):
        """Compute the multi-bolt to single-bolt reduction."""
        if not HAS_SIMILITUDE:
            QMessageBox.warning(self, "Module Not Found",
                              "Similitude module not available.")
            return

        # Get loading pattern from combo
        pattern_idx = self.loading_pattern_combo.currentIndex()
        loading_pattern = self.loading_pattern_combo.itemData(pattern_idx)
        if loading_pattern is None:
            loading_pattern = LoadingPattern.UNIFORM

        # Create configuration
        config = MultiBoltConfig(
            n_bolts=self.n_bolts_spin.value(),
            bolt_diameter=self.diameter_spin.value(),
            pitch=self.pitch_spin.value(),
            grip_length=self.grip_spin.value(),
            preload_per_bolt=self.preload_spin.value() * 1000,  # kN to N
            transverse_force_per_bolt=self.trans_force_spin.value() * 1000,
            bolt_circle_diameter=self.bcd_spin.value(),
            mu_thread=self.mu_thread_spin.value(),
            loading_pattern=loading_pattern,
            mu_bearing=self.mu_bearing_spin.value()
        )

        # Compute reduction
        self.equivalent_model = reduce_multi_bolt_to_single(config)

        # Update results table
        n = config.n_bolts
        d = config.bolt_diameter
        p = config.pitch

        data = [
            (f"{d:.1f} mm", f"{self.equivalent_model.d_equivalent:.1f} mm"),
            (f"{p:.2f} mm", f"{self.equivalent_model.p_equivalent:.2f} mm"),
            (f"{config.preload_per_bolt/1000:.1f} kN",
             f"{self.equivalent_model.F_p_equivalent/1000:.1f} kN"),
            (f"-", f"{self.equivalent_model.A_t_equivalent:.2f} mm²"),
            (f"{config.k_bolt_single:.2e} N/mm",
             f"{self.equivalent_model.k_bolt_equivalent:.2e} N/mm"),
            (f"{config.k_member_single:.2e} N/mm",
             f"{self.equivalent_model.k_member_equivalent:.2e} N/mm"),
            (f"-", f"{self.equivalent_model.k_bolt_equivalent / (self.equivalent_model.k_bolt_equivalent + self.equivalent_model.k_member_equivalent):.4f}"),
            (f"-", f"{self.equivalent_model.pi_preservation_quality * 100:.1f}%"),
        ]

        self.results_table.setUpdatesEnabled(False)
        self.results_table.blockSignals(True)
        try:
            for i, (orig, equiv) in enumerate(data):
                self.results_table.setItem(i, 1, QTableWidgetItem(orig))
                self.results_table.setItem(i, 2, QTableWidgetItem(equiv))
        finally:
            self.results_table.blockSignals(False)
            self.results_table.setUpdatesEnabled(True)

        # Update quality label
        quality = self.equivalent_model.pi_preservation_quality
        if quality > 0.95:
            color = Theme.GREEN
            label = "Excellent"
        elif quality > 0.85:
            color = Theme.BLUE
            label = "Good"
        elif quality > 0.70:
            color = Theme.YELLOW
            label = "Acceptable"
        else:
            color = Theme.RED
            label = "Poor"

        self.quality_label.setText(f"Pi-Group Preservation: {label} ({quality*100:.1f}%)")
        self.quality_label.setStyleSheet(f"font-weight: bold; color: {color};")

        # Update transfer summary
        self.summary_diameter_label.setText(
            f"{self.equivalent_model.d_equivalent:.1f} mm")
        self.summary_preload_label.setText(
            f"{self.equivalent_model.F_p_equivalent/1000:.1f} kN")
        self.summary_quality_label.setText(f"{label} ({quality*100:.1f}%)")
        self.summary_quality_label.setStyleSheet(f"font-weight: bold; color: {color};")

        # Switch to Results sub-tab
        self.sub_tabs.setCurrentIndex(1)

        # Emit signal
        self.reduction_computed.emit(self.equivalent_model)

    def _transfer_to_builder(self):
        """Transfer equivalent model to MSD Builder."""
        if self.equivalent_model is None:
            QMessageBox.warning(self, "No Model",
                              "Compute the equivalent model first.")
            return

        if HAS_SIMILITUDE:
            elements = create_msd_elements_from_equivalent(self.equivalent_model)
            self.transfer_requested.emit(elements)
            QMessageBox.information(self, "Transfer Complete",
                                  "Equivalent model transferred to MSD Builder.\n"
                                  "Open the Model Builder tab to view.")

    def refresh_theme(self):
        """Re-apply inline stylesheets after theme change."""
        self._header.setStyleSheet(f"font-size: {Theme.FONT_SIZE_HEADING}pt; font-weight: bold; color: {Theme.BLUE};")
        self._desc.setStyleSheet(f"color: {Theme.SUBTEXT};")
        self.quality_label.setStyleSheet(f"font-weight: bold; color: {Theme.SUBTEXT};")
        self.summary_diameter_label.setStyleSheet(f"font-weight: bold; color: {Theme.BLUE};")
        self.summary_preload_label.setStyleSheet(f"font-weight: bold; color: {Theme.PEACH};")


# =============================================================================
# GEOMETRIC SCALING PANEL
# =============================================================================

class GeometricScalingPanel(QWidget):
    """Panel for geometric scaling with loosening preservation."""

    scaling_computed = pyqtSignal(object)  # Emits ScaledLooseningModel
    transfer_requested = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scaled_model: Optional[ScaledLooseningModel] = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header
        self._header = QLabel("Geometric Scaling with Loosening Preservation")
        self._header.setStyleSheet(f"font-size: {Theme.FONT_SIZE_HEADING}pt; font-weight: bold; color: {Theme.MAUVE};")
        layout.addWidget(self._header)

        # Sub-tabs
        self.sub_tabs = QTabWidget()
        self.sub_tabs.setDocumentMode(True)
        self.sub_tabs.setUsesScrollButtons(True)
        self.sub_tabs.setElideMode(Qt.TextElideMode.ElideNone)

        # =================================================================
        # Sub-tab 1: Prototype & Scale
        # =================================================================
        proto_widget = QWidget()
        proto_vlayout = QVBoxLayout(proto_widget)
        proto_vlayout.setContentsMargins(8, 8, 8, 8)
        proto_vlayout.setSpacing(10)

        self._desc = QLabel("Create scaled model that preserves loosening behavior.\n"
                            "Includes scale effect corrections for friction and embedding.")
        self._desc.setStyleSheet(f"color: {Theme.SUBTEXT};")
        self._desc.setWordWrap(True)
        proto_vlayout.addWidget(self._desc)

        # Prototype parameters
        proto_group = QGroupBox("Prototype Joint Parameters")
        proto_form = QFormLayout(proto_group)
        proto_form.setSpacing(6)
        proto_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)

        self.proto_diameter_spin = QDoubleSpinBox()
        self.proto_diameter_spin.setRange(6, 100)
        self.proto_diameter_spin.setValue(24.0)
        self.proto_diameter_spin.setSuffix(" mm")
        self.proto_diameter_spin.setMinimumWidth(Theme.SPINBOX_MIN_WIDTH)
        proto_form.addRow("Bolt diameter (d_p):", self.proto_diameter_spin)

        self.proto_pitch_spin = QDoubleSpinBox()
        self.proto_pitch_spin.setRange(0.5, 10)
        self.proto_pitch_spin.setValue(3.0)
        self.proto_pitch_spin.setSuffix(" mm")
        self.proto_pitch_spin.setMinimumWidth(Theme.SPINBOX_MIN_WIDTH)
        proto_form.addRow("Thread pitch (p_p):", self.proto_pitch_spin)

        self.proto_grip_spin = QDoubleSpinBox()
        self.proto_grip_spin.setRange(10, 500)
        self.proto_grip_spin.setValue(100.0)
        self.proto_grip_spin.setSuffix(" mm")
        self.proto_grip_spin.setMinimumWidth(Theme.SPINBOX_MIN_WIDTH)
        proto_form.addRow("Grip length (L_p):", self.proto_grip_spin)

        self.proto_preload_spin = QDoubleSpinBox()
        self.proto_preload_spin.setRange(1, 5000)
        self.proto_preload_spin.setValue(160.0)
        self.proto_preload_spin.setSuffix(" kN")
        self.proto_preload_spin.setMinimumWidth(Theme.SPINBOX_MIN_WIDTH)
        proto_form.addRow("Preload (F_p):", self.proto_preload_spin)

        self.proto_freq_spin = QDoubleSpinBox()
        self.proto_freq_spin.setRange(1, 500)
        self.proto_freq_spin.setValue(25.0)
        self.proto_freq_spin.setSuffix(" Hz")
        self.proto_freq_spin.setMinimumWidth(Theme.SPINBOX_MIN_WIDTH)
        proto_form.addRow("Test frequency (f_p):", self.proto_freq_spin)

        proto_vlayout.addWidget(proto_group)

        # Scale factor
        scale_group = QGroupBox("Scale Factor")
        scale_form = QFormLayout(scale_group)
        scale_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)

        self.scale_factor_spin = QDoubleSpinBox()
        self.scale_factor_spin.setRange(0.05, 1.0)
        self.scale_factor_spin.setValue(0.25)
        self.scale_factor_spin.setDecimals(3)
        self.scale_factor_spin.setSingleStep(0.05)
        self.scale_factor_spin.setPrefix("lambda = ")
        self.scale_factor_spin.setMinimumWidth(Theme.SCALE_SPINBOX_MIN_WIDTH)
        self.scale_factor_spin.valueChanged.connect(self._update_scale_preview)
        scale_form.addRow("Geometric Scale:", self.scale_factor_spin)

        # Common presets
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(Theme.SPACING_XS)
        for scale, label in PRESET_SCALES:
            btn = QPushButton(label)
            btn.setMinimumWidth(Theme.PRESET_BUTTON_MIN_WIDTH)
            btn.clicked.connect(lambda checked, s=scale: self.scale_factor_spin.setValue(s))
            preset_layout.addWidget(btn)
        preset_layout.addStretch()
        scale_form.addRow("Presets:", preset_layout)

        # CS3: Cycle scaling mode selector
        self.cycle_mode_combo = QComboBox()
        if HAS_SIMILITUDE:
            for mode in CycleScalingMode:
                labels = {
                    'scaled_duration': 'Scaled Duration (faster test)',
                    'same_duration': 'Same Duration (same wall-clock)',
                    'same_cycles': 'Same Cycles (no scaling)',
                }
                self.cycle_mode_combo.addItem(labels.get(mode.value, mode.value), mode)
        self.cycle_mode_combo.setToolTip(
            "How to transform cycle counts between model and prototype.\n"
            "Scaled Duration: model runs fewer prototype-equivalent cycles\n"
            "Same Duration: same test time, model at higher frequency\n"
            "Same Cycles: no cycle transformation")
        scale_form.addRow("Cycle Scaling:", self.cycle_mode_combo)

        # LS3: Bolt standard selector for size lookup
        self.bolt_standard_combo = QComboBox()
        standards = get_available_standards() if HAS_BOLT_DB else ["ISO", "UNC"]
        for std in standards:
            self.bolt_standard_combo.addItem(std)
        self.bolt_standard_combo.setToolTip("Thread standard for model bolt size lookup")
        self.bolt_standard_combo.currentIndexChanged.connect(self._update_scale_preview)
        scale_form.addRow("Bolt Standard:", self.bolt_standard_combo)

        proto_vlayout.addWidget(scale_group)

        # Preview label
        self.preview_label = QLabel("Scaled diameter: - mm -> Standard: -")
        self.preview_label.setStyleSheet(f"color: {Theme.SUBTEXT};")
        proto_vlayout.addWidget(self.preview_label)

        # BUG-06/U1 fix: Compute button also in Prototype (Parameters) sub-tab
        compute_btn_proto = QPushButton("▶ Compute Scaled Model")
        compute_btn_proto.setObjectName("primary")
        compute_btn_proto.setMinimumHeight(Theme.BUTTON_MIN_HEIGHT_PRIMARY)
        compute_btn_proto.clicked.connect(self._compute_scaling)
        proto_vlayout.addWidget(compute_btn_proto)

        proto_vlayout.addStretch()

        proto_scroll = QScrollArea()
        proto_scroll.setWidgetResizable(True)
        proto_scroll.setFrameShape(QFrame.Shape.NoFrame)
        proto_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        proto_scroll.setWidget(proto_widget)
        self.sub_tabs.addTab(proto_scroll, "Prototype")

        # =================================================================
        # Sub-tab 2: Results
        # =================================================================
        results_widget = QWidget()
        results_vlayout = QVBoxLayout(results_widget)
        results_vlayout.setContentsMargins(8, 8, 8, 8)
        results_vlayout.setSpacing(10)

        # Compute button
        compute_btn = QPushButton("Compute Scaled Model")
        compute_btn.setObjectName("primary")
        compute_btn.clicked.connect(self._compute_scaling)
        results_vlayout.addWidget(compute_btn)

        # Results group
        results_group = QGroupBox("Scaled Model Results")
        results_group_layout = QVBoxLayout(results_group)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Parameter", "Prototype", "Model"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setRowCount(8)

        params = ["Diameter", "Pitch", "Grip Length", "Preload",
                  "Test Frequency", "Friction Corr (C_mu)", "Embedding Corr", "Quality"]
        self.results_table.setUpdatesEnabled(False)
        self.results_table.blockSignals(True)
        try:
            for i, param in enumerate(params):
                self.results_table.setItem(i, 0, QTableWidgetItem(param))
                self.results_table.setItem(i, 1, QTableWidgetItem("-"))
                self.results_table.setItem(i, 2, QTableWidgetItem("-"))
        finally:
            self.results_table.blockSignals(False)
            self.results_table.setUpdatesEnabled(True)

        results_group_layout.addWidget(self.results_table)
        results_vlayout.addWidget(results_group)

        # Warnings display
        self.warnings_label = QLabel("")
        self.warnings_label.setStyleSheet(f"color: {Theme.YELLOW};")
        self.warnings_label.setWordWrap(True)
        results_vlayout.addWidget(self.warnings_label)

        results_vlayout.addStretch()

        self.sub_tabs.addTab(results_widget, "Results")

        # =================================================================
        # Sub-tab 3: Corrections & Transfer
        # =================================================================
        corrections_widget = QWidget()
        corrections_vlayout = QVBoxLayout(corrections_widget)
        corrections_vlayout.setContentsMargins(8, 8, 8, 8)
        corrections_vlayout.setSpacing(10)

        # Scale effects info (LS4: detailed breakdown)
        scale_effects_group = QGroupBox("Scale Effect Corrections")
        se_layout = QVBoxLayout(scale_effects_group)

        self.friction_label = QLabel("Friction: +0% (C_mu = 1.00)")
        self.embedding_label = QLabel("Embedding: x1.0 relative effect")
        self.pitch_mismatch_label = QLabel("Pitch Mismatch: C_pitch = 1.00")
        self.cycle_label = QLabel("Cycle Transform: N_p = N_m x lambda")
        self.combined_corr_label = QLabel("Combined: C_total = 1.00")
        self.combined_corr_label.setStyleSheet(f"font-weight: bold; color: {Theme.PEACH};")

        se_layout.addWidget(self.friction_label)
        se_layout.addWidget(self.embedding_label)
        se_layout.addWidget(self.pitch_mismatch_label)
        se_layout.addWidget(self.cycle_label)
        se_layout.addWidget(self.combined_corr_label)

        corrections_vlayout.addWidget(scale_effects_group)

        # Transfer section
        transfer_desc = QLabel("Transfer the computed scaled model to the\n"
                               "MSD Builder for dynamic analysis.")
        transfer_desc.setStyleSheet(f"color: {Theme.SUBTEXT};")
        transfer_desc.setWordWrap(True)
        corrections_vlayout.addWidget(transfer_desc)

        transfer_btn = QPushButton("Transfer to MSD Builder")
        transfer_btn.setObjectName("success")
        transfer_btn.clicked.connect(self._transfer_to_builder)
        corrections_vlayout.addWidget(transfer_btn)

        corrections_vlayout.addStretch()

        self.sub_tabs.addTab(corrections_widget, "Corrections")

        layout.addWidget(self.sub_tabs)

        # Initial preview
        self._update_scale_preview()

    def _update_scale_preview(self):
        """Update the scale preview label (LS3: uses selected bolt standard)."""
        lam = self.scale_factor_spin.value()
        d_p = self.proto_diameter_spin.value()
        d_m = d_p * lam

        # Find nearest standard using selected standard
        std = self.bolt_standard_combo.currentText()
        if HAS_BOLT_DB:
            try:
                nearest_d, nearest_p = find_standard_bolt_size(d_m, std)
                prefix = "" if std in ("BSP", "BSW") else "M"
                self.preview_label.setText(
                    f"Scaled diameter: {d_m:.1f} mm -> Nearest {std}: "
                    f"{prefix}{nearest_d:.1f} x {nearest_p:.2f} mm"
                )
                return
            except Exception:
                pass

        # Fallback
        standard_sizes = [3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 27, 30, 33, 36]
        nearest = min(standard_sizes, key=lambda x: abs(x - d_m))
        self.preview_label.setText(
            f"Scaled diameter: {d_m:.1f} mm -> Nearest standard: M{nearest}"
        )

    def _compute_scaling(self):
        """Compute the geometric scaling."""
        if not HAS_SIMILITUDE:
            QMessageBox.warning(self, "Module Not Found",
                              "Similitude module not available.")
            return

        # Get cycle scaling mode (CS3)
        mode_idx = self.cycle_mode_combo.currentIndex()
        cycle_mode = self.cycle_mode_combo.itemData(mode_idx)
        if cycle_mode is None:
            cycle_mode = CycleScalingMode.SCALED_DURATION

        self.scaled_model = create_scaled_loosening_model(
            prototype_diameter=self.proto_diameter_spin.value(),
            prototype_pitch=self.proto_pitch_spin.value(),
            prototype_grip_length=self.proto_grip_spin.value(),
            prototype_preload=self.proto_preload_spin.value() * 1000,  # kN to N
            prototype_frequency=self.proto_freq_spin.value(),
            scale_factor=self.scale_factor_spin.value(),
            cycle_scaling_mode=cycle_mode
        )

        # Update results table
        sm = self.scaled_model
        data = [
            (f"{sm.prototype_diameter:.1f} mm", f"M{sm.standard_diameter:.0f}"),
            (f"{sm.prototype_pitch:.2f} mm", f"{sm.standard_pitch:.2f} mm"),
            (f"{sm.prototype_grip_length:.1f} mm", f"{sm.model_grip_length:.1f} mm"),
            (f"{sm.prototype_preload/1000:.1f} kN", f"{sm.model_preload:.0f} N"),
            (f"{sm.prototype_frequency:.1f} Hz", f"{sm.model_frequency:.1f} Hz"),
            ("-", f"{sm.friction_correction:.3f}"),
            ("-", f"{sm.embedding_correction:.3f}"),
            ("-", f"{sm.quality_score*100:.1f}%"),
        ]

        self.results_table.setUpdatesEnabled(False)
        self.results_table.blockSignals(True)
        try:
            for i, (proto, model) in enumerate(data):
                self.results_table.setItem(i, 1, QTableWidgetItem(proto))
                self.results_table.setItem(i, 2, QTableWidgetItem(model))
        finally:
            self.results_table.blockSignals(False)
            self.results_table.setUpdatesEnabled(True)

        # Update scale effect labels (LS4: detailed breakdown)
        lam = sm.scale_factor
        friction_pct = (sm.friction_correction - 1) * 100
        self.friction_label.setText(f"Friction: +{friction_pct:.1f}% (C_mu = {sm.friction_correction:.3f})")
        self.embedding_label.setText(f"Embedding: x{1/sm.embedding_correction:.1f} relative effect in model (C_e = {sm.embedding_correction:.3f})")
        pitch_pct = (sm.pitch_mismatch_correction - 1) * 100
        self.pitch_mismatch_label.setText(f"Pitch Mismatch: C_pitch = {sm.pitch_mismatch_correction:.4f} ({pitch_pct:+.1f}%)")
        self.cycle_label.setText(f"Cycle Transform: mode={sm.cycle_scaling_mode.value}, scale={sm.cycle_scale:.3f}")
        self.combined_corr_label.setText(f"Combined: C_total = {sm.combined_correction:.4f}")
        self.combined_corr_label.setStyleSheet(f"font-weight: bold; color: {Theme.PEACH};")

        # Show warnings
        if sm.warnings:
            self.warnings_label.setText("⚠️ " + "\n".join(sm.warnings))
        else:
            self.warnings_label.setText("")

        # Switch to Results sub-tab
        self.sub_tabs.setCurrentIndex(1)

        # Emit signal
        self.scaling_computed.emit(self.scaled_model)

    def _transfer_to_builder(self):
        """Transfer scaled model to MSD Builder."""
        if self.scaled_model is None:
            QMessageBox.warning(self, "No Model",
                              "Compute the scaled model first.")
            return

        if HAS_SIMILITUDE:
            elements = create_msd_elements_from_scaled(self.scaled_model)
            self.transfer_requested.emit(elements)
            QMessageBox.information(self, "Transfer Complete",
                                  "Scaled model transferred to MSD Builder.\n"
                                  "Open the Model Builder tab to view.")

    def refresh_theme(self):
        """Re-apply inline stylesheets after theme change."""
        self._header.setStyleSheet(f"font-size: {Theme.FONT_SIZE_HEADING}pt; font-weight: bold; color: {Theme.MAUVE};")
        self._desc.setStyleSheet(f"color: {Theme.SUBTEXT};")
        self.preview_label.setStyleSheet(f"color: {Theme.SUBTEXT};")
        self.warnings_label.setStyleSheet(f"color: {Theme.YELLOW};")
        self.combined_corr_label.setStyleSheet(f"font-weight: bold; color: {Theme.PEACH};")


# =============================================================================
# PI-GROUP DISPLAY PANEL
# =============================================================================

class PiGroupDisplayPanel(QWidget):
    """Panel for displaying loosening-specific Π-groups."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header
        self._header = QLabel("Π Loosening-Specific Dimensionless Groups")
        self._header.setStyleSheet(f"font-size: {Theme.FONT_SIZE_SUBHEADING}pt; font-weight: bold; color: {Theme.TEAL};")
        layout.addWidget(self._header)

        # Table
        self.pi_table = QTableWidget()
        self.pi_table.setColumnCount(5)
        self.pi_table.setHorizontalHeaderLabels([
            "Symbol", "Name", "Expression", "Value", "Status"
        ])
        self.pi_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # BUG-07 fix: Initialize Pi-groups with neutral "—" status (not fake ✓)
        # Actual values are filled when compute is pressed
        pi_data = [
            ("Π₁", "Slip Parameter", "F_t / (μ_b × F_p)", "—", "—"),
            ("Π₂", "Helix Parameter", "tan(λ) / (μ_t × sec(α))", "—", "—"),
            ("Π₃", "Preload Utilization", "F_p / (σ_y × A_t)", "—", "—"),
            ("Π₄", "Grip Ratio", "L / d", "—", "—"),
            ("Π₅", "Joint Constant", "k_b / (k_b + k_m)", "—", "—"),
            ("Π₆", "Bearing Leverage", "r_eff / r_m", "—", "—"),
            ("Π₇", "Pitch Ratio", "p / d", "—", "—"),
            ("Π₁₀", "Embedding Parameter", "f_z × k / F_p", "—", "—"),
        ]

        self.pi_table.setRowCount(len(pi_data))
        self.pi_table.setUpdatesEnabled(False)
        self.pi_table.blockSignals(True)
        try:
            for i, (symbol, name, expr, value, status) in enumerate(pi_data):
                self.pi_table.setItem(i, 0, QTableWidgetItem(symbol))
                self.pi_table.setItem(i, 1, QTableWidgetItem(name))
                self.pi_table.setItem(i, 2, QTableWidgetItem(expr))
                self.pi_table.setItem(i, 3, QTableWidgetItem(value))

                status_item = QTableWidgetItem(status)
                status_item.setForeground(QBrush(QColor(Theme.OVERLAY)))
                self.pi_table.setItem(i, 4, status_item)
        finally:
            self.pi_table.blockSignals(False)
            self.pi_table.setUpdatesEnabled(True)

        layout.addWidget(self.pi_table)

        # Summary
        self.summary_label = QLabel("Run analysis to compute Π-groups")
        self.summary_label.setStyleSheet(f"font-weight: bold; color: {Theme.OVERLAY};")
        layout.addWidget(self.summary_label)

    def update_pi_groups(self, pi_groups: list):
        """Update the Π-groups display from computed values."""
        self.pi_table.setRowCount(len(pi_groups))

        self.pi_table.setUpdatesEnabled(False)
        self.pi_table.blockSignals(True)
        matched = 0
        try:
            for i, pg in enumerate(pi_groups):
                self.pi_table.setItem(i, 0, QTableWidgetItem(pg.symbol))
                self.pi_table.setItem(i, 1, QTableWidgetItem(pg.name))
                self.pi_table.setItem(i, 2, QTableWidgetItem(pg.expression))
                self.pi_table.setItem(i, 3, QTableWidgetItem(f"{pg.prototype_value:.4f}"))

                if hasattr(pg, 'is_matched') and pg.is_matched:
                    status = "✓ Matched"
                    color = Theme.GREEN
                    matched += 1
                else:
                    deviation = abs(pg.model_value - pg.prototype_value) / max(abs(pg.prototype_value), 1e-10)
                    status = f"⚠ {deviation*100:.1f}% dev"
                    color = Theme.YELLOW if deviation < 0.1 else Theme.RED

                status_item = QTableWidgetItem(status)
                status_item.setForeground(QBrush(QColor(color)))
                self.pi_table.setItem(i, 4, status_item)
        finally:
            self.pi_table.blockSignals(False)
            self.pi_table.setUpdatesEnabled(True)

        total = len(pi_groups)
        pct = matched / total * 100 if total > 0 else 0

        if pct >= 95:
            color = Theme.GREEN
            status = "Similitude preserved"
        elif pct >= 80:
            color = Theme.YELLOW
            status = "Minor deviations"
        else:
            color = Theme.RED
            status = "Similitude compromised"

        self.summary_label.setText(f"Matched: {matched}/{total} ({pct:.0f}%) - {status}")
        self.summary_label.setStyleSheet(f"font-weight: bold; color: {color};")

    def refresh_theme(self):
        """Re-apply inline stylesheets after theme change."""
        self._header.setStyleSheet(f"font-size: {Theme.FONT_SIZE_SUBHEADING}pt; font-weight: bold; color: {Theme.TEAL};")
        self.summary_label.setStyleSheet(f"font-weight: bold; color: {Theme.GREEN};")


# =============================================================================
# SUGGESTED CONFIGURATION PANEL
# =============================================================================

class SuggestedConfigPanel(QWidget):
    """Panel showing the suggested scaled model configuration."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header
        self._header = QLabel("Suggested Model Configuration")
        self._header.setStyleSheet(f"font-size: {Theme.FONT_SIZE_SUBHEADING}pt; font-weight: bold; color: {Theme.GREEN};")
        layout.addWidget(self._header)

        # Configuration summary card
        self.config_card = QGroupBox("Scaled Test Specimen")
        card_layout = QFormLayout(self.config_card)
        card_layout.setSpacing(6)

        # Labels for configuration values
        self.bolt_size_label = QLabel("-")
        self.bolt_size_label.setStyleSheet(f"font-weight: bold; color: {Theme.BLUE};")
        card_layout.addRow("Bolt Size:", self.bolt_size_label)

        self.pitch_label = QLabel("-")
        card_layout.addRow("Thread Pitch:", self.pitch_label)

        self.grip_label = QLabel("-")
        card_layout.addRow("Grip Length:", self.grip_label)

        self.preload_label = QLabel("-")
        self.preload_label.setStyleSheet(f"font-weight: bold; color: {Theme.PEACH};")
        card_layout.addRow("Target Preload:", self.preload_label)

        self.frequency_label = QLabel("-")
        card_layout.addRow("Test Frequency:", self.frequency_label)

        self.cycle_factor_label = QLabel("-")
        card_layout.addRow("Cycle Transform:", self.cycle_factor_label)

        layout.addWidget(self.config_card)

        # Corrections summary
        self.corrections_card = QGroupBox("Scale Effect Corrections")
        corr_layout = QFormLayout(self.corrections_card)

        self.friction_corr_label = QLabel("-")
        corr_layout.addRow("Friction (C_mu):", self.friction_corr_label)

        self.embed_corr_label = QLabel("-")
        corr_layout.addRow("Embedding (C_e):", self.embed_corr_label)

        # LS4: Pitch mismatch correction display
        self.pitch_corr_label = QLabel("-")
        corr_layout.addRow("Pitch Mismatch (C_p):", self.pitch_corr_label)

        self.combined_corr_label2 = QLabel("-")
        self.combined_corr_label2.setStyleSheet(f"font-weight: bold; color: {Theme.PEACH};")
        corr_layout.addRow("Combined (C_total):", self.combined_corr_label2)

        self.quality_label = QLabel("-")
        self.quality_label.setStyleSheet(f"font-weight: bold;")
        corr_layout.addRow("Quality Score:", self.quality_label)

        layout.addWidget(self.corrections_card)

        # Interpretation text
        self.interpretation_text = QTextEdit()
        self.interpretation_text.setReadOnly(True)
        self.interpretation_text.setMinimumHeight(70)
        # Themed via global QSS (#themedPanel) so it re-themes on switch.
        self.interpretation_text.setObjectName("themedPanel")
        self.interpretation_text.setPlainText(
            "Configure the prototype parameters and scale factor, "
            "then click 'Compute Scaled Model' to generate the suggested configuration."
        )
        layout.addWidget(self.interpretation_text)

        layout.addStretch()

    def update_config(self, scaled_model: 'ScaledLooseningModel'):
        """Update the displayed configuration from a scaled model."""
        sm = scaled_model

        # Update labels
        self.bolt_size_label.setText(f"M{sm.standard_diameter:.0f}")
        self.pitch_label.setText(f"{sm.standard_pitch:.2f} mm")
        self.grip_label.setText(f"{sm.model_grip_length:.1f} mm")
        self.preload_label.setText(f"{sm.model_preload:.0f} N ({sm.model_preload/1000:.2f} kN)")
        self.frequency_label.setText(f"{sm.model_frequency:.1f} Hz")
        self.cycle_factor_label.setText(f"N_prototype = N_model x {sm.scale_factor:.3f}")

        # Corrections
        friction_pct = (sm.friction_correction - 1) * 100
        self.friction_corr_label.setText(f"{sm.friction_correction:.3f} (+{friction_pct:.1f}%)")
        self.embed_corr_label.setText(f"{sm.embedding_correction:.3f}")
        pitch_pct = (sm.pitch_mismatch_correction - 1) * 100
        self.pitch_corr_label.setText(f"{sm.pitch_mismatch_correction:.4f} ({pitch_pct:+.1f}%)")
        self.combined_corr_label2.setText(f"{sm.combined_correction:.4f}")
        self.combined_corr_label2.setStyleSheet(f"font-weight: bold; color: {Theme.PEACH};")

        # Quality
        quality = sm.quality_score * 100
        if quality >= 90:
            color = Theme.GREEN
            rating = "Excellent"
        elif quality >= 75:
            color = Theme.BLUE
            rating = "Good"
        elif quality >= 60:
            color = Theme.YELLOW
            rating = "Acceptable"
        else:
            color = Theme.RED
            rating = "Poor"

        self.quality_label.setText(f"{quality:.1f}% ({rating})")
        self.quality_label.setStyleSheet(f"font-weight: bold; color: {color};")

        # Interpretation
        interp_lines = [
            f"For prototype M{sm.prototype_diameter:.0f} at lambda={sm.scale_factor}:",
            f"",
            f"- Use standard M{sm.standard_diameter:.0f} bolt (ideal: {sm.model_diameter:.1f} mm)",
            f"- Apply {sm.model_preload:.0f} N preload ({sm.model_preload/1000:.2f} kN)",
            f"- Run test at {sm.model_frequency:.1f} Hz",
        ]

        if sm.warnings:
            interp_lines.append("")
            interp_lines.append("Warnings:")
            for w in sm.warnings:
                interp_lines.append(f"  - {w}")

        self.interpretation_text.setPlainText("\n".join(interp_lines))

    def refresh_theme(self):
        """Re-apply inline stylesheets after theme change."""
        self._header.setStyleSheet(f"font-size: {Theme.FONT_SIZE_SUBHEADING}pt; font-weight: bold; color: {Theme.GREEN};")
        self.bolt_size_label.setStyleSheet(f"font-weight: bold; color: {Theme.BLUE};")
        self.preload_label.setStyleSheet(f"font-weight: bold; color: {Theme.PEACH};")


# =============================================================================
# ERROR ANALYSIS PANEL
# =============================================================================

class ErrorAnalysisPanel(QWidget):
    """Panel showing error analysis between prototype and model."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header
        self._header = QLabel("Error Analysis")
        self._header.setStyleSheet(f"font-size: {Theme.FONT_SIZE_SUBHEADING}pt; font-weight: bold; color: {Theme.RED};")
        layout.addWidget(self._header)

        # Error table
        self.error_table = QTableWidget()
        self.error_table.setColumnCount(5)
        self.error_table.setHorizontalHeaderLabels([
            "Parameter", "Prototype", "Model", "Error (%)", "Status"
        ])
        self.error_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Initialize with empty rows
        params = [
            "Diameter Ratio",
            "Pitch Ratio (p/d)",
            "Grip Ratio (L/d)",
            "Preload Stress",
            "Frequency Ratio",
            "Slip Parameter (Pi1)",
            "Helix Parameter (Pi2)",
            "Joint Constant (Phi)",
        ]

        self.error_table.setRowCount(len(params))
        self.error_table.setUpdatesEnabled(False)
        self.error_table.blockSignals(True)
        try:
            for i, param in enumerate(params):
                self.error_table.setItem(i, 0, QTableWidgetItem(param))
                for j in range(1, 5):
                    self.error_table.setItem(i, j, QTableWidgetItem("-"))
        finally:
            self.error_table.blockSignals(False)
            self.error_table.setUpdatesEnabled(True)

        layout.addWidget(self.error_table)

        # Summary statistics
        stats_layout = QHBoxLayout()

        self.mean_error_label = QLabel("Mean Error: -")
        self.mean_error_label.setStyleSheet(f"font-weight: bold;")
        stats_layout.addWidget(self.mean_error_label)

        self.max_error_label = QLabel("Max Error: -")
        self.max_error_label.setStyleSheet(f"font-weight: bold;")
        stats_layout.addWidget(self.max_error_label)

        stats_layout.addStretch()

        self.overall_label = QLabel("Overall: -")
        self.overall_label.setStyleSheet(f"font-weight: bold; font-size: {Theme.FONT_SIZE_SUBHEADING}pt;")
        stats_layout.addWidget(self.overall_label)

        layout.addLayout(stats_layout)

    def update_errors(self, prototype_data: dict, model_data: dict, pi_groups: list = None):
        """Update error analysis from prototype and model data."""
        errors = []

        # Calculate errors for each parameter
        comparisons = [
            ("Diameter Ratio", prototype_data.get('d', 1), model_data.get('d', 1)),
            ("Pitch Ratio (p/d)",
             prototype_data.get('p', 1) / max(prototype_data.get('d', 1), 0.001),
             model_data.get('p', 1) / max(model_data.get('d', 1), 0.001)),
            ("Grip Ratio (L/d)",
             prototype_data.get('L', 1) / max(prototype_data.get('d', 1), 0.001),
             model_data.get('L', 1) / max(model_data.get('d', 1), 0.001)),
            ("Preload Stress",
             prototype_data.get('sigma_p', 1),
             model_data.get('sigma_p', 1)),
            ("Frequency Ratio",
             1.0,
             prototype_data.get('f', 1) / max(model_data.get('f', 1), 0.001)),
        ]

        # Add Pi group comparisons if available
        if pi_groups:
            for pg in pi_groups[:3]:  # First 3 Pi groups
                comparisons.append((
                    pg.name if hasattr(pg, 'name') else f"Pi_{len(comparisons)}",
                    pg.prototype_value if hasattr(pg, 'prototype_value') else 1.0,
                    pg.model_value if hasattr(pg, 'model_value') else 1.0
                ))

        # Fill table
        self.error_table.setRowCount(len(comparisons))

        self.error_table.setUpdatesEnabled(False)
        self.error_table.blockSignals(True)
        try:
            for i, (name, proto_val, model_val) in enumerate(comparisons):
                self.error_table.setItem(i, 0, QTableWidgetItem(name))
                self.error_table.setItem(i, 1, QTableWidgetItem(f"{proto_val:.4f}"))
                self.error_table.setItem(i, 2, QTableWidgetItem(f"{model_val:.4f}"))

                # Calculate error
                if abs(proto_val) > 1e-10:
                    error = abs(model_val - proto_val) / abs(proto_val) * 100
                else:
                    error = 0.0

                errors.append(error)

                error_item = QTableWidgetItem(f"{error:.2f}%")

                # Color code
                if error < 5:
                    status = "OK"
                    color = Theme.GREEN
                elif error < 15:
                    status = "~"
                    color = Theme.YELLOW
                else:
                    status = "!"
                    color = Theme.RED

                error_item.setForeground(QBrush(QColor(color)))
                self.error_table.setItem(i, 3, error_item)

                status_item = QTableWidgetItem(status)
                status_item.setForeground(QBrush(QColor(color)))
                self.error_table.setItem(i, 4, status_item)
        finally:
            self.error_table.blockSignals(False)
            self.error_table.setUpdatesEnabled(True)

        # Summary statistics
        if errors:
            mean_err = np.mean(errors)
            max_err = np.max(errors)

            self.mean_error_label.setText(f"Mean Error: {mean_err:.2f}%")
            self.max_error_label.setText(f"Max Error: {max_err:.2f}%")

            if max_err < 10:
                overall_text = "EXCELLENT"
                overall_color = Theme.GREEN
            elif max_err < 20:
                overall_text = "GOOD"
                overall_color = Theme.BLUE
            elif max_err < 35:
                overall_text = "ACCEPTABLE"
                overall_color = Theme.YELLOW
            else:
                overall_text = "POOR"
                overall_color = Theme.RED

            self.overall_label.setText(f"Overall: {overall_text}")
            self.overall_label.setStyleSheet(f"font-weight: bold; font-size: {Theme.FONT_SIZE_SUBHEADING}pt; color: {overall_color};")

    def refresh_theme(self):
        """Re-apply inline stylesheets after theme change."""
        self._header.setStyleSheet(f"font-size: {Theme.FONT_SIZE_SUBHEADING}pt; font-weight: bold; color: {Theme.RED};")


# =============================================================================
# COMPARISON PLOTS PANEL
# =============================================================================

class ComparisonPlotsPanel(QWidget):
    """Panel for visualizing comparison plots between prototype and model."""

    open_editor_requested = pyqtSignal(object)  # Emits matplotlib figure

    def __init__(self, mode: str = "scaling", parent=None):
        super().__init__(parent)
        self.mode = mode  # "scaling" or "multi_bolt"
        self.current_figure = None
        self.N_model = None
        self.F_model = None
        self.N_proto = None
        self.F_proto = None
        self.scale_factor = 1.0
        # MS7: Experimental data storage
        self.N_experimental = None
        self.F_experimental = None
        self.experimental_label = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header with Open in Editor button
        header_layout = QHBoxLayout()

        self._header = QLabel("Comparison Plots")
        self._header.setStyleSheet(f"font-size: {Theme.FONT_SIZE_SUBHEADING}pt; font-weight: bold; color: {Theme.PEACH};")
        header_layout.addWidget(self._header)

        header_layout.addStretch()

        self.open_editor_btn = QPushButton("Open in Editor")
        self.open_editor_btn.setToolTip("Open plot in separate window with full editing options")
        self.open_editor_btn.clicked.connect(self._open_in_editor)
        self.open_editor_btn.setEnabled(False)
        header_layout.addWidget(self.open_editor_btn)

        layout.addLayout(header_layout)

        # Plot widget or placeholder
        # Use taller figure for scaling mode (two subplots)
        if HAS_PLOT_WIDGET:
            fig_h = 9 if self.mode == "scaling" else 6
            self.plot_widget = PlotWidget(toolbar=True, width=10, height=fig_h)
            self.plot_widget.setMinimumHeight(200)
            layout.addWidget(self.plot_widget, stretch=1)
        else:
            placeholder = QLabel("Plot widget not available.\n"
                                "Install matplotlib to enable visualization.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setObjectName("placeholder")
            layout.addWidget(placeholder, stretch=1)
            self.plot_widget = None

        # Controls
        controls_group = QGroupBox("Display Options")
        controls_layout = QGridLayout(controls_group)
        controls_layout.setSpacing(6)

        if self.mode == "multi_bolt":
            self.show_model_check = QCheckBox("Equivalent Single Bolt")
            self.show_proto_check = QCheckBox("Original (per bolt)")
        else:
            self.show_model_check = QCheckBox("Model Test Data")
            self.show_proto_check = QCheckBox("Prototype Prediction")
        self.show_model_check.setChecked(True)
        self.show_model_check.toggled.connect(self._refresh_plot)

        self.show_proto_check.setChecked(True)
        self.show_proto_check.toggled.connect(self._refresh_plot)

        self.show_corrected_check = QCheckBox("Apply Corrections")
        self.show_corrected_check.setChecked(True)
        self.show_corrected_check.toggled.connect(self._refresh_plot)

        self.show_error_band_check = QCheckBox("Show Error Band")
        self.show_error_band_check.setChecked(False)
        self.show_error_band_check.toggled.connect(self._refresh_plot)

        # LS5: Show experimental data checkbox
        self.show_experimental_check = QCheckBox("Show Experimental Data")
        self.show_experimental_check.setChecked(True)
        self.show_experimental_check.toggled.connect(self._refresh_plot)

        controls_layout.addWidget(self.show_model_check, 0, 0)
        controls_layout.addWidget(self.show_proto_check, 0, 1)
        if self.mode != "multi_bolt":
            controls_layout.addWidget(self.show_corrected_check, 1, 0)
        else:
            self.show_corrected_check.setVisible(False)
        controls_layout.addWidget(self.show_error_band_check, 1, 1 if self.mode != "multi_bolt" else 0)
        controls_layout.addWidget(self.show_experimental_check, 2, 0)

        # MS7: CSV import button for experimental data
        import_btn = QPushButton("Import CSV (Junker Test Data)")
        import_btn.setToolTip(
            "Import experimental Junker test data from CSV file.\n"
            "Expected columns: Cycles, F/F0 (normalized preload)")
        import_btn.clicked.connect(self._import_csv_data)
        controls_layout.addWidget(import_btn, 2, 1)

        layout.addWidget(controls_group)

    def plot_loosening_comparison(self,
                                   N_model: np.ndarray,
                                   F_model: np.ndarray,
                                   N_proto: np.ndarray,
                                   F_proto: np.ndarray,
                                   scale_factor: float):
        """Plot loosening curves comparison between model and prototype."""
        # Store data for refresh
        self.N_model = N_model
        self.F_model = F_model
        self.N_proto = N_proto
        self.F_proto = F_proto
        self.scale_factor = scale_factor

        self._refresh_plot()
        self.open_editor_btn.setEnabled(True)

    def _refresh_plot(self):
        """Refresh the plot with current settings."""
        if self.plot_widget is None:
            return

        if self.N_model is None:
            # Show placeholder message when no data
            fig = self.plot_widget.figure
            fig.clear()
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "No comparison data available.\n\nRun an analysis to generate plots.",
                   ha='center', va='center', fontsize=12, color=Theme.SUBTEXT)
            ax.axis('off')
            self._apply_theme_to_ax(fig, ax)
            fig.tight_layout()
            self.plot_widget.canvas.draw()
            return

        fig = self.plot_widget.figure
        fig.clear()

        if self.mode == "multi_bolt":
            self._refresh_plot_multi_bolt(fig)
        else:
            self._refresh_plot_scaling(fig)

        fig.tight_layout()
        self.plot_widget.canvas.draw()

        # Store figure for editor
        self.current_figure = fig

    @staticmethod
    def _apply_theme_to_ax(fig, ax):
        """Apply current Theme colors to a figure and axes."""
        fig.set_facecolor(Theme.BASE)
        ax.set_facecolor(Theme.SURFACE0)
        ax.tick_params(colors=Theme.TEXT)
        ax.xaxis.label.set_color(Theme.TEXT)
        ax.yaxis.label.set_color(Theme.TEXT)
        ax.title.set_color(Theme.TEXT)
        for spine in ax.spines.values():
            spine.set_edgecolor(Theme.SURFACE2)
        leg = ax.get_legend()
        if leg is not None:
            leg.get_frame().set_facecolor(Theme.SURFACE0)
            leg.get_frame().set_edgecolor(Theme.SURFACE2)
            for t in leg.get_texts():
                t.set_color(Theme.TEXT)

    def _refresh_plot_multi_bolt(self, fig):
        """Single-subplot plot for multi-bolt comparison."""
        ax = fig.add_subplot(111)

        if self.show_model_check.isChecked():
            ax.plot(self.N_model, self.F_model * 100, 'o-',
                    color=Theme.BLUE, label='Equivalent Single Bolt',
                    markersize=5, linewidth=2)

        if self.show_proto_check.isChecked():
            ax.plot(self.N_proto, self.F_proto * 100, 's--',
                    color=Theme.GREEN, label='Original (per bolt)',
                    markersize=5, linewidth=2)

        if self.show_error_band_check.isChecked() and self.show_model_check.isChecked():
            ax.fill_between(self.N_model, self.F_model * 90, self.F_model * 110,
                            alpha=0.2, color=Theme.BLUE, label='10% band')

        # LS5/MS7: Overlay experimental data
        self._plot_experimental_data(ax)

        ax.set_xlabel('Cycles (N)', fontsize=11, color=Theme.TEXT)
        ax.set_ylabel('Normalized Preload F/F0 (%)', fontsize=11, color=Theme.TEXT)
        ax.set_title('Multi-Bolt Reduction: Loosening Comparison',
                     fontsize=12, fontweight='bold', color=Theme.TEXT)
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3, color=Theme.SURFACE1)
        ax.set_ylim(0, 110)
        ax.set_xlim(left=0)
        self._apply_theme_to_ax(fig, ax)

    def _refresh_plot_scaling(self, fig):
        """Two-subplot plot for geometric scaling comparison."""
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        fig.subplots_adjust(hspace=0.40)

        # Top plot: Preload vs Cycles (model domain)
        if self.show_model_check.isChecked():
            ax1.plot(self.N_model, self.F_model * 100, 'o-',
                    color=Theme.BLUE, label='Model Test Data',
                    markersize=5, linewidth=2)

        if self.show_proto_check.isChecked():
            # Show prototype in model cycle domain (scaled back)
            N_proto_scaled = self.N_proto / self.scale_factor
            ax1.plot(N_proto_scaled, self.F_proto * 100, 's--',
                    color=Theme.PEACH, label='Prototype (scaled to model cycles)',
                    markersize=5, linewidth=2)

        if self.show_error_band_check.isChecked() and self.show_model_check.isChecked():
            ax1.fill_between(self.N_model, self.F_model * 90, self.F_model * 110,
                            alpha=0.2, color=Theme.BLUE, label='10% band')

        # LS5/MS7: Overlay experimental data on top subplot
        self._plot_experimental_data(ax1)

        ax1.set_xlabel('Model Cycles (N_m)', fontsize=11, color=Theme.TEXT)
        ax1.set_ylabel('Normalized Preload F/F0 (%)', fontsize=11, color=Theme.TEXT)
        ax1.set_title(f'Loosening Comparison (Model Domain, λ={self.scale_factor:.3f})',
                     fontsize=12, fontweight='bold', color=Theme.TEXT)
        ax1.legend(loc='upper right', fontsize=9)
        ax1.grid(True, alpha=0.3, color=Theme.SURFACE1)
        ax1.set_ylim(0, 110)
        ax1.set_xlim(left=0)
        self._apply_theme_to_ax(fig, ax1)

        # Bottom plot: Preload vs Cycles (prototype domain)
        if self.show_model_check.isChecked():
            N_model_scaled = self.N_model * self.scale_factor
            ax2.plot(N_model_scaled, self.F_model * 100, 'o-',
                    color=Theme.BLUE, label='Model (scaled to prototype cycles)',
                    markersize=5, linewidth=2)

        if self.show_proto_check.isChecked():
            ax2.plot(self.N_proto, self.F_proto * 100, 's--',
                    color=Theme.PEACH, label='Prototype Prediction',
                    markersize=5, linewidth=2)

        ax2.set_xlabel('Prototype Cycles (N_p)', fontsize=11, color=Theme.TEXT)
        ax2.set_ylabel('Normalized Preload F/F₀ (%)', fontsize=11, color=Theme.TEXT)
        ax2.set_title('Loosening Comparison (Prototype Domain)',
                     fontsize=12, fontweight='bold', color=Theme.TEXT)
        ax2.legend(loc='upper right', fontsize=9)
        ax2.grid(True, alpha=0.3, color=Theme.SURFACE1)
        ax2.set_ylim(0, 110)
        ax2.set_xlim(left=0)
        self._apply_theme_to_ax(fig, ax2)

    def _import_csv_data(self):
        """Import experimental Junker test data from CSV (MS7)."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Import Junker Test Data",
            "", "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)"
        )
        if not filepath:
            return

        try:
            # Try to parse CSV: expected columns are Cycles,F/F0
            data = np.genfromtxt(filepath, delimiter=',', skip_header=1,
                                 filling_values=np.nan)
            if data.ndim == 1:
                # Single column - try tab/space delimiter
                data = np.genfromtxt(filepath, skip_header=1, filling_values=np.nan)

            if data.ndim < 2 or data.shape[1] < 2:
                QMessageBox.warning(self, "Import Error",
                    "CSV must have at least 2 columns: Cycles, F/F0")
                return

            # Remove NaN rows
            valid = ~np.isnan(data[:, 0]) & ~np.isnan(data[:, 1])
            data = data[valid]

            self.N_experimental = data[:, 0]
            self.F_experimental = data[:, 1]

            # If values > 1, assume percentage and normalize
            if np.max(self.F_experimental) > 2.0:
                self.F_experimental = self.F_experimental / 100.0

            import os
            self.experimental_label = os.path.basename(filepath)

            self._refresh_plot()
            QMessageBox.information(self, "Import Complete",
                f"Loaded {len(self.N_experimental)} data points from {self.experimental_label}")

        except Exception as e:
            QMessageBox.warning(self, "Import Error",
                f"Failed to read CSV file:\n{str(e)}")

    def _plot_experimental_data(self, ax):
        """Plot imported experimental data on the given axes (MS7)."""
        if (self.N_experimental is not None and self.F_experimental is not None
                and self.show_experimental_check.isChecked()):
            ax.plot(self.N_experimental, self.F_experimental * 100, 'D-',
                    color=Theme.YELLOW, label=f'Experimental ({self.experimental_label})',
                    markersize=4, linewidth=1.5, alpha=0.8)

    def _open_in_editor(self):
        """Open the current plot in the external editor window."""
        if self.current_figure is None:
            return

        if HAS_PLOT_WIDGET and PlotEditorWindow is not None:
            # Create a copy of the figure for the editor
            import matplotlib.pyplot as plt
            fig_h = 10 if self.mode == "scaling" else 8
            new_fig = plt.figure(figsize=(12, fig_h))

            if self.N_model is not None:
                if self.mode == "multi_bolt":
                    self._refresh_plot_multi_bolt(new_fig)
                else:
                    self._refresh_plot_scaling(new_fig)

            new_fig.tight_layout()

            # Open editor window
            editor = PlotEditorWindow(figure=new_fig,
                                     title="Similitude Comparison Plot Editor",
                                     parent=self.window())
            editor.show()
        else:
            QMessageBox.warning(self, "Editor Not Available",
                              "Plot editor window is not available.")

    def refresh_theme(self):
        """Re-apply inline stylesheets and redraw plots after theme change."""
        self._header.setStyleSheet(f"font-size: {Theme.FONT_SIZE_SUBHEADING}pt; font-weight: bold; color: {Theme.PEACH};")
        # Redraw the plot with updated Theme colors
        if self.N_model is not None:
            self._refresh_plot()


# =============================================================================
# ENHANCED SIMILITUDE TAB
# =============================================================================

class EnhancedSimilitudeTab(QWidget):
    """
    Enhanced Similitude Tab with loosening analysis integration.

    Features:
    1. Multi-Bolt to Single-Bolt Reduction
    2. Geometric Scaling with Loosening Preservation
    3. Π-Group Analysis for Loosening
    4. Suggested Model Configuration
    5. Comparison Plots (Prototype vs Model)
    6. Error Analysis
    7. Transfer to MSD Builder
    """

    transfer_to_builder = pyqtSignal(dict)  # Emits MSD element parameters
    send_to_solver = pyqtSignal(dict)        # U6: send scaled params to solver
    import_from_model_requested = pyqtSignal()  # U2: request model from AppState

    def __init__(self, parent=None):
        super().__init__(parent)
        self.analysis: Optional[LooseningSimlitudeAnalysis] = None
        self.last_scaled_model: Optional[ScaledLooseningModel] = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # U2: "Import from MSD Builder" bar at the top
        import_bar = QFrame()
        # Styled via global QSS (QFrame#importBar) so it re-themes on switch.
        import_bar.setObjectName("importBar")
        import_bar_layout = QHBoxLayout(import_bar)
        import_bar_layout.setContentsMargins(
            Theme.SPACING_MD, Theme.SPACING_XS, Theme.SPACING_MD, Theme.SPACING_XS)
        import_bar_layout.setSpacing(Theme.SPACING_MD)
        import_lbl = QLabel("Load prototype parameters from current model:")
        import_lbl.setObjectName("caption")  # themed SUBTEXT via global QSS
        import_bar_layout.addWidget(import_lbl)
        import_bar_layout.addStretch()
        self._import_btn = QPushButton("⬇ Import from MSD Builder")
        self._import_btn.setToolTip("Populate Similitude parameters from the current MSD Builder model")
        self._import_btn.clicked.connect(self.import_from_model_requested.emit)
        import_bar_layout.addWidget(self._import_btn)
        main_layout.addWidget(import_bar)

        # Analysis type tabs (top-level)
        self.analysis_tabs = QTabWidget()
        self.analysis_tabs.setDocumentMode(True)
        self.analysis_tabs.setUsesScrollButtons(True)
        self.analysis_tabs.setElideMode(Qt.TextElideMode.ElideNone)

        # =================================================================
        # Multi-bolt reduction panel + Pi Groups as sub-tab
        # =================================================================
        self.multi_bolt_panel = MultiBoltReductionPanel()

        # Add Pi Groups as a sub-tab inside Multi-Bolt
        self.pi_panel = PiGroupDisplayPanel()
        self.multi_bolt_panel.sub_tabs.addTab(self.pi_panel, "Pi Groups")

        # Add Comparison Plots as sub-tab inside Multi-Bolt
        self.multi_bolt_comparison_panel = ComparisonPlotsPanel(mode="multi_bolt")
        self.multi_bolt_panel.sub_tabs.addTab(self.multi_bolt_comparison_panel, "Comparison Plots")

        self.analysis_tabs.addTab(self.multi_bolt_panel, "Multi-Bolt")

        # =================================================================
        # Geometric scaling panel + Suggested Model, Error, Plots as sub-tabs
        # =================================================================
        self.scaling_panel = GeometricScalingPanel()

        # Add Suggested Config as sub-tab inside Scaling
        self.suggested_config_panel = SuggestedConfigPanel()
        self.scaling_panel.sub_tabs.addTab(self.suggested_config_panel, "Suggested Model")

        # Add Error Analysis as sub-tab inside Scaling
        self.error_panel = ErrorAnalysisPanel()
        self.scaling_panel.sub_tabs.addTab(self.error_panel, "Error Analysis")

        # Add Comparison Plots as sub-tab inside Scaling
        self.comparison_panel = ComparisonPlotsPanel()
        self.scaling_panel.sub_tabs.addTab(self.comparison_panel, "Comparison Plots")

        self.analysis_tabs.addTab(self.scaling_panel, "Scaling")

        main_layout.addWidget(self.analysis_tabs)

        # Export actions bar at bottom
        export_layout = QHBoxLayout()

        self._export_report_btn = QPushButton("Export Report")
        self._export_report_btn.setToolTip("Export analysis as Markdown report")
        self._export_report_btn.clicked.connect(self._export_report)
        self._export_report_btn.setEnabled(False)  # U4: disabled until analysis runs
        self._export_report_btn.setMinimumWidth(100)

        self._export_json_btn = QPushButton("Export JSON")
        self._export_json_btn.setToolTip("Export raw data as JSON")
        self._export_json_btn.clicked.connect(self._export_json)
        self._export_json_btn.setEnabled(False)  # U4
        self._export_json_btn.setMinimumWidth(90)

        # LS6: Export plot as image
        self._export_png_btn = QPushButton("Export Plot")
        self._export_png_btn.setToolTip("Export comparison plot as PNG image")
        self._export_png_btn.clicked.connect(self._export_plot_image)
        self._export_png_btn.setEnabled(False)  # U4
        self._export_png_btn.setMinimumWidth(90)

        # U6: Send to Solver
        self._send_to_solver_btn = QPushButton("→ Solver")
        self._send_to_solver_btn.setToolTip("Apply scaled model parameters to the Solver tab")
        self._send_to_solver_btn.clicked.connect(self._send_to_solver)
        self._send_to_solver_btn.setEnabled(False)  # U4
        self._send_to_solver_btn.setMinimumWidth(80)

        self._transfer_btn = QPushButton("→ Builder")
        self._transfer_btn.setObjectName("primary")
        self._transfer_btn.setToolTip("Transfer suggested config to MSD Builder")
        self._transfer_btn.clicked.connect(self._transfer_suggested)
        self._transfer_btn.setEnabled(False)  # U4
        self._transfer_btn.setMinimumWidth(80)

        export_layout.addWidget(self._export_report_btn)
        export_layout.addWidget(self._export_json_btn)
        export_layout.addWidget(self._export_png_btn)
        export_layout.addStretch()
        export_layout.addWidget(self._send_to_solver_btn)
        export_layout.addWidget(self._transfer_btn)

        main_layout.addLayout(export_layout)

    def _connect_signals(self):
        """Connect internal signals."""
        # Multi-bolt panel
        self.multi_bolt_panel.reduction_computed.connect(self._on_reduction_computed)
        self.multi_bolt_panel.transfer_requested.connect(self._on_transfer_requested)

        # Scaling panel
        self.scaling_panel.scaling_computed.connect(self._on_scaling_computed)
        self.scaling_panel.transfer_requested.connect(self._on_transfer_requested)

    def _on_reduction_computed(self, equivalent: 'EquivalentSingleBolt'):
        """Handle multi-bolt reduction completion."""
        if HAS_SIMILITUDE:
            # BUG-03 fix: populate analysis with actual computed data
            self.analysis = LooseningSimlitudeAnalysis()
            self.analysis.equivalent_model = equivalent
            if hasattr(equivalent, 'pi_groups') and equivalent.pi_groups:
                self.analysis.pi_groups = equivalent.pi_groups
            # Update Π-groups display
            if equivalent.pi_groups:
                self.pi_panel.update_pi_groups(equivalent.pi_groups)

            # Generate Jiang two-stage loosening curves for comparison
            N_cycles = np.array([0, 25, 50, 100, 150, 200, 300, 500,
                                 750, 1000, 1500, 2000, 3000, 5000])

            # Original (per bolt) - default Jiang params
            lambda1_orig, lambda2_orig, N_trans_orig = 0.015, 0.005, 200
            F_orig = np.zeros_like(N_cycles, dtype=float)
            for i, N in enumerate(N_cycles):
                if N <= N_trans_orig:
                    F_orig[i] = 1.0 - 0.15 * (1 - np.exp(-N / (N_trans_orig / 3)))
                else:
                    F_trans = 1.0 - 0.15 * (1 - np.exp(-N_trans_orig / (N_trans_orig / 3)))
                    F_orig[i] = F_trans * np.exp(-lambda2_orig * (N - N_trans_orig))

            # Equivalent single bolt - from reduction model params
            lam1 = getattr(equivalent, 'jiang_lambda1', lambda1_orig)
            lam2 = getattr(equivalent, 'jiang_lambda2', lambda2_orig)
            N_tr = getattr(equivalent, 'N_transition', N_trans_orig)
            F_equiv = np.zeros_like(N_cycles, dtype=float)
            for i, N in enumerate(N_cycles):
                if N <= N_tr:
                    F_equiv[i] = 1.0 - 0.15 * (1 - np.exp(-N / (N_tr / 3)))
                else:
                    F_trans = 1.0 - 0.15 * (1 - np.exp(-N_tr / (N_tr / 3)))
                    F_equiv[i] = F_trans * np.exp(-lam2 * (N - N_tr))

            # Plot: N_model = equivalent, N_proto = original (per bolt)
            self.multi_bolt_comparison_panel.plot_loosening_comparison(
                N_cycles, F_equiv, N_cycles, F_orig, 1.0
            )

            # U4: Enable export/transfer buttons after successful compute
            for btn in [self._export_report_btn, self._export_json_btn,
                        self._export_png_btn, self._transfer_btn]:
                btn.setEnabled(True)

    def _on_scaling_computed(self, scaled: 'ScaledLooseningModel'):
        """Handle geometric scaling completion."""
        if HAS_SIMILITUDE:
            # BUG-03 fix: populate analysis with actual computed data
            self.analysis = LooseningSimlitudeAnalysis()
            self.analysis.scaled_model = scaled
            self.last_scaled_model = scaled

            # Update suggested configuration panel
            self.suggested_config_panel.update_config(scaled)

            # Generate example loosening curves using Jiang two-stage model
            N_model = np.array([0, 25, 50, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 5000])

            # Two-stage decay parameters (Jiang 2003)
            lambda1, lambda2 = 0.012, 0.003
            N_trans = 200

            F_model = np.zeros_like(N_model, dtype=float)
            for i, N in enumerate(N_model):
                if N <= N_trans:
                    # Stage I: rapid plastic deformation
                    F_model[i] = 1.0 - 0.15 * (1 - np.exp(-N / (N_trans / 3)))
                else:
                    # Stage II: gradual rotational loosening
                    F_trans = 1.0 - 0.15 * (1 - np.exp(-N_trans / (N_trans / 3)))
                    F_model[i] = F_trans * np.exp(-lambda2 * (N - N_trans))

            # Transform to prototype domain
            N_proto = N_model * scaled.scale_factor

            # Apply embedding correction (model has higher relative loss)
            F_proto = F_model + (1 - F_model) * (1 - scaled.embedding_correction)

            # Plot comparison
            self.comparison_panel.plot_loosening_comparison(
                N_model, F_model, N_proto, F_proto, scaled.scale_factor
            )

            # Update error analysis
            prototype_data = {
                'd': scaled.prototype_diameter,
                'p': scaled.prototype_pitch,
                'L': scaled.prototype_grip_length,
                'sigma_p': scaled.prototype_preload / (np.pi * (scaled.prototype_diameter * 0.9)**2 / 4),
                'f': scaled.prototype_frequency,
            }

            model_data = {
                'd': scaled.standard_diameter,
                'p': scaled.standard_pitch,
                'L': scaled.model_grip_length,
                'sigma_p': scaled.model_preload / (np.pi * (scaled.standard_diameter * 0.9)**2 / 4),
                'f': scaled.model_frequency,
            }

            self.error_panel.update_errors(prototype_data, model_data)

            # Switch to Suggested Model sub-tab inside Scaling
            # (Prototype=0, Results=1, Corrections=2, Suggested Model=3)
            self.scaling_panel.sub_tabs.setCurrentIndex(3)

            # U4: Enable export/transfer buttons after successful compute
            for btn in [self._export_report_btn, self._export_json_btn,
                        self._export_png_btn, self._send_to_solver_btn, self._transfer_btn]:
                btn.setEnabled(True)

    def _on_transfer_requested(self, elements: dict):
        """Handle transfer to MSD Builder request."""
        self.transfer_to_builder.emit(elements)

    def _transfer_suggested(self):
        """Transfer the suggested configuration to MSD Builder."""
        if self.last_scaled_model is None:
            QMessageBox.warning(self, "No Configuration",
                              "Compute a scaled model first using the Scaling tab.")
            return

        if HAS_SIMILITUDE:
            elements = create_msd_elements_from_scaled(self.last_scaled_model)
            self.transfer_to_builder.emit(elements)
            QMessageBox.information(self, "Transfer Complete",
                                  "Suggested configuration transferred to MSD Builder.\n"
                                  "Open the Model Builder tab to view.")

    def _send_to_solver(self):
        """U6: Emit scaled model parameters to the Solver tab."""
        if self.last_scaled_model is None:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Scaled Model",
                                "Run Geometric Scaling first to produce scaled parameters.")
            return
        sm = self.last_scaled_model
        params = {
            "F_preload": float(getattr(sm, "model_preload", 0.0)),
            "frequency": float(getattr(sm, "model_frequency", 0.0)),
            "n_cycles": int(getattr(sm, "model_cycles", 5000)),
            "bolt_diameter": float(getattr(sm, "standard_diameter", 16.0)),
            "pitch": float(getattr(sm, "standard_pitch", 2.0)),
        }
        self.send_to_solver.emit(params)

    def populate_from_model(self, params: dict):
        """U2: Populate parameter fields from MSD model data."""
        d = float(params.get("bolt_diameter", 16.0))
        p = float(params.get("pitch", 2.0))
        fp_n = float(params.get("preload", 50000.0))
        fp_kn = fp_n / 1000.0  # panels use kN
        freq = float(params.get("frequency", 25.0))
        mu = float(params.get("mu_initial", 0.12))

        # Populate GeometricScalingPanel prototype fields
        try:
            self.scaling_panel.proto_diameter_spin.setValue(d)
            self.scaling_panel.proto_pitch_spin.setValue(p)
            self.scaling_panel.proto_preload_spin.setValue(fp_kn)
            self.scaling_panel.proto_freq_spin.setValue(freq)
        except Exception:
            pass

        # Populate MultiBoltReductionPanel fields
        try:
            self.multi_bolt_panel.diameter_spin.setValue(d)
            self.multi_bolt_panel.pitch_spin.setValue(p)
            self.multi_bolt_panel.preload_spin.setValue(fp_kn)
            self.multi_bolt_panel.mu_thread_spin.setValue(mu)
            self.multi_bolt_panel.mu_bearing_spin.setValue(mu)
        except Exception:
            pass

    def refresh_theme(self):
        """Re-apply inline stylesheets on all sub-panels after theme change."""
        for panel in [self.multi_bolt_panel, self.scaling_panel,
                      self.pi_panel, self.suggested_config_panel,
                      self.error_panel, self.comparison_panel,
                      self.multi_bolt_comparison_panel]:
            if hasattr(panel, 'refresh_theme'):
                try:
                    panel.refresh_theme()
                except Exception:
                    pass

    def _export_plot_image(self):
        """Export comparison plot as PNG image (LS6)."""
        # Determine which comparison panel is active
        current_tab = self.analysis_tabs.currentIndex()
        if current_tab == 0:
            panel = self.multi_bolt_comparison_panel
        else:
            panel = self.comparison_panel

        if panel.current_figure is None:
            QMessageBox.warning(self, "No Plot",
                              "Generate a comparison plot first.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Plot Image",
            "similitude_plot.png",
            "PNG (*.png);;SVG (*.svg);;PDF (*.pdf);;All Files (*)"
        )

        if filepath:
            try:
                panel.current_figure.savefig(filepath, dpi=150,
                    bbox_inches='tight', facecolor=Theme.BASE)
                QMessageBox.information(self, "Export Complete",
                    f"Plot exported to {filepath}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error",
                    f"Failed to export plot:\n{str(e)}")

    def _export_report(self):
        """Export similitude analysis report."""
        if self.last_scaled_model is None and self.analysis is None:
            QMessageBox.warning(self, "No Analysis",
                              "Perform an analysis first.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Report",
            "similitude_report.md",
            "Markdown (*.md);;All Files (*)"
        )

        if filepath:
            with open(filepath, 'w') as f:
                f.write("# Similitude Analysis Report\n\n")
                f.write(f"Generated: {np.datetime64('now')}\n\n")

                if self.last_scaled_model:
                    sm = self.last_scaled_model
                    f.write("## Prototype Configuration\n\n")
                    f.write(f"- Bolt Size: M{sm.prototype_diameter:.0f}\n")
                    f.write(f"- Pitch: {sm.prototype_pitch:.2f} mm\n")
                    f.write(f"- Grip Length: {sm.prototype_grip_length:.1f} mm\n")
                    f.write(f"- Preload: {sm.prototype_preload/1000:.1f} kN\n")
                    f.write(f"- Test Frequency: {sm.prototype_frequency:.1f} Hz\n\n")

                    f.write("## Suggested Model Configuration\n\n")
                    f.write(f"- Scale Factor: {sm.scale_factor:.3f}\n")
                    f.write(f"- Bolt Size: M{sm.standard_diameter:.0f}\n")
                    f.write(f"- Pitch: {sm.standard_pitch:.2f} mm\n")
                    f.write(f"- Grip Length: {sm.model_grip_length:.1f} mm\n")
                    f.write(f"- Preload: {sm.model_preload:.0f} N ({sm.model_preload/1000:.2f} kN)\n")
                    f.write(f"- Test Frequency: {sm.model_frequency:.1f} Hz\n\n")

                    f.write("## Scale Effect Corrections\n\n")
                    f.write(f"- Friction Correction (C_mu): {sm.friction_correction:.3f}\n")
                    f.write(f"- Embedding Correction (C_e): {sm.embedding_correction:.3f}\n")
                    f.write(f"- Quality Score: {sm.quality_score*100:.1f}%\n\n")

                    if sm.warnings:
                        f.write("## Warnings\n\n")
                        for w in sm.warnings:
                            f.write(f"- {w}\n")

                if self.analysis:
                    report = self.analysis.generate_report()
                    f.write("\n## Π-Groups\n\n")
                    for pg in report.get('pi_groups', []):
                        f.write(f"- {pg.get('symbol', '')}: {pg.get('name', '')} = "
                               f"{pg.get('prototype_value', 0):.4f}\n")

            QMessageBox.information(self, "Export Complete",
                                  f"Report exported to {filepath}")

    def _export_json(self):
        """Export analysis data to JSON."""
        if self.last_scaled_model is None and self.analysis is None:
            QMessageBox.warning(self, "No Analysis",
                              "Perform an analysis first.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export JSON",
            "similitude_data.json",
            "JSON (*.json);;All Files (*)"
        )

        if filepath:
            import json

            data = {}

            if self.last_scaled_model:
                sm = self.last_scaled_model
                data['prototype'] = {
                    'diameter': sm.prototype_diameter,
                    'pitch': sm.prototype_pitch,
                    'grip_length': sm.prototype_grip_length,
                    'preload': sm.prototype_preload,
                    'frequency': sm.prototype_frequency,
                }
                data['model'] = {
                    'scale_factor': sm.scale_factor,
                    'diameter': sm.standard_diameter,
                    'pitch': sm.standard_pitch,
                    'grip_length': sm.model_grip_length,
                    'preload': sm.model_preload,
                    'frequency': sm.model_frequency,
                }
                data['corrections'] = {
                    'friction': sm.friction_correction,
                    'embedding': sm.embedding_correction,
                }
                data['quality'] = sm.quality_score

            if self.analysis:
                data['analysis'] = self.analysis.generate_report()

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            QMessageBox.information(self, "Export Complete",
                                  f"Data exported to {filepath}")


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_similitude_tab(parent=None) -> QWidget:
    """
    Factory function to create the appropriate similitude tab.

    Returns EnhancedSimilitudeTab if similitude module is available,
    otherwise returns a basic placeholder.
    """
    if HAS_SIMILITUDE:
        return EnhancedSimilitudeTab(parent)
    else:
        # Return placeholder
        placeholder = QWidget(parent)
        layout = QVBoxLayout(placeholder)

        label = QLabel("Similitude Module Not Available")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"""
            color: {Theme.OVERLAY};
            font-size: 14pt;
            padding: 40px;
        """)

        info = QLabel(
            "The loosening similitude module could not be loaded.\n\n"
            "Please ensure the following file exists:\n"
            "bolt_analysis_studio/core/similitude/loosening_similitude.py\n\n"
            "This module enables:\n"
            "• Multi-bolt to single-bolt reduction\n"
            "• Geometric scaling with loosening preservation\n"
            "• Π-group analysis for loosening behavior"
        )
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet(f"color: {Theme.SUBTEXT};")
        info.setWordWrap(True)

        layout.addStretch()
        layout.addWidget(label)
        layout.addWidget(info)
        layout.addStretch()

        return placeholder


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Apply dark theme
    app.setStyleSheet(f"""
        QWidget {{
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
            border: 1px solid {Theme.SURFACE2};
            border-radius: 4px;
            padding: 6px 16px;
        }}
        QPushButton:hover {{
            background-color: {Theme.SURFACE2};
        }}
        QPushButton#primary {{
            background-color: {Theme.BLUE};
            color: {Theme.BUTTON_TEXT};
        }}
        QPushButton#success {{
            background-color: {Theme.GREEN};
            color: {Theme.BUTTON_TEXT};
        }}
        QTableWidget {{
            background-color: {Theme.BASE};
            gridline-color: {Theme.SURFACE1};
        }}
        QHeaderView::section {{
            background-color: {Theme.SURFACE0};
            color: {Theme.BLUE};
            padding: 6px;
            border: none;
        }}
    """)

    window = create_similitude_tab()
    window.setWindowTitle("Similitude Tab Test")
    window.resize(1000, 700)
    window.show()

    sys.exit(app.exec())
