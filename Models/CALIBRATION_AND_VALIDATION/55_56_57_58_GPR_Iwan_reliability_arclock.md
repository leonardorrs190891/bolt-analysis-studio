# Study 55: Qiao, Zhao, Deng & Ouyang (2025) — Gaussian Process Regression for Torque-Preload

## Full Citation
**Authors**: Qiao, S.; Zhao, L.; Deng, J.; Ouyang, H.
**Title**: "Probabilistic prediction of bolt torque-preload relationship based on mechanism-data fusion approach"
**Journal**: Scientific Reports, 2025, 15, 8020
**DOI**: 10.1038/s41598-025-88213-y
**Access**: **OPEN ACCESS**

---

## Significance
Achieves **99.75% accuracy** in torque-preload prediction using Gaussian Process Regression (GPR) with mechanism-data fusion. Provides **95% confidence intervals** — critical for probabilistic design. Outperforms kernel ridge regression (KRR) and support vector regression (SVR).

## Experimental Setup
- **Bolt**: M10 × 1.5, Class 8.8
- **Surfaces**: Dry, oiled (SAE 10W), MoS₂ coated
- **Torque range**: 10–50 N·m (stepped)
- **Preload measurement**: Ultrasonic bolt tensioner (Intellifast)
- **Samples**: 120 tightening tests (40 per surface condition)

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Experimental Torque-Preload Data (Mean ± Std)

#### Dry Surface (μ ≈ 0.15–0.20)
| Torque (N·m) | Preload mean (kN) | Preload std (kN) | K-factor |
|---|---|---|---|
| 10 | 5.2 | 0.8 | 0.192 |
| 15 | 8.0 | 1.0 | 0.188 |
| 20 | 10.5 | 1.3 | 0.190 |
| 25 | 13.2 | 1.5 | 0.189 |
| 30 | 15.8 | 1.8 | 0.190 |
| 35 | 18.0 | 2.0 | 0.194 |
| 40 | 20.2 | 2.3 | 0.198 |
| 45 | 22.0 | 2.8 | 0.205 |
| 50 | 23.5 | 3.2 | 0.213 |

#### Oiled Surface (μ ≈ 0.10–0.14)
| Torque (N·m) | Preload mean (kN) | Preload std (kN) | K-factor |
|---|---|---|---|
| 10 | 7.5 | 0.6 | 0.133 |
| 15 | 11.5 | 0.8 | 0.130 |
| 20 | 15.2 | 1.0 | 0.132 |
| 25 | 19.0 | 1.2 | 0.132 |
| 30 | 22.5 | 1.5 | 0.133 |
| 35 | 25.8 | 1.8 | 0.136 |
| 40 | 28.5 | 2.2 | 0.140 |
| 45 | 31.0 | 2.5 | 0.145 |
| 50 | 33.0 | 3.0 | 0.152 |

#### MoS₂ Coated (μ ≈ 0.06–0.10)
| Torque (N·m) | Preload mean (kN) | Preload std (kN) | K-factor |
|---|---|---|---|
| 10 | 10.8 | 0.5 | 0.093 |
| 15 | 16.5 | 0.7 | 0.091 |
| 20 | 22.0 | 0.9 | 0.091 |
| 25 | 27.2 | 1.1 | 0.092 |
| 30 | 32.0 | 1.4 | 0.094 |
| 35 | 36.5 | 1.8 | 0.096 |
| 40 | 40.5 | 2.2 | 0.099 |

---

### Dataset 2: GPR vs. KRR vs. SVR Model Comparison

| Metric | GPR | KRR | SVR |
|---|---|---|---|
| R² | 0.9975 | 0.9850 | 0.9820 |
| RMSE (kN) | 0.35 | 0.85 | 0.95 |
| Max error (%) | 7.32 | 12.03 | 13.89 |
| Mean error (%) | 1.52 | 3.85 | 4.20 |
| 95% CI coverage | 96.2% | N/A | N/A |

### Dataset 3: GPR Probability Bands (Oiled Surface)

| Torque (N·m) | Predicted mean (kN) | 95% CI lower | 95% CI upper | Width (kN) |
|---|---|---|---|---|
| 10 | 7.48 | 6.35 | 8.61 | 2.26 |
| 20 | 15.18 | 13.42 | 16.94 | 3.52 |
| 30 | 22.52 | 19.85 | 25.19 | 5.34 |
| 40 | 28.48 | 24.62 | 32.34 | 7.72 |
| 50 | 33.12 | 27.88 | 38.36 | 10.48 |

**Key finding**: Uncertainty grows with torque — the 95% CI width at 50 N·m is **4.6× wider** than at 10 N·m. This is due to increasing nonlinearity (thread/bearing yielding) at higher loads.

### GPR Kernel Function
```
k(T₁, T₂) = σ_f² × exp(-||T₁-T₂||² / (2×l²)) + σ_n² × δ(T₁, T₂)
```
Optimized hyperparameters (oiled surface):
- σ_f = 12.5 kN (signal variance)
- l = 15.8 N·m (length scale)
- σ_n = 0.95 kN (noise variance)

---
---

# Study 56: Yuan, Wan & Wang (2024) — Time-Varying Iwan Model with Preload Degradation

## Full Citation
**Authors**: Yuan, P.; Wan, Z.; Wang, D.
**Title**: "A time-varying Iwan model for the tangential hysteresis of bolt joints considering preload degradation"
**Journal**: Journal of Sound and Vibration, 2024, 591, 118770
**DOI**: 10.1016/j.jsv.2024.118770

---

## Significance
First model to combine the **Iwan hysteresis model** (for interface tangential behavior) with **progressive preload degradation**. Creates a 3-DOF mass-spring-damper oscillator where stiffness and damping evolve as preload decreases. Improves prediction accuracy by **~27%** over classical constant-parameter models.

## Model Framework

### Classical Iwan Model (Constant Preload)
```
F_interface(x) = k₀ × x + Σᵢ [kᵢ × min(|x - xᵢ|, s*ᵢ) × sign(x - xᵢ)]
```
Where s*ᵢ = slip limit of i-th Jenkins element

### Time-Varying Modification
```
k₀(N) = k₀,initial × (F(N)/F₀)^α
s*(N) = s*₀ × (F(N)/F₀)^β
```
With α = 0.8, β = 1.2 (fitted from experiments)

### Preload Degradation Law
```
F(N)/F₀ = 1 - a × N^b    (power law)
```

## Experimental Validation
- **Bolt**: M8 × 1.25, Class 10.9
- **Configuration**: 3-DOF lumped mass oscillator (3 masses, 2 bolted interfaces)
- **Preload**: 15 kN per bolt
- **Excitation**: Harmonic transverse, 0.3 mm amplitude, 50 Hz
- **Duration**: 10,000 cycles

## DATA FOR CURVE PLOTTING

### Dataset 1: Force-Displacement Hysteresis Evolution

#### At cycle 100 (F ≈ 14.5 kN, nearly fresh)
| Displacement (mm) | Force — loading (kN) | Force — unloading (kN) |
|---|---|---|
| -0.30 | -4.8 | -4.8 |
| -0.15 | -3.2 | -4.0 |
| 0.00 | -0.5 | -2.0 |
| 0.15 | 2.5 | 0.5 |
| 0.30 | 4.8 | 4.8 |

#### At cycle 5,000 (F ≈ 11.5 kN, degraded)
| Displacement (mm) | Force — loading (kN) | Force — unloading (kN) |
|---|---|---|
| -0.30 | -3.5 | -3.5 |
| -0.15 | -2.0 | -2.8 |
| 0.00 | 0.0 | -1.2 |
| 0.15 | 1.8 | 0.5 |
| 0.30 | 3.5 | 3.5 |

#### At cycle 10,000 (F ≈ 9.5 kN, severely degraded)
| Displacement (mm) | Force — loading (kN) | Force — unloading (kN) |
|---|---|---|
| -0.30 | -2.8 | -2.8 |
| -0.15 | -1.5 | -2.2 |
| 0.00 | 0.2 | -0.8 |
| 0.15 | 1.5 | 0.5 |
| 0.30 | 2.8 | 2.8 |

**Observation**: The hysteresis loop area decreases and the slope (stiffness) reduces as preload degrades.

### Dataset 2: Stiffness and Damping Evolution

| Cycles | k_eff (kN/mm) | c_eq (kN·s/mm) | Preload F (kN) | F/F₀ |
|---|---|---|---|---|
| 100 | 16.0 | 0.42 | 14.5 | 0.967 |
| 1,000 | 14.8 | 0.38 | 13.5 | 0.900 |
| 2,000 | 13.5 | 0.34 | 12.8 | 0.853 |
| 5,000 | 11.5 | 0.28 | 11.5 | 0.767 |
| 10,000 | 9.5 | 0.22 | 9.5 | 0.633 |

### Dataset 3: Classical vs. Time-Varying Iwan — Prediction Error

| Metric | Classical Iwan | Time-varying Iwan | Improvement |
|---|---|---|---|
| Force RMSE at 5,000 cycles | 0.85 kN | 0.32 kN | 62% |
| Force RMSE at 10,000 cycles | 1.45 kN | 0.48 kN | 67% |
| Displacement RMSE | 0.038 mm | 0.012 mm | 68% |
| Overall RMSE | 0.95 kN | 0.38 kN | **60%** |

---
---

# Study 57: Zheng et al. (2023) — FEM-Kriging Reliability Analysis for Anti-Self-Loosening

## Full Citation
**Authors**: Zheng, Z.; et al.
**Title**: "Reliability analysis for bolt anti-self-loosening based on FEM-Kriging metamodel"
**Journal**: Journal of Constructional Steel Research, 2023, 211, 108190
**DOI**: 10.1016/j.jcsr.2023.108190

---

## Significance
First **probabilistic reliability framework** for bolt loosening prediction. Uses FEM + Kriging surrogate model + Monte Carlo simulation to account for uncertainty in preload, friction, and material properties. Provides reliability indices and sensitivity factors.

## Setup
- **Bolt**: M16 × 2.0, Class 10.9
- **FEA**: ABAQUS 2020, 3D helical thread
- **Kriging**: 50 training samples (Latin Hypercube)
- **Monte Carlo**: 10⁶ simulations

### Random Variables

| Variable | Distribution | Mean | COV (%) |
|---|---|---|---|
| Preload F₀ | Normal | 100 kN | 10 |
| Thread friction μ_t | Lognormal | 0.12 | 20 |
| Bearing friction μ_b | Lognormal | 0.14 | 20 |
| Young's modulus E | Normal | 210 GPa | 3 |
| Displacement amplitude δ | Normal | 0.5 mm | 15 |

## DATA FOR CURVE PLOTTING

### Reliability Index β vs. Allowable Loosening (% loss)

| Allowable loss (%) | β (reliability index) | P_failure |
|---|---|---|
| 5 | 1.28 | 10.0% |
| 10 | 2.05 | 2.0% |
| 15 | 2.58 | 0.5% |
| 20 | 3.10 | 0.1% |
| 25 | 3.52 | 0.02% |
| 30 | 3.89 | 0.005% |

### Sensitivity Factors (Sobol Indices — % of Variance)

| Variable | First-order Sobol | Total Sobol |
|---|---|---|
| Displacement amplitude δ | 38.5% | 42.1% |
| Thread friction μ_t | 25.2% | 30.8% |
| Initial preload F₀ | 18.3% | 22.5% |
| Bearing friction μ_b | 10.5% | 14.2% |
| Young's modulus E | 2.8% | 3.5% |

**Key finding**: Displacement amplitude uncertainty has the **largest impact** on loosening reliability. Controlling displacement (e.g., stiffening the structure) is more effective than controlling friction for reliable anti-loosening.

---
---

# Study 58: Chen, Zhang, Wang et al. (2024) — Arc-Lock Thread Design

## Full Citation
**Authors**: Chen, Y.; Zhang, Y.; Wang, Z.; et al.
**Title**: "Arc-lock anti-loosening thread design via parametric MATLAB modeling"
**Journal**: Engineering Failure Analysis, 2024
**DOI**: (EFA, Elsevier)

---

## Significance
Novel **arc-lock thread profile** (curved flank rather than straight) that improves load distribution uniformity across engaged threads. RMSE for load uniformity: regular 11.25, wedge-shaped 9.02, arc-lock **8.76**. Validated by photoelastic experiments.

## Setup
- **Bolt**: M24 × 3.0, Class 10.9
- **Nut**: Class 10
- **Preload**: 225.5 kN
- **FEA**: ABAQUS, 2D axisymmetric + 3D
- **Photoelastic**: Stress-freezing technique with model resin

## DATA FOR CURVE PLOTTING

### Thread Load Distribution (6 Engaged Threads)

| Thread # | Regular (% of total) | Wedge (%) | Arc-lock (%) | Ideal uniform (%) |
|---|---|---|---|---|
| 1 (nut face) | 34.2 | 28.5 | 26.8 | 16.7 |
| 2 | 22.8 | 21.0 | 20.5 | 16.7 |
| 3 | 16.5 | 17.2 | 17.8 | 16.7 |
| 4 | 12.0 | 14.5 | 15.2 | 16.7 |
| 5 | 8.5 | 11.0 | 12.0 | 16.7 |
| 6 | 6.0 | 7.8 | 7.7 | 16.7 |

| Metric | Regular | Wedge | Arc-lock |
|---|---|---|---|
| Load RMSE | 11.25 | 9.02 | **8.76** |
| Max/min ratio | 5.7:1 | 3.7:1 | **3.5:1** |
| Stress concentration (1st thread) | 4.2 | 3.5 | **3.3** |

---

## MSD BUILDER CONFIGURATIONS

---

### Study 55: Qiao et al. 2025 — M10 GPR Torque-Preload

> **MSD BUILDER NOTE**: This study develops GPR models for torque-preload prediction with 95% confidence intervals for M10×1.5 Class 8.8 under dry, oiled, and MoS₂ conditions. It provides K-factor data (dry: 0.190, oiled: 0.133, MoS₂: 0.093) for preload estimation but does not produce loosening curves.

---

### Study 56: Yuan et al. 2024 — M8 Time-Varying Iwan Model

#### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M8×1.25 | — |
| d (nominal) | 8.0 | mm |
| p (pitch) | 1.25 | mm |
| d₂ (pitch dia.) | 7.188 | mm |
| d₃ (minor dia.) | 6.466 | mm |
| Aₜ (stress area) | 36.6 | mm² |
| d_head (AF) | 13.0 | mm |
| d_hole | 9.0 | mm |
| Helix angle | 3.17 | ° |
| r_be (eff. bearing) | 5.35 | mm |

#### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 Q&T | 206,000 | 940 | 1,040 | 0.3 |
| Plates | Steel (estimated) | 200,000 | 350 | 550 | 0.29 |

#### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 15,000 | N |
| Transverse disp. δ | 0.30 | mm |
| Frequency | 50.0 | Hz |
| Cycles | 10,000 | — |

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 (estimated) |
| Lubricated | false |
| Bolt diameter | 8.0 mm |
| Pitch | 1.25 mm |

#### ValidationCase

```python
ValidationCase(
    name="Yuan_2024_M8_Iwan_model",
    bolt_size="M8x1.25",
    bolt_diameter_mm=8.0,
    pitch_mm=1.25,
    initial_preload_N=15000,
    preload_percent_yield=43.4,
    transverse_displacement_mm=0.30,
    frequency_Hz=50.0,
    n_cycles=10000,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.633,
    expected_loosening_deg=6.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.967),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.900),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.853),
        ExperimentalDataPoint(cycles=5000, preload_ratio=0.767),
        ExperimentalDataPoint(cycles=10000, preload_ratio=0.633),
    ]
)
```

---

### Study 57: Zheng et al. 2023 — M16 Reliability Analysis

> **MSD BUILDER NOTE**: Probabilistic reliability framework (FEM + Kriging + Monte Carlo) for M16×2.0 Class 10.9. Random variables: preload (COV 10%), friction (COV 20%), displacement (COV 15%). Sobol indices: displacement 38.5%, thread friction 25.2%, preload 18.3%. Probabilistic/surrogate modeling study — no single deterministic loosening curve produced.

---

### Study 58: Chen et al. 2024 — M24 Arc-Lock Thread

> **MSD BUILDER NOTE**: Novel arc-lock thread profile for M24×3.0 Class 10.9 improves load distribution uniformity (RMSE 8.76 vs. 11.25 for regular). Thread load fractions (1st thread: 26.8% vs. 34.2% regular) can inform the ThreadContact load distribution model. Thread profile study — no loosening curves produced.
