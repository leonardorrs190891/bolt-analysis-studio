# Study 02: Jiang, Zhang, Park & Lee (2003/2004) — M12 Early Stage & Full Loosening

## Full Citations

### Paper A — Early Stage
**Authors**: Jiang, Y.; Zhang, M.; Park, T.-W.; Lee, C.-H.
**Title**: "A Study of Early Stage Self-Loosening of Bolted Joints"
**Journal**: ASME Journal of Mechanical Design, 2003, 125(3), 518–526
**DOI**: 10.1115/1.1598497

### Paper B — Full Experimental Study
**Authors**: Jiang, Y.; Zhang, M.; Lee, C.-H.
**Title**: "An Experimental Study of Self-Loosening of Bolted Joints"
**Journal**: ASME Journal of Mechanical Design, 2004, 126(5), 925–931
**DOI**: 10.1115/1.1767814

---

## Experimental Setup

### Bolt Specifications
- **Size**: M12 × 1.75 (ISO metric coarse thread)
- **Property class**: 10.9
- **Material**: Alloy steel, quenched and tempered
- **Yield strength R_p0.2**: 940 MPa
- **Ultimate tensile strength R_m**: 1,040 MPa
- **Proof load**: 83,200 N (M12 Class 10.9)
- **Thread pitch**: 1.75 mm
- **Stress area**: 84.3 mm²
- **Nominal diameter**: 12 mm
- **Pitch diameter**: 10.863 mm
- **Minor diameter**: 10.106 mm
- **Thread angle**: 60°
- **Helix angle**: approximately 2.93°

### Nut Specifications
- **Type**: Standard hex nut, Class 10
- **Special modification (Paper A only)**: Nut GLUED to bolt with cyanoacrylate adhesive to prevent nut rotation → isolates Stage I (non-rotational) preload loss

### Clamped Members
- **Material**: Steel plates
- **Surface condition**: Ground, clean, no coating
- **Thickness**: Variable (see grip length below)

### Test Fixture
- **Type**: Custom transverse vibration test machine (NOT standard Junker)
- **Loading**: Displacement-controlled cyclic transverse displacement
- **Actuation**: Hydraulic actuator
- **Preload measurement**: Strain-gauged bolt (4-gauge full bridge)
- **Nut rotation measurement**: Graduated scale and angular position sensor
- **Number of specimens tested**: **>100 individual bolted joints** (Paper B)

### Washer
- **Type**: Standard flat washer, hardened

---

## Test Parameters

### Standard Test Conditions (Paper B)
- **Standard preload**: 25,000 N (25 kN) → 29.7% of proof load
- **Alternative preload**: 41,000 N (41 kN) → 49.3% of proof load
- **Displacement amplitudes**: 0.127 mm to 1.27 mm (0.005" to 0.050")
- **Frequency**: 5 Hz
- **Grip length**: ~25 mm (standard); also tested at ~38 mm and ~51 mm
- **Hole clearance**: Standard (approximately 13.5 mm hole for M12)
- **Cycle count**: Up to 500+ cycles
- **Surface condition**: As-received (no lubricant), μ ≈ 0.15–0.20

### Early Stage Test Conditions (Paper A)
- **Preload**: 25 kN
- **Displacement amplitude**: 0.46 mm (0.018")
- **Frequency**: 5 Hz
- **Cycles**: 200 (to capture Stage I only)
- **Special condition**: Nut glued to prevent rotation

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Early Stage (Stage I) — Nut Glued, No Rotation (Paper A)

**Conditions**: M12×1.75, Class 10.9, F₀ = 25 kN, δ = 0.46 mm, f = 5 Hz

**[APPROXIMATE — digitized from Paper A, Figure 4]**

| Cycles | Preload (N) | F/F₀ | Nut rotation (°) |
|---|---|---|---|
| 0 | 25,000 | 1.000 | 0.0 |
| 1 | 24,200 | 0.968 | 0.0 |
| 5 | 23,000 | 0.920 | 0.0 |
| 10 | 22,000 | 0.880 | 0.0 |
| 20 | 21,000 | 0.840 | 0.0 |
| 50 | 19,500 | 0.780 | 0.0 |
| 100 | 18,000 | 0.720 | 0.0 |
| 150 | 17,000 | 0.680 | 0.0 |
| 200 | 16,500 | 0.660 | 0.0 |

**Key finding**: 10–34% preload loss WITHOUT any nut rotation. This is purely from cyclic plastic deformation (ratchetting) at thread roots and under-head contact. Jiang identified this as a previously unrecognized mechanism.

### Dataset 2: Full Loosening at Different Displacement Amplitudes (Paper B)

**Conditions**: M12×1.75, Class 10.9, F₀ = 25 kN, f = 5 Hz, standard grip length

**[APPROXIMATE — digitized from Paper B, Figure 5]**

#### δ = 0.254 mm (0.010")
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 25,000 | 1.000 |
| 50 | 24,000 | 0.960 |
| 100 | 23,200 | 0.928 |
| 200 | 22,500 | 0.900 |
| 300 | 22,000 | 0.880 |
| 500 | 21,500 | 0.860 |

*Loosening stabilized — below endurance limit*

#### δ = 0.381 mm (0.015")
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 25,000 | 1.000 |
| 10 | 23,500 | 0.940 |
| 20 | 22,500 | 0.900 |
| 50 | 20,500 | 0.820 |
| 100 | 18,000 | 0.720 |
| 200 | 14,000 | 0.560 |
| 300 | 11,000 | 0.440 |
| 500 | 7,000 | 0.280 |

#### δ = 0.46 mm (0.018")
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 25,000 | 1.000 |
| 5 | 23,500 | 0.940 |
| 10 | 22,000 | 0.880 |
| 20 | 19,500 | 0.780 |
| 50 | 14,000 | 0.560 |
| 100 | 8,500 | 0.340 |
| 150 | 5,000 | 0.200 |
| 200 | 3,000 | 0.120 |
| 250 | 2,000 | 0.080 |

#### δ = 0.635 mm (0.025")
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 25,000 | 1.000 |
| 5 | 21,000 | 0.840 |
| 10 | 17,000 | 0.680 |
| 20 | 11,000 | 0.440 |
| 50 | 4,000 | 0.160 |
| 100 | 1,500 | 0.060 |

#### δ = 1.27 mm (0.050")
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 25,000 | 1.000 |
| 2 | 18,000 | 0.720 |
| 5 | 12,000 | 0.480 |
| 10 | 6,000 | 0.240 |
| 20 | 2,000 | 0.080 |
| 50 | 500 | 0.020 |

---

### Dataset 3: D-N Curve (Displacement Amplitude vs. Cycles to Loosening)

**Loosening criterion**: Preload reaches 10% of initial value (2,500 N)

**[APPROXIMATE — from Paper B composite data]**

| Displacement amplitude δ (mm) | Cycles to F = 0.10·F₀ | Cycles to F = 0.50·F₀ |
|---|---|---|
| 0.254 | Did not loosen | Did not loosen |
| 0.381 | ~450 | ~150 |
| 0.46 | ~220 | ~65 |
| 0.508 | ~150 | ~40 |
| 0.635 | ~80 | ~20 |
| 0.762 | ~50 | ~12 |
| 1.016 | ~25 | ~6 |
| 1.27 | ~15 | ~4 |

**Endurance limit**: approximately **0.25–0.30 mm** for M12 at 25 kN preload.

---

### Dataset 4: Effect of Higher Preload (Paper B)

**Conditions**: M12×1.75, F₀ = 41 kN, δ = 0.46 mm, f = 5 Hz

**[APPROXIMATE — digitized from Paper B, Figure 8]**

| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 41,000 | 1.000 |
| 10 | 39,000 | 0.951 |
| 20 | 37,500 | 0.915 |
| 50 | 34,000 | 0.829 |
| 100 | 29,000 | 0.707 |
| 200 | 22,000 | 0.537 |
| 300 | 16,000 | 0.390 |
| 500 | 8,000 | 0.195 |

**Key finding**: Higher preload extends loosening life but does NOT prevent it at sufficiently high displacement amplitudes. The D-N curve shifts upward but maintains the same shape.

---

## Stage I / Stage II Transition

Jiang identified the transition from non-rotational (Stage I) to rotational (Stage II) loosening:

- **Transition point**: approximately **0.5° of nut rotation** (measured)
- **Stage I duration**: depends on displacement amplitude
  - At δ = 0.46 mm: ~50–100 cycles
  - At δ = 1.27 mm: ~2–5 cycles
- **Stage I preload loss**: 10–40% depending on amplitude
- **Stage II**: Linear nut rotation vs. cycles → exponential preload decay

### Nut Rotation vs. Cycles (δ = 0.46 mm, F₀ = 25 kN)

**[APPROXIMATE — from Paper A/B]**

| Cycles | Cumulative nut rotation (°) | Stage |
|---|---|---|
| 0 | 0.0 | — |
| 10 | 0.1 | I |
| 20 | 0.2 | I |
| 50 | 0.5 | I→II transition |
| 100 | 2.5 | II |
| 150 | 6.0 | II |
| 200 | 10.0 | II |
| 250 | 14.0 | II |

---

## Mechanism Description (from Jiang's papers)

### Stage I — Non-Rotational
- Caused by **cyclic plastic deformation** (ratchetting) at thread roots and bearing surfaces
- Material constitutive model: **Armstrong-Frederick kinematic hardening** with Jiang-Sehitoglu modifications
- Preload loss occurs even with nut glued → no relative rotation
- Loss is proportional to displacement amplitude
- Loss saturates after ~200 cycles (material stabilizes)

### Stage II — Rotational
- Nut begins to rotate relative to bolt
- Rotation rate approximately constant (linear nut angle vs. cycles)
- Preload decays exponentially with rotation
- Initiated when localized slip at thread/bearing surfaces coalesces into complete slip
- **Complete thread slip occurs BEFORE complete bearing slip** (per Izumi et al. 2005)

---

## Setup Reproduction Notes

### FEA Model Parameters (from Jiang et al. 2007, J. Mech. Des. 129:218–226)
- **Software**: ABAQUS/Standard
- **Element type**: C3D8R (8-node brick, reduced integration)
- **Total nodes**: ~22,387
- **Total elements**: ~18,000
- **Thread modeling**: Full helical geometry (NOT simplified)
- **Contact**: Surface-to-surface, Coulomb friction μ = 0.10 (parametric studies also at 0.05, 0.15, 0.20)
- **Preload application**: Thermal expansion method (ΔT applied to bolt shank to induce preload)
- **Material model**: Elastic-plastic with kinematic hardening
- **Loading**: Displacement applied to upper plate at 0.46 mm amplitude, quasi-static (inertia neglected)
- **Boundary conditions**: Lower plate fixed; upper plate free in transverse direction, constrained axially
- **Solution**: Implicit integration, automatic time stepping

### Experimental Fixture Critical Dimensions
- **Plate thickness**: 12.7 mm per plate (two plates clamped)
- **Total grip length**: approximately 25.4 mm
- **Hole diameter**: 13.5 mm (1.5 mm clearance)
- **Plate material**: AISI 1045 steel, normalized
- **Bolt length**: 40 mm (under head)
- **Thread engagement**: Full nut height (10.4 mm for M12)

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this experiment.

### Bolt & Thread Geometry

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
| Grip length | 25.4 | mm |
| Helix angle | 2.93 | ° |
| r_be (eff. bearing) | 7.60 | mm |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 Q&T | 206,000 | 940 | 1,040 | 0.3 |
| Plates | AISI 1045 | 200,000 | 530 | 690 | 0.29 |

### MSD Element Chain

```
GROUND — FLANGE(12.7mm) — FLANGE(12.7mm) — NUT — THREAD — SHANK — HEAD — GROUND
```

| Element | Key Parameters |
|---|---|
| HEAD | d=12.0, d_head=18.0, h_head=7.5 mm |
| SHANK | d=12.0, L≈15.0 mm (unthreaded portion) |
| THREAD | d=12.0, p=1.75, L=10.4 mm (engaged), At=84.3 |
| NUT | d=12.0, p=1.75, h_nut=10.4 mm |
| WASHER | d_bolt=12.0, OD=24.0, t=2.5 mm (hardened flat) |
| FLANGE_1 | t=12.7 mm, d_hole=13.5 mm, E=200,000 |
| FLANGE_2 | t=12.7 mm, d_hole=13.5 mm, E=200,000 |

### Loading (PropertyInspector) — Baseline Test

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 25,000 | N |
| % Yield | 31.6 | % |
| Transverse disp. δ | 0.46 | mm |
| Frequency | 5.0 | Hz |
| Cycles | 250 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 |
| Lubricated | false |
| Bolt diameter | 12.0 mm |
| Pitch | 1.75 mm |

### Additional Test Configurations

| Config | F₀ (N) | δ (mm) | f (Hz) | Notes |
|---|---|---|---|---|
| Stage I only (glued nut) | 25,000 | 0.46 | 5 | Non-rotational loss only |
| Baseline | 25,000 | 0.46 | 5 | Primary validation curve |
| Small amplitude | 25,000 | 0.254 | 5 | Near threshold — no loosening |
| Medium amplitude | 25,000 | 0.381 | 5 | Moderate loosening |
| Large amplitude | 25,000 | 0.635 | 5 | Rapid loosening |
| Extreme amplitude | 25,000 | 1.27 | 5 | Very rapid loosening |
| High preload | 41,000 | 0.46 | 5 | 49.3% proof |

### ValidationCase (for validation_cases.py)

```python
ValidationCase(
    name="Jiang_2003_M12_baseline",
    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,
    initial_preload_N=25000,
    preload_percent_yield=31.6,
    transverse_displacement_mm=0.46,
    frequency_Hz=5.0,
    n_cycles=250,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.08,
    expected_loosening_deg=14.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.940),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.880),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.780),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.560),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.340),
        ExperimentalDataPoint(cycles=150, preload_ratio=0.200),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.120),
        ExperimentalDataPoint(cycles=250, preload_ratio=0.080),
    ]
)
```
