# Member-Stiffness Rotation-Onset Instability — Design (2026-07-07)

**Goal:** Give rotational self-loosening a **grip-dependent onset + runaway** so a
short-grip (thin, stiff-bolt, low-resilience) joint crosses into rotation collapse
while a long-grip joint stays stable — reproducing the ~10× Rousseau steel
member-thickness spread (`0.088 / 0.624 / 0.903`) the model is currently blind to
(`MODEL_LEGITIMACY.md` §4.8, roadmap #10). Opt-in, default bit-identical,
physically motivated, provenance-honest, AS IS.

**Status:** design proposal (read-only investigation; no engine code changed).
This is a **DESIGN** document — the go/no-go and any implementation are the
professor's call, and gated by the honest assessment in §9.

**Relationship to prior merged work (important):** this is *not* a new mechanism
from scratch. The three ingredients it needs — the gross-slip **onset gate**
(`loosening_slip_coupling="gross_fraction"`, `1a3aff4`), the realistic
grip-dependent `δ_t ∝ L³` (`k_tr_mode="bending"`, `3b7eff6`), and the **squared
runaway** (`T_resist ∝ F_0`, original engine) — are **already in the code**. The
prior arc built the gate and the regime but gated a **negligible** loosening, so
the runaway never fired (`slip-regime-ktr-insufficient`, `mechanism-supply-arc`).
This design supplies the **one missing quantity: the loosening magnitude.**

---

## 1. Motivation — the falsified-obvious-fix, quantified

Rousseau & Bouzid 2025 (Materials), steel M12×1.75, grade 8.8, disp-controlled
±0.5 mm, 1 Hz, 180 cycles, grips 25 / 29 / 33 mm (`apparatus_notes/
rousseau2025_materials_M12.md`; CSVs `digitized_csv/rousseau2025_steel_t{10,12,14}.csv`):

| grip | DATA final F/F₀ | MODEL final (§4.8) | shape of the data curve |
|---|---:|---:|---|
| 25 mm (t10) | **0.088** | 0.20 | accelerating collapse, still plunging at N=180 |
| 29 mm (t12) | **0.624** | 0.30 | concave, **accelerating** (rate rises 0.029→0.059 /10cyc) |
| 33 mm (t14) | **0.903** | 0.39 | near-**linear** slow settling, ~10% total |

The data is a textbook **grip-dependent finite-time runaway** captured at three
phases: t14 barely started, t12 mid-flight, t10 near-total collapse. The nut-rotation
traces (paper Fig 5, not digitized) confirm: rotation onset matches the preload
drop for t10/t12, **near-zero rotation for t14**.

**Why the model is blind (diagnostic `member_stiffness_diagnostic.py`, §4.8):**
- Loss is ~60-70% **embedding**; **rotational loosening is ~0.3%** (negligible,
  though it fires every cycle). Model spread ~2× (0.20→0.39), data ~10×.
- The model's **only** grip lever is `k_b = E·A_s/L_eff ∝ 1/grip` (~32% over
  t10→t14). It enters *every* mechanism identically as `dF_0 = −k_b·δ` → thickness
  sensitivity is **structurally capped at ~32%**.
- FALSIFIED single-constant fixes (§4.8, diagnostic Parts B–D): `k_j ∝ 1/grip`
  (zero effect — loss is embedding-driven, doesn't touch `k_j`); loosening ×20
  (~2.8×); loosening ×20 + emb×0.25 (~1.1×). None reach 10×.
- The "member compliance / `δ_t ∝ grip³`" lead was separately **falsified
  pre-build** (`mechanism-supply-arc`): `δ_t` spans only ×1.56 (t10→t12) / ×2.3
  (t10→t14), "too sharp for `δ_t` to separate a linear loss," verdict **"the
  switch is nut-rotation ONSET, not slip."**

**Why rotational loosening is negligible — the root cause this design fixes.**
In `RotationalLooseningLoss.rate`:
```
d_theta = (... gates ...) * slip_fraction * (T_loose - T_resist) / k_torsional
k_torsional = k_j_init * d_2 / 2        # = 4e9 · 0.01086 / 2 ≈ 2.17e7 N·m/rad
```
`k_torsional` is an **arbitrary joint-stiffness proxy**, not a torsional stiffness.
The physical torsional compliance of the bolt shank is `G·J/L_eff` with
`J = π·d⁴/32`: for M12 grip-25 that is `77e9·1.37e-9/0.025 ≈ 4.2e3 N·m/rad` —
**~5000× smaller**. Dividing the torque excess by a number ~5000× too large makes
`Δθ ≈ 4.5e-7 rad/cycle` → ~0.3% preload loss over 180 cycles → the runaway the
model **already has** (`T_resist ∝ F_0` → as F₀ falls, `slip_fraction` grows → Δθ
grows) can **never trigger**. The obvious fix is not "make loosening a bigger
tuner"; it is "use the *right* torsional compliance so the existing runaway fires,
and let the existing grip-dependent onset gate decide *where* it fires."

---

## 2. Physical hypothesis

**Transverse self-loosening (Junker ratcheting) requires GROSS SLIP at the
head/thread interface, and whether a joint reaches gross slip is governed by the
bolt's bending resilience, which scales as grip³.** The imposed member displacement
δ is accommodated by (a) elastic bending of the bolt shank over the grip
(compliance `∝ L³/EI`) plus (b) interfacial slip. A **short grip** = stiff bolt =
small elastic bending capacity `δ_t = F_slip·L³/(c_bend·E·I)` → δ forces gross slip
at the bearing/thread → ratcheting back-off. A **long grip** = compliant bolt =
large `δ_t` → the bolt bends elastically and **absorbs δ without gross slip** →
no ratcheting → stable.

Once gross slip begins, the **reserve/runaway** takes over: the nut backs off via
the helix; `dF_0 = −k_b·(p/2π)·Δθ` converts rotation to preload loss; a
**thin-grip bolt has a small elastic reserve** `δ_bolt = F_0/k_b` (high `k_b`), so a
given rotation exhausts more of its preload, dropping `T_resist ∝ F_0`, which raises
`slip_fraction = 1 − T_resist/T_loose`, which raises Δθ → **finite-time collapse**.
A thick-grip bolt with large reserve loses preload slowly per radian *and* mostly
stays below the gross-slip onset → it survives the 180-cycle window.

This is the same physics the classic loosening literature attributes to the ratio
of imposed slip to bolt bending flexibility (Junker; Pai & Hess FE; Jiang; Yang &
Nassar): loosening has a **critical transverse-displacement threshold that is
grip/length dependent**, and above it the process is a self-accelerating ratchet.

---

## 3. The mechanism — one missing quantity, two existing gates

The design activates the runaway by replacing the arbitrary `k_torsional` with the
**physical bolt torsional compliance**, and lets the **already-merged** onset gate
supply the grip dependence.

### 3.1 Onset (grip-dependent) — REUSES merged code
- `k_tr_mode="bending"` → `δ_t = F_slip / (c_bend·E·I/L_eff³)`, `I = π·d_2⁴/64`,
  `F_slip = 0.46·μ·F_0`. This is the `∝ L³` reserve threshold. (merged `3b7eff6`)
- `loosening_slip_coupling="gross_fraction"` → gate
  `g_gs = slip/(slip+δ_t) = max(0, 1 − δ_t/δ_amp)` = gross-slip fraction of the
  stroke. `g_gs → 0` when the bolt absorbs δ elastically (thick grip);
  `g_gs → 1` deep in gross slip (thin grip). (merged `1a3aff4`)

### 3.2 Magnitude (the new, missing quantity)
Replace the runaway's denominator with the physical bolt-shank torsional
compliance scaled by an O(10) efficiency:
```
k_torsional_bending = eta_loose · G · J / L_eff ,     J = π·d_2⁴/32 ,  G = 77 GPa
```
Everything else in `RotationalLooseningLoss.rate` is **unchanged** (same
`T_loose`, `T_resist`, `slip_fraction`, the squared form, `dF_0 = −k_b·lead·Δθ`,
`dE = T_resist·Δθ`):
```
Δθ = g_gs · slip_fraction · (T_loose − T_resist) / k_torsional_bending
```
`eta_loose` is the **one new constant**: the bare shank `G·J/L_eff` alone collapses
t10 in ~25 cycles (too fast); `eta_loose ≈ 7–15` stretches it to the observed
~180-cycle collapse. Physically it is the **ratcheting inefficiency / effective
torsional locking** — the nut does *not* freely relax the full quasi-static
torsional deflection each cycle; only a fraction of the reversible slip becomes
net irreversible back-rotation, and the thread+bearing friction add torsional
resistance in series with the shank. It is the direct analogue of `tr_loose_gain`
(=2.0) and the Archard/creep coefficients: an O(1–10) per-pair empirical constant,
**not a curve knob per data point.**

### 3.3 How grip enters (the levers, explicitly)
- **Onset hinge `g_gs`** (dominant): `δ_t ∝ L³` → for the right `c_bend`, `g_gs`
  goes `0.62 / 0.40 / 0.12` across t10/t12/t14, sending thick grip toward zero
  rotation. This is the lever the prior arc lacked *teeth* for (it gated a
  negligible loosening).
- **Reserve**: `dF_0 = −k_b·lead·Δθ ∝ k_b ∝ 1/L` — thin grip loses more preload
  per radian. (Note: with `k_torsional ∝ 1/L`, `k_b/k_torsional` cancels, so in
  this exact form the reserve is *present but not the active differentiator* — the
  `g_gs` hinge dominates. A grip-independent `k_torsional` variant, §7, keeps the
  reserve active; both were probed.)
- **Runaway** (`T_resist ∝ F_0`, existing): turns the modest `g_gs` spread into a
  finite-time collapse `r(N) = (1 − x)/(1 − c·x)`, `x = N/N_collapse ∝ g_gs`,
  `c = T_resist,0/T_loose ≈ 0.53`. Solving the data for x gives **0.19 / 0.56 /
  0.96** — exactly "barely started / mid-flight / collapsed," reproduced when
  `g_gs` supplies that rate ratio.

---

## 4. Evidence it reaches ~10× (read-only probes, not committed)

Probes ran the real `DynamicStiffnessAnalyzer` with the mechanism injected as a
`LossMechanism` (no engine edit), Stage-A frozen constants, `geometry_for("M12x1.75",
grip)`, disp-mode ±0.5 mm, 180 cycles.

**Best fit** (`k_torsional = eta_loose·G·J/L`, `g_gs` hinge, squared runaway):
`eta_loose ≈ 15`, `c_bend ≈ 0.30`, mild settling —

| | t10 | t12 | t14 | global MAE |
|---|---:|---:|---:|---:|
| **model (proposed)** | **0.077** | **0.572** | **0.856** | **0.054** |
| data | 0.088 | 0.624 | 0.903 | — |
| model (baseline §4.8) | 0.20 | 0.30 | 0.39 | 0.373 |

Curve **shapes** match, not just endpoints — t10 model
`0.844→0.706→0.530→0.270→0.077` (N=40/80/120/160/180) vs data
`0.858→0.790→0.507→0.195→0.088` (accelerating collapse); t14 near-linear.

**Per-mechanism decomposition** (physical settling, `emb_scale=0.16`): t10 loss is
**79% rotation**, t12 **39% rotation**, t14 **0% rotation** (hinge correctly off) —
its ~20% loss is entirely embedding+creep+wear. The mechanism supplies the collapse
where the data has it and stays off where the data is flat.

**Ratchet-form variants** (`Δθ = k_r·(δ_slip/r_bearing)·slip_fraction^p`, a cleaner
kinematic story) fit **worse** (t10 over-collapses to 0, t12 undershoots) — the
squared torque-excess form tracks the accelerating shape better, so this design
proposes the minimal change to the *existing* squared form rather than a new
kinematic.

---

## 5. Engine change (proposed — `dynamic_stiffness_analyzer.py`)

**5.1 Module constant** (near `E_STEEL`, ~line 40):
```python
G_STEEL = 77e9   # Pa, shear modulus (carbon steel) — bolt-shank torsion G*J/L
```

**5.2 New `JointMaterial` fields** (near `k_tr_mode`/`c_bend`, ~line 177):
```python
# Rigidez torsional do loosening (spec 2026-07-07): "legacy" (default,
# k_torsional = k_j_init*d_2/2 ~2e7, backward-compat bit-identical) | "bolt_torsion"
# (fisica: k_torsional = eta_loose*G*J/L_eff, J=pi*d_2^4/32 ~4e3, ~5000x menor ->
# o runaway T_resist~F_0 que ja existe consegue disparar). So faz sentido com o
# gate de onset ligado (loosening_slip_coupling="gross_fraction" + k_tr_mode=
# "bending"), senao dispara em toda junta que escorrega.
loose_torsion_mode: str = "legacy"
# Eficiencia de ratcheting / travamento torsional efetivo [-]. So usado em
# loose_torsion_mode="bolt_torsion". O shank nu (eta=1) colapsa rapido demais
# (~25 ciclos); eta~7-15 estica pro colapso observado (~180). Per-par, O(1-10),
# analogo a tr_loose_gain. Nao usado em "legacy" => default irrelevante p/ compat.
eta_loose: float = 1.0
```

**5.3 In `RotationalLooseningLoss.rate`** — only the `k_torsional` line branches
(the `d_theta` expression, gates, `dF_0`, `dE` are untouched):
```python
if mat.loose_torsion_mode == "bolt_torsion":
    J = np.pi * geom.d_2 ** 4 / 32.0
    k_torsional = max(mat.eta_loose * G_STEEL * J / max(geom.L_eff, 1e-6), 1.0)
else:                                        # "legacy" — bit-identical
    k_torsional = mat.k_j_init * geom.d_2 / 2.0
```
The grip-dependent **onset** is supplied by the existing gates already multiplying
`d_theta` (`loosening_slip_gate` when `loosening_slip_coupling="gross_fraction"`,
which needs `k_tr_mode="bending"` for a real `δ_t`). No signature change.

**5.4 Conservation.** `dF_0 = −k_b·lead·Δθ` and `dE = T_resist·Δθ` both scale with
`k_torsional` identically to today — only the *constant* changes. Energy accounting
(the released elastic energy balances the friction work `T_resist·Δθ`) is preserved
bit-for-bit in structure; the residual behaves as it does for the current loosening.

**Total new surface: 1 module constant + 2 fields + 1 branch.** No new gate, no new
function — reuses `loosening_slip_gate`, `k_tr_transverse`, `c_bend`, the runaway.

---

## 6. Activation / backward-compatibility

- Default `loose_torsion_mode="legacy"` → `k_torsional` unchanged → **every existing
  run/fit/test bit-identical**, `eta_loose` unread. Hard guarantee.
- Meaningful only with the onset gate on (`loosening_slip_coupling="gross_fraction"`
  + `k_tr_mode="bending"`). With those off, `bolt_torsion` would make loosening
  ~5000× stronger with **no** grip gate → over-collapse everywhere; the design
  requires the trio and the validation flag sets all three.
- **Force-mode** (axial, `theta=0` → `F_tr=0`; or `slip_amp_override is None`) →
  `loosening_slip_gate` returns 1.0 and `F_tr < F_slip` path already zeroes
  loosening → mechanism inert regardless of mode. Axial track unaffected.
- Honors `model._v2_tuner_overrides` (the string field passes the type-aware filter
  like `conform_driver`/`k_tr_mode`; `eta_loose` is numeric).

---

## 7. Alternatives considered

- **Grip-independent scaled `k_torsional`** (`= k_j_init·d_2/2 / f`, f≈344): keeps
  the reserve lever `k_b ∝ 1/L` active (no `1/L` cancellation) so the reserve
  *and* the hinge both differentiate grips. Probed; comparable fit. Rejected as the
  headline form because `f` is a bare fudge factor with no physical dimension,
  whereas `eta_loose·G·J/L` names a real compliance × a named efficiency. Worth
  keeping as a fallback mode if the `1/L` cancellation proves undesirable.
- **Slip-arc ratchet** `Δθ = k_r·(δ_slip/r_bearing)·slip_fraction`: most physically
  transparent (ratcheting kinematics), `k_r` = O(0.01) ratchet efficiency. Fit
  worse (§4). Kept as the eventual "clean kinematic" endpoint; not proposed now.
- **Hill onset gate with its own `W`/`s_ref`**: adds a constant with no independent
  provenance. Rejected (knob-avoidance) — the `g_gs` hinge already has the shape.
- **Physical transmitted force `F_tr = min(k_bend·δ, μF_0)`** (the true
  F_amp↔δ_amp coupling, roadmap #4): changes the gross-slip loosening magnitude →
  breaks the frozen shear calibration → forces a canonical re-fit. Deferred, same
  gating as the loosening-slip-gate spec's Approach 3.

---

## 8. Validation — pre-registered, AS IS

New flag `transfer_validation.py --loose-torsion` sets `loose_torsion_mode=
"bolt_torsion"` + `loosening_slip_coupling="gross_fraction"` + `k_tr_mode="bending"`,
with `eta_loose` and `c_bend` as declared inputs; separate `transfer_*_torsion.*`
artifacts (mirrors `--ktr-bending`/`--loosen-coupled`). Constants declared with
provenance before running; verdict recorded either way.

### 8.1 Primary — Rousseau steel spread (the target)
Run t10/t12/t14 with one `(eta_loose, c_bend)` pair (declared, not per-curve).
**Pre-registered pass:** the **spread** `final(t14)/final(t10) ≥ 6×` (baseline
~1.9×; data ~10×) AND monotone ordering `final(t10) < final(t12) < final(t14)` AND
per-curve `final` within **±0.12** of data for **≥ 2 of 3**. (The probe hits
0.077/0.572/0.856 → spread 11×, all three within ±0.06 — but that used a mild
settling input; see §8.3.)

### 8.2 Guard — do not break the transfer sweep or shear calibration
- **Bit-identical OFF (hard gate, unit test):** default `legacy` → the standing V2 /
  calibration suite passes unchanged; `RotationalLooseningLoss.rate` returns
  identical `dF_0`/`dE` for any state.
- **46-curve transfer with the trio ON, universal `(eta_loose, c_bend)`
  (reported AS IS):** median MAE and vs-no-loss **must not regress** below the
  §4.8 baseline (median 0.228, 33/46 beat no-loss). *Expected AS-IS shape:* many
  low-amplitude / partial-slip cases stay gated OFF (`g_gs=0`) → unchanged; genuine
  transverse-collapse cases (Liu2025, Yang2019) should **improve** (they currently
  under-collapse with dano-OFF); some gross-slip cases the frozen `c_bend`
  mis-classifies may **regress**. Net expected neutral-to-slightly-better on
  collapse cases, bounded by `c_bend` regime accuracy — the same ceiling the
  `loosening-slip-gate` spec named.
- **Shear calibration (UFU 4 profiles):** inert by construction — M16 grip-40mm at
  δ=0.5 mm gives `δ_t ≈ 1.6 mm ≫ δ_amp` → `g_gs ≈ 0` → mechanism contributes ~0
  (probe confirmed: final 0.327 OFF vs 0.364 with the trio ON — the trio *reduces*
  the already-tiny rotation, it does not inject loss). The profiles keep
  `loose_torsion_mode="legacy"` regardless → zero perturbation.

### 8.3 Honest tension pre-registered (the t14-level caveat)
Reproducing t14 = 0.903 **also** requires the non-rotation settling
(embedding+creep+wear) to be milder for this rig: the decomposition shows the
mechanism correctly puts **0% rotation** on t14, yet settling alone gives ~20% loss
(→ 0.80) vs the data's ~10%, and the best fit reaches 0.856 only by driving
`emb_scale → 0.05` (sub-physical). **The rotation mechanism supplies the t10/t12
collapse; t14's high retention additionally depends on the separate over-aggressive
settling** (`MODEL_LEGITIMACY.md` §4.8 "over-predicts loss for t12/t14"; roadmap
#10 grip→stiffness scaling). The pre-registered Rousseau run therefore declares the
settling input (Rz class / emb provenance) explicitly and reports the split, rather
than crediting the whole triple to this mechanism.

---

## 9. Risks & honest assessment — clean FORM or smuggled constant?

**The FORM is clean and transferable.** Grip-dependent gross-slip onset
(`δ_t ∝ L³`, bolt bending) feeding the model's own squared runaway
(`T_resist ∝ F_0`) through the **physical** torsional compliance `G·J/L_eff` is
first-principles in its structure and grip-scaling. It builds on two already-merged
mechanisms and changes a **single arbitrary constant** (`k_j_init·d_2/2`, which was
never a torsional stiffness) into a named physical one. It makes onset
grip-dependent by construction and is default-inert.

**It carries fitted constants — honestly, two, both per-rig (consistent with §8
doctrine "forms transfer, constants are per-pair/rig"):**
1. **`eta_loose ≈ 7–15`** (NEW): a real ratcheting/torsional-locking efficiency, but
   its *value* is fitted to Rousseau, not derived. O(1–10), same status as
   `tr_loose_gain`, `K_archard`, `C_creep`. Defensible as physical, **not**
   first-principles.
2. **`c_bend ≈ 0.30`** (EXISTING): the amplitude-sweep calibration put it at 1.0;
   Rousseau needs ~0.30. `c_bend` is genuinely per-rig (`mechanism-supply-arc`:
   "single global `c_bend` can't fully separate") — e.g. the same 0.30 makes the
   M16 shear partial-slip, which is why the shear loosening must be carried by wear,
   not rotation. This tension is real and documented.

**The sharpest honesty point (§8.3):** the mechanism **does not, alone, reach the
triple.** It cleanly supplies the missing *collapse* (t10 0.20→0.08, t12 partial),
but t14 = 0.903 needs the *separate* settling-too-aggressive problem fixed. Claiming
this mechanism "reproduces the 10×" is only true in conjunction with a milder
settling input — which the fit currently smuggles as `emb_scale=0.05`. So: **a
clean, transferable FORM that resolves the rotation-onset half of §4.8, with one
new per-rig empirical constant, and an explicit dependency on the (orthogonal,
already-known) settling-scale issue for the other half.**

**Other risks:**
- **No arrest.** The runaway has no equilibrium: any joint past onset collapses to
  F₀=0 *eventually*. The data captures t12 mid-flight at N=180 (test stopped); the
  mechanism predicts t12 would fully collapse if cycled longer. For marginal joints
  this may **over-predict long-run loosening**. A stabilizing arrest / partial-slip
  equilibrium is a **separate missing form** (`slip-regime-ktr-insufficient`,
  roadmap #4) — out of scope here, flagged.
- **Erosion-into-gross-slip.** As embedding/creep nibble F₀, `δ_t ∝ F_slip ∝ F_0`
  shrinks, so a thick-grip joint just above onset can be pushed *into* gross slip
  after settling — making t14's stability sensitive to the settling level (couples
  to §8.3). Mitigated but not eliminated by embedding saturation.
- **`c_bend` sensitivity.** The `g_gs` hinge is sharp near `δ_t = δ_amp`; the triple
  placement is sensitive to `c_bend`. This is the "too sharp" concern the prior arc
  raised — here it is answered by the *runaway* doing the sharpening (a modest `g_gs`
  spread → large `final` spread), not by `δ_t` linearity, but the sensitivity to
  `c_bend` remains a calibration burden.

---

## 10. Files (if implemented)

| File | Change |
|---|---|
| `src/.../numerical/dynamic_stiffness_analyzer.py` | `G_STEEL` const; `JointMaterial.{loose_torsion_mode, eta_loose}`; `k_torsional` branch in `RotationalLooseningLoss.rate` |
| `tests/test_member_rotation_instability.py` | new (TDD): bit-identical `legacy`; `bolt_torsion` k_torsional value; grip-monotone spread; force-mode inert; shear-case inert |
| `New_Theory/transfer_validation.py` | `--loose-torsion` flag (sets the trio); `_torsion` artifacts |
| `New_Theory/member_stiffness_diagnostic.py` | add a Part E running the proposed form (read-only demo) |
| `New_Theory/MODEL_LEGITIMACY.md` | §4.8 addendum (verdict AS IS) + changelog |

## 11. Scope / out-of-scope

- **OUT:** canonical re-fit; the settling-scale fix (roadmap #10, needed for the
  t14 *level*); a runaway-arrest form (roadmap #4); the physical transmitted-force
  coupling; any change to the canonical `shared` block.
- **Foundational, opt-in:** like `k_tr_mode`/`conform_driver`/`W_crit`, a capability
  inert by default until a run/experiment opts in. It **composes with** the merged
  bending-`k_tr` and gross-fraction gate (needs both) and is orthogonal to damage
  (`d_theta` vs `dD`).
