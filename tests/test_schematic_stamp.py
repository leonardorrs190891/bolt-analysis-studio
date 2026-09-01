"""Fase 3: SchematicView desenha gradiente + carimbo sem crashar."""


def test_stamp_toggle_default_off(qapp):
    from bolt_analysis_studio.gui.msd_builder import SchematicView
    view = SchematicView()
    assert view._stamp_enabled is False  # default inerte (backward-compat)


def test_set_title_block_and_render(qapp):
    from PyQt6.QtGui import QPixmap, QPainter
    from bolt_analysis_studio.gui.msd_builder import SchematicView
    view = SchematicView()
    view.set_title_block("M16_junker", "Model", "Coupled", "MAE 0.024")
    view.set_stamp_enabled(True)
    # renderiza offscreen: drawBackground/drawForeground não devem lançar
    pm = QPixmap(400, 300)
    p = QPainter(pm)
    view.render(p)
    p.end()
    assert view._title_block["model"] == "M16_junker"
    assert view._stamp_enabled is True
