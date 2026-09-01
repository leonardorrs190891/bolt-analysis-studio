from bolt_analysis_studio.gui.chrome.widgets.auto_combo import AutoComboBox


def test_auto_default_resolves_via_inference(qapp):
    c = AutoComboBox(["Coulomb", "Stribeck", "LuGre"],
                     inference_fn=lambda ctx: "Stribeck" if ctx.get("lubricated") else "Coulomb")
    c.set_context({"lubricated": True})
    assert c.is_auto is True
    assert c.current_resolved_value() == "Stribeck"        # inferido
    assert c.currentText().startswith("Auto")


def test_override_fixes_choice_and_emits(qapp):
    seen = []
    c = AutoComboBox(["Coulomb", "Stribeck"], inference_fn=lambda ctx: "Coulomb")
    c.value_changed.connect(seen.append)
    c.set_value("Stribeck")
    assert c.is_auto is False
    assert c.current_resolved_value() == "Stribeck"
    assert seen == ["Stribeck"]


def test_reset_to_auto(qapp):
    c = AutoComboBox(["Coulomb", "Stribeck"], inference_fn=lambda ctx: "Coulomb")
    c.set_value("Stribeck")
    c.reset_to_auto()
    assert c.is_auto is True
    assert c.current_resolved_value() == "Coulomb"


def test_no_inference_fn_defaults_first_option(qapp):
    c = AutoComboBox(["A", "B"])
    assert c.current_resolved_value() == "A"
