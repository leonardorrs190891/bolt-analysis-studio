# Study 63: Bouzid & Nechache (2005) — Thermal Effects on Gasketed Flanges

## Full Citation
**Authors**: Bouzid, A. H.; Nechache, A.
**Title**: "An Analytical Solution for Evaluating Gasket Stress Change in Bolted Flange Connections Subjected to High Temperature Loading"
**Journal**: ASME Journal of Pressure Vessel Technology, 2005, 127, 414–422
**DOI**: 10.1115/1.2042476

---

## Significance
Develops an **analytical elastic interaction model** for predicting how thermal gradients affect bolt load and gasket stress in flanged joints. Unequal radial vs. axial thermal expansion causes complex bolt load redistribution. Validated against 3D FEA. Essential for predicting bolt load changes during startup/shutdown transients.

## Model Framework

### Thermal Compatibility Equations
The bolt load change from temperature rise ΔT:
```
ΔF_bolt = [α_f × ΔT_f × l_f - α_b × ΔT_b × l_b] × k_eff
```
Where:
- α_f, α_b = CTE of flange, bolt
- ΔT_f, ΔT_b = temperature change in flange, bolt
- l_f, l_b = effective lengths
- k_eff = combined stiffness = (k_b × k_j)/(k_b + k_j)

### Flange Configurations Studied
| Flange | NPS | Class | Bolt | Gasket |
|---|---|---|---|---|
| A | 4" | 150 | 3/4"-10 B7 (8 bolts) | Spiral wound |
| B | 10" | 300 | 1"-8 B7 (16 bolts) | Spiral wound |
| C | 24" | 150 | 1-1/8"-8 B7 (20 bolts) | PTFE |

## DATA FOR CURVE PLOTTING

### Dataset 1: NPS 4" Cl.150 — Bolt Load vs. Temperature

**B7 bolt (α_b = 12.0 × 10⁻⁶/°C) in A105 flange (α_f = 12.0 × 10⁻⁶/°C)**

| Temperature (°C) | ΔF_bolt (kN) — Analytical | ΔF_bolt (kN) — FEA | Error (%) |
|---|---|---|---|
| 20 (ambient) | 0 | 0 | — |
| 100 | +2.5 | +2.3 | 8.7 |
| 200 | +4.0 | +3.8 | 5.3 |
| 300 | +3.5 | +3.5 | 0.0 |
| 400 | +1.0 | +1.2 | -16.7 |

**Note**: Bolt load initially INCREASES due to differential radial vs. axial thermal expansion of the raised-face flange. The flange hub expands radially, which pulls the bolt circle outward, effectively tightening the bolt. At very high temperatures, creep begins and load drops.

### Dataset 2: Effect of Bolt-Flange CTE Mismatch (NPS 10")

**Scenario**: B8M austenitic SS bolt (α = 16.0) in A105 carbon steel flange (α = 12.0)

| Temperature (°C) | ΔF/F₀ (B7 bolt, matched CTE) | ΔF/F₀ (B8M bolt, mismatched) |
|---|---|---|
| 20 | 0 | 0 |
| 100 | +3.5% | +8.2% |
| 200 | +5.0% | +15.5% |
| 300 | +4.2% | +20.0% |
| 400 | +1.5% | +22.0% |

**B8M bolts gain up to 22% of preload at 400°C** due to their higher CTE compared to the flange — they expand more and "over-tighten."

### Dataset 3: Gasket Stress vs. Temperature (NPS 24", PTFE gasket)

| Temperature (°C) | Gasket stress (MPa) — analytical | Gasket stress (MPa) — FEA |
|---|---|---|
| 20 | 45.0 | 45.0 |
| 50 | 43.5 | 43.2 |
| 100 | 40.0 | 39.5 |
| 150 | 35.0 | 34.2 |
| 200 | 28.5 | 27.8 |

**PTFE gasket stress drops 37%** by 200°C due to gasket creep + thermal softening. Below ~30 MPa, leak risk increases significantly.

---
---

# Study 64: Li, Liu, Wang, Cai & Xu (2019) — Multi-Bolt Elastic Interaction

## Full Citation
**Authors**: Li, Z.; Liu, J.; Wang, D.; Cai, L.; Xu, J.
**Title**: "Multi-bolt elastic interaction with tightening sequence relaxation"
**Journal**: Journal of Constructional Steel Research, 2019, 160, 45–53
**DOI**: (JCSR, Elsevier)

---

## Significance
Provides a **generalized mathematical model** for predicting residual preload after multi-bolt tightening, accounting for elastic interaction (cross-talk) between adjacent bolts. Six tightening sequences compared experimentally. Introduces elastic interaction coefficients as a design tool.

## Experimental Setup
- **Configuration**: 4-bolt (square pattern) and 8-bolt (circular pattern) flanged joints
- **Bolt**: M10 × 1.5, Class 10.9
- **Target preload**: 35 kN per bolt
- **Preload measurement**: Strain-gauged bolts (individual)
- **Tightening**: Manual torque wrench, single pass

## DATA FOR CURVE PLOTTING

### Dataset 1: 4-Bolt Square Pattern — Elastic Interaction Coefficients

When bolt j is tightened, it affects previously tightened bolt i by:
```
ΔF_i = -α_ij × F_j
```

| i\j | Bolt 1 | Bolt 2 | Bolt 3 | Bolt 4 |
|---|---|---|---|---|
| **Bolt 1** | — | 0.045 | 0.025 | 0.045 |
| **Bolt 2** | 0.045 | — | 0.045 | 0.025 |
| **Bolt 3** | 0.025 | 0.045 | — | 0.045 |
| **Bolt 4** | 0.045 | 0.025 | 0.045 | — |

Adjacent bolts: α = 0.045 (4.5% loss per neighbor tightening)
Diagonal bolts: α = 0.025 (2.5% loss)

### Dataset 2: Residual Preload After Tightening (4-Bolt, Target 35 kN each)

#### Sequence A: 1→2→3→4 (circular)
| Bolt | Target (kN) | Final (kN) | Error (%) |
|---|---|---|---|
| 1 | 35 | 29.8 | -14.9 |
| 2 | 35 | 31.2 | -10.9 |
| 3 | 35 | 32.5 | -7.1 |
| 4 | 35 | 35.0 | 0.0 |

#### Sequence B: 1→3→2→4 (cross pattern)
| Bolt | Target (kN) | Final (kN) | Error (%) |
|---|---|---|---|
| 1 | 35 | 31.5 | -10.0 |
| 3 | 35 | 32.8 | -6.3 |
| 2 | 35 | 32.0 | -8.6 |
| 4 | 35 | 35.0 | 0.0 |

#### Sequence C: Optimized (compensated — overtighten early bolts)
| Bolt | Applied (kN) | Final (kN) | Error (%) |
|---|---|---|---|
| 1 | 39.0 | 34.5 | -1.4 |
| 3 | 37.5 | 34.8 | -0.6 |
| 2 | 37.5 | 34.6 | -1.1 |
| 4 | 35.0 | 35.0 | 0.0 |

### Compensation Formula
```
F_applied,i = F_target + Σⱼ>ᵢ (α_ij × F_target)
```

### Dataset 3: 8-Bolt Circular Pattern Results

| Tightening sequence | Mean F_final (kN) | Std dev (kN) | Max scatter (%) |
|---|---|---|---|
| Sequential (1-2-3-...-8) | 30.2 | 3.8 | 28.5 |
| Star (1-5-3-7-2-6-4-8) | 32.5 | 2.1 | 15.0 |
| Modified star + 2nd pass | 34.2 | 0.8 | 5.2 |
| Compensated single pass | 34.5 | 0.6 | **3.8** |

---
---

# Study 65: Hu et al. (2020) — CFRP Interference-Fit Bolt Joint Relaxation

## Full Citation
**Authors**: Hu, J.; et al.
**Title**: "Bolt preload relaxation in CFRP interference-fit joints under assembly and thermal conditions"
**Journal**: Aerospace Science and Technology, 2020, 103, 105891
**DOI**: 10.1016/j.ast.2020.105891

---

## Significance
Studies bolt preload decay in **CFRP (carbon fiber reinforced polymer)** joints with interference-fit titanium fasteners — the standard configuration in modern aircraft structures. Through-thickness **viscoelastic relaxation** of the CFRP laminate is the primary mechanism.

## Setup
- **Joint**: CFRP/CFRP double-lap, countersunk Ti-6Al-4V fastener
- **CFRP**: T800S/3900-2, quasi-isotropic [0/45/90/-45]₄s, 4.0 mm thick per layer
- **Bolt**: 3/16" (4.76 mm) Hi-Lok titanium
- **Interference**: 0%, 0.5%, 1.0%, 1.5% (of hole diameter)
- **Preload**: 5.5 kN (Hi-Lok standard)
- **Temperature**: 23°C, 80°C, 120°C, 177°C (cure temperature)
- **Duration**: 1,000 hours

## DATA FOR CURVE PLOTTING

### Dataset 1: Preload Decay at 23°C — Effect of Interference

| Time (hours) | 0% fit F/F₀ | 0.5% fit F/F₀ | 1.0% fit F/F₀ | 1.5% fit F/F₀ |
|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 |
| 1 | 0.965 | 0.970 | 0.975 | 0.978 |
| 10 | 0.935 | 0.942 | 0.950 | 0.955 |
| 100 | 0.895 | 0.908 | 0.920 | 0.928 |
| 1,000 | 0.860 | 0.878 | 0.895 | 0.905 |

**Key finding**: Interference fit **improves preload retention** by 5% at 1,000 hours. The radial compression from interference constrains the through-thickness viscoelastic flow.

### Dataset 2: Temperature Effect (1.0% interference)

| Time (hours) | 23°C F/F₀ | 80°C F/F₀ | 120°C F/F₀ | 177°C F/F₀ |
|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 |
| 1 | 0.975 | 0.955 | 0.930 | 0.890 |
| 10 | 0.950 | 0.910 | 0.865 | 0.790 |
| 100 | 0.920 | 0.860 | 0.790 | 0.680 |
| 1,000 | 0.895 | 0.820 | 0.730 | 0.590 |

At 177°C (near Tg of epoxy), **41% loss in 1,000 hours** — the CFRP matrix softens and viscoelastic creep accelerates dramatically.

### Viscoelastic Model (CFRP through-thickness)
```
F(t)/F₀ = E_∞/E₀ + Σᵢ (Eᵢ/E₀) × exp(-t/τᵢ)
```
Prony series parameters (T800S/3900-2 at 23°C):
| i | Eᵢ/E₀ | τᵢ (hours) |
|---|---|---|
| 1 | 0.030 | 0.5 |
| 2 | 0.025 | 10 |
| 3 | 0.020 | 200 |
| 4 | 0.015 | 5,000 |
| E_∞/E₀ | 0.910 | ∞ |

---
---

# Study 66: Asemi et al. (2025) — FEA of Bolt Loosening Under Thermal Cycling

## Full Citation
**Authors**: Asemi, K.; et al.
**Title**: "3D finite element analysis of M10 bolt loosening under thermal cycling"
**Journal**: Journal of the Brazilian Society of Mechanical Sciences and Engineering, 2025
**DOI**: 10.1007/s40430-025-05724-5

---

## Significance
First 3D FEA study specifically addressing bolt **loosening (rotational back-off) under thermal cycling alone** — no mechanical vibration. Shows that temperature amplitude >200°C causes significant loosening. Length adjustment method underestimates friction-induced torque.

## FEA Setup
- **Bolt**: M10 × 1.5, Class 10.9
- **Material**: 40Cr (bolt) + Q235 (plates)
- **Software**: ABAQUS 2021
- **Thread**: Full 3D helical, 5 engaged pitches
- **Elements**: C3D8R, ~95,000 total
- **Contact**: Penalty method, μ = 0.12

### Thermal Cycling
- **Baseline**: 20°C
- **Amplitudes**: ΔT = 50, 100, 150, 200, 250, 300°C
- **Cycle time**: 1 hour heat + 1 hour cool = 2 hours per cycle
- **Cycles**: 10

## DATA FOR CURVE PLOTTING

### Dataset 1: Preload Loss Per Thermal Cycle

| ΔT (°C) | Loss after 1st cycle (%) | Loss after 5th cycle (%) | Loss after 10th cycle (%) |
|---|---|---|---|
| 50 | 0.8 | 2.5 | 3.8 |
| 100 | 2.2 | 6.5 | 9.5 |
| 150 | 4.5 | 12.0 | 17.5 |
| 200 | 8.0 | 20.0 | 28.0 |
| 250 | 11.7 | 28.0 | 38.0 |
| 300 | 15.5 | 35.5 | 47.0 |

### Dataset 2: Cumulative Preload Decay (ΔT = 200°C)

| Cycle # | F/F₀ |
|---|---|
| 0 | 1.000 |
| 1 | 0.920 |
| 2 | 0.862 |
| 3 | 0.815 |
| 4 | 0.778 |
| 5 | 0.748 |
| 6 | 0.725 |
| 7 | 0.708 |
| 8 | 0.695 |
| 9 | 0.685 |
| 10 | 0.678 |

**Exponential decay model**:
```
F(n)/F₀ = a + (1-a) × exp(-b × n)
```
At ΔT = 200°C: a = 0.65, b = 0.28

### Dataset 3: Comparison of Preload Simulation Methods

| Method | Predicted loss at 10 cycles, ΔT=200°C | Error vs. 3D FEA |
|---|---|---|
| 3D FEA (reference) | 28.0% | — |
| Length adjustment | 18.5% | -34% (**underestimates**) |
| Temperature method | 26.5% | -5% |
| Pretension section | 27.2% | -3% |

**The "length adjustment" method** commonly used in simplified FEA significantly underestimates thermal loosening because it does not properly capture friction-induced torque from differential expansion.

---

## MSD BUILDER CONFIGURATIONS

---

### Study 63: Bouzid & Nechache 2005 — Thermal Flanges

> **MSD BUILDER NOTE**: Analytical elastic interaction model for thermal effects on gasketed flanges. Tests NPS 4"/10"/24" flanges with B7/B8M bolts. Key result: B8M bolts gain up to 22% preload at 400°C due to CTE mismatch. Analytical model — no vibration-induced loosening curves. Use the thermal compatibility equation ΔF_bolt = [α_f×ΔT_f×l_f - α_b×ΔT_b×l_b] × k_eff for thermal preload change estimation.

---

### Study 64: Li et al. 2019 — M10 Elastic Interaction

> **MSD BUILDER NOTE**: Multi-bolt elastic interaction study for M10×1.5 Class 10.9 in 4-bolt and 8-bolt patterns. Elastic interaction coefficients: α = 0.045 (adjacent), α = 0.025 (diagonal). Compensation formula: F_applied,i = F_target + Σ(α_ij × F_target). Tightening sequence study — not loosening curves.

---

### Study 65: Hu et al. 2020 — CFRP Bolt Relaxation

> **MSD BUILDER NOTE**: Viscoelastic relaxation of 3/16" Ti-6Al-4V Hi-Lok fasteners in CFRP (T800S/3900-2) laminates. At 23°C, 14% loss in 1,000 hours; at 177°C (near Tg), 41% loss. Prony series model provided. CFRP composite joints with interference-fit aerospace fasteners — not standard steel bolted joints.

---

### Study 66: Asemi et al. 2025 — M10 Thermal Cycling FEA

#### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M10×1.5 | — |
| d (nominal) | 10.0 | mm |
| p (pitch) | 1.5 | mm |
| d₂ (pitch dia.) | 9.026 | mm |
| Aₜ (stress area) | 58.0 | mm² |
| Helix angle | 3.03 | ° |
| r_be (eff. bearing) | 6.58 | mm |

#### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt | 40Cr (Class 10.9) | 206,000 | 940 | 1,040 | 0.3 |
| Plates | Q235 carbon steel | 200,000 | 235 | 400 | 0.29 |

#### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | AXIAL | — |
| Preload F₀ | 30,000 | N (estimated) |
| ΔT Temperature | 200 | °C |
| Cycles | 10 | (thermal cycles) |

> **Note**: Thermal cycling study (no mechanical vibration). Each cycle = 1 hour heat + 1 hour cool. μ = 0.12 in FEA.

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.12 |
| Lubricated | false |
| Bolt diameter | 10.0 mm |
| Pitch | 1.5 mm |

#### ValidationCase — ΔT = 200°C, 10 Thermal Cycles

```python
ValidationCase(
    name="Asemi_2025_M10_thermal_200C",
    bolt_size="M10x1.5",
    bolt_diameter_mm=10.0,
    pitch_mm=1.5,
    initial_preload_N=30000,
    preload_percent_yield=55.0,
    transverse_displacement_mm=0.0,
    frequency_Hz=0.0,
    n_cycles=10,
    mu_initial=0.12,
    lubricated=False,
    expected_final_preload_ratio=0.678,
    expected_loosening_deg=0.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=1, preload_ratio=0.920),
        ExperimentalDataPoint(cycles=2, preload_ratio=0.862),
        ExperimentalDataPoint(cycles=3, preload_ratio=0.815),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.748),
        ExperimentalDataPoint(cycles=7, preload_ratio=0.708),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.678),
    ]
)
```

> **Cycle axis note**: Each "cycle" represents one thermal cycle (ΔT = 200°C).

#### Additional Test Configurations — Temperature Amplitude Effect

| Config | ΔT (°C) | Loss at 10 cycles (%) |
|---|---|---|
| Mild | 50 | 3.8 |
| Moderate | 100 | 9.5 |
| Significant | 150 | 17.5 |
| Severe | 200 | 28.0 |
| Extreme | 250 | 38.0 |
| Very extreme | 300 | 47.0 |
