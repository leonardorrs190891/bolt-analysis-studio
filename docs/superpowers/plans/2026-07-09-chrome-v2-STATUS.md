# Chrome V2 — Status da Fundação (Plano 1 CONCLUÍDO)

**Data:** 2026-07-10 · **Plano:** `2026-07-09-chrome-v2-foundation.md` · **Modo:** inline (executing-plans)

## O que foi entregue

A **casca CAE funcional** do BAS V2, construída em paralelo à V1 (que segue intacta como fallback). Acessível via `python run_app.py --v2`.

| Peça | Arquivo | Testes |
|---|---|---|
| Fixture headless | `tests/conftest.py` (`qapp` offscreen, sem pytest-qt) | smoke |
| AutoComboBox (§3.B) | `gui/chrome/widgets/auto_combo.py` | 4 |
| CollapsibleGroup (§6) | `gui/chrome/widgets/collapsible.py` | 2 |
| parameter_help (§3.E) | `gui/chrome/parameter_help.py` + `.json` | 3 |
| ModelTree (§4) | `gui/chrome/widgets/model_tree.py` | 4 |
| ChromeInspector Basic/Advanced (§3.C) | `gui/chrome/widgets/property_inspector.py` | 4 |
| MultiViewport (§5) | `gui/chrome/widgets/multi_viewport.py` | 4 |
| ModuleBar/ContextBar/PromptArea (§3) | `gui/chrome/widgets/{module_bar,context_bar,prompt_area}.py` | 6 |
| ChromeWindow shell + máquina de módulos | `gui/chrome/app_window.py` | 5 |
| Entry-point opt-in | `run_app.py --v2` | 2 |

**Total: 35 testes do chrome + 38 de regressão de domínio, todos verdes.** Nenhum arquivo da V1/engine foi tocado (só `run_app.py` aditivo + `conftest.py` aditivo).

## Decisões-chave (efetivadas)
- **Construção paralela** em `gui/chrome/` — `main_window.py` V1 intocado.
- **`Theme` + `AppState` reutilizados as-is** (inventário confirmou); o shell subscreve `AppState.model_changed`.
- **Widgets headless-testáveis** sem `pytest-qt`: fixture `qapp` offscreen própria; `ChromeInspector` usa `isVisibleTo` (não `isVisible`) para contar linhas visíveis sem janela mostrada; teste do inspector isola o `QSettings`.
- **`ModelTree.populate`** robusto a `MSDElementData.type` (enum `ElementType`) e a fakes de teste (`element_type` string).

## Limitações honestas (por design da fundação)
- Os viewports mostram **placeholders nomeados** (`[ Model · viewport 1 ]`) — o conteúdo real de cada módulo vem nos planos 2-8.
- `File → Nova Análise` chama o `NewAnalysisWizard` real (defensivo com try/except); a navegação auto-advance pós-Create é do Plano 7.
- O smoke visual (`python run_app.py --v2` num display real) não foi exercido em headless — a verificação foi ast + 35 testes offscreen.

## Handoff — Plano 2: Módulo Model

Re-hospedar as peças reutilizáveis do MSD Builder dentro do chrome, mapeadas pelo inventário:
- `SchematicView` (`msd_builder.py:1311`) no viewport central do módulo Model; injetar um `QUndoStack` (`schematic.undo_stack = ...`) após construir.
- `ElementPalette` (`msd_builder.py:7246`) como dock/context à esquerda; sinais `element_selected(str)`, `preset_requested(str)`.
- `PropertyInspector` (`msd_builder.py:4892`) — decidir entre re-hospedar o inspector rico (abas Element/Loading/Contact) OU alimentar o `ChromeInspector` (grupos Basic/Advanced) com os campos do elemento selecionado.
- Levantar `load_from_msd_model`/`export_to_msd_model` (`msd_builder.py:10947/10853`) para um `ModelController` (não deixá-los presos no `MSDBuilderWindow`).
- Ligar `SchematicView.element_selected` → `ModelTree`/`ChromeInspector`; `AppState.model_changed` → repopular a tree (já ligado no shell).

Planos 3-8 (Contacts/Loads, Analysis+Jobs, Results+Validation, Report, auto-defaults+wizard-first, integradores 5→2 + promoção a default) no fim de `2026-07-09-chrome-v2-foundation.md`.
