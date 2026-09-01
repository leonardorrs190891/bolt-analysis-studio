# Study 14: Dinger & Friedrich (2011/2016) — FEA with Local Contact State Parameter

## Full Citations

### Paper A
**Authors**: Dinger, G.; Friedrich, C.
**Title**: "Avoiding self-loosening failure of bolted joints with numerical assessment of local contact state"
**Journal**: Engineering Failure Analysis, 2011, 18(8), 2188–2200
**DOI**: 10.1016/j.engfailanal.2011.07.012

### Paper B
**Authors**: Dinger, G.
**Title**: "Design of multi-bolted joints to prevent self-loosening failure"
**Journal**: Proc. IMechE Part C: J. Mechanical Engineering Science, 2016, 230(15), 2564–2578
**DOI**: 10.1177/0954406215612814

---

## FEA Model Details

### Bolt Specifications
- **Size**: M10 × 1.5 (Paper A) / M12 × 1.75 (Paper B)
- **Property class**: 10.9
- **Material**: Alloy steel

### FEA Model Parameters (Paper A — M10)
| Parameter | Value |
|---|---|
| Software | ABAQUS/Standard |
| Element type | C3D8I (incompatible modes) |
| Total elements | 82,434 |
| Total nodes | ~95,000 |
| Thread geometry | Full 3D helix, 4 turns engaged |
| Contact algorithm | Surface-to-surface, finite sliding |
| Friction model | Isotropic Coulomb |
| μ (all surfaces) | 0.10 (parametric: 0.05, 0.10, 0.15, 0.20) |
| Preload method | BOLT LOAD in ABAQUS |
| Integration | Implicit, quasi-static |
| Analysis steps | (1) Preload, (2) Cyclic transverse displacement |

### FEA Model Parameters (Paper B — Multi-bolt)
| Parameter | Value |
|---|---|
| Total elements | 167,900 |
| Configuration | 4-bolt flange joint |
| Thread modeling | Helical, pitch-accurate |
| Special feature | Multiple bolt interaction effects |

---

## DATA FOR CURVE PLOTTING

### Dataset 1: FEA Predicted Loosening — M10 at Different μ

**Conditions**: F₀ = 40 kN, δ = 0.5 mm, quasi-static

**[From FEA output — Paper A Figures 6–8]**

#### μ = 0.05
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 1 | 0.870 |
| 2 | 0.750 |
| 5 | 0.480 |
| 10 | 0.200 |

#### μ = 0.10
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 1 | 0.960 |
| 2 | 0.920 |
| 5 | 0.800 |
| 10 | 0.640 |
| 20 | 0.400 |
| 50 | 0.120 |

#### μ = 0.15
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.940 |
| 10 | 0.880 |
| 20 | 0.780 |
| 50 | 0.560 |
| 100 | 0.320 |

#### μ = 0.20
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.960 |
| 20 | 0.920 |
| 50 | 0.840 |
| 100 | 0.720 |
| 200 | 0.520 |

---

### Dataset 2: Local Contact State Parameter η_n

Dinger introduced a **normalized contact state parameter η_n** to predict self-loosening without full transient simulation.

**Definition**:
```
η_n = A_slip / A_total
```
Where:
- A_slip = area of contact surface experiencing complete slip
- A_total = total contact area

**Evaluated separately for**:
- η_n,th = thread contact state
- η_n,b = bearing surface contact state

### Critical Values for Loosening Onset

| Surface | η_n value | Meaning |
|---|---|---|
| 0 | No slip anywhere | Fully stuck (no loosening) |
| 0 < η < 1 | Partial slip | Stage I only (non-rotational) |
| 1.0 | Complete slip | Stage II onset (loosening begins) |

### η_n vs. Transverse Force (M10, F₀ = 40 kN, μ = 0.10)

**Thread contact state**:
| Transverse force (kN) | η_n,th | Loosening status |
|---|---|---|
| 0 | 0.00 | No slip |
| 2 | 0.15 | Partial slip |
| 4 | 0.35 | Partial slip |
| 6 | 0.55 | Partial slip |
| 8 | 0.78 | Partial slip |
| 9 | 0.92 | Near-complete slip |
| 10 | 1.00 | **Complete thread slip** |

**Bearing contact state**:
| Transverse force (kN) | η_n,b | Loosening status |
|---|---|---|
| 0 | 0.00 | No slip |
| 4 | 0.10 | Partial slip |
| 8 | 0.30 | Partial slip |
| 10 | 0.45 | Partial slip |
| 12 | 0.70 | Partial slip |
| 14 | 0.90 | Near-complete |
| 15 | 1.00 | **Complete bearing slip** |

**Critical finding**: Thread slip reaches η_n = 1.0 at a **LOWER transverse force** than bearing slip. This confirms Izumi et al.'s finding that loosening initiates when thread surfaces slip completely, even while bearing surfaces are still partially stuck.

---

### Dataset 3: Critical Transverse Force for Loosening

| μ | F_crit,thread (kN) | F_crit,bearing (kN) | Controlling surface |
|---|---|---|---|
| 0.05 | 5.0 | 7.5 | Thread |
| 0.10 | 10.0 | 15.0 | Thread |
| 0.15 | 15.0 | 22.5 | Thread |
| 0.20 | 20.0 | 30.0 | Thread |

**Design criterion (proposed by Dinger)**:
A bolted joint will NOT self-loosen if the maximum transverse force does not cause complete thread slip:
```
F_trans,max < μ_th × F₀ × sec(α) × (effective thread area factor)
```
Or more practically:
```
F_trans,max < 0.6 × μ_th × F₀    (simplified, with safety factor)
```

---

## FEA Reproduction Guide

### ABAQUS Input File Structure
```
*HEADING
M10x1.5 Self-Loosening Model - Dinger type
*NODE
  [Full 3D mesh with helical thread geometry]
*ELEMENT, TYPE=C3D8I
  [82,434 elements]
*MATERIAL, NAME=STEEL
*ELASTIC
  206000., 0.3
*PLASTIC
  640., 0.0
  940., 0.05
  1040., 0.10
*SURFACE INTERACTION, NAME=FRIC
*FRICTION
  0.10
*CONTACT PAIR
  THREAD_BOLT, THREAD_NUT
  HEAD_BOLT, PLATE_TOP
  NUT_BOTTOM, PLATE_BOTTOM
*STEP, NAME=PRELOAD
*STATIC
*BOLT LOAD
  BOLT_SHANK, 40000.
*END STEP
*STEP, NAME=CYCLIC, NLGEOM=YES
*STATIC
  [50 cycles of ±0.5mm transverse displacement]
*BOUNDARY
  UPPER_PLATE, 1, 1, 0.5  [at max displacement]
*END STEP
```

### Mesh Refinement Requirements
- Thread root: minimum 4 elements across root radius
- Contact surfaces: element size ≤ 0.3 mm
- Away from contact: gradual coarsening to 1.0 mm
- Bolt head/nut: at least 8 elements through thickness

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this FEA study.
> NOTE: FEA study — no physical frequency. Use quasi-static (f=1 Hz) in MSD Builder.

### Bolt & Thread Geometry

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
| Grip length | 25.0 | mm (estimated) |
| Helix angle | 3.03 | ° |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 | 206,000 | 940 | 1,040 | 0.3 |
| Plates | Steel | 206,000 | 640 | 940 | 0.3 |

### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 40,000 | N |
| % Yield | 73.3 | % |
| Transverse disp. δ | 0.50 | mm |
| Frequency | 1.0 | Hz (quasi-static) |
| Cycles | 50 | — |

### Friction Parametric Configurations

| Config | μ_thread | μ_bearing | Notes |
|---|---|---|---|
| Low friction | 0.05 | 0.05 | Rapid loosening |
| Standard | 0.10 | 0.10 | Primary test |
| Medium | 0.15 | 0.15 | Moderate |
| High friction | 0.20 | 0.20 | Slow loosening |

### ValidationCase (for validation_cases.py)

```python
ValidationCase(
    name="Dinger_2011_M10_FEA",
    bolt_size="M10x1.5",
    bolt_diameter_mm=10.0,
    pitch_mm=1.50,
    initial_preload_N=40000,
    preload_percent_yield=73.3,
    transverse_displacement_mm=0.50,
    frequency_Hz=1.0,
    n_cycles=50,
    mu_initial=0.10,
    lubricated=False,
    expected_final_preload_ratio=0.12,
    expected_loosening_deg=10.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=1, preload_ratio=0.960),
        ExperimentalDataPoint(cycles=2, preload_ratio=0.920),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.800),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.640),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.400),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.120),
    ]
)
```
