# Bolt Loosening Stage Definitions — Literature Review
**Bolt Analysis Studio v4.0 — Implementation reference**
*Compiled 2026-02-24. Updated 2026-02-24 with axial and combined loading models.*

---

## 1. The Foundational Two-Stage Model (Jiang et al., 2003–2007)

The most widely accepted classification in the literature is the **two-stage model** from:

> Jiang, Y.Y., Zhang, M., Lee, C.H. — "A Study of Early Stage Self-Loosening of Bolted Joints,"
> *Journal of Mechanical Design*, Vol. 125(3), pp. 518–526, **2003**.
>
> Zhang, M., Jiang, Y.Y. — "An Experimental Study of Self-Loosening of Bolted Joints,"
> *Journal of Mechanical Design*, Vol. 126(6), pp. 1062–1064, **2004**.
>
> Jiang, Y.Y. et al. — "Finite Element Modeling of Self-Loosening of Bolted Joints,"
> *Journal of Mechanical Design*, Vol. 129(2), pp. 218–226, **2007**.

Test conditions (2004 paper): M12 × 1.75 bolts, preloaded to 75% yield (≈ 25 kN),
cyclic transverse shear displacement at constant amplitude.

**Loading type: TRANSVERSE (Junker mechanism)**

---

### Stage I — Non-Rotational Loosening ("Early Stage")

| Property | Value / Description |
|----------|---------------------|
| **Standard literature name** | "Stage I", "Early-stage loosening", "Non-rotational loosening" |
| **Rotation criterion** | Nut rotation < **0.5°** cumulative — the single most-cited quantitative Jiang threshold |
| **F/F₀ at end of Stage I** | Not fixed — reported range 60–90% depending on loading amplitude; Jiang does **not** assign a preload-ratio boundary to Stage I; the boundary is the 0.5° rotation criterion only |
| **Physical mechanism** | Cyclic micro-slip at thread and bearing contacts causes local plastic ratcheting at thread roots. Stresses redistribute, bolt elongation decreases → preload drops without any nut rotation |
| **Fretting contribution** | Fretting wear at thread interfaces contributes a slow secondary decay after the initial drop |
| **Curve shape** | Rapid drop in first 5–50 cycles, then slower gradual decay. On a lin-log plot: steep initial descent levelling to a gentle slope |

**Key insight:** The 0.5° boundary is a **kinematic** criterion, not a preload-ratio criterion.
Preload can drop anywhere from 5% to 40%+ before this rotation threshold is reached.

---

### Stage II — Rotational Loosening ("Back-off")

| Property | Value / Description |
|----------|---------------------|
| **Standard literature name** | "Stage II", "Rotational loosening", "Nut back-off" |
| **Rotation criterion** | Cumulative rotation ≥ **0.5°** — triggers transition from Stage I to Stage II |
| **F/F₀ at entry** | Variable; whatever preload remains when rotation first exceeds 0.5° |
| **Physical mechanism** | Gross slip simultaneously at thread contact AND bearing head contact eliminates both friction torques (M_thread and M_bearing). Junker torque balance becomes: M_TP > M_K + M_G → nut rotates back along the helix |
| **Junker condition** | `M_TP = F_p · r_m · tan(λ) > M_K + M_G = F_p·(d₂/2)·µ_t/cos(α) + F_p·r_eff·µ_b` |
| **Curve shape** | Faster, roughly linear decrease of F/F₀ vs. cycles (on lin-lin scale). Steeper slope than Stage I |

---

## 2. Three-Stage Model — Axial Excitation

Reported for **axial** (not transverse) excitation and SHM / acoustic emission monitoring.
Applies to axially loaded joints, axial vibration, and is used in the BAS axial loading model.

### Primary sources

> "Competitive Failure of Bolt Loosening and Fatigue under Different Preloads,"
> *Chinese Journal of Mechanical Engineering*, 2021.
>
> Wang, J. et al. — "A three-stage criterion for loose bolt identification under random
> vibration," *Engineering Failure Analysis*, 2021.
>
> Multiple 2020–2022 acoustic emission / structural health monitoring papers
> from Chinese research groups (cited in review: Friction 9(6), 2021).

### Stage I — Rapid Initial Drop

| Property | Value / Description |
|----------|---------------------|
| **Standard name** | "Stage I", "Initial rapid drop", "Embedding phase" |
| **Duration** | First **5–50 cycles** (literature range; highly amplitude-dependent) |
| **Mechanism** | Asperity crushing, initial micro-plastic deformation of mating surfaces. Thread and bearing contact areas "bed in". Very high preload loss rate per cycle. |
| **F/F₀ loss** | Typically 10–40% of F₀ lost in this phase (joint geometry and preload level dependent) |
| **Curve shape** | Very steep initial drop on lin-lin plot; asymptotically approaches Stage II rate |
| **BAS transition criterion** | `_axial_rapid_done` latch: fires after `n_stage_i_cycles` cycles (default 50) OR when the 10-cycle rolling loss rate drops below 0.1%/cycle (embedding plateau reached) |

### Stage II — Slow Steady Decay

| Property | Value / Description |
|----------|---------------------|
| **Standard name** | "Stage II", "Slow decay", "Fretting / creep stage" |
| **Duration** | Hundreds to thousands of cycles |
| **Mechanism** | Fretting wear at thread contacts (Vingsbo-Söderberg partial-slip regime), viscoelastic creep/relaxation of clamped members, continued low-rate micro-slip |
| **F/F₀ range** | Slow, nearly linear decline from end-of-Stage-I preload down to ~0.40 |
| **Curve shape** | Nearly flat on lin-lin plot; slow steady slope. Much lower dF/dN than Stage I |
| **BAS transition criterion** | F/F₀ ≤ 0.40 (ISO 16130:2015 lower boundary of "acceptable" zone) OR Miner's damage fraction ≥ 0.80 |

### Stage III — Rapid Failure

| Property | Value / Description |
|----------|---------------------|
| **Standard name** | "Stage III", "Rapid failure", "Fatigue / runaway" |
| **Mechanism** | Fatigue crack initiation at thread root (cyclic stress amplitude has accumulated sufficient damage) OR gross rotational back-off triggered by the now-low preload reducing friction below the Junker threshold |
| **F/F₀** | ≤ 0.40 (ISO 16130 "poor self-locking" zone) |
| **Miner's trigger** | D ≥ 0.80 (fatigue life 80% consumed → crack initiation imminent) |
| **Curve shape** | Sudden steep drop toward 0; may be very rapid once fatigue crack propagates or rotational loosening begins |
| **BAS criterion** | `preload_ratio ≤ 0.40` OR `state.damage_fraction ≥ 0.80` |

### Axial vs. Transverse model comparison

| Aspect | Transverse (Jiang) | Axial (3-stage) |
|--------|--------------------|-----------------|
| Primary driver | Transverse slip → nut back-off | Axial stress cycling → fatigue + fretting |
| Stage I boundary | 0.5° cumulative rotation (kinematic) | ~50 cycles OR rate plateau (time-based) |
| Stage II / III boundary | F/F₀ sub-bands within Jiang Stage II | F/F₀ ≤ 0.40 (ISO 16130 poor zone) |
| Rotation involved? | Yes — nut back-off defines Stage II | No — primarily non-rotational until Stage III |
| Standard reference | DIN 25201-4; ISO 16130 | ISO 16130 zones (adapted) |

---

## 3. BAS Stage Model Selection by Loading Type

BAS selects the classification model automatically from `model.global_loading.load_type`:

| `load_type` field value | BAS model | Phases available |
|------------------------|-----------|-----------------|
| `TRANSVERSE` (default) | 5-stage Jiang | STABLE → NON_ROTATIONAL → TRANSITION → ROTATIONAL → RUNAWAY |
| `AXIAL` | 3-stage axial | AXIAL_STAGE_I → AXIAL_STAGE_II → AXIAL_STAGE_III |
| `COMBINED` | 5-stage Jiang | Same as TRANSVERSE (transverse mechanism dominant) |
| Any other | 5-stage Jiang | Fallback to TRANSVERSE model |

The `loading_type` parameter can also be passed directly to `CoupledLooseningAnalyzer(loading_type='axial')`.

### Complete Phase Enum

```python
class LooseningPhase(Enum):
    # ── Transverse (Junker) loading — Jiang 5-stage model ──
    STABLE          = "stable"           # F/F₀ > 0.90, Stage I latch open
    NON_ROTATIONAL  = "non_rotational"   # 0.75 < F/F₀ ≤ 0.90, Stage I latch open
    TRANSITION      = "transition"       # Stage I: F/F₀ ≤ 0.75; Stage II: F/F₀ > 0.55
    ROTATIONAL      = "rotational"       # Stage II latch; 0.20 < F/F₀ ≤ 0.55
    RUNAWAY         = "runaway"          # F/F₀ ≤ 0.20 or self_lock_lost

    # ── Axial loading — 3-stage axial model ──
    AXIAL_STAGE_I   = "axial_stage_i"   # rapid embedding drop; cycle ≤ n_stage_i
    AXIAL_STAGE_II  = "axial_stage_ii"  # slow fretting / creep decay
    AXIAL_STAGE_III = "axial_stage_iii" # failure: F/F₀ ≤ 0.40 or Miner D ≥ 0.80
```

### Stage colour mapping in BAS

| Phase | Colour | Hex (Catppuccin Mocha) |
|-------|--------|------------------------|
| STABLE | Green | `Theme.GREEN` |
| NON_ROTATIONAL | Blue | `Theme.BLUE` |
| TRANSITION | Yellow | `Theme.YELLOW` |
| ROTATIONAL | Peach | `Theme.PEACH` |
| RUNAWAY | Red | `Theme.RED` |
| AXIAL_STAGE_I | Teal | `Theme.TEAL` |
| AXIAL_STAGE_II | Mauve | `Theme.MAUVE` |
| AXIAL_STAGE_III | Red | `Theme.RED` |

---

## 4. Pai-Hess Slip Onset Condition (the 0.46 Factor)

> Pai, N.G. and Hess, D.P. — "Experimental study of loosening of threaded fasteners due to
> dynamic shear loads," *Journal of Sound and Vibration*, Vol. 253(3), pp. 585–602, **2002**.
>
> Pai, N.G. and Hess, D.P. — "Three-dimensional finite element analysis of threaded fastener
> loosening due to dynamic shear load," *Engineering Failure Analysis*, Vol. 9(4), pp. 383–402, **2002**.

### Key Finding

> "Bolt tension begins to loosen when the transverse load reaches approximately **46 to 66 percent**
> of the transverse load required to cause the bolt underhead bearing to slip completely."

This means **complete gross slip is not required** for loosening to initiate.
Localized partial slip (≈ 46% of full-slip force) is sufficient.

### Four Slip Mode Classification (Pai-Hess)

| Mode | Head slip | Thread slip | Loosening onset | Notes |
|------|-----------|-------------|-----------------|-------|
| 1 | Localized | Localized | ~46% of F_slip_full | Most common in service; conservative lower bound |
| 2 | Localized | Complete | ~50% | |
| 3 | Complete | Localized | ~55% | |
| 4 | Complete | Complete | ~66% | Classical Junker assumption (overly conservative) |

### Interpretation of `slip_onset_factor = 0.46`

```
F_slip_onset = slip_onset_factor × µ × N
```

- `0.46` → lower bound of Pai-Hess range; conservative (flags loosening earliest)
- `0.66` → upper bound (Mode 4, classical partial-slip)
- `1.00` → classical Coulomb / full-slip condition (Junker original)

**Caveat:** 0.46 is the reported lower bound, not a precise physical constant. It depends on thread geometry, preload level, and surface condition. Some subsequent papers cite "≈ 50%" as a rounded representative value.

---

## 5. Standards — Junker, DIN 65151, DIN 25201-4, ISO 16130

### Junker Test (SAE Paper 690055, 1969)

Original identification that **transverse vibration** is the most severe loading mode for bolt loosening. The mechanism: transverse force induces relative slip between nut/bolt bearing surfaces → eliminates friction torque → helix pitch torque drives nut rotation.

### DIN 65151 (Aerospace, superseded)

- Standardizes the Junker transverse vibration **test method**.
- Does **not** define multi-tier effectiveness letter classes (A/B/C/D/F) in its text.
- The single pass/fail threshold widely attributed to DIN 65151 in practice:
  **80% preload retention at 2,000 cycles** — but this number is more precisely from DIN 25201-4.

### DIN 25201-4 (2010, current German standard)

| Criterion | Value |
|-----------|-------|
| Pass threshold | ≥ **80% of initial preload** retained after 2,000 cycles |
| Reference calibration | Unsecured reference must self-loosen within **300 ± 100** cycles |
| Test frequency | **12.5 Hz** |
| Size transferability | Results are NOT transferable across bolt sizes |

### ISO 16130:2015 (Aerospace series)

| Zone | F/F₀ range | Assessment |
|------|-----------|------------|
| Good self-locking | **85%–100%** | Acceptable for safety-critical |
| Acceptable loss | **40%–85%** | Requires engineering judgment |
| Poor self-locking | **0%–40%** | Fails; redesign required |

> Source: Vibrationmaster (ISO 16130 summary).

**BAS implementation:** Warning fires at < 85% (ISO 16130 "good zone" boundary), not at 80%.
The 80% figure belongs to DIN 25201-4 and is mentioned in the warning text for reference.
Both thresholds are cited in `_check_self_lock()`.

**On letter effectiveness classes (A, B, C, D, F) in `locking_devices.json`:**
After thorough literature search, these letter grades are **not formally defined** in
DIN 65151, DIN 25201-4, or ISO 16130 as a multi-tier classification system.
They appear to be an industry/field-guide convention, not a standardized scheme.

---

## 6. Vingsbo-Söderberg Fretting Regimes

> Vingsbo, O. and Söderberg, S. — "On fretting maps," *Wear*, Vol. 126, pp. 131–147, **1988**.

| Regime | Slip amplitude (representative range) | Primary damage |
|--------|--------------------------------------|----------------|
| **Stick** | < 5–10 µm | Oxidation only; minimal wear; no fatigue crack |
| **Partial slip** | 5–70 µm | Fretting fatigue cracks; moderate wear; most fatigue-damaging |
| **Gross slip** | > 20–300 µm | Severe adhesive/abrasive wear; fatigue less dominant |

**Note on boundaries:** Transition amplitudes are NOT fixed. They depend on normal
load, material pair, frequency, and environment. For bolt thread contacts specifically,
the fretting-to-gross-slip transition is typically in the 10–50 µm range.

The BAS code maps these to: `stick` / `partial_slip` / `fretting` / `gross_slip`
(four names rather than three — `fretting` ≈ upper partial-slip/transition).

---

## 7. VDI 2230:2015 — Loosening-Relevant Content

VDI 2230 is a **design calculation** guideline, not a loosening classification standard.

| Parameter | Definition | Loosening relevance |
|-----------|------------|---------------------|
| Load ratio R | F_min / F_max in the cyclic bolt load | Determines if bolt sees fully alternating (R = -1), pulsating (R = 0), or asymmetric loading |
| Tightening factor α_A | Scatter multiplier for assembly friction (1.2–1.9) | Higher α_A → higher maximum preload requirement |
| Friction class A | µ_thread = 0.08–0.16 | Used for preload calculation |
| Friction class B | µ_thread = 0.12–0.20 | |
| Loosening proof | F_KR (min residual clamp) ≥ F_Kerf at all times | The VDI criterion: preload after all losses must remain positive and adequate |

---

## 8. BAS Stage Classification — Full Boundary Reference

### 8.1 Transverse / Junker model (5-stage, `loading_type='transverse'`)

Implemented as **Option C** (Jiang-faithful one-way latch). See `_classify_phase()`.

```
_stage_II_triggered starts False.
Fires True when cumulative_rotation_deg ≥ 0.5° (one-way, never resets in a run).

Stage I (latch = False):
  STABLE         if F/F₀ > 0.90
  NON_ROTATIONAL if F/F₀ > 0.75
  TRANSITION     if F/F₀ ≤ 0.75   ← heavy Stage I loss; Stage II imminent

Stage II (latch = True):
  TRANSITION     if F/F₀ > 0.55   ← early rotational loosening
  ROTATIONAL     if F/F₀ > 0.20   ← full Junker back-off
  RUNAWAY        if F/F₀ ≤ 0.20

Overrides (checked first):
  RUNAWAY if self_lock_lost AND torque_margin < 0.5
  RUNAWAY if F/F₀ ≤ 0.20

Expected animation: STABLE → NON_ROTATIONAL → TRANSITION → ROTATIONAL → RUNAWAY
```

### 8.2 Axial model (3-stage, `loading_type='axial'`)

Implemented in `_classify_phase_axial()`. See that method's docstring.

```
_axial_rapid_done starts False.
Fires True after n_stage_i_cycles (default 50) OR when 10-cycle rolling
loss rate drops below 0.1%/cycle (embedding plateau reached).

Stage III triggers first (overrides):
  AXIAL_STAGE_III if F/F₀ ≤ 0.40  (ISO 16130:2015 "poor" zone entry)
  AXIAL_STAGE_III if Miner's D ≥ 0.80  (fatigue crack initiation imminent)

Then:
  AXIAL_STAGE_I   if _axial_rapid_done is False
  AXIAL_STAGE_II  if _axial_rapid_done is True

Expected animation: AXIAL_STAGE_I → AXIAL_STAGE_II → AXIAL_STAGE_III
```

### 8.3 Combined loading (`loading_type='combined'`)

Uses 5-stage Junker model. Transverse mechanism dominates rotational risk.
`_stage_II_triggered` latch operates as in the transverse case.

### 8.4 Boundary table — all models

| Phase | F/F₀ condition | Secondary condition | Jiang | ISO 16130 | DIN 25201-4 |
|-------|---------------|---------------------|-------|-----------|-------------|
| STABLE | > 0.90 | Stage I latch open | rot < 0.5° | good zone | — |
| NON_ROTATIONAL | > 0.75 | Stage I latch open | rot < 0.5° | good zone | pass |
| TRANSITION | > 0.55 | either latch state | — | acceptable zone | pass |
| ROTATIONAL | > 0.20 | Stage II latch fired | rot ≥ 0.5° | acceptable zone | fail |
| RUNAWAY | ≤ 0.20 | — | — | poor zone | fail |
| AXIAL_STAGE_I | any | _axial_rapid_done = False | — | — | — |
| AXIAL_STAGE_II | > 0.40 | _axial_rapid_done = True | — | acceptable | pass |
| AXIAL_STAGE_III | ≤ 0.40 OR D ≥ 0.80 | — | — | poor zone | fail |
| Warning (85%) | < 0.85 | any | — | upper-zone bdry | — |
| Warning (80%) | < 0.80 | any | — | — | pass limit |

---

## 9. Implementation Notes

### Critical: rotation criteria

**DO NOT** gate `STABLE` or `NON_ROTATIONAL` on `cumulative_rotation_deg < X°`.
`cumulative_rotation_deg` is monotonically increasing and will exceed 0.5° within a few
hundred cycles even for a healthy joint. Use only the one-way latch `_stage_II_triggered`.

### Critical: axial Stage III threshold

The 0.40 threshold (`preload_ratio ≤ 0.40 → AXIAL_STAGE_III`) is the ISO 16130:2015
"poor self-locking" zone entry. It is NOT the same as the RUNAWAY 0.20 threshold used
in the Junker model. Axial fatigue failure is typically flagged earlier.

### `n_stage_i_cycles` parameter

Default 50. This is not a universal physical constant — it is calibrated to the Jiang
(2003) experimental observation that rapid initial drop occurs in "first 5–50 cycles"
under transverse loading. For axial loading the correct value depends on the specific
loading amplitude and bolt geometry. Override via `n_stage_i_cycles=` kwarg.

---

## 10. Key References (Chronological)

| Year | Author(s) | Title / Source | Key contribution |
|------|-----------|---------------|-----------------|
| 1969 | Junker | SAE Paper 690055 | Transverse vibration as primary loosening mechanism; helix torque balance |
| 1988 | Vingsbo & Söderberg | *Wear* 126, 131–147 | Fretting map: stick / partial slip / gross slip regimes |
| 2002 | Pai & Hess | *J. Sound Vib.* 253(3), 585–602 | Slip onset at 46–66% of full-slip force; four slip modes |
| 2002 | Pai & Hess | *Eng. Fail. Anal.* 9(4), 383–402 | FEA confirmation of partial-slip loosening onset |
| 2003 | Jiang, Zhang, Lee | *J. Mech. Des.* 125(3), 518–526 | Stage I early-stage loosening; micro-slip mechanism |
| 2004 | Zhang & Jiang | *J. Mech. Des.* 126(6), 1062–1064 | Experimental validation; 0.5° rotation = Stage I/II boundary |
| 2007 | Jiang et al. | *J. Mech. Des.* 129(2), 218–226 | FEA of Stage II; helix coupling in 3D |
| 2010 | — | DIN 25201-4 | 80% retention at 2,000 cycles; reference calibration method |
| 2015 | — | ISO 16130:2015 | Aerospace Junker test; 85%/40% zone boundaries |
| 2019 | Gong, Liu, Ding | *Proc. IMechE Part C*, 233(16) | Critical loosening condition; comparison of criteria |
| 2021 | Wang et al. | *Eng. Fail. Anal.* | Three-stage criterion under random vibration |
| 2021 | — | *Chin. J. Mech. Eng.* | Competitive failure — bolt loosening vs. fatigue; 3-stage axial model |
| 2024 | — | *Eng. Fail. Anal.* (Su-N curve) | F/F₀ = 0.95 as loosening onset in fatigue context |

---

*End of document.*
