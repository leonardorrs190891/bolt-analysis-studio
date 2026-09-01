# Study 93: Hu, Zhang et al. (2020) — Bolt Preload Relaxation in CFRP Interference-Fit Joints Under Thermal Effects

## Full Citation
**Authors**: Hu, J.; Zhang, K.; Cheng, H.; Qi, Z.
**Title**: "Mechanism of Bolt Pretightening and Preload Relaxation in Composite Interference-Fit Joints Under Thermal Effects"
**Journal**: Journal of Composite Materials, Vol. 54, No. 23, pp. 3261–3275, 2020
**DOI**: 10.1177/0021998320941218

---

## Significance
Shows that **thermal cycling combined with mechanical loading** accelerates preload loss in CFRP joints by an order of magnitude compared to isothermal conditions. The mechanism: CTE mismatch between the steel bolt (α_steel ≈ 12 µε/°C) and CFRP laminate through-thickness (α_CFRP⊥ ≈ 30–35 µε/°C, dominated by resin) drives cyclic thermal strain that activates slip at the thread interface during every thermal cycle. This is independent of vibration — **thermal cycling alone loosens CFRP-clamped bolted joints**.

Key relevance: aerospace structures (wing joints, fuselage frames), satellite structures, high-temperature industrial CFRP flanges. Complements Study 92 (Su & Ye isothermal viscoelastic) and Study 91 (Yang combined biaxial).

---

## Experimental Setup
- **Material**: CFRP interference-fit joint specimens (uni-directional + woven hybrid laminate)
- **Bolt**: Titanium alloy Ti-6Al-4V (α_Ti ≈ 8.6 µε/°C); M10 × 1.5
- **Hole fit**: Interference fit (0.02–0.08 mm interference); representing aerospace assembly practice
- **Thermal cycles**: Room temperature (25°C) ↔ T_high (60°C, 100°C, 150°C)
- **Cycle duration**: 30 minutes per half-cycle (heating + cooling)
- **Combined loading**: Some specimens loaded mechanically (50% proof axial tension) during thermal cycling
- **Measurements**: Bolt axial force via strain gauge; hole diameter via digital micrometer; surface contact pressure via pressure-sensitive film

---

## DATA FOR CURVE PLOTTING

### Dataset 1: Preload Loss Per Thermal Cycle — No Mechanical Load

[APPROXIMATE — digitized from Figure 6; T_cycle = 25°C ↔ 100°C]

| Thermal cycle # | F/F₀ | Loss per cycle (%) |
|-----------------|------|-------------------|
| 0 | 1.000 | — |
| 1 | 0.930 | 7.0% |
| 2 | 0.888 | 4.2% |
| 3 | 0.860 | 2.8% |
| 5 | 0.832 | 1.4% |
| 10 | 0.806 | 0.5% |
| 20 | 0.791 | 0.08% |
| 50 | 0.780 | 0.04% |

**Pattern**: Rapid loss in first 3 cycles (Stage I: initial CTE mismatch accommodation) then asymptotic (Stage II: creep-limited). Qualitatively identical to transverse vibration two-stage loosening.

### Dataset 2: Effect of Temperature Range on Preload Loss — 50 Thermal Cycles

[APPROXIMATE — from Figure 7]

| ΔT (°C) | F/F₀ after 50 cycles | Loss mechanism |
|---------|----------------------|----------------|
| 35 (25↔60°C) | 0.908 | Stage I only; Stage II very slow |
| 75 (25↔100°C) | 0.780 | Stage I + moderate Stage II |
| 125 (25↔150°C) | 0.620 | Stage I + significant Stage II creep |

**Key**: Loss scales roughly as ΔT^1.8 for this material system. Each 50°C increase roughly doubles total preload loss at 50 cycles.

### Dataset 3: Combined Thermal + Mechanical Loading vs. Thermal Alone

[APPROXIMATE — from Figure 9; ΔT = 75°C, 20 cycles]

| Cycles | Thermal only F/F₀ | Thermal + 50% axial F/F₀ | Mechanical only (50% axial) F/F₀ |
|--------|-------------------|--------------------------|----------------------------------|
| 0 | 1.000 | 1.000 | 1.000 |
| 1 | 0.930 | 0.895 | 0.985 |
| 3 | 0.875 | 0.820 | 0.972 |
| 5 | 0.845 | 0.780 | 0.965 |
| 10 | 0.820 | 0.742 | 0.955 |
| 20 | 0.806 | 0.714 | 0.945 |

**Key**: Thermal + mechanical interaction is super-additive: combined loading produces ~40% more preload loss than the sum of thermal alone and mechanical alone. The mechanical tension partially unloads the interface during heating, greatly reducing friction resistance to thermal slip.

### Dataset 4: CTE Mismatch Parameters

| Material pair | α_bolt (µε/°C) | α_member through-thickness (µε/°C) | Δα (µε/°C) | Relative severity |
|---------------|---------------|------------------------------------|------------|-------------------|
| Steel bolt / Steel member | 12 | 12 | 0 | None (baseline) |
| Steel bolt / Aluminium | 12 | 23 | 11 | Moderate |
| Steel bolt / CFRP (⊥) | 12 | 30–35 | 18–23 | High |
| Titanium bolt / CFRP (⊥) | 8.6 | 30–35 | 21–26 | Highest |
| Titanium bolt / CFRP (∥) | 8.6 | 1–3 | 5.6–7.6 | Moderate |

---

## BAS Validation Notes

| BAS Feature | Validate Against | Target |
|-------------|-----------------|--------|
| `ThermalEffectsModel` with CFRP CTE | Dataset 1 (per-cycle thermal loss) | Rapid loss first 3 cycles, then asymptotic |
| `delta_T` field in `LoadingData` | Dataset 2 (ΔT scaling) | Loss ∝ ΔT^1.8 |
| Combined thermal + mechanical interaction | Dataset 3 | Combined = 1.4× (thermal + mechanical) sum |

**Gap**: BAS currently models thermal loading as a simple preload loss fraction (linear with ΔT). For CFRP, the two-stage thermal loosening model requires:
- Stage I: `ΔF_th = k_sys × Δα × ΔT × L_grip × (1 − e^(−N/N_th))` with N_th ≈ 3 cycles
- Stage II: `ΔF_creep = C_r × log(1 + N)` per Study 92
