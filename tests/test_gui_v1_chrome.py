"""Fase 0: chrome da V1 sem emoji e sem numeração nas abas.

Nota de harness: `BoltAnalysisStudio.closeEvent` abre um `QMessageBox.question`
modal ("tem certeza que quer fechar?") que TRAVA em modo headless/offscreen —
ninguém clica o botão. A fixture `_auto_confirm_close` responde Yes
automaticamente para que `win.close()` não bloqueie os testes.
"""
import re

import pytest
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QGroupBox, QMessageBox

# Cobre setas (2190-21FF), técnico misc ⏹ (2300-23FF), geométrico ▶■● (25A0-25FF),
# símbolos/dingbats (2600-27BF), símbolos-setas (2B00-2BFF), seletor de variação
# (FE0F) e emoji (1F000-1FAFF).
_EMOJI = re.compile(
    "[←-⇿⌀-⏿■-◿☀-➿⬀-⯿️"
    "\U0001F000-\U0001FAFF]")


@pytest.fixture(autouse=True)
def _auto_confirm_close(monkeypatch):
    monkeypatch.setattr(
        QMessageBox, "question",
        lambda *a, **k: QMessageBox.StandardButton.Yes)
    yield


def test_tab_titles_have_no_emoji_or_numbering(qapp):
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    win = BoltAnalysisStudio()
    try:
        titles = [win.tab_widget.tabText(i) for i in range(win.tab_widget.count())]
    finally:
        win.close()
    assert titles[:4] == ["Project", "Model Builder", "Solver", "Results"]
    for t in titles:
        assert not _EMOJI.search(t), f"emoji em aba: {t!r}"
        assert not re.match(r"^\d+\.\s", t), f"numeração em aba: {t!r}"


def test_window_title_has_no_emoji(qapp):
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    win = BoltAnalysisStudio()
    try:
        assert "🔩" not in win.windowTitle()
        assert "Bolt Analysis Studio" in win.windowTitle()
    finally:
        win.close()


def test_no_emoji_in_any_action(qapp):
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    win = BoltAnalysisStudio()
    try:
        offenders = [a.text() for a in win.findChildren(QAction)
                     if a.text() and _EMOJI.search(a.text())]
    finally:
        win.close()
    assert offenders == [], f"ações com emoji: {offenders}"


def test_no_emoji_in_group_boxes(qapp):
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    win = BoltAnalysisStudio()
    try:
        offenders = [g.title() for g in win.findChildren(QGroupBox)
                     if g.title() and _EMOJI.search(g.title())]
    finally:
        win.close()
    assert offenders == [], f"group boxes com emoji: {offenders}"


def test_results_subtabs_have_no_emoji(qapp):
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    win = BoltAnalysisStudio()
    try:
        rt = win.results_tab.right_tabs
        offenders = [rt.tabText(i) for i in range(rt.count())
                     if _EMOJI.search(rt.tabText(i))]
    finally:
        win.close()
    assert offenders == [], f"sub-abas de Results com emoji: {offenders}"


def test_run_button_is_not_oversized(qapp):
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    win = BoltAnalysisStudio()
    try:
        assert win.solver_tab.run_btn.minimumHeight() <= 36
        assert "14pt" not in (win.solver_tab.run_btn.styleSheet() or "")
    finally:
        win.close()


def test_result_canvases_have_nav_toolbars(qapp):
    from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    win = BoltAnalysisStudio()
    try:
        toolbars = win.results_tab.findChildren(NavigationToolbar2QT)
    finally:
        win.close()
    assert len(toolbars) >= 2, "faltam toolbars matplotlib nos canvases de resultado"


def test_contact_dialog_uses_modern_backend():
    import bolt_analysis_studio.gui.contact_builder_dialog as m
    src = open(m.__file__, encoding="utf-8").read()
    assert "backend_qt5agg" not in src


def test_v1_toolbar_actions_have_icons(qapp):
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    from PyQt6.QtWidgets import QToolBar
    win = BoltAnalysisStudio()
    try:
        main_tb = next(tb for tb in win.findChildren(QToolBar)
                       if tb.windowTitle() == "Main Toolbar")
        acts = [a for a in main_tb.actions() if a.text()]
        assert acts and all(not a.icon().isNull() for a in acts)
    finally:
        win.close()


def test_run_app_sets_window_icon():
    from pathlib import Path
    src = Path(__file__).resolve().parent.parent / "run_app.py"
    assert "setWindowIcon" in src.read_text(encoding="utf-8")
