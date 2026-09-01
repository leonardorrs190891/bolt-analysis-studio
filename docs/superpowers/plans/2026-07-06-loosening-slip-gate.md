# Loosening Slip-Regime Gate — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline, the professor's established preference). Steps use checkbox (`- [ ]`) syntax. An Opus review of the engine diff runs before merge.

**Goal:** Gate rotational self-loosening by the gross-slip fraction of the stroke so it is suppressed in partial slip (stick) and active in gross slip — fixing the plateau over-prediction the k_tr fix left open. Opt-in, backward-compat, zero-refit.

**Architecture:** A `loosening_slip_gate(state, geom, mat, slip_amp)` helper returns `slip_amp/(slip_amp+δ_t)` (= gross-slip fraction) when `loosening_slip_coupling="gross_fraction"`, else `1.0`. `RotationalLooseningLoss.rate` multiplies its `d_theta` by that gate (alongside the existing `slip_onset_gate`/`conformation_gate`). Validate as a zero-refit transfer sweep (`--loosen-coupled`) against pre-registered thresholds. Canonical re-fit is a separate gated decision, NOT in this plan.

**Tech Stack:** Python, `DynamicStiffnessAnalyzer`, `transfer_validation.py`, pytest.

**Spec:** `docs/superpowers/specs/2026-07-06-loosening-slip-gate-design.md`

## Global Constraints

- All I/O `encoding='utf-8'`; `ast.parse` syntax-check after every `.py` edit; **run pytest and check the exit code before committing** (do NOT mask it with `| tail` in a `&&` chain — a failing test slipped through that way once).
- **Never `git add -A`** (explicit file lists — OneDrive parallel-session hazard); never touch `New_Theory/Materiais_Metalicos_EPL_Gb.docx` / `crash_log.txt`.
- Commits Portuguese, **no accents**, trailer `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- **Opt-in / backward-compat hard gate:** default `loosening_slip_coupling="off"` ⇒ gate `≡ 1.0` ⇒ every existing run/fit **bit-identical**. Force-mode (`slip_amp None`) ⇒ `1.0` even when on.
- **Canonical `shared` block NEVER written** by this work; **canonical re-fit is OUT of scope**.
- **Frozen pre-registered validation thresholds** (Task 3) — set before the run, recorded AS IS.
- `*.png`/`*.csv` gitignored (force-add experiment pngs with `git add -f`).
- **Conservation:** gate multiplies `d_theta`, so `dF_0` and `dE` scale together — do NOT gate only one.

---

### Task 1: Engine — gross-slip gate on rotational loosening (opt-in)

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (`JointMaterial` field after line 168 `c_bend`; new `loosening_slip_gate` after `k_tr_transverse` ~line 402; apply in `RotationalLooseningLoss.rate` at the `d_theta` line 765)
- Test: `tests/test_loosening_slip_gate.py` (new)

**Interfaces:**
- Produces: `JointMaterial.loosening_slip_coupling: str = "off"`; `loosening_slip_gate(state, geom, mat, slip_amp: Optional[float]) -> float`.
- Consumes: existing `F_slip_transverse(state, mat)`, `k_tr_transverse(geom, mat)`, `RotationalLooseningLoss.rate(..., slip_amp_override=None)`.

- [ ] **Step 1: Write the failing tests** — `tests/test_loosening_slip_gate.py`:

```python
"""Loosening slip-regime gate (spec 2026-07-06): gross-slip-fraction gate, opt-in."""
import numpy as np

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    RotationalLooseningLoss, F_slip_transverse, k_tr_transverse,
    loosening_slip_gate,
)

M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=2.09e-4)


def test_gate_off_by_default_returns_one():
    m = JointMaterial()
    assert m.loosening_slip_coupling == "off"
    st = SlowState(F_0=50e3)
    assert loosening_slip_gate(st, M16, m, 0.0) == 1.0
    assert loosening_slip_gate(st, M16, m, 5e-4) == 1.0
    assert loosening_slip_gate(st, M16, m, None) == 1.0


def test_gate_force_mode_returns_one_even_when_on():
    m = JointMaterial(loosening_slip_coupling="gross_fraction")
    st = SlowState(F_0=50e3)
    assert loosening_slip_gate(st, M16, m, None) == 1.0


def test_gate_partial_slip_is_zero():
    m = JointMaterial(loosening_slip_coupling="gross_fraction")
    st = SlowState(F_0=50e3)
    assert loosening_slip_gate(st, M16, m, 0.0) == 0.0


def test_gate_ramps_and_saturates_in_gross():
    m = JointMaterial(k_tr_mode="bending", loosening_slip_coupling="gross_fraction")
    st = SlowState(F_0=50e3)
    dt = F_slip_transverse(st, m) / k_tr_transverse(M16, m)   # delta_t
    assert abs(loosening_slip_gate(st, M16, m, dt) - 0.5) < 1e-9   # slip=dt => 1/2
    assert loosening_slip_gate(st, M16, m, 0.01 * dt) < 0.02       # barely gross
    assert loosening_slip_gate(st, M16, m, 100.0 * dt) > 0.98      # deep gross => ~1


def test_loosening_dF0_zeroed_in_partial_when_coupled():
    """coupling on + slip_amp=0 => g=0 => loosening dF_0 exactly 0."""
    m = JointMaterial(k_tr_mode="bending", loosening_slip_coupling="gross_fraction")
    st = SlowState(F_0=50e3)
    r = RotationalLooseningLoss().rate(st, M16, m, 0.4 * 50e3, np.pi / 2,
                                       0.5, 100, slip_amp_override=0.0)
    assert r["dF_0"] == 0.0
    assert r["dE_dissipated"] == 0.0


def test_end_to_end_gate_retains_preload_in_partial_regime():
    """liu2025-like M16 partial case: gate ON retains materially more F0 than OFF."""
    geom = M16
    F0, delta, freq, F_amp = 60e3, 0.25e-3, 0.5, 0.4 * 60e3

    def run(coupling):
        m = JointMaterial(k_tr_mode="bending", loosening_slip_coupling=coupling,
                          mu_bearing=0.15, mu_thread=0.15, emb_depth=9.5e-6,
                          C_creep=1.867e-11)
        ana = DynamicStiffnessAnalyzer(geom, m, F0)
        for _ in range(20000):
            ana.step_cycle(F_amp, np.pi / 2, freq, delta_amp=delta)
        return max(ana.state.F_0, 0.0) / F0

    r_off = run("off")
    r_on = run("gross_fraction")
    assert r_on > r_off + 0.2      # gate suppresses partial-slip loosening
    assert r_off < 0.5             # gate off: loosening drives collapse
    assert r_on > 0.6              # gate on: plateaus
```

- [ ] **Step 2: Run to verify fail**

Run: `python -m pytest tests/test_loosening_slip_gate.py -q; echo "EXIT=$?"`
Expected: FAIL — `ImportError: cannot import name 'loosening_slip_gate'`.

- [ ] **Step 3: Add the `JointMaterial` field** — after line 168 (`c_bend`):

```python
    # Acoplamento loosening<->regime de slip (spec 2026-07-06): "off" (default,
    # loosening usa o criterio de forca atual = backward-compat) | "gross_fraction"
    # (loosening gateado pela fracao de gross-slip do curso g=slip/(slip+delta_t)).
    # So faz sentido com k_tr_mode="bending"; force-mode (slip None) => 1.0.
    loosening_slip_coupling: str = "off"
```

- [ ] **Step 4: Add `loosening_slip_gate`** — after `k_tr_transverse` (~line 402):

```python
def loosening_slip_gate(state: SlowState, geom: JointGeometry,
                        mat: JointMaterial, slip_amp: Optional[float]) -> float:
    """Gate da fracao de gross-slip para o loosening rotacional (spec 2026-07-06).
    Junker precisa de GROSS slip (ratcheting); em partial slip (stick) o backing-
    off e suprimido. g = slip/(slip+delta_t) = (delta-delta_t)/delta = fracao de
    gross-slip do curso, delta_t = F_slip/k_tr. "off" ou slip_amp None (force-mode)
    => 1.0 (backward-compat)."""
    if mat.loosening_slip_coupling == "off" or slip_amp is None:
        return 1.0
    if mat.loosening_slip_coupling == "gross_fraction":
        delta_t = F_slip_transverse(state, mat) / max(k_tr_transverse(geom, mat), 1e-12)
        return slip_amp / max(slip_amp + delta_t, 1e-12)
    return 1.0
```

- [ ] **Step 5: Apply the gate in `RotationalLooseningLoss.rate`** — replace the `d_theta = (...)` block at line 765:

```python
        g_slip_regime = loosening_slip_gate(state, geom, mat, slip_amp_override)
        d_theta = (g * conformation_gate(state, mat) * g_slip_regime * k_scale
                   * slip_fraction * (T_loose - T_resist) / max(k_torsional, 1.0))
```

- [ ] **Step 6: Syntax-check**

Run: `python -c "import ast; ast.parse(open('src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py',encoding='utf-8').read()); print('OK')"`
Expected: `OK`.

- [ ] **Step 7: Run the new tests + backward-compat sweep** (check exit codes, no pipe-masking)

```bash
python -m pytest tests/test_loosening_slip_gate.py -q; echo "EXIT=$?"
python -m pytest tests/test_surface_damage.py tests/test_slip_onset_incubation.py \
  tests/test_pressure_conformation.py tests/test_v2_solver_preload.py \
  tests/test_shared_calibrator.py tests/test_predictive_damage_trigger.py \
  tests/test_slip_regime_ktr.py -q; echo "EXIT=$?"
```
Expected: both `EXIT=0`. Backward-compat: default `off` leaves every existing test unchanged.

- [ ] **Step 8: Commit**

```bash
git add src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py tests/test_loosening_slip_gate.py
git commit -m "feat(engine): gate do loosening ao regime de slip (gross-slip fraction, opt-in)" \
  -m "loosening_slip_gate(state,geom,mat,slip)=slip/(slip+delta_t)=fracao de gross-slip; multiplica d_theta do RotationalLooseningLoss (junto de slip_onset/conformation gates). Junker precisa de gross slip; partial => g=0 => loosening off. Opt-in loosening_slip_coupling='off' (default, bit-identical) | 'gross_fraction'. Zero constantes novas, preserva calibracao (dF_0 e dE escalam juntos = conservacao). 6 testes; backward-compat sweep verde." \
  -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Validation harness — `--loosen-coupled` flag

**Files:**
- Modify: `New_Theory/transfer_validation.py` (module flag near line 47; `_simulate` material build near line 131; `main()` arg parse + suffix + `choices` near lines 206–284)

**Interfaces:**
- Consumes: `JointMaterial.loosening_slip_coupling` + `k_tr_mode` (Task 1 + the merged k_tr fix).
- Produces: `--loosen-coupled` CLI flag → `_loosen` artifacts (`transfer_{results,report,grid}_loosen.*`). Composable suffix (mirrors `--ktr-bending` → `_ktr`).

- [ ] **Step 1: Add the module flag** — after line 47 (`_KTR_BENDING = ...`):

```python
_LOOSEN_COUPLED = False     # toggled por --loosen-coupled (loosening gateado pelo regime de slip, spec 2026-07-06; implica bending)
```

- [ ] **Step 2: Wire it into `_simulate`** — in the `kw` build (after the `_KTR_BENDING` block that sets `kw["k_tr_mode"]="bending"`), add:

```python
    if _LOOSEN_COUPLED:
        # --loosen-coupled: gate do loosening pela fracao de gross-slip. So faz
        # sentido com delta_t realista, entao forca bending tambem (spec 2026-07-06).
        kw["k_tr_mode"] = "bending"
        kw["loosening_slip_coupling"] = "gross_fraction"
```

- [ ] **Step 3: Parse the flag + compose suffix + record mode** — in `main()`:

Add to the `global` line and parsing (near line 206):
```python
    global _DAMAGE_ON, _DAMAGE_TRIGGER, _KTR_BENDING, _LOOSEN_COUPLED, TRIGGER_W_CRIT
    ...
    _LOOSEN_COUPLED = "--loosen-coupled" in sys.argv
```
After the `_KTR_BENDING` suffix block:
```python
    if _LOOSEN_COUPLED:
        suffix += "_loosen"
```
In the `choices` dict (near `ktr_mode=...`), add:
```python
                     loosening=("gross_fraction (gate do loosening pela fracao de "
                                "gross-slip; implica bending; spec 2026-07-06)"
                                if _LOOSEN_COUPLED else "off (criterio de forca atual)"),
```
And extend the console `print` mode line (near line 222) to include `loosening`.

- [ ] **Step 4: Syntax-check + smoke that the flag flows through**

```bash
python -c "import ast; ast.parse(open('New_Theory/transfer_validation.py',encoding='utf-8').read()); print('OK')"
python - <<'PY'
import sys; sys.path.insert(0,'src'); sys.path.insert(0,'New_Theory')
import transfer_validation as tv
tv._LOOSEN_COUPLED = True
import numpy as np
sel,_ = tv.select_cases()
# build one material via the private path to confirm the field is set
case = sel[0]; inp = tv.inputs_for(case)
# _simulate builds the material internally; assert no exception on 1 short run
r = tv._simulate(case, inp["grip_mm"]["value"], inp["mu"]["value"],
                 inp["rz"]["value"], inp["F_amp_N"]["value"], 5)
print("smoke OK, final ratio", round(r[0][-1], 4))
PY
echo "EXIT=$?"
```
Expected: `OK`, `smoke OK ...`, `EXIT=0`.

- [ ] **Step 5: Commit**

```bash
git add New_Theory/transfer_validation.py
git commit -m "feat(transfer): flag --loosen-coupled (gate do loosening ao regime de slip)" \
  -m "Espelha --ktr-bending: _LOOSEN_COUPLED seta loosening_slip_coupling='gross_fraction' + k_tr_mode='bending' (o gate so faz sentido com delta_t realista). Suffix composavel _loosen; choices.loosening registra o modo." \
  -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Run validation + document §4.8 AS IS

**Files:**
- Run artifacts: `New_Theory/transfer_{results,report,grid}_loosen.*`
- Modify: `New_Theory/MODEL_LEGITIMACY.md` (§4.8 addendum + §9 changelog; correct the k_tr addendum's embedding/creep mis-attribution)

**Pre-registered thresholds (FROZEN before the run, AS IS)** — from spec §5, calibrated to the known baselines (k_tr-only realized plateau 14% / collapse→loosens 45%; 7 plateau + 31 collapse cases):
- **Plateau fixed (primary):** realized plateau→plateaus (`final_data>0.55` with `final_pred>0.55`) **≥ 50%** (from 14%), AND median plateau `final_pred` improvement **≥ 0.2** vs the `axial_frac` baseline (`transfer_results.json`).
- **Collapse not destroyed (guard):** collapse→loosens (`final_data<0.30` with `final_pred<0.55`) **≥ 40%** (k_tr-only was 45%; genuine collapses already under-predicted by frozen cross-rig constants).
- **Global MAE** reported AS IS.

- [ ] **Step 1: Run the validation** (background, ~2–5 min)

```bash
python New_Theory/transfer_validation.py --loosen-coupled > /tmp/loosen_run.log 2>&1; echo "EXIT=$?"
```
(Use the scratchpad path for the log on Windows.) Expected: `EXIT=0`, artifacts `transfer_*_loosen.*` written.

- [ ] **Step 2: Compute the pre-registered metrics** — reuse the k_tr analysis shape (compare `transfer_results_loosen.json` vs the `axial_frac` baseline `transfer_results.json`):

```python
import json
from pathlib import Path
import numpy as np
R = r"C:/Users/leo_r/OneDrive/BPL/Analitical/BAS_V2"
base = {r["csv"]: r for r in json.load(open(R+"/New_Theory/transfer_results.json"))["results"]}
loo = {r["csv"]: r for r in json.load(open(R+"/New_Theory/transfer_results_loosen.json"))["results"]}
common = [c for c in loo if c in base]
COLL, PLAT = 0.30, 0.55
plat = [c for c in common if loo[c]["final_data"] > PLAT]
coll = [c for c in common if loo[c]["final_data"] < COLL]
plat_ok = sum(loo[c]["final_pred"] > PLAT for c in plat)
coll_ok = sum(loo[c]["final_pred"] < PLAT for c in coll)
imp = np.median([loo[c]["final_pred"] - base[c]["final_pred"] for c in plat])
print(f"plateau->plateaus {plat_ok}/{len(plat)}={plat_ok/max(len(plat),1):.0%} (thr >=50%)")
print(f"collapse->loosens {coll_ok}/{len(coll)}={coll_ok/max(len(coll),1):.0%} (thr >=40%)")
print(f"plateau final_pred improvement median {imp:+.3f} (thr >=0.2)")
print(f"GLOBAL median MAE base {np.median([base[c]['MAE'] for c in common]):.4f} -> "
      f"loosen {np.median([loo[c]['MAE'] for c in common]):.4f}")
```
Record the three verdicts (pass/fail) AS IS.

- [ ] **Step 3: Write the §4.8 addendum** — append after the k_tr addendum in `New_Theory/MODEL_LEGITIMACY.md`, AS IS: state whether each frozen threshold passed, the plateau/collapse trade-off observed, and **correct the k_tr addendum's mis-attribution** (add one sentence: the pre-gross erosion is loosening-dominated, not embedding/creep — per the 2026-07-06 decomposition). Add a `## 9` changelog row. Preserve artifacts (force-add the PNG).

- [ ] **Step 4: Commit**

```bash
git add New_Theory/MODEL_LEGITIMACY.md New_Theory/transfer_results_loosen.json New_Theory/transfer_report_loosen.md
git add -f New_Theory/transfer_grid_loosen.png
git commit -m "docs(4.8): validacao do gate do loosening AS IS (thresholds pre-registrados)" \
  -m "<preencher com os numeros AS IS: plateau->plateaus X%, collapse->loosens Y%, delta_final_pred Z; veredicto vs thresholds; trade-off plateau/collapse limitado pela acuracia de c_bend; corrige atribuicao embedding/creep do addendum de k_tr>" \
  -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

**Spec coverage:** §2 gate form → Task 1 (function + application, exact code); §3 engine change (field/function/apply/conservation) → Task 1 Steps 3–5; §4 activation/backward-compat → Task 1 field default + `test_gate_off_by_default`/`test_gate_force_mode` + Step 7 sweep; §5 validation + pre-registered thresholds → Task 3 (flag in Task 2); §6 testing → Task 1 Step 1 (all six tests: off, force-mode, partial=0, gross ramp, dF_0 zeroed, end-to-end); §7 files → Tasks 1–3; §8 scope (canonical re-fit OUT, Approach 3 deferred, `shared` untouched) → Global Constraints + Task 3 doc. ✅

**Placeholder scan:** Task 1 is fully code-exact (field, function, application, six tests with concrete fixtures/assertions). Task 2 gives the exact flag wiring mirroring `--ktr-bending`. Task 3's run outputs are unknown by design (AS IS) — the commit body placeholder is explicitly "fill with AS-IS numbers," not a hidden gap; the metrics script is complete. No forbidden placeholders. ✅

**Type consistency:** `loosening_slip_gate(state, geom, mat, slip_amp: Optional[float]) -> float` used identically in the helper, the tests, and the `RotationalLooseningLoss.rate` call (`slip_amp_override`); `loosening_slip_coupling: str` values `"off"`/`"gross_fraction"` consistent across field, gate, tests, and the harness flag. `F_slip_transverse`/`k_tr_transverse` signatures match their existing defs. ✅
