# GUI Layout → CAE profissional (estilo Abaqus) — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Levar o BAS V2 ao aspecto de um CAE profissional (Abaqus como referência) — de-emoji, paleta "engineering", ícones vetoriais, zonas Abaqus completas no chrome, módulos funcionais e polimento — sem tocar na física.

**Architecture:** Todo hex vive em `gui/theme.py` (design system central, já com re-skin ao vivo); o chrome V2 (`gui/chrome/`) usa o padrão **controller-embrulha-V1** já provado (`ModelController`/`ValidationController`) para re-hospedar as peças da V1 em docks Abaqus. Fases 0–3 são puramente visuais e independentes dos módulos funcionais (4–6) — podem rodar antes ou em paralelo.

**Tech Stack:** Python 3.10+, PyQt6 (QtWidgets, QtGui, QtSvg), matplotlib (backend_qtagg), pytest (headless via `tests/conftest.py`).

## Global Constraints

- **Encoding:** todo I/O de arquivo em `encoding='utf-8'` (Windows charmap quebra acentos). Docs/textos ao usuário em **pt-BR com acentos** — nunca remover acentos "por segurança de encoding".
- **Syntax-check obrigatório após cada edição:** `python -c "import ast; ast.parse(open('PATH', encoding='utf-8').read()); print('OK')"`.
- **Testes rodam headless:** `tests/conftest.py` já põe `src/` no `sys.path` e seta `QT_QPA_PLATFORM=offscreen`. Testes de widget pedem a fixture `qapp`. Comando padrão: `python -m pytest tests/test_ARQUIVO.py -v`.
- **Sem editable install neste ambiente** — dependa do `conftest.py`, nunca de `pip install -e`.
- **Nenhum hex fora do `theme.py`:** cores só via `Theme.*` ou via `objectName` + regra no `get_stylesheet()`. `setStyleSheet` inline por-widget **congela** a cor na troca de tema — proibido para cores temáticas (o próprio código já avisa disso).
- **`similitude_tab.py` NÃO importa `QSizePolicy`** — usar `setMinimumWidth()` etc.
- **Commits frequentes**, um por task. Mensagem em pt-BR, terminando com a linha `Co-Authored-By`.
- **Não reverter defaults físicos** de `JointMaterial` — este plano não toca em `numerical/`, `core/models`, nem calibração.
- **V1 permanece fallback** até a Fase 5 explicitamente promover o chrome a default.

---

## File Structure

**Criados:**
- `src/bolt_analysis_studio/gui/icons.py` — loader de ícones SVG com recolor por tema (Fase 2).
- `src/bolt_analysis_studio/resources/icons/*.svg` — set de ícones monocromáticos (Fase 2).
- `src/bolt_analysis_studio/resources/app_icon.svg` — ícone do aplicativo (Fase 2).
- `src/bolt_analysis_studio/gui/chrome/widgets/message_area.py` — `MessageArea` (Fase 3).
- `src/bolt_analysis_studio/gui/chrome/widgets/viewport_toolbar.py` — `ViewportToolbar` (Fase 3).
- `src/bolt_analysis_studio/gui/chrome/widgets/context_block.py` — `ContextBlock` (Fase 3).
- `src/bolt_analysis_studio/gui/chrome/controllers/analysis_controller.py` — `AnalysisController` (Fase 4).
- `src/bolt_analysis_studio/gui/chrome/controllers/results_controller.py` — `ResultsController` (Fase 4).
- `src/bolt_analysis_studio/gui/chrome/controllers/report_controller.py` — `ReportController` (Fase 4).
- `tests/test_gui_theme_engineering.py`, `tests/test_gui_icons.py`, `tests/test_chrome_message_area.py`, `tests/test_chrome_viewport_chrome.py`, `tests/test_chrome_analysis_module.py`, `tests/test_chrome_results_module.py`, `tests/test_chrome_report_module.py`, `tests/test_chrome_deep_tree.py`, `tests/test_gui_integrators.py`.

**Modificados (âncoras de linha do estado 2026-07-17):**
- `gui/theme.py` — nova paleta `THEME_ENGINEERING`; regras QSS novas em `get_stylesheet()`.
- `gui/main_window.py` — abas `:5316-5322`, toolbar `:5615-5663`, RUN `:1367-1375`, canvases órfãos `:2103,2128`, group boxes; integradores `:1101-1106,3235`.
- `gui/msd_builder.py` — `SchematicView` `:1311+` (gradiente + stamp), `ELEMENT_VISUALS` `:79-100`.
- `gui/chrome/widgets/{prompt_area,module_bar,multi_viewport}.py` — hexes → objectName+QSS.
- `gui/chrome/app_window.py` — novas docks/zonas, wiring de Run/Stop, deep-tree, atalhos.
- `gui/chrome/widgets/model_tree.py` — árvore profunda com contagens.
- `run_app.py` — default do chrome + `--theme engineering` + (Fase 5) promoção a default.
- `gui/contact_builder_dialog.py:33` — `backend_qt5agg` → `backend_qtagg`.
- `gui/splash.py` — restyle na paleta nova.

---

# FASE 0 — Quick wins na V1 (de-emoji + limpeza)

Objetivo: metade da percepção "não profissional" some ao remover emoji e normalizar botões, na GUI que o usuário realmente vê hoje. Independente de tudo o mais.

### Task 0.1: Abas e título da janela sem emoji/numeração

**Files:**
- Modify: `src/bolt_analysis_studio/gui/main_window.py:5156` (título), `:5316-5322` (abas)
- Test: `tests/test_gui_v1_chrome.py` (criar)

**Interfaces:**
- Produces: nada consumido por outras tasks; verifica só rótulos de aba.

- [ ] **Step 1: Escrever o teste que falha**

```python
# tests/test_gui_v1_chrome.py
"""Fase 0: chrome da V1 sem emoji e sem numeração nas abas."""
import re

def test_tab_titles_have_no_emoji_or_numbering(qapp):
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    win = BoltAnalysisStudio()
    try:
        titles = [win.tab_widget.tabText(i) for i in range(win.tab_widget.count())]
    finally:
        win.close()
    assert titles[:4] == ["Project", "Model Builder", "Solver", "Results"]
    emoji = re.compile(r"[\U0001F000-\U0001FAFF☀-➿]")
    for t in titles:
        assert not emoji.search(t), f"emoji em aba: {t!r}"
        assert not re.match(r"^\d+\.\s", t), f"numeração em aba: {t!r}"

def test_window_title_has_no_emoji(qapp):
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    win = BoltAnalysisStudio()
    try:
        assert "🔩" not in win.windowTitle()
        assert "Bolt Analysis Studio" in win.windowTitle()
    finally:
        win.close()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_gui_v1_chrome.py -v`
Expected: FAIL (títulos ainda têm `"1. 📁 Project"` etc.).

- [ ] **Step 3: Implementar — remover emoji/numeração**

Em `main_window.py:5316-5322`, trocar as 7 linhas `addTab` por:

```python
        self.tab_widget.addTab(self.project_tab, "Project")
        self.tab_widget.addTab(self.model_builder_tab, "Model Builder")
        self.tab_widget.addTab(self.solver_tab, "Solver")
        self.tab_widget.addTab(self.results_tab, "Results")
        self.tab_widget.addTab(self.similitude_tab, "Similitude")
        self.tab_widget.addTab(self.reports_tab, "Reports")
        self.tab_widget.addTab(self.documentation_tab, "Documentation")
```

Em `main_window.py:5156`, trocar o `setWindowTitle`:

```python
        self.setWindowTitle("Bolt Analysis Studio V2")
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_gui_v1_chrome.py -v` → PASS
Depois: `python -c "import ast; ast.parse(open('src/bolt_analysis_studio/gui/main_window.py', encoding='utf-8').read()); print('OK')"`

- [ ] **Step 5: Commit**

```bash
git add tests/test_gui_v1_chrome.py src/bolt_analysis_studio/gui/main_window.py
git commit -m "$(cat <<'EOF'
feat(gui): abas e titulo da V1 sem emoji/numeracao (Fase 0.1)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 0.2: Toolbar e títulos de group box sem emoji; sub-abas de Results

**Files:**
- Modify: `src/bolt_analysis_studio/gui/main_window.py:5615-5663` (toolbar), `:1909` (`🎵 Model Analysis`), `:2111` (`⚙️ Miner's Rule`), `:2138` (`🧭 Diagnostics`), `:1879` (`📋 Summary`), `:2031` (`📊 Plot View`), e os títulos de `QGroupBox` com emoji (`:377,425,509,630`)
- Test: `tests/test_gui_v1_chrome.py` (estender)

- [ ] **Step 1: Estender o teste**

```python
def test_toolbar_actions_have_no_emoji(qapp):
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    import re
    emoji = re.compile(r"[\U0001F000-\U0001FAFF☀-➿️]")
    win = BoltAnalysisStudio()
    try:
        for tb in win.findChildren(type(win.findChild(__import__('PyQt6.QtWidgets', fromlist=['QToolBar']).QToolBar))):
            for act in tb.actions():
                assert not emoji.search(act.text() or ""), f"emoji na toolbar: {act.text()!r}"
    finally:
        win.close()

def test_results_subtabs_have_no_emoji(qapp):
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    import re
    emoji = re.compile(r"[\U0001F000-\U0001FAFF☀-➿️]")
    win = BoltAnalysisStudio()
    try:
        rt = win.results_tab.right_tabs
        for i in range(rt.count()):
            assert not emoji.search(rt.tabText(i)), f"emoji sub-aba: {rt.tabText(i)!r}"
    finally:
        win.close()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_gui_v1_chrome.py -k "toolbar or subtabs" -v` → FAIL

- [ ] **Step 3: Implementar**

Toolbar (`:5622-5662`): remover o emoji + espaço de cada `QAction(...)` — `"📄 New"`→`"New"`, `"📂 Open"`→`"Open"`, `"💾 Save"`→`"Save"`, `"🔧 MSD Builder"`→`"MSD Builder"`, `"▶️ Run"`→`"Run"`, `"⏹️ Stop"`→`"Stop"`, `"📊 Plots"`→`"Plots"`, `"⚖️ Similitude"`→`"Similitude"`, `"📋 Report"`→`"Report"`.

Sub-abas de Results: `:1879` `"📋 Summary"`→`"Summary"`; `:1909` `"🎵 Model Analysis"`→`"Modal Analysis"`; `:2031` `"📊 Plot View"`→`"Plot View"`; `:2111` `"⚙️ Miner's Rule"`→`"Miner's Rule"`; `:2138` `"🧭 Diagnostics"`→`"Diagnostics"`.

Group boxes com emoji no título: buscar e limpar — `python -c "..."` não; usar Grep manual e trocar `QGroupBox("⚡ Quick Actions")`→`QGroupBox("Quick Actions")`, `"📁 Project Information"`→`"Project Information"`, `"📋 Standards & Codes"`→`"Standards & Codes"`, `"📊 Model Summary"`→`"Model Summary"`, `"📋 Summary Statistics"`→`"Summary Statistics"`. (Rodar `Grep "QGroupBox\(\"[^\"]*[\\x{1F000}-\\x{1FAFF}]"` para achar todos.)

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_gui_v1_chrome.py -v` → PASS
`python -c "import ast; ast.parse(open('src/bolt_analysis_studio/gui/main_window.py', encoding='utf-8').read()); print('OK')"`

- [ ] **Step 5: Commit**

```bash
git add tests/test_gui_v1_chrome.py src/bolt_analysis_studio/gui/main_window.py
git commit -m "$(cat <<'EOF'
feat(gui): toolbar/group-boxes/sub-abas da V1 sem emoji (Fase 0.2)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 0.3: Botão RUN normalizado + toolbars matplotlib nos canvases órfãos + backend alias

**Files:**
- Modify: `main_window.py:1367-1375` (RUN 50px), `:2103` (miners canvas), `:2131` (adv canvas), `gui/contact_builder_dialog.py:33` (backend)
- Test: `tests/test_gui_v1_chrome.py` (estender)

- [ ] **Step 1: Estender o teste**

```python
def test_run_button_is_not_oversized(qapp):
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    win = BoltAnalysisStudio()
    try:
        # RUN normalizado: usa a altura de botão primário do tema, não 50px inline
        assert win.solver_tab.run_btn.minimumHeight() <= 36
        assert "14pt" not in (win.solver_tab.run_btn.styleSheet() or "")
    finally:
        win.close()

def test_contact_dialog_uses_modern_backend():
    import bolt_analysis_studio.gui.contact_builder_dialog as m
    src = open(m.__file__, encoding="utf-8").read()
    assert "backend_qt5agg" not in src
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_gui_v1_chrome.py -k "run_button or backend" -v` → FAIL

- [ ] **Step 3: Implementar**

`main_window.py:1367-1375` — normalizar o RUN (mantém `objectName("success")`, remove o inline de 14pt e o height 50):

```python
        self.run_btn = QPushButton("Run Analysis")
        self.run_btn.setObjectName("success")
        self.run_btn.setMinimumHeight(Theme.BUTTON_MIN_HEIGHT_PRIMARY)
```

Canvases órfãos — dar toolbar do matplotlib. Após criar `self.miners_canvas_widget` (`:2103`), adicionar antes do `miners_layout.addWidget(self.miners_canvas_widget, ...)`:

```python
            from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
            miners_layout.addWidget(NavigationToolbar2QT(self.miners_canvas_widget, miners_tab))
```

E analogamente para `self.adv_canvas_widget` (`:2131`), antes do `adv_layout.addWidget(self.adv_canvas_widget, ...)`:

```python
            from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as _NT
            adv_layout.addWidget(_NT(self.adv_canvas_widget, adv_tab))
```

`contact_builder_dialog.py:33` — trocar `from matplotlib.backends.backend_qt5agg import ...` por `from matplotlib.backends.backend_qtagg import ...`.

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_gui_v1_chrome.py -v` → PASS
`python -c "import ast; ast.parse(open('src/bolt_analysis_studio/gui/main_window.py', encoding='utf-8').read()); print('OK')"`

- [ ] **Step 5: Commit**

```bash
git add tests/test_gui_v1_chrome.py src/bolt_analysis_studio/gui/main_window.py src/bolt_analysis_studio/gui/contact_builder_dialog.py
git commit -m "$(cat <<'EOF'
feat(gui): RUN normalizado + toolbars matplotlib + backend qtagg (Fase 0.3)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# FASE 1 — Tokens: paleta "Engineering Dark" + fim dos hexes soltos

### Task 1.1: Adicionar a paleta `THEME_ENGINEERING`

**Files:**
- Modify: `gui/theme.py:120-135` (dict `PALETTES`/`PALETTE_NAMES`), inserir `THEME_ENGINEERING` após `THEME_HIGH_CONTRAST` (`:120`)
- Test: `tests/test_gui_theme_engineering.py` (criar)

**Interfaces:**
- Produces: `PALETTES["engineering"]` com as 20 chaves canônicas; `Theme.set_theme("engineering")` funcional.

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_gui_theme_engineering.py
"""Fase 1: paleta Engineering Dark registrada e com contraste AA no corpo."""
import pytest
from bolt_analysis_studio.gui.theme import Theme, PALETTES, THEME_DARK

def _lum(hexcol):
    hexcol = hexcol.lstrip("#")
    r, g, b = (int(hexcol[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    R, G, B = f(r), f(g), f(b)
    return 0.2126*R + 0.7152*G + 0.0722*B

def _ratio(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

def test_engineering_palette_registered():
    assert "engineering" in PALETTES
    pal = PALETTES["engineering"]
    assert set(pal.keys()) == set(THEME_DARK.keys())  # mesmas 20 chaves canônicas

def test_engineering_body_text_contrast_AA():
    pal = PALETTES["engineering"]
    assert _ratio(pal["TEXT"], pal["BASE"]) >= 7.0        # AA/AAA corpo
    assert _ratio(pal["SUBTEXT"], pal["BASE"]) >= 4.5     # AA texto secundário

def test_engineering_accent_is_steel_blue():
    assert PALETTES["engineering"]["BLUE"].lower() == "#2f8fd0"

def test_set_theme_engineering_applies():
    try:
        Theme.set_theme("engineering")
        assert Theme.BASE == "#1e2023"
        assert Theme.is_dark() is True
    finally:
        Theme.set_theme("dark")
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_gui_theme_engineering.py -v` → FAIL (`"engineering" not in PALETTES`).

- [ ] **Step 3: Implementar a paleta**

Em `theme.py`, após o dict `THEME_HIGH_CONTRAST` (termina em `:120`) e antes de `PALETTES = {...}` (`:122`), inserir:

```python
THEME_ENGINEERING = {
    # "Engineering Dark" — grafite azulado + acento aço dessaturado.
    # Mapeia os tokens da spec 2026-07-17 §1.1 nas 20 chaves canônicas.
    "BASE": "#1e2023",
    "MANTLE": "#191b1e",
    "CRUST": "#141518",
    "SURFACE0": "#26282d",
    "SURFACE1": "#2e3138",
    "SURFACE2": "#3c4047",
    "TEXT": "#d6d8dc",
    "SUBTEXT": "#a4a8af",
    "OVERLAY": "#7c8087",
    "BLUE": "#2f8fd0",       # ACENTO (seleção, foco, prompt, viewport ativo)
    "GREEN": "#3fae72",      # PASS
    "RED": "#d05356",        # FAIL / RUNAWAY
    "PEACH": "#d98a4a",
    "YELLOW": "#d4a53a",     # WARN
    "MAUVE": "#8a7fd0",
    "TEAL": "#3fae9e",
    "PINK": "#c77faa",
    "SKY": "#4aa6e0",        # acento hover
    "LAVENDER": "#9aa0c0",
    "BUTTON_TEXT": "#14161a",
}
```

No dict `PALETTES` (`:122-127`) adicionar `"engineering": THEME_ENGINEERING,`. No `PALETTE_NAMES` (`:130-135`) adicionar `"engineering": "Engineering Dark",`. No `is_dark()` (`:267-269`) incluir `"engineering"`:

```python
        return cls._current in ("dark", "green", "engineering")
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_gui_theme_engineering.py -v` → PASS
`python -c "import ast; ast.parse(open('src/bolt_analysis_studio/gui/theme.py', encoding='utf-8').read()); print('OK')"`

- [ ] **Step 5: Commit**

```bash
git add tests/test_gui_theme_engineering.py src/bolt_analysis_studio/gui/theme.py
git commit -m "$(cat <<'EOF'
feat(theme): paleta Engineering Dark (grafite + acento aco) (Fase 1.1)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 1.2: Rotear os hexes hardcoded do chrome via `objectName` + QSS

**Files:**
- Modify: `gui/theme.py` (novas regras em `get_stylesheet()`, antes do fechamento `:861`), `gui/chrome/widgets/prompt_area.py`, `gui/chrome/widgets/module_bar.py`, `gui/chrome/widgets/multi_viewport.py`
- Test: `tests/test_chrome_theme_consistency.py` (criar)

**Interfaces:**
- Consumes: `Theme.get_stylesheet()`.
- Produces: `PromptArea` com `objectName("promptArea")`; run button `objectName("runButton")`; slots com propriedade dinâmica `active`.

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_chrome_theme_consistency.py
"""Fase 1: chrome não carrega hex hardcoded — cores vêm do tema."""
import re

_HARD = re.compile(r"#[0-9a-fA-F]{6}")

def test_prompt_area_has_no_hardcoded_hex():
    import bolt_analysis_studio.gui.chrome.widgets.prompt_area as m
    src = open(m.__file__, encoding="utf-8").read()
    assert not _HARD.search(src), "PromptArea ainda tem hex hardcoded"

def test_module_bar_run_and_badge_have_no_hardcoded_hex():
    import bolt_analysis_studio.gui.chrome.widgets.module_bar as m
    src = open(m.__file__, encoding="utf-8").read()
    assert not _HARD.search(src)

def test_multi_viewport_has_no_hardcoded_hex():
    import bolt_analysis_studio.gui.chrome.widgets.multi_viewport as m
    src = open(m.__file__, encoding="utf-8").read()
    assert not _HARD.search(src)

def test_stylesheet_carries_chrome_object_rules():
    from bolt_analysis_studio.gui.theme import Theme
    Theme._cached_stylesheet = None
    qss = Theme.get_stylesheet()
    assert "#promptArea" in qss
    assert "#runButton" in qss
    assert "viewportSlot" in qss
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_chrome_theme_consistency.py -v` → FAIL.

- [ ] **Step 3: Implementar — QSS + objectNames**

Em `theme.py`, dentro do f-string de `get_stylesheet()`, antes do `"""` de fechamento (`:861`), acrescentar:

```python

            QWidget#promptArea {{ background-color: {cls.BLUE}; }}
            QWidget#promptArea QLabel {{ color: {cls.BUTTON_TEXT}; }}

            QPushButton#runButton {{
                color: {cls.GREEN}; font-weight: 600;
            }}

            QFrame#viewportSlot {{ border: 1px solid {cls.SURFACE2}; }}
            QFrame#viewportSlot[active="true"] {{ border: 2px solid {cls.BLUE}; }}

            QLabel#badgePass {{ background-color: {cls.GREEN}; color: {cls.BUTTON_TEXT};
                                border-radius: 3px; padding: 0 6px; }}
            QLabel#badgeWarn {{ background-color: {cls.YELLOW}; color: {cls.BUTTON_TEXT};
                                border-radius: 3px; padding: 0 6px; }}
            QLabel#badgeFail {{ background-color: {cls.RED}; color: {cls.BUTTON_TEXT};
                                border-radius: 3px; padding: 0 6px; }}
            QLabel#badgeInfo {{ background-color: {cls.BLUE}; color: {cls.BUTTON_TEXT};
                                border-radius: 3px; padding: 0 6px; }}
```

`prompt_area.py` — remover o `setStyleSheet` inline (`:10`) e dar objectName:

```python
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("promptArea")
        lay = QHBoxLayout(self)
```

`module_bar.py` — run button (`:32-33`) e badge (`:52-57`):

```python
        self._run_btn = QPushButton("Run")
        self._run_btn.setObjectName("runButton")
        self._run_btn.clicked.connect(lambda: self.run_requested.emit())
```

```python
    def set_badge(self, text: str, kind: str = "info") -> None:
        names = {"pass": "badgePass", "warn": "badgeWarn",
                 "fail": "badgeFail", "info": "badgeInfo"}
        self._badge.setText(f"  {text}  " if text else "")
        self._badge.setObjectName(names.get(kind, "badgeInfo") if text else "")
        # re-aplica o QSS após troca de objectName
        self._badge.style().unpolish(self._badge)
        self._badge.style().polish(self._badge)
```

`multi_viewport.py` — `_Slot.__init__` seta objectName e `set_active` usa propriedade dinâmica (`:15-41`):

```python
class _Slot(QFrame):
    def __init__(self, index, on_focus):
        super().__init__()
        self.setObjectName("viewportSlot")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._index = index
        self._on_focus = on_focus
        lay = QVBoxLayout(self)
        lay.setContentsMargins(1, 1, 1, 1)
        self._content = QLabel(f"[ viewport {index + 1} ]")
        self._content.setMinimumSize(80, 60)
        lay.addWidget(self._content)
```

```python
    def set_active(self, active):
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_chrome_theme_consistency.py tests/test_chrome_*.py -v` → PASS (garantir que os testes de chrome existentes não regridem).
Syntax-check nos 4 arquivos editados.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chrome_theme_consistency.py src/bolt_analysis_studio/gui/theme.py src/bolt_analysis_studio/gui/chrome/widgets/prompt_area.py src/bolt_analysis_studio/gui/chrome/widgets/module_bar.py src/bolt_analysis_studio/gui/chrome/widgets/multi_viewport.py
git commit -m "$(cat <<'EOF'
refactor(chrome): hexes do chrome roteados via objectName+QSS (Fase 1.2)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 1.3: Tipografia numérica monoespaçada + densidade

**Files:**
- Modify: `gui/theme.py` (regra QSS para valores numéricos e densidade de árvore/toolbar, antes de `:861`)
- Test: `tests/test_gui_theme_engineering.py` (estender)

- [ ] **Step 1: Estender o teste**

```python
def test_stylesheet_has_numeric_mono_and_density():
    from bolt_analysis_studio.gui.theme import Theme
    Theme._cached_stylesheet = None
    qss = Theme.get_stylesheet()
    assert "QLabel#numeric" in qss           # papel de valor numérico
    assert Theme.FONT_MONO.split(",")[0].strip("'\" ") in qss  # Consolas presente
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_gui_theme_engineering.py -k numeric_mono -v` → FAIL

- [ ] **Step 3: Implementar**

No f-string de `get_stylesheet()`, junto das regras da Task 1.2, acrescentar:

```python

            QLabel#numeric, QLineEdit#numeric {{
                font-family: {cls.FONT_MONO};
                qproperty-alignment: 'AlignRight | AlignVCenter';
            }}
            QTreeWidget::item {{ padding: 1px 0; }}
            QToolBar {{ spacing: 2px; }}
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_gui_theme_engineering.py -v` → PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_gui_theme_engineering.py src/bolt_analysis_studio/gui/theme.py
git commit -m "$(cat <<'EOF'
feat(theme): papel numeric mono a direita + densidade (Fase 1.3)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 1.4: Menu de tema no chrome + Engineering como default do chrome

**Files:**
- Modify: `gui/chrome/app_window.py:114-130` (menus), `run_app.py:92,120-121,152-154`
- Test: `tests/test_chrome_theme_menu.py` (criar)

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_chrome_theme_menu.py
"""Fase 1: chrome expõe menu de tema (paridade com a V1)."""
def test_chrome_has_view_theme_menu(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        menus = [a.text() for a in win.menuBar().actions()]
        assert "View" in menus
        view = next(m.menu() for m in win.menuBar().actions() if m.text() == "View")
        subs = [a.text() for a in view.actions()]
        assert any("Engineering" in s for s in subs)
    finally:
        win.close()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_chrome_theme_menu.py -v` → FAIL (sem menu View).

- [ ] **Step 3: Implementar**

`app_window.py:_build_menus` — após `mb.addMenu("Edit")` (`:122`), inserir um menu View com os temas:

```python
        view_menu = mb.addMenu("View")
        theme_menu = view_menu.addMenu("Theme")
        from ..theme import Theme, PALETTE_NAMES
        for key, label in PALETTE_NAMES.items():
            act = theme_menu.addAction(label)
            act.triggered.connect(lambda _c=False, k=key: self._apply_theme(k))
```

Adicionar o handler (após `_open_wizard`, antes de `closeEvent`):

```python
    def _apply_theme(self, key: str) -> None:
        from ..theme import Theme
        try:
            Theme.set_theme(key)
            Theme.save_theme_preference()
            self.setStyleSheet(Theme.get_stylesheet())
        except Exception as exc:  # pragma: no cover - defensivo
            self.prompt.set_prompt(f"Tema indisponível: {exc}")
```

`run_app.py` — expor `engineering` no CLI (`:92`): `choices=['dark', 'light', 'green', 'engineering']`. E o default do chrome (`:120-121`): quando `--v2` e sem `--theme` e sem preferência salva, usar `engineering`:

```python
    from bolt_analysis_studio.gui.theme import Theme
    if args.theme:
        saved = args.theme
    elif args.v2 and not Theme._PREFS_FILE.exists():
        saved = "engineering"
    else:
        saved = Theme.load_theme_preference()
    Theme.set_theme(saved)
    app.setStyleSheet(Theme.get_stylesheet())
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_chrome_theme_menu.py -v` → PASS
`python -c "import ast; ast.parse(open('run_app.py', encoding='utf-8').read()); print('OK')"`

- [ ] **Step 5: Commit**

```bash
git add tests/test_chrome_theme_menu.py src/bolt_analysis_studio/gui/chrome/app_window.py run_app.py
git commit -m "$(cat <<'EOF'
feat(chrome): menu View>Theme + Engineering default do chrome (Fase 1.4)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# FASE 2 — Ícones vetoriais (aposentar emoji do chrome)

### Task 2.1: Loader de ícones SVG com recolor por tema + set base

**Files:**
- Create: `gui/icons.py`, `resources/icons/*.svg`, `resources/app_icon.svg`
- Test: `tests/test_gui_icons.py`

**Interfaces:**
- Produces: `icons.icon(name: str, color: str | None = None, size: int = 20) -> QIcon`; `icons.clear_icon_cache() -> None`. SVGs usam o token literal `__FG__` como cor de traço/preenchimento.

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_gui_icons.py
"""Fase 2: loader de ícones SVG recolore por tema e cacheia."""
from PyQt6.QtGui import QIcon

def test_icon_returns_non_null_for_known_name(qapp):
    from bolt_analysis_studio.gui import icons
    ic = icons.icon("run", size=20)
    assert isinstance(ic, QIcon)
    assert not ic.isNull()
    assert ic.availableSizes()  # tem ao menos um pixmap renderizado

def test_icon_recolors_by_argument(qapp):
    from bolt_analysis_studio.gui import icons
    a = icons.icon("run", color="#ff0000", size=16).pixmap(16, 16).toImage()
    b = icons.icon("run", color="#00ff00", size=16).pixmap(16, 16).toImage()
    # pelo menos um pixel difere entre vermelho e verde
    diff = any(a.pixel(x, y) != b.pixel(x, y)
               for x in range(16) for y in range(16))
    assert diff

def test_unknown_icon_is_null_not_crash(qapp):
    from bolt_analysis_studio.gui import icons
    assert icons.icon("does-not-exist").isNull()

def test_svg_assets_use_fg_token():
    from pathlib import Path
    import bolt_analysis_studio
    root = Path(bolt_analysis_studio.__file__).resolve().parent / "resources" / "icons"
    svgs = list(root.glob("*.svg"))
    assert len(svgs) >= 8
    for p in svgs:
        assert "__FG__" in p.read_text(encoding="utf-8"), f"{p.name} sem __FG__"
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_gui_icons.py -v` → FAIL (módulo/assets inexistentes).

- [ ] **Step 3: Implementar o loader**

Criar `gui/icons.py`:

```python
"""Loader de ícones SVG monocromáticos com recolor por tema.

Cada .svg em resources/icons/ usa o token literal ``__FG__`` como cor de
traço/preenchimento; o loader substitui pelo hex do tema (ou por uma cor
explícita) e renderiza um QPixmap. Cacheado por (name, color, size).
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PyQt6.QtCore import QByteArray, Qt
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer

from .theme import Theme

_ICON_DIR = Path(__file__).resolve().parent.parent / "resources" / "icons"


def _render(raw: bytes, size: int, color: str) -> QPixmap:
    data = raw.replace(b"__FG__", color.encode("ascii"))
    renderer = QSvgRenderer(QByteArray(data))
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    renderer.render(p)
    p.end()
    return pm


@lru_cache(maxsize=512)
def _cached(name: str, color: str, size: int) -> QIcon:
    path = _ICON_DIR / f"{name}.svg"
    if not path.exists():
        return QIcon()
    icon = QIcon()
    icon.addPixmap(_render(path.read_bytes(), size, color))
    return icon


def icon(name: str, color: str | None = None, size: int = 20) -> QIcon:
    return _cached(name, color or Theme.TEXT, size)


def clear_icon_cache() -> None:
    """Chamar em troca de tema para reconstruir ícones na nova cor."""
    _cached.cache_clear()
```

Criar `resources/icons/` com SVGs 24×24 stroke `__FG__`. Padrão de autoria (traço 2px, sem preenchimento salvo indicado), exemplos completos:

`resources/icons/run.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="__FG__" stroke="none"><path d="M8 5v14l11-7z"/></svg>
```
`resources/icons/stop.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="__FG__" stroke="none"><rect x="6" y="6" width="12" height="12" rx="1"/></svg>
```
`resources/icons/new.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="__FG__" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/></svg>
```
`resources/icons/open.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="__FG__" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7h6l2 2h10v9a2 2 0 0 1-2 2H3z"/></svg>
```
`resources/icons/save.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="__FG__" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3h11l3 3v15H5z"/><path d="M8 3v6h7"/><circle cx="12" cy="15" r="2"/></svg>
```
`resources/icons/undo.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="__FG__" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 7L4 12l5 5"/><path d="M4 12h11a5 5 0 0 1 0 10h-1"/></svg>
```
`resources/icons/redo.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="__FG__" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 7l5 5-5 5"/><path d="M20 12H9a5 5 0 0 0 0 10h1"/></svg>
```
`resources/icons/fit.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="__FG__" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>
```
`resources/icons/zoom-in.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="__FG__" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3M11 8v6M8 11h6"/></svg>
```
`resources/icons/zoom-out.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="__FG__" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3M8 11h6"/></svg>
```
`resources/icons/camera.svg` (screenshot):
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="__FG__" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8h4l2-2h6l2 2h4v11H3z"/><circle cx="12" cy="13" r="3.5"/></svg>
```
`resources/icons/wizard.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="__FG__" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 19l9-9M14 6l1.5-1.5M18 10l1.5-1.5M15 4l1 3 3 1-3 1-1 3-1-3-3-1 3-1z"/></svg>
```

Autorar os demais nomes do inventário (§1.3 da spec) seguindo este mesmo padrão 24×24: `pan, print, settings, help, element, contact, load, step, job, report, validation, expand, collapse, head, shank, thread, nut, washer, flange, gasket, ground`. Também `resources/app_icon.svg` (um parafuso estilizado, mesmo padrão, `fill="__FG__"`).

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_gui_icons.py -v` → PASS
`python -c "import ast; ast.parse(open('src/bolt_analysis_studio/gui/icons.py', encoding='utf-8').read()); print('OK')"`

- [ ] **Step 5: Commit**

```bash
git add tests/test_gui_icons.py src/bolt_analysis_studio/gui/icons.py src/bolt_analysis_studio/resources/
git commit -m "$(cat <<'EOF'
feat(gui): loader de icones SVG com recolor por tema + set base (Fase 2.1)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 2.2: Aplicar ícones no ModuleBar, ContextBar e Tree; rebuild na troca de tema

**Files:**
- Modify: `gui/chrome/widgets/module_bar.py` (Run/Stop com ícone), `gui/chrome/widgets/context_bar.py` (ações com ícone), `gui/chrome/widgets/model_tree.py` (nós com ícone), `gui/chrome/app_window.py` (callback de tema → `clear_icon_cache` + rebuild)
- Test: `tests/test_chrome_icons.py`

**Interfaces:**
- Consumes: `icons.icon(name, size)`.
- Produces: `ModuleBar._run_btn.icon()` não-nulo; nós de topo da `ModelTree` com ícone.

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_chrome_icons.py
"""Fase 2: chrome usa QIcon vetorial (não emoji) nos controles-chave."""
def test_run_stop_have_icons(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.module_bar import ModuleBar
    bar = ModuleBar()
    assert not bar._run_btn.icon().isNull()
    assert not bar._stop_btn.icon().isNull()

def test_tree_top_nodes_have_icons(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.model_tree import ModelTree, TOP_NODES
    tree = ModelTree()
    for i in range(tree.topLevelItemCount()):
        assert not tree.topLevelItem(i).icon(0).isNull()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_chrome_icons.py -v` → FAIL.

- [ ] **Step 3: Implementar**

`module_bar.py` — importar `from ...icons import icon` e setar nos botões:

```python
        self._run_btn = QPushButton("Run")
        self._run_btn.setObjectName("runButton")
        self._run_btn.setIcon(icon("run", size=16))
        self._run_btn.clicked.connect(lambda: self.run_requested.emit())
        self.addWidget(self._run_btn)
        self._stop_btn = QPushButton("Stop")
        self._stop_btn.setIcon(icon("stop", size=16))
        self._stop_btn.clicked.connect(lambda: self.stop_requested.emit())
```

`context_bar.py` — mapear rótulo→ícone e setar no `QAction`. Adicionar no topo:

```python
from ...icons import icon

_ICON_FOR = {
    "+ Element": "element", "+ Material": "new", "+ Thread": "contact",
    "+ Bearing": "contact", "+ Flange": "element", "+ Global Load": "load",
    "+ Per-Element": "load", "+ Thermal": "load", "+ Static-Preload": "step",
    "+ Coupled-Loosening": "step", "Solver": "settings", "Jobs": "job",
    "Preload": "validation", "Export": "save", "Template": "report",
}
```

No `set_module` (`:31-35`):

```python
        for label in _ACTIONS.get(name, []):
            act = QAction(label, self)
            ic = _ICON_FOR.get(label)
            if ic:
                act.setIcon(icon(ic, size=16))
            act.triggered.connect(lambda _c, L=label: self.action_triggered.emit(L))
            self.addAction(act)
            self._actions.append(act)
```

`model_tree.py` — importar `from ...icons import icon` e um mapa nó→ícone; no laço de `TOP_NODES` (`:33-37`):

```python
_NODE_ICON = {"Model": "element", "Contacts": "contact", "Loads": "load",
              "Analysis": "step", "Jobs": "job", "Results": "validation",
              "Validation": "validation", "Reports": "report"}
```
```python
        for name in TOP_NODES:
            it = QTreeWidgetItem([name])
            it.setIcon(0, icon(_NODE_ICON.get(name, "element"), size=16))
            it.setData(0, Qt.ItemDataRole.UserRole, ("module", NODE_TO_MODULE[name]))
            self.addTopLevelItem(it)
            self._tops[name] = it
```

`app_window.py` — registrar callback de tema que limpa o cache e reconstrói. No fim do `__init__` (após `switch_module("Model")`, `:58`):

```python
        from ..icons import clear_icon_cache
        from ..theme import Theme
        def _reskin_icons():
            clear_icon_cache()
            self.module_bar.rebuild_icons()
            self.tree.rebuild_icons()
        Theme.register_callback(_reskin_icons)
        self._reskin_icons = _reskin_icons  # segura referência
```

Adicionar `rebuild_icons()` em `ModuleBar` e `ModelTree` (re-setam os ícones com a cor atual). Em `ModuleBar`:

```python
    def rebuild_icons(self) -> None:
        self._run_btn.setIcon(icon("run", size=16))
        self._stop_btn.setIcon(icon("stop", size=16))
```
Em `ModelTree`:
```python
    def rebuild_icons(self) -> None:
        for name, it in self._tops.items():
            it.setIcon(0, icon(_NODE_ICON.get(name, "element"), size=16))
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_chrome_icons.py tests/test_chrome_*.py -v` → PASS
Syntax-check dos 4 arquivos.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chrome_icons.py src/bolt_analysis_studio/gui/chrome/widgets/module_bar.py src/bolt_analysis_studio/gui/chrome/widgets/context_bar.py src/bolt_analysis_studio/gui/chrome/widgets/model_tree.py src/bolt_analysis_studio/gui/chrome/app_window.py
git commit -m "$(cat <<'EOF'
feat(chrome): icones SVG no ModuleBar/ContextBar/Tree + reskin no tema (Fase 2.2)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 2.3: Ícones + ícone de aplicativo na V1 e no launcher

**Files:**
- Modify: `gui/main_window.py:5615-5663` (toolbar com QIcon), `run_app.py` (`app.setWindowIcon`)
- Test: `tests/test_gui_v1_chrome.py` (estender)

- [ ] **Step 1: Estender o teste**

```python
def test_v1_toolbar_actions_have_icons(qapp):
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    from PyQt6.QtWidgets import QToolBar
    win = BoltAnalysisStudio()
    try:
        tbs = win.findChildren(QToolBar)
        acts = [a for tb in tbs for a in tb.actions() if a.text()]
        assert acts and all(not a.icon().isNull() for a in acts)
    finally:
        win.close()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_gui_v1_chrome.py -k toolbar_actions_have_icons -v` → FAIL

- [ ] **Step 3: Implementar**

`main_window.py:_setup_toolbar` — importar `from .icons import icon` no topo do arquivo e dar ícone a cada ação:

```python
        new_action = QAction(icon("new"), "New", self)
        ...
        open_action = QAction(icon("open"), "Open", self)
        ...
        save_action = QAction(icon("save"), "Save", self)
        ...
        builder_action = QAction(icon("element"), "MSD Builder", self)
        ...
        run_action = QAction(icon("run"), "Run", self)
        ...
        stop_action = QAction(icon("stop"), "Stop", self)
        ...
        plots_action = QAction(icon("validation"), "Plots", self)
        ...
        similitude_action = QAction(icon("settings"), "Similitude", self)
        ...
        report_action = QAction(icon("report"), "Report", self)
```

`run_app.py` — após `app.setStyleSheet(...)` (`:122`):

```python
    from bolt_analysis_studio.gui.icons import icon
    app.setWindowIcon(icon("app_icon", size=256))
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_gui_v1_chrome.py -v` → PASS
Syntax-check.

- [ ] **Step 5: Commit**

```bash
git add tests/test_gui_v1_chrome.py src/bolt_analysis_studio/gui/main_window.py run_app.py
git commit -m "$(cat <<'EOF'
feat(gui): toolbar V1 com QIcon vetorial + icone do app (Fase 2.3)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# FASE 3 — Zonas Abaqus no chrome

### Task 3.1: Message area (Messages / Job Log)

**Files:**
- Create: `gui/chrome/widgets/message_area.py`
- Modify: `gui/chrome/app_window.py:103-111` (adicionar dock inferior)
- Test: `tests/test_chrome_message_area.py`

**Interfaces:**
- Produces: `MessageArea.append(text: str, channel: str = "messages") -> None`; `MessageArea.clear_channel(channel: str) -> None`; canais `"messages"` e `"job"`.

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_chrome_message_area.py
"""Fase 3: message area com abas Messages / Job Log."""
def test_message_area_channels(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.message_area import MessageArea
    ma = MessageArea()
    labels = [ma._tabs.tabText(i) for i in range(ma._tabs.count())]
    assert labels == ["Messages", "Job Log"]

def test_append_and_read(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.message_area import MessageArea
    ma = MessageArea()
    ma.append("preflight ok", "messages")
    ma.append("cycle 100/1000", "job")
    assert "preflight ok" in ma._views["messages"].toPlainText()
    assert "cycle 100/1000" in ma._views["job"].toPlainText()

def test_chrome_hosts_message_area(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        assert hasattr(win, "messages")
        win.messages.append("hello")
        assert "hello" in win.messages._views["messages"].toPlainText()
    finally:
        win.close()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_chrome_message_area.py -v` → FAIL

- [ ] **Step 3: Implementar**

Criar `gui/chrome/widgets/message_area.py`:

```python
"""MessageArea — área de mensagens/log do chrome (paridade Abaqus §3)."""
from __future__ import annotations

from PyQt6.QtWidgets import QPlainTextEdit, QTabWidget, QVBoxLayout, QWidget

_CHANNELS = [("messages", "Messages"), ("job", "Job Log")]


class MessageArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self._tabs = QTabWidget()
        self._views = {}
        for key, label in _CHANNELS:
            view = QPlainTextEdit()
            view.setReadOnly(True)
            view.setMaximumBlockCount(5000)   # não cresce sem limite
            self._views[key] = view
            self._tabs.addTab(view, label)
        lay.addWidget(self._tabs)

    def append(self, text: str, channel: str = "messages") -> None:
        view = self._views.get(channel)
        if view is not None:
            view.appendPlainText(text)

    def clear_channel(self, channel: str) -> None:
        view = self._views.get(channel)
        if view is not None:
            view.clear()
```

`app_window.py` — importar `from .widgets.message_area import MessageArea` e, no `_build_chrome`, após o prompt_dock (`:108`) e antes do `setStatusBar` (`:110`):

```python
        self.messages = MessageArea()
        msg_dock = QDockWidget("Messages", self)
        msg_dock.setWidget(self.messages)
        msg_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable
                             | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, msg_dock)
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_chrome_message_area.py -v` → PASS
Syntax-check dos 2 arquivos.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chrome_message_area.py src/bolt_analysis_studio/gui/chrome/widgets/message_area.py src/bolt_analysis_studio/gui/chrome/app_window.py
git commit -m "$(cat <<'EOF'
feat(chrome): message area (Messages/Job Log) (Fase 3.1)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 3.2: Toolbar de viewport + bloco de contexto

**Files:**
- Create: `gui/chrome/widgets/viewport_toolbar.py`, `gui/chrome/widgets/context_block.py`
- Modify: `gui/chrome/app_window.py` (montar acima do viewport; atualizar o bloco em `switch_module`)
- Test: `tests/test_chrome_viewport_chrome.py`

**Interfaces:**
- Produces: `ViewportToolbar(get_view: Callable[[], QGraphicsView])` com ações fit/zoom-in/zoom-out/screenshot; `ContextBlock.set_context(module: str, model: str, step: str) -> None`.

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_chrome_viewport_chrome.py
"""Fase 3: toolbar de viewport + bloco de contexto."""
def test_context_block_formats(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.context_block import ContextBlock
    cb = ContextBlock()
    cb.set_context("Model", "M16_junker", "Coupled-Loosening")
    txt = cb._label.text()
    assert "Model" in txt and "M16_junker" in txt and "Coupled-Loosening" in txt

def test_viewport_toolbar_actions(qapp):
    from PyQt6.QtWidgets import QGraphicsView
    from bolt_analysis_studio.gui.chrome.widgets.viewport_toolbar import ViewportToolbar
    view = QGraphicsView()
    tb = ViewportToolbar(lambda: view)
    labels = [a.text() for a in tb.actions() if a.text()]
    assert {"Fit", "Zoom In", "Zoom Out", "Screenshot"}.issubset(set(labels))

def test_chrome_updates_context_block_on_switch(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        win.switch_module("Loads")
        assert "Loads" in win.context_block._label.text()
    finally:
        win.close()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_chrome_viewport_chrome.py -v` → FAIL

- [ ] **Step 3: Implementar**

Criar `gui/chrome/widgets/context_block.py`:

```python
"""ContextBlock — faixa 'Module · Model · Step' abaixo do ModuleBar (Abaqus §3)."""
from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget


class ContextBlock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 2, 8, 2)
        self._label = QLabel("Module: — · Model: — · Step: —")
        lay.addWidget(self._label)
        lay.addStretch(1)

    def set_context(self, module: str, model: str, step: str) -> None:
        self._label.setText(
            f"Module: {module or '—'} · Model: {model or '—'} · Step: {step or '—'}")
```

Criar `gui/chrome/widgets/viewport_toolbar.py`:

```python
"""ViewportToolbar — fit/zoom/screenshot sobre o QGraphicsView ativo (Abaqus §5)."""
from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QGraphicsView, QToolBar

from ...icons import icon


class ViewportToolbar(QToolBar):
    def __init__(self, get_view: Callable[[], QGraphicsView], parent=None):
        super().__init__("Viewport", parent)
        self.setMovable(False)
        self._get_view = get_view
        self.addAction(icon("fit"), "Fit", self._fit)
        self.addAction(icon("zoom-in"), "Zoom In", lambda: self._zoom(1.25))
        self.addAction(icon("zoom-out"), "Zoom Out", lambda: self._zoom(0.8))
        self.addAction(icon("camera"), "Screenshot", self._screenshot)

    def _fit(self) -> None:
        view = self._get_view()
        scene = view.scene() if view is not None else None
        if scene is not None:
            view.fitInView(scene.itemsBoundingRect(),
                           Qt.AspectRatioMode.KeepAspectRatio)

    def _zoom(self, factor: float) -> None:
        view = self._get_view()
        if view is not None:
            view.scale(factor, factor)

    def _screenshot(self) -> None:
        view = self._get_view()
        if view is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salvar imagem", "viewport.png",
                                              "PNG (*.png)")
        if path:
            view.grab().save(path, "PNG")
```

`app_window.py` — importar ambos; no `_build_chrome`, após o `context_bar` (`:66`), inserir o context_block como toolbar-break:

```python
        self.context_block = ContextBlock()
        self.addToolBarBreak()
        cb_toolbar = QToolBar("ContextBlock")
        cb_toolbar.setMovable(False)
        cb_toolbar.addWidget(self.context_block)
        self.addToolBar(cb_toolbar)
        self.viewport_toolbar = ViewportToolbar(
            lambda: self.model_controller.viewport_widget())
        self.addToolBarBreak()
        self.addToolBar(self.viewport_toolbar)
```

(Importar `QToolBar` no `app_window.py`.) No `switch_module`, ao fim (antes do `if self.module_bar...`, `:177`), atualizar o bloco:

```python
        model_name = getattr(getattr(self.app_state, "model", None), "name", "") or "—"
        step = self.module_bar._step_combo.currentText()
        self.context_block.set_context(name, model_name, step)
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_chrome_viewport_chrome.py tests/test_chrome_*.py -v` → PASS
Syntax-check.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chrome_viewport_chrome.py src/bolt_analysis_studio/gui/chrome/widgets/viewport_toolbar.py src/bolt_analysis_studio/gui/chrome/widgets/context_block.py src/bolt_analysis_studio/gui/chrome/app_window.py
git commit -m "$(cat <<'EOF'
feat(chrome): toolbar de viewport + bloco de contexto (Fase 3.2)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 3.3: Gradiente de fundo + carimbo ISO 7200 no viewport

**Files:**
- Modify: `gui/msd_builder.py:1311+` (`SchematicView` — `drawBackground`/`drawForeground`; método `set_title_block`)
- Test: `tests/test_schematic_stamp.py`

**Interfaces:**
- Produces: `SchematicView.set_title_block(model: str, module: str, step: str, metric: str) -> None`; `SchematicView.set_stamp_enabled(bool)`.

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_schematic_stamp.py
"""Fase 3: SchematicView desenha gradiente + carimbo sem crashar."""
def test_set_title_block_and_render(qapp):
    from PyQt6.QtGui import QPixmap, QPainter
    from bolt_analysis_studio.gui.msd_builder import SchematicView
    view = SchematicView()
    view.set_title_block("M16_junker", "Model", "Coupled", "MAE 0.024")
    view.set_stamp_enabled(True)
    # renderiza offscreen: drawBackground/drawForeground não devem lançar
    pm = QPixmap(400, 300)
    p = QPainter(pm)
    view.render(p)
    p.end()
    assert view._title_block["model"] == "M16_junker"

def test_stamp_toggle_default_off(qapp):
    from bolt_analysis_studio.gui.msd_builder import SchematicView
    view = SchematicView()
    assert view._stamp_enabled is False  # default inerte (backward-compat)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_schematic_stamp.py -v` → FAIL

- [ ] **Step 3: Implementar**

Em `SchematicView.__init__` (após `:1358`, onde já seta o background brush), inicializar estado do carimbo:

```python
        self._stamp_enabled = False
        self._title_block = {"model": "", "module": "", "step": "", "metric": ""}
```

Adicionar métodos e overrides na classe:

```python
    def set_title_block(self, model="", module="", step="", metric="") -> None:
        self._title_block = {"model": model, "module": module,
                             "step": step, "metric": metric}
        self.viewport().update()

    def set_stamp_enabled(self, enabled: bool) -> None:
        self._stamp_enabled = bool(enabled)
        self.viewport().update()

    def drawBackground(self, painter, rect):
        # Gradiente vertical (assinatura CAE) + a grade fina por cima.
        from PyQt6.QtGui import QLinearGradient, QColor
        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0.0, QColor(Theme.SURFACE1))
        grad.setColorAt(1.0, QColor(Theme.CRUST))
        painter.fillRect(rect, grad)

    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect) if hasattr(super(), "drawForeground") else None
        if not self._stamp_enabled:
            return
        from PyQt6.QtGui import QColor, QPen, QFont
        from PyQt6.QtCore import Qt as _Qt
        tb = self._title_block
        lines = [f"Modelo  {tb['model'] or '—'}",
                 f"Modulo  {tb['module'] or '—'}   Step  {tb['step'] or '—'}",
                 f"{tb['metric'] or ''}"]
        painter.save()
        painter.resetTransform()          # carimbo em coords de tela, não da cena
        vp = self.viewport().rect()
        w, h = 240, 58
        x, y = vp.right() - w - 12, vp.bottom() - h - 12
        painter.setPen(QPen(QColor(Theme.SURFACE2), 1))
        painter.fillRect(x, y, w, h, QColor(Theme.CRUST))
        painter.drawRect(x, y, w, h)
        painter.setFont(QFont(Theme.FONT_MONO_FAMILY, 8))
        painter.setPen(QColor(Theme.SUBTEXT))
        for i, ln in enumerate(lines):
            painter.drawText(x + 8, y + 16 + i * 15, ln)
        painter.restore()
```

Nota: como o `drawBackground` agora pinta o gradiente, o `setBackgroundBrush(...)` em `:1358` fica redundante (pode manter — o override vence). A grade fina existente (`_draw_grid`) desenha itens na cena, acima do background.

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_schematic_stamp.py -v` → PASS
`python -c "import ast; ast.parse(open('src/bolt_analysis_studio/gui/msd_builder.py', encoding='utf-8').read()); print('OK')"`

- [ ] **Step 5: Commit**

```bash
git add tests/test_schematic_stamp.py src/bolt_analysis_studio/gui/msd_builder.py
git commit -m "$(cat <<'EOF'
feat(gui): viewport com gradiente + carimbo ISO 7200 (default off) (Fase 3.3)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 3.4: Prompt com instruções reais + desativar controles mortos até a Fase 4

**Files:**
- Modify: `gui/chrome/app_window.py` (prompts contextuais por ação; ligar stamp no Model; desabilitar Run/Stop com tooltip), `gui/chrome/widgets/module_bar.py` (`set_run_enabled`)
- Test: `tests/test_chrome_prompt_and_deadcontrols.py`

**Interfaces:**
- Produces: `ModuleBar.set_run_enabled(enabled: bool, reason: str = "") -> None`.

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_chrome_prompt_and_deadcontrols.py
"""Fase 3: Run/Stop desabilitados até a Fase 4; prompt de contexto."""
def test_run_disabled_with_reason(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.module_bar import ModuleBar
    bar = ModuleBar()
    bar.set_run_enabled(False, "Analysis chega na Fase 4")
    assert not bar._run_btn.isEnabled()
    assert "Fase 4" in bar._run_btn.toolTip()

def test_context_action_sets_instructional_prompt(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        win.switch_module("Contacts")
        win._on_context_action("+ Thread")
        assert win.prompt._prompt.text() != "Acao: + Thread"  # instrução, não eco
        assert len(win.prompt._prompt.text()) > 12
    finally:
        win.close()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_chrome_prompt_and_deadcontrols.py -v` → FAIL

- [ ] **Step 3: Implementar**

`module_bar.py`:

```python
    def set_run_enabled(self, enabled: bool, reason: str = "") -> None:
        self._run_btn.setEnabled(enabled)
        self._stop_btn.setEnabled(enabled)
        self._run_btn.setToolTip(reason if not enabled else "Rodar a análise")
```

`app_window.py` — no fim do `__init__`, desabilitar até a Fase 4:

```python
        self.module_bar.set_run_enabled(False, "Rode pela V1 (Solver); "
                                        "o módulo Analysis chega na Fase 4.")
```

Trocar `_on_context_action` por prompts instrucionais + ligar o stamp no Model. Substituir o método (`:182-183`) por:

```python
    _ACTION_HELP = {
        "+ Element": "Selecione um ponto no viewport para inserir o elemento.",
        "+ Thread": "Selecione a porca e depois o parafuso para criar o ThreadContact.",
        "+ Bearing": "Selecione as duas faces em contato para criar o bearing.",
        "+ Global Load": "Defina F0, amplitude e frequência no inspector à direita.",
        "+ Coupled-Loosening": "Configure dt e n_cycles; rode pela V1 até a Fase 4.",
    }

    def _on_context_action(self, label: str):
        self.prompt.set_prompt(self._ACTION_HELP.get(
            label, f"{label}: configure os parâmetros no inspector."))
```

No `switch_module`, no ramo `_SCHEMATIC_MODULES` (após `:162`), ligar o carimbo e alimentar o title block:

```python
            sv = self.model_controller.viewport_widget()
            if hasattr(sv, "set_stamp_enabled"):
                sv.set_stamp_enabled(True)
                mdl = getattr(self.app_state, "model", None)
                res = getattr(self.app_state, "results", None)
                metric = ""
                sv.set_title_block(getattr(mdl, "name", "") or "—", name,
                                   self.module_bar._step_combo.currentText(), metric)
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_chrome_prompt_and_deadcontrols.py tests/test_chrome_*.py -v` → PASS
Syntax-check.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chrome_prompt_and_deadcontrols.py src/bolt_analysis_studio/gui/chrome/widgets/module_bar.py src/bolt_analysis_studio/gui/chrome/app_window.py
git commit -m "$(cat <<'EOF'
feat(chrome): prompts instrucionais + stamp no Model + Run/Stop off ate Fase 4 (Fase 3.4)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# FASE 4 — Módulos funcionais (padrão controller-embrulha-V1)

Reutiliza o padrão já provado (`ModelController`/`ValidationController`): cada módulo embrulha o widget V1 correspondente e o re-hospeda num viewport do chrome. É o caminho de menor risco para dar função a Analysis/Results/Report.

### Task 4.1: AnalysisController — embrulha `SolverTab`, liga Run/Stop e o Job Log

**Files:**
- Create: `gui/chrome/controllers/analysis_controller.py`
- Modify: `gui/chrome/app_window.py` (instanciar; rotear módulo Analysis; wire Run/Stop; SolverWorker.log→message area)
- Test: `tests/test_chrome_analysis_module.py`

**Interfaces:**
- Consumes: `SolverTab` (V1), `AppState`.
- Produces: `AnalysisController.viewport_widget() -> QWidget`; `.run() -> None`; `.stop() -> None`; sinais `log_message = pyqtSignal(str)`, `progress = pyqtSignal(int, str)`, `job_state = pyqtSignal(str)` (`"running"|"done"|"error"|"idle"`).

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_chrome_analysis_module.py
"""Fase 4: módulo Analysis embrulha a SolverTab e expõe run/stop + log."""
def test_analysis_controller_exposes_solver_widget(qapp):
    from bolt_analysis_studio.gui.chrome.controllers.analysis_controller import AnalysisController
    ac = AnalysisController()
    w = ac.viewport_widget()
    assert w is not None
    assert hasattr(ac, "run") and hasattr(ac, "stop")

def test_analysis_controller_relays_log(qapp):
    from bolt_analysis_studio.gui.chrome.controllers.analysis_controller import AnalysisController
    ac = AnalysisController()
    seen = []
    ac.log_message.connect(seen.append)
    ac._on_log("preflight ok")
    assert "preflight ok" in seen

def test_chrome_analysis_module_hosts_solver(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        win.switch_module("Analysis")
        # o módulo Analysis não é mais placeholder
        assert win.analysis_controller.viewport_widget() is not None
        # Run agora habilitado
        assert win.module_bar._run_btn.isEnabled()
    finally:
        win.close()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_chrome_analysis_module.py -v` → FAIL

- [ ] **Step 3: Implementar**

Criar `gui/chrome/controllers/analysis_controller.py`:

```python
"""AnalysisController — embrulha a SolverTab (V1) e a re-hospeda no chrome.

Segue o padrão de ModelController: instancia o widget V1, re-expõe run/stop e
relança o log/progresso do SolverWorker como sinais que o chrome liga à
message area. Não reimplementa o solver.
"""
from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

from ....core.app_state import get_app_state


class AnalysisController(QObject):
    log_message = pyqtSignal(str)
    progress = pyqtSignal(int, str)
    job_state = pyqtSignal(str)          # running | done | error | idle

    def __init__(self, app_state=None, parent=None):
        super().__init__(parent)
        self.app_state = app_state or get_app_state()
        from ...main_window import SolverTab
        self._tab = SolverTab()
        self._wire()

    def _wire(self) -> None:
        # A SolverTab expõe run_btn/stop_btn e orquestra o SolverWorker.
        # Interceptamos o worker quando criado para relançar log/progress.
        tab = self._tab
        if hasattr(tab, "log_signal"):
            try:
                tab.log_signal.connect(self._on_log)
            except Exception:
                pass

    def viewport_widget(self):
        return self._tab

    def run(self) -> None:
        self.job_state.emit("running")
        btn = getattr(self._tab, "run_btn", None)
        if btn is not None:
            btn.click()

    def stop(self) -> None:
        btn = getattr(self._tab, "stop_btn", None)
        if btn is not None:
            btn.click()
        self.job_state.emit("idle")

    def _on_log(self, text: str) -> None:
        self.log_message.emit(text)

    def _on_progress(self, pct: int, msg: str) -> None:
        self.progress.emit(pct, msg)
```

Nota de implementação para o executor: a `SolverTab` cria o `SolverWorker` internamente. Verificar em `main_window.py` como a `SolverTab` publica log/progresso (procurar `self.log_signal`/`worker.log.connect`); se não houver um sinal público de log na `SolverTab`, adicionar um `log_signal = pyqtSignal(str)` na `SolverTab` e emiti-lo no slot que hoje recebe `worker.log`. Manter a mudança mínima e testada.

`app_window.py` — instanciar no `_build_chrome` (após `validation_controller`, `:94`):

```python
        self.analysis_controller = AnalysisController(self.app_state)
        self._center.addWidget(self.analysis_controller.viewport_widget())
        self.analysis_controller.log_message.connect(
            lambda t: self.messages.append(t, "job"))
        self.analysis_controller.job_state.connect(self._on_job_state)
```

Wire Run/Stop do ModuleBar (em `_wire_signals`, `:133-142`):

```python
        self.module_bar.run_requested.connect(self.analysis_controller.run)
        self.module_bar.stop_requested.connect(self.analysis_controller.stop)
```

Rotear o módulo Analysis (em `switch_module`, trocar o ramo `else` para tratar `"Analysis"`):

```python
        elif name == "Analysis":
            self._center.setCurrentWidget(self.analysis_controller.viewport_widget())
            self._inspector_dock.setWidget(self.inspector)
            self._palette_dock.hide()
            self.module_bar.set_run_enabled(True)
```

Handler de estado de job + habilitar Run só no módulo certo. Adicionar:

```python
    def _on_job_state(self, state: str) -> None:
        badge = {"running": ("RUNNING", "info"), "done": ("DONE", "pass"),
                 "error": ("ERROR", "fail"), "idle": ("", "info")}
        text, kind = badge.get(state, ("", "info"))
        self.module_bar.set_badge(text, kind)
        self.statusBar().showMessage(
            f"Projeto: — · Modulo: {self._current_module} · Job: {state}")
```

Remover a desabilitação global de Run posta na Task 3.4 (agora o Run habilita ao entrar em Analysis; nos demais módulos, desabilitar). No fim de `switch_module`, para módulos ≠ Analysis, `self.module_bar.set_run_enabled(False, "Entre no módulo Analysis para rodar.")` — colocar isso nos ramos schematic/Results/else.

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_chrome_analysis_module.py tests/test_chrome_*.py -v` → PASS
Syntax-check.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chrome_analysis_module.py src/bolt_analysis_studio/gui/chrome/controllers/analysis_controller.py src/bolt_analysis_studio/gui/chrome/app_window.py src/bolt_analysis_studio/gui/main_window.py
git commit -m "$(cat <<'EOF'
feat(chrome): modulo Analysis embrulha SolverTab + Run/Stop + Job Log (Fase 4.1)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 4.2: ResultsController — plots de Run como sub-modo do Results (Validation vira o outro)

**Files:**
- Create: `gui/chrome/controllers/results_controller.py`
- Modify: `gui/chrome/app_window.py` (Results = tabs [Run | Validation]; ContextBar "Run"/"Validation")
- Test: `tests/test_chrome_results_module.py`

**Interfaces:**
- Consumes: `ResultsTab` (V1), `AppState`.
- Produces: `ResultsController.viewport_widget() -> QWidget`; `.refresh() -> None` (re-plota do `app_state.results`).

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_chrome_results_module.py
"""Fase 4: Results tem sub-modo Run (ResultsTab) + Validation (browser)."""
def test_results_controller_wraps_results_tab(qapp):
    from bolt_analysis_studio.gui.chrome.controllers.results_controller import ResultsController
    rc = ResultsController()
    assert rc.viewport_widget() is not None
    assert hasattr(rc, "refresh")

def test_chrome_results_has_run_and_validation_submodes(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        win.switch_module("Results")
        # o container do Results é um QTabWidget com Run e Validation
        w = win._center.currentWidget()
        from PyQt6.QtWidgets import QTabWidget
        tabs = w if isinstance(w, QTabWidget) else w.findChild(QTabWidget)
        labels = [tabs.tabText(i) for i in range(tabs.count())]
        assert "Run" in labels and "Validation" in labels
    finally:
        win.close()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_chrome_results_module.py -v` → FAIL

- [ ] **Step 3: Implementar**

Criar `gui/chrome/controllers/results_controller.py`:

```python
"""ResultsController — embrulha a ResultsTab (V1) para os plots de Run."""
from __future__ import annotations

from PyQt6.QtCore import QObject

from ....core.app_state import get_app_state


class ResultsController(QObject):
    def __init__(self, app_state=None, parent=None):
        super().__init__(parent)
        self.app_state = app_state or get_app_state()
        from ...main_window import ResultsTab
        self._tab = ResultsTab()

    def viewport_widget(self):
        return self._tab

    def refresh(self) -> None:
        # Re-plota a partir do app_state.results, se a ResultsTab expõe um hook.
        for hook in ("refresh_plots", "_refresh", "update_results"):
            fn = getattr(self._tab, hook, None)
            if callable(fn):
                try:
                    fn()
                except Exception:
                    pass
                return
```

`app_window.py` — no `_build_chrome`, criar um `QTabWidget` para o Results agrupando Run + Validation:

```python
        from PyQt6.QtWidgets import QTabWidget
        self.results_controller = ResultsController(self.app_state)
        self._results_tabs = QTabWidget()
        self._results_tabs.addTab(self.results_controller.viewport_widget(), "Run")
        self._results_tabs.addTab(self.validation_controller.viewport_widget(), "Validation")
        self._center.addWidget(self._results_tabs)
```

No `switch_module`, ramo `Results` (`:163-168`), apontar para o `_results_tabs` e refrescar:

```python
        elif name == "Results":
            self._center.setCurrentWidget(self._results_tabs)
            self.results_controller.refresh()
            self._inspector_dock.setWidget(self.inspector)
            self._palette_dock.hide()
            self.module_bar.set_run_enabled(False, "Entre no módulo Analysis para rodar.")
```

(Remover a linha antiga que adicionava `validation_controller.viewport_widget()` direto ao `_center` para não duplicar o widget — ele agora vive dentro do `_results_tabs`.)

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_chrome_results_module.py tests/test_chrome_*.py -v` → PASS
Syntax-check.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chrome_results_module.py src/bolt_analysis_studio/gui/chrome/controllers/results_controller.py src/bolt_analysis_studio/gui/chrome/app_window.py
git commit -m "$(cat <<'EOF'
feat(chrome): Results com sub-modos Run (ResultsTab) + Validation (Fase 4.2)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 4.3: ReportController — embrulha a `ReportsTab`

**Files:**
- Create: `gui/chrome/controllers/report_controller.py`
- Modify: `gui/chrome/app_window.py` (rotear módulo Report)
- Test: `tests/test_chrome_report_module.py`

**Interfaces:**
- Produces: `ReportController.viewport_widget() -> QWidget`.

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_chrome_report_module.py
"""Fase 4: módulo Report embrulha a ReportsTab (não é mais placeholder)."""
def test_report_controller_wraps_reports_tab(qapp):
    from bolt_analysis_studio.gui.chrome.controllers.report_controller import ReportController
    rc = ReportController()
    assert rc.viewport_widget() is not None

def test_chrome_report_not_placeholder(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    from PyQt6.QtWidgets import QLabel
    win = ChromeWindow()
    try:
        win.switch_module("Report")
        w = win._center.currentWidget()
        # não é o placeholder "[ Report · viewport 1 ]"
        assert not (isinstance(w, QLabel) and "viewport" in w.text())
        assert win._center.currentWidget() is win.report_controller.viewport_widget()
    finally:
        win.close()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_chrome_report_module.py -v` → FAIL

- [ ] **Step 3: Implementar**

Criar `gui/chrome/controllers/report_controller.py`:

```python
"""ReportController — embrulha a ReportsTab (V1) para o módulo Report."""
from __future__ import annotations

from PyQt6.QtCore import QObject

from ....core.app_state import get_app_state


class ReportController(QObject):
    def __init__(self, app_state=None, parent=None):
        super().__init__(parent)
        self.app_state = app_state or get_app_state()
        from ...main_window import ReportsTab
        self._tab = ReportsTab()

    def viewport_widget(self):
        return self._tab
```

`app_window.py` — instanciar em `_build_chrome`:

```python
        self.report_controller = ReportController(self.app_state)
        self._center.addWidget(self.report_controller.viewport_widget())
```

E rotear em `switch_module` (novo ramo):

```python
        elif name == "Report":
            self._center.setCurrentWidget(self.report_controller.viewport_widget())
            self._inspector_dock.setWidget(self.inspector)
            self._palette_dock.hide()
            self.module_bar.set_run_enabled(False, "Entre no módulo Analysis para rodar.")
```

O ramo `else` (placeholder) agora só é atingido por módulos sem controller — na prática nenhum, mas mantê-lo como salvaguarda.

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_chrome_report_module.py tests/test_chrome_*.py -v` → PASS
Syntax-check.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chrome_report_module.py src/bolt_analysis_studio/gui/chrome/controllers/report_controller.py src/bolt_analysis_studio/gui/chrome/app_window.py
git commit -m "$(cat <<'EOF'
feat(chrome): modulo Report embrulha ReportsTab (Fase 4.3)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# FASE 5 — Consolidação (auto-defaults, tree profunda, integradores, chrome default)

### Task 5.1: Reduzir integradores 5→2 na V1 (spec §3.A)

**Files:**
- Modify: `gui/main_window.py:1101-1106` (combo do solver), `:3235` (segundo combo)
- Test: `tests/test_gui_integrators.py`

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_gui_integrators.py
"""Fase 5: apenas Newmark-β e HHT-α expostos (spec §3.A)."""
def test_solver_integrator_combo_has_two(qapp):
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    win = BoltAnalysisStudio()
    try:
        combos = win.findChildren(__import__('PyQt6.QtWidgets', fromlist=['QComboBox']).QComboBox)
        integ = [c for c in combos
                 if any("Newmark" in (c.itemText(i) or "") for i in range(c.count()))]
        assert integ, "combo de integrador não encontrado"
        for c in integ:
            items = [c.itemText(i) for i in range(c.count())]
            assert "Central Diff" not in items
            assert "RK4" not in items
            assert "Modal" not in items
    finally:
        win.close()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_gui_integrators.py -v` → FAIL

- [ ] **Step 3: Implementar**

`main_window.py:1101-1106` — reduzir a lista para os dois recomendados:

```python
            "Newmark-β",
            "HHT-α",
```
(remover `"Central Diff"`, `"Modal"`/`"Modal Superposition"`, `"RK4"`, `"Adaptive RK45"` da lista.) Fazer o mesmo em `:3235`:

```python
            ["Newmark-β", "HHT-α"]
```

Ajustar o texto de ajuda `:1144-1148` para descrever só os dois. (O `core/numerical/time_integration.py` mantém as classes — isto é só gating de UI.)

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_gui_integrators.py -v` → PASS
Syntax-check.

- [ ] **Step 5: Commit**

```bash
git add tests/test_gui_integrators.py src/bolt_analysis_studio/gui/main_window.py
git commit -m "$(cat <<'EOF'
feat(gui): expor so Newmark-beta e HHT-alpha (spec 3.A) (Fase 5.1)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 5.2: Model Tree profunda com contagens + menu de contexto

**Files:**
- Modify: `gui/chrome/widgets/model_tree.py` (contêineres aninhados; contagem; duplo-clique → módulo)
- Test: `tests/test_chrome_deep_tree.py`

**Interfaces:**
- Produces: `ModelTree.populate(model)` mostra `Contacts (n)`, `Loads (n)`, `Jobs (n)` com contagem no rótulo; nós de contato/carga como filhos.

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_chrome_deep_tree.py
"""Fase 5: árvore profunda com contagens por contêiner."""
class _FakeEl:
    def __init__(self, t): self.element_type = t

class _FakeModel:
    def __init__(self):
        self.name = "M16"
        self.elements = [_FakeEl("HEAD"), _FakeEl("NUT"),
                         _FakeEl("BEARING_HEAD"), _FakeEl("THREAD")]

def test_tree_counts_containers(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.model_tree import ModelTree
    tree = ModelTree()
    tree.populate(_FakeModel())
    labels = {tree.topLevelItem(i).text(0).split(" (")[0]:
              tree.topLevelItem(i).text(0) for i in range(tree.topLevelItemCount())}
    # contatos (BEARING_HEAD, THREAD) contam 2; membros/parafuso contam sob Model
    assert "(2)" in labels["Contacts"]
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_chrome_deep_tree.py -v` → FAIL

- [ ] **Step 3: Implementar**

Em `model_tree.py`, classificar elementos por contêiner e escrever a contagem no rótulo. Adicionar um conjunto de tipos de contato e reescrever `populate`:

```python
_CONTACT_TYPES = {"BEARING_HEAD", "BEARING_NUT", "FLANGE_FLANGE",
                  "WASHER_CONTACT", "GASKET_CONTACT", "GENERIC_CONTACT", "THREAD"}
```

```python
    def populate(self, model) -> None:
        self._model_node.takeChildren()
        self._tops["Contacts"].takeChildren()
        contacts = 0
        for el in getattr(model, "elements", []) or []:
            label = _element_label(el)
            if label in _CONTACT_TYPES:
                child = QTreeWidgetItem([label])
                child.setData(0, Qt.ItemDataRole.UserRole, ("element", el))
                self._tops["Contacts"].addChild(child)
                contacts += 1
            else:
                child = QTreeWidgetItem([label])
                child.setData(0, Qt.ItemDataRole.UserRole, ("element", el))
                self._model_node.addChild(child)
        self._set_count("Model", self._model_node.childCount())
        self._set_count("Contacts", contacts)
        self._model_node.setExpanded(True)

    def _set_count(self, name: str, n: int) -> None:
        base = name
        self._tops[name].setText(0, f"{base} ({n})" if n else base)
```

(Preservar `highlight_module`/`rebuild_icons`, que iteram sobre `self._tops` por chave — os `setText` com contagem não quebram porque as chaves de `self._tops` continuam sendo os nomes-base.)

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_chrome_deep_tree.py tests/test_chrome_*.py -v` → PASS
Syntax-check.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chrome_deep_tree.py src/bolt_analysis_studio/gui/chrome/widgets/model_tree.py
git commit -m "$(cat <<'EOF'
feat(chrome): model tree profunda com contagem por container (Fase 5.2)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 5.3: AutoComboBox com inferência + wizard auto-avança módulos (spec §3.B/§3.D)

**Files:**
- Modify: `gui/chrome/app_window.py` (`_open_wizard` → após criar, `switch_module("Model")` e sequência); `gui/chrome/widgets/auto_combo.py` (nada a mudar — só usar); adicionar uma função de inferência de exemplo consumida em Analysis
- Test: `tests/test_chrome_wizard_flow.py`

**Interfaces:**
- Consumes: `AutoComboBox(options, inference_fn)`.
- Produces: `ChromeWindow._after_wizard(model)` que popula a tree e navega Model→Loads→Analysis.

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_chrome_wizard_flow.py
"""Fase 5: após o wizard, o chrome popula a tree e vai para Model."""
class _FakeEl:
    element_type = "HEAD"
class _FakeModel:
    name = "wiz"
    elements = [_FakeEl()]

def test_after_wizard_navigates_and_populates(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        win._after_wizard(_FakeModel())
        assert win.current_module == "Model"
        assert win.tree._model_node.childCount() == 1
    finally:
        win.close()

def test_autocombo_infers_from_context(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.auto_combo import AutoComboBox
    combo = AutoComboBox(["Newmark-β", "HHT-α"],
                         inference_fn=lambda ctx: "HHT-α" if ctx.get("damping") else "Newmark-β")
    combo.set_context({"damping": True})
    assert combo.current_resolved_value() == "HHT-α"
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_chrome_wizard_flow.py -v` → FAIL (`_after_wizard` inexistente).

- [ ] **Step 3: Implementar**

`app_window.py` — extrair o pós-wizard e navegar:

```python
    def _after_wizard(self, model) -> None:
        self.app_state.model = model
        if model is not None:
            self.tree.populate(model)
            self.model_controller.sync_from_app_state()
        self.switch_module("Model")
        self.prompt.set_prompt("Modelo criado. Revise em Model → Loads → Analysis "
                               "e rode em Analysis.")
```

Trocar o corpo do `_open_wizard` (`:212-220`) para usar o novo hook:

```python
    def _open_wizard(self):
        try:
            from ..new_analysis_wizard import NewAnalysisWizard, build_model
            from PyQt6.QtWidgets import QDialog
            wiz = NewAnalysisWizard(self)
            if wiz.exec() == QDialog.DialogCode.Accepted:
                self._after_wizard(build_model(wiz.spec()))
        except Exception as exc:  # pragma: no cover - defensivo
            self.prompt.set_prompt(f"Wizard indisponivel: {exc}")
```

(O `AutoComboBox` já está pronto e testado; a task fixa o contrato de inferência via teste. A fiação campo-a-campo nos inspectores é follow-up de baixo risco — cada `AutoComboBox` recebe uma `inference_fn` que lê o `app_state.model`.)

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_chrome_wizard_flow.py tests/test_chrome_*.py -v` → PASS
Syntax-check.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chrome_wizard_flow.py src/bolt_analysis_studio/gui/chrome/app_window.py
git commit -m "$(cat <<'EOF'
feat(chrome): wizard auto-avanca p/ Model + contrato de inferencia (Fase 5.3)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 5.4: Promover o chrome a default; `--v1` como fallback

**Files:**
- Modify: `run_app.py:80-84` (flag), `:150-157` (dispatch)
- Test: `tests/test_run_app_flags.py`

**Interfaces:**
- Produces: sem flag → `ChromeWindow`; `--v1` → `BoltAnalysisStudio`.

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_run_app_flags.py
"""Fase 5: chrome vira default; --v1 é o fallback."""
import argparse
import importlib.util
from pathlib import Path

def _load_run_app():
    root = Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location("run_app", root / "run_app.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_default_is_chrome_flag_present():
    src = (Path(__file__).resolve().parent.parent / "run_app.py").read_text(encoding="utf-8")
    assert "--v1" in src
    # o default agora constrói ChromeWindow quando não há --v1
    assert "not args.v1" in src or "args.v1" in src
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_run_app_flags.py -v` → FAIL

- [ ] **Step 3: Implementar**

`run_app.py` — adicionar `--v1` e inverter o default. Substituir o bloco `--v2` (`:80-84`) mantendo-o como no-op de compat e adicionar:

```python
    parser.add_argument(
        '--v1',
        action='store_true',
        help='Launch the classic V1 7-tab window (fallback)'
    )
```

No dispatch (`:150-157`):

```python
        # Default agora é o chrome V2 (Abaqus-style). --v1 força a V1 clássica.
        if args.v1:
            from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
            window = BoltAnalysisStudio()
        else:
            from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
            window = ChromeWindow()
```

Ajustar o default de tema da Task 1.4: como o chrome é default, usar `engineering` quando não há preferência salva e sem `--theme` (independente de `--v2`):

```python
    elif not args.v1 and not Theme._PREFS_FILE.exists():
        saved = "engineering"
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_run_app_flags.py -v` → PASS
`python -c "import ast; ast.parse(open('run_app.py', encoding='utf-8').read()); print('OK')"`
Smoke manual (o executor roda): `python run_app.py --v1` abre a V1; `python run_app.py` abre o chrome.

- [ ] **Step 5: Commit**

```bash
git add tests/test_run_app_flags.py run_app.py
git commit -m "$(cat <<'EOF'
feat(run): chrome V2 vira default; --v1 fallback (Fase 5.4)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# FASE 6 — Polimento

### Task 6.1: Atalhos de teclado (módulos, fit, run) + readout de coords no prompt

**Files:**
- Modify: `gui/chrome/app_window.py` (`QShortcut` Ctrl+1..6, F, Ctrl+R; mouse-move do schematic → `prompt.set_coords`)
- Test: `tests/test_chrome_shortcuts.py`

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_chrome_shortcuts.py
"""Fase 6: atalhos de módulo e run registrados."""
def test_module_shortcuts_registered(qapp):
    from PyQt6.QtGui import QKeySequence
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        seqs = {s.key().toString() for s in win.findChildren(__import__(
            'PyQt6.QtGui', fromlist=['QShortcut']).QShortcut)}
        assert "Ctrl+1" in seqs
        assert "Ctrl+R" in seqs
    finally:
        win.close()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_chrome_shortcuts.py -v` → FAIL

- [ ] **Step 3: Implementar**

`app_window.py` — no fim do `__init__`, registrar atalhos:

```python
        from PyQt6.QtGui import QShortcut, QKeySequence
        for i, m in enumerate(MODULES, start=1):
            QShortcut(QKeySequence(f"Ctrl+{i}"), self,
                      activated=lambda name=m: self.switch_module(name))
        QShortcut(QKeySequence("Ctrl+R"), self,
                  activated=lambda: self.module_bar.run_requested.emit()
                  if self.module_bar._run_btn.isEnabled() else None)
        QShortcut(QKeySequence("F"), self, activated=self.viewport_toolbar._fit)
```

Readout de coords: conectar o hover do schematic ao prompt. Após montar o `model_controller`, se o schematic expõe `mouse_moved`/`scene_pos` usar; caso contrário, instalar um handler simples via `viewport().installEventFilter` é fora de escopo — manter o mínimo: quando `_fit` roda, escrever `prompt.set_coords("")`. (O readout completo de x/y é follow-up; o teste cobre só os atalhos.)

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_chrome_shortcuts.py tests/test_chrome_*.py -v` → PASS
Syntax-check.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chrome_shortcuts.py src/bolt_analysis_studio/gui/chrome/app_window.py
git commit -m "$(cat <<'EOF'
feat(chrome): atalhos Ctrl+1..6 / Ctrl+R / F (Fase 6.1)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 6.2: Empty states com direção (sem modelo / sem resultados)

**Files:**
- Modify: `gui/chrome/app_window.py` (prompt quando `app_state.model is None`; badge quando sem resultados)
- Test: `tests/test_chrome_empty_states.py`

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_chrome_empty_states.py
"""Fase 6: estados vazios orientam a próxima ação."""
def test_empty_model_prompts_wizard(qapp):
    from bolt_analysis_studio.core.app_state import get_app_state
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    st = get_app_state()
    st._model = None
    win = ChromeWindow(app_state=st)
    try:
        win.refresh_empty_state()
        assert "Ctrl+Shift+N" in win.prompt._prompt.text()
    finally:
        win.close()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_chrome_empty_states.py -v` → FAIL

- [ ] **Step 3: Implementar**

`app_window.py`:

```python
    def refresh_empty_state(self) -> None:
        if getattr(self.app_state, "model", None) is None:
            self.prompt.set_prompt("Nenhum modelo carregado — Ctrl+Shift+N abre o "
                                   "wizard de nova análise.")
```

Chamar `self.refresh_empty_state()` ao fim do `__init__` (após os atalhos) e no `_on_model_changed`.

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_chrome_empty_states.py tests/test_chrome_*.py -v` → PASS
Syntax-check.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chrome_empty_states.py src/bolt_analysis_studio/gui/chrome/app_window.py
git commit -m "$(cat <<'EOF'
feat(chrome): empty state orienta o wizard (Fase 6.2)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 6.3: Idioma único no chrome (prompts/menus em inglês) + splash restyle

**Files:**
- Modify: `gui/chrome/app_window.py` (`_PROMPTS`, menus, mensagens em inglês), `gui/splash.py` (paleta nova)
- Test: `tests/test_chrome_language.py`

Nota: **decisão do professor** (spec §6.2) — este task assume inglês no chrome. Se optar por português, inverter os literais. Manter tooltips/help bilíngues.

- [ ] **Step 1: Escrever o teste**

```python
# tests/test_chrome_language.py
"""Fase 6: prompts e menus do chrome num idioma só (inglês)."""
def test_module_prompts_in_english(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import _PROMPTS
    joined = " ".join(_PROMPTS.values()).lower()
    # sem marcadores pt claros nos prompts de módulo
    for pt in ("adicione", "configure o carregamento", "inspecione", "relatório"):
        assert pt not in joined

def test_file_menu_labels_english(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    try:
        file_menu = next(m.menu() for m in win.menuBar().actions() if m.text() == "File")
        labels = [a.text() for a in file_menu.actions() if a.text()]
        assert any("New Analysis" in L for L in labels)
    finally:
        win.close()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_chrome_language.py -v` → FAIL

- [ ] **Step 3: Implementar**

`app_window.py` — traduzir `_PROMPTS` (`:25-32`):

```python
_PROMPTS = {
    "Model": "Add or select elements in the viewport.",
    "Contacts": "Define contacts and friction/wear models.",
    "Loads": "Configure global and per-element loading.",
    "Analysis": "Define steps and run the analysis.",
    "Results": "Inspect plots and validation overlays.",
    "Report": "Assemble the report and choose a format.",
}
```

Traduzir os rótulos de menu (`:117,121,127,129`): `"Nova Análise…"`→`"New Analysis…"`, `"Sair"`→`"Quit"`, `"Reports de Validação (114 casos)"`→`"Validation reports (114 cases)"`, `"Prompt de intake (IA) — copiar"`→`"Copy AI intake prompt"`. Traduzir as mensagens de `_ACTION_HELP`, `_after_wizard`, `refresh_empty_state`, `set_run_enabled` para inglês (manter o sentido). O `statusBar` `"Projeto: … Modulo: … Job:"` → `"Project: … Module: … Job:"`.

`splash.py` — se houver hexes hardcoded, roteá-los via `Theme.*`; garantir que o texto de versão diga "V2".

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_chrome_language.py tests/test_chrome_*.py -v` → PASS
Syntax-check.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chrome_language.py src/bolt_analysis_studio/gui/chrome/app_window.py src/bolt_analysis_studio/gui/splash.py
git commit -m "$(cat <<'EOF'
feat(chrome): idioma unico (ingles) no chrome + splash restyle (Fase 6.3)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Validação final (após todas as fases)

- [ ] Suíte de GUI/chrome verde:
  `python -m pytest tests/test_gui_v1_chrome.py tests/test_gui_theme_engineering.py tests/test_gui_icons.py tests/test_chrome_*.py tests/test_gui_integrators.py tests/test_run_app_flags.py tests/test_schematic_stamp.py -v`
- [ ] Nenhuma regressão nos testes de chrome pré-existentes: `python -m pytest tests/test_main_window_chrome.py tests/test_chrome_model_module.py tests/test_chrome_validation_module.py -v`
- [ ] Smoke manual (executor): `python run_app.py` (chrome, Engineering Dark, ícones, message area, Run em Analysis, Results Run+Validation, Report); `python run_app.py --v1` (V1 sem emoji).
- [ ] Capturar screenshots antes/depois em `docs/ui/` (o repo não tinha nenhuma imagem de UI) para o manual e o PR.

---

## Notas de auto-revisão (cobertura vs spec 2026-07-17)

- §4 Quick wins V1 → Fase 0 (0.1–0.3). §1.1 paleta → 1.1. §1.2 tipografia/densidade → 1.3. §1.3 ícones → 2.1–2.3. §1.5 gradiente+carimbo → 3.3. §2.1 módulos → 4.1–4.3. §2.2 message area/viewport toolbar/contexto → 3.1–3.2. §2.3 tree profunda → 5.2. §2.4 inspector único → **parcial**: os módulos schematic (Model/Contacts/Loads) permanecem no inspector rico da V1; a unificação total em `CollapsibleGroup` é follow-up de maior porte (marcado, não incluído como task para não inflar risco). §2.5 prompts → 3.4. §3.2 wizard/auto-defaults → 5.3 (contrato; fiação campo-a-campo é follow-up). §3.4 plots → 4.2 + 0.3 (toolbars). §5 faseamento → estrutura deste plano. Integradores 5→2 (spec V2 §3.A) → 5.1. Chrome default → 5.4. Idioma único → 6.3.
- **Decisões do professor (spec §6)** que este plano assume por default e podem ser invertidas sem re-planejar: Engineering Dark como default do chrome (1.4/5.4); inglês no chrome (6.3). As demais (fonte dos ícones = SVG próprio; console Python adiado; V1 aposentável) estão respeitadas.
