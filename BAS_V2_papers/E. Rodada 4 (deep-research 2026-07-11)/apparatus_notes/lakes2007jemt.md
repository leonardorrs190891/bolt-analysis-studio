# Jaglinski, Nimityongskul, Schmitz & Lakes 2007 (JEMT) — Study of Bolt Load Loss in Bolted Aluminum Joints

## Citation + DOI

T. Jaglinski, A. Nimityongskul, R. Schmitz, R. S. Lakes, "Study of Bolt Load Loss in
Bolted Aluminum Joints," *Journal of Engineering Materials and Technology* 129 (2007)
48-54. DOI: [10.1115/1.2400262](https://doi.org/10.1115/1.2400262). University of
Wisconsin-Madison (Materials Science Program; Engineering Mechanics Program;
Department of Engineering Physics / Biomedical Engineering / Rheology Research Center).

Companion source of the underlying uniaxial creep/relaxation data (Table 1's isochronal
construction): Jaglinski, T., and Lakes, R. S., 2004, "Creep Behavior of Al–Si Die-Cast
Alloys," *ASME J. Eng. Mater. Technol.*, 126, pp. 378–382 (ref. [21] in this paper) — not
in this library, but the direct provenance of every g1/g2/n/f1/f2/n number reproduced
below.

## Gap tag(s)

- **G6 (primary)** — elevated temperature (220, 240, 260°C), the only paper in this
  library with a controlled, isothermal, multi-day **static thermal hold** at these
  levels. No vibration, no cyclic mechanical load anywhere in this study — pure
  thermal-expansion + creep/relaxation of an as-installed axial preload.
- **G3 (primary)** — per-pair creep constants for a **steel bolt screwed directly into a
  die-cast Al-Si block** (no nut, no gasket, no washer) — a materially distinct pairing
  from every other creep-relevant source in the library (steel-on-steel flanges,
  composite laminates, etc.).
- **G5 (minor)** — an explicit, two-level **retightening/preconditioning** protocol
  (bolt tightened once into a fresh hole vs. tightened, rested overnight, and
  retightened before test) run as a controlled contrast at all three temperatures.

## Rig / apparatus

- **Not a purpose-built rig — real engine hardware.** The test article is the cylinder
  head bolt of a small, air-cooled, die-cast-aluminum lawn-mower engine block. The
  cylinder-head joint was physically cut away from the rest of the engine for lab
  handling; otherwise no modification was made to the joint geometry itself. **No
  gasket** — the bolt threads directly into the as-cast aluminum (metal-to-metal joint,
  the aluminum thread itself acting as the "nut").
- **Instrumentation — direct bolt-shank strain gaging (not a load cell or washer
  transducer).** Two electrical-resistance strain gages were mounted on opposite sides
  of the bolt shank, wired as a full bridge with two further gages on a **dummy
  temperature-compensation bolt** inserted in an adjacent hole (only partially, shank
  exposed) so that thermal-output drift cancels. Gage models: Micro-Measurements
  **WK-13-250BG-350** for the first two tests, **WK-06-125AD-350/W** for the rest
  (changed for a lower-profile connection; gage size and thermal-expansion match were
  re-tuned for the bolt's size/material). Two 2.49 mm holes were drilled through the
  bolt head to route Teflon-coated lead wires without fouling the joint; wires anchored
  with CC High-Temperature Cement (Omega Engineering) and soldered to the gage leads
  with high-temperature solder (Micro-Measurements 570-28R); Kapton film insulates the
  soldered connection and (double-wrapped) the whole assembly from shorting against the
  cylinder head. Mineral wool was wrapped over both the active and dummy bolts so that
  **aluminum temperature, not air temperature**, drives the thermal compensation.
- **Control mode: static isothermal HOLD, not a thermal cycle.** The oven was
  preheated to the target set-point and allowed to reach steady state *before* the
  gaged joint was inserted (a step-like thermal boundary condition on the joint, even
  though the joint itself then takes 1-2 h to reach thermal equilibrium — see Fig. 4).
  Each joint was held at temperature for **exactly one week**, then removed and allowed
  to cool to room temperature while strain and temperature continued to be logged.
- **Acquisition**: a Tektronix TDS 420A oscilloscope recorded continuously for the first
  hour; for the remaining ~1 week the same instrument was re-triggered via an external
  clock + separate function generator (explains the "10%/1% of data shown" decimation
  callouts on Figs. 5/7 — the plotted markers are a manageable subsample of a much
  denser log).
- **Bolt elastic modulus independently measured, not assumed**: Resonant Ultrasound
  Spectroscopy (RUS, shear mode) on a cylinder cut from the same bolt stock gave
  **E_bolt = 205 GPa** (with assumed steel ν = 0.33) — used directly in the structural
  model, not a handbook default.
- Bolt-to-hole clearance was "reduced from 1.5 mm to 0.5 mm" once the bolts were gaged
  (radial clearance around the shank) — likely to steady/center the instrumented bolt
  in its hole; see the Digitization Caveats for a probable inconsistency between this
  text statement and Table 1's printed hole-diameter dimension.

## Specimen / materials

- **Bolt**: 8 mm diameter (d_b = 0.008 m) steel cylinder-head bolt/cap screw, "typical
  of those supplied with each specific engine block." **No ISO/SAE property class is
  stated anywhere in the paper** — a genuine gap, not an omission on our part.
- **Effective engaged length** λ = 0.036 m (36 mm), taken from the base of the bolt head
  to the **third engaged thread** (not the full bolt length — the authors checked: using
  the full length instead changes the 1-week prediction by only ~2%).
- **Bolt-head bearing diameter** d_bh = 0.0165 m (16.5 mm); **hole diameter** d_h is
  printed in Table 1 as **0.095 m** (see caveats — almost certainly a typo for
  0.0095 m); **edge distance** d_j = 0.005 m (hole edge to flange edge, frustum-of-cone
  effective-area formula, Eq. 5).
- **Bolt cross-section** A_b = 5.02×10⁻⁵ m² (= plain shank area, π/4×0.008² — confirms
  reported stresses are **nominal shank stresses**, not thread-root or any
  concentration factor). **Effective aluminum flange area** A_c = 1.07×10⁻⁴ m²
  (computed via the frustum-of-cone approximation, not measured).
- **Flange**: three separate as-received, production die-cast small-engine blocks
  ("first flange" / "second block" / "third block"), cut down to just the head-joint
  region. Material = **eutectic Al-Si die-cast alloy, exact composition proprietary**
  (undisclosed by the manufacturer).
- **No gasket. No locking device** (plain steel bolt threaded directly into the Al-Si
  casting). **Surface finish (Ra/Rz) not reported** — same gap as most other sources
  relative to BAS V2's `emb_depth_vdi` roughness-class lookup.
- **Tightening method**: strain-gage-monitored, **not torque-controlled** — "since
  applied torque is not directly related to preload due to varying friction losses in
  each hole, it is paramount that applied bolt strains match for subsequent tests at
  different temperatures." The paper never characterizes a torque-preload relationship
  or a friction coefficient at all.

## Test matrix

18 bolt tests total across 3 blocks, an unbalanced 3-temperature × 2-preconditioning
design (built for a within-block repeatability check, not a full factorial):

| Block | Temperature(s) | Unconditioned tests | Preconditioned tests | Figure |
|---|---|---|---|---|
| 1 ("first flange") | 220, 240, 260°C (1 each) | 1, 2, 3 (all 3) | — | Fig. 5 |
| 2 ("second block") | 260°C only | 4a, 4b, 5 | 6, 7a, 7b | Fig. 6(a)/(b) |
| 3 ("third block") | 240°C | 8 | 9a, 9b, 10a, 10b | Fig. 7(a) |
| 3 ("third block") | 220°C | — | 11a, 11b, 12, 13 | Fig. 7(b) |

Totals: 7 unconditioned tests, 11 preconditioned tests, 18 tests overall. A curated
"one representative curve per temperature" comparison of the **preconditioned** results
across all three temperatures (7a/10b/13) is given separately as **Fig. 8** — the
cleanest single plot in the paper and the source of our primary CSV set.

- **Initial preload / prestrain context**: "roughly 25% of the aluminum alloy's
  room-temperature yield strength" at the RT-installed condition; at the highest test
  temperature (260°C) the *same* installed preload corresponds to "50% of the yield
  strength in the aluminum alloy" (i.e., 50% of the much-reduced high-temperature Al
  yield, not a doubled preload).
- **Hold time**: exactly 1 week (604 800 s) at temperature for every test, followed by
  a monitored cool-down to room temperature.
- **#curves in the paper**: 18 raw test curves (Figs. 5, 6, 7) plus the 3-curve curated
  comparison (Fig. 8) and 2 theory-overlay figures (Figs. 10, 11) reusing the same
  experimental traces. **We digitized 6** (see Curve Inventory) — the 3 Fig. 8
  preconditioned curves (one per temperature) plus the 3 Fig. 5 unconditioned curves
  (one per temperature, same "first flange"/block 1), giving a clean temperature ×
  preconditioning contrast without redigitizing near-duplicate replicates.
- **Swept variables**: temperature (3 levels), preconditioning (2 levels, unbalanced),
  block/replicate (an explicit repeatability check, concentrated at 260°C).

## Experimental nuances

- **Room-temperature embedment relaxation ~10% in the first few minutes.** Even before
  any heating, bolts lost preload attributed to "embedment relaxation... localized
  plastic deformation due to small material imperfections on thread contact surfaces,"
  citing Bickford's generic ~10% figure as consistent with their own observation. This
  is **not a separately digitizable curve** here — it happens in the first minute(s)
  after tightening, essentially at or before our curves' first digitized point
  (t = 10 s), and is folded into (not resolvable from) each curve's own baseline.
- **Retightening preconditioning protocol (G5)**: "preconditioned" holes were tightened
  to the desired prestrain, left to sit at room temperature **overnight**, then
  **retightened as necessary** before the actual elevated-temperature test began.
  "Unconditioned" holes were simply tightened once, mimicking as-manufactured assembly.
  This is the source of our unconditioned-vs-preconditioned CSV contrast.
- **Near-total loss above 220°C is a POST-COOLDOWN, room-temperature statistic — not
  visible directly in the at-temperature decay curves.** After the full week at
  temperature, joints were removed from the oven and allowed to cool while still
  monitored (Fig. 9, tests 12/13 only, 220°C). It is only **after this additional
  cooldown** that bolts above 220°C reach ~100% prestress loss (many removable by hand)
  and 220°C-bolts retain ~20% or less **of the original room-temperature installed
  preload**. Our digitized Figs. 5/8 curves stop at the *end of the at-temperature
  hold* (still hot) — see Digitization Caveats for why their end-values (F/F0≈0.4-0.7
  unconditioned, ≈1.5 preconditioned) should not be confused with this 100%/20% figure.
- **Model behavior depends systematically on preconditioning.** For unconditioned
  holes, a pure creep-compliance model *overpredicts* retained bolt stress (avg +24%).
  For preconditioned holes, the true behavior sits *between* the creep and relaxation
  model predictions: creep underpredicts by 30% (260°C) / 10% (220°C); relaxation
  overpredicts by 20% (260°C) / 9% (220°C). The authors attribute this to the
  bolt/flange structural-compliance ratio being "intermediate" (neither the
  bolt-much-stiffer nor bolt-much-more-compliant limit, where creep or relaxation would
  strictly govern, applies here).
- **Unexplained slope changes in unconditioned curves.** Block-1 (Fig. 5, all
  unconditioned) shows "several pronounced slope changes... after several hours,"
  reproduced in none of the underlying uniaxial data; a milder version appears in
  Block-2's unconditioned 260°C curves (Fig. 6a) but not in any preconditioned curve.
  Mechanism not identified by the authors (die-casting porosity and non-uniform thread
  engagement are plausible candidates, not stated).
- **An instrumentation artifact, explicitly flagged**: the visible "kink" in Fig. 4's
  raw data is due to a strain-gage-conditioner channel change mid-test, not a physical
  effect — a useful general reminder that abrupt slope discontinuities in these
  week-long tests can be measurement artifacts.
- **Creep compliance / relaxation modulus constants (Table 1, reproduced verbatim)** —
  units: g1 in Pa⁻¹, f1 in Pa. Functional forms:

  `J(t,σ) = g1 + g2·σ^0.75·((t−10)/4990)^n`  (Eq. 7; t in seconds, σ in Pa, strain ε = J·σ)

  | Temp | g1 [Pa⁻¹] | g2 | n |
  |---|---|---|---|
  | 220°C | 1.478×10⁻¹¹ | 1.094×10⁻¹⁸ | 0.485 |
  | 240°C | 1.510×10⁻¹¹ | 6.050×10⁻¹⁸ | 0.280 |
  | 260°C | 1.503×10⁻¹¹ | 6.139×10⁻¹⁸ | 0.340 |

  `E(t,ε) = f1 + f2·ε^0.75·((t−10)/4990)^n`  (Eq. 9; stress σ(t) = E(t,ε)·ε)

  | Temp | f1 [Pa] | f2 | n |
  |---|---|---|---|
  | 220°C | 7.53×10¹⁰ | −1.36×10¹² | 0.246 |
  | 240°C | 7.16×10¹⁰ | −1.27×10¹² | 0.2942 |
  | 260°C | 7.17×10¹⁰ | −1.39×10¹² | 0.3139 |

  The stress/strain exponent **0.75 is fixed, not fitted** ("this value fits well with
  the isochronal data points of the metals," ref. [8]), and **n < 1 always** → the
  underlying uniaxial creep is **primary creep only** (no secondary/tertiary regime was
  reached in the source tests). The 3-point isochronal method used strains at
  t = 10, 5000, 1×10⁵ s (shifted by the `(t−10)/4990` term to account for the creep
  frame's 2 s load-rise time and the fact that data logging only starts at t = 10 s,
  not a true t = 0).
  Dimensional/geometric inputs from the same table: λ=0.036 m, d_b=0.008 m,
  d_bh=0.0165 m, d_h=0.095 m (sic), d_j=0.005 m, A_b=5.02×10⁻⁵ m², A_c=1.07×10⁻⁴ m².

## Main conclusions

- After 1 week at temperature and cooldown to room temperature: all bolts tested above
  220°C (i.e., at 240 and 260°C) showed ~100% prestress loss (often removable by hand);
  bolts held at 220°C retained ~20% or less of their original prestress.
- A simple 1-D structural model (Arimond-type, Eq. 3) combined with nonlinear
  stress/strain-dependent (but **not temperature-dependent** — each temperature needs
  its own separately-fitted constants) creep-compliance/relaxation-modulus equations
  from independent **uniaxial** testing predicts bolted-joint load loss to within
  9-30% — a useful engineering-level result from coupon data alone, but the simple
  model **does not capture the joint-level slope-change nonlinearities**.
- Unconditioned holes: creep-based models overpredict retained stress (avg +24%).
  Preconditioned holes: true behavior is intermediate between creep and relaxation
  model predictions (creep underpredicts 30%/10% at 260/220°C; relaxation overpredicts
  20%/9% at 260/220°C).
- Deviations are attributed to the model's lumped 1-D compliance-ratio treatment not
  capturing the true heterogeneous/concentrated stress state under the bolt head and in
  the aluminum threads, and to imperfect representation of the true (non-step,
  multi-stage) time-temperature boundary condition.
- The authors' own top recommendation for improvement is adding an explicit
  **temperature-dependence term** to the creep-compliance formulation so a single
  constitutive law could serve any general load/temperature history, rather than
  needing a fresh isochronal fit per temperature.

## Curve inventory

| Figure | Condition | CSV filename | x-unit | F0 (MPa, at t=10 s) | # pts |
|---|---|---|---|---:|---:|
| Fig. 8 | Preconditioned, test **7a**, 260°C (block 2) | `lakes2007jemt_260C_preconditioned.csv` | s | 95 | 28 |
| Fig. 8 | Preconditioned, test **10b**, 240°C (block 3) | `lakes2007jemt_240C_preconditioned.csv` | s | 96 | 28 |
| Fig. 8 | Preconditioned, test **13**, 220°C (block 3) | `lakes2007jemt_220C_preconditioned.csv` | s | 94 | 28 |
| Fig. 5 | Unconditioned, test **3**, 260°C (block 1) | `lakes2007jemt_260C_unconditioned.csv` | s | 118 | 28 |
| Fig. 5 | Unconditioned, test **2**, 240°C (block 1) | `lakes2007jemt_240C_unconditioned.csv` | s | 118 | 28 |
| Fig. 5 | Unconditioned, test **1**, 220°C (block 1) | `lakes2007jemt_220C_unconditioned.csv` | s | 118 | 28 |

Peak (thermally-induced) values read off the same curves, for provenance: 7a≈218 MPa
@ t≈4×10³ s; 10b≈196 MPa @ t≈5×10³ s; 13≈180 MPa @ t≈5×10³ s; test-3≈217 MPa
@ t≈1×10³ s; test-2≈179 MPa @ t≈1.5×10³ s; test-1≈160 MPa @ t≈5×10³ s. End-of-hold
(still at temperature, before cooldown) values: preconditioned trio converges to
≈143-144 MPa regardless of temperature; unconditioned trio ends spread out
(≈50/65/88 MPa for 260/240/220°C respectively — 220°C retaining the most, consistent
with the paper's qualitative trend).

**Not digitized (context only)**: Fig. 1 (head-joint photo), Fig. 2 (gaged bolt/gage
assembly photo), Fig. 3 (uniaxial creep/relaxation model-vs-data at 220°C — the source
validation behind Table 1, not a bolted-joint curve), Fig. 4 (single representative
thermal ramp-up example; establishes the "1 min/1 hr/1 day/1 week" time-marker
convention seen on Figs. 5-7; largely redundant with Fig. 5's own 260°C/block-1 curve),
Fig. 6 (block-2 replicates at 260°C only: 3 unconditioned [4a,4b,5] + 3 preconditioned
[6,7a,7b] — 7a already captured via Fig. 8; skipped as redundant replicate/scatter,
described qualitatively above), Fig. 7 (block-3 replicates at 240°C [8,9a,9b,10a,10b —
10b already captured via Fig. 8] and 220°C [11a,11b,12,13 — 13 already captured via
Fig. 8]; same reasoning), Fig. 9 (cooldown-only transient for tests 12/13, 220°C,
re-zeroed time axis — a different physical process/x-axis than the at-temperature
hold; this is where the paper's headline post-cooldown 100%/20% figures actually
originate, but it is not itself a "hold at elevated temperature" decay curve), Figs.
10-11 (model-vs-experiment theoretical overlays reusing the *same* experimental traces
already in Figs. 5/8 — no new experimental data).

## V2 mapping

- **Per-pair `C_creep` (steel bolt / die-cast Al-Si, no gasket)**: this is the cleanest
  "pure thermal creep/relaxation, no vibration" dataset in the library, directly
  relevant to the `C_creep` per-pair identifiability question (`MODEL_LEGITIMACY.md`
  §4.7). However, BAS V2's `C_creep` (Norton-law creep constant in `JointMaterial`) is
  currently used athermally (ambient-temperature static-hold creep, per the
  `anchor_creep.py`/li2022marstruc anchor) and **has no temperature-dependence term at
  all** in the engine. This paper's regime is 220-260°C with **3 numerically
  independent** g1/g2/n triplets (one per temperature — not interpolable without
  assuming a functional T-dependence). Treat this source as a strong **candidate anchor
  for a future ΔT-driven thermal-creep mechanism** ("ΔT reserved" in
  `parameter_registry.py` per CLAUDE.md roadmap), not as a plug-in value for the
  current athermal `C_creep`.
- **Functional-form mismatch**: the paper's own creep law,
  `J(t,σ) = g1 + g2·σ^0.75·t^n` (compliance = constant + stress^0.75 · time^n, a
  Findley/nonlinear-superposition family), is **not** the same functional family as
  BAS V2's Norton-law creep term. A literal g1/g2/n → `C_creep`/`n_creep` transplant is
  not dimensionally or functionally direct — use this data as a **validation target**
  for a new thermal-creep sub-model, not a source of a literal `C_creep` number.
- **Thermal-expansion mismatch (missing mechanism)**: the large, clearly visible,
  *reversible-looking* preload rise during heat-up (peak/F0 ratios of 1.9-2.3
  preconditioned, 1.4-1.8 unconditioned) is a pure thermal-expansion-mismatch effect
  (aluminum expands more than steel) that **`DynamicStiffnessAnalyzer` does not
  represent at all today** (no `alpha_thermal`/ΔT-driven elastic-preload term in
  `JointMaterial`). This dataset is a clean, quantified anchor for that missing term,
  independent of any creep assumption (it's read off the rising portion of the curve,
  before relaxation dominates).
- **Embedding (qualitative cross-check only)**: the paper's cited "~10% RT embedment
  relaxation in the first few minutes" is a direct qualitative cross-check for BAS V2's
  state-based `EmbeddingLoss` — but it is **not separately extractable as its own decay
  curve** from Figs. 5/8 (folded into each curve's t=10 s baseline, see nuances above).
- **Preconditioning contrast (G5, candidate not validated)**: the
  unconditioned-vs-preconditioned pair digitized here (same temperature family,
  different pre-test history) is a plausible, imperfect analog for roadmap item 5
  ("embedding renewal on reaperto") — preconditioned holes start at a lower, more
  repeatable baseline (~95 MPa vs ~118 MPa) and show much cleaner peaks (no
  "pronounced slope changes"), consistent with a settling/embedding-consumption
  story, but this is confounded with possibly different per-block target-preload
  choices (see caveats) — same "candidate, not validated" caution already attached to
  the in-library Liu2016wear Fig. 3 analog.
- **No friction/lubrication data**: torque-to-preload is explicitly *not*
  characterized (the paper works entirely in strain/stress space to sidestep it) —
  contributes nothing to `mu_bearing`/`mu_thread` anchors.
- **No vibration/cyclic loading anywhere**: contributes nothing to
  `WearLoss`/`RotationalLoosening`/`surface_damage`. This is a single-mechanism-family
  (thermal + creep/relaxation only) probe, which also means it does **not** fit the
  DIGITIZED_CASES assumption of force- or displacement-controlled *cycling* at a
  frequency — it is a static isothermal hold, not directly comparable to the
  vibration-loosening MAE metrics used across the rest of the 128-case gallery.

## Digitization caveats

- **Table 1's printed `d_h = 0.095 (m)` (95 mm hole diameter) is almost certainly a
  typo for 0.0095 m (9.5 mm).** Reproduced verbatim above per instructions, but flagged:
  a 95 mm hole is geometrically inconsistent with a 16.5 mm bolt-head diameter (d_bh)
  in the Eq. 5 frustum-of-cone derivation, which requires d_h < d_bh for the bolt head
  to bear on the flange at all; 9.5 mm is consistent with the 8 mm bolt shank plus a
  small radial clearance, and roughly matches the text's own mention of a
  0.5-1.5 mm shank-to-hole clearance. Verified by a direct 400 dpi crop of the
  vector-typeset PDF table (`figures/lakes2007jemt_table1.png`) — this is exactly what
  is printed in the original 2007 journal page, not an OCR artifact.
- **F_over_F0 convention**: F0 = each curve's own first digitized point (t = 10 s,
  essentially the as-tightened/pre-heating baseline), **not** the paper's own Eq. 3
  "F0" (which the paper defines as the *peak* post-heating thermal load, used only for
  the Figs. 10-11 theoretical overlays). With our convention, F/F0 rises above 1.0
  during the heat-up ramp (real thermal-expansion-driven clamp-force increase), peaks,
  then decays — the full physical history is preserved. Do not confuse this "1.0" with
  the paper's "100% prestress" language, which is a different, later reference point
  (next bullet).
- **The paper's "100% loss above 220°C / ~20% retained at 220°C" is a POST-COOLDOWN
  statistic, not visible in our curves.** It is measured after the joints were removed
  from the oven and cooled back to room temperature (Fig. 9, not digitized). Our CSVs
  stop at the end of the 1-week *at-temperature* hold (still hot) — the preconditioned
  trio ends around F/F0≈1.5 (≈143-144 MPa, all three temperatures converging) and the
  unconditioned trio ends spread out around F/F0≈0.4-0.7 (≈50-88 MPa). Neither should be
  read as "the retained fraction" the paper's abstract/conclusions quote — that number
  requires the additional cooldown step this source only shows for the 220°C tests.
- **Fig. 5's three curves are visually coincident** (a single undifferentiated line)
  for t below ~30-50 s, separating only once the joints begin heating toward their
  distinct target temperatures. The shared F0=118 MPa baseline used for all three test
   1/2/3 curves is read from this common early segment and carries slightly higher
  uncertainty (±3-5 MPa) than later, well-separated points.
- **General reading uncertainty**: figures are vector-typeset (not scanned raster) and
  were rendered directly from the PDF at 350-500 dpi, so line/tick positions are crisp;
  the main uncertainty is visually interpolating a curve's position between labeled
  gridlines (every 20 MPa in Fig. 8; every 100 MPa with one unlabeled half-way tick in
  Fig. 5) and, in Fig. 5, resolving three curves that overlap tightly through the early
  rise and cross one another around t=5000-10000 s. Estimate ±3-5 MPa typical, ±5-8 MPa
  in the busiest overlap regions (Fig. 5, t≈1000-10000 s).
- **Peak-time reads are approximate** (±20-30% in absolute seconds) since several
  peaks are broad/flat-topped (notably Fig. 8's 220°C/test-13 curve) rather than sharp
  maxima.
- **Small "slope-change" wiggles** explicitly reported by the authors in the
  unconditioned curves (Figs. 5, 6a) and the strain-gage-channel-change kink in Fig. 4
  are smoothed over here — only the primary rise/decay trend is digitized, consistent
  with "accuracy over quantity" for a calibration-input CSV.
- **Not digitized**: Figs. 6, 7 (replicate/scatter curves, superseded by Fig. 8's
  curated comparison for the preconditioned condition — see Curve Inventory), Fig. 9
  (cooldown transient, different x-axis/physical process), Figs. 10-11 (theory
  overlays on already-captured experimental traces). All remain available as rendered
  PNGs in `figures/` (`lakes2007jemt_p4_full.png` … `_p7_full.png` for full pages, plus
  the tight crops `lakes2007jemt_fig5.png`, `_fig8.png`, `_fig5_zoom_rise.png`,
  `_fig8_zoom_rise.png`, `_table1.png`) if a future pass wants the additional replicate
  curves.
