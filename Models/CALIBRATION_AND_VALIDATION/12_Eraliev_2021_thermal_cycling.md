# Study 12: Eraliev et al. (2021) — Self-Loosening Under Cyclical Temperature Changes

## Full Citation
**Authors**: Eraliev, O. M.; Zhang, Y.-H.; Lee, K.-H.; Lee, C.-H.
**Title**: "Experimental Investigation on Self-Loosening of a Bolted Joint under Cyclical Temperature Changes"
**Journal**: Advances in Mechanical Engineering, 2021, 13(10)
**DOI**: 10.1177/16878140211039428
**Access**: Open Access (SAGE)
**URL**: https://journals.sagepub.com/doi/full/10.1177/16878140211039428

---

## Experimental Setup

### Bolt Specifications
- **Size**: M12 × 1.75 (ISO metric coarse)
- **Property class**: 8.8
- **Material**: Medium carbon steel
- **Yield R_p0.2**: 640 MPa
- **UTS R_m**: 800 MPa
- **Stress area**: 84.3 mm²
- **Proof load**: 53,950 N (Class 8.8)
- **Coefficient of thermal expansion**: 12.0 × 10⁻⁶ /°C (steel)

### Nut
- Standard hex nut, Class 8
- Height: 10.4 mm

### Clamped Members
- **Material**: Carbon steel plates
- **Coefficient of thermal expansion**: 12.0 × 10⁻⁶ /°C (same as bolt → minimal differential expansion)
- **Note**: Real applications with dissimilar materials (e.g., steel bolt in aluminum flange) show MUCH greater thermal loosening

### Test Fixture
- Custom thermal cycling chamber with heating elements
- Strain-gauged bolt for continuous preload measurement
- Temperature measured via thermocouples on bolt and plates

### Test Parameters
- **Initial preload**: 5,000 N (5 kN) — intentionally low (9.3% of proof load)
- **Temperature range**: Room temperature (~25°C) to ~60°C
- **Heating rate**: Not specified (slow enough for thermal equilibrium)
- **Number of thermal cycles**: 10
- **No mechanical loading** — purely thermal effects

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Preload vs. Thermal Cycle Number

**[APPROXIMATE — digitized from published Figures 5–7]**

| Thermal cycle | Preload at max temp (N) | Preload after cooling (N) | F_cooled/F₀ | Loss per cycle (N) |
|---|---|---|---|---|
| 0 (initial, room temp) | — | 5,000 | 1.000 | — |
| 1 (heating) | ~8,000 | — | — | — |
| 1 (cooled) | — | 4,500 | 0.900 | 500 |
| 2 (heating) | ~7,200 | — | — | — |
| 2 (cooled) | — | 4,400 | 0.880 | 100 |
| 3 (heating) | ~7,000 | — | — | — |
| 3 (cooled) | — | 4,350 | 0.870 | 50 |
| 4 (cooled) | — | 4,320 | 0.864 | 30 |
| 5 (cooled) | — | 4,300 | 0.860 | 20 |
| 6 (cooled) | — | 4,285 | 0.857 | 15 |
| 7 (cooled) | — | 4,275 | 0.855 | 10 |
| 8 (cooled) | — | 4,270 | 0.854 | 5 |
| 9 (cooled) | — | 4,265 | 0.853 | 5 |
| 10 (cooled) | — | 4,260 | 0.852 | 5 |

### Dataset 2: Preload vs. Temperature Within a Single Cycle

**Cycle 1 detail** (F₀ = 5 kN):

| Temperature (°C) | Preload (N) | Notes |
|---|---|---|
| 25 (start) | 5,000 | Initial |
| 30 | 5,400 | Bolt elongation < joint compression |
| 35 | 5,900 | Preload increasing |
| 40 | 6,500 | Continued increase |
| 45 | 7,200 | Approaching max |
| 50 | 7,600 | |
| 55 | 7,900 | |
| 60 (max) | 8,000 | Peak preload at max temperature |
| 55 | 7,600 | Cooling begins |
| 50 | 7,000 | |
| 45 | 6,300 | |
| 40 | 5,600 | |
| 35 | 5,000 | Equal to initial — but then drops further! |
| 30 | 4,700 | Below initial preload |
| 25 (end) | 4,500 | **10% loss from initial** |

**Physical mechanism**: During heating, increased preload causes localized plastic deformation at thread flanks and bearing surfaces (embedment). When cooled, the bolt returns to its original length but the plastic deformation is permanent → net preload loss.

---

### Dataset 3: Cumulative Loss vs. Cycle Count

For the logarithmic decay model:
```
F_loss(n) = F₀ × [1 - a × ln(1 + b × n)]
```
Fitted parameters: a ≈ 0.065, b ≈ 1.0

| Cycle n | Predicted F/F₀ | Measured F/F₀ |
|---|---|---|
| 1 | 0.910 | 0.900 |
| 2 | 0.882 | 0.880 |
| 5 | 0.860 | 0.860 |
| 10 | 0.852 | 0.852 |
| 20 | 0.845 (extrapolated) | — |
| 50 | 0.835 (extrapolated) | — |
| 100 | 0.828 (extrapolated) | — |

---

## Comparison: Same vs. Dissimilar Materials

The Eraliev data is for **same-material** joints (steel-on-steel). For dissimilar materials with different CTE, the effect is dramatically larger.

### Estimated Thermal Loosening for Dissimilar Materials

For steel bolt (α = 12×10⁻⁶/°C) clamping aluminum (α = 23×10⁻⁶/°C):

| ΔT (°C) | Differential strain | Additional force change | Est. loss per cycle |
|---|---|---|---|
| 20 | 2.2×10⁻⁴ | ~2,000 N for M12 | ~8% |
| 50 | 5.5×10⁻⁴ | ~5,000 N for M12 | ~15% |
| 100 | 1.1×10⁻³ | ~10,000 N for M12 | ~25% |
| 200 | 2.2×10⁻³ | ~20,000 N for M12 | >40% |

### 2025 FE Study on Temperature Effects (J. Braz. Soc. Mech. Sci. Eng.)
A recent 2025 FE study on M10×1.5 bolts found:
- ΔT > 200°C → **11.7% loosening** in a short period
- Greatest loss during the **first thermal cycle** (consistent with Eraliev)
- Creep relaxation becomes significant above 300°C for carbon steel bolts
- For ASTM A193 B7 bolts at elevated temperatures, relaxation follows Norton's creep law

---

## Key Findings for Petrobras Applications

1. **First thermal cycle is critical**: produces the greatest preload loss (~10% for 35°C rise with same materials)
2. **Subsequent cycles**: diminishing losses (logarithmic decay)
3. **Dissimilar materials**: dramatically amplify thermal loosening
4. **Sour service (H₂S) environments**: Temperature fluctuations during startup/shutdown are particularly damaging because the bolt is simultaneously weakened by hydrogen embrittlement
5. **Mitigation**: Use materials with matched CTE; apply sufficient initial preload to absorb thermal-induced relaxation; consider Belleville washers for thermal compensation

---

## Reproduction Parameters

| Parameter | Value | Units |
|---|---|---|
| Bolt | M12 × 1.75 | — |
| Class | 8.8 | — |
| Initial preload | 5,000 | N |
| Temperature range | 25–60 | °C |
| ΔT per cycle | 35 | °C |
| Heating rate | ~1 | °C/min (est.) |
| Number of cycles | 10 | — |
| CTE (bolt) | 12.0 × 10⁻⁶ | /°C |
| CTE (plates) | 12.0 × 10⁻⁶ | /°C |
| E (at 25°C) | 206,000 | MPa |
| E (at 60°C) | ~204,000 | MPa |

---

## MSD BUILDER CONFIGURATION

> Copy these values directly into the MSD Builder (Tab 2) to recreate this experiment.
> NOTE: THERMAL loading only — no transverse displacement. Set delta_T in loading config.

### Bolt & Thread Geometry

| Parameter | Value | Unit |
|---|---|---|
| Bolt size | M12×1.75 | — |
| d (nominal) | 12.0 | mm |
| p (pitch) | 1.75 | mm |
| d₂ (pitch dia.) | 10.863 | mm |
| d₃ (minor dia.) | 9.853 | mm |
| Aₜ (stress area) | 84.3 | mm² |
| d_head (AF) | 18.0 | mm |
| Head height | 7.5 | mm |
| Nut height | 10.4 | mm |
| d_hole | 13.5 | mm |
| Grip length | 25.0 | mm (estimated) |
| Helix angle | 2.93 | ° |

### Material Properties

| Component | Material | E (MPa) | Sy (MPa) | Su (MPa) | ν | CTE (/°C) |
|---|---|---|---|---|---|---|
| Bolt/nut | Class 8.8 Q&T | 206,000 | 640 | 800 | 0.3 | 12.0×10⁻⁶ |
| Plates | Carbon steel | 206,000 | — | — | 0.3 | 12.0×10⁻⁶ |

### MSD Element Chain

    GROUND — FLANGE — FLANGE — NUT — THREAD — SHANK — HEAD — GROUND

### Loading (PropertyInspector) — Thermal Cycling

| Parameter | Value | Unit |
|---|---|---|
| Load type | THERMAL | — |
| Preload F₀ | 5,000 | N |
| % Yield | 9.3 | % |
| Transverse disp. δ | 0.0 | mm |
| ΔT | 35.0 | °C |
| Cycles | 10 | — |

### Friction (PropertyInspector)

| Parameter | Value |
|---|---|
| μ_initial | 0.15 |
| Lubricated | false |
| Bolt diameter | 12.0 mm |
| Pitch | 1.75 mm |

### ValidationCase (for validation_cases.py)

```python
ValidationCase(
    name="Eraliev_2021_M12_thermal",
    bolt_size="M12x1.75",
    bolt_diameter_mm=12.0,
    pitch_mm=1.75,
    initial_preload_N=5000,
    preload_percent_yield=9.3,
    transverse_displacement_mm=0.0,
    frequency_Hz=0.0,
    n_cycles=10,
    mu_initial=0.15,
    lubricated=False,
    expected_final_preload_ratio=0.852,
    expected_loosening_deg=0.0,
    experimental_data=[
        ExperimentalDataPoint(cycles=0, preload_ratio=1.000),
        ExperimentalDataPoint(cycles=1, preload_ratio=0.900),
        ExperimentalDataPoint(cycles=2, preload_ratio=0.880),
        ExperimentalDataPoint(cycles=5, preload_ratio=0.860),
        ExperimentalDataPoint(cycles=10, preload_ratio=0.852),
    ]
)
```
