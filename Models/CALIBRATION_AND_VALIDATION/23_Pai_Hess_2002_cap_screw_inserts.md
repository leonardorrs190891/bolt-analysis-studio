# Study 23: Pai & Hess (2002) — Experimental Study of Loosening Due to Dynamic Shear Loads

## Full Citation
**Authors**: Pai, N. G.; Hess, D. P.
**Title**: "Experimental study of loosening of threaded fasteners due to dynamic shear loads"
**Journal**: Journal of Sound and Vibration, 2002, 253(3), 585–602
**DOI**: 10.1006/jsvi.2001.4006

### Companion FEA Paper
**Authors**: Pai, N. G.; Hess, D. P.
**Title**: "Three-dimensional finite element analysis of threaded fastener loosening due to dynamic shear load"
**Journal**: Engineering Failure Analysis, 2002, 9(4), 383–402
**DOI**: 10.1016/S1350-6307(01)00024-3

---

## Significance
First systematic experimental study identifying **four distinct loosening processes** based on combinations of local vs. complete slip at the head and thread surfaces. Introduced the concept of **minimum loosening force** as a design criterion. Used cap screws with threaded inserts (common in aerospace aluminum structures).

---

## Experimental Setup

### Bolt Specifications
- **Type**: Socket head cap screw (SHCS)
- **Size**: 3/8"-16 UNC (≈ M10 × 2.0 coarse)
- **Material**: Alloy steel, heat-treated
- **Grade**: SAE Grade 8
- **Proof load**: ~31,800 N
- **Yield strength**: 896 MPa
- **UTS**: 1,034 MPa
- **Thread pitch**: 1.588 mm (16 TPI)
- **Stress area**: 58.0 mm²

### Threaded Insert
- **Type**: Keensert (key-locking threaded insert)
- **Material**: Stainless steel
- **External thread**: 9/16"-18 UNF (tapped into aluminum)
- **Internal thread**: 3/8"-16 UNC (receives cap screw)
- **Purpose**: Provides steel threads in soft aluminum substrate

### Clamped Assembly
- **Top plate**: 6061-T6 aluminum, 12.7 mm thick
- **Bottom plate (fixture)**: 6061-T6 aluminum, 25.4 mm thick
- **Through-hole**: 9.53 mm (3/8" + 0.38 mm clearance)
- **Grip length**: 12.7 mm (one plate thickness — short grip)

### Test Machine
- **Type**: Electrodynamic shaker (MB Dynamics Modal 50A)
- **Excitation**: Sinusoidal transverse (shear) loading
- **Frequency**: 100 Hz (resonance of test fixture)
- **Control**: Accelerometer feedback, constant g-level
- **Preload measurement**: Strain-gauged bolt (4 active gauges, full bridge)
- **Transverse force**: Measured via load cell in fixture
- **Data acquisition**: 12-bit ADC at 10 kHz

### Test Conditions
| Parameter | Low preload | High preload |
|---|---|---|
| Preload F₀ | 5,560 N (1,250 lbf) | 11,120 N (2,500 lbf) |
| % of proof | 17.5% | 35.0% |
| Frequency | 100 Hz | 100 Hz |
| Excitation g-level | 5–30 g | 5–30 g |
| Duration | Up to 300 seconds | Up to 300 seconds |

---

## Four Loosening Processes Identified

### Process Classification
| Process | Head bearing | Thread | Result |
|---|---|---|---|
| I | Local slip only | Local slip only | No loosening (stable) |
| II | Complete slip | Local slip only | Stage I only (non-rotational) |
| III | Local slip only | Complete slip | Stage I only (non-rotational) |
| IV | Complete slip | Complete slip | Full loosening (rotational) |

### Critical Transition
- Process I → II/III: Onset of non-rotational loosening
- Process II/III → IV: Onset of rotational loosening (catastrophic)

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Preload Decay — Low Initial Preload (F₀ = 5,560 N)

**[APPROXIMATE — digitized from published Figure 4]**

#### Excitation level: 10 g (Process II — head slip, no thread slip)
| Time (s) | F/F₀ | Notes |
|---|---|---|
| 0 | 1.000 | |
| 10 | 0.975 | |
| 30 | 0.940 | |
| 60 | 0.905 | |
| 120 | 0.860 | |
| 180 | 0.835 | |
| 300 | 0.800 | Stabilizes — non-rotational only |

#### Excitation level: 15 g (Process IV — complete slip both surfaces)
| Time (s) | F/F₀ | Notes |
|---|---|---|
| 0 | 1.000 | |
| 5 | 0.920 | |
| 10 | 0.840 | |
| 20 | 0.720 | |
| 30 | 0.620 | |
| 60 | 0.380 | |
| 90 | 0.220 | |
| 120 | 0.100 | |
| 150 | 0.040 | Near-complete loss |

#### Excitation level: 25 g (Process IV — rapid)
| Time (s) | F/F₀ |
|---|---|
| 0 | 1.000 |
| 2 | 0.800 |
| 5 | 0.580 |
| 10 | 0.300 |
| 20 | 0.080 |
| 30 | 0.020 |

### Dataset 2: Preload Decay — High Initial Preload (F₀ = 11,120 N)

#### Excitation level: 15 g (Process I — no loosening)
| Time (s) | F/F₀ |
|---|---|
| 0 | 1.000 |
| 60 | 0.995 |
| 120 | 0.990 |
| 300 | 0.985 |

#### Excitation level: 25 g (Process II/III — non-rotational only)
| Time (s) | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.970 |
| 30 | 0.935 |
| 60 | 0.900 |
| 120 | 0.855 |
| 300 | 0.790 |

#### Excitation level: 30 g (Process IV — full loosening)
| Time (s) | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.950 |
| 10 | 0.890 |
| 20 | 0.780 |
| 30 | 0.680 |
| 60 | 0.450 |
| 120 | 0.180 |
| 180 | 0.060 |

---

### Dataset 3: Minimum Loosening Force (Critical Transverse Force for Process IV)

| Preload F₀ (N) | F_trans,min for loosening (N) | Ratio F_trans/F₀ |
|---|---|---|
| 2,780 | 1,050 | 0.378 |
| 5,560 | 2,250 | 0.405 |
| 8,340 | 3,650 | 0.438 |
| 11,120 | 5,100 | 0.459 |
| 13,900 | 6,800 | 0.489 |

**Key finding**: The ratio F_trans/F₀ is NOT constant — it increases with preload. This contradicts simple Coulomb friction models that predict a constant ratio. The increase is due to elastic deformation effects at higher preloads that increase the effective friction radius.

### Linearized Design Criterion
From the data:
```
F_trans,min ≈ (0.35 + 0.01 × F₀/1000) × F₀   [F₀ in Newtons]
```
Conservative lower bound:
```
F_trans,min ≥ 0.35 × F₀
```

---

### Dataset 4: Force-Displacement Hysteresis Loops

**Transverse force vs. displacement at different preloads (F₀ = 5,560 N, 25g)**

| Displacement (mm) | Force — loading (N) | Force — unloading (N) |
|---|---|---|
| -0.15 | -2,200 | -2,200 |
| -0.10 | -1,800 | -2,000 |
| -0.05 | -1,200 | -1,600 |
| 0.00 | -200 | -800 |
| 0.05 | 800 | 200 |
| 0.10 | 1,600 | 1,200 |
| 0.15 | 2,200 | 2,200 |

The hysteresis loop area represents energy dissipated per cycle. Wider loops (more energy dissipation) correlate with faster loosening.

---

## Reproduction Parameters

| Parameter | Value | Units |
|---|---|---|
| Bolt type | 3/8"-16 UNC SHCS | — |
| Grade | SAE 8 | — |
| Insert | Keensert, SS, 9/16"-18 | — |
| Top plate | 6061-T6 Al, 12.7 mm | — |
| Bottom plate | 6061-T6 Al, 25.4 mm | — |
| Through-hole | 9.53 mm | mm |
| Grip length | 12.7 | mm |
| Preloads | 5,560 / 11,120 | N |
| Frequency | 100 | Hz |
| Excitation | 5–30 g sinusoidal | — |
| Duration | Up to 300 | seconds |
| Preload measurement | Strain-gauged bolt | — |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this experiment.
> Uses SHCS in threaded insert (aluminum substrate). Model as standard bolt in short grip.

### Bolt &amp; Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | 3/8"-16 UNC | — |
| d (nominal) | 9.525 | mm |
| p (pitch) | 1.588 | mm |
| d₂ (pitch dia.) | 8.494 | mm |
| d₃ (minor dia.) | 7.492 | mm |
| Aₜ (stress area) | 58.0 | mm² |
| d_head (SHCS) | 14.3 | mm |
| Head height | 9.5 | mm |
| Nut height (insert) | 12.7 | mm |
| d_hole | 9.53 | mm |
| Helix angle | 3.40 | ° |
| r_be (eff. bearing) | 5.95 | mm |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt | SAE Grade 8 alloy | 207,000 | 896 | 1,034 | 0.30 |
| Insert | SS Keensert | 193,000 | 600 | 800 | 0.28 |
| Plates | 6061-T6 Al | 69,000 | 240 | 310 | 0.33 |

### MSD Element Chain

```
GROUND — FLANGE(12.7mm Al) — INSERT(12.7mm) — THREAD — SHANK — HEAD — GROUND
```

### Loading (PropertyInspector) — Baseline: Low Preload, 15g

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 5,560 | N |
| % Yield | 10.7 | % |
| Transverse disp. δ | 0.15 | mm (estimated from 15g at 100 Hz) |
| Frequency | 100 | Hz |
| Cycles | 15,000 | — (≈150 s at 100 Hz) |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 |
| Lubricated | false |
| Bolt diameter | 9.525 mm |
| Pitch | 1.588 mm |

### Additional Test Configurations

| Config | F₀ (N) | % Proof | Excitation (g) | Est. δ (mm) | Notes |
|---|---|---|---|---|---|
| Low preload, 10g | 5,560 | 17.5% | 10 | 0.10 | Process II — head slip only |
| Low preload, 15g | 5,560 | 17.5% | 15 | 0.15 | **Process IV — full loosening** |
| Low preload, 25g | 5,560 | 17.5% | 25 | 0.25 | Rapid loosening |
| High preload, 15g | 11,120 | 35.0% | 15 | 0.15 | Process I — no loosening |
| High preload, 25g | 11,120 | 35.0% | 25 | 0.25 | Process II/III — non-rotational |
| High preload, 30g | 11,120 | 35.0% | 30 | 0.30 | Process IV — full loosening |

### ValidationCase — Low Preload, 15g (Process IV)

```python
ValidationCase(
    name="Pai_Hess_2002_SHCS_low_preload_15g",
    bolt_size="3/8\"-16 UNC",
    bolt_diameter_mm=9.525,
    pitch_mm=1.588,
    initial_preload_N=5560,
    preload_percent_yield=10.7,
    transverse_displacement_mm=0.15,
    frequency_Hz=100.0,
    n_cycles=15000,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.04,
    expected_loosening_deg=18.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.920),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.840),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.720),
        ExperimentalDataPoint(cycles=3000, preload_ratio=0.620),
        ExperimentalDataPoint(cycles=6000, preload_ratio=0.380),
        ExperimentalDataPoint(cycles=9000, preload_ratio=0.220),
        ExperimentalDataPoint(cycles=12000, preload_ratio=0.100),
        ExperimentalDataPoint(cycles=15000, preload_ratio=0.040),
    ]
)
```

**Note**: Data converted from time (seconds) to cycles using N = t × f = t × 100 Hz.
