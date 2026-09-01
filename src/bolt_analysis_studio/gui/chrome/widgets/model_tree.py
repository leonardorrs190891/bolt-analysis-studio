"""ModelTree — arvore de navegacao, fonte de verdade (spec abaqus §4)."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem

from ...icons import icon

# Nos de topo (modulos + Jobs/Validation/Reports). Similitude removida (spec §0.1).
TOP_NODES = ["Model", "Contacts", "Loads", "Analysis", "Jobs",
             "Results", "Validation", "Reports"]
# No -> modulo que ele ativa
NODE_TO_MODULE = {"Model": "Model", "Contacts": "Contacts", "Loads": "Loads",
                  "Analysis": "Analysis", "Jobs": "Analysis", "Results": "Results",
                  "Validation": "Results", "Reports": "Report"}
# No -> icone (nomes do set em resources/icons/)
_NODE_ICON = {"Model": "element", "Contacts": "contact", "Loads": "load",
              "Analysis": "step", "Jobs": "job", "Results": "validation",
              "Validation": "validation", "Reports": "report"}
# Tipos que vão para o contêiner Contacts (os demais ficam sob Model).
_CONTACT_TYPES = {"BEARING_HEAD", "BEARING_NUT", "FLANGE_FLANGE",
                  "WASHER_CONTACT", "GASKET_CONTACT", "GENERIC_CONTACT", "THREAD"}
# Tipo de elemento -> ícone (nomes do set em resources/icons/).
_ELEMENT_ICON = {"HEAD": "head", "SHANK": "shank", "NUT": "nut", "WASHER": "washer",
                 "FLANGE": "flange", "GASKET": "gasket", "THREAD": "thread",
                 "BEARING_HEAD": "contact", "BEARING_NUT": "contact",
                 "FLANGE_FLANGE": "contact", "WASHER_CONTACT": "contact",
                 "GASKET_CONTACT": "contact", "GENERIC_CONTACT": "contact",
                 "GROUND": "ground"}


def _element_label(el) -> str:
    """Nome do tipo do elemento, robusto a ElementData (.type enum) e fakes (.element_type str)."""
    etype = getattr(el, "element_type", None)
    if etype is None:
        t = getattr(el, "type", None)
        etype = getattr(t, "name", None) or (str(t) if t is not None else "ELEMENT")
    return str(etype)


class ModelTree(QTreeWidget):
    node_selected = pyqtSignal(str, object)   # (node_kind, payload)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setMinimumWidth(200)
        self._tops = {}
        for name in TOP_NODES:
            it = QTreeWidgetItem([name])
            it.setIcon(0, icon(_NODE_ICON.get(name, "element"), size=16))
            it.setData(0, Qt.ItemDataRole.UserRole, ("module", NODE_TO_MODULE[name]))
            self.addTopLevelItem(it)
            self._tops[name] = it
        self._model_node = self._tops["Model"]
        self.itemClicked.connect(lambda item, _col: self._emit_for(item))

    def populate(self, model) -> None:
        self._model_node.takeChildren()
        self._tops["Contacts"].takeChildren()
        for el in getattr(model, "elements", []) or []:
            label = _element_label(el)
            child = QTreeWidgetItem([label])
            child.setIcon(0, icon(_ELEMENT_ICON.get(label, "element"), size=14))
            child.setData(0, Qt.ItemDataRole.UserRole, ("element", el))
            if label in _CONTACT_TYPES:
                self._tops["Contacts"].addChild(child)
            else:
                self._model_node.addChild(child)
        self._set_count("Model", self._model_node.childCount())
        self._set_count("Contacts", self._tops["Contacts"].childCount())
        self._model_node.setExpanded(True)

    def _set_count(self, name: str, n: int) -> None:
        # Rótulo com contagem ("Contacts (3)"); a chave em _tops permanece o nome-base.
        self._tops[name].setText(0, f"{name} ({n})" if n else name)

    def highlight_module(self, name: str) -> None:
        for label, it in self._tops.items():
            font = it.font(0)
            font.setBold(NODE_TO_MODULE[label] == name)
            it.setFont(0, font)

    def rebuild_icons(self) -> None:
        """Reconstrói os ícones dos nós de topo na cor do tema atual."""
        for name, it in self._tops.items():
            it.setIcon(0, icon(_NODE_ICON.get(name, "element"), size=16))

    # helpers de teste/uso
    def _element_count(self) -> int:
        # Total de elementos populados (Model + Contacts).
        return self._model_node.childCount() + self._tops["Contacts"].childCount()

    def _emit_for(self, item: QTreeWidgetItem) -> None:
        data = item.data(0, Qt.ItemDataRole.UserRole) or ("unknown", None)
        self.node_selected.emit(data[0], data[1])

    def contextMenuEvent(self, event) -> None:
        """Menu de contexto em elementos: Editar / Excluir (emite node_selected)."""
        item = self.itemAt(event.pos())
        data = item.data(0, Qt.ItemDataRole.UserRole) if item is not None else None
        if data and data[0] == "element":
            from PyQt6.QtWidgets import QMenu
            menu = QMenu(self)
            menu.addAction("Editar",
                           lambda: self.node_selected.emit("edit", data[1]))
            menu.addAction("Excluir",
                           lambda: self.node_selected.emit("delete", data[1]))
            menu.exec(event.globalPos())
