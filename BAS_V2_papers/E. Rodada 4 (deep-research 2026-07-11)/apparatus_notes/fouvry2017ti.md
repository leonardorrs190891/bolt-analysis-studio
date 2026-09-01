# Fouvry, Arnaud, Mignot & Neubauer 2017 (Tribology International) — Contact size, frequency and cyclic normal force effects on Ti-6Al-4V fretting wear

## Citation + DOI

S. Fouvry, P. Arnaud, A. Mignot, P. Neubauer, "Contact size, frequency and cyclic normal
force effects on Ti–6Al–4V fretting wear processes: An approach combining friction power
and contact oxygenation," *Tribology International* 113 (2017) 460–473.
DOI: [10.1016/j.triboint.2016.12.049](http://dx.doi.org/10.1016/j.triboint.2016.12.049).

Laboratoire de Tribologie et Dynamiques des Systèmes (LTDS), UMR 5513, Ecole Centrale de
Lyon, France. Same laboratory/rig lineage as the in-library companion paper "Effect of
variable normal force and frequency on fretting wear of Ti-6Al-4V" (van Peteghem & Fouvry,
*Wear* 2011, ref. [15] of this paper) — that 2011 paper is the earlier/narrower study this
2017 paper extends with the contact-size ("R") sweep and the full friction-power-density
formalism (§4.2 here). Several other Fouvry-group fretting-wear-energy papers are also
present in this same paper batch (2007 energy-wear-capacity concept; Arnaud-Fouvry 2021;
Baydoun-Fouvry 2019/2021) — this note covers **only** the 2017 Ti-6Al-4V paper listed above.

## Gap tag(s)

- **G2 (primary)** — dependence of fretting/tribological wear rate on contact pressure and
  friction power density. This is the calibration library's target gap for a **pressure
  exponent in BAS V2's conformance/wear-gate formulation** (`W_conf_ref`, `conform_pressure_exp`
  = `n`) and for the **energy-wear coefficient** analogous to the merged `k_wear_spec` = K/H
  parameter (§4.42a `MODEL_LEGITIMACY.md`). This paper reports an explicit power law
  `α = K·(φ*)^n` with **both K and n given numerically and confirmed identically on two
  separate figures** (Figs. 11 and 15) — the cleanest single explicit exponent value in this
  paper's own right. Per the round's own indexing
  (`Models/CALIBRATION_AND_VALIDATION/curve_library/DEEP_RESEARCH_REPORT_R4.md`, row 10),
  **Baydoun & Fouvry 2019 is flagged as the "best anchor" for G2** (quasi-constant-pressure
  flat-on-flat design, isolating the pressure/amplitude/frequency effects more cleanly); this
  2017 paper is listed alongside Fouvry 2007 and van Peteghem-Fouvry 2011 as one of the
  "**G2 leads**" — i.e. a **complement**, not the primary anchor: its distinct contribution is
  the **friction-power-density exponent from an independent loading design** (Hertzian
  cylinder/plane, contact-size + frequency + cyclic-normal-force sweep, rather than
  flat-on-flat quasi-constant pressure).
- **G8 (secondary, titanium)** — this is a **Ti-6Al-4V/Ti-6Al-4V** dry sliding pair. It is a
  candidate anchor if/when a titanium-alloy bolted-joint pair needs its own creep/wear
  constant (paralleling the existing 304SS creep anchor, `New_Theory/creep_anchor.json`,
  §4.7 `MODEL_LEGITIMACY.md`) — **not** a substitute for the library's existing steel or
  aluminium pairs (repo principle: "constants are per-pair, forms transfer").
- **Explicitly NOT a bolt self-loosening paper.** There is **no preload, no bolt, no
  F/F0-vs-cycle curve of any kind** in this source. It is a pure fretting-wear tribology
  study (cylinder/plane coupon rig). Its only value to BAS V2 is the wear-law **functional
  form + coefficients + regime caveat**, not a validation curve.

## Rig / apparatus

- **Test system**: fretting wear rig adapted on an **MTS hydraulic machine**, developed at
  LTDS (same apparatus family as van Peteghem & Fouvry 2011). **Two independent
  servo-hydraulic actuators**: one controls tangential displacement (δ), the other controls
  normal force (P) **independently and simultaneously** — this is what allows the paper's
  novel "cyclic/variable normal force" tests (P oscillating in phase with δ, not just a
  constant clamping force), a rig capability most fretting/fatigue rigs do not have.
- **Contact configuration**: Ti-6Al-4V **cylinder-on-plane** (line contact, Hertzian
  cylindrical). Lateral width `L` is adjusted per tested radius `R` to maintain plane-strain
  conditions (so `L` co-varies with `R` in the test matrix — see Appendix A table).
- **Measurement chain**: tangential displacement δ via extensometer; tangential force Q and
  normal force P via two load sensors → the (Q–δ) fretting hysteresis loop directly gives
  dissipated friction energy `Ed` (loop area) each cycle; sliding amplitude `δ*g` = residual
  displacement at Q=0; sliding stroke `Δg = 2·δ*g`. A companion (Q/P–δ) "friction loop" is
  also plotted to visualize friction behaviour when RP<1 (P not constant during the cycle).
- **Wear measurement**: post-test **3D surface profilometry** on both plane and cylinder scars
  (after 30 min ultrasonic cleaning in ethanol to remove loose debris) → wear volumes `Vp`,
  `Vc`; total `V = Vp+Vc`. An **equivalent 2D profile ("2Deq")** is derived by averaging the 3D
  scan over the lateral width `L` and summing plane+cylinder — used purely to characterize
  scar **morphology** (the U-shape vs W-shape classification), not volume.
- **Chemical/structural analysis** (two representative extreme scars only: U-shape at
  f=0.11 Hz/RP=0.1, and W-shape at f=3 Hz/RP=1): SEM+EDX surface & cross-section (oxygen
  mapping, ~10 µm oxide layer in U-shape vs 50–100 µm metal-transfer/TTS structures in
  W-shape center) and XPS (TiO2/TiOxNy oxide-nitride in U-shape and W-shape borders vs
  almost pure **TiN nitride** in the W-shape's inner transfer zone — an unexpected
  room-temperature "nitriding" process).

## Materials

- Both cylinder and plane: **Ti-6Al-4V** (α/β titanium alloy), water-quenched from the α–β
  domain (below β-transus) + annealed at 700 °C. Both surfaces polished to **Ra = 0.1 µm**.
- Mechanical properties (paper's Table 1, cited from ref. [15]):
  - Elastic modulus E = 119 GPa
  - Poisson's ratio ν = 0.29
  - Yield stress = 970 MPa
  - Vickers hardness HV0.3 = 360
  - Density = 4.4 g/cm³

## Loading matrix

All tests: **fixed sliding amplitude** `δ*g = ±75 µm` (stroke `Δg = 150 µm`, gross-slip
fretting regime); imposed displacement amplitude `δ*` adjusted between ±120 and ±125 µm
(contact-stiffness-dependent) to hold that target constant. Reference/key condition:
R=80 mm, Pmax=1066 N/mm, RP=1, f=5 Hz, N=5000 cy → `pmax`=525 MPa Hertzian pressure,
Hertzian half-width `aH`=1.29 mm.

| Series | Fixed | Swept | Levels | N (cycles) |
|---|---|---|---|---|
| **R** (contact size) | RP=1, f=5 Hz; Pmax adjusted to hold `pmax`=525 MPa | R (mm) | 10, 20, 40, 80 (Pmax=133/267/533/1066 N/mm resp.) | 5000 |
| **P** (contact pressure) | R=80 mm, RP=1, f=5 Hz | Pmax (N/mm) | 67, 133, 267, 533, 1066 → `pmax`=131/186/263/371/525 MPa | 5000 |
| **f** (frequency) | R=80 mm, Pmax=1066 N/mm, RP=1 | f (Hz) | 0.05, 0.11, 0.5, 1, 2, 3, 4, 5 | 5000 |
| **RP** (cyclic normal-force ratio) | R=80 mm, Pmax=1066 N/mm, f=3 Hz | RP=Pmin/Pmax | 0.10, 0.25, 0.50, 0.75, 1.00 | 5000 |
| **RP–f** (fretting map, crossed) | R=80 mm, Pmax=1066 N/mm | RP × f | RP∈{0.10,0.25,0.50,0.75,1.00} × f∈{0.11,1,3,5 Hz} (not fully crossed) | 5000 and 10000 |

**Contact pressure range explored overall: `pmax` (Hertzian max) ≈ 131–525 MPa (0.131–0.525
GPa)** — a moderate, sub-GPa range, entirely below the ~1.2 GPa anchor-experiment pressure
already scoped in `MODEL_LEGITIMACY.md` §4.9 (see V2 mapping caveat below). Friction
coefficient `μ = Qmax/Pmax` is remarkably **constant at ≈0.6–0.65 across every single
series** (R, P, f, RP) — none of contact size, pressure, frequency, or normal-force
fluctuation measurably changes friction under gross slip; only the **wear rate** and **scar
morphology** respond to these variables.

## Wear law

**1. Baseline energy-wear framework** (equivalent to Archard's law when µ is constant,
`α = µ·K_Archard`): individual energy wear rate `α(i) = V(i)/ΣEd(i)` [mm³/J] per test;
aggregate `V = α·ΣEd` assuming one constant α — **shown by this paper to fail** in general.

**2. Bimodal wear rate by scar morphology** (Eq. 11/12, Fig. 10 — values below are the
**figure-annotated regression values**, since the running-text printing of these same
numbers is corrupted, see Digitization caveats):
- U-shape (abrasive) wear: `V = α_U·ΣEd`, **α_U = 3.55×10⁻⁴ mm³/J (R²=0.92)**
- W-shape (adhesive) wear: `V = α_W·ΣEd`, **α_W = 1.16×10⁻⁴ mm³/J (R²=0.82)**
- U-to-W wear-rate ratio: **K_α,U-W = α_U/α_W ≈ 3.06 ≈ 3** — abrasive U-shape wear is ~3×
  faster than adhesive W-shape wear at the *same* accumulated friction energy. A single
  constant energy-wear coefficient cannot capture the Ti-6Al-4V response.

**3. Friction power density formulation (the core deliverable, Eq. 13–16):**

```
φ* = (ΣEd / (N·Sf)) × f      [W/mm²]   (friction power density; Sf = final/worn contact area)
α  = K · (φ*)^n                        (energy wear rate power law)
```

- **n = −0.25** — the exponent (energy wear rate *decreases* with increasing friction power
  density). Confirmed **identically** by explicit chart annotation on both Fig. 11 and
  Fig. 15 ("n=-0.25").
- **K = α_ref = 1.10×10⁻⁴ mm³/J** — the energy-wear coefficient at φ*=1 W/mm². Confirmed
  **identically** by explicit chart annotation on both Fig. 11 and Fig. 15 ("K=1.10⁻⁴").
- **U-to-W transition threshold: φ*_th ≈ 0.09 W/mm² (90 mW/mm²)**, confirmed by explicit
  annotation on Fig. 11 ("φth*=90mW/mm²").
- This power law was fit **only on iso-contact-size data** (R=80 mm, Pmax=1066 N/mm fixed:
  the "f" series + "f-RP" fretting-map series, 33 usable (φ*, α) points). **Our own
  independent log-log linear regression over those same 33 points** (script-computed from
  the Appendix A table, not from pixel-reading the figure) gives **n = −0.243, K = 9.85×10⁻⁵
  mm³/J, R² = 0.735** — close to, but not identical to, the paper's stated fit (n matches
  almost exactly; K is ≈10% lower). R²=0.735 confirms the "wide scatter" the paper itself
  describes; the discrepancy is plausibly due to a different point-weighting/selection in
  the original regression, not a transcription error (see Digitization caveats for the
  full cross-check against Appendix A).
- Applied to **non-iso-contact-size data** (R-series, P-series — contact size itself
  varying), the same power law shows "wider scatter" (paper's own words) but the general
  trend still holds "surprisingly" well for wear-volume *prediction* purposes (Fig. 16),
  even though the U-to-W *transition* threshold itself shifts with contact size (Fig. 15
  discussion, §4.4).

**4. Frequency dependence** (secondary; iso-contact, RP=1 fixed): `V = V0·exp(k·f)`,
**V0 = 2.6 mm³, k = −0.28 (R² = 0.96)** — figure-annotated on Fig. 7 (the running text
prints "k=−2.8", a decimal-point artifact, see caveats). Wear rate increases **~3.5×** when
frequency drops from 5 Hz to 0.1 Hz — i.e., for this material/mechanism, **lower test
frequency is the conservative (higher-wear) condition**, contradicting the common assumption
that raising frequency (to cut test time) is conservative. µ stays ~constant (~0.65) across
the whole frequency sweep — the wear-rate change is a pure regime-switch effect, not a
friction-coefficient effect. U-shape scars for f<0.5 Hz, W-shape for f>2.5 Hz. The paper
recommends f<0.5 Hz for realistic (conservative) low-cycle-fretting predictions relevant to
turbine-blade dovetail start/stop cycling, versus the 5–20 Hz typically used in LCF
aeronautical test practice to cut cost.

**5. Normal-force-ratio (RP) dependence** (secondary): friction energy per cycle scales
linearly with RP: `Ed/Ed(1) = KRP·RP + BRP`, **KRP=0.65, BRP=0.35** (Ed(1) = energy at RP=1).
Confirmed exactly by our own computation from the Appendix A Rp-series (ratios
0.392/0.503/0.650/0.820/1.000 at RP=0.10/0.25/0.50/0.75/1.00 vs. the linear-fit prediction
0.415/0.513/0.675/0.838/1.000 — same trend, small residual scatter). Combined with the φ*
formulation this predicts the RP–f "fretting map" U-to-W boundary (Eq. 17–23, Fig. 14).

**6. Oxygenation-driven regime mechanism (critical caveat for the exponent's reach):** the
whole U↔W bifurcation is attributed to a "**contact oxygenation**" hypothesis — the
interfacial dioxygen concentration profile across the contact, relative to a threshold.
**Higher** contact pressure, frequency, contact size, and RP (less normal-force fluctuation)
all **reduce** contact oxygenation (compacted asperities block air access; faster/more shear
consumes available oxygen faster; larger contact ⇒ longer diffusion path to center) →
promote the W-shape/adhesive/**lower**-wear regime. The **opposite** conditions promote the
U-shape/abrasive/**higher**-wear regime. **This means the wear-rate-vs-φ* relationship is
fundamentally a regression across a regime *switch* (oxidative ↔ adhesive), not a single
continuous physical mechanism** — the paper's own conclusion is explicit that "more
elaborate wear models, combining contact size and friction power density... are needed,"
i.e., **the authors themselves flag n=-0.25 as regime-conditional/approximate, not a
universal exponent** — exactly the caveat this extraction task asked to capture.

## Main conclusions

- Two distinct fretting-wear regimes: **U-shape** (homogeneous abrasive, thin homogeneous
  oxide debris, high wear rate) vs. **W-shape** (composite: abrasive lateral borders +
  adhesive TTS-metal-transfer center, ~3× lower wear rate).
- Transition U→W is promoted by **increasing** contact pressure, contact size, sliding
  frequency, and normal-force ratio RP — i.e., by anything that reduces cyclic normal-force
  fluctuation or raises friction power dissipation.
- Very low sliding frequency (<0.5 Hz) is the realistic/conservative condition for
  turbine-blade dovetail-type low-frequency start/stop loading; standard 5–20 Hz lab test
  frequencies (used to cut cost) **underestimate** wear for this application — a
  non-conservative testing bias warning.
- U-to-W transition rationalized by a "contact oxygenation" hypothesis, corroborated by XPS
  (TiN nitride formation specifically in the under-oxygenated W-shape transfer zone).
- Wear volume is well predicted by `V = α_ref·(φ*)^n·ΣEd` for iso-contact-size conditions;
  extending to non-iso-contact-size (varying R) works but with wider scatter — contact size
  has a residual/independent effect on the oxygenation transition not fully captured by φ*
  alone.

## Curve inventory

**Source note**: Appendix A of this paper prints the **complete underlying test-condition
and wear-result table** (53 printed rows: R/P/RP/f/RP-f series, columns R, L, Pmax, `pmax_H`,
RP, f, N, scar shape, V, ΣEd, α, φ*; 48 after removing the 5 exact-duplicate RP_f_6–10 rows,
see Digitization caveats — that is the row count of our transcription below). All CSVs below
except the friction-coefficient one are
**transcribed directly from that table** (exact published values), **not pixel-digitized
from the scatter figures** — this is more accurate than reading marker centroids off Figs.
11/15, since it is the literal source data those figures were plotted from. Cross-validated:
recomputing `Ed(1)` from the table gives 1.552 J/cycle vs. the paper's stated "1.54 J/cycle"
(0.8% agreement); the three α values printed directly on Fig. 8 (2.4/2.2/1.5 ×10⁻⁴ mm³/J at
RP=0.10/0.50/1.00, f=3 Hz) match the corresponding Appendix A rows (2.39/2.24/1.52×10⁻⁴)
almost exactly.

| Figure | Series / condition | CSV filename | x (unit) | y (unit) | # pts |
|---|---|---|---|---|---|
| Fig. 11 (+ Fig. 9 map) | Iso-contact (R=80 mm, Pmax=1066 N/mm), **U-shape** points, "f" + "f-RP" series combined | `fouvry2017ti_alpha_vs_phi_Ushape.csv` | friction power density φ* (W/mm²) | energy wear rate α (mm³/J) | 20 |
| Fig. 11 | Iso-contact, **W-shape** points | `fouvry2017ti_alpha_vs_phi_Wshape.csv` | φ* (W/mm²) | α (mm³/J) | 6 |
| Fig. 11 | Iso-contact, **Intermediate** points | `fouvry2017ti_alpha_vs_phi_intermediate.csv` | φ* (W/mm²) | α (mm³/J) | 7 |
| Fig. 11 & 15 | Power-law **model** curve α=K·(φ*)ⁿ, K=1.10e-4, n=-0.25 (paper's figure-confirmed constants, not raw data) | `fouvry2017ti_alpha_vs_phi_powerlaw_fit.csv` | φ* (W/mm²) | α (mm³/J), model | 28 |
| Fig. 15 | Non-iso-contact, **R series** (contact-size sweep, iso-`pmax`=525 MPa) | `fouvry2017ti_alpha_vs_phi_nonisocontact_Rseries.csv` | φ* (W/mm²) | α (mm³/J) | 4 |
| Fig. 15 | Non-iso-contact, **P series** (pressure sweep, R=80 mm fixed) | `fouvry2017ti_alpha_vs_phi_nonisocontact_Pseries.csv` | φ* (W/mm²) | α (mm³/J) | 5 |
| Fig. 7 | Total wear volume vs. frequency (iso-contact, RP=1) | `fouvry2017ti_wear_volume_vs_frequency.csv` | frequency f (Hz) | total wear volume V (mm³) | 8 |
| Fig. 7 | Coefficient of friction vs. frequency (iso-contact, RP=1) | `fouvry2017ti_friction_coefficient_vs_frequency.csv` | frequency f (Hz) | friction coefficient µ (–) | 8 |
| Fig. 13 | Friction-energy ratio vs. normal-force ratio (f=3 Hz) | `fouvry2017ti_ed_ratio_vs_RP.csv` | normal force ratio RP=Pmin/Pmax (–) | Ed/Ed(1) energy ratio (–) | 5 |
| Appendix A | **Full source table** (reference; not a single x,y curve — 13 columns, see header) | `fouvry2017ti_appendixA_test_matrix.csv` | — | — | 48 rows |

**Not digitized (context only)**: Fig. 1 (rig/application schematic), Fig. 2 (loading-parameter
illustration), Figs. 3–6 (fretting loops / scar photos / 2Deq profiles — morphology
illustrations, no new numeric data beyond Appendix A), Fig. 8 (RP fretting-cycle/scar-morphology
illustration; its 3 printed α values are already in Appendix A and used only as a cross-check
above), Fig. 9 (RP–f fretting map illustration — loops/photos/2Deq profiles, qualitative), Fig.
10 (V vs. ΣEd scatter — superseded here by the more directly useful α-vs-φ* form; its two fit
constants are quoted in the Wear law section instead of re-digitized as a curve), Fig. 12/16
(predicted-vs-experimental wear-volume parity plots — model-diagnostic, not new data), Fig.
14 (U-to-W transition map prediction), Figs. 17–20 (SEM/EDX/XPS images + oxygenation schematic),
Fig. 21 (schematic only).

## V2 mapping

- **Pressure/power exponent → `W_conf_ref`/`conform_pressure_exp` (n) provenance**: this
  paper gives the cleanest single-pair, figure-confirmed power-law exponent found for a
  pressure/power-density-dependent wear/friction gate: **n = −0.25** (energy wear rate falls
  as friction power density rises). **Directionally analogous** to a saturating
  conformance gate (more pressure/power ⇒ smaller marginal effect) but the **mechanism is
  unrelated** — Fouvry's n reflects an oxidation-vs-adhesion wear-*mode* switch, not
  asperity conformance/flattening. Treat as **shape precedent** (a power-law
  pressure-dependent multiplier with a negative exponent is physically legitimate and
  independently observed in a real tribological system) — **not** a numeric value to plug
  directly into `W_conf_ref`/`n` without its own dedicated anchor experiment, consistent with
  the existing decision log (`CLAUDE.md` item 11(a): "Fase 3 tentou ancorar e FALHOU... Fouvry
  α ancora `K_archard`, não este [`W_conf_ref`]... experimento de âncora spec'd: fretting
  ~1.2 GPa medindo n"). **This paper's own pressure range tops out at 0.525 GPa** — well
  short of the ~1.2 GPa already scoped for that anchor experiment — so it does **not**
  itself satisfy that open item, but it is the closest same-author-group, same-formalism
  data point available below that pressure, and a natural reference point for designing the
  higher-pressure anchor test.
- **α (energy-wear coefficient, mm³/J) ↔ `k_wear_spec` (K/H, §4.42a merge)**: same
  *tribological role* (a wear-rate-per-dissipated-energy constant) as the merged
  `k_wear_spec` parameter, but **not numerically transferable** — different geometry (fretting
  scar volume on a line contact vs. thread-flank wear depth), different units, and a
  Ti-6Al-4V/Ti-6Al-4V pair not present in the bolt-joint calibration library. Its main
  transferable lesson: **even for one fixed, well-controlled nominal material pair, the
  "constant" wear coefficient swings ~3× (3.55e-4 vs 1.16e-4 mm³/J) between two wear-mode
  regimes** — a concrete, quantified caution against treating any single `k_wear_spec` as
  regime-independent.
- **G8 (titanium pair)**: flagged as a candidate anchor source only for a *future* titanium
  bolted-joint pair, not usable today (no bolt/joint data in this paper at all).
- **Regime caveat (repeat, load-bearing)**: n=-0.25 is fit **only** on iso-contact-size data;
  the underlying mechanism is a **bimodal regime switch** (oxidative U-shape ↔ adhesive
  W-shape), not one smooth physical law, and the paper's own non-iso-contact-size check
  (Fig. 15) shows visibly wider scatter. Any BAS V2 use of this exponent should be logged as
  "shape exists, magnitude/regime is pair- and contact-size-conditional" — same discipline
  already applied to `C_creep` (§4.7) and `emb_depth` (§1.3a) provenance in this repo.

## Digitization caveats

- **The published Appendix A table itself contains two internal errors, confirmed directly
  against the table image (not an OCR/extraction artifact of ours):**
  1. Row 4 of the table is printed with test label "**R_3**" a second time (should read
     `R_4`; R=80 mm, Pmax=1066 N/mm, W-shape). We use `R_4` in our transcription/CSVs. This
     row's values are identical to `P_1` (same physical test reused as the shared endpoint
     of both the R-series and P-series — internally consistent, confirms the transcription).
  2. Row **f_4** (R=80 mm, Pmax=1066 N/mm, RP=1, f=1 Hz, Intermediate scar) prints **V=0.00E+00
     and α=0.00E+00**, which is inconsistent with (a) the smooth trend of its neighboring
     f-series rows, (b) the exponential fit line explicitly plotted through the *other* seven
     f-series points in Fig. 7, and (c) the fact that Fig. 7 itself visibly plots a non-zero
     blue diamond at f=1 Hz. We therefore **excluded this row's table-printed (V=0, α=0)
     from all quantitative CSVs/regressions** (its φ*=3.61e-2 W/mm² value is presumably
     unaffected and was left out of the α-vs-φ* CSVs entirely for this row) and instead used
     an approximate value read directly off the Fig. 7 image for the wear-volume-vs-frequency
     CSV only: **V(f=1 Hz) ≈ 2.25 mm³ (± ~0.1 mm³, visual read, not from the table)**.
  3. Minor: the table's own column header prints "Pmax (**N/m**)"; the correct unit,
     confirmed by every occurrence in the running text and every figure caption ("Pmax=1066
     N/mm" etc.), is **N/mm** (force per unit contact length, standard for a line contact).
     Used N/mm throughout this note and in `fouvry2017ti_appendixA_test_matrix.csv`.
- **Three running-text equations print numbers inconsistent with their own figures' explicit
  annotations — we treat the figure annotations as authoritative** (each was visually
  confirmed on a ≥300 dpi crop, not re-inferred from OCR):
  1. Eq. (15)/§4.2 text: "with `αref` =**51.0 10⁻⁴** mm³/J" — but **Fig. 11 and Fig. 15 both**
     explicitly annotate the same curve as "**K=1.10⁻⁴**" (i.e. K=1.10×10⁻⁴ mm³/J). We use
     1.10×10⁻⁴ (figure value) throughout.
  2. Eq. (11)/§4.1 text: "α_U = **35800 μm³/J**" and "α_W = **11400 μm³/J**" — but **Fig. 10**
     explicitly annotates the two regression lines as "α_U = **3.55×10⁻⁴ mm³/J** (R²=0.92)"
     and "α_W = **1.16×10⁻⁴ mm³/J** (R²=0.82)". We use the figure values throughout (also
     consistent with Appendix A's own α column, which ranges ≈9×10⁻⁵–4.5×10⁻⁴ mm³/J — the
     "μm³/J" reading would be two orders of magnitude too small to match the table).
  3. §3.3.2 text: "V0=2.6 mm³ and **k=−2.8**" — but **Fig. 7** explicitly annotates
     "V = 2.6×exp(**−0.28**×f), R²=0.96". We use k=−0.28 (figure value) throughout; V0=2.6 is
     consistent between text and figure.
  All three follow the identical pattern (a decimal point dropped and digits concatenated,
  e.g. "1.10"→"51.0" reads as a transposition, "3.55"→"35800" and "0.28"→"2.8" read as a
  dropped decimal point) — almost certainly a systematic equation-typesetting/production
  artifact of this particular journal PDF rather than three unrelated errors, but each was
  verified independently against its own figure rather than assumed from the pattern.
- **Our own independent log-log regression does not exactly reproduce the paper's stated
  (K, n)**: fitting all 33 iso-contact (φ*, α) points from Appendix A gives n=−0.243 (paper:
  −0.25, close) and K=9.85×10⁻⁵ mm³/J (paper: 1.10×10⁻⁴, ≈10% lower), R²=0.735. This is
  reported as a transparency check, not a correction — the paper's figure-confirmed values
  are used as the primary reported constants; our regression is offered alongside as an
  independent, reproducible cross-check (script: pure Python, log-space OLS over the
  transcribed Appendix A table) and as a quantified indication of the real scatter in this
  dataset.
- **Coefficient-of-friction-vs-frequency CSV is genuinely pixel-digitized** (the only such
  CSV in this note) — read from a 400 dpi crop of Fig. 7's red-square series, calibrated
  against the shared left/right axis gridlines (left axis 0–4.0 mm³ over 4 gridlines
  exactly co-registered with the right axis 0–0.8 over the same 4 gridlines, i.e. µ =
  0.2×left-axis-equivalent-reading). Typical reading uncertainty ±0.02–0.03 in µ; values
  cluster 0.635–0.70, consistent with the paper's own stated "µ≈0.65, rather stable".
- **RP_f_6 through RP_f_10 in the printed Appendix A are exact duplicates of RP_f_1 through
  RP_f_5** (same R, L, Pmax, `pmax_H`, RP, f=3 Hz, N=5000, scar, V, ΣEd, α, φ* to the last
  printed digit) — an artifact of how the RP–f grid overlaps the standalone RP series at
  f=3 Hz. Excluded the duplicate block from all fits/CSVs to avoid double-weighting those 5
  points.
- General note: because essentially all quantitative CSVs here come from the literal
  Appendix A table rather than pixel-digitization, point counts reflect the paper's actual
  discrete test matrix (4–33 points per series) rather than a fixed pixel-sampling density —
  a deliberate accuracy-over-quantity choice per task instructions.
