# Studies 83–84: Pai & Hess (2002/2003) — Thread Geometry + Multi-Bolt Loosening

## Study 83: Pai & Hess (2002) — Experimental Study, Fine vs. Coarse Thread + Slip Classification

### Full Citation
**Authors**: Pai, N. G.; Hess, D. P.
**Title**: "Experimental study of loosening of threaded fasteners due to dynamic shear loads"
**Journal**: Journal of Sound and Vibration, 2002, Vol. 253, No. 3, pp. 585–602
**DOI**: 10.1006/jsvi.2001.4006

### Significance
The **original Pai-Hess experimental paper** that established the four-slip-classification taxonomy used throughout the self-loosening literature. Tests both coarse thread (5/16-18 UNC, ≈M8) and fine thread (5/16-24 UNF, ≈M8 fine) under identical Junker-type conditions, directly quantifying the thread pitch effect. Fine thread requires **25–35% higher shear force** to initiate complete rotational loosening. The four slip types are:

1. **Localized head + Localized thread**: Neither interface fully sliding; no rotational loosening
2. **Localized head + Complete thread**: Thread slides but head sticks; torque builds without preload loss
3. **Complete head + Localized thread**: Head slides but thread sticks; unusual, rare
4. **Complete head + Complete thread**: Both interfaces slide; rapid rotational loosening (Stage II)

This taxonomy is the experimental basis for BAS `compute_fretting_regime()` in `contacts/base.py`.

---

## Experimental Setup
- **Bolt**: 5/16-18 UNC (coarse thread) and 5/16-24 UNF (fine thread), Grade 5 (SAE), steel on steel
- **Apparatus**: Junker-type transverse vibration rig (Hess group, USF Tampa)
- **Shear load**: sinusoidal, 5 Hz; amplitude varied from sub-threshold to gross slip
- **Preload**: 50%, 70%, 90% of proof load
- **Head contact conditions**: free (can slide), constrained (cannot slide)
- **Measurements**: Preload via piezoelectric load cell; nut rotation; head sliding via LVDT

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Critical Shear Force for Rotational Loosening — Fine vs. Coarse Thread

[APPROXIMATE — digitized from Figures 4 and 7 of paper]

| Preload (% proof) | UNC Coarse — F_crit (N) | UNF Fine — F_crit (N) | UNF/UNC ratio |
|-------------------|-------------------------|-----------------------|---------------|
| 50% | 1,820 | 2,340 | 1.29 |
| 70% | 2,550 | 3,300 | 1.29 |
| 90% | 3,280 | 4,230 | 1.29 |

**Key**: Fine thread consistently requires ~29% higher critical force → consistent with helix angle theory (finer pitch → smaller helix angle → larger back-off torque barrier).

### Dataset 2: Preload Decay for Complete-Slip Condition (Type 4) — Coarse vs. Fine

[APPROXIMATE — digitized from Figure 9; both at 90% proof load, same shear amplitude]

| Cycles | UNC Coarse F/F₀ | UNF Fine F/F₀ |
|--------|-----------------|---------------|
| 0 | 1.000 | 1.000 |
| 10 | 0.940 | 0.975 |
| 25 | 0.840 | 0.920 |
| 50 | 0.680 | 0.830 |
| 100 | 0.430 | 0.690 |
| 200 | 0.180 | 0.510 |
| 300 | 0.040 | 0.360 |

### Dataset 3: Preload Decay by Slip Type — UNC, 70% Proof Load

[APPROXIMATE — from Figure 11 family of curves]

| Cycles | Type 1 (localized/localized) | Type 2 (localized head) | Type 4 (complete/complete) |
|--------|------------------------------|-------------------------|---------------------------|
| 0 | 1.000 | 1.000 | 1.000 |
| 100 | 0.985 | 0.970 | 0.500 |
| 500 | 0.972 | 0.940 | 0.080 |
| 1000 | 0.965 | 0.920 | 0.010 |

**Key**: Only Type 4 (complete slip at BOTH thread AND bearing) leads to rapid rotational loosening. Type 1 and Type 2 produce only Stage I non-rotational loss.

---

## Study 84: Pai & Hess (2003) — Multi-Bolt Placement, Loosening Cascade

### Full Citation
**Authors**: Pai, N. G.; Hess, D. P.
**Title**: "Influence of fastener placement on vibration-induced loosening"
**Journal**: Journal of Sound and Vibration, 2003, Vol. 268, pp. 617–626
**DOI**: 10.1016/S0022-460X(03)00202-X

### Significance
**The foundational multi-bolt loosening experiment.** Tests groups of 1/4-20 UNC cap screws in aluminum plate specimens with various bolt spacing and pattern configurations under 5 Hz transverse vibration. Establishes that:
1. **Edge bolts loosen faster** than centre bolts (higher local slip amplitude)
2. **Loosening of one bolt redistributes load** to adjacent bolts, accelerating their loosening
3. **Cascade loosening** occurs: once the first bolt reaches Stage II, the group progressively fails
4. **Multi-bolt groups cannot be predicted from single-bolt analysis** — the interaction is essential

Directly relevant to implementing multi-bolt mode in BAS and validating the `S2_Similitude_Multi_Bolt_Reduction` case.

---

## Experimental Setup
- **Bolt**: 1/4-20 UNC (≈M6) cap screws in aluminum plate specimens
- **Patterns tested**: Single row (2–5 bolts), double row (2×2, 2×3), edge vs. interior positions
- **Loading**: 5 Hz transverse vibration, displacement-controlled (fixed amplitude)
- **Preload**: Torque-controlled (uniform initial preload)
- **Measurements**: Individual bolt preload via load cells in each bolt hole; nut rotation per bolt

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Two-Bolt Row — Edge vs. Centre Position Effect

[APPROXIMATE — digitized from Figure 5 of paper]

Two bolts in a row perpendicular to vibration direction. The two bolts are labelled "Edge" (at the specimen edge, maximum slip amplitude) and "Centre" (at specimen centreline).

| Cycles | Edge bolt F/F₀ | Centre bolt F/F₀ |
|--------|----------------|-----------------|
| 0 | 1.000 | 1.000 |
| 50 | 0.880 | 0.940 |
| 100 | 0.730 | 0.890 |
| 200 | 0.480 | 0.820 |
| 300 | 0.230 | 0.745 |
| 500 | 0.060 | 0.650 |
| 700 | 0.010 | 0.545 |
| 1000 | 0.005 | 0.420 |

**Key**: Edge bolt enters Stage II at ≈100 cycles; centre bolt only reaches Stage II after the edge bolt has lost most preload (load redistribution effect).

### Dataset 2: Four-Bolt Group (2×2) — Individual Bolt Preload Decay

[APPROXIMATE — digitized from Figure 8; bolt positions: A=edge-edge, B=edge-centre, C=centre-edge, D=centre-centre]

| Cycles | Bolt A (corner) | Bolt B (edge) | Bolt C (edge) | Bolt D (centre) |
|--------|-----------------|---------------|---------------|-----------------|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 |
| 50 | 0.840 | 0.900 | 0.890 | 0.960 |
| 100 | 0.620 | 0.800 | 0.790 | 0.920 |
| 200 | 0.330 | 0.680 | 0.670 | 0.870 |
| 400 | 0.090 | 0.530 | 0.520 | 0.790 |
| 600 | 0.010 | 0.370 | 0.360 | 0.700 |
| 800 | 0.005 | 0.240 | 0.240 | 0.590 |
| 1200 | 0.005 | 0.080 | 0.090 | 0.440 |
| 1600 | 0.005 | 0.010 | 0.015 | 0.290 |

**Cascade sequence**: A → B ≈ C → D (corner bolt fails first, then edges, then centre).

### Dataset 3: Effect of Bolt Spacing on Loosening Rate

[APPROXIMATE — digitized from Figure 10; single bolt row, 3 bolts, spacing varied]

| Cycles | Narrow spacing (edge bolt) | Medium spacing (edge bolt) | Wide spacing (edge bolt) |
|--------|---------------------------|---------------------------|--------------------------|
| 0 | 1.000 | 1.000 | 1.000 |
| 100 | 0.680 | 0.740 | 0.800 |
| 200 | 0.370 | 0.460 | 0.580 |
| 400 | 0.090 | 0.200 | 0.340 |
| 600 | 0.010 | 0.060 | 0.180 |

**Key**: Narrower bolt spacing → greater load redistribution → faster cascade loosening.

---

## BAS Validation Notes

### Study 83 (Thread Geometry)

| BAS Feature | Validate Against | Target |
|-------------|-----------------|--------|
| `check_slip_condition()` with Pai-Hess `slip_onset_factor=0.46` | Dataset 1 (F_crit vs. thread type) | Fine thread: ~29% higher F_crit predicted |
| `compute_fretting_regime()` → 4 regime types | Dataset 3 (slip type preload curves) | Type 4 only → rapid Stage II; Type 1/2 → slow Stage I only |

### Study 84 (Multi-Bolt)

| BAS Feature | Validate Against | Target |
|-------------|-----------------|--------|
| Future multi-bolt mode | Dataset 2 (4-bolt group) | Cascade sequence A→B→C→D; corner first |
| `S2_Similitude_Multi_Bolt_Reduction` | Dataset 1 (edge vs. centre) | Edge bolt = worst case; use edge bolt data for single-bolt model |
| `slip_onset_factor` scaling with position | Dataset 3 (spacing effect) | Smaller spacing → higher effective slip amplitude → faster loosening |
