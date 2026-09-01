# Study 28: Zhao, Liu, Gong & Xue (2023) — Anti-Loosening Washers and Nuts: FEA Comparison

## Full Citation
**Authors**: Zhao, L.; Liu, J.; Gong, H.; Xue, L.
**Title**: "Study on Tightening, Anti-Loosening, and Fatigue Resistance Performances of Bolted Joints with Different Anti-Loosening Washers and Nuts"
**Journal**: Applied Sciences (MDPI), 2023, 13(24), 13253
**DOI**: 10.3390/app132413253
**Access**: **OPEN ACCESS**
**URL**: https://www.mdpi.com/2076-3417/13/24/13253

---

## Significance
Most comprehensive recent FEA comparison of **seven anti-loosening device types** under identical conditions. Uses full 3D helical thread modeling in ABAQUS. Evaluates tightening torque-angle curves, preload decay, and fatigue performance. Directly comparable to the DIN 25201-4 experimental data in Study 18.

---

## FEA Model

### Bolt Specifications
- **Size**: M10 × 1.5
- **Property class**: 10.9
- **Material**: 40Cr steel (≈ AISI 5140)

### Material Properties
| Component | E (MPa) | ν | σ_y (MPa) | σ_u (MPa) | Model |
|---|---|---|---|---|---|
| Bolt/nut (40Cr) | 211,000 | 0.30 | 835 | 980 | Bilinear kinematic |
| Washer (65Mn) | 210,000 | 0.28 | 785 | 980 | Bilinear kinematic |
| Plates (Q235) | 210,000 | 0.30 | 235 | 375 | Bilinear kinematic |

### FEA Parameters
| Parameter | Value |
|---|---|
| Software | ABAQUS 2020 |
| Solver | Explicit (quasi-static) |
| Element type | C3D8R |
| Total elements | ~120,000 |
| Thread | Full 3D helical, 6 engaged pitches |
| Contact | General contact, penalty method |
| Friction μ (thread) | 0.15 |
| Friction μ (bearing) | 0.15 |
| Mass scaling | Factor 100 (verified kinetic/internal <5%) |

### Loading Protocol
1. **Step 1 — Tightening**: Nut rotation to achieve target preload ~40 kN
2. **Step 2 — Stabilize**: Hold for 0.1 s
3. **Step 3 — Transverse vibration**: ±0.5 mm at 10 Hz, 30 cycles

---

## Seven Device Types Modeled

| # | Device | Mechanism | Key feature |
|---|---|---|---|
| 1 | Plain bolt + nut (reference) | Friction only | No anti-loosening |
| 2 | Plain washer | Distributes load | No anti-loosening |
| 3 | Wedge washer (Nord-Lock type) | Cam action, positive locking | Cam angle > thread pitch angle |
| 4 | Wedge-locking nut | Eccentric thread | Non-concentric threads create friction |
| 5 | Variable-diameter nut | Tapered thread | Thread interference at top |
| 6 | Eccentric double nut | Misaligned threads | Cross-loading between nuts |
| 7 | Double-thread bolt | Two pitch spirals | Interference between pitches |

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Preload Decay Comparison (All 7 devices, 30 cycles)

**[From FEA — Figures 10–12]**

| Cycles | Plain (ref) | Plain washer | Wedge washer | Wedge nut | Var-dia nut | Ecc. double | Dbl-thread |
|---|---|---|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 1 | 0.965 | 0.968 | 0.990 | 0.985 | 0.988 | 0.978 | 0.982 |
| 2 | 0.935 | 0.940 | 0.985 | 0.975 | 0.980 | 0.960 | 0.968 |
| 5 | 0.870 | 0.878 | 0.975 | 0.955 | 0.968 | 0.925 | 0.940 |
| 10 | 0.780 | 0.795 | 0.965 | 0.935 | 0.952 | 0.880 | 0.905 |
| 15 | 0.700 | 0.720 | 0.958 | 0.920 | 0.940 | 0.840 | 0.875 |
| 20 | 0.630 | 0.655 | 0.952 | 0.908 | 0.932 | 0.805 | 0.848 |
| 25 | 0.570 | 0.600 | 0.948 | 0.898 | 0.925 | 0.775 | 0.825 |
| 30 | 0.520 | 0.555 | 0.945 | 0.890 | 0.920 | 0.748 | 0.805 |

### Preload Retention at 30 Cycles (Ranked)

| Rank | Device | F/F₀ at 30 cycles | % retained |
|---|---|---|---|
| 1 | Wedge washer (Nord-Lock) | 0.945 | **94.5%** |
| 2 | Variable-diameter nut | 0.920 | 92.0% |
| 3 | Wedge-locking nut | 0.890 | 89.0% |
| 4 | Double-thread bolt | 0.805 | 80.5% |
| 5 | Eccentric double nut | 0.748 | 74.8% |
| 6 | Plain washer | 0.555 | 55.5% |
| 7 | Plain bolt + nut | 0.520 | 52.0% |

---

### Dataset 2: Nut Rotation Comparison

| Cycles | θ Plain (°) | θ Wedge washer (°) | θ Var-dia nut (°) |
|---|---|---|---|
| 0 | 0.0 | 0.0 | 0.0 |
| 5 | 2.8 | 0.2 | 0.5 |
| 10 | 6.5 | 0.4 | 0.9 |
| 15 | 10.8 | 0.5 | 1.2 |
| 20 | 15.2 | 0.6 | 1.4 |
| 25 | 19.5 | 0.7 | 1.5 |
| 30 | 23.8 | 0.8 | 1.6 |

---

### Dataset 3: Tightening Torque-Angle Curves

| Rotation angle (°) | Torque — Plain (N·m) | Torque — Wedge washer (N·m) | Torque — Var-dia nut (N·m) |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 90 | 12 | 14 | 18 |
| 180 | 28 | 32 | 38 |
| 270 | 48 | 55 | 62 |
| 360 | 72 | 80 | 88 |

Wedge washer requires ~10% more torque; variable-diameter nut ~22% more.

---

### Dataset 4: Fatigue Life Comparison (Von Mises at Critical Thread Root)

| Device | Max σ_VM at thread root (MPa) | Fatigue life estimate (cycles) | Relative to plain |
|---|---|---|---|
| Plain | 685 | 150,000 | 1.0× |
| Plain washer | 670 | 170,000 | 1.13× |
| Wedge washer | 690 | 145,000 | 0.97× |
| Wedge-locking nut | 720 | 120,000 | 0.80× |
| Variable-diameter nut | 750 | 95,000 | 0.63× |
| Eccentric double nut | 710 | 130,000 | 0.87× |
| Double-thread bolt | 730 | 110,000 | 0.73× |

**Key finding**: Anti-loosening devices that work by creating thread interference (variable-diameter nut, wedge-locking nut) tend to **increase thread root stress**, which **reduces fatigue life**. Wedge washers avoid this issue because they act at the bearing surface, not the threads.

---

## Design Recommendations

1. **Wedge washers** provide the best combination: highest anti-loosening with minimal fatigue penalty
2. Variable-diameter nuts retain preload well but reduce fatigue life by ~37%
3. Plain washers provide **negligible** anti-loosening benefit (only 3.5% improvement)
4. For fatigue-critical applications, avoid thread-based anti-loosening devices

---

## Reproduction Parameters

| Parameter | Value | Units |
|---|---|---|
| Bolt | M10 × 1.5 | — |
| Class | 10.9 (40Cr) | — |
| Preload | ~40 | kN |
| Amplitude | ±0.5 | mm |
| Frequency | 10 | Hz |
| Cycles modeled | 30 | — |
| μ (all surfaces) | 0.15 | — |
| Plate material | Q235 steel | — |
| Solver | ABAQUS 2020 Explicit | — |
| Elements | ~120,000 C3D8R | — |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this FEA study.
> Reference (plain bolt + nut) configuration. Anti-loosening devices modeled via modified friction/stiffness.

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
| Washer (65Mn) | Spring steel | 210,000 | 785 | 980 | 0.28 |
| Plates (Q235) | Structural steel | 210,000 | 235 | 375 | 0.30 |

### MSD Element Chain — Plain Reference

```
GROUND — FLANGE — FLANGE — NUT — THREAD — SHANK — HEAD — GROUND
```

### Loading (PropertyInspector) — FEA Baseline

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 40,000 | N |
| % Yield | 73.3 | % |
| Transverse disp. δ | 0.50 | mm |
| Frequency | 10.0 | Hz |
| Cycles | 30 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 |
| Lubricated | false |
| Bolt diameter | 10.0 mm |
| Pitch | 1.5 mm |

### Anti-Loosening Device Configurations

| Config | Device | μ_effective | k_modifier | Notes |
|---|---|---|---|---|
| Plain (ref) | None | 0.15 | 1.0× | Standard bolt + nut |
| Wedge washer | Nord-Lock | 0.15 + cam | 1.2× | Cam angle > helix angle |
| Wedge-lock nut | Eccentric thread | 0.20 | 1.0× | Higher effective μ |
| Variable-dia nut | Tapered | 0.18 | 1.0× | Thread interference |
| Double-thread | Two spirals | 0.15 | 1.0× | Pitch interference |

### ValidationCase — Plain Bolt Reference

```python
ValidationCase(
    name="Zhao_2023_M10_plain_FEA",
    bolt_size="M10x1.5",
    bolt_diameter_mm=10.0,
    pitch_mm=1.5,
    initial_preload_N=40000,
    preload_percent_yield=73.3,
    transverse_displacement_mm=0.50,
    frequency_Hz=10.0,
    n_cycles=30,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.520,
    expected_loosening_deg=23.8,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=1, preload_ratio=0.965),
        ExperimentalDataPoint(cycles=2, preload_ratio=0.935),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.870),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.780),
        ExperimentalDataPoint(cycles=15, preload_ratio=0.700),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.630),
        ExperimentalDataPoint(cycles=25, preload_ratio=0.570),
        ExperimentalDataPoint(cycles=30, preload_ratio=0.520),
    ]
)
```
