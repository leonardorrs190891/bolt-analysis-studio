# Similitude Example S2: Multi-Bolt to Single-Bolt Reduction — Flanged Joints

## Overview

**Similitude Type**: MULTI_BOLT_REDUCTION (Tab 5, "Multi-Bolt Reduction" sub-tab)

**Objective**: Reduce multi-bolt flanged joints to equivalent single-bolt MSD models that preserve loosening behavior, enabling efficient analysis in the MSD Builder without modeling every bolt individually.

**Source Data**: Three flanged joint configurations from the paper collection:
- **Case A**: NPS 4" Class 300, 8-bolt, 3/4"-10 UNC — Nechache & Bouzid (2007), Paper 30
- **Case B**: Wind turbine tower flange, 84-bolt, M36 × 4.0 — Badrkhani & Soyoz (2020), Paper 60
- **Case C**: NPS 24" Class 150, 20-bolt, 1-1/8"-8 UNC — Nechache & Bouzid (2007), Paper 30

**Why Multi-Bolt Reduction?**: Bolted flanges have n identical bolts sharing the load. The software's multi-bolt reduction computes an equivalent single bolt that captures the same loosening dynamics, so you can run a single-bolt MSD analysis instead of modeling all n bolts.

---

## Case A: NPS 4" Class 300 — 8-Bolt Petrochemical Flange

### Multi-Bolt Configuration (Prototype)

This is a standard ASME B16.5 flanged connection used in petrochemical piping.

| Parameter | Value | Unit | Notes |
|---|---|---|---|
| Number of bolts (n) | 8 | — | Equally spaced on bolt circle |
| Bolt size | 3/4"-10 UNC | — | SA-193 B7 studs |
| Bolt diameter (d) | 19.05 | mm | 0.750" |
| Thread pitch (p) | 2.54 | mm | 10 TPI |
| Grip length (L) | 85 | mm | Flange + gasket + flange |
| Preload per bolt (F_p) | 65,000 | N | ~70% proof |
| Bolt circle diameter (D_bc) | 190.5 | mm | 7.50" per ASME B16.5 |
| Flange OD | 254.0 | mm | 10.00" |
| Gasket type | PTFE-filled spiral wound | — | |
| μ_thread | 0.12 | — | Oiled |
| μ_bearing | 0.15 | — | |

#### Per-Bolt Properties

| Parameter | Value | Unit |
|---|---|---|
| d₂ (pitch dia.) | 17.399 | mm |
| d₃ (minor dia.) | 15.799 | mm |
| Aₜ (stress area) | 215 | mm² |
| Helix angle λ | 2.66 | ° |
| r_be (eff. bearing) | 11.5 | mm |
| E_bolt | 207,000 | MPa |
| σ_y bolt | 724 | MPa |
| k_bolt (estimated) | 520,000 | N/mm |
| k_member (estimated) | 1,560,000 | N/mm |

#### Material Properties

| Component | Material | E (MPa) | σ_y (MPa) | σ_u (MPa) | ν |
|---|---|---|---|---|---|
| Stud | SA-193 B7 (42CrMo4) | 207,000 | 724 | 862 | 0.30 |
| Nut | SA-194 2H | 207,000 | — | — | 0.30 |
| Flange | SA-105 (carbon) | 207,000 | 250 | 485 | 0.30 |
| Gasket | PTFE-filled SW | varies | — | — | — |

### Equivalent Single Bolt — Software Computation

The software's `reduce_multi_bolt_to_single()` function computes:

| Parameter | Formula | Value | Unit |
|---|---|---|---|
| d_eq | d × √n = 19.05 × √8 | 53.89 | mm |
| p_eq | p × √n = 2.54 × √8 | 7.19 | mm |
| A_t_eq | n × A_t = 8 × 215 | 1,720 | mm² |
| F_p_eq | n × F_p = 8 × 65,000 | 520,000 | N |
| F_t_eq | n × F_t | depends on loading | N |
| k_b_eq | n × k_b = 8 × 520,000 | 4,160,000 | N/mm |
| k_m_eq | n × k_m = 8 × 1,560,000 | 12,480,000 | N/mm |
| L_eq | L (unchanged) | 85 | mm |

**Note**: The equivalent bolt is NOT a real bolt — it's a mathematical construct. d_eq = 53.89 mm doesn't correspond to any standard bolt size. This is intentional.

### Pi Groups for Equivalent Single Bolt

| Pi Group | Name | Multi-Bolt (per bolt) | Equivalent Single | Match? |
|---|---|---|---|---|
| Π₃ | Preload utilization | 0.418 | 0.418 | EXACT |
| Π₄ | Grip ratio (L/d) | 4.46 | 1.58 | Changed (expected) |
| Π₅ | Joint constant (Φ) | 0.250 | 0.250 | EXACT |
| Π₇ | Pitch ratio (p/d) | 0.133 | 0.133 | EXACT |

The grip ratio changes because L stays constant while d grows. This is acceptable because the equivalent bolt preserves the **stiffness ratio** Φ exactly, which is the physically meaningful parameter.

### Creep Relaxation Data (from Paper 30)

At 400°C, NPS 4" Class 300 with B7 bolts:

| Time (hours) | F/F₀ per bolt | Total flange load (kN) | Equivalent single-bolt F/F₀ |
|---|---|---|---|
| 0 | 1.000 | 520 | 1.000 |
| 1 | 0.889 | 462 | 0.889 |
| 10 | 0.756 | 393 | 0.756 |
| 100 | 0.589 | 306 | 0.589 |
| 1,000 | 0.444 | 231 | 0.444 |
| 10,000 | 0.344 | 179 | 0.344 |
| 100,000 | 0.300 | 156 | 0.300 |

**Key principle**: For creep relaxation (no transverse vibration), the equivalent single bolt has EXACTLY the same F/F₀ curve as each individual bolt, because all bolts relax identically under symmetric thermal loading.

### Software Configuration — Multi-Bolt Reduction Panel

Enter these values in Tab 5 → "Multi-Bolt Reduction" sub-tab:

| Field | Value |
|---|---|
| Number of bolts | 8 |
| Bolt diameter | 19.05 mm |
| Thread pitch | 2.54 mm |
| Grip length | 85.0 mm |
| Preload per bolt | 65.0 kN |
| Transverse force | 15.0 kN (total on flange) |
| Bolt circle diameter | 190.5 mm |
| μ_thread | 0.12 |
| μ_bearing | 0.15 |

### MSD Element Chain — Equivalent Single Bolt

After running multi-bolt reduction, transfer to MSD Builder:

```
GROUND — FLANGE(weld neck) — GASKET(PTFE-filled SW) — FLANGE(weld neck) — NUT — THREAD — SHANK — HEAD — GROUND
```

With equivalent parameters:
- F₀ = 520,000 N (total preload)
- k elements scaled by n = 8

### ValidationCase — NPS 4" at 400°C

```python
ValidationCase(
    name="Similitude_S2A_NPS4_8bolt_400C",
    bolt_size="3/4\"-10 UNC × 8 bolts (equiv.)",
    bolt_diameter_mm=53.89,   # equivalent d = 19.05 × √8
    pitch_mm=7.19,            # equivalent p = 2.54 × √8
    initial_preload_N=520000, # total 8 × 65 kN
    preload_percent_yield=41.8,
    transverse_displacement_mm=0.0,
    frequency_Hz=0.0,
    n_cycles=100000,          # hours
    mu_initial=0.12,
    lubricated=True,
    expected_final_preload_ratio=0.300,
    expected_loosening_deg=0.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=1, preload_ratio=0.889),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.756),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.589),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.444),
        ExperimentalDataPoint(cycles=10000, preload_ratio=0.344),
        ExperimentalDataPoint(cycles=100000, preload_ratio=0.300),
    ]
)
```

> **Cycle axis note**: Each "cycle" represents 1 hour of creep exposure at 400°C.

---

## Case B: Wind Turbine Tower Flange — 84-Bolt Ring Flange

### Multi-Bolt Configuration (Prototype)

This represents a typical onshore wind turbine tower section joint.

| Parameter | Value | Unit | Notes |
|---|---|---|---|
| Number of bolts (n) | 84 | — | Ring flange, evenly spaced |
| Bolt size | M36 × 4.0 | — | Class 10.9 HV |
| Bolt diameter (d) | 36.0 | mm | |
| Thread pitch (p) | 4.0 | mm | |
| Grip length (L) | 120 | mm | Flange pair |
| Preload per bolt (F_p) | 510,000 | N | Design target |
| Bolt circle diameter (D_bc) | 3,800 | mm | ~4 m tower section |
| μ_thread | 0.14 | — | Lubricated (MoS₂) |
| μ_bearing | 0.14 | — | Lubricated |

#### Per-Bolt Properties

| Parameter | Value | Unit |
|---|---|---|
| d₂ (pitch dia.) | 33.402 | mm |
| Aₜ (stress area) | 817 | mm² |
| Helix angle λ | 2.18 | ° |
| E_bolt | 210,000 | MPa |
| σ_y bolt | 940 | MPa |
| σ_u bolt | 1,040 | MPa |
| k_bolt (estimated) | 1,430,000 | N/mm |
| k_member (estimated) | 4,290,000 | N/mm |

#### Material Properties

| Component | Material | E (MPa) | σ_y (MPa) | σ_u (MPa) |
|---|---|---|---|---|
| Bolt | 42CrMo4 (10.9) | 210,000 | 940 | 1,040 |
| Flange | S355J2 | 210,000 | 355 | 510 |

### Equivalent Single Bolt — Software Computation

| Parameter | Formula | Value | Unit |
|---|---|---|---|
| d_eq | d × √n = 36 × √84 | 330.0 | mm |
| p_eq | p × √n = 4 × √84 | 36.7 | mm |
| A_t_eq | n × A_t = 84 × 817 | 68,628 | mm² |
| F_p_eq | n × F_p = 84 × 510,000 | 42,840,000 | N |
| k_b_eq | n × k_b = 84 × 1,430,000 | 120,120,000 | N/mm |
| k_m_eq | n × k_m = 84 × 4,290,000 | 360,360,000 | N/mm |
| L_eq | L (unchanged) | 120 | mm |

### Wind Loading → Transverse Force per Bolt

Under IEC 61400-1 extreme wind (V_ref = 50 m/s), the critical bolt position experiences:

| Loading condition | Axial (per bolt) | Transverse (per bolt) | Moment (per bolt) |
|---|---|---|---|
| Normal operation (V=12 m/s) | +15 kN tension | ~5 kN | ~1.5 kN·m |
| Extreme (V=50 m/s) | +85 kN tension | ~25 kN | ~8 kN·m |
| Fatigue (combined) | ±42 kN range | ±12 kN range | — |

For the equivalent single bolt (transverse loosening analysis):
- F_t_eq = n × F_t_per_bolt ≈ 84 × 12 = **1,008 kN** transverse cyclic force
- Or equivalently: the equivalent single bolt sees the total shear demand

### Loosening Assessment

For a wind turbine, the primary concern is preload loss from:
1. **Embedding** (first weeks): ~5-10% loss
2. **Creep** (25-year service): ~5-10% at high preload fractions
3. **Fatigue-induced loosening**: Depends on flange gap behavior

Using Paper 62 data (Norton creep at 90% proof):

| Time (years) | F/F₀ per bolt | Equiv. single-bolt F/F₀ |
|---|---|---|
| 0 | 1.000 | 1.000 |
| 1 | 0.955 | 0.955 |
| 5 | 0.930 | 0.930 |
| 10 | 0.915 | 0.915 |
| 25 | 0.895 | 0.895 |

### Software Configuration — Multi-Bolt Reduction Panel

| Field | Value |
|---|---|
| Number of bolts | 84 |
| Bolt diameter | 36.0 mm |
| Thread pitch | 4.0 mm |
| Grip length | 120.0 mm |
| Preload per bolt | 510.0 kN |
| Transverse force | 1,008 kN (total) |
| Bolt circle diameter | 3,800 mm |
| μ_thread | 0.14 |
| μ_bearing | 0.14 |

### MSD Element Chain — Equivalent Single Bolt

```
GROUND — FLANGE(S355 tower section) — FLANGE(S355 tower section) — NUT — THREAD — SHANK — HEAD — GROUND
```

### ValidationCase — Wind Turbine 25-Year Creep

```python
ValidationCase(
    name="Similitude_S2B_WT_84bolt_M36_creep",
    bolt_size="M36x4.0 × 84 bolts (equiv.)",
    bolt_diameter_mm=330.0,   # equivalent d = 36 × √84
    pitch_mm=36.7,            # equivalent p = 4 × √84
    initial_preload_N=42840000,  # total 84 × 510 kN
    preload_percent_yield=66.4,
    transverse_displacement_mm=0.0,
    frequency_Hz=0.0,
    n_cycles=25,              # years
    mu_initial=0.14,
    lubricated=True,
    expected_final_preload_ratio=0.895,
    expected_loosening_deg=0.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=1, preload_ratio=0.955),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.930),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.915),
        ExperimentalDataPoint(cycles=25, preload_ratio=0.895),
    ]
)
```

> **Cycle axis note**: Each "cycle" represents 1 year of service.

---

## Case C: NPS 24" Class 150 — 20-Bolt Process Flange

### Multi-Bolt Configuration

A large-diameter, low-pressure process piping flange with PTFE sheet gasket.

| Parameter | Value | Unit | Notes |
|---|---|---|---|
| Number of bolts (n) | 20 | — | ASME B16.5 |
| Bolt size | 1-1/8"-8 UNC | — | SA-193 B7 |
| Bolt diameter (d) | 28.575 | mm | 1.125" |
| Thread pitch (p) | 3.175 | mm | 8 TPI |
| Grip length (L) | 110 | mm | Estimated |
| Preload per bolt (F_p) | 80,000 | N | |
| Bolt circle diameter (D_bc) | 635 | mm | 25" |
| Gasket type | PTFE sheet | — | High creep |
| μ_thread | 0.12 | — | |
| μ_bearing | 0.15 | — | |

#### Per-Bolt Properties

| Parameter | Value | Unit |
|---|---|---|
| Aₜ (stress area) | 430 | mm² |
| E_bolt | 207,000 | MPa |
| σ_y bolt | 724 | MPa |
| k_bolt (estimated) | 810,000 | N/mm |
| k_member (estimated) | 2,430,000 | N/mm |

### Equivalent Single Bolt

| Parameter | Formula | Value | Unit |
|---|---|---|---|
| d_eq | d × √n = 28.575 × √20 | 127.8 | mm |
| p_eq | p × √n = 3.175 × √20 | 14.2 | mm |
| A_t_eq | n × A_t = 20 × 430 | 8,600 | mm² |
| F_p_eq | n × F_p = 20 × 80,000 | 1,600,000 | N |
| k_b_eq | n × k_b = 20 × 810,000 | 16,200,000 | N/mm |
| k_m_eq | n × k_m = 20 × 2,430,000 | 48,600,000 | N/mm |

### PTFE Gasket Creep Data (from Paper 30)

PTFE gaskets are highly creep-susceptible. At 200°C:

| Time (hours) | F/F₀ per bolt | Total flange load (kN) | Equiv. F/F₀ |
|---|---|---|---|
| 0 | 1.000 | 1,600 | 1.000 |
| 10 | 0.820 | 1,312 | 0.820 |
| 100 | 0.680 | 1,088 | 0.680 |
| 1,000 | 0.540 | 864 | 0.540 |
| 10,000 | 0.430 | 688 | 0.430 |
| 100,000 | 0.350 | 560 | 0.350 |

**Critical observation**: After 100,000 hours (~11.4 years), 65% of preload is lost due to PTFE gasket creep. This has severe sealing implications — the required gasket stress for leak-tightness may not be maintained.

### Software Configuration — Multi-Bolt Reduction Panel

| Field | Value |
|---|---|
| Number of bolts | 20 |
| Bolt diameter | 28.575 mm |
| Thread pitch | 3.175 mm |
| Grip length | 110.0 mm |
| Preload per bolt | 80.0 kN |
| Transverse force | 0.0 kN (creep analysis) |
| Bolt circle diameter | 635.0 mm |
| μ_thread | 0.12 |
| μ_bearing | 0.15 |

### MSD Element Chain — Equivalent Single Bolt with Gasket

```
GROUND — FLANGE(weld neck, SA-105) — GASKET(PTFE sheet) — FLANGE(weld neck, SA-105) — NUT — THREAD — SHANK — HEAD — GROUND
```

### ValidationCase — NPS 24" at 200°C

```python
ValidationCase(
    name="Similitude_S2C_NPS24_20bolt_PTFE_200C",
    bolt_size="1-1/8\"-8 UNC × 20 bolts (equiv.)",
    bolt_diameter_mm=127.8,   # equivalent d = 28.575 × √20
    pitch_mm=14.2,            # equivalent p = 3.175 × √20
    initial_preload_N=1600000, # total 20 × 80 kN
    preload_percent_yield=25.7,
    transverse_displacement_mm=0.0,
    frequency_Hz=0.0,
    n_cycles=100000,          # hours
    mu_initial=0.12,
    lubricated=True,
    expected_final_preload_ratio=0.350,
    expected_loosening_deg=0.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.820),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.680),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.540),
        ExperimentalDataPoint(cycles=10000, preload_ratio=0.430),
        ExperimentalDataPoint(cycles=100000, preload_ratio=0.350),
    ]
)
```

> **Cycle axis note**: Each "cycle" represents 1 hour of creep exposure at 200°C.

---

## When Multi-Bolt Reduction Works Best

### Ideal Conditions (error < 5%)
1. **Symmetric loading**: All bolts experience the same conditions (creep, thermal, internal pressure)
2. **No bolt-to-bolt interaction**: Elastic interaction negligible after tightening
3. **Uniform preload**: All bolts at same initial preload (±5%)
4. **Creep/relaxation analysis**: Time-based preload loss without transverse vibration

### Conditions Requiring Caution (error 5-20%)
1. **Bending on flange**: Not all bolts see the same axial load (windward vs. leeward in wind turbines)
2. **Preload scatter**: If initial preload varies >10% between bolts
3. **Transverse vibration**: Individual bolt response may differ from equivalent single bolt
4. **Sequential tightening effects**: Elastic interaction cross-talk

### When NOT to Use Multi-Bolt Reduction
1. **Individual bolt failure assessment**: Need per-bolt stress for fatigue analysis
2. **Flange gap / opening analysis**: Requires flange bending model
3. **Leak rate calculation**: Requires gasket contact pressure distribution
4. **Non-uniform thermal loading**: Different bolts at different temperatures

---

## Comparison: Multi-Bolt Reduction vs. Geometric Scaling

| Aspect | Multi-Bolt Reduction (S2) | Geometric Scaling (S1) |
|---|---|---|
| **Purpose** | n bolts → 1 equivalent bolt | Large bolt → small bolt lab test |
| **Scale factor** | √n (bolt count) | λ (geometric ratio) |
| **Preserves** | Stiffness ratio, preload utilization | All Pi groups (approximately) |
| **Distorts** | Grip ratio (L/d_eq changes) | Pitch ratio (standard sizes) |
| **Typical use** | Flanged joint → MSD Builder analysis | Prototype → lab validation test |
| **Corrections** | None (exact for symmetric loading) | Friction, embedding, roughness |
| **Accuracy** | Exact for uniform conditions | ±5-15% depending on λ |

---

## Combined Application: Scale Model of Multi-Bolt Flange

The two modes can be combined sequentially:

**Step 1**: Reduce 84-bolt M36 wind turbine flange to equivalent single bolt
- Equivalent d = 330 mm, F_p = 42,840 kN

**Step 2**: Scale the equivalent single bolt down for lab testing
- λ = 0.05 → Model diameter ≈ 16.5 mm → use M16
- Model preload ≈ λ² × 42,840 = 107 kN (reasonable for M16!)
- Model frequency = f/λ = 0.1/0.05 = 2 Hz (for fatigue-equivalent loading)

This combined approach allows testing a **single M16 bolt** to predict the loosening behavior of an entire 84-bolt M36 wind turbine ring flange.

---

## References

- **NPS 4" flange data**: Nechache, A.; Bouzid, A. H. (2007). "Creep analysis of bolted flange joints." *Int. J. Pressure Vessels and Piping*, 84(3), 185–194.
- **Wind turbine bolt data**: Badrkhani Ajaei, B.; Soyoz, S. (2020). "Effects of preload deficiency on fatigue demands of wind turbine tower bolts." *J. Constructional Steel Research*, 166, 105933.
- **Norton creep data**: Wang et al. (2025). "Fatigue assessment for tower bolts of floating offshore wind turbine considering preload loss due to ambient temperature creep."
- **Tightening sequence**: Coria, I. et al. (2020). "Achieving uniform bolt preload distribution in bolted flanged connections." *Int. J. Pressure Vessels and Piping*, 182, 104054.
- **VDI reference**: VDI 2230 Part 1 (2015). *Systematic calculation of highly stressed bolted joints*.
