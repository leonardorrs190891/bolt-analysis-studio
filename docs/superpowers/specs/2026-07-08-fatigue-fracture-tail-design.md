# Fatigue-Fracture Tail — Design Spec

**Date:** 2026-07-08 · **Status:** designed (brainstorm 2026-07-08), opt-in/default-inert
**Roadmap:** the "fatigue tail" deferred item — curves that end in sudden fracture
(Yang2021, Li2022ti) are currently trimmed as out-of-model.
**Author:** Prof. L. R. R. da Silva

---

## 1. Motivation

Some rigs run to **bolt fatigue fracture**: a gradual loosening decay, then a
**sudden cliff** to ~0 as the bolt cracks. Signature in the library:

- `yang2021_fig2_typical`: 0.60 @5950 cyc → **0.00 @6020** (fracture in ~70 cycles).
- `li2022ti_axial_10Hz_full`: 0.52 @405k → **0.09 @410k**.

V2 (`DynamicStiffnessAnalyzer`) has no fatigue channel, so these tails are trimmed.
V1 (`coupled_loosening_analyzer`) already has the machinery — `SuNCurveModel`
(bilinear Su-N, thread-root stress `Kt·F/A_s`, Miner's D, Stage-III fracture at
D≥0.8). This form **ports that into V2** as an opt-in mechanism that drops preload
at Miner D≥1.

## 2. Mechanism — `FatigueLoss` (a `LossMechanism`)

Per cycle, **only when `fatigue_enabled=True`** (else returns zero → bit-identical):

1. **Alternating stress:** `σ_a = fat_Kt · |F_amp| / A_s` (thread-root, `A_s` from
   geometry). Direction-agnostic magnitude — correct for the axial validation rigs;
   direction-resolved axial-direct vs transverse-bending Kt is a documented refinement.
2. **Mean stress (evolves):** `σ_m = F_0 / A_s` — the preload *is* the mean stress, and
   it falls as the joint loosens (the loosening↔fatigue coupling).
3. **Goodman:** `σ_ar = σ_a / (1 − σ_m/fat_sigma_uts)` (equivalent fully-reversed
   amplitude; denominator clamped ≥ 1e-3).
4. **Bilinear Su-N** (`sun_life`, Yang params): `N_f = C₁·σ_ar^−m₁` (σ_ar ≥ knee) /
   `C₂·σ_ar^−m₂` (below knee); `N_f = ∞` below `fat_sigma_endurance`.
5. **Miner:** `dD = 1/N_f`; `state.D_fatigue += dD` via the `ds` channel.
6. **Cliff:** when `D_fatigue + dD ≥ 1`, fracture → `dF_0 = −(F_0 − F_res)`,
   `F_res = fatigue_residual_frac · F_0_init` (default 0). One-time; after fracture
   `D_fatigue ≥ 1` and `F_0 ≈ 0` so the mechanism (and all others) idle.

`dE_dissipated = 0` for the fatigue cliff (see §4).

## 3. New fields (all default-inert)

`SlowState`: `D_fatigue: float = 0.0`.

`JointMaterial` (defaults reproduce the current engine bit-for-bit; only read when enabled):
```
fatigue_enabled: bool = False
fat_Kt: float = 3.5                 # thread-root stress concentration
fat_sigma_uts: float = 1040e6       # Pa — UTS (class 10.9) for Goodman
fat_sigma_knee: float = 50e6        # Pa — bilinear knee (Yang)
fat_C1: float = 5e32                # high-stress coefficient
fat_m1: float = 3.5                 # high-stress exponent
fat_C2: float = 5e49                # low-stress coefficient
fat_m2: float = 6.0                 # low-stress exponent
fat_sigma_endurance: float = 10e6   # Pa — below this, infinite life
fatigue_residual_frac: float = 0.0  # residual F_0 fraction after fracture
```
Values ported from V1 `SuNCurveParams` (Yang, M16 cl.10.9) → **provenance** (handbook/
literature), not invented.

Register `FatigueLoss()` in the `DynamicStiffnessAnalyzer.losses` list.

## 4. Cliff energetics (phenomenological, documented)

The fracture releases stored elastic energy in one step; `dE=0` so the conservation
residual **spikes only at the fracture cycle** (a catastrophic structural event, not a
smooth dissipation channel — same class as #6 damage-collapse). Pre-fracture cycles
(dD tiny, dF_0=0) conserve normally. Not smoothed into the budget — AS-IS.

## 5. Validation (`New_Theory/fatigue_tail.py`)

Success bar = **represent + test-predict** (falsification-first):

- **Represent:** Yang2021 + Li2022ti — with the Su-N calibrated per-material to the
  observed fracture cycle, reproduce (a) the pre-fracture loosening AND (b) the cliff
  at N_fracture (right shape). The cliff appears; the model no longer needs trimming.
- **Falsification-test predict:** with the *handbook* Yang M16 Su-N (zero-refit), report
  how close N_fracture lands — honestly (S-N scatter + per-material → likely 2–10× off;
  the FORM transfers, the Su-N constants are per-material, §8).
- **No regression:** `fatigue_enabled=False` bit-identical (test); V2 suite green.

## 6. Provenance discipline

Su-N constants are **per-material** (handbook Wöhler curve for the bolt class, or fitted
per-rig — like `C_creep`). `Kt≈3.5`, `σ_uts≈1040 MPa` (class 10.9), `A_s` from geometry.
The Su-N *center* is the material's fatigue curve, never a free knob. Verdict AS-IS in
`MODEL_LEGITIMACY.md` §4.13.

## 7. Out of scope

Direction-resolved fatigue (axial-direct vs transverse-bending Kt); crack-growth
kinetics (Paris law) for the cliff *shape* (we model an instantaneous drop); rigorous
fracture energetics (#6). Transverse Junker bending fatigue (validation is axial).
