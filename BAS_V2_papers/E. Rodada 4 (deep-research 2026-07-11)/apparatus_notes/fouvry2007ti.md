# Fouvry, Paulin & Liskiewicz 2007 (Tribology International) — Application of an energy wear approach to quantify fretting contact durability: introduction of a wear energy capacity concept

## Citation + DOI

S. Fouvry, C. Paulin, T. Liskiewicz, "Application of an energy wear approach to
quantify fretting contact durability: Introduction of a wear energy capacity
concept", *Tribology International* 40 (2007) 1428–1440.
DOI: [10.1016/j.triboint.2007.02.011](https://doi.org/10.1016/j.triboint.2007.02.011)
LTDS, CNRS, École Centrale de Lyon.

**IMPORTANT — this is NOT a bolt self-loosening paper.** It contains **no
preload F/F0-vs-cycle curves** and no bolted-joint hardware at all. It is a
pure fretting-tribology paper (lab coupons: hard coatings and Ti–6Al–4V pins,
LTDS bench rigs). Its value to BAS V2 is purely as a **physics anchor** for the
model's energy-based wear formulation (see V2 mapping below).

## Gap tag (G2) + why

Tagged **G2** in `Models/CALIBRATION_AND_VALIDATION/curve_library/DEEP_RESEARCH_REPORT_R4.md`
(row 10: *"Fouvry leads G2 restantes ... capacidade energética por par, história
de pressão"*). This round's G2 = **"âncora de pressão W_conf_ref/n"** — provenance
for the pressure-dependent conformation gate (`W_conf_ref`, `conform_pressure_exp`)
that the professor adopted 2026-07-04 to resolve the sobretorque falsification
(`MODEL_LEGITIMACY.md` §4.9), but which currently has **no cross-pair anchor**
(Fase 3 anchoring attempt FAILED — no library dataset isolates `W_conf_ref`
itself, per CLAUDE.md item 11(a)). Baydoun & Fouvry 2019 (*Wear* 426–427) is
this round's "best anchor" for the **pressure exponent** (controlled
quasi-constant-pressure sweep). This 2007 paper is a **complement**: it does not
touch pressure-exponent identification directly, but it is the **canonical
reference for the energy-based wear coefficient itself** (α, linking wear
volume linearly to accumulated dissipated friction energy) and it introduces
the **"energy wear capacity" concept (χ)** — a single per-tribocouple constant
that gates when a wear process saturates/fails, structurally analogous (dose ÷
capacity, hyperbolic Nc(dose) master curve) to how `W_conf_ref` gates the
conformation mechanism. It gives BAS V2 (a) a textbook, high-confidence
derivation + values for `α` (candidate provenance for `k_wear_spec = K/H`) and
(b) the conceptual/quantitative template for an "energy capacity" constant
analogous in role to `W_conf_ref`.

## Rig / apparatus

LTDS in-house fretting rigs, built at **micro/meso/macro scale** (normal load
range 0.5–30 000 N across the family), reciprocating motion at constant
imposed velocity, closed chamber with active relative-humidity (RH) control
(50% RH used throughout this paper). Contact geometry is swappable
(cylinder/plane, sphere/plane, plane/plane); this paper uses two:

- **Sphere/plane** — R = 12.7 mm polycrystalline alumina ball vs. hard-coated
  Vanadis-23 (HSS) flat. Used for the non-adhesive-wear (hard coating) study
  (§3.1) and the local wear-depth/energy-capacity study (§4, TiC/alumina and
  TiN/alumina).
- **Cylinder/plane** — R = 10 mm, both bodies Ti–6Al–4V (homogeneous
  interface). Used for the adhesive-wear study (§3.2) and the MoS2-film/Ti64
  energy-capacity case (Fig. 16b).

Per cycle, tangential force Q(t) and displacement δ(t) are recorded and the
closed Q–δ fretting loop is analysed to extract: dissipated energy `Ed`
(hysteresis-loop area = friction work per cycle), sliding amplitude `δg`
(residual displacement at Q=0), tangential force amplitude `Q*`, displacement
amplitude `δ*`. Because the naive friction coefficient (μ=Q*/P) is biased high
by ploughing, an **energy friction coefficient** is used instead:
`μ_e = Ed / (4·P·δg)` (Eq. 1). Only **gross-slip** conditions are studied (no
partial-slip/cracking regime here).

**Wear measurement:** post-test, specimens ultrasonically cleaned (alcohol,
≥10 min) to remove trapped debris, then wear volume `V` extracted from axial +
cross 2D surface profiles. For hard coatings, only the **plane** scar volume is
counted (ball wear + coating transfer to the ball are both negligible). For
Ti–6Al–4V/Ti–6Al–4V, **both** plane (`V_P`) and cylinder (`V_C`) volumes are
measured and **summed** into the total `V_T` used in the analysis.

A separate **FEM "wear box"** (coupled Matlab + Abaqus, iterative remeshing
after each computed cycle, 2D cylinder/plane R=10 mm elastic plane-strain, 5 µm
surface mesh, µ=0.8, arbitrary demo α=1e5 µm³/J, 100× cycle-acceleration
factor) is used only to **validate** the elliptical/flat pressure-distribution
analytical shortcut (Eqs. 14–22) that converts bulk `ΣEd` into the **local**
energy density `ΣEd(0)` at the contact centre — it is not an independent wear
dataset.

## Materials

**Table 1 — non-adhesive-wear tribocouples** (all vs. 12.7 mm alumina ball,
E=370 GPa, ν=0.27, HV=2300 HV0.05, Ra=0.01 µm):

| Coating | E (GPa) | ν | Hardness | Thickness (µm) | Substrate adhesion (N) | Ra (µm) |
|---|---:|---:|---|---:|---:|---:|
| TiC | 510 | 0.2 | 1300 HV0.05 | 1.6 | 45 | 0.2 |
| VC | 460 | — | 2500 HV0.05 | 2.0 | 35 | — |
| TiN | 600 | 0.25 | 2000 HV0.05 | 4.0 | 35 | 0.2 |
| TiCN | 550 | — | 1700 HV0.05 | 2.5 | 40 | — |
| TiC/VC | 580 | 0.2 | 1450 HV0.05 | 2.5 | 35 | 0.2 |
| (TiC/VC)×2 | 580 | — | 2300 HV0.05 | 4.0 | 40 | — |
| Substrate Vanadis 23 | 230 | 0.3 | 64 HRC | – | – | 0.2 |

(All CVD-deposited on high-speed-steel Vanadis 23; blanks are as printed in the
source table, likely omitted-as-repeated rather than genuinely absent.)

**Table 2 — adhesive-wear tribocouple:** Ti–6Al–4V/Ti–6Al–4V — E=119 GPa,
ν=0.33, yield σ_Y02=970 MPa, 41 HRC.

**Fig. 16b tribocouple:** polymer-bonded MoS2 solid-lubricant film on
Ti–6Al–4V (R=10 mm cylinder, same geometry/rig as the Ti64/Ti64 case).

## Loading matrix

| Tribocouple | Normal load | Hertzian pressure | Amplitude δ* | Frequency | Cycles N |
|---|---|---|---|---|---|
| Hard coatings / alumina (§3.1, Fig. 3, Table 3) | P=100 N fixed | **"above 1 GPa"** (paper's explicit statement, initial/undamaged) | ±50, ±100 µm + mixed (50/100)×1/×2/×4 block sequences | 5 Hz | 5000–50 000 |
| TiN(4µm)/alumina (Fig. 16a) | P=50, 100, 150 N | ≈0.8–1.4 GPa (derived: Hertz p₀∝P^(1/3) scaling from the >1 GPa @100N reference — not itself stated) | ±25–100 µm | 5 Hz | up to ≈25 000 |
| Ti–6Al–4V/Ti–6Al–4V (§3.2, Fig. 4–5) | reference P=133 N/mm; swept 66–333 N/mm | **525 MPa max Hertzian @ 133 N/mm (explicit)**; ≈370–830 MPa derived range (Hertz p₀∝√P scaling across 66–333 N/mm) | reference ±75 µm; swept ±25–150 µm; variable 25/75 µm sequences | 5 Hz | reference 25 000; swept 10 000–50 000 |
| MoS2 film / Ti–6Al–4V (Fig. 16b) | P=133 N/mm | ≈525 MPa nominal (same geometry/load as the Ti64/Ti64 reference; not separately stated for the coated case) | ±25–200 µm | 5 Hz | up to ≈480 000 (lubricant film delays failure by ~1–2 orders of magnitude vs. bare metal/hard coatings) |

RH = 50% controlled throughout. All tests are **constant-normal-load,
imposed-displacement, gross-slip** fretting (no clamped-bolt hardware, no
axial preload decay — F/F0 is not a concept in this paper).

## Wear law (energy wear coefficient α, energy capacity χ)

**1. Non-adhesive wear (hard coatings) — plain dissipated-energy law (Eqs. 2–4):**

```
ΣEd = Σ Ed(i)                              (accumulated dissipated friction energy, J)
V = 0                    if ΣEd < Edth
V = α·(ΣEd − Edth)       if ΣEd > Edth      (Edth ≈ 0 for ceramics, no plastic deformation)
⇒ V = α·ΣEd
```

α = **energy wear coefficient** [µm³/J]. For TiC/alumina: **α = 415 µm³/J**,
linear fit R²=0.90 (paper's in-text value + Fig. 3's own on-chart annotation,
both explicit). Table 3 gives α for all 6 hard coatings (see **caveat** below
on this table's printed units):

| Coating | α (µm³/J) | R² |
|---|---:|---:|
| VC | 62.5 | 0.90 |
| TiC/VC | 121.8 | 0.95 |
| (TiC/VC)×2 | 176.4 | 0.97 |
| TiC | 415.1 | 0.92 |
| TiCN | 1764.8 | 0.87 |
| TiN | 6918.6 | 0.93 |

α spans **>2 orders of magnitude** across these 6 hard coatings — it is a
**per-tribocouple constant**, not a universal one (same epistemic status as
`C_creep`/`k_wear_spec` elsewhere in this codebase).

**2. Adhesive wear (Ti64/Ti64) — sliding-reduced energy law (Eqs. 5–7):** plain
`V=αΣEd` FAILS here (Fig. 4: strongly non-linear, amplitude-dependent — debris
is not freely ejected, seizure/transfer consumes part of the dissipated
energy). Fix: weight each cycle's energy by its own sliding amplitude relative
to a reference:
```
Eds(i) = (δg(i)/δg_ref)·Ed(i)     ΣEds = Σ Eds(i)     VT = αs·ΣEds
```
Normalizing by the reference key-point condition (R=10mm, P=133 N/mm, f=5Hz,
N=25 000 cycles) collapses ALL constant- and variable-amplitude tests onto one
line with **αs = 1** by construction (Fig. 5, R²=0.95).

**3. Local wear-depth form (Eqs. 12–24), same non-adhesive tribocouple:**
`h(x) = α·ΣEd(x)` where `ΣEd(0)` is the accumulated dissipated **energy
density** (J/µm²) at the contact centre (derived from bulk `ΣEd` via a
flat-pressure-distribution shortcut, Eq. 22, validated against a 2D FEM
"wear-box" simulation). For TiC/alumina: **αh = 474 µm³/J**, close to the bulk
α=415 µm³/J — paper's own "unified global–local" cross-check (αh≈α).

**4. Energy wear capacity χ (Eqs. 25–28) — the durability constant:**
Below a critical wear depth (**effective worn coating thickness, te**), Fig. 13
shows the phase-I linear `h=αh·ΣEd(0)` regime; above te, **instantaneous
spalling failure** (phase II) is observed. χ is defined as the accumulated
local energy density at that failure point:
```
χ ≈ Σ_{i=0}^{Nc} Ed(i)(0)     ≈ te/α
```
i.e. **the maximum energy density (J per unit area) the interface can absorb
before failure** — a single per-tribocouple durability constant, independent of
contact geometry (in principle). An **Ed–N master curve** (fatigue-S–N
analogy) follows directly:
```
Nc = χ / mean(Ed(Nc)(0))         mean(Ed(Nc)(0)) = ΣEd(Nc)(0)/Nc     (Eqs. 27–28)
```
**χ values identified (all J/µm², via the reverse Ed–N fit):**

| Tribocouple | χ (J/µm²) | Source |
|---|---:|---|
| TiC/alumina | **2.7×10⁻³** (SD 0.34×10⁻³, n=8 conditions, Table 4) | Fig. 13/14 |
| TiN(4µm)/alumina | **0.4×10⁻³** | Fig. 16a |
| MoS2 film/Ti–6Al–4V | **2×10⁻³** | Fig. 16b |

(MoS2's χ ≈5× TiN's despite similar order of magnitude — consistent with the
lubricant film's much longer measured life, up to Nc≈480 000 vs ≈25 000 for
TiN.)

## Main conclusions (paper's own, condensed)

- Non-adhesive (ceramic-type) hard-coating wear is well captured by a **plain**
  friction-energy law (`V=αΣEd`), sequence-independent (single/mixed-amplitude
  blocks all collapse onto the same line, Fig. 3).
- Adhesive metal/metal wear (Ti–Al alloys) needs the **sliding-reduced energy**
  form — debris ejection (not just formation) controls the rate, and larger
  amplitude → more efficient ejection → higher apparent wear-energy
  efficiency.
- A **local, energy-density-based** description (not just bulk volume) is
  required to predict interface durability; the pressure field flattens from
  Hertzian-elliptical to quasi-square as wear progresses (FEM-confirmed), and
  the flat approximation is an excellent shortcut after a very short transient
  (<100 cycles for TiC/alumina).
- Interface durability reduces to **one number per tribocouple**, χ — the
  critical accumulated local energy density before failure — giving a
  fatigue-S–N-style `Nc = χ/mean_Ed` master curve that collapses all
  pressure/amplitude/sequence conditions.
- The global (`α`) and local (`αh`) energy-wear coefficients agree closely for
  TiC/alumina (415 vs 474 µm³/J), supporting a **unified global–local**
  description, at least where third-body effects are minor.

## Curve inventory

All in `digitized_csv/`, prefix `fouvry2007ti_`. Column header is generic `x,y`
in every file — quantities/units documented here, NOT in the CSV.

| Figure/Table → CSV | x quantity (unit) | y quantity (unit) | #pts | Notes |
|---|---|---|---:|---|
| Fig. 3 → `wearvol_vs_energy_TiC.csv` | accumulated dissipated energy ΣEd (J) | wear volume V (**×10⁴ µm³**, i.e. ×1e4 for µm³) | 18 | TiC/alumina; all δ* sequences pooled (paper's point: sequence-invariant) |
| Fig. 4 → `wearvol_vs_energy_Ti64_25kcyc.csv` | ΣEd (J) | normalized wear volume V/V_ref (–) | 4 | Ti64/Ti64, 25 000-cycle series, plain energy (nonlinear — shown to fail) |
| Fig. 4 → `wearvol_vs_energy_Ti64_50kcyc.csv` | ΣEd (J) | V/V_ref (–) | 7 | Ti64/Ti64, 50 000-cycle series |
| Fig. 5 → `wearvol_vs_slidingreducedenergy_Ti64.csv` | normalized ΣEds/ΣEds_ref (–) | normalized V/V_ref (–) | 40 | Ti64/Ti64, all 3 marker families (constant + 2 variable-sequence) pooled — dense overlapping scatter, see caveats |
| Fig. 13 → `weardepth_vs_energydensity_TiC.csv` | ΣEd(0) (**×10⁻² J/µm²**, i.e. ×0.01 for J/µm²) | wear depth h (µm) | 16 | TiC/alumina; last 2 rows = phase-II spalling jump, not phase-I linear trend |
| Table 4 → `Nc_vs_meanenergydensity_TiC_alumina.csv` | fretting endurance Nc (cycles) | mean energy density Ed(Nc)(0) (**×10⁻⁶ J/µm²**) | 8 | **Computed exactly from Table 4's text values** (Eq. 27), not pixel-digitized — reproduces Fig. 14 to within plotting precision (cross-checked visually) |
| Fig. 16a → `Nc_vs_meanenergydensity_TiN_alumina.csv` | Nc (cycles) | mean energy density (**×10⁻⁶ J/µm²**) | 20 | TiN(4µm)/alumina; P=50/100/150N pooled (paper's point: master curve is P-independent); x-axis scale corrected, see caveats |
| Fig. 16b → `Nc_vs_meanenergydensity_MoS2_Ti64.csv` | Nc (cycles) | mean energy density (**×10⁻⁶ J/µm²**) | 10 | MoS2 film/Ti–6Al–4V, δ*=25–200µm sweep |

**8 CSVs total**, 0 curves invented — no F/F0 vs cycle data exists in this paper.

## V2 mapping

**α ↔ `k_wear_spec` (= K/H, [1/Pa]) provenance.** Dimensionally
`α [µm³/J] ≡ [m³/J] ≡ [1/Pa]` exactly the same base units as V2's
`k_wear_spec` (`src/bolt_analysis_studio/numerical/parameter_identifier.py`
`jm_k_wear_spec_param`, bounds [1e-15, 1e-12] 1/Pa, legacy-equivalent default
5e-14). The reconciliation: Fouvry's law is `V=α·Ed` with `Ed≈μ·P·L` (friction
work), while Archard's is `V=(K/H)·P·L` (normal-load×distance, no μ) — so
**k_wear_spec ≈ α·μ_eff**. Using V2's default µ_eff=0.15:

| Coating | α (µm³/J) | α_SI (1/Pa) | k_wear_spec ≈ α·µ (1/Pa) |
|---|---:|---:|---:|
| VC | 62.5 | 6.25e-17 | 9.4e-18 |
| TiC/VC | 121.8 | 1.22e-16 | 1.8e-17 |
| (TiC/VC)×2 | 176.4 | 1.76e-16 | 2.6e-17 |
| TiC | 415.1 | 4.15e-16 | 6.2e-17 |
| TiCN | 1764.8 | 1.76e-15 | 2.6e-16 |
| TiN | 6918.6 | 6.92e-15 | 1.04e-15 |

All 6 sit **at or below** V2's current `k_wear_spec` lower bound (1e-15) —
consistent with these being hard, wear-resistant ceramic coatings vs. a
steel-thread-calibrated default (bolted-joint threads gall/wear far faster than
TiN-on-alumina). Useful as a **low-end anchor/sanity bound** for the registry,
NOT a substitute value — different tribopair entirely (cross-material analogy
only, same caveat status as `C_creep` elsewhere in this codebase). There's
already an unreconciled hook for this exact constant:
`src/bolt_analysis_studio/visualization/loosening_plots.py:585` hardcodes
`alpha_fouvry=3e-8` in a demo `WearParameters(...)` call — units/provenance not
documented there; this note's Table 3 values are the traceable source if that
gets revisited. (Adhesive Ti64/Ti64 αs=1 is normalized-only in this paper — no
absolute µm³/J value is recoverable from Figs. 4–5 alone.)

**χ ↔ energy/pressure capacity like `W_conf_ref`.** χ [J/µm², an **areal**
energy-density capacity] and `W_conf_ref` [J, per
`validation/report_html.py:434`] are **not dimensionally identical** — the
mapping is **structural/conceptual, not a unit substitution**. Both are
"dose ÷ capacity" saturation constants gating a mechanism: Fouvry's
`Nc=χ/mean_Ed(Nc)` (hyperbolic, dose accumulates until failure) mirrors V2's
`conformation_gate = W_conf_ref/(W_conf+W_conf_ref)`
(`dynamic_stiffness_analyzer.py:635`, hyperbolic, dose accumulates until the
gate closes). To make χ commensurate with `W_conf_ref` one would multiply by a
representative contact area (χ·A_contact → J) — not attempted here (would need
a specific per-thread contact-area estimate, out of scope for this extraction).
This paper is best read as the **conceptual precedent** for "one energy-capacity
constant per tribological pair" that motivated `W_conf_ref`'s form, per the
round's own framing (`DEEP_RESEARCH_REPORT_R4.md` row 10: "capacidade
energética por par"), not as a numeric anchor for its value.

## Digitization caveats

- **Table 3 header units are almost certainly mislabeled in the original
  publication.** It prints "Energy wear coefficient α **(10³ µm³/J)**", which
  would make TiC's tabulated 415.1 mean 415,100 µm³/J. This directly
  contradicts (a) the in-text sentence two paragraphs earlier — "we deduced
  α = **415 µm³/J**" (no ×1000) — and (b) Fig. 3's own on-chart annotation
  "α =415 µm³/J", whose drawn slope is visually consistent with ≈400 µm³/J at
  the plotted axis scale (V up to 12×10⁴ µm³ over ΣEd up to 300 J). All three
  same-page sources should agree; two independent ones say "415" bare. **This
  note reports Table 3's numbers taken at face value in µm³/J (i.e., the "10³"
  multiplier is treated as a labeling artifact and ignored)** — flagging this
  explicitly in case a future reader re-checks against the original PDF/journal
  erratum.
- **χ / Table 4 sign.** Table 4's column header prints "Σ(Nc)Ed(0) (×10³
  J/µm²)" (no visible minus sign), but the body text states
  "χ = 2.7×10⁻³ J/µm² (SD 0.34×10⁻³)" — a **negative** exponent. Averaging
  Table 4's 8 raw values (2.6, 2.44, 2.66, 2.52, 2.2, 3.23, 3.03, 2.95) gives
  exactly 2.70, which only matches the stated χ if the multiplier is ×10⁻³, not
  ×10³. Resolved in favor of ×10⁻³ (also consistent with Figs. 13/14/16's own
  correctly-rendered "10⁻²"/"10⁻⁶" axis exponents) — likely a lost superscript
  minus sign in the original table typesetting, same failure mode as Table 3.
- **Symbol "χ".** The paper's own text renders as "w" or similar under plain
  extraction; visual inspection of Fig. 13 (boxed "χ" annotation) and its
  caption ("χ: Energy wear capacity") confirms the intended Greek letter is
  **χ (chi)**, used throughout this note and matching the task's naming.
- **Fig. 16a x-axis tick labels have an apparent typo/rendering artifact**:
  printed sequence reads "0, 50000, 10000, 15000, 20000, 25000, 3000" — the
  2nd and 7th ticks break the otherwise-even 5000-unit spacing implied by the
  unambiguous middle ticks (10000→25000). Digitization uses the corrected
  scale (0–30 000 in steps of 5000), i.e. reads "50000"→5000 and "3000"→30000.
- **Fig. 3 and Fig. 5 marker types pooled.** Both figures use 3–5 distinct
  marker shapes (different δ* sequences / loading types) that mostly overlap
  at this print resolution; per the paper's own message (all sequences
  collapse onto one line/curve regardless of marker), points are digitized as
  one pooled series rather than risk misattributing overlapping symbols to the
  wrong marker family. Fig. 4's two series (25k vs 50k cycles) were kept
  separate — clearly distinguishable, only 4 and 7 points.
- **Fig. 5** is very dense (>40 near-overlapping small diamonds/squares/
  triangles hugging the αs=1 diagonal at low x); the 40 digitized points are a
  representative read of the trend + scatter envelope, not an exhaustive
  pixel-perfect transcription of every symbol.
- All pixel-figure readings (everything except Table-4-derived
  `Nc_vs_meanenergydensity_TiC_alumina.csv`, which is computed exactly from
  printed table text) are manual visual estimates off 300 dpi crops — good for
  order-of-magnitude/trend/slope provenance, not for last-digit precision.
- No Hertzian pressure conversion is given in the paper for the 50/150 N TiN
  sweep or for the 66–333 N/mm Ti64/Ti64 sweep; the GPa/MPa ranges quoted in
  the Loading Matrix above for those two rows are **this note's own Hertz
  power-law scaling** from the paper's one explicit reference point in each
  family (>1 GPa @ 100 N; 525 MPa @ 133 N/mm), not values stated in the source.
