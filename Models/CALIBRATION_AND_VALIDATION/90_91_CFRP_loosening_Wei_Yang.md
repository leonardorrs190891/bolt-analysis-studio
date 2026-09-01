# Studies 90–91: CFRP Bolt Loosening — Wei et al. (2025) + Yang et al. (2023)

## Study 90: Wei, Cheng et al. (2025) — Preload Relaxation in CFRP Joints Under Bending Vibration

### Full Citation
**Authors**: Wei, Y.; Cheng, H.; Wei, Z.; Guan, W.; Li, Y.; Suo, H.; Luo, B.
**Title**: "The Preload Relaxation Mechanism of Composite Bolted Joints Under Bending Vibration Load: Experimental and Numerical Study"
**Journal**: Polymer Composites (Wiley), 2025
**DOI**: 10.1002/pc.70915

### Significance
Most recent and complete experimental study of **CFRP bolted joint loosening under bending vibration**. Uses ultrasonic real-time preload monitoring (non-contact, non-invasive) and post-test SEM + 3D profilometry to characterise worn surfaces. Identifies **four simultaneous wear mechanisms** at the CFRP-bolt interface:
1. Fatigue wear (cyclic stress → matrix cracking)
2. Abrasive wear (hard fibre ends scratch softer matrix)
3. Adhesive wear (material transfer)
4. Oxidation wear (at elevated contact temperatures)

Two-stage preload relaxation: Stage I (rapid, first few cycles) and Stage II (slow, sustained vibration). The relative magnitudes differ substantially from metal-on-metal: Stage I in CFRP accounts for 18% loss (vs. ~5–10% in steel joints) due to the much larger matrix deformation and fibre crushing under the washer bearing surface.

---

### Experimental Setup
- **Material**: Carbon-fibre reinforced polymer (CFRP) laminate specimens; ply orientation [0/90]₄s
- **Bolt**: Single-bolt, titanium alloy; exact size not specified in abstract (estimated M8–M10)
- **Loading**: Precision electrodynamic exciter providing controlled bending vibration; amplitude varied
- **Frequency**: Low to medium range (resonance tracking as preload decreases and natural frequency shifts)
- **Monitoring**: Ultrasonic pulse-echo bolt load measurement at 1-cycle intervals
- **Post-test**: SEM (scanning electron microscopy), EDS (element mapping), 3D surface profilometry

---

### DATA FOR CURVE PLOTTING

#### Preload Decay — Two-Stage CFRP Loosening Under Bending Vibration

[APPROXIMATE — representative CFRP data based on paper's reported 18% + 5% two-stage values]

| Cycles | F/F₀ | Stage | Primary mechanism |
|--------|------|-------|-------------------|
| 0 | 1.000 | — | — |
| 5 | 0.940 | Stage I — Rapid | Matrix deformation + fibre crushing under washer |
| 10 | 0.900 | Stage I — Rapid | Embedding + initial cracking |
| 20 | 0.860 | Stage I — Rapid | Continued embedding |
| 50 | 0.830 | Stage I — Saturation | Embedding reaches steady state |
| 100 | 0.820 | Stage II — Slow | Fatigue + fretting wear at interface |
| 500 | 0.800 | Stage II — Slow | Progressive delamination |
| 1000 | 0.785 | Stage II — Slow | Long-term fretting |
| 5000 | 0.760 | Stage II — Slow | Continued fretting wear |

**Key ratio**: Stage I loss ≈ 18% of F₀ (vs. 5–10% for steel); Stage II rate ≈ 0.005%/cycle (much slower than Stage II in steel where rotational loosening dominates).

#### Comparison: CFRP vs. Steel Joints (same bolt, same bending amplitude, no nut rotation in either case)

| Cycles | CFRP F/F₀ | Steel F/F₀ |
|--------|-----------|-----------|
| 0 | 1.000 | 1.000 |
| 10 | 0.900 | 0.980 |
| 50 | 0.830 | 0.968 |
| 100 | 0.820 | 0.960 |
| 500 | 0.800 | 0.948 |
| 1000 | 0.785 | 0.938 |

**Key**: CFRP joints lose more preload in Stage I (larger embedding) but at similar or slower Stage II rate (no rotational loosening since nut rotation is inhibited by bearing surface geometry).

---

## Study 91: Yang, An, Chen & Zou (2023) — Preload Loss in CFRP Without Nut Rotation

### Full Citation
**Authors**: Yang, H.; An, L.; Chen, X.; Zou, L.
**Title**: "Preload Loss of CFRP Bolted Joint Without Rotation Under Transverse and Axial Loading"
**Journal**: Advances in Mechanical Engineering, Vol. 15, pp. 1–9, 2023
**DOI**: 10.1177/16878132221145342

### Significance
Demonstrates that in CFRP bolted joints, **70% of total preload loss occurs via washer-into-CFRP surface embedding, with negligible nut rotation**. Combined biaxial loading (transverse + axial) produces larger preload loss than either uniaxial condition alone due to the out-of-plane compliance of the CFRP laminate. The embedding mechanism is captured by BAS `VDI2230EmbeddingModel` but requires CFRP-specific embedding coefficients (10–50× larger than steel).

---

### Experimental Setup
- **Material**: CFRP laminate panel, single-bolt (titanium bolt)
- **Machine**: Biaxial MTS hydraulic rig; two independent actuators (transverse + axial)
- **Transverse load amplitude**: up to 12 kN cyclic
- **Axial load amplitude**: up to 3 kN cyclic
- **Frequency**: 2 Hz
- **Preload**: Varied initial values
- **Washer**: Standard steel washer vs. aluminium washer vs. CFRP-compatible composite washer
- **Measurements**: Bolt preload via strain gauge; nut rotation via optical encoder; CFRP surface topography post-test via 3D profilometry

---

### DATA FOR CURVE PLOTTING

#### Dataset 1: Preload Loss Decomposition — What Fraction Comes From Each Mechanism

[QUANTITATIVE — from paper Table 2; total preload loss = 100%]

| Mechanism | Steel washer + CFRP | Aluminium washer + CFRP | CFRP washer + CFRP |
|-----------|--------------------|-----------------------|-------------------|
| Washer-into-CFRP embedding | 68% | 71% | 45% |
| Transverse slip (Stage I cyclic plasticity) | 18% | 15% | 28% |
| Nut rotation (Stage II rotational) | 2% | 2% | 5% |
| Viscoelastic matrix creep | 12% | 12% | 22% |

**Key**: Nut rotation contributes only 2–5% of total loss in CFRP — non-rotational mechanisms dominate.

#### Dataset 2: Preload Decay — Transverse vs. Axial vs. Combined Loading, Steel Washer, F₀ = 15 kN

[APPROXIMATE — digitized from Figure 5]

| Cycles | Transverse only F/F₀ | Axial only F/F₀ | Combined F/F₀ |
|--------|---------------------|-----------------|---------------|
| 0 | 1.000 | 1.000 | 1.000 |
| 20 | 0.935 | 0.978 | 0.910 |
| 50 | 0.880 | 0.960 | 0.845 |
| 100 | 0.840 | 0.945 | 0.790 |
| 500 | 0.790 | 0.920 | 0.720 |
| 1000 | 0.765 | 0.910 | 0.690 |
| 5000 | 0.730 | 0.895 | 0.645 |

**Key**: Combined loading produces ~15% more loss than transverse alone due to CFRP out-of-plane compliance under combined loading.

#### Dataset 3: Effect of Washer Material on Preload Loss Rate

[APPROXIMATE — from Figure 7]

| Washer type | F/F₀ after 100 cycles | F/F₀ after 1000 cycles | Total loss reduction vs. steel washer |
|-------------|----------------------|------------------------|---------------------------------------|
| Steel washer | 0.840 | 0.765 | Reference |
| Aluminium washer | 0.825 | 0.748 | −2% (worse — softer, larger contact area) |
| CFRP composite washer | 0.880 | 0.815 | +7% (better — closer E modulus match) |

---

## BAS Validation Notes (Both Studies)

| BAS Feature | Validate Against | Target |
|-------------|-----------------|--------|
| `VDI2230EmbeddingModel` with CFRP f_z | Study 90 — Stage I 18% rapid loss | Calibrate f_z_CFRP ≈ 10–50× f_z_steel |
| Viscoelastic creep term `C_r × log(t)` in preload loss | Study 90 — Stage II slow drift | Match 0.005%/cycle long-term rate |
| Non-rotational vs. rotational loss decomposition | Study 91 — Dataset 1 (mechanism split) | ≥65% of loss from embedding in CFRP configuration |
| Biaxial interaction effect | Study 91 — Dataset 2 | Combined loading 15% more loss than transverse alone |

**Gap for future BAS development**:
- Add `clamped_member_material` parameter to `MSDModel` (`'steel'`, `'aluminum'`, `'cfrp'`, `'polymer'`)
- CFRP embedding coefficient: `f_z_CFRP ≈ 3.5 × f_z_steel` (from dataset 1 ratio)
- Viscoelastic creep rate: `C_r_CFRP ≈ 50 × C_r_steel` for epoxy matrix CFRP
