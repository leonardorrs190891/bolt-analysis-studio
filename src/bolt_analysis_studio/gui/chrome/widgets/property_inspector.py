"""ChromeInspector — Property Inspector CAE com toggle Basic/Advanced (spec §3.C)."""
from __future__ import annotations

from PyQt6.QtCore import QSettings, pyqtSignal
from PyQt6.QtWidgets import (QButtonGroup, QFormLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QVBoxLayout, QWidget)

from .collapsible import CollapsibleGroup
from ..parameter_help import help_for

_LEVELS = ("Basic", "Advanced")


class ChromeInspector(QWidget):
    level_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = QSettings("BAS", "chrome")
        level = self._settings.value("inspector_level", "Basic")
        self._level = level if level in _LEVELS else "Basic"
        self._rows = []          # (widget, advanced: bool)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        header = QHBoxLayout()
        header.addWidget(QLabel("Properties"))
        header.addStretch(1)
        self._btns = QButtonGroup(self)
        for lvl in _LEVELS:
            b = QPushButton(lvl)
            b.setObjectName("levelToggle")
            b.setCheckable(True)
            b.setChecked(lvl == self._level)
            b.clicked.connect(lambda _c, L=lvl: self.set_level(L))
            self._btns.addButton(b)
            header.addWidget(b)
        root.addLayout(header)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._host = QWidget()
        self._host_layout = QVBoxLayout(self._host)
        self._host_layout.addStretch(1)
        self._scroll.setWidget(self._host)
        root.addWidget(self._scroll, 1)

    def level(self) -> str:
        return self._level

    def set_level(self, level: str) -> None:
        if level not in _LEVELS or level == self._level:
            self._sync_buttons()
            return
        self._level = level
        self._settings.setValue("inspector_level", level)
        self._settings.sync()
        self._apply_visibility()
        self._sync_buttons()
        self.level_changed.emit(level)

    def show_groups(self, specs) -> None:
        while self._host_layout.count() > 1:   # mantem o stretch final
            item = self._host_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._rows = []
        for spec in specs:
            group = CollapsibleGroup(spec.get("title", ""))
            for row in spec.get("rows", []):
                widget = row["widget"]
                hk = row.get("help") or ""
                if hk and help_for(hk):
                    widget.setToolTip(help_for(hk))
                group.add_row(row.get("label", ""), widget, hk)
                self._rows.append((widget, bool(row.get("advanced", False))))
            self._host_layout.insertWidget(self._host_layout.count() - 1, group)
        self._apply_visibility()

    def _apply_visibility(self) -> None:
        show_adv = self._level == "Advanced"
        for widget, advanced in self._rows:
            visible = show_adv or not advanced
            widget.setVisible(visible)
            lbl = self._row_label(widget)
            if lbl is not None:
                lbl.setVisible(visible)

    def _row_label(self, widget):
        parent = widget.parentWidget()
        form = parent.layout() if parent is not None else None
        if isinstance(form, QFormLayout):
            return form.labelForField(widget)
        return None

    def _sync_buttons(self):
        for b in self._btns.buttons():
            b.setChecked(b.text() == self._level)

    def _visible_row_count(self) -> int:
        return sum(1 for w, _adv in self._rows if w.isVisibleTo(self))
