"""New-Analysis Wizard.

5-page QWizard that walks a first-time user from "I have an experiment"
to a fully-populated MSD model open in the Builder.

The wizard does **not** lock anything — after it generates the model the
user is dropped into the editable MSD Builder where they can add /
remove / tweak elements normally. It's just a fast on-ramp.

Pages:
  1. Joint type      — preset element set
  2. Bolt geometry   — size, grade, preload
  3. Loading         — type, amplitude, frequency, cycles
  4. Reference data  — optional CSV pick
  5. Review          — summary + Generate

After exec() returns Accepted, call ``spec()`` for the chosen settings
and ``build_model(spec)`` to materialise an :class:`MSDModel`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QListWidget, QListWidgetItem, QComboBox, QDoubleSpinBox, QSpinBox,
    QGroupBox, QRadioButton, QButtonGroup, QPushButton, QFileDialog,
    QLineEdit, QTextEdit, QCheckBox,
)

from bolt_analysis_studio.core.models.element import (
    LoadingType, MaterialGrade, ElementType, MSDElementData,
    create_bolt_head, create_bolt_shank, create_thread_element,
    create_nut, create_flange, create_gasket, create_washer,
    create_ground,
)
from bolt_analysis_studio.core.models.model import MSDModel
from bolt_analysis_studio.core.databases.materials_database import (
    get_material,
)
from bolt_analysis_studio.gui.theme import Theme


# ---------------------------------------------------------------------------
# Joint-type presets — shape the element list the wizard generates
# ---------------------------------------------------------------------------

JOINT_PRESETS = [
    {
        "id": "single_axial",
        "label": "Junta simples · carregamento axial",
        "summary": "Parafuso + 2 chapas em contato metal-metal, tração axial cíclica.",
        "elements": ("HEAD", "SHANK", "THREAD", "NUT",
                     "FLANGE_TOP", "FLANGE_BOT"),
        "contacts": ("BEARING_HEAD", "BEARING_NUT", "THREAD_C", "FLANGE_FLANGE"),
        "default_loading": "AXIAL",
    },
    {
        "id": "single_shear",
        "label": "Junta simples · carregamento cisalhante (Junker)",
        "summary": "Parafuso + 2 chapas em contato metal-metal, deslizamento transversal.",
        "elements": ("HEAD", "SHANK", "THREAD", "NUT",
                     "FLANGE_TOP", "FLANGE_BOT"),
        "contacts": ("BEARING_HEAD", "BEARING_NUT", "THREAD_C", "FLANGE_FLANGE"),
        "default_loading": "TRANSVERSE",
    },
    {
        "id": "flange_axial",
        "label": "Flange com gaxeta · carregamento axial",
        "summary": "Flanges + gaxeta entre elas, tração axial. Perdas dominadas por creep da gaxeta.",
        "elements": ("HEAD", "SHANK", "THREAD", "NUT",
                     "FLANGE_TOP", "GASKET", "FLANGE_BOT"),
        "contacts": ("BEARING_HEAD", "BEARING_NUT", "THREAD_C", "GASKET_C"),
        "default_loading": "AXIAL",
    },
    {
        "id": "flange_shear",
        "label": "Flange com gaxeta · carregamento cisalhante",
        "summary": "Flanges + gaxeta, deslizamento transversal. Combina creep da gaxeta com afrouxamento Junker.",
        "elements": ("HEAD", "SHANK", "THREAD", "NUT",
                     "FLANGE_TOP", "GASKET", "FLANGE_BOT"),
        "contacts": ("BEARING_HEAD", "BEARING_NUT", "THREAD_C", "GASKET_C"),
        "default_loading": "TRANSVERSE",
    },
    {
        "id": "blank",
        "label": "Modelo vazio (construir do zero)",
        "summary": "Apenas define unidades & carregamento; nenhum elemento pré-criado.",
        "elements": (),
        "contacts": (),
        "default_loading": "TRANSVERSE",
    },
]


# Default per-contact MSD parameters (matches msd_builder.ELEMENT_VISUALS).
_CONTACT_DEFAULTS = {
    "BEARING_HEAD":  (ElementType.BEARING_HEAD,   1e10, 100, 0.001),
    "BEARING_NUT":   (ElementType.BEARING_NUT,    1e10, 100, 0.001),
    "THREAD_C":      (ElementType.THREAD,         6.6e7, 100, 0.005),
    "FLANGE_FLANGE": (ElementType.FLANGE_FLANGE,  1e10, 100, 0.001),
    "WASHER_C_TOP":  (ElementType.WASHER_CONTACT, 8e9,  80,  0.001),
    "WASHER_C_BOT":  (ElementType.WASHER_CONTACT, 8e9,  80,  0.001),
    "GASKET_C":      (ElementType.GASKET_CONTACT, 5e8,  500, 0.020),
}


# ---------------------------------------------------------------------------
# Bolt-size table (mm pitch, ISO metric coarse)
# ---------------------------------------------------------------------------

BOLT_SIZES = [
    ("M6",  6.0,  1.00),
    ("M8",  8.0,  1.25),
    ("M10", 10.0, 1.50),
    ("M12", 12.0, 1.75),
    ("M14", 14.0, 2.00),
    ("M16", 16.0, 2.00),
    ("M18", 18.0, 2.50),
    ("M20", 20.0, 2.50),
    ("M22", 22.0, 2.50),
    ("M24", 24.0, 3.00),
    ("M27", 27.0, 3.00),
    ("M30", 30.0, 3.50),
]


# ---------------------------------------------------------------------------
# Wizard spec
# ---------------------------------------------------------------------------

@dataclass
class AnalysisSpec:
    """User selections coming out of the wizard."""
    project_name: str = "New Analysis"
    joint_preset_id: str = "single_axial"
    bolt_diameter_mm: float = 12.0
    pitch_mm: float = 1.75
    grade: str = "Steel 10.9"
    flange_thickness_mm: float = 25.0
    preload_pct_yield: float = 70.0
    loading_type: str = "AXIAL"  # AXIAL / TRANSVERSE / COMBINED
    control_mode: str = "displacement"  # displacement / force
    delta_amplitude_mm: float = 0.5
    F_amplitude_N: float = 5000.0
    frequency_hz: float = 12.5
    n_cycles: int = 2000
    reference_csv_path: str = ""

    @property
    def joint_preset(self) -> dict:
        for p in JOINT_PRESETS:
            if p["id"] == self.joint_preset_id:
                return p
        return JOINT_PRESETS[0]


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

class _JointPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("1 · Joint configuration")
        self.setSubTitle(
            "Pick the closest joint topology. The wizard generates the "
            "matching elements; you can still add or remove anything later "
            "in the MSD Builder.")

        # Project name — names the generated MSDModel. Defaults to the same
        # value as AnalysisSpec.project_name so leaving it untouched (or empty)
        # reproduces the previous behaviour exactly.
        self.name_edit = QLineEdit()
        self.name_edit.setText(AnalysisSpec.project_name)
        self.name_edit.setPlaceholderText(AnalysisSpec.project_name)
        self.name_edit.setToolTip(
            "Nome do projeto — usado como nome do modelo MSD gerado. "
            "Se vazio, cai no default.")

        self.list = QListWidget()
        for p in JOINT_PRESETS:
            it = QListWidgetItem(p["label"])
            it.setData(Qt.ItemDataRole.UserRole, p["id"])
            it.setToolTip(p["summary"])
            self.list.addItem(it)
        self.list.setCurrentRow(0)
        self.list.itemSelectionChanged.connect(self._update_summary)
        self.list.itemSelectionChanged.connect(self.completeChanged.emit)

        self.summary = QLabel()
        self.summary.setWordWrap(True)
        # Theme-driven (wizard is recreated per open, so it reads the active
        # palette — works in both light and dark).
        self.summary.setStyleSheet(f"color:{Theme.SUBTEXT}; padding:6px;")

        name_form = QFormLayout()
        name_form.addRow("Nome do projeto:", self.name_edit)

        lay = QVBoxLayout(self)
        lay.addLayout(name_form)
        lay.addWidget(QLabel("<b>Joint type</b>"))
        lay.addWidget(self.list, stretch=1)
        lay.addWidget(self.summary)
        self._update_summary()

    def project_name(self) -> str:
        """Project name for the generated model; falls back to the
        AnalysisSpec default when the field is left empty."""
        return self.name_edit.text().strip() or AnalysisSpec.project_name

    def _update_summary(self):
        it = self.list.currentItem()
        if not it:
            self.summary.setText("")
            return
        pid = it.data(Qt.ItemDataRole.UserRole)
        for p in JOINT_PRESETS:
            if p["id"] == pid:
                elems = ", ".join(p["elements"]) or "(none)"
                self.summary.setText(
                    f"<b>{p['label']}</b><br>{p['summary']}"
                    f"<br><i>Elements:</i> {elems}")
                break

    def selected_id(self) -> str:
        it = self.list.currentItem()
        return it.data(Qt.ItemDataRole.UserRole) if it else "single_axial"


class _BoltPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("2 · Bolt geometry & material")
        self.setSubTitle(
            "Standard bolt size + grade. Preload is set as a fraction of "
            "yield; the actual kN depends on the grade once the model runs.")

        self.size_combo = QComboBox()
        for label, _d, _p in BOLT_SIZES:
            self.size_combo.addItem(label)
        self.size_combo.setCurrentText("M12")
        self.size_combo.currentTextChanged.connect(self._on_size)

        self.diam_label = QLabel("12.0 mm")
        self.pitch_label = QLabel("1.75 mm")

        self.grade_combo = QComboBox()
        for g in MaterialGrade:
            self.grade_combo.addItem(g.value)
        self.grade_combo.setCurrentText("Steel 10.9")

        self.flange_thickness = QDoubleSpinBox()
        self.flange_thickness.setRange(2.0, 200.0)
        self.flange_thickness.setSuffix(" mm")
        self.flange_thickness.setValue(25.0)

        self.preload_pct = QDoubleSpinBox()
        self.preload_pct.setRange(20.0, 90.0)
        self.preload_pct.setSuffix(" %")
        self.preload_pct.setValue(70.0)
        self.preload_pct.setToolTip(
            "Fraction of bolt yield used as installation preload. "
            "VDI 2230 typical: 70 %. ISO 16130: 60–80 %.")

        form = QFormLayout()
        form.addRow("Bolt size:", self.size_combo)
        form.addRow("Major diameter (auto):", self.diam_label)
        form.addRow("Thread pitch (auto):", self.pitch_label)
        form.addRow("Material grade:", self.grade_combo)
        form.addRow("Flange thickness (each):", self.flange_thickness)
        form.addRow("Preload (% yield):", self.preload_pct)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addStretch()

    def _on_size(self, label: str):
        for lab, d, p in BOLT_SIZES:
            if lab == label:
                self.diam_label.setText(f"{d:g} mm")
                self.pitch_label.setText(f"{p:g} mm")
                return

    def values(self) -> tuple:
        d = 12.0
        p = 1.75
        for lab, dd, pp in BOLT_SIZES:
            if lab == self.size_combo.currentText():
                d, p = dd, pp
                break
        return (d, p,
                self.grade_combo.currentText(),
                float(self.flange_thickness.value()),
                float(self.preload_pct.value()))


class _LoadingPage(QWizardPage):
    def __init__(self, joint_page: "_JointPage"):
        super().__init__()
        self.setTitle("3 · Loading conditions")
        self.setSubTitle(
            "Loading type + amplitudes. Values are typical for Junker "
            "transverse vibration testing — adjust to match your rig.")
        self._joint_page = joint_page

        self.loading_combo = QComboBox()
        self.loading_combo.addItems([
            "Transverse Junker (vibration ⟂ bolt axis)",
            "Axial pulsating tension",
            "Combined axial + transverse",
        ])
        self._loading_keys = ["TRANSVERSE", "AXIAL", "COMBINED"]

        # Control mode — displacement-controlled (impose δ) vs force-controlled
        # (impose F). Maps to the V2 engine's disp/force step_cycle modes.
        self.control_combo = QComboBox()
        self.control_combo.addItems([
            "Displacement-controlled (impose δ — Junker/crank rig)",
            "Force-controlled (impose F — servo-hydraulic)",
        ])
        self._control_keys = ["displacement", "force"]
        self.control_combo.currentIndexChanged.connect(self._on_control_changed)

        self.delta_spin = QDoubleSpinBox()
        self.delta_spin.setRange(0.0, 5.0)
        self.delta_spin.setSuffix(" mm")
        self.delta_spin.setDecimals(3)
        self.delta_spin.setValue(0.5)
        self.delta_spin.setToolTip(
            "Peak transverse displacement amplitude. Typical Junker: 0.3-1.0 mm.")

        self.force_spin = QDoubleSpinBox()
        self.force_spin.setRange(0.0, 1e6)
        self.force_spin.setSuffix(" N")
        self.force_spin.setDecimals(0)
        self.force_spin.setValue(5000.0)
        self.force_spin.setToolTip(
            "Axial dynamic-force amplitude (used for axial / combined modes).")

        self.freq_spin = QDoubleSpinBox()
        self.freq_spin.setRange(0.1, 1000.0)
        self.freq_spin.setSuffix(" Hz")
        self.freq_spin.setDecimals(2)
        self.freq_spin.setValue(12.5)

        self.cycles_spin = QSpinBox()
        self.cycles_spin.setRange(10, 1_000_000)
        self.cycles_spin.setValue(2000)
        self.cycles_spin.setSuffix(" cycles")

        form = QFormLayout()
        form.addRow("Loading type:", self.loading_combo)
        form.addRow("Control mode:", self.control_combo)
        form.addRow("Transverse amplitude δ:", self.delta_spin)
        form.addRow("Axial force amplitude:", self.force_spin)
        form.addRow("Frequency:", self.freq_spin)
        form.addRow("Cycles:", self.cycles_spin)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addStretch()
        self._on_control_changed()

    def _on_control_changed(self):
        """Grey out the input that isn't the control driver, so it's clear
        which quantity is imposed vs derived."""
        mode = self._control_keys[self.control_combo.currentIndex()]
        disp = (mode == "displacement")
        self.delta_spin.setEnabled(disp)
        self.force_spin.setEnabled(not disp)

    def initializePage(self):
        # Pre-select default loading from the joint preset
        pid = self._joint_page.selected_id()
        for p in JOINT_PRESETS:
            if p["id"] == pid:
                want = p.get("default_loading", "TRANSVERSE")
                if want in self._loading_keys:
                    self.loading_combo.setCurrentIndex(
                        self._loading_keys.index(want))
                break

    def values(self) -> tuple:
        idx = self.loading_combo.currentIndex()
        ltype = self._loading_keys[idx] if 0 <= idx < len(self._loading_keys) \
            else "TRANSVERSE"
        cmode = self._control_keys[self.control_combo.currentIndex()]
        return (ltype, cmode,
                float(self.delta_spin.value()),
                float(self.force_spin.value()),
                float(self.freq_spin.value()),
                int(self.cycles_spin.value()))


class _ReferencePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("4 · Reference data (optional)")
        self.setSubTitle(
            "Drop in a lab CSV (cycle, F_kN, F/F₀) so the calibration "
            "agent has something to fit against. Skip if you don't have "
            "experimental data yet.")

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("(no reference — analysis only)")
        self.path_edit.setReadOnly(True)
        self.browse_btn = QPushButton("Browse…")
        self.browse_btn.clicked.connect(self._browse)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(lambda: self.path_edit.setText(""))

        path_row = QHBoxLayout()
        path_row.addWidget(self.path_edit, stretch=1)
        path_row.addWidget(self.browse_btn)
        path_row.addWidget(self.clear_btn)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText(
            "First few rows of the chosen CSV appear here.")
        self.preview.setMaximumHeight(140)

        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("<b>Reference CSV</b>"))
        lay.addLayout(path_row)
        lay.addSpacing(6)
        lay.addWidget(QLabel("<b>Preview</b>"))
        lay.addWidget(self.preview)
        lay.addStretch()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Reference CSV", "",
            "CSV (*.csv);;All Files (*)")
        if not path:
            return
        self.path_edit.setText(path)
        self._fill_preview(path)

    def _fill_preview(self, path: str):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                head = "".join(fh.readline() for _ in range(8))
            self.preview.setPlainText(head)
        except Exception as exc:
            self.preview.setPlainText(f"(Could not read file: {exc})")

    def value(self) -> str:
        return self.path_edit.text().strip()


class _ReviewPage(QWizardPage):
    def __init__(self, wizard_ref):
        super().__init__()
        self.setTitle("5 · Review & generate")
        self.setSubTitle(
            "Click <b>Finish</b> to materialise the MSD model. "
            "It opens in the Builder where you can refine anything before "
            "running the solver.")
        self._wizard = wizard_ref

        self.summary = QLabel()
        self.summary.setWordWrap(True)
        self.summary.setTextFormat(Qt.TextFormat.RichText)
        # Theme-driven panel — reads the active palette at construction (wizard
        # is recreated per open), so it's correct in both light and dark.
        self.summary.setStyleSheet(
            f"padding: 8px; background: {Theme.SURFACE1}; "
            f"border:1px solid {Theme.SURFACE2}; color:{Theme.TEXT}; "
            f"border-radius:4px;")

        self.open_solver_check = QCheckBox(
            "After generating, also pre-load the reference into the "
            "Results tab (only if a CSV was provided)")
        self.open_solver_check.setChecked(True)

        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("<b>Configuration summary</b>"))
        lay.addWidget(self.summary)
        lay.addSpacing(8)
        lay.addWidget(self.open_solver_check)
        lay.addStretch()

    def initializePage(self):
        spec = self._wizard.spec()
        preset = spec.joint_preset
        elems = ", ".join(preset["elements"]) or "(none — empty model)"
        ref = spec.reference_csv_path or "(none)"
        self.summary.setText(
            f"<b>Project:</b> {spec.project_name}<br>"
            f"<b>Joint:</b> {preset['label']}<br>"
            f"<b>Elements to generate:</b> {elems}<br><br>"
            f"<b>Bolt:</b> M{spec.bolt_diameter_mm:g} × {spec.pitch_mm:g} mm  ·  "
            f"{spec.grade}<br>"
            f"<b>Flange thickness:</b> {spec.flange_thickness_mm:g} mm  ·  "
            f"<b>Preload:</b> {spec.preload_pct_yield:g}% yield<br><br>"
            f"<b>Loading:</b> {spec.loading_type}  ·  "
            f"<b>control:</b> {spec.control_mode}  ·  "
            f"δ = {spec.delta_amplitude_mm:g} mm  ·  "
            f"F = {spec.F_amplitude_N:g} N  ·  "
            f"f = {spec.frequency_hz:g} Hz  ·  "
            f"N = {spec.n_cycles}<br>"
            f"<b>Reference CSV:</b> {ref}")

    def will_load_reference(self) -> bool:
        return self.open_solver_check.isChecked()


# ---------------------------------------------------------------------------
# Wizard
# ---------------------------------------------------------------------------

class NewAnalysisWizard(QWizard):
    """Five-page on-ramp for a new BAS analysis."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Analysis Wizard")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setOption(QWizard.WizardOption.IndependentPages, False)
        self.setMinimumSize(720, 560)

        self._joint = _JointPage()
        self._bolt = _BoltPage()
        self._loading = _LoadingPage(self._joint)
        self._reference = _ReferencePage()
        self._review = _ReviewPage(self)

        self.addPage(self._joint)
        self.addPage(self._bolt)
        self.addPage(self._loading)
        self.addPage(self._reference)
        self.addPage(self._review)

        self.setButtonText(QWizard.WizardButton.FinishButton,
                           "Generate model")

    def spec(self) -> AnalysisSpec:
        d, p, grade, flange_t, preload_pct = self._bolt.values()
        ltype, cmode, delta, force, freq, n_cyc = self._loading.values()
        return AnalysisSpec(
            project_name=self._joint.project_name(),
            joint_preset_id=self._joint.selected_id(),
            bolt_diameter_mm=d,
            pitch_mm=p,
            grade=grade,
            flange_thickness_mm=flange_t,
            preload_pct_yield=preload_pct,
            loading_type=ltype,
            control_mode=cmode,
            delta_amplitude_mm=delta,
            F_amplitude_N=force,
            frequency_hz=freq,
            n_cycles=n_cyc,
            reference_csv_path=self._reference.value(),
        )

    def will_load_reference(self) -> bool:
        return self._review.will_load_reference()


# ---------------------------------------------------------------------------
# Model builder — turns AnalysisSpec into a populated MSDModel
# ---------------------------------------------------------------------------

def _grade_to_enum(grade_str: str) -> MaterialGrade:
    for g in MaterialGrade:
        if g.value == grade_str:
            return g
    return MaterialGrade.STEEL_10_9


def _next_id(model: MSDModel) -> int:
    """Next free element id, predictable for cross-element references."""
    used = {int(getattr(e, "id", 0) or 0) for e in model.elements}
    return (max(used) + 1) if used else 1


# Map wizard grade strings → materials_database keys.
_GRADE_DB_KEY = {
    "Steel 8.8":  "ISO_8.8",
    "Steel 10.9": "ISO_10.9",
    "Steel 12.9": "ISO_12.9",
    "A193 B7":    "A193_B7",
    "A320 L7":    "A320_L7",
}


def _lookup_yield_strength_MPa(grade_str: str) -> float:
    """Pull Sy from the canonical materials database; fall back to 800 MPa."""
    key = _GRADE_DB_KEY.get(grade_str)
    if key:
        mat = get_material(key)
        if mat is not None:
            return float(getattr(mat, "Sy", 800.0))
    return 800.0


def _make_contact(eid: int, token: str, name: str) -> MSDElementData:
    """Build a contact element with project-default MSD parameters."""
    etype, k, c, m = _CONTACT_DEFAULTS[token]
    el = MSDElementData(id=eid, name=name, type=etype)
    el.msd.k = k
    el.msd.c = c
    el.msd.m = m
    return el


def build_model(spec: AnalysisSpec) -> MSDModel:
    """Materialise an :class:`MSDModel` from the wizard spec."""
    model = MSDModel(name=spec.project_name)
    grade = _grade_to_enum(spec.grade)

    # Friction defaults (Level-3 persistent on the model itself)
    model.mu_initial = 0.12
    model.lubricated = False

    # Boundary condition: a runnable joint needs a fixed ground anchor at the
    # top of the chain, otherwise matrix assembly has no reference and
    # validation fails ("No ground element defined"). Matches the âncora interna .msd
    # models (GROUND is the first element).
    model.add_element(create_ground(id=_next_id(model)))

    for token in spec.joint_preset["elements"]:
        eid = _next_id(model)
        if token == "HEAD":
            el = create_bolt_head(
                id=eid, diameter=spec.bolt_diameter_mm, material=grade)
        elif token == "SHANK":
            el = create_bolt_shank(
                id=eid, diameter=spec.bolt_diameter_mm,
                length=max(2 * spec.flange_thickness_mm, 20.0),
                material=grade)
        elif token == "THREAD":
            el = create_thread_element(
                id=eid, diameter=spec.bolt_diameter_mm,
                pitch=spec.pitch_mm, length=15.0, material=grade)
        elif token == "NUT":
            el = create_nut(
                id=eid, diameter=spec.bolt_diameter_mm,
                pitch=spec.pitch_mm, material=grade)
        elif token in ("FLANGE_TOP", "FLANGE_BOT"):
            el = create_flange(
                id=eid, thickness=spec.flange_thickness_mm,
                bolt_diameter=spec.bolt_diameter_mm)
        elif token == "GASKET":
            el = create_gasket(
                id=eid,
                inner_diameter=spec.bolt_diameter_mm * 1.5,
                outer_diameter=spec.bolt_diameter_mm * 4.0,
                thickness=3.0,
                gasket_type="spiral_wound")
        elif token in ("WASHER_TOP", "WASHER_BOT"):
            el = create_washer(
                id=eid, bolt_diameter=spec.bolt_diameter_mm,
                thickness=3.0, material=grade)
        else:
            continue
        if hasattr(el, "name") and not el.name:
            el.name = token.title()
        model.add_element(el)

    # Contact-element pass — every interface listed in the preset.
    for ctoken in spec.joint_preset.get("contacts", ()):
        if ctoken not in _CONTACT_DEFAULTS:
            continue
        cid = _next_id(model)
        model.add_element(_make_contact(cid, ctoken, ctoken.replace("_", " ").title()))

    # Loading defaults
    gl = model.global_loading
    if spec.loading_type == "AXIAL":
        gl.type = LoadingType.AXIAL
    elif spec.loading_type == "COMBINED":
        gl.type = LoadingType.COMBINED
    else:
        gl.type = LoadingType.TRANSVERSE
    gl.preload_percent_yield = float(spec.preload_pct_yield)
    gl.control_mode = spec.control_mode
    # F_preload — rough estimate from grade Sy and ISO 724 stress area;
    # analyzer recomputes precisely from thread geometry, so this is a
    # display-friendly starting value.
    Sy = _lookup_yield_strength_MPa(spec.grade)
    d2 = spec.bolt_diameter_mm - 0.6495 * spec.pitch_mm
    d1 = spec.bolt_diameter_mm - 1.0825 * spec.pitch_mm
    A_s = math.pi / 4.0 * ((d2 + d1) / 2.0) ** 2  # mm²
    gl.F_preload = float(A_s * Sy * spec.preload_pct_yield / 100.0)
    gl.delta_amplitude = float(spec.delta_amplitude_mm)
    gl.F_amplitude = float(spec.F_amplitude_N)
    gl.frequency = float(spec.frequency_hz)
    gl.n_cycles = int(spec.n_cycles)
    gl.bolt_diameter = float(spec.bolt_diameter_mm)
    gl.pitch = float(spec.pitch_mm)

    # F_transverse derived from delta × k_member only after model is in
    # the Builder (which knows k); leave it 0 here so the inspector pulls
    # the live value once the user enters Tab 2.
    gl.F_transverse = 0.0

    return model
