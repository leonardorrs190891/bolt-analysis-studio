# Loosening Slip-Regime Gate — Design (2026-07-06)

**Goal:** Make rotational self-loosening respect the partial/gross-slip regime —
suppressed in partial slip (stick), active in gross slip — so the plateau cases
stop over-loosening. Opt-in, backward-compat, zero-refit (frozen calibration
preserved). This is the F_amp↔δ_amp coupling (roadmap #4) in gate form.

**Status:** design approved 2026-07-06 (brainstorm). Canonical re-fit OUT of
scope (a later gated decision), canonical `shared` block never written.

---

## 1. Motivation — why this, and why now

The k_tr fix (`spec 2026-07-05-slip-regime-ktr-fix`) corrected the **displacement**
slip regime (`resolve_transverse_slip`, bending `k_tr` → realistic `δ_t`), but
**failed** to fix the plateau over-prediction (`MODEL_LEGITIMACY.md` §4.8: realized
plateau→plateaus stayed 14%, `final_pred` +0.006 median). The k_tr addendum
diagnosed it as "embedding+creep erode F₀ across `δ_t` → runaway." A 2026-07-06
**per-mechanism decomposition** of the plateau case (liu2025 M16 amp0.25, data
plateau 0.68) shows that diagnosis was **partly mis-attributed**:

| cyc | F₀/F₀ᵢ | disp-slip | emb % | creep % | wear % | **loosening %** |
|---:|---:|---:|---:|---:|---:|---:|
| 1 000 | 0.784 | 0 | 14.4 | 5.6 | 0 | **1.7** |
| 5 000 | 0.690 | 0 | 14.4 | 7.3 | 0 | **9.2** |
| 10 000 | 0.572 | **0** | 14.4 | 8.0 | 0 | **20.4** |
| 20 000 | 0.199 | 135 µm | 14.4 | 8.4 | 6.3 | **51.0** |

- **Embedding already saturates** (state-based asymptote `k_emb_scale·emb_depth`,
  ~14.4%, done by cyc 1000) and **creep is slow-log** (∝F₀·Δln t, plateaus ~8.5%).
  Together ~23% → they would leave F₀ ≈ 0.77. **They are not the runaway.**
- **Rotational loosening is the dominant eroder** — and it grows to 20% **while
  the displacement slip is still 0** (partial). It is what actually crosses F₀
  through the `δ_t` threshold and triggers the gross-slip runaway.

**Root cause.** `RotationalLooseningLoss.rate` keys off a transverse **force**
criterion — `Phi_tr_active = 0.01 if F_tr < F_slip else tr_loose_gain·Phi_tr_correction`
with `F_tr = F_amp·sin θ` — plus `T_loose > T_resist`. In disp-mode `F_amp =
F_AMP_RATIO·F₀ = 0.4·F₀ ≫ F_slip = 0.46·μ·F₀ = 0.069·F₀`, so loosening fires
**regardless of the displacement-slip regime** the k_tr fix corrected. The k_tr
fix only reached `resolve_transverse_slip` (the **wear** path, minor: 6%);
loosening (dominant: 51%) bypassed it entirely.

**Physics.** Junker rotational self-loosening is a **ratcheting back-off that
requires gross slip** at the bearing/thread interface. Firing during stick /
partial slip is unphysical. Gating loosening by the actual gross-slip regime is
the physically-correct coupling.

---

## 2. The mechanism (Approach 1 — chosen)

A **gross-slip-fraction gate** on rotational loosening:

```
g_slip = slip_amp / (slip_amp + δ_t),   δ_t = F_slip / k_tr
```

Since `resolve_transverse_slip` returns `slip_amp = max(0, δ − δ_t)`, this equals
`(δ − δ_t)/δ` = **the fraction of the imposed stroke that is gross sliding**:

- partial slip (`δ < δ_t`) → `slip_amp = 0` → **g = 0** (loosening off);
- just past threshold → ramps in smoothly;
- deep gross (`δ ≫ δ_t`) → **g → 1** (loosening = current, calibration intact).

**Zero new constants** — it uses `slip_amp` (already resolved), `F_slip`, and
`k_tr` (both computable in `rate` from `state`/`mat`/`geom`), reconstructing the
gross-slip fraction without needing `delta_amp` passed in. This matters: the whole
program (§4.9/§5.1) is about *reducing* free parameters, not adding knobs. It is
a **gate** (0→1), not a re-scaling of the loosening driving force, so the frozen
gross-slip calibration (`tr_loose_gain`, `Phi_tr_correction`, `k_loose_scale_*`)
is **unchanged when firing** → valid as a **zero-refit** transfer experiment.

**Approaches considered and rejected (this cycle):**
- **Hill gate on `slip_amp` with a reference `s_ref`** — more shape control,
  mirrors `slip_onset_gate`, but **adds a constant** (`s_ref` + sharpness) with no
  independent provenance. Rejected: knob-avoidance.
- **Physical transmitted-force coupling** `F_tr = min(k_tr·δ, μ·F₀)` — the "true"
  F_amp↔δ_amp coupling and the eventual physical endpoint, but it **changes the
  gross-slip loosening magnitude** (`0.4·F₀` → `μ·F₀`) → **breaks the frozen
  calibration** → forces a canonical re-fit. Deferred to a later re-fit cycle
  (same gating as the k_tr fix). Extensible via the mode string (`"transmitted_force"`).

---

## 3. Engine change (`dynamic_stiffness_analyzer.py`)

**3.1 New `JointMaterial` field** (near `k_tr_mode`/`c_bend`, ~line 164):
```python
# Acoplamento loosening<->regime de slip (spec 2026-07-06): "off" (default,
# loosening usa o criterio de forca atual = backward-compat) | "gross_fraction"
# (loosening gateado pela fracao de gross-slip do curso g = slip/(slip+delta_t)).
# So faz sentido com k_tr_mode="bending" (delta_t realista). Force-mode => 1.0.
loosening_slip_coupling: str = "off"
```

**3.2 New module function** (near `k_tr_transverse`, ~line 400):
```python
def loosening_slip_gate(state: SlowState, geom: JointGeometry,
                        mat: JointMaterial, slip_amp: Optional[float]) -> float:
    """Gate da fracao de gross-slip para o loosening rotacional (spec 2026-07-06).
    Junker precisa de GROSS slip (ratcheting); em partial slip (stick) o
    backing-off e suprimido. g = slip/(slip+delta_t) = (delta-delta_t)/delta =
    fracao de gross-slip do curso, delta_t = F_slip/k_tr. "off" ou slip_amp None
    (force-mode) => 1.0 (backward-compat)."""
    if mat.loosening_slip_coupling == "off" or slip_amp is None:
        return 1.0
    if mat.loosening_slip_coupling == "gross_fraction":
        delta_t = F_slip_transverse(state, mat) / max(k_tr_transverse(geom, mat), 1e-12)
        return slip_amp / max(slip_amp + delta_t, 1e-12)
    return 1.0
```

**3.3 Apply in `RotationalLooseningLoss.rate`** (the `d_theta` line, ~line 765) —
multiply by the new gate alongside the existing two:
```python
g_slip_regime = loosening_slip_gate(state, geom, mat, slip_amp_override)
d_theta = (g * conformation_gate(state, mat) * g_slip_regime * k_scale
           * slip_fraction * (T_loose - T_resist) / max(k_torsional, 1.0))
```
`rate` already receives `slip_amp_override` and `geom` — **no signature change**.

**3.4 Conservation.** `dF_0 = −k_b·lead·d_theta` and `dE = T_resist·d_theta` both
scale by `g_slip_regime`, so the preload loss and its dissipation reduce
**proportionally** — energy accounting stays consistent (identical pattern to the
existing `slip_onset_gate`/`conformation_gate` on `d_theta`; NOT the
"dF_0-yes-dE-no" wear-amplification case).

---

## 4. Activation / backward-compatibility

- Default `loosening_slip_coupling="off"` → `g≡1` → every existing run/fit
  **bit-identical**. Hard gate.
- **Force-mode** (`slip_amp_override is None`, servohydraulic legacy) → `g=1` even
  when the coupling is on: there is no disp-regime to gate, so loosening keeps the
  imposed `F_amp`.
- The gate is only *meaningful* with a realistic `δ_t`, i.e. `k_tr_mode="bending"`
  (with `axial_frac`, `δ_t≈0` → `g≈1` always → ~no-op). The validation flag sets
  both; the two remain independently togglable fields for testing.
- Honors `model._v2_tuner_overrides` (string field passes the type-aware filter,
  like `conform_driver`).

---

## 5. Validation — pre-registered, AS IS

`transfer_validation.py --loosen-coupled` sets `loosening_slip_coupling=
"gross_fraction"` **and** `k_tr_mode="bending"`; separate `transfer_*_loosen.*`
artifacts; mirrors the `--ktr-bending`/`--damage-trigger` flag pattern.

**Honest tension pre-registered:** the gate makes the slip-regime *consequential*
(partial→no loosening→plateau; gross→loosening→collapse), so its accuracy is
**bounded by the `c_bend` regime accuracy** (Task 2: 77% collapse / 57% plateau
on the initial slip). We therefore expect plateaus to improve **and** some of the
~23% mis-classified collapses to regress. This is the honest coupling, not a bug.

**Frozen thresholds** (set before the run, recorded AS IS; calibrated against the
known baselines — k_tr-only realized plateau 14% / collapse→loosens 45%, Task 2
initial regime 57% plateau / 77% collapse; only **7 plateau** and **31 collapse**
cases, so plateau accuracy is quantized in 1/7≈14% steps):
- **Plateau fixed (primary):** realized plateau→plateaus (`final_data>0.55` cases
  with `final_pred>0.55`) **≥ 50%** (a real jump from 14%; passes at 4/7=57%,
  fails at 3/7=43%), AND median plateau `final_pred` improvement **≥ 0.2** vs the
  `axial_frac` baseline.
- **Collapse not destroyed (guard):** collapse→loosens (`final_data<0.30` cases
  with `final_pred<0.55`) **≥ 40%** — the k_tr-only baseline is already only 45%
  (genuine collapses are *under*-predicted by the frozen cross-rig constants,
  §4.8), so this guards against the gate driving it materially lower, not against
  a high bar.
- **Global MAE** reported AS IS (the point is the regime, not curve MAE; may not
  move much).

Verdict recorded vs these thresholds either way. The gate's ceiling is the
`c_bend` regime accuracy (Task 2), so plateaus improving **while** some
mis-classified collapses regress is the expected AS-IS shape — that outcome points
back to the Task 2 finding (single `c_bend` can't fully separate → better regime
separation / member-compliance is the next form), **not** to tuning this gate.

---

## 6. Testing (TDD)

`tests/test_loosening_slip_gate.py`:
- **backward-compat:** `loosening_slip_gate` returns exactly `1.0` when
  `coupling="off"` (default) — for any `slip_amp` including `None`.
- **force-mode:** `slip_amp=None` + `coupling="gross_fraction"` → `1.0`.
- **partial slip:** `slip_amp=0` + coupling on → `g=0` → loosening `dF_0≈0`
  (vs non-zero with coupling off, same state).
- **gross ramp:** `slip_amp>0` → `g∈(0,1)`; deep gross (`slip_amp≫δ_t`) → `g→1`
  → loosening `dF_0` ≈ the ungated value.
- **end-to-end money test:** a plateau-like disp case (small δ, high F₀) that
  **collapses** with the gate off **plateaus** with `k_tr_mode="bending"` +
  `coupling="gross_fraction"` (F₀ retained well above collapse).
- **backward-compat sweep:** the standing V2/calibration suite passes unchanged
  with default off.

---

## 7. Files

| File | Change |
|---|---|
| `src/.../numerical/dynamic_stiffness_analyzer.py` | `JointMaterial.loosening_slip_coupling` field; `loosening_slip_gate` function; apply in `RotationalLooseningLoss.rate` |
| `tests/test_loosening_slip_gate.py` | new (TDD) |
| `New_Theory/transfer_validation.py` | `--loosen-coupled` flag (sets coupling + bending); `_loosen` artifacts |
| `New_Theory/MODEL_LEGITIMACY.md` | §4.8 addendum (verdict AS IS) + changelog; correct the k_tr addendum's embedding/creep mis-attribution (loosening dominates the pre-gross erosion) |

---

## 8. Scope / out-of-scope

- **OUT:** canonical re-fit on the gated regime (later gated decision); the
  physical transmitted-force coupling (Approach 3, needs re-fit); any change to
  the canonical `shared` block; force-mode behavior.
- **Interactions:** composes with the merged bending `k_tr` (needs it to be
  meaningful) and with damage (`damage`/`W_crit` orthogonal — the gate is on
  `d_theta`, damage on `dD`). Conservation preserved (§3.4).
- **Foundational, opt-in:** like `k_tr_mode`/`W_crit`/`conform_driver`, this is a
  capability that stays inert by default until a run/experiment opts in.
