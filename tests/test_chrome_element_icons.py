"""#7: elementos na Model Tree ganham ícone SVG por tipo."""
from types import SimpleNamespace


def _model():
    return SimpleNamespace(name="M16", elements=[
        SimpleNamespace(element_type="HEAD", id=1),
        SimpleNamespace(element_type="NUT", id=2),
        SimpleNamespace(element_type="BEARING_HEAD", id=3),
        SimpleNamespace(element_type="THREAD", id=4),
    ])


def test_element_children_have_icons(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.model_tree import ModelTree
    tree = ModelTree()
    tree.populate(_model())
    model_node = tree._model_node
    contacts_node = tree._tops["Contacts"]
    assert model_node.childCount() >= 1
    assert contacts_node.childCount() >= 1
    for node in (model_node, contacts_node):
        for i in range(node.childCount()):
            assert not node.child(i).icon(0).isNull(), \
                f"elemento sem ícone: {node.child(i).text(0)}"
