# Study 51: Liu, Ouyang, Peng et al. (2016) — Axial Excitation Self-Loosening and Re-Tightening

## Full Citation
**Authors**: Liu, Z.; Ouyang, H.; Peng, J.; Zhu, S.; Ma, X.
**Title**: "Self-loosening of bolt joints under transverse load and repeated tightening-loosening cycles"
**Journal**: Wear, 2016, 346–347, 66–77
**DOI**: (Wear, Elsevier)

---

## Significance
Studies loosening under **axial excitation** (rather than transverse) and investigates the effect of **repeated tightening-loosening cycles**. Shows that preload drops quickly in the first 3 tightening-loosening cycles then stabilizes. SEM/EDX analysis reveals progressive thread surface damage. Directly relevant to maintenance re-torque intervals.

## Experimental Setup
- **Bolt**: M10 × 1.5, Class 8.8, electrolytic zinc plated (EZP)
- **Preload**: 13.5–14.5 kN (achieved via 30 N·m torque)
- **Excitation**: Axial sinusoidal, 10 Hz
- **Axial load amplitudes**: 7.5 kN and 12.5 kN
- **Duration**: 5,000 cycles per tightening cycle
- **Re-tightening**: Up to 10 cycles of tighten → vibrate → loosen → retighten

### Clamped Assembly
- **Material**: AISI 1045 steel
- **Plates**: 2 × 15 mm = 30 mm grip
- **Hole**: 11 mm (standard clearance)

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Axial Excitation — Effect of Amplitude (First Tightening)

#### Axial amplitude = 7.5 kN (F_ax/F₀ = 0.53)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 100 | 0.975 |
| 500 | 0.945 |
| 1,000 | 0.925 |
| 2,000 | 0.900 |
| 5,000 | 0.870 |

#### Axial amplitude = 12.5 kN (F_ax/F₀ = 0.89)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 100 | 0.940 |
| 500 | 0.870 |
| 1,000 | 0.815 |
| 2,000 | 0.750 |
| 5,000 | 0.660 |

**Key finding**: At F_ax/F₀ = 0.89, bolt experiences **partial unloading** each cycle (F_min = F₀ - F_ax = 1.5 kN), leading to significant thread slip and 34% preload loss in 5,000 cycles.

---

### Dataset 2: Repeated Tightening-Loosening Cycles (Axial 12.5 kN)

| Re-tightening cycle | F₀ (kN) | F after 5,000 vib. cycles (kN) | Loss per vib. cycle (%) |
|---|---|---|---|
| 1st | 14.2 | 9.4 | 33.8% |
| 2nd | 14.0 | 10.8 | 22.9% |
| 3rd | 13.8 | 11.5 | 16.7% |
| 4th | 13.6 | 11.6 | 14.7% |
| 5th | 13.5 | 11.6 | 14.1% |
| 6th | 13.5 | 11.7 | 13.3% |
| 8th | 13.4 | 11.7 | 12.7% |
| 10th | 13.3 | 11.8 | 11.3% |

**Stabilization occurs after ~3rd cycle**: Thread surfaces work-harden and asperities flatten, creating a more conforming contact. Initial tightening experiences the worst loosening.

---

### Dataset 3: Torque vs. Re-Tightening Cycle

| Cycle | Tightening torque (N·m) | Achieved preload (kN) | K-factor |
|---|---|---|---|
| 1st | 30.0 | 14.2 | 0.211 |
| 2nd | 30.0 | 14.0 | 0.214 |
| 3rd | 30.0 | 13.8 | 0.217 |
| 5th | 30.0 | 13.5 | 0.222 |
| 10th | 30.0 | 13.3 | 0.226 |

**Torque coefficient increases** with re-use due to surface damage — same torque produces progressively lower preload.

---

### Dataset 4: Thread Surface Damage (SEM Observations)

| Re-tightening cycle | Surface condition | Ra (μm) |
|---|---|---|
| New (unused) | Smooth, machining marks visible | 0.8 |
| After 1st cycle | Light scratching, adhesive wear particles | 1.2 |
| After 3rd cycle | Moderate plowing, zinc coating worn through | 2.0 |
| After 5th cycle | Severe plastic deformation, micro-pitting | 2.8 |
| After 10th cycle | Stabilized damage pattern, oxide layer | 3.2 |

---
---

# Study 52: Fan, Li, Zhang et al. (2023) — Fatigue Wear Under Transverse Cyclic Displacement

## Full Citation
**Authors**: Fan, H.; Li, Z.; Zhang, Y.; Wang, D.; Xu, J.
**Title**: "Research on fatigue wear mechanism of bolted joints under cyclic transverse displacement"
**Journal**: Tribology International, 2023, 178, 108030
**DOI**: 10.1016/j.triboint.2022.108030

---

## Significance
Identifies **fatigue wear** (rather than adhesive or abrasive wear) as the primary thread degradation mechanism during loosening. Fatigue life follows normal distribution at large amplitudes. Fracture morphology shows ductile dimples → fatigue cracks → catastrophic failure.

## Experimental Setup
- **Bolt**: M10 × 1.5, Class 10.9
- **Preload**: 35 kN
- **Displacement amplitudes**: 0.3, 0.5, 0.7, 0.9, 1.1 mm
- **Frequency**: 10 Hz
- **Duration**: To failure or 50,000 cycles

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Loosening Degree vs. Displacement Amplitude at 10,000 Cycles

| δ (mm) | F/F₀ at 10,000 cycles | Loosening degree (%) |
|---|---|---|
| 0.3 | 0.880 | 12.0 |
| 0.5 | 0.640 | 36.0 |
| 0.7 | 0.380 | 62.0 |
| 0.9 | 0.180 | 82.0 |
| 1.1 | 0.050 | 95.0 |

### Dataset 2: Preload Decay Curves

#### δ = 0.3 mm (sub-critical — primarily Stage I)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 1,000 | 0.960 |
| 5,000 | 0.920 |
| 10,000 | 0.880 |
| 20,000 | 0.840 |
| 50,000 | 0.780 |

#### δ = 0.7 mm (severe loosening)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 500 | 0.820 |
| 1,000 | 0.680 |
| 2,000 | 0.520 |
| 5,000 | 0.380 |
| 10,000 | 0.250 |

#### δ = 1.1 mm (rapid loosening → bolt fatigue)
| Cycles | F/F₀ | Notes |
|---|---|---|
| 0 | 1.000 | |
| 200 | 0.680 | |
| 500 | 0.380 | |
| 1,000 | 0.150 | |
| 2,000 | 0.050 | |
| 3,500 | 0.000 | Bolt fracture (fatigue) |

### Dataset 3: Fatigue Life Statistics at δ = 1.1 mm

| Sample | Cycles to fracture |
|---|---|
| 1 | 2,850 |
| 2 | 3,200 |
| 3 | 3,500 |
| 4 | 3,780 |
| 5 | 4,100 |
| **Mean** | **3,486** |
| **Std dev** | **487** |
| **COV** | **14.0%** |

Normal distribution confirmed by Shapiro-Wilk test (p = 0.82).

### Wear Mechanism Progression
| Stage | Cycles | Mechanism | Surface evidence |
|---|---|---|---|
| 1 | 0–500 | Adhesive wear | Material transfer, micro-welding |
| 2 | 500–2,000 | Abrasive wear | Plowing grooves, wear debris |
| 3 | 2,000–3,000 | Fatigue wear | Subsurface cracks, delamination |
| 4 | 3,000+ | Fatigue fracture | Crack propagation → brittle fracture |

---
---

# Study 53: Liu, Wang, Li et al. (2021) — Self-Loosening Without External Load

## Full Citation
**Authors**: Liu, J.; Wang, X.; Li, Z.; Cai, L.; Xu, J.
**Title**: "Self-loosening of threaded fasteners without external load"
**Journal**: Engineering Failure Analysis, 2021, 127, 105541
**DOI**: 10.1016/j.engfailanal.2021.105541

---

## Significance
Demonstrates that bolted joints can lose preload **even without any external vibration or load** — purely from internal elastic recovery and plastic deformation redistribution after tightening. This is the baseline "no-load" relaxation that occurs in every bolted joint, typically 2–10% in the first minutes after assembly.

## Setup
- **Bolt**: M16 × 2.0, Class 10.9
- **Preload**: 120 kN (via torque-controlled tightening)
- **Clamped material**: AISI 4140 steel, 2 × 20 mm
- **Monitoring**: Strain-gauged bolt, continuous recording for 48 hours
- **No external load applied**
- **FEA**: 3D helix thread model in ABAQUS

## DATA FOR CURVE PLOTTING

### Dataset 1: Preload Decay Without External Load

| Time after tightening | F/F₀ | Mechanism |
|---|---|---|
| 0 (tighten complete) | 1.000 | — |
| 10 seconds | 0.975 | Elastic recovery of thread engagement |
| 1 minute | 0.960 | Bearing surface settling |
| 5 minutes | 0.948 | Thread surface plastic flow |
| 30 minutes | 0.938 | Micro-asperity creep |
| 1 hour | 0.932 | |
| 6 hours | 0.922 | |
| 24 hours | 0.915 | |
| 48 hours | 0.912 | Stabilized |

### Dataset 2: Elastic vs. Plastic Contributions (FEA Decomposition)

| Time | Total loss (%) | Elastic recovery (%) | Plastic deformation (%) |
|---|---|---|---|
| 10 s | 2.5 | 1.8 | 0.7 |
| 1 min | 4.0 | 2.0 | 2.0 |
| 5 min | 5.2 | 2.0 | 3.2 |
| 1 hour | 6.8 | 2.0 | 4.8 |
| 24 hours | 8.5 | 2.0 | 6.5 |
| 48 hours | 8.8 | 2.0 | 6.8 |

**Key finding**: Elastic recovery accounts for only ~2% and occurs within the first 10 seconds. The remaining 6.8% loss is **plastic deformation** at thread roots and under the bearing surface, continuing for hours.

### Dataset 3: Effect of Preload Level

| F₀ (kN) | % of proof | Loss at 48 hours (%) |
|---|---|---|
| 60 | 30% | 3.5 |
| 90 | 45% | 5.8 |
| 120 | 60% | 8.8 |
| 150 | 75% | 12.5 |
| 180 | 90% | 18.2 |

**Near-yield tightening** (90% proof) causes nearly 5× more initial relaxation than 30% proof tightening.

---
---

# Study 54: İçmez, İnce & Enser (2025) — Energy-Equilibrium Loosening Model

## Full Citation
**Authors**: İçmez, H.; İnce, S.; Enser, K.
**Title**: "An Energy-Equilibrium Analytical Approach to Self-Loosening of Bolted Joints Under Transverse Vibration"
**Journal**: European Journal of Research and Development, 2025, 5(1), 294–309
**DOI**: 10.56038/ejrnd.v5i1.693
**Access**: **OPEN ACCESS**

---

## Significance
Develops an **energy-equilibrium analytical model** for predicting bolt rotation angle per cycle and clamping force decay during Junker test. No FEA required — closed-form expressions validated against experimental data. Practical for quick engineering calculations.

## Model Framework

### Energy Balance Per Cycle
```
W_input (transverse displacement) = W_friction (thread + bearing) + W_rotation (nut back-off)
```

### Bolt Rotation Per Cycle
```
Δθ = [F_trans × δ × (1 - μ_eff × tan(α+ρ))] / [F₀ × r_eff × (μ_eff + tan(α+ρ))]
```
Where:
- F_trans = transverse force amplitude
- δ = displacement amplitude
- μ_eff = effective friction coefficient (combined thread + bearing)
- α = thread helix angle
- ρ = friction angle = arctan(μ_thread)
- r_eff = effective bearing radius

### Preload Decay
```
F(N) = F₀ × exp(-N × Δθ × p / (2π × L_bolt))
```
Where p = thread pitch, L_bolt = bolt stretch length

## Validation Data

### Model vs. Experiment (M10 × 1.5, Gr.8.8, F₀ = 25 kN, δ = ±0.5 mm)

| Cycles | Experimental F/F₀ | Model F/F₀ | Error (%) |
|---|---|---|---|
| 0 | 1.000 | 1.000 | 0.0 |
| 50 | 0.920 | 0.925 | +0.5 |
| 100 | 0.860 | 0.870 | +1.2 |
| 200 | 0.750 | 0.768 | +2.4 |
| 500 | 0.540 | 0.565 | +4.6 |
| 1,000 | 0.350 | 0.380 | +8.6 |

### Effect of Friction Coefficient (M10, F₀ = 25 kN, δ = ±0.5 mm)

| μ_eff | Predicted Δθ (°/cycle) | Predicted F/F₀ at 500 cycles |
|---|---|---|
| 0.08 | 0.42 | 0.320 |
| 0.10 | 0.28 | 0.450 |
| 0.12 | 0.18 | 0.565 |
| 0.15 | 0.10 | 0.690 |
| 0.20 | 0.04 | 0.835 |
| 0.25 | 0.01 | 0.940 |

### Critical Displacement for Loosening Onset
```
δ_critical = μ_eff × F₀ / k_transverse
```
Below δ_critical, only non-rotational relaxation occurs.

| μ_eff | F₀ (kN) | k_trans (kN/mm) | δ_critical (mm) |
|---|---|---|---|
| 0.10 | 25 | 50 | 0.050 |
| 0.12 | 25 | 50 | 0.060 |
| 0.15 | 25 | 50 | 0.075 |
| 0.10 | 40 | 50 | 0.080 |
| 0.15 | 40 | 50 | 0.120 |

---

## MSD BUILDER CONFIGURATIONS

---

### Study 51: Liu et al. 2016 — M10 Axial Excitation & Re-Tightening

#### Bolt & Thread Geometry

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
| Bolt/nut | Class 8.8 (EZP) | 206,000 | 640 | 800 | 0.3 |
| Plates | AISI 1045 | 200,000 | 530 | 690 | 0.29 |

#### MSD Element Chain

```
GROUND — FLANGE(15mm) — FLANGE(15mm) — NUT — THREAD — SHANK — HEAD — GROUND
```

#### Loading (PropertyInspector) — High Amplitude Case

| Parameter | Value | Unit |
|---|---|---|
| Load type | AXIAL | — |
| Preload F₀ | 14,200 | N |
| External Force | 12,500 | N (axial sinusoidal amplitude) |
| Frequency | 10.0 | Hz |
| Cycles | 5,000 | — |

> **Note**: This study uses AXIAL excitation. Set Load type = AXIAL. The external force is a pulsating axial load superimposed on the preload.

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 (zinc plated) |
| Lubricated | false |
| Bolt diameter | 10.0 mm |
| Pitch | 1.5 mm |

#### ValidationCase — Axial 12.5 kN (1st Tightening)

```python
ValidationCase(
    name="Liu_2016_M10_axial_12.5kN",
    bolt_size="M10x1.5",
    bolt_diameter_mm=10.0,
    pitch_mm=1.5,
    initial_preload_N=14200,
    preload_percent_yield=42.2,
    transverse_displacement_mm=0.0,
    frequency_Hz=10.0,
    n_cycles=5000,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.66,
    expected_loosening_deg=3.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.940),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.870),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.815),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.750),
        ExperimentalDataPoint(cycles=5000, preload_ratio=0.660),
    ]
)
```

---

### Study 52: Fan et al. 2023 — M10 Fatigue Wear

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
| Bolt/nut | Class 10.9 Q&T | 206,000 | 940 | 1,040 | 0.3 |
| Plates | Steel (estimated) | 200,000 | 350 | 550 | 0.29 |

#### Loading (PropertyInspector) — δ = 0.7 mm

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 35,000 | N |
| Transverse disp. δ | 0.70 | mm |
| Frequency | 10.0 | Hz |
| Cycles | 10,000 | — |

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 (estimated) |
| Lubricated | false |
| Bolt diameter | 10.0 mm |
| Pitch | 1.5 mm |

#### ValidationCase — δ = 0.7 mm (Severe Loosening)

```python
ValidationCase(
    name="Fan_2023_M10_fatigue_wear_0.7mm",
    bolt_size="M10x1.5",
    bolt_diameter_mm=10.0,
    pitch_mm=1.5,
    initial_preload_N=35000,
    preload_percent_yield=64.1,
    transverse_displacement_mm=0.70,
    frequency_Hz=10.0,
    n_cycles=10000,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.25,
    expected_loosening_deg=12.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.820),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.680),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.520),
        ExperimentalDataPoint(cycles=5000, preload_ratio=0.380),
        ExperimentalDataPoint(cycles=10000, preload_ratio=0.250),
    ]
)
```

#### Additional Test Configurations

| Config | δ (mm) | F/F₀ at 10,000 cycles | Notes |
|---|---|---|---|
| Sub-critical | 0.3 | 0.880 | Primarily Stage I |
| Moderate | 0.5 | 0.640 | Two-stage loosening |
| Severe | 0.7 | 0.380 (at 5k) | Wear-dominated |
| Extreme | 0.9 | 0.180 | Rapid loosening |
| Failure | 1.1 | 0.050 | Bolt fracture at ~3,500 cycles |

---

### Study 53: Liu et al. 2021 — Self-Loosening Without External Load

> **MSD BUILDER NOTE**: This study demonstrates preload loss without any external vibration — purely from elastic recovery and plastic deformation after tightening. M16×2.0 Class 10.9 at 120 kN loses ~8.8% in 48 hours. This represents baseline "no-load relaxation" and serves as a lower-bound reference. The MSD Builder's current models focus on vibration-induced loosening.

---

### Study 54: Icmez et al. 2025 — M10 Energy-Equilibrium Model

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
| Bolt/nut | Class 8.8 | 206,000 | 640 | 800 | 0.3 |
| Plates | Steel (estimated) | 200,000 | 350 | 550 | 0.29 |

#### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 25,000 | N |
| Transverse disp. δ | 0.50 | mm |
| Frequency | 10.0 | Hz |
| Cycles | 1,000 | — |

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.12 |
| Lubricated | false |
| Bolt diameter | 10.0 mm |
| Pitch | 1.5 mm |

#### ValidationCase

```python
ValidationCase(
    name="Icmez_2025_M10_energy_model",
    bolt_size="M10x1.5",
    bolt_diameter_mm=10.0,
    pitch_mm=1.5,
    initial_preload_N=25000,
    preload_percent_yield=45.8,
    transverse_displacement_mm=0.50,
    frequency_Hz=10.0,
    n_cycles=1000,
    mu_initial=0.12,
    lubricated=False,
    expected_final_preload_ratio=0.35,
    expected_loosening_deg=10.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.920),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.860),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.750),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.540),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.350),
    ]
)
```
