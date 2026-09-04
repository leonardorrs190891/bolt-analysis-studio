# Runaway-Arrest / Partial-Slip Equilibrium — Design (2026-07-07)

**Goal:** Give the V2 rotational self-loosening a **physically-motivated arrest** so a
joint past the loosening onset settles at a **stable residual preload** (an S-curve /
plateau) instead of running to `F_0 = 0`. This supplies the **separate missing form**
flagged by roadmap #4 and by the member-stiffness spec §9 (`2026-07-07-member-stiffness-
rotation-instability-design.md`): `loose_torsion_mode="bolt_torsion"` restores
grip-sensitive rotation but **over-collapses** (any joint past onset → `F_0=0`, no
arrest), which is why #10 is a *"validated capability, NOT adopted"* (`MODEL_LEGITIMACY.md`
§4.8). This arrest is what makes #10 **adoptable**. Opt-in, default bit-identical,
physically motivated, provenance-honest, AS IS.

**Status:** design proposal (read-only investigation; no engine code changed). The
go/no-go and any implementation are the professor's call, gated by the honest
assessment in §9.

**Relationship to prior work:** orthogonal to and composable with the merged trio
(`loose_torsion_mode="bolt_torsion"` `4e…`, `loosening_slip_coupling="gross_fraction"`
`1a3aff4`, `k_tr_mode="bending"` `3b7eff6`). Those supply the grip-dependent **onset +
runaway magnitude**; this supplies the **arrest** that the runaway lacks. It is a single
new gate in the same family as `slip_onset_gate` / `conformation_gate` /
`loosening_slip_gate` — all of which already multiply the loosening `d_theta`.

---

## 1. The runaway, precisely

`RotationalLooseningLoss.rate` (`dynamic_stiffness_analyzer.py` ~L792–875) synthesises a
two-factor off-torque and compares it to the joint's holding torque:

```
F_tr        = F_amp · sin(theta)                       # fixed drive (input F_amp)
Phi_tr_act  = tr_loose_gain · Phi_tr_correction        # =2.0 once past the slip threshold
T_loose     = Phi_tr_act · cos(beta) · F_tr · d_2/2    # ∝ F_amp  (does NOT fall with F_0)
T_resist    = mu_thread·F_0·d_2/(2cosα) + mu_bearing·F_0·r_bearing   # ∝ F_0
slip_fraction = (T_loose − T_resist) / T_loose         # → 1 as F_0 → 0
d_theta     = gates · slip_fraction · (T_loose − T_resist) / k_torsional
dF_0        = −k_b · (p/2π) · d_theta                  # helix converts rotation → preload loss
```

The instability is structural: **`T_loose` is anchored to the fixed input `F_amp`, while
`T_resist ∝ F_0`.** As the nut backs off and `F_0` falls, `T_resist` falls, so
`slip_fraction → 1` and `(T_loose − T_resist) → T_loose` — the per-cycle `d_theta`
*grows* as `F_0` shrinks. The only fixed point is `F_0 = 0` (or `T_loose ≤ T_resist`,
which is the *onset threshold* above which the mechanism is simply off, not a floor
below it). In `legacy` `k_torsional` the loss is ~0.3%/run so this never bites; with
`bolt_torsion`'s physical `k_torsional` (~5000× smaller) it **fires and finite-time
collapses** (`MODEL_LEGITIMACY.md` §4.8: *"t10 over-collapsa pra 0 … sem forma de
ARRESTO"*).

**What the data actually does (`digitized_csv/`, read-only):**

| case | rig | data final F/F₀ | shape at test end |
|---|---|---:|---|
| Rousseau steel **t10** (grip 25) | M12, ±0.5 mm, 1 Hz, 180 cyc | **0.088** | S-curve; rate **decelerates** 0.078→0.059→0.049 /10cyc → floor ~0.05–0.09 |
| Rousseau steel **t12** (grip 29) | " | **0.624** | concave, still descending (mid-flight) |
| Rousseau steel **t14** (grip 33) | " | **0.903** | near-linear slow settling (~10%), rotation ≈ 0 |
| Liu2025 M16 **amp0.25** | 12.5 Hz | **0.68** | long plateau then slow decline |
| Liu2025 M16 **amp0.4/0.8**, Yang2019 5 Hz | " / 5 Hz | 0.33 / **0.00** | **accelerating** collapse (genuine runaway) |

Two facts drive this design: (a) **t10 decelerates into a residual ~0.05–0.09** — an
*arrest*, not a finite-time plunge; and (b) some cases (Yang 5 Hz → exactly 0) are
**genuine collapses** that must be preserved. The arrest must stop the false collapse
(t10) without lifting the true ones.

---

## 2. Physical hypothesis — a self-locked stick core

**Transverse ratcheting can only drain the preload held in *excess* of a self-locked
core; the core cannot be shed no matter how many cycles pass.**

Under oscillating transverse slip the head/thread bearing contact is in **Cattaneo–
Mindlin partial slip**: an annular micro-slip zone surrounds a central **stick zone**
that never fully slips within a cycle. The stick zone restores static thread friction
each half-cycle and keeps a fraction of the clamp force locked against the unscrewing
helix torque. Equivalently (thread view): a plain metric thread is **self-locking**
under pure preload (helix angle `β` < friction angle `arctan μ`); transverse slip only
momentarily "fluidizes" the flank contact enough to let the helix off-torque win, and
the fraction it can fluidize scales with the *excess* clamp above the self-locking limit.
Either way there is a **residual preload `F_min` that the transverse mechanism cannot
remove.** As loosening proceeds and `F_0 → F_min`, the drainable excess `(F_0 − F_min)`
vanishes and the back-rotation rate → 0 → **stable equilibrium at `F_min`**.

`F_min` scales with the seated preload (it is the stick-zone fraction of the clamp), so
the natural dimensionless parameter is `f_min = F_min / F_0_init`. This is the same
"forms transfer, constants are per-pair/rig" doctrine as the rest of the model (§8):
the *form* (excess-only ratcheting) is first-principles; the *value* `f_min` is a
per-pair fitted constant, O(0.05–0.10).

---

## 3. The mechanism — one gate, one parameter

A **closing gate** on the loosening drive, mirroring the existing
`conformation_gate`/`slip_onset_gate` structure but driven by the **preload deficit**
rather than pressure-weighted or raw slip work:

```
F_min             = loose_arrest_floor · F_0_init
self_locking_gate = max(0, 1 − F_min / F_0)          # ∈ [0,1); 1.0 exactly when floor=0
```

It multiplies the loosening `d_theta` alongside the three gates already there:

```
d_theta = g_onset · conformation_gate · g_slip_regime · self_locking_gate
          · k_scale · slip_fraction · (T_loose − T_resist) / k_torsional
```

Everything upstream is **unchanged** — `T_loose`, `T_resist`, `slip_fraction`, the
squared runaway, `k_torsional` (legacy or `bolt_torsion`), `dF_0 = −k_b·(p/2π)·d_theta`,
`dE = T_resist·d_theta`. The gate simply says **only `(F_0 − F_min)` participates**:
`d_theta ∝ (F_0 − F_min)/F_0 × (the existing drive)`.

### 3.1 Why this yields a *stable* equilibrium (and the transmissibility cap does not)
- **Stability.** Past onset the ungated `d_theta > 0`, so `dF_0 < 0`. With the gate,
  `dF_0 = 0 ⟺ self_locking_gate = 0 ⟺ F_0 = F_min`. For `F_0 > F_min` the gate is
  positive → `F_0` decreases *toward* `F_min`; at `F_0 = F_min` it stops; the gate is
  clamped `≥ 0` (no spontaneous re-tightening), so loosening cannot push `F_0` below
  `F_min`. **`F_min` is a stable absorbing floor.** The approach is logarithmic
  (`gate ≈ (F_0−F_min)/F_0` near the floor), so within a finite test window the residual
  sits slightly *above* `F_min` — consistent with t10 still creeping at N=180.
- **Why not "scale `T_loose` with the carried load" (options a/d).** The obvious fix —
  drive `T_loose` by the Coulomb-transmissible force `min(F_amp, μ_tr·F_0)` instead of
  fixed `F_amp` — *does* bound `slip_fraction < 1` (kills the finite-time singularity),
  but it does **not** produce a controllable positive residual: it makes **both**
  `T_loose ∝ F_0` and `T_resist ∝ F_0`, so the net back-torque is homogeneous of degree
  1 in `F_0` and its only zero is `F_0 = 0`. The system is then **collapse-or-nothing**
  (a·μ_tr > b → exponential collapse to 0; a·μ_tr < b → loosening off entirely). A probe
  confirmed this: with `μ_tr = 0.30` the drive is throttled so hard that t10 *settles at
  0.73* (loosening nearly extinguished), not a controlled arrest. **A stable interior
  residual requires a symmetry-breaking term that is not ∝ F_0** — the self-locked core
  `F_min` (an `F_0`-independent locked clamp) is exactly that term, and is more physical
  and more minimal (one parameter) than a transmissibility cap + separate seating torque
  (two).

### 3.2 How it composes with #10 (`bolt_torsion`) — makes it adoptable
The gate multiplies `d_theta` **after** `k_torsional` is formed, so it is orthogonal to
the legacy/`bolt_torsion` branch:
- `bolt_torsion` sets the **onset location and runaway magnitude** (physical
  `k_torsional = eta_loose·G·J/L_eff`, grip-gated by `gross_fraction`).
- `self_locking_gate` sets the **floor** the runaway decelerates into.
Together the past-onset trajectory **accelerates then decelerates → an S-curve arresting
at `F_min`**. This directly removes the blocking caveat in §4.8 / #10 §9 (*"o runaway não
tem equilíbrio; roadmap #4"*). With `loose_arrest_floor=0` the composition is **exactly
#10 as merged** (gate ≡ 1.0), so adopting the floor is a strictly additive opt-in.

---

## 4. Evidence (read-only probes, not committed)

Probes injected the gate as a `LossMechanism` subclass over the **real**
`DynamicStiffnessAnalyzer` (no engine edit), Stage-A frozen constants,
`geometry_for(...)`, disp-mode, trio ON (`bolt_torsion` + `gross_fraction` + `bending`,
`eta_loose=15`, `c_bend=0.30`, mild settling `emb_scale=0.16` — the same inputs the #10
probe used). Gate applied to the **loosening `dF_0`/`dE` only**.

**Primary — Rousseau steel (one universal `f_min`):**

| grip | data final | #10 no-floor (`f_min=0`) | **+ floor `f_min=0.05`** |
|---|---:|---:|---:|
| t10 (25) | 0.088 | **0.000** (over-collapse) | **0.091** |
| t12 (29) | 0.624 | 0.502 | 0.541 |
| t14 (33) | 0.903 | 0.869 | 0.869 (floor inert, `g_gs≈0`) |

t10 turns from a finite-time collapse to 0 into a **stable arrest at 0.091 ≈ data
0.088**; the trajectory decelerates near the floor (matches the data's shrinking end-of-
curve steps). Grip **ordering preserved and spread ≈ 9.5×** (0.869/0.091; data 10.3×;
`legacy` baseline ~1.9×). The floor is **inert on t14** (never approaches `F_min`), so it
does not disturb the low-loss end.

**Sweep of `f_min`** (t10): `0.00→0.000`, `0.05→0.091`, `0.09→0.185`, `0.15→0.294`. The
residual is monotone in `f_min` and lands in the data band at `f_min≈0.05`. (Because the
approach is logarithmic, the finite-window residual is ~2× the asymptotic `F_min`.)

**Guard — shear âncora interna inertness (even when turned on).** Loosening-only gate, M16 grip-40
δ0.5 `legacy` mode (the profile's mode): `f_min=0→0.3273`, `0.05→0.3315`, `0.09→0.3348`
— a **<0.005 perturbation**, because shear-âncora interna loss is wear-dominated and the rotation it
throttles is tiny. (The profiles keep `loose_arrest_floor=0` regardless → *zero*
perturbation.) NB: applying the gate to **wear too** perturbs shear-âncora interna materially
(0.3273→0.3573) — so the design scopes the gate to **loosening only** (§7).

**Guard — genuine collapses.** With `f_min < FLOOR_TRIM (0.10)` the arrested residual
(~0.05–0.09) sits **below the analysis floor**, so cases the model genuinely collapses
keep their sub-0.10 tail (trimmed) and still read as collapsed; the floor never lifts a
curve above 0.10. (Yang 5 Hz → 0 and Liu amp0.4/0.8 are not reached by rotation in the
model at all — a *separate* pre-existing gap — so the floor is doubly harmless there.)

---

## 5. Engine change (proposed — `dynamic_stiffness_analyzer.py`)

**5.1 New `JointMaterial` field** (next to `loose_torsion_mode`/`eta_loose`, ~L197):
```python
# Arresto do runaway de loosening (spec 2026-07-07, roadmap #4 / #10 §9): fracao da
# pre-carga inicial AUTO-TRAVADA (nucleo de stick Cattaneo-Mindlin / limite de
# auto-travamento da rosca) que o ratcheting transverso NAO consegue drenar. So a
# pre-carga em EXCESSO ao piso F_min = loose_arrest_floor*F_0_init afrouxa; quando
# F_0 -> F_min o drive -> 0 => equilibrio estavel (runaway vira S-curve/plato).
# 0.0 = sem piso (gate=1.0 exato, backward-compat bit-identical). Per-par, O(0.05-
# 0.10), analogo a eta_loose/tr_loose_gain. So morde com o runaway LIGADO
# (loose_torsion_mode="bolt_torsion"); em legacy o loosening ja e ~0.3%. Mantenha
# < FLOOR_TRIM (0.10) do harness p/ nao levantar colapsos genuinos acima do trim.
loose_arrest_floor: float = 0.0
```

**5.2 New gate function** (next to `conformation_gate`, ~L399):
```python
def self_locking_gate(state: SlowState, mat: JointMaterial) -> float:
    """Gate de arresto por auto-travamento (spec 2026-07-07).

    Retorna g in [0,1) que MULTIPLICA a perda de pre-carga do loosening rotacional.
    So a pre-carga em excesso ao piso de auto-travamento F_min = loose_arrest_floor*
    F_0_init participa do ratcheting transverso: g = max(0, 1 - F_min/F_0). Quando
    F_0 -> F_min o drive -> 0 => equilibrio estavel (runaway vira S-curve). Espelha
    conformation_gate (closing 1->0) mas o driver e o DEFICIT de pre-carga, nao o
    trabalho de conformacao. Com loose_arrest_floor<=0 retorna 1.0 exato
    (backward-compat bit-identical; guarda o F_0<=0)."""
    if mat.loose_arrest_floor <= 0.0 or state.F_0 <= 0.0:
        return 1.0
    F_min = mat.loose_arrest_floor * max(state.F_0_init, 0.0)
    return max(0.0, 1.0 - F_min / max(state.F_0, 1e-9))
```

**5.3 One term in `RotationalLooseningLoss.rate`** (the `d_theta` product, ~L867 — the
only change; `slip_fraction`, `T_loose`, `T_resist`, `dF_0`, `dE` untouched):
```python
d_theta = (g * conformation_gate(state, mat) * g_slip_regime
           * self_locking_gate(state, mat) * k_scale        # <-- added factor
           * slip_fraction * (T_loose - T_resist) / max(k_torsional, 1.0))
```

**5.4 Conservation.** The gate multiplies `d_theta`, so `dF_0 = −k_b·(p/2π)·d_theta`
and `dE = T_resist·d_theta` scale **together** by `g` — identical structure to the three
existing gates. The released elastic energy still balances the friction work; the
conservation residual behaves exactly as for the current loosening. No accounting change.

**Total new surface: 1 field + 1 function + 1 multiplicative factor.** No new state, no
signature change, no new accumulator (unlike `slip_onset_W`/`W_conf` this floor reads the
live `F_0`/`F_0_init` — no bookkeeping).

---

## 6. Activation / backward-compatibility

- Default `loose_arrest_floor=0.0` → `self_locking_gate` returns **1.0 exactly** →
  every existing run/fit/test **bit-identical** (hard guarantee, including #10 with the
  floor off = #10 as merged).
- Meaningful only with the runaway on (`loose_torsion_mode="bolt_torsion"` + the onset
  trio); in `legacy` the loosening is ~0.3% so the floor is negligible.
- **Force-mode / axial** (`theta=0`, `slip_amp_override is None`): loosening already
  inert (`loosening_slip_gate`/`F_tr<F_slip`), so the floor is doubly inert. Axial track
  unaffected.
- **Shear-âncora interna profiles** keep `loose_arrest_floor=0` → untouched (and near-inert even if
  on, §4).
- Honors `model._v2_tuner_overrides` (`loose_arrest_floor` is numeric → passes the
  type-aware filter).

---

## 7. Alternatives considered

- **Transmissibility cap on the drive** `F_tr_eff = min(F_amp·sinθ, μ_tr·F_0)` (options
  a/d). Physically the Coulomb-transmissible force, and it *does* remove the finite-time
  singularity (bounds `slip_fraction<1`). **Rejected as the sole mechanism**: with both
  torques then `∝ F_0`, it is collapse-or-nothing — no controllable positive residual
  (§3.1, probe: t10→0.73 = loosening extinguished). Kept as the *deeper justification*
  for the floor (the floor is the reduced-order closure of "drive falls with transmitted
  force **and** a locked core resists").
- **Transmissibility cap + separate seating torque `T_lock`.** Gives a true residual
  `F_0* = T_lock/(a·μ_tr − b)`, but needs **two** fitted constants and forces `μ_tr` far
  above `μ_bearing` (awkward provenance). Rejected for the single-parameter floor.
- **Preload-loss-keyed closing gate (like `conformation_gate`, raw slip work).** Would
  arrest, but its driver (accumulated slip work) scales with the loss itself, so the
  plateau/collapse split does not fall out cleanly and it adds a new accumulator +
  reference constant. Rejected (the deficit-driven floor is simpler and has a crisper
  physical meaning).
- **Gate applied to wear too** (hard multi-mechanism floor, mirroring
  `conformation_gate`). More physical as a *true* preload floor, but perturbs the
  wear-calibrated shear âncora interna (§4, 0.327→0.357). Deferred/optional; the runaway to arrest
  is rotational, so the headline scopes the gate to loosening. If a wear-dominated
  collapse later leaks past `F_min`, extend then.

---

## 8. Validation — pre-registered, AS IS

New flag `transfer_validation.py --loose-arrest` sets the trio + `loose_arrest_floor`
(declared, not per-curve); separate `transfer_*_arrest.*` artifacts (mirrors
`--loosen-coupled`). Constants declared with provenance before running; verdict recorded
either way.

### 8.1 Primary — Rousseau steel arrest (the target)
One declared `(loose_arrest_floor, eta_loose, c_bend, emb_scale)` across t10/t12/t14.
**Pre-registered pass:**
- **t10 arrests, not collapses:** `final(t10) ∈ [loose_arrest_floor, loose_arrest_floor
  + 0.10]` (was 0.000; probe 0.091) AND the end-of-run per-cycle rate < the mid-curve
  peak rate (deceleration signature).
- **Monotone ordering** `final(t10) < final(t12) < final(t14)` (probe 0.091<0.541<0.869).
- **Spread** `final(t14)/final(t10) ≥ 6×` (`legacy` ~1.9×; data 10.3×; probe 9.5×).
- **Floor inert on t14:** `|final(t14; floor on) − final(t14; floor off)| < 0.01`
  (probe 0.869 = 0.869).

### 8.2 Guards
- **Bit-identical OFF (hard, unit test):** `loose_arrest_floor=0` → `self_locking_gate`
  returns 1.0 and `RotationalLooseningLoss.rate` returns identical `dF_0`/`dE` for any
  state; the standing V2 / calibration suite passes unchanged. `bolt_torsion` + floor-off
  reproduces #10 bit-for-bit.
- **Shear calibration (âncora interna 4 profiles):** profiles keep `loose_arrest_floor=0` →
  untouched; even forced on (loosening-only gate) the final perturbs **< 0.005** (probe
  0.3273→0.3315).
- **46-curve transfer, trio + floor, universal `f_min` (reported AS IS):** median MAE
  **must not regress** below the §4.8 baseline (median 0.228, 33/46 beat no-loss) nor
  below trio-no-floor. *Expected AS-IS:* low-amplitude / thick-grip cases stay gated
  (`g_gs≈0` or `F_0 ≫ F_min`) → unchanged; the fast-collapsing rotation cases stop at a
  physical residual instead of 0. **Collapse guard:** with `loose_arrest_floor < FLOOR_TRIM
  (0.10)` the arrested residual is below the trim, so genuine collapses keep reading as
  collapsed (no curve lifted above 0.10). This constraint is part of the pass.

### 8.3 Honest tension pre-registered
The floor sets **where fast-collapsing cases stop**; it does **not** by itself reproduce
the plateau *levels* of t12 (0.624) / t14 (0.903) / Liu amp0.25 (0.68) — those are set by
the **approach rate** (`gross_fraction` gate `g_gs`, drive, settling), which is the
orthogonal §8.3/#10 concern (over-aggressive settling; grip→stiffness scaling, roadmap
#10). The Rousseau run therefore declares the settling input explicitly and reports the
split (arrest vs approach-rate), rather than crediting the whole triple to this gate.

---

## 9. Risks & honest assessment — clean FORM or another fitted constant?

**The FORM is clean, minimal, and yields a *true* equilibrium.** "Only preload in excess
of a self-locked core participates in transverse ratcheting" is first-principles
(Cattaneo–Mindlin partial slip / thread self-locking), monotone, default-inert, gives a
provably **stable** interior fixed point (§3.1) — not merely a soft exponential landing —
and drops in as **one factor** in the existing `d_theta` product with no new state and no
conservation change. It composes with #10 by construction and is exactly what turns
#10's over-collapse into an S-curve (the reason #10 is "validated, not adopted").

**It carries one new fitted constant — honestly:**
1. **`loose_arrest_floor ≈ 0.05` (NEW):** a real self-locked-clamp fraction, but its
   *value* is fitted to Rousseau, not derived. Per-pair, O(0.05–0.10), same status as
   `eta_loose`, `tr_loose_gain`, `K_archard`, `C_creep`. Defensible as physical, **not**
   first-principles in value. (It must be declared per-rig — §8 doctrine.)

**The sharpest honesty points:**
- **The floor does not explain the plateau *spectrum* (§8.3).** It converts a false
  finite-time collapse (t10) into a physical residual and preserves the grip ordering; it
  does **not** derive t12/t14/Liu-amp0.25 levels — those need the approach-rate + settling
  work already flagged. Claiming this gate "reproduces the residuals" is only true for the
  *arrested* cases; for the apparent plateaus it is the drive/settling, not the floor.
- **Universality of `f_min`.** The probe used one `f_min` for the target; whether a single
  value transfers across rigs is unknown (per-pair by doctrine). Declared per-rig in
  validation; a cross-rig sweep is the honest test, expected to need re-declaration.
- **Wear leak.** Scoped to loosening (to protect wear-calibrated shear), so in a
  *wear-dominated* collapse wear could still drag `F_0` below `F_min`. Fine for
  loosening-dominated Rousseau (t10 arrests at 0.091 ≫ the 0.05 asymptote); a hard
  multi-mechanism floor (gate on wear too) is the documented extension (§7).
- **Approach is logarithmic**, so the finite-window residual is ~2× the asymptotic
  `F_min`; the mapping `f_min → observed residual` depends on the test length. Declared,
  not hidden.

**Bottom line:** a **clean, minimal, first-principles FORM** that gives a genuine stable
residual and makes #10 adoptable, with **one** new per-rig empirical constant
(`loose_arrest_floor`) and an explicit, pre-registered dependency on the (orthogonal,
already-known) approach-rate/settling issue for the plateau *levels*. Confidence: **high
on the form and the stability/composition proof; medium on the value transferring
cross-rig** (per-pair, like every other constant in §8).

---

## 10. Files (if implemented)

| File | Change |
|---|---|
| `src/.../numerical/dynamic_stiffness_analyzer.py` | `JointMaterial.loose_arrest_floor`; `self_locking_gate(...)`; one factor in `RotationalLooseningLoss.rate` `d_theta` |
| `tests/test_runaway_arrest.py` | new (TDD): bit-identical floor=0; gate value; stable-floor monotone convergence; force-mode inert; shear-case near-inert; #10+floor-off == #10 |
| `New_Theory/transfer_validation.py` | `--loose-arrest` flag (trio + `loose_arrest_floor`); `_arrest` artifacts |
| `New_Theory/member_stiffness_diagnostic.py` | add a Part E running trio+floor (read-only demo) |
| `New_Theory/MODEL_LEGITIMACY.md` | §4.8 addendum (arrest verdict AS IS) + changelog |

## 11. Scope / out-of-scope

- **OUT:** canonical re-fit; the settling-scale / approach-rate fix (roadmap #10, for the
  plateau *levels*); the physical `F_amp↔δ_amp` transmissible-force coupling (roadmap #4,
  the mechanistic parent of §3.1); extending the gate to wear; any change to the canonical
  `shared` block.
- **Foundational, opt-in:** like `k_tr_mode`/`loose_torsion_mode`/`conform_driver`, a
  capability inert by default until a run/experiment opts in. It **composes with** the
  merged trio (needs `bolt_torsion` to matter) and is orthogonal to damage (`d_theta` vs
  `dD`) and to conformation (deficit-driven vs pressure-driven — complementary: at normal
  preload conformation ≈ 1 and the floor arrests; at sobretorque the floor ≈ 1 and
  conformation arrests).
```
