# Validation Candidates by Loading Condition — BAS v4.0
## internal reference — Petrobras R&D
**Compiled**: 2026-02-26
**Purpose**: Select 2+ papers per condition to validate the coupled loosening analyzer, preload loss models, and similitude module.

**Legend**:
- ✅ **IN FOLDER** — file exists in `Models/CALIBRATION_AND_VALIDATION/`; quantitative digitized data available
- 🌐 **WEB** — found via literature search; not yet in folder; full citation provided
- ⭐ **RECOMMENDED** — best candidate for that condition based on data richness and BAS relevance

---

## HOW TO USE THIS DOCUMENT

For each condition, two or more papers are listed. Review the "Key data for BAS" column and the notes, then mark which ones you want to add to the validation suite. Priority tiers:

| Tier | Meaning |
|------|---------|
| **1 — Calibrate** | Use to tune free parameters (`C_loosening`, `mu_initial`, etc.) |
| **2 — Validate** | Use to verify frozen parameters against independent data |
| **3 — Extended** | Specialized phenomena; qualitative or boundary-case check |

---

## CONDITION A — Transverse (Shear) Loading, Single Bolt

*Core Junker-type test. Dominant loosening mechanism. Already well covered.*

| # | Paper | File | Bolt | F₀ | δ (mm) | f (Hz) | N | Key data | Tier |
|---|-------|------|------|----|--------|--------|---|----------|------|
| A1 ⭐ | Lu et al. (2024), *Sensors* 24(11):3306 | ✅ `01_Lu_2024_M8_tangential_parametric.md` | M8×1.25 | 2–15 kN | 0.25–2.0 | 1–3 | 50–1000 | 14 configs; F/F₀ vs N digitized | 1 |
| A2 ⭐ | Jiang, Zhang et al. (2003/2004), *ASME J. Mech. Des.* | ✅ `02_Jiang_2003_2004_M12_early_stage.md` | M12×1.75 | 10–41 kN | 0.25–1.27 | 5 | 50–500 | Stage I/II separation; glued-nut; >100 specimens | 1 |
| A3 | Housari & Nassar (2007), *J. Vib. Acoust.* | ✅ `04_Housari_Nassar_2007_friction_effects.md` | M10 | — | varied | varied | varied | μ sweep: 0.05–0.30; loosening vs. friction | 1 |
| A4 | Yang & Nassar (2011), *J. Vib. Acoust.* | ✅ `06_Yang_Nassar_2011_cap_screw.md` | 5/16″-24 UNC | — | varied | varied | varied | Cap screw; analytical + experimental | 2 |
| A5 | Yang et al. (2023), *IJPEM* | ✅ `10_Yang_2023_phenomenological_model.md` | M6, M8 | — | varied | varied | varied | Power-law phenomenological model; R²>0.95 | 2 |
| A6 | Hattori, Yamashita, Mizuno (2010), *EPJ Web Conf.* | ✅ `11_Hattori_2010_critical_slippage.md` | M6, M10, M16 | — | varied | varied | varied | Critical slippage; reaction moments; size effect | 2 |

**Notes**: A1 and A2 are the primary calibration papers. A6 provides the critical slippage (threshold amplitude) validation.

---

## CONDITION B — Axial (Pulsating Tension) Loading

*Pure tension-tension or tension-compression cyclic loading along bolt axis. Different mechanism from transverse.*

| # | Paper | File | Bolt | F₀ | F_ax | f (Hz) | N | Key data | Tier |
|---|-------|------|------|----|------|--------|---|----------|------|
| B1 ⭐ | Liu et al. (2017), *Tribology Int.*, Vol. 115, pp. 432–451. DOI: 10.1016/j.triboint.2017.05.037 | 🌐 | M10×1.5 (8.8) | 10–25 kN | 0.5–3 kN ampl. | 10 | 2000 | F/F₀ vs N; MoS₂ coating; two-stage non-rotational loss quantified | 2 |
| B2 ⭐ | Liu, Ouyang et al. (2016), *Wear* 346–347:66–77 | ✅ `51_52_53_54_axial_fatiguewear_noload_energy.md` | M10×1.5 (8.8) | 13.5–14.5 kN | 7.5 kN, 12.5 kN | 10 | 5000 | Axial excitation; repeated tightening cycles; 34% loss at F_ax/F₀=0.89 | 2 |
| B3 | Cai, Fang, Liu, Ouyang (2016), *Wear* 346–347:29–38. DOI: 10.1016/j.wear.2015.10.013 | 🌐 | M10×1.5 | 20 kN | 2 kN ampl. | varied | 1000 | 15% preload loss; FEA ±10%; thread damage SEM | 2 |
| B4 | Izumi, Yokoyama, Sakai (2005–2011), JST/JSME | ✅ `16_Izumi_Sakai_Japanese_studies.md` | M10, M16 | — | varied | varied | varied | FEA thread slip under axial load; mechanism study | 3 |

**Notes**: B1 is the richest experimental dataset for pure axial loosening with quantitative F/F₀ curves. B2 is already in the folder. The 3-stage axial model in BAS (`_classify_phase_axial()`) needs B1 and B2 for validation.

---

## CONDITION C — Combined Axial + Transverse Loading

*Interaction between axial and transverse force components. Competitive failure: loosening vs. fatigue fracture.*

| # | Paper | File | Bolt | Loading | Key data | Tier |
|---|-------|------|------|---------|----------|------|
| C1 ⭐ | Yang et al. (2021), *Chinese J. Mech. Eng.* 34, Art. 12. DOI: 10.1186/s10033-021-00663-3 | ✅ `13_Yang_2021_combined_loading.md` | M8×1.25 (8.8) | Trans + axial, varied ratio ξ = F_trans/F_axial | Failure mode boundary: loosening vs. fatigue; ξ_critical = 0.075 mm/kN | 2 |
| C2 ⭐ | Yang, Nassar, Wu (2021), *Shock and Vibration* 2021:1441122. DOI: 10.1155/2021/1441122 | 🌐 | M8×1.25 (8.8) | Biaxial; R_axial varied | R as sole failure-mode determinant; stress ratio × transverse amplitude map | 2 |
| C3 | Zhang, Jiang, Lee (2006), *ASME J. Press. Vessel Technol.* 128(3):388. DOI: 10.1115/1.2217972 | ✅ `03_Zhang_Jiang_2006_clamped_length.md` | M12×1.75 | Transverse + oblique (bending component) | Clamped length + loading direction; F/F₀ vs N for 3 grip lengths | 2 |
| C4 | Liu, Mi et al. (2021), *Eng. Fail. Anal.* 119:104985. DOI: 10.1016/j.engfailanal.2020.104985 | 🌐 | M8–M12 | Torsional excitation with varying mean-to-alternating ratio (R in torsion) | Three clamping force evolution patterns; GA-BP prediction model | 3 |

**Notes**: C1 and C2 are the same experimental group (Yang et al.) with complementary data. C1 is already in the folder. C2 provides the stress ratio R perspective which feeds into BAS `R_factor` VDI field. The failure mode boundary ξ_critical = 0.075 mm/kN is directly implementable as a BAS check.

---

## CONDITION D — Bending Loading

*Cyclic bending moment applied to the clamped structure or bolt flange. Distinct from pure transverse shear. NOT yet in folder.*

| # | Paper | File | Bolt | Setup | Key data | Tier |
|---|-------|------|------|-------|----------|------|
| D1 ⭐ | Ishimura, Sawa, Karami, Nagao (2010), *ASME PVP2010*, pp. 405–413. DOI: 10.1115/PVP2010-25326 | 🌐 | Flanged specimens | Repeated bending moments on bolted flange; FEM validation | Loosening mechanism under bending identified (distinct from Junker): bearing surface gross sliding from contact pressure redistribution | 3 |
| D2 ⭐ | Wei, Cheng et al. (2025), *Polymer Composites*. DOI: 10.1002/pc.70915 | 🌐 | CFRP single bolt | Controlled bending vibration; ultrasonic preload monitoring; SEM + profilometry | Two-stage loss: 18% rapid (embedding) + 5% slow (fretting); 4 simultaneous wear mechanisms identified | 3 |
| D3 | Yokoyama, Olsson, Izumi, Sakai (2012), *Eng. Fail. Anal.* 23:35–43. DOI: 10.1016/j.engfailanal.2012.01.010 | 🌐 | M10 (est.) | Rotary bending on disk-bolt-shaft; 3D FEM | Elastic torsion spring-back as primary driver under rotary bending; loosening at lower force than Junker theory | 3 |
| D4 | Mazzola, Johnson et al. (2020), *IMAC XXXVIII*, Springer pp. 191–199. OSTI: 1642845 | 🌐 | Instrumented (Sandia) | Modal excitation of C-beam; bending-dominant mode shape | Resonance bending → slip amplitude amplified by Q-factor; rapid preload loss at sub-threshold forcing | 3 |

**Notes**: Bending is the largest gap in the current library. D1 is the best starting point for flanged joints. D4 (Sandia C-beam) is the most rigorous experimental demonstration of resonance-bending coupling. These are Tier 3 (qualitative/trend) for BAS since the MSD model does not yet include bending DOF.

---

## CONDITION E — Torsional Loading (Structure Twisted, Not Bolt Rotated)

*The clamped structure is twisted cyclically. Different physics from Junker transverse shear. NOT yet in folder.*

| # | Paper | File | Bolt | Setup | Key data | Tier |
|---|-------|------|------|-------|----------|------|
| E1 ⭐ | Liu, Ouyang, Feng et al. (2019), *Tribology Int.* 140:105877. DOI: 10.1016/j.triboint.2019.105877 | 🌐 | M12 (8.8) | Custom torsional rig; sinusoidal twist; F monitored | Hysteresis loop shape transition (elliptical→polygon) = slip regime indicator; torsional loosening is step-function event | 2 |
| E2 ⭐ | Liu, Ouyang, Peng et al. (2018), *Tribology Int.* 127:226–236. DOI: 10.1016/j.triboint.2018.06.021 | 🌐 | M12 (8.8) | Same rig; 0.5°–5° amplitude; 3 preload levels | 3 clamping-force evolution patterns; μ_bearing > μ_thread → stable (opposite of transverse Junker) | 2 |
| E3 | Liu, Fan et al. (2022), *Tribology Int.* 174:107764. DOI: 10.1016/j.triboint.2022.107764 | 🌐 | M12 | Torsional + wear coupling; SEM post-test | Fretting wear reduces μ → triggers secondary loosening acceleration; wear-loosening coupling under torsion | 3 |

**Notes**: E1 and E2 are from the same productive group (Chongqing University / Liverpool group) with consistent apparatus. A `'torsional'` loading type in BAS `_classify_phase()` would be validated against E1 and E2. Key insight: bearing friction > thread friction = torsionally stable — the OPPOSITE sensitivity from transverse loading.

---

## CONDITION F — High-Frequency and Random Vibration Loading

*Frequencies >50 Hz; broadband random PSD; sine-on-random. Partially covered in folder.*

| # | Paper | File | Bolt | Frequency | Loading | Key data | Tier |
|---|-------|------|------|-----------|---------|----------|------|
| F1 ⭐ | Du, Qiu et al. (2022), *Eng. Fail. Anal.* 133:105954. DOI: 10.1016/j.engfailanal.2021.105954 | 🌐 | M8×1.25 (4-bolt) | Broadband random PSD | Triaxial random vibration | Three-stage criterion (Steady/Transition/Loosen) from strain amplitude evolution; reproducible across PSD shapes | 2 |
| F2 ⭐ | Du, Qiu, Li (2025), *Machines* 13(2):80. DOI: 10.3390/machines13020080 | ✅ `33_Du_Qiu_2025_sine_on_random_vibration.md` | M8×1.25 (4-bolt) | 15–1000 Hz SOR | Sine-on-random; PSD 0.2 g²/Hz | Time-to-Loosen: <60 s at 10 N·m vs >300 s at 30 N·m; 3-stage criterion under SOR | 2 |
| F3 | Hess (2018), *NASA/TM-2018-219775*. NTRS: 20180002978 | ✅ `19_Sandia_NASA_reports.md` | Aerospace (≈M4.8) | 20–2000 Hz broadband | Random vibration qualification | 50% preload loss despite safety wire; forensic investigation; demonstrates thread friction insufficient for small bolts | 3 |
| F4 | Tang, Wang et al. (2025), *Agriculture (MDPI)* 15(7):749. DOI: 10.3390/agriculture15070749 | 🌐 | M8–M12 (est.) | 5–25 Hz + harmonics to >100 Hz | Combine harvester vibrating screen | Critical threshold: P_bolt=78.4 N, torque=0.5 N·m; multi-frequency accelerates loosening vs. single-freq Junker | 3 |

**Notes**: F1 and F2 are the most complete experimental treatments of random and SOR loosening. F2 is already in the folder. F1 provides the pure-random baseline that F2 builds upon — they should be used together.

---

## CONDITION G — Variable Amplitude (D-N Loosening Life Curves)

*Analogous to S-N fatigue curves. Displacement amplitude vs. loosening life cycles. Miner's rule applicability.*

| # | Paper | File | Bolt | Key data | Tier |
|---|-------|------|------|----------|------|
| G1 ⭐ | Yang et al. (2019), *Shock and Vibration* 2019:2036509. DOI: 10.1155/2019/2036509 | ✅ `09_Yang_2019_M10_variable_amplitude.md` | M10 (8.8) | D-N loosening life curves; Miner's rule; two-block loading prediction within ±20% | 2 |
| G2 ⭐ | Yang, Jeong et al. (2025), *Appl. Sciences / Sci. Rep.* PMC:11901137 | ✅ `26_Yang_Jeong_2025_variable_amplitude_multibolt.md` | M10–M12 multi-bolt | Variable amplitude multi-bolt; non-proportional loosening rates; practical loosening life framework | 2 |
| G3 | Du et al. (2025), *Machines* 13(2):80 | ✅ `33_Du_Qiu_2025_sine_on_random_vibration.md` | M8×1.25 | SOR three-stage; preload retention vs. tightening torque | 3 |

**Notes**: G1 and G2 directly validate BAS `MinersRuleAccumulator` and the D-N curve generation in `coupled_loosening_analyzer.py`. G1 also checks the D-N exponent m which must be within 0.5 of experimental (per the validation plan).

---

## CONDITION H — Load Ratio R (Stress Ratio, Fatigue-Loosening Boundary)

*R = F_min/F_max for pulsating loads. The VDI 2230 `R_factor` parameter in BAS. NOT well covered in folder yet.*

| # | Paper | File | Bolt | R range tested | Key data | Tier |
|---|-------|------|------|---------------|----------|------|
| H1 ⭐ | Yang, Nassar, Wu (2021), *Chinese J. Mech. Eng.* 34:12. DOI: 10.1186/s10033-021-00663-3 | ✅ `13_Yang_2021_combined_loading.md` | M8 (8.8) | ξ (load ratio) 0.025–0.15 mm/kN | Failure mode boundary: loosening dominates above ξ_critical = 0.075 mm/kN; below → fatigue fracture | 2 |
| H2 ⭐ | Yang, Nassar, Wu (2021), *Shock and Vibration* 2021:1441122. DOI: 10.1155/2021/1441122 | 🌐 | M8 (8.8) | R_axial = -1, 0, 0.1, 0.5 | R_axial = -1 most aggressive (tensile-compressive); interaction of R with transverse amplitude mapped | 2 |
| H3 | Liu, Mi et al. (2021), *Eng. Fail. Anal.* 129:105697. DOI: 10.1016/j.engfailanal.2021.105697 | 🌐 | M8–M12 | Multiple preload levels, R varied | Confirms R as sole failure-mode determinant across 5 preload levels and 3 amplitudes | 2 |

**Notes**: H1 is already in the folder under `13_`. H2 is the essential companion paper (stress ratio R of axial component). The combination H1+H2 fully characterizes the failure mode map as a function of R_axial × ξ_transverse — directly relevant to the BAS `R_factor` field in `LoadingData`.

---

## CONDITION I — Frequency Effects (f as Independent Variable)

*Frequency varied explicitly while displacement amplitude is held constant. Tests whether loosening rate depends on frequency or only on displacement.*

| # | Paper | File | Bolt | f range | Key finding | Tier |
|---|-------|------|------|---------|------------|------|
| I1 ⭐ | Lu et al. (2024), *Sensors* 24(11):3306 | ✅ `01_Lu_2024_M8_tangential_parametric.md` | M8×1.25 | 1, 2, 3 Hz | Frequency has minor effect at constant amplitude; loosening rate governed by displacement | 1 |
| I2 ⭐ | Sanclemente & Hess (2007), *Eng. Fail. Anal.* 14(1):239–249. DOI: 10.1016/j.engfailanal.2005.11.021 | ✅ `24_Sanclemente_Hess_2007_DOE_factorial.md` | 1/4-20 UNC | 5 Hz (fixed); ANOVA ranking | ANOVA ranking: amplitude > pitch > preload > μ_bearing > μ_thread > diameter > frequency (negligible) | 2 |
| I3 | Yang et al. (2019), *Shock and Vibration* 2019:2036509 | ✅ `09_Yang_2019_M10_variable_amplitude.md` | M10 | 5 vs 12.5 Hz | Equivalent at same displacement → frequency effect minimal | 2 |

**Notes**: Literature consensus is that frequency has negligible effect on loosening at constant displacement amplitude. I2 (Sanclemente DOE) provides the definitive ANOVA ranking. BAS must reproduce this ranking in its sensitivity analysis to pass validation.

---

## CONDITION J — Pitch and Thread Geometry Effects

*Thread pitch, helix angle, number of engaged threads, thread fit/clearance as variables.*

| # | Paper | File | Bolt | Variables | Key data | Tier |
|---|-------|------|------|-----------|----------|------|
| J1 ⭐ | Nassar & Housari (2006), *ASME J. Press. Vessel Technol.* 128(4):590. DOI: 10.1115/1.2349572 | ✅ `07_Nassar_Housari_2006_pitch_preload.md` | M8, M10; UNF vs UNC | Pitch (fine vs coarse); preload 50–90% yield | Fine thread: 30–40% more cycles to same loss; helix angle is primary variable | 2 |
| J2 ⭐ | Nassar & Housari (2007), *J. Mech. Des.* | ✅ `08_Nassar_Housari_2007_clearance_fit.md` | M10 | Hole clearance 3–10%; thread fit 1B–3B | Clearance and fit effects quantified | 2 |
| J3 | Pai & Hess (2002), *J. Sound Vib.* 253(3):585–602. DOI: 10.1006/jsvi.2001.4006 | 🌐 | 5/16-18 UNC + 5/16-24 UNF | Fine vs. coarse; 4 slip classification types | Fine thread: 25–35% higher shear force to initiate rotational loosening; localized vs gross slip classification | 2 |
| J4 | Pai & Hess (2002), *Eng. Fail. Anal.* 9(4):383. DOI: 10.1016/S1350-6307(01)00024-3 | 🌐 | 5/16-18 UNC (3D FEA) | Helix angle explicitly modeled; 6 engaged threads | >60% load on first 2 threads; helix angle without 3D FEA underestimates loosening by 40% | 3 |

**Notes**: J1 and J2 are already in the folder. J3 (Pai-Hess 2002 experimental) should be added as it provides the fine/coarse comparison with quantitative data for a UNC bolt size also used in J2. J3 is also the original paper for the 4-slip-classification taxonomy used in BAS `compute_fretting_regime()`.

---

## CONDITION K — Preload Level Effects (% Yield)

*Initial preload as % of proof/yield load. Critical for calibrating Stage I saturation.*

| # | Paper | File | Bolt | Preload range | Key data | Tier |
|---|-------|------|------|--------------|----------|------|
| K1 ⭐ | Lu et al. (2024), *Sensors* 24(11):3306 | ✅ `01_Lu_2024_M8_tangential_parametric.md` | M8×1.25 | 2,105 / 7,886 / 11,567 / 14,007 / 15,027 N (5 levels) | Full parametric sweep; all other parameters fixed | 1 |
| K2 ⭐ | Jiang et al. (2004), *ASME J. Mech. Des.* 126(5):925. DOI: 10.1115/1.1767814 | ✅ `02_Jiang_2003_2004_M12_early_stage.md` | M12×1.75 | 25 kN vs. 41 kN (standard vs. high preload) | Higher preload delays Stage II onset; Stage I fraction increases | 1 |
| K3 | Housari & Nassar (2007), *J. Vib. Acoust.* | ✅ `04_Housari_Nassar_2007_friction_effects.md` | M10 | 50%, 70%, 90% yield | Interaction with friction coefficient; preload + friction crossing effects | 1 |

**Notes**: Preload effects are the second-most important calibration variable after amplitude. All three papers are already in the folder. Adequate coverage.

---

## CONDITION L — Clamped Length / Grip Ratio Effects

*Bolt grip length (clamped member thickness) as a variable.*

| # | Paper | File | Bolt | L_grip range | Key data | Tier |
|---|-------|------|------|-------------|----------|------|
| L1 ⭐ | Zhang, Jiang, Lee (2006), *ASME J. Press. Vessel Technol.* 128(3):388. DOI: 10.1115/1.2217972 | ✅ `03_Zhang_Jiang_2006_clamped_length.md` | M12×1.75 | 25, 38, 51, 68 mm | F/F₀ vs N for 4 grip lengths; longer grip → more cycles to Stage II onset | 2 |
| L2 ⭐ | Rousseau & Bouzid (2025), *Materials* 18(2):462. DOI: 10.3390/ma18020462 | ✅ `25_Rousseau_Bouzid_2025_material_thickness.md` | M12 | HDPE clamped members | Material-dependent loosening; polymer creep adds to loosening | 3 |

**Notes**: L1 (already in folder) is the definitive clamped length paper. L2 extends to soft clamped members (HDPE polymer) which tests the embedding model. Adequate for this condition.

---

## CONDITION M — Multi-Bolt Flanged Connections Under Vibration

*Groups of bolts; load redistribution; sequential loosening cascade; flange interaction.*

| # | Paper | File | Setup | Bolts | Key data | Tier |
|---|-------|------|-------|-------|----------|------|
| M1 ⭐ | Pai & Hess (2003), *J. Sound Vib.* 268:617–626. DOI: 10.1016/S0022-460X(03)00202-X | 🌐 | Multi-bolt lap joint; bolt pattern varied; aluminum plate | 1/4-20 UNC (≈M6) group | Loosening cascade: edge bolt loosens first → load shift → adjacent bolt loosens faster; multi-bolt ≠ single-bolt | 2 |
| M2 ⭐ | Yang, Jeong et al. (2025), *Sci. Rep. / PMC* PMC:11901137 | ✅ `26_Yang_Jeong_2025_variable_amplitude_multibolt.md` | Multi-bolt structure; variable amplitude | M10–M12 group | Non-proportional loosening rates; multi-bolt loosening life framework | 2 |
| M3 | Sun et al. (2022), *Shock and Vibration* 2022:7844875. DOI: 10.1155/2022/7844875 | 🌐 | Aero-engine 8-bolt circular flange spigot | M6 (8-bolt) | Asymmetric stiffness from partial loosening produces sideband frequencies (detection signature); FEM + exp. | 3 |
| M4 | Coria, Abasolo et al. (2020), *Int. J. Press. Vessels Piping* 182:104054 | ✅ `59_60_61_62_wind_turbine_flange_studies.md` | 12-bolt NPS 4″ class 300 flange | M20×2.5 (10.9) | Preload scatter: star pattern ±25%; circular ±36%; tightening sequence optimization | 2 |
| M5 | Wiegand (2021), *Eng. Fail. Anal.* | ✅ `71_Wiegand_2021_VDI_validation_index.md` | 4-bolt flanged connection | M-series | VDI 2230 load factor validation; eccentric loading effect; VDI overestimates by up to 2x | 2 |

**Notes**: M1 (Pai-Hess 2003 multi-bolt) must be added — it is the foundational experiment for multi-bolt sequential loosening and is NOT yet in the folder. M2 is already in the folder. M5 directly validates the VDI load-factor concept used in BAS.

---

## CONDITION N — Gasket Relaxation and Creep (Static + Cyclic)

*Preload loss from gasket deformation. Separate from rotational loosening. Non-rotational mechanism.*

| # | Paper | File | Gasket | Loading | Key data | Tier |
|---|-------|------|--------|---------|----------|------|
| N1 ⭐ | Nechache & Bouzid (2007), *ASME J. Press. Vessel Technol.* | ✅ `30_Nechache_Bouzid_2007_creep_flange_joints.md` | Spiral-wound; flexible graphite | Static + cyclic pressure; NPS 3″-52″ | Long-term gasket creep prediction; Norton-Bailey model | 2 |
| N2 ⭐ | Bouzid, Chaaban, Bazergui (1995), *ASME J. Press. Vessel Technol.* 117(1):71. DOI: 10.1115/1.2842093 | 🌐 | Spiral-wound + flex. graphite | Static compression + 200°C thermal | 20–60% preload loss; viscoelastic model validated | 2 |
| N3 | Bouzid & Nechache (2006), *ASME J. Press. Vessel Technol.* 128(3):394. DOI: 10.1115/1.2218343 | 🌐 | SBR rubber 3 mm; aramid 3 mm; flex. graphite | Elastic interaction + creep combined | Aramid: 30% preload loss under ambient compression; elastic interaction alone = 10–30% | 2 |
| N4 | Abid & Nash (2014), *IIUM Eng. J.* 15(2) | 🌐 | Spiral-wound (NPS 4″, M20) | Cyclic pressure 1–10 Hz | 3%/100 cycles drift under cyclic pressure; frequency-dependent drift rate | 3 |

**Notes**: N1 is already in the folder. N2 and N3 are the foundational Bouzid papers that underpin N1 — they should be added to provide the constitutive viscoelastic model that BAS `NortonBaileyCreepModel` is based on.

---

## CONDITION O — Large Bolt Scaling (M20–M64)

*Size effects; geometry scaling; wind turbine / offshore bolts.*

| # | Paper | File | Bolt range | Key data | Tier |
|---|-------|------|-----------|----------|------|
| O1 ⭐ | Karlsen & Lemu (2022), *Proc. IMechE Part E* | ✅ `29_Karlsen_Lemu_2022_large_bolt_M20_M42.md` | M20, M30, M42 | Proportionally scaled test series; quantitative F/F₀ for all 3 sizes | 2 |
| O2 ⭐ | Wind turbine flange studies (Coria, Dong et al.) | ✅ `59_60_61_62_wind_turbine_flange_studies.md` | M20–M36 | Tightening sequences; operational loosening; large flange | 3 |
| O3 | Schaumann & Lochte-Holtgreven (2015), *ISOPE*. DOI: (OnePetro) | 🌐 | M36, M64 | VDI 2230 fatigue overestimates by 25% for M64; zinc coating −10–15% fatigue life | 2 |

**Notes**: O1 is the ideal calibration case for geometric scaling in BAS Similitude tab (see S1 in folder). O3 provides the size-effect evidence that BAS should flag for bolts > M30.

---

## CONDITION P — Small Bolts (M3–M6, Precision/Electronics)

*Bolts smaller than M8. Size effects in the opposite direction from large bolts. NOT in folder.*

| # | Paper | File | Bolt | Key data | Tier |
|---|-------|------|------|----------|------|
| P1 ⭐ | Bhattacharya, Sen, Das (2010), *Mech. Mach. Theory* 45(8):1215. DOI: 10.1016/j.mechmachtheory.2008.08.004 | 🌐 | M4, M5, M6 | Direct Junker test on M4/M5; spring washer effect; small bolts disproportionately susceptible; lower self-locking margin | 3 |
| P2 ⭐ | Sanclemente & Hess (2007), *Eng. Fail. Anal.* 14(1):239. DOI: 10.1016/j.engfailanal.2005.11.021 | ✅ `24_Sanclemente_Hess_2007_DOE_factorial.md` | 1/4-20 UNC (≈M6.35) | Parametric ANOVA; loosening threshold scales inversely with diameter at same yield fraction | 2 |
| P3 | NASA/TM-2018-219775 (Hess) | ✅ `19_Sandia_NASA_reports.md` | #10-32 UNF (≈M4.8) | Real failure: 50% preload loss despite safety wire; broadband 20–2000 Hz launch vibration | 3 |

**Notes**: P1 (Bhattacharya 2010) must be added to the folder — it is the ONLY paper that directly tests M4 and M5 bolts under Junker conditions. P2 and P3 are already in the folder.

---

## CONDITION Q — CFRP / Composite Clamped Members

*Viscoelastic creep, anisotropic contact compliance, embedding into polymer matrix. NOT well covered in current folder.*

| # | Paper | File | Member | Key data | Tier |
|---|-------|------|--------|----------|------|
| Q1 ⭐ | Wei, Cheng et al. (2025), *Polymer Composites*. DOI: 10.1002/pc.70915 | 🌐 | CFRP laminate | Bending vibration; ultrasonic preload monitoring; Stage I: 18% rapid embedding; Stage II: 5% fretting | 3 |
| Q2 ⭐ | Yang, An, Chen, Zou (2023), *Adv. Mech. Eng.* 15:1–9. DOI: 10.1177/16878132221145342 | 🌐 | CFRP panel | Biaxial loading; no nut rotation; 70% preload loss from washer embedding; non-rotational dominant | 3 |
| Q3 | Su & Ye (2016), *Composites Part B* Vol. 91:12. (PolyU) | 🌐 | CFRP composite | 1.93 Hz vibration; viscoelastic creep model; logarithmic preload decay; temperature-dependent | 3 |
| Q4 | Eraliev et al. (2021), *Adv. Mech. Eng.* | ✅ `12_Eraliev_2021_thermal_cycling.md` | M12 steel (but thermal + loosening coupling method transferable to CFRP) | Thermal cycling preload loss | 3 |

**Notes**: Q1 and Q2 are the most current and complete CFRP loosening papers. Both are Tier 3 because BAS does not yet have a polymer embedding model. They define the requirements for future development.

---

## CONDITION R — Thermal Loading and High-Temperature Loosening

*Temperature-induced preload loss via CTE mismatch, creep, and stress relaxation.*

| # | Paper | File | Bolt / System | T range | Key data | Tier |
|---|-------|------|--------------|---------|----------|------|
| R1 ⭐ | Eraliev et al. (2021), *Adv. Mech. Eng.* | ✅ `12_Eraliev_2021_thermal_cycling.md` | M12×1.75 | Cyclic ΔT | Preload vs. temperature cycles | 3 |
| R2 ⭐ | Brown et al. (2017), B7/B16 bolts at 385°C | ✅ `47_48_49_50_hightemp_B7_B16_IN718_IN783.md` | B7, B16 (alloy steel) | 385°C | Thermal relaxation; stress relaxation data | 2 |
| R3 | den Otter & Maljaars (2020), *J. Constr. Steel Res.* | ✅ `31_den_Otter_Maljaars_2020_stainless_steel_aluminum.md` | SS bolt / Al member | Ambient to 100°C | CTE mismatch preload loss; SS + Al combination | 3 |
| R4 | Hu, Zhang et al. (2020), *J. Composite Materials* 54(23):3261. DOI: 10.1177/0021998320941218 | 🌐 | CFRP interference-fit | Thermal cycling combined with mech. loading | CTE mismatch (steel vs CFRP) 10× accelerates preload loss | 3 |

**Notes**: Already well-covered in folder. R4 extends to CFRP thermal effects not currently modeled.

---

## CONDITION S — Similitude and Geometric Scaling

*Scale model experiments to predict prototype behavior. Buckingham Pi groups.*

| # | Paper | File | Scale | Key data | Tier |
|---|-------|------|-------|----------|------|
| S1 ⭐ | Karlsen & Lemu (2022) — used as M20→M42 prediction | ✅ `S1_Similitude_Geometric_Scaling_M20_to_M42.md` + `29_Karlsen_Lemu_2022_large_bolt_M20_M42.md` | M20→M42 (scale ratio 1:2.1) | Proportionally scaled conditions; experimental validation of geometric scaling | 2 |
| S2 ⭐ | Multi-bolt reduction (various papers aggregated) | ✅ `S2_Similitude_Multi_Bolt_Reduction_Flanged_Joints.md` | Multi-bolt → single-bolt reduction | Analytical similitude; multi-bolt equivalence | 3 |
| S3 | Li, Luo et al. (2022), *Proc. IMechE Part C* 236(10):5192. DOI: 10.1177/09544062211059736 | 🌐 | Rotor system with bolted flanges (1:3 scale) | Frequency prediction error <5.4% on 1:3 scale model; joint stiffness nonlinearity must be included | 3 |
| S4 | Li, Wen, Luo, Jin (2022), *Mathematics* 10(1):3. DOI: 10.3390/math10010003 | 🌐 | Dual-rotor bolted flange (1:3 scale) | Buckingham Pi for dual-rotor; amplitude and frequency scaling factors; <5% error | 3 |

**Notes**: S1 and S2 are the primary BAS Similitude tab validation cases (already structured). S3 and S4 extend similitude to rotordynamic applications — useful if BAS Similitude tab is extended beyond loosening rate scaling.

---

## CONDITION T — Locking Devices Comparison

*Anti-loosening devices tested under Junker conditions. Relative effectiveness ranking.*

| # | Paper | File | Devices | Test method | Key data | Tier |
|---|-------|------|---------|------------|----------|------|
| T1 ⭐ | DIN 65151 / Nord-Lock / HEICO / Hardlock data | ✅ `18_Junker_test_locking_devices.md` | 8 device types | DIN 65151 Junker | Preload retention curves; Junker effectiveness class A–F | 2 |
| T2 ⭐ | Sase, Koga et al. (1996), *Anti-loosening Nuts* | ✅ `32_Sase_Koga_1996_anti_loosening_nuts_7types.md` | 7 nut types | Junker-type | Relative ranking; step-by-step preload decay | 2 |
| T3 | Zhao, Liu et al. (2023), *Anti-loosening FEA comparison* | ✅ `28_Zhao_Liu_2023_anti_loosening_FEA_comparison.md` | 7 anti-loosening devices | FEA | Relative ranking; mechanism analysis | 3 |
| T4 | Amano (2024), *Double-thread bolt, ISO 16130* | ✅ `35_Amano_2024_double_thread_bolt_ISO16130.md` | Double-thread bolt | ISO 16130 | Residual load rate ≥85% (ISO rating-1) confirmed | 2 |

**Notes**: T1 directly validates the `locking_devices.json` database in BAS. T4 validates the ISO 16130 85% threshold used in `_check_self_lock()`.

---

## CONDITION U — VDI 2230 Load Factor Validation

*Experimental validation of the load introduction factor Φ (phi) and load factor n_phi from VDI 2230.*

| # | Paper | File | System | Key finding | Tier |
|---|-------|------|--------|------------|------|
| U1 ⭐ | Wiegand (2021), *Eng. Fail. Anal.* | ✅ `71_Wiegand_2021_VDI_validation_index.md` | 4-bolt flange | VDI 2230 load factor overestimates by up to 2x for eccentric loading; VDI conservative for symmetric loading | 2 |
| U2 ⭐ | Schaumann & Marten (2009), *NSCC*. PDF from Uni Hannover | 🌐 | M36 bolts (wind turbine) | VDI underestimates size effect; VDI overestimates fatigue limit by 15–20% for M36 | 2 |
| U3 | Schaumann, Lochte-Holtgreven, Steppeler (2015), *ISOPE*. DOI: OnePetro | 🌐 | M36, M64 (offshore WT) | VDI fatigue limit 25% non-conservative for M64; zinc coating −10–15% life | 2 |

**Notes**: U1 is already in the folder. U2 and U3 provide the large-bolt size-effect context. The combined message: VDI 2230 is conservative for symmetric small bolts but non-conservative for M36+ under eccentric loading. BAS should flag this limitation.

---

## SUMMARY: PAPERS TO ADD TO FOLDER (New Acquisitions)

The following papers were found via web search and are recommended for addition as new files in `Models/CALIBRATION_AND_VALIDATION/`. Papers already in the folder are excluded.

### High Priority (Tier 2 — quantitative validation data)

| File # | Paper | Condition | Why add |
|--------|-------|-----------|---------|
| `72_` | Liu et al. (2017), *Tribology Int.* 115:432. DOI: 10.1016/j.triboint.2017.05.037 | B — Axial | Richest axial loosening dataset; two-stage non-rotational with F/F₀ curves; MoS₂ coating |
| `73_` | Yang, Nassar, Wu (2021), *Shock Vib.* 2021:1441122. DOI: 10.1155/2021/1441122 | H/C — Load ratio R | Stress ratio R_axial as failure mode determinant; companion to `13_Yang_2021` |
| `74_` | Pai & Hess (2003), *J. Sound Vib.* 268:617. DOI: 10.1016/S0022-460X(03)00202-X | M — Multi-bolt | First multi-bolt loosening cascade experiment; bolt-group interaction; ESSENTIAL gap |
| `75_` | Bouzid, Chaaban, Bazergui (1995), *ASME J. PVT* 117(1):71. DOI: 10.1115/1.2842093 | N — Gasket creep | Foundational gasket creep paper; viscoelastic model calibration reference |
| `76_` | Bouzid & Nechache (2006), *ASME J. PVT* 128(3):394. DOI: 10.1115/1.2218343 | N — Gasket creep | Elastic interaction + creep combined; quantitative |
| `77_` | Du, Qiu et al. (2022), *Eng. Fail. Anal.* 133:105954. DOI: 10.1016/j.engfailanal.2021.105954 | F — Random vib. | Three-stage loosening criterion under pure random vibration; companion to `33_Du_Qiu_2025` |
| `78_` | Liu, Ouyang, Peng et al. (2018), *Tribology Int.* 127:226. DOI: 10.1016/j.triboint.2018.06.021 | E — Torsional | Best quantitative torsional loosening data; 3 clamping-force evolution patterns; M12 |
| `79_` | Liu, Ouyang, Feng et al. (2019), *Tribology Int.* 140:105877. DOI: 10.1016/j.triboint.2019.105877 | E — Torsional | Hysteresis loop shape as slip indicator; follow-on to `78_` |

### Medium Priority (Tier 3 — qualitative or specialized phenomena)

| File # | Paper | Condition | Why add |
|--------|-------|-----------|---------|
| `80_` | Bhattacharya, Sen, Das (2010), *Mech. Mach. Theory* 45(8):1215 | P — Small bolts | ONLY paper with M4/M5 Junker tests; spring washer data |
| `81_` | Ishimura, Sawa, Karami, Nagao (2010), *ASME PVP2010-25326* | D — Bending | Flanged joint bending moment loosening; distinct mechanism from Junker |
| `82_` | Wei, Cheng et al. (2025), *Polymer Composites*. DOI: 10.1002/pc.70915 | Q/D — CFRP bending | Most recent CFRP loosening under bending vibration; two-stage quantified |
| `83_` | Yang, An, Chen, Zou (2023), *Adv. Mech. Eng.* 15. DOI: 10.1177/16878132221145342 | Q — CFRP | Non-rotational dominant in CFRP; washer embedding quantified (70% of total loss) |
| `84_` | Schaumann & Marten (2009), NSCC. + Schaumann et al. (2015), ISOPE | U — VDI validation | Large bolt VDI 2230 non-conservatism; size effect experimental proof |
| `85_` | Mazzola, Johnson et al. (2020), *IMAC XXXVIII*. OSTI:1642845 | D/F — Bending resonance | Sandia C-beam; resonance bending → preload loss without high force |

---

## VALIDATION SUITE RECOMMENDATION (Minimum Set)

If you can only pick one set of papers per condition for code validation, here is the recommended minimum:

| Condition | Use for BAS | Paper(s) to use | Current status |
|-----------|------------|-----------------|----------------|
| Transverse (calibration) | `C_loosening`, `lambda_stage1` | A1 (Lu 2024) + A2 (Jiang 2003) | ✅ In folder |
| Axial loosening | `_classify_phase_axial()` | B1 (Liu 2017) + B2 (Liu 2016) | 🌐 B1 new; ✅ B2 in folder |
| Combined / load ratio R | `R_factor` in VDI fields | C1 (Yang 2021) + H2 (Yang 2021 Shock Vib) | ✅ C1; 🌐 H2 new |
| Variable amplitude / Miner | `MinersRuleAccumulator` | G1 (Yang 2019) + G2 (Yang 2025) | ✅ Both in folder |
| Frequency as variable | `dynamic_factor` in VDI | I2 (Sanclemente ANOVA) | ✅ In folder |
| Pitch / thread geometry | Thread params in analyzer | J1 (Nassar 2006) + J3 (Pai 2002) | ✅ J1; 🌐 J3 new |
| Multi-bolt cascade | Future multi-bolt mode | M1 (Pai 2003) + M2 (Yang 2025) | 🌐 M1 new; ✅ M2 in folder |
| Gasket creep (cyclic) | `NortonBaileyCreepModel` | N1 (Nechache 2007) + N2 (Bouzid 1995) | ✅ N1; 🌐 N2 new |
| Large bolt scaling | Similitude tab | O1 (Karlsen 2022) | ✅ In folder |
| Locking devices | `locking_devices.json` | T1 (DIN 65151) + T4 (Amano ISO 16130) | ✅ Both in folder |
| VDI 2230 validation | `Phi_load` in LoadingData | U1 (Wiegand 2021) | ✅ In folder |
| Torsional loading | New `'torsional'` loading type | E1 (Liu 2019) + E2 (Liu 2018) | 🌐 Both new |
| Bending loading | Future bending DOF | D1 (Ishimura 2010) | 🌐 New |
| CFRP members | Future polymer embedding | Q2 (Yang 2023) | 🌐 New |
| Random vibration | `load_waveform = 'random'` | F1 (Du 2022) + F2 (Du 2025) | 🌐 F1 new; ✅ F2 in folder |

---

*End of document — Total conditions covered: 21 | Papers listed: 68 | Already in folder: 38 | New (web-sourced): 30*
