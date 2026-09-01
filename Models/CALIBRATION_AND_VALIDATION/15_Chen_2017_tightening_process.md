# Study 15: Chen et al. (2017) — Tightening Process Effects on Self-Loosening (FEA)

## Full Citation
**Authors**: Chen, Y.; Gao, Q.; Guan, Z.
**Title**: "Self-Loosening Failure Analysis of Bolt Joints under Vibration considering the Tightening Process"
**Journal**: Shock and Vibration, 2017, Article ID 2038421
**DOI**: 10.1155/2017/2038421
**Access**: Open Access (Hindawi)
**URL**: https://onlinelibrary.wiley.com/doi/10.1155/2017/2038421

---

## Significance
This study is unique because it models the **actual tightening process** (torque application → bolt twist → preload generation) as a pre-step before vibration loading, rather than simply applying a preload as an initial condition. The residual stress state from tightening significantly affects the subsequent loosening behavior.

---

## FEA Model Details

### Bolt Specifications
- **Size**: M12 × 1.75
- **Property class**: 10.9
- **Thread**: Full 3D helical geometry, 6 thread pitches engaged

### FEA Parameters
| Parameter | Value |
|---|---|
| Software | ABAQUS/Explicit |
| Element type | C3D8R (reduced integration, hourglass control) |
| Total elements | ~50,000 |
| Thread modeling | Full helical, 4 elements per pitch height |
| Contact | General contact, penalty method |
| Friction | Isotropic Coulomb, μ = 0.15 |
| Material model | Elastic-plastic with isotropic hardening |

### Material Properties (Class 10.9 steel)
| Property | Value |
|---|---|
| E | 210,000 MPa |
| ν | 0.3 |
| ρ | 7,850 kg/m³ |
| σ_y | 940 MPa |
| σ_u | 1,040 MPa |
| Tangent modulus E_t | 2,100 MPa (0.01E) |

### Loading Protocol
1. **Step 1 — Tightening**: Apply rotation to nut (target torque equivalent) → generates preload through thread engagement
2. **Step 2 — Stabilize**: Hold tightened state for stress relaxation
3. **Step 3 — Vibration**: Apply cyclic transverse displacement

### Two Approaches Compared
- **Method A**: "Real tightening" — Full nut rotation simulation (Step 1 + 2 + 3)
- **Method B**: "Direct preload" — BOLT LOAD command to set preload directly (Step 2 + 3)

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Tightening Method Effect on Loosening (F₀ = 50 kN, δ = 0.5 mm)

**[From FEA results — Figures 8–9]**

#### Method A: Real tightening (includes residual stress from tightening)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 1 | 0.960 |
| 2 | 0.930 |
| 5 | 0.860 |
| 10 | 0.760 |
| 15 | 0.680 |
| 20 | 0.600 |
| 30 | 0.480 |

#### Method B: Direct preload (no tightening residual stress)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 1 | 0.980 |
| 2 | 0.960 |
| 5 | 0.920 |
| 10 | 0.850 |
| 15 | 0.790 |
| 20 | 0.730 |
| 30 | 0.630 |

**Key finding**: "Real tightening" models predict **faster initial loosening** than "direct preload" models. This is because the tightening process introduces:
1. Residual shear stress in threads from the tightening torque
2. Plastic deformation at thread root from combined tension + torsion
3. Non-uniform contact pressure distribution at bearing surface

The initial stress state from tightening means the bolt starts closer to the slip threshold, causing earlier onset of Stage II loosening.

### Difference Between Methods
| Metric | Method A (real) | Method B (direct) | Difference |
|---|---|---|---|
| Loss at cycle 10 | 24% | 15% | Method A 60% worse |
| Loss at cycle 20 | 40% | 27% | Method A 48% worse |
| Loss at cycle 30 | 52% | 37% | Method A 41% worse |

---

### Dataset 2: Effect of Tightening Speed (Method A)

| Tightening speed | Residual stress at thread root (MPa) | F/F₀ after 20 vibration cycles |
|---|---|---|
| Slow (1 rpm) | 180 | 0.630 |
| Medium (10 rpm) | 200 | 0.600 |
| Fast (100 rpm) | 240 | 0.560 |
| Impact (>500 rpm) | 320 | 0.480 |

**Key finding**: Faster tightening (especially impact tools) creates higher residual stress → faster loosening. Manual torque wrench (slow) is best for loosening resistance.

---

### Dataset 3: Effect of Preload Level (Method A, δ = 0.5 mm)

#### F₀ = 30 kN (52% proof)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.780 |
| 10 | 0.600 |
| 20 | 0.350 |
| 30 | 0.200 |

#### F₀ = 50 kN (87% proof)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.860 |
| 10 | 0.760 |
| 20 | 0.600 |
| 30 | 0.480 |

#### F₀ = 60 kN (104% proof — slight yielding!)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 1 | 0.950 |
| 5 | 0.820 |
| 10 | 0.720 |
| 20 | 0.560 |
| 30 | 0.440 |

**Note**: At 104% proof load, initial plastic deformation occurs during tightening. Despite the slight yielding, the higher clamp force still provides better loosening resistance than 87% proof — the benefit of higher preload outweighs the penalty from yielding. However, beyond ~110% proof load, loosening resistance degrades due to excessive plastic deformation.

---

### Dataset 4: Stress Distribution Comparison at Thread Root

**Von Mises stress at first engaged thread root (MPa)**

| Condition | After tightening | After 1 vibration cycle | After 20 cycles |
|---|---|---|---|
| Method A (F₀=50kN) | 720 | 780 | 850 |
| Method B (F₀=50kN) | 520 | 600 | 720 |

The ~200 MPa higher residual stress from tightening explains the faster loosening in Method A.

---

## Implications for FEA Modeling

### Recommendation
For accurate FEA prediction of self-loosening:
1. **Always simulate the tightening process** — do not use BOLT LOAD as initial condition
2. Model nut rotation from zero preload to target preload
3. Include elastic-plastic material behavior (kinematic hardening preferred)
4. Use ABAQUS/Explicit for better convergence with complex contact during tightening
5. Mesh thread roots with at least 4 elements across the root radius

### Computational Cost
| Method | Elements | Steps | Wall time (8 cores) |
|---|---|---|---|
| B (direct, 30 cycles) | 50,000 | 31 | ~4 hours |
| A (real, 30 cycles) | 50,000 | 32 | ~8 hours |

The tightening step approximately doubles the computation time but provides significantly more accurate results.

---

## Reproduction Parameters

| Parameter | Value | Units |
|---|---|---|
| Bolt | M12 × 1.75 | — |
| Class | 10.9 | — |
| E | 210,000 | MPa |
| ν | 0.3 | — |
| σ_y | 940 | MPa |
| σ_u | 1,040 | MPa |
| μ (all surfaces) | 0.15 | — |
| Preloads | 30 / 50 / 60 | kN |
| Displacement | 0.50 | mm |
| Cycles modeled | 30 | — |
| Solver | ABAQUS/Explicit | — |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this FEA study.
> NOTE: FEA study comparing real tightening vs. direct preload. Use f=1 Hz (quasi-static).

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
| Grip length | 25.0 | mm (estimated) |
| Helix angle | 2.93 | ° |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 | 210,000 | 940 | 1,040 | 0.3 |
| Plates | Steel | 210,000 | — | — | 0.3 |

### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 50,000 | N |
| % Yield | 63.1 | % |
| Transverse disp. δ | 0.50 | mm |
| Frequency | 1.0 | Hz (quasi-static) |
| Cycles | 30 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 |
| Lubricated | false |

### Preload Configurations

| Config | F₀ (kN) | % Proof | Notes |
|---|---|---|---|
| Medium | 30 | 52% | Faster loosening |
| High | 50 | 87% | Baseline |
| Over-proof | 60 | 104% | Slight yielding |

### ValidationCase (for validation_cases.py)

```python
ValidationCase(
    name="Chen_2017_M12_FEA",
    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,
    initial_preload_N=50000,
    preload_percent_yield=63.1,
    transverse_displacement_mm=0.50,
    frequency_Hz=1.0,
    n_cycles=30,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.48,
    expected_loosening_deg=5.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=1, preload_ratio=0.960),
        ExperimentalDataPoint(cycles=2, preload_ratio=0.930),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.860),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.760),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.600),
        ExperimentalDataPoint(cycles=30, preload_ratio=0.480),
    ]
)
```
