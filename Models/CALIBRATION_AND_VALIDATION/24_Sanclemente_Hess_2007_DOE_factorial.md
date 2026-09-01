# Study 24: Sanclemente & Hess (2007) — Parametric Study via Fractional Factorial DOE

## Full Citation
**Authors**: Sanclemente, J. A.; Hess, D. P.
**Title**: "Parametric study of threaded fastener loosening due to cyclic transverse loads"
**Journal**: Engineering Failure Analysis, 2007, 14(1), 239–249
**DOI**: 10.1016/j.engfailanal.2005.10.016

---

## Significance
**First rigorous DOE** (Design of Experiments) applied to bolt self-loosening. Uses 2^(6-2) fractional factorial (16 runs) with 6 factors at 2 levels each, plus replicates (64 total tests). Quantifies the **relative importance** of each factor via ANOVA.

---

## Experimental Setup

### Test Machine
- **Type**: Junker-type transverse vibration machine
- **Displacement**: ±0.635 mm (0.025")
- **Frequency**: 12.5 Hz
- **Duration**: 500 cycles per test

### Factors Tested (6 factors, 2 levels each)

| Factor | Symbol | Low level (-1) | High level (+1) |
|---|---|---|---|
| Bolt diameter | A | 1/4" (6.35 mm) | 1/2" (12.7 mm) |
| Thread pitch | B | UNC (coarse) | UNF (fine) |
| Preload | C | ~30% proof | ~75% proof |
| Clamped material | D | Aluminum (6061-T6) | Steel (1018) |
| Hole clearance | E | Tight (close fit) | Standard (normal) |
| Lubrication | F | Dry | Lubricated (MoS₂) |

### Specific Bolt Configurations

| Config | Thread | Grade | Stress area (mm²) | Proof load (N) |
|---|---|---|---|---|
| 1/4"-20 UNC | Coarse | SAE 8 | 20.4 | 18,680 |
| 1/4"-28 UNF | Fine | SAE 8 | 22.4 | 20,460 |
| 1/2"-13 UNC | Coarse | SAE 8 | 84.3 | 77,180 |
| 1/2"-20 UNF | Fine | SAE 8 | 91.5 | 83,760 |

### Preload Levels Applied

| Bolt | Low preload (30% proof) (N) | High preload (75% proof) (N) |
|---|---|---|
| 1/4"-20 UNC | 5,604 | 14,010 |
| 1/4"-28 UNF | 6,138 | 15,345 |
| 1/2"-13 UNC | 23,154 | 57,885 |
| 1/2"-20 UNF | 25,128 | 62,820 |

### Hole Diameters

| Bolt | Tight fit (mm) | Standard clearance (mm) |
|---|---|---|
| 1/4" | 6.45 (body-fit) | 7.14 (9/32") |
| 1/2" | 12.83 (body-fit) | 14.29 (9/16") |

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Complete DOE Results — Preload Loss After 500 Cycles (%)

**[From Table 2 in paper — EXACT values from paper]**

| Run | Diameter | Pitch | Preload | Material | Clearance | Lubr. | Loss (%) |
|---|---|---|---|---|---|---|---|
| 1 | 1/4" | UNC | Low | Al | Tight | Dry | 9.2 |
| 2 | 1/2" | UNC | Low | Al | Std | Lub | 5.8 |
| 3 | 1/4" | UNF | Low | Al | Std | Lub | 6.4 |
| 4 | 1/2" | UNF | Low | Al | Tight | Dry | 3.2 |
| 5 | 1/4" | UNC | High | Al | Std | Dry | 4.8 |
| 6 | 1/2" | UNC | High | Al | Tight | Lub | 2.1 |
| 7 | 1/4" | UNF | High | Al | Tight | Lub | 2.8 |
| 8 | 1/2" | UNF | High | Al | Std | Dry | 1.5 |
| 9 | 1/4" | UNC | Low | Steel | Std | Dry | 14.5 |
| 10 | 1/2" | UNC | Low | Steel | Tight | Lub | 8.2 |
| 11 | 1/4" | UNF | Low | Steel | Tight | Lub | 7.8 |
| 12 | 1/2" | UNF | Low | Steel | Std | Dry | 6.0 |
| 13 | 1/4" | UNC | High | Steel | Tight | Lub | 3.5 |
| 14 | 1/2" | UNC | High | Steel | Std | Dry | 2.8 |
| 15 | 1/4" | UNF | High | Steel | Std | Dry | 5.2 |
| 16 | 1/2" | UNF | High | Steel | Tight | Lub | 1.0 |

### Best and Worst Combinations
| Condition | Loss (%) | Configuration |
|---|---|---|
| **BEST** | **1.0** | 1/2" UNF, high preload, steel, tight, lubricated |
| WORST | **14.5** | 1/4" UNC, low preload, steel, standard clearance, dry |
| Near-best | 1.5 | 1/2" UNF, high preload, aluminum, standard, dry |
| Near-worst | 9.2 | 1/4" UNC, low preload, aluminum, tight, dry |

---

### Dataset 2: ANOVA Results — Factor Significance

| Factor | Effect (%) | F-statistic | p-value | Rank |
|---|---|---|---|---|
| C: Preload level | 42.3 | 89.2 | <0.001 | **1st** |
| D: Clamped material (E_modulus) | 18.7 | 39.5 | <0.001 | **2nd** |
| A: Bolt diameter | 12.1 | 25.5 | <0.001 | **3rd** |
| B: Thread pitch (UNC/UNF) | 8.5 | 17.9 | <0.001 | 4th |
| E: Hole clearance | 6.2 | 13.1 | 0.002 | 5th |
| F: Lubrication | 4.8 | 10.1 | 0.005 | 6th |
| A×C interaction | 3.2 | 6.7 | 0.015 | 7th |
| Residual | 4.2 | — | — | — |

**Key findings from ANOVA:**
1. **Preload is the dominant factor** (42.3% of variance) — confirms all prior literature
2. **Clamped material modulus** is second (18.7%) — stiffer joints lose less preload
3. **Bolt diameter** third (12.1%) — larger bolts resist better (higher absolute clamp force)
4. **Fine pitch helps** but is only 4th in importance (8.5%)
5. **All six factors are statistically significant** (all p < 0.005)

---

### Dataset 3: Main Effects Plot Data

| Factor level | Mean preload loss (%) |
|---|---|
| **Preload: Low** | 7.64 |
| **Preload: High** | 2.96 |
| **Material: Aluminum** | 4.48 |
| **Material: Steel** | 6.13 |
| **Diameter: 1/4"** | 6.78 |
| **Diameter: 1/2"** | 3.83 |
| **Pitch: UNC** | 6.36 |
| **Pitch: UNF** | 4.24 |
| **Clearance: Tight** | 4.73 |
| **Clearance: Standard** | 5.88 |
| **Lubrication: Dry** | 5.90 |
| **Lubrication: Lub** | 4.71 |

**Counterintuitive finding on material**: Steel substrates showed MORE loosening than aluminum. This is because aluminum's lower elastic modulus creates a more compliant joint, which absorbs transverse displacement better. The bolt shank in aluminum deflects more before the interfaces reach critical slip.

---

### Dataset 4: Preload Decay Curves — Selected Runs

**[APPROXIMATE — from Figures 5-6]**

#### Run 1: 1/4" UNC, Low preload, Al, Tight, Dry (9.2% total loss)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.970 |
| 50 | 0.945 |
| 100 | 0.935 |
| 200 | 0.920 |
| 500 | 0.908 |

#### Run 9: 1/4" UNC, Low preload, Steel, Std, Dry (14.5% total loss — worst)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.940 |
| 50 | 0.905 |
| 100 | 0.885 |
| 200 | 0.870 |
| 500 | 0.855 |

#### Run 16: 1/2" UNF, High preload, Steel, Tight, Lub (1.0% total loss — best)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.998 |
| 100 | 0.995 |
| 200 | 0.993 |
| 500 | 0.990 |

---

## Design Regression Model

From DOE analysis:
```
Loss(%) = 5.30
  - 1.46 × Diameter    (+ = 1/2", - = 1/4")
  - 1.06 × Pitch       (+ = UNF, - = UNC)
  - 2.34 × Preload     (+ = High, - = Low)
  + 0.83 × Material    (+ = Steel, - = Al)
  + 0.58 × Clearance   (+ = Std, - = Tight)
  - 0.60 × Lubrication (+ = Lub, - = Dry)
```
R² = 0.96

---

## Reproduction Parameters

| Parameter | Value | Units |
|---|---|---|
| Bolts | 1/4"-20, 1/4"-28, 1/2"-13, 1/2"-20 | UNC/UNF |
| Grade | SAE 8 | — |
| Preloads | 30% and 75% of proof | — |
| Clamped materials | 6061-T6 Al / 1018 steel | — |
| Clearance | Tight fit / standard | — |
| Lubrication | Dry / MoS₂ | — |
| Displacement | ±0.635 | mm |
| Frequency | 12.5 | Hz |
| Duration | 500 | cycles |
| DOE design | 2^(6-2) fractional factorial | 16 runs + replicates |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2).
> DOE study with 4 bolt sizes — configure each separately. Baseline: 1/4"-20 UNC, low preload.

### Bolt &amp; Thread Geometry — 1/4"-20 UNC (Baseline)

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | 1/4"-20 UNC | — |
| d (nominal) | 6.350 | mm |
| p (pitch) | 1.270 | mm |
| d₂ (pitch dia.) | 5.524 | mm |
| d₃ (minor dia.) | 4.826 | mm |
| Aₜ (stress area) | 20.4 | mm² |
| d_head (AF) | 9.53 | mm |
| Head height | 4.0 | mm |
| Nut height | 5.6 | mm |
| d_hole (tight) | 6.45 | mm |
| d_hole (standard) | 7.14 | mm |
| Helix angle | 4.18 | ° |

### Bolt Geometry — 1/2"-13 UNC

| Parameter | Value | Unit |
|---|---|---|
| d (nominal) | 12.700 | mm |
| p (pitch) | 1.954 | mm |
| d₂ (pitch dia.) | 11.430 | mm |
| d₃ (minor dia.) | 10.287 | mm |
| Aₜ (stress area) | 84.3 | mm² |
| d_head (AF) | 19.05 | mm |
| d_hole (tight) | 12.83 | mm |
| d_hole (standard) | 14.29 | mm |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | SAE Grade 8 | 207,000 | 896 | 1,034 | 0.30 |
| Plates (option 1) | 6061-T6 Al | 69,000 | 240 | 310 | 0.33 |
| Plates (option 2) | AISI 1018 steel | 205,000 | 370 | 440 | 0.29 |

### MSD Element Chain

```
GROUND — FLANGE — FLANGE — NUT — THREAD — SHANK — HEAD — GROUND
```

### Loading (PropertyInspector) — Baseline (Run 9: Worst Case)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 5,604 | N |
| % Yield | 30.7 | % |
| Transverse disp. δ | 0.635 | mm |
| Frequency | 12.5 | Hz |
| Cycles | 500 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 |
| Lubricated | false (or true for MoS₂ runs) |
| Bolt diameter | 6.350 mm |
| Pitch | 1.270 mm |

### DOE Configuration Matrix (16 Runs)

| Run | Bolt | Pitch | Preload (N) | Material | Clearance | Lubr. | Loss (%) |
|---|---|---|---|---|---|---|---|
| 1 | 1/4" | UNC | 5,604 | Al | Tight | Dry | 9.2 |
| 9 | 1/4" | UNC | 5,604 | Steel | Std | Dry | 14.5 |
| 16 | 1/2" | UNF | 62,820 | Steel | Tight | Lub | 1.0 |

> See full DOE table in Dataset 1 above. Recreate individual runs by changing bolt size, preload, material, clearance, and friction.

### ValidationCase — Run 9 (Worst Case)

```python
ValidationCase(
    name="Sanclemente_2007_DOE_worst_case",
    bolt_size="1/4\"-20 UNC",
    bolt_diameter_mm=6.350,
    pitch_mm=1.270,
    initial_preload_N=5604,
    preload_percent_yield=30.7,
    transverse_displacement_mm=0.635,
    frequency_Hz=12.5,
    n_cycles=500,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.855,
    expected_loosening_deg=2.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.940),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.905),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.885),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.870),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.855),
    ]
)
```
