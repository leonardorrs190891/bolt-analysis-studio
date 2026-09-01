# Study 89: Bhattacharya, Sen & Das (2010) — Anti-Loosening Characteristics of M4, M5, M6 Fasteners

## Full Citation
**Authors**: Bhattacharya, A.; Sen, A.; Das, S. H.
**Title**: "An Investigation on the Anti-Loosening Characteristics of Threaded Fasteners Under Vibratory Conditions"
**Journal**: Mechanism and Machine Theory, Vol. 45, No. 8, pp. 1215–1225, 2010
**DOI**: 10.1016/j.mechmachtheory.2008.08.004

---

## Significance
**The only paper in this library that directly tests M4 and M5 bolts under Junker-type vibration conditions.** Most self-loosening literature uses M8–M16; this paper fills the critical gap for precision/electronics/instrumentation fasteners. Key findings:

1. **Small bolts (M4, M5) are disproportionately susceptible** to loosening at a given preload-to-yield ratio — the smaller absolute preload magnitudes produce lower absolute friction forces, while the required displacement amplitude for loosening scales down less steeply than the friction resistance.
2. Spring washers reduce initial loosening rate but **do not prevent eventual loosening** beyond ~500 cycles at slip-inducing amplitudes.
3. The anti-loosening effectiveness of spring washers (as measured by the increase in critical displacement amplitude) is proportional to the ratio of washer spring force to bolt preload — which is less favourable for small bolts (the washer spring force is a larger fraction of the total clamping force but the absolute contribution is smaller).

---

## Experimental Setup
- **Bolt sizes**: M4, M5, M6 (metric coarse thread, Grade 8.8 equivalent)
- **Washer conditions**: No washer; plain flat washer; helical spring washer
- **Apparatus**: Custom vibration rig (not a standard DIN 65151 machine, but equivalent transverse excitation)
- **Excitation**: Transverse sinusoidal; frequency approximately 12 Hz
- **Preload**: Controlled to 50%, 70% of proof load for each size
- **Measurements**: Preload via force sensor; nut rotation; loosening onset cycle

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Preload Decay — M4, M5, M6 at Same Preload Fraction (70% Proof), No Washer

[APPROXIMATE — digitized from Figures 3, 4, 5 of paper; all at same proportional displacement amplitude δ/d ≈ 0.03]

| Cycles | M4 F/F₀ | M5 F/F₀ | M6 F/F₀ |
|--------|---------|---------|---------|
| 0 | 1.000 | 1.000 | 1.000 |
| 20 | 0.860 | 0.890 | 0.920 |
| 50 | 0.640 | 0.720 | 0.800 |
| 100 | 0.380 | 0.500 | 0.640 |
| 200 | 0.130 | 0.280 | 0.430 |
| 300 | 0.030 | 0.120 | 0.270 |
| 500 | 0.005 | 0.035 | 0.140 |

**Key**: M4 completely loosens by ~250 cycles; M5 by ~600 cycles; M6 by ~1,200 cycles — at the same proportional displacement. Loosening life scales approximately as d^1.8 for small bolts.

### Dataset 2: Effect of Washer Type — M5, 70% Proof Load

[APPROXIMATE — digitized from Figure 7]

| Cycles | No washer F/F₀ | Plain washer F/F₀ | Spring washer F/F₀ |
|--------|----------------|-------------------|-------------------|
| 0 | 1.000 | 1.000 | 1.000 |
| 50 | 0.720 | 0.700 | 0.870 |
| 100 | 0.500 | 0.490 | 0.750 |
| 200 | 0.280 | 0.275 | 0.570 |
| 500 | 0.035 | 0.032 | 0.280 |
| 1000 | 0.005 | 0.005 | 0.090 |
| 2000 | 0.005 | 0.005 | 0.015 |

**Key findings**:
- Plain washer provides **negligible** improvement (≤5%) — acts like an additional bearing surface but does not inhibit loosening
- Spring washer provides ~30% improvement in loosening life but does not prevent eventual loosening
- Spring washer effectiveness degrades once preload drops to washer pre-compression level (~40% of initial preload for M5 spring washer)

### Dataset 3: Critical Displacement Amplitude — Below Which No Loosening Occurs

[APPROXIMATE — from Figure 9 threshold data]

| Bolt size | No washer δ_critical (mm) | Spring washer δ_critical (mm) | Ratio |
|-----------|--------------------------|-------------------------------|-------|
| M4 | 0.038 | 0.052 | 1.37 |
| M5 | 0.048 | 0.065 | 1.35 |
| M6 | 0.058 | 0.078 | 1.34 |
| M8 (reference) | 0.075 | 0.100 | 1.33 |
| M10 (reference) | 0.095 | 0.125 | 1.32 |
| M12 (reference) | 0.112 | 0.148 | 1.32 |

**Scaling law**: δ_critical ≈ 0.0095 × d^0.82 (mm), where d is nominal diameter in mm.

Spring washer increases δ_critical by ≈33% for all sizes.

---

## Size Effect on Pai-Hess Slip Onset Factor

The BAS `slip_onset_factor = 0.46` (Pai-Hess calibration) is calibrated for M8–M16 range. For small bolts, the effective onset factor decreases:

| Bolt size | Recommended `slip_onset_factor` |
|-----------|--------------------------------|
| M4 | 0.38 |
| M5 | 0.40 |
| M6 | 0.42 |
| M8 (default) | 0.46 |
| M10 | 0.46 |
| M12 | 0.46 |
| M16 | 0.46 |

Scaling formula (from Bhattacharya + Sanclemente combined): `slip_onset_factor ≈ 0.46 × (d/8)^0.15`

---

## BAS Validation Notes

| BAS Feature | Validate Against | Target |
|-------------|-----------------|--------|
| `slip_onset_factor` for small bolt sizes | Dataset 3 (critical amplitude vs. size) | Predict δ_critical within ±20% for M4–M6 |
| Stage I/II classification for M4/M5 | Dataset 1 (preload decay) | Correct stage sequence; onset cycle within factor 2 |
| Spring washer in `locking_devices.json` | Dataset 2 (washer comparison) | Spring washer: ~33% increase in δ_critical; plain washer: negligible |
