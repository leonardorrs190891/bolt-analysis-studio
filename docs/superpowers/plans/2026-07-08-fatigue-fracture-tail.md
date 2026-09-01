# Fatigue-Fracture Tail Implementation Plan

> REQUIRED SUB-SKILL: superpowers:executing-plans. Steps use `- [ ]`.

**Goal:** Opt-in `FatigueLoss` mechanism in V2 — bilinear Su-N + Goodman → Miner's D → preload cliff at D≥1 — so V2 can express bolt fatigue fracture (Yang2021, Li2022ti).

**Architecture:** Self-contained `LossMechanism` + `sun_life()` helper + `SlowState.D_fatigue` + `JointMaterial` fatigue params (default-inert). Spec: `docs/superpowers/specs/2026-07-08-fatigue-fracture-tail-design.md`.

## Global Constraints
- Default-inert: `fatigue_enabled=False` → `FatigueLoss.rate` returns zero, bit-identical (test proves).
- Cliff `dE=0` (phenomenological); pre-fracture cycles conserve.
- Su-N constants per-material (provenance), Yang M16 defaults. utf-8, ast syntax-check after edits.

---

### Task 1: fields + sun_life + FatigueLoss (TDD)

**Files:** Modify `src/.../dynamic_stiffness_analyzer.py` (SlowState ~279, JointMaterial after `couple_famp_slip`, new `sun_life`+`FatigueLoss` after `ThreadFrettingLoss`, losses list ~1042). Test: `tests/test_fatigue_tail.py`.

**Interfaces — Produces:** `sun_life(sigma_ar, mat) -> float`; `FatigueLoss` (name="fatigue"); `SlowState.D_fatigue`; `JointMaterial.{fatigue_enabled, fat_Kt, fat_sigma_uts, fat_sigma_knee, fat_C1, fat_m1, fat_C2, fat_m2, fat_sigma_endurance, fatigue_residual_frac}`.

- [ ] **Step 1: Failing tests**
```python
import numpy as np, pytest
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    FatigueLoss, sun_life)

def _geom(grip_mm=30.0):
    return JointGeometry(A_s=84.3e-6, L_eff=grip_mm*1e-3, d_2=10.86e-3,
                         pitch=1.75e-3, r_bearing=9e-3, A_contact=117.6e-6)

def test_defaults_inert():
    m=JointMaterial()
    assert m.fatigue_enabled is False and m.fat_Kt==3.5 and m.fatigue_residual_frac==0.0
    assert m.D_fatigue if False else SlowState(F_0=1.0).D_fatigue==0.0

def test_sun_life_bilinear_and_endurance():
    m=JointMaterial()
    assert sun_life(5e6, m)==float("inf")                      # below endurance
    hi=sun_life(200e6,m); lo=sun_life(80e6,m)
    assert 0<hi<lo                                             # higher stress -> shorter life

def test_fatigue_off_is_zero():
    r=FatigueLoss().rate(SlowState(F_0=2e4,F_0_init=2e4),_geom(),JointMaterial(),
                         10e3,0.0,30.0,1)
    assert r["dF_0"]==0.0 and r["dE_dissipated"]==0.0 and r["ds"]=={}

def test_fatigue_cliff_fires():
    # tiny knee/C so N_f small -> D crosses 1 fast -> cliff drops F_0
    m=JointMaterial(fatigue_enabled=True, fat_C1=1e3, fat_m1=1.0, fat_sigma_endurance=1.0)
    ana=DynamicStiffnessAnalyzer(_geom(), m, 20e3)
    fired=False
    for _ in range(500):
        ana.step_cycle(10e3,0.0,30.0)
        if ana.state.F_0<=1.0: fired=True; break
    assert fired and ana.state.D_fatigue>=1.0
```
- [ ] **Step 2: run → fail** (ImportError).
- [ ] **Step 3: implement** `sun_life` + `FatigueLoss` + fields + register (code in spec §2-3).
- [ ] **Step 4: run → pass.**
- [ ] **Step 5: bit-identical guard** — a multi-cycle run with all-default == explicit `fatigue_enabled=False`; then run the broad V2 suite green.
- [ ] **Step 6: commit** `feat(engine): FatigueLoss opt-in fatigue-fracture cliff (default-inert)`

---

### Task 2: validation harness (`New_Theory/fatigue_tail.py`)

- [ ] **Step 1:** Load Yang2021 + Li2022ti CSVs. For each, run V2 axial force-mode with `fatigue_enabled=True`; sweep the Su-N level (e.g. scale `fat_C1`) to place the cliff at the observed N_fracture (represent). Report pre-fracture MAE + cliff cycle vs data.
- [ ] **Step 2:** Falsification-test — with handbook Yang defaults (no refit), report N_fracture_model / N_fracture_data ratio per case. Honest AS-IS (likely 2-10x).
- [ ] **Step 3: commit** `feat(fatigue): Yang2021+Li2022ti validation (represent + falsification-predict)`

---

### Task 3: verdict + finish

- [ ] **Step 1:** `MODEL_LEGITIMACY.md` §4.13 AS-IS verdict (form represents cliff; Su-N per-material; predict-ratio honest; energetics phenomenological).
- [ ] **Step 2:** full V2 suite green; commit; finishing-a-development-branch (merge/PR/keep/discard).

## Self-Review
- Fields/signatures consistent spec↔plan↔tests (`sun_life(sigma_ar, mat)`, `FatigueLoss.rate(...)`, `D_fatigue`). ✓
- No placeholders; real code in steps. ✓
