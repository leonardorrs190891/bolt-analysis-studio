"""Fase 5: após o wizard, o chrome popula a tree e navega para Model."""
from types import SimpleNamespace


def test_after_wizard_navigates_and_populates(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    model = SimpleNamespace(name="wiz",
                            elements=[SimpleNamespace(element_type="HEAD", id=1)])
    win = ChromeWindow()
    try:
        win._after_wizard(model)
        assert win.current_module == "Model"
        assert win.tree._model_node.childCount() == 1
    finally:
        win.close()


def test_autocombo_infers_from_context(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.auto_combo import AutoComboBox
    combo = AutoComboBox(["Newmark-β", "HHT-α"],
                         inference_fn=lambda ctx: "HHT-α" if ctx.get("damping") else "Newmark-β")
    combo.set_context({"damping": True})
    assert combo.current_resolved_value() == "HHT-α"
    combo.set_context({"damping": False})
    assert combo.current_resolved_value() == "Newmark-β"
