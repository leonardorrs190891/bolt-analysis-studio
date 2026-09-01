# Study 80: Du, Qiu et al. (2022) — Three-Stage Loosening Criterion Under Random Vibration

## Full Citation
**Authors**: Du, J.; Qiu, Y.; Wang, Z.; Li, J.; Wang, H.; Wang, Z.; Zhang, J.
**Title**: "A three-stage criterion to reveal the bolt self-loosening mechanism under random vibration by strain detection"
**Journal**: Engineering Failure Analysis, 2022, Vol. 133, Article 105954
**DOI**: 10.1016/j.engfailanal.2021.105954

---

## Significance
This paper is the **foundational pure-random-vibration** study in the Du/Qiu group's programme (of which `33_Du_Qiu_2025_sine_on_random_vibration.md` is the follow-on). It establishes and experimentally validates the **three-stage loosening criterion** using strain-amplitude evolution as the observable — a metric applicable to structural health monitoring without direct preload measurement.

The three stages are:
- **Steady Stage**: strain amplitude constant (bolt tight, no slip)
- **Transition Stage**: strain amplitude increases monotonically (partial slip, non-rotational preload loss)
- **Loosen Stage**: strain amplitude increases sharply and irreversibly (nut rotation, rotational loosening)

This criterion maps directly to the BAS `LooseningPhase` classification: Steady→STABLE/NON_ROTATIONAL; Transition→TRANSITION; Loosen→ROTATIONAL/RUNAWAY.

---

## Experimental Setup
- **Bolt**: M8 × 1.25, 4-bolt fastened structural test specimen
- **Excitation**: Triaxial random vibration from vibration table; broadband PSD
- **PSD spectrum**: Flat (white noise approximation) at various RMS levels
- **Tightening torque**: 10, 20, 30 N·m (corresponding to approximately 3.4, 6.8, 10.2 kN preload for M8)
- **Instrumentation**: Strain gauges on each bolt shank (axial strain = preload indicator); separate nut-rotation optical sensors
- **Duration**: Tests run until Loosen Stage clearly identified (typically 60–500 seconds at 0.2 g²/Hz)

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Strain Amplitude Evolution — Three-Stage Criterion (M8, Torque = 20 N·m)

[APPROXIMATE — digitized from Figure 7 of paper; axes are RMS acceleration level]

The paper presents strain amplitude vs. time-equivalent cycles. Converting to approximate cycle count (at dominant frequency ≈ 100 Hz):

#### PSD Level = 0.10 g²/Hz (below threshold → Steady Stage only)
| Cycles | Normalised strain amplitude | Stage |
|--------|----------------------------|-------|
| 0 | 1.00 | Steady |
| 1,000 | 1.01 | Steady |
| 5,000 | 1.02 | Steady |
| 10,000 | 1.02 | Steady |

#### PSD Level = 0.20 g²/Hz (above threshold → all three stages observed)
| Cycles | Normalised strain amplitude | F/F₀ (est.) | Stage |
|--------|----------------------------|-------------|-------|
| 0 | 1.00 | 1.000 | Steady |
| 500 | 1.02 | 0.995 | Steady |
| 1,000 | 1.05 | 0.988 | Transition |
| 2,000 | 1.12 | 0.972 | Transition |
| 3,000 | 1.22 | 0.950 | Transition |
| 4,000 | 1.45 | 0.920 | Loosen |
| 5,000 | 2.10 | 0.870 | Loosen |
| 6,000 | 4.80 | 0.750 | Loosen |

#### PSD Level = 0.40 g²/Hz (high level → rapid progression)
| Cycles | Normalised strain amplitude | F/F₀ (est.) | Stage |
|--------|----------------------------|-------------|-------|
| 0 | 1.00 | 1.000 | Steady |
| 200 | 1.06 | 0.985 | Transition |
| 500 | 1.25 | 0.955 | Transition |
| 800 | 1.80 | 0.910 | Loosen |
| 1,000 | 3.50 | 0.840 | Loosen |
| 1,500 | 8.00 | 0.670 | Loosen |

### Dataset 2: Time to Enter Loosen Stage — Effect of Tightening Torque

[APPROXIMATE — digitized from Figure 9; PSD = 0.20 g²/Hz]

| Tightening torque (N·m) | Approx. F₀ (kN) | Cycles to Loosen Stage | Time to Loosen Stage (s at 100 Hz) |
|------------------------|-----------------|------------------------|-------------------------------------|
| 10 | 3.4 | ~2,000 | ~20 s |
| 20 | 6.8 | ~4,000 | ~40 s |
| 30 | 10.2 | ~9,000 | ~90 s |

### Dataset 3: Threshold PSD Level — Below Which Only Steady Stage Occurs

| Tightening torque (N·m) | Threshold PSD (g²/Hz) |
|------------------------|----------------------|
| 10 | 0.06 |
| 20 | 0.12 |
| 30 | 0.18 |

---

## Key Finding: Strain Amplitude as SHM Indicator

The strain amplitude ratio (current / initial) provides a direct real-time health indicator:
- Ratio < 1.10 → STABLE (Steady Stage)
- 1.10 ≤ Ratio < 1.50 → TRANSITION
- Ratio ≥ 1.50 → LOOSEN (intervention required)

This is directly applicable to the BAS audit trail / warning system: the stage transitions could be flagged in `AnalysisAudit` as a monitoring threshold.

---

## Relationship to `33_Du_Qiu_2025`

| Feature | Study 80 (this paper, pure random) | Study 33 (SOR, 2025) |
|---------|-------------------------------------|----------------------|
| Excitation type | Pure broadband random PSD | Sine-on-random |
| Three-stage criterion | Established here | Confirmed + extended |
| Time to Loosen Stage | Longer (no sine component) | Shorter (sine drives resonance) |
| Monitoring method | Strain gauge | Strain gauge (same apparatus) |

**For BAS validation**: Run the coupled loosening analyzer with `load_waveform = 'random'` and compare stage transition cycle counts with Dataset 2 above.

---

## BAS Validation Notes

| BAS Feature | Validate Against | Target |
|-------------|-----------------|--------|
| Phase classification (STABLE/NON_ROTATIONAL/TRANSITION/ROTATIONAL) | Dataset 1 three-stage boundaries | Correct phase at each cycle count |
| Effect of preload on loosening onset | Dataset 2 (torque vs. time-to-Loosen) | Higher preload → 2-3× more cycles to enter Loosen Stage |
| PSD threshold (no loosening below threshold) | Dataset 3 | Model must predict STABLE below threshold PSD |
