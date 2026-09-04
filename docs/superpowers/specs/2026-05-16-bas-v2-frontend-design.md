# Design — BAS V2 frontend (Abaqus-style, simplificado)

**Data:** 2026-05-16
**Autor:** Prof. Leonardo Rosa Ribeiro da Silva (brainstorm)
**Status:** Design aprovado. Pronto para plano de implementação.
**Repositório:** `C:\Users\leo_r\OneDrive\BPL\Analitical\BAS_V2` (fork de `BAS@548dd6a`).
**Base:** Este spec estende `2026-05-16-abaqus-frontend-design.md` (mesma pasta) com o pacote de simplificações decidido em 2026-05-16. Onde houver conflito, este documento prevalece.

---

## 0. O que muda em relação ao BAS v4.0 (resumo executivo)

V2 mantém **toda a física e ciência** do BAS v4.0 — modelos de fricção, wear, preload-loss, similitude, validation, calibration permanecem completos. A reorganização é em duas frentes:

1. **Layout CAE-style** — janela única com module dropdown, Model Tree, multi-viewport, Property Inspector. Substitui as 7 abas. (Detalhado em `2026-05-16-abaqus-frontend-design.md`.)
2. **Simplificações de UX** — defaults inteligentes, Basic/Advanced toggle, wizard-first, inline help. Detalhado abaixo (§3).

Não há remoção de capacidade física. Há remoção de **integradores numéricos redundantes** (de 5 para 2) e **reorganização do que aparece por default** (de "tudo na mesa" para "essencial primeiro, advanced sob clique").

---

## 0.1. Update 2026-05-17 — remoção do módulo Similitude

Decisão de 2026-05-17: o módulo **Similitude** sai do V2. Razão: o foco do V2 é o modelo energético não-linear (DynamicStiffnessAnalyzer + two-factor loosening theory), que ainda não está em condições para análise de similaridade. Quando a teoria estiver calibrada, similaridade volta como módulo separado em V3.

**Consequências:**
- Frontend: 7 → 6 módulos (Model, Contacts, Loads, Analysis, Results, Report)
- Tree: nó "📐 Similitude Studies" removido. Multi-bolt e Geometric scaling não aparecem mais.
- Código: `core/similitude/` pode ser mantido na codebase (não é GUI-acoplado) mas não tem entrada UI.
- Spec teórico `2026-05-16-two-factor-loosening-theory.md` §9.1 e §9.2: remover menções a Similitude no Inspector.

---

## 1. Layout & estrutura (referência)

Layout, módulos, Model Tree, multi-viewport, linguagem visual: ver `2026-05-16-abaqus-frontend-design.md` §1–§11. Em síntese:

- 6 módulos: **Model · Contacts · Loads · Analysis · Results · Report**. (Similitude foi removida — ver §0.1.)
- Tree à esquerda, multi-viewport central (1 / 1×2 / 2×1 / 2×2), Inspector à direita.
- Dark engineering moderno (`#1e1e1e` base, accent `#007acc`).
- Jobs e Validation como nós da Tree mapeando para os módulos Analysis e Results respectivamente.

Este documento não repete esses detalhes; só sobrescreve onde necessário.

---

## 2. O que sobrevive da física (preservado intacto)

| Camada | Conteúdo preservado |
|--------|---------------------|
| Fricção | Coulomb · Stribeck · Rate-State · Elasto-Plastic · LuGre (5 modelos) |
| Wear | Archard 3-fase · Energy-based (Fouvry) · Fretting (Vingsbo-Söderberg) · Fatigue (4 modelos) |
| Preload-loss | Jiang 5-stage transverse · 3-stage axial · Junker clássico · Pai-Hess · Yamamoto · Nassar · Hattori · gasket creep Bouzid (8 modelos) |
| Similitude | Multi-bolt reduction · Geometric scaling (Buckingham Π) |
| Calibration | `ParameterIdentifier` + `CalibrationDialog` (μ, Stage I/II params) |
| Validation | 97 papers indexados, reference curves âncora interna, `validation_cases.py` |
| VDI 2230 | R-factor, dynamic factor, n_load_plane, waveform |
| Locking devices | 8 tipos (free, prevailing torque, Nord-Lock, Belleville, double-nut, chemical, etc.) |
| Matriz | Newmark-β + HHT-α (ver §3.A) |

Tudo isso continua na codebase. A diferença vs v4.0 é como aparece na UI.

---

## 3. Pacote de simplificações UX (V2 only)

### 3.A. Integradores numéricos: 5 → 2

**Sobrevivem:**
- **Newmark-β** (α=0.5, β=0.25, average-acceleration) — default. Incondicionalmente estável, segunda ordem, energy-preserving. Cobre 95% dos casos.
- **HHT-α** — opção para problemas com modos espúrios de alta frequência (amortecimento numérico controlado por α).

**Saem do código:**
- Central Difference
- Modal Superposition
- RK4 explícito

**Onde aparece na UI:** módulo Analysis, Inspector, grupo "Solver", visível apenas em modo **Advanced** (ver §3.C). Default: Newmark-β; combo "Integrator: [Newmark-β ▼ / HHT-α]" com tooltip explicando quando preferir cada um.

**Migração:** o factory `create_integrator(method_name)` perde 3 branches. `time_integration.py` perde 3 classes. Testes que referenciam os removidos são atualizados ou removidos.

### 3.B. Auto-defaults inteligentes

Todo combo box de modelo físico passa a ter `Auto (<inferido>)` como primeira opção e default. A inferência usa o contexto disponível:

| Combo | Regra de inferência |
|-------|---------------------|
| Friction model | `Coulomb` se dry · `Stribeck` se `lubricated=True` · `LuGre` se locking device tipo Nord-Lock (alto stick-slip) |
| Wear model | `Archard 3-fase` se metallic · `Fretting (Vingsbo)` se amplitude < 50 µm · `Fatigue` se Miner's D estimado > 0.3 |
| Preload-loss model | `Jiang 5-stage` se loading transverse · `3-stage axial` se loading axial · `+ Bouzid creep` adicional se há gasket no modelo |
| Solver integrator | `Newmark-β` sempre (HHT só por escolha explícita) |
| Slip-onset factor | `Auto (0.46 Pai-Hess)` se nenhum locking device · valor do locking device se houver |

Usuário vê `Auto (Coulomb)` no combo; clicar abre o dropdown completo com todas as 5 opções. Selecionar override fixa a escolha (texto vira `Coulomb` sem o prefixo "Auto"). Botão "Reset to Auto" em cada combo retorna ao default inferido.

Implementação: cada combo box é `AutoComboBox(QComboBox)` que aceita `inference_fn=callable_returning_default(context)` e expõe `is_auto`/`current_resolved_value()`.

### 3.C. Inspector com toggle Basic ↔ Advanced

Toggle no header do Inspector (`[Basic / Advanced]`, segmented switch). Default: **Basic**.

**Basic** mostra ~10–12 campos essenciais por nó selecionado:
- Loading > Global → Load type, F₀, % Yield, Δ amplitude, Frequency, N cycles
- Locking → Type, Junker class (read-only)
- Contact (thread) → μ_static, k_thread, n_threads engaged
- Analysis > Step → Solver default ("Auto · Newmark"), Steps, dt, n_cycles
- Results > plot → X/Y axis, Reference overlay, MAE/RMSE pass/fail

**Advanced** expande para tudo:
- Loading > Global → +VDI 2230 (R, Phi, dyn factor, waveform), thermal ΔT, ext force/torque, slip-onset factor
- Locking → +friction Δμ, slip-onset override, Junker class detail
- Contact → +μ_kinetic, K_archard, hardness, fretting threshold, helix angle, friction model, wear model
- Analysis > Step → +integrator (Newmark/HHT), HHT-α, tolerances, max iter, time-step adaptation
- Results > plot → +color scheme, style, range overrides, smoothing window

O toggle persiste por sessão (`QSettings`). Tooltip do botão: "Basic: campos essenciais. Advanced: todos os parâmetros."

Critério para classificar campo como Basic vs Advanced: o campo Basic é aquele que **muda o resultado em mais de 5% nos casos do training set** (âncora interna-13A, Lu 2024, Jiang 2003). Tudo que afeta menos de 5% e tem default razoável vai pra Advanced. Lista canônica de campos Basic está em §6.

### 3.D. Wizard-first com ícone 🧙

Botão **"🧙 Nova Análise"** primário e proeminente:
- No módulo **Project** (página inicial pós-splash), como card grande no topo da página
- No menu **File → Nova Análise…** com shortcut `Ctrl+Shift+N`
- Não escondido em sub-menu; é o caminho primário de entrada

Wizard de 5 páginas (mantém estrutura do `NewAnalysisWizard` atual):
1. Joint preset (single_metal · single_gasketed · with_washers · cfrp · blank)
2. Bolt (grade, diameter, length, preload % yield)
3. Loading (type, amplitude, frequency, cycles)
4. Reference CSV (opcional — para validation overlay)
5. Review (resumo + botão Create)

Após "Create": modelo construído via `build_model(spec)`, app navega automaticamente para módulo Model → módulo Loads → módulo Analysis → "Run". Onboarding contínuo, sem o usuário precisar saber onde clicar em seguida. Visualmente: barra de progresso horizontal "1·Model ─ 2·Contacts ─ 3·Loads ─ 4·Analysis ─ 5·Run" no topo, com o passo atual destacado.

### 3.E. Help inline (tooltips e info chips)

Cada campo do Inspector tem ícone `?` à direita (cor `#888`, hover `#fff`). Hover mostra tooltip 1-3 linhas:

```
μ_static
Coefficient of static friction (dry: 0.10–0.20 · lubricated: 0.05–0.12).
Higher = more resistance to initial slip. Pai-Hess slip-onset uses 0.46×μ.
```

Tooltips vêm de um catálogo único `gui/parameter_help.json` (chave = nome do widget, valor = string). Mantém docs sincronizadas com a UI; tradução BR/EN futura simples.

Validação visual inline: quando o valor digitado está fora da faixa típica, o campo ganha border `#d4b13a` (amarelo) + ícone `⚠` ao lado, com tooltip explicando ("μ = 0.50 is unusually high — typical range 0.10–0.20"). Não bloqueia entrada; só sinaliza.

---

## 4. Estrutura de pastas em V2 (proposta)

```
BAS_V2/
├── src/bolt_analysis_studio/
│   ├── core/                    (mesma estrutura do v4.0 — datos, contatos, similitude, etc.)
│   ├── numerical/
│   │   ├── time_integration.py  (REDUZIDO: só Newmark + HHT)
│   │   ├── coupled_loosening_analyzer.py
│   │   ├── friction_models.py
│   │   ├── wear_models.py
│   │   ├── preload_loss_models.py
│   │   └── ...
│   ├── visualization/           (reaproveitado: plotters matplotlib)
│   ├── gui/
│   │   ├── main_window.py       (NOVO: QMainWindow + module bar + dock widgets)
│   │   ├── modules/
│   │   │   ├── model_module.py
│   │   │   ├── contacts_module.py
│   │   │   ├── loads_module.py
│   │   │   ├── analysis_module.py
│   │   │   ├── results_module.py
│   │   │   └── report_module.py
│   │   ├── widgets/
│   │   │   ├── model_tree.py
│   │   │   ├── property_inspector.py    (com toggle Basic/Advanced)
│   │   │   ├── auto_combo.py            (combo com Auto-default + override)
│   │   │   ├── multi_viewport.py        (1 / 1×2 / 2×1 / 2×2)
│   │   │   ├── module_bar.py
│   │   │   ├── context_bar.py
│   │   │   └── prompt_area.py
│   │   ├── new_analysis_wizard.py       (reaproveitado, mais proeminente)
│   │   ├── parameter_help.json          (catálogo de tooltips)
│   │   └── theme.py                     (paleta dark engineering)
│   └── ...
├── tests/
│   ├── test_main_window_chrome.py       (NOVO)
│   ├── test_model_tree.py               (NOVO)
│   ├── test_auto_combo.py               (NOVO)
│   ├── test_inspector_toggle.py         (NOVO)
│   ├── test_multi_viewport.py           (NOVO)
│   └── ...                              (todos os testes de domínio existentes mantidos)
├── docs/superpowers/specs/
│   ├── 2026-05-16-abaqus-frontend-design.md     (base layout)
│   └── 2026-05-16-bas-v2-frontend-design.md     (este documento)
└── ...
```

A camada `gui/main_window.py` atual do v4.0 (~5000 linhas com 7 abas) será **reescrita do zero** — não migrada. Os widgets reutilizáveis (SchematicView, MatrixViewerDialog, plot canvases) vêm intactos.

---

## 5. Migração de v4.0 → V2 (estratégia)

V2 não tenta manter retrocompatibilidade visual com v4.0 — é um redesign. Mas mantém:

- **Formato `.msd`**: idêntico. Arquivos do v4.0 abrem em V2 sem conversão.
- **API pública de `core/` e `numerical/`**: idêntica. Scripts do usuário continuam funcionando.
- **`AppState`, `MSDModel`, `AnalysisResult`**: mesmos dataclasses, mesma serialização.

A reescrita é estritamente da camada `gui/`. Ordem sugerida:

1. Esqueleto `main_window.py` (QMainWindow + menubar + module bar + status bar). Sem módulos funcionais ainda.
2. Widgets compartilhados (`model_tree`, `property_inspector`, `auto_combo`, `multi_viewport`, `context_bar`, `prompt_area`).
3. Theme + parameter_help.json.
4. Módulo Model (mais simples — reutiliza SchematicView).
5. Módulos Contacts e Loads (extensões do Model module).
6. Módulo Analysis + Jobs sub-mode.
7. Módulo Results + Validation sub-mode (reaproveita plotters da visualization/).
8. Módulo Report (menos crítico para a sensação inicial).
9. Wizard-first integration + auto-defaults wiring.
10. Basic/Advanced toggle finalization + parameter_help tooltips.

Cada passo é um plano de implementação separado (writing-plans skill).

---

## 6. Lista canônica de campos Basic vs Advanced

Critério aplicado: campo é **Basic** se está nesta lista; caso contrário é **Advanced** (visível só com toggle).

### Module: Model
**Basic:** Material grade · diameter · length · k · c · m
**Advanced:** Yield stress override · density · thermal expansion · damping ratio per element

### Module: Contacts
**Basic:** μ_static (per contact) · k_thread · n threads engaged · contact type
**Advanced:** μ_kinetic · friction model · wear model · K_archard · hardness · fretting threshold · helix angle · damping per contact · slip-onset factor

### Module: Loads
**Basic:** Load type (TRANSVERSE/AXIAL/COMBINED) · F₀ preload · % Yield (auto) · Δ amplitude · Frequency · N cycles · Locking device type
**Advanced:** VDI 2230 R-factor · Phi_load · dynamic factor · n_load_plane · waveform · Thermal ΔT · ext force · ext torque · slip-onset override · friction Δμ from locking · Junker class · per-element loads

### Module: Analysis
**Basic:** Step name · dt (auto) · n_cycles
**Advanced:** Integrator (Newmark/HHT) · HHT-α · Newmark β,γ · max iter · tolerances · time-step adaptation · adaptive dt min/max · output frequency

### Module: Results
**Basic:** Active plots (chips) · Reference overlay · Layout · X/Y axis · MAE/RMSE pass/fail
**Advanced:** Color scheme · line style · marker · smoothing window · range overrides · phase label format · damage threshold display

### Module: Similitude
**Basic:** Scale factor · prototype bolt · target bolt
**Advanced:** Π groups visibility · individual scaling ratios · joint stiffness correction · Wiegand index

### Module: Report
**Basic:** Template · sections enabled (checkboxes) · Format (PDF/HTML/CSV)
**Advanced:** Header text · logo path · footer text · per-section options

---

## 7. O que sai (lista explícita de remoções)

- **Aba "Documentation"** → menu Help → User Guide (mesmo conteúdo).
- **`time_integration.py`**:
  - `class CentralDifferenceIntegrator` → removida
  - `class ModalSuperposition` → removida
  - `class RungeKutta4` → removida
  - `create_integrator()` factory → mantida, retorna só Newmark ou HHT
- **`tests/test_time_integration_*.py`** → testes dos 3 integradores removidos saem; testes Newmark/HHT permanecem.
- **MSD Builder atual** → substituído pelo conjunto de módulos Model/Contacts/Loads. Lógica do SchematicView e ContactPropertiesDialog **reaproveitada**.
- **SolverTab atual** → substituído pelo módulo Analysis + sub-mode Jobs.
- **ResultsTab atual** → substituído pelo módulo Results + sub-mode Validation.
- **Similitude/Reports tabs atuais** → substituídos pelos módulos homônimos.
- **DocumentationTab** → removida.

Nenhuma remoção em `core/`, `numerical/` (exceto integradores), `visualization/`.

---

## 8. Testes

Mantém todos os testes de domínio existentes (`test_coupled_loosening.py`, `test_independent_joints.py`, `test_validation_cases.py`, `test_parameter_identifier.py`, etc.).

Novos testes de UI/widgets:
- `test_main_window_chrome.py` — QMainWindow boot, menubar wired, module dropdown switching
- `test_model_tree.py` — hierarchy population, selection → module switch, signal propagation
- `test_property_inspector.py` — Basic/Advanced toggle, persistence, field grouping
- `test_auto_combo.py` — inference function dispatch, override behavior, reset
- `test_multi_viewport.py` — layout switching (1 / 1×2 / 2×1 / 2×2), active viewport tracking
- `test_wizard_flow.py` — 5-page navigation, build_model integration, auto-advance to modules
- `test_parameter_help.py` — every Basic/Advanced field has a help entry

Pre-existing `test_gui.py` continua skipado (fixture issues conhecidos).

---

## 9. Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| Reescrita do main_window quebra fluxos validados (âncora interna calibration, similitude export) | Cada módulo é portado individualmente com smoke test antes de avançar. v4.0 permanece no repo BAS/ original como referência viva. |
| Auto-defaults inferem errado em casos edge | Toda inferência tem fallback explícito + tooltip "inferred from <context>"; usuário pode sempre override e fixar. |
| Basic/Advanced toggle esconde campo crítico em estudo específico | Toggle é por-sessão; usuário avançado mantém Advanced ativo. Campos críticos (preload, μ, ciclos) ficam em Basic. |
| Multi-viewport com Matplotlib pode ficar lento (>2 plots simultâneos com 10k pontos cada) | Plot downsampling no display layer (1k pontos visíveis máx, dados completos em export). Métrica de aceitação: ≤200 ms para repintar 2×2 com Job-1 padrão. |
| HHT-α menos testado que Newmark — pode ter regressão | Suite de regressão compara Newmark vs HHT em 5 casos de validation; resultados <2% divergência. |

---

## 10. Deliverable & próximos passos

Este spec encerra a fase de design. Próximo passo: invocar `writing-plans` para criar plano de implementação detalhado, baseado na ordem de §5.

O primeiro plano cobrirá: esqueleto `main_window.py` + theme.py + parameter_help.json + widgets reutilizáveis (steps 1–3 de §5). Os demais módulos virão em planos subsequentes — cada um pequeno, isolado, com checkpoint de review.
