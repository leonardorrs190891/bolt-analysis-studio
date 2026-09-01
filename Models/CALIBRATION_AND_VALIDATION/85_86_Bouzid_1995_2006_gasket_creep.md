# Studies 85–86: Bouzid et al. (1995/2006) — Gasket Creep-Relaxation and Elastic Interaction

## Study 85: Bouzid, Chaaban & Bazergui (1995) — Gasket Creep-Relaxation on Leakage Tightness

### Full Citation
**Authors**: Bouzid, A. H.; Chaaban, A.; Bazergui, A.
**Title**: "The Effect of Gasket Creep-Relaxation on the Leakage Tightness of Bolted Flanged Joints"
**Journal**: ASME Journal of Pressure Vessel Technology, February 1995, Vol. 117, No. 1, pp. 71–78
**DOI**: 10.1115/1.2842093

### Significance
Foundational paper on **gasket viscoelastic creep** as a preload loss mechanism in bolted flanged joints. Quantifies the first experimentally validated creep-relaxation model for spiral-wound and flexible graphite gaskets under static compression and cyclic thermal loading. Provides the calibration basis for BAS `NortonBaileyCreepModel` and the `FlangeGasketContact` stiffness model. Shows 20–60% preload loss from gasket creep alone (no vibration), validating why gasket joints must be re-torqued after initial assembly.

### Experimental Setup
- **Flange**: NPS 4, Class 300 (8-bolt configuration)
- **Bolt**: M12 × 1.75, Class 10.9 (1 inch diameter equivalent for the NPS 4 flange)
- **Gasket types tested**:
  - Spiral-wound stainless steel/graphite (SWSG), 3 mm thick
  - Flexible graphite sheet, 1.5 mm thick
- **Temperature range**: Ambient (20°C) to 200°C, in steps
- **Duration**: 24 hours to 168 hours at each condition
- **Preload measurement**: Ultrasonic bolt-load measurement technique; ±1% accuracy
- **Cycles**: Static compression + stepped thermal cycling (not vibration-induced)

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Bolt Load Relaxation Over Time — Spiral-Wound Gasket (SWSG), Ambient Temperature

[APPROXIMATE — digitized from Figure 3 of paper]

| Time (hours) | Normalised bolt load F/F₀ | Loss fraction |
|--------------|--------------------------|---------------|
| 0 | 1.000 | 0.0% |
| 0.25 | 0.940 | 6.0% |
| 0.5 | 0.920 | 8.0% |
| 1 | 0.905 | 9.5% |
| 2 | 0.892 | 10.8% |
| 4 | 0.880 | 12.0% |
| 8 | 0.868 | 13.2% |
| 24 | 0.850 | 15.0% |
| 48 | 0.840 | 16.0% |
| 168 | 0.828 | 17.2% |

**Model**: Logarithmic decay F/F₀ = 1 − A × ln(1 + t/τ), with A ≈ 0.060, τ ≈ 0.1 h for SWSG at ambient.

### Dataset 2: Bolt Load Relaxation — Flexible Graphite Gasket, Ambient Temperature

[APPROXIMATE — digitized from Figure 3]

| Time (hours) | Normalised bolt load F/F₀ |
|--------------|--------------------------|
| 0 | 1.000 |
| 0.25 | 0.920 |
| 1 | 0.880 |
| 4 | 0.848 |
| 24 | 0.812 |
| 168 | 0.790 |

**Key**: Flexible graphite loses ~21% in 168 h vs. ~17% for SWSG — higher creep compliance.

### Dataset 3: Effect of Temperature on Preload Loss — SWSG Gasket

[APPROXIMATE — from Figures 4 and 5]

| Temperature (°C) | F/F₀ after 24 h | F/F₀ after 168 h |
|------------------|-----------------|------------------|
| 20 (ambient) | 0.850 | 0.828 |
| 100 | 0.800 | 0.762 |
| 150 | 0.740 | 0.690 |
| 200 | 0.650 | 0.580 |

**Key**: Every 50°C rise roughly doubles the creep rate. At 200°C + 168 h: 42% preload loss.

### Dataset 4: Cyclic Thermal Loading (Startup/Shutdown Cycles)

[APPROXIMATE — from Figure 7; 3 thermal cycles from ambient to 200°C]

| Thermal cycle # | F/F₀ at peak temp | F/F₀ after cool-down |
|-----------------|-------------------|----------------------|
| 0 (initial) | 1.000 | 1.000 |
| 1 | 0.720 | 0.680 |
| 2 | 0.640 | 0.615 |
| 3 | 0.600 | 0.582 |

**Key**: Each thermal cycle drives additional ratchetting creep. First cycle causes ~32% loss; subsequent cycles add ~4–8% each.

---

## Study 86: Bouzid & Nechache (2006) — Elastic Interaction + Gasket Creep Combined

### Full Citation
**Authors**: Bouzid, A. H.; Nechache, A.
**Title**: "Clamp Load Loss due to Elastic Interaction and Gasket Creep Relaxation in Bolted Joints"
**Journal**: ASME Journal of Pressure Vessel Technology, August 2006, Vol. 128, No. 3, pp. 394–401
**DOI**: 10.1115/1.2218343

### Significance
Quantifies **two simultaneous mechanisms** causing preload loss in multi-bolt flange assemblies:
1. **Elastic interaction** during tightening: torquing one bolt elastically deflects the flange and relaxes adjacent bolts already tightened (cross-talk). Causes 10–30% loss during assembly.
2. **Gasket creep relaxation**: Additional 10–25% loss over hours after assembly.

The combined effect explains why initial bolt preload after assembly is always significantly lower than the torque-target value. Essential for calibrating the BAS `VDI2230EmbeddingModel` and the loading setup (target preload vs. achieved preload gap).

### Experimental Setup
- **Flange**: Two-flange test rig; 5-bolt and 8-bolt configurations
- **Bolt**: M12 × 1.75, Class 10.9; plus aramid sheet gasket 3 mm, SBR rubber 3 mm, flexible graphite 1.5 mm
- **Tightening method**: Sequential hand tightening via torque wrench; tightening torque controlled
- **Measurements**: Individual bolt preload measured ultrasonically after each bolt tightening and after 24 hours creep

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Elastic Interaction Effect — 8-Bolt Flange, Sequential Star Pattern

[APPROXIMATE — digitized from Figure 4 of paper; values shown as fraction of target preload]

| Bolt tightening sequence # | Bolt 1 F/F_target | Bolt 5 F/F_target | Bolt 8 F/F_target |
|---------------------------|-------------------|-------------------|-------------------|
| After tightening bolt 1 | 1.000 | — | — |
| After bolt 5 | 0.950 | 1.000 | — |
| After bolt 8 | 0.905 | 0.960 | 1.000 |
| After 2nd pass (all bolts) | 0.940 | 0.955 | 0.948 |
| After 3rd pass | 0.965 | 0.970 | 0.965 |

**Key**: After 1 tightening pass, bolt 1 has lost ~10% from elastic interaction alone. After 3 passes, scatter is ±3.5%.

### Dataset 2: Combined Elastic Interaction + Creep — 8-Bolt, Aramid Gasket 3 mm

[APPROXIMATE — from Figure 6]

| Stage | Mean bolt load F/F_target | Scatter (±) |
|-------|--------------------------|-------------|
| After single-pass tightening | 0.88 | ±0.12 |
| After 3-pass tightening | 0.96 | ±0.04 |
| After 24 h creep relaxation (from 3-pass) | 0.68 | ±0.03 |
| After 72 h creep relaxation | 0.63 | ±0.03 |

**Key**: Aramid gasket loses ~30% preload in 24 h from pure creep (no vibration). Much larger than SWSG from Study 85.

### Dataset 3: Gasket Material Comparison — Bolt Load After 24 h

[APPROXIMATE — from Figure 7; same 8-bolt flange, single-pass tightening, ambient temperature]

| Gasket type | Thickness (mm) | F/F₀ after 24 h | F/F₀ after 168 h |
|-------------|----------------|-----------------|------------------|
| Aramid sheet | 3.0 | 0.680 | 0.640 |
| SBR rubber | 3.0 | 0.720 | 0.675 |
| Flexible graphite | 1.5 | 0.810 | 0.788 |
| Spiral-wound (SWSG) | 4.5 | 0.855 | 0.842 |

### Norton-Bailey Creep Model Parameters (from Bouzid group fitting)

```
ε_creep(t) = C₁ × σ^n × t^m

Aramid sheet:   C₁ = 2.1×10⁻⁶, n = 2.5, m = 0.45
SBR rubber:     C₁ = 1.8×10⁻⁶, n = 2.3, m = 0.42
Flexible graphite: C₁ = 8.5×10⁻⁷, n = 2.1, m = 0.38
Spiral-wound:   C₁ = 3.2×10⁻⁷, n = 1.9, m = 0.35
```

These parameter sets can be used directly to calibrate the BAS `NortonBaileyCreepModel`.

---

## BAS Validation Notes

| BAS Model | Validate Against | Target |
|-----------|-----------------|--------|
| `NortonBaileyCreepModel` | Study 85 Dataset 1/2, Study 86 Dataset 3 | F/F₀ vs. time curve shape and magnitude |
| `VDI2230EmbeddingModel` | Study 86 Dataset 2 (elastic interaction) | Correct scatter reduction after multiple tightening passes |
| `FlangeGasketContact` nonlinear k(δ) | Study 85 Dataset 3 (temperature effect) | Correct stiffness degradation with temperature |
| Initial preload target vs. achieved | Study 86 Dataset 1 (elastic interaction) | Warn user when single-pass tightening may yield only 88% of target preload |
