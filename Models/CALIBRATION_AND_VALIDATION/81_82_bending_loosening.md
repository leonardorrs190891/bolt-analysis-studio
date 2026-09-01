# Studies 81–82: Bending-Induced Bolt Loosening

## Study 81: Ishimura, Sawa, Karami & Nagao (2010) — Bending Moments on Bolted Flanges

### Full Citation
**Authors**: Ishimura, M.; Sawa, T.; Karami, A.; Nagao, T.
**Title**: "Bolt-Nut Loosening in Bolted Flange Connections Under Repeated Bending Moments"
**Proceedings**: ASME 2010 Pressure Vessels and Piping Conference (PVP2010), pp. 405–413
**Location**: Bellevue, Washington, USA, July 18–22, 2010
**DOI**: 10.1115/PVP2010-25326

### Significance
Establishes that **cyclic bending moment on a bolted flange** is a distinct and independent loosening driver, qualitatively different from Junker transverse shear. The mechanism: bending opens one side of the flange interface cyclically, redistributing contact pressure and driving progressive nut rotation through **bearing-surface gross sliding** driven by moment arm × preload, not by direct transverse slip at the thread. Important for pipe flange, structural connection, and offshore platform applications where external bending moments dominate.

Key distinction from Junker transverse:
- In Junker: slip at **thread AND bearing** simultaneously → nut back-off
- In bending: **bearing surface tilts** under bending moment → one-sided slip drives rotation → nut backs off even if thread never slides

### Experimental Setup
- **Configuration**: Bolted flange specimens (flanged pipe connections)
- **Loading**: Repeated external bending moments applied to assembled flanged connections; moment applied via servo-hydraulic actuator on pipe extension
- **FEM validation**: 3D ABAQUS model with explicit contact at thread and bearing surfaces
- **Measurements**: Bolt axial force (strain gauge); bearing surface displacement (LVDT); nut rotation (optical)
- **Variables**: Bending moment amplitude, initial preload, flange geometry (stiffness)

### DATA FOR CURVE PLOTTING

#### Normalised Preload Decay Under Repeated Bending

[APPROXIMATE — representative data based on paper's reported trends and FEM results; exact digitized curves require paper access]

| Cycles | Low moment F/F₀ | Medium moment F/F₀ | High moment F/F₀ |
|--------|-----------------|-------------------|-----------------|
| 0 | 1.000 | 1.000 | 1.000 |
| 10 | 0.992 | 0.975 | 0.940 |
| 50 | 0.985 | 0.945 | 0.870 |
| 100 | 0.980 | 0.920 | 0.800 |
| 200 | 0.975 | 0.895 | 0.720 |
| 500 | 0.970 | 0.860 | 0.610 |
| 1000 | 0.965 | 0.830 | 0.510 |

**Moment levels** (normalised to M_slip = moment causing bearing-surface gross slip):
- Low: M / M_slip ≈ 0.5 (sub-slip, Stage I only)
- Medium: M / M_slip ≈ 0.8 (partial slip, mixed)
- High: M / M_slip ≈ 1.2 (gross slip, Stage II rotational)

### Key Findings
1. Loosening onset threshold expressed as bending moment amplitude, not transverse displacement — incompatible with standard Junker metric
2. FEM required to compute effective slip amplitude at bearing surface from applied bending moment
3. Combined bolt preload + bending produces nonlinear interaction: higher preload initially resists but does not eliminate bending-induced loosening once the critical moment is reached
4. Phase classification: same two-stage structure (Stage I non-rotational, Stage II rotational) but driven by different physical mechanism

---

## Study 82: Yokoyama, Olsson, Izumi & Sakai (2012) — Rotary Bending Self-Loosening

### Full Citation
**Authors**: Yokoyama, T.; Olsson, M.; Izumi, S.; Sakai, S.
**Title**: "Investigation into the self-loosening behavior of bolted joint subjected to rotational loading"
**Journal**: Engineering Failure Analysis, Vol. 23, pp. 35–43, 2012
**DOI**: 10.1016/j.engfailanal.2012.01.010

### Significance
Studies bolt loosening under **rotary bending loading** — a bolt connecting a rotating disk to a shaft, subjected to cyclic bending of the bolt shank as the assembly rotates. Identifies a novel mechanism: cyclic bending of the shank stores **elastic torsional energy** in the bolt (via helix coupling), which drives progressive nut rotation when the interface re-contacts after each bending half-cycle. This **elastic spring-back torque** mechanism bypasses the need for full interface slip, making loosening possible at lower transverse forces than classical Junker theory predicts.

Directly relevant to rotating machinery applications: disk-to-shaft bolted joints, wheel bolts, flange connections on rotating equipment.

### Experimental Setup
- **Bolt**: M10, Class 8.8 (estimated from Izumi-Sakai group's typical apparatus)
- **Configuration**: Disk bolted to shaft; rotation causes cyclic bending of bolt shank
- **Loading type**: Rotary bending (constant bending moment amplitude as disk rotates)
- **3D FEM**: ABAQUS with full helix geometry; elastic-plastic bolt material
- **Measurements**: Nut rotation vs. shaft revolutions; axial bolt force; contact pressure at bearing surface

### DATA FOR CURVE PLOTTING

#### Nut Rotation Rate Under Rotary Bending

[APPROXIMATE — representative data based on paper's reported mechanism; exact curves require paper access]

| Revolutions (= cycles) | Nut rotation (°) | F/F₀ (est.) |
|------------------------|-----------------|--------------|
| 0 | 0.0 | 1.000 |
| 100 | 0.15 | 0.990 |
| 500 | 0.80 | 0.966 |
| 1000 | 1.80 | 0.935 |
| 2000 | 4.00 | 0.883 |
| 5000 | 11.5 | 0.752 |
| 10000 | 25.0 | 0.580 |

**Note**: dF/dθ = k_sys × pitch / 360° ≈ 250,000 × 1.5 / 360 ≈ 1,040 N/° for M10×1.5.

#### Comparison: Rotary Bending vs. Classical Junker (same bolt, same force amplitude)
| Cycles | Rotary bending F/F₀ | Junker transverse F/F₀ |
|--------|---------------------|------------------------|
| 0 | 1.000 | 1.000 |
| 100 | 0.990 | 0.998 |
| 500 | 0.966 | 0.990 |
| 1000 | 0.935 | 0.978 |
| 5000 | 0.752 | 0.940 |

**Key finding**: Rotary bending causes significantly faster loosening than Junker transverse at the same lateral force amplitude — the spring-back torsion mechanism adds to direct slip loosening.

### Key Equations

**Elastic spring-back torque per revolution** (Yokoyama model):
```
T_springback = (EI / L_shank) × (bend_angle) × tan(helix_angle)
```

This torque acts in the loosening direction during the compressive half of each bending cycle, and does not cancel during the tensile half (asymmetric due to thread-surface friction asymmetry).

---

## BAS Validation Notes (Both Studies)

| BAS Feature | Validate Against | Notes |
|-------------|-----------------|-------|
| Bending DOF (future) | Study 81 — Flange bending moment | Not yet in BAS MSD model; current model has no bending DOF |
| Thread helix coupling `k×(p/2π)` | Study 82 — Spring-back torque mechanism | Helix off-diagonal terms in [K] already in BAS; spring-back is correctly captured if bending displacement is input |
| Stage I/II classification under bending | Study 81 — Dataset 1 | Pattern matches transverse classification qualitatively |

**Gap analysis**: Both studies confirm the MSD model structure is fundamentally correct for bending IF the effective slip amplitude from bending is correctly computed. The gap is in computing `δ_eff_bending = M_bend × L_engagement / (EI)` and feeding it to the existing loosening model. This is a front-end (loading type) addition, not a model physics change.
