# Slip-Regime (k_tr) Fix — Design (2026-07-05)

**Status:** design (brainstormed 2026-07-05). Terminal step → writing-plans.
**Decision:** build **all three layers, most robust, OPT-IN** (structural bending `k_tr` + calibration + Mindlin micro-fretting). Canonical re-fit is a **separate gated decision**.

---

## 1. Problem

The predictive-damage-trigger falsification (`MODEL_LEGITIMACY.md` §4.8, 2026-07-05)
pinned the missing form: the model has **essentially no partial-slip regime**. In
disp-mode `slip = max(0, δ − F_slip/k_tr)` with `k_tr = 0.3·k_j_init = 1.2e9 N/m`
(a fraction of the **axial** joint stiffness `k_j_init=4e9`). That gives a gross-slip
onset `δ_t = F_slip/k_tr ≈ 0.001–0.02 mm` — so with δ = 0.25–2 mm **every case is full
gross slip** (`slip ≈ δ`). The library data (controlled amplitude sweeps: Lu M8
0.25mm→plateau / 0.5→collapse; Liu M16; Yang M10) shows the real partial→gross
transition is at `δ_t ~ 0.3 mm`. So the model over-predicts loosening for the plateau
cases and cannot distinguish plateau from collapse.

## 2. Diagnosis (grounded)

`δ_t = F_slip/k_tr`, `F_slip = 0.46·μ·F0` (Pai–Hess). To get `δ_t ~ 0.3 mm` at
`F_slip ~ 3450 N` (M16, 50 kN) needs **`k_tr ~ 1e7 N/m`** — the current `1.2e9` is
**~100× too stiff**. Two scales must not be conflated:

- **Macro (sets δ_t, the regime switch):** the **structural transverse stiffness** the
  whole joint accommodates before gross sliding. **Bolt bending** dominates:
  `k_tr ≈ c·E·I/L³` (I = πd⁴/64, L ≈ grip). Cantilever `3EI/L³ ≈ 1.5e7` (M16, L=50mm)
  → `δ_t ≈ 0.23 mm` — the right scale (bolt *shear* `G·A_s/L ≈ 2.4e8` is 20× too stiff;
  Mindlin *contact* `8·G·a ≈ 7e9` is ~600× too stiff — both wrong for the macro δ_t).
- **Micro (fretting wear inside the contact):** the Mindlin edge micro-slip (µm-scale),
  present even in partial slip — this WEARS but drives ~no net loosening.

**Unification:** `δ_t = F_slip/k_tr ∝ F0·L³/(E·d⁴)` predicts the observed dependences:
higher F0 → larger δ_t (sobretorque plateaus; low-F0 Lu collapses at the same δ); and
**thicker grip → longer L → softer k_tr → larger δ_t → plateau** — which is exactly the
§4.8 item-10 member-stiffness mode (Rousseau t10 collapses / t14 plateaus). **One form
subsumes the amplitude, preload, AND member-stiffness separators.**

## 3. Design (three layers, opt-in)

### 3.1 Layer 1 — structural bending `k_tr` (the macro δ_t)
Replace `k_tr = 0.3·k_j_init` (in `resolve_transverse_slip`) with a transverse
**bending** stiffness of the clamped bolt:
```
k_tr = c_bend · E · I / L_eff³,   I = π·d⁴/64,   L_eff ≈ grip
δ_t  = F_slip / k_tr = 0.46·μ·F0 / (c_bend·E·I/L³)     (∝ F0·L³/(E·d⁴))
```
Per-rig by construction (scales with `d`, `L_eff`). `c_bend` = a boundary/member
factor (3 cantilever … 12 fixed-fixed) — calibrated (Layer 2). `slip = max(0, δ − δ_t)`
unchanged in structure; only the stiffness is now physical.

### 3.2 Layer 2 — calibrated boundary/compliance factor
`c_bend` (and any member-compliance-in-series correction) is **calibrated to the
amplitude-sweep transitions** (Lu M8 0.25→0.5, Liu M16, Yang M10, Rousseau t10/t14) —
one interpretable factor pinning where partial→gross flips. Provenance: the sweep set;
physics-first (a boundary condition, ~1, not a free curve-knob).

### 3.3 Layer 3 — Mindlin micro-fretting (partial-slip wear, no loosening)
In **partial slip** (`δ < δ_t`): the contact still has edge micro-slip that **dissipates
and WEARS** (classic fretting) but drives **~no net loosening**. In **gross slip**
(`δ > δ_t`): full sliding → wear **and** loosening. So the two regimes differ in *what*
the slip drives, not just its magnitude: partial → a small fretting-wear dose, no
rotational loosening; gross → both. (This is why plateaus can still show surface damage
without losing preload.) Implemented as a partial-regime micro-slip term feeding wear
(and the damage dose) but gated OUT of the rotational-loosening `dF_0`.

## 4. Opt-in & backward-compat (this is FOUNDATIONAL)

Every slip-driven mechanism (wear, rotational loosening, conformation `W_conf`, the
damage dose `W_slip_acc`, `slip_onset`) sees this slip. The **âncora interna canonical calibration
was fitted with `δ_t≈0` (always gross slip)** — so a correct δ_t **shifts the canonical
fit** (plateau cases stop over-loosening; sobretorque may plateau via partial slip). To
avoid silently invalidating the canonical block:

- **Opt-in flag / sentinel:** default reproduces the current `k_tr = 0.3·k_j_init`
  (δ_t≈0, gross-slip-always) — every existing run/fit **bit-unchanged**. The corrected
  regime is enabled explicitly (e.g. `k_tr_mode="bending"` or `c_bend>0`).
- **Re-founding the canonical calibration on the corrected regime is a SEPARATE GATED
  decision** (like the Stage-B / conformation-adoption gates) — taken only after the
  corrected regime is validated standalone.

## 5. Interactions (examine in validation, don't pre-judge)
- **Damage trigger (falsified):** a correct partial/gross regime may **rescue** it —
  partial-slip plateaus → ~no gross-slip dose → no damage; gross-slip collapses → dose →
  damage. Re-run `--damage-trigger` on the corrected regime as part of validation.
- **Conformation:** high-F0 sobretorque may plateau via *partial slip* under the
  corrected δ_t — possibly **overlapping** what conformation captured. Flag if the
  corrected regime reduces the need for `W_conf_ref` on sobretorque (a consolidation
  lead, not this spec's job).
- **Member-stiffness (item 10):** the corrected `k_tr(L)` should improve Rousseau
  t10/t14 — check it.

## 6. Validation & success criteria
Standalone (opt-in on, canonical untouched), on the transfer library + the amplitude
sweeps:
1. **Regime accuracy:** partial slip (`slip≈0`) on the plateau cases, gross on the
   collapse cases — a confusion matrix; the controlled sweeps (Lu/Liu/Yang) flip at the
   right δ.
2. **Plateau over-prediction fixed:** the §4.8 plateau cases (Yang/Liu) stop grinding to
   `final_pred≈0` (the base-model over-loosening that the falsification exposed).
3. **Damage-trigger rescue (bonus):** re-run `--damage-trigger`; does the corrected
   regime let a `W_crit` separate collapse from plateau now?
4. **Pre-registered thresholds** (frozen in the plan): regime-accuracy target + a
   plateau-MAE improvement bar; recorded AS IS.

## 7. New constants & provenance
| Constant | Meaning | Default | Provenance |
|---|---|---|---|
| `k_tr_mode` | `"axial_frac"` (current) \| `"bending"` (corrected) | `"axial_frac"` (backward-compat) | design flag |
| `c_bend` | boundary/member factor in `c·E·I/L³` | ~3 (cantilever start) | calibrated to amplitude sweeps (Layer 2) |
| partial-slip fretting-wear coeff | micro-slip wear in the partial regime | 0 = off | Mindlin/fretting lit + calibration |

`E`, `I` (from `d`), `L_eff` (grip) are inputs (geometry/material), not knobs.

## 8. Open questions (for the plan / the professor)
1. **`c_bend` single value or a real series model** (bolt bending + member compliance)?
   Start with one calibrated `c_bend`; add member compliance only if the sweeps demand.
2. **Partial-slip fretting-wear magnitude** — does the data constrain it, or keep it a
   documented small term? (May tie to the strand-3 Fouvry energy-density.)
3. **Canonical re-fit** — after validation, is re-founding the calibration on the
   corrected regime in scope, or a later campaign? (Gated decision.)

## 9. Phasing (for writing-plans)
- **Phase A — structural `k_tr` (opt-in):** `k_tr_mode="bending"` + `c_bend` in
  `resolve_transverse_slip`; default `"axial_frac"` (backward-compat); tests.
- **Phase B — calibrate `c_bend`:** fit to the amplitude-sweep transitions; regime
  accuracy.
- **Phase C — Mindlin partial-slip wear:** partial-regime micro-slip → wear (not
  loosening); tests.
- **Phase D — validation:** transfer + sweeps + damage-trigger rescue, pre-registered,
  AS IS. (Canonical re-fit = separate gated decision, NOT in this plan.)
