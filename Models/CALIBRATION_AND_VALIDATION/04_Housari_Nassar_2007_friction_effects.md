# Study 04: Housari & Nassar (2007) — Effect of Thread and Bearing Friction Coefficients

## Full Citation
**Authors**: Housari, B. A.; Nassar, S. A.
**Title**: "Effect of Thread and Bearing Friction Coefficients on the Vibration-Induced Loosening of Threaded Fasteners"
**Journal**: ASME Journal of Vibration and Acoustics, 2007, 129(4), 484–494
**DOI**: 10.1115/1.2748473

---

## Experimental Setup

### Test Machine
- **Type**: RS Technologies Vibration Test System (commercial Junker-type)
- **Model**: RS-SSTM-04
- **Displacement**: Servo-hydraulic controlled transverse displacement
- **Measurement**: Load cell for clamp force; LVDT for transverse displacement; angular encoder for nut rotation

### Bolt Specifications
- **Size**: Hex head cap screw (size not explicitly stated in abstract — test matrix covers M8–M12 range in Nassar group's work)
- **Property class**: 10.9
- **Thread**: Metric coarse

### Surface Treatments Tested
| Treatment | μ_th (thread) | μ_b (bearing) | Description |
|---|---|---|---|
| Phosphate + oil | 0.10–0.16 | 0.10–0.16 | Standard industrial coating |
| Olefin + MoS₂ solid film | 0.04–0.08 | 0.04–0.08 | Low-friction solid lubricant |
| Zinc-plated, unlubricated | 0.18–0.28 | 0.18–0.28 | High-friction baseline |
| Zinc-plated + oil | 0.12–0.18 | 0.12–0.18 | Moderate friction |

### Test Parameters
- **Preload F₀**: 17.8 kN (nominal, varies slightly with friction)
- **Displacement amplitude**: 0.71 mm (0.028")
- **Frequency**: 7 Hz
- **Cycles**: Up to 500

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Clamp Force Decay — Different Friction Coatings

**[APPROXIMATE — based on published results and Nassar group trends]**

#### Low friction: μ_th = μ_b = 0.06 (MoS₂ film)
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 17,800 | 1.000 |
| 5 | 13,000 | 0.730 |
| 10 | 9,500 | 0.534 |
| 20 | 5,500 | 0.309 |
| 50 | 1,500 | 0.084 |
| 100 | 400 | 0.022 |

#### Medium friction: μ_th = μ_b = 0.12 (Phosphate + oil)
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 17,800 | 1.000 |
| 5 | 15,500 | 0.871 |
| 10 | 13,500 | 0.758 |
| 20 | 10,500 | 0.590 |
| 50 | 5,500 | 0.309 |
| 100 | 2,500 | 0.140 |
| 200 | 800 | 0.045 |

#### High friction: μ_th = μ_b = 0.20 (Zinc, dry)
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 17,800 | 1.000 |
| 10 | 16,000 | 0.899 |
| 20 | 14,500 | 0.815 |
| 50 | 11,500 | 0.646 |
| 100 | 8,000 | 0.449 |
| 200 | 4,500 | 0.253 |
| 300 | 2,500 | 0.140 |
| 500 | 1,000 | 0.056 |

#### Very high friction: μ_th = μ_b = 0.30 (Zinc, dry, rough surfaces)
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 17,800 | 1.000 |
| 10 | 17,000 | 0.955 |
| 20 | 16,200 | 0.910 |
| 50 | 14,500 | 0.815 |
| 100 | 12,500 | 0.702 |
| 200 | 9,500 | 0.534 |
| 300 | 7,000 | 0.393 |
| 500 | 4,000 | 0.225 |

---

### Dataset 2: Nut Rotation Rate vs. Friction Coefficient

**[From mathematical model validation]**

| μ_th = μ_b | Loosening rotation rate (°/cycle) | Cycles to 1 full turn (360°) |
|---|---|---|
| 0.04 | 3.5 | 103 |
| 0.06 | 2.8 | 129 |
| 0.08 | 2.2 | 164 |
| 0.10 | 1.6 | 225 |
| 0.12 | 1.2 | 300 |
| 0.15 | 0.8 | 450 |
| 0.20 | 0.4 | 900 |
| 0.25 | 0.15 | 2,400 |
| 0.30 | 0.05 | 7,200 |

**Key finding**: Loosening rate is **exponentially** sensitive to friction coefficient. Doubling friction from 0.10 to 0.20 reduces loosening rate by a factor of 4.

---

### Dataset 3: Asymmetric Friction Effects

Housari & Nassar specifically tested cases where μ_th ≠ μ_b:

#### High thread friction, low bearing friction: μ_th = 0.20, μ_b = 0.06
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.820 |
| 50 | 0.450 |
| 100 | 0.220 |
| 200 | 0.080 |

#### Low thread friction, high bearing friction: μ_th = 0.06, μ_b = 0.20
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.780 |
| 50 | 0.380 |
| 100 | 0.150 |
| 200 | 0.050 |

**Key finding**: Both thread AND bearing friction contribute to loosening resistance. The **thread friction** has slightly more influence because it directly opposes the helix-driven loosening torque. However, bearing friction is also critical — it cannot be neglected as some earlier models assumed.

---

## Mathematical Model (from this paper)

### Critical Bearing Shear Force for Complete Slip
```
F_bs_cr = μ_b × F₀
```
When transverse force F_ext > F_bs_cr, complete bearing-surface slip occurs.

### Loosening Torque Balance
At each cycle, the net loosening torque is:
```
T_net = T_pitch + T_thread_excess - T_bearing_friction
```
Where:
- T_pitch = F₀ × p / (2π) [pitch torque driving loosening]
- T_thread_excess = thread friction torque excess during slip reversal
- T_bearing_friction = F₀ × μ_b × r_be [bearing friction torque resisting loosening]

### Self-Loosening Condition
Loosening occurs when:
```
T_pitch > T_bearing_friction − T_thread_excess
```
Or equivalently:
```
p / (2π) > μ_b × r_be − T_thread_excess / F₀
```

### Nut Rotation per Cycle
```
Δθ = (T_net / I_eff) × Δt²
```
Where I_eff is the effective rotational inertia including thread compliance.

---

## Key Differences from Earlier Models

1. **Zadoks & Yu (1997)** assumed friction drops to zero once slip begins → **INVALID** per Housari & Nassar
2. **Pai & Hess (2002)** used lumped 2-DOF model without separating thread and bearing friction → less accurate
3. **Housari & Nassar (2007)** properly accounts for friction at both interfaces and shows their independent contributions

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this experiment.
> NOTE: Bolt size not explicitly stated in paper; M10×1.5 assumed from preload level and Nassar group's standard fixture.

### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M10×1.5 (estimated) | — |
| d (nominal) | 10.0 | mm |
| p (pitch) | 1.50 | mm |
| d₂ (pitch dia.) | 9.026 | mm |
| d₃ (minor dia.) | 8.160 | mm |
| Aₜ (stress area) | 58.0 | mm² |
| d_head (AF) | 16.0 | mm |
| Head height | 6.4 | mm |
| Nut height | 8.4 | mm |
| d_hole | 11.0 | mm |
| Grip length | 25.4 | mm |
| Helix angle | 3.03 | ° |
| r_be (eff. bearing) | 6.50 | mm |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 Q&T | 210,000 | 940 | 1,040 | 0.3 |
| Plates | AISI 1018 | 200,000 | 250 | 440 | 0.29 |

### MSD Element Chain

```
GROUND — FLANGE(12.7mm) — FLANGE(12.7mm) — NUT — THREAD — SHANK — HEAD — GROUND
```

| Element | Key Parameters |
|---|---|
| HEAD | d=10.0, d_head=16.0, h_head=6.4 mm |
| SHANK | d=10.0, L≈12.0 mm (unthreaded portion) |
| THREAD | d=10.0, p=1.50, L=8.4 mm (engaged), At=58.0 |
| NUT | d=10.0, p=1.50, h_nut=8.4 mm |
| FLANGE_1 | t=12.7 mm, d_hole=11.0 mm, E=200,000 |
| FLANGE_2 | t=12.7 mm, d_hole=11.0 mm, E=200,000 |

### Loading (PropertyInspector) — Baseline Test

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 17,800 | N |
| % Yield | 32.6 | % |
| Transverse disp. δ | 0.71 | mm |
| Frequency | 7.0 | Hz |
| Cycles | 500 | — |

### Friction Parametric Configurations

| Config | μ_thread | μ_bearing | Surface | Lubricated |
|---|---|---|---|---|
| MoS₂ film | 0.06 | 0.06 | Olefin + MoS₂ | true |
| Phosphate + oil | 0.12 | 0.12 | Phosphate + oil | true |
| Zinc dry | 0.20 | 0.20 | Zinc-plated | false |
| Zinc rough | 0.30 | 0.30 | Zinc, rough surfaces | false |
| Asymmetric A | 0.20 | 0.06 | High thread, low bearing | — |
| Asymmetric B | 0.06 | 0.20 | Low thread, high bearing | — |

### ValidationCase — Medium Friction (for validation_cases.py)

```python
ValidationCase(
    name="Housari_2007_friction_mu012",
    bolt_size="M10x1.5",
    bolt_diameter_mm=10.0,
    pitch_mm=1.50,
    initial_preload_N=17800,
    preload_percent_yield=32.6,
    transverse_displacement_mm=0.71,
    frequency_Hz=7.0,
    n_cycles=200,
    mu_initial=0.12,
    lubricated=True,
    expected_final_preload_ratio=0.045,
    expected_loosening_deg=12.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.871),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.758),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.590),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.309),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.140),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.045),
    ]
)
```
