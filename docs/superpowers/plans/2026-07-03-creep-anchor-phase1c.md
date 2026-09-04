# Library Confrontation Phase 1 — Plan 2 of 3: C_creep Anchor (sub-campaign C) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Estimate `C_creep` from the li2022marstruc STATIC-creep dataset (no vibration — the mechanism isolated), report its CI, and re-run the Stage-A shared fit with the prior re-centered on the anchor — measuring the impact honestly (spec §1.7).

**Architecture:** New script `New_Theory/anchor_creep.py` (uses `library_common`): static mode = pseudo-cycles of 1 minute (freq=1/60 Hz, F_amp=0) so only embedding+creep act (registry-truth verified in tests); joint fit of {C_creep shared + emb_depth per Ra level} over the 6 curves in log-space; linearized CI; then Stage-A re-run via `calibrate_shared.build_shared_config` with priors/bounds overridden. Cross-material honesty: 304SS ≠ âncora interna pair — the anchor re-centers the prior, never replaces by decree.

**Tech Stack:** Python 3, numpy, scipy.optimize.least_squares, matplotlib (Agg), pytest. No engine changes.

## Global Constraints

- Branch `library-confrontation-c` from `main` (post-`87fc4a3`); merge-commit back when finished.
- utf-8 I/O; `ast.parse` after every .py edit; commits PT-without-accents + trailer `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- **This is a declared MEASUREMENT (not zero-refit):** free parameters are exactly {C_creep, emb_depth×4 Ra levels} = 5, fitted to the 6 static curves. Everything else frozen: `frozen_constants()` for N_emb/K_archard/tr_loose_gain (K_archard/tr_loose_gain provably inert at F_amp=0 — tested), geometry from the apparatus note (M16×80 **304SS E=193 GPa**, grip L=20 mm — both `paper` provenance, no gaps).
- Pre-registered: alignment = normalize data AND sim at the first data point (curves start 96.7–100.4% post-tightening); x-axis is MINUTES (1 pseudo-cycle = 1 min, freq=1/60 Hz); no trims (600-min runs, no fatigue).
- The 6 curves: 10 kN × Ra {0.078, 0.122, 0.306, 0.8} + {5, 15} kN × Ra 0.8 (the 5/15 kN curves SHARE Ra0.8's emb_depth — they test the creep law's F₀-form).
- Known model-form issue to REPORT (not fix): the engine's fractional creep loss `k_b·C·Δln(t)` is F₀-invariant, while the data is non-monotonic in F₀ (10 kN loses 5.85%, 5 kN 2.6%, 15 kN 1.85%; digitization cloud ±2%). Whatever the residuals show goes in the write-up AS IS.
- Stage-A re-run: `priors["C_creep"] = anchor`, `bounds["C_creep"] = (anchor/f², anchor·f²)` with `f` = the anchor's CI factor, clipped to [1e-13, 1e-9]; `fit_parsimonious(tol=0.005, max_constants=4)`; compare against the committed shared block (C_creep 1.165e-11, MAE global 0.0796) — before/after table.
- Results AS IS; stage only named files; scratch (.superpowers/, crash_log.txt, *.docx) untouched.
- Timing: static sims are 600 cycles → anchor fit runs in seconds; Stage-A re-run ≈ 6 min (background Bash, tee'd log).

## File Structure

| File | Responsibility |
|---|---|
| `New_Theory/anchor_creep.py` (create) | static-mode runner, 5-param anchor fit + CI, Stage-A prior re-run, artifacts |
| `tests/test_anchor_creep.py` (create) | static-regime registry-truth + synthetic recovery |
| `New_Theory/creep_anchor.json`, `creep_anchor.png`, `creep_anchor_report.md` (generated) | committed artifacts |
| `New_Theory/MODEL_LEGITIMACY.md`, `CLAUDE.md` (Task 2) | §4.7 + §5.1 procedência do C_creep + changelog; command |

---

### Task 1: `anchor_creep.py` + tests + science runs

**Files:**
- Create: `New_Theory/anchor_creep.py`
- Test: `tests/test_anchor_creep.py` (create)
- Generated (committed): `New_Theory/creep_anchor.json`, `New_Theory/creep_anchor.png` (force-add), `New_Theory/creep_anchor_report.md`

**Interfaces:**
- Consumes: `library_common.frozen_constants()/geometry_for()/load_full_curve()/Provenance`; `calibrate_shared.build_shared_config(n_cycles=2500)`; `SharedCalibrator`.
- Produces: importable functions `simulate_static(F0_N, C_creep, emb_depth_m, n_min, K_archard=1e-4)` → np.ndarray ratio (len n_min+1) and `fit_anchor(curves)` → dict (tests import them); the JSON schema Task 2 transcribes.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_anchor_creep.py`:

```python
"""Ancora de C_creep (creep estatico, sub-campanha C) — spec 2026-07-03 §1.7."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "New_Theory"))

from anchor_creep import fit_anchor, simulate_static  # noqa: E402


def test_registry_truth_wear_inert_in_static_mode():
    # F_amp=0: sem slip transversal => K_archard estruturalmente nao-lido
    # (mesma doutrina registry-truth, estendida ao regime estatico).
    a = simulate_static(10e3, C_creep=3e-11, emb_depth_m=2e-6, n_min=300,
                        K_archard=1e-4)
    b = simulate_static(10e3, C_creep=3e-11, emb_depth_m=2e-6, n_min=300,
                        K_archard=2e-4)
    assert np.array_equal(a, b)


def test_static_mode_loses_preload_via_embedding_and_creep():
    r = simulate_static(10e3, C_creep=3e-11, emb_depth_m=2e-6, n_min=600)
    assert r[0] == 1.0 and r[-1] < 0.999      # perde algo
    assert r[-1] > 0.5                         # mas nao colapsa
    # monotonico nao-crescente
    assert np.all(np.diff(r) <= 1e-12)


def test_fit_anchor_recovers_synthetic_C_creep():
    # Gera 3 curvas estaticas com C conhecido + ruido e recupera C (rel 25%).
    rng = np.random.default_rng(7)
    C_true, embs = 3e-11, {0.8: 3e-6, 0.122: 1e-6}
    curves = []
    for F0, ra in [(10e3, 0.8), (5e3, 0.8), (10e3, 0.122)]:
        r = simulate_static(F0, C_true, embs[ra], n_min=600)
        mins = np.linspace(1, 600, 12)
        vals = np.interp(mins, np.arange(601), r) + rng.normal(0, 0.003, 12)
        curves.append(dict(name=f"syn_{F0:.0f}_{ra}", F0_N=F0, Ra_um=ra,
                           minutes=mins, ratio=vals))
    res = fit_anchor(curves)
    assert res["C_creep_anchor"] == pytest.approx(C_true, rel=0.25)
    assert res["ci_factor"] >= 1.0
    assert set(res["emb_depth_um_by_Ra"]) == {"0.8", "0.122"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_anchor_creep.py -q`
Expected: FAIL at collection with `ModuleNotFoundError: No module named 'anchor_creep'`.

- [ ] **Step 3: Write the script**

Create `New_Theory/anchor_creep.py`:

```python
"""Sub-campanha C — ancora independente de C_creep (spec 2026-07-03 §1.7).

Creep ESTATICO li2022marstruc (M16 304SS, sem vibracao, eixo x em MINUTOS):
isola o mecanismo de creep. Fit declarado de {C_creep + emb_depth por Ra}
(5 parametros, 6 curvas); depois re-roda o Estagio A com o prior de C_creep
re-centrado na ancora (cross-material: 304SS != par da âncora interna — re-centra, nao
substitui por decreto).

Run:  python New_Theory/anchor_creep.py [--skip-stage-a]
Runtime: ancora ~segundos; re-run do Estagio A ~6 min.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial,
)
from library_common import (  # noqa: E402
    Provenance, frozen_constants, geometry_for, load_full_curve,
)

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"

# Aparato (nota li2022_marstruc_contact_creep.md — proveniencia 'paper'):
# M16x80 304SS E=193 GPa, grip L=20 mm, contato 60x60. Curvas comecam no
# primeiro registro pos-aperto (96.7-100.4%) -> alinhamento no 1o ponto.
GEOM = geometry_for("M16x2.0", grip_mm=20.0, E=193e9)
FREQ_STATIC = 1.0 / 60.0          # 1 pseudo-ciclo = 1 minuto

CURVES_DEF = [
    # csv, F0 [N], Ra [um]
    (f"{DIG}/li2022marstruc_creep_10kN_Ra0p078_min.csv", 10e3, 0.078),
    (f"{DIG}/li2022marstruc_creep_10kN_Ra0p122_min.csv", 10e3, 0.122),
    (f"{DIG}/li2022marstruc_creep_10kN_Ra0p306_min.csv", 10e3, 0.306),
    (f"{DIG}/li2022marstruc_creep_10kN_Ra0p8_min.csv",   10e3, 0.8),
    (f"{DIG}/li2022marstruc_creep_5kN_Ra0p8_min.csv",     5e3, 0.8),
    (f"{DIG}/li2022marstruc_creep_15kN_Ra0p8_min.csv",   15e3, 0.8),
]
BOUNDS_C = (1e-13, 1e-9)
BOUNDS_EMB = (1e-8, 20e-6)


def simulate_static(F0_N, C_creep, emb_depth_m, n_min, K_archard=1e-4):
    """Modo estatico: F_amp=0 (sem slip => wear/loosening inertes),
    freq=1/60 Hz => t = N minutos. Retorna ratio[0..n_min]."""
    consts, _ = frozen_constants()
    consts = dict(consts, C_creep=C_creep, K_archard=K_archard)
    mat = JointMaterial(emb_depth=emb_depth_m, **consts)
    ana = DynamicStiffnessAnalyzer(GEOM, mat, F0_N)
    out = np.empty(n_min + 1)
    out[0] = 1.0
    for n in range(1, n_min + 1):
        ana.step_cycle(0.0, 0.0, FREQ_STATIC)
        out[n] = max(ana.state.F_0, 0.0) / F0_N
    return out


def _load_curves():
    out = []
    for csv, F0, ra in CURVES_DEF:
        mins, ratio = load_full_curve(csv)
        out.append(dict(name=Path(csv).stem, F0_N=F0, Ra_um=ra,
                        minutes=mins, ratio=ratio))
    return out


def fit_anchor(curves):
    """Fit conjunto log-espaco: x = [ln C, ln emb_Ra...] (Ra em ordem de
    aparicao). Retorna ancora + CI linearizado + MAE por curva."""
    ra_levels = []
    for c in curves:
        if c["Ra_um"] not in ra_levels:
            ra_levels.append(c["Ra_um"])

    def unpack(x):
        C = float(np.exp(x[0]))
        embs = {ra: float(np.exp(v)) for ra, v in zip(ra_levels, x[1:])}
        return C, embs

    def resid(x):
        C, embs = unpack(x)
        out = []
        for c in curves:
            n_max = int(c["minutes"][-1])
            sim = simulate_static(c["F0_N"], C, embs[c["Ra_um"]], n_max)
            m0 = c["minutes"][0]
            data_al = c["ratio"] / c["ratio"][0]
            sim_al = sim / max(np.interp(m0, np.arange(n_max + 1), sim), 1e-9)
            pred = np.interp(c["minutes"], np.arange(n_max + 1), sim_al)
            out.extend((pred - data_al) / np.sqrt(len(data_al)))
        return np.array(out)

    x0 = [np.log(5e-11)] + [np.log(2e-6)] * len(ra_levels)
    lo = [np.log(BOUNDS_C[0])] + [np.log(BOUNDS_EMB[0])] * len(ra_levels)
    hi = [np.log(BOUNDS_C[1])] + [np.log(BOUNDS_EMB[1])] * len(ra_levels)
    res = least_squares(resid, x0, bounds=(lo, hi), method="trf",
                        xtol=1e-10, ftol=1e-10, diff_step=1e-3, max_nfev=200)
    C, embs = unpack(res.x)
    # CI linearizado (log-espaco): cov = sigma^2 (JtJ)^-1
    r0 = resid(res.x)
    J = np.zeros((len(r0), len(res.x)))
    for i in range(len(res.x)):
        xp, xm = res.x.copy(), res.x.copy()
        xp[i] += 0.02
        xm[i] -= 0.02
        J[:, i] = (resid(xp) - resid(xm)) / 0.04
    sigma2 = float(np.sum(r0 ** 2)) / max(len(r0) - len(res.x), 1)
    try:
        ci = float(np.exp(1.96 * np.sqrt(
            max((sigma2 * np.linalg.inv(J.T @ J))[0, 0], 0.0))))
    except np.linalg.LinAlgError:
        ci = float("inf")
    # MAE por curva no otimo
    maes = {}
    for c in curves:
        n_max = int(c["minutes"][-1])
        sim = simulate_static(c["F0_N"], C, embs[c["Ra_um"]], n_max)
        m0 = c["minutes"][0]
        data_al = c["ratio"] / c["ratio"][0]
        sim_al = sim / max(np.interp(m0, np.arange(n_max + 1), sim), 1e-9)
        maes[c["name"]] = float(np.mean(np.abs(
            np.interp(c["minutes"], np.arange(n_max + 1), sim_al) - data_al)))
    return dict(C_creep_anchor=C, ci_factor=ci,
                emb_depth_um_by_Ra={str(ra): embs[ra] * 1e6 for ra in ra_levels},
                mae_by_curve=maes, n_params=len(res.x), n_points=len(r0))


def rerun_stage_a(anchor, ci_factor):
    """Re-roda o Estagio A com prior de C_creep re-centrado (spec §1.7)."""
    from calibrate_shared import build_shared_config
    from bolt_analysis_studio.calibration.shared_calibrator import SharedCalibrator
    cfg = build_shared_config(n_cycles=2500)
    f2 = min(max(ci_factor, 1.5), 10.0) ** 2
    lo = max(anchor / f2, 1e-13)
    hi = min(anchor * f2, 1e-9)
    cfg.priors["C_creep"] = anchor
    cfg.bounds["C_creep"] = (lo, hi)
    res = SharedCalibrator(cfg).fit_parsimonious(tol=0.005, max_constants=4)
    return dict(prior=anchor, bounds=[lo, hi],
                free_constants=res["free_constants"],
                C_creep_fitted=res["constants"]["C_creep"],
                mae_global=res["mae_global"],
                mae_by_condition=res["mae_by_condition"],
                F0_estimates=res["F0_estimates"])


def main():
    curves = _load_curves()
    anchor = fit_anchor(curves)
    print("== ancora de C_creep (li2022marstruc, estatico) ==")
    print(f"C_creep = {anchor['C_creep_anchor']:.4g}  x/ {anchor['ci_factor']:.2f}"
          f"  (Estagio A: 1.165e-11, IC x/2.30)")
    for ra, e in anchor["emb_depth_um_by_Ra"].items():
        print(f"  emb_depth(Ra={ra}) = {e:.3f} um")
    for n, m in anchor["mae_by_curve"].items():
        print(f"  MAE {n} = {m:.4f}")

    # conservacao no modo estatico (spec §5): so emb+creep ativos => ~0
    C, embs = anchor["C_creep_anchor"], anchor["emb_depth_um_by_Ra"]
    consts0, _ = frozen_constants()
    mat0 = JointMaterial(emb_depth=embs["0.8"] * 1e-6,
                         **dict(consts0, C_creep=C))
    ana0 = DynamicStiffnessAnalyzer(GEOM, mat0, 10e3)
    for _ in range(600):
        ana0.step_cycle(0.0, 0.0, FREQ_STATIC)
    resid_static = float(ana0.energy.conservation_residual)
    print(f"residual de conservacao (estatico, 10kN, 600 min): {resid_static:.3e}")

    # plot 2x3
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, c in zip(axes.flat, curves):
        n_max = int(c["minutes"][-1])
        sim = simulate_static(c["F0_N"], C, embs[str(c["Ra_um"])] * 1e-6, n_max)
        m0 = c["minutes"][0]
        data_al = c["ratio"] / c["ratio"][0]
        sim_al = sim / max(np.interp(m0, np.arange(n_max + 1), sim), 1e-9)
        ax.plot(c["minutes"], data_al, "o-", ms=3, label="dado")
        ax.plot(np.arange(n_max + 1), sim_al, "k-",
                label=f"fit (MAE={anchor['mae_by_curve'][c['name']]:.3f})")
        ax.set_title(f"F0={c['F0_N']/1e3:g}kN Ra={c['Ra_um']}", fontsize=9)
        ax.set_xlabel("min")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
    plt.tight_layout()
    fig.savefig(ROOT / "New_Theory" / "creep_anchor.png", dpi=110)

    stage_a = None
    if "--skip-stage-a" not in sys.argv:
        print("\n== re-run do Estagio A com prior re-centrado (~6 min) ==")
        stage_a = rerun_stage_a(anchor["C_creep_anchor"], anchor["ci_factor"])
        print(f"antes: C_creep=1.165e-11, MAE global 0.0796")
        print(f"depois: C_creep={stage_a['C_creep_fitted']:.4g}, "
              f"MAE global {stage_a['mae_global']:.4f}, "
              f"livres={stage_a['free_constants']}")

    out = dict(campaign="C anchor (spec 2026-07-03 §1.7)",
               provenance=dict(
                   geometry="paper (li2022_marstruc: M16x80 304SS E=193GPa, L=20mm)",
                   x_axis="minutos (1 pseudo-ciclo = 1 min, freq=1/60 Hz)",
                   cross_material="304SS != par da âncora interna: ancora re-centra o prior"),
               conservation_residual_static=resid_static,
               anchor=anchor, stage_a_rerun=stage_a)
    (ROOT / "New_Theory" / "creep_anchor.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# Ancora de C_creep — creep estatico (spec 2026-07-03 §1.7)", "",
             f"C_creep = {anchor['C_creep_anchor']:.4g} x/ {anchor['ci_factor']:.2f} "
             f"(Estagio A: 1.165e-11 x/2.30)", "",
             "| Curva | MAE |", "|---|---:|"]
    lines += [f"| {n} | {m:.4f} |" for n, m in anchor["mae_by_curve"].items()]
    if stage_a:
        lines += ["", f"Re-run Estagio A: C_creep {stage_a['C_creep_fitted']:.4g}, "
                  f"MAE global {stage_a['mae_global']:.4f} (antes 0.0796), "
                  f"livres {stage_a['free_constants']}"]
    (ROOT / "New_Theory" / "creep_anchor_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("Artefatos: creep_anchor.json, creep_anchor.png, creep_anchor_report.md")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Syntax check + run tests**

Run: `python -c "import ast; ast.parse(open('New_Theory/anchor_creep.py', encoding='utf-8').read()); print('OK')"`
Run: `python -m pytest tests/test_anchor_creep.py -v`
Expected: 3 PASS (~1–2 min; the synthetic-recovery fit runs dozens of 600-cycle sims).

- [ ] **Step 5: Science run (background, tee to `.superpowers/sdd/creep-anchor.log`, ~7 min total)**

Run: `python New_Theory/anchor_creep.py 2>&1 | tee .superpowers/sdd/creep-anchor.log`
Sanity: anchor value printed with CI; 6 MAEs finite; emb_depth(Ra) values printed (check monotonic with Ra — report if not, don't fix); conservation residual (static) ≈ 0; Stage-A re-run block prints before/after; 3 artifacts written. Record results AS IS — including if the anchor lands far from 1.165e-11 or if the Stage-A MAE worsens (both are findings about transferability of C_creep across tribo-pairs).

- [ ] **Step 6: Commit**

```bash
git add New_Theory/anchor_creep.py tests/test_anchor_creep.py New_Theory/creep_anchor.json New_Theory/creep_anchor_report.md
git add -f New_Theory/creep_anchor.png
git commit -m "calib: ancora independente de C_creep (creep estatico li2022marstruc)

Fit declarado {C_creep + emb_depth por Ra} nas 6 curvas estaticas
(minutos, 304SS E=193GPa, L=20mm, proveniencia paper); CI linearizado;
re-run do Estagio A com prior re-centrado. Registry-truth do regime
estatico (wear inerte com F_amp=0) testado. Resultados AS IS.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: docs — anchor verdict

**Files:**
- Modify: `New_Theory/MODEL_LEGITIMACY.md` (§4.7 after §4.6; §5.1 provenance row for C_creep; §9 changelog)
- Modify: `CLAUDE.md` (command line)

**Interfaces:**
- Consumes: `New_Theory/creep_anchor.json` + `creep_anchor_report.md`.

- [ ] **Step 1: MODEL_LEGITIMACY §4.7**

Insert after §4.6 (Portuguese WITH accents; every `<...>` transcribed from creep_anchor.json):

```markdown
### 4.7 Âncora independente de C_creep — creep estático (Fase 1C, spec §1.7)

Fit **declarado** (medição, não zero-refit) de {C_creep + emb_depth por nível
de Ra} nas 6 curvas de relaxação estática do li2022marstruc (M16 304SS,
E=193 GPa, L=20 mm — procedência `paper`; eixo x em minutos; sem vibração ⇒
wear/loosening estruturalmente inertes, verificado por registry-truth).

| Métrica | Valor |
|---|---|
| C_creep (âncora) | <...> ×/÷ <...> |
| C_creep (Estágio A, referência) | 1,165e-11 ×/÷ 2,30 |
| emb_depth(Ra 0,078/0,122/0,306/0,8) | <...> µm |
| MAE por curva | <faixa> |
| Re-run Estágio A (prior re-centrado) | C_creep <...>, MAE global <...> (antes 0,0796) |

<2-4 frases honestas: a âncora concorda/discorda do valor do Estágio A e o
que isso diz sobre transferibilidade entre pares tribológicos (304SS vs aço
âncora interna); emb_depth cresce com Ra? (esperado fisicamente); a invariância-F₀ da
fração de creep do modelo vs a não-monotonicidade do dado (±2% de nuvem) —
achado de forma se os resíduos a mostrarem.>
```

- [ ] **Step 2: §5.1 provenance + changelog + CLAUDE.md**

In §5.1's provenance table, update the `C_creep` row's "Procedência HOJE" to: "âncora de dado independente (creep estático li2022marstruc, §4.7) re-centrando o prior — antes: default ajustado historicamente à curva". Append changelog row:

```markdown
| 2026-07-03 | §4.7 âncora de C_creep (Fase 1C): fit declarado no creep estático li2022marstruc (mecanismo isolado, sem vibração); prior do Estágio A re-centrado no valor ancorado (<valor>); §5.1 atualizada — C_creep é a primeira constante com procedência de dado independente. |
```

CLAUDE.md commands block: add `python New_Theory/anchor_creep.py   # ancora de C_creep (estatico, ~7 min; --skip-stage-a p/ so a ancora)`.

- [ ] **Step 3: Regression + commit**

Run: `python -m pytest tests/test_anchor_creep.py tests/test_library_common.py tests/test_shared_calibrator.py -q`
Expected: ~15 passed.

```bash
git add New_Theory/MODEL_LEGITIMACY.md CLAUDE.md
git commit -m "docs: ancora de C_creep (§4.7) + procedencia de dado independente (§5.1)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Report the anchor verdict; Plan 3 (transferência transversal A) follows.
