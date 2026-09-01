# Study 10: Yang, Jeong & Lim (2023) — Phenomenological Model for Bolt Loosening

## Full Citation
**Authors**: Yang, G. S.; Jeong, C. Y.; Lim, T. S.
**Title**: "A Phenomenological Model for Bolt Loosening Characteristics in Bolted Joints Under Cyclic Loading"
**Journal**: International Journal of Precision Engineering and Manufacturing, 2023, 24, 825–835
**DOI**: 10.1007/s12541-023-00783-x

---

## Experimental Setup

### Bolt Specifications

#### Configuration A: M6 bolts
- **Size**: M6 × 1.0 × 65 mm
- **Property class**: 10.9
- **Stress area**: 20.1 mm²
- **Yield**: 940 MPa
- **Pitch**: 1.0 mm

#### Configuration B: M8 bolts
- **Size**: M8 × 1.25 × 65 mm
- **Property class**: 10.9
- **Stress area**: 36.6 mm²
- **Yield**: 940 MPa
- **Pitch**: 1.25 mm

### Test Machine
- **Type**: Junker vibration test machine (DIN 65151 compatible)
- **Displacement measurement**: LVDT
- **Preload measurement**: Piezoelectric load cell
- **Nut rotation**: Optical encoder

### Test Parameters — M8

| Parameter | Values |
|---|---|
| Initial clamping force F₀ | 14,300 N (14.3 kN) |
| Displacement amplitudes | 0.18, 0.25, 0.35, 0.45, 0.55, 0.65 mm |
| Frequency | 12.5 Hz |
| Cycles | Up to 2,000 |

### Test Parameters — M6

| Parameter | Values |
|---|---|
| Initial clamping force F₀ | 8,500 N (8.5 kN) |
| Displacement amplitudes | 0.15, 0.20, 0.30, 0.40, 0.50 mm |
| Frequency | 12.5 Hz |
| Cycles | Up to 2,000 |

---

## DATA FOR CURVE PLOTTING

### Dataset 1: M8 Normalized Clamping Force Decay

**[APPROXIMATE — digitized from published figures]**

#### δ = 0.18 mm (below threshold)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 100 | 0.975 |
| 500 | 0.950 |
| 1,000 | 0.940 |
| 2,000 | 0.930 |

#### δ = 0.25 mm
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.940 |
| 100 | 0.900 |
| 200 | 0.840 |
| 500 | 0.740 |
| 1,000 | 0.640 |
| 2,000 | 0.520 |

#### δ = 0.35 mm
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.900 |
| 20 | 0.840 |
| 50 | 0.720 |
| 100 | 0.560 |
| 200 | 0.380 |
| 500 | 0.150 |
| 1,000 | 0.050 |

#### δ = 0.45 mm
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.880 |
| 10 | 0.780 |
| 20 | 0.620 |
| 50 | 0.360 |
| 100 | 0.160 |
| 200 | 0.050 |

#### δ = 0.55 mm
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.820 |
| 10 | 0.660 |
| 20 | 0.440 |
| 50 | 0.180 |
| 100 | 0.050 |

#### δ = 0.65 mm
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 2 | 0.780 |
| 5 | 0.580 |
| 10 | 0.360 |
| 20 | 0.160 |
| 50 | 0.030 |

---

### Dataset 2: M6 Normalized Clamping Force Decay

#### δ = 0.15 mm (below threshold)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 500 | 0.955 |
| 1,000 | 0.940 |
| 2,000 | 0.925 |

#### δ = 0.30 mm
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.880 |
| 20 | 0.800 |
| 50 | 0.620 |
| 100 | 0.420 |
| 200 | 0.220 |
| 500 | 0.060 |

#### δ = 0.50 mm
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 2 | 0.750 |
| 5 | 0.520 |
| 10 | 0.300 |
| 20 | 0.120 |
| 50 | 0.020 |

---

### Dataset 3: D-N Loosening Life Curves (Both Sizes)

**Loosening life N_L defined as F = 0.10 × F₀**

#### M8 (F₀ = 14.3 kN)
| δ (mm) | N_L (cycles) |
|---|---|
| 0.18 | >10,000 (threshold) |
| 0.25 | ~3,500 |
| 0.35 | ~700 |
| 0.45 | ~180 |
| 0.55 | ~70 |
| 0.65 | ~25 |

#### M6 (F₀ = 8.5 kN)
| δ (mm) | N_L (cycles) |
|---|---|
| 0.15 | >10,000 (threshold) |
| 0.20 | ~4,000 |
| 0.30 | ~400 |
| 0.40 | ~100 |
| 0.50 | ~30 |

---

## Phenomenological Model

### Universal Loosening Life Equation
All data from both bolt sizes collapsed to a single power-law relationship:

```
N_L = C × (Δd)^(-m)
```

Where:
- N_L = loosening life (cycles to 10% preload)
- Δd = transverse displacement amplitude (mm)
- C = material/joint constant
- m = exponent (slope in log-log plot)

**Fitted parameters**:
- For M8: C ≈ 10.5, m ≈ 3.8
- For M6: C ≈ 5.2, m ≈ 3.5
- **Universal (both sizes normalized)**: C ≈ 8.0, m ≈ 3.65

### Normalized Decay Curve
When plotting F/F₀ vs. N/N_L, all curves for both bolt sizes collapse to a **single master curve**:

```
F/F₀ = 1 - (N/N_L)^n
```

Where n ≈ 0.6–0.8 (shape parameter).

Alternatively, using an exponential:
```
F/F₀ = exp(-k × (N/N_L)^n)
```
With k ≈ 2.3 and n ≈ 0.7.

### Master Curve Data Points

| N/N_L | F/F₀ (master curve) |
|---|---|
| 0.00 | 1.000 |
| 0.01 | 0.950 |
| 0.02 | 0.920 |
| 0.05 | 0.850 |
| 0.10 | 0.760 |
| 0.20 | 0.600 |
| 0.30 | 0.460 |
| 0.40 | 0.340 |
| 0.50 | 0.240 |
| 0.60 | 0.160 |
| 0.70 | 0.100 |
| 0.80 | 0.060 |
| 0.90 | 0.030 |
| 1.00 | 0.010 |

This master curve means: once you know N_L for a given amplitude (from the D-N curve), you can generate the complete decay curve for any condition.

---

## Reproduction Notes

| Parameter | M6 | M8 |
|---|---|---|
| Bolt length (total) | 65 mm | 65 mm |
| Grip length | ~25 mm (est.) | ~25 mm (est.) |
| Head across flats | 10 mm | 13 mm |
| Nut height | 5.2 mm | 6.5 mm |
| Frequency | 12.5 Hz | 12.5 Hz |
| Waveform | Sinusoidal | Sinusoidal |
| Surface condition | Standard (unlubricated) | Standard (unlubricated) |
| Estimated μ | 0.15–0.20 | 0.15–0.20 |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this experiment.
> Two bolt sizes — create separate models for M6 and M8.

### M8 Configuration (Primary)

#### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M8×1.25 | — |
| d (nominal) | 8.0 | mm |
| p (pitch) | 1.25 | mm |
| d₂ (pitch dia.) | 7.188 | mm |
| d₃ (minor dia.) | 6.466 | mm |
| Aₜ (stress area) | 36.6 | mm² |
| d_head (AF) | 13.0 | mm |
| Head height | 5.3 | mm |
| Nut height | 6.5 | mm |
| d_hole | 9.0 | mm |
| Grip length | 25.0 | mm (estimated) |
| Helix angle | 3.17 | ° |

#### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 Q&T | 210,000 | 940 | 1,040 | 0.3 |
| Plates | Steel | 210,000 | — | — | 0.3 |

#### Loading — DIN 65151 Junker Test

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 14,300 | N |
| % Yield | 41.6 | % |
| Transverse disp. δ | 0.65 | mm |
| Frequency | 12.5 | Hz |
| Cycles | 2,000 | — |

#### Friction

| Parameter | Value |
|---|---|
| μ_initial | 0.18 |
| Lubricated | false |

### M6 Configuration

| Parameter | Value |
|---|---|
| Bolt size | M6×1.0 |
| d=6.0, p=1.00, d₂=5.350, d₃=4.773, Aₜ=20.1 mm² |
| d_head=10.0, h_head=4.0, h_nut=5.2, d_hole=6.6 mm |
| F₀ = 8,500 N (44.8% yield) |
| δ = 0.50 mm, f = 12.5 Hz |
| μ_initial = 0.18, Lubricated = false |

### Amplitude Test Matrix

| Bolt | δ (mm) | Expected N_L (F=0.10×F₀) |
|---|---|---|
| M8 | 0.18 | >10,000 (threshold) |
| M8 | 0.25 | ~3,500 |
| M8 | 0.35 | ~700 |
| M8 | 0.45 | ~180 |
| M8 | 0.55 | ~70 |
| M8 | 0.65 | ~25 |
| M6 | 0.15 | >10,000 (threshold) |
| M6 | 0.30 | ~400 |
| M6 | 0.50 | ~30 |

### ValidationCase — M8 at 0.65mm (for validation_cases.py)

```python
ValidationCase(
    name="Yang_2023_M8_Junker",
    bolt_size="M8x1.25",
    bolt_diameter_mm=8.0,
    pitch_mm=1.25,
    initial_preload_N=14300,
    preload_percent_yield=41.6,
    transverse_displacement_mm=0.65,
    frequency_Hz=12.5,
    n_cycles=50,
    mu_initial=0.18,
    lubricated=False,
    expected_final_preload_ratio=0.03,
    expected_loosening_deg=12.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=2, preload_ratio=0.780),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.580),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.360),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.160),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.030),
    ]
)
```
