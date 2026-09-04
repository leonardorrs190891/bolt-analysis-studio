# Library Confrontation Phase 1 — Plan 1 of 3: Foundation + Axial Track (sub-campaign B) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Zero-refit prediction of the 13 axial force-mode literature curves (Liu2017 + Li2022ti) with frozen Stage-A constants and `emb_depth` taken from the VDI 2230 handbook table — the first out-of-sample test of the shared-physics model, plus the shared `library_common.py` foundation Plans 2–3 reuse.

**Architecture:** Spec `docs/superpowers/specs/2026-07-03-library-confrontation-phase1-design.md` §1.6 (B1 predict-first / B2 fit-only-if-fails) + §1.3a (emb_depth as per-joint handbook input, anti-knob discipline). New helper module `New_Theory/library_common.py` (ISO thread table, VDI f_Z table, frozen-constants loader, curve loader, provenance records) consumed by `New_Theory/calibrate_axial.py`. Sub-campaigns C and A get their own plans afterward.

**Tech Stack:** Python 3, numpy, scipy, matplotlib (Agg), pytest. No engine changes, no new dependencies.

## Global Constraints

- Work on feature branch `library-confrontation-b` from `main`; merge-commit back when finished.
- utf-8 I/O everywhere; `ast.parse` syntax check after every `.py` edit; commits Portuguese-without-accents + trailer `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- **Zero-refit discipline (spec §1.1, §1.3a):** Stage-A constants come from the `shared` block of `New_Theory/joint_calibrations.json` and are NEVER adjusted; `emb_depth` comes from the VDI table by finish class (provenance `handbook`); μ/grip gaps filled by `MSD_BLOCK_COVERAGE.md` rules with provenance `assumed`; NO parameter is tuned against any library curve in B1.
- **Alignment rule (pre-registered):** both data and simulation are normalized at the FIRST data point's cycle (data curves are normalized post-settling; li2022ti is normalized at N=200 — same rule covers it). Uniform for all curves; never per-curve tuned.
- **Trims (spec §1.6):** `li2022ti_axial_10Hz_full` trimmed to cycles ≤ 3.3e5 (fatigue tail is out-of-model). Liu2017 curves have no collapse stage (documented) — no trim.
- **B2 gate:** run B2 (parsimonious fit, budget ≤2 constants, train on the 2 central curves only) ONLY if B1's median MAE_pred > 0.05 OR B1 loses to the 1-parameter exponential baseline on > half the curves. Anything B2 frees is a candidate form-falsification, documented — never silently absorbed.
- All results recorded AS IS (success or falsification — both are findings).
- Foreign/untracked working-tree files: stage ONLY the files named in each task (never `git add -A`; never touch `New_Theory/Materiais_Metalicos_EPL_Gb.docx`, `crash_log.txt`).
- Timing facts: `step_cycle` ≈ 0.11 ms → 10⁶-cycle curve ≈ 1.5–2 min; base B1 (13 curves) ≈ 20 min. **Sensitivity bands run only on the pre-registered representative subset** `SENS_SUBSET = {"Liu2017 P0=15", "Liu2017 P0=21", "Liu2017 AF=12.5", "Li2022ti 10Hz"}` (extremes of both sweeps + one Li2022) — 4 extra sims each → full B1 ≈ 45–60 min via background Bash with tee'd log. Other curves get `MAE_band: null` in the JSON (declared, not silent).

## File Structure

| File | Responsibility |
|---|---|
| `New_Theory/library_common.py` (create) | ISO thread table, VDI 2230 f_Z table + `emb_depth_vdi()`, `frozen_constants()`, `load_full_curve()`, `Provenance` |
| `tests/test_library_common.py` (create) | table lookups, frozen-constants loading, curve reading, provenance |
| `New_Theory/calibrate_axial.py` (create) | B1 zero-refit run (13 curves, gradients, conservation, sensitivity, report) + B2 behind `--fit` |
| `New_Theory/axial_results.json`, `axial_track.png`, `axial_report.md` (generated) | committed artifacts of the science run |
| `New_Theory/MODEL_LEGITIMACY.md`, `CLAUDE.md` (modify, Task 3) | §4.6 axial-track results + changelog; commands |

---

### Task 1: `library_common.py` — shared foundation

**Files:**
- Create: `New_Theory/library_common.py`
- Test: `tests/test_library_common.py` (create)

**Interfaces:**
- Consumes: `New_Theory/joint_calibrations.json` `shared` block (committed, schema 2); `bolt_analysis_studio.numerical.dynamic_stiffness_analyzer.JointGeometry`.
- Produces (Tasks 2 + Plans 2–3 rely on):
  - `ISO_THREADS: Dict[str, dict]` — key = bolt_size string as used by ValidationCases (e.g. `"M12x1.75"`), values `{d_mm, p_mm, A_s_mm2, d2_mm}`
  - `emb_depth_vdi(rz_class: str, n_inner_interfaces: int, loading: str = "axial") -> tuple[float, dict]` — returns (f_Z total in meters, breakdown dict)
  - `frozen_constants(json_path=...) -> tuple[dict, dict]` — (JointMaterial kwargs from the Stage-A `shared` block priors+fitted constants EXCLUDING `emb_depth`, provenance dict)
  - `load_full_curve(csv_rel_path: str) -> tuple[np.ndarray, np.ndarray]` — full-resolution (cycles, ratio) from a repo-relative CSV
  - `geometry_for(bolt_size: str, grip_mm: float, r_bearing_mm=None, A_contact_mm2=100.0, E=None) -> JointGeometry`
  - `Provenance` dataclass: `value, source ('paper'|'handbook'|'iso'|'assumed'|'stage_a')`, `note`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_library_common.py`:

```python
"""Fundacao da Fase 1 (confronto com a biblioteca) — spec 2026-07-03 §1.3/§2."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "New_Theory"))

from library_common import (  # noqa: E402
    ISO_THREADS, Provenance, emb_depth_vdi, frozen_constants, geometry_for,
    load_full_curve,
)


def test_iso_threads_table_has_the_library_sizes():
    for size, As in [("M6x1.0", 20.1), ("M8x1.25", 36.6), ("M10x1.5", 58.0),
                     ("M12x1.75", 84.3), ("M12x1.5", 88.1), ("M16x2.0", 157.0),
                     ("M30x3.5", 561.0), ("M42x4.5", 1121.0)]:
        assert ISO_THREADS[size]["A_s_mm2"] == pytest.approx(As, rel=0.01), size
    # d2 via ISO 724: d - 0.6495*P
    assert ISO_THREADS["M12x1.75"]["d2_mm"] == pytest.approx(12 - 0.6495 * 1.75,
                                                             abs=0.01)


def test_emb_depth_vdi_axial_fine_ground_two_plates():
    # Rz<10, 1 interface interna, axial: rosca 3 + 2 apoios 2.5 + 1 interface 1.5
    fz, br = emb_depth_vdi("Rz<10", n_inner_interfaces=1, loading="axial")
    assert fz == pytest.approx(9.5e-6, rel=1e-6)
    assert br["thread_um"] == 3.0 and br["bearing_um"] == 2.5
    # classe mais grossa aumenta monotonicamente
    fz_mid, _ = emb_depth_vdi("Rz10-40", 1)
    fz_hi, _ = emb_depth_vdi("Rz40-160", 1)
    assert fz < fz_mid < fz_hi


def test_frozen_constants_read_stage_a_shared_block():
    kw, prov = frozen_constants()
    assert kw["C_creep"] == pytest.approx(1.1646709063295502e-11)
    assert "emb_depth" not in kw          # emb_depth e input por junta (§1.3a)
    assert all(k not in kw for k in ("k_emb_scale", "Phi_tr_correction"))
    assert prov["C_creep"].source == "stage_a"
    assert prov["K_archard"].source == "stage_a"   # prior nao-fitado tambem congelado


def test_load_full_curve_reads_digitized_csv():
    cyc, ratio = load_full_curve(
        "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/"
        "liu2017_axial_F0_18kN.csv")
    assert len(cyc) >= 10 and cyc[0] < cyc[-1]
    assert ratio[-1] == pytest.approx(0.885, abs=0.01)   # nota de aparato


def test_geometry_for_builds_joint_geometry():
    g = geometry_for("M12x1.75", grip_mm=30.0)
    assert g.A_s == pytest.approx(84.3e-6, rel=0.01)
    assert g.L_eff == pytest.approx(0.030)
    assert g.d_2 == pytest.approx(10.863e-3, abs=2e-5)
    assert g.pitch == pytest.approx(1.75e-3)


def test_provenance_record():
    p = Provenance(0.15, "assumed", "mu default MSD_BLOCK_COVERAGE regra 3")
    assert p.source == "assumed"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_library_common.py -q`
Expected: FAIL at collection with `ModuleNotFoundError: No module named 'library_common'`.

- [ ] **Step 3: Implement the module**

Create `New_Theory/library_common.py`:

```python
"""Fundacao comum da Fase 1 do confronto com a biblioteca (spec 2026-07-03).

Regras de proveniencia (spec §1.3/§1.3a): todo input carrega Provenance
('paper' = nota de aparato; 'handbook' = tabela VDI 2230/DIN; 'iso' = tabela
de rosca; 'assumed' = regra do MSD_BLOCK_COVERAGE, sujeito a banda de
sensibilidade; 'stage_a' = constante congelada do bloco shared).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys  # noqa: E402
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    JointGeometry,
)

SHARED_JSON = ROOT / "New_Theory" / "joint_calibrations.json"


@dataclass(frozen=True)
class Provenance:
    value: float
    source: str      # 'paper' | 'handbook' | 'iso' | 'assumed' | 'stage_a'
    note: str = ""


# --- ISO 898-1 / ISO 724: roscas usadas pela biblioteca ----------------------
def _d2(d: float, p: float) -> float:
    return d - 0.6495 * p


ISO_THREADS: Dict[str, dict] = {
    "M6x1.0":   dict(d_mm=6.0,  p_mm=1.0,  A_s_mm2=20.1,  d2_mm=_d2(6, 1.0)),
    "M8x1.25":  dict(d_mm=8.0,  p_mm=1.25, A_s_mm2=36.6,  d2_mm=_d2(8, 1.25)),
    "M10x1.5":  dict(d_mm=10.0, p_mm=1.5,  A_s_mm2=58.0,  d2_mm=_d2(10, 1.5)),
    "M12x1.75": dict(d_mm=12.0, p_mm=1.75, A_s_mm2=84.3,  d2_mm=_d2(12, 1.75)),
    "M12x1.5":  dict(d_mm=12.0, p_mm=1.5,  A_s_mm2=88.1,  d2_mm=_d2(12, 1.5)),
    "M16x2.0":  dict(d_mm=16.0, p_mm=2.0,  A_s_mm2=157.0, d2_mm=_d2(16, 2.0)),
    "M30x3.5":  dict(d_mm=30.0, p_mm=3.5,  A_s_mm2=561.0, d2_mm=_d2(30, 3.5)),
    "M42x4.5":  dict(d_mm=42.0, p_mm=4.5,  A_s_mm2=1121.0, d2_mm=_d2(42, 4.5)),
}

# --- VDI 2230-1 Tabela 5 (valores-guia de assentamento f_Z, um, POR SUPERFICIE;
#     coluna de carregamento axial; carregamento cisalhante tem interfaces
#     maiores — aproximacao documentada: usar coluna axial + banda de classe
#     adjacente como sensibilidade, spec §1.3a). ---------------------------------
_VDI_FZ_UM = {
    #  classe        rosca  apoio(cabeca/porca)  interface interna
    "Rz<10":     dict(thread=3.0, bearing=2.5, interface=1.5),
    "Rz10-40":   dict(thread=3.0, bearing=3.0, interface=2.0),
    "Rz40-160":  dict(thread=3.0, bearing=4.0, interface=3.0),
}
_VDI_ORDER = ["Rz<10", "Rz10-40", "Rz40-160"]


def emb_depth_vdi(rz_class: str, n_inner_interfaces: int,
                  loading: str = "axial") -> Tuple[float, dict]:
    """f_Z total da pilha [m] = rosca + 2 apoios + n interfaces internas.
    Proveniencia 'handbook'. `loading` registrado no breakdown (coluna axial
    usada para ambos — aproximacao pre-registrada)."""
    row = _VDI_FZ_UM[rz_class]
    total_um = (row["thread"] + 2.0 * row["bearing"]
                + n_inner_interfaces * row["interface"])
    return total_um * 1e-6, dict(rz_class=rz_class, loading=loading,
                                 thread_um=row["thread"],
                                 bearing_um=row["bearing"],
                                 interface_um=row["interface"],
                                 n_inner_interfaces=n_inner_interfaces,
                                 total_um=total_um)


def vdi_adjacent_classes(rz_class: str) -> Tuple[str, str]:
    """Classes vizinhas para a banda de sensibilidade (§1.3a)."""
    i = _VDI_ORDER.index(rz_class)
    lo = _VDI_ORDER[max(i - 1, 0)]
    hi = _VDI_ORDER[min(i + 1, len(_VDI_ORDER) - 1)]
    return lo, hi


def frozen_constants(json_path: Path = SHARED_JSON) -> Tuple[dict, Dict[str, Provenance]]:
    """Constantes fisicas CONGELADAS do Estagio A: priors do bloco shared com
    os valores fitados por cima; emb_depth EXCLUIDO (input por junta, §1.3a).
    Tuners nao entram (defaults 1.0 do engine)."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    consts = dict(data["shared"]["constants"])
    consts.pop("emb_depth", None)
    # c_D/k_dmg_wear so agem com damage_active — inofensivos, mas removemos
    # por clareza: nenhuma condicao da biblioteca declara dano inicial.
    consts.pop("c_D", None)
    consts.pop("k_dmg_wear", None)
    prov = {k: Provenance(v, "stage_a", "bloco shared (joint_calibrations.json)")
            for k, v in consts.items()}
    return consts, prov


def load_full_curve(csv_rel_path: str) -> Tuple[np.ndarray, np.ndarray]:
    d = np.genfromtxt(ROOT / csv_rel_path, delimiter=",", skip_header=1,
                      encoding="utf-8")
    return d[:, 0], d[:, 1]


def geometry_for(bolt_size: str, grip_mm: float, r_bearing_mm: float = None,
                 A_contact_mm2: float = 100.0, E: float = None) -> JointGeometry:
    """JointGeometry a partir da tabela ISO + grip. r_bearing default = 0.75*d
    (raio efetivo do apoio da cabeca, mesma proporcao do M16 do Estagio A:
    12mm/16mm)."""
    t = ISO_THREADS[bolt_size]
    kw = dict(A_s=t["A_s_mm2"] * 1e-6,
              L_eff=grip_mm * 1e-3,
              d_2=t["d2_mm"] * 1e-3,
              pitch=t["p_mm"] * 1e-3,
              r_bearing=(r_bearing_mm if r_bearing_mm is not None
                         else 0.75 * t["d_mm"]) * 1e-3,
              A_contact=A_contact_mm2 * 1e-6)
    if E is not None:
        kw["E"] = E
    return JointGeometry(**kw)
```

- [ ] **Step 4: Syntax check + run tests**

Run: `python -c "import ast; ast.parse(open('New_Theory/library_common.py', encoding='utf-8').read()); print('OK')"`
Run: `python -m pytest tests/test_library_common.py -v`
Expected: 6 PASS. (`test_frozen_constants...` asserts `K_archard` has provenance `stage_a` — `shared["constants"]` contains ALL priors with fitted values overlaid, so K_archard is present at its prior 1e-4; if the key is somehow absent, that is a data-shape finding to report, not to patch around.)

- [ ] **Step 5: Commit**

```bash
git add New_Theory/library_common.py tests/test_library_common.py
git commit -m "calib: fundacao da Fase 1 — tabelas ISO/VDI, constantes congeladas, proveniencia

ISO 898/724 (8 roscas da biblioteca), VDI 2230 Tabela 5 (f_Z por classe
de rugosidade, coluna axial + banda de classe adjacente), frozen_constants
do bloco shared (emb_depth excluido — input por junta, spec §1.3a).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: `calibrate_axial.py` — B1 zero-refit run (+B2 gate)

**Files:**
- Create: `New_Theory/calibrate_axial.py`
- Generated artifacts (committed): `New_Theory/axial_results.json`, `New_Theory/axial_track.png`, `New_Theory/axial_report.md`

**Interfaces:**
- Consumes: everything from Task 1; `DynamicStiffnessAnalyzer`, `JointMaterial`; the 13 digitized CSVs.
- Produces: `run_condition(cond: dict, consts: dict, emb_m: float, frac_sensitivity: bool) -> dict` internals are script-local; the JSON schema below is what Plan-3/Task-3 docs consume.

**The 13 pre-registered conditions** (from `apparatus_notes/liu2017_triboint_axial.md` trial matrix and `li2022_triboint_axial_freq.md`; A_F values are NOT in the ValidationCase fields — they live here):

- [ ] **Step 1: Write the script**

Create `New_Theory/calibrate_axial.py`:

```python
"""Sub-campanha B — trilho AXIAL, predicao-primeiro (spec 2026-07-03 §1.6).

B1 (default): predicao zero-refit das 13 curvas axiais com constantes do
Estagio A congeladas + emb_depth de tabela VDI (§1.3a). Nenhum parametro e
ajustado a nenhuma curva. B2 (--fit): SO se o gate do B1 falhar (mediana
MAE>0.05 ou perder do baseline exponencial em >50% das curvas).

Run:  python New_Theory/calibrate_axial.py [--quick] [--fit]
  --quick: n_cycles cap 2e4 (smoke; nao grava artefatos cientificos)
Runtime B1 completo: ~25-40 min (13 curvas ate 1e6 ciclos + sensibilidade).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial,
)
from library_common import (  # noqa: E402
    Provenance, emb_depth_vdi, frozen_constants, geometry_for,
    load_full_curve, vdi_adjacent_classes,
)

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"

# --- Condicoes pre-registradas (notas de aparato; NAO editar apos rodar) -----
# Liu2017: M12x1.75 10.9 retificado (classe Rz<10 assumida p/ rosca laminada e
# superficies usinadas finas — sensibilidade = classe adjacente), 30 Hz, 1e6.
# Grip nao reportado -> 2.5*d = 30 mm, 'assumed', banda 24-36 mm (2d-3d).
# Li2022ti: M10, A_F=10 kN, 10/15/20 Hz; normalizado em N=200; grip 25 mm
# 'assumed'. Trim do full-run em 3.3e5 (fadiga).
LIU17 = dict(bolt="M12x1.75", grip_mm=30.0, rz="Rz<10", n_if=1, freq=30.0,
             n_cycles=1_000_000, mu=0.15,
             prov=dict(grip=Provenance(30.0, "assumed", "2.5d; banda 24-36"),
                       rz=Provenance(0, "assumed", "usinado fino; banda classe adjacente"),
                       mu=Provenance(0.15, "assumed", "MSD_BLOCK_COVERAGE regra 3")))
LI22 = dict(bolt="M10x1.5", grip_mm=25.0, rz="Rz<10", n_if=1,
            n_cycles=330_000, mu=0.15,
            prov=dict(grip=Provenance(25.0, "assumed", "2.5d; banda 20-30"),
                      rz=Provenance(0, "assumed", "banda classe adjacente"),
                      mu=Provenance(0.15, "assumed", "MSD_BLOCK_COVERAGE regra 3")))

CONDITIONS = [
    # nome, csv, F0 [N], F_amp [N], base
    ("Liu2017 P0=15",   f"{DIG}/liu2017_axial_F0_15kN.csv",   15e3, 10e3, LIU17),
    ("Liu2017 P0=16.5", f"{DIG}/liu2017_axial_F0_16p5kN.csv", 16.5e3, 10e3, LIU17),
    ("Liu2017 P0=18",   f"{DIG}/liu2017_axial_F0_18kN.csv",   18e3, 10e3, LIU17),
    ("Liu2017 P0=19.5", f"{DIG}/liu2017_axial_F0_19p5kN.csv", 19.5e3, 10e3, LIU17),
    ("Liu2017 P0=21",   f"{DIG}/liu2017_axial_F0_21kN.csv",   21e3, 10e3, LIU17),
    ("Liu2017 AF=7.5",  f"{DIG}/liu2017_axial_AF_7p5kN.csv",  18e3, 7.5e3, LIU17),
    ("Liu2017 AF=8.75", f"{DIG}/liu2017_axial_AF_8p75kN.csv", 18e3, 8.75e3, LIU17),
    ("Liu2017 AF=11.25", f"{DIG}/liu2017_axial_AF_11p25kN.csv", 18e3, 11.25e3, LIU17),
    ("Liu2017 AF=12.5", f"{DIG}/liu2017_axial_AF_12p5kN.csv", 18e3, 12.5e3, LIU17),
    ("Li2022ti 10Hz",   f"{DIG}/li2022ti_axialmin_10Hz.csv",  10e3, 10e3, dict(LI22, freq=10.0)),
    ("Li2022ti 15Hz",   f"{DIG}/li2022ti_axialmin_15Hz.csv",  10e3, 10e3, dict(LI22, freq=15.0)),
    ("Li2022ti 20Hz",   f"{DIG}/li2022ti_axialmin_20Hz.csv",  10e3, 10e3, dict(LI22, freq=20.0)),
    ("Li2022ti 10Hz full", f"{DIG}/li2022ti_axial_10Hz_full.csv", 10e3, 10e3, dict(LI22, freq=10.0)),
]


def simulate(name, F0, F_amp, base, consts, emb_m, n_cycles):
    geom = geometry_for(base["bolt"], base["grip_mm"])
    mat = JointMaterial(emb_depth=emb_m, **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    ratio = np.empty(n_cycles + 1)
    ratio[0] = 1.0
    for n in range(1, n_cycles + 1):
        ana.step_cycle(F_amp, 0.0, base["freq"])          # AXIAL, force-mode
        ratio[n] = max(ana.state.F_0, 0.0) / F0
    residual = float(ana.energy.conservation_residual)
    return np.arange(n_cycles + 1), ratio, residual


# Sensibilidade so no subconjunto representativo pre-registrado (runtime):
# extremos dos dois sweeps + uma curva Li2022. Demais: MAE_band=None declarado.
SENS_SUBSET = {"Liu2017 P0=15", "Liu2017 P0=21", "Liu2017 AF=12.5",
               "Li2022ti 10Hz"}


def predict_one(entry, consts, cap=None):
    name, csv, F0, F_amp, base = entry
    cyc_d, r_d = load_full_curve(csv)
    n_max = int(min(base["n_cycles"], cyc_d[-1]))
    if cap:
        n_max = min(n_max, cap)
    keep = cyc_d <= n_max
    cyc_d, r_d = cyc_d[keep], r_d[keep]
    emb_m, br = emb_depth_vdi(base["rz"], base["n_if"])
    sim_N, sim_r, resid = simulate(name, F0, F_amp, base, consts, emb_m, n_max)
    # alinhamento pre-registrado: normalizar AMBOS no primeiro ponto do dado
    n0 = cyc_d[0]
    r_d_al = r_d / r_d[0]
    sim_at_n0 = np.interp(n0, sim_N, sim_r)
    sim_al = sim_r / max(sim_at_n0, 1e-9)
    pred = np.interp(cyc_d, sim_N, sim_al)
    mae = float(np.mean(np.abs(pred - r_d_al)))
    # baseline (ii): decaimento exponencial 1-parametro fitado A CADA curva
    lam = _fit_exp(cyc_d - n0, r_d_al)
    mae_exp = float(np.mean(np.abs(np.exp(-lam * (cyc_d - n0)) - r_d_al)))
    # sensibilidade (§1.5): grip 2d/3d x classe Rz adjacente -> banda de MAE,
    # SO no subconjunto representativo pre-registrado (runtime).
    band = None
    if name in SENS_SUBSET:
        maes = []
        for gmm in (2.0, 3.0):
            for rzc in set(vdi_adjacent_classes(base["rz"])):
                e2, _ = emb_depth_vdi(rzc, base["n_if"])
                b2 = dict(base, grip_mm=gmm * float(base["bolt"].split("x")[0][1:]))
                _, s2, _ = simulate(name, F0, F_amp, b2, consts, e2, n_max)
                s2_al = s2 / max(np.interp(n0, np.arange(len(s2)), s2), 1e-9)
                maes.append(float(np.mean(np.abs(
                    np.interp(cyc_d, np.arange(len(s2)), s2_al) - r_d_al))))
        band = [min(maes), max(maes)]
    return dict(name=name, csv=csv, F0_N=F0, F_amp_N=F_amp,
                emb_depth_um=br["total_um"], rz_class=base["rz"],
                n_cycles=n_max, MAE=mae, MAE_exp_baseline=mae_exp,
                MAE_band=band,
                final_data=float(r_d_al[-1]), final_pred=float(pred[-1]),
                conservation_residual=resid,
                curve=dict(cycles=cyc_d.tolist(), data=r_d_al.tolist(),
                           pred=pred.tolist()))


def _fit_exp(n, r):
    """lambda de r=exp(-lam n) por minimos quadrados em log (r>0)."""
    m = r > 0.05
    if m.sum() < 2 or n[m].max() <= 0:
        return 0.0
    return max(float(-np.polyfit(n[m], np.log(r[m]), 1)[0]), 0.0)


def main():
    quick = "--quick" in sys.argv
    cap = 20_000 if quick else None
    consts, prov = frozen_constants()
    print(f"Constantes congeladas (Estagio A): {consts}")
    results = [predict_one(e, consts, cap) for e in CONDITIONS]

    for r in results:
        band = ("banda " + "-".join(f"{b:.4f}" for b in r["MAE_band"])
                if r["MAE_band"] else "banda —")
        print(f"{r['name']:22s} MAE={r['MAE']:.4f} "
              f"(exp-baseline {r['MAE_exp_baseline']:.4f}, {band}) "
              f"fim dado={r['final_data']:.3f} pred={r['final_pred']:.3f} "
              f"resid={r['conservation_residual']:.2e}")
    maes = [r["MAE"] for r in results]
    beats = sum(r["MAE"] <= r["MAE_exp_baseline"] for r in results)
    med = float(np.median(maes))
    gate_fail = med > 0.05 or beats < len(results) / 2
    print(f"\nMediana MAE={med:.4f}; vence baseline exp em {beats}/{len(results)}")
    print("GATE B1:", "FALHOU -> rodar --fit (B2)" if gate_fail else "PASSOU")

    # gradientes dado-vs-modelo (P0-sweep e AF-sweep do Liu2017)
    def _grad(sel, xkey):
        xs = [r[xkey] for r in results if r["name"].startswith(sel)]
        yd = [r["final_data"] for r in results if r["name"].startswith(sel)]
        yp = [r["final_pred"] for r in results if r["name"].startswith(sel)]
        gd = np.polyfit(xs, yd, 1)[0] if len(xs) > 2 else float("nan")
        gp = np.polyfit(xs, yp, 1)[0] if len(xs) > 2 else float("nan")
        return float(gd), float(gp)
    g_P0 = _grad("Liu2017 P0", "F0_N")
    g_AF = _grad("Liu2017 AF", "F_amp_N")
    print(f"grad d(fim)/dP0: dado {g_P0[0]:.3e} /N, modelo {g_P0[1]:.3e} /N")
    print(f"grad d(fim)/dAF: dado {g_AF[0]:.3e} /N, modelo {g_AF[1]:.3e} /N")

    # plot 4x4
    fig, axes = plt.subplots(4, 4, figsize=(18, 14))
    for ax, r in zip(axes.flat, results):
        ax.semilogx(r["curve"]["cycles"], r["curve"]["data"], "o-", ms=3,
                    label="dado")
        ax.semilogx(r["curve"]["cycles"], r["curve"]["pred"], "k-",
                    label=f"pred (MAE={r['MAE']:.3f})")
        ax.set_title(r["name"], fontsize=9)
        ax.set_ylim(0.5, 1.05); ax.grid(alpha=0.3); ax.legend(fontsize=7)
    for ax in axes.flat[len(results):]:
        ax.axis("off")
    plt.tight_layout()
    fig.savefig(ROOT / "New_Theory" / "axial_track.png", dpi=110)

    if quick:
        print("--quick: nao gravando artefatos cientificos.")
        return
    out = dict(campaign="B1 zero-refit axial (spec 2026-07-03 §1.6)",
               frozen_constants=consts,
               provenance={k: vars(v) for k, v in prov.items()},
               gate=dict(median_MAE=med, beats_exp_baseline=f"{beats}/{len(results)}",
                         failed=bool(gate_fail)),
               gradients=dict(dfinal_dP0=dict(data=g_P0[0], model=g_P0[1]),
                              dfinal_dAF=dict(data=g_AF[0], model=g_AF[1])),
               results=[{k: v for k, v in r.items() if k != "curve"}
                        for r in results])
    (ROOT / "New_Theory" / "axial_results.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# Trilho axial — B1 zero-refit (spec 2026-07-03 §1.6)", "",
             f"Mediana MAE={med:.4f}; vence baseline exp em {beats}/{len(results)}; "
             f"gate {'FALHOU' if gate_fail else 'PASSOU'}.", "",
             "| Curva | MAE | exp-baseline | banda sens. | fim dado | fim pred |",
             "|---|---:|---:|---|---:|---:|"]
    for r in results:
        band = ("–".join(f"{b:.3f}" for b in r["MAE_band"])
                if r["MAE_band"] else "—")
        lines.append(f"| {r['name']} | {r['MAE']:.4f} | {r['MAE_exp_baseline']:.4f}"
                     f" | {band} | {r['final_data']:.3f} | {r['final_pred']:.3f} |")
    (ROOT / "New_Theory" / "axial_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("Artefatos: axial_results.json, axial_track.png, axial_report.md")


if __name__ == "__main__":
    main()
```

Note for the implementer: the plan intentionally does NOT include B2 code. If (and only if) the B1 gate FAILS, STOP and report the gate numbers to the controller — B2's design (train-2-central/predict-11) gets its own reviewed step; do not improvise it.

- [ ] **Step 2: Syntax check + quick smoke**

Run: `python -c "import ast; ast.parse(open('New_Theory/calibrate_axial.py', encoding='utf-8').read()); print('OK')"`
Run (background, tee to `.superpowers/sdd/axial-quick.log`, ~2–4 min): `python New_Theory/calibrate_axial.py --quick`
Sanity: 13 lines printed, all MAE finite, conservation residuals small (|resid| < 1% of typical energies — expect ≈0 in axial: wear/loosening dormant), PNG written, no JSON in quick mode.

- [ ] **Step 3: Full B1 run (background, tee to `.superpowers/sdd/axial-full.log`, ~25–40 min)**

Run: `python New_Theory/calibrate_axial.py 2>&1 | tee .superpowers/sdd/axial-full.log`
Then verify: `python -c "import json; d=json.load(open('New_Theory/axial_results.json', encoding='utf-8')); print(d['gate']); print(len(d['results']), 'curvas')"`
Expected: gate dict + `13 curvas`. Record the gate verdict AS IS. If `failed: true` → report BLOCKED-style to controller with the numbers (B2 decision is the controller's).

- [ ] **Step 4: Commit**

```bash
git add New_Theory/calibrate_axial.py New_Theory/axial_results.json New_Theory/axial_report.md
git add -f New_Theory/axial_track.png
git commit -m "calib: trilho axial B1 — predicao zero-refit das 13 curvas (Liu2017 + Li2022ti)

Constantes do Estagio A congeladas; emb_depth de tabela VDI 2230 com
proveniencia handbook; alinhamento no primeiro ponto do dado; gradientes
d(fim)/dP0 e d(fim)/dAF dado-vs-modelo; residual de conservacao monitorado;
baselines e bandas de sensibilidade pre-registrados. Resultado gravado AS IS.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: docs — axial-track verdict

**Files:**
- Modify: `New_Theory/MODEL_LEGITIMACY.md` (new §4.6 + changelog row)
- Modify: `CLAUDE.md` (commands block + one gotcha)

**Interfaces:**
- Consumes: `New_Theory/axial_results.json` + `axial_report.md` (Task 2).

- [ ] **Step 1: MODEL_LEGITIMACY §4.6**

Insert after §4.5, transcribing REAL numbers from `axial_results.json` (every `<...>` replaced from the artifact — transcription, not authoring):

```markdown
### 4.6 Trilho axial — predição zero-refit (Fase 1B, spec 2026-07-03)

13 curvas axiais força-controladas (Liu 2017 M12: sweeps de P₀ e A_F; Li 2022
M10: sweep de frequência) preditas com as constantes do Estágio A **congeladas**
e `emb_depth` de **tabela VDI 2230** (input por junta, procedência handbook —
§1.3a do spec). Nenhum parâmetro ajustado a nenhuma curva.

| Métrica | Valor |
|---|---|
| Mediana MAE_pred | <...> |
| Vence o baseline exponencial 1-par/curva | <...>/13 |
| Gradiente ∂(fim)/∂P₀ dado vs modelo | <...> vs <...> |
| Gradiente ∂(fim)/∂A_F dado vs modelo | <...> vs <...> |
| Residual de conservação (típico) | <...> |
| Gate B1 | <PASSOU/FALHOU> |

<2-3 frases honestas: onde acerta, onde erra, o que o erro aponta;
bandas de sensibilidade (grip 2d-3d × classe Rz adjacente) e se alguma
conclusão é `inconclusive` por depender da banda.>
```

- [ ] **Step 2: changelog + CLAUDE.md**

MODEL_LEGITIMACY §9 changelog row:

```markdown
| 2026-07-03 | §4.6 trilho axial (Fase 1B): predição zero-refit das 13 curvas Liu2017/Li2022ti com constantes congeladas + emb_depth de tabela VDI (input por junta). Gate B1: <verdito>. emb_depth deixou de ser constante universal — diagnóstico + doutrina anti-knob no spec 2026-07-03 §1.3a. |
```

CLAUDE.md commands block (after the shared-fit commands):

```bash
# Trilho axial B1 (Fase 1B): predicao zero-refit, ~25-40 min; --quick p/ smoke
python New_Theory/calibrate_axial.py
```

CLAUDE.md gotcha (V2 staged calibration section): `emb_depth` is a PER-JOINT input (VDI 2230 f_Z by roughness class; `library_common.emb_depth_vdi`), not a universal constant — the âncora interna-rig 30 µm default only fits the âncora interna rig; provenance discipline in spec 2026-07-03 §1.3a.

- [ ] **Step 3: Regression + commit**

Run: `python -m pytest tests/test_library_common.py tests/test_shared_calibrator.py tests/test_parameter_registry.py tests/test_embedding_state_based.py -q`
Expected: all PASS (~20 tests).

```bash
git add New_Theory/MODEL_LEGITIMACY.md CLAUDE.md
git commit -m "docs: veredicto do trilho axial B1 (§4.6) + emb_depth como input por junta

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Report the B1 verdict to the user; Plans 2 (âncora de C_creep) and 3 (transferência A) follow as separate plans informed by this result.
