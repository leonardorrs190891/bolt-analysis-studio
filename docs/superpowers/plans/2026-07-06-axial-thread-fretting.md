# Axial Thread-Flank Fretting Loss Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline, the professor's established preference). Steps use checkbox (`- [ ]`) syntax. An Opus review of the engine diff runs before merge.

**Goal:** Add `ThreadFrettingLoss` — an opt-in Archard flank-wear mechanism driven by the axial load amplitude (`F_ax = F_amp·|cos θ|`, reusing `K_archard`) — so the model develops a non-zero `∂(final)/∂A_F` (the form §4.6 falsified as missing), then calibrate its one constant `k_thread_fret` and validate on the axial harness.

**Architecture:** New `LossMechanism` sibling of `WearLoss`; `dF₀ = −k_b·d_fret` with `d_fret ∝ K_archard·F₀·(F_ax/k_b)` ⇒ `dF₀ ∝ −F₀·A_F`. New `JointMaterial.k_thread_fret` (default 0.0 = inert) + `SlowState.delta_thread_fret`. Calibrate `k_thread_fret` to the Liu2017 A_F gradient in `calibrate_axial.py`; validate against pre-registered thresholds.

**Tech Stack:** Python, `DynamicStiffnessAnalyzer`, `calibrate_axial.py`, pytest.

**Spec:** `docs/superpowers/specs/2026-07-06-axial-thread-fretting-design.md`

## Global Constraints

- All I/O `encoding='utf-8'`; `ast.parse` syntax-check after every `.py` edit; **run pytest and check the exit code before committing** (never mask with `| tail` in a `&&` chain).
- **Never `git add -A`** (explicit file lists — OneDrive hazard); never touch `New_Theory/Materiais_Metalicos_EPL_Gb.docx` / `crash_log.txt`.
- Commits Portuguese, **no accents**, trailer `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- **Opt-in / backward-compat hard gate:** default `k_thread_fret=0.0` ⇒ mechanism returns zeros ⇒ every existing run/fit **bit-identical**. Second guarantee: axial-driven, so `F_ax=0` on the transverse library (θ=π/2) → inert there even when enabled.
- **This adds a NEW fitted per-pair constant** (`k_thread_fret`) — the deferred "B2". Not zero-refit; provenance documented (fitted to Liu2017 axial).
- **Canonical `shared` block NEVER written**; canonical re-fit OUT of scope.
- **Frozen pre-registered validation thresholds** (Task 3) — set before the run, recorded AS IS.
- `*.png`/`*.csv` gitignored (force-add experiment pngs).
- **Conservation:** mirror `WearLoss` (real friction `dE`, preload loss via `U_released`); track `delta_thread_fret` so the ledger stays consistent.

---

### Task 1: Engine — `ThreadFrettingLoss` mechanism (opt-in)

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (`JointMaterial.k_thread_fret` after line 91 `hardness`; `SlowState.delta_thread_fret` after line 216 `delta_wear`; new `ThreadFrettingLoss` after `WearLoss` ~line 718; register in `self.losses` lines 845–849)
- Test: `tests/test_thread_fretting.py` (new)

**Interfaces:**
- Produces: `JointMaterial.k_thread_fret: float = 0.0`; `SlowState.delta_thread_fret: float = 0.0`; `ThreadFrettingLoss` (`name="thread_fretting"`), `.rate(state, geom, mat, F_amp, theta_load, freq, cycle_N, slip_amp_override=None) -> dict`.

- [ ] **Step 1: Write the failing tests** — `tests/test_thread_fretting.py`:

```python
"""Axial thread-flank fretting loss (spec 2026-07-06): Archard flank, opt-in, prop A_F."""
import numpy as np

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    ThreadFrettingLoss,
)

M12 = JointGeometry(A_s=84.3e-6, L_eff=0.040, d_2=10.863e-3,
                    pitch=1.75e-3, r_bearing=10e-3, A_contact=1.5e-4)


def test_off_by_default_returns_zero():
    m = JointMaterial()                      # k_thread_fret default 0.0
    assert m.k_thread_fret == 0.0
    st = SlowState(F_0=50e3)
    r = ThreadFrettingLoss().rate(st, M12, m, 20e3, 0.0, 30.0, 100)
    assert r["dF_0"] == 0.0 and r["dE_dissipated"] == 0.0


def test_axial_loss_scales_linearly_with_AF():
    m = JointMaterial(k_thread_fret=0.5)
    st = SlowState(F_0=50e3)
    r1 = ThreadFrettingLoss().rate(st, M12, m, 10e3, 0.0, 30.0, 100)   # axial, A_F=10kN
    r2 = ThreadFrettingLoss().rate(st, M12, m, 20e3, 0.0, 30.0, 100)   # axial, A_F=20kN
    assert r1["dF_0"] < 0.0                                            # loss
    assert abs(r2["dF_0"]) == abs(r1["dF_0"]) * 2                      # linear in A_F


def test_transverse_is_inert_even_when_enabled():
    m = JointMaterial(k_thread_fret=0.5)
    st = SlowState(F_0=50e3)
    r = ThreadFrettingLoss().rate(st, M12, m, 20e3, np.pi / 2, 30.0, 100)  # theta=pi/2
    assert r["dF_0"] == 0.0                                            # F_ax = cos(pi/2) = 0


def test_end_to_end_AF_gradient_becomes_nonzero():
    """Two axial runs at different A_F give different final F0 (today identical)."""
    geom = M12
    def run(F_amp):
        m = JointMaterial(k_thread_fret=0.5, mu_thread=0.12, mu_bearing=0.12,
                          emb_depth=9.5e-6)
        ana = DynamicStiffnessAnalyzer(geom, m, 40e3)
        for _ in range(2000):
            ana.step_cycle(F_amp, 0.0, 30.0)                          # axial, force-mode
        return max(ana.state.F_0, 0.0) / 40e3
    assert run(15e3) > run(25e3)             # higher A_F => more loss => lower final


def test_conservation_residual_bounded_axial():
    geom = M12
    m = JointMaterial(k_thread_fret=0.5, mu_thread=0.12, mu_bearing=0.12, emb_depth=9.5e-6)
    ana = DynamicStiffnessAnalyzer(geom, m, 40e3)
    for _ in range(2000):
        ana.step_cycle(20e3, 0.0, 30.0)
    assert abs(ana.energy.conservation_residual) < 1e4                # same order as 4.6 baseline
```

- [ ] **Step 2: Run to verify fail**

Run: `python -m pytest tests/test_thread_fretting.py -q; echo "EXIT=$?"`
Expected: FAIL — `ImportError: cannot import name 'ThreadFrettingLoss'`.

- [ ] **Step 3: Add `JointMaterial.k_thread_fret`** — after line 91 (`hardness`):

```python
    # Fretting de flanco de rosca dirigido pela amplitude de carga AXIAL (spec
    # 2026-07-06): fator geometrico/engajamento (flank-slip frac + area + projecao
    # flanco->axial), O(0.1-1). 0.0 = mecanismo OFF (backward-compat). Fitado
    # per-par ao Liu2017 axial (a "B2" adiada, procedencia = fitted).
    k_thread_fret: float = 0.0
```

- [ ] **Step 4: Add `SlowState.delta_thread_fret`** — after line 216 (`delta_wear`):

```python
    delta_thread_fret: float = 0.0   # m — profundidade de fretting de flanco (axial)
```

(Do NOT add it to `as_array` — that method is unconsumed and already omits `D`; the `setattr` ds-loop applies the field by name.)

- [ ] **Step 5: Add `ThreadFrettingLoss`** — after `WearLoss` (~line 718):

```python
class ThreadFrettingLoss(LossMechanism):
    """Fretting/wear de flanco de rosca sob carga AXIAL oscilante (spec 2026-07-06).

    Forma faltante da falsificacao axial (MODEL_LEGITIMACY.md 4.6): perda dirigida
    pela amplitude de carga axial A_F, abaixo do onset de loosening. Archard no
    flanco (mesmo par de material que o bearing => reusa K_archard/hardness),
    dirigido pelo micro-slip de flanco s_flank = F_ax/k_b. Irma do WearLoss.
    dF_0 = -k_b*d_fret  =>  dF_0 ~ -F0*A_F (k_b cancela). Inerte em transversal
    (F_ax = F_amp*|cos theta| = 0 em theta=pi/2) e com k_thread_fret=0 (default).
    """
    name = "thread_fretting"

    def rate(self, state, geom, mat, F_amp, theta_load, freq, cycle_N,
             slip_amp_override=None):
        F_clamp = max(state.F_0, 0.0)
        F_ax = F_amp * abs(np.cos(theta_load))            # componente axial da amplitude
        if mat.k_thread_fret <= 0.0 or F_ax <= 0.0 or F_clamp <= 0.0:
            return dict(dF_0=0.0, dE_dissipated=0.0, ds={})
        s_flank = F_ax / max(geom.k_b, 1.0)               # amplitude de desloc. axial
        fret_dist = 4.0 * s_flank                         # ida+volta, como WearLoss
        d_fret = (mat.k_thread_fret * mat.K_archard * F_clamp * fret_dist
                  / max(mat.hardness * geom.A_s, 1.0))
        dF_0 = -geom.k_b * d_fret
        dE = mat.mu_thread * F_clamp * fret_dist          # trabalho de atrito no flanco
        return dict(dF_0=dF_0, dE_dissipated=dE,
                    ds=dict(delta_thread_fret=d_fret))
```

- [ ] **Step 6: Register in `self.losses`** — lines 845–849, append after `RotationalLooseningLoss()`:

```python
        self.losses = loss_mechanisms or [
            EmbeddingLoss(),
            CreepLoss(),
            WearLoss(),
            RotationalLooseningLoss(),
            ThreadFrettingLoss(),
        ]
```

- [ ] **Step 7: Syntax-check + tests + backward-compat sweep** (check exit codes)

```bash
python -c "import ast; ast.parse(open('src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py',encoding='utf-8').read()); print('OK')"
python -m pytest tests/test_thread_fretting.py -q; echo "EXIT=$?"
python -m pytest tests/test_surface_damage.py tests/test_slip_onset_incubation.py \
  tests/test_pressure_conformation.py tests/test_v2_solver_preload.py \
  tests/test_shared_calibrator.py tests/test_slip_regime_ktr.py \
  tests/test_loosening_slip_gate.py tests/test_anchor_creep.py \
  tests/test_transfer_validation.py -q; echo "EXIT=$?"
```
Expected: both `EXIT=0` (default off + transverse-inert ⇒ everything unchanged).

- [ ] **Step 8: Commit**

```bash
git add src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py tests/test_thread_fretting.py
git commit -m "feat(engine): ThreadFrettingLoss — fretting de flanco axial (prop A_F, opt-in)" \
  -m "Forma faltante do 4.6: Archard no flanco de rosca dirigido por F_ax=F_amp*|cos theta|, reusa K_archard/hardness, s_flank=F_ax/k_b. dF_0=-k_b*d_fret => dF_0~-F0*A_F (k_b cancela). k_thread_fret default 0=off (bit-identical); inerte em transversal (F_ax=0). Novo estado delta_thread_fret. 5 testes; backward-compat sweep verde." \
  -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Calibrate `k_thread_fret` + validate on the axial harness

**Files:**
- Modify: `New_Theory/calibrate_axial.py` (module flag `_K_THREAD_FRET` near the imports/top; inject into the `mat` build in `simulate` line 74; `--k-thread-fret <val>` arg + a `--calibrate-fret` sweep in `main`)

**Interfaces:**
- Consumes: `JointMaterial.k_thread_fret` (Task 1). Produces: calibrated `k_thread_fret` value + the pre-registered metrics (A_F gradient, axial MAE, P₀ gradient) printed/written.

- [ ] **Step 1: Add the module flag + inject into the material** — near the top of `calibrate_axial.py` add `_K_THREAD_FRET = 0.0`, and in `simulate` (line 74) change the `mat` build to pass it:

```python
    mat = JointMaterial(emb_depth=emb_m, mu_thread=base["mu"],
                        mu_bearing=base["mu"], k_thread_fret=_K_THREAD_FRET,
                        **consts)
```

- [ ] **Step 2: Add CLI in `main()`** — parse a fixed value or a calibration sweep:

```python
    global _K_THREAD_FRET
    if "--k-thread-fret" in sys.argv:
        _K_THREAD_FRET = float(sys.argv[sys.argv.index("--k-thread-fret") + 1])
    if "--calibrate-fret" in sys.argv:
        _calibrate_fret(consts)      # sweep, print best k vs the A_F gradient, then continue at best
```

- [ ] **Step 3: Add the calibration sweep** — a function that sweeps `k_thread_fret`, computes the model A_F gradient at each, and picks the value closest to the data gradient (−2.216e-5/N). Mirror the existing `_grad`:

```python
def _calibrate_fret(consts):
    global _K_THREAD_FRET
    target = -2.216e-5                       # data dfinal/dAF (N^-1), 4.6
    best = None
    print("k_thread_fret sweep (model dfinal/dAF vs target %.3e):" % target)
    for k in [0.0, 0.05, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0]:
        _K_THREAD_FRET = k
        results = [predict_one(e, consts) for e in ENTRIES]
        yd = [r["final_data"] for r in results if r["name"].startswith("Liu2017 AF")]
        yp = [r["final_pred"] for r in results if r["name"].startswith("Liu2017 AF")]
        xs = [r["F_amp_N"] for r in results if r["name"].startswith("Liu2017 AF")]
        gm = float(np.polyfit(xs, yp, 1)[0]) if len(xs) > 1 else 0.0
        print(f"  k={k:5.2f}  model dfinal/dAF={gm:.3e}")
        if best is None or abs(gm - target) < abs(best[1] - target):
            best = (k, gm)
    _K_THREAD_FRET = best[0]
    print(f"BEST k_thread_fret={best[0]} (model grad {best[1]:.3e} vs data {target:.3e})")
```

(Note: `ENTRIES` / `predict_one` / `r["F_amp_N"]` — confirm the exact names in `calibrate_axial.py` when implementing; `predict_one` returns a dict with `final_pred`/`final_data` and the entry carries `F_amp`. Adapt the key names to the file. If `predict_one` doesn't expose `F_amp`, pull it from the entry tuple `(name, csv, F0, F_amp, base)`.)

- [ ] **Step 4: Syntax-check + run the calibration sweep**

```bash
python -c "import ast; ast.parse(open('New_Theory/calibrate_axial.py',encoding='utf-8').read()); print('OK')"
python New_Theory/calibrate_axial.py --calibrate-fret --quick; echo "EXIT=$?"
```
Expected: `OK`; the sweep prints model `dfinal/dAF` rising (more negative) with `k`, a BEST value, `EXIT=0`.

- [ ] **Step 5: Full run at the calibrated value + capture metrics**

```bash
python New_Theory/calibrate_axial.py --k-thread-fret <BEST>; echo "EXIT=$?"
```
Record AS IS: `gradients.dfinal_dAF` (model vs data), `dfinal_dP0` (model vs data, must stay sign-positive), median `MAE_pred` on Liu2017 vs the §4.6 baseline 0.1518, and whether the 5 A_F curves now differ.

- [ ] **Step 6: Confirm the transverse library is untouched**

```bash
python New_Theory/transfer_validation.py 2>&1 | grep GLOBAL; echo "EXIT=$?"
```
Expected: GLOBAL median MAE **unchanged** vs the committed baseline (k_thread_fret=0 default in the transfer harness; and F_ax=0 there regardless). Hard backward-compat check.

- [ ] **Step 7: Commit**

```bash
git add New_Theory/calibrate_axial.py
git commit -m "feat(axial): calibra k_thread_fret ao gradiente dfinal/dAF do Liu2017" \
  -m "<preencher: BEST k_thread_fret, model dfinal/dAF vs data -2.216e-5, MAE axial vs 0.1518, dfinal/dP0 mantem sinal, transversal inalterado>" \
  -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Document §4.6 AS IS + provenance + changelog

**Files:**
- Modify: `New_Theory/MODEL_LEGITIMACY.md` (§4.6 addendum with the AS-IS verdict vs the frozen thresholds; §5.1 provenance line for `k_thread_fret`; §9 changelog row)

**Pre-registered thresholds (FROZEN, from spec §5):**
- **Representability (primary):** calibrated `k_thread_fret` ⇒ `∂(final)/∂A_F` **negative** and the 5 A_F-sweep curves **separate monotonically** (were identical at 0.6555).
- **Magnitude:** `∂(final)/∂A_F` within a **factor of ~2** of −2.216e-5/N.
- **Axial MAE:** median `MAE_pred` on Liu2017 **improves** vs 0.1518.
- **P₀ gradient:** stays sign-positive (was +1.585e-5/N vs data +2.633e-5/N).
- **Transverse library:** median MAE **bit-identical** (hard check).

- [ ] **Step 1: Write the §4.6 addendum** — append after the existing §4.6 content, AS IS: state each frozen threshold's pass/fail with the measured numbers, the calibrated `k_thread_fret`, and the honest note that the magnitude is partly circular (fit) so the *representability* + non-regression are the real result. Add a `## 9` changelog row and a `## 5.1` provenance line (`k_thread_fret` = fitted, per-pair, Liu2017 axial — a §5.1-class constant, the deferred B2).

- [ ] **Step 2: Commit**

```bash
git add New_Theory/MODEL_LEGITIMACY.md
git commit -m "docs(4.6): validacao do fretting de flanco axial AS IS (thresholds pre-registrados)" \
  -m "<preencher com os numeros AS IS + veredicto vs thresholds>" \
  -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

**Spec coverage:** §2 mechanism form → Task 1 Step 5 (exact `rate`); §3 engine change (field/state/class/register) → Task 1 Steps 3–6; §4 activation/backward-compat → Task 1 field default + `test_off_by_default`/`test_transverse_is_inert` + Step 7 sweep + Task 2 Step 6; §5 validation + pre-registered thresholds → Task 2 (calibrate+run) + Task 3 (verdict); §6 testing → Task 1 Step 1 (off-default, axial∝A_F, transverse-inert, gradient-nonzero, conservation); §7 files → Tasks 1–3; §8 scope (new fitted constant, canonical untouched, viscous-bookkeeping orthogonal) → Global Constraints + Task 3 provenance. ✅

**Placeholder scan:** Task 1 fully code-exact. Task 2 gives the exact wiring + a complete calibration-sweep function, with an explicit note to confirm `ENTRIES`/`predict_one`/`F_amp` key names against the file (they exist per the grep: `predict_one(entry, ...)`, entry tuple `(name, csv, F0, F_amp, base)`, `_grad` over AF-sweep) — adaptation, not a gap. Task 2/3 commit bodies are "fill with AS-IS numbers" (empirical outputs unknown by design), not hidden gaps. ✅

**Type consistency:** `ThreadFrettingLoss.rate(...)` matches the `LossMechanism.rate` signature used by the other mechanisms; `k_thread_fret: float`, `delta_thread_fret: float`; `ds=dict(delta_thread_fret=...)` applied by the existing `setattr` loop; `_K_THREAD_FRET` injected into the `simulate` `mat` build. `F_ax = F_amp·|cos θ|` consistent between the mechanism and the tests (θ=0 axial, θ=π/2 transverse). ✅
