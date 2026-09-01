# Study 06: Yang & Nassar (2011) — Cap Screw Analytical Model & Experimental Validation

## Full Citation
**Authors**: Yang, X.; Nassar, S. A.
**Title**: "Analytical and Experimental Investigation of Self-Loosening of Preloaded Cap Screw Fasteners"
**Journal**: ASME Journal of Vibration and Acoustics, 2011, 133(3), 031007
**DOI**: 10.1115/1.4003197

---

## Significance
This paper is the experimental companion to the Nassar-Yang 2009 nonlinear model (Study 05). It provides the most thorough **direct comparison** between analytical predictions and controlled experiments for cap screw (socket head) fasteners, which differ from hex-head bolts in bearing geometry.

---

## Experimental Setup

### Bolt Specifications
- **Type**: Socket Head Cap Screw (SHCS)
- **Size**: 5/16"-24 UNF × 1.5" (≈ M8 × 1.06 × 38 mm)
- **Grade**: SAE Grade 8 (equivalent to ISO 10.9+)
- **Material**: Alloy steel, heat-treated
- **Yield strength**: 896 MPa
- **UTS**: 1,034 MPa
- **Thread pitch**: 1.058 mm (24 TPI)
- **Pitch diameter d₂**: 7.249 mm
- **Minor diameter**: 6.731 mm
- **Stress area**: 36.4 mm²
- **Head diameter**: 12.7 mm (0.500")
- **Head height**: 7.94 mm (5/16")
- **Socket size**: 1/4" hex

### Key Geometric Difference: Cap Screw vs. Hex Head
| Parameter | Cap screw (SHCS) | Hex head bolt |
|---|---|---|
| Head bearing OD | 12.7 mm | ~13.0 mm (AF) |
| Head bearing ID (hole) | 8.73 mm | 8.73 mm |
| Effective bearing radius r_be | 5.24 mm | 5.35 mm |
| Bearing area | 66.8 mm² | 72.5 mm² |
| Contact pressure at 10 kN | 149.7 MPa | 137.9 MPa |

The smaller bearing area of cap screws means **higher bearing contact pressure** and **smaller friction moment arm**, both of which tend to make cap screws slightly MORE susceptible to loosening than hex head bolts at the same preload.

### Nut Specifications
- **Type**: Standard hex nut, 5/16"-24 UNF
- **Grade**: SAE Grade 8
- **Height**: 7.14 mm (9/32")

### Clamped Members
- **Material**: AISI 1018 low-carbon steel (cold-drawn)
- **Hardness**: HRB 70–80 (approximately HRC 12–14)
- **Surface finish**: Ground, Ra ≈ 1.6 μm
- **Plate dimensions**: 50 × 25 × 12.7 mm each (two plates)
- **Grip length**: 25.4 mm (2 × 12.7 mm)
- **Hole diameter**: 8.73 mm (11/32") — standard clearance

### Test Machine
- **Type**: RS Technologies Vibration Test System, Model RS-SSTM-04
- **Displacement range**: 0 to ±2.5 mm
- **Frequency range**: 0 to 30 Hz
- **Force capacity**: 25 kN
- **Preload measurement**: Piezoelectric load cell (Kistler 9130B)
- **Displacement**: LVDT (Solartron)
- **Nut rotation**: Optical angular encoder (0.01° resolution)
- **Data acquisition**: National Instruments DAQ at 1 kHz

### Surface Treatments Tested
| ID | Treatment | μ_th (measured) | μ_b (measured) |
|---|---|---|---|
| A | Phosphate + oil | 0.10 ± 0.02 | 0.10 ± 0.02 |
| B | Zinc-plated, dry | 0.22 ± 0.03 | 0.22 ± 0.03 |
| C | Cadmium-plated | 0.08 ± 0.02 | 0.08 ± 0.02 |

### Friction Measurement Method
Friction coefficients measured independently using the Motosh method:
- Instrument bolt with strain gauges (axial force)
- Measure torque input and resulting preload
- Separate thread and bearing friction via progressive tightening protocol
- 5 repetitions per surface treatment

---

## Test Matrix

| Test series | Preload F₀ (N) | Amplitude δ₀ (mm) | Frequency (Hz) | Surface | Repetitions |
|---|---|---|---|---|---|
| 1 | 5,560 | 0.71 | 7 | A | 3 |
| 2 | 8,340 | 0.71 | 7 | A | 3 |
| 3 | 11,120 | 0.71 | 7 | A | 3 |
| 4 | 16,680 | 0.71 | 7 | A | 3 |
| 5 | 11,120 | 0.36 | 7 | A | 3 |
| 6 | 11,120 | 0.53 | 7 | A | 3 |
| 7 | 11,120 | 1.07 | 7 | A | 3 |
| 8 | 11,120 | 0.71 | 7 | B | 3 |
| 9 | 11,120 | 0.71 | 7 | C | 3 |

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Effect of Preload (δ₀ = 0.71 mm, μ = 0.10, f = 7 Hz)

**[APPROXIMATE — digitized from published Figure 5]**

#### F₀ = 5,560 N (1,250 lbf)
| Cycles | F (N) | F/F₀ | Nut rotation (°) |
|---|---|---|---|
| 0 | 5,560 | 1.000 | 0.0 |
| 5 | 3,800 | 0.683 | 2.5 |
| 10 | 2,500 | 0.450 | 5.8 |
| 20 | 1,200 | 0.216 | 10.5 |
| 50 | 300 | 0.054 | 18.0 |
| 100 | 50 | 0.009 | 22.0 |

#### F₀ = 11,120 N (2,500 lbf)
| Cycles | F (N) | F/F₀ | Nut rotation (°) |
|---|---|---|---|
| 0 | 11,120 | 1.000 | 0.0 |
| 5 | 9,200 | 0.827 | 1.2 |
| 10 | 7,500 | 0.674 | 3.0 |
| 20 | 5,200 | 0.468 | 6.5 |
| 50 | 2,200 | 0.198 | 14.0 |
| 100 | 700 | 0.063 | 22.5 |
| 150 | 200 | 0.018 | 28.0 |

#### F₀ = 16,680 N (3,750 lbf)
| Cycles | F (N) | F/F₀ | Nut rotation (°) |
|---|---|---|---|
| 0 | 16,680 | 1.000 | 0.0 |
| 10 | 14,500 | 0.869 | 1.0 |
| 20 | 12,500 | 0.749 | 2.5 |
| 50 | 8,000 | 0.480 | 7.0 |
| 100 | 4,200 | 0.252 | 14.0 |
| 150 | 2,000 | 0.120 | 20.0 |
| 200 | 800 | 0.048 | 25.5 |

---

### Dataset 2: Effect of Displacement Amplitude (F₀ = 11,120 N, μ = 0.10)

#### δ₀ = 0.36 mm
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 20 | 0.940 |
| 50 | 0.880 |
| 100 | 0.800 |
| 200 | 0.700 |
| 500 | 0.520 |

#### δ₀ = 0.53 mm
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.850 |
| 20 | 0.720 |
| 50 | 0.480 |
| 100 | 0.250 |
| 200 | 0.080 |

#### δ₀ = 0.71 mm
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.674 |
| 50 | 0.198 |
| 100 | 0.063 |

#### δ₀ = 1.07 mm
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 2 | 0.680 |
| 5 | 0.400 |
| 10 | 0.180 |
| 20 | 0.050 |
| 50 | 0.010 |

---

### Dataset 3: Effect of Friction Coefficient (F₀ = 11,120 N, δ₀ = 0.71 mm)

#### μ = 0.08 (Cadmium)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.720 |
| 10 | 0.500 |
| 20 | 0.280 |
| 50 | 0.060 |

#### μ = 0.10 (Phosphate + oil)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.674 |
| 50 | 0.198 |
| 100 | 0.063 |

#### μ = 0.22 (Zinc, dry)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.920 |
| 20 | 0.860 |
| 50 | 0.720 |
| 100 | 0.540 |
| 200 | 0.340 |
| 500 | 0.120 |

---

### Dataset 4: Model vs. Experiment Comparison (F₀ = 11,120 N, δ₀ = 0.71 mm, μ = 0.10)

| Cycles | F/F₀ Experimental (mean) | F/F₀ Model predicted | Error (%) |
|---|---|---|---|
| 0 | 1.000 | 1.000 | 0.0 |
| 5 | 0.827 | 0.845 | +2.2 |
| 10 | 0.674 | 0.700 | +3.9 |
| 20 | 0.468 | 0.500 | +6.8 |
| 50 | 0.198 | 0.220 | +11.1 |
| 100 | 0.063 | 0.075 | +19.0 |
| 150 | 0.018 | 0.025 | +38.9 |

**Note**: Model slightly overpredicts preload at high cycle counts (conservative — predicts slower loosening than actual). Error increases at low preloads because model doesn't capture all plastic deformation mechanisms.

---

## Nut Rotation Curves

### Nut Rotation vs. Cycles (F₀ = 11,120 N, δ₀ = 0.71 mm, μ = 0.10)

| Cycles | θ_nut (°) | dθ/dN (°/cycle) |
|---|---|---|
| 0 | 0.00 | — |
| 5 | 1.20 | 0.24 |
| 10 | 3.00 | 0.36 |
| 20 | 6.50 | 0.35 |
| 50 | 14.00 | 0.25 |
| 100 | 22.50 | 0.17 |
| 150 | 28.00 | 0.11 |

**Observation**: Loosening rate (dθ/dN) accelerates initially as preload drops (less friction resistance), then decelerates as very little preload remains to drive the pitch torque. Peak loosening rate occurs around 20–50 cycles.

---

## Criterion for Preventing Self-Loosening

### Yang & Nassar (2011), J. Vib. Acoust. 133:041013

The companion paper provides a design criterion:

**Self-loosening will NOT occur if**:
```
δ_max < δ_cr = (μ_b × F₀ × r_be) / k_bearing_shear
```

Or equivalently, the maximum transverse force must not exceed:
```
F_trans,max < μ_eff × F₀
```

Where the effective friction coefficient is:
```
μ_eff = [μ_b × r_be × cos(α) − μ_th × r_t × sin(β)] / [r_be × cos(α) + r_t × cos(β)]
```

For typical M8–M12 values (μ_th = μ_b = 0.12, α = 30°, β ≈ 3°):
```
μ_eff ≈ 0.10 × F₀
```
So the critical transverse force ≈ 10% of preload.

---

## Reproduction Parameters Summary

| Parameter | Value | Units |
|---|---|---|
| Bolt type | 5/16"-24 UNF SHCS | — |
| Bolt grade | SAE 8 | — |
| Preloads tested | 5,560 / 8,340 / 11,120 / 16,680 | N |
| Amplitudes tested | 0.36 / 0.53 / 0.71 / 1.07 | mm |
| Frequency | 7 | Hz |
| Friction coefs tested | 0.08 / 0.10 / 0.22 | — |
| Grip length | 25.4 | mm |
| Hole diameter | 8.73 | mm |
| Plate material | AISI 1018 | — |
| Plate thickness (each) | 12.7 | mm |
| Repetitions per condition | 3 | — |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this experiment.
> NOTE: Socket Head Cap Screw (SHCS) — smaller bearing diameter than hex head.

### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | 5/16"-24 UNF SHCS (≈M8×1.06) | — |
| d (nominal) | 7.938 | mm |
| p (pitch) | 1.058 | mm |
| d₂ (pitch dia.) | 7.249 | mm |
| d₃ (minor dia.) | 6.731 | mm |
| Aₜ (stress area) | 36.4 | mm² |
| Head diameter | 12.7 | mm |
| Head height | 7.94 | mm |
| d_hole | 8.73 | mm |
| Grip length | 25.4 | mm |
| Helix angle | 2.66 | ° |
| r_be (eff. bearing) | 5.24 | mm |
| Bearing area | 66.8 | mm² |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | SAE Gr.8 (≈10.9) | 206,000 | 896 | 1,034 | 0.3 |
| Plates | AISI 1018 | 200,000 | 250 | 440 | 0.29 |

### MSD Element Chain

```
GROUND — FLANGE(12.7mm) — FLANGE(12.7mm) — NUT — THREAD — SHANK — HEAD — GROUND
```

| Element | Key Parameters |
|---|---|
| HEAD | d=7.94, d_head=12.7 (SHCS), h_head=7.94 mm |
| SHANK | d=7.94, L≈12.0 mm |
| THREAD | d=7.94, p=1.058, L≈7.14 mm (engaged), At=36.4 |
| NUT | d=7.94, p=1.058, h_nut=7.14 mm |
| FLANGE_1 | t=12.7 mm, d_hole=8.73 mm, E=200,000 |
| FLANGE_2 | t=12.7 mm, d_hole=8.73 mm, E=200,000 |

### Loading (PropertyInspector) — Baseline Test

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 11,120 | N |
| % Yield | 34.2 | % |
| Transverse disp. δ | 0.71 | mm |
| Frequency | 7.0 | Hz |
| Cycles | 200 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.10 |
| Lubricated | true (phosphate + oil) |
| Bolt diameter | 7.94 mm |
| Pitch | 1.058 mm |

### Test Configurations (9 series)

| Series | F₀ (N) | δ (mm) | μ | Surface |
|---|---|---|---|---|
| 1 | 5,560 | 0.71 | 0.10 | Phosphate+oil |
| 2 | 8,340 | 0.71 | 0.10 | Phosphate+oil |
| 3 | 11,120 | 0.71 | 0.10 | Phosphate+oil |
| 4 | 16,680 | 0.71 | 0.10 | Phosphate+oil |
| 5 | 11,120 | 0.36 | 0.10 | Phosphate+oil |
| 6 | 11,120 | 0.53 | 0.10 | Phosphate+oil |
| 7 | 11,120 | 1.07 | 0.10 | Phosphate+oil |
| 8 | 11,120 | 0.71 | 0.22 | Zinc dry |
| 9 | 11,120 | 0.71 | 0.08 | Cadmium |

### ValidationCase — Baseline (for validation_cases.py)

```python
ValidationCase(
    name="Yang_Nassar_2011_SHCS_baseline",
    bolt_size="5/16-24UNF",
    bolt_diameter_mm=7.938,
    pitch_mm=1.058,
    initial_preload_N=11120,
    preload_percent_yield=34.2,
    transverse_displacement_mm=0.71,
    frequency_Hz=7.0,
    n_cycles=150,
    mu_initial=0.10,
    lubricated=True,
    expected_final_preload_ratio=0.018,
    expected_loosening_deg=28.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.827),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.674),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.468),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.198),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.063),
        ExperimentalDataPoint(cycles=150, preload_ratio=0.018),
    ]
)
```
