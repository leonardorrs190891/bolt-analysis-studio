from PyQt6.QtWidgets import QLineEdit
from bolt_analysis_studio.gui.chrome.widgets.collapsible import CollapsibleGroup


def test_add_row_and_count(qapp):
    g = CollapsibleGroup("Global Loading")
    g.add_row("Preload F0", QLineEdit())
    g.add_row("Frequency", QLineEdit())
    assert g.row_count() == 2


def test_collapse_hides_body_and_emits(qapp):
    seen = []
    g = CollapsibleGroup("X")
    g.toggled.connect(seen.append)
    g.add_row("a", QLineEdit())
    assert g.is_collapsed() is False
    g.set_collapsed(True)
    assert g.is_collapsed() is True
    assert g._body.isVisibleTo(g) is False
    assert seen == [True]
