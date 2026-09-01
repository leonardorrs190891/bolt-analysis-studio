# Study 11: Hattori, Yamashita & Mizuno (2010) — Critical Slippage Data (M6, M10, M16)

## Full Citation
**Authors**: Hattori, T.; Yamashita, M.; Mizuno, M.
**Title**: "Loosening and Sliding Behaviour of Bolt-Nut Fastener under Transverse Loading"
**Journal**: EPJ Web of Conferences, 2010, 6, 08002
**DOI**: 10.1051/epjconf/20100608002
**Conference**: ICEM14 — 14th International Conference on Experimental Mechanics
**Access**: Open Access
**URL**: https://www.epj-conferences.org/articles/epjconf/pdf/2010/05/epjconf_ICEM14_08002.pdf

---

## Experimental Setup

### Bolt Specifications (Three Sizes Tested)

| Parameter | M6 | M10 | M16 |
|---|---|---|---|
| Pitch (mm) | 1.0 | 1.5 | 2.0 |
| Stress area (mm²) | 20.1 | 58.0 | 157.0 |
| Property class | 4.8 | 4.8 | 4.8 |
| Yield R_p0.2 (MPa) | 320 | 320 | 320 |
| UTS R_m (MPa) | 420 | 420 | 420 |
| Standard axial tension Fs (N) | 4,412 | 12,732 | 34,464 |

**Note**: Class 4.8 is low-strength — intentionally chosen to allow loosening at moderate displacements. For high-strength Class 10.9 bolts, scale preloads accordingly.

### Nut
- **Type**: Standard hex nut
- **Class**: 4

### Clamped Members
- **Material**: S45C steel (JIS, equivalent to AISI 1045)
- **E**: 206 GPa
- **ν**: 0.3
- **Surface**: Machined, no coating

### Test Fixture
- **Type**: Custom transverse vibration rig
- **Loading**: Displacement-controlled cyclic transverse loading
- **Measurement**: Strain gauges on bolt for preload; displacement transducer for slippage
- **Special**: Reaction moment sensors at nut and bolt head to measure individual torque components

---

## Test Matrix

### Preload Levels for M16 (Primary Test Size)
| Test ID | Bolt axial tension F₀ (N) | F₀/Fs (%) |
|---|---|---|
| M16-15 | 15,000 | 43.5% |
| M16-20 | 20,000 | 58.0% |
| M16-25 | 25,000 | 72.5% |
| M16-30 | 30,000 | 87.0% |
| M16-35 | 35,000 | 101.5% |

### Displacement Amplitudes
- Range: 0.1 mm to 1.0 mm (varied per test)
- Loading rate: Quasi-static and dynamic (1–5 Hz)

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Critical Slippage S_cr for M16 (Class 4.8)

The **critical slippage S_cr** is the transverse displacement at which complete bearing-surface slip occurs and loosening begins to propagate. Below S_cr, only partial slip occurs (Stage I). Above S_cr, Stage II loosening (rotational) proceeds.

| Bolt axial tension F₀ (kN) | Critical slippage S_cr (mm) | S_cr / d ratio |
|---|---|---|
| 15 | 0.31 | 0.019 |
| 20 | 0.33 | 0.021 |
| 25 | 0.39 | 0.024 |
| 30 | 0.48 | 0.030 |
| 35 | 0.55 | 0.034 |

**Key finding**: S_cr increases approximately linearly with preload. Higher preload requires larger displacement to initiate loosening.

**Empirical fit**:
```
S_cr (mm) = 0.012 × F₀(kN) + 0.12    (for M16 Class 4.8)
```
Or in dimensionless form:
```
S_cr / d = 0.00075 × (F₀/Fs) + 0.012
```

---

### Dataset 2: Loosening Speed vs. Displacement (M16, F₀ = 25 kN)

**Loosening speed** = rate of preload loss (N/cycle) after onset of Stage II

| Displacement amplitude (mm) | Loosening speed (N/cycle) | S/S_cr ratio |
|---|---|---|
| 0.20 | 0 (no loosening) | 0.51 |
| 0.30 | 0 (Stage I only) | 0.77 |
| 0.39 | ~10 (onset) | 1.00 |
| 0.50 | ~80 | 1.28 |
| 0.60 | ~200 | 1.54 |
| 0.70 | ~400 | 1.79 |
| 0.80 | ~650 | 2.05 |
| 0.90 | ~900 | 2.31 |
| 1.00 | ~1,200 | 2.56 |

**Key finding**: Loosening speed increases approximately as **(S/S_cr − 1)²** for S > S_cr.

---

### Dataset 3: Reaction Moments at Thread and Bearing Surfaces (M16, F₀ = 25 kN, S = 0.6 mm)

This unique dataset separates thread friction torque from bearing friction torque during a loading cycle.

**[APPROXIMATE — digitized from Figure 4]**

| Phase in cycle | Thread reaction torque T_th (N·m) | Bearing reaction torque T_b (N·m) | Net loosening torque (N·m) |
|---|---|---|---|
| Loading (0→+δ) | +3.2 (resisting) | +5.8 (resisting) | -9.0 (no loosening) |
| Max displacement (+δ) | +2.0 | +4.5 | -6.5 |
| Unloading (+δ→0) | -1.5 (assisting) | +3.0 (resisting) | -1.5 |
| Reversal (0→−δ) | -3.0 (assisting) | -0.5 (assisting) | +3.5 (LOOSENING) |
| Max negative (−δ) | -2.5 | -1.0 | +3.5 (LOOSENING) |
| Return (−δ→0) | +1.0 (resisting) | +2.0 (resisting) | -3.0 |

**Critical observation**: Loosening torque is positive only during the reversal phase of the displacement cycle. The pitch torque (~0.8 N·m for M16 at 25 kN) contributes but is small compared to the friction torque asymmetry during reversal.

---

### Dataset 4: Cross-Size Comparison

#### Critical Slippage Normalized

| Bolt size | F₀ (kN) | F₀/Fs | S_cr (mm) | S_cr/d |
|---|---|---|---|---|
| M6 | 2.5 | 0.57 | 0.10 | 0.017 |
| M6 | 3.5 | 0.79 | 0.14 | 0.023 |
| M10 | 7.0 | 0.55 | 0.22 | 0.022 |
| M10 | 10.0 | 0.79 | 0.30 | 0.030 |
| M16 | 20.0 | 0.58 | 0.33 | 0.021 |
| M16 | 30.0 | 0.87 | 0.48 | 0.030 |

**Scaling observation**: S_cr/d is approximately constant at **0.020–0.030** for a given F₀/Fs ratio. This suggests a **similitude relationship** for scaling loosening tests across bolt sizes.

---

### Dataset 5: Preload Decay Curves (M16, Different Preloads)

**[APPROXIMATE — digitized from published figures]**

#### F₀ = 15 kN, S = 0.5 mm
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.820 |
| 20 | 0.680 |
| 50 | 0.400 |
| 100 | 0.180 |
| 200 | 0.050 |

#### F₀ = 25 kN, S = 0.5 mm
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.880 |
| 20 | 0.780 |
| 50 | 0.560 |
| 100 | 0.340 |
| 200 | 0.160 |
| 400 | 0.050 |

#### F₀ = 35 kN, S = 0.5 mm
| Cycles | F/F₀ |
|---|---|
| 0 | 1.000 |
| 10 | 0.960 |
| 20 | 0.920 |
| 50 | 0.820 |
| 100 | 0.700 |
| 200 | 0.520 |
| 400 | 0.320 |
| 800 | 0.150 |

---

## Reproduction Notes

### FEA Parameters (Hattori also did FEA validation)
- **Software**: ANSYS (likely Mechanical APDL)
- **Element type**: SOLID185 (3D brick)
- **Thread geometry**: Simplified helix (cosinusoidal profile)
- **Contact**: CONTA174/TARGE170, Coulomb friction
- **Friction coefficient**: μ = 0.15 (all surfaces)
- **Mesh**: ~30,000 elements for M16 model
- **Loading**: Quasi-static, displacement-controlled

### S45C Steel Properties
| Property | Value |
|---|---|
| Young's modulus E | 206,000 MPa |
| Poisson's ratio ν | 0.3 |
| Yield strength | 490 MPa |
| Density | 7,800 kg/m³ |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this experiment.
> NOTE: Class 4.8 (LOW strength). Three bolt sizes tested — primary data for M16.

### M16 Configuration (Primary)

#### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M16×2.0 | — |
| d (nominal) | 16.0 | mm |
| p (pitch) | 2.00 | mm |
| d₂ (pitch dia.) | 14.701 | mm |
| d₃ (minor dia.) | 13.546 | mm |
| Aₜ (stress area) | 157.0 | mm² |
| d_head (AF) | 24.0 | mm |
| Head height | 10.0 | mm |
| Nut height | 13.0 | mm |
| d_hole | 17.5 | mm |
| Grip length | 30.0 | mm (estimated) |
| Helix angle | 2.48 | ° |
| r_be (eff. bearing) | 10.00 | mm |

#### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν |
|---|---|---|---|---|---|
| Bolt/nut | Class 4.8 | 206,000 | 320 | 420 | 0.3 |
| Plates | S45C (≈AISI 1045) | 206,000 | 490 | 690 | 0.3 |

#### Loading — Baseline Test

| Parameter | Value | Unit |
|---|---|---|
| Load type | TRANSVERSE | — |
| Preload F₀ | 25,000 | N |
| % Yield | 49.8 | % |
| Transverse disp. δ | 0.50 | mm |
| Frequency | 5.0 | Hz |
| Cycles | 400 | — |

#### Friction

| Parameter | Value |
|---|---|
| μ_initial | 0.15 |
| Lubricated | false |

### Cross-Size Configurations

| Bolt | F₀ (N) | % Yield | d_head (mm) | d_hole (mm) | δ (mm) |
|---|---|---|---|---|---|
| M6×1.0 | 2,500 | 39.0 | 10.0 | 6.6 | 0.10-0.20 |
| M10×1.5 | 7,000 | 37.8 | 16.0 | 11.0 | 0.20-0.40 |
| M16×2.0 | 25,000 | 49.8 | 24.0 | 17.5 | 0.30-1.00 |

### ValidationCase — M16 at 25kN (for validation_cases.py)

```python
ValidationCase(
    name="Hattori_2010_M16_25kN",
    bolt_size="M16x2.0",
    bolt_diameter_mm=16.0,
    pitch_mm=2.00,
    initial_preload_N=25000,
    preload_percent_yield=49.8,
    transverse_displacement_mm=0.50,
    frequency_Hz=5.0,
    n_cycles=400,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.05,
    expected_loosening_deg=12.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.880),
        ExperimentalDataPoint(cycles=20, preload_ratio=0.780),
        ExperimentalDataPoint(cycles=50, preload_ratio=0.560),
        ExperimentalDataPoint(cycles=100, preload_ratio=0.340),
        ExperimentalDataPoint(cycles=200, preload_ratio=0.160),
        ExperimentalDataPoint(cycles=400, preload_ratio=0.050),
    ]
)
```
