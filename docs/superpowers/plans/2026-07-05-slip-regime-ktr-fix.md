# Slip-Regime (k_tr) Fix — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline, the professor's established preference). Steps use checkbox (`- [ ]`) syntax. An Opus review of the engine diff runs before merge.

**Goal:** Give the engine a real partial/gross-slip regime by replacing the too-stiff `k_tr = 0.3·k_axial` with the bolt's transverse **bending** stiffness — **opt-in** (default reproduces current), validated standalone (regime accuracy + plateau fix + does it rescue the falsified damage trigger). Canonical re-fit is a separate gated decision, NOT in this plan.

**Architecture:** A `k_tr_transverse(geom, mat)` helper selects `"axial_frac"` (current, default) or `"bending"` (`c_bend·E·I/L³`). `resolve_transverse_slip` gains an optional `geom`; the 4 call sites (all have `geom`) pass it. Calibrate `c_bend` to the amplitude sweeps, validate, then add the Mindlin partial-slip micro-fretting-wear term.

**Tech Stack:** Python, `DynamicStiffnessAnalyzer`, `transfer_validation.py`, pytest.

**Spec:** `docs/superpowers/specs/2026-07-05-slip-regime-ktr-fix-design.md`

## Global Constraints

- All I/O `encoding='utf-8'`; `ast.parse` syntax-check after every `.py` edit; **run pytest and check the exit code before committing** (do NOT mask it with `| tail` in a `&&` chain — a failing test slipped through that way once).
- **Never `git add -A`**; never touch `New_Theory/Materiais_Metalicos_EPL_Gb.docx` / `crash_log.txt`.
- Commits Portuguese, **no accents**, trailer `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- **Opt-in / backward-compat hard gate:** default `k_tr_mode="axial_frac"` ⇒ `k_tr = max(0.3·k_j_init,1)` exactly ⇒ every existing run/fit **bit-identical**. The `geom` arg is threaded but unused in that mode.
- **Canonical `shared` block NEVER written** by this work; **canonical re-fit is OUT of scope** (a later gated decision).
- **Frozen pre-registered validation thresholds** (Task 3) — set before the run, recorded AS IS.
- `*.png`/`*.csv` gitignored (force-add experiment pngs).

---

### Task 1: Engine — bending `k_tr` (opt-in) in `resolve_transverse_slip`

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (`JointMaterial` ~line 158; new `k_tr_transverse` near `F_slip_transverse` line 379; `resolve_transverse_slip` line 476; 4 call sites: `W_ext_per_cycle` line 522, `WearLoss.rate` line 644, `step_cycle` lines 859 & 930)
- Test: `tests/test_slip_regime_ktr.py` (new)

**Interfaces:**
- Produces: `JointMaterial.k_tr_mode: str = "axial_frac"`, `JointMaterial.c_bend: float = 3.0`; `k_tr_transverse(geom, mat) -> float`; `resolve_transverse_slip(..., geom=None)`.

- [ ] **Step 1: Write the failing tests** — `tests/test_slip_regime_ktr.py`:

```python
"""Slip regime k_tr fix (spec 2026-07-05): bending k_tr, opt-in."""
import numpy as np
import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    k_tr_transverse, resolve_transverse_slip,
)

M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)


def test_ktr_axial_frac_is_default_and_current():
    m = JointMaterial()  # k_tr_mode default "axial_frac"
    assert m.k_tr_mode == "axial_frac"
    assert k_tr_transverse(M16, m) == max(m.k_j_init * 0.3, 1.0)   # current


def test_ktr_bending_is_much_softer_and_per_rig():
    m = JointMaterial(k_tr_mode="bending", c_bend=3.0)
    k_bend = k_tr_transverse(M16, m)
    assert k_bend < 1e8                       # ~1e7, ~100x softer than axial 1.2e9
    # per-rig: bigger d (stiffer) => larger k_tr; longer L => smaller k_tr
    M8 = JointGeometry(A_s=36.6e-6, L_eff=0.030, d_2=7.188e-3, pitch=1.25e-3,
                       r_bearing=6e-3, A_contact=52e-6)
    assert k_tr_transverse(M8, m) < k_bend    # smaller bolt => softer bending


def test_ktr_bending_gives_realistic_delta_t():
    """delta_t = F_slip/k_tr ~ 0.1-0.5mm (not ~0.001mm) at M16 nominal."""
    m = JointMaterial(k_tr_mode="bending", c_bend=3.0)
    st = SlowState(F_0=50e3)
    # partial at delta=0.1mm (below delta_t), gross at delta=0.6mm (above)
    slip_lo = resolve_transverse_slip(st, m, 20e3, np.pi/2, delta_amp=0.1e-3, geom=M16)
    slip_hi = resolve_transverse_slip(st, m, 20e3, np.pi/2, delta_amp=0.6e-3, geom=M16)
    assert slip_lo == 0.0                      # partial slip (below delta_t)
    assert slip_hi > 0.0                       # gross slip (above delta_t)


def test_backward_compat_axial_frac_slip_unchanged():
    """Default mode: slip identical whether or not geom is passed (geom unused)."""
    m = JointMaterial()
    st = SlowState(F_0=50e3)
    s_no = resolve_transverse_slip(st, m, 20e3, np.pi/2, delta_amp=0.5e-3)
    s_ge = resolve_transverse_slip(st, m, 20e3, np.pi/2, delta_amp=0.5e-3, geom=M16)
    assert s_no == s_ge                        # geom ignored in axial_frac
```

- [ ] **Step 2: Run to verify fail** (`k_tr_transverse` undefined, `k_tr_mode` not a field).

- [ ] **Step 3: Add `JointMaterial` fields** (after `k_damage_scale`/onset fields):

```python
    # Regime de slip (spec 2026-07-05): k_tr_mode "axial_frac" (default, atual =
    # 0.3*k_j_init, delta_t~0) | "bending" (rigidez de FLEXAO do parafuso
    # c_bend*E*I/L^3 ~ 1e7 -> delta_t~0.3mm, prop F0*L^3/(E*d^4)). Opt-in.
    k_tr_mode: str = "axial_frac"
    c_bend: float = 3.0              # fator de contorno/compliance (~3 cantilever), calibrado
```

- [ ] **Step 4: Add `k_tr_transverse`** (near `F_slip_transverse`, ~line 382):

```python
def k_tr_transverse(geom: JointGeometry, mat: JointMaterial) -> float:
    """Rigidez transversal de onset de slip. 'axial_frac' (default, backward-
    compat) = 0.3*k_j_init (~1e9, delta_t~0). 'bending' = flexao do parafuso
    c_bend*E*I/L_eff^3 (I=pi*d^4/64, d~d_2), ~1e7 -> delta_t~0.3mm (spec
    2026-07-05). geom None => axial_frac (a bending precisa da geometria)."""
    if mat.k_tr_mode == "bending" and geom is not None:
        d = geom.d_2                              # diametro efetivo de flexao
        I = np.pi * d ** 4 / 64.0
        return max(mat.c_bend * geom.E * I / max(geom.L_eff, 1e-6) ** 3, 1.0)
    return max(mat.k_j_init * 0.3, 1.0)
```

- [ ] **Step 5: Use it in `resolve_transverse_slip`** — add `geom=None` param, replace the `k_tr = ...` line:

```python
def resolve_transverse_slip(state: SlowState, mat: JointMaterial,
                            F_amp: float, theta_load: float,
                            delta_amp: Optional[float] = None,
                            geom: Optional[JointGeometry] = None) -> float:
    ...
    F_slip = F_slip_transverse(state, mat)
    k_tr = k_tr_transverse(geom, mat)        # was: max(mat.k_j_init * 0.3, 1.0)
    ...
```

- [ ] **Step 6: Thread `geom` at the 4 call sites** — pass `geom=geom` (W_ext_per_cycle:522, WearLoss.rate:644 — both have `geom`) and `geom=self.geom` (step_cycle:859 & 930).

- [ ] **Step 7: Syntax-check + tests + backward-compat sweep**

```bash
python -c "import ast; ast.parse(open('src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py',encoding='utf-8').read()); print('OK')"
python -m pytest tests/test_slip_regime_ktr.py -q; echo "EXIT=$?"
python -m pytest tests/test_surface_damage.py tests/test_slip_onset_incubation.py tests/test_pressure_conformation.py tests/test_v2_solver_preload.py tests/test_shared_calibrator.py tests/test_predictive_damage_trigger.py -q; echo "EXIT=$?"
```
Expected: all pass, both EXIT=0 (backward-compat: default axial_frac unchanged).

- [ ] **Step 8: Commit** (`feat(engine): k_tr de flexao opt-in (k_tr_mode bending) — regime partial/gross slip`).

---

### Task 2: Calibrate `c_bend` to the amplitude sweeps (Phase B)

**Files:** `New_Theory/calibrate_ktr.py` (new, analysis) or a scratchpad sweep; the calibrated `c_bend` recorded.

**Interfaces:** Consumes the amplitude-sweep cases (Lu M8 fig18/20, Liu M16, Yang M10, Rousseau t10/t14) from `DIGITIZED_CASES`; produces the `c_bend` that best matches the partial→gross transition.

- [ ] **Step 1:** Sweep `c_bend` (e.g. 1..10); for each, with `k_tr_mode="bending"`, compute per-case model slip and the **regime match**: partial (slip≈0) on the low-amplitude/plateau members, gross on the high-amplitude/collapse members of each controlled sweep. Rank by regime accuracy.
- [ ] **Step 2:** Pick the `c_bend` maximizing regime accuracy across the sweeps; record it + the per-sweep transition δ_t vs the observed flip. AS IS (if no single `c_bend` separates all, that's a finding → note whether member-compliance-in-series is needed, spec §8 Q1).
- [ ] **Step 3:** Set `c_bend` default to the calibrated value (or document it as the recommended value for `bending` mode). Commit (`calib: c_bend calibrado aos amplitude sweeps (regime partial/gross)`).

---

### Task 3: Validate the core regime fix (Phase D-core)

**Files:** `New_Theory/transfer_validation.py` (a `--ktr-bending` flag, separate `_ktr` artifacts), `MODEL_LEGITIMACY.md` (§4.8 addendum).

**Pre-registered thresholds (FROZEN before the run, AS IS):**
- **Regime accuracy:** with `k_tr_mode="bending"` (calibrated `c_bend`), the plateau cases (`final_data>0.55`) get model `slip≈0`/low loosening and the collapse cases (`final_data<0.30`) get gross slip — **≥70%** correct on each side (looser than the trigger's 75% since c_bend is one global factor).
- **Plateau over-prediction fixed:** the §4.8 plateau cases (Yang, low-amp Liu) — `final_pred` rises from ≈0 toward the data plateau (a **≥0.2 improvement** in `final_pred` on those cases).
- **Damage-trigger rescue (bonus, not a gate):** re-run `--damage-trigger` *with* `k_tr_mode="bending"`; report whether a `W_crit` now separates collapse from plateau (the falsified §4.8 result may flip). Recorded AS IS either way.

- [ ] **Step 1:** Add `--ktr-bending` to `transfer_validation` (sets `k_tr_mode="bending"`, calibrated `c_bend` on the material; separate `transfer_*_ktr.*` artifacts; mirrors the `--damage-on`/`--damage-trigger` flag pattern). Test + commit.
- [ ] **Step 2:** Run it (background, ~2–5 min). Compute regime accuracy, the plateau-`final_pred` improvement, per-source median/p90 vs the damage-off baseline.
- [ ] **Step 3:** Re-run `--damage-trigger --ktr-bending` (the rescue check) + the `W_crit` sweep on the corrected regime.
- [ ] **Step 4:** Document §4.8 addendum AS IS (does the bending `k_tr` fix the regime? the plateau over-prediction? rescue the trigger?) + changelog + preserve artifacts. Verdict vs the frozen thresholds.

---

### Task 4: Mindlin partial-slip micro-fretting wear (Phase C)

**Gate:** proceed after Task 3 confirms the core regime fix works. If partial-slip cases now have `slip=0` and the data shows they still *wear* (fretting) without loosening, add the partial-regime wear term.

**Files:** `dynamic_stiffness_analyzer.py` (partial-slip micro-slip → `WearLoss` dose, gated OUT of rotational-loosening `dF_0`); tests.

- [ ] Add a partial-regime micro-slip amount (small, Mindlin edge-slip scale) that feeds **wear** (and the damage dose `W_slip_acc`) but contributes **~zero rotational-loosening `dF_0`** — the "partial slip = wear, no loosening" split. Default-off (a `partial_fret_coeff=0` sentinel). TDD; re-run Task 3 validation to check it adds partial-slip wear realism without hurting the regime/plateau result. Commit + doc.

---

## Self-Review

**Spec coverage:** §3.1 bending `k_tr` → Task 1 (exact); §3.2 calibrate `c_bend` → Task 2; §3.3 Mindlin partial-slip wear → Task 4 (gated on Task 3); §4 opt-in/foundational → Task 1 default + "canonical re-fit OUT of scope"; §5 interactions (damage-trigger rescue, conformation overlap, member stiffness) → Task 3 validation; §6 validation → Task 3. Canonical re-fit correctly excluded. ✅

**Placeholder scan:** Task 1 fully code-exact (fields, helper, the `k_tr =` swap, the 4 call-site edits named with line numbers). Tasks 2–4 give structure + the flag-pattern precedent (`--damage-on`/`--damage-trigger`) + pre-registered numbers; the empirical outputs (calibrated `c_bend`, run results) are unknown by design (AS IS). Task 4 is gated on Task 3. No hidden gaps.

**Type consistency:** `k_tr_transverse(geom, mat)` returns float; `k_tr_mode: str`, `c_bend: float`; `resolve_transverse_slip(..., geom=None)`; `geom=self.geom`/`geom=geom` at the call sites (all confirmed to have `geom`). `d = geom.d_2` for `I` (documented approximation; `c_bend` absorbs the exact-diameter factor). ✅
