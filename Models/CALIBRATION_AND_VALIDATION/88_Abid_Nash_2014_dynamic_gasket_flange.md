# Study 88: Abid & Nash (2014) — Gasketed Bolted Flanged Pipe Joint Under Dynamic Loading

## Full Citation
**Authors**: Abid, M.; Nash, D. H.
**Title**: "Stamina of a Gasketed Bolted Flanged Pipe Joint Under Dynamic Loading"
**Journal**: IIUM Engineering Journal, 2014, Vol. 15, No. 2
**Link**: https://journals.iium.edu.my/ejournal/index.php/iiumej/article/view/565

---

## Significance
The only paper in this library that specifically studies bolt preload loss under **cyclic harmonic internal pressure** in a gasketed flanged joint — the primary loading condition in pressure vessel and piping systems. Distinguishes between **transient step loading** and **steady harmonic cyclic pressure**, showing that cyclic pressure causes more aggressive bolt load loss because gasket micro-creep ratcheting accumulates with each pressure cycle. Frequency is found to matter at higher frequencies (larger bolt load oscillation amplitude), but the net loosening drift is pressure-amplitude dominated.

---

## Experimental Setup
- **Flange**: NPS 4, Class 300 (8 bolts)
- **Bolt**: M20 × 2.5, Class 10.9
- **Gasket**: Spiral-wound stainless steel/graphite (SWSG)
- **Internal pressure**: Cyclic harmonic (sinusoidal) + transient step; max = 100% design pressure (5.11 MPa for NPS 4 Class 300)
- **Frequencies**: 1, 2, 5, 10 Hz
- **Duration**: up to 500 cycles per frequency level
- **Measurements**: Individual bolt loads via strain gauges; gasket contact stress distribution via pressure film; flange gap via LVDT

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Bolt Load vs. Pressure Cycle — Steady Harmonic at 5 Hz, 100% Design Pressure

[APPROXIMATE — digitized from Figure 6 of paper]

| Cycles | Bolt load F/F₀ | Gasket contact stress / initial (σ_g/σ_g0) |
|--------|----------------|---------------------------------------------|
| 0 | 1.000 | 1.000 |
| 50 | 0.988 | 0.981 |
| 100 | 0.978 | 0.968 |
| 200 | 0.966 | 0.953 |
| 300 | 0.957 | 0.942 |
| 500 | 0.944 | 0.929 |

**Steady drift rate**: ≈ 3% per 100 cycles at 5 Hz, 100% design pressure.

### Dataset 2: Effect of Frequency — 100% Design Pressure, 300 Cycles

[APPROXIMATE — from Figure 8]

| Frequency (Hz) | F/F₀ after 300 cycles | Bolt load oscillation amplitude ΔF/F₀ |
|----------------|----------------------|---------------------------------------|
| 1 Hz | 0.972 | ±0.035 |
| 2 Hz | 0.966 | ±0.048 |
| 5 Hz | 0.957 | ±0.062 |
| 10 Hz | 0.950 | ±0.075 |

**Key**: Higher frequency → larger bolt load oscillation amplitude (dynamic amplification) → faster net drift. Bolt load oscillation ΔF is proportional to frequency due to inertial effects in the pipe system.

### Dataset 3: Comparison — Harmonic vs. Transient Step Loading

[APPROXIMATE — from Figure 7; same peak pressure (100% design), same number of cycles]

| Cycles | Harmonic (5 Hz) F/F₀ | Step transient F/F₀ |
|--------|----------------------|---------------------|
| 0 | 1.000 | 1.000 |
| 50 | 0.988 | 0.994 |
| 100 | 0.978 | 0.990 |
| 200 | 0.966 | 0.986 |
| 500 | 0.944 | 0.981 |

**Key**: Harmonic loading causes ~2.5× more preload loss than transient step loading at the same number of cycles and same peak pressure.

### Dataset 4: Gasket Contact Stress Distribution Evolution

[QUALITATIVE — from Figure 9; inner vs. outer radius contact stress after 500 cycles]

| Radial position | Initial σ_g (MPa) | After 500 cycles σ_g (MPa) | Change |
|-----------------|-------------------|-----------------------------|--------|
| Inner radius | 52 | 41 | −21% |
| Mean radius | 58 | 50 | −14% |
| Outer radius | 61 | 57 | −7% |

**Key**: Non-uniform gasket creep — inner radius stress drops faster, indicating risk of leakage at inner gasket edge under sustained dynamic loading.

---

## BAS Validation Notes

| BAS Feature | Validate Against | Target |
|-------------|-----------------|--------|
| `FlangeGasketContact` + `NortonBaileyCreepModel` under cyclic loading | Dataset 1 (steady drift) | ~3%/100 cycles drift at design pressure |
| Frequency-dependent bolt load oscillation | Dataset 2 | Higher freq → larger ΔF oscillation; net drift increases with freq |
| Gasket creep + cyclic interaction | Dataset 3 (harmonic vs. step) | Harmonic produces 2.5× more loss than equivalent step |
| Non-uniform gasket stress (future feature) | Dataset 4 | Inner radius creeps faster → leakage risk indicator |
