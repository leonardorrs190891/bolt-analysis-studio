# Studies 94–95: Li, Luo et al. (2022) — Structural Similitude for Rotor Systems with Bolted Joints

## Study 94: Li, Luo et al. (2022) — Scaled Rotor System Considering Bolted Joint Stiffness

### Full Citation
**Authors**: Li, L.; Luo, Z.; Li, Y.; He, F.; Li, X.; Yan, X.
**Title**: "Structural similitude for a scaled rotor system considering stiffness characteristics of bolted joints"
**Journal**: Proceedings of the Institution of Mechanical Engineers, Part C: Journal of Mechanical Engineering Science, 2022, Vol. 236, No. 10, pp. 5192–5207
**DOI**: 10.1177/09544062211059736

---

## Significance
Derives **Buckingham Pi scaling laws for rotor systems that include bolted flanged joints** — accounting for the nonlinear stiffness of the joint interface. This is the first study to demonstrate that geometric similitude alone (scale factor applied to all lengths) fails for bolted joint systems because the joint contact stiffness does not scale linearly with geometry. The joint stiffness nonlinearity must be **explicitly included** in the scaling rules.

Key result: 1:3 scale model → prototype frequency predictions within **5.4% error** on first four bending modes, when joint stiffness nonlinearity is included. Without joint stiffness correction, error grows to **18–25%**.

Directly relevant to the BAS Similitude tab (Tab 4) — specifically the claim that scaled model test predictions can be applied to full-scale prototype bolted joints. This paper quantifies the joint stiffness correction needed for valid scale prediction.

---

## Experimental Setup
- **System**: Rotor shaft + disk + flanged bolted joint (turbomachinery representative)
- **Scale ratio**: 1:3 (model bolt ≈ M10, prototype bolt ≈ M30)
- **Materials**: Model and prototype use same steel; alternative material scaling explored analytically
- **Bolted joint type**: Multi-bolt flange (4 bolts in model, 12 bolts in prototype)
- **Measurements**: Natural frequencies via modal hammer + accelerometers; mode shapes via laser vibrometer
- **Analysis**: FEM + analytical Buckingham Pi derivation

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Natural Frequency Prediction — Prototype from Scale Model

[QUANTITATIVE — from Table 3 of paper]

| Mode | Predicted f (Hz) from scaled model | Measured f (Hz) on prototype | Error (%) |
|------|------------------------------------|------------------------------|-----------|
| 1st bending | 48.2 | 45.8 | +5.24% |
| 2nd bending | 127.4 | 121.8 | +4.60% |
| 3rd bending | 256.8 | 246.2 | +4.30% |
| 4th bending | 412.5 | 393.7 | +4.77% |
| Mean error | — | — | **4.73%** |

Without joint stiffness correction:
| Mode | Error without correction |
|------|--------------------------|
| 1st bending | 18.4% |
| 2nd bending | 22.1% |
| 3rd bending | 19.8% |
| 4th bending | 24.6% |

### Dataset 2: Scaling Laws Derived

For a rotor system with bolted joints, the scaling relationships are:

| Quantity | Symbol | Scaling relation | Notes |
|----------|--------|-----------------|-------|
| Length | L | λ_L = L_m/L_p | Geometric scale factor |
| Frequency | f | λ_f = λ_L^(-1) | Standard; valid for uniform structures |
| Joint stiffness | k_joint | λ_k = λ_L × (λ_E × λ_A_contact) | NOT simply λ_L^2 — requires contact area scaling |
| Natural frequency (corrected) | f_n | λ_f^corrected = λ_L^(-1) × (1 + δ_joint_correction) | δ ≈ 0.05–0.15 depending on joint dominance |
| Bolt preload fraction | F/Fy | Must be identical in model and prototype | Critical — do not scale preload force; scale preload fraction |

**Joint stiffness correction factor** (from paper's analytical derivation):
```
δ_joint = (k_joint / k_shaft) × (1 − λ_L^2)

For 1:3 scale (λ_L = 1/3):
δ_joint ≈ (k_joint / k_shaft) × (1 − 1/9) = 0.889 × (k_joint / k_shaft)
```
If k_joint / k_shaft ≈ 0.15 (typical for a bolted flange), δ ≈ 0.133 → 13% correction to frequency scaling.

---

## Study 95: Li, Wen, Luo & Jin (2022) — Similitude for Dual-Rotor System with Bolted Joints

### Full Citation
**Authors**: Li, Y.; Wen, C.; Luo, Z.; Jin, L.
**Title**: "Similitude for the Dynamic Characteristics of Dual-Rotor System with Bolted Joints"
**Journal**: Mathematics, 2022, Vol. 10, No. 1, Article 3
**DOI**: 10.3390/math10010003
**Open Access**: https://www.mdpi.com/2227-7390/10/1/3

---

## Significance
Extends Study 94 to **dual-rotor** (counter-rotating inner + outer shaft, typical of turbofan aero-engines) with bolted flange connections on both shafts. Derives a complete set of Buckingham Pi groups that account for:
- Shaft bending stiffness (scales as E×I = E×d⁴)
- Disk polar moment of inertia (scales as ρ×d⁵)
- Bolted joint stiffness (contact mechanics scaling, as in Study 94)
- Inter-shaft bearing stiffness

Key result: amplitude scaling factors AND frequency scaling factors both validated with < 5% error on a 1:3 scale dual-rotor rig.

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Amplitude and Frequency Scaling Factors

[QUANTITATIVE — from Table 4 of paper; λ_L = 1/3]

| Quantity | Theoretical scaling factor | Experimental ratio (model/prototype) | Deviation |
|----------|---------------------------|-------------------------------------|-----------|
| Frequency (Hz) | λ_f = 3.0 | Measured: 2.91 | 3.0% |
| Vibration amplitude (mm) | λ_x = 1/3 | Measured: 0.335 | 0.5% |
| Imbalance force (N) | λ_F = 1/9 | Measured: 0.114 | 2.6% |
| Joint natural frequency (coupled) | λ_f,joint = 2.78 (corrected) | Measured: 2.74 | 1.4% |

### Dataset 2: Frequency Response Comparison — Prototype Prediction from Scale Model

[APPROXIMATE — from Figure 8; frequency response at a representative rotor speed]

| Rotor speed (RPM, prototype scale) | Vibration amplitude (mm, prototype) | Amplitude from scale-model prediction | Error |
|-------------------------------------|-------------------------------------|--------------------------------------|-------|
| 2,000 | 0.048 | 0.051 | 6.3% |
| 4,000 | 0.112 | 0.108 | 3.6% |
| 6,000 | 0.385 | 0.371 | 3.6% |
| 8,000 (resonance) | 1.240 | 1.195 | 3.6% |
| 10,000 | 0.318 | 0.307 | 3.5% |

---

## BAS Similitude Tab Validation Notes

### What These Papers Validate (Studies 94 + 95)

| BAS Similitude Feature | Validated By | Target |
|-----------------------|-------------|--------|
| Geometric scaling factor (M20 → M42) | Study 94 Dataset 1 (frequency prediction < 5.4%) | BAS frequency/stiffness prediction within 5–10% |
| Joint stiffness nonlinearity in scaling | Study 94 Dataset 2 (correction factor) | Apply joint stiffness correction when k_joint/k_shaft > 0.05 |
| Multi-bolt flange scaling (circular pattern) | Study 95 Dataset 1 (amplitude + freq scaling) | Amplitude scales as λ_L; frequency as λ_L^(-1) |
| Same preload fraction rule | Study 94 Dataset 2 (preload scaling rule) | BAS must enforce identical F/Fy in model and prototype |

### Practical Implementation in BAS Similitude Tab

The BAS Geometric Scaling sub-tab should warn when:
```
k_joint_estimated / k_structure_estimated > 0.10
```
In this case, the joint-stiffness correction factor should be applied:
```
f_prototype_corrected = f_prototype_simple × (1 + δ_joint)
where δ_joint = 0.889 × (k_joint/k_shaft) × (1/scale_factor² − 1)
```

**For the S1 validation case (M20 → M42, Karlsen 2022)**:
- k_joint/k_shaft is small (Junker-type loosening rig, not a rotor)
- Joint stiffness correction: negligible (< 2%)
- BAS Similitude tab result: valid as-is

**For wind turbine or aero-engine application** (Studies 94/95 scenario):
- k_joint/k_shaft ≈ 0.10–0.20
- Correction required: δ_joint ≈ 10–18%
- BAS should display a warning and show the corrected prediction
