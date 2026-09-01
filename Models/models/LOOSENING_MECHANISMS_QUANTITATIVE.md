# Bolted Joint Loosening Mechanisms — Quantitative Reference
## For Bolt Analysis Studio v4.0 Loosening Curve Improvement

*Compiled 2026-02-21 from: BoltScience documents (Eccles), VDI 2230, BOLTCALC training materials, and peer-reviewed literature.*

---

## Overview: Taxonomy of Preload Loss

Total preload decay splits into two independent categories:

```
PRELOAD LOSS ΔF_total
├── ROTATIONAL LOOSENING (fastener rotates, threads disengage)
│   └── Junker mechanism: transverse slip at thread + bearing surface simultaneously
│
└── NON-ROTATIONAL LOOSENING (no fastener rotation)
    ├── Embedding (immediate — first few cycles)
    ├── Stress Relaxation (time-dependent creep)
    ├── Thermal / CTE mismatch effects
    ├── Gasket creep/relaxation
    └── Wear-induced loss (long-term, cyclic slip)
```

**Critical design insight (Eccles/BoltScience):** In practice, loosening is usually a *combination*:
non-rotational preload reduction → joint movement initiated → rotational self-loosening or fatigue.
Once joint movement begins, failure mode is almost always self-loosening or fatigue fracture.

---

## 1. Rotational Self-Loosening (Junker Mechanism)

### 1.1 Physical Mechanism

Junker (1969) established that **transverse dynamic loads** are far more severe than axial dynamic loads.
Self-loosening occurs when relative micro-slip occurs at **both**:
1. The mating thread interface (stud–nut), AND
2. The bearing surface under the nut face or bolt head

The helix of the thread then acts as an inclined plane, converting transverse displacement into nut rotation.

### 1.2 Slip Initiation Criterion

```
Slip initiates when:   F_transverse > μ × F_preload

Thread slip condition:  F_trans > μ_thread × F_preload
Bearing slip condition: F_trans > μ_bearing × F_preload × (r_eff / r_thread)

Both must slip simultaneously for rotational loosening to proceed.
```

**Quantitative threshold (Junker test, M10 coarse, μ = 0.12):**
- For F₀ = 30 kN: slip begins at F_trans ≈ 3.6 kN (12% of preload)
- For F₀ = 15 kN (after partial embedding loss): slip begins at F_trans ≈ 1.8 kN

### 1.3 Preload Decay Curve Shape — Two Stages

```
F_preload
│
F₀ ─────┐
        │ Stage 1: Rapid decline
        │  (non-rotational + initiation of rotation)
        │  Duration: ~10²–10³ cycles
        └──────────────────┐
                           │ Stage 2: Gradual continued decline
                           │  (steady nut rotation per cycle)
                           └──────────────────────────────── N (cycles)
```

**Quantitative stage data:**
- Stage 1 ends / Stage 2 begins at approximately **0.5° of cumulative nut rotation**
- Complete loosening (nut detachment risk): within **10³–10⁴ cycles** for unprotected joints under transverse vibration amplitude exceeding the slip threshold
- Residual preload at plateau: typically **5–15% of F₀** (joint not fully loose, but below functional minimum)

### 1.4 Preload Loss Rate Formula (Rotational)

```
ΔF_rot per cycle = k_bolt × (p / 2π) × Δθ_per_cycle

where:
  k_bolt  = bolt axial stiffness [N/mm]
  p       = thread pitch [mm]
  Δθ      = nut rotation per cycle [rad]
  Δθ ≈ (F_trans − μ×F_preload) / (k_thread × r_eff)  (slip-based estimate)
```

**Example (M16 × 2.0, k_bolt = 1200 N/mm, F₀ = 50 kN, μ = 0.12):**
- Slip threshold: F_trans > 6.0 kN
- At F_trans = 10 kN: net slipping force = 4.0 kN
- Δθ ≈ 0.002 rad/cycle → ΔF_rot ≈ 1200 × (2.0/2π) × 0.002 ≈ **0.76 N/cycle**
- At this rate: 50% preload loss in ≈ **33 000 cycles** (if μ stays constant)

### 1.5 Effect of Vibration Amplitude

| Amplitude (fraction of slip threshold) | Loosening behavior |
|---|---|
| < 1.0 (sub-threshold) | No rotational loosening; only non-rotational mechanisms active |
| 1.0–1.5 | Slow rotational loosening; Stage 2 dominates |
| > 1.5 | Rapid rotational loosening; Stage 1 very short |
| > 3.0 | Near-complete loosening in < 200 cycles |

**Note:** Vibration frequency has minimal effect on the loosening *rate per cycle*.
Amplitude is the dominant parameter.

### 1.6 Countering Measures and Their Limits

| Device | Mechanism | Effectiveness |
|---|---|---|
| Helical spring washer | Adds spring compliance | **Ineffective**; can loosen *faster* than plain bolt |
| Prevailing torque nut | Nylon/plastic drag torque | Bolt retention device only; NOT a true lock nut under transverse vibration |
| Higher preload | Raises slip threshold | Effective until yield is exceeded |
| Thread locking compound | Bonding | Effective if cure is complete |
| Fine thread | Larger helix resistance | Slightly better than coarse |
| Double nut (jam nut) | Compressive thread contact | Effective if correctly applied |

---

## 2. Embedding (Non-Rotational)

### 2.1 Physical Mechanism

Even **apparently smooth** machined surfaces have micro-asperities. Under compressive load at the:
- Nut face / bolt head bearing surface
- Joint interface faces
- Thread flanks (engaged threads)

...these asperities undergo **plastic flattening** (occurs even below bulk yield stress because real contact
area ≪ apparent contact area → high local stress). This shortens the joint stack, reducing bolt
extension and hence preload.

Embedding occurs in two phases:
1. **During tightening** (significant flattening at assembly)
2. **After tightening** (additional settling under sustained load and applied forces)

### 2.2 VDI 2230 Quantitative Values

VDI 2230 Table 5.4/1 — **Embedding per interface** (approximate guide values):

| Surface condition | Roughness Rz [µm] | Embedding per interface [µm] |
|---|---|---|
| Ground / lapped | < 4 | 0.5 – 1.0 |
| Fine machined | 4 – 10 | 1.0 – 2.5 |
| Medium machined | 10 – 40 | 2.0 – 4.0 |
| Rough machined | 40 – 100 | 3.5 – 6.5 |
| As-rolled / coated | > 100 | 5.0 – 10.0 |
| Painted / lacquered | — | 50 – 100 |

**Total joint embedding** = Σ (embedding × n_interfaces)

Typical interfaces in a flanged joint: bolt head face (×1) + thread engagement zone (×1) + flange contact (×1) + nut face (×1) = **4 interfaces**

**Example calculation (VDI 2230, M16 steel, Rz ≈ 16 µm, k_bolt+members = 300 N/µm):**
```
f_Z_per_interface ≈ 3 µm
Total f_Z = 4 interfaces × 3 µm = 12 µm (add gasket if present)
ΔF_embed = k_system × f_Z = 300 [N/µm] × 12 [µm] = 3,600 N (≈ 7% of 50 kN preload)
```

**BOLTCALC example (M10 × 1.5, Class 10.9, L_grip = 65.4 mm):**
- Embedding loss = **3,262 N** (of 21,319 N minimum preload → **15.3% loss**)

### 2.3 Effect on Small vs. Large Fasteners

| Bolt diameter | Typical embedding loss as % of preload |
|---|---|
| M6 | 25 – 38% |
| M10 | 12 – 20% |
| M16 | 6 – 10% |
| M24 | 3 – 6% |
| M36 | 1.5 – 3% |

Small fasteners are disproportionately affected because k_system is lower relative to f_Z.

### 2.4 Surface Pressure Limit (Embedding vs. Creep Boundary)

When bearing stress **p_bearing > p_lim** (limiting surface pressure of joint material):
```
p_lim values:
  Steel (high strength)  ≈ 900 – 1200 N/mm²
  Steel (structural)     ≈ 500 – 700 N/mm²
  Aluminium alloy        ≈ 80 – 150 N/mm²
  Cast iron              ≈ 120 – 200 N/mm²
  PTFE / plastic         ≈ 10 – 30 N/mm²
```

Above p_lim, embedding becomes **uncontrolled creep** (see §4).
Remedy: flanged fasteners (larger bearing area) or hardened washers.

**BOLTCALC engine mount example:** Aluminium support (p_lim = 120 N/mm², p_actual = 178 N/mm²):
Factor of Safety = 0.67 → **FAILED** → excessive embedding/creep anticipated.

### 2.5 Embedding Model for Software

```
ΔF_embed(N) = k_sys × f_Z_total

f_Z_total = Σᵢ [f_Z_interface(Rz_i, material_i)]

Recommended curve shape:
  ΔF_embed(t) = ΔF_embed_final × (1 - e^(-N / N_c))

where:
  N_c ≈ 10–50 cycles (embedding is essentially complete within first 50 cycles)
  ΔF_embed_final = k_sys × f_Z_total
```

---

## 3. Stress Relaxation (Time-Dependent, Non-Rotational)

### 3.1 Physical Mechanism

At sustained stress levels, materials undergo **creep** (time-dependent plastic deformation) even below
the instantaneous yield point. In a bolt, this shortens the bolt and/or thickens the nut, reducing bolt
extension and preload.

### 3.2 Quantitative Data

**Short-term relaxation (room temperature, steel):**

| Timeframe | Preload loss |
|---|---|
| Immediately after tightening | ~2% (thread settlement) |
| First 24 hours | 3 – 8% additional |
| 21 days | +3.6% cumulative |
| Long term (years) | +2% additional |

**Temperature-dependent relaxation (ASTM bolt materials at 725°F / 385°C):**

| Bolt material | Relaxation at high temperature |
|---|---|
| ASTM A193 B7 (CrMo alloy) | **~60%** preload loss |
| ASTM A193 B16 (CrMoV alloy) | **~25%** preload loss |
| ASTM A193 B8M (316 SS) | Near zero / slight gain |

**Critical temperature thresholds:**
```
> 150°C  : Begin checking relaxation for mild steel
> 250°C  : Significant relaxation activated for alloyed/construction steels
> 400°C  : Major relaxation for all standard fastener materials
> 550°C  : Use refractory alloys (Inconel, A286, etc.)
```

**Extreme case (plastics/composites under bolt head):**
Up to **80% clamp force loss over 12 hours** observed experimentally.

### 3.3 Relaxation Model

```
F_p(t) = F_p0 × e^(-t / τ)          (simple exponential)

or more accurately:

F_p(t) = F_p0 × (1 - C_r × log₁₀(t))    (logarithmic — VDI 2230 form)

where:
  C_r = material-dependent relaxation coefficient
  C_r ≈ 0.01–0.03  for steel at room temperature
  C_r ≈ 0.05–0.15  for steel at 200–300°C
  C_r ≈ 0.20–0.40  for aluminium at room temperature
  C_r ≈ 0.10–0.30  for PTFE/soft gaskets
```

---

## 4. Gasket Creep / Relaxation

### 4.1 Mechanism

Gasket materials (especially soft ones) undergo **viscoplastic compression** under bolt load,
reducing the effective grip length and thus the bolt preload.

### 4.2 Quantitative Data by Gasket Type

| Gasket type | Creep relaxation | Retorque required? |
|---|---|---|
| Metallic ring joint (RTJ) | < 1% at ambient | No |
| Spiral wound (SW) | 2–5% at ambient | Generally no |
| Kammprofile (semi-metallic) | 2–8% | Depends on filler |
| Compressed fibre / CNAF | 10–20% | Yes |
| PTFE / flexible graphite | 15–35% | **Yes** |
| Soft rubber | 30–60% | Yes |

**Flange creep (material yields under gasket seating stress):**
- ASME bolted flange joints: up to **70% bolt load relaxation** when flange material creeps
- Spiral wound gasket study: negligible creep at ambient; significant at temperature + pressure cycling

### 4.3 Creep Model

```
δ_gasket(t) = δ₀ × [1 + C_g × log₁₀(1 + t/t_ref)]

ΔF_gasket = k_sys_series × δ_gasket(t)

where:
  C_g    = gasket creep coefficient (material-specific)
  δ₀    = initial gasket deflection [mm]
  t_ref  = reference time (typically 1 hour)
```

---

## 5. Thermal / CTE Mismatch Effects

### 5.1 Mechanism

When bolt and clamped members have **different coefficients of thermal expansion** (CTE),
a temperature change ΔT generates an internal force change in the bolt:

```
ΔF_thermal = (α_member × L_member - α_bolt × L_bolt) × ΔT × (k_b × k_m / (k_b + k_m))

For uniform temperature change:
ΔF_thermal = (α_m - α_b) × ΔT × L_grip × k_system
```

### 5.2 CTE Values for Common Materials

| Material | CTE α [×10⁻⁶ /°C] |
|---|---|
| Carbon steel (bolt) | 11.7 |
| Stainless steel 316 | 16.0 |
| Cast iron | 10.5 |
| Aluminium alloy | 23.6 |
| Titanium | 8.6 |
| PTFE | 112 |
| Carbon fibre (CFRP) | 1–5 (depends on orientation) |

**Critical mismatch example (steel bolt M12, aluminium flange, ΔT = +100°C, L = 50 mm):**
```
Δα = 23.6 - 11.7 = 11.9 × 10⁻⁶ /°C
ΔF = 11.9×10⁻⁶ × 100 × 50 × k_system
   ≈ 0.0595 mm × 300 N/mm = +17.9 kN  (heating: bolt gets MORE preload, member yield risk)

Cooling ΔT = -100°C:
ΔF ≈ -17.9 kN  (preload LOSS — loosening risk)
```

### 5.3 Thermal Cycling Preload Decay

Repeated thermal cycling causes **ratcheting** — irreversible preload loss per cycle:

| Cycle number | Preload loss per cycle |
|---|---|
| 1st cycle | **~41%** of initial preload lost |
| 2nd cycle | ~8.5% additional |
| 3rd cycle | ~5.5% additional |
| 4th cycle | ~4.0% additional |
| Nth (N > 5) | Asymptotic to residual value |

```
Thermal ratcheting model:
F_p(N) = F_p0 × [1 - A × (1 - e^(-N/τ_th))]

where:
  A    = total fractional loss at saturation (0.6–0.8 for high Δα cases)
  τ_th = thermal cycle constant (typically 2–5 cycles to reach 63% of saturation)
```

---

## 6. Wear-Induced Preload Loss

### 6.1 Mechanism

Under cyclic transverse loading below the Junker slip threshold, **fretting wear** occurs
at the contact interfaces. Material removal shortens the joint stack → preload loss.

Archard's wear law:

```
V_wear = K × F_n × s / H

where:
  K    = wear coefficient (dimensionless, material/lubrication dependent)
  F_n  = normal (contact) force [N]
  s    = sliding distance [mm]
  H    = hardness of softer material [N/mm²]

ΔF_wear = k_sys × h_wear   where h_wear = V_wear / A_contact
```

### 6.2 Wear Coefficient K by Condition

| Contact condition | Wear coefficient K |
|---|---|
| Metal–metal, dry, unlubricated | 1×10⁻³ – 1×10⁻² |
| Metal–metal, lubricated | 1×10⁻⁵ – 1×10⁻⁴ |
| Fretting (micro-slip, unlubricated) | 1×10⁻⁴ – 1×10⁻³ |
| Fretting (lubricated) | 1×10⁻⁶ – 1×10⁻⁴ |
| Hard coating vs. steel | 1×10⁻⁶ – 1×10⁻⁵ |

### 6.3 Wear Preload Loss Rate

Wear-induced preload loss is **cumulative and slow** (unlike embedding which saturates early).
For a typical M16 joint under fretting conditions:

```
h_wear per cycle ≈ 0.001–0.01 µm (fretting regime)
ΔF_wear per cycle ≈ 0.3–3 N/cycle (k_sys = 300 N/µm, A = 1 cm²)
```

At 10⁶ cycles: total ΔF_wear ≈ **300 – 3000 N** (0.6–6% of typical 50 kN preload)
Wear becomes significant at very high cycle counts or poor lubrication conditions.

---

## 7. External Force Effects on Clamp Force

### 7.1 Axial Load Factor (Load Introduction)

External axial force F_A reduces clamp force by (1 - Φ) × F_A:

```
Φ = k_b / (k_b + k_m)   [load factor, Shigley/VDI 2230]

Typical values:
  Φ = 0.05 – 0.15  (hard joint: km >> kb, e.g., short steel flange)
  Φ = 0.30 – 0.60  (soft joint: kb ≈ km, e.g., long bolt + gasket)
  Φ → 1.0          (only bolt, no members — theoretical limit)
```

**Eccentric loading factor n (load introduction factor):**
```
n = 0   : load at clamping interface (most favorable)
n = 0.5 : load at mid-plane of clamped parts (typical)
n = 1   : load at bolt head/nut (least favorable)

Φ_eccentric = n × Φ
```

### 7.2 Clamp Force vs. External Axial Load

```
F_clamp(F_A) = F₀ - (1 - Φ) × F_A   [while F_clamp > 0]
F_bolt(F_A)  = F₀ + Φ × F_A          [while clamp maintained]

Separation condition:   F_A > F₀ / (1 - Φ)
```

**Example (M16, F₀ = 50 kN, Φ = 0.15):**
- At F_A = 20 kN: ΔF_clamp = -17 kN, F_clamp = 33 kN (still clamped)
- Separation load: F_A_sep = 50/0.85 = **58.8 kN**

### 7.3 Transverse Force (Shear)

Clamp force required to prevent slip under transverse force F_T:

```
F_clamp_required = F_T / (μ × n_shear_planes)

Example (F_T = 5 kN, μ = 0.20, 2 shear planes):
F_clamp = 5000 / (0.20 × 2) = 12,500 N minimum
```

---

## 8. Friction and Tightening Scatter

### 8.1 Torque Distribution

For a **typical M12 flanged bolt (Dacromet finish, 10.9 class)**:

| Torque component | Value [Nm] | Fraction |
|---|---|---|
| Thread extension (stretching bolt) | 11.1 Nm | 13.5% |
| Thread friction | 30.9 Nm | 37.4% |
| **Nut/head face friction** | **42.6 Nm** | **51.5%** |
| **Total** | **83.8 Nm** | 100% |

Key insight: **~50% of tightening torque is absorbed by bearing face friction**.
This is the most variable component and dominates preload scatter.

### 8.2 Friction Coefficient Typical Ranges

| Surface condition | μ_thread | μ_bearing |
|---|---|---|
| Dry, as-received steel | 0.12 – 0.18 | 0.12 – 0.20 |
| Lightly oiled | 0.08 – 0.12 | 0.08 – 0.14 |
| Molybdenum disulphide | 0.05 – 0.08 | 0.05 – 0.10 |
| Dacromet / Geomet coating | 0.10 – 0.16 | 0.10 – 0.16 |
| Zinc plated | 0.10 – 0.18 | 0.12 – 0.20 |
| PTFE coated | 0.04 – 0.08 | 0.04 – 0.08 |

**Friction variation in practice:** Up to **2:1 ratio** between min and max μ for a given nominal condition.
This directly causes ±50% preload scatter for a given tightening torque.

### 8.3 Preload from Torque (Full Torque-Tension Equation)

```
T_tighten = F₀ × [p/(2π) + μ_thread × d₂/(2cosα) + μ_bearing × D_bearing/2]

where:
  F₀            = desired preload [N]
  p             = thread pitch [mm]
  μ_thread      = thread friction coefficient
  d₂            = thread pitch diameter [mm]
  α             = thread half-angle (30° for metric ISO)
  μ_bearing     = bearing face friction coefficient
  D_bearing     = effective bearing diameter [mm]

Simplified (nut factor K):
  T = K × d × F₀    where K ≈ 0.15–0.22 for typical steel fasteners
```

---

## 9. Preload Decay Curve — Combined Model for BAS Software

### 9.1 Recommended Total Preload Function

```python
def F_preload(t, N, T_temp):
    """
    Combined preload decay model.

    Parameters:
    - t   : time [hours]
    - N   : vibration cycles
    - T   : temperature [°C]
    """
    # Initial assembly preload
    F0 = F_assembly

    # 1. Embedding (saturates within first ~50 cycles)
    delta_embed = f_Z_total   # µm, from VDI 2230 Table 5.4/1
    dF_embed = k_sys * delta_embed * (1 - exp(-N / N_c_embed))
    # N_c_embed ≈ 10–50 cycles

    # 2. Stress relaxation (logarithmic, time-dependent)
    dF_relax = F0 * C_r * log10(1 + t / t_ref)
    # C_r = material+temp dependent (see §3.3)

    # 3. Gasket creep (if gasket present)
    dF_gasket = k_sys * delta0_gasket * C_g * log10(1 + t / t_ref_gasket)

    # 4. Rotational loosening (Junker — only if F_trans > slip threshold)
    if F_transverse > mu_eff * F_preload_current:
        dF_rot = k_bolt * (pitch / (2*pi)) * theta_rate * N
    else:
        dF_rot = 0

    # 5. Wear (long-term, cumulative)
    dF_wear = k_sys * K_wear * F_contact * slip_amplitude * N / (H * A)

    # 6. Thermal ratcheting (if thermal cycling)
    dF_thermal = F0 * A_th * (1 - exp(-N_thermal / tau_th))

    F_current = F0 - dF_embed - dF_relax - dF_gasket - dF_rot - dF_wear - dF_thermal
    return max(F_current, 0)
```

### 9.2 Mechanism Dominance by Phase

| Phase | Dominant mechanism | Typical % of total loss |
|---|---|---|
| Assembly | Friction scatter | ±30–50% of target |
| Cycles 1–50 | Embedding + relaxation (Stage 1) | 10–20% |
| Cycles 50–500 | Rotational loosening (if threshold exceeded) | 30–70% |
| Cycles > 500 | Steady-state rotation or stabilization | Variable |
| Long-term (years) | Stress relaxation + wear | 2–10% additional |

### 9.3 Preload Safety Factor Requirements (VDI 2230)

```
Minimum design preload:
F_min_required = F_clamp_function + F_embedding_loss + F_margin

Assembly preload target:
F_assembly = F_min_required × Tightening_Factor

Tightening Factor TF = F_max / F_min   (accounts for friction scatter)
  TF = 1.4 – 2.0  (torque wrench, typical)
  TF = 1.1 – 1.3  (hydraulic tensioner)
  TF = 1.05–1.15  (elongation measurement)

VDI 2230 target: F_assembly ≈ 0.90 × F_yield_min (90% of minimum yield)
```

---

## 10. Implementation Guidance for BAS Software

### 10.1 Curve Fitting Priorities

The loosening curve (preload vs. cycles/time) should be implemented as a **superposition** of the following
basis functions, each independently parameterised:

| Mechanism | Basis function | Key parameters |
|---|---|---|
| Embedding | `A × (1 - exp(-N/Nc))` | A = k_sys × f_Z; Nc = 10–50 |
| Relaxation | `B × log₁₀(1 + t)` | B = F₀ × C_r |
| Gasket creep | `C × log₁₀(1 + t)` | C = k_sys × δ₀ × C_g |
| Rotational (Junker) | `D × N` (linear per cycle, above threshold) | D = k_bolt × p/2π × θ_rate |
| Thermal ratcheting | `E × (1 - exp(-N_th/τ))` | E = F₀ × A_th |
| Wear | `F × N` (linear, very slow) | F = k_sys × wear_rate |

### 10.2 Sensor / Validation Data Correspondence

The Junker test machine produces the canonical **preload vs. cycles** decay curve.
Standard output: `F_preload(N) / F₀` — normalised preload ratio.

Expected shapes from literature:
- **No loosening:** flat curve at F/F₀ ≈ 0.95–1.0 (only embedding loss)
- **Partial loosening:** rapid drop to F/F₀ ≈ 0.40–0.60, then plateau
- **Full loosening:** rapid drop to F/F₀ ≈ 0.05–0.10 within 10³ cycles

### 10.3 Material/Contact Parameters to Expose in UI

For each mechanism, these are the **minimum parameters** the user should be able to configure:

```
Embedding:
  - Surface roughness Rz per interface [µm]
  - Number of interfaces
  - Joint system stiffness k_sys [N/mm]

Relaxation:
  - Temperature [°C]
  - Bolt material (for C_r lookup)
  - Time of service [hours]

Gasket:
  - Gasket type (lookup C_g table)
  - Initial compression δ₀ [mm]

Rotational:
  - Transverse force F_trans [N] or amplitude [mm]
  - Friction coefficient μ (thread + bearing)
  - Thread pitch p [mm]
  - Slip threshold detection: automatic from μ × F₀

Thermal:
  - CTE_bolt, CTE_member [µm/m·°C]
  - Temperature swing ΔT [°C]
  - Number of thermal cycles

Wear:
  - Contact material pair (for K lookup)
  - Lubrication condition
  - Slip amplitude per cycle [µm]
```

---

---

## 11. Fretting Wear Regime Map

### 11.1 Vingsbo–Söderberg Classification (1988)

Three slip regimes govern wear and loosening at contact interfaces:

| Regime | Slip Amplitude δ | Wear Mechanism | Loosening Effect |
|--------|-----------------|----------------|-----------------|
| **Stick** | δ < 1–5 µm | No wear | No preload loss from wear |
| **Partial slip (mixed)** | 5 µm < δ < 50 µm | Oxidative + debris | Fretting fatigue; slow preload loss |
| **Gross slip** | δ > 50–300 µm | Adhesive/abrasive | Archard wear; rapid preload loss |

Key finding: wear coefficient increases **1–2 orders of magnitude** as δ goes from 20 µm to 300 µm.

### 11.2 Mindlin Partial-Slip Contact Mechanics

For Hertzian contact radius `a` under normal force P and tangential force Q:

```
Stick zone radius:  c = a × (1 − Q/(μP))^(1/3)
Slip annulus:       a_stick = c,  a_outer = a

Slip index (Fouvry et al., 1996):
  SI = δ_slip / δ_total
  SI < 0.1  → stick  (no loosening from wear)
  0.1–0.9   → partial/mixed (fretting fatigue, slow loss)
  SI > 0.9  → gross slip (Archard wear, rapid loss)
```

### 11.3 Fretting Stages in Bolted Joints (Quantitative)

**Stage F1 (rapid, 0–500 cycles):**
- Cyclic plastic deformation at thread roots
- Contact stiffness drops **10–30%**
- Preload loss: **5–15% of F_p0**

**Stage F2 (gradual, 500–10 000+ cycles):**
- Archard wear at thread/bearing interface
- Loss rate: **0.01–0.1% per 100 cycles**
- Friction coefficient evolves: µ drops 0.12–0.18 → 0.08–0.12 after wear-in

**Stage F3 (accelerated):**
- Fretting transitions to gross slip
- µ_kinetic reduced by **20–40%** versus unworn threads after 5 000 fretting cycles
- Self-locking condition violated → rotational loosening triggered

### 11.4 Self-Locking Condition and Wear Degradation

```
Self-locking condition:  tan(λ) < µ × cos(α_half-flank)

For M16 × 2.0:
  λ = arctan(p / π d₂) = arctan(2.0 / π × 14.7) ≈ 2.48°
  α = 30° (ISO metric half-flank)
  tan(2.48°) = 0.0433 < µ × cos(30°) = µ × 0.866
  → Self-locking requires µ > 0.0500

Initial (new bolt): µ = 0.12  → tan(λ) = 0.043 << 0.104  ✓ safe
After fretting:     µ = 0.045 → tan(λ) = 0.043 ≈ 0.039   ✗ boundary/danger zone
```

Once µ crosses the self-locking boundary, rotational loosening becomes irreversible.

### 11.5 Archard Wear Preload Loss — Worked Example

For M16 (k_sys = 400 kN/mm, A_contact = 200 mm², K = 10⁻⁵):
```
V_wear per cycle = K × F_n × δ_slip / H
                 = 10⁻⁵ × 50 000 N × 0.05 mm / 1 500 N/mm²
                 = 1.67 × 10⁻⁵ mm³/cycle

h_wear per cycle = V / A = 8.3 × 10⁻⁸ mm/cycle = 0.083 nm/cycle
ΔF_wear per cycle = k_sys × h_wear = 400 × 8.3 × 10⁻⁸ = 0.033 N/cycle
After 10 000 cycles: ΔF_wear ≈ 330 N  (0.66% of 50 kN)
After 100 000 cycles: ΔF_wear ≈ 3 300 N  (6.6%) — significant at high cycle counts
```

---

## 12. Multi-Stage Loosening Phase Model

### 12.1 Five-Phase Taxonomy with Quantitative Boundaries

Synthesized from Chen (2017, Shock & Vibration), PMC review (2021), and Boltscience:

| Phase | F_p/F_p0 | Cumulative Nut Rotation | Loss Rate dF_p/dN | Dominant Mechanism |
|-------|----------|------------------------|-------------------|--------------------|
| **STABLE** | > 0.90 | ≈ 0° | < 0.01%/cycle | Elastic cycling; no slip |
| **NON-ROTATIONAL** | 0.75–0.90 | < 0.5° | 0.01–0.1%/cycle | Embedding + fretting Stage F1 |
| **TRANSITION** | 0.55–0.75 | 0.5°–5° | 0.1–1.0%/cycle | Localized slip; mixed fretting |
| **ROTATIONAL** | 0.20–0.55 | > 5°, growing | 1–5%/cycle | Full bearing+thread slip (Junker) |
| **RUNAWAY** | < 0.20 | Unlimited | > 5%/cycle | Complete slip; nut disengaging |

**Critical transition criterion (Chen et al., 2017):**
The NON-ROTATIONAL → ROTATIONAL boundary is at **0.5° of cumulative nut rotation**.

**Pai & Hess (2002) localized slip discovery:**
Rotational loosening initiates at only **46–66% of the transverse force required for complete bearing slip**.
Localized edge-slip (not complete surface slip) is sufficient to drive nut rotation.
Four slip combination types:
1. Localized head + localized thread slip (onset, lowest force)
2. Localized head + complete thread slip
3. Complete head + localized thread slip
4. Complete head + complete thread slip (Junker complete loosening)

**Corrected slip onset (replaces classical Junker threshold):**
```
Classical:  F_onset = µ × F_p   (overestimates resistance by 1.5–2×)
Corrected:  F_onset ≈ 0.46 × µ × F_p  (lower bound, conservative design)
            F_onset ≈ 0.66 × µ × F_p  (upper bound)
```

### 12.2 Double-Exponential Preload Decay Model (Stage 1)

Tsinghua University found Stage 1 clamping force follows a **double-exponential**:

```
F_p(N) = F₀ − A₁ × (1 − exp(−N/N₁)) − A₂ × (1 − exp(−N/N₂))

where:
  A₁, N₁ = rapid initial loss (thread settlement, micro-asperity collapse)
  A₂, N₂ = slower secondary loss (fretting, cyclic plastic deformation)
  N₁ ≈ 10–50 cycles
  N₂ ≈ 200–1 000 cycles
  A₁ + A₂ = total Stage 1 loss amplitude (typically 10–25% of F₀)
```

Parameters scale with transverse vibration amplitude: larger amplitude → larger A₁, A₂ and shorter N₁, N₂.

Once Stage 1 is complete (N >> N₂):
- If F_p/F_p0 > 0.75: system settles into STABLE or NON-ROTATIONAL phase
- If F_p/F_p0 ≤ 0.75: transition to ROTATIONAL phase likely

### 12.3 Stage 2 Decay — Linear Rotational Model

After transition to ROTATIONAL phase:
```
F_p(N) = F_p(N_transition) − dF_rot/dN × (N − N_transition)

dF_rot/dN = k_bolt × (p / 2π) × Δθ_per_cycle
```

This linear model holds until RUNAWAY (complete slip, no self-arresting).

### 12.4 Variable Amplitude Loosening Life (Miner's Rule Analog)

PMC 2025 (Materials), Yang et al. (2019, Shock & Vibration):

```
Loosening life at amplitude δ_i:
  N_i = A × δ_i^(−b)   [power-law D-N curve]
  Typical M10 steel: A ≈ 10⁸,  b ≈ 3  (δ in mm)

Cumulative damage under variable amplitude:
  D = Σ (n_i / N_i) = 1  at 20% preload loss

Prediction accuracy: within ±1.2× factor experimentally validated.
```

### 12.5 Design-Level Phase Boundary Summary

```
F_p/F_p0 > 0.90   → SAFE          No action needed
F_p/F_p0 = 0.80   → ACCEPTABLE    ISO 16130 minimum pass criterion
F_p/F_p0 = 0.75   → WARNING       Non-rotational mechanisms active; inspect
F_p/F_p0 = 0.55   → CRITICAL      Slip initiated; rotational loosening imminent
F_p/F_p0 < 0.20   → FAILURE       Joint integrity compromised
```

**ISO 16130:2015 acceptance criterion:** locking device is adequate if **≥ 80% preload retained after 2 000 Junker cycles** at the reference amplitude.

---

## 13. Locking Device Performance (Quantitative)

### 13.1 Comparative Preload Retention at 2 000 Junker Cycles

From ISO 16130 data, Eccles/Boltscience, and published Junker campaigns:

| Locking Method | Preload Retention | Notes |
|---------------|------------------|-------|
| Plain nut (no locking) | **0–5%** | Complete loss in 20–200 cycles |
| Helical spring washer | 10–40% | Often ineffective; can loosen faster |
| Serrated washer | 20–60% | Surface and material dependent |
| Nyloc nut (DIN 985) | 30–70% | Retains preload plateau; T_prev-dependent |
| All-metal prevailing torque nut | 40–80% | Reusable; degrades ~10–20% per reuse |
| Nord-Lock wedge washer | 60–95% | Geometric lock, not friction |
| HEICO-LOCK | 70–95% | Similar mechanism to Nord-Lock |
| Loctite 242 (blue, medium) | 85–100% | Requires F_p ≥ threshold; 150°C limit |
| Loctite 271 (red, high) | 85–100% | Requires heat for disassembly |
| Safety wire / castle nut | ~100% | Positive mechanical retention |

### 13.2 ISO 2320:2015 Prevailing Torque Requirements

Minimum off-torque for all-metal prevailing torque nuts (first assembly):

| Nut Size | Min Off-Torque (N·m) | Max On-Torque (N·m) |
|----------|---------------------|---------------------|
| M6 | 0.5 | 3.5 |
| M8 | 0.7 | 5.0 |
| M10 | 1.0 | 7.5 |
| M12 | 1.5 | 10.0 |
| M16 | 3.0 | 18.0 |
| M20 | 5.0 | 28.0 |

Non-metallic insert (nyloc): max on-torque = ~50% of all-metal values.

**Residual preload plateau (Eccles/Boltscience):**
```
F_p_residual ≈ T_prev / (µ_t × r_t × tan(λ + ρ))

DIN 985 M12 nyloc (T_prev = 3–7 N·m):
  F_p_residual ≈ 2–5 kN  (of initial 20–30 kN → 10–25% retained)
```

### 13.3 Torque Margin Analysis (Junker Theorem)

```
Three-torque model (M16, µ = 0.12, F_p ≈ 95 kN):
  T_tighten ≈ 195 N·m
    T_thread   ≈ 120 N·m  (62% — drives nut rotation)
    T_bearing  ≈  75 N·m  (38% — resists nut rotation)

  T_loosen = T_bearing_resist − T_thread_unwind
           = 75 − 90 = −15 N·m  (negative → spontaneous loosening once slip occurs)
```

Negative torque margin is Junker's fundamental theorem: once bearing AND thread surfaces simultaneously slip, the bolt WILL loosen regardless of preload level. Locking devices work by preventing simultaneous slip.

### 13.4 Failure Conditions for Locking Devices

**Nyloc (non-metallic insert):**
- Nylon degrades > 100–120°C → loss of prevailing torque → ineffective
- Each reuse: 10–20% loss of prevailing torque. After 5 reuses: may fall below ISO 2320 minimum
- If operating axial load exceeds the residual preload plateau: full disengagement possible

**All-metal prevailing torque nuts:**
- If pulsating axial load exceeds residual plateau → complete detachment risk
- Degrades with each reuse (less than nyloc, but still degrades)

**Chemical locking (Loctite):**
- Fails above rated temperature (242: 150°C, 243: 150°C oil-tolerant, 263: 200°C)
- Below threshold preload (~4.4 kN for M16): incomplete cure → poor retention
- NASA: acceptable as secondary feature only for flight-critical joints

---

## Sources

**Local documents (C:\Users\leo_r\OneDrive\BPL\Analitical\BAS\Bolted\):**
- Eccles, B. (2011). *Why Nuts and Bolts Can Self-Loosen.* Bolt Science Ltd.
- Bolt Science Ltd. (2003). *Joint Analysis using the BOLTCALC Program.* Training material.
- Bolt Science Ltd. (2024). *Bolting Technology for Engineers and Designers.* Course brochure.
- Bolt Science Ltd. (2003). *Torque Analysis using the BOLTCALC Program.* Training material.
- *Bolted Joint Force-Extension Diagram: Complete Construction Method.* (project document)

**Standards:**
- VDI 2230:2015 — *Systematic calculation of highly stressed bolted joints*
- ASME PCC-1 — *Guidelines for Pressure Boundary Bolted Flange Joint Assembly*
- ASME B16.20 — Spiral Wound Gasket performance

**Web / peer-reviewed:**
- [Preload Stability of Modern Bolted Joints — Athens Journal](https://www.athensjournals.gr/technology/2022-9-3-3-Held.pdf)
- [Bolted Joint Embedding Loss — ResearchHub](https://researchhub.blog/bolted-joint-embedding-loss-calculation-guide)
- [Thermal Effects on Preloaded Joints — Nord-Lock](https://www.nord-lock.com/learnings/bolting-tips/2019/thermal-effects-on-preloaded-joints/)
- [Self-Loosening under Cyclical Temperature — SAGE Journals](https://journals.sagepub.com/doi/full/10.1177/16878140211039428)
- [Clamp Load Loss — Gasket Creep Relaxation, ASME](https://asmedigitalcollection.asme.org/pressurevesseltech/article-abstract/128/3/394/444172)
- [Gasket Relaxation & Retorques — TEADIT](https://teadit.com/us/article/gasket-relaxation-the-importance-of-retorques-in-bolted-flange-joints/)
- [Self-Loosening under Transverse Vibration — Fasten.one](https://fasten.one/self-loosening-of-bolted-joints-under-transverse-vibration/)
- [Self-Loosening Failure Analysis — Wiley / Shock and Vibration](https://onlinelibrary.wiley.com/doi/10.1155/2017/2038421)
- [CTE Mismatch in Bolted Joints — ALLVAR Alloys](https://allvaralloys.com/cte_mismatch_in_bolted_joints/)
- [Review of VDI 2230 Application — PCB/RS Technologies](https://www.pcb.com/Contentstore/mktgcontent/whitepapers/md-0430-revnr-(review-of-the-application-of-design-guideline-vdi-2230-white-paper).pdf)
- [Junker Test — Wikipedia](https://en.wikipedia.org/wiki/Junker_test)

**Peer-reviewed (added 2026-02-22 from web research):**
- Pai, D.H. & Hess, D.P. (2002). *Experimental study of loosening of threaded fasteners due to dynamic shear loads.* Journal of Sound and Vibration, 253(3), 585–602.
- Pai, D.H. & Hess, D.P. (2002). *Three-dimensional finite element analysis of threaded fastener loosening due to dynamic shear load.* Engineering Failure Analysis, 9(4), 383–402.
- Chen, Y. et al. (2017). *Self-Loosening Failure Analysis of Bolt Joints under Vibration considering the Tightening Process.* Shock and Vibration. DOI: 10.1155/2017/2038421.
- Yang, X. et al. (2019). *Experimental Study and Life Prediction of Bolt Loosening Life under Variable Amplitude Vibration.* Shock and Vibration. DOI: 10.1155/2019/2036509.
- Vingsbo, O. & Söderberg, S. (1988). *On fretting maps.* Wear, 126(2), 131–147.
- Fouvry, S. et al. (1996). *Quantification of fretting damage.* Wear, 200(1–2), 186–205.
- [Fretting wear of bolted joint interfaces — ScienceDirect (2020)](https://www.sciencedirect.com/science/article/pii/S004316482030870X)
- [Roles of thread wear on self-loosening of bolted joints — ScienceDirect (2017)](https://www.sciencedirect.com/science/article/abs/pii/S0043164817310670)
- [Review of research on loosening of threaded fasteners — Friction, Springer (2021)](https://link.springer.com/article/10.1007/s40544-021-0497-1)
- [Critical load for preventing rotational loosening — ScienceDirect (2024)](https://www.sciencedirect.com/science/article/abs/pii/S1350630724002632)
- [Prediction of Bolt Loosening Life — PMC / Materials (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11901137/)
- [Mechanism and quantitative evaluation model of slip-induced loosening — ResearchGate](https://www.researchgate.net/publication/340415123)
- Eccles, B. *The loosening of prevailing torque nuts.* Bolt Science Ltd. [PDF](https://www.boltscience.com/pages/the-loosening-of-prevailing-torque-nuts.pdf)
- ISO 2320:2015 — *Prevailing torque steel hexagon nuts — Mechanical and performance properties.*
- ISO 16130:2015 — *Airframe bolting — Dynamic testing of the locking characteristics of bolted joint assemblies under transverse loading conditions (vibration test).*
- NASA-STD-5020B (2021) — *Requirements for Threaded Fastening Systems in Spaceflight Hardware.*

**Companion document:**
- See `LOOSENING_LOADING_CONDITIONS.md` — Loosening under pure axial, shear, bending, and impact loading conditions.
