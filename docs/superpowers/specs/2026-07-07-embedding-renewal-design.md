# Embedding renewal on re-tightening (roadmap #5) — design

**Date:** 2026-07-07
**Context:** V2 energy engine (`dynamic_stiffness_analyzer.py`); brainstormed with
Prof. Leonardo. **Status:** design for review (pre-implementation).

---

## 1. Motivation

Roadmap #5: *"the model doesn't reset `δ_emb` on re-tightening; physical reality may
differ."* Today the engine has **no re-tighten operation** — every condition is a
fresh simulation from a fixed initial state:

- **reusada** → `{emb_consumed_frac=1.0, D_init=0.3}` (embedding exhausted).
- **reaperto** → `{D_init=0.3}` only ⇒ `emb_consumed_frac=0` ⇒ **fresh FULL embedding**,
  yet it fits MAE 0.038 with zero curve tuners.

Re-tightening *already-bedded* surfaces getting the *same* fresh embedding as a virgin
joint is physically suspect — the 0.038 fit may hold for the wrong reason (phantom
embedding standing in for damage).

**Falsification target now exists.** Liu 2022 (*Structures* 44:1303, M12×1.75 cl.8.8,
35CrMn, 45-steel plates, transverse disp-controlled 0.3 mm @ 12.5 Hz, T=80 N·m) is a
dedicated re-tightening study, **already digitized (21 curves)** and wired in
`validation_cases.py`; `apparatus_notes/liu2022_istruc_retightening.md` tags it the
**PRIMARY embedding-renewal target**. Curve groups (R_F normalised to first-tightening F₀):

| Group | Condition |
|---|---|
| `liu2022_fig5_{dry,oil}_F*` | first tightening (2 lube × 2 achieved-F₀) |
| `liu2022_fig6a_dry_release_t0..t3` | dry, release-angle retighten |
| `liu2022_fig6b_oil_release_t0..t3` | oil, release-angle retighten — **restores ~100% F₀** |
| `liu2022_fig7a_oil_direct_t0..t3` | oil, direct-to-torque retighten — restores ~88–90% |
| `liu2022_fig8_multi_t0..t4` | dry, multiple retightens; **t4 = fatigue fracture (trim)** |

---

## 2. Physical hypothesis (from the apparatus note)

`D` **persists** across retightenings while `δ_emb` **partially renews** (surface damage
exposes fresh asperities). Consequences, from *one* physics:

- **Dry** (μ≈0.2): more slip work ⇒ faster `D` growth (via `c_D`) ⇒ each retighten
  recovers less and loosens faster.
- **Oil** (μ≈0.1): low slip work ⇒ `D` stays low ⇒ ~100% restore, slow loosening.

**Dry vs oil differ ONLY by the input μ** — the whole `D`-trajectory contrast must emerge
from that single difference, with all physics constants shared. That is the test.

---

## 3. Mechanism design (Approach 1: quasi-static `retighten()` state-operation)

Rejected alternatives: (2) model each `tN` curve as an independent joint with per-`t`
calibrated initial state — curve-fitting per phase, can't predict the sequence; (3) full
re-torque dynamics (Newmark during tightening) — overkill for a quasi-static preload.

### 3.1 The operation — `DynamicStiffnessAnalyzer.retighten(...)`

A discrete state transformation applied *between* cycling phases. Signature:

```python
def retighten(self, applied_torque: float | None = None,
              new_F0: float | None = None) -> None
```

Exactly one of `applied_torque` (predict F₀, §3.2 — the primary path) or `new_F0`
(explicit override, for tests / measured-input studies) must be given.

**State transformation:**

| State | On retighten | Rationale |
|---|---|---|
| `F_0` | ← F₀_achieved (§3.2) or `new_F0` | the re-torque re-establishes preload |
| `F_0_init` | **unchanged** | GW stiffness reference is the joint's fundamental stiffness, not re-set by torque |
| `delta_emb` | ← `delta_emb·(1 − k_emb_renew·D)`, clamped `[0, target]` (§3.3) | damage exposes fresh embedding capacity |
| `delta_creep` | persist | permanent viscoelastic deformation |
| `delta_wear` | persist | removed material does not return |
| `theta_loose` | **← 0** | the nut is physically turned back in the tightening direction (confirmed) |
| `D` | persist | damage does not heal; grows further next phase |
| `W_conf` | persist | high-pressure conformation is permanent |
| `W_slip_acc` | persist | accumulated slip history (only matters when `slip_onset_W>0`, off in baseline; revisit if a dataset needs per-phase re-incubation) |
| `_cycle_counter` | **persist** | it is the **creep clock** (`CreepLoss` uses `t = cycle_N/freq`); resetting to 0 would restart creep from `t_0` and multi-count the early fast-creep (~4× over 4 phases). The per-phase plot x-axis (data restarts at 0 each retighten) is reconstructed **harness-side**, not in the engine. |
| `history` | persist | full trace across phases (harness records R_F per cycle externally) |
| energy budget | **rebase** (§3.5) | conservation validated per cycling segment |

### 3.2 Torque → preload (recovery), falsify-first

Motosh tightening-torque balance, reusing the engine's **existing** friction terms
(cf. `T_resistance`) plus the lead (pitch) term:

```
T_tighten(F0) = F0 · [ lead_per_radian
                       + μ_thread · d_2 / (2·cos(THREAD_FLANK_ANGLE))
                       + μ_bearing_eff(D) · r_bearing ]
```

with `lead_per_radian = pitch/(2π)`, `THREAD_FLANK_ANGLE = 30°`, and
`μ_bearing_eff(D) = μ_bearing·(1 − k_dmg_mu·D)` (already in the engine). Linear in F₀, so

```
F0_achieved = T_applied / [ lead_per_radian + μ_thread·d_2/(2cosα) + μ_bearing_eff(D)·r_bearing ]
```

New module helper `tightening_torque(F0, state, geom, mat)` mirrors `T_resistance`.

**Falsify-first (professor's call):** no galling / friction-rise term is added. Dry vs
oil baseline recovery follows from the μ difference (lower μ → higher F₀). The dry
*progressive* recovery decline is **left to the data**. Note the frozen `shared` block
has **`k_dmg_mu` absent (=0)**, so `μ_bearing_eff(D)=μ_bearing` and the predicted recovery
is **flat across retightenings** (no D coupling). Setting `k_dmg_mu>0` would make recovery
**rise** with D (lower μ → higher F₀). Either way the frozen physics **cannot** produce
the observed *decline*. We **pre-register** the flat prediction; if Liu2022 falsifies it,
that is a documented finding naming a missing term (thread galling / geometric recovery
ceiling), not a knob to add pre-emptively.

### 3.3 Embedding renewal rule (opt-in, default-inert)

```
delta_emb ← delta_emb · (1 − k_emb_renew · D)        # clamped to [0, target]
```

New `JointMaterial.k_emb_renew: float = 0.0`. **Default 0 ⇒ retighten keeps `δ_emb`
exactly ⇒ bit-identical backward-compat.** Linear coupling (confirmed): restored
capacity ∝ D — one constant, parsimonious. `target = k_emb_scale·emb_depth` (same as
`EmbeddingLoss`). `k_emb_renew>0` is what makes a dry (high-D) joint re-settle after each
retighten and loosen faster.

### 3.4 API / surface summary

- **New** `JointMaterial.k_emb_renew` (float, default 0.0). Added to `to_dict`/`from_dict`
  paths and the V2 tuner override filter automatically (filtered by `__dataclass_fields__`).
- **New** `DynamicStiffnessAnalyzer.retighten(applied_torque=None, new_F0=None)`.
- **New** module helper `tightening_torque(F0, state, geom, mat)`.
- No change to `step_cycle` or the loss mechanisms. Existing sims never call `retighten`,
  so they are untouched.

### 3.5 Energy accounting at the discrete event

`retighten` rebases the budget: `U_stored_init ← U_internal(new state)`, and the
cumulative `W_ext` / `W_diss_*` accumulators reset so `conservation_residual` measures the
**current cycling segment** (≈ 0, as today). The discrete re-torque work (wrench work =
ΔU_stored + tightening friction) is **not** folded into the per-cycle budget — out of
scope; the per-segment cyclic conservation is what we validate.

---

## 4. Validation plan

New harness `New_Theory/validate_retightening.py` reproduces the Liu2022 protocol with
Stage-A frozen constants (no per-curve refit):

1. Tighten: `F0 = tightening_torque⁻¹(80 N·m, D=0, μ_lube)`. Run 5000 cycles,
   `step_cycle(F_amp, θ=π/2, 12.5 Hz, delta_amp=0.3e-3)` (transverse, disp-controlled).
   Record R_F(t0) = F_0/F0_first.
2. `retighten(80 N·m)` → run 5000 cycles → R_F(t1). Repeat t2, t3.
3. Two runs: **dry** (μ_thread=μ_bearing≈0.2) and **oil** (≈0.1); one shared physics set,
   `k_emb_renew` freed + damage active via `frozen_constants(include_damage=True)` so
   `c_D=2.0`/`k_dmg_wear=4.0` come from the `shared` block (`k_dmg_mu` is **absent=0**);
   `emb_depth` **overridden** to the Liu2022 VDI value (M12 fine-ground, not the M16
   default 30 µm). Dry degradation is damage-driven: dry's higher μ → more friction work
   → faster `D` growth (`c_D`) → stronger wear amplification (`k_dmg_wear`). R_F normalised
   to first-tightening F₀.
4. Compare each `tN` to `fig6a` (dry-release), `fig6b` (oil-release), `fig7a` (oil-direct);
   `fig8` for the multi-retighten trend (trim t4 fracture).
5. **Secondary (fidelity goal, option B):** re-simulate the âncora interna **reaperto** condition as
   `nova → cycle → retighten` instead of fresh-full-embedding, and confirm the 0.038-class
   fit is preserved with **renewal** carrying the re-settling and **D** carrying the
   collapse — i.e. it fits for the *right reason*, not phantom fresh embedding.

Inputs carry provenance (μ dry/oil, grip incl. 20 mm load-cell, 45-steel plate stiffness)
per the apparatus note.

---

## 5. Falsification criteria (pre-registered, AS IS)

Recorded **before** the run; the mechanism is a *validated capability* only if it clears
these with `k_emb_renew` freed at most, not per-curve tuners:

- **G1 (oil restore):** oil-release t1..t3 first-point R_F ≥ 0.95 (model reproduces
  ~100% restore) and per-curve MAE < 0.05.
- **G2 (dry acceleration):** define per-phase loss `ΔR_F(tN) = R_F(start of tN) −
  R_F(end of tN)` over each 5000-cycle phase. The dry data shows `ΔR_F` **monotone
  increasing** t0→t3; the model must reproduce the increasing ordering and land within
  ~2× of the observed per-phase losses.
- **G3 (dry vs oil from μ alone):** with all constants shared and only μ differing, the
  model separates dry (declining, accelerating) from oil (stable, slow). Failure ⇒ the
  contrast needs more than μ (finding).
- **G4 (recovery trend):** the frozen physics (`k_dmg_mu=0`) predicts recovery **flat**
  across retightenings; the data **declines** (dry). The flat prediction is pre-registered
  and checked against the decline. Disagreement is the expected, documented finding (missing
  galling/geometric term) — **not** a gate failure of embedding renewal itself.
- **G5 (parsimony — is renewal even needed?):** compare the dry-series fit with
  `k_emb_renew=0` (frozen `k_dmg_wear` amplification alone) vs `k_emb_renew` freed. Embedding
  renewal is *justified* only if freeing it cuts the dry MAE by > 0.005 (forward-selection
  tol). If wear-amplification alone reproduces the dry acceleration, renewal is **not**
  justified by this dataset — a documented negative finding, and `k_emb_renew` stays 0.
- **Backward-compat:** `k_emb_renew=0` ⇒ `retighten` leaves `δ_emb` unchanged; full suite
  bit-identical where `retighten` is unused.

Verdict is written AS IS to `MODEL_LEGITIMACY.md` (new §4.10), whichever way it falls.

---

## 6. Discipline

Opt-in / default-inert (`k_emb_renew=0`; `retighten` is a new method); TDD (failing tests
first: torque→preload inversion, renewal clamp, θ_loose reset, backward-compat, per-segment
conservation); syntax-check after edits; utf-8 I/O; Opus review before merge. Update
decomposition/serialization consumers for the new field where they enumerate
`JointMaterial` fields.

---

## 7. Out of scope

- A damage→tightening-friction (galling) term or geometric recovery ceiling — **deferred**
  pending the G4 falsification result.
- fig8 t4 fatigue-fracture endpoint (out-of-model; trim).
- Propagating `retighten` to the GUI Run / `.msd` (follow-up if adopted).
- Re-fitting the canonical `shared`/`profiles` blocks (this is validation, not adoption).
