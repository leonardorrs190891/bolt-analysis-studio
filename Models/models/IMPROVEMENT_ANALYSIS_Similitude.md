# Improvement Analysis: Similitude and Scaling Analysis

## Overview

This document analyzes the Similitude module (`core/similitude/similitude.py`, `similitude_plots.py`, `loosening_similitude.py`, `gui/similitude_tab.py`) for bugs, gaps, missing features, and improvement opportunities. Findings are compared against the reference formulation in Part IX (Similitude and Scaling Analysis) and informed by recent literature on structural similitude, bolted joint scaling, and distorted similitude methods.

**Last updated**: 2026-02-16

## Implementation Status (Updated 2026-02-16)

### CRITICAL - All Fixed
- [x] **CS1** - Pi5 hardcoded: Now computed from `PrototypeData.force_introduction_factor` using VDI 2230 stiffness model
- [x] **CS2** - Material dissimilarity: `SimilitudeAnalysis` now accepts `model_elastic_modulus` and `model_density`, propagates to `ScaleFactors`
- [x] **CS3** - Stress area in PrototypeData: Fixed to use `d1 = d - 1.0825p` (minor diameter per ISO 898-1)

### HIGH - Mostly Implemented
- [x] **HS1** - Thermal similitude: Added thermal parameters, Pi_th group, thermal_time scale factor
- [x] **HS2** - Fatigue size effect: Added Kuguel correction in scale effects
- [x] **HS5** - Scale effect uncertainty: Added uncertainty_low/high fields
- [x] **HS6** - Distorted similitude: Added DistortedScaleFactors dataclass
- [ ] **HS3** - Lubrication regime assessment (planned)
- [ ] **HS4** - Multi-scale validation framework (planned)
- [ ] **HS7** - Pi-group cross-referencing (planned)

### MEDIUM - Partially Implemented
- [ ] **MS1** - Loading pattern in multi-bolt reduction (planned)
- [x] **MS2** - Thread pitch mismatch assessment: `assess_pitch_mismatch()` in `loosening_similitude.py`
- [ ] **MS3** - Uncertainty propagation (Monte Carlo) (planned)
- [ ] **MS4** - Equivalent single bolt formula modes (planned)
- [ ] **MS5** - Non-metric bolt sizes (planned)
- [x] **MS6** - Dynamic similitude verification
- [ ] **MS7** - Experimental data import (planned)
- [x] **MS8** - Scale factor sensitivity analysis

---

## CRITICAL — Bugs That Produce Wrong Results

### CS1. Pi5 (Joint Constant) Hardcoded at 0.22
**File**: `similitude.py`, `_calculate_pi_groups()` method
**Reference**: Part IX, Section 38.2 — Π₅ = C = k_b/(k_b + k_m)

Both prototype and model Joint Constant Φ are hardcoded to 0.22, regardless of the actual bolt and member stiffness values in `PrototypeData`. Since this Pi-group always matches (both set to 0.22), the analysis never detects deviations in the load introduction factor — one of the most important parameters governing bolted joint behavior.

**Impact**: Pi-group match assessment is unreliable. A model with poor stiffness ratio preservation will still show "Excellent" for Π₅.

**Fix**: Compute from actual stiffness:
```python
def _compute_joint_constant(self, proto: PrototypeData) -> float:
    """VDI 2230 load introduction factor."""
    # Bolt stiffness (series of head + shank + thread)
    d = proto.bolt_diameter / 1000  # mm to m
    L = proto.grip_length / 1000
    E = proto.bolt_elastic_modulus * 1e6  # MPa to Pa
    At = proto.tensile_stress_area * 1e-6  # mm² to m²
    A_shank = np.pi / 4 * d**2

    k_head = 0.5 * E * d
    k_shank = E * A_shank / (L * 0.4)  # unthreaded portion ~40% of grip
    k_thread = E * At / (L * 0.6)      # threaded portion ~60% of grip
    k_bolt = 1.0 / (1/k_head + 1/k_shank + 1/k_thread)

    # Member stiffness (VDI 2230 frustum model)
    t = proto.flange_thickness / 1000
    E_m = proto.member_elastic_modulus * 1e6
    d_w = proto.washer_outer_diameter / 1000 if proto.washer_outer_diameter > 0 else 1.6 * d
    k_member = E_m * d * np.pi / (2 * np.log(5)) * (t / d)  # simplified

    return k_bolt / (k_bolt + k_member)
```

---

### CS2. Material Dissimilarity Modes Produce Identical Results
**File**: `similitude.py`, `ScaleFactors` initialization
**Reference**: Part IX, Section 36.4 — Three material similarity classifications

`MaterialSimilarity.SIMILAR` and `DIFFERENT` produce the same `ScaleFactors` as `SAME` because `elastic_modulus_ratio` and `density_ratio` always default to 1.0. The constructor accepts these parameters, but `SimilitudeAnalysis.__init__()` never passes them.

**Impact**: For mixed-material joints (e.g., A286 stainless bolt in 6061 aluminum flange), all derived scale factors are wrong. Force, frequency, velocity, and acceleration scale factors depend on E_m/E_p and ρ_m/ρ_p.

**Fix**: When material similarity is SIMILAR or DIFFERENT, require model material properties and compute ratios:
```python
if self.material_similarity != MaterialSimilarity.SAME:
    E_ratio = model_E / prototype_E
    rho_ratio = model_rho / prototype_rho
    self.scales = ScaleFactors(
        geometric=lambda_,
        elastic_modulus_ratio=E_ratio,
        density_ratio=rho_ratio
    )
```

---

### CS3. Loosening Curve Transformation Uses Incorrect Cycle Scaling
**File**: `loosening_similitude.py`, `LooseningCurveTransform.generate_prototype_prediction()`
**Reference**: Part IX, Section 37.3 — Time scales as λ√(ρ/E)

The cycle transformation uses `N_proto = N_model × λ` (geometric scale). But cycles are dimensionless counts, and the relationship between model and prototype cycles depends on the loading frequency ratio:
- Frequency scales as 1/λ (same material)
- Test duration scales as λ
- Therefore cycles = f × t, and the number of cycles should be preserved (N_proto = N_model) when the test is conducted at the scaled frequency for the scaled duration

Alternatively, if the model test runs for the same duration (not scaled), then `N_proto = N_model × λ` is correct. The code should make this assumption explicit and configurable.

**Impact**: Loosening prediction may be off by a factor of λ depending on interpretation.

**Fix**: Add `cycle_scaling_mode` parameter:
```python
class LooseningCurveTransform:
    SCALED_DURATION = "scaled"    # Same physical duration ratio → N_proto = N_model
    SAME_DURATION = "same"        # Same absolute test time → N_proto = N_model × λ
    SAME_CYCLES = "cycles"        # Same number of cycles → N_proto = N_model
```

---

## HIGH — Significant Feature Gaps

### HS1. No Thermal Similitude Scaling
**Reference**: Part IX, Section 40.5 — "Thermal effects require separate scaling"
**Code**: `PrototypeData` has no thermal parameters; `ScaleFactors` has no thermal factors

The reference explicitly notes that thermal time constants scale differently from mechanical time:
- Thermal diffusivity: α = k/(ρ·c_p)
- Thermal time constant: τ_th ∝ L²/α (scales as λ²)
- Mechanical time constant: τ_mech ∝ λ√(ρ/E) (scales as λ)

For thermal cycling tests or joints operating at elevated temperature, this mismatch means the model reaches thermal equilibrium faster (relative to mechanical loading) than the prototype.

**Impact**: For thermal-mechanical coupling analysis (Petrobras subsea applications with temperature transients), thermal similitude is critical.

**Implementation**:
```python
@dataclass
class ThermalScaleFactors:
    thermal_conductivity_ratio: float = 1.0  # k_m/k_p
    specific_heat_ratio: float = 1.0         # cp_m/cp_p

    @property
    def thermal_diffusivity_ratio(self) -> float:
        return self.thermal_conductivity_ratio / (self.density_ratio * self.specific_heat_ratio)

    @property
    def thermal_time_constant(self) -> float:
        """Fourier number scaling: τ_th = L²/α"""
        return self.geometric**2 / self.thermal_diffusivity_ratio

    @property
    def biot_number_ratio(self) -> float:
        """Biot number preservation check"""
        return self.geometric / self.thermal_conductivity_ratio
```

---

### HS2. No Fatigue Size Effect Correction
**Reference**: Part IX, Section 39 mentions Kuguel (1961) but doesn't implement fatigue scaling
**Literature**: Kuguel, R. (1961), ASTM Proceedings

The current scale effect analysis covers surface roughness, friction, embedding, thread tolerance, and stress concentration. It does not address the **statistical size effect** on fatigue life, which is relevant when bolt loosening interacts with fatigue crack initiation.

**Size effect on fatigue**:
- Highly stressed volume (HSV) effect: larger bolts have more material at peak stress
- Surface area effect: more surface defects in larger components
- Stress gradient effect: shallower gradients in larger thread roots

**Correction factor (Kuguel)**:
```python
def fatigue_size_correction(d_proto, d_model):
    """Kuguel size effect for fatigue life at thread root."""
    # Volume ratio of highly stressed zone
    V_ratio = (d_model / d_proto)**3
    # Kuguel exponent (0.05-0.10 for steel)
    n_kuguel = 0.07
    C_fatigue = V_ratio**(-n_kuguel)
    return C_fatigue  # > 1.0 means model is stronger
```

---

### HS3. No Lubrication Regime Assessment
**Reference**: Part IX, Section 40.5 — "Lubrication regime may change"
**Code**: No lubrication regime check exists

The similitude framework assumes friction behavior is qualitatively the same in model and prototype. However, if the model operates in a different lubrication regime (e.g., boundary vs. mixed), friction behavior changes fundamentally:

**Hersey number criterion**: H = η·v/(p) where η = viscosity, v = sliding velocity, p = contact pressure
- Same material: v is preserved, but p = F/A scales as σ (preserved for same material), so H is preserved
- Different material or different lubricant: H changes

**Implementation**:
```python
def assess_lubrication_regime(proto, model, lubricant_viscosity):
    """Check Hersey number preservation between prototype and model."""
    # Sliding velocity at thread (helix unwinding speed)
    v_proto = proto.frequency * proto.thread_pitch * 1e-3  # m/s
    v_model = model.frequency * model.thread_pitch * 1e-3

    # Contact pressure (preload / bearing area)
    A_proto = np.pi / 4 * (proto.washer_outer_diameter**2 - proto.bolt_diameter**2) * 1e-6
    A_model = np.pi / 4 * (model.washer_outer_diameter**2 - model.bolt_diameter**2) * 1e-6
    p_proto = proto.preload_force / A_proto
    p_model = model.preload_force / A_model

    H_proto = lubricant_viscosity * v_proto / p_proto
    H_model = lubricant_viscosity * v_model / p_model

    regime_proto = classify_regime(H_proto)  # boundary, mixed, hydrodynamic
    regime_model = classify_regime(H_model)

    return regime_proto == regime_model, H_proto, H_model
```

---

### HS4. No Multi-Scale Validation Framework
**Reference**: Part IX, Section 40.3 — "Tests at two or more scale factors are recommended"
**Code**: Multi-scale comparison exists in plots but not in analysis

The reference recommends testing at multiple scales (e.g., 1:2 and 1:4) to verify scaling law validity. The current code generates multi-scale comparison plots (`plot_multi_scale_comparison()`) but doesn't provide:
- Statistical confidence analysis across scales
- Trend verification (do results scale consistently?)
- Outlier detection for specific scale effects
- Recommended next-best scale if current scale fails quality check

**Implementation**:
```python
class MultiScaleValidation:
    def __init__(self, prototype, scales=[0.5, 0.333, 0.25]):
        self.analyses = [SimilitudeAnalysis(prototype, s) for s in scales]

    def verify_scaling_trend(self, measured_data):
        """Check if measured data follows predicted scaling law."""
        # Fit power law: Q_model = a × λ^b
        # Compare fitted exponent b with theoretical exponent
        pass

    def optimal_scale_recommendation(self, max_correction=1.15, min_diameter=8):
        """Find largest scale with combined correction < threshold."""
        for analysis in sorted(self.analyses, key=lambda a: a.scale_factor, reverse=True):
            if (analysis.combined_correction <= max_correction and
                analysis.model_diameter >= min_diameter):
                return analysis
        return None

    def confidence_interval(self, n_replicates=3, cov=0.10):
        """Statistical confidence bound on prototype prediction."""
        pass
```

---

### HS5. Scale Effect Corrections Are Purely Empirical
**File**: `similitude.py`, `ScaleEffect` factory methods
**Reference**: Part IX, Sections 39.2–39.5

All correction factors use fixed empirical coefficients:
- Roughness: `C = 1 + 0.10 × (Rz/d ratio deviation)`
- Friction: `C = 1 + 0.08 × (1 - λ)`
- Embedding: `C = 1 + 0.05 × (1/λ - 1)`
- Thread: `C = 1 + 0.02 × (1/λ - 1)`

These coefficients are not derived from first principles and have no published experimental validation. The sensitivity of the combined correction to these coefficients should be assessed.

**Improvement**: Add uncertainty quantification:
```python
@dataclass
class ScaleEffectWithUncertainty:
    correction_factor: float
    uncertainty_range: Tuple[float, float]  # (lower, upper) 95% confidence
    coefficient_source: str  # "VDI 2230", "empirical", "literature"
    validation_status: str   # "validated", "assumed", "calibrated"

    @property
    def correction_range(self):
        """Return (C_low, C_nominal, C_high)"""
        return (self.correction_factor * self.uncertainty_range[0],
                self.correction_factor,
                self.correction_factor * self.uncertainty_range[1])
```

---

### HS6. No Distorted Similitude Support
**Literature**: Liu et al. (2025), Structural Health Monitoring; Li et al. (2022), Sagepub

Classical similitude requires all dimensions to scale uniformly by λ. **Distorted similitude** allows certain dimensions to scale differently (e.g., bolt diameter scales by λ₁ but grip length scales by λ₂). This is necessary when:
- Standard bolt sizes don't match the ideal scaled diameter
- Flange thickness is constrained by available plate stock
- Thread pitch ratio deviates from ideal scaling

Recent research proposes improved least-square similitude methods based on Lagrange energy for estimating scaling laws and eliminating coupling effects in distorted models.

**Implementation**:
```python
@dataclass
class DistortedScaleFactors:
    """Scale factors for distorted (non-uniform) geometric similitude."""
    lambda_diameter: float      # Bolt diameter scaling
    lambda_length: float        # Grip length scaling
    lambda_thickness: float     # Flange thickness scaling
    lambda_pitch: float         # Thread pitch scaling (may differ from λ_d)

    @property
    def is_undistorted(self) -> bool:
        """Check if all geometric scales are equal (classical similitude)."""
        scales = [self.lambda_diameter, self.lambda_length,
                  self.lambda_thickness, self.lambda_pitch]
        return max(scales) - min(scales) < 0.01

    def compute_distortion_penalty(self) -> float:
        """Quantify deviation from ideal (undistorted) similitude."""
        lambda_ref = self.lambda_diameter
        penalties = [
            abs(self.lambda_length - lambda_ref) / lambda_ref,
            abs(self.lambda_thickness - lambda_ref) / lambda_ref,
            abs(self.lambda_pitch - lambda_ref) / lambda_ref,
        ]
        return sum(penalties) / len(penalties)

    def energy_based_correction(self, mass_matrix, stiffness_matrix):
        """Lagrange energy method for distorted similitude correction.
        Per Li et al. (2022), minimizes energy error between distorted
        model and ideal scaled model."""
        pass
```

---

### HS7. Loosening-Specific Π-Groups Not Cross-Referenced with Classical Π-Groups
**Files**: `similitude.py` defines 12 Π-groups; `loosening_similitude.py` defines 8 different Π-groups
**Reference**: Part IX defines 12 groups; loosening extension adds specialized groups

The two modules define overlapping but inconsistent sets of dimensionless groups:
- `similitude.py`: Π₁ = L/d, Π₂ = t/d, Π₃ = F_p/(σ_y·A_t), ..., Π₁₂ = d_w/d
- `loosening_similitude.py`: Π₁ = F_t/(μ_b·F_p), Π₂ = tan(λ)/(μ_t·sec(α)), ...

There is no cross-reference or consistency check between them. A user running both analyses sees different Π numbering for the same physical system.

**Fix**: Unify into a single Pi-group registry:
```python
class PiGroupRegistry:
    """Central registry of all dimensionless groups."""
    CLASSICAL = [...]    # Part IX groups Π₁-Π₁₂
    LOOSENING = [...]     # Loosening-specific groups
    ALL = CLASSICAL + LOOSENING  # Complete set

    def get_required_groups(self, analysis_type):
        if analysis_type == "similitude":
            return self.CLASSICAL
        elif analysis_type == "loosening_similitude":
            return self.CLASSICAL + self.LOOSENING
```

---

## MEDIUM — Methodology Improvements

### MS1. Loading Pattern Ignored in Multi-Bolt Reduction
**File**: `loosening_similitude.py`, `reduce_multi_bolt_to_single()`
**Reference**: Part IX, Section 40 — practical application for flanged joints

`LoadingPattern` enum (UNIFORM, MOMENT, COMBINED, SHEAR) exists but the reduction function always applies uniform distribution. For Petrobras flange applications:

- **Moment loading** (wind, wave, riser tension): Most-loaded bolt sees ~1.5–2.0× average load
- **Shear loading** (pipe weight, thermal expansion): Cosine distribution around bolt circle
- **Combined**: Superposition with different phase angles

**Fix**: Implement proper load distribution per pattern:
```python
def bolt_load_factor(pattern, n_bolts, bolt_index):
    """Load factor for bolt at angular position index (0-based)."""
    theta = 2 * np.pi * bolt_index / n_bolts
    if pattern == LoadingPattern.UNIFORM:
        return 1.0
    elif pattern == LoadingPattern.MOMENT:
        return 1.0 + np.cos(theta)  # max = 2.0 at θ=0
    elif pattern == LoadingPattern.SHEAR:
        return 1.0 + 0.5 * np.cos(theta)
    elif pattern == LoadingPattern.COMBINED:
        return 1.0 + np.cos(theta) + 0.3 * np.cos(2*theta)
```

---

### MS2. No Thread Pitch Mismatch Assessment
**File**: `loosening_similitude.py`, `create_scaled_loosening_model()`

When the ideal scaled pitch doesn't match a standard ISO metric pitch, the code selects the nearest standard size and generates a warning if diameter mismatch exceeds 15% or pitch ratio error exceeds 10%. However, it doesn't assess the **mechanical impact** of the pitch mismatch.

**Thread pitch affects**:
- Helix angle λ = arctan(p/(π·d₂)) — critical for loosening
- Self-locking condition: tan(λ) < μ_t × sec(α)
- Per-thread stiffness: k_t = E·A_t/p
- Thread engagement length requirements

**Improvement**: Add pitch mismatch impact assessment:
```python
def assess_pitch_mismatch(proto_pitch, proto_d, model_pitch, model_d):
    """Assess impact of pitch ratio deviation on loosening behavior."""
    lambda_proto = np.arctan(proto_pitch / (np.pi * (proto_d - 0.6495*proto_pitch)))
    lambda_model = np.arctan(model_pitch / (np.pi * (model_d - 0.6495*model_pitch)))

    # Helix angle deviation directly affects loosening torque
    helix_deviation = abs(lambda_model - lambda_proto) / lambda_proto * 100

    # Self-locking margin change
    mu_thread = 0.12  # typical
    alpha = 30 * np.pi / 180  # flank half-angle
    margin_proto = mu_thread / np.cos(alpha) - np.tan(lambda_proto)
    margin_model = mu_thread / np.cos(alpha) - np.tan(lambda_model)

    return {
        'helix_angle_deviation_pct': helix_deviation,
        'self_locking_margin_proto': margin_proto,
        'self_locking_margin_model': margin_model,
        'loosening_sensitivity': 'HIGH' if helix_deviation > 5 else 'LOW',
    }
```

---

### MS3. No Uncertainty Propagation in Prototype Predictions
**Reference**: Part IX, Section 40.4 — "Report corrected prediction with an uncertainty bound"

The current implementation computes a single-point prototype prediction without any uncertainty quantification. The reference explicitly requires uncertainty bounds.

**Sources of uncertainty**:
1. Scale effect correction factors (±10–20% per factor)
2. Friction measurement scatter (±15–20%)
3. Preload control accuracy (±5–10% with torque method)
4. Material property variation (±3–5%)
5. Geometric tolerance effects

**Implementation**: Monte Carlo uncertainty propagation:
```python
def prototype_prediction_with_uncertainty(model_measurement, scale_factors,
                                          corrections, n_samples=10000):
    """Monte Carlo uncertainty propagation for prototype prediction."""
    # Sample each correction factor from its uncertainty distribution
    C_roughness = np.random.normal(corrections.roughness, 0.03, n_samples)
    C_friction = np.random.normal(corrections.friction, 0.02, n_samples)
    C_embedding = np.random.normal(corrections.embedding, 0.05, n_samples)

    C_combined = C_roughness * C_friction * C_embedding

    # Raw scaling
    Q_proto_raw = model_measurement / scale_factors.force

    # Corrected predictions (distribution)
    Q_proto = Q_proto_raw * C_combined

    return {
        'mean': np.mean(Q_proto),
        'std': np.std(Q_proto),
        'ci_95': (np.percentile(Q_proto, 2.5), np.percentile(Q_proto, 97.5)),
        'ci_99': (np.percentile(Q_proto, 0.5), np.percentile(Q_proto, 99.5)),
    }
```

---

### MS4. Equivalent Single Bolt Diameter Formula Lacks Physical Basis
**File**: `loosening_similitude.py`, `reduce_multi_bolt_to_single()`

The equivalent diameter `d_eq = d × √n` comes from area equivalence (same total tensile stress area). However, this doesn't preserve:
- Bending stiffness (which scales as d⁴, not d²)
- Torsional stiffness of the bolt
- Thread engagement behavior
- Bearing pressure distribution

For multi-bolt to single-bolt reduction, the equivalent model should preserve the loosening-relevant parameters, not just area.

**Improvement**: Add multiple equivalence modes:
```python
class EquivalenceMode(Enum):
    AREA = "area"            # d_eq = d × √n (current)
    STIFFNESS = "stiffness"  # Preserves k_bolt = n × k_single
    PRELOAD = "preload"      # Preserves total preload and stiffness ratio
    LOOSENING = "loosening"  # Preserves loosening Π-groups
```

---

### MS5. No Standard Bolt Size Database for Non-Metric Systems
**File**: `similitude.py`, `find_standard_bolt_size()`

The function includes metric (M4–M64) and UNC (1/4"–2-1/2") sizes. Missing:
- UNF (fine thread) sizes — important for vibration-critical applications
- BSP/BSW sizes — used in some Petrobras legacy equipment
- ASTM A193 custom sizes (e.g., 7/8"-9 UNC, 1-1/8"-7 UNC common in pressure vessels)

---

### MS6. No Dynamic Similitude Verification
**Reference**: Part IX, Section 36.3 — Dynamic similitude requires force ratio matching

The analysis checks geometric Π-groups but doesn't verify dynamic similitude by comparing:
- Inertial force ratio: ρ·L²·f²·δ
- Elastic force ratio: E·L·ε
- Friction force ratio: μ·F_p
- Damping force ratio: c·v

For loosening analysis, the balance between inertial forces (which drive transverse slip) and friction forces (which resist loosening) must be preserved.

**Implementation**: Add force ratio checks:
```python
def check_dynamic_similitude(proto, model, scales):
    """Verify dynamic force ratios are preserved."""
    # Inertial / Elastic ratio (should be preserved)
    IE_proto = proto.density * proto.frequency**2 * proto.grip_length / proto.bolt_elastic_modulus
    IE_model = model.density * model.frequency**2 * model.grip_length / model.bolt_elastic_modulus
    IE_deviation = abs(IE_model - IE_proto) / IE_proto * 100

    # Friction / Inertial ratio (governs loosening onset)
    FI_proto = proto.thread_friction * proto.preload / (proto.density * (proto.bolt_diameter/1000)**3 * proto.frequency**2)
    FI_model = model.thread_friction * model.preload / (model.density * (model.bolt_diameter/1000)**3 * model.frequency**2)
    FI_deviation = abs(FI_model - FI_proto) / FI_proto * 100

    return {
        'inertial_elastic_deviation': IE_deviation,
        'friction_inertial_deviation': FI_deviation,
        'dynamic_similitude_quality': 'Good' if max(IE_deviation, FI_deviation) < 5 else 'Marginal',
    }
```

---

### MS7. Loosening Comparison Plots Lack Experimental Data Import
**File**: `similitude_tab.py`, `ComparisonPlotsPanel`

The comparison panel generates synthetic loosening curves using the Jiang two-stage model. There is no way to import actual experimental data (from model tests) to:
- Compare measured vs. predicted model behavior
- Validate scaling law accuracy
- Calibrate correction factors against real data

**Implementation**: Add CSV import for experimental data:
```python
def import_experimental_data(self, filepath):
    """Import Junker test data: columns = [Cycle, Preload_N, Rotation_deg]"""
    data = np.loadtxt(filepath, delimiter=',', skiprows=1)
    cycles = data[:, 0]
    preload = data[:, 1]
    self.plot_experimental_overlay(cycles, preload)
```

---

### MS8. No Sensitivity Analysis for Scale Factor Selection
**Reference**: Part IX, Section 40.2 — recommends λ_min = 0.25

The minimum scale factor recommendation (λ = 0.25) is fixed. A sensitivity analysis showing how key outputs (correction factor, Pi-group match quality, cost estimate) vary with scale factor would help engineers select the optimal model size.

**Implementation**:
```python
def scale_factor_sensitivity(prototype, lambda_range=np.linspace(0.1, 1.0, 20)):
    """Compute sensitivity of analysis quality metrics to scale factor."""
    results = []
    for lam in lambda_range:
        analysis = SimilitudeAnalysis(prototype, lam)
        results.append({
            'lambda': lam,
            'combined_correction': analysis.combined_correction,
            'pi_groups_matched': sum(1 for pg in analysis.pi_groups if pg.is_matched),
            'quality': analysis.get_similitude_quality(),
            'model_diameter': prototype.bolt_diameter * lam,
            'model_preload': prototype.preload_force * lam**2,
        })
    return results
```

---

## LOW — GUI and Visualization Improvements

### LS1. Similitude Tab Has No Interactive Parameter Exploration
**File**: `similitude_tab.py`

The scaling panel requires clicking "Compute" after every parameter change. Real-time parameter exploration (sliders, live preview) would significantly improve the workflow.

**Implementation**: Connect parameter spinbox `valueChanged` signals to auto-recompute with debouncing (500ms delay).

---

### LS2. No Export to LaTeX/PDF for Academic Reports
**File**: `similitude_tab.py`, `_export_report()`

The export function generates Markdown only. For Petrobras R&D deliverables and academic publications, direct PDF or LaTeX export would be valuable.

---

### LS3. Comparison Plots Don't Show Correction Effect
**File**: `similitude_tab.py`, `ComparisonPlotsPanel`

When "Apply Corrections" is checked, the corrected curve replaces the raw curve. It should show both curves simultaneously to visualize the correction magnitude.

---

### LS4. No Bolt Size Selection Helper
**File**: `similitude_tab.py`, `GeometricScalingPanel`

After computing the scaled model, the user sees the ideal diameter and nearest standard size. There is no interactive helper that:
- Shows multiple standard bolt options near the ideal size
- Compares Pi-group deviations for each option
- Recommends coarse vs. fine thread based on pitch ratio preservation
- Displays thread geometry comparison table

---

### LS5. No Report of Individual Scale Effect Contributions
**File**: `similitude_tab.py`, corrections sub-tab

The corrections tab shows total friction and embedding corrections but not the individual scale effect contributions (roughness, thread tolerance, stress concentration). The full breakdown from `SimilitudeAnalysis.scale_effects` should be displayed.

---

### LS6. Error Analysis Panel Uses Fixed Parameters
**File**: `similitude_tab.py`, `ErrorAnalysisPanel`

The 8 error parameters are computed from fixed reference values rather than actual user input. The panel should use the computed prototype and model values from the scaling analysis.

---

### LS7. No Similitude Results in Report Tab
**File**: `gui/main_window.py`, Reports Tab integration

The similitude analysis results are not included in the main Reports tab (Tab 6) output. The "Similitude" report type exists in the menu but generates a placeholder.

**Fix**: Pass `SimilitudeAnalysis` results to report generator, including:
- Scale factor and quality assessment
- Pi-group comparison table
- Scale effect corrections table
- Prototype prediction with uncertainty bounds

---

### LS8. Multi-Bolt Panel Does Not Read From MSD Model
**File**: `similitude_tab.py`, `MultiBoltReductionPanel`

The multi-bolt configuration must be entered manually. It should be able to read bolt count, diameter, preload, and stiffness from the current MSD model.

**Implementation**: Add "Import from Model" button that reads `model.elements` and `model.global_loading`.

---

## Architecture Gap: Reference vs Implementation

### Part IX Requirements vs Current Code

| Feature | Reference | Code Status | Notes |
|---|---|---|---|
| Buckingham Π theorem | 12 groups | 12 implemented | ✅ Complete |
| Geometric similitude | All lengths scale by λ | ✅ Correct | |
| Kinematic similitude | Velocity field similar | ⚠ Implicit | Not explicitly verified |
| Dynamic similitude | Force ratios match | ❌ Missing | MS6 |
| Complete similitude | Friction + wear + surface | ⚠ Partial | Friction correction only |
| Same material scaling | E_m/E_p = 1 | ✅ Works | Default mode |
| Similar material scaling | E/ρ preserved | ❌ Not implemented | CS2 |
| Different material scaling | General E, ρ ratios | ❌ Not implemented | CS2 |
| Surface roughness correction | C = 1 + 0.10×(Rz/d dev) | ✅ Implemented | Empirical coefficient |
| Friction correction | C = 1 + 0.08×(1-λ) | ✅ Implemented | Empirical coefficient |
| Embedding correction | C = 1 + 0.05×(1/λ - 1) | ✅ Implemented | Empirical coefficient |
| Thread tolerance correction | C = 1 + 0.02×(1/λ - 1) | ✅ Implemented | |
| Stress concentration | C = 1.0 | ✅ Correct | Preserved under geometric similitude |
| Combined correction | Product of individual C | ✅ Correct | |
| Uncertainty bounds on prediction | Required per 40.4 | ❌ Missing | MS3 |
| Multi-scale validation | Recommended per 40.3 | ⚠ Partial | Plots exist, no analysis |
| Thermal scaling | Separate treatment per 40.5 | ❌ Missing | HS1 |
| Standard bolt size lookup | Metric + UNC | ✅ Implemented | Missing UNF, BSP |
| Worked example (M30→M10) | Complete in Section 41 | ✅ Reproducible | |

### Loosening Similitude Extensions

| Feature | Reference | Code Status | Notes |
|---|---|---|---|
| Multi-bolt to single-bolt | Area equivalence | ✅ Implemented | MS4: lacks stiffness mode |
| Loading pattern effects | 4 patterns defined | ❌ Not used | MS1 |
| Loosening Π-groups | 8 groups | ✅ Implemented | HS7: separate from classical |
| Jiang two-stage model | Parameters from fit | ✅ Implemented | λ₁, λ₂, N_trans |
| Cycle scaling | N_proto = f(N_model) | ⚠ Ambiguous | CS3 |
| Embedding scaling correction | Applied in prediction | ✅ Implemented | |
| Transfer to MSD Builder | Element dict creation | ✅ Implemented | |

---

## New Improvements Based on Literature Review

### NI1. Cross-Domain Bolt Looseness Detection via Distorted Similitude
**Reference**: Liu et al. (2025), Structural Health Monitoring, "Cross-domain bolt looseness detection of cylindrical shell structures based on a distorted similitude model"

This recent work introduces an improved least-square similitude method based on Lagrange energy for cylindrical shell structures with bolted joints. Key innovations:
- Establishes scaling laws that handle non-uniform geometric scaling
- Eliminates coupling effects between different scaling factors
- Enables cross-domain prediction from one geometry to another
- Applicable to cylindrical shell flanges (common in Petrobras applications)

**Implementation**: Add distorted similitude option that relaxes the uniform λ requirement and computes optimal scaling using energy-based methods.

---

### NI2. Bolted Joint Rotor Similitude Framework
**Reference**: Li et al. (2022), Proc. IMechE Part C, "Structural similitude for a scaled rotor system considering stiffness characteristics of bolted joints"

For rotating equipment bolted connections (pumps, compressors, turbines), this framework:
- Develops scaling relationships specific to bolted rotor systems
- Considers piecewise linear stiffness nonlinearity at bolted interfaces
- Handles different materials between prototype and model
- Derives frequency response scaling for non-proportional damping

**Relevance to BAS**: Extends similitude capability to rotating machinery joints, broadening the application scope beyond static flanged connections.

---

### NI3. Machine Learning-Assisted Parameter Prediction
**Reference**: ArXiv 2412.08286 (2024), "Towards Precision in Bolted Joint Design: A Preliminary Machine Learning-Based Parameter Prediction"

Recent work applies ML to predict bolted joint parameters, which could enhance similitude analysis:
- Train on database of prototype-model test pairs
- Predict correction factors from joint parameters
- Quantify prediction confidence intervals
- Adaptively weight correction factors based on historical accuracy

---

### NI4. Finite Similitude Theory for Dynamic Buckling
**Reference**: MDPI Journal of Marine Science (2025), "Scaling the Dynamic Buckling Behavior of a Box Girder Based on the Finite Similitude Approach"

The finite similitude approach deduces similarity scaling criteria applicable to both static and dynamic responses. This newer methodology:
- Goes beyond classical Buckingham Π to handle nonlinear regimes
- Accounts for material nonlinearity under dynamic loading
- Addresses limitations of conventional dimensional analysis for ultimate strength

**Relevance**: Could improve BAS similitude predictions for joints approaching yield or experiencing plastic deformation at thread roots.

---

## Prioritized Improvement Roadmap

| Priority | ID | Description | Effort | Impact |
|---|---|---|---|---|
| **1** | CS1 | Fix hardcoded Pi5 joint constant | LOW | Correct Pi-group assessment |
| **2** | CS2 | Implement material dissimilarity scaling | MEDIUM | Enable mixed-material joints |
| **3** | CS3 | Fix/clarify cycle scaling in loosening curves | LOW | Correct prototype prediction |
| **4** | HS7 | Unify classical and loosening Π-group registries | MEDIUM | Consistent analysis framework |
| **5** | MS1 | Implement loading pattern effects in multi-bolt | MEDIUM | Realistic flange analysis |
| **6** | MS3 | Add uncertainty propagation | MEDIUM | Required per reference doc |
| **7** | HS2 | Add fatigue size effect correction | LOW | More complete scale effects |
| **8** | MS2 | Add thread pitch mismatch impact assessment | LOW | Better standard bolt selection |
| **9** | HS1 | Add thermal similitude scaling | HIGH | Thermal-mechanical coupling |
| **10** | MS6 | Implement dynamic similitude verification | MEDIUM | Complete similitude check |
| **11** | HS4 | Add multi-scale validation framework | HIGH | Experimental validation support |
| **12** | HS6 | Add distorted similitude support | HIGH | Non-uniform scaling capability |
| **13** | MS8 | Add scale factor sensitivity analysis | LOW | Better scale selection |
| **14** | HS3 | Add lubrication regime assessment | MEDIUM | Friction regime verification |
| **15** | MS7 | Add experimental data import | MEDIUM | Data-driven validation |
| **16** | LS4 | Add bolt size selection helper | LOW | Better UX |
| **17** | LS7 | Integrate results into Reports tab | MEDIUM | Report completeness |
| **18** | LS8 | Read multi-bolt config from MSD model | LOW | Workflow integration |
| **19** | HS5 | Add uncertainty to scale effect coefficients | MEDIUM | Rigorous assessment |
| **20** | NI1 | Distorted similitude (Lagrange energy method) | HIGH | Advanced scaling capability |

---

## References

1. Buckingham, E. (1914). "On Physically Similar Systems; Illustrations of the Use of Dimensional Equations." *Physical Review*, 4(4), 345–376.
2. VDI 2230 Part 1 (2015). *Systematic Calculation of Highly Stressed Bolted Joints — Joints with One Cylindrical Bolt*.
3. Kuguel, R. (1961). "A Relation Between Theoretical Stress Concentration Factor and Fatigue Notch Factor Deduced from the Concept of Highly Stressed Volume." *Proceedings ASTM*, 61, 732–748.
4. Barenblatt, G.I. (2003). *Scaling*. Cambridge Texts in Applied Mathematics. Cambridge University Press.
5. Liu, P., Wang, X., and Wang, Y. (2025). "Cross-domain bolt looseness detection of cylindrical shell structures based on a distorted similitude model." *Structural Health Monitoring*.
6. Li, L., Luo, Z., et al. (2022). "Structural similitude for a scaled rotor system considering stiffness characteristics of bolted joints." *Proc. IMechE Part C: J. Mechanical Engineering Science*.
7. MDPI (2025). "Scaling the Dynamic Buckling Behavior of a Box Girder Based on the Finite Similitude Approach." *J. Marine Science and Engineering*, 13(8), 1496.
8. Szirtes, T. (2007). *Applied Dimensional Analysis and Modeling*, 2nd ed. Elsevier/Butterworth-Heinemann.
9. Nassar, S.A. and Housari, B.A. (2007). "Study of the Effect of Hole Clearance and Thread Fit on the Self-Loosening of Threaded Fasteners." *ASME J. Mechanical Design*, 129(6), 586–594.
10. Jiang, Y., Zhang, M., and Lee, C.-H. (2003). "A Study of Early Stage Self-Loosening of Bolted Joints." *ASME J. Mechanical Design*, 125(3), 518–526.
11. Hintikka, J., Lehtovaara, A., and Mantyla, A. (2020). "Running-in in Fretting, Transition from Near-Stable Friction Regime to Gross Sliding." *Tribology International*, 143, 106073.
12. ArXiv 2412.08286 (2024). "Towards Precision in Bolted Joint Design: A Preliminary Machine Learning-Based Parameter Prediction."
13. ASME (2019). "A Review of Similitude Methods for Structural Engineering." *Applied Mechanics Reviews*, 71(3), 030802.
