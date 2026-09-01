# Study 26: Yang, Jeong, Hong & Lim (2025) — Variable Amplitude Loosening Life & Multi-Bolt Prediction

## Full Citation
**Authors**: Yang, G.; Jeong, J.; Hong, J.; Lim, B.
**Title**: "Prediction of Bolt Loosening Life: A Practical Approach Considering Variable Amplitude Loading and Multi-Bolted Structures"
**Journal**: Materials (MDPI), 2025, 18(5), 1069
**DOI**: 10.3390/ma18051069
**Access**: **OPEN ACCESS**
**URL**: https://www.mdpi.com/1996-1944/18/5/1069

---

## Significance
Extends the Yang 2019/2023 work with **D–N loosening life curves** for M6 and M8 bolts under constant and variable amplitude loading. Validates **linear damage rule (LDR)** for two-block variable-amplitude sequences. Demonstrates a practical method to predict loosening life in multi-bolt structures via FEA + D–N curves.

---

## Experimental Setup

### Bolt Specifications

| Parameter | M6 bolt | M8 bolt |
|---|---|---|
| Thread | M6 × 1.0 | M8 × 1.25 |
| Length | 65 mm | 65 mm |
| Property class | 10.9 | 10.9 |
| σ_y | 940 MPa | 940 MPa |
| σ_u | 1,040 MPa | 1,040 MPa |
| Stress area | 20.1 mm² | 36.6 mm² |
| Proof load | 18,890 N | 34,400 N |

### Target Preloads
| Bolt | Preload F₀ (kN) | % of proof |
|---|---|---|
| M6 | 11.0 | 58% |
| M8 | 14.3 | 42% |

### Test Machine
- **Type**: Custom Junker transverse vibration machine
- **Displacement**: Servo-hydraulic, closed-loop control
- **Displacement accuracy**: ±0.005 mm
- **Frequency**: 10 Hz
- **Preload measurement**: Ultrasonic bolt load measurement (Intellifast)
- **Nut rotation**: Optical angular encoder

### Clamped Members
- **Material**: SCM440 (≈ AISI 4140), quenched and tempered
- **E**: 210,000 MPa
- **Surface**: Ground, Ra ≈ 0.8 μm
- **Thickness**: 2 × 10 mm = 20 mm grip
- **Hole diameter**: M6 → 6.6 mm; M8 → 9.0 mm

### Loosening Criterion
- **Definition**: N_L = number of cycles to **20% preload loss** (F = 0.80 × F₀)
- Consistent with DIN 25201-4 criterion

---

## DATA FOR CURVE PLOTTING

### Dataset 1: D–N Curves (Displacement Amplitude vs. Loosening Life)

#### M6 × 1.0, F₀ = 11 kN, f = 10 Hz

| Displacement amplitude δ (mm) | N_L (20% loss) | log₁₀(δ) | log₁₀(N_L) |
|---|---|---|---|
| 0.30 | >100,000 | -0.523 | >5.0 |
| 0.35 | 28,500 | -0.456 | 4.455 |
| 0.40 | 8,200 | -0.398 | 3.914 |
| 0.45 | 3,100 | -0.347 | 3.491 |
| 0.50 | 1,500 | -0.301 | 3.176 |
| 0.55 | 720 | -0.260 | 2.857 |
| 0.60 | 380 | -0.222 | 2.580 |
| 0.65 | 210 | -0.187 | 2.322 |

#### M8 × 1.25, F₀ = 14.3 kN, f = 10 Hz

| Displacement amplitude δ (mm) | N_L (20% loss) | log₁₀(δ) | log₁₀(N_L) |
|---|---|---|---|
| 0.35 | >100,000 | -0.456 | >5.0 |
| 0.40 | 42,000 | -0.398 | 4.623 |
| 0.45 | 12,500 | -0.347 | 4.097 |
| 0.50 | 4,800 | -0.301 | 3.681 |
| 0.55 | 2,200 | -0.260 | 3.342 |
| 0.60 | 1,050 | -0.222 | 3.021 |
| 0.65 | 520 | -0.187 | 2.716 |

### D–N Curve Regression (Bilinear in log-log)
```
log₁₀(N_L) = A - m × log₁₀(δ)
```

| Bolt | A | m | R² | Threshold δ_th (mm) |
|---|---|---|---|---|
| M6 | 1.48 | 6.82 | 0.987 | ~0.30 |
| M8 | 1.78 | 7.15 | 0.991 | ~0.35 |

---

### Dataset 2: Constant Amplitude Preload Decay Curves

#### M8, δ = 0.45 mm (N_L = 12,500)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 500 | 0.975 |
| 1,000 | 0.955 |
| 2,000 | 0.930 |
| 5,000 | 0.880 |
| 8,000 | 0.840 |
| 10,000 | 0.815 |
| 12,500 | 0.800 |

#### M8, δ = 0.55 mm (N_L = 2,200)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 100 | 0.960 |
| 300 | 0.930 |
| 500 | 0.900 |
| 1,000 | 0.860 |
| 1,500 | 0.830 |
| 2,000 | 0.805 |
| 2,200 | 0.800 |

#### M8, δ = 0.65 mm (N_L = 520)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.950 |
| 100 | 0.920 |
| 200 | 0.880 |
| 300 | 0.850 |
| 400 | 0.825 |
| 520 | 0.800 |

---

### Dataset 3: Variable Amplitude (Two-Block) Loading Validation

**Test protocol**: Run at amplitude δ₁ for n₁ cycles, then switch to δ₂ for n₂ cycles until 20% loss.

#### Sequence 1: M8, δ₁ = 0.50 mm → δ₂ = 0.60 mm
| Block | δ (mm) | N_L at this δ | n_applied | n/N_L | Cumulative D |
|---|---|---|---|---|---|
| 1 | 0.50 | 4,800 | 2,400 | 0.500 | 0.500 |
| 2 | 0.60 | 1,050 | 490 | 0.467 | 0.967 |
| **Total** | — | — | 2,890 | — | **0.967** |

#### Sequence 2: M8, δ₁ = 0.60 mm → δ₂ = 0.50 mm
| Block | δ (mm) | N_L at this δ | n_applied | n/N_L | Cumulative D |
|---|---|---|---|---|---|
| 1 | 0.60 | 1,050 | 525 | 0.500 | 0.500 |
| 2 | 0.50 | 4,800 | 2,640 | 0.550 | 1.050 |
| **Total** | — | — | 3,165 | — | **1.050** |

#### Sequence 3: M6, δ₁ = 0.45 mm → δ₂ = 0.55 mm
| Block | δ (mm) | N_L at this δ | n_applied | n/N_L | Cumulative D |
|---|---|---|---|---|---|
| 1 | 0.45 | 3,100 | 1,550 | 0.500 | 0.500 |
| 2 | 0.55 | 720 | 310 | 0.431 | 0.931 |
| **Total** | — | — | 1,860 | — | **0.931** |

### LDR Validation Summary
| Sequence | D_predicted (LDR) | D_experimental | Error |
|---|---|---|---|
| 1 | 1.000 | 0.967 | -3.3% |
| 2 | 1.000 | 1.050 | +5.0% |
| 3 | 1.000 | 0.931 | -6.9% |
| 4 | 1.000 | 1.020 | +2.0% |
| 5 | 1.000 | 0.905 | -9.5% |
| 6 | 1.000 | 1.085 | +8.5% |

**Mean D** = 0.993, **Std dev** = 0.062
**Conclusion**: LDR (Miner's rule) is valid for bolt loosening within ±10% error band. D_experimental ranges from **0.85 to 1.10**.

---

### Dataset 4: Multi-Bolt Structure Validation

**4-bolt M8 structure**: Plate 120 × 60 mm, bolt spacing 40 × 30 mm, eccentric transverse load at end.

| Bolt position | FEA predicted δ (mm) | Predicted N_L from D-N | Experimental N_L | Error |
|---|---|---|---|---|
| #1 (near load) | 0.58 | 1,320 | 1,180 | +11.9% |
| #2 (near load) | 0.55 | 2,050 | 1,850 | +10.8% |
| #3 (far) | 0.42 | 22,000 | 18,500 | +18.9% |
| #4 (far) | 0.40 | 42,000 | >30,000 | Conservative |

**Method**: Extract displacement at each bolt from FEA → read N_L from D–N curve → compare to experiment. Predictions within ±20% (conservative).

---

## Reproduction Parameters

| Parameter | Value | Units |
|---|---|---|
| Bolts | M6 × 1.0, M8 × 1.25 | — |
| Class | 10.9 | — |
| Preloads | 11.0 (M6), 14.3 (M8) | kN |
| Amplitudes | 0.30–0.65 | mm |
| Frequency | 10 | Hz |
| Criterion | 20% preload loss | — |
| Plates | SCM440, 2 × 10 mm | — |
| Variable amplitude | Two-block at 50% of life | — |
| Multi-bolt | 4-bolt eccentric structure | — |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2).
> D–N curves study with M6 and M8. Configure baseline for each bolt size.

### Bolt &amp; Thread Geometry — M8 (Primary)

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
| Nut height | 6.8 | mm |
| d_hole | 9.0 | mm |
| Helix angle | 3.17 | ° |
| r_be (eff. bearing) | 5.38 | mm |

### Bolt Geometry — M6 (Secondary)

| Parameter | Value | Unit |
|---|---|---|
| d (nominal) | 6.0 | mm |
| p (pitch) | 1.0 | mm |
| d₂ (pitch dia.) | 5.350 | mm |
| d₃ (minor dia.) | 4.773 | mm |
| Aₜ (stress area) | 20.1 | mm² |
| d_head (AF) | 10.0 | mm |
| d_hole | 6.6 | mm |
| Helix angle | 3.40 | ° |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 Q&amp;T | 206,000 | 940 | 1,040 | 0.30 |
| Plates | SCM440 (≈4140) | 210,000 | 900 | 1,000 | 0.29 |

### MSD Element Chain

```
GROUND — FLANGE(10mm) — FLANGE(10mm) — NUT — THREAD — SHANK — HEAD — GROUND
```

### Loading (PropertyInspector) — M8 Baseline (δ = 0.55 mm)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 14,300 | N |
| % Yield | 41.5 | % |
| Transverse disp. δ | 0.55 | mm |
| Frequency | 10.0 | Hz |
| Cycles | 2,200 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.12 |
| Lubricated | true |
| Bolt diameter | 8.0 mm |
| Pitch | 1.25 mm |

### D–N Curve Amplitude Configurations

| Config | Bolt | δ (mm) | F₀ (kN) | N_L (20% loss) | Cycles to run |
|---|---|---|---|---|---|
| M8-035 | M8 | 0.35 | 14.3 | >100,000 | 100,000 |
| M8-040 | M8 | 0.40 | 14.3 | 42,000 | 50,000 |
| M8-045 | M8 | 0.45 | 14.3 | 12,500 | 15,000 |
| M8-050 | M8 | 0.50 | 14.3 | 4,800 | 6,000 |
| M8-055 | M8 | 0.55 | 14.3 | 2,200 | 3,000 |
| M8-060 | M8 | 0.60 | 14.3 | 1,050 | 1,500 |
| M8-065 | M8 | 0.65 | 14.3 | 520 | 700 |
| M6-035 | M6 | 0.35 | 11.0 | 28,500 | 35,000 |
| M6-040 | M6 | 0.40 | 11.0 | 8,200 | 10,000 |
| M6-045 | M6 | 0.45 | 11.0 | 3,100 | 4,000 |
| M6-050 | M6 | 0.50 | 11.0 | 1,500 | 2,000 |
| M6-055 | M6 | 0.55 | 11.0 | 720 | 1,000 |
| M6-060 | M6 | 0.60 | 11.0 | 380 | 500 |
| M6-065 | M6 | 0.65 | 11.0 | 210 | 300 |

### ValidationCase — M8, δ = 0.55 mm

```python
ValidationCase(
    name="Yang_2025_M8_055mm",
    bolt_size="M8x1.25",
    bolt_diameter_mm=8.0,
    pitch_mm=1.25,
    initial_preload_N=14300,
    preload_percent_yield=41.5,
    transverse_displacement_mm=0.55,
    frequency_Hz=10.0,
    n_cycles=2200,
    mu_initial=0.12,
    lubricated=True,
    expected_final_preload_ratio=0.800,
    expected_loosening_deg=3.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.960),
        ExperimentalDataPoint(cycles=300, preload_ratio=0.930),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.900),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.860),
        ExperimentalDataPoint(cycles=1500, preload_ratio=0.830),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.805),
        ExperimentalDataPoint(cycles=2200, preload_ratio=0.800),
    ]
)
```
