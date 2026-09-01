# Baydoun, Fouvry, Descartes & Arnaud 2019 (Wear) — Fretting wear rate evolution of a flat-on-flat low alloyed steel contact: a weighted friction energy formulation

## Citation + DOI

Soha Baydoun, Siegfried Fouvry, Sylvie Descartes, Pierre Arnaud. "Fretting wear rate
evolution of a flat-on-flat low alloyed steel contact: A weighted friction energy
formulation." *Wear*, 2019, 426–427, pp.676–693.
DOI: [10.1016/j.wear.2018.12.022](https://doi.org/10.1016/j.wear.2018.12.022).
HAL id: hal-03093057 (author PDF, submitted 3 Jan 2021).

Affiliations: Soha Baydoun^(a,b) (LTDS + LaMCoS), Siegfried Fouvry^(a,*) (LTDS,
corresponding), Sylvie Descartes^(b) (LaMCoS), Pierre Arnaud^(a) (LTDS).
^a Ecole Centrale de Lyon, LTDS Laboratory, 36 av Guy de Collongue, 69130 Ecully, France.
^b INSA de Lyon, LaMCoS Laboratory, 27 bis Av. Jean Capelle, F 69621 Villeurbanne Cedex,
France. Keywords (paper's own): Fretting wear, Flat-on-flat contact, Loading conditions,
FEM simulations.

Same lab/rig lineage as three other papers already in this library: `baydoun_arxiv.md`
(Baydoun & Fouvry, *Tribology International* 147 (2020) 106266 — the "oxygen distance"
`d_O` companion, which explicitly cites **this** paper as ref. [27] to justify its own
constant-pressure claim), `arnaud2021ti.md` (Arnaud/Baydoun/Fouvry, *Tribology
International* 161 (2021) 107077 — couples `d_O` with explicit α coefficients for
Ti-6Al-4V), and `fouvry2017ti.md` (Fouvry/Arnaud/Mignot/Neubauer, *Tribology
International* 113 (2017) 460–473 — Ti-6Al-4V cylinder-on-flat, its own `α=K·(φ*)^n`
power law). This note covers only the 2019 *Wear* paper listed above — the **actual**
weighted-friction-energy wear-rate paper (the arXiv/TI2020 note flagged this exact
ambiguity in advance and correctly deferred to this note for the numeric α/exponents).

## Gap tag (G2) + why

Tagged **G2 — pressure-controlled dissipated-energy fretting-wear anchor** for BAS V2's
energy-based wear coefficient (Fouvry α ↔ `k_wear_spec`=K/H) and a pressure exponent for
the conformance gate (`W_conf_ref`, `n`).

Per this round's own indexing (`Models/CALIBRATION_AND_VALIDATION/curve_library/
DEEP_RESEARCH_REPORT_R4.md`, row 1), this paper is explicitly flagged as the
**"G2 (melhor âncora)" — the best anchor for G2** among all papers fetched this round,
with the rationale (translated): *"Flat-on-flat 35NCD16 with quasi-constant controlled
pressure + pressure/amplitude/frequency/duration sweep; energy-weighted formulation →
provenance for the conformance gate's pressure exponent. Caveat: abrasive→adhesive
transition ⇒ regime-conditioned exponent."* That caveat is confirmed firsthand in this
note's Wear-law section below — it is real, not a hedge.

**Why it earns "best anchor" over the other G2-tagged papers in this library**: unlike
sphere-on-flat or cylinder-on-flat rigs (including `fouvry2017ti`'s own Hertzian
cylinder-on-plane), the flat-on-flat geometry here keeps contact area — and hence mean
pressure — genuinely constant as wear progresses (verified by the authors' own FEM
check, see Rig section), which isolates the pressure dependence from a confounding
area-growth artifact. It is also the paper that reports **all four** loading exponents
(cycles, pressure, amplitude, frequency) from dedicated single-parameter sweeps around
one shared reference condition, plus an explicit α value and an Archard-equivalent K.

**Confirmed: this is NOT a bolt-loosening paper.** Zero F/F0-vs-cycle, preload-ratio, or
torque curves anywhere in the 22 printed pages (23 with HAL cover). It is a pure
flat-on-flat fretting-wear coupon/materials-science study — its only value to BAS V2 is
the wear-law functional form + coefficients + the regime-conditional caveat, not a
validation curve.

## Rig / apparatus

- **Test system**: fretting device at LTDS Laboratory (Ecole Centrale de Lyon),
  consisting of an **MTS hydraulic shaker/actuator** imposing displacement-controlled
  cyclic loading on the **top** sample. The **bottom** sample is fixed on an adjustable
  holder used to obtain good flat-on-flat alignment (the paper notes flat-on-flat's main
  practical drawback is high sensitivity to alignment). Ambient conditions: T=25±5 °C,
  RH=40±10 %.
- **Contact geometry — the paper's central methodological point**: FLAT-ON-FLAT, both
  top and bottom specimens square, **5×5 mm ⇒ contact area S=25 mm² fixed**. This
  geometry is deliberately chosen over the more common sphere-on-flat/cylinder-on-flat
  because those geometries' contact area **grows** as wear extends, progressively
  softening the nominal pressure; flat-on-flat instead keeps S — and therefore the mean
  pressure — quasi-static over the whole test.
- **Data acquisition**: displacement δ, tangential force Q, and normal force P are
  recorded, giving a quadrilateral (Q–δ) fretting-cycle hysteresis loop under gross slip.
  Dissipated energy per cycle `Ed` = area of that loop; accumulated `ΣEd` = sum over all
  N cycles (Eq. 1). Sliding amplitude `δg` is held at its target value by continuously
  adjusting the imposed displacement amplitude `δ*` to compensate test-system compliance
  `δs` (`δg = δ* − δs = const`); `δg` is taken equal to the displacement aperture `δo`
  (residual displacement at Q=0), which is not itself affected by system compliance.
  Conventional friction `µ=Q*/P` (Eq. 3, contaminated by border-ploughing at the peak
  displacement) is distinguished from an **energetic friction coefficient**
  `µe = π·Ed / (4·Q*·δ*)`-type average (Eq. 4) that better represents gross-slip
  friction. Machine stiffness is stated as `Ks=0.0132 N/m` (§3.2.2 and Nomenclature) —
  transcribed as printed; this value seems dimensionally very soft for a hydraulic-rig
  fixture and is plausibly a unit typo in the original (e.g. intended N/µm), but it only
  feeds a fretting-loop compliance correction (Eq. 11, FEM-vs-experiment loop-shape
  comparison in §3.2.2), not the wear-rate model itself, so it was not chased further.
- **Friction result used throughout the rest of the paper**: `µe` is essentially
  **constant, 0.7±0.04, across every loading condition** (N, p, δg, f swept
  independently, Fig. 10) — this constancy is exactly what makes the Archard and
  friction-energy approaches equivalent (`K=µ·α`, Eq. 9) and lets the whole paper proceed
  using the energy (α) formulation alone.
- **Wear measurement**: post-test 3D optical/stylus surface profilometry on both top and
  bottom samples, after a 20-minute ultrasonic ethanol bath to remove loose, non-adhering
  oxide debris. A reference plane (intact surface) splits each scar into `V-` (material
  removed, below the plane) and `V+` (adhesive material transfer, above the plane); net
  wear per sample `Vt = V- − V+` (Eq. 5); total wear volume `V = Vt(top)+Vt(bottom)`
  (Eq. 6). An averaged 2D wear profile (`2Dave`, over the transverse length L=5 mm) is
  also derived for qualitative morphology comparison across conditions (not used for
  volume).
- **Why pressure is treated as quasi-constant — an FEM cross-check, not just an
  assumption** (§2.6, using the Arnaud et al. 2017 Matlab-Python-Abaqus wear-simulation
  code, ref. [21]): the flat-on-flat contact has a known drawback — stress concentration
  at the free borders gives a discontinuous pressure distribution. The FEM shows this
  edge concentration is transient: at the reference condition, edge pressure starts ~4×
  the central value but **decays to ~2× within 500 cycles** as wear "hones" (rounds) the
  borders; away from the edges, the pressure is homogeneous and stays at the nominal
  ~100 MPa throughout. The reported **peak transient edge pressure over the whole test
  matrix is ~468 MPa** (still below the 950 MPa yield stress) — and the authors state
  explicitly that they capped their own pressure sweep at **p≤175 MPa specifically so
  that even this edge transient stays elastic** (border yield was found to occur above a
  mean pressure of ~175 MPa in their FEM). This transient-edge-pressure ceiling (≈468 MPa
  ≈ 0.468 GPa at most) is the highest pressure number anywhere in this paper, and it is
  still **below the bolt-relevant 0.5–1.5 GPa window** (see Loading matrix below).

## Materials

Both bodies: **35NCD16** (French/AFNOR steel designation — the same alloy as
"34NiCrMo16" in the EN designation used by the sibling `baydoun_arxiv`/`arnaud2021ti`
papers from the same group), a homogeneous interface, tempered-martensitic low-alloy
steel described as having good mechanical properties in any direction, high strength and
hardenability, and good dimensional stability.

**Table 1** (mechanical properties, "obtained from the documentation of material
supplier"):

| E (GPa) | ν | σy 0.2% (MPa) | σu (MPa) |
|---|---|---|---|
| 205 | 0.3 | 950 | 1130 |

(Identical numbers to the `baydoun_arxiv` companion note's Table 1 — same steel, same
supplier source, consistent across both papers.)

**No hardness (HV/Vickers/Rockwell) value is reported anywhere in this paper** (confirmed
by a full-text search for "hardness", "Vickers", "HV", "Rockwell" — zero hits besides the
"E (GPa)" units string). This matches the companion `baydoun_arxiv` note's identical
finding for the same material. This absence is directly relevant to the V2 mapping below
— it blocks a clean α→K/H conversion from this source alone.

## Loading matrix

**Reference test condition "O"** (repeated 3×): **N=20 000 cycles, p=100 MPa,
δg=±100 µm, f=1 Hz**, S=25 mm² (fixed contact area, all tests).

One-parameter-at-a-time sweeps around O ("blue dot" tests in the paper's own Fig. 7,
used for model calibration):

| Parameter | Levels tested | Extrema labels |
|---|---|---|
| Number of cycles, N | 5 000, 10 000, 15 000, 20 000(O), 30 000, 40 000 | G=5 000, H=40 000 |
| Contact pressure, p | **10, 25, 50, 75, 100(O), 125, 150, 175 MPa** | A=10 MPa, B=175 MPa |
| Sliding amplitude, δg | ±25, ±50, ±75, ±100(O), ±125, ±150, ±175, ±200 µm | C=±25 µm, D=±200 µm |
| Frequency, f | 0.5, 1(O), 2, 5, 6, 8, 10 Hz | E=0.5 Hz, F=10 Hz |

**Contact pressure — explicit units and the GPa question (decisive check requested)**:
the pressure sweep is **10–175 MPa = 0.010–0.175 GPa**, confirmed independently three
ways: (1) the running text states it verbatim ("p=10, 25, 50, 75, 100, 125, 150, and
175 MPa"); (2) the Fig. 12 caption repeats the identical list with units "MPa"; (3) direct
visual inspection of Figs. 12a/12b/12c (rendered at ≥300 dpi, see
`figures/baydoun2019wear_fig12_abc.png` and the zoomed crops) shows axis labels reading
**"contact pressure, p (MPa)"** with tick marks 0–200, matching the digitized x-values
exactly. **This pressure range does NOT reach the 0.5–1.5 GPa bolt-relevant window** —
it sits roughly one to two orders of magnitude below it. Even the FEM-computed transient
edge-pressure ceiling (~468 MPa ≈ 0.468 GPa, see Rig section) stays under it. This is a
deliberate design choice by the authors (flat-on-flat, low/moderate quasi-constant
pressure), not an oversight.

**Sliding amplitude**: ±25 to ±200 µm, 25 µm steps (8 levels — see Digitization caveats
for a discrepancy between the paper's caption text, which omits ±150 µm, and the actual
figures, which plot it).

**Frequency**: 0.5–10 Hz (7 levels: 0.5, 1, 2, 5, 6, 8, 10).

**Cycle counts**: 5 000–40 000 for the dedicated N-sweep; the reference and every other
single-parameter sweep runs at the fixed N=20 000.

**Validation set** ("black squares/rhombuses" in Fig. 7, two parameters changed at once
relative to O, plus a contact-size sweep S=25–100 mm² at p=50 MPa): **45 tests total**
(Fig. 19/20), used to validate — not calibrate — the model, entirely outside the
one-parameter-at-a-time calibration domain.

**Reduced-model identification** (§3.5.2): only **9 test conditions / 11 experiments**
(O × 3 repeats, plus the 8 single extrema A–H) are needed to re-derive the exponents and
α within 3.46% of the full calibration, and within a comparable (actually slightly
better) validation error against the same 45-test set (27.87% vs. 30.53% relative
standard deviation) — a practical "minimum experimental sequence" result directly
relevant to this repo's own calibration-economy goals.

## Wear law — weighted friction-energy formulation

**Baseline relations**: energy-wear approach `V = α·ΣEd` (Eq. 7); Archard approach
`V = K·ΣW` with Archard loading factor `ΣW = P·δg` (Eq. 2, Eq. 8); when the friction
coefficient is constant (confirmed here, `µe≈0.7` across the board), the two are
equivalent, `K = µ·α` (Eq. 9) — the paper proceeds with the energy (α) formulation for
simplicity.

**Energy wear rate (α), mm³/J** — the headline constant, computed as the slope of total
wear volume V vs. cumulated dissipated energy ΣEd:
- **Global fit** (from the N-sweep, Fig. 11b): **α_ref = 4.383×10⁻⁵ mm³/J**.
- **Reduced-model fit** (average of the 3 reference-condition repeats only, used e.g. as
  the FEM's own input in §2.6): **α_ref,r = 4.231×10⁻⁵ mm³/J**. Difference between the
  two: <3.46 %.
- **Archard-equivalent global reference coefficient**: **K_ref = 3.030×10⁻⁵ mm³/J**
  (consistent with `K=µ·α`: 0.7×4.383e-5 ≈ 3.07e-5, close to the stated value).

**Weighted friction-energy model** (Eqs. 14–15) — a multiplicative power law over all
four loading variables, referenced to condition O:

```
V_pred = α_ref · { (N/N_ref)^nN · (p/p_ref)^np · (δg/δg,ref)^nδg · (f/f_ref)^nf } · ΣEd
   N_ref = 20 000 cycles, p_ref = 100 MPa, δg,ref = ±100 µm, f_ref = 1 Hz, S = 25 mm² (fixed)
```

Exponents (each fit separately, minimizing the standard deviation between V and V_pred
over its own single-parameter sweep, Eq. 16, Vref=0.606 mm³):

| Fit | nN (cycles) | np (pressure) | nδg (amplitude) | nf (frequency) | α used |
|---|---:|---:|---:|---:|---|
| **Global** (Fig. 17, all sweep data) | 0 | **0.6** | **0.7** | **−0.3** | 4.383e-5 |
| **Reduced** (§3.5.2, extrema only) | 0 | **0.5** | **0.8** | **−0.3** | 4.231e-5 |

Interpretation (authors' own words): wear volume is **linear** in cycle count (nN=0 —
steady-state wear rate, no additional running-in/end-of-life term captured), nonlinearly
**proportional** to pressure and sliding amplitude, and nonlinearly **inversely**
proportional to frequency.

**Model validation**: the full weighted-energy model (Eq. 17) fits the calibration data
at **R²=93%** (Fig. 18a); its Archard-equivalent weighted form (Eq. 19, K_ref=3.030e-5)
at **R²=94%** (Fig. 18b) — both markedly better than either (a) the plain, unweighted
energy approach (`V=4.41×10⁻⁵·ΣEd`, **R²=0.66**, Fig. 15 — "no longer reliable" per the
authors) or (b) a friction-power-density formulation `α(φ*)=K·exp(n·φ*)` analogous to
Fouvry's Ti-6Al-4V approach (only ~9-point R² improvement over the plain energy
approach, still dispersive at higher p/δg — §3.4.2, Eq. 12–13). Out-of-domain validation
(the 45-test set, including the S=25–100 mm² contact-size sweep at p=50 MPa):
**R²=0.89** (global-fit parameters, Fig. 19) / **R²=0.91** (reduced-fit parameters,
Fig. 20) — both essentially as good as the in-domain fit, and showing wear volume scales
linearly with contact size S over the tested range (25–100 mm²), i.e. contact size has
only a minor/near-negligible effect on the *rate* within this window (a "stabilized
domain," consistent with Fouvry et al. 2009's prior finding cited in-text).

**Abrasive ↔ adhesive transition — the regime-conditional caveat (central to the V2
mapping)**:
- **Fig. 12c** (energy wear rate α vs. contact pressure) shows a **knee at
  p_th ≈ 125 MPa**: below it, α is roughly flat (~2.5–3.4×10⁻⁵ mm³/J over 25–125 MPa);
  above it, α steepens sharply to 5.7–6.7×10⁻⁵ mm³/J at 150–175 MPa.
- **Fig. 13c** (energy wear rate α vs. sliding amplitude) shows an analogous **knee at
  δg_th ≈ 125 µm**: a shallow dip/plateau below it (~2.3–4.4×10⁻⁵ mm³/J over 25–100 µm),
  then a steep climb above it (5–7×10⁻⁵ mm³/J at 150–200 µm).
- The authors invoke **two competing physical mechanisms**, and are explicit that
  neither alone explains the full picture: (1) **contact-oxygenation (IOC) theory** —
  higher pressure/larger amplitude improves debris ejection and/or oxygen access,
  favoring abrasive (high-wear) behavior; by itself this would predict a *monotonic*
  trend, not a knee; (2) **elastic-to-plastic shakedown** (Johnson-type
  pressure-friction shakedown maps) — above a threshold pressure, asperity response
  shifts from elastic to plastic shakedown, accumulating plastic strain and
  *independently* accelerating wear. The paper states plainly that the oxygenation
  concept **cannot explain** the super-threshold acceleration in α, and leans on the
  shakedown/third-body hypothesis for that specific regime change — i.e., **a single
  fitted power-law exponent is a regression across a wear-mode/mechanism transition**,
  not one continuous physical law. This is the same structural caveat the sibling
  `fouvry2017ti.md` note flags for its own n=−0.25 (there: oxidative U-shape ↔ adhesive
  W-shape) — same lab, same "regime-conditional, not universal" discipline required.
- **3D profiles + EDX (Tables 3–4 in the paper, not digitized here, see below)**:
  confirm a **mixed abrasive+adhesive regime at every single tested condition** (never
  purely one or the other) — adhesion concentrated near the contact center, abrasion at
  the borders, consistent with the interfacial-oxygen-concentration ("IOC") partition
  concept the sibling `baydoun_arxiv` paper formalizes as `d_O`.

**Wear depth** (§4, Eq. 21–22, secondary finding): a simple explicit formula converts
`(α, ΣEd, S)` into a predicted maximum wear depth `hmax,FEM`, compared against the
experimental `hmax`. Agreement is **poor at low wear degradation** (dominated by
adhesive-transfer noise) and **improves markedly at high wear degradation** (once the
scar has become a homogeneous, transfer-free flat profile) — an explicitly acknowledged
model limitation, not claimed to be resolved.

## Main conclusions

1. FEM confirms the flat-on-flat contact converges to a genuinely flat, quasi-constant
   pressure distribution (away from the free borders) within <500 cycles — the
   "constant pressure" premise for the whole campaign is verified, not just assumed.
2. Wear rate depends on contact pressure, sliding amplitude, and frequency, but is
   **linear** (rate-independent) in cycle count — a single energy-wear-rate constant per
   condition suffices, no additional aging/running-in term is needed at this level.
3. A **weighted (multiplicative power-law) friction-energy formulation** combining all
   four loading variables against one shared reference α gives a reliable prediction
   (R²=93–94% in-domain), validated **outside** the calibration domain — including across
   varying contact sizes (25–100 mm²) — at R²=89–91%.
4. A **reduced experimental strategy** (9 conditions / 11 tests: reference + the 8
   single-parameter extrema) reproduces the full-campaign model almost exactly — a
   concrete "minimum test sequence" precedent.
5. A **mixed abrasive+adhesive wear regime is present at every tested condition**
   (never purely one or the other), explained via contact-oxygenation (IOC, macro-scale
   partition: adhesive center / abrasive border) plus a third-body debris-flow
   equilibrium (explains the cycle-count independence of the rate).
6. The model's **wear-depth** prediction (via FEM, using the same α) is reliable only at
   high wear degradation; low-wear scars are dominated by adhesive-transfer noise the
   current formulation does not capture — flagged by the authors as needing future work.

## Curve inventory

All 8 CSVs listed in the task are present in `digitized_csv/` and were verified against
the source figures (`figures/baydoun2019wear_fig11.png`, `..._fig12_abc.png`,
`..._fig13_abc.png`, `..._fig14_ab.png` and their zoom crops) — none were modified.

| Figure | CSV | x (unit) | y (unit) | # pts |
|---|---|---|---|---|
| Fig. 11a | `baydoun2019wear_fig11a_wearvol_vs_ncycles.csv` | number of cycles, N (cycles) | total wear volume, V (mm³) | 8 |
| Fig. 11b | `baydoun2019wear_fig11b_wearvol_vs_energy.csv` | cumulated dissipated energy, ΣEd (J) | total wear volume, V (mm³) | 8 |
| Fig. 12a | `baydoun2019wear_fig12a_wearvol_vs_pressure.csv` | contact pressure, p (**MPa**) | total wear volume, V (mm³) | 10 |
| Fig. 12c | `baydoun2019wear_fig12c_wearrate_vs_pressure.csv` | contact pressure, p (**MPa**) | energy wear rate, α (mm³/J) — **stored ×10⁻⁵**, i.e. multiply CSV value by 1e-5 for true mm³/J | 8 |
| Fig. 13a | `baydoun2019wear_fig13a_wearvol_vs_amplitude.csv` | sliding amplitude, δg (µm) | total wear volume, V (mm³) | 10 |
| Fig. 13c | `baydoun2019wear_fig13c_wearrate_vs_amplitude.csv` | sliding amplitude, δg (µm) | energy wear rate, α (mm³/J) — **stored ×10⁻⁵** | 9 |
| Fig. 14a | `baydoun2019wear_fig14a_wearvol_vs_frequency.csv` | frequency, f (Hz) | total wear volume, V (mm³) | 9 |
| Fig. 14b | `baydoun2019wear_fig14b_wearrate_vs_frequency.csv` | frequency, f (Hz) | energy wear rate, α (mm³/J) — **stored ×10⁻⁵** | 9 |

Row counts include repeated reference-condition points (up to 3× at the shared O
condition in panels a/b, 2× in the α panels — see Digitization caveats for why panel (c)
consistently shows fewer O-repeats than panels (a)/(b)).

**Not digitized (context/qualitative only, no numeric curves needed)**: Fig. 1
(schematic, not present in this Wear paper — application photos are Fig. 1 in the arXiv
companion, not here — this paper's Fig. 1 is the industrial-application fretting-damage
photo montage), Fig. 2 (sample/contact/rig schematic), Fig. 3 (fretting-cycle/log
schematic), Fig. 4 (3D-profile/2Dave computation schematic), Fig. 5–6 (FEM "wear box"
setup + pressure-distribution-vs-cycles line plot — the latter's headline numbers, ~468
MPa peak edge / ~200 MPa stabilized edge / ~100 MPa center, are already quoted in the Rig
section above), Fig. 7 (test-matrix scatter, not a result curve), Fig. 8 (µ, µe vs. test
duration, log-x — a friction-evolution-stages plot, not wear), Fig. 9 (fretting-cycle
Q–δ and Q–δc loops), Fig. 10 (µe vs. each loading parameter — confirms µe≈0.7±0.04
constant, already stated in text, low digitization value), Fig. 12b/13b (V vs. ΣEd for
pressure/amplitude sweeps — same information as panels a/c combined, redundant), Tables
2–5 (optical/3D/EDX scar images, qualitative), Fig. 15 (plain energy approach parity,
R²=0.66, quoted in text), Fig. 16 (friction-power-density formulation, quoted in text),
Fig. 17 (E% vs. exponent calibration curves — the four exponents are exact numbers
quoted in text, no need to re-digitize the error-minimization curves themselves), Fig.
18 (weighted-energy/weighted-Archard parity, R²=93/94%, quoted in text), Fig. 19/20
(predicted-vs-experimental parity for the 45-test validation set, R²=89/91%, quoted in
text), Fig. 21 (2Dave profile comparisons, qualitative), Fig. 22 (hmax vs hmax,FEM +
Δhmax% parity, discussed qualitatively in Wear-law section).

## V2 mapping

- **α (energy-wear coefficient, mm³/J) ↔ `k_wear_spec` = K/H (§4.42a merge)**: same
  *functional role* (a wear-volume-per-dissipated-friction-energy constant) but **not a
  direct numeric drop-in**. Two separate reasons: (1) this paper reports **no hardness**
  for 35NCD16, so α cannot be converted into an actual K/H ratio without sourcing H
  externally (out of scope here); (2) this paper's own "K" (Eq. 8–9, K_ref=3.030×10⁻⁵
  mm³/J) is **already a dimensional, work-normalized constant** (mm³/J, same units as
  α, related by `K=µ·α`) — it is **not** the classical dimensionless Archard K that
  `k_wear_spec=K/H [1/Pa]` is built from. Do not literally divide this paper's K_ref by
  an externally-sourced H and call the result `k_wear_spec` — the units would not
  reconcile without re-deriving K_ref from first principles (true sliding distance and
  contact pressure, not the paper's `P·δg` surrogate for ΣW). Treat α_ref/K_ref as a
  **same-family reference magnitude and functional precedent** (both are "wear volume
  per unit of tribological loading," in the same low-carbon/low-alloy steel family BAS
  V2 already targets), not a plug-in value.
- **Pressure exponent (np=0.5–0.6) → candidate provenance for `conform_pressure_exp`/
  `W_conf_ref`'s pressure exponent `n`**: this paper is the round's own flagged "best G2
  anchor," and it is the cleanest same-family exponent available **at low pressure**
  (quasi-constant-pressure-by-design rig, dedicated single-parameter sweep, both a
  global and an independently-reproduced reduced-model exponent agreeing to within
  0.1). However, **it does not itself close the open `W_conf_ref` anchor gap**:
  1. **Pressure range mismatch**: 10–175 MPa (0.01–0.175 GPa) is one to two orders of
     magnitude below the ~0.5–1.5 GPa bolt-relevant window already scoped in
     `MODEL_LEGITIMACY.md` §4.9 / `CLAUDE.md` item 11(a) (which explicitly calls for a
     dedicated ~1.2 GPa fretting anchor experiment measuring `n` — still open,
     "Fase 3 tentou ancorar e FALHOU... experimento de âncora spec'd: fretting ~1.2 GPa
     medindo n"). Even this paper's own FEM-predicted transient edge-pressure ceiling
     (~468 MPa) stays below that window.
  2. **Sign/mechanism mismatch with the other Fouvry-lab exponent already in this
     library**: `fouvry2017ti`'s n=−0.25 describes energy wear rate *decreasing* with
     rising friction *power density* φ* (W/mm², pressure×velocity combined); this
     paper's np=+0.5–0.6 describes wear volume *increasing* with rising raw pressure p
     (MPa) at fixed velocity/frequency. These are not the same quantity, and their
     opposite signs should **not** be read as contradictory or averaged — they measure
     different physical couplings (power-density-driven wear-mode switch vs.
     pressure-driven wear-volume magnitude at fixed loading rate).
  3. **Regime-conditional, per the paper's own analysis** (see Wear-law section): np is
     fit *across* an abrasive→adhesive-plus-plastic-shakedown transition with an
     explicit knee at p_th≈125 MPa — not one smooth mechanism.
  - **Bottom line**: use this paper as a **shape/family precedent** (a positive,
    sub-linear-to-linear pressure exponent on wear volume is physically legitimate and
    independently observed in this exact "Fouvry flat-on-flat, low-alloy steel"
    lineage), and as the natural low-pressure reference point when designing the
    still-open high-pressure (~1.2 GPa) anchor experiment — **not** as a number to plug
    directly into `conform_pressure_exp`.
- **Amplitude exponent (nδg=0.7–0.8)**: no direct BAS V2 counterpart currently uses a
  sliding-amplitude exponent on a wear coefficient (V2's transverse wear mechanism uses
  slip distance linearly via Archard-type accumulation, not a separate power-law
  amplitude correction) — flagged here only as a same-family reference magnitude,
  should a future amplitude-nonlinearity mechanism be justified by data.
- **Frequency exponent (nf=−0.3)**: same family/shape as other Fouvry-lab fretting
  results (mild inverse power law); no current BAS V2 mechanism has an explicit
  frequency exponent on wear rate — reference precedent only.
- **Regime caveat (repeat, load-bearing)**: both np and nδg are fit across a
  wear-mode/mechanism transition (abrasive↔adhesive↔plastic-shakedown), explicitly
  acknowledged as such by the authors. Any BAS V2 use of these exponents should be
  logged with the same "shape exists, magnitude/regime is pair-and-condition-
  conditional" discipline already applied to `C_creep` (§4.7) and `emb_depth` (§1.3a) in
  this repo, and to `fouvry2017ti`'s own n=−0.25.
- **Rig-methodology provenance value (independent of any single number)**: this paper's
  FEM-validated demonstration that a flat-on-flat design achieves genuinely
  quasi-constant contact pressure within <500 cycles corroborates the same
  "constant-pressure" assumption used by, and already cited across, this whole
  Baydoun/Fouvry/Arnaud paper family in this library.
- **Materials note**: 35NCD16 (=34NiCrMo16) elastic/strength properties (E=205 GPa,
  ν=0.3, σy=950 MPa, σu=1130 MPa) are available if a future case study needs this
  specific low-alloy steel; no current BAS V2 validation case uses it. No hardness is
  available from this source specifically.

## Digitization caveats

- **Fig. 12c has only 7 distinct pressure levels (25–175 MPa), one fewer than Figs.
  12a/12b (10–175 MPa)** — confirmed by direct visual inspection of a ≥300 dpi crop
  (`figures/baydoun2019wear_fig12c_left.png`): the "A" extremum label sits directly
  above the **p=25 MPa** marker in panel (c), whereas in panel (a) the same "A" label
  sits above the **p=10 MPa** marker. The source figure itself never plots a p=10 MPa
  energy-wear-rate point (its wear volume was measurable in panel (a), V=0.08 mm³, but
  no corresponding α point appears in panel (c) — plausibly because the near-zero wear
  made that particular ratio too noisy to plot reliably, though the paper does not say
  so explicitly). **The existing CSV (8 rows: 7 unique pressures, with p=100 doubled)
  correctly reflects the published figure as-is — this is a source-figure quirk, not a
  digitization error, and no fix was made.**
- **Figs. 13a/13c (sliding-amplitude sweep) both correctly plot 8 distinct amplitudes,
  including δg=150 µm** — confirmed by direct visual inspection of ≥300 dpi crops
  (`figures/baydoun2019wear_fig13a_zoom.png`, `..._fig13c_zoom.png`): panel (a) shows
  clearly separated markers at x=25, 50, 75, 100(×3 cluster), 125, **150**, 175, 200 —
  and panel (c) shows the corresponding trend (with 2 reps at 100). This **contradicts**
  the paper's own caption text, which lists only 7 values twice (identically, in-text
  §3.3.3 and in the Fig. 13 caption): "δg=±25, ±50, ±75, ±100, ±125, ±175, and ±200 µm"
  — silently omitting "±150". Given the figure itself unambiguously plots a δg=150 µm
  point (and the exactly analogous Fig. 12/pressure caption correctly lists all 8 of
  its own values in the same sentence structure), this is judged a **paper-source
  transcription typo** (dropped "±150,"), not a digitization error. **The existing
  CSVs (10 rows for 13a, 9 rows for 13c) are correct as digitized against the actual
  plotted points and were left unmodified.**
- **Two citation/labeling inconsistencies noticed in the source PDF itself (not
  introduced by us)**: (a) Table 1's in-text citation for the material-supplier
  documentation reads "[19]", but reference [19] in the bibliography is a Fouvry
  fatigue paper (*Int. J. Fatigue* 2014) unrelated to steel supply — the actual steel
  catalogue is reference [18] ("C.D.S. Qualité — catalogue, Lugand Aciers, 2018"),
  suggesting an off-by-one citation-numbering slip in the original paper; (b) the FEM
  section (§2.6) uses α=4.231×10⁻⁵ mm³/J as its simulation input, which (as presented
  later in the paper) is actually the **reduced-model** value α_ref,r (§3.5.2), not the
  paper's headline **global** α_ref=4.383×10⁻⁵ mm³/J (§3.4.3) introduced afterward —
  both values are genuine and independently confirmed elsewhere in the paper, this is
  only a presentation-order note, not a numerical error.
- **Cross-validation performed on all 8 CSVs, all consistent**: (1) Fig. 11a/11b — the
  digitized slope reproduces the stated α_ref (e.g. the O-condition triplet sits at
  ΣEd≈13 800–14 800 J, V≈0.46–0.63 mm³, giving α≈4.0–4.3×10⁻⁵ mm³/J, matching); (2) Fig.
  12a's own printed quadratic trendline ("y=3E-05x²+0.002x") evaluated at x=175 gives
  V≈1.27 mm³ vs. the digitized 1.33 mm³ (within marker-size tolerance); (3) every
  pressure/amplitude/frequency x-value across all 6 relevant CSVs matches the paper's
  explicitly stated sweep list to the exact MPa/µm/Hz number (not an approximate pixel
  read) — high confidence specifically in the x-axes; y-values are genuine
  marker-centroid reads off ≥300 dpi crops, typical precision ≈±0.02–0.05 mm³ (volume
  panels) and ≈±0.1–0.2 (×10⁻⁵ mm³/J units, wear-rate panels), consistent with marker
  size at this resolution.
- **Unit-scale reminder** (repeated from the Curve inventory table because it is easy to
  miss): the y-column in `..._fig12c_...`, `..._fig13c_...`, and `..._fig14b_...` stores
  the **raw axis value as printed** (e.g. "3.3"), which represents the true energy wear
  rate **only after multiplying by 1e-5** (i.e. 3.3 → 3.3×10⁻⁵ mm³/J). No unit
  conversion was pre-applied inside the CSVs.
- **No CSV was modified.** All 8 were read, checked against the source figures
  (including two apparent discrepancies vs. the paper's own caption text, both resolved
  in favor of the figures as documented above), and confirmed accurate as originally
  digitized.
