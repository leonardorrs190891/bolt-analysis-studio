# Study 13: Yang et al. (2021) — Competitive Failure: Bolt Loosening vs. Fatigue Under Different Preloads

## Full Citation
**Authors**: Yang, J.; Wang, D.; Chen, L.; Zhong, J.
**Title**: "Competitive Failure of Bolt Loosening and Fatigue under Different Preloads"
**Journal**: Chinese Journal of Mechanical Engineering, 2021, 34, Article 141
**DOI**: 10.1186/s10033-021-00663-3
**Access**: Open Access (SpringerOpen)
**URL**: https://cjme.springeropen.com/articles/10.1186/s10033-021-00663-3

---

## Experimental Setup

### Bolt Specifications
- **Size**: M8 × 1.25 × 70 mm
- **Property class**: 8.8
- **Material**: Medium carbon alloy steel
- **Stress area**: 36.6 mm²
- **Yield R_p0.2**: 640 MPa
- **UTS R_m**: 800 MPa
- **Proof load**: 23,400 N

### Test Fixture
- **Type**: Modified Junker-type with capability for combined transverse + axial loading
- **Transverse displacement**: Servo-hydraulic, displacement-controlled
- **Axial load**: Separate actuator, load-controlled
- **Measurements**: Load cell (preload), LVDT (displacement), angular encoder (nut rotation)

### Initial Preloads Tested
| Preload level | F₀ (N) | % of proof load |
|---|---|---|
| Low | 5,680 | 24.3% |
| Medium | 8,520 | 36.4% |
| Standard | 14,050 | 60.0% |
| High | 17,040 | 72.8% |

### Loading Conditions
- **Transverse displacement**: δ = 0.6 mm (constant for all tests)
- **Axial load superimposed**: F_axial = 0, 4, 6, 8, 10 kN (sinusoidal, same frequency)
- **Frequency**: 5 Hz
- **Phase**: Axial and transverse loads are in-phase

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Effect of Initial Preload on Loosening (δ = 0.6 mm, no axial load)

**[APPROXIMATE — digitized from published Figure 4]**

#### F₀ = 5,680 N (low preload)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.750 |
| 10 | 0.550 |
| 20 | 0.320 |
| 50 | 0.100 |
| 100 | 0.020 |

#### F₀ = 8,520 N (medium preload)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.830 |
| 10 | 0.680 |
| 20 | 0.480 |
| 50 | 0.220 |
| 100 | 0.080 |
| 200 | 0.020 |

#### F₀ = 14,050 N (standard preload)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.860 |
| 20 | 0.740 |
| 50 | 0.500 |
| 100 | 0.300 |
| 200 | 0.130 |
| 500 | 0.030 |

#### F₀ = 17,040 N (high preload)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.920 |
| 20 | 0.850 |
| 50 | 0.680 |
| 100 | 0.480 |
| 200 | 0.280 |
| 500 | 0.100 |
| 1,000 | 0.030 |

---

### Dataset 2: Combined Transverse + Axial Loading (F₀ = 14,050 N, δ = 0.6 mm)

**[APPROXIMATE — digitized from published Figures 6–7]**

#### Pure transverse (F_axial = 0)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.500 |
| 100 | 0.300 |
| 200 | 0.130 |

#### F_axial = 4 kN
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.450 |
| 100 | 0.250 |
| 200 | 0.100 |

#### F_axial = 6 kN
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.400 |
| 100 | 0.200 |
| 200 | 0.070 |

#### F_axial = 10 kN
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 20 | 0.500 |
| 50 | 0.250 |
| 100 | 0.080 |
| 200 | 0.020 |

**Key finding**: Superimposing axial load ACCELERATES loosening because it promotes alternating partial separation of the bearing surface, reducing friction resistance to nut rotation.

---

### Dataset 3: Critical Load Ratio — Loosening vs. Fatigue

The paper defines a **critical load ratio**:
```
ξ_cr = δ / F_axial    (mm/kN)
```

| ξ = δ/F_axial | Dominant failure mode |
|---|---|
| ξ > 0.15 | Pure loosening (preload loss) |
| 0.075 < ξ < 0.15 | Combined loosening + fatigue |
| ξ < 0.075 | Pure fatigue (bolt fracture) |

**Critical ratio ξ_cr ≈ 0.075 mm/kN** is proposed as an **inherent property of the bolt**, independent of absolute load magnitudes.

### Failure Mode Map (M8 × 1.25 Class 8.8)

| δ (mm) | F_axial (kN) | ξ | Failure mode | Life (cycles) |
|---|---|---|---|---|
| 0.6 | 0 | ∞ | Loosening | ~500 |
| 0.6 | 4 | 0.150 | Loosening dominant | ~400 |
| 0.6 | 8 | 0.075 | Transition | ~600 (loosening slows, fatigue onset) |
| 0.6 | 10 | 0.060 | Fatigue dominant | ~2,000 (bolt fracture) |
| 0.3 | 4 | 0.075 | Transition | ~1,500 |
| 0.3 | 8 | 0.038 | Fatigue | ~5,000 (bolt fracture) |

---

## Reproduction Parameters

| Parameter | Value | Units |
|---|---|---|
| Bolt | M8 × 1.25 × 70 | mm |
| Class | 8.8 | — |
| Preloads | 5,680 / 8,520 / 14,050 / 17,040 | N |
| Transverse δ | 0.6 | mm |
| Axial loads | 0 / 4 / 6 / 8 / 10 | kN |
| Frequency | 5 | Hz |
| Grip length | ~30 mm (estimated from bolt length) | mm |
| Surface | Unlubricated | — |
| μ (estimated) | 0.15–0.20 | — |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this experiment.
> NOTE: Tests combined TRANSVERSE + AXIAL loading — use COMBINED load type.

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
| Grip length | 30.0 | mm (estimated) |
| Helix angle | 3.17 | ° |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 8.8 Q&T | 210,000 | 640 | 800 | 0.3 |
| Plates | Steel | 210,000 | — | — | 0.3 |

### Loading — Pure Transverse (Baseline)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 14,050 | N |
| % Yield | 60.0 | % |
| Transverse disp. δ | 0.6 | mm |
| Frequency | 5.0 | Hz |
| Cycles | 500 | — |

### Combined Loading Configurations

| Config | F₀ (N) | δ (mm) | F_axial (N) | Notes |
|---|---|---|---|---|
| Low preload | 5,680 | 0.6 | 0 | 24.3% proof |
| Medium preload | 8,520 | 0.6 | 0 | 36.4% proof |
| Standard preload | 14,050 | 0.6 | 0 | 60.0% proof |
| High preload | 17,040 | 0.6 | 0 | 72.8% proof |
| Trans+Axial 4kN | 14,050 | 0.6 | 4,000 | Combined |
| Trans+Axial 6kN | 14,050 | 0.6 | 6,000 | Combined |
| Trans+Axial 10kN | 14,050 | 0.6 | 10,000 | Fatigue dominant |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.18 |
| Lubricated | false |

### ValidationCase — Standard Preload (for validation_cases.py)

```python
ValidationCase(
    name="Yang_2021_M8_combined",
    bolt_size="M8x1.25",
    bolt_diameter_mm=8.0,
    pitch_mm=1.25,
    initial_preload_N=14050,
    preload_percent_yield=60.0,
    transverse_displacement_mm=0.6,
    frequency_Hz=5.0,
    n_cycles=500,
    mu_initial=0.18,
    lubricated=False,
    expected_final_preload_ratio=0.03,
    expected_loosening_deg=15.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.860),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.740),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.500),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.300),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.130),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.030),
    ]
)
```
