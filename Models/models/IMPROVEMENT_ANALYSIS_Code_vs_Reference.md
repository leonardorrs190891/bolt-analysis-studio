# Improvement Analysis: Code Implementation vs. Reference Models

## Overview

This document compares the Bolt Analysis Studio (BAS) source code against the reference mathematical formulations in `BAS/Models/models/` (Parts I–XII) to identify bugs, gaps, inconsistencies, and improvement opportunities. Findings are categorized by severity.

---

## CRITICAL — Bugs That Produce Wrong Results

### C1. Distributed Thread Stiffness Formula Is Wrong
**File**: `element.py`, `create_distributed_thread()` lines 1771–1776
**Reference**: Part III, Section 11.2 (thread stiffness as parallel-of-series)

The formula has an extraneous `n_segments` multiplier and inverted division:
```python
# Current (WRONG):
k_base = n_segments * k_total / inv_factor_sum

# Correct:
k_base = k_total * inv_factor_sum
```

For series springs: `1/k_total = Σ(1/(φᵢ × k_base))`, solving for k_base gives `k_base = k_total × Σ(1/φᵢ)`. The code multiplies by `n_segments` and divides instead of multiplying. This means the distributed thread model gives **incorrect equivalent stiffness** — the series combination won't match the monolithic thread stiffness.

**Impact**: Any analysis using per-thread load distribution (Yamamoto, exponential, power law) will have wrong thread stiffness.

---

### C2. Head Stiffness Inconsistency (0.4 vs 0.5)
**Files**: `element.py` line 1094 uses `k = 0.4*E*d`; `model.py` line 100 uses `k = 0.5*E*d`
**Reference**: Part III cites VDI 2230: `δ_head = 0.5d/(E·d)` → `k_head = 2·E·d` per unit... actual VDI formula: `k_head = E·d·π/(2·ln5)` ≈ `0.5·E·d`

Two files compute head stiffness with different multipliers. The `0.5` in `model.py` is closer to VDI 2230. The `0.4` in `element.py` is 20% lower.

**Impact**: Bolt stiffness and therefore stiffness ratio Φ will differ depending on which code path is used.

**Fix**: Standardize on `0.5*E*d` per VDI 2230 in both files.

---

### C3. Stress Area Uses Wrong Diameter (d₃ vs d₁)
**Files**: `element.py` line 703 uses `d₃ = d - 1.2268p` (root diameter); `preload_loss_models.py` line 94 uses `d₃ = d - 1.0825p` (minor diameter d₁)
**Reference**: ISO 898-1 defines stress area as `Aₜ = π/4 × ((d₂+d₁)/2)²` where `d₁ = d - 1.0825p`

The element module uses the **root diameter d₃** instead of the **minor diameter d₁**. d₃ < d₁ always, so `element.py` computes a smaller (more conservative) stress area than the ISO standard. For M12×1.75: d₁ = 9.853mm, d₃ = 9.706mm — a 1.5% error in diameter → ~3% error in Aₜ.

**Impact**: Preload utilization ratios, yield percentages, and stiffness calculations will be slightly inconsistent between modules.

**Fix**: Use `d₁ = d - 1.0825p` consistently per ISO 898-1.

---

### C4. Iwan Friction Model Returns Zero
**File**: `friction_models.py`, `IwanFriction` class, lines 376–410

The `element_states` array is initialized to zeros and **never updated**. The force calculation `F_i = k_i * element_states[i]` therefore always returns zero. The Iwan model (Segalman 4-parameter, 50 Jenkins elements) is completely non-functional.

**Impact**: Anyone selecting the Iwan friction model gets zero friction force — incorrect results with no warning.

**Fix**: Implement state update in `integrate_state()` that evolves each Jenkins element based on displacement history.

---

### C5. Contact System Not Wired Into Solver
**Files**: `model.py` `assemble_matrices()`, `time_integration.py` solvers
**Reference**: Part III Section 11.3 explicitly shows contacts contributing to [K]; Part XI Section 45 shows force vector assembly from contacts

The reference documents describe a system where:
1. Contacts contribute to [K] and [C] via `get_stiffness_contribution()` / `get_damping_contribution()`
2. Contacts contribute tribological forces to {F} via `get_force_contribution()`
3. Contact states are updated each time step via `update_state()`

**None of this is connected in the code**:
- `assemble_matrices()` uses only element-based assembly, not contacts
- Time integrators don't call `get_force_contribution()` on contacts
- No solver calls `update_state()` on contacts

The contact classes (ThreadContact, BearingContact, GasketContact, etc.) are architecturally complete but produce **no effect on any analysis**.

**Impact**: The entire contact system (helix coupling, per-thread analysis, gasket nonlinearity, bearing friction) is dead code. All loosening predictions come solely from the `CoupledLooseningAnalyzer` which has its own independent models.

---

## HIGH — Significant Methodology Gaps

### H1. HHT Contact Solver Evaluates Tribological Force at Wrong State
**File**: `time_integration.py` lines 721–722

Both `F_trib_i` and `F_trib_ip1` use `U[i], V[i]` — they are identical. The force at t_{n+1} should use the predicted state (U_pred, V_pred). This reduces the HHT scheme from 2nd-order to effectively 1st-order for nonlinear contact problems.

### H2. Preload Loss Uses Trace of K as System Stiffness
**File**: `time_integration.py` line 520

`k_sys = np.sum(np.diag(self.K))` takes the trace (sum of diagonal entries). For a tridiagonal stiffness matrix, this is NOT the equivalent series stiffness. The correct formula is:
```
k_sys = k_bolt × k_member / (k_bolt + k_member)
```
The trace can be 5–10× larger than the actual system stiffness, causing underestimation of preload loss.

### H3. CoupledLooseningAnalyzer Is Disconnected from Contact Objects
**Reference**: Part XI describes a framework using Contact objects for friction/wear/loosening
**Code**: `CoupledLooseningAnalyzer` has its own `FrictionEvolutionParams` and `WearModelParams` completely independent of the contact system

The analyzer duplicates the contact system's models with different implementations:
- Friction evolution formula differs from `FrictionData.get_friction_evolution()` in `element.py`
- Wear model differs from `WearModel` in `friction_models.py`
- Thread/bearing friction are treated as equal (should be separate)

### H4. No Thermal Expansion Preload Loss
**Reference**: Part IV defines `ΔF_thermal = k_sys × L × ΔT × (α_member - α_bolt)` as a key mechanism
**Code**: `CoupledLooseningAnalyzer` only uses temperature for friction/hardness degradation

For dissimilar-material joints (e.g., SS bolt in aluminum — Paper 31), thermal expansion mismatch is the **dominant** preload loss mechanism. The code computes `ThermalEffectsModel` in `preload_loss_models.py` but this model is never integrated into the coupled analyzer.

### H5. Matrix Assembly Doesn't Reassemble During Integration
**File**: `time_integration.py`, `solve_with_contacts()` on Newmark and HHT

Comment says "For now, we use constant matrices." The K_eff_lu factorization is done once. This means:
- Gasket nonlinear stiffness k(δ) is never updated
- Preload-dependent contact stiffness is frozen
- Any state-dependent stiffness change is ignored

For nonlinear problems (gaskets, elastoplastic contacts), this is incorrect.

### H6. Stretched Exponential and Logarithmic Models Decay to Zero
**File**: `preload_loss_models.py`

The stretched exponential `F = F₀·exp(-(N/N₀)^β)` and logarithmic `F = F₀ - k·ln(N+1)` models both predict complete preload loss at large N. Real joints always retain some residual preload unless the bolt physically separates. These models need a floor/residual parameter like the single/double exponential models have.

### H7. Missing Bouc-Wen and Coulomb-Viscous Friction Models
**File**: `friction_models.py`

`FrictionModelType` enum includes BOUC_WEN and COULOMB_VISCOUS but no corresponding classes exist. The factory function raises ValueError for these types.

---

## MEDIUM — Methodology Improvements

### M1. K-Factor (Nut Factor) Oversimplified
**File**: `preload_loss_models.py` line 123
**Reference**: Part IV gives full VDI 2230 expression

Current: `K = 0.16 + 0.5×μ_total` (linear approximation)
VDI 2230: `K = (d₂/2d)×[p/(πd₂) + μₜ/cos(α)] + μ_b×D_km/(2d)`

The simplified formula gives K=0.22 at μ=0.12; VDI gives K=0.18 — a 22% error that propagates to all torque-preload calculations.

### M2. Modal Analysis Uses `eig` Instead of `eigh`
**File**: `model.py` lines 706, 738

Since M and K are symmetric positive definite, `scipy.linalg.eigh(K, M)` is:
- More numerically stable (guaranteed real eigenvalues)
- ~2× faster
- Eliminates the need to filter complex eigenvalues

### M3. Central Difference Uses Force at Wrong Time Step
**File**: `time_integration.py` line 871

Uses `F[i]` (current time) but central difference formulation requires `F[i+1]` (next time) for the effective force. The computed `F[i+1]` is never used. This introduces a one-step time lag in the forcing.

### M4. NonlinearNewmark Convergence Checks Total Displacement
**File**: `time_integration.py` line 1284

`norm_du = np.linalg.norm(u_new - U[i])` checks total displacement from step start, not the Newton iteration increment. Should check `np.linalg.norm(du)`. This means convergence is declared when the total step is small, not when the iteration has converged.

### M5. Pi5 (Joint Constant) Hardcoded in Similitude
**File**: `similitude.py`

Both prototype and model Joint Constant (Φ = k_b/(k_b+k_m)) are hardcoded at 0.22. Should be computed from actual bolt/member stiffness provided by the user. This defeats the purpose of checking Pi-group preservation.

### M6. Material Dissimilarity Not Handled in Scaling
**File**: `similitude.py`

`MaterialSimilarity.SIMILAR` and `DIFFERENT` modes produce the same `ScaleFactors` as `SAME` — the E_ratio and rho_ratio in the constructor always default to 1.0. The reference (Part IX) specifies distinct scaling for different materials.

### M7. Loading Pattern Ignored in Multi-Bolt Reduction
**File**: `loosening_similitude.py`

`LoadingPattern` enum (UNIFORM, MOMENT, COMBINED, SHEAR) exists but `reduce_multi_bolt_to_single()` always does uniform reduction regardless. For wind turbine flanges under bending, the most-loaded bolt sees ~1.5–2× the average — this should be captured.

### M8. Loosening Coefficient Not Parameterizable
**File**: `coupled_loosening_analyzer.py`

`C_loosening = 0.3` is hardcoded. The reference (Part XI, Section 40) states this should be calibrated to specific Junker test data. It should be a parameter in `TwoStageLooseningParams`.

### M9. Thread and Bearing Friction Assumed Equal
**File**: `coupled_loosening_analyzer.py`

Both surfaces use the same friction evolution model with the same parameters. The reference (Part VII, Parts V Section 26) explicitly treats them separately: thread friction has the flank angle amplification factor (sec α) and different contact pressure from bearing friction.

### M10. LuGre State Not Integrated Properly
**File**: `friction_models.py`

`LuGre.friction_force()` does not update `self.z` (bristle state). The state is only updated by separate `integrate_state()` calls that nothing in the calling code ensures happen. The `friction_coefficient()` method assumes a fixed 1000 N normal force for normalization.

### M11. Wear Accumulation Bug
**File**: `friction_models.py`, `WearEvolutionModel`

Each call to `wear_rate_per_cycle()` also adds to `self.accumulated_wear` inside `archard_wear_depth()`. Calling `stiffness_evolution()` for the same cycle array double-counts wear.

### M12. Energy Dissipation Quarter-Cycle vs Full-Cycle
**File**: `friction_models.py` vs `preload_loss_models.py`

Fouvry energy wear in `friction_models.py` line 612 uses `E = F×δ` (one quarter-cycle). The `EnergyDissipationModel` in `preload_loss_models.py` correctly uses `E = 4×μ×N×δ`. These should be consistent.

---

## LOW — Refinements and Best Practices

### L1. `apply_rayleigh_damping()` Sets Dirty Flag Incorrectly
**File**: `model.py` lines 674–675

Sets `_is_dirty = False` after modifying only `_C`, but `_M` and `_K` from the previous assembly call are cached. Next `assemble_matrices()` returns stale M/K with new C.

### L2. Determinant-Based Validation Can Overflow
**File**: `model.py` lines 983, 1023

`det(M)` and `det(K)` can overflow for large systems. Use condition number or rank checks instead.

### L3. MaterialGrade Enum Is Just a Label
**File**: `element.py`

Setting `grade = MaterialGrade.A320_L7` does NOT populate E, Sy, Su — they remain at defaults (A193 B7 values). Need a lookup table from grade to properties.

### L4. ThreadContact Hardcoded Inertia and Time Step
**File**: `thread_contact.py`

`J_nut = 1e-4` kg·m² and `dt = 0.0001` s are placeholders in `get_force_contribution()`. These should come from the model and time integration parameters.

### L5. No Adaptive Time Stepping
**Reference**: Part VIII discusses adaptive stepping for contact problems
**Code**: All 5 integrators use fixed dt

For stick-slip transitions, fixed dt can miss events (too large) or waste computation (too small). At minimum, the critical dt for central difference should be enforced.

### L6. Duplicate Friction Evolution Implementations
**Files**: `element.py` `FrictionData.get_friction_evolution()` and `friction_models.py` `FrictionEvolutionModel.friction_coefficient()`

Two implementations of the same 3-phase Hintikka model with **different formulations** that produce different results. Should be unified.

### L7. Random Force Uses Only 50 Sinusoids
**File**: `time_integration.py` line 1561

For broadband random excitation, 50 components may not capture the spectral content adequately. Should be parameterizable.

### L8. Sparse Matrix Support Imported But Not Used
**File**: `time_integration.py`

Imports `csr_matrix`, `spsolve`, `eigsh` from scipy.sparse but all matrices are dense numpy arrays. For systems with >50 DOFs (e.g., per-thread distributed model), sparse solvers would be significantly faster.

---

## Prioritized Improvement Roadmap

| Priority | ID | Description | Effort | Impact |
|---|---|---|---|---|
| **1** | C5 | Wire contact system into matrix assembly and solver | HIGH | Enables the entire contact/tribology infrastructure |
| **2** | C1 | Fix distributed thread stiffness formula | LOW | Correct per-thread analysis |
| **3** | C2+C3 | Standardize head stiffness and stress area formulas | LOW | Consistent calculations |
| **4** | H3 | Connect CoupledLooseningAnalyzer to Contact objects | HIGH | Unified friction/wear/loosening |
| **5** | H2 | Fix system stiffness calculation in solver | LOW | Correct preload loss |
| **6** | C4 | Implement Iwan friction state update | MEDIUM | Working Iwan model |
| **7** | H4 | Add thermal expansion preload loss | MEDIUM | Critical for dissimilar materials |
| **8** | M1 | Implement proper VDI 2230 K-factor | LOW | Accurate torque-preload |
| **9** | H1 | Fix HHT tribological force evaluation | LOW | Correct nonlinear contact dynamics |
| **10** | M5+M6 | Fix similitude Pi5 and material scaling | LOW | Accurate scaling predictions |
| **11** | H5 | Add matrix reassembly option for nonlinear problems | HIGH | Correct gasket/elastoplastic analysis |
| **12** | M2 | Switch to eigh for modal analysis | LOW | Better numerics |
| **13** | L6 | Unify friction evolution implementations | LOW | Code consistency |
| **14** | H6 | Add residual floor to stretched exp/log models | LOW | Physical correctness |
| **15** | M8+M9 | Parameterize loosening coeff, separate thread/bearing μ | LOW | Better calibration |
