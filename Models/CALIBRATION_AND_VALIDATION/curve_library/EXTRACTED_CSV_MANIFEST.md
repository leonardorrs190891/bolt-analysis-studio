# Curvas extraidas da biblioteca (prontas p/ calibrar, sem download)

**200 curvas F/F0-vs-ciclo limpas** extraidas das tabelas ja digitalizadas nas notas de `CALIBRATION_AND_VALIDATION/`, em `extracted_csv/` (2 colunas `cycle,F_over_F0`). Outras 33 tabelas (ciclos-ate-X%, velocidade, atrito, mal-normalizadas) movidas para `extracted_csv/_needs_review/`.

Use direto na calibracao: aponte `reference_csv_path` de um `ValidationCase` para o CSV.

## Curvas por nota fonte

| Nota | # curvas |
|---|--:|
| 20_Gong_Liu_2018_2019_FEA_factors | 18 |
| 01_Lu_2024_M8_tangential_parametric | 16 |
| 18_Junker_test_locking_devices | 14 |
| 06_Yang_Nassar_2011_cap_screw | 11 |
| 03_Zhang_Jiang_2006_clamped_length | 9 |
| 08_Nassar_Housari_2007_clearance_fit | 9 |
| 10_Yang_2023_phenomenological_model | 9 |
| 07_Nassar_Housari_2006_pitch_preload | 8 |
| 13_Yang_2021_combined_loading | 8 |
| 29_Karlsen_Lemu_2022_large_bolt_M20_M42 | 8 |
| 02_Jiang_2003_2004_M12_early_stage | 7 |
| 51_52_53_54_axial_fatiguewear_noload_energy | 7 |
| 04_Housari_Nassar_2007_friction_effects | 6 |
| 25_Rousseau_Bouzid_2025_material_thickness | 6 |
| 27_Li_Liu_2020_directional_vibration_relaxation | 6 |
| 09_Yang_2019_M10_variable_amplitude | 5 |
| 15_Chen_2017_tightening_process | 5 |
| 17_Eccles_2010_tribological | 5 |
| 14_Dinger_Friedrich_2011_FEA | 4 |
| 34_Amano_2024_double_thread_bolt_ISO16130 | 4 |
| 72_Liu_Cai_2016_2017_axial_dynamic | 4 |
| 74_76_77_78_torsional_loosening_Liu_group | 4 |
| 11_Hattori_2010_critical_slippage | 3 |
| 24_Sanclemente_Hess_2007_DOE_factorial | 3 |
| 26_Yang_Jeong_2025_variable_amplitude_multibolt | 3 |
| 92_Su_Ye_2016_CFRP_viscoelastic | 3 |
| S1_Similitude_Geometric_Scaling_M20_to_M42 | 3 |
| 05_Nassar_Yang_2009_math_model | 1 |
| 12_Eraliev_2021_thermal_cycling | 1 |
| 32_Sase_Koga_1996_anti_loosening_nuts_7types | 1 |
| 35_36_37_38_wear_material_rotational_direction | 1 |
| 55_56_57_58_GPR_Iwan_reliability_arclock | 1 |
| 63_64_65_66_thermal_interaction_CFRP_cycling | 1 |
| 80_Du_2022_random_vibration_3stage | 1 |
| 81_82_bending_loosening | 1 |
| 85_86_Bouzid_1995_2006_gasket_creep | 1 |
| 88_Abid_Nash_2014_dynamic_gasket_flange | 1 |
| 90_91_CFRP_loosening_Wei_Yang | 1 |
| 93_Hu_Zhang_2020_CFRP_thermal_preload | 1 |
| **TOTAL** | **200** |

## Todas as curvas

| CSV | Nota | Dataset/condicao | pts | F/F0 ini | F/F0 fim |
|---|---|---|--:|--:|--:|
| 01_Lu_2024_M8_tangential_parametric__Amplitude_0_25_mm__6.csv | 01_Lu_2024_M8_tangential_parametric | Amplitude 0 25 mm | 8 | 1.0 | 0.795 |
| 01_Lu_2024_M8_tangential_parametric__Amplitude_0_50_mm__7.csv | 01_Lu_2024_M8_tangential_parametric | Amplitude 0 50 mm | 9 | 1.0 | 0.004 |
| 01_Lu_2024_M8_tangential_parametric__Amplitude_1_0_mm__8.csv | 01_Lu_2024_M8_tangential_parametric | Amplitude 1 0 mm | 6 | 1.0 | 0.064 |
| 01_Lu_2024_M8_tangential_parametric__Amplitude_1_5_mm__9.csv | 01_Lu_2024_M8_tangential_parametric | Amplitude 1 5 mm | 7 | 1.0 | 0.009 |
| 01_Lu_2024_M8_tangential_parametric__Amplitude_2_0_mm__10.csv | 01_Lu_2024_M8_tangential_parametric | Amplitude 2 0 mm | 7 | 1.0 | 0.004 |
| 01_Lu_2024_M8_tangential_parametric__Ra_0_8_m_smooth__11.csv | 01_Lu_2024_M8_tangential_parametric | Ra 0 8 m smooth | 6 | 1.0 | 0.035 |
| 01_Lu_2024_M8_tangential_parametric__Ra_1_6_m_medium__12.csv | 01_Lu_2024_M8_tangential_parametric | Ra 1 6 m medium | 6 | 1.0 | 0.064 |
| 01_Lu_2024_M8_tangential_parametric__Ra_3_2_m_rough__13.csv | 01_Lu_2024_M8_tangential_parametric | Ra 3 2 m rough | 6 | 1.0 | 0.095 |
| 01_Lu_2024_M8_tangential_parametric__T_10_Nm_F_5_963_N__2.csv | 01_Lu_2024_M8_tangential_parametric | T 10 Nm F 5 963 N | 6 | 1.0 | 0.309 |
| 01_Lu_2024_M8_tangential_parametric__T_16_Nm_F_8_402_N__3.csv | 01_Lu_2024_M8_tangential_parametric | T 16 Nm F 8 402 N | 6 | 1.0 | 0.187 |
| 01_Lu_2024_M8_tangential_parametric__T_22_Nm_F_11_567_N__4.csv | 01_Lu_2024_M8_tangential_parametric | T 22 Nm F 11 567 N | 6 | 1.0 | 0.064 |
| 01_Lu_2024_M8_tangential_parametric__T_28_Nm_F_15_027_N__5.csv | 01_Lu_2024_M8_tangential_parametric | T 28 Nm F 15 027 N | 6 | 1.0 | 0.234 |
| 01_Lu_2024_M8_tangential_parametric__T_4_Nm_F_2_105_N__1.csv | 01_Lu_2024_M8_tangential_parametric | T 4 Nm F 2 105 N | 6 | 1.0 | 0.037 |
| 01_Lu_2024_M8_tangential_parametric__f_1_Hz__14.csv | 01_Lu_2024_M8_tangential_parametric | f 1 Hz | 4 | 1.0 | 0.064 |
| 01_Lu_2024_M8_tangential_parametric__f_3_Hz__15.csv | 01_Lu_2024_M8_tangential_parametric | f 3 Hz | 4 | 1.0 | 0.059 |
| 01_Lu_2024_M8_tangential_parametric__f_5_Hz__16.csv | 01_Lu_2024_M8_tangential_parametric | f 5 Hz | 4 | 1.0 | 0.054 |
| 02_Jiang_2003_2004_M12_early_stage__0_254_mm_0_010__2.csv | 02_Jiang_2003_2004_M12_early_stage | 0 254 mm 0 010 | 6 | 1.0 | 0.86 |
| 02_Jiang_2003_2004_M12_early_stage__0_381_mm_0_015__3.csv | 02_Jiang_2003_2004_M12_early_stage | 0 381 mm 0 015 | 8 | 1.0 | 0.28 |
| 02_Jiang_2003_2004_M12_early_stage__0_46_mm_0_018__4.csv | 02_Jiang_2003_2004_M12_early_stage | 0 46 mm 0 018 | 9 | 1.0 | 0.08 |
| 02_Jiang_2003_2004_M12_early_stage__0_635_mm_0_025__5.csv | 02_Jiang_2003_2004_M12_early_stage | 0 635 mm 0 025 | 6 | 1.0 | 0.06 |
| 02_Jiang_2003_2004_M12_early_stage__1_27_mm_0_050__6.csv | 02_Jiang_2003_2004_M12_early_stage | 1 27 mm 0 050 | 6 | 1.0 | 0.02 |
| 02_Jiang_2003_2004_M12_early_stage__Dataset_1_Early_Stage_Stage_I_Nut_Glued_No_Rotation_Pap__1.csv | 02_Jiang_2003_2004_M12_early_stage | Dataset 1 Early Stage Stage I Nut Glued No Rotation Pa | 9 | 1.0 | 0.66 |
| 02_Jiang_2003_2004_M12_early_stage__Dataset_4_Effect_of_Higher_Preload_Paper_B__7.csv | 02_Jiang_2003_2004_M12_early_stage | Dataset 4 Effect of Higher Preload Paper B | 8 | 1.0 | 0.195 |
| 03_Zhang_Jiang_2006_clamped_length__30_from_transverse__7.csv | 03_Zhang_Jiang_2006_clamped_length | 30 from transverse | 6 | 1.0 | 0.06 |
| 03_Zhang_Jiang_2006_clamped_length__45_from_transverse__8.csv | 03_Zhang_Jiang_2006_clamped_length | 45 from transverse | 6 | 1.0 | 0.18 |
| 03_Zhang_Jiang_2006_clamped_length__60_from_transverse__9.csv | 03_Zhang_Jiang_2006_clamped_length | 60 from transverse | 6 | 1.0 | 0.42 |
| 03_Zhang_Jiang_2006_clamped_length__Pure_axial_90_from_transverse__10.csv | 03_Zhang_Jiang_2006_clamped_length | Pure axial 90 from transverse | 6 | 1.0 | 0.84 |
| 03_Zhang_Jiang_2006_clamped_length__Pure_transverse_0_from_transverse__6.csv | 03_Zhang_Jiang_2006_clamped_length | Pure transverse 0 from transverse | 5 | 1.0 | 0.06 |
| 03_Zhang_Jiang_2006_clamped_length__l_c_12_7_mm_l_d_1_06_Short_grip__1.csv | 03_Zhang_Jiang_2006_clamped_length | l c 12 7 mm l d 1 06 Short grip | 6 | 1.0 | 0.04 |
| 03_Zhang_Jiang_2006_clamped_length__l_c_25_4_mm_l_d_2_12_Standard_grip__2.csv | 03_Zhang_Jiang_2006_clamped_length | l c 25 4 mm l d 2 12 Standard grip | 7 | 1.0 | 0.12 |
| 03_Zhang_Jiang_2006_clamped_length__l_c_38_1_mm_l_d_3_18_Long_grip__3.csv | 03_Zhang_Jiang_2006_clamped_length | l c 38 1 mm l d 3 18 Long grip | 8 | 1.0 | 0.1 |
| 03_Zhang_Jiang_2006_clamped_length__l_c_50_8_mm_l_d_4_23_Extra_long_grip__4.csv | 03_Zhang_Jiang_2006_clamped_length | l c 50 8 mm l d 4 23 Extra long grip | 8 | 1.0 | 0.3 |
| 04_Housari_Nassar_2007_friction_effects__High_friction_th_b_0_20_Zinc_dry__3.csv | 04_Housari_Nassar_2007_friction_effects | High friction th b 0 20 Zinc dry | 8 | 1.0 | 0.056 |
| 04_Housari_Nassar_2007_friction_effects__High_thread_friction_low_bearing_friction_th_0_20_b_0_0__5.csv | 04_Housari_Nassar_2007_friction_effects | High thread friction low bearing friction th 0 20 b 0  | 5 | 1.0 | 0.08 |
| 04_Housari_Nassar_2007_friction_effects__Low_friction_th_b_0_06_MoS_film__1.csv | 04_Housari_Nassar_2007_friction_effects | Low friction th b 0 06 MoS film | 6 | 1.0 | 0.022 |
| 04_Housari_Nassar_2007_friction_effects__Low_thread_friction_high_bearing_friction_th_0_06_b_0_2__6.csv | 04_Housari_Nassar_2007_friction_effects | Low thread friction high bearing friction th 0 06 b 0  | 5 | 1.0 | 0.05 |
| 04_Housari_Nassar_2007_friction_effects__Medium_friction_th_b_0_12_Phosphate_oil__2.csv | 04_Housari_Nassar_2007_friction_effects | Medium friction th b 0 12 Phosphate oil | 7 | 1.0 | 0.045 |
| 04_Housari_Nassar_2007_friction_effects__Very_high_friction_th_b_0_30_Zinc_dry_rough_surfaces__4.csv | 04_Housari_Nassar_2007_friction_effects | Very high friction th b 0 30 Zinc dry rough surfaces | 8 | 1.0 | 0.225 |
| 05_Nassar_Yang_2009_math_model__Predicted_vs_Measured_Loosening_Curve__1.csv | 05_Nassar_Yang_2009_math_model | Predicted vs Measured Loosening Curve | 7 | 1.0 | 0.07 |
| 06_Yang_Nassar_2011_cap_screw__0_08_Cadmium__8.csv | 06_Yang_Nassar_2011_cap_screw | 0 08 Cadmium | 5 | 1.0 | 0.06 |
| 06_Yang_Nassar_2011_cap_screw__0_10_Phosphate_oil__9.csv | 06_Yang_Nassar_2011_cap_screw | 0 10 Phosphate oil | 4 | 1.0 | 0.063 |
| 06_Yang_Nassar_2011_cap_screw__0_22_Zinc_dry__10.csv | 06_Yang_Nassar_2011_cap_screw | 0 22 Zinc dry | 7 | 1.0 | 0.12 |
| 06_Yang_Nassar_2011_cap_screw__0_36_mm__4.csv | 06_Yang_Nassar_2011_cap_screw | 0 36 mm | 6 | 1.0 | 0.52 |
| 06_Yang_Nassar_2011_cap_screw__0_53_mm__5.csv | 06_Yang_Nassar_2011_cap_screw | 0 53 mm | 6 | 1.0 | 0.08 |
| 06_Yang_Nassar_2011_cap_screw__0_71_mm__6.csv | 06_Yang_Nassar_2011_cap_screw | 0 71 mm | 4 | 1.0 | 0.063 |
| 06_Yang_Nassar_2011_cap_screw__1_07_mm__7.csv | 06_Yang_Nassar_2011_cap_screw | 1 07 mm | 6 | 1.0 | 0.01 |
| 06_Yang_Nassar_2011_cap_screw__Dataset_4_Model_vs_Experiment_Comparison_F_11_120_N_0_7__11.csv | 06_Yang_Nassar_2011_cap_screw | Dataset 4 Model vs Experiment Comparison F 11 120 N 0  | 7 | 1.0 | 0.018 |
| 06_Yang_Nassar_2011_cap_screw__F_11_120_N_2_500_lbf__2.csv | 06_Yang_Nassar_2011_cap_screw | F 11 120 N 2 500 lbf | 7 | 1.0 | 0.018 |
| 06_Yang_Nassar_2011_cap_screw__F_16_680_N_3_750_lbf__3.csv | 06_Yang_Nassar_2011_cap_screw | F 16 680 N 3 750 lbf | 7 | 1.0 | 0.048 |
| 06_Yang_Nassar_2011_cap_screw__F_5_560_N_1_250_lbf__1.csv | 06_Yang_Nassar_2011_cap_screw | F 5 560 N 1 250 lbf | 6 | 1.0 | 0.009 |
| 07_Nassar_Housari_2006_pitch_preload__3_8_16_UNC_coarse_p_1_588_mm__4.csv | 07_Nassar_Housari_2006_pitch_preload | 3 8 16 UNC coarse p 1 588 mm | 6 | 1.0 | 0.06 |
| 07_Nassar_Housari_2006_pitch_preload__3_8_24_UNF_fine_p_1_058_mm__5.csv | 07_Nassar_Housari_2006_pitch_preload | 3 8 24 UNF fine p 1 058 mm | 7 | 1.0 | 0.04 |
| 07_Nassar_Housari_2006_pitch_preload__F_10_kN_low__6.csv | 07_Nassar_Housari_2006_pitch_preload | F 10 kN low | 5 | 1.0 | 0.08 |
| 07_Nassar_Housari_2006_pitch_preload__F_25_kN_medium__7.csv | 07_Nassar_Housari_2006_pitch_preload | F 25 kN medium | 4 | 1.0 | 0.1 |
| 07_Nassar_Housari_2006_pitch_preload__F_40_kN_high_69_proof__8.csv | 07_Nassar_Housari_2006_pitch_preload | F 40 kN high 69 proof | 7 | 1.0 | 0.04 |
| 07_Nassar_Housari_2006_pitch_preload__M10_1_0_superfine_p_1_00_mm_2_02__3.csv | 07_Nassar_Housari_2006_pitch_preload | M10 1 0 superfine p 1 00 mm 2 02 | 8 | 1.0 | 0.03 |
| 07_Nassar_Housari_2006_pitch_preload__M10_1_25_fine_p_1_25_mm_2_53__2.csv | 07_Nassar_Housari_2006_pitch_preload | M10 1 25 fine p 1 25 mm 2 53 | 7 | 1.0 | 0.06 |
| 07_Nassar_Housari_2006_pitch_preload__M10_1_5_coarse_p_1_50_mm_3_03__1.csv | 07_Nassar_Housari_2006_pitch_preload | M10 1 5 coarse p 1 50 mm 3 03 | 7 | 1.0 | 0.02 |
| 08_Nassar_Housari_2007_clearance_fit__10_clearance_loose__3.csv | 08_Nassar_Housari_2007_clearance_fit | 10 clearance loose | 6 | 1.0 | 0.01 |
| 08_Nassar_Housari_2007_clearance_fit__1B_fit_loose__4.csv | 08_Nassar_Housari_2007_clearance_fit | 1B fit loose | 6 | 1.0 | 0.01 |
| 08_Nassar_Housari_2007_clearance_fit__2B_fit_standard__5.csv | 08_Nassar_Housari_2007_clearance_fit | 2B fit standard | 6 | 1.0 | 0.02 |
| 08_Nassar_Housari_2007_clearance_fit__3B_fit_close__6.csv | 08_Nassar_Housari_2007_clearance_fit | 3B fit close | 7 | 1.0 | 0.03 |
| 08_Nassar_Housari_2007_clearance_fit__3_clearance_tight__1.csv | 08_Nassar_Housari_2007_clearance_fit | 3 clearance tight | 7 | 1.0 | 0.08 |
| 08_Nassar_Housari_2007_clearance_fit__6_clearance_standard__2.csv | 08_Nassar_Housari_2007_clearance_fit | 6 clearance standard | 6 | 1.0 | 0.02 |
| 08_Nassar_Housari_2007_clearance_fit__Best_case_3_clearance_3B_fit__7.csv | 08_Nassar_Housari_2007_clearance_fit | Best case 3 clearance 3B fit | 7 | 1.0 | 0.05 |
| 08_Nassar_Housari_2007_clearance_fit__Combined_Effect_Ratio__9.csv | 08_Nassar_Housari_2007_clearance_fit | Combined Effect Ratio | 3 | 1.0 | 0.3 |
| 08_Nassar_Housari_2007_clearance_fit__Worst_case_10_clearance_1B_fit__8.csv | 08_Nassar_Housari_2007_clearance_fit | Worst case 10 clearance 1B fit | 5 | 1.0 | 0.03 |
| 09_Yang_2019_M10_variable_amplitude__0_3_mm_Below_near_threshold__1.csv | 09_Yang_2019_M10_variable_amplitude | 0 3 mm Below near threshold | 8 | 1.0 | 0.827 |
| 09_Yang_2019_M10_variable_amplitude__0_4_mm__2.csv | 09_Yang_2019_M10_variable_amplitude | 0 4 mm | 9 | 1.0 | 0.269 |
| 09_Yang_2019_M10_variable_amplitude__0_6_mm__3.csv | 09_Yang_2019_M10_variable_amplitude | 0 6 mm | 9 | 1.0 | 0.019 |
| 09_Yang_2019_M10_variable_amplitude__0_8_mm__4.csv | 09_Yang_2019_M10_variable_amplitude | 0 8 mm | 8 | 1.0 | 0.008 |
| 09_Yang_2019_M10_variable_amplitude__1_0_mm__5.csv | 09_Yang_2019_M10_variable_amplitude | 1 0 mm | 7 | 1.0 | 0.008 |
| 10_Yang_2023_phenomenological_model__0_15_mm_below_threshold__7.csv | 10_Yang_2023_phenomenological_model | 0 15 mm below threshold | 4 | 1.0 | 0.925 |
| 10_Yang_2023_phenomenological_model__0_18_mm_below_threshold__1.csv | 10_Yang_2023_phenomenological_model | 0 18 mm below threshold | 5 | 1.0 | 0.93 |
| 10_Yang_2023_phenomenological_model__0_25_mm__2.csv | 10_Yang_2023_phenomenological_model | 0 25 mm | 7 | 1.0 | 0.52 |
| 10_Yang_2023_phenomenological_model__0_30_mm__8.csv | 10_Yang_2023_phenomenological_model | 0 30 mm | 7 | 1.0 | 0.06 |
| 10_Yang_2023_phenomenological_model__0_35_mm__3.csv | 10_Yang_2023_phenomenological_model | 0 35 mm | 8 | 1.0 | 0.05 |
| 10_Yang_2023_phenomenological_model__0_45_mm__4.csv | 10_Yang_2023_phenomenological_model | 0 45 mm | 7 | 1.0 | 0.05 |
| 10_Yang_2023_phenomenological_model__0_50_mm__9.csv | 10_Yang_2023_phenomenological_model | 0 50 mm | 6 | 1.0 | 0.02 |
| 10_Yang_2023_phenomenological_model__0_55_mm__5.csv | 10_Yang_2023_phenomenological_model | 0 55 mm | 6 | 1.0 | 0.05 |
| 10_Yang_2023_phenomenological_model__0_65_mm__6.csv | 10_Yang_2023_phenomenological_model | 0 65 mm | 6 | 1.0 | 0.03 |
| 11_Hattori_2010_critical_slippage__F_15_kN_S_0_5_mm__2.csv | 11_Hattori_2010_critical_slippage | F 15 kN S 0 5 mm | 6 | 1.0 | 0.05 |
| 11_Hattori_2010_critical_slippage__F_25_kN_S_0_5_mm__3.csv | 11_Hattori_2010_critical_slippage | F 25 kN S 0 5 mm | 7 | 1.0 | 0.05 |
| 11_Hattori_2010_critical_slippage__F_35_kN_S_0_5_mm__4.csv | 11_Hattori_2010_critical_slippage | F 35 kN S 0 5 mm | 8 | 1.0 | 0.15 |
| 12_Eraliev_2021_thermal_cycling__Dataset_1_Preload_vs_Thermal_Cycle_Number__1.csv | 12_Eraliev_2021_thermal_cycling | Dataset 1 Preload vs Thermal Cycle Number | 3 | 1.0 | 0.875 |
| 13_Yang_2021_combined_loading__F_14_050_N_standard_preload__3.csv | 13_Yang_2021_combined_loading | F 14 050 N standard preload | 7 | 1.0 | 0.03 |
| 13_Yang_2021_combined_loading__F_17_040_N_high_preload__4.csv | 13_Yang_2021_combined_loading | F 17 040 N high preload | 8 | 1.0 | 0.03 |
| 13_Yang_2021_combined_loading__F_5_680_N_low_preload__1.csv | 13_Yang_2021_combined_loading | F 5 680 N low preload | 6 | 1.0 | 0.02 |
| 13_Yang_2021_combined_loading__F_8_520_N_medium_preload__2.csv | 13_Yang_2021_combined_loading | F 8 520 N medium preload | 7 | 1.0 | 0.02 |
| 13_Yang_2021_combined_loading__F_axial_10_kN__8.csv | 13_Yang_2021_combined_loading | F axial 10 kN | 5 | 1.0 | 0.02 |
| 13_Yang_2021_combined_loading__F_axial_4_kN__6.csv | 13_Yang_2021_combined_loading | F axial 4 kN | 4 | 1.0 | 0.1 |
| 13_Yang_2021_combined_loading__F_axial_6_kN__7.csv | 13_Yang_2021_combined_loading | F axial 6 kN | 4 | 1.0 | 0.07 |
| 13_Yang_2021_combined_loading__Pure_transverse_F_axial_0__5.csv | 13_Yang_2021_combined_loading | Pure transverse F axial 0 | 4 | 1.0 | 0.13 |
| 14_Dinger_Friedrich_2011_FEA__0_05__1.csv | 14_Dinger_Friedrich_2011_FEA | 0 05 | 5 | 1.0 | 0.2 |
| 14_Dinger_Friedrich_2011_FEA__0_10__2.csv | 14_Dinger_Friedrich_2011_FEA | 0 10 | 7 | 1.0 | 0.12 |
| 14_Dinger_Friedrich_2011_FEA__0_15__3.csv | 14_Dinger_Friedrich_2011_FEA | 0 15 | 6 | 1.0 | 0.32 |
| 14_Dinger_Friedrich_2011_FEA__0_20__4.csv | 14_Dinger_Friedrich_2011_FEA | 0 20 | 6 | 1.0 | 0.52 |
| 15_Chen_2017_tightening_process__F_30_kN_52_proof__4.csv | 15_Chen_2017_tightening_process | F 30 kN 52 proof | 5 | 1.0 | 0.2 |
| 15_Chen_2017_tightening_process__F_50_kN_87_proof__5.csv | 15_Chen_2017_tightening_process | F 50 kN 87 proof | 5 | 1.0 | 0.48 |
| 15_Chen_2017_tightening_process__F_60_kN_104_proof_slight_yielding__6.csv | 15_Chen_2017_tightening_process | F 60 kN 104 proof slight yielding | 6 | 1.0 | 0.44 |
| 15_Chen_2017_tightening_process__Method_A_Real_tightening_includes_residual_stress_from___1.csv | 15_Chen_2017_tightening_process | Method A Real tightening includes residual stress from | 8 | 1.0 | 0.48 |
| 15_Chen_2017_tightening_process__Method_B_Direct_preload_no_tightening_residual_stress__2.csv | 15_Chen_2017_tightening_process | Method B Direct preload no tightening residual stress | 8 | 1.0 | 0.63 |
| 17_Eccles_2010_tribological__All_metal_prevailing_torque_nut_DIN_6925_M8_Class_10_9__5.csv | 17_Eccles_2010_tribological | All metal prevailing torque nut DIN 6925 M8 Class 10 9 | 7 | 1.0 | 0.14 |
| 17_Eccles_2010_tribological__Dataset_1_Friction_Coefficient_Evolution_During_Repeate__1.csv | 17_Eccles_2010_tribological | Dataset 1 Friction Coefficient Evolution During Repeat | 8 | 1.0 | 0.495 |
| 17_Eccles_2010_tribological__Dataset_5_Torque_Residual_Method_Eccles_s_Contribution__6.csv | 17_Eccles_2010_tribological | Dataset 5 Torque Residual Method Eccles s Contribution | 4 | 1.0 | 0.18 |
| 17_Eccles_2010_tribological__Nylon_insert_nut_DIN_985_M8_Class_10_9__4.csv | 17_Eccles_2010_tribological | Nylon insert nut DIN 985 M8 Class 10 9 | 7 | 1.0 | 0.06 |
| 17_Eccles_2010_tribological__Phase_1_Friction_INCREASES_Cycles_0_50__2.csv | 17_Eccles_2010_tribological | Phase 1 Friction INCREASES Cycles 0 50 | 5 | 1.0 | 0.364 |
| 18_Junker_test_locking_devices__All_Metal_Prevailing_Torque_Nut_DIN_6925__5.csv | 18_Junker_test_locking_devices | All Metal Prevailing Torque Nut DIN 6925 | 7 | 1.0 | 0.12 |
| 18_Junker_test_locking_devices__Double_Nut_DIN_25201_properly_installed_thin_nut_first___11.csv | 18_Junker_test_locking_devices | Double Nut DIN 25201 properly installed thin nut first | 7 | 1.0 | 0.68 |
| 18_Junker_test_locking_devices__HEICO_LOCK_Wedge_Locking_Washer__9.csv | 18_Junker_test_locking_devices | HEICO LOCK Wedge Locking Washer | 7 | 1.0 | 0.88 |
| 18_Junker_test_locking_devices__Helical_Spring_Washer_DIN_127__2.csv | 18_Junker_test_locking_devices | Helical Spring Washer DIN 127 | 8 | 1.0 | 0.0 |
| 18_Junker_test_locking_devices__Nord_Lock_Wedge_Locking_Washer_NL_Series__8.csv | 18_Junker_test_locking_devices | Nord Lock Wedge Locking Washer NL Series | 7 | 1.0 | 0.86 |
| 18_Junker_test_locking_devices__Nylon_Insert_Lock_Nut_Nyloc_DIN_985__4.csv | 18_Junker_test_locking_devices | Nylon Insert Lock Nut Nyloc DIN 985 | 7 | 1.0 | 0.06 |
| 18_Junker_test_locking_devices__Serrated_Flange_Bolt_IFI_145__10.csv | 18_Junker_test_locking_devices | Serrated Flange Bolt IFI 145 | 7 | 1.0 | 0.6 |
| 18_Junker_test_locking_devices__Serrated_Flange_Bolt__14.csv | 18_Junker_test_locking_devices | Serrated Flange Bolt | 6 | 1.0 | 0.35 |
| 18_Junker_test_locking_devices__Spring_Washer_DIN_127__13.csv | 18_Junker_test_locking_devices | Spring Washer DIN 127 | 4 | 1.0 | 0.01 |
| 18_Junker_test_locking_devices__Thread_Locking_Adhesive_Loctite_242_Medium_Strength__6.csv | 18_Junker_test_locking_devices | Thread Locking Adhesive Loctite 242 Medium Strength | 5 | 1.0 | 0.97 |
| 18_Junker_test_locking_devices__Thread_Locking_Adhesive_Loctite_271_High_Strength__7.csv | 18_Junker_test_locking_devices | Thread Locking Adhesive Loctite 271 High Strength | 5 | 1.0 | 0.98 |
| 18_Junker_test_locking_devices__Toothed_Lock_Washer_DIN_6797__3.csv | 18_Junker_test_locking_devices | Toothed Lock Washer DIN 6797 | 7 | 1.0 | 0.0 |
| 18_Junker_test_locking_devices__Unsecured_Bolt_Standard_Nut_Reference_Baseline__1.csv | 18_Junker_test_locking_devices | Unsecured Bolt Standard Nut Reference Baseline | 8 | 1.0 | 0.0 |
| 18_Junker_test_locking_devices__Unsecured__12.csv | 18_Junker_test_locking_devices | Unsecured | 4 | 1.0 | 0.02 |
| 20_Gong_Liu_2018_2019_FEA_factors__0_06__10.csv | 20_Gong_Liu_2018_2019_FEA_factors | 0 06 | 5 | 1.0 | 0.08 |
| 20_Gong_Liu_2018_2019_FEA_factors__0_10__11.csv | 20_Gong_Liu_2018_2019_FEA_factors | 0 10 | 5 | 1.0 | 0.32 |
| 20_Gong_Liu_2018_2019_FEA_factors__0_15__12.csv | 20_Gong_Liu_2018_2019_FEA_factors | 0 15 | 5 | 1.0 | 0.62 |
| 20_Gong_Liu_2018_2019_FEA_factors__0_20__13.csv | 20_Gong_Liu_2018_2019_FEA_factors | 0 20 | 4 | 1.0 | 0.79 |
| 20_Gong_Liu_2018_2019_FEA_factors__0_30__14.csv | 20_Gong_Liu_2018_2019_FEA_factors | 0 30 | 3 | 1.0 | 0.92 |
| 20_Gong_Liu_2018_2019_FEA_factors__0_5_mm_clearance_standard__7.csv | 20_Gong_Liu_2018_2019_FEA_factors | 0 5 mm clearance standard | 4 | 1.0 | 0.45 |
| 20_Gong_Liu_2018_2019_FEA_factors__1_0_mm_clearance_medium__8.csv | 20_Gong_Liu_2018_2019_FEA_factors | 1 0 mm clearance medium | 4 | 1.0 | 0.3 |
| 20_Gong_Liu_2018_2019_FEA_factors__2_0_mm_clearance_oversized__9.csv | 20_Gong_Liu_2018_2019_FEA_factors | 2 0 mm clearance oversized | 5 | 1.0 | 0.1 |
| 20_Gong_Liu_2018_2019_FEA_factors__F_20_kN_35_proof__15.csv | 20_Gong_Liu_2018_2019_FEA_factors | F 20 kN 35 proof | 5 | 1.0 | 0.1 |
| 20_Gong_Liu_2018_2019_FEA_factors__F_35_kN_61_proof__16.csv | 20_Gong_Liu_2018_2019_FEA_factors | F 35 kN 61 proof | 5 | 1.0 | 0.28 |
| 20_Gong_Liu_2018_2019_FEA_factors__F_50_kN_87_proof__17.csv | 20_Gong_Liu_2018_2019_FEA_factors | F 50 kN 87 proof | 4 | 1.0 | 0.45 |
| 20_Gong_Liu_2018_2019_FEA_factors__F_57_kN_99_proof__18.csv | 20_Gong_Liu_2018_2019_FEA_factors | F 57 kN 99 proof | 4 | 1.0 | 0.56 |
| 20_Gong_Liu_2018_2019_FEA_factors__Zero_clearance_body_fit_tight__6.csv | 20_Gong_Liu_2018_2019_FEA_factors | Zero clearance body fit tight | 4 | 1.0 | 0.84 |
| 20_Gong_Liu_2018_2019_FEA_factors__p_1_00_mm_superfine__1.csv | 20_Gong_Liu_2018_2019_FEA_factors | p 1 00 mm superfine | 5 | 1.0 | 0.7 |
| 20_Gong_Liu_2018_2019_FEA_factors__p_1_50_mm_fine__2.csv | 20_Gong_Liu_2018_2019_FEA_factors | p 1 50 mm fine | 5 | 1.0 | 0.55 |
| 20_Gong_Liu_2018_2019_FEA_factors__p_1_75_mm_coarse_standard_M12__3.csv | 20_Gong_Liu_2018_2019_FEA_factors | p 1 75 mm coarse standard M12 | 5 | 1.0 | 0.45 |
| 20_Gong_Liu_2018_2019_FEA_factors__p_2_00_mm_extra_coarse__4.csv | 20_Gong_Liu_2018_2019_FEA_factors | p 2 00 mm extra coarse | 5 | 1.0 | 0.35 |
| 20_Gong_Liu_2018_2019_FEA_factors__p_2_50_mm_very_coarse__5.csv | 20_Gong_Liu_2018_2019_FEA_factors | p 2 50 mm very coarse | 5 | 1.0 | 0.25 |
| 24_Sanclemente_Hess_2007_DOE_factorial__Run_16_1_2_UNF_High_preload_Steel_Tight_Lub_1_0_total_l__3.csv | 24_Sanclemente_Hess_2007_DOE_factorial | Run 16 1 2 UNF High preload Steel Tight Lub 1 0 total  | 5 | 1.0 | 0.99 |
| 24_Sanclemente_Hess_2007_DOE_factorial__Run_1_1_4_UNC_Low_preload_Al_Tight_Dry_9_2_total_loss__1.csv | 24_Sanclemente_Hess_2007_DOE_factorial | Run 1 1 4 UNC Low preload Al Tight Dry 9 2 total loss | 6 | 1.0 | 0.908 |
| 24_Sanclemente_Hess_2007_DOE_factorial__Run_9_1_4_UNC_Low_preload_Steel_Std_Dry_14_5_total_loss__2.csv | 24_Sanclemente_Hess_2007_DOE_factorial | Run 9 1 4 UNC Low preload Steel Std Dry 14 5 total los | 6 | 1.0 | 0.855 |
| 25_Rousseau_Bouzid_2025_material_thickness__HDPE_t_10_mm_grip_20_mm__4.csv | 25_Rousseau_Bouzid_2025_material_thickness | HDPE t 10 mm grip 20 mm | 7 | 1.0 | 0.0 |
| 25_Rousseau_Bouzid_2025_material_thickness__HDPE_t_12_mm_grip_24_mm__5.csv | 25_Rousseau_Bouzid_2025_material_thickness | HDPE t 12 mm grip 24 mm | 7 | 1.0 | 0.0 |
| 25_Rousseau_Bouzid_2025_material_thickness__HDPE_t_14_mm_grip_28_mm__6.csv | 25_Rousseau_Bouzid_2025_material_thickness | HDPE t 14 mm grip 28 mm | 6 | 1.0 | 0.0 |
| 25_Rousseau_Bouzid_2025_material_thickness__Steel_t_10_mm_grip_20_mm_l_d_1_67__1.csv | 25_Rousseau_Bouzid_2025_material_thickness | Steel t 10 mm grip 20 mm l d 1 67 | 9 | 1.0 | 0.0 |
| 25_Rousseau_Bouzid_2025_material_thickness__Steel_t_12_mm_grip_24_mm_l_d_2_00__2.csv | 25_Rousseau_Bouzid_2025_material_thickness | Steel t 12 mm grip 24 mm l d 2 00 | 7 | 1.0 | 0.0 |
| 25_Rousseau_Bouzid_2025_material_thickness__Steel_t_14_mm_grip_28_mm_l_d_2_33__3.csv | 25_Rousseau_Bouzid_2025_material_thickness | Steel t 14 mm grip 28 mm l d 2 33 | 7 | 1.0 | 0.0 |
| 26_Yang_Jeong_2025_variable_amplitude_multibolt__M8_0_45_mm_N_L_12_500__1.csv | 26_Yang_Jeong_2025_variable_amplitude_multibolt | M8 0 45 mm N L 12 500 | 8 | 1.0 | 0.8 |
| 26_Yang_Jeong_2025_variable_amplitude_multibolt__M8_0_55_mm_N_L_2_200__2.csv | 26_Yang_Jeong_2025_variable_amplitude_multibolt | M8 0 55 mm N L 2 200 | 8 | 1.0 | 0.8 |
| 26_Yang_Jeong_2025_variable_amplitude_multibolt__M8_0_65_mm_N_L_520__3.csv | 26_Yang_Jeong_2025_variable_amplitude_multibolt | M8 0 65 mm N L 520 | 7 | 1.0 | 0.8 |
| 27_Li_Liu_2020_directional_vibration_relaxation__Dataset_2_Transverse_vs_Axial_Vibration_Comparison__4.csv | 27_Li_Liu_2020_directional_vibration_relaxation | Dataset 2 Transverse vs Axial Vibration Comparison | 7 | 1.0 | 0.5 |
| 27_Li_Liu_2020_directional_vibration_relaxation__Dataset_3_Effect_of_Displacement_Amplitude_T_40_N_m_f_1__5.csv | 27_Li_Liu_2020_directional_vibration_relaxation | Dataset 3 Effect of Displacement Amplitude T 40 N m f  | 7 | 1.0 | 0.79 |
| 27_Li_Liu_2020_directional_vibration_relaxation__Dataset_5_Effect_of_Frequency_T_40_N_m_0_5_mm__6.csv | 27_Li_Liu_2020_directional_vibration_relaxation | Dataset 5 Effect of Frequency T 40 N m 0 5 mm | 5 | 1.0 | 0.51 |
| 27_Li_Liu_2020_directional_vibration_relaxation__T_30_N_m_F_17_5_kN__1.csv | 27_Li_Liu_2020_directional_vibration_relaxation | T 30 N m F 17 5 kN | 8 | 1.0 | 0.43 |
| 27_Li_Liu_2020_directional_vibration_relaxation__T_40_N_m_F_23_3_kN__2.csv | 27_Li_Liu_2020_directional_vibration_relaxation | T 40 N m F 23 3 kN | 7 | 1.0 | 0.5 |
| 27_Li_Liu_2020_directional_vibration_relaxation__T_50_N_m_F_29_2_kN__3.csv | 27_Li_Liu_2020_directional_vibration_relaxation | T 50 N m F 29 2 kN | 7 | 1.0 | 0.59 |
| 29_Karlsen_Lemu_2022_large_bolt_M20_M42__Dataset_4_Effect_of_Displacement_Amplitude_M30_Standard__7.csv | 29_Karlsen_Lemu_2022_large_bolt_M20_M42 | Dataset 4 Effect of Displacement Amplitude M30 Standar | 5 | 1.0 | 0.7 |
| 29_Karlsen_Lemu_2022_large_bolt_M20_M42__Effect_of_Displacement_Amplitude_M30_Bondura__8.csv | 29_Karlsen_Lemu_2022_large_bolt_M20_M42 | Effect of Displacement Amplitude M30 Bondura | 4 | 1.0 | 0.99 |
| 29_Karlsen_Lemu_2022_large_bolt_M20_M42__M20_Bondura__2.csv | 29_Karlsen_Lemu_2022_large_bolt_M20_M42 | M20 Bondura | 5 | 1.0 | 0.955 |
| 29_Karlsen_Lemu_2022_large_bolt_M20_M42__M20_Standard_HV__1.csv | 29_Karlsen_Lemu_2022_large_bolt_M20_M42 | M20 Standard HV | 7 | 1.0 | 0.18 |
| 29_Karlsen_Lemu_2022_large_bolt_M20_M42__M30_Bondura__4.csv | 29_Karlsen_Lemu_2022_large_bolt_M20_M42 | M30 Bondura | 5 | 1.0 | 0.96 |
| 29_Karlsen_Lemu_2022_large_bolt_M20_M42__M30_Standard_HV__3.csv | 29_Karlsen_Lemu_2022_large_bolt_M20_M42 | M30 Standard HV | 7 | 1.0 | 0.26 |
| 29_Karlsen_Lemu_2022_large_bolt_M20_M42__M42_Bondura__6.csv | 29_Karlsen_Lemu_2022_large_bolt_M20_M42 | M42 Bondura | 4 | 1.0 | 0.968 |
| 29_Karlsen_Lemu_2022_large_bolt_M20_M42__M42_Standard_HV__5.csv | 29_Karlsen_Lemu_2022_large_bolt_M20_M42 | M42 Standard HV | 7 | 1.0 | 0.33 |
| 32_Sase_Koga_1996_anti_loosening_nuts_7types__Device_Configurations__1.csv | 32_Sase_Koga_1996_anti_loosening_nuts_7types | Device Configurations | 9 | 1.0 | 1.0 |
| 34_Amano_2024_double_thread_bolt_ISO16130__DTB_IIC_M12_large_backlash_worn_die__4.csv | 34_Amano_2024_double_thread_bolt_ISO16130 | DTB IIC M12 large backlash worn die | 8 | 1.0 | 0.52 |
| 34_Amano_2024_double_thread_bolt_ISO16130__DTB_IIC_M12_medium_backlash_EDM_die__3.csv | 34_Amano_2024_double_thread_bolt_ISO16130 | DTB IIC M12 medium backlash EDM die | 8 | 1.0 | 0.75 |
| 34_Amano_2024_double_thread_bolt_ISO16130__DTB_IIC_M12_small_backlash_ground_die__2.csv | 34_Amano_2024_double_thread_bolt_ISO16130 | DTB IIC M12 small backlash ground die | 8 | 1.0 | 0.878 |
| 34_Amano_2024_double_thread_bolt_ISO16130__Standard_M12_1_75_no_anti_loosening__1.csv | 34_Amano_2024_double_thread_bolt_ISO16130 | Standard M12 1 75 no anti loosening | 8 | 1.0 | 0.02 |
| 35_36_37_38_wear_material_rotational_direction__Preload_Decay_Under_Rotational_Vibration_F_25_kN_1_0__1.csv | 35_36_37_38_wear_material_rotational_direction | Preload Decay Under Rotational Vibration F 25 kN 1 0 | 6 | 1.0 | 0.71 |
| 51_52_53_54_axial_fatiguewear_noload_energy__0_3_mm_sub_critical_primarily_Stage_I__6.csv | 51_52_53_54_axial_fatiguewear_noload_energy | 0 3 mm sub critical primarily Stage I | 6 | 1.0 | 0.78 |
| 51_52_53_54_axial_fatiguewear_noload_energy__0_7_mm_severe_loosening__7.csv | 51_52_53_54_axial_fatiguewear_noload_energy | 0 7 mm severe loosening | 6 | 1.0 | 0.25 |
| 51_52_53_54_axial_fatiguewear_noload_energy__1_1_mm_rapid_loosening_bolt_fatigue__8.csv | 51_52_53_54_axial_fatiguewear_noload_energy | 1 1 mm rapid loosening bolt fatigue | 6 | 1.0 | 0.0 |
| 51_52_53_54_axial_fatiguewear_noload_energy__Axial_amplitude_12_5_kN_F_ax_F_0_89__2.csv | 51_52_53_54_axial_fatiguewear_noload_energy | Axial amplitude 12 5 kN F ax F 0 89 | 6 | 1.0 | 0.66 |
| 51_52_53_54_axial_fatiguewear_noload_energy__Axial_amplitude_7_5_kN_F_ax_F_0_53__1.csv | 51_52_53_54_axial_fatiguewear_noload_energy | Axial amplitude 7 5 kN F ax F 0 53 | 6 | 1.0 | 0.87 |
| 51_52_53_54_axial_fatiguewear_noload_energy__Dataset_2_Repeated_Tightening_Loosening_Cycles_Axial_12__3.csv | 51_52_53_54_axial_fatiguewear_noload_energy | Dataset 2 Repeated Tightening Loosening Cycles Axial 1 | 8 | 1.0 | 0.937 |
| 51_52_53_54_axial_fatiguewear_noload_energy__Dataset_3_Torque_vs_Re_Tightening_Cycle__4.csv | 51_52_53_54_axial_fatiguewear_noload_energy | Dataset 3 Torque vs Re Tightening Cycle | 5 | 1.0 | 0.937 |
| 55_56_57_58_GPR_Iwan_reliability_arclock__Dataset_2_Stiffness_and_Damping_Evolution__1.csv | 55_56_57_58_GPR_Iwan_reliability_arclock | Dataset 2 Stiffness and Damping Evolution | 5 | 0.967 | 0.633 |
| 63_64_65_66_thermal_interaction_CFRP_cycling__Dataset_2_Cumulative_Preload_Decay_T_200_C__1.csv | 63_64_65_66_thermal_interaction_CFRP_cycling | Dataset 2 Cumulative Preload Decay T 200 C | 11 | 1.0 | 0.678 |
| 72_Liu_Cai_2016_2017_axial_dynamic__Amplitude_0_5_kN_F_ax_F_0_025__1.csv | 72_Liu_Cai_2016_2017_axial_dynamic | Amplitude 0 5 kN F ax F 0 025 | 5 | 1.0 | 0.978 |
| 72_Liu_Cai_2016_2017_axial_dynamic__Amplitude_1_0_kN_F_ax_F_0_050__2.csv | 72_Liu_Cai_2016_2017_axial_dynamic | Amplitude 1 0 kN F ax F 0 050 | 5 | 1.0 | 0.955 |
| 72_Liu_Cai_2016_2017_axial_dynamic__Amplitude_2_0_kN_F_ax_F_0_100__3.csv | 72_Liu_Cai_2016_2017_axial_dynamic | Amplitude 2 0 kN F ax F 0 100 | 7 | 1.0 | 0.893 |
| 72_Liu_Cai_2016_2017_axial_dynamic__Amplitude_3_0_kN_F_ax_F_0_150__4.csv | 72_Liu_Cai_2016_2017_axial_dynamic | Amplitude 3 0 kN F ax F 0 150 | 7 | 1.0 | 0.83 |
| 74_76_77_78_torsional_loosening_Liu_group__Amplitude_1_0_Type_B_slow_progressive__1.csv | 74_76_77_78_torsional_loosening_Liu_group | Amplitude 1 0 Type B slow progressive | 7 | 1.0 | 0.81 |
| 74_76_77_78_torsional_loosening_Liu_group__Amplitude_2_0_Type_B_to_C_transition__2.csv | 74_76_77_78_torsional_loosening_Liu_group | Amplitude 2 0 Type B to C transition | 6 | 1.0 | 0.72 |
| 74_76_77_78_torsional_loosening_Liu_group__Amplitude_5_0_Type_C_rapid_runaway__3.csv | 74_76_77_78_torsional_loosening_Liu_group | Amplitude 5 0 Type C rapid runaway | 6 | 1.0 | 0.18 |
| 74_76_77_78_torsional_loosening_Liu_group__Preload_Decay_Amplitude_3_0_F_20_kN__4.csv | 74_76_77_78_torsional_loosening_Liu_group | Preload Decay Amplitude 3 0 F 20 kN | 7 | 1.0 | 0.24 |
| 80_Du_2022_random_vibration_3stage__PSD_Level_0_10_g_Hz_below_threshold_Steady_Stage_only__1.csv | 80_Du_2022_random_vibration_3stage | PSD Level 0 10 g Hz below threshold Steady Stage only | 4 | 1.0 | 1.02 |
| 81_82_bending_loosening__Nut_Rotation_Rate_Under_Rotary_Bending__1.csv | 81_82_bending_loosening | Nut Rotation Rate Under Rotary Bending | 7 | 1.0 | 0.58 |
| 85_86_Bouzid_1995_2006_gasket_creep__Dataset_4_Cyclic_Thermal_Loading_Startup_Shutdown_Cycle__1.csv | 85_86_Bouzid_1995_2006_gasket_creep | Dataset 4 Cyclic Thermal Loading Startup Shutdown Cycl | 4 | 1.0 | 0.6 |
| 88_Abid_Nash_2014_dynamic_gasket_flange__Dataset_2_Effect_of_Frequency_100_Design_Pressure_300_C__1.csv | 88_Abid_Nash_2014_dynamic_gasket_flange | Dataset 2 Effect of Frequency 100 Design Pressure 300  | 4 | 0.95 | 0.972 |
| 90_91_CFRP_loosening_Wei_Yang__Preload_Decay_Two_Stage_CFRP_Loosening_Under_Bending_Vi__1.csv | 90_91_CFRP_loosening_Wei_Yang | Preload Decay Two Stage CFRP Loosening Under Bending V | 9 | 1.0 | 0.76 |
| 92_Su_Ye_2016_CFRP_viscoelastic__F_30_proof_load__1.csv | 92_Su_Ye_2016_CFRP_viscoelastic | F 30 proof load | 7 | 1.0 | 0.752 |
| 92_Su_Ye_2016_CFRP_viscoelastic__F_50_proof_load__2.csv | 92_Su_Ye_2016_CFRP_viscoelastic | F 50 proof load | 7 | 1.0 | 0.804 |
| 92_Su_Ye_2016_CFRP_viscoelastic__F_70_proof_load__3.csv | 92_Su_Ye_2016_CFRP_viscoelastic | F 70 proof load | 7 | 1.0 | 0.849 |
| 93_Hu_Zhang_2020_CFRP_thermal_preload__Dataset_1_Preload_Loss_Per_Thermal_Cycle_No_Mechanical___1.csv | 93_Hu_Zhang_2020_CFRP_thermal_preload | Dataset 1 Preload Loss Per Thermal Cycle No Mechanical | 8 | 1.0 | 0.78 |
| S1_Similitude_Geometric_Scaling_M20_to_M42__M30_Experimental_Data_1_5_mm_F_325_kN__3.csv | S1_Similitude_Geometric_Scaling_M20_to_M42 | M30 Experimental Data 1 5 mm F 325 kN | 7 | 1.0 | 0.26 |
| S1_Similitude_Geometric_Scaling_M20_to_M42__Model_Experimental_Loosening_Curve_ACTUAL_from_Paper_29__2.csv | S1_Similitude_Geometric_Scaling_M20_to_M42 | Model Experimental Loosening Curve ACTUAL from Paper 2 | 7 | 1.0 | 0.18 |
| S1_Similitude_Geometric_Scaling_M20_to_M42__Prototype_Experimental_Loosening_Curve_ACTUAL_from_Pape__1.csv | S1_Similitude_Geometric_Scaling_M20_to_M42 | Prototype Experimental Loosening Curve ACTUAL from Pap | 7 | 1.0 | 0.33 |
