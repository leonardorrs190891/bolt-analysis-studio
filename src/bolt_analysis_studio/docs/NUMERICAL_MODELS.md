# Bolt Analysis Studio v4.0 — Numerical Models Reference

**Source:** `Models/models/Part_VII_Friction_Models.md`, `Part_X_Preload_Loss_Models.md`, `Part_VIII_Numerical_Solvers.md`

---

## 1. Friction Models

Six friction models of increasing physical fidelity are implemented in `numerical/friction_models.py`, plus one viscous variant.

### 1.1 Overview

| Model | State Variables | Key Physics | Computational Cost |
|---|---|---|---|
| Regularized Coulomb | 0 | Static/kinetic transition, Stribeck (algebraic) | Very low |
| CoulombViscous | 0 | Coulomb + viscous drag (combined) | Very low |
| Dahl | 1 (F, force-based) | Pre-sliding stiffness, displacement hysteresis | Low |
| LuGre | 1 (z, bristle deflection) | Pre-sliding, Stribeck, friction lag, stick-slip | Medium |
| Bouc-Wen | 1 (z, hysteretic) | Smooth hysteresis, no explicit yield surface | Medium |
| Iwan (Segalman 4-param) | n (element states) | Microslip hysteresis, power-law energy dissipation | High |

### 1.2 Regularized Coulomb Model

The classical Coulomb model with smooth hyperbolic tangent regularization:

```
F_f = −[μ_k + (μ_s − μ_k)·exp(−|v|/v_trans)] · F_n · tanh(v/v_reg)
```

**Parameters:**
- μ_s = 0.15 (static friction coefficient)
- μ_k = 0.12 (kinetic friction coefficient)
- v_reg = 1×10⁻⁴ m/s (regularization velocity)
- v_trans = 0.01 m/s (Stribeck transition velocity)

**Rotational form (bearings, threads):**
```
T_f = −μ(ω) · F_n · r_eff · tanh(ω/ω_reg)    where ω_reg = v_reg / r_eff
```

**Use when:** Quick design calculations, parameter studies, short loosening estimates.

**Limitations:** No pre-sliding displacement, no friction memory, no hysteresis.

### 1.3 LuGre Dynamic Friction Model

Developed by Canudas de Wit, Olsson, Åström, Lischinsky (1995). Represents the contact as an ensemble of microscopic elastic "bristles."

**State equation (bristle deflection):**
```
dz/dt = v − (σ₀|v|/g(v)) · z
```

**Friction force:**
```
F = σ₀·z + σ₁·(dz/dt) + σ₂·v
```

**Stribeck function:**
```
g(v) = F_c + (F_s − F_c)·exp(−|v/v_s|^α)
```

**Parameters:**
- σ₀ = 10⁵ N/m (bristle stiffness — pre-sliding contact stiffness)
- σ₁ = 300 N·s/m (micro-damping — pre-sliding hysteresis)
- σ₂ = 0.1 N·s/m (viscous coefficient — lubricant drag)
- F_s = 100 N (max static friction force)
- F_c = 80 N (Coulomb friction force)
- v_s = 0.001 m/s (Stribeck velocity)
- α = 2.0 (Stribeck exponent)

**Steady-state (constant velocity):**
```
z_ss = g(v)/σ₀ · sign(v)
F_ss(v) = g(v)·sign(v) + σ₂·v    ← Standard Stribeck curve
```

**Numerical integration (implicit Euler for stability):**
```
z^(n+1) = (z^n + Δt·v^(n+1)) / (1 + Δt·σ₀·|v^(n+1)|/g(v^(n+1)))
```

**Key phenomena captured:**
1. Pre-sliding displacement (~1–10 μm at thread/bearing interfaces)
2. Stick-slip transitions (smooth, no chattering)
3. Friction lag (hysteresis at velocity reversals)
4. Variable break-away force
5. Stribeck velocity-weakening effect

**Use when:** High-fidelity loosening simulations, stick-slip transition analysis, lubrication effects.

### 1.4 Dahl Friction Model

Introduced by P.R. Dahl (1968). Rate-independent — friction depends on displacement, not velocity.

**State equation:**
```
dF/dx = σ·(1 − F/F_c·sign(v))^α
```

**Parameters:**
- σ = 10⁵ N/m (contact stiffness)
- F_c = 100 N (Coulomb friction)
- α = 1.0 (shape exponent; 1/3 for Mindlin Hertzian contact)

**Analytical solution (constant velocity, α=1):**
```
F(x) = F_c·(1 − exp(−σx/F_c))
```

**Pre-sliding displacement:** x_ps = F_c/σ

**Relationship to LuGre:** Dahl = LuGre with σ₁=0, σ₂=0, g(v)=F_c (no Stribeck, no damping).

**Energy dissipation per cycle:** W_d ∝ x_amp^(2+1/α)
For α=1: W_d ∝ x_amp³ (matches Mindlin partial-slip theory).

**Use when:** Low-velocity applications, pre-sliding displacement analysis, quasi-static loading.

### 1.5 Iwan Distributed Element Model (Segalman 4-Parameter)

Represents friction as n parallel Jenkins elements (spring + ideal Coulomb slider), each with critical slip force φ_i.

**Density of slip forces (power-law distribution):**
```
ρ(φ) = R·χ·φ^(χ−1) / F_s^(χ+1)
```

**Backbone curve:**
```
F(u) = K_T·u·[1 − 1/(χ+2)·(K_T·u/F_s)^(χ+2)]    for K_T·|u| < F_s
F(u) = F_s·sign(u)                                   for K_T·|u| ≥ F_s
```

**Energy dissipation per cycle (power law — the defining feature):**
```
W_d ∝ F_amp^β    where β = χ + 3
```

For bolted joints: β = 2.5–3.0 (χ = −0.5 to 0.0)

**Parameters:**
- K_T = 10⁶ N/m (initial tangent stiffness)
- F_s = 100 N (critical macroslip force)
- χ = 0.5 (power-law exponent; BAS default)
- R = 1.0 (density normalization)
- n = 50 elements (discretization)

**Use when:** Modal analysis (joint damping), microslip studies, when energy dissipation exponent measured experimentally.

### 1.6 Bouc-Wen Hysteretic Friction Model

Introduced by Bouc (1967), extended by Wen (1976). Represents smooth hysteresis without an explicit yield criterion.

**State equation (hysteretic variable z):**
```
dz/dt = A·v − β·|v|·|z|^(n−1)·z − γ·v·|z|^n
```

**Friction force:**
```
F = α·k·z + c·v
```

**Parameters:**
- A = 1.0 (controls pre-yield stiffness)
- β = 0.5 (controls shape of hysteresis loop — softening)
- γ = 0.5 (controls pinching / strength degradation)
- n = 1.0 (shape exponent — n=1 → bilinear, n→∞ → elasto-plastic)
- α = 0.6 (ratio of post-yield to pre-yield stiffness)
- k = 1×10⁵ N/m (elastic stiffness)
- c = 50 N·s/m (viscous damping)

**Properties:**
- Smooth force-displacement relationship (no discontinuities)
- Captures pinching, strength degradation, stiffness degradation through A, β, γ
- z is bounded: |z|_max = (A/(β+γ))^(1/n)
- Special cases: β=γ=1/2, n=1 → bilinear; n→∞ → ideal elasto-plastic

**Use when:** Soft contact interfaces, polymer/composite fasteners, smooth hysteresis required without an explicit slip threshold.

### 1.7 Three-Phase Friction Evolution Model

Based on fretting experiments of Hintikka et al. (2019, 2020). Captures cycle-dependent evolution of μ over 10³–10⁶ cycles.

**Complete equation:**
```
μ(N) = μ₀ + (μ_peak−μ₀)·(1−e^(−N/N₁))·e^(−N/N₂)   ← Phase I: running-in peak
              + (μ_ss−μ₀)·(1−e^(−N/N₃))               ← Phase II: stabilization
```

**Long-term degradation (N > N_critical):**
```
μ(N) = μ_base(N) + β_degrade·ln(N/N_critical)
```

**Default parameters:**
| Parameter | Default | Physical Meaning |
|---|---|---|
| μ₀ | 0.14 | As-installed (with coating/lubricant) |
| μ_peak | 0.18 | Maximum during running-in (~N₁ cycles) |
| μ_ss | 0.12 | Long-term steady-state |
| N₁ | 50 | Running-in rise rate (cycles) |
| N₂ | 500 | Peak decay rate (cycles) |
| N₃ | 5000 | Stabilization approach rate (cycles) |
| β_degrade | 0.01 | Long-term drift magnitude |
| N_critical | 10⁵ | Phase III onset |

**Three phases:**
- **Phase I (0–N₁):** Running-in — asperity truncation, coating breakthrough → μ rises
- **Phase II (N₁–N_critical):** Oxide debris forms, surface polishes → μ decays to μ_ss
- **Phase III (N > N_critical):** Fatigue, fretting damage, lubricant depletion → slow drift

**Coupling with instantaneous models:**
```
F_c(N) = μ(N)·F_n         # Updates LuGre F_c each cycle
F_s(N) = (μ_s/μ_k)·μ(N)·F_n  # Updates LuGre F_s each cycle
```

**Use when:** Long-duration simulations (>1000 cycles), coated fasteners, loosening life prediction.

### 1.8 Friction Model Selection Guide

| Scenario | Recommended | Reason |
|---|---|---|
| Quick design check (<1000 cycles) | Regularized Coulomb | Fast, adequate |
| Junker test simulation (<10k cycles) | LuGre + Three-Phase | Within-cycle + evolution |
| Long-term service (>10⁵ cycles) | Three-Phase + Coupled | Evolution dominates |
| Modal/frequency response | Iwan | Correct energy dissipation exponent |
| Pre-sliding / microslip | Dahl or Iwan | Displacement-based hysteresis |
| High-fidelity stick-slip | LuGre | Rate-dependent state + Stribeck |
| Soft/polymer interfaces | Bouc-Wen | Smooth hysteresis, no discontinuities |

---

## 2. Preload Loss Models

Implemented in `numerical/preload_loss_models.py`. 9 models are fully implemented (SingleExponential, DoubleExponential, StretchedExponential, Logarithmic, VDI2230Embedding, NortonBaileyCreep, PowerLaw, JiangTwoStage, CombinedMechanism); the reference framework (Part X) documents 15 models for future implementation.

**Total preload evolution:**
```
F_p(N) = F_p0 − ΔF_embed(N) − ΔF_creep(t) − ΔF_relax(t,T)
                − ΔF_wear(N) − ΔF_thermal(ΔT) − ΔF_rot(N)
```

**System stiffness (VDI 2230):**
```
k_sys = k_b·k_m / (k_b + k_m)

All non-rotational losses: ΔF_i = k_sys · δ_i
```

### 2.1 Single Exponential Decay

```
F(N) = F_∞ + (F₀ − F_∞)·exp(−λN)
```

| Parameter | Symbol | Typical Range |
|---|---|---|
| Decay rate | λ | 0.001–0.01 cycles⁻¹ |
| Residual ratio | F_∞/F₀ | 0.60–0.85 |
| Half-life | N₁/₂ = ln2/λ | 70–700 cycles |

**Use:** First approximation, single-mechanism dominance.

### 2.2 Double Exponential Decay

```
F(N) = F_∞ + A₁·exp(−λ₁N) + A₂·exp(−λ₂N)    (A₁+A₂+F_∞ = F₀)
```

- Fast component (λ₁ = 0.01–0.10): embedding, gasket seating, initial thread settling
- Slow component (λ₂ = 0.001–0.01): wear, thread slip accumulation, creep

**Use:** When experimental data show clear "knee" separating two decay regimes.

### 2.3 Stretched Exponential (KWW Model)

```
F(N) = F_∞ + (F₀ − F_∞)·exp(−(λN)^β)    0 < β < 1
```

β = 1 → standard exponential; β < 1 → distributed relaxation times (multiple interfaces).

### 2.4 Logarithmic Decay Model

Simple logarithmic decay — accurate for embedding-dominated early-stage loss:

```
F(N) = max(F_residual, F₀ − k_log·ln(N+1))
```

| Parameter | Symbol | Typical Range |
|---|---|---|
| Decay rate | k_log | 0.01–0.10 × F₀ per decade |
| Residual preload | F_residual | 0.50–0.80 × F₀ |

**Linearization:** In log(N) space, the model is linear — useful for extrapolation from short-duration tests to service life.

**Use:** Embedding-dominated scenarios (rough surfaces, few cycles), quick upper-bound estimate.

### 2.6 VDI 2230 Embedding Loss Model

Standards-based settling from VDI 2230 §R₃:

```
ΔF_embed = k_sys · f_z · L · (1 − exp(−N/N_c))
```

Where f_z is the embedding depth per surface pair (μm), L is the number of contact interfaces, N_c is the characteristic settling cycle count (~100 cycles).

Surface roughness effect: f_z = 2.0–6.5 μm (smooth) to 6.5–12.5 μm (rough)

### 2.7 Norton-Bailey Creep Relaxation (High Temperature)

```
ε_cr(t) = A·σⁿ·t^m    (Norton-Bailey power law)
ΔF_relax(t) = k_sys · L_bolt · A · (F₀/A_t)ⁿ · t^m
```

Applicable for T > 300°C (creep-dominated relaxation).

### 2.8 Power-Law Model (Lu et al., 2024)

Only 2 parameters, >85% fitting accuracy on M8 parametric data:

```
F(N)/F₀ = a · N^(−b)    or equivalently    F(N) = F₀ · (N/N_ref)^(−b)
```

**M8 calibration data (Lu 2024):**

| Sub-case | F₀ (N) | δ (mm) | f (Hz) | F_final/F₀ |
|---|---|---|---|---|
| Baseline | 11,567 | 1.0 | 1 | 0.064 |
| Low preload | 2,105 | 1.0 | 1 | 0.037 |
| High preload | 15,027 | 1.0 | 1 | 0.234 |
| Small amplitude | 11,567 | 0.25 | 1 | 0.795 |
| Large amplitude | 11,567 | 2.0 | 1 | 0.004 |

### 2.9 Jiang Two-Stage Model

From Jiang, Zhang, Lee (2003). Separates loosening into:

**Stage I — Non-rotational (N < N_trans):** Plastic micro-deformation at thread roots and under head:
```
F(N)/F₀ = 1 − η_max·(1 − exp(−λ_stage1·N))
```

**Stage II — Rotational (N > N_trans):** Nut back-off per cycle (angular increment × helix):
```
dF/dN = −k_bolt · (p/2π) · (dθ/dN)_loosening
```

**M12 calibration data (Jiang 2003):**
- Glued nut (Stage I only): 34% loss in 200 cycles at δ=0.46mm, f=5Hz, μ=0.15, F₀=25kN
- Free nut: 92% loss in 250 cycles at same conditions

### 2.10 Combined Mechanism Model

Superposition of all active mechanisms:

```
F_p(N) = F₀ · [1 − f_embed(N) − f_wear(N) − f_rot(N) − f_creep(t) − f_thermal(ΔT)]
```

Physical bounds enforced: F_p ≥ 0

---

## 3. Self-Loosening Models

### 3.1 Junker Mechanism (Torque Balance)

**Pitch torque (DRIVES loosening — pure geometry):**
```
T_pitch = F_p · p/(2π)
```

**Thread friction torque (RESISTS loosening):**
```
T_thread = μ_t · F_p · d₂ / (2·cos α)    (α = 30° for metric threads)
```

**Bearing friction torque (RESISTS loosening):**
```
T_bearing = μ_b · F_p · r_eff
r_eff = (2/3) · (r_o³ − r_i³) / (r_o² − r_i²)    (annular contact centroid)
```

**Loosening condition:**
```
T_pitch > T_thread + T_bearing
⟹ F_p cancels ⟹ condition is purely geometric + friction:
p/(2π) > μ_t·d₂/(2cosα) + μ_b·r_eff
```

**Critical friction coefficient (μ_t = μ_b = μ):**
```
μ_crit = p·cos(α) / (π·d₂ + 2π·r_eff·cos(α))
```

For M16 (p=2mm, d₂=14.701mm): μ_crit ≈ 0.024 → always stable under static loading.
Under transverse vibration, effective friction drops momentarily → loosening occurs.

**Torque margin (BAS metric):**
```
TM = (T_thread + T_bearing) / T_pitch    (>1.0 = stable)
```

### 3.2 Pai-Hess Slip Regimes

Four regimes classified by slip state at both bearing surfaces:

| Regime | Head | Nut | Loosening? |
|---|---|---|---|
| 1 | STICK | STICK | No |
| 2 | SLIP | STICK | Partial (head-end only) |
| 3 | STICK | SLIP | Partial (nut-end only) |
| 4 | SLIP | SLIP | Full (classical Junker) |

Even Regime 2 or 3 produces loosening due to bolt torsional compliance.

### 3.3 Nassar-Yang Model

Closed-form loosening rate for transverse vibration:

```
dθ/dN = C_loosening · (F_trans/F_p − μ_crit/μ)² · f(geometry)
```

where C_loosening is the calibration parameter (currently 0.3, needs calibration against experimental data per M8 plan).

---

## 4. Time Integration Methods

Six integrators plus one Newton-Raphson variant implemented in `numerical/time_integration.py`. All have `solve_with_contacts()` signature.

### 4.1 Method Overview

| Method | β | γ | Stability | Accuracy | Best For |
|---|---|---|---|---|---|
| Newmark-β (constant average) | 0.25 | 0.5 | Unconditionally stable | 2nd order | Standard problems |
| Newmark-β (linear accel) | 1/6 | 0.5 | Conditionally stable | 2nd order | Smooth loads |
| NonlinearNewmark (Newton-Raphson) | 0.25 | 0.5 | Unconditionally stable | 2nd order | Strongly nonlinear contacts |
| HHT-α | — | — | Unconditionally stable | 2nd order | High-frequency damping |
| Central Difference | 0 | 0.5 | Conditionally stable | 2nd order | Wave propagation |
| Modal Superposition | — | — | Unconditionally stable | Mode-dependent | Linear systems |
| Runge-Kutta 4 (RK4) | — | — | Conditionally stable | 4th order | Smooth ODEs |
| Adaptive RK45 (Dormand-Prince) | — | — | Explicit, adaptive Δt | 4th/5th order | Multi-scale problems |

### 4.2 Newmark-β Algorithm

**Predictor:**
```
{ũ}_(n+1) = {u}_n + Δt{u̇}_n + (0.5−β)Δt²{ü}_n
{ṽ}_(n+1) = {u̇}_n + (1−γ)Δt{ü}_n
```

**Effective stiffness:**
```
[K_eff] = [K] + γ/(β·Δt)·[C] + 1/(β·Δt²)·[M]
```

**Solve:**
```
[K_eff]{u}_(n+1) = {F_eff}
```

**Corrector:**
```
{ü}_(n+1) = ({u}_(n+1) − {ũ}_(n+1)) / (β·Δt²)
{u̇}_(n+1) = {ṽ}_(n+1) + γ·Δt·{ü}_(n+1)
```

### 4.3 NonlinearNewmark (Newton-Raphson Iteration)

Extends standard Newmark-β to handle nonlinear restoring forces (contacts with large preload changes, gasket nonlinearity).

**Predictor (same as linear Newmark):**
```
{ũ}_(n+1) = {u}_n + Δt{u̇}_n + (0.5−β)Δt²{ü}_n
{ṽ}_(n+1) = {u̇}_n + (1−γ)Δt{ü}_n
```

**Newton-Raphson loop:**
```
Residual:   R(u) = M·a(u) + f_int(u, v) − F_ext
Jacobian:   J = ∂R/∂u ≈ M/(βΔt²) + C·γ/(βΔt) + K_T
Increment:  du = −J⁻¹·R
Update:     u_new += α·du    (line search with step α ≤ 1)
```

**Convergence criteria (configurable):**
- Force: |R| / |F_ext| < ε_F = 1×10⁻⁶
- Displacement: |du| / |u| < ε_u = 1×10⁻⁸
- Energy: du·R < ε_E = 1×10⁻¹²

**Use when:** Gasket contacts (nonlinear k(δ)), large preload changes per step, strongly coupled friction-preload evolution.

### 4.4 HHT-α (Hilber-Hughes-Taylor)

Extends Newmark with numerical damping for high-frequency modes (α = −1/3 to 0):

```
[M]{ü}_(n+1) + (1+α)[C]{u̇}_(n+1) − α[C]{u̇}_n
            + (1+α)[K]{u}_(n+1) − α[K]{u}_n = {F}_(n+1+α)
```

Recommended when high-frequency modes cause spurious oscillations.

### 4.5 solve_with_contacts() Signature

```python
def solve_with_contacts(
    self,
    time_params: TimeParams,
    F_ext_func: Callable,
    contacts: List[Contact],
    preload: float,
    u0: np.ndarray,
    v0: np.ndarray
) -> IntegrationResult:
    ...
```

Contact states are updated at each time step via `contact.update_state(x, v, dt, preload)`.

### 4.6 Automatic Time Step Selection

For loosening analysis, BAS auto-selects dt based on:
```
dt_auto = min(T_period/20, 1/f_nyquist, t_settling/100)
```

Recommended frequency ranges:
- 0–10 Hz: dt = 0.005 s
- 10–100 Hz: dt = 0.001 s
- 100+ Hz: dt = 0.0002 s

---

## 5. Coupled Loosening Analysis

Implemented in `numerical/coupled_loosening_analyzer.py`.

### 5.1 FrictionEvolutionParams

```python
@dataclass
class FrictionEvolutionParams:
    model: str = "three_phase"      # "constant", "exponential", "three_phase"
    mu_initial: float = 0.15        # As-installed
    mu_peak: float = 0.18           # Running-in maximum
    mu_steady: float = 0.10         # Long-term steady state
    mu_minimum: float = 0.03        # Absolute floor (never goes below)
    N_phase1: int = 50              # Running-in duration
    N_phase2: int = 500             # Peak-to-steady transition

    # M9 feature — separate thread and bearing friction
    mu_thread_initial: Optional[float] = None   # Overrides mu_initial for threads
    mu_bearing_initial: Optional[float] = None  # Overrides mu_initial for bearings
```

### 5.2 Friction Extraction Hierarchy

When creating analyzer from MSD model, friction is extracted with 5-level fallback:

1. Explicit `mu_initial` parameter passed to `create_analyzer_from_msd_model()`
2. `model.global_loading.mu_initial` if > 0
3. `model.mu_initial` field
4. Average of `contact.friction.mu_static` across all contacts
5. Default = 0.12

### 5.3 WearModelParams and WearEvolutionModel

```python
@dataclass
class WearModelParams:
    model: str = "archard"          # "archard", "energy", "fretting"
    K_wear: float = 1e-7            # Archard wear coefficient (free calibration param)
    H_surface: float = 2500e6      # Surface hardness [Pa]
    fretting_threshold: float = 50e-6  # Slip amplitude below which fretting dominates [m]
```

**`WearEvolutionModel` — Stiffness Degradation**

Tracks cumulative wear depth h(N) and the resulting joint stiffness degradation:

**Archard wear accumulation:**
```
h(N) = K_wear × p_contact × s_sliding / H_surface
```

**Stiffness degradation (hyperbolic):**
```
k(N) = k₀ / (1 + γ_stiff × h(N))
```

Where γ_stiff = stiffness sensitivity to wear depth (m⁻¹).

**Preload loss from wear:**
```
F_p(N) = F_p0 × k(N) / k₀    (proportional to stiffness ratio)
```

**Running-in phase (nonlinear acceleration):**
```
dh/dN = K_wear × p × v × (1 + A_runin × exp(−N/N_runin))
```

where A_runin and N_runin capture the elevated wear rate during initial surface conforming.

**Energy-based wear** (Fouvry model):
```
h = α_fouvry × E_dissipated = α_fouvry × ∫ F_friction × δ_slip dt
```

Useful when friction force and slip amplitude are tracked directly from time integration.

### 5.4 Results Structure

`CoupledLooseningResult` stores:
- `preload_vs_cycles`: np.ndarray (N, F/F₀)
- `loosening_angle_vs_cycles`: np.ndarray (N, θ radians)
- `friction_vs_cycles`: np.ndarray (N, μ)
- `wear_vs_cycles`: np.ndarray (N, h wear depth)
- `_raw_loosening_results`: raw `LooseningResults` object (for `CoupledLooseningResultsPlotter`)
- `loosening_rate`: float cycles⁻¹
- `cycles_to_50pct_loss`: int

---

## 6. Preload Loss Mechanisms Summary Table

| Mechanism | Time Scale | Typical Loss | Model Implemented |
|---|---|---|---|
| Embedding (surface settling) | First 10–200 cycles | 5–15% of F₀ | VDI 2230 + exponential |
| Gasket creep | Hours to months | 10–40% | Logarithmic + Norton-Bailey |
| Bolt stress relaxation | Hours to years | 5–30% | Norton-Bailey |
| Thread wear | Thousands of cycles | 2–10% | Archard |
| Differential thermal expansion | Temperature change | ±20–30% | Linear thermal model |
| Cyclic plastic strain | Hundreds of cycles | 5–20% | Jiang Stage I |
| Rotational loosening (Junker) | Instantaneous when slip | Up to 100% | Jiang Stage II + Nassar-Yang |

---

*Source files: `numerical/preload_loss_models.py`, `numerical/friction_models.py`, `numerical/time_integration.py`, `numerical/coupled_loosening_analyzer.py`*

*Reference: Models/models/Part_VII_Friction_Models.md, Part_X_Preload_Loss_Models.md, Part_VIII_Numerical_Solvers.md*
