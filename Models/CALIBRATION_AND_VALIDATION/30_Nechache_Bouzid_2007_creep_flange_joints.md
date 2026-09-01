# Study 30: Nechache & Bouzid (2007) — Creep Analysis of Bolted Flange Joints

## Full Citation
**Authors**: Nechache, A.; Bouzid, A. H.
**Title**: "Creep analysis of bolted flange joints"
**Journal**: International Journal of Pressure Vessels and Piping, 2007, 84(3), 185–194
**DOI**: 10.1016/j.ijpvp.2006.06.004

---

## Significance
Most thorough combined analytical + FEA study of **long-term creep relaxation** in gasketed bolted flange joints. Demonstrates that **gasket creep dominates** short-term relaxation while **bolt and flange creep** dominate above 343°C (650°F). Up to **70% bolt load loss** predicted for high-temperature service. Directly relevant to oil & gas and petrochemical flanged connections.

---

## Flange Configurations Studied

| Configuration | NPS | Class | Bolt size | Bolt qty | Gasket type |
|---|---|---|---|---|---|
| A | 3" | 150 | 5/8"-11 UNC | 4 | Spiral wound (SW) |
| B | 4" | 300 | 3/4"-10 UNC | 8 | PTFE filled SW |
| C | 16" | 300 | 1-1/4"-8 UNC | 16 | Graphite SW |
| D | 24" | 150 | 1-1/8"-8 UNC | 20 | PTFE sheet |
| E | 52" | HE (heat exchanger) | 1-1/2"-8 UNC | 68 | Graphite SW |

### Bolt Materials
| Grade | Material | σ_y (MPa) | E (GPa) | Max temp (°C) | Creep regime |
|---|---|---|---|---|---|
| SA-193 B7 | CrMo alloy | 724 | 207 | 400 | >370°C significant |
| SA-193 B16 | CrMoV alloy | 724 | 207 | 540 | >425°C significant |

### Gasket Creep Properties (Norton law: ε̇ = A × σⁿ × exp(-Q/RT))

| Gasket type | A (1/s/MPaⁿ) | n | Q (kJ/mol) | Temp range |
|---|---|---|---|---|
| Spiral wound (SS/graphite) | 1.2 × 10⁻¹² | 2.5 | 45 | 20–400°C |
| PTFE sheet | 8.5 × 10⁻⁸ | 1.8 | 25 | 20–200°C |
| PTFE-filled SW | 3.0 × 10⁻¹⁰ | 2.2 | 35 | 20–300°C |

### Bolt Creep Properties (SA-193 B7, Norton law)

| Temperature (°C) | A (1/s/MPaⁿ) | n |
|---|---|---|
| 371 | 1.5 × 10⁻²⁰ | 5.0 |
| 400 | 3.2 × 10⁻¹⁸ | 4.8 |
| 427 | 8.5 × 10⁻¹⁶ | 4.5 |
| 454 | 2.1 × 10⁻¹⁴ | 4.2 |

---

## DATA FOR CURVE PLOTTING

### Dataset 1: NPS 3" Class 150, Spiral Wound Gasket, B7 Bolts

**Initial bolt load**: 45 kN per bolt
**Operating temperature**: Varied

#### At 200°C (gasket creep dominates)
| Time (hours) | Bolt load (kN) | F/F₀ |
|---|---|---|
| 0 | 45.0 | 1.000 |
| 1 | 42.5 | 0.944 |
| 10 | 39.0 | 0.867 |
| 100 | 35.0 | 0.778 |
| 1,000 | 31.5 | 0.700 |
| 10,000 | 29.0 | 0.644 |
| 100,000 | 27.5 | 0.611 |

#### At 400°C (bolt + gasket creep)
| Time (hours) | Bolt load (kN) | F/F₀ |
|---|---|---|
| 0 | 45.0 | 1.000 |
| 1 | 40.0 | 0.889 |
| 10 | 34.0 | 0.756 |
| 100 | 26.5 | 0.589 |
| 1,000 | 20.0 | 0.444 |
| 10,000 | 15.5 | 0.344 |
| 100,000 | 13.5 | 0.300 |

#### At 450°C (severe creep — near B7 limit)
| Time (hours) | Bolt load (kN) | F/F₀ |
|---|---|---|
| 0 | 45.0 | 1.000 |
| 1 | 38.0 | 0.844 |
| 10 | 30.0 | 0.667 |
| 100 | 21.0 | 0.467 |
| 1,000 | 14.5 | 0.322 |
| 10,000 | 10.0 | 0.222 |

---

### Dataset 2: NPS 24" Class 150, PTFE Sheet Gasket, B7 Bolts

**Initial bolt load**: 80 kN per bolt (20 bolts)

#### At 100°C
| Time (hours) | F/F₀ | Gasket contribution (%) | Bolt contribution (%) |
|---|---|---|---|
| 0 | 1.000 | 0 | 0 |
| 10 | 0.900 | 92 | 8 |
| 100 | 0.820 | 90 | 10 |
| 1,000 | 0.740 | 85 | 15 |
| 10,000 | 0.680 | 78 | 22 |
| 100,000 | 0.640 | 70 | 30 |

#### At 200°C
| Time (hours) | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.820 |
| 100 | 0.680 |
| 1,000 | 0.540 |
| 10,000 | 0.430 |
| 100,000 | 0.350 |

**Note**: PTFE gaskets are much more creep-susceptible than spiral wound. At 200°C, 65% of bolt load is lost in 100,000 hours (≈11 years).

---

### Dataset 3: NPS 52" Heat Exchanger, Graphite SW Gasket

**Initial bolt load**: 120 kN per bolt (68 bolts)
**Temperature**: 350°C

| Time (hours) | FEA F/F₀ | Analytical F/F₀ | Error (%) |
|---|---|---|---|
| 0 | 1.000 | 1.000 | 0.0 |
| 10 | 0.920 | 0.915 | 0.5 |
| 100 | 0.840 | 0.830 | 1.2 |
| 1,000 | 0.720 | 0.705 | 2.1 |
| 10,000 | 0.600 | 0.580 | 3.3 |
| 50,000 | 0.520 | 0.495 | 4.8 |
| 100,000 | 0.480 | 0.450 | 6.3 |

**Analytical model matches FEA within 5% up to 10,000 hours**, then diverges due to progressive gasket plasticity not fully captured by the Norton creep model.

---

### Dataset 4: B7 vs. B16 Bolt Material Comparison (NPS 4", 400°C)

| Time (hours) | F/F₀ SA-193 B7 | F/F₀ SA-193 B16 |
|---|---|---|
| 0 | 1.000 | 1.000 |
| 10 | 0.850 | 0.920 |
| 100 | 0.720 | 0.850 |
| 1,000 | 0.560 | 0.760 |
| 10,000 | 0.420 | 0.680 |
| 100,000 | 0.340 | 0.620 |

**Key finding**: B16 (CrMoV) retains **82% more bolt load** than B7 (CrMo) at 100,000 hours at 400°C, due to superior creep resistance from vanadium strengthening.

---

### Dataset 5: Creep Contribution Breakdown (NPS 16", 350°C, 10,000 hours)

| Component | Contribution to total relaxation (%) |
|---|---|
| Gasket creep | 52 |
| Bolt creep | 28 |
| Flange creep | 12 |
| Washer embedment | 5 |
| Thread embedment | 3 |

At higher temperatures (>400°C), bolt creep becomes dominant:

| Component | At 200°C | At 350°C | At 450°C |
|---|---|---|---|
| Gasket | 80% | 52% | 30% |
| Bolt | 8% | 28% | 48% |
| Flange | 5% | 12% | 15% |
| Other | 7% | 8% | 7% |

---

## Analytical Model

### Creep Relaxation Equation (for each component)
```
ΔF_bolt / Δt = -[k_bolt × k_joint / (k_bolt + k_joint)] × [ε̇_bolt + ε̇_gasket × (k_bolt/k_gasket)]
```

Where:
- k_bolt = bolt stiffness (E_b × A_s / l_b)
- k_joint = joint stiffness (1/k_flange + 1/k_gasket)⁻¹
- ε̇_bolt = bolt creep rate (Norton law)
- ε̇_gasket = gasket creep rate (Norton law)

### Simplified Bolt Load Decay
```
F(t) = F₀ × exp(-t/τ)
```
With effective time constant:
```
τ = (k_bolt + k_joint) / (k_bolt × k_joint) × (1 / (A × σ^(n-1)))
```

---

## Reproduction Parameters

| Parameter | Value | Units |
|---|---|---|
| Flange sizes | NPS 3" to 52" | — |
| Classes | 150 / 300 / HE | — |
| Bolt grades | SA-193 B7, B16 | — |
| Gasket types | SW graphite, PTFE, PTFE-filled SW | — |
| Temperatures | 100–450 | °C |
| Duration | Up to 100,000 | hours |
| FEA | ANSYS, axisymmetric + 3D | — |

---

## MSD BUILDER CONFIGURATION

> This study models **creep relaxation** in gasketed flanged joints (not transverse vibration).
> MSD Builder configuration is for the NPS 3" Class 150 flanged joint (smallest/simplest case).
> Use THERMAL/CREEP loading type in the software when available.

### Bolt &amp; Thread Geometry — 5/8"-11 UNC

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | 5/8"-11 UNC | — |
| d (nominal) | 15.875 | mm |
| p (pitch) | 2.309 | mm |
| d₂ (pitch dia.) | 14.376 | mm |
| d₃ (minor dia.) | 13.005 | mm |
| Aₜ (stress area) | 145 | mm² |
| Grade | SA-193 B7 | — |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt | SA-193 B7 CrMo | 207,000 | 724 | 862 | 0.30 |
| Flange | SA-105 (carbon) | 207,000 | 250 | 485 | 0.30 |
| Gasket | Spiral wound SS/graphite | varies | — | — | — |

### MSD Element Chain — Flanged Joint

```
GROUND — FLANGE(weld neck) — GASKET — FLANGE(weld neck) — NUT — THREAD — SHANK — HEAD — GROUND
```

### Loading (PropertyInspector) — NPS 3" at 200°C

| Parameter | Value | Unit |
|---|---|---|
| Load type | THERMAL | — |
| Preload F₀ | 45,000 | N (per bolt) |
| ΔT | 180 | °C (20→200°C) |
| Duration | 100,000 | hours |
| n_bolts | 4 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.12 |
| Lubricated | true |
| Bolt diameter | 15.875 mm |
| Pitch | 2.309 mm |

### Temperature Configurations

| Config | Temperature (°C) | ΔT (°C) | Duration (hr) | Expected F/F₀ at end |
|---|---|---|---|---|
| Low temp | 200 | 180 | 100,000 | 0.611 |
| Med temp | 400 | 380 | 100,000 | 0.300 |
| High temp | 450 | 430 | 10,000 | 0.222 |

### ValidationCase — NPS 3", 200°C

```python
ValidationCase(
    name="Nechache_2007_NPS3_B7_200C",
    bolt_size="5/8\"-11 UNC",
    bolt_diameter_mm=15.875,
    pitch_mm=2.309,
    initial_preload_N=45000,
    preload_percent_yield=42.8,
    transverse_displacement_mm=0.0,
    frequency_Hz=0.0,
    n_cycles=0,
    mu_initial=0.12,
    lubricated=True,
    expected_final_preload_ratio=0.611,
    expected_loosening_deg=0.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=1, preload_ratio=0.944),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.867),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.778),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.700),
        ExperimentalDataPoint(cycles=10000, preload_ratio=0.644),
        ExperimentalDataPoint(cycles=100000, preload_ratio=0.611),
    ]
)
```

**Note**: "Cycles" in this ValidationCase represent **hours** of creep exposure, not mechanical vibration cycles. The x-axis is time in hours on a logarithmic scale.
