# Intake de Casos do Usuário Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (inline). Steps em checkbox `- [ ]`.

**Goal:** Pipeline completo da spec `2026-07-10-user-case-intake-design.md`: prompt de IA copiável/baixável, importador do `.bascase.json` (schema v1, curva embutida), ajuste prévio per-rig (emb/floor lidos + fit só de c_bend), caso do usuário entra no registry como fonte "USER" e ganha report v2 / browser / Abrir no Model — refinável editando o bloco `prefit`.

**Architecture:** O importador escreve a cópia canônica em `Models/USER_CASES/` (JSON + CSV derivado da curva) e constrói um `ValidationCase` real (source = shim com `.name="USER"`). Ganchos mínimos nos módulos existentes: `inputs_for` honra `case._user_inputs` (grip/µ/Rz do usuário); `material_kwargs_for` aplica `case._prefit_overrides` (bloco prefit do arquivo) após as adotadas; `all_records()` agrega `user_cases.user_records()` (import lazy, cache invalidável). Todo o resto (runner, decomposição, report v2, gui_bridge, browser) funciona sem mudança.

**Tech Stack:** stdlib + numpy; PyQt6 só na camada GUI; leitores de `calibration.provenance` p/ o prefit.

## Global Constraints

- `utf-8`, `ast.parse` após edição, commit por tarefa, `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`; não tocar engine/`core/validation_cases.py`/foreign files.
- Fatos verificados: `emb_depth_from_curve(cyc, ratio, F0_N, k_b, early_index=1, vdi_ref_m=None) -> (float, dict)` e `arrest_floor_from_curve(ratio, tail_frac=0.05, min_points=2) -> (float, dict)` (`calibration/provenance.py:58/79`); `_PACKS["LEGACY"]` no runner; `all_records()` é `lru_cache` (invalidar com `.cache_clear()`); testes existentes assumem 128 casos — atualizar p/ "128 não-USER".
- QThread em teste: `.run()` síncrono.
- `Models/USER_CASES/` versionado com um exemplo (`exemplo_M12.bascase.json` + CSV derivado).

## File Structure

**Create:**
```
src/bolt_analysis_studio/validation/intake_prompt.py   # Task 1
src/bolt_analysis_studio/docs/INTAKE_PROMPT.md         # Task 1
src/bolt_analysis_studio/validation/user_cases.py      # Task 2
src/bolt_analysis_studio/validation/prefit.py          # Task 3
Models/USER_CASES/exemplo_M12.bascase.json             # Task 5
tests/test_intake_prompt.py, tests/test_user_cases.py, tests/test_prefit.py
```
**Modify:** `validation/inputs.py` (hook `_user_inputs`), `validation/runner.py` (hook `_prefit_overrides`), `validation/case_registry.py` (agrega USER + `refresh_records`), `validation/report.py` (CLI `--import`), `chrome/widgets/validation_browser.py` + `controllers/validation_controller.py` (botões), `tests/test_validation_registry.py` e `tests/test_validation_report_html.py` (128 → 128 não-USER), `docs/VALIDATION_CASE_REPORTS.md` (seção intake).

---

## Task 1: `intake_prompt.py` — o prompt + doc

**Files:**
- Create: `src/bolt_analysis_studio/validation/intake_prompt.py`, `src/bolt_analysis_studio/docs/INTAKE_PROMPT.md`
- Test: `tests/test_intake_prompt.py`

**Interfaces:**
- Produces: `INTAKE_PROMPT: str` (PT, autocontido); `SCHEMA_EXAMPLE: str` (JSON de exemplo embutido no prompt, parseável).

- [ ] **Step 1: Teste falhando** `tests/test_intake_prompt.py`:

```python
import json


def test_prompt_is_self_contained():
    from bolt_analysis_studio.validation.intake_prompt import (INTAKE_PROMPT,
                                                               SCHEMA_EXAMPLE)
    p = INTAKE_PROMPT
    # perguntas do ensaio (bloco test do schema)
    for termo in ("pré-carga", "frequência", "ciclos", "controle",
                  "deslocamento", "força", "amplitude", "lubrifica",
                  "rugosidade", "grip", "parafuso"):
        assert termo in p.lower() or termo in p, termo
    # regras de normalizacao da curva
    for termo in ("F/F₀", "kN", "csv", "txt"):
        assert termo in p or termo.lower() in p.lower(), termo
    assert "bascase_version" in p                     # schema embutido
    assert "APENAS o JSON" in p or "apenas o JSON" in p
    json.loads(SCHEMA_EXAMPLE)                        # exemplo parseia


def test_docs_file_matches_prompt():
    from pathlib import Path
    from bolt_analysis_studio.validation.intake_prompt import INTAKE_PROMPT
    md = Path("src/bolt_analysis_studio/docs/INTAKE_PROMPT.md").read_text(encoding="utf-8")
    assert INTAKE_PROMPT.strip() in md                # doc = prompt + cabecalho
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** `intake_prompt.py` (o texto completo — escrever exatamente):

```python
# -*- coding: utf-8 -*-
"""Prompt de intake de casos do usuario (spec 2026-07-10-user-case-intake §5).
O usuario copia/baixa este prompt no software, cola numa IA junto com o arquivo
bruto da curva, responde as perguntas e recebe um .bascase.json importavel."""

SCHEMA_EXAMPLE = """{
  "bascase_version": 1,
  "name": "Ensaio M12 bancada X",
  "description": "Junker ±0.5 mm, parafuso classe 8.8, seco",
  "test": {
    "bolt_size": "M12x1.75",
    "bolt_diameter_mm": 12.0,
    "pitch_mm": 1.75,
    "grip_mm": 30.0,
    "preload_N": 30000.0,
    "preload_percent_yield": null,
    "loading_type": "TRANSVERSE",
    "control_mode": "displacement",
    "delta_amplitude_mm": 0.5,
    "F_amplitude_N": null,
    "frequency_Hz": 12.5,
    "n_cycles": 2000,
    "mu": null,
    "lubricated": false,
    "rz_class": null,
    "material_pair": "aço/aço",
    "notes": "aperto por torquímetro, 3 repetições, curva = média"
  },
  "curve": {
    "x_unit": "cycles",
    "y_unit": "F_over_F0",
    "points": [[0, 1.0], [100, 0.97], [500, 0.91], [2000, 0.83]]
  },
  "provenance": {
    "generated_by": "BAS intake prompt v1 + <nome da IA>",
    "date": "AAAA-MM-DD"
  },
  "prefit": {}
}"""

INTAKE_PROMPT = f"""Você é um assistente de engenharia preparando um CASO DE
ENSAIO para o Bolt Analysis Studio (BAS), um software de análise de
auto-afrouxamento de juntas aparafusadas. Sua tarefa: entrevistar o usuário,
normalizar a curva experimental dele e emitir UM ÚNICO arquivo JSON no schema
abaixo, que o software importa diretamente.

== PASSO 1 — Receba a curva experimental ==
O usuário vai colar ou anexar os dados em qualquer formato (txt, csv, planilha,
tabela colada, duas colunas separadas por espaço...). A curva é a pré-carga do
parafuso ao longo do ensaio. Identifique as duas colunas:
- x: ciclos de carga (ou tempo — pergunte qual);
- y: força de aperto, em F/F₀ (razão, começa ≈ 1.0), kN ou N — pergunte qual.
Regras de normalização que VOCÊ aplica:
- Se y está em kN ou N, mantenha os valores e declare "y_unit": "F_kN" ou
  "F_N" (o software divide por F₀ na importação).
- Se x está em tempo, converta para ciclos usando a frequência informada; se o
  ensaio é estático (creep, sem vibração), use "x_unit": "minutes".
- Ordene por x crescente, remova linhas não-numéricas, mantenha TODOS os
  pontos válidos (mínimo 4).
- Sanidade: se y_unit = F_over_F0 e o primeiro ponto não é ≈1.0 (±0.05),
  pergunte ao usuário se a curva já está normalizada.

== PASSO 2 — Entreviste o usuário (uma pergunta por vez) ==
Pergunte, explicando o porquê de cada uma (elas montam o modelo
massa-mola-amortecedor da junta no software):
1. Parafuso: designação métrica (ex.: M12x1.75) OU diâmetro nominal [mm] e
   passo [mm]. (Define a rosca, a área de tensão e a rigidez do parafuso.)
2. Comprimento de aperto (grip) [mm] — a espessura total apertada. (Define a
   rigidez axial k_b = E·A_s/L_eff. Se não souber, diga "não sei" — o
   software assume 2,5×diâmetro.)
3. Pré-carga inicial F₀ [N] OU % do escoamento do parafuso. (Referência de
   toda a curva F/F₀.)
4. Tipo de carga: TRANSVERSE (cisalhamento/Junker — movimento perpendicular
   ao parafuso) ou AXIAL (ao longo do parafuso).
5. Tipo de controle do ensaio: deslocamento imposto ("displacement", ex.:
   ±0,5 mm — típico de bancada Junker com excêntrico) ou força imposta
   ("force", ex.: servo-hidráulico). E a amplitude: δ [mm] se deslocamento,
   F_amp [N] se força.
6. Frequência de excitação [Hz].
7. Número total de ciclos do ensaio.
8. Coeficiente de atrito µ, se conhecido; lubrificado ou seco?
9. Acabamento das superfícies, se souber: retificado fino (Rz<4),
   usinado fino (Rz<10), usinado (Rz10-40) ou bruto (Rz40-160). (Governa o
   assentamento/embedding inicial.)
10. Par de materiais (ex.: aço/aço, aço/alumínio, titânio) e observações
    relevantes (reaperto? dispositivo de travamento? fratura no fim?).
Campo que o usuário não souber = null no JSON (o software aplica valores
assumidos documentados e marca a proveniência).

== PASSO 3 — Emita o arquivo ==
Responda com APENAS o JSON (sem texto antes/depois, sem markdown), no schema
exato abaixo, preenchendo "provenance.generated_by" com seu nome/modelo e a
data de hoje. Deixe "prefit" como objeto vazio (o software preenche no ajuste
prévio). O usuário salvará como <nome>.bascase.json e importará no BAS em
Results → Validation → "Importar caso…".

SCHEMA (com valores de exemplo):
{SCHEMA_EXAMPLE}

Regras do schema: "bolt_size" OU o par "bolt_diameter_mm"+"pitch_mm";
"preload_N" OU "preload_percent_yield" (pelo menos um); "loading_type" ∈
{{"TRANSVERSE","AXIAL"}}; "control_mode" ∈ {{"displacement","force"}};
TRANSVERSE exige "delta_amplitude_mm" > 0; force/AXIAL exige "F_amplitude_N";
"y_unit" ∈ {{"F_over_F0","F_kN","F_N"}}; "x_unit" ∈ {{"cycles","minutes"}}.
"""
```

`docs/INTAKE_PROMPT.md`: cabeçalho de 3 linhas ("Prompt de intake — copie
daqui ou pelo software (Results → Validation → Copiar prompt). Rev. v1
2026-07-10.") + o `INTAKE_PROMPT` verbatim. Gerar por script no Step 3 (não
duplicar à mão):

```bash
python -c "
import sys; sys.path.insert(0,'src')
from bolt_analysis_studio.validation.intake_prompt import INTAKE_PROMPT
open('src/bolt_analysis_studio/docs/INTAKE_PROMPT.md','w',encoding='utf-8').write(
  '# Prompt de intake de casos do usuário (v1)\n\nCopie daqui ou pelo software'
  ' (Results → Validation → \"Copiar prompt\"). Rev. 2026-07-10.\n\n---\n\n'
  + INTAKE_PROMPT.strip() + '\n')
print('MD escrito')"
```

- [ ] **Step 4: `ast.parse` + rodar** — `python -m pytest tests/test_intake_prompt.py -q` → **2 passed**.
- [ ] **Step 5: Commit** — `git commit -m "feat(validation): INTAKE_PROMPT — prompt de intake copiavel (schema bascase v1)"`

---

## Task 2: `user_cases.py` — validação, importação, registry

**Files:**
- Create: `src/bolt_analysis_studio/validation/user_cases.py`
- Modify: `src/bolt_analysis_studio/validation/inputs.py` (hook `_user_inputs` no `inputs_for`), `src/bolt_analysis_studio/validation/case_registry.py` (agrega USER + `refresh_records()`), `tests/test_validation_registry.py` (128 → não-USER), `tests/test_validation_report_html.py` (idem no write_reports)
- Test: `tests/test_user_cases.py`

**Interfaces:**
- Consumes: `case_registry.CaseRecord`, `core.validation_cases.ValidationCase`, `inputs.RZ_DEFAULT`.
- Produces: `USER_CASES_DIR: Path` (default `Models/USER_CASES`, monkeypatchável); `validate_bascase(data: dict) -> list[str]`; `import_user_case(path, dest_dir=None) -> CaseRecord` (salva JSON canônico + CSV derivado, invalida cache do registry); `user_records(dest_dir=None) -> list[CaseRecord]`; `case_registry.refresh_records()`.

- [ ] **Step 1: Teste falhando** `tests/test_user_cases.py`:

```python
import json

VALID = {
    "bascase_version": 1, "name": "Ensaio teste M12",
    "description": "junker sintetico",
    "test": {"bolt_size": "M12x1.75", "grip_mm": 30.0, "preload_N": 30000.0,
             "loading_type": "TRANSVERSE", "control_mode": "displacement",
             "delta_amplitude_mm": 0.5, "F_amplitude_N": None,
             "frequency_Hz": 12.5, "n_cycles": 400, "mu": 0.18,
             "lubricated": False, "rz_class": "Rz10-40",
             "material_pair": "aço/aço", "notes": ""},
    "curve": {"x_unit": "cycles", "y_unit": "F_kN",
              "points": [[0, 30.0], [100, 28.5], [250, 27.0], [400, 26.1]]},
    "provenance": {"generated_by": "teste", "date": "2026-07-10"},
    "prefit": {},
}


def _write(tmp_path, data, name="caso.bascase.json"):
    p = tmp_path / name
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_validate_ok_and_errors(tmp_path):
    from bolt_analysis_studio.validation.user_cases import validate_bascase
    assert validate_bascase(VALID) == []
    bad = json.loads(json.dumps(VALID))
    bad["test"]["delta_amplitude_mm"] = 0
    bad["curve"]["points"] = [[0, 1.0]]
    errs = validate_bascase(bad)
    assert any("delta_amplitude_mm" in e for e in errs)
    assert any("points" in e for e in errs)


def test_import_normalizes_curve_and_writes_canonical(tmp_path):
    from bolt_analysis_studio.validation.user_cases import import_user_case
    rec = import_user_case(_write(tmp_path, VALID), dest_dir=tmp_path / "uc")
    assert rec.source == "USER" and rec.family == "transverse"
    assert rec.case_class == "full_curve" and rec.csv_path.exists()
    import numpy as np
    d = np.genfromtxt(rec.csv_path, delimiter=",", skip_header=1)
    assert abs(d[0, 1] - 1.0) < 1e-9              # kN normalizado p/ ratio
    assert (rec.csv_path.parent / rec.csv_path.name.replace(".csv", ".bascase.json")).exists()
    case = rec.validation_case
    assert case.initial_preload_N == 30000.0
    assert case.source.name == "USER"
    # inputs do usuario com proveniencia 'user'
    from bolt_analysis_studio.validation.inputs import inputs_for
    inp = inputs_for(case)
    assert inp["grip_mm"] == {"value": 30.0, "prov": "user"}
    assert inp["mu"]["value"] == 0.18 and inp["mu"]["prov"] == "user"


def test_user_records_and_registry_integration(tmp_path, monkeypatch):
    from bolt_analysis_studio.validation import user_cases
    from bolt_analysis_studio.validation.case_registry import (all_records,
                                                               refresh_records)
    monkeypatch.setattr(user_cases, "USER_CASES_DIR", tmp_path / "uc")
    user_cases.import_user_case(_write(tmp_path, VALID))
    refresh_records()
    recs = all_records()
    users = [r for r in recs if r.source == "USER"]
    assert len(users) == 1
    assert len([r for r in recs if r.source != "USER"]) == 128
    refresh_records()                              # limpa p/ os demais testes
    monkeypatch.undo()
    refresh_records()


def test_runner_simulates_user_case(tmp_path, monkeypatch):
    from bolt_analysis_studio.validation import user_cases
    from bolt_analysis_studio.validation.runner import simulate_case
    monkeypatch.setattr(user_cases, "USER_CASES_DIR", tmp_path / "uc")
    rec = user_cases.import_user_case(_write(tmp_path, VALID))
    res = simulate_case(rec, n_cap=400)
    assert res.ok and res.mae is not None
    assert res.decomp                              # decomposicao presente
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** `user_cases.py`:

```python
# -*- coding: utf-8 -*-
"""Casos do usuario (.bascase.json, schema v1 — spec 2026-07-10 §4-5):
validacao com erros por campo, importacao (copia canonica em Models/USER_CASES/
+ CSV derivado da curva embutida) e records fonte 'USER' que entram no registry
e herdam TODO o pipeline (runner/report/browser/Abrir no Model)."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Optional

import numpy as np

from ..core.validation_cases import ValidationCase
from .case_registry import CaseRecord
from .inputs import repo_root

USER_CASES_DIR = repo_root() / "Models" / "USER_CASES"
_Y_UNITS = {"F_over_F0", "F_kN", "F_N"}
_X_UNITS = {"cycles", "minutes"}


class _UserSource:
    """Shim de ValidationSource p/ casos do usuario (evita tocar o enum)."""
    name = "USER"
    value = "User case"


def validate_bascase(data: dict) -> List[str]:
    errs: List[str] = []
    if data.get("bascase_version") != 1:
        errs.append("bascase_version: deve ser 1")
    if not (data.get("name") or "").strip():
        errs.append("name: obrigatório")
    t = data.get("test") or {}
    if not t.get("bolt_size") and not (t.get("bolt_diameter_mm") and t.get("pitch_mm")):
        errs.append("test.bolt_size OU (bolt_diameter_mm + pitch_mm): obrigatório")
    if not t.get("preload_N") and not t.get("preload_percent_yield"):
        errs.append("test.preload_N OU preload_percent_yield: obrigatório")
    lt = t.get("loading_type")
    if lt not in ("TRANSVERSE", "AXIAL"):
        errs.append("test.loading_type: TRANSVERSE ou AXIAL")
    cm = t.get("control_mode")
    if cm not in ("displacement", "force"):
        errs.append("test.control_mode: displacement ou force")
    if lt == "TRANSVERSE" and cm == "displacement" and not (
            t.get("delta_amplitude_mm") or 0) > 0:
        errs.append("test.delta_amplitude_mm: > 0 obrigatório em "
                    "TRANSVERSE/displacement")
    if cm == "force" and not (t.get("F_amplitude_N") or 0) > 0:
        errs.append("test.F_amplitude_N: > 0 obrigatório em control_mode=force")
    if not (t.get("frequency_Hz") or 0) > 0:
        errs.append("test.frequency_Hz: > 0 obrigatório")
    if not (t.get("n_cycles") or 0) > 0:
        errs.append("test.n_cycles: > 0 obrigatório")
    c = data.get("curve") or {}
    if c.get("x_unit") not in _X_UNITS:
        errs.append(f"curve.x_unit: um de {sorted(_X_UNITS)}")
    if c.get("y_unit") not in _Y_UNITS:
        errs.append(f"curve.y_unit: um de {sorted(_Y_UNITS)}")
    pts = c.get("points") or []
    if len(pts) < 4:
        errs.append("curve.points: mínimo 4 pontos")
    else:
        try:
            xs = [float(p[0]) for p in pts]
            ys = [float(p[1]) for p in pts]
            if any(b <= a for a, b in zip(xs, xs[1:])):
                errs.append("curve.points: x deve ser estritamente crescente")
            if c.get("y_unit") == "F_over_F0" and abs(ys[0] - 1.0) > 0.05:
                errs.append("curve.points: F_over_F0 deve começar ≈ 1.0")
            if min(ys) <= 0:
                errs.append("curve.points: y deve ser > 0")
        except (TypeError, ValueError, IndexError):
            errs.append("curve.points: pares numéricos [x, y]")
    return errs


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "caso_usuario"


def _normalize_curve(data: dict) -> tuple:
    c = data["curve"]
    t = data["test"]
    pts = np.asarray(c["points"], dtype=float)
    cyc, y = pts[:, 0], pts[:, 1]
    if c["y_unit"] == "F_kN":
        y = y * 1e3
    if c["y_unit"] in ("F_kN", "F_N"):
        F0 = float(t.get("preload_N") or y[0])
        ratio = y / max(F0, 1e-9)
    else:
        ratio = y
    freq = float(t["frequency_Hz"])
    if c["x_unit"] == "minutes":
        # regra dos casos de creep: 1 pseudo-ciclo = 1 min => freq = 1/60 Hz
        freq = 1.0 / 60.0
    return cyc, ratio / max(ratio[0], 1e-9), freq


def _build_case(data: dict, csv_rel: str, freq: float,
                final_ratio: float) -> ValidationCase:
    t = data["test"]
    d_mm = float(t.get("bolt_diameter_mm") or
                 t["bolt_size"].split("x")[0][1:])
    p_mm = float(t.get("pitch_mm") or t["bolt_size"].split("x")[1])
    bolt_size = t.get("bolt_size") or f"M{d_mm:g}x{p_mm:g}"
    F0 = float(t.get("preload_N") or 0.0)
    pct = float(t.get("preload_percent_yield") or 70.0)
    if F0 <= 0:            # so %yield: estima F0 ~ pct% * Sy(8.8) * A_s generica
        A_s_mm2 = np.pi / 4.0 * (d_mm - 0.9382 * p_mm) ** 2
        F0 = pct / 100.0 * 640e6 * A_s_mm2 * 1e-6
    delta = float(t.get("delta_amplitude_mm") or 0.0)
    case = ValidationCase(
        name=data["name"], description=data.get("description", ""),
        source=_UserSource(), reference=data.get("provenance", {}).get(
            "generated_by", "caso do usuário"),
        bolt_size=bolt_size, bolt_diameter_mm=d_mm, pitch_mm=p_mm,
        initial_preload_N=F0, preload_percent_yield=pct,
        transverse_displacement_mm=(delta if t["loading_type"] == "TRANSVERSE"
                                    else 0.0),
        frequency_Hz=freq, n_cycles=int(t["n_cycles"]),
        mu_initial=float(t.get("mu") or 0.15),
        lubricated=bool(t.get("lubricated") or False),
        expected_final_preload_ratio=final_ratio, expected_loosening_deg=0.0,
        notes=t.get("notes", ""), reference_csv_path=csv_rel)
    # inputs com proveniencia do usuario (hook do inputs_for)
    ui = {}
    if t.get("grip_mm"):
        ui["grip_mm"] = dict(value=float(t["grip_mm"]), prov="user")
    if t.get("mu"):
        ui["mu"] = dict(value=float(t["mu"]), prov="user")
    if t.get("rz_class"):
        ui["rz"] = dict(value=t["rz_class"], prov="user")
    if t.get("F_amplitude_N"):
        ui["F_amp_N"] = dict(value=float(t["F_amplitude_N"]), prov="user")
    case._user_inputs = ui
    case._prefit_overrides = dict(data.get("prefit", {}).get("overrides", {}))
    case._bascase = data
    return case


def _record_from(data: dict, json_path: Path, csv_path: Path) -> CaseRecord:
    cyc, ratio, freq = _normalize_curve(data)
    rel = csv_path.relative_to(repo_root()).as_posix() \
        if csv_path.is_relative_to(repo_root()) else str(csv_path)
    case = _build_case(data, rel, freq, float(ratio[-1]))
    t = data["test"]
    fam = ("axial" if t["loading_type"] == "AXIAL"
           else "creep" if data["curve"]["x_unit"] == "minutes"
           else "transverse")
    return CaseRecord(
        case_id=json_path.stem.replace(".bascase", ""), name=data["name"],
        source="USER", family=fam, case_class="full_curve",
        caveats=[n for n in [t.get("notes") or ""] if n],
        validation_case=case, csv_path=csv_path,
        apparatus_note_path=None, gallery_entry=None)


def import_user_case(path, dest_dir: Optional[Path] = None) -> CaseRecord:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    errs = validate_bascase(data)
    if errs:
        raise ValueError("bascase inválido: " + "; ".join(errs))
    dest = Path(dest_dir) if dest_dir else USER_CASES_DIR
    dest.mkdir(parents=True, exist_ok=True)
    slug = _slug(data["name"])
    cyc, ratio, _ = _normalize_curve(data)
    csv_path = dest / f"{slug}.csv"
    csv_path.write_text("cycle,F_over_F0\n" + "\n".join(
        f"{x:g},{y:.6f}" for x, y in zip(cyc, ratio)), encoding="utf-8")
    json_path = dest / f"{slug}.bascase.json"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    from . import case_registry
    case_registry.refresh_records()
    return _record_from(data, json_path, csv_path)


def user_records(dest_dir: Optional[Path] = None) -> List[CaseRecord]:
    dest = Path(dest_dir) if dest_dir else USER_CASES_DIR
    out: List[CaseRecord] = []
    if not dest.exists():
        return out
    for jp in sorted(dest.glob("*.bascase.json")):
        try:
            data = json.loads(jp.read_text(encoding="utf-8"))
            if validate_bascase(data):
                continue                          # invalido: ignora no scan
            csv_path = jp.with_name(jp.name.replace(".bascase.json", ".csv"))
            if not csv_path.exists():
                continue
            out.append(_record_from(data, jp, csv_path))
        except (OSError, json.JSONDecodeError, ValueError):
            continue
    return out
```

`inputs.py` — no início de `inputs_for`, antes do `SOURCE_INPUTS.get(...)`:

```python
    ui = getattr(case, "_user_inputs", None)
    if ui is not None:
        d = _d_mm(case)
        return dict(
            grip_mm=ui.get("grip_mm", dict(value=2.5 * d, prov="assumed")),
            mu=ui.get("mu", dict(value=0.15, prov="assumed")),
            rz=ui.get("rz", dict(value=RZ_DEFAULT, prov="assumed")),
            F_amp_N=ui.get("F_amp_N", dict(
                value=F_AMP_RATIO * case.initial_preload_N,
                prov="literature (Pai&Hess 2002: 0.38-0.49 medido)")))
```

`case_registry.py` — em `all_records()`, após o dedup, agregar (lazy import,
sem dedup contra os 128 — ids de usuário têm o próprio namespace de slug):

```python
    from . import user_cases                      # lazy: evita import circular
    recs = recs + user_cases.user_records()
    return recs
```

e novo helper:

```python
def refresh_records() -> None:
    """Invalida o cache (novos casos do usuario aparecem no proximo all_records)."""
    all_records.cache_clear()
```

Testes existentes: em `tests/test_validation_registry.py`, trocar
`assert len(recs) == 128` por `assert len([r for r in recs if r.source != "USER"]) == 128`
(e o de ids únicos idem); em `tests/test_validation_report_html.py`
`test_write_reports_all_cases`, trocar `== 128` por `>= 128`.

- [ ] **Step 4: `ast.parse` (3 arquivos) + rodar** — `python -m pytest tests/test_user_cases.py tests/test_validation_registry.py tests/test_validation_inputs.py -q` → verde.
- [ ] **Step 5: Commit** — `git commit -m "feat(validation): user_cases — import .bascase.json + fonte USER no registry"`

---

## Task 3: `prefit.py` — ajuste prévio per-rig + hook no runner

**Files:**
- Create: `src/bolt_analysis_studio/validation/prefit.py`
- Modify: `src/bolt_analysis_studio/validation/runner.py` (`material_kwargs_for` aplica `case._prefit_overrides` após as adotadas)
- Test: `tests/test_prefit.py`

**Interfaces:**
- Consumes: `calibration.provenance.emb_depth_from_curve/arrest_floor_from_curve`; `runner.simulate_case/_PACKS`; `inputs.geometry_for_case/inputs_for/load_full_curve`.
- Produces: `prefit_user_case(rec, n_cap=None) -> dict` (bloco prefit: `{"overrides": {...}, "provenance": {...}, "mae": float}`), gravado no JSON canônico do caso; runner honra `case._prefit_overrides`.

- [ ] **Step 1: Teste falhando** `tests/test_prefit.py`:

```python
import json

from tests.test_user_cases import VALID, _write


def test_prefit_reads_emb_floor_and_fits_cbend(tmp_path, monkeypatch):
    from bolt_analysis_studio.validation import user_cases
    from bolt_analysis_studio.validation.prefit import prefit_user_case
    monkeypatch.setattr(user_cases, "USER_CASES_DIR", tmp_path / "uc")
    rec = user_cases.import_user_case(_write(tmp_path, VALID))
    block = prefit_user_case(rec, n_cap=400)
    ov = block["overrides"]
    assert ov["emb_depth"] > 0                     # lido da queda inicial
    assert "loose_arrest_floor" in ov              # lido do plato final
    assert "c_bend" in ov and ov["k_tr_mode"] == "bending"
    assert block["provenance"]["emb_depth"].startswith("data_implied")
    assert block["provenance"]["c_bend"] == "fitado-this-rig (unico DOF §4.42)"
    # gravado no JSON canonico
    jp = tmp_path / "uc" / f"{rec.case_id}.bascase.json"
    saved = json.loads(jp.read_text(encoding="utf-8"))
    assert saved["prefit"]["overrides"]["c_bend"] == ov["c_bend"]


def test_prefit_improves_or_matches_zero_fit(tmp_path, monkeypatch):
    from bolt_analysis_studio.validation import user_cases
    from bolt_analysis_studio.validation.prefit import prefit_user_case
    from bolt_analysis_studio.validation.runner import simulate_case
    monkeypatch.setattr(user_cases, "USER_CASES_DIR", tmp_path / "uc")
    rec = user_cases.import_user_case(_write(tmp_path, VALID))
    mae0 = simulate_case(rec, n_cap=400).mae       # zero-fit
    block = prefit_user_case(rec, n_cap=400)
    rec.validation_case._prefit_overrides = block["overrides"]
    mae1 = simulate_case(rec, n_cap=400).mae
    assert mae1 <= mae0 + 1e-9


def test_axial_prefit_reads_only(tmp_path, monkeypatch):
    from bolt_analysis_studio.validation import user_cases
    from bolt_analysis_studio.validation.prefit import prefit_user_case
    data = json.loads(json.dumps(VALID))
    data["name"] = "Ensaio axial teste"
    data["test"].update(loading_type="AXIAL", control_mode="force",
                        F_amplitude_N=10000.0, delta_amplitude_mm=None)
    monkeypatch.setattr(user_cases, "USER_CASES_DIR", tmp_path / "uc")
    rec = user_cases.import_user_case(_write(tmp_path, data, "ax.bascase.json"))
    block = prefit_user_case(rec, n_cap=400)
    assert "c_bend" not in block["overrides"]      # axial: nada fitado
    assert block["overrides"]["emb_depth"] > 0
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** `prefit.py`:

```python
# -*- coding: utf-8 -*-
"""Ajuste previo per-rig de casos do usuario (spec 2026-07-10 §3.1 — a doutrina
que a campanha legitimou, §4.42/L24): LE da propria curva o que e legivel
(emb_depth da queda inicial, loose_arrest_floor do plato final) e FITA apenas
c_bend (transversal; axial: nada). Resultado gravado no .bascase.json com
proveniencia por constante — refinar = editar/refitar esses campos."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import numpy as np

from ..calibration.provenance import (arrest_floor_from_curve,
                                      emb_depth_from_curve)
from .case_registry import CaseRecord
from .inputs import geometry_for_case, inputs_for, load_full_curve, repo_root
from .runner import _PACKS, simulate_case

_CBEND_GRID = [0.3, 1.0, 3.0, 10.0, 30.0, 50.0]


def _mae_with(rec: CaseRecord, overrides: dict, n_cap) -> float:
    rec.validation_case._prefit_overrides = overrides
    res = simulate_case(rec, n_cap=n_cap)
    return res.mae if (res.ok and res.mae is not None) else float("inf")


def prefit_user_case(rec: CaseRecord, n_cap: Optional[int] = None) -> dict:
    case = rec.validation_case
    inp = inputs_for(case)
    geom = geometry_for_case(case, grip_mm=inp["grip_mm"]["value"])
    rel = (rec.csv_path.relative_to(repo_root()).as_posix()
           if rec.csv_path.is_relative_to(repo_root()) else str(rec.csv_path))
    cyc, ratio = load_full_curve(rel)
    F0 = case.initial_preload_N
    emb, emb_br = emb_depth_from_curve(cyc, ratio, F0, geom.k_b)
    floor, floor_br = arrest_floor_from_curve(ratio)
    prov = {"emb_depth": emb_br.get("provenance", "data_implied_early_drop"),
            "loose_arrest_floor": ("lido-do-dado (platô final)"
                                   if floor_br.get("plateau", True)
                                   else "lido-do-dado (LIMITE INFERIOR — "
                                        "curva termina em queda)")}
    if rec.family == "transverse":
        base = dict(_PACKS["LEGACY"])
        base.update(emb_depth=emb, loose_arrest_floor=floor)
        maes = {c: _mae_with(rec, dict(base, c_bend=c), n_cap)
                for c in _CBEND_GRID}
        best = min(maes, key=maes.get)
        # refino 1x entre vizinhos do grid (log)
        idx = _CBEND_GRID.index(best)
        lo = _CBEND_GRID[max(idx - 1, 0)]
        hi = _CBEND_GRID[min(idx + 1, len(_CBEND_GRID) - 1)]
        for c in np.geomspace(lo, hi, 5):
            m = _mae_with(rec, dict(base, c_bend=float(c)), n_cap)
            if m < maes[best]:
                maes[float(c)] = m
                best = float(c)
        overrides = dict(base, c_bend=float(best))
        mae = maes[best]
        prov["c_bend"] = "fitado-this-rig (unico DOF §4.42)"
    else:                                          # axial/creep: so leitura
        overrides = dict(emb_depth=emb)
        if floor_br.get("plateau", True) and floor > 0:
            overrides["loose_arrest_floor"] = floor
        mae = _mae_with(rec, overrides, n_cap)
    case._prefit_overrides = overrides
    block = {"overrides": {k: (float(v) if isinstance(v, (int, float)) else v)
                           for k, v in overrides.items()},
             "provenance": prov, "mae": (None if mae == float("inf") else mae)}
    # grava no JSON canonico do caso
    jp = rec.csv_path.with_name(rec.csv_path.name.replace(".csv", ".bascase.json"))
    if jp.exists():
        data = json.loads(jp.read_text(encoding="utf-8"))
        data["prefit"] = block
        jp.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                      encoding="utf-8")
    return block
```

`runner.py` — em `material_kwargs_for`, após o loop das adotadas:

```python
    pf = getattr(rec.validation_case, "_prefit_overrides", None)
    if pf:                                        # ajuste previo do caso USER
        for k, v in pf.items():
            if k in fields:
                kw[k] = v
```

- [ ] **Step 4: `ast.parse` + rodar** — `python -m pytest tests/test_prefit.py tests/test_validation_runner.py -q` → verde (paridade dos 128 intacta: casos não-USER não têm `_prefit_overrides`).
- [ ] **Step 5: Commit** — `git commit -m "feat(validation): prefit per-rig — emb/floor lidos + fit so de c_bend; runner honra prefit"`

---

## Task 4: CLI `--import` + botões na GUI

**Files:**
- Modify: `src/bolt_analysis_studio/validation/report.py`, `chrome/widgets/validation_browser.py`, `chrome/controllers/validation_controller.py`
- Test: append em `tests/test_user_cases.py` e `tests/test_validation_browser.py`

**Interfaces:**
- Produces: CLI `--import <path.bascase.json>` (importa + prefit + simula + regenera reports); browser: `btn_import`, `btn_prompt_copy`, `btn_prompt_save`, sinais `import_case_requested()`, `copy_prompt_requested()`, `save_prompt_requested()`; controller: `import_case(path) -> Optional[str]` (case_id; None se inválido — mostra erros no prompt area via sinal `import_failed(str)`), `copy_prompt()`.

- [ ] **Step 1: Testes falhando** — append em `tests/test_validation_browser.py`:

```python
def test_browser_has_intake_buttons(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.validation_browser import ValidationBrowser
    b = ValidationBrowser()
    assert b.btn_import.text().startswith("Importar")
    got = []
    b.copy_prompt_requested.connect(lambda: got.append(1))
    b.btn_prompt_copy.click()
    assert got == [1]


def test_controller_import_and_copy_prompt(qapp, tmp_path, monkeypatch):
    import json
    from tests.test_user_cases import VALID
    from bolt_analysis_studio.core.app_state import get_app_state
    from bolt_analysis_studio.gui.chrome.controllers.validation_controller import (
        ValidationController)
    from bolt_analysis_studio.validation import user_cases
    from bolt_analysis_studio.validation.case_registry import refresh_records
    monkeypatch.setattr(user_cases, "USER_CASES_DIR", tmp_path / "uc")
    st = get_app_state(); st.new_project()
    c = ValidationController(st)
    p = tmp_path / "novo.bascase.json"
    p.write_text(json.dumps(VALID), encoding="utf-8")
    cid = c.import_case(p, prefit=False)           # sem prefit no teste (rapido)
    assert cid is not None
    assert any(r.source == "USER" for r in
               __import__("bolt_analysis_studio.validation.case_registry",
                          fromlist=["all_records"]).all_records())
    c.copy_prompt()
    from PyQt6.QtWidgets import QApplication
    assert "bascase_version" in QApplication.clipboard().text()
    refresh_records(); st.new_project()
```

e em `tests/test_user_cases.py`:

```python
def test_cli_import(tmp_path):
    import os
    import subprocess
    import sys
    from pathlib import Path
    src_dir = str(Path(__file__).resolve().parents[1] / "src")
    env = {**os.environ,
           "PYTHONPATH": src_dir + os.pathsep + os.environ.get("PYTHONPATH", ""),
           "BAS_USER_CASES_DIR": str(tmp_path / "uc")}
    p = _write(tmp_path, VALID)
    out = subprocess.run(
        [sys.executable, "-m", "bolt_analysis_studio.validation.report",
         "--import", str(p), "--cap", "300", "--out", str(tmp_path / "html"),
         "--store", str(tmp_path / "store.json")],
        capture_output=True, text=True, env=env)
    assert out.returncode == 0, out.stderr
    assert "ensaio_teste_m12" in out.stdout.lower()
```

(env `BAS_USER_CASES_DIR`: `user_cases.py` deve ler
`os.environ.get("BAS_USER_CASES_DIR")` como override do default — adicionar.)

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar.**

`user_cases.py` (topo): `USER_CASES_DIR = Path(os.environ["BAS_USER_CASES_DIR"]) if os.environ.get("BAS_USER_CASES_DIR") else repo_root() / "Models" / "USER_CASES"` (+ `import os`).

`report.py`: argumento `--import dest="import_path"` + no `main`, antes do
seed: se `args.import_path`: `rec = import_user_case(args.import_path)`;
`prefit_user_case(rec, n_cap=args.cap)`; `todo = [rec]` (o loop existente
simula e salva no store); prints de erros de validação → exit 2 (try/except
ValueError).

`validation_browser.py`: 3 botões novos na fileira (`btn_import` "Importar
caso…", `btn_prompt_copy` "Copiar prompt", `btn_prompt_save` "Salvar
prompt…"), sempre habilitados; sinais `import_case_requested`,
`copy_prompt_requested`, `save_prompt_requested` (sem payload — o controller
abre os diálogos).

`validation_controller.py`:

```python
    def import_case(self, path, prefit: bool = True):
        from ....validation.case_registry import refresh_records
        from ....validation.prefit import prefit_user_case
        from ....validation.user_cases import import_user_case
        try:
            rec = import_user_case(path)
        except (ValueError, OSError) as exc:
            self.import_failed.emit(str(exc))
            return None
        if prefit:
            try:
                prefit_user_case(rec)
            except Exception as exc:              # prefit degrada, import fica
                self.import_failed.emit(f"prefit degradado: {exc}")
        refresh_records()
        self.store.put(simulate_case(rec))
        self.store.save()
        self.browser.refresh_case(rec.case_id)
        return rec.case_id

    def copy_prompt(self) -> None:
        from PyQt6.QtWidgets import QApplication
        from ....validation.intake_prompt import INTAKE_PROMPT
        QApplication.clipboard().setText(INTAKE_PROMPT)
```

+ sinal `import_failed = pyqtSignal(str)`; conectar os sinais do browser:
`import_case_requested` → `_import_dialog` (QFileDialog.getOpenFileName com
filtro `*.bascase.json;;*.json`, chama `import_case`), `copy_prompt_requested`
→ `copy_prompt`, `save_prompt_requested` → `_save_prompt_dialog`
(QFileDialog.getSaveFileName default `BAS_intake_prompt.txt`, escreve
`INTAKE_PROMPT` utf-8).

- [ ] **Step 4: `ast.parse` (4 arquivos) + rodar** — `python -m pytest tests/test_user_cases.py tests/test_validation_browser.py -q` → verde.
- [ ] **Step 5: Commit** — `git commit -m "feat(validation): CLI --import + botoes Importar caso/Copiar prompt/Salvar prompt"`

---

## Task 5: Exemplo + docs + verificação final + STATUS

- [ ] **Step 1: Criar o exemplo** `Models/USER_CASES/exemplo_M12.bascase.json` (o `VALID` do teste com name "Exemplo M12 (sintético)" e description explicando que é demonstração) e rodar `PYTHONPATH=src python -m bolt_analysis_studio.validation.report --import Models/USER_CASES/exemplo_M12.bascase.json` → confere: prefit gravado no JSON, report gerado em `reports/exemplo_m12_sintetico.html`, caso aparece no mestre como fonte USER.
- [ ] **Step 2: Docs** — `docs/VALIDATION_CASE_REPORTS.md`: nova seção "5. Casos do usuário (intake via IA)" (fluxo, onde copiar o prompt, schema, ajuste prévio e como refinar = editar `prefit.overrides` e re-importar/re-simular); seção 17 da aba Documentation ganha 1 parágrafo do intake.
- [ ] **Step 3: Suítes completas** — todos os `tests/test_validation_*.py` + `tests/test_user_cases.py` + `tests/test_prefit.py` + `tests/test_intake_prompt.py` + chrome (browser/module) + regressão de domínio (38) → verde.
- [ ] **Step 4: STATUS** — `docs/superpowers/plans/2026-07-10-user-case-intake-STATUS.md` (entregue, números do exemplo — MAE zero-fit vs prefit —, limitações: prefit transversal ~N×simulações com cap; c_bend só age com bending; curva de imagem fica a critério da IA) + memória.
- [ ] **Step 5: Commit final.**

---

## Self-Review

**Spec coverage:** §4 schema (Task 2 validate), §5 prompt (Task 1), importer+registry (Task 2), prefit doutrina (Task 3), GUI+CLI (Task 4), docs+exemplo (Task 5), erro por campo (validate_bascase + import_failed), refino futuro = editar prefit (documentado Task 5). ✔
**Placeholder scan:** limpo — todos os steps com código/comando. ✔
**Type consistency:** `import_user_case(path, dest_dir=None) -> CaseRecord` (T2) usado em T3/T4/T5; `prefit_user_case(rec, n_cap=None) -> dict` (T3) em T4/T5; `_prefit_overrides` produzido em T2/T3 e consumido no runner (T3); `USER_CASES_DIR` monkeypatch/env (T2/T4); `refresh_records()` (T2) em T4. `ValidationCase(mu_initial=...)` — conferir na execução se o campo é `mu_initial` (dataclass usa `mu_initial`; sim, `validation_cases.py:90`). ✔
**Riscos:** (a) prefit transversal = ~11 simulações com n_cap — segundos a minutos; GUI roda em thread (import_case chamado do diálogo roda inline... mover p/ _ResimWorker-like se travar — aceito v1 com caso pequeno; documentar); (b) `case._user_inputs`/`_prefit_overrides` são atributos dinâmicos num dataclass — padrão já usado no projeto (`model._v2_tuner_overrides`); (c) contagens 128 nos testes atualizadas para não-USER.
