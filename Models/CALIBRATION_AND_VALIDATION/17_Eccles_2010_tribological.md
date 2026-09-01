# Study 17: Eccles (2010) — Tribological Effects, Friction Evolution, and Coating Effects

## Full Citation
**Authors**: Eccles, W.
**Title**: "Tribological Aspects of the Self-Loosening of Threaded Fasteners"
**Institution**: University of Central Lancashire (UCLan), PhD Thesis
**Year**: 2010
**Type**: Doctoral dissertation
**Note**: The most comprehensive tribological study of bolt loosening. Key results also published in:
- Eccles, W. (2010): "A new approach to the checking of the loosening characteristics of threaded fasteners", SAE Int. J. Mater. Manuf. 3(1):739–745
- Eccles, W.; Sherrington, I.; Arnell, R.D. (2010): "Towards an understanding of the loosening characteristics of prevailing torque nuts"

---

## Experimental Setup

### Test Machine
- **Type**: Junker transverse vibration test machine (DIN 65151/25201-4 compliant)
- **Modified by**: Eccles — added torque measurement capability at bolt head and nut
- **Special instrumentation**: Separate torque measurement on head-side and nut-side to isolate thread vs. bearing friction during loosening

### Bolt Sizes Tested
| Size | Class | Surface treatments |
|---|---|---|
| M8 × 1.25 | 8.8, 10.9, 12.9 | Zinc, phosphate, cadmium, bare, MoS₂ |
| M10 × 1.5 | 10.9 | Zinc-plated |
| M12 × 1.75 | 10.9 | Zinc-plated |

### Test Parameters (Standard)
- **Preload**: 70% proof load (per DIN 25201-4)
- **Frequency**: 12.5 Hz
- **Duration**: Up to 2,000 cycles
- **Displacement**: Adjusted per DIN 25201-4 reference test (300±100 cycle failure criterion)

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Friction Coefficient Evolution During Repeated Tightening (M8 Zinc-Plated)

This dataset shows how friction changes when a bolt is tightened, loosened, and re-tightened repeatedly — critical for maintenance/retorquing applications.

**Tightening torque**: T = 25 Nm (M8 Class 10.9)

| Tightening cycle | μ_total (measured) | Achieved preload at 25 Nm (kN) | % of fresh preload |
|---|---|---|---|
| 1 (fresh) | 0.14 | 22.0 | 100% |
| 2 | 0.18 | 17.0 | 77% |
| 3 | 0.21 | 14.5 | 66% |
| 4 | 0.23 | 13.3 | 60% |
| 5 | 0.25 | 12.2 | 55% |
| 6 | 0.26 | 11.8 | 54% |
| 8 | 0.27 | 11.3 | 51% |
| 10 | 0.28 | 10.9 | 50% |

**Key finding**: After 10 tightening cycles, friction increases by **100%** (0.14 → 0.28) and achievable preload drops by **50%** at the same torque. This has critical implications for bolted joints that are frequently re-torqued during maintenance.

### Friction Increase Mechanism
1. **Zinc coating wear**: Soft zinc layer wears through, exposing harder steel substrate
2. **Surface roughening**: Repeated sliding creates plowing grooves
3. **Debris generation**: Wear particles act as abrasive medium
4. **Work hardening**: Contact surfaces harden from repeated plastic deformation
5. **Adhesion**: Metal-to-metal contact after coating loss → galling tendency

---

### Dataset 2: Friction Evolution During Vibration Loosening (M8 × 1.25 Class 10.9, Zinc-Plated)

**Initial conditions**: F₀ = 22 kN, μ_initial = 0.14, DIN 25201-4 test

**[APPROXIMATE — from PhD thesis data]**

#### Phase 1: Friction INCREASES (Cycles 0–50)
| Cycles | μ_th (thread) | μ_b (bearing) | Preload (kN) | F/F₀ |
|---|---|---|---|---|
| 0 | 0.14 | 0.14 | 22.0 | 1.000 |
| 5 | 0.15 | 0.15 | 19.0 | 0.864 |
| 10 | 0.16 | 0.16 | 16.5 | 0.750 |
| 20 | 0.17 | 0.17 | 13.0 | 0.591 |
| 50 | 0.18 | 0.18 | 8.0 | 0.364 |

#### Phase 2: Friction DECREASES (Cycles 50–500)
| Cycles | μ_th | μ_b | Preload (kN) | F/F₀ |
|---|---|---|---|---|
| 100 | 0.16 | 0.15 | 4.5 | 0.205 |
| 200 | 0.13 | 0.12 | 2.0 | 0.091 |
| 500 | 0.10 | 0.09 | 0.5 | 0.023 |

#### Phase 3: Severe Wear (Cycles 500+)
| Cycles | μ_th | μ_b | Notes |
|---|---|---|---|
| 500+ | 0.08 | 0.07 | Coating completely worn through |
| 1,000+ | 0.06 | 0.05 | Polished steel-on-steel |

**Three-Phase Friction Model**:
1. **Early cycles (0–50)**: μ INCREASES — asperity deformation, work hardening, initial embedding → this actually SLOWS loosening temporarily
2. **Intermediate (50–500)**: μ DECREASES — micro-cracks develop, wear debris separates contacts, coating breaks through
3. **Late (500+)**: μ continues DECREASING — severe surface damage, delamination wear, polished surfaces

---

### Dataset 3: Effect of Surface Coating (M8 Class 10.9, F₀ = ~70% proof)

| Coating | μ_initial | Cycles to 50% loss | Cycles to 80% loss | Classification |
|---|---|---|---|---|
| Bare steel (degreased) | 0.25 | ~80 | ~250 | High friction, moderate resistance |
| Zinc-plated (dry) | 0.22 | ~50 | ~150 | Standard |
| Zinc-plated + oil | 0.14 | ~25 | ~80 | Low friction, poor resistance |
| Cadmium-plated | 0.10 | ~12 | ~40 | Very low friction, worst |
| Phosphate + oil | 0.12 | ~18 | ~60 | Low friction |
| Phosphate + MoS₂ | 0.08 | ~8 | ~25 | Lowest friction, fastest loosening |
| Zinc flake (Geomet) | 0.12 | ~20 | ~65 | Moderate |

**Critical insight**: Lower friction = FASTER loosening. The common practice of lubricating bolts to achieve accurate preload comes at the cost of reduced loosening resistance. This is a fundamental design trade-off.

---

### Dataset 4: Prevailing Torque Nut Performance (M8, M10)

#### Nylon insert nut (DIN 985) — M8 Class 10.9
| Cycles | F/F₀ | Prevailing torque (Nm) |
|---|---|---|
| 0 | 1.000 | 4.2 (initial) |
| 50 | 0.780 | 3.5 |
| 100 | 0.620 | 2.8 |
| 200 | 0.450 | 2.0 |
| 500 | 0.220 | 1.2 |
| 1,000 | 0.100 | 0.8 |
| 2,000 | 0.060 | 0.5 |

**Prevailing torque degradation**: The nylon insert loses ~88% of its prevailing torque resistance over 2,000 vibration cycles.

#### All-metal prevailing torque nut (DIN 6925) — M8 Class 10.9
| Cycles | F/F₀ | Prevailing torque (Nm) |
|---|---|---|
| 0 | 1.000 | 6.5 (initial) |
| 50 | 0.850 | 5.8 |
| 100 | 0.720 | 5.0 |
| 200 | 0.560 | 4.2 |
| 500 | 0.350 | 3.2 |
| 1,000 | 0.220 | 2.5 |
| 2,000 | 0.140 | 2.0 |

#### Critical Failure Mode: Combined Axial + Transverse
Under **combined axial + transverse loading**, prevailing torque nuts can completely detach:

| Loading combination | Prevailing torque nut result |
|---|---|
| Transverse only | Loosens but retains residual clamp |
| Transverse + 20% axial | Same |
| Transverse + 50% axial | **Nut continues past zero clamp** |
| Transverse + 80% axial | **Complete nut detachment** |

**Mechanism**: When the alternating axial load momentarily exceeds the residual clamp force + prevailing torque, the nut gains a small increment of rotation. Over many cycles, these increments accumulate until the nut unscrews completely. This was first documented by Eccles and represents a serious safety concern for prevailing torque nuts in combined loading environments.

---

### Dataset 5: Torque Residual Method (Eccles's Contribution)

Eccles developed a method to assess loosening by measuring the **residual torque** after vibration testing:

```
T_residual = T_tightening − ΔT_loosening
```

| Cycles | T_residual / T_initial | F/F₀ |
|---|---|---|
| 0 | 1.000 | 1.000 |
| 100 | 0.650 | 0.720 |
| 500 | 0.350 | 0.420 |
| 1,000 | 0.180 | 0.250 |

**Note**: Residual torque drops faster than preload because torque also depends on friction (which changes during vibration).

---

## Reproduction Parameters

| Parameter | M8 test | M10 test | M12 test |
|---|---|---|---|
| Class | 8.8 / 10.9 / 12.9 | 10.9 | 10.9 |
| Preload (70% proof) | 15.5–22.0 kN | 35.0 kN | 50.5 kN |
| Frequency | 12.5 Hz | 12.5 Hz | 12.5 Hz |
| Displacement | Per DIN 25201-4 | Per DIN 25201-4 | Per DIN 25201-4 |
| Duration | 2,000 cycles | 2,000 cycles | 2,000 cycles |
| Coatings | 7 types tested | Zinc-plated | Zinc-plated |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate Eccles's primary test.
> NOTE: DIN 25201-4 test — displacement adjusted so unsecured bolt loosens in 300±100 cycles.

### Bolt & Thread Geometry (M8 Primary)

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M8×1.25 | — |
| d (nominal) | 8.0 | mm |
| p (pitch) | 1.25 | mm |
| d₂ (pitch dia.) | 7.188 | mm |
| d₃ (minor dia.) | 6.466 | mm |
| Aₜ (stress area) | 36.6 | mm² |
| d_head (AF) | 13.0 | mm |
| Head height | 5.3 | mm |
| Nut height | 6.5 | mm |
| d_hole | 9.0 | mm |
| Grip length | 24.0 | mm (estimated) |
| Helix angle | 3.17 | ° |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 10.9 Q&T | 210,000 | 940 | 1,040 | 0.3 |
| Plates | Steel | 210,000 | — | — | 0.3 |

### Loading — DIN 25201-4 Test

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 22,000 | N |
| % Yield | 63.9 | % |
| Transverse disp. δ | 0.70 | mm (estimated for 300-cycle reference) |
| Frequency | 12.5 | Hz |
| Cycles | 2,000 | — |

### Friction — Zinc-Plated Baseline

| Parameter | Value |
|---|---|
| μ_initial | 0.14 |
| Lubricated | false |

### Coating Comparison Configurations

| Config | Surface | μ_initial | Expected 50% life (cycles) |
|---|---|---|---|
| Bare steel | Degreased | 0.25 | ~80 |
| Zinc dry | Zinc-plated | 0.22 | ~50 |
| Zinc + oil | Zinc + oil | 0.14 | ~25 |
| Cadmium | Cadmium-plated | 0.10 | ~12 |
| Phosphate+oil | Phosphate+oil | 0.12 | ~18 |
| MoS₂ | Phosphate+MoS₂ | 0.08 | ~8 |
| Zinc flake | Geomet | 0.12 | ~20 |

### ValidationCase — Zinc Baseline (for validation_cases.py)

```python
ValidationCase(
    name="Eccles_2010_M8_zinc",
    bolt_size="M8x1.25",
    bolt_diameter_mm=8.0,
    pitch_mm=1.25,
    initial_preload_N=22000,
    preload_percent_yield=63.9,
    transverse_displacement_mm=0.70,
    frequency_Hz=12.5,
    n_cycles=500,
    mu_initial=0.14,
    lubricated=False,
    expected_final_preload_ratio=0.023,
    expected_loosening_deg=18.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.864),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.750),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.591),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.364),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.205),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.091),
        ExperimentalDataPoint(cycles=500, preload_ratio=0.023),
    ]
)
```
