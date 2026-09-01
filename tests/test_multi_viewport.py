from PyQt6.QtWidgets import QLabel
from bolt_analysis_studio.gui.chrome.widgets.multi_viewport import MultiViewport


def test_default_layout_single(qapp):
    v = MultiViewport()
    assert v.layout_name() == "1"
    assert v.slot_count() == 1


def test_switch_to_2x2_has_four_slots(qapp):
    v = MultiViewport()
    v.set_layout("2x2")
    assert v.slot_count() == 4


def test_set_widget_and_active(qapp):
    seen = []
    v = MultiViewport()
    v.set_layout("1x2")
    v.active_changed.connect(seen.append)
    v.set_widget(1, QLabel("plot B"))
    v.set_active(1)
    assert v.active_index == 1
    assert seen[-1] == 1


def test_bad_layout_raises(qapp):
    v = MultiViewport()
    try:
        v.set_layout("3x3")
        assert False, "esperava ValueError"
    except ValueError:
        pass
