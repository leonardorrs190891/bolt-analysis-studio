# Predictive Damage Trigger — Design (2026-07-05)

**Status:** design (brainstormed 2026-07-05). Terminal step → writing-plans.
**Author dialogue:** Prof. Leonardo Rosa + Claude. Decision: build **all three layers, most robust**.

---

## 1. Problem

Damage activation is a **manual per-condition flag** (`ConditionSpec.damage_active` /
the calibration). The §4.8 `--damage-on` what-if showed damage IS the collapse
mechanism, but **per-condition, not universal**: turning it on everywhere helps the
collapse cases (Karlsen 0.226→0.139) and **hurts the plateaus** (YANG 0.656→0.718,
LIU 0.640→0.670); the global *median* improves but **p90 worsens** and beats-no-loss
is flat — a wash trade-off. We need damage to **self-trigger where collapse is coming**,
replacing the manual flag with a physical onset.

## 2. What separates collapse from plateau (grounded in the library)

From the transfer library (46 curves; `scratchpad` analysis 2026-07-05):

- **NOT pressure or %proof** — both span the full range in *both* regimes (collapse at
  40 MPa/10% *and* 503 MPa/79%; plateau at 49 MPa/11% *and* 323 MPa/55%).
- **The strongest separator is SLIP AMPLITUDE (the fretting slip regime).** Controlled
  amplitude sweeps at a *fixed joint* flip plateau↔collapse:
  - **Lu M8, F0=12 kN:** δ=0.25 mm → plateau (fd 0.77); δ≥0.5 mm → collapse (fd 0.10–0.16).
  - **Liu M16, F0=60 kN:** δ=0.25–0.3 → plateau (fd 0.68); δ=0.4–0.8 → collapse-ish (fd 0.33).
  - **Yang M10:** δ=0.4–0.6 → plateau; δ=0.6 @ 5 Hz → collapse.
  This is the classic **partial-slip (stick → plateau) vs gross-slip (sliding → wear/
  fretting damage → collapse)** transition, at δ ≈ the elastic slip limit `μ·F0/k_tr`.
- **Two residual modes** the slip regime does NOT explain:
  - **Near-proof overload:** Bauer M8 at 94% proof collapses at δ=0.07 mm (*not* gross slip).
  - **Member stiffness:** Rousseau t10 collapses but t12/t14 plateau at *identical*
    preload/amplitude (grip thickness → member stiffness; this is §4.8 roadmap item 10).

## 3. Layered design (all three, most robust)

### 3.1 Core (layers 1+2): gross-slip-gated fretting-dose onset

**Layer 1 — slip regime (folded, no new gate).** Damage growth is already driven by the
per-cycle **slip dissipation**, which is ~0 in partial slip (`slip = max(0, δ − F_slip/
k_tr) = 0`) and >0 in gross slip. And `SlowState.W_slip_acc` (the tuner-independent raw
transverse slip work, `4·μ·F0·slip`) **only accrues in gross slip**. So the regime
dependence is inherent — no separate gate, no new constant (parsimony = robustness; a
redundant explicit gate would only add a knob).

**Layer 2 — fretting-dose onset (one new Hill gate, mirroring `slip_onset`).**

```
g_dmg = 1.0                          if W_crit <= 0       # transparent (guards 0/0)
g_dmg = W_slip_acc^k / (W_slip_acc^k + W_crit^k)  else    # damage-onset gate ∈ [0,1)
dD   *= g_dmg                                             # gate the existing D-growth
```

Below the critical fretting dose `W_crit` → `g_dmg≈0` → `D` stays ~0 → **plateau**. Above
→ `g_dmg→1` → `D` grows (wear amplification `1+k_dmg_wear·D` + friction drop
`1−k_dmg_mu·D`) → **collapse**. This is the *exact* structure of `slip_onset_gate`
(Hill gate on `W_slip_acc`), now applied to **damage growth** instead of the slip-driven
loss. It **replaces the manual `damage_active`**: `c_D>0` is always available; the
onset gate + the (automatic) gross-slip dependence decide *whether/when* `D` grows.

- New `JointMaterial` fields: `W_crit` (J), `dmg_onset_sharpness` (default = same as
  `slip_onset_sharpness`, 4).
- **Ordering:** `slip_onset_W` (loss incubation) < `W_crit` (damage/collapse) — physical
  sequence settle → loss → collapse.
- **Fouvry link:** `W_crit` is a *critical accumulated fretting energy to initiate
  damage* — the same energy-capacity concept the strand-3 hunt identified (Fouvry
  `Tribology Int.` 2007). This is its provenance target (Phase-3-style, per-pair).

### 3.2 Layer 3 (residual modes — split by what physics can ground)

- **Near-proof overload → a physics-motivated onset path (activator).** At very high
  preload fraction (→ near-yield local plasticity / accelerated relaxation), damage can
  initiate *without* gross slip. Add a **second onset contribution** keyed on a preload-
  severity variable `s_proof = F0/(proof·A_s)` (a real, provenance-carrying input), e.g.
  `g_dmg = max( dose_gate, severity_gate(s_proof) )` where `severity_gate` is a Hill gate
  on `s_proof` with threshold `s_proof_crit` (~0.85–0.9). Physics-motivated (not a
  black-box classifier); **validated to generalize** — if it doesn't beat "off" on the
  library, it reverts to diagnostic.
- **Member stiffness (Rousseau) → diagnostic only.** t10-vs-t14 is the §4.8 item-10
  `grip→L_eff→k_b` scaling — a **stiffness form issue, not damage**. Forcing it into the
  damage trigger would be curve-fitting. Layer 3 **flags** it (a member-stiffness
  severity diagnostic in the report) and defers the fix to roadmap item 10.

## 4. Conformation interaction

The onset gate gates `dD` (damage growth) but leaves `dE` ungated (the "dF_0 yes, dE no"
pattern), so `W_slip_acc` keeps accruing even when conformation has arrested the *loss*.
⇒ **conformation delays, does not prevent, damage** (physical: a conformed joint under
continued gross slip eventually frets/fails). `W_crit` must be high enough that conformed
plateaus (sobretorque) don't cross it in a realistic test window. **Note (examine in
validation, do not re-litigate):** high-F0 joints may plateau because they're *partial
slip* (`δ < μ·F0/k_tr`) — a mechanism that may overlap what conformation captured for
sobretorque.

## 5. New constants & provenance

| Constant | Meaning | Default | Provenance |
|---|---|---|---|
| `W_crit` (J) | critical fretting dose for damage onset | **0 = transparent gate** (`g_dmg≡1` ⇒ ungated growth; overall inert via `c_D=0` default) | per-pair, fitted here; Fouvry energy-capacity target (Phase 3) |
| `dmg_onset_sharpness` | Hill exponent `k` | 4 (= `slip_onset_sharpness`) | shape, fixed |
| `s_proof_crit` | near-proof onset threshold (fraction of proof) | 1.0 (= off) | ~0.85–0.9 fitted; handbook (near-yield) |

**Default-inert / backward-compat:** with `c_D=0` (current default) damage is inert
regardless — bit-unchanged. The trigger is opt-in: set `c_D>0` + `W_crit>0` (+ optional
`s_proof_crit<1`). When `W_crit=0` the gate is transparent (`g_dmg≡1`), reproducing the
current ungated damage growth (so the existing damage-active profiles reproduce exactly).

## 6. Validation & success criteria

Re-run the transfer sweep with the trigger **deciding** (no manual `damage_active`; a
`--damage-trigger` mode of `transfer_validation.py`, separate artifacts):

1. **Regime accuracy:** damage auto-activates (`final D > threshold`) on the collapse
   cases and stays ~inert on the plateau cases — a classification confusion matrix
   (collapse/plateau × damage-on/off) across the 46 curves.
2. **MAE:** beats **both** the manual-flag baseline **and** the blanket `--damage-on`
   (which was a median-only wash). Report per-source + global median AND p90 (p90 is the
   trade-off tell).
3. **Pre-registered thresholds** (frozen before the run, AS IS): a target regime-accuracy
   and a "no-worse-than-blanket p90" — set in the plan, recorded whatever the result.

## 7. Testing

- Unit: `g_dmg` Hill shape (0 below `W_crit`, →1 above); `W_crit=0` ⇒ `g_dmg≡1`
  (backward-compat, `np.array_equal` on a damage-active trajectory); near-proof
  `severity_gate`; default-inert (`c_D=0` ⇒ D≡0 regardless of `W_crit`).
- Registry-truth: the onset constants offered only when the regime warrants (a
  `ParameterRule` predicate).
- Backward-compat: existing damage-active profile (reusada/reaperto) reproduces with
  `W_crit=0`.

## 8. Open questions (for the plan / the professor)

1. **`s_proof` proof-stress source** — from the bolt class (config) or a default? (Same
   issue as the A_contact/proof discussion.)
2. **Does the near-proof activator generalize** or revert to diagnostic? (Empirical —
   decided by the validation, pre-registered.)
3. **Partial-slip vs conformation overlap** for high-F0 plateaus — a validation
   observation, possibly a future consolidation (not this spec).

## 9. Phasing (for writing-plans)

- **Phase A — core (3.1):** `W_crit` onset gate on damage growth + tests + backward-compat.
- **Phase B — near-proof (3.2 activator):** `s_proof_crit` path + tests.
- **Phase C — validation (§6):** `--damage-trigger` transfer mode + pre-registered run +
  AS-IS documentation (regime accuracy, MAE vs baselines, member-stiffness diagnostic).
