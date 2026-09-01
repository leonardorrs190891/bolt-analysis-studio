# Study 29: Karlsen & Lemu (2022) — Large Bolt (M20–M42) Anti-Loosening Expanding Pin System

## Full Citation
**Authors**: Karlsen, A.; Lemu, H. G.
**Title**: "Comparative study on loosening of anti-loosening bolt and standard bolt system"
**Journal**: Engineering Failure Analysis, 2022, 140, 106590
**DOI**: 10.1016/j.engfailanal.2022.106590

---

## Significance
**Largest bolt sizes tested** in the loosening literature (M20, M30, M42). Compares a novel expanding-pin anti-loosening system (Bondura®) against standard HV bolt-nut. Directly relevant to **offshore wind tower ring flanges** and **oil & gas flanged joints** using large-diameter bolts.

---

## Experimental Setup

### Bolt Systems Compared

#### Standard HV System
| Size | Grade | Proof load (kN) | Preload tested (kN) |
|---|---|---|---|
| M20 | 10.9/HV | 178 | 135 (76%) |
| M30 | 10.9/HV | 434 | 325 (75%) |
| M42 | 10.9/HV | 878 | 660 (75%) |

#### Bondura® Expanding Pin System
- **Concept**: Bolt shank contains expanding sleeves that lock into the hole wall
- **Effect**: Eliminates clearance → bolt acts as dowel pin → shear transfer through shank
- **Material**: Same as standard (10.9)
- **Installation**: Axial tensioning + hydraulic pin expansion

### Test Machine
- **Type**: Custom-built Junker transverse vibration test rig (scaled up)
- **Capacity**: Up to 100 kN transverse force
- **Displacement**: ±5.0 mm (±2.5 mm typical for testing)
- **Frequency**: 5 Hz (lower than standard due to large inertia)
- **Preload**: Hydraulic tensioner (SKF/Hydrocam) with ultrasonic verification

### Clamped Assembly
- **Material**: S355 structural steel
- **Two plates**: Thickness scaled with bolt size
  - M20: 2 × 25 mm = 50 mm grip
  - M30: 2 × 37.5 mm = 75 mm grip
  - M42: 2 × 52.5 mm = 105 mm grip
- **Hole clearance (standard)**: d + 2 mm (M20: 22 mm, M30: 33 mm, M42: 45 mm)
- **Hole for Bondura**: Reamed to body-fit (d + 0.1 mm)

---

## DATA FOR CURVE PLOTTING

### Dataset 1: M20 — Standard vs. Bondura (F₀ = 135 kN, δ = 1.0 mm)

**[APPROXIMATE — digitized from published Figure 5]**

#### M20 Standard HV
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.920 |
| 100 | 0.850 |
| 200 | 0.740 |
| 500 | 0.540 |
| 1,000 | 0.350 |
| 2,000 | 0.180 |

#### M20 Bondura
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 200 | 0.990 |
| 500 | 0.980 |
| 1,000 | 0.970 |
| 2,000 | 0.955 |

---

### Dataset 2: M30 — Standard vs. Bondura (F₀ = 325 kN, δ = 1.5 mm)

#### M30 Standard HV
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.935 |
| 100 | 0.880 |
| 200 | 0.790 |
| 500 | 0.620 |
| 1,000 | 0.440 |
| 2,000 | 0.260 |

#### M30 Bondura
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 200 | 0.995 |
| 500 | 0.985 |
| 1,000 | 0.975 |
| 2,000 | 0.960 |

---

### Dataset 3: M42 — Standard vs. Bondura (F₀ = 660 kN, δ = 2.0 mm)

#### M42 Standard HV
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.945 |
| 100 | 0.895 |
| 200 | 0.820 |
| 500 | 0.670 |
| 1,000 | 0.500 |
| 2,000 | 0.330 |

#### M42 Bondura
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 500 | 0.990 |
| 1,000 | 0.982 |
| 2,000 | 0.968 |

---

### Dataset 4: Effect of Displacement Amplitude — M30 Standard

| Cycles | F/F₀ at δ=0.5mm | F/F₀ at δ=1.0mm | F/F₀ at δ=1.5mm | F/F₀ at δ=2.0mm |
|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 |
| 100 | 0.960 | 0.920 | 0.880 | 0.840 |
| 500 | 0.880 | 0.740 | 0.620 | 0.500 |
| 1,000 | 0.800 | 0.580 | 0.440 | 0.300 |
| 2,000 | 0.700 | 0.400 | 0.260 | 0.140 |

### Effect of Displacement Amplitude — M30 Bondura

| Cycles | F/F₀ at δ=0.5mm | F/F₀ at δ=1.0mm | F/F₀ at δ=1.5mm | F/F₀ at δ=2.0mm |
|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 |
| 500 | 0.998 | 0.992 | 0.985 | 0.978 |
| 1,000 | 0.995 | 0.985 | 0.975 | 0.960 |
| 2,000 | 0.990 | 0.975 | 0.960 | 0.940 |

---

### Dataset 5: Preload Retention Summary at 2,000 Cycles

| Bolt | δ (mm) | Standard F/F₀ | Bondura F/F₀ | Improvement factor |
|---|---|---|---|---|
| M20 | 1.0 | 0.180 | 0.955 | **5.3×** |
| M30 | 1.5 | 0.260 | 0.960 | **3.7×** |
| M42 | 2.0 | 0.330 | 0.968 | **2.9×** |
| M30 | 0.5 | 0.700 | 0.990 | 1.4× |
| M30 | 2.0 | 0.140 | 0.940 | **6.7×** |

---

## Key Findings

1. **Body-fit bolts are the most effective anti-loosening strategy for large bolts**: The Bondura system essentially eliminates the clearance gap, preventing relative transverse motion at the interfaces.

2. **Scaling effect**: Larger bolts retain preload slightly better than smaller bolts (at proportionally scaled amplitude), because the absolute friction forces scale with preload while the driving loosening torque from pitch is relatively smaller.

3. **Clearance is the critical parameter for large bolts**: Standard M42 has 3 mm clearance (45 - 42 mm), which allows significant lateral movement before the shank contacts the hole wall. The Bondura system reduces this to ~0.1 mm.

4. **For offshore wind flanges**: The standard practice of using M30+ HV bolts with 2 mm clearance provides **inadequate loosening resistance** under significant transverse loads. Body-fit systems or alternative locking strategies are necessary.

---

## Reproduction Parameters

| Parameter | M20 | M30 | M42 | Units |
|---|---|---|---|---|
| Preload | 135 | 325 | 660 | kN |
| % of proof | 76% | 75% | 75% | — |
| Grip length | 50 | 75 | 105 | mm |
| Standard hole | 22 | 33 | 45 | mm |
| Bondura hole | 20.1 | 30.1 | 42.1 | mm |
| Amplitudes | 0.5–2.0 | 0.5–2.0 | 0.5–2.0 | mm |
| Frequency | 5 | 5 | 5 | Hz |
| Duration | 2,000 | 2,000 | 2,000 | cycles |
| Plate material | S355 | S355 | S355 | — |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2).
> Large bolt study: M20, M30, M42. Configure each size separately.

### Bolt &amp; Thread Geometry — M20 (Baseline)

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M20×2.5 | — |
| d (nominal) | 20.0 | mm |
| p (pitch) | 2.5 | mm |
| d₂ (pitch dia.) | 18.376 | mm |
| d₃ (minor dia.) | 16.933 | mm |
| Aₜ (stress area) | 245 | mm² |
| d_head (AF) | 30.0 | mm |
| Head height | 12.5 | mm |
| Nut height | 18.0 | mm |
| d_hole (standard) | 22.0 | mm |
| Helix angle | 2.48 | ° |
| r_be (eff. bearing) | 12.5 | mm |

### Bolt Geometry — M30

| Parameter | Value | Unit |
|---|---|---|
| d (nominal) | 30.0 | mm |
| p (pitch) | 3.5 | mm |
| d₂ (pitch dia.) | 27.727 | mm |
| d₃ (minor dia.) | 25.706 | mm |
| Aₜ (stress area) | 561 | mm² |
| d_head (AF) | 46.0 | mm |
| d_hole (standard) | 33.0 | mm |

### Bolt Geometry — M42

| Parameter | Value | Unit |
|---|---|---|
| d (nominal) | 42.0 | mm |
| p (pitch) | 4.5 | mm |
| d₂ (pitch dia.) | 39.077 | mm |
| d₃ (minor dia.) | 36.479 | mm |
| Aₜ (stress area) | 1,120 | mm² |
| d_head (AF) | 65.0 | mm |
| d_hole (standard) | 45.0 | mm |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 HV | 206,000 | 940 | 1,040 | 0.30 |
| Plates | S355 structural | 210,000 | 355 | 510 | 0.30 |

### MSD Element Chain

```
GROUND — FLANGE(scaled) — FLANGE(scaled) — NUT — THREAD — SHANK — HEAD — GROUND
```

### Loading (PropertyInspector) — M20 Baseline

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 135,000 | N |
| % Yield | 58.6 | % |
| Transverse disp. δ | 1.0 | mm |
| Frequency | 5.0 | Hz |
| Cycles | 2,000 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.14 |
| Lubricated | true |
| Bolt diameter | 20.0 mm |
| Pitch | 2.5 mm |

### Size Configuration Matrix

| Config | Bolt | F₀ (kN) | % Proof | Grip (mm) | δ (mm) | Cycles |
|---|---|---|---|---|---|---|
| M20-std | M20 | 135 | 76% | 50 | 1.0 | 2,000 |
| M30-std | M30 | 325 | 75% | 75 | 1.5 | 2,000 |
| M42-std | M42 | 660 | 75% | 105 | 2.0 | 2,000 |
| M30-d05 | M30 | 325 | 75% | 75 | 0.5 | 2,000 |
| M30-d10 | M30 | 325 | 75% | 75 | 1.0 | 2,000 |
| M30-d20 | M30 | 325 | 75% | 75 | 2.0 | 2,000 |

### ValidationCase — M20 Standard

```python
ValidationCase(
    name="Karlsen_2022_M20_standard",
    bolt_size="M20x2.5",
    bolt_diameter_mm=20.0,
    pitch_mm=2.5,
    initial_preload_N=135000,
    preload_percent_yield=58.6,
    transverse_displacement_mm=1.0,
    frequency_Hz=5.0,
    n_cycles=2000,
    mu_initial=0.14,
    lubricated=True,
    expected_final_preload_ratio=0.180,
    expected_loosening_deg=15.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.920),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.850),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.740),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.540),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.350),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.180),
    ]
)
```
