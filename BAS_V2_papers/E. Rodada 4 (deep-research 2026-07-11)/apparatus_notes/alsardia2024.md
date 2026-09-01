# Alsardia 2024 (Acta Polytechnica Hungarica) — Bolt Preload Variations During Repeated Tightenings

## Citation

Talal Alsardia, "Bolt Preload Variations During Repeated Tightenings," *Acta Polytechnica
Hungarica* 21(2) (2024) 133-150. Department of Railway Vehicles and Vehicle System Analysis,
Faculty of Transportation Engineering and Vehicle Engineering, Budapest University of Technology
and Economics (BME), Hungary. e-mail: alsardia@edu.bme.hu.

**No DOI is printed anywhere in this PDF.** *Acta Polytechnica Hungarica* is a fully open-access
journal (published by Óbuda University); cite by volume/issue/page only, as instructed.

## Gap tag(s)

- **G5 (primary) — re-tightening / embedding renewal.** This is a *repeated full
  tighten-then-fully-release* protocol on the same bolt/nut (20 cycles), at **constant input
  torque**, i.e. a direct, clean, multi-point analog for `retighten()`/`k_emb_renew`/
  `emb_consumed_frac` territory (CLAUDE.md roadmap item 5) — richer than a single retightening
  event, and independent of the in-library Z. Liu et al. 2020 paper (cited here as ref. [12],
  "Changing behavior of friction coefficient for high strength bolts during repeated tightening,"
  *Tribol Int* 151) which the paper's own literature review distinguishes as a related but separate
  study.
- **G7 (secondary) — lubrication contrast.** Four lubrication states (as-is / dry / MoS2 / oiled)
  on the *same* bolt/nut geometry, torque, and protocol, with a directly reported first-cycle nut
  factor **K** per condition (Table 6) — a clean, quantified friction/nut-factor anchor set,
  useful for `mu_bearing`/`mu_thread` defaults by lubrication condition.

## Rig / apparatus

- **Control mode: torque-controlled static tightening, full release between tightenings** — NOT a
  vibration/Junker transverse-slip rig and NOT a cyclic rotation-loosening test. Each "tightening"
  is a discrete, quasi-static event: torque up to 20 N·m, hold briefly (preload noted), then fully
  loosen the nut until preload returns to zero, then re-tighten. Repeated 20× per bolt.
- **Fixture** (Fig. 2, Fig. 6): the bolt head is clamped in a bench **vise** (fixed reaction — there
  is no clamped two-flange "grip" stack in the usual sense). The bolt shank passes through a
  dedicated **HBM KMR+/40 kN strain-gauge bolt-force sensor**, sandwiched between "Washer 1"
  (nut side) and "Washer 2" (head side); the M8 nut is tightened onto the exposed threaded end.
  This is a standard torque-tension load-cell fixture, not a representative flange/plate joint.
- **Torque tool**: manual ½-inch mechanical torque wrench (Brüder Mannesmann Werkzeuge, type II
  class A, range 10-210 N·m, accuracy ±4%), operated by a single operator (the author) throughout,
  same tool/environment for all tests — tightening-speed effects deliberately not controlled for
  (cited as negligible per refs. [21-23]). Average time to generate preload per tightening ≈1.06 s
  (Fig. 3 sample trace).
- **Sensor / DAQ**: HBM KMR+/40 kN bolt-force sensor calibrated per VDI/VDE 2638, accuracy class
  1.5 (±1%); HBM QuantumX data acquisition unit + PC logging, per **ISO 16047**.
- **Environment**: closed, air-conditioned room held at constant 25°C / 55% RH throughout (clamping
  force is temperature/humidity-sensitive per ref. [7]).
- **Sample design**: 20 *different* bolt+nut pairs per lubrication condition (not one bolt reused
  across conditions), each pair carried through its own 20-cycle tighten/release sequence — so the
  reported curve at each tightening number is a **cross-sectional mean over n=20 specimens**, not
  one specimen's own repeated-tightening trajectory. 4 conditions × 20 bolts × 20 cycles = **1600
  individual measurements** (matches the abstract).

## Specimen / materials

- **Bolt**: M8×40, **full-threaded** (no unthreaded shank — Table 1 lists an unthreaded length
  under the head of only 2.25 mm), property class **10.9**, black surface finish.
- **Nut**: M8, property class **8**, same black finish. Bolts/nuts/washers are deliberately
  **commercial, uncertified fasteners** ("cheapest types" from fastener shops, unknown manufacturer
  and batch) — a stated design choice contrasting with most literature that uses certified,
  known-spec hardware.
- **Geometry** (Table 1, ISO thread nomenclature): pitch P=1.25 mm (coarse), thread lead angle
  α=3.168°, thread profile angle β=60°, across-flats s=13 mm, across-corners e=15 mm, head
  thickness k=5.25 mm, washer-face diameter dw=12 mm, washer-face depth c=0.4 mm, head-junction
  radius r=0.3 mm, computed friction-cone angle ρ'=6.587°. Table 1's two geometric entries labeled
  "d1=7.188 mm" and "d2=10.75 mm" are ambiguous on transcription (see Digitization caveats) — the
  7.188 mm value matches the standard ISO M8 pitch diameter; core bolt identity (M8×40, 1.25 mm
  pitch, grade 10.9/8) is unambiguous from the running text regardless.
- **Lubrication states** (surfaces prepared once, before the *first* tightening only — not
  replenished between the 20 cycles within a condition):
  1. **As-is** — as-received black-finish surfaces, no treatment ("out of the box").
  2. **Dry** — degreased with Loctite SF 7061 solvent before first tightening (removes any factory
     protective film; worst-case friction).
  3. **MoS2** — molybdenum disulfide solid powder lubricant applied to thread + under-head before
     first tightening.
  4. **Oiled** — a few drops of mineral-based 15W-40 motor oil (MOL MSE) applied to thread +
     under-head before first tightening.

## Test matrix

| Variable | Levels |
|---|---|
| Input torque | 20 N·m, constant (all conditions, all 20 cycles) |
| Tightening/release cycles per bolt | 20 |
| Lubrication condition | As-is, Dry, MoS2, Oiled (4) |
| Bolts (=nuts) per condition | 20 (fresh pair per condition, no reuse across conditions) |
| Total measurements | 1600 (4 × 20 × 20) |
| Curves digitized (this note) | 4 — one preload-vs-tightening-number series per lubrication condition |

## Experimental nuances

- **Bilinear vs single-slope trends** (Table 3, Fig. 9): As-is and Oiled show a genuine slope
  *change* around the 5th tightening (As-is: ≈flat then decreasing; Oiled: increasing then flat).
  Dry and MoS2 show the *same* qualitative slope before and after cycle 5 (both "slightly
  decrease"/"slightly decrease" for Dry, both "strong decrease"/"strong decrease" for MoS2) — i.e.
  effectively a single continuous regime, not a real two-stage break, despite Table 3's bilinear
  framing.
- **Oiled is the only condition where preload *increases* with repeated tightening** (+≈20% over
  the first 5 cycles, then plateau ≈+21% through cycle 20) — the opposite sign from every other
  condition and from typical self-loosening preload-loss mechanisms.
- **Rank-order crossings across cycles** (explicitly discussed in the text): at cycle 2, order
  (high→low) is As-is > MoS2 > Oiled > Dry; by cycle 3, Oiled overtakes MoS2 and stays ahead through
  cycle 10; the final order (persisting to cycle 20) is Oiled > As-is > MoS2 > Dry. Separately, in
  the *percentage-loss* ranking, Dry overtakes As-is (becomes the "less-bad" of the two) between
  cycles 11 and 12 — reproduced in our digitized Fig. 10 data (As-is/Dry cross between cycle 11,
  -14.6%/-15.6%, and cycle 12, -17.3%/-14.6%).
- **Theoretical torque-tension prediction (Motosh eq./ISO 16047, with literature-assumed µ [25])
  matches measurement only for the Oiled condition** (17.37 kN predicted vs 17.71 kN measured). For
  As-is and MoS2 the assumed µ *overestimates* friction (measured preload exceeds prediction); for
  Dry it *underestimates* friction (measured preload falls short) — i.e. generic literature µ values
  are not reliable predictors for this uncertified/commercial hardware.
- **Statistics**: two-way mixed ANOVA (lubrication × cycle, n=20/condition) found both main effects
  and their interaction significant at p<2e-16 (Table 4). Dunnett's test vs. As-is as control
  (Table 5) shows Dry and MoS2 significantly worse than As-is at every checked cycle (1, 5, 10, 15,
  20); Oiled is statistically indistinguishable from As-is through cycle 15 but becomes
  significantly *better* by cycle 20 (p=0.0143).
- **Ensemble-mean curves**: per-cycle scatter (IQR/whiskers) is shown only as boxplots (Fig. 7) and
  histograms (Fig. 8) — not digitized here (out of scope; only the preload-vs-tightening-number
  mean curves were requested).

## Main conclusions

- Preload varies significantly and systematically over 20 repeated tighten/release cycles at fixed
  input torque; the direction and magnitude of the trend is strongly lubrication-dependent.
- Findings validate the standard engineering practice against reusing disassembled bolts/nuts/
  washers: the first tightening gives the highest (or, for Oiled, most conservative/stable) preload
  in most lubrication cases.
- A small amount of oil lubricant gives the most stable, repeatable preload across repeated
  tightening — the best-performing condition overall.
- MoS2 gives the highest *initial* preload (lowest initial nut factor, K=0.105) but the widest
  scatter and the largest overall loss (~44.7%) by cycle 20 — good first installation, poor
  repeatability.
- As-is and Oiled behave similarly at the very first cycles (attributed to a thin residual oil film
  from manufacturing/storage on the black-finish surface) but diverge sharply under repeated
  cycling.

## Curve inventory

Primary source figures: **Figure 9** (preload mean, kN, vs. repetition 1-20) and **Figure 10**
(preload percentage change vs. first tightening, vs. repetition 1-20) — both are **vector-drawn
plots** (not raster images) embedded in the PDF, confirmed via `page.get_drawings()` (2646 vector
path objects on Fig. 9's page, 1221 on Fig. 10's page, zero embedded raster images on either page).
Marker centers were extracted directly from the vector path bounding boxes (filled square/circle/
diamond shapes for As-is/Dry/MoS2; clustered stroke centers for the Oiled asterisk markers) and
calibrated against the axis tick-mark vector objects — calibration residuals were <0.02 units on
both axes (essentially exact), confirmed against Table 2's first-cycle values to <0.01 kN.

| Lubrication | CSV filename | x-axis unit | First-tightening preload F1 (Table 2) | Last (cycle 20) | # points |
|---|---|---|---:|---:|---:|
| As-is | `alsardia2024_asis.csv` | tightening # (1-20) | 22.83 kN | 15.67 kN (F/F0=0.687, -31.3%) | 20 |
| Dry | `alsardia2024_dry.csv` | tightening # (1-20) | 12.95 kN | 10.34 kN (F/F0=0.799, -20.1%) | 20 |
| MoS2 | `alsardia2024_mos2.csv` | tightening # (1-20) | 23.71 kN | 13.02 kN (F/F0=0.549, -45.1%) | 20 |
| Oiled | `alsardia2024_oiled.csv` | tightening # (1-20) | 17.71 kN | 21.51 kN (F/F0=1.215, +21.5%) | 20 |

CSV format: header `x,F_over_F0`; `x` = tightening number 1..20; `F_over_F0` computed as
`1 + (Figure 10 % change)/100` (see caveats below for why Figure 10 was used as the primary source
instead of Figure 9's own kN curve). First-tightening absolute preload (kN), transcribed directly
from **Table 2**, is recorded in the table above rather than as a CSV column, matching this
library's established 2-column `x,F_over_F0` convention (cf. `jcsr2023_*.csv`, `liu2016wear_*.csv`).

**Not digitized (out of scope / context only)**: Fig. 1 (torque-distribution schematic), Fig. 2
(rig schematic), Fig. 3 (single tightening-release trace vs. time), Fig. 4 (flowchart), Fig. 5
(bolt drawing), Fig. 6 (setup photo), Fig. 7 (preload boxplots), Fig. 8 (preload histograms),
Fig. 11 (nut factor K vs. repetition — Table 6's clean first-cycle K values were transcribed
instead, see below), Fig. 12 (nut factor boxplot).

**Table 6 (first-cycle nut factor K, transcribed, not digitized)**:

| Lubrication | Calculated K | Theoretical K | Assumed µ [25] |
|---|---:|---:|---:|
| MoS2 | 0.105 | 0.12 | 0.08 |
| As-is | 0.110 | 0.171 | 0.12 |
| Oiled | 0.141 | 0.144 | 0.10 |
| Dry | 0.193 | 0.18 | 0.13 |

## V2 mapping

- **Regime**: constant-torque, full-release repeated installation — maps to `retighten()` /
  embedding-renewal territory (roadmap item 5), *not* the cyclic `step_cycle()` loosening engine
  (no rotation, no vibration, no sustained slip). Each of the 20 points is a discrete
  install-then-fully-disassemble event on nominally the same asperities, i.e. the independent
  variable is **installation count**, not cycles-under-load or accumulated slip — none of the
  existing per-cycle mechanisms (`k_emb_scale`/embedding depth, `C_creep`, `K_archard`/wear,
  `surface_damage D`) are natively driven by a discrete reinstall counter, so this dataset would
  need a new state axis (or a reinterpretation of `emb_consumed_frac` incremented per full
  engagement) rather than a direct slot-in.
- **Constant-torque control means the curve is a friction/nut-factor signature in disguise**:
  since T=K·F·D is held fixed, F_i = T/(K_i·D) — the measured preload trajectory is mathematically
  the inverse of the evolving nut factor (Fig. 11/Table 6). This is a clean secondary source for
  calibrating a friction-coefficient (or nut-factor) evolution law driven by reinstall count.
- **G7 lubrication anchors**: Table 6's calculated first-cycle K per condition (MoS2 0.105, As-is
  0.110, Oiled 0.141, Dry 0.193) is a directly usable candidate default set for `mu_bearing`/
  `mu_thread` by lubrication condition, complementing existing per-paper friction anchors already
  in the library.
- **Oiled's preload *increase* is an unmodeled "conditioning" effect**: friction apparently
  *decreasing* with reinstall count under oil (more of the fixed input torque converts to tension)
  — opposite in sign to every existing V2 mechanism, all of which only remove preload. Flag as a
  modeling gap if a reinstall-count-driven friction-evolution law is ever prioritized; this paper
  is currently the cleanest single anchor for that sign/magnitude (+20% over ~5 reinstalls, then
  flat).
- **Ensemble-mean caveat carries into calibration use**: these curves are population means over
  n=20 specimens per point, appropriate for fitting an *expected* trend but not for single-specimen
  variance/scatter (which would require digitizing Fig. 7/8's boxplot/histogram data instead).

## Digitization caveats

- **Internal inconsistency in the source paper for the As-is condition, resolved in favor of the
  majority of independent sources.** Figure 9's own plotted "As-is" (blue) curve ends at **≈18.8
  kN** at cycle 20 (only a ≈17.7% drop from its own cycle-1 marker), visually confirmed by a tight
  high-DPI crop (no missed/overlapping marker near the 15.7 kN gridline). This **contradicts**
  Table 3 ("22.8 to 15.7"), the body text ("reaching its minimum value of 15.7 kN at cycle 20" /
  "≈31%"), and **Figure 10's own plotted As-is percentage curve** (-31.3% at cycle 20, i.e.
  22.83×(1-0.313)=15.68 kN) — three independent, mutually consistent sources vs. one outlier. The
  other three conditions (Dry, MoS2, Oiled) are mutually consistent across Figure 9, Figure 10, and
  Table 3 to within ≈1 percentage point (normal cross-figure digitization noise). We therefore built
  **all four CSVs from Figure 10** (validated against Table 2's F1 and Table 3's endpoint for all
  four conditions, not just three), rather than Figure 9. If Figure 9's own (apparently erroneous)
  As-is trajectory is ever needed, its vector-extracted values were: 22.83, 23.23, 23.23, 22.66,
  23.00, 22.92, 22.31, 22.07, 21.67, 21.59, 20.77, 20.55, 20.22, 20.21, 19.95, 19.48, 19.22, 18.91,
  19.08, 18.79 kN (cycles 1-20) — noticeably shallower than the table/text/Fig.10-consistent
  trajectory from cycle ≈7 onward. We cannot determine from the PDF alone whether Figure 9's As-is
  series used stale/partial data or a transcription slip on the author's part; it reads as a
  genuine erratum in the source, not a digitization artifact on our end (our calibration residuals
  were <0.02 units on both axes, and Table 2's first-cycle values matched to <0.01 kN for all four
  conditions in both figures).
- **Method**: both figures are native vector plots (PyMuPDF `get_drawings()` found thousands of
  path objects, zero raster images, on each page). Marker centers = bounding-box centers of the
  filled path objects (blue square = As-is, gray circle = Dry, orange diamond = MoS2). The Oiled
  series uses an unfilled green asterisk marker, extracted by clustering nearby stroke-path
  centers: each asterisk resolves to a tight cluster of ≈4 coincident bounding-box centers
  (the crossing strokes of the "*" glyph all share the same center), cleanly separable from the
  sparser single-stroke centers of the connecting dashed line (which are spread along each
  inter-point segment, not clustered). A legend swatch (one marker of each series, positioned
  above the plot's top border, y≈189 pt on Fig. 9's page) was present in the vector data and
  excluded by a y-position threshold.
- **Axis calibration**: fit by least squares against the major/minor tick-mark vector objects
  (8-9 y-ticks, 5-11 x-ticks depending on the figure); residuals were ≤0.02 kN / ≤0.02 percentage
  points and ≤0.005 tightening-numbers — i.e. calibration error is negligible compared to the
  marker-center extraction itself.
- `F_over_F0 = 1 + (Fig. 10 % change)/100`, sign-preserved (positive = preload increase, relevant
  for Oiled) — this is exactly the paper's own eq. (6) `V_i` ratio, just re-expressed as a fraction
  instead of a percentage.
- Table 2's first-tightening kN values (transcribed, not digitized) matched our independent
  vector-extracted cycle-1 marker position on **both** Figure 9 and Figure 10 to <0.01 kN for all
  four conditions, which is the main cross-check underpinning confidence in the axis calibration.
- Table 1's two-column geometry layout produced ambiguous symbol-to-value pairing on linear text
  extraction for two secondary diameters ("d1=7.188 mm", "d2=10.75 mm" — see Specimen/materials);
  does not affect the digitized curves or the unambiguous core bolt identity.
- Figures 7, 8, 11, 12 were not rendered/digitized — out of scope per task instructions (only
  preload-vs-tightening-number curves requested); described qualitatively from the running text
  and Table 6 only.
