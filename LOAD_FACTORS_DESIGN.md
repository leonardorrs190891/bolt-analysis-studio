# Load Factors Integration — Design Document

**Bolt Analysis Studio v4.0**
LTAD/UFU — Petrobras R&D
February 2026

---

## Document Set

This document is part of a coordinated four-document reference for the BAS loosening analysis framework:

| Document | Scope |
|----------|-------|
| `LOOSENING_MECHANISMS_QUANTITATIVE.md` | Theory: mechanism taxonomy, fretting regime map, five-stage phase model, locking devices (§1–§13) |
| `LOOSENING_LOADING_CONDITIONS.md` | Theory: loading-type-specific analysis — axial, shear, bending, impact, combined (§1–§7) |
| **`LOAD_FACTORS_DESIGN.md`** (this document) | Software design: VDI 2230 load factors R, Φ, n, φ, waveform |
| `LOOSENING_IMPLEMENTATION_PLAN.md` | Master implementation plan: phased tasks, theory→code mapping, test plan |

Cross-references below use the notation `[LMQ §X]` for `LOOSENING_MECHANISMS_QUANTITATIVE.md`
and `[LLC §X]` for `LOOSENING_LOADING_CONDITIONS.md`.

---

## 1. Motivation

The current `LoadingData` dataclass defines cyclic loading via a **single amplitude** (`F_amplitude`) plus frequency. This is insufficient for realistic bolted joint analysis because:

1. Real service loads are rarely symmetric about zero. The **stress ratio R = F_min/F_max** determines whether the load is tensile-only (R ≥ 0), fully reversed (R = −1), or compressive (R < 0). This changes friction forces, separation risk, and fatigue life.

2. The **VDI 2230 load factor Φ** (resilience ratio) governs how an external axial force splits between the bolt and the clamped members. Currently, `create_analyzer_from_msd_model()` estimates Φ implicitly from assembled [K] diagonals, but the GUI never exposes it or lets the analyst override it.

3. **Where the load enters** the joint (at the nut face, mid-grip, or joint interface) changes how much of the external force becomes "seen" by the bolt. This is the **force application factor n** (VDI 2230 §5.4).

4. **Impact/dynamic amplification φ** is not modelled at all. A suddenly applied load is amplified by up to 2× compared to quasi-static.

5. The **load waveform** is always sinusoidal. Square-wave and triangular shapes are common in Junker test rigs.

### 1.1 Theoretical Context

The load factor variables in this document are grounded in the companion theory documents:

- **Stage transitions** [LMQ §12.5]: When F_K_min drops below thresholds (0.90 / 0.75 / 0.55 / 0.20 × F_p0), the loosening phase changes. The R-factor and Φ directly determine F_K_min at peak load, and therefore which stage the joint is in.

- **Pai & Hess corrected slip criterion** [LMQ §12.1]: Rotational loosening initiates at only **46–66 %** of the classical µ×F_K_min threshold. The R-factor affects the worst-case F_K_min each cycle, which sets the effective slip onset.

- **Axial vs. transverse severity** [LLC §1.3]: Pure axial loading (R ≥ 0, no transverse) does NOT cause Junker loosening. However, it lowers F_K_min, reducing the transverse force needed to trigger slip. This interaction is captured by the Φ_eff and separation check.

- **Impact amplification** [LLC §4]: The dynamic factor φ models single-event and repeated-impact preload reduction; φ = 2 corresponds to a suddenly applied load (theoretical maximum for a linear system). The Hopkinson bar studies confirm tightening–loosening alternation, which the waveform parameter can approximate with a square wave.

- **Shear joint type** [LLC §2]: For a bearing-type joint where the bolt carries transverse load directly (n=1), Φ_eff = Φ and the full transverse force reduces clamp force. For a friction-type joint (n=0), the transverse force is ideally carried by friction and does not reduce the bolt clamp force until slip occurs.

- **Fretting wear coupling** [LMQ §11.4]: As µ degrades due to fretting (20–40% reduction after 5 000 cycles), the Pai-Hess slip threshold drops proportionally, accelerating the transition to ROTATIONAL phase even without changes to the applied load.

---

## 2. New Variables — Definitions

### 2.1 Load Ratio (Stress Ratio) — R

```
R = F_min / F_max       (-∞ < R < 1, but physically -1 ≤ R < 1 for bolts)
```

| R value | Load type | Typical scenario |
|---------|-----------|-----------------|
| R = 1 | Constant load | Static case, no fatigue |
| R = 0 | Pulsating tension | Pressure vessel, zero-to-max |
| R = 0.1 | Light tension pulsation | Typical service |
| R = -1 | Fully reversed | Vibration test, Junker |
| R < -1 | Compressive max | Heavy impact (rare) |

**Derived mean/alternating decomposition:**
```
F_mean  = F_max × (1 + R) / 2
F_alt   = F_max × (1 − R) / 2
F_ext(t) = F_mean + F_alt × waveform(t)
```

where `F_max` maps to the existing `F_amplitude` field (to be renamed to `F_max` or kept with a derived property).

### 2.2 Load Factor (Resilience Ratio) — Φ  *(VDI 2230 §5.2)*

```
Φ_K = C_S / (C_bolt + C_S)
```

where C_bolt = bolt axial stiffness, C_S = members (clamped parts) stiffness.

Physical meaning: fraction of external axial force that increases bolt force. The complementary fraction (1 − Φ) reduces the clamp force.

- Φ close to 0: stiff joint (plates much stiffer than bolt) → external force mostly relieves clamp
- Φ close to 1: flexible joint (bolt much stiffer than members) → external force mostly stretches bolt

**Auto-compute**: Φ can be derived from the assembled [K] matrix (already done partially in `create_analyzer_from_msd_model()`), but the analyst should also be able to override it.

**VDI 2230 eccentricity correction:**
```
Φ_K_eccentric = Φ_K_centric × (1 + (s_sym × a_p) / I_T)
```
For the basic implementation, use the centric value and document the eccentricity correction as future work.

### 2.3 Force Application Factor — n  *(VDI 2230 §5.4)*

```
n ∈ [0, 1]
```

| n | Load introduced at | Typical element |
|---|-------------------|--------------------|
| 0 | Nut/head bearing face (outside clamped member) | External flange attachment |
| 0.5 | Mid-grip (inside clamped member) | Pipe flange bolt hole |
| 1 | Joint interface (between the two members) | Junker test fixture |

Effect on load factor:
```
Φ_n = Φ_K × n   +   (1 − n) × 0       →   Φ_effective = n × Φ_K
```

Strictly, a load introduced at the joint interface (n=1) sees the full stiffness ratio. A load introduced outside at the bearing face (n=0) is fully external and does not benefit from member stiffness.

### 2.4 Dynamic Amplification Factor — φ

```
F_impact = φ × F_static
```

| φ | Loading type |
|---|-------------|
| 1.0 | Quasi-static |
| 1.2 | Slow transient |
| 1.5 | Machinery vibration |
| 2.0 | Sudden impact (φ_max for linear system) |

For sinusoidal loads near resonance:
```
φ = 1 / sqrt((1 − (f/f_n)²)² + (2ζ × f/f_n)²)
```
where f_n is the natural frequency (from assembled [M][K]) and ζ is the modal damping ratio.

### 2.5 Load Waveform

| Value | Description | F(t) |
|-------|-------------|------|
| `"sinusoidal"` | Smooth harmonic (default) | F_mean + F_alt × sin(ωt) |
| `"square"` | Junker-type rectangular | F_max or F_min, step-switched |
| `"triangular"` | Linear ramp up/down | Piecewise-linear |
| `"sawtooth"` | One-sided ramp | Used in ratchet studies |
| `"random"` | Gaussian noise (σ = F_alt) | Power-law spectrum |

---

## 3. Derived Quantities — Auto-Computed Labels in GUI

All of the following are **read-only** labels in the UI, computed live whenever inputs change:

| Symbol | Formula | Location |
|--------|---------|----------|
| F_mean | `F_max × (1+R) / 2` | Loading > Global |
| F_alt | `F_max × (1−R) / 2` | Loading > Global |
| Φ (auto) | `k_bolt / (k_bolt + k_member)` | Loading > Global |
| F_bolt_alt | `Φ_eff × F_alt × φ` | Loading > Global |
| ΔF_clamp | `(1−Φ_eff) × F_max × φ` | Loading > Global |
| F_K_min | `F_preload − ΔF_clamp` | Loading > Global |
| Separation? | `F_K_min > 0` → OK / WARNING | Loading > Global |
| σ_a_bolt | `F_bolt_alt / A_s` | Loading > Global |

The **separation check** is safety-critical: if F_K_min ≤ 0, the joint opens under peak load, which causes immediate rotational loosening regardless of friction.

---

## 4. How Load Factors Enter the System Matrices

### 4.1 External Force Vector {F_ext}(t)

**Current implementation** (`solver_worker.py:_run_time_integration`, line ~561):
```python
F_amplitude[load_dof] = config.load_amplitude
F_func = harmonic_force(F_amplitude, config.load_frequency)
# → F(t) = A × sin(ωt)   (zero mean, R = -1 implicitly)
```

**Target implementation:**
```python
F_mean_vec = np.zeros(n_dof)
F_alt_vec  = np.zeros(n_dof)
F_mean_vec[load_dof] = config.F_max * (1 + config.R_factor) / 2
F_alt_vec[load_dof]  = config.F_max * (1 - config.R_factor) / 2 * config.dynamic_factor

F_func = biased_harmonic_force(F_mean_vec, F_alt_vec,
                                config.load_frequency,
                                waveform=config.load_waveform)
# → F(t) = F_mean + F_alt × waveform(t)
```

A new function `biased_harmonic_force()` needs to be added to `time_integration.py`.

### 4.2 Contact Normal Force — F_N(t)

The contact normal force at any time step is:

```
F_N_bolt(t)      = F_preload  +  Φ_eff × F_ext(t)     [bolt tension]
F_N_interface(t) = F_preload  −  (1−Φ_eff) × F_ext(t) [clamp force]
```

where `Φ_eff = n_load_plane × Phi_load`.

This is consumed in `model.assemble_force_vector()` via the `preload` argument and in `contact.update_state()`. Currently `contact.normal_force = preload` (constant). The change is:

```python
# Current (model.py ~line 631):
contact.normal_force = preload

# Target:
phi_eff = model.global_loading.n_load_plane * model.global_loading.Phi_load
F_ext_current = F_external[load_dof]  # current instantaneous external force
contact.normal_force = preload + phi_eff * F_ext_current
```

For the **loosening analysis**, the critical normal forces are:
- **Thread contact**: `F_N = F_preload + Φ_eff × F_ext(t)` — always compressive, does not separate
- **Bearing contact**: same as thread
- **Interface/flange contact**: `F_N = F_preload − (1−Φ_eff) × F_ext(t)` — can open if F_ext large

### 4.3 Friction Force in {F}

Thread resisting torque (opposes loosening):
```
T_thread(t) = μ_t × F_N_bolt(t) × d₂ / (2 × cos(α))
            = μ_t × [F_preload + Φ_eff × F_ext(t)] × d₂ / (2 × cos(α))
```

Bearing resisting torque:
```
T_bearing(t) = μ_b × F_N_bolt(t) × r_eff
```

Helix torque (drives loosening when interface slips):
```
T_helix(t) = F_N_bolt(t) × r × tan(λ)
```

With varying F_ext, all three terms now oscillate. The **loosening condition** becomes:

```
Slip occurs when:  F_transverse(t) > μ_eff × F_N_interface(t)

After slip, nut advances by:  Δθ = p / (2π × N_threads)

Net loosening per cycle:  Δθ_net = Δθ_slip − Δθ_retighten
```

If `F_N_interface` drops to zero (separation), Δθ_net is maximal — full loosening per cycle.

> **Pai & Hess correction** [LMQ §12.1]: the classical slip condition `F_trans > µ × F_K_min`
> overestimates resistance by 1.5–2×. The corrected onset threshold is 46–66 % of that value.
> See §11 below for implementation guidance.

> **Axial + transverse interaction** [LLC §5.1]: When the external load has both axial and
> transverse components, use the combined check:
> `F_trans / (µ × F_K_min) + F_axial / F_sep ≤ 1.0`

### 4.4 Coupled Loosening Analyzer Integration

In `create_analyzer_from_msd_model()`, add R-factor extraction:

```python
# Add after extracting n_cycles (line ~2489):
R_factor = getattr(loading, 'R_factor', 0.0)
Phi_load = getattr(loading, 'Phi_load', None)  # None = auto-compute
n_plane  = getattr(loading, 'n_load_plane', 0.5)
dyn_fac  = getattr(loading, 'dynamic_factor', 1.0)

info['R_factor'] = R_factor
info['n_load_plane'] = n_plane
info['dynamic_factor'] = dyn_fac

# If Phi not user-specified, compute from k_bolt / k_member (already done ~line 2600):
if Phi_load is None:
    Phi_load = k_bolt / (k_bolt + k_member)   # Resilience ratio
info['Phi_load'] = Phi_load

Phi_eff = n_plane * Phi_load
info['Phi_effective'] = Phi_eff

# Applied to analyzer:
analyzer.params.R_factor    = R_factor
analyzer.params.Phi_eff     = Phi_eff
analyzer.params.dynamic_fac = dyn_fac
```

Inside the loosening cycle loop (around `_simulate_cycle()` in `CoupledLooseningAnalyzer`), replace:

```python
# Current (constant amplitude transverse force):
F_trans = self.params.transverse_force_amplitude

# Target (peak force accounting for R):
F_max_trans = self.params.transverse_force_amplitude * self.params.dynamic_fac
F_min_trans = F_max_trans * self.params.R_factor
# Normal force at worst-case moment (peak external load):
F_N_min = (self.params.current_preload
           - (1 - self.params.Phi_eff) * F_max_trans / self.params.dynamic_fac
           × ... )
```

---

## 5. Changes Required — File by File

### 5.1 `src/bolt_analysis_studio/core/models/element.py`

**What**: Add 5 new fields to `LoadingData` + update `to_dict()`/`from_dict()`

**New fields** (add after `phase_transverse`):
```python
# --- Load Factors (VDI 2230 / fatigue) ---
R_factor: float = 0.0          # Load ratio R = F_min/F_max (−1 ≤ R < 1)
                                # R=0 → pulsating tension; R=−1 → fully reversed
Phi_load: Optional[float] = None  # VDI 2230 load factor Φ (None = auto from [K])
n_load_plane: float = 0.5      # Force application factor (0=bearing face, 1=interface)
dynamic_factor: float = 1.0    # Impact/dynamic amplification φ (1.0 = quasi-static)
load_waveform: str = "sinusoidal"  # "sinusoidal"|"square"|"triangular"|"sawtooth"|"random"
```

**Fix `get_loading_ratio()`** — current implementation computes R relative to preload (wrong for cyclic analysis):
```python
# Current (wrong for cyclic fatigue):
def get_loading_ratio(self) -> float:
    F_max = self.F_preload + self.F_amplitude
    F_min = self.F_preload - self.F_amplitude
    return F_min / F_max

# Corrected — R is the ratio of the CYCLIC load extremes, not bolt stress extremes:
@property
def R(self) -> float:
    """Load ratio of the applied cyclic force (not bolt stress)."""
    return self.R_factor

@property
def F_mean(self) -> float:
    """Mean component of cyclic force [N]."""
    return self.F_amplitude * (1 + self.R_factor) / 2

@property
def F_alt(self) -> float:
    """Alternating component of cyclic force [N]."""
    return self.F_amplitude * (1 - self.R_factor) / 2
```

**Update `to_dict()` / `from_dict()`**:
```python
# to_dict — add:
"R_factor": self.R_factor,
"Phi_load": self.Phi_load,
"n_load_plane": self.n_load_plane,
"dynamic_factor": self.dynamic_factor,
"load_waveform": self.load_waveform,

# from_dict — already handled generically by cls(**{k:v ...}) pattern
# but add None-safe handling for Phi_load:
if 'Phi_load' in data and data['Phi_load'] == 'null':
    data['Phi_load'] = None
```

---

### 5.2 `src/bolt_analysis_studio/numerical/time_integration.py`

**What**: Add `biased_harmonic_force()` and update waveform functions to support R factor.

**New function** (add alongside `harmonic_force`):
```python
def biased_harmonic_force(
    F_mean: np.ndarray,
    F_alt: np.ndarray,
    frequency: float,
    phase: float = 0.0,
    waveform: str = "sinusoidal"
) -> Callable[[float], np.ndarray]:
    """
    Create force function with mean offset and arbitrary waveform.

    F(t) = F_mean + F_alt × w(ωt + φ)

    where w(θ) is the normalized waveform:
      - "sinusoidal":  w = sin(θ)
      - "square":      w = sign(sin(θ))
      - "triangular":  w = (2/π) × arcsin(sin(θ))
      - "sawtooth":    w = 2 × (θ/(2π) − floor(θ/(2π) + 0.5))
    """
    import numpy as np
    omega = 2 * np.pi * frequency
    F_mean = np.asarray(F_mean, dtype=float)
    F_alt  = np.asarray(F_alt,  dtype=float)

    waveform_funcs = {
        "sinusoidal": lambda theta: np.sin(theta),
        "square":     lambda theta: np.sign(np.sin(theta)),
        "triangular": lambda theta: (2 / np.pi) * np.arcsin(np.clip(np.sin(theta), -1, 1)),
        "sawtooth":   lambda theta: 2 * (theta / (2*np.pi) - np.floor(theta / (2*np.pi) + 0.5)),
    }
    w_func = waveform_funcs.get(waveform, waveform_funcs["sinusoidal"])

    def F(t: float) -> np.ndarray:
        theta = omega * t + phase
        return F_mean + F_alt * w_func(theta)

    return F
```

---

### 5.3 `src/bolt_analysis_studio/core/solver_worker.py`

**What**: Update `TimeIntegrationConfig` and `CoupledLooseningConfig` + use new force function.

**`TimeIntegrationConfig`** — add fields (after `load_dof`):
```python
# Load ratio and waveform
R_factor: float = 0.0           # Load ratio (0 = pulsating, -1 = fully reversed)
dynamic_factor: float = 1.0     # Impact amplification
load_waveform: str = "sinusoidal"

# VDI 2230 load factors
Phi_load: Optional[float] = None   # None = auto from k_bolt/k_member
n_load_plane: float = 0.5          # Force application factor
```

**`CoupledLooseningConfig`** — add fields:
```python
R_factor: float = 0.0
Phi_load: Optional[float] = None
n_load_plane: float = 0.5
dynamic_factor: float = 1.0
load_waveform: str = "sinusoidal"
```

**`_run_time_integration()`** — replace F_func construction:
```python
# Replace lines ~557-569:
loading = model.global_loading if (model and hasattr(model, 'global_loading')) else None
R   = getattr(loading, 'R_factor',      config.R_factor)
phi = getattr(loading, 'dynamic_factor', config.dynamic_factor)
wfm = getattr(loading, 'load_waveform', config.load_waveform)

F_max_val = config.load_amplitude * phi
F_mean_vec = np.zeros(n_dof)
F_alt_vec  = np.zeros(n_dof)
F_mean_vec[load_dof] = F_max_val * (1 + R) / 2
F_alt_vec[load_dof]  = F_max_val * (1 - R) / 2

F_func = biased_harmonic_force(F_mean_vec, F_alt_vec,
                                config.load_frequency, waveform=wfm)
```

---

### 5.4 `src/bolt_analysis_studio/core/models/model.py`

**What**: Update `assemble_force_vector()` to use time-varying normal force in contacts.

```python
def assemble_force_vector(self, x, x_dot, t, F_external, preload=0.0):
    F_total = F_external.copy()
    ...
    # New: compute effective normal force at this instant
    phi_eff = getattr(self, '_phi_eff', None)
    if phi_eff is not None and len(F_external) > 0:
        # Find load DOF (first non-zero in F_external, or use stored _load_dof)
        load_dof = getattr(self, '_load_dof', 0)
        F_ext_now = F_external[load_dof] if load_dof < len(F_external) else 0.0
        effective_normal = preload + phi_eff * F_ext_now
    else:
        effective_normal = preload

    for contact in self.contacts:
        ...
        contact.normal_force = effective_normal   # was: contact.normal_force = preload
        ...
```

The `_phi_eff` and `_load_dof` are set when the model is exported from MSD Builder:
```python
# In export_to_msd_model() or after assemble_matrices():
model._phi_eff   = n_load_plane * Phi_load   # from global_loading
model._load_dof  = loading_dof_index
```

---

### 5.5 `src/bolt_analysis_studio/numerical/coupled_loosening_analyzer.py`

**What**: Pass R_factor, Phi_eff, dynamic_factor through to the cycle simulation.

**In `create_analyzer_from_msd_model()`** (after existing extraction block ~line 2489):
```python
# Extract new load factors
if hasattr(model, 'global_loading') and model.global_loading:
    loading = model.global_loading
    R_factor      = getattr(loading, 'R_factor',       0.0)
    Phi_load_user = getattr(loading, 'Phi_load',        None)
    n_plane       = getattr(loading, 'n_load_plane',    0.5)
    dynamic_fac   = getattr(loading, 'dynamic_factor',  1.0)
else:
    R_factor = 0.0; Phi_load_user = None; n_plane = 0.5; dynamic_fac = 1.0

# Compute Phi if not user-specified (uses k_bolt/k_member already computed above)
if Phi_load_user is not None and 0 < Phi_load_user <= 1:
    Phi_load = Phi_load_user
    info['Phi_source'] = 'user'
else:
    Phi_load = k_bolt / (k_bolt + k_member)
    info['Phi_source'] = 'auto_from_K'

Phi_eff = n_plane * Phi_load
info['R_factor']      = R_factor
info['Phi_load']      = Phi_load
info['Phi_eff']       = Phi_eff
info['dynamic_factor']= dynamic_fac
```

**In `LooseningAnalysisParams`** (the dataclass for analyzer parameters), add:
```python
R_factor: float = 0.0
Phi_eff: float = 0.3        # Typical bolted flange
dynamic_factor: float = 1.0
```

**In the cycle simulation loop**, update friction forces:
```python
# Current:
F_normal = self.state.current_preload

# Target:
# F_ext cycles between F_ext_max and R × F_ext_max
F_ext_max = self.params.transverse_force_amplitude * self.params.dynamic_factor
F_ext_min = F_ext_max * self.params.R_factor

# Thread/bolt normal force (increases with F_ext):
F_N_bolt_max = self.state.current_preload + self.params.Phi_eff * F_ext_max
F_N_bolt_min = self.state.current_preload + self.params.Phi_eff * F_ext_min

# Interface clamp force (decreases with F_ext):
F_K_max = self.state.current_preload - (1 - self.params.Phi_eff) * F_ext_min  # clamp at min load
F_K_min = self.state.current_preload - (1 - self.params.Phi_eff) * F_ext_max  # clamp at peak load

# Separation check
if F_K_min <= 0:
    # Joint opens → full immediate loosening contribution
    separation_factor = abs(F_K_min) / self.state.current_preload
    # loosening rate increases proportionally
else:
    separation_factor = 0.0

# Thread friction torque at worst-case (peak external force):
T_thread_resist = (self.params.mu_thread * F_N_bolt_max
                   * self.params.pitch_diameter_m / (2 * np.cos(self.params.flank_angle_rad)))

# Loosening condition uses F_K_min (worst-case clamp):
slip_condition = F_ext_max > self.params.mu_bearing * F_K_min
```

---

### 5.6 `src/bolt_analysis_studio/gui/msd_builder.py`

**What**: Add new widgets to the Loading > Global sub-tab in `PropertyInspector`.

**New widgets in `_setup_loading_group()`** (or wherever the loading form is built):

```python
# === Load Ratio (R factor) ===
self.R_factor_spin = QDoubleSpinBox()
self.R_factor_spin.setRange(-1.0, 0.99)
self.R_factor_spin.setValue(0.0)
self.R_factor_spin.setDecimals(2)
self.R_factor_spin.setSingleStep(0.1)
self.R_factor_spin.setToolTip(
    "Load ratio R = F_min / F_max\n"
    "R = 0:  pulsating tension (0 to F_max)\n"
    "R = -1: fully reversed (−F_max to +F_max)\n"
    "R = 0.1: typical service condition")
self.R_factor_spin.valueChanged.connect(self._on_loading_param_changed)

# === Dynamic factor ===
self.dynamic_factor_spin = QDoubleSpinBox()
self.dynamic_factor_spin.setRange(1.0, 3.0)
self.dynamic_factor_spin.setValue(1.0)
self.dynamic_factor_spin.setDecimals(2)
self.dynamic_factor_spin.setSingleStep(0.1)
self.dynamic_factor_spin.setToolTip(
    "Dynamic amplification factor φ\n"
    "1.0 = quasi-static\n"
    "1.5 = machinery vibration\n"
    "2.0 = sudden impact")
self.dynamic_factor_spin.valueChanged.connect(self._on_loading_param_changed)

# === Force application factor (n) ===
self.n_load_plane_spin = QDoubleSpinBox()
self.n_load_plane_spin.setRange(0.0, 1.0)
self.n_load_plane_spin.setValue(0.5)
self.n_load_plane_spin.setDecimals(2)
self.n_load_plane_spin.setSingleStep(0.1)
self.n_load_plane_spin.setToolTip(
    "Force application factor n (VDI 2230 §5.4)\n"
    "n = 0: load at nut/head bearing face\n"
    "n = 0.5: load at mid-grip\n"
    "n = 1: load at joint interface (Junker test)")
self.n_load_plane_spin.valueChanged.connect(self._on_loading_param_changed)

# === Load factor Phi (override) ===
self.phi_load_spin = QDoubleSpinBox()
self.phi_load_spin.setRange(0.0, 1.0)
self.phi_load_spin.setValue(0.0)          # 0 = auto-compute
self.phi_load_spin.setDecimals(3)
self.phi_load_spin.setSingleStep(0.01)
self.phi_load_spin.setSpecialValueText("auto")   # shown when value == 0
self.phi_load_spin.setToolTip(
    "VDI 2230 load factor Φ = C_member / (C_bolt + C_member)\n"
    "Set to 0 for automatic calculation from model stiffness.\n"
    "Typical range: 0.1 (rigid joint) to 0.5 (flexible)")
self.phi_load_spin.valueChanged.connect(self._on_loading_param_changed)

# === Load waveform ===
self.load_waveform_combo = QComboBox()
for wf in [("Sinusoidal", "sinusoidal"), ("Square / Junker", "square"),
           ("Triangular", "triangular"), ("Sawtooth", "sawtooth")]:
    self.load_waveform_combo.addItem(wf[0], wf[1])
self.load_waveform_combo.setToolTip(
    "Waveform shape of the cyclic loading.\n"
    "'Square / Junker' matches the DIN 65151 test rig profile.")
self.load_waveform_combo.currentIndexChanged.connect(self._on_loading_param_changed)

# === Read-only derived labels ===
self.R_derived_Fmean_label  = QLabel("F_mean: —")
self.R_derived_Falt_label   = QLabel("F_alt:  —")
self.R_derived_Phi_label    = QLabel("Φ (auto): —")
self.R_derived_FKmin_label  = QLabel("F_K_min: —")
self.R_separation_label     = QLabel("")  # "OK" or "WARNING: separation"
```

**Add rows to form layout:**
```python
loading_layout.addRow("Load ratio (R):", self.R_factor_spin)
loading_layout.addRow("Force applic. (n):", self.n_load_plane_spin)
loading_layout.addRow("Dyn. factor (φ):", self.dynamic_factor_spin)
loading_layout.addRow("Load factor (Φ):", self.phi_load_spin)
loading_layout.addRow("Waveform:", self.load_waveform_combo)

# Separator
sep = QLabel("─── Derived ────────────────")
sep.setStyleSheet(f"color: {Theme.OVERLAY};")
loading_layout.addRow(sep)

loading_layout.addRow("", self.R_derived_Fmean_label)
loading_layout.addRow("", self.R_derived_Falt_label)
loading_layout.addRow("", self.R_derived_Phi_label)
loading_layout.addRow("", self.R_derived_FKmin_label)
loading_layout.addRow("", self.R_separation_label)
```

**Update `_on_loading_param_changed()` / `_on_bolt_geom_changed()`** to refresh derived labels:
```python
def _refresh_load_factor_labels(self):
    F_max  = self.preload_force_spin.value()   # or F_amplitude widget
    R      = self.R_factor_spin.value()
    phi_v  = self.dynamic_factor_spin.value()
    n_v    = self.n_load_plane_spin.value()
    Phi_u  = self.phi_load_spin.value()        # 0 = auto

    F_mean = F_max * (1 + R) / 2
    F_alt  = F_max * (1 - R) / 2

    # Auto Phi from stiffness
    if Phi_u < 0.001:
        Phi = self._cached_Phi if hasattr(self, '_cached_Phi') else 0.3
        phi_str = f"Φ (auto): {Phi:.3f}"
    else:
        Phi = Phi_u
        phi_str = f"Φ (user): {Phi:.3f}"

    Phi_eff = n_v * Phi
    F_K_min = self._get_preload() - (1 - Phi_eff) * F_max * phi_v

    self.R_derived_Fmean_label.setText(f"F_mean: {F_mean/1000:.2f} kN")
    self.R_derived_Falt_label.setText(f"F_alt:  {F_alt/1000:.2f} kN")
    self.R_derived_Phi_label.setText(phi_str)
    self.R_derived_FKmin_label.setText(f"F_K_min: {F_K_min/1000:.2f} kN")

    if F_K_min <= 0:
        self.R_separation_label.setText("⚠ SEPARATION at peak load!")
        self.R_separation_label.setStyleSheet(f"color: {Theme.RED}; font-weight: bold;")
    elif F_K_min < 0.1 * self._get_preload():
        self.R_separation_label.setText("⚠ Near separation — check R")
        self.R_separation_label.setStyleSheet(f"color: {Theme.YELLOW};")
    else:
        self.R_separation_label.setText("✓ No separation")
        self.R_separation_label.setStyleSheet(f"color: {Theme.GREEN};")
```

**Update `get_loading_data()` / `set_loading_data()`**:
```python
# get_loading_data — add to returned dict:
"R_factor":       self.R_factor_spin.value(),
"Phi_load":       self.phi_load_spin.value() or None,
"n_load_plane":   self.n_load_plane_spin.value(),
"dynamic_factor": self.dynamic_factor_spin.value(),
"load_waveform":  self.load_waveform_combo.currentData(),

# set_loading_data — add:
if "R_factor"       in data: self.R_factor_spin.setValue(data["R_factor"])
if "Phi_load"       in data and data["Phi_load"]: self.phi_load_spin.setValue(data["Phi_load"])
if "n_load_plane"   in data: self.n_load_plane_spin.setValue(data["n_load_plane"])
if "dynamic_factor" in data: self.dynamic_factor_spin.setValue(data["dynamic_factor"])
if "load_waveform"  in data:
    idx = self.load_waveform_combo.findData(data["load_waveform"])
    if idx >= 0: self.load_waveform_combo.setCurrentIndex(idx)
```

**Automatic Φ update from model stiffness** — in `MSDBuilderWindow.export_to_msd_model()` or `_on_msd_builder_model_changed()`:
```python
try:
    M, K, C = msd_model.assemble_matrices()
    k_diag = np.diag(K)
    k_sig = k_diag[k_diag > 1e3]
    if len(k_sig) >= 2:
        k_bolt_est   = 1.0 / (1.0 / k_sig[:len(k_sig)//2]).sum()
        k_member_est = 1.0 / (1.0 / k_sig[len(k_sig)//2:]).sum()
        Phi_auto = k_bolt_est / (k_bolt_est + k_member_est)
        self.inspector._cached_Phi = Phi_auto
        self.inspector._refresh_load_factor_labels()
except Exception:
    pass
```

---

## 6. Persistence Changes

`MSDModel.to_dict()` already serializes `global_loading` via `LoadingData.to_dict()`. Once the 5 new fields are added to `LoadingData`, they will serialize automatically.

**Backward compatibility in `LoadingData.from_dict()`**: the `cls(**{k:v ...})` pattern already handles missing keys by using dataclass defaults, so old `.msd` files will load cleanly with default values (R=0, Φ=None, n=0.5, φ=1.0, waveform="sinusoidal").

---

## 7. Integration into Reports

In `main_window._generate_report_html()`, add a "Load Factors" sub-section to the Loading section:

```html
<h3>Load Factors</h3>
<table>
  <tr><td>Load ratio R</td><td>{R_factor:.2f}</td></tr>
  <tr><td>Load type</td><td>{R_desc}</td></tr>
  <tr><td>F_mean</td><td>{F_mean/1000:.2f} kN</td></tr>
  <tr><td>F_alternating</td><td>{F_alt/1000:.2f} kN</td></tr>
  <tr><td>Load factor Φ</td><td>{Phi_load:.3f}</td></tr>
  <tr><td>Force applic. n</td><td>{n_load_plane:.2f}</td></tr>
  <tr><td>Φ_effective (n×Φ)</td><td>{Phi_eff:.3f}</td></tr>
  <tr><td>Dynamic factor φ</td><td>{dynamic_factor:.2f}</td></tr>
  <tr><td>Min clamp force F_K_min</td><td>{F_K_min/1000:.2f} kN</td></tr>
  <tr><td>Separation risk</td><td>{sep_status}</td></tr>
  <tr><td>Waveform</td><td>{load_waveform}</td></tr>
</table>
```

---

## 8. Implementation Sequence

Execute in this order to keep the app functional at every step:

### Step 1 — Data model only (0 risk)

- Add the 5 new fields to `LoadingData` in `element.py`
- Add `F_mean`, `F_alt`, `R` properties
- Update `to_dict()` / `from_dict()`
- **Test**: `python -c "from bolt_analysis_studio.core.models.element import LoadingData; d = LoadingData(); print(d.R_factor)"`

### Step 2 — GUI widgets (visual only)

- Add all new widgets + derived labels to `PropertyInspector` Loading > Global
- Wire `_refresh_load_factor_labels()`
- Update `get_loading_data()` / `set_loading_data()`
- **Test**: Open MSD Builder → Loading > Global → verify new fields appear and labels update

### Step 3 — Force function (time integration)

- Add `biased_harmonic_force()` to `time_integration.py`
- Update `TimeIntegrationConfig` with new fields
- Update `_run_time_integration()` to use new function
- **Test**: Run time integration with R=0 → verify mean component in displacement

### Step 4 — Loosening analyzer (coupled analysis)

- Update `LooseningAnalysisParams` with `R_factor`, `Phi_eff`, `dynamic_factor`
- Update `create_analyzer_from_msd_model()` extraction block
- Update cycle loop to use `F_N_bolt` / `F_K_min` as derived above
- **Test**: Run coupled loosening with R=−1 vs R=0, verify loosening rate differs

### Step 5 — Contact normal force (matrix level)

- Update `model.assemble_force_vector()` to use time-varying normal force
- Set `model._phi_eff` and `model._load_dof` in `export_to_msd_model()`
- **Test**: Matrix Viewer → Force tab → verify contact force oscillates with loading

### Step 6 — Auto Φ update + separation indicator

- Compute Φ_auto from k_bolt/k_member after matrix assembly
- Display in derived labels; show separation warning in red when F_K_min ≤ 0
- Add to Reports HTML

---

## 9. Standards References

| Symbol | Source | Clause | Description |
|--------|--------|--------|-------------|
| R = F_min/F_max | ISO 12107, ASTM E647 | — | Fatigue load ratio |
| Φ, Φ_K | VDI 2230 Part 1 (2015) | §5.2, Eq. 5.1 | Load factor (resilience ratio) |
| n | VDI 2230 Part 1 (2015) | §5.4, Eq. 5.4 | Force application factor |
| α_A (tightening) | VDI 2230 Part 1 (2015) | §5.4.3 | Preload scatter factor (already implemented) |
| φ (dynamic) | VDI 2230 Part 1 (2015) | §5.3.2 | Dynamic load factor |
| F_SA, F_KA | VDI 2230 Part 1 (2015) | §5.2, Eq. 5.3 | Alternating bolt force, clamp force change |
| σ_A = F_SA/A_s | VDI 2230 Part 1 (2015) | §5.6 | Bolt stress amplitude |
| Separation check | VDI 2230 Part 1 (2015) | §5.5, Eq. 5.14 | F_K_min > 0 required |
| Junker (DIN 65151) | DIN 65151 (2002) | §4, §5 | Transverse vibration loosening test |

---

## 10. Summary of New Parameters

| Parameter | Symbol | Dataclass field | Default | Range | GUI widget |
|-----------|--------|-----------------|---------|-------|------------|
| Load ratio | R | `R_factor` | 0.0 | −1 to 0.99 | `R_factor_spin` |
| Load factor | Φ | `Phi_load` | None (auto) | 0–1 | `phi_load_spin` (0=auto) |
| Force applic. | n | `n_load_plane` | 0.5 | 0–1 | `n_load_plane_spin` |
| Dynamic factor | φ | `dynamic_factor` | 1.0 | 1–3 | `dynamic_factor_spin` |
| Waveform | — | `load_waveform` | "sinusoidal" | enum | `load_waveform_combo` |
| Mean force | F_m | (derived) | — | — | `R_derived_Fmean_label` |
| Alternating force | F_a | (derived) | — | — | `R_derived_Falt_label` |
| Min clamp force | F_K_min | (derived) | — | — | `R_derived_FKmin_label` |
| Separation status | — | (derived) | — | — | `R_separation_label` |

---

## 11. Connection to Five-Stage Loosening Model

*Cross-reference: [LMQ §12] — Multi-Stage Loosening Phase Model*

The load factor variables in this document map directly to the phase transition boundaries:

### 11.1 F_K_min as the Phase Indicator

The minimum instantaneous clamp force:
```
F_K_min = F_preload − (1 − Φ_eff) × F_max × φ
```

maps to the loosening phase table as follows:

| F_K_min / F_p0 | Phase (from [LMQ §12.1]) | Solver Action |
|----------------|--------------------------|---------------|
| > 0.90 | STABLE | No loosening; only non-rotational mechanisms |
| 0.75 – 0.90 | NON-ROTATIONAL | Embedding + fretting active; log WARNING |
| 0.55 – 0.75 | TRANSITION | Localized slip possible; reduce time step |
| 0.20 – 0.55 | ROTATIONAL | Junker mechanism engaged |
| ≤ 0.20 | RUNAWAY | Immediate full loosening per cycle |
| ≤ 0 (separation) | SEPARATION | F_K_min = 0 overrides all → worst case |

The `R_separation_label` in the GUI must display RUNAWAY-level warning (red) when
F_K_min/F_p0 ≤ 0.55 — not only when separation (F_K_min ≤ 0) occurs.

### 11.2 Pai & Hess Corrected Slip Criterion

*Cross-reference: [LMQ §12.1]*

The classical slip condition used in §4.3 (`F_trans > µ × F_K_min`) overestimates the
required transverse force by 1.5–2×. The corrected slip onset from Pai & Hess (2002):

```python
# In CoupledLooseningAnalyzer._simulate_cycle() (see §5.5):
slip_onset_factor = getattr(self.params, 'slip_onset_factor', 0.46)
# 0.46 = conservative (lower bound from Pai & Hess)
# 0.66 = nominal
# 1.00 = classical Junker (over-optimistic)

slip_condition = F_ext_max > slip_onset_factor * self.params.mu_bearing * F_K_min
```

Add `slip_onset_factor` to `LooseningAnalysisParams` (default 0.46) and expose it as
a configurable parameter in the Loading > Global sub-tab.

### 11.3 Fretting Wear µ Degradation

*Cross-reference: [LMQ §11.3, §11.4]*

As µ degrades during long-term fretting, the effective slip threshold drops:
```
F_slip(N) = slip_onset_factor × µ(N) × F_K_min

µ(N) = µ₀ × (1 − wear_factor × min(N, N_sat) / N_sat)
where:
  wear_factor ≈ 0.20–0.40  (20–40% reduction)
  N_sat ≈ 5 000 cycles     (saturation cycle count)
```

The `CoupledLooseningAnalyzer` should update `params.mu_thread` and `params.mu_bearing`
each cycle using this degradation model. The self-locking condition [LMQ §11.4]:
```python
if np.tan(params.helix_angle_rad) >= params.mu_thread * np.cos(params.flank_angle_rad):
    # Self-locking condition violated → mark phase as ROTATIONAL, cannot recover
    state.phase = LooseningPhase.ROTATIONAL
    state.self_lock_lost = True
```

### 11.4 Loading-Type-Specific Φ_eff Adjustment

*Cross-reference: [LLC §2, §3, §4]*

| Loading type | Recommended n | Recommended Φ_eff source |
|-------------|--------------|--------------------------|
| Pure axial tension | n = 0 | Auto from k_bolt/k_member |
| Transverse Junker | n = 1 | Auto; Φ_eff = Φ (full transverse coupling) |
| Bending/eccentric | n = 0.5 | Auto; apply prying correction from [LLC §3.1] |
| Impact (single event) | n = 1, φ = 2.0 | Manual override; φ from impact severity |
| Combined service | n = 0.5 | Auto; check combined criterion from [LLC §5.1] |

For bending loading, the effective bearing area is non-uniform [LLC §3.1]; the slip
threshold reduction of 8–12% can be approximated by multiplying the slip_onset_factor by
`(1 − 0.10)` when the bending load introduces >10% bearing pressure asymmetry.
