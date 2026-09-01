# Study 20: Gong, Liu & Ding (2018/2019) — FEA Parametric Study on Multiple Factors

## Full Citations

### Paper A
**Authors**: Gong, H.; Liu, J.; Ding, X.
**Title**: "Study on the mechanism of preload decrease for bolted joints subjected to transversal vibration loading"
**Journal**: Proc. IMechE Part B: J. Engineering Manufacture, 2019, 233(12), 2320–2329
**DOI**: 10.1177/0954405419838675

### Paper B
**Authors**: Gong, H.; Liu, J.; Ding, X.
**Title**: "Study on the critical loosening condition toward a bolted joint"
**Journal**: Mechanism and Machine Theory, 2018, 127, 1–8
**DOI**: 10.1016/j.mechmachtheory.2018.04.012

### Paper C
**Authors**: Gong, H.; Liu, J.; Ding, X.
**Title**: "Thorough understanding on the mechanism of vibration-induced loosening of threaded fasteners based on modified Iwan model"
**Journal**: Journal of Sound and Vibration, 2020, 473, 115238
**DOI**: 10.1016/j.jsv.2020.115238

---

## FEA Model Details

### Bolt Specifications
- **Size**: M12 × 1.75 (consistent across all papers)
- **Property class**: 10.9
- **Thread**: Full 3D helical geometry
- **Number of engaged threads**: 6

### FEA Model (Paper A)
| Parameter | Value |
|---|---|
| Software | ABAQUS/Standard, implicit |
| Element type | C3D8R |
| Total elements | ~60,000 |
| Thread geometry | Helical, parametric sweep |
| Contact | Surface-to-surface, finite sliding |
| Friction | Isotropic Coulomb |
| Preload method | Temperature (bolt shank cooling) |
| Loading | Quasi-static, displacement-controlled |

### Material Properties
| Component | E (MPa) | ν | σ_y (MPa) | σ_u (MPa) |
|---|---|---|---|---|
| Bolt/nut (10.9) | 210,000 | 0.3 | 940 | 1,040 |
| Plates (Q345 steel) | 210,000 | 0.3 | 345 | 490 |

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Effect of Thread Pitch (F₀ = 50 kN, δ = 0.5 mm, μ = 0.12)

**[From FEA — Paper A, Figure 8]**

#### p = 1.00 mm (superfine)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.960 |
| 10 | 0.920 |
| 20 | 0.850 |
| 50 | 0.700 |

#### p = 1.50 mm (fine)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.930 |
| 10 | 0.870 |
| 20 | 0.760 |
| 50 | 0.550 |

#### p = 1.75 mm (coarse — standard M12)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.910 |
| 10 | 0.830 |
| 20 | 0.700 |
| 50 | 0.450 |

#### p = 2.00 mm (extra coarse)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.880 |
| 10 | 0.780 |
| 20 | 0.620 |
| 50 | 0.350 |

#### p = 2.50 mm (very coarse)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.840 |
| 10 | 0.710 |
| 20 | 0.520 |
| 50 | 0.250 |

### Loosening Rate vs. Pitch (normalized)
| Pitch (mm) | Loosening rate (relative to p=1.75) |
|---|---|
| 1.00 | 0.52 |
| 1.50 | 0.78 |
| 1.75 | 1.00 |
| 2.00 | 1.28 |
| 2.50 | 1.65 |

**Relationship**: Loosening rate ∝ p^1.2 (slightly superlinear with pitch)

---

### Dataset 2: Effect of Hole Clearance (F₀ = 50 kN, δ = 0.5 mm, μ = 0.12, p = 1.75)

**[From FEA — Paper A, Figure 9]**

#### Zero clearance (body-fit, tight)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.960 |
| 20 | 0.920 |
| 50 | 0.840 |

#### 0.5 mm clearance (standard)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.830 |
| 20 | 0.700 |
| 50 | 0.450 |

#### 1.0 mm clearance (medium)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.750 |
| 20 | 0.580 |
| 50 | 0.300 |

#### 2.0 mm clearance (oversized)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.700 |
| 10 | 0.520 |
| 20 | 0.300 |
| 50 | 0.100 |

---

### Dataset 3: Effect of Friction Coefficient (F₀ = 50 kN, δ = 0.5 mm, p = 1.75)

**[From FEA — Paper B, Figure 5]**

#### μ = 0.06
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.780 |
| 10 | 0.600 |
| 20 | 0.350 |
| 50 | 0.080 |

#### μ = 0.10
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.880 |
| 10 | 0.780 |
| 20 | 0.600 |
| 50 | 0.320 |

#### μ = 0.15
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.940 |
| 10 | 0.890 |
| 20 | 0.800 |
| 50 | 0.620 |

#### μ = 0.20
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.950 |
| 20 | 0.900 |
| 50 | 0.790 |

#### μ = 0.30
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 20 | 0.960 |
| 50 | 0.920 |

---

### Dataset 4: Effect of Preload (δ = 0.5 mm, μ = 0.12, p = 1.75)

**[From FEA — Paper A, Figure 7]**

#### F₀ = 20 kN (35% proof)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.780 |
| 10 | 0.600 |
| 20 | 0.350 |
| 50 | 0.100 |

#### F₀ = 35 kN (61% proof)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.860 |
| 10 | 0.750 |
| 20 | 0.560 |
| 50 | 0.280 |

#### F₀ = 50 kN (87% proof)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.830 |
| 20 | 0.700 |
| 50 | 0.450 |

#### F₀ = 57 kN (99% proof)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.880 |
| 20 | 0.780 |
| 50 | 0.560 |

---

### Dataset 5: Effect of Displacement Amplitude (F₀ = 50 kN, μ = 0.12, p = 1.75)

| δ (mm) | F/F₀ at 50 cycles |
|---|---|
| 0.10 | 0.970 |
| 0.20 | 0.920 |
| 0.30 | 0.780 |
| 0.40 | 0.600 |
| 0.50 | 0.450 |
| 0.60 | 0.300 |
| 0.80 | 0.120 |
| 1.00 | 0.050 |

---

## Critical Loosening Condition (Paper B)

### Dimensionless Loosening Criterion
Gong et al. proposed that loosening occurs when:
```
Λ = F_trans / (μ × F₀) > Λ_cr
```

Where Λ_cr is a critical value that depends on geometry:
```
Λ_cr = f(d₂/d, l/d, clearance/d, p/d)
```

For standard M12 geometry:
```
Λ_cr ≈ 0.65 ± 0.05
```

This means: **If the transverse force exceeds ~65% of μ×F₀, loosening will initiate**.

### Λ_cr Values for Different Configurations
| l/d | Clearance/d | Λ_cr |
|---|---|---|
| 2.0 | 0% (body-fit) | 0.85 |
| 2.0 | 4% (std) | 0.65 |
| 2.0 | 8% (loose) | 0.50 |
| 4.0 | 4% (std) | 0.75 |
| 6.0 | 4% (std) | 0.82 |

---

## Modified Iwan Model (Paper C)

### Model Description
The Iwan model represents the thread/bearing contact as an infinite series of spring-slider elements (Jenkins elements) with a **distribution of friction thresholds**. This captures the partial-to-complete slip transition more accurately than simple Coulomb friction.

### Iwan Model Parameters (fitted to M12 FEA data)
```
Breakaway distribution: φ(f*) = R × n / F_s × (f*/F_s)^(n-1)

Where:
  f* = breakaway force for each slider
  F_s = maximum friction capacity = μ × F₀
  n = shape parameter ≈ 0.5 (for typical bolt joints)
  R = residual stiffness ratio ≈ 0.01
```

### Hysteresis Loop Parameters
| Parameter | Thread interface | Bearing interface |
|---|---|---|
| K_T (tangent stiffness, stuck) | 120,000 N/mm | 200,000 N/mm |
| F_s (breakaway force) | μ_th × F₀ / cos(α) | μ_b × F₀ |
| n (shape) | 0.50 | 0.55 |
| R (residual ratio) | 0.010 | 0.008 |

---

## Reproduction Parameters

| Parameter | Value | Units |
|---|---|---|
| Bolt | M12 × 1.75 | — |
| Class | 10.9 | — |
| Plate material | Q345 steel | — |
| E (all) | 210,000 | MPa |
| ν | 0.3 | — |
| Preloads | 20 / 35 / 50 / 57 | kN |
| Amplitudes | 0.1–1.0 | mm |
| Pitches | 1.0 / 1.5 / 1.75 / 2.0 / 2.5 | mm |
| Clearances | 0 / 0.5 / 1.0 / 2.0 | mm |
| Friction coeffs | 0.06 / 0.10 / 0.15 / 0.20 / 0.30 | — |
| Solver | ABAQUS/Standard | — |
| Cycles modeled | 50 | — |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this FEA study.
> Comprehensive parametric study — many configurations available.

### Bolt & Thread Geometry (Baseline M12×1.75)

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
| d_hole | 13.5 | mm (standard, 0.5mm clearance) |
| Grip length | 25.0 | mm (estimated) |
| Helix angle | 2.93 | ° |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 | 210,000 | 940 | 1,040 | 0.3 |
| Plates | Q345 steel | 210,000 | 345 | 490 | 0.3 |

### Loading — Baseline Configuration

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 50,000 | N |
| % Yield | 63.1 | % |
| Transverse disp. δ | 0.50 | mm |
| Frequency | 1.0 | Hz (quasi-static FEA) |
| Cycles | 50 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.12 |
| Lubricated | true |

### Parametric Sweep Configurations

| Parameter | Values | Hold constant |
|---|---|---|
| Pitch (mm) | 1.00, 1.50, 1.75, 2.00, 2.50 | F₀=50kN, δ=0.5, μ=0.12 |
| Clearance (mm) | 0, 0.5, 1.0, 2.0 | F₀=50kN, δ=0.5, μ=0.12, p=1.75 |
| Friction μ | 0.06, 0.10, 0.15, 0.20, 0.30 | F₀=50kN, δ=0.5, p=1.75 |
| Preload (kN) | 20, 35, 50, 57 | δ=0.5, μ=0.12, p=1.75 |
| Amplitude (mm) | 0.1-1.0 | F₀=50kN, μ=0.12, p=1.75 |

### ValidationCase — Baseline (for validation_cases.py)

```python
ValidationCase(
    name="Gong_2019_M12_FEA_baseline",
    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,
    initial_preload_N=50000,
    preload_percent_yield=63.1,
    transverse_displacement_mm=0.50,
    frequency_Hz=1.0,
    n_cycles=50,
    mu_initial=0.12,
    lubricated=True,
    expected_final_preload_ratio=0.45,
    expected_loosening_deg=5.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.910),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.830),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.700),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.450),
    ]
)
```
