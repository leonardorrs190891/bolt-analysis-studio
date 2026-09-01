# Chrome V2 — Fundação (Plano 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir a **casca (chrome) CAE "estilo Abaqus"** do BAS V2 — um `QMainWindow` de janela única com module bar, Model Tree, multi-viewport e Property Inspector com toggle Basic/Advanced — em paralelo à GUI V1 de 7 abas, acessível via `python run_app.py --v2`, sem tocar a V1 (que permanece como fallback).

**Architecture:** Um novo pacote `gui/chrome/` hospeda o shell e os widgets compartilhados. O shell **reutiliza intactos** o `Theme` (`gui/theme.py`) como design-system e o singleton `AppState` (`core/app_state.py`) como barramento de estado (sinais `model_changed`/`results_changed`/`project_changed`). Os widgets novos (module bar, context bar, prompt area, Model Tree, AutoComboBox, CollapsibleGroup, Inspector, MultiViewport) são folhas independentes e testáveis isoladamente; o `ChromeWindow` os monta e faz a máquina de estados de módulos. Os **conteúdos reais** de cada módulo (SchematicView no Model, plots no Results, etc.) NÃO entram aqui — os viewports mostram placeholders nomeados; os módulos vêm em planos subsequentes (ver "Planos seguintes" no fim).

**Tech Stack:** Python 3, PyQt6, pytest (sem `pytest-qt` — usamos uma fixture `qapp` offscreen própria), matplotlib (só via primitives já existentes, não neste plano).

## Global Constraints

- **Encoding `utf-8` em TODO file I/O** (Windows charmap quebra sem isso).
- **Sempre `ast.parse`** após cada edição de `.py`: `python -c "import ast; ast.parse(open('CAMINHO', encoding='utf-8').read()); print('OK')"`.
- **Testes headless**: todo teste de widget roda com `QT_QPA_PLATFORM=offscreen` (a fixture `qapp` garante isso). **NÃO** use `pytest-qt`/`qtbot` — não está instalado (o `test_gui.py` legado fica skipado por isso).
- **NÃO tocar a V1**: `gui/main_window.py`, `gui/msd_builder.py` e as abas ficam **intactos**. A única modificação fora de `gui/chrome/` é o wiring `--v2` em `run_app.py` (aditivo) e a fixture `qapp` em `tests/conftest.py` (aditivo).
- **Escopo `gui/` apenas**: proibido alterar `core/`, `numerical/`, `visualization/`, formato `.msd`. Reutilizar `Theme` e `AppState` **as-is** (não recriar `theme.py`).
- **Não tocar arquivos foreign** (WIP de sessão paralela): `New_Theory/frontier_polish.py`, `New_Theory/liu2025_nemb_probe.py`, `New_Theory/Materiais_Metalicos_EPL_Gb.docx`.
- **Um commit por tarefa**, mensagem terminando com `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- **Interfaces canônicas** (fixadas aqui; toda tarefa as respeita à letra):
  - Módulos: `MODULES = ["Model", "Contacts", "Loads", "Analysis", "Results", "Report"]` (Similitude removida por spec §0.1).
  - `AutoComboBox(options, inference_fn=None, parent=None)` — sinal `value_changed(str)`; props `is_auto: bool`, `current_resolved_value() -> str`, `reset_to_auto()`.
  - `CollapsibleGroup(title, parent=None)` — sinal `toggled(bool)`; métodos `add_row(label: str, widget: QWidget, help_key: str = "")`, `set_collapsed(bool)`, `is_collapsed() -> bool`.
  - `ModelTree(parent=None)` — sinal `node_selected(str, object)` (node_kind, payload); métodos `populate(model)`, `highlight_module(name: str)`.
  - `ChromeInspector(parent=None)` — sinal `level_changed(str)` ("Basic"/"Advanced"); métodos `set_level(str)`, `level() -> str`, `show_groups(specs: list)`; persiste nível em `QSettings("BAS", "chrome")`.
  - `MultiViewport(parent=None)` — sinal `active_changed(int)`; métodos `set_layout(name: str)` com `name ∈ {"1","1x2","2x1","2x2"}`, `set_widget(index: int, w: QWidget)`, prop `active_index: int`.
  - `ModuleBar(parent=None)` — sinais `module_changed(str)`, `step_changed(str)`, `run_requested()`, `stop_requested()`; métodos `set_module(str)`, `set_badge(text: str, kind: str)`.
  - `ContextBar(parent=None)` — sinal `action_triggered(str)`; método `set_module(str)` (troca o conjunto de botões).
  - `PromptArea(parent=None)` — métodos `set_prompt(str)`, `set_coords(str)`.
  - `ChromeWindow(app_state=None, parent=None)` — método `switch_module(name: str)`; propriedade `current_module: str`.

---

## File Structure

**Create:**
```
src/bolt_analysis_studio/gui/chrome/
├── __init__.py
├── app_window.py            # ChromeWindow(QMainWindow) — monta o shell + máquina de módulos
├── parameter_help.py        # load_parameter_help(), help_for(widget_name)
├── parameter_help.json      # catálogo de tooltips (chave=widget, valor=string)
└── widgets/
    ├── __init__.py
    ├── auto_combo.py         # AutoComboBox(QComboBox)
    ├── collapsible.py        # CollapsibleGroup(QWidget)
    ├── model_tree.py         # ModelTree(QTreeWidget)
    ├── property_inspector.py # ChromeInspector(QWidget)
    ├── multi_viewport.py     # MultiViewport(QWidget)
    ├── module_bar.py         # ModuleBar(QToolBar)
    ├── context_bar.py        # ContextBar(QToolBar)
    └── prompt_area.py        # PromptArea(QWidget)
tests/
├── test_auto_combo.py
├── test_collapsible_group.py
├── test_parameter_help.py
├── test_model_tree.py
├── test_inspector_toggle.py
├── test_multi_viewport.py
├── test_chrome_bars.py
└── test_main_window_chrome.py
```

**Modify:**
- `tests/conftest.py` — adicionar fixture `qapp` (session-scoped, offscreen). Aditivo.
- `run_app.py` — flag `--v2` que instancia `ChromeWindow` em vez de `BoltAnalysisStudio`. Aditivo.

**Reuse as-is (NÃO modificar):** `gui/theme.py` (`Theme`), `core/app_state.py` (`get_app_state`, `AppState`), `gui/new_analysis_wizard.py`, `gui/msd_builder.py`, `visualization/plot_manager.py`.

---

## Task 1: Test scaffolding — fixture `qapp` offscreen

Habilita todos os testes de widget sem `pytest-qt`. O `tests/conftest.py` já existe (põe `src/` no path); **estenda-o**, não sobrescreva.

**Files:**
- Modify: `tests/conftest.py`
- Test: `tests/test_chrome_smoke.py` (Create)

**Interfaces:**
- Produces: fixture `qapp` (session-scoped) → `QApplication` única, offscreen.

- [ ] **Step 1: Ler o conftest atual** para não apagar o setup de `sys.path`.

Run: `python -c "print(open('tests/conftest.py', encoding='utf-8').read())"`

- [ ] **Step 2: Anexar a fixture** ao fim de `tests/conftest.py` (preserve o conteúdo existente):

```python
import os
import pytest

# Qt headless: precisa vir antes de qualquer import de QtWidgets.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session")
def qapp():
    """QApplication única para os testes de widget do chrome V2 (sem pytest-qt)."""
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app
```

- [ ] **Step 3: Escrever o smoke test** `tests/test_chrome_smoke.py`:

```python
def test_qapp_boots(qapp):
    from PyQt6.QtWidgets import QWidget
    w = QWidget()
    w.setObjectName("smoke")
    assert w.objectName() == "smoke"
```

- [ ] **Step 4: Rodar** — `python -m pytest tests/test_chrome_smoke.py -q` → **1 passed**.
- [ ] **Step 5: Commit** — `git add tests/conftest.py tests/test_chrome_smoke.py && git commit -m "test(chrome): fixture qapp offscreen para widgets V2"`

---

## Task 2: `AutoComboBox` — combo com Auto-default + override

Combo onde a 1ª opção é `Auto (<inferido>)`; selecionar override fixa a escolha; `reset_to_auto()` volta ao inferido (spec §3.B).

**Files:**
- Create: `src/bolt_analysis_studio/gui/chrome/__init__.py` (vazio), `src/bolt_analysis_studio/gui/chrome/widgets/__init__.py` (vazio), `src/bolt_analysis_studio/gui/chrome/widgets/auto_combo.py`
- Test: `tests/test_auto_combo.py`

**Interfaces:**
- Produces: `AutoComboBox(options: list[str], inference_fn=None, parent=None)`, sinal `value_changed(str)`, `is_auto: bool`, `current_resolved_value() -> str`, `reset_to_auto()`, `set_context(ctx)`.

- [ ] **Step 1: Escrever o teste** `tests/test_auto_combo.py`:

```python
from bolt_analysis_studio.gui.chrome.widgets.auto_combo import AutoComboBox


def test_auto_default_resolves_via_inference(qapp):
    c = AutoComboBox(["Coulomb", "Stribeck", "LuGre"],
                     inference_fn=lambda ctx: "Stribeck" if ctx.get("lubricated") else "Coulomb")
    c.set_context({"lubricated": True})
    assert c.is_auto is True
    assert c.current_resolved_value() == "Stribeck"        # inferido
    assert c.currentText().startswith("Auto")


def test_override_fixes_choice_and_emits(qapp):
    seen = []
    c = AutoComboBox(["Coulomb", "Stribeck"], inference_fn=lambda ctx: "Coulomb")
    c.value_changed.connect(seen.append)
    c.set_value("Stribeck")
    assert c.is_auto is False
    assert c.current_resolved_value() == "Stribeck"
    assert seen == ["Stribeck"]


def test_reset_to_auto(qapp):
    c = AutoComboBox(["Coulomb", "Stribeck"], inference_fn=lambda ctx: "Coulomb")
    c.set_value("Stribeck")
    c.reset_to_auto()
    assert c.is_auto is True
    assert c.current_resolved_value() == "Coulomb"


def test_no_inference_fn_defaults_first_option(qapp):
    c = AutoComboBox(["A", "B"])
    assert c.current_resolved_value() == "A"
```

- [ ] **Step 2: Rodar e ver falhar** — `python -m pytest tests/test_auto_combo.py -q` → FAIL (ImportError).
- [ ] **Step 3: Implementar** `auto_combo.py`:

```python
"""AutoComboBox — combo com opção 'Auto (<inferido>)' + override (spec §3.B)."""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox


class AutoComboBox(QComboBox):
    value_changed = pyqtSignal(str)

    def __init__(self, options, inference_fn=None, parent=None):
        super().__init__(parent)
        self._options = list(options)
        self._inference_fn = inference_fn
        self._context = {}
        self._is_auto = True
        self._rebuild()
        self.currentIndexChanged.connect(self._on_index_changed)

    # --- estado ---
    @property
    def is_auto(self) -> bool:
        return self._is_auto

    def set_context(self, ctx: dict) -> None:
        self._context = dict(ctx or {})
        if self._is_auto:
            self._rebuild()

    def _inferred(self) -> str:
        if self._inference_fn is not None:
            try:
                val = self._inference_fn(self._context)
                if val in self._options:
                    return val
            except Exception:
                pass
        return self._options[0] if self._options else ""

    def current_resolved_value(self) -> str:
        if self._is_auto:
            return self._inferred()
        return self.currentText()

    # --- ações ---
    def set_value(self, value: str) -> None:
        if value not in self._options:
            return
        self._is_auto = False
        self._rebuild()
        self.setCurrentText(value)  # dispara _on_index_changed → value_changed

    def reset_to_auto(self) -> None:
        self._is_auto = True
        self._rebuild()
        self.value_changed.emit(self.current_resolved_value())

    # --- interno ---
    def _rebuild(self) -> None:
        self.blockSignals(True)
        self.clear()
        if self._is_auto:
            self.addItem(f"Auto ({self._inferred()})")
        else:
            for opt in self._options:
                self.addItem(opt)
        self.blockSignals(False)

    def _on_index_changed(self, _idx: int) -> None:
        if not self._is_auto:
            self.value_changed.emit(self.currentText())
```

- [ ] **Step 4: `ast.parse`** nos 3 arquivos criados; rodar `python -m pytest tests/test_auto_combo.py -q` → **4 passed**.
- [ ] **Step 5: Commit** — `git add src/bolt_analysis_studio/gui/chrome/ tests/test_auto_combo.py && git commit -m "feat(chrome): AutoComboBox (Auto-default + override, spec 3.B)"`

---

## Task 3: `CollapsibleGroup` — grupo colapsável do Inspector

Cabeçalho clicável `▼ Título` (estilo Unity/Blender) que mostra/esconde um corpo em grid (spec abaqus §6).

**Files:**
- Create: `src/bolt_analysis_studio/gui/chrome/widgets/collapsible.py`
- Test: `tests/test_collapsible_group.py`

**Interfaces:**
- Consumes: nada.
- Produces: `CollapsibleGroup(title, parent=None)`, sinal `toggled(bool)`, `add_row(label, widget, help_key="")`, `set_collapsed(bool)`, `is_collapsed() -> bool`, `row_count() -> int`.

- [ ] **Step 1: Teste** `tests/test_collapsible_group.py`:

```python
from PyQt6.QtWidgets import QLineEdit
from bolt_analysis_studio.gui.chrome.widgets.collapsible import CollapsibleGroup


def test_add_row_and_count(qapp):
    g = CollapsibleGroup("Global Loading")
    g.add_row("Preload F0", QLineEdit())
    g.add_row("Frequency", QLineEdit())
    assert g.row_count() == 2


def test_collapse_hides_body_and_emits(qapp):
    seen = []
    g = CollapsibleGroup("X")
    g.toggled.connect(seen.append)
    g.add_row("a", QLineEdit())
    assert g.is_collapsed() is False
    g.set_collapsed(True)
    assert g.is_collapsed() is True
    assert g._body.isVisibleTo(g) is False
    assert seen == [True]
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** `collapsible.py`:

```python
"""CollapsibleGroup — grupo colapsável do Property Inspector (spec abaqus §6)."""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (QFormLayout, QToolButton, QVBoxLayout, QWidget)


class CollapsibleGroup(QWidget):
    toggled = pyqtSignal(bool)  # True = colapsado

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self._collapsed = False
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._header = QToolButton()
        self._header.setText(f"▼  {title}")   # ▼
        self._header.setCheckable(True)
        self._header.setChecked(True)
        self._header.setStyleSheet("QToolButton { border: none; text-align: left; font-weight: 600; }")
        self._header.clicked.connect(lambda _: self.set_collapsed(not self._collapsed))
        outer.addWidget(self._header)

        self._body = QWidget()
        self._form = QFormLayout(self._body)
        self._form.setContentsMargins(12, 2, 4, 6)
        self._form.setVerticalSpacing(3)
        outer.addWidget(self._body)
        self._title = title

    def add_row(self, label: str, widget: QWidget, help_key: str = "") -> None:
        if help_key:
            widget.setProperty("help_key", help_key)
        self._form.addRow(label, widget)

    def row_count(self) -> int:
        return self._form.rowCount()

    def is_collapsed(self) -> bool:
        return self._collapsed

    def set_collapsed(self, collapsed: bool) -> None:
        collapsed = bool(collapsed)
        if collapsed == self._collapsed:
            return
        self._collapsed = collapsed
        self._body.setVisible(not collapsed)
        arrow = "▶" if collapsed else "▼"   # ▶ / ▼
        self._header.setText(f"{arrow}  {self._title}")
        self.toggled.emit(collapsed)
```

- [ ] **Step 4: `ast.parse` + `python -m pytest tests/test_collapsible_group.py -q`** → **2 passed**.
- [ ] **Step 5: Commit** — `git commit -m "feat(chrome): CollapsibleGroup (inspector groups)"`

---

## Task 4: `parameter_help` — catálogo de tooltips

Catálogo único `parameter_help.json` (chave = nome do widget, valor = string 1-3 linhas) + loader (spec §3.E).

**Files:**
- Create: `src/bolt_analysis_studio/gui/chrome/parameter_help.json`, `src/bolt_analysis_studio/gui/chrome/parameter_help.py`
- Test: `tests/test_parameter_help.py`

**Interfaces:**
- Produces: `load_parameter_help() -> dict`, `help_for(widget_name: str) -> str` (string vazia se ausente).

- [ ] **Step 1: Teste** `tests/test_parameter_help.py`:

```python
from bolt_analysis_studio.gui.chrome.parameter_help import load_parameter_help, help_for


def test_catalog_loads_as_dict():
    cat = load_parameter_help()
    assert isinstance(cat, dict) and len(cat) >= 5


def test_help_for_known_and_unknown():
    assert "friction" in help_for("mu_static").lower()
    assert help_for("__nao_existe__") == ""


def test_all_values_are_short_strings():
    for k, v in load_parameter_help().items():
        assert isinstance(v, str) and v.strip()
        assert v.count("\n") <= 3
```

- [ ] **Step 2: Criar `parameter_help.json`** (seed com os campos Basic da spec §6; UTF-8):

```json
{
  "mu_static": "Coefficient of static friction (dry: 0.10–0.20 · lubricated: 0.05–0.12). Higher = more resistance to initial slip. Pai-Hess slip-onset uses 0.46×μ.",
  "F_preload": "Initial clamp force F0 [kN]. Sets the joint's starting tension; loosening is measured as its decay.",
  "percent_yield": "Preload as a fraction of bolt proof/yield. Typical target 70%.",
  "delta_amplitude": "Transverse displacement amplitude [mm] of the imposed cyclic motion (Junker/disp-mode).",
  "frequency": "Excitation frequency [Hz] of the cyclic load.",
  "n_cycles": "Number of load cycles to simulate.",
  "load_type": "TRANSVERSE (shear/Junker), AXIAL, or COMBINED loading regime.",
  "locking_type": "Locking device: free-running, prevailing-torque, Nord-Lock, Belleville, double-nut, chemical, etc.",
  "integrator": "Newmark-β (default, unconditionally stable) or HHT-α (adds numerical damping for spurious high-freq modes).",
  "k_thread": "Thread-contact stiffness [N/m]."
}
```

- [ ] **Step 3: Implementar `parameter_help.py`:**

```python
"""Catálogo de tooltips do Inspector (spec §3.E). Fonte única: parameter_help.json."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_JSON = Path(__file__).with_name("parameter_help.json")


@lru_cache(maxsize=1)
def load_parameter_help() -> dict:
    try:
        return json.loads(_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def help_for(widget_name: str) -> str:
    return load_parameter_help().get(widget_name, "")
```

- [ ] **Step 4: `ast.parse` + `python -m pytest tests/test_parameter_help.py -q`** → **3 passed**.
- [ ] **Step 5: Commit** — `git commit -m "feat(chrome): parameter_help catalog + loader (spec 3.E)"`

---

## Task 5: `ModelTree` — árvore de navegação (fonte de verdade)

Hierarquia fixa dos 6 módulos + nós Jobs/Validation (spec abaqus §4); popula os elementos do modelo sob "Model"; clicar num nó emite `node_selected`.

**Files:**
- Create: `src/bolt_analysis_studio/gui/chrome/widgets/model_tree.py`
- Test: `tests/test_model_tree.py`

**Interfaces:**
- Produces: `ModelTree(parent=None)`, sinal `node_selected(str, object)`, `populate(model)`, `highlight_module(name)`.
- Consumes: um objeto modelo com atributo iterável `elements` (defensivo — usa `getattr(model, "elements", [])`). O worker deve CONFERIR os nomes reais em `src/bolt_analysis_studio/core/models/model.py` antes de finalizar (campo pode ser `elements` list ou dict).

- [ ] **Step 1: Teste** `tests/test_model_tree.py` (usa um fake leve — isolamento; a integração real é o smoke da Task 9):

```python
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


def test_click_emits_node_selected(qapp):
    seen = []
    t = ModelTree()
    t.node_selected.connect(lambda kind, payload: seen.append(kind))
    item = t.topLevelItem(0)
    t.setCurrentItem(item)
    t._emit_for(item)          # simula clique
    assert seen and isinstance(seen[0], str)
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar `model_tree.py`** (hierarquia da spec abaqus §4, sem Similitude):

```python
"""ModelTree — árvore de navegação, fonte de verdade (spec abaqus §4)."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem

# Nós de topo (módulos + Jobs/Validation/Reports). Similitude removida (spec §0.1).
TOP_NODES = ["Model", "Contacts", "Loads", "Analysis", "Jobs",
             "Results", "Validation", "Reports"]
# Nó → módulo que ele ativa
NODE_TO_MODULE = {"Model": "Model", "Contacts": "Contacts", "Loads": "Loads",
                  "Analysis": "Analysis", "Jobs": "Analysis", "Results": "Results",
                  "Validation": "Results", "Reports": "Report"}


class ModelTree(QTreeWidget):
    node_selected = pyqtSignal(str, object)   # (node_kind, payload)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setMinimumWidth(200)
        self._tops = {}
        self._model_node = None
        for name in TOP_NODES:
            it = QTreeWidgetItem([name])
            it.setData(0, Qt.ItemDataRole.UserRole, ("module", NODE_TO_MODULE[name]))
            self.addTopLevelItem(it)
            self._tops[name] = it
        self._model_node = self._tops["Model"]
        self.itemClicked.connect(lambda item, _col: self._emit_for(item))

    def populate(self, model) -> None:
        self._model_node.takeChildren()
        for el in getattr(model, "elements", []) or []:
            etype = getattr(el, "element_type", getattr(el, "type", "ELEMENT"))
            child = QTreeWidgetItem([str(etype)])
            child.setData(0, Qt.ItemDataRole.UserRole, ("element", el))
            self._model_node.addChild(child)
        self._model_node.setExpanded(True)

    def highlight_module(self, name: str) -> None:
        for label, it in self._tops.items():
            font = it.font(0)
            font.setBold(NODE_TO_MODULE[label] == name)
            it.setFont(0, font)

    # helpers de teste/uso
    def _element_count(self) -> int:
        return self._model_node.childCount()

    def _emit_for(self, item: QTreeWidgetItem) -> None:
        data = item.data(0, Qt.ItemDataRole.UserRole) or ("unknown", None)
        self.node_selected.emit(data[0], data[1])
```

- [ ] **Step 4: `ast.parse` + `python -m pytest tests/test_model_tree.py -q`** → **3 passed**.
- [ ] **Step 5: Confirmar campos reais** — ler `core/models/model.py`; se o campo não for `elements` (lista de objetos com `element_type`), ajustar `populate` e o teste de forma consistente. Re-rodar.
- [ ] **Step 6: Commit** — `git commit -m "feat(chrome): ModelTree (navegação fonte-de-verdade, spec 4)"`

---

## Task 6: `ChromeInspector` — Property Inspector com toggle Basic/Advanced

Painel direito: header com segmented `[Basic | Advanced]` (persistido em `QSettings`), corpo de `CollapsibleGroup`s. `show_groups(specs)` renderiza campos, escondendo os `advanced` quando em Basic (spec §3.C).

**Files:**
- Create: `src/bolt_analysis_studio/gui/chrome/widgets/property_inspector.py`
- Test: `tests/test_inspector_toggle.py`

**Interfaces:**
- Consumes: `CollapsibleGroup` (Task 3), `AutoComboBox` (Task 2), `help_for` (Task 4).
- Produces: `ChromeInspector(parent=None)`, sinal `level_changed(str)`, `set_level(str)`, `level() -> str`, `show_groups(specs)`. Spec de grupo: `{"title": str, "rows": [{"label": str, "widget": QWidget, "advanced": bool, "help": str}]}`.

- [ ] **Step 1: Teste** `tests/test_inspector_toggle.py`:

```python
from PyQt6.QtWidgets import QLineEdit
from bolt_analysis_studio.gui.chrome.widgets.property_inspector import ChromeInspector


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
    assert insp._visible_row_count() == 1        # só a Basic


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
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar `property_inspector.py`:**

```python
"""ChromeInspector — Property Inspector CAE com toggle Basic/Advanced (spec §3.C)."""
from __future__ import annotations

from PyQt6.QtCore import QSettings, pyqtSignal
from PyQt6.QtWidgets import (QButtonGroup, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QVBoxLayout, QWidget)

from .collapsible import CollapsibleGroup
from ..parameter_help import help_for

_LEVELS = ("Basic", "Advanced")


class ChromeInspector(QWidget):
    level_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = QSettings("BAS", "chrome")
        self._level = self._settings.value("inspector_level", "Basic")
        if self._level not in _LEVELS:
            self._level = "Basic"
        self._rows = []          # (widget_container, advanced: bool)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        header = QHBoxLayout()
        header.addWidget(QLabel("Properties"))
        header.addStretch(1)
        self._btns = QButtonGroup(self)
        for lvl in _LEVELS:
            b = QPushButton(lvl)
            b.setCheckable(True)
            b.setChecked(lvl == self._level)
            b.clicked.connect(lambda _c, L=lvl: self.set_level(L))
            self._btns.addButton(b)
            header.addWidget(b)
        root.addLayout(header)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._host = QWidget()
        self._host_layout = QVBoxLayout(self._host)
        self._host_layout.addStretch(1)
        self._scroll.setWidget(self._host)
        root.addWidget(self._scroll, 1)

    def level(self) -> str:
        return self._level

    def set_level(self, level: str) -> None:
        if level not in _LEVELS or level == self._level:
            # ainda sincroniza botões se chamado com o mesmo nível
            self._sync_buttons()
            return
        self._level = level
        self._settings.setValue("inspector_level", level)
        self._settings.sync()
        self._apply_visibility()
        self._sync_buttons()
        self.level_changed.emit(level)

    def show_groups(self, specs) -> None:
        # limpa
        while self._host_layout.count() > 1:   # mantém o stretch final
            item = self._host_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._rows = []
        for spec in specs:
            group = CollapsibleGroup(spec.get("title", ""))
            for row in spec.get("rows", []):
                widget = row["widget"]
                hk = row.get("help") or ""
                if hk and help_for(hk):
                    widget.setToolTip(help_for(hk))
                group.add_row(row.get("label", ""), widget, hk)
                self._rows.append((widget, bool(row.get("advanced", False))))
            self._host_layout.insertWidget(self._host_layout.count() - 1, group)
        self._apply_visibility()

    def _apply_visibility(self) -> None:
        show_adv = self._level == "Advanced"
        for widget, advanced in self._rows:
            # esconde/mostra a linha inteira via o label do QFormLayout também
            widget.setVisible(show_adv or not advanced)
            lbl = self._row_label(widget)
            if lbl is not None:
                lbl.setVisible(show_adv or not advanced)

    def _row_label(self, widget):
        form = widget.parentWidget().layout() if widget.parentWidget() else None
        try:
            from PyQt6.QtWidgets import QFormLayout
            if isinstance(form, QFormLayout):
                return form.labelForField(widget)
        except Exception:
            pass
        return None

    def _sync_buttons(self):
        for b in self._btns.buttons():
            b.setChecked(b.text() == self._level)

    def _visible_row_count(self) -> int:
        return sum(1 for w, _adv in self._rows if w.isVisible())
```

- [ ] **Step 4: `ast.parse` + `python -m pytest tests/test_inspector_toggle.py -q`** → **4 passed**. (Se `_visible_row_count` divergir por `isVisible()` retornar False fora de janela mostrada, use `isVisibleTo(parent)` ou uma flag interna de visibilidade — ajuste o helper e mantenha o teste significativo.)
- [ ] **Step 5: Commit** — `git commit -m "feat(chrome): ChromeInspector Basic/Advanced toggle + QSettings (spec 3.C)"`

---

## Task 7: `MultiViewport` — container de layouts 1 / 1×2 / 2×1 / 2×2

Área central que hospeda 1-4 sub-viewports; troca de layout; viewport ativo com outline azul (spec abaqus §5).

**Files:**
- Create: `src/bolt_analysis_studio/gui/chrome/widgets/multi_viewport.py`
- Test: `tests/test_multi_viewport.py`

**Interfaces:**
- Produces: `MultiViewport(parent=None)`, sinal `active_changed(int)`, `set_layout(name)`, `set_widget(index, w)`, `active_index: int`, `layout_name() -> str`, `slot_count() -> int`.

- [ ] **Step 1: Teste** `tests/test_multi_viewport.py`:

```python
from PyQt6.QtWidgets import QLabel
from bolt_analysis_studio.gui.chrome.widgets.multi_viewport import MultiViewport


def test_default_layout_single(qapp):
    v = MultiViewport()
    assert v.layout_name() == "1"
    assert v.slot_count() == 1


def test_switch_to_2x2_has_four_slots(qapp):
    v = MultiViewport()
    v.set_layout("2x2")
    assert v.slot_count() == 4


def test_set_widget_and_active(qapp):
    seen = []
    v = MultiViewport()
    v.set_layout("1x2")
    v.active_changed.connect(seen.append)
    v.set_widget(1, QLabel("plot B"))
    v.set_active(1)
    assert v.active_index == 1
    assert seen[-1] == 1


def test_bad_layout_raises(qapp):
    v = MultiViewport()
    try:
        v.set_layout("3x3")
        assert False, "esperava ValueError"
    except ValueError:
        pass
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar `multi_viewport.py`** (QGridLayout + slots placeholder):

```python
"""MultiViewport — layouts fixos 1 / 1x2 / 2x1 / 2x2 (spec abaqus §5)."""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

_LAYOUTS = {
    "1":   [(0, 0, 1, 1)],
    "1x2": [(0, 0, 1, 1), (0, 1, 1, 1)],
    "2x1": [(0, 0, 1, 1), (1, 0, 1, 1)],
    "2x2": [(0, 0, 1, 1), (0, 1, 1, 1), (1, 0, 1, 1), (1, 1, 1, 1)],
}


class _Slot(QFrame):
    def __init__(self, index, on_focus):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._index = index
        self._on_focus = on_focus
        lay = QVBoxLayout(self)
        lay.setContentsMargins(1, 1, 1, 1)
        self._content = QLabel(f"[ viewport {index + 1} ]")
        self._content.setMinimumSize(80, 60)
        lay.addWidget(self._content)

    def mousePressEvent(self, ev):
        self._on_focus(self._index)
        super().mousePressEvent(ev)

    def set_content(self, w):
        lay = self.layout()
        old = lay.takeAt(0)
        if old and old.widget():
            old.widget().deleteLater()
        self._content = w
        lay.addWidget(w)

    def set_active(self, active):
        self.setStyleSheet("QFrame { border: 2px solid #007acc; }" if active
                           else "QFrame { border: 1px solid #3e3e42; }")


class MultiViewport(QWidget):
    active_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(2)
        self._slots = []
        self._active = 0
        self._layout_name = "1"
        self.set_layout("1")

    def layout_name(self) -> str:
        return self._layout_name

    def slot_count(self) -> int:
        return len(self._slots)

    @property
    def active_index(self) -> int:
        return self._active

    def set_layout(self, name: str) -> None:
        if name not in _LAYOUTS:
            raise ValueError(f"layout desconhecido: {name!r}")
        for s in self._slots:
            self._grid.removeWidget(s)
            s.deleteLater()
        self._slots = []
        for i, (r, c, rs, cs) in enumerate(_LAYOUTS[name]):
            slot = _Slot(i, self.set_active)
            self._grid.addWidget(slot, r, c, rs, cs)
            self._slots.append(slot)
        self._layout_name = name
        self._active = 0
        self._refresh_active()

    def set_widget(self, index: int, w: QWidget) -> None:
        if 0 <= index < len(self._slots):
            self._slots[index].set_content(w)

    def set_active(self, index: int) -> None:
        if 0 <= index < len(self._slots) and index != self._active:
            self._active = index
            self._refresh_active()
            self.active_changed.emit(index)

    def _refresh_active(self) -> None:
        for i, s in enumerate(self._slots):
            s.set_active(i == self._active)
```

- [ ] **Step 4: `ast.parse` + `python -m pytest tests/test_multi_viewport.py -q`** → **4 passed**.
- [ ] **Step 5: Commit** — `git commit -m "feat(chrome): MultiViewport (layouts 1/1x2/2x1/2x2, spec 5)"`

---

## Task 8: Barras do chrome — `ModuleBar`, `ContextBar`, `PromptArea`

As barras superior/contextual/inferior (spec abaqus §3).

**Files:**
- Create: `src/bolt_analysis_studio/gui/chrome/widgets/module_bar.py`, `.../context_bar.py`, `.../prompt_area.py`
- Test: `tests/test_chrome_bars.py`

**Interfaces:**
- Produces:
  - `ModuleBar(QToolBar)`: sinais `module_changed(str)`, `step_changed(str)`, `run_requested()`, `stop_requested()`; `set_module(str)`, `set_badge(text, kind)`.
  - `ContextBar(QToolBar)`: sinal `action_triggered(str)`; `set_module(str)`.
  - `PromptArea(QWidget)`: `set_prompt(str)`, `set_coords(str)`.

- [ ] **Step 1: Teste** `tests/test_chrome_bars.py`:

```python
from bolt_analysis_studio.gui.chrome.widgets.module_bar import ModuleBar, MODULES
from bolt_analysis_studio.gui.chrome.widgets.context_bar import ContextBar
from bolt_analysis_studio.gui.chrome.widgets.prompt_area import PromptArea


def test_modulebar_lists_six_modules(qapp):
    mb = ModuleBar()
    assert MODULES == ["Model", "Contacts", "Loads", "Analysis", "Results", "Report"]
    assert mb._module_combo.count() == 6


def test_modulebar_module_change_emits(qapp):
    seen = []
    mb = ModuleBar()
    mb.module_changed.connect(seen.append)
    mb.set_module("Loads")
    assert seen == ["Loads"]


def test_modulebar_run_stop_signals(qapp):
    ran = []
    mb = ModuleBar()
    mb.run_requested.connect(lambda: ran.append("run"))
    mb._run_btn.click()
    assert ran == ["run"]


def test_contextbar_switches_button_set_per_module(qapp):
    cb = ContextBar()
    cb.set_module("Loads")
    loads_actions = cb._action_names()
    cb.set_module("Results")
    results_actions = cb._action_names()
    assert loads_actions != results_actions
    assert any("Load" in a for a in loads_actions)


def test_contextbar_action_emits(qapp):
    seen = []
    cb = ContextBar()
    cb.action_triggered.connect(seen.append)
    cb.set_module("Loads")
    cb._trigger_first()
    assert len(seen) == 1


def test_prompt_area_sets_text(qapp):
    p = PromptArea()
    p.set_prompt("Selecione um elemento")
    p.set_coords("N=412")
    assert "Selecione" in p._prompt.text()
    assert "412" in p._coords.text()
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar `module_bar.py`:**

```python
"""ModuleBar — module dropdown, step, Run/Stop, badges (spec abaqus §3.2)."""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox, QLabel, QPushButton, QToolBar

MODULES = ["Model", "Contacts", "Loads", "Analysis", "Results", "Report"]


class ModuleBar(QToolBar):
    module_changed = pyqtSignal(str)
    step_changed = pyqtSignal(str)
    run_requested = pyqtSignal()
    stop_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Module", parent)
        self.setMovable(False)
        self.addWidget(QLabel("  Module: "))
        self._module_combo = QComboBox()
        self._module_combo.addItems(MODULES)
        self._module_combo.currentTextChanged.connect(self.module_changed.emit)
        self.addWidget(self._module_combo)

        self.addWidget(QLabel("   Step: "))
        self._step_combo = QComboBox()
        self._step_combo.addItems(["Static-Preload", "Coupled-Loosening"])
        self._step_combo.currentTextChanged.connect(self.step_changed.emit)
        self.addWidget(self._step_combo)

        self.addSeparator()
        self._run_btn = QPushButton("▶ Run")
        self._run_btn.setStyleSheet("QPushButton { color: #6cd486; font-weight: 600; }")
        self._run_btn.clicked.connect(lambda: self.run_requested.emit())
        self.addWidget(self._run_btn)
        self._stop_btn = QPushButton("■ Stop")
        self._stop_btn.clicked.connect(lambda: self.stop_requested.emit())
        self.addWidget(self._stop_btn)

        self.addSeparator()
        self._badge = QLabel("")
        self.addWidget(self._badge)

    def set_module(self, name: str) -> None:
        if name in MODULES and name != self._module_combo.currentText():
            self._module_combo.setCurrentText(name)   # dispara module_changed
        elif name in MODULES:
            self.module_changed.emit(name)

    def set_badge(self, text: str, kind: str = "info") -> None:
        colors = {"pass": "#0e7c3a", "warn": "#d4b13a", "fail": "#c44", "info": "#007acc"}
        self._badge.setText(f"  {text}  " if text else "")
        self._badge.setStyleSheet(
            f"QLabel {{ background: {colors.get(kind, '#007acc')}; color: white; border-radius: 3px; }}"
            if text else "")
```

- [ ] **Step 4: Implementar `context_bar.py`** (conjunto de botões por módulo, spec abaqus §3.3):

```python
"""ContextBar — botões que mudam por módulo ativo (spec abaqus §3.3)."""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QToolBar

# Conjunto de ações por módulo (rótulo do botão).
_ACTIONS = {
    "Model":    ["+ Element", "+ Material", "Assembly", "Locking Device"],
    "Contacts": ["+ Thread", "+ Bearing", "+ Flange", "Friction/Wear"],
    "Loads":    ["+ Global Load", "+ Per-Element", "+ Thermal", "+ Locking"],
    "Analysis": ["+ Static-Preload", "+ Coupled-Loosening", "Solver", "Jobs"],
    "Results":  ["Preload", "Friction", "Phase", "Miner", "Layout", "Overlay", "Export"],
    "Report":   ["Template", "Sections", "Format", "Preview"],
}


class ContextBar(QToolBar):
    action_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__("Context", parent)
        self.setMovable(False)
        self._module = None
        self._actions = []

    def set_module(self, name: str) -> None:
        self.clear()
        self._actions = []
        for label in _ACTIONS.get(name, []):
            act = QAction(label, self)
            act.triggered.connect(lambda _c, L=label: self.action_triggered.emit(L))
            self.addAction(act)
            self._actions.append(act)
        self._module = name

    def _action_names(self):
        return [a.text() for a in self._actions]

    def _trigger_first(self):
        if self._actions:
            self._actions[0].trigger()
```

- [ ] **Step 5: Implementar `prompt_area.py`:**

```python
"""PromptArea — banner azul de instrução contextual + coords (spec abaqus §3.5)."""
from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget


class PromptArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QWidget { background: #007acc; } QLabel { color: white; }")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 3, 8, 3)
        self._prompt = QLabel("Pronto.")
        self._coords = QLabel("")
        lay.addWidget(self._prompt)
        lay.addStretch(1)
        lay.addWidget(self._coords)

    def set_prompt(self, text: str) -> None:
        self._prompt.setText(text)

    def set_coords(self, text: str) -> None:
        self._coords.setText(text)
```

- [ ] **Step 6: `ast.parse` nos 3 + `python -m pytest tests/test_chrome_bars.py -q`** → **6 passed**.
- [ ] **Step 7: Commit** — `git commit -m "feat(chrome): ModuleBar + ContextBar + PromptArea (spec abaqus 3)"`

---

## Task 9: `ChromeWindow` — o shell que monta tudo + máquina de módulos

O `QMainWindow` que junta menubar, ModuleBar, ContextBar, docks (Tree esquerda, Inspector direita), central MultiViewport, PromptArea + status bar; aplica o `Theme`; subscreve o `AppState`; troca de módulo sincronizando ContextBar + prompt + highlight da Tree.

**Files:**
- Create: `src/bolt_analysis_studio/gui/chrome/app_window.py`
- Test: `tests/test_main_window_chrome.py`

**Interfaces:**
- Consumes: `ModuleBar`, `ContextBar`, `PromptArea`, `ModelTree`, `ChromeInspector`, `MultiViewport` (Tasks 2-8); `Theme` (`gui/theme.py`); `get_app_state` (`core/app_state.py`).
- Produces: `ChromeWindow(app_state=None, parent=None)`, `switch_module(name)`, `current_module: str`.

- [ ] **Step 1: Teste** `tests/test_main_window_chrome.py`:

```python
from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
from bolt_analysis_studio.gui.chrome.widgets.module_bar import MODULES


def test_boots_with_three_zones(qapp):
    w = ChromeWindow()
    assert w.tree is not None
    assert w.inspector is not None
    assert w.viewport is not None
    assert w.current_module == "Model"          # default


def test_switch_module_updates_context_and_tree(qapp):
    w = ChromeWindow()
    w.switch_module("Loads")
    assert w.current_module == "Loads"
    assert any("Load" in a for a in w.context_bar._action_names())


def test_module_bar_drives_switch(qapp):
    w = ChromeWindow()
    w.module_bar.set_module("Results")
    assert w.current_module == "Results"


def test_all_modules_switch_without_error(qapp):
    w = ChromeWindow()
    for m in MODULES:
        w.switch_module(m)
        assert w.current_module == m


def test_appstate_model_populates_tree(qapp):
    from types import SimpleNamespace
    from bolt_analysis_studio.core.app_state import get_app_state
    st = get_app_state()
    w = ChromeWindow(app_state=st)
    st.model = SimpleNamespace(elements=[SimpleNamespace(element_type="HEAD", id=1)])
    assert w.tree._element_count() == 1
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar `app_window.py`:**

```python
"""ChromeWindow — shell CAE do BAS V2 (spec abaqus §3). Opt-in via run_app.py --v2.

Reutiliza Theme (design-system) e AppState (barramento) as-is; V1 permanece
como fallback. Os viewports mostram placeholders — os módulos reais vêm em
planos subsequentes.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDockWidget, QLabel, QMainWindow, QStatusBar)

from ..theme import Theme
from ...core.app_state import get_app_state
from .widgets.module_bar import ModuleBar, MODULES
from .widgets.context_bar import ContextBar
from .widgets.prompt_area import PromptArea
from .widgets.model_tree import ModelTree
from .widgets.property_inspector import ChromeInspector
from .widgets.multi_viewport import MultiViewport

# Prompt contextual por módulo (spec §3.5).
_PROMPTS = {
    "Model": "Adicione ou selecione elementos no viewport.",
    "Contacts": "Defina contatos e modelos de atrito/desgaste.",
    "Loads": "Configure o carregamento global e por-elemento.",
    "Analysis": "Defina os steps e rode a análise.",
    "Results": "Inspecione os plots e overlays de validação.",
    "Report": "Monte o relatório e escolha o formato.",
}
# Layout default do viewport por módulo (spec abaqus §5).
_DEFAULT_LAYOUT = {"Model": "1", "Contacts": "1", "Loads": "1",
                   "Analysis": "1", "Results": "2x2", "Report": "1"}


class ChromeWindow(QMainWindow):
    def __init__(self, app_state=None, parent=None):
        super().__init__(parent)
        self.app_state = app_state or get_app_state()
        self._current_module = None
        self.setWindowTitle("Bolt Analysis Studio V2 (chrome)")
        self.resize(1280, 800)
        self._build_chrome()
        self._wire_signals()
        try:
            self.setStyleSheet(Theme.get_stylesheet())
        except Exception:
            pass
        # popula a tree se já houver modelo
        if getattr(self.app_state, "model", None) is not None:
            self.tree.populate(self.app_state.model)
        self.switch_module("Model")

    # --- construção ---
    def _build_chrome(self):
        self.module_bar = ModuleBar()
        self.addToolBar(self.module_bar)
        self.addToolBarBreak()
        self.context_bar = ContextBar()
        self.addToolBar(self.context_bar)

        self.tree = ModelTree()
        tree_dock = QDockWidget("Model Tree", self)
        tree_dock.setWidget(self.tree)
        tree_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, tree_dock)

        self.inspector = ChromeInspector()
        insp_dock = QDockWidget("Properties", self)
        insp_dock.setWidget(self.inspector)
        insp_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, insp_dock)

        self.viewport = MultiViewport()
        self.setCentralWidget(self.viewport)

        self.prompt = PromptArea()
        prompt_dock = QDockWidget("", self)
        prompt_dock.setTitleBarWidget(QLabel())   # sem barra de título
        prompt_dock.setWidget(self.prompt)
        prompt_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, prompt_dock)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Projeto: — · Módulo: — · Job: idle")
        self._build_menus()

    def _build_menus(self):
        mb = self.menuBar()
        file_menu = mb.addMenu("File")
        act = file_menu.addAction("Nova Análise…")
        act.setShortcut("Ctrl+Shift+N")
        act.triggered.connect(self._open_wizard)
        file_menu.addSeparator()
        file_menu.addAction("Sair", self.close)
        mb.addMenu("Edit")
        mod_menu = mb.addMenu("Module")
        for m in MODULES:
            mod_menu.addAction(m, lambda _c=False, name=m: self.switch_module(name))
        mb.addMenu("Help")

    # --- sinais ---
    def _wire_signals(self):
        self.module_bar.module_changed.connect(self.switch_module)
        self.context_bar.action_triggered.connect(self._on_context_action)
        self.tree.node_selected.connect(self._on_tree_node)
        st = self.app_state
        if hasattr(st, "model_changed"):
            st.model_changed.connect(self._on_model_changed)

    # --- máquina de módulos ---
    @property
    def current_module(self) -> str:
        return self._current_module

    def switch_module(self, name: str) -> None:
        if name not in MODULES:
            return
        self._current_module = name
        self.context_bar.set_module(name)
        self.tree.highlight_module(name)
        self.prompt.set_prompt(_PROMPTS.get(name, ""))
        self.viewport.set_layout(_DEFAULT_LAYOUT.get(name, "1"))
        # placeholder nomeado em cada slot (os módulos reais vêm depois)
        for i in range(self.viewport.slot_count()):
            self.viewport.set_widget(i, QLabel(f"[ {name} · viewport {i + 1} ]"))
        self.statusBar().showMessage(f"Projeto: — · Módulo: {name} · Job: idle")
        if self.module_bar._module_combo.currentText() != name:
            self.module_bar._module_combo.setCurrentText(name)

    # --- handlers ---
    def _on_context_action(self, label: str):
        self.prompt.set_prompt(f"Ação: {label}")

    def _on_tree_node(self, kind: str, payload):
        if kind == "module" and payload in MODULES:
            self.switch_module(payload)

    def _on_model_changed(self, model):
        if model is not None:
            self.tree.populate(model)

    def _open_wizard(self):
        try:
            from ..new_analysis_wizard import NewAnalysisWizard, build_model
            from PyQt6.QtWidgets import QDialog
            wiz = NewAnalysisWizard(self)
            if wiz.exec() == QDialog.DialogCode.Accepted:
                self.app_state.model = build_model(wiz.spec())
        except Exception as exc:  # pragma: no cover - defensivo na fundação
            self.prompt.set_prompt(f"Wizard indisponível: {exc}")
```

- [ ] **Step 4: `ast.parse` + `python -m pytest tests/test_main_window_chrome.py -q`** → **5 passed**. (Se o `_on_model_changed` não disparar por o `AppState.model` setter emitir `model_changed(object)` com assinatura diferente, confira `core/app_state.py:504-509` e ajuste o connect; o teste `test_appstate_model_populates_tree` valida esse caminho.)
- [ ] **Step 5: Commit** — `git commit -m "feat(chrome): ChromeWindow shell + máquina de módulos (spec abaqus 3)"`

---

## Task 10: Entry-point opt-in `run_app.py --v2` + smoke

Habilita `python run_app.py --v2` abrindo o `ChromeWindow`, sem tocar o caminho V1 default.

**Files:**
- Modify: `run_app.py`
- Test: `tests/test_chrome_entrypoint.py` (Create)

**Interfaces:**
- Consumes: `ChromeWindow`.

- [ ] **Step 1: Ler `run_app.py`** para achar onde `argparse`/`sys.argv` são tratados e onde `BoltAnalysisStudio` é instanciado (a flag `--builder` já existe — seguir o mesmo padrão).

- [ ] **Step 2: Teste** `tests/test_chrome_entrypoint.py` (valida a fábrica, sem `exec()` do app):

```python
def test_chrome_window_factory_importable(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    w = ChromeWindow()
    assert w.windowTitle().startswith("Bolt Analysis Studio V2")
```

- [ ] **Step 3: Adicionar a flag** em `run_app.py`: onde a CLI é parseada, aceitar `--v2`; quando presente, instanciar `ChromeWindow` (import tardio, dentro do ramo) em vez de `BoltAnalysisStudio`, reaproveitando o mesmo `QApplication`, tema e (se houver) splash. Manter todo o resto do fluxo default intocado. Exemplo do ramo:

```python
if "--v2" in sys.argv:
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    window = ChromeWindow()
else:
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    window = BoltAnalysisStudio()
window.show()
```

(Adapte à estrutura real do `run_app.py` — se ele usa `argparse`, adicione `parser.add_argument("--v2", action="store_true")` e ramifique por `args.v2`.)

- [ ] **Step 4: `ast.parse` em `run_app.py` + `python -m pytest tests/test_chrome_entrypoint.py -q`** → **1 passed**.
- [ ] **Step 5: Smoke manual (opcional, se houver display):** `python run_app.py --v2` abre o chrome; trocar módulos pela dropdown; `File → Nova Análise` popula a Tree. Documentar no PR se rodado.
- [ ] **Step 6: Commit** — `git commit -m "feat(chrome): entry-point opt-in run_app.py --v2 (V1 permanece fallback)"`

---

## Task 11: Verificação final + doc de status

Fecha o plano: suíte inteira verde (chrome + regressão de domínio), e um doc de status apontando o próximo plano.

**Files:**
- Create: `docs/superpowers/plans/2026-07-09-chrome-v2-STATUS.md`

- [ ] **Step 1: Rodar a suíte do chrome** — `python -m pytest tests/test_auto_combo.py tests/test_collapsible_group.py tests/test_parameter_help.py tests/test_model_tree.py tests/test_inspector_toggle.py tests/test_multi_viewport.py tests/test_chrome_bars.py tests/test_main_window_chrome.py tests/test_chrome_entrypoint.py tests/test_chrome_smoke.py -q` → **tudo verde**.
- [ ] **Step 2: Rodar regressão de domínio** (garantir que nada da V1/engine quebrou — nenhum arquivo compartilhado foi tocado, mas confirmar): `python -m pytest tests/test_calibration_server.py tests/test_parameter_registry.py tests/test_library_common.py -q` → verde.
- [ ] **Step 3: Escrever `2026-07-09-chrome-v2-STATUS.md`** — o que foi entregue (widgets + shell + entry-point), os testes, e o handoff para o **Plano 2 (Módulo Model)**: re-hospedar `SchematicView` + `ElementPalette` + `PropertyInspector` (do `msd_builder.py`) dentro do viewport/inspector do chrome, com um `QUndoStack` injetado e `load_from_msd_model`/`export_to_msd_model` levantados para um controller.
- [ ] **Step 4: Commit** — `git commit -m "docs(chrome): status da fundação V2 + handoff p/ Plano 2 (Módulo Model)"`

---

## Self-Review

**1. Spec coverage (steps 1-3 de §5 da spec bas-v2):**
- Step 1 (esqueleto `main_window` QMainWindow + module bar + status bar) → Task 9 (`ChromeWindow`) + Task 8 (barras). ✔
- Step 2 (widgets compartilhados: model_tree, property_inspector, auto_combo, multi_viewport, context_bar, prompt_area) → Tasks 2,3,5,6,7,8. ✔ (`module_bar` é extra necessário ao shell.)
- Step 3 (theme + parameter_help.json) → `Theme` reutilizado as-is (inventário confirma) + Task 4 (`parameter_help`). ✔
- Basic/Advanced toggle (§3.C) → Task 6. AutoComboBox (§3.B) → Task 2. Wizard-first (§3.D) → menu `File → Nova Análise` na Task 9 (integração completa fica no Plano 9 da spec). Inline help (§3.E) → Task 4 + tooltips na Task 6. ✔
- **Fora deste plano (por design, spec §10):** os 6 módulos com conteúdo real (Model/Contacts/Loads/Analysis/Results/Report), integradores 5→2, remoção de abas. São planos subsequentes.

**2. Placeholder scan:** os "placeholders" dos viewports (`QLabel("[ Model · viewport 1 ]")`) são **conteúdo real e intencional** desta fundação (a spec §10 diz o 1º plano não traz os módulos), não TODOs. Nenhum step tem "implemente depois" sem código.

**3. Type consistency:** as assinaturas em "Interfaces canônicas" (topo) são usadas idênticas em todas as tasks: `AutoComboBox.value_changed`, `CollapsibleGroup.add_row/set_collapsed`, `ModelTree.node_selected(str,object)/populate/highlight_module`, `ChromeInspector.set_level/level/show_groups/level_changed`, `MultiViewport.set_layout/set_widget/active_index/active_changed`, `ModuleBar.module_changed/run_requested/set_module`, `ContextBar.set_module/action_triggered`, `PromptArea.set_prompt/set_coords`, `ChromeWindow.switch_module/current_module`. Consistente entre definição (Tasks 2-8) e consumo (Task 9).

**Riscos conhecidos anotados nas tasks:** (a) `ModelTree.populate` depende do campo real de `MSDModel` — Task 5 Step 5 obriga conferir `core/models/model.py`; (b) `ChromeInspector._visible_row_count` pode precisar de `isVisibleTo` em vez de `isVisible` fora de janela mostrada — Task 6 Step 4; (c) o connect de `AppState.model_changed` — Task 9 Step 4 obriga conferir a assinatura em `core/app_state.py`.

---

## Planos seguintes (roadmap, spec §5 steps 4-10)

Cada um é um plano writing-plans próprio, pequeno e com checkpoint:

- **Plano 2 — Módulo Model:** re-hospedar `SchematicView` + `ElementPalette` + `PropertyInspector` no chrome (undo_stack injetado; `load/export_to_msd_model` num controller).
- **Plano 3 — Módulos Contacts + Loads:** extensões do Model (interfaces destacadas; overlays de carga; `PropertyInspector.set_loading_data`).
- **Plano 4 — Módulo Analysis + Jobs:** re-hospedar `SolverTab`/`SolverWorker`/`AnalysisConfig`; extrair `_run_analysis` para um `AnalysisController`; viewport monitor (log+progress+live preload).
- **Plano 5 — Módulo Results + Validation:** extrair os 17 `_plot_*` para um `ResultsController(plot_widget, theme)`; grid 2×2; overlay de reference + MAE/RMSE.
- **Plano 6 — Módulo Report:** re-hospedar `ReportsTab`.
- **Plano 7 — Auto-defaults wiring + Wizard-first completo** (§3.B/§3.D): inference_fns por combo; auto-advance módulo→módulo pós-Create.
- **Plano 8 — Redução de integradores 5→2** (§3.A) + remoção das abas V1 e promoção do chrome a default.
