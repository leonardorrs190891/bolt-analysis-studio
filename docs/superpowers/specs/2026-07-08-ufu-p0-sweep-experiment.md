> **VOID (2026-07-08, diretiva do professor): experimento UFU COMPLETAMENTE DESCARTADO — tudo sera feito com dados de literatura. Mantido apenas como registro historico do protocolo.**

# UFU Axial P₀-Sweep — Cross-Validation Experiment Protocol (pre-registered)

**Date:** 2026-07-08 · **Status:** PLANNED (awaiting professor's go + rig booking)
**Purpose:** the ONE experiment that can promote the axial pre-conformance forms
(`emb_conform_exp` / `creep_conform_exp`, §4.14a-rev) from *"calibrated structure that
generalizes within-rig"* to *"predictive law"* — a second, independent preload sweep.
**PI:** Prof. Leonardo Rosa Ribeiro da Silva (UFU / LTAD)
**Analysis pipeline (already exists, runs as-is on the new CSVs):**
`New_Theory/axial_ground_fit.py` + `New_Theory/axial_overfit_checks.py`.

---

## 1. Scientific questions (in falsification order)

- **Q1 (the replication):** on a different rig/pair, is the slow-tail rate
  **preload-dependent** (∝F₀⁻ⁿ) — or F₀-flat (Norton-universal)? Liu2017 said
  F₀⁻²; the model bet the *form* transfers. **This is the headline test.**
- **Q2:** does the fast-settlement loss follow the pre-conformance power law
  `S = min(1,(p_ref/p_init)^n_fast)` — including the **S=1 plateau below p_ref**
  (a falsifiable kink no smooth alternative reproduces)?
- **Q3 (per-pair doctrine):** do the *levels* (emb_cap, C_creep) differ per-pair
  (expected: YES) while the *exponents* land in a transferable band (n∈[1.5–5])?
- **Q4 (mechanism, independent of curves):** does the **post-tightening static
  relaxation fraction decrease with F₀**? (Pre-conformance says higher torque-up
  consumes more of the settle-able reservoir — measurable before any cycling.)
- **Q5 (time vs cycles):** is the slow tail driven by wall-clock time (creep) or
  cycle count (cyclic settlement)? One frequency pair decides. (Li2022ti hinted
  frequency matters; the engine currently uses wall-clock — this pins it.)

## 2. Test matrix

### Arm A — main preload sweep (primary, powers Q1–Q3)

| # | F₀ [kN] | % proof (M12 10.9 ≈ 70 kN) | A_F [kN] | freq | cycles | runs |
|---|---|---|---|---|---|---|
| A1 | 10 | 14% | 8 | 25 Hz | 10⁶ | 1 |
| A2 | 13 | 19% | 8 | 25 Hz | 10⁶ | 1 |
| A3 | 16 | 23% | 8 | 25 Hz | 10⁶ | **3** (replicates) |
| A4 | 20 | 29% | 8 | 25 Hz | 10⁶ | 1 |
| A5 | 25 | 36% | 8 | 25 Hz | 10⁶ | 1 |
| A6 | 30 | 43% | 8 | 25 Hz | 10⁶ | **3** (replicates) |

Design rationale: **6 levels over a 3× ratio** (Liu had 5 over 1.4× — too narrow to
discriminate power laws sharply; 3× gives SE(n) ≈ 0.2–0.4 with the replicate noise floor).
The **low end (10 kN)** deliberately probes below the expected p_ref so the S=1 plateau
(Q2 kink) is observable — this also removes the LOCO anchor-fragility by *measuring* the
plateau instead of assuming it. Replicates at A3/A6 give the **test-to-test scatter floor**
(the 16.5 kN lesson from Liu2017: n=1 per condition left us unable to separate scatter
from signal). Constant absolute A_F = 8 kN (< F₀ everywhere; matches the model's F_amp
driver; below joint-opening for all levels).

### Arm B — static dwell controls (Q4/Q5 + independent C_creep anchor; bench, ~zero actuator time)

| # | F₀ [kN] | protocol |
|---|---|---|
| B1–B3 | 10 / 16 / 30 | tighten → log preload continuously for ≥ 24 h, NO cycling |

Directly separates time-creep from cycle-driven settlement (compare B loss at the same
wall-clock as an A run), anchors C_creep(this rig) independently — the same role
`anchor_creep.py`/li2022marstruc played — and tests Q4 (relaxation fraction vs F₀).

### Arm C — frequency pair (Q5; 2 runs)

| # | F₀ | A_F | freq | cycles |
|---|---|---|---|---|
| C1 | 16 kN | 8 kN | 25 Hz | 3×10⁵ |
| C2 | 16 kN | 8 kN | 5 Hz | 3×10⁵ (same N, 5× the wall-clock) |

If the tails overlay in **cycles**, the slow channel is cyclic (engine should switch the
creep clock to N); if they overlay in **time**, it's creep (current engine correct).

### Arm D — amplitude mini-sweep (secondary; feeds the §4.6 A_F missing form)

| # | F₀ | A_F [kN] | freq | cycles |
|---|---|---|---|---|
| D1–D4 | 16 kN | 4 / 6 / 10 / 12 | 25 Hz | 3×10⁵ |

Opportunistic (rig already set up): gives THIS rig's ∂(final)/∂A_F so the thread-fretting
level (`k_thread_fret`, Fouvry-gated) finally has a same-rig dataset. Cut first if time-boxed.

## 3. Specimen & instrumentation

- **Fasteners:** M12×1.75 grade 10.9 (matches Liu2017 → isolates the *rig/pair* variable),
  hardened washers + class-10 nut. **VIRGIN set every run** (no reuse — reuse ≡
  `emb_consumed_frac>0` and corrupts the fast reservoir). One purchase lot. ~22 sets + 4 spare.
- **Joint stack:** two steel plates, grip ≈ 30 mm (2.5d), through-hole **load washer**
  (0–50 kN, ≤0.25% FS) in the stack — document every interface (the n_if input for
  `emb_depth_vdi`). Plate/washer faying surfaces: measure **Rz on the profilometer** (LTAD)
  before testing — this is the emb_depth *input* provenance, never a fitted knob.
- **Tightening: preload-controlled, not torque-controlled** — tighten to target F₀ by
  load-washer feedback (kills nut-factor scatter, the biggest F₀ uncertainty in Liu2017).
  Record torque–angle–preload during tightening + **10 min static hold BEFORE cycling**
  (this hold is the Q4 measurement — log it at ≥1 Hz).
- **Loading:** axial servohydraulic (±100 kN class), force-controlled sine, R>0
  (cyclic amplitude A_F about the working point; joint never unloaded to zero).
- **DAQ:** continuous preload logging, decimated: every cycle for N≤10³ (fast reservoir +
  N_emb shape), then log-spaced ≥60 points/decade to 10⁶. Thermocouple on the nut (frequency
  arm heating check). Export **`cycle, F_kN, F_over_F0`** CSV (the pipeline's native format).

## 4. Pre-registered predictions & gates (declared BEFORE data exists — §4.6 discipline)

| gate | prediction (model bet) | falsified if |
|---|---|---|
| **G1** (Q1, headline) | tail rate/decade falls with F₀, power exponent n_slow ∈ [1–4] | tail rate F₀-flat (±20%) → slow pre-conformance is Liu2017-specific → demote form |
| **G2** (Q2) | fast loss follows S·(reservoir)/F₀ with n_fast ∈ [1.5–5]; **plateau below p_ref** (loss saturates at low F₀) | no plateau + power law loses to linear/exp on BIC |
| **G3** (Q3) | full-curve fit MAE ≤ 2× the replicate scatter floor; C_creep/emb_cap ≠ Liu2017 values (per-pair OK) | form can't fit within 2× floor at any constants → structural miss |
| **G4** (Q4) | 10-min post-tightening relaxation *fraction* decreases monotonically with F₀ | flat or increasing → pre-conformance mechanism wrong even if curves fit |
| **G5** (transfer) | applying **Liu2017's exponents** with only levels refit lands within 1.5× of the own-fit MAE | >1.5× → exponents are per-rig (documented, not hidden) |
| **G6** (Q5) | declared agnostic — either outcome updates the engine clock | — |

Analysis is frozen: `axial_ground_fit.py` (fit) + `axial_overfit_checks.py` (LOCO/BIC/
residual-floor/stability) run unmodified on the new CSVs; G5 adds one swap-exponents run.

## 5. Budget & schedule (estimate)

| item | quantity |
|---|---|
| Actuator time — Arm A | 6×11 h + 4 replicate runs ≈ **110 h** |
| Arm C + D | ≈ 30 h |
| Arm B | bench fixtures, parallel (24 h × 3, no actuator) |
| Calendar | ~3–4 weeks incl. setup, with Arm D as the cut-line |
| Consumables | ~26 M12 10.9 fastener sets (one lot), 2 plates, 1 load washer |

**Decision points for you** (the plan assumes; adjust freely): (a) servohydraulic
availability & max frequency (25 Hz assumed; anything ≥10 Hz works, Arm A stretches);
(b) M12 to match Liu vs M16 to match UFU tooling — M12 recommended (isolates the rig
variable); an M16 repeat later would then test *size* transfer separately; (c) dry vs
lightly-oiled threads — pick one and document (per-lube doctrine); (d) whether Arm D
survives the time box.

## 6. What each outcome means

- **G1–G5 pass:** the pre-conformance forms hold cross-rig → exponents get a transfer
  band → candidate for `shared`-block adoption (your call), and the model's axial
  channel becomes *predictive* with two-rig provenance.
- **G1 fails (tail F₀-flat here):** the Liu2017 slow-tail load-dependence is
  rig-specific → `creep_conform_exp` stays a per-rig opt-in, doctrine unchanged —
  and we will have learned it from OUR data, pre-registered, not from a fit.
- **Either way:** UFU gains its own axial dataset (currently the rig portfolio is
  transverse-only), the C_creep anchor gets a third pair (§4.7), and Arm D seeds the
  §4.6 amplitude mechanism.
