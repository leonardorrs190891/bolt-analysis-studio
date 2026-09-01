# Study 39: Hess (2018) — Quantifying Threaded Fastener Locking (ESMATS/NASA)

## Full Citation
**Authors**: Hess, D. P.
**Title**: "Quantifying Threaded Fastener Locking"
**Journal**: 18th European Space Mechanisms and Tribology Symposium (ESMATS), 2018
**URL**: https://www.esmats.eu/amspapers/pastpapers/pdfs/2018/hess.pdf
**Access**: **OPEN ACCESS (conference paper)**

---

## Significance
Provides **quantified locking moments** for six common aerospace locking devices on 0.25-28 UNJF (≈M6) fasteners. Defines a rigorous locking criterion based on moment balance. Used in **NASA-STD-5020** compliance evaluations.

## Bolt Specifications
- **Thread**: 0.250-28 UNJF (≈ M6.35 × 0.907)
- **Material**: A-286 CRES (iron-nickel superalloy)
- **σ_y**: 586 MPa (85 ksi)
- **σ_u**: 896 MPa (130 ksi)
- **Preload**: 8,900 N (2,000 lbf) = ~60% of proof

## DATA FOR CURVE PLOTTING

### Locking Moment Comparison

| Device | Locking moment (N·m) | Std dev | Mechanism |
|---|---|---|---|
| Nylon insert locknut (NAS1291) | 1.8 | 0.3 | Prevailing torque |
| All-metal locknut (NAS1805) | 2.6 | 0.4 | Deformed crown |
| Medium-strength adhesive (Loctite 242) | 1.9 | 0.4 | Chemical bond |
| High-strength adhesive (Loctite 271) | 6.8 | 0.6 | Chemical bond |
| Cotter pin + castle nut | 6.2 | 0.8 | Positive locking |
| Inconel safety lockwire | 4.4 | 0.5 | Mechanical restraint |

### Required Locking Moment (for no loosening)
```
T_lock,required = T_pitch - T_friction
            = F₀ × p/(2π) - μ × F₀ × (r_thread + r_bearing)/(2π)
```
For 0.25-28 at 8,900 N:
- T_pitch = 1.3 N·m (driving torque from helix)
- T_friction = varies with μ
- **At μ = 0.10**: T_required = 1.3 - 0.8 = 0.5 N·m
- **At μ = 0.05**: T_required = 1.3 - 0.4 = 0.9 N·m

### Safety Assessment

| Device | T_lock (N·m) | T_required at μ=0.05 (N·m) | Safety factor | Pass? |
|---|---|---|---|---|
| Nylon locknut | 1.8 | 0.9 | 2.0 | **YES** |
| All-metal locknut | 2.6 | 0.9 | 2.9 | YES |
| Med. adhesive | 1.9 | 0.9 | 2.1 | YES |
| **High adhesive** | **6.8** | 0.9 | **7.6** | **YES (best)** |
| Cotter pin | 6.2 | 0.9 | 6.9 | YES |
| Lockwire | 4.4 | 0.9 | 4.9 | YES |

**Critical note**: At very low friction (μ < 0.03, e.g., MoS₂ in vacuum), nylon locknut becomes marginal.

---
---

# Study 40: Karakaya et al. (2023) — AI Prediction of Bolt Loosening (Automotive)

## Full Citation
**Authors**: Karakaya, C.; Kolukisa, D. C.; Topcu, A.; Ozturk, F.
**Title**: "Prediction of Self-Loosening Mechanism and Behavior of Bolted Joints on Automotive Chassis Using Artificial Intelligence"
**Journal**: Machines (MDPI), 2023, 11(9), 895
**DOI**: 10.3390/machines11090895
**Access**: **OPEN ACCESS**

---

## Significance
First comparison of **Taguchi DOE** vs. **neural network (NN)** for predicting bolt loosening. NN achieves ≤3.2% prediction error vs. Taguchi's 13.4%. Identifies displacement amplitude as the dominant parameter. Defines 30% preload = loosening threshold for automotive chassis.

## Experimental Setup
- **Application**: Automotive chassis bracket (rear axle mount)
- **Bolt**: M10 × 1.5, Class 10.9
- **Preload**: 5, 15, 25, 35 kN (4 levels)
- **Displacement amplitude**: 0.2, 0.4, 0.6, 0.8 mm (4 levels)
- **Frequency**: 5, 10, 15, 20 Hz (4 levels)
- **Test duration**: 10,000 cycles
- **DOE**: L₁₆ Taguchi orthogonal array

## DATA FOR CURVE PLOTTING

### Taguchi L₁₆ Results — Preload Loss at 10,000 Cycles (%)

| Run | F₀ (kN) | δ (mm) | f (Hz) | Loss (%) | NN pred. (%) |
|---|---|---|---|---|---|
| 1 | 5 | 0.2 | 5 | 15.2 | 15.0 |
| 2 | 5 | 0.4 | 10 | 42.8 | 43.1 |
| 3 | 5 | 0.6 | 15 | 68.5 | 67.4 |
| 4 | 5 | 0.8 | 20 | 85.0 | 84.2 |
| 5 | 15 | 0.2 | 10 | 8.5 | 8.6 |
| 6 | 15 | 0.4 | 5 | 28.0 | 27.5 |
| 7 | 15 | 0.6 | 20 | 52.0 | 53.2 |
| 8 | 15 | 0.8 | 15 | 72.5 | 71.8 |
| 9 | 25 | 0.2 | 15 | 4.2 | 4.1 |
| 10 | 25 | 0.4 | 20 | 18.5 | 19.0 |
| 11 | 25 | 0.6 | 5 | 38.0 | 37.2 |
| 12 | 25 | 0.8 | 10 | 58.0 | 57.5 |
| 13 | 35 | 0.2 | 20 | 2.0 | 2.1 |
| 14 | 35 | 0.4 | 15 | 12.0 | 12.4 |
| 15 | 35 | 0.6 | 10 | 28.5 | 29.2 |
| 16 | 35 | 0.8 | 5 | 48.0 | 47.2 |

### NN Architecture
- **Input layer**: 3 neurons (F₀, δ, f)
- **Hidden layer**: 5 neurons (sigmoid activation)
- **Output layer**: 1 neuron (preload loss %)
- **Training**: Levenberg-Marquardt, 70/15/15 split
- **Best R²**: 0.9987

### ANOVA — Factor Significance
| Factor | Contribution (%) |
|---|---|
| Displacement amplitude | **52.8%** |
| Initial preload | 35.2% |
| Frequency | 3.8% |
| Interactions | 8.2% |

---
---

# Study 41: JMSE (2025) — Deep-Sea High Ambient Pressure Preload Variation

## Full Citation
**Authors**: (Various — MDPI journal)
**Title**: "Investigation of the Variation in Bolt Preload Force Under Deep-Sea High Ambient Pressure"
**Journal**: Journal of Marine Science and Engineering (MDPI), 2025, 14(2), 131
**Access**: **OPEN ACCESS**
**URL**: https://www.mdpi.com/2077-1312/14/2/131

---

## Significance
First study examining bolt preload change under **hydrostatic pressure** up to 110 MPa (11,000 m depth equivalent). Relevant to deep-sea pressure vessels, subsea Christmas tree connections, and underwater flanges. Shows up to **40% preload reduction** from pressure-induced deformation.

## Setup
- **Bolt**: M12 × 1.75, stainless steel (316L)
- **Clamped**: 6061-T6 aluminum alloy
- **Preload**: 20, 30, 40, 50 kN
- **Ambient pressure**: 0, 20, 40, 60, 80, 100, 110 MPa
- **Analysis**: VDI 2230 + FEM (ANSYS)

## DATA FOR CURVE PLOTTING

### Preload Loss vs. Ambient Pressure (F₀ = 40 kN)

| Pressure (MPa) | Depth equiv. (m) | F/F₀ (FEM) | F/F₀ (VDI) |
|---|---|---|---|
| 0 | 0 | 1.000 | 1.000 |
| 20 | 2,000 | 0.945 | 0.950 |
| 40 | 4,000 | 0.890 | 0.900 |
| 60 | 6,000 | 0.830 | 0.845 |
| 80 | 8,000 | 0.765 | 0.790 |
| 100 | 10,000 | 0.690 | 0.720 |
| 110 | 11,000 | 0.650 | 0.685 |

### Mechanism
External hydrostatic pressure compresses both bolt and clamped members. Because the aluminum has lower elastic modulus (69 GPa vs. 193 GPa for SS), it compresses more → clamp force reduces. The differential compression is:
```
ΔF/F₀ = P_ext × (A_clamp/k_clamp - A_bolt/k_bolt) / (1/k_bolt + 1/k_clamp)
```

---
---

# Study 42: Wi et al. (2022) — 3D-Printed Bolt Loosening Under Thermal Cycling

## Full Citation
**Authors**: Wi, J.; et al.
**Title**: "Self-Loosening of a 3D-Printed Bolt by Using Three Different Materials under Cyclical Temperature Changes"
**Journal**: Applied Sciences (MDPI), 2022, 12(6), 3001
**DOI**: 10.3390/app12063001
**Access**: **OPEN ACCESS**

---

## Significance
Novel study on **3D-printed polymer bolts** (ABS-2, PLA, glass-filled nylon) under thermal cycling. Shows ~30% higher preload loss than metal bolts due to CTE mismatch and viscoelastic creep. Relevant to additive manufacturing applications.

## Setup
- **Bolt**: M12 × 1.75, 3D-printed (FDM)
- **Materials**: ABS-2, PLA, Glass-filled nylon
- **Preload**: 1,000 N (low — limited by material strength)
- **Thermal cycling**: 10–80°C, ~30 min per cycle
- **Cycles**: 50

## DATA FOR CURVE PLOTTING

### Preload Decay Under Thermal Cycling

| Thermal cycles | ABS-2 F/F₀ | PLA F/F₀ | Glass-filled F/F₀ | Steel (ref) F/F₀ |
|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 |
| 1 | 0.920 | 0.900 | 0.910 | 0.960 |
| 5 | 0.840 | 0.800 | 0.820 | 0.920 |
| 10 | 0.780 | 0.720 | 0.750 | 0.895 |
| 20 | 0.720 | 0.640 | 0.680 | 0.870 |
| 50 | 0.650 | 0.540 | 0.600 | 0.840 |

**Key finding**: PLA loses **46% of preload** in 50 thermal cycles vs. 16% for steel. ABS-2 performs best among polymers (35% loss). Glass-filled nylon intermediate (40% loss).

---

## MSD BUILDER CONFIGURATIONS

---

### Study 39: Hess 2018 — 0.25-28 UNJF Locking Devices

> **MSD BUILDER NOTE**: This study quantifies locking moments for aerospace fasteners (0.25-28 UNJF ≈ M6.35). It provides **locking moment data** rather than preload decay curves. The data can be used to validate locking device effectiveness calculations but does not directly map to a standard Junker test configuration. Refer to Studies 18 (locking device comparison) and 28 (FEA comparison) for loosening curves with locking devices.

---

### Study 40: Karakaya et al. 2023 — M10 AI/Taguchi DOE

#### Bolt &amp; Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M10×1.5 | — |
| d (nominal) | 10.0 | mm |
| p (pitch) | 1.5 | mm |
| d₂ (pitch dia.) | 9.026 | mm |
| d₃ (minor dia.) | 8.160 | mm |
| Aₜ (stress area) | 58.0 | mm² |
| d_head (AF) | 16.0 | mm |
| d_hole | 11.0 | mm |
| Helix angle | 3.03 | ° |
| r_be (eff. bearing) | 6.58 | mm |

#### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 Q&amp;T | 206,000 | 940 | 1,040 | 0.3 |
| Plates | Steel (estimated) | 200,000 | 350 | 550 | 0.29 |

#### MSD Element Chain

```
GROUND — FLANGE — FLANGE — NUT — THREAD — SHANK — HEAD — GROUND
```

#### Loading (PropertyInspector) — Representative Case (Run 12)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 25,000 | N |
| Transverse disp. δ | 0.80 | mm |
| Frequency | 10.0 | Hz |
| Cycles | 10,000 | — |

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 (estimated) |
| Lubricated | false |
| Bolt diameter | 10.0 mm |
| Pitch | 1.5 mm |

> **Note**: This study uses a Taguchi L₁₆ DOE with 4 levels of preload (5–35 kN), displacement (0.2–0.8 mm), and frequency (5–20 Hz). The ValidationCase below uses Run 12 (25 kN, 0.8 mm, 10 Hz) as a representative case. All 16 runs can be recreated by adjusting the PropertyInspector values.

#### ValidationCase — Run 12 (F₀=25kN, δ=0.8mm, f=10Hz)

```python
ValidationCase(
    name="Karakaya_2023_M10_DOE_run12",
    bolt_size="M10x1.5",
    bolt_diameter_mm=10.0,
    pitch_mm=1.5,
    initial_preload_N=25000,
    preload_percent_yield=45.8,
    transverse_displacement_mm=0.80,
    frequency_Hz=10.0,
    n_cycles=10000,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.42,
    expected_loosening_deg=12.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=10000, preload_ratio=0.420),
    ]
)
```

---

### Study 41: JMSE 2025 — M12 Deep-Sea Pressure

> **MSD BUILDER NOTE**: This study examines preload variation under **hydrostatic pressure** (0–110 MPa), not cyclic vibration. The preload change is static (pressure-dependent, not cycle-dependent) and driven by differential elastic compression of bolt vs. clamped members. The MSD Builder's current loosening models do not include ambient pressure effects. Use the VDI 2230 external force framework to approximate the hydrostatic compression as an equivalent external axial load.

---

### Study 42: Wi et al. 2022 — 3D-Printed Polymer Bolts

> **MSD BUILDER NOTE**: This study tests **3D-printed polymer bolts** (ABS-2, PLA, glass-filled nylon) under thermal cycling. These materials have fundamentally different mechanical properties (E ~ 1–3 GPa, σ_y ~ 30–60 MPa) compared to steel fasteners. The MSD Builder's standard material database does not include polymer bolt materials. Thermal cycling loosening requires viscoelastic material models not currently implemented. For reference only.
