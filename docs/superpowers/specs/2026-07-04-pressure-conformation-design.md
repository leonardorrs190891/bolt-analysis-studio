# Pressure-Dependent Slip Conformation — Design Spec

**Date:** 2026-07-04
**Status:** Design (awaiting review → writing-plans)
**Motivates:** Phase-2 item (a) — the sobretorque falsification (`New_Theory/MODEL_LEGITIMACY.md` §4.5)

---

## 1. Problem

Stage A's shared physics cannot fit the **sobretorque** (over-torque) condition, and the Phase-2 F0-bound experiment (`sobretorque_f0bound.json`, merged `1afde67`) proved it's **not** a too-tight F0 bound: raising the sobretorque preload to the yield-based sanity ceiling (120 → 132.8 kN) moved its MAE only 0.1378 → 0.1351 with F0 railed at the new ceiling → **structural falsification: a mechanism is missing.**

### Diagnosis (grounded, `scratchpad/sob_misfit_diag.py`)

Shared model (raised-fit constants, F0 = 132.8 kN) vs TP6 data:

| cycle | TP6 data | shared model |
|---|---|---|
| 75 | 0.800 | 0.812 |
| 300 | 0.710 | 0.671 |
| 1000 | 0.670 | 0.429 |
| 2500 | 0.600 | **0.160** |

The over-torqued joint **settles fast (1.0→0.80 in ~75 cycles) then plateaus (~0.60)**. The model captures the settling, then **keeps grinding to 0.16 — it never arrests.** The failure is concentrated in the mid-to-late regime and is worst for the highest-preload condition. The missing physics is a **pressure-scaled *arrest* of slip-driven loosening after the contact settles** — not "less slip everywhere" (the early settling already matches).

### Why the obvious fix is wrong

A naive Greenwood-Williamson pressure-dependent transverse stiffness `k_tr(F0)` has an **unfavorable sign** in the current slip law `slip = max(0, δ − F_slip/k_tr)` (higher `k_tr` ⇒ *more* slip; recorded in spec `2026-07-03-library-confrontation-phase1-design.md` §4). The data wants the *opposite*: the high-pressure contact **locks up** and slip decays toward zero.

---

## 2. Goal / non-goals

**Goal:** add one mechanism-form so the shared physics reproduces the sobretorque plateau **without disturbing the conditions that already fit** and **without re-fitting the transverse constants** — a single physics whose activation is decided by contact pressure alone.

**Non-goals:**
- Not the axial ∝A_F mechanism (Phase-1B falsification — separate item; that's an *amplitude*-driven flank loss, this is a *pressure*-driven arrest).
- Not touching embedding (gives the fast settling) or creep (gives the slow post-plateau decline).
- Not a per-condition switch or tuner. One shared physics, pressure-gated.
- Not Stage B (tuner-layer removal) — orthogonal.

---

## 3. Mechanism: pressure-gated slip conformation

A conformation state grows from the transverse slip work, **weighted by contact pressure**, and progressively shuts off the slip that feeds wear + rotational-loosening. The three physical pictures the professor endorsed ("all") reconcile as one:

- **Conformation → slip decays** is the generative cause.
- **Wear-regime collapse** is subsumed: wear → 0 because *slip* → 0, no independent K-collapse needed.
- **Equilibrium preload** is the *consequence*: F0 stops falling once slip is arrested; the residual slow decline is the untouched creep.

At high preload → fast conformation → early plateau (sobretorque). At nominal preload → conformation stays negligible over the test → nova/reusada/reaperto untouched. Pressure alone decides excitation (the parameter-registry "excited by regime" property, made physical).

---

## 4. Concrete form

- **Contact pressure:** `p = F_0 / A_contact` (`state.F_0` start-of-cycle; `A_contact` from `JointGeometry`). No new input.
- **Reference pressure:** `p_ref` — a **shared** reference contact pressure (default = nominal preload / `A_contact`, i.e. ~5e8 Pa for the UFU rig at 50 kN / 1e-4 m²). Provenance `reference`, **not fitted**; must be shared/fixed across conditions so that sobretorque's higher absolute F0 is the discriminator (do NOT set it per-joint from `F0_init`, or the ratio collapses to 1 for every condition).
- **New state `W_conf` (J)** — accumulates per cycle from the *raw* slip work weighted by pressure:
  ```
  W_conf += (p / p_ref)**n · dW_slip_raw
  dW_slip_raw = 4 · μ_eff · F_0 · slip_raw
  ```
  `dW_slip_raw` is the same tuner-independent raw transverse slip work `SlowState.W_slip_acc` already accumulates for `slip_onset` — reuse it so conformation timing does not drift with the tuners.
- **Conformation fraction:** `c = W_conf / (W_conf + W_conf_ref)` ∈ [0, 1) — a saturating close-gate. (A Hill exponent `m` for a sharper knee is an optional refinement; default `m = 1`.)
- **Coupling — a conformation gate, mirroring `slip_onset_gate`.** Define `g_conf(state, mat) = 1 − c = W_conf_ref / (W_conf + W_conf_ref)` (and `g_conf ≡ 1` when `W_conf_ref ≤ 0`). It multiplies the **slip-driven preload loss** inside `WearLoss` (the `d_wear` term, alongside the existing `slip_onset_gate` factor) and `RotationalLooseningLoss` (the `d_theta` term). This is a **gate function, not a `slip_amp_override`**: `WearLoss` reads slip amplitude, but `RotationalLooseningLoss` is torque-driven and *ignores* `slip_amp_override`, so a shared gate is the only uniform way to suppress both. As `c → 1`, `g_conf → 0` and both slip-driven channels arrest. `EmbeddingLoss` and `CreepLoss` are untouched.

### Curve reproduction

Fast settle (embedding + early wear, before `c` grows) → plateau (`c → 1`, slip-driven loss arrested) → slow decline (creep, F0-driven, survives the arrest). Reproduces all three regimes of TP6.

---

## 5. Conservation — gate `dF_0`, keep `dE` (the conservation-safe `slip_onset` pattern)

The gate suppresses the **preload loss `dF_0`** on the slip-driven channels but **not** the friction heat `dE`, identical to how `slip_onset_gate` is applied today: `WearLoss` gates `d_wear` (→ `dF_0 = −k_b·d_wear`) but leaves its `dE = k_scale·μ·F·slip_dist` ungated; `RotationalLooseningLoss` gates `d_theta`, so its `dF_0` and its `dE = T_resist·d_theta` scale together. This is the pattern that keeps `energy.conservation_residual ≈ 0`: the friction work `dE` still balances the friction term already inside `W_ext_per_cycle`, and the gated `dF_0` self-balances through the existing `U_released` accounting (less preload drop ⇒ less elastic energy released ⇒ `ΔU` adjusts). **No new energy term, no `W_ext` change** — `W_conf` is driven by the raw slip work (monotonic, tuner-independent) exactly as `W_slip_acc` is.

**Physical reading:** the conformed contact stops *shedding preload* (a mild-wear / locked-ratchet regime) while still carrying frictional micro-slip — closer to picture B (wear-regime arrest) than to literal full stick. Because the loosening prediction depends only on `dF_0`, this reproduces the plateau identically to a full-stick model.

> **Correction note (transparency — the draft had this inverted):** an earlier draft claimed a "full stick / no-heat" account (gate both `dF_0` and `dE`, "no `U_released`"). Reading `step_cycle`/`WearLoss` showed that reasoning was backwards — it is the **`dF_0`-only** gate that is conservation-safe via the existing `U_released` machinery (the same reason `slip_onset` and the damage amplifier both keep `dE`); a strict full-stick would *additionally* require gating `W_ext`'s transverse-friction term (more invasive) and would not change the fit. We take the `dF_0`-only gate. Gating `W_ext` for a strict-stick energy account is deferred as unnecessary.

---

## 6. New constants, provenance, backward-compatibility

| Constant | Meaning | Default | Provenance |
|---|---|---|---|
| `W_conf_ref` (J) | conformation scale (half-conformation slip-work) | **0 = OFF** (sentinel → `c ≡ 0`) | per-pair/rig, fitted here |
| `n` | pressure exponent | 1.0 | per-pair/rig, fitted here |
| `p_ref` (Pa) | reference contact pressure | nominal preload / `A_contact` | `reference` (geometry+nominal, **not fitted**) |

- **Default inert:** `W_conf_ref = 0` ⇒ mechanism off ⇒ `c ≡ 0` ⇒ every existing fit is **bit-unchanged** (same sentinel discipline as `slip_onset_W = 0`).
- **Provenance:** `W_conf_ref` and `n` are per-pair/rig tribology constants — fitted in this work, so the honest validation is the shared-fit-with-transfer-check in §9, recorded AS IS. A literature anchor for the pressure scaling is deferred to Phase-3 provenance (as with `C_creep`).
- Only **2 fitted numbers** (`W_conf_ref`, `n`) enter the dataset, and they are offered to the optimizer **only when the over-torque regime is present** (§8).

---

## 7. Driver variant (decision + documented alternative)

**Chosen for the first implementation — raw-slip-driven (monotonic):** `W_conf` accumulates from `slip_raw` (imposed kinematics), so `c` climbs monotonically to full lock. Simplest, reuses the `W_slip_acc` accumulator, one clean state, easy to test.

**Documented alternative — effective-slip-driven (self-limiting):** drive `W_conf` from the *effective* (gated) slip by weighting each increment by the start-of-cycle conformation gate `g_conf`. Then conformation self-attenuates as the joint locks. **Recommendation:** build raw-driven first; if it needs an implausibly sharp `W_conf_ref`/`n` to keep nova inert while locking sobretorque, switch to the self-limiting variant. Both are single-mechanism; the switch is localized to the `W_conf` update line.

> **Correction note (built + validated 2026-07-04, strand 2 — this claim was overstated).** An earlier draft called this a "true equilibrium `c<1` (picture C emerging on its own)". That is **wrong for the minimal, localized form**. Weighting the increment by `g_conf` gives a **self-limiting *plateau***, not a fixed point: the increment shrinks two ways (via `g_conf` *and* via the driver `∝F_0^{n+1}` as `F_0` falls), so over the finite test `c` plateaus `<1` — but **asymptotically `c→1`** because creep keeps `F_0` (hence the driver) nonzero. A genuine `c*<1` fixed point would require conformation to feed back into the **slip kinematics** (raise the stick capacity so disp-mode `slip → 0` and the joint sticks) — a larger change that touches the slip computation and entangles with roadmap item #4 (`F_amp↔δ_amp`); **deferred**. What the minimal form *does* deliver (validated, `MODEL_LEGITIMACY.md §4.9`): effective `n=2` vs OFF ⇒ **RESOLVED and cleaner than raw** (sobretorque 0.1379 → 0.0299; all three other conditions *improve*), and **more robust under freed `n`** (holds the others within the hold even at the railed `n=4`, where the raw driver breaches it). The `n`-rail itself is **objective-driven** (global-MAE always wants sharper separation), so it persists for *both* drivers — `n=2` fixed remains the right modeling choice.

---

## 8. Engine & registry integration

- `SlowState`: add `W_conf: float = 0.0` (+ serialization if `SlowState` is serialized). `CycleSnapshot` may expose `c` for plotting (optional).
- `JointMaterial`: add `W_conf_ref = 0.0`, `conform_pressure_exp = 1.0`, `p_ref_conform = <nominal>` (all default to the inert state).
- Module-level `conformation_gate(state, mat) -> float` next to `slip_onset_gate`: returns `W_conf_ref/(W_conf+W_conf_ref)`, or `1.0` when `W_conf_ref <= 0` (inert). `WearLoss.rate` multiplies `d_wear` by it (gating `dF_0`, leaving `dE`); `RotationalLooseningLoss.rate` multiplies `d_theta` by it (gating `dF_0` and its derived `dE = T_resist·d_theta` together).
- `DynamicStiffnessAnalyzer.step_cycle`: accumulate `W_conf` in the existing §4.6 block **alongside `W_slip_acc`** (after `F_0`, no ordering deps) from the same raw slip work weighted by `(p/p_ref)**n`, `p = F_0/A_contact`. Mechanisms read the start-of-cycle `W_conf` (via the gate) exactly as they read start-of-cycle `W_slip_acc`/`D`.
- `parameter_registry.py`: add a `ParameterRule` for `W_conf_ref` (and `conform_pressure_exp`) with a predicate `_over_torque` = "some condition's contact pressure `F0_init/A_contact` exceeds `κ·p_ref`" (κ TBD in the plan, e.g. 1.5). So `active_candidates` offers the conformation constants to `fit_parsimonious` **only** when the dataset contains an over-torque condition — axial/transverse-only datasets never see them. Registry-truth test: with the mechanism off (`W_conf_ref=0`), the engine trajectory is bit-identical (`np.array_equal`).

---

## 9. Validation & success criteria (method: direct A/B, `n` fixed — decided 2026-07-04)

A **standalone experiment** (`New_Theory/conformation_fit.py`; canonical `shared` block untouched, per the `creep_anchor`/`sobretorque_f0bound` precedent), **not** the canonical `fit_parsimonious` — the conformation constants are novel (no anchor to regularize toward), so a head-to-head fit is the honest, unbiased test.

**A/B fit** on the canonical shared config (same F0 setup — 120 kN sobretorque bound — in both arms, so conformation is the *only* difference), via direct `SharedCalibrator._fit_subset`:
- **Baseline:** `{C_creep}` free, conformation off (`W_conf_ref=0`).
- **Treatment:** `{C_creep, W_conf_ref}` free, conformation active with `conform_pressure_exp=2` and `p_ref_conform=5e8` **fixed** (one new fitted number, `W_conf_ref`).

**Pre-registered verdict** (frozen before the run; consistent with the `sobretorque_f0bound` thresholds):
- **RESOLVED** — sobretorque MAE < **0.06** (out of the 18× outlier band, toward its ~0.007 local floor) AND each of nova/reusada/reaperto moves < **0.01** vs baseline AND `conservation_residual` ≈ baseline.
- **FALSIFIED** — sobretorque stays > **0.10**, OR any other condition degrades by > **0.02** (conformation "fixes" sobretorque only by disturbing the others ⇒ the constants are not pressure-separable — a clean falsification of the form, like the F0-bound experiment falsified the bound hypothesis).
- **PARTIAL** — in between.

**Integrity guard:** test **n=2 only** and record AS IS. Escalation (n=3 → fit `n` → the self-limiting-equilibrium driver of §7) is a **documented follow-on decided after seeing the n=2 result**, never an automatic loop-until-it-passes. Do not tune to force a pass.

Report as `MODEL_LEGITIMACY.md` §4.9 (Fable — falsification-logic + writing): the fitted `W_conf_ref`, per-condition MAE deltas for both arms, the conservation residual, and the verdict.

---

## 10. Testing

- **Registry-truth:** `W_conf_ref=0` ⇒ trajectory bit-identical to pre-change (`np.array_equal`) for a nova run — proves default-inert / backward-compat.
- **Monotonic lock:** with the mechanism on at high pressure, `c` increases monotonically in [0,1) (equivalently `conformation_gate → 0`); wear + rotational-loosening **`dF_0` → 0** as `c → 1` (their `dE` continues — see §5).
- **Pressure gating:** at `p = p_ref` (nova), `c` stays below a small bound over 2500 cycles; at `p ≈ 2.6·p_ref` (sobretorque), `c` crosses ~0.5 within the test — the regime separation is real.
- **Conservation:** `conservation_residual ≈ 0` on a full sobretorque run — the `dF_0`-only gate reuses the `slip_onset`/`U_released` balance, so the residual must stay at its pre-change level, not degrade.
- **Plateau shape:** a sobretorque run produces settle→plateau (not runaway), qualitatively matching TP6.
- The 18-file calibration suite stays green (default-inert guarantees no regression).

---

## 11. Open questions (for the plan / the professor)

1. **Driver variant** (§7): **RESOLVED (professor, 2026-07-04): raw-slip driver.** Self-limiting equilibrium kept as the documented fallback in §7 if raw needs an implausibly sharp `W_conf_ref`/`n` to keep nova inert.
2. **Hill exponent `m`** on `c` (sharper knee) — default 1; add only if the plateau onset is too gradual.
3. **`κ` in the over-torque predicate** (§8) — the pressure multiple above which the constants are offered; pick in the plan (~1.5).
4. **`p_ref` sourcing** — nominal-preload/`A_contact` is the reference; confirm the nominal (50 kN UFU) is the right anchor vs a material/handbook contact-pressure scale (Phase-3 provenance).
