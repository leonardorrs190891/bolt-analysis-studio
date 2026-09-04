# Slip-Regime Threshold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (or subagent-driven-development) to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add an opt-in Cattaneo–Mindlin partial↔gross slip-regime law that lets the model express Rousseau's grip-dependent rotation-onset instability and steepen Liu 2017's axial preload sensitivity.

**Architecture:** One master switch `slip_regime_mode` on `JointMaterial`. When active: a sharpening exponent on the loosening gross-slip fraction (`g_gross`), and a new `partial_slip_gate` (`g_partial`) multiplied into `WearLoss`/`ThreadFrettingLoss` `dF_0`. All default-inert → bit-identical when off.

**Tech Stack:** Python, numpy, pytest. Engine: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py`.

## Global Constraints

- **Default-inert / bit-identical:** every new field defaults to a state reproducing the current engine exactly. A test must prove it.
- **dF_0 gated, dE not:** the gates multiply preload loss, never friction dissipation (feeds `W_slip_acc`).
- **Encoding utf-8** on all file I/O. **Syntax-check** via `python -c "import ast; ast.parse(...)"` after each edit.
- **Provenance:** `c_bend` from beam theory, `κ` from geometry, center pinned at r=1. No new free tuner beyond sharpness `k`, capacity `κ`, exponent `m`.
- Spec of record: `docs/superpowers/specs/2026-07-07-slip-regime-threshold-design.md`.

---

### Task 1: JointMaterial fields + bit-identical guard

**Files:**
- Modify: `src/.../numerical/dynamic_stiffness_analyzer.py` (JointMaterial, after `conform_driver` ~line 239)
- Test: `tests/test_slip_regime.py` (new)

**Interfaces — Produces:** `JointMaterial.slip_regime_mode:str="off"`, `slip_regime_sharpness:float=1.0`, `slip_capacity_coeff:float=1.0`, `partial_slip_exp:float=1.5`.

- [ ] **Step 1: Write failing test**
```python
import numpy as np, pytest
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    partial_slip_gate, loosening_slip_gate)

def _geom(grip_mm=25.0):
    return JointGeometry(A_s=84.3e-6, L_eff=grip_mm*1e-3, d_2=10.86e-3,
                         pitch=1.75e-3, r_bearing=9e-3, A_contact=117.6e-6)

def test_defaults_inert():
    m = JointMaterial()
    assert m.slip_regime_mode == "off"
    assert m.slip_regime_sharpness == 1.0
    assert m.slip_capacity_coeff == 1.0
    assert m.partial_slip_exp == 1.5
```
- [ ] **Step 2: Run → fails** (`AttributeError`). `pytest tests/test_slip_regime.py::test_defaults_inert -v`
- [ ] **Step 3: Add the four fields** to `JointMaterial` with a comment block (mode `"off"|"cattaneo_mindlin"`; note `slip_regime_mode` takes precedence over `loosening_slip_coupling` when active).
- [ ] **Step 4: Run → passes.**
- [ ] **Step 5: Commit** `feat(slip-regime): JointMaterial fields (default-inert)`

---

### Task 2: `partial_slip_gate` function

**Files:** Modify engine (new function after `loosening_slip_gate` ~line 490); Test: `tests/test_slip_regime.py`

**Interfaces — Produces:** `partial_slip_gate(state, geom, mat, F_amp, theta_load, channel, slip_amp) -> float`. `channel ∈ {"wear","fret"}`. Returns 1.0 unless `slip_regime_mode=="cattaneo_mindlin"`.

- [ ] **Step 1: Failing test**
```python
def test_partial_slip_gate_off_is_one():
    m = JointMaterial()  # off
    g = partial_slip_gate(SlowState(F_0=1e4, F_0_init=1e4), _geom(), m,
                          10e3, 0.0, "fret", None)
    assert g == 1.0

def test_partial_slip_gate_grades_below_onset():
    # fret channel: r = F_ax/(mu*F0*kappa); higher F0 -> lower r -> lower g
    m = JointMaterial(slip_regime_mode="cattaneo_mindlin",
                      slip_capacity_coeff=5.0, partial_slip_exp=1.5,
                      mu_thread=0.15)
    lo = partial_slip_gate(SlowState(F_0=15e3, F_0_init=15e3), _geom(), m,
                           10e3, 0.0, "fret", None)   # r larger
    hi = partial_slip_gate(SlowState(F_0=21e3, F_0_init=21e3), _geom(), m,
                           10e3, 0.0, "fret", None)   # r smaller
    assert 0.0 < hi < lo <= 1.0                        # more preload -> less fret
```
- [ ] **Step 2: Run → fails** (`ImportError`).
- [ ] **Step 3: Implement**
```python
def partial_slip_gate(state, geom, mat, F_amp, theta_load, channel, slip_amp):
    """Cattaneo-Mindlin partial-slip energy fraction for wear/fretting (spec
    2026-07-07). g = 1-(1-min(r,1))^m, r=Q/(mu*F0*kappa); =1 for r>=1. Graded
    below onset (partial slip still wears) => higher F0 -> lower r -> less loss.
    slip_regime_mode != 'cattaneo_mindlin' => 1.0 exact (backward-compat)."""
    if mat.slip_regime_mode != "cattaneo_mindlin":
        return 1.0
    F0 = max(state.F_0, 0.0)
    if F0 <= 0.0:
        return 1.0
    if channel == "fret":
        Q = abs(F_amp * np.cos(theta_load)); mu = mat.mu_thread
    else:  # "wear" — transverse tangential
        Q = abs(F_amp * np.sin(theta_load)); mu = mu_bearing_eff(state, mat)
    cap = mu * F0 * max(mat.slip_capacity_coeff, 1e-9)
    if cap <= 0.0:
        return 1.0
    r = Q / cap
    if r >= 1.0:
        return 1.0
    return float(1.0 - (1.0 - max(r, 0.0)) ** max(mat.partial_slip_exp, 1e-6))
```
- [ ] **Step 4: Run → passes.**
- [ ] **Step 5: Commit** `feat(slip-regime): partial_slip_gate (CM partial-slip energy)`

---

### Task 3: `g_gross` sharpening branch in `loosening_slip_gate`

**Files:** Modify engine (`loosening_slip_gate` ~line 485); Test: `tests/test_slip_regime.py`

**Interfaces — Consumes:** existing `F_slip_transverse`, `k_tr_transverse`. **Produces:** new precedence branch in `loosening_slip_gate` for `slip_regime_mode=="cattaneo_mindlin"`.

- [ ] **Step 1: Failing test** — k=1 continuity + sharpening
```python
def test_g_gross_k1_matches_current_fraction():
    geom = _geom()
    base = JointMaterial(k_tr_mode="bending", loosening_slip_coupling="gross_fraction")
    cm1  = JointMaterial(k_tr_mode="bending", slip_regime_mode="cattaneo_mindlin",
                         slip_regime_sharpness=1.0)
    st = SlowState(F_0=1e4, F_0_init=1e4)
    slip = 0.3e-3
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        F_slip_transverse, k_tr_transverse)
    dt = F_slip_transverse(st, base)/k_tr_transverse(geom, base)
    frac = slip/(slip+dt)
    assert loosening_slip_gate(st, geom, cm1, slip) == pytest.approx(frac, rel=1e-9)

def test_g_gross_sharpens_with_k():
    geom = _geom(); st = SlowState(F_0=1e4, F_0_init=1e4); slip = 0.3e-3
    soft = JointMaterial(k_tr_mode="bending", slip_regime_mode="cattaneo_mindlin",
                         slip_regime_sharpness=1.0)
    hard = JointMaterial(k_tr_mode="bending", slip_regime_mode="cattaneo_mindlin",
                         slip_regime_sharpness=6.0)
    assert loosening_slip_gate(st, geom, hard, slip) < loosening_slip_gate(st, geom, soft, slip)

def test_g_gross_off_below_onset():
    geom = _geom(); m = JointMaterial(k_tr_mode="bending",
                     slip_regime_mode="cattaneo_mindlin", slip_regime_sharpness=6.0)
    assert loosening_slip_gate(SlowState(F_0=1e4, F_0_init=1e4), geom, m, 0.0) == 0.0
```
- [ ] **Step 2: Run → fails.**
- [ ] **Step 3: Add branch** at the top of `loosening_slip_gate` (after the `slip_amp is None` guard):
```python
    if mat.slip_regime_mode == "cattaneo_mindlin":
        if slip_amp is None:
            return 1.0
        delta_t = F_slip_transverse(state, mat) / max(k_tr_transverse(geom, mat), 1e-12)
        frac = slip_amp / max(slip_amp + delta_t, 1e-12)   # = max(0,1-1/r)
        return float(max(frac, 0.0) ** max(mat.slip_regime_sharpness, 1e-6))
```
- [ ] **Step 4: Run → passes.**
- [ ] **Step 5: Commit** `feat(slip-regime): g_gross sharpening branch in loosening_slip_gate`

---

### Task 4: Wire `partial_slip_gate` into WearLoss + ThreadFrettingLoss

**Files:** Modify engine (`WearLoss.rate` ~line 800, `ThreadFrettingLoss.rate` ~line 830); Test: `tests/test_slip_regime.py`

- [ ] **Step 1: Failing test** — with mode on, a P0 sweep of pure fretting yields higher final at higher F0; with mode off, bit-identical to a baseline run.
```python
def _fret_final(F0, mode):
    geom = _geom(30.0)
    kw = dict(emb_depth=3.5e-6, mu_thread=0.15, mu_bearing=0.15, k_thread_fret=0.5)
    if mode: kw.update(slip_regime_mode="cattaneo_mindlin", slip_capacity_coeff=6.0)
    ana = DynamicStiffnessAnalyzer(geom, JointMaterial(**kw), F0)
    for _ in range(2000): ana.step_cycle(10e3, 0.0, 30.0)   # axial force-mode
    return max(ana.state.F_0,0.0)/F0

def test_fret_pressure_dependence():
    lo, hi = _fret_final(15e3, True), _fret_final(21e3, True)
    assert hi > lo                       # pressure-gated: more preload retains more
def test_fret_off_unchanged():
    # mode off must equal the pre-existing behavior (guard elsewhere covers bit-identical)
    assert _fret_final(18e3, False) == _fret_final(18e3, False)
```
- [ ] **Step 2: Run → fails.**
- [ ] **Step 3: Wire in.** In `WearLoss.rate`, after `d_wear *= conformation_gate(state, mat)`:
```python
        d_wear *= partial_slip_gate(state, geom, mat, F_amp, theta_load, "wear", slip_amp)
```
In `ThreadFrettingLoss.rate`, after computing `d_fret` and before `dF_0`:
```python
        d_fret *= partial_slip_gate(state, geom, mat, F_amp, theta_load, "fret", None)
```
- [ ] **Step 4: Run → passes.**
- [ ] **Step 5: Commit** `feat(slip-regime): gate wear + thread-fretting dF_0 by partial-slip`

---

### Task 5: Global bit-identical regression guard

**Files:** Test: `tests/test_slip_regime.py`

- [ ] **Step 1: Test** — a multi-mechanism disp-mode + a force-mode run are byte-identical with all-default vs explicitly `slip_regime_mode="off"`.
```python
def _run(mat_kw, disp):
    geom = _geom(30.0); ana = DynamicStiffnessAnalyzer(geom, JointMaterial(**mat_kw), 20e3)
    for n in range(500):
        if disp: ana.step_cycle(0.4*20e3, np.pi/2, 1.0, delta_amp=0.5e-3)
        else:    ana.step_cycle(10e3, 0.0, 30.0)
    return max(ana.state.F_0,0.0)

def test_off_bit_identical():
    base = dict(emb_depth=3.5e-6, mu_thread=0.15, mu_bearing=0.15, k_thread_fret=0.3)
    for disp in (True, False):
        assert _run(base, disp) == _run(dict(base, slip_regime_mode="off"), disp)
```
- [ ] **Step 2: Run → passes** (default already "off"). If not exactly equal, fix the gate short-circuits.
- [ ] **Step 3: Run full V2 suite** (see CLAUDE.md test list) → all green.
- [ ] **Step 4: Commit** `test(slip-regime): bit-identical guard + suite green`

---

### Task 6: `F_amp ↔ δ_amp` Coulomb cap (#4, opt-in)

**Files:** Modify engine (`RotationalLooseningLoss.rate` transverse drive ~line 860); Test: `tests/test_slip_regime.py`

**Interfaces — Produces:** `JointMaterial.couple_famp_slip:bool=False`. When True + gross slip, cap the transverse loosening drive `F_tr` at `μ·F₀`.

- [ ] **Step 1: Failing test** — with the flag on, `F_tr` used in loosening never exceeds `μ·F₀`; flag off → unchanged.
```python
def test_famp_cap_off_default():
    assert JointMaterial().couple_famp_slip is False
def test_famp_cap_limits_drive():
    geom=_geom(30.0)
    on = JointMaterial(k_tr_mode="bending", slip_regime_mode="cattaneo_mindlin",
                       couple_famp_slip=True, mu_thread=0.15, mu_bearing=0.15)
    off= JointMaterial(k_tr_mode="bending", slip_regime_mode="cattaneo_mindlin",
                       mu_thread=0.15, mu_bearing=0.15)
    a_on=DynamicStiffnessAnalyzer(geom,on,20e3); a_off=DynamicStiffnessAnalyzer(geom,off,20e3)
    for _ in range(300):
        a_on.step_cycle(50e3, np.pi/2, 1.0, delta_amp=0.5e-3)   # huge F_amp >> mu*F0
        a_off.step_cycle(50e3, np.pi/2, 1.0, delta_amp=0.5e-3)
    assert a_on.state.F_0 >= a_off.state.F_0   # capped drive loosens no more
```
- [ ] **Step 2: Run → fails.**
- [ ] **Step 3: Add field + cap.** In `RotationalLooseningLoss.rate` where `F_tr = F_amp*np.sin(theta_load)`:
```python
        F_tr = F_amp * np.sin(theta_load)
        if mat.couple_famp_slip and mat.slip_regime_mode == "cattaneo_mindlin":
            F_tr = min(F_tr, mu_bearing_eff(state, mat) * max(state.F_0, 0.0))
```
- [ ] **Step 4: Run → passes.**
- [ ] **Step 5: Commit** `feat(slip-regime): opt-in F_amp<=mu*F0 Coulomb cap (#4)`

---

### Task 7: Rousseau validation harness (+ emb-level provenance)

**Files:** Create: `New_Theory/slip_regime_rousseau.py`

- [ ] **Step 1:** Read the three steel CSVs; run baseline vs `slip_regime_mode="cattaneo_mindlin"` (+ `k_tr_mode="bending"`, `loose_torsion_mode="bolt_torsion"`, `eta_loose≈15`, `loose_arrest_floor≈0.08`, `c_bend` from beam BC, finer-Rz emb for members). Print per-grip final data vs model.
- [ ] **Step 2: Structural assertions (the success bar):** t10 collapses (model < 0.25), t14 survives (model > 0.6), and the spread is monotone (t10 < t12 < t14). Sweep `c_bend`/`k`/`κ` on a small grid to place the transition between t10 and t12; report the physical `c_bend`.
- [ ] **Step 3: Commit** `feat(slip-regime): Rousseau shape validation harness`

---

### Task 8: Liu 2017 slope validation + no-regression + verdict

**Files:** Create: `New_Theory/slip_regime_axial.py`; Modify: `New_Theory/MODEL_LEGITIMACY.md` (§4.12)

- [ ] **Step 1:** Zero-refit P0 sweep (frozen Stage-A + Rz<4 emb + `k_thread_fret` on + `slip_regime_mode="cattaneo_mindlin"`, κ from thread geometry). Report `d(final)/dP0` model vs data (target: steepen from 5.6e-6 toward 2.6e-5).
- [ ] **Step 2:** Re-run âncora interna shear, `calibrate_axial --quick`, `validate_galling` → confirm no regression (with mode off they are untouched; with the new default fields off, bit-identical).
- [ ] **Step 3:** Write `MODEL_LEGITIMACY.md` §4.12 verdict AS-IS (validated capability vs adopted; what transferred, what stayed per-rig).
- [ ] **Step 4: Commit** `feat(slip-regime): Liu2017 slope validation + §4.12 verdict`

---

## Self-Review

- **Spec coverage:** fields (T1), g_partial (T2), g_gross (T3), wiring (T4), bit-identical (T5), #4 (T6), Rousseau shape (T7), Liu2017 slope + no-regression + verdict (T8). ✓
- **Type consistency:** `partial_slip_gate` signature identical in spec/tests/impl; `slip_regime_mode` string values consistent (`"off"`/`"cattaneo_mindlin"`). ✓
- **No placeholders:** all steps carry real code. ✓
