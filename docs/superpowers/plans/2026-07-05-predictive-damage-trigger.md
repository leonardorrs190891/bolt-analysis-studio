# Predictive Damage Trigger — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline, the professor's established preference this session) to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax. An Opus review of the engine diff runs before merge (engine-change discipline).

**Goal:** Replace the manual `damage_active` flag with a **physical damage-onset trigger** — damage self-activates only after the accumulated gross-slip fretting dose crosses a critical value `W_crit` — so damage helps the collapse cases without hurting the plateaus (the §4.8 `--damage-on` trade-off).

**Architecture:** One new module-level Hill gate `damage_onset_gate` (mirrors `slip_onset_gate`) multiplies the existing `dD` growth in `step_cycle`. The slip regime is folded in for free (`dD ∝ W_slip_cycle`, ~0 in partial slip). Validated by re-running the transfer sweep with the trigger *deciding* (no manual flag), against pre-registered thresholds. The near-proof activator is **evidence-gated** on the validation (likely a diagnostic — near-proof is a non-slip mechanism).

**Tech Stack:** Python, `DynamicStiffnessAnalyzer`, `transfer_validation.py`, pytest.

**Spec:** `docs/superpowers/specs/2026-07-05-predictive-damage-trigger-design.md`

## Global Constraints

- All file I/O `encoding='utf-8'`. `python -c "import ast; ast.parse(open('PATH',encoding='utf-8').read())"` after every `.py` edit.
- **Never `git add -A`** — explicit file lists. **Never** touch `New_Theory/Materiais_Metalicos_EPL_Gb.docx` or `crash_log.txt` (professor's WIP).
- Commits: Portuguese, **no accents**, trailer `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- **Default-inert / backward-compat is a hard gate:** `c_D=0` default ⇒ damage inert regardless; `W_crit=0` ⇒ `damage_onset_gate≡1` (transparent) ⇒ existing damage-active profiles (reusada/reaperto) reproduce **bit-identically**.
- **Canonical `shared` block** of `joint_calibrations.json` NEVER written by this work.
- **Frozen pre-registered validation thresholds** (Task 4) — set before the run, recorded AS IS, never tuned to pass.
- Science AS IS; `*.png`/`*.csv` gitignored (force-add experiment pngs).

---

### Task 1: Engine — `damage_onset_gate` + `W_crit` gate on damage growth

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (`JointMaterial` damage fields ~line 154; new gate fn near `slip_onset_gate` line 321; `step_cycle` D-growth line 895–898)
- Test: `tests/test_predictive_damage_trigger.py` (new)

**Interfaces:**
- Consumes: `SlowState.W_slip_acc` (start-of-cycle, gross-slip-gated), existing `dD` growth.
- Produces: `damage_onset_gate(state, mat) -> float`; `JointMaterial.W_crit: float = 0.0`, `JointMaterial.dmg_onset_sharpness: float = 4.0`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_predictive_damage_trigger.py`:

```python
"""Predictive damage-onset trigger (spec 2026-07-05). W_crit gate on D-growth."""
import numpy as np
import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    damage_onset_gate,
)

M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)


def _run(mat, F0, n, delta=0.5e-3):
    ana = DynamicStiffnessAnalyzer(M16, mat, F0)
    for _ in range(n):
        ana.step_cycle(20e3, np.pi / 2, 0.5, delta_amp=delta)
    return ana


def test_gate_transparent_when_W_crit_nonpositive():
    mat = JointMaterial()  # W_crit default 0.0
    for w in (0.0, 1e3, 1e9):
        assert damage_onset_gate(SlowState(F_0=50e3, W_slip_acc=w), mat) == 1.0


def test_gate_hill_shape():
    mat = JointMaterial(W_crit=1e4, dmg_onset_sharpness=4.0)
    g_lo = damage_onset_gate(SlowState(F_0=50e3, W_slip_acc=1e3), mat)   # below
    g_at = damage_onset_gate(SlowState(F_0=50e3, W_slip_acc=1e4), mat)   # at
    g_hi = damage_onset_gate(SlowState(F_0=50e3, W_slip_acc=1e6), mat)   # above
    assert g_lo < 0.05
    assert g_at == pytest.approx(0.5)
    assert g_hi > 0.95
    assert g_lo < g_at < g_hi


def test_backward_compat_W_crit_zero_reproduces_ungated_damage():
    """W_crit=0 (transparent) => D-growth bit-identical to pre-trigger engine."""
    common = dict(c_D=2.0, k_dmg_wear=4.0, k_dmg_mu=1.0)
    d_ungated = _run(JointMaterial(**common), 120e3, 200).state.D
    d_wcrit0 = _run(JointMaterial(**common, W_crit=0.0), 120e3, 200).state.D
    assert d_wcrit0 == d_ungated                      # exact


def test_default_inert_no_damage_regardless_of_W_crit():
    """c_D=0 (default) => D stays 0 even with W_crit set."""
    d = _run(JointMaterial(W_crit=1e4), 120e3, 200).state.D
    assert d == 0.0


def test_onset_delays_then_grows_damage():
    """With c_D>0 and W_crit>0: D stays ~0 until the dose crosses W_crit, then grows."""
    common = dict(c_D=2.0, k_dmg_wear=4.0, k_dmg_mu=1.0)
    d_gated = _run(JointMaterial(**common, W_crit=5e4), 120e3, 2000).state.D
    d_ungated = _run(JointMaterial(**common, W_crit=0.0), 120e3, 2000).state.D
    assert d_gated < d_ungated                        # onset delayed the growth
    assert d_gated > 0.0                              # but eventually grows (dose crossed)
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m pytest tests/test_predictive_damage_trigger.py -q`
Expected: fail — `damage_onset_gate` undefined, `W_crit` not a field.

- [ ] **Step 3: Add the `JointMaterial` fields**

Near the damage fields (after `k_damage_scale`, ~line 158):

```python
    # Gate de ONSET do dano (predictive trigger, spec 2026-07-05): D so cresce
    # depois que o trabalho de slip cru acumulado (W_slip_acc, ja gross-slip-
    # gated) cruza W_crit. W_crit=0 => gate transparente (backward-compat).
    W_crit: float = 0.0              # J — dose critica de fretting p/ onset (0 = off)
    dmg_onset_sharpness: float = 4.0  # k do Hill (= slip_onset_sharpness)
```

- [ ] **Step 4: Add `damage_onset_gate` (near `slip_onset_gate`, ~line 321)**

```python
def damage_onset_gate(state: SlowState, mat: JointMaterial) -> float:
    """Gate de ONSET do dano (spec 2026-07-05): espelha slip_onset_gate, mas
    portao do CRESCIMENTO do dano. g=W_slip_acc^k/(W_slip_acc^k+W_crit^k):
    abaixo de W_crit ~0 (D nao cresce -> plato), acima ~1 (D cresce -> colapso).
    W_crit<=0 => 1.0 (transparente, guarda o 0/0, backward-compat ungated)."""
    if mat.W_crit <= 0.0:
        return 1.0
    w = max(state.W_slip_acc, 0.0)
    k = mat.dmg_onset_sharpness
    return float(w ** k / (w ** k + mat.W_crit ** k))
```

- [ ] **Step 5: Gate the D-growth in `step_cycle`**

Change the D-growth (lines 895–898) to multiply `dD` by the gate:

```python
        if self.mat.c_D > 0.0 and self.mat.W_ref > 0.0:
            dD = (self.mat.k_damage_scale * self.mat.c_D
                  * (W_slip_cycle / self.mat.W_ref) * (1.0 - self.state.D)
                  * damage_onset_gate(self.state, self.mat))
            self.state.D = min(1.0, max(0.0, self.state.D + dD))
```

(The gate reads start-of-cycle `W_slip_acc` — updated later at ~line 907 — same ordering as `slip_onset_gate`. No order deps.)

- [ ] **Step 6: Syntax-check + run tests**

```bash
python -c "import ast; ast.parse(open('src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py',encoding='utf-8').read()); print('OK')"
python -m pytest tests/test_predictive_damage_trigger.py -q
```
Expected: OK; all pass.

- [ ] **Step 7: Backward-compat sweep + commit**

```bash
python -m pytest tests/test_surface_damage.py tests/test_slip_onset_incubation.py tests/test_pressure_conformation.py tests/test_v2_solver_preload.py tests/test_shared_calibrator.py -q
git add src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py tests/test_predictive_damage_trigger.py
git commit -m "feat(engine): gate de onset do dano (W_crit) sobre a D-growth — predictive trigger core" \
  -m "damage_onset_gate espelha slip_onset_gate: D so cresce apos o dose de fretting (W_slip_acc) cruzar W_crit. Substitui o damage_active manual pela fisica. Slip regime folded (dD ja ~ W_slip_cycle, ~0 em partial slip). Default-inert (c_D=0); W_crit=0 transparente (backward-compat bit-identical)." \
  -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Registry rule — offer `W_crit` only when the regime warrants

**Files:**
- Modify: `src/bolt_analysis_studio/calibration/parameter_registry.py`
- Test: `tests/test_parameter_registry.py`

**Interfaces:**
- Consumes: existing `ParameterRule`/predicate pattern (e.g. `_dano`, `_pressao_elevada`).
- Produces: a `ParameterRule` for `W_crit` (fittable) under a predicate that the dataset has a damage/collapse-capable regime (transverse gross slip present). `dmg_onset_sharpness` not fittable (shape).

- [ ] **Step 1: Write the failing test** — assert `W_crit` is in `active_candidates` for a transverse-slip damage regime and absent otherwise (mirror the existing conformation/damage predicate tests). (Copy the exact regime fields from the existing damage predicate test.)

- [ ] **Step 2–4:** run-fail → add the rule + predicate (reuse the transverse-slip/damage predicate; `W_crit` fittable bounds e.g. `(1e3, 1e7)`) → run-pass.

- [ ] **Step 5: Commit** (`feat(calib): ParameterRule p/ W_crit (onset do dano) sob regime de slip transverso`).

---

### Task 3: Validation harness — `--damage-trigger` mode of `transfer_validation.py`

**Files:**
- Modify: `New_Theory/transfer_validation.py` (a `--damage-trigger` flag; separate `transfer_*_trigger.*` artifacts)
- Test: `tests/test_transfer_validation.py`

**Interfaces:**
- Produces: `--damage-trigger` mode that sets `c_D`/`k_dmg_wear`/`k_dmg_mu` (Stage-A damage physics) **AND** `W_crit>0` (+ `dmg_onset_sharpness`) on the material so damage **self-triggers** — no manual `damage_active`. Records final `D` per case + the collapse/plateau classification.

- [ ] **Step 1: Write the failing test** — `build`-style helper or a module flag `_DAMAGE_TRIGGER` (mirror the `_DAMAGE_ON` pattern from the `--damage-on` what-if): assert the material carries `c_D>0` and `W_crit>0` under the flag, and default path unchanged.

- [ ] **Step 2–5:** implement the flag in `_simulate` (`c_D=2, k_dmg_wear=4, k_dmg_mu=1, W_crit=<W_crit>` — `W_crit` a module constant, chosen so sobretorque-scale plateaus don't cross it; document the choice) + separate artifacts (suffix `_trigger`) + record `final_D` in `predict_case`. Run-fail → implement → run-pass. **Commit** (`feat: modo --damage-trigger no transfer_validation (dano auto-disparado por W_crit)`).

---

### Task 4: Run the validation + document AS IS (Phase C)

**Files:**
- Create (artifacts): `New_Theory/transfer_results_trigger.{json,md}`, `transfer_grid_trigger.png`
- Modify: `New_Theory/MODEL_LEGITIMACY.md` (§4.8 addendum), `.superpowers/sdd/progress.md`

**Pre-registered thresholds (FROZEN before the run — record AS IS whatever the result):**
- **Regime accuracy:** trigger activates damage (`final_D > 0.3`) on **≥75%** of collapse cases (`final_data < 0.30`) AND stays inert (`final_D < 0.10`) on **≥75%** of plateau cases (`final_data > 0.55`).
- **MAE (best-of-both):** GLOBAL median **≤ 0.19** (≈ blanket damage-on 0.1825, i.e. collapses helped) **AND** GLOBAL p90 **≤ 0.645** (≈ damage-off 0.6397, i.e. plateaus NOT hurt — the blanket-on p90 was 0.6696). Achieving both = the trigger delivers blanket-on's collapse gains without its plateau regression.
- **Baselines** for the report: damage-off (median 0.2281 / p90 0.6397) and blanket damage-on (0.1825 / 0.6696), both already committed.

- [ ] **Step 1:** Run `python New_Theory/transfer_validation.py --damage-trigger` (background, ~2–5 min).
- [ ] **Step 2:** Compute vs baselines: per-source median + p90, the regime-accuracy confusion matrix (collapse/plateau × damage-on/off), and check against the frozen thresholds. Also **diagnose the residual modes**: (a) **near-proof** — do the Bauer cases have gross slip (`W_slip_cycle>0`)? If ~0, the slip-driven trigger *cannot* reach them → near-proof is a **non-slip mechanism (diagnostic)**, gating Task 5. (b) **member-stiffness** — Rousseau t10/t14 (item 10, diagnostic).
- [ ] **Step 3:** Commit artifacts AS IS + write the §4.8 addendum (regime accuracy, MAE vs both baselines, verdict against the frozen thresholds, residual-mode diagnosis) + changelog. Opus-recompute-from-JSON discipline for the scientific write-up.

---

### Task 5 (CONDITIONAL — Phase B): near-proof activator

**Gate:** build ONLY IF Task 4 Step 2 shows the near-proof (Bauer) cases have **gross slip** (`W_slip_cycle>0`, so a slip-driven onset can reach them) AND the core trigger misses them. **Otherwise near-proof stays a documented diagnostic** (non-slip relaxation, out of the trigger's scope) — this is the pre-registered §3.2 "reverts to diagnostic," and Task 5 is skipped.

- [ ] If viable: add `s_proof_crit` (JointMaterial, default 1.0=off) + `proof_stress` source (from config/class or a documented default), fold a `severity_gate(s_proof=F_0_init/(proof·A_s))` into `damage_onset_gate` as `g_dmg = max(dose_gate, severity_gate)`; TDD; re-run the trigger validation; document AS IS whether it helps the near-proof cases without hurting others.

---

## Self-Review

**Spec coverage:** §3.1 core → Task 1; §8 registry → Task 2; §6 validation → Tasks 3–4; §3.2 near-proof → Task 5 (evidence-gated, matching the spec's "reverts to diagnostic"); member-stiffness diagnostic → Task 4 Step 2. Conformation-interaction (§4) is observed in Task 4's diagnosis, not a build step. ✅

**Placeholder scan:** Task 1 is fully code-exact. Tasks 2–3 give structure + the exact pattern to mirror (existing registry predicate; the `_DAMAGE_ON` flag precedent) rather than re-transcribing ~40 lines — deliberate, the implementer has both in-repo. Task 4's numbers are pre-registered (frozen); the run's outputs are unknown by design (AS IS). Task 5 is explicitly conditional. No hidden gaps.

**Type consistency:** `damage_onset_gate(state, mat)` ✓; `W_crit: float`, `dmg_onset_sharpness: float` on `JointMaterial`; gate multiplies `dD` (float). `W_crit` module constant in Task 3 vs `JointMaterial.W_crit` field — distinct, both used correctly (the harness sets the field from its constant). ✅
