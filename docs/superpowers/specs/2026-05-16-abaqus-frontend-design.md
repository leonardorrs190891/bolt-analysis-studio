# Design — Frontend BAS no estilo Abaqus/CAE

**Data:** 2026-05-16
**Autor:** Prof. Leonardo Rosa Ribeiro da Silva (brainstorm)
**Status:** Design conceitual. Sem implementação — pensar a forma do frontend, não construir.
**Escopo:** Reimaginar a camada `gui/` do BAS v4.0. Não toca `core/`, `numerical/`, formato `.msd`.

---

## 1. Visão

BAS Studio reorganizado como aplicação CAE-style de janela única, inspirada no Abaqus/CAE. Substitui as 7 abas do app atual por:

- **Module dropdown** no topo controlando o modo de trabalho (máquina de estados explícita).
- **Model Tree** à esquerda como fonte de verdade da navegação.
- **Multi-viewport** central, divisível em até 4 painéis.
- **Property Inspector** contextual à direita.
- **Prompt area** + **status bar** embaixo.

Linguagem visual: **dark engineering moderno** — fundo `#1e1e1e`, painéis `#252526–#2d2d30`, accent `#007acc`, accents semânticos verde/amarelo/vermelho para validação e severidade.

A reorganização é puramente da camada GUI. Toda a física, persistência e numérica continua intocada.

---

## 2. Módulos

Sete módulos, na ordem do workflow:

| # | Módulo | Substitui (atual) | Conteúdo principal |
|---|--------|-------------------|---------------------|
| 1 | **Model** | Aba Model Builder (estrutura) | Elements (HEAD, SHANK, THREAD, NUT, WASHER, FLANGE, GASKET), Materials, Assembly, Locking Device |
| 2 | **Contacts** | Aba Model Builder (tribologia) | Thread / Bearing / Flange-Flange / Gasket / Generic contacts, friction & wear models |
| 3 | **Loads** | Aba Model Builder (loading) | Global loading, per-element loads, VDI 2230, thermal |
| 4 | **Analysis** | Aba Solver | Steps (Static-Preload, Coupled-Loosening), solver method, dt, n_cycles, tolerances |
| 5 | **Results** | Aba Results + parte de Validation | Multi-viewport com plots (preload, friction, phase, Miner, wear, rotation), overlay de reference |
| 6 | **Similitude** | Aba Similitude | Multi-bolt reduction + geometric scaling |
| 7 | **Report** | Aba Reports | Geração PDF / HTML / CSV |

A aba **Documentation** é removida; conteúdo migra para o menu **Help → User Guide** inalterado.

Validation aparece como **nó dedicado da Tree** (ao lado de Similitude) com sub-nós Reference Curves / Calibration Papers / Validation Cases, e também como **overlay dentro do módulo Results** (chip "Overlay: âncora interna-13A" na context bar). Duas portas de entrada para o mesmo dado.

---

## 3. Chrome (layout fixo)

De cima para baixo:

1. **Menubar** — `File · Edit · View · Model · Module · Tools · Plug-ins · Help`.
2. **Module bar** — botões de arquivo, undo/redo, separador, `Module: [▼]`, `Step: [▼]`, separador, `▶ Run` (verde) / `⏹ Stop`, badges contextuais (ex: `VALIDATION · PASS`).
3. **Context bar** — muda completamente conforme módulo ativo (em Loads: `+ Global Load / + Per-Element / + Thermal / + Locking`; em Results: chips de plot-type + Layout/Overlay/Export).
4. **Body grid** — 3 colunas:
   - **Model Tree** (220 px, esquerda)
   - **Multi-viewport** (flex, centro)
   - **Property Inspector** (260–280 px, direita)
5. **Prompt area** — banner azul (`#007acc`) com instrução contextual à esquerda e coordenadas/cursor à direita. Honra o Abaqus.
6. **Status bar** — `#181818`, mostra projeto · módulo · step · job status · memória · versão.

---

## 4. Model Tree

Hierarquia única, presente em todos os módulos:

```
📁 Project "<nome>.msd"
├── 📦 Model
│   ├── Elements            (HEAD, SHANK, THREAD, NUT, WASHER, FLANGE, GASKET)
│   ├── Materials           (Steel 10.9, A320 L7, ...)
│   ├── Assembly            (ordem série/paralelo, conexões)
│   └── Locking Device
├── 🔗 Contacts
│   ├── Thread Contacts
│   ├── Bearing Contacts    (head, nut)
│   ├── Flange-Flange / Flange-Gasket
│   └── Friction & Wear models
├── ⬇️ Loads
│   ├── Global              (preload, F_trans, freq, ciclos, ΔT)
│   └── Per-Element         (forças/constraints específicas)
├── ▶️ Analysis Steps
│   ├── Static-Preload
│   └── Coupled-Loosening   (n_cycles, dt, solver method)
├── 🧪 Jobs
│   └── Job-N               (queued / running / done)
├── 📊 Results
│   └── Job-N
│       ├── Preload Decay · Friction μ · Wear · Phase Map · Miner's D · Rotation
├── ✅ Validation
│   ├── Reference Curves    (âncora interna 5A, 13A, ...)
│   ├── Calibration Papers  (Lu 2024, Jiang 2003, ...)
│   └── Validation Cases    (entradas de validation_cases.py)
├── 📐 Similitude Studies
│   ├── Multi-Bolt Reduction
│   └── Geometric Scaling (1:N)
└── 📄 Reports
```

A Tree é a fonte de verdade da navegação:
- Clicar num nó muda o módulo ativo (se necessário), seleciona o item no Inspector, e realça no viewport.
- O **Module dropdown** é um atalho/breadcrumb da Tree — não é o estado primário.

---

## 5. Multi-viewport

Layouts suportados: `1 / 1×2 / 2×1 / 2×2` (botão "Layout" na context bar — não é divisão livre tipo Abaqus avançado puro, mas cobre todos os casos práticos).

Cada sub-viewport mostra o conteúdo apropriado ao **módulo ativo**:

| Módulo | Viewport content | Layout default |
|--------|-----------------|----------------|
| Model | MSD schematic 2D editável (drag-drop) | 1 |
| Contacts | MSD com interfaces destacadas (clicáveis) | 1 |
| Loads | MSD com setas/símbolos de carga sobrepostos | 1 |
| Analysis | Timeline visual dos steps + (quando Jobs selecionado na Tree) solver log + barra de progresso + live preload preview | 1 ou 1×2 |
| Results | Plots matplotlib trocando por chip + (quando Validation selecionado na Tree) comparison plot com overlay de reference | 2×2 (preload / μ / phase / Miner) |
| Similitude | Scaling chart | 1 |
| Report | Live preview do relatório | 1 |

Os nós **🧪 Jobs** e **✅ Validation** da Tree não são módulos próprios — são state/output que vive sob os módulos Analysis e Results respectivamente. Clicar em Jobs alterna o viewport do módulo Analysis para o modo monitor (log + progress + preview). Clicar em Validation alterna o viewport do módulo Results para o modo comparison (overlay + MAE/RMSE).

Viewport ativo recebe outline azul (`#007acc`) e o Inspector reflete suas propriedades. Toolbar do viewport tem split / camera / fullscreen.

---

## 6. Property Inspector

Estrutura permanente: **grupos colapsáveis** com cabeçalho `▼ Group Name` (estilo Unity/Blender), em vez de dialogs modais "Edit Load…" como no Abaqus puro. Reduz fricção para edição rápida e mantém parâmetros visíveis.

Exemplo (módulo Loads, nó "Global" selecionado):

```
Properties — Global Load
▼ Global Loading
  Load type        [TRANSVERSE ▼]
  Preload F₀       [50.0 kN]
  % Yield          [70 %]
  Δ amplitude      [0.65 mm]
  Frequency        [12.5 Hz]
  N cycles         [2 000]
▼ Locking Device
  Type             [Free Running Nut ▼]
  Junker class     [F]
  Slip-onset       [0.46]
▼ VDI 2230
  R-factor         [−1.0]
  Dyn. factor      [1.0]
  Waveform         [sinusoidal ▼]
```

Em Results, o Inspector mostra plot config + statistics + validation verdict (MAE / RMSE / PASS-FAIL com cor semântica).

---

## 7. Signal flow conceitual

Mantém o padrão signal-based atual do BAS (`model_changed`, `loading_changed`, `similitude_changed` etc.). O que muda:

1. **Seleção na Tree** → emite signal → atualiza módulo ativo (se diferente) + carrega item no Inspector + realça no viewport.
2. **Edição no Inspector** → propaga pro estado do projeto (`AppState`) → invalida o(s) viewport(s) correspondentes → re-renderiza.
3. **Mudança de módulo** (via dropdown ou Tree) → context bar muda widget set → viewport(s) trocam conteúdo, mas Tree e seleção corrente persistem.
4. **Multi-viewport sync** → uma única seleção (cycle hover, element pick) é compartilhada entre todos os sub-viewports do mesmo módulo (ex: hover em N=412 no plot de preload destaca N=412 no phase map).

As 3 zonas (Tree / Viewport / Inspector) são sempre visíveis e cooperam — antes viviam em abas separadas.

---

## 8. Onde o paradigma diverge do Abaqus puro

- **Sem Mesh** — geometria BAS é 1D MSD, dataclass. Módulo Mesh some.
- **Similitude e Validation são módulos** — Abaqus não tem equivalentes. Entram como cidadãos de primeira classe.
- **Multi-viewport com layouts fixos** (1 / 1×2 / 2×1 / 2×2) em vez de divisão livre. Cobre os casos práticos sem complexidade extra.
- **Inspector com grupos colapsáveis**, não dialogs modais. Reduz cliques.
- **Validation tem dupla entrada** (módulo dedicado + overlay em Results) — reflete que validação é o foco atual do projeto, não um afterthought.

---

## 9. Linguagem visual (dark engineering moderno)

**Cores base:**
- App background `#1e1e1e`
- Panel background `#252526`
- Toolbar `#2d2d30`
- Borders `#3e3e42`
- Text primary `#d4d4d4`, secondary `#b0b0b0`, hint `#9e9e9e`, label `#888`
- Accent (selection / active) `#007acc`
- Active row in Tree `#094771`

**Accents semânticos:**
- Success / PASS — `#0e7c3a` (badge) / `#6cd486` (text) / `#2d8f3f` (sw)
- Warning — `#d4b13a`
- Danger / RUNAWAY — `#c44`
- Stage colors (phase map): Stable `#2d8f3f` · Non-rot `#4a90e2` · Transit `#d4b13a` · Rotational `#e08c5a` · Runaway `#c44` · Axial-I `#4ac0c0` · Axial-II `#a878c0` · Axial-III `#c44`

**Tipografia:**
- UI: Inter / Segoe UI, 11 px base
- Valores numéricos: JetBrains Mono / Consolas, 10 px (alinhados à direita)

**Densidade:** alta — 3 px vertical entre props no Inspector, 2 px entre rows da Tree, 5 px gap entre botões na context bar. Estação de trabalho, não dashboard.

---

## 10. Fora de escopo

- **Sem mudanças** em `core/` (models, contacts, similitude, validation_cases, project_io, app_state, workflow).
- **Sem mudanças** em `numerical/` (time_integration, coupled_loosening_analyzer, wear_models, preload_loss_models, friction_models, parameter_identifier, sun_curve, miners_rule).
- **Sem mudanças** em `visualization/` — os plotters Matplotlib são reutilizados, só mudam de container Qt.
- **Sem mudanças** no formato `.msd` ou no schema de `MSDModel.to_dict()`.
- Aba **Documentation** vira menu Help → User Guide com o mesmo conteúdo.

A reorganização é estritamente de `gui/`: substituir o `QTabWidget` raiz por um `QMainWindow` com `QToolBar` (module/context), `QDockWidget` (tree, inspector), `QSplitter` (multi-viewport) e os widgets existentes reagrupados.

---

## 11. Deliverable deste design

Este documento + dois mockups HTML salvos em `.superpowers/brainstorm/1366-1778936971/content/`:
- `main-layout.html` — chrome completo com módulo Loads ativo, viewport dividido em 2.
- `module-results.html` — módulo Results com grid 2×2, validation PASS badge.

Não há implementação prevista nesta sessão (`sem modificar o software`). Próximos passos viáveis quando/se o usuário decidir implementar:

1. Prototipar o chrome (`QMainWindow` + `QToolBar` module bar + `QDockWidget` tree/inspector) num arquivo isolado, sem tocar o resto.
2. Implementar um único módulo (Model) end-to-end, reusando os widgets existentes do MSD Builder dentro do novo container.
3. Migrar módulo por módulo, mantendo as 7 abas como fallback durante a transição.
