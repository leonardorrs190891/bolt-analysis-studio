# Melhorias de layout — BAS V2 com cara de CAE profissional (estilo Abaqus)

**Data:** 2026-07-17 · **Status:** proposta para revisão do professor
**Complementa:** `2026-05-16-abaqus-frontend-design.md` (layout base) e `2026-05-16-bas-v2-frontend-design.md` (6 módulos)

Objetivo: levar o software ao aspecto de um CAE profissional (Abaqus como referência),
com uso fácil e intuitivo e interface "bonita para engenheiro". Este documento é uma
**auditoria do estado atual** (com evidência em `arquivo:linha`) + **direção visual
proposta** + **faseamento**. Nada aqui mexe na física — é só GUI.

---

## 0. Diagnóstico resumido — onde estamos hoje

Duas GUIs coexistem:

| | V1 (default, `run_app.py`) | Chrome V2 (`run_app.py --v2`) |
|---|---|---|
| Estrutura | `QTabWidget` com 7 abas numeradas + emoji (`main_window.py:5316-5322`) | Shell CAE real: ModuleBar c/ dropdown, Model Tree, viewport, inspector, prompt area (`chrome/app_window.py:61-112`) |
| Tema | Catppuccin Mocha via `theme.py` (4 paletas, QSS central de ~580 linhas) | Reusa o mesmo tema, **mas** com acentos hardcoded fora dele (`#007acc`, `#6cd486`) |
| Módulos | Todos funcionam | Model/Contacts/Loads/Results(Validation) reais; **Analysis, Jobs, Report = placeholders**; Run/Stop **desligados** (sinais nunca conectados, `module_bar.py:12-14` vs `app_window.py:133-142`) |
| Ícones | Zero `QIcon` de asset; emoji em abas, menus, toolbar, group boxes | Zero também; glifos Unicode (`▶`, `▼`, `📥`) |

O ponto importante: **não é um app "Qt cru"** — já existe um design system central e vivo
(`theme.py`: 4 paletas, re-skin ao vivo, matplotlib integrado). O aspecto "não
profissional" vem de decisões pontuais e repetidas, não de falta de estilização:

1. **Emoji como linguagem de ícones** — abas `"1. 📁 Project"…"7. 📖 Documentation"`,
   toolbar inteira (`"📄 New"`, `"▶️ Run"`…, `main_window.py:5615-5663`), títulos de
   group box (`"⚡ Quick Actions"`, `:509`), título da janela `"🔩 Bolt Analysis Studio
   v4.0"` (`:5156`), até `"🎵 Model Analysis"` para análise modal (`:1909`). Nenhum CAE
   usa emoji no chrome. É o item nº 1 que faz o app ler como "consumidor".
2. **Paleta Catppuccin** (roxo/rosa pastel de editor de código) versus a paleta
   "engineering gray + aço" que a spec §9 prescreve — e o chrome V2 hardcoda a segunda
   por fora do tema (`prompt_area.py:10`, `module_bar.py:33,53`,
   `multi_viewport.py:40-41`, `validation_browser.py:102-106`), então trocar de tema
   **não** recolore o chrome. Duas identidades visuais no mesmo binário.
3. **Inspector com abas-dentro-de-abas** (Element / Loading{Global, Per-Element} /
   Contact{Global, Per-Element}, `msd_builder.py:4996-5072`) — dois níveis de
   `QTabWidget` aninhados; Abaqus resolve isso com grupos colapsáveis filtrados por
   contexto.
4. **Zonas Abaqus faltantes no chrome**: sem message area (log rolável), sem toolbar de
   viewport, sem bloco de contexto ("Module · Model · Step"), prompt area que só ecoa
   `"Acao: <label>"` (`app_window.py:182-183`).
5. **Proporções de página de marketing**: botão RUN com 50 px de altura + font-size
   14 pt inline (`main_window.py:1367-1375`), botões do Project com 44-48 px.
6. **Inconsistências espalhadas**: ~30 `setStyleSheet` inline em `similitude_tab.py`
   (congelam cores na troca de tema — o próprio código avisa do hazard); canvases de
   resultado **sem** toolbar do matplotlib (`main_window.py:2103,2128,4296`) enquanto
   `plot_manager.py:146` tem; idioma misto PT/EN (`"🧙 Nova Análise (Wizard)"` vs
   wizard todo em inglês); backend legado `backend_qt5agg` em
   `contact_builder_dialog.py:33`.
7. **Sem ícone de aplicativo** (.ico) — janela, taskbar e Alt-Tab mostram o ícone
   genérico do Python.

---

## 1. Direção visual proposta — "bancada de engenharia"

Uma única identidade, definida em tokens no `theme.py` e consumida por V1 e chrome
(nenhum hex fora do tema). A spec §9 já aponta a direção (cinzas neutros + acento
`#007acc`); a proposta abaixo **refina** para não ficar "clone do VS Code": cinzas
levemente azulados de grafite, acento aço dessaturado, e os números — a matéria-prima
do engenheiro — sempre em monoespaçada alinhada à direita.

### 1.1 Paleta "Engineering Dark" (5ª paleta em `theme.py`, default do chrome)

| Token | Hex | Uso |
|---|---|---|
| `CRUST` | `#141518` | statusbar, message area, fundos mais profundos |
| `BASE` | `#1e2023` | fundo geral do app |
| `SURFACE0` | `#26282d` | painéis, docks, inspector |
| `SURFACE1` | `#2e3138` | toolbars, headers de grupo |
| `BORDER` | `#3c4047` | bordas 1 px (única espessura de borda) |
| `TEXT` / `SUBTEXT` / `HINT` | `#d6d8dc` / `#a4a8af` / `#7c8087` | 3 níveis, nunca mais que isso |
| `ACCENT` | `#2f8fd0` (hover `#4aa6e0`) | seleção, foco, prompt, viewport ativo — **único acento** |
| `VIEW_TOP` → `VIEW_BOT` | `#2d3640` → `#12151a` | gradiente vertical do viewport (assinatura Abaqus) |
| `PASS` / `WARN` / `FAIL` / `RUN` | `#3fae72` / `#d4a53a` / `#d05356` / `#4aa6e0` | badges, gates, estado de job |

Regras: (a) todo hex vive em `theme.py` — os hardcoded do chrome
(`prompt_area.py:10`, `module_bar.py:33,53`, `multi_viewport.py:40-41`,
`validation_browser.py:17-19,102-106`) passam a ler tokens; (b) Catppuccin, Light,
Petrobras e High-Contrast continuam como opções (o mecanismo de re-skin ao vivo já
existe, `theme.py:236-259`); (c) o chrome ganha o menu de tema que hoje só a V1 tem.

### 1.2 Tipografia

| Papel | Fonte | Regra |
|---|---|---|
| UI (labels, menus, tree) | Segoe UI 9-10 pt | nativa do Windows; sem itálico no chrome |
| **Valores numéricos** | Consolas 9 pt, **alinhados à direita** | em TODO campo, célula, tree count e statusbar — os dígitos alinham em coluna e o engenheiro compara grandezas de relance |
| Headers de grupo do inspector | Segoe UI 8 pt, weight 600, MAIÚSCULAS c/ tracking | estética de painel de instrumento |
| Fórmulas (dock F1) | Georgia serif (manter) | já é um toque distintivo bom |

### 1.3 Ícones — aposentar o emoji do chrome

O item de maior impacto isolado. Hoje: zero assets (`resources/` não existe, nenhum
`QIcon` de arquivo, nenhum `.qrc`).

- Adotar um set **SVG monocromático** permissivo (recomendo **Tabler Icons**, MIT; ou
  Lucide, ISC) + ~10 SVGs próprios para os elementos MSD (head, shank, thread, nut,
  washer, flange, gasket, ground, contact, load) redesenhando os glifos Unicode atuais
  de `ELEMENT_VISUALS` (`msd_builder.py:79-100`) como vetores.
- Loader com **recolor por tema** (SVG tingido com `Theme.TEXT`/`ACCENT` em runtime) —
  um utilitário `theme.icon("run")` de ~40 linhas resolve, sem `.qrc` compilado.
- Inventário mínimo (~40): new/open/save/save-as · undo/redo · run/stop/pause ·
  fit/zoom±/pan/print/screenshot · os 10 de elemento · contact/load/step/job/
  report/validation/wizard · expand/collapse · settings/help/formula.
- **Emoji sai de**: título da janela, abas, menus, toolbar, group boxes, tree, botões.
  Pode permanecer nos HTMLs de documentação (explorador de variáveis etc.), que são
  outro meio.
- **Ícone de aplicativo**: um parafuso vetorial simples como `.ico` multi-resolução
  (16/32/48/256) via `app.setWindowIcon` — janela, taskbar, Alt-Tab e splash.
- Nota: a spec base §9 prescreve glifos emoji na tree (📁 📦 🔗…) — **revisar a spec**
  neste ponto; foi escrita antes desta auditoria.

### 1.4 Densidade — "estação de trabalho, não dashboard"

A spec §9 já pede densidade alta; falta aplicar:

- Alturas de controle 24-26 px; linhas da tree 22 px; toolbar com ícones 16 px
  (20 px no ModuleBar); espaçamento entre propriedades 3-4 px.
- Botões gigantes normalizados: RUN de 50 px → ação de toolbar padrão + botão primário
  de 28-30 px no módulo Analysis (o destaque vem da cor `ACCENT`, não do tamanho).
- Grid de ações 2×2 do Project (44 px) → lista compacta ou cards de 32 px.

### 1.5 Assinatura visual: viewport-herói com **carimbo de desenho técnico**

Todo CAE tem uma marca no viewport (Abaqus: gradiente azul + triad + bloco "ODB:
Job-1.odb / Step: Step-1"). A assinatura proposta para o BAS — enraizada no mundo do
usuário (desenho mecânico, VDI 2230) — é um **carimbo ISO 7200 discreto** no canto
inferior direito do viewport:

```
┌ BAS V2 ─────────────────────────────┐
│ Modelo  M16_junker.msd              │
│ Módulo  Model      Step  Coupled    │
│ Job     idle       MAE   0.024 ✓    │
└─────────────────────────── 2026-07-17┘
```

- Desenhado direto na cena (`QGraphicsView.drawForeground` / overlay do matplotlib),
  fonte Consolas 8 pt, borda 1 px `BORDER`, atualiza com o estado (job rodando →
  linha `Job` em `RUN`; validação → MAE + gate).
- Combinado com o **gradiente de fundo do viewport** (`VIEW_TOP→VIEW_BOT`) — o
  `SchematicView` hoje usa fundo chapado `Theme.BASE` (`msd_builder.py:1358`); a grade
  fina existente (`:1523-1524`) fica por cima do gradiente.
- É o único lugar "ousado" do design; todo o resto permanece quieto e disciplinado.
- Bônus prático: screenshots do viewport saem **auto-documentados** para relatórios e
  papers — exatamente o que um engenheiro quer.

---

## 2. Estrutura Abaqus — completar o chrome V2

O esqueleto certo já existe. Alvo (zonas novas marcadas com `*`):

```
┌────────────────────────────────────────────────────────────────────────────┐
│ File  Edit  View  Model  Module  Tools  Help                               │
├────────────────────────────────────────────────────────────────────────────┤
│ [↶][↷] │ Module [Model ▾]  Step [Coupled ▾] │ [▶ Run][■ Stop] │ ✓ VALID.   │ ← ícones SVG
├────────────────────────────────────────────────────────────────────────────┤
│ Module: Model · Model: M16_junker · Step: Coupled-Loosening        *       │ ← bloco de contexto
├──────────────┬──────────────────────────────────────────────┬──────────────┤
│ Model Tree   │ [fit][zoom±][pan][print] *  ← toolbar viewport│ Properties   │
│ ▾ Model (1)  │                                              │ ▾ GEOMETRY   │
│  ▾ Parts (7) │        VIEWPORT                              │   d  16.0 mm │
│   Materials 2│        gradiente + grade                     │   P   2.0 mm │
│ ▾ Contacts 3 │        esquema MSD                           │ ▾ FRICTION   │
│ ▾ Loads (2)  │                                              │   µ_th 0.120 │
│ ▾ Analysis   │                    ┌ carimbo ISO 7200 ┐ *    │              │
│   Jobs (1)   │                    └──────────────────┘      │ [Basic|Adv]  │
│ ▸ Results    │                                              │              │
├──────────────┴──────────────────────────────────────────────┴──────────────┤
│ ► Selecione o flange para aplicar a carga transversal…          (prompt)   │
├────────────────────────────────────────────────────────────────────────────┤
│ Mensagens │ Log do job │ Console                                  *        │ ← message area
├────────────────────────────────────────────────────────────────────────────┤
│ Projeto: M16_junker.msd · Módulo: Model · Job: idle                  v2.0  │
└────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Terminar os módulos (pré-requisito de tudo)

É o Plano 4-6 já roteirizado no roadmap do chrome
(`2026-07-09-chrome-v2-foundation.md:1378-1389`): **Analysis + Jobs** (re-hospedar
SolverTab/SolverWorker; hoje o Run mora só na V1), **Results de Run** (extrair os 17
`_plot_*` para um `ResultsController` em grid 2×2 — o módulo Results atual é o browser
de Validation, que vira sub-modo), **Report**. Sem isso o chrome não pode virar default
e o layout Abaqus fica de fachada.

### 2.2 Zonas faltantes

- **Message area** (dock inferior colapsável, abas *Mensagens / Log do job / Console*):
  Abaqus tem message area + CLI; o BAS tem só prompt de 1 linha + statusbar. O log do
  `SolverWorker` (progresso por ciclo, warnings ISO 16130, conservação de energia) hoje
  não tem onde aparecer. Console Python = opcional/última prioridade.
- **Toolbar do viewport** (fit, zoom±, pan, screenshot, print) — o `SchematicView` já
  tem zoom 0.10-8.0× por mouse (`msd_builder.py:1373-1378`) mas sem affordance visível.
- **Bloco de contexto** sob o ModuleBar ("Module · Model · Step"), como o Abaqus.
- **Controles mortos**: Run/Stop/Step do ModuleBar não conectados e o ContextBar que só
  escreve `"Acao: <label>"` no prompt — **conectar (com Plano 4) ou ocultar até lá**.
  Botão verde que não faz nada é o oposto de "profissional".

### 2.3 Model Tree com profundidade Abaqus

Hoje a tree é rasa: 8 nós fixos + elementos sob "Model" (`model_tree.py:8-13`).
Alvo: contêineres aninhados **com contagem** ("Contacts (3)", "Jobs (1)"), menu de
contexto (Edit/Delete/Suppress), duplo-clique = editar no inspector, ícone SVG por
tipo de nó, negrito/badge `WARN` em item incompleto. A tree é a navegação primária do
Abaqus — no BAS ela ainda é um espelho passivo.

### 2.4 Um único paradigma de inspector

Hoje coexistem **dois**: o rico da V1 (abas aninhadas) nos módulos Model/Contacts/Loads
e o `ChromeInspector` (grupos colapsáveis Basic/Advanced) nos demais — a costura é
visível dentro da mesma janela. Alvo: **só grupos colapsáveis** (`CollapsibleGroup` já
existe e é o padrão Unity/Blender/spec §6), com toggle Basic|Advanced persistente, e o
conteúdo **filtrado pelo módulo + seleção** (o que hoje são as sub-abas Global/
Per-Element vira: seleção vazia → global; elemento selecionado → per-element). Os
campos Basic por módulo já estão canonizados na spec V2 §6.

### 2.5 Prompt area com instruções de verdade

O padrão Abaqus que mais ajuda iniciante. Cada ação contextual escreve a instrução do
próximo passo ("Clique em dois elementos para criar o contato…"), erros explicam o
conserto ("Toda porca precisa de um ThreadContact — selecione a porca e use *+ Contact*"),
e estado vazio orienta ("Nenhum modelo carregado — **Ctrl+Shift+N** abre o wizard").

---

## 3. Usabilidade e intuitividade

1. **Idioma único na UI** (hoje: menus EN, wizard EN, prompts do chrome PT, botão
   `"🧙 Nova Análise"` PT). Recomendação: **inglês no chrome** (convenção CAE;
   screenshots publicáveis em paper) com help/tooltips bilíngues — mas é decisão do
   professor (§6).
2. **Wizard-first + auto-defaults** (Plano 7 da spec): `AutoComboBox` está construído e
   testado mas **não ligado a nenhum módulo**; o wizard não auto-avança os módulos após
   criar. Ligar os dois é o maior ganho de "fácil e intuitivo" por linha de código.
3. **Unidades sempre visíveis**: sufixo de unidade em todo campo numérico (`16.0 mm`,
   `50 kN`, `0.5 Hz`), cinza `HINT`, respeitando o toggle SI/IMP existente.
4. **Plots com interação de engenheiro**: toolbar do matplotlib em TODOS os canvases
   (faltam em `main_window.py:2103,2128,4296`); **readout de cursor** (x/y em unidades
   na barra do viewport); sombreamento dos estágios I/II/III na curva de preload;
   export CSV/PNG por plot. rcParams unificados via `Theme.get_plot_style()` (já
   existe, `theme.py:901-926`) — só padronizar grid fino alpha 0.25 + minor ticks.
5. **Erros e vazios com direção, não humor**: toda mensagem diz o que aconteceu e qual
   o próximo clique (já temos bons exemplos nos gates de validação; generalizar).
6. **Atalhos**: Ctrl+Shift+N wizard (spec), F1 fórmulas (existe), `F` = fit view,
   Ctrl+1..6 = trocar módulo, Ctrl+R = run. Documentar no menu Help.
7. **Verbos consistentes**: o botão que diz *Run* gera status *Running* e log
   *Run completed* — mesma palavra em todo o fluxo (hoje: Run/Solve/Análise misturam).

---

## 4. Quick wins na V1 (enquanto o chrome não é default)

A V1 continua sendo o que o usuário vê. Custo ~1 dia, impacto imediato:

| Item | Onde |
|---|---|
| Abas sem número e sem emoji (`"Project"`, `"Model Builder"`, …) | `main_window.py:5316-5322` |
| Título da janela sem emoji + `.ico` de app | `main_window.py:5156` |
| Toolbar com ícones SVG (ou, interinamente, só texto) | `main_window.py:5615-5663` |
| Group boxes sem emoji nos títulos | `main_window.py:377,425,509,630…` |
| `"🎵 Model Analysis"` → `"Modal Analysis"` (ícone certo) | `main_window.py:1909` |
| RUN 50 px → botão primário normal | `main_window.py:1367-1375` |
| Toolbar matplotlib nos 3 canvases órfãos | `main_window.py:2103,2128,4296` |
| `backend_qt5agg` → `backend_qtagg` | `contact_builder_dialog.py:33` |
| Migrar `setStyleSheet` inline p/ QSS+objectName (não congela tema) | `similitude_tab.py:100-943`, `msd_builder.py:4958` |
| Restyle do splash na paleta nova + versão "V2" | `run_app.py` (AnimatedSplashScreen) |

---

## 5. Faseamento sugerido

| Fase | Conteúdo | Esforço | Impacto visual |
|---|---|---|---|
| **0. Quick wins V1** | tabela do §4 | ~1 dia | alto (de-emoji é metade da percepção) |
| **1. Tokens** | paleta Engineering Dark no `theme.py`; rotear hexes do chrome via tema; tipografia numérica mono à direita; densidade QSS; menu de tema no chrome | 1-2 dias | alto |
| **2. Ícones** | set SVG + loader com recolor + aplicar em ModuleBar/ContextBar/Tree/menus/abas V1; `.ico` do app | 2-3 dias | **muito alto** |
| **3. Zonas Abaqus** | message area, toolbar de viewport, bloco de contexto, gradiente + **carimbo ISO 7200**, prompt com instruções, ocultar controles mortos | 2-4 dias | alto |
| **4. Módulos (Planos 4-6)** | Analysis+Jobs, Results de Run 2×2, Report | maior (já roteirizado) | estrutural |
| **5. Consolidação (Planos 7-8)** | AutoComboBox + wizard auto-advance; tree profunda; inspector único; integradores 5→2; **chrome vira default**, abas V1 aposentadas | médio | estrutural |
| **6. Polimento** | readout de cursor, sombreamento de estágios, empty states, atalhos, idioma único | contínuo | médio |

Fases 0-3 são independentes dos Planos 4-6 e podem andar antes/em paralelo — o app
melhora de aparência **sem esperar** a migração funcional. Sugestão de captura de
baseline: criar `docs/ui/` com screenshots antes/depois por fase (hoje o repo não tem
**nenhuma** imagem da UI — útil também para o manual).

---

## 6. Decisões em aberto (professor)

1. **Paleta default**: Engineering Dark proposta (§1.1) vs manter Catppuccin. Proposta:
   Engineering como default do chrome; Catppuccin permanece opcional.
2. **Idioma da UI**: inglês (convenção CAE / papers) vs português (laboratório).
   Tooltips/help podem ser bilíngues em qualquer cenário.
3. **Fonte dos ícones**: Tabler (MIT) / Lucide (ISC) / desenhar set próprio. Proposta:
   Tabler + ~10 SVGs próprios para elementos MSD.
4. **Console Python** na message area: fazer (paridade Abaqus, scriptabilidade) ou
   adiar indefinidamente. Proposta: adiar; só *Mensagens* + *Log do job* já cobrem 95%.
5. **Quando aposentar a V1** (Plano 8): critério sugerido = chrome com Analysis+Results
   +Report reais e 2 semanas de uso sem regressão.
6. **Revisão da spec base §9** (emoji na tree): atualizar a spec para ícones SVG.

---

## Apêndice A — referências de arquivo

| Assunto | Referência |
|---|---|
| Design system central (paletas, QSS, plot style, re-skin) | `src/bolt_analysis_studio/gui/theme.py:29-135,236-259,276-862,901-926` |
| Abas 7× numeradas+emoji · título janela · toolbar emoji | `gui/main_window.py:5316-5322,5156,5615-5663` |
| Sub-abas Results emoji · RUN 50 px · canvases sem toolbar | `gui/main_window.py:1837-2138,1367-1375,2103,2128,4296` |
| Inspector abas-dentro-de-abas | `gui/msd_builder.py:4996-5072` |
| Glifos de elemento (base p/ ícones SVG próprios) | `gui/msd_builder.py:79-100` |
| SchematicView (fundo, grade, zoom — receberá gradiente+carimbo) | `gui/msd_builder.py:1311,1358,1373-1378,1523-1524` |
| Chrome shell · switch de módulo · prompt stub | `gui/chrome/app_window.py:61-112,149-179,182-183` |
| Hexes hardcoded fora do tema | `gui/chrome/widgets/prompt_area.py:10`, `module_bar.py:33,53`, `multi_viewport.py:40-41`, `validation_browser.py:17-19,102-106` |
| Run/Stop/Step nunca conectados | `gui/chrome/widgets/module_bar.py:12-14` vs `app_window.py:133-142` |
| Tree rasa | `gui/chrome/widgets/model_tree.py:8-13` |
| AutoComboBox pronto e não usado | `gui/chrome/widgets/auto_combo.py` |
| Roadmap Planos 4-8 | `docs/superpowers/plans/2026-07-09-chrome-v2-foundation.md:1378-1389` + STATUS dos planos 1-3/B |
| Linguagem visual prescrita (cinzas, #007acc, densidade, mono p/ números) | `docs/superpowers/specs/2026-05-16-abaqus-frontend-design.md` §9 |
| Campos Basic/Advanced canônicos por módulo | `docs/superpowers/specs/2026-05-16-bas-v2-frontend-design.md` §6 |
| Inline styles a migrar | `gui/similitude_tab.py:100-943`, `gui/msd_builder.py:4958` |
| Backend matplotlib legado | `gui/contact_builder_dialog.py:33` |
