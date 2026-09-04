# Pacote `validation` (Plano A) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (inline) ou subagent-driven-development. Steps em checkbox `- [ ]`.

**Goal:** Pacote `src/bolt_analysis_studio/validation/` que documenta e simula os **128 casos de validação** — registry unificado, runner V2 com decomposição por mecanismo, cache com fingerprint, reports HTML (por caso + geral) e CLI — com o menu V1 "Validation Gallery" gerando via pacote.

**Architecture:** Port da lógica canônica da sandbox (`library_common.geometry_for`/`emb_depth_vdi`/`frozen_constants`, `transfer_validation.inputs_for`, `generate_case_reports.report/master_index`) para módulos testados no produto. Constantes continuam vindo dos JSONs versionados (`joint_calibrations.json` bloco `shared`, `adopted_configs.json` via `knowledge_base.suggest_overrides`). O runner cobre 4 famílias (transversal disp-mode, axial força, creep estático, legado built-in) com degradação honesta para o resto.

**Tech Stack:** Python stdlib + numpy; engine `DynamicStiffnessAnalyzer`; HTML gerado por string (sem template lib); pytest.

## Global Constraints

- `encoding='utf-8'` em TODO I/O; `ast.parse` após cada edição; um commit por tarefa; `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- **NÃO tocar**: engine (`numerical/`), `core/validation_cases.py`, `New_Theory/library_common.py`/`transfer_validation.py` (o follow-up de delegação é outro plano), arquivos foreign (`New_Theory/frontier_polish.py`, `New_Theory/liu2025_nemb_probe.py`).
- V1 `main_window.py`: só o handler `_open_validation_gallery` (linhas ~8208-8239).
- Fatos verificados no código-base (2026-07-10): `CycleSnapshot.dF_0_by_mech: Dict[str,float]` (`dynamic_stiffness_analyzer.py:510`, preenchido em :1585 com `mech.name` ∈ {embedding, creep, wear, thread_fretting, fatigue, rotational_loosening}); `knowledge_base.suggest_overrides(source)->dict`; `calibration.profiles.load_shared_material()->dict`; gallery = `report_data.json["gallery"]` (82 entradas, campos `csv, source, mae, data{x,y}, model{x,y}, n_max, amp_mm, ...`); âncora interna CSVs têm **3 colunas** (cycle, F_kN, F_over_F0); axial: F_amp por tabela curada (P0 sweep: 10 kN; AF sweep: token `AF_*kN` do stem; Li2022ti: 10 kN, M10x1.5 grip 25 mm Rz<10; Liu2017: M12x1.75 grip 30 mm Rz<4).
- Runtime: testes usam `n_cap` pequeno (≤2000 ciclos) — NUNCA rodar 128 casos completos em teste.

## File Structure

**Create:**
```
src/bolt_analysis_studio/validation/
├── __init__.py            # docstring do pacote
├── inputs.py              # Task 1: port ISO/VDI/geometry/frozen_constants/inputs_for
├── case_registry.py       # Task 2: CaseRecord + classificação dos 128
├── runner.py              # Task 3: simulate_case + decomposição
├── store.py               # Task 4: cache JSON + seed da galeria + fingerprint
├── report_html.py         # Task 5: report por caso + geral
└── report.py              # Task 6: CLI (python -m bolt_analysis_studio.validation.report)
tests/test_validation_inputs.py
tests/test_validation_registry.py
tests/test_validation_runner.py
tests/test_validation_store.py
tests/test_validation_report_html.py
```
**Modify:** `src/bolt_analysis_studio/gui/main_window.py` (Task 6, só `_open_validation_gallery`).

---

## Task 1: `inputs.py` — port das primitivas com paridade

**Files:**
- Create: `src/bolt_analysis_studio/validation/__init__.py`, `src/bolt_analysis_studio/validation/inputs.py`
- Test: `tests/test_validation_inputs.py`

**Interfaces:**
- Consumes: `numerical.dynamic_stiffness_analyzer.JointGeometry`; `New_Theory/joint_calibrations.json` (leitura).
- Produces: `Provenance(value, source, note)` (frozen dataclass); `ISO_THREADS: dict`; `emb_depth_vdi(rz_class, n_inner_interfaces, loading="axial") -> (float, dict)`; `vdi_adjacent_classes(rz) -> (str, str)`; `frozen_constants(include_damage=False) -> (dict, dict)`; `geometry_for(bolt_size, grip_mm, ...) -> JointGeometry`; `load_full_curve(csv_rel_path) -> (np.ndarray, np.ndarray)` (**com suporte a CSV de 3 colunas**: usa colunas 0 e última); `inputs_for(case) -> dict` (grip_mm/mu/rz/F_amp_N com proveniência, **estendido às fontes axiais**); `repo_root() -> Path`.

- [ ] **Step 1: Teste falhando** `tests/test_validation_inputs.py`:

```python
import numpy as np


def test_geometry_parity_with_library_common():
    # paridade bit-a-bit com a fonte portada (New_Theory/library_common.py)
    import sys
    from pathlib import Path
    from bolt_analysis_studio.validation.inputs import geometry_for, repo_root
    sys.path.insert(0, str(repo_root() / "New_Theory"))
    import library_common as lc
    for size, grip in [("M16x2.0", 40.0), ("M12x1.75", 30.0), ("M8x1.25", 8.0)]:
        a, b = geometry_for(size, grip), lc.geometry_for(size, grip)
        for f in ("A_s", "L_eff", "d_2", "pitch", "r_bearing", "A_contact"):
            assert getattr(a, f) == getattr(b, f), (size, f)


def test_emb_depth_vdi_table():
    from bolt_analysis_studio.validation.inputs import emb_depth_vdi
    total, br = emb_depth_vdi("Rz<10", n_inner_interfaces=1)
    assert abs(total - 9.5e-6) < 1e-12          # 3 + 2*2.5 + 1*1.5 um (trilho axial §4.6)
    assert br["total_um"] == 9.5
    total4, _ = emb_depth_vdi("Rz<4", n_inner_interfaces=1)
    assert abs(total4 - 3.5e-6) < 1e-12         # 1 + 2*1 + 0.5 (Bolt Science)


def test_frozen_constants_reads_shared_block():
    from bolt_analysis_studio.validation.inputs import frozen_constants
    consts, prov = frozen_constants()
    assert "C_creep" in consts and "emb_depth" not in consts    # input por junta, excluido
    assert "c_D" not in consts                                   # dano off por default
    assert all(p.source == "stage_a" for p in prov.values())
    consts_d, _ = frozen_constants(include_damage=True)
    assert "c_D" in consts_d


def test_load_full_curve_handles_3ancora_interna():
    from bolt_analysis_studio.validation.inputs import load_full_curve
    cyc, ratio = load_full_curve(
        "Models/EXPERIMENTAL_ANCORA/reference_curves/ancora_interna.csv")
    assert len(cyc) == len(ratio) > 3
    assert 0.0 <= ratio[-1] <= 1.5              # coluna F/F0, nao F_kN


def test_inputs_for_transverse_and_axial():
    from bolt_analysis_studio.core.validation_cases import DIGITIZED_CASES
    from bolt_analysis_studio.validation.inputs import inputs_for
    by_src = {}
    for c in DIGITIZED_CASES:
        by_src.setdefault(c.source.name, c)
    liu25 = inputs_for(by_src["LIU_2025"])
    assert liu25["grip_mm"]["prov"] == "assumed"          # regra 2.5d
    assert liu25["F_amp_N"]["value"] == 0.4 * by_src["LIU_2025"].initial_preload_N
    ax = inputs_for(by_src["LIU_2017_P0"])                # fonte axial agora suportada
    assert ax["rz"]["value"] == "Rz<4"                    # fine-ground (§4.6 resolvido)
    assert ax["grip_mm"]["value"] == 30.0
```

- [ ] **Step 2: Rodar e ver falhar** — `python -m pytest tests/test_validation_inputs.py -q` → FAIL (`ModuleNotFoundError`).

- [ ] **Step 3: Implementar.** `__init__.py`:

```python
"""Pacote de validacao do BAS V2 — registry dos 128 casos, runner com
decomposicao por mecanismo, cache com fingerprint e reports HTML.
Spec: docs/superpowers/specs/2026-07-10-validation-case-reports-design.md."""
```

`inputs.py` — **port de `New_Theory/library_common.py` (rev. atual) + `transfer_validation.inputs_for` estendido**. Copiar de lá `Provenance`, `_d2`, `ISO_THREADS`, `_VDI_FZ_UM`, `_VDI_ORDER`, `emb_depth_vdi`, `vdi_adjacent_classes`, `frozen_constants`, `geometry_for` **inteiros e sem alteração de valores** (são a fonte da paridade), trocando só a resolução de raiz e o loader de curva:

```python
"""Primitivas de input com proveniencia — PORT de New_Theory/library_common.py
(2026-07-10, spec §2.4): fonte canonica passa a ser o produto; a sandbox
delegara aqui em follow-up. Valores identicos aos da campanha (teste de
paridade). Constantes vem dos JSONs versionados (bloco shared)."""
from __future__ import annotations

import json
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

from ..numerical.dynamic_stiffness_analyzer import JointGeometry


def repo_root() -> Path:
    root = Path(__file__).resolve().parents[3]
    if not (root / "New_Theory").exists():       # layout sem src/ intermediario
        root = Path(__file__).resolve().parents[2]
    return root


SHARED_JSON = repo_root() / "New_Theory" / "joint_calibrations.json"

# ... [Provenance, _d2, ISO_THREADS, _VDI_FZ_UM, _VDI_ORDER, emb_depth_vdi,
#      vdi_adjacent_classes, frozen_constants, geometry_for copiados VERBATIM
#      de New_Theory/library_common.py linhas 29-131 e 140-172, com
#      SHARED_JSON acima como default de frozen_constants] ...


def load_full_curve(csv_rel_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Curva de referencia (repo-relativa). 2 colunas (cycle, ratio) ou
    3 colunas âncora interna (cycle, F_kN, F_over_F0) — sempre col 0 e a ULTIMA."""
    d = np.genfromtxt(repo_root() / csv_rel_path, delimiter=",",
                      skip_header=1, encoding="utf-8")
    return d[:, 0], d[:, -1]


# --- inputs por caso (port de transfer_validation.inputs_for, estendido) ----
F_AMP_RATIO = 0.4          # literatura Pai&Hess 2002 (0.38-0.49 medido)
RZ_DEFAULT = "Rz10-40"
SOURCE_INPUTS = {
    "LIU_2025":      dict(grip=None, mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "BAUER_2024":    dict(grip=("bolt", "paper"), mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "LU_2024":       dict(grip=None, mu=(0.18, "paper"), rz=RZ_DEFAULT),
    "ICMEZ_2025":    dict(grip=("csv", "paper"), mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "YANG_2019":     dict(grip=None, mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "ROUSSEAU_2025": dict(grip=("csv", "paper"), mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "KARLSEN_2022":  dict(grip=None, mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    # fontes axiais (tabela curada de calibrate_axial.py CONDITIONS):
    "LIU_2017_P0":   dict(grip=(30.0, "paper"), mu=(0.15, "assumed"), rz="Rz<4"),
    "LIU_2017_AF":   dict(grip=(30.0, "paper"), mu=(0.15, "assumed"), rz="Rz<4"),
    "LI_2022TI":     dict(grip=(25.0, "assumed"), mu=(0.15, "assumed"), rz="Rz<10"),
}
ROUSSEAU_GRIPS = {"t10": 25.0, "t12": 29.0, "t14": 33.0}
ICMEZ_GRIPS = {"lk13p8": 13.8, "lk19p8": 19.8}
BAUER_GRIPS = {"M8": 8.0, "M12": 12.0}


def _d_mm(case) -> float:
    return float(case.bolt_size.split("x")[0][1:])


def inputs_for(case) -> dict:
    """grip/mu/rz/F_amp com proveniencia. Fontes fora de SOURCE_INPUTS caem na
    regra assumed (grip 2.5d, mu 0.15, Rz default) — degradacao honesta."""
    src = SOURCE_INPUTS.get(case.source.name,
                            dict(grip=None, mu=(0.15, "assumed"), rz=RZ_DEFAULT))
    stem = Path(getattr(case, "reference_csv_path", "") or "").stem
    g = src["grip"]
    if g is None:
        grip = dict(value=2.5 * _d_mm(case), prov="assumed")
    elif isinstance(g[0], float):
        grip = dict(value=g[0], prov=g[1])
    elif g[0] == "bolt":
        key = "M8" if case.bolt_size.startswith("M8") else "M12"
        grip = dict(value=BAUER_GRIPS[key], prov="paper")
    else:  # "csv": grip codificado no nome do arquivo
        table = ROUSSEAU_GRIPS if "rousseau" in stem else ICMEZ_GRIPS
        key = next((k for k in table if k in stem), None)
        grip = (dict(value=table[key], prov="paper") if key
                else dict(value=2.5 * _d_mm(case), prov="assumed"))
    return dict(
        grip_mm=grip,
        mu=dict(value=src["mu"][0], prov=src["mu"][1]),
        rz=dict(value=src["rz"], prov="assumed"),
        F_amp_N=dict(value=F_AMP_RATIO * case.initial_preload_N,
                     prov="literature (Pai&Hess 2002: 0.38-0.49 medido)"))
```

NOTA para o implementador: onde o esqueleto diz "copiados VERBATIM", abrir
`New_Theory/library_common.py` e copiar os blocos citados sem editar valores —
o teste de paridade pega qualquer desvio. `SOURCE_INPUTS` acima espelha
`transfer_validation.SOURCE_INPUTS` (incl. Rousseau `("csv","paper")`) +
extensão axial da tabela `CONDITIONS` de `calibrate_axial.py`.

- [ ] **Step 4: `ast.parse` + rodar** — `python -m pytest tests/test_validation_inputs.py -q` → **5 passed**.
- [ ] **Step 5: Commit** — `git add src/bolt_analysis_studio/validation/ tests/test_validation_inputs.py && git commit -m "feat(validation): inputs.py — port com paridade de library_common + inputs_for estendido (Plano A)"`

---

## Task 2: `case_registry.py` — os 128 casos unificados

**Files:**
- Create: `src/bolt_analysis_studio/validation/case_registry.py`
- Test: `tests/test_validation_registry.py`

**Interfaces:**
- Consumes: `core.validation_cases.ValidationCaseManager.get_all_cases()` (128), `inputs.repo_root/load_full_curve`.
- Produces: `CaseRecord` (dataclass: `case_id, name, source, family, case_class, caveats, validation_case, csv_path, apparatus_note_path, gallery_entry`); `all_records() -> List[CaseRecord]`; `record(case_id) -> Optional[CaseRecord]`. `family ∈ {"transverse","axial","creep","other"}`; `case_class ∈ {"full_curve","final_ratio"}`.

- [ ] **Step 1: Teste falhando** `tests/test_validation_registry.py`:

```python
def test_registry_covers_all_cases_with_unique_ids():
    from bolt_analysis_studio.validation.case_registry import all_records
    recs = all_records()
    assert len(recs) == 128
    ids = [r.case_id for r in recs]
    assert len(set(ids)) == 128


def test_classification_and_families():
    from bolt_analysis_studio.validation.case_registry import all_records
    recs = all_records()
    by_class = {}
    for r in recs:
        by_class.setdefault(r.case_class, []).append(r)
    assert len(by_class["full_curve"]) >= 110         # digitalizados + âncora interna legado c/ CSV
    assert len(by_class["final_ratio"]) >= 8          # built-in sem CSV
    fams = {r.family for r in recs}
    assert {"transverse", "axial", "creep"} <= fams
    axial = [r for r in recs if r.family == "axial"]
    assert all(r.validation_case.transverse_displacement_mm == 0 for r in axial)


def test_gallery_matching_and_caveats():
    from bolt_analysis_studio.validation.case_registry import all_records
    recs = all_records()
    with_gallery = [r for r in recs if r.gallery_entry is not None]
    assert len(with_gallery) == 82                    # cobertura atual da galeria
    fract = [r for r in recs if any("fratura" in c for c in r.caveats)]
    assert fract                                       # caudas de fratura marcadas


def test_record_lookup_and_apparatus_note():
    from bolt_analysis_studio.validation.case_registry import all_records, record
    recs = all_records()
    r0 = next(r for r in recs if r.gallery_entry is not None)
    assert record(r0.case_id) is r0 or record(r0.case_id).case_id == r0.case_id
    noted = [r for r in recs if r.apparatus_note_path]
    assert noted and all(n.exists() for n in {r.apparatus_note_path for r in noted})
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** `case_registry.py`:

```python
"""Registry unificado dos 128 casos de validacao (spec §3): ValidationCase +
classe do dado + paths (CSV, apparatus_notes, galeria). Leitura pura — quem
simula e' o runner; quem cacheia e' o store."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from ..core.validation_cases import ValidationCaseManager
from .inputs import repo_root

_AXIAL_SOURCES = {"LIU_2017_P0", "LIU_2017_AF", "LI_2022TI"}
_NOTES_DIR = "Models/CALIBRATION_AND_VALIDATION/curve_library/apparatus_notes"
# fonte -> arquivo de nota de aparato (existentes no repo)
_SOURCE_NOTES = {
    "LIU_2025": "liu2025_scirep_M16.md", "BAUER_2024": "bauer2024_efa.md",
    "LU_2024": "lu2024_sensors_M8.md", "ICMEZ_2025": "demir2024_ejrnd_M8.md",
    "YANG_2019": "yang2019_sv_M10.md", "YANG_2021": "yang2021_sv_combined.md",
    "ROUSSEAU_2025": "rousseau2025_materials_M12.md",
    "ROUSSEAU_HDPE": "rousseau2025_materials_M12.md",
    "KARLSEN_2022": "karlsen2022_M30M42.md", "SANDIA_2021": "sandia2021_cbeam.md",
    "LIU_2022": "liu2022_istruc_retightening.md",
    "LIU_2022_RET": "liu2022_istruc_retightening.md",
    "LIU_2017_P0": "liu2017_triboint_axial.md",
    "LIU_2017_AF": "liu2017_triboint_axial.md",
    "LI_2022": "li2022_marstruc_contact_creep.md",
    "LI_2022TI": "li2022_triboint_axial_freq.md",
    "WANG_2020": "wang2020_aime_pretightening.md",
}
# tokens de caveat (espelha exclusoes pre-registradas da campanha + notas)
_CAVEAT_TOKENS = {
    "hdpe": "par polimérico (HDPE) — fora do domínio metálico declarado",
    "vibralock": "dispositivo de travamento — out-of-model declarado",
    "varamp": "protocolo de amplitude variável",
    "fig2_single": "ensaio até fratura — cauda fora do afrouxamento puro",
    "full": "cauda com fratura por fadiga — trim recomendado",
    "creep": "creep estático (eixo x em MINUTOS; freq 1/60 Hz)",
}


@dataclass
class CaseRecord:
    case_id: str
    name: str
    source: str
    family: str                 # transverse | axial | creep | other
    case_class: str             # full_curve | final_ratio
    caveats: List[str]
    validation_case: object
    csv_path: Optional[Path]
    apparatus_note_path: Optional[Path]
    gallery_entry: Optional[dict]


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


@lru_cache(maxsize=1)
def _gallery_by_stem() -> Dict[str, dict]:
    p = repo_root() / "New_Theory" / "report_data.json"
    if not p.exists():
        return {}
    try:
        gal = json.loads(p.read_text(encoding="utf-8")).get("gallery", [])
    except (OSError, json.JSONDecodeError):
        return {}
    return {e["csv"]: e for e in gal}


def _build_record(case) -> CaseRecord:
    root = repo_root()
    rel = getattr(case, "reference_csv_path", "") or ""
    csv_path = (root / rel) if rel else None
    has_curve = csv_path is not None and csv_path.exists()
    stem = Path(rel).stem if rel else ""
    src = case.source.name
    if src in _AXIAL_SOURCES:
        fam = "axial"
    elif "creep" in stem or (src == "LI_2022" and case.frequency_Hz < 0.05):
        fam = "creep"
    elif case.transverse_displacement_mm > 0:
        fam = "transverse"
    else:
        fam = "other"
    caveats = [msg for tok, msg in _CAVEAT_TOKENS.items() if tok in stem.lower()]
    note = _SOURCE_NOTES.get(src)
    note_path = (root / _NOTES_DIR / note) if note else None
    if note_path is not None and not note_path.exists():
        note_path = None
    return CaseRecord(
        case_id=stem or _slug(case.name), name=case.name, source=src,
        family=fam, case_class="full_curve" if has_curve else "final_ratio",
        caveats=caveats, validation_case=case,
        csv_path=csv_path if has_curve else None,
        apparatus_note_path=note_path,
        gallery_entry=_gallery_by_stem().get(stem))


@lru_cache(maxsize=1)
def all_records() -> List[CaseRecord]:
    recs = [_build_record(c) for c in ValidationCaseManager.get_all_cases()]
    seen: Dict[str, int] = {}
    for r in recs:                       # ids unicos (colisao improvavel, mas barata)
        if r.case_id in seen:
            seen[r.case_id] += 1
            r.case_id = f"{r.case_id}_{seen[r.case_id]}"
        else:
            seen[r.case_id] = 0
    return recs


def record(case_id: str) -> Optional[CaseRecord]:
    return next((r for r in all_records() if r.case_id == case_id), None)
```

- [ ] **Step 4: `ast.parse` + rodar** — `python -m pytest tests/test_validation_registry.py -q` → **4 passed**. Se contagens exatas divergirem (ex.: `>=110`), ajustar o limiar do teste ao valor REAL impresso — os limites do teste documentam o dataset, não o contrário.
- [ ] **Step 5: Commit** — `git commit -m "feat(validation): case_registry — 128 casos unificados (classe, familia, caveats, galeria) (Plano A)"`

---

## Task 3: `runner.py` — simulação com decomposição por mecanismo

**Files:**
- Create: `src/bolt_analysis_studio/validation/runner.py`
- Test: `tests/test_validation_runner.py`

**Interfaces:**
- Consumes: Task 1 (`frozen_constants, emb_depth_vdi, geometry_for, inputs_for, load_full_curve`), Task 2 (`CaseRecord`), `knowledge_base.suggest_overrides`, `DynamicStiffnessAnalyzer/JointMaterial`.
- Produces: `CaseResult` (dataclass com `to_dict()/from_dict()`): `case_id, ok, error, cycles: List[float], ratio: List[float], mae, rmse, maxerr, maxerr_at, final_pred, final_data, decomp: Dict[str, List[float]], D_final, config_used: dict, generated_at: str, engine_fingerprint: str`; `simulate_case(record, n_cap=None, now=None) -> CaseResult`; `engine_fingerprint() -> str`.

- [ ] **Step 1: Teste falhando** `tests/test_validation_runner.py`:

```python
import numpy as np


def _short_transverse_record():
    from bolt_analysis_studio.validation.case_registry import all_records
    recs = [r for r in all_records()
            if r.family == "transverse" and r.case_class == "full_curve"]
    return min(recs, key=lambda r: r.validation_case.n_cycles)


def test_simulate_transverse_with_decomposition():
    from bolt_analysis_studio.validation.runner import simulate_case
    rec = _short_transverse_record()
    res = simulate_case(rec, n_cap=1500)
    assert res.ok and res.error is None
    assert res.mae is not None and 0.0 <= res.mae < 1.0
    assert len(res.cycles) == len(res.ratio) > 10
    # decomposicao: soma dos mecanismos == perda total (fechamento exato do engine)
    total_loss = 1.0 - res.ratio[-1]
    decomp_sum = sum(v[-1] for v in res.decomp.values())
    assert abs(decomp_sum - total_loss) < 1e-6
    assert set(res.decomp) >= {"embedding", "creep", "wear"}


def test_simulate_axial_force_mode():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.runner import simulate_case
    rec = next(r for r in all_records() if r.family == "axial")
    res = simulate_case(rec, n_cap=1500)
    assert res.ok
    assert res.config_used["mode"] == "force"
    assert res.config_used["F_amp_N"] > 0


def test_final_ratio_case_compares_endpoint():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.runner import simulate_case
    rec = next(r for r in all_records() if r.case_class == "final_ratio")
    res = simulate_case(rec, n_cap=1500)
    assert res.ok
    assert res.final_data is not None            # expected_final_preload_ratio
    assert res.mae is None or res.mae >= 0       # sem curva -> mae None ou pontos esparsos


def test_unparameterized_loading_degrades_honestly():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.runner import simulate_case
    others = [r for r in all_records() if r.family == "other"
              and r.validation_case.transverse_displacement_mm == 0]
    if not others:                                # dataset pode nao ter 'other'
        return
    res = simulate_case(others[0], n_cap=500)
    assert (not res.ok) and "proveni" in res.error


def test_fingerprint_stable_and_result_roundtrip():
    from bolt_analysis_studio.validation.runner import (CaseResult,
                                                        engine_fingerprint,
                                                        simulate_case)
    assert engine_fingerprint() == engine_fingerprint()
    rec = _short_transverse_record()
    res = simulate_case(rec, n_cap=300, now="2026-07-10T00:00:00")
    d = res.to_dict()
    back = CaseResult.from_dict(d)
    assert back.case_id == res.case_id and back.mae == res.mae
    assert back.generated_at == "2026-07-10T00:00:00"
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** `runner.py`:

```python
"""Runner canonico de casos de validacao (spec §3): engine V2 + constantes com
proveniencia (bloco shared congelado + adotadas per-rig via knowledge_base) +
decomposicao por mecanismo (CycleSnapshot.dF_0_by_mech; a soma fecha exatamente
F0*(1-ratio) — mesma garantia do plot Mechanism Decomposition do Run)."""
from __future__ import annotations

import datetime
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from ..calibration import knowledge_base as kb
from ..numerical.dynamic_stiffness_analyzer import (DynamicStiffnessAnalyzer,
                                                    JointMaterial)
from .case_registry import CaseRecord
from .inputs import (emb_depth_vdi, frozen_constants, geometry_for,
                     inputs_for, load_full_curve, repo_root)

_MAX_POINTS = 400            # amostragem das curvas/decomposicao no resultado
_AXIAL_F_AMP = {"LIU_2017_P0": 10e3, "LI_2022TI": 10e3}   # calibrate_axial CONDITIONS


@dataclass
class CaseResult:
    case_id: str
    ok: bool
    error: Optional[str] = None
    cycles: List[float] = field(default_factory=list)
    ratio: List[float] = field(default_factory=list)
    mae: Optional[float] = None
    rmse: Optional[float] = None
    maxerr: Optional[float] = None
    maxerr_at: Optional[float] = None
    final_pred: Optional[float] = None
    final_data: Optional[float] = None
    decomp: Dict[str, List[float]] = field(default_factory=dict)
    D_final: float = 0.0
    config_used: dict = field(default_factory=dict)
    generated_at: str = ""
    engine_fingerprint: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "CaseResult":
        return cls(**{k: v for k, v in d.items()
                      if k in cls.__dataclass_fields__})


def engine_fingerprint() -> str:
    """sha256 curto do estado que muda predicoes: bloco shared + configs
    adotadas + versao das constantes default do engine."""
    consts, _ = frozen_constants()
    adopted = {s: kb.adopted_config(s) for s in kb.adopted_sources()}
    blob = json.dumps({"shared": consts, "adopted": adopted},
                      sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


def _adopted_overrides(source: str) -> dict:
    """Config adotada da fonte (best-match por prefixo, como o gerador da
    campanha) traduzida a campos de engine."""
    for s in kb.adopted_sources():
        if source.split("_")[0].upper() in s.upper():
            return kb.suggest_overrides(s)
    return {}


def _axial_f_amp(source: str, stem: str) -> Optional[float]:
    if source in _AXIAL_F_AMP:
        return _AXIAL_F_AMP[source]
    m = re.search(r"AF_([\dp]+)kN", stem)         # liu2017_axial_AF_8p75kN
    if m:
        return float(m.group(1).replace("p", ".")) * 1e3
    return None


def _loading_for(rec: CaseRecord) -> dict:
    case = rec.validation_case
    inp = inputs_for(case)
    if rec.family == "transverse":
        return dict(mode="displacement", delta_mm=case.transverse_displacement_mm,
                    F_amp_N=inp["F_amp_N"]["value"], theta=np.pi / 2,
                    inputs=inp)
    if rec.family == "axial":
        stem = rec.csv_path.stem if rec.csv_path else ""
        f_amp = _axial_f_amp(rec.source, stem)
        if f_amp is None:
            raise ValueError("F_amp axial sem proveniência para este caso")
        return dict(mode="force", delta_mm=0.0, F_amp_N=f_amp, theta=0.0,
                    inputs=inp)
    if rec.family == "creep":
        return dict(mode="force", delta_mm=0.0, F_amp_N=0.0, theta=0.0,
                    inputs=inp)
    raise ValueError("carregamento sem proveniência no runner v1 "
                     "(família 'other': modal/força não parametrizado)")


def _sample_idx(n: int) -> np.ndarray:
    if n <= _MAX_POINTS:
        return np.arange(n + 1)
    return np.unique(np.linspace(0, n, _MAX_POINTS).astype(int))


def simulate_case(rec: CaseRecord, n_cap: Optional[int] = None,
                  now: Optional[str] = None) -> CaseResult:
    case = rec.validation_case
    stamp = now or datetime.datetime.now().isoformat(timespec="seconds")
    fp = engine_fingerprint()
    try:
        load = _loading_for(rec)
    except ValueError as exc:
        return CaseResult(case_id=rec.case_id, ok=False, error=str(exc),
                          generated_at=stamp, engine_fingerprint=fp)
    try:
        inp = load["inputs"]
        consts, _ = frozen_constants()
        emb_m, emb_br = emb_depth_vdi(inp["rz"]["value"], n_inner_interfaces=1)
        geom = geometry_for(case.bolt_size, grip_mm=inp["grip_mm"]["value"])
        overrides = _adopted_overrides(rec.source)
        mu = inp["mu"]["value"]
        kw = dict(emb_depth=emb_m, mu_thread=mu, mu_bearing=mu,
                  conform_driver="effective", **consts)
        fields = JointMaterial.__dataclass_fields__
        for k, v in overrides.items():            # adotadas per-rig por cima
            if k in fields:
                kw[k] = v
        mat = JointMaterial(**kw)
        F0 = case.initial_preload_N
        ana = DynamicStiffnessAnalyzer(geom, mat, F0)

        # curva de referencia / n de ciclos
        if rec.case_class == "full_curve":
            cyc_d, r_d = load_full_curve(str(rec.csv_path.relative_to(repo_root())))
            r_d = r_d / max(r_d[0], 1e-9)
            n_max = int(cyc_d[-1])
        else:
            cyc_d, r_d = None, None
            n_max = int(case.n_cycles)
        if n_cap:
            n_max = min(n_max, int(n_cap))

        ratio = np.empty(n_max + 1)
        ratio[0] = 1.0
        cum = {}
        cum_hist: Dict[str, np.ndarray] = {}
        for n in range(1, n_max + 1):
            ana.step_cycle(load["F_amp_N"], load["theta"], case.frequency_Hz,
                           delta_amp=(load["delta_mm"] * 1e-3
                                      if load["mode"] == "displacement" else None))
            ratio[n] = max(ana.state.F_0, 0.0) / F0
            snap = ana.history[-1]
            for mech, dF in snap.dF_0_by_mech.items():
                cum[mech] = cum.get(mech, 0.0) + dF
                cum_hist.setdefault(mech, np.zeros(n_max + 1))[n] = cum[mech]

        idx = _sample_idx(n_max)
        mae = rmse = maxerr = maxerr_at = final_data = None
        if cyc_d is not None:
            keep = cyc_d <= n_max
            cd, rd = cyc_d[keep], r_d[keep]
            pred = np.interp(cd, np.arange(n_max + 1), ratio)
            err = np.abs(pred - rd)
            if len(err):
                mae = float(np.mean(err)); rmse = float(np.sqrt(np.mean(err**2)))
                k = int(np.argmax(err))
                maxerr, maxerr_at = float(err[k]), float(cd[k])
                final_data = float(rd[-1])
        else:
            final_data = float(case.expected_final_preload_ratio)

        return CaseResult(
            case_id=rec.case_id, ok=True,
            cycles=idx.astype(float).tolist(), ratio=ratio[idx].tolist(),
            mae=mae, rmse=rmse, maxerr=maxerr, maxerr_at=maxerr_at,
            final_pred=float(ratio[-1]), final_data=final_data,
            decomp={m: (h / F0)[idx].tolist() for m, h in cum_hist.items()},
            D_final=float(ana.state.D),
            config_used=dict(mode=load["mode"], F_amp_N=load["F_amp_N"],
                             delta_mm=load["delta_mm"], mu=mu,
                             grip_mm=inp["grip_mm"]["value"],
                             rz=inp["rz"]["value"], emb_um=emb_br["total_um"],
                             overrides=overrides, n_max=n_max),
            generated_at=stamp, engine_fingerprint=fp)
    except Exception as exc:                       # degrada, nao derruba o batch
        return CaseResult(case_id=rec.case_id, ok=False,
                          error=f"{type(exc).__name__}: {exc}",
                          generated_at=stamp, engine_fingerprint=fp)
```

NOTA de sinal: `decomp` guarda a perda CUMULATIVA **normalizada por F0** (mesma
unidade do ratio) — a soma dos mecanismos em qualquer ciclo == `1 - ratio` ali
(fechamento exato do engine; se o teste de fechamento falhar > 1e-6, investigar
antes de afrouxar — é a garantia do plot do Run).

- [ ] **Step 4: `ast.parse` + rodar** — `python -m pytest tests/test_validation_runner.py -q` → **5 passed** (runtime ~10-30 s).
- [ ] **Step 5: Commit** — `git commit -m "feat(validation): runner — simulate_case com decomposicao por mecanismo exata (Plano A)"`

---

## Task 4: `store.py` — cache com fingerprint + seed da galeria

**Files:**
- Create: `src/bolt_analysis_studio/validation/store.py`
- Test: `tests/test_validation_store.py`

**Interfaces:**
- Consumes: Task 3 (`CaseResult`, `engine_fingerprint`), Task 2 (`all_records`), `report_data.json`.
- Produces: `ValidationStore(path=None)` com `get(case_id) -> Optional[CaseResult]`, `put(result)`, `is_stale(case_id) -> bool`, `seed_from_gallery() -> int`, `save()/load()`, `all_ids() -> List[str]`. Default path: `Models/CALIBRATION_AND_VALIDATION/validation_store.json`.

- [ ] **Step 1: Teste falhando** `tests/test_validation_store.py`:

```python
def test_roundtrip_and_staleness(tmp_path):
    from bolt_analysis_studio.validation.runner import CaseResult, engine_fingerprint
    from bolt_analysis_studio.validation.store import ValidationStore
    st = ValidationStore(path=tmp_path / "store.json")
    res = CaseResult(case_id="x", ok=True, mae=0.05,
                     generated_at="2026-07-10T00:00:00",
                     engine_fingerprint=engine_fingerprint())
    st.put(res); st.save()
    st2 = ValidationStore(path=tmp_path / "store.json")
    assert st2.get("x").mae == 0.05
    assert st2.is_stale("x") is False
    stale = CaseResult(case_id="y", ok=True, engine_fingerprint="deadbeef0000")
    st2.put(stale)
    assert st2.is_stale("y") is True              # fingerprint diverge
    assert st2.is_stale("nao-existe") is True     # ausente = stale


def test_seed_from_gallery(tmp_path):
    from bolt_analysis_studio.validation.store import ValidationStore
    st = ValidationStore(path=tmp_path / "store.json")
    n = st.seed_from_gallery()
    assert n == 82
    seeded = st.get("liu2025_M16_amp0p25")
    assert seeded is not None and seeded.ok
    assert seeded.mae is not None
    assert seeded.decomp == {}                    # seed nao tem decomposicao
    assert seeded.engine_fingerprint == "gallery-seed"
    assert st.is_stale("liu2025_M16_amp0p25")     # seed e' sempre stale (honesto)
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** `store.py`:

```python
"""Cache persistente dos resultados de validacao (spec §3): um JSON com um
CaseResult por caso + fingerprint do engine. Seed inicial importado da galeria
(report_data.json) para consulta instantanea — marcado 'gallery-seed' e sempre
stale (a primeira re-simulacao o substitui e preenche a decomposicao)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .inputs import repo_root
from .runner import CaseResult, engine_fingerprint

_DEFAULT = "Models/CALIBRATION_AND_VALIDATION/validation_store.json"


class ValidationStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else repo_root() / _DEFAULT
        self._data: Dict[str, dict] = {}
        self.load()

    def load(self) -> None:
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                self._data = {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._data, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.path)                    # escrita atomica (padrao profiles.py)

    def get(self, case_id: str) -> Optional[CaseResult]:
        d = self._data.get(case_id)
        return CaseResult.from_dict(d) if d else None

    def put(self, result: CaseResult) -> None:
        self._data[result.case_id] = result.to_dict()

    def all_ids(self) -> List[str]:
        return sorted(self._data)

    def is_stale(self, case_id: str) -> bool:
        d = self._data.get(case_id)
        if not d:
            return True
        return d.get("engine_fingerprint") != engine_fingerprint()

    def seed_from_gallery(self) -> int:
        """Importa as 82 entradas da galeria como resultados 'gallery-seed'
        (sem decomposicao; sempre stale). Nao sobrescreve resultados reais."""
        p = repo_root() / "New_Theory" / "report_data.json"
        if not p.exists():
            return 0
        gallery = json.loads(p.read_text(encoding="utf-8")).get("gallery", [])
        n = 0
        for e in gallery:
            cid = e["csv"]
            cur = self._data.get(cid)
            if cur and cur.get("engine_fingerprint") != "gallery-seed":
                continue                          # resultado real vence o seed
            self._data[cid] = CaseResult(
                case_id=cid, ok=True,
                cycles=[float(x) for x in e["model"]["x"]],
                ratio=[float(y) for y in e["model"]["y"]],
                mae=float(e["mae"]),
                rmse=float(e.get("rmse_interp") or 0) or None,
                maxerr=float(e.get("maxerr_interp") or 0) or None,
                maxerr_at=float(e.get("maxerr_at") or 0) or None,
                final_pred=float(e["model"]["y"][-1]),
                final_data=float(e["data"]["y"][-1]),
                config_used=dict(label=e.get("label", ""),
                                 amp_mm=e.get("amp_mm")),
                generated_at="(campanha)",
                engine_fingerprint="gallery-seed").to_dict()
            n += 1
        return n
```

- [ ] **Step 4: `ast.parse` + rodar** — `python -m pytest tests/test_validation_store.py -q` → **2 passed**.
- [ ] **Step 5: Commit** — `git commit -m "feat(validation): store — cache com fingerprint + seed da galeria (Plano A)"`

---

## Task 5: `report_html.py` — report por caso (com decomposição) + geral

**Files:**
- Create: `src/bolt_analysis_studio/validation/report_html.py`
- Test: `tests/test_validation_report_html.py`

**Interfaces:**
- Consumes: Tasks 1-4; `knowledge_base.adopted_config`; `calibration.profiles.load_shared_material`.
- Produces: `case_report_html(record, result) -> str`; `master_report_html(records, results: Dict[str,CaseResult]) -> str`; `write_reports(out_dir=None, results=None) -> Path` (escreve `reports/<case_id>.html` p/ TODOS os records + `validation_report.html`; default out = `New_Theory/validation_html/` — onde o menu V1 já procura). `FLOORS` (pisos de repetibilidade, port do `convergence_indicator`).

- [ ] **Step 1: Teste falhando** `tests/test_validation_report_html.py`:

```python
def _fake_result(case_id, with_decomp=True):
    from bolt_analysis_studio.validation.runner import CaseResult
    decomp = ({"embedding": [0, 0.03, 0.05], "wear": [0, 0.01, 0.04],
               "creep": [0, 0.0, 0.01]} if with_decomp else {})
    return CaseResult(case_id=case_id, ok=True, cycles=[0, 500, 1000],
                      ratio=[1.0, 0.96, 0.90], mae=0.031, rmse=0.04,
                      maxerr=0.06, maxerr_at=800, final_pred=0.90,
                      final_data=0.88, decomp=decomp,
                      generated_at="2026-07-10T12:00:00",
                      engine_fingerprint="abc123")


def test_case_report_sections_full_curve():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.report_html import case_report_html
    rec = next(r for r in all_records()
               if r.case_class == "full_curve" and r.family == "transverse")
    html = case_report_html(rec, _fake_result(rec.case_id))
    assert "Condições de contorno" in html          # utf-8 intacto
    assert "Modelo MSD" in html
    assert "Decomposição por mecanismo" in html     # §4 nova (pedido do professor)
    assert "embedding" in html and "wear" in html
    assert "MAE" in html and "0.031" in html
    assert 'charset="utf-8"' in html


def test_case_report_degrades_without_decomp_and_curve():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.report_html import case_report_html
    rec = next(r for r in all_records() if r.case_class == "final_ratio")
    html = case_report_html(rec, _fake_result(rec.case_id, with_decomp=False))
    assert "re-simule" in html.lower()              # aviso do seed sem decomposicao
    assert "sem curva digitalizada" in html.lower() or "ratio final" in html.lower()


def test_case_report_shows_error_result():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.report_html import case_report_html
    from bolt_analysis_studio.validation.runner import CaseResult
    rec = all_records()[0]
    res = CaseResult(case_id=rec.case_id, ok=False, error="sem proveniência X",
                     generated_at="t", engine_fingerprint="f")
    html = case_report_html(rec, res)
    assert "sem proveniência X" in html


def test_write_reports_all_cases(tmp_path):
    from bolt_analysis_studio.validation.report_html import write_reports
    out = write_reports(out_dir=tmp_path)           # resultados: store/seed/None
    reports = list((tmp_path / "reports").glob("*.html"))
    assert len(reports) == 128
    master = (tmp_path / "validation_report.html").read_text(encoding="utf-8")
    assert "128" in master
    assert "full_curve" in master or "curva completa" in master
    assert "gerado em" in master.lower() or "Gerado" in master
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** `report_html.py` — port de `New_Theory/generate_case_reports.py` com estas mudanças estruturais (copiar `_CSS`, `_fnum`, `_row`, `_svg` e a estrutura do `report()`/`master_index()` de lá, adaptando):

1. **Fontes de dados**: em vez de `entry` da galeria, recebe `(CaseRecord, CaseResult)`. Curva do dado: `load_full_curve(rec.csv_path)` quando `full_curve` (senão pontos esparsos de `case.experimental_data` / ratio final). Curva do modelo: `result.cycles/ratio`. Erros: `result.mae/rmse/maxerr/maxerr_at` (— quando None).
2. **§4 nova "Decomposição por mecanismo"** (após o Resultado): área empilhada SVG das séries cumulativas `result.decomp` (mesma técnica do `_svg`: polígonos empilhados, um `<path>` por mecanismo com paleta fixa `{embedding:"#2f6f8f", creep:"#8f6f2f", wear:"#b3452c", rotational_loosening:"#5f8f2f", thread_fretting:"#7f5fa0", fatigue:"#a05f5f"}`) + tabela de shares finais (`mech: 100*valor_final/max(soma,1e-12)%`). Quando `result.decomp` vazio (seed): `<p class="verd">Resultado de snapshot da campanha — re-simule o caso para obter a decomposição por mecanismo.</p>`.
3. **Degradação honesta**: `final_ratio` → banner "sem curva digitalizada — comparação pontual (ratio final esperado {x})"; `result.ok=False` → banner de erro com `result.error`, sem seções de resultado; caveats do record listados na seção Veredicto/caveats com link relativo à nota de aparato quando existir.
4. **Constantes**: manter tabela per-rig (`kb.adopted_config` best-match, `PROV`) + shared (`load_shared_material`, `SHARED_PROV`) do port; adicionar linha `engine fingerprint / gerado em` no rodapé com `result.engine_fingerprint/generated_at`.
5. **Master**: agrupar por fonte como o port; adicionar colunas `classe` e `família`; cabeçalho com estatísticas globais só dos results `ok` com `mae` (média, mediana), pisos `FLOORS` portados de `convergence_indicator.py` (dict literal com comentário de proveniência) e contagem `mae <= piso+0.02`; carimbo global `gerado em ... · engine <fingerprint>`; casos com erro em seção própria "não simuláveis (degradação honesta)".
6. **`write_reports(out_dir=None, results=None)`**: `out_dir` default `repo_root()/"New_Theory"/"validation_html"`; `results` default = `ValidationStore()` (com `seed_from_gallery()` se vazio) → `{cid: store.get(cid)}`; para records sem resultado usa `CaseResult(ok=False, error="nunca simulado — rode o CLI --all")`. Escreve todos com `encoding="utf-8"`, retorna o path do master.

- [ ] **Step 4: `ast.parse` + rodar** — `python -m pytest tests/test_validation_report_html.py -q` → **4 passed**.
- [ ] **Step 5: Commit** — `git commit -m "feat(validation): report_html — 128 reports com decomposicao por mecanismo + geral com pisos (Plano A)"`

---

## Task 6: CLI + rewire do menu V1

**Files:**
- Create: `src/bolt_analysis_studio/validation/report.py`
- Modify: `src/bolt_analysis_studio/gui/main_window.py` (só `_open_validation_gallery`, ~8208)
- Test: append em `tests/test_validation_report_html.py`

**Interfaces:**
- Produces: `python -m bolt_analysis_studio.validation.report [--all] [--case ID] [--from-store] [--cap N] [--out DIR]`; função `ensure_reports(regenerate=False) -> Path` (usada pelo menu V1: seed+write se master ausente, retorna path do master).

- [ ] **Step 1: Teste falhando** — append:

```python
def test_ensure_reports_generates_master(tmp_path, monkeypatch):
    from bolt_analysis_studio.validation import report as cli
    master = cli.ensure_reports(out_dir=tmp_path)
    assert master.name == "validation_report.html" and master.exists()


def test_cli_single_case(tmp_path):
    import subprocess, sys
    from bolt_analysis_studio.validation.case_registry import all_records
    rec = min((r for r in all_records() if r.case_class == "full_curve"),
              key=lambda r: r.validation_case.n_cycles)
    out = subprocess.run(
        [sys.executable, "-m", "bolt_analysis_studio.validation.report",
         "--case", rec.case_id, "--cap", "300", "--out", str(tmp_path)],
        capture_output=True, text=True, cwd=None)
    assert out.returncode == 0, out.stderr
    assert (tmp_path / "reports" / f"{rec.case_id}.html").exists()
```

(No teste de subprocess, propagar `PYTHONPATH` com `src/` se necessário —
mesma técnica do `tests/conftest.py`; usar `env={**os.environ, "PYTHONPATH": ...}`.)

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** `report.py`:

```python
"""CLI dos reports de validacao (spec §3):
  python -m bolt_analysis_studio.validation.report            # geral do store/seed
  python -m bolt_analysis_studio.validation.report --case ID  # re-simula 1 caso
  python -m bolt_analysis_studio.validation.report --all      # re-simula os 128 (~min)
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from .case_registry import all_records, record
from .report_html import write_reports
from .runner import simulate_case
from .store import ValidationStore


def ensure_reports(out_dir: Optional[Path] = None,
                   regenerate: bool = False) -> Path:
    """Garante o report geral (seed da galeria se o store estiver vazio).
    Nao simula nada — rapido o bastante p/ o menu da GUI."""
    store = ValidationStore()
    if not store.all_ids():
        store.seed_from_gallery()
        store.save()
    return write_reports(out_dir=out_dir)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="bolt_analysis_studio.validation.report")
    ap.add_argument("--all", action="store_true", help="re-simula os 128 casos")
    ap.add_argument("--case", help="re-simula um caso (case_id)")
    ap.add_argument("--from-store", action="store_true",
                    help="so regenera HTML do cache, sem simular")
    ap.add_argument("--cap", type=int, default=None,
                    help="teto de ciclos por caso (smoke)")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)

    store = ValidationStore()
    if not store.all_ids():
        n = store.seed_from_gallery()
        print(f"seed da galeria: {n} casos")
    todo = []
    if args.case:
        rec = record(args.case)
        if rec is None:
            print(f"caso desconhecido: {args.case}")
            return 2
        todo = [rec]
    elif args.all:
        todo = all_records()
    for i, rec in enumerate(todo, 1):
        res = simulate_case(rec, n_cap=args.cap)
        store.put(res)
        tag = f"MAE={res.mae:.4f}" if res.mae is not None else (
            "ok" if res.ok else f"ERRO: {res.error}")
        print(f"[{i}/{len(todo)}] {rec.case_id:45s} {tag}")
    if todo:
        store.save()
    master = write_reports(out_dir=args.out)
    print(f"reports em {master.parent} (master: {master.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

`main_window.py` — dentro de `_open_validation_gallery`, ANTES do loop de
candidates, tentar gerar via pacote (mantendo o fallback atual intacto):

```python
        # Gera/atualiza via pacote validation (Plano A) — rapido (store/seed).
        try:
            from bolt_analysis_studio.validation.report import ensure_reports
            target = ensure_reports()
            webbrowser.open(target.as_uri())
            self._on_status_message(f"Validation Gallery → {target.name}")
            return
        except Exception:
            pass   # fallback: abrir um HTML existente (comportamento antigo)
```

- [ ] **Step 4: `ast.parse` nos 2 arquivos + rodar** — `python -m pytest tests/test_validation_report_html.py -q` → **6 passed**.
- [ ] **Step 5: Commit** — `git commit -m "feat(validation): CLI de reports + menu V1 gera via pacote (Plano A)"`

---

## Task 7: Geração real dos 128 + verificação final + STATUS

- [ ] **Step 1: Rodar o batch completo** — `python -m bolt_analysis_studio.validation.report --all` (SEM `--cap`; ~5-30 min; se algum caso individual passar de ~10 min, re-rodar só ele com `--cap 200000` e registrar no STATUS). Conferir o stdout: quantos ok/erro por família; erros esperados só na família `other`.
- [ ] **Step 2: Abrir 3 reports no navegador** (se display disponível) ou inspecionar o HTML de: 1 transversal rico (decomposição presente), 1 axial, 1 final_ratio (degradação). Verificar bytes UTF-8 do título com `python -c "b=open(PATH,'rb').read(); assert 'Condições'.encode() in b"`.
- [ ] **Step 3: Suítes** — `python -m pytest tests/test_validation_inputs.py tests/test_validation_registry.py tests/test_validation_runner.py tests/test_validation_store.py tests/test_validation_report_html.py -q` → verde; regressão: `python -m pytest tests/test_calibration_server.py tests/test_parameter_registry.py tests/test_library_common.py -q` → **38 passed**.
- [ ] **Step 4: STATUS** — escrever `docs/superpowers/plans/2026-07-10-validation-package-core-STATUS.md`: entregue (tabela módulo/testes), números reais do batch (ok/erro por família, MAE global vs galeria), decisões, limitações honestas (runner v1 não cobre família `other`; MAEs do runner ≠ MAEs da campanha onde a campanha usou configs experimentais não-adotadas — o report é o CANÔNICO adotado), handoff Plano B (GUI V2). Atualizar `CLAUDE.md` (§ Reference docs: linha do pacote validation + CLI).
- [ ] **Step 5: Commit** — `git add -A docs/ CLAUDE.md Models/CALIBRATION_AND_VALIDATION/validation_store.json && git commit -m "docs(validation): batch 128 + STATUS Plano A + handoff Plano B"`

---

## Self-Review

**Spec coverage:** §3 pacote (Tasks 1-5) ✔; CLI (Task 6) ✔; menu V1 (Task 6) ✔; decomposição por mecanismo (Task 3 runner + Task 5 §4) ✔; degradação honesta (registry caveats + runner error + report banners) ✔; seed da galeria (Task 4) ✔; report geral com pisos (Task 5.5) ✔; batch real (Task 7) ✔. GUI V2 = Plano B (fora deste plano, § 7 da spec). ✔
**Placeholder scan:** blocos "copiados VERBATIM" apontam arquivo+linhas exatas da fonte de port (paridade testada) — não é TBD, é instrução de cópia. Sem TODO/TBD. ✔
**Type consistency:** `CaseRecord`/`CaseResult` campos usados nas Tasks 3-6 conferem com as definições (Tasks 2-3); `write_reports(out_dir, results)` (Task 5) chamado nas Tasks 6-7; `ensure_reports(out_dir, regenerate)` definido e usado; `simulate_case(rec, n_cap, now)` consistente. ✔
**Riscos anotados:** (a) contagens exatas do registry podem divergir (Step 4 da Task 2 manda ajustar ao real); (b) fechamento decomposição vs ratio é garantia do engine — falha = bug real, não afrouxar; (c) MAEs do runner podem diferir da galeria (configs de campanha ≠ adotadas) — documentar no STATUS, é o comportamento canônico desejado; (d) runtime do batch — cap manual documentado.
