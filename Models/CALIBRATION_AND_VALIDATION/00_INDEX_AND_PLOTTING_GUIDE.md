# Self-Loosening & Preload Loss Data Library — Master Index

## Purpose
This library contains detailed quantitative data extracted from published studies on bolt self-loosening and preload loss. Each file corresponds to one or more papers from a research group, organized to enable direct curve reproduction and experimental setup replication.

---

## File Index

| File | Study / Source | Bolt Size | Loading Type | Key Curves |
|---|---|---|---|---|
| `01_Lu_2024_M8_tangential_parametric.md` | Lu et al. (2024), Sensors 24(11):3306 | M8×1.25 | Transverse cyclic | Preload decay vs. cycles (5 torques, 5 amplitudes, 3 roughnesses, 3 frequencies) |
| `02_Jiang_2003_2004_M12_early_stage.md` | Jiang, Zhang et al. (2003/2004), ASME J. Mech. Des. | M12×1.75 | Transverse displacement | Early-stage + full loosening; >100 specimens |
| `03_Zhang_Jiang_2006_clamped_length.md` | Zhang, Jiang et al. (2006), J. Press. Vessel Technol. | M12×1.75 | Transverse + combined | Clamped length and loading direction effects |
| `04_Housari_Nassar_2007_friction_effects.md` | Housari & Nassar (2007), J. Vib. Acoust. | M10 (model) | Transverse cyclic | Friction coefficient parametric sweeps |
| `05_Nassar_Yang_2009_math_model.md` | Nassar & Yang (2009), J. Vib. Acoust. | General | Transverse harmonic | Nonlinear mathematical model with equations |
| `06_Yang_Nassar_2011_cap_screw.md` | Yang & Nassar (2011), J. Vib. Acoust. | 5/16"-24 | Transverse cyclic | Cap screw analytical + experimental |
| `07_Nassar_Housari_2006_pitch_preload.md` | Nassar & Housari (2006), J. Press. Vessel Technol. | M8, M10 | Transverse cyclic | Pitch and preload effects |
| `08_Nassar_Housari_2007_clearance_fit.md` | Nassar & Housari (2007), J. Mech. Des. | M10 | Transverse cyclic | Hole clearance (3–10%) and thread fit (1B–3B) |
| `09_Yang_2019_M10_variable_amplitude.md` | Yang et al. (2019), Shock and Vibration | M10 | Transverse variable | D-N loosening life curves; Miner's rule |
| `10_Yang_2023_phenomenological_model.md` | Yang, Jeong & Lim (2023), IJPEM | M6, M8 | Transverse (Junker) | Phenomenological power-law model |
| `11_Hattori_2010_critical_slippage.md` | Hattori, Yamashita, Mizuno (2010), EPJ Web Conf. | M6, M10, M16 | Transverse cyclic | Critical slippage data; reaction moments |
| `12_Eraliev_2021_thermal_cycling.md` | Eraliev et al. (2021), Adv. Mech. Eng. | M12×1.75 | Thermal cycling | Preload vs. temperature cycles |
| `13_Yang_2021_combined_loading.md` | Yang et al. (2021), Chinese J. Mech. Eng. | M8×1.25 | Transverse + axial | Competitive failure: loosening vs. fatigue |
| `14_Dinger_Friedrich_2011_FEA.md` | Dinger & Friedrich (2011/2016), Eng. Fail. Anal. | M10×1.5 | Transverse FEA | Local contact state parameter η_n |
| `15_Chen_2017_tightening_process.md` | Chen et al. (2017), Shock and Vibration | M12×1.75 | Transverse FEA | Tightening process effects on loosening |
| `16_Izumi_Sakai_Japanese_studies.md` | Izumi, Yokoyama, Sakai (2005–2011), JST/JSME | M10, M16 | Transverse + axial | FEA thread slip; axial loosening mechanism |
| `17_Eccles_2010_tribological.md` | Eccles (2010), PhD Thesis, UCLan | M8, M10, M12 | Transverse (Junker) | Friction evolution; coating effects; prevailing torque nut failure |
| `18_Junker_test_locking_devices.md` | Compiled from DIN 25201-4, Nord-Lock, HEICO, Hardlock | M8, M10, M12 | Transverse (DIN 65151) | Locking device comparison curves |
| `19_Sandia_NASA_reports.md` | SAND2019-12525C; NASA/TP-2018-219787 | SAE Gr.9; various | Modal excitation; vibration | Government test data |
| `20_Gong_Liu_2018_2019_FEA_factors.md` | Gong, Liu, Ding (2018/2019), Proc. IMechE C / SAGE | M12 | Transverse FEA | Parametric: pitch, clearance, friction, preload |
| `21_reference_bolt_properties.md` | VDI 2230, DIN, ISO, ASTM compiled | M6–M42 | — | Preload tables, friction tables, material properties |
| `22_mathematical_models_summary.md` | Compiled from all sources | — | — | All equations needed for curve generation |
| `23_Pai_Hess_2002_cap_screw_inserts.md` | Pai & Hess (2002), J. Sound Vib. | 5/16″-24 | Transverse dynamic shear | Cap screw inserts; 4 loosening process types |
| `24_Sanclemente_Hess_2007_DOE_factorial.md` | Sanclemente & Hess (2007), Eng. Fail. Anal. | 1/4-20 UNC | Transverse cyclic | DOE factorial; ANOVA factor rankings |
| `25_Rousseau_Bouzid_2025_material_thickness.md` | Rousseau & Bouzid (2025), Materials | M12 | Transverse; HDPE members | Clamped member material and thickness effects |
| `26_Yang_Jeong_2025_variable_amplitude_multibolt.md` | Yang, Jeong et al. (2025), Sci. Rep. | M10–M12 | Variable amplitude, multi-bolt | Non-proportional loosening; multi-bolt life framework |
| `27_Li_Liu_2020_directional_vibration_relaxation.md` | Li & Liu (2020), various | M10 | Axial vs. transverse | Directional vibration comparison |
| `28_Zhao_Liu_2023_anti_loosening_FEA_comparison.md` | Zhao, Liu et al. (2023), Eng. Fail. Anal. | M-series | Transverse FEA | 7 anti-loosening devices; FEA ranking |
| `29_Karlsen_Lemu_2022_large_bolt_M20_M42.md` | Karlsen & Lemu (2022), Proc. IMechE E | M20, M30, M42 | Transverse (Junker scaled) | Proportionally scaled tests; size effect |
| `30_Nechache_Bouzid_2007_creep_flange_joints.md` | Nechache & Bouzid (2007), ASME J. PVT | M12 (NPS flanges) | Static + cyclic pressure | Gasket creep; Norton-Bailey; long-term |
| `31_den_Otter_Maljaars_2020_stainless_steel_aluminum.md` | den Otter & Maljaars (2020) | SS bolt / Al member | Thermal cycling | CTE mismatch preload loss |
| `32_Sase_Koga_1996_anti_loosening_nuts_7types.md` | Sase, Koga et al. (1996), JSME | M-series | Transverse (Junker) | 7 nut types; relative effectiveness ranking |
| `33_Du_Qiu_2025_sine_on_random_vibration.md` | Du, Qiu, Li (2025), Machines 13(2):80 | M8×1.25 (4-bolt) | Sine-on-random, 15–1000 Hz | 3-stage criterion; tightening torque effect |
| `34_Amano_2024_double_thread_bolt_ISO16130.md` | Amano (2024), Heliyon | M8, M10 | ISO 16130 Junker test | Double-thread bolt; residual axial load ≥85% |
| `35_36_37_38_wear_material_rotational_direction.md` | Zhang 2019 FEA + others | M10–M16 | Transverse FEA | Wear depth; material; rotational direction effects |
| `39_40_41_42_locking_AI_deepsea_3Dprint.md` | Various 2020–2023 | Various | Various | Locking AI; deep-sea; 3D-printed fasteners |
| `43_44_45_46_jackbolt_washer_doublenut_pitch.md` | Various | M-series | Transverse | Jackbolts; washers; double nut; pitch variations |
| `47_48_49_50_hightemp_B7_B16_IN718_IN783.md` | Brown 2017 + others | B7, B16 alloy steel; IN718 | High temperature (up to 650°C) | Thermal relaxation data; stress relaxation |
| `51_52_53_54_axial_fatiguewear_noload_energy.md` | Liu, Ouyang et al. 2016 + others | M10 | Axial excitation; wear | Axial loosening; repeated tightening cycles; SEM |
| `55_56_57_58_GPR_Iwan_reliability_arclock.md` | Various | Various | Various | GPR prediction; Iwan model; reliability |
| `59_60_61_62_wind_turbine_flange_studies.md` | Coria 2020 + others | M20 (12-bolt NPS 4) | Multi-bolt flange | Tightening sequence; preload scatter |
| `63_64_65_66_thermal_interaction_CFRP_cycling.md` | Various | M-series; CFRP | Thermal cycling | CFRP thermal; dissimilar materials |
| `67_68_69_70_MoS2_complex_random_neutron.md` | Various | Various | Various | MoS₂ coating; complex loading; neutron measurement |
| `71_Wiegand_2021_VDI_validation_index.md` | Wiegand (2021), Eng. Fail. Anal. | M-series (4-bolt flange) | Multi-bolt flanged | VDI 2230 load factor validation; eccentric loading |
| `72_Liu_Cai_2016_2017_axial_dynamic.md` | Liu et al. (2017), Tribology Int. 115:432 + Cai et al. (2016), Wear 346–347:29 | M10×1.5 | Axial pulsating tension | Two-stage non-rotational loss; MoS₂ coating effect; F/F₀ vs N curves; FEA validation ±10% |
| `74_76_77_78_torsional_loosening_Liu_group.md` | Liu, Ouyang et al. (2018/2019/2022), Tribology Int. (3 papers) | M12 | Torsional excitation | 3 clamping-force evolution types (A/B/C); hysteresis loop shape as slip indicator; wear-loosening coupling |
| `79_Yang_2021_composite_excitation_Rfactor.md` | Yang, Nassar & Wu (2021), Shock and Vibration, Art. 1441122 | M8×1.25 | Combined axial + transverse; R varied | R_axial as failure mode determinant; ξ_critical(R) map; R=−1 produces 3× faster loosening |
| `80_Du_2022_random_vibration_3stage.md` | Du, Qiu et al. (2022), Eng. Fail. Anal. 133:105954 | M8×1.25 (4-bolt) | Pure broadband random PSD | 3-stage criterion (Steady/Transition/Loosen) via strain amplitude; PSD threshold; torque vs. time-to-Loosen |
| `81_82_bending_loosening.md` | Ishimura et al. (2010), ASME PVP2010 + Yokoyama et al. (2012), Eng. Fail. Anal. 23:35 | Flanged; M10 | Bending moment; rotary bending | Bending-distinct mechanism from Junker; spring-back torsion; Stage I/II under bending |
| `83_84_Pai_Hess_2002_2003_thread_multibolt.md` | Pai & Hess (2002), J. Sound Vib. 253:585 + Pai & Hess (2003), J. Sound Vib. 268:617 | 5/16-18 UNC + 5/16-24 UNF; 1/4-20 UNC group | Transverse shear; multi-bolt | Fine vs. coarse thread (29% higher F_crit); 4 slip classification types; multi-bolt cascade; corner bolt first |
| `85_86_Bouzid_1995_2006_gasket_creep.md` | Bouzid, Chaaban & Bazergui (1995), ASME J. PVT 117:71 + Bouzid & Nechache (2006), ASME J. PVT 128:394 | M12, NPS 4 flanges | Static + cyclic compression; thermal | Gasket creep-relaxation 20–60% preload loss; elastic interaction 10–30%; Norton-Bailey calibration params |
| `87_Liu_Mi_2021_competitive_failure_Rfactor.md` | Liu, Mi et al. (2021), Eng. Fail. Anal. 129:105697 | M8–M12 | Biaxial; R ratio varied | R as sole failure-mode determinant across 15 preload × amplitude combinations; R_critical ≈ 0.55 |
| `88_Abid_Nash_2014_dynamic_gasket_flange.md` | Abid & Nash (2014), IIUM Engineering Journal 15(2) | M20, NPS 4 Class 300 | Cyclic harmonic internal pressure | 3%/100 cycles drift at design pressure; harmonic 2.5× worse than step; frequency-dependent ΔF |
| `89_Bhattacharya_2010_small_bolts_M4_M5.md` | Bhattacharya, Sen & Das (2010), Mech. Mach. Theory 45(8):1215 | M4, M5, M6 | Transverse Junker-type | Only paper with M4/M5 Junker tests; size scaling δ_critical ∝ d^0.82; spring washer +33% |
| `90_91_CFRP_loosening_Wei_Yang.md` | Wei et al. (2025), Polymer Composites + Yang et al. (2023), Adv. Mech. Eng. 15 | CFRP single-bolt specimens | Bending vibration; biaxial | Two-stage CFRP relaxation (18% rapid embedding + 5% slow); 70% loss from washer embedding; non-rotational dominant |
| `92_Su_Ye_2016_CFRP_viscoelastic.md` | Su & Ye (2016), Composites Part B 91:12 | CFRP (M8–M10 est.) | Vibration at 1.93 Hz; multiple temps | Logarithmic creep model A×ln(1+t/τ); rate doubles per ~20°C; Norton-Bailey CFRP parameter set |
| `93_Hu_Zhang_2020_CFRP_thermal_preload.md` | Hu, Zhang et al. (2020), J. Composite Materials 54(23):3261 | CFRP; Ti-6Al-4V bolt M10 | Thermal cycling; combined thermo-mechanical | CTE mismatch accelerates loss 10×; Stage I/II thermal pattern; combined loading = 1.4× sum |
| `94_95_Li_Luo_2022_similitude_rotordynamics.md` | Li, Luo et al. (2022), Proc. IMechE Part C 236:5192 + Li et al. (2022), Mathematics 10(1):3 | 1:3 scale model (M10 → M30 equiv.) | Dynamic / rotordynamic excitation | Buckingham Pi scaling with joint stiffness correction; frequency prediction error <5.4%; amplitude scaling validated |
| `96_Schaumann_2009_2015_large_bolt_VDI.md` | Schaumann & Marten (2009), NSCC + Schaumann et al. (2015), ISOPE-I-15-714 | M36, M64 (Grade 10.9) | Tension-tension R=0.1 fatigue | VDI 2230 overestimates fatigue limit: +19% for M36, +33% for M64; zinc coating −10–13%; size-effect non-conservatism |

---

## Plotting Guide

### Recommended Plot Types

1. **Normalized preload decay**: F(N)/F₀ vs. N (cycles) — allows direct comparison across bolt sizes and preload levels
2. **D-N loosening life curve**: Displacement amplitude (mm) vs. Loosening life N_L (cycles) on log-log scale — analogous to S-N fatigue curve
3. **Friction coefficient evolution**: μ_th and μ_b vs. N (cycles)
4. **Locking device comparison**: F(N)/F₀ vs. N for multiple devices on same plot
5. **Parametric sweeps**: Family of curves varying one parameter (torque, amplitude, roughness, etc.)

### Normalization Conventions Used

- **F₀**: Initial preload (measured, not nominal)
- **N**: Number of loading cycles
- **Δd or δ**: Transverse displacement amplitude (mm, peak or peak-to-peak — CHECK EACH PAPER)
- **f**: Frequency (Hz)
- **μ_th**: Thread friction coefficient
- **μ_b**: Bearing (underhead) friction coefficient
- **l_c**: Clamped length (mm)
- **d**: Nominal bolt diameter (mm)

### Data Format Convention

All tabular data in this library uses:
- SI units (N, mm, Hz, MPa)
- Cycle counts as integers
- Preload values in Newtons
- Friction coefficients dimensionless
- Temperatures in °C

### How to Use for Plotting

Each study file contains a section titled **"DATA FOR CURVE PLOTTING"** with tables formatted as:
```
Cycles | Preload (N) | Normalized F/F₀
```
These can be directly copied into Python/MATLAB/Excel. Where exact digitized points were not available, the data is marked as **[APPROXIMATE — digitized from published figure]** and the figure number is referenced so you can verify against the original paper.
