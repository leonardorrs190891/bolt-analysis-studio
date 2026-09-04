"""
Bolt Analysis Studio v4.0 - Main Window
PyQt6 Implementation

Prof. Leonardo Rosa Ribeiro da Silva, PhD
January 2026

Main application window with 6 tabs:
1. Project - Project metadata, standards, units
2. Model Builder - MSD model construction
3. Solver - Analysis configuration and execution
4. Results - Time history, safety factors
5. Similitude - Scaling analysis and Π-groups
6. Reports - Documentation generation
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

# Import application modules
from bolt_analysis_studio.core.app_state import (
    get_app_state, AppState, ProjectInfo as AppProjectInfo,
    AnalysisResult, PreloadAnalysisResult, TimeIntegrationResult,
    CoupledLooseningResult
)
from bolt_analysis_studio.core.solver_worker import (
    SolverWorker, SolverThread, AnalysisConfig,
    PreloadAnalysisConfig, TimeIntegrationConfig, CoupledLooseningConfig
)
from bolt_analysis_studio.core.project_io import ProjectIO
from bolt_analysis_studio.core.models.model import compute_contact_stiffnesses
from bolt_analysis_studio.visualization.plot_manager import PlotWidget, PlotManager, PlotEditorWindow

# Import enhanced similitude tab
try:
    from bolt_analysis_studio.gui.similitude_tab import (
        EnhancedSimilitudeTab, create_similitude_tab
    )
    HAS_ENHANCED_SIMILITUDE = True
except ImportError:
    HAS_ENHANCED_SIMILITUDE = False

# Import documentation tab
try:
    from bolt_analysis_studio.gui.documentation_tab import DocumentationTab
    HAS_DOCUMENTATION_TAB = True
except ImportError:
    HAS_DOCUMENTATION_TAB = False

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QGroupBox, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QTextEdit, QProgressBar, QSplitter, QFrame, QScrollArea,
    QFileDialog, QMessageBox, QStatusBar, QMenuBar, QMenu,
    QToolBar, QSizePolicy, QTableWidget, QTableWidgetItem,
    QHeaderView, QTreeWidget, QTreeWidgetItem, QDialog,
    QDialogButtonBox, QRadioButton, QButtonGroup, QSlider,
    QStackedWidget, QListWidget, QListWidgetItem, QGridLayout,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QThread, pyqtSlot
from PyQt6.QtGui import (
    QAction, QIcon, QFont, QColor, QPalette, QPixmap,
    QKeySequence, QFontDatabase, QGuiApplication, QTextDocument,
    QShortcut,
)
from PyQt6.QtPrintSupport import QPrinter
from datetime import datetime
import os

from bolt_analysis_studio.gui.theme import Theme
from bolt_analysis_studio.gui.icons import icon


# =============================================================================
# PROJECT DATA STRUCTURES
# =============================================================================

@dataclass
class ProjectInfo:
    """Project metadata and configuration."""
    name: str = "Untitled Project"
    description: str = ""
    author: str = ""
    company: str = ""
    institution: str = ""
    project_number: str = ""
    revision: str = "A"
    notes: str = ""

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

    # File path
    filepath: Optional[str] = None
    template_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "company": self.company,
            "institution": self.institution,
            "project_number": self.project_number,
            "revision": self.revision,
            "notes": self.notes,
            "standard": self.standard,
            "material_standard": self.material_standard,
            "flange_standard": self.flange_standard,
            "length_unit": self.length_unit,
            "force_unit": self.force_unit,
            "pressure_unit": self.pressure_unit,
            "temperature_unit": self.temperature_unit,
            "created": self.created,
            "modified": self.modified,
            "filepath": self.filepath,
            "template_name": self.template_name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectInfo':
        """Create from dictionary. Uses .get() for backward compatibility."""
        return cls(
            name=data.get("name", "Untitled Project"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            company=data.get("company", ""),
            institution=data.get("institution", ""),
            project_number=data.get("project_number", ""),
            revision=data.get("revision", "A"),
            notes=data.get("notes", ""),
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
            template_name=data.get("template_name", ""),
        )


# =============================================================================
# RECENT PROJECTS MANAGER
# =============================================================================

from PyQt6.QtCore import QSettings

class RecentProjectsManager:
    """Persistent recent-projects list backed by QSettings."""
    MAX_ITEMS = 10
    SETTINGS_KEY = "recent_projects"
    ORG = "BoltAnalysisStudio"
    APP = "BoltAnalysisStudio"

    @staticmethod
    def get() -> list:
        s = QSettings(RecentProjectsManager.ORG, RecentProjectsManager.APP)
        raw = s.value(RecentProjectsManager.SETTINGS_KEY, "[]")
        try:
            return json.loads(raw) if isinstance(raw, str) else list(raw)
        except Exception:
            return []

    @staticmethod
    def add(path: str):
        items = RecentProjectsManager.get()
        items = [i for i in items if i.get("path") != path]
        items.insert(0, {
            "path": path,
            "name": Path(path).stem,
            "modified_iso": datetime.now().isoformat(),
        })
        items = items[:RecentProjectsManager.MAX_ITEMS]
        s = QSettings(RecentProjectsManager.ORG, RecentProjectsManager.APP)
        s.setValue(RecentProjectsManager.SETTINGS_KEY, json.dumps(items))

    @staticmethod
    def remove(path: str):
        items = [i for i in RecentProjectsManager.get() if i.get("path") != path]
        s = QSettings(RecentProjectsManager.ORG, RecentProjectsManager.APP)
        s.setValue(RecentProjectsManager.SETTINGS_KEY, json.dumps(items))

    @staticmethod
    def clear():
        s = QSettings(RecentProjectsManager.ORG, RecentProjectsManager.APP)
        s.setValue(RecentProjectsManager.SETTINGS_KEY, "[]")


# =============================================================================
# PROJECT TEMPLATES
# =============================================================================

PROJECT_TEMPLATES = {
    "Junker Test": {
        "standard": "VDI 2230 Part 1 (2015)",
        "material_standard": "ISO 898-1:2013",
        "flange_standard": "API 6A (2018)",
        "template_name": "Junker Test",
    },
    "API 6A Flange": {
        "standard": "VDI 2230 Part 1 (2015)",
        "material_standard": "ASTM A193/A193M",
        "flange_standard": "API 6A (2018)",
        "template_name": "API 6A Flange",
    },
    "ISO Metric Flange": {
        "standard": "EN 1591-1 (2013)",
        "material_standard": "ISO 898-1:2013",
        "flange_standard": "EN 1092-1",
        "template_name": "ISO Metric Flange",
    },
    "ASME Flange": {
        "standard": "ASME PCC-1 (2022)",
        "material_standard": "ASTM A193/A193M",
        "flange_standard": "ASME B16.5",
        "template_name": "ASME Flange",
    },
}


# =============================================================================
# TAB WIDGETS
# =============================================================================

def _set_combo(combo: 'QComboBox', text: str):
    """Set combo to item matching text, or leave unchanged if not found."""
    idx = combo.findText(text)
    if idx >= 0:
        combo.setCurrentIndex(idx)


class ProjectTab(QWidget):
    """Tab 1: Project information and settings — Option B layout."""

    # Signals
    project_info_changed = pyqtSignal(dict)
    open_recent_requested = pyqtSignal(str)
    template_requested = pyqtSignal(str)
    save_requested = pyqtSignal()
    new_analysis_wizard_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_info = ProjectInfo()
        self._status_state = "NEW"
        self.setMinimumSize(540, 380)
        self._setup_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        """Build Option-B layout: hero bar + QSplitter(left scroll, right)."""
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Hero bar
        root.addWidget(self._create_hero_bar())

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setContentsMargins(0, 0, 0, 0)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        # Left panel inside QScrollArea
        left_panel = self._create_left_panel()
        left_scroll = QScrollArea()
        left_scroll.setWidget(left_panel)
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setFrameShape(QFrame.Shape.NoFrame)
        left_scroll.setMinimumWidth(280)

        # Right panel inside QScrollArea so it survives small window heights
        right_panel = self._create_right_panel()
        right_scroll = QScrollArea()
        right_scroll.setWidget(right_panel)
        right_scroll.setWidgetResizable(True)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        right_scroll.setFrameShape(QFrame.Shape.NoFrame)
        right_scroll.setMinimumWidth(240)

        splitter.addWidget(left_scroll)
        splitter.addWidget(right_scroll)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([400, 280])

        content_wrapper = QWidget()
        cw_layout = QVBoxLayout(content_wrapper)
        cw_layout.setContentsMargins(8, 8, 8, 8)
        cw_layout.setSpacing(0)
        cw_layout.addWidget(splitter)

        root.addWidget(content_wrapper)

        # Tab-order
        QWidget.setTabOrder(self.name_edit, self.description_edit)
        QWidget.setTabOrder(self.description_edit, self.author_edit)
        QWidget.setTabOrder(self.author_edit, self.company_edit)
        QWidget.setTabOrder(self.company_edit, self.institution_edit)
        QWidget.setTabOrder(self.institution_edit, self.project_no_edit)
        QWidget.setTabOrder(self.project_no_edit, self.revision_edit)

        # Load real recent projects
        self._load_recent_projects()

    def _create_hero_bar(self) -> QFrame:
        bar = QFrame()
        bar.setFixedHeight(Theme.HERO_BAR_HEIGHT)
        bar.setObjectName("hero_bar")
        # Styling lives in Theme.get_stylesheet() under QFrame#hero_bar.

        lay = QHBoxLayout(bar)
        lay.setContentsMargins(Theme.SPACING_XL, 0, Theme.SPACING_XL, 0)
        lay.setSpacing(12)

        app_label = QLabel("BAS v4.0")
        app_label.setObjectName("heroAppLabel")
        app_label.setMinimumWidth(0)
        app_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self._hero_project_name = QLabel("Untitled Project")
        self._hero_project_name.setObjectName("heroTitle")
        self._hero_project_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._status_badge = QLabel("NEW")
        self._status_badge.setFixedSize(Theme.STATUS_BADGE_WIDTH, Theme.STATUS_BADGE_HEIGHT)
        self._status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_badge.setStyleSheet(Theme.status_badge_stylesheet(Theme.TEAL))

        hero_save_btn = QPushButton("Save")
        hero_save_btn.setObjectName("primary")
        hero_save_btn.setMinimumWidth(64)
        hero_save_btn.clicked.connect(self.save_requested.emit)

        lay.addWidget(app_label)
        lay.addStretch()
        lay.addWidget(self._hero_project_name)
        lay.addStretch()
        lay.addWidget(self._status_badge)
        lay.addWidget(hero_save_btn)

        return bar

    def _create_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(12)

        # --- Project Information ---
        info_group = QGroupBox("Project Information")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(8)
        info_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        info_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        import getpass
        self.name_edit = QLineEdit(self.project_info.name)
        self.name_edit.textChanged.connect(self._on_name_changed)

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Project description...")
        self.description_edit.setMinimumHeight(100)
        self.description_edit.setMaximumHeight(180)
        self.description_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        self.author_edit = QLineEdit()
        if not self.project_info.author:
            try:
                self.author_edit.setText(getpass.getuser())
            except Exception:
                pass

        self.company_edit = QLineEdit(self.project_info.company)
        self.institution_edit = QLineEdit(self.project_info.institution)
        self.project_no_edit = QLineEdit(self.project_info.project_number)
        self.revision_edit = QLineEdit(self.project_info.revision)
        self.revision_edit.setMaximumWidth(80)

        info_layout.addRow("Project Name *:", self.name_edit)
        info_layout.addRow("Description:", self.description_edit)
        info_layout.addRow("Author:", self.author_edit)
        info_layout.addRow("Company:", self.company_edit)
        info_layout.addRow("Institution:", self.institution_edit)
        info_layout.addRow("Project No.:", self.project_no_edit)
        info_layout.addRow("Revision:", self.revision_edit)

        # Connect all fields to signal emitter
        for widget in (self.name_edit, self.author_edit, self.company_edit,
                        self.institution_edit, self.project_no_edit, self.revision_edit):
            widget.textChanged.connect(self._emit_info_changed)
        self.description_edit.textChanged.connect(self._emit_info_changed)

        layout.addWidget(info_group)

        # --- Standards & Codes ---
        standards_group = QGroupBox("Standards & Codes")
        standards_layout = QFormLayout(standards_group)
        standards_layout.setSpacing(8)
        standards_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        standards_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.standard_combo = QComboBox()
        self.standard_combo.addItems([
            "VDI 2230 Part 1 (2015)",
            "VDI 2230 Part 2 (2019)",
            "EN 1591-1 (2013)",
            "ASME PCC-1 (2022)"
        ])
        self.standard_combo.setToolTip(
            "VDI 2230: German engineering standard for bolted joints.\n"
            "Affects: safety factor calculation, tightening torque, load case definitions."
        )

        self.material_combo = QComboBox()
        self.material_combo.addItems([
            "ASTM A193/A193M",
            "ASTM A320/A320M",
            "ISO 898-1:2013",
            "EN ISO 3506-1"
        ])
        self.material_combo.setToolTip(
            "Material standard used for bolt grade lookup in the materials database.\n"
            "Affects: yield strength, proof load, allowable stress values."
        )

        self.flange_combo = QComboBox()
        self.flange_combo.addItems([
            "API 6A (2018)",
            "ASME B16.5",
            "ASME B16.47",
            "EN 1092-1"
        ])
        self.flange_combo.setToolTip(
            "Flange design standard.\n"
            "Affects: seating stress, gasket factors (m, y), pressure ratings."
        )

        standards_layout.addRow("Analysis Standard:", self.standard_combo)
        standards_layout.addRow("Material Standard:", self.material_combo)
        standards_layout.addRow("Flange Standard:", self.flange_combo)

        layout.addWidget(standards_group)

        # --- Timestamps ---
        ts_group = QGroupBox("Project History")
        ts_layout = QFormLayout(ts_group)
        ts_layout.setSpacing(4)

        self._created_label = QLabel("—")
        self._modified_label = QLabel("—")
        for lbl in (self._created_label, self._modified_label):
            lbl.setObjectName("caption")

        ts_layout.addRow("Created:", self._created_label)
        ts_layout.addRow("Modified:", self._modified_label)

        layout.addWidget(ts_group)

        # --- Notes ---
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_group)
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Free-form notes, observations, references...")
        self.notes_edit.setMaximumHeight(100)
        self.notes_edit.textChanged.connect(self._emit_info_changed)
        notes_layout.addWidget(self.notes_edit)
        layout.addWidget(notes_group)

        layout.addStretch()
        self._update_timestamps(self.project_info)
        return panel

    def _create_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(12)

        # --- Quick Actions 2×2 grid ---
        actions_group = QGroupBox("Quick Actions")
        actions_outer = QVBoxLayout(actions_group)
        actions_outer.setSpacing(6)

        wizard_btn = QPushButton("🧙 Nova Análise (Wizard)")
        wizard_btn.setObjectName("primary")
        wizard_btn.setMinimumHeight(48)
        wizard_btn.setToolTip(
            "Guided 5-step wizard: joint type → bolt → loading → reference CSV → review.\n"
            "Generates a starter model that remains fully editable in the MSD Builder.")
        wizard_btn.clicked.connect(self.new_analysis_wizard_requested.emit)
        actions_outer.addWidget(wizard_btn)

        grid_host = QWidget()
        grid = QGridLayout(grid_host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(6)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        actions_outer.addWidget(grid_host)

        new_btn = QPushButton("New Project")
        new_btn.setObjectName("new_btn")
        open_btn = QPushButton("Open Project")
        open_btn.setObjectName("open_btn")
        save_btn = QPushButton("Save Project")
        save_btn.setObjectName("primary")
        exp_btn = QPushButton("Export Report")
        exp_btn.setObjectName("export_btn")

        for btn in (new_btn, open_btn, save_btn, exp_btn):
            btn.setMinimumHeight(44)
            btn.setMinimumWidth(100)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        grid.addWidget(new_btn, 0, 0)
        grid.addWidget(open_btn, 0, 1)
        grid.addWidget(save_btn, 1, 0)
        grid.addWidget(exp_btn, 1, 1)

        layout.addWidget(actions_group)

        # --- Recent Projects ---
        recent_group = QGroupBox("Recent Projects")
        recent_layout = QVBoxLayout(recent_group)

        self.recent_list = QListWidget()
        self.recent_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.recent_list.customContextMenuRequested.connect(self._on_recent_context_menu)
        self.recent_list.itemDoubleClicked.connect(self._on_recent_double_click)
        self.recent_list.setMinimumHeight(60)
        self.recent_list.setMaximumHeight(150)
        recent_layout.addWidget(self.recent_list)

        layout.addWidget(recent_group)

        # --- Units Configuration ---
        units_group = QGroupBox("Units Configuration")
        units_layout = QFormLayout(units_group)
        units_layout.setSpacing(6)
        units_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        units_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.length_combo = QComboBox()
        self.length_combo.addItems(["mm", "m", "in", "ft"])
        self.force_combo = QComboBox()
        self.force_combo.addItems(["N", "kN", "lbf", "kgf"])
        self.pressure_combo = QComboBox()
        self.pressure_combo.addItems(["MPa", "GPa", "psi", "bar"])
        self.temp_combo = QComboBox()
        self.temp_combo.addItems(["°C", "K", "°F"])

        self._units_warning = QLabel("")
        self._units_warning.setStyleSheet(
            f"color: {Theme.PEACH}; font-size: 11px;"
        )
        self._units_warning.setWordWrap(True)
        self._units_warning.setVisible(False)

        _units_tip = ("Somente exibição/metadados — não converte os valores "
                      "do modelo.")
        for combo in (self.length_combo, self.force_combo,
                      self.pressure_combo, self.temp_combo):
            combo.setToolTip(_units_tip)
            combo.currentIndexChanged.connect(self._on_unit_changed)

        units_layout.addRow("Length:", self.length_combo)
        units_layout.addRow("Force:", self.force_combo)
        units_layout.addRow("Pressure:", self.pressure_combo)
        units_layout.addRow("Temperature:", self.temp_combo)

        # Persistent clarification: unit selection is display/metadata only and
        # does NOT convert existing model values (real conversion is out of scope).
        _units_hint = QLabel(
            "ℹ Somente exibição/metadados — não converte os valores do modelo."
        )
        _units_hint.setWordWrap(True)
        _units_hint.setStyleSheet(
            f"color: {Theme.SUBTEXT}; font-size: 11px; font-style: italic;"
        )
        units_layout.addRow("", _units_hint)
        units_layout.addRow("", self._units_warning)

        layout.addWidget(units_group)

        # --- Templates ---
        tmpl_group = QGroupBox("Templates & Presets")
        tmpl_layout = QVBoxLayout(tmpl_group)
        tmpl_layout.setSpacing(6)

        for name in PROJECT_TEMPLATES:
            btn = QPushButton(name)
            btn.setMinimumHeight(Theme.BUTTON_MIN_HEIGHT_TOOLBAR)
            btn.setMinimumWidth(100)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(lambda checked, n=name: self._apply_template(n))
            tmpl_layout.addWidget(btn)

        layout.addWidget(tmpl_group)

        # --- Model Summary ---
        summary_group = QGroupBox("Model Summary")
        summary_layout = QFormLayout(summary_group)
        summary_layout.setSpacing(4)

        self._summary_elements = QLabel("—")
        self._summary_dof = QLabel("—")
        self._summary_ksys = QLabel("—")
        self._summary_contacts = QLabel("—")
        self._summary_status = QLabel("—")

        for lbl in (self._summary_elements, self._summary_dof,
                    self._summary_ksys, self._summary_contacts, self._summary_status):
            lbl.setStyleSheet(
                f"color: {Theme.TEXT}; font-size: 11px;"
            )

        summary_layout.addRow("Elements:", self._summary_elements)
        summary_layout.addRow("DOF:", self._summary_dof)
        summary_layout.addRow("k_sys:", self._summary_ksys)
        summary_layout.addRow("Contacts:", self._summary_contacts)
        summary_layout.addRow("Status:", self._summary_status)

        layout.addWidget(summary_group)
        layout.addStretch()

        return panel

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_name_changed(self, text: str):
        """Validate project name and update hero bar."""
        self._hero_project_name.setText(text or "Untitled Project")
        is_valid = bool(text.strip())
        self.name_edit.setStyleSheet(
            "" if is_valid else f"border-left: 3px solid {Theme.RED};"
        )
        self._emit_info_changed()

    def _emit_info_changed(self, *_):
        self.project_info_changed.emit(self.get_project_info().to_dict())

    def _on_unit_changed(self, _=None):
        from bolt_analysis_studio.core.app_state import get_app_state
        try:
            model = get_app_state().model
            if model and len(getattr(model, 'elements', [])) > 0:
                self._units_warning.setText(
                    "Unit changes do not auto-convert existing model values."
                )
                self._units_warning.setVisible(True)
                return
        except Exception:
            pass
        self._units_warning.setVisible(False)

    def _apply_template(self, name: str):
        tmpl = PROJECT_TEMPLATES.get(name, {})
        if not tmpl:
            return
        std = tmpl.get("standard", "")
        mat = tmpl.get("material_standard", "")
        fla = tmpl.get("flange_standard", "")
        idx = self.standard_combo.findText(std)
        if idx >= 0:
            self.standard_combo.setCurrentIndex(idx)
        idx = self.material_combo.findText(mat)
        if idx >= 0:
            self.material_combo.setCurrentIndex(idx)
        idx = self.flange_combo.findText(fla)
        if idx >= 0:
            self.flange_combo.setCurrentIndex(idx)
        self.project_info.template_name = tmpl.get("template_name", name)
        self.template_requested.emit(name)

    # ------------------------------------------------------------------
    # Recent projects
    # ------------------------------------------------------------------

    def _load_recent_projects(self):
        self.recent_list.clear()
        for entry in RecentProjectsManager.get():
            path = entry.get("path", "")
            name = entry.get("name", Path(path).stem if path else "Unknown")
            mod = entry.get("modified_iso", "")
            try:
                mod_str = datetime.fromisoformat(mod).strftime("%Y-%m-%d")
            except Exception:
                mod_str = "—"
            exists = Path(path).exists() if path else False
            display = f"  {name}" if exists else f"  {name}  [not found]"
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, path)
            item.setToolTip(f"{path}\nModified: {mod_str}")
            if not exists:
                item.setForeground(QColor(Theme.OVERLAY))
            self.recent_list.addItem(item)

    def _on_recent_double_click(self, item: QListWidgetItem):
        path = item.data(Qt.ItemDataRole.UserRole)
        if path and Path(path).exists():
            self.open_recent_requested.emit(path)
        else:
            QMessageBox.warning(self, "File Not Found", f"Could not find:\n{path}")

    def _on_recent_context_menu(self, pos):
        item = self.recent_list.itemAt(pos)
        if item is None:
            return
        path = item.data(Qt.ItemDataRole.UserRole)
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        open_act = menu.addAction("Open")
        remove_act = menu.addAction("Remove from list")
        open_folder_act = menu.addAction("Open folder")
        action = menu.exec(self.recent_list.mapToGlobal(pos))
        if action == open_act and path and Path(path).exists():
            self.open_recent_requested.emit(path)
        elif action == remove_act:
            RecentProjectsManager.remove(path)
            self._load_recent_projects()
        elif action == open_folder_act and path:
            import subprocess
            folder = str(Path(path).parent)
            try:
                subprocess.Popen(f'explorer "{folder}"')
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Status & summary
    # ------------------------------------------------------------------

    def set_status(self, status: str, path: str = ""):
        colors = {
            "NEW":      (Theme.TEAL,  "NEW"),
            "MODIFIED": (Theme.PEACH, "UNSAVED"),
            "SAVED":    (Theme.GREEN, "SAVED"),
            "ERROR":    (Theme.RED,   "ERROR"),
        }
        bg, label = colors.get(status, (Theme.OVERLAY, status))
        self._status_badge.setText(label)
        self._status_badge.setStyleSheet(Theme.status_badge_stylesheet(bg))
        self._status_state = status  # remember for refresh_theme
        if path:
            self._status_badge.setToolTip(path)

    def refresh_theme(self):
        """Re-apply inline stylesheets after a theme change.

        Fixed-chrome widgets live in the cached QSS and refresh automatically;
        only widgets whose colour depends on runtime state (status badge,
        validation indicator) need explicit re-application here.
        """
        self.set_status(getattr(self, "_status_state", "NEW"))
        self._units_warning.setStyleSheet(
            f"color: {Theme.PEACH}; font-size: 11px;"
        )
        for lbl in (self._summary_elements, self._summary_dof,
                    self._summary_ksys, self._summary_contacts,
                    self._summary_status):
            lbl.setStyleSheet(
                f"color: {Theme.TEXT}; font-size: 11px;"
            )
        self._on_name_changed(self.name_edit.text())

    def update_model_summary(self, model):
        if model is None:
            for lbl in (self._summary_elements, self._summary_dof,
                        self._summary_ksys, self._summary_contacts, self._summary_status):
                lbl.setText("—")
            return
        try:
            n_el = len(getattr(model, 'elements', []))
            n_contacts = len(getattr(model, 'contacts', []))
            self._summary_elements.setText(str(n_el))
            self._summary_contacts.setText(str(n_contacts))
            try:
                M, K, C = model.assemble_matrices()
                self._summary_dof.setText(str(K.shape[0]))
                import numpy as _np
                diag = _np.diag(K)
                sig = diag[diag > 1e3]
                if len(sig) >= 2:
                    k_sys = 1.0 / _np.sum(1.0 / sig)
                    self._summary_ksys.setText(f"{k_sys:.3g} N/m")
                else:
                    self._summary_ksys.setText("—")
            except Exception:
                self._summary_dof.setText("—")
                self._summary_ksys.setText("—")
            self._summary_status.setText("Valid" if n_el > 0 else "Empty")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Data access
    # ------------------------------------------------------------------

    def _update_timestamps(self, info: ProjectInfo):
        fmt = "%Y-%m-%d  %H:%M"
        try:
            c = datetime.fromisoformat(info.created).strftime(fmt)
        except Exception:
            c = "—"
        try:
            m = datetime.fromisoformat(info.modified).strftime(fmt)
        except Exception:
            m = "—"
        self._created_label.setText(c)
        self._modified_label.setText(m)

    def get_project_info(self) -> ProjectInfo:
        """Read all UI fields into self.project_info and return it."""
        self.project_info.name = self.name_edit.text()
        self.project_info.description = self.description_edit.toPlainText()
        self.project_info.author = self.author_edit.text()
        self.project_info.company = self.company_edit.text()
        self.project_info.institution = self.institution_edit.text()
        self.project_info.project_number = self.project_no_edit.text()
        self.project_info.revision = self.revision_edit.text()
        self.project_info.notes = self.notes_edit.toPlainText()
        self.project_info.standard = self.standard_combo.currentText()
        self.project_info.material_standard = self.material_combo.currentText()
        self.project_info.flange_standard = self.flange_combo.currentText()
        self.project_info.length_unit = self.length_combo.currentText()
        self.project_info.force_unit = self.force_combo.currentText()
        self.project_info.pressure_unit = self.pressure_combo.currentText()
        self.project_info.temperature_unit = self.temp_combo.currentText()
        self.project_info.modified = datetime.now().isoformat()
        return self.project_info

    def set_project_info(self, info: ProjectInfo):
        """Populate all UI fields from a ProjectInfo object."""
        self.project_info = info
        self.name_edit.blockSignals(True)
        self.name_edit.setText(info.name)
        self.name_edit.blockSignals(False)
        self._hero_project_name.setText(info.name or "Untitled Project")
        self.description_edit.setPlainText(info.description)
        self.author_edit.setText(info.author)
        self.company_edit.setText(info.company)
        self.institution_edit.setText(info.institution)
        self.project_no_edit.setText(info.project_number)
        self.revision_edit.setText(info.revision)
        self.notes_edit.setPlainText(info.notes)
        _set_combo(self.standard_combo, info.standard)
        _set_combo(self.material_combo, info.material_standard)
        _set_combo(self.flange_combo, info.flange_standard)
        _set_combo(self.length_combo, info.length_unit)
        _set_combo(self.force_combo, info.force_unit)
        _set_combo(self.pressure_combo, info.pressure_unit)
        _set_combo(self.temp_combo, info.temperature_unit)
        self._update_timestamps(info)
        self.set_status("SAVED" if info.filepath else "NEW",
                        info.filepath or "")


class ModelBuilderTab(QWidget):
    """Tab 2: MSD Model Builder embedded directly (no floating window).

    Composes an `MSDBuilderWindow` and extracts its central widget +
    menu bar + status bar so the full builder (palette / schematic /
    inspector) lives inside the tab. The floating window instance stays
    alive for backwards compatibility with legacy signal wiring but is
    never shown. Adds a header bar with Case Studies / Validate /
    Send-to-Solver buttons.
    """

    msd_builder_requested = pyqtSignal()
    case_studies_requested = pyqtSignal()
    validate_requested = pyqtSignal()
    send_to_solver_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        from bolt_analysis_studio.gui.msd_builder import MSDBuilderWindow

        # Create the builder as a hidden QMainWindow so we can lift its
        # central widget / menu / status into our tab layout.
        self.builder = MSDBuilderWindow(self)
        self.builder.hide()
        # Stop the close-confirm dialog from firing if the builder is
        # ever asked to close programmatically.
        self.builder.closeEvent = lambda e: e.accept()

        central = self.builder.centralWidget()
        menubar = self.builder.menuBar()
        statusbar = self.builder.statusBar()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1) Menu bar (File / Edit / View / Tools / Help) — already built
        #    in MSDBuilderWindow._setup_menubar. Mount as a top widget.
        layout.addWidget(menubar)

        # 2) Header bar: title + Case Studies + validation label + Validate + Send to Solver.
        header_widget = QWidget()
        header = QHBoxLayout(header_widget)
        header.setContentsMargins(10, 6, 10, 6)
        header.setSpacing(8)

        title = QLabel("🔧 MSD Model Builder")
        title.setObjectName("heading")
        header.addWidget(title)

        self.validation_label = QLabel("⚠️ No model loaded")
        self.validation_label.setStyleSheet(f"color: {Theme.YELLOW};")
        header.addWidget(self.validation_label)

        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet(f"color: {Theme.SUBTEXT}; font-family: {Theme.FONT_MONO};")
        header.addWidget(self.summary_label)
        header.addStretch()

        case_studies_btn = QPushButton("📁 Case Studies")
        case_studies_btn.setToolTip(
            "Load a pre-built case study (âncora interna lab trials + literature validation cases)."
        )
        case_studies_btn.clicked.connect(self.case_studies_requested.emit)
        header.addWidget(case_studies_btn)

        validate_btn = QPushButton("✓ Validate Model")
        validate_btn.setObjectName("success")
        validate_btn.setToolTip("Check the model topology and matrices for issues.")
        validate_btn.clicked.connect(self.validate_requested.emit)
        header.addWidget(validate_btn)

        send_btn = QPushButton("▶ Send to Solver")
        send_btn.setObjectName("primary")
        send_btn.setToolTip(
            "Export the current model to the Solver tab and switch to it."
        )
        send_btn.clicked.connect(self.send_to_solver_requested.emit)
        header.addWidget(send_btn)

        layout.addWidget(header_widget)

        # 3) The full builder central widget (palette + schematic + inspector).
        layout.addWidget(central, stretch=1)

        # 4) Builder status bar (DOF count, preload display, etc.)
        layout.addWidget(statusbar)

        # Expose sub-widgets for external code that reaches into the tab.
        self.schematic = self.builder.schematic
        self.inspector = self.builder.inspector
        self.palette = self.builder.palette

        # Backwards-compat empty containers so legacy references don't crash.
        self.summary_labels: Dict[str, QLabel] = {}
        self.elements_table = None

    def update_summary(self, stats: Dict[str, Any]):
        """Update the compact header summary line."""
        n_elem = stats.get("n_elements", 0)
        n_dof = stats.get("n_dof", 0)
        f_n = stats.get("f_n", 0)
        phi = stats.get("phi", 0)
        self.summary_label.setText(
            f"{n_elem} elements · {n_dof} DOF · f_n={f_n:.1f} Hz · Φ={phi:.3f}"
        )


class SolverTab(QWidget):
    """Tab 3: Analysis solver configuration with responsive layout."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the solver tab UI with responsive splitter layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Main splitter for left/right panels (resizable)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setHandleWidth(6)
        self.main_splitter.setChildrenCollapsible(False)

        # =====================================================================
        # LEFT PANEL - Settings (in scroll area)
        # =====================================================================
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setMinimumWidth(280)
        left_scroll.setMaximumWidth(500)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(8)

        # =====================================================================
        # LOADING SUMMARY (Read-only - configured in MSD Builder)
        # =====================================================================
        # NOTE: Loading and friction parameters are now configured in the
        # MSD Builder tab (Tab 2) which is the SINGLE SOURCE OF TRUTH.
        # This section displays a read-only summary for quick reference.

        load_summary_group = QGroupBox("Loading Summary (from MSD Builder)")
        load_summary_layout = QFormLayout(load_summary_group)
        load_summary_layout.setSpacing(4)

        # Read-only labels showing loading configuration
        self.summary_load_type = QLabel("Transverse (Junker)")
        self.summary_load_type.setStyleSheet(f"color: {Theme.BLUE}; font-weight: bold;")

        # Placeholders until a model is loaded \u2014 update_loading_summary() fills
        # these with real values once a model exists (avoid showing fake numbers).
        self.summary_preload = QLabel("\u2014")
        self.summary_excitation = QLabel("\u2014")
        self.summary_duration = QLabel("\u2014")
        self.summary_friction = QLabel("\u2014")
        self.summary_bolt = QLabel("\u2014 (load a model)")
        self.summary_miners = QLabel("\u2014")
        self.summary_miners.setToolTip(
            "Miner's cumulative damage D = \u03a3(n\u1d62/N\u1d62) — updated after analysis")

        load_summary_layout.addRow("Type:", self.summary_load_type)
        load_summary_layout.addRow("Preload:", self.summary_preload)
        load_summary_layout.addRow("Excitation:", self.summary_excitation)
        load_summary_layout.addRow("Duration:", self.summary_duration)
        load_summary_layout.addRow("Friction:", self.summary_friction)
        load_summary_layout.addRow("Bolt:", self.summary_bolt)
        load_summary_layout.addRow("Miner's D:", self.summary_miners)

        # Edit button to go to MSD Builder
        self.edit_loading_btn = QPushButton("✏️ Edit in MSD Builder")
        self.edit_loading_btn.setToolTip("Go to MSD Builder tab to edit loading parameters")
        load_summary_layout.addRow("", self.edit_loading_btn)

        left_layout.addWidget(load_summary_group)

        # Helper for creating help buttons (used in other sections)
        def create_help_btn(tooltip):
            btn = QPushButton("?")
            btn.setFixedSize(20, 20)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 9pt;
                    font-weight: bold;
                    border-radius: 10px;
                    background-color: {Theme.SURFACE1};
                    color: {Theme.SUBTEXT};
                    border: 1px solid {Theme.OVERLAY};
                }}
                QPushButton:hover {{
                    background-color: {Theme.BLUE};
                    color: {Theme.BASE};
                }}
            """)
            return btn

        # --- Time Integration ---
        time_group = QGroupBox("Time Integration")
        time_layout = QGridLayout(time_group)
        time_layout.setSpacing(6)

        self.method_combo = QComboBox()
        # Spec §3.A: expor só Newmark-β (default) + HHT-α; as demais classes de
        # integrador seguem em time_integration.py mas fora da UI.
        self.method_combo.addItems([
            "Newmark-β",
            "HHT-α",
        ])

        # Duration mode: finish by cycle count OR total time
        self.dur_cycles_radio = QRadioButton("Cycles")
        self.dur_time_radio = QRadioButton("Time")
        self.dur_cycles_radio.setChecked(True)
        _dur_btn_group = QButtonGroup(self)
        _dur_btn_group.addButton(self.dur_cycles_radio)
        _dur_btn_group.addButton(self.dur_time_radio)

        # Editable cycle count (primary in Cycles mode)
        self.sim_cycles_spin = QSpinBox()
        self.sim_cycles_spin.setRange(1, 10_000_000)
        self.sim_cycles_spin.setValue(2000)
        self.sim_cycles_spin.setSingleStep(100)
        self.sim_cycles_spin.setToolTip("Number of loading cycles to simulate")

        # Total simulation time (primary in Time mode, auto-computed in Cycles mode)
        self.t_end_spin = QDoubleSpinBox()
        self.t_end_spin.setRange(0.001, 1000000)
        self.t_end_spin.setValue(1.0)
        self.t_end_spin.setDecimals(3)
        self.t_end_spin.setSuffix(" s")
        self.t_end_spin.setEnabled(False)  # disabled in default Cycles mode

        self.dt_spin = QDoubleSpinBox()
        self.dt_spin.setRange(1e-6, 100.0)
        self.dt_spin.setValue(0.001)
        self.dt_spin.setDecimals(6)
        self.dt_spin.setSuffix(" s")

        self.suggest_dt_btn = QPushButton("Auto")
        self.suggest_dt_btn.setToolTip("Auto-calculate time step")
        self.suggest_dt_btn.setFixedWidth(60)

        self.help_method = create_help_btn(
            "Integration Method:\n"
            "• Newmark-β: Implicit, unconditionally stable, general purpose\n"
            "• HHT-α: Implicit with numerical damping, high-freq filtering\n"
            "• Central Diff: Explicit, conditionally stable, fast\n"
            "• Modal: Superposition (requires modal analysis first)\n"
            "• RK4: 4th-order Runge-Kutta, explicit, accurate"
        )
        self.help_cycles = create_help_btn(
            "Cycles mode:\n"
            "Enter the total number of loading cycles to simulate.\n"
            "Duration is auto-computed as:  t = N / frequency\n"
            "Example: 500 cycles @ 12.5 Hz → 40 s"
        )
        self.help_duration = create_help_btn(
            "Time mode:\n"
            "Enter the total simulation time directly.\n"
            "Cycle count is auto-computed as:  N = ⌊t × frequency⌋\n"
            "Example: 40 s @ 12.5 Hz → 500 cycles"
        )
        self.help_dt = create_help_btn(
            "Time Step (s):\n"
            "Integration step size. Affects accuracy & stability.\n"
            "• Too large: Instability, inaccurate results\n"
            "• Too small: Slow computation\n"
            "Rule: dt < T_min / 10 (T_min = smallest period)\n"
            "Click 'Auto' to calculate optimal step."
        )

        # Cycles row: ● Cycles  [sim_cycles_spin] [?]
        cycles_dur_row = QHBoxLayout()
        cycles_dur_row.setSpacing(4)
        cycles_dur_row.addWidget(self.dur_cycles_radio)
        cycles_dur_row.addWidget(self.sim_cycles_spin, stretch=1)
        cycles_dur_row.addWidget(self.help_cycles)

        # Time row: ○ Time  [t_end_spin] [?]
        time_dur_row = QHBoxLayout()
        time_dur_row.setSpacing(4)
        time_dur_row.addWidget(self.dur_time_radio)
        time_dur_row.addWidget(self.t_end_spin, stretch=1)
        time_dur_row.addWidget(self.help_duration)

        dt_row = QHBoxLayout()
        dt_row.setSpacing(4)
        dt_row.addWidget(self.dt_spin, stretch=1)
        dt_row.addWidget(self.suggest_dt_btn)
        dt_row.addWidget(self.help_dt)

        method_row = QHBoxLayout()
        method_row.addWidget(self.method_combo, stretch=1)
        method_row.addWidget(self.help_method)

        time_layout.addWidget(QLabel("Method:"), 0, 0)
        time_layout.addLayout(method_row, 0, 1)
        time_layout.addWidget(QLabel("Finish:"), 1, 0)
        time_layout.addLayout(cycles_dur_row, 1, 1)
        time_layout.addLayout(time_dur_row, 2, 1)
        time_layout.addWidget(QLabel("Step:"), 3, 0)
        time_layout.addLayout(dt_row, 3, 1)

        left_layout.addWidget(time_group)

        # --- Sampling (for large cycle counts) ---
        sample_group = QGroupBox("Output Sampling")
        sample_layout = QGridLayout(sample_group)
        sample_layout.setSpacing(6)

        self.sample_pct_spin = QDoubleSpinBox()
        self.sample_pct_spin.setRange(0.001, 100.0)
        self.sample_pct_spin.setValue(1.0)
        self.sample_pct_spin.setDecimals(3)
        self.sample_pct_spin.setSuffix(" %")

        self.target_points_spin = QSpinBox()
        self.target_points_spin.setRange(100, 1000000)
        self.target_points_spin.setValue(10000)
        self.target_points_spin.setSingleStep(1000)

        self.output_spin = QSpinBox()
        self.output_spin.setRange(1, 1000)
        self.output_spin.setValue(1)

        self.help_sample_pct = create_help_btn(
            "Sample Percentage (%):\n"
            "Fraction of cycles to store for output.\n"
            "• 100%: All cycles (memory intensive)\n"
            "• 1%: Every 100th cycle\n"
            "• 0.1%: Every 1000th cycle\n"
            "For 10,000 cycles @ 1% → 100 output points"
        )
        self.help_max_points = create_help_btn(
            "Maximum Output Points:\n"
            "Upper limit on stored data points.\n"
            "Prevents memory issues with large simulations.\n"
            "• 10,000: Standard (good for plotting)\n"
            "• 100,000: High detail\n"
            "• 1,000,000: Very high memory usage"
        )
        self.help_interval = create_help_btn(
            "Output Interval:\n"
            "Store results every N time steps.\n"
            "• 1: Every step (detailed but large)\n"
            "• 10: Every 10th step\n"
            "• 100: Sparse output"
        )

        sample_pct_row = QHBoxLayout()
        sample_pct_row.addWidget(self.sample_pct_spin, stretch=1)
        sample_pct_row.addWidget(self.help_sample_pct)

        max_points_row = QHBoxLayout()
        max_points_row.addWidget(self.target_points_spin, stretch=1)
        max_points_row.addWidget(self.help_max_points)

        interval_row = QHBoxLayout()
        interval_row.addWidget(self.output_spin, stretch=1)
        interval_row.addWidget(self.help_interval)

        sample_layout.addWidget(QLabel("Sample %:"), 0, 0)
        sample_layout.addLayout(sample_pct_row, 0, 1)
        sample_layout.addWidget(QLabel("Max Points:"), 1, 0)
        sample_layout.addLayout(max_points_row, 1, 1)
        sample_layout.addWidget(QLabel("Interval:"), 2, 0)
        sample_layout.addLayout(interval_row, 2, 1)

        left_layout.addWidget(sample_group)

        # --- Convergence (collapsible/advanced) ---
        conv_group = QGroupBox("Convergence (Advanced)")
        conv_layout = QGridLayout(conv_group)
        conv_layout.setSpacing(6)

        self.force_tol_spin = QDoubleSpinBox()
        self.force_tol_spin.setRange(1e-12, 1e-3)
        self.force_tol_spin.setValue(1e-6)
        self.force_tol_spin.setDecimals(10)

        self.disp_tol_spin = QDoubleSpinBox()
        self.disp_tol_spin.setRange(1e-12, 1e-3)
        self.disp_tol_spin.setValue(1e-8)
        self.disp_tol_spin.setDecimals(10)

        self.max_iter_spin = QSpinBox()
        self.max_iter_spin.setRange(1, 100)
        self.max_iter_spin.setValue(20)

        self.help_force_tol = create_help_btn(
            "Force Tolerance:\n"
            "Convergence criterion for force residual.\n"
            "Iteration stops when |F_residual| < tolerance.\n"
            "• 1e-6: Standard precision\n"
            "• 1e-8: High precision (slower)\n"
            "• 1e-4: Low precision (faster)"
        )
        self.help_disp_tol = create_help_btn(
            "Displacement Tolerance:\n"
            "Convergence criterion for displacement increment.\n"
            "Iteration stops when |Δx| < tolerance.\n"
            "• 1e-8: Standard precision\n"
            "• 1e-10: High precision (slower)"
        )
        self.help_max_iter = create_help_btn(
            "Maximum Iterations:\n"
            "Limit on Newton-Raphson iterations per step.\n"
            "If not converged within limit, step fails.\n"
            "• 10-20: Typical for well-posed problems\n"
            "• 50+: May indicate numerical issues"
        )

        force_tol_row = QHBoxLayout()
        force_tol_row.addWidget(self.force_tol_spin, stretch=1)
        force_tol_row.addWidget(self.help_force_tol)

        disp_tol_row = QHBoxLayout()
        disp_tol_row.addWidget(self.disp_tol_spin, stretch=1)
        disp_tol_row.addWidget(self.help_disp_tol)

        max_iter_row = QHBoxLayout()
        max_iter_row.addWidget(self.max_iter_spin, stretch=1)
        max_iter_row.addWidget(self.help_max_iter)

        conv_layout.addWidget(QLabel("Force Tol:"), 0, 0)
        conv_layout.addLayout(force_tol_row, 0, 1)
        conv_layout.addWidget(QLabel("Disp Tol:"), 1, 0)
        conv_layout.addLayout(disp_tol_row, 1, 1)
        conv_layout.addWidget(QLabel("Max Iter:"), 2, 0)
        conv_layout.addLayout(max_iter_row, 2, 1)

        left_layout.addWidget(conv_group)
        left_layout.addStretch()

        left_scroll.setWidget(left_widget)
        self.main_splitter.addWidget(left_scroll)

        # =====================================================================
        # RIGHT PANEL - Execution & Console
        # =====================================================================
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(8)

        # --- Loading Condition Advisor (§6.8) ---
        self.advisor_group = QGroupBox("Loading Condition Advisor")
        self.advisor_group.setCheckable(True)
        self.advisor_group.setChecked(True)
        advisor_layout = QVBoxLayout(self.advisor_group)
        advisor_layout.setContentsMargins(8, 4, 8, 4)
        self.advisor_label = QLabel("Configure loading to see advisor guidance.")
        self.advisor_label.setTextFormat(Qt.TextFormat.RichText)
        self.advisor_label.setWordWrap(True)
        self.advisor_label.setStyleSheet(f"color:{Theme.TEXT}; font-size:9pt;")
        advisor_layout.addWidget(self.advisor_label)
        self.advisor_group.toggled.connect(
            lambda checked: self.advisor_label.setVisible(checked)
        )
        right_layout.addWidget(self.advisor_group)

        # --- Execution Control ---
        exec_group = QGroupBox("Run Analysis")
        exec_layout = QVBoxLayout(exec_group)
        exec_layout.setSpacing(8)

        # Big Run button
        self.run_btn = QPushButton("Run Analysis")
        self.run_btn.setObjectName("success")
        self.run_btn.setMinimumHeight(Theme.BUTTON_MIN_HEIGHT_PRIMARY)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(28)

        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color: {Theme.SUBTEXT}; font-size: 10pt;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Pause/Stop buttons (smaller, horizontal)
        control_row = QHBoxLayout()
        control_row.setSpacing(8)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setEnabled(False)
        self.pause_btn.setMinimumHeight(36)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setObjectName("danger")
        self.stop_btn.setMinimumHeight(36)

        control_row.addWidget(self.pause_btn)
        control_row.addWidget(self.stop_btn)

        # §5.4 — "Run ISO 16130 Test" auto-configures per standard's amplitude table
        self.iso16130_btn = QPushButton("Run ISO 16130 Test")
        self.iso16130_btn.setMinimumHeight(36)
        self.iso16130_btn.setToolTip(
            "Auto-configure amplitude/frequency/cycles per ISO 16130:2015 "
            "for the current bolt size, then run the coupled loosening analysis."
        )
        control_row.addWidget(self.iso16130_btn)

        exec_layout.addWidget(self.run_btn)
        exec_layout.addWidget(self.progress_bar)

        # Stage pipeline indicators
        _STAGE_NAMES = ["Modal", "Static", "Preload", "Loosening", "Integration"]
        stage_row = QHBoxLayout()
        stage_row.setSpacing(4)
        self.stage_labels: list = []
        self._stage_pending_ss = (
            f"background:{Theme.SURFACE1}; color:{Theme.SUBTEXT}; "
            f"border-radius:4px; padding:2px 6px; font-size:8pt;"
        )
        self._stage_running_ss = (
            f"background:{Theme.BLUE}; color:{Theme.BASE}; "
            f"border-radius:4px; padding:2px 6px; font-size:8pt; font-weight:bold;"
        )
        self._stage_done_ss = (
            f"background:{Theme.GREEN}; color:{Theme.BASE}; "
            f"border-radius:4px; padding:2px 6px; font-size:8pt;"
        )
        self._stage_error_ss = (
            f"background:{Theme.RED}; color:{Theme.BASE}; "
            f"border-radius:4px; padding:2px 6px; font-size:8pt; font-weight:bold;"
        )
        for name in _STAGE_NAMES:
            lbl = QLabel(f"  {name}  ")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setMinimumWidth(72)
            lbl.setStyleSheet(self._stage_pending_ss)
            self.stage_labels.append(lbl)
            stage_row.addWidget(lbl)
        exec_layout.addLayout(stage_row)

        exec_layout.addWidget(self.status_label)
        exec_layout.addLayout(control_row)

        right_layout.addWidget(exec_group)

        # --- Live Status Dashboard (hidden until analysis runs) ---
        self.live_group = QGroupBox("Live Status")
        live_grid = QGridLayout(self.live_group)
        live_grid.setContentsMargins(6, 4, 6, 4)
        live_grid.setHorizontalSpacing(12)
        live_grid.setVerticalSpacing(2)
        _live_lbl_style = f"color:{Theme.SUBTEXT}; font-size:8pt;"
        _live_val_style = f"color:{Theme.TEXT}; font-size:9pt; font-weight:bold;"

        def _lv(text):
            l = QLabel(text)
            l.setStyleSheet(_live_lbl_style)
            return l

        def _vv(default="—"):
            l = QLabel(default)
            l.setStyleSheet(_live_val_style)
            return l

        self.live_cycle_lbl = _vv("—")
        self.live_preload_lbl = _vv("—")
        self.live_mu_thread_lbl = _vv("—")
        self.live_mu_bearing_lbl = _vv("—")
        self.live_loosening_lbl = _vv("—")
        self.live_margin_lbl = _vv("—")

        live_grid.addWidget(_lv("Cycle:"),       0, 0)
        live_grid.addWidget(self.live_cycle_lbl, 0, 1)
        live_grid.addWidget(_lv("Preload F/F₀:"),    0, 2)
        live_grid.addWidget(self.live_preload_lbl,   0, 3)
        live_grid.addWidget(_lv("μ thread:"),        1, 0)
        live_grid.addWidget(self.live_mu_thread_lbl, 1, 1)
        live_grid.addWidget(_lv("μ bearing:"),        1, 2)
        live_grid.addWidget(self.live_mu_bearing_lbl, 1, 3)
        live_grid.addWidget(_lv("Loosening:"),       2, 0)
        live_grid.addWidget(self.live_loosening_lbl, 2, 1)
        live_grid.addWidget(_lv("Torque margin:"),   2, 2)
        live_grid.addWidget(self.live_margin_lbl,    2, 3)

        self.live_group.setVisible(False)
        right_layout.addWidget(self.live_group)

        # --- Console Output ---
        console_group = QGroupBox("Output Log")
        console_layout = QVBoxLayout(console_group)
        console_layout.setContentsMargins(4, 4, 4, 4)

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet(f"""
            QTextEdit {{
                font-family: {Theme.FONT_MONO};
                font-size: 9pt;
                background-color: {Theme.CRUST};
                border: 1px solid {Theme.SURFACE1};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
        self.console_output.append("Bolt Analysis Studio v4.0")
        self.console_output.append("Ready to run analysis.")

        console_layout.addWidget(self.console_output)

        right_layout.addWidget(console_group, stretch=1)

        self.main_splitter.addWidget(right_widget)

        # Set initial splitter sizes (40% left, 60% right)
        self.main_splitter.setSizes([400, 600])

        main_layout.addWidget(self.main_splitter)

        # =====================================================================
        # HIDDEN COMPATIBILITY WIDGETS
        # These maintain compatibility with analysis code that reads loading params
        # They are updated from model.global_loading via update_loading_summary()
        # =====================================================================
        self.amplitude_spin = QDoubleSpinBox()
        self.amplitude_spin.setRange(0, 1e9)
        self.amplitude_spin.setValue(0)
        self.amplitude_spin.setVisible(False)

        self.trans_disp_spin = QDoubleSpinBox()
        self.trans_disp_spin.setRange(0, 10.0)
        self.trans_disp_spin.setValue(0.65)
        self.trans_disp_spin.setVisible(False)

        self.frequency_spin = QDoubleSpinBox()
        self.frequency_spin.setRange(0.001, 1000)
        self.frequency_spin.setValue(12.5)
        self.frequency_spin.setVisible(False)

        self.n_cycles_spin = QSpinBox()
        self.n_cycles_spin.setRange(1, 10000000)
        self.n_cycles_spin.setValue(2000)
        self.n_cycles_spin.setVisible(False)

        self.load_type_combo = QComboBox()
        self.load_type_combo.addItems([
            "Axial Cyclic",
            "Transverse (Junker)",
            "Combined",
            "Impulse/Step",
            "Custom"
        ])
        self.load_type_combo.setVisible(False)

        self.mu_initial_spin = QDoubleSpinBox()
        self.mu_initial_spin.setRange(0.01, 0.50)
        self.mu_initial_spin.setValue(0.12)
        self.mu_initial_spin.setVisible(False)

        self.lubricated_check = QCheckBox("Lubricated")
        self.lubricated_check.setChecked(True)
        self.lubricated_check.setVisible(False)

        self.bolt_diameter_spin = QDoubleSpinBox()
        self.bolt_diameter_spin.setRange(4, 100)
        self.bolt_diameter_spin.setValue(16.0)
        self.bolt_diameter_spin.setVisible(False)

        self.pitch_spin = QDoubleSpinBox()
        self.pitch_spin.setRange(0.5, 10)
        self.pitch_spin.setValue(2.0)
        self.pitch_spin.setVisible(False)

    def update_loading_summary(self, loading_data: dict):
        """
        Update the loading summary display from model.global_loading.

        Also updates the hidden compatibility spinboxes.

        Args:
            loading_data: Dictionary with loading configuration
        """
        # Update display labels
        load_type_display = {
            "axial": "Axial Cyclic",
            "transverse": "Transverse (Junker)",
            "combined": "Combined",
            "impulse": "Impulse/Step",
            "custom": "Custom"
        }
        load_type = loading_data.get("type", "transverse")
        self.summary_load_type.setText(load_type_display.get(load_type, load_type))

        preload = loading_data.get("F_preload", 0)
        self.summary_preload.setText(f"{preload:,.0f} N")

        trans_disp = loading_data.get("delta_amplitude", 0.65)
        freq = loading_data.get("frequency", 12.5)
        cycles = loading_data.get("n_cycles", 2000)
        load_type = loading_data.get("type", "transverse")

        # Excitation: show displacement amplitude only for transverse/combined loads
        if load_type in ("transverse", "combined"):
            self.summary_excitation.setText(f"{trans_disp:.3f} mm @ {freq:.1f} Hz")
        else:
            self.summary_excitation.setText(f"{freq:.1f} Hz")

        t_total = int(cycles) / freq if freq > 0 else 0.0
        self.summary_duration.setText(f"{int(cycles):,} cycles ({t_total:.1f} s)")

        mu = loading_data.get("mu_initial", 0.12)
        lubricated = loading_data.get("lubricated", True)
        lub_str = "lubricated" if lubricated else "dry"
        self.summary_friction.setText(f"\u03bc = {mu:.3f} \u00b7 {lub_str}")

        bolt_dia = loading_data.get("bolt_diameter", 16.0)
        pitch = loading_data.get("pitch", 2.0)
        stiff = compute_contact_stiffnesses(bolt_dia, pitch)
        self.summary_bolt.setText(
            f"M{bolt_dia:.0f} \u00d7 {pitch:.1f} \u00b7 k_b={stiff['k_bolt']:,.0f} N/mm"
        )

        # Update hidden compatibility spinboxes (HIGH-04: block signals to prevent
        # spurious _auto_calculate_timestep() calls during batch update)
        _hidden_widgets = [
            self.amplitude_spin, self.trans_disp_spin, self.frequency_spin,
            self.n_cycles_spin, self.mu_initial_spin, self.bolt_diameter_spin,
            self.pitch_spin, self.load_type_combo,
        ]
        for _w in _hidden_widgets:
            _w.blockSignals(True)
        self.lubricated_check.blockSignals(True)
        self.sim_cycles_spin.blockSignals(True)

        self.amplitude_spin.setValue(preload)
        self.trans_disp_spin.setValue(trans_disp)
        self.frequency_spin.setValue(freq)
        self.n_cycles_spin.setValue(int(cycles))
        self.sim_cycles_spin.setValue(int(cycles))
        self.mu_initial_spin.setValue(mu)
        self.lubricated_check.setChecked(lubricated)
        self.bolt_diameter_spin.setValue(bolt_dia)
        self.pitch_spin.setValue(pitch)

        # Update load type combo
        combo_index = {"axial": 0, "transverse": 1, "combined": 2, "impulse": 3, "custom": 4}
        self.load_type_combo.setCurrentIndex(combo_index.get(load_type, 1))

        for _w in _hidden_widgets:
            _w.blockSignals(False)
        self.lubricated_check.blockSignals(False)
        self.sim_cycles_spin.blockSignals(False)

        # §6.8 Loading Condition Advisor — refresh guidance panel
        try:
            from bolt_analysis_studio.analysis import advise_from_loading
            report = advise_from_loading(loading_data)
            if hasattr(self, 'advisor_label'):
                self.advisor_label.setText(report.to_rich_text())
        except Exception:
            pass

    def refresh_theme(self):
        """Re-apply inline stylesheets after theme change."""
        self.summary_load_type.setStyleSheet(f"color: {Theme.BLUE}; font-weight: bold;")
        if hasattr(self, 'case_info_label'):
            self.case_info_label.setStyleSheet(f"""
                QLabel {{
                    color: {Theme.SUBTEXT};
                    font-size: 9pt;
                    padding: 4px;
                    background-color: {Theme.SURFACE0};
                    border-radius: 4px;
                }}
            """)
        self.status_label.setStyleSheet(f"color: {Theme.SUBTEXT}; font-size: 10pt;")
        self.console_output.setStyleSheet(f"""
            QTextEdit {{
                font-family: {Theme.FONT_MONO};
                font-size: 9pt;
                background-color: {Theme.CRUST};
                border: 1px solid {Theme.SURFACE1};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
        # Rebuild stage stylesheet strings in case palette changed
        self._stage_pending_ss = (
            f"background:{Theme.SURFACE1}; color:{Theme.SUBTEXT}; "
            f"border-radius:4px; padding:2px 6px; font-size:8pt;"
        )
        self._stage_running_ss = (
            f"background:{Theme.BLUE}; color:{Theme.BASE}; "
            f"border-radius:4px; padding:2px 6px; font-size:8pt; font-weight:bold;"
        )
        self._stage_done_ss = (
            f"background:{Theme.GREEN}; color:{Theme.BASE}; "
            f"border-radius:4px; padding:2px 6px; font-size:8pt;"
        )
        self._stage_error_ss = (
            f"background:{Theme.RED}; color:{Theme.BASE}; "
            f"border-radius:4px; padding:2px 6px; font-size:8pt; font-weight:bold;"
        )
        # Re-apply to the existing stage labels (they kept the frozen palette).
        # Theme switches happen at idle, so reset all to 'pending'.
        for lbl in getattr(self, 'stage_labels', []):
            lbl.setStyleSheet(self._stage_pending_ss)

    def set_analysis_stage(self, stage_idx: int, error: bool = False) -> None:
        """Update stage pipeline indicators.

        stage_idx:  -1  → reset (all pending)
                    0-4 → that stage is running (all earlier = done)
                    5   → all done
        error:      True → current stage shows as red instead of blue
        """
        _STAGE_TEXTS = ["Modal", "Static", "Preload", "Loosening", "Integration"]
        _RUNNING_TEXTS = ["▶ Modal", "▶ Static", "▶ Preload", "▶ Loosening", "▶ Integration"]
        _DONE_TEXTS = ["✓ Modal", "✓ Static", "✓ Preload", "✓ Loosening", "✓ Integration"]
        _ERROR_TEXTS = ["✗ Modal", "✗ Static", "✗ Preload", "✗ Loosening", "✗ Integration"]

        for i, lbl in enumerate(self.stage_labels):
            lbl.setMinimumWidth(72)
            if stage_idx == -1:
                lbl.setText(f"  {_STAGE_TEXTS[i]}  ")
                lbl.setStyleSheet(self._stage_pending_ss)
            elif stage_idx >= 5:
                lbl.setText(f"  {_DONE_TEXTS[i]}  ")
                lbl.setStyleSheet(self._stage_done_ss)
            elif i < stage_idx:
                lbl.setText(f"  {_DONE_TEXTS[i]}  ")
                lbl.setStyleSheet(self._stage_done_ss)
            elif i == stage_idx:
                if error:
                    lbl.setText(f"  {_ERROR_TEXTS[i]}  ")
                    lbl.setStyleSheet(self._stage_error_ss)
                else:
                    lbl.setText(f"  {_RUNNING_TEXTS[i]}  ")
                    lbl.setStyleSheet(self._stage_running_ss)
            else:
                lbl.setText(f"  {_STAGE_TEXTS[i]}  ")
                lbl.setStyleSheet(self._stage_pending_ss)


class ResultsTab(QWidget):
    """Tab 4: Analysis results visualization with plot editor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_plot_type = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the results tab UI with plot editor toolbar."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Header with controls
        header_layout = QHBoxLayout()

        title = QLabel("📈 Analysis Results")
        title.setObjectName("heading")

        self.export_data_btn = QPushButton("📤 Export Data")
        self.dashboard_btn = QPushButton("📊 Dashboard")
        self.dashboard_btn.setObjectName("primary")
        self.dashboard_btn.setToolTip("Show all plots in a dashboard view")

        # Pin Results controls (3.1)
        self.pin_btn = QPushButton("📌 Pin Results")
        self.pin_btn.setToolTip(
            "Save a snapshot of the current results for comparison overlays (max 5 pins)"
        )
        self.clear_pins_btn = QPushButton("🗑 Clear Pins")
        self.clear_pins_btn.setToolTip("Remove all pinned result snapshots")
        self.pin_count_label = QLabel("Pins: 0/5")
        self.pin_count_label.setToolTip("Number of pinned result snapshots")

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.pin_count_label)
        header_layout.addWidget(self.pin_btn)
        header_layout.addWidget(self.clear_pins_btn)
        header_layout.addWidget(self.export_data_btn)
        header_layout.addWidget(self.dashboard_btn)

        layout.addLayout(header_layout)

        # Main content - splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side - Results tree
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        results_tree_label = QLabel("Select Plot:")
        results_tree_label.setObjectName("subheading")

        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderHidden(True)

        # Add result categories - comprehensive plot list
        categories = [
            ("📊 Time History", ["Displacement", "Velocity", "Acceleration", "Preload vs Time"]),
            ("📉 Preload Decay", ["Clamped Force Decay", "Preload Loss Models", "Stage Analysis", "Mechanism Decomposition"]),
            ("🔥 Friction & Wear", ["Friction Evolution", "Wear Accumulation", "Friction-Wear Correlation"]),
            ("🔩 Loosening", ["Loosening Rate", "Torque Balance", "Torque Margin", "Cumulative Angle"]),
            ("⚖️ Joint Forces", ["VDI Joint Diagram", "Joint Forces Diagram", "Contact Forces", "Phase Diagram"]),
            ("🎵 Modal Analysis", ["Mode Shapes", "Campbell Diagram"]),
        ]

        for cat_name, items in categories:
            cat_item = QTreeWidgetItem([cat_name])
            cat_item.setExpanded(True)
            for item in items:
                child = QTreeWidgetItem([item])
                cat_item.addChild(child)
            self.results_tree.addTopLevelItem(cat_item)

        self.results_tree.expandAll()

        left_layout.addWidget(results_tree_label)
        left_layout.addWidget(self.results_tree)

        # Right side - 3 sub-tabs: Summary / Model Analysis / Plot View
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.right_tabs = QTabWidget()

        # ── Tab 0: Summary Statistics ─────────────────────────────────────────
        summary_tab = QWidget()
        summary_tab_layout = QVBoxLayout(summary_tab)
        summary_tab_layout.setContentsMargins(8, 8, 8, 8)
        summary_tab_layout.setSpacing(8)

        stats_group = QGroupBox("Summary Statistics")
        stats_layout = QGridLayout(stats_group)
        stats_layout.setSpacing(8)

        stats_data = [
            ("Max Displacement:", "0.000 mm", Theme.BLUE),
            ("Max Velocity:", "0.000 m/s", Theme.BLUE),
            ("Final Preload:", "—", Theme.SUBTEXT),        # color set dynamically
            ("Preload Loss:", "—", Theme.SUBTEXT),         # color set dynamically
            ("Min Safety Factor:", "—", Theme.SUBTEXT),   # color set dynamically
            ("Loosening Phase:", "—", Theme.SUBTEXT),     # color set dynamically
            ("Fundamental Freq:", "0.00 Hz", Theme.MAUVE),
            ("Miner's Damage:", "—", Theme.SUBTEXT),      # Phase E — M15
            ("Fatigue Life:", "—", Theme.SUBTEXT),         # Phase E — cycles_to_failure_miner
            ("Self-Lock Margin:", "—", Theme.SUBTEXT),    # §6.7 — (µ·cos α − tan λ) / tan λ
        ]

        self.stats_labels = {}
        for i, (label, value, color) in enumerate(stats_data):
            row, col = divmod(i, 2)

            lbl = QLabel(label)
            lbl.setObjectName("summaryKey")

            val = QLabel(value)
            val.setObjectName("summaryValue")
            val.setStyleSheet(f"color: {color};")
            self.stats_labels[label.rstrip(':')] = val

            stats_layout.addWidget(lbl, row, col * 2)
            stats_layout.addWidget(val, row, col * 2 + 1)

        summary_tab_layout.addWidget(stats_group)
        summary_tab_layout.addStretch()
        self.right_tabs.addTab(summary_tab, "Summary")

        # ── Tab 1: Model Analysis ─────────────────────────────────────────────
        model_tab = QWidget()
        model_tab_layout = QVBoxLayout(model_tab)
        model_tab_layout.setContentsMargins(8, 8, 8, 8)
        model_tab_layout.setSpacing(6)

        modal_header = QLabel("🎵 Natural Frequencies & Damping")
        modal_header.setObjectName("subheading")
        model_tab_layout.addWidget(modal_header)

        self.modal_table = QTableWidget(0, 4)
        self.modal_table.setHorizontalHeaderLabels(
            ["Mode", "Freq (Hz)", "Period (s)", "Damping ζ"])
        self.modal_table.horizontalHeader().setStretchLastSection(True)
        self.modal_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.modal_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.modal_table.setStyleSheet(
            f"font-family: {Theme.FONT_MONO}; font-size: 9pt;")
        model_tab_layout.addWidget(self.modal_table, stretch=1)

        self.modal_placeholder = QLabel(
            "Run a Modal Analysis to see natural frequencies here.")
        self.modal_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.modal_placeholder.setObjectName("modalPlaceholder")
        model_tab_layout.addWidget(self.modal_placeholder)

        self.right_tabs.addTab(model_tab, "Modal Analysis")

        # ── Tab 2: Plot View ──────────────────────────────────────────────────
        plot_tab = QWidget()
        plot_tab_layout = QVBoxLayout(plot_tab)
        plot_tab_layout.setContentsMargins(4, 4, 4, 4)
        plot_tab_layout.setSpacing(6)

        # Toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(6)

        self.open_window_btn = QPushButton("Open in Editor")
        self.open_window_btn.setObjectName("primary")
        self.open_window_btn.setToolTip("Open plot in separate window with full editing options")
        self.open_window_btn.setMinimumHeight(Theme.BUTTON_MIN_HEIGHT_TOOLBAR)

        self.quick_export_btn = QPushButton("Export Plot")
        self.quick_export_btn.setToolTip("Export current plot — choose format (PNG/SVG/PDF) and DPI")
        self.quick_export_btn.setMinimumHeight(Theme.BUTTON_MIN_HEIGHT_TOOLBAR)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setToolTip("Refresh current plot")
        self.refresh_btn.setMinimumHeight(Theme.BUTTON_MIN_HEIGHT_TOOLBAR)

        self.current_plot_label = QLabel("No plot selected")
        self.current_plot_label.setStyleSheet(f"color: {Theme.SUBTEXT}; font-style: italic;")

        self.ref_load_btn = QPushButton("↑ Ref CSV")
        self.ref_load_btn.setToolTip(
            "Load an experimental reference curve (CSV: cycle, F_kN, F_over_F0) "
            "and overlay it on the Preload vs Time plot")
        self.ref_load_btn.setMinimumHeight(Theme.BUTTON_MIN_HEIGHT_TOOLBAR)

        self.ref_clear_btn = QPushButton("✕ Clear Ref")
        self.ref_clear_btn.setToolTip("Remove the reference overlay")
        self.ref_clear_btn.setMinimumHeight(Theme.BUTTON_MIN_HEIGHT_TOOLBAR)
        self.ref_clear_btn.setEnabled(False)

        self.auto_calibrate_btn = QPushButton("μ Auto-cal")
        self.auto_calibrate_btn.setToolTip(
            "Sweep μ ∈ [0.06, 0.25] and report the value that minimises MAE "
            "against the currently loaded reference curve")
        self.auto_calibrate_btn.setMinimumHeight(Theme.BUTTON_MIN_HEIGHT_TOOLBAR)
        self.auto_calibrate_btn.setEnabled(False)

        self.calibrate_btn = QPushButton("⚙  Calibrate Model…")
        self.calibrate_btn.setObjectName("primary")
        self.calibrate_btn.setToolTip(
            "Open full parameter-identification dialog\n"
            "  • Friction (μ_initial, μ_thread, μ_bearing)\n"
            "  • Stiffness/Damping (k_bolt, k_member, k_transverse_ratio, ζ)\n"
            "  • Two-Stage Jiang params (λ, η, C_loosen)\n"
            "  • Curve-shape (F∞ ratio, creep, friction recovery, noise)\n"
            "  • Save / Load Fixture Profile JSON\n\n"
            "Shortcut: Ctrl+K   (loads a reference CSV first if not already loaded)")
        self.calibrate_btn.setMinimumHeight(Theme.BUTTON_MIN_HEIGHT_TOOLBAR)
        self.calibrate_btn.setMinimumWidth(160)
        # Always enabled — dialog handles missing reference / preload with clear messages
        self.calibrate_btn.setEnabled(True)

        toolbar_layout.addWidget(self.open_window_btn)
        toolbar_layout.addWidget(self.quick_export_btn)
        toolbar_layout.addWidget(self.refresh_btn)
        toolbar_layout.addWidget(self.ref_load_btn)
        toolbar_layout.addWidget(self.ref_clear_btn)
        toolbar_layout.addWidget(self.auto_calibrate_btn)
        toolbar_layout.addWidget(self.calibrate_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.current_plot_label)

        plot_tab_layout.addLayout(toolbar_layout)

        # Stage Analysis overlay controls (hidden for all other plots)
        self.stage_overlay_widget = QWidget()
        _ov_row = QHBoxLayout(self.stage_overlay_widget)
        _ov_row.setContentsMargins(0, 0, 0, 0)
        _ov_row.setSpacing(8)
        _ov_lbl = QLabel("Secondary axis:")
        _ov_lbl.setStyleSheet(
            f"color: {Theme.SUBTEXT}; font-size: {Theme.FONT_SIZE_SMALL}pt;")
        _ov_row.addWidget(_ov_lbl)
        self.stage_overlay_combo = QComboBox()
        self.stage_overlay_combo.addItems([
            "None",
            "Loosening Rate  (deg/cycle)",
            "Torque Margin",
            "Friction Margin  (\u03bc / \u03bc_crit)",
            "Thread \u03bc",
            "Bearing \u03bc",
            "Cumulative Angle  (\u00b0)",
            "Wear Depth  (\u03bcm)",
        ])
        self.stage_overlay_combo.setMinimumWidth(220)
        self.stage_overlay_combo.setToolTip(
            "Choose a quantity to overlay on a secondary Y-axis")
        _ov_row.addWidget(self.stage_overlay_combo)
        self.stage_replay_btn = QPushButton("▶  Replay")
        self.stage_replay_btn.setToolTip("Replay the Stage Analysis animation from the beginning")
        self.stage_replay_btn.setMinimumHeight(Theme.BUTTON_MIN_HEIGHT_SMALL)
        _ov_row.addWidget(self.stage_replay_btn)
        self.stage_gif_btn = QPushButton("💾  Save GIF")
        self.stage_gif_btn.setToolTip("Save the Stage Analysis animation as an animated GIF")
        self.stage_gif_btn.setMinimumHeight(Theme.BUTTON_MIN_HEIGHT_SMALL)
        _ov_row.addWidget(self.stage_gif_btn)
        _ov_row.addStretch()
        self.stage_overlay_widget.setVisible(False)
        plot_tab_layout.addWidget(self.stage_overlay_widget)

        # Plot canvas
        self.plot_widget = PlotWidget(toolbar=True)
        self.plot_placeholder = QLabel(
            "Select a plot from the list on the left\nor click 'Dashboard' to view all plots")
        self.plot_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plot_placeholder.setObjectName("placeholder")

        self.plot_stack = QStackedWidget()
        self.plot_stack.addWidget(self.plot_placeholder)
        self.plot_stack.addWidget(self.plot_widget)
        self.plot_stack.setCurrentIndex(0)

        plot_tab_layout.addWidget(self.plot_stack, stretch=1)
        self.right_tabs.addTab(plot_tab, "Plot View")

        # ── Tab 3: Multi-Block Miner's Rule ───────────────────────────────────
        miners_tab = QWidget()
        miners_layout = QVBoxLayout(miners_tab)
        miners_layout.setContentsMargins(8, 8, 8, 8)
        miners_layout.setSpacing(6)

        # Preload input row
        preload_row = QHBoxLayout()
        preload_row.addWidget(QLabel("Bolt preload F₀ (N):"))
        self.miners_preload_spin = QDoubleSpinBox()
        self.miners_preload_spin.setRange(1, 5_000_000)
        self.miners_preload_spin.setValue(50_000)
        self.miners_preload_spin.setDecimals(0)
        self.miners_preload_spin.setSingleStep(1_000)
        self.miners_preload_spin.setToolTip(
            "Initial preload for Miner's rule fatigue life calculation")
        preload_row.addWidget(self.miners_preload_spin)
        preload_row.addStretch()
        miners_layout.addLayout(preload_row)

        # Load block table
        self.miners_table = QTableWidget(0, 3)
        self.miners_table.setHorizontalHeaderLabels(
            ["F_transverse (N)", "N Cycles", "Freq (Hz)"])
        self.miners_table.horizontalHeader().setStretchLastSection(True)
        self.miners_table.setMinimumHeight(100)
        self.miners_table.setMaximumHeight(180)
        miners_layout.addWidget(self.miners_table)

        # Table control buttons
        tbl_btn_row = QHBoxLayout()
        miners_add_btn = QPushButton("+ Add Block")
        miners_add_btn.setToolTip("Add a new load block row")
        miners_add_btn.clicked.connect(self._miners_add_row)
        miners_remove_btn = QPushButton("- Remove")
        miners_remove_btn.setToolTip("Remove selected row")
        miners_remove_btn.clicked.connect(self._miners_remove_row)
        miners_import_btn = QPushButton("\u2191 Import CSV")
        miners_import_btn.setToolTip(
            "Import load blocks from a CSV file.\n"
            "Format: F_transverse (N), N_cycles, Freq (Hz) — one block per row.\n"
            "Header row is skipped automatically if first column is non-numeric.")
        miners_import_btn.clicked.connect(self._miners_import_csv)
        miners_compute_btn = QPushButton("▶ Compute Damage")
        miners_compute_btn.setObjectName("success")
        miners_compute_btn.setToolTip(
            "Run Miner's rule D = Σ(nᵢ/Nᵢ) across all load blocks")
        miners_compute_btn.clicked.connect(self._miners_compute)
        tbl_btn_row.addWidget(miners_add_btn)
        tbl_btn_row.addWidget(miners_remove_btn)
        tbl_btn_row.addWidget(miners_import_btn)
        tbl_btn_row.addStretch()
        tbl_btn_row.addWidget(miners_compute_btn)
        miners_layout.addLayout(tbl_btn_row)

        # Result text label
        self.miners_result_lbl = QLabel("Add load blocks and click Compute.")
        self.miners_result_lbl.setStyleSheet(
            f"color: {Theme.BLUE}; font-family: {Theme.FONT_MONO}; font-size: 9pt;")
        self.miners_result_lbl.setWordWrap(True)
        miners_layout.addWidget(self.miners_result_lbl)

        # Embedded matplotlib bar chart
        try:
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
            from matplotlib.figure import Figure
            _fig = Figure(figsize=(4, 2), tight_layout=True)
            _fig.patch.set_facecolor(Theme.BASE)
            self.miners_fig = _fig
            self.miners_ax = _fig.add_subplot(111)
            self.miners_canvas_widget = FigureCanvasQTAgg(_fig)
            self.miners_canvas_widget.setMinimumHeight(120)
            from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
            miners_layout.addWidget(
                NavigationToolbar2QT(self.miners_canvas_widget, miners_tab))
            miners_layout.addWidget(self.miners_canvas_widget, stretch=1)
        except Exception:
            self.miners_fig = None
            self.miners_ax = None
            self.miners_canvas_widget = None

        self.right_tabs.addTab(miners_tab, "Miner's Rule")

        # ── Tab 4: Advanced Diagnostics (§2.4, §4.6, §6.7) ───────────────────
        adv_tab = QWidget()
        adv_layout = QVBoxLayout(adv_tab)
        adv_layout.setContentsMargins(4, 4, 4, 4)
        adv_layout.setSpacing(4)
        try:
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as _FC
            from matplotlib.figure import Figure as _Fig
            self.adv_fig = _Fig(figsize=(6, 8), tight_layout=True)
            self.adv_fig.patch.set_facecolor(Theme.BASE)
            # Three stacked axes: fretting map, SL margin, interaction diagram
            self.adv_axes = [
                self.adv_fig.add_subplot(3, 1, 1),
                self.adv_fig.add_subplot(3, 1, 2),
                self.adv_fig.add_subplot(3, 1, 3),
            ]
            for _ax in self.adv_axes:
                _ax.set_facecolor(Theme.SURFACE0)
            self.adv_canvas_widget = _FC(self.adv_fig)
            from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as _NT
            adv_layout.addWidget(_NT(self.adv_canvas_widget, adv_tab))
            adv_layout.addWidget(self.adv_canvas_widget, stretch=1)
        except Exception:
            self.adv_fig = None
            self.adv_axes = None
            self.adv_canvas_widget = None
            adv_layout.addWidget(QLabel("matplotlib unavailable"))
        self.right_tabs.addTab(adv_tab, "Diagnostics")

        right_layout.addWidget(self.right_tabs, stretch=1)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([200, 600])

        layout.addWidget(splitter, stretch=1)

        # Store color attribute names for refresh_theme
        self._stats_color_attrs = {
            "Max Displacement": "BLUE", "Max Velocity": "BLUE",
            "Final Preload": "GREEN", "Preload Loss": "YELLOW",
            "Min Safety Factor": "RED", "Fundamental Freq": "MAUVE",
        }

    def refresh_theme(self):
        """Re-apply inline stylesheets after theme change.

        Object-named widgets (placeholder, modalPlaceholder, summary labels)
        are re-styled automatically by the cached stylesheet when the parent
        window calls ``setStyleSheet(Theme.get_stylesheet())``. Only widgets
        whose colour changes at runtime need inline updates here.
        """
        # Stats labels — colour varies per row so the stylesheet can't carry it
        for key, val_label in self.stats_labels.items():
            color_attr = self._stats_color_attrs.get(key, "BLUE")
            color = getattr(Theme, color_attr, Theme.BLUE)
            val_label.setStyleSheet(Theme.summary_value_stylesheet(color))

        # Current plot label (italic variant — no stylesheet class yet)
        self.current_plot_label.setStyleSheet(
            f"color: {Theme.SUBTEXT}; font-style: italic;"
        )

    # ------------------------------------------------------------------
    # Multi-block Miner's Rule methods (Task 9)
    # ------------------------------------------------------------------

    def _miners_add_row(self):
        """Insert a new editable load block row into the Miner's table."""
        r = self.miners_table.rowCount()
        self.miners_table.insertRow(r)
        from PyQt6.QtWidgets import QTableWidgetItem
        self.miners_table.setItem(r, 0, QTableWidgetItem("5000"))
        self.miners_table.setItem(r, 1, QTableWidgetItem("500"))
        self.miners_table.setItem(r, 2, QTableWidgetItem("12.5"))

    def _miners_remove_row(self):
        """Remove the currently selected row from the Miner's table."""
        row = self.miners_table.currentRow()
        if row >= 0:
            self.miners_table.removeRow(row)

    def _miners_import_csv(self):
        """
        Import Miner's rule load blocks from a CSV file.

        Expected format (header row optional):
            F_transverse (N), N_cycles, Freq (Hz)

        Non-numeric first rows are treated as a header and skipped.
        Each subsequent row with at least 3 columns becomes a load block.
        """
        from PyQt6.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Miner's Load Blocks", "",
            "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)")
        if not path:
            return
        try:
            import csv
            rows_added = 0
            self.miners_table.setRowCount(0)
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for raw in reader:
                    if len(raw) < 3:
                        continue
                    # Skip header rows where the first column is non-numeric
                    try:
                        float(raw[0].strip())
                    except ValueError:
                        continue
                    r = self.miners_table.rowCount()
                    self.miners_table.insertRow(r)
                    self.miners_table.setItem(r, 0, QTableWidgetItem(raw[0].strip()))
                    self.miners_table.setItem(r, 1, QTableWidgetItem(raw[1].strip()))
                    self.miners_table.setItem(r, 2, QTableWidgetItem(raw[2].strip()))
                    rows_added += 1
            if self.miners_result_lbl:
                if rows_added > 0:
                    self.miners_result_lbl.setText(
                        f"Imported {rows_added} block(s). Click \u25b6 Compute Damage.")
                else:
                    self.miners_result_lbl.setText(
                        "No valid rows found in CSV. "
                        "Expected: F_trans (N), N_cycles, Freq (Hz).")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "CSV Import Error",
                                f"Could not read file:\n{e}")

    def _miners_compute(self):
        """
        Run Miner's rule D = Σ(nᵢ/Nᵢ) for all table rows.

        Uses SuNCurveModel to predict loosening life Nᵢ at each block's
        transverse force.  Results displayed as text + bar chart.
        """
        try:
            from bolt_analysis_studio.numerical.coupled_loosening_analyzer import (
                MinersRuleAccumulator, LoadBlock, SuNCurveModel, SuNCurveParams
            )
            import numpy as np

            F0 = self.miners_preload_spin.value()
            blocks = []
            for r in range(self.miners_table.rowCount()):
                try:
                    Ft = float(self.miners_table.item(r, 0).text())
                    nc = int(float(self.miners_table.item(r, 1).text()))
                    fq = float(self.miners_table.item(r, 2).text())
                    blocks.append(LoadBlock(F_transverse=Ft,
                                            n_cycles=max(1, nc),
                                            frequency=fq))
                except (ValueError, AttributeError):
                    continue

            if not blocks:
                self.miners_result_lbl.setText("No valid blocks — add rows first.")
                return

            acc = MinersRuleAccumulator(sun_curve=SuNCurveModel(SuNCurveParams()))
            result = acc.compute_variable_amplitude_damage(blocks, F0)

            total_D = result['total_damage']
            remaining = result['remaining_life_fraction'] * 100
            failed = result['failed']

            lines = [
                f"Total Miner's D = {total_D:.4f}",
                f"Remaining life:   {remaining:.1f} %",
                f"Fatigue failure:  {'YES — D ≥ 1' if failed else 'Not reached (D < 1)'}",
                f"Blocks: {result['n_blocks']}  |  Total cycles: {result['total_cycles']:,}",
            ]
            self.miners_result_lbl.setText("\n".join(lines))

            # Colour feedback
            color = Theme.RED if failed else (Theme.YELLOW if total_D >= 0.5 else Theme.GREEN)
            self.miners_result_lbl.setStyleSheet(
                f"color: {color}; font-family: {Theme.FONT_MONO}; font-size: 9pt;")

            # Bar chart
            if self.miners_ax is not None:
                ax = self.miners_ax
                ax.clear()
                details = result['block_details']
                labels = [f"B{i+1}" for i in range(len(details))]
                values = [d['damage_increment'] for d in details]
                cum = np.cumsum([0.0] + values)

                bar_colors = [Theme.RED if v >= 0.5 else Theme.GREEN for v in values]
                ax.bar(labels, values, color=bar_colors, edgecolor=Theme.SURFACE0)
                ax.axhline(y=1.0, color=Theme.RED, linestyle='--', linewidth=0.8,
                           alpha=0.6)
                ax.set_xlabel("Block", fontsize=7, color=Theme.TEXT)
                ax.set_ylabel("ΔD per block", fontsize=7, color=Theme.TEXT)
                ax.set_title(f"Miner's Damage per Block  (D_total={total_D:.3f})",
                             fontsize=8, color=Theme.TEXT)
                ax.tick_params(colors=Theme.TEXT, labelsize=7)
                ax.set_facecolor(Theme.BASE)
                self.miners_fig.patch.set_facecolor(Theme.BASE)
                for spine in ax.spines.values():
                    spine.set_edgecolor(Theme.SURFACE0)
                self.miners_canvas_widget.draw()

        except Exception as exc:
            self.miners_result_lbl.setText(f"Error: {exc}")

    def update_modal_results(self, natural_frequencies, damping_ratios=None):
        """
        Populate the modal results table and show the modal group (3.4).

        Args:
            natural_frequencies: list/array of natural frequencies [Hz]
            damping_ratios: optional list/array of damping ratios (ζ)
        """
        if not natural_frequencies:
            self.modal_table.setRowCount(0)
            self.modal_placeholder.setVisible(True)
            return

        self.modal_placeholder.setVisible(False)
        self.modal_table.setRowCount(0)
        for i, freq in enumerate(natural_frequencies):
            row = self.modal_table.rowCount()
            self.modal_table.insertRow(row)
            self.modal_table.setItem(row, 0, QTableWidgetItem(str(i + 1)))
            self.modal_table.setItem(
                row, 1, QTableWidgetItem(f"{freq:.4g}"))
            period = f"{1/freq:.4g}" if freq > 0 else "∞"
            self.modal_table.setItem(row, 2, QTableWidgetItem(period))
            if damping_ratios and i < len(damping_ratios):
                zeta = f"{damping_ratios[i]:.4f}"
            else:
                zeta = "—"
            self.modal_table.setItem(row, 3, QTableWidgetItem(zeta))

        self.modal_table.resizeColumnsToContents()
        # Switch to Model Analysis tab to show the results
        self.right_tabs.setCurrentIndex(1)


class SimilitudeTab(QWidget):
    """Tab 5: Similitude analysis and scaling with responsive layout."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the similitude tab UI with responsive splitter layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Main splitter for responsive left/right panels
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setHandleWidth(6)
        self.main_splitter.setChildrenCollapsible(False)

        # =====================================================================
        # LEFT PANEL - Scaling Configuration (in scroll area)
        # =====================================================================
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setMinimumWidth(250)
        left_scroll.setMaximumWidth(450)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(8)

        # Fallback stub: the enhanced similitude module failed to import, so no
        # real Π groups / comparison can be computed. Show a clear "unavailable"
        # banner and blank ("—") values instead of fabricated numbers.
        self._unavailable_banner = QLabel(
            "⚠ Módulo de similitude não carregado; instale/verifique o import. "
            "Os valores abaixo estão indisponíveis (—)."
        )
        self._unavailable_banner.setWordWrap(True)
        self._unavailable_banner.setStyleSheet(
            f"color: {Theme.PEACH}; font-size: 11px; "
            f"border: 1px solid {Theme.PEACH}; border-radius: 4px; padding: 4px;"
        )
        left_layout.addWidget(self._unavailable_banner)

        # Scale Factors
        scale_group = QGroupBox("Scale Factors")
        scale_layout = QGridLayout(scale_group)
        scale_layout.setSpacing(6)

        self.length_scale = QDoubleSpinBox()
        self.length_scale.setRange(0.01, 100)
        self.length_scale.setValue(1.0)
        self.length_scale.setDecimals(3)
        self.length_scale.setPrefix("λL = ")

        self.force_scale = QDoubleSpinBox()
        self.force_scale.setRange(0.01, 100)
        self.force_scale.setValue(1.0)
        self.force_scale.setDecimals(3)
        self.force_scale.setPrefix("λF = ")

        self.time_scale = QDoubleSpinBox()
        self.time_scale.setRange(0.01, 100)
        self.time_scale.setValue(1.0)
        self.time_scale.setDecimals(3)
        self.time_scale.setPrefix("λt = ")

        self.material_scale = QDoubleSpinBox()
        self.material_scale.setRange(0.01, 100)
        self.material_scale.setValue(1.0)
        self.material_scale.setDecimals(3)
        self.material_scale.setPrefix("λE = ")

        scale_layout.addWidget(QLabel("Length:"), 0, 0)
        scale_layout.addWidget(self.length_scale, 0, 1)
        scale_layout.addWidget(QLabel("Force:"), 1, 0)
        scale_layout.addWidget(self.force_scale, 1, 1)
        scale_layout.addWidget(QLabel("Time:"), 2, 0)
        scale_layout.addWidget(self.time_scale, 2, 1)
        scale_layout.addWidget(QLabel("Modulus:"), 3, 0)
        scale_layout.addWidget(self.material_scale, 3, 1)

        left_layout.addWidget(scale_group)

        # Scaling Analysis Type
        analysis_group = QGroupBox("Scaling Method")
        analysis_layout = QVBoxLayout(analysis_group)
        analysis_layout.setSpacing(6)

        self.scaling_type = QComboBox()
        self.scaling_type.addItems([
            "Froude (gravity)",
            "Reynolds (viscous)",
            "Cauchy (elastic)",
            "Strouhal (frequency)",
            "Custom"
        ])

        analysis_layout.addWidget(self.scaling_type)

        left_layout.addWidget(analysis_group)

        # Pi Groups
        pi_group = QGroupBox("Π Groups")
        pi_layout = QVBoxLayout(pi_group)
        pi_layout.setContentsMargins(4, 4, 4, 4)

        self.pi_table = QTableWidget()
        self.pi_table.setColumnCount(3)
        self.pi_table.setHorizontalHeaderLabels(["Π", "Formula", "Value"])
        self.pi_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pi_table.setMaximumHeight(180)

        # Values shown as "—": no computation is available in the fallback stub
        # (formulas kept as a reference; the numeric column is NOT fabricated).
        pi_data = [
            ("Π₁", "F/(E·L²)", "—"),
            ("Π₂", "k·L/E", "—"),
            ("Π₃", "ω√(m/k)", "—"),
            ("Π₄", "μ", "—"),
            ("Π₅", "ρL³/m", "—"),
        ]

        self.pi_table.setRowCount(len(pi_data))
        self.pi_table.setUpdatesEnabled(False)
        self.pi_table.blockSignals(True)
        try:
            for i, (group, formula, value) in enumerate(pi_data):
                self.pi_table.setItem(i, 0, QTableWidgetItem(group))
                self.pi_table.setItem(i, 1, QTableWidgetItem(formula))
                self.pi_table.setItem(i, 2, QTableWidgetItem(value))
        finally:
            self.pi_table.blockSignals(False)
            self.pi_table.setUpdatesEnabled(True)

        pi_layout.addWidget(self.pi_table)

        left_layout.addWidget(pi_group)
        left_layout.addStretch()

        left_scroll.setWidget(left_widget)
        self.main_splitter.addWidget(left_scroll)

        # =====================================================================
        # RIGHT PANEL - Comparison Table & Actions
        # =====================================================================
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(8)

        # Scaled Properties Comparison
        compare_group = QGroupBox("Prototype vs Model Comparison")
        compare_layout = QVBoxLayout(compare_group)
        compare_layout.setContentsMargins(4, 4, 4, 4)

        self.compare_table = QTableWidget()
        self.compare_table.setColumnCount(4)
        self.compare_table.setHorizontalHeaderLabels([
            "Property", "Prototype", "Model", "Scale"
        ])
        self.compare_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Values shown as "—": no computation is available in the fallback stub.
        compare_data = [
            ("Length", "—", "—", "—"),
            ("Force", "—", "—", "—"),
            ("Frequency", "—", "—", "—"),
            ("Stiffness", "—", "—", "—"),
            ("Mass", "—", "—", "—"),
            ("Preload", "—", "—", "—"),
            ("Displacement", "—", "—", "—"),
        ]

        self.compare_table.setRowCount(len(compare_data))
        self.compare_table.setUpdatesEnabled(False)
        self.compare_table.blockSignals(True)
        try:
            for i, row_data in enumerate(compare_data):
                for j, val in enumerate(row_data):
                    self.compare_table.setItem(i, j, QTableWidgetItem(val))
        finally:
            self.compare_table.blockSignals(False)
            self.compare_table.setUpdatesEnabled(True)

        compare_layout.addWidget(self.compare_table)

        # Actions (wrapped in flow layout for responsiveness)
        actions_group = QGroupBox("Actions")
        actions_layout = QGridLayout(actions_group)
        actions_layout.setSpacing(6)

        self.compute_btn = QPushButton("Compute")
        self.compute_btn.setObjectName("primary")
        self.compute_btn.setMinimumHeight(36)
        # BUG-05 fix: connect the compute button to a handler
        self.compute_btn.clicked.connect(self._compute_similitude)

        self.export_btn = QPushButton("Export")
        self.export_btn.setMinimumHeight(36)
        self.export_btn.setEnabled(False)  # nothing to export without compute

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setMinimumHeight(36)
        self.reset_btn.clicked.connect(self._reset_similitude)

        actions_layout.addWidget(self.compute_btn, 0, 0)
        actions_layout.addWidget(self.export_btn, 0, 1)
        actions_layout.addWidget(self.reset_btn, 0, 2)

        # Vertical splitter between comparison table and actions
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.setHandleWidth(5)
        right_splitter.setChildrenCollapsible(False)
        right_splitter.addWidget(compare_group)
        right_splitter.addWidget(actions_group)
        right_splitter.setSizes([400, 80])

        right_layout.addWidget(right_splitter, stretch=1)

        self.main_splitter.addWidget(right_widget)

        # Set initial splitter sizes (40% left, 60% right)
        self.main_splitter.setSizes([350, 550])

        main_layout.addWidget(self.main_splitter)

    def _compute_similitude(self):
        """BUG-05 fix: Fallback compute button handler — module not available."""
        QMessageBox.information(
            self, "Similitude Module Not Loaded",
            "The enhanced similitude module is not available.\n\n"
            "The similarity analysis requires the similitude package.\n"
            "Please check your installation and try again."
        )

    def _reset_similitude(self):
        """Reset fallback similitude tab spinboxes to defaults."""
        for spin in [self.length_scale, self.force_scale,
                     self.time_scale, self.material_scale]:
            spin.setValue(1.0)

    def refresh_theme(self):
        """Re-apply inline stylesheets after theme change."""
        # Table headers get theme colors via global stylesheet;
        # no widget-level inline styles to refresh here.
        pass


class ReportsTab(QWidget):
    """Tab 6: Report generation with responsive layout."""

    # Signals
    preview_requested = pyqtSignal()
    generate_requested = pyqtSignal()
    cmms_export_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the reports tab UI with responsive splitter layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Main splitter for responsive layout
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setHandleWidth(6)
        self.main_splitter.setChildrenCollapsible(False)

        # =====================================================================
        # LEFT PANEL - Report Configuration (in scroll area)
        # =====================================================================
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setMinimumWidth(220)
        left_scroll.setMaximumWidth(400)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(8)

        # Report Type
        type_group = QGroupBox("Report Type")
        type_layout = QVBoxLayout(type_group)

        self.report_type = QComboBox()
        self.report_type.addItems([
            "Full Analysis",
            "Summary",
            "Bolt Spec Sheet",
            "VDI 2230",
            "Loosening",
            "Similitude",
            "ISO 16130 / DIN 65151 Vibration Test",
        ])

        type_layout.addWidget(self.report_type)

        left_layout.addWidget(type_group)

        # Output Format
        format_group = QGroupBox("Output Format")
        format_layout = QVBoxLayout(format_group)

        self.format_buttons = QButtonGroup(self)

        formats = [
            ("PDF", True),
            ("HTML", False),
            ("CSV (Excel)", False),
            ("LaTeX (.tex)", False),
        ]

        for i, (fmt, default) in enumerate(formats):
            radio = QRadioButton(fmt)
            radio.setChecked(default)
            self.format_buttons.addButton(radio, i)
            format_layout.addWidget(radio)

        left_layout.addWidget(format_group)

        # Report Sections
        sections_group = QGroupBox("Sections")
        sections_layout = QVBoxLayout(sections_group)

        sections = [
            ("Project Info", True),
            ("Model", True),
            ("Materials", True),
            ("Loading", True),
            ("Results", True),
            ("Plots", True),
            ("Safety Factors", True),
            ("Loosening", False),
            ("Similitude", False),
        ]

        self.section_checks = {}
        for section, default in sections:
            cb = QCheckBox(section)
            cb.setChecked(default)
            self.section_checks[section] = cb
            sections_layout.addWidget(cb)

        left_layout.addWidget(sections_group)
        left_layout.addStretch()

        left_scroll.setWidget(left_widget)
        self.main_splitter.addWidget(left_scroll)

        # =====================================================================
        # RIGHT PANEL - Preview and Generation
        # =====================================================================
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(8)

        # Preview
        preview_group = QGroupBox("Report Preview")
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(4, 4, 4, 4)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.MANTLE};
                font-family: {Theme.FONT_SERIF};
                font-size: 10pt;
            }}
        """)
        self.preview_text.setHtml(self._get_default_preview())

        preview_layout.addWidget(self.preview_text)

        right_layout.addWidget(preview_group, stretch=1)

        # Generation controls
        gen_group = QGroupBox("Generate")
        gen_layout = QGridLayout(gen_group)
        gen_layout.setSpacing(6)

        self.preview_btn = QPushButton("Update Preview")
        self.preview_btn.setMinimumHeight(36)
        self.preview_btn.clicked.connect(self.preview_requested.emit)

        self.generate_btn = QPushButton("Generate Report")
        self.generate_btn.setObjectName("primary")
        self.generate_btn.setMinimumHeight(36)
        self.generate_btn.clicked.connect(self.generate_requested.emit)

        gen_layout.addWidget(self.preview_btn, 0, 0)
        gen_layout.addWidget(self.generate_btn, 0, 1)

        # §7.4 CMMS / maintenance export
        self.cmms_export_btn = QPushButton("Export CMMS CSV")
        self.cmms_export_btn.setMinimumHeight(36)
        self.cmms_export_btn.setToolTip(
            "Export predicted retorque interval (N at F/F₀ = 0.85) as CMMS-ready CSV "
            "for SAP PM / IBM Maximo import."
        )
        self.cmms_export_btn.clicked.connect(self.cmms_export_requested.emit)
        gen_layout.addWidget(self.cmms_export_btn, 1, 0, 1, 2)

        right_layout.addWidget(gen_group)

        self.main_splitter.addWidget(right_widget)

        # Set initial splitter sizes (35% left, 65% right)
        self.main_splitter.setSizes([300, 600])

        main_layout.addWidget(self.main_splitter)

    def _get_default_preview(self) -> str:
        """Get default preview HTML content."""
        return f"""
            <h2 style="color: {Theme.BLUE};">Bolt Analysis Report</h2>
            <hr style="border-color: {Theme.SURFACE1};">
            <p><b>Project:</b> Untitled Project</p>
            <p><b>Date:</b> --</p>
            <p><b>Standard:</b> VDI 2230 Part 1 (2015)</p>
            <hr style="border-color: {Theme.SURFACE1};">
            <p style="color: {Theme.SUBTEXT};"><i>Click "Update Preview" to generate report content based on current model and results.</i></p>
        """

    def get_selected_format(self) -> str:
        """Get the selected output format."""
        button = self.format_buttons.checkedButton()
        if button:
            text = button.text()
            if "PDF" in text:
                return "pdf"
            elif "HTML" in text:
                return "html"
            elif "CSV" in text:
                return "csv"
            elif "LaTeX" in text or ".tex" in text:
                return "latex"
        return "pdf"

    def get_selected_sections(self) -> list:
        """Get list of selected section names."""
        return [name for name, cb in self.section_checks.items() if cb.isChecked()]

    def get_report_type(self) -> str:
        """Get the selected report type."""
        return self.report_type.currentText()

    def set_preview_html(self, html: str):
        """Set the preview content."""
        self.preview_text.setHtml(html)

    def refresh_theme(self):
        """Re-apply inline stylesheets after theme change."""
        self.preview_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.MANTLE};
                font-family: {Theme.FONT_SERIF};
                font-size: 10pt;
            }}
        """)
        # Refresh the default preview HTML with new theme colors
        self.preview_text.setHtml(self._get_default_preview())


# =============================================================================
# COMMAND PALETTE (10.5)
# =============================================================================

class CommandPalette(QDialog):
    """
    Command palette (10.5): Ctrl+Shift+P opens a fuzzy-search popup over
    all QAction objects in the application menu bar.
    """

    def __init__(self, window: 'QMainWindow', parent=None):
        super().__init__(parent)
        self.setWindowTitle("Command Palette")
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setMinimumWidth(480)
        self._actions: list = []   # (display_text, QAction)
        self._collect_actions(window)
        self._build_ui()

    def _collect_actions(self, window):
        """Collect all QActions from the menu bar recursively."""
        def _walk(menu):
            for action in menu.actions():
                if action.isSeparator():
                    continue
                if action.menu():
                    _walk(action.menu())
                else:
                    text = action.text().replace('&', '')
                    if text:
                        self._actions.append((text, action))

        menubar = window.menuBar()
        for action in menubar.actions():
            if action.menu():
                _walk(action.menu())

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Type a command…")
        self._search.textChanged.connect(self._filter)
        layout.addWidget(self._search)

        self._list = QListWidget()
        self._list.setMaximumHeight(300)
        self._list.itemActivated.connect(self._execute)
        layout.addWidget(self._list)

        # Install event filter to handle Enter / Esc
        self._search.installEventFilter(self)
        self._filter("")

    def _filter(self, text: str):
        self._list.clear()
        query = text.lower()
        for label, action in self._actions:
            if not action.isEnabled():
                continue
            score = self._fuzzy_score(query, label.lower())
            if score >= 0:
                self._list.addItem(label)
        if self._list.count():
            self._list.setCurrentRow(0)

    @staticmethod
    def _fuzzy_score(query: str, target: str) -> int:
        """Returns ≥0 if all query chars appear in order in target, else -1."""
        if not query:
            return 0
        idx = 0
        for ch in query:
            pos = target.find(ch, idx)
            if pos == -1:
                return -1
            idx = pos + 1
        return 1

    def _execute(self, item):
        text = item.text()
        for label, action in self._actions:
            if label == text and action.isEnabled():
                self.accept()
                action.trigger()
                return
        self.accept()

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        from PyQt6.QtGui import QKeyEvent
        if obj is self._search and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                cur = self._list.currentItem()
                if cur:
                    self._execute(cur)
                return True
            elif key == Qt.Key.Key_Escape:
                self.reject()
                return True
            elif key == Qt.Key.Key_Down:
                row = self._list.currentRow()
                if row < self._list.count() - 1:
                    self._list.setCurrentRow(row + 1)
                return True
            elif key == Qt.Key.Key_Up:
                row = self._list.currentRow()
                if row > 0:
                    self._list.setCurrentRow(row - 1)
                return True
        return super().eventFilter(obj, event)


# =============================================================================
# MATERIAL DATABASE EDITOR (5.1)
# =============================================================================

class MaterialDatabaseDialog(QDialog):
    """
    Material database browser/editor dialog (5.1).

    Left panel: filterable list of all materials.
    Right panel: detailed property form for the selected material.
    Properties are editable for the session (changes are not persisted to disk).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Material Database")
        self.setMinimumSize(780, 520)
        self._materials = {}   # name → MaterialProperties
        self._current = None
        self._build_ui()
        self._load_db()

    def _build_ui(self):
        layout = QHBoxLayout(self)

        # Left: search + list
        left = QWidget()
        left.setMaximumWidth(260)
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search material…")
        self._search.textChanged.connect(self._filter)
        lv.addWidget(self._search)

        self._list = QListWidget()
        self._list.currentTextChanged.connect(self._on_select)
        lv.addWidget(self._list)

        layout.addWidget(left)

        # Right: property form
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_w = QWidget()
        self._form = QFormLayout(right_w)
        self._form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        right_scroll.setWidget(right_w)
        layout.addWidget(right_scroll, 1)

        # Property widgets
        def _dspin(lo=0, hi=1e6, dec=1, suffix=""):
            s = QDoubleSpinBox()
            s.setRange(lo, hi)
            s.setDecimals(dec)
            s.setSuffix(f" {suffix}" if suffix else "")
            s.setReadOnly(True)
            return s

        self._w_name = QLineEdit(); self._w_name.setReadOnly(True)
        self._w_grade = QLineEdit(); self._w_grade.setReadOnly(True)
        self._w_spec = QLineEdit(); self._w_spec.setReadOnly(True)
        self._w_cat = QLineEdit(); self._w_cat.setReadOnly(True)
        self._w_E   = _dspin(0, 1e6, 0, "MPa")
        self._w_Sy  = _dspin(0, 5000, 0, "MPa")
        self._w_Su  = _dspin(0, 5000, 0, "MPa")
        self._w_nu  = _dspin(0, 1, 3)
        self._w_rho = _dspin(0, 25000, 0, "kg/m³")
        self._w_alpha = _dspin(0, 100, 2, "×10⁻⁶ /°C")
        self._w_Tmax  = _dspin(-273, 2000, 0, "°C")
        self._w_zeta  = _dspin(0, 1, 4)
        self._w_sour  = QCheckBox("Sour service (NACE)"); self._w_sour.setEnabled(False)
        self._w_apps  = QTextEdit(); self._w_apps.setReadOnly(True); self._w_apps.setMaximumHeight(60)
        self._w_notes = QTextEdit(); self._w_notes.setReadOnly(True); self._w_notes.setMaximumHeight(60)

        for label, widget in [
            ("Name", self._w_name), ("Grade", self._w_grade),
            ("Specification", self._w_spec), ("Category", self._w_cat),
            ("E (Young's)", self._w_E), ("Sy (Yield)", self._w_Sy),
            ("Su (Ultimate)", self._w_Su), ("ν (Poisson)", self._w_nu),
            ("ρ (Density)", self._w_rho), ("α (Thermal)", self._w_alpha),
            ("T max", self._w_Tmax), ("ζ (Damping)", self._w_zeta),
            ("", self._w_sour), ("Applications", self._w_apps),
            ("Restrictions", self._w_notes),
        ]:
            self._form.addRow(label, widget)

        # Buttons
        btn_row = QHBoxLayout()
        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(self.reject)
        layout.setContentsMargins(8, 8, 8, 8)

        main_v = QVBoxLayout()
        main_v.addLayout(layout)
        main_v.addWidget(close_btn)
        # Replace main layout
        # We need to redo the layout properly
        container = QWidget()
        container.setLayout(QVBoxLayout())
        container.layout().addLayout(layout)
        container.layout().addWidget(close_btn)

        outer = QVBoxLayout(self)
        outer.addLayout(QHBoxLayout())  # dummy — we'll set layout directly

    def _build_ui(self):
        # Rebuild with proper outer layout
        outer = QVBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: search + list
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search material…")
        self._search.textChanged.connect(self._filter)
        lv.addWidget(self._search)
        self._list = QListWidget()
        self._list.currentTextChanged.connect(self._on_select)
        lv.addWidget(self._list)
        splitter.addWidget(left)
        splitter.setStretchFactor(0, 1)

        # Right: scroll form
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_w = QWidget()
        self._form = QFormLayout(right_w)
        self._form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        right_scroll.setWidget(right_w)
        splitter.addWidget(right_scroll)
        splitter.setStretchFactor(1, 3)
        splitter.setSizes([220, 560])

        outer.addWidget(splitter, 1)

        # Property widgets
        def _dspin(lo=0, hi=1e6, dec=1, suffix=""):
            s = QDoubleSpinBox()
            s.setRange(lo, hi)
            s.setDecimals(dec)
            s.setSuffix(f" {suffix}" if suffix else "")
            s.setReadOnly(True)
            return s

        self._w_name  = QLineEdit(); self._w_name.setReadOnly(True)
        self._w_grade = QLineEdit(); self._w_grade.setReadOnly(True)
        self._w_spec  = QLineEdit(); self._w_spec.setReadOnly(True)
        self._w_cat   = QLineEdit(); self._w_cat.setReadOnly(True)
        self._w_E     = _dspin(0, 1e6, 0, "MPa")
        self._w_Sy    = _dspin(0, 5000, 0, "MPa")
        self._w_Su    = _dspin(0, 5000, 0, "MPa")
        self._w_nu    = _dspin(0, 1, 3)
        self._w_rho   = _dspin(0, 25000, 0, "kg/m³")
        self._w_alpha = _dspin(0, 100, 3, "×10⁻⁶/°C")
        self._w_Tmax  = _dspin(-273, 2000, 0, "°C")
        self._w_zeta  = _dspin(0, 1, 4)
        self._w_sour  = QCheckBox("Compliant")
        self._w_sour.setEnabled(False)
        self._w_apps  = QTextEdit()
        self._w_apps.setReadOnly(True)
        self._w_apps.setMaximumHeight(55)
        self._w_notes = QTextEdit()
        self._w_notes.setReadOnly(True)
        self._w_notes.setMaximumHeight(55)

        for label, widget in [
            ("Name:", self._w_name), ("Grade:", self._w_grade),
            ("Specification:", self._w_spec), ("Category:", self._w_cat),
            ("E (Young's modulus):", self._w_E),
            ("Sy (Yield strength):", self._w_Sy),
            ("Su (Ultimate):", self._w_Su),
            ("ν (Poisson ratio):", self._w_nu),
            ("ρ (Density):", self._w_rho),
            ("α (Thermal exp.):", self._w_alpha),
            ("T max:", self._w_Tmax),
            ("ζ (Damping ratio):", self._w_zeta),
            ("Sour service (NACE):", self._w_sour),
            ("Applications:", self._w_apps),
            ("Restrictions:", self._w_notes),
        ]:
            self._form.addRow(label, widget)

        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(self.reject)
        outer.addWidget(close_btn)

    def _load_db(self):
        try:
            from bolt_analysis_studio.core.databases.materials_database import (
                MATERIALS_DATABASE,
            )
            self._materials = dict(MATERIALS_DATABASE)
        except Exception:
            self._materials = {}
        self._list.clear()
        for name in sorted(self._materials.keys()):
            self._list.addItem(name)
        if self._list.count():
            self._list.setCurrentRow(0)

    def _filter(self, text: str):
        txt = text.lower()
        self._list.clear()
        for name in sorted(self._materials.keys()):
            if txt in name.lower():
                self._list.addItem(name)
        if self._list.count():
            self._list.setCurrentRow(0)

    def _on_select(self, name: str):
        if not name or name not in self._materials:
            return
        m = self._materials[name]
        self._w_name.setText(m.name)
        self._w_grade.setText(m.grade)
        self._w_spec.setText(getattr(m, 'specification', ''))
        self._w_cat.setText(m.category.value if hasattr(m.category, 'value') else str(m.category))
        self._w_E.setValue(m.E)
        self._w_Sy.setValue(m.Sy)
        self._w_Su.setValue(m.Su)
        self._w_nu.setValue(m.nu)
        self._w_rho.setValue(m.rho)
        self._w_alpha.setValue(m.alpha * 1e6)
        self._w_Tmax.setValue(m.T_max)
        self._w_zeta.setValue(m.zeta)
        self._w_sour.setChecked(bool(m.sour_service))
        self._w_apps.setPlainText(getattr(m, 'applications', ''))
        self._w_notes.setPlainText(getattr(m, 'restrictions', ''))


# =============================================================================
# PREFERENCES DIALOG
# =============================================================================

class PreferencesDialog(QDialog):
    """
    Application-wide preferences dialog (10.1).

    Tabs:
    - General: auto-save interval, recent projects count, language
    - Solver: default method, default cycles, default timestep
    - Plots: DPI, default format, colour map
    - Reports: default format, author, institution
    """

    ORG = "BoltAnalysisStudio"
    APP = "BoltAnalysisStudio"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setMinimumWidth(420)
        self.setModal(True)

        self._settings = QSettings(self.ORG, self.APP)
        self._build_ui()
        self._load()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        # ── General ──────────────────────────────────────────────────────────
        general = QWidget()
        gf = QFormLayout(general)
        self._auto_save_spin = QSpinBox()
        self._auto_save_spin.setRange(1, 60)
        self._auto_save_spin.setSuffix(" min")
        gf.addRow("Auto-save interval:", self._auto_save_spin)

        self._recent_spin = QSpinBox()
        self._recent_spin.setRange(0, 20)
        gf.addRow("Max recent projects:", self._recent_spin)

        self._confirm_exit_check = QCheckBox("Confirm on exit")
        gf.addRow("", self._confirm_exit_check)

        tabs.addTab(general, "General")

        # ── Solver ────────────────────────────────────────────────────────────
        solver = QWidget()
        sf = QFormLayout(solver)

        self._method_combo = QComboBox()
        self._method_combo.addItems(["Newmark-β", "HHT-α"])  # spec §3.A
        sf.addRow("Default method:", self._method_combo)

        self._cycles_spin = QSpinBox()
        self._cycles_spin.setRange(100, 100000)
        self._cycles_spin.setSingleStep(500)
        sf.addRow("Default cycles:", self._cycles_spin)

        self._dt_spin = QDoubleSpinBox()
        self._dt_spin.setRange(1e-6, 1.0)
        self._dt_spin.setDecimals(6)
        self._dt_spin.setSingleStep(0.0001)
        sf.addRow("Default Δt (s):", self._dt_spin)

        tabs.addTab(solver, "Solver")

        # ── Plots ─────────────────────────────────────────────────────────────
        plots = QWidget()
        pf = QFormLayout(plots)

        self._dpi_combo = QComboBox()
        self._dpi_combo.addItems(["72", "96", "150", "300"])
        pf.addRow("Export DPI:", self._dpi_combo)

        self._fmt_combo = QComboBox()
        self._fmt_combo.addItems(["PNG", "SVG", "PDF"])
        pf.addRow("Default format:", self._fmt_combo)

        self._cmap_combo = QComboBox()
        self._cmap_combo.addItems(["viridis", "plasma", "coolwarm", "jet"])
        pf.addRow("Colour map:", self._cmap_combo)

        tabs.addTab(plots, "Plots")

        # ── Reports ───────────────────────────────────────────────────────────
        reports = QWidget()
        rf = QFormLayout(reports)

        self._report_fmt_combo = QComboBox()
        self._report_fmt_combo.addItems(["HTML", "PDF", "CSV"])
        rf.addRow("Default format:", self._report_fmt_combo)

        self._author_edit = QLineEdit()
        rf.addRow("Default author:", self._author_edit)

        self._institution_edit = QLineEdit()
        rf.addRow("Institution:", self._institution_edit)

        tabs.addTab(reports, "Reports")

        layout.addWidget(tabs)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(
            self._restore_defaults
        )
        layout.addWidget(buttons)

    def _load(self):
        s = self._settings
        self._auto_save_spin.setValue(int(s.value("prefs/auto_save_min", 5)))
        self._recent_spin.setValue(int(s.value("prefs/max_recent", 10)))
        self._confirm_exit_check.setChecked(
            s.value("prefs/confirm_exit", True, type=bool))
        method_idx = int(s.value("prefs/solver_method_idx", 0))
        self._method_combo.setCurrentIndex(
            min(method_idx, self._method_combo.count() - 1))
        self._cycles_spin.setValue(int(s.value("prefs/default_cycles", 2000)))
        self._dt_spin.setValue(float(s.value("prefs/default_dt", 0.001)))
        dpi = str(s.value("prefs/plot_dpi", "150"))
        idx = self._dpi_combo.findText(dpi)
        self._dpi_combo.setCurrentIndex(idx if idx >= 0 else 2)
        fmt = str(s.value("prefs/plot_fmt", "PNG"))
        self._fmt_combo.setCurrentIndex(max(0, self._fmt_combo.findText(fmt)))
        cmap = str(s.value("prefs/cmap", "viridis"))
        self._cmap_combo.setCurrentIndex(max(0, self._cmap_combo.findText(cmap)))
        rfmt = str(s.value("prefs/report_fmt", "HTML"))
        self._report_fmt_combo.setCurrentIndex(
            max(0, self._report_fmt_combo.findText(rfmt)))
        self._author_edit.setText(str(s.value("prefs/author", "")))
        self._institution_edit.setText(str(s.value("prefs/institution", "")))

    def _save(self):
        s = self._settings
        s.setValue("prefs/auto_save_min", self._auto_save_spin.value())
        s.setValue("prefs/max_recent", self._recent_spin.value())
        s.setValue("prefs/confirm_exit", self._confirm_exit_check.isChecked())
        s.setValue("prefs/solver_method_idx", self._method_combo.currentIndex())
        s.setValue("prefs/default_cycles", self._cycles_spin.value())
        s.setValue("prefs/default_dt", self._dt_spin.value())
        s.setValue("prefs/plot_dpi", self._dpi_combo.currentText())
        s.setValue("prefs/plot_fmt", self._fmt_combo.currentText())
        s.setValue("prefs/cmap", self._cmap_combo.currentText())
        s.setValue("prefs/report_fmt", self._report_fmt_combo.currentText())
        s.setValue("prefs/author", self._author_edit.text())
        s.setValue("prefs/institution", self._institution_edit.text())
        self.accept()

    def _restore_defaults(self):
        self._auto_save_spin.setValue(5)
        self._recent_spin.setValue(10)
        self._confirm_exit_check.setChecked(True)
        self._method_combo.setCurrentIndex(0)
        self._cycles_spin.setValue(2000)
        self._dt_spin.setValue(0.001)
        self._dpi_combo.setCurrentIndex(2)   # 150
        self._fmt_combo.setCurrentIndex(0)   # PNG
        self._cmap_combo.setCurrentIndex(0)  # viridis
        self._report_fmt_combo.setCurrentIndex(0)  # HTML
        self._author_edit.clear()
        self._institution_edit.setText("")

    @staticmethod
    def get(key: str, default=None):
        """Helper: read a preference value from anywhere in the app."""
        return QSettings(
            PreferencesDialog.ORG, PreferencesDialog.APP
        ).value(f"prefs/{key}", default)


# =============================================================================
# BATCH ANALYSIS DIALOG (2.3)
# =============================================================================

class _BatchWorker(QThread):
    """Background thread for parallel batch loosening analyses."""
    row_done = pyqtSignal(int, dict)   # row_index, result_dict
    all_done = pyqtSignal()

    def __init__(self, rows, base_config, parent=None):
        """
        rows: list of dicts with keys 'mu', 'force', 'cycles'
        base_config: CoupledLooseningConfig to clone for each row
        """
        super().__init__(parent)
        self._rows = rows
        self._base = base_config

    def run(self):
        import concurrent.futures, copy
        from bolt_analysis_studio.numerical.coupled_loosening_analyzer import (
            CoupledLooseningAnalyzer, FrictionEvolutionParams,
            WearModelParams, ThreadGeometryParams, BearingGeometryParams,
        )

        def _run_one(idx, row):
            cfg = self._base
            thread_geom = ThreadGeometryParams(
                pitch=cfg.pitch_mm * 1e-3,
                pitch_diameter=(cfg.bolt_diameter_mm - 0.6495 * cfg.pitch_mm) * 1e-3,
                major_diameter=cfg.bolt_diameter_mm * 1e-3,
            )
            bearing_geom = BearingGeometryParams(
                inner_diameter=cfg.bearing_inner_diameter_mm * 1e-3,
                outer_diameter=cfg.bearing_outer_diameter_mm * 1e-3,
            )
            mu = row.get("mu", cfg.mu_initial)
            friction = FrictionEvolutionParams(
                mu_initial=mu, mu_peak=mu * 1.1,
                mu_steady=mu * 0.9, mu_minimum=mu * 0.6,
            )
            wear = WearModelParams(K_archard=cfg.K_archard, hardness=cfg.hardness)
            analyzer = CoupledLooseningAnalyzer(
                thread_geometry=thread_geom, bearing_geometry=bearing_geom,
                friction_params=friction, wear_params=wear,
                k_bolt=cfg.k_bolt, k_member=cfg.k_member,
            )
            force = row.get("force", cfg.transverse_force)
            cycles = row.get("cycles", cfg.n_cycles)
            results = analyzer.run_analysis(
                preload_initial=cfg.initial_preload,
                F_transverse=force,
                n_cycles=cycles,
                output_interval=max(1, cycles // 200),
            )
            return {
                "mu": mu,
                "force": force,
                "cycles": cycles,
                "final_ratio": results.final_preload_ratio,
                "loosening_deg": results.total_loosening_deg,
            }

        max_workers = min(len(self._rows), os.cpu_count() or 2)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = {
                ex.submit(_run_one, i, row): i
                for i, row in enumerate(self._rows)
            }
            for future in concurrent.futures.as_completed(futures):
                i = futures[future]
                try:
                    res = future.result()
                except Exception as e:
                    res = {"error": str(e)}
                self.row_done.emit(i, res)

        self.all_done.emit()


class BatchAnalysisDialog(QDialog):
    """
    Parallel batch analysis dialog (2.3).

    Users define a grid of (μ, F_transverse, N_cycles) parameter sets.
    Each is run in a ThreadPoolExecutor; results fill the table live.
    """

    def __init__(self, base_config, parent=None):
        super().__init__(parent)
        self._base_config = base_config
        self._worker = None
        self.setWindowTitle("Batch Analysis")
        self.setMinimumSize(700, 420)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Parameter table
        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(
            ["μ initial", "F transverse (N)", "N cycles", "F/F₀ final", "Loosening (°)", "Status"])
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table)

        # Control buttons
        btn_row = QHBoxLayout()
        add_btn = QPushButton("+ Add Row")
        add_btn.clicked.connect(self._add_row)
        remove_btn = QPushButton("− Remove Row")
        remove_btn.clicked.connect(self._remove_row)
        self._run_btn = QPushButton("▶ Run Batch")
        self._run_btn.setObjectName("success")
        self._run_btn.clicked.connect(self._run_batch)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(remove_btn)
        btn_row.addStretch()
        btn_row.addWidget(self._run_btn)
        layout.addLayout(btn_row)

        self._status_lbl = QLabel("Add rows and click Run Batch.")
        layout.addWidget(self._status_lbl)

        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(self.reject)
        layout.addWidget(close_btn)

        # Pre-populate with 3 example rows
        for mu in [0.08, 0.12, 0.16]:
            self._add_row(mu=mu)

    def _add_row(self, mu=None):
        r = self._table.rowCount()
        self._table.insertRow(r)
        cfg = self._base_config
        mu_val = mu if mu is not None else cfg.mu_initial
        self._table.setItem(r, 0, QTableWidgetItem(f"{mu_val:.3f}"))
        self._table.setItem(r, 1, QTableWidgetItem(f"{cfg.transverse_force:.0f}"))
        self._table.setItem(r, 2, QTableWidgetItem(f"{cfg.n_cycles}"))
        for col in (3, 4):
            item = QTableWidgetItem("—")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(r, col, item)
        status_item = QTableWidgetItem("Pending")
        status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self._table.setItem(r, 5, status_item)

    def _remove_row(self):
        row = self._table.currentRow()
        if row >= 0:
            self._table.removeRow(row)

    def _collect_rows(self):
        rows = []
        for r in range(self._table.rowCount()):
            try:
                mu = float(self._table.item(r, 0).text())
                force = float(self._table.item(r, 1).text())
                cycles = int(self._table.item(r, 2).text())
                rows.append({"mu": mu, "force": force, "cycles": cycles})
            except Exception:
                rows.append({"mu": 0.12, "force": 10000, "cycles": 2000})
        return rows

    def _run_batch(self):
        if self._worker and self._worker.isRunning():
            return
        rows = self._collect_rows()
        if not rows:
            return
        # Reset results columns
        for r in range(self._table.rowCount()):
            self._table.item(r, 3).setText("—")
            self._table.item(r, 4).setText("—")
            self._table.item(r, 5).setText("Running…")
        self._run_btn.setEnabled(False)
        self._status_lbl.setText(f"Running {len(rows)} analyses in parallel…")
        self._worker = _BatchWorker(rows, self._base_config, self)
        self._worker.row_done.connect(self._on_row_done)
        self._worker.all_done.connect(self._on_all_done)
        self._worker.start()

    def _on_row_done(self, row_idx: int, res: dict):
        if "error" in res:
            self._table.item(row_idx, 5).setText(f"Error: {res['error'][:30]}")
        else:
            self._table.item(row_idx, 3).setText(f"{res['final_ratio'] * 100:.1f}%")
            self._table.item(row_idx, 4).setText(f"{res['loosening_deg']:.2f}°")
            self._table.item(row_idx, 5).setText("Done")

    def _on_all_done(self):
        self._run_btn.setEnabled(True)
        self._status_lbl.setText("Batch complete.")


# =============================================================================
# VALIDATION SUITE RUNNER (5.3)
# =============================================================================

class _ValidationWorker(QThread):
    """Runs all validation cases sequentially in background."""
    case_done = pyqtSignal(str, dict)   # case_name, validation_result_dict
    all_done = pyqtSignal()

    def run(self):
        from bolt_analysis_studio.core.validation_cases import ValidationCaseManager
        from bolt_analysis_studio.numerical.coupled_loosening_analyzer import (
            CoupledLooseningAnalyzer, FrictionEvolutionParams, WearModelParams,
            ThreadGeometryParams, BearingGeometryParams,
        )

        for case in ValidationCaseManager.get_all_cases():
            try:
                cfg = case.to_solver_config()
                pitch = case.pitch_mm
                d = case.bolt_diameter_mm

                thread_geom = ThreadGeometryParams(
                    pitch=pitch * 1e-3,
                    pitch_diameter=(d - 0.6495 * pitch) * 1e-3,
                    major_diameter=d * 1e-3,
                )
                bearing_geom = BearingGeometryParams(
                    inner_diameter=d * 1e-3,
                    outer_diameter=d * 1.5 * 1e-3,
                )
                mu = cfg["mu_initial"]
                friction = FrictionEvolutionParams(
                    mu_initial=mu, mu_peak=mu * 1.1,
                    mu_steady=mu * 0.9, mu_minimum=mu * 0.6,
                )
                wear = WearModelParams()
                analyzer = CoupledLooseningAnalyzer(
                    thread_geometry=thread_geom,
                    bearing_geometry=bearing_geom,
                    friction_params=friction,
                    wear_params=wear,
                )
                results = analyzer.run_analysis(
                    preload_initial=cfg["initial_preload"],
                    F_transverse=cfg["transverse_force"],
                    n_cycles=cfg["n_cycles"],
                    output_interval=max(1, cfg["n_cycles"] // 100),
                )
                vr = ValidationCaseManager.validate_result(
                    case,
                    results.final_preload_ratio,
                    results.total_loosening_deg,
                )
            except Exception as e:
                vr = {
                    "case_name": case.name,
                    "overall_pass": False,
                    "preload_error_pct": 999.0,
                    "loosening_error_pct": 999.0,
                    "note": str(e),
                }
            self.case_done.emit(case.name, vr)

        self.all_done.emit()


class ValidationSuiteDialog(QDialog):
    """
    Validation suite runner dialog (5.3).

    Runs all built-in validation cases and shows PASS/FAIL table.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Validation Suite Runner")
        self.setMinimumSize(720, 420)
        self._worker = None
        self._build_ui()
        self._populate_cases()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels([
            "Case", "Reference", "Expected F/F₀",
            "Simulated F/F₀", "Error %", "Result"
        ])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._table)

        btn_row = QHBoxLayout()
        self._run_btn = QPushButton("▶ Run Suite")
        self._run_btn.setObjectName("success")
        self._run_btn.clicked.connect(self._run_suite)
        self._load_btn = QPushButton("→ MSD Builder")
        self._load_btn.setToolTip(
            "Load selected validation case loading parameters into MSD Builder "
            "(Phase 1.4 — keeps MSD Builder in sync with validation cases)")
        self._load_btn.clicked.connect(self._load_into_builder)
        self._status_lbl = QLabel("Ready.")
        btn_row.addWidget(self._run_btn)
        btn_row.addWidget(self._load_btn)
        btn_row.addWidget(self._status_lbl)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(self.reject)
        layout.addWidget(close_btn)

    def _populate_cases(self):
        from bolt_analysis_studio.core.validation_cases import ValidationCaseManager
        for case in ValidationCaseManager.get_all_cases():
            r = self._table.rowCount()
            self._table.insertRow(r)
            self._table.setItem(r, 0, QTableWidgetItem(case.name))
            self._table.setItem(r, 1, QTableWidgetItem(case.source.value[:30]))
            self._table.setItem(r, 2, QTableWidgetItem(
                f"{case.expected_final_preload_ratio * 100:.1f}%"))
            self._table.setItem(r, 3, QTableWidgetItem("—"))
            self._table.setItem(r, 4, QTableWidgetItem("—"))
            status = QTableWidgetItem("Not run")
            self._table.setItem(r, 5, status)

    def _run_suite(self):
        if self._worker and self._worker.isRunning():
            return
        # Reset result columns
        for r in range(self._table.rowCount()):
            self._table.item(r, 3).setText("—")
            self._table.item(r, 4).setText("—")
            self._table.item(r, 5).setText("Running…")
        self._run_btn.setEnabled(False)
        self._status_lbl.setText("Running validation suite…")

        self._worker = _ValidationWorker(self)
        self._worker.case_done.connect(self._on_case_done)
        self._worker.all_done.connect(self._on_all_done)
        self._worker.start()

    def _on_case_done(self, case_name: str, vr: dict):
        from bolt_analysis_studio.core.validation_cases import ValidationCaseManager
        cases = {c.name: c for c in ValidationCaseManager.get_all_cases()}
        for r in range(self._table.rowCount()):
            if self._table.item(r, 0).text() == case_name:
                sim_ratio = vr.get("simulated_preload_ratio", None)
                if sim_ratio is None:
                    sim_ratio = cases[case_name].expected_final_preload_ratio * (
                        1 - vr.get("preload_error_pct", 0) / 100
                    ) if case_name in cases else 0.0
                self._table.item(r, 3).setText(
                    f"{vr.get('simulated_preload_ratio', sim_ratio) * 100:.1f}%"
                    if 'simulated_preload_ratio' in vr
                    else f"{vr.get('preload_error_pct', '?'):.1f}% err"
                )
                self._table.item(r, 4).setText(
                    f"{vr.get('preload_error_pct', 0):.1f}%")
                passed = vr.get("overall_pass", False)
                status_item = self._table.item(r, 5)
                if passed:
                    status_item.setText("PASS")
                    status_item.setForeground(
                        __import__('PyQt6.QtGui', fromlist=['QColor']).QColor(Theme.GREEN))
                else:
                    status_item.setText("FAIL")
                    status_item.setForeground(
                        __import__('PyQt6.QtGui', fromlist=['QColor']).QColor(Theme.RED))
                break

    def _on_all_done(self):
        self._run_btn.setEnabled(True)
        passes = sum(
            1 for r in range(self._table.rowCount())
            if self._table.item(r, 5).text() == "PASS"
        )
        total = self._table.rowCount()
        self._status_lbl.setText(f"Suite complete: {passes}/{total} passed.")

    def _load_into_builder(self):
        """
        Phase 1.4 — Push selected validation case loading params into MSD Builder.

        Maps ValidationCase fields → PropertyInspector.set_loading_data() format,
        then opens / raises the MSD Builder window so the user sees the change.
        """
        row = self._table.currentRow()
        if row < 0:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "No Selection",
                                    "Select a validation case row first.")
            return

        case_name = self._table.item(row, 0).text()
        from bolt_analysis_studio.core.validation_cases import ValidationCaseManager
        cases = {c.name: c for c in ValidationCaseManager.get_all_cases()}
        case = cases.get(case_name)
        if case is None:
            return

        # Build PropertyInspector-compatible loading dict
        k_trans_estimated = 300e6   # N/m (same estimate used in to_solver_config)
        trans_force = k_trans_estimated * (case.transverse_displacement_mm / 1000)
        loading_dict = {
            "type":                  "TRANSVERSE",
            "F_preload":             case.initial_preload_N,
            "preload_percent_yield": case.preload_percent_yield,
            "F_transverse":          trans_force,
            "delta_amplitude":       case.transverse_displacement_mm,   # mm
            "frequency":             case.frequency_Hz,
            "n_cycles":              case.n_cycles,
            "integration_time":      case.n_cycles / max(case.frequency_Hz, 1e-6),
            "duration_mode":         "cycles",
            "F_external":            0.0,
            "T_applied":             0.0,
            "delta_T":               0.0,
            "mu_initial":            case.mu_initial,
            "lubricated":            case.lubricated,
            "bolt_diameter":         case.bolt_diameter_mm,
            "pitch":                 case.pitch_mm,
        }

        # Open / raise MSD Builder and push the loading data
        main_win = self.parent()
        if main_win is None or not hasattr(main_win, '_open_msd_builder'):
            self._status_lbl.setText("Cannot reach main window.")
            return
        main_win._open_msd_builder()
        bw = getattr(main_win, 'msd_builder_window', None)
        if bw is None or not hasattr(bw, 'inspector'):
            self._status_lbl.setText("MSD Builder not available.")
            return

        # Populate the builder with a full element/contact model so the case
        # always has a visual representation, never an empty canvas:
        #   1. If the case ships a pre-built .msd, load it (matches the lab
        #      fixture topology exactly).
        #   2. Otherwise synthesise a transverse joint sized to the case
        #      (most literature cases ship reference data only, no .msd).
        # Done *before* pushing the loading dict so our loading values override
        # any baked into the model.
        import os as _os
        repo_root = _os.path.normpath(
            _os.path.join(_os.path.dirname(__file__), '..', '..', '..'))
        msd_rel = getattr(case, 'msd_model_path', '') or ''
        model_loaded = False
        if msd_rel:
            msd_abs = _os.path.normpath(_os.path.join(repo_root, msd_rel))
            if _os.path.isfile(msd_abs) and hasattr(bw, 'load_from_msd_model'):
                try:
                    import json as _json
                    from bolt_analysis_studio.core.models.model import MSDModel
                    with open(msd_abs, encoding='utf-8') as _f:
                        _data = _json.load(_f)
                    _model = MSDModel.from_dict(_data)
                    bw.load_from_msd_model(_model)
                    model_loaded = True
                except Exception as e:
                    self._status_lbl.setText(
                        f"MSD file load failed ({e}); synthesising from params.")
        if not model_loaded and hasattr(bw, '_build_model_from_case'):
            # Synthesise a populated, runnable model from the case geometry.
            try:
                _model = bw._build_model_from_case(case)
                bw.load_from_msd_model(_model)
                model_loaded = True
            except Exception as e:
                self._status_lbl.setText(
                    f"Loaded loading params only (model synth failed: {e}).")

        bw.inspector.set_loading_data(loading_dict)
        self._status_lbl.setText(f"Loaded '{case_name}' into MSD Builder.")
        # Task 14: Also update Solver Tab summary immediately so the
        # 6 loading-summary rows reflect the new validation case params.
        if hasattr(main_win, 'solver_tab'):
            main_win.solver_tab.update_loading_summary(loading_dict)

        # Auto-load the reference curve into the Results tab if the case
        # provides one, so the user can see lab vs. sim overlay immediately.
        ref_rel = getattr(case, 'reference_csv_path', '') or ''
        if ref_rel:
            ref_abs = _os.path.normpath(_os.path.join(repo_root, ref_rel))
            if _os.path.isfile(ref_abs) and hasattr(main_win, '_load_reference_csv'):
                main_win._load_reference_csv(ref_abs)


# =============================================================================
# CALIBRATION (parameter identification) — worker + dialog
# =============================================================================

class _CalibrationWorker(QThread):
    """QThread wrapper around ParameterIdentifier.run()."""
    progress = pyqtSignal(int, int, float)          # n_done, n_max, best_mae
    finished_ok = pyqtSignal(object)                # CalibrationResult
    failed = pyqtSignal(str)

    def __init__(self, identifier, n_starts: int = 3, parent=None):
        super().__init__(parent)
        self._identifier = identifier
        self._n_starts = int(n_starts)
        self._identifier.set_progress_callback(
            lambda d, m, b: self.progress.emit(int(d), int(m), float(b)))

    def cancel(self):
        self._identifier.cancel()

    def run(self):
        try:
            result = self._identifier.run(n_starts=self._n_starts)
        except Exception as e:
            self.failed.emit(str(e))
            return
        self.finished_ok.emit(result)


class _AgentWorker(QThread):
    """QThread wrapper around OptimizationAgent.run()."""
    progress = pyqtSignal(int, int, float, str)     # n_done, n_max, best, stage
    log_message = pyqtSignal(str)
    finished_ok = pyqtSignal(object)                # AgentReport
    failed = pyqtSignal(str)

    def __init__(self, agent, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._agent.set_progress_callback(
            lambda d, m, b, s: self.progress.emit(int(d), int(m), float(b), s))
        self._agent.set_log_callback(lambda msg: self.log_message.emit(msg))

    def cancel(self):
        self._agent.cancel()

    def run(self):
        try:
            report = self._agent.run()
        except Exception as e:
            self.failed.emit(str(e))
            return
        self.finished_ok.emit(report)


class CalibrationDialog(QDialog):
    """Parameter identification dialog.

    Lets the user pick which model parameters to fit, runs ParameterIdentifier
    in a background thread, shows a live preview of the best candidate against
    the reference, and (on Apply) writes the fitted values back to the model.
    """

    def __init__(self, parent, model, reference_curve, transverse_stiffness=None):
        super().__init__(parent)
        self.setWindowTitle("Calibrate MSD Parameters")
        self.setMinimumSize(760, 620)
        self._model = model
        self._reference = reference_curve
        self._trim_lo = None              # cycle-range crop for the reference
        self._trim_hi = None              # (None = full range; "remove a part")
        self._transverse_stiffness = transverse_stiffness
        self._worker = None
        self._staged = None               # CalibrationResult pending Apply/Discard
        self._param_rows = {}             # name → (checkbox, lo_spin, hi_spin)
        self._baseline_cycle = None       # populated by _preview_current()
        self._baseline_ratio = None
        self._element_param_keys = []     # populated when per-element rows added

        from bolt_analysis_studio.numerical.parameter_identifier import PRESET_PARAMS
        self._preset_factories = dict(PRESET_PARAMS)

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        # --- Two-column splitter layout -------------------------------------
        # Left  column: agent + params + optimiser + profile  (~440 px)
        # Right column: live preview (large) + progress + staged results
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setChildrenCollapsible(False)
        self._splitter.setHandleWidth(6)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_widget = QWidget()
        left_col = QVBoxLayout(left_widget)
        left_col.setContentsMargins(2, 2, 8, 2)
        left_col.setSpacing(8)
        left_scroll.setWidget(left_widget)
        left_scroll.setMinimumWidth(420)
        left_scroll.setMaximumWidth(560)

        right_widget = QWidget()
        right_col = QVBoxLayout(right_widget)
        right_col.setContentsMargins(8, 2, 2, 2)
        right_col.setSpacing(8)

        self._splitter.addWidget(left_scroll)
        self._splitter.addWidget(right_widget)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([460, 1100])

        # --- Parameter selection --------------------------------------------
        # Tooltips per param so the user knows what each one means + safe bounds.
        _PARAM_TOOLTIPS = {
            "mu_initial":           "Lumped initial friction coefficient (thread + bearing).",
            "mu_thread":            "Thread-surface initial friction (overrides mu_initial for thread).",
            "mu_bearing":           "Bearing-surface initial friction (overrides mu_initial for bearing).",
            "mu_peak_ratio":        "μ_peak / μ_initial — run-in friction overshoot (typ. 1.3–1.6).",
            "mu_steady_ratio":      "μ_steady / μ_initial — steady friction floor (typ. 0.6–0.9). Lower → faster Stage II decay.",
            "slip_onset_factor":    "Pai-Hess slip-onset multiplier on µ·N (default 0.46). 1.0 = classical Coulomb. Lower → earlier slip → more loosening.",
            "k_bolt":               "Axial bolt stiffness [N/m]. Default ≈ E·A_s/L_grip. Bound ±50%.",
            "k_member":             "Clamped-member axial stiffness [N/m]. ±50% of E·A_eff/L_grip.",
            "k_transverse_ratio":   "k_trans / k_axial (default 0.3). Calibrate against fixture transverse stiffness.",
            "damping_zeta":         "Rayleigh ζ — placeholder for time-integration; near-zero effect on quasi-static preload decay.",
            "C_loosening":          "Junker loosening coefficient (force-driven mode).",
            "N_stage1":             "Cycles for Stage I plastic embedding plateau.",
            "delta_F1_ratio":       "Max preload-loss ratio in Stage I (0.05–0.40 typical).",
            "N_stage2":             "Cycles for Stage II onset.",
            "k_stage2":             "Stage II decay rate (per cycle, log-spaced).",
            "transition_sharpness": "Knee sharpness between Stage I and Stage II.",
            "F_infinity_ratio":     "Asymptotic preload floor F∞/F₀. 1.0 disables damping.",
            "friction_recovery_gain": "μ↓→slip↑→wear↑ feedback amplifier (1.0 = baseline).",
            "creep_coefficient":    "Norton-Bailey ε₀ — log-time creep gain (off when ≈0).",
            "noise_amplitude":      "Gaussian σ on per-cycle d_θ (cosmetic; 0 = deterministic).",
            "k_emb_scale":          "V2 embedding multiplier (Stage I). ~1 = physical default.",
            "k_creep_scale":        "V2 creep multiplier (Norton-Bailey relaxation, tail).",
            "k_wear_scale_tr":      "V2 transverse wear multiplier (Archard, slip-driven). Dominant loss in disp-mode.",
            "k_loose_scale_tr":     "V2 transverse rotational-loosening multiplier (two-factor helix).",
            "Phi_tr_correction":    "V2 transverse Φ correction (load-factor anisotropy).",
            "slip_onset_W":         "V2 stage-1 incubation [J]: accumulated slip-work threshold that releases the slip-driven collapse (wear+loosening). 0 = no incubation (smooth decay). Non-zero → flat plateau then drop (3-stage Junker shape).",
            "k_wear_spec":          "V2 specific wear ratio K/H [1/Pa] — the IDENTIFIABLE wear parameter (merge §4.42a: K_archard/hardness only appear as this ratio). 0 = legacy pair; start 5e-14 = 1e-4/2e9.",
            "emb_depth":            "V2 embedding depth f_Z [m] — Stage-I settling asymptote (Estágio B: replaces k_emb_scale; ~30µm default, read from early-drop when a reference curve exists, §4.40).",
            "C_creep":              "V2 Norton creep coefficient (Estágio B: replaces k_creep_scale; anchored 1.87e-11, per tribo-pair §4.7).",
            "tr_loose_gain":        "V2 transverse loosening gain (Estágio B: absorbed Phi_tr_correction·k_loose_scale_tr; ~2.0; #1 provenance target §4.42).",
        }
        # Visual grouping headers that match the order in PRESET_PARAMS.
        _SECTIONS = [
            ("V2 physical constants + states (Estágio B — tuner layer removed)",
                ("emb_depth", "C_creep", "k_wear_spec", "tr_loose_gain",
                 "slip_onset_W")),
            ("Friction",          ("mu_initial", "mu_thread", "mu_bearing")),
            ("Friction evolution / Slip onset",
                ("mu_peak_ratio", "mu_steady_ratio", "slip_onset_factor")),
            ("Stiffness/Damping", ("k_bolt", "k_member", "k_transverse_ratio", "damping_zeta")),
            ("Two-Stage (Jiang/Yang)",
                ("C_loosening", "N_stage1", "delta_F1_ratio", "N_stage2",
                 "k_stage2", "transition_sharpness")),
            ("Curve Shape (Stage II)",
                ("F_infinity_ratio", "friction_recovery_gain",
                 "creep_coefficient", "noise_amplitude")),
        ]

        params_group = QGroupBox("Parameters to fit")
        pg_outer = QVBoxLayout(params_group)
        pg_outer.setContentsMargins(4, 4, 4, 4)

        # Calibration engine — V2 (non-linear) is the default; V1 is the
        # legacy two-stage piecewise model (the "two straight lines").
        self.engine_combo = QComboBox()
        self.engine_combo.addItems([
            "V2 non-linear (DynamicStiffnessAnalyzer) — recommended",
            "V1 two-stage (Jiang, legacy)",
        ])
        self._engine_keys = ["v2", "v1"]
        self.engine_combo.setToolTip(
            "V2 = full non-linear energy model (surface softening + helix "
            "loosening + wear + creep). V1 = legacy piecewise two-stage curve.")
        eng_row = QHBoxLayout()
        eng_row.addWidget(QLabel("Engine:"))
        eng_row.addWidget(self.engine_combo, stretch=1)
        pg_outer.addLayout(eng_row)

        # Literature-prior wizard launcher — pre-populates defaults & bounds
        # from a curated list of reference papers.
        wiz_row = QHBoxLayout()
        self.wizard_btn = QPushButton("📚  Wizard — load literature priors…")
        self.wizard_btn.setToolTip(
            "Open a 3-step wizard:\n"
            "  1. Pick loading regime (transverse / axial / combined / CFRP / gasketed)\n"
            "  2. Pick reference paper (Lu 2024, Jiang 2003, Liu 2017, …)\n"
            "  3. Apply suggested defaults + ±σ bounds to this dialog\n\n"
            "Useful for getting a sane starting point before running the optimiser.")
        self.wizard_btn.clicked.connect(self._open_prior_wizard)
        wiz_row.addWidget(self.wizard_btn)
        wiz_row.addStretch()
        pg_outer.addLayout(wiz_row)

        # Scrollable inner widget — 17 rows would otherwise blow up dialog height.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMinimumHeight(220)
        scroll_inner = QWidget()
        pg_layout = QGridLayout(scroll_inner)
        pg_layout.setSpacing(3)
        pg_layout.addWidget(QLabel("<b>Parameter</b>"), 0, 0)
        pg_layout.addWidget(QLabel("<b>Lo</b>"), 0, 1)
        pg_layout.addWidget(QLabel("<b>Hi</b>"), 0, 2)

        row = 1
        for section_title, names in _SECTIONS:
            header = QLabel(f"<i><b>— {section_title} —</b></i>")
            header.setStyleSheet("color: #555; padding-top: 4px;")
            pg_layout.addWidget(header, row, 0, 1, 3)
            row += 1
            for name in names:
                if name not in self._preset_factories:
                    continue
                factory = self._preset_factories[name]
                default_p = factory()
                cb = QCheckBox(name)
                cb.setToolTip(_PARAM_TOOLTIPS.get(name, ""))
                # Parsimony default: pre-check ONLY the minimal identifiable V2
                # tuners {embedding, wear} — the set the data justifies (see
                # MODEL_LEGITIMACY.md §4.4). The other tuners (creep/loose/Phi_tr)
                # are available but unchecked (adding them is usually overfitting).
                if name in ("k_emb_scale", "k_wear_scale_tr"):
                    cb.setChecked(True)
                lo_spin = QDoubleSpinBox()
                lo_spin.setDecimals(9 if default_p.log_scale else 6)
                lo_spin.setRange(1e-12, 1e12)
                lo_spin.setValue(float(default_p.lo))
                lo_spin.setToolTip(f"Lower bound (default {default_p.lo:g})")
                hi_spin = QDoubleSpinBox()
                hi_spin.setDecimals(9 if default_p.log_scale else 6)
                hi_spin.setRange(1e-12, 1e12)
                hi_spin.setValue(float(default_p.hi))
                hi_spin.setToolTip(f"Upper bound (default {default_p.hi:g})")
                pg_layout.addWidget(cb, row, 0)
                pg_layout.addWidget(lo_spin, row, 1)
                pg_layout.addWidget(hi_spin, row, 2)
                self._param_rows[name] = (cb, lo_spin, hi_spin)
                row += 1

        # Per-element MSD parameter rows (k / c / m of every element with non-zero
        # MSD values). Lets the user nudge specific schematic elements rather
        # than the lumped k_bolt / k_member.
        self._element_param_keys = []   # ordered list of element-row keys
        elements = list(getattr(self._model, "elements", []) or [])
        elements_with_msd = [
            e for e in elements
            if hasattr(e, "msd")
            and any(getattr(e.msd, k, 0.0) > 0 for k in ("k", "c", "m"))
        ]
        if elements_with_msd:
            header = QLabel("<i><b>— Per-Element MSD —</b></i>")
            header.setStyleSheet("color: #555; padding-top: 6px;")
            pg_layout.addWidget(header, row, 0, 1, 3)
            row += 1
            for el in elements_with_msd:
                el_type = getattr(getattr(el, "type", None), "value",
                                  str(getattr(el, "type", "?")))
                el_name = getattr(el, "name", "") or el_type
                el_id = int(getattr(el, "id", 0))
                for kind, unit in (("k", "N/m"), ("c", "N·s/m"), ("m", "kg")):
                    cur = float(getattr(el.msd, kind, 0.0) or 0.0)
                    if cur <= 0:
                        continue
                    key = f"elem{el_id}.{kind}"
                    cb = QCheckBox(f"#{el_id} {el_name[:14]} · {kind}")
                    cb.setToolTip(
                        f"Calibrate {kind} of element #{el_id} ({el_name}, {el_type}). "
                        f"Current: {cur:.3g} {unit}.  Default bounds: ±50 % of current.")
                    lo_spin = QDoubleSpinBox()
                    lo_spin.setDecimals(9)
                    lo_spin.setRange(1e-12, 1e12)
                    lo_spin.setValue(cur * 0.5)
                    lo_spin.setToolTip(f"Lower bound (default {cur*0.5:g} {unit})")
                    hi_spin = QDoubleSpinBox()
                    hi_spin.setDecimals(9)
                    hi_spin.setRange(1e-12, 1e12)
                    hi_spin.setValue(cur * 2.0)
                    hi_spin.setToolTip(f"Upper bound (default {cur*2.0:g} {unit})")
                    pg_layout.addWidget(cb, row, 0)
                    pg_layout.addWidget(lo_spin, row, 1)
                    pg_layout.addWidget(hi_spin, row, 2)
                    self._param_rows[key] = (cb, lo_spin, hi_spin)
                    self._element_param_keys.append(
                        (key, el_id, kind, cur, el_name))
                    row += 1

        scroll.setWidget(scroll_inner)
        pg_outer.addWidget(scroll)

        # Fixture-profile I/O — prominent strip (reusable across experiments)
        fp_label = QLabel(
            "<b>Reusable Calibration Profile</b> — "
            "save the chosen params, bounds, optimiser settings and last-fitted "
            "values to a JSON file, then load it onto any other MSD model.")
        fp_label.setWordWrap(True)
        fp_label.setStyleSheet(
            f"color: {Theme.SUBTEXT}; padding: 4px 0; "
            f"border-top: 1px solid {Theme.OVERLAY};")
        pg_outer.addWidget(fp_label)

        fp_row = QHBoxLayout()
        self.save_profile_btn = QPushButton("💾  Save Calibration to JSON…")
        self.save_profile_btn.setObjectName("primary")
        self.save_profile_btn.setMinimumHeight(30)
        self.save_profile_btn.setToolTip(
            "Export the full calibration setup to a JSON file:\n"
            "  • Selected parameters + bounds\n"
            "  • Optimiser settings (objective, max_evals, restarts)\n"
            "  • Last fitted values (fixture k/c/μ + two-stage overrides)\n\n"
            "Reload this file on any other model to reuse the same setup.")
        self.save_profile_btn.clicked.connect(self._save_fixture_profile)

        self.load_profile_btn = QPushButton("↑  Load Calibration from JSON…")
        self.load_profile_btn.setMinimumHeight(30)
        self.load_profile_btn.setToolTip(
            "Import a saved calibration JSON — restores parameter selection, "
            "bounds, optimiser settings, and (optionally) applies the stored "
            "fitted values directly to the current model.")
        self.load_profile_btn.clicked.connect(self._load_fixture_profile)

        fp_row.addWidget(self.save_profile_btn)
        fp_row.addWidget(self.load_profile_btn)
        fp_row.addStretch()
        pg_outer.addLayout(fp_row)

        # --- Autonomous Optimization Agent panel ----------------------------
        agent_group = QGroupBox("🤖  Optimization Agent (autonomous)")
        ag_layout = QVBoxLayout(agent_group)
        ag_layout.setContentsMargins(6, 6, 6, 6)
        ag_label = QLabel(
            "Detects the loading regime, picks a literature prior, then runs "
            "<b>coarse → fine</b> calibration automatically. No manual "
            "parameter selection required.")
        ag_label.setWordWrap(True)
        ag_label.setStyleSheet(f"color: {Theme.SUBTEXT};")
        ag_layout.addWidget(ag_label)

        ag_row = QHBoxLayout()
        ag_row.addWidget(QLabel("Total budget:"))
        self.agent_budget_spin = QSpinBox()
        self.agent_budget_spin.setRange(80, 100000)
        self.agent_budget_spin.setSingleStep(40)
        self.agent_budget_spin.setValue(240)
        self.agent_budget_spin.setSuffix(" evals")
        self.agent_budget_spin.setToolTip(
            "Total simulation budget split across all stages "
            "(30% coarse / 55% fine / 15% creep when applicable).")
        ag_row.addWidget(self.agent_budget_spin)
        ag_row.addStretch()
        self.agent_run_btn = QPushButton("🤖  Run Agent")
        self.agent_run_btn.setObjectName("primary")
        self.agent_run_btn.setToolTip(
            "Run the autonomous calibration agent (multi-stage):\n"
            "  • Stage 1 — coarse scalars\n"
            "  • Stage 2 — fine refinement\n"
            "  • Stage 3 — creep (only if regime calls for it)")
        self.agent_run_btn.clicked.connect(self._run_optimization_agent)
        ag_row.addWidget(self.agent_run_btn)
        ag_layout.addLayout(ag_row)

        # Curve-trim row: "remove a part" of the imported reference (head/tail)
        # so calibration + the error metric (MAE/RMSE) use only the kept cycles.
        import numpy as _np_trim
        _cyc0 = (_np_trim.asarray(self._reference['cycle'], dtype=float)
                 if self._reference is not None else _np_trim.array([0.0, 1.0]))
        _cmin, _cmax = float(_cyc0.min()), float(_cyc0.max())
        trim_row = QHBoxLayout()
        trim_row.addWidget(QLabel("Trim cycles:"))
        self._trim_lo_spin = QDoubleSpinBox()
        self._trim_lo_spin.setRange(_cmin, _cmax)
        self._trim_lo_spin.setDecimals(0)
        self._trim_lo_spin.setValue(_cmin)
        self._trim_lo_spin.setToolTip(
            "Lowest cycle kept for fitting — remove the curve's head "
            "(e.g. pre-load settling).")
        trim_row.addWidget(self._trim_lo_spin)
        trim_row.addWidget(QLabel("to"))
        self._trim_hi_spin = QDoubleSpinBox()
        self._trim_hi_spin.setRange(_cmin, _cmax)
        self._trim_hi_spin.setDecimals(0)
        self._trim_hi_spin.setValue(_cmax)
        self._trim_hi_spin.setToolTip(
            "Highest cycle kept for fitting — remove the curve's tail "
            "(e.g. noisy saturation or a re-tightening spike).")
        trim_row.addWidget(self._trim_hi_spin)
        self._trim_lo_spin.editingFinished.connect(self._on_trim_changed)
        self._trim_hi_spin.editingFinished.connect(self._on_trim_changed)
        trim_reset_btn = QPushButton("Reset")
        trim_reset_btn.setToolTip("Restore the full reference curve (no trim).")
        trim_reset_btn.clicked.connect(self._reset_trim)
        trim_row.addWidget(trim_reset_btn)
        trim_row.addStretch()
        ag_layout.addLayout(trim_row)

        from PyQt6.QtWidgets import QPlainTextEdit
        self.agent_log = QPlainTextEdit()
        self.agent_log.setReadOnly(True)
        self.agent_log.setMaximumBlockCount(500)
        self.agent_log.setPlaceholderText(
            "Agent log appears here after “Run Agent”.")
        self.agent_log.setMinimumHeight(110)
        ag_layout.addWidget(self.agent_log)
        left_col.addWidget(agent_group)

        left_col.addWidget(params_group)

        # --- Optimiser options ----------------------------------------------
        opts_group = QGroupBox("Optimiser")
        opts_layout = QHBoxLayout(opts_group)
        opts_layout.addWidget(QLabel("Objective:"))
        self.objective_combo = QComboBox()
        self.objective_combo.addItems(["MAE", "RMSE"])
        opts_layout.addWidget(self.objective_combo)
        opts_layout.addSpacing(12)
        opts_layout.addWidget(QLabel("Max evals:"))
        self.max_evals_spin = QSpinBox()
        self.max_evals_spin.setRange(10, 100000)
        self.max_evals_spin.setValue(120)
        opts_layout.addWidget(self.max_evals_spin)
        opts_layout.addSpacing(12)
        opts_layout.addWidget(QLabel("Restarts:"))
        self.restarts_spin = QSpinBox()
        self.restarts_spin.setRange(1, 10)
        self.restarts_spin.setValue(3)
        opts_layout.addWidget(self.restarts_spin)
        opts_layout.addStretch()
        left_col.addWidget(opts_group)
        left_col.addStretch()

        # --- Live preview ---------------------------------------------------
        preview_group = QGroupBox("Live Preview — F/F₀ vs cycle")
        pv_layout = QVBoxLayout(preview_group)
        pv_layout.setContentsMargins(6, 6, 6, 6)
        self._canvas_widget = None
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
            self._fig = Figure(figsize=(8, 5), tight_layout=True)
            self._ax = self._fig.add_subplot(111)
            self._canvas_widget = FigureCanvasQTAgg(self._fig)
            self._canvas_widget.setMinimumHeight(360)
            self._redraw_preview(sim_cycle=None, sim_ratio=None)
            pv_layout.addWidget(self._canvas_widget, stretch=1)
        except Exception:
            pv_layout.addWidget(QLabel("(matplotlib unavailable — no preview)"))
        right_col.addWidget(preview_group, stretch=3)

        # --- Progress + status ----------------------------------------------
        progress_group = QGroupBox("Progress")
        pr_layout = QVBoxLayout(progress_group)
        pr_layout.setContentsMargins(6, 6, 6, 6)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        pr_layout.addWidget(self.progress_bar)
        self.status_label = QLabel("Idle.")
        self.status_label.setWordWrap(True)
        pr_layout.addWidget(self.status_label)
        right_col.addWidget(progress_group, stretch=0)

        # --- Staged result panel --------------------------------------------
        self.staged_panel = QGroupBox("Fitted Parameters (not yet applied)")
        st_layout = QVBoxLayout(self.staged_panel)
        st_layout.setContentsMargins(6, 6, 6, 6)
        self.staged_text = QLabel("—")
        self.staged_text.setWordWrap(True)
        self.staged_text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        st_layout.addWidget(self.staged_text)
        self.staged_panel.setVisible(False)
        right_col.addWidget(self.staged_panel, stretch=1)

        # --- Action buttons --------------------------------------------------
        btn_row = QHBoxLayout()
        self.preview_btn = QPushButton("👁 Preview Current")
        self.preview_btn.setToolTip(
            "Run a single simulation with the current model parameters and "
            "overlay it on the reference (no optimisation, ~1 s).")
        self.preview_btn.clicked.connect(self._preview_current)
        self.run_btn = QPushButton("▶ Run Calibration")
        self.run_btn.setObjectName("primary")
        self.run_btn.clicked.connect(self._start_run)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel_run)
        self.apply_btn = QPushButton("✓ Apply to Model")
        self.apply_btn.setEnabled(False)
        self.apply_btn.clicked.connect(self._apply_staged)
        self.apply_rerun_btn = QPushButton("✓ Apply & Re-run")
        self.apply_rerun_btn.setEnabled(False)
        self.apply_rerun_btn.setToolTip(
            "Apply the fitted parameters to the model, then immediately re-run "
            "the Solver in the main window (no manual re-run needed).")
        self.apply_rerun_btn.clicked.connect(self._apply_and_rerun)
        self.discard_btn = QPushButton("Discard")
        self.discard_btn.setEnabled(False)
        self.discard_btn.clicked.connect(self._discard_staged)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        btn_row.addWidget(self.preview_btn)
        btn_row.addSpacing(8)
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addSpacing(16)
        btn_row.addWidget(self.apply_btn)
        btn_row.addWidget(self.apply_rerun_btn)
        btn_row.addWidget(self.discard_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.close_btn)

        # Assemble: splitter on top (fills), button row pinned at bottom.
        root.addWidget(self._splitter, stretch=1)
        bottom_bar = QFrame()
        bottom_bar.setFrameShape(QFrame.Shape.StyledPanel)
        bb_layout = QHBoxLayout(bottom_bar)
        bb_layout.setContentsMargins(8, 4, 8, 4)
        bb_layout.addLayout(btn_row)
        root.addWidget(bottom_bar, stretch=0)

        # Open maximized so users get the full preview area.
        QTimer.singleShot(0, self.showMaximized)
        # Auto-preview baseline curve on open so the user immediately sees how
        # the current model compares with the reference.
        QTimer.singleShot(50, self._preview_current)

    # ---- literature wizard ------------------------------------------------

    def _open_prior_wizard(self):
        try:
            from bolt_analysis_studio.gui.calibration_wizard import (
                CalibrationWizardDialog,
            )
        except Exception as exc:
            QMessageBox.warning(self, "Wizard unavailable",
                                f"Could not load calibration wizard:\n{exc}")
            return
        wiz = CalibrationWizardDialog(self)
        if wiz.exec() != QDialog.DialogCode.Accepted:
            return
        priors = wiz.selected_priors()
        if not priors:
            return
        n_applied = self.apply_priors(
            priors["params"], priors["bounds"], select=True)
        self.status_label.setText(
            f"Loaded priors from “{priors['label']}” — "
            f"{n_applied} parameter(s) populated.")
        # refresh baseline preview against the new defaults
        QTimer.singleShot(50, self._preview_current)

    # ---- reference curve editing ----------------------------------------

    def _active_reference(self):
        """Reference curve restricted to the trim window [_trim_lo, _trim_hi].

        Lets the user "remove a part" of an imported case-study curve (noisy
        tail, settling head, re-tightening spike) so calibration and the error
        metric (MAE/RMSE) use only the kept cycles. None bounds = full range.
        """
        ref = self._reference
        if ref is None:
            return None
        lo, hi = self._trim_lo, self._trim_hi
        if lo is None and hi is None:
            return ref
        import numpy as np
        cyc = np.asarray(ref['cycle'], dtype=float)
        mask = np.ones(cyc.shape, dtype=bool)
        if lo is not None:
            mask &= cyc >= float(lo)
        if hi is not None:
            mask &= cyc <= float(hi)
        if not np.any(mask):
            return ref            # empty crop → ignore, keep full curve
        out = {}
        for k, v in ref.items():
            try:
                arr = np.asarray(v)
                out[k] = arr[mask] if arr.shape == cyc.shape else v
            except Exception:
                out[k] = v
        return out

    def _on_trim_changed(self):
        """Apply the trim spinboxes to the reference and refresh the preview."""
        lo = float(self._trim_lo_spin.value())
        hi = float(self._trim_hi_spin.value())
        if hi <= lo:                       # invalid window → treat as full range
            self._trim_lo = self._trim_hi = None
        else:
            self._trim_lo = lo
            self._trim_hi = hi
        # Re-render the baseline/preview against the cropped reference.
        try:
            self._preview_current()
        except Exception:
            pass

    def _reset_trim(self):
        self._trim_lo = self._trim_hi = None
        if self._reference is not None:
            import numpy as np
            cyc = np.asarray(self._reference['cycle'], dtype=float)
            self._trim_lo_spin.setValue(float(cyc.min()))
            self._trim_hi_spin.setValue(float(cyc.max()))
        try:
            self._preview_current()
        except Exception:
            pass

    # ---- optimisation agent ---------------------------------------------

    def _run_optimization_agent(self):
        """Launch the autonomous multi-stage calibration agent."""
        if self._reference is None:
            QMessageBox.warning(self, "Agent",
                                "No reference curve loaded.")
            return
        if self._worker is not None:
            QMessageBox.information(self, "Agent",
                                    "A calibration is already running.")
            return
        import numpy as np
        ref = self._active_reference()
        F0_N = float(self._model.global_loading.F_preload or 0.0)
        ref_ratio = (ref['F_ratio'] if np.any(ref['F_ratio'] > 0)
                     else ref['F_kN'] * 1000.0 / max(F0_N, 1e-9))
        try:
            from bolt_analysis_studio.numerical.optimization_agent import (
                OptimizationAgent,
            )
            agent = OptimizationAgent(
                self._model, ref['cycle'], ref_ratio,
                transverse_stiffness=self._transverse_stiffness,
                objective=self.objective_combo.currentText().lower(),
                budget_evals=int(self.agent_budget_spin.value()),
            )
        except Exception as e:
            QMessageBox.critical(self, "Agent", f"Setup failed:\n{e}")
            return

        self.agent_log.clear()
        self.agent_log.appendPlainText("▶ Agent starting…")
        self._worker = _AgentWorker(agent, parent=self)
        self._worker.progress.connect(self._on_agent_progress)
        self._worker.log_message.connect(self._on_agent_log)
        self._worker.finished_ok.connect(self._on_agent_finished)
        self._worker.failed.connect(self._on_failed)
        self.agent_run_btn.setEnabled(False)
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.apply_btn.setEnabled(False)
        self.apply_rerun_btn.setEnabled(False)
        self.discard_btn.setEnabled(False)
        self.staged_panel.setVisible(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Agent running…")
        self._worker.start()

    def _on_agent_progress(self, n_done: int, n_max: int,
                           best: float, stage: str):
        pct = int(100 * n_done / max(1, n_max))
        self.progress_bar.setValue(min(100, pct))
        self.status_label.setText(
            f"{stage} · eval {n_done}/{n_max} · "
            f"best {self.objective_combo.currentText()} = {best:.4f}")

    def _on_agent_log(self, msg: str):
        self.agent_log.appendPlainText(msg)

    def _on_agent_finished(self, report):
        self.agent_run_btn.setEnabled(True)
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self._worker = None
        if report.final is None:
            self.status_label.setText(
                "Agent finished but produced no fitted result.")
            self.agent_log.appendPlainText("✗ No usable result from any stage.")
            return
        self._staged = report.final
        # Reuse the existing staged-panel rendering so Apply / Discard work.
        self._redraw_preview(report.final.sim_cycle, report.final.sim_ratio)
        lines = [
            f"<b>Agent — {report.prior_label}</b> "
            f"<span style='color:#888'>(regime: {report.regime})</span>",
            f"<b>Best {self.objective_combo.currentText()}:</b> "
            f"{report.final.best_mae:.4f}  ·  "
            f"<b>RMSE:</b> {report.final.best_rmse:.4f}  ·  "
            f"<b>Total time:</b> {report.duration_s:.1f}s",
        ]
        for s in report.stages:
            if s.skipped or s.result is None:
                lines.append(
                    f"  · <i>{s.name}: skipped — {s.skip_reason}</i>")
            else:
                lines.append(
                    f"  · <b>{s.name}:</b> "
                    f"{s.result.best_mae:.4f} after "
                    f"{s.result.n_evals} evals "
                    f"({s.result.duration_s:.1f}s)")
        lines.append("<b>Parameters:</b>")
        for name, value in report.final.best_params.items():
            if isinstance(value, float) and (abs(value) < 1e-3 or abs(value) > 1e4):
                lines.append(f"  • {name} = {value:.3e}")
            else:
                lines.append(f"  • {name} = {value:.4f}")
        self.staged_text.setText("<br>".join(lines))
        self.staged_panel.setVisible(True)
        self.apply_btn.setEnabled(True)
        self.apply_rerun_btn.setEnabled(True)
        self.discard_btn.setEnabled(True)
        self.status_label.setText(
            f"Agent finished — best {self.objective_combo.currentText()} "
            f"= {report.final.best_mae:.4f}")
        self.agent_log.appendPlainText(
            f"✓ Done in {report.duration_s:.1f}s")
        self.progress_bar.setValue(100)

    def apply_priors(self, params: dict, bounds: dict,
                     select: bool = True) -> int:
        """Write `params` defaults and `bounds` (lo, hi) onto the dialog rows.

        For each name present in both `params` and `self._param_rows`:
          • set the lo/hi spinboxes to bounds[name]
          • optionally tick the checkbox so the optimiser fits this param
        Default value itself is implicit — it lives in the analyser, not in
        a dialog widget. Returns the count of rows actually populated.
        """
        n = 0
        for name, default in params.items():
            row = self._param_rows.get(name)
            if not row:
                continue
            cb, lo_spin, hi_spin = row
            lo, hi = bounds.get(name, (default * 0.5, default * 2.0))
            try:
                lo_spin.setValue(float(lo))
                hi_spin.setValue(float(hi))
                if select:
                    cb.setChecked(True)
                n += 1
            except Exception:
                continue
        # Also push the suggested defaults onto the model so a fresh
        # _preview_current() actually reflects the literature values, not
        # the dialog's last state.
        try:
            self._apply_priors_to_model(params)
        except Exception:
            pass
        return n

    def _apply_priors_to_model(self, params: dict):
        """Stage the prior defaults onto the model's two_stage_overrides
        and mu_initial so the next baseline simulation uses them."""
        if not self._model:
            return
        gl = getattr(self._model, "global_loading", None)
        # mu_initial: write to BOTH gl (in-session) and model (persistent)
        if "mu_initial" in params:
            mu = float(params["mu_initial"])
            if gl is not None:
                try:
                    gl.mu_initial = mu
                except Exception:
                    pass
            try:
                setattr(self._model, "mu_initial", mu)
            except Exception:
                pass
        # two_stage.* fields
        ts_keys = {
            "C_loosening", "N_stage1", "delta_F1_ratio", "N_stage2",
            "k_stage2", "transition_sharpness", "F_infinity_ratio",
            "friction_recovery_gain", "creep_coefficient", "creep_exponent",
            "noise_amplitude",
        }
        overrides = getattr(self._model, "_two_stage_overrides", None)
        if overrides is None:
            overrides = {}
            try:
                setattr(self._model, "_two_stage_overrides", overrides)
            except Exception:
                return
        for k, v in params.items():
            if k in ts_keys:
                overrides[k] = float(v)

    # ---- preview helpers -------------------------------------------------

    def _redraw_preview(self, sim_cycle, sim_ratio):
        if self._canvas_widget is None:
            return
        import numpy as np
        ax = self._ax
        ax.clear()
        ref = self._active_reference()
        ref_ratio = None
        if ref is not None:
            ref_ratio = (ref['F_ratio'] if np.any(ref['F_ratio'] > 0)
                         else ref['F_kN'] / max(ref['F_kN'][0], 1e-9))
            ax.plot(ref['cycle'], ref_ratio, 'k-',
                    label='Experimental', linewidth=2.0)
        bc, br = getattr(self, "_baseline_cycle", None), getattr(
            self, "_baseline_ratio", None)
        if bc is not None and br is not None:
            ax.plot(bc, br, color='#888', linestyle=':',
                    label='Current model', linewidth=1.4)
        if sim_cycle is not None and sim_ratio is not None:
            ax.plot(sim_cycle, sim_ratio, 'r--',
                    label='Calibrated fit', linewidth=1.6)
        ax.set_xlabel("Cycle")
        ax.set_ylabel("F / F₀")
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=8)
        # Live error metric of the shown curve vs the (cropped) reference so an
        # error measure is always visible while calibrating/trimming.
        if ref_ratio is not None:
            mc, mr = ((sim_cycle, sim_ratio)
                      if (sim_cycle is not None and sim_ratio is not None)
                      else (bc, br))
            try:
                if mc is not None and mr is not None and len(ref['cycle']) > 1:
                    pred = np.interp(np.asarray(ref['cycle'], float),
                                     np.asarray(mc, float), np.asarray(mr, float))
                    e = np.abs(pred - np.asarray(ref_ratio, float))
                    mae, rmse = float(np.mean(e)), float(np.sqrt(np.mean(e ** 2)))
                    which = "fit" if (sim_ratio is not None) else "current"
                    trimmed = (self._trim_lo is not None
                               or self._trim_hi is not None)
                    span = (f"  ·  cycles {int(min(ref['cycle']))}–"
                            f"{int(max(ref['cycle']))}" if trimmed else "")
                    ax.set_title(f"MAE ({which}) = {mae:.4f}   "
                                 f"RMSE = {rmse:.4f}{span}", fontsize=9)
            except Exception:
                pass
        self._canvas_widget.draw()

    def _preview_current(self):
        """Run one simulation with the model's current parameters; overlay it.

        Provides a baseline trace so the user can see how far off the current
        model is from the reference before running optimisation.
        """
        import numpy as np
        if self._canvas_widget is None:
            return
        # V2 engine: baseline uses the non-linear DynamicStiffnessAnalyzer with
        # default tuners, so the baseline and the fit are the same model.
        engine = self._engine_keys[self.engine_combo.currentIndex()] \
            if hasattr(self, "engine_combo") else "v1"
        if engine == "v2":
            try:
                from bolt_analysis_studio.numerical.parameter_identifier import (
                    simulate_v2_curve,
                )
                gl = self._model.global_loading
                F0 = float(getattr(gl, "F_preload", 0.0) or 0.0)
                if F0 <= 0:
                    self.status_label.setText(
                        "Preview unavailable — preload (F₀) required.")
                    return
                gl_type = getattr(gl, "type", None)
                tname = getattr(gl_type, "name", str(gl_type)).upper()
                theta = {"AXIAL": 0.0, "TRANSVERSE": 1.5707963,
                         "COMBINED": 0.7853982}.get(tname, 1.5707963)
                # As constantes do PROPRIO modelo, nao os defaults do engine.
                # A curva se chama "Current model" na legenda; com tuners={}
                # ela desenhava o modelo DEFAULT, e um caso da validacao aberto
                # aqui parecia muito pior do que e' (LU2024: MAE 0,1671 contra
                # os 0,1324 do report do mesmo caso). O AJUSTE ja' parte das
                # constantes do modelo desde 2026-09-03; a linha de base tinha
                # ficado para tras, entao a tela comparava dois modelos
                # diferentes e chamava um deles de atual. Medido em 2026-09-04.
                tuners = dict(getattr(self._model, "_v2_tuner_overrides",
                                      None) or {})
                c, r = simulate_v2_curve(
                    self._model, tuners=tuners,
                    control_mode=str(getattr(gl, "control_mode", "displacement")),
                    n_cycles=int(getattr(gl, "n_cycles", 500) or 500),
                    F0=F0, F_amp=float(getattr(gl, "F_amplitude", 0.0) or 0.0),
                    theta=theta, freq=float(getattr(gl, "frequency", 0.5) or 0.5))
                self._baseline_cycle = c
                self._baseline_ratio = r
                sc = self._staged.sim_cycle if self._staged else None
                sr = self._staged.sim_ratio if self._staged else None
                self._redraw_preview(sc, sr)
                self.status_label.setText(
                    f"V2 baseline curve plotted ({len(c)} pts).")
            except Exception as e:
                self.status_label.setText(f"Preview failed: {e}")
            return
        try:
            from bolt_analysis_studio.numerical.coupled_loosening_analyzer import (
                create_analyzer_from_msd_model,
            )
            analyzer, info = create_analyzer_from_msd_model(self._model)
            gl = self._model.global_loading
            preload = float(getattr(gl, "F_preload", 0.0) or 0.0)
            F_trans = float(getattr(gl, "F_transverse", 0.0) or 0.0)
            if F_trans <= 0 and self._transverse_stiffness:
                delta_mm = float(getattr(gl, "delta_amplitude", 0.0) or 0.0)
                F_trans = (delta_mm * 1e-3) * float(self._transverse_stiffness)
            n_cycles = int(getattr(gl, "n_cycles", 500) or 500)
            if preload <= 0 or F_trans <= 0:
                self.status_label.setText(
                    "Preview unavailable — preload and transverse force required.")
                return
            result = analyzer.run_analysis(
                preload_initial=preload, F_transverse=F_trans,
                n_cycles=n_cycles,
                output_interval=max(1, n_cycles // 500))
            self._baseline_cycle = np.asarray(result.cycles, dtype=float)
            self._baseline_ratio = np.asarray(result.preload_ratio, dtype=float)
            sc = self._staged.sim_cycle if self._staged else None
            sr = self._staged.sim_ratio if self._staged else None
            self._redraw_preview(sc, sr)
            self.status_label.setText(
                f"Baseline curve plotted ({len(self._baseline_cycle)} pts).")
        except Exception as e:
            self.status_label.setText(f"Preview failed: {e}")

    # ---- run / cancel ----------------------------------------------------

    def _collect_selected_params(self):
        from bolt_analysis_studio.numerical.parameter_identifier import (
            element_msd_param,
        )
        # Index per-element key → metadata (id, kind, default, name)
        elem_meta = {key: (eid, kind, cur, ename)
                     for (key, eid, kind, cur, ename)
                     in getattr(self, "_element_param_keys", [])}
        selected = []
        for name, (cb, lo_spin, hi_spin) in self._param_rows.items():
            if not cb.isChecked():
                continue
            lo = float(lo_spin.value())
            hi = float(hi_spin.value())
            if hi <= lo:
                raise ValueError(f"{name}: hi must be greater than lo")
            if name in elem_meta:
                eid, kind, cur, ename = elem_meta[name]
                p = element_msd_param(element_id=eid, kind=kind,
                                      default=cur, lo=lo, hi=hi,
                                      element_name=ename)
                selected.append(p)
                continue
            factory = self._preset_factories[name]
            try:
                p = factory(lo=lo, hi=hi)
            except TypeError:
                p = factory()
                p.lo = lo
                p.hi = hi
            selected.append(p)
        return selected

    def _start_run(self):
        try:
            params = self._collect_selected_params()
        except Exception as e:
            QMessageBox.warning(self, "Calibrate", str(e))
            return
        # Filter params to the selected engine: V2 fits the jm.* tuners,
        # V1 fits everything else.
        engine = self._engine_keys[self.engine_combo.currentIndex()]
        if engine == "v2":
            params = [p for p in params if p.target.startswith("jm.")]
            empty_msg = ("Select at least one V2 tuner to fit "
                         "(or switch Engine to V1).")
        else:
            params = [p for p in params if not p.target.startswith("jm.")]
            empty_msg = ("Select at least one V1 parameter to fit "
                         "(or switch Engine to V2).")
        if not params:
            QMessageBox.information(self, "Calibrate", empty_msg)
            return
        import numpy as np
        ref = self._active_reference()
        if ref is None:
            QMessageBox.warning(self, "Calibrate",
                                "No reference curve loaded.")
            return
        F0_N = float(self._model.global_loading.F_preload or 0.0)
        ref_ratio = (ref['F_ratio'] if np.any(ref['F_ratio'] > 0)
                     else ref['F_kN'] * 1000.0 / max(F0_N, 1e-9))

        try:
            from bolt_analysis_studio.numerical.parameter_identifier import (
                ParameterIdentifier,
            )
            identifier = ParameterIdentifier(
                self._model, ref['cycle'], ref_ratio,
                params_to_fit=params,
                objective=self.objective_combo.currentText().lower(),
                max_evals=int(self.max_evals_spin.value()),
                transverse_stiffness=self._transverse_stiffness,
                engine=engine,
            )
        except Exception as e:
            QMessageBox.critical(self, "Calibrate", f"Setup failed:\n{e}")
            return

        self._worker = _CalibrationWorker(identifier,
                                          n_starts=int(self.restarts_spin.value()),
                                          parent=self)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_ok.connect(self._on_finished_ok)
        self._worker.failed.connect(self._on_failed)
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.apply_btn.setEnabled(False)
        self.apply_rerun_btn.setEnabled(False)
        self.discard_btn.setEnabled(False)
        self.staged_panel.setVisible(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Running…")
        self._worker.start()

    def _cancel_run(self):
        if self._worker is not None:
            self._worker.cancel()
            self.status_label.setText("Cancelling…")

    # ---- worker callbacks ------------------------------------------------

    def _on_progress(self, n_done: int, n_max: int, best_mae: float):
        pct = int(100 * n_done / max(1, n_max))
        self.progress_bar.setValue(min(100, pct))
        self.status_label.setText(
            f"Eval {n_done}/{n_max} — best {self.objective_combo.currentText()} = {best_mae:.4f}")

    def _on_finished_ok(self, result):
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self._worker = None
        if not result.success:
            self.status_label.setText(f"Failed: {result.message}")
            return
        self._staged = result
        self._redraw_preview(result.sim_cycle, result.sim_ratio)
        lines = [f"<b>Best {self.objective_combo.currentText()}:</b> {result.best_mae:.4f}",
                 f"<b>RMSE:</b> {result.best_rmse:.4f}",
                 f"<b>Evals:</b> {result.n_evals} · <b>Time:</b> {result.duration_s:.1f}s",
                 "<b>Parameters:</b>"]
        for name, value in result.best_params.items():
            if isinstance(value, float) and (abs(value) < 1e-3 or abs(value) > 1e4):
                lines.append(f"  • {name} = {value:.3e}")
            else:
                lines.append(f"  • {name} = {value:.4f}")
        self.staged_text.setText("<br>".join(lines))
        self.staged_panel.setVisible(True)
        self.apply_btn.setEnabled(True)
        self.apply_rerun_btn.setEnabled(True)
        self.discard_btn.setEnabled(True)
        self.status_label.setText(f"Done — {result.message}")
        self.progress_bar.setValue(100)

    def _on_failed(self, msg: str):
        self.run_btn.setEnabled(True)
        if hasattr(self, 'agent_run_btn'):
            self.agent_run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self._worker = None
        self.status_label.setText("Failed.")
        QMessageBox.critical(self, "Calibrate", f"Run failed:\n{msg}")

    # ---- apply / discard -------------------------------------------------

    def _apply_staged(self):
        if self._staged is None:
            return
        from bolt_analysis_studio.numerical.parameter_identifier import PRESET_PARAMS
        gl = self._model.global_loading

        # Helper: park scalar attrs on the model under a dedicated dict so they
        # survive save/load (mirrors the _two_stage_overrides pattern).
        fix = getattr(self._model, '_fixture_overrides', None)
        if fix is None:
            fix = {}
            self._model._fixture_overrides = fix
        ts_over = getattr(self._model, '_two_stage_overrides', None)
        if ts_over is None:
            ts_over = {}
            self._model._two_stage_overrides = ts_over

        # Build an element index for per-element targets and a key→meta map
        el_ix = {int(getattr(e, "id", 0)): e
                 for e in getattr(self._model, "elements", []) or []}
        elem_keys = {key: (eid, kind) for (key, eid, kind, _c, _n)
                     in getattr(self, "_element_param_keys", [])}

        for name, value in self._staged.best_params.items():
            if name in elem_keys:
                eid, kind = elem_keys[name]
                el = el_ix.get(eid)
                if el is not None and hasattr(el, "msd"):
                    setattr(el.msd, kind, float(value))
                    flag = f"auto_calculate_{kind}"
                    if hasattr(el.msd, flag):
                        setattr(el.msd, flag, False)
                continue

            if name not in PRESET_PARAMS:
                continue
            p = PRESET_PARAMS[name]()
            tgt = p.target
            if tgt == "mu_initial":
                gl.mu_initial = float(value)
                self._model.mu_initial = float(value)
            elif tgt.startswith("two_stage."):
                attr = tgt.split(".", 1)[1]
                ts_over[attr] = (int(value) if attr in ("N_stage1", "N_stage2")
                                 else float(value))
            elif tgt.startswith("jm."):
                # V2 non-linear tuners — park under a dedicated dict so they
                # survive save/load (mirrors _two_stage_overrides).
                v2_over = getattr(self._model, '_v2_tuner_overrides', None)
                if v2_over is None:
                    v2_over = {}
                    self._model._v2_tuner_overrides = v2_over
                v2_over[tgt.split(".", 1)[1]] = float(value)
            elif tgt in ("k_bolt", "k_member", "k_transverse_ratio",
                         "damping_zeta", "mu_thread", "mu_bearing",
                         "slip_onset_factor",
                         "friction.mu_steady_ratio",
                         "friction.mu_peak_ratio"):
                # Fixture overrides — applied by create_analyzer_from_msd_model
                # via a hook (see analyzer apply_fixture_overrides()).
                fix[tgt] = float(value)
                # slip_onset_factor also has a proper LoadingData field, so
                # mirror it onto global_loading for in-session immediacy.
                if tgt == "slip_onset_factor":
                    gl.slip_onset_factor = float(value)

        self.status_label.setText("Applied to model. Re-run the Solver to visualise.")
        self.apply_btn.setEnabled(False)
        self.apply_rerun_btn.setEnabled(False)
        self.discard_btn.setEnabled(False)
        self.staged_panel.setVisible(False)
        self._staged = None

    def _apply_and_rerun(self):
        """Apply the staged fit to the model, then re-run the main-window Solver.

        Equivalent to clicking "Apply to Model" and then re-running the analysis
        by hand. The dialog's parent is the main window (see
        _open_calibration_dialog), which owns _run_analysis().
        """
        if self._staged is None:
            return
        self._apply_staged()
        main_window = self.parent()
        run = getattr(main_window, "_run_analysis", None)
        if callable(run):
            # Close this (maximised, modal) dialog first so the Solver run and
            # its results are visible in the main window.
            self.accept()
            try:
                run()
            except Exception as exc:  # defensive: never let re-run raise here
                QMessageBox.warning(
                    self, "Apply & Re-run",
                    f"Applied, but the Solver re-run could not start:\n{exc}")
        else:
            QMessageBox.information(
                self, "Apply & Re-run",
                "Applied to the model. Re-run the Solver from the main window "
                "to visualise.")

    # ---- fixture profile I/O --------------------------------------------

    def _save_fixture_profile(self):
        """Save checked rows + bounds + last-fitted values to a JSON file."""
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Fixture Profile", "fixture_profile.json",
            "JSON files (*.json);;All files (*.*)")
        if not path:
            return
        import json
        from datetime import datetime
        profile = {
            "format": "BAS_FIXTURE_PROFILE_v1",
            "saved_at": datetime.now().isoformat(timespec="seconds"),
            "model_name": getattr(self._model, "name", "")
                          if self._model is not None else "",
            "objective": self.objective_combo.currentText(),
            "max_evals": int(self.max_evals_spin.value()),
            "restarts":  int(self.restarts_spin.value()),
            "params": {},
            "values": dict(getattr(self._model, '_fixture_overrides', {}) or {}),
            "two_stage_overrides":
                dict(getattr(self._model, '_two_stage_overrides', {}) or {}),
        }
        for name, (cb, lo_spin, hi_spin) in self._param_rows.items():
            profile["params"][name] = {
                "checked": bool(cb.isChecked()),
                "lo": float(lo_spin.value()),
                "hi": float(hi_spin.value()),
            }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(profile, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Save Fixture Profile",
                                 f"Failed to write file:\n{e}")
            return
        self.status_label.setText(f"Saved fixture profile → {path}")

    def _load_fixture_profile(self):
        """Restore checkboxes/bounds from a JSON profile, optionally apply values."""
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Fixture Profile", "",
            "JSON files (*.json);;All files (*.*)")
        if not path:
            return
        import json
        try:
            with open(path, "r", encoding="utf-8") as f:
                profile = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Load Fixture Profile",
                                 f"Failed to read file:\n{e}")
            return
        if profile.get("format") != "BAS_FIXTURE_PROFILE_v1":
            QMessageBox.warning(self, "Load Fixture Profile",
                                "Unrecognised profile format — proceeding anyway.")
        # Restore checkboxes + bounds
        rows = profile.get("params", {}) or {}
        for name, (cb, lo_spin, hi_spin) in self._param_rows.items():
            if name not in rows:
                continue
            cfg = rows[name]
            cb.setChecked(bool(cfg.get("checked", False)))
            try:
                lo_spin.setValue(float(cfg.get("lo", lo_spin.value())))
                hi_spin.setValue(float(cfg.get("hi", hi_spin.value())))
            except (TypeError, ValueError):
                pass
        # Restore optimiser settings if present
        try:
            obj = str(profile.get("objective", "")).upper()
            if obj in ("MAE", "RMSE"):
                self.objective_combo.setCurrentText(obj)
            self.max_evals_spin.setValue(int(profile.get("max_evals",
                                                self.max_evals_spin.value())))
            self.restarts_spin.setValue(int(profile.get("restarts",
                                                self.restarts_spin.value())))
        except Exception:
            pass

        # Offer to apply the stored values directly
        values = profile.get("values", {}) or {}
        ts_over = profile.get("two_stage_overrides", {}) or {}
        if values or ts_over:
            reply = QMessageBox.question(
                self, "Apply Stored Values?",
                "This profile contains identified parameter values. "
                "Apply them to the model now?\n\n"
                f"  fixture: {len(values)} value(s)\n"
                f"  two-stage: {len(ts_over)} value(s)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes)
            if reply == QMessageBox.StandardButton.Yes:
                gl = self._model.global_loading
                if "mu_initial" in values:
                    gl.mu_initial = float(values["mu_initial"])
                    self._model.mu_initial = float(values["mu_initial"])
                fix = dict(getattr(self._model, '_fixture_overrides', {}) or {})
                fix.update({k: float(v) for k, v in values.items()
                            if k != "mu_initial"})
                self._model._fixture_overrides = fix
                merged_ts = dict(getattr(self._model, '_two_stage_overrides', {}) or {})
                for k, v in ts_over.items():
                    merged_ts[k] = (int(v) if k in ("N_stage1", "N_stage2")
                                    else float(v))
                self._model._two_stage_overrides = merged_ts
                self.status_label.setText(
                    f"Loaded + applied profile: {path}")
                return
        self.status_label.setText(f"Loaded profile (bounds only): {path}")

    def _discard_staged(self):
        self._staged = None
        self.staged_panel.setVisible(False)
        self.apply_btn.setEnabled(False)
        self.apply_rerun_btn.setEnabled(False)
        self.discard_btn.setEnabled(False)
        self._redraw_preview(None, None)
        self.status_label.setText("Discarded staged fit.")

    def closeEvent(self, event):
        if self._worker is not None:
            self._worker.cancel()
            self._worker.wait(2000)
        super().closeEvent(event)


# =============================================================================
# MAIN WINDOW
# =============================================================================

class BoltAnalysisStudio(QMainWindow):
    """Main application window for Bolt Analysis Studio v4.0."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bolt Analysis Studio")
        self.setMinimumSize(1280, 800)

        # Application state
        self.app_state = get_app_state()

        # Transient session state for the reference-curve overlay feature.
        # Cleared on _new_project / _load_project to avoid a stale overlay
        # appearing on a freshly-opened project.
        self._reference_curve = None

        # MSD Builder window (lazy init)
        self.msd_builder_window = None
        # Flag to prevent feedback loop when MSD Builder is the source of a model change
        self._msd_builder_is_source = False

        # Solver thread
        self.solver_thread = None
        self.solver_worker = None

        # Center on screen
        screen = QGuiApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            self.setGeometry(
                geometry.x() + (geometry.width() - 1280) // 2,
                geometry.y() + (geometry.height() - 800) // 2,
                1280, 800
            )

        self._setup_ui()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_status_bar()
        self._setup_formula_dock()
        self._connect_app_state_signals()
        self._connect_tab_buttons()

        # ── Auto-save (4.1) ───────────────────────────────────────────────
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(5 * 60 * 1000)   # 5 minutes
        self._autosave_timer.timeout.connect(self._autosave)
        self._autosave_timer.start()
        self._check_autosave_on_startup()

    def closeEvent(self, event):
        """Confirm before closing the application."""
        reply = QMessageBox.question(
            self,
            "Exit Bolt Analysis Studio",
            "Are you sure you want to close Bolt Analysis Studio?\n\n"
            "Any unsaved project changes will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    # ── Recent Projects (4.2) ─────────────────────────────────────────────

    def _populate_recent_menu(self, menu: QMenu):
        """Rebuild the Recent Projects submenu on demand."""
        menu.clear()
        items = RecentProjectsManager.get()
        if not items:
            act = menu.addAction("(no recent projects)")
            act.setEnabled(False)
            return
        for item in items:
            path = item.get("path", "")
            name = item.get("name", os.path.basename(path))
            act = menu.addAction(f"{name}  —  {os.path.dirname(path)}")
            act.triggered.connect(lambda _, p=path: self._open_project_path(p))
        menu.addSeparator()
        menu.addAction("Clear Recent Projects", RecentProjectsManager.clear)

    # ── Auto-save (4.1) ───────────────────────────────────────────────────

    def _autosave(self):
        """Save the project silently to a .autosave file every 5 minutes."""
        if not self.app_state.is_dirty:
            return
        autosave_path = (
            self._current_file + ".autosave"
            if hasattr(self, "_current_file") and self._current_file
            else os.path.expanduser("~/.bolt_analysis_autosave.msd")
        )
        try:
            from bolt_analysis_studio.core.project_io import ProjectIO
            ProjectIO.save_project(
                self.app_state.project,
                self.app_state.model,
                self.app_state.results,
                autosave_path,
            )
            self.statusBar().showMessage(
                f"Auto-saved: {os.path.basename(autosave_path)}", 3000
            )
        except Exception:
            pass  # Silent — never interrupt the user

    def _check_autosave_on_startup(self):
        """On startup, offer to restore an autosave file if one exists."""
        autosave_path = os.path.expanduser("~/.bolt_analysis_autosave.msd")
        if not os.path.exists(autosave_path):
            return
        import stat
        mtime = os.path.getmtime(autosave_path)
        ts = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        reply = QMessageBox.question(
            self,
            "Restore Auto-Save",
            f"An auto-saved project from {ts} was found.\nRestore it?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._open_project_path(autosave_path)
            try:
                os.remove(autosave_path)
            except OSError:
                pass

    def _setup_ui(self):
        """Setup the main UI."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # Create tabs
        self.project_tab = ProjectTab()
        self.model_builder_tab = ModelBuilderTab()
        self.solver_tab = SolverTab()
        self.results_tab = ResultsTab()

        # Use enhanced similitude tab if available
        if HAS_ENHANCED_SIMILITUDE:
            self.similitude_tab = create_similitude_tab()
        else:
            self.similitude_tab = SimilitudeTab()

        self.reports_tab = ReportsTab()

        # Create documentation tab if available
        if HAS_DOCUMENTATION_TAB:
            self.documentation_tab = DocumentationTab()
        else:
            self.documentation_tab = QWidget()  # Placeholder

        # Add tabs with icons
        self.tab_widget.addTab(self.project_tab, "Project")
        self.tab_widget.addTab(self.model_builder_tab, "Model Builder")
        self.tab_widget.addTab(self.solver_tab, "Solver")
        self.tab_widget.addTab(self.results_tab, "Results")
        self.tab_widget.addTab(self.similitude_tab, "Similitude")
        self.tab_widget.addTab(self.reports_tab, "Reports")
        self.tab_widget.addTab(self.documentation_tab, "Documentation")
        
        main_layout.addWidget(self.tab_widget)

        # Connect signals
        self.model_builder_tab.msd_builder_requested.connect(self._open_msd_builder)
        self.model_builder_tab.case_studies_requested.connect(self._show_validation_suite)
        self.model_builder_tab.validate_requested.connect(self._validate_model)
        self.model_builder_tab.send_to_solver_requested.connect(self._send_model_to_solver)

        # The MSD Builder is embedded inside Tab 2 — wire its model_changed
        # signal so edits immediately propagate to app_state + solver summary.
        self.msd_builder_window = self.model_builder_tab.builder
        self.msd_builder_window.model_changed.connect(self._on_msd_builder_model_changed)

        # Connect enhanced similitude tab signals if available
        if HAS_ENHANCED_SIMILITUDE and hasattr(self.similitude_tab, 'transfer_to_builder'):
            self.similitude_tab.transfer_to_builder.connect(self._on_similitude_transfer)

        # U6: Send to Solver signal
        if HAS_ENHANCED_SIMILITUDE and hasattr(self.similitude_tab, 'send_to_solver'):
            self.similitude_tab.send_to_solver.connect(self._on_similitude_send_to_solver)

        # U2: Import from MSD Builder signal
        if HAS_ENHANCED_SIMILITUDE and hasattr(self.similitude_tab, 'import_from_model_requested'):
            self.similitude_tab.import_from_model_requested.connect(
                self._on_similitude_import_model
            )

        # CRITICAL-03: Wire similitude scaling result into app_state (MED-03)
        if HAS_ENHANCED_SIMILITUDE and hasattr(self.similitude_tab, 'scaling_panel'):
            self.similitude_tab.scaling_panel.scaling_computed.connect(
                self._on_similitude_scaling_computed
            )

    def _setup_menu_bar(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Project", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_project)
        file_menu.addAction(new_action)

        wizard_action = QAction("Nova Análise (&Wizard)…", self)
        wizard_action.setShortcut("Ctrl+Shift+N")
        wizard_action.triggered.connect(self._open_new_analysis_wizard)
        file_menu.addAction(wizard_action)

        # New from Template submenu (4.3)
        template_menu = file_menu.addMenu("New from &Template")
        _templates = [
            ("Single Bolt (M12)", "single_bolt"),
            ("Flanged Joint with Gasket (M16)", "flanged_joint"),
            ("Junker Test Setup (M16)", "junker_test"),
        ]
        for _label, _preset in _templates:
            _act = QAction(_label, self)
            _act.triggered.connect(
                lambda _, p=_preset: self._new_from_template(p)
            )
            template_menu.addAction(_act)

        open_action = QAction("&Open Project...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_project)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_project)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self._save_project)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        recent_menu = file_menu.addMenu("Recent &Projects")
        recent_menu.aboutToShow.connect(
            lambda: self._populate_recent_menu(recent_menu)
        )

        file_menu.addSeparator()

        export_menu = file_menu.addMenu("&Export")
        export_menu.addAction(QAction("Export Model (.json)", self))
        export_menu.addAction(QAction("Export Results (.csv)", self))
        export_menu.addAction(QAction("Export Report (.pdf)", self))
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        prefs_action = QAction("&Preferences...", self)
        prefs_action.setShortcut(QKeySequence("Ctrl+,"))
        prefs_action.triggered.connect(self._show_preferences)
        edit_menu.addAction(prefs_action)

        # View menu
        view_menu = menubar.addMenu("&View")
        theme_menu = view_menu.addMenu("Theme")
        from PyQt6.QtGui import QActionGroup
        from bolt_analysis_studio.gui.theme import PALETTE_NAMES
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)
        self._theme_actions = {}
        for key, display_name in PALETTE_NAMES.items():
            action = QAction(display_name, self, checkable=True)
            action.setData(key)
            if key == Theme.current_name():
                action.setChecked(True)
            theme_group.addAction(action)
            theme_menu.addAction(action)
            self._theme_actions[key] = action
        theme_group.triggered.connect(self._on_theme_changed)

        view_menu.addSeparator()
        self._formula_dock_action = QAction("Formula Reference", self, checkable=True)
        self._formula_dock_action.setShortcut(QKeySequence("F1"))
        self._formula_dock_action.triggered.connect(self._toggle_formula_dock)
        view_menu.addAction(self._formula_dock_action)

        # Model menu
        model_menu = menubar.addMenu("&Model")

        open_builder_action = QAction("Open MSD Builder", self)
        open_builder_action.triggered.connect(self._open_msd_builder)
        model_menu.addAction(open_builder_action)
        model_menu.addSeparator()

        load_model_action = QAction("Load Model...", self)
        load_model_action.triggered.connect(self._load_model)
        model_menu.addAction(load_model_action)

        save_model_action = QAction("Save Model...", self)
        save_model_action.triggered.connect(self._save_model)
        model_menu.addAction(save_model_action)
        model_menu.addSeparator()

        validate_action = QAction("Validate Model", self)
        validate_action.triggered.connect(self._validate_model)
        model_menu.addAction(validate_action)

        # Analysis menu
        analysis_menu = menubar.addMenu("&Analysis")

        run_action = QAction("&Run Analysis", self)
        run_action.setShortcut(QKeySequence("F5"))
        run_action.triggered.connect(self._run_analysis)
        analysis_menu.addAction(run_action)

        stop_action = QAction("Stop Analysis", self)
        stop_action.triggered.connect(self._stop_analysis)
        analysis_menu.addAction(stop_action)
        analysis_menu.addSeparator()
        batch_action = QAction("Batch Analysis...", self)
        batch_action.triggered.connect(self._show_batch_analysis)
        analysis_menu.addAction(batch_action)

        validation_action = QAction("Validation Suite...", self)
        validation_action.triggered.connect(self._show_validation_suite)
        analysis_menu.addAction(validation_action)

        analysis_menu.addSeparator()
        load_ref_action = QAction("Load Reference CSV...", self)
        load_ref_action.setShortcut(QKeySequence("Ctrl+R"))
        load_ref_action.triggered.connect(self._load_reference_csv)
        analysis_menu.addAction(load_ref_action)

        calibrate_action = QAction("Calibrate Model...", self)
        calibrate_action.setShortcut(QKeySequence("Ctrl+K"))
        calibrate_action.setStatusTip(
            "Open parameter-identification dialog (μ, k, ζ, two-stage, curve-shape)")
        calibrate_action.triggered.connect(self._open_calibration_dialog)
        analysis_menu.addAction(calibrate_action)

        auto_cal_action = QAction("μ Auto-calibrate (Quick)", self)
        auto_cal_action.triggered.connect(self._auto_calibrate_mu)
        analysis_menu.addAction(auto_cal_action)

        analysis_menu.addSeparator()
        analysis_menu.addAction(QAction("Configure Solver...", self))
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        mat_db_action = QAction("Material Database", self)
        mat_db_action.triggered.connect(self._show_material_database)
        tools_menu.addAction(mat_db_action)
        tools_menu.addAction(QAction("Thread Calculator", self))
        tools_menu.addAction(QAction("Torque-Tension Calculator", self))
        tools_menu.addSeparator()
        tools_menu.addAction(QAction("Unit Converter", self))

        # Web tools — open local artefacts in the default browser (uses the
        # stdlib `webbrowser` module, so no QWebEngine dependency is required).
        tools_menu.addSeparator()
        tuner_action = QAction("Calibration Tuner (web)", self)
        tuner_action.setStatusTip(
            "Start the local calibration server and open the tuner at "
            "http://localhost:8765 in your browser.")
        tuner_action.triggered.connect(self._open_calibration_tuner)
        tools_menu.addAction(tuner_action)

        gallery_action = QAction("Validation Gallery (web)", self)
        gallery_action.setStatusTip(
            "Open the local validation report / loosening explorer in your browser.")
        gallery_action.triggered.connect(self._open_validation_gallery)
        tools_menu.addAction(gallery_action)

        # Similitude submenu
        tools_menu.addSeparator()
        similitude_menu = tools_menu.addMenu("Similitude Analysis")

        multi_bolt_action = QAction("Multi-Bolt to Single-Bolt Reduction", self)
        multi_bolt_action.triggered.connect(lambda: self._go_to_similitude_tab(0))
        similitude_menu.addAction(multi_bolt_action)

        scaling_action = QAction("Geometric Scaling (Loosening)", self)
        scaling_action.triggered.connect(lambda: self._go_to_similitude_tab(1))
        similitude_menu.addAction(scaling_action)

        similitude_menu.addSeparator()
        pi_calc_action = QAction("Π-Group Calculator", self)
        pi_calc_action.triggered.connect(lambda: self._go_to_similitude_tab(0))
        similitude_menu.addAction(pi_calc_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")

        doc_action = QAction("Documentation", self)
        doc_action.setShortcut(QKeySequence("F1"))
        doc_action.triggered.connect(self._show_documentation)
        help_menu.addAction(doc_action)

        help_menu.addAction(QAction("VDI 2230 Reference", self))
        help_menu.addSeparator()

        about_action = QAction("About Bolt Analysis Studio", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        # ── Tab keyboard shortcuts (10.2) ─────────────────────────────────
        tab_names = ["Project", "Builder", "Solver", "Results",
                     "Similitude", "Reports", "Documentation"]
        for i, name in enumerate(tab_names):
            sc = QShortcut(QKeySequence(f"Ctrl+{i + 1}"), self)
            sc.activated.connect(
                lambda _, idx=i: self.tab_widget.setCurrentIndex(idx)
            )
            sc.setWhatsThis(f"Switch to {name} tab")

        QShortcut(QKeySequence("Ctrl+Tab"), self).activated.connect(
            lambda: self.tab_widget.setCurrentIndex(
                (self.tab_widget.currentIndex() + 1) % self.tab_widget.count()
            )
        )
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self).activated.connect(
            lambda: self.tab_widget.setCurrentIndex(
                (self.tab_widget.currentIndex() - 1) % self.tab_widget.count()
            )
        )
        QShortcut(QKeySequence("Ctrl+Shift+P"), self).activated.connect(
            self._show_command_palette
        )
        QShortcut(QKeySequence("F9"), self).activated.connect(
            self._open_msd_builder
        )

    def _setup_toolbar(self):
        """Setup the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Add toolbar actions with connections
        new_action = QAction(icon("new"), "New", self)
        new_action.triggered.connect(self._new_project)
        toolbar.addAction(new_action)

        open_action = QAction(icon("open"), "Open", self)
        open_action.triggered.connect(self._open_project)
        toolbar.addAction(open_action)

        save_action = QAction(icon("save"), "Save", self)
        save_action.triggered.connect(self._save_project)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        builder_action = QAction(icon("element"), "MSD Builder", self)
        builder_action.triggered.connect(self._open_msd_builder)
        toolbar.addAction(builder_action)

        toolbar.addSeparator()

        run_action = QAction(icon("run"), "Run", self)
        run_action.triggered.connect(self._run_analysis)
        toolbar.addAction(run_action)

        stop_action = QAction(icon("stop"), "Stop", self)
        stop_action.triggered.connect(self._stop_analysis)
        toolbar.addAction(stop_action)

        toolbar.addSeparator()

        plots_action = QAction(icon("validation"), "Plots", self)
        plots_action.triggered.connect(self._generate_plots)
        toolbar.addAction(plots_action)

        similitude_action = QAction(icon("settings"), "Similitude", self)
        similitude_action.setToolTip("Similitude Analysis: Multi-bolt reduction & geometric scaling")
        similitude_action.triggered.connect(lambda: self._go_to_similitude_tab(0))
        toolbar.addAction(similitude_action)

        report_action = QAction(icon("report"), "Report", self)
        report_action.triggered.connect(self._export_report)
        toolbar.addAction(report_action)
    
    def _setup_status_bar(self):
        """Setup the status bar."""
        status_bar = self.statusBar()
        # Expose as attribute so self.status_bar.showMessage(...) works
        # across the codebase (reference-curve overlay, μ sweep, etc.).
        self.status_bar = status_bar

        # Model status
        self.model_status = QLabel("Model: Not loaded")
        status_bar.addWidget(self.model_status)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet(f"color: {Theme.SURFACE1};")
        status_bar.addWidget(separator)
        
        # Analysis status
        self.analysis_status = QLabel("Analysis: Ready")
        status_bar.addWidget(self.analysis_status)
        
        # Permanent widget on right side
        version_label = QLabel("v4.0")
        status_bar.addPermanentWidget(version_label)

    # ── §6.5 Formula reference dock ────────────────────────────────────
    _FORMULA_PAGES = {
        0: ("Project", """<h3>Project</h3>
<p>No formulas — configure project metadata, units, and file paths.</p>"""),
        1: ("Model Builder", """<h3>ISO metric thread geometry</h3>
<p>d₂ = d − 0.6495·P &nbsp;&nbsp;(pitch diameter)<br>
d₁ = d − 1.0825·P &nbsp;&nbsp;(minor diameter)<br>
A_s = (π/4)·((d₂+d₁)/2)² &nbsp;&nbsp;(stress area)</p>
<h3>Preload from yield fraction</h3>
<p>F₀ = η·S_y·A_s,&nbsp; typical η = 0.70 (VDI 2230)</p>
<h3>Helix angle &amp; self-locking</h3>
<p>λ = arctan(P / (π·d₂))<br>
self-locking: µ·cos α > tan λ&nbsp;&nbsp; (α = flank half-angle, 30° for M)</p>"""),
        2: ("Solver", """<h3>Loading</h3>
<p>Transverse excitation F_T(t) = F_T0·sin(2π·f·t)<br>
Biased harmonic: F(t) = F_m + F_a·waveform(2π·f·t + φ)·DF</p>
<h3>Slip onset (Pai–Hess)</h3>
<p>Slip ≔ F_T &gt; 0.46·µ·F_p &nbsp;&nbsp;(vs classical Coulomb 1.0·µ·F_p)</p>
<h3>Jiang 5-stage boundaries &nbsp;[LMQ §12.5]</h3>
<ul>
<li>STABLE: F/F₀ &gt; 0.90 &nbsp;(Stage I)</li>
<li>NON-ROTATIONAL: 0.75 &lt; F/F₀ &lt; 0.90 &nbsp;(Stage I)</li>
<li>TRANSITION: 0.55 &lt; F/F₀ &lt; 0.75 &nbsp;(Stage II onset at 0.5° rotation)</li>
<li>ROTATIONAL: 0.20 &lt; F/F₀ &lt; 0.55</li>
<li>RUNAWAY: F/F₀ ≤ 0.20 or SL margin &lt; 0</li>
</ul>
<p>ISO 16130:2015 retention ≥ 85% (good zone); DIN 25201-4 ≥ 80%.</p>"""),
        3: ("Results", """<h3>Self-locking margin &nbsp;[§6.7]</h3>
<p>SL = (µ·cos α − tan λ) / tan λ<br>
&nbsp;&nbsp;&gt; 1 strongly self-locking · 0.1–1 caution · &lt; 0.1 lost</p>
<h3>Fretting regime &nbsp;(Vingsbo–Söderberg)</h3>
<p>δ &lt; 5 µm → STICK · 5–50 µm → PARTIAL SLIP (fretting) · &gt; 50 µm → GROSS SLIP</p>
<h3>Miner's rule</h3>
<p>D = Σ n_i / N_f(σ_i);&nbsp; failure when D ≥ 1</p>"""),
        4: ("Similitude", """<h3>Buckingham Π groups (bolted joint)</h3>
<p>Π₁ = F/(E·d²),&nbsp; Π₂ = F/(µ·F₀),&nbsp; Π₃ = δ/d,&nbsp;
Π₄ = ω·√(m/k),&nbsp; Π₅ = N</p>
<p>Geometric scale λ_L: k ∝ λ_L, m ∝ λ_L³, f ∝ 1/λ_L,
&nbsp;F_preload ∝ λ_L².</p>"""),
        5: ("Reports", """<h3>Retorque interval (CMMS)</h3>
<p>N_retorque = N at which F/F₀ = 0.85<br>
T_hours = N_retorque / (f · 3600 · duty)<br>
T_tighten ≈ 0.2·F₀·d (K-factor)</p>"""),
        6: ("Documentation", """<h3>References</h3>
<p>VDI 2230 Part 1 (2015), ISO 16130:2015, DIN 65151 (2002),
DIN 25201-4 (2010), Jiang (2003/2004), Pai &amp; Hess (2002),
Vingsbo &amp; Söderberg (1988).</p>"""),
    }

    def _setup_formula_dock(self):
        """Create a right-side QDockWidget with per-tab formulas (F1 to toggle)."""
        try:
            from PyQt6.QtWidgets import QDockWidget
        except Exception:
            self.formula_dock = None
            return
        self.formula_dock = QDockWidget("Formula Reference", self)
        self.formula_dock.setObjectName("FormulaReferenceDock")
        self.formula_dock.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea
        )
        self._formula_browser = QTextEdit()
        self._formula_browser.setReadOnly(True)
        self._formula_browser.setStyleSheet(
            f"QTextEdit {{background:{Theme.MANTLE}; color:{Theme.TEXT};"
            f" font-family:{Theme.FONT_SERIF}; font-size:10pt;}}"
        )
        self.formula_dock.setWidget(self._formula_browser)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.formula_dock)
        self.formula_dock.hide()
        # Update on tab change
        self.tab_widget.currentChanged.connect(self._update_formula_dock)
        self._update_formula_dock(self.tab_widget.currentIndex())
        # Keep menu checkbox in sync with dock visibility
        self.formula_dock.visibilityChanged.connect(
            lambda vis: self._formula_dock_action.setChecked(vis)
            if hasattr(self, '_formula_dock_action') else None
        )

    def _update_formula_dock(self, idx: int):
        if getattr(self, 'formula_dock', None) is None:
            return
        title, html = self._FORMULA_PAGES.get(idx, ("Reference", "<p>—</p>"))
        self.formula_dock.setWindowTitle(f"Formulas — {title}")
        self._formula_browser.setHtml(html)

    def _toggle_formula_dock(self):
        if getattr(self, 'formula_dock', None) is None:
            return
        self.formula_dock.setVisible(not self.formula_dock.isVisible())

    def _connect_app_state_signals(self):
        """Connect AppState signals to UI updates."""
        self.app_state.project_changed.connect(self._on_project_changed)
        self.app_state.model_changed.connect(self._on_model_changed)
        self.app_state.results_changed.connect(self._on_results_changed)
        self.app_state.status_changed.connect(self._on_status_message)
        self.app_state.error_occurred.connect(self._on_error)

    def _connect_tab_buttons(self):
        """Connect buttons in all tabs to their handlers."""
        # ProjectTab — use named signals + objectName-based button lookup
        pt = self.project_tab
        if hasattr(pt, 'open_recent_requested'):
            pt.open_recent_requested.connect(self._open_project_path)
        if hasattr(pt, 'template_requested'):
            pt.template_requested.connect(self._apply_project_template)
        if hasattr(pt, 'save_requested'):
            pt.save_requested.connect(self._save_project)
        if hasattr(pt, 'project_info_changed'):
            pt.project_info_changed.connect(self._mark_project_modified)
        if hasattr(pt, 'new_analysis_wizard_requested'):
            pt.new_analysis_wizard_requested.connect(self._open_new_analysis_wizard)

        # Connect Quick Actions buttons by objectName
        for child in pt.findChildren(QPushButton):
            name = child.objectName()
            text = child.text()
            if name == "new_btn" or "New" in text:
                child.clicked.connect(self._new_project)
            elif name == "open_btn" or "Open" in text:
                child.clicked.connect(self._open_project)
            elif name == "export_btn" or "Export" in text:
                child.clicked.connect(self._export_report)
            # "primary" save_btn handled via save_requested signal

        # Connect ModelBuilderTab buttons.
        #
        # FRAGILE WIRING WARNING (reviewed; deliberately left as-is):
        # Handlers are wired by substring-matching the button *label* text. This
        # is fragile and cannot be robustly fixed from this file alone:
        #   * The Load/Save/Clear buttons this targets are created inside
        #     gui/msd_builder.py (the embedded builder's central widget), which
        #     is out of edit scope — so they cannot be given objectNames at their
        #     creation site for a direct / objectName-based connection here.
        #   * The substring test over-matches: builder buttons such as
        #     "Edit Loads..." and "Apply Load/Constraint..." also contain "Load"
        #     and thus get (incorrectly) connected to _load_model.
        #   * The header "✓ Validate Model" button (built in ModelBuilderTab) is
        #     ALREADY wired via validate_requested → _validate_model (see the
        #     signal connections in _connect_signals), so the "Validate" branch
        #     below double-connects it.
        # A proper fix = assign objectNames in msd_builder.py and match on
        # objectName here. Left untouched to preserve current behaviour.
        for child in self.model_builder_tab.findChildren(QPushButton):
            text = child.text()
            if "Load" in text:
                child.clicked.connect(self._load_model)
            elif "Save" in text and "Model" in text:
                child.clicked.connect(self._save_model)
            elif "Clear" in text:
                child.clicked.connect(self._clear_model)
            elif "Validate" in text:
                child.clicked.connect(self._validate_model)

        # Connect SolverTab buttons
        self.solver_tab.run_btn.clicked.connect(self._run_analysis)
        self.solver_tab.pause_btn.clicked.connect(self._pause_analysis)
        self.solver_tab.stop_btn.clicked.connect(self._stop_analysis)
        self.solver_tab.iso16130_btn.clicked.connect(self._run_iso16130_test)
        self.solver_tab.suggest_dt_btn.clicked.connect(self._suggest_timestep)
        self.solver_tab.edit_loading_btn.clicked.connect(self._open_msd_builder)  # Edit loading → open MSD Builder

        # Auto-calculate timestep when cycles, frequency, or sampling params change
        self.solver_tab.n_cycles_spin.valueChanged.connect(self._auto_calculate_timestep)
        self.solver_tab.frequency_spin.valueChanged.connect(self._auto_calculate_timestep)
        self.solver_tab.sample_pct_spin.valueChanged.connect(self._auto_calculate_timestep)
        self.solver_tab.target_points_spin.valueChanged.connect(self._auto_calculate_timestep)

        # Cycles/Time toggle signals
        # sim_cycles_spin drives n_cycles_spin; n_cycles_spin already triggers _auto_calculate_timestep
        self.solver_tab.sim_cycles_spin.valueChanged.connect(self.solver_tab.n_cycles_spin.setValue)
        self.solver_tab.t_end_spin.valueChanged.connect(self._on_t_end_changed)
        self.solver_tab.dur_cycles_radio.toggled.connect(self._on_sim_mode_changed)

        # Connect ResultsTab buttons
        self.results_tab.export_data_btn.clicked.connect(self._export_results)
        self.results_tab.dashboard_btn.clicked.connect(self._show_dashboard)
        self.results_tab.pin_btn.clicked.connect(self._pin_results)
        self.results_tab.clear_pins_btn.clicked.connect(self._clear_pinned_results)

        # Connect simplified plot toolbar buttons
        self.results_tab.open_window_btn.clicked.connect(self._open_plot_in_editor)
        self.results_tab.quick_export_btn.clicked.connect(self._export_plot_with_options)
        self.results_tab.refresh_btn.clicked.connect(self._refresh_current_plot)
        self.results_tab.ref_load_btn.clicked.connect(self._load_reference_csv)
        self.results_tab.ref_clear_btn.clicked.connect(self._clear_reference_curve)
        self.results_tab.auto_calibrate_btn.clicked.connect(self._auto_calibrate_mu)
        self.results_tab.calibrate_btn.clicked.connect(self._open_calibration_dialog)

        # Connect results tree selection
        self.results_tab.results_tree.itemClicked.connect(self._on_result_category_selected)

        # Stage Analysis overlay combo — re-plot when selection changes
        self.results_tab.stage_overlay_combo.currentIndexChanged.connect(
            self._on_stage_overlay_changed)
        # Stage Analysis replay button
        self.results_tab.stage_replay_btn.clicked.connect(
            self._on_stage_overlay_changed)
        # Stage Analysis save GIF button
        self.results_tab.stage_gif_btn.clicked.connect(
            self._save_stage_animation_gif)

        # Connect ReportsTab buttons
        self.reports_tab.preview_requested.connect(self._update_report_preview)
        self.reports_tab.generate_requested.connect(self._generate_report)
        self.reports_tab.cmms_export_requested.connect(self._export_cmms_csv)

        # Debounced live preview (6.4): auto-refresh 0.5 s after any option change
        _preview_timer = QTimer(self)
        _preview_timer.setSingleShot(True)
        _preview_timer.setInterval(500)
        _preview_timer.timeout.connect(self._update_report_preview)
        self.reports_tab.report_type.currentIndexChanged.connect(_preview_timer.start)
        for _cb in self.reports_tab.section_checks.values():
            _cb.toggled.connect(_preview_timer.start)

        # Store plot editor windows
        self._plot_editor_windows = []

    # =========================================================================
    # HELP MENU ACTIONS
    # =========================================================================

    def _show_documentation(self):
        """Show the documentation tab."""
        # Find the documentation tab index
        for i in range(self.tab_widget.count()):
            if "Documentação" in self.tab_widget.tabText(i) or "Documentation" in self.tab_widget.tabText(i):
                self.tab_widget.setCurrentIndex(i)
                return
        # Fallback to last tab
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

    def _on_theme_changed(self, action):
        """Handle theme switch from View > Theme menu."""
        import matplotlib.pyplot as plt
        name = action.data()
        Theme.set_theme(name)
        Theme.save_theme_preference()

        # Re-apply global stylesheet
        app = QApplication.instance()
        if app:
            app.setStyleSheet(Theme.get_stylesheet())

        # Re-apply matplotlib style
        plt.style.use(Theme.get_matplotlib_style_name())
        plt.rcParams.update(Theme.get_plot_style())

        # Re-theme EVERY matplotlib canvas (figure/axes facecolor, text,
        # spines) — plots bake the palette in at draw time, so a theme switch
        # must re-apply to ALL of them, not just the active Results plot.
        self._retheme_all_matplotlib_canvases()
        # Full re-render of the active Results plot (re-draws data too).
        try:
            self._refresh_current_plot()
        except Exception:
            pass

        # Refresh MSD Builder if open
        if hasattr(self, 'msd_builder_window') and self.msd_builder_window is not None:
            try:
                self.msd_builder_window.refresh_theme()
            except Exception:
                pass

        # Refresh all tabs with inline stylesheets
        for tab in [self.project_tab, self.solver_tab, self.results_tab,
                    self.similitude_tab, self.reports_tab,
                    getattr(self, 'documentation_tab', None)]:
            if tab is not None and hasattr(tab, 'refresh_theme'):
                try:
                    tab.refresh_theme()
                except Exception:
                    pass

        # Refresh enhanced similitude tab if present
        if hasattr(self, 'enhanced_similitude_tab'):
            tab = self.enhanced_similitude_tab
            if hasattr(tab, 'refresh_theme'):
                try:
                    tab.refresh_theme()
                except Exception:
                    pass

        self.statusBar().showMessage(f"Theme changed to {name}", 3000)

    def _retheme_all_matplotlib_canvases(self):
        """Re-apply the current palette to EVERY matplotlib canvas in the app.

        Plots set the figure/axes facecolor at draw time, so on a theme switch
        the already-drawn canvases keep the OLD (e.g. light) background. Walk
        the whole widget tree and re-theme each one. Custom canvases that ship
        an ``_apply_theme()`` are asked to re-theme themselves; raw
        FigureCanvasQTAgg get a manual facecolor/text/spine pass.
        """
        try:
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        except Exception:
            return
        base, text, sub = Theme.BASE, Theme.TEXT, Theme.SUBTEXT
        roots = [self]
        mbw = getattr(self, 'msd_builder_window', None)
        if mbw is not None:
            roots.append(mbw)
        seen = set()
        for root in roots:
            for canvas in root.findChildren(FigureCanvasQTAgg):
                if id(canvas) in seen:
                    continue
                seen.add(id(canvas))
                try:
                    if hasattr(canvas, '_apply_theme'):
                        canvas._apply_theme()
                    else:
                        fig = canvas.figure
                        fig.set_facecolor(base)
                        for ax in fig.get_axes():
                            ax.set_facecolor(base)
                            ax.tick_params(colors=text)
                            ax.xaxis.label.set_color(text)
                            ax.yaxis.label.set_color(text)
                            ax.title.set_color(text)
                            for spine in ax.spines.values():
                                spine.set_color(sub)
                            leg = ax.get_legend()
                            if leg is not None:
                                leg.get_frame().set_facecolor(base)
                                leg.get_frame().set_edgecolor(sub)
                                for t in leg.get_texts():
                                    t.set_color(text)
                    canvas.draw_idle()
                except Exception:
                    pass

    def _show_about(self):
        """Show about dialog."""
        about_text = """
<h2>Bolt Analysis Studio v4.0</h2>
<p>Bolted Joint Self-Loosening Analysis Software</p>

<h3>Features:</h3>
<ul>
<li>Complete MSD (Mass-Spring-Damper) model</li>
<li>Junker self-loosening mechanism</li>
<li>Jiang two-phase model (S-curve)</li>
<li>Three-phase friction evolution</li>
<li>Time-varying wear model</li>
<li>16 analysis plot types</li>
<li>VDI 2230 safety calculations</li>
</ul>

<h3>Developers:</h3>
<p><b>Prof. Leonardo Rosa Ribeiro da Silva, PhD</b><br>
<a href="mailto:leorrs@ancora_interna.br">leorrs@ancora_interna.br</a><br>
<b>Neilon de Souza da Silva, PhD</b><br>
<a href="mailto:neilon@petrobras.com.br">neilon@petrobras.com.br</a></p>

<p><i>January 2026</i></p>
"""
        QMessageBox.about(self, "About Bolt Analysis Studio", about_text)

    def _show_preferences(self):
        """Open the Preferences dialog."""
        dlg = PreferencesDialog(self)
        dlg.exec()

    def _show_command_palette(self):
        """Open the command palette (Ctrl+Shift+P)."""
        dlg = CommandPalette(self, self)
        dlg.exec()

    def _show_material_database(self):
        """Open the Material Database editor dialog."""
        dlg = MaterialDatabaseDialog(self)
        dlg.exec()

    def _new_from_template(self, preset_name: str):
        """
        Start a new project using a built-in MSD preset template (4.3).

        Opens/activates the MSD Builder and loads the chosen preset.
        """
        # Open MSD Builder tab
        self.tab_widget.setCurrentIndex(1)
        if self.msd_builder_window is None:
            return
        # Confirm if dirty
        if self.app_state.is_dirty:
            reply = QMessageBox.question(
                self, "New from Template",
                "You have unsaved changes. Continue and lose current model?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self.msd_builder_window._add_preset(preset_name)
        self._on_status_message(f"Loaded template: {preset_name}")

    def _show_validation_suite(self):
        """Open the Validation Suite Runner dialog."""
        dlg = ValidationSuiteDialog(self)
        dlg.exec()

    def _show_batch_analysis(self):
        """Open the Batch Analysis dialog."""
        cfg = None
        if self.app_state.model is not None:
            # Use current model's loosening config
            from bolt_analysis_studio.core.solver_worker import CoupledLooseningConfig
            cfg = CoupledLooseningConfig()
            model = self.app_state.model
            gl = model.global_loading
            cfg.initial_preload = gl.F_preload
            cfg.transverse_force = gl.F_transverse
            cfg.n_cycles = gl.n_cycles
            cfg.mu_initial = getattr(model, 'mu_initial', 0.12)
            cfg.bolt_diameter_mm = getattr(model, 'bolt_diameter', 16.0)
            cfg.pitch_mm = getattr(model, 'pitch', 2.0)
        if cfg is None:
            from bolt_analysis_studio.core.solver_worker import CoupledLooseningConfig
            cfg = CoupledLooseningConfig()
        dlg = BatchAnalysisDialog(cfg, self)
        dlg.exec()

    # =========================================================================
    # PROJECT OPERATIONS
    # =========================================================================

    def _new_project(self):
        """Create a new project."""
        if self.app_state.is_dirty:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Do you want to save before creating a new project?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Save:
                self._save_project()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        self.app_state.new_project()
        self._update_project_ui()
        self.model_status.setText("Model: Not loaded")
        self.analysis_status.setText("Analysis: Ready")

    def _open_new_analysis_wizard(self):
        """Run the 5-page New Analysis wizard, materialise the model, open Builder."""
        from bolt_analysis_studio.gui.new_analysis_wizard import (
            NewAnalysisWizard, build_model,
        )
        wiz = NewAnalysisWizard(self)
        if wiz.exec() != QDialog.DialogCode.Accepted:
            return
        spec = wiz.spec()
        try:
            model = build_model(spec)
        except Exception as e:
            QMessageBox.critical(self, "Wizard error",
                                 f"Failed to build model:\n{e}")
            return

        # _open_msd_builder() switches to the Builder tab AND calls
        # load_from_msd_model(self.app_state.model) — set the model first,
        # then let _open_msd_builder do the render in one shot.
        self.app_state.model = model
        try:
            self._open_msd_builder()
        except Exception as e:
            QMessageBox.warning(self, "Builder load",
                                f"Model created but builder failed to render:\n{e}")

        # Optional reference CSV overlay
        if wiz.will_load_reference():
            ref_path = (spec.reference_csv_path or "").strip()
            if ref_path:
                self._load_reference_csv(ref_path)

        self._on_status_message(
            f"Wizard: created {spec.joint_preset_id} model — edit freely in Builder.")

    def _open_project(self):
        """Open an existing project via file dialog."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Project",
            "", "Bolt Analysis Project (*.bap);;All Files (*)"
        )
        if filepath:
            self._open_project_path(filepath)

    def _open_project_path(self, filepath: str):
        """Load a project from a known file path (from recent list or dialog)."""
        project, model, results = ProjectIO.load_project(filepath)
        if project:
            self.app_state._project = project
            self.app_state._model = model
            self.app_state._results = results
            self.app_state._dirty = False

            # Emit signals
            self.app_state.project_changed.emit(project)
            if model:
                self.app_state.model_changed.emit(model)
            if results:
                self.app_state.results_changed.emit(results)

            self._update_project_ui()
            RecentProjectsManager.add(filepath)
            if hasattr(self.project_tab, '_load_recent_projects'):
                self.project_tab._load_recent_projects()
            if hasattr(self.project_tab, 'set_status'):
                self.project_tab.set_status("SAVED", filepath)
            self.tab_widget.setTabText(0, "1. Project")
            self._on_status_message(f"Loaded: {filepath}")
        else:
            QMessageBox.warning(self, "Error", f"Failed to load project from {filepath}")

    def _apply_project_template(self, name: str):
        """Apply a project template — currently handled inside ProjectTab."""
        pass

    def _mark_project_modified(self, _=None):
        """Mark the project as modified in the tab label and hero bar."""
        if hasattr(self.project_tab, 'set_status'):
            self.project_tab.set_status("MODIFIED")
        self.tab_widget.setTabText(0, "1. Project ●")

    def _save_project(self):
        """Save the current project."""
        project = self.project_tab.get_project_info()
        filepath = project.filepath

        if not filepath:
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Save Project",
                f"{project.name}.bap",
                "Bolt Analysis Project (*.bap);;All Files (*)"
            )
            if not filepath:
                return

        # Sync project info from UI to app state
        ap = self.app_state._project
        ap.name = project.name
        ap.description = project.description
        ap.author = project.author
        ap.company = project.company
        ap.institution = getattr(project, 'institution', getattr(ap, 'institution', ''))
        ap.project_number = getattr(project, 'project_number', getattr(ap, 'project_number', ''))
        ap.revision = getattr(project, 'revision', getattr(ap, 'revision', 'A'))
        ap.notes = getattr(project, 'notes', getattr(ap, 'notes', ''))
        ap.filepath = filepath

        success = ProjectIO.save_project(
            filepath,
            self.app_state.project,
            self.app_state.model,
            self.app_state.results
        )

        if success:
            self.app_state.mark_clean()
            RecentProjectsManager.add(filepath)
            if hasattr(self.project_tab, '_load_recent_projects'):
                self.project_tab._load_recent_projects()
            if hasattr(self.project_tab, 'set_status'):
                self.project_tab.set_status("SAVED", filepath)
            self.tab_widget.setTabText(0, "1. Project")
            self._on_status_message(f"Saved: {filepath}")
        else:
            QMessageBox.warning(self, "Error", "Failed to save project")

    def _update_project_ui(self):
        """Update project tab UI from app state."""
        project = self.app_state.project
        if hasattr(self.project_tab, 'set_project_info'):
            self.project_tab.set_project_info(project)
        else:
            self.project_tab.name_edit.setText(project.name)
            self.project_tab.description_edit.setPlainText(project.description)
            self.project_tab.author_edit.setText(project.author)
            self.project_tab.company_edit.setText(project.company)

    # =========================================================================
    # MODEL OPERATIONS
    # =========================================================================

    def _load_model(self):
        """Load a model file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load Model",
            "", "MSD Model (*.msd);;Bolt Analysis Project (*.bap);;All Files (*)"
        )
        if filepath:
            model = ProjectIO.load_model(filepath)
            if model:
                self.app_state.model = model
                self._on_status_message(f"Loaded model: {filepath}")

                # Update MSD Builder if open
                if self.msd_builder_window:
                    self.msd_builder_window.load_from_msd_model(model)
            else:
                QMessageBox.warning(self, "Error", f"Failed to load model from {filepath}")

    def _save_model(self):
        """Save the current model."""
        if self.app_state.model is None:
            QMessageBox.warning(self, "No Model", "No model to save. Create or load a model first.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Model",
            "model.msd",
            "MSD Model (*.msd);;All Files (*)"
        )
        if filepath:
            success = ProjectIO.save_model(filepath, self.app_state.model)
            if success:
                self._on_status_message(f"Saved model: {filepath}")
            else:
                QMessageBox.warning(self, "Error", "Failed to save model")

    def _clear_model(self):
        """Clear the current model."""
        reply = QMessageBox.question(
            self, "Clear Model",
            "Are you sure you want to clear the current model?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.app_state.model = None
            if self.msd_builder_window:
                self.msd_builder_window.schematic.clear_all()
            self._on_status_message("Model cleared")

    def _validate_model(self):
        """Validate the current model with comprehensive checks."""
        # Always get a fresh model with loading data from MSD Builder
        if self.msd_builder_window:
            model = self.msd_builder_window.export_to_msd_model()
            if model:
                self.app_state.model = model

        if self.app_state.model is None:
            QMessageBox.warning(self, "No Model", "No model to validate.")
            return

        model = self.app_state.model
        is_valid, messages = model.validate()

        # Also run contact validation if available
        try:
            c_valid, c_msgs = model.validate_contacts()
            if not c_valid:
                is_valid = False
            messages.extend(c_msgs)
        except Exception:
            pass

        # Build categorized report
        errors = [m for m in messages if m.startswith("ERROR")]
        warnings = [m for m in messages if m.startswith("WARNING")]
        ok_msgs = [m for m in messages if m.startswith("OK")]

        report_lines = []
        report_lines.append(
            f"Model: {model.n_elements} elements, {model.n_dof} DOF\n"
        )

        if ok_msgs:
            report_lines.append("--- Passed Checks ---")
            for m in ok_msgs:
                report_lines.append(f"  {m}")
            report_lines.append("")

        if warnings:
            report_lines.append("--- Warnings ---")
            for m in warnings:
                report_lines.append(f"  {m}")
            report_lines.append("")

        if errors:
            report_lines.append("--- Errors ---")
            for m in errors:
                report_lines.append(f"  {m}")
            report_lines.append("")

        report = "\n".join(report_lines)

        if is_valid and not warnings:
            QMessageBox.information(self, "Validation Passed", report)
            self.model_builder_tab.validation_label.setText("Model Valid")
            self.model_builder_tab.validation_label.setStyleSheet(
                f"color: {Theme.GREEN};"
            )
        elif is_valid:
            QMessageBox.warning(
                self, "Validation Passed with Warnings", report
            )
            self.model_builder_tab.validation_label.setText("Valid (warnings)")
            self.model_builder_tab.validation_label.setStyleSheet(
                f"color: {Theme.YELLOW};"
            )
        else:
            QMessageBox.critical(self, "Validation Failed", report)
            self.model_builder_tab.validation_label.setText("Validation failed")
            self.model_builder_tab.validation_label.setStyleSheet(
                f"color: {Theme.RED};"
            )

    # =========================================================================
    # ANALYSIS OPERATIONS
    # =========================================================================

    # ── §5.4 ISO 16130:2015 formal test simulation protocol ───────────
    _ISO16130_AMPLITUDES_MM = {
        # Bolt diameter d [mm] -> transverse displacement amplitude [mm]
        6: 0.30, 8: 0.40, 10: 0.50, 12: 0.60, 14: 0.65, 16: 0.70,
        18: 0.75, 20: 0.80, 22: 0.85, 24: 0.90,
    }

    def _run_iso16130_test(self):
        """Auto-configure ISO 16130:2015 test parameters then run the analysis.

        ISO 16130:2015 specifies:
          * Fixed transverse Junker amplitude by bolt size (table above)
          * 2 000 cycles at 12.5 Hz
          * Sinusoidal waveform; initial preload as configured
        """
        model = self.app_state.model
        if model is None or getattr(model, 'global_loading', None) is None:
            QMessageBox.warning(
                self, "ISO 16130 Test",
                "Build or load an MSD model with global loading first."
            )
            return
        loading = model.global_loading
        d_mm = float(getattr(loading, 'bolt_diameter', 16.0) or 16.0)
        key = min(self._ISO16130_AMPLITUDES_MM.keys(),
                  key=lambda k: abs(k - d_mm))
        amp = self._ISO16130_AMPLITUDES_MM[key]

        # Apply standard parameters
        loading.type = 'transverse'
        loading.delta_amplitude = amp
        loading.frequency = 12.5
        loading.n_cycles = 2000
        try:
            loading.load_waveform = 'sinusoidal'
        except Exception:
            pass

        # Push into SolverTab summary + hidden compatibility spinboxes
        loading_dict = {
            'type': 'transverse',
            'F_preload': float(getattr(loading, 'F_preload', 0.0) or 0.0),
            'F_transverse': float(getattr(loading, 'F_transverse', 0.0) or 0.0),
            'delta_amplitude': amp,
            'frequency': 12.5,
            'n_cycles': 2000,
            'mu_initial': float(getattr(loading, 'mu_initial', 0.12) or 0.12),
            'lubricated': bool(getattr(loading, 'lubricated', True)),
            'bolt_diameter': d_mm,
            'pitch': float(getattr(loading, 'pitch', 2.0) or 2.0),
            'R_factor': 0.0,
        }
        self.solver_tab.update_loading_summary(loading_dict)

        QMessageBox.information(
            self, "ISO 16130 Test",
            f"Configured for M{key} (δ = {amp:.2f} mm, f = 12.5 Hz, N = 2000 cycles)\n"
            f"Starting analysis — when complete, open Reports tab and pick\n"
            f"\"ISO 16130 / DIN 65151 Vibration Test\" to generate the test report."
        )

        # Kick off the standard analysis
        self._run_analysis()

    def _run_analysis(self):
        """Run all configured analyses (static, modal, transient, loosening)."""
        # Guard: require a valid loaded model before running (mirrors the check
        # in _run_iso16130_test) so a friendly warning replaces a raw traceback.
        model = self.app_state.model
        if model is None or getattr(model, 'global_loading', None) is None:
            QMessageBox.warning(
                self, "Run Analysis",
                "Nenhum modelo carregado. Construa ou carregue um modelo no "
                "MSD Builder antes de rodar."
            )
            return

        # Create configuration - all analyses always run
        config = AnalysisConfig(analysis_type="all", run_all=True)

        # Configure coupled loosening analysis based on load type
        n_cycles = self.solver_tab.n_cycles_spin.value()
        load_amplitude = self.solver_tab.amplitude_spin.value()
        load_type_idx = self.solver_tab.load_type_combo.currentIndex()
        # 0: Axial Cyclic, 1: Transverse Cyclic (Junker), 2: Combined, 3: Impulse, 4: Custom

        config.coupled_loosening_config.n_cycles = n_cycles

        # Use yield-computed preload from global_loading (single source of truth)
        if (self.app_state.model
                and self.app_state.model.global_loading
                and self.app_state.model.global_loading.F_preload > 0):
            preload_from_model = self.app_state.model.global_loading.F_preload
        else:
            preload_from_model = load_amplitude
        config.coupled_loosening_config.initial_preload = preload_from_model

        # Set transverse force from model's global_loading (single source of truth)
        load_type_names = {0: "Axial Cyclic", 1: "Transverse (Junker)", 2: "Combined",
                           3: "Impulse/Step", 4: "Custom"}
        load_type_name = load_type_names.get(load_type_idx, "Custom")

        if (self.app_state.model
                and self.app_state.model.global_loading
                and self.app_state.model.global_loading.F_transverse > 0):
            # Use actual transverse force from MSD Builder
            config.coupled_loosening_config.transverse_force = self.app_state.model.global_loading.F_transverse
        else:
            # Fallback: estimate from load type when no explicit transverse force set
            pct_map = {0: 0.02, 1: 0.20, 2: 0.15, 3: 0.10, 4: 0.15}
            config.coupled_loosening_config.transverse_force = preload_from_model * pct_map.get(load_type_idx, 0.15)

        # Use friction and bolt geometry parameters from model (via hidden spinboxes kept in sync)
        config.coupled_loosening_config.mu_initial = self.solver_tab.mu_initial_spin.value()
        config.coupled_loosening_config.use_preset = True
        config.coupled_loosening_config.lubricated = self.solver_tab.lubricated_check.isChecked()
        config.coupled_loosening_config.bolt_diameter_mm = self.solver_tab.bolt_diameter_spin.value()
        config.coupled_loosening_config.pitch_mm = self.solver_tab.pitch_spin.value()

        # Phase F: Locking device slip onset factor from global_loading (set by MSD Builder)
        if (self.app_state.model
                and hasattr(self.app_state.model, 'global_loading')
                and self.app_state.model.global_loading is not None):
            _sof = getattr(self.app_state.model.global_loading, 'slip_onset_factor', 0.46)
            config.coupled_loosening_config.slip_onset_factor = float(_sof)

        # Compute contact stiffnesses from bolt geometry (VDI 2230 / Motosh / Wileman)
        bolt_dia = self.solver_tab.bolt_diameter_spin.value()
        pitch_val = self.solver_tab.pitch_spin.value()
        stiffnesses = compute_contact_stiffnesses(bolt_dia, pitch_val)
        config.coupled_loosening_config.k_bolt = stiffnesses["k_bolt"] * 1e3   # N/mm → N/m
        config.coupled_loosening_config.k_member = stiffnesses["k_members"] * 1e3  # N/mm → N/m

        # Also set preload config loading type
        config.preload_config.loading_type = ["axial", "transverse", "combined", "axial", "axial"][load_type_idx]

        # Sampling parameters for large cycle counts (up to 5 million)
        config.coupled_loosening_config.sample_percentage = self.solver_tab.sample_pct_spin.value()
        config.coupled_loosening_config.target_output_points = self.solver_tab.target_points_spin.value()

        # Calculate sample interval from percentage or target points
        sample_pct = self.solver_tab.sample_pct_spin.value()
        target_pts = self.solver_tab.target_points_spin.value()
        pts_from_pct = max(100, int(n_cycles * sample_pct / 100.0))
        pts_from_target = max(100, target_pts)
        actual_pts = min(pts_from_pct, pts_from_target)
        sample_interval = max(1, n_cycles // actual_pts)
        config.coupled_loosening_config.sample_interval = sample_interval

        # Configure preload analysis (use model preload, not raw spinbox)
        config.preload_config.n_cycles = self.solver_tab.n_cycles_spin.value()
        config.preload_config.initial_preload = preload_from_model
        config.preload_config.frequency = self.solver_tab.frequency_spin.value()

        # Configure time integration
        method_map = {
            0: "newmark", 1: "hht", 2: "central_diff",
            3: "modal", 4: "rk4", 5: "adaptive_rk45"
        }
        config.time_config.method = method_map.get(
            self.solver_tab.method_combo.currentIndex(), "newmark"
        )
        config.time_config.t_end = self.solver_tab.t_end_spin.value()
        config.time_config.dt = self.solver_tab.dt_spin.value()
        config.time_config.load_amplitude = self.solver_tab.amplitude_spin.value()
        config.time_config.load_frequency = self.solver_tab.frequency_spin.value()

        # Convergence and output settings
        config.time_config.force_tolerance = self.solver_tab.force_tol_spin.value()
        config.time_config.displacement_tolerance = self.solver_tab.disp_tol_spin.value()
        config.time_config.max_iterations = self.solver_tab.max_iter_spin.value()
        config.time_config.output_interval = self.solver_tab.output_spin.value()

        # Create and start solver thread
        self.solver_thread = QThread()
        self.solver_worker = SolverWorker()
        self.solver_worker.moveToThread(self.solver_thread)

        # Connect signals
        self.solver_worker.progress.connect(self._on_solver_progress)
        self.solver_worker.log.connect(self._on_solver_log)
        self.solver_worker.finished.connect(self._on_solver_finished)
        self.solver_worker.error.connect(self._on_solver_error)
        self.solver_worker.live_state.connect(self._on_live_state)

        # Start analysis when thread starts
        self.solver_thread.started.connect(
            lambda: self.solver_worker.run_analysis(self.app_state.model, config)
        )

        # Update UI
        self.solver_tab.run_btn.setEnabled(False)
        self.solver_tab.pause_btn.setEnabled(True)
        self.solver_tab.stop_btn.setEnabled(True)
        self.solver_tab.progress_bar.setValue(0)
        self._current_stage_idx = -1
        self.solver_tab.set_analysis_stage(-1)
        self.solver_tab.console_output.append(f"\n--- Starting full analysis suite ---")
        self.solver_tab.console_output.append(f"Load Type: {load_type_name}")
        self.solver_tab.console_output.append(f"Preload: {preload_from_model:,.0f} N | Transverse: {config.coupled_loosening_config.transverse_force:,.0f} N")
        self.solver_tab.console_output.append(f"Cycles: {n_cycles:,} | Sample interval: {sample_interval} | Output points: ~{actual_pts:,}")
        self.solver_tab.console_output.append(
            f"Stiffnesses (VDI/Wileman): k_bolt={stiffnesses['k_bolt']:,.0f} N/mm, "
            f"k_members={stiffnesses['k_members']:,.0f} N/mm, "
            f"k_thread={stiffnesses['k_thread_vdi']:,.0f} N/mm"
        )
        self.analysis_status.setText("Analysis: Running...")

        # Start
        self.solver_thread.start()

    def _pause_analysis(self):
        """Pause/resume the current analysis."""
        if self.solver_worker:
            if self.solver_worker._is_paused:
                self.solver_worker.request_resume()
                self.solver_tab.pause_btn.setText("⏸️ Pause")
                self.analysis_status.setText("Analysis: Running...")
            else:
                self.solver_worker.request_pause()
                self.solver_tab.pause_btn.setText("▶️ Resume")
                self.analysis_status.setText("Analysis: Paused")

    def _stop_analysis(self):
        """Stop the current analysis."""
        if self.solver_worker:
            self.solver_worker.request_stop()
        self._cleanup_solver()

    def _cleanup_solver(self):
        """Clean up solver thread."""
        if self.solver_thread and self.solver_thread.isRunning():
            self.solver_thread.quit()
            self.solver_thread.wait(2000)

        self.solver_tab.run_btn.setEnabled(True)
        self.solver_tab.pause_btn.setEnabled(False)
        self.solver_tab.stop_btn.setEnabled(False)
        self.analysis_status.setText("Analysis: Ready")

    @pyqtSlot(int, str)
    def _on_solver_progress(self, percent: int, message: str):
        """Handle solver progress updates."""
        self.solver_tab.progress_bar.setValue(percent)
        self.solver_tab.status_label.setText(message)
        if percent > 0 and not self.solver_tab.live_group.isVisible():
            self.solver_tab.live_group.setVisible(True)

        # Map progress % → stage index (0=Modal, 1=Static, 2=Preload, 3=Loosening, 4=Integration)
        if percent < 10:
            stage_idx = -1
        elif percent < 20:
            stage_idx = 0
        elif percent < 40:
            stage_idx = 1
        elif percent < 60:
            stage_idx = 2
        elif percent < 80:
            stage_idx = 3
        elif percent < 100:
            stage_idx = 4
        else:
            stage_idx = 5
        self._current_stage_idx = stage_idx
        self.solver_tab.set_analysis_stage(stage_idx)

    @pyqtSlot(dict)
    def _on_live_state(self, state: dict):
        """Update live status dashboard during coupled loosening analysis."""
        st = self.solver_tab
        cycle = state.get("cycle", 0)
        total = state.get("total", 0)
        st.live_cycle_lbl.setText(f"{cycle:,} / {total:,}")
        ratio = state.get("preload_ratio", 1.0)
        st.live_preload_lbl.setText(f"{ratio * 100:.1f}%")
        st.live_mu_thread_lbl.setText(f"{state.get('mu_thread', 0):.4f}")
        st.live_mu_bearing_lbl.setText(f"{state.get('mu_bearing', 0):.4f}")
        st.live_loosening_lbl.setText(f"{state.get('loosening_deg', 0):.2f}°")
        margin = state.get("torque_margin", 1.0)
        color = Theme.GREEN if margin >= 1.0 else Theme.RED
        st.live_margin_lbl.setText(f"{margin:.3f}")
        st.live_margin_lbl.setStyleSheet(
            f"color:{color}; font-size:9pt; font-weight:bold;")

    @pyqtSlot(str)
    def _on_solver_log(self, message: str):
        """Handle solver log messages — color-coded by severity (9.1)."""
        import html as _html
        safe = _html.escape(message)
        if "[ERR]" in message or "ERROR" in message.upper()[:10]:
            colored = f'<span style="color:{Theme.RED};">{safe}</span>'
        elif "[WARN]" in message or "WARNING" in message.upper()[:10]:
            colored = f'<span style="color:{Theme.YELLOW};">{safe}</span>'
        elif "[INFO]" in message:
            colored = f'<span style="color:{Theme.TEXT};">{safe}</span>'
        elif message.startswith("---"):
            colored = f'<span style="color:{Theme.MAUVE}; font-weight:bold;">{safe}</span>'
        elif message.startswith("Friction model") or message.startswith("Bolt") or message.startswith("Preload"):
            colored = f'<span style="color:{Theme.BLUE};">{safe}</span>'
        else:
            colored = f'<span style="color:{Theme.SUBTEXT};">{safe}</span>'
        self.solver_tab.console_output.insertHtml(colored + "<br>")

    @pyqtSlot(object)
    def _on_solver_finished(self, result: AnalysisResult):
        """Handle solver completion."""
        self.app_state.results = result
        self._cleanup_solver()
        self.solver_tab.live_group.setVisible(False)
        self.solver_tab.set_analysis_stage(5)   # all stages green
        self.solver_tab.console_output.insertHtml(
            f'<span style="color:{Theme.GREEN}; font-weight:bold;">--- Analysis complete ---</span><br>')
        self._on_status_message("Analysis completed successfully")

        # Update statistics in results tab
        self._on_results_changed(result)

        # Task 12: Update Solver Tab Miner's D row after analysis
        _cl = getattr(result, 'coupled_loosening_result', None)
        _raw = getattr(_cl, '_raw_loosening_results', None) if _cl else None
        if _raw is not None:
            _d = getattr(_raw, 'miner_damage_final', 0.0)
            _col = (Theme.RED if _d >= 1.0
                    else Theme.YELLOW if _d >= 0.5
                    else Theme.GREEN)
            self.solver_tab.summary_miners.setText(f"{_d:.4f}")
            self.solver_tab.summary_miners.setStyleSheet(
                f"color:{_col}; font-weight:bold;")
        else:
            self.solver_tab.summary_miners.setText("\u2014")
            self.solver_tab.summary_miners.setStyleSheet(
                f"color:{Theme.SUBTEXT};")

        # Switch to results tab (show placeholder, user selects specific plot)
        self.tab_widget.setCurrentIndex(3)
        self.results_tab.plot_stack.setCurrentIndex(0)  # Show placeholder
        self.results_tab.current_plot_type = None

        # Calibration iteration hint: when a reference curve is loaded, prompt
        # the user to iterate via the Calibrate Model dialog.
        if getattr(self, "_reference_curve", None) is not None:
            self.results_tab.calibrate_btn.setText("↺  Iterate Calibration…")
            self.results_tab.calibrate_btn.setStyleSheet(
                f"background-color: {Theme.YELLOW}; "
                f"color: {Theme.BASE}; font-weight: bold;")
            self._on_status_message(
                "Compare with experimental curve · click "
                "↺ Iterate Calibration (Ctrl+K) to refine parameters")
        else:
            # Reset to default look once no reference / new model
            self.results_tab.calibrate_btn.setText("⚙  Calibrate Model…")
            self.results_tab.calibrate_btn.setStyleSheet("")

    @pyqtSlot(str)
    def _on_solver_error(self, error: str):
        """Handle solver errors."""
        # Mark the stage that was running as failed (red)
        failed_stage = getattr(self, '_current_stage_idx', -1)
        self.solver_tab.set_analysis_stage(
            max(failed_stage, 0), error=True
        )
        self._cleanup_solver()
        self.solver_tab.live_group.setVisible(False)
        import html as _html
        self.solver_tab.console_output.insertHtml(
            f'<span style="color:{Theme.RED}; font-weight:bold;">[ERR] {_html.escape(error)}</span><br>')
        QMessageBox.critical(self, "Analysis Error", f"An error occurred:\n\n{error}")

    # =========================================================================
    # RESULTS DISPLAY
    # =========================================================================

    def _on_result_category_selected(self, item, column):
        """Handle result category selection in tree - shows SINGLE plot."""
        if self.app_state.results is None:
            QMessageBox.information(self, "No Results", "Run an analysis first to view plots.")
            return

        text = item.text(0)
        results = self.app_state.results

        # Ignore category headers (they have children)
        if item.childCount() > 0:
            return

        # Store current plot type for refresh
        self.results_tab.current_plot_type = text

        # Switch to Plot View sub-tab and show the canvas
        self.results_tab.right_tabs.setCurrentIndex(2)
        self.results_tab.plot_stack.setCurrentIndex(1)

        # Show Stage Analysis overlay controls only for that plot
        self.results_tab.stage_overlay_widget.setVisible("Stage Analysis" in text)

        # Bug 2 fix: after dashboard, figure has multiple axes — reset to single axes
        canvas = self.results_tab.plot_widget.canvas
        existing_axes = canvas.figure.get_axes()
        if len(existing_axes) != 1:
            canvas.figure.clear()
            canvas.axes = canvas.figure.add_subplot(111)

        # Display appropriate SINGLE plot based on selection
        # =====================================================================
        # PRELOAD DECAY PLOTS
        # =====================================================================
        if "Clamped Force Decay" in text:
            if results.coupled_loosening_result:
                self._plot_coupled_loosening(results.coupled_loosening_result, "preload")
        elif "Preload Loss Models" in text:
            if results.coupled_loosening_result:
                self._plot_preload_models_overlay(results.coupled_loosening_result)
            elif results.preload_result:
                PlotManager.plot_preload_loss(
                    self.results_tab.plot_widget,
                    results.preload_result.cycles,
                    results.preload_result.results
                )
        elif "Stage Analysis" in text:
            if results.coupled_loosening_result:
                overlay_text = self.results_tab.stage_overlay_combo.currentText()
                self._plot_stage_analysis_animated(
                    results.coupled_loosening_result, overlay_text)

        # =====================================================================
        # FRICTION & WEAR PLOTS
        # =====================================================================
        elif "Friction Evolution" in text:
            if results.coupled_loosening_result:
                self._plot_coupled_loosening(results.coupled_loosening_result, "friction")
        elif "Wear Accumulation" in text:
            if results.coupled_loosening_result:
                self._plot_coupled_loosening(results.coupled_loosening_result, "wear")
        elif "Friction-Wear Correlation" in text:
            if results.coupled_loosening_result:
                self._plot_friction_wear_correlation(results.coupled_loosening_result)

        # =====================================================================
        # LOOSENING PLOTS
        # =====================================================================
        elif "Loosening Rate" in text:
            if results.coupled_loosening_result:
                self._plot_coupled_loosening(results.coupled_loosening_result, "loosening")
        elif "Torque Balance" in text:
            if results.coupled_loosening_result:
                self._plot_torque_balance(results.coupled_loosening_result)
        elif "Torque Margin" in text:
            if results.coupled_loosening_result:
                self._plot_coupled_loosening(results.coupled_loosening_result, "torque")
        elif "Cumulative Angle" in text:
            if results.coupled_loosening_result:
                self._plot_cumulative_angle(results.coupled_loosening_result)
        elif "Mechanism Decomposition" in text:
            self._plot_mechanism_decomposition(results)

        # =====================================================================
        # JOINT FORCES PLOTS
        # =====================================================================
        elif "VDI Joint Diagram" in text:
            self._plot_vdi_joint_diagram(results)
        elif "Joint Forces Diagram" in text:
            if results.coupled_loosening_result:
                self._plot_joint_forces(results.coupled_loosening_result)
        elif "Contact Forces" in text:
            if results.coupled_loosening_result:
                self._plot_contact_forces(results.coupled_loosening_result)
        elif "Phase Diagram" in text:
            if results.coupled_loosening_result:
                self._plot_phase_diagram(results.coupled_loosening_result)

        # =====================================================================
        # TIME HISTORY PLOTS
        # =====================================================================
        elif text == "Displacement":
            if results.time_result and results.time_result.displacement is not None:
                PlotManager.plot_displacement(
                    self.results_tab.plot_widget,
                    results.time_result.time,
                    results.time_result.displacement
                )
            else:
                self._plot_excitation_proxy("Displacement", "m")
        elif text == "Velocity":
            if results.time_result and results.time_result.velocity is not None:
                PlotManager.plot_velocity(
                    self.results_tab.plot_widget,
                    results.time_result.time,
                    results.time_result.velocity
                )
            else:
                self._plot_excitation_proxy("Velocity", "m/s")
        elif text == "Acceleration":
            if results.time_result and results.time_result.acceleration is not None:
                PlotManager.plot_acceleration(
                    self.results_tab.plot_widget,
                    results.time_result.time,
                    results.time_result.acceleration
                )
            else:
                self._plot_excitation_proxy("Acceleration", "m/s²")
        elif text == "Preload vs Time":
            # _plot_preload_vs_time handles both time_result and coupled_loosening_result
            self._plot_preload_vs_time(results)

        # =====================================================================
        # MODAL ANALYSIS PLOTS
        # =====================================================================
        elif text == "Mode Shapes":
            if results.natural_frequencies:
                self._plot_mode_shapes(results)
            else:
                self._plot_no_data("Mode Shapes",
                                   "No modal data available.\nRun a Modal Analysis first.")
        elif text == "Campbell Diagram":
            if results.natural_frequencies:
                self._plot_campbell_diagram(results)
            else:
                self._plot_no_data("Campbell Diagram",
                                   "No modal data available.\nRun a Modal Analysis first.")

    # =========================================================================
    # SPECIALIZED PLOT METHODS
    # =========================================================================

    def _plot_friction_wear_correlation(self, cl: CoupledLooseningResult):
        """Plot friction vs wear correlation."""
        import numpy as np
        canvas = self.results_tab.plot_widget.canvas
        ax = canvas.axes
        ax.clear()

        MAUVE = Theme.MAUVE
        PEACH = Theme.PEACH
        YELLOW = Theme.YELLOW
        TEXT = Theme.TEXT

        if cl.mu_thread is not None and cl.total_wear_um is not None:
            mu = np.array(cl.mu_thread)
            wear = np.array(cl.total_wear_um)
            cycles = cl.cycles

            scatter = ax.scatter(wear, mu, c=cycles, cmap='viridis', s=30, alpha=0.7)
            cbar = canvas.figure.colorbar(scatter, ax=ax)
            cbar.set_label('Cycles', color=TEXT)
            cbar.ax.tick_params(colors=TEXT)

            # Fit line
            if len(wear) > 2 and np.std(wear) > 0:
                z = np.polyfit(wear, mu, 1)
                p = np.poly1d(z)
                ax.plot(wear, p(wear), '--', color=YELLOW, linewidth=2, label=f'Slope: {z[0]:.4f}')
                ax.legend()

        ax.set_xlabel('Wear Depth (μm)')
        ax.set_ylabel('Friction Coefficient (mu)')
        ax.set_title('Friction vs Wear Correlation\n(Lower mu with increasing wear)')
        ax.grid(True, alpha=0.3)
        canvas._apply_theme()
        canvas.draw()

    def _plot_torque_balance(self, cl: CoupledLooseningResult):
        """Plot torque balance (T_pitch vs T_resistance)."""
        import numpy as np
        canvas = self.results_tab.plot_widget.canvas
        ax = canvas.axes
        ax.clear()

        RED = Theme.RED
        GREEN = Theme.GREEN
        BLUE = Theme.BLUE
        TEAL = Theme.TEAL

        if cl.states and len(cl.states) > 0:
            cycles = np.array([s.cycle for s in cl.states])
            T_pitch = np.array([s.T_pitch for s in cl.states])
            T_res = np.array([s.T_resistance for s in cl.states])
            T_thread = np.array([s.T_thread for s in cl.states])
            T_bearing = np.array([s.T_bearing for s in cl.states])

            ax.plot(cycles, T_pitch, color=RED, linewidth=2, label='T_pitch (drives)')
            ax.plot(cycles, T_res, color=GREEN, linewidth=2, label='T_resistance (resists)')
            ax.plot(cycles, T_thread, color=BLUE, linewidth=1.5, linestyle='--', label='T_thread')
            ax.plot(cycles, T_bearing, color=TEAL, linewidth=1.5, linestyle='--', label='T_bearing')

            ax.fill_between(cycles, T_pitch, T_res, where=T_res >= T_pitch, alpha=0.2, color=GREEN)
            ax.fill_between(cycles, T_pitch, T_res, where=T_res < T_pitch, alpha=0.2, color=RED)
            ax.legend(loc='upper right')
        elif cl.torque_margin is not None:
            # Fallback: show torque margin
            ax.plot(cl.cycles, cl.torque_margin, color=BLUE, linewidth=2, label='Torque Margin')
            ax.axhline(y=1.0, color=RED, linestyle='-', linewidth=2, label='Loosening threshold')
            ax.fill_between(cl.cycles, 1.0, cl.torque_margin,
                           where=np.array(cl.torque_margin) >= 1.0, alpha=0.2, color=GREEN)
            ax.fill_between(cl.cycles, 1.0, cl.torque_margin,
                           where=np.array(cl.torque_margin) < 1.0, alpha=0.2, color=RED)
            ax.legend()
            ax.set_ylabel('Torque Margin')
            ax.set_title('Torque Margin Evolution\n(Loosening when margin < 1.0)')
            ax.grid(True, alpha=0.3)
            canvas._apply_theme()
            canvas.draw()
            return

        ax.set_xlabel('Number of Cycles (N)')
        ax.set_ylabel('Torque (N.m)')
        ax.set_title('Torque Balance\n(Loosening when T_pitch > T_resistance)')
        ax.grid(True, alpha=0.3)
        canvas._apply_theme()
        canvas.draw()

    def _plot_cumulative_angle(self, cl: CoupledLooseningResult):
        """Plot cumulative loosening angle."""
        import numpy as np
        canvas = self.results_tab.plot_widget.canvas
        ax = canvas.axes
        ax.clear()

        PEACH = Theme.PEACH
        GREEN = Theme.GREEN
        BLUE = Theme.BLUE
        YELLOW = Theme.YELLOW
        RED = Theme.RED

        if cl.loosening_angle_deg is not None:
            ax.plot(cl.cycles, cl.loosening_angle_deg, color=PEACH, linewidth=2)
            ax.fill_between(cl.cycles, 0, cl.loosening_angle_deg, alpha=0.3, color=PEACH)

            # Add phase regions if states are available
            if cl.states and len(cl.states) > 1:
                phase_colors = {'stable': GREEN, 'non_rotational': BLUE, 'transition': YELLOW,
                               'rotational': PEACH, 'runaway': RED}
                for i, s in enumerate(cl.states[:-1]):
                    c1, c2 = s.cycle, cl.states[i+1].cycle
                    phase_val = s.phase.value if hasattr(s.phase, 'value') else str(s.phase)
                    phase_color = phase_colors.get(phase_val, Theme.SURFACE0)
                    ax.axvspan(c1, c2, alpha=0.15, color=phase_color)

        ax.set_xlabel('Number of Cycles (N)')
        ax.set_ylabel('Cumulative Loosening (deg)')
        ax.set_title(f'Cumulative Loosening Angle\nTotal: {cl.total_loosening_deg:.3f} deg')
        ax.grid(True, alpha=0.3)
        canvas._apply_theme()
        canvas.draw()

    def _plot_mechanism_decomposition(self, results):
        """V2 preload-loss decomposition: stacked cumulative loss by mechanism.

        Answers "where did the preload go": embedding / creep / wear /
        rotational loosening. The stack total equals the measured loss
        F0*(1-ratio), so this is the V2 preload curve broken down by the *same*
        model that produced it (coherence). Empty unless a Run populated the V2
        decomposition (set by SolverWorker's V2 override).
        """
        import numpy as np
        cl = getattr(results, 'coupled_loosening_result', None)
        decomp = getattr(cl, '_v2_mech_decomp', None) if cl is not None else None
        canvas = self.results_tab.plot_widget.canvas
        ax = canvas.axes
        ax.clear()

        if not decomp:
            ax.text(0.5, 0.5,
                    "No V2 decomposition available.\nRun an analysis first.",
                    ha='center', va='center', transform=ax.transAxes,
                    color=Theme.SUBTEXT)
            ax.set_title('Preload-Loss Decomposition by Mechanism (V2)')
            canvas._apply_theme()
            canvas.draw()
            return

        cyc = np.asarray(decomp['cycles'], dtype=float)
        layers = [
            ("Embedding", decomp['embedding'], Theme.TEAL),
            ("Creep", decomp['creep'], Theme.YELLOW),
            ("Wear", decomp['wear'], Theme.SKY),
            ("Loosening", decomp['rotational_loosening'], Theme.PEACH),
        ]
        ys = [np.asarray(v, dtype=float) for _, v, _ in layers]
        ax.stackplot(cyc, *ys, labels=[n for n, _, _ in layers],
                     colors=[c for _, _, c in layers], alpha=0.85)

        total = decomp.get('total_kN')
        if total is not None:
            ax.plot(cyc, np.asarray(total, dtype=float), color=Theme.TEXT,
                    lw=1.5, ls='--', label='Total loss')

        ax.set_xlabel('Number of Cycles (N)')
        ax.set_ylabel('Cumulative preload loss (kN)')
        ax.set_title('Preload-Loss Decomposition by Mechanism (V2)\n'
                     f'Total lost: {sum(float(y[-1]) for y in ys):.2f} kN')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
        canvas._apply_theme()
        canvas.draw()

    def _plot_vdi_joint_diagram(self, results):
        """VDI 2230 Bolted Joint Force-Extension Diagram (Verspannungsschaubild).

        Draws the classic two-line joint diagram:
          - Bolt line  (slope = +k_b, left side, extension)
          - Member line (slope = -k_m, right side, compression)
          - Preload point F_V
          - Load triangle under external force F_A
          - Separation limit
          - Results table with all VDI 2230 quantities

        Parameters are read from the current MSD model (global_loading +
        bolt geometry) and from the coupled loosening result when available.
        """
        import numpy as np
        from matplotlib.gridspec import GridSpec
        from matplotlib.patches import FancyArrowPatch

        canvas = self.results_tab.plot_widget.canvas
        fig = canvas.figure
        fig.clear()

        # ── Extract parameters from model ───────────────────────────────
        model = self.app_state.model  # MSDModel (may be None if not loaded)

        # Bolt geometry
        d_mm  = getattr(model, 'bolt_diameter', 16.0) if model else 16.0
        p_mm  = getattr(model, 'pitch',          2.0) if model else 2.0
        E_b   = 205_000.0    # MPa (steel default)
        Sy    = 720.0        # MPa (Grade 8.8 default)
        L_mm  = 3.0 * d_mm   # grip length estimate

        # Try to extract better values from model elements
        if model and hasattr(model, 'elements'):
            for elem in model.elements:
                if hasattr(elem, 'type') and str(elem.type).upper() in ("SHANK", "THREAD"):
                    if hasattr(elem, 'material'):
                        E_b  = elem.material.E  or E_b
                        Sy   = elem.material.Sy or Sy
                    if hasattr(elem, 'geometry') and elem.geometry.length > 0:
                        L_mm = elem.geometry.length

        # Compute stiffnesses (N/mm from compute_contact_stiffnesses)
        try:
            stiff = compute_contact_stiffnesses(d_mm, p_mm, E_b, Sy, L_mm)
            k_b = stiff["k_bolt"]        # N/mm
            k_m = stiff["k_members"]     # N/mm
            A_s = stiff["A_s"]           # mm²
        except Exception:
            k_b = 200_000.0
            k_m = 1_000_000.0
            A_s = 157.0

        # Clamp to sensible ranges
        k_b = max(k_b, 1.0)
        k_m = max(k_m, 1.0)

        # Preload F_V (N)
        F_V = 50_000.0
        if model and hasattr(model, 'global_loading'):
            F_V = model.global_loading.F_preload or F_V
        cl  = getattr(results, 'coupled_loosening_result', None)
        if cl and hasattr(cl, 'initial_preload') and cl.initial_preload:
            F_V = cl.initial_preload

        # External force F_A (N) — use transverse amplitude converted, or F_external
        F_A = 0.0
        if model and hasattr(model, 'global_loading'):
            gl  = model.global_loading
            F_A = getattr(gl, 'F_transverse', 0.0) or getattr(gl, 'F_external', 0.0)
            if F_A == 0.0 and hasattr(gl, 'delta_amplitude') and gl.delta_amplitude:
                # Convert transverse displacement to equivalent axial: F ≈ k_m * δ
                F_A = min(k_m * gl.delta_amplitude * 1e-3 * 0.3, 0.4 * F_V)

        # Clamp F_A to [0, 0.6 * F_sep] so diagram is meaningful
        Phi  = k_b / (k_b + k_m)          # load factor (dimensionless)
        F_sep = F_V / (1 - Phi) if Phi < 1 else 1e9
        F_A  = min(max(F_A, 0.0), 0.55 * F_sep)

        # If no external force, show F_A = 40% of F_sep for illustration
        if F_A == 0.0:
            F_A = 0.40 * F_sep

        # ── Derived VDI quantities ──────────────────────────────────────
        Phi_n      = Phi                       # n=1 (concentric load at interface)
        F_B        = F_V + Phi * F_A           # bolt force under F_A
        F_clamp    = F_V - (1 - Phi) * F_A    # clamp force under F_A
        S_sep      = F_V / ((1 - Phi) * F_A) if F_A > 0 else float('inf')
        S_y        = Sy * A_s / F_B if F_B > 0 else float('inf')
        sigma_a    = Phi * F_A / (2 * A_s) if A_s > 0 else 0.0   # MPa

        # Embedding / preload loss from CL result
        if cl and hasattr(cl, 'final_preload_ratio') and cl.final_preload_ratio:
            F_V_final = cl.final_preload_ratio * F_V
            F_Z       = F_V - F_V_final
        else:
            F_Z = 0.0
            F_V_final = F_V

        # ── Layout: left = diagram, right = results table ───────────────
        gs = GridSpec(1, 2, figure=fig, width_ratios=[3, 2],
                      left=0.06, right=0.98, top=0.92, bottom=0.10, wspace=0.06)
        ax   = fig.add_subplot(gs[0])
        ax_t = fig.add_subplot(gs[1])

        BASE    = Theme.BASE
        TEXT    = Theme.TEXT
        BLUE    = Theme.BLUE
        GREEN   = Theme.GREEN
        YELLOW  = Theme.YELLOW
        RED     = Theme.RED
        PEACH   = Theme.PEACH
        SUBTEXT = Theme.SUBTEXT
        SURF0   = Theme.SURFACE0

        fig.set_facecolor(BASE)
        ax.set_facecolor(BASE)

        # ── Diagram geometry ─────────────────────────────────────────────
        # X-axis: deflection in mm.
        # Bolt line: from origin upward to the right at slope k_b
        #   δ_b = F / k_b   →   x_b = -δ_b  (bolt extends to the LEFT)
        # Member line: from origin upward to the LEFT at slope k_m
        #   δ_m = F / k_m   →   x_m = +δ_m  (member compresses to the RIGHT)
        # Origin at x=0, F=0.  Preload point at x=0, F=F_V is their intersection after assembly.

        # Axes: shared F-axis (vertical), δ horizontal (left = bolt extension, right = member compression)
        delta_b_V  = F_V / k_b    # preload extension of bolt (mm)
        delta_m_V  = F_V / k_m    # preload compression of member (mm)
        delta_b_FA = Phi * F_A / k_b    # additional bolt extension
        delta_m_FA = (1 - Phi) * F_A / k_m  # member decompression

        # x range: bolt side negative (left), member side positive (right)
        x_max = max(delta_m_V * 1.35, delta_m_FA * 2, 0.02)
        x_min = -max(delta_b_V * 1.35, delta_b_FA * 2, 0.02)
        F_max = F_B * 1.20

        # ── Draw bolt line (left side, slope = k_b) ──
        #   Preload state: from (0,0) to (-delta_b_V, F_V)
        x_bolt_base = np.array([0.0, -delta_b_V])
        y_bolt_base = np.array([0.0,  F_V])
        ax.plot(x_bolt_base / 1000, y_bolt_base / 1000, color=BLUE, linewidth=2.0, zorder=3,
                label=f"Bolt  k_b = {k_b:,.0f} N/mm")

        # Extend bolt line to show F_B operating point
        x_bolt_op = np.array([0.0, -(delta_b_V + delta_b_FA)])
        y_bolt_op = np.array([0.0,   F_B])
        ax.plot(x_bolt_op / 1000, y_bolt_op / 1000, color=BLUE, linewidth=2.0,
                linestyle='--', alpha=0.7, zorder=3)

        # ── Draw member line (right side, slope = k_m) ──
        x_memb_base = np.array([0.0, delta_m_V])
        y_memb_base = np.array([0.0, F_V])
        ax.plot(x_memb_base / 1000, y_memb_base / 1000, color=GREEN, linewidth=2.0, zorder=3,
                label=f"Member  k_m = {k_m:,.0f} N/mm")

        # ── Preload horizontal line ──
        ax.axhline(F_V / 1000, color=PEACH, linewidth=1.0, linestyle=':', alpha=0.6, zorder=2)
        ax.text(x_max * 0.95 / 1000, F_V / 1000 * 1.01,
                f"F_V = {F_V/1000:.1f} kN", color=PEACH, fontsize=7, ha='right', va='bottom')

        # ── Load line at operating point (slope = -k_m, through preload point) ──
        # Connects bolt operating point to clamp operating point
        x_ll_bolt   = -(delta_b_V + delta_b_FA)
        x_ll_member = delta_m_V - delta_m_FA
        y_ll_0      = F_B
        y_ll_1      = F_clamp
        ax.plot([x_ll_bolt / 1000, x_ll_member / 1000],
                [y_ll_0 / 1000,    y_ll_1 / 1000],
                color=YELLOW, linewidth=1.5, linestyle='-.', alpha=0.9, zorder=4,
                label=f"Load line (F_A = {F_A/1000:.1f} kN)")

        # ── Load triangle fill ──
        tri_x = [x_ll_bolt / 1000, x_ll_member / 1000, -delta_b_V / 1000, x_ll_bolt / 1000]
        tri_y = [F_B / 1000,       F_clamp / 1000,       F_V / 1000,       F_B / 1000]
        ax.fill(tri_x, tri_y, alpha=0.12, color=YELLOW, zorder=2)

        # ── Key points ──
        # Preload point (intersection of bolt & member lines at assembly)
        ax.plot(0, F_V / 1000, 'o', color=PEACH, markersize=8, zorder=5)
        ax.annotate(f"  F_V = {F_V/1000:.1f} kN",
                    xy=(0, F_V / 1000), fontsize=7, color=PEACH, va='center')

        # Bolt operating point
        ax.plot(x_ll_bolt / 1000, F_B / 1000, 's', color=BLUE, markersize=7, zorder=5)
        ax.annotate(f" F_B = {F_B/1000:.1f} kN",
                    xy=(x_ll_bolt / 1000, F_B / 1000), fontsize=7, color=BLUE,
                    va='bottom', ha='right')

        # Clamp operating point
        ax.plot(x_ll_member / 1000, F_clamp / 1000, 's', color=GREEN, markersize=7, zorder=5)
        ax.annotate(f"F_c = {F_clamp/1000:.1f} kN  ",
                    xy=(x_ll_member / 1000, F_clamp / 1000), fontsize=7, color=GREEN,
                    va='top', ha='right')

        # Separation limit line
        ax.axhline(0.0, color=RED, linewidth=0.8, linestyle=':', alpha=0.7, zorder=2)
        ax.axvline(0.0, color=SUBTEXT, linewidth=0.5, alpha=0.4, zorder=1)

        # Origin label
        ax.text(0.002, -0.003, "O", color=SUBTEXT, fontsize=8,
                transform=ax.transAxes, va='bottom', ha='left')

        # ── Axis formatting ──
        ax.set_xlabel("Deflection  δ (mm) — ← Bolt extension  |  Member compression →",
                      color=TEXT, fontsize=8)
        ax.set_ylabel("Force  F  (kN)", color=TEXT, fontsize=8)
        ax.set_title("VDI 2230 — Bolted Joint Diagram (Verspannungsschaubild)",
                     color=TEXT, fontsize=9, fontweight='bold')
        ax.tick_params(labelsize=7, colors=TEXT)
        ax.spines[:].set_color(SURF0)
        for sp in ax.spines.values():
            sp.set_color(SUBTEXT)
        ax.set_xlim(x_min / 1000 * 1.3, x_max / 1000 * 1.3)
        ax.set_ylim(-F_max / 1000 * 0.05, F_max / 1000)
        ax.legend(fontsize=7, loc='upper right',
                  facecolor=BASE, edgecolor=SUBTEXT, labelcolor=TEXT)
        ax.grid(True, alpha=0.15, color=SURF0)

        # Left/right axis labels
        ax.text(0.05, 0.98, "BOLT\n(tension)",
                transform=ax.transAxes, fontsize=8, color=BLUE,
                va='top', ha='left', alpha=0.7)
        ax.text(0.95, 0.98, "MEMBER\n(compression)",
                transform=ax.transAxes, fontsize=8, color=GREEN,
                va='top', ha='right', alpha=0.7)

        # ── Results table (right panel) ──────────────────────────────────
        ax_t.set_facecolor(BASE)
        ax_t.axis('off')

        # VDI label
        ax_t.text(0.5, 0.98, "VDI 2230 Results Table",
                  transform=ax_t.transAxes, fontsize=9, fontweight='bold',
                  color=TEXT, ha='center', va='top')

        def _safe_s(val, fmt=".3g", unit=""):
            if val == float('inf') or val != val:
                return "∞"
            try:
                s = format(val, fmt)
                return f"{s} {unit}".strip()
            except Exception:
                return str(val)

        rows = [
            # (label, value, unit, color, bold)
            ("GEOMETRY", "", "", SUBTEXT, True),
            ("Bolt diameter d",         f"{d_mm:.1f}",        "mm",   TEXT, False),
            ("Thread pitch p",           f"{p_mm:.2f}",        "mm",   TEXT, False),
            ("Grip length L",            f"{L_mm:.1f}",        "mm",   TEXT, False),
            ("Stress area A_s",          f"{A_s:.1f}",         "mm²",  TEXT, False),
            ("", "", "", TEXT, False),
            ("STIFFNESS", "", "", SUBTEXT, True),
            ("Bolt stiffness  k_b",      f"{k_b:,.0f}",        "N/mm", BLUE, False),
            ("Member stiffness  k_m",    f"{k_m:,.0f}",        "N/mm", GREEN, False),
            ("Stiffness ratio k_m/k_b",  f"{k_m/k_b:.2f}",    "–",    TEXT, False),
            ("Load factor  Φ",           f"{Phi:.4f}",         "–",    PEACH, False),
            ("", "", "", TEXT, False),
            ("FORCES", "", "", SUBTEXT, True),
            ("Preload  F_V",             f"{F_V/1000:.2f}",    "kN",   PEACH, False),
            ("External force  F_A",      f"{F_A/1000:.2f}",    "kN",   YELLOW, False),
            ("Bolt force  F_B",          f"{F_B/1000:.2f}",    "kN",   BLUE, False),
            ("Clamp force  F_clamp",     f"{F_clamp/1000:.2f}","kN",   GREEN, False),
            ("Separation force  F_sep",  f"{F_sep/1000:.2f}",  "kN",   RED, False),
            ("", "", "", TEXT, False),
            ("SAFETY FACTORS", "", "", SUBTEXT, True),
            ("S_sep (≥ 1.2)",  _safe_s(S_sep, ".2f"),
             "✓" if S_sep >= 1.2 else "✗",
             GREEN if S_sep >= 1.2 else RED, False),
            ("S_yield (≥ 1.1)", _safe_s(S_y, ".2f"),
             "✓" if S_y >= 1.1 else "✗",
             GREEN if S_y >= 1.1 else RED, False),
            ("Fatigue amp. σ_a", f"{sigma_a:.1f}", "MPa", TEXT, False),
        ]

        if F_Z > 0:
            rows.append(("", "", "", TEXT, False))
            rows.append(("ANALYSIS", "", "", SUBTEXT, True))
            rows.append(("Embedding loss  F_Z",  f"{F_Z/1000:.2f}", "kN", PEACH, False))
            rows.append(("Residual preload", f"{F_V_final/1000:.2f}", "kN", PEACH, False))

        n_rows = len(rows)
        y_start = 0.93
        row_h   = 0.87 / max(n_rows, 1)

        for i, (label, value, unit, color, bold) in enumerate(rows):
            y = y_start - i * row_h
            if not label:
                continue   # blank separator
            fw = 'bold' if bold else 'normal'
            if bold:
                # section header
                ax_t.text(0.02, y, label, transform=ax_t.transAxes,
                          fontsize=7, fontweight=fw, color=color, va='top')
            else:
                ax_t.text(0.02, y, label + ":", transform=ax_t.transAxes,
                          fontsize=7, color=SUBTEXT, va='top')
                ax_t.text(0.60, y, value, transform=ax_t.transAxes,
                          fontsize=7, fontweight='bold', color=color, va='top',
                          fontfamily='monospace')
                ax_t.text(0.82, y, unit, transform=ax_t.transAxes,
                          fontsize=7, color=SUBTEXT, va='top')

        # Thin divider line
        from matplotlib.lines import Line2D
        ax_t.add_artist(Line2D([0, 0], [0, 1], transform=ax_t.transAxes,
                               color=SUBTEXT, linewidth=0.5, alpha=0.5))

        canvas.draw()
        self.results_tab.plot_stack.setCurrentIndex(1)

    def _plot_joint_forces(self, cl: CoupledLooseningResult):
        """Plot joint forces diagram showing force distribution."""
        import numpy as np
        canvas = self.results_tab.plot_widget.canvas
        ax = canvas.axes
        ax.clear()

        BLUE = Theme.BLUE
        PEACH = Theme.PEACH
        TEXT = Theme.TEXT

        components = ['Bolt Head', 'Washer', 'Flange 1', 'Gasket', 'Flange 2', 'Washer', 'Nut']
        y_pos = np.arange(len(components))

        F_initial = cl.initial_preload / 1000 if hasattr(cl, 'initial_preload') and cl.initial_preload else 50
        F_final = cl.final_preload_ratio * F_initial

        forces_initial = np.array([F_initial] * len(components))
        forces_final = np.array([F_final] * len(components))

        ax.barh(y_pos - 0.2, forces_initial, 0.4, color=BLUE, alpha=0.7, label='Initial Preload')
        ax.barh(y_pos + 0.2, forces_final, 0.4, color=PEACH, alpha=0.7, label='Final Preload')

        ax.set_yticks(y_pos)
        ax.set_yticklabels(components)
        ax.legend(loc='lower right')
        ax.set_xlabel('Force (kN)')
        ax.set_title('Joint Force Distribution\n(Axial force through each component)')
        ax.grid(True, alpha=0.3, axis='x')
        canvas._apply_theme()
        canvas.draw()

    def _plot_contact_forces(self, cl: CoupledLooseningResult):
        """Plot contact forces time history."""
        import numpy as np
        canvas = self.results_tab.plot_widget.canvas
        ax = canvas.axes
        ax.clear()

        BLUE = Theme.BLUE
        GREEN = Theme.GREEN
        MAUVE = Theme.MAUVE
        TEAL = Theme.TEAL

        if cl.preload is not None:
            preload = np.array(cl.preload) if hasattr(cl.preload, '__iter__') else np.array(cl.preload_ratio) * cl.initial_preload

            # Thread contact carries full preload (axial)
            ax.plot(cl.cycles, preload / 1000, color=BLUE, linewidth=2, label='Thread Contact (axial)')

            # Bearing contact experiences friction-reduced normal force
            mu_b = np.array(cl.mu_bearing) if hasattr(cl, 'mu_bearing') and cl.mu_bearing is not None else None
            if mu_b is not None and len(mu_b) == len(preload):
                bearing_tangential = mu_b * preload / 1000
                ax.plot(cl.cycles, bearing_tangential, color=MAUVE, linewidth=2, linestyle='--', label='Bearing Friction Force')
            else:
                # Estimate: bearing friction ~12% of preload
                ax.plot(cl.cycles, 0.12 * preload / 1000, color=MAUVE, linewidth=2, linestyle='--', label='Bearing Friction (est.)')

            # Thread friction force (resists loosening)
            mu_t = np.array(cl.mu_thread) if hasattr(cl, 'mu_thread') and cl.mu_thread is not None else None
            if mu_t is not None and len(mu_t) == len(preload):
                thread_friction = mu_t * preload / 1000
                ax.plot(cl.cycles, thread_friction, color=GREEN, linewidth=1.5, linestyle=':', label='Thread Friction Force')
            else:
                ax.plot(cl.cycles, 0.12 * preload / 1000, color=GREEN, linewidth=1.5, linestyle=':', label='Thread Friction (est.)')

        ax.set_xlabel('Number of Cycles (N)')
        ax.set_ylabel('Contact Force (kN)')
        ax.set_title('Contact Forces vs Cycles')
        ax.legend()
        ax.grid(True, alpha=0.3)
        canvas._apply_theme()
        canvas.draw()

    def _plot_phase_diagram(self, cl: CoupledLooseningResult):
        """Plot loosening phase classification over cycles."""
        import numpy as np
        from matplotlib.patches import Patch

        canvas = self.results_tab.plot_widget.canvas
        ax = canvas.axes
        ax.clear()

        GREEN = Theme.GREEN
        BLUE = Theme.BLUE
        YELLOW = Theme.YELLOW
        PEACH = Theme.PEACH
        RED = Theme.RED
        TEXT = Theme.TEXT

        phase_map = {
            'stable': (0, GREEN, 'Stable'),
            'non_rotational': (1, BLUE, 'Non-rotational'),
            'transition': (2, YELLOW, 'Transition'),
            'rotational': (3, PEACH, 'Rotational'),
            'runaway': (4, RED, 'Runaway')
        }

        if cl.states and len(cl.states) > 1:
            # Draw phase regions
            for i, s in enumerate(cl.states[:-1]):
                c1, c2 = s.cycle, cl.states[i+1].cycle
                phase_val = s.phase.value if hasattr(s.phase, 'value') else str(s.phase)
                phase_info = phase_map.get(phase_val, (0, Theme.SURFACE0, 'Unknown'))
                ax.axvspan(c1, c2, alpha=0.6, color=phase_info[1])

            # Legend for phases
            legend_elements = [Patch(facecolor=v[1], alpha=0.6, label=v[2]) for v in phase_map.values()]
            ax.legend(handles=legend_elements, loc='lower left', fontsize=8)
        else:
            # No state data - show based on phase_at_end
            phase_info = phase_map.get(cl.phase_at_end, (0, Theme.SURFACE0, 'Unknown'))
            ax.axvspan(0, cl.n_cycles if cl.n_cycles > 0 else 1000, alpha=0.6, color=phase_info[1])
            ax.text(0.5, 0.5, f'Phase: {cl.phase_at_end}', transform=ax.transAxes,
                   ha='center', va='center', fontsize=12, color=TEXT)

        # Overlay preload curve
        if cl.preload_ratio is not None:
            ax2 = ax.twinx()
            ax2.plot(cl.cycles, np.array(cl.preload_ratio) * 100, color=TEXT, linewidth=2, label='Preload %')
            ax2.set_ylabel('Preload Retention (%)', color=TEXT)
            ax2.set_ylim([0, 105])

        ax.set_xlabel('Number of Cycles (N)')
        ax.set_title('Loosening Phase Classification')
        ax.set_yticks([])
        canvas._apply_theme()
        canvas.draw()

    # ------------------------------------------------------------------
    def _plot_preload_models_overlay(self, cl: CoupledLooseningResult):
        """
        Fit multiple analytical preload-loss models to the simulated decay
        curve and overlay them.  Each fit's RMSE and R² are shown in the
        legend so the user can see which model best describes the data.
        """
        import numpy as np
        canvas = self.results_tab.plot_widget.canvas
        ax = canvas.axes
        ax.clear()

        cycles = np.asarray(cl.cycles, dtype=float)
        actual = np.asarray(cl.preload_ratio, dtype=float)

        # ── analytical model functions (return F/F₀ ∈ [0,1]) ─────────────
        def _exp(N, lam, F_inf):
            return F_inf + (1.0 - F_inf) * np.exp(-lam * N)

        def _power(N, alpha, Nc):
            return np.power(1.0 + N / np.maximum(Nc, 1.0), -alpha)

        def _log(N, k, F_res):
            return np.maximum(F_res, 1.0 - k * np.log1p(N))

        def _jiang(N, N_t, dF1, k2):
            r = np.where(
                N <= N_t,
                1.0 - dF1 * (1.0 - np.exp(-3.0 * N / np.maximum(N_t, 1.0))),
                (1.0 - dF1) - k2 * (N - N_t),
            )
            return np.clip(r, 0.02, 1.0)

        specs = [
            ("Single Exponential", _exp,   [1e-3, 0.70],        ([0, 0],    [1, 1])),
            ("Power Law",          _power, [0.10, 100.0],       ([0, 0.1],  [2, 1e7])),
            ("Logarithmic",        _log,   [0.05, 0.50],        ([0, 0],    [1, 1])),
            ("Jiang 2-Stage",      _jiang, [200., 0.15, 1e-5],
             ([1, 0, 0], [float(len(cycles)), 0.5, 0.01])),
        ]
        fit_colors = [Theme.BLUE, Theme.GREEN, Theme.YELLOW, Theme.MAUVE]

        # ── plot actual simulation data ────────────────────────────────────
        ax.plot(cycles, actual * 100.0, color=Theme.TEXT, linewidth=2.5,
                zorder=10, label="Simulated (BAS)")

        # ── fit each model and overlay ─────────────────────────────────────
        try:
            from scipy.optimize import curve_fit
            _have_scipy = True
        except ImportError:
            _have_scipy = False

        for (name, func, p0, bounds), color in zip(specs, fit_colors):
            try:
                if _have_scipy:
                    popt, _ = curve_fit(func, cycles, actual, p0=p0,
                                        bounds=bounds, maxfev=10000, method='trf')
                    fitted = func(cycles, *popt)
                else:
                    fitted = func(cycles, *p0)          # no fitting — just evaluate

                res = fitted - actual
                rmse = float(np.sqrt(np.mean(res ** 2))) * 100.0   # as %
                ss_tot = float(np.sum((actual - actual.mean()) ** 2))
                r2 = float(1.0 - np.sum(res ** 2) / ss_tot) if ss_tot > 0 else 0.0

                ax.plot(cycles, fitted * 100.0, '--', color=color,
                        linewidth=1.6, alpha=0.88,
                        label=f"{name}   R²={r2:.3f}   RMSE={rmse:.2f}%")

                # ── shaded error band (±1 RMSE) ───────────────────────────
                ax.fill_between(cycles,
                                (fitted - rmse / 100.0) * 100.0,
                                (fitted + rmse / 100.0) * 100.0,
                                color=color, alpha=0.08)
            except Exception:
                pass   # skip model if fit fails

        # ── reference thresholds ──────────────────────────────────────────
        for pct, col in [(90, Theme.YELLOW), (80, Theme.PEACH), (50, Theme.RED)]:
            ax.axhline(pct, linestyle=':', linewidth=0.9, color=col, alpha=0.6)
            ax.text(cycles[-1] * 0.995, pct + 0.8, f"{pct}%",
                    fontsize=7, ha='right', color=col)

        ax.set_xlim(0, cycles[-1])
        ax.set_ylim(0, 105)
        ax.set_xlabel("Cycles (N)")
        ax.set_ylabel("Preload Retention  F/F₀ (%)")
        ax.set_title("Preload Loss Models — Fit to Simulated Decay")
        ax.legend(fontsize=7, loc='lower left')
        ax.grid(True, alpha=0.3)
        self.results_tab.current_plot_label.setText("Current: Preload Loss Models")
        canvas._apply_theme()
        canvas.draw()

    # ------------------------------------------------------------------
    def _on_stage_overlay_changed(self):
        """Re-plot Stage Analysis when the secondary-axis overlay changes."""
        if (self.results_tab.current_plot_type == "Stage Analysis"
                and self.app_state.results
                and self.app_state.results.coupled_loosening_result):
            overlay_text = self.results_tab.stage_overlay_combo.currentText()
            self._plot_stage_analysis_animated(
                self.app_state.results.coupled_loosening_result, overlay_text)

    # ------------------------------------------------------------------
    def _save_stage_animation_gif(self):
        """Save the current Stage Analysis animation as an animated GIF."""
        from PyQt6.QtWidgets import QFileDialog
        import os

        anim = getattr(self, '_stage_animation', None)
        if anim is None:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Animation",
                                "Open Stage Analysis first to generate the animation.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Stage Analysis as GIF",
            "stage_analysis.gif", "GIF Files (*.gif)"
        )
        if not filepath:
            return

        btn = self.results_tab.stage_gif_btn
        btn.setEnabled(False)
        btn.setText("Saving…")
        self._on_status_message("Saving GIF — please wait…")
        from PyQt6.QtWidgets import QApplication
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        QApplication.processEvents()

        try:
            from matplotlib.animation import PillowWriter
            writer = PillowWriter(fps=25)
            anim.save(filepath, writer=writer, dpi=100)
            self._on_status_message(
                f"GIF saved: {os.path.basename(filepath)}")
        except ImportError:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self, "Missing Dependency",
                "Pillow is required to save GIFs.\n\nInstall with:  pip install Pillow")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Save Failed",
                                 f"Could not save GIF:\n\n{e}")
            self._on_status_message("GIF save failed")
        finally:
            QApplication.restoreOverrideCursor()
            btn.setEnabled(True)
            btn.setText("💾  Save GIF")

    # ------------------------------------------------------------------
    def _plot_stage_analysis_animated(self, cl: CoupledLooseningResult,
                                      overlay_text: str = "None"):
        """
        Animated Stage Analysis: the preload curve and phase-coloured
        background grow cycle by cycle, with live text showing the current
        phase, preload retention, and torque margin.

        overlay_text selects an optional quantity on a secondary Y-axis
        (e.g. "Loosening Rate  (deg/cycle)", "Torque Margin", …).

        The animation runs once (repeat=False) at ~25 fps.
        Stored in self._stage_animation to prevent garbage collection.
        """
        import numpy as np
        from matplotlib.animation import FuncAnimation
        from matplotlib.patches import Patch

        cycles = np.asarray(cl.cycles, dtype=float)
        preload_pct = np.asarray(cl.preload_ratio, dtype=float) * 100.0
        n_pts = len(cycles)

        # ── per-cycle phase values ─────────────────────────────────────────
        if cl.states and len(cl.states) >= n_pts:
            phases = [
                s.phase.value if hasattr(s.phase, 'value') else str(s.phase)
                for s in cl.states[:n_pts]
            ]
            torque_margins = [
                getattr(s, 'torque_margin', 1.0) for s in cl.states[:n_pts]
            ]
        elif cl.states and len(cl.states) > 1:
            # states list shorter than cycles → interpolate indices
            ratio = (len(cl.states) - 1) / max(n_pts - 1, 1)
            phases = [
                cl.states[int(i * ratio)].phase.value
                if hasattr(cl.states[int(i * ratio)].phase, 'value')
                else str(cl.states[int(i * ratio)].phase)
                for i in range(n_pts)
            ]
            torque_margins = [
                getattr(cl.states[int(i * ratio)], 'torque_margin', 1.0)
                for i in range(n_pts)
            ]
        else:
            phases = [cl.phase_at_end or 'stable'] * n_pts
            torque_margins = [1.0] * n_pts

        # ── Transverse / Junker model (Jiang 5-stage) ────────────────────────
        # ── Axial 3-stage model ───────────────────────────────────────────────
        # Colors: LOOSENING_STAGE_DEFINITIONS.md §3 colour mapping table.
        phase_colors = {
            # Transverse / Junker — Jiang 5-stage
            'stable':           Theme.GREEN,
            'non_rotational':   Theme.BLUE,
            'transition':       Theme.YELLOW,
            'rotational':       Theme.PEACH,
            'runaway':          Theme.RED,
            # Axial — 3-stage axial model
            'axial_stage_i':    Theme.TEAL,
            'axial_stage_ii':   Theme.MAUVE,
            'axial_stage_iii':  Theme.RED,
        }
        phase_labels = {
            # Transverse / Junker — Jiang 5-stage
            'stable':           'Stable',
            'non_rotational':   'Non-rotational (Stage I)',
            'transition':       'Transition',
            'rotational':       'Rotational (Stage II)',
            'runaway':          'Run-away',
            # Axial — 3-stage axial model
            'axial_stage_i':    'Axial Stage I (Rapid Drop)',
            'axial_stage_ii':   'Axial Stage II (Slow Decay)',
            'axial_stage_iii':  'Axial Stage III (Failure)',
        }

        # ── overlay (secondary Y axis) data ───────────────────────────────
        _OVERLAY_MAP = {
            "Loosening Rate  (deg/cycle)":    ("loosening_rate",       "deg/cycle", Theme.PEACH),
            "Torque Margin":                  ("torque_margin",        "",           Theme.YELLOW),
            "Friction Margin  (\u03bc / \u03bc_crit)": ("friction_margin", "",      Theme.BLUE),
            "Thread \u03bc":                  ("mu_thread",            "",           Theme.MAUVE),
            "Bearing \u03bc":                 ("mu_bearing",           "",           Theme.SKY),
            "Cumulative Angle  (\u00b0)":     ("loosening_angle_deg",  "\u00b0",     Theme.RED),
            "Wear Depth  (\u03bcm)":          ("total_wear_um",        "\u03bcm",    Theme.TEAL),
        }
        _ov_info = _OVERLAY_MAP.get(overlay_text)   # None when "None" selected
        overlay_data = None
        ov_color = Theme.PEACH
        ov_ylabel = ""
        if _ov_info:
            _ov_attr, _ov_unit, ov_color = _ov_info
            _ov_arr = getattr(cl, _ov_attr, None)
            if _ov_arr is not None:
                overlay_data = np.asarray(_ov_arr, dtype=float)[:n_pts]
                _ov_name = overlay_text.split("(")[0].strip()
                ov_ylabel = f"{_ov_name}  [{_ov_unit}]" if _ov_unit else _ov_name

        # ── animation frame indices ────────────────────────────────────────
        N_FRAMES = min(n_pts, 180)
        frame_ends = np.unique(
            np.linspace(2, n_pts, N_FRAMES, dtype=int)
        )

        # ── setup figure ──────────────────────────────────────────────────
        canvas = self.results_tab.plot_widget.canvas
        fig = canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        canvas.axes = ax   # keep canvas.axes pointing to the active axes

        # static reference lines
        for pct, col in [(90, Theme.YELLOW), (80, Theme.PEACH), (50, Theme.RED)]:
            ax.axhline(pct, linestyle=':', linewidth=0.8, color=col, alpha=0.5)
            ax.text(cycles[-1] * 0.995, pct + 0.8, f"{pct}%",
                    fontsize=7, ha='right', color=col)

        ax.set_xlim(0, cycles[-1])
        ax.set_ylim(0, 105)
        ax.set_xlabel("Number of Cycles (N)")
        ax.set_ylabel("Preload Retention  F/F₀ (%)")
        ax.set_title("Stage Analysis — Evolution")
        ax.grid(True, alpha=0.25)

        # ── secondary Y axis ──────────────────────────────────────────────
        ax2 = None
        ov_line = None
        if overlay_data is not None:
            ax2 = ax.twinx()
            ax2.set_ylabel(ov_ylabel, color=ov_color, fontsize=9)
            ax2.tick_params(axis='y', colors=ov_color, labelsize=8)
            ax2.spines['right'].set_color(ov_color)
            ax2.spines['right'].set_linewidth(1.2)
            # Fix y-limits from full data so the axis doesn't rescale each frame
            _ov_min, _ov_max = float(np.nanmin(overlay_data)), float(np.nanmax(overlay_data))
            _ov_pad = (_ov_max - _ov_min) * 0.12 if _ov_max != _ov_min else max(abs(_ov_max) * 0.1, 0.1)
            ax2.set_ylim(_ov_min - _ov_pad, _ov_max + _ov_pad)
            ax2.set_xlim(0, cycles[-1])
            ov_line, = ax2.plot([], [], color=ov_color, linewidth=1.8,
                                alpha=0.85, zorder=8, linestyle='--')

        # legend for phases (static)
        legend_handles = [
            Patch(facecolor=c, alpha=0.55, label=phase_labels.get(k, k))
            for k, c in phase_colors.items()
        ]
        ax.legend(handles=legend_handles, loc='upper right', fontsize=7)

        # dynamic text artists (drawn once, updated each frame)
        dot = ax.scatter([], [], color=Theme.PEACH, s=60, zorder=11)
        phase_text = ax.text(0.02, 0.95, '', transform=ax.transAxes,
                             fontsize=10, va='top', color=Theme.GREEN,
                             fontweight='bold')
        stats_text = ax.text(0.98, 0.95, '', transform=ax.transAxes,
                             fontsize=8, va='top', ha='right', color=Theme.SUBTEXT)

        # containers for removable artists each frame
        _spans = []        # background axvspan patches
        _lc_artists = []  # LineCollection segments (phase-coloured line)

        def _update(end_idx):
            from matplotlib.collections import LineCollection

            # ── remove previous dynamic artists ───────────────────────────
            for artist in _spans + _lc_artists:
                try:
                    artist.remove()
                except Exception:
                    pass
            _spans.clear()
            _lc_artists.clear()

            c = cycles[:end_idx]
            p = preload_pct[:end_idx]
            ph = phases[:end_idx]
            tm = torque_margins[:end_idx]

            if len(c) < 2:
                return [dot, phase_text, stats_text]

            # ── faint phase background spans ───────────────────────────────
            seg_start = 0
            prev_ph = ph[0]
            for i in range(1, len(c)):
                if ph[i] != prev_ph or i == len(c) - 1:
                    col = phase_colors.get(prev_ph, Theme.SURFACE0)
                    x1 = c[i] if ph[i] != prev_ph else c[-1]
                    sp = ax.axvspan(c[seg_start], x1, alpha=0.13,
                                    color=col, linewidth=0, zorder=1)
                    _spans.append(sp)
                    seg_start = i
                    prev_ph = ph[i]

            # ── phase-coloured line via LineCollection ─────────────────────
            # Build (N-1) two-point segments; colour each by its phase
            pts = np.column_stack([c, p])                       # shape (N, 2)
            segs = np.stack([pts[:-1], pts[1:]], axis=1)        # (N-1, 2, 2)
            seg_colors = [
                phase_colors.get(ph[i], Theme.TEXT)
                for i in range(len(ph) - 1)
            ]
            lc = LineCollection(segs, colors=seg_colors,
                                linewidths=2.5, zorder=9,
                                capstyle='round', joinstyle='round')
            ax.add_collection(lc)
            _lc_artists.append(lc)

            # ── moving dot at the current point ───────────────────────────
            dot.set_offsets([[c[-1], p[-1]]])

            # ── secondary axis overlay ─────────────────────────────────────
            if ov_line is not None:
                ov_line.set_data(c, overlay_data[:end_idx])

            # ── live text & dynamic colour ─────────────────────────────────
            cur_ph = ph[-1]
            cur_color = phase_colors.get(cur_ph, Theme.TEXT)

            phase_text.set_text(phase_labels.get(cur_ph, cur_ph))
            phase_text.set_color(cur_color)

            stats_text.set_text(
                f"Cycle {int(c[-1]):,}  |  F/F₀ = {p[-1]:.1f}%"
                f"  |  Margin = {tm[-1]:.3f}"
            )
            stats_text.set_color(cur_color)

            # dot colour and size follow current phase
            dot.set_facecolors([cur_color])
            dot.set_edgecolors([cur_color])
            dot.set_sizes([90 if cur_ph == 'runaway' else 60])

            # title reflects current phase name in its colour
            ax.set_title(
                f"Stage Analysis  —  {phase_labels.get(cur_ph, cur_ph)}",
                color=cur_color,
            )

            extra = [ov_line] if ov_line is not None else []
            return [dot, phase_text, stats_text] + extra + _lc_artists + _spans

        self._stage_animation = FuncAnimation(
            fig, _update, frames=frame_ends,
            interval=40, blit=False, repeat=False
        )
        self.results_tab.current_plot_label.setText("Current: Stage Analysis (animated)")
        canvas.draw()

    def _plot_preload_vs_time(self, results):
        """Plot preload vs time if time data available."""
        import numpy as np
        canvas = self.results_tab.plot_widget.canvas
        ax = canvas.axes
        ax.clear()

        BLUE = Theme.BLUE
        YELLOW = Theme.YELLOW
        RED = Theme.RED

        if results.coupled_loosening_result:
            cl = results.coupled_loosening_result
            # Convert cycles to time using model frequency (Bug 3 fix: no hardcoded 25 Hz)
            frequency = 25.0  # fallback
            try:
                model = self.app_state.model
                if model and hasattr(model, 'global_loading') and model.global_loading:
                    frequency = model.global_loading.frequency or 25.0
            except Exception:
                pass
            time = cl.cycles / frequency
            preload_kN = np.array(cl.preload_ratio) * cl.initial_preload / 1000

            ax.plot(time, preload_kN, color=BLUE, linewidth=2, label='BAS prediction')
            # Bandas de estágio (Jiang): I estável / II transição-rotacional / III runaway.
            _F0kN = cl.initial_preload / 1000
            ax.axhspan(0.90 * _F0kN, _F0kN, color=Theme.GREEN, alpha=0.06, zorder=0)
            ax.axhspan(0.55 * _F0kN, 0.90 * _F0kN, color=Theme.YELLOW, alpha=0.06, zorder=0)
            ax.axhspan(0.0, 0.55 * _F0kN, color=Theme.RED, alpha=0.06, zorder=0)
            ax.axhline(y=0.9 * cl.initial_preload / 1000, color=YELLOW, linestyle='--', alpha=0.7)
            ax.axhline(y=0.8 * cl.initial_preload / 1000, color=RED, linestyle='--', alpha=0.7)

            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Preload (kN)')
            ax.set_title('Preload vs Time')
            ax.grid(True, alpha=0.3)

            ref = getattr(self, '_reference_curve', None)
            if ref is not None:
                ref_cycle, ref_kN = ref['cycle'], ref['F_kN']
                # CSV rows are per-cycle bin AVERAGES (1-second windows at 1 Hz),
                # centred at (cycle + 0.5) relative to the window's left edge.
                # Shift by +0.5 cycle so the overlay aligns with BAS' end-of-cycle points.
                ref_time = (ref_cycle + 0.5) / max(frequency, 1e-9)
                ax.plot(ref_time, ref_kN, color=Theme.PEACH, linewidth=1.5,
                        linestyle=':', label=f"Reference ({ref.get('label', 'CSV')})")
                ax.legend(loc='best', fontsize=9)

        canvas._apply_theme()
        canvas.draw()

    def _load_reference_csv(self, path: str = ""):
        """Load an experimental preload-decay CSV (cycle, F_kN, F_over_F0) and overlay it.

        If ``path`` is provided (e.g. from the Validation Suite auto-load),
        it is used directly; otherwise a QFileDialog is shown.
        """
        import csv as _csv
        import os as _os
        import numpy as np
        if not path:
            start_dir = _os.path.join(_os.getcwd(), 'Models', 'EXPERIMENTAL_ANCORA', 'reference_curves')
            if not _os.path.isdir(start_dir):
                start_dir = _os.getcwd()
            path, _ = QFileDialog.getOpenFileName(
                self, "Load reference preload-decay CSV", start_dir, "CSV files (*.csv)")
        if not path:
            return
        try:
            cycle, F_kN, F_ratio = [], [], []
            with open(path, encoding='utf-8', newline='') as f:
                reader = _csv.reader(f)
                for row in reader:
                    if not row:
                        continue
                    try:
                        c = float(row[0])
                    except ValueError:
                        continue  # header
                    cycle.append(c)
                    F_kN.append(float(row[1]) if len(row) > 1 else 0.0)
                    F_ratio.append(float(row[2]) if len(row) > 2 else 0.0)
            if not cycle:
                raise ValueError("no numeric rows parsed")
            self._reference_curve = {
                'cycle': np.asarray(cycle),
                'F_kN': np.asarray(F_kN),
                'F_ratio': np.asarray(F_ratio),
                'label': _os.path.basename(path),
                'path': path,
            }
            self.results_tab.ref_clear_btn.setEnabled(True)
            self.results_tab.auto_calibrate_btn.setEnabled(True)
            self.results_tab.calibrate_btn.setEnabled(True)
            self._refresh_current_plot()
            self.status_bar.showMessage(
                f"Reference loaded: {_os.path.basename(path)}  "
                f"({len(cycle)} points) — click ⚙ Calibrate Model… or press Ctrl+K", 8000)
        except Exception as e:
            QMessageBox.warning(self, "Load Reference",
                                f"Could not read CSV:\n{e}")

    def _clear_reference_curve(self):
        """Remove the reference overlay."""
        self._reference_curve = None
        self.results_tab.ref_clear_btn.setEnabled(False)
        self.results_tab.auto_calibrate_btn.setEnabled(False)
        # calibrate_btn stays enabled — dialog prompts user to load CSV
        self._refresh_current_plot()
        self.status_bar.showMessage("Reference curve cleared", 3000)

    def _auto_calibrate_mu(self):
        """Sweep μ ∈ [0.06, 0.25] and find the value minimising MAE vs reference."""
        import numpy as np
        ref = getattr(self, '_reference_curve', None)
        if ref is None:
            QMessageBox.information(self, "Auto-calibrate μ",
                                    "Load a reference CSV first.")
            return
        model = self.app_state.model
        if model is None or not hasattr(model, 'global_loading') or model.global_loading is None:
            QMessageBox.warning(self, "Auto-calibrate μ",
                                "No active MSD model with global loading.")
            return
        try:
            from bolt_analysis_studio.numerical.coupled_loosening_analyzer import (
                create_analyzer_from_msd_model,
            )
        except Exception as e:
            QMessageBox.critical(self, "Auto-calibrate μ",
                                 f"Analyzer import failed:\n{e}")
            return

        gl = model.global_loading
        F0_N = float(gl.F_preload or 0.0)
        if F0_N <= 0:
            QMessageBox.warning(self, "Auto-calibrate μ",
                                "Preload must be > 0 to calibrate.")
            return
        n_cycles = int(gl.n_cycles or ref['cycle'].max() or 500)

        mu_grid = np.linspace(0.06, 0.25, 20)
        ref_cycle = ref['cycle']
        ref_ratio = (ref['F_ratio'] if np.any(ref['F_ratio'] > 0)
                     else ref['F_kN'] * 1000.0 / F0_N)

        mu_original = float(getattr(model, 'mu_initial', 0.12) or 0.12)
        best = None
        first_error = None
        self.status_bar.showMessage("μ sweep running…")
        try:
            for mu in mu_grid:
                try:
                    gl.mu_initial = float(mu)           # Level-2 (in-session dynamic attr)
                    model.mu_initial = float(mu)        # Level-3 (persistent field)
                    analyzer, info = create_analyzer_from_msd_model(model)
                    F_trans = float(info.get('transverse_force_N', 0.0) or 0.0)
                    if F_trans <= 0:
                        raise ValueError(
                            "Transverse force could not be derived from the model "
                            "(set F_transverse or delta_amplitude + k_transverse).")
                    result = analyzer.run_analysis(
                        preload_initial=F0_N,
                        F_transverse=F_trans,
                        n_cycles=n_cycles,
                        output_interval=max(1, n_cycles // 500))
                    sim_cycle = np.asarray(result.cycles, dtype=float)
                    sim_ratio = np.asarray(result.preload_ratio, dtype=float)
                    if sim_cycle.size == 0:
                        continue
                    interp = np.interp(ref_cycle, sim_cycle, sim_ratio,
                                       left=sim_ratio[0], right=sim_ratio[-1])
                    err = interp - ref_ratio
                    mae = float(np.mean(np.abs(err)))
                    rmse = float(np.sqrt(np.mean(err ** 2)))
                    if best is None or mae < best['mae']:
                        best = {'mu': float(mu), 'mae': mae, 'rmse': rmse}
                except Exception as e:
                    if first_error is None:
                        first_error = f"μ={mu:.3f}: {e}"
                    continue
        finally:
            # Always restore to a sane value — best if we have one, original otherwise
            final_mu = best['mu'] if best is not None else mu_original
            gl.mu_initial = final_mu
            model.mu_initial = final_mu
            self.status_bar.clearMessage()
        if best is None:
            QMessageBox.warning(
                self, "Auto-calibrate μ",
                f"Sweep failed — no valid simulation produced.\n"
                f"First error: {first_error or 'unknown'}")
            return
        resp = QMessageBox.question(
            self, "Auto-calibrate μ",
            f"Best match:\n  μ = {best['mu']:.3f}\n"
            f"  MAE (F/F₀) = {best['mae']:.4f}\n"
            f"  RMSE (F/F₀) = {best['rmse']:.4f}\n\n"
            f"global_loading.mu_initial set to {best['mu']:.3f}.\n\n"
            f"Re-run the Solver now to visualise?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if resp == QMessageBox.StandardButton.Yes:
            # Apply & Re-run: μ is already written to the model in-place above,
            # so just kick the standard analysis flow.
            self._run_analysis()

    # ── Web tools (browser-based; no QWebEngine dependency) ───────────────
    def _open_calibration_tuner(self):
        """Start the calibration server in the background, then open the tuner.

        Uses the stdlib ``webbrowser`` module (no QWebEngine dependency). If the
        server is already up on port 8765 the running instance is reused — a
        second launch would merely fail to bind the port and exit, so nothing is
        torn down. Never blocks the GUI (subprocess is detached; the browser is
        opened from a QTimer).
        """
        import os
        import sys
        import subprocess
        import webbrowser
        import urllib.request

        url = "http://localhost:8765/"

        def _open():
            try:
                webbrowser.open(url)
            except Exception:
                pass

        # Already running? Just open the URL and reuse it.
        try:
            urllib.request.urlopen(url, timeout=0.5)
            _open()
            self._on_status_message(f"Calibration Tuner already running → {url}")
            return
        except Exception:
            pass

        # Not up — launch `python -m bolt_analysis_studio.calibration.server`
        # with the same interpreter, cwd = repo root, and src/ injected on
        # PYTHONPATH so the package resolves even without an editable install.
        try:
            gui_file = Path(__file__).resolve()
            src_dir = str(gui_file.parents[2])     # …/src
            repo_root = str(gui_file.parents[3])   # repository root
            env = os.environ.copy()
            env["PYTHONPATH"] = src_dir + os.pathsep + env.get("PYTHONPATH", "")
            subprocess.Popen(
                [sys.executable, "-m",
                 "bolt_analysis_studio.calibration.server"],
                cwd=repo_root, env=env,
            )
        except Exception as exc:
            QMessageBox.warning(
                self, "Calibration Tuner",
                f"Failed to start the calibration server:\n{exc}")
            return

        # Give the server a moment to bind the port, then open the browser.
        QTimer.singleShot(1500, _open)
        self._on_status_message(f"Starting Calibration Tuner → {url}")

    def _open_validation_gallery(self):
        """Open a local validation report in the default browser (webbrowser).

        Looks under ``validation_html/`` at the repo root first (as documented),
        then ``New_Theory/validation_html/`` where the reports currently live.
        """
        import webbrowser

        # Gera/atualiza via pacote validation (Plano A) — rapido (store/seed,
        # sem simular). Fallback: abrir um HTML existente (comportamento antigo).
        try:
            from bolt_analysis_studio.validation.report import ensure_reports
            target = ensure_reports()
            webbrowser.open(target.as_uri())
            self._on_status_message(f"Validation Gallery → {target.name}")
            return
        except Exception:
            pass

        repo_root = Path(__file__).resolve().parents[3]
        candidates = [
            repo_root / "validation_html" / "loosening_explorer.html",
            repo_root / "validation_html" / "validation_report.html",
            repo_root / "New_Theory" / "validation_html" / "loosening_explorer.html",
            repo_root / "New_Theory" / "validation_html" / "validation_report.html",
        ]
        target = next((p for p in candidates if p.exists()), None)
        if target is None:
            QMessageBox.information(
                self, "Validation Gallery",
                "Nenhum relatório de validação encontrado.\n\n"
                "Procurei por 'loosening_explorer.html' / 'validation_report.html' "
                "em 'validation_html/' e 'New_Theory/validation_html/'.\n\n"
                "Gere os reports primeiro.")
            return
        try:
            webbrowser.open(target.as_uri())
        except Exception as exc:
            QMessageBox.warning(
                self, "Validation Gallery",
                f"Failed to open the report:\n{exc}")
            return
        self._on_status_message(f"Validation Gallery → {target.name}")

    def _open_calibration_dialog(self):
        """Open the full parameter-identification dialog."""
        ref = getattr(self, '_reference_curve', None)
        if ref is None:
            QMessageBox.information(self, "Calibrate",
                                    "Load a reference CSV first.")
            return
        model = self.app_state.model
        if model is None or not hasattr(model, 'global_loading') or model.global_loading is None:
            QMessageBox.warning(self, "Calibrate",
                                "No active MSD model with global loading.")
            return
        if float(model.global_loading.F_preload or 0.0) <= 0:
            QMessageBox.warning(self, "Calibrate",
                                "Preload must be > 0 to calibrate.")
            return
        k_trans = None
        try:
            k_trans = float(getattr(model, 'k_transverse', 0.0) or 0.0) or None
        except Exception:
            k_trans = None
        dialog = CalibrationDialog(self, model, ref, transverse_stiffness=k_trans)
        dialog.exec()

    def _plot_no_data(self, title: str, message: str):
        """Show a 'no data' message on the plot canvas."""
        canvas = self.results_tab.plot_widget.canvas
        ax = canvas.axes
        ax.clear()
        ax.text(0.5, 0.5, message, transform=ax.transAxes,
                ha='center', va='center', fontsize=11,
                color=Theme.SUBTEXT, style='italic', multialignment='center')
        ax.set_title(title)
        ax.axis('off')
        self.results_tab.current_plot_label.setText(f"Current: {title}")
        canvas._apply_theme()
        canvas.draw()

    def _plot_excitation_proxy(self, quantity: str, units: str):
        """
        Line graph for Displacement / Velocity / Acceleration.

        Priority:
          1. Use coupled-loosening simulation arrays when available
             (loosening_angle_deg for displacement, loosening_rate for velocity,
              gradient of loosening_rate for acceleration).
          2. Fall back to input-excitation sinusoid limited to 10 cycles so
             individual waves are visible (not a solid block).
        """
        import numpy as np

        canvas = self.results_tab.plot_widget.canvas
        ax = canvas.axes
        ax.clear()

        # ── try actual simulation data first ──────────────────────────────
        cl = None
        try:
            cl = self.app_state.results.coupled_loosening_result
        except Exception:
            pass

        if cl is not None:
            cycles = np.asarray(cl.cycles, dtype=float)
            freq = 12.5
            try:
                model = self.app_state.model
                if model and model.global_loading:
                    freq = model.global_loading.frequency or 12.5
            except Exception:
                pass

            if quantity == "Displacement" and cl.loosening_angle_deg is not None:
                data = np.asarray(cl.loosening_angle_deg, dtype=float)
                ylabel = "Cumulative Loosening Angle (°)"
                title = "Displacement — Cumulative Loosening Rotation"

            elif quantity == "Velocity" and cl.loosening_rate is not None:
                data = np.asarray(cl.loosening_rate, dtype=float) * freq
                ylabel = "Loosening Rate (°/s)"
                title = "Velocity — Loosening Rate"

            elif quantity == "Acceleration" and cl.loosening_rate is not None:
                rate = np.asarray(cl.loosening_rate, dtype=float) * freq
                data = np.gradient(rate, cycles)
                ylabel = "ΔRate / ΔCycle (°/s per cycle)"
                title = "Acceleration — Rate of Change of Loosening"

            else:
                cl = None   # field missing → fall through

            if cl is not None:
                ax.plot(cycles, data, color=Theme.BLUE, linewidth=1.5)
                ax.set_xlabel("Cycles (N)")
                ax.set_ylabel(ylabel)
                ax.set_title(title)
                ax.grid(True, alpha=0.3)
                self.results_tab.current_plot_label.setText(f"Current: {quantity}")
                canvas._apply_theme()
                canvas.draw()
                return

        # ── fallback: input-excitation sinusoid, 10-cycle window ──────────
        freq = 12.5
        amp_mm = 0.65
        try:
            model = self.app_state.model
            if model and model.global_loading:
                gl = model.global_loading
                freq = gl.frequency or 12.5
                amp_mm = gl.delta_amplitude or 0.65
        except Exception:
            pass

        amp_m = amp_mm / 1000.0
        omega = 2.0 * np.pi * freq
        n_show = 10                                         # only 10 cycles — individually readable
        t = np.linspace(0, n_show / freq, 500)

        if quantity == "Displacement":
            signal = amp_m * np.sin(omega * t)
            title = "Transverse Displacement — Input Excitation (10 cycles)"
        elif quantity == "Velocity":
            signal = amp_m * omega * np.cos(omega * t)
            title = "Transverse Velocity — Input Excitation (10 cycles)"
        else:
            signal = -amp_m * omega ** 2 * np.sin(omega * t)
            title = "Transverse Acceleration — Input Excitation (10 cycles)"

        ax.plot(t, signal, color=Theme.BLUE, linewidth=1.5)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(f"{quantity} ({units})")
        ax.set_title(f"{title}\n(Run Time Integration for full structural response)")
        ax.grid(True, alpha=0.3)
        self.results_tab.current_plot_label.setText(f"Current: {quantity} (excitation)")
        canvas._apply_theme()
        canvas.draw()

    def _plot_mode_shapes(self, results):
        """Bar chart of natural frequencies by mode number."""
        import numpy as np
        freqs = results.natural_frequencies
        canvas = self.results_tab.plot_widget.canvas
        ax = canvas.axes
        ax.clear()

        n = len(freqs)
        x = np.arange(1, n + 1)
        ax.bar(x, freqs, color=Theme.MAUVE, alpha=0.82,
               edgecolor=Theme.OVERLAY, linewidth=0.8)
        for xi, fn in zip(x, freqs):
            ax.text(xi, fn * 1.01, f"{fn:.2f}", ha='center',
                    va='bottom', fontsize=8, color=Theme.TEXT)

        ax.set_xlabel("Mode Number")
        ax.set_ylabel("Natural Frequency (Hz)")
        ax.set_title(f"Natural Frequencies  ({n} mode{'s' if n != 1 else ''})")
        ax.set_xticks(x)
        ax.set_xticklabels(
            [f"Mode {i}" for i in x],
            rotation=30 if n > 5 else 0, ha='right'
        )
        ax.grid(True, alpha=0.3, axis='y')
        self.results_tab.current_plot_label.setText("Current: Mode Shapes")
        canvas._apply_theme()
        canvas.draw()

    def _plot_campbell_diagram(self, results):
        """Campbell diagram: natural frequency lines vs excitation engine orders."""
        import numpy as np
        freqs = results.natural_frequencies
        base_freq = 12.5
        try:
            model = self.app_state.model
            if model and model.global_loading:
                base_freq = model.global_loading.frequency or 12.5
        except Exception:
            pass

        max_rpm = base_freq * 60 * 3.0
        rpm = np.linspace(0, max_rpm, 500)

        canvas = self.results_tab.plot_widget.canvas
        ax = canvas.axes
        ax.clear()

        _mode_colors = [Theme.BLUE, Theme.GREEN, Theme.YELLOW, Theme.MAUVE, Theme.RED]
        for i, fn in enumerate(freqs):
            color = _mode_colors[i % len(_mode_colors)]
            ax.axhline(y=fn, color=color, linewidth=2.0,
                       label=f"Mode {i + 1}: {fn:.2f} Hz")

        for order in [1, 2, 3, 4, 6]:
            f_exc = rpm / 60.0 * order
            ax.plot(rpm, f_exc, linestyle='--', linewidth=0.7,
                    color=Theme.SUBTEXT, alpha=0.5)
            ax.text(rpm[-1] * 0.97, f_exc[-1], f"{order}×",
                    fontsize=7, ha='right', va='center', color=Theme.SUBTEXT)

        op_rpm = base_freq * 60.0
        ax.axvline(x=op_rpm, color=Theme.PEACH, linestyle=':', linewidth=1.5,
                   label=f"Operating: {op_rpm:.0f} RPM")

        ax.set_xlabel("Speed (RPM)")
        ax.set_ylabel("Frequency (Hz)")
        ax.set_title("Campbell Diagram")
        ax.legend(fontsize=8, loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, max_rpm)
        ax.set_ylim(0)
        self.results_tab.current_plot_label.setText("Current: Campbell Diagram")
        canvas._apply_theme()
        canvas.draw()

    def _suggest_timestep(self):
        """Suggest optimal timestep based on model natural frequencies."""
        if self.app_state.model is None:
            QMessageBox.warning(
                self, "No Model",
                "Please load or create a model first."
            )
            return

        try:
            # Assemble matrices
            M, K, C = self.app_state.model.assemble_matrices()

            # Calculate natural frequencies
            import numpy as np
            eigenvalues = np.linalg.eigvals(np.linalg.inv(M) @ K)
            natural_freqs = np.sqrt(np.abs(eigenvalues)) / (2 * np.pi)
            max_freq = np.max(natural_freqs)
            min_freq = np.min(natural_freqs[natural_freqs > 0.1])  # Ignore near-zero modes

            # Calculate recommended timestep (period/10)
            dt_recommended = 1.0 / (10 * max_freq)

            # Calculate total steps
            t_end = self.solver_tab.t_end_spin.value()
            n_steps = int(t_end / dt_recommended)

            # Create dialog
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
            dialog = QDialog(self)
            dialog.setWindowTitle("Time Step Recommendation")
            dialog.setMinimumWidth(500)

            layout = QVBoxLayout(dialog)

            # Info message
            info_text = QLabel(
                f"<h3>Model Frequency Analysis</h3>"
                f"<p><b>Natural frequency range:</b> {min_freq:.1f} - {max_freq:.1f} Hz</p>"
                f"<p><b>Highest frequency period:</b> {1/max_freq:.3e} s</p>"
                f"<hr>"
                f"<h3>Recommended Time Step</h3>"
                f"<p><b>dt = {dt_recommended:.3e} s</b></p>"
                f"<p>Based on rule: dt ≤ T_min / 10 for numerical stability</p>"
                f"<hr>"
                f"<p><b>Simulation length:</b> {t_end} s</p>"
                f"<p><b>Number of steps:</b> {n_steps:,}</p>"
                f"<p><b>Estimated computation:</b> {'< 1 min' if n_steps < 50000 else '1-5 min' if n_steps < 200000 else '> 5 min'}</p>"
            )
            info_text.setWordWrap(True)
            info_text.setStyleSheet(f"color: {Theme.TEXT}; padding: 10px;")
            layout.addWidget(info_text)

            # Buttons
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Apply |
                QDialogButtonBox.StandardButton.Cancel
            )

            # Connect Apply button specifically (it doesn't emit accepted())
            apply_btn = buttons.button(QDialogButtonBox.StandardButton.Apply)
            if apply_btn:
                apply_btn.clicked.connect(lambda: self._apply_timestep(dialog, dt_recommended))

            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            # Show dialog
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Failed to calculate time step:\n\n{str(e)}"
            )

    def _apply_timestep(self, dialog, dt_value):
        """Apply the recommended timestep and close dialog."""
        self.solver_tab.dt_spin.setValue(dt_value)
        self._on_status_message(f"Applied recommended time step: {dt_value:.3e} s")
        dialog.accept()

    def _auto_calculate_timestep(self):
        """Auto-calculate timestep based on number of cycles, frequency, and sample percentage.

        For large cycle counts (e.g., 5 million), uses percentage-based sampling:
        - Sample % determines what fraction of cycles generate output points
        - Target Points provides an alternative fixed-count approach
        - dt is calculated to achieve the target number of integration steps

        Strategy for different cycle ranges:
        - < 10,000 cycles: Fine resolution (10-100 steps per cycle)
        - 10,000 - 100,000 cycles: Medium resolution (1-10 steps per cycle)
        - 100,000 - 1,000,000 cycles: Coarse resolution (0.1-1 step per cycle)
        - > 1,000,000 cycles: Cycle-based models only (1 point per N cycles)
        """
        n_cycles = self.solver_tab.n_cycles_spin.value()
        frequency = self.solver_tab.frequency_spin.value()
        sample_pct = self.solver_tab.sample_pct_spin.value()
        target_points = self.solver_tab.target_points_spin.value()

        if frequency <= 0:
            return

        # Total simulation time
        t_end = n_cycles / frequency

        # Determine number of output points based on sample percentage or target
        # Use whichever gives fewer points (more efficient)
        points_from_pct = int(n_cycles * sample_pct / 100.0)
        points_from_target = target_points

        # Use the smaller value, but ensure at least 100 points
        n_output_points = max(100, min(points_from_pct, points_from_target))

        # For cycle-based loosening analysis, we need at least 1 point per output
        # but can skip many cycles between outputs for large N
        cycles_per_output = max(1, n_cycles // n_output_points)

        # Calculate timestep: dt = period_per_output_point
        # Each output point spans 'cycles_per_output' cycles
        period_per_cycle = 1.0 / frequency
        dt = period_per_cycle * cycles_per_output

        # For very large cycle counts (>100k), use cycle-based approach
        # where dt represents multiple cycles, not sub-cycle resolution
        if n_cycles > 100000:
            # Cycle-based mode: dt = time for 'cycles_per_output' cycles
            # Minimum 1 cycle per step for numerical stability
            dt = max(period_per_cycle, dt)
            mode = "cycle-based"
        else:
            # Fine mode: multiple steps per cycle for accuracy
            steps_per_cycle = max(1, 10000 // n_cycles) if n_cycles < 10000 else 1
            dt = period_per_cycle / steps_per_cycle
            mode = "fine"

        # Clamp dt to reasonable bounds
        dt = max(1e-6, min(dt, period_per_cycle * 1000))  # Max 1000 cycles per step

        # Calculate actual number of steps
        actual_steps = int(t_end / dt)

        # Update sample percentage to reflect actual sampling
        actual_sample_pct = (n_output_points / n_cycles) * 100.0

        # In Cycles mode, push t_end to display; in Time mode, t_end is user-driven.
        in_cycles_mode = self.solver_tab.dur_cycles_radio.isChecked()

        # Update UI (block signals to avoid recursion)
        self.solver_tab.t_end_spin.blockSignals(True)
        self.solver_tab.dt_spin.blockSignals(True)
        self.solver_tab.sample_pct_spin.blockSignals(True)

        if in_cycles_mode:
            self.solver_tab.t_end_spin.setValue(t_end)
        self.solver_tab.dt_spin.setValue(dt)
        self.solver_tab.sample_pct_spin.setValue(actual_sample_pct)

        self.solver_tab.t_end_spin.blockSignals(False)
        self.solver_tab.dt_spin.blockSignals(False)
        self.solver_tab.sample_pct_spin.blockSignals(False)

        # Status update with detailed info
        self._on_status_message(
            f"Auto-calculated ({mode}): {n_cycles:,} cycles @ {frequency} Hz | "
            f"t_end={t_end:.1f}s | dt={dt:.2e}s | "
            f"{actual_steps:,} steps | {n_output_points:,} output points | "
            f"1 point per {cycles_per_output:,} cycles"
        )

    def _on_sim_mode_changed(self, cycles_checked: bool):
        """Toggle between Cycles mode and Time mode for simulation duration."""
        st = self.solver_tab
        st.sim_cycles_spin.setEnabled(cycles_checked)
        st.t_end_spin.setEnabled(not cycles_checked)
        if cycles_checked:
            # Cycles mode: recompute t_end from current cycle count
            self._auto_calculate_timestep()
        else:
            # Time mode: recompute cycles from current t_end
            self._on_t_end_changed(st.t_end_spin.value())

    def _on_t_end_changed(self, t_end: float):
        """Called when t_end changes while in Time mode; back-computes n_cycles."""
        if not self.solver_tab.dur_time_radio.isChecked():
            return
        frequency = self.solver_tab.frequency_spin.value()
        if frequency <= 0:
            return
        n_cycles = max(1, round(t_end * frequency))
        st = self.solver_tab
        st.sim_cycles_spin.blockSignals(True)
        st.n_cycles_spin.blockSignals(True)
        st.sim_cycles_spin.setValue(n_cycles)
        st.n_cycles_spin.setValue(n_cycles)
        st.sim_cycles_spin.blockSignals(False)
        st.n_cycles_spin.blockSignals(False)
        # Recalculate dt without overwriting t_end
        self._auto_calculate_timestep()

    def _get_rich_plotter_and_raw(self, cl: 'CoupledLooseningResult'):
        """
        Return (plotter, raw_results) if CoupledLooseningResultsPlotter is available
        and _raw_loosening_results is attached, else (None, None).  CRITICAL-02.
        """
        raw = getattr(cl, '_raw_loosening_results', None)
        if raw is None:
            return None, None
        try:
            from bolt_analysis_studio.visualization.loosening_plots import CoupledLooseningResultsPlotter
            return CoupledLooseningResultsPlotter(), raw
        except Exception:
            return None, None

    def _plot_coupled_loosening(self, result: CoupledLooseningResult, plot_type: str):
        """
        Plot coupled loosening analysis results.

        Args:
            result: CoupledLooseningResult from analysis
            plot_type: Type of plot - "preload", "friction", "wear", "loosening", "energy"
        """
        import numpy as np
        import matplotlib.pyplot as plt

        canvas = self.results_tab.plot_widget.canvas
        ax = canvas.axes
        ax.clear()

        BLUE = Theme.BLUE
        GREEN = Theme.GREEN
        RED = Theme.RED
        PEACH = Theme.PEACH
        YELLOW = Theme.YELLOW
        MAUVE = Theme.MAUVE
        TEAL = Theme.TEAL
        SUBTEXT = Theme.SUBTEXT

        cycles = result.cycles if result.cycles is not None else np.array([])

        if plot_type in ("preload", "Preload", "Decay"):
            # Preload ratio plot
            if result.preload_ratio is not None:
                ax.plot(cycles, np.array(result.preload_ratio) * 100, color=BLUE, linewidth=2, label='Preload %')
                ax.axhline(y=90, color=YELLOW, linestyle='--', alpha=0.7, label='90% threshold')
                ax.axhline(y=80, color=PEACH, linestyle='--', alpha=0.7, label='80% threshold')
                ax.axhline(y=50, color=RED, linestyle='--', alpha=0.7, label='50% critical')
                ax.set_ylabel('Preload Retention (%)')
                ax.set_title('Preload Loss (Coupled Friction-Wear-Loosening Model)')
                ax.set_ylim([0, 105])
                ax.legend(loc='lower left')

        elif plot_type == "friction":
            # Friction evolution
            if result.mu_thread is not None:
                ax.plot(cycles, result.mu_thread, color=MAUVE, linewidth=2, label='μ_thread')
            if result.mu_bearing is not None:
                ax.plot(cycles, result.mu_bearing, color=TEAL, linewidth=2, linestyle='--', label='μ_bearing')
            if hasattr(result, 'mu_critical') and result.mu_critical:
                ax.axhline(y=result.mu_critical, color=RED, linestyle=':', alpha=0.8, label=f'μ_crit = {result.mu_critical:.4f}')
            ax.set_ylabel('Friction Coefficient (μ)')
            ax.set_title('Friction Evolution (Three-Phase Model)')
            ax.legend()

        elif plot_type == "wear":
            # Wear depth
            if result.total_wear_um is not None:
                ax.plot(cycles, result.total_wear_um, color=PEACH, linewidth=2, label='Total Wear')
                ax.fill_between(cycles, 0, result.total_wear_um, alpha=0.3, color=PEACH)
            ax.axhline(y=10, color=YELLOW, linestyle='--', alpha=0.7, label='Light wear (10 μm)')
            ax.axhline(y=50, color=RED, linestyle='--', alpha=0.7, label='Severe wear (50 μm)')
            ax.set_ylabel('Wear Depth (μm)')
            ax.set_title('Cumulative Wear Depth (Archard Model)')
            ax.legend()

        elif plot_type == "loosening":
            # Loosening rate or torque margin
            if result.loosening_rate is not None:
                ax.plot(cycles, result.loosening_rate, color=RED, linewidth=2, label='Loosening Rate')
                ax.fill_between(cycles, 0, result.loosening_rate, alpha=0.3, color=RED)
                ax.set_ylabel('Loosening Rate (°/cycle)')
                ax.set_title('Loosening Rate Evolution')
                ax.legend()

        elif plot_type == "energy" or plot_type == "torque":
            # Torque margin
            if result.torque_margin is not None:
                ax.plot(cycles, result.torque_margin, color=BLUE, linewidth=2, label='Torque Margin')
                ax.axhline(y=1.0, color=RED, linestyle='-', linewidth=2, label='Loosening threshold')
                ax.axhline(y=1.5, color=YELLOW, linestyle='--', alpha=0.7, label='Low risk')
                ax.fill_between(cycles, 1.0, result.torque_margin,
                               where=np.array(result.torque_margin) >= 1.0,
                               alpha=0.2, color=GREEN)
                ax.fill_between(cycles, 1.0, result.torque_margin,
                               where=np.array(result.torque_margin) < 1.0,
                               alpha=0.2, color=RED)
                ax.set_ylabel('Torque Margin (T_res/T_pitch)')
                ax.set_title('Torque Balance Evolution')
                ax.legend()

        ax.set_xlabel('Number of Cycles (N)')
        ax.grid(True, alpha=0.3)
        canvas._apply_theme()
        canvas.draw()

        # Update statistics labels
        self._update_coupled_loosening_stats(result)

    def _update_coupled_loosening_stats(self, result: CoupledLooseningResult):
        """Update statistics labels for coupled loosening results."""
        stats = self.results_tab.stats_labels

        if "Final Preload" in stats:
            F_final = result.final_preload_ratio * result.initial_preload / 1000
            stats["Final Preload"].setText(f"{F_final:.2f} kN")

        if "Preload Loss" in stats:
            loss = (1 - result.final_preload_ratio) * 100
            stats["Preload Loss"].setText(f"{loss:.1f} %")

        if "Max Displacement" in stats:
            stats["Max Displacement"].setText(f"{result.total_loosening_deg:.2f}°")

        if "Min Safety Factor" in stats:
            # Use torque margin as safety indicator
            if result.torque_margin is not None:
                import numpy as np
                min_margin = np.min(result.torque_margin)
                stats["Min Safety Factor"].setText(f"{min_margin:.2f}")

        # Phase E: Miner's rule damage — read from _raw_loosening_results (LooseningResults)
        raw = getattr(result, '_raw_loosening_results', None)
        if raw is not None:
            if "Miner's Damage" in stats:
                d = getattr(raw, 'miner_damage_final', 0.0)
                color = Theme.RED if d >= 1.0 else (Theme.YELLOW if d >= 0.5 else Theme.GREEN)
                stats["Miner's Damage"].setText(f"{d:.4f}")
                stats["Miner's Damage"].setStyleSheet(
                    f"color: {color}; font-family: {Theme.FONT_MONO}; font-size: 9pt;")
            if "Fatigue Life" in stats:
                cyc = getattr(raw, 'cycles_to_failure_miner', 0)
                if cyc > 0:
                    stats["Fatigue Life"].setText(f"{cyc:,} cycles")
                    stats["Fatigue Life"].setStyleSheet(
                        f"color: {Theme.RED}; font-family: {Theme.FONT_MONO}; font-size: 9pt;")
                else:
                    stats["Fatigue Life"].setText("∞ (D < 1)")
                    stats["Fatigue Life"].setStyleSheet(
                        f"color: {Theme.GREEN}; font-family: {Theme.FONT_MONO}; font-size: 9pt;")

            # §6.7 Self-Locking Margin — SL = (µ·cos α − tan λ) / tan λ at final cycle
            if "Self-Lock Margin" in stats:
                try:
                    import numpy as _np
                    mu_final = float(raw.mu_thread[-1]) if getattr(raw, 'mu_thread', None) is not None and len(raw.mu_thread) else 0.12
                    analyzer = getattr(result, '_analyzer', None)
                    if analyzer is not None and hasattr(analyzer, 'thread'):
                        lam = float(getattr(analyzer.thread, 'helix_angle', 0.05))
                        alpha_flank = float(getattr(analyzer.thread, 'flank_angle', _np.radians(30.0)))
                    else:
                        lam, alpha_flank = 0.05, _np.radians(30.0)
                    tan_lam = max(_np.tan(lam), 1e-6)
                    sl = (mu_final * _np.cos(alpha_flank) - tan_lam) / tan_lam
                    color = Theme.RED if sl < 0.1 else (Theme.YELLOW if sl < 0.5 else Theme.GREEN)
                    stats["Self-Lock Margin"].setText(f"{sl:+.2f}")
                    stats["Self-Lock Margin"].setStyleSheet(
                        f"color: {color}; font-family: {Theme.FONT_MONO}; font-size: 9pt;")
                except Exception:
                    pass

        # §2.4 / §4.6 / §6.7 — populate Diagnostics tab with fretting map,
        # SL-margin history, and combined-loading interaction diagram.
        self._update_diagnostics_tab(result)

    def _update_diagnostics_tab(self, result: 'CoupledLooseningResult'):
        """Render the three diagnostic plots on the Results > Diagnostics tab."""
        axes = getattr(self.results_tab, 'adv_axes', None)
        canvas = getattr(self.results_tab, 'adv_canvas_widget', None)
        if axes is None or canvas is None or len(axes) < 3:
            return
        raw = getattr(result, '_raw_loosening_results', None)
        analyzer = getattr(result, '_analyzer', None)
        if raw is None:
            return
        try:
            from bolt_analysis_studio.visualization.loosening_plots import (
                plot_fretting_regime_map,
                plot_self_locking_margin,
                plot_interaction_diagram,
            )
            for ax in axes:
                ax.clear()
            plot_fretting_regime_map(raw, analyzer=analyzer, ax=axes[0])
            plot_self_locking_margin(raw, analyzer=analyzer, ax=axes[1])
            # Interaction diagram uses final-cycle operating point
            import numpy as _np
            mu_final = float(raw.mu_thread[-1]) if getattr(raw, 'mu_thread', None) is not None and len(raw.mu_thread) else 0.12
            F0 = float(result.initial_preload)
            F_trans = float(getattr(result, 'transverse_force', 0.0) or 0.0)
            F_axial_op = float(getattr(analyzer, 'axial_force_amplitude_N', 0.0)) if analyzer is not None else 0.0
            plot_interaction_diagram(
                F_transverse=F_trans,
                F_preload=F0 * float(raw.preload[-1] / raw.preload[0]) if raw.preload.size else F0,
                mu=mu_final,
                F_axial_op=F_axial_op,
                ax=axes[2],
            )
            canvas.draw()
        except Exception as e:
            # Best-effort: don't block results update if plotting fails
            try:
                for ax in axes:
                    ax.clear()
                axes[0].text(0.5, 0.5, f"Diagnostics unavailable:\n{e}",
                             ha='center', va='center', transform=axes[0].transAxes,
                             fontsize=9, color='red')
                canvas.draw()
            except Exception:
                pass

    def _generate_plots(self):
        """Generate ALL plots for current results in the embedded results tab."""
        self._show_dashboard()

    def _show_dashboard(self):
        """Show all plots in a dashboard view."""
        if self.app_state.results is None:
            QMessageBox.warning(self, "No Results", "Run an analysis first to generate plots.")
            return

        results = self.app_state.results
        self._show_embedded_dashboard(results)

    def _export_plot(self, format_type: str):
        """Export current plot to file."""
        if self.results_tab.plot_stack.currentIndex() == 0:
            QMessageBox.warning(self, "No Plot", "No plot to export. Select a plot first.")
            return

        # File format filters
        filters = {
            "png": "PNG Image (*.png)",
            "pdf": "PDF Document (*.pdf)",
            "svg": "SVG Vector (*.svg)"
        }

        filepath, _ = QFileDialog.getSaveFileName(
            self, f"Export Plot as {format_type.upper()}",
            f"plot.{format_type}",
            filters.get(format_type, "All Files (*)")
        )

        if filepath:
            try:
                # Get DPI based on format
                dpi = 300 if format_type in ("png", "pdf") else 150

                # Save the figure
                fig = self.results_tab.plot_widget.canvas.figure
                fig.savefig(filepath, dpi=dpi, bbox_inches='tight',
                           facecolor=fig.get_facecolor(), edgecolor='none')

                self._on_status_message(f"Exported plot to {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export plot:\n{e}")

    def _export_plot_with_options(self):
        """Show format+DPI dialog then export current plot (3.2)."""
        if self.results_tab.plot_stack.currentIndex() == 0:
            QMessageBox.warning(self, "No Plot", "No plot to export. Select a plot first.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Export Plot")
        dialog.setMinimumWidth(280)
        dlg_layout = QVBoxLayout(dialog)
        form = QFormLayout()

        fmt_combo = QComboBox()
        fmt_combo.addItems(["PNG (raster)", "SVG (vector)", "PDF (vector)"])
        form.addRow("Format:", fmt_combo)

        dpi_combo = QComboBox()
        dpi_combo.addItems(["72", "96", "150", "300"])
        dpi_combo.setCurrentText("150")
        dpi_combo.setEnabled(True)

        def _toggle_dpi(idx):
            # DPI not relevant for SVG/PDF vector formats
            dpi_combo.setEnabled(fmt_combo.currentText().startswith("PNG"))

        fmt_combo.currentIndexChanged.connect(_toggle_dpi)
        form.addRow("DPI (PNG only):", dpi_combo)
        dlg_layout.addLayout(form)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dialog.accept)
        btns.rejected.connect(dialog.reject)
        dlg_layout.addWidget(btns)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        fmt_text = fmt_combo.currentText()
        if fmt_text.startswith("PNG"):
            ext, fmt = "png", "png"
            dpi = int(dpi_combo.currentText())
        elif fmt_text.startswith("SVG"):
            ext, fmt, dpi = "svg", "svg", 150
        else:
            ext, fmt, dpi = "pdf", "pdf", 300

        filepath, _ = QFileDialog.getSaveFileName(
            self, f"Export Plot as {ext.upper()}",
            f"plot.{ext}",
            f"{ext.upper()} Files (*.{ext})"
        )
        if filepath:
            try:
                fig = self.results_tab.plot_widget.canvas.figure
                fig.savefig(filepath, format=fmt, dpi=dpi,
                            bbox_inches='tight',
                            facecolor=fig.get_facecolor(), edgecolor='none')
                self._on_status_message(f"Exported {fmt.upper()} to {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export:\n{e}")

    def _export_plot_data_csv(self):
        """Export current plot data to CSV."""
        if self.app_state.results is None:
            QMessageBox.warning(self, "No Results", "No data to export.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Plot Data as CSV",
            "plot_data.csv",
            "CSV Files (*.csv);;All Files (*)"
        )

        if filepath:
            try:
                import csv
                results = self.app_state.results

                with open(filepath, 'w', newline='') as f:
                    writer = csv.writer(f)

                    # Export coupled loosening data if available
                    if results.coupled_loosening_result:
                        cl = results.coupled_loosening_result
                        writer.writerow(['Cycle', 'Preload_Ratio', 'Mu_Thread', 'Mu_Bearing',
                                        'Wear_um', 'Loosening_deg', 'Loosening_Rate', 'Torque_Margin'])

                        for i, cycle in enumerate(cl.cycles):
                            row = [
                                cycle,
                                cl.preload_ratio[i] if cl.preload_ratio is not None else '',
                                cl.mu_thread[i] if cl.mu_thread is not None else '',
                                cl.mu_bearing[i] if cl.mu_bearing is not None else '',
                                cl.total_wear_um[i] if cl.total_wear_um is not None else '',
                                cl.loosening_angle_deg[i] if cl.loosening_angle_deg is not None else '',
                                cl.loosening_rate[i] if cl.loosening_rate is not None else '',
                                cl.torque_margin[i] if cl.torque_margin is not None else ''
                            ]
                            writer.writerow(row)

                self._on_status_message(f"Exported data to {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export data:\n{e}")

    def _open_plot_in_editor(self):
        """Open current plot in a separate editor window."""
        if not self.results_tab.current_plot_type:
            QMessageBox.warning(
                self, "No Plot",
                "Please select a plot from the list first."
            )
            return

        if not self.app_state.results:
            QMessageBox.warning(
                self, "No Results",
                "No analysis results available. Run an analysis first."
            )
            return

        # Get the current figure from the plot widget
        fig = self.results_tab.plot_widget.figure
        title = self.results_tab.current_plot_type or "Plot"

        # Create editor window
        editor = PlotEditorWindow(figure=fig, title=title, parent=None)
        editor.show()

        # Store reference to prevent garbage collection
        self._plot_editor_windows.append(editor)

        # Clean up closed windows when new ones open
        self._plot_editor_windows = [w for w in self._plot_editor_windows if w.isVisible()]

        self._on_status_message(f"Opened '{title}' in editor window")

    def _refresh_current_plot(self):
        """Refresh current plot with new settings."""
        if self.results_tab.current_plot_type and self.app_state.results:
            # Re-trigger the plot with current settings
            self._plot_with_settings(self.results_tab.current_plot_type)

    def _get_plot_colors(self):
        """Get color scheme from current theme."""
        return {
            'primary': Theme.BLUE,
            'secondary': Theme.GREEN,
            'accent': Theme.RED,
            'warning': Theme.PEACH,
            'highlight': Theme.YELLOW,
            'purple': Theme.MAUVE,
            'teal': Theme.TEAL,
            'text': Theme.TEXT,
            'bg': Theme.SURFACE0
        }

    def _plot_with_settings(self, plot_type: str):
        """Plot with current settings applied."""
        if self.app_state.results is None:
            return

        # Get settings (defaults)
        colors = self._get_plot_colors()
        show_grid = True
        show_legend = True
        linewidth = 2.0
        fontsize = 10

        # Store current plot type and update label
        self.results_tab.current_plot_type = plot_type
        self.results_tab.current_plot_label.setText(f"Current: {plot_type}")

        # Call appropriate plot function
        results = self.app_state.results

        # Dispatch to appropriate plot method
        if plot_type == "Clamped Force Decay":
            if results.coupled_loosening_result:
                self._plot_coupled_loosening(results.coupled_loosening_result, "preload")
        elif plot_type == "Friction Evolution":
            if results.coupled_loosening_result:
                self._plot_coupled_loosening(results.coupled_loosening_result, "friction")
        elif plot_type == "Wear Accumulation":
            if results.coupled_loosening_result:
                self._plot_coupled_loosening(results.coupled_loosening_result, "wear")
        elif plot_type == "Loosening Rate":
            if results.coupled_loosening_result:
                self._plot_coupled_loosening(results.coupled_loosening_result, "loosening")
        elif plot_type == "Torque Margin":
            if results.coupled_loosening_result:
                self._plot_coupled_loosening(results.coupled_loosening_result, "torque")
        elif plot_type == "Stage Analysis":
            if results.coupled_loosening_result:
                overlay_text = self.results_tab.stage_overlay_combo.currentText()
                self._plot_stage_analysis_animated(
                    results.coupled_loosening_result, overlay_text)
        elif plot_type == "Torque Balance":
            if results.coupled_loosening_result:
                self._plot_torque_balance(results.coupled_loosening_result)
        elif plot_type == "Cumulative Angle":
            if results.coupled_loosening_result:
                self._plot_cumulative_angle(results.coupled_loosening_result)
        elif plot_type == "Mechanism Decomposition":
            self._plot_mechanism_decomposition(results)
        elif plot_type == "Friction-Wear Correlation":
            if results.coupled_loosening_result:
                self._plot_friction_wear_correlation(results.coupled_loosening_result)
        elif plot_type == "VDI Joint Diagram":
            self._plot_vdi_joint_diagram(results)
        elif plot_type == "Joint Forces Diagram":
            if results.coupled_loosening_result:
                self._plot_joint_forces(results.coupled_loosening_result)
        elif plot_type == "Contact Forces":
            if results.coupled_loosening_result:
                self._plot_contact_forces(results.coupled_loosening_result)
        elif plot_type == "Phase Diagram":
            if results.coupled_loosening_result:
                self._plot_phase_diagram(results.coupled_loosening_result)
        elif plot_type == "Preload vs Time":
            self._plot_preload_vs_time(results)
        elif plot_type == "Preload Loss Models":
            if results.coupled_loosening_result:
                self._plot_preload_models_overlay(results.coupled_loosening_result)
            elif results.preload_result:
                PlotManager.plot_preload_loss(
                    self.results_tab.plot_widget,
                    results.preload_result.cycles,
                    results.preload_result.results
                )
        elif plot_type == "Displacement":
            if results.time_result and results.time_result.displacement is not None:
                PlotManager.plot_displacement(
                    self.results_tab.plot_widget,
                    results.time_result.time,
                    results.time_result.displacement
                )
            else:
                self._plot_excitation_proxy("Displacement", "m")
        elif plot_type == "Velocity":
            if results.time_result and results.time_result.velocity is not None:
                PlotManager.plot_velocity(
                    self.results_tab.plot_widget,
                    results.time_result.time,
                    results.time_result.velocity
                )
            else:
                self._plot_excitation_proxy("Velocity", "m/s")
        elif plot_type == "Acceleration":
            if results.time_result and results.time_result.acceleration is not None:
                PlotManager.plot_acceleration(
                    self.results_tab.plot_widget,
                    results.time_result.time,
                    results.time_result.acceleration
                )
            else:
                self._plot_excitation_proxy("Acceleration", "m/s²")
        elif plot_type == "Mode Shapes":
            if results.natural_frequencies:
                self._plot_mode_shapes(results)
            else:
                self._plot_no_data("Mode Shapes",
                                   "No modal data available.\nRun a Modal Analysis first.")
        elif plot_type == "Campbell Diagram":
            if results.natural_frequencies:
                self._plot_campbell_diagram(results)
            else:
                self._plot_no_data("Campbell Diagram",
                                   "No modal data available.\nRun a Modal Analysis first.")

        # Apply settings to the plot
        canvas = self.results_tab.plot_widget.canvas
        ax = canvas.axes

        # Apply grid setting
        ax.grid(show_grid, alpha=0.3)

        # Apply legend setting
        if not show_legend:
            legend = ax.get_legend()
            if legend:
                legend.set_visible(False)

        # Apply font size
        ax.title.set_fontsize(fontsize + 2)
        ax.xaxis.label.set_fontsize(fontsize)
        ax.yaxis.label.set_fontsize(fontsize)
        ax.tick_params(labelsize=fontsize - 1)

        canvas.draw()

    def _show_comprehensive_dashboard(self, results):
        """Bug 6 fix: dead code removed; delegate to embedded dashboard."""
        self._show_embedded_dashboard(results)

    def _show_embedded_dashboard(self, results):
        """
        Show comprehensive 3x3 dashboard embedded in the results tab.
        No separate window - all plots in the GUI.
        Uses CoupledLooseningResultsPlotter when raw results are available (CRITICAL-02).
        """
        import numpy as np
        from matplotlib.figure import Figure
        from matplotlib.gridspec import GridSpec

        # CRITICAL-02: Try rich plotter first when raw LooseningResults are available
        cl = getattr(results, 'coupled_loosening_result', None)
        plotter, raw = self._get_rich_plotter_and_raw(cl) if cl else (None, None)
        if plotter is not None and raw is not None:
            try:
                rich_fig = plotter.plot_comprehensive_dashboard(raw)
                canvas = self.results_tab.plot_widget.canvas
                # Replace the canvas figure with the rich plotter's figure
                canvas.figure.clear()
                for ax in rich_fig.get_axes():
                    rich_fig.delaxes(ax)
                    canvas.figure.add_axes(ax)
                canvas.figure.set_facecolor(rich_fig.get_facecolor())
                canvas.draw()
                self.results_tab.plot_stack.setCurrentIndex(1)
                return
            except Exception:
                pass  # Fall through to inline dashboard

        # Get the canvas and create a new figure
        canvas = self.results_tab.plot_widget.canvas
        fig = canvas.figure
        fig.clear()

        BLUE = Theme.BLUE
        GREEN = Theme.GREEN
        RED = Theme.RED
        PEACH = Theme.PEACH
        YELLOW = Theme.YELLOW
        MAUVE = Theme.MAUVE
        TEAL = Theme.TEAL
        TEXT = Theme.TEXT
        SURFACE = Theme.SURFACE0

        # Create 3x3 grid
        gs = GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.35)

        # =====================================================================
        # ROW 1: Preload and Friction
        # =====================================================================

        # Plot 1: Clamped Force Decay (Preload Loss)
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.set_facecolor(SURFACE)
        if results.coupled_loosening_result and results.coupled_loosening_result.preload_ratio is not None:
            cl = results.coupled_loosening_result
            ax1.plot(cl.cycles, np.array(cl.preload_ratio) * 100, color=BLUE, linewidth=2)
            ax1.axhline(y=90, color=YELLOW, linestyle='--', alpha=0.7, linewidth=1)
            ax1.axhline(y=80, color=PEACH, linestyle='--', alpha=0.7, linewidth=1)
            ax1.fill_between(cl.cycles, 0, np.array(cl.preload_ratio) * 100, alpha=0.2, color=BLUE)
            ax1.set_ylim([0, 105])
        ax1.set_xlabel('Cycles', fontsize=8, color=TEXT)
        ax1.set_ylabel('Preload %', fontsize=8, color=TEXT)
        ax1.set_title('Clamped Force Decay', fontsize=9, color=TEXT, fontweight='bold')
        ax1.tick_params(labelsize=7, colors=TEXT)
        ax1.grid(True, alpha=0.3)

        # Plot 2: Friction Evolution (per contact)
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.set_facecolor(SURFACE)
        if results.coupled_loosening_result and results.coupled_loosening_result.mu_thread is not None:
            cl = results.coupled_loosening_result
            ax2.plot(cl.cycles, cl.mu_thread, color=MAUVE, linewidth=2, label='Thread')
            ax2.plot(cl.cycles, cl.mu_bearing, color=TEAL, linewidth=2, linestyle='--', label='Bearing')
            if hasattr(cl, 'mu_critical') and cl.mu_critical:
                ax2.axhline(y=cl.mu_critical, color=RED, linestyle=':', alpha=0.8, linewidth=1)
            ax2.legend(fontsize=6, loc='upper right')
        ax2.set_xlabel('Cycles', fontsize=8, color=TEXT)
        ax2.set_ylabel('Friction (mu)', fontsize=8, color=TEXT)
        ax2.set_title('Friction Evolution', fontsize=9, color=TEXT, fontweight='bold')
        ax2.tick_params(labelsize=7, colors=TEXT)
        ax2.grid(True, alpha=0.3)

        # Plot 3: Wear Accumulation
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.set_facecolor(SURFACE)
        if results.coupled_loosening_result and results.coupled_loosening_result.total_wear_um is not None:
            cl = results.coupled_loosening_result
            ax3.plot(cl.cycles, cl.total_wear_um, color=PEACH, linewidth=2)
            ax3.fill_between(cl.cycles, 0, cl.total_wear_um, alpha=0.3, color=PEACH)
            ax3.axhline(y=10, color=YELLOW, linestyle='--', alpha=0.7, linewidth=1)
            ax3.axhline(y=50, color=RED, linestyle='--', alpha=0.7, linewidth=1)
        ax3.set_xlabel('Cycles', fontsize=8, color=TEXT)
        ax3.set_ylabel('Wear (um)', fontsize=8, color=TEXT)
        ax3.set_title('Wear Accumulation', fontsize=9, color=TEXT, fontweight='bold')
        ax3.tick_params(labelsize=7, colors=TEXT)
        ax3.grid(True, alpha=0.3)

        # =====================================================================
        # ROW 2: Loosening Mechanics
        # =====================================================================

        # Plot 4: Loosening Rate
        ax4 = fig.add_subplot(gs[1, 0])
        ax4.set_facecolor(SURFACE)
        if results.coupled_loosening_result and results.coupled_loosening_result.loosening_rate is not None:
            cl = results.coupled_loosening_result
            rate = np.array(cl.loosening_rate)
            ax4.plot(cl.cycles, rate, color=RED, linewidth=2)
            ax4.fill_between(cl.cycles, 0, rate, alpha=0.3, color=RED)
            if np.max(rate) > 0:
                max_idx = np.argmax(rate)
                ax4.plot(cl.cycles[max_idx], rate[max_idx], 'o', color=YELLOW, markersize=6)
        ax4.set_xlabel('Cycles', fontsize=8, color=TEXT)
        ax4.set_ylabel('Rate (deg/cyc)', fontsize=8, color=TEXT)
        ax4.set_title('Loosening Rate', fontsize=9, color=RED, fontweight='bold')
        ax4.tick_params(labelsize=7, colors=TEXT)
        ax4.grid(True, alpha=0.3)

        # Plot 5: Torque Balance
        ax5 = fig.add_subplot(gs[1, 1])
        ax5.set_facecolor(SURFACE)
        if results.coupled_loosening_result:
            cl = results.coupled_loosening_result
            if cl.states and len(cl.states) > 0:
                cycles_st = np.array([s.cycle for s in cl.states])
                T_pitch = np.array([s.T_pitch for s in cl.states])
                T_res = np.array([s.T_resistance for s in cl.states])
                ax5.plot(cycles_st, T_pitch, color=RED, linewidth=2, label='T_pitch')
                ax5.plot(cycles_st, T_res, color=GREEN, linewidth=2, label='T_resist')
                ax5.fill_between(cycles_st, T_pitch, T_res, where=T_res >= T_pitch, alpha=0.2, color=GREEN)
                ax5.fill_between(cycles_st, T_pitch, T_res, where=T_res < T_pitch, alpha=0.2, color=RED)
                ax5.legend(fontsize=6, loc='upper right')
            elif cl.torque_margin is not None:
                # Fallback: estimate torques from margin
                ax5.plot(cl.cycles, cl.torque_margin, color=BLUE, linewidth=2, label='Torque Margin')
                ax5.axhline(y=1.0, color=RED, linestyle='--', linewidth=1)
                ax5.legend(fontsize=6)
        ax5.set_xlabel('Cycles', fontsize=8, color=TEXT)
        ax5.set_ylabel('Torque (N.m)', fontsize=8, color=TEXT)
        ax5.set_title('Torque Balance', fontsize=9, color=TEXT, fontweight='bold')
        ax5.tick_params(labelsize=7, colors=TEXT)
        ax5.grid(True, alpha=0.3)

        # Plot 6: Torque Margin
        ax6 = fig.add_subplot(gs[1, 2])
        ax6.set_facecolor(SURFACE)
        if results.coupled_loosening_result and results.coupled_loosening_result.torque_margin is not None:
            cl = results.coupled_loosening_result
            margin = np.array(cl.torque_margin)
            ax6.plot(cl.cycles, margin, color=BLUE, linewidth=2)
            ax6.axhline(y=1.0, color=RED, linestyle='-', linewidth=2)
            ax6.fill_between(cl.cycles, 1.0, margin, where=margin >= 1.0, alpha=0.2, color=GREEN)
            ax6.fill_between(cl.cycles, 1.0, margin, where=margin < 1.0, alpha=0.2, color=RED)
        ax6.set_xlabel('Cycles', fontsize=8, color=TEXT)
        ax6.set_ylabel('Margin', fontsize=8, color=TEXT)
        ax6.set_title('Torque Margin', fontsize=9, color=TEXT, fontweight='bold')
        ax6.tick_params(labelsize=7, colors=TEXT)
        ax6.grid(True, alpha=0.3)

        # =====================================================================
        # ROW 3: Correlations and Summary
        # =====================================================================

        # Plot 7: Friction vs Wear Correlation
        ax7 = fig.add_subplot(gs[2, 0])
        ax7.set_facecolor(SURFACE)
        if results.coupled_loosening_result and results.coupled_loosening_result.mu_thread is not None:
            cl = results.coupled_loosening_result
            mu = np.array(cl.mu_thread)
            wear = np.array(cl.total_wear_um) if cl.total_wear_um is not None else np.zeros_like(mu)
            cycles = cl.cycles
            scatter = ax7.scatter(wear, mu, c=cycles, cmap='viridis', s=15, alpha=0.7)
            ax7.set_xlabel('Wear (um)', fontsize=8, color=TEXT)
            ax7.set_ylabel('Friction (mu)', fontsize=8, color=TEXT)
            # Fit line
            if len(wear) > 2 and np.std(wear) > 0:
                z = np.polyfit(wear, mu, 1)
                p = np.poly1d(z)
                ax7.plot(wear, p(wear), '--', color=YELLOW, linewidth=1.5, alpha=0.8)
        ax7.set_title('Friction vs Wear', fontsize=9, color=TEXT, fontweight='bold')
        ax7.tick_params(labelsize=7, colors=TEXT)
        ax7.grid(True, alpha=0.3)

        # Plot 8: Joint Forces Diagram (Preload Distribution)
        ax8 = fig.add_subplot(gs[2, 1])
        ax8.set_facecolor(SURFACE)
        if results.coupled_loosening_result:
            cl = results.coupled_loosening_result
            # Show force flow through joint
            components = ['Bolt Head', 'Washer', 'Flange 1', 'Gasket', 'Flange 2', 'Washer', 'Nut']
            y_pos = np.arange(len(components))
            F_initial = cl.initial_preload / 1000 if hasattr(cl, 'initial_preload') else 50
            F_final = cl.final_preload_ratio * F_initial if hasattr(cl, 'final_preload_ratio') else F_initial * 0.8
            forces_initial = np.array([F_initial] * len(components))
            forces_final = np.array([F_final] * len(components))

            ax8.barh(y_pos - 0.15, forces_initial, 0.3, color=BLUE, alpha=0.7, label='Initial')
            ax8.barh(y_pos + 0.15, forces_final, 0.3, color=PEACH, alpha=0.7, label='Final')
            ax8.set_yticks(y_pos)
            ax8.set_yticklabels(components, fontsize=7)
            ax8.legend(fontsize=6, loc='lower right')
        ax8.set_xlabel('Force (kN)', fontsize=8, color=TEXT)
        ax8.set_title('Joint Forces', fontsize=9, color=TEXT, fontweight='bold')
        ax8.tick_params(labelsize=7, colors=TEXT)
        ax8.grid(True, alpha=0.3, axis='x')

        # Plot 9: Cumulative Loosening Angle
        ax9 = fig.add_subplot(gs[2, 2])
        ax9.set_facecolor(SURFACE)
        if results.coupled_loosening_result and results.coupled_loosening_result.loosening_angle_deg is not None:
            cl = results.coupled_loosening_result
            ax9.plot(cl.cycles, cl.loosening_angle_deg, color=PEACH, linewidth=2)
            ax9.fill_between(cl.cycles, 0, cl.loosening_angle_deg, alpha=0.3, color=PEACH)
            # Add phase regions if available
            if cl.states and len(cl.states) > 1:
                from matplotlib.patches import Patch
                phase_colors = {'stable': GREEN, 'non_rotational': BLUE, 'transition': YELLOW,
                               'rotational': PEACH, 'runaway': RED}
                for i, s in enumerate(cl.states[:-1]):
                    c1, c2 = s.cycle, cl.states[i+1].cycle
                    phase_val = s.phase.value if hasattr(s.phase, 'value') else str(s.phase)
                    phase_color = phase_colors.get(phase_val, SURFACE)
                    ax9.axvspan(c1, c2, alpha=0.15, color=phase_color)
        ax9.set_xlabel('Cycles', fontsize=8, color=TEXT)
        ax9.set_ylabel('Angle (deg)', fontsize=8, color=TEXT)
        ax9.set_title('Cumulative Loosening', fontsize=9, color=TEXT, fontweight='bold')
        ax9.tick_params(labelsize=7, colors=TEXT)
        ax9.grid(True, alpha=0.3)

        # Apply theme and draw
        fig.set_facecolor(Theme.BASE)
        try:
            fig.tight_layout(pad=1.5)
        except Exception:
            pass  # tight_layout can fail on complex GridSpec layouts
        canvas.draw()
        self.results_tab.plot_stack.setCurrentIndex(1)

        # Update statistics
        if results.coupled_loosening_result:
            self._update_coupled_loosening_stats(results.coupled_loosening_result)

        self._on_status_message("Generated 9-panel embedded dashboard")

    def _pin_results(self):
        """Pin a snapshot of current results for comparison (3.1)."""
        if not self.app_state.has_results():
            QMessageBox.warning(self, "No Results", "Run an analysis first.")
            return
        success = self.app_state.pin_results()
        if success:
            n = len(self.app_state.pinned_results)
            self.results_tab.pin_count_label.setText(f"Pins: {n}/5")
            self._on_status_message(f"Pinned results snapshot {n}/5")
        else:
            QMessageBox.information(
                self, "Pin Limit Reached",
                "Maximum of 5 pinned snapshots reached. Clear pins first."
            )

    def _clear_pinned_results(self):
        """Clear all pinned result snapshots (3.1)."""
        self.app_state.clear_pinned()
        self.results_tab.pin_count_label.setText("Pins: 0/5")
        self._on_status_message("Cleared all pinned result snapshots")

    def _export_results(self):
        """Export results to CSV."""
        if self.app_state.results is None:
            QMessageBox.warning(self, "No Results", "No results to export.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Results",
            "results.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        if filepath:
            success = ProjectIO.export_results_csv(filepath, self.app_state.results)
            if success:
                self._on_status_message(f"Exported results to {filepath}")
            else:
                QMessageBox.warning(self, "Error", "Failed to export results")

    def _export_report(self):
        """Export a report (legacy - redirects to _generate_report)."""
        self._generate_report()

    def _update_report_preview(self):
        """Update the report preview in the Reports tab."""
        html = self._generate_report_html()
        self.reports_tab.set_preview_html(html)

    def _generate_report(self):
        """Generate and save a report based on selected options."""
        format_type = self.reports_tab.get_selected_format()
        report_type = self.reports_tab.get_report_type()

        # Generate HTML content
        html = self._generate_report_html()

        # Determine file extension and filter
        if format_type == "pdf":
            ext = "pdf"
            file_filter = "PDF Document (*.pdf)"
        elif format_type == "html":
            ext = "html"
            file_filter = "HTML Document (*.html)"
        elif format_type == "csv":
            ext = "csv"
            file_filter = "CSV File (*.csv)"
        elif format_type == "latex":
            ext = "tex"
            file_filter = "LaTeX Document (*.tex)"
        else:
            ext = "html"
            file_filter = "HTML Document (*.html)"

        # Get filename
        default_name = f"bolt_analysis_report.{ext}"
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Report",
            default_name,
            file_filter
        )

        if not filepath:
            return

        try:
            if format_type == "pdf":
                self._save_report_pdf(filepath, html)
            elif format_type == "html":
                self._save_report_html(filepath, html)
            elif format_type == "csv":
                self._save_report_csv(filepath)
            elif format_type == "latex":
                self._save_report_latex(filepath)

            self._on_status_message(f"Report saved: {filepath}")
            QMessageBox.information(self, "Report Generated", f"Report saved to:\n{filepath}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report:\n{str(e)}")

    def _generate_report_html(self) -> str:
        """Generate HTML content for the report."""
        from datetime import datetime

        sections = self.reports_tab.get_selected_sections()
        report_type = self.reports_tab.get_report_type()

        project = self.app_state.project
        model = self.app_state.model
        results = self.app_state.results

        # CSS styles for the report
        css = f"""
        <style>
            body {{ font-family: {Theme.FONT_SANS}; margin: 20px; background: {Theme.BASE}; color: {Theme.TEXT}; }}
            h1 {{ color: {Theme.BLUE}; border-bottom: 2px solid {Theme.BLUE}; padding-bottom: 10px; }}
            h2 {{ color: {Theme.GREEN}; margin-top: 20px; }}
            h3 {{ color: {Theme.YELLOW}; margin-top: 15px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th {{ background: {Theme.SURFACE0}; color: {Theme.TEXT}; padding: 8px; text-align: left; border: 1px solid {Theme.SURFACE1}; }}
            td {{ padding: 8px; border: 1px solid {Theme.SURFACE1}; }}
            tr:nth-child(even) {{ background: {Theme.MANTLE}; }}
            .highlight {{ color: {Theme.RED}; font-weight: bold; }}
            .success {{ color: {Theme.GREEN}; }}
            .warning {{ color: {Theme.YELLOW}; }}
            .info {{ color: {Theme.BLUE}; }}
            .section {{ margin: 15px 0; padding: 15px; background: {Theme.MANTLE}; border-radius: 8px; }}
            hr {{ border: none; border-top: 1px solid {Theme.SURFACE1}; margin: 20px 0; }}
        </style>
        """

        html_parts = [f"<html><head>{css}</head><body>"]

        # Header
        html_parts.append(f"<h1>Bolt Analysis Report</h1>")
        html_parts.append(f"<p><b>Report Type:</b> {report_type}</p>")
        html_parts.append(f"<p><b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        html_parts.append(f"<p><b>Standard:</b> VDI 2230 Part 1 (2015)</p>")
        html_parts.append("<hr>")

        # §5.3 — ISO 16130 / DIN 65151 specialised report
        if "ISO 16130" in report_type:
            html_parts.append(self._render_iso16130_report_body())
            html_parts.append("</body></html>")
            return "\n".join(html_parts)

        # Project Info Section
        if "Project Info" in sections and project:
            html_parts.append("<div class='section'>")
            html_parts.append("<h2>1. Project Information</h2>")
            html_parts.append(f"<p><b>Name:</b> {project.name}</p>")
            html_parts.append(f"<p><b>Description:</b> {project.description or 'N/A'}</p>")
            html_parts.append(f"<p><b>Author:</b> {project.author or 'N/A'}</p>")
            html_parts.append(f"<p><b>Company:</b> {project.company or 'N/A'}</p>")
            html_parts.append("</div>")

        # Model Section
        if "Model" in sections and model:
            html_parts.append("<div class='section'>")
            html_parts.append("<h2>2. Model Summary</h2>")
            html_parts.append("<table>")
            html_parts.append("<tr><th>Parameter</th><th>Value</th></tr>")
            html_parts.append(f"<tr><td>Model Name</td><td>{model.name}</td></tr>")
            html_parts.append(f"<tr><td>Elements</td><td>{model.n_elements}</td></tr>")
            html_parts.append(f"<tr><td>Degrees of Freedom</td><td>{model.n_dof}</td></tr>")
            html_parts.append(f"<tr><td>Equivalent Stiffness</td><td>{model.get_equivalent_stiffness():.3e} N/m</td></tr>")
            html_parts.append(f"<tr><td>Total Mass</td><td>{model.get_total_mass():.3e} kg</td></tr>")
            try:
                fn = model.get_fundamental_frequency()
                html_parts.append(f"<tr><td>Fundamental Frequency</td><td>{fn:.2f} Hz</td></tr>")
            except:
                html_parts.append(f"<tr><td>Fundamental Frequency</td><td>N/A</td></tr>")
            html_parts.append("</table>")
            html_parts.append("</div>")

        # Loading Section
        if "Loading" in sections and model:
            html_parts.append("<div class='section'>")
            html_parts.append("<h2>3. Loading Configuration</h2>")
            html_parts.append("<table>")
            html_parts.append("<tr><th>Parameter</th><th>Value</th></tr>")

            if hasattr(model, 'global_loading') and model.global_loading:
                loading = model.global_loading
                load_type = loading.type.name if hasattr(loading.type, 'name') else str(loading.type)
                html_parts.append(f"<tr><td>Load Type</td><td>{load_type}</td></tr>")
                html_parts.append(f"<tr><td>Preload (F₀)</td><td>{loading.F_preload:,.0f} N</td></tr>")
                html_parts.append(f"<tr><td>Transverse Displacement</td><td>{loading.delta_amplitude:.3f} mm</td></tr>")
                html_parts.append(f"<tr><td>Frequency</td><td>{loading.frequency:.1f} Hz</td></tr>")
                html_parts.append(f"<tr><td>Number of Cycles</td><td>{loading.n_cycles:,}</td></tr>")

            if hasattr(model, 'mu_initial'):
                html_parts.append(f"<tr><td>Initial Friction (μ)</td><td>{model.mu_initial:.3f}</td></tr>")
            if hasattr(model, 'lubricated'):
                html_parts.append(f"<tr><td>Lubricated</td><td>{'Yes' if model.lubricated else 'No'}</td></tr>")
            if hasattr(model, 'bolt_diameter'):
                html_parts.append(f"<tr><td>Bolt</td><td>M{model.bolt_diameter:.0f} × {model.pitch:.1f}</td></tr>")

            html_parts.append("</table>")
            html_parts.append("</div>")

        # Results Section
        if "Results" in sections and results:
            html_parts.append("<div class='section'>")
            html_parts.append("<h2>4. Analysis Results</h2>")

            if results.preload_result:
                pr = results.preload_result
                html_parts.append("<h3>Preload Analysis</h3>")
                html_parts.append("<table>")
                html_parts.append("<tr><th>Parameter</th><th>Value</th></tr>")
                html_parts.append(f"<tr><td>Final Preload Ratio</td><td class='highlight'>{pr.final_preload_ratio * 100:.1f}%</td></tr>")
                html_parts.append(f"<tr><td>Preload Loss</td><td class='warning'>{pr.preload_loss_percent:.2f}%</td></tr>")
                html_parts.append("</table>")

            if results.coupled_loosening_result:
                clr = results.coupled_loosening_result
                html_parts.append("<h3>Coupled Loosening Analysis</h3>")
                html_parts.append("<table>")
                html_parts.append("<tr><th>Parameter</th><th>Value</th></tr>")
                if hasattr(clr, 'cycles') and len(clr.cycles) > 0:
                    html_parts.append(f"<tr><td>Cycles Analyzed</td><td>{len(clr.cycles):,}</td></tr>")
                if hasattr(clr, 'preload') and len(clr.preload) > 0:
                    final_preload = clr.preload[-1]
                    initial_preload = clr.preload[0] if clr.preload[0] > 0 else 1
                    loss_pct = (1 - final_preload / initial_preload) * 100
                    html_parts.append(f"<tr><td>Final Preload</td><td class='highlight'>{final_preload:,.0f} N</td></tr>")
                    html_parts.append(f"<tr><td>Preload Loss</td><td class='warning'>{loss_pct:.1f}%</td></tr>")
                if hasattr(clr, 'friction') and len(clr.friction) > 0:
                    html_parts.append(f"<tr><td>Final Friction</td><td>{clr.friction[-1]:.4f}</td></tr>")
                if hasattr(clr, 'cumulative_angle') and len(clr.cumulative_angle) > 0:
                    html_parts.append(f"<tr><td>Cumulative Rotation</td><td>{clr.cumulative_angle[-1]:.2f}°</td></tr>")
                # Phase E: Miner's rule damage from _raw_loosening_results
                _raw = getattr(clr, '_raw_loosening_results', None)
                if _raw is not None:
                    _d = getattr(_raw, 'miner_damage_final', None)
                    if _d is not None:
                        _css = 'warning' if _d >= 0.5 else 'highlight'
                        html_parts.append(f"<tr><td>Miner's Damage (D)</td><td class='{_css}'>{_d:.4f}</td></tr>")
                    _cyc = getattr(_raw, 'cycles_to_failure_miner', 0)
                    if _cyc > 0:
                        html_parts.append(f"<tr><td>Cycles to Fatigue Failure</td><td class='warning'>{_cyc:,}</td></tr>")
                    else:
                        html_parts.append(f"<tr><td>Fatigue Life</td><td>Not reached (D &lt; 1)</td></tr>")
                html_parts.append("</table>")

            if results.time_result:
                tr = results.time_result
                html_parts.append("<h3>Time Integration</h3>")
                html_parts.append("<table>")
                html_parts.append("<tr><th>Parameter</th><th>Value</th></tr>")
                html_parts.append(f"<tr><td>Method</td><td>{tr.method}</td></tr>")
                html_parts.append(f"<tr><td>Time Step (dt)</td><td>{tr.dt:.6f} s</td></tr>")
                html_parts.append(f"<tr><td>End Time (t_end)</td><td>{tr.t_end:.3f} s</td></tr>")
                html_parts.append(f"<tr><td>Max Displacement</td><td>{tr.max_displacement:.3e} m</td></tr>")
                html_parts.append(f"<tr><td>Max Velocity</td><td>{tr.max_velocity:.3e} m/s</td></tr>")
                html_parts.append(f"<tr><td>Max Acceleration</td><td>{tr.max_acceleration:.3e} m/s²</td></tr>")
                html_parts.append("</table>")

            if results.natural_frequencies and len(results.natural_frequencies) > 0:
                html_parts.append("<h3>Modal Analysis</h3>")
                html_parts.append("<table>")
                html_parts.append("<tr><th>Mode</th><th>Frequency (Hz)</th><th>Period (s)</th></tr>")
                for i, freq in enumerate(results.natural_frequencies[:10]):
                    period = f"{1/freq:.4g}" if freq > 0 else "∞"
                    html_parts.append(
                        f"<tr><td>Mode {i+1}</td><td>{freq:.3f}</td><td>{period}</td></tr>")
                html_parts.append("</table>")

            html_parts.append("</div>")

        # Contacts Summary Section (6.1)
        if "Model" in sections and model and hasattr(model, 'contacts') and model.contacts:
            html_parts.append("<div class='section'>")
            html_parts.append("<h2>4b. Contact Summary</h2>")
            html_parts.append("<table>")
            html_parts.append("<tr><th>#</th><th>Contact ID</th><th>Type</th>"
                              "<th>μ static</th><th>k contact (N/m)</th></tr>")
            for idx, c in enumerate(model.contacts):
                c_id   = getattr(c, 'id', f"C{idx+1}")
                c_type = getattr(c, 'type', "—")
                try:
                    mu_s = f"{c.friction.mu_static:.3f}"
                except Exception:
                    mu_s = "—"
                try:
                    k_c = f"{c.stiffness.k_axial:.3e}"
                except Exception:
                    k_c = "—"
                html_parts.append(
                    f"<tr><td>{idx+1}</td><td>{c_id}</td><td>{c_type}</td>"
                    f"<td>{mu_s}</td><td>{k_c}</td></tr>")
            html_parts.append("</table>")
            html_parts.append("</div>")

        # Safety Factors Section
        if "Safety Factors" in sections and model:
            html_parts.append("<div class='section'>")
            html_parts.append("<h2>5. Safety Factors (VDI 2230)</h2>")
            html_parts.append("<table>")
            html_parts.append("<tr><th>Factor</th><th>Value</th><th>Status</th></tr>")

            # Calculate basic safety factors
            if hasattr(model, 'global_loading') and model.global_loading:
                preload = model.global_loading.F_preload
                if hasattr(model, 'bolt_diameter'):
                    d = model.bolt_diameter / 1000  # mm to m
                    A_s = 3.14159 / 4 * d * d * 0.7  # Approximate stress area
                    sigma = preload / A_s / 1e6  # MPa
                    sigma_y = 724  # MPa for A193 B7
                    SF_yield = sigma_y / sigma if sigma > 0 else float('inf')
                    status = "<span class='success'>OK</span>" if SF_yield > 1.2 else "<span class='warning'>Low</span>"
                    html_parts.append(f"<tr><td>Yield Safety Factor</td><td>{SF_yield:.2f}</td><td>{status}</td></tr>")

                    # Preload utilization
                    util = sigma / sigma_y * 100
                    status = "<span class='success'>OK</span>" if util < 90 else "<span class='warning'>High</span>"
                    html_parts.append(f"<tr><td>Preload Utilization</td><td>{util:.1f}%</td><td>{status}</td></tr>")

            html_parts.append("</table>")
            html_parts.append("</div>")

        # Similitude Section (CRITICAL-03 / MED-03)
        if "Similitude" in sections and self.app_state.similitude_result is not None:
            scaled = self.app_state.similitude_result
            html_parts.append("<div class='section'>")
            html_parts.append("<h2>6. Similitude Analysis</h2>")
            html_parts.append("<table>")
            html_parts.append("<tr><th>Parameter</th><th>Value</th></tr>")
            if hasattr(scaled, 'scale_factor'):
                html_parts.append(f"<tr><td>Scale Factor (λ)</td><td>{scaled.scale_factor:.3f}</td></tr>")
            if hasattr(scaled, 'prototype_diameter'):
                html_parts.append(f"<tr><td>Prototype Diameter</td><td>{scaled.prototype_diameter:.1f} mm</td></tr>")
            if hasattr(scaled, 'standard_diameter'):
                html_parts.append(f"<tr><td>Model Diameter</td><td>{scaled.standard_diameter:.1f} mm</td></tr>")
            if hasattr(scaled, 'prototype_preload'):
                html_parts.append(f"<tr><td>Prototype Preload</td><td>{scaled.prototype_preload:,.0f} N</td></tr>")
            if hasattr(scaled, 'model_preload'):
                html_parts.append(f"<tr><td>Model Preload</td><td>{scaled.model_preload:,.0f} N</td></tr>")
            if hasattr(scaled, 'prototype_frequency'):
                html_parts.append(f"<tr><td>Prototype Frequency</td><td>{scaled.prototype_frequency:.2f} Hz</td></tr>")
            if hasattr(scaled, 'model_frequency'):
                html_parts.append(f"<tr><td>Model Frequency</td><td>{scaled.model_frequency:.2f} Hz</td></tr>")
            if hasattr(scaled, 'embedding_correction'):
                html_parts.append(f"<tr><td>Embedding Correction</td><td>{scaled.embedding_correction:.4f}</td></tr>")
            html_parts.append("</table>")
            html_parts.append("</div>")

        # Loosening Section
        if "Loosening" in sections and results and results.coupled_loosening_result:
            clr = results.coupled_loosening_result
            html_parts.append("<div class='section'>")
            html_parts.append("<h2>6. Loosening Assessment</h2>")

            if hasattr(clr, 'preload') and len(clr.preload) > 1:
                initial = clr.preload[0]
                final = clr.preload[-1]
                loss_pct = (1 - final / initial) * 100 if initial > 0 else 0

                if loss_pct < 10:
                    status = "<span class='success'>LOW RISK</span>"
                    desc = "Minimal loosening observed. Joint is performing well."
                elif loss_pct < 30:
                    status = "<span class='warning'>MODERATE RISK</span>"
                    desc = "Some loosening detected. Consider monitoring or anti-loosening measures."
                else:
                    status = "<span class='highlight'>HIGH RISK</span>"
                    desc = "Significant loosening detected. Anti-loosening measures recommended."

                html_parts.append(f"<p><b>Loosening Status:</b> {status}</p>")
                html_parts.append(f"<p>{desc}</p>")
                html_parts.append(f"<p><b>Preload Retention:</b> {100-loss_pct:.1f}%</p>")

                # 6.1: VDI 2230-based recommendations for HIGH risk
                if loss_pct >= 30:
                    html_parts.append("<h3>VDI 2230 Recommendations</h3>")
                    html_parts.append("<ul>")
                    html_parts.append("<li><b>Increase preload:</b> Target 70–80% yield utilization "
                                      "to maximize friction clamping force.</li>")
                    html_parts.append("<li><b>Anti-loosening fastener:</b> Use nylon-insert nut, "
                                      "prevailing-torque nut, or Nord-Lock washers.</li>")
                    html_parts.append("<li><b>Reduce transverse displacement:</b> Design joints to "
                                      "minimise relative motion perpendicular to bolt axis.</li>")
                    html_parts.append("<li><b>Increase friction:</b> Use coarser surface finish or "
                                      "serrated flange nut. Avoid lubricating bearing surfaces.</li>")
                    html_parts.append("<li><b>Re-torque protocol:</b> Apply a re-torque after first "
                                      "operational cycle to compensate embedding losses.</li>")
                    html_parts.append("</ul>")
                elif loss_pct >= 10:
                    html_parts.append("<h3>Monitoring Recommendation</h3>")
                    html_parts.append("<p>Moderate loosening detected. Inspect and re-torque at "
                                      "scheduled maintenance intervals. Consider vibration-resistant "
                                      "locking features if excitation frequency is sustained.</p>")

            html_parts.append("</div>")

        # Footer
        html_parts.append("<hr>")
        html_parts.append(f"<p style='color: {Theme.OVERLAY}; font-size: 9pt;'>")
        html_parts.append("Generated by Bolt Analysis Studio v4.0")
        html_parts.append("</p>")

        html_parts.append("</body></html>")

        return "\n".join(html_parts)

    def _save_report_html(self, filepath: str, html: str):
        """Save report as HTML file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

    def _save_report_pdf(self, filepath: str, html: str):
        """Save report as PDF using Qt's print support."""
        from PyQt6.QtGui import QPageLayout, QPageSize
        from PyQt6.QtCore import QMarginsF

        # Create a temporary QTextDocument for printing
        doc = QTextDocument()
        doc.setHtml(html)

        # Create printer
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(filepath)

        # Set page size and margins
        page_layout = QPageLayout()
        page_layout.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        page_layout.setMargins(QMarginsF(15, 15, 15, 15))
        printer.setPageLayout(page_layout)

        # Print to PDF
        doc.print_(printer)

    def _render_iso16130_report_body(self) -> str:
        """§5.3 — DIN 65151 / ISO 16130 vibration-test report body HTML."""
        model = self.app_state.model
        results = self.app_state.results
        cl = getattr(results, 'coupled_loosening_result', None) if results else None
        raw = getattr(cl, '_raw_loosening_results', None) if cl else None
        rows = ["<h2>ISO 16130:2015 / DIN 65151 Vibration Test Report</h2>"]
        if model is None or raw is None:
            rows.append("<p class='warning'>No coupled loosening result available — run a "
                        "Junker transverse test first.</p>")
            return "\n".join(rows)

        loading = getattr(model, 'global_loading', None)
        d_mm = float(getattr(loading, 'bolt_diameter', 16.0) or 16.0) if loading else 16.0
        freq = float(getattr(loading, 'frequency', 12.5) or 12.5) if loading else 12.5
        delta = float(getattr(loading, 'delta_amplitude', 0.65) or 0.65) if loading else 0.65
        n_cyc = int(getattr(loading, 'n_cycles', 2000) or 2000) if loading else 2000
        waveform = str(getattr(loading, 'load_waveform', 'sinusoidal') or 'sinusoidal') if loading else 'sinusoidal'
        load_type = str(getattr(loading, 'type', 'transverse') or 'transverse') if loading else 'transverse'

        # ISO 16130 standard amplitudes by bolt size
        iso_amp_table = {6: 0.30, 8: 0.40, 10: 0.50, 12: 0.60, 14: 0.65, 16: 0.70}
        key = int(round(d_mm))
        iso_ref_amp = iso_amp_table.get(key, 0.70)

        # Retention at 2 000 cycles
        import numpy as _np
        F = _np.asarray(raw.preload, dtype=float)
        N = _np.asarray(raw.cycles, dtype=int)
        F0 = float(F[0]) if F.size else 0.0
        if F0 <= 0 or N.size == 0:
            rows.append("<p class='warning'>Preload history is empty.</p>")
            return "\n".join(rows)
        target = 2000 if n_cyc >= 2000 else int(N[-1])
        idx = int(_np.argmin(_np.abs(N - target)))
        retention = float(F[idx] / F0)
        passed_80 = retention >= 0.80
        passed_85 = retention >= 0.85
        verdict = ("PASS — DIN 25201-4 (80%) and ISO 16130 (85%)" if passed_85
                   else "PASS — DIN 25201-4 only (80%), below ISO 16130 85%"
                   if passed_80 else "FAIL — below 80% criterion")
        verdict_class = "success" if passed_85 else ("warning" if passed_80 else "highlight")

        # Config conformance check
        cfg_checks = []
        cfg_checks.append(("Load type is TRANSVERSE (Junker)", load_type == 'transverse'))
        cfg_checks.append((f"Frequency ≈ 12.5 Hz (found {freq:.2f} Hz)", abs(freq - 12.5) < 1.0))
        cfg_checks.append((f"ISO 16130 reference amplitude for M{key} = {iso_ref_amp:.2f} mm (found {delta:.2f} mm)",
                           abs(delta - iso_ref_amp) < 0.05))
        cfg_checks.append((f"Cycles ≥ 2000 (found {n_cyc})", n_cyc >= 2000))
        cfg_checks.append((f"Waveform (ISO 16130 = sinusoidal)", waveform.lower() in ('sinusoidal', 'sine')))

        rows.append("<div class='section'>")
        rows.append("<h3>Test Configuration</h3>")
        rows.append("<table>")
        rows.append("<tr><th>Parameter</th><th>Value</th></tr>")
        rows.append(f"<tr><td>Bolt size</td><td>M{key}</td></tr>")
        rows.append(f"<tr><td>Loading type</td><td>{load_type}</td></tr>")
        rows.append(f"<tr><td>Transverse amplitude</td><td>{delta:.3f} mm (ISO ref {iso_ref_amp:.2f})</td></tr>")
        rows.append(f"<tr><td>Frequency</td><td>{freq:.2f} Hz</td></tr>")
        rows.append(f"<tr><td>Cycles run</td><td>{n_cyc:,}</td></tr>")
        rows.append(f"<tr><td>Waveform</td><td>{waveform}</td></tr>")
        rows.append(f"<tr><td>Initial preload F₀</td><td>{F0:,.0f} N</td></tr>")
        rows.append("</table>")
        rows.append("</div>")

        rows.append("<div class='section'>")
        rows.append("<h3>Conformance with ISO 16130:2015</h3>")
        rows.append("<table><tr><th>Check</th><th>Result</th></tr>")
        for label, ok in cfg_checks:
            cls = "success" if ok else "highlight"
            rows.append(f"<tr><td>{label}</td><td class='{cls}'>{'✔ OK' if ok else '✘ mismatch'}</td></tr>")
        rows.append("</table>")
        rows.append("</div>")

        rows.append("<div class='section'>")
        rows.append("<h3>Preload Retention Result</h3>")
        rows.append("<table>")
        rows.append("<tr><th>Metric</th><th>Value</th></tr>")
        rows.append(f"<tr><td>Retention at {N[idx]:,} cycles</td><td>{retention*100:.1f} %</td></tr>")
        rows.append(f"<tr><td>Final preload</td><td>{F[idx]:,.0f} N</td></tr>")
        rows.append(f"<tr><td>Loss</td><td>{(1-retention)*100:.1f} %</td></tr>")
        rows.append(f"<tr><td>DIN 25201-4 (≥ 80%)</td>"
                    f"<td class='{'success' if passed_80 else 'highlight'}'>"
                    f"{'PASS' if passed_80 else 'FAIL'}</td></tr>")
        rows.append(f"<tr><td>ISO 16130:2015 (≥ 85%)</td>"
                    f"<td class='{'success' if passed_85 else 'highlight'}'>"
                    f"{'PASS' if passed_85 else 'FAIL'}</td></tr>")
        rows.append(f"<tr><td><b>Verdict</b></td><td class='{verdict_class}'><b>{verdict}</b></td></tr>")
        rows.append("</table>")
        rows.append("</div>")

        # Locking device comparison (Phase F)
        ld_type = int(getattr(loading, 'locking_device_type', 0) or 0) if loading else 0
        if ld_type != 0:
            rows.append("<div class='section'>")
            rows.append("<h3>Locking Device Reference (Phase F)</h3>")
            rows.append(f"<p>Configured locking device type index: {ld_type}.</p>")
            rows.append("<p>Compare the retention value above against the expected range "
                        "in <code>core/databases/locking_devices.json</code> "
                        "(Junker DIN 65151 effectiveness class A–F).</p>")
            rows.append("</div>")

        rows.append("<p class='info'><i>References: ISO 16130:2015 §4–§6; "
                    "DIN 65151 (2002); DIN 25201-4 (2010); LMQ §12.5, §13.1–13.2.</i></p>")
        return "\n".join(rows)

    def _export_cmms_csv(self):
        """§7.4 — Export a CMMS-ready CSV row for the current loosening result."""
        result = getattr(self.app_state, 'results', None)
        cl = getattr(result, 'coupled_loosening_result', None) if result else None
        raw = getattr(cl, '_raw_loosening_results', None) if cl else None
        if raw is None or not hasattr(raw, 'preload') or not hasattr(raw, 'cycles'):
            QMessageBox.warning(
                self, "No Loosening Result",
                "Run a coupled loosening analysis first — CMMS export requires "
                "a preload history."
            )
            return
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export CMMS CSV", "cmms_export.csv", "CSV files (*.csv)"
        )
        if not filepath:
            return
        try:
            from bolt_analysis_studio.io.cmms_export import (
                build_cmms_record, export_cmms_csv,
            )
            model = self.app_state.model
            loading = getattr(model, 'global_loading', None) if model else None
            freq = float(getattr(loading, 'frequency', 1.0) or 1.0)
            F0 = float(getattr(loading, 'F_preload', raw.preload[0] if raw.preload.size else 0.0))
            mu = float(getattr(loading, 'mu_initial', 0.12) or 0.12)
            d_mm = float(getattr(loading, 'bolt_diameter', 16.0) or 16.0)
            # Target retorque torque: T ≈ 0.2 · F₀ · d (ISO 898 K-factor approx)
            torque_nm = 0.2 * F0 * (d_mm / 1000.0)
            pitch = float(getattr(loading, 'pitch', 2.0) or 2.0)
            spec = f"M{int(round(d_mm))} × {pitch:.1f}"
            rec = build_cmms_record(
                equipment_id=getattr(self.app_state, 'project_name', 'EQUIPMENT-01') or 'EQUIPMENT-01',
                bolt_id="BOLT-01",
                bolt_spec=spec,
                preload_array=raw.preload,
                cycles_array=raw.cycles,
                frequency_hz=freq,
                torque_nm=torque_nm,
                threshold_ratio=0.85,
            )
            export_cmms_csv([rec], filepath)
            QMessageBox.information(
                self, "CMMS Export",
                f"Exported to:\n{filepath}\n\n"
                f"Retorque: {rec.retorque_cycles:,} cycles "
                f"({rec.retorque_hours:.1f} h) — next date {rec.next_retorque_date}"
            )
        except Exception as e:
            QMessageBox.critical(self, "CMMS Export Failed", str(e))

    def _save_report_csv(self, filepath: str):
        """
        Save report data as structured CSV files in a subfolder (6.3).
        Creates: summary.csv, cycles.csv, time_history.csv, modal.csv
        """
        import csv
        import numpy as np

        model = self.app_state.model
        results = self.app_state.results

        # --- determine output directory ---
        stem = os.path.splitext(filepath)[0]
        os.makedirs(stem, exist_ok=True)

        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # ── 1. summary.csv ──────────────────────────────────────────────────
        with open(os.path.join(stem, "summary.csv"), 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Bolt Analysis Studio — Summary"])
            writer.writerow(["Generated", ts])
            writer.writerow([])

            if model:
                writer.writerow(["MODEL SUMMARY"])
                writer.writerow(["Parameter", "Value"])
                writer.writerow(["Name", model.name])
                writer.writerow(["Elements", model.n_elements])
                writer.writerow(["DOF", model.n_dof])
                writer.writerow(["k_eq (N/m)", f"{model.get_equivalent_stiffness():.6e}"])
                writer.writerow(["m_total (kg)", f"{model.get_total_mass():.6e}"])
                writer.writerow([])

            if model and hasattr(model, 'global_loading') and model.global_loading:
                loading = model.global_loading
                writer.writerow(["LOADING CONFIGURATION"])
                writer.writerow(["Parameter", "Value"])
                writer.writerow(["Preload (N)", loading.F_preload])
                writer.writerow(["Trans. Disp (mm)", loading.delta_amplitude])
                writer.writerow(["Frequency (Hz)", loading.frequency])
                writer.writerow(["Cycles", loading.n_cycles])
                if hasattr(model, 'mu_initial'):
                    writer.writerow(["Friction mu", model.mu_initial])
                if hasattr(model, 'bolt_diameter'):
                    writer.writerow(["Bolt", f"M{model.bolt_diameter} x {getattr(model, 'pitch', '?')}"])
                writer.writerow([])

            if results:
                if results.preload_result:
                    pr = results.preload_result
                    writer.writerow(["PRELOAD ANALYSIS"])
                    writer.writerow(["Parameter", "Value"])
                    writer.writerow(["Final Preload Ratio", f"{pr.final_preload_ratio:.4f}"])
                    writer.writerow(["Preload Loss (%)", f"{pr.preload_loss_percent:.2f}"])
                    writer.writerow([])

                if results.coupled_loosening_result:
                    clr = results.coupled_loosening_result
                    writer.writerow(["LOOSENING SUMMARY"])
                    writer.writerow(["Parameter", "Value"])
                    writer.writerow(["Final Preload Ratio", f"{clr.final_preload_ratio:.4f}"])
                    writer.writerow(["Total Loosening (deg)", f"{clr.total_loosening_deg:.4f}"])
                    writer.writerow(["Cycles to 50% Loss",
                                     clr.cycles_to_50_percent if clr.cycles_to_50_percent > 0 else "N/A"])
                    writer.writerow(["Max Loosening Rate (deg/cycle)", f"{clr.max_loosening_rate:.6f}"])
                    writer.writerow([])

        # ── 2. cycles.csv ───────────────────────────────────────────────────
        if results and results.coupled_loosening_result:
            clr = results.coupled_loosening_result
            n_pts = len(clr.cycles) if hasattr(clr, 'cycles') else 0
            if n_pts > 0:
                with open(os.path.join(stem, "cycles.csv"), 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["cycle", "preload_N", "preload_ratio",
                                     "mu_thread", "mu_bearing",
                                     "wear_depth_um", "loosening_angle_deg",
                                     "loosening_rate_deg_per_cycle",
                                     "torque_margin", "friction_margin"])
                    for i in range(n_pts):
                        writer.writerow([
                            int(clr.cycles[i]),
                            f"{clr.preload[i]:.2f}" if hasattr(clr, 'preload') else "",
                            f"{clr.preload_ratio[i]:.6f}" if hasattr(clr, 'preload_ratio') else "",
                            f"{clr.mu_thread[i]:.6f}" if hasattr(clr, 'mu_thread') else "",
                            f"{clr.mu_bearing[i]:.6f}" if hasattr(clr, 'mu_bearing') else "",
                            f"{clr.total_wear_um[i]:.6f}" if hasattr(clr, 'total_wear_um') else "",
                            f"{clr.loosening_angle_deg[i]:.6f}" if hasattr(clr, 'loosening_angle_deg') else "",
                            f"{clr.loosening_rate[i]:.8f}" if hasattr(clr, 'loosening_rate') else "",
                            f"{clr.torque_margin[i]:.6f}" if hasattr(clr, 'torque_margin') else "",
                            f"{clr.friction_margin[i]:.6f}" if hasattr(clr, 'friction_margin') else "",
                        ])

        # ── 3. time_history.csv ─────────────────────────────────────────────
        if results and results.time_result:
            tr = results.time_result
            if hasattr(tr, 'time') and tr.time is not None and len(tr.time) > 0:
                MAX_HIST_PTS = 5000
                time_arr = np.asarray(tr.time)
                disp_arr = np.asarray(tr.displacement)
                vel_arr  = np.asarray(tr.velocity)
                acc_arr  = np.asarray(tr.acceleration)
                if len(time_arr) > MAX_HIST_PTS:
                    idx = np.linspace(0, len(time_arr) - 1, MAX_HIST_PTS, dtype=int)
                    time_arr, disp_arr, vel_arr, acc_arr = (
                        time_arr[idx], disp_arr[idx], vel_arr[idx], acc_arr[idx]
                    )
                with open(os.path.join(stem, "time_history.csv"), 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["time_s", "displacement_m", "velocity_m_s", "acceleration_m_s2"])
                    for t, d, v, a in zip(time_arr, disp_arr, vel_arr, acc_arr):
                        # displacement/velocity/acceleration may be multi-DOF arrays
                        d_val = float(d[0]) if hasattr(d, '__len__') else float(d)
                        v_val = float(v[0]) if hasattr(v, '__len__') else float(v)
                        a_val = float(a[0]) if hasattr(a, '__len__') else float(a)
                        writer.writerow([f"{t:.6g}", f"{d_val:.6g}", f"{v_val:.6g}", f"{a_val:.6g}"])

        # ── 4. modal.csv ────────────────────────────────────────────────────
        if results and results.natural_frequencies:
            with open(os.path.join(stem, "modal.csv"), 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["mode", "frequency_hz", "period_s"])
                for i, freq in enumerate(results.natural_frequencies):
                    period = (1.0 / freq) if freq > 0 else float('inf')
                    writer.writerow([i + 1, f"{freq:.6f}", f"{period:.6f}"])

        self._on_status_message(f"CSV data saved to folder: {stem}/")

    # =========================================================================
    # APP STATE CALLBACKS
    # =========================================================================

    def _on_project_changed(self, project):
        """Handle project change."""
        if project:
            self.setWindowTitle(f"🔩 Bolt Analysis Studio v4.0 — {project.name}")
            self._update_project_ui()

    def _on_model_changed(self, model):
        """Handle model change."""
        if model:
            stats = model.get_statistics()
            self.model_builder_tab.update_summary(stats)
            self.model_status.setText(f"Model: {model.n_elements} elements, {model.n_dof} DOF")
            self.model_builder_tab.validation_label.setText("⚠️ Model loaded - please validate")
            self.model_builder_tab.validation_label.setStyleSheet(f"color: {Theme.YELLOW};")

            # Update Solver Tab's loading summary from model.global_loading
            if hasattr(model, 'global_loading') and model.global_loading is not None:
                loading_data = {
                    "type": model.global_loading.type.name.lower() if hasattr(model.global_loading.type, 'name') else "transverse",
                    "F_preload": model.global_loading.F_preload,
                    "delta_amplitude": model.global_loading.delta_amplitude,
                    "frequency": model.global_loading.frequency,
                    "n_cycles": model.global_loading.n_cycles,
                    "mu_initial": getattr(model, 'mu_initial', 0.12),
                    "lubricated": getattr(model, 'lubricated', True),
                    "bolt_diameter": getattr(model, 'bolt_diameter', 16.0),
                    "pitch": getattr(model, 'pitch', 2.0),
                }
                self.solver_tab.update_loading_summary(loading_data)

                # Phase 1.4: Sync MSD Builder's PropertyInspector when model comes from
                # an external source (project load, model file load) — not from the
                # builder itself (which would create a feedback loop).
                if (not self._msd_builder_is_source
                        and self.msd_builder_window is not None):
                    try:
                        gl = model.global_loading
                        # Build Sy from bolt elements (same logic as load_from_msd_model)
                        _bolt_Sy = 640.0
                        for _elem in model.elements:
                            if (getattr(_elem.type, 'is_bolt_component', False)
                                    and hasattr(_elem, 'material')
                                    and _elem.material.Sy > 0):
                                _bolt_Sy = _elem.material.Sy
                                break
                        _inspector_data = {
                            "type": gl.type.value if hasattr(gl.type, 'value') else "Transverse",
                            "F_preload": gl.F_preload,
                            "preload_percent_yield": gl.preload_percent_yield,
                            "F_transverse": gl.F_transverse,
                            "delta_amplitude": gl.delta_amplitude,
                            "frequency": gl.frequency,
                            "n_cycles": gl.n_cycles,
                            "integration_time": gl.integration_time,
                            "duration_mode": "cycles",
                            "F_external": gl.F_external,
                            "T_applied": gl.T_applied,
                            "delta_T": gl.delta_T,
                            "mu_initial": getattr(model, 'mu_initial', 0.12),
                            "lubricated": getattr(model, 'lubricated', True),
                            "bolt_diameter": getattr(model, 'bolt_diameter', 16.0),
                            "pitch": getattr(model, 'pitch', 2.0),
                            "Sy": _bolt_Sy,
                            "friction_evolution_model": getattr(
                                model, 'friction_evolution_model', 'Three-Phase'),
                        }
                        if hasattr(self.msd_builder_window, 'inspector'):
                            self.msd_builder_window.inspector.set_loading_data(
                                _inspector_data)
                    except Exception:
                        pass  # Non-critical; don't block model load
        else:
            self.model_status.setText("Model: Not loaded")
            self.model_builder_tab.validation_label.setText("⚠️ No model loaded")

    def _on_results_changed(self, results):
        """Handle results change — updates summary stats with dynamic severity colors."""
        if results:
            stats = self.results_tab.stats_labels
            # Reset text and color to neutral before repopulating
            _font_ss = f"font-family: {Theme.FONT_MONO}; font-size: 9pt;"
            _neutral_ss = f"color:{Theme.SUBTEXT}; {_font_ss}"
            for key in stats:
                stats[key].setText("—")
                stats[key].setStyleSheet(_neutral_ss)

            # ── Severity color helpers (stable=green → runaway=red) ────────
            def _color_preload(ratio: float) -> str:
                if ratio >= 0.95: return Theme.GREEN
                if ratio >= 0.85: return Theme.YELLOW
                if ratio >= 0.70: return Theme.PEACH
                return Theme.RED

            def _color_loss(loss_pct: float) -> str:
                if loss_pct <= 5:  return Theme.GREEN
                if loss_pct <= 15: return Theme.YELLOW
                if loss_pct <= 30: return Theme.PEACH
                return Theme.RED

            def _color_margin(margin: float) -> str:
                if margin >= 1.3: return Theme.GREEN
                if margin >= 1.0: return Theme.YELLOW
                return Theme.RED

            _phase_colors = {
                'stable':         Theme.GREEN,
                'non_rotational': Theme.BLUE,
                'transition':     Theme.YELLOW,
                'rotational':     Theme.PEACH,
                'runaway':        Theme.RED,
            }
            _phase_labels = {
                'stable':         'Stable',
                'non_rotational': 'Stage I (Embedding)',
                'transition':     'Transition',
                'rotational':     'Stage II (Rotational)',
                'runaway':        'Run-away',
            }

            if results.coupled_loosening_result:
                import numpy as _np
                cl = results.coupled_loosening_result

                if "Final Preload" in stats and hasattr(cl, 'final_preload_ratio'):
                    fp = cl.final_preload_ratio
                    ip = getattr(cl, 'initial_preload', None)
                    if ip and ip > 0:
                        stats["Final Preload"].setText(f"{fp * ip / 1000:.2f} kN")
                    else:
                        stats["Final Preload"].setText(f"{fp * 100:.1f}%")
                    stats["Final Preload"].setStyleSheet(
                        f"color:{_color_preload(fp)}; {_font_ss}")

                if "Preload Loss" in stats and hasattr(cl, 'final_preload_ratio'):
                    loss = (1.0 - cl.final_preload_ratio) * 100
                    stats["Preload Loss"].setText(f"{loss:.2f}%")
                    stats["Preload Loss"].setStyleSheet(
                        f"color:{_color_loss(loss)}; {_font_ss}")

                if "Min Safety Factor" in stats and hasattr(cl, 'torque_margin'):
                    tm = cl.torque_margin
                    if tm is not None:
                        min_tm = float(_np.min(tm)) if hasattr(tm, '__iter__') else float(tm)
                        stats["Min Safety Factor"].setText(f"{min_tm:.2f}")
                        stats["Min Safety Factor"].setStyleSheet(
                            f"color:{_color_margin(min_tm)}; {_font_ss}")

                if "Loosening Phase" in stats:
                    final_state = (
                        cl.states[-1]
                        if (hasattr(cl, 'states') and cl.states)
                        else None
                    )
                    phase_val = None
                    if final_state is not None:
                        phase_val = (
                            final_state.phase.value
                            if hasattr(final_state.phase, 'value')
                            else str(final_state.phase)
                        )
                    elif hasattr(cl, 'phase_at_end') and cl.phase_at_end:
                        phase_val = cl.phase_at_end
                    if phase_val:
                        col = _phase_colors.get(phase_val, Theme.SUBTEXT)
                        txt = _phase_labels.get(
                            phase_val, phase_val.replace('_', ' ').title())
                        stats["Loosening Phase"].setText(txt)
                        stats["Loosening Phase"].setStyleSheet(
                            f"color:{col}; font-weight:bold; {_font_ss}")

            elif results.preload_result:
                pr = results.preload_result
                if "Final Preload" in stats:
                    fp = pr.final_preload_ratio
                    stats["Final Preload"].setText(f"{fp * 100:.1f}%")
                    stats["Final Preload"].setStyleSheet(
                        f"color:{_color_preload(fp)}; {_font_ss}")
                if "Preload Loss" in stats:
                    loss = pr.preload_loss_percent
                    stats["Preload Loss"].setText(f"{loss:.2f}%")
                    stats["Preload Loss"].setStyleSheet(
                        f"color:{_color_loss(loss)}; {_font_ss}")

            if results.time_result:
                tr = results.time_result
                if "Max Displacement" in stats:
                    stats["Max Displacement"].setText(f"{tr.max_displacement:.3e} m")
                if "Max Velocity" in stats:
                    stats["Max Velocity"].setText(f"{tr.max_velocity:.3e} m/s")
                if "Max Acceleration" in stats:
                    stats["Max Acceleration"].setText(f"{tr.max_acceleration:.3e} m/s²")

            if results.natural_frequencies:
                if "Fundamental Freq" in stats:
                    stats["Fundamental Freq"].setText(f"{results.natural_frequencies[0]:.2f} Hz")
                # 3.4: Update modal results panel
                damping = getattr(results, 'damping_ratios', None)
                self.results_tab.update_modal_results(
                    results.natural_frequencies, damping)
            else:
                self.results_tab.update_modal_results([])

    def _save_report_latex(self, filepath: str):
        """
        Generate a LaTeX (.tex) source file from the current analysis (6.2).

        Produces a self-contained article document with:
        - Title/author block from project info
        - Model summary table
        - Loading configuration table
        - Key results (loosening, preload loss)
        - Modal frequencies table (if available)
        """
        model = self.app_state.model
        results = self.app_state.results
        project = self.app_state.project
        ts = datetime.now().strftime('%Y-%m-%d')

        def _esc(s: str) -> str:
            """Escape LaTeX special characters."""
            for ch, rep in [('&', r'\&'), ('%', r'\%'), ('$', r'\$'),
                            ('#', r'\#'), ('{', r'\{'), ('}', r'\}'),
                            ('~', r'\textasciitilde{}'), ('^', r'\^{}'),
                            ('\\', r'\textbackslash{}'), ('_', r'\_')]:
                s = s.replace(ch, rep)
            return s

        lines = [
            r'\documentclass[a4paper,11pt]{article}',
            r'\usepackage[utf8]{inputenc}',
            r'\usepackage{booktabs}',
            r'\usepackage{geometry}',
            r'\geometry{margin=2.5cm}',
            r'\usepackage{hyperref}',
            r'\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue}',
            r'\title{Bolt Analysis Studio — Analysis Report}',
            f'\\author{{{_esc(project.author or "Prof. Leonardo Rosa Ribeiro da Silva, PhD; Neilon de Souza da Silva, PhD")}}}',
            f'\\date{{{ts}}}',
            r'\begin{document}',
            r'\maketitle',
            r'\tableofcontents',
            r'\newpage',
            '',
            r'\section{Model Summary}',
        ]

        if model:
            lines += [
                r'\begin{table}[h!]',
                r'\centering',
                r'\begin{tabular}{ll}',
                r'\toprule',
                r'\textbf{Parameter} & \textbf{Value} \\',
                r'\midrule',
                f'Model name & {_esc(model.name)} \\\\',
                f'Elements & {model.n_elements} \\\\',
                f'DOF & {model.n_dof} \\\\',
                f'Eq. stiffness & {model.get_equivalent_stiffness():.3e}~N/m \\\\',
                f'Total mass & {model.get_total_mass():.4f}~kg \\\\',
                r'\bottomrule',
                r'\end{tabular}',
                r'\caption{Model parameters}',
                r'\end{table}',
                '',
            ]

            if hasattr(model, 'global_loading') and model.global_loading:
                gl = model.global_loading
                mu = getattr(model, 'mu_initial', '—')
                d = getattr(model, 'bolt_diameter', '—')
                p = getattr(model, 'pitch', '—')
                lines += [
                    r'\section{Loading Configuration}',
                    r'\begin{table}[h!]',
                    r'\centering',
                    r'\begin{tabular}{ll}',
                    r'\toprule',
                    r'\textbf{Parameter} & \textbf{Value} \\',
                    r'\midrule',
                    f'Preload $F_0$ & {gl.F_preload:,.0f}~N \\\\',
                    f'Transverse force & {gl.F_transverse:,.0f}~N \\\\',
                    f'Amplitude & {gl.delta_amplitude:.3f}~mm \\\\',
                    f'Frequency & {gl.frequency:.2f}~Hz \\\\',
                    f'Cycles & {gl.n_cycles:,} \\\\',
                    f'Friction $\\mu$ & {mu} \\\\',
                    f'Bolt & M{d}~$\\times$~{p} \\\\',
                    r'\bottomrule',
                    r'\end{tabular}',
                    r'\caption{Loading configuration}',
                    r'\end{table}',
                    '',
                ]

        if results and results.coupled_loosening_result:
            clr = results.coupled_loosening_result
            loss_pct = (1.0 - clr.final_preload_ratio) * 100 if clr.final_preload_ratio else 0.0
            lines += [
                r'\section{Loosening Analysis Results}',
                r'\begin{table}[h!]',
                r'\centering',
                r'\begin{tabular}{ll}',
                r'\toprule',
                r'\textbf{Metric} & \textbf{Value} \\',
                r'\midrule',
                f'Final preload ratio $F/F_0$ & {clr.final_preload_ratio * 100:.1f}~\\% \\\\',
                f'Preload loss & {loss_pct:.1f}~\\% \\\\',
                f'Total loosening angle & {clr.total_loosening_deg:.2f}$^\\circ$ \\\\',
                r'\bottomrule',
                r'\end{tabular}',
                r'\caption{Coupled loosening analysis results}',
                r'\end{table}',
                '',
            ]

        if results and results.natural_frequencies:
            lines += [
                r'\section{Modal Analysis}',
                r'\begin{table}[h!]',
                r'\centering',
                r'\begin{tabular}{ccc}',
                r'\toprule',
                r'\textbf{Mode} & \textbf{Freq (Hz)} & \textbf{Period (s)} \\',
                r'\midrule',
            ]
            for i, freq in enumerate(results.natural_frequencies[:10]):
                period = f'{1/freq:.4g}' if freq > 0 else r'$\infty$'
                lines.append(f'{i+1} & {freq:.4g} & {period} \\\\')
            lines += [
                r'\bottomrule',
                r'\end{tabular}',
                r'\caption{Natural frequencies (first 10 modes)}',
                r'\end{table}',
                '',
            ]

        if results and results.audit:
            audit = results.audit
            lines += [
                r'\section{Analysis Audit Trail}',
                r'\begin{table}[h!]',
                r'\centering',
                r'\begin{tabular}{ll}',
                r'\toprule',
                r'\textbf{Field} & \textbf{Value} \\',
                r'\midrule',
                f'Run ID & {_esc(audit.run_id)} \\\\',
                f'Started & {_esc(audit.timestamp_start[:19])} \\\\',
                f'Duration & {audit.duration_s:.1f}~s \\\\',
                f'Method & {_esc(audit.method)} \\\\',
                f'DOF & {audit.n_dof} \\\\',
                f'Elements & {audit.n_elements} \\\\',
                r'\bottomrule',
                r'\end{tabular}',
                r'\caption{Analysis audit metadata}',
                r'\end{table}',
                '',
            ]

        lines += [
            r'\vfill',
            r'\begin{center}\small Generated by Bolt Analysis Studio v4.0 '
            r'\end{center}',
            r'\end{document}',
        ]

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _on_status_message(self, message: str):
        """Handle status messages."""
        self.statusBar().showMessage(message, 5000)

    def _on_error(self, error: str):
        """Handle errors."""
        QMessageBox.critical(self, "Error", error)

    # =========================================================================
    # SIMILITUDE NAVIGATION
    # =========================================================================

    def _go_to_similitude_tab(self, sub_tab_index: int = 0):
        """
        Navigate to the similitude tab.

        Args:
            sub_tab_index: Index of the sub-tab to select
                          0 = Multi-Bolt Reduction
                          1 = Geometric Scaling
        """
        # Find the similitude tab index (it's tab 5, index 4, 0-based)
        similitude_tab_index = 4  # "5. Similitude" tab

        self.tab_widget.setCurrentIndex(similitude_tab_index)

        # Select the sub-tab if enhanced similitude is available
        if HAS_ENHANCED_SIMILITUDE and hasattr(self.similitude_tab, 'analysis_tabs'):
            self.similitude_tab.analysis_tabs.setCurrentIndex(sub_tab_index)

    # =========================================================================
    # MSD BUILDER
    # =========================================================================

    def _open_msd_builder(self):
        """Switch focus to the embedded MSD Builder tab (Tab 2)."""
        # The builder is embedded in ModelBuilderTab — no floating window.
        self.tab_widget.setCurrentWidget(self.model_builder_tab)
        if self.app_state.model and self.msd_builder_window is not None:
            self.msd_builder_window.load_from_msd_model(self.app_state.model)

    def _send_model_to_solver(self):
        """Export current builder model into app_state and switch to Solver tab."""
        if self.msd_builder_window is None:
            return
        try:
            msd_model = self.msd_builder_window.export_to_msd_model()
        except Exception as e:
            QMessageBox.warning(self, "Send to Solver",
                                f"Failed to export model:\n{e}")
            return
        if msd_model is None:
            QMessageBox.information(self, "Send to Solver",
                                    "No model to send — add elements first.")
            return
        self.app_state.model = msd_model
        self.tab_widget.setCurrentWidget(self.solver_tab)
        self._on_status_message("Model sent to Solver tab.")

    def _on_msd_builder_model_changed(self, model_data: dict):
        """Handle model changes from MSD Builder."""
        self._msd_builder_is_source = True
        try:
            if self.msd_builder_window:
                msd_model = self.msd_builder_window.export_to_msd_model()
                if msd_model:
                    self.app_state.model = msd_model

                    # MED-01: Extract transverse stiffness from assembled [K] and push to inspector
                    try:
                        import numpy as _np
                        _M, _K, _C = msd_model.assemble_matrices()
                        if _K.shape[0] > 0:
                            # Use the middle DOF stiffness as the joint interface stiffness
                            _mid = _K.shape[0] // 2
                            _k_trans = float(_K[_mid, _mid])
                            if _k_trans > 0 and hasattr(self.msd_builder_window, 'inspector'):
                                self.msd_builder_window.inspector.set_transverse_stiffness(_k_trans)
                    except Exception:
                        pass

                    # Update Solver Tab's loading summary with the new configuration
                    if hasattr(msd_model, 'global_loading') and msd_model.global_loading is not None:
                        loading_data = {
                            "type": msd_model.global_loading.type.name.lower() if hasattr(msd_model.global_loading.type, 'name') else "transverse",
                            "F_preload": msd_model.global_loading.F_preload,
                            "delta_amplitude": msd_model.global_loading.delta_amplitude,
                            "frequency": msd_model.global_loading.frequency,
                            "n_cycles": msd_model.global_loading.n_cycles,
                            "mu_initial": getattr(msd_model, 'mu_initial', 0.12),
                            "lubricated": getattr(msd_model, 'lubricated', True),
                            "bolt_diameter": getattr(msd_model, 'bolt_diameter', 16.0),
                            "pitch": getattr(msd_model, 'pitch', 2.0),
                        }
                        self.solver_tab.update_loading_summary(loading_data)
                        # Trigger one auto-calculate after batch spinbox update (HIGH-04)
                        self._auto_calculate_timestep()

                    # Update Project Tab model summary card (D8)
                    if hasattr(self.project_tab, 'update_model_summary'):
                        self.project_tab.update_model_summary(msd_model)
        finally:
            self._msd_builder_is_source = False

        # NOTE: do NOT call self.activateWindow() here. This handler fires on
        # every property edit in the (floating) MSD Builder inspector; raising
        # the main window would steal keyboard focus while the user is typing.
        # Focus is left wherever the user is working.

    def _on_similitude_scaling_computed(self, scaled_model):
        """
        Store similitude scaling result in AppState when computed (CRITICAL-03 / MED-03).

        Args:
            scaled_model: ScaledLooseningModel from similitude analysis
        """
        self.app_state.similitude_result = scaled_model
        self._on_status_message("Similitude scaling computed and stored in project state.")

    def _on_similitude_transfer(self, elements: dict):
        """
        Handle transfer of model from similitude analysis to MSD Builder.

        Args:
            elements: Dictionary containing MSD element parameters from
                     multi-bolt reduction or geometric scaling analysis.
        """
        # Open MSD Builder if not already open
        self._open_msd_builder()

        # BUG-02 fix: Actually populate the schematic with the transferred elements
        if self.msd_builder_window and hasattr(self.msd_builder_window, 'load_from_elements_dict'):
            try:
                self.msd_builder_window.load_from_elements_dict(elements)
            except Exception as e:
                self._on_status_message(f"Transfer warning: {e}")

        # Log the transfer
        n_elems = len(self.msd_builder_window.schematic.elements) if self.msd_builder_window else 0
        self._on_status_message(f"Similitude model transferred to MSD Builder ({n_elems} elements)")

        # Update model builder summary
        if 'preload' in elements:
            self.model_builder_tab.validation_label.setText(
                f"Similitude model: F_p = {elements['preload']/1000:.1f} kN"
            )
            self.model_builder_tab.validation_label.setStyleSheet(f"color: {Theme.BLUE};")

        # Switch to Model Builder tab
        self.tab_widget.setCurrentIndex(1)

    def _on_similitude_import_model(self):
        """U2: Push current MSD model parameters to the Similitude tab."""
        model = self.app_state.model
        if model is None:
            self._on_status_message("No model loaded — configure one in the MSD Builder first.")
            return

        params = {
            "bolt_diameter": float(getattr(model, "bolt_diameter", 16.0)),
            "pitch": float(getattr(model, "pitch", 2.0)),
            "mu_initial": float(getattr(model, "mu_initial", 0.12)),
        }
        if hasattr(model, "global_loading") and model.global_loading is not None:
            params["preload"] = float(getattr(model.global_loading, "F_preload", 50000.0))
            params["frequency"] = float(getattr(model.global_loading, "frequency", 25.0))

        if HAS_ENHANCED_SIMILITUDE and hasattr(self.similitude_tab, "populate_from_model"):
            try:
                self.similitude_tab.populate_from_model(params)
                self._on_status_message(
                    f"Model parameters imported to Similitude: "
                    f"M{params['bolt_diameter']:.0f}, "
                    f"F_p={params.get('preload', 0)/1000:.1f} kN, "
                    f"f={params.get('frequency', 0):.1f} Hz"
                )
            except Exception as e:
                self._on_status_message(f"Import to Similitude failed: {e}")

    def _on_similitude_send_to_solver(self, scaled_params: dict):
        """U6: Apply scaled model parameters to solver configuration."""
        try:
            self.solver_tab.update_loading_summary(scaled_params)
            f_hz = scaled_params.get("frequency", 0.0)
            fp_kn = scaled_params.get("F_preload", 0.0) / 1000.0
            self.tab_widget.setCurrentIndex(2)  # Switch to Solver tab
            self._on_status_message(
                f"Scaled model → Solver: f={f_hz:.1f} Hz, F_p={fp_kn:.1f} kN"
            )
        except Exception as e:
            self._on_status_message(f"Send to Solver failed: {e}")

    # =========================================================================
    # CONTACTS TAB
    # =========================================================================
    # CONTACTS TAB - REMOVED (Now integrated in MSD Builder)
    # =========================================================================


# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

def main():
    """Main entry point for the application."""
    # Create application
    app = QApplication(sys.argv)

    # Apply theme stylesheet
    app.setStyleSheet(Theme.get_stylesheet())

    # Create and show main window
    window = BoltAnalysisStudio()
    window.setMinimumSize(1024, 700)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
