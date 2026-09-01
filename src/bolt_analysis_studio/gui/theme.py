"""
Central Theme Module for Bolt Analysis Studio v4.0
===================================================

Provides 3 switchable color themes:
- Dark (Catppuccin Mocha) - default
- Light (Catppuccin Latte)
- Green (corporate green/yellow/Ming)

All GUI modules import Theme from here. Theme.BLUE etc. are mutable
class attributes overwritten by set_theme(), so 330+ runtime references
automatically see the new values.

Prof. Leonardo Rosa Ribeiro da Silva, PhD
February 2026
"""

import json
from pathlib import Path
from typing import Callable, Dict, List, Optional

import matplotlib.pyplot as plt


# =============================================================================
# COLOR PALETTES
# =============================================================================

THEME_DARK = {
    "BASE": "#1e1e2e",
    "MANTLE": "#181825",
    "CRUST": "#11111b",
    "SURFACE0": "#313244",
    "SURFACE1": "#45475a",
    "SURFACE2": "#585b70",
    "TEXT": "#cdd6f4",
    "SUBTEXT": "#a6adc8",
    "OVERLAY": "#6c7086",
    "BLUE": "#89b4fa",
    "GREEN": "#a6e3a1",
    "RED": "#f38ba8",
    "PEACH": "#fab387",
    "YELLOW": "#f9e2af",
    "MAUVE": "#cba6f7",
    "TEAL": "#94e2d5",
    "PINK": "#f5c2e7",
    "SKY": "#89dceb",
    "LAVENDER": "#b4befe",
    "BUTTON_TEXT": "#11111b",
}

THEME_LIGHT = {
    "BASE": "#eff1f5",
    "MANTLE": "#e6e9ef",
    "CRUST": "#dce0e8",
    "SURFACE0": "#ccd0da",
    "SURFACE1": "#bcc0cc",
    "SURFACE2": "#acb0be",
    "TEXT": "#4c4f69",
    "SUBTEXT": "#5c5f77",
    "OVERLAY": "#6c6f85",
    "BLUE": "#1e66f5",
    "GREEN": "#40a02b",
    "RED": "#d20f39",
    "PEACH": "#fe640b",
    "YELLOW": "#df8e1d",
    "MAUVE": "#8839ef",
    "TEAL": "#179299",
    "PINK": "#ea76cb",
    "SKY": "#04a5e5",
    "LAVENDER": "#7287fd",
    "BUTTON_TEXT": "#eff1f5",
}

THEME_PETROBRAS = {
    "BASE": "#1a3a4a",
    "MANTLE": "#163347",
    "CRUST": "#112a3a",
    "SURFACE0": "#21576A",
    "SURFACE1": "#2a6a80",
    "SURFACE2": "#3a7a90",
    "TEXT": "#FFFFFF",
    "SUBTEXT": "#d0e8f0",
    "OVERLAY": "#6a9ab0",
    "BLUE": "#008542",
    "GREEN": "#008542",
    "RED": "#d42020",
    "PEACH": "#FDC82F",
    "YELLOW": "#FDC82F",
    "MAUVE": "#00a86b",
    "TEAL": "#20b080",
    "PINK": "#ff8080",
    "SKY": "#4db8d0",
    "LAVENDER": "#00b060",
    "BUTTON_TEXT": "#FFFFFF",
}

THEME_HIGH_CONTRAST = {
    # WCAG AA compliant: black/white background with saturated primaries.
    "BASE": "#000000",
    "MANTLE": "#0a0a0a",
    "CRUST": "#000000",
    "SURFACE0": "#1a1a1a",
    "SURFACE1": "#2e2e2e",
    "SURFACE2": "#5a5a5a",
    "TEXT": "#ffffff",
    "SUBTEXT": "#e0e0e0",
    "OVERLAY": "#a0a0a0",
    "BLUE": "#00e0ff",
    "GREEN": "#00ff66",
    "RED": "#ff4040",
    "PEACH": "#ffaa00",
    "YELLOW": "#ffee00",
    "MAUVE": "#ff66ff",
    "TEAL": "#00ffcc",
    "PINK": "#ff8fd1",
    "SKY": "#66ddff",
    "LAVENDER": "#c0a0ff",
    "BUTTON_TEXT": "#000000",
}

THEME_ENGINEERING = {
    # "Engineering Dark" — grafite azulado + acento aço dessaturado.
    # Mapeia os tokens da spec 2026-07-17 §1.1 nas 20 chaves canônicas.
    "BASE": "#1e2023",
    "MANTLE": "#191b1e",
    "CRUST": "#141518",
    "SURFACE0": "#26282d",
    "SURFACE1": "#2e3138",
    "SURFACE2": "#3c4047",
    "TEXT": "#d6d8dc",
    "SUBTEXT": "#a4a8af",
    "OVERLAY": "#7c8087",
    "BLUE": "#2f8fd0",       # ACENTO (seleção, foco, prompt, viewport ativo)
    "GREEN": "#3fae72",      # PASS
    "RED": "#d05356",        # FAIL / RUNAWAY
    "PEACH": "#d98a4a",
    "YELLOW": "#d4a53a",     # WARN
    "MAUVE": "#8a7fd0",
    "TEAL": "#3fae9e",
    "PINK": "#c77faa",
    "SKY": "#4aa6e0",        # acento hover
    "LAVENDER": "#9aa0c0",
    "BUTTON_TEXT": "#14161a",
}

PALETTES = {
    "dark": THEME_DARK,
    "light": THEME_LIGHT,
    "green": THEME_PETROBRAS,
    "high_contrast": THEME_HIGH_CONTRAST,
    "engineering": THEME_ENGINEERING,
}

# Palette display names for menus
PALETTE_NAMES = {
    "dark": "Dark (Catppuccin Mocha)",
    "light": "Light (Catppuccin Latte)",
    "green": "Green",
    "high_contrast": "High Contrast (WCAG AA)",
    "engineering": "Engineering Dark",
}


# =============================================================================
# THEME CLASS (mutable class attributes)
# =============================================================================

class Theme:
    """Application color theme with mutable class attributes.

    Every GUI module references Theme.BLUE, Theme.BASE, etc.
    ``set_theme()`` overwrites all 19 attributes from the selected palette,
    so all downstream code automatically sees the new colors.
    """

    # --- current palette name ---
    _current: str = "dark"
    _cached_stylesheet: Optional[str] = None

    # --- font family constants (same across all themes) ---
    FONT_SANS = "'Bahnschrift', 'Segoe UI', 'Tahoma', sans-serif"
    FONT_MONO = "'Consolas', 'Courier New', monospace"
    FONT_SERIF = "'Georgia', serif"

    # Primary font family name (for QFont constructor, no quoting/fallback).
    FONT_SANS_FAMILY = "Bahnschrift"
    FONT_MONO_FAMILY = "Consolas"

    # --- font size constants (in pt; used in inline QSS + QFont) ---
    FONT_SIZE_MICRO = 7       # axes tick labels in embedded charts
    FONT_SIZE_SMALL = 8       # summary stats, status badges, hint text
    FONT_SIZE_LABEL = 9       # default body text (base — densidade de estação)
    FONT_SIZE_SUBHEADING = 10 # group titles, secondary headings, hero badge
    FONT_SIZE_HEADING = 11    # primary headings, hero app label
    FONT_SIZE_LARGE = 13      # hero title, section headings, emphasized

    # --- layout/sizing constants (in px) ---
    HERO_BAR_HEIGHT = 52
    STATUS_BADGE_WIDTH = 80
    STATUS_BADGE_HEIGHT = 24
    TOOLBAR_ICON_SIZE = 20
    BUTTON_MIN_HEIGHT_PRIMARY = 36
    BUTTON_MIN_HEIGHT_TOOLBAR = 32
    BUTTON_MIN_HEIGHT_SMALL = 26

    # --- border radii (in px) ---
    BORDER_RADIUS_SM = 3
    BORDER_RADIUS_MD = 4
    BORDER_RADIUS_LG = 6
    BORDER_RADIUS_XL = 8

    # --- padding (CSS string shortcuts) ---
    PADDING_BUTTON = "6px 12px"
    PADDING_TOOLBAR = "4px 10px"
    PADDING_GROUP_BOX = "10px"
    PADDING_CONTENT = "10px"
    PADDING_PLACEHOLDER = "40px"
    PADDING_PLACEHOLDER_SM = "20px"

    # --- spacing (for QLayout.setSpacing, in px) ---
    SPACING_XS = 4
    SPACING_SM = 6
    SPACING_MD = 8
    SPACING_LG = 10
    SPACING_XL = 16

    # --- widget minimum widths (in px) ---
    SPINBOX_MIN_WIDTH = 80
    SCALE_SPINBOX_MIN_WIDTH = 110
    PRESET_BUTTON_MIN_WIDTH = 44
    COMBOBOX_MIN_WIDTH = 220

    # --- colour attributes (initialized to dark) ---
    BASE = THEME_DARK["BASE"]
    MANTLE = THEME_DARK["MANTLE"]
    CRUST = THEME_DARK["CRUST"]
    SURFACE0 = THEME_DARK["SURFACE0"]
    SURFACE1 = THEME_DARK["SURFACE1"]
    SURFACE2 = THEME_DARK["SURFACE2"]
    TEXT = THEME_DARK["TEXT"]
    SUBTEXT = THEME_DARK["SUBTEXT"]
    OVERLAY = THEME_DARK["OVERLAY"]
    BLUE = THEME_DARK["BLUE"]
    GREEN = THEME_DARK["GREEN"]
    RED = THEME_DARK["RED"]
    PEACH = THEME_DARK["PEACH"]
    YELLOW = THEME_DARK["YELLOW"]
    MAUVE = THEME_DARK["MAUVE"]
    TEAL = THEME_DARK["TEAL"]
    PINK = THEME_DARK["PINK"]
    SKY = THEME_DARK["SKY"]
    LAVENDER = THEME_DARK["LAVENDER"]
    BUTTON_TEXT = THEME_DARK["BUTTON_TEXT"]

    # --- callbacks ---
    _callbacks: List[Callable] = []

    # -----------------------------------------------------------------
    # Core API
    # -----------------------------------------------------------------

    @classmethod
    def set_theme(cls, name: str) -> None:
        """Switch to a named palette ('dark', 'light', 'green').

        Updates all 19 class attributes, rebuilds ELEMENT_VISUALS colors,
        and fires registered callbacks.
        """
        palette = PALETTES.get(name)
        if palette is None:
            raise ValueError(f"Unknown theme: {name!r}. Choose from {list(PALETTES)}")
        cls._current = name
        cls._cached_stylesheet = None
        for key, value in palette.items():
            setattr(cls, key, value)

        # Rebuild module-level captures that were frozen at import time
        _rebuild_element_visuals()

        # Notify listeners
        for cb in cls._callbacks:
            try:
                cb()
            except Exception:
                pass

    @classmethod
    def current_name(cls) -> str:
        """Return the active palette name."""
        return cls._current

    @classmethod
    def is_dark(cls) -> bool:
        """True when the current palette is visually dark."""
        return cls._current in ("dark", "green", "engineering")

    # -----------------------------------------------------------------
    # Stylesheet
    # -----------------------------------------------------------------

    @classmethod
    def get_stylesheet(cls) -> str:
        """Generate application stylesheet from current colors (cached)."""
        if cls._cached_stylesheet is not None:
            return cls._cached_stylesheet
        cls._cached_stylesheet = f"""
            QMainWindow {{
                background-color: {cls.BASE};
                color: {cls.TEXT};
            }}

            QWidget {{
                background-color: {cls.BASE};
                color: {cls.TEXT};
                font-family: {cls.FONT_SANS};
                font-size: 9pt;
            }}

            QToolTip {{
                background-color: {cls.SURFACE0};
                color: {cls.TEXT};
                border: 1px solid {cls.SURFACE2};
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 8pt;
            }}

            QLabel {{
                font-size: 9pt;
            }}

            QLabel#heading {{
                font-size: 11pt;
                font-weight: bold;
                color: {cls.BLUE};
            }}

            QLabel#subheading {{
                font-size: 10pt;
                font-weight: bold;
                color: {cls.TEXT};
            }}

            QTabWidget::pane {{
                border: 1px solid {cls.SURFACE1};
                background-color: {cls.BASE};
                border-radius: 4px;
            }}

            QTabBar::tab {{
                background-color: {cls.SURFACE0};
                color: {cls.SUBTEXT};
                padding: 7px 16px;
                margin-right: 3px;
                border: 1px solid {cls.SURFACE2};
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-size: 9pt;
            }}

            QTabBar::tab:selected {{
                background-color: {cls.SURFACE1};
                color: {cls.BLUE};
                border: 1px solid {cls.BLUE};
                border-bottom: 2px solid {cls.BLUE};
                font-weight: 600;
            }}

            QTabBar::tab:hover:!selected {{
                background-color: {cls.SURFACE1};
                color: {cls.TEXT};
            }}

            QGroupBox {{
                border: 1px solid {cls.SURFACE1};
                border-radius: 4px;
                margin-top: 12px;
                padding: 8px;
                font-size: 9pt;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 8px;
                color: {cls.BLUE};
                font-size: 9pt;
                font-weight: bold;
            }}

            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                background-color: {cls.SURFACE1};
                border: 1px solid {cls.SURFACE2};
                border-radius: 3px;
                padding: 4px 6px;
                color: {cls.TEXT};
                font-size: 9pt;
                min-height: 24px;
            }}

            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border: 1px solid {cls.BLUE};
            }}

            QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QComboBox:disabled {{
                background-color: {cls.SURFACE0};
                color: {cls.OVERLAY};
            }}

            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
                width: 24px;
            }}

            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}

            /* Spinbox step buttons — MUST define the subcontrols explicitly,
               otherwise styling the QAbstractSpinBox base (border/padding above)
               leaves the up/down buttons with a broken/zero hit region and
               clicking them does nothing. */
            QSpinBox::up-button, QDoubleSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 18px;
                border-left: 1px solid {cls.SURFACE2};
                border-top-right-radius: 3px;
                background-color: {cls.SURFACE2};
            }}
            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 18px;
                border-left: 1px solid {cls.SURFACE2};
                border-bottom-right-radius: 3px;
                background-color: {cls.SURFACE2};
            }}
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: {cls.BLUE};
            }}
            QSpinBox::up-button:pressed, QDoubleSpinBox::up-button:pressed,
            QSpinBox::down-button:pressed, QDoubleSpinBox::down-button:pressed {{
                background-color: {cls.SURFACE1};
            }}
            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
                image: none;
                width: 0; height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 6px solid {cls.TEXT};
            }}
            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
                image: none;
                width: 0; height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {cls.TEXT};
            }}

            QComboBox QAbstractItemView {{
                background-color: {cls.SURFACE0};
                border: 1px solid {cls.SURFACE2};
                border-radius: 4px;
                selection-background-color: {cls.SURFACE1};
                selection-color: {cls.BLUE};
                padding: 4px;
            }}

            QComboBox QAbstractItemView::item {{
                padding: 6px 12px;
                min-height: 24px;
            }}

            QComboBox QAbstractItemView::item:hover {{
                background-color: {cls.SURFACE1};
            }}

            QPushButton {{
                background-color: {cls.SURFACE1};
                color: {cls.TEXT};
                border: 1px solid {cls.SURFACE2};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 9pt;
            }}

            QPushButton:hover {{
                background-color: {cls.SURFACE2};
                border-color: {cls.BLUE};
            }}

            QPushButton:pressed {{
                background-color: {cls.SURFACE0};
            }}

            QPushButton:disabled {{
                background-color: {cls.SURFACE0};
                color: {cls.OVERLAY};
            }}

            QPushButton:checked {{
                background-color: {cls.BLUE};
                color: {cls.BUTTON_TEXT};
                border: 1px solid {cls.BLUE};
            }}

            QPushButton:checked:hover {{
                background-color: {cls.LAVENDER};
                border-color: {cls.LAVENDER};
            }}

            QPushButton#primary {{
                background-color: {cls.BLUE};
                color: {cls.BUTTON_TEXT};
                border: 1px solid {cls.BLUE};
            }}

            QPushButton#primary:hover {{
                background-color: {cls.LAVENDER};
            }}

            QPushButton#primary:disabled {{
                background-color: {cls.SURFACE1};
                color: {cls.OVERLAY};
            }}

            QPushButton#danger {{
                background-color: {cls.RED};
                color: {cls.BUTTON_TEXT};
                border: 1px solid {cls.RED};
            }}

            QPushButton#danger:hover {{
                background-color: {cls.PINK};
            }}

            QPushButton#danger:disabled {{
                background-color: {cls.SURFACE1};
                color: {cls.OVERLAY};
            }}

            QPushButton#success {{
                background-color: {cls.GREEN};
                color: {cls.BUTTON_TEXT};
                border: 1px solid {cls.GREEN};
            }}

            QPushButton#success:hover {{
                background-color: {cls.TEAL};
            }}

            QPushButton#success:disabled {{
                background-color: {cls.SURFACE1};
                color: {cls.OVERLAY};
            }}

            QProgressBar {{
                border: 2px solid {cls.SURFACE2};
                border-radius: 6px;
                text-align: center;
                background-color: {cls.SURFACE0};
                min-height: 24px;
                font-size: 9pt;
                font-weight: bold;
                color: {cls.TEXT};
            }}

            QProgressBar::chunk {{
                background-color: {cls.BLUE};
                border-radius: 4px;
            }}

            QScrollBar:vertical {{
                background-color: {cls.SURFACE0};
                width: 12px;
                border-radius: 6px;
            }}

            QScrollBar::handle:vertical {{
                background-color: {cls.SURFACE2};
                border-radius: 6px;
                min-height: 30px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {cls.OVERLAY};
            }}

            QScrollBar:horizontal {{
                background-color: {cls.SURFACE0};
                height: 12px;
                border-radius: 6px;
            }}

            QScrollBar::handle:horizontal {{
                background-color: {cls.SURFACE2};
                border-radius: 6px;
                min-width: 30px;
            }}

            QTableWidget {{
                background-color: {cls.BASE};
                gridline-color: {cls.SURFACE1};
                border: 1px solid {cls.SURFACE1};
            }}

            QTableWidget::item {{
                padding: 4px;
            }}

            QTableWidget::item:selected {{
                background-color: {cls.SURFACE1};
                color: {cls.BLUE};
            }}

            QHeaderView::section {{
                background-color: {cls.SURFACE0};
                color: {cls.BLUE};
                padding: 6px;
                border: none;
                border-right: 1px solid {cls.SURFACE1};
                font-weight: bold;
            }}

            QTreeWidget {{
                background-color: {cls.BASE};
                border: 1px solid {cls.SURFACE1};
                border-radius: 4px;
                outline: none;
            }}

            QTreeWidget::item {{
                padding: 6px 8px;
                border-radius: 4px;
                margin: 1px 4px;
            }}

            QTreeWidget::item:hover {{
                background-color: {cls.SURFACE0};
            }}

            QTreeWidget::item:selected {{
                background-color: {cls.SURFACE1};
                color: {cls.BLUE};
            }}

            QTreeWidget::item:selected:hover {{
                background-color: {cls.SURFACE2};
            }}

            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {{
                border-image: none;
                image: none;
            }}

            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {{
                border-image: none;
                image: none;
            }}

            QCheckBox {{
                spacing: 8px;
                padding: 4px;
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {cls.SURFACE2};
                background-color: {cls.SURFACE0};
            }}

            QCheckBox::indicator:hover {{
                border-color: {cls.BLUE};
                background-color: {cls.SURFACE1};
            }}

            QCheckBox::indicator:checked {{
                background-color: {cls.BLUE};
                border-color: {cls.BLUE};
            }}

            QCheckBox::indicator:checked:hover {{
                background-color: {cls.LAVENDER};
                border-color: {cls.LAVENDER};
            }}

            QCheckBox::indicator:disabled {{
                background-color: {cls.SURFACE0};
                border-color: {cls.SURFACE1};
            }}

            QSlider::groove:horizontal {{
                background-color: {cls.SURFACE0};
                height: 6px;
                border-radius: 3px;
            }}

            QSlider::handle:horizontal {{
                background-color: {cls.BLUE};
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }}

            QSlider::handle:horizontal:hover {{
                background-color: {cls.LAVENDER};
            }}

            QSlider::sub-page:horizontal {{
                background-color: {cls.BLUE};
                border-radius: 3px;
            }}

            QStatusBar {{
                background-color: {cls.MANTLE};
                color: {cls.SUBTEXT};
                border-top: 1px solid {cls.SURFACE1};
            }}

            QMenuBar {{
                background-color: {cls.MANTLE};
                color: {cls.TEXT};
                padding: 2px;
            }}

            QMenuBar::item {{
                padding: 4px 8px;
            }}

            QMenuBar::item:selected {{
                background-color: {cls.SURFACE1};
            }}

            QMenu {{
                background-color: {cls.SURFACE0};
                border: 1px solid {cls.SURFACE1};
                padding: 4px;
            }}

            QMenu::item {{
                padding: 6px 24px;
            }}

            QMenu::item:selected {{
                background-color: {cls.SURFACE1};
                color: {cls.BLUE};
            }}

            QToolBar {{
                background-color: {cls.MANTLE};
                border: none;
                spacing: 4px;
                padding: 4px;
            }}

            QToolButton {{
                background-color: transparent;
                border: none;
                padding: 4px;
                border-radius: 4px;
            }}

            QToolButton:hover {{
                background-color: {cls.SURFACE1};
            }}

            QToolButton:pressed {{
                background-color: {cls.SURFACE2};
            }}

            QToolButton:checked {{
                background-color: {cls.BLUE};
                color: {cls.BUTTON_TEXT};
                border: 1px solid {cls.BLUE};
                border-radius: 4px;
            }}

            QToolButton:checked:hover {{
                background-color: {cls.LAVENDER};
                border-color: {cls.LAVENDER};
            }}

            QSplitter::handle {{
                background-color: {cls.SURFACE1};
            }}

            QSplitter::handle:hover {{
                background-color: {cls.BLUE};
            }}

            QSplitter::handle:pressed {{
                background-color: {cls.BLUE};
            }}

            QSplitter::handle:horizontal {{
                width: 10px;
                border-left: 1px solid {cls.SURFACE2};
                border-right: 1px solid {cls.SURFACE2};
            }}

            QSplitter::handle:vertical {{
                height: 10px;
                border-top: 1px solid {cls.SURFACE2};
                border-bottom: 1px solid {cls.SURFACE2};
            }}

            QLabel#value {{
                font-family: {cls.FONT_MONO};
                color: {cls.GREEN};
            }}

            QFrame#separator {{
                background-color: {cls.SURFACE1};
            }}

            QFrame#hero_bar {{
                background-color: {cls.MANTLE};
                border-bottom: 1px solid {cls.SURFACE1};
            }}

            QLabel#elementHeader {{
                color: {cls.BLUE};
                background-color: {cls.SURFACE0};
                padding: 6px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
            }}

            QFrame#importBar {{
                background-color: {cls.MANTLE};
                border-radius: {cls.BORDER_RADIUS_MD}px;
            }}

            QWidget#minimap {{
                background-color: {cls.BASE};
                border: 1px solid {cls.SURFACE1};
                border-radius: 3px;
            }}

            /* Reusable info/result panel — themed via QSS so it never freezes
               the startup palette. Apply with setObjectName("themedPanel"). */
            QTextEdit#themedPanel, QLabel#themedPanel, QFrame#themedPanel {{
                background-color: {cls.MANTLE};
                border: 1px solid {cls.SURFACE1};
                border-radius: {cls.BORDER_RADIUS_MD}px;
                padding: {cls.SPACING_MD}px;
                color: {cls.TEXT};
            }}

            QLabel#heroAppLabel {{
                color: {cls.SUBTEXT};
                font-size: 11px;
            }}

            QLabel#heroTitle {{
                color: {cls.TEXT};
                font-size: 13px;
                font-weight: bold;
            }}

            QLabel#placeholder {{
                color: {cls.OVERLAY};
                font-size: {cls.FONT_SIZE_HEADING}pt;
                padding: {cls.PADDING_PLACEHOLDER};
                border: 2px dashed {cls.SURFACE1};
                border-radius: {cls.BORDER_RADIUS_XL}px;
            }}

            QLabel#modalPlaceholder {{
                color: {cls.OVERLAY};
                font-size: {cls.FONT_SIZE_LABEL}pt;
                padding: {cls.PADDING_PLACEHOLDER_SM};
            }}

            QLabel#caption {{
                color: {cls.SUBTEXT};
                font-size: 10px;
            }}

            QLabel#summaryValue {{
                font-family: {cls.FONT_MONO};
                font-size: {cls.FONT_SIZE_SMALL}pt;
            }}

            QLabel#summaryKey {{
                color: {cls.SUBTEXT};
                font-size: {cls.FONT_SIZE_SMALL}pt;
            }}

            /* Papel "numeric": valores numéricos em monoespaçada à direita
               (tipografia de instrumento — dígitos alinham em coluna). */
            QLabel#numeric, QLineEdit#numeric {{
                font-family: {cls.FONT_MONO};
                qproperty-alignment: 'AlignRight | AlignVCenter';
            }}

            /* Densidade de estação de trabalho. */
            QTreeWidget::item {{ padding: 1px 0; }}
            QToolBar {{ spacing: 2px; }}

            /* Chrome V2: cores via tema (não mais hex hardcoded). */
            QWidget#promptArea {{ background-color: {cls.BLUE}; }}
            QWidget#promptArea QLabel {{ color: {cls.BUTTON_TEXT}; }}

            QPushButton#runButton {{ color: {cls.GREEN}; font-weight: 600; }}

            QFrame#viewportSlot {{ border: 1px solid {cls.SURFACE2}; }}
            QFrame#viewportSlot[active="true"] {{ border: 2px solid {cls.BLUE}; }}

            QLabel#badgePass {{ background-color: {cls.GREEN}; color: {cls.BUTTON_TEXT}; border-radius: 3px; padding: 0 6px; }}
            QLabel#badgeWarn {{ background-color: {cls.YELLOW}; color: #141518; border-radius: 3px; padding: 0 6px; }}
            QLabel#badgeFail {{ background-color: {cls.RED}; color: {cls.BUTTON_TEXT}; border-radius: 3px; padding: 0 6px; }}
            QLabel#badgeInfo {{ background-color: {cls.BLUE}; color: {cls.BUTTON_TEXT}; border-radius: 3px; padding: 0 6px; }}

            /* Trilha de passos do workflow (módulos numerados) — pílulas com
               contorno; passo atual = pílula azul preenchida. */
            QToolButton#moduleStep {{
                padding: 5px 14px; margin: 0 1px;
                border: 1px solid {cls.SURFACE2}; border-radius: 5px;
                background-color: {cls.SURFACE0}; color: {cls.SUBTEXT};
            }}
            QToolButton#moduleStep:hover {{ color: {cls.TEXT}; border-color: {cls.SUBTEXT}; }}
            QToolButton#moduleStep:checked {{
                color: {cls.BUTTON_TEXT}; background-color: {cls.BLUE};
                border-color: {cls.BLUE}; font-weight: 600;
            }}
            QToolButton#nextStep {{ color: {cls.BLUE}; font-weight: 600; padding: 5px 12px; }}
            QToolButton#nextStep:hover {{ background-color: {cls.SURFACE1}; }}

            /* Segmented toggle Basic/Advanced do inspector — contornos claros. */
            QPushButton#levelToggle {{
                border: 1px solid {cls.SURFACE2}; border-radius: 4px;
                padding: 3px 14px; background-color: {cls.SURFACE0}; color: {cls.SUBTEXT};
            }}
            QPushButton#levelToggle:hover {{ color: {cls.TEXT}; }}
            QPushButton#levelToggle:checked {{
                background-color: {cls.BLUE}; color: {cls.BUTTON_TEXT};
                border-color: {cls.BLUE}; font-weight: 600;
            }}

            /* Barra de título dos docks laterais + cabeçalho de mensagens. */
            QWidget#dockTitle {{ background-color: {cls.SURFACE1}; }}
            QLabel#dockTitleLabel {{ color: {cls.SUBTEXT}; font-size: 8pt; font-weight: 600; }}
            QToolButton#dockCollapse, QToolButton#dockClose, QToolButton#msgCollapse {{
                border: none; color: {cls.SUBTEXT}; padding: 1px 5px;
            }}
            QToolButton#dockCollapse:hover, QToolButton#dockClose:hover,
            QToolButton#msgCollapse:hover {{
                color: {cls.TEXT}; background-color: {cls.SURFACE2}; border-radius: 3px;
            }}
        """
        return cls._cached_stylesheet

    # -----------------------------------------------------------------
    # Inline-stylesheet helpers (for widgets whose colour changes at runtime)
    # -----------------------------------------------------------------

    @classmethod
    def status_badge_stylesheet(cls, bg_color: str) -> str:
        """Return a stylesheet string for the project-status badge.

        The badge's background changes per state (NEW/SAVED/MODIFIED/ERROR),
        so it can't live in the cached stylesheet.  Everything else is pulled
        from the current theme constants.
        """
        return (
            f"background-color: {bg_color};"
            f"color: {cls.BASE};"
            f"border-radius: {cls.BORDER_RADIUS_MD}px;"
            "font-size: 10px;"
            "font-weight: bold;"
        )

    @classmethod
    def summary_value_stylesheet(cls, color: str) -> str:
        """Color-only override for ``QLabel#summaryValue`` (font from QSS)."""
        return f"color: {color};"

    # -----------------------------------------------------------------
    # Matplotlib helpers
    # -----------------------------------------------------------------

    @classmethod
    def get_matplotlib_style_name(cls) -> str:
        """Return the base matplotlib style to use."""
        if cls.is_dark():
            return 'dark_background'
        return 'seaborn-v0_8-whitegrid'

    @classmethod
    def get_plot_style(cls) -> Dict[str, object]:
        """Return an rcParams dict for matplotlib from current colors."""
        return {
            'figure.facecolor': cls.BASE,
            'axes.facecolor': cls.SURFACE0,
            'axes.edgecolor': cls.SURFACE2,
            'axes.labelcolor': cls.TEXT,
            'axes.titlecolor': cls.TEXT,
            'xtick.color': cls.SUBTEXT,
            'ytick.color': cls.SUBTEXT,
            'text.color': cls.TEXT,
            'grid.color': cls.SURFACE1,
            'grid.alpha': 0.5 if cls.is_dark() else 0.3,
            'legend.facecolor': cls.SURFACE0,
            'legend.edgecolor': cls.SURFACE2,
            'legend.labelcolor': cls.TEXT,
            'font.family': 'sans-serif',
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 11,
            'legend.fontsize': 9,
            'figure.dpi': 100,
            'savefig.dpi': 300,
            'savefig.bbox': 'tight',
            'savefig.facecolor': cls.BASE,
        }

    @classmethod
    def get_plot_colors(cls) -> Dict[str, str]:
        """Return the COLORS dict used by loosening_plots / contact_plots."""
        return {
            'background': cls.BASE,
            'surface': cls.SURFACE0,
            'overlay': cls.OVERLAY,
            'text': cls.TEXT,
            'subtext': cls.SUBTEXT,
            'red': cls.RED,
            'peach': cls.PEACH,
            'yellow': cls.YELLOW,
            'green': cls.GREEN,
            'teal': cls.TEAL,
            'blue': cls.BLUE,
            'mauve': cls.MAUVE,
            'pink': cls.PINK,
            'lavender': cls.LAVENDER,
            'sapphire': cls.SKY,  # mapped to SKY
        }

    @classmethod
    def get_line_colors(cls) -> List[str]:
        """Return ordered list of line colors for multi-series plots."""
        return [
            cls.BLUE, cls.GREEN, cls.PEACH, cls.MAUVE,
            cls.TEAL, cls.PINK, cls.YELLOW, cls.SKY,
        ]

    @classmethod
    def get_theme_dict(cls) -> Dict[str, str]:
        """Return a THEME dict (uppercase keys) for plot_manager compat."""
        return {
            "BASE": cls.BASE,
            "MANTLE": cls.MANTLE,
            "CRUST": cls.CRUST,
            "SURFACE0": cls.SURFACE0,
            "SURFACE1": cls.SURFACE1,
            "SURFACE2": cls.SURFACE2,
            "TEXT": cls.TEXT,
            "SUBTEXT": cls.SUBTEXT,
            "OVERLAY": cls.OVERLAY,
            "BLUE": cls.BLUE,
            "GREEN": cls.GREEN,
            "RED": cls.RED,
            "PEACH": cls.PEACH,
            "YELLOW": cls.YELLOW,
            "MAUVE": cls.MAUVE,
            "TEAL": cls.TEAL,
            "PINK": cls.PINK,
            "SKY": cls.SKY,
            "LAVENDER": cls.LAVENDER,
            "BUTTON_TEXT": cls.BUTTON_TEXT,
        }

    # -----------------------------------------------------------------
    # Callback system
    # -----------------------------------------------------------------

    @classmethod
    def register_callback(cls, fn: Callable) -> None:
        """Register a function to call when the theme changes."""
        if fn not in cls._callbacks:
            cls._callbacks.append(fn)

    @classmethod
    def unregister_callback(cls, fn: Callable) -> None:
        """Remove a previously registered callback."""
        try:
            cls._callbacks.remove(fn)
        except ValueError:
            pass

    # -----------------------------------------------------------------
    # Persistence
    # -----------------------------------------------------------------

    _PREFS_DIR = Path.home() / ".bolt_analysis_studio"
    _PREFS_FILE = _PREFS_DIR / "preferences.json"

    @classmethod
    def save_theme_preference(cls) -> None:
        """Persist the current theme name to disk."""
        try:
            cls._PREFS_DIR.mkdir(parents=True, exist_ok=True)
            prefs: Dict = {}
            if cls._PREFS_FILE.exists():
                with open(cls._PREFS_FILE, "r", encoding="utf-8") as f:
                    prefs = json.load(f)
            prefs["theme"] = cls._current
            with open(cls._PREFS_FILE, "w", encoding="utf-8") as f:
                json.dump(prefs, f, indent=2)
        except Exception:
            pass

    @classmethod
    def load_theme_preference(cls) -> str:
        """Load saved theme name (returns 'dark' if none saved)."""
        try:
            if cls._PREFS_FILE.exists():
                with open(cls._PREFS_FILE, "r", encoding="utf-8") as f:
                    prefs = json.load(f)
                name = prefs.get("theme", "dark")
                if name in PALETTES:
                    return name
        except Exception:
            pass
        return "dark"


# =============================================================================
# ELEMENT_VISUALS REBUILD
# =============================================================================

# Mapping: element key -> Theme attribute name for its color
_ELEMENT_COLOR_MAP_V1 = {
    "HEAD": "BLUE",
    "SHANK": "BLUE",
    "THREAD": "MAUVE",
    "NUT": "BLUE",
    "WASHER": "SKY",
    "FLANGE": "GREEN",
    "GASKET": "PEACH",
    "CONTACT": "YELLOW",
    "GROUND": "SURFACE2",
}

_ELEMENT_COLOR_MAP_V2 = {
    "HEAD": "BLUE",
    "SHANK": "BLUE",
    "NUT": "GREEN",
    "WASHER": "MAUVE",
    "FLANGE": "TEAL",
    "GASKET": "PEACH",
    "THREAD": "YELLOW",
    "BEARING_HEAD": "RED",
    "BEARING_NUT": "RED",
    "FLANGE_FLANGE": "MAUVE",
    "WASHER_CONTACT": "MAUVE",
    "GASKET_CONTACT": "PEACH",
    "GENERIC_CONTACT": "RED",
    "GROUND": "OVERLAY",
}


def _rebuild_element_visuals() -> None:
    """Update .color on ELEMENT_VISUALS dicts in msd_builder and msd_builder_v2.

    Called by ``set_theme()`` after class attributes are updated.
    Uses late imports to avoid circular dependencies.
    """
    # --- msd_builder (unified) ---
    try:
        from bolt_analysis_studio.gui import msd_builder
        visuals = getattr(msd_builder, "ELEMENT_VISUALS", None)
        if visuals:
            # Use v2 color map (more comprehensive)
            for key, attr in _ELEMENT_COLOR_MAP_V2.items():
                if key in visuals:
                    visuals[key].color = getattr(Theme, attr)
    except Exception:
        pass
