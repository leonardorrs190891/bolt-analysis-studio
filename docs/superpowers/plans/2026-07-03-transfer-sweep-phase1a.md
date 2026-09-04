# Library Confrontation Phase 1 — Plan 3 of 3: Zero-Refit Transverse Transfer Sweep (sub-campaign A) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Predict ~46 transverse disp-mode literature curves (7 papers, M8→M42, 0.07–2.0 mm) with Stage-A constants frozen and all inputs named-with-provenance — the decisive out-of-sample sweep, entirely pre-registered in this plan.

**Architecture:** New script `New_Theory/transfer_validation.py` consuming `library_common` (frozen constants, VDI table, ISO geometry) and `validation_cases.DIGITIZED_CASES` (rule-based selection: source allow-list + CSV-substring exclusions, so no dependence on display names). Both spec baselines computed per curve; sensitivity bands on a pre-registered 8-curve subset; per-source aggregation. Runtime is small (Junker cycle counts ≤ ~2×10⁴ → whole sweep ≈ 2–5 min).

**Tech Stack:** Python 3, numpy, matplotlib (Agg), pytest. No engine changes.

## Global Constraints

- Branch `library-confrontation-a` from `main` (post-`000b8ce`); merge-commit back when finished.
- utf-8 I/O; `ast.parse` after every .py edit; commits PT-without-accents + trailer `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- **Zero-refit (spec §1.1):** constants ONLY from `frozen_constants()` (Stage-A shared block; `emb_depth` excluded there and supplied per-source from the VDI table). NO parameter tuned against any curve. Tuners at engine defaults.
- **Damage OFF for all cases (pre-registered choice):** every selected case is a NEW joint (reused/retightened curves are excluded by rule), and in Stage A damage physics was active only for pre-damaged joints (reusada/reaperto states). So `frozen_constants()` default (no c_D/k_dmg_wear) is the Stage-A-faithful configuration; collapse-shaped curves (Bauer fig8, Liu2025 0.8 mm) are then EXPECTED to under-predict — that is a finding about damage-growth-from-virgin, recorded, not patched. The JSON records this choice + rationale.
- **Selection rule (pre-registered):** cases from `DIGITIZED_CASES` whose `source.name` ∈ {LIU_2025, BAUER_2024, LU_2024, ICMEZ_2025, YANG_2019, ROUSSEAU_2025, KARLSEN_2022} and `transverse_displacement_mm > 0`, EXCLUDING any case whose `reference_csv_path` contains one of: `hdpe` (polymer pair — declared domain limit), `vibralock` (locking device — out-of-model), `varamp` (variable-amplitude protocol — outside the constant-δ harness, NOT outside the model), `fig2_single` (runs to fracture). Every exclusion is recorded in the JSON with its reason — no silent drops (spec §3-A).
- **Named inputs with provenance (spec §1.3):** per-source table in the script (grip/μ/Rz with `paper`/`assumed`/`handbook` provenance; per-case grip overrides by CSV substring where the paper reports them: Bauer l_K=8/12 by bolt size, demir lk13p8/lk19p8, Rousseau steel_t10/12/14 → 25/29/33 mm). `F_amp = 0.4·F₀` per case (assumed — same F_amp/F₀ ratio as the Stage-A âncora interna condition; the F↔δ coupling is a declared Fase-2 item), sensitivity-banded.
- **Alignment (pre-registered):** normalize data AND sim at the first data point's cycle. **Floor-trim (pre-registered, uniform):** drop data points with ratio < 0.10 (fracture-approach zone); per-curve `n_trimmed` recorded.
- **Baselines (spec §1.4, BOTH this time):** (i) no-loss `ratio≡1`; (ii) per-curve 1-parameter exponential `exp(−λN)`, λ≥0 by log-least-squares.
- **Sensitivity (spec §1.5) on the pre-registered 8-curve subset** (CSV stems): liu2025_M16_amp0p25, liu2025_M16_amp0p8, lu2024_M8_fig18_amp0p25, lu2024_M8_fig18_amp2p0, bauer2024_M12_fig8_test1, demir2024_amp0p4_F17p6_lk13p8, karlsen2022_M42_HV_run20p0, rousseau2025_steel_t10. Variants per case: μ ×0.75/×1.25, emb ±Rz class, F_amp ratio 0.2/0.6, grip 2d/3d ONLY where grip is `assumed`. Others get `band: null` (declared).
- Results AS IS; stage only named files; scratch untouched. Expect gate-free reporting (this sub-campaign has no B2 analog — the distribution IS the result).

## File Structure

| File | Responsibility |
|---|---|
| `New_Theory/transfer_validation.py` (create) | selection rule, per-source inputs, sweep, baselines, sensitivity, artifacts |
| `tests/test_transfer_validation.py` (create) | selection-rule tests, provenance completeness, smoke predict |
| `New_Theory/transfer_results.json`, `transfer_grid.png`, `transfer_report.md` (generated) | committed artifacts |
| `New_Theory/MODEL_LEGITIMACY.md`, `CLAUDE.md` (Task 2) | §4.8 + §8 Fase-1 wrap + changelog; command |

---

### Task 1: `transfer_validation.py` + tests + the sweep

**Files:**
- Create: `New_Theory/transfer_validation.py`
- Test: `tests/test_transfer_validation.py` (create)
- Generated (committed): `New_Theory/transfer_results.json`, `New_Theory/transfer_grid.png` (force-add), `New_Theory/transfer_report.md`

**Interfaces:**
- Consumes: `library_common.frozen_constants()/emb_depth_vdi()/vdi_adjacent_classes()/geometry_for()/load_full_curve()`; `bolt_analysis_studio.core.validation_cases.DIGITIZED_CASES` (fields: `source.name`, `bolt_size`, `initial_preload_N`, `transverse_displacement_mm`, `frequency_Hz`, `reference_csv_path`, `name`); `DynamicStiffnessAnalyzer`, `JointMaterial`.
- Produces: importable `select_cases() -> tuple[list, list]` (selected ValidationCases, exclusions `[{csv, reason}]`) and `inputs_for(case) -> dict` (grip_mm/mu/rz/F_amp_N each `{value, prov}`) — tests import both; the JSON schema Task 2 transcribes.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_transfer_validation.py`:

```python
"""Transferencia zero-refit transversal (sub-campanha A) — spec 2026-07-03 §1."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "New_Theory"))

from transfer_validation import inputs_for, predict_case, select_cases  # noqa: E402


def test_selection_rule_counts_and_exclusions():
    selected, excluded = select_cases()
    csvs = [Path(c.reference_csv_path).name for c in selected]
    # regra pre-registrada: nenhum excluido presente
    for token in ("hdpe", "vibralock", "varamp", "fig2_single"):
        assert not any(token in n for n in csvs), token
    # exclusoes registradas com motivo (sem drop silencioso)
    assert len(excluded) >= 10                     # 3 hdpe + 4 vibralock + 2 varamp + 1 fracture
    assert all(e["reason"] for e in excluded)
    # fontes verificadas na construcao dos casos:
    per_source = {}
    for c in selected:
        per_source[c.source.name] = per_source.get(c.source.name, 0) + 1
    assert per_source["LIU_2025"] == 6             # 7 digitalizadas - fig2_single
    assert per_source["BAUER_2024"] == 9
    for src in ("LU_2024", "ICMEZ_2025", "YANG_2019", "ROUSSEAU_2025",
                "KARLSEN_2022"):
        assert per_source.get(src, 0) > 0, src
    assert len(selected) >= 40                     # varredura substancial
    # todos transversais
    assert all(c.transverse_displacement_mm > 0 for c in selected)


def test_inputs_have_provenance_for_every_selected_case():
    selected, _ = select_cases()
    for c in selected:
        inp = inputs_for(c)
        for key in ("grip_mm", "mu", "rz", "F_amp_N"):
            assert inp[key]["prov"] in ("paper", "assumed", "handbook",
                                        "iso"), (c.name, key)
            assert inp[key]["value"] is not None
        # overrides de paper onde documentados:
        stem = Path(c.reference_csv_path).stem
        if "lk13p8" in stem:
            assert inp["grip_mm"]["value"] == pytest.approx(13.8)
            assert inp["grip_mm"]["prov"] == "paper"
        if "rousseau2025_steel_t10" in stem:
            assert inp["grip_mm"]["value"] == pytest.approx(25.0)
            assert inp["grip_mm"]["prov"] == "paper"
        if c.source.name == "BAUER_2024" and c.bolt_size.startswith("M8"):
            assert inp["grip_mm"]["value"] == pytest.approx(8.0)


def test_predict_case_smoke():
    selected, _ = select_cases()
    small = min(selected, key=lambda c: c.n_cycles)   # o caso mais curto
    r = predict_case(small, do_sensitivity=False)
    assert np.isfinite(r["MAE"]) and np.isfinite(r["MAE_exp"])
    assert np.isfinite(r["MAE_noloss"])
    assert 0 < r["final_pred"] <= 1.05
    assert r["n_cycles"] > 0 and r["band"] is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_transfer_validation.py -q`
Expected: FAIL at collection with `ModuleNotFoundError: No module named 'transfer_validation'`.

- [ ] **Step 3: Write the script**

Create `New_Theory/transfer_validation.py`:

```python
"""Sub-campanha A — transferencia ZERO-REFIT transversal (spec 2026-07-03 §1).

Constantes do Estagio A congeladas; inputs nomeados com proveniencia; selecao
por REGRA pre-registrada (fontes + exclusoes por substring de CSV, todas
registradas com motivo). Dano OFF (casos = juntas novas; fidelidade ao Estagio
A, onde dano so ativa em juntas pre-danificadas) — colapsos devem sub-predizer
e isso e um ACHADO sobre crescimento de dano em junta virgem, nao um bug.

Run:  python New_Theory/transfer_validation.py
Runtime: ~2-5 min (46 curvas + sensibilidade em 8).
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
from bolt_analysis_studio.core.validation_cases import DIGITIZED_CASES  # noqa: E402
from library_common import (  # noqa: E402
    emb_depth_vdi, frozen_constants, geometry_for, load_full_curve,
    vdi_adjacent_classes,
)

ALLOWED_SOURCES = {"LIU_2025", "BAUER_2024", "LU_2024", "ICMEZ_2025",
                   "YANG_2019", "ROUSSEAU_2025", "KARLSEN_2022"}
EXCLUDE_TOKENS = {
    "hdpe": "par polimerico (HDPE) — fora do dominio declarado do modelo",
    "vibralock": "dispositivo de travamento — out-of-model declarado",
    "varamp": "protocolo de amplitude variavel — fora do harness de delta constante",
    "fig2_single": "ensaio ate fratura — fora do escopo de afrouxamento puro",
}
FLOOR_TRIM = 0.10          # pre-registrado: descarta pontos com ratio < 0.10
F_AMP_RATIO = 0.4          # assumed: mesma razao F_amp/F0 do rig âncora interna (Estagio A)
RZ_DEFAULT = "Rz10-40"     # superficies usinadas estruturais (assumed)
SENS_STEMS = {"liu2025_M16_amp0p25", "liu2025_M16_amp0p8",
              "lu2024_M8_fig18_amp0p25", "lu2024_M8_fig18_amp2p0",
              "bauer2024_M12_fig8_test1", "demir2024_amp0p4_F17p6_lk13p8",
              "karlsen2022_M42_HV_run20p0", "rousseau2025_steel_t10"}

# Inputs por fonte (MSD_BLOCK_COVERAGE + notas de aparato). grip 'assumed'
# segue a regra 2.5d; mu de Lu2024 derivado do coef. de torque K=0.23-0.27
# (Motosh) na nota — ~0.18.
SOURCE_INPUTS = {
    "LIU_2025":      dict(grip=None, mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "BAUER_2024":    dict(grip=("bolt", "paper"), mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "LU_2024":       dict(grip=None, mu=(0.18, "paper"), rz=RZ_DEFAULT),
    "ICMEZ_2025":    dict(grip=("csv", "paper"), mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "YANG_2019":     dict(grip=None, mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "ROUSSEAU_2025": dict(grip=("csv", "paper"), mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "KARLSEN_2022":  dict(grip=None, mu=(0.15, "assumed"), rz=RZ_DEFAULT),
}
ROUSSEAU_GRIPS = {"t10": 25.0, "t12": 29.0, "t14": 33.0}
ICMEZ_GRIPS = {"lk13p8": 13.8, "lk19p8": 19.8}
BAUER_GRIPS = {"M8": 8.0, "M12": 12.0}


def select_cases():
    selected, excluded = [], []
    for c in DIGITIZED_CASES:
        if c.source.name not in ALLOWED_SOURCES:
            continue
        if c.transverse_displacement_mm <= 0:
            continue
        csv = Path(c.reference_csv_path).name
        hit = next((t for t in EXCLUDE_TOKENS if t in csv), None)
        if hit:
            excluded.append(dict(csv=csv, reason=EXCLUDE_TOKENS[hit]))
        else:
            selected.append(c)
    return selected, excluded


def _d_mm(case):
    return float(case.bolt_size.split("x")[0][1:])


def inputs_for(case):
    src = SOURCE_INPUTS[case.source.name]
    stem = Path(case.reference_csv_path).stem
    # grip
    if src["grip"] is None:
        grip = dict(value=2.5 * _d_mm(case), prov="assumed")
    elif src["grip"][0] == "bolt":
        key = "M8" if case.bolt_size.startswith("M8") else "M12"
        grip = dict(value=BAUER_GRIPS[key], prov="paper")
    else:  # "csv"
        table = ROUSSEAU_GRIPS if "rousseau" in stem else ICMEZ_GRIPS
        key = next(k for k in table if k in stem)
        grip = dict(value=table[key], prov="paper")
    mu = dict(value=src["mu"][0], prov=src["mu"][1])
    rz = dict(value=src["rz"], prov="assumed")
    F_amp = dict(value=F_AMP_RATIO * case.initial_preload_N, prov="assumed")
    return dict(grip_mm=grip, mu=mu, rz=rz, F_amp_N=F_amp)


def _simulate(case, grip_mm, mu, rz_class, F_amp_N, n_cycles):
    consts, _ = frozen_constants()
    emb_m, _ = emb_depth_vdi(rz_class, n_inner_interfaces=1)
    geom = geometry_for(case.bolt_size, grip_mm=grip_mm)
    mat = JointMaterial(emb_depth=emb_m, mu_thread=mu, mu_bearing=mu, **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, case.initial_preload_N)
    delta = case.transverse_displacement_mm * 1e-3
    ratio = np.empty(n_cycles + 1)
    ratio[0] = 1.0
    for n in range(1, n_cycles + 1):
        ana.step_cycle(F_amp_N, np.pi / 2, case.frequency_Hz, delta_amp=delta)
        ratio[n] = max(ana.state.F_0, 0.0) / case.initial_preload_N
    return ratio


def _fit_exp(n, r):
    m = r > 0.05
    if m.sum() < 2 or n[m].max() <= 0:
        return 0.0
    return max(float(-np.polyfit(n[m], np.log(r[m]), 1)[0]), 0.0)


def _mae_curve(case, inp, cyc_d, r_d_al, n0, grip=None, mu=None, rz=None,
               F_amp=None):
    n_max = int(cyc_d[-1])
    sim = _simulate(case, grip or inp["grip_mm"]["value"],
                    mu or inp["mu"]["value"], rz or inp["rz"]["value"],
                    F_amp or inp["F_amp_N"]["value"], n_max)
    sim_al = sim / max(np.interp(n0, np.arange(n_max + 1), sim), 1e-9)
    pred = np.interp(cyc_d, np.arange(n_max + 1), sim_al)
    return float(np.mean(np.abs(pred - r_d_al))), pred


def predict_case(case, do_sensitivity):
    cyc, ratio = load_full_curve(case.reference_csv_path)
    keep = ratio >= FLOOR_TRIM
    n_trimmed = int((~keep).sum())
    cyc_d, r_d = cyc[keep], ratio[keep]
    n0 = cyc_d[0]
    r_d_al = r_d / r_d[0]
    inp = inputs_for(case)
    mae, pred = _mae_curve(case, inp, cyc_d, r_d_al, n0)
    mae_noloss = float(np.mean(np.abs(1.0 - r_d_al)))
    lam = _fit_exp(cyc_d - n0, r_d_al)
    mae_exp = float(np.mean(np.abs(np.exp(-lam * (cyc_d - n0)) - r_d_al)))
    band = None
    if do_sensitivity:
        maes = [mae]
        v = inp["mu"]["value"]
        for mu2 in (0.75 * v, 1.25 * v):
            maes.append(_mae_curve(case, inp, cyc_d, r_d_al, n0, mu=mu2)[0])
        for rz2 in set(vdi_adjacent_classes(inp["rz"]["value"])):
            maes.append(_mae_curve(case, inp, cyc_d, r_d_al, n0, rz=rz2)[0])
        F0 = case.initial_preload_N
        for fr in (0.2, 0.6):
            maes.append(_mae_curve(case, inp, cyc_d, r_d_al, n0,
                                   F_amp=fr * F0)[0])
        if inp["grip_mm"]["prov"] == "assumed":
            d = _d_mm(case)
            for g in (2.0 * d, 3.0 * d):
                maes.append(_mae_curve(case, inp, cyc_d, r_d_al, n0, grip=g)[0])
        band = [min(maes), max(maes)]
    return dict(name=case.name, csv=Path(case.reference_csv_path).name,
                source=case.source.name, F0_N=case.initial_preload_N,
                delta_amp_mm=case.transverse_displacement_mm,
                freq_Hz=case.frequency_Hz,
                inputs={k: dict(value=(v["value"] if not isinstance(
                    v["value"], str) else v["value"]), prov=v["prov"])
                    for k, v in inp.items()},
                n_cycles=int(cyc_d[-1]), n_trimmed=n_trimmed,
                MAE=mae, MAE_noloss=mae_noloss, MAE_exp=mae_exp,
                final_data=float(r_d_al[-1]), final_pred=float(pred[-1]),
                band=band,
                curve=dict(cycles=cyc_d.tolist(), data=r_d_al.tolist(),
                           pred=pred.tolist()))


def main():
    selected, excluded = select_cases()
    consts, prov = frozen_constants()
    print(f"{len(selected)} curvas selecionadas, {len(excluded)} excluidas "
          f"(com motivo). Constantes congeladas: {consts}")
    results = []
    for case in selected:
        stem = Path(case.reference_csv_path).stem
        r = predict_case(case, do_sensitivity=stem in SENS_STEMS)
        results.append(r)
        print(f"{r['csv']:45s} MAE={r['MAE']:.4f} exp={r['MAE_exp']:.4f} "
              f"noloss={r['MAE_noloss']:.4f}")

    # agregados por fonte + global
    def _agg(rs):
        maes = [r["MAE"] for r in rs]
        return dict(n=len(rs), median_MAE=float(np.median(maes)),
                    p90_MAE=float(np.percentile(maes, 90)),
                    beats_exp=int(sum(r["MAE"] <= r["MAE_exp"] for r in rs)),
                    beats_noloss=int(sum(r["MAE"] <= r["MAE_noloss"]
                                         for r in rs)))
    per_source = {}
    for r in results:
        per_source.setdefault(r["source"], []).append(r)
    aggregates = {s: _agg(rs) for s, rs in sorted(per_source.items())}
    aggregates["GLOBAL"] = _agg(results)
    for s, a in aggregates.items():
        print(f"{s:15s} n={a['n']:2d} medianMAE={a['median_MAE']:.4f} "
              f"p90={a['p90_MAE']:.4f} vs_exp={a['beats_exp']}/{a['n']} "
              f"vs_noloss={a['beats_noloss']}/{a['n']}")

    # grid unico
    ncols = 7
    nrows = int(np.ceil(len(results) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 3 * nrows))
    for ax, r in zip(np.atleast_1d(axes).flat, results):
        ax.plot(r["curve"]["cycles"], r["curve"]["data"], "o-", ms=2)
        ax.plot(r["curve"]["cycles"], r["curve"]["pred"], "k-")
        ax.set_title(f"{r['csv'][:34]}\nMAE={r['MAE']:.3f}", fontsize=7)
        ax.set_ylim(0, 1.05)
        ax.grid(alpha=0.3)
    for ax in np.atleast_1d(axes).flat[len(results):]:
        ax.axis("off")
    plt.tight_layout()
    fig.savefig(ROOT / "New_Theory" / "transfer_grid.png", dpi=90)

    out = dict(
        campaign="A zero-refit transversal (spec 2026-07-03 §1)",
        frozen_constants=consts,
        choices=dict(F_amp_ratio=F_AMP_RATIO, floor_trim=FLOOR_TRIM,
                     rz_default=RZ_DEFAULT,
                     damage="OFF — juntas novas; no Estagio A o dano so ativa "
                            "em juntas pre-danificadas; colapsos devem "
                            "sub-predizer (achado, nao bug)",
                     alignment="normalizacao no 1o ponto do dado"),
        exclusions=excluded,
        aggregates=aggregates,
        results=[{k: v for k, v in r.items() if k != "curve"}
                 for r in results])
    (ROOT / "New_Theory" / "transfer_results.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    g = aggregates["GLOBAL"]
    lines = ["# Transferencia zero-refit transversal (spec 2026-07-03 §1)", "",
             f"{len(results)} curvas, {len(excluded)} exclusoes registradas. "
             f"GLOBAL: mediana MAE {g['median_MAE']:.4f}, p90 {g['p90_MAE']:.4f}, "
             f"vence exp {g['beats_exp']}/{g['n']}, vence no-loss "
             f"{g['beats_noloss']}/{g['n']}.", "",
             "| Fonte | n | mediana | p90 | vs exp | vs no-loss |",
             "|---|--:|--:|--:|--:|--:|"]
    for s, a in aggregates.items():
        lines.append(f"| {s} | {a['n']} | {a['median_MAE']:.4f} | "
                     f"{a['p90_MAE']:.4f} | {a['beats_exp']}/{a['n']} | "
                     f"{a['beats_noloss']}/{a['n']} |")
    (ROOT / "New_Theory" / "transfer_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("Artefatos: transfer_results.json, transfer_grid.png, "
          "transfer_report.md")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Syntax check + run tests**

Run: `python -c "import ast; ast.parse(open('New_Theory/transfer_validation.py', encoding='utf-8').read()); print('OK')"`
Run: `python -m pytest tests/test_transfer_validation.py -v`
Expected: 3 PASS (~1 min; the smoke predict runs one short curve). If `test_selection_rule_counts_and_exclusions` fails on a per-source count, STOP and report the actual `per_source` dict — the builder may use different enum names than pre-registered; that is a controller decision, not something to patch silently. Same rule for a `KeyError` from `geometry_for` on an unexpected `bolt_size` string (e.g. "M30" without pitch): STOP and report the exact string — the controller adds the ISO alias; do not guess a geometry.

- [ ] **Step 5: The sweep (background, tee to `.superpowers/sdd/transfer-sweep.log`, ~2–5 min)**

Run: `python New_Theory/transfer_validation.py 2>&1 | tee .superpowers/sdd/transfer-sweep.log`
Sanity: ~46 curves, exclusions ≥ 10 with reasons, all MAEs finite, aggregates printed for 7 sources + GLOBAL, 3 artifacts written. Record AS IS.

- [ ] **Step 6: Commit**

```bash
git add New_Theory/transfer_validation.py tests/test_transfer_validation.py New_Theory/transfer_results.json New_Theory/transfer_report.md
git add -f New_Theory/transfer_grid.png
git commit -m "calib: varredura de transferencia zero-refit transversal (46 curvas, 7 papers)

Constantes do Estagio A congeladas; selecao por regra pre-registrada com
exclusoes motivadas; inputs nomeados com proveniencia; dois baselines;
bandas de sensibilidade no subconjunto pre-registrado; dano OFF (juntas
novas, fidelidade ao Estagio A). Resultados AS IS.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: docs — transfer verdict + Phase-1 wrap

**Files:**
- Modify: `New_Theory/MODEL_LEGITIMACY.md` (§4.8 after §4.7; §8 Fase-1 wrap; §9 changelog)
- Modify: `CLAUDE.md` (command; suite line gains `tests/test_transfer_validation.py`)

**Interfaces:**
- Consumes: `New_Theory/transfer_results.json` + `transfer_report.md`.

- [ ] **Step 1: MODEL_LEGITIMACY §4.8**

Insert after §4.7 (Portuguese WITH accents; `<...>` transcribed from the JSON):

```markdown
### 4.8 Transferência zero-refit transversal — a varredura (Fase 1A, spec §1)

<n> curvas de <7> papers (M8→M42, 0,07–2,0 mm), preditas com as constantes do
Estágio A congeladas e inputs nomeados com procedência (`paper`/`handbook`/
`assumed` com bandas); <n_excl> exclusões registradas com motivo (HDPE,
Vibralock, amplitude variável, fratura). Dano OFF por pré-registro (juntas
novas — no Estágio A o dano só ativa em juntas pré-danificadas).

| Agregado | mediana MAE | p90 | vence exp (1-par/curva) | vence no-loss |
|---|---:|---:|---:|---:|
| GLOBAL | <...> | <...> | <...> | <...> |
<uma linha por fonte>

<4-6 frases honestas: onde transfere (fontes/regimes com mediana baixa e
vitórias sobre o baseline exponencial = evidência genuína de generalização);
onde falha e o que a falha aponta (colapsos sem dano-de-virgem; escala M30/M42;
amplitudes extremas; sensibilidade a inputs assumed onde a banda cruza a
conclusão → `inconclusive`); como isso se compara ao arnês sintético §4.3.>
```

- [ ] **Step 2: §8 Fase-1 wrap + changelog + CLAUDE.md**

§8: update the generalization bullet to summarize all three Fase-1 results (axial falsification §4.6; C_creep per-pair anchor §4.7; transverse transfer §4.8 with its headline). §9 changelog row:

```markdown
| 2026-07-03 | §4.8 varredura de transferência zero-refit (Fase 1A): <n> curvas/7 papers com constantes congeladas e inputs com procedência; <resumo de 1 linha do resultado>. Fase 1 (B axial, C âncora, A transferência) completa — ver §8. |
```

CLAUDE.md: command `python New_Theory/transfer_validation.py   # varredura zero-refit (~2-5 min)`; suite line gains `tests/test_transfer_validation.py`.

- [ ] **Step 3: Regression + commit**

Run: `python -m pytest tests/test_transfer_validation.py tests/test_library_common.py tests/test_anchor_creep.py -q`
Expected: ~12 passed.

```bash
git add New_Theory/MODEL_LEGITIMACY.md CLAUDE.md
git commit -m "docs: veredicto da transferencia zero-refit (§4.8) + fechamento da Fase 1 (§8)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Report the sweep verdict + the Phase-1 completion summary.
