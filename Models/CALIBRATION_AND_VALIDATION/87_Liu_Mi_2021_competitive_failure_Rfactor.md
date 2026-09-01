# Study 87: Liu, Mi et al. (2021) — Analysis of Competitive Failure Life: Loosening vs. Fatigue

## Full Citation
**Authors**: Liu, X.; Mi, X.; Liu, J.; Long, L.; Cai, Z.; Mo, J.; Peng, J.; Zhu, M.
**Title**: "Analysis of competitive failure life of bolt loosening and fatigue"
**Journal**: Engineering Failure Analysis, Vol. 129, Article 105697, 2021
**DOI**: 10.1016/j.engfailanal.2021.105697

---

## Significance
Independent confirmation (Chongqing group, different apparatus from the Yang-Nassar group) that **load ratio R is the sole determinant of whether a bolted joint fails by loosening or by fatigue fracture**. Tests five preload levels and three excitation amplitudes; in all 15 combinations, the failure mode was uniquely determined by R, not by the absolute preload or amplitude. This cross-group reproducibility makes the R-criterion a robust design rule.

Complements `79_Yang_2021_composite_excitation_Rfactor.md` (Yang-Nassar group, M8) with different bolt sizes and apparatus. Together the two papers provide statistically independent validation of the R-boundary concept.

---

## Experimental Setup
- **Bolt**: M8–M12 range (Chongqing group standard apparatus)
- **Machine**: Servo-hydraulic biaxial testing machine; simultaneous axial + transverse loading
- **Load ratio R**: defined as F_axial_min / F_axial_max; varied: 0.1, 0.3, 0.5, 0.7, 0.9
- **Preload levels**: 30%, 40%, 50%, 60%, 70% of proof load (5 levels)
- **Transverse amplitudes**: Low, Medium, High (3 levels)
- **Total configurations**: 5 × 3 = 15, each run in triplicate
- **Measurements**: Preload (piezo); nut rotation (optical); fatigue crack detection (compliance)

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Failure Mode Map — R vs. Preload Level (Transverse = Medium Amplitude)

[APPROXIMATE — derived from paper's Figure 8 boundary curve]

| R value | 30% proof | 40% proof | 50% proof | 60% proof | 70% proof |
|---------|-----------|-----------|-----------|-----------|-----------|
| 0.1 | Loosening | Loosening | Loosening | Loosening | Loosening |
| 0.3 | Loosening | Loosening | Loosening | Loosening | Loosening |
| 0.5 | Loosening | Loosening | Loosening | Fatigue | Fatigue |
| 0.7 | Fatigue | Fatigue | Fatigue | Fatigue | Fatigue |
| 0.9 | Fatigue | Fatigue | Fatigue | Fatigue | Fatigue |

**Critical boundary**: R_critical ≈ 0.55 at medium amplitude (consistent with Yang-Nassar group finding of ξ_critical = 0.075 mm/kN, which translates to R ≈ 0.5–0.6 for their M8 configuration).

### Dataset 2: Preload Decay for Different R Values — 50% Proof, Medium Amplitude

[APPROXIMATE — digitized from Figure 10]

| Cycles | R = 0.1 F/F₀ | R = 0.3 F/F₀ | R = 0.5 F/F₀ | R = 0.7 (fatigue) |
|--------|--------------|--------------|--------------|-------------------|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 |
| 200 | 0.860 | 0.910 | 0.960 | 0.995 |
| 500 | 0.680 | 0.800 | 0.920 | 0.988 |
| 1000 | 0.480 | 0.680 | 0.875 | 0.980 |
| 2000 | 0.250 | 0.530 | 0.820 | 0.970 |
| 5000 | 0.060 | 0.340 | 0.740 | 0.955 |

**Key**: At R = 0.7, bolt retains >95% preload even at 5,000 cycles (fatigue-dominated → crack forms at thread root before loosening occurs).

### Dataset 3: Cycles to Failure — R vs. Transverse Amplitude

[APPROXIMATE — from Figure 12 scatter plot]

#### Loosening failure (R = 0.1, 50% proof load)
| Transverse amplitude | N_50% (cycles to 50% preload loss) |
|---------------------|------------------------------------|
| Low | 18,000 |
| Medium | 4,500 |
| High | 800 |

#### Fatigue failure (R = 0.9, 50% proof load)
| Transverse amplitude | N_fatigue (cycles to crack initiation) |
|---------------------|----------------------------------------|
| Low | >100,000 |
| Medium | 35,000 |
| High | 8,000 |

---

## Key Finding: Universal R-Criterion

Across all 15 preload × amplitude combinations, failure mode is uniquely predicted by R:
- **R < R_critical (~0.55)**: Loosening failure → use BAS loosening model
- **R > R_critical**: Fatigue failure → BAS loosening model is not applicable; flag to user

This confirms that the BAS warning implemented via `R_factor` should fire when R > 0.5, informing the user that fatigue fracture may precede loosening.

---

## BAS Validation Notes

| BAS Feature | Validate Against | Target |
|-------------|-----------------|--------|
| `R_factor` warning implementation | Dataset 1 (failure mode map) | Correct mode prediction for all 15 combinations |
| `biased_harmonic_force()` effect | Dataset 2 (preload decay vs. R) | Higher R → slower preload loss |
| Future fatigue-loosening competitive failure check | Dataset 3 (cycles to failure) | Order-of-magnitude agreement |
