# Bolt Analysis Studio v4.0 — Calibration & Validation Reference

**Source:** `Models/CALIBRATION_AND_VALIDATION/CALIBRATION_AND_VALIDATION_PLAN.md`
**Date:** 2026-02-18
**Scope:** 71 reference papers across 4 validation tiers

---

## 1. Calibration Philosophy

### 1.1 What "Calibrated" Means

A calibrated BAS produces predictions within known uncertainty bounds:

| Target | Acceptance Criterion |
|---|---|
| Preload decay curves (F/F₀ vs N) | ±15% for coupled loosening model |
| Loosening onset cycle | Within factor of 2× of experimental observation |
| D-N curves (displacement–life) | Within experimental scatter band |
| Critical friction coefficient (μ_critical) | ±10% vs Nassar-Yang analytical prediction |
| Preload loss models | Must bound experimental data correctly |
| Torque balance (T_pitch vs T_resistance) | Correct loosening/no-loosening outcome for ALL cases |

### 1.2 Calibration vs. Validation

| Phase | Purpose | Data | Model Access |
|---|---|---|---|
| **Calibration** | Tune free parameters | Papers 01, 02, 04, 05 (training set) | Full — adjust parameters |
| **Validation** | Verify against independent data | Papers 03, 06–71 (test set) | **Frozen** — no changes |
| **Sensitivity** | Quantify parameter influence | All papers | Systematic sweeps |

---

## 2. Free Parameters — The 8 Calibration Parameters

| Parameter | Current Default | Code Location | Physical Meaning |
|---|---|---|---|
| `C_loosening` | 0.3 (hardcoded) | `coupled_loosening_analyzer.py:494` | Loosening efficiency coefficient |
| `mu_initial` | 0.15 | `FrictionEvolutionParams:77` | Initial friction coefficient |
| `mu_peak` | 0.18 | `FrictionEvolutionParams:78` | Peak running-in friction |
| `mu_steady` | 0.10 | `FrictionEvolutionParams:79` | Steady-state friction |
| `mu_minimum` | 0.03 | `FrictionEvolutionParams:80` | Absolute floor |
| `N_phase1` | 50 | `FrictionEvolutionParams` | Running-in duration (cycles) |
| `N_phase2` | 500 | `FrictionEvolutionParams` | Transition duration (cycles) |
| `K_wear` | 1×10⁻⁷ | `WearModelParams` | Archard wear coefficient |

Additional parameters requiring calibration:
- `H_surface` = 2500 MPa (surface hardness)
- `lambda_stage1` = 0.02 (Jiang Stage I ratcheting rate)
- `eta_max` = 0.30 (max Stage I loss fraction; Jiang data: 34% max)
- `omega_loosen` = per-case (Stage II rate in deg/cycle)
- `K_factor` formula (currently oversimplified; should use full VDI formula)

---

## 3. Critical Bugs Blocking Calibration

These issues from `IMPROVEMENT_ANALYSIS_Code_vs_Reference.md` must be resolved before calibration:

| Bug | Description | Calibration Impact |
|---|---|---|
| **C1** | Distributed thread stiffness formula wrong | k_total wrong for all thread models |
| **C2** | Head stiffness 0.4 vs 0.5 inconsistency | 20% bolt stiffness error propagates everywhere |
| **C3** | Stress area uses d3 instead of d1 | ~3% error in A_t, affects yield calculations |
| **C5** | Contact system not wired into solver | Cannot calibrate contact-based models |
| **H2** | System stiffness uses trace(K) | 5–10× overestimation of k_sys |
| **H3** | CoupledLooseningAnalyzer disconnected from contacts | Loosening model ignores contact friction/wear |
| **M1** | K-factor (nut factor) oversimplified | 22% error in torque-preload relation |
| **M8** | C_loosening hardcoded at 0.3 | Cannot calibrate to experimental data |
| **M9** | Thread and bearing friction assumed equal | Cannot reproduce separate-friction experiments |

---

## 4. Validation Tiers

### Tier 1: Primary Calibration Cases (Training Set)

Four papers with richest quantitative data, used to tune parameters.

---

#### Case T1: Lu 2024 — M8 Parametric (Paper 01)

14 test configurations. Best parametric coverage in the literature.

**Bolt:** M8 × 1.25 mm, A_t = 36.6 mm²
**Test setup:** DIN 65151 Junker-type transverse vibration

| Sub-case | F₀ (N) | δ (mm) | f (Hz) | μ | N_cycles | F_final/F₀ |
|---|---|---|---|---|---|---|
| T1a: Baseline | 11,567 | 1.0 | 1 | 0.20 | 100 | 0.064 |
| T1b: Low preload | 2,105 | 1.0 | 1 | 0.20 | 100 | 0.037 |
| T1c: High preload | 15,027 | 1.0 | 1 | 0.20 | 100 | 0.234 |
| T1d: Small amplitude | 11,567 | 0.25 | 1 | 0.20 | 1000 | 0.795 |
| T1e: Large amplitude | 11,567 | 2.0 | 1 | 0.20 | 50 | 0.004 |
| T1f: Smooth Ra=0.8 | 11,567 | 1.0 | 1 | 0.18 | 100 | 0.035 |
| T1g: Rough Ra=3.2 | 11,567 | 1.0 | 1 | 0.22 | 100 | 0.095 |

**Calibration target:** Adjust `C_loosening` so T1a matches F/F₀ at cycles 5, 10, 20, 50, 100.

**Acceptance:** Mean absolute error < 0.10 on F/F₀ across all data points.

---

#### Case T2: Jiang 2003/2004 — M12 Two-Stage (Paper 02)

Definitive Stage I/II separation. The glued-nut data isolates non-rotational loss.

**Bolt:** M12 × 1.75 mm
**Reference:** Jiang Y., Zhang M., Lee C.H. (2003). ASME J. Mech. Design, Vol. 125, pp. 518–526.

| Sub-case | F₀ (N) | δ (mm) | f (Hz) | μ | N_cycles | F_final/F₀ |
|---|---|---|---|---|---|---|
| T2a: Glued nut (Stage I) | 25,000 | 0.46 | 5 | 0.15 | 200 | 0.660 |
| T2b: Free nut baseline | 25,000 | 0.46 | 5 | 0.15 | 250 | 0.080 |
| T2c: Threshold amplitude | 25,000 | 0.254 | 5 | 0.15 | 500 | 0.860 |
| T2d: Large amplitude | 25,000 | 0.635 | 5 | 0.15 | 100 | 0.060 |
| T2e: Very large amplitude | 25,000 | 1.27 | 5 | 0.15 | 50 | 0.020 |
| T2f: Higher preload | 41,000 | 0.46 | 5 | 0.15 | 500 | 0.195 |

**Calibration targets:**
- T2a (glued nut): Calibrate `lambda_stage1`, `eta_max` → 34% loss in 200 cycles
- T2b (free nut): Calibrate `C_loosening` → ~0.05 deg/cycle loosening rate
- T2c (threshold): Verify model predicts no rotational loosening (Stage I only)

---

#### Case T3: Housari & Nassar 2007 — Friction Parametric (Paper 04)

Systematic μ sweep. Directly calibrates friction evolution model.

| Sub-case | μ_thread | μ_bearing | Key Observation |
|---|---|---|---|
| T3a | 0.05 | 0.05 | Complete loss < 50 cycles |
| T3b | 0.10 | 0.10 | Moderate loosening |
| T3c | 0.15 | 0.15 | Standard behavior |
| T3d | 0.20 | 0.20 | Slow loosening |
| T3e | 0.30 | 0.30 | Very slow, may not fully loosen |

**Calibration target:** Match ranking and relative rates. Verify μ_critical prediction.

---

#### Case T4: Nassar & Yang 2009 — Analytical Reference (Paper 05)

Complete closed-form reference solution. BAS must reproduce curves exactly.

**Calibration target:** `NassarYangLooseningModel` output < 1% error vs paper equations.

---

### Tier 2: Core Validation Cases (Test Set — Parameters Frozen)

| Case | Paper | Bolt | Key Test | Expected BAS Error |
|---|---|---|---|---|
| V1 | 03 Zhang-Jiang 2006 | M12 | Clamped length effect (25, 38, 51 mm) | <20% on final preload |
| V2 | 06 Yang-Nassar 2011 | 5/16"-24 UNC | Cap screw analytical + experimental | <15% |
| V3 | 07 Nassar-Housari 2006 | M8, M10 | Pitch effect (1.0, 1.25, 1.5 mm) | <20% |
| V4 | 08 Nassar-Housari 2007 | M10 | Hole clearance (3–10%) and thread fit | <25% |
| V5 | 09 Yang 2019 | M10 | Variable amplitude D-N life curves | Factor of 2 |
| V6 | 10 Yang 2023 | M6, M8 | Phenomenological power-law model | <15% |
| V7 | 11 Hattori 2010 | M6, M10, M16 | Critical slippage, size effect | <20% |
| V8 | 17 Eccles 2010 | M8–M12 | Friction evolution, coating effects | <15% on μ(N) |
| V9 | 18 Junker test | M8–M12 | DIN 65151 standard test, locking devices | Correct ranking |
| V10 | 20 Gong-Liu 2019 | M12 | FEA parametric (pitch, clearance, friction) | <25% |

---

### Tier 3: Extended Validation (Specialized Phenomena)

| Case | Paper(s) | Phenomenon | BAS Requirement |
|---|---|---|---|
| V11 | 12 Eraliev 2021 | Thermal cycling (M12, ΔT) | Correct preload loss direction and magnitude |
| V12 | 13 Yang 2021 | Combined axial + transverse (M8) | Interaction effect captured |
| V13 | 25 Rousseau 2025 | HDPE clamped members (M12) | Material-dependent loosening rate |
| V14 | 26 Yang 2025 | Variable amplitude multi-bolt | D-N curve and Miner's rule |
| V15 | 29 Karlsen 2022 | Large bolts M20–M42 | Size scaling correctness |
| V16 | 30 Nechache 2007 | Gasket creep (NPS 3"–52") | Long-term creep prediction |
| V17 | 31 den Otter 2020 | SS bolts in aluminum | CTE mismatch thermal loss |
| V18 | 33 Du 2025 | Sine-on-random vibration | Combined loading response |
| V19 | 47 Brown 2017 | High temp B7/B16 (385°C) | Thermal relaxation prediction |
| V20 | 71 Wiegand 2021 | VDI 2230 vs FEM (4-bolt flange) | Load introduction factor |

---

### Tier 4: Qualitative Validation (Trend Verification)

These papers provide directional trends but insufficient digitized data for quantitative fit.

| Paper(s) | What to Verify |
|---|---|
| 14 Dinger-Friedrich 2011 | FEA contact state parameter (partial vs complete slip) |
| 15 Chen 2017 | Tightening process effect direction |
| 16 Izumi-Sakai | Thread slip precedes bearing slip |
| 19 Sandia/NASA | Modal excitation loosening mechanism |
| 23 Pai-Hess 2002 | 4 loosening process identification |
| 24 Sanclemente-Hess 2007 | DOE factor rankings match BAS sensitivity |
| 27 Li-Liu 2020 | Transverse loading dominates over axial |
| 28 Zhao 2023 | 7 anti-loosening devices: correct relative ranking |
| 32 Sase 1996 | 7 nut types: correct relative ranking |
| 34 Amano 2024 | Double-thread bolt improvement direction |
| 53 Liu 2021 | Self-loosening without external load (thermal/embedding) |

---

## 5. Calibration Procedure

### Phase 1: Fix Critical Bugs (see Section 3 above)

### Phase 2: Implement Validation Infrastructure

Recommended directory structure:
```
tests/validation/
├── __init__.py
├── validation_cases.py          — ValidationCase dataclass + ExperimentalDataPoint
├── validation_runner.py         — Automated test runner
├── calibration_optimizer.py     — scipy.optimize parameter sweep
├── validation_report.py         — Generate comparison plots and error metrics
└── data/
    ├── lu_2024_m8.json          — Digitized data from Paper 01
    ├── jiang_2003_m12.json      — Digitized data from Paper 02
    └── ...
```

### Phase 3: Single-Case Calibration

For T1a (Lu 2024 M8 Baseline):

```python
# Target: C_loosening such that F/F₀ at N=5, 10, 20, 50, 100 matches within 0.10
optimizer = CalibratorOptimizer(
    param_names=["C_loosening"],
    param_bounds=[(0.05, 1.0)],
    case=T1a_case,
    loss="mean_absolute_error"
)
result = optimizer.minimize()  # scipy.optimize.minimize(method='Nelder-Mead')
C_loosening_calibrated = result.x[0]
```

### Phase 4: Validate Frozen Parameters

Run all Tier 2 cases with calibrated parameters. Generate comparison plots.

### Phase 5: Sensitivity Analysis

Sweep each parameter ±50% independently. Report influence rank.

---

## 6. Key Literature — Top References

| Authors | Year | Paper | Key Contribution to BAS |
|---|---|---|---|
| Junker, G.H. | 1969 | SAE 690055 | Fundamental loosening mechanism (transverse slip) |
| Jiang, Zhang, Lee | 2003 | ASME J. Mech. Design 125 | Two-stage model (Stage I / Stage II) |
| Jiang, Zhang | 2004 | ASME J. Mech. Design 126 | Three-stage extension |
| Pai & Hess | 2002 | Eng. Failure Analysis 9 | Partial slip (4 slip regimes) |
| Nassar & Housari | 2006 | ASME J. Mech. Design 128 | Pitch effect (M8/M10) |
| Nassar & Yang | 2009 | ASME J. Pressure Vessel 131 | Closed-form analytical model |
| Hintikka et al. | 2019, 2020 | Tribology International 131, 143 | Three-phase friction evolution |
| Eccles, W. | 2010 | PhD Thesis, UCLan | Tribological aspects (coating effects) |
| Lu et al. | 2024 | (Paper 01) | Power-law model, M8 parametric data |
| Gong & Liu | 2019 | (Paper 20) | FEA parametric study |
| Hattori et al. | 2010 | (Paper 11) | Size effect, critical slippage |
| VDI 2230 | 2015 | Part 1 | Embedding, K-factor, design standards |
| Yang & Nassar | 2011 | (Paper 06) | Cap screw analytical + experimental |

---

## 7. Validation Data File Index

Files located in `Models/CALIBRATION_AND_VALIDATION/`:

```
00_INDEX_AND_PLOTTING_GUIDE.md   — Master index and plotting instructions
CALIBRATION_AND_VALIDATION_PLAN.md — This document (source)

Papers 01–71 organized as:
  01_Lu_2024_M8_Parametric.md      — Training case T1
  02_Jiang_2003_M12_TwoStage.md    — Training case T2
  03_Zhang_Jiang_2006.md           — Validation case V1
  04_Housari_Nassar_2007.md        — Training case T3
  05_Nassar_Yang_2009.md           — Training case T4
  06_Yang_Nassar_2011.md           — Validation case V2
  ...
  71_Wiegand_2021.md               — Validation case V20

S1_Similitude_Study.md           — Similitude scale factor cases
S2_Similitude_Study.md           — Additional similitude validation

IMPROVEMENT_ANALYSIS_Code_vs_Reference.md — Bug list C1–H7
IMPROVEMENT_ANALYSIS_MSD_Builder.md       — UX issues
IMPROVEMENT_ANALYSIS_Similitude.md        — Similitude gaps
```

---

## 8. Key Physical Insights from Validation Literature

These quantitative findings from the experimental literature define what BAS must reproduce:

### 8.1 Stage I vs Stage II Loosening (Jiang 2003/2004)

| Feature | Stage I (Non-Rotational) | Stage II (Rotational) |
|---|---|---|
| Nut rotation | None | Yes — back-off per cycle |
| Mechanism | Plastic micro-deformation at thread roots | Transverse slip at both interfaces → helix drives nut back |
| Preload loss at 200 cycles | 10–34% (depends on amplitude) | Up to 92% at 250 cycles |
| Threshold amplitude | δ < 0.254 mm for M12×1.75 → Stage I only | δ > 0.254 mm → Stage II begins |
| Isolatable? | Yes — glue nut to shaft | No — must use free nut |

**Implication:** BAS must correctly predict which stage is active for a given δ/F₀ combination.

### 8.2 Preload Sensitivity (Lu 2024 — M8)

| Preload Level | F₀ (N) | F_final/F₀ at N=100 |
|---|---|---|
| Very low (4 Nm torque) | 2,105 | 0.037 (96% loss!) |
| Medium (16 Nm) | 11,567 | 0.064 (94% loss) |
| High (28 Nm) | 15,027 | 0.234 (77% loss) |

**Finding:** 7× difference in preload retention between lowest and highest tightening. Lower preload → dramatically faster loosening (nonlinear sensitivity).

**Critical finding:** 50.2% preload loss in the first cycle at δ = 2.0 mm (large amplitude regime).

### 8.3 Amplitude Dominance

The transverse displacement amplitude δ is the primary control parameter (dominant in DOE studies):

| δ (mm) | F_final/F₀ at N=100 (M8, F₀=11.6 kN) | Regime |
|---|---|---|
| 0.25 | 0.795 (minimal loss) | Stage I only — near threshold |
| 1.0 | 0.064 (severe loss) | Stage II active |
| 2.0 | 0.004 (essentially complete) | Runaway — first-cycle loss |

**Below threshold:** ~800–1 000 cycles endurance limit before significant loosening.

### 8.4 Friction Coefficient Role (Housari-Nassar 2007 — M10)

| μ (uniform) | Outcome at 200 cycles |
|---|---|
| 0.05 | Complete loss (< 50 cycles) |
| 0.10 | Rapid loosening |
| 0.15 | Standard loosening behavior |
| 0.20 | Slow loosening |
| 0.30 | Very slow — may not fully loosen |

**Critical friction (M16):** μ_critical ≈ 0.024 — below this, ANY transverse load causes loosening even without vibration.

### 8.5 Parameter Rankings (DOE Results — Sanclemente-Hess 2007)

From factorial DOE analysis, parameter significance order for loosening rate:

1. **Displacement amplitude δ** (primary — dominant)
2. **Preload F₀** (secondary)
3. **Friction coefficient μ** (tertiary)
4. **Thread geometry** (pitch p, d₂) (quaternary)
5. **Frequency f** (minimal effect on steady-state rate)

BAS sensitivity analysis results must match this ranking.

---

## 9. Expected BAS Performance After Full Calibration

Based on the validation plan targets:

| Analysis Type | Expected Accuracy | Key Sensitivity |
|---|---|---|
| Loosening onset cycle | Factor of 2× | C_loosening (dominant), mu_initial |
| Preload at N=100 cycles | ±15% | C_loosening, lambda_stage1 |
| Preload at N=1000 cycles | ±20% | K_wear, mu_steady |
| D-N life curve shape | Within scatter band | mu_initial, bolt geometry |
| Friction coefficient evolution | ±15% on μ(N) | mu_peak, N_phase1, N_phase2 |
| Critical friction threshold | ±10% | Thread geometry, d₂, r_eff |

---

*Source: `Models/CALIBRATION_AND_VALIDATION/CALIBRATION_AND_VALIDATION_PLAN.md`*
*Papers stored in `Models/Papers/` (71 references)*
