# Stage B — Tuner-Removal Refactor Plan (roadmap #8)

> Gated on the professor's explicit go for the BREAKING step (Phase 4). Phases 1–2 are
> non-breaking. Companion to `docs/superpowers/specs/2026-07-07-stage-b-scoping.md`
> (this is the implementation plan that spec calls for). Produced 2026-07-08 (parallel
> scoping agent, read-only; verified against current source).

## Load-bearing findings (verified against current source)

1. **The physics-only calibration path already exists + is merged.** `SharedCalibrator`
   (`calibration/shared_calibrator.py`) never fits tuners — `_material()` builds
   `JointMaterial(**constants)` (k_*_scale default 1.0). The `shared` block of
   `joint_calibrations.json` already stores only physical constants. **Stage B is
   engineering hygiene, not added legitimacy.**
2. **The GUI does not read `joint_calibrations.json`.** Only `New_Theory/*.py`, `tests/*`,
   `calibration/server.py`, `calibration/profiles.py` consume it. The "make the GUI read
   `shared`" framing is imprecise — the Run uses `JointMaterial` defaults + hardcoded
   `conf_defaults` + `_v2_tuner_overrides`.
3. **`_v2_tuner_overrides` is NOT serialized.** `model.py` persists only `two_stage_overrides`
   (V1). The `main_window.py:4914` comment ("survive save/load") is WRONG. On-disk UFU `.msd`
   carry no V2 `k_*_scale`. So the shim's real inputs are (a) in-session overrides from a live
   StagedCalibrator run and (b) the `profiles` block — NOT persisted `.msd`. Surfaces a
   **persistence decision** (Phase 0).
4. **CORRECTION to the scoping spec's fold table:** `k_wear_scale_tr` **does** enter `dE`
   (`WearLoss` multiplies `k_scale` into both `d_wear`→`dF_0` AND `dE`). Folding it into
   `K_archard` is **ratio-trajectory bit-identical but NOT energy-channel bit-identical**
   (K_archard is absent from `dE`, which references `mu_bearing_eff`). Test strategy must key
   "bit-identical" on the **ratio trajectory + per-mechanism dF_0**, and check energy as
   **conservation residual ≈ 0**, never `dE` equality. No single-constant fold preserves `dE`.

## 1. Inventory — tuner → read site → fold target → exactness

| Tuner | Read site | Folds into | Exactness |
|---|---|---|---|
| `k_emb_scale` | EmbeddingLoss (`target=k_emb·emb_depth`), __init__ seed, retighten | `emb_depth *= v` | **EXACT** (dF_0 + dE) |
| `k_creep_scale` | CreepLoss (`d_delta *= v`) | `C_creep *= v` | **EXACT** |
| `k_wear_scale_tr` | WearLoss `d_wear` AND `dE` | `K_archard *= v` | **ratio EXACT; dE shifts** |
| `k_wear_scale_ax` | WearLoss (cos²θ) | — (no axial track) | **LOST** (`*_ax`) |
| `k_loose_scale_tr` | RotationalLoosening (linear on d_theta) | `tr_loose_gain *= v` | **NOT EXACT** (gain enters slip_fraction non-linearly) |
| `k_loose_scale_ax` | RotationalLoosening (cos²θ) | — | **LOST** |
| `Phi_tr_correction` | Phi_eff AND loosening (`tr_loose_gain·Phi_tr_corr`) | `tr_loose_gain *= v` | **EXACT on loosening; Phi_eff branch LOST** |
| `Phi_ax_correction` | Phi_eff (axial) | — | **LOST** |
| `k_damage_scale` | damage growth (`dD = k_damage·c_D·…`) | `c_D *= v` | **EXACT** |

**De-risker:** the canonical profiles only ever free **`{k_emb_scale, k_wear_scale_tr}`** (all
others = 1.0). k_emb folds fully exactly; k_wear folds ratio-exactly ⇒ **every shipped calibrated
curve is ratio-bit-identical after the fold.** Non-exact folds only bite hand-set `.msd` knobs,
which do not exist on disk (finding #3).

## 2. Legacy translation shim

New pure module `calibration/tuner_shim.py`: `translate_legacy_tuners(overrides) -> dict`.
Multiplicative map (k_emb→emb_depth, k_creep→C_creep, k_wear_scale_tr→K_archard,
Phi_tr_correction/k_loose_scale_tr→tr_loose_gain, k_damage→c_D; `*_ax`→drop + DeprecationWarning).
Requirements: multiply (never overwrite) against the effective base; applied once at the
consumption boundary (`solver_worker._compute_v2_history`, `server.py:_material`), NOT on
deserialization; idempotent; per-key warning replaces today's silent drop. Note `K_archard` is
also read by `ThreadFrettingLoss` (inert by default) — folding scales axial fretting too
(physically consistent; document).

## 3. Source-of-truth consolidation

Adopt one loader `profiles.load_shared_material(path) -> constants` so the Run, server, and scripts
read physical constants from ONE place instead of three hardcoded copies (`JointMaterial`
defaults, `solver_worker` conf_defaults, `SharedCalibrator.PHYSICAL_PRIORS`). `W_conf_ref=7671`
already came from `shared` — replaces a hardcoded copy with a read. `parameter_registry.py` is
already Stage-B-shaped (references physical constants, no change).

## 4. Test strategy (bit-identical = ratio + dF_0-by-mech; energy = residual≈0)

- **A. Fold-equivalence (current engine, the gate):** `JM(k_x=v)` ≡ `JM(k_x=1, physconst=base·v)` on
  ratio trajectory to FP tol, per tuner, across nova/reusada/sobretorque/reaperto. Assert dE
  divergence for k_wear (pin the nuance); assert Phi_eff/k_loose divergence where non-exact.
- **B. Shim unit tests** (map, composition-multiplies, `*_ax` dropped+warned, idempotent).
- **C. End-to-end legacy-.msd equivalence** through the shim-active Run vs a pre-B baseline fixture.
- **D. No-regression:** `calibrate_shared.py` (tuners≡1.0 already → MAE unchanged),
  `transfer_validation.py` (bit-identical), conservation residual ≈ 0 outside collapse.
- **E. ~53 tuner refs across 14 test files**; core (shared_calibrator, shared_block_persistence)
  green unchanged; staged/profiles/server/solver/embedding tests retarget onto constants.

## 5. Phased ordering (breaking work last)

- **Phase 0 (decisions, no code):** (a) `*_ax` delete vs keep-as-deprecated-no-op (recommend KEEP
  until axial matures — roadmap #9 will want the ax/tr distinction back); (b) fix the
  `_v2_tuner_overrides` persistence gap or declare tuners session-only; (c) confirm the `shared`
  regression baseline number (JSON canonical `mae_global` 0.0509 with conformation).
- **Phase 1 (non-breaking):** shim + fold-equivalence tests against the current engine. Migration
  safety in isolation. Fully reversible.
- **Phase 2 (non-breaking):** Run/HTML/server read `shared.constants` via the one loader; `k_*`
  fields stay as live no-op aliases (default 1.0). Delivers "the GUI runs the shared physics" with
  zero API break.
- **Phase 3:** migrate calibration dialog + `parameter_identifier` targets onto constants; wire the
  shim at the two boundaries.
- **Phase 4 (BREAKING, last):** remove the 9 fields, update ~53 test refs / 14 files, drop
  `profiles` + writers, update docs.

## Risks / recommendation

- **Deleting `*_ax` closes a door roadmap #9 (axial ∝ A_F) reopens** — keep as a named physical
  ratio if/when axial matures, not a tuner.
- **Provenance hazard (decisive):** `k_wear_scale_tr` currently absorbs per-rig magnitude that
  `K_archard`/`W_conf_ref` lack provenance for (§4.8/§4.9 nulls). Removing the knob WITHOUT giving
  those constants per-par provenance leaves the model without the knob AND without the provenance
  — §8's pivot is "provide provenance per constant." **Strong argument to defer Phase 4** until
  ≥1 constant (esp. `W_conf_ref`) gains per-par provenance.

**Bottom line:** Phases 1–2 are small, non-breaking, and deliver the real product value ("GUI runs
the shared physics") without foreclosing the Phase-2-provenance decision. Phase 4 (field deletion)
is highest-blast-radius, least urgent, and best deferred. The science (tuners redundant) is already
proven + merged in the `shared` block.
