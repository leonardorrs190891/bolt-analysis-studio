# baydoun_arxiv — arXiv:2101.12014 (Baydoun & Fouvry)

## Citation (verified from page 1 + cross-check)

**Title (page 1, exact):** "An experimental investigation of adhesive wear extension in
fretting interface: application of the contact oxygenation concept"
**Authors:** Soha Baydoun, Siegfried Fouvry* (*corresponding)
**Affiliation:** Ecole Centrale de Lyon, LTDS Laboratory (Laboratoire de Tribologie et
Dynamique des Systèmes), 36 av Guy de Collongue, 69130 Ecully, France
**Keywords (paper's own):** Fretting wear, Contact oxygenation, Flat-on-flat contact,
Abrasive-adhesive wear
**arXiv id:** 2101.12014 (per supplied filename/PDF; no in-text arXiv watermark string
was found by full-text extraction — see Digitization caveats). Content and title were
independently cross-verified via the reference list of the companion paper
Arnaud/Baydoun/Fouvry (Tribology International 2021, 161:107077; `arnaud2021ti_*` in
this folder), whose ref. [24] reads verbatim: *"S. Baydoun, S. Fouvry, An experimental
investigation of adhesive wear extension in fretting interface: Application of the
contact oxygenation concept, Tribology International 147 (2020) 106266."* This
confirms the peer-reviewed home of this manuscript is **Tribology International 147
(2020) 106266** — a different journal/venue than "Wear 2019" assumed in the task brief
(see next section).

## Gap tag (G2) + why

Tagged G2 (energy-wear formulation constants for the Baydoun/Fouvry fretting-wear
program). **IMPORTANT CORRECTION after reading the full text: this specific paper is
NOT the weighted-friction-energy wear-rate paper.** It contains no wear-volume, no
dissipated-energy axis, and no energy-wear coefficient (α, mm³/J) of its own. Its
entire content is a different (but related and rig-sharing) result: a **power-law
model for the "oxygen distance" `d_O`** — a length scale that partitions the fretting
scar into an outer abrasive-oxidized ring and an inner adhesive-metallic core. It is
still relevant to G2 because (a) it is authored by the same PI/lab, shares the exact
flat-on-flat rig and material family, and is explicitly cited as supplying the
"constant contact pressure" justification used by the wear-rate paper, and (b) its
`d_O(f,p)` partition is the direct input consumed by the actual energy-wear-coefficient
model in the companion Arnaud2021TI paper (see below) — i.e. it supplies the "where"
that the energy formulation needs to decide "how much" (which of two very different
α values applies at a given radius/position).

## NO bolt-loosening curves

Confirmed: zero F/F0-vs-cycle, preload-ratio, or torque curves anywhere in the 37
pages. This is a pure fretting-wear-mechanism materials-science paper (flat-on-flat
coupon rig), not a bolted-joint study.

## Relation to Baydoun2019 Wear (the actual weighted-friction-energy paper)

**Not the same paper, not a preprint of it.** Reference [27] inside this arXiv paper is
verbatim: *"Baydoun S, Fouvry S, Descartes S, Arnaud P. Fretting wear rate evolution of
a flat-on-flat low alloyed steel contact: A weighted friction energy formulation. Wear
2019;426–427:676–93."* That is a **separate, earlier 4-author paper** (adds S.
Descartes and P. Arnaud as co-authors) published in *Wear* — present in this same
round-4 folder as its own PDF ("Fretting wear rate evolution flat-on-flat weighted
friction energy (Baydoun-Fouvry Wear 2019 - HAL).pdf"), being handled by a separate
agent under prefix `baydoun2019wear`. This arXiv paper (2101.12014) cites ref. [27]
exactly once, purely to justify that "this configuration allows a constant contact
area and consequently a constant contact pressure during fretting wear test [27]" —
i.e. it **reuses and confirms** the flat-on-flat constant-pressure rig validated in the
Wear-2019 paper, but does not repeat or re-derive its wear-rate/energy formulation.
**No content overlap; no duplicate curves to worry about** between this note and
`baydoun2019wear`'s.

**Bonus finding — a third, closely related paper already in this library:**
"Modeling adhesive and abrasive wear phenomena in fretting interfaces: A multiphysics
approach coupling friction energy, third body and contact oxygenation concepts"
(Arnaud, Baydoun, Fouvry, *Tribology International* 2021, 161:107077 — file
`Modeling adhesive and abrasive wear in fretting interfaces (Arnaud-Fouvry TI 2021 -
HAL).pdf`, prefix `arnaud2021ti`, already text-extracted in this folder) is the paper
that **actually couples** the `d_O` partition formalized here with **explicit energy
wear coefficients** `α` (mm³/J) — e.g. for Ti-6Al-4V cylinder/plane specimens:
`α_c,ab=4.1e-4 mm³/J`, `α_c,ad=0.5e-5 mm³/J`, `α_p,ab=5.1e-4 mm³/J`,
`α_p,ad=1.1e-4 mm³/J` (its §3, Table 1/Fig.4). **If gap G2's headline deliverable is a
numeric energy-wear coefficient, that number lives in `arnaud2021ti`, not here** —
recommend checking whether the agent handling that file has extracted these α values;
if not, they are a high-value target for a follow-up pass (out of scope for this note,
which is scoped strictly to arXiv:2101.12014).

## Rig / apparatus

Hydraulic fretting wear test system, custom-built at LTDS (Ecole Centrale de Lyon),
for **large horizontal crossed flat-on-flat** contacts. Bottom sample fixed; top sample
displaced by an MTS (MTS Systems Corp.) hydraulic actuator. Measured: fretting
displacement δ, tangential force Q, normal force P → Q-δ fretting log +
dissipated energy `Ed` (J) per cycle (plotted as a schematic axis in Fig. 2 only — not
used quantitatively in this paper's own model). Gross-slip fretting controlled by
monitoring `δg` (residual displacement at Q=0), with `δ*` (imposed stroke) continuously
adjusted to hold `δg` constant. Ambient conditions: T=25±5°C, RH=40±10%.

**Contact geometry:** rectangular crossed flat-on-flat, contact area A = L×W, with L
the length parallel to sliding direction δ and W the transverse length. This
configuration keeps contact area (and hence mean pressure) constant through the whole
test (cf. ref. [27]). Minimum distance from contact center to the free border,
`d = min(L,W)/2` (their Eq. 5), sets the geometric ceiling on the measurable `d_O`.

## Materials + hardness

**34NiCrMo16** (tempered low-alloy steel), homogeneous, both samples. From supplier
documentation (their Table 1):

| Young's modulus E | Poisson ν | Yield σy(0.2%) | Ultimate σu |
|---|---|---|---|
| 205 GPa | 0.3 | 950 MPa | 1130 MPa |

**No hardness (HV) value is reported in this paper.** (Likely reported in the
Wear-2019 companion paper — check `baydoun2019wear` note.)

## Loading matrix

**Reference test condition** (repeated 3×): N=20 000 cycles, p=100 MPa, δg=±100 µm,
f=1 Hz, A=5×5=25 mm² (square).

**Plain crossed flat-on-flat, cross-test sweep** (one parameter varied at a time
around the reference):
- Contact pressure p: **25–175 MPa** (5 levels, 25 MPa steps)
- Sliding amplitude δg: **±25 to ±200 µm** (8 levels, 25 µm steps)
- Frequency f: **0.5–10 Hz** (9 levels: 0.5,1,2,3,4,5,6,8,10)
- Number of cycles N: **5 000–40 000 cycles** (6 levels)
- Contact area A: **10–25 mm²**, varied two ways — reducing L (sliding-parallel) from
  5→2 mm at fixed W=5 mm, or reducing W (transverse) from 5→2 mm at fixed L=5 mm
  (isolates contact-size effect from contact-orientation effect)

**Textured crossed flat-on-flat** (macro-grooved bottom sample, validation set outside
the plain-sample calibration domain): rectangular grooves, depth D=1 mm, thickness
t=0.5 mm, groove length=5 mm, pad width W_pad=0.5–5 mm (varies the minimum
center-to-border distance `d`). Matrix: p={50,100,150} MPa × δg={±50,±100,±150} µm ×
f={0.5,1,5} Hz, N=20 000 fixed. Total dataset for model validation: **104 tests** (49
calibration, plain untextured + 55 validation, textured).

Contact-pressure range for this paper: **25–175 MPa** (well below GPa-scale Hertzian
fretting rigs — this is a **quasi-constant, flat, low/moderate pressure** regime by
design, consistent with the flat-on-flat configuration's purpose).

## Wear law — NOT an energy-wear coefficient; a d_O(f,p) power law for wear-MODE partition

This paper does not fit a wear-rate-vs-energy law. It fits the **length scale `d_O`**
("oxygen distance": the width of the outer, oxidized/abrasive corona measured from the
contact border inward) against each loading variable, one at a time, all normalized to
the reference condition (`d_O,ref=1.51 mm`):

- **Frequency** (Eq. 13): `d_O/d_O,ref = K_f·(f/f_ref)^n_f`, n_f = **−0.22**, K_f=1.12,
  R²=0.86 — `d_O` decreases with frequency (asymptotically, 99%→87%→69% abrasive-area
  fraction for f=0.5→1→10 Hz).
- **Contact pressure** (Eq. 14): `d_O/d_O,ref = K_p·(p/p_ref)^n_p`, n_p = **−0.32**,
  K_p=1.02, R²=0.89 — `d_O` drops 53% from p=25→175 MPa. A simpler companion
  correlation is also given directly in text: `%A_ab = 1.55·p^-0.13` (fraction of
  abrasive area vs. pressure in MPa).
- **Cycles** (Eq. 15): no significant trend; `d_O ≈ K_N·d_O,ref ≈ 1.42 mm`, K_N=0.94
  (±0.10) — stabilized before 5000 cycles, constant out to 40 000.
- **Sliding amplitude** (Eq. 16): no significant trend; `d_O ≈ K_δ·d_O,ref ≈ 1.57 mm`,
  K_δ=1.04 (±0.09) — attributed to the tested amplitudes (±25 to ±200 µm) all
  remaining <8% of the contact half-width, i.e. still deep in "gross slip but small
  vs. contact size" territory, not approaching reciprocating sliding.
- **Contact area / orientation** (Eq. 17): no significant trend; `d_O ≈ K_A·d_O,ref ≈
  1.37 mm`, K_A=0.91 — and no difference between reducing L vs. reducing W (isotropic
  di-oxygen diffusion).

**Combined master power law** (Eqs. 18–20, transcribed directly from the rendered
page — the OCR text layer lost the math, image-verified):

```
d_O/d_O,ref = (K_N·K_δ·K_A·K_f·K_p) · (f/f_ref)^n_f · (p/p_ref)^n_p     (18)
K_N·K_δ·K_A·K_f·K_p ≈ 1.0                                                (19)
d_O = d_O,ref · (f/f_ref)^n_f · (p/p_ref)^n_p                            (20)
   with d_O,ref = 1.51 mm, n_f = -0.22, n_p = -0.32, p_ref = 100 MPa, f_ref = 1 Hz
```

i.e. once the near-unity weak-dependence factors are dropped, `d_O` is governed by
pressure and frequency alone through two mild sub-linear power-law exponents (both
|n|<0.35). Eq. 20 validated against all 104 tests (plain + textured): **R²=0.44,
COR=0.76** for `d_O` itself (Fig. 13); much stronger for the derived areas — abrasion
area `A_ab`: R²=0.98, COR=0.99; relative abrasive fraction `%A_ab`: R²=0.73, COR=0.86
(Fig. 18, Eqs. 20–21 combined with the simple homothetic-rectangle geometry of Fig.
17).

Physical narrative (§4, Discussion): the driver behind all of this is the **friction
power density** `µ·p·v` (µ=friction coefficient, p=pressure, v=sliding speed) — higher
p·v accelerates fresh-metal oxide-layer consumption faster than ambient dioxygen can
diffuse back in, shrinking the oxygenated (abrasive) corona and growing the
oxygen-starved (adhesive) core. No numeric µ value is given in this paper.

## Main conclusions

1. Contact-oxygenation concept (IOP/di-oxygen partial pressure balance, from ref. [20])
   is confirmed experimentally via measurable `d_O`.
2. `d_O` responds strongly (power law) to **pressure and frequency only**; it is
   essentially insensitive to cycle count, sliding amplitude, and contact
   area/orientation over the ranges tested.
3. A single closed-form `d_O(f,p)` (Eq. 20) predicts wear-mode transition (abrasive ↔
   mixed abrasive-adhesive) and the resulting scar partition areas for **both plain
   and macro-textured surfaces** (i.e. generalizes outside its own calibration domain)
   — validated on 104 tests total.
4. Explicitly flagged as a stepping stone toward a full wear-RATE model: "this
   formalization … will permit a better description of the global wear rate such that
   different wear rates should be expected in the distinct adhesion and abrasion
   zones" — exactly what `arnaud2021ti` then does with its two α coefficients.

## Curve inventory

| Figure | CSV | x (unit) | y (unit) | #pts |
|---|---|---|---|---|
| Fig. 7b | `baydoun_arxiv_fig7b_dO_vs_frequency.csv` | frequency f (Hz) | oxygen distance d_O (mm) | 9 |
| Fig. 8b | `baydoun_arxiv_fig8b_dO_vs_pressure.csv` | contact pressure p (MPa) | oxygen distance d_O (mm) | 7 |
| Fig. 9b | `baydoun_arxiv_fig9b_dO_vs_cycles.csv` | cycle count N (cycles) | oxygen distance d_O (mm) | 6 |
| Fig. 10b | `baydoun_arxiv_fig10b_dO_vs_amplitude.csv` | sliding amplitude δg (µm) | oxygen distance d_O (mm) | 8 |

All four were originally plotted by the authors as **dimensionless ratios**
(`f/f_ref`, `p/p_ref`, `N/N_ref`, `δg/δg,ref` on x; `d_O/d_O,ref` on y). Physical units
were recovered exactly (no added uncertainty) by multiplying the read-off ratio by the
paper-stated reference constants: `f_ref=1 Hz`, `p_ref=100 MPa`, `N_ref=20 000 cycles`,
`δg,ref=100 µm`, `d_O,ref=1.51 mm`. The reference (1,1) point in each plot carries the
paper's own error bars (≈±0.08 mm on d_O) reflecting the 3 repeats.

**Not digitized (deliberately, see caveats below):**
- **Fig. 12b** (`d_O` vs. contact-area ratio, two overlapping series "variable L" /
  "variable W") — closed-form result already fully captured above (Eq. 17, K_A=0.91,
  d_O≈1.37 mm); the two marker series overlap heavily at this figure's print size,
  making point-by-point (x,y) extraction unreliable enough that a CSV would risk
  more error than value added over the already-exact closed-form number.
- **Fig. 13** (`d_O,pred` vs `d_O,exp` parity, 7 categories × plain/textured, ~30+
  overlapping markers) and **Fig. 18a/b/c** (`A_ab`, `%A_ab` parity, same categories) —
  multi-series categorical parity scatters with heavy marker overlap; their summary
  statistics (R², COR, quoted above) are stated explicitly in the text and are exact,
  so re-digitizing the scatter cloud was judged lower value than the risk of
  mis-attributing points to the wrong category.
- Fig. 1, 3, 5, 6a, 11, 14, 17: schematics/micrographs/EDX maps, not curves.

## V2 mapping

This paper does **not** supply a `k_wear_spec` or `W_conf_ref`-type number directly —
it has no wear-rate/energy axis. Its transferable content for BAS V2:

- **Rig provenance corroboration**: confirms (independently, via ref. [27]) that the
  flat-on-flat configuration used across this whole Baydoun/Fouvry/Arnaud family is
  legitimately treated as constant-contact-pressure — supports any per-pair constant
  sourced from `baydoun2019wear` or `arnaud2021ti` as being drawn from a genuinely
  constant-p rig, not a Hertzian/variable-pressure one.
- **Exponent family, not a value to import**: `n_p=-0.32` and `n_f=-0.22` govern a
  *different* physical quantity (a wear-**mode** partition length scale, not a
  wear-**rate** or preload-loss exponent) — do **not** plug these into
  `conform_pressure_exp` or `k_wear_spec`'s pressure dependence directly. They are
  offered only as a soft consistency check: both are mild sub-linear
  (|n|<0.35) power laws of the same "Fouvry-lab fretting" family as the pressure
  exponents used elsewhere in this library.
- **Amplitude/cycle/area-independence caveat**: do **not** read "d_O is
  amplitude-independent" as "wear volume is amplitude-independent" — this paper's
  `d_O` is a spatial partition boundary, and its amplitude-independence is explicitly
  attributed to the tested amplitudes staying <8% of contact half-width (still deep
  gross-slip, not approaching reciprocating sliding). BAS V2's wear mechanism
  legitimately keeps amplitude-dependence (slip distance drives Archard removal); this
  finding does not contradict that.
- **Follow-up pointer for gap G2**: the actual α (mm³/J) energy-wear coefficients are
  in `arnaud2021ti` (Ti-6Al-4V, cylinder/plane geometries) — flag for whoever closes
  out G2 to confirm those were captured, since that is the paper that literally
  answers "what is the weighted friction energy wear coefficient."
- 34NiCrMo16 elastic/strength properties (E=205 GPa, ν=0.3, σy=950 MPa, σu=1130 MPa)
  are available if a case study ever needs this specific steel; no current BAS V2
  validation case uses it.

## Digitization caveats

- No in-text arXiv identifier string (e.g. "arXiv:2101.12014v1 [...]") was found by
  full-text extraction of the PDF; the id is taken from the supplied filename and
  corroborated indirectly (title/author match via the `arnaud2021ti` reference list,
  see Citation section). Recommend a final visual check of the PDF's first-page
  margin/footer if arXiv-portal-exact metadata is later required (not done here to
  stay within scope).
- All four digitized curves were read off **linear-linear** dimensionless-ratio plots
  with visible gridlines at 0.5 intervals (y) and figure-specific intervals (x);
  points were read by direct visual inspection of a ≥300 dpi crop against those
  gridlines, not by pixel-coordinate regression — typical precision ≈±0.02–0.03 on
  the ratio axis (≈±0.03–0.05 mm on d_O after rescaling), except the pressure-figure
  x-values, which were cross-validated exactly against the explicit MPa values stated
  in the running text (25/50/75/100/125/150/175 MPa) and the cycle-figure x-values
  against the stated cycle counts (5000...40000) — both match to the ratio grid
  exactly, giving high confidence in those two axes specifically.
- Original PDF text extraction (`pdf_tools.py text`) failed part-way (Unicode
  `⇒` "⇒" in a cp1252 console) until re-run with `PYTHONIOENCODING=utf-8`; full
  37-page text was obtained on the second pass. No content was lost.
