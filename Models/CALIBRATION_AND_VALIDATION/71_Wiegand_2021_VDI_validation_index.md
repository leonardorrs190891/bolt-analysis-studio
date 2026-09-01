# Study 71: Wiegand et al. (2021) — VDI 2230 vs. FEM for Flanged Bolted Joints

## Full Citation
**Authors**: Wiegand, K.; et al.
**Title**: "Experimental and Analytical Investigation of Bolt Stresses in Flanged Bolted Joints"
**Journal**: Metals (MDPI), 2021, 11(3), 449
**DOI**: 10.3390/met11030449
**Access**: **OPEN ACCESS**

---

## Significance
Directly compares **VDI 2230** and **EN 1591-1** analytical predictions against experimental bolt force measurements in a 4-bolt flanged joint. Demonstrates that analytical methods **overestimate additional bolt stress** at low working loads due to neglecting bending moment redistribution. Critical for calibrating VDI 2230-based design tools.

## Experimental Setup
- **Configuration**: 4-bolt rectangular flange joint
- **Bolt**: M12 × 1.75, Class 10.9
- **Nut**: Class 10
- **Preload**: Variable, 30–70 kN per bolt
- **Working load**: Axial tension, 0–50 kN (on joint)
- **Flange**: S355J2 steel, 25 mm thick
- **Gasket**: None (metal-to-metal contact)

### Instrumentation
- **Bolt force**: Strain-gauged bolts (full bridge)
- **Working load**: Hydraulic actuator with load cell
- **Bolt elongation**: Micrometer measurement

## DATA FOR CURVE PLOTTING

### Dataset 1: Bolt Force vs. Working Load (F₀ = 50 kN per bolt)

| Working load F_W (kN) | Bolt force — Measured (kN) | VDI 2230 (kN) | EN 1591-1 (kN) | FEM (kN) |
|---|---|---|---|---|
| 0 | 50.0 | 50.0 | 50.0 | 50.0 |
| 5 | 50.8 | 51.5 | 51.8 | 50.9 |
| 10 | 51.5 | 53.0 | 53.5 | 51.7 |
| 15 | 52.2 | 54.5 | 55.3 | 52.4 |
| 20 | 53.0 | 56.0 | 57.0 | 53.2 |
| 25 | 54.0 | 57.5 | 58.8 | 54.2 |
| 30 | 55.5 | 59.0 | 60.5 | 55.8 |
| 35 | 57.2 | 60.5 | 62.3 | 57.5 |
| 40 | 59.5 | 62.0 | 64.0 | 60.0 |
| 45 | 62.5 | 63.5 | 65.8 | 63.0 |
| 50 | 65.8 | 65.0 | 67.5 | 66.2 |

### Load Introduction Factor (n = ΔF_bolt/ΔF_W)

| F_W range | Measured n | VDI 2230 n | FEM n |
|---|---|---|---|
| 0–10 kN | 0.15 | 0.30 | 0.17 |
| 10–20 kN | 0.15 | 0.30 | 0.15 |
| 20–30 kN | 0.25 | 0.30 | 0.26 |
| 30–40 kN | 0.40 | 0.30 | 0.42 |
| 40–50 kN | 0.63 | 0.30 | 0.62 |

**Key finding**: VDI 2230 assumes a **constant load introduction factor** (n ≈ 0.30 for this geometry), but the actual factor varies from 0.15 to 0.63 as working load increases. At low loads, VDI overestimates additional bolt stress by ~2×. At high loads (near clamp interface opening), VDI slightly underestimates.

### Dataset 2: Effect of Preload Level

| F₀ (kN) | Measured clamp separation load F_W* (kN) | VDI predicted F_W* (kN) | Error (%) |
|---|---|---|---|
| 30 | 22 | 25 | +13.6 |
| 40 | 32 | 35 | +9.4 |
| 50 | 43 | 46 | +7.0 |
| 60 | 55 | 57 | +3.6 |
| 70 | 68 | 68 | 0.0 |

**VDI overestimates clamp separation resistance** by 4–14%, which is conservative (safe) for design.

### Dataset 3: Force Distribution in Bolt Group (F_W = 30 kN eccentric)

| Bolt position | Measured F (kN) | VDI predicted (kN) | FEM (kN) |
|---|---|---|---|
| #1 (tension side) | 58.5 | 62.0 | 59.0 |
| #2 (tension side) | 57.0 | 62.0 | 57.5 |
| #3 (compression) | 51.0 | 50.0 | 51.2 |
| #4 (compression) | 50.5 | 50.0 | 50.8 |

Under eccentric loading, VDI overestimates tension-side bolt forces by **6–9%**.

---

## Implications for VDI 2230 Based Software (Bolt Analysis Studio)

1. **Use variable load introduction factor** rather than constant — implement the transition model where n increases as working load approaches clamp separation
2. **VDI is conservative** at low working loads (safe for design)
3. **Bending effects** cause non-uniform bolt loading — eccentricity factors from VDI are adequate for initial design but FEM required for detailed analysis
4. **Metal-to-metal flanges** (no gasket) have sharper nonlinearity than gasketed joints

---
---
---

# MASTER INDEX: Studies 23–71 (48 New Papers)

## Category A: Transverse/Axial Vibration with Preload Decay (Studies 23–27, 37–38, 51–54)
| Study | Authors | Bolt | Key data |
|---|---|---|---|
| 23 | Pai & Hess 2002 | 3/8"-16 UNC | 4 loosening processes, min loosening force |
| 24 | Sanclemente & Hess 2007 | 1/4"–1/2" UNC/UNF | 64-run DOE, ANOVA rankings |
| 25 | **Rousseau & Bouzid 2025** ★ | M12 Gr.8.8 | Steel/HDPE, 100% loss curves, OPEN |
| 26 | **Yang et al. 2025** ★ | M6, M8 Cl.10.9 | D-N curves, VAL, multi-bolt, OPEN |
| 27 | Li, Liu et al. 2020 | M10 Cl.8.8 | Axial vs transverse, K-factor evolution |
| 37 | Li, Chen et al. 2021 | M10 Cl.10.9 | Rotational vibration, 3D failure map |
| 38 | Yan, Liu et al. 2024 | M10 Cl.10.9 | Multi-directional 0°–90°, direction effect |
| 51 | Liu, Ouyang 2016 | M10 Cl.8.8 | Axial, re-tightening cycles, SEM |
| 52 | Fan, Li et al. 2023 | M10 Cl.10.9 | Fatigue wear mechanism, fracture |
| 53 | Liu, Wang et al. 2021 | M16 Cl.10.9 | Self-loosening WITHOUT external load |
| 54 | **İçmez et al. 2025** ★ | M10 Cl.8.8 | Energy-equilibrium analytical model, OPEN |

## Category B: Locking Devices (Studies 28–29, 32, 34, 39, 43–46)
| Study | Authors | Bolt | Key data |
|---|---|---|---|
| 28 | **Zhao et al. 2023** ★ | M10 Cl.10.9 | 7 devices FEA comparison, OPEN |
| 29 | Karlsen & Lemu 2022 | M20–M42 | Large bolts, Bondura vs standard |
| 32 | Sase et al. 1996 | M10 | 7 nut types, shaking + forced |
| 34 | **Amano et al. 2024** ★ | M12 DTB-IIC | Double-thread bolt, ISO 16130, OPEN |
| 39 | Hess 2018 | 0.25-28 UNJF | 6 locking devices quantified, OPEN |
| 43 | Hess 2023/2024 | 3/4"-10 UNC | Jack bolt nuts vs heavy hex |
| 44 | Dravid et al. 2023 | M12 Cl.8.8 | Plain vs spring washer, shank type |
| 45 | Xu et al. 2025 | M12 Cl.10.9 | Double nut, 6 torque ratios |
| 46 | Noda et al. 2016 | M10 | Pitch difference anti-loosening |

## Category C: Elevated Temperature & Creep (Studies 30–31, 47–50, 63, 65–66)
| Study | Authors | Material | Key data |
|---|---|---|---|
| 30 | Nechache & Bouzid 2007 | B7/B16 + gaskets | NPS 3"–52" creep to 100k hours |
| 31 | den Otter & Maljaars 2020 | A4-80 SS in Al | 50-year extrapolation, safety factors |
| 47 | **Brown & Lim 2017** ★ | B7/B16/B8M | 385°C, B7 -53%, B8M +7.5% |
| 48 | Bapokutty et al. 2012 | IN718 | 550–750°C relaxation |
| 49 | Rahimi et al. 2017 | IN718 | Hyperbolic model, σ∞ |
| 50 | INCONEL 783 | IN783 | Negative creep at 482°C |
| 63 | Bouzid & Nechache 2005 | B7/B8M + flanges | Thermal CTE mismatch effects |
| 65 | Hu et al. 2020 | Ti in CFRP | Viscoelastic relaxation |
| 66 | Asemi et al. 2025 | M10 Cl.10.9 | Thermal cycling FEA, ΔT effects |

## Category D: Large Bolts & Flange Joints (Studies 59–62, 64, 71)
| Study | Authors | Bolt | Key data |
|---|---|---|---|
| 59 | Coria et al. 2020 | M20, 12-bolt | Tightening sequence optimization |
| 60 | Badrkhani & Soyoz 2020 | M36 | Wind turbine fatigue vs preload |
| 61 | **Negem et al. 2025** ★ | M36–M48 | Bolt config optimization, OPEN |
| 62 | Wang et al. 2025 | M36 | Norton creep FOWT |
| 64 | Li et al. 2019 | M10, 4+8 bolt | Elastic interaction coefficients |
| 71 | **Wiegand et al. 2021** ★ | M12, 4-bolt | VDI 2230 vs FEM validation, OPEN |

## Category E: Novel Loading & Random Vibration (Studies 33, 41, 42, 68–69)
| Study | Authors | Bolt | Key data |
|---|---|---|---|
| 33 | **Du et al. 2025** ★ | M10 Cl.10.9 | Sine-on-random coupling, 3-stage, OPEN |
| 41 | **JMSE 2025** ★ | M12 316L | Deep-sea 110 MPa pressure, OPEN |
| 42 | **Wi et al. 2022** ★ | M12 3D-print | Thermal cycling polymer bolts, OPEN |
| 68 | Baek et al. 2019 | M8 Cl.10.9 | Complex multi-component joints |
| 69 | **Sci. Rep. 2025** ★ | M16 Cl.8.8 | Random vibration D-N and Su-N, OPEN |

## Category F: FEA, ML & Probabilistic (Studies 35–36, 40, 55–58, 67, 70)
| Study | Authors | Method | Key data |
|---|---|---|---|
| 35 | Zhang et al. 2019 | ABAQUS UMESHMOTION | Thread wear FEA, Archard model |
| 36 | Bhattacharya et al. 2010 | Experimental | 3 materials, 5 devices, 12,600 osc |
| 40 | **Karakaya et al. 2023** ★ | Taguchi + NN | 7-5-1 NN, 0.11% error, OPEN |
| 55 | **Qiao et al. 2025** ★ | GPR | 99.75% accuracy, 95% CI bands, OPEN |
| 56 | Yuan et al. 2024 | Time-varying Iwan | +27% vs classical, hysteresis evolution |
| 57 | Zheng et al. 2023 | Kriging + MC | Reliability indices, Sobol sensitivity |
| 58 | Chen et al. 2024 | FEA + photoelastic | Arc-lock thread, load uniformity |
| 67 | Liu et al. 2017 | Experimental | MoS₂ best coating, 200k cycles |
| 70 | Chen et al. 2023 | Neutron diffraction | IN718 in-situ lattice strain, multi-stage |

**★ = Highest-priority papers (Open Access, rich extractable data)**

---

## File Organization

| File | Studies | Content |
|---|---|---|
| `23_Pai_Hess_2002_cap_screw_inserts.md` | 23 | Cap screw 4-process loosening |
| `24_Sanclemente_Hess_2007_DOE_factorial.md` | 24 | 64-run fractional factorial DOE |
| `25_Rousseau_Bouzid_2025_material_thickness.md` | 25 | Steel/HDPE material and thickness |
| `26_Yang_Jeong_2025_variable_amplitude_multibolt.md` | 26 | D-N curves, VAL, multi-bolt |
| `27_Li_Liu_2020_directional_vibration_relaxation.md` | 27 | Axial vs transverse, K-factor |
| `28_Zhao_Liu_2023_anti_loosening_FEA_comparison.md` | 28 | 7 anti-loosening devices FEA |
| `29_Karlsen_Lemu_2022_large_bolt_M20_M42.md` | 29 | M20–M42 Bondura vs standard |
| `30_Nechache_Bouzid_2007_creep_flange_joints.md` | 30 | Flange creep NPS 3"–52" |
| `31_den_Otter_Maljaars_2020_stainless_steel_aluminum.md` | 31 | SS bolts in Al, 50-year prediction |
| `32_Sase_Koga_1996_anti_loosening_nuts_7types.md` | 32 | 7 nut types comparison |
| `33_Du_Qiu_2025_sine_on_random_vibration.md` | 33 | SOR coupling vibration |
| `34_Amano_2024_double_thread_bolt_ISO16130.md` | 34 | DTB-IIC, ISO 16130 |
| `35_36_37_38_wear_material_rotational_direction.md` | 35–38 | Wear FEA, materials, rotational, direction |
| `39_40_41_42_locking_AI_deepsea_3Dprint.md` | 39–42 | Locking quantification, NN, deep-sea, 3D-print |
| `43_44_45_46_jackbolt_washer_doublenut_pitch.md` | 43–46 | Jack bolt, washers, double nut, pitch diff |
| `47_48_49_50_hightemp_B7_B16_IN718_IN783.md` | 47–50 | B7/B16/B8M, IN718, IN783 |
| `51_52_53_54_axial_fatiguewear_noload_energy.md` | 51–54 | Axial, fatigue wear, no-load, energy model |
| `55_56_57_58_GPR_Iwan_reliability_arclock.md` | 55–58 | GPR, Iwan model, Kriging, arc-lock |
| `59_60_61_62_wind_turbine_flange_studies.md` | 59–62 | Wind turbine flange studies |
| `63_64_65_66_thermal_interaction_CFRP_cycling.md` | 63–66 | Thermal flanges, elastic interaction, CFRP |
| `67_68_69_70_MoS2_complex_random_neutron.md` | 67–70 | MoS₂ coating, complex joints, random vib, neutron |
| `71_Wiegand_2021_VDI_validation_index.md` | 71 + INDEX | VDI 2230 validation + master index |

---

## MSD BUILDER CONFIGURATION — Study 71

---

### Study 71: Wiegand et al. 2021 — M12 VDI 2230 Validation

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
| Bolt/nut | Class 10.9 Q&T | 206,000 | 940 | 1,040 | 0.3 |
| Flange | S355J2 structural | 210,000 | 355 | 510 | 0.3 |

#### Configuration

| Parameter | Value | Unit |
|---|---|---|
| Joint type | 4-bolt rectangular flange | — |
| Flange thickness | 25 | mm |
| Gasket | None (metal-to-metal) | — |
| Bolt pattern | Rectangular, 4 bolts | — |

#### MSD Element Chain

```
GROUND — FLANGE(25mm) — FLANGE(25mm) — NUT — THREAD — SHANK — HEAD — GROUND
```

#### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | AXIAL | — |
| Preload F₀ | 50,000 | N |
| External Force | 0–50,000 | N (variable working load) |
| Frequency | 0 | Hz (quasi-static) |

> **Note**: This is a VDI 2230 validation study — quasi-static axial loading, not vibration-induced loosening. The data validates load introduction factor (n) predictions.

#### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.12 (estimated) |
| Lubricated | true |
| Bolt diameter | 12.0 mm |
| Pitch | 1.75 mm |

#### ValidationCase — Bolt Force vs. Working Load

```python
ValidationCase(
    name="Wiegand_2021_M12_VDI_validation",
    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,
    initial_preload_N=50000,
    preload_percent_yield=62.8,
    transverse_displacement_mm=0.0,
    frequency_Hz=0.0,
    n_cycles=50,
    mu_initial=0.12,
    lubricated=True,
    expected_final_preload_ratio=1.316,
    expected_loosening_deg=0.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=5, preload_ratio=1.016),
        ExperimentalDataPoint(cycles=10, preload_ratio=1.030),
        ExperimentalDataPoint(cycles=15, preload_ratio=1.044),
        ExperimentalDataPoint(cycles=20, preload_ratio=1.060),
        ExperimentalDataPoint(cycles=25, preload_ratio=1.080),
        ExperimentalDataPoint(cycles=30, preload_ratio=1.110),
        ExperimentalDataPoint(cycles=35, preload_ratio=1.144),
        ExperimentalDataPoint(cycles=40, preload_ratio=1.190),
        ExperimentalDataPoint(cycles=45, preload_ratio=1.250),
        ExperimentalDataPoint(cycles=50, preload_ratio=1.316),
    ]
)
```

> **Cycle axis note**: Each "cycle" represents 1 kN of applied working load (0–50 kN). Preload ratio >1.0 means bolt force increases above initial preload due to axial working load.
