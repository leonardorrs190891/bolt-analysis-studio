# Study 03: Zhang, Jiang, Park & Lee (2006) — Clamped Length and Loading Direction Effects

## Full Citation
**Authors**: Zhang, M.; Jiang, Y.; Park, T.-W.; Lee, C.-H.
**Title**: "An Experimental Investigation of the Effects of Clamped Length and Loading Direction on Self-Loosening of Bolted Joints"
**Journal**: ASME Journal of Pressure Vessel Technology, 2006, 128(3), 388–393
**DOI**: 10.1115/1.2218342

---

## Experimental Setup

### Bolt Specifications
- **Size**: M12 × 1.75 (identical to Jiang 2003/2004 studies)
- **Property class**: 10.9
- **Material**: Alloy steel, quenched and tempered
- **Stress area**: 84.3 mm²
- **Proof load**: 83,200 N

### Nut & Washer
- Standard hex nut, Class 10
- Hardened flat washers on both sides

### Clamped Members
- **Material**: AISI 1045 steel, normalized
- **Surface**: Ground, clean
- **Variable**: Plate thickness varied to change grip length

### Test Machine
- Same custom transverse vibration machine as Jiang 2003/2004
- Strain-gauged bolts for preload measurement
- Angular position sensor for nut rotation

---

## Test Matrix

### Variable: Clamped Length
| Configuration | Grip length l_c (mm) | l_c / d ratio | Plate setup |
|---|---|---|---|
| Short | 12.7 | 1.06 | 1 × 12.7 mm plate |
| Standard | 25.4 | 2.12 | 2 × 12.7 mm plates |
| Long | 38.1 | 3.18 | 3 × 12.7 mm plates |
| Extra long | 50.8 | 4.23 | 4 × 12.7 mm plates |

### Variable: Loading Direction
| Direction | Description |
|---|---|
| Pure transverse | Displacement perpendicular to bolt axis (standard Junker-type) |
| 30° from transverse | Combined: 87% transverse + 50% axial components |
| 45° from transverse | Equal transverse and axial components |
| 60° from transverse | Combined: 50% transverse + 87% axial |
| Pure axial | Displacement along bolt axis only |

### Common Parameters
- **Preload F₀**: 25,000 N (standard); also 41,000 N
- **Displacement amplitude**: 0.46 mm (0.018")
- **Frequency**: 5 Hz

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Effect of Clamped Length (δ = 0.46 mm, F₀ = 25 kN, pure transverse)

**[APPROXIMATE — digitized from published Figure 4]**

#### l_c = 12.7 mm (l/d = 1.06) — Short grip
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 25,000 | 1.000 |
| 5 | 20,000 | 0.800 |
| 10 | 16,000 | 0.640 |
| 20 | 10,000 | 0.400 |
| 50 | 3,500 | 0.140 |
| 100 | 1,000 | 0.040 |

#### l_c = 25.4 mm (l/d = 2.12) — Standard grip
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 25,000 | 1.000 |
| 5 | 23,500 | 0.940 |
| 10 | 22,000 | 0.880 |
| 20 | 19,500 | 0.780 |
| 50 | 14,000 | 0.560 |
| 100 | 8,500 | 0.340 |
| 200 | 3,000 | 0.120 |

#### l_c = 38.1 mm (l/d = 3.18) — Long grip
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 25,000 | 1.000 |
| 10 | 23,000 | 0.920 |
| 20 | 21,500 | 0.860 |
| 50 | 18,000 | 0.720 |
| 100 | 14,000 | 0.560 |
| 200 | 9,000 | 0.360 |
| 300 | 5,500 | 0.220 |
| 500 | 2,500 | 0.100 |

#### l_c = 50.8 mm (l/d = 4.23) — Extra long grip
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 25,000 | 1.000 |
| 10 | 24,000 | 0.960 |
| 20 | 23,000 | 0.920 |
| 50 | 21,000 | 0.840 |
| 100 | 18,500 | 0.740 |
| 200 | 15,000 | 0.600 |
| 300 | 12,000 | 0.480 |
| 500 | 7,500 | 0.300 |

**Key finding**: Increasing grip length significantly retards loosening. At l/d > 4.5, loosening rate is dramatically reduced. This is because longer bolts are more flexible (lower axial stiffness k_b), allowing more elastic energy absorption before joint slips.

### Cycles to 50% Preload Loss vs. l/d Ratio
| l/d ratio | Cycles to F = 0.5·F₀ |
|---|---|
| 1.06 | ~15 |
| 2.12 | ~65 |
| 3.18 | ~175 |
| 4.23 | ~350 |

---

### Dataset 2: Effect of Loading Direction (l_c = 25.4 mm, δ = 0.46 mm, F₀ = 25 kN)

**[APPROXIMATE — digitized from published Figure 6]**

#### Pure transverse (0° from transverse)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.560 |
| 100 | 0.340 |
| 200 | 0.120 |
| 300 | 0.060 |

#### 30° from transverse
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.680 |
| 100 | 0.480 |
| 200 | 0.260 |
| 300 | 0.150 |
| 500 | 0.060 |

#### 45° from transverse
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.780 |
| 100 | 0.640 |
| 200 | 0.450 |
| 300 | 0.320 |
| 500 | 0.180 |

#### 60° from transverse
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.880 |
| 100 | 0.800 |
| 200 | 0.680 |
| 300 | 0.580 |
| 500 | 0.420 |

#### Pure axial (90° from transverse)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.950 |
| 100 | 0.920 |
| 200 | 0.880 |
| 300 | 0.860 |
| 500 | 0.840 |

**Key finding**: Pure transverse loading is the most severe. Pure axial loading produces minimal loosening (<20% loss in 500 cycles). The loosening severity scales approximately with the **transverse component** of the applied displacement: F_transverse = δ × cos(θ).

---

## Design Implications

### Loosening Resistance by l/d Ratio
| l/d ratio | Loosening resistance | Recommendation |
|---|---|---|
| < 2.0 | Very poor | Avoid; use locking devices |
| 2.0 – 3.0 | Poor to moderate | Standard, needs assessment |
| 3.0 – 4.0 | Good | Improved resistance |
| > 4.5 | Excellent | Significantly reduces loosening |

### VDI 2230 Recommendation
VDI 2230 recommends l_c/d ≥ 5 for optimal bolt resilience and loosening resistance. The Jiang/Zhang data supports this recommendation quantitatively.

---

## Reproduction Parameters Summary

| Parameter | Value | Units |
|---|---|---|
| Bolt | M12 × 1.75 | — |
| Class | 10.9 | — |
| E (bolt) | 206,000 | MPa |
| ν | 0.3 | — |
| Preloads | 25,000 / 41,000 | N |
| Displacement | 0.46 | mm (peak) |
| Frequency | 5 | Hz |
| Grip lengths | 12.7 / 25.4 / 38.1 / 50.8 | mm |
| Hole diameter | ~13.5 | mm |
| Plate material | AISI 1045 | — |
| Friction (estimated) | 0.15–0.20 | — |
| Thread engagement | 10.4 | mm (full nut) |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this experiment.
> Same bolt geometry as Study 02 (Jiang 2003). Vary FLANGE thickness to test grip length effects.

### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M12×1.75 | — |
| d (nominal) | 12.0 | mm |
| p (pitch) | 1.75 | mm |
| d₂ (pitch dia.) | 10.863 | mm |
| d₃ (minor dia.) | 9.853 | mm |
| Aₜ (stress area) | 84.3 | mm² |
| d_head (AF) | 18.0 | mm |
| Head height | 7.5 | mm |
| Nut height | 10.4 | mm |
| d_hole | 13.5 | mm |
| Helix angle | 2.93 | ° |
| r_be (eff. bearing) | 7.60 | mm |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 Q&T | 206,000 | 940 | 1,040 | 0.3 |
| Plates | AISI 1045 | 200,000 | 530 | 690 | 0.29 |

### MSD Element Chain

```
GROUND — FLANGE(variable) — FLANGE(variable) — NUT — THREAD — SHANK — HEAD — GROUND
```

### Loading (PropertyInspector) — All Configurations

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 25,000 | N |
| % Yield | 31.6 | % |
| Transverse disp. δ | 0.46 | mm |
| Frequency | 5.0 | Hz |
| Cycles | 500 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 |
| Lubricated | false |
| Bolt diameter | 12.0 mm |
| Pitch | 1.75 mm |

### Grip Length Configurations (4 models)

| Config | Grip (mm) | l/d | Plate setup | FLANGE_1 (mm) | FLANGE_2 (mm) | Shank L (mm) |
|---|---|---|---|---|---|---|
| Short | 12.7 | 1.06 | 1×12.7 | 12.7 | — | 2.3 |
| Standard | 25.4 | 2.12 | 2×12.7 | 12.7 | 12.7 | 15.0 |
| Long | 38.1 | 3.18 | 3×12.7 | 12.7+12.7 | 12.7 | 27.7 |
| Extra long | 50.8 | 4.23 | 4×12.7 | 12.7+12.7 | 12.7+12.7 | 40.4 |

### ValidationCase — Standard Grip (for validation_cases.py)

```python
ValidationCase(
    name="Zhang_2006_M12_grip_25mm",
    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,
    initial_preload_N=25000,
    preload_percent_yield=31.6,
    transverse_displacement_mm=0.46,
    frequency_Hz=5.0,
    n_cycles=300,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.06,
    expected_loosening_deg=15.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.940),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.880),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.780),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.560),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.340),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.120),
    ]
)
```

### ValidationCase — Short Grip

```python
ValidationCase(
    name="Zhang_2006_M12_grip_12.7mm",
    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,
    initial_preload_N=25000,
    preload_percent_yield=31.6,
    transverse_displacement_mm=0.46,
    frequency_Hz=5.0,
    n_cycles=100,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.04,
    expected_loosening_deg=20.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.800),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.640),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.400),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.140),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.040),
    ]
)
```

### ValidationCase — Extra Long Grip

```python
ValidationCase(
    name="Zhang_2006_M12_grip_50.8mm",
    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,
    initial_preload_N=25000,
    preload_percent_yield=31.6,
    transverse_displacement_mm=0.46,
    frequency_Hz=5.0,
    n_cycles=500,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.30,
    expected_loosening_deg=8.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.960),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.920),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.840),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.740),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.600),
        ExperimentalDataPoint(cycles=300, preload_ratio=0.480),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.300),
    ]
)
```
