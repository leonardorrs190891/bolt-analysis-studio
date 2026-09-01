# Declining re-tightening recovery — thread galling vs geometric ceiling (design)

**Date:** 2026-07-07
**Context:** V2 energy engine (`dynamic_stiffness_analyzer.py`). Sibling of
`2026-07-07-embedding-renewal-design.md` (which added `retighten`/`tightening_torque`/
`k_emb_renew`). **Status:** design for review (pre-implementation). Falsify-first,
opt-in / default-inert. DESIGN ONLY — no engine code written here.

---

## 1. Motivation — the G4 finding

`retighten(applied_torque)` predicts the recovered preload via the Motosh balance
`tightening_torque` (analyzer L444–458), reusing the engine's existing friction terms:

```
T_tighten(F0) = F0 · [ lead_per_radian
                       + μ_thread · d_2 / (2·cos 30°)      (thread flank)
                       + μ_bearing_eff(D) · r_bearing ]    (bearing / under-head)
   with  μ_bearing_eff(D) = μ_bearing · (1 − k_dmg_mu·D)
```

Linear in F₀ ⇒ `F0_achieved = T_applied / K(D)`, where `K` is the nut factor (the
bracket). The frozen canonical `shared` block has **`k_dmg_mu = 0`**, so `K` is
**independent of D** and the model predicts recovery **flat** across successive
retightenings (`R_F(start of tN) ≈ 1.0` for all N). Pre-registered §3.2 of the sibling
spec; verdict recorded in `MODEL_LEGITIMACY.md` §4.10 (G4).

**But Liu2022 (Structures, M12) dry re-tightening declines:** the achieved preload at the
start of each phase, normalised to first-tightening F₀, is

| phase | t0 | t1 | t2 | t3 |
|---|---|---|---|---|
| **dry** `R_F(start)` | 1.000 | 0.918 | 0.832 | 0.793 |
| **oil** `R_F(start)` | ~1.00 | ~1.00 | ~1.00 | ~1.00 (release restores ~100%) |

So the frozen physics **cannot** produce the observed dry decline (`k_dmg_mu=0` → flat;
and `k_dmg_mu>0` would make recovery *rise*, since lower bearing μ → higher F₀ at fixed T
— the wrong sign). A **missing FORM** is named, not a knob to tune away: *at fixed torque,
a damaged joint recovers less preload.* This spec designs that form.

### 1.1 The sign subtlety (why we cannot reuse `k_dmg_mu`)

The reaperto **collapse** and the reduced **recovery** need friction to move in **opposite
directions**:

| symptom | interface | μ must | existing driver |
|---|---|---|---|
| reaperto collapse (faster loosening) | **bearing** annulus | **fall** (less back-off resistance) + wear ↑ | `k_dmg_mu` (bearing, currently 0) + `k_dmg_wear` (active) |
| reduced recovery (less F₀ at fixed T) | **thread** flank | **rise** (higher nut factor) | **none — this spec** |

A single `k_dmg_mu` cannot do both. The physical resolution the apparatus note already
hints at: **thread-flank galling** (adhesion/roughening on the thread, raises the
*tightening* nut factor) is a **different interface** and a **different event**
(re-torque) from **bearing-face debris/polishing** (lowers *cycling* back-off resistance).
Opposite μ-signs on different surfaces is coherent, not contradictory.

---

## 2. Physical hypothesis

`D` (surface damage) persists across retightenings and grows faster when slip work is
higher (dry, high μ). Beyond its existing roles (bearing-μ modulation + wear amplification
+ embedding renewal), damage on the **thread flanks** raises the **effective tightening
friction**, so a fixed re-torque of 80 N·m develops progressively less preload:

- **Dry** (μ≈0.2–0.24): high slip work ⇒ `D` grows ⇒ thread galling ⇒ nut factor `K(D)`
  rises ⇒ `F0 = T/K(D)` **declines** each retighten. The *same* rising D also amplifies
  wear (`k_dmg_wear`) and renews embedding (`k_emb_renew`) → each phase also loosens
  faster. One D-trajectory, two symptoms (recovery ↓ **and** loss-rate ↑).
- **Oil** (μ≈0.1–0.18): low slip work ⇒ `D` stays low ⇒ no galling ⇒ `K` ≈ constant ⇒
  recovery **flat** (~100%), slow loosening.

The dry-vs-oil contrast must emerge from the **single μ-input difference**, all physics
constants shared. That is the test.

---

## 3. Two candidates

### Candidate A — thread galling (damage → tightening-friction rise) **[RECOMMENDED]**

Damage raises the thread-flank friction **seen only at re-torque**. New helper mirroring
`mu_bearing_eff`:

```
μ_thread_tighten_eff(D) = μ_thread · (1 + k_gall · D)          # k_gall ≥ 0
```

Used **only** inside `tightening_torque` (the thread term):

```
K(D) = lead_per_radian
     + μ_thread_tighten_eff(D) · d_2 / (2·cos 30°)     # ← galling enters here
     + μ_bearing_eff(D) · r_bearing                    # ← unchanged (collapse driver)

F0_achieved = T_applied / K(D)                         # declines as D grows
```

- **New field** `JointMaterial.k_gall: float = 0.0`. Default 0 ⇒ `μ_thread_tighten_eff =
  μ_thread` ⇒ `K` identical ⇒ **exact bit-identical backward-compat** (and `retighten`
  unchanged when `k_gall=0`).
- **Scope: `tightening_torque` only.** `step_cycle`, the loss mechanisms, `T_resistance`
  (cycling back-off resistance) are **untouched** ⇒ the reaperto collapse physics
  (`k_dmg_mu` bearing-fall + `k_dmg_wear`) is intact **by construction**.
- Linear coupling ∝ D: one constant, parsimonious, same functional form as the engine's
  other two damage couplings (`mu_bearing_eff`, wear amplification).

**Why thread and not bearing (or both)?** Bearing μ is already spoken for by the collapse
(`k_dmg_mu`, opposite sign). Putting galling on the thread keeps the two damage-on-friction
effects on physically distinct surfaces with independent signs. A "both terms rise"
variant is possible (see §3.3 magnitudes) but couples galling to the same interface whose
μ falls for the collapse — avoid. **Thread-only** is the clean choice.

**Why `tightening_torque` only and not also `T_resistance` (cycling)?** Galled flanks are
permanently rougher, so in principle cycling thread friction also rises. But raising
cycling thread friction *resists* back-off ⇒ **slower** loosening — which contradicts the
dry data (each dry phase loosens **faster**, gate G2). So the cycling-friction coupling
has the wrong sign for the observed within-phase acceleration; the acceleration is already
carried by D-amplified wear + embedding renewal. Scoping galling to the discrete re-torque
event keeps the division of labour clean:
- **between phases (recovery, G4):** thread galling raises re-torque `K` → less F₀. *(new)*
- **within phases (acceleration, G2):** `k_dmg_wear` + `k_emb_renew`, both ∝ D. *(existing)*

Deferred extension (only if a dataset demands it): a separate, smaller cycling-thread
term. Not now.

### Candidate B — geometric recovery ceiling (permanent set / accumulated wear)

Hypothesis: accumulated `delta_wear` (removed bearing material) + permanent set caps the
clamp reachable at fixed torque. Two representable forms:

- **B1 (multiplicative cap):** `F0_achieved = min(T/K, F0_first·(1 − k_set·δ_wear/δ_ref))`.
- **B2 (prevailing-torque offset):** `F0_achieved = max(0, (T − T_prev(D or δ_wear))/K)`,
  with a locknut-like offset `T_prev = k_prev·(…)` that must be overcome before preload
  develops (debris/thread damage resisting rotation).

**Rejected as the primary.** Reasons:

1. **No fixed-torque mechanism for B1.** Torque-controlled tightening reaches `F0 = T/K`
   regardless of how much material was removed — removing bearing material does **not**
   lower the torque-balance target (it changes stack thickness → `k_b` only to 2nd order).
   A raw "cap ∝ δ_wear" is not a torque-balance quantity; it is phenomenological with no
   clean derivation. Recovery decline at fixed torque **requires** either a friction rise
   (→ Candidate A) or a torque offset (→ B2).
2. **B2 is defensible but degenerate + non-standard.** An additive prevailing torque does
   reduce achieved F₀, but functionally it overlaps Candidate A (both cut F₀ with
   accumulated damage) while being the *less standard* torque-tension deviation — the
   classical, measured cause of repeated-tightening preload loss is **nut-factor scatter /
   friction rise (galling)**, not a prevailing torque (which is a locknut construct).
3. **Torque-confounded discriminator.** Galling (multiplicative) gives a **torque-
   independent** fractional decline `R_F = K(t0)/K(tN)`; a prevailing-torque offset gives a
   **torque-dependent** one `R_F = (T−T_prev)/T`. Liu2022 uses a **single** torque
   (80 N·m), so this dataset **cannot** discriminate A from B2 — default to the more
   physical/standard A.
4. **Worse transfer.** Tying recovery to `δ_wear` inherits the §4.10/§4.6 finding that
   `k_wear_scale` (hence `δ_wear` level) is a **per-rig** constant that **over-predicts**
   on Liu2022. Tying recovery to `D` (Candidate A) aligns with the apparatus note's own
   hypothesis ("dry: D accumulates, recovers less") and with the existing damage ontology.

### 3.3 Magnitude check (both candidates land in a physical range)

Motosh breakdown for Liu2022 M12×1.75 @ T=80 N·m (`d_2=10.86 mm`, `r_bearing≈7.75 mm`
[approx — head/washer geometry], lead ≈ 8% of `K`, thread ≈ 41%, bearing ≈ 50%):

To hit the dry decline `R_F = {1, 0.918, 0.832, 0.793}` the nut factor must rise
`dK/K = 1/R_F − 1 = {0, 0.089, 0.202, 0.261}`. Solving Candidate A:

| phase | dK/K needed | `k_gall·D` (thread-only, thr≈41%) | `k_gall·D` (both terms, fric≈92%) |
|---|---|---|---|
| t1 | +0.089 | **0.22** | 0.10 |
| t2 | +0.202 | **0.49** | 0.22 |
| t3 | +0.261 | **0.63** | 0.28 |

So thread-only galling needs `k_gall·D` up to ~0.63 at t3. If the per-rig fit puts dry
`D(t3) ≈ 0.3–0.6`, then `k_gall ≈ 1–2` — an O(1) galling coefficient, physically bounded
and fittable. (Robust to `r_bearing` within reason; the thread fraction stays ≈0.4.)

---

## 4. Recommendation

**Adopt Candidate A: thread galling.** One new opt-in field:

```python
# JointMaterial (dynamic_stiffness_analyzer.py)
# Galling de flanco de rosca no re-aperto (spec 2026-07-07): superficie danificada
# eleva o atrito de rosca VISTO NO APERTO => nut factor sobe => F0 recuperado cai.
# So atua em tightening_torque (evento de re-aperto), nunca em step_cycle/T_resistance
# => colapso do reaperto (k_dmg_mu bearing + k_dmg_wear) intacto. Sinal OPOSTO ao
# k_dmg_mu (interface distinta: flanco de rosca vs face de bearing). 0.0 = inerte
# (mu_thread_tighten_eff = mu_thread, K identico, backward-compat exato).
k_gall: float = 0.0        # acoplamento dano -> atrito de rosca no aperto [-]
```

New module helper `mu_thread_tighten_eff(state, mat)` (mirrors `mu_bearing_eff`); the only
call-site is the thread term of `tightening_torque`. **No other code path changes.**
Add `k_gall` wherever `JointMaterial` fields are enumerated (to_dict/from_dict — automatic
via `__dataclass_fields__` filter; V2 tuner-override filter; decomposition/serialization
consumers), same as `k_emb_renew`.

This is the **minimal** single-parameter form. A minimal *combination* (galling +
`k_emb_renew`) is expected anyway: galling carries the **starting-point** decline (G4),
`k_emb_renew` carries the **within-phase** faster re-settling. They are orthogonal (one in
`tightening_torque`, one in `retighten`'s δ_emb update). No B-term is added.

### 4.1 How it produces declining dry recovery while oil stays flat

Everything flows from **one** input difference (μ_dry ≈ 0.2 vs μ_oil ≈ 0.1) through the
**shared** damage physics:

```
dry:  high μ → high per-cycle slip work (4·μ·F0·slip) → W_slip_acc ↑ → D grows (c_D)
      → K(D) = lead + μ_thread·(1+k_gall·D)·d_2/(2cosα) + μ_bearing_eff(D)·r_bearing  rises
      → F0_achieved = 80 / K(D)  DECLINES  each retighten            [G4 dry]
      (same D also ↑ wear via k_dmg_wear and renews δ_emb via k_emb_renew → phase loosens faster [G2])

oil:  low μ  → low slip work → D stays ≈ 0 → k_gall·D ≈ 0 → K ≈ const
      → F0_achieved ≈ 80 / K0  FLAT  (~100% restore)                 [G1/G3 oil]
```

No per-phase tuning, no per-curve initial state: the sequence is a **prediction** of the
shared D-trajectory under two μ inputs.

---

## 5. Validation plan

Extends `New_Theory/validate_retightening.py` (built for §4.10). Frozen Stage-A constants;
free **at most** `{k_gall, k_emb_renew}` (galling + renewal), **never** per-curve tuners.

1. **Dry sequence:** tighten `F0 = 80/K(D=0, μ_dry)`; run 5000 cyc
   `step_cycle(F_amp, θ=π/2, 12.5 Hz, delta_amp=0.3e-3)`; record `R_F(t0)`. Then
   `retighten(80 N·m)` → 5000 cyc → `R_F(t1)`; repeat t2, t3. Because `k_gall>0` and D has
   grown, each `retighten` solves `F0 = 80/K(D)` with a **higher** K ⇒ lower start.
2. **Oil sequence:** identical protocol, μ_oil only. D stays low ⇒ K ≈ K0 ⇒ flat starts.
3. **Compare `R_F(start of tN)`** to the dry-release (`fig6a`) and oil-release (`fig6b`)
   start points; compare per-phase decay shapes to `fig6a/6b/7a`; `fig8` for the
   multi-retighten trend (**trim t4 fatigue fracture** — out-of-model).

**Pre-registered gates (AS IS, before running):**

- **G4′ (recovery decline — the target of THIS spec):** with `k_gall` freed, dry
  `R_F(start)` must be **monotone decreasing** t0→t3 and land within ~2× of the observed
  per-step drops `{−0.082, −0.086, −0.039}`; oil `R_F(start)` stays ≥ 0.95 (flat) with the
  **same** `k_gall` (its low D makes galling inert). Galling is *justified* only if it
  clears this; else documented negative finding, `k_gall` stays 0.
- **G-parsimony:** freeing `k_gall` must cut the dry start-point MAE by > 0.005
  (forward-selection tol) vs `k_gall=0`. If wear-amplification/renewal alone already
  reproduce the start-point decline, galling is not justified by this dataset.
- **G-sign:** the **same** `k_gall` that fits dry must leave oil flat (recovery from μ
  contrast alone). Failure ⇒ the contrast needs more than μ+galling (finding).
- **Backward-compat:** `k_gall=0` ⇒ `tightening_torque` bit-identical ⇒ full suite
  unchanged where `retighten` is unused.

### 5.1 CRITICAL DEPENDENCY — the Liu2022 level confound (must be resolved FIRST)

**§4.10 showed the zero-refit Liu2022 validation COLLAPSES.** Three cross-rig constants
transferred from M16/UFU do **not** transfer to M12/Liu2022:

1. `c_D=2.0` / `k_dmg_wear=4.0` (the UFU **collapse** signature) drive a spurious runaway
   (D→1, wear→5×) on a joint that in reality loses only 14–27%;
2. `emb_depth` (VDI) over-predicts settling of the fine-ground M12 surface (§4.6 again);
3. `k_wear_scale=1.0` (frozen) vs the 0.44 fitted to M16 UFU nova ⇒ wear ~2.3× too fast.

The joint collapses to `F0→0` within the first phase — and **on a joint already at ≈0, any
recovery term is unobservable** (galling raising K, or renewal of δ_emb, do nothing to a
clamp that is already gone — exactly the confound that neutered G5 in §4.10).

**Therefore a clean test of galling REQUIRES the per-rig LEVEL first.** Before freeing
`k_gall`, the harness must re-establish a **non-collapsing** M12 baseline by re-calibrating
the per-rig level: `{emb_depth (M12 fine-ground VDI value), k_wear_scale, mild/off damage
c_D·k_dmg_wear}` so the dry joint reproduces the ~14–27% per-phase loss (**not** collapse).
Only once the level is right does the **recovery-decline shape** become a meaningful,
isolable target for `k_gall`. This is the same "forms transfer, constants don't" verdict of
`MODEL_LEGITIMACY.md` §8: the galling **form** is what we validate; its **constant**
(`k_gall`) and the enabling **level constants** are **per-rig** and must be fit to Liu2022,
with honest provenance = *fitted*. **Provenance-honest:** `k_gall` is not universal; the
oil-vs-dry *ordering* is the transferable claim, the *magnitude* is per-rig.

Sequencing: **(1)** re-calibrate M12 level → non-collapsing dry baseline; **(2)** confirm
`R_F(start)` decline is present and separable from the within-phase decay; **(3)** free
`k_gall`, run G4′/parsimony/sign; **(4)** write verdict AS IS to `MODEL_LEGITIMACY.md`
§4.11 (or extend §4.10), whichever way it falls.

---

## 6. Risks / limitations

- **Level confound dominates (highest risk).** If step (1) is skipped, G4′ is untestable
  (collapse hides recovery). This is a hard prerequisite, not a footnote.
- **Identifiability of `k_gall` vs `k_emb_renew`.** Both make dry loosen faster and (via D)
  grow together. They are separable in principle — galling shifts the **start point** of
  each phase (a step), renewal steepens the **within-phase** decay — but only if the
  digitized `R_F(start)` points are read accurately (±0.5% R_F per the note). Fit them
  jointly and check the start-point residual specifically, not just whole-curve MAE.
- **Single-torque dataset cannot discriminate A vs B2.** Acknowledged (§3.3.3). We pick A
  on physical-standard grounds; a multi-torque re-tightening study would be needed to
  falsify A vs a prevailing-torque offset. Note for future data acquisition.
- **Oil-direct vs oil-release ~10% gap is OUT OF SCOPE.** `fig7a` (oil-direct) restores
  only ~88–90% while `fig6b` (oil-release) restores ~100% — a **protocol** effect
  (release-angle relieves stored thread torsion / prevailing torque before re-torque), not
  a **damage** effect. Both are low-D, so the D-driven galling term predicts ~flat for
  both and will **not** capture this ~10% protocol gap. Do not tune `k_gall` to it; flag it
  as a separate (torsion-relief) form if a future spec targets it.
- **`r_bearing` provenance.** The magnitude table uses `r_bearing≈7.75 mm` (M12 head/hole
  estimate); Liu2022 stacks a 20 mm washer-type load cell — the effective bearing radius
  should be taken from the actual stack when the harness is built. The *fraction* split
  (thread≈0.4) and hence the O(1) `k_gall` conclusion are robust to this.
- **Energy accounting.** Galling raises the discrete re-torque friction work (wrench work),
  which — per the sibling spec §3.5 — is deliberately **outside** the per-cycle budget
  (`retighten` rebases the segment). So `conservation_residual` (per cycling segment) is
  unaffected. No new energy-budget obligation.

---

## 7. Discipline / out of scope

- **Opt-in / default-inert:** `k_gall=0` ⇒ `μ_thread_tighten_eff=μ_thread` ⇒
  `tightening_torque` bit-identical ⇒ exact backward-compat. Physically motivated
  (thread-flank galling raises the nut factor — textbook torque-tension degradation).
  Provenance-honest (`k_gall` per-rig, fitted; ordering transferable, magnitude not).
- **TDD (failing tests first):** galling raises K → lower F₀ at fixed T (monotone in D);
  `k_gall=0` bit-identical; galling scoped to `tightening_torque` (assert `step_cycle` /
  `T_resistance` outputs unchanged when only `k_gall` varies); D=0 ⇒ no effect.
- **Keeps collapse intact by construction:** no touch to `k_dmg_mu`, `k_dmg_wear`,
  `step_cycle`, `T_resistance`.
- **Out of scope:** the geometric ceiling / prevailing-torque form (B — rejected §3);
  cycling-thread galling coupling (wrong sign for G2 — deferred); oil-direct vs oil-release
  protocol gap (§6); propagating to GUI Run / `.msd`; re-fitting canonical `shared`/
  `profiles` (this is validation, not adoption). The per-rig M12 **level** re-calibration
  (§5.1) is a **prerequisite** of the validation, not part of this mechanism's adoption.
