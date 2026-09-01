# Van Peteghem, Fouvry & Petit 2011 (Wear) — Effect of variable normal force and frequency on fretting wear response of Ti-6Al-4V contact

**NOTE — not a bolt self-loosening paper.** This is a pure fretting-wear tribology study (blade-disk
turbojet contact simulation). It contains **NO preload / F-F0-vs-cycle curves and no bolted joint at
all**. Its value to BAS V2 is purely as a **mechanism/provenance anchor**: energy-based wear behaviour
under a *cyclically varying* normal force (i.e. a time-varying contact pressure with a contact-opening
stage each cycle), which is exactly the loading shape a pressure-dependent conformance gate is meant to
capture.

## Citation + DOI

B. van Peteghem, S. Fouvry, J. Petit, "Effect of variable normal force and frequency on fretting wear
response of Ti–6Al–4V contact," *Wear* 271 (2011) 1535–1542.
DOI: [10.1016/j.wear.2011.01.060](https://doi.org/10.1016/j.wear.2011.01.060).

LTDS (Laboratoire de Tribologie et Dynamique des Systèmes) — Ecole Centrale de Lyon, France. Funded by
Safran/Snecma (aeronautical turbojet blade-disk fretting motivation). Same LTDS/Fouvry group and rig
lineage as the in-library "Fouvry 2017 Tribol Int" (contact size/frequency/cyclic normal force) paper —
that 2017 paper is a distinct, later study; this 2011 paper is the earlier one introducing the variable
normal-force rig and the constant-vs-variable-NF / frequency contrast. Ref. [1] cited throughout
(Fouvry, Paulin, Deyber, Tribology International 42(3) (2009) 461-474) established the δg*=75 μm
reference sliding amplitude and the contact-size effect for the same Ti-6Al-4V/Ti-6Al-4V pairing — not
itself in this library, cited here only as the source of the reference test condition.

## Gap tag(s) + why

- **G2 (primary)** — pressure-**history** dependence of wear/friction dissipation, i.e. provenance for a
  conformance/contact-opening gate that depends on the time-history of normal force /contact pressure,
  not just its instantaneous or peak value. This paper is a direct, controlled experiment on exactly that
  question: same material, same target sliding amplitude, same frequency, only the **normal-force
  waveform** (constant plateau vs ramp-up/plateau/ramp-down-with-brief-contact-opening) is varied. The
  headline result — a single `V = αV·ΣEd` energy-wear line fits **both** waveforms at fixed frequency
  (Fig. 9b, R²=0.98) while the raw wear-per-cycle rate differs by ~3× between the two waveforms (Fig. 9a)
  — is direct evidence that the correct state variable is the **dissipated-energy integral** (itself
  pressure-history-dependent through Q(t)·δ(t)), not a separate empirical "normal-force-shape" tuner. That
  is precisely the physics a conformance gate keyed to accumulated/instantaneous contact work should
  reproduce.
- **G8 (secondary)** — Ti-6Al-4V material anchor: mechanical properties (Table 1), an energy-wear
  coefficient αV for a Ti-6Al-4V/Ti-6Al-4V cylinder-plane fretting pair, and a strong, quantified
  frequency dependence of that coefficient (factor ~5.5 over a factor-45 frequency range) — useful
  reference points for any titanium-specific `k_wear_spec` (=K/H) provenance work, independent of the
  bolted-joint validation library (which is currently steel/aluminium dominated).

## Rig / apparatus

- **Machine**: MTS **axial-torsion** servo-hydraulic testing machine, **two independently driven
  servo-hydraulic actuators** — a radial actuator drives the **normal force**, an axial actuator drives
  the **tangential displacement**. This decoupled 2-actuator control is what makes a genuinely
  *independent* normal-force waveform (as opposed to a fixed dead-weight/spring normal load) possible —
  the key apparatus enabler for the G2 experiment.
- **Contact geometry**: cylinder-on-plane, cylinder radius **R=80 mm**, contact length **8 mm** (chosen
  "as a compromise between simplicity and representativeness" of the real blade-disk contact, Fig. 1).
- **Normal-force mechanism**:
  - *Constant normal-force tests* (series a, b): P held at a fixed plateau (8523 N) for the whole test,
    sinusoidal tangential displacement δ(t) (Fig. 4a).
  - *Variable normal-force tests* (series c): **square-shaped** (trapezoidal) co-evolution of P(t) and
    δ(t) — both ramp up linearly together from 0 to P=8523 N / δ=δmax, hold at plateau, then ramp back
    down to 0 at the same rate (Fig. 4b). When δ is held at zero, **P is driven slightly negative**
    (a deliberate small tensile/separating command) to reproduce genuine **contact opening** each cycle —
    modelling the blade falling to the bottom of the disk socket when the engine stops (Fig. 1). This
    contact-opening stage is the physical feature this paper isolates that a constant-NF test cannot
    represent at all.
  - Displacement amplitude was tuned per test so that the *actual* sliding amplitude δg (LVDT-measured,
    net of system+contact tangential compliance) matched across constant/variable conditions, "rationalising
    the comparison" (Fig. 3 defines the δ-vs-δg compliance correction).
- **Sensors**: tangential displacement via LVDT; normal force via a 25 kN load cell; tangential
  (friction) force via a 250 kN load cell (the latter is a shared/oversized cell from the axial-torsion
  frame's normal fatigue-test range — actual Q never exceeds a few kN here, so resolution is coarser than
  a dedicated small-range cell would give; flagged as a plausibility caveat, not a transcription error).
- **Wear measurement**: mass loss (before/after weighing) plus **3D profilometry** of the cleaned
  (ultrasound/ethanol) scar to get wear volume V (µm³). Scars additionally characterized by optical
  microscopy, SEM, EDS (energy-dispersive spectrometry) and XRD — used here to explain *why* the wear
  process differs chemically (titanium-nitride formation) between conditions, not to measure V itself.
- **Dissipated energy**: Ed computed per cycle as the fretting-loop (Q–δ hysteresis loop) area,
  `Ed = ∮ Q(t)·δ(t) dt` (Eq. 1), accumulated over the whole test as `ΣEd = Σᵢ Ed(i)` (Eq. 2) — i.e. Ed is
  itself an integral over the load *history* within each cycle, already "pressure/force-history aware" by
  construction.

## Materials (Table 1)

Ti-6Al-4V (alpha-beta titanium), both bodies (Ti-6Al-4V/Ti-6Al-4V self-mated contact):

| Property | Value |
|---|---|
| Elastic modulus E | 119 GPa |
| Poisson's ratio ν | 0.29 |
| Yield stress | 970 MPa |
| Vickers hardness HV0.3 | 360 |
| Density | 4.4 (g/cm³, implied — unit not printed in Table 1 but standard for Ti-6Al-4V) |

## Loading matrix

Per Table 2 (test series) and Table 3 (individual tests, reproduced in full below):

| Test series | Normal force (N) | δmax (µm) | Frequency (Hz) | Cycles |
|---|---|---|---|---|
| (a) | 8523 (constant) | 240 | 5 | 1000–15,000 |
| (b) | 8523 (constant) | 240 | 0.11; 1; 3; 5 | 1000 |
| (c) | Variable, 0→8523 | 240 | 0.11 | 1000–5000 |

- **Normal-force levels / variation pattern**: max normal force P=8523 N fixed for all tests (constant
  plateau in series a/b; ramp-up→plateau→ramp-down-with-brief-opening in series c). Linear normal loading
  at max P = 1065 N/mm (=8523 N / 8 mm contact length).
- **Contact pressure range**: max Hertzian contact pressure **525 MPa (0.525 GPa)** at P=8523 N — reached
  continuously in constant-NF tests, reached only **momentarily at the cycle plateau** in variable-NF
  tests (pressure sweeps 0→525 MPa→~0/slightly-negative every cycle, following the Hertzian P(t)
  relation for a cylinder-plane contact). This 0→0.525 GPa cyclic sweep, synchronized with the
  displacement/contact-opening sequence, is the literal pressure-**history** signal referenced by gap G2.
- **Sliding amplitude**: imposed displacement δ*=±120 µm (δmax=240 µm peak-to-peak) nominal, giving an
  actual (compliance-corrected) sliding amplitude δg*≈±75 µm nominal (δgmax=2δg*≈150 µm total stroke) —
  the reference gross-slip condition from ref. [1]. The specific tests intercompared in Figs. 9/10 measured
  δg*=68 µm (δgmax=136 µm) — slightly below the 75/150 nominal target, normal test-to-test scatter; individual
  Table 3 rows show δgmax scatter from 70 to 176.8 µm even within one nominal condition.
- **Frequencies**: 0.11, 1, 3, 5 Hz, all under constant NF; only **0.11 Hz** under variable NF ("due to
  technical aspects, i.e. control of the loading sequences" — the variable-NF actuator sequencing could
  not be run reliably at higher frequency). This asymmetry means the paper can show NF-waveform invariance
  only at 0.11 Hz, and frequency dependence only under constant NF — the two effects were never crossed
  in a full 2×2 (NF-shape × frequency) design.
- **Cycles**: 1000–15,000 (constant NF, frequency/duration sweep, series a/b); 1000–5000 (variable NF,
  series c).
- **Friction coefficient** (context, not itself a wear curve): from a separate constant-NF variable-
  displacement test (Fig. 5) used to locate the partial↔gross-slip transition: μt≈0.9 at the sliding
  transition, dropping to μstab≈0.7 once gross slip is established — this stabilized μ is what feeds the
  Q(t) used in the Ed integral for the main test series.

### Full Table 3 (test conditions + wear results — source of every CSV below)

| Test # | N cycles | f (Hz) | Condition | δgmax (µm) | ΣEd (J) | V (µm³) |
|---|---:|---:|---|---:|---:|---:|
| 1 | 10,000 | 5 | Constant | 176.8 | 17,200 | 1.81E+09 |
| 2 | n/a | n/a | n/a | n/a | n/a | n/a |
| 3 | 5000 | 5 | Constant | 134 | 7010 | 8.88E+08 |
| 4 | 7500 | 5 | Constant | 141 | 10,400 | 1.14E+09 |
| 5 | 1000 | 0.11 | Variable | 150 | 563 | 3.69E+08 |
| 6 | 1000 | 5 | Constant | 70 | 1130 | 1.17E+08 |
| 7 | 1000 | 0.11 | Constant | 155 | 1330 | 3.01E+07 |
| 8 | 1000 | 1 | Constant | 107 | 878 | 4.24E+08 |
| 9 | 1000 | 3 | Constant | 137.6 | 1410 | 2.92E+08 |
| 10 | 2500 | 0.11 | Variable | 76.8 | 968 | 5.46E+08 |
| 11 | 15,000 | 5 | Constant | 150.4 | 24,500 | 2.18E+09 |
| 12 | 5000 | 0.11 | Variable | 103 | 2920 | 1.26E+09 |
| 13 | 2500 | 0.11 | Constant | 138 | 3390 | 1.98E+09 |
| 14 | 5000 | 0.11 | Constant | 150 | 6670 | 3.61E+09 |

(Row 5's V and row 13's V are printed in the original PDF as "369E+08" and "l.98E+09" respectively —
confirmed by high-DPI crop to be typesetting defects in the source paper itself, not an extraction
artifact — transcribed above as the evidently-intended 3.69E+08 and 1.98E+09, consistent with every
other row's `X.XXE+0Y` format.)

## Wear behaviour

- **Energy-wear proportionality**: `V = αV · ΣEd` (Eq. 3) — wear volume scales linearly with accumulated
  dissipated energy, no offset, across all tested conditions.
- **Energy wear rate invariance vs. normal-force waveform** (the G2 headline): at fixed frequency
  (0.11 Hz), plotting V vs. cycles gives visibly different slopes for constant vs. variable NF (Fig. 9a —
  "the constant normal force condition promotes a wear kinetics nearly three times higher than variable
  normal force conditions"), but re-plotting the **same** tests' V vs. ΣEd instead of vs. cycles collapses
  both conditions onto **one single master line** (Fig. 9b): **αV = 534,900 µm³/J, R²=0.98**. I.e. the
  cycle-rate difference is fully explained by the variable-NF waveform dissipating less energy per cycle
  (contact spends part of each cycle at low/zero pressure), not by any change in the energy-to-wear
  conversion efficiency itself.
- **Effect of variable normal force + contact-opening sequence**: beyond the *quantitative* wear-rate
  effect above, the contact-opening sequence changes the wear **process** qualitatively — constant NF
  (closed interface) develops a three-zone scar with a titanium-nitride (TiOxNy) layer at the centre
  (oxygen-depletion-driven, confirmed by XRD/EDS, Figs. 12-14), whereas variable NF (opening interface,
  air/oxygen re-admitted each cycle) develops a **homogeneous oxide-only** scar with **no TiOxNy** at all —
  a generalized-oxidation mechanism instead of a localized-nitridation one. So: same energy-wear
  *coefficient*, different wear *mechanism/chemistry*.
- **Dissipated energy decreases under variable NF**: for matched cycle counts at 0.11 Hz, ΣEd for
  variable-NF tests is markedly lower than for constant-NF tests (e.g. at N=5000: 2920 J variable vs.
  6670 J constant — the constant case dissipates ~2.3× more energy over the same number of cycles; the
  fitted-slope comparison in text rounds this to "nearly three times").
- **Frequency effect (independent of, and larger than, the NF-waveform effect)**: comparing constant-NF
  tests at 0.11 Hz vs. 5 Hz (Fig. 10) gives **two different** energy-wear coefficients — αV=534,900 µm³/J
  at 0.11 Hz vs. **αV=97,500 µm³/J (R²=0.95) at 5 Hz** — i.e. increasing frequency by a factor of 45
  (0.11→5 Hz) reduces the energy wear rate by a factor of ~5 (534,900/97,500≈5.5). Mechanism proposed:
  lower frequency (slower sliding) gives oxygen more *time* to react with freshly exposed titanium,
  building a thicker, more wear-promoting oxide layer per unit dissipated energy — a tribo-oxidation
  kinetics effect, not a mechanical one. The authors explicitly warn that most fretting-wear laws are
  extracted at 5-20 Hz and would **underestimate** real (low-frequency, e.g. flight-cycle) wear rates.
  Variable-NF tests were only run at 0.11 Hz, so whether this frequency effect also holds under a variable
  normal-force waveform is explicitly left open by the authors ("dedicated investigations are currently
  underway").

## Main conclusions

1. Energy wear rate (`V = αV·ΣEd`) is **not dependent on the normal-force loading waveform** at fixed
   frequency — a single αV fits both constant and variable (contact-opening) normal-force sequences.
2. **Test frequency strongly controls the wear rate**: lower frequency → higher energy wear rate (factor
   ~5 reduction for a factor-45 frequency increase, 0.11→5 Hz), attributed to longer oxygen-titanium
   reaction time at low frequency (thicker oxide layer).
3. **The normal-force sequence controls interface structure/chemistry, not the energy-wear coefficient**:
   constant NF (closed contact) → progressive oxygen depletion → titanium-nitride formation at the scar
   centre; variable NF (contact-opening) → generalized homogeneous oxidation, no nitride.
4. Practical implication: conventional constant-NF fretting tests remain valid for extracting a
   *representative* energy wear rate for complex (variable-NF) blade-disk contacts, provided equivalent
   sliding speed/frequency is used — but must be run at realistically low (flight-representative)
   frequency, not the conventional 5-20 Hz, to avoid dangerously optimistic (underestimated) wear
   predictions.

## Curve inventory

All five CSVs below are **exact transcriptions of individual Table 3 test results** (ΣEd, V, N, per
test), not pixel-traced continuous curves — each plotted marker in Figs. 9/10 corresponds to one complete
fretting test, so there is no finer-grained underlying data to digitize. Point assignment to each
series/CSV was cross-validated by recomputing the through-origin least-squares slope of each candidate
point set and comparing to the paper's own reported αV/R²: the 4-point {1,3,4,11} vs. 5-point {1,3,4,6,11}
Δ-series both reproduce αV≈97,400-97,500 µm³/J closely (reported 97,500, R²=0.95), and the 5-point ×+□
combined 0.11 Hz set {5,10,12,13,14} reproduces αV≈535,300 µm³/J (reported 534,900, R²=0.98) — confirming
**Test 7 (N=1000, constant, 0.11 Hz) is excluded from both energy-based fits** (see caveats).

| Figure | Series | CSV filename | x quantity (unit) | y quantity (unit) | Table 3 tests | # pts |
|---|---|---|---|---|---|---|
| Fig. 9a | Constant NF, 0.11 Hz, δg*≈68 µm | `vanpeteghem2011wear_fig9a_constant_011hz.csv` | Number of cycles N (count) | Wear volume V (µm³) | 7, 13, 14 | 3 |
| Fig. 9a | Variable NF, 0.11 Hz, δg*≈68 µm | `vanpeteghem2011wear_fig9a_variable_011hz.csv` | Number of cycles N (count) | Wear volume V (µm³) | 5, 10, 12 | 3 |
| Fig. 9b | Constant NF, 0.11 Hz — part of the combined master-curve fit αV=534,900 µm³/J, R²=0.98 | `vanpeteghem2011wear_fig9b_constant_011hz.csv` | Dissipated energy ΣEd (J) | Wear volume V (µm³) | 13, 14 | 2 |
| Fig. 9b | Variable NF, 0.11 Hz — part of the same combined master-curve fit | `vanpeteghem2011wear_fig9b_variable_011hz.csv` | Dissipated energy ΣEd (J) | Wear volume V (µm³) | 5, 10, 12 | 3 |
| Fig. 10 | Constant NF, 5 Hz — separate fit αV=97,500 µm³/J, R²=0.95 | `vanpeteghem2011wear_fig10_constant_5hz.csv` | Dissipated energy ΣEd (J) | Wear volume V (µm³) | 1, 3, 4, 6, 11 | 5 |

Fig. 10 reuses the same `fig9b_constant_011hz` / `fig9b_variable_011hz` point sets for its (×)/(□) 0.11 Hz
series (plotted alongside the new (Δ) 5 Hz series on one combined axes to show the frequency contrast
directly) — not duplicated as separate files.

**Not digitized (context only, not wear/energy curves)**: Fig. 1 (blade-disk contact schematic), Fig. 2
(rig photo), Fig. 3 (loading-variable definitions schematic), Fig. 4 (P/δ/Q(t) loading-cycle schematics),
Fig. 5 (COF + sliding amplitude vs. cycle during the variable-displacement slip-transition test), Fig. 6
(Q-δ fretting loops, constant NF, two cycle counts), Fig. 7 (Q-δ fretting loops, variable NF), Fig. 8
(COF vs. cycle number for 3 conditions — tribological context, not a wear/energy quantity), Figs. 11-14
(optical/SEM/XRD/EDS scar characterization — chemistry/structure, not digitizable x,y wear data).

## V2 mapping

- **Pressure-history dependence ↔ conformance-gate provenance**: this paper is direct, quantitative
  evidence that an energy-integral state variable (`ΣEd`, itself accumulated from an instantaneous
  Q(t)·δ(t) that is zero/near-zero whenever contact pressure is zero/near-zero) reproduces the *same*
  wear-per-unit-energy law regardless of whether normal force/pressure is held constant or cycled through
  a full ramp-plateau-opening sequence. This directly supports BAS V2's pressure-dependent conformance
  gate design (`W_conf_ref`/`conform_driver="effective"`, CLAUDE.md §7/§4.9): the gate's job is to track
  accumulated contact work under a *time-varying* pressure/preload signal, and this paper shows that such
  an energy-history-based accounting is exactly what collapses two very different normal-force histories
  onto one physical law — i.e. it is evidence FOR putting the pressure-history dependence into an energy
  channel rather than into a separate empirical normal-force-shape multiplier.
- **α ↔ k_wear_spec**: `αV` [µm³/J] here plays the same conceptual role as BAS V2's `k_wear_spec = K/H`
  [1/Pa] (§4.42a merge) — both are energy(or Archard)-normalized wear-rate constants meant to be
  identifiable independent of the loading waveform. This paper's clean demonstration that αV is
  **NF-waveform-invariant but strongly frequency/oxidation-kinetics-dependent** (factor ~5.5 across the
  tested frequency range) is a caution for any single canonical `k_wear_spec`: it should be expected to
  carry its own frequency/environment dependence per material pair, same "constants are per-pair, forms
  transfer" pattern already documented for `C_creep` (§4.7) and `emb_depth` (§4.6/roadmap item 9) — this
  paper is a second, independent (fretting-wear rather than bolt-loosening) confirmation of that pattern,
  this time isolating **frequency/dwell-time** rather than **contact geometry** as the per-condition lever.
- **Ti = G8**: Table 1's Ti-6Al-4V properties (E=119 GPa, ν=0.29, σy=970 MPa, HV0.3=360) and the αV values
  above are the first titanium-specific energy-wear numbers in this round's library — usable as a sanity
  range if a titanium bolted-joint case is ever added, but NOT a substitute for a titanium **bolted-joint**
  calibration (no preload/clamping-force data exists in this paper at all).
- **Not directly usable**: because there is no bolt, no preload, and no F/F0 curve, this paper cannot seed
  a `joint_calibrations.json` profile or a `validation_cases.py` entry by itself — its contribution is
  qualitative/mechanistic provenance (gate design justification) plus a titanium αV reference point, not a
  fittable preload-decay curve.

## Digitization caveats

- **Sparse, discrete points, not a dense pixel-traced curve.** Every (x,y) pair above is one full fretting
  test's exact reported (ΣEd or N, V) values from Table 3, cross-validated against marker positions in
  Figs. 9/10 (not independently pixel-picked with sub-test resolution) — accuracy is limited only by the
  paper's own reporting precision (3 significant figures), not by digitization/reading error. This is why
  each CSV has only 2-5 points rather than the 10-40 typical of a continuously-sampled curve; there is no
  finer-grained data to extract.
- **Test 7 exclusion is an inference, not a stated fact.** The paper does not explicitly say Test 7
  (N=1000, constant NF, 0.11 Hz, ΣEd=1330 J, V=3.01E7 µm³ — anomalously low wear for its energy, likely
  related to the "tangential force peak during the first cycles" transient described in Section 3.1 for
  short constant-NF tests) is excluded from the Fig. 9b/10 linear fits. It was excluded here because (a)
  visually no low-lying outlier point is distinguishable near (1330, 3E7) in the high-DPI crop of Fig. 9b,
  and (b) recomputing the through-origin least-squares slope **without** Test 7 reproduces the paper's
  stated αV/R² closely, while including it would pull the fit down and degrade R² noticeably below 0.98.
  Test 7 IS included in Fig. 9a's constant-NF vs.-cycles series (its (1000, 3.01E7) point sits
  indistinguishably close to the plotted origin marker on that linear-µm³ axis, consistent either way).
- **Two source-paper typesetting defects, corrected in transcription** (confirmed via a 350 dpi crop, not
  an extraction/OCR artifact on our end): Table 3 row 5's V is printed "369E+08" (missing decimal point)
  and row 13's V is printed "l.98E+09" (lowercase "L" for "1"). Both corrected to 3.69E+08 and 1.98E+09
  respectively, consistent with every other row's format and with the Fig. 9/10 marker positions.
- **δgmax scatter across nominally-equivalent tests** (70-176.8 µm within tests all described by the
  paper as approximately the same δg* condition) was not reconciled further — treated as normal
  test-to-test compliance/wear-groove variability, per the paper's own framing ("similar relative sliding
  strokes... similar mean sliding speeds").
- Units: wear volume V is in **µm³ (cubic micrometres)**, confirmed both from the Fig. 9/10 y-axis label
  ("Wear volume (µm³)") and from order-of-magnitude sanity (a ~1 mm³ scar volume over an 8 mm × ~1-2 mm ×
  ~0.1 mm scar is physically reasonable) — Table 3's printed column header "V (m³)" is the same
  µ-stripping typesetting defect as above, NOT literal cubic metres.
- No frequency/variable-NF cross data exists (variable NF was only run at 0.11 Hz) — do not extrapolate
  the ~5.5× frequency effect onto variable-NF conditions; the paper itself declines to do so.
