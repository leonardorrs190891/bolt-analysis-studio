import pytest
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QLineEdit
from bolt_analysis_studio.gui.chrome.widgets.property_inspector import ChromeInspector


@pytest.fixture(autouse=True)
def _clean_settings():
    """Isola o QSettings persistente entre testes (default = Basic)."""
    QSettings("BAS", "chrome").remove("inspector_level")
    yield
    QSettings("BAS", "chrome").remove("inspector_level")


def _specs():
    return [{"title": "Global Loading", "rows": [
        {"label": "Preload F0", "widget": QLineEdit(), "advanced": False, "help": "F_preload"},
        {"label": "VDI R-factor", "widget": QLineEdit(), "advanced": True, "help": ""},
    ]}]


def test_default_level_is_basic(qapp):
    insp = ChromeInspector()
    assert insp.level() == "Basic"


def test_basic_hides_advanced_rows(qapp):
    insp = ChromeInspector()
    insp.set_level("Basic")
    insp.show_groups(_specs())
    assert insp._visible_row_count() == 1        # so a Basic


def test_advanced_shows_all_and_emits(qapp):
    seen = []
    insp = ChromeInspector()
    insp.level_changed.connect(seen.append)
    insp.show_groups(_specs())
    insp.set_level("Advanced")
    assert insp._visible_row_count() == 2
    assert seen == ["Advanced"]


def test_level_persists_via_qsettings(qapp):
    insp = ChromeInspector()
    insp.set_level("Advanced")
    del insp
    insp2 = ChromeInspector()
    assert insp2.level() == "Advanced"
