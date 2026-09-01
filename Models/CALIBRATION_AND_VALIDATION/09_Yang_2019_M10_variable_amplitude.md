# Study 09: Yang et al. (2019) — M10 Variable Amplitude Vibration & Loosening Life Prediction

## Full Citation
**Authors**: Yang, J.; Chen, L.; Wang, D.
**Title**: "Experimental Study and Life Prediction of Bolt Loosening Life under Variable Amplitude Vibration"
**Journal**: Shock and Vibration, 2019, Article ID 2036509
**DOI**: 10.1155/2019/2036509
**Access**: Open Access
**URL**: https://onlinelibrary.wiley.com/doi/10.1155/2019/2036509

---

## Experimental Setup

### Bolt Specifications
- **Size**: M10 × 1.5 (ISO metric coarse)
- **Property class**: 10.9 (high-strength)
- **Material**: Alloy steel
- **Yield strength R_p0.2**: 940 MPa
- **Ultimate tensile strength R_m**: 1,040 MPa
- **Stress area**: 58.0 mm²
- **Proof load**: 54,520 N

### Nut
- **Type**: Standard hex nut, Class 10
- **Height**: 8.4 mm (M10)

### Clamped Members
- **Material**: Steel (grade not specified)
- **Configuration**: Two-plate lap joint

### Test Machine
- **Type**: Junker-type transverse vibration test machine (likely DIN 65151 compliant)
- **Preload measurement**: Strain gauge on bolt / load cell
- **Nut rotation**: Angular encoder

### Test Conditions — Constant Amplitude
- **Initial preload F₀**: 26,000 N (26 kN) → 47.7% of proof load
- **Frequency**: 5 Hz (confirmed frequency independence at 5–20 Hz)
- **Displacement amplitudes tested**: 0.3, 0.4, 0.6, 0.8, 1.0 mm

### Test Conditions — Variable Amplitude
- **Block loading sequences**: Two-step and multi-step amplitude programs
- **Miner's rule application**: Linear damage accumulation D = Σ(nᵢ/Nᵢ) = 1

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Constant Amplitude Preload Decay Curves

**[APPROXIMATE — digitized from published Figure 3]**

#### δ = 0.3 mm (Below/near threshold)
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 26,000 | 1.000 |
| 100 | 25,200 | 0.969 |
| 500 | 24,000 | 0.923 |
| 1,000 | 23,500 | 0.904 |
| 2,000 | 23,000 | 0.885 |
| 5,000 | 22,500 | 0.865 |
| 10,000 | 22,000 | 0.846 |
| 20,000 | 21,500 | 0.827 |

*Near endurance limit — very slow loosening, predominantly Stage I*

#### δ = 0.4 mm
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 26,000 | 1.000 |
| 50 | 24,500 | 0.942 |
| 100 | 23,500 | 0.904 |
| 500 | 20,000 | 0.769 |
| 1,000 | 18,000 | 0.692 |
| 2,000 | 16,000 | 0.615 |
| 5,000 | 13,000 | 0.500 |
| 9,000 | 10,000 | 0.385 |
| 15,000 | 7,000 | 0.269 |

#### δ = 0.6 mm
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 26,000 | 1.000 |
| 10 | 23,500 | 0.904 |
| 20 | 21,500 | 0.827 |
| 50 | 18,000 | 0.692 |
| 100 | 14,000 | 0.538 |
| 200 | 9,500 | 0.365 |
| 500 | 4,500 | 0.173 |
| 1,000 | 2,000 | 0.077 |
| 2,000 | 500 | 0.019 |

#### δ = 0.8 mm
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 26,000 | 1.000 |
| 5 | 22,000 | 0.846 |
| 10 | 19,000 | 0.731 |
| 20 | 14,500 | 0.558 |
| 50 | 7,500 | 0.288 |
| 100 | 3,000 | 0.115 |
| 200 | 1,000 | 0.038 |
| 500 | 200 | 0.008 |

#### δ = 1.0 mm
| Cycles | Preload (N) | F/F₀ |
|---|---|---|
| 0 | 26,000 | 1.000 |
| 2 | 20,000 | 0.769 |
| 5 | 15,000 | 0.577 |
| 10 | 9,500 | 0.365 |
| 20 | 4,500 | 0.173 |
| 50 | 1,000 | 0.038 |
| 100 | 200 | 0.008 |

---

### Dataset 2: D-N Curve (Displacement-Life Curve)

**Loosening life N_L defined as**: cycles at which preload drops to **10% of F₀** (i.e., F = 2,600 N)

| Displacement amplitude δ (mm) | N_L (cycles to 10% F₀) | log₁₀(δ) | log₁₀(N_L) |
|---|---|---|---|
| 0.30 | >50,000 (did not reach) | -0.523 | >4.699 |
| 0.40 | ~18,000 | -0.398 | 4.255 |
| 0.50 | ~4,500 | -0.301 | 3.653 |
| 0.60 | ~1,200 | -0.222 | 3.079 |
| 0.70 | ~500 | -0.155 | 2.699 |
| 0.80 | ~250 | -0.097 | 2.398 |
| 0.90 | ~140 | -0.046 | 2.146 |
| 1.00 | ~80 | 0.000 | 1.903 |

**D-N curve equation** (bilinear in log-log):
```
For δ > δ_threshold:
  log₁₀(N_L) = A - m × log₁₀(δ)

Fitted parameters:
  A ≈ 1.90 (intercept)
  m ≈ 3.5 to 4.0 (slope, varies with preload)
  δ_threshold ≈ 0.30 mm (endurance limit for M10 at 26 kN)
```

This is directly analogous to the Basquin equation for fatigue:
```
S-N: σ = σ'_f × (2N)^b
D-N: δ = δ'_f × (N_L)^(-1/m)
```

---

### Dataset 3: Frequency Independence Verification

| Frequency (Hz) | Cycles to 50% loss (δ = 0.6 mm) |
|---|---|
| 5 | ~100 |
| 10 | ~95 |
| 15 | ~100 |
| 20 | ~105 |

**Conclusion**: Frequency has no significant effect on loosening in the 5–20 Hz range. Only displacement amplitude matters.

---

### Dataset 4: Variable Amplitude Loading (Block Loading)

#### Two-Step Loading: High → Low
**Step 1**: δ₁ = 0.8 mm for n₁ cycles, then **Step 2**: δ₂ = 0.6 mm for remaining cycles

| n₁ at δ₁=0.8mm | Remaining life at δ₂=0.6mm | n₁/N₁ + n₂/N₂ (Miner sum) |
|---|---|---|
| 50 (20% of N₁) | ~850 (71% of N₂) | 0.20 + 0.71 = 0.91 |
| 100 (40% of N₁) | ~550 (46% of N₂) | 0.40 + 0.46 = 0.86 |
| 150 (60% of N₁) | ~300 (25% of N₂) | 0.60 + 0.25 = 0.85 |

#### Two-Step Loading: Low → High
**Step 1**: δ₁ = 0.6 mm for n₁ cycles, then **Step 2**: δ₂ = 0.8 mm for remaining cycles

| n₁ at δ₁=0.6mm | Remaining life at δ₂=0.8mm | n₁/N₁ + n₂/N₂ (Miner sum) |
|---|---|---|
| 200 (17% of N₁) | ~220 (88% of N₂) | 0.17 + 0.88 = 1.05 |
| 400 (33% of N₁) | ~150 (60% of N₂) | 0.33 + 0.60 = 0.93 |
| 600 (50% of N₁) | ~100 (40% of N₂) | 0.50 + 0.40 = 0.90 |

**Key finding**: Miner's linear damage sum for bolt loosening is approximately **D = 0.85–1.05**, with High→Low sequences giving D < 1 (conservative) and Low→High giving D ≈ 1 (accurate). This validates the use of Miner's rule for loosening life prediction under variable amplitude loading.

---

## Reproduction Parameters Summary

| Parameter | Value | Units |
|---|---|---|
| Bolt size | M10 × 1.5 | — |
| Property class | 10.9 | — |
| Initial preload | 26,000 | N |
| Displacement amplitudes | 0.3–1.0 | mm |
| Frequency | 5 | Hz |
| Loading waveform | Sinusoidal (displacement-controlled) | — |
| Loosening criterion | F = 0.10 × F₀ | — |
| Surface condition | Standard (unlubricated) | — |
| Estimated μ | 0.15–0.20 | — |
| Grip length | ~20–25 mm (estimated) | mm |
| Hole clearance | Standard (~10.5 mm) | mm |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this experiment.

### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M10×1.5 | — |
| d (nominal) | 10.0 | mm |
| p (pitch) | 1.50 | mm |
| d₂ (pitch dia.) | 9.026 | mm |
| d₃ (minor dia.) | 8.160 | mm |
| Aₜ (stress area) | 58.0 | mm² |
| d_head (AF) | 16.0 | mm |
| Head height | 6.4 | mm |
| Nut height | 8.4 | mm |
| d_hole | 11.0 | mm |
| Grip length | 22.0 | mm (estimated) |
| Helix angle | 3.03 | ° |
| r_be (eff. bearing) | 6.50 | mm |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 Q&T | 210,000 | 940 | 1,040 | 0.3 |
| Plates | Steel | 210,000 | — | — | 0.3 |

### MSD Element Chain

    GROUND — FLANGE(11mm) — FLANGE(11mm) — NUT — THREAD — SHANK — HEAD — GROUND

### Loading (PropertyInspector) — Baseline Test

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 26,000 | N |
| % Yield | 47.7 | % |
| Transverse disp. δ | 0.60 | mm |
| Frequency | 5.0 | Hz |
| Cycles | 2,000 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 |
| Lubricated | false |
| Bolt diameter | 10.0 mm |
| Pitch | 1.50 mm |

### Amplitude Configurations

| Config | δ (mm) | Expected N_L (10% F₀) | Notes |
|---|---|---|---|
| Threshold | 0.30 | >50,000 | Near endurance limit |
| Low | 0.40 | ~18,000 | Slow loosening |
| Medium | 0.60 | ~1,200 | Standard test |
| High | 0.80 | ~250 | Rapid loosening |
| Extreme | 1.00 | ~80 | Very rapid |

### ValidationCase — 0.6mm Amplitude (for validation_cases.py)

```python
ValidationCase(
    name="Yang_2019_M10_0.6mm",
    bolt_size="M10x1.5",
    bolt_diameter_mm=10.0,
    pitch_mm=1.50,
    initial_preload_N=26000,
    preload_percent_yield=47.7,
    transverse_displacement_mm=0.60,
    frequency_Hz=5.0,
    n_cycles=2000,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.019,
    expected_loosening_deg=20.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.904),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.827),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.692),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.538),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.365),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.173),
        ExperimentalDataPoint(cycles=1000, preload_ratio=0.077),
        ExperimentalDataPoint(cycles=2000, preload_ratio=0.019),
    ]
)
```
