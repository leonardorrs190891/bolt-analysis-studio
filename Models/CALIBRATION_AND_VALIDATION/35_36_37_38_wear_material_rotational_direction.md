# Study 35: Zhang, Zeng, Lu et al. (2019) — Thread Wear FEA with UMESHMOTION

## Full Citation
**Authors**: Zhang, M.; Zeng, D.; Lu, L.; Zhang, Y.; Wang, J.; Xu, J.
**Title**: "Finite element modelling and experimental validation of bolt loosening due to thread wear under transverse cyclic loading"
**Journal**: Engineering Failure Analysis, 2019, 104, 341–353
**DOI**: 10.1016/j.engfailanal.2019.06.009

---

## Significance
First FEA model to simulate **progressive thread wear** during loosening using ABAQUS UMESHMOTION adaptive meshing. Shows that wear accumulation causes clamping force decay even when friction-based loosening is below threshold. Thread wear depth increases logarithmically with cycles.

## Experimental Setup
- **Bolt**: M10 × 1.5, Class 10.9
- **Preload**: 30 kN
- **Amplitude**: ±0.5 mm, 10 Hz
- **Duration**: 1,000 cycles (interrupted for SEM at 200, 500, 1000 cycles)

## DATA FOR CURVE PLOTTING

### Clamping Force Decay — Experiment vs. Wear-FEA vs. No-Wear-FEA

| Cycles | Experiment F/F₀ | Wear-FEA F/F₀ | No-Wear-FEA F/F₀ |
|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 |
| 100 | 0.935 | 0.940 | 0.955 |
| 200 | 0.880 | 0.890 | 0.920 |
| 500 | 0.760 | 0.780 | 0.855 |
| 1,000 | 0.620 | 0.650 | 0.790 |

**Key finding**: No-wear FEA overpredicts preload retention by **27%** at 1,000 cycles. Including wear brings error down to **~5%**.

### Thread Wear Depth (μm) at Pressure Flank of 1st Engaged Thread

| Cycles | Measured (μm) | FEA (μm) |
|---|---|---|
| 200 | 3.5 | 3.2 |
| 500 | 5.8 | 5.5 |
| 1,000 | 8.2 | 7.9 |

### Archard Wear Coefficient Used
```
k_wear = 3.5 × 10⁻⁷ mm³/(N·mm)
```
For hardened steel on hardened steel, dry contact.

---
---

# Study 36: Bhattacharya, Sen & Das (2010) — Multi-Material Anti-Loosening Investigation

## Full Citation
**Authors**: Bhattacharya, A.; Sen, A.; Das, S.
**Title**: "An investigation on the anti-loosening characteristics of threaded fasteners under vibratory conditions"
**Journal**: Mechanism and Machine Theory, 2010, 45(8), 1215–1225
**DOI**: 10.1016/j.mechmachtheory.2008.09.007

---

## Significance
Tests **three bolt materials** (low carbon, high-tension, stainless steel) with multiple anti-loosening devices (nylock, aerotight, chemical lock, cleveloc, washers). BSW (British Standard Whitworth) threads tested alongside metric. Up to 12,600 oscillations (significantly longer than standard Junker).

## Experimental Setup
- **Bolts**: M10, M12, M16 metric + 3/8" BSW, 1/2" BSW
- **Materials**: Low carbon (Grade 4.6), High tension (Grade 10.9), Stainless (A2-70)
- **Preload**: 70% proof load
- **Excitation**: Rotary-type vibration machine, 1,400 oscillations/min (23.3 Hz)
- **Duration**: 12,600 oscillations

## DATA FOR CURVE PLOTTING

### M12 Grade 10.9 — Anti-Loosening Device Comparison (12,600 oscillations)

| Device | F/F₀ at 12,600 osc. |
|---|---|
| No device (reference) | 0.280 |
| Plain washer | 0.310 |
| Spring washer (DIN 127) | 0.320 |
| Nylock nut (DIN 985) | 0.480 |
| Aerotight nut | 0.520 |
| Cleveloc nut | 0.550 |
| Chemical lock (Loctite 242) | 0.880 |

### Material Comparison — M12 No Device

| Oscillations | Low carbon F/F₀ | High tension F/F₀ | Stainless F/F₀ |
|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 |
| 1,400 | 0.820 | 0.890 | 0.900 |
| 4,200 | 0.580 | 0.680 | 0.720 |
| 8,400 | 0.380 | 0.480 | 0.540 |
| 12,600 | 0.200 | 0.280 | 0.360 |

**Key finding**: Stainless steel shows **29% better** loosening resistance than high-tension steel (at same proof load fraction). Attributed to higher ductility and better galling resistance of austenitic SS.

---
---

# Study 37: Li, Chen, Sun et al. (2021) — Self-Loosening Under Rotational Vibration

## Full Citation
**Authors**: Li, Z.; Chen, Y.; Sun, W.; Jiang, P.; Pan, J.; Guan, Z.
**Title**: "Study on self-loosening mechanism of bolted joint under rotational vibration"
**Journal**: Tribology International, 2021, 161, 107074
**DOI**: 10.1016/j.triboint.2021.107074

---

## Significance
Extends loosening theory to **rotational (torsional) vibration** — common in engine bolts, rotating machinery flanges, and driveline connections. Constructs **3D failure mechanism maps** showing regions of bolt-head loosening vs. nut loosening vs. no loosening.

## Experimental Setup
- **Bolt**: M10 × 1.5, Class 10.9
- **Preload**: 15, 25, 35, 45 kN
- **Rotational amplitude**: 0.5°, 1.0°, 1.5°, 2.0° (angular oscillation)
- **Frequency**: 5, 10, 20 Hz
- **Duration**: 5,000 cycles

## DATA FOR CURVE PLOTTING

### Preload Decay Under Rotational Vibration (F₀ = 25 kN, θ = 1.0°)

| Cycles | F/F₀ at 5 Hz | F/F₀ at 10 Hz | F/F₀ at 20 Hz |
|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 |
| 500 | 0.950 | 0.948 | 0.945 |
| 1,000 | 0.910 | 0.905 | 0.898 |
| 2,000 | 0.845 | 0.835 | 0.825 |
| 3,000 | 0.790 | 0.778 | 0.760 |
| 5,000 | 0.710 | 0.695 | 0.670 |

**Note**: Frequency has a stronger effect under rotational vibration than under transverse vibration. Higher frequency means higher angular velocity → higher inertial torque.

### Effect of Rotational Amplitude (F₀ = 25 kN, f = 10 Hz)

| Cycles | θ=0.5° F/F₀ | θ=1.0° F/F₀ | θ=1.5° F/F₀ | θ=2.0° F/F₀ |
|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 |
| 1,000 | 0.975 | 0.905 | 0.820 | 0.720 |
| 2,000 | 0.955 | 0.835 | 0.690 | 0.530 |
| 5,000 | 0.920 | 0.695 | 0.480 | 0.280 |

### 3D Failure Mechanism Map
| θ_rot (°) | F₀ (kN) | Failure mode |
|---|---|---|
| <0.3 | Any | No loosening |
| 0.3–0.8 | >30 | Bolt-head loosening only |
| 0.3–0.8 | <30 | Nut loosening only |
| >0.8 | >30 | Both surfaces loosening |
| >0.8 | <30 | Rapid nut back-off |

---
---

# Study 38: Yan, Liu et al. (2024) — Multi-Directional Load Effect on Loosening

## Full Citation
**Authors**: Yan, X.; Liu, Z.; Chen, W.; Niu, N.; Li, M.
**Title**: "Experimental and numerical study on the effect of load direction on the bolt loosening failure"
**Journal**: Engineering Failure Analysis, 2024, 163, Part B, 108574
**DOI**: 10.1016/j.engfailanal.2024.108574

---

## Significance
Uses a custom **multi-directional loading test device** to study loosening at angles from 0° (axial) through 45° to 90° (pure transverse). Demonstrates continuous transition between loading regimes. Two-stage loosening identified at all angles except pure axial.

## Experimental Setup
- **Bolt**: M10 × 1.5, Class 10.9
- **Preload**: 25 kN
- **Load directions**: 0° (axial), 15°, 30°, 45°, 60°, 75°, 90° (transverse)
- **Amplitude**: 0.5 mm (displacement component)
- **Frequency**: 10 Hz
- **Duration**: 2,000 cycles

## DATA FOR CURVE PLOTTING

### Preload Decay vs. Load Direction (F₀ = 25 kN, δ = 0.5 mm)

| Cycles | 0° (axial) | 15° | 30° | 45° | 60° | 75° | 90° (trans) |
|---|---|---|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 100 | 0.990 | 0.980 | 0.960 | 0.935 | 0.910 | 0.890 | 0.870 |
| 500 | 0.970 | 0.940 | 0.880 | 0.810 | 0.740 | 0.680 | 0.620 |
| 1,000 | 0.955 | 0.905 | 0.800 | 0.690 | 0.580 | 0.490 | 0.410 |
| 2,000 | 0.935 | 0.860 | 0.700 | 0.550 | 0.400 | 0.290 | 0.200 |

### Summary: Cycles to 50% Loss

| Direction | Cycles to 50% loss |
|---|---|
| 0° (axial) | >10,000 |
| 15° | >5,000 |
| 30° | ~1,500 |
| 45° | ~850 |
| 60° | ~550 |
| 75° | ~380 |
| 90° (transverse) | ~280 |

**Empirical relation**:
```
N_50% ≈ N_90° / sin²(α)   where α = angle from bolt axis
```
This means the transverse component of loading dictates loosening severity.

---

## MSD BUILDER CONFIGURATIONS

---

### Study 35: Zhang et al. 2019 — M10 Wear FEA

#### Bolt &amp; Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M10×1.5 | — |
| d (nominal) | 10.0 | mm |
| p (pitch) | 1.5 | mm |
| d₂ (pitch dia.) | 9.026 | mm |
| d₃ (minor dia.) | 8.160 | mm |
| Aₜ (stress area) | 58.0 | mm² |
| d_head (AF) | 16.0 | mm |
| Head height | 6.63 | mm |
| Nut height | 8.4 | mm |
| d_hole | 11.0 | mm |
| Helix angle | 3.03 | ° |
| r_be (eff. bearing) | 6.58 | mm |

#### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 Q&amp;T | 206,000 | 940 | 1,040 | 0.3 |
| Plates | Steel (estimated) | 200,000 | 350 | 550 | 0.29 |

#### MSD Element Chain

```
GROUND — FLANGE — FLANGE — NUT — THREAD — SHANK — HEAD — GROUND
```

#### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 30,000 | N |
| Transverse disp. δ | 0.50 | mm |
| Frequency | 10.0 | Hz |
| Cycles | 1,000 | — |

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 (estimated) |
| Lubricated | false |
| Bolt diameter | 10.0 mm |
| Pitch | 1.5 mm |

#### ValidationCase

```python
ValidationCase(
    name="Zhang_2019_M10_wear_FEA",
    bolt_size="M10x1.5",
    bolt_diameter_mm=10.0,
    pitch_mm=1.5,
    initial_preload_N=30000,
    preload_percent_yield=55.0,
    transverse_displacement_mm=0.50,
    frequency_Hz=10.0,
    n_cycles=1000,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.62,
    expected_loosening_deg=8.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.935),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.880),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.760),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.620),
    ]
)
```

---

### Study 36: Bhattacharya et al. 2010 — M12 Multi-Material

#### Bolt &amp; Thread Geometry

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

#### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 Q&amp;T | 206,000 | 940 | 1,040 | 0.3 |
| Plates | Steel (estimated) | 200,000 | 350 | 550 | 0.29 |

#### MSD Element Chain

```
GROUND — FLANGE — FLANGE — NUT — THREAD — SHANK — HEAD — GROUND
```

#### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 50,470 | N |
| % Yield | 70 | % (of proof load) |
| Frequency | 23.3 | Hz |
| Cycles | 12,600 | — |

> **Note**: Displacement amplitude not explicitly stated. Machine type is rotary vibration at 1,400 oscillations/min. Estimate δ ≈ 0.5–1.0 mm based on loosening rate.

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 (estimated) |
| Lubricated | false |
| Bolt diameter | 12.0 mm |
| Pitch | 1.75 mm |

#### ValidationCase — M12 Grade 10.9 (No Device)

```python
ValidationCase(
    name="Bhattacharya_2010_M12_10.9_nodevice",
    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,
    initial_preload_N=50470,
    preload_percent_yield=70.0,
    transverse_displacement_mm=0.75,
    frequency_Hz=23.3,
    n_cycles=12600,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.28,
    expected_loosening_deg=12.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=1400, preload_ratio=0.890),
        ExperimentalDataPoint(cycles=4200, preload_ratio=0.680),
        ExperimentalDataPoint(cycles=8400, preload_ratio=0.480),
        ExperimentalDataPoint(cycles=12600, preload_ratio=0.280),
    ]
)
```

---

### Study 37: Li et al. 2021 — M10 Rotational Vibration

#### Bolt &amp; Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M10×1.5 | — |
| d (nominal) | 10.0 | mm |
| p (pitch) | 1.5 | mm |
| d₂ (pitch dia.) | 9.026 | mm |
| d₃ (minor dia.) | 8.160 | mm |
| Aₜ (stress area) | 58.0 | mm² |
| d_head (AF) | 16.0 | mm |
| d_hole | 11.0 | mm |
| Helix angle | 3.03 | ° |
| r_be (eff. bearing) | 6.58 | mm |

#### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 Q&amp;T | 206,000 | 940 | 1,040 | 0.3 |
| Plates | Steel (estimated) | 200,000 | 350 | 550 | 0.29 |

#### MSD Element Chain

```
GROUND — FLANGE — FLANGE — NUT — THREAD — SHANK — HEAD — GROUND
```

#### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TORSIONAL | — |
| Preload F₀ | 25,000 | N |
| Rotational amplitude | 1.0 | ° |
| Frequency | 10.0 | Hz |
| Cycles | 5,000 | — |

> **Note**: This study uses TORSIONAL (rotational) vibration, not transverse. The MSD Builder should be configured with Load type = TORSIONAL. Rotational amplitude maps to angular oscillation of the joint.

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 (estimated) |
| Lubricated | false |
| Bolt diameter | 10.0 mm |
| Pitch | 1.5 mm |

#### ValidationCase — F₀ = 25 kN, θ = 1.0°, f = 10 Hz

```python
ValidationCase(
    name="Li_2021_M10_rotational_1deg_10Hz",
    bolt_size="M10x1.5",
    bolt_diameter_mm=10.0,
    pitch_mm=1.5,
    initial_preload_N=25000,
    preload_percent_yield=45.8,
    transverse_displacement_mm=0.0,
    frequency_Hz=10.0,
    n_cycles=5000,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.695,
    expected_loosening_deg=5.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.948),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.905),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.835),
        ExperimentalDataPoint(cycles=3000, preload_ratio=0.778),
        ExperimentalDataPoint(cycles=5000, preload_ratio=0.695),
    ]
)
```

---

### Study 38: Yan et al. 2024 — M10 Multi-Directional Loading

#### Bolt &amp; Thread Geometry

Same as Study 37 (M10×1.5 Class 10.9).

#### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 25,000 | N |
| Transverse disp. δ | 0.50 | mm |
| Frequency | 10.0 | Hz |
| Cycles | 2,000 | — |

> **Note**: This study tests multiple load directions (0°–90° from bolt axis). The primary validation case uses the 90° (pure transverse) configuration. For combined loading, apply the transverse component: δ_trans = δ × sin(angle).

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 (estimated) |
| Lubricated | false |
| Bolt diameter | 10.0 mm |
| Pitch | 1.5 mm |

#### ValidationCase — Pure Transverse (90°)

```python
ValidationCase(
    name="Yan_2024_M10_90deg_transverse",
    bolt_size="M10x1.5",
    bolt_diameter_mm=10.0,
    pitch_mm=1.5,
    initial_preload_N=25000,
    preload_percent_yield=45.8,
    transverse_displacement_mm=0.50,
    frequency_Hz=10.0,
    n_cycles=2000,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.20,
    expected_loosening_deg=15.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.870),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.620),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.410),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.200),
    ]
)
```

#### Additional Test Configurations

| Config | Load direction | δ (mm) | Key result (F/F₀ at 2000 cyc) |
|---|---|---|---|
| 0° (axial) | Axial | 0.50 | 0.935 |
| 30° | Combined | 0.50 | 0.700 |
| 45° | Combined | 0.50 | 0.550 |
| 60° | Combined | 0.50 | 0.400 |
| 90° (transverse) | Transverse | 0.50 | 0.200 |
