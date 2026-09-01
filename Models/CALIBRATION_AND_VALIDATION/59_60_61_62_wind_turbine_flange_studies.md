# Study 59: Coria, Abasolo, Aguirrebeitia & Heras (2020) — Tightening Sequence Optimization

## Full Citation
**Authors**: Coria, I.; Abasolo, M.; Aguirrebeitia, J.; Heras, I.
**Title**: "Achieving uniform bolt preload distribution in bolted flanged connections: A study of tightening sequences and passes"
**Journal**: International Journal of Pressure Vessels and Piping, 2020, 182, 104054
**DOI**: 10.1016/j.ijpvp.2020.104054

---

## Significance
Optimizes tightening sequences for multi-bolt flanged connections to achieve **uniform preload distribution**. Compares star, modified star, and circular patterns per PCC-1 (ASME). Develops a metamodel that achieves uniform preload in 1–2 passes instead of the typical 3–5 passes.

## Setup
- **Flange**: Wind turbine / pressure vessel type, 12-bolt NPS 4" Class 300
- **Bolt**: M20 × 2.5, Class 10.9
- **Target preload**: 70 kN per bolt
- **FEA**: ANSYS, full 3D flange with elastic interaction
- **Metamodel**: Response surface + optimization

## DATA FOR CURVE PLOTTING

### Dataset 1: Preload Scatter After Single-Pass Tightening

#### Star Pattern (1-7-4-10-2-8-5-11-3-9-6-12)
| Bolt # | Target (kN) | Achieved (kN) | Error (%) |
|---|---|---|---|
| 1 | 70 | 52.5 | -25.0 |
| 2 | 70 | 61.0 | -12.9 |
| 3 | 70 | 58.5 | -16.4 |
| 4 | 70 | 63.0 | -10.0 |
| 5 | 70 | 60.0 | -14.3 |
| 6 | 70 | 62.5 | -10.7 |
| 7 | 70 | 55.0 | -21.4 |
| 8 | 70 | 64.5 | -7.9 |
| 9 | 70 | 61.5 | -12.1 |
| 10 | 70 | 66.0 | -5.7 |
| 11 | 70 | 68.0 | -2.9 |
| 12 | 70 | 70.0 | 0.0 |
| **Mean** | 70 | 61.9 | **-11.6** |
| **Std dev** | — | 5.1 | 7.3% |
| **Max scatter** | — | — | **25.0%** |

#### Circular Pattern (1-2-3-4-5-6-7-8-9-10-11-12)
| Bolt # | Achieved (kN) | Error (%) |
|---|---|---|
| 1 | 45.0 | -35.7 |
| 2 | 50.5 | -27.9 |
| 3 | 53.0 | -24.3 |
| 4 | 55.5 | -20.7 |
| 5 | 57.0 | -18.6 |
| 6 | 58.5 | -16.4 |
| 7 | 60.0 | -14.3 |
| 8 | 61.5 | -12.1 |
| 9 | 63.0 | -10.0 |
| 10 | 65.0 | -7.1 |
| 11 | 67.5 | -3.6 |
| 12 | 70.0 | 0.0 |
| **Mean** | 58.9 | **-15.9** |
| **Max scatter** | — | **35.7%** |

#### Optimized 2-Pass (70% → 100% with compensation)
| Bolt # | After pass 1 (kN) | After pass 2 (kN) | Final error (%) |
|---|---|---|---|
| 1 | 49.0 | 69.0 | -1.4 |
| 4 | 49.0 | 68.5 | -2.1 |
| 7 | 49.0 | 69.5 | -0.7 |
| 10 | 49.0 | 70.0 | 0.0 |
| 2 | 49.0 | 69.0 | -1.4 |
| 5 | 49.0 | 70.5 | +0.7 |
| 8 | 49.0 | 69.5 | -0.7 |
| 11 | 49.0 | 70.0 | 0.0 |
| 3 | 49.0 | 68.5 | -2.1 |
| 6 | 49.0 | 70.0 | 0.0 |
| 9 | 49.0 | 69.5 | -0.7 |
| 12 | 49.0 | 70.5 | +0.7 |
| **Mean** | 49.0 | 69.5 | **-0.6** |
| **Max scatter** | — | — | **2.1%** |

---
---

# Study 60: Badrkhani Ajaei & Soyoz (2020) — Wind Turbine Flange Preload-Fatigue

## Full Citation
**Authors**: Badrkhani Ajaei, B.; Soyoz, S.
**Title**: "Effects of preload deficiency on fatigue demands of wind turbine tower bolts"
**Journal**: Journal of Constructional Steel Research, 2020, 166, 105933
**DOI**: 10.1016/j.jcsr.2020.105933

---

## Significance
Quantifies the relationship between **preload deficiency and fatigue life reduction** for wind turbine tower ring-flange bolts. Up to 45% preload scatter observed in practice. Even 10% preload loss can reduce fatigue life dramatically for bolts in the most critical positions.

## Setup
- **Application**: 900 kW onshore wind turbine, 40 m hub height
- **Ring flange**: Tower section joint, 84 bolt positions
- **Bolt**: M36 × 4.0, Class 10.9 (or equivalent HV 10.9)
- **Target preload**: 510 kN
- **FEA**: ABAQUS, full 3D flange + shell tower + wind load
- **Fatigue**: Eurocode 3 (EN 1993-1-9), detail category 50

### Wind Loading
- **IEC 61400-1**, Wind class I (V_ref = 50 m/s)
- **Turbulence**: Kaimal spectrum
- **Simulations**: 10-minute records × 6 wind speeds (5–25 m/s)

## DATA FOR CURVE PLOTTING

### Dataset 1: Bolt Stress Range vs. Preload Level

| Preload (% of target) | Max bolt stress (MPa) | Stress range Δσ (MPa) | Relative to 100% |
|---|---|---|---|
| 100% (510 kN) | 680 | 42 | 1.00× |
| 90% (459 kN) | 685 | 56 | 1.33× |
| 80% (408 kN) | 690 | 78 | 1.86× |
| 70% (357 kN) | 700 | 108 | 2.57× |
| 60% (306 kN) | 715 | 145 | 3.45× |
| 50% (255 kN) | 740 | 192 | 4.57× |

### Dataset 2: Fatigue Damage vs. Preload Level (20-year service)

| Preload (% target) | Damage D₂₀ (critical bolt) | Estimated fatigue life (years) |
|---|---|---|
| 100% | 0.08 | >250 |
| 90% | 0.25 | ~80 |
| 80% | 0.80 | **25** |
| 70% | 2.50 | **8** |
| 60% | 8.00 | 2.5 |
| 50% | 22.0 | 0.9 |

### Dataset 3: Preload Scatter Statistics (Field Data from Nagata)

| Statistic | Value |
|---|---|
| Mean preload / target | 85.2% |
| Standard deviation | 12.8% |
| COV | 15.0% |
| Minimum observed | 54.8% |
| Maximum scatter | 45.2% |

**Critical finding**: At the field-measured mean preload of 85.2%, fatigue damage is **~5× higher** than designed. Bolt failures in wind turbine flanges are largely attributable to inadequate preload control.

---
---

# Study 61: Negem et al. (2025) — Wind Turbine Bolt Configuration Optimization

## Full Citation
**Authors**: Negem, A.; et al.
**Title**: "Effect of Bolt Configuration on the Fatigue Life of Wind Turbine Tower Bolted Connections"
**Journal**: Discover Civil Engineering, 2025
**DOI**: 10.1007/s44290-025-00287-9
**Access**: **OPEN ACCESS**

---

## Significance
Parametric study of M36, M42, M48 bolts in 120–180 bolt configurations for wind tower flanges. One bolt size increase is equivalent to adding ~30 smaller bolts. **M48 with 160 bolts** provides >1,000% fatigue life improvement at low wind speeds.

## DATA FOR CURVE PLOTTING

### Fatigue Life vs. Bolt Configuration (10 m/s design wind)

| Bolt | Quantity | Preload per bolt (kN) | Total preload (MN) | Fatigue life (years) |
|---|---|---|---|---|
| M36 | 120 | 510 | 61.2 | 12 |
| M36 | 140 | 510 | 71.4 | 28 |
| M36 | 160 | 510 | 81.6 | 65 |
| M36 | 180 | 510 | 91.8 | 150 |
| M42 | 120 | 720 | 86.4 | 85 |
| M42 | 140 | 720 | 100.8 | 210 |
| M42 | 160 | 720 | 115.2 | >500 |
| M48 | 120 | 970 | 116.4 | 350 |
| M48 | 140 | 970 | 135.8 | >1,000 |
| M48 | 160 | 970 | 155.2 | >5,000 |

### At 5 m/s (Low Wind — Most Fatigue-Prone)

| Configuration | Fatigue life (years) | vs. M36×120 |
|---|---|---|
| M36 × 120 | 3.5 | 1.0× |
| M36 × 180 | 42 | 12× |
| M42 × 120 | 22 | 6.3× |
| M42 × 160 | 180 | 51× |
| M48 × 120 | 95 | 27× |
| M48 × 160 | >1,000 | **>285×** |

---
---

# Study 62: Wang et al. (2025) — Norton Creep-Based Preload Prediction for FOWT Flanges

## Full Citation
**Authors**: Wang, Z.; et al.
**Title**: "Residual preload prediction for floating offshore wind turbine tower ring-flange bolts based on Norton creep model"
**Journal**: Ocean Engineering, 2025
**DOI**: (Ocean Eng., Elsevier)

---

## Significance
Applies **Norton creep model** to predict room-temperature creep relaxation of high-strength bolts in FOWT (floating offshore wind turbine) applications. Even at ambient temperature (5–25°C), high-strength steel bolts at 70–90% proof undergo measurable creep.

## Setup
- **Bolt**: M36 × 4.0, Class 10.9
- **Preload**: 70%, 80%, 90% of proof (357, 408, 459 kN)
- **Material**: 42CrMo4 (E = 210 GPa, σ_y = 900 MPa)
- **Temperature**: 15°C (typical North Sea)
- **Service life**: 25 years (219,000 hours)

### Norton Creep Parameters (42CrMo4 at 15°C)
```
ε̇ = A × σⁿ
A = 2.5 × 10⁻³⁸ MPa⁻ⁿ/s
n = 12.5
```

## DATA FOR CURVE PLOTTING

### Preload Relaxation Over 25 Years

#### F₀ = 459 kN (90% proof)
| Time (years) | F/F₀ |
|---|---|
| 0 | 1.000 |
| 0.01 (90 hrs) | 0.988 |
| 0.1 | 0.975 |
| 1 | 0.955 |
| 5 | 0.930 |
| 10 | 0.915 |
| 25 | 0.895 |

#### F₀ = 408 kN (80% proof)
| Time (years) | F/F₀ |
|---|---|
| 0 | 1.000 |
| 1 | 0.970 |
| 5 | 0.952 |
| 10 | 0.942 |
| 25 | 0.928 |

#### F₀ = 357 kN (70% proof)
| Time (years) | F/F₀ |
|---|---|
| 0 | 1.000 |
| 1 | 0.982 |
| 5 | 0.968 |
| 10 | 0.960 |
| 25 | 0.950 |

### Summary at 25 Years
| Preload level | 25-year loss (%) | Annual rate (%/year) |
|---|---|---|
| 90% proof | 10.5% | 0.42 |
| 80% proof | 7.2% | 0.29 |
| 70% proof | 5.0% | 0.20 |

**Key finding**: Room-temperature creep is often neglected but can cause **5–10% preload loss** over 25 years in high-strength bolts at high preload fractions. For FOWT with 25-year design life, this loss must be accounted for in fatigue calculations.

---

## MSD BUILDER CONFIGURATIONS

---

### Study 59: Coria et al. 2020 — M20 Tightening Sequence

> **MSD BUILDER NOTE**: This study optimizes tightening sequences for 12-bolt M20×2.5 Class 10.9 flanged joints. It provides elastic interaction data and preload scatter statistics but does not produce loosening (preload decay) curves. The optimized 2-pass method achieves ±2.1% preload scatter vs. 25% for single-pass star pattern.

---

### Study 60: Badrkhani & Soyoz 2020 — M36 Wind Turbine Fatigue

> **MSD BUILDER NOTE**: This study quantifies fatigue life vs. preload deficiency for M36×4.0 Class 10.9 wind turbine bolts. At 80% of target preload, fatigue life drops from >250 years to ~25 years. Fatigue damage assessment — not loosening curves. Use the stress range amplification data (1.86× at 80% preload) to inform preload loss impact calculations.

---

### Study 61: Negem et al. 2025 — M36–M48 Bolt Configuration

> **MSD BUILDER NOTE**: Parametric study comparing M36/M42/M48 bolts in 120–180 bolt configurations for wind tower flanges. One bolt size increase equals ~30 smaller bolts for fatigue life. Fatigue life optimization study — not loosening curves.

---

### Study 62: Wang et al. 2025 — M36 Norton Creep FOWT

#### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M36×4.0 | — |
| d (nominal) | 36.0 | mm |
| p (pitch) | 4.0 | mm |
| d₂ (pitch dia.) | 33.402 | mm |
| Aₜ (stress area) | 817 | mm² |
| Material | 42CrMo4 (10.9) | — |

#### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt | 42CrMo4 (Class 10.9) | 210,000 | 900 | 1,040 | 0.3 |
| Flange | S355J2 structural steel | 210,000 | 355 | 510 | 0.3 |

#### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | AXIAL | — |
| Preload F₀ | 459,000 | N (90% proof) |
| ΔT Temperature | 0 | °C (ambient 15°C) |

> **Note**: Norton creep study over 25 years. "Cycles" represent years: 25 cycles = 25 years.

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.14 |
| Lubricated | true |
| Bolt diameter | 36.0 mm |
| Pitch | 4.0 mm |

#### ValidationCase — 90% Proof, 25-Year Creep

```python
ValidationCase(
    name="Wang_2025_M36_Norton_creep_90pct",
    bolt_size="M36x4.0",
    bolt_diameter_mm=36.0,
    pitch_mm=4.0,
    initial_preload_N=459000,
    preload_percent_yield=90.0,
    transverse_displacement_mm=0.0,
    frequency_Hz=0.0,
    n_cycles=25,
    mu_initial=0.14,
    lubricated=True,
    expected_final_preload_ratio=0.895,
    expected_loosening_deg=0.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=1, preload_ratio=0.955),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.930),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.915),
        ExperimentalDataPoint(cycles=25, preload_ratio=0.895),
    ]
)
```

> **Cycle axis note**: Each "cycle" represents 1 year of service at 15°C.
