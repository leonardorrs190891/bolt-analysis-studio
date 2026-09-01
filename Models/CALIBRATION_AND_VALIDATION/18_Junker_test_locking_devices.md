# Study 18: Locking Device Comparison — Compiled Junker Test Data

## Sources
This file compiles DIN 25201-4 B test results from multiple manufacturers, academic studies, and standards bodies.

### Primary Sources
1. **Nord-Lock Group**: Published Junker test results (DIN 25201-4)
2. **HEICO Fastening Systems**: Junker test comparison charts
3. **Eccles, W. (2010)**: PhD Thesis, University of Central Lancashire
4. **Friede, R.; Lange, J. (2009)**: "Self loosening of prestressed bolts", Nordic Steel Construction Conference (NSCC2009), pp. 272–279
5. **Izumi et al. (2009)**: "Loosening-resistance evaluation of double-nut tightening method and spring washer", Eng. Fail. Anal. 16(5):1510–1519
6. **DIN 25201-4:2010**: "Design guide for bolted joints – Part 4: Securing of bolted joints"

---

## Standard Junker Test Protocol (DIN 25201-4 B)

### Test Conditions
- **Bolt size**: M8 (most common), also M10, M12
- **Property class**: 8.8, 10.9, or 12.9
- **Initial preload**: ~70% of minimum proof load
- **Displacement**: Set by reference test (unsecured bolt must loosen in 300 ± 100 cycles)
- **Typical amplitude**: ±0.5 to ±1.0 mm for M8
- **Frequency**: 12.5 Hz (750 cycles/min)
- **Duration**: 2,000 cycles
- **Pass criterion**: ≥80% preload retention at 2,000 cycles
- **Number of tests**: 1 reference test (unsecured) + 12 verification tests (secured)

### Typical Initial Preloads for DIN 25201-4

| Bolt | Class | Proof load (N) | 70% proof (N) | 50% proof (N) |
|---|---|---|---|---|
| M8 | 8.8 | 22,100 | 15,470 | 11,050 |
| M8 | 10.9 | 31,400 | 21,980 | 15,700 |
| M10 | 8.8 | 35,200 | 24,640 | 17,600 |
| M10 | 10.9 | 49,900 | 34,930 | 24,950 |
| M12 | 8.8 | 50,800 | 35,560 | 25,400 |
| M12 | 10.9 | 72,100 | 50,470 | 36,050 |

---

## DATA FOR CURVE PLOTTING

### Dataset 1: M8 Class 10.9, F₀ ≈ 22 kN, ±0.7 mm, 12.5 Hz

**[Compiled from multiple manufacturer test reports — approximate consensus values]**

#### Unsecured Bolt + Standard Nut (Reference/Baseline)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 25 | 0.650 |
| 50 | 0.400 |
| 100 | 0.150 |
| 200 | 0.050 |
| 500 | 0.010 |
| 1,000 | 0.005 |
| 2,000 | 0.000 |

#### Helical Spring Washer (DIN 127)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 25 | 0.600 |
| 50 | 0.350 |
| 100 | 0.130 |
| 200 | 0.040 |
| 500 | 0.010 |
| 1,000 | 0.000 |
| 2,000 | 0.000 |

**WORSE than unsecured in some tests!** DIN 127 was withdrawn in 2003. Spring washers are now classified as "INEFFECTIVE" per DIN 25201-4.

#### Toothed Lock Washer (DIN 6797)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 25 | 0.620 |
| 50 | 0.360 |
| 100 | 0.140 |
| 200 | 0.050 |
| 500 | 0.010 |
| 2,000 | 0.000 |

**INEFFECTIVE** — similar to unsecured.

#### Nylon Insert Lock Nut (Nyloc, DIN 985)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.780 |
| 100 | 0.620 |
| 200 | 0.420 |
| 500 | 0.200 |
| 1,000 | 0.100 |
| 2,000 | 0.060 |

**Partial protection** — prevailing torque feature maintains some residual preload, but does NOT pass 80% criterion. Nylon degrades above 120°C.

#### All-Metal Prevailing Torque Nut (DIN 6925)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.800 |
| 100 | 0.660 |
| 200 | 0.480 |
| 500 | 0.280 |
| 1,000 | 0.180 |
| 2,000 | 0.120 |

**Better than nylon at high temperatures** but still fails 80% criterion.

#### Thread-Locking Adhesive (Loctite 242 — Medium Strength)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 100 | 0.990 |
| 500 | 0.980 |
| 1,000 | 0.975 |
| 2,000 | 0.970 |

**EXCELLENT** — virtually no preload loss. **PASSES** DIN 25201-4 easily.

#### Thread-Locking Adhesive (Loctite 271 — High Strength)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 100 | 0.995 |
| 500 | 0.990 |
| 1,000 | 0.985 |
| 2,000 | 0.980 |

**EXCELLENT** — effectively zero loosening. Removal requires heating to ~250°C.

#### Nord-Lock Wedge-Locking Washer (NL Series)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.960 |
| 100 | 0.940 |
| 200 | 0.920 |
| 500 | 0.900 |
| 1,000 | 0.880 |
| 2,000 | 0.860 |

**PASSES** DIN 25201-4 (>80% at 2,000 cycles). Wedge-locking principle: cams dig into contact surfaces, converting loosening rotation into bolt stretch.

#### HEICO-LOCK Wedge-Locking Washer
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.970 |
| 100 | 0.950 |
| 200 | 0.930 |
| 500 | 0.910 |
| 1,000 | 0.895 |
| 2,000 | 0.880 |

**PASSES** DIN 25201-4. Similar performance to Nord-Lock.

#### Serrated Flange Bolt (IFI-145)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.900 |
| 100 | 0.840 |
| 200 | 0.780 |
| 500 | 0.700 |
| 1,000 | 0.650 |
| 2,000 | 0.600 |

**Moderate protection** — serrations increase effective bearing friction. May damage soft clamped materials.

#### Double Nut (DIN 25201 — properly installed: thin nut first, thick nut on top)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.920 |
| 100 | 0.870 |
| 200 | 0.820 |
| 500 | 0.760 |
| 1,000 | 0.720 |
| 2,000 | 0.680 |

**Moderate to good protection** when properly installed. FAILS if installed incorrectly (thick nut first).

---

### Dataset 2: M10 Class 10.9 (Friede & Lange 2009)

**Test**: M10×30, Class 8.8, ±2 mm transverse displacement

#### Unsecured
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.350 |
| 100 | 0.100 |
| 150 | 0.020 |

#### Spring Washer (DIN 127)
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.300 |
| 100 | 0.080 |
| 150 | 0.010 |

**Worse than unsecured** at ±2 mm displacement!

#### Serrated Flange Bolt
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 50 | 0.650 |
| 100 | 0.500 |
| 200 | 0.400 |
| 500 | 0.350 |
| 1,000 | 0.350 |

**Stabilizes at reduced preload** — the serrations "lock in" once they engage.

### Friede & Lange: Effect of Grip Length on M20

| l/d ratio | Cycles to 50% loss (unsecured, ±0.5 mm) |
|---|---|
| 2.0 | ~50 |
| 3.0 | ~150 |
| 4.0 | ~500 |
| 4.5 | ~1,500 |
| 5.0 | ~5,000+ (near endurance limit) |

---

### Dataset 3: Eccles (2010) — Prevailing Torque Nut Failure Modes

**Critical finding**: Prevailing torque nuts can **completely detach from the bolt** under combined axial + transverse loading.

| Loading type | Prevailing torque nut behavior |
|---|---|
| Pure transverse only | Loosens but maintains residual clamp at prevailing torque level |
| Transverse + mild axial | Same as above |
| Transverse + moderate axial | Nut continues rotating past residual clamp |
| Transverse + high axial | **Complete nut detachment** — nut spins off entirely |

**Mechanism**: When residual axial load exceeds the prevailing torque's friction capacity, the nut continues to unwind. The prevailing torque nut has no positive mechanical lock — it relies solely on thread interference, which can be overcome.

---

## Locking Device Classification (DIN 25201)

| Category | Examples | Effectiveness |
|---|---|---|
| **No securing** | Bare bolt + nut | 0% retention |
| **Loss prevention** | Spring washer, toothed washer, nylon nut | Prevents nut from falling off, but preload lost |
| **Bolt locking** | Wedge-locking washers, adhesive, serrated flange | Maintains preload under vibration |
| **Bolt securing** | Safety wire, cotter pin, tab washer | Positive mechanical lock — cannot rotate |

### VDI 2230 Categorization
| Method | VDI 2230 Class |
|---|---|
| Sufficient preload (primary) | "Securing by clamp force" |
| Thread adhesive | Chemical |
| Nord-Lock / HEICO | Mechanical (bolt locking) |
| Spring washer | NOT recognized as effective |
| Prevailing torque nut | Friction-based |
| Cotter pin / safety wire | Form-locking |

---

## MSD BUILDER NOTE

> This file is a **reference/compilation document** and does not represent a single reproducible test configuration.
> For MSD Builder configurations, refer to the individual experimental studies (Papers 01–15, 20, 23–34) that contain specific test parameters.
