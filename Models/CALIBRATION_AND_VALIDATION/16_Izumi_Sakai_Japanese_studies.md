# Study 16: Izumi, Yokoyama & Sakai (2005–2011) — Japanese Studies on Thread Slip Mechanism

## Full Citations

### Paper A — First 3D FEA of Thread Slip
**Authors**: Izumi, S.; Yokoyama, T.; Iwasaki, A.; Sakai, S.
**Title**: "Three-dimensional finite element analysis of tightening and loosening mechanism of threaded fastener"
**Journal**: Engineering Failure Analysis, 2005, 12(4), 604–615
**DOI**: 10.1016/j.engfailanal.2004.09.009

### Paper B — Slip Sequence Discovery
**Authors**: Izumi, S.; Yokoyama, T.; Kimura, M.; Sakai, S.
**Title**: "Loosening-resistance evaluation of double-nut tightening method and spring washer by three-dimensional finite element analysis"
**Journal**: Engineering Failure Analysis, 2009, 16(5), 1510–1519
**DOI**: 10.1016/j.engfailanal.2008.09.027

### Paper C — Sakai's Theoretical Framework (Classic)
**Authors**: Sakai, T.
**Title**: "The friction coefficient of fasteners"
**Journal**: Bulletin of JSME, 1978, 21(159), 1385–1390
**DOI**: 10.1299/jsme1958.21.1385

### Paper D — Axial Loading Mechanism
**Authors**: Sakai, T.
**Title**: "Mechanism of bolt self-loosening under axial vibration"
**Journal**: Proc. IMechE Part C: J. Mechanical Engineering Science, 2011, 225(8), 1887–1897
**DOI**: 10.1177/0954406211404654

---

## Paper A & B: Thread Slip Mechanism (FEA)

### FEA Model — Izumi et al. (2005)
| Parameter | Value |
|---|---|
| Software | ANSYS Mechanical (parametric design language) |
| Element type | SOLID185 (3D 8-node) |
| Contact elements | CONTA174 / TARGE170 |
| Total elements | ~80,000 |
| Bolt size | M10 × 1.5 |
| Thread modeling | Full helical geometry (8 pitch segments) |
| Friction | Isotropic Coulomb |
| μ values tested | 0.05, 0.10, 0.15, 0.20, 0.30 |
| Loading | Quasi-static transverse displacement |

### Critical Discovery: Slip Sequence

**Thread surfaces slip completely BEFORE bearing surfaces**

This is the fundamental mechanism that enables self-loosening. The sequence is:

1. **Transverse force increases** → partial slip begins at both thread and bearing
2. **Thread complete slip occurs first** → entire thread helix in relative sliding
3. During thread slip, the helix geometry converts transverse force into loosening torque
4. **Bearing surface still partially stuck** → provides reduced resistance to rotation
5. Net loosening torque exceeds bearing resistance → nut rotates

### Contact State Data (M10, F₀ = 40 kN, μ = 0.15)

**[From FEA — digitized from Figures in Paper A]**

#### Thread Contact State vs. Transverse Force
| F_trans / (μ × F₀) | Thread slip fraction | Bearing slip fraction |
|---|---|---|
| 0.0 | 0.00 | 0.00 |
| 0.2 | 0.05 | 0.02 |
| 0.4 | 0.18 | 0.08 |
| 0.6 | 0.45 | 0.20 |
| 0.7 | 0.65 | 0.30 |
| 0.8 | 0.85 | 0.42 |
| 0.9 | 0.95 | 0.55 |
| 1.0 | **1.00** | 0.65 |
| 1.1 | 1.00 | 0.78 |
| 1.2 | 1.00 | 0.88 |
| 1.4 | 1.00 | **1.00** |

**Key ratio**: Thread complete slip occurs at F_trans ≈ 1.0 × μ × F₀
Bearing complete slip occurs at F_trans ≈ 1.4 × μ × F₀
Thread slips at **71%** of the force needed for bearing slip.

### Why Thread Slips First
- Thread contact is a **helical inclined plane** → the normal force resolves into both axial and tangential components
- Bearing contact is a **flat annular surface** → higher friction resistance per unit force
- Thread pitch creates a **geometric advantage** for slip in the loosening direction
- The effective friction coefficient at threads is reduced by the helix angle:
  ```
  μ_eff_thread = μ × cos(α) ≈ 0.87 × μ    (for 60° threads, α = 30°)
  ```

---

## Paper B: Spring Washer and Double Nut Evaluation

### FEA Results — Spring Washer (DIN 127)

| Configuration | Cycles to 50% loss | Relative performance |
|---|---|---|
| Bare bolt + nut | 25 | 1.0× (reference) |
| Spring washer (DIN 127) | 20 | **0.8× (WORSE!)** |
| Toothed washer (DIN 6797) | 22 | 0.9× (negligible) |

**Why spring washers fail**: The spring washer reduces the effective bearing area and creates stress concentrations. When flattened by preload, it provides no spring-back benefit. The sharp edges dig into the surface, reducing effective friction by disturbing the contact.

### FEA Results — Double Nut (Properly Installed)

| Configuration | Cycles to 50% loss | Relative performance |
|---|---|---|
| Bare bolt + nut | 25 | 1.0× |
| Double nut (thick on thin) | 85 | **3.4×** |
| Double nut (thin on thick) | 30 | 1.2× (wrong installation) |

**Proper double nut installation**:
1. Run thin nut down and tighten to ~50% of target preload
2. Run thick nut on top of thin nut
3. Hold thin nut with wrench, tighten thick nut to full target preload
4. The thick nut pushes DOWN on the thin nut, creating opposing thread flank loads

**Wrong installation** (thick nut first, thin on top): Provides almost no benefit because the thin nut cannot generate sufficient opposing force.

---

## Paper D: Sakai (2011) — Axial Loading Mechanism

### Key Finding
Pure axial vibration **rarely causes rotational loosening** unless:
1. The bolt shank experiences **torsional vibration** from the axial load (due to helix geometry)
2. The **restitution torque** from shank untwisting exceeds bearing friction during the unloading phase
3. **Part separation** occurs (preload drops below zero momentarily during vibration)

### Conditions for Axial Loosening

For loosening to occur under pure axial vibration:
```
Axial loosening occurs when:
  F_axial × tan(β) × r_t > μ_b × (F₀ - F_axial) × r_be

Which simplifies to:
  F_axial / F₀ > μ_b × r_be / (tan(β) × r_t + μ_b × r_be)
```

For typical M12 values (μ = 0.15, β = 2.93°, r_t = 5.43 mm, r_be = 7.60 mm):
```
F_axial / F₀ > 0.15 × 7.60 / (0.051 × 5.43 + 0.15 × 7.60) = 0.80
```

This means the axial load must be **>80% of the preload** to cause loosening — essentially requiring joint separation.

### Axial Loosening Data (M16, F₀ = 35 kN)

| Pulsating axial force (kN) | Peak F_ext/F₀ | Nut rotation after 500 cycles (°) | Stage |
|---|---|---|---|
| 10 | 0.29 | <0.01 | No loosening |
| 20 | 0.57 | 0.05 | Negligible |
| 25 | 0.71 | 0.2 | Very slow |
| 28 | 0.80 | 0.5 | Threshold |
| 30 | 0.86 | 1.5 | Moderate |
| 32 | 0.91 | 3.0 | Significant |
| 34 | 0.97 | 5.5 | Near-separation |

**Comparison**: Under **transverse** loading at 0.5 mm amplitude, the same bolt loses 50% preload in ~50 cycles. Under **axial** loading, even at 90% of preload, only 3° of rotation occurs in 500 cycles. This quantitatively confirms that transverse loading is **orders of magnitude** more severe than axial loading for loosening.

---

## Paper C: Sakai (1978) — Critical Slippage Theory (Classic)

### The Sakai Equation (fundamental relationship)
The critical transverse displacement for onset of loosening:
```
S_cr = μ × F₀ / k_t
```

Where:
- S_cr = critical transverse displacement (mm)
- μ = friction coefficient (effective, combining thread and bearing)
- F₀ = preload (N)
- k_t = transverse joint stiffness (N/mm)

### Transverse Joint Stiffness
```
k_t = G × A_contact / t
```
Where:
- G = shear modulus (~80,000 MPa for steel)
- A_contact = effective contact area
- t = effective slip layer thickness (approximately equal to thread engagement)

### Typical Values of k_t
| Bolt | k_t (N/mm) | Source |
|---|---|---|
| M8 | ~40,000 | Estimated |
| M10 | ~60,000 | Nassar group data |
| M12 | ~80,000 | Jiang data |
| M16 | ~120,000 | Hattori data |
| M20 | ~180,000 | Estimated |

---

## Reproduction Notes — ANSYS Setup

### Mesh Generation for Helical Thread
```
! ANSYS APDL commands for M10 helical thread
/PREP7
ET,1,SOLID185
HPTCREATE,1,LINE,,0,0,0,0,0,1  ! Helix axis
! Create thread profile cross-section
! Sweep along helix path
! Typical: 36 elements around circumference, 4 per pitch height
! Total: ~80,000 elements
```

### Contact Definition
```
! Thread contact pair
ET,2,CONTA174    ! Contact on bolt threads
ET,3,TARGE170    ! Target on nut threads
MP,MU,1,0.15     ! Friction coefficient
KEYOPT,2,10,2    ! Augmented Lagrangian
KEYOPT,2,12,0    ! Standard contact
```

### Loading Sequence
```
! Step 1: Preload (BOLT LOAD or thermal method)
! Step 2: Transverse displacement cycles
*DO,CYCLE,1,50
  D,TOP_PLATE,UX,+0.5    ! Forward
  SOLVE
  D,TOP_PLATE,UX,-0.5    ! Reverse
  SOLVE
*ENDDO
```

---

## MSD BUILDER NOTE

> This file is a **reference/compilation document** and does not represent a single reproducible test configuration.
> For MSD Builder configurations, refer to the individual experimental studies (Papers 01–15, 20, 23–34) that contain specific test parameters.
