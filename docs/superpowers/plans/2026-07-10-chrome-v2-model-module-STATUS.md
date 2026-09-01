# Chrome V2 — Status do Módulo Model (Plano 2 CONCLUÍDO)

**Data:** 2026-07-10 · **Plano:** `2026-07-10-chrome-v2-model-module.md` · **Modo:** inline (executing-plans)

## O que foi entregue

O **módulo Model é real**: ao ativá-lo, o usuário vê e edita o modelo MSD no
`SchematicView` (drag-drop da palette, undo/redo, inspector rico), com
sincronização bidirecional com o `AppState`. Os demais módulos seguem em
placeholders (planos 3-8). Confirmado visualmente pelo usuário
(`python run_app.py --v2`, wizard → 12 elementos no schematic).

| Peça | Arquivo | Testes |
|---|---|---|
| `ModelController` — embrulha `MSDBuilderWindow` oculto; expõe `schematic`/`palette`/`inspector` + `undo_stack`; `load_model`/`export_model`; sync com guarda `_syncing` | `gui/chrome/controllers/model_controller.py` | 5 |
| Integração no shell — central `QStackedWidget` (pág. 0 = MultiViewport, pág. 1 = schematic estável), dock `Elements` (palette, só no Model), swap do inspector rico, `_on_model_changed → sync_from_app_state` | `gui/chrome/app_window.py` | 5 |
| Isolamento de teste — `ChromeWindow.closeEvent` desconecta do `model_changed`; fixture autouse `_reset_app_state` (no-op p/ testes sem GUI, checa `sys.modules`) | `app_window.py` + `tests/conftest.py` | (suite) |

**Total: 45 testes do chrome + 38 de regressão de domínio, todos verdes.**
`msd_builder.py` **não foi modificado** — o controller o reutiliza intacto.

## Decisões-chave (efetivadas)

- **Wrapper, não extração**: o `ModelController` instancia um `MSDBuilderWindow`
  oculto e re-hospeda seus filhos já cablados — validado por probe (headless,
  round-trip 11→11 elementos, sobrevive a reparent). Zero risco de regressão na V1.
- **Central em `QStackedWidget`**: o schematic é **página estável** — não é
  deletado na troca de módulo (ao contrário dos slots do MultiViewport, que
  recriam labels). Motivo central do redesign do central.
- **Sync bidirecional com guarda de reentrância** (`_syncing`, try/finally):
  edição no schematic → `export_model` → `AppState.model` (emite
  `model_changed`, guardado); `AppState.model` externo (wizard, load) →
  `sync_from_app_state` → `load_model`.
- **Isolamento do singleton `AppState` nos testes**: janelas de testes
  anteriores acumulavam receivers em `model_changed` e quebravam em `_fit_view`
  quando um teste setava `st.model`. Correção dupla: `closeEvent` desconecta +
  fixture autouse zera o singleton entre testes (sem forçar import de PyQt6
  nos testes numéricos).

## Limitações honestas

- O inspector rico é o `PropertyInspector` da V1 as-is (abas
  Element/Loading/Contact) — a reorganização Basic/Advanced do chrome (spec
  §3.C) não se aplica a ele ainda; o `ChromeInspector` segue nos outros módulos.
- `export_model` roda a cada `model_changed` estrutural do schematic — sem
  debounce; ok na escala atual (≤ dezenas de elementos).
- O `MSDBuilderWindow` oculto existe por inteiro (tabs, menus) — custo de
  memória aceito em troca de reuso total; extração real das peças é
  possível follow-up pós-Plano 8.

## Handoff — Plano 3 (Contacts + Loads)

- **Contacts**: schematic com interfaces de contato destacadas/clicáveis —
  usar `schematic.contacts` e o sinal `context_edit_contact_props_requested`;
  o módulo ativa a aba Contact do inspector rico.
- **Loads**: alimentar o módulo com `PropertyInspector.get_loading_data`/
  `set_loading_data` + sinal `loading_changed(dict)` → `AppState`; overlays
  de carga no schematic via `update_load_overlays(loading_data)`.
- Padrão estabelecido aqui: cada módulo real ganha um controller em
  `gui/chrome/controllers/` que re-hospeda peças V1 e vira página do
  `_center`; `switch_module` decide página + inspector + docks contextuais.

Planos 4-8 (Analysis+Jobs, Results+Validation, Report, auto-defaults+
wizard-first, integradores + promoção a default) no fim de
`2026-07-09-chrome-v2-foundation.md`.
