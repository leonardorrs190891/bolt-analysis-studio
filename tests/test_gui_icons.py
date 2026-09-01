"""Fase 2: loader de ícones SVG recolore por tema e cacheia."""
from PyQt6.QtGui import QIcon


def test_icon_returns_non_null_for_known_name(qapp):
    from bolt_analysis_studio.gui import icons
    ic = icons.icon("run", size=20)
    assert isinstance(ic, QIcon)
    assert not ic.isNull()
    assert ic.availableSizes()  # tem ao menos um pixmap renderizado


def test_icon_recolors_by_argument(qapp):
    from bolt_analysis_studio.gui import icons
    a = icons.icon("run", color="#ff0000", size=16).pixmap(16, 16).toImage()
    b = icons.icon("run", color="#00ff00", size=16).pixmap(16, 16).toImage()
    diff = any(a.pixel(x, y) != b.pixel(x, y)
               for x in range(16) for y in range(16))
    assert diff, "recolor não alterou nenhum pixel"


def test_unknown_icon_is_null_not_crash(qapp):
    from bolt_analysis_studio.gui import icons
    assert icons.icon("does-not-exist").isNull()


def test_svg_assets_use_fg_token():
    from pathlib import Path
    import bolt_analysis_studio
    root = Path(bolt_analysis_studio.__file__).resolve().parent / "resources" / "icons"
    svgs = list(root.glob("*.svg"))
    assert len(svgs) >= 8
    for p in svgs:
        assert "__FG__" in p.read_text(encoding="utf-8"), f"{p.name} sem __FG__"
