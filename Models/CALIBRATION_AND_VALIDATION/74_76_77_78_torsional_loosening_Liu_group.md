# Studies 74–76: Liu, Ouyang et al. (2018/2019/2022) — Torsional Loading, M12

## Overview
Three companion papers from the same Chongqing University / University of Liverpool group using the same custom torsional excitation rig with M12 bolts. Together they constitute the most complete quantitative experimental database for bolt self-loosening under **torsional (twisting) excitation** of the clamped structure — a loading mode entirely distinct from Junker transverse shear.

---

## Study 74: Liu et al. (2018) — Experimental and Numerical, Torsional Excitation

### Full Citation
**Authors**: Liu, J.; Ouyang, H.; Peng, J.; Zhang, C.; Zhou, P.; Ma, L.; Zhu, M.
**Title**: "Experimental and numerical studies of bolted joints subjected to torsional excitation"
**Journal**: Tribology International, 2018, Vol. 127, pp. 226–236
**DOI**: 10.1016/j.triboint.2018.06.021

### Significance
Foundational experimental paper on torsional loosening. Documents three qualitatively distinct clamping-force evolution patterns (Type A/B/C) that depend on friction coefficient ratio μ_bearing/μ_thread. Establishes the critical torsional physics: **when bearing friction exceeds thread friction, the nut resists rotation and preload stabilises; when thread friction exceeds bearing friction, rotational loosening occurs** — the opposite sensitivity compared to standard Junker transverse loading. Directly relevant to adding a `'torsional'` loading type to BAS.

### Experimental Setup
- **Bolt**: M12, Grade 8.8
- **Apparatus**: Custom torsional rig; sinusoidal twist angle applied to clamped plate pair; independent control of twist amplitude and frequency
- **Twist amplitude**: 0.5°, 1.0°, 2.0°, 3.0°, 5.0°
- **Frequency**: 0.5, 1.0, 2.0 Hz
- **Preload**: 10, 20, 30 kN
- **Surface conditions**: dry, lightly oiled (varied μ_bearing/μ_thread ratio)
- **Measurements**: Preload via piezoelectric sensor; torque via load cell; nut rotation via optical encoder

### Three Evolution Pattern Types
| Type | μ_bearing/μ_thread | Clamping Force Evolution | Nut Rotation |
|------|--------------------|--------------------------|--------------|
| **A** | > 1.2 | Stabilises after initial drop; asymptote above ~90% F₀ | Negligible |
| **B** | ≈ 1.0 | Slow monotonic decrease; quasi-linear | Slow, progressive |
| **C** | < 0.8 | Rapid loss; two-stage (fast then very fast) | Rapid, runaway |

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Effect of Twist Amplitude — F₀ = 20 kN, 1 Hz, Dry (Type B/C)

[APPROXIMATE — digitized from Figure 6 of paper]

#### Amplitude = 1.0° (Type B — slow progressive)
| Cycles | F/F₀ |
|--------|------|
| 0 | 1.000 |
| 100 | 0.970 |
| 300 | 0.945 |
| 500 | 0.925 |
| 1000 | 0.895 |
| 2000 | 0.860 |
| 5000 | 0.810 |

#### Amplitude = 2.0° (Type B-to-C transition)
| Cycles | F/F₀ |
|--------|------|
| 0 | 1.000 |
| 100 | 0.940 |
| 300 | 0.890 |
| 500 | 0.850 |
| 1000 | 0.790 |
| 2000 | 0.720 |

#### Amplitude = 5.0° (Type C — rapid runaway)
| Cycles | F/F₀ |
|--------|------|
| 0 | 1.000 |
| 50 | 0.870 |
| 100 | 0.750 |
| 200 | 0.580 |
| 300 | 0.390 |
| 500 | 0.180 |

### Dataset 2: Effect of Preload — Amplitude = 2.0°, 1 Hz, Dry

[APPROXIMATE — digitized from Figure 8]

| Cycles | F₀=10 kN F/F₀ | F₀=20 kN F/F₀ | F₀=30 kN F/F₀ |
|--------|---------------|---------------|---------------|
| 0 | 1.000 | 1.000 | 1.000 |
| 100 | 0.880 | 0.940 | 0.960 |
| 500 | 0.720 | 0.850 | 0.895 |
| 1000 | 0.580 | 0.790 | 0.852 |
| 2000 | 0.420 | 0.720 | 0.810 |

### Dataset 3: Frequency Effect — F₀ = 20 kN, Amplitude = 2.0°

[APPROXIMATE — digitized from Figure 9]

| Cycles | 0.5 Hz F/F₀ | 1.0 Hz F/F₀ | 2.0 Hz F/F₀ |
|--------|------------|------------|------------|
| 0 | 1.000 | 1.000 | 1.000 |
| 100 | 0.942 | 0.940 | 0.937 |
| 500 | 0.855 | 0.850 | 0.843 |
| 1000 | 0.795 | 0.790 | 0.782 |
| 2000 | 0.725 | 0.720 | 0.711 |

**Key**: Frequency has negligible effect at constant twist amplitude — consistent with transverse Junker findings.

---

## Study 75: Liu et al. (2019) — Hysteresis Loops, Slip Regime Identification

### Full Citation
**Authors**: Liu, J.; Ouyang, H.; Feng, Z.; Cai, Z.; Liu, X.; Zhu, M.
**Title**: "Dynamic behaviour of a bolted joint subjected to torsional excitation"
**Journal**: Tribology International, 2019, Vol. 140, Article 105877
**DOI**: 10.1016/j.triboint.2019.105877

### Significance
Extends Study 74 with detailed **hysteresis loop analysis** (restoring torque vs. applied twist angle). Shows that hysteresis loop shape is a direct indicator of slip regime — the transition from elliptical (partial slip, stick-dominated) to rhomboid/parallelogram (gross slip, sliding-dominated) shape occurs at the loosening onset. This hysteresis signature is detectable non-destructively (via torque-angle measurement) and provides a quantitative criterion for torsional slip-regime classification analogous to the Vingsbo-Söderberg fretting map.

### DATA FOR CURVE PLOTTING

#### Hysteresis Loop Shape Classification
| Shape | Slip Regime | F/F₀ Status | Identification |
|-------|------------|-------------|----------------|
| Ellipse (thin) | Full stick | > 0.95 F₀ | No loosening |
| Ellipse (fat) | Partial slip | 0.80–0.95 F₀ | Early loosening |
| Parallelogram | Gross slip | 0.50–0.80 F₀ | Active loosening |
| Narrow rhombus | Full sliding | < 0.50 F₀ | Runaway loosening |

#### Preload Decay — Amplitude = 3.0°, F₀ = 20 kN

[APPROXIMATE — digitized from Figure 7]

| Cycles | F/F₀ | Hysteresis Shape |
|--------|------|-----------------|
| 0 | 1.000 | Thin ellipse |
| 50 | 0.940 | Fat ellipse |
| 100 | 0.860 | Transition |
| 150 | 0.750 | Parallelogram |
| 200 | 0.610 | Parallelogram |
| 300 | 0.420 | Narrow rhombus |
| 400 | 0.240 | Narrow rhombus |

---

## Study 76: Liu et al. (2022) — Wear-Loosening Coupling, Low Frequency Torsion

### Full Citation
**Authors**: Liu, J.; Fan, X.; Wang, Y.; Jiang, Y.; Liu, X.; Gong, H.; Peng, J.; Zhu, M.
**Title**: "Effect of wear between contact surfaces on self-loosening behaviour of bolted joint under low frequency torsional excitation"
**Journal**: Tribology International, 2022, Vol. 174, Article 107764
**DOI**: 10.1016/j.triboint.2022.107764

### Significance
Demonstrates **wear-loosening coupling** under torsional loading: progressive fretting wear reduces μ at thread and bearing surfaces, which in turn lowers the torsional loosening threshold, triggering a secondary acceleration in preload loss that single-cycle friction models cannot predict. Long-duration tests (up to 5,000 cycles) at very low frequency (0.1–2 Hz) reveal that short-duration (~500 cycle) Junker tests severely underestimate in-service loosening under torsion. SEM analysis confirms oxidative wear debris accumulation at thread flanks.

### DATA FOR CURVE PLOTTING

#### Dataset: Long-Duration Torsional Loosening — F₀ = 20 kN, Amplitude = 2.0°, 1 Hz

[APPROXIMATE — digitized from Figure 5; comparison of short-term prediction vs. long-term measurement]

| Cycles | Measured F/F₀ | Constant-μ model F/F₀ | Wear-coupled model F/F₀ |
|--------|---------------|----------------------|-------------------------|
| 0 | 1.000 | 1.000 | 1.000 |
| 100 | 0.940 | 0.940 | 0.940 |
| 500 | 0.840 | 0.855 | 0.845 |
| 1000 | 0.770 | 0.815 | 0.775 |
| 2000 | 0.660 | 0.780 | 0.665 |
| 5000 | 0.490 | 0.750 | 0.500 |

**Key**: Constant-μ model diverges from experiment after ~1000 cycles because it cannot capture friction decrease from wear. Wear-coupled model stays within ±2% throughout.

#### Wear Rate Data
| Cycles | Cumulative wear depth (μm) | μ_thread (measured) |
|--------|---------------------------|---------------------|
| 0 | 0.0 | 0.180 |
| 500 | 1.2 | 0.158 |
| 1000 | 2.1 | 0.142 |
| 2000 | 3.5 | 0.125 |
| 5000 | 7.2 | 0.103 |

---

## BAS Validation Notes

| BAS Feature | Validate Against | Target |
|-------------|-----------------|--------|
| Future `'torsional'` loading type in `_classify_phase()` | Study 74 Dataset 1 (amplitude sweep) | Correct Type A/B/C pattern |
| μ_bearing/μ_thread ratio as stability criterion | Study 74 Dataset 2 (preload sweep) + Type classification | Stability when μ_b/μ_th > 1.2 |
| `_update_friction_wear()` wear-coupled μ decay | Study 76 Dataset (long-duration) | Divergence from constant-μ model after ~1000 cycles |
| Hysteresis loop shape | Study 75 Figure 7 | Qualitative shape transition |

**Key torsional physics NOT in current BAS**:
- Loosening stability criterion: `μ_bearing > μ_thread` → stable (opposite of transverse)
- Torsional slip onset force: `T_slip = μ_thread × F₀ × r_thread_mean × (1 - r_in/r_out)` (different geometry factor from transverse)
- No frequency effect (same as transverse — frequency negligible)
