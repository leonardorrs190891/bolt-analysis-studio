"""Literature-grounded calibration wizard.

Three-page QWizard that walks the user through:
  1. Pick a loading regime (transverse Junker, axial pulsating, etc.)
  2. Pick a reference study within that regime
  3. Review the suggested parameter values + ±sigma bounds, then apply

On accept, exposes ``selected_priors()`` returning::

    {
      "id":     "<paper id>",
      "label":  "<human label>",
      "params": {name: default_value, ...},
      "bounds": {name: (lo, hi), ...},
    }

The caller (CalibrationDialog) then writes those into its spinboxes and
ticks the matching parameter checkboxes.
"""
from __future__ import annotations

import json
import os
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QTextEdit, QGroupBox, QGridLayout, QSizePolicy,
)


_REGIME_LABELS = {
    "transverse_junker":  "Transverse Junker (steel-on-steel)",
    "axial_pulsating":    "Axial pulsating tension (R≈0)",
    "combined_R_factor":  "Combined axial+transverse (R-factor sweep)",
    "cfrp_composite":     "CFRP / composite member",
    "gasketed_creep":     "Gasketed flange (creep-dominated)",
    "torsional":          "Torsional loosening",
    "bending":            "Bending-induced loosening",
}


def _priors_path() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(
        here, "..", "core", "databases", "literature_priors.json"))


def load_priors() -> dict:
    """Return the parsed literature_priors.json, or an empty stub on failure."""
    try:
        with open(_priors_path(), "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:
        return {"_error": str(exc), "entries": []}


# =============================================================================
# Pages
# =============================================================================

class _RegimePage(QWizardPage):
    def __init__(self, entries):
        super().__init__()
        self.setTitle("1 · Select loading regime")
        self.setSubTitle(
            "Pick the loading mode that best matches your experiment. "
            "Each regime points to a different family of literature priors.")
        self._entries = entries

        regimes = sorted({e.get("regime", "") for e in entries if e.get("regime")})
        self.regime_list = QListWidget()
        for r in regimes:
            it = QListWidgetItem(_REGIME_LABELS.get(r, r))
            it.setData(Qt.ItemDataRole.UserRole, r)
            n = sum(1 for e in entries if e.get("regime") == r)
            it.setToolTip(f"{n} reference paper(s) in this regime.")
            self.regime_list.addItem(it)

        self.regime_list.itemSelectionChanged.connect(self.completeChanged.emit)

        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("<b>Loading regime</b>"))
        lay.addWidget(self.regime_list, stretch=1)

        # PyQt6: the 4th arg (changedSignal) must be an actual bound signal,
        # not the string "currentRowChanged" — passing a string raises
        # TypeError and crashes the whole app when this wizard opens.
        self.registerField("regime*", self.regime_list,
                           "currentRow", self.regime_list.currentRowChanged)

    def isComplete(self):
        return self.regime_list.currentRow() >= 0

    def selected_regime(self) -> Optional[str]:
        it = self.regime_list.currentItem()
        return it.data(Qt.ItemDataRole.UserRole) if it else None


class _PaperPage(QWizardPage):
    def __init__(self, entries, regime_page: "_RegimePage"):
        super().__init__()
        self.setTitle("2 · Pick reference study")
        self.setSubTitle(
            "Choose the paper closest to your experimental conditions "
            "(bolt size, amplitude, frequency).")
        self._all = entries
        self._regime_page = regime_page

        self.paper_list = QListWidget()
        self.paper_list.itemSelectionChanged.connect(self._on_select)
        self.paper_list.itemSelectionChanged.connect(self.completeChanged.emit)

        self.detail = QTextEdit()
        self.detail.setReadOnly(True)
        self.detail.setMinimumHeight(160)

        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("<b>Reference papers in this regime</b>"))
        lay.addWidget(self.paper_list, stretch=2)
        lay.addWidget(QLabel("<b>Details</b>"))
        lay.addWidget(self.detail, stretch=1)

    def initializePage(self):
        regime = self._regime_page.selected_regime()
        self.paper_list.clear()
        for e in self._all:
            if e.get("regime") != regime:
                continue
            it = QListWidgetItem(e.get("label", e.get("id", "(unnamed)")))
            it.setData(Qt.ItemDataRole.UserRole, e)
            it.setToolTip(e.get("notes", ""))
            self.paper_list.addItem(it)
        if self.paper_list.count() > 0:
            self.paper_list.setCurrentRow(0)

    def _on_select(self):
        e = self.selected_entry()
        if not e:
            self.detail.clear()
            return
        html = (
            f"<p><b>{e.get('label', '')}</b><br>"
            f"<i>{e.get('paper', '')}</i><br>"
            f"DOI: {e.get('doi', 'n/a')}</p>"
            f"<p><b>Bolt:</b> {e.get('bolt', 'n/a')}<br>"
            f"<b>Loading:</b> {e.get('loading', 'n/a')}</p>"
            f"<p>{e.get('notes', '')}</p>"
        )
        self.detail.setHtml(html)

    def isComplete(self):
        return self.paper_list.currentRow() >= 0

    def selected_entry(self) -> Optional[dict]:
        it = self.paper_list.currentItem()
        return it.data(Qt.ItemDataRole.UserRole) if it else None


class _ReviewPage(QWizardPage):
    def __init__(self, paper_page: "_PaperPage"):
        super().__init__()
        self.setTitle("3 · Review priors")
        self.setSubTitle(
            "These values will pre-populate the calibration dialog. "
            "Bounds are default ± σ from the literature; you can still tighten "
            "them by hand before running the optimiser.")
        self._paper_page = paper_page

        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)

        self.params_group = QGroupBox("Suggested parameters (default · lo · hi)")
        self.params_group.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._params_layout = QGridLayout(self.params_group)
        self._params_layout.setSpacing(4)

        lay = QVBoxLayout(self)
        lay.addWidget(self.summary_label)
        lay.addWidget(self.params_group, stretch=1)

    def initializePage(self):
        e = self._paper_page.selected_entry() or {}
        self.summary_label.setText(
            f"<p><b>{e.get('label', '')}</b><br>"
            f"<i>{e.get('paper', '')}</i> · DOI {e.get('doi', 'n/a')}</p>")

        # clear grid
        while self._params_layout.count():
            w = self._params_layout.takeAt(0).widget()
            if w is not None:
                w.deleteLater()

        params = e.get("params", {}) or {}
        sigmas = e.get("bounds_sigma", {}) or {}

        self._params_layout.addWidget(QLabel("<b>Param</b>"), 0, 0)
        self._params_layout.addWidget(QLabel("<b>Default</b>"), 0, 1)
        self._params_layout.addWidget(QLabel("<b>Lo</b>"), 0, 2)
        self._params_layout.addWidget(QLabel("<b>Hi</b>"), 0, 3)
        for i, (name, default) in enumerate(params.items(), start=1):
            sigma = float(sigmas.get(name, abs(default) * 0.25))
            lo = max(default - sigma, default * 0.1) if default > 0 \
                else default - abs(sigma)
            hi = default + sigma
            self._params_layout.addWidget(QLabel(name), i, 0)
            self._params_layout.addWidget(QLabel(f"{default:.4g}"), i, 1)
            self._params_layout.addWidget(QLabel(f"{lo:.4g}"), i, 2)
            self._params_layout.addWidget(QLabel(f"{hi:.4g}"), i, 3)


# =============================================================================
# Wizard
# =============================================================================

class CalibrationWizardDialog(QWizard):
    """3-page wizard that returns a literature-grounded prior pack.

    Use ``selected_priors()`` after exec() returns Accepted to retrieve the
    chosen entry (with computed lo/hi bounds).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calibration Wizard — Literature Priors")
        self.setOption(QWizard.WizardOption.IndependentPages, False)
        self.setMinimumSize(640, 520)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

        priors = load_priors()
        entries = list(priors.get("entries", []) or [])
        if priors.get("_error"):
            entries = []

        self._regime = _RegimePage(entries)
        self._paper = _PaperPage(entries, self._regime)
        self._review = _ReviewPage(self._paper)

        self.addPage(self._regime)
        self.addPage(self._paper)
        self.addPage(self._review)

        self.setButtonText(QWizard.WizardButton.FinishButton,
                           "Use these settings")

    def selected_priors(self) -> Optional[dict]:
        e = self._paper.selected_entry()
        if not e:
            return None
        params = dict(e.get("params", {}) or {})
        sigmas = dict(e.get("bounds_sigma", {}) or {})
        bounds: dict = {}
        for name, default in params.items():
            sigma = float(sigmas.get(name, abs(default) * 0.25))
            if default > 0:
                lo = max(default - sigma, default * 0.1)
            else:
                lo = default - abs(sigma)
            hi = default + sigma
            if hi <= lo:
                hi = lo * 2.0 + 1e-12
            bounds[name] = (lo, hi)
        return {
            "id":     e.get("id", ""),
            "label":  e.get("label", ""),
            "params": params,
            "bounds": bounds,
        }
