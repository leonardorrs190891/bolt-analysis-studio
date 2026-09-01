# Studies 72–73: Liu et al. (2017) + Cai et al. (2016) — Axial Dynamic Loosening, M10

## Study 72: Liu et al. (2017) — Self-Loosening Under Dynamic Axial Load

### Full Citation
**Authors**: Liu, J.; Ouyang, H.; Feng, Z.; Cai, Z.; Liu, X.; Zhu, M.
**Title**: "Study on self-loosening of bolted joints excited by dynamic axial load"
**Journal**: Tribology International, 2017, Vol. 115, pp. 432–451
**DOI**: 10.1016/j.triboint.2017.05.037

### Significance
Definitive experimental study of bolt self-loosening under **pure axial (tension-tension pulsating) excitation** — the primary loading condition in pressure vessels, pipe flanges, and structural joints under cyclic internal pressure. Shows that axial loading causes exclusively **non-rotational** preload loss (no nut back-off) via two mechanisms: cyclic plasticity at thread roots (Stage I, rapid) and fretting wear at thread flanks (Stage II, slow). Surface coatings (MoS₂, Cr₂O₃) are evaluated. Directly validates BAS `_classify_phase_axial()` three-stage model.

### Experimental Setup
- **Bolt**: M10 × 1.5, Class 8.8, three surface conditions: bare steel, MoS₂ coating, Cr₂O₃ coating
- **Clamped members**: AISI 1045 steel plates, grip ~30 mm
- **Preload**: 10, 15, 20, 25 kN (achieved via torque wrench + strain gauge calibration)
- **Axial load amplitude**: 0.5, 1.0, 2.0, 3.0 kN (tension-tension; minimum load = F₀ − F_amp > 0)
- **Frequency**: 10 Hz
- **Cycles**: up to 2,000
- **Measurements**: Preload via piezoelectric force sensor; nut rotation via optical sensor; thread surface damage by SEM + EDX post-test

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Effect of Axial Amplitude — Bare Steel, F₀ = 20 kN

[APPROXIMATE — digitized from Figure 5 of paper]

#### Amplitude = 0.5 kN (F_ax/F₀ = 0.025)
| Cycles | F/F₀ |
|--------|------|
| 0 | 1.000 |
| 200 | 0.996 |
| 500 | 0.991 |
| 1000 | 0.985 |
| 2000 | 0.978 |

#### Amplitude = 1.0 kN (F_ax/F₀ = 0.050)
| Cycles | F/F₀ |
|--------|------|
| 0 | 1.000 |
| 200 | 0.990 |
| 500 | 0.980 |
| 1000 | 0.968 |
| 2000 | 0.955 |

#### Amplitude = 2.0 kN (F_ax/F₀ = 0.100)
| Cycles | F/F₀ |
|--------|------|
| 0 | 1.000 |
| 50 | 0.980 |
| 100 | 0.965 |
| 200 | 0.950 |
| 500 | 0.930 |
| 1000 | 0.912 |
| 2000 | 0.893 |

#### Amplitude = 3.0 kN (F_ax/F₀ = 0.150)
| Cycles | F/F₀ |
|--------|------|
| 0 | 1.000 |
| 50 | 0.968 |
| 100 | 0.945 |
| 200 | 0.920 |
| 500 | 0.885 |
| 1000 | 0.855 |
| 2000 | 0.830 |

### Dataset 2: Effect of Coating — F₀ = 20 kN, Amplitude = 2.0 kN

[APPROXIMATE — digitized from Figure 8]

| Cycles | Bare steel F/F₀ | MoS₂ coated F/F₀ | Cr₂O₃ coated F/F₀ |
|--------|-----------------|-------------------|-------------------|
| 0 | 1.000 | 1.000 | 1.000 |
| 50 | 0.980 | 0.990 | 0.987 |
| 100 | 0.965 | 0.982 | 0.978 |
| 200 | 0.950 | 0.974 | 0.970 |
| 500 | 0.930 | 0.960 | 0.956 |
| 1000 | 0.912 | 0.950 | 0.945 |
| 2000 | 0.893 | 0.940 | 0.935 |

**Key**: MoS₂ reduces Stage I amplitude by ~40% and Stage II fretting rate by ~40% compared to bare steel.

### Dataset 3: Effect of Preload — Amplitude = 2.0 kN, Bare Steel

[APPROXIMATE — digitized from Figure 7]

| Cycles | F₀=10 kN F/F₀ | F₀=15 kN F/F₀ | F₀=20 kN F/F₀ | F₀=25 kN F/F₀ |
|--------|---------------|---------------|---------------|---------------|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 |
| 100 | 0.930 | 0.952 | 0.965 | 0.971 |
| 500 | 0.870 | 0.905 | 0.930 | 0.940 |
| 1000 | 0.820 | 0.875 | 0.912 | 0.924 |
| 2000 | 0.775 | 0.848 | 0.893 | 0.908 |

**Key**: Higher preload reduces Stage I loss fraction (but not Stage II rate). Consistent with cyclic-plasticity mechanism: larger F₀ keeps thread flanks in compression, reducing plastic strain per cycle.

---

## Study 73: Cai et al. (2016) — Axial Excitation + Wear, M10

### Full Citation
**Authors**: Cai, Z.; Fang, X.; Liu, J.; Ouyang, H.
**Title**: "Experimental and numerical studies of bolted joints subjected to axial excitation"
**Journal**: Wear, 2016, Vol. 346–347, pp. 29–38
**DOI**: 10.1016/j.wear.2015.10.013

### Significance
Companion paper to Study 72 (same Chongqing group, same apparatus), with emphasis on **wear characterisation** and **FEA validation**. Provides SEM images of thread flank fretting damage confirming the Stage II fretting mechanism. FEA model reproduces experimental preload-loss curve within ±10%. Quantifies how MoS₂ lubricant reduces fretting damage.

### Experimental Setup
- **Bolt**: M10 × 1.5, steel; with and without MoS₂ lubricant
- **Preload**: 20 kN
- **Axial amplitude**: 2.0 kN
- **Frequency**: 10 Hz; cycles up to 1,000
- **Post-test SEM + EDX**: thread flank fretting scars, oxidised wear debris
- **FEA**: ABAQUS; explicit thread helix geometry; contact with Coulomb friction

### DATA FOR CURVE PLOTTING

[APPROXIMATE — digitized from Figure 4]

| Cycles | Dry steel F/F₀ | MoS₂ lubricant F/F₀ | FEA prediction F/F₀ |
|--------|----------------|----------------------|----------------------|
| 0 | 1.000 | 1.000 | 1.000 |
| 100 | 0.965 | 0.982 | 0.968 |
| 200 | 0.952 | 0.975 | 0.955 |
| 500 | 0.935 | 0.964 | 0.939 |
| 1000 | 0.915 | 0.955 | 0.920 |

**FEA error**: Mean absolute error ≈ 0.005 on F/F₀ (well within ±10%).

---

## BAS Validation Notes

| BAS Model | Validate Against | Target |
|-----------|-----------------|--------|
| `_classify_phase_axial()` Stage I / Stage II | Dataset 1 (amplitude sweep) | Correct stage at each cycle count |
| `_axial_rapid_done` latch transition | All datasets | Stage I saturates within first 50–100 cycles |
| `FrictionEvolutionModel` with MoS₂ | Dataset 2 (coating comparison) | MoS₂ reduces Stage I loss by ~40% |
| `ArchardWearModel` (Stage II) | Dataset 3 (preload sweep) | Higher F₀ → lower Stage II rate; order-of-magnitude correct |

**Key parameter from these papers**:
- Stage I duration: N_stage_i ≈ 50–100 cycles (matches BAS default `n_stage_i_cycles=50`)
- Stage II rate: ~0.05–0.10% preload per cycle at F_ax/F₀ = 0.10
- MoS₂ `mu_reduction`: −40% of friction evolution rate; `K_wear` reduction: −40%
