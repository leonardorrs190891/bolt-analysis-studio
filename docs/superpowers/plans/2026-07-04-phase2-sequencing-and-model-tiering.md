# Phase 2 — Sequencing & Model Tiering

**What this is:** the map for BAS V2 Phase 2 (per `CLAUDE.md` item 11 / `MODEL_LEGITIMACY.md` §8). It classifies every Phase-2 item by readiness, fixes the execution order, states the accepted model-tiering doctrine (Opus session + Fable swaps), and — for the items that are **form changes** (new physics whose functional form is the professor's decision) — states the exact design question that must be answered before a bite-sized plan can be written. **No physics is invented here.**

Phase 1 verdict this builds on (§8): *mechanism forms and couplings transfer cross-rig; constants are per-pair/per-rig/per-joint properties needing per-constant provenance.* Phase 2 shifts the program from "fit fewer numbers" to "supply provenance per constant + supply the missing forms."

---

## Model-tiering doctrine (accepted)

Session runs on **Opus 4.8 (max effort)**. Fable is swapped in as a subagent at exactly two kinds of point, where Phase 1 showed its capability was load-bearing:

1. **Final whole-branch review** of each branch (subagent-driven-development already dispatches the final review on the most capable model).
2. **Falsification-logic checks + scientific writing** — any task that writes a *conclusion* into `MODEL_LEGITIMACY.md` (a verdict, a per-constant provenance claim, a transfer result). The Fable reviewer must *recompute* the claim from the raw artifact (JSON), not trust the script's printed answer.

Everything else — implementers (sonnet/haiku for transcription), per-task reviewers, mechanical runs — stays on the cheaper tiers. This pays Fable's premium only on the ~5% of work where it earned it.

**Fallback:** if subagents cannot access Fable, run the two swap points on **Opus 4.8 at max effort**, and have the reviewer independently recompute every scientific claim from the artifact. You lose the independent-derivation edge; you keep the review.

Each individual plan repeats its own per-task tiering table.

---

## Item inventory & readiness

| # | Item | Type | Plan status |
|---|---|---|---|
| 1 | **Test-hardening** (frac/damage range validation, LOCO regression, upsert_shared return) | mechanical | ✅ `2026-07-04-test-hardening-stage-a.md` |
| 2 | **Re-run `calibrate_4_profiles`** under state-based embedding (+ fix the `shared`-block clobber) | mechanical | ✅ `2026-07-04-recalibrate-4-profiles-state-embedding.md` |
| 3 | **Sobretorque F0-bound → 133 kN** discrimination (bound-too-tight vs missing pressure-dependent regime) | science run (pre-registered) | ✅ `2026-07-04-sobretorque-f0-bound-133kn.md` |
| 4 | **Member-stiffness scaling** (Rousseau t10/12/14 over-prediction with thickness) | **investigation first** | ⏳ needs diagnostic pass — stub below |
| 5 | **Embedding renewal on reaperto** (δ_emb reset on re-tighten; 21 liu2022 curves) | **form change** | ⏳ needs design decision — stub below |
| 6 | **F_amp↔δ_amp coupling** in disp-mode (F_amp ≤ µ·F_0 in full slip; yang2021) | **form change** | ⏳ needs design decision — stub below |
| 7 | **Axial ∝A_F loss mechanism** (thread-flank fretting; the Phase-1B falsification) | **form change (the big one)** | ⏳ needs design decision — stub below |
| 8 | **Profile-likelihood CIs** for the fitted constants | Phase 3 (uncertainty) | ⏳ separate phase — pointer below |

---

## Recommended execution order

**Immediate (ready — no decisions needed):**

1. **Test-hardening** (#1) — cheapest; locks the guardrails (range validation, LOCO regression, upsert contract) that protect everything after it.
2. **Re-run `calibrate_4_profiles`** (#2) — removes a **landmine**: the current script clobbers the canonical `shared` block on any run. Fix + regression-confirm before more calibration work touches that file.
3. **Sobretorque 133 kN** (#3) — the sharpest Phase-2 science result and the professor's top roadmap item.

#3 is *independent* of #1/#2 (it reads the intact `shared` block as baseline and writes only its own artifacts), so it can lead if the professor prefers the science first. #1 and #2 are quick and remove risk, so the recommendation is #1 → #2 → #3.

**After the professor decides the forms (each needs a brainstorming pass first):**

4. **Member-stiffness investigation** (#4) — diagnose *where* the grip→stiffness map breaks before proposing a fix.
5. **Embedding renewal** (#5), **F↔δ coupling** (#6), **Axial ∝A_F** (#7) — order by appetite; #7 is the deepest (it's the mechanism whose absence Phase 1B falsified) and benefits from #4's stiffness insight landing first.
6. **Profile-likelihood CIs** (#8, Phase 3) — after the forms stabilize; CIs on a still-changing model are premature.

---

## Design-question stubs (form-change items — brainstorm before planning)

These are **not** plans. Each states what Phase 1 established, what data exists, and the specific physics/API decision the professor must make. Writing a bite-sized plan for any of these before the decision would mean inventing the professor's physics — exactly the anti-pattern (anti-knob, physics-first) the program has held to. When ready, each becomes a `superpowers:brainstorming` → spec → plan cycle.

### #4 — Member-stiffness scaling (investigation first)

- **Phase 1 finding (§4.8):** Rousseau t10/12/14 is the library's only member-thickness sweep. The model goes from slight *under*-prediction to increasing *over*-prediction of loosening as plate thickness grows (MAE 0.228 → 0.373 → 0.380; `final_pred − final_data` −0.31/−0.51), **without collapse**. So the `grip → L_eff → k_b` mapping and/or the fixed `k_j` does not scale with member thickness. This is a **form** clue, not a tuner.
- **Diagnostic question (do this before any fix):** instrument `k_b`, `k_j`, and `L_eff` across t=10/12/14 mm and compare `k_j` to the VDI 2230 member-stiffness (Rötscher/cone) model. *Which* term fails to scale — the bolt compliance `L_eff`, the fixed member stiffness `k_j`, or their ratio in the helix coupling?
- **Decision needed:** only after the diagnostic — whether the fix is (a) a thickness-dependent `k_j` from VDI 2230 (provenance = handbook, not fitted), (b) a corrected `grip → L_eff` map, or (c) something in the helix-coupling assembly. **Recommendation:** run the diagnostic as a small read-only investigation plan first (no model change), then brainstorm the fix.

### #5 — Embedding renewal on re-tightening

- **Phase 1 / model state:** the state-based `EmbeddingLoss` seeds already-consumed embedding via `initial_embedding_frac`, but there is **no mechanism to reset `δ_emb` when a joint is re-tightened** mid-life. The reaperto/TP7 condition and the 21 liu2022 retightening curves exercise exactly this.
- **Decision needed (physics + small API shape):**
  - On a re-tighten event, does `δ_emb` fully reset to 0 (asperities re-seat completely), partially (a renewal fraction `f_renew ∈ [0,1]`), or not at all?
  - Is renewal *per-event* or does it decay with the number of prior re-tightenings (asperities flatten permanently)?
  - **API shape:** how is a re-tighten event expressed to `step_cycle`/the analyzer — a `reseat(new_F0)` method, a flag on `step_cycle`, or a scripted state edit? (Keep it a named state transition, consistent with the `initial_embedding_frac` doctrine.)
- **Data:** 21 liu2022 retightening curves (verify axis units and the retighten schedule in the apparatus note before planning).

### #6 — F_amp ↔ δ_amp coupling (disp-mode)

- **Model state (CLAUDE.md item 4):** in displacement-controlled mode, `F_amp` and `delta_amp` are passed **independently** to `step_cycle`. Physically, in full slip `F_amp ≤ µ·F_0` — the two are not free.
- **Decision needed:** the coupling law. Options to weigh (professor's call — do not pick unilaterally): cap `F_amp` at `µ·F_0` (hard clip); derive `F_amp` from `δ_amp` through the transverse stiffness up to the slip limit; or a smooth transition (stick→slip) between them. Which is faithful to the servo-hydraulic vs crank-driven rigs?
- **Data:** yang2021 composite (confirm it is disp-controlled and provides both amplitudes before planning).
- **Interaction:** this touches the same slip path as WearLoss/RotationalLooseningLoss — coordinate with #7 so the two form changes don't fight over the slip definition.

### #7 — Axial ∝A_F loss mechanism (the Phase-1B falsification)

- **Phase 1B finding (§4.6):** the current mechanism set was **structurally falsified** on the axial track — `∂(final)/∂A_F ≡ 0` in the model (wear = transverse slip; creep = F₀-only; embedding = amplitude-blind) vs **−2.216e-5/N** in the Liu2017 data. This is a **missing form**, not a tuner. B2 was proven futile (the latent channel is ~30× below threshold).
- **Identified seam (handoff):** a loss driven by axial amplitude — thread-flank fretting/wear, ∝ `A_F` — grafted onto `WearLoss` as a flank-slip source.
- **Decision needed (the deepest set — a full brainstorming pass):**
  - **Rate law:** Archard-like flank wear with slip ∝ `A_F`? A fretting term with an amplitude threshold? Energy-based? What is the closed form?
  - **State variable:** does it drive the existing `δ_wear`, or a new `δ_flank`? (New state ⇒ `SlowState` field + serialization + conservation bookkeeping.)
  - **Geometry map:** how does axial amplitude `A_F` map to flank micro-slip amplitude (pitch, flank half-angle, helix)? This map is where the provenance lives — it must come from geometry, not a fitted knob.
  - **Conservation:** does it follow the established "dF_0 yes, dE no" pattern (like damage/wear amplification), or is `dE` the real flank friction work? Get this right up front — §4.6 already flagged an open `W_damp_visc` bookkeeping gap in axial force-mode.
- **Calibration/falsification target:** the mechanism must reproduce the sign and rough magnitude of `∂(final)/∂A_F ≈ −2.216e-5/N` (Liu2017), *without* re-fitting the transverse constants — i.e., it must transfer, per the §8 doctrine.
- **Explicit non-starter:** do **not** reach for GW `k_tr(F0)` as the pressure/amplitude lever — its sign is unfavorable in the current slip equation (spec Fase 1 §4). If the sobretorque run (#3) returns "missing mechanism," the same caveat binds there.

### #8 — Profile-likelihood confidence intervals (Phase 3)

- **Goal:** proper uncertainty on the fitted constants (currently only the linearized CIs from the creep anchor exist). Profile-likelihood over `C_creep`, `K_archard`, etc., across the shared fit.
- **Gate:** defer until the forms (#5–#7) stabilize — CIs on a model still gaining mechanisms would be re-done. Separate phase; own spec when the time comes.

---

## Cross-cutting constraints (all Phase-2 work)

- **OneDrive + parallel session share the checkout:** never `git add -A`; stage explicit file lists; foreign working-tree changes are the user's WIP (preserve, never stage). git can be slow/fragile here — bound long git commands.
- **Experiments never overwrite the canonical `shared` block** of `New_Theory/joint_calibrations.json` (precedent: `creep_anchor.json`, `sobretorque_f0bound.json`). Item #2 fixes the one script that violated this.
- **Per-constant provenance:** any input must come from a table/paper with a `Provenance` tag (`library_common.py`), never fitted from the target curve. `emb_depth` = per-joint VDI 2230 table input; `C_creep` = per-pair anchor.
- **AS IS:** pre-registered thresholds/case-lists frozen before runs; falsification findings documented, never tuner-patched.
- `.json`/`.png`/`.md`/`.py` are not gitignored; `*.csv` needs `git add -f`; PDFs stay out of git.
- Commits PT sem acentos + `Co-Authored-By` trailer of the authoring model (session default: `Claude Opus 4.8 (1M context) <noreply@anthropic.com>`).

---

## Note on Stage B

Stage B (deleting the 9 tuner fields, spec 2026-07-02 §3) is **not** a Phase-2 item and is **not** scheduled here. The A→B gate verdict (`PASSA COM RESSALVAS`, §4.5) explicitly reserves that decision for the professor. It is triggered only on explicit request.
