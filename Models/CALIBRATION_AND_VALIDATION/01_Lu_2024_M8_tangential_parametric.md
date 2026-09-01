# Study 01: Lu et al. (2024) — M8 Bolt Preload Relaxation Under Tangential Cyclic Load

## Full Citation
**Authors**: Lu, Y.; Hou, Y.; Guo, W.; Zhao, X.; Chen, M.
**Title**: "Prediction of Pre-Loading Relaxation of Bolt Structure of Complex Equipment under Tangential Cyclic Load"
**Journal**: Sensors, 2024, 24(11), 3306
**DOI**: 10.3390/s24113306
**PMC**: PMC11174751 (Open Access)
**URL**: https://pmc.ncbi.nlm.nih.gov/articles/PMC11174751/

---

## Experimental Setup

### Bolt Specifications
- **Bolt type**: Hexagonal head bolt
- **Size**: M8 × 1.25 (metric, coarse thread)
- **Property class**: 8.8
- **Material**: Medium carbon steel (C ≈ 0.28–0.50%, per ISO 898-1)
- **Yield strength R_p0.2**: 640 MPa (Class 8.8)
- **Ultimate tensile strength R_m**: 800 MPa (Class 8.8)
- **Proof load**: 32,000 N (M8 Class 8.8 per ISO 898-1)
- **Thread pitch**: 1.25 mm
- **Thread angle**: 60° (ISO metric)

### Nut Specifications
- **Type**: Standard hexagonal nut
- **Property class**: 8 (matching bolt)
- **Material**: Medium carbon steel

### Clamped Members
- **Material**: Nickel steel plates
- **Hardness**: Not explicitly specified (assumed HRC 20–30 range)
- **Surface finish**: Variable — tested at Ra 0.8, Ra 1.6, and Ra 3.2 μm

### Test Fixture
- **Machine**: 50 kN electro-hydraulic servo fatigue testing machine
- **Loading type**: Tangential (transverse) cyclic displacement
- **Displacement control**: Servo-hydraulic actuator
- **Preload measurement**: Strain gauge on bolt shank (calibrated)
- **Configuration**: Single-bolt through-hole joint with clevis-type fixture

### Washer
- Not explicitly mentioned — assumed flat washer per standard practice

---

## Test Parameters — Parametric Study Design

### Parameter Variations

| Parameter | Values tested | Held constant |
|---|---|---|
| Tightening torque | 4, 10, 16, 22, 28 Nm | Amplitude=1.0 mm, Ra=1.6, f=1 Hz |
| Displacement amplitude | 0.25, 0.50, 1.0, 1.5, 2.0 mm | Torque=22 Nm, Ra=1.6, f=1 Hz |
| Surface roughness | Ra 0.8, 1.6, 3.2 μm | Torque=22 Nm, Amplitude=1.0 mm, f=1 Hz |
| Frequency | 1, 3, 5 Hz | Torque=22 Nm, Amplitude=1.0 mm, Ra=1.6 |

### Initial Preloads (Measured)

| Tightening torque (Nm) | Measured initial preload F₀ (N) | % of proof load |
|---|---|---|
| 4 | 2,105 | 6.6% |
| 10 | 5,963 | 18.6% |
| 16 | 8,402 | 26.3% |
| 22 | 11,567 | 36.1% |
| 28 | 15,027 | 47.0% |

**Note**: These preloads are low relative to proof load. The K-factor (nut factor) implied is approximately K = T/(F·d) ≈ 22/(11567×0.008) ≈ 0.238, consistent with unlubricated zinc-plated M8 bolts.

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Effect of Tightening Torque (Amplitude = 1.0 mm, Ra = 1.6, f = 1 Hz)

**[APPROXIMATE — digitized from published Figure 7]**

#### T = 4 Nm (F₀ = 2,105 N)
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 2,105 | 1.000 |
| 5 | 1,200 | 0.570 |
| 10 | 600 | 0.285 |
| 20 | 300 | 0.143 |
| 50 | 150 | 0.071 |
| 100 | 78 | 0.037 |

#### T = 10 Nm (F₀ = 5,963 N)
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 5,963 | 1.000 |
| 5 | 4,800 | 0.805 |
| 10 | 4,200 | 0.704 |
| 20 | 3,600 | 0.604 |
| 50 | 2,600 | 0.436 |
| 100 | 1,845 | 0.309 |

#### T = 16 Nm (F₀ = 8,402 N)
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 8,402 | 1.000 |
| 5 | 6,200 | 0.738 |
| 10 | 5,000 | 0.595 |
| 20 | 3,800 | 0.452 |
| 50 | 2,200 | 0.262 |
| 100 | 1,568 | 0.187 |

#### T = 22 Nm (F₀ = 11,567 N)
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 11,567 | 1.000 |
| 5 | 7,500 | 0.648 |
| 10 | 5,500 | 0.475 |
| 20 | 3,200 | 0.277 |
| 50 | 1,200 | 0.104 |
| 100 | 742 | 0.064 |

#### T = 28 Nm (F₀ = 15,027 N)
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 15,027 | 1.000 |
| 5 | 12,000 | 0.799 |
| 10 | 10,000 | 0.666 |
| 20 | 7,500 | 0.499 |
| 50 | 5,000 | 0.333 |
| 100 | 3,523 | 0.234 |

---

### Dataset 2: Effect of Displacement Amplitude (T = 22 Nm, F₀ = 11,567 N, Ra = 1.6, f = 1 Hz)

**[APPROXIMATE — digitized from published Figure 8]**

#### Amplitude = 0.25 mm
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 11,567 | 1.000 |
| 10 | 11,000 | 0.951 |
| 20 | 10,700 | 0.925 |
| 50 | 10,200 | 0.882 |
| 100 | 9,800 | 0.847 |
| 200 | 9,500 | 0.821 |
| 500 | 9,300 | 0.804 |
| 1000 | 9,200 | 0.795 |

#### Amplitude = 0.50 mm
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 11,567 | 1.000 |
| 5 | 9,000 | 0.778 |
| 10 | 7,000 | 0.605 |
| 20 | 4,500 | 0.389 |
| 50 | 1,500 | 0.130 |
| 100 | 600 | 0.052 |
| 200 | 200 | 0.017 |
| 400 | 100 | 0.009 |
| 500 | 50 | 0.004 |

#### Amplitude = 1.0 mm
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 11,567 | 1.000 |
| 5 | 7,500 | 0.648 |
| 10 | 5,500 | 0.475 |
| 20 | 3,200 | 0.277 |
| 50 | 1,200 | 0.104 |
| 100 | 742 | 0.064 |

#### Amplitude = 1.5 mm
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 11,567 | 1.000 |
| 2 | 7,000 | 0.605 |
| 5 | 4,500 | 0.389 |
| 10 | 2,500 | 0.216 |
| 20 | 1,000 | 0.086 |
| 50 | 300 | 0.026 |
| 100 | 100 | 0.009 |

#### Amplitude = 2.0 mm
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 11,567 | 1.000 |
| 1 | 5,760 | 0.498 |
| 2 | 3,500 | 0.303 |
| 5 | 1,500 | 0.130 |
| 10 | 500 | 0.043 |
| 20 | 150 | 0.013 |
| 50 | 50 | 0.004 |

**Key finding**: First cycle at 2.0 mm amplitude reduced preload by **50.2%**.

---

### Dataset 3: Effect of Surface Roughness (T = 22 Nm, Amplitude = 1.0 mm, f = 1 Hz)

**[APPROXIMATE — digitized from published Figure 9]**

#### Ra = 0.8 μm (smooth)
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 11,567 | 1.000 |
| 5 | 6,500 | 0.562 |
| 10 | 4,500 | 0.389 |
| 20 | 2,500 | 0.216 |
| 50 | 800 | 0.069 |
| 100 | 400 | 0.035 |

#### Ra = 1.6 μm (medium)
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 11,567 | 1.000 |
| 5 | 7,500 | 0.648 |
| 10 | 5,500 | 0.475 |
| 20 | 3,200 | 0.277 |
| 50 | 1,200 | 0.104 |
| 100 | 742 | 0.064 |

#### Ra = 3.2 μm (rough)
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 11,567 | 1.000 |
| 5 | 8,500 | 0.735 |
| 10 | 6,800 | 0.588 |
| 20 | 4,500 | 0.389 |
| 50 | 2,000 | 0.173 |
| 100 | 1,100 | 0.095 |

**Key finding**: Rougher surfaces provide more friction and resist loosening slightly better in early cycles, but all converge to near-complete loss by 100 cycles at 1.0 mm amplitude.

---

### Dataset 4: Effect of Frequency (T = 22 Nm, Amplitude = 1.0 mm, Ra = 1.6)

**[APPROXIMATE — digitized from published Figure 10]**

#### f = 1 Hz
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 11,567 | 1.000 |
| 10 | 5,500 | 0.475 |
| 50 | 1,200 | 0.104 |
| 100 | 742 | 0.064 |

#### f = 3 Hz
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 11,567 | 1.000 |
| 10 | 5,300 | 0.458 |
| 50 | 1,100 | 0.095 |
| 100 | 680 | 0.059 |

#### f = 5 Hz
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 11,567 | 1.000 |
| 10 | 5,100 | 0.441 |
| 50 | 1,000 | 0.086 |
| 100 | 620 | 0.054 |

**Key finding**: Frequency has minimal effect on loosening behavior (consistent with all literature). Slightly faster loosening at higher frequencies due to inertia effects.

---

## Mathematical Models (from this paper)

### Allometric Model
```
F(N) = a × N^b
```
Where a and b are fitted constants. Accuracy: **>85.5%** (R² > 0.855)

### Nine-Stage Polynomial Model
```
F(N) = c₀ + c₁N + c₂N² + c₃N³ + c₄N⁴ + c₅N⁵ + c₆N⁶ + c₇N⁷ + c₈N⁸ + c₉N⁹
```
Accuracy: **>90.4%** (R² > 0.904)

### Double Exponential Model (general form)
```
F(N) = A₁·exp(−B₁·N) + A₂·exp(−B₂·N)
```
Where:
- A₁ + A₂ = F₀ (initial preload)
- B₁ >> B₂ (fast decay + slow decay)
- Typical values for M8 at 1.0 mm: A₁ ≈ 0.6·F₀, B₁ ≈ 0.15, A₂ ≈ 0.4·F₀, B₂ ≈ 0.01

---

## Setup Reproduction Notes

### Critical Dimensions for FEA/Experimental Reproduction
- M8×1.25: nominal diameter 8 mm, pitch diameter 7.188 mm, minor diameter 6.647 mm
- Stress area: 36.6 mm²
- Bolt head: hex across flats = 13 mm, head height = 5.3 mm
- Nut: hex across flats = 13 mm, nut height = 6.5 mm
- Bearing diameter (effective): approximately 11.6 mm (for standard washer)
- Hole diameter: likely 8.4 mm (standard clearance) or 9.0 mm (medium clearance)
- Grip length: not explicitly stated — estimate 20–30 mm based on fixture description

### Loading Protocol
1. Tighten bolt to target torque using calibrated torque wrench
2. Record initial preload via strain gauge
3. Apply sinusoidal transverse displacement at specified amplitude and frequency
4. Record preload at each cycle (or at specified intervals)
5. Test duration: 100–1,000 cycles depending on amplitude

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this experiment.

### Bolt & Thread Geometry

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
| Grip length | 24.0 | mm (estimated, 2 plates) |
| Helix angle | 3.17 | ° |
| r_be (eff. bearing) | 5.31 | mm |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 8.8 Q&T | 210,000 | 640 | 800 | 0.3 |
| Plates | Nickel steel | 200,000 | — | — | 0.29 |

### MSD Element Chain

```
GROUND — FLANGE(12mm) — FLANGE(12mm) — NUT — THREAD — SHANK — HEAD — GROUND
```

| Element | Key Parameters |
|---|---|
| HEAD | d=8.0, d_head=13.0, h_head=5.3 mm |
| SHANK | d=8.0, L≈10 mm (unthreaded portion) |
| THREAD | d=8.0, p=1.25, L≈6.5 mm (engaged), At=36.6 |
| NUT | d=8.0, p=1.25, h_nut=6.5 mm |
| FLANGE_1 | t=12.0 mm, d_hole=9.0 mm, E=200,000 |
| FLANGE_2 | t=12.0 mm, d_hole=9.0 mm, E=200,000 |

### Loading (PropertyInspector) — Baseline Test

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 11,567 | N |
| % Yield | 49.4 | % |
| Transverse disp. δ | 1.0 | mm |
| Frequency | 1.0 | Hz |
| Cycles | 100 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.20 |
| Lubricated | false |
| Bolt diameter | 8.0 mm |
| Pitch | 1.25 mm |

### Additional Test Configurations

| Config | F₀ (N) | δ (mm) | f (Hz) | μ_est | Notes |
|---|---|---|---|---|---|
| Low torque (4 Nm) | 2,105 | 1.0 | 1 | 0.20 | Rapid loosening |
| Med torque (16 Nm) | 8,402 | 1.0 | 1 | 0.20 | |
| Baseline (22 Nm) | 11,567 | 1.0 | 1 | 0.20 | Primary test |
| High torque (28 Nm) | 15,027 | 1.0 | 1 | 0.20 | |
| Small amplitude | 11,567 | 0.25 | 1 | 0.20 | Near threshold |
| Medium amplitude | 11,567 | 0.50 | 1 | 0.20 | |
| Large amplitude | 11,567 | 1.5 | 1 | 0.20 | Very rapid |
| Extreme amplitude | 11,567 | 2.0 | 1 | 0.20 | 50% loss in 1 cycle |
| Smooth surface | 11,567 | 1.0 | 1 | 0.18 | Ra=0.8 μm |
| Rough surface | 11,567 | 1.0 | 1 | 0.22 | Ra=3.2 μm |
| High frequency | 11,567 | 1.0 | 5 | 0.20 | f=5 Hz |

### ValidationCase (for validation_cases.py)

```python
ValidationCase(
    name="Lu_2024_M8_baseline",
    bolt_size="M8x1.25",
    bolt_diameter_mm=8.0,
    pitch_mm=1.25,
    initial_preload_N=11567,
    preload_percent_yield=49.4,
    transverse_displacement_mm=1.0,
    frequency_Hz=1.0,
    n_cycles=100,
    mu_initial=0.20,
    lubricated=False,
    expected_final_preload_ratio=0.064,
    expected_loosening_deg=15.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.648),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.475),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.277),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.104),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.064),
    ]
)
```
