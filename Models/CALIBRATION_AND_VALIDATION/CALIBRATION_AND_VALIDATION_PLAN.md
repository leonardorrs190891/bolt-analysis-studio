# Calibration & Validation Plan — Bolt Analysis Studio v4.0

## LTAD/UFU - Petrobras R&D

**Date**: 2026-02-28
**Scope**: Systematic calibration of BAS numerical models against published experimental data from 97 reference papers in `Models/CALIBRATION_AND_VALIDATION/`.
**Prerequisite**: All bug fixes from `IMPROVEMENT_ANALYSIS_Code_vs_Reference.md` (C1–C5, H1–H7) and UI improvements from `MSD_BUILDER_UX_DESIGN_STUDY.md`, `SOLVER_TAB_STUDY.md`, and `RESULTS_TAB_STUDY.md` must be completed first.

---

## 1. Calibration Philosophy

### 1.1 What "Calibrated" Means

A calibrated software produces predictions that agree with published experimental data within known uncertainty bounds. For BAS, this means:

1. **Preload decay curves** (F/F0 vs. N) must match experimental data within +/-15% for the coupled loosening model
2. **Loosening onset cycle** must be predicted within a factor of 2x of experimental observation
3. **D-N curves** (displacement-life) must fall within the experimental scatter band
4. **Critical friction coefficient** (mu_critical) must agree with analytical Nassar-Yang predictions within +/-10%
5. **Preload loss models** (exponential, stretched exponential, VDI embedding) must bound the experimental data correctly
6. **Torque balance** (T_pitch vs T_resistance) must predict the correct loosening/no-loosening outcome for every validation case

### 1.2 Calibration vs. Validation

| Phase | Purpose | Data Source | Model Access |
|-------|---------|-------------|--------------|
| **Calibration** | Tune free parameters (C_loosening, friction evolution rates, wear coefficients) | Papers 01, 02, 04, 05 (training set) | Full — adjust parameters |
| **Validation** | Verify predictions against independent data | Papers 03, 06-20, 23-71 (test set) | Frozen — no parameter changes |
| **Sensitivity** | Quantify parameter influence on predictions | All papers | Systematic sweeps |

### 1.3 Free Parameters to Calibrate

| Parameter | Current Value | Location | Physical Meaning | Calibration Target |
|-----------|---------------|----------|-------------------|-------------------|
| `C_loosening` | 0.3 (hardcoded) | `coupled_loosening_analyzer.py:494` | Loosening efficiency coefficient | Papers 01, 02 preload decay shape |
| `mu_initial` | 0.15 (default) | `FrictionEvolutionParams:77` | Initial friction coefficient | VDI 2230 Table 21 + Papers 04, 17 |
| `mu_peak` | 0.18 (default) | `FrictionEvolutionParams:78` | Peak running-in friction | Paper 17 (Eccles) friction evolution |
| `mu_steady` | 0.10 (default) | `FrictionEvolutionParams:79` | Steady-state friction | Paper 17 (Eccles) long-term data |
| `mu_minimum` | 0.03 (default) | `FrictionEvolutionParams:80` | Absolute floor | Paper 04 (Housari-Nassar) parametric |
| `N_phase1` | 50 | `FrictionEvolutionParams` | Running-in duration (cycles) | Paper 02 (Jiang) Stage I data |
| `N_phase2` | 500 | `FrictionEvolutionParams` | Transition duration | Paper 02 (Jiang) Stage I→II transition |
| `K_wear` | 1e-7 | `WearModelParams` | Archard wear coefficient | Papers 17, 35 (Eccles, Zhang wear data) |
| `H_surface` | 2500 MPa | `WearModelParams` | Surface hardness | Paper 21 (reference properties) |
| `lambda_stage1` | 0.02 | `TwoStageLooseningParams` | Stage I ratchetting rate | Paper 02 (Jiang glued-nut data) |
| `eta_max` | 0.30 | `TwoStageLooseningParams` | Max Stage I loss fraction | Paper 02 (Jiang glued-nut: 34% max) |
| `omega_loosen` | per-case | `TwoStageLooseningParams` | Stage II rate (deg/cycle) | Papers 01, 02, 06 experimental rates |
| `K_factor` | 0.16+0.5*mu | `preload_loss_models.py:123` | Nut factor for torque-preload | Paper 21 VDI table (should be VDI formula) |

---

## 2. Validation Case Database

### 2.1 Tier 1: Primary Calibration Cases (Training Set)

These papers have the richest quantitative data and are used to tune parameters.

#### Case T1: Lu 2024 — M8 Parametric (Paper 01)

**Why**: 14 test configurations with digitized data. Best parametric coverage.

| Sub-case | F0 (N) | delta (mm) | f (Hz) | mu | n_cycles | F_final/F0 |
|----------|--------|------------|--------|-----|----------|------------|
| T1a: Baseline | 11,567 | 1.0 | 1 | 0.20 | 100 | 0.064 |
| T1b: Low preload | 2,105 | 1.0 | 1 | 0.20 | 100 | 0.037 |
| T1c: High preload | 15,027 | 1.0 | 1 | 0.20 | 100 | 0.234 |
| T1d: Small amplitude | 11,567 | 0.25 | 1 | 0.20 | 1000 | 0.795 |
| T1e: Large amplitude | 11,567 | 2.0 | 1 | 0.20 | 50 | 0.004 |
| T1f: Smooth (Ra=0.8) | 11,567 | 1.0 | 1 | 0.18 | 100 | 0.035 |
| T1g: Rough (Ra=3.2) | 11,567 | 1.0 | 1 | 0.22 | 100 | 0.095 |

**Calibration target**: Match preload decay curve shape. Adjust `C_loosening` so that the T1a baseline curve matches F/F0 at cycles 5, 10, 20, 50, 100.

**Acceptance criterion**: Mean absolute error < 0.10 on F/F0 across all data points.

#### Case T2: Jiang 2003/2004 — M12 Two-Stage (Paper 02)

**Why**: Definitive Stage I/II separation. Nut glued data isolates non-rotational loss.

| Sub-case | F0 (N) | delta (mm) | f (Hz) | mu | n_cycles | F_final/F0 |
|----------|--------|------------|--------|-----|----------|------------|
| T2a: Glued nut (Stage I only) | 25,000 | 0.46 | 5 | 0.15 | 200 | 0.660 |
| T2b: Free nut baseline | 25,000 | 0.46 | 5 | 0.15 | 250 | 0.080 |
| T2c: Small amplitude (threshold) | 25,000 | 0.254 | 5 | 0.15 | 500 | 0.860 |
| T2d: Large amplitude | 25,000 | 0.635 | 5 | 0.15 | 100 | 0.060 |
| T2e: Very large amplitude | 25,000 | 1.27 | 5 | 0.15 | 50 | 0.020 |
| T2f: Higher preload | 41,000 | 0.46 | 5 | 0.15 | 500 | 0.195 |

**Calibration targets**:
- T2a glued nut: Calibrate `lambda_stage1` and `eta_max` so Stage I model matches 34% loss in 200 cycles
- T2b free nut: Calibrate `C_loosening` for Stage II rate to match the ~0.05 deg/cycle loosening rate
- T2c threshold: Verify model predicts no rotational loosening (Stage I only)

#### Case T3: Housari & Nassar 2007 — Friction Parametric (Paper 04)

**Why**: Systematic friction coefficient sweep. Directly calibrates friction evolution.

| Sub-case | mu_th | mu_b | Key observation |
|----------|-------|------|-----------------|
| T3a | 0.05 | 0.05 | Rapid loosening, complete loss < 50 cycles |
| T3b | 0.10 | 0.10 | Moderate loosening |
| T3c | 0.15 | 0.15 | Standard behavior |
| T3d | 0.20 | 0.20 | Slow loosening |
| T3e | 0.30 | 0.30 | Very slow, may not fully loosen |

**Calibration target**: Match the ranking and relative rates. Verify mu_critical prediction matches the threshold where loosening transitions from slow to fast.

#### Case T4: Nassar & Yang 2009 — Analytical Model (Paper 05)

**Why**: Complete closed-form reference solution. BAS implementation should reproduce the Nassar-Yang curves exactly.

**Calibration target**: BAS `NassarYangLooseningModel` class output must match the paper's equation predictions to < 1% error (model-to-model, not model-to-experiment).

---

### 2.2 Tier 2: Core Validation Cases (Test Set — Do Not Tune Parameters)

These cases verify the calibrated model against independent experiments.

| Case | Paper | Bolt | Key Test | Expected BAS Error |
|------|-------|------|----------|-------------------|
| V1 | 03 Zhang-Jiang 2006 | M12 | Clamped length effect (25, 38, 51 mm) | < 20% on final preload |
| V2 | 06 Yang-Nassar 2011 | 5/16"-24 UNC | Cap screw analytical + experimental | < 15% |
| V3 | 07 Nassar-Housari 2006 | M8, M10 | Pitch effect (1.0, 1.25, 1.5 mm) | < 20% |
| V4 | 08 Nassar-Housari 2007 | M10 | Hole clearance (3-10%) and thread fit | < 25% |
| V5 | 09 Yang 2019 | M10 | Variable amplitude D-N life curves | Factor of 2 |
| V6 | 10 Yang 2023 | M6, M8 | Phenomenological power-law model | < 15% |
| V7 | 11 Hattori 2010 | M6, M10, M16 | Critical slippage, size effect | < 20% |
| V8 | 17 Eccles 2010 | M8-M12 | Friction evolution, coating effects | < 15% on mu(N) |
| V9 | 18 Junker test | M8-M12 | DIN 65151 standard test, locking devices | Correct ranking |
| V10 | 20 Gong-Liu 2019 | M12 | FEA parametric (pitch, clearance, friction) | < 25% |
| V21 | 72 Liu 2017 | M10 | Axial pulsating tension, two-stage non-rotational loss | < 20% on Stage I fraction |
| V22 | 73 Cai 2016 | M10 | MoS₂/Cr₂O₃ coating effect on axial embedding | Correct coating ranking |
| V23 | 74 Liu 2018 | M12 | Torsional excitation, μ_bearing/μ_thread ratio stability | Correct stable/unstable prediction |
| V24 | 75 Liu 2019 | M12 | Torsional hysteresis loop, slip regime identification | Correct fretting-map regime |
| V25 | 79 Yang 2021 | M8 | Combined axial+transverse, R_factor failure mode map | R_critical boundary within 0.1 |
| V26 | 80 Du 2022 | M8 (4-bolt) | Random broadband PSD, three-stage loosening criterion | Correct stage at each PSD level |
| V27 | 83 Pai-Hess 2002 | 1/4"-20 UNC + UNF | Slip onset factor, fine vs coarse thread F_crit ratio | slip_onset_factor within 20% |
| V28 | 84 Pai-Hess 2003 | 1/4"-20 UNC (×4) | Multi-bolt cascade loosening; corner bolt first | Correct loosening order |
| V29 | 85 Bouzid 1995 | M20 NPS 4" flange | Gasket creep Norton-Bailey calibration (4 gasket types) | K_cr, n_cr within 15% |
| V30 | 87 Liu-Mi 2021 | M8–M12 | R_critical ≈ 0.55 universal failure-mode boundary | Correct failure mode for all 15 sub-cases |

### 2.3 Tier 3: Extended Validation (Specialized Phenomena)

| Case | Paper(s) | Phenomenon | What BAS Must Show |
|------|----------|------------|-------------------|
| V11 | 12 Eraliev 2021 | Thermal cycling (M12, DeltaT) | Correct preload loss direction/magnitude |
| V12 | 13 Yang 2021 | Combined axial + transverse (M8) | Interaction effect captured |
| V13 | 25 Rousseau 2025 | HDPE clamped members (M12) | Material-dependent loosening rate |
| V14 | 26 Yang 2025 | Variable amplitude multi-bolt | D-N curve and Miner's rule |
| V15 | 29 Karlsen 2022 | Large bolts M20-M42 | Size scaling correctness |
| V16 | 30 Nechache 2007 | Gasket creep (NPS 3"-52") | Long-term creep prediction |
| V17 | 31 den Otter 2020 | SS bolts in aluminum | CTE mismatch thermal loss |
| V18 | 33 Du 2025 | Sine-on-random vibration | Combined loading response |
| V19 | 47 Brown 2017 | High temp B7/B16 (385C) | Thermal relaxation |
| V20 | 71 Wiegand 2021 | VDI 2230 vs FEM (4-bolt flange) | Load introduction factor |
| V31 | 81 Ishimura 2010 | M10 flanged | Bending moment loosening, bearing gross-slide mechanism | Correct loosening direction |
| V32 | 82 Yokoyama 2012 | M10 | Rotary bending, elastic spring-back torsion | Phase offset effect captured |
| V33 | 86 Bouzid 2006 | M20 NPS 4" | Elastic interaction + creep combined in multi-bolt flange | Interaction term within 30% |
| V34 | 88 Abid 2014 | M20 NPS 4" | Dynamic internal pressure (harmonic vs step) | Harmonic 2× worse than step |
| V35 | 89 Bhattacharya 2010 | M4, M5 | Small bolt δ_critical scaling (δ ∝ d^0.82) | Size-law exponent within 0.15 |
| V36 | 90 Wei 2025 | M10 CFRP | CFRP bending vibration, two-stage embedding dominant | Correct dominant mechanism flag |
| V37 | 92 Su-Ye 2016 | M8–M10 CFRP | Viscoelastic logarithmic creep, temperature dependence | Doubling temperature ≤ 25°C |
| V38 | 94 Li 2022 | M10 → M30 (1:3) | Similitude joint-stiffness correction, frequency < 5.4% | Frequency error < 8% with correction |

### 2.4 Tier 4: Qualitative Validation (Trend Verification)

These papers provide trends but not enough digitized data for quantitative comparison.

| Paper(s) | What to Verify |
|----------|----------------|
| 14 Dinger-Friedrich 2011 | FEA contact state parameter (partial vs complete slip) |
| 15 Chen 2017 | Tightening process effect direction |
| 16 Izumi-Sakai | Thread slip before bearing slip |
| 19 Sandia/NASA | Modal excitation loosening mechanism |
| 23 Pai-Hess 2002 | 4 loosening process identification |
| 24 Sanclemente-Hess 2007 | DOE factor rankings match BAS sensitivity |
| 27 Li-Liu 2020 | Axial vs transverse: transverse is dominant |
| 28 Zhao 2023 | 7 anti-loosening devices: correct relative ranking |
| 32 Sase 1996 | 7 nut types: correct relative ranking |
| 34 Amano 2024 | Double-thread bolt improvement direction |
| 53 Liu 2021 | Self-loosening without external load (thermal/embedding) |
| 74–76 Liu torsional | Torsional stability criterion: μ_bearing > μ_thread → stable (opposite of Junker) |
| 87 Liu-Mi 2021 | R_critical ≈ 0.55 as universal fatigue/loosening failure-mode boundary |
| 90–91 Wei-Yang CFRP | CFRP embedding: non-rotational dominance (~70% of total loss), nut rotation ≤ 5% |
| 96–97 Schaumann | Large bolt (M36+) VDI non-conservatism: warn when d > 30 mm (+19% at M36, +33% at M64) |
| 93 Hu 2020 | Thermal + mechanical super-additive in CFRP: combined = 1.4 × (thermal + mechanical) |

---

## 3. Calibration Procedure

### 3.1 Phase 1: Fix Critical Bugs First

Before any calibration, the following issues from `IMPROVEMENT_ANALYSIS_Code_vs_Reference.md` MUST be resolved:

| Bug | Description | Impact on Calibration |
|-----|-------------|----------------------|
| **C1** | Distributed thread stiffness formula wrong | k_total will be wrong for all distributed-thread models |
| **C2** | Head stiffness 0.4 vs 0.5 inconsistency | 20% error in bolt stiffness propagates to all predictions |
| **C3** | Stress area uses wrong diameter (d3 vs d1) | ~3% error in A_t affects yield calculations |
| **C5** | Contact system not wired into solver | Cannot calibrate contact-based models at all |
| **H2** | System stiffness uses trace(K) | 5-10x overestimation of k_sys corrupts preload loss |
| **H3** | CoupledLooseningAnalyzer disconnected from contacts | Loosening model uses independent friction/wear models |
| **M1** | K-factor (nut factor) oversimplified | 22% error in torque-preload relation |
| **M8** | C_loosening hardcoded at 0.3 | Cannot calibrate to experimental data |
| **M9** | Thread and bearing friction assumed equal | Cannot reproduce separate-friction experiments |

**Estimated effort**: 3-4 days for an experienced developer to resolve all critical bugs.

### 3.2 Phase 2: Implement Validation Infrastructure

Create `tests/validation/` directory with the following structure:

```
tests/validation/
├── __init__.py
├── validation_cases.py          # ValidationCase dataclass + ExperimentalDataPoint
├── validation_runner.py         # Automated test runner
├── calibration_optimizer.py     # Parameter optimization (scipy.optimize)
├── validation_report.py         # Generate comparison plots and error metrics
├── data/
│   ├── lu_2024_m8.json          # Experimental data from Paper 01
│   ├── jiang_2003_m12.json      # Experimental data from Paper 02
│   ├── housari_2007_m10.json    # Experimental data from Paper 04
│   ├── nassar_yang_2009.json    # Analytical reference from Paper 05
│   ├── yang_nassar_2011.json    # Paper 06
│   ├── eccles_2010.json         # Paper 17 friction data
│   ├── hattori_2010.json        # Paper 11 critical slippage
│   └── ...                      # One file per paper with tabular data
└── results/
    ├── calibration_report.html  # Generated report
    └── plots/                   # Comparison plots
```

#### 3.2.1 ValidationCase Dataclass

```python
@dataclass
class ExperimentalDataPoint:
    """Single experimental measurement."""
    cycles: int
    preload_ratio: float              # F/F0
    preload_N: Optional[float] = None # Absolute preload (N)
    nut_rotation_deg: Optional[float] = None
    mu_thread: Optional[float] = None
    mu_bearing: Optional[float] = None
    wear_um: Optional[float] = None
    temperature_C: Optional[float] = None

@dataclass
class ValidationCase:
    """Complete test configuration with experimental data."""
    # Identification
    name: str                         # e.g., "Lu_2024_M8_baseline"
    paper_ref: str                    # e.g., "01"
    paper_citation: str               # Full citation
    tier: int                         # 1=calibration, 2=validation, 3=extended, 4=qualitative

    # Bolt geometry
    bolt_size: str                    # "M8x1.25"
    bolt_diameter_mm: float
    pitch_mm: float
    bolt_class: str                   # "8.8", "10.9", "12.9"
    stress_area_mm2: float
    pitch_diameter_mm: float
    head_af_mm: float                 # Across-flats
    head_height_mm: float
    nut_height_mm: float
    hole_diameter_mm: float
    grip_length_mm: float

    # Material
    E_bolt_MPa: float = 210000.0
    E_member_MPa: float = 200000.0
    Sy_bolt_MPa: float = 640.0

    # Loading
    initial_preload_N: float
    preload_percent_yield: float
    transverse_displacement_mm: float
    frequency_Hz: float
    n_cycles: int
    loading_type: str = "TRANSVERSE"  # TRANSVERSE, AXIAL, COMBINED, THERMAL

    # Friction
    mu_thread_initial: float
    mu_bearing_initial: float
    lubricated: bool = False
    surface_condition: str = "dry"    # dry, oiled, MoS2, zinc-plated

    # Expected outcomes
    expected_final_preload_ratio: float
    expected_loosening_onset_cycle: Optional[int] = None
    expected_total_loosening_deg: Optional[float] = None
    expected_loosening_rate_deg_per_cycle: Optional[float] = None

    # Experimental data points for curve comparison
    experimental_data: List[ExperimentalDataPoint] = field(default_factory=list)

    # Metadata
    notes: str = ""
    data_quality: str = "digitized"   # digitized, exact, approximate
```

#### 3.2.2 Validation Runner

```python
class ValidationRunner:
    """Run BAS analysis for a validation case and compare with experimental data."""

    def run_case(self, case: ValidationCase) -> ValidationResult:
        """
        1. Build MSD model from case geometry
        2. Set loading parameters
        3. Run CoupledLooseningAnalyzer
        4. Compare with experimental data
        5. Return error metrics
        """
        # Build model
        model = self._build_model(case)

        # Run analysis
        analyzer = CoupledLooseningAnalyzer(model, ...)
        result = analyzer.analyze()

        # Compare
        errors = self._compute_errors(result, case.experimental_data)

        return ValidationResult(case=case, prediction=result, errors=errors)

    def _compute_errors(self, prediction, experimental_data):
        """Compute error metrics at experimental data points."""
        errors = {}

        # Interpolate prediction to experimental cycle counts
        pred_cycles = prediction.cycles
        pred_ratio = prediction.preload_ratio

        for point in experimental_data:
            pred_at_cycle = np.interp(point.cycles, pred_cycles, pred_ratio)
            abs_error = abs(pred_at_cycle - point.preload_ratio)
            rel_error = abs_error / max(point.preload_ratio, 0.01)
            errors[point.cycles] = {
                'predicted': pred_at_cycle,
                'experimental': point.preload_ratio,
                'abs_error': abs_error,
                'rel_error': rel_error
            }

        # Summary metrics
        errors['MAE'] = np.mean([e['abs_error'] for e in errors.values() if isinstance(e, dict)])
        errors['RMSE'] = np.sqrt(np.mean([e['abs_error']**2 for e in errors.values() if isinstance(e, dict)]))
        errors['max_error'] = max(e['abs_error'] for e in errors.values() if isinstance(e, dict))

        return errors
```

#### 3.2.3 Calibration Optimizer

```python
class CalibrationOptimizer:
    """Optimize free parameters against training data."""

    def calibrate(self, training_cases: List[ValidationCase]) -> Dict[str, float]:
        """
        Use scipy.optimize.minimize to find best-fit parameters.

        Parameters optimized:
        - C_loosening (0.01 - 1.0)
        - mu_peak (mu_initial - 0.30)
        - mu_steady (0.03 - mu_initial)
        - N_phase1 (10 - 200)
        - N_phase2 (100 - 2000)
        - K_wear (1e-9 - 1e-5)
        - lambda_stage1 (0.005 - 0.10)
        - eta_max (0.05 - 0.50)
        """
        from scipy.optimize import minimize, differential_evolution

        def objective(params):
            """Total RMSE across all training cases."""
            C_loosening, mu_peak, mu_steady, N_phase1, K_wear, lambda_s1, eta_max = params

            total_error = 0.0
            for case in training_cases:
                result = self._run_with_params(case, params)
                errors = self._compute_errors(result, case.experimental_data)
                total_error += errors['RMSE'] ** 2

            return total_error / len(training_cases)

        # Bounds for each parameter
        bounds = [
            (0.01, 1.0),     # C_loosening
            (0.12, 0.30),    # mu_peak
            (0.03, 0.12),    # mu_steady
            (10, 200),       # N_phase1
            (1e-9, 1e-5),    # K_wear
            (0.005, 0.10),   # lambda_stage1
            (0.05, 0.50),    # eta_max
        ]

        result = differential_evolution(objective, bounds, maxiter=100,
                                         seed=42, tol=1e-4)

        return {
            'C_loosening': result.x[0],
            'mu_peak': result.x[1],
            'mu_steady': result.x[2],
            'N_phase1': result.x[3],
            'K_wear': result.x[4],
            'lambda_stage1': result.x[5],
            'eta_max': result.x[6],
            'total_RMSE': np.sqrt(result.fun),
        }
```

### 3.3 Phase 3: Calibration Execution

#### Step 1: Calibrate Stage I Parameters (Jiang Glued-Nut Data)

Using **Case T2a** (glued nut, no rotation):

```
Target: F/F0 = 0.66 at N=200 (34% loss from pure non-rotational mechanisms)

Parameters to tune:
  lambda_stage1 → controls rate of Stage I loss
  eta_max → controls maximum Stage I fraction

Expected result:
  lambda_stage1 ≈ 0.02-0.04 per cycle
  eta_max ≈ 0.30-0.40
```

**Validation**: After calibrating on T2a (delta=0.46mm), predict T2c (delta=0.254mm) — Stage I loss should be smaller (~14% at 500 cycles, near threshold).

#### Step 2: Calibrate C_loosening (Lu 2024 Baseline)

Using **Case T1a** (M8, 22 Nm, 1.0 mm, 1 Hz):

```
Target: Match F/F0 at cycles 5, 10, 20, 50, 100:
  N=5:   F/F0 = 0.648
  N=10:  F/F0 = 0.475
  N=20:  F/F0 = 0.277
  N=50:  F/F0 = 0.104
  N=100: F/F0 = 0.064

With Stage I calibrated from Step 1:
  Stage II must account for the rapid decay after Stage I saturates.

Tune C_loosening to minimize RMSE across all 6 data points.
```

**Cross-validation**: After calibrating on T1a, predict T1b-T1g without changing C_loosening. Only mu_initial and preload change. Check that the model captures the parametric trends correctly.

#### Step 3: Calibrate Friction Evolution (Eccles Data)

Using **Paper 17** (Eccles 2010) friction evolution measurements:

```
Target: Match mu_thread(N) and mu_bearing(N) curves for:
  - Dry steel-on-steel
  - Zinc-plated
  - MoS2 coated

Tune:
  mu_peak / mu_initial ratio (running-in amplification)
  N_phase1 (running-in duration)
  mu_steady (long-term value)
```

#### Step 4: Calibrate Wear Model (Zhang 2019 FEA Data)

Using **Paper 35** (Zhang 2019) wear depth predictions and **Paper 17** (Eccles) experimental wear:

```
Target: Archard wear coefficient K so that:
  - Predicted wear depth matches magnitude order (um scale)
  - Wear-induced preload loss adds correctly to rotational loss

Tune: K_wear and H_surface
```

#### Step 5: Global Optimization

Run the `CalibrationOptimizer` with Cases T1a, T1d, T1e, T2a, T2b, T2d simultaneously. This finds the parameter set that minimizes total error across all training configurations.

### 3.4 Phase 4: Validation Execution

With all parameters frozen from Phase 3, run the Tier 2 validation cases (V1-V10) and compute error metrics.

#### Acceptance Criteria

| Metric | Target | Action if Failed |
|--------|--------|-----------------|
| MAE on F/F0 | < 0.10 for each case | Review model assumptions, check input parameters |
| RMSE on F/F0 | < 0.15 for each case | Consider case-specific calibration factors |
| Loosening onset cycle | Within factor of 2 | Check critical friction calculation |
| D-N curve exponent | Within 0.5 of experimental m | Review slip threshold model |
| Trend direction | 100% correct | Bug in model physics |
| Parametric ranking | Correct order for all sweeps | Check parameter sensitivity mapping |

---

## 4. Validation Report Format

### 4.1 Per-Case Report Card

For each validation case, generate:

```
╔═══════════════════════════════════════════════════════════════╗
║  Case: Jiang_2003_M12_baseline (V2b)                        ║
║  Paper: Jiang et al. (2003), ASME J. Mech. Des.             ║
║  Bolt: M12x1.75, Class 10.9                                 ║
║  Loading: F0=25 kN, delta=0.46 mm, f=5 Hz                   ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Preload Decay Comparison:                                   ║
║                                                               ║
║  1.0 ┤●──────────────────────── Experimental                ║
║      │  ●·····                   BAS Prediction              ║
║  0.8 ┤    ●  ·····                                           ║
║      │       ●   ·····                                       ║
║  0.6 ┤           ●  ····                                     ║
║      │               ·  ●                                    ║
║  0.4 ┤                   · ·                                 ║
║      │                     ●  ·                              ║
║  0.2 ┤                        ● ·                            ║
║      │                           ●·                          ║
║  0.0 ┤────────────────────────────●──                        ║
║      0    50   100   150   200   250                         ║
║                  Cycles (N)                                  ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║  Error Metrics:                                               ║
║    MAE  = 0.052                 ✅ (< 0.10)                  ║
║    RMSE = 0.068                 ✅ (< 0.15)                  ║
║    Max Error = 0.11 at N=50     ⚠️  (slightly high)          ║
║    Onset: BAS=35, Exp=50 cycles ✅ (factor 1.4)             ║
║                                                               ║
║  VERDICT: PASS                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### 4.2 Summary Dashboard

Generate a summary table and plots:

1. **Scatter plot**: Predicted vs. Experimental F/F0 at all data points from all cases (should cluster near 45-degree line)
2. **Error histogram**: Distribution of absolute errors across all data points
3. **Parametric validation matrix**: 2D heatmap of error by (bolt size x amplitude)
4. **D-N validation plot**: Overlay of BAS D-N predictions vs. experimental D-N data from Papers 09, 26
5. **Friction evolution validation**: BAS mu(N) vs. Eccles (Paper 17) measured mu(N)

### 4.3 Automated Test Integration

Add to `pytest`:

```python
# tests/test_validation.py

@pytest.mark.parametrize("case_name", [
    "Lu_2024_M8_baseline",
    "Jiang_2003_M12_baseline",
    "Jiang_2003_M12_glued_nut",
    "Yang_Nassar_2011_UNC",
    # ... all Tier 2 cases
])
def test_validation_case(case_name):
    """Each validation case must pass acceptance criteria."""
    case = load_validation_case(case_name)
    result = ValidationRunner().run_case(case)

    assert result.errors['MAE'] < 0.10, f"MAE={result.errors['MAE']:.3f} > 0.10"
    assert result.errors['RMSE'] < 0.15, f"RMSE={result.errors['RMSE']:.3f} > 0.15"

    # Trend check: preload should decrease monotonically
    assert all(result.prediction.preload_ratio[i] >= result.prediction.preload_ratio[i+1]
               for i in range(len(result.prediction.preload_ratio)-1))
```

---

## 5. Specific Model Validations

### 5.1 Preload Loss Models (preload_loss_models.py)

| Model | Validate Against | Acceptance |
|-------|-----------------|------------|
| `SingleExponentialModel` | Papers 01, 02 late-stage data | R2 > 0.90 on log(F) vs N |
| `DoubleExponentialModel` | Paper 01 full curves (A1, B1, A2, B2 fitted) | R2 > 0.95 |
| `StretchedExponentialModel` | Paper 01 T=22Nm data | R2 > 0.90 |
| `VDI2230EmbeddingModel` | Paper 02 glued-nut data (Stage I only) | Match 10-34% loss range |
| `JiangTwoStageModel` | Paper 02 combined Stage I+II | Match transition point within 30% |
| `JiangThreeStageModel` | Paper 02 full dataset | Match all three stages |
| `PowerLawModel` (F=a*N^b) | Paper 01 Lu allometric fits | Match published a, b values |
| `NortonBaileyCreepModel` | Paper 30 Nechache gasket creep + Papers 85/86 Bouzid (4 gasket types) | Match 100k-hour predictions; K_cr/n_cr within 15% |
| `ThermalEffectsModel` | Paper 12 Eraliev thermal cycling + Paper 93 Hu CFRP thermal | Correct preload change direction; CFRP loss ∝ ΔT^1.8 |
| `ViscoelasticCFRPCreepModel` (new) | Papers 92 Su-Ye + 93 Hu | Logarithmic decay ΔF/F₀ = A·ln(1+t/τ); A doubles per ~20°C; R² > 0.99 |
| Axial two-stage non-rotational model | Papers 72 Liu 2017 + 73 Cai 2016 | Stage I fraction matches amplitude sweep (4 levels); coating ranking correct |

### 5.2 Friction Models (friction_models.py)

| Model | Validate Against | Acceptance |
|-------|-----------------|------------|
| `CoulombFriction` | Paper 21 VDI friction tables | Correct mu for each surface condition |
| `LuGreFriction` | Paper 05 Nassar-Yang stick-slip analysis | Qualitative stick-slip behavior |
| `FrictionEvolutionModel` (3-phase) | Paper 17 Eccles evolution data | Match 3-phase shape and timing |
| `StribeckModel` | Paper 04 velocity-dependent friction | Correct velocity-friction curve shape |
| `WearEvolutionModel` (Archard) | Paper 35 Zhang FEA wear depths | Order-of-magnitude agreement |
| Torsional friction ratio stability criterion | Papers 74–76 Liu torsional series | μ_bearing/μ_thread > 1 → stable; correct 3 evolution types (A/B/C) |
| Coating friction multiplier (MoS₂, Cr₂O₃, zinc) | Paper 73 Cai 2016 coating sweep | MoS₂ Stage I −40%; zinc fatigue penalty −10 to −13% (Papers 96/97) |

### 5.3 Coupled Loosening Analyzer

| Aspect | Validate Against | Acceptance |
|--------|-----------------|------------|
| Torque balance (T_pitch vs T_resistance) | Paper 05 Nassar-Yang equations | < 5% difference |
| Critical friction coefficient | Paper 11 Hattori slippage data | < 10% on mu_critical |
| Loosening rate (deg/cycle) | Paper 02 Jiang nut rotation data | Within factor 2 |
| Phase classification | Paper 02 Stage I/II transition | Correct phase at each cycle |
| Preload decay shape | Papers 01, 02, 06 experimental curves | MAE < 0.10 |
| D-N curve generation | Papers 09, 26 displacement-life data | Exponent within 0.5 |
| Axial phase classification `_classify_phase_axial()` | Papers 72 Liu + 73 Cai axial datasets | Correct AXIAL_STAGE_I/II/III at each cycle count |
| R_factor failure mode boundary | Papers 79 Yang + 87 Liu-Mi (R_critical ≈ 0.55) | Correct failure mode (loosening vs fatigue) for R = −1, 0, +0.1, +0.5 |
| Random vibration three-stage criterion | Paper 80 Du 2022 broadband PSD | Correct stage (Steady/Transition/Loosen) for each PSD level |
| Multi-bolt cascade loosening sequence | Paper 84 Pai-Hess 2003 4-bolt | Corner bolt loosens first; individual preload decay within factor 2 |
| VDI size-effect non-conservatism warning | Papers 96/97 Schaumann M36/M64 | Warning fires for d > 30 mm; overestimate factor within 5% of literature |

### 5.4 NassarYangLooseningModel (Analytical)

This model should produce EXACT agreement with the Nassar-Yang 2009 paper equations.

| Verification | Source | Acceptance |
|-------------|--------|------------|
| Critical thread force | Eq. in Paper 05 | < 1% |
| Critical bearing force | Eq. in Paper 05 | < 1% |
| Net loosening torque | Eq. in Paper 05 | < 1% |
| Rotation per cycle | Eq. in Paper 05 | < 2% |
| Preload decay curve shape | Paper 05 Figure 3 | Visual match |

---

## 6. Sensitivity Analysis

### 6.1 One-at-a-Time (OAT) Parameter Sweeps

For each free parameter, sweep through its valid range while holding others at calibrated values. Plot the effect on key output metrics.

| Parameter | Sweep Range | Output Metric |
|-----------|-------------|---------------|
| C_loosening | 0.05 - 1.0 | Cycles to 50% preload loss |
| mu_initial | 0.05 - 0.30 | Loosening onset cycle |
| F_preload | 10% - 90% yield | Final preload ratio at N=1000 |
| delta (amplitude) | 0.1 - 2.0 mm | D-N loosening life |
| Bolt diameter | M6 - M42 | Normalized loosening rate |
| Clamped length | 1d - 5d | Stage I loss fraction |
| Grip/diameter ratio | 1.5 - 6.0 | Threshold amplitude |

### 6.2 Sobol Sensitivity Indices

Run a Monte Carlo analysis (N=10,000 samples) to compute first-order and total Sobol indices for each parameter. This identifies which parameters most influence the predictions and where calibration effort should focus.

**Priority based on literature**: From Paper 24 (Sanclemente-Hess DOE), the ANOVA ranking is:
1. Transverse displacement amplitude (dominant)
2. Thread pitch (significant)
3. Preload level (significant)
4. Bearing friction (moderate)
5. Thread friction (moderate)
6. Bolt diameter (moderate)
7. Frequency (negligible)

BAS sensitivity analysis should reproduce this ranking.

---

## 7. Implementation Roadmap

### 7.1 Timeline

| Week | Task | Deliverables |
|------|------|-------------|
| **1** | Fix C1-C5 bugs, standardize formulas | All critical bugs resolved, unit tests pass |
| **2** | Fix H2, M1, M8, M9 (system stiffness, K-factor, C_loosening parameterization, separate thread/bearing mu) | Configurable parameters in analyzer |
| **3** | Create validation infrastructure (dataclasses, runner, data files) | `tests/validation/` working with T1a case |
| **4** | Extract experimental data from Papers 01-20 into JSON format | 10+ JSON data files |
| **5** | Phase 3: Calibrate Stage I params (Jiang glued-nut) | lambda_stage1, eta_max calibrated |
| **6** | Phase 3: Calibrate C_loosening (Lu 2024 baseline + parametric) | C_loosening optimized |
| **7** | Phase 3: Calibrate friction evolution + wear (Eccles, Zhang data) | All free parameters set |
| **8** | Phase 3: Global optimization across training set | Final calibrated parameter set |
| **9** | Phase 4: Run Tier 2 validation (V1-V10) | Validation report for 10 core cases |
| **10** | Phase 4: Run Tier 3 validation (V11-V20) | Extended validation report |
| **11** | Sensitivity analysis (OAT + Sobol) | Sensitivity report, parameter rankings |
| **12** | Documentation and integration (core 12 weeks complete) | Final calibration report, pytest integration |
| **13** | Axial loading validation (V21/V22 — Papers 72/73) | `_classify_phase_axial()` validated; axial JSON data files |
| **14** | Torsional + R-factor validation (V23–V26, V30 — Papers 74–76, 79, 80, 87) | Torsional stability criterion confirmed; R_critical boundary verified |
| **15** | Gasket creep calibration + multi-bolt cascade (V28/V29 — Papers 83–86) | Norton-Bailey CFRP/gasket params; multi-bolt cascade data files |
| **16** | CFRP, small bolt, large bolt, similitude validation (V35–V38 — Papers 89–97) | All Tier 3 extended cases pass; large-bolt warning in report |

### 7.2 Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `tests/validation/__init__.py` | CREATE | Package init |
| `tests/validation/validation_cases.py` | CREATE | Dataclass definitions |
| `tests/validation/validation_runner.py` | CREATE | Automated test runner |
| `tests/validation/calibration_optimizer.py` | CREATE | Parameter optimization |
| `tests/validation/validation_report.py` | CREATE | Report generation (HTML + plots) |
| `tests/validation/data/*.json` | CREATE | One per paper, extracted experimental data |
| `tests/test_validation.py` | CREATE | Pytest parametric tests |
| `coupled_loosening_analyzer.py` | MODIFY | Make C_loosening, mu params configurable |
| `preload_loss_models.py` | MODIFY | Fix K-factor formula (M1), add residual floor (H6) |
| `element.py` | MODIFY | Fix C1, C2, C3 (stiffness and stress area) |
| `model.py` | MODIFY | Fix H2 (system stiffness) |
| `friction_models.py` | MODIFY | Fix C4 (Iwan state), unify friction evolution (L6) |

### 7.3 Success Criteria

The calibration and validation is complete when:

1. All Tier 1 training cases: MAE < 0.08 on F/F0
2. All Tier 2 validation cases: MAE < 0.10 on F/F0
3. All Tier 2 validation cases: RMSE < 0.15 on F/F0
4. Loosening onset prediction: within factor 2 for all cases
5. D-N curve: exponent m within 0.5 of experimental for M8, M10, M12
6. DOE parameter ranking: matches Sanclemente-Hess 2007 ANOVA order
7. Nassar-Yang model: < 2% error vs. analytical equations
8. All `pytest` validation tests pass in CI

---

## 8. Data Extraction Priority

### Papers with Most Complete Digitized Data (extract to JSON first)

| Priority | Paper | Data Points | Configurations | Data Type |
|----------|-------|-------------|----------------|-----------|
| **1** | 01 Lu 2024 | ~70 | 14 configs | F/F0 vs N (digitized) |
| **2** | 02 Jiang 2003/2004 | ~50 | 7 configs + D-N curve | F/F0, rotation, D-N |
| **3** | 05 Nassar-Yang 2009 | Analytical | Equation reference | Torque, rotation, F |
| **4** | 17 Eccles 2010 | ~40 | 3 surface conditions | mu(N), F/F0(N) |
| **5** | 11 Hattori 2010 | ~20 | 3 bolt sizes | Critical slippage |
| **6** | 06 Yang-Nassar 2011 | ~30 | Analytical + experimental | F/F0, rotation |
| **7** | 09 Yang 2019 | ~20 | D-N life curves | N_L vs delta |
| **8** | 10 Yang 2023 | ~15 | M6, M8 phenomenological | F/F0 vs N |
| **9** | 04 Housari 2007 | ~25 | 5 friction levels | F/F0 vs N |
| **10** | 07 Nassar-Housari 2006 | ~15 | M8, M10 pitch effect | F/F0 vs N |
| **11** | 72 Liu 2017 | ~25 | M10 axial, 4 amplitude levels + 3 coatings | F/F0 vs N (axial) |
| **12** | 80 Du 2022 | ~20 | M8 4-bolt random PSD, 3 tightening torques | PSD vs stage threshold |
| **13** | 83 Pai-Hess 2002 | ~20 | UNC/UNF M6.35–M12 thread type + slip types | F_crit vs bolt size |
| **14** | 85 Bouzid 1995 | ~30 | 4 gasket types, Norton-Bailey creep params | ΔF/F0 vs time (gasket) |
| **15** | 87 Liu-Mi 2021 | ~30 | M8–M12, 15 R×amplitude sub-cases | Failure mode map |
| **16** | 92 Su-Ye 2016 | ~25 | M8–M10 CFRP, 3 preloads × 4 temperatures | F/F0 vs cycles (CFRP) |

### Data Format (JSON)

```json
{
    "paper_ref": "01",
    "paper_citation": "Lu et al. (2024), Sensors 24(11):3306",
    "configurations": [
        {
            "config_id": "T1a_baseline",
            "bolt_size": "M8x1.25",
            "bolt_class": "8.8",
            "initial_preload_N": 11567,
            "displacement_mm": 1.0,
            "frequency_Hz": 1.0,
            "mu_estimated": 0.20,
            "lubricated": false,
            "grip_length_mm": 24.0,
            "data_quality": "digitized_from_figure_7",
            "data_points": [
                {"cycles": 0, "preload_ratio": 1.000},
                {"cycles": 5, "preload_ratio": 0.648},
                {"cycles": 10, "preload_ratio": 0.475},
                {"cycles": 20, "preload_ratio": 0.277},
                {"cycles": 50, "preload_ratio": 0.104},
                {"cycles": 100, "preload_ratio": 0.064}
            ]
        }
    ]
}
```

---

## 9. Comparison with Literature Recommendations

### 9.1 What the Literature Says About Model Accuracy

| Source | Claimed Accuracy | Our Target |
|--------|-----------------|------------|
| Nassar-Yang (2009) analytical | ~10% error vs. FEA | < 5% model-to-model |
| Jiang (2003) two-stage | Qualitative match | < 15% on F/F0 |
| Yang (2023) phenomenological | R2 > 0.95 for fitted curves | R2 > 0.90 with calibrated params |
| Lu (2024) allometric | R2 > 0.855 | R2 > 0.90 with double-exp |
| Dinger (2011) FEA | < 5% vs. experiment | Reference for contact mechanics |
| Gong-Liu (2019) FEA parametric | < 10% vs. experiment | < 25% for simplified MSD model |

### 9.2 Known Limitations of MSD Approach

The BAS uses a **lumped Mass-Spring-Damper** model, not full 3D FEA. Known limitations:

1. **No spatial resolution** of thread stress distribution (unlike ABAQUS contact models)
2. **No bending effects** (unlike beam FE models)
3. **No contact pressure distribution** (uniform assumption)
4. **Friction is bulk, not local** (no partial-slip to full-slip transition per contact patch)
5. **No ratchetting plasticity** (Stage I modeled empirically, not via Armstrong-Frederick)

These limitations mean BAS predictions will inherently be less accurate than dedicated FEA for complex geometries. The target is **engineering accuracy** (< 20% error) rather than **research accuracy** (< 5% error).

### 9.3 When BAS Should NOT Be Used Alone

Based on the literature, BAS results should be supplemented with FEA for:
- Eccentric loading on multi-bolt patterns (Paper 71 shows VDI overestimates by up to 2x)
- Gasket creep beyond 10,000 hours (Paper 30 shows significant nonlinearity)
- Thermal cycling with dissimilar materials (Papers 31, 65 show complex interactions)
- Anti-loosening device comparison (Paper 28 shows FEA needed for device-specific mechanisms)
- Very large bolts M36+ (Papers 29, 96/97: VDI 2230 non-conservative by 19–33%; zinc coating adds additional −10–13% fatigue penalty not modelled by VDI)
- **CFRP or composite clamped members** (Papers 90–93): non-rotational embedding dominates (~70% of loss); viscoelastic matrix creep requires dedicated two-stage CFRP model; rate doubles per ~20°C temperature rise; BAS metal-joint model will underpredict total loss
- **Torsional excitation loading** (Papers 74–76): stability depends on μ_bearing/μ_thread ratio; reverse of Junker criterion; BAS transverse model does not capture this regime
- **Small bolts M3–M6** (Paper 89): δ_critical scales as d^0.82, not linearly; BAS slip_onset_factor must be adjusted as 0.46×(d/8)^0.15 for sub-M8 sizes
- **Pure random/broadband PSD excitation** (Paper 80): BAS currently requires sinusoidal amplitude input; random PSD three-stage threshold requires spectral analysis outside BAS scope

---

## Appendix A: Experimental Data Reference Quick-Lookup

| Bolt Size / Condition | Papers with Data | Best Calibration Paper | Key Parameters |
|----------------------|-----------------|----------------------|----------------|
| M4, M5 (small bolts) | **89** | **89 (Bhattacharya 2010)** | δ_critical ∝ d^0.82; slip_onset = 0.46×(d/8)^0.15 |
| M6 | 10, 11, 26 | 10 (Yang 2023) | Phenomenological model |
| M8 | 01, 13, 26, 79, 80, 87 | **01 (Lu 2024)** | 14 configs, parametric; R-factor map (79, 87); random PSD (80) |
| M10 | 04, 07, 08, 09, 11, 14, 27, 32, 37, 38, 72, 73, 81, 82 | 04 (Housari) + 09 (Yang) | Friction sweep + D-N; axial (72/73); bending (81/82) |
| M12 | **02**, 03, 12, 15, 20, 25, 34, 41, 44, 45, 74, 75, 76 | **02 (Jiang 2003)** | Stage I/II, 100+ specimens; torsional series (74–76) |
| M16 | 11, 53, 69 | 11 (Hattori) | Critical slippage |
| M20-M42 | 29, 59, 60, 61, 62, 85, 86, 88 | 29 (Karlsen) + 85/86 (Bouzid gasket) | Large bolt scaling; gasket creep calibration |
| M36, M64 (offshore/WT) | **96, 97** | **96/97 (Schaumann 2009/2015)** | VDI 2230 non-conservative: +19% at M36, +33% at M64; zinc −13% |
| UNC (inch) | 06, 23, 24, 39, 43, 83, 84 | 06 (Yang-Nassar) + 24 (Sanclemente) + 83 (Pai-Hess) | DOE rankings; UNF thread advantage +29% F_crit; multi-bolt cascade (84) |
| CFRP clamped | **90, 91, 92, 93** | **92 (Su-Ye 2016)** | Viscoelastic creep ΔF = A·ln(1+t/τ); non-rotational dominant; thermal ×1.4 interaction (93) |
| Torsional loading | **74, 75, 76** | **74 (Liu 2018)** | μ_bearing/μ_thread stability criterion; 3 evolution types A/B/C |
| High-temp | 30, 31, 47, 48, 49, 50 | 47 (Brown B7/B16) | Thermal relaxation |

## Appendix B: Critical Formulas to Validate

### B.1 Nassar-Yang Critical Friction

```
mu_critical = (p / (2*pi*r_t)) * cos(alpha) / [1 + (r_be/r_t)*cos(alpha)]
```

For M12x1.75: mu_critical = (1.75 / (2*pi*5.43)) * cos(30) / [1 + (7.6/5.43)*cos(30)] = 0.0256 * 0.866 / [1 + 1.212] = 0.0222 / 2.212 = **0.010**

This is very low -- it means any friction above ~0.01 prevents loosening in theory. The practical threshold is higher because dynamic effects, inertia, and partial slip reduce the effective resistance. Literature reports practical mu_critical in the range **0.04-0.08** for metric bolts.

### B.2 VDI 2230 K-Factor

```
K = (d2/(2d)) * [p/(pi*d2) + mu_th/cos(alpha)] + mu_b * D_km / (2d)
```

For M12x1.75, mu=0.12:
K = (10.863/24) * [1.75/(pi*10.863) + 0.12/cos(30)] + 0.12 * 15.2 / 24
K = 0.4526 * [0.0513 + 0.1386] + 0.076
K = 0.4526 * 0.1899 + 0.076
K = 0.0859 + 0.076 = **0.162**

Current BAS approximation: K = 0.16 + 0.5*0.12 = **0.22** (36% too high!)

### B.3 Preload per Degree of Nut Rotation

```
dF/d_theta = k_sys * p / 360
```

For M12, k_sys ~ 250,000 N/mm:
dF/d_theta = 250,000 * 1.75 / 360 = **1,215 N/deg**

So 0.05 deg/cycle loosening rate = 60.8 N/cycle preload loss at F0=50 kN.
At 250 cycles: 15,200 N lost = 30.4% preload loss.

This aligns with Paper 02 experimental data (F/F0 = 0.08 at 250 cycles for delta=0.46mm).
