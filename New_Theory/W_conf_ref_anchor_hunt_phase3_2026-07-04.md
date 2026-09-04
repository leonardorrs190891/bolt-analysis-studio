# Phase-3 anchor hunt for `W_conf_ref` (pressure-conformation energy scale) — DEEP pass

**Task:** go deeper than the prior bounded hunt
(`New_Theory/W_conf_ref_provenance_hunt_2026-07-04.md`) and decide, concretely,
whether **Path A** (cross-rig over-torqued loosening curve), **Path B** (a citable
Fouvry steel energy-capacity number), or **Path C** (honest null) can anchor
`W_conf_ref` (canonical fit = **7671 J**, `n=2`, `p_ref=5e8 Pa`, effective driver).
**Date:** 2026-07-04 · READ-ONLY.

---

## 1. VERDICT

**Path C — honest null.** No anchorable data exists in either the digitized library
(Path A) or citable literature (Path B). This *confirms and strengthens* the prior
hunt's null, but with two concrete additions the prior pass never produced: (1) Path A
is now operationalized and closed — the exact candidate curves were identified and
shown to fail identifiability, with the single best "honorable mention" named; (2) Path
B now has a concrete citable steel energy number, but it anchors the **wrong quantity**
(`K_archard`, not `W_conf_ref`).

**One-line strongest finding:** the closest thing to a cross-rig conformation signal is
the **Lu 2024 M8 torque sweep** (`lu2024_M8_fig20_T28Nm.csv`: F0=15 kN ≈ 71 % proof
decelerates and flattens toward F/F0 ≈ 0.23, while `lu2024_M8_fig20_T4Nm.csv`: F0=2.1 kN
collapses to ≈ 0.04) — a genuine preload→arrest *trend*, but it **cannot isolate**
`W_conf_ref` (confounds, wrong pressure regime, wrong pair, only ~100 cycles).

**Concern:** `W_conf_ref` remains one rung *below* `C_creep` on the provenance ladder
(`C_creep` has one disjoint-IC independent measurement; `W_conf_ref` has none), and the
frozen transfer harness cannot even *excite* the conformation gate on any library case
except the âncora interna sobretorque itself — see §5 (the `A_contact=100 mm²` artifact).

---

## 2. Path A — cross-rig over-torqued plateau curve (the tractable path, now closed)

### 2.1 What "excites conformation" means numerically (the key mechanical fact)

In the frozen Phase-1 harness (`New_Theory/library_common.py::geometry_for`),
**`A_contact = 100 mm² = 1e-4 m²` is a FIXED default for every bolt size** (never
scaled with `d`), and `p_ref_conform = 5e8 Pa` is a fixed `JointMaterial` constant.
Therefore the conformation excitation term reduces to:

```
p / p_ref = (F0 / 1e-4) / 5e8  =  F0[N] / 50000  =  F0 / 50 kN
increment ∝ (p/p_ref)^n = (F0/50kN)^2      (n = 2)
```

So conformation is driven **purely by absolute preload F0 relative to 50 kN** (the âncora interna
nominal). Verified against the canonical `shared` block of `joint_calibrations.json`:

| âncora interna condition | F0 | p/p_ref = F0/50 kN | (p/p_ref)² | conformation |
|---|---:|---:|---:|---|
| nova / reusada / reaperto | 50 kN | 1.0 | 1.0 | inert (baseline) |
| **sobretorque** | **120 kN** | **2.4** | **5.76** | **strongly excited** |

The sobretorque (120 kN on an M16 10.9, ≈ 90 % proof / ≈ 80 % yield) is the **only**
high-pressure condition. To find a cross-rig anchor, a library curve must reach a
*comparable* excitation (F0 well above 50 kN, or a genuinely high absolute contact
pressure ≈ 1.2 GPa) **and** show the diagnostic settle→plateau→slow-decline shape
**and** be a case where the no-conformation model *under-predicts* the plateau (the
sobretorque signature: model grinds to 0.16 while data holds ~0.60).

### 2.2 Every transverse library case, scored (F0, excitation, % proof, shape)

Preloads from apparatus notes / `DIGITIZED_CASES`; proof loads from A_s × proof stress
(8.8 ≈ 580 MPa, 10.9 ≈ 830 MPa).

| Source / CSV stem | Bolt | F0 | p/p_ref (harness) | % proof | Curve shape | Verdict |
|---|---|---:|---:|---:|---|---|
| `liu2025_M16_amp0p25` | M16 8.8 | 60 kN | 1.2 | 66 % | slow decline → 0.675 (plateau-ish) | pressure only 1.2× nominal; plateau is **low-amplitude** (same bolt at ≥0.4 mm collapses to 0.33) — not pressure-conformation |
| `liu2025_M16_amp0p3` | M16 8.8 | 60 kN | 1.2 | 66 % | → 0.683 | same |
| `bauer2024_M12_fig8_test1..3` | M12×1.5 8.8 | 50 kN | 1.0 | **98 %** | 3-stage slow→accelerate→**collapse** | highest % proof in library, but **collapses** (opposite of arrest) |
| `bauer2024_M8_fig6_rep1..6` | M8 8.8 | 20 kN | 0.4 | **94 %** | quasi-linear **collapse** to ~0, <1000 cyc | near-proof but collapses; low absolute pressure (small bolt) |
| `demir2024_amp0p3_F17p6_lk19p8` | M8 8.8 | 17.6 kN | 0.35 | 83 % | ~linear decay → 0.549 (200 cyc) | high % proof, but short test, no plateau, low absolute pressure |
| `lu2024_M8_fig20_T28Nm` | M8 8.8 | 15 kN | 0.3 | 71 % | fast settle → **decelerating** → ~0.23 flattening | **best trend** (see §2.3) — but pressure below p_ref, confounded |
| `lu2024_M8_fig20_T4Nm` | M8 8.8 | 2.1 kN | 0.04 | 10 % | **collapse** to 0.04 | the low-preload contrast in the sweep |
| `yang2019_M10_amp0p4_5Hz` | M10 10.9 | 26 kN | 0.53 | 54 % | decline to ~0.70 | moderate everything; not high pressure |
| `rousseau2025_steel_t14` | M12 8.8 | 10.3 kN | 0.21 | 21 % | plateau → 0.903 | plateau is **member-stiffness** (thick grip), LOW preload |
| `rousseau2025_steel_t10` | M12 8.8 | 10.3 kN | 0.21 | 21 % | collapse → 0.088 | low pressure |
| `karlsen2022_M30_HV_run*` | M30 10.9 | 312–373 kN | 6.2–7.5 † | 70 % yield | **catastrophic collapse, no plateau** (note line 47) | see §2.4 — harness artifact + collapse |
| `karlsen2022_M42_HV_run*` | M42 10.9 | 660–720 kN | 13–14 † | 70 % yield | catastrophic collapse | same |
| `karlsen2022_*_vibralock_*` | M30/M42 | 351–720 kN | 7–14 † | 70 % yield | near-flat 3–10 % loss | flat is a **locking device** (wedge-cam nut), not conformation |
| `yang2021_*` | M8 8.8 | 14.1 kN | 0.28 | 66 % | composite (axial+shear), collapse/fracture | transverse slip confounded by simultaneous axial load |
| `liu2022_fig*` (retightening) | M12 8.8 | 20–28 kN | 0.4–0.56 | ~50 % | reaperto family | moderate pressure; damage/retighten study |

† Karlsen p/p_ref is a **harness artifact**: with `A_contact` fixed at 100 mm² for a
30–42 mm bolt, the model computes an absurd 1.6–3 GPa "nominal" pressure. With the
*real* M30/M42 bearing-annulus area (≈ 1600 / 3200 mm²), contact pressure at 350 / 690
kN is only ≈ 0.22 GPa ≈ **0.4× p_ref** — LOW. Either reading kills Karlsen as a
conformation test: harness-artifact-high (curves collapse → would *falsify* a universal
conformation) or physically-low (gate inert).

### 2.3 The one honorable mention — Lu 2024 Fig 20 torque sweep

`Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/lu2024_M8_fig20_T{4,10,16,22,28}Nm.csv`
is the **only controlled preload/torque sweep at fixed transverse amplitude** in the
library. The shape trend is real and conformation-like:

- **T28Nm (F0 = 15 kN, 71 % proof):** 1.00 → 0.62 (cycle 2, fast settle) → decelerates,
  slope flattening over the last decade (0.266 → 0.253 → 0.240 → 0.233 → 0.230, cycles
  68→100). A settle→arrest shape.
- **T4Nm (F0 = 2.1 kN, 10 % proof):** 1.00 → 0.04 catastrophic collapse by cycle 100.

Higher preload ⇒ more arrest — the qualitative *direction* of pressure-conformation.

**Why it still cannot anchor `W_conf_ref` (four independent reasons):**
1. **Confounded with ordinary preload-slip dependence.** In disp-mode `slip = max(0, δ −
   F_slip/k_tr)`, so higher F0 already gives less slip → slower loss *without any
   conformation*. Lu's T28-vs-T4 gap is exactly what the plain model predicts; nothing
   forces a conformation term. (Contrast the âncora interna sobretorque, where the plain model
   *under*-predicts the plateau — that under-prediction is the only clean conformation
   fingerprint, and no Lu curve shows it.)
2. **Wrong pressure regime for the frozen gate.** F0=15 kN → p/p_ref = 0.3 → the
   `n=2` gate is essentially inert; you would have to re-scale `p_ref` to the M8 rig to
   make it fire, at which point the fitted `W_conf_ref` is rig-specific by construction.
3. **Different tribo-pair.** Soft **nickel-steel** members with a "massive first-cycle
   drop" — not the âncora interna bolt/washer/member steel pair.
4. **Too short.** ~100 cycles, no long slow-decline tail to separate creep from a
   conformation plateau.

A `W_conf_ref` "isolation fit" on Lu Fig 20 is *possible* but its identifiability is
poor (indistinguishable from preload-slip + slip-onset) and its value would be
M8-nickel-steel-rig-specific — a per-pair number with a large error bar, not an anchor
of the âncora interna 7671 J.

### 2.4 Path-A conclusion

**No library curve combines (high absolute contact pressure ≈ âncora interna sobretorque) + (a
sustained settle→plateau→slow-decline) + (no-conformation under-prediction).** The
cases split cleanly:
- **High % proof → collapse** (Bauer M8 94 %, Bauer M12×1.5 98 %, Demir M8 83 %): the
  arrest never happens, so `W_conf_ref` is inert/unidentifiable there.
- **Plateau shape → low pressure, other cause** (Liu 2025 0.25 mm = low amplitude;
  Rousseau t14 = member stiffness; Lu 0.25 mm = below slip onset).
- **Highest harness excitation (Karlsen) → artifact + collapse/locking-flat.**

This is itself an informative cross-rig finding (parallel to §4.8): a high preload
*fraction* on another rig does **not** reproduce the âncora interna sobretorque plateau — the
plateau appears tied to the âncora interna rig's specific small bearing contact (100 mm² → ~1.2
GPa at 120 kN) and pair. Consistent with "forms transfer, constants are per pair/rig."

---

## 3. Path B — a citable Fouvry steel energy number

### 3.1 What was found (concrete, citable)

| Quantity | Value | Steel / conditions | Source |
|---|---|---|---|
| **Energy wear rate/coefficient α** (wear *volume* per dissipated energy) | **4.23×10⁻⁵ mm³/J** | 52100 bearing steel, sphere-on-flat, reference contact size L_C=L_T=5 mm | Fouvry group, "Modeling contact size effect on fretting wear" (hal-03453455) — via web search excerpt |
| Energy wear coefficient α | 4×10⁻⁴ mm³/J | Ti-6Al-4V, 300–400 MPa contact pressure | same search corpus (Ti alloy) |
| **"Wear energy capacity" χ** = max accumulated dissipated energy **density** before contact failure; "a characteristic variable for each surface treatment" | **concept only — no numeric steel value** | steel-steel | Fouvry, Paulin, Liskiewicz, *Tribology International* 2007, PII **S0301679X07000436** |
| "Friction energy capacity" / "effective energy density threshold" | numeric values exist for **coatings** (TiN, TiC, DLC), not bare steel | coatings | Fouvry 2004, PII S0301679X0400115X |

### 3.2 Why none of these anchors `W_conf_ref`

- **α = 4.23×10⁻⁵ mm³/J is the wrong quantity.** It is a wear-*volume* rate — the
  energy analog of **`K_archard`**, not of `W_conf_ref`. (It could genuinely anchor
  `K_archard` for a steel pair, a separate provenance win, but the doc's §5.1 already
  lists `K_archard` provenance as "literature".) It says nothing about a slip-*arrest*
  energy scale.
- **χ is the conceptually closest quantity but (a) has no citable steel number** (only
  coatings), and **(b) targets the wrong endpoint** — Fouvry χ is energy-to-wear-failure
  (contact *destruction*); `W_conf_ref` is energy-to-slip-arrest (contact *lock-up /
  conformation*). These are opposite tribological endpoints, so even a perfect χ number
  would be an order-of-magnitude plausibility band, not an anchor.
- **Units mismatch.** χ is an energy *density* (J/mm²); `W_conf_ref` is a
  *pressure-weighted total* energy (J) at the whole bearing contact.

### 3.3 Conversion sketch (if a steel χ ever surfaces) — explicit assumptions

To compare a hypothetical steel χ [J/mm²] to `W_conf_ref` [J], one would:
1. Take the âncora interna bearing contact area A ≈ 100 mm² (`A_contact` = 1e-4 m², the harness
   value) — **assumption 1**: the model's nominal A_contact is the real conforming area.
2. Multiply: total energy ≈ χ · A → J — **assumption 2**: uniform dissipation over A.
3. Unwind the pressure weighting: `W_conf_ref` accumulates `(p/p_ref)^n · dW_slip_raw`;
   at the sobretorque p ≈ 2.4·p_ref, n=2, the weight ≈ 5.76 — **assumption 3**: divide
   the raw-work-to-half-conformation by ~5.76 to reach the density-comparable raw energy.
4. Compare to the **internal** (non-anchor) order-of-magnitude from the prior hunt: raw
   areal density ≈ **~20 J/mm²** at half-conformation. This is computed from the *same*
   âncora interna data+geometry that produced the fit — it is an internal consistency check, **not**
   a literature match, and must never be presented as an anchor.

**Path-B conclusion:** framework citable, a concrete steel energy-wear *rate* citable
(α = 4.23×10⁻⁵ mm³/J), but the `W_conf_ref` analog (steel χ energy *capacity/density*,
same endpoint) is **not** citable and would be endpoint-mismatched anyway. Not an anchor.

---

## 4. Path C — the honest null + the exact experiment that WOULD anchor it

Neither A nor B yields an anchor. The dedicated Phase-3 experiment, built in the mold of
`anchor_creep.py` (isolate the mechanism, fit the one constant, re-center the prior,
pre-register that a disagreement is the expected informative outcome):

- **Rig:** a dedicated fretting/oscillating-sliding rig (or the âncora interna Junker rig fitted
  with a **small high-pressure bearing coupon**) able to hold a **known high contact
  pressure ≈ 1.2 GPa** (matching the sobretorque) and measure friction force and slip
  per cycle continuously (a friction-loop / dissipated-energy instrument).
- **Tribo-pair (the anchor's whole point — same pair as âncora interna, cross-material allowed like
  the C_creep 304SS anchor):** the âncora interna bolt-head-bearing / washer / member steel, same
  materials and same surface roughness class (Rz). If unavailable, a documented cross-
  pair (structural/bolt steel) — a disagreeing cross-pair result is still valid.
- **What to measure:** the **accumulated frictional dissipated energy**
  `Σ ∮ F_fric · d(slip)` versus the **degree of contact conformation / slip-arrest** —
  i.e. track the per-cycle slip-driven preload-loss rate and locate the accumulated
  (raw) slip work at which that rate is **halved**. Sweep contact pressure across ≥3
  levels so the pressure exponent **n** can be measured independently (it is currently
  *fixed* at 2 by choice, not measured).
- **Reduction to `W_conf_ref`:** the accumulated pressure-weighted slip work at the
  half-loss-rate point **is** `W_conf_ref` directly. Measure at a pressure p, divide by
  area and unwind `(p/p_ref)^n` with the measured n to place it on the model's scale;
  compare to the canonical **7671 J**.
- **Pre-registration:** a disagreement with 7671 J (as `C_creep`'s ~11.7× disjoint-IC
  disagreement, §4.7) is the **expected, informative** outcome — it quantifies per-pair
  transfer, it does **not** falsify the conformation *form* (the A/B in §4.9 already
  sustains the form).

Until then, `MODEL_LEGITIMACY.md` §4.9 strand-3 / §5.1 already record the honest status
correctly: **"framework identified, per-pair by that framework's own definition, but
numerically unanchored — Phase 3 open."** This deep pass confirms that wording and adds
the Path-A closure and the α number above; **no doc change is required** unless you want
to cite the Lu Fig 20 honorable mention or the α=4.23e-5 mm³/J figure.

---

## 5. What was searched (auditable)

**Prior work re-read first (not repeated):** `New_Theory/W_conf_ref_provenance_hunt_2026-07-04.md`;
`MODEL_LEGITIMACY.md` §4.5 (sobretorque falsification), §4.7 (C_creep anchor), §4.8
(transfer), §4.9 all four strands + §5.1 provenance table; spec
`docs/superpowers/specs/2026-07-04-pressure-conformation-design.md` (§4 form, §6
constants, §9 A/B); `New_Theory/anchor_creep.py` (the anchor template).

**Path-A library sweep (the new work):**
- `New_Theory/transfer_validation.py` (46-curve case list, selection rule) +
  `New_Theory/library_common.py` (found the `A_contact=100 mm²` fixed default and
  `p_ref=5e8` → the `p/p_ref = F0/50kN` reduction).
- `joint_calibrations.json` `shared` block (F0 per condition, W_conf_ref=7671,
  n=2, p_ref=5e8, effective driver).
- All 16 `curve_library/apparatus_notes/*.md` (esp. `MSD_BLOCK_COVERAGE.md`,
  `karlsen2022`, `liu2025`, `bauer2024`, `demir2024`, `lu2024`, `rousseau2025`,
  `yang2019`, `liu2022`, `wang2020`, `li2022_*`, `yang2021`, `cja2022`) — read preloads,
  torques, curve shapes, plateau notes.
- Direct CSV inspection: `lu2024_M8_fig20_T4Nm.csv`, `lu2024_M8_fig20_T28Nm.csv`,
  `liu2025_M16_amp0p25.csv`, `liu2025_M16_amp0p3.csv`,
  `demir2024_amp0p3_F17p6_lk19p8.csv`.
- Grepped `apparatus_notes/` for: plateau, over-torque, over-tighten, preload fraction,
  % yield, % proof, proof load, high preload, contact pressure.

**Path-B web (bounded, 4 calls):**
- WebSearch: Fouvry "wear energy capacity" fretting steel critical dissipated energy
  density J/mm3 → concept confirmed, PII S0301679X07000436; no steel numeric χ.
- WebSearch: fretting steel energy wear coefficient α mm3/J 52100/34CrNiMo6 → **α =
  4.23×10⁻⁵ mm³/J (52100 steel)**, 4×10⁻⁴ mm³/J (Ti-6Al-4V).
- WebSearch: "friction/wear energy capacity" steel J/mm2 Fouvry numeric → capacity
  values exist for coatings only, not bare steel.
- WebFetch hal-03453455 (Fouvry contact-size paper) → blocked (Anubis 403); value
  above is from the search excerpt, not the full text.

**Sources (web):**
- https://www.sciencedirect.com/science/article/abs/pii/S0301679X07000436 (Fouvry 2007, wear energy capacity χ)
- https://hal.science/hal-03453455/document (Fouvry, contact size effect; α = 4.23e-5 mm³/J for 52100 — from excerpt)
- https://www.sciencedirect.com/science/article/abs/pii/S0301679X0400115X (Fouvry 2004, friction energy capacity, coatings)
- https://link.springer.com/article/10.1007/s11249-013-0133-y (dissipated-energy wear prediction)

**No number or citation in this report is fabricated. "No anchorable data" is the
result.**
