# Study 08: Nassar & Housari (2007) — Effect of Hole Clearance and Thread Fit on Self-Loosening

## Full Citation
**Authors**: Nassar, S. A.; Housari, B. A.
**Title**: "Study of the Effect of Hole Clearance and Thread Fit on the Self-Loosening of Threaded Fasteners"
**Journal**: ASME Journal of Mechanical Design, 2007, 129(6), 586–594
**DOI**: 10.1115/1.2717227

---

## Experimental Setup

### Bolt Specifications
- **Size**: 3/8"-24 UNF (≈ M10 fine)
- **Grade**: SAE Grade 8 (R_p0.2 = 896 MPa, R_m = 1,034 MPa)
- **Stress area**: 36.4 mm²

### Test Machine
- RS Technologies RS-SSTM-04 (same as all Nassar group studies)
- Piezoelectric load cell, LVDT, optical encoder

### Common Parameters
- **Preload F₀**: 11,120 N (2,500 lbf)
- **Displacement amplitude**: 0.71 mm (0.028")
- **Frequency**: 7 Hz
- **Surface treatment**: Phosphate + oil (μ = 0.10)
- **Grip length**: 25.4 mm

---

## Variable: Hole Clearance

### Hole Sizes Tested

| Clearance level | Hole diameter (mm) | Clearance (mm) | Clearance (% of d) |
|---|---|---|---|
| Tight (3%) | 9.81 | 0.29 | 3.0% |
| Standard (6%) | 10.10 | 0.57 | 6.0% |
| Loose (10%) | 10.48 | 0.95 | 10.0% |

Note: Bolt nominal diameter d = 9.525 mm (3/8")

### Physical Explanation
Larger hole clearance allows the bolt shank to translate freely within the hole before engaging the hole wall. Once engaged, the shank acts as a dowel pin and carries shear load. With tighter clearance, engagement occurs earlier in the loading cycle, reducing the displacement at the thread/bearing interfaces.

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Effect of Hole Clearance (F₀ = 11,120 N, δ = 0.71 mm, μ = 0.10)

**[APPROXIMATE — digitized from published Figure 6]**

#### 3% clearance (tight)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.900 |
| 20 | 0.820 |
| 50 | 0.660 |
| 100 | 0.480 |
| 200 | 0.280 |
| 500 | 0.080 |

#### 6% clearance (standard)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.750 |
| 20 | 0.560 |
| 50 | 0.280 |
| 100 | 0.100 |
| 200 | 0.020 |

#### 10% clearance (loose)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.680 |
| 10 | 0.480 |
| 20 | 0.250 |
| 50 | 0.060 |
| 100 | 0.010 |

### Summary: Cycles to 50% Preload Loss
| Clearance | Cycles to 50% |
|---|---|
| 3% | ~95 |
| 6% | ~20 |
| 10% | ~10 |

**Key finding**: Reducing hole clearance from 10% to 3% increases loosening life by approximately **10×**. This is one of the strongest geometric factors affecting loosening.

### Quantitative Relationship
The loosening rate increases approximately exponentially with clearance:
```
Rate ∝ exp(k × clearance%)
```
With k ≈ 0.25 per percent of clearance.

Or equivalently, loosening life:
```
N_50% ≈ N_ref × exp(−0.25 × (Cl% − Cl_ref%))
```

---

## Variable: Thread Fit Class

### ASME Thread Fit Classes Tested

| Class | Description | Tolerance | Typical application |
|---|---|---|---|
| 1B (internal) / 1A (external) | Loose fit | Maximum allowance | Easy assembly, dirty environments |
| 2B / 2A | Standard fit | Normal | General purpose (most common) |
| 3B / 3A | Close fit | Minimum allowance | Precision, tight tolerance |

### Key Dimensional Differences
| Fit class | Pitch dia. tolerance (mm) | Flank clearance (mm) |
|---|---|---|
| 1B/1A | ±0.10 | 0.15–0.20 |
| 2B/2A | ±0.06 | 0.08–0.12 |
| 3B/3A | ±0.03 | 0.03–0.06 |

---

### Dataset 2: Effect of Thread Fit Class (F₀ = 11,120 N, δ = 0.71 mm, μ = 0.10)

**[APPROXIMATE — digitized from published Figure 8]**

#### 1B fit (loose)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 5 | 0.720 |
| 10 | 0.520 |
| 20 | 0.300 |
| 50 | 0.080 |
| 100 | 0.010 |

#### 2B fit (standard)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.750 |
| 20 | 0.560 |
| 50 | 0.280 |
| 100 | 0.100 |
| 200 | 0.020 |

#### 3B fit (close)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.870 |
| 20 | 0.760 |
| 50 | 0.540 |
| 100 | 0.340 |
| 200 | 0.160 |
| 500 | 0.030 |

### Summary: Cycles to 50% Preload Loss
| Fit class | Cycles to 50% |
|---|---|
| 1B (loose) | ~12 |
| 2B (standard) | ~20 |
| 3B (close) | ~55 |

**Key finding**: Close-fit threads (3B) resist loosening ~5× better than loose-fit (1B). Tighter thread fit reduces the play at thread flanks, requiring higher force for complete thread slip.

---

### Dataset 3: Combined Effects — Tight Hole + Close Fit vs. Loose Hole + Loose Fit

#### Best case: 3% clearance + 3B fit
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 20 | 0.900 |
| 50 | 0.780 |
| 100 | 0.620 |
| 200 | 0.420 |
| 500 | 0.180 |
| 1,000 | 0.050 |

#### Worst case: 10% clearance + 1B fit
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 2 | 0.600 |
| 5 | 0.350 |
| 10 | 0.150 |
| 20 | 0.030 |

### Combined Effect Ratio
| Configuration | Cycles to 50% | Ratio to worst case |
|---|---|---|
| 10% + 1B (worst) | ~4 | 1.0× |
| 6% + 2B (standard) | ~20 | 5.0× |
| 3% + 3B (best) | ~150 | 37.5× |

The combined effect of tight clearance + close fit provides a **38× improvement** in loosening resistance compared to the worst case. This is a purely geometric improvement — no coating, locking device, or increased preload required.

---

## Design Recommendations (from this paper)

1. **Use minimum possible hole clearance** — Standard ISO clearances (medium fit) are sufficient for assembly; close fit is better for vibration resistance
2. **Specify thread fit class** — Use 2A/2B minimum; use 3A/3B for critical applications
3. **Avoid oversized holes** — Oversized holes (for misalignment tolerance) dramatically reduce loosening resistance
4. **Body-fit bolts** — Consider body-fit (reamed hole) bolts for highest loosening resistance

### ISO Hole Clearances Reference
| Bolt size | Fine (d + 0.5) | Medium (d + 1.0) | Coarse (d + 2.0) |
|---|---|---|---|
| M8 | 8.5 mm | 9.0 mm | 10.0 mm |
| M10 | 10.5 mm | 11.0 mm | 12.0 mm |
| M12 | 12.5 mm | 13.5 mm | 14.0 mm |
| M16 | 16.5 mm | 17.5 mm | 18.0 mm |
| M20 | 20.5 mm | 22.0 mm | 24.0 mm |

---

## Reproduction Parameters

| Parameter | Value | Units |
|---|---|---|
| Bolt | 3/8"-24 UNF | — |
| Grade | SAE 8 | — |
| Preload | 11,120 | N |
| Amplitude | 0.71 | mm |
| Frequency | 7 | Hz |
| μ | 0.10 | — |
| Hole clearances | 3%, 6%, 10% of d | — |
| Thread fits | 1B, 2B, 3B | ASME B1.1 |
| Grip length | 25.4 | mm |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this experiment.
> NOTE: 3/8"-24 UNF ≈ M10 fine equivalent. For hole clearance tests, vary d_hole in FLANGE elements.

### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | 3/8"-24 UNF (≈M10 fine) | — |
| d (nominal) | 9.525 | mm |
| p (pitch) | 1.058 | mm |
| d₂ (pitch dia.) | 8.944 | mm |
| Aₜ (stress area) | 42.3 | mm² |
| d_head (AF) | 14.3 | mm |
| Head height | 5.56 | mm |
| d_hole | 10.10 | mm (6% standard) |
| Grip length | 25.4 | mm |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | SAE Gr.8 | 206,000 | 896 | 1,034 | 0.3 |
| Plates | AISI 1018 | 200,000 | 250 | 440 | 0.29 |

### MSD Element Chain

```
GROUND — FLANGE(12.7mm) — FLANGE(12.7mm) — NUT — THREAD — SHANK — HEAD — GROUND
```

### Loading (PropertyInspector)

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 11,120 | N |
| % Yield | 29.4 | % |
| Transverse disp. δ | 0.71 | mm |
| Frequency | 7.0 | Hz |
| Cycles | 500 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.10 |
| Lubricated | true (phosphate + oil) |

### Hole Clearance Configurations

| Config | d_hole (mm) | Clearance (%) | Thread fit | Notes |
|---|---|---|---|---|
| Tight hole | 9.81 | 3% | 2B standard | Best resistance |
| Standard hole | 10.10 | 6% | 2B standard | Baseline |
| Loose hole | 10.48 | 10% | 2B standard | Worst |
| Loose fit | 10.10 | 6% | 1B loose | Worst thread |
| Close fit | 10.10 | 6% | 3B close | Best thread |
| Best combo | 9.81 | 3% | 3B close | 37.5× better |
| Worst combo | 10.48 | 10% | 1B loose | Reference (worst) |

### ValidationCase — Standard Config (for validation_cases.py)

```python
ValidationCase(
    name="Nassar_2007_clearance_standard",
    bolt_size="3/8-24UNF",
    bolt_diameter_mm=9.525,
    pitch_mm=1.058,
    initial_preload_N=11120,
    preload_percent_yield=29.4,
    transverse_displacement_mm=0.71,
    frequency_Hz=7.0,
    n_cycles=200,
    mu_initial=0.10,
    lubricated=True,
    expected_final_preload_ratio=0.02,
    expected_loosening_deg=18.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.750),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.560),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.280),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.100),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.020),
    ]
)
```
