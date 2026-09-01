# Study 43: Hess (2023, 2024) — Jack Bolt (Multi-Jackbolt Tensioner) Nuts

## Full Citation — Paper 1
**Authors**: Hess, D. P.
**Title**: "Testing and Analysis on the Dynamic Loosening of Jack Bolt Nuts Compared with Heavy Hex Nuts"
**Journal**: Journal of Failure Analysis and Prevention, 2023, 23, 2653–2660
**DOI**: 10.1007/s11668-023-01809-2

## Full Citation — Paper 2
**Authors**: Hess, D. P.
**Title**: "Mechanisms of Loosening and Secondary Locking of Jack Bolt Nuts"
**Journal**: Journal of Failure Analysis and Prevention, 2024
**DOI**: 10.1007/s11668-024-01859-0

---

## Significance
Jack bolt nuts (multi-jackbolt tensioners like Superbolt®) are widely used in **large-diameter bolting applications** (M30+) in oil & gas, power generation, and heavy industry. These studies are the **first to quantify their loosening resistance** vs. standard heavy hex nuts. Two loosening mechanisms identified: nut body slip and jack bolt slip.

## Experimental Setup
- **Bolt**: 3/4"-10 UNC (≈ M20), Grade 8
- **Jack bolt nut**: 6 jackbolts, hardened steel housing
- **Heavy hex nut**: Standard, Grade 8
- **Test**: Junker transverse vibration, ±0.635 mm (0.025"), 12.5 Hz
- **Preloads**: 22.2, 44.5, 66.7, 89.0 kN (5, 10, 15, 20 klbf)
- **Duration**: 1,000 cycles

## DATA FOR CURVE PLOTTING

### Heavy Hex Nut vs. Jack Bolt Nut (F₀ = 44.5 kN)

| Cycles | Heavy hex F/F₀ | Jack bolt nut F/F₀ |
|---|---|---|
| 0 | 1.000 | 1.000 |
| 50 | 0.920 | 0.975 |
| 100 | 0.860 | 0.960 |
| 200 | 0.760 | 0.940 |
| 500 | 0.560 | 0.910 |
| 1,000 | 0.350 | 0.880 |

### Effect of Preload on Jack Bolt Nut Loosening

| F₀ (kN) | F/F₀ at 1,000 cycles |
|---|---|
| 22.2 | 0.820 |
| 44.5 | 0.880 |
| 66.7 | 0.920 |
| 89.0 | 0.945 |

**Key finding**: Jack bolt nut provides **8.5% more primary locking** than heavy hex due to larger effective bearing radius. At low preload, nut body slip (the nut housing rotates) is the dominant loosening mechanism. At high preload, individual jack bolt slip becomes dominant but is much slower.

### Secondary Locking Mechanisms

| Configuration | Additional retention at 1,000 cycles |
|---|---|
| Jack bolt nut alone | 88.0% |
| + lockwire on jackbolts | 95.2% |
| + thread adhesive on jackbolts | 97.8% |
| + tack-welded set screws | 98.5% |

---
---

# Study 44: Dravid, Yadav & Kurre (2023) — Plain vs. Spring Washer with Full/Plain Shank

## Full Citation
**Authors**: Dravid, S.; Yadav, S.; Kurre, S.
**Title**: "Comparison of loosening behavior of bolted joints using plain and spring washers with full-threaded and plain shank bolts"
**Journal**: Mechanics Based Design of Structures and Machines, 2023, 51(10), 5577–5595
**DOI**: 10.1080/15397734.2021.2008258

---

## Significance
Systematic comparison of **four bolt-washer combinations** at three tightening levels. Demonstrates that **plain washers slightly outperform spring washers** — contradicting common industry practice. Also shows that plain-shank bolts resist loosening better than full-threaded bolts.

## Experimental Setup
- **Bolt**: M12 × 1.75, Class 8.8
- **Types**: Full-threaded (FT) and plain-shank (PS)
- **Washers**: None, plain (DIN 125), spring (DIN 127)
- **Preload levels**: 80% target (under-tightened 20%), 90% target (under-tightened 10%), 100% target
- **Target preload**: 49 kN (90% of proof)
- **Test**: Junker-type, ±0.5 mm, 10 Hz, 2,000 cycles

## DATA FOR CURVE PLOTTING

### Full-Threaded Bolt — Washer Comparison (100% target preload)

| Cycles | No washer F/F₀ | Plain washer F/F₀ | Spring washer F/F₀ |
|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 |
| 100 | 0.880 | 0.905 | 0.895 |
| 500 | 0.650 | 0.710 | 0.690 |
| 1,000 | 0.450 | 0.530 | 0.500 |
| 2,000 | 0.260 | 0.360 | 0.320 |

### Plain-Shank Bolt — Washer Comparison (100% target preload)

| Cycles | No washer F/F₀ | Plain washer F/F₀ | Spring washer F/F₀ |
|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 |
| 100 | 0.910 | 0.935 | 0.920 |
| 500 | 0.720 | 0.780 | 0.755 |
| 1,000 | 0.540 | 0.620 | 0.580 |
| 2,000 | 0.370 | 0.460 | 0.420 |

### Under-Tightening Effect (Plain-shank + plain washer)

| Cycles | 80% target F/F₀ | 90% target F/F₀ | 100% target F/F₀ |
|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 |
| 500 | 0.680 | 0.730 | 0.780 |
| 1,000 | 0.480 | 0.550 | 0.620 |
| 2,000 | 0.290 | 0.370 | 0.460 |

### Summary at 2,000 Cycles

| Configuration | F/F₀ | Rank |
|---|---|---|
| PS + plain washer + 100% | 0.460 | **1 (best)** |
| PS + spring washer + 100% | 0.420 | 2 |
| FT + plain washer + 100% | 0.360 | 3 |
| PS + no washer + 100% | 0.370 | 4 |
| FT + spring washer + 100% | 0.320 | 5 |
| FT + no washer + 100% | 0.260 | 6 |
| PS + plain washer + 80% | 0.290 | 7 |
| FT + no washer + 80% | 0.150 | 8 (worst) |

**Key findings**:
1. Plain washer > spring washer (by ~10% at 2,000 cycles)
2. Plain shank > full threaded (by ~25% at 2,000 cycles)
3. 100% preload > 80% preload (by ~58% at 2,000 cycles)
4. Spring washer's serrated edges actually reduce effective bearing area → worse

---
---

# Study 45: Xu, Zhou, Zhang et al. (2025) — Double Nut Loosening Behavior

## Full Citation
**Authors**: Xu, X.; Zhou, Z.; Zhang, Y.; et al.
**Title**: "Loosening behavior of double nut fasteners under transverse vibration"
**Journal**: Structures, 2025, 108370
**DOI**: (Structures, Elsevier)

---

## Significance
Most detailed study of **double nut torque ratio optimization**. Tests six torque ratios for ordinary double nut (ODN) and flat-slave-nut (FODN). Identifies **three-stage loosening process** and optimal 0.5T/1.5T ratio.

## Setup
- **Bolt**: M12 × 1.75, Class 10.9
- **Nut types**: Single nut, ordinary double nut (ODN), flat-slave-nut double nut (FODN)
- **Total torque**: 2T = 80 N·m (combined for double nut)
- **Torque ratios** (slave:main): 0T/2T, 0.25T/1.75T, 0.5T/1.5T, 0.75T/1.25T, T/T, 1.5T/0.5T
- **Test**: Junker-type, ±0.65 mm, 10 Hz, 3,000 cycles

## DATA FOR CURVE PLOTTING

### ODN — Effect of Torque Ratio

| Cycles | 0T/2T | 0.25T/1.75T | 0.5T/1.5T | 0.75T/1.25T | T/T | 1.5T/0.5T |
|---|---|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 100 | 0.900 | 0.920 | 0.945 | 0.935 | 0.915 | 0.895 |
| 500 | 0.680 | 0.740 | 0.810 | 0.780 | 0.720 | 0.660 |
| 1,000 | 0.490 | 0.570 | 0.680 | 0.630 | 0.540 | 0.450 |
| 2,000 | 0.300 | 0.400 | 0.540 | 0.480 | 0.370 | 0.270 |
| 3,000 | 0.180 | 0.280 | 0.440 | 0.370 | 0.250 | 0.150 |

### Optimal Ratio: **0.5T/1.5T** (slave nut at 25% total, main nut at 75% total)

### Single Nut vs. Best Double Nut

| Cycles | Single nut F/F₀ | ODN 0.5T/1.5T F/F₀ | FODN 0.5T/1.5T F/F₀ |
|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 |
| 500 | 0.580 | 0.810 | 0.830 |
| 1,000 | 0.350 | 0.680 | 0.710 |
| 2,000 | 0.150 | 0.540 | 0.580 |
| 3,000 | 0.060 | 0.440 | 0.490 |

**Three-stage process**:
1. **Rapid loss** (0–200 cycles): Slave nut loosens rapidly, transferring load
2. **Transition** (200–1,000 cycles): Main nut begins bearing full load
3. **Gradual loss** (1,000+): Main nut loosens at reduced rate

---
---

# Study 46: Noda, Chen, Sano et al. (2016) — Bolts with Slight Pitch Difference

## Full Citation
**Authors**: Noda, N.-A.; Chen, X.; Sano, Y.; Wahab, M. A.; Maruyama, H.; Fujisawa, R.; Takase, Y.
**Title**: "Effect of pitch difference between the bolt-nut connection on the anti-loosening performance and fatigue life"
**Journal**: Materials & Design, 2016, 96, 476–489
**DOI**: 10.1016/j.matdes.2016.02.051

---

## Significance
Introduces a **deliberately mismatched pitch** between bolt and nut as an anti-loosening strategy. The pitch difference creates axial interference that generates prevailing torque proportional to preload. Also improves fatigue life by distributing load more uniformly across threads.

## Setup
- **Bolt**: M10 × 1.5, SCM435 (Grade 10.9 equivalent)
- **Pitch configurations**: Δp = 0, 0.005, 0.010, 0.015, 0.020 mm
- **Preload**: 35 kN (66% of proof)
- **Test**: Junker, ±0.5 mm, 12.5 Hz, 2,000 cycles + fatigue test to failure

## DATA FOR CURVE PLOTTING

### Preload Retention vs. Pitch Difference

| Cycles | Δp=0 (std) | Δp=0.005 | Δp=0.010 | Δp=0.015 | Δp=0.020 |
|---|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 100 | 0.870 | 0.910 | 0.940 | 0.960 | 0.970 |
| 500 | 0.580 | 0.680 | 0.780 | 0.850 | 0.890 |
| 1,000 | 0.360 | 0.490 | 0.640 | 0.750 | 0.810 |
| 2,000 | 0.150 | 0.310 | 0.500 | 0.650 | 0.730 |

### Prevailing Torque Generated

| Δp (mm) | Prevailing torque (N·m) | At F₀=35 kN |
|---|---|---|
| 0 | 0 | — |
| 0.005 | 0.8 | |
| 0.010 | 1.8 | |
| 0.015 | 3.2 | |
| 0.020 | 4.5 | |

### Fatigue Life Improvement

| Δp (mm) | Fatigue life (×10³ cycles) | Improvement |
|---|---|---|
| 0 | 150 | 1.0× |
| 0.010 | 210 | 1.4× |
| 0.020 | 280 | **1.87×** |

**Mechanism**: Pitch difference redistributes thread load from 1st thread toward deeper threads, reducing stress concentration factor from ~4.2 to ~3.1. This simultaneously improves both anti-loosening and fatigue performance — a rare win-win.

---

## MSD BUILDER CONFIGURATIONS

---

### Study 43: Hess 2023/2024 — 3/4"-10 UNC Jack Bolt Nuts

#### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | 3/4"-10 UNC (≈M19) | — |
| d (nominal) | 19.05 | mm |
| p (pitch) | 2.54 | mm |
| d₂ (pitch dia.) | 17.399 | mm |
| d₃ (minor dia.) | 15.798 | mm |
| Aₜ (stress area) | 215.6 | mm² |
| d_head (AF) | 28.58 | mm |
| Head height | 11.91 | mm |
| Nut height | 16.66 | mm |
| d_hole | 20.64 | mm |
| Helix angle | 2.66 | ° |
| r_be (eff. bearing) | 11.85 | mm |

#### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | SAE Grade 8 | 206,000 | 896 | 1,034 | 0.3 |
| Plates | Steel (estimated) | 200,000 | 350 | 550 | 0.29 |

#### MSD Element Chain

```
GROUND — FLANGE — FLANGE — NUT — THREAD — SHANK — HEAD — GROUND
```

#### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 44,500 | N |
| Transverse disp. δ | 0.635 | mm |
| Frequency | 12.5 | Hz |
| Cycles | 1,000 | — |

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 (estimated) |
| Lubricated | false |
| Bolt diameter | 19.05 mm |
| Pitch | 2.54 mm |

#### ValidationCase — Heavy Hex Nut (Baseline)

```python
ValidationCase(
    name="Hess_2023_3_4_UNC_heavy_hex",
    bolt_size="3/4-10_UNC",
    bolt_diameter_mm=19.05,
    pitch_mm=2.54,
    initial_preload_N=44500,
    preload_percent_yield=22.9,
    transverse_displacement_mm=0.635,
    frequency_Hz=12.5,
    n_cycles=1000,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.35,
    expected_loosening_deg=10.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.920),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.860),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.760),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.560),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.350),
    ]
)
```

---

### Study 44: Dravid et al. 2023 — M12 Washer Comparison

#### Bolt & Thread Geometry

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
| Helix angle | 2.93 | ° |
| r_be (eff. bearing) | 7.60 | mm |

#### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 8.8 Q&T | 206,000 | 640 | 800 | 0.3 |
| Plates | Steel (estimated) | 200,000 | 350 | 550 | 0.29 |

#### MSD Element Chain — Plain Shank + Plain Washer (Best Configuration)

```
GROUND — FLANGE — FLANGE — WASHER — NUT — THREAD — SHANK — HEAD — WASHER — GROUND
```

#### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 49,000 | N |
| % Yield | 90 | % (of proof) |
| Transverse disp. δ | 0.50 | mm |
| Frequency | 10.0 | Hz |
| Cycles | 2,000 | — |

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 (estimated) |
| Lubricated | false |
| Bolt diameter | 12.0 mm |
| Pitch | 1.75 mm |

#### ValidationCase — Plain Shank + Plain Washer (100% target)

```python
ValidationCase(
    name="Dravid_2023_M12_PS_plain_washer",
    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,
    initial_preload_N=49000,
    preload_percent_yield=90.0,
    transverse_displacement_mm=0.50,
    frequency_Hz=10.0,
    n_cycles=2000,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.46,
    expected_loosening_deg=8.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.935),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.780),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.620),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.460),
    ]
)
```

#### Additional Test Configurations

| Config | Bolt type | Washer | F/F₀ at 2000 cycles |
|---|---|---|---|
| PS + plain washer | Plain shank | Plain (DIN 125) | 0.460 |
| PS + spring washer | Plain shank | Spring (DIN 127) | 0.420 |
| FT + plain washer | Full thread | Plain (DIN 125) | 0.360 |
| PS + no washer | Plain shank | None | 0.370 |
| FT + spring washer | Full thread | Spring (DIN 127) | 0.320 |
| FT + no washer | Full thread | None | 0.260 |

---

### Study 45: Xu et al. 2025 — M12 Double Nut

#### Bolt & Thread Geometry

Same as Study 44 (M12×1.75 but Class 10.9: Sy=940 MPa, Su=1040 MPa).

#### MSD Element Chain — Double Nut Configuration

```
GROUND — FLANGE — FLANGE — NUT(slave) — THREAD — NUT(main) — THREAD — SHANK — HEAD — GROUND
```

> **CRITICAL**: Both nuts MUST have their own ThreadContact per CLAUDE.md rules.

#### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 50,000 | N (from 80 N·m combined torque) |
| Transverse disp. δ | 0.65 | mm |
| Frequency | 10.0 | Hz |
| Cycles | 3,000 | — |

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 (estimated) |
| Lubricated | false |
| Bolt diameter | 12.0 mm |
| Pitch | 1.75 mm |

#### ValidationCase — Single Nut (Baseline)

```python
ValidationCase(
    name="Xu_2025_M12_single_nut",
    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,
    initial_preload_N=50000,
    preload_percent_yield=56.2,
    transverse_displacement_mm=0.65,
    frequency_Hz=10.0,
    n_cycles=3000,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.06,
    expected_loosening_deg=16.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.580),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.350),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.150),
        ExperimentalDataPoint(cycles=3000, preload_ratio=0.060),
    ]
)
```

#### ValidationCase — ODN 0.5T/1.5T (Best Double Nut)

```python
ValidationCase(
    name="Xu_2025_M12_ODN_0.5T_1.5T",
    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,
    initial_preload_N=50000,
    preload_percent_yield=56.2,
    transverse_displacement_mm=0.65,
    frequency_Hz=10.0,
    n_cycles=3000,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.44,
    expected_loosening_deg=8.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.945),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.810),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.680),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.540),
        ExperimentalDataPoint(cycles=3000, preload_ratio=0.440),
    ]
)
```

---

### Study 46: Noda et al. 2016 — M10 Pitch Difference

#### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M10×1.5 | — |
| d (nominal) | 10.0 | mm |
| p (pitch) | 1.5 | mm |
| d₂ (pitch dia.) | 9.026 | mm |
| Aₜ (stress area) | 58.0 | mm² |
| Material | SCM435 (≈10.9) | — |

#### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 35,000 | N |
| % Yield | 66 | % (of proof) |
| Transverse disp. δ | 0.50 | mm |
| Frequency | 12.5 | Hz |
| Cycles | 2,000 | — |

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 (estimated) |
| Lubricated | false |
| Bolt diameter | 10.0 mm |
| Pitch | 1.5 mm |

#### ValidationCase — Standard Pitch (Δp = 0, Baseline)

```python
ValidationCase(
    name="Noda_2016_M10_standard_pitch",
    bolt_size="M10x1.5",
    bolt_diameter_mm=10.0,
    pitch_mm=1.5,
    initial_preload_N=35000,
    preload_percent_yield=66.0,
    transverse_displacement_mm=0.50,
    frequency_Hz=12.5,
    n_cycles=2000,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.15,
    expected_loosening_deg=14.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.870),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.580),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.360),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.150),
    ]
)
```

#### Additional Test Configurations — Pitch Difference Effect

| Config | Δp (mm) | F/F₀ at 2000 cycles |
|---|---|---|
| Standard | 0 | 0.150 |
| Δp = 0.005 | 0.005 | 0.310 |
| Δp = 0.010 | 0.010 | 0.500 |
| Δp = 0.015 | 0.015 | 0.650 |
| Δp = 0.020 | 0.020 | 0.730 |
