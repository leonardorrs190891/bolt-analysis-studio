"""#3: tree interativa — clique em elemento sincroniza com o viewport; menu de contexto."""
from types import SimpleNamespace

import pytest
from PyQt6.QtWidgets import QMessageBox, QTreeWidget


@pytest.fixture(autouse=True)
def _auto_confirm_close(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question",
                        lambda *a, **k: QMessageBox.StandardButton.Yes)
    yield


def _fake_model():
    return SimpleNamespace(name="M16", elements=[
        SimpleNamespace(element_type="HEAD", id=1),
        SimpleNamespace(element_type="NUT", id=2),
    ])


def test_element_node_click_switches_to_model(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    from PyQt6.QtCore import Qt
    win = ChromeWindow()
    try:
        win.tree.populate(_fake_model())
        node = win.tree._model_node.child(0)
        el = node.data(0, Qt.ItemDataRole.UserRole)[1]
        win.switch_module("Analysis")            # começa fora da família schematic
        win._on_tree_node("element", el)
        assert win.current_module == "Model"     # clicar elemento traz o schematic
    finally:
        win.close()


def test_tree_overrides_context_menu(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.model_tree import ModelTree
    assert "contextMenuEvent" in vars(ModelTree)   # override próprio na classe
