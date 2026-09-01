from bolt_analysis_studio.gui.chrome.parameter_help import load_parameter_help, help_for


def test_catalog_loads_as_dict():
    cat = load_parameter_help()
    assert isinstance(cat, dict) and len(cat) >= 5


def test_help_for_known_and_unknown():
    assert "friction" in help_for("mu_static").lower()
    assert help_for("__nao_existe__") == ""


def test_all_values_are_short_strings():
    for k, v in load_parameter_help().items():
        assert isinstance(v, str) and v.strip()
        assert v.count("\n") <= 3
