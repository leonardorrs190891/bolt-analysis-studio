# Explorador Interativo de Variáveis — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Gerar um documento estático interativo — uma página HTML por campo de `JointMaterial` (80) + índice — com a curva-padrão de afrouxamento, um slider (ou seletor para modos) que a reforma ao vivo, texto de física bilíngue, equação e referências de literatura.

**Architecture:** Um gerador Python (`New_Theory/build_variable_explorer.py`) enumera uma tabela `VARIABLE_SPECS` (uma entrada por campo), roda o **engine real** via `calibration.server.handle_simulate` varrendo cada variável, e renderiza HTML 100% standalone (CSS+JS+dados inline; plotter canvas vanilla). Nenhuma física em JS — o engine é a fonte única.

**Tech Stack:** Python 3 (stdlib + numpy já usados no projeto), HTML/CSS/JS vanilla (zero dependência externa, convenção do report v3), pytest.

## Global Constraints

- **Encoding utf-8** em todo I/O de arquivo (Windows charmap quebra sem isso).
- **Syntax-check via `python -c "import ast; ast.parse(open(P,encoding='utf-8').read())"`** após cada edição de `.py`, antes de rodar teste.
- **Nenhuma física reimplementada em JS** — todas as curvas vêm de `handle_simulate`.
- **Zero dependência externa no HTML** (sem CDN): CSS+JS+dados inline em cada arquivo.
- **`tests/conftest.py` já põe `src/` no `sys.path`** (não há editable install neste ambiente).
- **Cobre TODOS os 80 campos** de `JointMaterial.__dataclass_fields__` — sem exceção.
- **Bilíngue PT/EN** com toggle; **tema claro/escuro** com toggle (localStorage).
- **Commits frequentes**, staging explícito por arquivo (sessão paralela do OneDrive; nunca `git add -A`).
- Saída em `New_Theory/variable_explorer/`.
- **Payload do `handle_simulate`** (contrato fixo):
  - `geom` = `{A_s, L_eff, d_2, pitch, r_bearing, A_contact}` (`_GEOM_KEYS`)
  - `loading` = `{F0_init, F_amp, theta, freq, N, delta_amp, D_init}` (`_LOAD_KEYS`)
  - `mat` = qualquer subconjunto de campos de `JointMaterial` (filtrado por `__dataclass_fields__`)
  - `segments` = `{N_I, N_II}`
  - retorna `{"curve": {"N": [...], "ratio": [...]}, "decomposition": {...}, ...}`
- **Baselines (verbatim do tuner):**
  - **geom M16:** `A_s=157e-6, L_eff=0.050, d_2=14.70e-3, pitch=2.0e-3, r_bearing=12e-3, A_contact=1.0e-4`
  - **transverse (curva-padrão principal):** `F0_init=50000, F_amp=20000, theta=90, freq=0.5, N=2500, delta_amp=0.5e-3, D_init=0`, `segments={N_I:50, N_II:500}`
  - **axial (modo força):** igual, mas `theta=0, delta_amp=0, F_amp=10000, freq=30`
  - **creep (eixo em minutos Li2022):** transverse com `freq=1/60`

---

## File Structure

- `New_Theory/build_variable_explorer.py` — **gerador**. Contém: `VarSpec` (dataclass), `BASELINES` (builders de payload), `VARIABLE_SPECS` (lista de 80), helpers de validação, `sweep_variable`, `render_variable_page`, `render_index`, `build`, `main`. Também as strings-template de CSS/JS inline.
- `New_Theory/variable_explorer/` — **saída** gerada: `index.html` + `var_<name>.html` × 80.
- `tests/test_variable_explorer.py` — testes (registry-truth, cobertura, slider-vivo, integração, smoke de render).

Um arquivo `.py` só: o gerador é coeso (schema + dados + render) e cabe em contexto; separar template/dados/render em módulos seria over-engineering para um script de doc.

---

### Task 1: Esqueleto — `VarSpec`, baselines, validação, teste registry-truth

**Files:**
- Create: `New_Theory/build_variable_explorer.py`
- Create: `tests/test_variable_explorer.py`

**Interfaces:**
- Produces:
  - `VarSpec` dataclass com campos: `name:str, symbol:str, unit:str, group:str, category:str` (`"physical"|"form"|"numerical"|"mode"`), `sweep:tuple|None` (`(lo,hi,n,scale)`, `scale∈{"lin","log"}`), `choices:list|None` (para modes/bools), `context:dict` (`{"baseline":str, "overrides":dict}`), `physics_pt:str, physics_en:str, equation:str, anchor_key:str|None, lessons:list[str], refs:list[tuple], related:list[str], negligible:bool`
  - `VARIABLE_SPECS: list[VarSpec]` (começa vazia; preenchida nas Tasks 6+)
  - `all_field_names() -> set[str]` (de `JointMaterial.__dataclass_fields__`)
  - `spec_names() -> set[str]`
  - `missing_fields() -> set[str]` (`all_field_names() - spec_names()`)
  - `validate_specs() -> None` (raise se algum `name` não é campo, se há duplicata, ou se `sweep` e `choices` ambos None/ambos setados)
  - `BASELINES: dict[str, callable]` — `BASELINES[id]()` retorna payload base `{"geom":..., "loading":..., "segments":...}` (sem `mat`)

- [ ] **Step 1: Escrever o teste que falha**

```python
# tests/test_variable_explorer.py
import importlib.util, pathlib, sys
import dataclasses as dc

ROOT = pathlib.Path(__file__).resolve().parents[1]
GEN = ROOT / "New_Theory" / "build_variable_explorer.py"

def _load():
    spec = importlib.util.spec_from_file_location("build_variable_explorer", GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_spec_names_are_real_fields():
    mod = _load()
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
    fields = set(JointMaterial.__dataclass_fields__)
    for s in mod.VARIABLE_SPECS:
        assert s.name in fields, f"{s.name} nao e campo de JointMaterial"
    # sem duplicatas
    names = [s.name for s in mod.VARIABLE_SPECS]
    assert len(names) == len(set(names)), "spec duplicado"

def test_baselines_build_valid_payloads():
    mod = _load()
    for bid in ("transverse", "axial", "creep"):
        p = mod.BASELINES[bid]()
        assert set(p["geom"]) == {"A_s","L_eff","d_2","pitch","r_bearing","A_contact"}
        assert set(p["loading"]) == {"F0_init","F_amp","theta","freq","N","delta_amp","D_init"}
        assert set(p["segments"]) == {"N_I","N_II"}
```

- [ ] **Step 2: Rodar e verificar que falha**

Run: `python -m pytest tests/test_variable_explorer.py -q`
Expected: FAIL — `ModuleNotFoundError`/`FileNotFoundError` (gerador não existe).

- [ ] **Step 3: Implementar o esqueleto**

```python
# New_Theory/build_variable_explorer.py
"""Gera o Explorador Interativo de Variaveis (docs).

Uma pagina HTML por campo de JointMaterial + indice. Curvas pre-computadas
pelo engine REAL (calibration.server.handle_simulate) — nenhuma fisica em JS.
Ver docs/superpowers/specs/2026-07-12-variable-explorer-design.md
"""
from __future__ import annotations
import dataclasses as dc
import pathlib, sys

_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial

OUTDIR = _ROOT / "New_Theory" / "variable_explorer"

_GEOM_M16 = dict(A_s=157e-6, L_eff=0.050, d_2=14.70e-3, pitch=2.0e-3,
                 r_bearing=12e-3, A_contact=1.0e-4)
_SEG = dict(N_I=50, N_II=500)

def _transverse():
    return dict(geom=dict(_GEOM_M16),
                loading=dict(F0_init=50000.0, F_amp=20000.0, theta=90.0,
                             freq=0.5, N=2500, delta_amp=0.5e-3, D_init=0.0),
                segments=dict(_SEG))

def _axial():
    p = _transverse()
    p["loading"].update(theta=0.0, delta_amp=0.0, F_amp=10000.0, freq=30.0)
    return p

def _creep():
    p = _transverse()
    p["loading"].update(freq=1.0/60.0)
    return p

BASELINES = {"transverse": _transverse, "axial": _axial, "creep": _creep}


@dc.dataclass
class VarSpec:
    name: str
    symbol: str
    unit: str
    group: str
    category: str            # physical | form | numerical | mode
    context: dict            # {"baseline": str, "overrides": dict}
    physics_pt: str
    physics_en: str
    equation: str
    sweep: tuple | None = None      # (lo, hi, n, scale)  scale in {lin, log}
    choices: list | None = None     # p/ modes/bools
    anchor_key: str | None = None
    lessons: list = dc.field(default_factory=list)
    refs: list = dc.field(default_factory=list)     # [(pt, en, fonte)]
    related: list = dc.field(default_factory=list)
    negligible: bool = False


VARIABLE_SPECS: list[VarSpec] = []   # preenchida nas Tasks 6+


def all_field_names() -> set:
    return set(JointMaterial.__dataclass_fields__)

def spec_names() -> set:
    return {s.name for s in VARIABLE_SPECS}

def missing_fields() -> set:
    return all_field_names() - spec_names()

def validate_specs() -> None:
    fields = all_field_names()
    seen = set()
    for s in VARIABLE_SPECS:
        if s.name not in fields:
            raise ValueError(f"VarSpec '{s.name}' nao e campo de JointMaterial")
        if s.name in seen:
            raise ValueError(f"VarSpec duplicado: {s.name}")
        seen.add(s.name)
        if (s.sweep is None) == (s.choices is None):
            raise ValueError(f"'{s.name}': setar exatamente um de sweep/choices")
```

- [ ] **Step 4: Syntax-check + rodar o teste**

Run: `python -c "import ast; ast.parse(open('New_Theory/build_variable_explorer.py',encoding='utf-8').read()); print('OK')"`
Run: `python -m pytest tests/test_variable_explorer.py -q`
Expected: PASS (2 testes; `VARIABLE_SPECS` vazia → registry-truth passa trivialmente).

- [ ] **Step 5: Commit**

```bash
git add New_Theory/build_variable_explorer.py tests/test_variable_explorer.py
git commit -m "feat(explorer): esqueleto VarSpec + baselines + registry-truth"
```

---

### Task 2: Helper de simulação — `sweep_variable`

**Files:**
- Modify: `New_Theory/build_variable_explorer.py`
- Test: `tests/test_variable_explorer.py`

**Interfaces:**
- Consumes: `VarSpec`, `BASELINES`, `handle_simulate`
- Produces:
  - `sweep_values(spec) -> list` — a grade de valores (linspace/logspace ou `choices`)
  - `simulate(spec, value) -> dict` — payload = baseline + `context.overrides` + `{spec.name: value}` → `handle_simulate` → `{"N": [...], "ratio": [...]}`
  - `sweep_variable(spec) -> dict` — `{"default": <default do campo>, "values": [...], "curves": [{"value","N","ratio"} ...], "baseline_idx": <indice do valor mais proximo do default, ou None>}`

- [ ] **Step 1: Escrever o teste que falha**

```python
def test_sweep_variable_moves_curve():
    mod = _load()
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
    # spec ad-hoc de emb_depth (nao depende de VARIABLE_SPECS ainda)
    s = mod.VarSpec(
        name="emb_depth", symbol="d", unit="m", group="embedding",
        category="physical",
        context={"baseline": "transverse", "overrides": {}},
        physics_pt="x", physics_en="x", equation="x",
        sweep=(5e-6, 60e-6, 6, "lin"))
    res = mod.sweep_variable(s)
    assert res["default"] == JointMaterial().emb_depth
    assert len(res["curves"]) == 6
    for c in res["curves"]:
        assert c["ratio"][0] == 1.0
        assert all(r <= 1.0001 for r in c["ratio"])
    # slider-vivo: curvas NAO sao todas iguais
    finals = [c["ratio"][-1] for c in res["curves"]]
    assert max(finals) - min(finals) > 1e-3
```

- [ ] **Step 2: Rodar e verificar que falha**

Run: `python -m pytest tests/test_variable_explorer.py::test_sweep_variable_moves_curve -q`
Expected: FAIL — `AttributeError: module has no attribute 'sweep_variable'`.

- [ ] **Step 3: Implementar**

```python
# adicionar imports no topo:
import numpy as np
from bolt_analysis_studio.calibration.server import handle_simulate

def sweep_values(spec: VarSpec) -> list:
    if spec.choices is not None:
        return list(spec.choices)
    lo, hi, n, scale = spec.sweep
    if scale == "log":
        return [float(x) for x in np.logspace(np.log10(lo), np.log10(hi), int(n))]
    return [float(x) for x in np.linspace(lo, hi, int(n))]

def simulate(spec: VarSpec, value) -> dict:
    base = BASELINES[spec.context["baseline"]]()
    mat = dict(spec.context.get("overrides", {}))
    mat[spec.name] = value
    payload = dict(base)
    payload["mat"] = mat
    out = handle_simulate(payload)
    # handle_simulate devolve np.float64 -> coagir p/ float/int nativo,
    # senao json.dumps (no render) quebra.
    return {"N": [int(n) for n in out["curve"]["N"]],
            "ratio": [float(r) for r in out["curve"]["ratio"]]}

def sweep_variable(spec: VarSpec) -> dict:
    default = getattr(JointMaterial(), spec.name)
    values = sweep_values(spec)
    curves = [{"value": v, **simulate(spec, v)} for v in values]
    baseline_idx = None
    if spec.sweep is not None and isinstance(default, (int, float)):
        diffs = [abs(float(v) - float(default)) for v in values]
        baseline_idx = int(min(range(len(diffs)), key=diffs.__getitem__))
    return {"default": default, "values": values, "curves": curves,
            "baseline_idx": baseline_idx}
```

- [ ] **Step 4: Syntax-check + rodar o teste**

Run: `python -c "import ast; ast.parse(open('New_Theory/build_variable_explorer.py',encoding='utf-8').read()); print('OK')"`
Run: `python -m pytest tests/test_variable_explorer.py::test_sweep_variable_moves_curve -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add New_Theory/build_variable_explorer.py tests/test_variable_explorer.py
git commit -m "feat(explorer): sweep_variable roda handle_simulate por valor"
```

---

### Task 3: Render de página de variável — template, plotter inline, PT/EN, tema

**Files:**
- Modify: `New_Theory/build_variable_explorer.py`
- Test: `tests/test_variable_explorer.py`

**Interfaces:**
- Consumes: `VarSpec`, `sweep_variable`
- Produces:
  - `render_variable_page(spec, sweep_result, prev_name=None, next_name=None) -> str` (HTML completo standalone)
  - Constantes de template `_PLOTTER_JS: str` (canvas vanilla: eixos ciclo×F/F₀, grade, curva atual em destaque, curva-default de referência, fantasmas translúcidos das varreduras) e `_BASE_CSS: str`.

**Detalhes do HTML gerado (o template deve produzir):**
- `<!doctype html>` + `<meta charset=utf-8>` + `<title>`.
- Bloco `<script>` com `const DATA = {...}` (JSON de `sweep_result` + metadados do spec).
- Controle: `<input type=range>` (sweep) OU `<select>` (choices/modes/bools). O `oninput` chama `redraw(idx)` (só troca qual curva está em destaque — todas já pré-computadas).
- Dois blocos de texto marcados `data-lang="pt"` / `data-lang="en"`; botão toggle PT/EN que alterna `document.documentElement.dataset.lang` e persiste em `localStorage`.
- Botão toggle tema que alterna `data-theme` e persiste em `localStorage`; CSS cobre claro/escuro.
- `<canvas>` + o `_PLOTTER_JS` inline (roda no load, desenha idx default).
- Seções: cabeçalho (nome/símbolo/unidade/grupo/categoria/default/faixa), gráfico+controle, física (PT+EN), equação, referências (âncora + L# + refs curadas), navegação prev/next + link índice.
- Cross-links `related`: renderiza "só age com [[X]]" como `<a href="var_X.html">`.

- [ ] **Step 1: Escrever o teste que falha**

```python
from html.parser import HTMLParser

def _parse_ok(html):
    class P(HTMLParser):
        pass
    P().feed(html)   # nao levanta => bem-formado o bastante

def test_render_variable_page_smoke():
    mod = _load()
    s = mod.VarSpec(
        name="emb_depth", symbol="d", unit="m", group="embedding",
        category="physical",
        context={"baseline": "transverse", "overrides": {}},
        physics_pt="Assentamento plastico das asperezas.",
        physics_en="Plastic settling of asperities.",
        equation="delta_emb(N)=d(1-e^{-N/N_emb})",
        sweep=(5e-6, 60e-6, 6, "lin"),
        refs=[("VDI 2230", "VDI 2230", "vdi2230")])
    res = mod.sweep_variable(s)
    html = mod.render_variable_page(s, res, prev_name=None, next_name="C_creep")
    _parse_ok(html)
    assert "<canvas" in html
    assert "const DATA" in html
    assert 'data-lang="pt"' in html and 'data-lang="en"' in html
    assert "Assentamento plastico" in html and "Plastic settling" in html
    assert "var_C_creep.html" in html          # link next
    assert "<input" in html or "<select" in html
```

- [ ] **Step 2: Rodar e verificar que falha**

Run: `python -m pytest tests/test_variable_explorer.py::test_render_variable_page_smoke -q`
Expected: FAIL — `AttributeError: render_variable_page`.

- [ ] **Step 3: Implementar** o template. Escrever `_BASE_CSS`, `_PLOTTER_JS` (canvas 2D: mapear N→x, ratio→y; desenhar grade, eixos rotulados, fantasmas com `globalAlpha` baixo, curva-default tracejada, curva ativa sólida; `redraw(idx)` só re-renderiza) e `render_variable_page` montando o HTML com `json.dumps(DATA)`. Usar `json` (import no topo). O controle é `<input type=range min=0 max=len-1>` quando `spec.sweep`, senão `<select>` com uma option por choice. Persistência de idioma/tema via `localStorage` no JS inline.

*(Código completo do template — ~180 linhas de CSS+JS+f-string — é escrito nesta task; segue o padrão do report v3 `New_Theory/validation_html`. Não há placeholder: o engenheiro produz o HTML que satisfaz as asserções acima e os "Detalhes do HTML gerado".)*

- [ ] **Step 4: Syntax-check + rodar o teste**

Run: `python -c "import ast; ast.parse(open('New_Theory/build_variable_explorer.py',encoding='utf-8').read()); print('OK')"`
Run: `python -m pytest tests/test_variable_explorer.py::test_render_variable_page_smoke -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add New_Theory/build_variable_explorer.py tests/test_variable_explorer.py
git commit -m "feat(explorer): template de pagina (plotter canvas inline, PT/EN, tema)"
```

---

### Task 4: Render do índice + `build` + `main`

**Files:**
- Modify: `New_Theory/build_variable_explorer.py`
- Test: `tests/test_variable_explorer.py`

**Interfaces:**
- Consumes: `VarSpec`, `render_variable_page`, `sweep_variable`, `OUTDIR`
- Produces:
  - `render_index(specs) -> str` — agrupa por `spec.group`; cada variável = link `var_<name>.html` + gancho + categoria; descreve a curva-padrão. PT/EN + tema.
  - `build(specs, outdir) -> list[pathlib.Path]` — valida, roda `sweep_variable` por spec, escreve `var_<name>.html` (prev/next encadeados na ordem de `specs`) + `index.html`. `encoding="utf-8"`.
  - `main()` — `validate_specs()`, avisa `missing_fields()` se houver, `build(VARIABLE_SPECS, OUTDIR)`.

- [ ] **Step 1: Escrever o teste que falha**

```python
def test_build_writes_files(tmp_path):
    mod = _load()
    specs = [
        mod.VarSpec(name="emb_depth", symbol="d", unit="m", group="embedding",
                    category="physical",
                    context={"baseline":"transverse","overrides":{}},
                    physics_pt="a", physics_en="a", equation="e",
                    sweep=(5e-6,60e-6,4,"lin")),
        mod.VarSpec(name="C_creep", symbol="C", unit="m/dec", group="creep",
                    category="physical",
                    context={"baseline":"creep","overrides":{}},
                    physics_pt="b", physics_en="b", equation="e",
                    sweep=(1e-12,1e-10,4,"log")),
    ]
    paths = mod.build(specs, tmp_path)
    assert (tmp_path / "index.html").exists()
    assert (tmp_path / "var_emb_depth.html").exists()
    assert (tmp_path / "var_C_creep.html").exists()
    idx = (tmp_path / "index.html").read_text(encoding="utf-8")
    _parse_ok(idx)
    assert "var_emb_depth.html" in idx and "var_C_creep.html" in idx
```

- [ ] **Step 2: Rodar e verificar que falha**

Run: `python -m pytest tests/test_variable_explorer.py::test_build_writes_files -q`
Expected: FAIL — `AttributeError: build`.

- [ ] **Step 3: Implementar** `render_index`, `build`, `main`, e `if __name__ == "__main__": main()`.

- [ ] **Step 4: Syntax-check + rodar o teste**

Run: `python -c "import ast; ast.parse(open('New_Theory/build_variable_explorer.py',encoding='utf-8').read()); print('OK')"`
Run: `python -m pytest tests/test_variable_explorer.py::test_build_writes_files -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add New_Theory/build_variable_explorer.py tests/test_variable_explorer.py
git commit -m "feat(explorer): render do indice + build + main CLI"
```

---

## Tasks de conteúdo (6–21): preencher `VARIABLE_SPECS`

**Padrão comum a todas:** cada task adiciona as entradas `VarSpec` do batch a `VARIABLE_SPECS`, com:
- `context.overrides` = os companheiros mínimos que deixam o slider vivo (ver tabela do batch);
- `sweep`/`choices` = faixa da tabela;
- `physics_pt`/`physics_en` = 1–2 parágrafos, redigidos a partir da seção citada de `New_Theory/MODEL_MATH_REFERENCE.md` + a nota do `CLAUDE.md` + o comentário do campo em `dynamic_stiffness_analyzer.py`;
- `equation` = da seção citada;
- `anchor_key` = chave em `knowledge_base.anchor_priors()` quando existir (`mu_dry`, `conform_pressure_exp`, `C_creep_por_par`, `emb_depth`, `N_emb`, `F_amp_ratio`, `fat_sigma_endurance`), senão `None`;
- `lessons` = L# relevantes (de `knowledge_base.lessons()`), `refs` = citações de `curve_library/apparatus_notes/` / specs / `BAS_V2_papers/`;
- `related` = campo(s) primário(s) para cross-link.

**Teste comum a cada batch** (adicionar um teste parametrizado por batch):

```python
import pytest
def _specs_of(mod, group):
    return [s for s in mod.VARIABLE_SPECS if s.group == group]

@pytest.mark.parametrize("group", ["embedding"])   # << trocar por batch
def test_batch_present_and_live(group):
    mod = _load()
    fields_expected = BATCH_FIELDS[group]           # dict no topo do teste
    got = {s.name for s in _specs_of(mod, group)}
    assert got == fields_expected
    for s in _specs_of(mod, group):
        if s.negligible:
            continue
        res = mod.sweep_variable(s)
        finals = [c["ratio"][-1] for c in res["curves"]]
        assert max(finals) - min(finals) > 1e-4, f"slider morto: {s.name}"
```

Cada task abaixo: (1) adicionar as entradas; (2) `ast.parse` OK; (3) atualizar `BATCH_FIELDS` + rodar o teste do batch → PASS; (4) commit `feat(explorer): conteudo <grupo>`.

> **Exemplar totalmente resolvido:** o **Batch B2 (Creep, Task 7)** abaixo traz o código Python completo das entradas como modelo de estilo/densidade; os demais batches trazem a tabela por-campo (contexto, sweep, fonte, related) — o engenheiro redige a prosa PT/EN a partir das fontes citadas, seguindo o exemplar.

---

### Task 6 (B1): Embedding — 9 campos

**group:** `embedding`

| campo | symbol/unit | category | context (baseline · overrides) | sweep / choices | fonte (MMR §, anchor, L#) | related |
|---|---|---|---|---|---|---|
| `emb_depth` | δ_∞ / m | physical | transverse · {} | (5e-6, 60e-6, 15, lin) | §4.1; anchor `emb_depth`; L24 | — |
| `N_emb` | N_emb / ciclos | form | transverse · {} | (5, 200, 15, log) | §4.1; anchor `N_emb` | `emb_depth` |
| `emb_conform_exp` | n / – | form | transverse · {emb_conform_exp acionado; nenhum companheiro extra} | (0, 3, 13, lin) | §6; CLAUDE.md conformação | `p_ref_emb` |
| `p_ref_emb` | p_ref / Pa | form | transverse · {emb_conform_exp:2.0} | (5e7, 4e8, 15, log) | §6 | `emb_conform_exp` |
| `creep_conform_exp` | n_slow / – | form | transverse · {} | (0, 3, 13, lin) | §6 slow-tail | `p_ref_emb` |
| `emb_amp_exp` | q_amp / – | form | axial · {} | (0, 4, 13, lin) | §6 ρ-unif; L18 | `rho_ref_emb` |
| `rho_ref_emb` | ρ_ref / – | form | axial · {emb_amp_exp:3.0} | (0.2, 1.2, 15, lin) | §6 ρ-unif | `emb_amp_exp` |
| `emb_load_frac` | – | form | transverse · {} | (0, 1.0, 15, lin) | §6; L19 Lu | — |
| `emb_slip_gate` | q / – | form | transverse · {emb_load_frac:0.3} | (0, 4, 13, lin) | §6 bedding slip-gated | `emb_load_frac` |

Steps: adicionar as 9 entradas; `BATCH_FIELDS["embedding"]={...}`; rodar teste do batch (`test_batch_present_and_live[embedding]`) → PASS; commit.

---

### Task 7 (B2): Creep — 2 campos — **EXEMPLAR (código completo)**

**group:** `creep`

- [ ] **Step 1: Adicionar as entradas** (modelo de densidade para os demais batches):

```python
VARIABLE_SPECS += [
    VarSpec(
        name="C_creep", symbol="C_creep", unit="m/(log-decada·Pa)",
        group="creep", category="physical",
        context={"baseline": "creep", "overrides": {}},
        sweep=(1e-12, 1e-10, 15, "log"),
        equation="delta_creep(t) = C_creep * F_0 * log(t/t_0 + 1)",
        physics_pt=(
            "Creep logaritmico (Norton-Bailey) da interface sob a pre-carga: o "
            "assentamento lento cresce com log do tempo e escala com F_0. Aumentar "
            "C_creep aprofunda a cauda lenta da curva (perda continuada de F/F_0 "
            "muito depois do assentamento inicial). E POR PAR tribologico, nao "
            "universal: a ancora 304SS (9.9e-13) e o fit da âncora interna (1.2e-11) tem ICs "
            "disjuntos — o bloco 'shared' canonico mantem o valor da âncora interna."),
        physics_en=(
            "Logarithmic (Norton-Bailey) creep of the interface under preload: the "
            "slow settling grows with log-time and scales with F_0. Raising C_creep "
            "deepens the slow tail of the curve (continued F/F_0 loss long after "
            "initial embedding). It is PER tribological pair, not universal: the "
            "304SS anchor (9.9e-13) and the âncora interna fit (1.2e-11) have disjoint CIs — "
            "the canonical 'shared' block keeps the âncora interna value."),
        anchor_key="C_creep_por_par",
        lessons=[],
        refs=[("Li 2022 (creep estatico, ancora)", "Li 2022 (static creep, anchor)",
               "curve_library/apparatus_notes (li2022)"),
              ("§4.7 MODEL_LEGITIMACY (per-par)", "§4.7 MODEL_LEGITIMACY (per-pair)",
               "New_Theory/MODEL_LEGITIMACY.md")],
        related=["t_0", "creep_conform_exp"]),
    VarSpec(
        name="t_0", symbol="t_0", unit="s", group="creep", category="form",
        context={"baseline": "creep", "overrides": {}},
        sweep=(0.1, 100.0, 15, "log"),
        equation="delta_creep(t) = C_creep * F_0 * log(t/t_0 + 1)",
        physics_pt=(
            "Tempo de referencia do creep logaritmico: desloca o inicio da escala "
            "log. Valores menores adiantam a cauda de creep; efeito modesto frente "
            "a C_creep."),
        physics_en=(
            "Reference time of the logarithmic creep: shifts the onset of the log "
            "scale. Smaller values bring the creep tail earlier; modest effect "
            "compared to C_creep."),
        anchor_key=None, lessons=[],
        refs=[("§4.2 MODEL_MATH_REFERENCE", "§4.2 MODEL_MATH_REFERENCE",
               "New_Theory/MODEL_MATH_REFERENCE.md")],
        related=["C_creep"]),
]
```

- [ ] **Step 2: `ast.parse` OK.**
- [ ] **Step 3: `BATCH_FIELDS["creep"]={"C_creep","t_0"}`; rodar `test_batch_present_and_live[creep]`** → PASS.
- [ ] **Step 4: Commit** `feat(explorer): conteudo creep (exemplar)`.

---

### Task 8 (B3): Wear — 5 campos

**group:** `wear`

| campo | context | sweep / choices | fonte | related |
|---|---|---|---|---|
| `K_archard` | transverse · {} | (1e-5, 1e-3, 15, log) | §4.3; gotcha K/H | `hardness`,`k_wear_spec` |
| `hardness` | transverse · {} | (1e9, 4e9, 15, log) | §4.3; gotcha K/H | `K_archard`,`k_wear_spec` |
| `k_wear_spec` | transverse · {} | (0, 5e-13, 15, lin) | §4.3 merge K/H §4.42a | `K_archard`,`hardness` |
| `k_wear_running` | transverse · {} | (1.0, 5.0, 14, lin) | §6 running-in; Zhang2019 | `N_wear_run` |
| `N_wear_run` | transverse · {k_wear_running:3.0} | (10, 1000, 15, log) | §6 running-in | `k_wear_running` |

Nota: `k_wear_spec` sobrepõe K/H só se `>0`; sweep começa em 0 (=legado) e sobe.

---

### Task 9 (B4): Greenwood-Williamson (rigidez) — 2 campos

**group:** `stiffness`

| campo | context | sweep | fonte | related |
|---|---|---|---|---|
| `k_j_init` | transverse · {} | (1e9, 8e9, 15, log) | §3; GW softening | `alpha_GW` |
| `alpha_GW` | transverse · {} | (0.1, 1.0, 15, lin) | §3; GW | `k_j_init` |

---

### Task 10 (B5): Atrito — 2 campos

**group:** `friction`

| campo | context | sweep | fonte | related |
|---|---|---|---|---|
| `mu_thread` | transverse · {} | (0.05, 0.30, 15, lin) | §3; anchor `mu_dry`; Pai-Hess L(µ) | `mu_bearing` |
| `mu_bearing` | transverse · {} | (0.05, 0.30, 15, lin) | §3; anchor `mu_dry` | `mu_thread` |

---

### Task 11 (B6): Fretting axial — 3 campos

**group:** `axial_fretting`

| campo | context | sweep | fonte | related |
|---|---|---|---|---|
| `k_thread_fret` | axial · {} | (0, 1.0, 15, lin) | §4.5; roadmap #9 | `fret_freq_exp` |
| `fret_freq_exp` | axial · {k_thread_fret:0.5} | (0, 2.0, 13, lin) | §4.5 dwell; §4.39 Li2022ti | `f_ref_fret`,`k_thread_fret` |
| `f_ref_fret` | axial · {k_thread_fret:0.5, fret_freq_exp:1.0} | (5, 30, 15, lin) | §4.5 | `fret_freq_exp` |

---

### Task 12 (B7): Loosening — núcleo — 6 campos

**group:** `loosening`

| campo | category | context | sweep / choices | fonte | related |
|---|---|---|---|---|---|
| `tr_loose_gain` | physical | transverse · {} | (0.5, 5.0, 15, lin) | §4.4; DOF #1 provenance | — |
| `free_spin` | form | transverse · {} | (0, 1.0, 15, lin) | §6; §4.23 Rousseau θ | — |
| `loose_arrest_floor` | form | transverse · {} | (0, 0.15, 15, lin) | §6; §4.8 #10 arrest | — |
| `loosening_slip_coupling` | mode | transverse · {k_tr_mode:"bending"} | choices=["off","gross_fraction"] | §5.1 | `k_tr_mode` |
| `loose_torsion_mode` | mode | transverse · {loosening_slip_coupling:"gross_fraction", k_tr_mode:"bending"} | choices=["legacy","bolt_torsion"] | §5.1; #10 | `eta_loose` |
| `eta_loose` | form | transverse · {loose_torsion_mode:"bolt_torsion", loosening_slip_coupling:"gross_fraction", k_tr_mode:"bending"} | (1.0, 15.0, 15, lin) | §5.1 | `loose_torsion_mode` |

---

### Task 13 (B8): Regime de slip (Cattaneo-Mindlin) — 8 campos

**group:** `slip_regime`

| campo | category | context | sweep / choices | fonte | related |
|---|---|---|---|---|---|
| `k_tr_mode` | mode | transverse · {} | choices=["axial_frac","bending"] | §5.1 | `c_bend` |
| `c_bend` | form | transverse · {k_tr_mode:"bending"} | (0.2, 3.0, 15, lin) | §5.1; §4 k_tr | `k_tr_mode` |
| `slip_regime_mode` | mode | transverse · {} | choices=["off","cattaneo_mindlin"] | §5.2; slip-regime form | `slip_capacity_coeff` |
| `slip_regime_sharpness` | form | transverse · {slip_regime_mode:"cattaneo_mindlin"} | (0.5, 4.0, 15, lin) | §5.2 | `slip_regime_mode` |
| `slip_capacity_coeff` | form | transverse · {slip_regime_mode:"cattaneo_mindlin"} | (0.3, 3.0, 15, lin) | §5.2 | `slip_regime_mode` |
| `partial_slip_exp` | form | transverse · {slip_regime_mode:"cattaneo_mindlin", k_partial_slip:0.5} | (0.5, 3.0, 15, lin) | §5.2 | `k_partial_slip` |
| `couple_famp_slip` | mode | transverse · {} | choices=[false, true] | §5.2; roadmap #4 | — |
| `k_partial_slip` | form | transverse · {} | (0, 2.0, 15, lin) | §6; §4.25/§4.31 dE_partial | `partial_slip_exp` |

---

### Task 14 (B9): Ratchet / loosening graduado — 7 campos

**group:** `ratchet`

| campo | category | context | sweep / choices | fonte | related |
|---|---|---|---|---|---|
| `k_ratchet` | form | transverse · {} | (0, 2.0, 15, lin) | §6; §4.15 kinematic-ratchet | `delta_free` |
| `delta_free` | form | transverse · {k_ratchet:0.5} | (0, 1e-3, 15, lin) | §6 | `k_ratchet` |
| `ratchet_torque_coupled` | mode | transverse · {k_ratchet:0.5} | choices=[false, true] | §6 | `k_ratchet` |
| `loose_kin_ceiling` | form | transverse · {} | (0, 1.0, 15, lin) | §6 graded loosening | `loose_rate_mode` |
| `loose_rate_mode` | mode | transverse · {} | choices=["torque","kinematic"] | §5.1 | `loose_kin_ceiling` |
| `s_crit_loose` | form | transverse · {loose_rate_mode:"kinematic"} | (0, 5e-4, 15, lin) | §6 graded_scrit | `k_loose_graded` |
| `k_loose_graded` | form | transverse · {loose_rate_mode:"kinematic", s_crit_loose:2e-4} | (0, 2.0, 15, lin) | §6 | `s_crit_loose` |

---

### Task 15 (B10): Surface damage — 9 campos

**group:** `damage`

| campo | category | context | sweep / choices | fonte | related |
|---|---|---|---|---|---|
| `c_D` | physical | transverse · {k_dmg_mu:1.0, k_dmg_wear:4.0} | (0, 5.0, 15, lin) | §4; surface_damage | `k_dmg_mu`,`k_dmg_wear` |
| `W_ref` | form | transverse · {c_D:2.0, k_dmg_mu:1.0, k_dmg_wear:4.0} | (1e3, 1e5, 15, log) | §4 damage | `c_D` |
| `k_dmg_mu` | form | transverse · {c_D:2.0, k_dmg_wear:4.0} | (0, 3.0, 15, lin) | §4 damage→µ | `c_D` |
| `k_dmg_wear` | form | transverse · {c_D:2.0, k_dmg_mu:1.0} | (0, 8.0, 15, lin) | §4 damage→wear | `c_D` |
| `W_crit` | form | transverse · {c_D:2.0, k_dmg_mu:1.0, k_dmg_wear:4.0} | (0, 5e4, 15, lin) | §5.2 predictive-trigger | `dmg_onset_sharpness` |
| `dmg_onset_sharpness` | form | transverse · {c_D:2.0, k_dmg_wear:4.0, W_crit:1e4} | (1.0, 8.0, 15, lin) | §5.2 | `W_crit` |
| `dmg_gross_exp` | form | transverse · {c_D:2.0, k_dmg_wear:4.0, k_tr_mode:"bending"} | (0, 3.0, 15, lin) | §5.2 onset por gross-slip | `c_D` |
| `dmg_dwell_exp` | form | transverse · {c_D:2.0, k_dmg_wear:4.0} | (0, 2.0, 15, lin) | §6 dwell; Yang 5/10Hz | `f_ref_dmg` |
| `f_ref_dmg` | form | transverse · {c_D:2.0, k_dmg_wear:4.0, dmg_dwell_exp:1.0} | (5, 20, 15, lin) | §6 | `dmg_dwell_exp` |

---

### Task 16 (B11): Slip-onset + conformação de pressão — 6 campos

**group:** `conformation`

| campo | category | context | sweep / choices | fonte | related |
|---|---|---|---|---|---|
| `slip_onset_W` | form | transverse · {} | (0, 5e4, 15, lin) | §5.2 incubação (stage-1) | `slip_onset_sharpness` |
| `slip_onset_sharpness` | form | transverse · {slip_onset_W:1e4} | (1.0, 8.0, 15, lin) | §5.2 | `slip_onset_W` |
| `W_conf_ref` | physical | transverse · {conform_driver:"effective", conform_pressure_exp:2.0} | (0, 2e4, 15, lin) | §6; §4.9; ADOTADO shared | `conform_driver` |
| `conform_pressure_exp` | form | transverse · {conform_driver:"effective", W_conf_ref:7671.0} | (1.0, 3.0, 15, lin) | §6; anchor `conform_pressure_exp` | `W_conf_ref` |
| `p_ref_conform` | form | transverse · {conform_driver:"effective", W_conf_ref:7671.0, conform_pressure_exp:2.0} | (1e8, 1e9, 15, log) | §6 | `W_conf_ref` |
| `conform_driver` | mode | transverse · {W_conf_ref:7671.0, conform_pressure_exp:2.0} | choices=["raw","effective"] | §5.1; §4.9 driver | `W_conf_ref` |

---

### Task 17 (B12): Membro (complacência) — 2 campos

**group:** `member`

| campo | context | sweep | fonte | related |
|---|---|---|---|---|
| `k_member_shear` | transverse · {k_tr_mode:"bending"} | (0, 5e8, 15, lin) | §6; §4.20 HDPE item 2 | `member_loss_eta` |
| `member_loss_eta` | transverse · {k_member_shear:1e8} | (0, 1.0, 15, lin) | §6; §4.25 loops | `k_member_shear` |

Nota: em aço `k_member_shear` é desprezível; o contexto usa membro complacente (valor baixo) para o slider agir — a prosa explica isso.

---

### Task 18 (B13): Re-aperto — 2 campos

**group:** `retighten`

| campo | context | sweep | fonte | related |
|---|---|---|---|---|
| `k_emb_renew` | transverse · {c_D:2.0, k_dmg_mu:1.0, k_dmg_wear:4.0, D_init via loading? nao — usar overrides c_D} | (0, 1.0, 15, lin) | §6; roadmap #5 embedding renewal | `k_gall` |
| `k_gall` | transverse · {c_D:2.0, k_dmg_mu:1.0, k_dmg_wear:4.0} | (0, 5.0, 15, lin) | §6; §4.11 galling | `k_emb_renew` |

Nota: `k_emb_renew`/`k_gall` só agem em `retighten()`. `handle_simulate` **não** re-aperta → o slider ficaria morto. **Decisão:** marcar ambos `negligible=True` e a prosa explica "só atua no re-aperto (fora do escopo desta curva de ensaio contínuo); ver [[k_dmg_mu]]/cadeia de re-aperto no runner de validação". O teste isenta `negligible`.

---

### Task 19 (B14): Fadiga (cauda de fratura, S-N) — 10 campos

**group:** `fatigue`

| campo | category | context | sweep / choices | fonte | related |
|---|---|---|---|---|---|
| `fatigue_enabled` | mode | axial · {} | choices=[false, true] | §4.6 FatigueLoss | `fat_Kt` |
| `fatigue_residual_frac` | form | axial · {fatigue_enabled:true} | (0, 0.5, 15, lin) | §4.6 | `fatigue_enabled` |
| `fat_Kt` | form | axial · {fatigue_enabled:true} | (1.0, 5.0, 15, lin) | §4.6; Su-N | `fatigue_enabled` |
| `fat_sigma_uts` | form | axial · {fatigue_enabled:true} | (8e8, 1.2e9, 15, lin) | §4.6 Goodman | `fat_sigma_endurance` |
| `fat_sigma_knee` | form | axial · {fatigue_enabled:true} | (3e7, 8e7, 15, lin) | §4.6 | `fat_sigma_endurance` |
| `fat_C1` | form | axial · {fatigue_enabled:true} | (1e32, 1e33, 9, log) | §4.6 curva 1 | `fat_m1` |
| `fat_m1` | form | axial · {fatigue_enabled:true} | (3.0, 5.0, 15, lin) | §4.6 | `fat_C1` |
| `fat_C2` | form | axial · {fatigue_enabled:true} | (1e49, 1e50, 9, log) | §4.6 curva 2 | `fat_m2` |
| `fat_m2` | form | axial · {fatigue_enabled:true} | (5.0, 7.0, 15, lin) | §4.6 | `fat_C2` |
| `fat_sigma_endurance` | form | axial · {fatigue_enabled:true} | (4.6e7, 6.3e7, 15, lin) | §4.6; anchor `fat_sigma_endurance` | `fat_sigma_knee` |

Nota: se o baseline axial não fraturar dentro de N=2500, aumentar `N` no `context.overrides` do batch (via `loading`? não — `context` só mexe `mat`). **Decisão:** para este batch, o `sweep_variable` de fadiga usa um baseline axial com `N` maior; adicionar um baseline `"fatigue"` em `BASELINES` (axial com `N=... ` alto o suficiente para o cliff, ex. `N` que leve `sigma` acima do joelho) nesta task. Se ainda assim algum `fat_*` não mover a curva (Goodman insensível no regime), marcá-lo `negligible=True` com prosa honesta.

---

### Task 20 (B15): Gatilho de crash — 2 campos

**group:** `crash`

| campo | context | sweep | fonte | related |
|---|---|---|---|---|
| `crash_trigger_frac` | transverse · {} | (0, 0.9, 15, lin) | §6; §4.30 criticalidade | `crash_trigger_sharpness` |
| `crash_trigger_sharpness` | transverse · {crash_trigger_frac:0.6} | (1.0, 16.0, 15, lin) | §6 | `crash_trigger_frac` |

---

### Task 21 (B16): Numérico / inércia — 5 campos (negligible)

**group:** `numerical`

Todos `category="numerical"`, `negligible=True`, `context=transverse`, sweep pequeno só para mostrar a chatura da curva. Prosa: "parâmetro de solver/inércia — efeito negligível no afrouxamento quase-estático; existe para o balanço dinâmico [M]/[C]/Rayleigh."

| campo | sweep | fonte |
|---|---|---|
| `rayleigh_alpha` | (0, 0.1, 8, lin) | §3 Rayleigh |
| `rayleigh_beta` | (0, 1e-4, 8, lin) | §3 Rayleigh |
| `m_x` | (0.1, 2.0, 8, lin) | §3 [M] |
| `m_y` | (0.1, 2.0, 8, lin) | §3 [M] |
| `I_theta` | (1e-6, 1e-4, 8, log) | §3 [M] |

Teste do batch numérico: verifica presença + que são todos `negligible` (isento de slider-vivo).

---

### Task 22: Cobertura total, geração e documentação

**Files:**
- Modify: `tests/test_variable_explorer.py` (teste de cobertura vira o gate final)
- Modify: `CLAUDE.md` (tabela de reference docs)
- Generate: `New_Theory/variable_explorer/` (80 + índice)

- [ ] **Step 1: Escrever/ativar o teste de cobertura total**

```python
def test_all_fields_covered():
    mod = _load()
    missing = mod.missing_fields()
    assert not missing, f"campos sem VarSpec: {sorted(missing)}"
    assert len(mod.VARIABLE_SPECS) == len(mod.all_field_names()) == 80
```

- [ ] **Step 2: Rodar toda a suíte**

Run: `python -m pytest tests/test_variable_explorer.py -q`
Expected: PASS (cobertura + todos os batches + smokes). Se algum `slider morto` falhar, ajustar o `context.overrides` daquele campo (ligar o companheiro certo) ou marcá-lo `negligible=True` com justificativa na prosa.

- [ ] **Step 3: Gerar o documento**

Run: `python New_Theory/build_variable_explorer.py`
Expected: escreve `New_Theory/variable_explorer/index.html` + 80 `var_*.html`; imprime `0 campos faltando`.
Verificar: `python -c "import pathlib; print(len(list(pathlib.Path('New_Theory/variable_explorer').glob('var_*.html'))))"` → `80`.

- [ ] **Step 4: Validar HTML gerado** (parse de uma amostra)

Run: `python -c "from html.parser import HTMLParser; import pathlib,glob; [HTMLParser().feed(pathlib.Path(f).read_text(encoding='utf-8')) for f in glob.glob('New_Theory/variable_explorer/*.html')]; print('HTML OK')"`
Expected: `HTML OK`.

- [ ] **Step 5: Documentar no CLAUDE.md** — na tabela "Reference docs", adicionar:

```
| `New_Theory/variable_explorer/index.html` | **Explorador interativo de variáveis**: uma página por campo de `JointMaterial` (80) — curva-padrão + slider + física PT/EN + refs. Gerado por `python New_Theory/build_variable_explorer.py` (curvas do engine real via `handle_simulate`). |
```

E em "V2 calibration tooling", adicionar o comando:
```
# Gerar o explorador interativo de variaveis (docs; ~1-2 min)
python New_Theory/build_variable_explorer.py
```

- [ ] **Step 6: Commit final**

```bash
git add New_Theory/build_variable_explorer.py tests/test_variable_explorer.py CLAUDE.md
git add New_Theory/variable_explorer
git commit -m "feat(explorer): 80 paginas geradas + cobertura total + docs"
```

---

## Self-Review (preenchido pelo autor do plano)

**1. Cobertura do spec:**
- §0 objetivo → Tasks 3–4 (página+índice) + 6–21 (conteúdo). ✅
- §1 decisões (80 campos, estático, 1 arquivo/campo, refs proveniência+curadoria, standalone, PT/EN) → Global Constraints + Tasks 1,3,22. ✅
- §2 engine=fonte única → Task 2 (`handle_simulate`). ✅
- §3 sliders vivos / negligible → teste slider-vivo (batches) + `negligible` (Tasks 18,19,21). ✅
- §4 baselines verbatim → Global Constraints + Task 1 (`BASELINES`) + Task 19 (baseline fatigue). ✅
- §5 gerador/VARIABLE_SPECS/validação → Tasks 1,2,4 + 6–21. ✅
- §6 conteúdo da página (toggle PT/EN, tema, plotter, refs, related) → Task 3. ✅
- §7 índice → Task 4. ✅
- §8 testes (registry-truth, cobertura, slider-vivo, integração, smoke) → Tasks 1,2,3,4,22 + batches. ✅
- §9 entregáveis → Task 22 (gera + CLAUDE.md). ✅

**2. Placeholder scan:** As tabelas por-campo são especificações completas (contexto, sweep, fonte, related); a prosa PT/EN é redigida das fontes citadas — é o trabalho de conteúdo, não placeholder. Batch B2 traz código completo como exemplar. O template HTML (Task 3) é escrito na task seguindo os "Detalhes do HTML gerado" + asserções do teste.

**3. Consistência de tipos:** `VarSpec` (Task 1) usado igual em todas as tasks; `sweep_variable`/`simulate`/`render_variable_page`/`render_index`/`build` com assinaturas fixas nos blocos Interfaces. `handle_simulate` conforme contrato em Global Constraints.
