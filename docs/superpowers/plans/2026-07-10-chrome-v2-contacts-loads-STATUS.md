# Chrome V2 — Status dos Módulos Contacts + Loads (Plano 3 CONCLUÍDO)

**Data:** 2026-07-10 · **Plano:** `2026-07-10-chrome-v2-contacts-loads.md` · **Modo:** inline (executing-plans)

## O que foi entregue

**Contacts** e **Loads** deixaram de ser placeholders: ambos mostram o
`SchematicView` estável (o mesmo do Model — contatos desenhados, overlays de
carga) com o `PropertyInspector` rico focado na aba própria. Edições de
carregamento na aba Loading agora **persistem no `AppState`**
(`export_to_msd_model` → `global_loading`).

| Peça | Arquivo | Testes |
|---|---|---|
| `show_inspector_tab(kind)` (element/loading/contact → aba 0/1/2) + canal loading→AppState (`_builder.model_changed` filtrado por `source=="loading"` → `_push_to_app_state`, refactor de `_on_schematic_changed`) | `gui/chrome/controllers/model_controller.py` | 3 novos (8 total) |
| Família schematic no shell: `_SCHEMATIC_MODULES = {Model: element, Contacts: contact, Loads: loading}`; `switch_module` unifica os 3 (schematic no centro, inspector rico na aba própria, paleta só no Model) | `gui/chrome/app_window.py` | 4 novos (9 total) |

**Total: 52 testes do chrome + 38 de regressão de domínio, todos verdes.**
`msd_builder.py` **não foi modificado** (commits `77ef0f4`, `1e7ed67`).

## Decisões-chave (efetivadas)

- **Módulo = aba do inspector**: Contacts/Loads não são novas telas — são o
  mesmo schematic com o inspector rico focado (mesma semântica de módulo do
  Abaqus). A V1 já fazia isso por botões (`main_window.py:9011/9014`).
- **Canal loading filtrado por `source`**: `MSDBuilderWindow.model_changed(dict)`
  emite `{"source": "loading", ...}` nas edições de carregamento; o controller
  só reage a esse source (edições estruturais já fluem por
  `schematic.model_changed` — evita export duplo no mesmo evento).
- **Overlays e diálogo de contato de graça**: a fiação interna do builder
  oculto já chama `schematic.update_load_overlays` a cada `loading_changed` e
  abre o `ContactPropertiesDialog` no duplo-clique da interface
  (`context_edit_contact_props_requested`) — nada a recablar no chrome.
- **Anti-loop em duas camadas**: `_syncing` no push (o `model_changed` do
  AppState não re-carrega durante o push) e `set_loading_data` é bulk-restore
  que não emite `loading_changed` (`_updating`).

## Limitações honestas

- As abas Contact/Loading são as da V1 as-is — a reorganização Basic/Advanced
  do spec §6 para esses campos ainda não se aplica (mesmo trade-off do Plano 2).
- Trocar de módulo **reseta a aba** do inspector (Model→element, etc.) — a
  sub-navegação manual do usuário dentro do inspector não sobrevive à troca.
- Sem highlight adicional das interfaces de contato além do render existente
  do schematic — exigiria tocar `msd_builder.py` (fora do contrato wrapper).
- O smoke manual com display (overlays ao editar F₀/amplitude; diálogo de
  contato no duplo-clique) não foi exercido em headless — verificação foi
  ast + 52 testes offscreen; a fiação usada é a mesma da V1 em produção.

## Handoff — Plano 4 (Analysis + Jobs)

- Re-hospedar a configuração de análise e a execução: o `SolverTab` da V1
  (`gui/main_window.py`) contém o `SolverWorker` (QThread) e o resumo
  read-only do loading.
- Módulo Analysis: step/dt/n_cycles Basic + integrador (Newmark/HHT) Advanced
  (spec §6); sub-mode **Jobs** com fila/progresso/status do worker.
- O Run deve usar o caminho V2-coerente (`SolverWorker._compute_v2_history`,
  overrides `model._v2_tuner_overrides`, conformação ligada por default) —
  igual à V1; `AppState.results` já existe como barramento dos resultados.
- Padrão consolidado: controller por módulo em `gui/chrome/controllers/`
  re-hospedando peças V1; página no `_center`; `switch_module` decide página +
  inspector + docks contextuais.

Planos 5-8 (Results+Validation, Report, auto-defaults+wizard-first,
integradores + promoção a default) no fim de `2026-07-09-chrome-v2-foundation.md`.
