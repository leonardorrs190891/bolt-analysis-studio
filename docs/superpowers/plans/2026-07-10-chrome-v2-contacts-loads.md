# Chrome V2 — Módulos Contacts + Loads (Plano 3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (inline) ou subagent-driven-development. Steps em checkbox `- [ ]`.

**Goal:** Dar conteúdo real aos módulos **Contacts** e **Loads** do chrome V2: ambos mostram o mesmo `SchematicView` estável do módulo Model no centro (Contacts com as interfaces de contato já desenhadas; Loads com os overlays de carga), com o `PropertyInspector` rico focado na aba certa (Contact/Loading), e **edições de carregamento propagando ao `AppState`** (persistência via `export_to_msd_model` → `global_loading`).

**Architecture:** Zero extração — mesma estratégia wrapper do Plano 2. O `ModelController` ganha (a) `show_inspector_tab(kind)` que seleciona a aba do `inspector_tabs` (0=element, 1=loading, 2=contact — mesmos índices que a V1 usa em `main_window.py:9011/9014`), e (b) escuta `MSDBuilderWindow.model_changed(dict)` filtrando `source == "loading"` para exportar+empurrar ao `AppState` (o canal estrutural já flui por `schematic.model_changed`; o de loading NÃO — `PropertyInspector.loading_changed → _on_loading_changed` só emite o sinal da janela, hoje sem consumidor no chrome). O `ChromeWindow.switch_module` passa a tratar a **família schematic** `{Model, Contacts, Loads}` uniformemente: página do schematic + inspector rico + aba própria; paleta só no Model. Overlays de carga e diálogo de contato **já funcionam** pela fiação interna do builder oculto (`_on_loading_changed → update_load_overlays`; `context_edit_contact_props_requested → _context_edit_contact_props`).

**Tech Stack:** PyQt6, pytest (fixture `qapp` offscreen + autouse `_reset_app_state`).

## Global Constraints

- Mesmas dos Planos 1-2: `encoding='utf-8'`, `ast.parse` após cada edição, testes offscreen sem `pytest-qt`, **não tocar a V1** exceto o que já é do chrome, **não tocar `core/`/`numerical/`/engine**, não tocar arquivos foreign (`New_Theory/frontier_polish.py`, `New_Theory/liu2025_nemb_probe.py` — têm diffs de outra sessão, não commitá-los).
- **NÃO modificar `msd_builder.py`** — reuso as-is do builder oculto.
- Só editar: `gui/chrome/controllers/model_controller.py`, `gui/chrome/app_window.py`, testes.
- Um commit por tarefa; `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- **Interfaces canônicas (novas neste plano):**
  - `ModelController.show_inspector_tab(kind: str)` — `kind ∈ {"element","loading","contact"}` → `inspector.inspector_tabs.setCurrentIndex(0/1/2)`; kind desconhecido = no-op.
  - `ModelController._push_to_app_state()` — export+push guardado por `_syncing` (refactor do corpo de `_on_schematic_changed`).
  - `ModelController._on_builder_changed(payload: dict)` — reage só a `payload.get("source") == "loading"`.
  - `ChromeWindow._SCHEMATIC_MODULES = {"Model": "element", "Contacts": "contact", "Loads": "loading"}` (dict de classe).

## Fatos do código-base que este plano usa (verificados)

- `PropertyInspector.inspector_tabs` (`msd_builder.py:4996`): aba 0 "Element", 1 "Loading" (:5041), 2 "Contact" (:5072). A V1 já seleciona por índice (`:9011/:9014`).
- `PropertyInspector.loading_changed = pyqtSignal(dict)` (`:4901`); **toda edição de widget** emite `loading_changed(get_loading_data())`; `set_loading_data` (`:6518`) é bulk-restore com `self._updating = True` e **não emite**.
- `MSDBuilderWindow.model_changed = pyqtSignal(dict)` (`:8690`); `_on_loading_changed` (`:9760`) emite `{"source": "loading", "loading_data": data}` **e** já chama `schematic.update_load_overlays(data)`.
- `export_to_msd_model` (`:10853`) lê `inspector.get_loading_data()` e escreve `model.global_loading.{type,F_preload,preload_percent_yield,F_transverse,delta_amplitude,control_mode,frequency,n_cycles,...}` — a persistência do Loads é de graça.
- `SchematicView` já desenha as interfaces de contato (`self.contacts`, `:1343`; render `:1873`) e emite `context_edit_contact_props_requested(int)` (`:1324`) — conectado dentro do builder oculto ao `_context_edit_contact_props` (`:9466`, diálogo `ContactPropertiesDialog`). Nada a fazer no Contacts além de focar a aba.

## File Structure

**Modify:**
```
src/bolt_analysis_studio/gui/chrome/controllers/model_controller.py  # Task 1
src/bolt_analysis_studio/gui/chrome/app_window.py                    # Task 2
tests/test_model_controller.py                                       # Task 1 (append)
tests/test_chrome_model_module.py                                    # Task 2 (append)
```
**Create:** `docs/superpowers/plans/2026-07-10-chrome-v2-contacts-loads-STATUS.md` (Task 3).

---

## Task 1: `ModelController` — seleção de aba + canal loading→AppState

**Files:**
- Modify: `src/bolt_analysis_studio/gui/chrome/controllers/model_controller.py`
- Test: `tests/test_model_controller.py` (append no fim)

**Interfaces:**
- Consumes: `inspector.inspector_tabs` (QTabWidget), `MSDBuilderWindow.model_changed(dict)`, `inspector.loading_changed(dict)`/`set_loading_data`/`get_loading_data`.
- Produces: `show_inspector_tab(kind)`, `_push_to_app_state()`, `_on_builder_changed(payload)` — usados pela Task 2.

- [ ] **Step 1: Escrever os testes (falhando)** — append em `tests/test_model_controller.py`:

```python
def test_show_inspector_tab_selects_index(qapp):
    c = ModelController()
    c.show_inspector_tab("contact")
    assert c.inspector.inspector_tabs.currentIndex() == 2
    c.show_inspector_tab("loading")
    assert c.inspector.inspector_tabs.currentIndex() == 1
    c.show_inspector_tab("element")
    assert c.inspector.inspector_tabs.currentIndex() == 0
    c.show_inspector_tab("nope")                             # desconhecido = no-op
    assert c.inspector.inspector_tabs.currentIndex() == 0


def test_loading_edit_pushes_to_appstate(qapp):
    # Simula a edicao do usuario na aba Loading: set_loading_data (bulk, nao
    # emite) + emissao manual de loading_changed (o que qualquer widget faz).
    st = get_app_state(); st.new_project()
    c = ModelController(st)
    c.load_model(_model())
    st._model = None                                         # p/ detectar o push
    c.inspector.set_loading_data({"F_preload": 77777.0})
    c.inspector.loading_changed.emit(c.inspector.get_loading_data())
    assert st.model is not None
    assert abs(st.model.global_loading.F_preload - 77777.0) < 1e-6
    assert c._syncing is False                               # flag restaurada
    st.new_project()


def test_builder_changed_ignores_non_loading_sources(qapp):
    st = get_app_state(); st.new_project()
    c = ModelController(st)
    c.load_model(_model())
    st._model = None
    c._on_builder_changed({"source": "outra_coisa"})
    assert st.model is None                                  # nao empurrou
    st.new_project()
```

- [ ] **Step 2: Rodar e ver falhar** — `python -m pytest tests/test_model_controller.py -q` → 3 novos FAIL (`AttributeError: show_inspector_tab` etc.), 5 antigos PASS.

- [ ] **Step 3: Implementar** em `model_controller.py`:

**(a)** Constante de módulo (após os imports, antes da classe):

```python
# Abas do PropertyInspector rico (mesmos indices que a V1 usa em main_window).
_TAB_INDEX = {"element": 0, "loading": 1, "contact": 2}
```

**(b)** No `__init__`, logo após `self.schematic.model_changed.connect(self._on_schematic_changed)`:

```python
        # canal de loading: PropertyInspector.loading_changed -> (builder oculto)
        # _on_loading_changed -> model_changed({"source": "loading"}) -> push.
        self._builder.model_changed.connect(self._on_builder_changed)
```

**(c)** Novo método público (junto de `viewport_widget`):

```python
    def show_inspector_tab(self, kind: str) -> None:
        idx = _TAB_INDEX.get(kind)
        if idx is not None:
            self.inspector.inspector_tabs.setCurrentIndex(idx)
```

**(d)** Refatorar `_on_schematic_changed` extraindo `_push_to_app_state`, e adicionar `_on_builder_changed` — substituir o método `_on_schematic_changed` inteiro por:

```python
    def _push_to_app_state(self) -> None:
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

    def _on_schematic_changed(self) -> None:
        self._push_to_app_state()

    def _on_builder_changed(self, payload) -> None:
        # So o canal de loading: edicoes estruturais ja fluem por
        # schematic.model_changed (evita export duplo no mesmo evento).
        if isinstance(payload, dict) and payload.get("source") == "loading":
            self._push_to_app_state()
```

- [ ] **Step 4: `ast.parse` + rodar** — `python -c "import ast; ast.parse(open('src/bolt_analysis_studio/gui/chrome/controllers/model_controller.py', encoding='utf-8').read()); print('OK')"` e `python -m pytest tests/test_model_controller.py -q` → **8 passed**.

- [ ] **Step 5: Commit**

```bash
git add src/bolt_analysis_studio/gui/chrome/controllers/model_controller.py tests/test_model_controller.py
git commit -m "feat(chrome): ModelController — abas do inspector + canal loading->AppState (Plano 3)"
```

---

## Task 2: `ChromeWindow` — Contacts e Loads viram módulos schematic

**Files:**
- Modify: `src/bolt_analysis_studio/gui/chrome/app_window.py`
- Test: `tests/test_chrome_model_module.py` (append no fim)

**Interfaces:**
- Consumes: `ModelController.show_inspector_tab(kind)` (Task 1), `viewport_widget()`, docks `_inspector_dock`/`_palette_dock` (Plano 2).
- Produces: `ChromeWindow._SCHEMATIC_MODULES` (dict de classe) + novo comportamento de `switch_module` para Contacts/Loads.

- [ ] **Step 1: Escrever os testes (falhando)** — append em `tests/test_chrome_model_module.py`:

```python
def test_contacts_module_shows_schematic_and_contact_tab(qapp):
    w = ChromeWindow()
    w.switch_module("Contacts")
    assert w._center.currentWidget() is w.model_controller.schematic
    assert isinstance(w._inspector_dock.widget(), PropertyInspector)
    assert w.model_controller.inspector.inspector_tabs.currentIndex() == 2
    assert not w._palette_dock.isVisibleTo(w)      # paleta so no Model


def test_loads_module_shows_schematic_and_loading_tab(qapp):
    w = ChromeWindow()
    w.switch_module("Loads")
    assert w._center.currentWidget() is w.model_controller.schematic
    assert w.model_controller.inspector.inspector_tabs.currentIndex() == 1
    assert not w._palette_dock.isVisibleTo(w)


def test_model_module_selects_element_tab_and_palette(qapp):
    w = ChromeWindow()
    w.switch_module("Loads")
    w.switch_module("Model")
    assert w.model_controller.inspector.inspector_tabs.currentIndex() == 0
    assert w._palette_dock.isVisibleTo(w)


def test_leaving_schematic_family_restores_placeholders(qapp):
    w = ChromeWindow()
    w.switch_module("Contacts")
    w.switch_module("Analysis")
    assert w._center.currentWidget() is w.viewport
    assert w._inspector_dock.widget() is w.inspector
    assert not w._palette_dock.isVisibleTo(w)
```

- [ ] **Step 2: Rodar e ver falhar** — `python -m pytest tests/test_chrome_model_module.py -q` → os 2 primeiros novos FAIL (Contacts/Loads ainda caem no ramo placeholder), 5 antigos PASS.

- [ ] **Step 3: Editar `app_window.py`.** Duas mudanças cirúrgicas:

**(a)** Dict de classe, logo após a linha `class ChromeWindow(QMainWindow):` (antes do `__init__`):

```python
    # Familia schematic: modulos que mostram o SchematicView estavel no centro,
    # diferindo so na aba do inspector rico (spec §6: Model/Contacts/Loads).
    _SCHEMATIC_MODULES = {"Model": "element", "Contacts": "contact", "Loads": "loading"}
```

**(b)** Em `switch_module`, substituir o bloco `if name == "Model": ... else: ...` inteiro por:

```python
        if name in self._SCHEMATIC_MODULES:
            # Familia Model/Contacts/Loads: schematic estavel no centro,
            # inspector rico na aba propria; paleta de elementos so no Model.
            self._center.setCurrentWidget(self.model_controller.viewport_widget())
            self._inspector_dock.setWidget(self.model_controller.inspector)
            self.model_controller.show_inspector_tab(self._SCHEMATIC_MODULES[name])
            self._palette_dock.setVisible(name == "Model")
        else:
            # Demais modulos: placeholders no MultiViewport, ChromeInspector.
            self._center.setCurrentWidget(self.viewport)
            self.viewport.set_layout(_DEFAULT_LAYOUT.get(name, "1"))
            for i in range(self.viewport.slot_count()):
                self.viewport.set_widget(i, QLabel(f"[ {name} · viewport {i + 1} ]"))
            self._inspector_dock.setWidget(self.inspector)
            self._palette_dock.hide()
```

- [ ] **Step 4: `ast.parse`** — `python -c "import ast; ast.parse(open('src/bolt_analysis_studio/gui/chrome/app_window.py', encoding='utf-8').read()); print('OK')"`.

- [ ] **Step 5: Rodar** — `python -m pytest tests/test_chrome_model_module.py tests/test_model_controller.py -q` → **17 passed** (9+8). Atenção ao teste antigo `test_leaving_model_restores_placeholder_and_chrome_inspector` (sai p/ "Results" — segue no ramo placeholder, deve continuar verde).

- [ ] **Step 6: Suíte chrome inteira** — `python -m pytest tests/test_main_window_chrome.py tests/test_chrome_model_module.py tests/test_model_controller.py -q` → verde (em especial `test_all_modules_switch_without_error`, que agora passa pelos dois ramos novos).

- [ ] **Step 7: Commit**

```bash
git add src/bolt_analysis_studio/gui/chrome/app_window.py tests/test_chrome_model_module.py
git commit -m "feat(chrome): modulos Contacts e Loads reais (familia schematic + aba propria) (Plano 3)"
```

---

## Task 3: Verificação final + STATUS

- [ ] **Step 1: Suíte chrome completa** — `python -m pytest tests/test_chrome_smoke.py tests/test_auto_combo.py tests/test_collapsible_group.py tests/test_parameter_help.py tests/test_model_tree.py tests/test_inspector_toggle.py tests/test_multi_viewport.py tests/test_chrome_bars.py tests/test_main_window_chrome.py tests/test_chrome_entrypoint.py tests/test_model_controller.py tests/test_chrome_model_module.py -q` → tudo verde (52 esperados: 45 do Plano 2 + 7 novos).
- [ ] **Step 2: Regressão de domínio** — `python -m pytest tests/test_calibration_server.py tests/test_parameter_registry.py tests/test_library_common.py -q` → **38 passed**.
- [ ] **Step 3: Smoke manual opcional (com display):** `python run_app.py --v2` → wizard cria modelo → módulo Loads: mudar F₀/amplitude na aba Loading e ver os overlays no schematic; módulo Contacts: duplo-clique numa interface de contato abre o `ContactPropertiesDialog`.
- [ ] **Step 4: Escrever `docs/superpowers/plans/2026-07-10-chrome-v2-contacts-loads-STATUS.md`** — o que foi entregue (tabela peça/arquivo/testes), decisões (família schematic; canal loading filtrado por `source`; overlays/diálogo de graça pela fiação interna do builder), limitações honestas (aba Contact é a da V1 as-is, sem reorganização Basic/Advanced §6; troca de módulo reseta a aba do inspector; sem highlight extra de contatos além do render existente — exigiria tocar `msd_builder.py`), e handoff p/ o Plano 4 (Analysis + Jobs: `SolverTab`/`SolverWorker` re-hospedados, submissão/monitor de job, spec §5 passo 6).
- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/2026-07-10-chrome-v2-contacts-loads-STATUS.md
git commit -m "docs(chrome): status Plano 3 (Contacts+Loads) + handoff Plano 4"
```

---

## Self-Review

**Spec coverage:** spec §5 passo 5 ("Módulos Contacts e Loads — extensões do Model module") → Tasks 1-2; §6 define as abas-fonte (Contact/Loading do inspector rico). A reorganização Basic/Advanced do §6 para esses campos fica explicitamente fora (limitação honesta — segue o padrão do Plano 2, que manteve o inspector rico as-is). ✔
**Placeholder scan:** nenhum TBD/TODO; todo step de código tem o código; comandos com resultado esperado. ✔
**Type consistency:** `show_inspector_tab(kind)` definido na Task 1 (c) e consumido na Task 2 (b) com os mesmos kinds do `_SCHEMATIC_MODULES`; `_push_to_app_state`/`_on_builder_changed` definidos na Task 1 (d), testados na Task 1 Step 1; `_SCHEMATIC_MODULES` definido e usado só na Task 2. Índices de aba {0,1,2} conferidos contra `msd_builder.py:5010/5041/5072`. ✔
**Riscos anotados:** (a) loop loading→push→model_changed→sync→load→set_loading_data: interrompido duas vezes (`_syncing` no push; `set_loading_data` não emite por `_updating`); (b) export duplo por evento estrutural: evitado filtrando `source == "loading"`; (c) `setVisible(name == "Model")` substitui o par show()/hide() — mesmo efeito, um caminho só.

## Handoff — Plano 4 (Analysis + Jobs)

Re-hospedar a configuração de análise e a execução: `SolverTab` (V1 `gui/main_window.py`) tem o `SolverWorker` (QThread) e o resumo read-only do loading; o módulo Analysis expõe step/dt/n_cycles + integrador (spec §6), o sub-mode Jobs mostra fila/progresso. `AppState` já carrega `results`; o Run deve rodar o caminho V2-coerente (`_compute_v2_history`) como na V1.
