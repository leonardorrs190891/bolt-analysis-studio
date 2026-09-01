# Sobretorque F0-bound 133 kN — Discrimination Run Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Discriminate the sobretorque falsification (MODEL_LEGITIMACY §4.5) — is the shared fit's bad sobretorque MAE (0.1378, F0 pinned at the 120 kN bound) because the bound is *too tight* (true over-torque preload was higher), or because a *pressure-dependent contact regime is missing* from the physics?

**Architecture:** A standalone experiment script `New_Theory/sobretorque_f0bound.py`, modeled on `New_Theory/anchor_creep.py` (own JSON/PNG/report; the canonical `shared` block of `joint_calibrations.json` is **never written**). It re-runs Stage A (`SharedCalibrator.fit_parsimonious`) with only one change — the sobretorque `estimate_F0` upper bound raised from 120 kN to the physical sanity ceiling `F0_SANITY_N ≈ 132.8 kN` (= 0.9·Rp0.2·A_s) — then compares against the committed baseline and classifies the outcome with **pre-registered** thresholds. Pure helpers (`read_baseline`, `classify_verdict`) are unit-tested; the fit itself is a science run recorded **as is**.

**Tech Stack:** Python 3, numpy, scipy (via `SharedCalibrator`), matplotlib (Agg). Reuses `New_Theory/calibrate_shared.py::build_shared_config` and `bolt_analysis_studio.calibration.shared_calibrator.SharedCalibrator`.

## Model tiering & swaps (session on Opus 4.8 max effort)

Baked-in recommendation the professor accepted (Opus session + Fable subagents at two specific points):

| Task | Implementer | Task reviewer | Notes |
|---|---|---|---|
| 1 (helpers + tests) | sonnet | sonnet | Mechanical; plan carries the code. |
| 2 (fit orchestration + smoke) | sonnet | sonnet | Mechanical transcription + `--quick` smoke. |
| 3 (real run, record AS IS) | opus | — (no code; controller verifies artifacts) | Long run; interpretation is Task 4. |
| 4 (MODEL_LEGITIMACY §4.5 addendum) | **fable** (falsification-logic + scientific writing) | **fable** | This is the load-bearing swap: the discrimination verdict is a scientific conclusion written into the living doc. |
| Final whole-branch review | **fable** | — | Per subagent-driven-development, dispatch the final review on the most capable model. |

**Fallback if subagents have no Fable access:** run Task 4 and the final review on **Opus 4.8 at max effort**. You lose the independent-derivation edge on the verdict logic — mitigate by having the Task-4 reviewer *recompute* the verdict from the raw JSON numbers rather than trusting the script's printed verdict.

**Do NOT** downgrade Task 4 to a cheap model, and do NOT let the implementer that wrote the script also be the sole reviewer of its scientific verdict.

## Global Constraints

- All file I/O uses `encoding='utf-8'` (Windows charmap errors otherwise).
- Syntax-check every `.py` edit before testing: `python -c "import ast; ast.parse(open('PATH', encoding='utf-8').read()); print('OK')"`.
- **Never `git add -A`.** Stage explicit file lists only — the repo is OneDrive-synced and a parallel session writes into the same checkout. Foreign uncommitted changes in the working tree are the user's WIP: never stage them.
- **The canonical `shared` block of `New_Theory/joint_calibrations.json` is NEVER written by this experiment.** This script only writes `sobretorque_f0bound.{json,png,md}` — same discipline as `creep_anchor.json`.
- **Science results are recorded AS IS.** Never tune thresholds or inputs to force a verdict. The three verdicts (rescued / missing-mechanism / partial) are all publishable outcomes.
- `.json`/`.png`/`.md`/`.py` are **not** gitignored — normal `git add <path>` works (unlike `*.csv`/`*.pdf`).
- Commits in Portuguese, no accents, ending with the trailer `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` (the trailer reflects the model that authored the commit; Fable-authored commits use the Fable line).
- `tests/conftest.py` puts `src/` on `sys.path`; test files that import `New_Theory/` modules add `New_Theory` themselves.

---

### Task 1: Pure helpers + pre-registered thresholds

**Files:**
- Create: `New_Theory/sobretorque_f0bound.py` (constants + pure helpers only in this task)
- Test: `tests/test_sobretorque_f0bound.py`

**Interfaces:**
- Consumes: nothing (self-contained pure functions).
- Produces (later tasks + tests rely on these exact names):
  - `F0_SANITY_N: float` — sanity ceiling, ≈ 132822 N.
  - `RESCUE_MAE = 0.06`, `PERSIST_MAE = 0.10` — pre-registered verdict thresholds.
  - `read_baseline(json_path) -> dict` with keys `mae` (float), `f0_N` (float), `mae_global` (float), read from the committed `shared` block.
  - `classify_verdict(mae_base, mae_new, f0_new, ceiling) -> dict` with keys `verdict` (str), `pinned_at_new_ceiling` (bool), `delta_mae` (float), `mae_base`, `mae_new`, `f0_new_N`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_sobretorque_f0bound.py`:

```python
"""Discriminacao do sobretorque (bound F0 -> 133 kN). Testa os helpers puros
(thresholds pre-registrados); a corrida cientifica em si nao e testada."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "New_Theory"))
sys.path.insert(0, str(ROOT / "src"))

from sobretorque_f0bound import (  # noqa: E402
    F0_SANITY_N, RESCUE_MAE, PERSIST_MAE, read_baseline, classify_verdict,
)


def test_ceiling_matches_calibrate_shared_and_value():
    # DRY: mesmo teto de sanidade que calibrate_shared.F0_SANITY_N
    from calibrate_shared import F0_SANITY_N as canonical
    assert F0_SANITY_N == pytest.approx(canonical)
    assert F0_SANITY_N == pytest.approx(132_822.0, rel=1e-4)


def test_read_baseline_from_shared_block(tmp_path):
    j = tmp_path / "joint_calibrations.json"
    j.write_text(json.dumps({
        "schema": 2,
        "shared": {
            "mae_global": 0.0796,
            "conditions": {
                "sobretorque": {
                    "states": {"F0_test_N": 120000.0, "F0_provenance": "estimated"},
                    "MAE": 0.1378,
                },
            },
        },
    }), encoding="utf-8")
    b = read_baseline(j)
    assert b["mae"] == pytest.approx(0.1378)
    assert b["f0_N"] == pytest.approx(120000.0)
    assert b["mae_global"] == pytest.approx(0.0796)


def test_classify_verdict_rescued():
    # MAE cai para a banda fittavel + F0 interior => bound era apertado demais
    v = classify_verdict(mae_base=0.1378, mae_new=0.03,
                         f0_new=125_000.0, ceiling=F0_SANITY_N)
    assert v["verdict"] == "bound-too-tight (rescued)"
    assert v["pinned_at_new_ceiling"] is False
    assert v["delta_mae"] == pytest.approx(0.1078)


def test_classify_verdict_missing_mechanism():
    # F0 crava no novo teto e MAE continua alta => mecanismo faltante
    v = classify_verdict(mae_base=0.1378, mae_new=0.13,
                         f0_new=F0_SANITY_N, ceiling=F0_SANITY_N)
    assert v["verdict"] == "missing mechanism (falsified again)"
    assert v["pinned_at_new_ceiling"] is True


def test_classify_verdict_partial():
    v = classify_verdict(mae_base=0.1378, mae_new=0.08,
                         f0_new=128_000.0, ceiling=F0_SANITY_N)
    assert v["verdict"] == "partial / inconclusive"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_sobretorque_f0bound.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sobretorque_f0bound'` (module not created yet).

- [ ] **Step 3: Write the minimal module (constants + helpers)**

Create `New_Theory/sobretorque_f0bound.py`:

```python
"""Fase 2 — discriminacao do sobretorque (MODEL_LEGITIMACY §4.5).

O Estagio A nao fecha o sobretorque: F0_test cravou no bound de 120 kN, MAE
0.1378 (18.9x o fit local de 1 parametro). Duas hipoteses:
  (A) bound apertado demais — a pre-carga real do ensaio (over-torque) era
      > 120 kN; com o teto elevado ao limite de sanidade (0.9*Rp0.2*A_s ~
      132.8 kN) o fit compartilhado alcanca o sobretorque.
  (B) mecanismo faltante — over-torque introduz um regime dependente da
      pressao de contato (atrito/wear/assentamento) ausente na fisica atual;
      elevar o teto NAO resgata o sobretorque.

Este experimento re-roda o Estagio A com o UNICO input mudado (teto do
estimate_F0 do sobretorque), le o baseline COMMITADO e classifica o resultado
com thresholds PRE-REGISTRADOS. Artefatos proprios; o bloco `shared` canonico
NUNCA e escrito (mesma disciplina de creep_anchor.json).

CUIDADO (spec Fase 1 §4): a hipotese GW k_tr(F0) para pressao-de-contato tem
sinal DESFAVORAVEL no slip atual (k_tr^ => slip^). Um veredicto de "mecanismo
faltante" NAO deve ser lido como aval para ressuscitar GW k_tr(F0) ingenuo.

Run:  python New_Theory/sobretorque_f0bound.py [--quick]
  --quick: n_cycles=300 (smoke; NAO gravar como resultado cientifico)
Runtime do run completo: ~15-40 min (fit_parsimonious x 4 condicoes + LOCO
nao e re-rodado aqui).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

SHARED_JSON = ROOT / "New_Theory" / "joint_calibrations.json"
OUT_JSON = ROOT / "New_Theory" / "sobretorque_f0bound.json"
OUT_PNG = ROOT / "New_Theory" / "sobretorque_f0bound.png"
OUT_MD = ROOT / "New_Theory" / "sobretorque_f0bound_report.md"

# Teto de sanidade F0 = 0.9 * Rp0.2(classe 10.9 = 940 MPa) * A_s(M16 = 157mm2)
# = 132.8 kN. Mesma formula de calibrate_shared.F0_SANITY_N (teste pina).
F0_SANITY_N = 0.9 * 940e6 * 157e-6

# Thresholds PRE-REGISTRADOS do veredicto (nao mexer para forcar resultado):
#   RESCUE_MAE  = entra na banda fittavel (demais condicoes fitam 0.046-0.05).
#   PERSIST_MAE = continua longe (> ~70% do baseline 0.138).
RESCUE_MAE = 0.06
PERSIST_MAE = 0.10


def read_baseline(json_path=SHARED_JSON) -> dict:
    """Baseline do sobretorque do bloco `shared` COMMITADO (bound 120 kN)."""
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    sob = data["shared"]["conditions"]["sobretorque"]
    return dict(mae=float(sob["MAE"]),
                f0_N=float(sob["states"]["F0_test_N"]),
                mae_global=float(data["shared"]["mae_global"]))


def classify_verdict(mae_base: float, mae_new: float, f0_new: float,
                     ceiling: float) -> dict:
    """Classificacao pre-registrada. AS IS — nenhum threshold e ajustado."""
    pinned = f0_new >= 0.999 * ceiling
    if mae_new <= RESCUE_MAE:
        verdict = "bound-too-tight (rescued)"
    elif mae_new >= PERSIST_MAE:
        verdict = "missing mechanism (falsified again)"
    else:
        verdict = "partial / inconclusive"
    return dict(verdict=verdict, pinned_at_new_ceiling=pinned,
                delta_mae=mae_base - mae_new,
                mae_base=mae_base, mae_new=mae_new, f0_new_N=f0_new)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_sobretorque_f0bound.py -v`
Expected: PASS (5 tests).

- [ ] **Step 5: Syntax-check and commit**

```bash
python -c "import ast; ast.parse(open('New_Theory/sobretorque_f0bound.py', encoding='utf-8').read()); print('OK')"
git add New_Theory/sobretorque_f0bound.py tests/test_sobretorque_f0bound.py
git commit -m "fase2: helpers do experimento sobretorque F0-bound (thresholds pre-registrados)"
```

---

### Task 2: Fit orchestration (raised bound) + smoke

**Files:**
- Modify: `New_Theory/sobretorque_f0bound.py` (append `run_raised_fit` + `main`)

**Interfaces:**
- Consumes: `build_shared_config` (from `calibrate_shared`), `SharedCalibrator` (from `bolt_analysis_studio.calibration.shared_calibrator`), and the Task-1 helpers.
- Produces: `run_raised_fit(n_cycles) -> (cal, res)` where `cal` is the fitted `SharedCalibrator` and `res` is the `fit_parsimonious` result dict; `main()` writing `sobretorque_f0bound.{json,png,md}`.

- [ ] **Step 1: Append `run_raised_fit` and `main` to the module**

Append to `New_Theory/sobretorque_f0bound.py`:

```python
def run_raised_fit(n_cycles: int):
    """Re-roda o Estagio A com o UNICO input mudado: teto do estimate_F0 do
    sobretorque 120 kN -> F0_SANITY_N (~132.8 kN). Import de calibrate_shared
    e lazy (mantem o import do modulo leve para os testes dos helpers)."""
    from calibrate_shared import build_shared_config
    from bolt_analysis_studio.calibration.shared_calibrator import SharedCalibrator
    cfg = build_shared_config(n_cycles=n_cycles)
    cfg.estimate_F0 = dict(cfg.estimate_F0,
                           sobretorque=(40_000.0, F0_SANITY_N))
    cal = SharedCalibrator(cfg)
    res = cal.fit_parsimonious(tol=0.005, max_constants=4)
    return cal, res


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    quick = "--quick" in sys.argv
    n_cycles = 300 if quick else 2500

    base = read_baseline()
    cal, res = run_raised_fit(n_cycles)
    mae_new = float(res["mae_by_condition"]["sobretorque"])
    f0_new = float(res["F0_estimates"]["sobretorque"])
    verdict = classify_verdict(base["mae"], mae_new, f0_new, F0_SANITY_N)

    print("== sobretorque: bound F0 120 kN -> %.1f kN (sanity) ==" %
          (F0_SANITY_N / 1e3))
    print(f"baseline : MAE {base['mae']:.4f}  F0 {base['f0_N']/1e3:.1f} kN "
          f"(global {base['mae_global']:.4f})")
    print(f"raised   : MAE {mae_new:.4f}  F0 {f0_new/1e3:.1f} kN "
          f"(global {res['mae_global']:.4f})  livres {res['free_constants']}")
    print(f"veredicto: {verdict['verdict']}  "
          f"(dMAE {verdict['delta_mae']:+.4f}, "
          f"cravado_no_teto={verdict['pinned_at_new_ceiling']})")

    # plot: TP6 + sim do bound elevado (baseline anotado no titulo)
    sob = next(c for c in cal.cfg.conditions if c.name == "sobretorque")
    sim_N, sim_ratio = cal._run_condition(sob)
    fig, ax = plt.subplots(figsize=(8, 5))
    for c in sob.curves:
        ax.plot(c["cycles"], c["ratio"], "o-", ms=4, color="#00B050",
                alpha=0.8, label=c["name"])
    ax.plot(sim_N, sim_ratio, "k-", lw=2.5,
            label=f"sim bound {F0_SANITY_N/1e3:.0f}kN "
                  f"(MAE={mae_new:.3f}, F0={f0_new/1e3:.1f}kN)")
    ax.set_title(f"sobretorque — baseline 120kN MAE {base['mae']:.3f}  |  "
                 f"veredicto: {verdict['verdict']}", fontsize=9)
    ax.set_xlabel("Ciclos N"); ax.set_ylabel(r"$F_0/F_{0,init}$")
    ax.set_xlim(0, n_cycles); ax.set_ylim(0, 1.05); ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    fig.savefig(OUT_PNG, dpi=120)

    if quick:
        print("--quick: smoke (NAO cientifico); artefatos gerados, sem gravar "
              "JSON/report de resultado.")
        return

    out = dict(
        campaign="Fase 2 — sobretorque F0-bound (MODEL_LEGITIMACY §4.5)",
        provenance=dict(
            f0_ceiling_N=F0_SANITY_N,
            f0_ceiling_formula="0.9 * Rp0.2(10.9=940MPa) * A_s(M16=157mm2)",
            only_change="estimate_F0[sobretorque] top 120kN -> 132.8kN",
            canonical_shared_block="NAO escrito (experimento)"),
        thresholds=dict(RESCUE_MAE=RESCUE_MAE, PERSIST_MAE=PERSIST_MAE),
        baseline=base,
        raised=dict(mae_sobretorque=mae_new, f0_test_N=f0_new,
                    mae_global=res["mae_global"],
                    free_constants=res["free_constants"],
                    mae_by_condition=res["mae_by_condition"],
                    F0_estimates=res["F0_estimates"]),
        verdict=verdict,
        caveat=("GW k_tr(F0) tem sinal desfavoravel no slip atual (spec Fase 1 "
                "§4) — 'missing mechanism' NAO avaliza k_tr(F0) ingenuo."))
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")

    lines = [
        "# Sobretorque — discriminacao do bound F0 (Fase 2)", "",
        f"Baseline (bound 120 kN): MAE {base['mae']:.4f}, "
        f"F0 {base['f0_N']/1e3:.1f} kN, global {base['mae_global']:.4f}.", "",
        f"Bound elevado ao teto de sanidade ({F0_SANITY_N/1e3:.1f} kN): "
        f"MAE {mae_new:.4f}, F0 {f0_new/1e3:.1f} kN, "
        f"global {res['mae_global']:.4f}.", "",
        f"**Veredicto (pre-registrado): {verdict['verdict']}** "
        f"(dMAE {verdict['delta_mae']:+.4f}; "
        f"cravado no teto: {verdict['pinned_at_new_ceiling']}).", "",
        "Ressalva: GW k_tr(F0) tem sinal desfavoravel no slip atual "
        "(spec Fase 1 §4).",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Artefatos: {OUT_JSON.name}, {OUT_PNG.name}, {OUT_MD.name}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Syntax-check**

Run: `python -c "import ast; ast.parse(open('New_Theory/sobretorque_f0bound.py', encoding='utf-8').read()); print('OK')"`
Expected: `OK`

- [ ] **Step 3: Re-run the helper tests (regression — module still imports light)**

Run: `python -m pytest tests/test_sobretorque_f0bound.py -v`
Expected: PASS (5 tests) — importing the module must not trigger the heavy `calibrate_shared` import (it is lazy inside `run_raised_fit`).

- [ ] **Step 4: Smoke the full path with `--quick`**

Run: `python New_Theory/sobretorque_f0bound.py --quick`
Expected: prints baseline + raised + a `veredicto:` line, creates `New_Theory/sobretorque_f0bound.png`, and prints the `--quick` non-scientific notice (no JSON/report written). Values are meaningless at n_cycles=300 — this only proves the path runs end-to-end.

- [ ] **Step 5: Commit (do NOT commit the smoke PNG)**

```bash
git checkout -- New_Theory/sobretorque_f0bound.png 2>/dev/null || rm -f New_Theory/sobretorque_f0bound.png
git add New_Theory/sobretorque_f0bound.py
git commit -m "fase2: orquestracao do fit com bound elevado + smoke --quick"
```

---

### Task 3: Real run — record the verdict AS IS

**Files:**
- Produce (artifacts, committed): `New_Theory/sobretorque_f0bound.json`, `New_Theory/sobretorque_f0bound.png`, `New_Theory/sobretorque_f0bound_report.md`

**Interfaces:**
- Consumes: the committed module + the intact `shared` block of `joint_calibrations.json`.
- Produces: the recorded discrimination result consumed by Task 4.

- [ ] **Step 1: Confirm the baseline block is intact (canary)**

Run: `python -c "import json; d=json.load(open('New_Theory/joint_calibrations.json',encoding='utf-8')); s=d['shared']['conditions']['sobretorque']; print(round(s['MAE'],4), round(s['states']['F0_test_N']/1e3,1))"`
Expected: `0.1378 120.0` (approx). If this fails, the `shared` block was clobbered — STOP and restore from git before proceeding (do not run the experiment against a corrupted baseline).

- [ ] **Step 2: Run the real experiment (background, ~15-40 min)**

Run: `python New_Theory/sobretorque_f0bound.py`
Expected: writes `sobretorque_f0bound.{json,png,md}`, prints the baseline/raised/veredicto lines. **Record the verdict exactly as printed — do not re-run to get a different answer.**

- [ ] **Step 3: Verify the canonical block was NOT touched**

Run: `git status --porcelain New_Theory/joint_calibrations.json`
Expected: **empty** (the experiment must not modify `joint_calibrations.json`). If it is non-empty, that is a bug in the script — fix and re-run.

- [ ] **Step 4: Commit the artifacts**

```bash
git add New_Theory/sobretorque_f0bound.json New_Theory/sobretorque_f0bound.png New_Theory/sobretorque_f0bound_report.md
git commit -m "fase2: resultado do experimento sobretorque F0-bound (AS IS)"
```

---

### Task 4: MODEL_LEGITIMACY §4.5 addendum (Fable swap)

**Files:**
- Modify: `New_Theory/MODEL_LEGITIMACY.md` (append an addendum to §4.5)

**Interfaces:**
- Consumes: `New_Theory/sobretorque_f0bound.json` (the recorded numbers).
- Produces: the updated living-doc conclusion.

> **Dispatch this task on Fable** (falsification-logic + scientific writing). The reviewer (also Fable, or Opus-max fallback) must **recompute** `verdict`, `delta_mae`, and `pinned_at_new_ceiling` directly from `sobretorque_f0bound.json` and confirm they match the addendum text — do not trust the script's printed verdict blindly.

- [ ] **Step 1: Read the current §4.5 and the result JSON**

Read `New_Theory/MODEL_LEGITIMACY.md` (locate §4.5) and `New_Theory/sobretorque_f0bound.json`.

- [ ] **Step 2: Write the addendum**

Append to §4.5 an addendum stating, from the JSON: baseline (120 kN, MAE 0.1378), raised-ceiling result (F0, MAE, global, pinned?), the pre-registered verdict, and the interpretation:
- **rescued** → the 120 kN bound was too tight; the true test preload was higher; record the recovered F0 with provenance `estimated (F0-bound raised to sanity ceiling)`. Note whether F0 landed at the ceiling (→ over-torque near 0.9·Rp0.2, flag for provenance).
- **missing mechanism** → raising F0 to the yield-based sanity ceiling did not rescue sobretorque; this is a *structural* falsification pointing at a pressure-dependent contact regime absent from the current physics. **Explicitly state** the GW k_tr(F0) sign caveat (spec Fase 1 §4): the fix is not naive pressure-stiffness. Cross-link to the Phase-2 sequencing doc.
- **partial** → record both effects AS IS; no forcing.

Keep the canonical `shared` block described as unchanged (this was an experiment). Add a `## Changelog` line dated today.

- [ ] **Step 3: Commit**

```bash
git add New_Theory/MODEL_LEGITIMACY.md
git commit -m "docs: §4.5 addendum — veredicto do experimento sobretorque F0-bound"
```

---

## Self-Review (controller, after all tasks)

- **Spec coverage:** discrimination question answered with a pre-registered verdict? ✅ Tasks 1–4.
- **Canonical block untouched:** Task 3 Step 3 enforces it. ✅
- **AS IS:** thresholds frozen in Task 1; Task 3 forbids re-running for a different answer. ✅
- **Type consistency:** `read_baseline`/`classify_verdict` keys match between the module (Task 1), `main` (Task 2), and the test (Task 1). ✅
- **Model swaps:** Task 4 + final review flagged for Fable with an Opus-max fallback and a recompute-the-verdict guard. ✅
