# Conformation Validation (Plan B — calibration + science) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test whether the pressure-conformation mechanism (Plan A, merged `0e60082`) resolves the sobretorque falsification (spec `2026-07-04-pressure-conformation-design.md` §9): does a shared fit with conformation active plateau sobretorque toward its ~0.007 floor **without disturbing** nova/reusada/reaperto (residual ≈ baseline)? Recorded AS IS — RESOLVED / PARTIAL / FALSIFIED.

**Architecture:** A standalone experiment `New_Theory/conformation_fit.py` (canonical `shared` block **never written** — `creep_anchor`/`sobretorque_f0bound` precedent). A direct A/B fit via `SharedCalibrator._fit_subset`: **baseline** `{C_creep}` (conformation off) vs **treatment** `{C_creep, W_conf_ref}` (conformation active, `conform_pressure_exp=2` and `p_ref_conform=5e8` fixed — one new fitted number). Same 120 kN sobretorque F0 setup in both arms, so conformation is the only difference. Pure helpers (`classify_conformation_verdict`, `build_conformation_config`) are unit-tested; the fit is a science run recorded AS IS.

**Tech Stack:** Python 3, numpy, scipy (via `SharedCalibrator`), matplotlib (Agg). Reuses `New_Theory/calibrate_shared.py::build_shared_config` + `bolt_analysis_studio.calibration.shared_calibrator`.

## Model tiering & swaps (session on Opus 4.8 max effort)

| Task | Implementer | Task reviewer |
|---|---|---|
| 1 (helpers + tests) | sonnet | sonnet |
| 2 (A/B orchestration + smoke) | sonnet | sonnet |
| 3 (real A/B run, record AS IS) | opus (controller verifies) | — |
| 4 (MODEL_LEGITIMACY §4.9) | **fable** (falsification-logic + writing) | **fable** |
| Final whole-branch review | **fable** | — |

**Fable is load-bearing here** (the verdict is a scientific conclusion). Fallback if subagents lack Fable: Opus-max, with the reviewer **recomputing the verdict from `conformation_fit.json`** rather than trusting the script's printed verdict.

## Global Constraints

- All file I/O uses `encoding='utf-8'`; `ast.parse` syntax-check every `.py` edit.
- **Never `git add -A`.** Explicit file lists only. Foreign untracked `New_Theory/Materiais_Metalicos_EPL_Gb.docx` and `crash_log.txt` — never touch.
- **The canonical `shared` block of `joint_calibrations.json` is NEVER written** — this experiment writes only `conformation_fit.{json,png,md}`. Verify with `git status` after the run.
- Commits in Portuguese, no accents, ending with the trailer `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- **Pre-registered thresholds are frozen (spec §9): `RESOLVE_MAE=0.06`, `PERSIST_MAE=0.10`, others-hold `0.01`, others-degrade `0.02`.** Never tune them to force a verdict.
- **Integrity: test `n=2` only.** Escalation (n=3 → fit `n` → equilibrium driver) is a follow-on the professor decides after seeing the n=2 result — NOT an automatic loop.
- `.json`/`.md`/`.py` are not gitignored; `*.png` is (force-add the plot per the Phase-1 figure precedent).

---

### Task 1: Pure helpers (config builder + pre-registered verdict)

**Files:**
- Create: `New_Theory/conformation_fit.py` (constants + `build_conformation_config` + `classify_conformation_verdict` only in this task).
- Test: `tests/test_conformation_fit.py`.

**Interfaces:**
- Produces: `RESOLVE_MAE=0.06`, `PERSIST_MAE=0.10`, `OTHERS_HOLD=0.01`, `OTHERS_DEGRADE=0.02`; `build_conformation_config(n_cycles=2500) -> SharedCalibrationConfig` (canonical config + conformation constants in `priors`, `W_conf_ref` in `bounds`); `classify_conformation_verdict(base_maes, treat_maes, base_resid, treat_resid) -> dict` with keys `verdict` ("RESOLVED"/"PARTIAL"/"FALSIFIED"), `sobretorque_mae`, `max_others_delta`, `others_deltas`, `resid_ok`.

- [ ] **Step 1: Write the failing tests** — create `tests/test_conformation_fit.py`:

```python
"""Validacao da conformacao (spec 2026-07-04 §9). Helpers puros."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "New_Theory"))
sys.path.insert(0, str(ROOT / "src"))

from conformation_fit import (  # noqa: E402
    RESOLVE_MAE, PERSIST_MAE, build_conformation_config,
    classify_conformation_verdict,
)


def _maes(nova, reusada, sobretorque, reaperto):
    return {"nova": nova, "reusada": reusada,
            "sobretorque": sobretorque, "reaperto": reaperto}


def test_config_has_conformation_constants_fixed_n2():
    cfg = build_conformation_config(n_cycles=300)
    assert cfg.priors["conform_pressure_exp"] == 2.0
    assert cfg.priors["p_ref_conform"] == 5.0e8
    assert cfg.priors["W_conf_ref"] > 0.0
    assert "W_conf_ref" in cfg.bounds          # fitavel
    assert "conform_pressure_exp" not in cfg.bounds   # fixo (nao candidato)


def test_verdict_resolved():
    base = _maes(0.076, 0.059, 0.135, 0.045)
    treat = _maes(0.078, 0.060, 0.030, 0.046)   # sob cai, outros ~iguais
    v = classify_conformation_verdict(base, treat, base_resid=0.3, treat_resid=0.3)
    assert v["verdict"] == "RESOLVED"


def test_verdict_falsified_by_disturbing_others():
    base = _maes(0.076, 0.059, 0.135, 0.045)
    treat = _maes(0.110, 0.060, 0.030, 0.046)   # sob cai MAS nova degrada +0.034
    v = classify_conformation_verdict(base, treat, base_resid=0.3, treat_resid=0.3)
    assert v["verdict"] == "FALSIFIED"


def test_verdict_falsified_by_persistent_sobretorque():
    base = _maes(0.076, 0.059, 0.135, 0.045)
    treat = _maes(0.077, 0.060, 0.125, 0.046)   # sob nao cede (>0.10)
    v = classify_conformation_verdict(base, treat, base_resid=0.3, treat_resid=0.3)
    assert v["verdict"] == "FALSIFIED"


def test_verdict_partial():
    base = _maes(0.076, 0.059, 0.135, 0.045)
    treat = _maes(0.078, 0.060, 0.08, 0.046)    # sob em [0.06,0.10], outros ok
    v = classify_conformation_verdict(base, treat, base_resid=0.3, treat_resid=0.3)
    assert v["verdict"] == "PARTIAL"
```

- [ ] **Step 2: Run to verify failure** — `python -m pytest tests/test_conformation_fit.py -v`. Expected: `ModuleNotFoundError: No module named 'conformation_fit'`.

- [ ] **Step 3: Write the module (constants + helpers only).** Create `New_Theory/conformation_fit.py`:

```python
"""Fase 2 — validacao do mecanismo de conformacao dependente de pressao
(spec 2026-07-04 §9). Testa se a fisica compartilhada COM conformacao ativa
fecha o sobretorque SEM perturbar as demais condicoes.

A/B direto (SharedCalibrator._fit_subset), n=2 fixo, W_conf_ref o unico novo
numero fitado. Artefatos proprios; o bloco `shared` canonico NUNCA e escrito.
Thresholds PRE-REGISTRADOS (spec §9) — nao ajustar para forcar veredicto.

Run:  python New_Theory/conformation_fit.py [--quick]
Runtime: ~2-6 h (duas passadas de fit x 4 condicoes x 2500 ciclos).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

OUT_JSON = ROOT / "New_Theory" / "conformation_fit.json"
OUT_PNG = ROOT / "New_Theory" / "conformation_fit.png"
OUT_MD = ROOT / "New_Theory" / "conformation_fit_report.md"

# Thresholds PRE-REGISTRADOS (spec §9) — congelados.
RESOLVE_MAE = 0.06
PERSIST_MAE = 0.10
OTHERS_HOLD = 0.01
OTHERS_DEGRADE = 0.02
_OTHERS = ("nova", "reusada", "reaperto")


def build_conformation_config(n_cycles: int = 2500):
    """Config compartilhada canonica + constantes de conformacao nos priors
    (n=2 e p_ref fixos; W_conf_ref e o unico novo fitavel)."""
    from calibrate_shared import build_shared_config
    cfg = build_shared_config(n_cycles=n_cycles)
    cfg.priors = dict(cfg.priors, W_conf_ref=1e5,
                      conform_pressure_exp=2.0, p_ref_conform=5.0e8)
    cfg.bounds = dict(cfg.bounds, W_conf_ref=(1e3, 1e8))
    return cfg


def classify_conformation_verdict(base_maes, treat_maes,
                                  base_resid, treat_resid) -> dict:
    """Veredicto pre-registrado (spec §9). AS IS."""
    sob = float(treat_maes["sobretorque"])
    deltas = {c: float(treat_maes[c] - base_maes[c]) for c in _OTHERS}
    max_delta = max(deltas.values())
    resid_ok = abs(treat_resid) <= abs(base_resid) + 1.0
    if sob < RESOLVE_MAE and max_delta < OTHERS_HOLD and resid_ok:
        verdict = "RESOLVED"
    elif sob > PERSIST_MAE or max_delta > OTHERS_DEGRADE:
        verdict = "FALSIFIED"
    else:
        verdict = "PARTIAL"
    return dict(verdict=verdict, sobretorque_mae=sob,
                max_others_delta=max_delta, others_deltas=deltas,
                resid_ok=resid_ok)
```

- [ ] **Step 4: Run to verify pass** — `python -m pytest tests/test_conformation_fit.py -v`. Expected: 5 passed. (The heavy `calibrate_shared` import is lazy inside `build_conformation_config`, so `test_verdict_*` don't pay it; `test_config_*` does.)

- [ ] **Step 5: Syntax-check and commit.**
```bash
python -c "import ast; ast.parse(open('New_Theory/conformation_fit.py', encoding='utf-8').read()); print('OK')"
git add New_Theory/conformation_fit.py tests/test_conformation_fit.py
git commit -m "fase2: helpers da validacao de conformacao (config A/B + veredicto pre-registrado)" -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: A/B orchestration + smoke

**Files:**
- Modify: `New_Theory/conformation_fit.py` (append `run_ab`, `_sobretorque_residual`, `main`).

**Interfaces:**
- Consumes: `SharedCalibrator`, `build_shared_config` (baseline), `build_conformation_config` (treatment), `DynamicStiffnessAnalyzer`.
- Produces: `run_ab(n_cycles) -> (cal_b, base_maes, cal_t, treat_maes)`; `_sobretorque_residual(cal, n_cycles) -> float`; `main()` writing the three artifacts.

- [ ] **Step 1: Append the orchestration.**

```python
def run_ab(n_cycles: int):
    """Baseline {C_creep} (conformacao off) vs treatment {C_creep, W_conf_ref}
    (conformacao ativa, n=2 fixo). Mesmo setup de F0 (bound 120 kN) nos dois."""
    from bolt_analysis_studio.calibration.shared_calibrator import SharedCalibrator
    from calibrate_shared import build_shared_config
    cal_b = SharedCalibrator(build_shared_config(n_cycles=n_cycles))
    cal_b._fit_subset(["C_creep"])
    base_maes = cal_b.mae_by_condition()
    cal_t = SharedCalibrator(build_conformation_config(n_cycles=n_cycles))
    cal_t._fit_subset(["C_creep", "W_conf_ref"])
    treat_maes = cal_t.mae_by_condition()
    return cal_b, base_maes, cal_t, treat_maes


def _sobretorque_residual(cal, n_cycles: int) -> float:
    """Residual de conservacao rodando o sobretorque com as constantes de
    `cal` (mesmo setup de _run_condition, mas expondo energy)."""
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer)
    cond = next(c for c in cal.cfg.conditions if c.name == "sobretorque")
    ana = DynamicStiffnessAnalyzer(
        cal.cfg.geom, cal._material(cond), cal._F0(cond),
        initial_damage=cond.D_init, initial_embedding_frac=cond.emb_consumed_frac)
    for _ in range(n_cycles):
        ana.step_cycle(cond.F_amp, cal.cfg.theta, cal.cfg.freq,
                       delta_amp=cond.delta_amp)
    return float(ana.energy.conservation_residual)


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    quick = "--quick" in sys.argv
    n_cycles = 300 if quick else 2500

    cal_b, base_maes, cal_t, treat_maes = run_ab(n_cycles)
    base_resid = _sobretorque_residual(cal_b, n_cycles)
    treat_resid = _sobretorque_residual(cal_t, n_cycles)
    verdict = classify_conformation_verdict(base_maes, treat_maes,
                                            base_resid, treat_resid)
    W_conf_ref_fit = float(cal_t.constants["W_conf_ref"])

    print("== conformacao A/B (n=2 fixo; W_conf_ref o unico novo fitado) ==")
    for c in ("nova", "reusada", "sobretorque", "reaperto"):
        print(f"  {c:12s} base {base_maes[c]:.4f} -> treat {treat_maes[c]:.4f}"
              f"  (d {treat_maes[c]-base_maes[c]:+.4f})")
    print(f"  W_conf_ref fitado = {W_conf_ref_fit:.4g}")
    print(f"  residual sobretorque: base {base_resid:.3e} -> treat {treat_resid:.3e}")
    print(f"  VEREDICTO (pre-registrado): {verdict['verdict']}")

    # plot: sobretorque data + baseline sim + treatment sim
    sob_b = next(c for c in cal_b.cfg.conditions if c.name == "sobretorque")
    nb, rb = cal_b._run_condition(sob_b)
    sob_t = next(c for c in cal_t.cfg.conditions if c.name == "sobretorque")
    nt, rt = cal_t._run_condition(sob_t)
    fig, ax = plt.subplots(figsize=(8, 5))
    for cv in sob_b.curves:
        ax.plot(cv["cycles"], cv["ratio"], "o", ms=4, color="#00B050",
                alpha=0.8, label=cv["name"])
    ax.plot(nb, rb, "r--", lw=2, label=f"baseline (MAE {base_maes['sobretorque']:.3f})")
    ax.plot(nt, rt, "k-", lw=2.5,
            label=f"conformacao (MAE {treat_maes['sobretorque']:.3f})")
    ax.set_title(f"sobretorque A/B — veredicto {verdict['verdict']}", fontsize=9)
    ax.set_xlabel("Ciclos N"); ax.set_ylabel(r"$F_0/F_{0,init}$")
    ax.set_xlim(0, n_cycles); ax.set_ylim(0, 1.05); ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()

    if quick:
        fig.savefig(OUT_PNG, dpi=110)
        print("--quick: smoke (NAO cientifico); png gerado, sem JSON/report.")
        return
    fig.savefig(OUT_PNG, dpi=120)

    out = dict(
        campaign="Fase 2 — validacao da conformacao (spec 2026-07-04 §9)",
        method="A/B direto _fit_subset; n=2 fixo; W_conf_ref unico novo fitado",
        thresholds=dict(RESOLVE_MAE=RESOLVE_MAE, PERSIST_MAE=PERSIST_MAE,
                        OTHERS_HOLD=OTHERS_HOLD, OTHERS_DEGRADE=OTHERS_DEGRADE),
        baseline=dict(mae_by_condition=base_maes,
                      C_creep=float(cal_b.constants["C_creep"]),
                      sobretorque_residual=base_resid),
        treatment=dict(mae_by_condition=treat_maes,
                       C_creep=float(cal_t.constants["C_creep"]),
                       W_conf_ref=W_conf_ref_fit,
                       conform_pressure_exp=2.0, p_ref_conform=5.0e8,
                       sobretorque_residual=treat_resid),
        verdict=verdict,
        canonical_shared_block="NAO escrito (experimento)")
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    lines = ["# Validacao da conformacao — A/B (Fase 2)", "",
             f"**Veredicto (pre-registrado): {verdict['verdict']}**", "",
             "| Condicao | baseline | conformacao | delta |", "|---|---:|---:|---:|"]
    lines += [f"| {c} | {base_maes[c]:.4f} | {treat_maes[c]:.4f} | "
              f"{treat_maes[c]-base_maes[c]:+.4f} |"
              for c in ("nova", "reusada", "sobretorque", "reaperto")]
    lines += ["", f"W_conf_ref fitado = {W_conf_ref_fit:.4g} (n=2 fixo). "
              f"Residual sobretorque {base_resid:.3e} -> {treat_resid:.3e}."]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Artefatos: {OUT_JSON.name}, {OUT_PNG.name}, {OUT_MD.name}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Syntax-check** — `python -c "import ast; ast.parse(open('New_Theory/conformation_fit.py', encoding='utf-8').read()); print('OK')"`.

- [ ] **Step 3: Re-run helper tests** — `python -m pytest tests/test_conformation_fit.py -v` → 5 passed (module still imports light; `SharedCalibrator` import is lazy inside `run_ab`).

- [ ] **Step 4: Smoke** — `python New_Theory/conformation_fit.py --quick` → prints the A/B table + a `VEREDICTO:` line, writes only the PNG, prints the `--quick` notice; **no JSON/report**. Then `git status --porcelain New_Theory/joint_calibrations.json` must be empty (canonical block untouched). Values are meaningless at n=300 — path check only.

- [ ] **Step 5: Remove the smoke PNG and commit the `.py`.**
```bash
rm -f New_Theory/conformation_fit.png
python -c "import ast; ast.parse(open('New_Theory/conformation_fit.py', encoding='utf-8').read()); print('OK')"
git add New_Theory/conformation_fit.py
git commit -m "fase2: orquestracao A/B da validacao de conformacao + smoke --quick" -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Real A/B run — record the verdict AS IS

**Files:** Produce (committed): `New_Theory/conformation_fit.{json,png,md}`.

- [ ] **Step 1: Canary** — confirm the canonical `shared` block is intact before the run: `python -c "import json,hashlib; d=json.load(open('New_Theory/joint_calibrations.json',encoding='utf-8')); print(hashlib.sha256(json.dumps(d.get('shared'),sort_keys=True).encode()).hexdigest()[:16])"`. Record the hash.

- [ ] **Step 2: Run (background, ~2–6 h)** — `MPLBACKEND=Agg python New_Theory/conformation_fit.py`. Record the printed A/B table + verdict **exactly** — do not re-run to change it (n=2 is the pre-registered test).

- [ ] **Step 3: Verify canonical block untouched** — re-run the Step-1 hash (must match) and `git status --porcelain New_Theory/joint_calibrations.json` (must be empty). If either fails, the experiment wrote the canonical block — bug; restore from git and fix.

- [ ] **Step 4: Commit the artifacts** (force-add the PNG, `*.png` is gitignored).
```bash
git add -f New_Theory/conformation_fit.png
git add New_Theory/conformation_fit.json New_Theory/conformation_fit_report.md
git commit -m "fase2: resultado da validacao de conformacao (A/B, n=2, AS IS)" -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: MODEL_LEGITIMACY §4.9 addendum (Fable)

**Files:** Modify `New_Theory/MODEL_LEGITIMACY.md` (new §4.9).

> Dispatch on **Fable** (falsification-logic + scientific writing). The reviewer (Fable, or Opus-max fallback) must **recompute** the verdict from `conformation_fit.json` and confirm it matches the addendum.

- [ ] **Step 1** Read `New_Theory/conformation_fit.json` and recompute the verdict from its numbers (RESOLVE_MAE/PERSIST_MAE/others thresholds).
- [ ] **Step 2** Write §4.9: the A/B method (n=2 fixed, one new fitted number `W_conf_ref`), the per-condition MAE deltas (both arms), the fitted `W_conf_ref`, the conservation residual, and the pre-registered verdict. Interpretation per outcome:
  - **RESOLVED** → the pressure-conformation form resolves the sobretorque falsification with one shared, pressure-gated number; state it plainly, link the mechanism (Plan A) and this validation; note it's a standalone experiment (canonical block unchanged) pending the professor's adoption decision (like Stage B).
  - **PARTIAL/FALSIFIED** → record AS IS; state precisely how (sobretorque didn't cede / others disturbed) and that the documented follow-on (n=3 → fit `n` → equilibrium driver, spec §7) is the professor's next-hypothesis decision. Do NOT tune to pass.
  - Cross-link the F0-bound experiment (§4.5) — this closes that thread's "missing mechanism" verdict either way.
- [ ] **Step 3** Add a 2026-07-04 changelog line. Commit `MODEL_LEGITIMACY.md` only.

---

## Self-Review (controller, after all tasks)

- **Method fidelity:** direct A/B, n=2 fixed, one new fitted number `W_conf_ref`, canonical config in both arms (spec §9). ✅
- **Canonical block untouched:** T3 Steps 1+3 enforce (hash + git status). ✅
- **Pre-registration / AS IS:** thresholds frozen in T1; T3 forbids re-running for a different verdict; escalation is a follow-on, not a loop. ✅
- **Type consistency:** `classify_conformation_verdict` / `build_conformation_config` / `run_ab` signatures match across module, tests, and `main`. `cal._material`/`cal._F0`/`cal._run_condition`/`cal.mae_by_condition` are the real `SharedCalibrator` internals (verified against source). ✅
- **Fable swaps:** T4 + final review, with Opus-max fallback + recompute-from-JSON guard. ✅

## Final review

Dispatch on **Fable** (scientific conclusion). It recomputes the verdict from `conformation_fit.json`, checks the A/B isolates conformation (same F0 setup both arms), confirms canonical block untouched, and adjudicates the §4.9 interpretation is calibrated (no overclaim on RESOLVED; honest on PARTIAL/FALSIFIED).
