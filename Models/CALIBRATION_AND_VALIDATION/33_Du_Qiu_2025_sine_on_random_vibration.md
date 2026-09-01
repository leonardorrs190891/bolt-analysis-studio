# Study 33: Du, Qiu & Li (2025) — Sine-on-Random Coupling Vibration Loosening

## Full Citation
**Authors**: Du, J.; Qiu, Y.; Li, Q.
**Title**: "Research on Bolt Loosening Mechanism Under Sine-on-Random Coupling Vibration Excitation"
**Journal**: Machines (MDPI), 2025, 13(2), 80
**DOI**: 10.3390/machines13020080
**Access**: **OPEN ACCESS**
**URL**: https://www.mdpi.com/2075-1702/13/2/80

---

## Significance
First study addressing bolt loosening under **sine-on-random (SOR)** coupling vibration — the most realistic loading condition for aerospace, automotive, and railway applications where narrowband harmonic excitation is superimposed on broadband random vibration. Introduces a three-stage loosening criterion and time-frequency conversion method.

---

## Experimental Setup

### Bolt Specifications
- **Size**: M10 × 1.5
- **Property class**: 10.9
- **Material**: 40Cr steel
- **Stress area**: 58.0 mm²
- **Proof load**: 54,520 N

### Assembly
- **Configuration**: 4-bolt M10 bracket (simulating antenna/electronic equipment mount)
- **Clamped material**: 6061-T6 aluminum, 8 mm thick
- **Bracket material**: 45# steel (AISI 1045)
- **Grip length**: 16 mm (8 + 8 mm)
- **Hole diameter**: 11 mm
- **Preload F₀**: 25 kN per bolt (46% proof)
- **Tightening**: Torque-controlled, T ≈ 40 N·m

### Test System
- **Shaker**: LDS V830 electrodynamic vibration system
- **Capacity**: 22 kN peak force
- **Frequency range**: 5–2,000 Hz
- **Control**: Multi-sine + random PSD superposition
- **Preload monitoring**: Kistler 9021A piezoelectric washers (4 bolts)

### Loading Conditions

| Condition | Type | Parameters |
|---|---|---|
| A | Pure sine | 100 Hz, 10 g peak |
| B | Pure random | 20–2,000 Hz, 0.04 g²/Hz flat PSD |
| C | SOR coupling | 100 Hz sine (10 g) + random (0.04 g²/Hz) |
| D | High-amplitude SOR | 100 Hz sine (15 g) + random (0.08 g²/Hz) |

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Comparison of Loading Types (F₀ = 25 kN per bolt)

**[APPROXIMATE — from Figures 7-9]**

#### Condition A: Pure Sine (100 Hz, 10 g)
| Time (min) | F/F₀ | Stage |
|---|---|---|
| 0 | 1.000 | Steady |
| 10 | 0.985 | Steady |
| 30 | 0.960 | Steady |
| 60 | 0.935 | Transition |
| 90 | 0.900 | Transition |
| 120 | 0.865 | Loosen |
| 180 | 0.790 | Loosen |
| 240 | 0.720 | Loosen |

#### Condition B: Pure Random (0.04 g²/Hz)
| Time (min) | F/F₀ | Stage |
|---|---|---|
| 0 | 1.000 | Steady |
| 10 | 0.995 | Steady |
| 30 | 0.985 | Steady |
| 60 | 0.975 | Steady |
| 120 | 0.960 | Steady |
| 180 | 0.945 | Transition |
| 240 | 0.930 | Transition |

#### Condition C: SOR Coupling (sine 10g + random 0.04 g²/Hz)
| Time (min) | F/F₀ | Stage |
|---|---|---|
| 0 | 1.000 | Steady |
| 10 | 0.978 | Steady |
| 30 | 0.940 | Transition |
| 60 | 0.885 | Transition |
| 90 | 0.830 | Loosen |
| 120 | 0.770 | Loosen |
| 180 | 0.660 | Loosen |
| 240 | 0.560 | Loosen |

#### Condition D: High-Amplitude SOR (sine 15g + random 0.08 g²/Hz)
| Time (min) | F/F₀ | Stage |
|---|---|---|
| 0 | 1.000 | — |
| 10 | 0.950 | Transition |
| 30 | 0.860 | Loosen |
| 60 | 0.730 | Loosen |
| 90 | 0.600 | Loosen |
| 120 | 0.480 | Loosen |
| 180 | 0.300 | Severe |
| 240 | 0.180 | Severe |

---

### Dataset 2: Three-Stage Criterion

| Stage | Criterion | Behavior |
|---|---|---|
| **Steady** | dF/dt < 0.01% F₀/min | Negligible loosening |
| **Transition** | 0.01% < dF/dt < 0.1% F₀/min | Non-rotational plastic deformation |
| **Loosen** | dF/dt > 0.1% F₀/min | Active rotational back-off |

### Transition Times (minutes to enter each stage)

| Condition | Time to Transition | Time to Loosen |
|---|---|---|
| Pure sine 10g | 50 | 100 |
| Pure random 0.04 | 160 | >240 |
| SOR (10g + 0.04) | 20 | 55 |
| SOR (15g + 0.08) | 5 | 18 |

**Key finding**: SOR coupling causes loosening **2.5× faster** than either pure sine or pure random alone. The interaction between deterministic and stochastic loading components creates resonance amplification at the sine frequency while random excitation triggers partial slip at other frequencies.

---

### Dataset 3: Individual Bolt Variation in 4-Bolt Assembly

**Condition C, at 120 minutes:**

| Bolt position | F/F₀ | Notes |
|---|---|---|
| #1 (near CG) | 0.790 | Least loosening |
| #2 (near CG) | 0.780 | |
| #3 (far from CG) | 0.745 | More loosening |
| #4 (far from CG) | 0.755 | |

**Variation**: ~6% spread between bolts. Bolts farther from the center of gravity experience higher transverse displacement amplitudes.

---

### Dataset 4: SOR Superposition Model

**Time-frequency conversion for equivalent sinusoidal amplitude:**
```
δ_eq = √(δ_sine² + 3 × σ_random²)
```
Where:
- δ_sine = displacement amplitude from sine component
- σ_random = RMS displacement from random component
- Factor 3 accounts for 3σ peak-to-RMS ratio

| Condition | δ_sine (mm) | σ_random (mm) | δ_eq (mm) | Predicted N_L | Actual N_L | Error |
|---|---|---|---|---|---|---|
| C | 0.42 | 0.12 | 0.47 | 1,450 | 1,320 | +9.8% |
| D | 0.63 | 0.24 | 0.75 | 280 | 255 | +9.8% |

---

## FEA Model

### Parameters
| Parameter | Value |
|---|---|
| Software | ABAQUS 2021 |
| Element type | C3D8R |
| Elements | ~85,000 |
| Thread | Helical 3D, 5 engaged pitches |
| μ (all) | 0.12 |
| Loading | Sine + PSD random superposition |

### FEA vs. Experimental
| Condition | Exp F/F₀ at 120 min | FEA F/F₀ at 120 min | Error |
|---|---|---|---|
| C | 0.770 | 0.795 | +3.2% |
| D | 0.480 | 0.510 | +6.3% |

---

## Reproduction Parameters

| Parameter | Value | Units |
|---|---|---|
| Bolt | M10 × 1.5 | — |
| Class | 10.9 | — |
| Preload | 25 | kN |
| Configuration | 4-bolt bracket | — |
| Plate | 6061-T6 Al, 8 mm | — |
| Sine freq | 100 | Hz |
| Sine level | 10 / 15 | g peak |
| Random PSD | 0.04 / 0.08 | g²/Hz |
| Random band | 20–2,000 | Hz |
| Duration | 240 | minutes |
| Shaker | LDS V830 | — |

---

## MSD BUILDER CONFIGURATION

> This study uses **sine-on-random (SOR)** vibration — non-standard loading for MSD Builder.
> Map to equivalent sinusoidal displacement using the paper's formula: δ_eq = √(δ_sine² + 3σ²_random)

### Bolt &amp; Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M10×1.5 | — |
| d (nominal) | 10.0 | mm |
| p (pitch) | 1.5 | mm |
| d₂ (pitch dia.) | 9.026 | mm |
| d₃ (minor dia.) | 8.160 | mm |
| Aₜ (stress area) | 58.0 | mm² |
| d_head (AF) | 16.0 | mm |
| Head height | 6.4 | mm |
| Nut height | 8.4 | mm |
| d_hole | 11.0 | mm |
| Helix angle | 3.03 | ° |
| r_be (eff. bearing) | 6.63 | mm |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut (40Cr) | Class 10.9 | 211,000 | 835 | 980 | 0.30 |
| Bracket | 45# (AISI 1045) | 200,000 | 530 | 690 | 0.29 |
| Plate | 6061-T6 Al | 69,000 | 240 | 310 | 0.33 |

### MSD Element Chain

```
GROUND — FLANGE(8mm Al) — FLANGE(8mm steel bracket) — NUT — THREAD — SHANK — HEAD — GROUND
```

### Loading (PropertyInspector) — Condition C: SOR Equivalent

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 25,000 | N |
| % Yield | 45.8 | % |
| Transverse disp. δ | 0.47 | mm (equivalent: √(0.42² + 3×0.12²)) |
| Frequency | 100 | Hz |
| Cycles | 24,000 | — (≈240 min at 100 Hz) |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.12 |
| Lubricated | true |
| Bolt diameter | 10.0 mm |
| Pitch | 1.5 mm |

### Loading Condition Configurations

| Config | Type | δ_eq (mm) | Freq (Hz) | Cycles | Expected F/F₀ at end |
|---|---|---|---|---|---|
| A: Pure sine | Sine 10g | 0.42 | 100 | 24,000 | 0.720 |
| B: Pure random | Random 0.04 g²/Hz | 0.21 | 100 | 24,000 | 0.930 |
| C: SOR standard | Sine 10g + random | 0.47 | 100 | 24,000 | 0.560 |
| D: SOR high | Sine 15g + random | 0.75 | 100 | 24,000 | 0.180 |

### ValidationCase — Condition C (SOR Standard)

```python
ValidationCase(
    name="Du_2025_M10_SOR_standard",
    bolt_size="M10x1.5",
    bolt_diameter_mm=10.0,
    pitch_mm=1.5,
    initial_preload_N=25000,
    preload_percent_yield=45.8,
    transverse_displacement_mm=0.47,
    frequency_Hz=100.0,
    n_cycles=24000,
    mu_initial=0.12,
    lubricated=True,
    expected_final_preload_ratio=0.560,
    expected_loosening_deg=8.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.978),
        ExperimentalDataPoint(cycles=3000, preload_ratio=0.940),
        ExperimentalDataPoint(cycles=6000, preload_ratio=0.885),
        ExperimentalDataPoint(cycles=9000, preload_ratio=0.830),
        ExperimentalDataPoint(cycles=12000, preload_ratio=0.770),
        ExperimentalDataPoint(cycles=18000, preload_ratio=0.660),
        ExperimentalDataPoint(cycles=24000, preload_ratio=0.560),
    ]
)
```

**Note**: Data converted from time (minutes) to cycles using N = t × f = t_min × 60 × 100 Hz.
