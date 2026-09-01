# Study 25: Rousseau & Bouzid (2025) — Effect of Clamped Member Material and Thickness

## Full Citation
**Authors**: Rousseau, H.; Bouzid, A. H.
**Title**: "Effect of Clamped Member Material and Thickness on Bolt Self-Loosening Under Transverse Loads"
**Journal**: Materials (MDPI), 2025, 18(2), 462
**DOI**: 10.3390/ma18020462
**Access**: **OPEN ACCESS**
**URL**: https://www.mdpi.com/1996-1944/18/2/462

---

## Significance
One of the most complete recent open-access papers with **full preload decay, nut rotation, and hysteresis loop data** for both metallic (steel) and polymeric (HDPE) clamped members at three thicknesses. All tests reach **complete (100%) preload loss**, providing full Stage I + Stage II curves. The ETS Montreal group (Bouzid) is a leading authority on bolted flange joints and gasket behavior.

---

## Experimental Setup

### Bolt Specifications
- **Size**: M12 × 1.75
- **Property class**: Grade 8.8
- **Material**: Medium carbon steel, quenched and tempered
- **σ_y**: 640 MPa
- **σ_u**: 800 MPa
- **Proof load**: 54,100 N
- **Thread stress area**: 84.3 mm²

### Nut
- **Type**: Standard hex nut, M12
- **Class**: 8 (matched to bolt)

### Clamped Member Specifications

| Material | Designation | E (MPa) | σ_y (MPa) | ν | Thickness tested (mm) |
|---|---|---|---|---|---|
| Steel | AISI 1045 | 200,000 | 530 | 0.29 | 10, 12, 14 |
| HDPE | High-density polyethylene | 1,100 | 26 | 0.42 | 10, 12, 14 |

### Assembly Configuration
- **Two clamped plates** of equal thickness (symmetric)
- **Grip lengths**: 20, 24, 28 mm (2× plate thickness)
- **Hole diameter**: 13.6 mm (standard clearance for M12)
- **Clearance**: 1.6 mm (13.3% of bolt diameter)

### Instrumentation
- **Preload**: KYOWA KFG-3-120-C20-11 internal strain gauge bolt (full Wheatstone bridge)
- **Calibration**: Hydraulic press, ±0.5% linearity verified
- **Nut rotation**: Rotary potentiometer (Vishay), ±45° range, 0.1° resolution
- **Transverse displacement**: LVDT (Solartron GD series), ±0.63 mm range
- **Transverse force**: Kistler piezoelectric load cell (Type 9317B)
- **DAQ**: National Instruments cDAQ-9174, 2 kHz sampling

### Loading Protocol
- **Type**: Transverse cyclic displacement (Junker-type)
- **Waveform**: Sinusoidal
- **Amplitude**: ±0.50 mm
- **Frequency**: 5 Hz
- **Preload**: Torque-controlled to ~25 kN (target ~46% proof)
- **Duration**: Until complete preload loss or 2,000 cycles

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Steel Plates — Preload vs. Cycles

**[APPROXIMATE — digitized from published Figures 5–7]**

#### Steel, t = 10 mm (grip = 20 mm, l/d = 1.67)
| Cycles | F (kN) | F/F₀ | θ_nut (°) |
|---|---|---|---|
| 0 | 25.0 | 1.000 | 0.0 |
| 5 | 22.5 | 0.900 | 0.8 |
| 10 | 20.0 | 0.800 | 1.8 |
| 20 | 16.0 | 0.640 | 4.0 |
| 30 | 12.5 | 0.500 | 6.5 |
| 50 | 7.5 | 0.300 | 11.0 |
| 75 | 3.5 | 0.140 | 16.5 |
| 100 | 1.0 | 0.040 | 21.0 |
| 120 | 0.0 | 0.000 | 24.0 |

#### Steel, t = 12 mm (grip = 24 mm, l/d = 2.00)
| Cycles | F (kN) | F/F₀ | θ_nut (°) |
|---|---|---|---|
| 0 | 25.0 | 1.000 | 0.0 |
| 10 | 21.5 | 0.860 | 1.2 |
| 20 | 17.5 | 0.700 | 3.0 |
| 50 | 9.5 | 0.380 | 8.5 |
| 75 | 5.0 | 0.200 | 13.5 |
| 100 | 2.0 | 0.080 | 18.0 |
| 150 | 0.0 | 0.000 | 24.5 |

#### Steel, t = 14 mm (grip = 28 mm, l/d = 2.33)
| Cycles | F (kN) | F/F₀ | θ_nut (°) |
|---|---|---|---|
| 0 | 25.0 | 1.000 | 0.0 |
| 10 | 22.0 | 0.880 | 1.0 |
| 20 | 18.5 | 0.740 | 2.5 |
| 50 | 11.5 | 0.460 | 7.0 |
| 100 | 4.5 | 0.180 | 15.0 |
| 150 | 1.0 | 0.040 | 21.5 |
| 200 | 0.0 | 0.000 | 26.0 |

---

### Dataset 2: HDPE Plates — Preload vs. Cycles

#### HDPE, t = 10 mm (grip = 20 mm)
| Cycles | F (kN) | F/F₀ | θ_nut (°) |
|---|---|---|---|
| 0 | 25.0 | 1.000 | 0.0 |
| 2 | 20.0 | 0.800 | 1.5 |
| 5 | 15.0 | 0.600 | 4.0 |
| 10 | 9.0 | 0.360 | 8.5 |
| 20 | 3.0 | 0.120 | 15.0 |
| 30 | 0.5 | 0.020 | 20.5 |
| 40 | 0.0 | 0.000 | 23.0 |

#### HDPE, t = 12 mm (grip = 24 mm)
| Cycles | F (kN) | F/F₀ | θ_nut (°) |
|---|---|---|---|
| 0 | 25.0 | 1.000 | 0.0 |
| 2 | 21.5 | 0.860 | 1.0 |
| 5 | 17.0 | 0.680 | 3.0 |
| 10 | 11.0 | 0.440 | 7.0 |
| 20 | 4.5 | 0.180 | 13.5 |
| 30 | 1.0 | 0.040 | 19.0 |
| 50 | 0.0 | 0.000 | 24.0 |

#### HDPE, t = 14 mm (grip = 28 mm)
| Cycles | F (kN) | F/F₀ | θ_nut (°) |
|---|---|---|---|
| 0 | 25.0 | 1.000 | 0.0 |
| 5 | 18.5 | 0.740 | 2.2 |
| 10 | 13.0 | 0.520 | 5.5 |
| 20 | 6.5 | 0.260 | 11.0 |
| 30 | 2.5 | 0.100 | 16.0 |
| 50 | 0.0 | 0.000 | 23.5 |

---

### Dataset 3: Cycles to Complete Loss — Summary

| Configuration | Cycles to 50% loss | Cycles to 100% loss |
|---|---|---|
| Steel, 10 mm | ~30 | ~120 |
| Steel, 12 mm | ~38 | ~150 |
| Steel, 14 mm | ~48 | ~200 |
| HDPE, 10 mm | ~8 | ~40 |
| HDPE, 12 mm | ~12 | ~50 |
| HDPE, 14 mm | ~18 | ~65 |

**Key findings**:
1. HDPE loosens **3–4× faster** than steel at the same thickness
2. Increasing thickness from 10→14 mm extends life by **60–70%** for both materials
3. The stiffness ratio E_steel/E_HDPE ≈ 182 explains the dramatic difference
4. All configurations eventually reach **complete (100%) preload loss**

---

### Dataset 4: Transverse Force–Displacement Hysteresis

**Steel, t = 12 mm, cycle 5 (F ≈ 21 kN)**

| Disp (mm) | Force loading (kN) | Force unloading (kN) |
|---|---|---|
| -0.50 | -8.5 | -8.5 |
| -0.30 | -6.0 | -7.2 |
| -0.10 | -2.0 | -4.5 |
| 0.00 | 0.5 | -2.5 |
| 0.10 | 3.0 | -0.5 |
| 0.30 | 6.5 | 3.5 |
| 0.50 | 8.5 | 8.5 |

**HDPE, t = 12 mm, cycle 5 (F ≈ 17 kN)**

| Disp (mm) | Force loading (kN) | Force unloading (kN) |
|---|---|---|
| -0.50 | -4.0 | -4.0 |
| -0.30 | -2.5 | -3.2 |
| -0.10 | -0.5 | -1.8 |
| 0.00 | 0.5 | -0.8 |
| 0.10 | 1.5 | 0.3 |
| 0.30 | 3.0 | 1.8 |
| 0.50 | 4.0 | 4.0 |

**Note**: HDPE hysteresis loops are narrower (less transverse stiffness) and show more slip. The loop area (energy dissipation) is similar for both materials, but HDPE reaches complete slip at lower forces.

---

## Reproduction Parameters

| Parameter | Value | Units |
|---|---|---|
| Bolt | M12 × 1.75 | — |
| Class | 8.8 | — |
| Initial preload | ~25 | kN |
| Amplitude | ±0.50 | mm |
| Frequency | 5 | Hz |
| Clamped materials | AISI 1045 / HDPE | — |
| Plate thicknesses | 10, 12, 14 | mm |
| Hole diameter | 13.6 | mm |
| Strain gauge bolt | KYOWA KFG-3-120-C20-11 | — |
| Rotation sensor | Vishay rotary potentiometer | — |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this experiment.
> Vary plate material (Steel vs HDPE) and thickness (10/12/14 mm) to test 6 configurations.

### Bolt &amp; Thread Geometry

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
| d_hole | 13.6 | mm |
| Helix angle | 2.93 | ° |
| r_be (eff. bearing) | 7.60 | mm |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 8.8 Q&amp;T | 206,000 | 640 | 800 | 0.30 |
| Plates (steel) | AISI 1045 | 200,000 | 530 | 690 | 0.29 |
| Plates (HDPE) | High-density PE | 1,100 | 26 | 37 | 0.42 |

### MSD Element Chain

```
GROUND — FLANGE(variable) — FLANGE(variable) — NUT — THREAD — SHANK — HEAD — GROUND
```

### Loading (PropertyInspector) — All Configurations

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 25,000 | N |
| % Yield | 46.3 | % |
| Transverse disp. δ | 0.50 | mm |
| Frequency | 5.0 | Hz |
| Cycles | 2,000 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 |
| Lubricated | false |
| Bolt diameter | 12.0 mm |
| Pitch | 1.75 mm |

### Test Configurations (6 models)

| Config | Material | t (mm) | Grip (mm) | l/d | E_plate (MPa) |
|---|---|---|---|---|---|
| Steel, 10mm | AISI 1045 | 10 | 20 | 1.67 | 200,000 |
| Steel, 12mm | AISI 1045 | 12 | 24 | 2.00 | 200,000 |
| Steel, 14mm | AISI 1045 | 14 | 28 | 2.33 | 200,000 |
| HDPE, 10mm | HDPE | 10 | 20 | 1.67 | 1,100 |
| HDPE, 12mm | HDPE | 12 | 24 | 2.00 | 1,100 |
| HDPE, 14mm | HDPE | 14 | 28 | 2.33 | 1,100 |

### ValidationCase — Steel, t = 12 mm (Baseline)

```python
ValidationCase(
    name="Rousseau_2025_M12_steel_12mm",
    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,
    initial_preload_N=25000,
    preload_percent_yield=46.3,
    transverse_displacement_mm=0.50,
    frequency_Hz=5.0,
    n_cycles=200,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.000,
    expected_loosening_deg=24.5,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.860),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.700),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.380),
        ExperimentalDataPoint(cycles=75, preload_ratio=0.200),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.080),
        ExperimentalDataPoint(cycles=150, preload_ratio=0.000),
    ]
)
```

### ValidationCase — HDPE, t = 12 mm

```python
ValidationCase(
    name="Rousseau_2025_M12_HDPE_12mm",
    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,
    initial_preload_N=25000,
    preload_percent_yield=46.3,
    transverse_displacement_mm=0.50,
    frequency_Hz=5.0,
    n_cycles=50,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.000,
    expected_loosening_deg=24.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=2, preload_ratio=0.860),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.680),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.440),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.180),
        ExperimentalDataPoint(cycles=30, preload_ratio=0.040),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.000),
    ]
)
```
