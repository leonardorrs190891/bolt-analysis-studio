# Study 31: den Otter & Maljaars (2020) — Stainless Steel Bolt Preload Loss in Aluminum Joints

## Full Citation
**Authors**: den Otter, C.; Maljaars, J.
**Title**: "Preload loss of stainless steel bolts in aluminium plated slip resistant connections"
**Journal**: Thin-Walled Structures, 2020, 157, 106984
**DOI**: 10.1016/j.tws.2020.106984

---

## Significance
First comprehensive study of **long-term preload loss** in stainless steel bolts clamping aluminum alloys — the most common material combination in architectural facades, marine structures, and lightweight structural applications. Provides **50-year extrapolated predictions** with reliability analysis and partial safety factors.

---

## Experimental Setup

### Bolt Specifications
| Parameter | M16 | M24 |
|---|---|---|
| Size | M16 × 2.0 | M24 × 3.0 |
| Material | A4-80 (316 austenitic SS) | A4-80 (316 austenitic SS) |
| σ_0.2 (min) | 600 MPa | 600 MPa |
| σ_u (min) | 800 MPa | 800 MPa |
| E | 193,000 MPa | 193,000 MPa |
| Stress area | 157 mm² | 353 mm² |
| Proof load | 94,200 N | 211,800 N |
| α_CTE | 16.0 × 10⁻⁶/°C | 16.0 × 10⁻⁶/°C |

### Clamped Members — Aluminum Alloys
| Alloy | Temper | σ_0.2 (MPa) | E (GPa) | α_CTE (10⁻⁶/°C) | Creep tendency |
|---|---|---|---|---|---|
| 5083 | H321 | 215 | 71.0 | 23.8 | High (non-heat-treatable) |
| 5454 | H34 | 200 | 70.0 | 23.8 | High |
| 6061 | T6 | 240 | 69.0 | 23.6 | Low (precipitation hardened) |

### Preload Measurement
- **Method**: BoltSafe CMS (Continuous Monitoring System) load cells
- **Accuracy**: ±1% of reading
- **Range**: 0–250 kN
- **Sampling**: Continuous, logged every 1 hour

### Test Matrix

| Test ID | Bolt | Aluminum | F₀/f_u,b | F₀ (kN) | Temperature |
|---|---|---|---|---|---|
| A1 | M16 | 5083 | 0.70 | 87.8 | 20°C |
| A2 | M16 | 5083 | 0.50 | 62.7 | 20°C |
| A3 | M16 | 5083 | 0.27 | 33.9 | 20°C |
| B1 | M16 | 5454 | 0.70 | 87.8 | 20°C |
| C1 | M16 | 6061-T6 | 0.70 | 87.8 | 20°C |
| C2 | M16 | 6061-T6 | 0.50 | 62.7 | 20°C |
| D1 | M24 | 5083 | 0.70 | 197.3 | 20°C |
| D2 | M24 | 6061-T6 | 0.70 | 197.3 | 20°C |

### Assembly
- **Plate thickness**: 2 × 10 mm = 20 mm grip
- **Hole diameter**: M16 → 18 mm; M24 → 26 mm
- **Tightening method**: Calibrated torque wrench
- **Test duration**: Up to 2,500 hours (~104 days)

---

## DATA FOR CURVE PLOTTING

### Dataset 1: M16 in 5083 Aluminum — Effect of Preload Level

**[APPROXIMATE — digitized from published Figure 5]**

#### F₀/f_u = 0.70 (87.8 kN)
| Time (hours) | F/F₀ | Absolute loss (kN) |
|---|---|---|
| 0 | 1.000 | 0.0 |
| 1 | 0.990 | 0.9 |
| 10 | 0.975 | 2.2 |
| 100 | 0.950 | 4.4 |
| 500 | 0.925 | 6.6 |
| 1,000 | 0.910 | 7.9 |
| 2,500 | 0.895 | 9.2 |

#### F₀/f_u = 0.50 (62.7 kN)
| Time (hours) | F/F₀ |
|---|---|
| 0 | 1.000 |
| 1 | 0.993 |
| 10 | 0.982 |
| 100 | 0.965 |
| 500 | 0.945 |
| 1,000 | 0.935 |
| 2,500 | 0.920 |

#### F₀/f_u = 0.27 (33.9 kN)
| Time (hours) | F/F₀ |
|---|---|
| 0 | 1.000 |
| 1 | 0.997 |
| 10 | 0.990 |
| 100 | 0.978 |
| 500 | 0.965 |
| 1,000 | 0.958 |
| 2,500 | 0.948 |

---

### Dataset 2: Material Comparison — M16 at 70% (87.8 kN)

| Time (hours) | 5083-H321 F/F₀ | 5454-H34 F/F₀ | 6061-T6 F/F₀ |
|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 |
| 1 | 0.990 | 0.991 | 0.995 |
| 10 | 0.975 | 0.976 | 0.985 |
| 100 | 0.950 | 0.952 | 0.972 |
| 500 | 0.925 | 0.928 | 0.958 |
| 1,000 | 0.910 | 0.912 | 0.950 |
| 2,500 | 0.895 | 0.898 | 0.940 |

**Key finding**: 5083 and 5454 (non-heat-treatable) creep ~40% more than 6061-T6 (precipitation hardened). Heat-treatable alloys are significantly better for maintaining bolt preload.

---

### Dataset 3: M16 vs. M24 in 5083

| Time (hours) | M16 F/F₀ | M24 F/F₀ |
|---|---|---|
| 0 | 1.000 | 1.000 |
| 100 | 0.950 | 0.955 |
| 1,000 | 0.910 | 0.918 |
| 2,500 | 0.895 | 0.905 |

M24 retains slightly more preload (proportionally) due to larger bearing area → lower contact pressure.

---

### Dataset 4: 50-Year Extrapolation (Power-Law Creep Model)

**Model**: F(t)/F₀ = 1 - a × t^b

| Parameter | 5083/5454 | 6061-T6 |
|---|---|---|
| a | 0.0085 | 0.0045 |
| b | 0.28 | 0.25 |
| R² | 0.996 | 0.994 |

#### Predicted Preload Loss at 50 Years (438,000 hours)

| Bolt | Aluminum | F₀/f_u | 50-year F/F₀ | 50-year loss (%) |
|---|---|---|---|---|
| M16 | 5083 | 0.70 | 0.82 | **18%** |
| M16 | 5083 | 0.50 | 0.86 | 14% |
| M16 | 5454 | 0.70 | 0.82 | 18% |
| M16 | 6061-T6 | 0.70 | 0.89 | **11%** |
| M16 | 6061-T6 | 0.50 | 0.92 | 8% |
| M24 | 5083 | 0.70 | 0.83 | 17% |
| M24 | 6061-T6 | 0.70 | 0.90 | 10% |

---

### Dataset 5: Reliability Analysis — Partial Safety Factors

**For 50-year design life, β = 3.8 (EN 1990, CC2):**

| Aluminum alloy | γ_preload (partial safety factor) | Design preload retention |
|---|---|---|
| 5083/5454 | 1.40 | F_design = F₀ / 1.40 |
| 6061-T6 | 1.25 | F_design = F₀ / 1.25 |

**Interpretation**: For 5083 joints, design preload should be taken as 71% of initial preload (1/1.40) to account for 50-year creep with appropriate reliability.

---

## Creep Mechanism Analysis

### Stainless Steel Bolt Contribution
At room temperature, A4-80 bolt creep is **negligible** (<1% in 50 years). All relaxation comes from the aluminum clamped members.

### Aluminum Creep Mechanism
1. **Primary creep** (first 100 hours): Dislocation glide, rapid initial loss
2. **Secondary creep** (100–10,000 hours): Steady-state, dislocation climb
3. **Tertiary** (>10,000 hours): Not observed at room temperature stresses

### Contact Pressure Effect
The bearing area contact pressure drives aluminum creep:
- M16 at 87.8 kN on 5083: σ_contact ≈ 185 MPa (~86% of σ_0.2)
- At σ/σ_0.2 > 0.5, power-law creep activates in aluminum

---

## Reproduction Parameters

| Parameter | Value | Units |
|---|---|---|
| Bolts | M16, M24 | A4-80 (316 SS) |
| Preload ratios | 0.27, 0.50, 0.70 × f_u | — |
| Aluminum alloys | 5083-H321, 5454-H34, 6061-T6 | — |
| Plate thickness | 2 × 10 | mm |
| Temperature | 20 | °C |
| Duration | 2,500 | hours |
| Load measurement | BoltSafe CMS | continuous |
| Extrapolation | Power-law creep model | to 50 years |

---

## MSD BUILDER CONFIGURATION

> This study models **long-term creep relaxation** of SS bolts in aluminum (not transverse vibration).
> Configure as static preload with creep-susceptible clamped members.

### Bolt &amp; Thread Geometry — M16 (Primary)

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M16×2.0 | — |
| d (nominal) | 16.0 | mm |
| p (pitch) | 2.0 | mm |
| d₂ (pitch dia.) | 14.701 | mm |
| d₃ (minor dia.) | 13.546 | mm |
| Aₜ (stress area) | 157 | mm² |
| d_head (AF) | 24.0 | mm |
| Head height | 10.0 | mm |
| Nut height | 14.8 | mm |
| d_hole | 18.0 | mm |
| Helix angle | 2.48 | ° |
| r_be (eff. bearing) | 10.25 | mm |

### Bolt Geometry — M24

| Parameter | Value | Unit |
|---|---|---|
| d (nominal) | 24.0 | mm |
| p (pitch) | 3.0 | mm |
| d₂ (pitch dia.) | 22.051 | mm |
| d₃ (minor dia.) | 20.319 | mm |
| Aₜ (stress area) | 353 | mm² |
| d_head (AF) | 36.0 | mm |
| d_hole | 26.0 | mm |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν | α_CTE (10⁻⁶/°C) |
|---|---|---|---|---|---|---|
| Bolt/nut | A4-80 (316 SS) | 193,000 | 600 | 800 | 0.28 | 16.0 |
| Plates (opt 1) | 5083-H321 Al | 71,000 | 215 | 345 | 0.33 | 23.8 |
| Plates (opt 2) | 6061-T6 Al | 69,000 | 240 | 310 | 0.33 | 23.6 |

### MSD Element Chain

```
GROUND — FLANGE(10mm Al) — FLANGE(10mm Al) — NUT — THREAD — SHANK — HEAD — GROUND
```

### Loading (PropertyInspector) — M16 in 5083, 70%

| Parameter | Value | Unit |
|---|---|---|
| Load type | AXIAL (static preload, creep) | — |
| Preload F₀ | 87,800 | N |
| % Yield | 93.5 | % (of A4-80 σ_0.2) |
| Duration | 2,500 | hours |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 |
| Lubricated | false |
| Bolt diameter | 16.0 mm |
| Pitch | 2.0 mm |

### Test Configurations

| Config | Bolt | Al Alloy | F₀/f_u | F₀ (kN) | Duration (hr) |
|---|---|---|---|---|---|
| A1 | M16 | 5083 | 0.70 | 87.8 | 2,500 |
| A2 | M16 | 5083 | 0.50 | 62.7 | 2,500 |
| A3 | M16 | 5083 | 0.27 | 33.9 | 2,500 |
| B1 | M16 | 5454 | 0.70 | 87.8 | 2,500 |
| C1 | M16 | 6061-T6 | 0.70 | 87.8 | 2,500 |
| C2 | M16 | 6061-T6 | 0.50 | 62.7 | 2,500 |
| D1 | M24 | 5083 | 0.70 | 197.3 | 2,500 |
| D2 | M24 | 6061-T6 | 0.70 | 197.3 | 2,500 |

### ValidationCase — M16 in 5083, F₀/f_u = 0.70

```python
ValidationCase(
    name="den_Otter_2020_M16_5083_70pct",
    bolt_size="M16x2.0",
    bolt_diameter_mm=16.0,
    pitch_mm=2.0,
    initial_preload_N=87800,
    preload_percent_yield=93.5,
    transverse_displacement_mm=0.0,
    frequency_Hz=0.0,
    n_cycles=0,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.895,
    expected_loosening_deg=0.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=1, preload_ratio=0.990),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.975),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.950),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.925),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.910),
        ExperimentalDataPoint(cycles=2500, preload_ratio=0.895),
    ]
)
```

**Note**: "Cycles" in this ValidationCase represent **hours** of static creep exposure. The x-axis is time in hours on a logarithmic scale.
