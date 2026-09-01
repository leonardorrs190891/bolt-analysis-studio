# Pressure-Conformation Mechanism (engine) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the pressure-gated slip-conformation mechanism to `DynamicStiffnessAnalyzer` (spec `docs/superpowers/specs/2026-07-04-pressure-conformation-design.md`) — a `conformation_gate` that suppresses the slip-driven preload loss (wear + rotational-loosening) as an over-torqued contact conforms, **default-inert** so every existing fit is bit-unchanged. This plan delivers the mechanism + its activation-registry rule + engine tests. **The calibration/science validation (fit `W_conf_ref`/`n` on the shared block, §4.9 writeup) is a separate follow-up plan (Plan B).**

**Architecture:** Mirror the existing `slip_onset_gate` pattern exactly. A new `SlowState.W_conf` accumulates the raw transverse slip work weighted by contact pressure `(p/p_ref)**n`; `conformation_gate(state,mat) = W_conf_ref/(W_conf+W_conf_ref)` multiplies the slip-driven `dF_0` inside `WearLoss` (on `d_wear`) and `RotationalLooseningLoss` (on `d_theta`). Conservation is `dF_0`-only (keep `dE`), reusing the proven `U_released` balance. `W_conf_ref <= 0` ⇒ gate ≡ 1 (inert).

**Tech Stack:** Python 3, numpy, pytest. No new dependencies.

## Model tiering & swaps (session on Opus 4.8 max effort)

Engine + tests, **no scientific conclusion is produced here** (that's Plan B). So **no Fable**.

| Task | Implementer | Task reviewer |
|---|---|---|
| 1 (`conformation_gate` + fields) | sonnet | sonnet |
| 2 (wire gate + `W_conf` accumulation + engine tests) | sonnet | sonnet |
| 3 (registry rule + predicate) | sonnet | sonnet |
| Final whole-branch review | **opus** (touches the core loss path + conservation) | — |

## Global Constraints

- All file I/O uses `encoding='utf-8'`.
- Syntax-check every `.py` edit before testing: `python -c "import ast; ast.parse(open('PATH', encoding='utf-8').read()); print('OK')"`.
- **Never `git add -A`.** Explicit file lists only. Foreign untracked files `New_Theory/Materiais_Metalicos_EPL_Gb.docx` and `crash_log.txt` are the user's WIP — never stage/touch/discard them.
- Commits in Portuguese, no accents, ending with the trailer `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- **Default-inert is the load-bearing invariant:** `W_conf_ref` defaults to `0.0` ⇒ `conformation_gate ≡ 1.0` and `W_conf` never accumulates ⇒ the full 18-file V2 calibration suite must stay green with unchanged counts. Run it in the final review.
- `tests/conftest.py` puts `src/` on `sys.path`.
- Mirror the existing idioms: the gate is a module-level function like `slip_onset_gate` (line ~301); `W_conf` accumulates in `step_cycle` alongside `W_slip_acc` (the §4.6 block, ~line 857-866); `RotationalLooseningLoss` is **torque-driven** and ignores `slip_amp_override`, so the gate is the only uniform coupling.

---

### Task 1: `conformation_gate` + state/material fields (inert by default)

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` — `JointMaterial` (after `slip_onset_sharpness`, ~line 170), `SlowState` (after `W_slip_acc`, ~line 188), and a new `conformation_gate` function (after `slip_onset_gate`, ~line 318).
- Test: `tests/test_pressure_conformation.py` (new).

**Interfaces:**
- Produces: `JointMaterial.W_conf_ref` (float, default 0.0), `.conform_pressure_exp` (float, default 1.0), `.p_ref_conform` (float, default 5.0e8); `SlowState.W_conf` (float, default 0.0); `conformation_gate(state, mat) -> float` returning `1.0` when `W_conf_ref <= 0` else `W_conf_ref/(W_conf+W_conf_ref)` ∈ (0,1].

- [ ] **Step 1: Write the failing unit tests** — create `tests/test_pressure_conformation.py`:

```python
"""Conformacao dependente de pressao (spec 2026-07-04). Unidade + engine."""
import numpy as np
import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    conformation_gate,
)

M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)


def _run(mat, F0, n_cycles, delta=0.5e-3):
    ana = DynamicStiffnessAnalyzer(M16, mat, F0)
    r = [1.0]
    for _ in range(n_cycles):
        ana.step_cycle(20e3, np.pi / 2, 0.5, delta_amp=delta)
        r.append(max(ana.state.F_0, 0.0) / F0)
    return ana, np.array(r)


def test_gate_inert_when_ref_nonpositive():
    mat = JointMaterial()  # W_conf_ref default 0.0
    for w in (0.0, 1e3, 1e9):
        assert conformation_gate(SlowState(F_0=50e3, W_conf=w), mat) == 1.0


def test_gate_closes_monotonically_with_conformation():
    mat = JointMaterial(W_conf_ref=1e4)
    g0 = conformation_gate(SlowState(F_0=50e3, W_conf=0.0), mat)
    ghalf = conformation_gate(SlowState(F_0=50e3, W_conf=1e4), mat)
    ghi = conformation_gate(SlowState(F_0=50e3, W_conf=1e6), mat)
    assert g0 == pytest.approx(1.0)
    assert ghalf == pytest.approx(0.5)
    assert ghi < 0.05
    assert g0 > ghalf > ghi > 0.0
```

- [ ] **Step 2: Run to verify failure** — `python -m pytest tests/test_pressure_conformation.py -v`. Expected: `ImportError` (`conformation_gate` not defined).

- [ ] **Step 3: Add the fields and the gate.**

In `JointMaterial`, immediately after `slip_onset_sharpness: float = 4.0`:
```python

    # ========================================================
    # Conformacao dependente de pressao (sobretorque, spec 2026-07-04).
    # W_conf cresce do trabalho de slip cru ponderado por (p/p_ref)^n
    # (p = F_0/A_contact); conformation_gate = W_conf_ref/(W_conf+W_conf_ref)
    # suprime a perda de preload slip-driven (wear + loosening) conforme o
    # contato de alta pressao se conforma. Pressure-gated => inerte em baixa
    # pre-carga. W_conf_ref<=0 => gate=1 (inativo, backward-compat exato).
    # ========================================================
    W_conf_ref: float = 0.0             # J — escala de conformacao (0 = off)
    conform_pressure_exp: float = 1.0   # n — expoente de pressao [-]
    p_ref_conform: float = 5.0e8        # Pa — pressao de contato de referencia
```

In `SlowState`, immediately after the `W_slip_acc` field (and its comment):
```python
    W_conf: float = 0.0              # J — trabalho de conformacao acumulado
                                     #     (pressure-weighted; driver do
                                     #      conformation_gate)
```

After the `slip_onset_gate` function (before `F_slip_transverse`):
```python
def conformation_gate(state: SlowState, mat: JointMaterial) -> float:
    """Gate de conformacao dependente de pressao (spec 2026-07-04 §4).

    Retorna g in (0,1] que MULTIPLICA a perda de pre-carga slip-driven
    (wear + loosening rotacional). Conforme o trabalho de conformacao
    acumulado (``state.W_conf``, ponderado por pressao) cresce, g -> 0 e o
    afrouxamento slip-driven se arresta (plato do sobretorque). Espelha
    ``slip_onset_gate`` mas FECHANDO (1 -> 0). Com ``W_conf_ref <= 0`` retorna
    1.0 exato (mecanismo inativo, backward-compat).
    """
    if mat.W_conf_ref <= 0.0:
        return 1.0
    return float(mat.W_conf_ref / (max(state.W_conf, 0.0) + mat.W_conf_ref))
```

- [ ] **Step 4: Run to verify pass** — `python -m pytest tests/test_pressure_conformation.py -v`. Expected: 2 passed.

- [ ] **Step 5: Syntax-check and commit.**
```bash
python -c "import ast; ast.parse(open('src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py', encoding='utf-8').read()); print('OK')"
git add src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py tests/test_pressure_conformation.py
git commit -m "conformacao: conformation_gate + campos W_conf/W_conf_ref (inerte por default)" -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Wire the gate + accumulate `W_conf` in `step_cycle`

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` — `WearLoss.rate` (after the `slip_onset_gate` line, ~607), `RotationalLooseningLoss.rate` (the `d_theta = ...` line, ~676), `step_cycle` (after the `W_slip_acc` update, ~866).
- Test: `tests/test_pressure_conformation.py` (append).

**Interfaces:**
- Consumes: `conformation_gate` (Task 1), `mu_bearing_eff`, `SlowState.W_conf`, `_slip_acc` (the raw slip already computed at ~line 861 in `step_cycle`).
- Produces: `WearLoss`/`RotationalLooseningLoss` `dF_0` scaled by the gate; `state.W_conf` accumulated per cycle (guarded by `W_conf_ref > 0`).

- [ ] **Step 1: Write the failing engine tests** — append to `tests/test_pressure_conformation.py`:

```python
def test_inert_by_default_leaves_state_untouched():
    ana, r = _run(JointMaterial(), 50e3, 300)
    assert ana.state.W_conf == 0.0                        # accumulator off
    assert conformation_gate(ana.state, ana.mat) == 1.0   # gate never bites
    assert 0.0 < r[-1] < 1.0                               # normal loosening still happens


def test_conformation_arrests_loosening_at_high_pressure():
    F0 = 132.8e3
    ctrl, r_ctrl = _run(JointMaterial(), F0, 2500)                    # no conformation
    conf, r_conf = _run(JointMaterial(W_conf_ref=1e4), F0, 2500)      # active
    assert conf.state.W_conf > 0.0                        # accumulated
    assert conformation_gate(conf.state, conf.mat) < 0.5  # substantially closed
    assert r_conf[-1] > r_ctrl[-1] + 0.2                  # plateau vs runaway


def test_conformation_does_not_degrade_conservation():
    ctrl, _ = _run(JointMaterial(), 132.8e3, 1500)
    conf, _ = _run(JointMaterial(W_conf_ref=1e4), 132.8e3, 1500)
    assert abs(conf.energy.conservation_residual) <= abs(ctrl.energy.conservation_residual) + 1.0


def test_pressure_gates_regime_separation():
    # SAME constants; only F0 (pressure) differs => nova ~inert, sobretorque locks
    mat = dict(W_conf_ref=5e4, conform_pressure_exp=2.0)
    nova, _ = _run(JointMaterial(**mat), 50e3, 2500)
    sob, _ = _run(JointMaterial(**mat), 132.8e3, 2500)
    g_nova = conformation_gate(nova.state, JointMaterial(**mat))
    g_sob = conformation_gate(sob.state, JointMaterial(**mat))
    assert g_nova > g_sob + 0.3   # pressure separates the regimes
    assert g_sob < 0.6            # sobretorque conforms
```

- [ ] **Step 2: Run to verify failure** — `python -m pytest tests/test_pressure_conformation.py -v`. Expected: the four new tests FAIL (`W_conf` never accumulates and the gate isn't wired, so `arrests`/`separation` fail; `inert_by_default` passes already).

- [ ] **Step 3: Wire the gate into the two slip-driven mechanisms.**

In `WearLoss.rate`, immediately after `d_wear *= slip_onset_gate(state, mat)`:
```python
        # Conformacao dependente de pressao (spec 2026-07-04 §4/§5): suprime a
        # perda de preload por wear conforme o contato de alta pressao se
        # conforma. Gate dF_0 (NAO dE — mesmo padrao do slip_onset). g=1 se
        # W_conf_ref<=0 (backward-compat exato).
        d_wear *= conformation_gate(state, mat)
```

In `RotationalLooseningLoss.rate`, replace the single line
```python
        d_theta = g * k_scale * slip_fraction * (T_loose - T_resist) / max(k_torsional, 1.0)
```
with
```python
        # g = incubacao (slip_onset); conformation_gate = arresto por
        # conformacao de alta pressao (spec 2026-07-04). Ambos gateiam d_theta,
        # logo dF_0 E o dE derivado (=T_resist*d_theta).
        d_theta = (g * conformation_gate(state, mat) * k_scale * slip_fraction
                   * (T_loose - T_resist) / max(k_torsional, 1.0))
```

- [ ] **Step 4: Accumulate `W_conf` in `step_cycle`.** Immediately after the `self.state.W_slip_acc += (...)` block (the §4.6 comment block), add:
```python
        # ===== 4.7) Acumula trabalho de conformacao (pressure-weighted), driver
        # do conformation_gate (spec 2026-07-04). Mesmo slip cru de 4.6,
        # ponderado por (p/p_ref)^n, p = F_0/A_contact. Guardado por
        # W_conf_ref>0 => W_conf fica 0.0 exato quando inativo (backward-compat).
        if self.mat.W_conf_ref > 0.0:
            p = max(self.state.F_0, 0.0) / max(self.geom.A_contact, 1e-12)
            pw = (p / self.mat.p_ref_conform) ** self.mat.conform_pressure_exp
            self.state.W_conf += pw * (
                4.0 * mu_bearing_eff(self.state, self.mat)
                * max(self.state.F_0, 0.0) * max(_slip_acc, 0.0))
```

- [ ] **Step 5: Run to verify pass** — `python -m pytest tests/test_pressure_conformation.py -v`. Expected: all tests pass (6). If `test_conformation_arrests_loosening_at_high_pressure` shows no arrest, do **not** invent numbers — report it (it would mean the wiring is wrong, since a closed gate must reduce `d_wear`/`d_theta`).

- [ ] **Step 6: Syntax-check and commit.**
```bash
python -c "import ast; ast.parse(open('src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py', encoding='utf-8').read()); print('OK')"
git add src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py tests/test_pressure_conformation.py
git commit -m "conformacao: gate em WearLoss+RotationalLoosening (dF_0) + acumula W_conf no step_cycle" -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Activation-registry rule (`_pressao_elevada`)

**Files:**
- Modify: `src/bolt_analysis_studio/calibration/parameter_registry.py` — add the `_pressao_elevada` predicate (after `_aperto_por_torque`, ~line 76) and three `ParameterRule`s to `PARAMETER_REGISTRY` (~after line 116).
- Test: `tests/test_parameter_registry.py` (append; read it first for the fixture style — it imports from `bolt_analysis_studio.calibration.parameter_registry` and constructs `ConditionSpec`s).

**Interfaces:**
- Consumes: `LoadingRegime.F0_provenance`, `active_candidates(bounds, priors, conditions, theta, estimated)`.
- Produces: `W_conf_ref` and `conform_pressure_exp` offered by `active_candidates` **only** when a condition has `F0_provenance in ("estimated","torque")`; `p_ref_conform` never fittable; and no `KeyError` when `W_conf_ref` is in bounds+priors (the rule now exists).

- [ ] **Step 1: Write the failing test** — append to `tests/test_parameter_registry.py`:

```python
def test_conformation_offered_only_under_elevated_pressure():
    import numpy as np
    from bolt_analysis_studio.calibration.shared_calibrator import ConditionSpec
    from bolt_analysis_studio.calibration.parameter_registry import active_candidates

    bounds = {"W_conf_ref": (1e2, 1e8), "K_archard": (1e-5, 1e-3)}
    priors = {"W_conf_ref": 1e4, "K_archard": 1e-4}

    def cond(name):
        return ConditionSpec(name=name, curves=[], F0_init=50e3,
                             F_amp=20e3, delta_amp=0.5e-3)

    # all-nominal dataset: W_conf_ref NOT offered (K_archard still is, transversal)
    nom = active_candidates(bounds, priors, [cond("nova")], np.pi / 2, set())
    assert "W_conf_ref" not in nom
    assert "K_archard" in nom

    # over-torque present (F0 estimated): W_conf_ref offered
    ot = active_candidates(bounds, priors,
                           [cond("nova"), cond("sobretorque")],
                           np.pi / 2, {"sobretorque"})
    assert "W_conf_ref" in ot
```

- [ ] **Step 2: Run to verify failure** — `python -m pytest tests/test_parameter_registry.py::test_conformation_offered_only_under_elevated_pressure -v`. Expected: FAIL — with `W_conf_ref` in bounds+priors but no fittable rule, `active_candidates` raises `KeyError` (the loud-by-design guard). That failure confirms the guard; Step 3 adds the rule.

- [ ] **Step 3: Add the predicate and rules.**

After `_aperto_por_torque`:
```python
def _pressao_elevada(r: LoadingRegime) -> bool:
    # Conformacao slip-driven so e excitada sob pressao de contato elevada
    # (over-torque). Proxy no dataset compartilhado: F0 nao-nominal (estimado
    # ou por torque) => pre-carga elevada. Este predicado e o gate de OFERTA
    # ao otimizador; o pressure-weighting no engine e o gate fino (inerte em
    # F0 nominal de qualquer forma).
    return r.F0_provenance in ("estimated", "torque")
```

Inside the `PARAMETER_REGISTRY` tuple, after the incubation rules (`slip_onset_sharpness`):
```python
    # --- conformacao dependente de pressao (sobretorque, spec 2026-07-04) ---
    ParameterRule("W_conf_ref", "physical", True, _pressao_elevada,
                  "conformacao slip-driven excitada so sob pressao de contato "
                  "elevada (over-torque); inerte em F0 nominal"),
    ParameterRule("conform_pressure_exp", "physical", True, _pressao_elevada,
                  "expoente de pressao da conformacao"),
    ParameterRule("p_ref_conform", "physical", False, _pressao_elevada,
                  "pressao de contato de referencia (input, nao fitado)"),
```

- [ ] **Step 4: Run to verify pass** — `python -m pytest tests/test_parameter_registry.py -v`. Expected: the new test passes and the existing registry-truth tests stay green.

- [ ] **Step 5: Syntax-check and commit.**
```bash
python -c "import ast; ast.parse(open('src/bolt_analysis_studio/calibration/parameter_registry.py', encoding='utf-8').read()); print('OK')"
git add src/bolt_analysis_studio/calibration/parameter_registry.py tests/test_parameter_registry.py
git commit -m "registry: regra _pressao_elevada oferta W_conf_ref/conform_pressure_exp so em over-torque" -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review (controller, after all tasks)

- **Spec coverage:** §4 gate/coupling (T1+T2), §5 conservation dF_0-only (T2 test), §6 default-inert (T1/T2), §8 engine + registry integration (T1-T3), §10 tests (T1-T3). The §9 calibration/validation + §4.9 writeup are **out of scope → Plan B.** ✅
- **Default-inert invariant:** `W_conf_ref=0` ⇒ gate≡1 (T1 test) + `W_conf` guarded off (T2 test) ⇒ 18-file suite unchanged (final review). ✅
- **Conservation:** `dF_0`-only gate; T2 asserts residual doesn't degrade vs control. ✅
- **Type/name consistency:** `conformation_gate`, `W_conf`, `W_conf_ref`, `conform_pressure_exp`, `p_ref_conform` identical across engine, tests, and registry. ✅
- **Registry KeyError guard:** T3 Step 2 deliberately hits it (proves the guard), Step 3 resolves it. ✅
- **Placeholders:** none — every step carries complete code. The test constants (`W_conf_ref=1e4`/`5e4`, `n=2`) are **test fixtures** chosen to make the arrest/separation visible, not calibrated science (that's Plan B).

## Final review

Dispatch on **opus** (core loss path + conservation). Run the full 18-file V2 calibration suite (`CLAUDE.md` → V2 calibration package tests) + `tests/test_pressure_conformation.py`; expected: prior baseline **unchanged** + the new conformation tests green (default-inert ⇒ no regression).

---

## Follow-up: Plan B (calibration + science) — NOT in this plan

Separate plan/brainstorm: extend `build_shared_config` with `W_conf_ref`/`conform_pressure_exp` bounds+priors, run the shared fit (registry now offers them under over-torque), and validate that **sobretorque MAE drops toward its 0.007 floor while nova/reusada/reaperto hold and residual≈0** — recorded AS IS (partial/failure is a finding, spec §9), then `MODEL_LEGITIMACY.md` §4.9 (Fable). Known subtlety to resolve there: the log-prior regularization pulls `W_conf_ref` toward its prior, and the forward-selection baseline uses priors for non-free constants — so the prior choice interacts with whether the mechanism activates without over-suppressing nova (spec §7's raw-vs-equilibrium fallback is the lever if `n` can't separate the regimes). That's why calibration is its own plan.
