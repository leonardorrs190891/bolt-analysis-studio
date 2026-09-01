"""Fase 5: árvore profunda com contagens por contêiner."""
from types import SimpleNamespace


def _model():
    return SimpleNamespace(name="M16", elements=[
        SimpleNamespace(element_type="HEAD", id=1),
        SimpleNamespace(element_type="NUT", id=2),
        SimpleNamespace(element_type="BEARING_HEAD", id=3),
        SimpleNamespace(element_type="THREAD", id=4),
    ])


def test_tree_counts_containers(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.model_tree import ModelTree
    tree = ModelTree()
    tree.populate(_model())
    labels = {tree.topLevelItem(i).text(0).split(" (")[0]: tree.topLevelItem(i).text(0)
              for i in range(tree.topLevelItemCount())}
    assert "(2)" in labels["Contacts"]     # BEARING_HEAD + THREAD
    assert "(2)" in labels["Model"]        # HEAD + NUT


def test_element_count_is_total(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.model_tree import ModelTree
    tree = ModelTree()
    tree.populate(_model())
    assert tree._element_count() == 4      # total Model + Contacts
