# Arnaud, Baydoun & Fouvry 2021 (Tribology International) — Modeling adhesive and abrasive wear phenomena in fretting interfaces (WTO multiphysics model)

**NOTE — this is a fretting-wear MODELING paper, NOT a bolt self-loosening paper.** It
contains **NO preload / F-F0-vs-cycle curves and no bolted joint at all** — no bolt, no
nut, no clamped members. Its value to BAS V2 is purely as a **G2 lead/anchor**: a
regime-specific (adhesive-vs-abrasive) energy-wear-coefficient formalism, plus a
physically-grounded mechanism (interfacial di-oxygen partial pressure, via an
Advection-Dispersion-Reaction "ADR" model) for **switching** between the two regimes as
a function of contact pressure, size and sliding frequency. Everything quantitative in
this paper is either (a) a **model equation + fitted/assumed constant**, or (b) a
**reused, already-published experimental dataset** (Ti-6Al-4V cylinder-on-flat fretting
wear, from Fouvry et al. 2017 Tribology International, ref. [15] — itself present in
this same library, already separately digitized under `fouvry2017ti_*.csv`/
`fouvry2017ti.md` in this folder). Nothing here is new preload/loosening data.

## Citation + DOI

P. Arnaud, S. Baydoun, S. Fouvry, "Modeling adhesive and abrasive wear phenomena in
fretting interfaces: A multiphysics approach coupling friction energy, third body and
contact oxygenation concepts," *Tribology International* 161 (2021) 107077.
DOI: [10.1016/j.triboint.2021.107077](https://doi.org/10.1016/j.triboint.2021.107077).
HAL id: hal-03453434. Authors: MINES ParisTech (Centre des Matériaux) + Ecole Centrale
de Lyon (LTDS laboratory).

Two companion papers, both cited internally as refs. [15] and [16] and both directly
consumed as inputs by this paper's model (see Model/apparatus below), are cross-checked
against sibling notes already in this folder:

- **Ref. [15]** — S. Fouvry, P. Arnaud, A. Mignot, P. Neubauer, "Contact size, frequency
  and cyclic normal force effects on Ti–6Al–4V fretting wear processes," *Tribology
  International* 113 (2017) 460–473. This is the **source of every experimental data
  point** reused in this paper's Figs. 2-4, 11-13 (the R=80 mm, Fn,L=1066 N/mm Ti-6Al-4V
  cylinder-on-flat condition). Present in this library
  ("Contact size frequency and cyclic normal force effects on Ti-6Al-4V fretting wear
  (Fouvry 2017 Tribol Int).pdf", already text-extracted as `fouvry2017ti_fulltext.txt`
  and partly digitized as `fouvry2017ti_alpha_vs_phi_*.csv` — see Curve inventory below
  for how this note's own α-vs-φ* CSVs relate to those).
- **Ref. [16]** — S. Baydoun, P. Arnaud, S. Fouvry, "Modelling adhesive wear extension in
  fretting interfaces: An advection-dispersion-reaction contact oxygenation approach,"
  *Tribology International* 151 (2020) 106490. This is the **source of the ADR PDE
  formalism** (Eqs. 13-23 here) and is what this paper's own β/γ reaction-rate
  calibration (Fig. 8/9 here) reduces to a 1D/homogeneous special case of. **Ref. [16]
  itself is not present as a separate PDF in this Rodada-4 folder** — only its
  close 2-author cousin **ref. [24]** (S. Baydoun, S. Fouvry, "An experimental
  investigation of adhesive wear extension in fretting interface: Application of the
  contact oxygenation concept," *Tribology International* 147 (2020) 106266) is present,
  as the arXiv preprint 2101.12014, already noted in `apparatus_notes/baydoun_arxiv.md`.
  That sibling note's own d_O(f,p) power law (34NiCrMo16 **steel**, flat-on-flat,
  p=25-175 MPa) is the same "oxygen distance" concept as this paper's Ti-6Al-4V
  cylinder-on-flat d_O, on a different material/rig — see V2 mapping for why this
  matters (it independently separates a pressure exponent from a frequency exponent,
  which this paper's own calibration does not).

## Gap tag (G2 lead) + why

**G2** — energy-based fretting-wear formalism. This paper is a **lead/anchor**, not a
calibration source: it supplies (a) a validated closed-form for how an energy-wear
coefficient α (mm³/J) should depend on the friction power density φ* through an
exponential two-asymptote law, (b) two concrete, materially-anchored numeric values for
that law's asymptotes (abrasive α_ab, adhesive α_ad) for a Ti-6Al-4V/Ti-6Al-4V pair, and
(c) a mechanistic (not just curve-fit) argument for **why** a wear interface should be
expected to switch between two different wear-rate regimes — grounded in a real
physico-chemical threshold (local O2 partial pressure) rather than an arbitrary tuner.
This is exactly the kind of "regime-specific constant + physically-motivated gate" precedent
BAS V2's own gated mechanisms (`slip_onset_gate`, the pressure-dependent conformance
gate, `surface_damage`-modulated friction/wear) are built from — see V2 mapping.

## Model/apparatus

**What is modeled — "WTO": Wear (friction-energy) + Third-body + contact-Oxygenation.**
Three sub-models are coupled iteratively (Fig. 10, "global algorithm"):

1. **Local friction-energy surface-wear model** (2D FEM, from Arnaud & Fouvry 2018,
   *Wear* 412-413:92-108 — not itself in this library): at iteration *n*, wear-depth
   increment at position *x* on each counterface = local wear coefficient × local
   friction energy density × acceleration factor (Eqs. 5-9). Includes a **dynamic
   third-body (debris) layer** that grows/thins with the wear increment and modifies the
   local pressure profile (and hence the local friction energy density) that feeds back
   into the next iteration.
2. **ADR (Advection-Dispersion-Reaction) contact-oxygenation model** (finite-difference,
   Runge-Kutta-4, from ref. [16], reduced here to 1D): computes the steady-state profile
   of di-oxygen partial pressure P_O2(x) within the porous third-body layer, balancing
   Darcy advection, Fickian dispersion, and a reaction term consuming O2 via Ti
   oxidation.
3. **Coupling logic** (Eq. 38): at every FE node *x* and every macro-iteration, compare
   the local P_O2(x) to a threshold P_O2,th. If P_O2(x) ≥ P_O2,th → the node is
   "oxygenated" → **abrasive** wear coefficient α_ab is used there. If P_O2(x) <
   P_O2,th → **adhesive** wear coefficient α_ad is used instead. This produces a
   spatially-discontinuous wear-rate distribution across the contact, which is what
   generates the composite "W-shape" scar (abrasive corona + adhesive core) instead of
   the classical, spatially-uniform "U-shape".

The loop runs: FEM mechanical wear increment → ADR oxygenation update → new α(x)
distribution → remesh → repeat, until the target experimental cycle count *N* is
reached (an acceleration factor β_A,n lets each numerical iteration represent many real
fretting cycles, capped so no single iteration removes more than 3 µm).

**Validation experiments = Ti-6Al-4V cylinder-on-flat**, reused unchanged from ref. [15]
(Fouvry 2017 TI) — **not new data generated by this paper**. Main condition: cylinder
radius R=80 mm sliding on a flat plane, both Ti-6Al-4V, lateral width LW=8 mm, normal
force Fn=8530 N (linear normal force Fn,L=1066 N/mm), sliding (gross-slip) amplitude
δg*=±75 µm, N=5000 cycles, sliding frequency swept 0.1-10 Hz (7 discrete frequencies
underlie the 7-point scatter in Fig. 4 — the paper states the sweep range but does not
enumerate the intermediate frequency values; only the extremes 0.1 Hz and 10 Hz and a
few named values 0.1/1/2/5 Hz for the profile figures are given explicitly). Initial
(unworn) Hertzian contact pressure p_max=525 MPa, Hertzian half-width a_H=1.29 mm
(both evolve/grow with wear during the test). δg*/a_H<6%, i.e. even under gross slip the
fretting stroke is small relative to the (growing) contact size — most of the interface
is never directly exposed to ambient air, which is precisely why an internal oxygenation
gradient (rather than a simple "exposed vs not" binary) is needed.

A **second, separate** experimental configuration — reused from ref. [16]'s own
flat-on-flat calibration methodology — is used purely to calibrate the ADR reaction-rate
constants (β, γ; see Wear model below), not to validate the wear-depth predictions:
homogeneous flat-on-flat Ti-6Al-4V/Ti-6Al-4V, contact area S=Lx×Ly=5×5=25 mm² (so
pressure stays flat/constant through the test, unlike the evolving-Hertzian main test),
p=100 MPa, δg=±100 µm, N=20000 cycles, f=1/5/10 Hz only.

## Materials

Homogeneous **Ti-6Al-4V / Ti-6Al-4V** contact (both cylinder and plane), matching ref.
[15]'s rig.

| Body | Property | Value |
|---|---|---|
| First bodies (Ti-6Al-4V cylinder + plane) | Young's modulus E | 119 GPa |
| First bodies | Poisson's ratio ν | 0.287 |
| Third body (debris/oxide layer, FEM part) | Young's modulus E | 100 GPa (modeling input for the debris-layer FEM part, not an independently measured oxide-powder modulus) |
| Third body | Poisson's ratio ν | 0.3 |

Oxidation chemistry (Ti-only, homogeneous contact assumed — no separate treatment of a
second material): Ti(s) + O2(g) ⇌ TiO2(s), standard enthalpy of formation ≈ −1000 kJ/mol
at 20°C, standard entropy ΔrS0 = −185.3 J/K/mol (from CRC Handbook, ref. [34]).

## Loading matrix

| Quantity | Main validation test (cylinder-on-flat, ref. [15] data) | ADR-calibration test (flat-on-flat, ref. [16] method) |
|---|---|---|
| Contact geometry | Cylinder R=80 mm on flat, LW=8 mm | Flat-on-flat, Lx=Ly=5 mm (S=25 mm²) |
| Normal force / linear force | Fn=8530 N (Fn,L=1066 N/mm) | p=100 MPa fixed (constant contact area ⇒ constant pressure) |
| **Contact pressure** | Initial Hertzian **p_max=525 MPa** (0.525 GPa), evolving with wear; local **overpressure** in the long-term (80000-cycle) exploratory run can exceed **2× the initial Hertzian value (~1.2-1.3 GPa)** at the abrasive/adhesive domain boundary once a W-shape scar is established (Fig. 19, f=2 Hz case) | Flat, constant **100 MPa** by construction |
| Sliding (gross-slip) amplitude δg* | ±75 µm | ±100 µm |
| Frequency f | **0.1 to 10 Hz** (7 pts for the α-vs-φ* sweep; 0.1/1/2/5 Hz named for the wear-profile figures) | **1, 5, 10 Hz only** (3 pts, used solely to fit β and γ) |
| Cycles N | 5000 | 20000 |
| Friction coefficient | Energy friction coefficient μe≈0.6 (Eq. 1), quasi-constant vs. frequency | μe=0.6 assumed (not independently measured for this specific test) |
| φ* range spanned | ≈0 to 0.24 W/mm² (Fig. 4/14/15 x-axis) | 0.024 (f=1 Hz, reference), 0.12 (f=5 Hz), 0.24 W/mm² (f=10 Hz) |

Contact size and normal force are **held fixed** in this paper's own validation runs —
only frequency is swept. The abstract's mention of the ADR mechanism being "a function
of contact pressure, size and frequency" describes the **general capability of the ADR
formalism** (inherited from ref. [16]/[24]), not a sweep this paper itself re-exercises;
this paper only exercises the frequency axis of that general capability (see V2 mapping
caveat on the β/γ calibration below).

## Wear model

**Global energy-wear law** (Eq. 2, applied locally as Eq. 5-6): wear volume/depth is
proportional to accumulated dissipated friction energy/energy density through an
energy-wear coefficient α [mm³/J]:

```
V = α · ΣEd                      (global, Eq. 2)
h(x) = α · Σφ(x)                 (local, Eq. 5)
```

with the **energy friction coefficient** μe = Ed/(4·Fn·δg*) (Eq. 1) and **friction power
density** φ* = Ed/(S·f) = ΣEd/(S·N·f) (Eq. 3, units **W/mm²** — see caveat below on an
axis-label typo in two of the paper's own figures).

**Two regime-specific energy wear coefficients** (the paper's headline deliverable), each
following the same exponential two-asymptote form vs. friction power density (Eq. 4):

```
α(φ*) = (α_ab − α_ad) / exp(ε·φ*) + α_ad
```

α_ab = pure-abrasive asymptote (φ*→0), α_ad = pure-adhesive asymptote (φ*→∞), ε = sigmoid
steepness. **Table 1 values** (both fitted independently — once to the raw experimental
scatter, once to the WTO model's own numerical output):

| Fit target | Counterface | α_ab (mm³/J) | α_ad (mm³/J) | ε (mm²/W) |
|---|---|---:|---:|---:|
| Experiments (Fig. 4) | cylinder | 4.1×10⁻⁴ | **1.0×10⁻⁵** | 11 |
| Experiments (Fig. 4) | plane | 5.1×10⁻⁴ | 1.0×10⁻⁴ | 11 |
| WTO model (Fig. 14) | cylinder | 4.1×10⁻⁴ | **0.9×10⁻⁴** | 22 |
| WTO model (Fig. 14) | plane | 5.1×10⁻⁴ | 1.4×10⁻⁴ | 22 |

α_ab is effectively an **input** (same value used for the "experiments" and "WTO" rows —
it is the directly-measured abrasive wear rate, not independently re-fitted by the
model). α_ad and ε are the two numbers the model actually predicts/re-derives, and they
**do not match** the simple experimental curve-fit closely, especially for the cylinder:
the WTO-consistent adhesive coefficient (0.9×10⁻⁴) is **~9× higher** than the simple
exponential fit to the raw cylinder scatter (1.0×10⁻⁵) — the authors attribute the raw
cylinder scatter's own dispersion to an unmodeled plane→cylinder metal-transfer
phenomenon, so the "true" α_c,ad is not a settled number even within this paper. Also
note ε **doubles** from 11 (fit directly to noisy experimental scatter) to 22 (fit to the
WTO model's own smoother numerical curve) — i.e. the model's regime transition is sharper
(more step-like) than the raw-data curve-fit suggests.

**Threshold friction power density for the U→W shape transition**: φ*_th = **0.1 W/mm²**
(an experimentally observed value, from ref. [15], reproduced without independent
re-derivation in this paper).

**ADR oxygenation transition** (mechanism for *where* α_ab vs α_ad applies): local di-
oxygen partial pressure P_O2(x) computed from an advection-dispersion-reaction PDE
(Eq. 13: a·dPi/dt = −∇·(Ji)+Ri = −∇·(−Di∇Pi+vPi)), solved by 4th-order Runge-Kutta finite
differences (space step Δx=40 µm, time step Δt=8×10⁻⁵ s, steady-state convergence
ε_r=10⁻⁴). Threshold **P_O2,th = 0.1 Pa** (reused from Iwabuchi et al. 1983 for a
*steel* interface — applied to Ti-6Al-4V here **without independent re-derivation for
titanium**; justified only qualitatively via TiO2's very low standard oxidation
potential). Reaction-rate coefficient calibrated as a power law in friction power density
(Eq. 29): **r_O2 = β·(φ*/φ*_ref)^γ**, with **β=218.64 s⁻¹, γ=0.94** (R²=0.98), φ*_ref=
0.024 W/mm² (the f=1 Hz reference condition of the flat-on-flat calibration test
described above) — fit against only 3 points (f=1, 5, 10 Hz, **frequency varied at fixed
pressure**; see V2 mapping caveat). Other ADR constants (Table 2): debris-bed porosity
a=0.48 (assumed constant), particle size dp=1 µm, longitudinal dispersivity αL=aw,n/10
(Pickens-Grisak relation, aw,n = instantaneous worn contact half-width), gas properties
of O2/N2 (viscosity via Wilke's model, diffusion via Carman-Kozeny), ambient air
composition P_O2=21278 Pa / P_N2=80046 Pa at T=298 K, P=101325 Pa.

**Third-body conversion factor** γ_tb = **0.85** (constant in space and time — a
deliberately coarse simplification, calibrated against the pure-abrasive f=1 Hz U-shape
case; the paper notes an elliptic, position-dependent γ_tb(x) would improve the U-shape
depth prediction but was not implemented here).

**Scar-shape prediction**: homogeneous P_O2(x) ≥ P_O2,th everywhere ⇒ constant α=α_ab ⇒
smooth, continuous **"U-shape"** wear profile (low frequency, f=0.1 Hz in the main test).
P_O2(x) dropping below P_O2,th in the contact interior (higher frequency) ⇒ discontinuous
α(x) (α_ab laterally, α_ad centrally) ⇒ composite **"W-shape"** profile with the maximum
wear depth on the lateral (abrasive) shoulders and a local minimum at the centre
(adhesive core) — the model's central achievement, not previously reproducible by a
single-coefficient wear law.

**Quantitative validation** (Fig. 13, WTO vs. a plain Wear+Third-body-only "WT" ablation
lacking the oxygenation gate) — relative error in max wear depth (h_max%) and its lateral
position (X_hmax%) vs. experiment:

| Frequency | Scar shape | WT h_max% | WT X_hmax% | WTO h_max% | WTO X_hmax% |
|---|---|---:|---:|---:|---:|
| 0.1 Hz | U (homogeneous, no adhesive) | ≈35% | 0% | ≈35% (same as WT) | 0% (same as WT) |
| 2 Hz | W | ≈45% | 100% (predicts max at centre — wrong) | <15% | <20% |
| 5 Hz | W | ≈20% | 100% (same failure mode) | <5% | <20% |

I.e. once adhesive wear activates (W-shape), the plain WT ablation is not just
quantitatively worse but **qualitatively wrong** (puts the deepest point at the centre
instead of the shoulders) — the oxygenation gate is what recovers the correct
qualitative scar topology, not just a refinement of an already-right answer.

**Overpressure / TTS discussion** (Section 5, context — not part of the core wear-model
deliverable): because the W-shape's central adhesive domain carries most of the contact
load on a shrunk, discontinuous surface, the *local* peak pressure there can reach
2-3× the *initial* Hertzian value once the interface has run long enough (long-term
80000-cycle exploratory simulation, not the 5000-cycle validated main test) — offered as
an explanation for why fretting cracking and tribologically-transformed-structure (TTS,
white-layer) formation are experimentally observed in the mixed-slip regime rather than
at the classical partial/gross-slip transition. Not a wear-depth/energy validation curve
itself; not digitized.

## Main conclusions

1. The WTO model is the first to reproduce the composite "W-shape" adhesive-abrasive
   fretting scar (not just the classical "U-shape"), by combining a friction-energy wear
   model with an oxygenation-driven spatial partition between two energy-wear
   coefficients.
2. It predicts the U→W shape transition at a threshold friction power density, matching
   experiment.
3. Despite using only two wear coefficients (α_ab, α_ad), the model reproduces the
   asymptotic decay of the *global* wear rate with frequency observed experimentally —
   because it is really tracking the *area fraction* under each regime, not just
   interpolating a single global number.
4. The inner adhesive domain's radial extent is predicted to be nearly constant once
   established; growth of the overall worn contact radius is driven mainly by lateral
   (abrasive-domain) extension.
5. The oxygenation-driven scar discontinuity generates local contact-pressure
   overshoots (2-3× initial Hertzian) that plausibly explain independently-reported
   cracking/TTS location anomalies (mixed-slip regime, not partial-slip transition).
6. Explicitly flagged limitations: constant (not position/time-varying) third-body
   conversion factor and constant (not third-body-nature-dependent) porosity both limit
   quantitative accuracy, especially for the U-shape depth and the low/medium-frequency
   wear-rate over-prediction of the decay.

## Curve inventory

| Figure | Series | CSV filename | x quantity (unit) | y quantity (unit) | Experiment vs. model | #pts |
|---|---|---|---|---|---|---|
| Fig. 4 | Plane, raw scatter | `arnaud2021ti_alpha_vs_phi_plane_exp.csv` | Friction power density φ* (W/mm²) | Energy wear coefficient α (mm³/J) | **Experiment** | 7 |
| Fig. 4 | Cylinder, raw scatter | `arnaud2021ti_alpha_vs_phi_cylinder_exp.csv` | Friction power density φ* (W/mm²) | Energy wear coefficient α (mm³/J) | **Experiment** | 7 |
| Fig. 14 | Plane, "numerical WTO" scatter | `arnaud2021ti_alpha_vs_phi_plane_model.csv` | Friction power density φ* (W/mm²) | Energy wear coefficient α (mm³/J) | **Model** (WTO simulation output) | 7 |
| Fig. 14 | Cylinder, "numerical WTO" scatter | `arnaud2021ti_alpha_vs_phi_cylinder_model.csv` | Friction power density φ* (W/mm²) | Energy wear coefficient α (mm³/J) | **Model** (WTO simulation output) | 7 |
| Fig. 9 | Reaction rate coefficient markers | `arnaud2021ti_reaction_rate_vs_freq_model.csv` | Sliding frequency f (Hz) | Oxidation reaction rate r_O2 (s⁻¹) | **Model** (ADR-back-computed to match experimental d_O; not itself a directly-measured quantity — see caveats) | 3 |
| Fig. 12 (row 3, col 1) | Total worn thickness, f=0.1 Hz (U-shape) | `arnaud2021ti_wear_profile_0p1Hz_Ushape_exp.csv` | Lateral position X (mm) | Total worn thickness Z (mm) | **Experiment** (2Deq) | 26 |
| Fig. 12 (row 3, col 1) | Total worn thickness, f=0.1 Hz (U-shape) | `arnaud2021ti_wear_profile_0p1Hz_Ushape_model.csv` | Lateral position X (mm) | Total worn thickness Z (mm) | **Model** (WTO) | 25 |
| Fig. 12 (row 3, col 2) | Total worn thickness, f=2 Hz (W-shape) | `arnaud2021ti_wear_profile_2Hz_Wshape_exp.csv` | Lateral position X (mm) | Total worn thickness Z (mm) | **Experiment** (2Deq) | 26 |
| Fig. 12 (row 3, col 2) | Total worn thickness, f=2 Hz (W-shape) | `arnaud2021ti_wear_profile_2Hz_Wshape_model.csv` | Lateral position X (mm) | Total worn thickness Z (mm) | **Model** (WTO) | 25 |

**Why these and not others**: Figs. 4/14 are the paper's own primary "wear coefficient
vs. energy density" validation pair (the literal ask: regime-specific α, experiment vs.
model, both counterfaces). Fig. 9 is the calibration curve underlying the ADR
oxygenation-transition mechanism (the "pressure/oxygenation dependence" ask). Fig. 12's
"total worn thickness" row was chosen over its "cylinder worn profile" / "plane worn
profile" rows (same figure, rows 1-2) because it is the single clean curve per
frequency/model directly showing the **U-shape vs. W-shape scar morphology** and the
**max wear depth** call-out that the task specifically names — the per-counterface rows
are noisier (small-scale oscillations in the raw profilometry) and carry the same
qualitative story with more digitizing risk for no added value. f=0.1 Hz and f=2 Hz were
chosen (over the third available case, f=5 Hz) as the clearest U-shape/W-shape contrast
pair; f=5 Hz repeats the f=2 Hz story at lower absolute wear and was not separately
digitized.

**Not digitized (context only, not wear-vs-energy/pressure curves)**: Fig. 1 (U/W-shape
schematic), Fig. 2 (rig + fretting-loop schematic), Fig. 3 (scar morphology micrographs
vs. frequency), Fig. 5-7 (contact-oxygenation concept schematics, air-distilling
illustration), Fig. 8 (ADR calibration methodology illustration — its **numeric result**
is what Fig. 9 plots, which **is** digitized), Fig. 10 (global algorithm flowchart),
Fig. 11 (plane wear profile vs. frequency, superseded here by the cleaner Fig. 12 "total
worn thickness" row), Fig. 13 (h_max%/X_hmax% bar chart — only 3 frequencies reported;
transcribed as a table above instead of a thin 3-point CSV), Fig. 16 (per-cycle
multi-panel dynamic snapshot: pressure/P_O2/wear/third-body vs. X at 4 cycle counts × 3
frequencies — rich but not itself a model-vs-experiment comparison, it's WTO-only),
Fig. 17 (worn/adhesive radius vs. cycles, long-term 80000-cycle exploratory run, WTO-only
no experimental counterpart), Fig. 18 (per-cycle wear-increment profile, WTO-only),
Fig. 19 (max contact pressure vs. cycles, WTO-only, the overpressure result — reported
as a number range in Wear model above instead), Figs. 20-22 (TTS/cracking discussion,
qualitative, third-party data schematics not this paper's own wear-depth/energy curves).

## V2 mapping

- **Regime-specific α ↔ `k_wear_spec`**: BAS V2's wear formalism (`K_archard`/`hardness`,
  merged into the single canonical `k_wear_spec = K/H` [1/Pa], CLAUDE.md §4.42a) is
  currently a **single, regime-blind constant**. This paper is a concrete, physically-
  grounded precedent for splitting a wear-rate constant into **two regime-specific
  values gated by a threshold** on a local physical driver, rather than tuning one global
  number to a compromise value. It is **not a direct numeric transplant** — α here [mm³/J,
  friction-energy-normalized] and `k_wear_spec` [1/Pa, Archard-normalized] are different
  formalisms requiring their own unit/physics reconciliation, and both are Ti-6Al-4V-
  fretting-specific, not portable constants (same "constants are per-pair, forms
  transfer" pattern documented throughout `MODEL_LEGITIMACY.md`). The transferable
  **form** is: "wear rate is not one number; it is two numbers plus a state-dependent
  switch," which is a candidate structural upgrade path for `k_wear_spec` if/when BAS V2
  needs to represent a wear-regime transition (e.g. running-in vs. steady-state, or a
  lubricated-vs-dry transition) rather than always fitting a single effective value.
- **Pressure/oxygenation ↔ conformance-gate basis**: the ADR mechanism (a state variable
  — here, a *spatial* O2-partial-pressure profile — crossing a threshold to switch
  physical regime) is structurally the same pattern as BAS V2's own gated mechanisms:
  the pressure-dependent conformance gate (`conform_driver="effective"`,
  `W_conf_ref`, CLAUDE.md §4.9), `slip_onset_gate`'s Hill-function incubation, and
  `surface_damage` D's friction/wear modulation. This paper is best read as **qualitative
  precedent/validation for the gate-design pattern itself** (a real physico-chemical
  threshold mechanism producing exactly this kind of two-regime switch), not as a source
  of a reusable pressure exponent or threshold value — BAS V2 has no within-contact
  spatial resolution (lumped slow-state MSD model), so the ADR's literal spatial PDE
  cannot be ported; only the "threshold-gated regime switch" structural idea transfers.
- **A caveat on the β/γ calibration worth flagging explicitly**: this paper's own ADR
  reaction-rate fit (β=218.64 s⁻¹, γ=0.94, R²=0.98) is calibrated by varying **frequency
  only**, at **fixed pressure** (p=100 MPa, 3 points: f=1/5/10 Hz) — so γ≈0.94 (~1,
  "linear in frequency") is being extracted from a φ*=μe·p·(4·δg·f) sweep that only ever
  moved the *f* factor. The sibling note `apparatus_notes/baydoun_arxiv.md` (ref. [24]'s
  own arXiv preprint, 34NiCrMo16 steel, flat-on-flat, independently varying **both**
  pressure 25-175 MPa and frequency 0.5-10 Hz for the same underlying "oxygen distance"
  d_O concept) finds two **different** exponents for the analogous quantity:
  n_p=−0.32 (pressure) vs. n_f=−0.22 (frequency) — i.e. pressure and frequency do **not**
  necessarily collapse onto one exponent for this class of mechanism. This paper's own
  γ=0.94 has therefore only been validated along the frequency axis; whether the same
  exponent applies if pressure were varied independently is untested within this paper
  itself. Treat γ as a **frequency-specific** exponent for Ti-6Al-4V at p≈100 MPa, not
  a universal φ*-exponent, if this number is ever reused.
- **Caveat = modeling, not new data**: this paper contributes **zero new preload/
  loosening curves and no new curve-library case** — it is a model-development paper
  whose validation data is entirely borrowed from ref. [15] (already independently in
  this library as `fouvry2017ti_*`). Its α_ab/α_ad/ε/β/γ/P_O2,th numbers are Ti-6Al-4V-
  dry-fretting-specific constants, not directly reusable in a bolted-joint calibration
  without their own provenance work. Its real, durable contribution to BAS V2 is
  **conceptual**: a validated instance of "two regime-specific wear constants + a
  physically-motivated threshold gate reproduces a scar-shape transition that a single
  constant cannot" — a template worth remembering if/when a BAS V2 wear-regime-splitting
  form is ever justified by data (currently, per CLAUDE.md's `k_wear_spec` merge note,
  BAS V2 deliberately keeps wear as a single lumped constant).

## Digitization caveats

- **Units typo in the source paper's own figure axis labels** (Figs. 4 and 15, but
  *not* Fig. 14): the x-axis is printed "(W/mm³)" in Figs. 4 and 15, but the paper's own
  nomenclature section, Eq. 3 (φ*=Ed/(S·f), units J/(mm²·s)=W/mm²) and Fig. 14's
  (correctly-labeled) "(W/mm²)" axis, plus the in-figure threshold annotation itself
  ("φ_th*=0.1 **W/mm²**" printed directly on the Fig. 4 chart) all agree the quantity is
  friction power density per unit **area**, W/mm². Treated the "W/mm³" appearing on two
  of the six chart axes as a copy-paste typo and used W/mm² throughout this note and all
  CSVs.
- **ε units inconsistency**: the in-text first definition (page 9-10 area, just after
  Eq. 4) states "ε is presently fixed at ε=11 **J/mm³**", which is dimensionally
  inconsistent with exp(ε·φ*) needing to be dimensionless when φ* is in W/mm² — Table 1
  instead states **ε=11 mm²/W** (dimensionally consistent) for the same fit, and this is
  the value used throughout this note.
- **α_c,ad / α_p,ad in-text vs. Table 1 discrepancy**: the in-text sentence immediately
  preceding Table 1 states α_c,ad=**0.5×10⁻⁵** mm³/J and α_p,ad=**1.1×10⁻⁴** mm³/J, while
  Table 1 itself (the structured, explicitly-labeled compilation, and the source also
  used by the sibling `baydoun_arxiv.md` note when it flagged these same in-text numbers)
  states α_c,ad=**1.0×10⁻⁵** mm³/J and α_p,ad=**1.0×10⁻⁴** mm³/J. Table 1's values were
  used here (for both the note text and as anchors cross-checking the digitized scatter)
  because a later in-text self-consistency check ("the quasi-negligible adhesive wear
  rate coefficient... i.e. α_c,ad=1.0×10⁻⁵ mm³/J ≈0.025·α_c,ab") arithmetically matches
  Table 1's 1.0×10⁻⁵ (1.0e-5/4.1e-4=0.0244) but not the earlier in-text 0.5×10⁻⁵
  (0.5e-5/4.1e-4=0.0122) — treated as a typo in the earlier in-text sentence, not in
  Table 1.
- **Fig. 4/14 scatter digitization**: read by direct visual inspection of a ≥300-400 dpi
  crop against the linear gridlines (y: 0, 2×10⁻⁴, 4×10⁻⁴, 6×10⁻⁴; x: 0, 0.05, ...,
  0.25), not by pixel-coordinate regression. Estimated precision ≈±0.1-0.2×10⁻⁴ mm³/J on
  α and ≈±0.005-0.01 W/mm² on φ*. The x=0 anchor points for both Fig. 14 series were
  fixed to the paper-stated exact α_ab values (Table 1) rather than pixel-read, since the
  model curve is defined to pass through that value by construction. Both experiment
  series show visible scatter around their own Eq. 4 fit curve (most pronounced for the
  cylinder, consistent with the paper's own "large dispersion... attributed to the
  transfer phenomenon" caveat for that counterface) — a real feature of the data, not a
  digitization artifact; do not "correct" these points toward the smooth Eq. 4 curve.
- **Fig. 9 markers are a model-derived quantity, not a direct measurement**: r_O2 is
  *extracted from the ADR analysis* (back-fit so that the ADR-simulated d_O matches the
  experimentally-measured d_O at each frequency) — it is not itself something a sensor
  measures. Labeled "model" in the curve inventory for that reason, though it sits
  upstream of (and is consumed by) the WTO wear-depth predictions.
- **Fig. 12 wear-profile digitization**: read off the "total worn thickness (mm) vs. X
  position (mm)" row only (not the separate cylinder/plane profile rows, which show the
  same two curves' constituent halves with more small-scale noise). Small (~0.005-0.008
  mm) below-zero excursions on the outer shoulders of both the experimental U-shape and
  W-shape curves (around |X|≈2.0-2.3 mm) were read directly off the plotted curve and
  kept as-is; these are almost certainly profilometry baseline noise, not a physical
  "negative wear," but are small enough not to affect the overall shape/depth story.
  Estimated precision ≈±0.003-0.005 mm on Z, ≈±0.1 mm on X. Digitized peak-depth values
  were cross-checked against the paper's own Fig. 13 h_max% figures: U-shape (f=0.1 Hz)
  digitized exp/model peaks (0.155 mm / 0.107 mm) give a 31% relative error, close to the
  paper's stated ≈35%; W-shape (f=2 Hz) digitized peaks (≈0.065 mm both) give <10%
  relative error, consistent with the paper's stated WTO h_max%<15%.
- **Frequency values for the Fig. 4/14 sweep are not all enumerated in text** — only the
  extremes (0.1 Hz, 10 Hz) and the profile-figure subset (0.1/1/2/5 Hz) are named
  explicitly. The 7 φ* x-values in the `_exp`/`_model` CSVs are therefore read purely
  from marker pixel position, not back-computed from a frequency list (unlike the ADR
  calibration test, whose 3 φ* values ARE back-computable exactly from the stated
  f=1/5/10 Hz at p=100 MPa/δg=100 µm — 0.024/0.12/0.24 W/mm², matching Table 2 exactly).
- File `arnaud2021ti_fulltext.txt` (full 46-page text dump, page-marker-tagged) and
  `arnaud2021ti_err.txt` (empty — the extraction succeeded on the first UTF-8-forced
  attempt after an initial cp1252 console encoding failure) were left in the Rodada-4
  root alongside the equivalent files already produced there by sibling agents for other
  papers in this round, consistent with that established working-file convention.
