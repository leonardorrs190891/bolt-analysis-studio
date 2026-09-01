# Módulo Validation no chrome V2 — Status (Plano B CONCLUÍDO)

**Data:** 2026-07-10 · **Plano:** `2026-07-10-validation-gui-module.md` ·
**Spec:** `2026-07-10-validation-case-reports-design.md` §4 + requisito do
professor ("todos esses estudos devem estar disponíveis para ser rodados
livremente no software") · **Modo:** inline

## O que foi entregue

O módulo **Results** do chrome V2 (`python run_app.py --v2`) agora abre o
**navegador de validação**: árvore fonte→caso (128), detalhe com curva
artigo-vs-modelo + decomposição por mecanismo + métricas + staleness, e as
ações Re-simular caso · Re-simular tudo (thread) · Report HTML · Report geral
· **Abrir no Model/Run**.

| Peça | Responsabilidade | Testes |
|---|---|---|
| `validation/runner.py` (refactor) | `material_kwargs_for`/`loading_for` públicos — fonte única de montagem p/ runner E GUI | 2 novos (9) |
| `validation/gui_bridge.py` | caso → `AnalysisSpec`+`build_model` + `_v2_tuner_overrides` (material) + `_v2_geometry_overrides` (geometria SI com proveniência) + fricção Level-2/3 | 5 |
| `core/solver_worker.py` | canal ADITIVO `_v2_geometry_overrides` no `_compute_v2_history` (ausente/inválido = bit-idêntico ao anterior) | 2 |
| `chrome/widgets/validation_browser.py` | árvore + detalhe matplotlib (curvas + decomposição empilhada) + botões/sinais | 4 |
| `chrome/controllers/validation_controller.py` | orquestração: `_ResimWorker` (QThread, store salvo por caso), abrir reports, `open_in_model` | 2 |
| `chrome/app_window.py` | Results → página Validation; `case_opened_in_model` → `switch_module("Model")` | 3 |

**Suítes: 61 chrome + 44 validation/solver + 38 regressão de domínio, verdes.**

## Fidelidade Run-vs-report (MEDIDA, não presumida)

O mesmo caso pelos dois caminhos (`simulate_case` do report vs
`_compute_v2_history` do Run com o modelo do bridge), lu2024_M8_fig18_amp2p0:
**delta máx 0.00016, médio 0.00008** em F/F₀ (final 0.0858 vs 0.0856). Os dois
canais de override (material + geometria) fecham o gap que existia (Run usava
L_eff=3d e A_contact=1e-4 fixos). Resíduo ~1e-4 = detalhes internos do Run
(p_ref da conformação via %yield vs A_contact, arredondamentos) —
documentado, desprezível vs MAE típico 0.03-0.2.

## Fluxo "rodar livremente" (requisito atendido)

Results → selecionar caso → **Abrir no Model/Run** → o app monta o modelo MSD
completo (cadeia com GROUND, F₀ do caso, µ nos dois níveis, carregamento
disp/força com amplitude/freq/ciclos do caso, CSV de referência p/ overlay) e
navega ao Model — dali o usuário **edita o que quiser** (inspector rico,
palette, Loading/Contact) e roda a análise; os overrides de caso continuam
anexados até serem alterados. Casos da família `other` (Sandia modal, sem
proveniência de carregamento) têm o botão desabilitado — degradação honesta.

## Limitações honestas

- Re-simular tudo roda na thread com progresso por caso na árvore, mas sem
  barra/percentual dedicado (polish de UI p/ os planos do chrome).
- O V1 (7 abas) não ganhou o browser — continua com o Validation Suite Dialog
  (PASS/FAIL) + menu Validation Gallery (reports HTML via pacote). O caminho
  novo é o chrome V2.
- `test_leaving_model_restores_placeholder_and_chrome_inspector` (Plano 2) foi
  atualizado: usava "Results" como exemplo de placeholder; agora usa "Report".
- Editar o modelo depois de "Abrir no Model" NÃO recalcula os overrides de
  caso (são um snapshot do caso; mudar diâmetro do parafuso no inspector não
  atualiza `_v2_geometry_overrides` — o usuário assume a autoria da variação;
  os campos do config do Run continuam mandando em F0/n_cycles).

## Handoff

- **Plano 4 da sequência chrome (Analysis + Jobs)**: re-hospedar SolverTab/
  SolverWorker; com ele o fluxo caso→Model→**Run** fica 100% dentro do V2
  (hoje o Run mora na V1/SolverTab).
- Adoção das configs por-curva (fecha o gap de adoção do Plano A) — decisão
  do professor; promover zhang2006 a casos; `library_common` delegar ao pacote.
