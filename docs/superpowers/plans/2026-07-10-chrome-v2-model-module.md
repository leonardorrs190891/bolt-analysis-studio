# Chrome V2 — Módulo Model (Plano 2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (inline) ou subagent-driven-development. Steps em checkbox `- [ ]`.

**Goal:** Dar conteúdo real ao **módulo Model** do chrome V2: re-hospedar o `SchematicView` + `ElementPalette` + `PropertyInspector` do `msd_builder.py` dentro do shell, com edição drag-drop funcional, `QUndoStack` ativo e sincronização bidirecional com o `AppState`. Ao ativar o módulo Model, o usuário vê e edita o modelo MSD real (não mais placeholder).

**Architecture:** Um `ModelController` (novo) embrulha uma instância **oculta** de `MSDBuilderWindow` e **expõe** seus três filhos já cablados (`schematic`/`palette`/`inspector`) + o `undo_stack` injetado. Delega `load_model`/`export_model` aos métodos `load_from_msd_model`/`export_to_msd_model` da janela (provado por probe: instancia headless, round-trip 11→11, sobrevive a reparent). O `ChromeWindow` troca seu widget central para um `QStackedWidget` — página 0 = `MultiViewport` (placeholders/outros módulos), página 1 = o `SchematicView` do Model (página estável, não deletada na troca de módulo). Ao ativar Model: mostra a página do schematic, troca o dock direito para o `PropertyInspector` rico, e mostra um dock esquerdo com a `ElementPalette`. Sincronização bidirecional schematic↔AppState com flag de reentrância `_syncing` (sem loop).

**Tech Stack:** PyQt6, pytest (fixture `qapp` offscreen da fundação).

## Global Constraints

- Mesmas da fundação: `utf-8`, `ast.parse` após cada edição, testes offscreen sem `pytest-qt`, **não tocar a V1** exceto o que já é do chrome, **não tocar `core/`/`numerical/`/engine**, não tocar arquivos foreign (`New_Theory/frontier_polish.py`, `New_Theory/liu2025_nemb_probe.py`).
- **NÃO modificar `msd_builder.py`** — o controller o reutiliza como está. Só cria arquivos novos em `gui/chrome/` + edita `gui/chrome/app_window.py`.
- Um commit por tarefa; `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- **Interfaces canônicas:**
  - `ModelController(app_state=None, parent=None)` (QObject) — sinal `model_edited()`; atributos `schematic`, `palette`, `inspector`, `undo_stack`; métodos `load_model(model)`, `export_model() -> Optional[MSDModel]`, `viewport_widget() -> QWidget`, `sync_from_app_state()`; flag `_syncing`.
  - `ChromeWindow` ganha: atributo `model_controller: ModelController`; `_center: QStackedWidget`; docks `_inspector_dock`, `_palette_dock`; comportamento de `switch_module` para Model.

## File Structure

**Create:**
```
src/bolt_analysis_studio/gui/chrome/controllers/
├── __init__.py
└── model_controller.py       # ModelController
tests/
├── test_model_controller.py
└── test_chrome_model_module.py
```
**Modify:** `src/bolt_analysis_studio/gui/chrome/app_window.py` (central QStackedWidget + registro do ModelController + ativação/desativação do Model + sync).

---

## Task 1: `ModelController` — embrulha o MSDBuilderWindow oculto

**Files:**
- Create: `gui/chrome/controllers/__init__.py` (vazio), `gui/chrome/controllers/model_controller.py`
- Test: `tests/test_model_controller.py`

**Interfaces:**
- Consumes: `MSDBuilderWindow` (`gui/msd_builder.py`), `get_app_state` (`core/app_state.py`).
- Produces: `ModelController` (ver interfaces canônicas).

- [ ] **Step 1: Teste** `tests/test_model_controller.py`:

```python
from bolt_analysis_studio.gui.chrome.controllers.model_controller import ModelController
from bolt_analysis_studio.gui.new_analysis_wizard import build_model, AnalysisSpec
from bolt_analysis_studio.core.app_state import get_app_state


def _model():
    return build_model(AnalysisSpec())


def test_controller_exposes_wired_parts(qapp):
    c = ModelController()
    from bolt_analysis_studio.gui.msd_builder import SchematicView, ElementPalette, PropertyInspector
    assert isinstance(c.schematic, SchematicView)
    assert isinstance(c.palette, ElementPalette)
    assert isinstance(c.inspector, PropertyInspector)
    assert c.undo_stack is not None
    assert c.schematic.undo_stack is c.undo_stack           # injetado pela janela
    assert c.viewport_widget() is c.schematic


def test_load_and_export_round_trip(qapp):
    c = ModelController()
    c.load_model(_model())
    assert len(c.schematic.elements) == 11
    exported = c.export_model()
    assert exported is not None and len(exported.elements) == 11


def test_load_none_is_noop(qapp):
    c = ModelController()
    c.load_model(None)                                       # nao levanta
    assert len(c.schematic.elements) == 0


def test_schematic_change_syncs_to_appstate_no_loop(qapp):
    st = get_app_state(); st.new_project()
    c = ModelController(st)
    c.load_model(_model())
    st._model = None                                         # limpa p/ detectar o sync
    c._on_schematic_changed()                                # simula edicao estrutural
    assert st.model is not None and len(st.model.elements) == 11
    assert c._syncing is False                               # flag restaurada (finally)
    st.new_project()


def test_load_does_not_reentrantly_sync(qapp):
    # carregar um modelo NAO deve disparar _on_schematic_changed -> app_state
    st = get_app_state(); st.new_project()
    c = ModelController(st)
    st._model = None
    c.load_model(_model())                                   # durante load, _syncing=True
    assert st.model is None                                  # load nao re-empurrou p/ app_state
    st.new_project()
```

- [ ] **Step 2: Rodar e ver falhar** — `python -m pytest tests/test_model_controller.py -q`.
- [ ] **Step 3: Implementar** `gui/chrome/controllers/__init__.py` (vazio com docstring) e `model_controller.py`:

```python
"""ModelController — embrulha um MSDBuilderWindow oculto e expoe seus filhos
cablados (schematic/palette/inspector) para o chrome V2 re-hospedar. Delega
load/export ao metodo da janela. Sincroniza schematic<->AppState com guarda de
reentrancia (sem loop). Ver Plano 2."""
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from ...msd_builder import MSDBuilderWindow
from ....core.app_state import get_app_state


class ModelController(QObject):
    model_edited = pyqtSignal()   # emitido apos uma edicao estrutural do schematic

    def __init__(self, app_state=None, parent=None):
        super().__init__(parent)
        self.app_state = app_state or get_app_state()
        self._builder = MSDBuilderWindow()
        self._builder.hide()                      # nunca exibida; so fonte das pecas
        self.schematic = self._builder.schematic
        self.palette = self._builder.palette
        self.inspector = self._builder.inspector
        self.undo_stack = self._builder.undo_stack
        self._syncing = False
        # edicao estrutural do schematic -> propaga p/ o AppState
        self.schematic.model_changed.connect(self._on_schematic_changed)

    # --- pecas p/ o chrome hospedar ---
    def viewport_widget(self):
        return self.schematic

    # --- carga/exportacao (delegadas a janela) ---
    def load_model(self, model) -> None:
        if model is None:
            return
        self._syncing = True                      # nao re-sincroniza durante a carga
        try:
            self._builder.load_from_msd_model(model)
        finally:
            self._syncing = False

    def export_model(self) -> Optional[object]:
        return self._builder.export_to_msd_model()

    # --- sincronizacao ---
    def sync_from_app_state(self) -> None:
        if self._syncing:
            return
        model = getattr(self.app_state, "model", None)
        if model is not None:
            self.load_model(model)

    def _on_schematic_changed(self) -> None:
        if self._syncing:
            return
        model = self.export_model()
        if model is None:
            return
        self._syncing = True
        try:
            self.app_state.model = model          # emite model_changed (guardado)
        finally:
            self._syncing = False
        self.model_edited.emit()
```

- [ ] **Step 4: `ast.parse` + `python -m pytest tests/test_model_controller.py -q`** → **5 passed**.
- [ ] **Step 5: Commit** — `git commit -m "feat(chrome): ModelController embrulha MSDBuilderWindow (Plano 2)"`

---

## Task 2: Integrar o Módulo Model no `ChromeWindow`

Trocar o central por `QStackedWidget` (página 0 = MultiViewport; página 1 = schematic do Model); registrar o `ModelController`; ativar/desativar o Model (schematic + inspector rico + palette dock); ligar a sincronização externa.

**Files:**
- Modify: `gui/chrome/app_window.py`
- Test: `tests/test_chrome_model_module.py`

- [ ] **Step 1: Teste** `tests/test_chrome_model_module.py`:

```python
from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
from bolt_analysis_studio.gui.msd_builder import SchematicView, PropertyInspector
from bolt_analysis_studio.gui.new_analysis_wizard import build_model, AnalysisSpec
from bolt_analysis_studio.core.app_state import get_app_state


def test_model_module_shows_schematic_in_center(qapp):
    w = ChromeWindow()
    w.switch_module("Model")
    assert w._center.currentWidget() is w.model_controller.schematic
    assert isinstance(w._center.currentWidget(), SchematicView)


def test_model_module_swaps_inspector_to_rich(qapp):
    w = ChromeWindow()
    w.switch_module("Model")
    assert isinstance(w._inspector_dock.widget(), PropertyInspector)
    assert w._palette_dock.isVisibleTo(w)          # palette aparece no Model


def test_leaving_model_restores_placeholder_and_chrome_inspector(qapp):
    w = ChromeWindow()
    w.switch_module("Model")
    w.switch_module("Results")
    assert w._center.currentWidget() is w.viewport      # volta ao MultiViewport
    assert w._inspector_dock.widget() is w.inspector    # ChromeInspector de volta
    assert not w._palette_dock.isVisibleTo(w)


def test_appstate_model_loads_into_schematic(qapp):
    st = get_app_state(); st.new_project()
    w = ChromeWindow(app_state=st)
    st.model = build_model(AnalysisSpec())
    assert len(w.model_controller.schematic.elements) == 11   # via sync externo
    assert w.tree._element_count() == 11                       # tree tambem popula
    st.new_project()


def test_all_modules_still_switch(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.module_bar import MODULES
    w = ChromeWindow()
    for m in MODULES:
        w.switch_module(m)
        assert w.current_module == m
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Editar `app_window.py`.** Fazer estas mudanças cirúrgicas:

**(a)** Imports no topo: adicionar
```python
from PyQt6.QtWidgets import QStackedWidget   # juntar aos QtWidgets ja importados
from .controllers.model_controller import ModelController
```

**(b)** Em `_build_chrome`, trocar o central de `self.viewport` direto para um stack. Onde hoje está:
```python
        self.viewport = MultiViewport()
        self.setCentralWidget(self.viewport)
```
substituir por:
```python
        self.viewport = MultiViewport()
        self._center = QStackedWidget()
        self._center.addWidget(self.viewport)          # pagina 0: placeholders/outros
        self.setCentralWidget(self._center)
        # controller do Modulo Model (embrulha o builder); seu schematic e pagina 1
        self.model_controller = ModelController(self.app_state)
        self._center.addWidget(self.model_controller.viewport_widget())
```

**(c)** Guardar referências dos docks. Onde o inspector dock é criado, guardar `self._inspector_dock = insp_dock`. E adicionar um palette dock (esquerda, abaixo/junto da tree), inicialmente escondido:
```python
        self._inspector_dock = insp_dock       # (renomear a variavel local p/ atributo)
        # dock da paleta de elementos (so visivel no modulo Model)
        from PyQt6.QtWidgets import QDockWidget
        self._palette_dock = QDockWidget("Elements", self)
        self._palette_dock.setWidget(self.model_controller.palette)
        self._palette_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._palette_dock)
        self._palette_dock.hide()
```
(NOTA: `self.model_controller` precisa existir antes deste bloco — garantir a ordem em `_build_chrome`: criar o controller logo após o stack, como em (b), e o palette dock depois. Se a ordem no arquivo colocar o inspector dock antes do controller, mover a criação do controller para antes.)

**(d)** Em `_wire_signals`, ligar o sync externo. O `_on_model_changed` já existe (popula a tree); estendê-lo para também sincronizar o controller:
```python
    def _on_model_changed(self, model):
        if model is not None:
            self.tree.populate(model)
        # sincroniza o schematic do Modulo Model (guarda de reentrancia no controller)
        self.model_controller.sync_from_app_state()
```

**(e)** Reescrever `switch_module` para tratar o Model especialmente:
```python
    def switch_module(self, name: str) -> None:
        if name not in MODULES:
            return
        self._current_module = name
        self.context_bar.set_module(name)
        self.tree.highlight_module(name)
        self.prompt.set_prompt(_PROMPTS.get(name, ""))
        if name == "Model":
            self._center.setCurrentWidget(self.model_controller.viewport_widget())
            self._inspector_dock.setWidget(self.model_controller.inspector)
            self._palette_dock.show()
        else:
            self._center.setCurrentWidget(self.viewport)
            self.viewport.set_layout(_DEFAULT_LAYOUT.get(name, "1"))
            for i in range(self.viewport.slot_count()):
                self.viewport.set_widget(i, QLabel(f"[ {name} · viewport {i + 1} ]"))
            self._inspector_dock.setWidget(self.inspector)      # ChromeInspector
            self._palette_dock.hide()
        self.statusBar().showMessage(f"Projeto: — · Modulo: {name} · Job: idle")
        if self.module_bar._module_combo.currentText() != name:
            self.module_bar._module_combo.setCurrentText(name)
```

**(f)** No `__init__`, a chamada `if getattr(self.app_state, "model", None) is not None: self.tree.populate(...)` — estender para também `self.model_controller.sync_from_app_state()` (ou confiar que `switch_module("Model")` no fim do init cuida; mas o boot chama `switch_module("Model")` que NÃO carrega o modelo — só troca a UI). Adicionar após o populate:
```python
        if getattr(self.app_state, "model", None) is not None:
            self.tree.populate(self.app_state.model)
            self.model_controller.sync_from_app_state()
```

- [ ] **Step 4: `ast.parse` em `app_window.py`.**
- [ ] **Step 5: Rodar** — `python -m pytest tests/test_chrome_model_module.py -q` → **5 passed**. Se `setWidget` num QDockWidget deletar o widget antigo (não deveria), ou se a ordem de criação do controller/dock quebrar, ajustar conforme o erro (o controller deve existir antes do palette dock).
- [ ] **Step 6: Rodar a suíte de chrome inteira** (garantir que a fundação não regrediu com o central virando stack) — `python -m pytest tests/test_main_window_chrome.py tests/test_chrome_model_module.py -q` → verde. Em especial `test_boots_with_three_zones` e `test_all_modules_switch_without_error` devem continuar passando.
- [ ] **Step 7: Commit** — `git commit -m "feat(chrome): Modulo Model integrado (schematic+palette+inspector, sync AppState) (Plano 2)"`

---

## Task 3: Verificação final + STATUS

- [ ] **Step 1: Suíte chrome completa** — `python -m pytest tests/test_chrome_smoke.py tests/test_auto_combo.py tests/test_collapsible_group.py tests/test_parameter_help.py tests/test_model_tree.py tests/test_inspector_toggle.py tests/test_multi_viewport.py tests/test_chrome_bars.py tests/test_main_window_chrome.py tests/test_chrome_entrypoint.py tests/test_model_controller.py tests/test_chrome_model_module.py -q` → tudo verde.
- [ ] **Step 2: Regressão de domínio** — `python -m pytest tests/test_calibration_server.py tests/test_parameter_registry.py tests/test_library_common.py -q` → verde.
- [ ] **Step 3: Smoke manual opcional (com display):** `python run_app.py --v2`, ir ao módulo Model, arrastar elementos da palette, Ctrl+Z; `File → Nova Análise` popula o schematic.
- [ ] **Step 4: Escrever `docs/superpowers/plans/2026-07-10-chrome-v2-model-module-STATUS.md`** — o que foi entregue + handoff p/ Plano 3 (Contacts + Loads: destacar interfaces de contato no schematic; `PropertyInspector.set_loading_data`/`loading_changed` p/ o módulo Loads; overlays de carga via `schematic.update_load_overlays`).
- [ ] **Step 5: Commit** — `git commit -m "docs(chrome): status Plano 2 (Modulo Model) + handoff Plano 3"`

---

## Self-Review

**Spec coverage:** spec §5 step 4 ("Módulo Model — reutiliza SchematicView") → Tasks 1-2. Reutilização máxima (schematic/palette/inspector + undo + load/export vêm do `MSDBuilderWindow` intacto). ✔
**Placeholder scan:** os placeholders permanecem só para os módulos ainda não implementados (Contacts/Loads/Analysis/Results/Report) — intencional (planos 3-8). ✔
**Type consistency:** `ModelController.viewport_widget()` retorna `self.schematic` (usado em `_center.addWidget` e `switch_module`); `sync_from_app_state`/`_on_schematic_changed`/`_syncing` consistentes entre Task 1 (def) e Task 2 (uso). `_center`/`_inspector_dock`/`_palette_dock`/`model_controller` definidos em `_build_chrome` e usados em `switch_module`/`_on_model_changed`. ✔
**Riscos anotados:** (a) ordem de criação controller-antes-do-palette-dock (Task 2 Step 3c NOTA); (b) `QDockWidget.setWidget` não deve deletar o widget antigo — se deletar, manter refs e usar um QStackedWidget no dock (Task 2 Step 5); (c) `QStackedWidget` não deleta páginas na troca → o schematic sobrevive às trocas de módulo (motivo central do redesign do central).

## Handoff — Plano 3 (Contacts + Loads)
Contacts: schematic com interfaces destacadas/clicáveis (`schematic.contacts`, sinais `context_edit_contact_props_requested`); Loads: alimentar o módulo com `PropertyInspector.get_loading_data/set_loading_data` + sinal `loading_changed(dict)` → `AppState`; overlays de carga no schematic via `update_load_overlays(loading_data)`.
