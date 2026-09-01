# Slip-Regime Threshold (Cattaneo–Mindlin) — Design Spec

**Date:** 2026-07-07 · **Status:** designed (brainstorm 2026-07-07), opt-in/default-inert
**Closes:** roadmap #10 (member-stiffness rotation-onset) · steepens #9/#3 axial preload sensitivity
**Author:** Prof. L. R. R. da Silva

---

## 1. Motivation

Two validated-report cases fail for the *same* absent physics — a partial↔gross
slip regime threshold:

- **Rousseau 2025 (member stiffness):** data spans **10×** across plate thickness
  (t10 final 0.088 → t14 0.903). The shipped model is thickness-blind (baseline
  0.203/0.304/0.388). The spread is a **grip-dependent rotation-onset instability**:
  short/stiff grips overshoot the friction capacity → gross slip → runaway; long/
  compliant grips stay stuck. `MODEL_LEGITIMACY.md` §4.8 falsified `k_j`-scaling.
- **Liu 2017 (axial):** `d(final)/dP₀` is ~5× too flat (model 5.6e-6 vs data 2.6e-5
  /N). Higher preload → larger stick zone → less fretting → retains more; the axial
  fretting channel has **no pressure dependence**.

The engine already carries most of the scaffolding, so this is *unify + complete*,
not *invent*:

- `loosening_slip_gate` (line ~478) computes a **smooth** gross-slip fraction
  `slip/(slip+δ_t)` with `δ_t = F_slip/k_tr` — but smooth is exactly the "Rousseau
  too sharp" wall the earlier δ_t separator hit.
- `k_tr_transverse` (line ~464) `"bending"` mode already gives the grip lever
  `c_bend·E·I/L³ ∝ 1/L³`.
- `WearLoss` / `ThreadFrettingLoss` have **no** regime gate — no stick/pressure
  dependence.

## 2. The ratio

Per channel, per cycle:

```
r = Q / (μ · F₀ · κ)          (demanded tangential load / friction capacity)
```

- **Q (demanded tangential load):**
  - transverse loosening & bearing wear: `Q_tr` from the imposed stroke through the
    transverse stiffness (disp-mode `k_tr·δ_imposed`; force-mode `F_amp·sinθ`).
  - thread-flank fretting (axial): `Q_ax = F_amp·|cosθ|`.
- **μ:** `mu_thread` at the flank, `mu_bearing_eff(state,mat)` at the bearing.
- **κ = `slip_capacity_coeff`:** the one per-channel geometric scaling (thread
  engagement / bearing radius) that places the transition. **Provenance-able**
  (thread geometry), not a free knob. For loosening κ is *fixed* by the existing
  `SLIP_ONSET_PAI_HESS` constant (see §4), so the only genuinely new κ is the
  wear/fretting capacity.

The transition **center is pinned at the Coulomb condition r = 1** (physics); only
the *width* (sharpness) is a rig constant.

## 3. Two laws (the "two-law split")

The two channel families have genuinely different physics, so they get different
laws of the same `r`:

**(a) Gross-slip onset — loosening.** Ratcheting/backing-off requires gross slip:

```
g_gross(r) = max(0, 1 − 1/r) ** k          (k = slip_regime_sharpness)
```

- `r ≤ 1` → 0 (stick core holds, no backing-off).
- `r → ∞` → 1 (deep gross slip = full ratcheting).
- **k = 1 reduces exactly to today's `slip/(slip+δ_t)` gross fraction**
  (`max(0,1−1/r) = slip/(slip+δ_t)` since `r = δ_imposed/δ_t`), so this is a
  *sharpening exponent* on the existing physics — continuity guaranteed. k > 1
  suppresses moderate gross slip so only deep gross slip (thin grips) loosens.

**(b) Partial-slip energy — wear + thread-fretting.** These dissipate in partial
slip too (the slip annulus), so a smooth Cattaneo–Mindlin energy fraction:

```
g_partial(r) = 1 − (1 − min(max(r,0),1)) ** m      (m = partial_slip_exp, ≈1.5)
             = 1 for r ≥ 1
```

- nonzero and graded for `0 < r < 1` → higher F₀ → lower r → lower g → less
  fretting (the Liu 2017 slope).
- `r ≥ 1` → 1 (gross slip, F₀-independent stroke energy).

Both laws multiply **`dF_0` only, never `dE`** — the same "dF_0 yes, dE no"
convention as `slip_onset_gate` / `conformation_gate` / damage amplification
(micro-slip still dissipates heat and feeds `W_slip_acc`).

## 4. Wiring & the master switch

One new master switch on `JointMaterial`:

```
slip_regime_mode: str = "off"        # "off" | "cattaneo_mindlin"
slip_regime_sharpness: float = 1.0   # k in g_gross  (1.0 == current gross fraction)
slip_capacity_coeff: float = 1.0     # κ for wear/fretting g_partial
partial_slip_exp: float = 1.5        # m in g_partial
```

When `slip_regime_mode == "cattaneo_mindlin"`:

1. **`loosening_slip_gate`** gains a precedence branch (checked *before* the
   `loosening_slip_coupling` branches): returns `g_gross(r_loose)` with
   `r_loose = (slip_amp + δ_t)/δ_t = 1 + slip_amp/δ_t`, `δ_t = F_slip_transverse/k_tr`.
   (Reuses `F_slip_transverse` & `k_tr_transverse`; force-mode `slip_amp None` → 1.0,
   backward-compat.) So κ_loose is implicitly `SLIP_ONSET_PAI_HESS` — no new knob.
2. **`WearLoss.rate`**: multiply `d_wear` by `partial_slip_gate(r_wear)`,
   `r_wear = Q_tr/(mu_bearing_eff·F₀·κ)`.
3. **`ThreadFrettingLoss.rate`**: multiply `d_fret` by `partial_slip_gate(r_fret)`,
   `r_fret = F_ax/(mu_thread·F₀·κ)`.

When `slip_regime_mode == "off"` (default): `loosening_slip_gate` keeps its current
logic; a standalone `partial_slip_gate` returns **1.0** exactly ⇒ **bit-identical**
to today's engine. `slip_regime_mode` takes precedence over `loosening_slip_coupling`
when active (documented).

**New standalone function** `partial_slip_gate(state, geom, mat, F_amp, theta_load,
channel, slip_amp)` → matches the composable-gate pattern; `channel ∈ {"wear",
"fret"}` selects Q and μ. Returns 1.0 when `slip_regime_mode != "cattaneo_mindlin"`.

## 5. Composition with existing gates

Orthogonal and stacking — the onset *starts* the runaway, the floor *stops* it:

| gate | role | when |
|---|---|---|
| `slip_onset_gate` | Jiang stage-I incubation | opens 0→1 on `W_slip_acc` |
| `conformation_gate` | high-pressure conformation arrest | closes 1→0 on `W_conf` |
| **`g_gross` (this spec)** | gross-slip onset for loosening | 0 below r=1, →1 above |
| `self_locking_gate` | residual floor `F_min` | closes as F₀→F_min |
| **`g_partial` (this spec)** | partial-slip micro-wear/fret | graded below r=1 |

No double-gating: `g_gross` *replaces* the `loosening_slip_coupling` fraction (mode
dispatch), it does not stack on it.

## 6. Provenance discipline

- `c_bend`: from beam-bending end-restraint (`3·EI/L³` cantilever … `12·EI/L³`
  guided-clamped) — **computed, not fitted** at 0.30. Sets where `r_loose` crosses 1
  across grips.
- `κ` (`slip_capacity_coeff`): thread-engagement / bearing geometry (O(5–10) for the
  flank so `r_fret` straddles 1 across the Liu 2017 P₀ sweep).
- `k` (`slip_regime_sharpness`): per-rig transition width, O(2–8).
- Center pinned at r = 1 (Coulomb). `μ` per-pair.

## 7. Validation (success bar = "right shape, both cases")

Structural first; MAE is a consequence.

- **Rousseau** (`New_Theory/slip_regime_rousseau.py`): with `slip_regime_mode=
  "cattaneo_mindlin"`, `k_tr_mode="bending"`, `loose_torsion_mode="bolt_torsion"`,
  `loose_arrest_floor≈0.08`, `c_bend` from beam theory — **t10 collapses, t14
  survives, monotone spread** across thickness (the model can *express* the 10×).
- **Liu 2017** (`New_Theory/slip_regime_axial.py`): `d(final)/dP₀` steepens from
  5.6e-6 toward the data's 2.6e-5 /N, with κ from thread geometry.
- **No regression** (standing constraint): a test asserts `slip_regime_mode="off"`
  is bit-identical; UFU shear, axial zero-refit (`calibrate_axial`), and
  re-tightening (`validate_galling`) re-run green.
- **Verdict** logged AS-IS in `MODEL_LEGITIMACY.md` §4.12 (validated capability vs
  adopted fix, per the project doctrine).

## 8. Paired in-scope (same physics)

- **`F_amp ↔ δ_amp` coupling (#4):** in disp-mode, cap the slip-driving force at the
  Coulomb limit `μ·F₀` in gross slip (`r ≥ 1`). Completes the slip-regime; separate
  task, same plan.
- **Rousseau emb-level provenance:** thick-grip t14 over-loses because embedding is
  too deep (data 10% vs model 61%). Use the finer-Rz `emb_depth` class for the steel
  members (input provenance, not a fit). Needed *with* the onset form to fully close
  Rousseau.

## 9. Out of scope (own campaigns / later)

Fouvry anchor for `K_archard`/`k_thread_fret`; axial viscous bookkeeping;
identifiability of {k, κ, c_bend}; polymer/gasket creep; damage-collapse
conservation (#6); fatigue-fracture tail; thermal ΔT; `W_conf_ref` lab anchor;
Stage B tuner removal (#8). Tracked separately.
