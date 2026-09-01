# Study 79: Yang, Nassar & Wu (2021) — Competitive Failure Under Composite Excitation; Stress Ratio R

## Full Citation
**Authors**: Yang, X.; Nassar, S. A.; Wu, Z.
**Title**: "Competitive Failure of Loosening and Fatigue of Bolts under Composite Excitation"
**Journal**: Shock and Vibration, 2021, Article 1441122
**DOI**: 10.1155/2021/1441122

---

## Significance
Companion paper to Yang et al. (2021) *Chinese J. Mech. Eng.* (already in folder as `13_Yang_2021_combined_loading.md`). While that paper established the critical load ratio ξ_critical = 0.075 mm/kN as the failure mode boundary, **this paper systematically varies the axial stress ratio R_axial = F_axial_min / F_axial_max** as an independent parameter and shows how R shifts the failure mode boundary curve. Fully-reversed axial loading (R = −1) combined with transverse excitation is the most aggressive combination because the compressive half-cycle partially unloads the bearing surface, enabling larger interface slip during the tensile half-cycle.

This paper directly validates the BAS `R_factor` VDI field in `LoadingData` and the `biased_harmonic_force()` function in `time_integration.py`.

---

## Experimental Setup
- **Bolt**: M8 × 1.25 × 70, Grade 8.8
- **Machine**: MTS servo-hydraulic tensile-torsion testing machine
- **Axial load**: sinusoidal pulsating; R_axial = F_min/F_max varied: −1.0, −0.5, 0.0, 0.1, 0.5
- **Transverse load**: sinusoidal, fixed amplitude range
- **Preload levels**: 30%, 50%, 70% of proof load (≈ 8.0, 13.3, 18.6 kN for M8 Grade 8.8)
- **Cycles**: 2,000–50,000 depending on failure mode
- **Measurements**: Preload via piezoelectric sensor; nut rotation via laser sensor; fatigue crack detection via compliance change

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Failure Mode Map — R_axial vs. ξ (Transverse/Axial Load Ratio)

[APPROXIMATE — digitized from Figure 6 of paper]

| R_axial | ξ_critical (mm/kN) | Dominant failure mode below ξ_critical |
|---------|-------------------|----------------------------------------|
| 0.5 | 0.110 | Fatigue fracture |
| 0.1 | 0.090 | Fatigue fracture |
| 0.0 (tension-zero) | 0.075 | Fatigue fracture |
| −0.5 | 0.052 | Fatigue fracture |
| −1.0 (fully reversed) | 0.038 | Fatigue fracture |

**Interpretation**: As R decreases (more compressive), ξ_critical decreases → loosening dominates over a wider range of transverse amplitudes. Fully-reversed axial loading makes the bolt most susceptible to loosening because bearing-surface friction is periodically removed.

### Dataset 2: Preload Decay — R_axial = 0.0, F₀ = 70% Proof (≈ 18.6 kN), ξ = 0.10 mm/kN (Loosening-Dominant)

[APPROXIMATE — digitized from Figure 8]

| Cycles | R= −1.0 F/F₀ | R= 0.0 F/F₀ | R= 0.5 F/F₀ |
|--------|--------------|-------------|-------------|
| 0 | 1.000 | 1.000 | 1.000 |
| 100 | 0.870 | 0.920 | 0.960 |
| 500 | 0.640 | 0.760 | 0.870 |
| 1000 | 0.440 | 0.610 | 0.800 |
| 2000 | 0.250 | 0.460 | 0.740 |
| 5000 | 0.080 | 0.280 | 0.660 |

**Key**: R = −1 produces >3× faster loosening than R = 0.5 at the same transverse amplitude.

### Dataset 3: Cycles to 50% Preload Loss — Effect of R_axial and Preload Level

[APPROXIMATE — from Figure 10 contour data]

| Preload Level | R = 0.5 | R = 0.0 | R = −1.0 |
|---------------|---------|---------|----------|
| 30% proof | 8,500 | 3,200 | 1,100 |
| 50% proof | 14,000 | 5,500 | 2,000 |
| 70% proof | 22,000 | 9,000 | 3,400 |

---

## Key Equations for BAS Implementation

### Critical Load Ratio as Function of R_axial
From Yang et al. combined data (this paper + `13_Yang_2021_combined_loading.md`):

```
ξ_critical(R) ≈ 0.075 × [1 + 0.47 × R]   (R ∈ [−1, +1])
```

- R = 0 → ξ_critical = 0.075 mm/kN  (standard tension-zero)
- R = −1 → ξ_critical = 0.038 mm/kN  (fully reversed, most aggressive)
- R = +1 → ξ_critical = 0.112 mm/kN  (constant tension, most resistant)

### BAS Implementation Check
```python
# In _run_analysis() after bolt geometry assignment:
R = config.coupled_loosening_config.R_factor  # from LoadingData.R_factor
xi = delta_amplitude_mm / (F_preload_N / 1000)  # mm / kN
xi_critical = 0.075 * (1 + 0.47 * R)
if xi < xi_critical:
    # Fatigue-dominated mode — loosening model may overpredict
    emit_warning(f"Load ratio ξ={xi:.3f} < ξ_critical={xi_critical:.3f}: fatigue fracture may precede loosening")
```

---

## BAS Validation Notes

| BAS Feature | Validate Against | Target |
|-------------|-----------------|--------|
| `R_factor` in `LoadingData` | Dataset 1 (failure mode map) | Correct R-dependent boundary |
| `biased_harmonic_force()` with R < 0 | Dataset 2 (preload decay vs. R) | R=−1 produces 3× faster loosening than R=0.5 |
| Phase classification under combined loading | Dataset 2 | RUNAWAY or ROTATIONAL phase within 1000 cycles for R=−1, ξ=0.10 |
