# Conformation Equilibrium (Self-Limiting) Driver — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline, the professor's established preference this session) to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax. An Opus final review of the complete engine+config diff runs before merge (engine-change discipline, per Plan A).

**Goal:** Add the effective-slip (self-limiting) conformation driver as a selectable mode, and validate AS IS whether it resolves sobretorque at a fixed moderate `n` *and* relaxes the sharp-`n` rail that strand 1 (fit-n) exposed in the raw driver.

**Architecture:** A new `conform_driver ∈ {"raw","effective"}` mode on `JointMaterial`. The raw driver (default, current behavior) accumulates `W_conf` from the pressure-weighted raw slip work monotonically. The effective driver weights each increment by the start-of-cycle conformation gate `g_conf`, so the driver self-attenuates as the joint conforms (and further as `F_0` drops, `∝F_0^{n+1}`). This is the localized change spec §7 authorized. It is a **self-limiting plateau, not a true equilibrium `c*<1`** (asymptotically `c→1` under creep); a genuine fixed point would need slip-kinematic feedback (deferred, entangles with roadmap item #4). Validation is a pre-registered A/B (raw vs effective) reusing the frozen §9 thresholds, plus a fit-n re-run on the effective driver.

**Tech Stack:** Python, `DynamicStiffnessAnalyzer`, `SharedCalibrator`, pytest.

## Global Constraints

- All file I/O `encoding='utf-8'`. `python -c "import ast; ast.parse(open('PATH',encoding='utf-8').read())"` after every `.py` edit.
- **Never `git add -A`** — stage explicit file lists only. **Never** touch/stage `New_Theory/Materiais_Metalicos_EPL_Gb.docx` or `crash_log.txt` (the professor's untracked WIP).
- Commit messages: Portuguese, **no accents**, ending with the trailer `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- The canonical `shared` block of `New_Theory/joint_calibrations.json` is **NEVER written** by this work (hash `21ed6a7ad94114d0` must stay intact). Experiment artifacts are standalone JSON/MD.
- Frozen pre-registered thresholds (spec §9): RESOLVE 0.06, PERSIST 0.10, others-hold 0.01, others-degrade 0.02 — **not adjustable to force a verdict**. Record AS IS.
- **Backward-compat is a hard gate:** `conform_driver` default `"raw"` ⇒ every existing engine run and calibration is **bit-identical** to today. The `W_conf_ref=0` sentinel (`conformation_gate≡1`, `W_conf` stays 0) is also preserved.
- The effective driver is a **standalone experiment**; adopting it (or the raw driver) into the canonical `shared` block is a **separate decision for the professor**.

---

### Task 1: Engine — `conform_driver` field + effective-slip branch

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (`JointMaterial` ~line 180; `step_cycle` §4.7 block, lines 910–915)
- Test: `tests/test_pressure_conformation.py`

**Interfaces:**
- Consumes: existing `conformation_gate(state, mat)` (line 335), `SlowState.W_conf` (line 201), `JointMaterial.{W_conf_ref, conform_pressure_exp, p_ref_conform}`.
- Produces: `JointMaterial.conform_driver: str = "raw"`. Effective branch: when `conform_driver == "effective"`, the per-cycle `W_conf` increment is multiplied by the start-of-cycle `conformation_gate(state, mat)`.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_pressure_conformation.py`:

```python
def test_conform_driver_default_is_raw():
    """Default mode = raw (monotonic) — backward-compat."""
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
    assert JointMaterial().conform_driver == "raw"


def _run_W_conf(driver, n_cycles=40):
    """Roda o engine com conformacao ativa e devolve W_conf ao final."""
    import numpy as np  # noqa: F401
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer, JointMaterial, JointGeometry)
    mat = JointMaterial(W_conf_ref=1.0e4, conform_pressure_exp=2.0,
                        p_ref_conform=5.0e8, conform_driver=driver)
    geom = JointGeometry()
    an = DynamicStiffnessAnalyzer(geom=geom, mat=mat, F_0_init=120_000.0)
    for _ in range(n_cycles):
        an.step_cycle(F_amp=0.0, theta_load=0.0, freq=0.5, delta_amp=0.5e-3)
    return an.state.W_conf


def test_effective_driver_self_attenuates_below_raw():
    """Efetivo pondera o incremento pelo gate => W_conf cresce menos que o raw."""
    w_raw = _run_W_conf("raw")
    w_eff = _run_W_conf("effective")
    assert w_eff > 0.0            # ainda cresce
    assert w_eff < w_raw          # mas menos (auto-atenuacao)


def test_effective_driver_inert_when_W_conf_ref_zero():
    """Com W_conf_ref=0 o modo efetivo continua inerte (W_conf fica 0)."""
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer, JointMaterial, JointGeometry)
    mat = JointMaterial(W_conf_ref=0.0, conform_driver="effective")
    an = DynamicStiffnessAnalyzer(geom=JointGeometry(), mat=mat, F_0_init=120_000.0)
    for _ in range(10):
        an.step_cycle(F_amp=0.0, theta_load=0.0, freq=0.5, delta_amp=0.5e-3)
    assert an.state.W_conf == 0.0
```

> Note: match the real `DynamicStiffnessAnalyzer` / `JointGeometry` constructor signatures used elsewhere in `tests/test_pressure_conformation.py` — if the existing tests build the analyzer differently (e.g. a helper or different kwarg names), reuse that exact construction. The three assertions (default=raw; effective<raw and >0; inert at W_conf_ref=0) are the contract; adapt only the construction boilerplate.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_pressure_conformation.py -q`
Expected: `test_conform_driver_default_is_raw` fails (no `conform_driver` field / unexpected kwarg); the driver tests fail (no `conform_driver` kwarg).

- [ ] **Step 3: Add the `conform_driver` field to `JointMaterial`**

Near the other conformation fields (`W_conf_ref`, `conform_pressure_exp`, `p_ref_conform`, ~line 180):

```python
    # driver do conformation_gate (spec §7): "raw" = monotonico (acumula o
    # trabalho de slip cru, default, backward-compat); "effective" = auto-
    # limitante (pondera o incremento pelo gate de inicio-de-ciclo, plateau <1).
    conform_driver: str = "raw"
```

- [ ] **Step 4: Add the effective branch in `step_cycle` §4.7**

Replace the accumulation (lines 910–915) with:

```python
        if self.mat.W_conf_ref > 0.0:
            p = max(self.state.F_0, 0.0) / max(self.geom.A_contact, 1e-12)
            pw = (p / max(self.mat.p_ref_conform, 1e-12)) ** self.mat.conform_pressure_exp
            dW_conf = pw * (
                4.0 * mu_bearing_eff(self.state, self.mat)
                * max(self.state.F_0, 0.0) * max(_slip_acc, 0.0))
            if self.mat.conform_driver == "effective":
                # driver de equilibrio auto-limitante (spec §7): pondera pelo
                # gate de INICIO-de-ciclo (state.W_conf ainda nao foi atualizado
                # neste ciclo) — o mesmo g que os mecanismos viram; c e slip_eff
                # co-determinados, resolvido de forma explicita (consistente com
                # o padrao "le no inicio, atualiza depois" de W_slip_acc/D/F_0).
                dW_conf *= conformation_gate(self.state, self.mat)
            self.state.W_conf += dW_conf
```

- [ ] **Step 5: Syntax-check + run the tests to verify they pass**

Run:
```bash
python -c "import ast; ast.parse(open('src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py',encoding='utf-8').read()); print('OK')"
python -m pytest tests/test_pressure_conformation.py -q
```
Expected: OK; all pass (new 3 + existing).

- [ ] **Step 6: Commit**

```bash
git add src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py tests/test_pressure_conformation.py
git commit -m "feat(engine): driver de conformacao 'effective' (auto-limitante) selecionavel" \
  -m "conform_driver: raw (default, backward-compat bit-identical) | effective (pondera o incremento de W_conf pelo gate de inicio-de-ciclo -> plateau auto-limitante, spec §7). Guardado por W_conf_ref>0. 3 testes: default=raw, effective<raw, inerte com W_conf_ref=0." \
  -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Config plumbing — `conform_driver` on the shared config + `_material` + `build_conformation_config_effective`

**Files:**
- Modify: `src/bolt_analysis_studio/calibration/shared_calibrator.py` (`SharedCalibrationConfig` ~line 65; `_material` line 85)
- Modify: `New_Theory/conformation_fit.py` (add `build_conformation_config_effective`)
- Test: `tests/test_shared_calibrator.py`, `tests/test_conformation_fit.py`

**Interfaces:**
- Consumes: `JointMaterial.conform_driver` (Task 1); existing `build_conformation_config` (conformation_fit.py line 34).
- Produces: `SharedCalibrationConfig.conform_driver: str = "raw"`; `_material` sets `kw["conform_driver"] = self.cfg.conform_driver`; `build_conformation_config_effective(n_cycles=2500)` returns a config with `conform_driver="effective"`.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_shared_calibrator.py`:

```python
def test_material_carries_conform_driver_and_constants_stay_numeric():
    """conform_driver flui via config (nao via priors) -> material recebe a
    string, e self.constants segue 100% numerico (line 204 float(v) safe)."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "New_Theory"))
    from conformation_fit import build_conformation_config_effective
    from bolt_analysis_studio.calibration.shared_calibrator import SharedCalibrator
    cfg = build_conformation_config_effective(n_cycles=50)
    assert cfg.conform_driver == "effective"
    cal = SharedCalibrator(cfg)
    mat = cal._material(cfg.conditions[0])
    assert mat.conform_driver == "effective"
    # nenhuma string vazou para as constantes numericas
    assert all(isinstance(v, (int, float)) for v in cal.constants.values())
```

Add to `tests/test_conformation_fit.py`:

```python
def test_config_effective_selects_self_limiting_driver():
    """build_conformation_config_effective liga o driver 'effective' e herda
    o resto (n=2 fixo, W_conf_ref fitavel)."""
    from conformation_fit import (build_conformation_config,
                                   build_conformation_config_effective)
    assert build_conformation_config(n_cycles=50).conform_driver == "raw"
    cfg = build_conformation_config_effective(n_cycles=50)
    assert cfg.conform_driver == "effective"
    assert "W_conf_ref" in cfg.bounds                    # segue fitavel
    assert "conform_pressure_exp" not in cfg.bounds      # n segue fixo
    assert cfg.priors["conform_pressure_exp"] == 2.0
```

(Also add `build_conformation_config_effective` to the `from conformation_fit import (...)` block at the top of `tests/test_conformation_fit.py`.)

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_shared_calibrator.py::test_material_carries_conform_driver_and_constants_stay_numeric tests/test_conformation_fit.py::test_config_effective_selects_self_limiting_driver -q`
Expected: fail — `SharedCalibrationConfig` has no `conform_driver`; `build_conformation_config_effective` undefined.

- [ ] **Step 3: Add `conform_driver` to `SharedCalibrationConfig`**

After `max_nfev: int = 40` (line 65):

```python
    # modo do driver de conformacao propagado ao JointMaterial (nao-numerico,
    # portanto NAO vai em priors/constants — via config, aplicado em _material).
    conform_driver: str = "raw"
```

- [ ] **Step 4: Apply it in `_material`**

In `_material` (line 78–85), add before `return`:

```python
        kw["conform_driver"] = self.cfg.conform_driver
        return JointMaterial(**kw)
```

- [ ] **Step 5: Add `build_conformation_config_effective` to `conformation_fit.py`**

After `build_conformation_config_fitn` (line 51):

```python
def build_conformation_config_effective(n_cycles: int = 2500):
    """Como build_conformation_config (n=2 fixo, W_conf_ref o unico fitavel),
    mas seleciona o driver auto-limitante 'effective' (spec §7): o incremento de
    W_conf e ponderado pelo gate de inicio-de-ciclo (plateau, nao equilibrio
    verdadeiro c*<1). Testa se a auto-atenuacao mantem a nova inerte SEM o n
    agudo que o strand 1 (fit-n) expos no driver raw."""
    cfg = build_conformation_config(n_cycles=n_cycles)
    cfg.conform_driver = "effective"
    return cfg
```

- [ ] **Step 6: Syntax-check + run the tests**

Run:
```bash
python -c "import ast; ast.parse(open('src/bolt_analysis_studio/calibration/shared_calibrator.py',encoding='utf-8').read()); ast.parse(open('New_Theory/conformation_fit.py',encoding='utf-8').read()); print('OK')"
python -m pytest tests/test_shared_calibrator.py tests/test_conformation_fit.py -q
```
Expected: OK; all pass.

- [ ] **Step 7: Commit**

```bash
git add src/bolt_analysis_studio/calibration/shared_calibrator.py New_Theory/conformation_fit.py tests/test_shared_calibrator.py tests/test_conformation_fit.py
git commit -m "feat(calib): propaga conform_driver via SharedCalibrationConfig + build_conformation_config_effective" \
  -m "conform_driver (nao-numerico) via config -> _material (constants seguem 100% numericas, line 204 float(v) safe). build_conformation_config_effective liga o modo auto-limitante herdando n=2 fixo." \
  -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Validation script — A/B raw-vs-effective (n=2) + fit-n on effective

**Files:**
- Modify: `New_Theory/conformation_fit.py` (add `main_effective`; extend the `__main__` dispatch)
- Test: `tests/test_conformation_fit.py`

**Interfaces:**
- Consumes: `build_conformation_config` (raw), `build_conformation_config_effective`, `build_conformation_config_fitn` + a fit-n-on-effective variant, `classify_conformation_verdict`, `SharedCalibrator._fit_subset`, `mae_by_condition`, `_sobretorque_residual` (reuse the helpers `main`/`main_fitn` already use).
- Produces: `main_effective()` writing `New_Theory/conformation_effective.json` + `conformation_effective_report.md`; `__main__` dispatches `--effective` → `main_effective()`. `build_conformation_config_effective_fitn(n_cycles)` = effective + `conform_pressure_exp` freed in `(0.5, 4.0)`.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_conformation_fit.py`:

```python
def test_config_effective_fitn_frees_n_and_keeps_effective_driver():
    from conformation_fit import build_conformation_config_effective_fitn
    cfg = build_conformation_config_effective_fitn(n_cycles=50)
    assert cfg.conform_driver == "effective"
    assert cfg.bounds["conform_pressure_exp"] == (0.5, 4.0)
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/test_conformation_fit.py::test_config_effective_fitn_frees_n_and_keeps_effective_driver -q`
Expected: fail — `build_conformation_config_effective_fitn` undefined.

- [ ] **Step 3: Add `build_conformation_config_effective_fitn` + `main_effective`**

After `build_conformation_config_effective`:

```python
def build_conformation_config_effective_fitn(n_cycles: int = 2500):
    """Driver 'effective' com n TAMBEM fitavel — testa se a auto-atenuacao tira
    o n do teto (o rail que o strand 1 expos no driver raw)."""
    cfg = build_conformation_config_effective(n_cycles=n_cycles)
    cfg.bounds = dict(cfg.bounds, conform_pressure_exp=(0.5, 4.0))
    return cfg
```

`main_effective()` mirrors `main`/`main_fitn` (reuse their run/verdict helpers verbatim — do not re-implement the fit or the classifier). Structure:

1. **Baseline (raw, n=2):** `SharedCalibrator(build_conformation_config(n_cycles))`; `._fit_subset(["C_creep", "W_conf_ref"])`; record `mae_by_condition` + sobretorque residual.
2. **Treatment (effective, n=2):** `SharedCalibrator(build_conformation_config_effective(n_cycles))`; `._fit_subset(["C_creep", "W_conf_ref"])`; record MAEs + residual + fitted `W_conf_ref`.
3. **Verdict:** `classify_conformation_verdict(base_maes, treat_maes, base_resid, treat_resid)` — the SAME frozen classifier.
4. **Fit-n on effective:** `SharedCalibrator(build_conformation_config_effective_fitn(n_cycles))`; `._fit_subset(["C_creep", "W_conf_ref", "conform_pressure_exp"])`; record fitted `n` (does it still rail at 4.0?) + its MAEs.
5. Write `conformation_effective.json` (baseline/treatment/verdict blocks mirroring `conformation_fit.json`, plus a `fitn_effective` block with `conform_pressure_exp_fitted` and its MAEs) + a short `conformation_effective_report.md`. Print a one-screen summary like `main_fitn`.

Add to the `__main__` dispatch:

```python
    if "--effective" in sys.argv:
        main_effective()
    elif "--fit-n" in sys.argv:
        main_fitn()
    else:
        main()
```

- [ ] **Step 4: Syntax-check + run the test**

Run:
```bash
python -c "import ast; ast.parse(open('New_Theory/conformation_fit.py',encoding='utf-8').read()); print('OK')"
python -m pytest tests/test_conformation_fit.py -q
```
Expected: OK; all pass.

- [ ] **Step 5: `--quick` smoke of the runner (tiny n, just proves it executes end-to-end)**

Run: `python New_Theory/conformation_fit.py --effective --quick 2>&1 | tail -20` (if `--quick` isn't wired for `main_effective`, run with a small `n_cycles` hardcoded temporarily, or skip and rely on Task 4's real run — do NOT commit a hacked n_cycles).
Expected: produces `conformation_effective.json` with baseline/treatment/verdict/fitn_effective keys, no exception. (Smoke only; the real run is Task 4.)

- [ ] **Step 6: Commit (code + tests only — NOT the smoke JSON)**

```bash
git add New_Theory/conformation_fit.py tests/test_conformation_fit.py
git commit -m "feat(conformation): A/B raw-vs-effective (n=2) + fit-n no driver effective" \
  -m "main_effective(): baseline raw vs treatment effective (mesmo n=2, mesmo classificador congelado §9) + fit-n no effective (o n sai do teto?). Artefatos conformation_effective.{json,md}. Dispatch --effective." \
  -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Real run + document AS IS (§4.9 strand-2 addendum + §7 reframe)

**Files:**
- Create (untracked artifacts): `New_Theory/conformation_effective.json`, `conformation_effective_report.md`
- Modify: `New_Theory/MODEL_LEGITIMACY.md` (§4.9 strand-2 addendum + changelog line)
- Modify: `docs/superpowers/specs/2026-07-04-pressure-conformation-design.md` (§7 reframe: "true equilibrium" → self-limiting plateau)

**Interfaces:**
- Consumes: the committed script (Task 3), the frozen classifier, `conformation_fit.json` (raw n=2 baseline for cross-reference).
- Produces: the documented strand-2 verdict AS IS.

- [ ] **Step 1: Run the real A/B + fit-n-on-effective (background)**

Run (background, ~1–3 h like the raw run): `python New_Theory/conformation_fit.py --effective > <scratchpad>/conf-effective-run.log 2>&1`
Wait for exit 0.

- [ ] **Step 2: Independently recompute the verdict from the committed JSON**

Load `conformation_effective.json`; re-run `classify_conformation_verdict` on its baseline/treatment MAEs + residuals (as done for fit-n). Confirm the stored verdict. Note the fitted `W_conf_ref`, the effective-vs-raw MAE deltas, and **whether fit-n's `n` still rails at 4.0** (the strand-1 linkage — the headline question of strand 2).

- [ ] **Step 3: Verify the canonical block is intact**

Confirm `joint_calibrations.json` `shared` hash is still `21ed6a7ad94114d0` and `git status --short` shows only the two known foreign untracked files plus the new experiment artifacts.

- [ ] **Step 4: Commit the artifacts AS IS**

```bash
git add -f New_Theory/conformation_effective.json New_Theory/conformation_effective_report.md   # *.json/*.md not ignored; -f harmless. If a png is produced, git add -f it too.
git commit -m "fase2 strengthen: resultado A/B raw-vs-effective + fit-n effective AS IS" \
  -m "<preencher com os numeros reais: sobretorque base->treat, deriva das outras, n do fit-n effective (railou?), residual>" \
  -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 5: Write the §4.9 strand-2 addendum + §7 reframe (Opus-fallback subagent; Fable is spend-capped)**

Dispatch an Opus subagent (recompute-from-JSON discipline) to:
- Read `conformation_effective.json`; recompute the verdict; write a **§4.9 "Robustez — driver de equilíbrio (strand 2/3)"** addendum AS IS: the A/B result (does effective RESOLVE at n=2? do the others hold? residual?), and critically **whether the effective driver takes `n` off the ceiling** in fit-n (the strand-1→strand-2 test). Calibrated language; cross-link strand 1.
- Amend spec `§7`: replace the "true equilibrium `c < 1`" claim for the minimal form with the accurate characterization — **self-limiting plateau** (increment self-attenuates via the gate *and* `∝F_0^{n+1}`; over the finite test `c` plateaus `<1`, asymptotically `→1` under creep). A genuine `c*<1` fixed point needs slip-kinematic feedback (raise stick capacity so disp-mode slip→0) — deferred, entangles with roadmap item #4. Keep §7's raw-vs-effective recommendation structure.
- Append a dated 2026-07-04 changelog line in `MODEL_LEGITIMACY.md`.
- Commit `New_Theory/MODEL_LEGITIMACY.md` + the spec file only. Portuguese, no-accent commit + trailer.

- [ ] **Step 6: Opus final review of the whole strand-2 diff**

Run `git diff main...HEAD` for the strand-2 branch; dispatch an Opus reviewer over the engine+config+script diff (backward-compat bit-identity for `raw`, no leaked string into numeric constants, conservation unaffected by the gated increment, no canonical-block writes). Fix Critical/Important findings, then finish the branch.

---

## Self-Review

**Spec coverage:** §7 (driver variant) → Tasks 1–4; §8 (engine/registry integration — `conform_driver` needs no ParameterRule since it's a mode, not a fitted constant) → Task 2; §9 (frozen thresholds, A/B method) → Task 3–4 reuse verbatim. The plateau-vs-true-equilibrium honesty correction → Task 4 §7 reframe. ✅

**Placeholder scan:** All code steps carry full code except Task 4 Step 4's commit body (the real numbers are unknown until the run) and `main_effective`'s body (Step 3 specifies structure + "reuse `main`/`main_fitn` helpers verbatim" rather than duplicating ~60 lines — DRY; the implementer has both as templates in the same file). These are deliberate, not omissions.

**Type consistency:** `conform_driver: str` on both `JointMaterial` and `SharedCalibrationConfig`, default `"raw"`, values `{"raw","effective"}`; `_material` sets `kw["conform_driver"]`; `build_conformation_config_effective`/`_effective_fitn` set `cfg.conform_driver="effective"`. Consistent across tasks. ✅
