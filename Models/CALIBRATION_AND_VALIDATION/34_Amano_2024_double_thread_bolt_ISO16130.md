# Study 34: Amano, Shinbutsu, Takemasu et al. (2024) — Double-Thread Anti-Loosening Bolt

## Full Citation
**Authors**: Amano, H.; Shinbutsu, T.; Takemasu, T.; Miyazaki, S.; Kiso, H.; Senba, R.; Karasawa, T.
**Title**: "Optimization of anti-loosening bolt based on double thread mechanism: Development of ground rolling die and effect of thread accuracy on loosening resistance"
**Journal**: Heliyon, 2024, 10(7), e28631
**DOI**: 10.1016/j.heliyon.2024.e28631
**Access**: **OPEN ACCESS**
**URL**: https://doi.org/10.1016/j.heliyon.2024.e28631

---

## Significance
Details the design and manufacturing of the **DTB-IIC double-thread bolt** — a novel anti-loosening fastener where two independent thread spirals with slightly different pitches create an interference fit that resists rotation. Tested per **ISO 16130** (replacement for DIN 25201-4). Ground rolling dies achieve >10× die life compared to conventional EDM.

---

## Double-Thread Mechanism

### Operating Principle
The bolt has two co-helical threads with a **slight pitch difference**:
- Thread A: Standard pitch p₁
- Thread B: Modified pitch p₂ = p₁ + Δp (Δp ≈ 0.02 mm)

When the nut is tightened:
1. Both threads engage the nut
2. The pitch difference creates **opposing axial forces** in the two thread systems
3. Any attempt to rotate the nut in the loosening direction is resisted by the differential pitch force
4. The resistance increases with preload (self-energizing)

### Key Parameters
| Parameter | Standard M12 | DTB-IIC M12 |
|---|---|---|
| Pitch (primary) | 1.75 mm | 1.75 mm |
| Pitch (secondary) | — | 1.77 mm |
| Δp | — | 0.02 mm |
| Backlash (axial play) | 0.05–0.10 mm | 0.01–0.03 mm |
| Prevailing torque | 0 N·m | 2.5–4.0 N·m |

---

## Experimental Setup

### Bolt Specifications
- **Size**: M12 × 1.75
- **Material**: AISI 4135 (SCM435) — equivalent to SAE J429 Grade 8
- **σ_y**: 900 MPa
- **σ_u**: 1,000 MPa
- **Surface**: Zinc-phosphate coating, μ ≈ 0.10–0.14

### Junker Test per ISO 16130
- **Machine**: ISO 16130 compliant transverse vibration tester
- **Amplitude**: ±0.75 mm
- **Frequency**: 12.5 Hz
- **Preload**: 70% of proof load = 50.5 kN
- **Duration**: 2,000 cycles
- **Pass criterion**: ≥80% preload retention at 2,000 cycles

---

## DATA FOR CURVE PLOTTING

### Dataset 1: DTB-IIC vs. Standard Bolt (ISO 16130 Junker test)

**[From Figure 12 in paper]**

#### Standard M12 × 1.75 (no anti-loosening)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.880 |
| 100 | 0.780 |
| 200 | 0.620 |
| 500 | 0.350 |
| 1,000 | 0.140 |
| 1,500 | 0.050 |
| 2,000 | 0.020 |

#### DTB-IIC M12 (small backlash, ground die)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.975 |
| 100 | 0.965 |
| 200 | 0.950 |
| 500 | 0.928 |
| 1,000 | 0.905 |
| 1,500 | 0.890 |
| 2,000 | 0.878 |

#### DTB-IIC M12 (medium backlash, EDM die)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.960 |
| 100 | 0.940 |
| 200 | 0.910 |
| 500 | 0.860 |
| 1,000 | 0.810 |
| 1,500 | 0.775 |
| 2,000 | 0.750 |

#### DTB-IIC M12 (large backlash, worn die)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.940 |
| 100 | 0.900 |
| 200 | 0.840 |
| 500 | 0.740 |
| 1,000 | 0.640 |
| 1,500 | 0.570 |
| 2,000 | 0.520 |

### ISO 16130 Rating
| Configuration | F/F₀ at 2,000 | Rating | Pass? |
|---|---|---|---|
| Standard bolt | 0.020 | — | FAIL |
| DTB-IIC (small backlash) | 0.878 | **Rating-1** | **PASS** |
| DTB-IIC (medium backlash) | 0.750 | Rating-2 | Marginal |
| DTB-IIC (large backlash) | 0.520 | — | FAIL |

---

### Dataset 2: Effect of Backlash (Axial Play) on Loosening Resistance

| Backlash (mm) | F/F₀ at 2,000 cycles | Prevailing torque (N·m) |
|---|---|---|
| 0.01 | 0.900 | 4.0 |
| 0.02 | 0.878 | 3.5 |
| 0.03 | 0.840 | 3.0 |
| 0.05 | 0.750 | 2.5 |
| 0.08 | 0.640 | 1.8 |
| 0.10 | 0.520 | 1.2 |

**Critical finding**: Backlash must be ≤0.03 mm for Rating-1 compliance. This requires high thread accuracy achievable only with ground rolling dies.

---

### Dataset 3: Manufacturing Die Comparison

| Die type | Thread accuracy (JIS) | Backlash (mm) | Die life (bolts) | Cost |
|---|---|---|---|---|
| Ground rolling die | Grade 6g (tight) | 0.01–0.02 | >50,000 | High initial |
| EDM die | Grade 6g-7g | 0.03–0.05 | 3,000–5,000 | Low initial |
| Worn ground die | Grade 7g (loose) | 0.05–0.10 | N/A | N/A |

---

### Dataset 4: FEM Validation — Thread Contact Stress

**ABAQUS model, M12, F₀ = 50.5 kN**

| Thread position | Standard σ_contact (MPa) | DTB-IIC σ_contact (MPa) |
|---|---|---|
| 1st engaged thread | 420 | 380 |
| 2nd | 280 | 310 |
| 3rd | 180 | 250 |
| 4th | 120 | 200 |
| 5th | 80 | 160 |
| 6th | 50 | 120 |

**Note**: DTB-IIC distributes load more uniformly across threads (less stress concentration at first thread), which also improves fatigue life.

---

## Reproduction Parameters

| Parameter | Value | Units |
|---|---|---|
| Bolt | M12 × 1.75 DTB-IIC | — |
| Material | SCM435 / AISI 4135 | — |
| Preload | 50.5 (70% proof) | kN |
| Amplitude | ±0.75 | mm |
| Frequency | 12.5 | Hz |
| Duration | 2,000 | cycles |
| Standard | ISO 16130 | — |
| Surface | Zinc-phosphate | — |
| μ | 0.10–0.14 | — |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2).
> ISO 16130 Junker test. Compare standard bolt vs DTB-IIC anti-loosening bolt.

### Bolt &amp; Thread Geometry

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

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt | SCM435 (AISI 4135) | 206,000 | 900 | 1,000 | 0.30 |
| Nut | Class 10 | 206,000 | 940 | 1,040 | 0.30 |

### MSD Element Chain

```
GROUND — FLANGE — FLANGE — NUT — THREAD — SHANK — HEAD — GROUND
```

### Loading (PropertyInspector) — ISO 16130

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 50,500 | N |
| % Yield | 66.6 | % |
| Transverse disp. δ | 0.75 | mm |
| Frequency | 12.5 | Hz |
| Cycles | 2,000 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.12 |
| Lubricated | true (zinc-phosphate coating) |
| Bolt diameter | 12.0 mm |
| Pitch | 1.75 mm |

### Configurations

| Config | Bolt Type | Backlash (mm) | μ_eff | Expected F/F₀ at 2000 |
|---|---|---|---|---|
| Standard | Plain M12 | 0.05–0.10 | 0.12 | 0.020 |
| DTB-IIC small | Double-thread | 0.01–0.02 | 0.12 | 0.878 |
| DTB-IIC medium | Double-thread | 0.03–0.05 | 0.12 | 0.750 |
| DTB-IIC large | Double-thread | 0.05–0.10 | 0.12 | 0.520 |

### ValidationCase — Standard M12 (Reference)

```python
ValidationCase(
    name="Amano_2024_M12_standard_ISO16130",
    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,
    initial_preload_N=50500,
    preload_percent_yield=66.6,
    transverse_displacement_mm=0.75,
    frequency_Hz=12.5,
    n_cycles=2000,
    mu_initial=0.12,
    lubricated=True,
    expected_final_preload_ratio=0.020,
    expected_loosening_deg=25.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.880),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.780),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.620),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.350),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.140),
        ExperimentalDataPoint(cycles=1500, preload_ratio=0.050),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.020),
    ]
)
```
