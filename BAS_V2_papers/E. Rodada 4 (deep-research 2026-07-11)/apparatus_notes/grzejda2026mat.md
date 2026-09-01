# Grzejda, Parus & Kwiatkowski 2026 (Materials) — Behaviour of a Preloaded Asymmetric Multi-Bolted Connection Under Cyclic Loads by Experimental Research

## Citation + DOI

Rafał Grzejda, Arkadiusz Parus, Konrad Kwiatkowski, "Behaviour of a Preloaded Asymmetric
Multi-Bolted Connection Under Cyclic Loads by Experimental Research," *Materials* 19 (2026)
1414. DOI: [10.3390/ma19071414](https://doi.org/10.3390/ma19071414) (MDPI, open access, CC BY).
Faculty of Mechanical Engineering and Mechatronics, West Pomeranian University of Technology
in Szczecin (WPUT), Poland. Received 29 Jan 2026, accepted 30 Mar 2026, published 1 Apr 2026.

Part of a single research programme on the same rig/connection: preloading-process study [ref.
36, IEEE Access 2021], bolt-removal health-assessment [ref. 37, FME Trans 2021], and a
**monotonic**-load companion on the identical connection [ref. 38, *Materials* 2021, 14, 2353] —
the present paper is explicitly the cyclic-load extension of [38] and reuses its rig, bolt
calibration and connection design without repeating the calibration details in full (cross-
referenced throughout).

## Role = NULL BENCHMARK / negative control

Gap tag: **benchmark / negative control** — no G1-G8 loosening-physics gap applies; the point of
this paper is the *absence* of preload loss, self-loosening or fatigue-relevant stress under a
real, fairly severe (asymmetric geometry + asymmetric/off-axis loading + two amplitude levels +
three frequencies spanning two decades) cyclic test.

Why this is valuable to BAS V2: essentially the entire calibration/validation library (128
digitized cases) consists of joints that DO lose preload — decaying `F/F0` curves used to fit or
falsify loosening mechanisms. That one-sidedness creates a real risk that a model tuned only
against decay curves becomes "collapse-happy" (predicts some loosening whenever cyclic load is
present, because every calibration target it has ever seen decays). This paper anchors the other
end of the spectrum with real, quantitative, multi-frequency data: a properly preloaded joint,
run at cyclic loads whose amplitude is a substantial fraction of the preload itself (10-20 kN
operating vs. 22 kN preload), across three frequencies (0.1, 1, 10 Hz) and two amplitude levels,
shows **no measurable loosening at all** — bolt force stays within about ±1.5% of nominal
(±2% is the paper's own conservative headline), with the small residual variation fully explained
by a static, non-dissipative structural effect (prying-driven load redistribution), not by any
slip/embedding/creep/wear process. If `DynamicStiffnessAnalyzer` is ever exercised with these
boundary conditions (comfortable preload, no reported interfacial slip, short-duration moderate-
frequency cyclic load), the model's four loss mechanisms should all return near-zero net `dF_0`
per cycle and `preload_ratio(t)` should stay flat — a useful false-positive guard-rail,
complementary to (not a replacement for) the decay-curve-heavy validation set.

## Rig/apparatus

- **Test machine**: Instron 8850 servo-hydraulic testing machine (Instron GmbH, Darmstadt,
  Germany), **force-controlled**. Commercial software WaveMatrix v1.5.318 commands the sinusoidal
  external load `Fo(t)`; this is the independent/control variable. Individual bolt force `Fbi(t)`
  is the measured, dependent response — i.e. this is a **force-mode** experiment throughout, no
  displacement/strain control of the joint.
- **Connection fixture**: the asymmetric 7-bolt connection (see Specimen) is clamped between the
  Instron's upper and lower heads via auxiliary plate supports that allow compression; the whole
  assembly is inclined 60° from horizontal, so an axial ram force is resolved into a combination
  of compressive/tensile and shear loading at the bolted interface.
- **Bolt-force monitoring (per-bolt, all 7 channels simultaneous)**: each bolt carries 4× Tenmex
  TFxy-4/120 resistance strain gauges (Tenmex Electrical Resistance Tensometry Laboratory, Łódź,
  Poland), arranged as two perpendicular measuring grids, glued to the outer cylindrical surface
  of the bolt **shank**, wired into a full Wheatstone bridge. Gauge lead wires exit through 4×2 mm
  holes drilled in each bolt **head** (confirmed not to affect strength — the governing minimum
  cross-section stays at the thread root, unchanged).
- **Signal chain**: bridge signals → Esam Traveller CF conditioner/amplifier (SGA 2D plug-in card;
  8 analogue channels/board, simultaneous acquisition, 16-bit A/D per channel, digital hardware
  filter per channel) → dSPACE MicroLabBox (dual-core NXP QorIQ P5020 @ 2 GHz, Xilinx Kintex-7
  FPGA, 24 analogue-in/16 analogue-out channels, 16-bit, 1 Msample/s, ±10 V range) → PC (AMD Ryzen
  5 5600G, 32 GB RAM, Windows 11) → recorded/processed in MATLAB/Simulink R2018b. An NDN
  DF1743005C 4-channel laboratory power supply feeds the bridges.
- **Prior, separate per-bolt calibration** (full detail in companion paper [38], only summarized
  here): each of the 7 bolts was individually axially loaded on the *same* Instron 8850 using a
  purpose-built ball-joint fixture (special bolt + holder + spherical sleeve + backing plate +
  a **class-10** hex nut + washer — note: a different, stronger nut than used in the actual test
  connection) to obtain a per-bolt linear force-vs-strain characteristic with **zero hysteresis**
  (bolts heat-treated specifically to suppress hysteresis before calibration). The main-test force
  readout for every bolt is this per-bolt linear calibration, not a generic strain-gauge gauge-
  factor formula.
- **Preloading**: bolts tightened in 3 passes to 20% → 60% → 100% of the target force F = 22 kN,
  in a fixed order repeated in every pass (see Test matrix). The paper does not explicitly restate
  whether the tightening itself was closed-loop on the live calibrated bolt-force readout or torque-
  controlled; given the whole rig exists to read bolt force directly, force-feedback tightening is
  the natural reading, but this is our inference, not an explicit statement in this paper.

## Specimen/materials

- **Connection geometry** (Figure 1): two mating plates ("2" and "3"), each **28 mm thick**,
  joined by 7 bolts through an asymmetric contact area; plate "2" is welded to a "top plate" (1)
  and plate "3" is welded to a "base" (5). Overall connection height **266 mm**. The whole assembly
  is inclined **60° from horizontal**. The 7 bolt holes are deliberately **non-uniformly**
  distributed around a kidney/heart-shaped lightening cut-out in the mating faces (Figure 1b,
  Figure 5) — a genuinely irregular pattern, not a regular polygon with one hole removed.
- **Plate material**: 1.0577 non-alloy structural steel per PN-EN 10025-2 [ref. 45] (material
  number 1.0577 is commonly assigned to grade S355J2 in that standard — a well-known
  correspondence we infer for context; the paper itself cites only the material number/standard,
  not a named grade).
- **Bolts**: custom-machined **M10×1.25** (fine pitch), property class **8.8** (ISO 898-1 /
  PN-EN ISO 898-1), machined entirely in-house (Centre for Advanced Manufacturing, WPUT Szczecin)
  to add the 4×2 mm head holes and the shank finish needed for the strain gauges, then heat-treated
  to minimize hysteresis. Bolting selection per PN-EN 1515-1.
- **Nuts**: high hex nuts, property class **8** (ISO 898-2 / PN-EN ISO 898-2) in the tested
  connection (the separate single-bolt calibration fixture instead used a class-10 nut — flagged
  above so the two are not conflated).
- **No washers** in the tested connection — a deliberate choice "to minimise the impact of the
  number of contacts... on modelling accuracy" (the paper's own stated rationale, since the data
  is meant to validate a systemic multi-bolt model).
- **Bolt proof load** (grade 8.8, M10×1.25, per the paper's Discussion): 35.5 kN. Nominal preload
  F = 22 kN ≈ 62% of proof load, selected via **EN 1993-1-8** (PN-EN 1993-1-8, Eurocode 3 Part
  1-8, Joints) [ref. 51] — a fairly standard, non-aggressive utilisation.

## Test matrix

**Preload**: F = 22 kN target per bolt (all 7 nominally identical), applied in 3 passes (20% →
60% → 100% of F), each pass visiting the 7 holes in the same fixed order: **hole 1 → 4 → 7 → 3 →
6 → 2 → 5** (Figure 5's "hole/pass-order" labels: 1/1, 4/2, 7/3, 3/4, 6/5, 2/6, 5/7). This order
was previously identified, in the companion preloading-process paper, as the most suitable
sequence for this specific asymmetric geometry.

**Operating cyclic load** (Instron-commanded, sinusoidal): `Fo(t) = Fom + Foa·sin(2π t/T)`
(Figure 8), applied to the top plate. Nine test variants (Table 2 of the paper):

| Test | Fom (kN) | Foa (kN) | T (s) | f (Hz) | Fo(t) range | Waveform type |
|---|---:|---:|---:|---:|---|---|
| 1 | 10 | 10 | 10 | 0.1 | 0 → 20 kN | pulsating (fully released each cycle) |
| 2 | 10 | 10 | 1 | 1 | 0 → 20 kN | pulsating |
| 3 | 10 | 10 | 0.1 | 10 | 0 → 20 kN | pulsating |
| 4 | 20 | 20 | 10 | 0.1 | 0 → 40 kN | pulsating |
| 5 | 20 | 20 | 1 | 1 | 0 → 40 kN | pulsating |
| 6 | 20 | 20 | 0.1 | 10 | 0 → 40 kN | pulsating |
| 7 | 20 | 10 | 10 | 0.1 | 10 → 30 kN | reduced amplitude (never released) |
| 8 | 20 | 10 | 1 | 1 | 10 → 30 kN | reduced amplitude |
| 9 | 20 | 10 | 0.1 | 10 | 10 → 30 kN | reduced amplitude |

I.e. two "fully pulsating" mean/amplitude combinations (Foa = Fom, released to 0 kN every cycle)
at two force levels, plus one higher-mean/lower-relative-amplitude combination (never released
below 10 kN), each run at three frequencies spanning two decades (0.1, 1, 10 Hz) = 9 variants.

**Recorded/plotted duration**: the time-history figures (Figs. 9-11) show a **60 s window for the
three T=10 s (0.1 Hz) tests (= 6 cycles)** and a **10 s window for the T=1 s (1 Hz, = 10 cycles)
and T=0.1 s (10 Hz, = 100 cycles) tests**. The paper does not explicitly state whether these
windows are the full test duration or a representative excerpt of a longer run (see Digitization
caveats). Tables 3-5 report, per test per bolt (i = 1..7): mean force `Fbmi` (kN), force amplitude
`Fbai` (kN), and max force `Fbmaxi = Fbmi + Fbai` (kN).

## Experimental nuances

- **Prying action drives a real, static load redistribution** (Figure 12's mechanical model):
  because the plates are not perfectly rigid and the connection/loading is asymmetric, the
  effective centre of rotation shifts from the bolt-pattern centroid toward the more-compressed
  outer edge as load increases. This makes bolts No. 1 and No. 7 (on what the authors call the
  "prying line") see a slight, mutually **symmetric unloading** (mean force below the 22 kN
  nominal), while the central bolts (3-6, and to a lesser extent 2) see a slight **overloading**
  (mean force above nominal). This redistribution is present already in the **static/mean** bolt
  force (Table 3) — it is not a cyclic phenomenon — and grows slightly as the mean external load
  `Fom` rises from 10 to 20 kN.
- **Distorted (non-ideal-sinusoid) waveform** in some traces: for the pulsating tests specifically
  (Figs. 9a,b and 10a,b — Tests 1, 2, 4, 5), some bolts show a flattened/distorted peak rather than
  a clean sinusoid, attributed to the same prying/variable-contact-stiffness mechanism (localized
  separation/re-contact of the mating surfaces makes the transfer from the commanded external sine
  to individual bolt force mildly non-linear).
- **The ±2% headline is validated by three independent arguments** given in the Discussion: (1)
  the strain-gauge/Wheatstone-bridge measuring chain itself was confirmed linear with **zero
  hysteresis** during the separate single-bolt calibration; (2) the applied external loads
  (10-20 kN amplitude) stay well below the connection's design strength per EN 1993-1-8; (3) the
  near-null result repeats consistently across all three frequencies and both amplitude levels —
  i.e. it is not a single lucky measurement.
- **Our own recomputation from Table 5** (all 63 `Fbmaxi` values = 9 tests × 7 bolts) gives a
  *tighter* bound than the paper's own "±2%" headline: every reported maximum bolt force sits
  between **-1.31% (bolt 1, Tests 7/8) and +1.45% (bolt 4, Test 4)** relative to the 22 kN nominal
  — i.e. comfortably inside ±1.5%, confirming ±2% is a deliberately conservative round number.
- **Cyclic (dynamic) amplitude alone is far smaller still** (Table 4): 0.004-0.032 kN absolute,
  i.e. **0.02%-0.15%** of the 22 kN nominal. Bolt 6 is consistently the most dynamically-responsive
  bolt (largest `Fbai` in 8 of 9 tests); bolts 1 and 5 are the least responsive.
  Peak-to-peak cyclic amplitude never exceeds ±0.032 kN (bolt 6, Tests 4-6) — the authors state
  this keeps the stress amplitude below the EN 1993-1-8 fatigue limit; no fatigue cracking or bolt
  failure of any kind is reported anywhere in the paper.
- **Bolt numbering (spatial) ≠ tightening order (temporal)** — both use labels 1-7 in Figure 5 but
  are different permutations. Tables 3-5's `Fbmi`/`Fbai`/`Fbmaxi` subscripts follow the *spatial*
  hole numbering (bolt 1 = the hole nearest the base, on the prying line, tightened *first* in
  each pass; bolt 6 = a central hole, tightened *fifth* in each pass) — do not confuse the two.

## Main conclusions

1. Across all nine test variants (two amplitude/mean combinations at two force levels, plus one
   reduced-amplitude combination, each at three frequencies spanning 0.1-10 Hz), **every one of
   the 7 bolt forces stayed within a narrow band of the 22 kN initial preload** — the paper's own
   conservative bound is ±2%; our own tightest bound from Table 5 is -1.31%/+1.45%. **No preload
   relaxation, no self-loosening, and no fatigue-relevant stress amplitude were observed in any
   variant.**
2. The small force variation that does occur is not random: it is a predictable, geometry-driven
   **load redistribution** (prying action), not a dissipative process — bolts near the "prying
   line" (1 and 7) see slight symmetric unloading; central bolts (especially 3-6) see slight
   overloading. Reproducible across the entire test matrix and explained by a simple mechanical
   prying model.
3. A correctly preloaded, **highly** asymmetric (both geometry and loading) multi-bolt connection
   is safe under the tested operating cyclic loads **without any additional anti-loosening
   device or measure** — presented as new evidence because prior cyclic-MBC literature (reviewed
   in the Introduction) is overwhelmingly limited to symmetric connections and/or does not monitor
   individual bolt forces.
4. The authors explicitly position this dataset as a **quantitative benchmark for a forthcoming,
   separate publication** validating a general "systemic approach" to multi-bolt-connection
   modelling (decomposing the joint into plate-pair + interface-layer + bolt-assembly subsystems)
   — i.e. the authors themselves intend this null result as calibration/validation ground truth,
   which is exactly the role assigned to it here.

## Curve inventory

| Figure | Test / bolt | CSV filename | x-axis unit | F0 used to normalize | # points |
|---|---|---|---|---|---|
| Fig. 10b — Test No. 5 (Fom=20 kN, Foa=20 kN, T=1 s → f=1 Hz; "pulsating" 0→40 kN external load) | Bolt No. 1 (hole 1, adjacent to the base / on the "prying line"; smaller of the two digitized amplitudes) | `grzejda2026mat_bolt1_base.csv` | time (s), 0-9.75 s (cycle # ≈ t since T = 1 s exactly) | 22 kN (nominal target preload, EN 1993-1-8 — **not** this bolt's own achieved mean) | 40 |
| Fig. 10b — same test | Bolt No. 6 (hole 6, central; the most dynamically-responsive bolt in 8/9 tests per Table 4) | `grzejda2026mat_bolt6_central.csv` | time (s), 0-9.75 s | 22 kN (same convention) | 40 |

Both CSVs sample the **same test** (Test 5) on the **same time grid** (0, 0.25, ..., 9.75 s — 4
points/cycle at f=1 Hz), chosen because: (a) it is one of the tests with the largest reported
cyclic amplitude for bolt 6 (`Fba6`=0.032 kN, tied with Tests 4 and 6); (b) the T=1 s period gives
a cleanly resolved waveform at this figure's native resolution (unlike the T=0.1 s tests, whose
100 cycles/10 s alias into a solid-looking band); and (c) a shared time base lets the pair
directly contrast the two ends of the prying-driven redistribution the paper describes (bolt 1
undershoots the 22 kN nominal; bolt 6 overshoots it).

Digitized values cross-check tightly against the paper's own Tables 3-4 for Test 5: our pixel
extraction gives mean F=21.727 kN / amplitude=0.0054 kN for bolt 1 (paper: `Fbm1`=21.724 kN /
`Fba1`=0.008 kN) and mean F=22.108 kN / amplitude=0.031 kN for bolt 6 (paper: `Fbm6`=22.108 kN /
`Fba6`=0.032 kN) — within 0.01-0.03 kN (≤0.15% of F0) of the authors' own reported statistics,
confirming the pixel calibration.

**Not digitized (context only)**: Figure 1 (connection scheme/3-D model), Figure 2 (bolt sketch/
photo), Figure 3 (strain-gauge wiring diagram), Figure 4 (single-bolt calibration fixture),
Figure 5 (bolt-hole numbering + tightening order — used only to interpret Tables 3-5), Figure 6
(rig photo), Figure 7 (block diagram), Figure 8 (schematic waveform *definition*, not data),
Figure 9 (Tests 1-3, all 7 bolts — same null pattern as Fig. 10 at smaller amplitude, skipped to
avoid redundancy), Figure 11 (Tests 7-9, all 7 bolts — reduced-amplitude variants, same null
pattern), Figure 12 (prying mechanism diagram), Table 1 (instrumentation specs) and Tables 3-5
(point statistics per test/bolt, already fully transcribed into this note's Experimental-nuances/
Main-conclusions text above rather than re-digitized as a curve).

## V2 mapping

- **Expected engine behaviour, if this case were ever set up as a validation entry**:
  `preload_ratio(t) ≈ 1.00 ± 0.02` (paper's own headline bound), or more precisely `≈1.00` with
  excursions no larger than about `-0.013/+0.015` (our tightened, Table-5-derived bound), for the
  entire run, with **no monotonic drift/decay component**. All four loss mechanisms (Embedding,
  Creep, Wear, RotationalLoosening) should contribute ~0 net `dF_0` per cycle: there is no reported
  interfacial slip (no loosening/relaxation observed at all), so `WearLoss`/`RotationalLoosening`
  have no driving stimulus; the tested windows are short (tens to ~100 cycles) at genuinely
  elastic load levels, so `CreepLoss`/`EmbeddingLoss` should likewise stay negligible. If a model
  run under these boundary conditions predicted a visible preload decay, that would flag the model
  as over-eager to loosen — a useful false-positive guard-rail, complementary to (not a
  replacement for) the mostly-decaying 128-case validation set.
- **Out of scope for the single-joint engine**: the physical effect this paper actually documents
  — prying-driven force *redistribution* across 7 bolts in a statically-indeterminate, asymmetric
  frame — is a linear-elastic **structural/system** effect (an indeterminate load-path problem),
  not a self-loosening mechanism. `DynamicStiffnessAnalyzer` models a single joint's slow-state
  evolution (`F_0, δ_emb, δ_creep, δ_wear, θ_loose, D`); it has no multi-bolt/frame load-path
  model. **Do not** map the bolt-to-bolt spread (bolt 1 vs. bolt 6) onto any of the 4 loss
  mechanisms or onto `k_wear`/`k_loose`/etc. — it is a boundary-condition/geometry effect
  (effectively a per-bolt F0 or per-bolt external-load offset), not a physics-tuner target.
- This paper is therefore best used as a **pass/fail guard-rail** (does the model stay flat when
  it physically should?) rather than as a per-mechanism calibration source — consistent with its
  "benchmark/negative control" gap tag (no G1-G8 loosening-physics gap applies).
- If a future MSD case study is ever built from this paper (e.g. for the Results/Validation
  module), the natural per-bolt input would be F0=22 kN (or the bolt's own Table-3 achieved mean,
  if bolt-level fidelity is wanted), amplitude `Foa`/`Fom` per Table 2, frequency per `T`, and
  **force-controlled mode** (`step_cycle(F_amp, theta_load, freq)`, no `delta_amp` — the Instron
  commands a force, not a displacement). No washer in the load path (per Rig/apparatus) if the
  contact stack is ever modelled in MSD Builder.

## Digitization caveats

- Both digitized curves come from a **single figure panel** (Fig. 10b, Test No. 5), read via a
  colour-matched pixel-extraction script (MATLAB default 7-colour palette; axis box calibrated
  from the plot's own border lines at 500 dpi: pixel columns 52/797 ↔ t=0/10 s, pixel rows 78/858
  ↔ F=22.4/21.7 kN) rather than manual eyeballing — chosen specifically because the resulting
  mean/amplitude values could be cross-checked numerically against the paper's own Tables 3-4 (see
  Curve inventory), giving good confidence in the pixel calibration.
- **Bolt 1's cyclic amplitude** (≈0.005-0.008 kN, i.e. only ~6-9 pixels peak-to-trough at 500 dpi)
  is close to the practical resolution floor of this digitization method. Its envelope/amplitude
  is reliable (cross-checked against Table 4), but the fine within-cycle shape (e.g. any small
  asymmetry) should not be over-interpreted — at this amplitude, pixel-level anti-aliasing noise is
  a non-negligible fraction of the signal. Bolt 6's larger amplitude (≈0.03 kN, ~35 pixels) is well
  clear of this floor and its shape is more trustworthy.
- **Coverage**: only 2 of the 7 bolts and 1 of the 9 tests were digitized (per task scope: "one or
  two representative traces"). Bolt 6 was chosen as the most dynamically-variable bolt (largest
  `Fbai` in 8/9 tests per Table 4). Bolt 1 was chosen over Bolt 5 (the numerically least-variable
  bolt by our own summed-amplitude check across all 9 tests, very close to Bolt 1) because Bolt 1
  is one of the two bolts (with Bolt 7) the authors explicitly single out for the "symmetric
  unloading" prying signature — making the Bolt 1/Bolt 6 pair more illustrative of the paper's own
  narrative. Bolts 2, 3, 4, 5, 7 and Tests 1-4, 6-9 are not digitized here; their point statistics
  are fully available in Tables 3-5 (transcribed/discussed above) if finer coverage is ever needed.
- **Sampling grid**: 0, 0.25, ..., 9.75 s (4 points/cycle) was chosen deliberately over a coarser
  0.5 s (2 points/cycle) grid — because the period T=1 s is an exact multiple of 0.5 s, a 0.5 s
  grid aliases into peaks-and-troughs only (loses the rise/fall shape entirely and, despite being
  numerically correct, visually resembles a manufactured square wave). The 0.25 s grid preserves a
  recognisable rise-peak-fall-trough waveform shape while spanning the full plotted 10 s/10-cycle
  record and staying within the requested 15-40 point budget.
- **Normalization convention**: `F_over_F0` uses the **nominal target** preload F0=22 kN (the same
  value the paper's own Z-indicator, Eq. 2, is defined against), not each bolt's individually-
  achieved mean force (Table 3). This is intentional, not an error: bolt 1's series therefore sits
  slightly below 1.0 (≈0.987) and bolt 6's sits slightly above 1.0 (≈1.005) by construction,
  mirroring the paper's own framing of "deviation from the 22 kN target."
- **Duration/cycle-count ambiguity**: the paper does not state whether the ~10-100 cycles shown in
  Figs. 9-11 are the full test duration or a representative excerpt of a longer run, nor is a total
  cycle count given anywhere. Treat the "no drift" conclusion as validated over the tens-to-~100-
  cycle window actually shown/analysed, **not** as a verified high-cycle-count (10^4-10^6 cycles)
  fatigue guarantee — a real difference from most other (decaying) curves in this library, which
  often run to 10^4-10^6 cycles.
- Material-number-to-grade mapping (1.0577 → commonly S355J2 per EN 10025-2) is our own well-known-
  correspondence inference added for context; the paper itself cites only the material number and
  standard, not a named steel grade.
