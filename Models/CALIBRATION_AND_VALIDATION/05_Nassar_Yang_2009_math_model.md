# Study 05: Nassar & Yang (2009) — Nonlinear Mathematical Model for Vibration-Induced Loosening

## Full Citation
**Authors**: Nassar, S. A.; Yang, X.
**Title**: "A Mathematical Model for Vibration-Induced Loosening of Preloaded Threaded Fasteners"
**Journal**: ASME Journal of Vibration and Acoustics, 2009, 131(2), 021009
**DOI**: 10.1115/1.2981165

---

## Model Description

This paper presents the **definitive nonlinear analytical model** for predicting self-loosening of preloaded threaded fasteners under transverse harmonic excitation. It supersedes the earlier linear model (Nassar & Housari 2005) and is the most complete closed-form solution available.

### Model Assumptions
1. Bolt and nut modeled as rigid bodies (thread deformation neglected)
2. Thread helix is a continuous inclined plane with friction
3. Bearing surface is a flat annular contact with friction
4. Transverse displacement is harmonic: δ(t) = δ₀ sin(ωt)
5. Both complete slip and partial slip phases are modeled
6. Preload decreases incrementally each cycle due to nut back-off

### Degrees of Freedom
- **Transverse displacement**: Applied (input)
- **Nut rotation θ**: Computed (output)
- **Axial displacement (preload)**: Computed from θ via pitch relationship

---

## Complete Equation Set for Implementation

### Geometric Parameters
```
d₂ = bolt pitch diameter (mm)
d_h = bolt head / washer bearing diameter, outer (mm)
d_w = hole diameter (mm)
p = thread pitch (mm)
α = thread half-angle = 30° (for metric threads)
β = helix angle = arctan(p / (π × d₂))
r_t = d₂ / 2 (thread pitch radius)
r_be = (d_h + d_w) / (2 × 2) × (d_h² + d_h×d_w + d_w²) / (d_h² + d_w²)  [effective bearing radius]
```

Note on r_be: The effective bearing radius for a hollow annular contact is:
```
r_be = (2/3) × (R³ - r³) / (R² - r²)
```
Where R = d_h/2 (outer bearing radius) and r = d_w/2 (hole radius).

### Thread Forces During Transverse Loading

The thread shear force due to transverse displacement:
```
F_ts = (3 × E × I₁) / (k × L³) × δ₀ × sin(ωt)
```
Where:
- E = Young's modulus of bolt
- I₁ = second moment of area of engaged thread cross-section
- k = correction factor for thread stiffness
- L = engaged thread length

### Bearing Surface Shear Force
```
F_bs = (3 × E × I₂) / (L_b³) × δ₀ × sin(ωt)
```
Where I₂ is the second moment of area for bearing contact.

### Critical Forces for Complete Slip
```
F_ts_cr = μ_th × F × (1 / cos(α))   [thread critical force]
F_bs_cr = μ_b × F                    [bearing critical force]
```
Where F is the current axial preload.

### Net Loosening Torque per Half-Cycle

When complete slip occurs at both interfaces:
```
T_loosening = F × [p/(2π)] - F × μ_b × r_be × sign(θ̇) + T_thread_net
```

Where T_thread_net accounts for the asymmetry between the tightening and loosening directions of thread friction:
```
T_thread_net = F × μ_th × r_t / cos(α) × [sin(β + φ) - sin(β - φ)]
```
With φ = arctan(μ_th / cos(α)) being the friction angle.

### Incremental Nut Rotation per Cycle
```
Δθ_cycle = ∫₀^(2π/ω) (T_net / J_eff) dt
```
This integral must be evaluated numerically because T_net changes sign and magnitude through the cycle depending on slip state.

### Preload Update
After each cycle:
```
F_{n+1} = F_n - k_b × Δθ_cycle × p / (2π)
```
Where k_b is the bolt-joint stiffness:
```
k_b = (k_bolt × k_joint) / (k_bolt + k_joint)
```

---

## MODEL VALIDATION DATA (for plotting against theory)

### Test Conditions for Validation
- **Bolt**: 5/16"-24 UNF × 1.5" (≈ M8×1.06) hex head cap screw
- **Property class**: SAE Grade 8 (equivalent to Class 10.9)
- **Preload**: 11,120 N (2,500 lbf)
- **Displacement amplitude**: 0.71 mm (0.028")
- **Frequency**: 7 Hz
- **μ_th**: 0.10 (phosphate + oil)
- **μ_b**: 0.10 (phosphate + oil)

### Predicted vs. Measured Loosening Curve

**[APPROXIMATE — from Figure 6 of paper]**

| Cycles | F/F₀ (Measured) | F/F₀ (Model predicted) |
|---|---|---|
| 0 | 1.000 | 1.000 |
| 10 | 0.850 | 0.870 |
| 20 | 0.720 | 0.740 |
| 50 | 0.480 | 0.510 |
| 100 | 0.250 | 0.280 |
| 150 | 0.130 | 0.150 |
| 200 | 0.070 | 0.080 |

**Agreement**: Model predicts loosening within **±5–10%** of experimental values.

---

## Parametric Predictions from Model

### Effect of Preload Level (δ₀ = 0.71 mm, μ = 0.10)

| Initial preload F₀ (N) | Cycles to 50% loss | Cycles to 90% loss |
|---|---|---|
| 5,560 (1,250 lbf) | ~20 | ~80 |
| 11,120 (2,500 lbf) | ~35 | ~130 |
| 16,680 (3,750 lbf) | ~55 | ~200 |
| 22,240 (5,000 lbf) | ~80 | ~300 |

### Effect of Displacement Amplitude (F₀ = 11,120 N, μ = 0.10)

| Amplitude δ₀ (mm) | Cycles to 50% loss | Cycles to 90% loss |
|---|---|---|
| 0.25 | >500 (no full slip) | >1,000 |
| 0.50 | ~90 | ~350 |
| 0.71 | ~35 | ~130 |
| 1.00 | ~15 | ~55 |
| 1.50 | ~6 | ~20 |

### Effect of Friction (F₀ = 11,120 N, δ₀ = 0.71 mm)

| μ_th = μ_b | Cycles to 50% loss | Cycles to 90% loss |
|---|---|---|
| 0.05 | ~12 | ~45 |
| 0.10 | ~35 | ~130 |
| 0.15 | ~80 | ~300 |
| 0.20 | ~200 | ~800 |
| 0.30 | ~1,000+ | >5,000 |

---

## Implementation Notes for Software

### Algorithm for Computing Loosening Curve
```
INPUT: F₀, δ₀, ω, μ_th, μ_b, bolt geometry, material properties
SET: F = F₀, θ_total = 0

FOR each cycle n = 1 to N_max:
    1. Compute F_ts_max and F_bs_max for current δ₀
    2. Check if F_ts_max > F_ts_cr (thread complete slip?)
    3. Check if F_bs_max > F_bs_cr (bearing complete slip?)
    4. IF both complete slip:
         Compute T_net by integrating torque over one cycle
         Compute Δθ = T_net × Δt² / J_eff (simplified)
    5. ELSE IF partial slip only:
         Δθ ≈ 0 (negligible loosening in partial slip)
    6. UPDATE:
         θ_total += Δθ
         ΔF = k_b × Δθ × p / (2π)
         F = F - ΔF
    7. IF F < 0.01 × F₀: BREAK (fully loosened)
    8. STORE: (n, F, F/F₀, θ_total)

OUTPUT: Preload decay curve and nut rotation curve
```

### Key Physical Constants for 5/16"-24 UNF
| Parameter | Value | Units |
|---|---|---|
| Nominal diameter d | 7.938 | mm |
| Pitch p | 1.058 | mm (24 TPI) |
| Pitch diameter d₂ | 7.249 | mm |
| Minor diameter | 6.731 | mm |
| Stress area | 36.4 | mm² |
| Thread half-angle α | 30 | ° |
| Helix angle β | 2.66 | ° |
| Head bearing OD | 12.7 | mm |
| Hole diameter | 8.73 | mm |
| Effective bearing radius r_be | 5.24 | mm |
| Bolt E | 206,000 | MPa |
| Bolt length (grip) | 25.4 | mm |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this experiment.
> NOTE: Inch-series 5/16"-24 UNF ≈ M8×1.06 equivalent. Use metric closest match M8×1.25 in MSD Builder, or enter custom thread geometry.

### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | 5/16"-24 UNF (≈M8×1.06) | — |
| d (nominal) | 7.938 | mm |
| p (pitch) | 1.058 | mm |
| d₂ (pitch dia.) | 7.249 | mm |
| d₃ (minor dia.) | 6.731 | mm |
| Aₜ (stress area) | 36.4 | mm² |
| Head bearing OD | 12.7 | mm |
| Head height | 7.94 | mm |
| d_hole | 8.73 | mm |
| Grip length | 25.4 | mm |
| Helix angle | 2.66 | ° |
| r_be (eff. bearing) | 5.24 | mm |

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
| HEAD | d=7.94, d_head=12.7, h_head=7.94 mm |
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
| Lubricated | true |
| Bolt diameter | 7.94 mm |
| Pitch | 1.058 mm |

### Additional Test Configurations

| Config | F₀ (N) | δ (mm) | μ | Notes |
|---|---|---|---|---|
| Low preload | 5,560 | 0.71 | 0.10 | Rapid loosening |
| Baseline | 11,120 | 0.71 | 0.10 | Primary validation |
| High preload | 16,680 | 0.71 | 0.10 | |
| Very high preload | 22,240 | 0.71 | 0.10 | |
| Small amplitude | 11,120 | 0.25 | 0.10 | Near threshold |
| Medium amplitude | 11,120 | 0.50 | 0.10 | |
| Large amplitude | 11,120 | 1.00 | 0.10 | |
| Very large | 11,120 | 1.50 | 0.10 | |
| Low friction | 11,120 | 0.71 | 0.05 | Fastest loosening |
| High friction | 11,120 | 0.71 | 0.15 | |
| Very high friction | 11,120 | 0.71 | 0.20 | |

### ValidationCase (for validation_cases.py)

```python
ValidationCase(
    name="Nassar_Yang_2009_baseline",
    bolt_size="5/16-24UNF",
    bolt_diameter_mm=7.938,
    pitch_mm=1.058,
    initial_preload_N=11120,
    preload_percent_yield=34.2,
    transverse_displacement_mm=0.71,
    frequency_Hz=7.0,
    n_cycles=200,
    mu_initial=0.10,
    lubricated=True,
    expected_final_preload_ratio=0.07,
    expected_loosening_deg=25.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.850),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.720),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.480),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.250),
        ExperimentalDataPoint(cycles=150, preload_ratio=0.130),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.070),
    ]
)
```
