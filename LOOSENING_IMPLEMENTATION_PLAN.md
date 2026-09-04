# Loosening Analysis — Master Implementation Plan

**Bolt Analysis Studio v4.0**
internal reference — Petrobras R&D
February 2026

---

## Document Set

| Document | Role | Key Content |
|----------|------|-------------|
| `LOOSENING_MECHANISMS_QUANTITATIVE.md` | **Theory A** — Mechanism reference | §1–10: original mechanisms; §11 fretting map; §12 five-stage model; §13 locking devices |
| `LOOSENING_LOADING_CONDITIONS.md` | **Theory B** — Loading conditions | Axial, shear, bending, impact, combined; severity ranking; 14-criterion transition table |
| `LOAD_FACTORS_DESIGN.md` | **Design** — VDI 2230 load factors | R, Φ, n, φ, waveform; GUI widgets; code snippets for 6 files |
| **`LOOSENING_IMPLEMENTATION_PLAN.md`** (this) | **Plan** — Master roadmap | Phased tasks; theory→code mapping; priority matrix; test plan |

---

## 1. Theory → Code Mapping

The table below links every quantitative finding in the theory documents to the BAS source
file and class/method that should implement it.

| Theory Finding | Source Ref | BAS File | Class / Method | Phase |
|----------------|-----------|----------|----------------|-------|
| Five-stage taxonomy (STABLE…RUNAWAY) | LMQ §12.1 | `solver_worker.py` | `LooseningPhase` enum | B |
| Quantitative stage boundaries (F_p/F_p0) | LMQ §12.1 | `solver_worker.py` | `_classify_phase()` | B |
| 0.5° rotation NON-ROT→ROT boundary | LMQ §12.1 | `solver_worker.py` | `_classify_phase()` | B |
| Pai-Hess slip onset 46–66% | LMQ §12.1 | `coupled_loosening_analyzer.py` | `_simulate_cycle()` | C |
| Double-exponential Stage 1 decay | LMQ §12.2 | `coupled_loosening_analyzer.py` | `_stage1_decay()` | B |
| Miner's rule D-N loosening life | LMQ §12.3 | `coupled_loosening_analyzer.py` | `predict_loosening_life()` | E |
| Vingsbo-Söderberg fretting map | LMQ §11.1 | `contacts/thread.py` | `_fretting_regime()` | D |
| Mindlin partial-slip stick zone | LMQ §11.2 | `contacts/base.py` | `compute_slip_index()` | D |
| Fretting µ degradation 20-40% | LMQ §11.3 | `coupled_loosening_analyzer.py` | `_update_friction_wear()` | D |
| Self-locking condition (tan λ < µ cos α) | LMQ §11.4 | `coupled_loosening_analyzer.py` | `_check_self_lock()` | D |
| Archard wear preload loss rate | LMQ §11.5 | `numerical/wear_models.py` | `ArchwoodWear` | D |
| Locking device retention table | LMQ §13.1 | `core/databases/locking_devices.json` | (new data file) | F |
| ISO 2320 prevailing torque values | LMQ §13.2 | `core/databases/locking_devices.json` | (new data file) | F |
| Load ratio R = F_min/F_max | LFD §2.1 | `core/models/element.py` | `LoadingData.R_factor` | A |
| VDI 2230 load factor Φ | LFD §2.2 | `core/models/element.py` | `LoadingData.Phi_load` | A |
| Force application factor n | LFD §2.3 | `core/models/element.py` | `LoadingData.n_load_plane` | A |
| Dynamic amplification φ | LFD §2.4 | `core/models/element.py` | `LoadingData.dynamic_factor` | A |
| Load waveform (square, triangular…) | LFD §2.5 | `numerical/time_integration.py` | `biased_harmonic_force()` | A |
| F_K_min → separation check | LFD §3 | `gui/msd_builder.py` | `_refresh_load_factor_labels()` | A |
| Φ_eff in contact normal force | LFD §4.2 | `core/models/model.py` | `assemble_force_vector()` | A |
| Axial loading → no rotation | LLC §1.1 | `coupled_loosening_analyzer.py` | `_simulate_cycle()` | C |
| Axial+transverse interaction check | LLC §5.1 | `coupled_loosening_analyzer.py` | `_check_combined_slip()` | C |
| Bearing-type vs friction-type shear | LLC §2.1-2.2 | `core/models/model.py` | `ShearJointType` enum | E |
| Bending prying slip threshold reduction | LLC §3.1 | `coupled_loosening_analyzer.py` | `_prying_correction()` | E |
| Impact single-event embedding | LLC §4.1 | `numerical/preload_loss_models.py` | `impact_embedding_loss()` | E |
| Impact stage I1-I4 progression | LLC §4.4 | `solver_worker.py` | `_classify_impact_phase()` | E |

**Abbreviations:** LMQ = LOOSENING_MECHANISMS_QUANTITATIVE.md, LLC = LOOSENING_LOADING_CONDITIONS.md, LFD = LOAD_FACTORS_DESIGN.md

---

## 2. Current State Assessment

### Already Implemented (no changes needed)
- `LooseningPhase` enum: STABLE, NON_ROTATIONAL, TRANSITION, ROTATIONAL, RUNAWAY values exist
- `CoupledLooseningResult.states`: List[LooseningState] linked to solver (fixed in session 2026-02-23)
- Stage Analysis animation with phase coloring (main_window.py)
- Friction evolution model selector (Three-Phase, Exponential Decay, Stribeck, LuGre, Constant)
- `_make_friction_params()` helper in coupled_loosening_analyzer.py
- Archard wear volume formula in `numerical/preload_loss_models.py`
- Contact µ seeded from `mu_initial_spin` (ContactPropertiesDialog, FlangeJointWizard)
- Convergence early-exit: steady-state (<0.1%/200 cycles) + full loosening (<2% F₀)
- `_preflight_check()` in solver_worker.py (resonance, yield, dt/period, µ range)

### Partially Implemented (needs update)
- `LoadingData` dataclass: has `F_amplitude`, `F_preload` but missing R, Φ, n, φ, waveform fields
- Slip threshold in `_simulate_cycle()`: uses classical µ×F_p (Pai-Hess correction not applied)
- Contact normal force in `assemble_force_vector()`: constant preload (time-varying Φ_eff not applied)
- Stage transitions: phases assigned per-cycle but boundaries not checked against quantitative thresholds
- Fretting wear: Archard formula exists but µ degradation over cycles not fed back to friction model

### Not Yet Implemented
- Five-stage quantitative boundaries with 0.5° rotation criterion
- Double-exponential Stage 1 decay model
- Pai-Hess 46–66% corrected slip onset
- VDI 2230 load factors in GUI (R, Φ, n, φ, waveform widgets)
- Self-locking condition check with µ degradation
- Axial-vs-transverse loading type enforcement (axial alone → no rotation flag)
- Bending prying correction on slip threshold
- Impact loading stage model (I1–I4)
- Locking device database and selection in UI
- Miner's rule D-N loosening life prediction

---

## 3. Phase A — VDI 2230 Load Factors (LOAD_FACTORS_DESIGN.md)

**Priority: High | Effort: Medium | Risk: Low**
**Design reference:** LOAD_FACTORS_DESIGN.md §5 (Steps 1–6)

### A.1 Data Model (`element.py`)

Add to `LoadingData` dataclass:
```python
R_factor: float = 0.0           # F_min/F_max; 0=pulsating, -1=fully reversed
Phi_load: Optional[float] = None  # VDI 2230 Φ; None = auto from [K]
n_load_plane: float = 0.5       # Force application factor
dynamic_factor: float = 1.0     # Impact amplification φ
load_waveform: str = "sinusoidal"  # sinusoidal|square|triangular|sawtooth
```
Add derived properties: `R`, `F_mean`, `F_alt`.
Update `to_dict()` / `from_dict()`.

### A.2 Force Function (`time_integration.py`)

Add `biased_harmonic_force(F_mean, F_alt, frequency, waveform)` function.
Waveforms: sinusoidal, square (`np.sign(sin)`), triangular (`arcsin(sin)` scaled), sawtooth.

### A.3 Solver Integration (`solver_worker.py`)

Add R_factor, Phi_load, n_load_plane, dynamic_factor, load_waveform to:
- `TimeIntegrationConfig`
- `CoupledLooseningConfig`
Replace single-amplitude `F_func` construction with `biased_harmonic_force()`.

### A.4 Contact Normal Force (`model.py`)

In `assemble_force_vector()`, replace constant `contact.normal_force = preload` with:
```python
contact.normal_force = preload + phi_eff * F_ext_current  # for bolt-side contacts
contact.normal_force = preload - (1 - phi_eff) * F_ext_current  # for interface contacts
```
Set `model._phi_eff` and `model._load_dof` in `export_to_msd_model()`.

### A.5 Loosening Analyzer (`coupled_loosening_analyzer.py`)

Extract R, Φ, n, φ in `create_analyzer_from_msd_model()`.
Compute `Phi_eff = n × Phi`. Auto-compute Phi from k_bolt/k_member if not user-specified.
Update cycle loop to use `F_N_bolt(t)` and `F_K_min(t)`.
Add separation_factor into loosening rate.

### A.6 GUI (`msd_builder.py`)

Add to Loading > Global sub-tab:
- `R_factor_spin` (−1 to 0.99), `n_load_plane_spin` (0–1), `dynamic_factor_spin` (1–3)
- `phi_load_spin` (0=auto, else 0–1), `load_waveform_combo`
- Read-only derived labels: F_mean, F_alt, Φ_auto, F_K_min, separation status
- Separation warning: yellow at F_K_min/F_p0 ≤ 0.55; red at ≤ 0.20; error at ≤ 0

Update `get_loading_data()` / `set_loading_data()` and `_on_loading_param_changed()`.

**Files changed:** `element.py`, `time_integration.py`, `solver_worker.py`, `model.py`, `coupled_loosening_analyzer.py`, `msd_builder.py`

**Test:** `tests/test_load_factors.py` — verify R=0 vs R=−1 loosening rate difference; separation warning trigger; Φ auto-compute vs manual override.

---

## 4. Phase B — Five-Stage Loosening Phase Model

**Priority: High | Effort: Low | Risk: Low**
**Theory reference:** LMQ §12.1, §12.2

### B.1 Phase Classification (`solver_worker.py`)

Replace heuristic phase assignment with quantitative boundaries:
```python
def _classify_phase(preload_ratio: float, nut_rotation_deg: float) -> LooseningPhase:
    if preload_ratio > 0.90 and nut_rotation_deg < 0.1:
        return LooseningPhase.STABLE
    if preload_ratio > 0.75 and nut_rotation_deg < 0.5:
        return LooseningPhase.NON_ROTATIONAL
    if preload_ratio > 0.55 and nut_rotation_deg < 5.0:
        return LooseningPhase.TRANSITION
    if preload_ratio > 0.20:
        return LooseningPhase.ROTATIONAL
    return LooseningPhase.RUNAWAY
```

Boundary: **0.5° cumulative nut rotation** marks NON_ROTATIONAL → TRANSITION (Chen 2017).
Track `cumulative_rotation_deg` in `LooseningState`.

### B.2 Double-Exponential Stage 1 (`coupled_loosening_analyzer.py`)

Add Stage 1 overlay to the preload decay curve:
```python
def _stage1_decay(N: int, A1: float, N1: float, A2: float, N2: float) -> float:
    """Double-exponential preload loss for Stage 1 (N up to ~N2×5)."""
    return A1 * (1 - np.exp(-N / N1)) + A2 * (1 - np.exp(-N / N2))
```
Parameters from amplitude:
- `N1 = 10–50` cycles (thread settlement), `N2 = 200–1000` (fretting)
- `A1 + A2` = Stage 1 amplitude (set from embedding loss estimate)

### B.3 ISO 16130 Warning in Solver Log

After analysis completion, check: if `F_p_final / F_p0 < 0.80`, emit warning:
```
"ISO 16130 fail: final preload {ratio:.0%} < 80% retention threshold"
```

**Files changed:** `solver_worker.py`, `coupled_loosening_analyzer.py`

**Test:** `tests/test_stage_transitions.py` — verify all five phase transitions at boundary values; verify 0.5° rotation criterion; verify double-exponential parameters scale with amplitude.

---

## 5. Phase C — Corrected Slip Criterion (Pai & Hess)

**Priority: High | Effort: Low | Risk: Low**
**Theory reference:** LMQ §12.1, LFD §11.2

### C.1 Slip Onset Factor (`coupled_loosening_analyzer.py`)

Add `slip_onset_factor: float = 0.46` to `LooseningAnalysisParams`.

Replace in `_simulate_cycle()`:
```python
# Before (classical Junker — overestimates resistance):
slip_condition = F_trans > self.params.mu_bearing * F_K_min

# After (Pai & Hess corrected):
slip_condition = F_trans > (self.params.slip_onset_factor
                            * self.params.mu_bearing * F_K_min)
```

### C.2 Axial Loading Gate (`coupled_loosening_analyzer.py`)

When loading type is `AXIAL_TENSION` (no transverse component), set rotational loosening
rate to zero regardless of other parameters:
```python
if self.params.loading_type == 'AXIAL_TENSION':
    delta_theta = 0.0  # Axial loading cannot cause Junker loosening [LLC §1.1]
```

### C.3 Combined Slip Check (`coupled_loosening_analyzer.py`)

Add `_check_combined_slip()` for axial+transverse interaction [LLC §5.1]:
```python
def _check_combined_slip(F_trans, F_axial, F_K_min, F_sep, mu, slip_onset):
    """Returns True if combined loading causes slip."""
    ratio_trans = F_trans / (slip_onset * mu * F_K_min)
    ratio_axial = F_axial / F_sep if F_sep > 0 else 0.0
    return (ratio_trans + ratio_axial) >= 1.0
```

**Files changed:** `coupled_loosening_analyzer.py`

**Test:** `tests/test_slip_criterion.py` — verify slip onset at 46% vs classical; verify axial-only mode has zero nut rotation; verify combined interaction threshold.

---

## 6. Phase D — Fretting Wear Coupling

**Priority: Medium | Effort: Medium | Risk: Medium**
**Theory reference:** LMQ §11.1–§11.5

### D.1 Fretting Regime Classification (`contacts/base.py`)

Add `compute_fretting_regime(delta_slip_um)` method:
```python
def compute_fretting_regime(self, delta_slip_um: float) -> str:
    if delta_slip_um < 5.0:    return 'stick'
    if delta_slip_um < 50.0:   return 'partial_slip'
    return 'gross_slip'
```

Add `compute_slip_index(delta_slip, delta_total)` → SI = δ_slip/δ_total.

### D.2 µ Degradation Model (`coupled_loosening_analyzer.py`)

Add `_update_friction_wear(N)` called each cycle:
```python
def _update_friction_wear(self, N: int):
    """Degrade µ due to fretting wear (LMQ §11.3)."""
    wear_factor = self.params.fretting_wear_factor  # default 0.30
    N_sat = self.params.fretting_N_sat              # default 5000
    fraction = min(N, N_sat) / N_sat
    mu_degraded = self.params.mu_thread_initial * (1.0 - wear_factor * fraction)
    self.params.mu_thread = max(mu_degraded, 0.04)  # floor at 0.04
    self.params.mu_bearing = self.params.mu_thread * 0.85
```

### D.3 Self-Locking Check (`coupled_loosening_analyzer.py`)

Add `_check_self_lock()` called after each µ update:
```python
def _check_self_lock(self) -> bool:
    """Returns True if self-locking condition is still satisfied (LMQ §11.4)."""
    lambda_rad = self.params.helix_angle_rad
    alpha_rad  = self.params.flank_angle_rad
    return np.tan(lambda_rad) < self.params.mu_thread * np.cos(alpha_rad)
```

When self-locking is lost: force transition to ROTATIONAL phase (irreversible).
Log: `"Self-locking condition violated at cycle {N}: tan(λ)={:.4f} ≥ µ×cos(α)={:.4f}"`

### D.4 Archard Preload Loss Integration (`numerical/preload_loss_models.py`)

Connect existing Archard formula to per-cycle preload update:
```python
def wear_preload_loss_per_cycle(k_sys, K_wear, F_n, delta_slip_mm,
                                H_hardness, A_contact_mm2) -> float:
    V_per_cycle = K_wear * F_n * delta_slip_mm / H_hardness  # mm³/cycle
    h_per_cycle = V_per_cycle / A_contact_mm2                # mm/cycle
    return k_sys * h_per_cycle                               # N/cycle
```

### D.5 New Parameters in `LooseningAnalysisParams`

```python
fretting_wear_factor: float = 0.30    # µ degradation fraction at saturation
fretting_N_sat: int = 5000            # cycles to saturation
K_wear_thread: float = 1e-5           # Archard wear coefficient (steel fretting)
H_thread_MPa: float = 1500.0          # Thread surface hardness
A_thread_contact_mm2: float = 200.0   # Thread bearing area
```

**Files changed:** `contacts/base.py`, `coupled_loosening_analyzer.py`, `numerical/preload_loss_models.py`

**Test:** `tests/test_fretting_wear.py` — verify µ degradation curve; verify self-locking violation triggers phase change; verify Archard loss accumulates correctly at 10 000 cycles.

---

## 7. Phase E — Loading Condition Support

**Priority: Medium | Effort: High | Risk: Medium**
**Theory reference:** LLC §1–§6

### E.1 Shear Joint Type (`core/models/model.py`)

Add `ShearJointType` enum: `BEARING_TYPE`, `FRICTION_TYPE`.
Add field to `MSDModel.global_loading` via `LoadingData`: `shear_joint_type: str = 'friction'`.

In `_simulate_cycle()`:
- Bearing-type: full transverse displacement drives bolt shank movement → use Junker model directly
- Friction-type: check friction capacity first; if not exceeded → no transverse micro-slip

### E.2 Bending Prying Correction (`coupled_loosening_analyzer.py`)

Add `_prying_correction(bending_moment_Nm, r_eff_mm, F_p_N)` [LLC §3.1]:
```python
def _prying_correction(M_Nm, r_eff_mm, F_p_N):
    """Returns factor to reduce slip threshold due to bearing pressure asymmetry."""
    r_eff_m = r_eff_mm / 1000.0
    F_asymmetry = M_Nm / r_eff_m     # Additional equivalent transverse force
    prying_ratio = F_asymmetry / F_p_N
    # ~8-12% threshold reduction per 10% asymmetry:
    reduction = min(0.12, prying_ratio * 1.2)
    return 1.0 - reduction            # Multiply into slip_onset_factor
```

### E.3 Impact Stage Model (`solver_worker.py`)

Add `_classify_impact_phase(delta_per_impact_mm, mu, F_p_N, k_joint_N_mm)`:
- Compute `delta_slip_threshold = mu * F_p_N / k_joint_N_mm` (slip threshold in mm)
- If `delta_per_impact < delta_slip_threshold`: → Stage I2 (no Junker activation)
- Else: → Stage I3+ (Junker mechanism, use rotational loosening rate per impact event)

### E.4 Miner's Rule Loosening Life (`coupled_loosening_analyzer.py`)

Add `predict_loosening_life(delta_amplitudes, n_cycles_per_amplitude)` [LMQ §12.3]:
```python
def predict_loosening_life(self, deltas_mm, ni_cycles,
                           A=1e8, b=3.0, criterion_ratio=0.80) -> dict:
    """Miner's rule: D = Σ(n_i / N_i) = 1 at criterion_ratio preload loss."""
    Ni = [A * (d ** -b) for d in deltas_mm]
    D_total = sum(n / N for n, N in zip(ni_cycles, Ni))
    N_remaining = (1.0 - D_total) * np.mean(Ni) if D_total < 1.0 else 0
    return {'damage': D_total, 'N_remaining': N_remaining,
            'life_exhausted': D_total >= 1.0}
```

**Files changed:** `core/models/model.py`, `core/models/element.py`, `coupled_loosening_analyzer.py`, `solver_worker.py`

**Test:** `tests/test_loading_conditions.py` — verify axial-only: zero nut rotation; verify bending prying threshold reduction; verify impact I2 vs I3 classification; verify Miner's rule D-N accuracy.

---

## 8. Phase F — Locking Device Database and Selector

**Priority: Low | Effort: Medium | Risk: Low**
**Theory reference:** LMQ §13

### F.1 Locking Device Data File

Create `src/bolt_analysis_studio/core/databases/locking_devices.json`:
```json
{
  "devices": [
    { "name": "Plain nut (no lock)",   "retention_2000_cycles": [0.0, 0.05], "max_temp_C": 300, "reusable": true  },
    { "name": "Spring washer",         "retention_2000_cycles": [0.10, 0.40], "max_temp_C": 300, "reusable": true  },
    { "name": "Nyloc nut (DIN 985)",   "retention_2000_cycles": [0.30, 0.70], "max_temp_C": 120,  "reusable": false },
    { "name": "All-metal prevailing",  "retention_2000_cycles": [0.40, 0.80], "max_temp_C": 300, "reusable": true  },
    { "name": "Nord-Lock wedge",       "retention_2000_cycles": [0.60, 0.95], "max_temp_C": 300, "reusable": true  },
    { "name": "Loctite 242 (blue)",    "retention_2000_cycles": [0.85, 1.00], "max_temp_C": 150,  "reusable": false },
    { "name": "Loctite 271 (red)",     "retention_2000_cycles": [0.85, 1.00], "max_temp_C": 150,  "reusable": false },
    { "name": "Safety wire / castle",  "retention_2000_cycles": [0.99, 1.00], "max_temp_C": 500, "reusable": true  }
  ],
  "iso_2320_prevailing_torque": {
    "M6":  { "min_Nm": 0.5, "max_Nm": 3.5 },
    "M8":  { "min_Nm": 0.7, "max_Nm": 5.0 },
    "M10": { "min_Nm": 1.0, "max_Nm": 7.5 },
    "M12": { "min_Nm": 1.5, "max_Nm": 10.0 },
    "M16": { "min_Nm": 3.0, "max_Nm": 18.0 },
    "M20": { "min_Nm": 5.0, "max_Nm": 28.0 }
  }
}
```

### F.2 Locking Device Selector in PropertyInspector

Add "Locking" section to Contact > Global sub-tab:
- `locking_device_combo` (QComboBox, populated from `locking_devices.json`)
- Read-only labels: expected retention range, temperature limit
- Warning if operating temperature > `max_temp_C`
- ISO 16130 pass/fail indicator based on expected retention vs. 80% threshold

### F.3 Locking Device Effect in Loosening Analyzer

When a locking device is selected, apply its effect to the cycle loop:
```python
# Residual preload floor from locking device:
F_p_floor = F_p0 * locking_device.min_retention
if self.state.current_preload <= F_p_floor:
    # Loosening has reached the device's floor — mark as stabilized
    self.state.phase = LooseningPhase.NON_ROTATIONAL
    break
```

**Files changed:** New `locking_devices.json`, `msd_builder.py`, `coupled_loosening_analyzer.py`

**Test:** `tests/test_locking_devices.py` — verify floor effect stops loosening at device minimum; verify temperature warning triggers; verify ISO 16130 pass/fail.

---

## 9. Testing Plan

### Unit Tests (new files)

| File | Tests | Phase |
|------|-------|-------|
| `tests/test_load_factors.py` | R-factor → F_mean/F_alt; Φ auto vs manual; separation trigger; waveform shapes | A |
| `tests/test_stage_transitions.py` | All 5 phase boundaries; 0.5° rotation criterion; double-exponential Stage 1 | B |
| `tests/test_slip_criterion.py` | Pai-Hess 46% vs classical; axial-only = zero rotation; combined interaction | C |
| `tests/test_fretting_wear.py` | µ degradation curve; self-locking violation; Archard loss accumulation | D |
| `tests/test_loading_conditions.py` | Axial vs transverse rate ratio; bending prying; impact I2/I3; Miner's D-N | E |
| `tests/test_locking_devices.py` | Retention floor; temperature warning; ISO 16130 pass/fail | F |

### Integration Tests

```bash
# Run full loosening analysis with R=-1 (Junker) vs R=0 (pulsating):
python -m pytest tests/test_stage_transitions.py tests/test_slip_criterion.py -v

# Run matrix assembly tests (already passing):
python -m pytest tests/test_matrix_assembly.py tests/test_validation_cases.py -v

# Full test suite (excluding test_gui.py per CLAUDE.md):
python -m pytest tests/ --ignore=tests/test_gui.py -v
```

### Validation Benchmarks

| Benchmark | Expected Result | Theory Ref | Phase |
|-----------|----------------|------------|-------|
| Junker M10, F_p0=30 kN, µ=0.12, δ=0.5 mm | Slip at δ×µ×F_p = 3.6 kN (classical) or 1.7 kN (Pai-Hess) | LMQ §1.2 | C |
| Stage 1 double-exponential fit vs Tsinghua data | R² > 0.95 for first 1000 cycles | LMQ §12.2 | B |
| VDI 2230 embedding: M16, 4 interfaces, Rz=10µm | ΔF ≈ 4.8 kN = 9.6% of 50 kN | LMQ §2.2 | A (existing) |
| Fretting wear, M16, 10 000 cycles | ΔF_wear ≈ 330 N (0.66% of 50 kN) | LMQ §11.5 | D |
| Nyloc M12 residual preload plateau | F_p_residual = 2–5 kN (10–25% of F_p0) | LMQ §13.2 | F |
| Miner's rule M10, variable amplitude | Prediction within ±1.2× of test data | LMQ §12.3 | E |

---

## 10. Priority Matrix

```
HIGH IMPACT / LOW EFFORT (do first):
  ✦ Phase B — Five-Stage Phase Boundaries        (classifies existing solver output)
  ✦ Phase C — Pai-Hess Corrected Slip Criterion  (improves all existing analyses immediately)

HIGH IMPACT / MEDIUM EFFORT:
  ✦ Phase A — VDI 2230 Load Factors GUI + Code   (new capability; 6 files)
  ✦ Phase D — Fretting Wear µ Coupling           (long-term accuracy improvement)

MEDIUM IMPACT / MEDIUM EFFORT:
  ◆ Phase E — Loading Condition Support           (shear, bending, impact, Miner)

LOW IMPACT / LOW EFFORT (do last):
  ◇ Phase F — Locking Device Database            (reference/reporting; no solver change)
```

### Recommended Implementation Order

```
B → C → A → D → E → F
│    │    │    │    │    └─ F: locking DB (standalone, any time)
│    │    │    │    └─────── E: loading conditions (builds on B, C, A)
│    │    │    └──────────── D: fretting wear (builds on C; independent of A)
│    │    └─────────────────  A: load factors GUI (builds on B, C for slip check)
│    └──────────────────────── C: Pai-Hess slip (1-day change; immediate benefit)
└───────────────────────────── B: stage boundaries (1-day change; immediate benefit)
```

---

## 11. File Change Summary

| File | Phase | Change Type | Backward Compatible? |
|------|-------|-------------|---------------------|
| `core/models/element.py` | A | Add 5 fields to `LoadingData` | Yes (defaults) |
| `numerical/time_integration.py` | A | Add `biased_harmonic_force()` | Yes (additive) |
| `solver_worker.py` | A, B, E | Add configs, phase classifier, impact classifier | Yes (defaults) |
| `core/models/model.py` | A, E | Update `assemble_force_vector()`, add `ShearJointType` | Yes (optional flag) |
| `coupled_loosening_analyzer.py` | A, B, C, D, E | Major updates to cycle loop | Yes (defaults) |
| `gui/msd_builder.py` | A, F | Add R/Φ/n/φ widgets, locking device selector | Yes |
| `contacts/base.py` | D | Add `compute_fretting_regime()`, `compute_slip_index()` | Yes (additive) |
| `contacts/thread.py` | D | Use fretting regime in slip calculation | Yes (flag) |
| `numerical/preload_loss_models.py` | D | Connect Archard to per-cycle update | Yes |
| `core/databases/locking_devices.json` | F | New file | N/A |
| `tests/test_load_factors.py` | A | New test file | N/A |
| `tests/test_stage_transitions.py` | B | New test file | N/A |
| `tests/test_slip_criterion.py` | C | New test file | N/A |
| `tests/test_fretting_wear.py` | D | New test file | N/A |
| `tests/test_loading_conditions.py` | E | New test file | N/A |
| `tests/test_locking_devices.py` | F | New test file | N/A |

---

## 12. Key Design Decisions

### Decision 1: Pai-Hess Factor as Configurable Parameter
The corrected slip onset (0.46–0.66 × µ × F_K_min) is exposed as `slip_onset_factor`
in `LooseningAnalysisParams`. Default = 0.46 (conservative). This lets users tune it
for their specific joint geometry or compare against Junker test data.

**Rationale:** The Pai-Hess factor varies with joint geometry and surface condition.
A fixed value of 0.46 would be over-conservative for some joints; making it configurable
allows matching to experimental data.

### Decision 2: µ Degradation as Optional
The fretting wear µ degradation (Phase D) is enabled by `fretting_wear_enabled: bool = False`
by default. When disabled, µ is constant (existing behavior). This avoids changing
existing validated results.

**Rationale:** Fretting wear is significant only at high cycle counts (>5 000). For
typical analysis runs (500–2 000 cycles), the effect is <5% and the added computation
is unnecessary.

### Decision 3: Waveform Does Not Change Total Energy
The waveform shape (square vs sinusoidal) at the same F_max and F_min produces different
peak force rates but the same energy per cycle. The loosening rate per cycle is dominated
by the peak transverse force (not the average), so square-wave Junker tests are more
severe than sinusoidal at the same amplitude.

**Implementation:** `biased_harmonic_force()` normalises waveforms to [−1, +1] range,
so F_max and F_min are always reached regardless of waveform shape.

### Decision 4: Stage 1 Double-Exponential Overlays Existing Model
The double-exponential Stage 1 model (Phase B) is added as an **overlay** on top of
the existing preload loss mechanisms (embedding, relaxation, gasket creep). It represents
the combined Stage 1 effect without replacing the individual mechanism models.

At N > 5×N₂ (typically N > 5 000), the Stage 1 overlay saturates and the Stage 2
rotational model takes over entirely.
