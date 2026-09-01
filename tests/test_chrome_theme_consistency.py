"""Fase 1: chrome não carrega hex hardcoded — cores vêm do tema."""
import re

_HARD = re.compile(r"#[0-9a-fA-F]{6}")


def test_prompt_area_has_no_hardcoded_hex():
    import bolt_analysis_studio.gui.chrome.widgets.prompt_area as m
    src = open(m.__file__, encoding="utf-8").read()
    assert not _HARD.search(src), "PromptArea ainda tem hex hardcoded"


def test_module_bar_run_and_badge_have_no_hardcoded_hex():
    import bolt_analysis_studio.gui.chrome.widgets.module_bar as m
    src = open(m.__file__, encoding="utf-8").read()
    assert not _HARD.search(src)


def test_multi_viewport_has_no_hardcoded_hex():
    import bolt_analysis_studio.gui.chrome.widgets.multi_viewport as m
    src = open(m.__file__, encoding="utf-8").read()
    assert not _HARD.search(src)


def test_stylesheet_carries_chrome_object_rules():
    from bolt_analysis_studio.gui.theme import Theme
    Theme._cached_stylesheet = None
    qss = Theme.get_stylesheet()
    assert "#promptArea" in qss
    assert "#runButton" in qss
    assert "viewportSlot" in qss
