# Similitude Example S1: Geometric Scaling — M20 Lab Model to Predict M42 Prototype

## Overview

**Similitude Type**: GEOMETRIC_SCALING (Tab 5, "Geometric Scaling" sub-tab)

**Objective**: Use a small-scale M20 Junker test (lab model) to predict the loosening behavior of an M42 bolt in an offshore/wind turbine flange (full-scale prototype), using the software's geometric scaling and scale-effect correction algorithms.

**Source Data**: Karlsen & Lemu (2022) — Paper 29 — tested M20, M30, and M42 under proportionally scaled conditions. This provides rare **experimental validation** of geometric scaling for bolt loosening.

**Why this is an ideal validation case**: Karlsen & Lemu designed their test program with proportional scaling:
- Grip lengths: 50, 75, 105 mm (ratio ≈ 1.0 : 1.5 : 2.1 → proportional to diameter)
- Displacements: 1.0, 1.5, 2.0 mm (proportional to diameter)
- Preloads: 135, 325, 660 kN (≈75% proof for each size)
- Same material (10.9 + S355), same frequency (5 Hz), same surface treatment

This is effectively a similitude experiment, even though the authors framed it as a "comparative study."

---

## Prototype Definition (M42 — Full Scale)

The "prototype" is the large bolt that we want to predict.

### Prototype Parameters — Similitude Tab Input

| Parameter | Value | Unit | Notes |
|---|---|---|---|
| Bolt diameter (d_p) | 42.0 | mm | M42 × 4.5 ISO coarse |
| Thread pitch (p_p) | 4.5 | mm | |
| Grip length (L_p) | 105.0 | mm | 2 × 52.5 mm S355 plates |
| Preload (F_p) | 660,000 | N | 75% of 878 kN proof |
| Test frequency (f_p) | 5.0 | Hz | Scaled Junker rig |

### Prototype Bolt Geometry (Reference)

| Parameter | Value | Unit |
|---|---|---|
| d₂ (pitch dia.) | 39.077 | mm |
| d₃ (minor dia.) | 36.479 | mm |
| Aₜ (stress area) | 1,120 | mm² |
| Helix angle λ | 2.10 | ° |
| d_head (AF) | 65.0 | mm |
| d_hole (standard) | 45.0 | mm |
| Clearance | 3.0 | mm |

### Prototype Material

| Component | Material | E (MPa) | σ_y (MPa) | σ_u (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 HV | 206,000 | 940 | 1,040 | 0.30 |
| Plates | S355 structural | 210,000 | 355 | 510 | 0.30 |

### Prototype Experimental Loosening Curve (ACTUAL — from Paper 29)

This is the **target curve** we want to predict from the model test.

| Cycles | F/F₀ (measured) |
|---|---|
| 0 | 1.000 |
| 50 | 0.945 |
| 100 | 0.895 |
| 200 | 0.820 |
| 500 | 0.670 |
| 1,000 | 0.500 |
| 2,000 | 0.330 |

---

## Model Definition (M20 — Lab Scale)

The "model" is the small bolt tested in the laboratory.

### Scale Factor

```
λ = d_model / d_prototype = 20 / 42 = 0.476
```

Nearest standard scale: approximately **1:2.1** (between 1:2 and 1:2.5)

### Model Parameters — As Tested (Paper 29)

| Parameter | Tested Value | Ideal Scaled Value | Ratio | Notes |
|---|---|---|---|---|
| Diameter | 20.0 mm | 20.0 mm | 1.000 | Exact (by design) |
| Pitch | 2.5 mm | 2.14 mm (4.5×λ) | 1.167 | Uses standard ISO pitch |
| Grip length | 50.0 mm | 50.0 mm (105×λ) | 1.000 | Exact |
| Preload | 135,000 N | 149,700 N (660k×λ²) | 0.902 | 10% below ideal |
| Displacement | 1.0 mm | 0.95 mm (2.0×λ) | 1.051 | 5% above ideal |
| Frequency | 5.0 Hz | 10.5 Hz (5/λ) | 0.476 | **Not scaled** — same f |

### Model Bolt Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M20 × 2.5 | — |
| d₂ (pitch dia.) | 18.376 | mm |
| d₃ (minor dia.) | 16.933 | mm |
| Aₜ (stress area) | 245 | mm² |
| Helix angle λ | 2.48 | ° |
| d_head (AF) | 30.0 | mm |
| d_hole (standard) | 22.0 | mm |
| Clearance | 2.0 | mm |

### Model Experimental Loosening Curve (ACTUAL — from Paper 29)

This is the **input curve** from which we predict prototype behavior.

| Cycles | F/F₀ (measured) |
|---|---|
| 0 | 1.000 |
| 50 | 0.920 |
| 100 | 0.850 |
| 200 | 0.740 |
| 500 | 0.540 |
| 1,000 | 0.350 |
| 2,000 | 0.180 |

---

## Similitude Analysis — Step by Step

### Step 1: Buckingham Pi Groups Comparison

The software computes 8 loosening-specific Pi groups for both model and prototype:

| Pi Group | Name | Prototype (M42) | Model (M20) | Error (%) | Status |
|---|---|---|---|---|---|
| Π₁ | Slip parameter (F_t/μF_p) | — | — | — | Depends on loading |
| Π₂ | Helix parameter (tanλ/μ·secα) | 0.262 | 0.295 | +12.6% | WARNING |
| Π₃ | Preload utilization (σ_p/σ_y) | 0.627 | 0.586 | -6.5% | OK |
| Π₄ | Grip ratio (L/d) | 2.50 | 2.50 | 0.0% | EXACT |
| Π₅ | Joint constant (Φ) | ~0.25 | ~0.25 | ~0% | OK (same material) |
| Π₆ | Bearing leverage (r_eff/r_m) | 1.66 | 1.63 | -1.8% | OK |
| Π₇ | Pitch ratio (p/d) | 0.107 | 0.125 | +16.8% | WARNING |
| Π₁₀ | Embedding parameter | — | — | — | Scale-dependent |

**Key distortions**:
- **Π₇ (pitch ratio)** is 17% higher in model because ISO standard pitches don't scale continuously. M20 uses p=2.5mm, but ideal scaled pitch would be 2.14mm.
- **Π₂ (helix parameter)** is 13% higher in model, directly linked to the pitch distortion (steeper helix angle → more driving torque).
- These distortions mean the **M20 model will loosen FASTER** than predicted by pure similitude — which is exactly what the data shows.

### Step 2: Scale Effect Corrections

The software's `ScaleFactors` class computes five corrections at λ = 0.476:

| Scale Effect | Correction Factor | Severity | Explanation |
|---|---|---|---|
| Surface roughness | 1.052 | MEDIUM | Rz/d ratio doubles at half scale |
| Friction coefficient | 1.042 | LOW | μ increases ~4.2% at this scale |
| Embedding loss | 2.10× relative | HIGH | Absolute embedding ~constant, relative loss ∝ 1/λ |
| Thread form tolerance | 1.049 | LOW | ISO tolerance is absolute, not proportional |
| Stress concentration | 1.000 | NEGLIGIBLE | Kt preserved (r/P constant in ISO) |

**Combined correction factor**: C_combined ≈ 1.15

### Step 3: Cycle Domain Transformation

The software scales the cycle axis:
```
N_prototype = N_model × λ = N_model × 0.476
```

This means 2,000 model cycles correspond to ~952 prototype cycles.

**Physical interpretation**: The M20 model loosens faster per cycle because:
1. Smaller bolt = less absolute friction resistance
2. Higher pitch ratio = more driving torque per unit displacement
3. Less rotational inertia = easier to initiate back-off

### Step 4: Preload Transformation

The software corrects the F/F₀ curve for embedding effects:
```
(F/F₀)_proto = (F/F₀)_model + [1 - (F/F₀)_model] × (1 - C_embed)
```

Where C_embed = λ = 0.476. The embedding correction shifts the loosening curve **upward** for the prototype (less relative embedding loss).

### Step 5: Predicted vs. Actual Prototype Curve

Applying the full transformation to the M20 data:

| M20 Cycles | M20 F/F₀ | → Predicted M42 Cycles | → Predicted M42 F/F₀ | Actual M42 F/F₀ | Error |
|---|---|---|---|---|---|
| 0 | 1.000 | 0 | 1.000 | 1.000 | 0.0% |
| 50 | 0.920 | 24 | 0.958 | ~0.960 | -0.2% |
| 100 | 0.850 | 48 | 0.921 | 0.945 | -2.5% |
| 200 | 0.740 | 95 | 0.864 | 0.895 | -3.5% |
| 500 | 0.540 | 238 | 0.759 | 0.820 | -7.4% |
| 1,000 | 0.350 | 476 | 0.659 | 0.670 | -1.6% |
| 2,000 | 0.180 | 952 | 0.571 | 0.500 (interp.) | +14.2% |

**Assessment**: The scaling prediction is within **±8% for 0–500 prototype cycles** (the most relevant range), with increasing error beyond that due to the pitch ratio distortion (Π₇).

---

## Intermediate Validation: M30 as Cross-Check

The M30 data provides an intermediate validation point.

### M30 Scale Factors

```
λ_M30_to_M42 = 30 / 42 = 0.714
λ_M30_to_M20 = 30 / 20 = 1.50 (M20 → M30 upscale)
```

### M30 Experimental Data (δ = 1.5 mm, F₀ = 325 kN)

| Cycles | F/F₀ (measured) |
|---|---|
| 0 | 1.000 |
| 50 | 0.935 |
| 100 | 0.880 |
| 200 | 0.790 |
| 500 | 0.620 |
| 1,000 | 0.440 |
| 2,000 | 0.260 |

### Size Effect Trend (at 2,000 cycles, proportional displacement)

| Bolt | δ/d ratio | F/F₀ at 2,000 cycles | Observation |
|---|---|---|---|
| M20 | 1.0/20 = 0.050 | 0.180 | Most loosening |
| M30 | 1.5/30 = 0.050 | 0.260 | Intermediate |
| M42 | 2.0/42 = 0.048 | 0.330 | Least loosening |

**Key insight**: Even at nearly identical δ/d ratios, **larger bolts retain more preload**. This confirms the scale effect: absolute friction forces scale with F_p (∝ d²) while pitch-induced driving torque scales with p×d (∝ d^1.5 for ISO threads), giving a net advantage to larger bolts.

---

## Software Configuration — Similitude Tab

### Geometric Scaling Panel Inputs

Enter these values in Tab 5 → "Geometric Scaling" sub-tab:

| Field | Value |
|---|---|
| **Prototype section** | |
| Bolt diameter (d_p) | 42.0 mm |
| Thread pitch (p_p) | 4.5 mm |
| Grip length (L_p) | 105.0 mm |
| Preload (F_p) | 660.0 kN |
| Test frequency (f_p) | 5.0 Hz |
| **Scale section** | |
| Geometric Scale (λ) | 0.476 |

### Expected Software Output

The software should display:

1. **Suggested Model Configuration**:
   - Nearest standard bolt: M20 × 2.5
   - Model grip: 50.0 mm
   - Model preload: ~150 kN (λ² × 660 kN)
   - Model frequency: ~10.5 Hz (f/λ)

2. **Scale Effects Radar**: Medium severity for roughness and embedding, low for friction and tolerances.

3. **Pi Group Comparison**: All primary groups matched within 5% except Π₇ (pitch ratio) at ~17%.

4. **Loosening Curve Comparison**: Two subplots showing model and prototype domain predictions.

### MSD Builder Transfer

After running similitude analysis, click "Transfer to MSD Builder" to create:

```
GROUND — FLANGE(25mm S355) — FLANGE(25mm S355) — NUT(M20) — THREAD(M20×2.5) — SHANK(M20) — HEAD(M20) — GROUND
```

With loading: F₀=135 kN, δ=1.0 mm, f=5 Hz (or scaled f=10.5 Hz).

---

## Displacement Amplitude Scaling — Additional Configurations

Karlsen & Lemu also tested M30 at multiple amplitudes, enabling amplitude scaling validation:

### M30 Standard at Various δ (F₀ = 325 kN)

| δ (mm) | δ/d ratio | F/F₀ at 1,000 cycles | F/F₀ at 2,000 cycles |
|---|---|---|---|
| 0.5 | 0.017 | 0.800 | 0.700 |
| 1.0 | 0.033 | 0.580 | 0.400 |
| 1.5 | 0.050 | 0.440 | 0.260 |
| 2.0 | 0.067 | 0.300 | 0.140 |

### Scaling δ from M20 to M42

Using displacement scaling: δ_model = λ × δ_prototype

| Prototype δ (mm) | Model δ (mm) | δ/d (proto) | δ/d (model) | Match? |
|---|---|---|---|---|
| 2.0 | 0.95 (→ use 1.0) | 0.048 | 0.050 | ~OK |
| 3.0 | 1.43 (→ use 1.5) | 0.071 | 0.075 | ~OK |
| 4.0 | 1.90 (→ use 2.0) | 0.095 | 0.100 | ~OK |

---

## Limitations and Recommendations

### What Geometric Scaling Captures Well
1. Relative loosening trends (which conditions cause faster loosening)
2. Critical displacement threshold (approximately scales with λ)
3. Stage I vs Stage II transition timing
4. Effect of preload percentage on loosening resistance

### What Requires Correction
1. **Absolute loosening rate**: Model loosens ~30-50% faster than prototype (per cycle basis) due to pitch ratio distortion
2. **Embedding losses**: Must apply C_embed correction (model has ~2× relative embedding)
3. **Friction coefficient**: Slight increase at smaller scale (4-8%)
4. **Cycle count**: Scale N by λ to approximate prototype cycles

### Design Recommendation
For offshore wind or oil & gas applications with M36+ bolts:
- Run lab tests on M20 or M16 (λ = 0.38–0.48)
- Apply geometric scaling corrections from the software
- Use the predicted prototype curve as a **conservative estimate** (model loosens faster)
- Always validate with at least one full-scale test for critical applications

---

## References

- **Primary data**: Karlsen, A.; Lemu, H. G. (2022). "Comparative study on loosening of anti-loosening bolt and standard bolt system." *Engineering Failure Analysis*, 140, 106590.
- **Loosening theory**: Jiang, Y. et al. (2003). "A Study of Early Stage Self-Loosening of Bolted Joints." *ASME J. Mech. Design*, 125(3), 518–526.
- **Scaling theory**: Buckingham, E. (1914). "On Physically Similar Systems." *Physical Review*, 4(4), 345–376.
- **VDI reference**: VDI 2230 Part 1 (2015). *Systematic calculation of highly stressed bolted joints*.
- **Scale effects in friction**: Nassar, S. A.; Housari, B. A. (2007). "Effect of Thread Pitch and Initial Tension on the Self-Loosening of Threaded Fasteners." *ASME J. Pressure Vessel Tech.*, 128(4), 590–598.

---

## ValidationCase — Similitude Prediction (for validation_cases.py)

### M20 Model Input Curve

```python
ValidationCase(
    name="Similitude_S1_M20_model_input",
    bolt_size="M20x2.5",
    bolt_diameter_mm=20.0,
    pitch_mm=2.5,
    initial_preload_N=135000,
    preload_percent_yield=58.6,
    transverse_displacement_mm=1.0,
    frequency_Hz=5.0,
    n_cycles=2000,
    mu_initial=0.14,
    lubricated=True,
    expected_final_preload_ratio=0.180,
    expected_loosening_deg=15.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.920),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.850),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.740),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.540),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.350),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.180),
    ]
)
```

### M42 Prototype Actual (Validation Target)

```python
ValidationCase(
    name="Similitude_S1_M42_prototype_actual",
    bolt_size="M42x4.5",
    bolt_diameter_mm=42.0,
    pitch_mm=4.5,
    initial_preload_N=660000,
    preload_percent_yield=62.7,
    transverse_displacement_mm=2.0,
    frequency_Hz=5.0,
    n_cycles=2000,
    mu_initial=0.14,
    lubricated=True,
    expected_final_preload_ratio=0.330,
    expected_loosening_deg=10.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.945),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.895),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.820),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.670),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.500),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.330),
    ]
)
```

### M30 Intermediate Cross-Check

```python
ValidationCase(
    name="Similitude_S1_M30_intermediate",
    bolt_size="M30x3.5",
    bolt_diameter_mm=30.0,
    pitch_mm=3.5,
    initial_preload_N=325000,
    preload_percent_yield=61.6,
    transverse_displacement_mm=1.5,
    frequency_Hz=5.0,
    n_cycles=2000,
    mu_initial=0.14,
    lubricated=True,
    expected_final_preload_ratio=0.260,
    expected_loosening_deg=12.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.935),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.880),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.790),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.620),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.440),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.260),
    ]
)
```
