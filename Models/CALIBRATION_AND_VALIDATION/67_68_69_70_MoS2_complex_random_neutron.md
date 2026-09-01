# Study 67: Liu, Ouyang, Feng et al. (2017) — MoS₂ Coating Anti-Loosening Under Axial Excitation

## Full Citation
**Authors**: Liu, Z.; Ouyang, H.; Feng, J.; Zhu, S.; Ma, X.
**Title**: "Self-loosening behavior of bolted joints under axial excitation and effect of anti-loosening coating"
**Journal**: Tribology International, 2017, 115, 432–451
**DOI**: 10.1016/j.triboint.2017.05.037

---

## Significance
Most comprehensive study of **MoS₂ surface coatings** as anti-loosening treatment. Tests under axial excitation (not transverse) for up to 2×10⁵ cycles. MoS₂ provides **best anti-loosening performance** while also reducing the required tightening torque by ~40%. Loosening torque found to be <50% of tightening torque.

## Experimental Setup
- **Bolt**: M10 × 1.5, Class 8.8
- **Surface treatments**: (1) Bare steel, (2) Zinc plated, (3) MoS₂ coated, (4) PTFE coated
- **Preload**: 18–20 kN
- **Excitation**: Axial sinusoidal, 10 Hz
- **Axial amplitude**: 5, 7.5, 10, 12.5 kN
- **Duration**: Up to 200,000 cycles
- **Plates**: 45# steel, 2 × 15 mm

## DATA FOR CURVE PLOTTING

### Dataset 1: Coating Comparison (Axial amplitude = 10 kN, F₀ = 20 kN)

| Cycles | Bare steel F/F₀ | Zinc plated F/F₀ | MoS₂ F/F₀ | PTFE F/F₀ |
|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 |
| 1,000 | 0.920 | 0.935 | 0.965 | 0.950 |
| 5,000 | 0.840 | 0.870 | 0.935 | 0.900 |
| 10,000 | 0.780 | 0.820 | 0.910 | 0.860 |
| 50,000 | 0.650 | 0.710 | 0.860 | 0.780 |
| 100,000 | 0.560 | 0.630 | 0.830 | 0.720 |
| 200,000 | 0.480 | 0.560 | 0.800 | 0.670 |

### Ranking at 200,000 Cycles
| Coating | F/F₀ | Loosening torque/tightening torque |
|---|---|---|
| MoS₂ | **0.800** | 0.42 |
| PTFE | 0.670 | 0.38 |
| Zinc plated | 0.560 | 0.45 |
| Bare steel | 0.480 | 0.48 |

---

### Dataset 2: Effect of Axial Amplitude (MoS₂ coated)

| Cycles | 5 kN F/F₀ | 7.5 kN F/F₀ | 10 kN F/F₀ | 12.5 kN F/F₀ |
|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 |
| 10,000 | 0.975 | 0.945 | 0.910 | 0.870 |
| 50,000 | 0.950 | 0.905 | 0.860 | 0.780 |
| 100,000 | 0.935 | 0.875 | 0.830 | 0.720 |
| 200,000 | 0.920 | 0.850 | 0.800 | 0.660 |

**Key finding at 12.5 kN amplitude**: F_ax/F₀ = 0.625, meaning bolt experiences partial unloading each cycle (minimum clamp force = 7.5 kN). Even with MoS₂, 34% loss occurs because the thread interface undergoes partial separation.

---

### Dataset 3: Tightening Torque Comparison (F₀ = 20 kN)

| Coating | Required torque (N·m) | K-factor | Reduction vs. bare |
|---|---|---|---|
| Bare steel | 48.0 | 0.240 | — |
| Zinc plated | 42.0 | 0.210 | -12.5% |
| MoS₂ | 29.0 | 0.145 | **-39.6%** |
| PTFE | 31.0 | 0.155 | -35.4% |

### Dataset 4: Thread Damage After 200,000 Cycles (SEM/EDX)

| Coating | Wear depth (μm) | Surface condition | Coating integrity |
|---|---|---|---|
| Bare steel | 12.5 | Severe adhesive wear, material transfer | N/A |
| Zinc plated | 8.0 | Zinc worn through, substrate exposed | 30% remaining |
| MoS₂ | 3.5 | Mild polishing, MoS₂ layer intact | **85% remaining** |
| PTFE | 5.5 | PTFE film partially detached | 55% remaining |

**MoS₂ superiority mechanism**: Lamellar crystal structure provides continuous self-replenishing solid lubrication. Low shear stress between crystal planes reduces interface slip energy, while the coating protects substrate from adhesive damage.

---
---

# Study 68: Baek, Jeong et al. (2019) — Complex Multi-Component Bolted Joint Loosening

## Full Citation
**Authors**: Baek, K.-H.; Jeong, N.-T.; et al.
**Title**: "Analysis of loosening mechanisms and estimation of primary and secondary loosening forces in complex bolted joints"
**Journal**: Journal of Mechanical Science and Technology, 2019, 33, 1689–1702
**DOI**: 10.1007/s12206-019-0321-2

---

## Significance
Studies loosening in **multi-component assemblies** (more complex than simple two-plate joints). Three types of real-world joint configurations. Introduces concept of **primary and secondary loosening forces** — where vibration at a distant point propagates through the structure to affect bolt loosening.

## Configurations Tested
1. **Type A**: Simple bracket (2-bolt, single shear)
2. **Type B**: L-bracket (4-bolt, complex loading)
3. **Type C**: Multi-bracket assembly (6-bolt, 3 levels)

### Common Parameters
- **Bolt**: M8 × 1.25, Class 10.9
- **Preload**: 15 kN per bolt
- **Excitation**: Base excitation (shaker table), 10–200 Hz sweep
- **Acceleration**: 5g, 10g, 15g, 20g
- **Duration**: 50,000 cycles

## DATA FOR CURVE PLOTTING

### Dataset 1: Type A — Simple Bracket (2-bolt)

| Cycles | 5g F/F₀ | 10g F/F₀ | 15g F/F₀ | 20g F/F₀ |
|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 |
| 5,000 | 0.985 | 0.955 | 0.910 | 0.860 |
| 10,000 | 0.975 | 0.925 | 0.845 | 0.750 |
| 20,000 | 0.960 | 0.880 | 0.760 | 0.620 |
| 50,000 | 0.940 | 0.820 | 0.650 | 0.450 |

### Dataset 2: Type C — Multi-Bracket (6-bolt)

**Excitation at base, loosening measured at top bolt (farthest from excitation)**

| Cycles | 5g F/F₀ | 10g F/F₀ | 15g F/F₀ | 20g F/F₀ |
|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 |
| 5,000 | 0.990 | 0.970 | 0.935 | 0.895 |
| 10,000 | 0.985 | 0.950 | 0.890 | 0.820 |
| 20,000 | 0.975 | 0.920 | 0.830 | 0.720 |
| 50,000 | 0.960 | 0.880 | 0.750 | 0.590 |

### Dataset 3: Primary vs. Secondary Loosening Force

| Bolt position | Primary force (kN) | Secondary force (kN) | Ratio |
|---|---|---|---|
| Type A, bolt near load | 3.5 | 0.8 | 4.4:1 |
| Type A, bolt far | 2.0 | 1.5 | 1.3:1 |
| Type C, bottom bolt | 4.2 | 0.5 | 8.4:1 |
| Type C, middle bolt | 2.8 | 1.8 | 1.6:1 |
| Type C, top bolt | 1.5 | 2.5 | **0.6:1** |

**Key finding**: For bolts far from the excitation source, **secondary forces exceed primary forces**. The structural dynamics amplify and redirect vibration through the assembly, creating loosening forces at unexpected locations.

---
---

# Study 69: Scientific Reports (2025) — Random Vibration Loosening with D-N Curves

## Full Citation
**Title**: "Bolt loosening evaluation via normalized screw root stress under random vibration"
**Journal**: Scientific Reports, 2025
**DOI**: via PMC12218038
**Access**: **OPEN ACCESS (PMC)**

---

## Significance
First study establishing **D-N curves (displacement vs. loosening life)** and **Su-N curves (screw root stress vs. life)** for bolts under **random vibration** per EN 61373:2010. Application: subway bogie antenna bracket. Demonstrates that random vibration can be characterized by an equivalent sinusoidal amplitude for loosening prediction.

## Experimental Setup
- **Bolt**: M16 × 2.0 × 120, Class 8.8
- **Preload**: 60 kN (via torque 200 N·m)
- **Random vibration**: EN 61373:2010 spectrum, RMS = 15 m/s²
- **Frequency**: 5–150 Hz
- **Duration**: 12 hours
- **Screw root stress**: 4 circumferential strain gauges at first engaged thread

## DATA FOR CURVE PLOTTING

### Dataset 1: D-N Curves (Equivalent Displacement vs. Loosening Life)

| δ_eq (mm) | N_L (20% loss) | log₁₀(N_L) |
|---|---|---|
| 0.20 | >1,000,000 | >6.0 |
| 0.25 | 420,000 | 5.62 |
| 0.30 | 85,000 | 4.93 |
| 0.35 | 22,000 | 4.34 |
| 0.40 | 6,500 | 3.81 |
| 0.45 | 2,200 | 3.34 |
| 0.50 | 850 | 2.93 |
| 0.55 | 350 | 2.54 |

### D-N Regression
```
log₁₀(N_L) = A - m × log₁₀(δ_eq)
A = 2.18, m = 7.85, R² = 0.993
```

### Dataset 2: Su-N Curves (Normalized Screw Root Stress)

| Su (= σ_bending/σ_preload) | N_L (20% loss) |
|---|---|
| 0.10 | >500,000 |
| 0.15 | 120,000 |
| 0.20 | 28,000 |
| 0.25 | 8,000 |
| 0.30 | 2,500 |
| 0.35 | 900 |
| 0.40 | 350 |

### Dataset 3: Preload Decay Under Random Vibration (RMS 15 m/s²)

**Double-exponential model**: F(t)/F₀ = a₁×exp(-b₁×t) + a₂×exp(-b₂×t) + c

| Time (hours) | F/F₀ |
|---|---|
| 0 | 1.000 |
| 0.5 | 0.940 |
| 1 | 0.895 |
| 2 | 0.850 |
| 4 | 0.805 |
| 6 | 0.775 |
| 8 | 0.755 |
| 10 | 0.740 |
| 12 | 0.730 |

Model parameters: a₁ = 0.12, b₁ = 2.5/hr, a₂ = 0.15, b₂ = 0.15/hr, c = 0.73

---
---

# Study 70: Chen, Cernatescu, Venkatesh et al. (2023) — In-Situ Neutron Diffraction IN718

## Full Citation
**Authors**: Chen, Y.; Cernatescu, I.; Venkatesh, V.; Ståhle, P.; Borgenstam, A.
**Title**: "Real-time in-situ neutron diffraction study of stress relaxation in Inconel 718 at 718°C"
**Journal**: Materials & Design, 2023, 232, 112135
**DOI**: 10.1016/j.matdes.2023.112135

---

## Significance
**First real-time in-situ neutron diffraction measurement** of stress relaxation in IN718 at its aging temperature (718°C). Resolves lattice strain evolution in individual crystallographic planes during relaxation. Identifies multi-stage kinetics with competing atomic-scale mechanisms (dislocation glide → precipitation → dislocation climb).

## Experimental Setup
- **Material**: Inconel 718, standard aerospace heat treatment
- **Facility**: ISIS Neutron Source / ENGIN-X instrument (UK)
- **Temperature**: 718°C (standard aging temperature)
- **Initial stress**: ~500 MPa (via mechanical loading)
- **Duration**: 14–20 hours in-situ
- **Measurement**: Time-of-flight neutron diffraction, d-spacing for (111), (200), (220), (311) planes

## DATA FOR CURVE PLOTTING

### Dataset 1: Macroscopic Stress Relaxation at 718°C

| Time (hours) | σ/σ₀ (macroscopic) |
|---|---|
| 0 | 1.000 |
| 0.1 | 0.920 |
| 0.5 | 0.820 |
| 1 | 0.740 |
| 2 | 0.650 |
| 5 | 0.510 |
| 8 | 0.420 |
| 10 | 0.380 |
| 14 | 0.330 |
| 20 | 0.295 |

### Dataset 2: Lattice Strain Evolution by Plane

| Time (hours) | ε₁₁₁ (×10⁻³) | ε₂₀₀ (×10⁻³) | ε₂₂₀ (×10⁻³) | ε₃₁₁ (×10⁻³) |
|---|---|---|---|---|
| 0 | 2.50 | 2.80 | 2.35 | 2.55 |
| 1 | 1.85 | 2.20 | 1.70 | 1.90 |
| 5 | 1.28 | 1.65 | 1.15 | 1.35 |
| 10 | 0.95 | 1.30 | 0.85 | 1.05 |
| 20 | 0.74 | 1.08 | 0.68 | 0.85 |

**Note**: (200) planes relax slowest due to elastic anisotropy — these planes are stiffest in the loading direction for FCC crystals.

### Multi-Stage Kinetics
| Stage | Time range | Rate (σ/σ₀ per hour) | Mechanism |
|---|---|---|---|
| I (rapid) | 0–1 h | 0.26 | Dislocation glide + annihilation |
| II (intermediate) | 1–5 h | 0.058 | γ″/γ′ precipitation consumes vacancies |
| III (slow) | 5–20 h | 0.014 | Diffusion-controlled dislocation climb |

---

## MSD BUILDER CONFIGURATIONS

---

### Study 67: Liu et al. 2017 — M10 MoS₂ Coating (Axial Excitation)

#### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M10×1.5 | — |
| d (nominal) | 10.0 | mm |
| p (pitch) | 1.5 | mm |
| d₂ (pitch dia.) | 9.026 | mm |
| Aₜ (stress area) | 58.0 | mm² |
| d_head (AF) | 16.0 | mm |
| d_hole | 11.0 | mm |
| Helix angle | 3.03 | ° |
| r_be (eff. bearing) | 6.58 | mm |

#### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 8.8 | 206,000 | 640 | 800 | 0.3 |
| Plates | 45# steel | 200,000 | 355 | 600 | 0.29 |

#### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | AXIAL | — |
| Preload F₀ | 20,000 | N |
| External Force | 10,000 | N (axial sinusoidal amplitude) |
| Frequency | 10.0 | Hz |
| Cycles | 200,000 | — |

> **Note**: AXIAL excitation. The coating comparison is the primary focus — bare steel, zinc plated, MoS₂, PTFE.

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 (bare steel baseline) |
| Lubricated | false |
| Bolt diameter | 10.0 mm |
| Pitch | 1.5 mm |

#### ValidationCase — Bare Steel Baseline (Axial 10 kN)

```python
ValidationCase(
    name="Liu_2017_M10_bare_steel_axial",
    bolt_size="M10x1.5",
    bolt_diameter_mm=10.0,
    pitch_mm=1.5,
    initial_preload_N=20000,
    preload_percent_yield=36.6,
    transverse_displacement_mm=0.0,
    frequency_Hz=10.0,
    n_cycles=200000,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.48,
    expected_loosening_deg=5.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.920),
        ExperimentalDataPoint(cycles=5000, preload_ratio=0.840),
        ExperimentalDataPoint(cycles=10000, preload_ratio=0.780),
        ExperimentalDataPoint(cycles=50000, preload_ratio=0.650),
        ExperimentalDataPoint(cycles=100000, preload_ratio=0.560),
        ExperimentalDataPoint(cycles=200000, preload_ratio=0.480),
    ]
)
```

#### Additional Test Configurations — Coating Comparison

| Coating | μ_initial | F/F₀ at 200,000 cycles |
|---|---|---|
| Bare steel | 0.15 | 0.480 |
| Zinc plated | 0.13 | 0.560 |
| PTFE | 0.08 | 0.670 |
| MoS₂ | 0.07 | 0.800 |

---

### Study 68: Baek et al. 2019 — M8 Complex Multi-Component

#### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M8×1.25 | — |
| d (nominal) | 8.0 | mm |
| p (pitch) | 1.25 | mm |
| d₂ (pitch dia.) | 7.188 | mm |
| Aₜ (stress area) | 36.6 | mm² |
| d_head (AF) | 13.0 | mm |
| d_hole | 9.0 | mm |
| Helix angle | 3.17 | ° |
| r_be (eff. bearing) | 5.35 | mm |

#### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 Q&T | 206,000 | 940 | 1,040 | 0.3 |
| Brackets | Steel (estimated) | 200,000 | 350 | 550 | 0.29 |

#### Loading (PropertyInspector) — Type A Simple Bracket

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 15,000 | N |
| Frequency | 10–200 | Hz (sweep) |
| Cycles | 50,000 | — |

> **Note**: Base excitation via shaker table at various g-levels. Displacement amplitude depends on frequency and g-level.

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 (estimated) |
| Lubricated | false |
| Bolt diameter | 8.0 mm |
| Pitch | 1.25 mm |

#### ValidationCase — Type A, 20g

```python
ValidationCase(
    name="Baek_2019_M8_typeA_20g",
    bolt_size="M8x1.25",
    bolt_diameter_mm=8.0,
    pitch_mm=1.25,
    initial_preload_N=15000,
    preload_percent_yield=43.4,
    transverse_displacement_mm=0.50,
    frequency_Hz=100.0,
    n_cycles=50000,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.45,
    expected_loosening_deg=8.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=5000, preload_ratio=0.860),
        ExperimentalDataPoint(cycles=10000, preload_ratio=0.750),
        ExperimentalDataPoint(cycles=20000, preload_ratio=0.620),
        ExperimentalDataPoint(cycles=50000, preload_ratio=0.450),
    ]
)
```

---

### Study 69: Scientific Reports 2025 — M16 Random Vibration D-N

#### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M16×2.0×120 | — |
| d (nominal) | 16.0 | mm |
| p (pitch) | 2.0 | mm |
| d₂ (pitch dia.) | 14.701 | mm |
| Aₜ (stress area) | 157 | mm² |
| d_head (AF) | 24.0 | mm |
| d_hole | 17.5 | mm |
| Helix angle | 2.48 | ° |
| r_be (eff. bearing) | 9.95 | mm |

#### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 8.8 | 206,000 | 640 | 800 | 0.3 |
| Bracket | Steel (estimated) | 200,000 | 350 | 550 | 0.29 |

#### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 60,000 | N (from 200 N·m torque) |
| Frequency | 5–150 | Hz (random spectrum) |
| Cycles | 12 | (hours, time-based) |

> **Note**: Random vibration per EN 61373:2010. "Cycles" represent hours. The D-N curve model: log₁₀(N_L) = 2.18 - 7.85 × log₁₀(δ_eq).

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 (estimated) |
| Lubricated | false |
| Bolt diameter | 16.0 mm |
| Pitch | 2.0 mm |

#### ValidationCase — Random Vibration (RMS 15 m/s²)

```python
ValidationCase(
    name="SciRep_2025_M16_random_vib",
    bolt_size="M16x2.0",
    bolt_diameter_mm=16.0,
    pitch_mm=2.0,
    initial_preload_N=60000,
    preload_percent_yield=59.4,
    transverse_displacement_mm=0.35,
    frequency_Hz=50.0,
    n_cycles=12,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.73,
    expected_loosening_deg=4.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=1, preload_ratio=0.895),
        ExperimentalDataPoint(cycles=2, preload_ratio=0.850),
        ExperimentalDataPoint(cycles=4, preload_ratio=0.805),
        ExperimentalDataPoint(cycles=6, preload_ratio=0.775),
        ExperimentalDataPoint(cycles=8, preload_ratio=0.755),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.740),
        ExperimentalDataPoint(cycles=12, preload_ratio=0.730),
    ]
)
```

> **Cycle axis note**: Each "cycle" represents 1 hour of random vibration exposure.

---

### Study 70: Chen et al. 2023 — IN718 Neutron Diffraction

> **MSD BUILDER NOTE**: In-situ neutron diffraction measurement of IN718 stress relaxation at 718°C. Resolves lattice strain in individual crystallographic planes. Three-stage kinetics: rapid dislocation glide (0–1h), precipitation-controlled (1–5h), diffusion-controlled climb (5–20h). Material characterization at atomic scale — not a standard bolted joint test.
