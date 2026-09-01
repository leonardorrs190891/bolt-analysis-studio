# Bolted Joint Loosening Under Different Loading Conditions
## Quantitative Reference — Loading-Type-Specific Mechanisms

*Companion to `LOOSENING_MECHANISMS_QUANTITATIVE.md`*
*Compiled 2026-02-22 from web research and peer-reviewed literature.*

---

## Overview: Loading Condition Severity Ranking

| Loading Type | Loosening Severity | Mechanism | Typical Cycles to 50% Loss |
|-------------|-------------------|-----------|---------------------------|
| **Transverse (Junker)** | ★★★★★ Highest | Rotational (bearing+thread slip) | 10²–10³ |
| **Combined transverse+torsion** | ★★★★★ Highest | Multiple slip paths | < 10² |
| **Bending/eccentric** | ★★★★ High | Local slip; prying | 10³–10⁴ |
| **Impact/shock (repeated)** | ★★★★ High | Embedding + cyclic ratcheting | 10–10² |
| **Axial dynamic (cyclic tension)** | ★★★ Moderate | Non-rotational; no rotation | > 10⁴ |
| **Torsional (rotational vibration)** | ★★★ Moderate | Direct angular loosening | 10³–10⁴ |
| **Axial static (sustained)** | ★★ Low | Stress relaxation only | N/A (time) |
| **Pure shear, bearing-type joint** | ★★★★ High | Bolt moves in hole; fretting | 10³–10⁵ |
| **Pure shear, friction-type joint** | ★★ Low | Friction transfer; embedment | > 10⁵ if F_p maintained |

---

## 1. Pure Axial Loading

### 1.1 What Axial Loading Does (and Does Not Do)

**Critical finding (Junker 1969; Sauer et al. 1950; confirmed by all subsequent research):**

> Purely axial cyclic loading does **NOT** cause rotational self-loosening.

Axial excitation causes cyclic preload fluctuation (tension increase and decrease) but no cumulative nut rotation. The mechanism is fundamentally different from transverse loading.

**Why axial loading cannot cause Junker-type loosening:**
- Thread helix requires a **circumferential torque component** to drive nut rotation
- Pure axial load creates no circumferential force at the thread contact
- The bolt bending/shear compliance that couples transverse→torsional DOF is absent

**What axial loading does cause:**
1. **Cyclic bolt tension fluctuation:** ΔF_bolt = Φ × F_axial_amplitude (elastic, reversible)
2. **Fatigue damage:** at high cycle counts if stress range exceeds endurance limit
3. **Preload scatter amplification:** if axial dynamic load approaches or exceeds joint separation load
4. **Ratcheting** (if applied load approaches yield): irreversible plastic elongation → preload loss

### 1.2 Quantitative Axial Load Effects

**Bolt tension variation under cyclic axial load:**
```
F_bolt(t) = F₀ + Φ × F_A × sin(ωt)   [while joint remains clamped]

where:
  Φ = k_b / (k_b + k_m) = load factor
  Typical Φ = 0.05–0.20 (metal-to-metal joints)
  Typical Φ = 0.30–0.60 (joints with soft gaskets)

Clamp force variation:
  F_clamp(t) = F₀ − (1−Φ) × F_A × sin(ωt)
```

**Joint separation criterion:**
```
F_A_sep = F₀ / (1 − Φ)    [external axial load to cause separation]

Example (M16, F₀ = 50 kN, Φ = 0.15):
  F_A_sep = 50 / 0.85 = 58.8 kN
```

**Preload loss from repeated axial overload (Nassar, 2005):**
External axial load causes irreversible plastic deformation of the bolt material. Under high-amplitude axial cycling near yield, this is the dominant non-rotational preload loss mechanism.

```
Approximate ratcheting loss per cycle (cyclic axial load > 0.8 × F_yield):
  ΔF_plastic_per_cycle ≈ 0.5–2% of F_p   (depends on material, stress ratio)
```

### 1.3 Comparison: Axial vs. Transverse Loosening Rate

From Junker (1969) and confirmation by Sauer, Clark-Cook, and subsequent researchers:

| Parameter | Axial Vibration | Transverse Vibration |
|-----------|----------------|---------------------|
| Nut rotation? | None | Yes (drives loosening) |
| Cycles to 50% preload loss | > 100 000 (if any) | 100–1 000 |
| Mechanism | Plastic elongation + fatigue | Junker rotational |
| F_A required for loosening | Must exceed F_A_sep | Only 46–66% of µ×F_p |
| Reversible? | Yes (below yield) | No (nut rotates) |

**Severity ratio:** Transverse loading causes ~10×–100× faster preload loss than equivalent-force axial loading.

### 1.4 Axial Loading Stage Progression

Under pure axial excitation (F_A < F_sep), the loosening stages are:

```
Stage A1 — STABLE (elastic cycling, N < 10⁴)
  F_p/F_p0 ≈ 0.90–1.00
  No nut rotation; preload fluctuates but returns to baseline

Stage A2 — RATCHETING (if F_A > 0.8 × F_yield, N = 10⁴–10⁶)
  F_p/F_p0 gradually decreasing: 0.70–0.90
  No nut rotation; slow irreversible bolt elongation

Stage A3 — FATIGUE (N > endurance limit cycles)
  Crack initiation at thread root
  If fracture: sudden complete loss
  Preload loss: 0% until fracture, then 100%
```

**Design rule:** Under pure axial dynamic loading, size the joint for fatigue (bolt stress range), not self-loosening. Use σ_a < σ_endurance / S_F (S_F ≥ 1.5 for critical joints).

---

## 2. Shear / Transverse Loading — Joint Type Comparison

### 2.1 Bearing-Type Shear Joints (Bolt Carries Shear Directly)

In a **bearing-type** joint, the connected members move until the bolt shank contacts the hole walls.
The shear load is carried by bolt bearing stress (bolt vs. hole), not by friction.

**Loosening mechanism:** The relative slip between bolt and hole wall drives fretting.
The cyclic shear force creates a transverse displacement of the bolt shank → this IS the Junker mechanism.

**Quantitative behavior:**
- Shear load is transferred without requiring clamping force
- BUT the bolt shank movement under cyclic load → transverse microslip at thread and bearing → loosening
- Loosening rate depends on displacement amplitude of the bolt shank in the hole

**Preload retention:** Poor. Bearing-type joints allow bolt movement → high loosening risk.

```
Slip onset (Pai & Hess):
  F_shear_onset ≈ 0.46 × µ × F_p  (localized slip threshold)
  Full slip:      F_shear = µ × F_p  (classical Junker)

At 2 mm tangential displacement amplitude:
  Complete loosening within ~50 cycles (ScienceDirect 2024, tangential cyclic load study)
```

### 2.2 Friction-Type Shear Joints (Slip-Resistant)

In a **friction-type** (slip-resistant) joint, shear is transferred entirely by friction:
```
F_shear_max = µ × F_p × n_shear_planes    [no-slip condition]
```

The bolt shank never contacts the hole wall. If F_p is maintained → no bolt movement → no Junker loosening.

**Quantitative behavior:**
- If F_p is maintained above the friction slip threshold: STABLE
- Preload loss is only from embedding, relaxation (non-rotational mechanisms)
- If friction slip occurs (F_shear > µ × F_p × n): joint slips → bearing-type behavior → rapid loosening

**Preload requirements for friction joints:**
```
Required minimum clamp force:
  F_p_min = (F_shear / n_shear_planes) / µ × SF_slip

Typical SF_slip = 1.2–1.5 (structural) or 1.8–2.0 (critical)

Example (F_shear = 50 kN, µ = 0.30, n = 2, SF = 1.5):
  F_p_min = (50 000 / 2) / 0.30 × 1.5 = 125 000 N = 125 kN
```

**Critical finding for friction joints (corrosion effect):**
Specimens in seawater (10-year exposure): 92.1% preload loss. Loss of friction → joint converts from friction-type to bearing-type → high loosening risk.

### 2.3 Preload Decay Rate Comparison

Under 0.25 mm tangential cyclic displacement amplitude (ScienceDirect, PMC studies):

| Cycle Count | Bearing-Type F_p/F_p0 | Friction-Type (intact) F_p/F_p0 |
|-------------|----------------------|--------------------------------|
| 0 | 1.00 | 1.00 |
| 10 | 0.85 | 0.95 |
| 50 | 0.60 | 0.88 |
| 100 | 0.35–0.45 | 0.82 |
| 1 000 | 0.10–0.20 | 0.78 |

At 2 mm amplitude: bearing-type complete loosening within 50 cycles.
At 0.25 mm amplitude: ~22% preload loss after 100 cycles in bearing-type joints.

---

## 3. Bending / Eccentric Loading

### 3.1 Physical Mechanism

A bending moment M applied to the joint creates a **non-uniform normal pressure** across the bearing annulus:
- Tension side: local contact pressure decreases → slips first
- Compression side: local contact pressure increases → remains stuck

The effective transverse force threshold for slip is **lower** than for uniform preload:

```
F_trans_eff = F_trans + M / r_eff   (tension-side equivalent transverse force)

where r_eff = effective bearing radius (≈ 0.5 × (D_outer + D_inner) / 2)

For 10% asymmetric normal force distribution:
  Effective slip threshold drops by ~8–12% compared to concentric loading
```

### 3.2 Prying Action Under Bending

For a stiff flange loaded eccentrically (prying factor n):

```
Eccentric load factor:
  n = 0   → load at clamping interface (no prying, favorable)
  n = 0.5 → load at mid-plane of clamped parts (typical)
  n = 1   → load at bolt head/nut plane (maximum prying, unfavorable)

Modified stiffness ratio:
  Φ_n = n × Φ   (effective load factor under eccentric loading)

Clamp force with prying:
  F_clamp(F_A) = F₀ − (1 − Φ_n) × F_A
```

For n = 1 and Φ = 0.15: Φ_n = 0.15, but the clamp force drops faster than for central loading.

### 3.3 Bending-Induced Bolt Stress

Bolt bending stress (ASME/NASA analysis):
```
σ_bending = M_bolt × (d/2) / I_bolt

M_bolt = M_ext × (k_b / (k_b + k_m)) × (e / L_grip)

where e = eccentricity of load from bolt axis
```

Bending stress **adds to** tensile stress from preload and reduces fatigue life:
```
Total bolt stress = σ_preload + σ_bending + σ_cyclic
```

At σ_bending > 20% of σ_preload: fatigue life may be reduced by factor of 3–5× versus concentric loading.

### 3.4 Bending Loading Stage Progression

```
Stage B1 — STABLE (M < M_slip_threshold)
  Non-uniform pressure but no slip anywhere
  Same as axial loading; only non-rotational mechanisms

Stage B2 — LOCALIZED SLIP (M > M_crit on tension side)
  Partial slip on tension side of bearing annulus
  NON-ROTATIONAL → TRANSITION boundary
  F_p/F_p0 ≈ 0.75–0.90

Stage B3 — PROGRESSIVE SLIP (cyclic bending)
  Each bending cycle advances the slip annulus circumferentially
  Equivalent to Pai-Hess localized slip → rotational loosening initiates
  F_p/F_p0 ≈ 0.55–0.75

Stage B4 — ROTATIONAL LOOSENING
  Full bearing surface slip (alternating tension/compression faces)
  Identical to transverse Junker mechanism from here
```

**Key insight (from ScienceDirect 2024):** Bending of the bolt shank *limits* self-loosening compared to pure shear, because bending stiffness resists the rotation that drives loosening. However, the bending stress concentration at the thread root accelerates fatigue failure.

### 3.5 Design Guidance for Bending Loads

```
Minimum preload to prevent bending-induced loosening:
  F_p_min = (F_trans + M/r_eff) / µ × 1.5   (with SF = 1.5)

For cyclic bending: check BOTH loosening criterion AND fatigue:
  σ_a / σ_endurance + F_p_loss / F_p ≤ 1.0
```

---

## 4. Impact / Shock Loading

### 4.1 Single-Impact Preload Loss

**Embedding type (asperity collapse — occurs on first impact):**
- Metal-to-metal, no coating: **2–5% of F_p**
- Coated surfaces or gasket: **5–10% of F_p**
- Subsequent impacts on same surface: **< 1% per event** (asperities already collapsed)

**VDI 2230 embedding allowance** (per interface, applicable to each new contact):
```
ΔF_embed_impact = k_sys × f_Z_per_interface

Metal-to-metal:  f_Z ≈ 2–5 µm per interface
With gasket:     f_Z ≈ 10–50 µm per interface
Painted:         f_Z ≈ 50–100 µm per interface
```

**Preload loss per M16 impact event (k_sys = 400 kN/mm, 4 interfaces, Rz = 10 µm):**
```
f_Z_total = 4 × 3 µm = 12 µm
ΔF_embed = 400 × 12 = 4 800 N  (9.6% of 50 kN preload)
```

### 4.2 Repeated Impact — Accumulative Preload Loss

Impact loading that generates transverse displacement at the joint interface → Junker mechanism applies:

**From ScienceDirect (2020), threaded connection under compressive impact:**
- Hopkinson bar experiments: "tightening-loosening alternation" — each impact half-cycle can loosen or tighten
- The pressure wave reflects at the free end → tension wave → cyclic preload oscillation
- Under repeated tensile pulses: cumulative preload loss (non-rotational ratcheting)

**Quantitative loosening thresholds under repeated impact:**
```
Dividing criterion (from PMC literature review):
  - Early stage loosening vs. continued self-loosening: 0.5° nut rotation
  - Total loosening criterion: preload < 10% of initial value (F_p/F_p0 < 0.10)

Under tangential impact (0.25 mm amplitude, 100 cycles):
  Preload loss ≈ 22%  (PMC/ScienceDirect 2024)

Under tangential impact (2.0 mm amplitude, 50 cycles):
  Complete loosening (100% loss)  (ScienceDirect 2024)
```

### 4.3 Approximate Single-Impact Formula

For a low-velocity impact (v < 5 m/s) on an M16 bolt:

```
Permanent deformation per impact:
  δ_permanent ≈ 1–5 µm  (function of material hardness, impact energy)

Preload loss:
  ΔF_p_impact = k_sys × δ_permanent
  ≈ 400 kN/mm × (1–5 × 10⁻³ mm) = 0.4–2.0 kN per impact event

As fraction of 50 kN preload: 0.8–4.0% per impact
```

After first impact (asperities collapsed): each subsequent impact causes < 0.5% additional loss from embedding alone.

**If impact causes transverse displacement > 0.5 mm:**
Junker mechanism activates → use rotational loosening model from §12 of main document.

### 4.4 Impact Stage Progression

```
Stage I1 — FIRST IMPACT (instantaneous)
  Rapid embedding: 2–10% preload loss
  F_p/F_p0 = 0.90–0.98 after first event

Stage I2 — REPEATED SMALL IMPACTS (δ_trans < slip threshold)
  Only non-rotational losses: embedding (saturates), fretting
  F_p/F_p0 slowly declining: 0.75–0.90 over 10²–10³ events

Stage I3 — REPEATED LARGE IMPACTS (δ_trans > slip threshold = µ × F_p / k_joint)
  Junker mechanism activates each impact cycle
  F_p/F_p0 rapidly falling: 0.55→0.20 within 10–100 impacts
  ROTATIONAL → RUNAWAY phase

Stage I4 — COMPLETE LOOSENING
  F_p/F_p0 < 0.10; nut may detach on subsequent impact
```

### 4.5 Impact Design Guidance (NASA-STD-5020B)

- All joints subject to impact loads: **mandatory locking feature** required
- Preferred: positive mechanical retention (safety wire, castle nut) for high-impact environments
- Chemical locking (Loctite) acceptable as secondary feature only if primary mechanical lock is present
- Vibration/impact qualification testing required per MIL-STD-810 or equivalent spectrum

---

## 5. Combined Loading Interaction

### 5.1 Axial + Transverse Interaction

Axial cyclic load reduces instantaneous clamping force → lowers the slip threshold for transverse loads:

```
Instantaneous slip threshold:
  F_slip_threshold(t) = µ × F_clamp(t) = µ × [F₀ − (1−Φ) × F_A × sin(ωt)]

During peak axial phase (F_A positive):
  F_clamp,min = F₀ − (1−Φ) × F_A    [most vulnerable instant]
  F_slip,min  = µ × F_clamp,min

If simultaneous transverse force F_T > F_slip,min: loosening initiates
```

**Worst case interaction:** When F_A is tensile (reducing clamp force) AND F_T is at peak — a common scenario in structural joints under combined service loads.

**Engineering rule of thumb:**
```
Combined check (conservative):
  F_T / (µ × F₀) + F_A / F_sep ≤ 1.0   (interaction margin = 1.0 at boundary)
```

### 5.2 Torsional + Transverse Loading

Under combined torsional and transverse displacement loading (2023–2024 research, ScienceDirect):

- Loosening initiates **before** the pure-transverse threshold is reached
- No standardized closed-form formula, but FEA shows approximately **elliptical interaction boundary**:

```
(F_T / F_T_crit)² + (M_T / M_T_crit)² ≤ 1.0   (approximate interaction diagram)
```

For pure torsional vibration: direct angular loosening drives nut rotation without need for transverse force.

### 5.3 VDI 2230 Combined Loading Framework

VDI 2230 decomposes loading into: F_A (axial), F_Q (transverse), M_T (torque), M_B (bending).

**Slip check:** All components checked independently (conservative — does not account for synergistic effects).
```
Minimum preload for friction slip resistance:
  F_p_min = (F_Q / (µ × n_friction_surfaces)) × SF_slip

where SF_slip = 1.2–1.5 (structural) or 1.8–2.0 (critical/pressure-retaining)
```

**Separation check:** Bolt load must not exceed joint separation load under combined axial + bending:
```
F_A + M_B / r_bolt < F₀ × (1 − Φ)
```

### 5.4 Superposition of Preload Loss Mechanisms

For combined loading conditions, preload loss mechanisms superpose (approximately independent):

```python
F_p_total(N, t) = F₀
  − ΔF_embed(N)         # embedding: 2–10%, saturates in 10–50 cycles
  − ΔF_relaxation(t)    # relaxation: logarithmic, time-dependent
  − ΔF_gasket(t)        # gasket creep: if present
  − ΔF_rotational(N)    # Junker: only if F_trans > 0.46 × µ × F_p_current
  − ΔF_fretting(N)      # wear: slow, cumulative
  − ΔF_thermal(N_th)    # thermal ratcheting: if ΔT cycling
  − ΔF_impact(N_imp)    # impact embedding: diminishing per event
```

**Order of dominance:**
1. Initial: Embedding + relaxation (cycles 1–50, time 0–24 h)
2. Early service: Rotational loosening (if above threshold) — overtakes all others
3. Long-term: Fretting wear + stress relaxation — if rotational prevented

---

## 6. Loading-Specific BAS Software Configuration Guide

| Loading Condition | Recommended Load Type | Key Parameters | Stage Progression |
|------------------|----------------------|----------------|-------------------|
| Pure axial tension | AXIAL_TENSION | F_A amplitude, Φ, F₀/F_yield | A1 → A2 → A3 (fatigue) |
| Transverse/Junker | TRANSVERSE | δ_amplitude, µ, frequency | STABLE → NON_ROT → ROT → RUNAWAY |
| Bending + transverse | ECCENTRIC | M_B, e, r_eff, F_T | B1 → B2 → B3 → ROT |
| Impact (single) | IMPACT | v_impact, material, n_events | I1 → stable |
| Repeated impact | IMPACT + TRANSVERSE | δ_per_impact, n_events, µ | I1 → I2 → I3 |
| Combined service | COMBINED | All of the above | Superposition model §5.4 |

### Simulation Recommendations by Loading Type

**Pure axial:**
- Use time integration (Newmark-β) with Φ-weighted external force
- Monitor: F_p ratio, bolt stress amplitude for fatigue check
- Critical output: stress ratio R = σ_min/σ_max, compare to S-N curve

**Transverse (Junker):**
- Use coupled loosening analyzer with Pai-Hess corrected slip threshold (0.46–0.66 × µ × F_p)
- Monitor: nut rotation angle, phase (STABLE/NON-ROT/TRANSITION/ROTATIONAL/RUNAWAY)
- Critical output: loosening rate dθ/dN, cycles to RUNAWAY

**Bending:**
- Apply as eccentric axial + transverse equivalent force
- Use r_eff to compute local slip threshold: F_slip_local = µ × F_p × (1 − M_B / (F_p × r_eff))
- Monitor: local bearing pressure distribution, partial slip index

**Impact:**
- Apply as single-cycle high-amplitude transverse excitation
- If δ_impact > δ_slip: each impact = 1 loosening cycle
- Monitor: cumulative embedding + rotational loss per impact event

---

## 7. Quantitative Transition Criteria — Summary Table

| Criterion | Threshold | Source | Phase Transition |
|-----------|-----------|--------|-----------------|
| Nut rotation | 0.5° cumulative | Chen 2017 | NON-ROT → ROT |
| Preload ratio | 0.75 | Synthesized | STABLE → NON-ROT |
| Preload ratio | 0.55 | Synthesized | NON-ROT → ROT |
| Preload ratio | 0.20 | Synthesized | ROT → RUNAWAY |
| ISO 16130 acceptance | ≥ 0.80 at 2 000 cycles | ISO 16130:2015 | Pass/Fail |
| Slip onset (Pai-Hess) | 46–66% of µ×F_p | Pai & Hess 2002 | STABLE → TRANSITION |
| Self-locking condition | tan(λ) < µ×cos(α) | Thread mechanics | Irreversible loosening boundary |
| Fretting: stick→partial | δ < 5 µm | Vingsbo-Söderberg 1988 | No wear → fretting fatigue |
| Fretting: partial→gross | δ > 50 µm | Vingsbo-Söderberg 1988 | Archard wear regime |
| Fretting wear µ loss | 20–40% after 5 000 cycles | ScienceDirect 2017 | Self-locking condition approach |
| Axial loosening criterion | F_A > F_sep = F₀/(1−Φ) | VDI 2230 / NASA | Joint separation |
| Impact: total loosening | F_p/F_p0 < 0.10 | Literature review | RUNAWAY |

---

## Sources

- Junker, G.H. (1969). *New Criteria for Self-Loosening of Fasteners Under Vibration.* SAE Paper 690055.
- Pai, D.H. & Hess, D.P. (2002). *Experimental study of loosening of threaded fasteners due to dynamic shear loads.* JSV 253(3), 585–602.
- Chen, Y. et al. (2017). *Self-Loosening Failure Analysis of Bolt Joints under Vibration.* Shock and Vibration. DOI:10.1155/2017/2038421.
- Yang, X. et al. (2019). *Experimental Study and Life Prediction of Bolt Loosening Life under Variable Amplitude Vibration.* Shock and Vibration.
- Vingsbo, O. & Söderberg, S. (1988). *On fretting maps.* Wear, 126(2), 131–147.
- Nassar, S.A. & Housari, B.A. (2006). *Study of the Effect of Hole Clearance and Thread Fit on the Self-Loosening of Threaded Fasteners.* ASME J. Mech. Design.
- VDI 2230:2015. *Systematic calculation of highly stressed bolted joints.*
- NASA-STD-5020B (2021). *Requirements for Threaded Fastening Systems in Spaceflight Hardware.*
- NASA TM 106943. *Preloaded Joint Analysis Methodology for NASA Launch Vehicles.*
- ISO 16130:2015. *Airframe bolting — Dynamic testing of locking characteristics under transverse loading.*
- ISO 2320:2015. *Prevailing torque steel hexagon nuts.*
- [Preload loss of high-strength bolts in friction connections — ScienceDirect 2022](https://www.sciencedirect.com/science/article/abs/pii/S1350630722003909)
- [Prediction of Pre-Loading Relaxation under Tangential Cyclic Load — PMC 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11174751/)
- [Loosening of threaded connection under axial compressive impact — ScienceDirect 2020](https://www.sciencedirect.com/science/article/abs/pii/S0734743X20307338)
- [Critical load for preventing rotational loosening — ScienceDirect 2024](https://www.sciencedirect.com/science/article/abs/pii/S1350630724002632)
- [Fretting wear of bolted joint interfaces — ScienceDirect 2020](https://www.sciencedirect.com/science/article/pii/S004316482030870X)
- [Roles of thread wear on self-loosening — ScienceDirect 2017](https://www.sciencedirect.com/science/article/abs/pii/S0043164817310670)
- [Review of research on loosening of threaded fasteners — Friction, Springer 2021](https://link.springer.com/article/10.1007/s40544-021-0497-1)
- [Prediction of Bolt Loosening Life — PMC / Materials 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC11901137/)
- Eccles, B. *The loosening of prevailing torque nuts.* Bolt Science Ltd. [boltscience.com](https://www.boltscience.com/pages/the-loosening-of-prevailing-torque-nuts.pdf)
- [Experimental study: time-related preload relaxation under vibration in different directions — ScienceDirect 2019](https://www.sciencedirect.com/science/article/abs/pii/S0301679X19305225)
- [Bending Effect in Concentric Bolted Joints Under Transverse Load — ResearchGate](https://www.researchgate.net/publication/267596066)
