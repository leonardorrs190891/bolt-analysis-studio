# Study 07: Nassar & Housari (2006) — Effect of Thread Pitch and Initial Preload

## Full Citation
**Authors**: Nassar, S. A.; Housari, B. A.
**Title**: "Effect of Thread Pitch and Initial Tension on the Self-Loosening of Threaded Fasteners"
**Journal**: ASME Journal of Pressure Vessel Technology, 2006, 128(4), 590–598
**DOI**: 10.1115/1.2349574

---

## Experimental Setup

### Test Machine
- **Type**: RS Technologies Vibration Test System RS-SSTM-04
- **Loading**: Transverse cyclic displacement, servo-hydraulic
- **Preload measurement**: Kistler piezoelectric load cell
- **Displacement**: LVDT

### Bolt Configurations

| Config | Thread | Pitch (mm) | TPI | Diameter (mm) | Class/Grade |
|---|---|---|---|---|---|
| A | M10 × 1.5 (coarse) | 1.50 | — | 10 | 10.9 |
| B | M10 × 1.25 (fine) | 1.25 | — | 10 | 10.9 |
| C | M10 × 1.0 (superfine) | 1.00 | — | 10 | 10.9 |
| D | 3/8"-16 UNC | 1.588 | 16 | 9.525 | SAE Gr.8 |
| E | 3/8"-24 UNF | 1.058 | 24 | 9.525 | SAE Gr.8 |

### Common Parameters
- **Surface treatment**: Phosphate + oil (μ ≈ 0.10)
- **Displacement amplitude**: 0.71 mm (0.028")
- **Frequency**: 7 Hz
- **Grip length**: 25.4 mm
- **Clamped plates**: AISI 1018 steel, 2 × 12.7 mm

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Effect of Thread Pitch — M10 Series (F₀ = 25 kN, δ = 0.71 mm)

**[APPROXIMATE — digitized from published Figure 5]**

#### M10 × 1.5 (coarse, p = 1.50 mm, β = 3.03°)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.850 |
| 10 | 0.720 |
| 20 | 0.540 |
| 50 | 0.280 |
| 100 | 0.100 |
| 200 | 0.020 |

#### M10 × 1.25 (fine, p = 1.25 mm, β = 2.53°)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.880 |
| 10 | 0.780 |
| 20 | 0.620 |
| 50 | 0.380 |
| 100 | 0.180 |
| 200 | 0.060 |

#### M10 × 1.0 (superfine, p = 1.00 mm, β = 2.02°)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.920 |
| 10 | 0.850 |
| 20 | 0.730 |
| 50 | 0.520 |
| 100 | 0.310 |
| 200 | 0.140 |
| 500 | 0.030 |

**Key finding**: Finer pitch significantly resists loosening. M10×1.0 retains preload ~3× longer than M10×1.5 at the same conditions. The helix angle β is smaller for fine pitch → smaller pitch torque → less driving force for loosening.

### Cycles to 50% Preload Loss vs. Pitch
| Thread | Pitch (mm) | Helix angle β (°) | Cycles to 50% loss |
|---|---|---|---|
| M10 × 1.5 | 1.50 | 3.03 | ~18 |
| M10 × 1.25 | 1.25 | 2.53 | ~30 |
| M10 × 1.0 | 1.00 | 2.02 | ~55 |

### Ratio Analysis
Loosening rate scales approximately as:
```
Rate ∝ tan(β) ∝ p / (π × d₂)
```
The ratio of loosening rates for M10×1.5 vs M10×1.0:
```
tan(3.03°) / tan(2.02°) = 1.50 ≈ 1.5
```
Close to the pitch ratio of 1.5/1.0 = 1.5 → confirming linear pitch dependence.

---

### Dataset 2: Inch-Series Pitch Comparison (F₀ = 11,120 N, δ = 0.71 mm)

#### 3/8"-16 UNC (coarse, p = 1.588 mm)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.820 |
| 10 | 0.680 |
| 20 | 0.480 |
| 50 | 0.200 |
| 100 | 0.060 |

#### 3/8"-24 UNF (fine, p = 1.058 mm)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.880 |
| 10 | 0.780 |
| 20 | 0.600 |
| 50 | 0.340 |
| 100 | 0.150 |
| 200 | 0.040 |

---

### Dataset 3: Effect of Initial Preload — M10×1.5 (δ = 0.71 mm, μ = 0.10)

**[APPROXIMATE — from Figure 7]**

#### F₀ = 10 kN (low)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.750 |
| 10 | 0.560 |
| 20 | 0.320 |
| 50 | 0.080 |

#### F₀ = 25 kN (medium)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.720 |
| 50 | 0.280 |
| 100 | 0.100 |

#### F₀ = 40 kN (high — 69% proof)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.880 |
| 20 | 0.780 |
| 50 | 0.560 |
| 100 | 0.360 |
| 200 | 0.160 |
| 500 | 0.040 |

**Key finding**: Doubling the preload approximately doubles the loosening life (in cycles). However, high preload does NOT prevent loosening — it only delays it. The only way to prevent loosening entirely is to keep the transverse displacement below the critical threshold.

---

## Design Recommendation from This Study

**For vibration-critical applications, use fine-pitch threads:**

| Bolt size | Recommended pitch | Standard designation |
|---|---|---|
| M8 | 1.0 mm (fine) | M8 × 1.0 |
| M10 | 1.0 mm (fine) | M10 × 1.0 |
| M12 | 1.25 mm (fine) | M12 × 1.25 |
| M16 | 1.5 mm (fine) | M16 × 1.5 |
| M20 | 1.5 mm (fine) | M20 × 1.5 |

Note: Fine-pitch threads also provide:
- Higher preload for same torque (smaller pitch contribution to torque)
- Better preload accuracy (less scatter)
- Greater fatigue strength (smaller stress concentration at thread root)
- But: more susceptible to thread galling and cross-threading

---

## Reproduction Parameters

| Parameter | Value | Units |
|---|---|---|
| Bolts | M10×1.0, M10×1.25, M10×1.5, 3/8"-16, 3/8"-24 | — |
| Preloads | 10, 25, 40 | kN |
| Amplitude | 0.71 | mm |
| Frequency | 7 | Hz |
| Surface | Phosphate + oil | — |
| μ | 0.10 ± 0.02 | — |
| Grip length | 25.4 | mm |
| Plate material | AISI 1018 | — |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this experiment.
> Multiple bolt configurations — create separate models for each pitch.

### Bolt & Thread Geometry — M10×1.5 (Baseline)

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M10×1.5 | — |
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

### Pitch Variants

| Variant | p (mm) | d₂ (mm) | Aₜ (mm²) | Helix (°) | Notes |
|---|---|---|---|---|---|
| M10×1.5 coarse | 1.50 | 9.026 | 58.0 | 3.03 | Standard |
| M10×1.25 fine | 1.25 | 9.188 | 61.2 | 2.53 | Better resistance |
| M10×1.0 superfine | 1.00 | 9.350 | 64.5 | 2.02 | Best resistance |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 Q&T | 210,000 | 940 | 1,040 | 0.3 |
| Plates | AISI 1018 | 200,000 | 250 | 440 | 0.29 |

### MSD Element Chain

```
GROUND — FLANGE(12.7mm) — FLANGE(12.7mm) — NUT — THREAD — SHANK — HEAD — GROUND
```

### Loading (PropertyInspector) — All Configurations

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Transverse disp. δ | 0.71 | mm |
| Frequency | 7.0 | Hz |
| Cycles | 500 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.10 |
| Lubricated | true (phosphate + oil) |

### Preload Configurations

| Config | Bolt | F₀ (N) | % Yield | Notes |
|---|---|---|---|---|
| Low | M10×1.5 | 10,000 | 18.3 | Rapid loosening |
| Medium | M10×1.5 | 25,000 | 45.8 | Primary test |
| High | M10×1.5 | 40,000 | 73.3 | 69% proof |
| Pitch test coarse | M10×1.5 | 25,000 | 45.8 | p=1.50mm |
| Pitch test fine | M10×1.25 | 25,000 | 43.4 | p=1.25mm |
| Pitch test superfine | M10×1.0 | 25,000 | 41.2 | p=1.00mm |

### ValidationCase — M10×1.5 Baseline (for validation_cases.py)

```python
ValidationCase(
    name="Nassar_2006_M10x1.5_pitch",
    bolt_size="M10x1.5",
    bolt_diameter_mm=10.0,
    pitch_mm=1.50,
    initial_preload_N=25000,
    preload_percent_yield=45.8,
    transverse_displacement_mm=0.71,
    frequency_Hz=7.0,
    n_cycles=200,
    mu_initial=0.10,
    lubricated=True,
    expected_final_preload_ratio=0.02,
    expected_loosening_deg=18.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.850),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.720),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.540),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.280),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.100),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.020),
    ]
)
```
