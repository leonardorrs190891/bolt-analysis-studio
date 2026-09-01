"""Fase 3: message area com abas Messages / Job Log."""


def test_message_area_channels(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.message_area import MessageArea
    ma = MessageArea()
    labels = [ma._tabs.tabText(i) for i in range(ma._tabs.count())]
    assert labels == ["Messages", "Job Log"]


def test_append_and_read(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.message_area import MessageArea
    ma = MessageArea()
    ma.append("preflight ok", "messages")
    ma.append("cycle 100/1000", "job")
    assert "preflight ok" in ma._views["messages"].toPlainText()
    assert "cycle 100/1000" in ma._views["job"].toPlainText()


def test_clear_channel(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.message_area import MessageArea
    ma = MessageArea()
    ma.append("x", "job")
    ma.clear_channel("job")
    assert ma._views["job"].toPlainText() == ""


def test_chrome_hosts_message_area(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        assert hasattr(win, "messages")
        win.messages.append("hello")
        assert "hello" in win.messages._views["messages"].toPlainText()
    finally:
        win.close()


def test_panels_submenu_has_hide_toggles(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        view = next(m.menu() for m in win.menuBar().actions()
                    if m.text() == "Exibir")
        panels = next((a.menu() for a in view.actions()
                       if a.text() == "Painéis"), None)
        assert panels is not None
        labels = [a.text() for a in panels.actions()]
        assert "Model Tree" in labels and "Properties" in labels
        assert any("mensagens" in L.lower() for L in labels)
        # o toggle realmente esconde/mostra o dock (bug do toggleViewAction nativo)
        act = next(a for a in panels.actions() if a.text() == "Model Tree")
        act.setChecked(False)
        assert win._tree_dock.isHidden()
        act.setChecked(True)
        assert not win._tree_dock.isHidden()
    finally:
        win.close()


def test_messages_dock_is_hide_only_not_closable(qapp):
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QDockWidget
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        feats = win._msg_dock.features()
        assert not (feats & QDockWidget.DockWidgetFeature.DockWidgetClosable)
        # está na parte inferior
        assert win.dockWidgetArea(win._msg_dock) == Qt.DockWidgetArea.BottomDockWidgetArea
    finally:
        win.close()


def test_side_panels_have_collapse_and_close_titlebar(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.dock_title_bar import DockTitleBar
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        for dock in (win._tree_dock, win._inspector_dock):
            tb = dock.titleBarWidget()
            assert isinstance(tb, DockTitleBar)          # barra custom
            assert tb._close is not None                 # botão fechar (✕)
            tb.toggle_collapsed()                        # colapsar encolhe a largura
            assert tb.is_collapsed() and dock.maximumWidth() <= 40
            tb.toggle_collapsed()                        # expande de volta
            assert not tb.is_collapsed() and dock.maximumWidth() > 40
    finally:
        win.close()


def test_elements_palette_on_right_with_titlebar(qapp):
    from PyQt6.QtCore import Qt
    from bolt_analysis_studio.gui.chrome.widgets.dock_title_bar import DockTitleBar
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        assert win.dockWidgetArea(win._palette_dock) == \
            Qt.DockWidgetArea.RightDockWidgetArea            # ao lado de Properties
        assert isinstance(win._palette_dock.titleBarWidget(), DockTitleBar)
        view = next(m.menu() for m in win.menuBar().actions() if m.text() == "Exibir")
        panels = next(a.menu() for a in view.actions() if a.text() == "Painéis")
        assert "Elements" in [a.text() for a in panels.actions()]
    finally:
        win.close()


def test_prompt_flows_into_messages(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        win.prompt.set_prompt("Modelo criado teste 123")
        assert "Modelo criado teste 123" in win.messages._views["messages"].toPlainText()
    finally:
        win.close()


def test_message_area_collapse_toggle(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.message_area import MessageArea
    ma = MessageArea()
    assert not ma.is_collapsed()
    ma.toggle_collapsed()
    assert ma.is_collapsed() and ma._tabs.isHidden()
    ma.toggle_collapsed()
    assert not ma.is_collapsed() and not ma._tabs.isHidden()


def test_run_reveals_messages_dock(qapp):
    from PyQt6.QtWidgets import QMessageBox
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    QMessageBox.question = staticmethod(lambda *a, **k: QMessageBox.StandardButton.Yes)
    win = ChromeWindow()
    try:
        win._msg_dock.hide()
        assert win._msg_dock.isHidden()
        win._on_job_state("running")
        assert not win._msg_dock.isHidden()          # rodar revela as mensagens
    finally:
        win.close()
