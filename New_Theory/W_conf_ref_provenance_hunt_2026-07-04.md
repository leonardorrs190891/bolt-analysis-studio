# Provenance hunt for `W_conf_ref` (pressure-conformation energy scale)

**Task:** does an independent anchor exist for `W_conf_ref` (~10⁴ J conformation-energy
scale), analogous to the C_creep anchor (`MODEL_LEGITIMACY.md` §4.7)?
**Date:** 2026-07-04 · READ-ONLY provenance research.

---

## 1. VERDICT

**NO direct anchor found — `W_conf_ref` is a fitted per-pair/rig constant, exactly like
C_creep.** Bounds-plausibility is only *weak*: the correct literature framework exists
(Fouvry **wear/friction energy capacity** — a critical *accumulated dissipated energy
density* to reach a tribological endpoint), and it independently reproduces the C_creep
lesson ("**it is a characteristic variable for each surface treatment**" → per-pair, not
universal). But it does **not** anchor the number, for three reasons: (a) it targets the
**opposite** tribological endpoint (contact *failure* / wear-depth, not slip-*arrest* /
lock-up); (b) it is an **energy density** (J/mm²), whereas `W_conf_ref` is a
*pressure-weighted total energy* (J) at the whole bearing contact; (c) **no clean numeric
J/mm² value for steel** could be obtained from the local library or bounded web search to
even pin the order of magnitude.

This matches the honest C_creep outcome almost verbatim: **forms/frameworks transfer,
constants are per tribological pair.** `W_conf_ref`'s provenance is genuine Phase-3 work
and, on today's evidence, will remain a fitted-per-pair constant (its magnitude is
*internally* sensible against the âncora interna test's own dissipation budget, but that is not an
independent anchor).

---

## 2. WHAT WAS SEARCHED (auditable)

### Precedent studied first (as instructed)
- `New_Theory/MODEL_LEGITIMACY.md` §4.7 (C_creep static-creep anchor), §5.1 (per-parameter
  provenance table), §4.9 + changelog (the conformation A/B that produced `W_conf_ref`).
- `docs/superpowers/specs/2026-07-04-pressure-conformation-design.md` §4, §6 (the constant's
  definition, form, and the explicit "literature anchor deferred to Phase-3" note).

**How C_creep was anchored (the template):** an *independent* experiment isolating the
mechanism (li2022marstruc static contact-creep relaxation, 304SS, no vibration → wear/
loosening structurally inert) was fitted for C_creep alone. The anchored value
(9.9e-13) **disagreed with the âncora interna dynamic fit (1.2e-11) by ~11.7× with disjoint CIs** →
honest conclusion: C_creep is **per tribological pair**; the âncora interna value is estimate-on-curve.
The analogous hunt for `W_conf_ref` would need an independent experiment yielding a
conformation/shakedown *energy scale* for a clamped metallic contact.

### Local library (primary)
- `Models/CALIBRATION_AND_VALIDATION/curve_library/apparatus_notes/` — all 16 notes incl.
  `MSD_BLOCK_COVERAGE.md` (per-source MSD data matrix). Grepped for conform / running-in /
  asperity / shakedown / settle / plateau / lock-up / arrest.
- `Models/CALIBRATION_AND_VALIDATION/51_52_53_54_axial_fatiguewear_noload_energy.md`
  (Studies 51 Liu-2016, 52 Fan-2023, 53 Liu-2021, 54 İçmez-2025 energy-equilibrium).
- `Models/CALIBRATION_AND_VALIDATION/curve_library/DEEP_RESEARCH_REPORT{,_R2}.md`,
  `CALIBRATION_AND_VALIDATION_PLAN.md`.
- `BAS_V2_papers/README.md` (67-paper index, folders A–D).
- Repo-wide grep across all `*.md`: `Fouvry`, `energy density`, `J/mm`, `MJ/m`,
  `shakedown`, `energy wear coefficient`, `dissipated energy`, `accumulated…energy`,
  `running-in`, `conform`.
- Code: `src/.../numerical/wear_models.py` (Fouvry `EnergyBasedWearModel`),
  `Models/models/Part_X_Preload_Loss_Models.md` §54 (energy dissipation / Fouvry relation),
  `Models/models/Part_XI…`, `Models/new_advances/1_MODEL_COUPLING_STUDY.md`,
  `LOOSENING_MECHANISMS_QUANTITATIVE.md` §11 (fretting stages, slip index).

### Web (secondary, bounded — 3 searches + 1 OA-PDF fetch)
- WebSearch: "fretting wear energy approach Fouvry dissipated energy density threshold steel
  bolted joint J/mm2".
- WebSearch: "accumulated frictional energy to reach steady-state fretting shakedown clamped
  contact running-in energy self-loosening".
- WebSearch: `"wear energy capacity" OR "critical energy density" fretting steel value
  J/mm3 mm3/J energy wear coefficient numeric`.
- WebFetch: open-access CMC 2019 fretting-wear review PDF (techscience.cn) — checked for any
  numeric energy-capacity / threshold value (**none extractable**).
- (PubMed/Scholar MCP tools available but not used — biomedical-focused, irrelevant here.)

---

## 3. ENERGY-SCALE FIGURES FOUND (source · units · anchor or bound?)

| Concept found | Source | Units / value | Relation to `W_conf_ref` |
|---|---|---|---|
| **Fouvry "wear/friction energy capacity" χ** = *max accumulated dissipated energy density before contact failure*; "**a characteristic variable for each surface treatment**" | Fouvry, Paulin, Liskiewicz, *Tribology International* 2007, "Application of an energy wear approach to quantify fretting contact durability: introduction of a wear energy capacity concept" (ScienceDirect PII **S0301679X07000436**) | energy **density** (J/mm² or J/mm³); **no numeric steel value obtained** | **Closest concept, but does NOT anchor.** Different endpoint (failure vs. slip-arrest), different quantity (density vs. pressure-weighted total J), and no citable number. Independently **confirms "per-pair, not universal"** (= C_creep lesson). |
| **Fouvry energy-wear coefficient α_w** (V = α_w·ΣE_d) | `Part_X…md` §54.5 (cites Fouvry 2003, *Wear* 255:287, DOI 10.1016/S0043-1648(03)00117-0); `wear_models.py` `EnergyBasedWearModel` | steel/steel dry **1e-7–5e-7 mm³/J** (Part_X); **5e-15 m³/J** default (code) | Anchors **wear volume rate** (a `K_archard` analog), **not** a conformation-arrest energy. Wrong quantity. |
| **Fretting cumulative energy threshold `E_th`** (wear begins only after ΣE_d > E_th) | `wear_models.py` (`energy_threshold`, **default 0.0 = inert**); `1_MODEL_COUPLING_STUDY.md:650` | J (cumulative); **no independent value** | An energy scale for wear *onset* (incubation) — **opposite polarity** to conformation (arrest) and it's the model's own knob defaulting to 0. Not an anchor. |
| **Elastic/plastic shakedown reached in ~4 sliding reversals** | Web (shakedown lit.: mdpi.com/2079-4991/13/10/1584; ScienceDirect S0043164800005081) | **cycles**, not energy | Classical shakedown is stress/cycle-based and ~4 cycles — far faster than the model's ~75-cycle conformation. Different mechanism; **not** an energy anchor. |
| İçmez 2025 "energy-equilibrium" loosening model | Study 54 (DOI 10.56038/ejrnd.v5i1.693) | per-cycle W balance (no scale) | A per-cycle rotation energy balance; carries **no** accumulated conformation-energy scale. |
| Qualitative "asperities flatten → more conforming contact" / "run-in surfaces lose less" | Study 51 Liu-2016; `karlsen2022`, `sandia2021` apparatus notes | **no numbers** | Corroborates the *physical picture* of conformation/running-in; supplies **no energy figure**. |

**Order-of-magnitude sanity (INTERNAL, not an anchor — flagged honestly):** at sobretorque
raw slip work ≈ 4·μ·F₀·slip ≈ 4·0.15·1.2e5·5e-4 ≈ **~36 J/cycle**. With the pressure
weighting (p/p_ref)ⁿ ≈ 2.5² ≈ 6.25, half-conformation (`W_conf = W_conf_ref = 1.25e4 J`)
is reached at ≈ 2e3 J of *raw* work ≈ **~55 cycles**, consistent with the observed ~75-cycle
settle→plateau of TP6 (spec §1 diagnosis). Dividing by A_contact≈1e-4 m² gives a raw areal
density ≈ **~20 J/mm²** — dimensionally the same kind of quantity as Fouvry's χ and not
obviously implausible. **But this uses the same âncora interna data + model geometry that produced the
fit, so it is internal consistency, not an independent anchor**, and no literature χ value
was obtained to confirm/refute the 20 J/mm² magnitude.

---

## 4. RECOMMENDATION — how `MODEL_LEGITIMACY.md` should record the status

Record `W_conf_ref` honestly as **"fitted per-pair/rig constant; no independent anchor;
provenance = Phase-3, unresolved"**, explicitly parallel to C_creep (§4.7) but *weaker*
(C_creep at least has a disjoint-IC independent measurement; `W_conf_ref` has none). Suggested
wording for §4.9 (or its Phase-3 provenance note) and the §5.1 provenance table row:

1. **State the framework exists but does not anchor the number.** The literature home is
   Fouvry's **wear/friction energy capacity** (critical accumulated dissipated *energy
   density* before a contact endpoint; Fouvry et al., *Tribology Int.* 2007, PII
   S0301679X07000436). It **confirms** the per-pair property (χ is "a characteristic variable
   for each surface treatment") — i.e. the same "**forms transfer, constants don't**" verdict
   of §4.6–4.8/§8 — **but** targets a different endpoint (failure/wear-depth, not
   slip-arrest), is a density not a pressure-weighted total, and no numeric steel value could
   be sourced. So: **framework anchors the *concept and the per-pair status*, not the value.**

2. **Do not claim numeric consistency.** The ~20 J/mm² implied areal density is an
   *internal* order-of-magnitude check (same âncora interna data), not a literature match — label it as
   such; no uncited number should be presented as an anchor.

3. **§5.1 provenance table:** add `W_conf_ref` with Camada = tunável/físico-fenomenológico,
   Procedência HOJE = "ajustado à curva do sobretorque (1 rig, 1 condição); sem âncora
   independente", Procedência IDEAL = "capacidade de energia de atrito (Fouvry χ) medida
   **por par tribológico** num ensaio de fretting dedicado que isole o assentamento sob alta
   pressão de bearing". Same footing as the honest `c_D, k_dmg_*` row.

4. **Point the Phase-3 experiment (parallel to anchor_creep.py):** an independent
   fretting/shakedown test on the **same tribo-pair** that measures accumulated dissipated
   energy vs. contact conformation/lock-up (or reuses a high-pressure bearing coupon), then
   compare its energy-density scale (÷ area, unwinding the (p/p_ref)ⁿ weighting) to
   `W_conf_ref`. Pre-register that a **disagreement is the expected, informative outcome**
   (as C_creep's ~11.7× disagreement was) — it would quantify per-pair transfer, not falsify
   the *form*. Keep the caveat already in §4.9 ("`n`/`p_ref` fixed by choice, form
   phenomenological-sustained not proven"): the anchor hunt is about the **constant**, and it
   came up empty.

**Bottom line for the doc:** `W_conf_ref` sits *below* C_creep on the provenance ladder —
C_creep = "anchored, disagrees, therefore per-pair"; `W_conf_ref` = "framework identified,
per-pair by that framework's own definition, but **unanchored numerically**." Honest label:
**NO anchor; fitted-per-pair; Phase-3 open.**
