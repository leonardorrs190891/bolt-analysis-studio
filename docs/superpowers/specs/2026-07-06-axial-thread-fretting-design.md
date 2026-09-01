# Axial Thread-Flank Fretting Loss (∝ A_F) — Design (2026-07-06)

**Goal:** Supply the missing loss *form* the axial track needs — thread-flank
fretting wear driven by the oscillating axial load amplitude — so the model
develops a non-zero `∂(final)/∂A_F` (target −2.216e-5/N, Liu2017), which is
structurally `≡ 0` today. Opt-in, default-inert, naturally silent on the
transverse library.

**Status:** design approved 2026-07-06 (brainstorm). This introduces a **new
mechanism with a new fitted per-pair constant** (the deferred "B2 refit" §4.6
named) — NOT a zero-refit gate. Canonical `shared` block never written; canonical
re-fit out of scope.

---

## 1. Motivation — the §4.6 structural falsification

The axial track (Fase 1B, `MODEL_LEGITIMACY.md` §4.6) **failed Gate B1** with a
*form* falsification, not a constant one: the V2 mechanism set contains **no loss
driven by the cyclic axial load amplitude** below the loosening onset — wear =
*transverse* slip, creep = F₀ only, embedding = amplitude-blind. So the five
Liu2017 A_F-sweep predictions are the **identical curve** (final 0.6555) →
`∂(final)/∂A_F ≡ 0` (model) vs **−2.216e-5/N** (data). No refit of frozen
constants can create A_F dependence that no mechanism carries — which is why B2
was not run; the falsification *is* the result, and it **names the missing form**:
**fretting/wear at the thread flanks under oscillating axial load, ∝ A_F**,
corroborated by Liu2017's own SEM of thread-flank wear.

This design supplies that form.

## 2. The mechanism (Approach A — Archard flank fretting, reuse `K_archard`)

A new `LossMechanism`, `ThreadFrettingLoss` (`name="thread_fretting"`), a
structural sibling of `WearLoss`, at the thread flank instead of the bearing:

```
F_ax      = F_amp * |cos(theta_load)|            # axial load amplitude component
if k_thread_fret <= 0 or F_ax <= 0 or F_0 <= 0:  return zero
s_flank   = F_ax / geom.k_b                      # bolt axial displacement amplitude
fret_dist = 4.0 * s_flank                        # per cycle (fwd+rev), as in WearLoss
d_fret    = k_thread_fret * K_archard * F_0 * fret_dist / max(hardness * A_s, 1.0)
dF_0      = -geom.k_b * d_fret
dE        = mu_thread * F_0 * fret_dist          # flank friction work
ds        = dict(delta_thread_fret = d_fret)
```

- **Driver:** `F_ax = F_amp·|cos θ|` — the axial component. For the Liu2017 axial
  cases (θ=0) `F_ax = A_F`; for the transverse library (θ=π/2) `F_ax = 0` → the
  mechanism is **identically zero** there (doubly backward-compatible).
- **Archard, reusing `K_archard` + `hardness`** (flank and bearing are the same
  material pair). The flank-slip fraction, contact area, and flank-angle→axial
  projection all fold into the single factor `k_thread_fret`.
- **Emergent clean form:** `k_b` cancels (`fret_dist ∝ 1/k_b`, `dF_0 = −k_b·d_fret`)
  ⇒ `dF_0 = −k_thread_fret·K_archard·F₀·(4·F_ax)/(hardness·A_s)`, i.e.
  `dF_0 ∝ −F₀·A_F` — exactly the negative `∂/∂A_F` the falsification demands.
- **Reference area `A_s`** (stress area, a `JointGeometry` field): a physical
  thread-scale area; its exact value folds into `k_thread_fret` on calibration.
- **Conservation:** same pattern as `WearLoss` — real friction `dE`, the extra
  preload loss balanced via `U_released`; `dF_0` and the tracked `delta_thread_fret`
  keep the ledger consistent. (The pre-existing axial force-mode viscous-bookkeeping
  caveat, §4.6, is orthogonal and unchanged; noted, not fixed here.)

**The one new constant: `k_thread_fret` (default 0.0 = OFF).** O(0.1–1), a
geometric/engagement factor; a geometry-derived value is the calibration starting
point, but it is **fit to the Liu2017 axial data** → provenance: *fitted, per-pair*
(the deferred B2). Documented as such (§5.1-class constant), not a universal.

## 3. Engine change (`dynamic_stiffness_analyzer.py`)

- **`JointMaterial` field** (near the wear fields): `k_thread_fret: float = 0.0`
  with a comment (opt-in; axial-driven flank fretting; default 0 = inert).
- **`SlowState` field** (after `delta_wear`, line 216): `delta_thread_fret: float = 0.0`.
  `as_array` (line 229) is **not** consumed and already omits `D` — leave it
  untouched; the `setattr` ds-loop (line 937) applies the new field by name.
- **New class `ThreadFrettingLoss(LossMechanism)`** after `WearLoss` (~line 718),
  body per §2.
- **Register** in `DynamicStiffnessAnalyzer.__init__` default `self.losses` list
  (lines 845–849): append `ThreadFrettingLoss()`. Default `k_thread_fret=0` keeps
  it inert, so registration is backward-compat.

## 4. Activation / backward-compatibility

- Default `k_thread_fret=0.0` → mechanism returns zeros → every existing run/fit
  **bit-identical** (hard gate).
- Axial-driven: `F_ax=0` for the transverse library (θ=π/2) → **zero contribution
  even when enabled** → the transverse work (loosening gate, conformation, staged
  calibration) is provably untouched. This is a *second* independent guarantee.
- Honors `model._v2_tuner_overrides` (numeric field, passes the type-aware filter).

## 5. Validation — pre-registered, AS IS

Harness: `calibrate_axial.py` (the §4.6 harness; Liu2017 M12 A_F + P₀ sweeps,
Li2022 M10 freq). `k_thread_fret` calibrated to the axial data (a geometry-derived
starting value, then a 1-parameter fit to the A_F gradient).

**Honesty guard (pre-registered):** `k_thread_fret` is fit to the A_F data, so the
gradient *magnitude* is partly circular. The scientific test is **representability**
— that supplying the form makes the A_F dependence *possible at all* — plus
non-regression elsewhere. **Frozen thresholds:**
- **Representability (primary):** with `k_thread_fret` calibrated, `∂(final)/∂A_F`
  is **negative** and the 5 A_F-sweep curves **separate monotonically** (today
  identical at 0.6555) — structurally impossible without the form.
- **Magnitude:** `∂(final)/∂A_F` within a **factor of ~2** of −2.216e-5/N after calibration.
- **Axial MAE:** median `MAE_pred` on the Liu2017 A_F sweep **improves** vs the
  §4.6 baseline **0.1518**.
- **P₀ gradient not wrecked:** `∂(final)/∂P₀` stays sign-correct (was +1.585e-5/N
  model vs +2.633e-5/N data, ~60%); the new mechanism (`∝ F₀·A_F`) adds F₀
  dependence, so this may shift — recorded AS IS, must not flip sign.
- **Transverse library unchanged:** `transfer_validation` median MAE **bit-identical**
  (F_ax=0 → mechanism inert) — a hard backward-compat check.

Verdict recorded vs these either way.

## 6. Testing (TDD) — `tests/test_thread_fretting.py`

- **off-by-default:** `k_thread_fret=0` → `ThreadFrettingLoss.rate` returns
  `dF_0=0, dE=0` for any axial load.
- **axial → loss ∝ A_F:** `k_thread_fret>0`, θ=0 → `dF_0 < 0`, and `dF_0` scales
  **linearly with `F_amp`** (double A_F → double `dF_0`) and with `F_0`.
- **transverse inert:** θ=π/2 → `F_ax=0` → `dF_0 = 0` even with `k_thread_fret>0`.
- **gradient nonzero end-to-end:** two short axial runs at different `A_F` (θ=0,
  `k_thread_fret>0`) give **different** final `F_0/F_0i` (today identical).
- **conservation:** `analyzer.energy.conservation_residual` does not blow up
  (stays same order as the §4.6 baseline) on an axial run with the mechanism on.
- **backward-compat sweep:** the standing V2/calibration suite passes unchanged
  (default off).

## 7. Files

| File | Change |
|---|---|
| `src/.../numerical/dynamic_stiffness_analyzer.py` | `JointMaterial.k_thread_fret`; `SlowState.delta_thread_fret`; `ThreadFrettingLoss` class; register in `self.losses` |
| `tests/test_thread_fretting.py` | new (TDD) |
| `New_Theory/calibrate_axial.py` | calibrate `k_thread_fret` to the A_F gradient; report the pre-registered metrics |
| `New_Theory/MODEL_LEGITIMACY.md` | §4.6 addendum (verdict AS IS) + §5.1 provenance line for `k_thread_fret` + changelog |

## 8. Scope / out-of-scope

- **OUT:** canonical re-fit / any change to the `shared` block; the transverse
  library (inert by construction); fixing the pre-existing axial viscous-bookkeeping
  residual (§4.6, orthogonal — noted, not touched); frequency (Li2022) as a separate
  axis (the mechanism is quasi-static; freq enters only via existing creep `t=N/freq`).
- **Interactions:** composes with all transverse mechanisms (zero there); with
  damage (orthogonal — `dD` unaffected). Conservation mirrors `WearLoss`.
- **New-constant honesty:** unlike the recent zero-refit gates, this adds a fitted
  per-pair constant (`k_thread_fret`) — the scientifically-mandated missing form.
  Provenance documented; not presented as universal.
