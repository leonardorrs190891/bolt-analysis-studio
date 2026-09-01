"""Fase 1: paleta Engineering Dark registrada e com contraste AA no corpo."""
from bolt_analysis_studio.gui.theme import Theme, PALETTES, THEME_DARK


def _lum(hexcol):
    hexcol = hexcol.lstrip("#")
    r, g, b = (int(hexcol[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    R, G, B = f(r), f(g), f(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B


def _ratio(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def test_engineering_palette_registered():
    assert "engineering" in PALETTES
    pal = PALETTES["engineering"]
    assert set(pal.keys()) == set(THEME_DARK.keys())  # mesmas 20 chaves canônicas


def test_engineering_body_text_contrast_AA():
    pal = PALETTES["engineering"]
    assert _ratio(pal["TEXT"], pal["BASE"]) >= 7.0        # AA/AAA corpo
    assert _ratio(pal["SUBTEXT"], pal["BASE"]) >= 4.5     # AA texto secundário


def test_engineering_accent_is_steel_blue():
    assert PALETTES["engineering"]["BLUE"].lower() == "#2f8fd0"


def test_set_theme_engineering_applies():
    try:
        Theme.set_theme("engineering")
        assert Theme.BASE == "#1e2023"
        assert Theme.is_dark() is True
    finally:
        Theme.set_theme("dark")


def test_stylesheet_has_numeric_mono_and_density():
    Theme._cached_stylesheet = None
    qss = Theme.get_stylesheet()
    assert "QLabel#numeric" in qss           # papel de valor numérico
    assert Theme.FONT_MONO.split(",")[0].strip("'\" ") in qss  # Consolas presente
