# Study 19: Sandia National Labs & NASA Reports — Loosening in Real Structures

## Source A: Sandia National Laboratories

### Full Citation
**Authors**: Miller, D. L.; Marshek, K. M.; et al.
**Title**: "Loosening of Bolted Joints Under Dynamic Loading"
**Report**: SAND2019-12525C
**Institution**: Sandia National Laboratories, Albuquerque, NM
**Year**: 2019
**Access**: OSTI (https://www.osti.gov/servlets/purl/1642845)

### Experimental Setup
- **Configuration**: C-beam assembly with bolted connections
- **Bolt**: SAE Grade 9 (UTS 1,034 MPa), zinc-plated
- **Bolt size**: Not explicitly stated (likely 3/8" or 1/2" based on C-beam)
- **Excitation**: Modal excitation (shaker table)
- **Frequency range**: 275–350 Hz (near structural resonances)
- **Modes excited**: First bending, torsion, out-of-phase bending
- **Duration**: 5 minutes per excitation level
- **Preload measurement**: Ultrasonic bolt gauges (most accurate method)

### Preload Levels Tested
| Level | Preload | Description |
|---|---|---|
| Finger-tight | ~50 N | Near-zero preload |
| Low | 311 N (70 lbf) | Very light |
| Medium | 1,000 N (225 lbf) | Below design |
| High | 4,450 N (1,000 lbf) | Design preload |

### KEY DATA

| Preload | Mode excited | Duration | Preload loss | Result |
|---|---|---|---|---|
| Finger-tight | Out-of-phase bending | 5 min | **100%** (nut fell off) | Complete failure |
| Finger-tight | First bending | 5 min | ~60% | Significant loosening |
| 311 N | Out-of-phase bending | 5 min | ~15% | Moderate loss |
| 311 N | First bending | 5 min | ~5% | Minor loss |
| 1,000 N | All modes | 5 min | **<5%** | Negligible |
| 4,450 N | All modes | 5 min | **<2%** | Negligible |

**Key finding**: At realistic design preloads (>1,000 N), only minimal loosening was observed even at resonance. Loosening is primarily a problem for **under-torqued or finger-tight joints**. This is consistent with the principle that sufficient preload is the primary defense against loosening.

### Acceleration Levels
- Peak acceleration at bolt location: 10–100 g (depending on mode and input level)
- Displacement at bolt: 0.01–0.10 mm (much smaller than Junker test amplitudes)
- At 275 Hz with 0.05 mm amplitude: velocity = 86.5 mm/s

---

## Source B: NASA Technical Report

### Full Citation
**Authors**: VanHorn, D. A.
**Title**: "Preload Loss in a Spacecraft Fastener via Vibration-Induced Unwinding"
**Report**: NASA/TP-2018-219787
**Year**: 2018
**Access**: https://ntrs.nasa.gov/citations/20180002978

### Context
During ground vibration testing of a launch vehicle upper stage, bolted cup-cone pyrotechnic joints experienced unexpected preload loss despite safety wire and high thread friction.

### Joint Configuration
- **Type**: Cup-cone pyrotechnic separation joint
- **Number of bolts**: 6, circumferentially placed
- **Bolt**: NAS1352 series (high-strength aerospace fastener)
- **Property class**: Equivalent to Grade 8 / Class 10.9
- **Thread locking**: Safety wire + high-friction thread coating
- **Initial preload**: Set by torque (target ~70% proof)
- **Vibration**: Random vibration qualification test (per NASA-STD-7001)

### Loosening Data

| Bolt position | Initial preload | Post-vibration preload | Loss (%) |
|---|---|---|---|
| Position 1 | 100% (nominal) | ~95% | 5% |
| Position 2 | 100% | ~90% | 10% |
| Position 3 | 100% | ~50% | **50%** |
| Position 4 | 100% | ~85% | 15% |
| Position 5 | 100% | ~50% | **50%** |
| Position 6 | 100% | ~92% | 8% |

**Two bolts lost 50% of preload** — unacceptable for flight hardware.

### Root Cause Analysis
1. Cup-cone geometry concentrates bending loads at bolt locations
2. Vibration mode shape caused differential displacement at bolt circle
3. Safety wire prevented >0.5 turns of rotation but could not prevent small (<0.5 turn) loosening
4. Asymmetric loading due to mode shape → some bolts experienced much higher transverse displacement
5. Thread coating degraded during vibration → friction coefficient dropped

### Corrective Actions
- Increased preload to 90% of proof load
- Added Belleville washers for preload maintenance
- Changed from safety wire to chemical thread locking (Loctite 262)
- Added ultrasonic preload verification after vibration testing

---

## Source C: NASA-STD-5020B (Threaded Fastening Systems Requirements)

### Key Requirements for Spaceflight Hardware
| Requirement | Specification |
|---|---|
| Minimum preload | **65% of yield strength** |
| Preload verification | Required by test (ultrasonic or strain gauge) |
| Nut factor K | Must be determined experimentally for each lot |
| Locking feature | **Mandatory** — at least one positive locking device |
| Vibration screening | Required for all flight-critical joints |
| Statistical confidence | 90% probability at 95% confidence |

### NASA Preload Philosophy
- **Primary locking**: Sufficient preload (eliminates joint slip under design loads)
- **Secondary locking**: Positive locking device (chemical or mechanical)
- **Tertiary locking**: Inspection/verification (ultrasonic, torque audit)
- **All three levels required** for flight-critical joints

---

## Source D: NASA CR-195390 (Thread Movement Study)

### Full Citation
**Authors**: Junker, G.; Wallace, P. W.
**Title**: "Experimental Analysis of Thread Movement in Bolted Connections due to Vibrations"
**Report**: NASA CR-195390 (also published through NTRS: 19950018571)
**Year**: 1995

### Key Experimental Data (1/2"-13 UNC bolts)
- Tested at various preloads under controlled transverse vibration
- Thread movement (relative rotation between bolt and nut) measured with optical techniques

| Displacement amplitude (mm) | Thread movement per cycle (°) | Preload loss per cycle (N) |
|---|---|---|
| 0.13 | <0.01 | <5 |
| 0.25 | 0.03 | ~15 |
| 0.38 | 0.15 | ~80 |
| 0.51 | 0.40 | ~200 |
| 0.76 | 1.20 | ~600 |
| 1.02 | 2.50 | ~1,200 |

### Implications for Petrobras Flanged Joints
- Flanged joints in oil & gas service experience transverse displacements from:
  - Thermal expansion/contraction of piping
  - Pressure pulsations
  - Mechanical vibration from rotating equipment
  - Seismic loads
- Typical transverse displacement at flange face: 0.01–0.10 mm (well below Junker test levels)
- However, long-term operation (millions of cycles from pump vibration) can accumulate significant loosening even at small amplitudes
- **Belleville washers** (disc springs) recommended for applications with >50°C temperature swings

---

## MSD BUILDER NOTE

> This file is a **reference/compilation document** and does not represent a single reproducible test configuration.
> For MSD Builder configurations, refer to the individual experimental studies (Papers 01–15, 20, 23–34) that contain specific test parameters.
