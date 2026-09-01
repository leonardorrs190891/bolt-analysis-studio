# Study 21: Reference Bolt Properties, Friction Tables, and Material Data

## Sources
- VDI 2230:2015 (Systematic calculation of highly stressed bolted joints)
- ISO 898-1:2013 (Mechanical properties of fasteners — Bolts, screws, and studs)
- ISO 898-2:2012 (Mechanical properties — Nuts)
- DIN 13 (Metric ISO thread dimensions)
- ASME B1.1 (Unified Inch Screw Threads)
- ASTM specifications (A193, A320, A453, A105, A182)

---

## Metric Bolt Dimensions (ISO 898)

### Thread Geometry

| Size | Pitch p (mm) | d₂ pitch dia (mm) | d₃ minor dia (mm) | A_s stress area (mm²) | d_head AF (mm) | d_hole std (mm) |
|---|---|---|---|---|---|---|
| M6 | 1.00 | 5.350 | 4.773 | 20.1 | 10 | 6.6 |
| M8 | 1.25 | 7.188 | 6.466 | 36.6 | 13 | 9.0 |
| M10 | 1.50 | 9.026 | 8.160 | 58.0 | 16 | 11.0 |
| M12 | 1.75 | 10.863 | 9.853 | 84.3 | 18 | 13.5 |
| M14 | 2.00 | 12.701 | 11.546 | 115.0 | 21 | 15.5 |
| M16 | 2.00 | 14.701 | 13.546 | 157.0 | 24 | 17.5 |
| M20 | 2.50 | 18.376 | 16.933 | 245.0 | 30 | 22.0 |
| M24 | 3.00 | 22.051 | 20.319 | 353.0 | 36 | 26.0 |
| M30 | 3.50 | 27.727 | 25.706 | 561.0 | 46 | 33.0 |
| M36 | 4.00 | 33.402 | 31.093 | 817.0 | 55 | 39.0 |
| M42 | 4.50 | 39.077 | 36.479 | 1,120 | 65 | 45.0 |

### Derived Geometric Parameters

| Size | Helix angle β (°) | Thread angle α (°) | r_be bearing radius (mm) | Head height (mm) | Nut height (mm) |
|---|---|---|---|---|---|
| M6 | 3.40 | 30 | 4.03 | 4.0 | 5.2 |
| M8 | 3.17 | 30 | 5.31 | 5.3 | 6.5 |
| M10 | 3.03 | 30 | 6.50 | 6.4 | 8.4 |
| M12 | 2.93 | 30 | 7.60 | 7.5 | 10.4 |
| M16 | 2.48 | 30 | 10.00 | 10.0 | 13.0 |
| M20 | 2.48 | 30 | 12.50 | 12.5 | 16.0 |
| M24 | 2.48 | 30 | 14.90 | 15.0 | 19.0 |

---

## Mechanical Properties by Class

### Bolts (ISO 898-1)

| Class | R_p0.2 (MPa) | R_m (MPa) | Hardness HRC | Material |
|---|---|---|---|---|
| 4.8 | 320 | 420 | — | Low/medium carbon steel |
| 5.8 | 420 | 520 | — | Low/medium carbon steel |
| 8.8 | 640 | 800 | 22–32 | Medium carbon steel, Q&T |
| 9.8 | 720 | 900 | — | Medium carbon steel, Q&T |
| 10.9 | 940 | 1,040 | 32–39 | Alloy steel, Q&T |
| 12.9 | 1,100 | 1,220 | 39–44 | Alloy steel, Q&T |

### Inch-Series (SAE/ASTM)

| Grade | R_p0.2 (MPa) | R_m (MPa) | Equivalent ISO |
|---|---|---|---|
| SAE 2 | 393 | 510 | ~5.8 |
| SAE 5 | 586 | 827 | ~8.8 |
| SAE 8 | 896 | 1,034 | ~10.9 |
| SAE 9 | 896 | 1,034 | ~10.9 |
| ASTM A193 B7 | 724 | 862 | ~9.8 |
| ASTM A320 L7 | 724 | 862 | ~9.8 |
| ASTM A320 L7M | 552 | 724 | ~8.8 |
| ASTM A453 Gr.660 | 586 | 862 | — |

---

## Preload Tables (VDI 2230)

### 90% R_p0.2 Utilization, μ_total = 0.12

| Size | Class 8.8 F_V (kN) | Class 10.9 F_V (kN) | Class 12.9 F_V (kN) |
|---|---|---|---|
| M6 | 9.6 | 14.1 | 16.6 |
| M8 | 17.6 | 25.8 | 30.3 |
| M10 | 27.8 | 40.9 | 48.0 |
| M12 | 40.6 | 59.7 | 70.0 |
| M16 | 75.4 | 110.8 | 130.0 |
| M20 | 117.6 | 173.0 | 203.0 |
| M24 | 169.4 | 249.0 | 292.0 |
| M30 | 269.3 | 396.0 | 464.0 |
| M36 | 392.2 | 577.0 | 676.0 |
| M42 | 537.6 | 790.0 | 927.0 |

### Tightening Torques (VDI 2230, μ = 0.12)

| Size | Class 8.8 M_A (Nm) | Class 10.9 M_A (Nm) | Class 12.9 M_A (Nm) |
|---|---|---|---|
| M6 | 9.2 | 13.5 | 15.9 |
| M8 | 22.5 | 33.0 | 38.7 |
| M10 | 44.4 | 65.2 | 76.6 |
| M12 | 77.8 | 114.4 | 134.2 |
| M16 | 192.8 | 283.2 | 332.2 |
| M20 | 375.8 | 552.6 | 648.5 |
| M24 | 649.1 | 954.0 | 1,119 |

---

## Friction Coefficient Data

### VDI 2230 Friction Classes

| Class | μ_total range | Surface treatment | Lubricant |
|---|---|---|---|
| A | 0.04–0.10 | — | MoS₂, graphite, PTFE |
| B | 0.08–0.16 | Phosphate | Oil, wax |
| C | 0.08–0.16 | Hot-dip galvanized | MoS₂ |
| D | 0.08–0.16 | Organic coating | Integrated lubricant |
| E | 0.14–0.24 | Zinc-plated | Light oil |
| F | 0.20–0.35 | Austenitic steel | Oil |
| G | 0.20–0.35 | Zinc-plated | None (dry) |
| H | ≥0.30 | Austenitic steel | None (dry) |

### Measured Friction Values (compiled from literature)

| Surface combination | μ_th | μ_b | Source |
|---|---|---|---|
| Steel-on-steel, dry | 0.20–0.30 | 0.20–0.30 | VDI 2230 |
| Steel-on-steel, oiled | 0.12–0.18 | 0.10–0.16 | VDI 2230 |
| Zinc-plated, dry | 0.20–0.35 | 0.20–0.35 | Eccles 2010 |
| Zinc-plated, oiled | 0.12–0.18 | 0.10–0.16 | Eccles 2010 |
| Phosphate + oil | 0.08–0.14 | 0.08–0.14 | Nassar 2005 |
| MoS₂ solid film | 0.04–0.08 | 0.04–0.08 | Nassar 2005 |
| PTFE coating | 0.06–0.12 | 0.06–0.12 | Liu 2017 |
| Cadmium-plated | 0.08–0.14 | 0.08–0.14 | NASA data |
| Hot-dip galvanized | 0.10–0.18 | 0.10–0.18 | VDI 2230 |
| ASTM A193 B7, as-machined | 0.15–0.25 | 0.15–0.25 | Industry data |
| ASTM A320 L7/L7M + MoS₂ | 0.06–0.12 | 0.06–0.12 | Industry data |

### Torque-Preload K-Factor (Nut Factor)

The relationship T = K × F × d gives:

| μ_total | K (nut factor) |
|---|---|
| 0.06 | 0.10 |
| 0.08 | 0.12 |
| 0.10 | 0.14 |
| 0.12 | 0.16 |
| 0.14 | 0.18 |
| 0.16 | 0.20 |
| 0.18 | 0.22 |
| 0.20 | 0.24 |
| 0.25 | 0.28 |
| 0.30 | 0.33 |

### Friction Distribution in Tightening

For any given bolt, the input torque distributes approximately:
- **~50%** → Bearing friction (under-head or nut face)
- **~38%** → Thread friction
- **~12%** → Pitch torque (actual clamping force generation)

Exact distribution: T_total = F × [p/(2π) + μ_th × d₂/(2cos α) + μ_b × r_be]

---

## Material Properties for FEA

### Standard Steel Properties

| Property | Value | Units |
|---|---|---|
| Young's modulus E | 206,000–210,000 | MPa |
| Poisson's ratio ν | 0.28–0.30 | — |
| Density ρ | 7,800–7,850 | kg/m³ |
| CTE α | 11.0–12.5 × 10⁻⁶ | /°C |
| Shear modulus G | ~80,000 | MPa |

### ASTM A193 B7 (Petrobras-relevant)
| Property | Value |
|---|---|
| Composition | 42CrMo4 (4140/4142) |
| R_p0.2 | 724 MPa (≤2.5" dia) |
| R_m | 862 MPa (≤2.5" dia) |
| Max service temp | 450°C |
| Hardness | HRC 22–35 |

### ASTM A320 L7 (Low-temperature service)
| Property | Value |
|---|---|
| Composition | 4140/4142, impact tested |
| R_p0.2 | 724 MPa |
| R_m | 862 MPa |
| Impact test | Charpy V at −101°C, ≥20 J |
| Min service temp | −101°C |

### ASTM A320 L7M (Sour service, NACE MR0175)
| Property | Value |
|---|---|
| Composition | 4140/4142 |
| R_p0.2 | 552 MPa |
| R_m | 724 MPa |
| Max hardness | HRC 22 (NACE requirement) |
| H₂S service | Yes, per NACE MR0175 |

---

## Bolt Stiffness Calculations (for preload decay models)

### Bolt Axial Stiffness
```
k_b = A_eff × E / l_eff
```
Where l_eff = l_shank + 0.4×d (for hex head) + 0.4×d (for nut)

### Joint (Clamped Members) Stiffness
Rotscher cone method (VDI 2230):
```
k_j = π × E_j × d_w × tan(φ) / [ln((D_A + d_w)(D_A - d_h)) / ((D_A - d_w)(D_A + d_h)))]
```
Where φ ≈ 25–30° is the half-angle of the pressure cone.

### Simplified VDI 2230 Stiffness Ratio
```
n = k_b / (k_b + k_j)
```
Typical values: n ≈ 0.15–0.30 for standard joints

### Load Introduction Factor
For a joint with external axial load F_A:
```
ΔF_bolt = n × F_A        (additional bolt load)
ΔF_joint = (1−n) × F_A   (joint relief)
```

Residual clamp force: F_clamp = F_V − (1−n) × F_A
Joint separates when: F_A > F_V / (1−n)

---

## MSD BUILDER NOTE

> **Study 21** is a **reference data compilation** (thread geometry, material properties, friction tables, stiffness formulas).
> It does not represent a specific experimental or FEA loosening study.
>
> **Use in software**: This data is already encoded in the BAS databases:
> - Thread geometry tables → `databases/threads_database.json`
> - Material properties → `databases/materials_database.py` and `databases/materials.json`
> - Friction coefficient tables → `numerical/friction_models.py` default ranges
> - Stiffness formulas → `core/models/model.py` assembly logic
>
> No `ValidationCase` is applicable for this reference file.
