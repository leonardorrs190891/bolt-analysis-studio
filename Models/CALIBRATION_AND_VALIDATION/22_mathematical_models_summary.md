# Study 22: Mathematical Models Summary — All Equations for Generating Loosening Curves

## Overview
This file collects ALL mathematical models needed to generate theoretical preload decay curves, organized from simplest (empirical fits) to most complex (physics-based). Each model includes the complete equation set, required inputs, and validated parameter ranges.

---

## Model 1: Allometric Power Law (Simplest)

### Source
Lu et al. (2024), Sensors 24(11):3306

### Equation
```
F(N) = a × N^b
```

### Parameters
- F(N): preload at cycle N (in Newtons)
- N: number of loading cycles
- a: coefficient (≈ F₀ for N=1)
- b: exponent (negative, typically −0.3 to −0.8)

### Fitting Procedure
1. Take experimental data points (N_i, F_i)
2. Take log of both sides: ln(F) = ln(a) + b × ln(N)
3. Linear regression on (ln(N), ln(F))

### Typical Parameters (M8, 1.0 mm amplitude)
```
a ≈ 9,500 N
b ≈ −0.55
R² > 0.855
```

### Valid Range
- N > 1 (diverges at N=0)
- Best for rapid loosening (Stage II dominant)
- Not suitable for threshold-regime behavior

---

## Model 2: Double Exponential Decay

### Source
General — used by Li et al. (2016, Tsinghua) and many others

### Equation
```
F(N) = A₁ × exp(−B₁ × N) + A₂ × exp(−B₂ × N)
```

### Physical Interpretation
- First term: **Stage I** (rapid initial loss from plastic deformation)
- Second term: **Stage II** (gradual rotational loosening)
- A₁ + A₂ = F₀ (initial preload)
- B₁ >> B₂ (fast rate >> slow rate)

### Typical Parameters

#### M8 at 1.0 mm amplitude, F₀ = 11,567 N
```
A₁ = 7,000 N    (60.5% of F₀)
B₁ = 0.12 per cycle
A₂ = 4,567 N    (39.5% of F₀)
B₂ = 0.008 per cycle
```

#### M12 at 0.46 mm amplitude, F₀ = 25,000 N
```
A₁ = 10,000 N   (40% of F₀)
B₁ = 0.030 per cycle
A₂ = 15,000 N   (60% of F₀)
B₂ = 0.004 per cycle
```

### Fitting Procedure
1. Plot ln(F) vs. N — should show bilinear behavior
2. Late-stage data (large N): fit A₂, B₂ from the slower linear region
3. Subtract: F_residual = F − A₂×exp(−B₂×N)
4. Fit A₁, B₁ from F_residual vs. N

---

## Model 3: Phenomenological Power-Law Life Model

### Source
Yang, Jeong & Lim (2023), IJPEM 24:825–835

### Loosening Life Equation
```
N_L = C × (Δd)^(−m)
```

Where:
- N_L: loosening life (cycles to 10% residual preload)
- Δd: transverse displacement amplitude (mm)
- C: joint constant
- m: exponent (typically 3.5–4.0)

### Master Decay Curve
Once N_L is known, the normalized decay curve is:
```
F/F₀ = exp(−k × (N/N_L)^n)
```

With universal parameters:
- k = 2.3
- n = 0.7

### To Generate Any Curve
```
INPUT: F₀, Δd, C, m, k, n
STEP 1: N_L = C × Δd^(−m)
STEP 2: For each cycle N:
    F/F₀ = exp(−2.3 × (N/N_L)^0.7)
    F = F₀ × F/F₀
```

### Fitted Constants
| Bolt | C | m |
|---|---|---|
| M6 Class 10.9 | 5.2 | 3.5 |
| M8 Class 10.9 | 10.5 | 3.8 |
| M10 Class 10.9 | 22.0 | 3.9 |
| M12 Class 10.9 | 45.0 | 4.0 |

---

## Model 4: Jiang Two-Stage Model

### Source
Jiang, Zhang et al. (2003/2004), ASME J. Mech. Des.

### Stage I: Non-Rotational (Cyclic Plasticity)

Preload loss from ratchetting at thread roots:
```
ΔF_I(N) = F₀ × [1 − exp(−λ × N)] × η
```

Where:
- λ: material ratchetting rate parameter (≈ 0.02–0.05 per cycle)
- η: maximum Stage I loss fraction (0.10–0.40, depends on displacement amplitude)
- N: number of cycles

The ratchetting strain follows Armstrong-Frederick kinematic hardening:
```
dε_p = (3/2) × (dλ_p / σ_eq) × s
```
With back stress evolution:
```
dα = C × dε_p − γ × α × dp
```

### Stage II: Rotational (Nut Back-Off)

After transition (at ~0.5° nut rotation):
```
θ(N) = θ_tr + ω_loosen × (N − N_tr)
```
Where:
- θ_tr ≈ 0.5° (transition angle)
- N_tr: cycle at transition
- ω_loosen: loosening rate (°/cycle, approximately constant)

Preload from nut rotation:
```
F_II(N) = F_I(N_tr) − k_b × [θ(N) − θ_tr] × p / (360°)
```

### Combined Model
```
For N ≤ N_tr: F(N) = F₀ − ΔF_I(N)
For N > N_tr:  F(N) = F(N_tr) − k_b × ω_loosen × (N − N_tr) × p / 360
```

### Transition Criteria
Stage I → Stage II transition occurs when:
- θ_nut accumulates to ≈ 0.5°
- OR when the ratchetting-induced preload loss causes complete contact slip
- Approximate: N_tr ≈ 30/δ (cycles), where δ is displacement amplitude in mm

---

## Model 5: Nassar-Yang Nonlinear Model (Most Complete)

### Source
Nassar & Yang (2009), J. Vib. Acoust. 131:021009

### Full Algorithm (Python pseudocode)
```python
import numpy as np

def loosening_curve(F0, delta, omega, mu_th, mu_b, bolt_params, N_max):
    """
    Compute preload decay curve using Nassar-Yang model.
    
    Parameters:
    F0: initial preload (N)
    delta: transverse displacement amplitude (mm)
    omega: angular frequency (rad/s) = 2*pi*f
    mu_th: thread friction coefficient
    mu_b: bearing friction coefficient
    bolt_params: dict with p, d2, alpha, r_be, E, I_thread, L_engage
    N_max: maximum number of cycles
    """
    p = bolt_params['p']           # pitch (mm)
    d2 = bolt_params['d2']         # pitch diameter (mm)
    alpha = bolt_params['alpha']   # half thread angle (rad) = pi/6
    r_t = d2 / 2                   # thread pitch radius (mm)
    r_be = bolt_params['r_be']     # effective bearing radius (mm)
    beta = np.arctan(p / (np.pi * d2))  # helix angle (rad)
    
    # Bolt-joint stiffness
    k_b = bolt_params['k_bolt']    # N/mm
    k_j = bolt_params['k_joint']   # N/mm
    k_sys = (k_b * k_j) / (k_b + k_j)  # N/mm
    
    F = F0
    results = [(0, F, 1.0, 0.0)]  # (cycle, preload, F/F0, theta_total)
    theta_total = 0
    
    for n in range(1, N_max + 1):
        # Critical forces for complete slip
        F_th_cr = mu_th * F / np.cos(alpha)  # thread critical
        F_b_cr = mu_b * F                     # bearing critical
        
        # Applied transverse forces (simplified - peak values)
        # These depend on joint stiffness and geometry
        F_th_applied = delta * bolt_params['k_thread_shear']
        F_b_applied = delta * bolt_params['k_bearing_shear']
        
        # Check for complete slip
        thread_slip = F_th_applied > F_th_cr
        bearing_slip = F_b_applied > F_b_cr
        
        if thread_slip and bearing_slip:
            # Both surfaces in complete slip — loosening occurs
            # Pitch torque (drives loosening)
            T_pitch = F * p / (2 * np.pi)
            
            # Bearing friction torque (resists loosening)
            T_bearing = mu_b * F * r_be
            
            # Thread friction torque (net effect depends on slip direction)
            phi = np.arctan(mu_th / np.cos(alpha))
            T_thread_net = F * r_t * mu_th / np.cos(alpha) * np.sin(2 * beta)
            
            # Net loosening torque
            T_net = T_pitch - T_bearing + T_thread_net
            
            if T_net > 0:
                # Compute rotation increment
                # Simplified: assume constant rotation per cycle
                d_theta = T_net / (mu_b * F * r_be) * (np.pi / 180)  # degrees
                
                # Update preload
                d_F = k_sys * d_theta * (np.pi / 180) * p / (2 * np.pi)
                F = max(0, F - d_F)
                theta_total += d_theta
        else:
            # Partial slip only — Stage I loss (small)
            d_F_stage1 = 0.001 * F  # ~0.1% per cycle in partial slip
            F = max(0, F - d_F_stage1)
        
        results.append((n, F, F/F0, theta_total))
        
        if F < 0.01 * F0:
            break
    
    return results
```

---

## Model 6: D-N Curve (Displacement-Life, Fatigue Analogy)

### Equation (from Yang et al. 2019)
```
log₁₀(N_L) = A − m × log₁₀(δ)
```

Or equivalently:
```
N_L = 10^A × δ^(−m)
```

### Parameters by Bolt Size and Preload

| Bolt | Preload (% proof) | A | m | δ_threshold (mm) |
|---|---|---|---|---|
| M8 8.8 | 50% | 1.4 | 3.5 | 0.20 |
| M8 10.9 | 50% | 1.7 | 3.8 | 0.22 |
| M10 10.9 | 50% | 1.9 | 3.9 | 0.30 |
| M12 10.9 | 30% | 1.6 | 3.8 | 0.25 |
| M12 10.9 | 50% | 2.1 | 4.0 | 0.35 |
| M16 4.8 | 50% | 1.8 | 3.5 | 0.33 |
| M16 4.8 | 80% | 2.3 | 3.8 | 0.48 |

### Effect of Preload on D-N Curve
Higher preload shifts the D-N curve **upward** (longer life at same amplitude):
```
A(F₀) = A_ref + k_A × ln(F₀/F_ref)
```
With k_A ≈ 0.3–0.5

### Effect of Friction on D-N Curve
Higher friction shifts the D-N curve **upward**:
```
A(μ) = A_ref + k_μ × (μ − μ_ref) / μ_ref
```
With k_μ ≈ 1.0–2.0

---

## Model 7: Critical Transverse Force (Loosening Threshold)

### Simplified Criterion (from Nassar & Yang 2011)
Self-loosening will NOT occur if:
```
F_trans < F₀ × μ_b × cos(β) / [1 + μ_th × tan(β)/cos(α)]
```

### Even Simpler (Dinger's design criterion):
```
F_trans < 0.5 × μ_min × F₀
```
Where μ_min = min(μ_th, μ_b)

### Critical Displacement (from threshold)
```
δ_cr = F_trans_cr / k_joint_shear
```

---

## Conversion Between Preload Loss and Nut Rotation

### Preload per Degree of Nut Rotation
```
ΔF_per_degree = k_sys × p / 360
```

Examples:
| Bolt | k_sys (N/mm) | p (mm) | ΔF per degree (N/°) |
|---|---|---|---|
| M8 | ~150,000 | 1.25 | 521 |
| M10 | ~200,000 | 1.50 | 833 |
| M12 | ~250,000 | 1.75 | 1,215 |
| M16 | ~400,000 | 2.00 | 2,222 |
| M20 | ~500,000 | 2.50 | 3,472 |

### Total Nut Rotation for Complete Loosening
```
θ_total = F₀ / ΔF_per_degree    (degrees)
θ_turns = θ_total / 360         (full turns)
```

| Bolt | Class | F₀ at 70% proof (N) | θ_total (°) | Turns |
|---|---|---|---|---|
| M8 | 10.9 | 22,000 | 42.2 | 0.12 |
| M10 | 10.9 | 35,000 | 42.0 | 0.12 |
| M12 | 10.9 | 50,500 | 41.6 | 0.12 |
| M16 | 10.9 | 110,000 | 49.5 | 0.14 |
| M20 | 10.9 | 173,000 | 49.8 | 0.14 |

**Note**: Only ~0.12 full turns of nut rotation causes complete preload loss! This illustrates how critical even small angular movements are.

---

## Quick-Reference: Which Model to Use?

| Application | Recommended Model | Complexity |
|---|---|---|
| Quick estimate, known amplitude | Model 3 (Phenomenological) | Low |
| Curve fitting to test data | Model 2 (Double exponential) | Low |
| Design verification (will it loosen?) | Model 7 (Critical force) | Low |
| Loosening life estimation | Model 6 (D-N curve) | Medium |
| Full transient simulation | Model 5 (Nassar-Yang) | High |
| FEA validation / detailed mechanism | Model 4 (Jiang two-stage) | High |
| Rough preliminary design | Model 1 (Power law) | Very low |

---

## MSD BUILDER NOTE

> This file is a **mathematical models reference** and does not represent a single reproducible test configuration.
> The models described here are implemented in the software's numerical layer (`numerical/preload_loss_models.py`).
> For MSD Builder configurations with experimental data, refer to the individual experimental studies (Papers 01–15, 20, 23–34) that contain specific test parameters and ValidationCase code blocks.
