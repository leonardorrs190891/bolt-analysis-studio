"""Fase 2: chrome usa QIcon vetorial (não emoji) nos controles-chave."""


def test_run_stop_have_icons(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.module_bar import ModuleBar
    bar = ModuleBar()
    assert not bar._run_btn.icon().isNull()
    assert not bar._stop_btn.icon().isNull()


def test_tree_top_nodes_have_icons(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.model_tree import ModelTree
    tree = ModelTree()
    for i in range(tree.topLevelItemCount()):
        assert not tree.topLevelItem(i).icon(0).isNull()


def test_context_bar_actions_have_icons(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.context_bar import ContextBar
    bar = ContextBar()
    bar.set_module("Model")
    # ao menos uma ação do módulo Model tem ícone
    assert any(not a.icon().isNull() for a in bar.actions())
