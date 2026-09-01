from types import SimpleNamespace
from bolt_analysis_studio.gui.chrome.widgets.model_tree import ModelTree, TOP_NODES


def test_fixed_hierarchy_present_without_model(qapp):
    t = ModelTree()
    labels = {t.topLevelItem(i).text(0) for i in range(t.topLevelItemCount())}
    for name in TOP_NODES:
        assert any(name in lbl for lbl in labels)


def test_populate_lists_elements_under_model(qapp):
    t = ModelTree()
    model = SimpleNamespace(elements=[
        SimpleNamespace(element_type="HEAD", id=1),
        SimpleNamespace(element_type="NUT", id=2),
    ])
    t.populate(model)
    assert t._element_count() == 2


def test_populate_reads_enum_type_field(qapp):
    # MSDElementData real usa .type (ElementType enum); a tree deve usar o .name
    t = ModelTree()
    enum_like = SimpleNamespace(name="FLANGE")
    model = SimpleNamespace(elements=[SimpleNamespace(type=enum_like, id=7)])
    t.populate(model)
    assert t._model_node.child(0).text(0) == "FLANGE"


def test_click_emits_node_selected(qapp):
    seen = []
    t = ModelTree()
    t.node_selected.connect(lambda kind, payload: seen.append(kind))
    item = t.topLevelItem(0)
    t.setCurrentItem(item)
    t._emit_for(item)          # simula clique
    assert seen and isinstance(seen[0], str)
