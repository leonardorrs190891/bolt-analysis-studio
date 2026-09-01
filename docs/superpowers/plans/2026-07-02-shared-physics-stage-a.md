# Shared-Physics Calibration (Stage A) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One set of physical constants, fitted jointly across all 4 M16 shear conditions, with conditions differing only by named measurable states — proving the V2 model is an analytical model, not a per-curve fit.

**Architecture:** Stage A of `docs/superpowers/specs/2026-07-02-shared-physics-model-design.md`. Non-breaking: tuners stay in the API but are frozen ≡ 1.0 and never fitted. Adds (1) a state-based EmbeddingLoss + `initial_embedding_frac`, (2) a `SharedCalibrator` that fits physical constants in log-space with literature priors over all conditions at once, plus leave-one-condition-out (LOCO) validation, (3) the `calibrate_shared.py` science run, (4) identifiability of the shared fit, (5) doc updates + the A→B gate verdict. **Stage B (tuner-layer removal) is a separate plan, written only after the §2.8 gate is evaluated.**

**Tech Stack:** Python 3, numpy, scipy.optimize.least_squares (trf), matplotlib, pytest. No new dependencies.

## Global Constraints

- All file I/O with `encoding='utf-8'` (Windows charmap gotcha, CLAUDE.md).
- After every `.py` edit run the syntax check: `python -c "import ast; ast.parse(open('PATH', encoding='utf-8').read()); print('OK')"`.
- Tuners (`k_*_scale`, `Phi_*_correction`, `k_damage_scale`) are NEVER fitted in Stage A — they stay at their default 1.0 (spec §2.1).
- Named states are fixed inputs: `D_init=0.3` (reusada, reaperto), `emb_consumed_frac=1.0` (reusada). Only `F0_test` of sobretorque is estimated (fallback spec §2.3), bounds `[40e3, 120e3]` N, sanity `≤ 0.9·940e6·157e-6 ≈ 133 kN`.
- Forward selection: `tol=0.005` (spec §2.2). Fitted-number budget is **≤5 TOTAL dataset-wide** (spec §5.1): the estimated `F0_test` counts as 1, so the science run uses `max_constants=4`. Regularization `lambda_reg=0.001` as log-prior `√λ·(ln p − ln p_default)`.
- Physical-constant bounds (spec §2.2): `emb_depth [5e-6, 80e-6]`, `N_emb [10, 200]`, `K_archard [1e-5, 1e-3]`, `C_creep [1e-12, 1e-9]`, `tr_loose_gain [0.5, 10]`, `c_D [0.5, 8]`, `k_dmg_wear [0.5, 8]`.
- Fitting is in log-space (constants are positive and span decades).
- Global MAE weights conditions equally (mean over per-condition MAE), so single-curve conditions (TP6, TP7) are not drowned by nova's 4 curves. Residuals are weighted `err / (√len(curve) · √n_curves_of_condition)` for the same reason.
- Commit messages: Portuguese without accents, prefix style (`v2:`, `calib:`, `docs:`, `test:`), and end with the `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>` trailer.
- Tests run as `python -m pytest tests/<file> -v` from the repo root (`tests/conftest.py` puts `src/` on `sys.path`).
- Existing calibration suite that must stay green: `python -m pytest tests/test_surface_damage.py tests/test_staged_calibrator.py tests/test_calibration_segmentation.py tests/test_calibration_decomposition.py tests/test_calibration_profiles.py tests/test_calibration_server.py tests/test_v2_solver_preload.py tests/test_slip_onset_incubation.py tests/test_case_study_models.py tests/test_calibration_trim.py tests/test_v2_calibration.py` (slow — several minutes; run at the checkpoints where a task says so, not after every step).

## File Structure

| File | Responsibility |
|---|---|
| `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (modify) | `EmbeddingLoss.rate` → state-based geometric form; `DynamicStiffnessAnalyzer.__init__` gains `initial_embedding_frac` |
| `src/bolt_analysis_studio/calibration/profiles.py` (modify) | add `upsert_shared()` — writes the `shared` block + `schema: 2`, preserving `profiles` |
| `src/bolt_analysis_studio/calibration/shared_calibrator.py` (create) | `ConditionSpec`, `SharedCalibrationConfig`, `SharedCalibrator` (`fit_parsimonious`, `loco`) |
| `src/bolt_analysis_studio/calibration/__init__.py` (modify) | export the new names |
| `New_Theory/calibrate_shared.py` (create) | the science run: builds config, fits, LOCO, PNG, saves `shared` block |
| `New_Theory/identifiability_analysis.py` (modify) | `--shared` mode: sloppiness + CIs of the shared fit |
| `New_Theory/MODEL_LEGITIMACY.md` (modify) | §4.5 shared-fit results + gate verdict + changelog |
| `CLAUDE.md` (modify) | commands, shared-calibration summary, gotchas |
| `tests/test_embedding_state_based.py` (create) | embedding form: closed-form exactness, scale semantics, consumed fraction |
| `tests/test_shared_block_persistence.py` (create) | `upsert_shared` round-trip |
| `tests/test_shared_calibrator.py` (create) | synthetic recovery, F0 estimation, LOCO |

---

### Task 1: State-based EmbeddingLoss + `initial_embedding_frac`

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (class `EmbeddingLoss`, ~line 524; `DynamicStiffnessAnalyzer.__init__`, ~line 702)
- Test: `tests/test_embedding_state_based.py` (create)

**Interfaces:**
- Consumes: existing `SlowState.delta_emb`, `JointMaterial.emb_depth/N_emb/k_emb_scale`, `JointGeometry.k_b`.
- Produces: `DynamicStiffnessAnalyzer(geometry, material, initial_preload, loss_mechanisms=None, initial_damage=0.0, initial_embedding_frac=0.0)` — new keyword-compatible parameter appended last (old positional calls unaffected). `EmbeddingLoss.rate` unchanged signature, new internal form.

**Why this form** (spec §2.4): the geometric increment `dδ = (target − δ_emb)·(1 − e^(−1/N_emb))` reproduces Norton's closed form `δ(N) = target·(1 − e^(−N/N_emb))` **exactly** at integer cycles (the old clock-based increment only approximated it), and makes a non-zero initial embedding state (reused washer) representable. `target = k_emb_scale·emb_depth` preserves the legacy tuner semantics (the tuner scaled the *asymptote*) so existing calibrated profiles keep their meaning until Stage B.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_embedding_state_based.py`:

```python
"""Embedding state-based (forma geometrica exata) — spec 2026-07-02 §2.4."""
import numpy as np
import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, EmbeddingLoss, JointGeometry, JointMaterial,
    SlowState,
)

GEOM = JointGeometry()


def _iterate_embedding(mat, n_cycles, delta_emb0=0.0):
    """Aplica so o EmbeddingLoss.rate ciclo a ciclo (unit-level)."""
    state = SlowState(F_0=50e3, F_0_init=50e3, delta_emb=delta_emb0)
    mech = EmbeddingLoss()
    for n in range(1, n_cycles + 1):
        r = mech.rate(state, GEOM, mat, 0.0, np.pi / 2, 0.5, n)
        state.delta_emb += r["ds"]["delta_emb"]
    return state.delta_emb


def test_virgin_trajectory_matches_norton_closed_form_exactly():
    mat = JointMaterial()
    for n_check in (1, 10, 50, 150, 300):
        got = _iterate_embedding(mat, n_check)
        expected = mat.emb_depth * (1.0 - np.exp(-n_check / mat.N_emb))
        assert got == pytest.approx(expected, rel=1e-9), f"N={n_check}"


def test_k_emb_scale_scales_the_asymptote_legacy_semantics():
    # k_emb_scale=0.18 (perfil reusada legado) => assintota 0.18*emb_depth,
    # NAO 1.0*emb_depth mais devagar.
    mat = JointMaterial(k_emb_scale=0.18)
    got = _iterate_embedding(mat, int(20 * mat.N_emb))
    assert got == pytest.approx(0.18 * mat.emb_depth, rel=1e-4)


def test_initial_embedding_frac_suppresses_embedding_loss():
    mat = JointMaterial()
    fresh = DynamicStiffnessAnalyzer(GEOM, mat, 50e3,
                                     loss_mechanisms=[EmbeddingLoss()])
    used = DynamicStiffnessAnalyzer(GEOM, mat, 50e3,
                                    loss_mechanisms=[EmbeddingLoss()],
                                    initial_embedding_frac=1.0)
    assert used.state.delta_emb == pytest.approx(mat.emb_depth, rel=1e-9)
    for _ in range(200):
        fresh.step_cycle(20e3, np.pi / 2, 0.5, delta_amp=0.5e-3)
        used.step_cycle(20e3, np.pi / 2, 0.5, delta_amp=0.5e-3)
    drop_fresh = 1.0 - fresh.state.F_0 / 50e3
    drop_used = 1.0 - used.state.F_0 / 50e3
    assert drop_fresh > 0.0
    assert drop_used < 0.05 * drop_fresh  # embedding ja consumido: quase nada


def test_default_frac_zero_is_backward_compatible():
    # Sem o novo arg, delta_emb parte de 0 e a assinatura antiga funciona
    # (initial_damage continua sendo o 5o argumento posicional).
    ana = DynamicStiffnessAnalyzer(GEOM, JointMaterial(), 50e3, None, 0.2)
    assert ana.state.D == pytest.approx(0.2)
    assert ana.state.delta_emb == 0.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_embedding_state_based.py -v`
Expected: `test_virgin_trajectory_matches_norton_closed_form_exactly` FAILS (old increment form deviates from closed form beyond rel=1e-9), `test_k_emb_scale_scales_the_asymptote_legacy_semantics` FAILS, `test_initial_embedding_frac_suppresses_embedding_loss` FAILS with `TypeError: __init__() got an unexpected keyword argument 'initial_embedding_frac'`.

- [ ] **Step 3: Implement the new EmbeddingLoss form**

In `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py`, replace the body of `EmbeddingLoss` (keep the class position, ~line 524):

```python
class EmbeddingLoss(LossMechanism):
    """Embedding plástico das asperezas. Domina nos primeiros ~N_emb ciclos.

    Forma state-based (decaimento geométrico exato, spec 2026-07-02 §2.4):
    o incremento depende da profundidade ainda disponível, não do relógio de
    ciclos. Para junta virgem reproduz EXATAMENTE a forma fechada de Norton
        δ_emb(N) = δ_target·(1 − e^{−N/N_emb}),
    e permite estado inicial não-nulo (arruela reusada, emb_consumed_frac>0).
    δ_target = k_emb_scale·emb_depth preserva a semântica legada do tuner
    (assíntota escalada) até a remoção da camada de tuners (Estágio B).
    """
    name = "embedding"

    def rate(self, state, geom, mat, F_amp, theta_load, freq, cycle_N,
             slip_amp_override=None):
        target = mat.k_emb_scale * mat.emb_depth
        remaining = max(target - state.delta_emb, 0.0)
        d_delta = remaining * (1.0 - np.exp(-1.0 / mat.N_emb))
        # Perda de preload: ΔF_0 = −k_b · Δδ (encurtamento da pilha)
        dF_0 = -geom.k_b * d_delta
        # Trabalho plástico = F_clamp · Δδ
        dE = max(state.F_0, 0.0) * d_delta
        return dict(dF_0=dF_0, dE_dissipated=dE,
                    ds=dict(delta_emb=d_delta))
```

- [ ] **Step 4: Add `initial_embedding_frac` to the analyzer constructor**

In the same file, change `DynamicStiffnessAnalyzer.__init__` (~line 702) — new parameter appended after `initial_damage`, and `delta_emb` seeded in the `SlowState` call:

```python
    def __init__(self,
                 geometry: JointGeometry,
                 material: JointMaterial,
                 initial_preload: float,
                 loss_mechanisms: Optional[List[LossMechanism]] = None,
                 initial_damage: float = 0.0,
                 initial_embedding_frac: float = 0.0):
        self.geom = geometry
        self.mat = material
        self.state = SlowState(F_0=initial_preload,
                               F_0_init=initial_preload,
                               D=initial_damage,
                               delta_emb=(initial_embedding_frac
                                          * material.k_emb_scale
                                          * material.emb_depth))
```

(The rest of `__init__` is unchanged.)

- [ ] **Step 5: Syntax check + run the new tests**

Run: `python -c "import ast; ast.parse(open('src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py', encoding='utf-8').read()); print('OK')"`
Run: `python -m pytest tests/test_embedding_state_based.py -v`
Expected: 4 PASS.

- [ ] **Step 6: Run the full calibration suite (regression checkpoint)**

Run: `python -m pytest tests/test_surface_damage.py tests/test_staged_calibrator.py tests/test_calibration_segmentation.py tests/test_calibration_decomposition.py tests/test_calibration_profiles.py tests/test_calibration_server.py tests/test_v2_solver_preload.py tests/test_slip_onset_incubation.py tests/test_case_study_models.py tests/test_calibration_trim.py tests/test_v2_calibration.py -x -q`
Expected: all PASS. The embedding trajectory shift vs the old increment is ≤ ~1% of `emb_depth` (the new form is the exact closed form; the old one approximated it), which is far below the MAE tolerances asserted in these tests. If any assertion fails by a hair (< 0.005 MAE), the fix is to relax that single tolerance with a comment pointing at spec §2.4 — do NOT revert the form.

- [ ] **Step 7: Commit**

```bash
git add src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py tests/test_embedding_state_based.py
git commit -m "v2: embedding state-based (forma geometrica exata) + initial_embedding_frac

Forma nova reproduz exatamente a forma fechada de Norton e permite
estado inicial de embedding consumido (arruela reusada). Spec
2026-07-02-shared-physics-model-design §2.4.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: `upsert_shared` persistence (schema 2 block)

**Files:**
- Modify: `src/bolt_analysis_studio/calibration/profiles.py`
- Test: `tests/test_shared_block_persistence.py` (create)

**Interfaces:**
- Consumes: existing `load_profiles(path) -> dict`, `save_profiles(path, data) -> None`.
- Produces: `upsert_shared(path: PathLike, shared: dict) -> dict` — sets `data["schema"] = 2` and `data["shared"] = shared`, preserves any existing `profiles` block, atomic save, returns the full dict.

- [ ] **Step 1: Write the failing test**

Create `tests/test_shared_block_persistence.py`:

```python
"""Bloco `shared` (schema 2) no joint_calibrations.json — spec 2026-07-02 §2.6."""
import json

from bolt_analysis_studio.calibration.profiles import (
    load_profiles, save_profiles, upsert_shared,
)


def test_upsert_shared_preserves_profiles_and_sets_schema(tmp_path):
    path = tmp_path / "joint_calibrations.json"
    save_profiles(path, {"profiles": {"nova": {"tuners": {"k_emb_scale": 1.0}}}})

    shared = {
        "calibrated_at": "2026-07-02",
        "free_constants": ["K_archard"],
        "constants": {"K_archard": 2e-4},
        "conditions": {
            "sobretorque": {
                "states": {"F0_test_N": 71000.0, "F0_provenance": "estimated"},
                "MAE": 0.02,
            },
        },
        "loco": {"sobretorque": {"MAE_pred": 0.03}},
    }
    upsert_shared(path, shared)

    data = load_profiles(path)
    assert data["schema"] == 2
    assert data["shared"]["constants"]["K_archard"] == 2e-4
    assert data["shared"]["conditions"]["sobretorque"]["states"]["F0_provenance"] == "estimated"
    # bloco antigo intocado (GUI continua lendo profiles no Estagio A)
    assert data["profiles"]["nova"]["tuners"]["k_emb_scale"] == 1.0
    # arquivo e json valido em utf-8
    assert json.loads(path.read_text(encoding="utf-8"))["schema"] == 2


def test_upsert_shared_on_missing_file_creates_it(tmp_path):
    path = tmp_path / "new.json"
    upsert_shared(path, {"constants": {}})
    data = load_profiles(path)
    assert data["schema"] == 2
    assert data["shared"] == {"constants": {}}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_shared_block_persistence.py -v`
Expected: FAIL with `ImportError: cannot import name 'upsert_shared'`.

- [ ] **Step 3: Implement `upsert_shared`**

Append to `src/bolt_analysis_studio/calibration/profiles.py`:

```python
def upsert_shared(path: PathLike, shared: dict) -> dict:
    """Grava/atualiza o bloco `shared` (calibracao de fisica compartilhada,
    spec 2026-07-02 §2.6) e marca schema 2. O bloco `profiles` legado e
    preservado (o GUI continua lendo profiles durante o Estagio A)."""
    data = load_profiles(path)
    data["schema"] = 2
    data["shared"] = shared
    save_profiles(path, data)
    return data
```

- [ ] **Step 4: Syntax check + run tests**

Run: `python -c "import ast; ast.parse(open('src/bolt_analysis_studio/calibration/profiles.py', encoding='utf-8').read()); print('OK')"`
Run: `python -m pytest tests/test_shared_block_persistence.py tests/test_calibration_profiles.py -v`
Expected: all PASS (the existing profiles tests prove `profiles` handling is untouched).

- [ ] **Step 5: Commit**

```bash
git add src/bolt_analysis_studio/calibration/profiles.py tests/test_shared_block_persistence.py
git commit -m "calib: bloco shared (schema 2) no joint_calibrations.json

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: `SharedCalibrator` — joint fit of physical constants + LOCO

**Files:**
- Create: `src/bolt_analysis_studio/calibration/shared_calibrator.py`
- Modify: `src/bolt_analysis_studio/calibration/__init__.py` (add exports)
- Test: `tests/test_shared_calibrator.py` (create)

**Interfaces:**
- Consumes: `DynamicStiffnessAnalyzer(geom, mat, F0, initial_damage=..., initial_embedding_frac=...)` from Task 1; `JointGeometry`, `JointMaterial`.
- Produces (used by Tasks 4–5):
  - `PHYSICAL_PRIORS: Dict[str, float]`
  - `ConditionSpec(name, curves, F0_init, F_amp, delta_amp, D_init=0.0, emb_consumed_frac=0.0, damage_active=False)`
  - `SharedCalibrationConfig(geom, conditions, theta, freq, n_cycles, bounds, priors=..., lambda_reg=0.001, estimate_F0={}, W_ref=1e4, k_dmg_mu=1.0, max_nfev=40)`
  - `SharedCalibrator(config)` with:
    - `.constants: Dict[str, float]`, `.F0_estimates: Dict[str, float]`
    - `._residuals(x, free_consts, f0_names)` (log-space; reused by the identifiability script)
    - `._fit_subset(free_consts: List[str]) -> None`
    - `.mae_by_condition() -> Dict[str, float]`, `.global_mae() -> float`
    - `.fit_parsimonious(tol=0.005, max_constants=5) -> dict` with keys `free_constants, constants, F0_estimates, mae_global, mae_by_condition, selection_history`
    - `.loco(free_constants: List[str]) -> dict` mapping condition name → `{"MAE_pred": float, "state_F0_from_full_fit": bool}`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_shared_calibrator.py`:

```python
"""SharedCalibrator: UMA fisica, N estados — spec 2026-07-02 §2.5.

Testes sinteticos rapidos (n_cycles=300, poucas constantes livres): geram
curvas do proprio modelo com constantes conhecidas + ruido e verificam
recuperacao / estimacao de F0 / LOCO.
"""
import numpy as np
import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)
from bolt_analysis_studio.calibration.shared_calibrator import (
    ConditionSpec, SharedCalibrationConfig, SharedCalibrator,
)

M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)
N_CYC = 300
NOISE = 0.005


def _synth_curve(name, K_archard, F0_true, seed):
    """Gera uma curva F/F0 do proprio modelo (constante de wear conhecida)."""
    mat = JointMaterial(K_archard=K_archard)
    ana = DynamicStiffnessAnalyzer(M16, mat, F0_true)
    ratio = [1.0]
    for _ in range(N_CYC):
        ana.step_cycle(20e3, np.pi / 2, 0.5, delta_amp=0.5e-3)
        ratio.append(max(ana.state.F_0, 0.0) / F0_true)
    cycles = np.linspace(0.0, N_CYC, 15)
    ref = np.interp(cycles, np.arange(N_CYC + 1), np.array(ratio))
    rng = np.random.default_rng(seed)
    return {"name": name, "cycles": cycles,
            "ratio": ref + rng.normal(0.0, NOISE, ref.shape)}


def _cond(name, K_archard, F0_true=50e3, F0_declared=None, seed=0):
    return ConditionSpec(
        name=name,
        curves=[_synth_curve(name, K_archard, F0_true, seed)],
        F0_init=F0_declared if F0_declared is not None else F0_true,
        F_amp=20e3, delta_amp=0.5e-3)


def _config(conds, bounds, estimate_F0=None):
    return SharedCalibrationConfig(
        geom=M16, conditions=conds, theta=np.pi / 2, freq=0.5,
        n_cycles=N_CYC, bounds=bounds,
        estimate_F0=estimate_F0 or {}, max_nfev=25)


def test_shared_fit_recovers_wear_constant_across_two_conditions():
    K_true = 1.6e-4   # 1.6x o prior de literatura (1e-4)
    conds = [_cond("c0", K_true, seed=0), _cond("c1", K_true, seed=1)]
    cal = SharedCalibrator(_config(conds, {"K_archard": (1e-5, 1e-3)}))
    res = cal.fit_parsimonious(tol=0.002, max_constants=2)
    assert "K_archard" in res["free_constants"]
    assert res["constants"]["K_archard"] == pytest.approx(K_true, rel=0.3)
    assert res["mae_global"] <= 4 * NOISE
    # tuners nunca entram: so constantes fisicas no resultado
    assert all(not k.endswith("_scale") for k in res["constants"])


def test_estimate_F0_improves_fit_and_moves_toward_truth():
    # curva gerada a 90 kN mas declarada a 50 kN
    cond = _cond("sobre", 1e-4, F0_true=90e3, F0_declared=50e3, seed=2)

    cal_fixed = SharedCalibrator(_config([cond], {}))
    mae_fixed = cal_fixed.global_mae()

    cal_est = SharedCalibrator(_config([cond], {},
                                       estimate_F0={"sobre": (40e3, 120e3)}))
    cal_est._fit_subset([])           # so o estado F0 (nenhuma constante)
    mae_est = cal_est.global_mae()

    assert mae_est < mae_fixed - 0.005          # estimar F0 melhora o fit
    assert cal_est.F0_estimates["sobre"] > 60e3  # e anda na direcao certa


def test_loco_predicts_held_out_condition_with_shared_physics():
    K_true = 1.6e-4
    conds = [_cond(f"c{i}", K_true, seed=i) for i in range(3)]
    cal = SharedCalibrator(_config(conds, {"K_archard": (1e-5, 1e-3)}))
    res = cal.fit_parsimonious(tol=0.002, max_constants=1)
    loco = cal.loco(res["free_constants"])
    assert set(loco) == {"c0", "c1", "c2"}
    for name, r in loco.items():
        # fisica compartilhada: predicao da condicao retida ~ nivel do ruido
        assert r["MAE_pred"] <= 6 * NOISE, name
        assert r["state_F0_from_full_fit"] is False


def test_fit_is_deterministic():
    conds = [_cond("c0", 1.5e-4, seed=3)]
    cfg = _config(conds, {"K_archard": (1e-5, 1e-3)})
    a = SharedCalibrator(cfg).fit_parsimonious(tol=0.002, max_constants=1)
    b = SharedCalibrator(cfg).fit_parsimonious(tol=0.002, max_constants=1)
    assert a["constants"] == b["constants"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_shared_calibrator.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'bolt_analysis_studio.calibration.shared_calibrator'`.

- [ ] **Step 3: Implement `SharedCalibrator`**

Create `src/bolt_analysis_studio/calibration/shared_calibrator.py`:

```python
"""Calibrador compartilhado (Estagio A, spec 2026-07-02 §2.5): UMA fisica
(constantes do par tribologico) fitada em conjunto sobre TODAS as condicoes;
condicoes diferem apenas por estados nomeados (D_init, emb_consumed_frac, F0).

Tuners (k_*_scale, Phi_*_correction, k_damage_scale) NUNCA sao fitados aqui —
ficam no default 1.0. O fit e em log-espaco (constantes positivas, ordens de
magnitude variadas) com prior de literatura: residuo += sqrt(lambda)*(ln p -
ln p_default), substituindo o pull-to-1 do StagedCalibrator.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Dict, List, Tuple

import numpy as np
from scipy.optimize import least_squares

from ..numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)

# Constantes fisicas que o calibrador conhece + prior de literatura (default).
PHYSICAL_PRIORS: Dict[str, float] = {
    "emb_depth": 30e-6,
    "N_emb": 50.0,
    "K_archard": 1e-4,
    "C_creep": 5e-11,
    "tr_loose_gain": 2.0,
    "c_D": 2.0,          # fisica de dano — so afeta condicoes damage_active
    "k_dmg_wear": 4.0,   # idem
}
_DAMAGE_CONSTANTS = ("c_D", "k_dmg_wear")


@dataclass
class ConditionSpec:
    """Uma condicao experimental: curvas + estados nomeados (inputs fisicos)."""
    name: str
    curves: List[dict]              # [{"name", "cycles", "ratio"}, ...]
    F0_init: float                  # pre-carga do ensaio [N]
    F_amp: float                    # amplitude de forca [N]
    delta_amp: float                # amplitude de deslocamento imposto [m]
    D_init: float = 0.0
    emb_consumed_frac: float = 0.0
    damage_active: bool = False


@dataclass
class SharedCalibrationConfig:
    geom: JointGeometry
    conditions: List[ConditionSpec]
    theta: float
    freq: float
    n_cycles: int
    bounds: Dict[str, Tuple[float, float]]   # bounds das constantes fisicas
    priors: Dict[str, float] = field(
        default_factory=lambda: dict(PHYSICAL_PRIORS))
    lambda_reg: float = 0.001
    # Fallback §2.3: F0 estimado UMA vez — nome da condicao -> (lo, hi) em N.
    estimate_F0: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    # fisica de dano fixa aplicada as condicoes damage_active
    W_ref: float = 1.0e4
    k_dmg_mu: float = 1.0
    max_nfev: int = 40


class SharedCalibrator:
    def __init__(self, config: SharedCalibrationConfig):
        self.cfg = config
        self.constants: Dict[str, float] = dict(config.priors)
        # centro geometrico dos bounds como chute inicial do F0 estimado
        self.F0_estimates: Dict[str, float] = {
            name: float(np.sqrt(lo * hi))
            for name, (lo, hi) in config.estimate_F0.items()}

    # ---- simulacao ----
    def _material(self, cond: ConditionSpec) -> JointMaterial:
        kw = {k: v for k, v in self.constants.items()
              if k not in _DAMAGE_CONSTANTS}
        if cond.damage_active:
            kw.update(c_D=self.constants["c_D"],
                      k_dmg_wear=self.constants["k_dmg_wear"],
                      W_ref=self.cfg.W_ref, k_dmg_mu=self.cfg.k_dmg_mu)
        return JointMaterial(**kw)

    def _F0(self, cond: ConditionSpec) -> float:
        return self.F0_estimates.get(cond.name, cond.F0_init)

    def _run_condition(self, cond: ConditionSpec):
        F0 = self._F0(cond)
        ana = DynamicStiffnessAnalyzer(
            self.cfg.geom, self._material(cond), F0,
            initial_damage=cond.D_init,
            initial_embedding_frac=cond.emb_consumed_frac)
        ratio = [1.0]
        for _ in range(self.cfg.n_cycles):
            ana.step_cycle(cond.F_amp, self.cfg.theta, self.cfg.freq,
                           delta_amp=cond.delta_amp)
            ratio.append(max(ana.state.F_0, 0.0) / F0)
        return np.arange(self.cfg.n_cycles + 1), np.array(ratio)

    # ---- metricas ----
    def mae_by_condition(self) -> Dict[str, float]:
        out = {}
        for cond in self.cfg.conditions:
            sim_N, sim_ratio = self._run_condition(cond)
            maes = [float(np.mean(np.abs(
                np.interp(c["cycles"], sim_N, sim_ratio) - c["ratio"])))
                for c in cond.curves]
            out[cond.name] = float(np.mean(maes))
        return out

    def global_mae(self) -> float:
        """Media sobre CONDICOES (nao curvas): TP6/TP7 pesam igual a nova."""
        by = self.mae_by_condition()
        return float(np.mean(list(by.values())))

    # ---- fit (log-espaco) ----
    def _apply_x(self, x, free_consts: List[str], f0_names: List[str]) -> None:
        for name, xi in zip(free_consts, x[:len(free_consts)]):
            self.constants[name] = float(np.exp(xi))
        for name, xi in zip(f0_names, x[len(free_consts):]):
            self.F0_estimates[name] = float(np.exp(xi))

    def _residuals(self, x, free_consts: List[str], f0_names: List[str]):
        self._apply_x(x, free_consts, f0_names)
        res: List[float] = []
        for cond in self.cfg.conditions:
            sim_N, sim_ratio = self._run_condition(cond)
            w_cond = np.sqrt(max(len(cond.curves), 1))
            for c in cond.curves:
                err = np.interp(c["cycles"], sim_N, sim_ratio) - c["ratio"]
                res.extend(err / (np.sqrt(max(len(err), 1)) * w_cond))
        # prior de literatura em log-espaco (substitui o pull-to-1)
        lam = np.sqrt(self.cfg.lambda_reg)
        for name, xi in zip(free_consts, x[:len(free_consts)]):
            res.append(lam * (xi - np.log(self.cfg.priors[name])))
        return np.array(res) if res else np.array([0.0])

    def _fit_subset(self, free_consts: List[str]) -> None:
        """Fita `free_consts` + os estados F0 configurados (sempre ativos)."""
        f0_names = list(self.cfg.estimate_F0.keys())
        if not free_consts and not f0_names:
            return
        x0, lo, hi = [], [], []
        for name in free_consts:
            x0.append(np.log(self.constants[name]))
            b = self.cfg.bounds[name]
            lo.append(np.log(b[0])); hi.append(np.log(b[1]))
        for name in f0_names:
            x0.append(np.log(self.F0_estimates[name]))
            b = self.cfg.estimate_F0[name]
            lo.append(np.log(b[0])); hi.append(np.log(b[1]))
        result = least_squares(self._residuals, x0, bounds=(lo, hi),
                               args=(free_consts, f0_names), method="trf",
                               xtol=1e-8, ftol=1e-8, diff_step=1e-2,
                               max_nfev=self.cfg.max_nfev)
        # a ultima avaliacao interna nao e necessariamente o otimo — reaplica
        self._apply_x(result.x, free_consts, f0_names)

    def fit_parsimonious(self, tol: float = 0.005,
                         max_constants: int = 5) -> dict:
        """Forward selection sobre CONSTANTES FISICAS: parte dos priors de
        literatura e so libera uma constante se ela cortar o MAE global > tol
        (anti-overfitting, mesma filosofia do StagedCalibrator.fit_parsimonious).
        Estados F0 configurados participam de todo subset (sao estados, nao
        candidatos)."""
        cands = [c for c in self.cfg.bounds if c in self.cfg.priors]
        if not any(c.damage_active for c in self.cfg.conditions):
            cands = [c for c in cands if c not in _DAMAGE_CONSTANTS]
        self.constants = dict(self.cfg.priors)
        free: List[str] = []
        self._fit_subset(free)                    # baseline: so estados
        best = self.global_mae()
        history: List[tuple] = [("(defaults+estados)", best)]
        while len(free) < max_constants:
            trials = []
            for cand in cands:
                if cand in free:
                    continue
                saved_c = dict(self.constants)
                saved_f = dict(self.F0_estimates)
                self._fit_subset(free + [cand])
                trials.append((cand, self.global_mae(),
                               dict(self.constants), dict(self.F0_estimates)))
                self.constants, self.F0_estimates = saved_c, saved_f
            if not trials:
                break
            cand, m, snap_c, snap_f = min(trials, key=lambda z: z[1])
            if best - m < tol:
                break
            free.append(cand)
            best = m
            self.constants, self.F0_estimates = snap_c, snap_f
            history.append((cand, m))
        return {
            "free_constants": free,
            "constants": {k: float(v) for k, v in self.constants.items()},
            "F0_estimates": {k: float(v) for k, v in self.F0_estimates.items()},
            "mae_global": float(best),
            "mae_by_condition": self.mae_by_condition(),
            "selection_history": history,
        }

    def loco(self, free_constants: List[str]) -> dict:
        """Leave-one-condition-out: refita as demais condicoes (mesmo conjunto
        livre) e PREDIZ a retida usando so os estados nomeados dela. Se o F0 da
        retida era estimado (sobretorque), usa o valor do fit completo e marca
        state_F0_from_full_fit=True (limitacao documentada, spec §2.5)."""
        out: Dict[str, dict] = {}
        full_f0 = dict(self.F0_estimates)
        full_consts = dict(self.constants)
        for held in self.cfg.conditions:
            rest = [c for c in self.cfg.conditions if c.name != held.name]
            sub_cfg = replace(
                self.cfg, conditions=rest,
                estimate_F0={k: v for k, v in self.cfg.estimate_F0.items()
                             if k != held.name})
            sub = SharedCalibrator(sub_cfg)
            sub._fit_subset(list(free_constants))
            pred = SharedCalibrator(replace(self.cfg, conditions=[held]))
            pred.constants = dict(sub.constants)
            pred.F0_estimates = ({held.name: full_f0[held.name]}
                                 if held.name in full_f0 else {})
            out[held.name] = {
                "MAE_pred": pred.mae_by_condition()[held.name],
                "state_F0_from_full_fit": held.name in full_f0,
            }
        # restaura o estado do fit completo
        self.constants, self.F0_estimates = full_consts, full_f0
        return out
```

- [ ] **Step 4: Export from the package**

In `src/bolt_analysis_studio/calibration/__init__.py`, add (matching however the existing names are exported there — if the file only has a docstring, add plain imports):

```python
from .shared_calibrator import (          # noqa: F401
    PHYSICAL_PRIORS, ConditionSpec, SharedCalibrationConfig, SharedCalibrator,
)
```

- [ ] **Step 5: Syntax check + run tests**

Run: `python -c "import ast; ast.parse(open('src/bolt_analysis_studio/calibration/shared_calibrator.py', encoding='utf-8').read()); print('OK')"`
Run: `python -m pytest tests/test_shared_calibrator.py -v`
Expected: 4 PASS (takes a few minutes — each fit simulates 300-cycle runs repeatedly).

- [ ] **Step 6: Commit**

```bash
git add src/bolt_analysis_studio/calibration/shared_calibrator.py src/bolt_analysis_studio/calibration/__init__.py tests/test_shared_calibrator.py
git commit -m "calib: SharedCalibrator — uma fisica, N estados (fit conjunto + LOCO)

Fit em log-espaco das constantes fisicas com prior de literatura;
tuners congelados em 1.0; estados nomeados por condicao; F0 estimavel
(fallback sobretorque); leave-one-condition-out. Spec 2026-07-02 §2.5.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: `calibrate_shared.py` — the science run

**Files:**
- Create: `New_Theory/calibrate_shared.py`
- Modify (result): `New_Theory/joint_calibrations.json` (gains `schema`/`shared`), `New_Theory/calibration_shared.png` (new)

**Interfaces:**
- Consumes: `SharedCalibrator` API from Task 3, `upsert_shared` from Task 2, the 11 `New_Theory/M16_shear_*.csv` curves.
- Produces: `build_shared_config(n_cycles: int = 2500) -> SharedCalibrationConfig` (imported by Task 5), the `shared` JSON block (spec §2.6), the PNG, and the console tables Task 6 transcribes.

- [ ] **Step 1: Write the script**

Create `New_Theory/calibrate_shared.py`:

```python
"""Calibracao COMPARTILHADA (Estagio A, spec 2026-07-02): UMA fisica para as
4 condicoes M16 shear +-0.5mm 0.5Hz; condicoes diferem so por estados nomeados
(D_init, emb_consumed_frac, F0_test). Tuners nunca sao fitados (ficam em 1.0).

Output:
  New_Theory/joint_calibrations.json   (bloco `shared`, schema 2; `profiles` preservado)
  New_Theory/calibration_shared.png    (grid 2x2, MESMAS constantes nas 4)

Run:  python New_Theory/calibrate_shared.py [--quick]
  --quick: n_cycles=600 (smoke; NAO gravar como resultado cientifico)
Runtime esperado do run completo: ~1-3 h (forward selection x 4 condicoes
x 2500 ciclos por avaliacao + LOCO).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointGeometry
from bolt_analysis_studio.calibration.shared_calibrator import (
    ConditionSpec, SharedCalibrationConfig, SharedCalibrator,
)
from bolt_analysis_studio.calibration.profiles import upsert_shared

DATA_DIR = ROOT / "New_Theory"
OUT_JSON = DATA_DIR / "joint_calibrations.json"
OUT_PNG = DATA_DIR / "calibration_shared.png"

M16_GEOM = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                         pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)
F0_NOM_N, F_AMP_N, DELTA_AMP_M = 50_000.0, 20_000.0, 0.5e-3
THETA, FREQ_HZ = np.pi / 2, 0.5

# Estados nomeados por condicao (spec §2.3). sobretorque: F0 estimado (§2.3
# fallback — usuario nao tem o registro do ensaio TP6).
CONDITIONS_DEF = {
    "nova": dict(
        curves=["TP3_nova", "TP8_nova", "TP11_nova", "MEAN_nova"],
        states={}),
    "reusada": dict(
        curves=["TP4_reusada", "TP5_reusada", "TP9_reusada", "TP10_reusada",
                "MEAN_reusada"],
        states=dict(D_init=0.3, emb_consumed_frac=1.0, damage_active=True)),
    "sobretorque": dict(
        curves=["TP6_sobretorque"],
        states={}),
    "reaperto": dict(
        curves=["TP7_reaperto"],
        states=dict(D_init=0.3, damage_active=True)),
}
BOUNDS = {
    "emb_depth": (5e-6, 80e-6), "N_emb": (10.0, 200.0),
    "K_archard": (1e-5, 1e-3), "C_creep": (1e-12, 1e-9),
    "tr_loose_gain": (0.5, 10.0), "c_D": (0.5, 8.0), "k_dmg_wear": (0.5, 8.0),
}
ESTIMATE_F0 = {"sobretorque": (40_000.0, 120_000.0)}
# sanity §2.3: F0_test <= 0.9 * Rp0.2 * A_s (M16 10.9: 0.9*940MPa*157mm2)
F0_SANITY_N = 0.9 * 940e6 * 157e-6
COND_COLORS = {"nova": "#4F81BD", "reusada": "#C00000",
               "sobretorque": "#00B050", "reaperto": "#92D050"}


def load_curves(names):
    out = []
    for name in names:
        d = np.genfromtxt(DATA_DIR / f"M16_shear_{name}.csv",
                          delimiter=",", skip_header=1)
        out.append({"name": name, "cycles": d[:, 0], "ratio": d[:, 1]})
    return out


def build_shared_config(n_cycles: int = 2500) -> SharedCalibrationConfig:
    conds = []
    for name, spec in CONDITIONS_DEF.items():
        s = spec["states"]
        conds.append(ConditionSpec(
            name=name, curves=load_curves(spec["curves"]),
            F0_init=F0_NOM_N, F_amp=F_AMP_N, delta_amp=DELTA_AMP_M,
            D_init=s.get("D_init", 0.0),
            emb_consumed_frac=s.get("emb_consumed_frac", 0.0),
            damage_active=s.get("damage_active", False)))
    return SharedCalibrationConfig(
        geom=M16_GEOM, conditions=conds, theta=THETA, freq=FREQ_HZ,
        n_cycles=n_cycles, bounds=BOUNDS, estimate_F0=ESTIMATE_F0)


def main():
    n_cycles = 600 if "--quick" in sys.argv else 2500
    cfg = build_shared_config(n_cycles)
    cal = SharedCalibrator(cfg)

    print("== fit_parsimonious (constantes fisicas compartilhadas) ==")
    # max_constants=4: o F0_test estimado do sobretorque ocupa 1 slot do
    # orcamento de <=5 numeros fitados no dataset inteiro (spec §5.1).
    res = cal.fit_parsimonious(tol=0.005, max_constants=4)
    print(f"constantes livres: {res['free_constants']}")
    for k in res["free_constants"]:
        print(f"  {k:15s} = {res['constants'][k]:.4g}"
              f"   (prior {cfg.priors[k]:.4g})")
    for name, f0 in res["F0_estimates"].items():
        ok = "OK" if f0 <= F0_SANITY_N else "ACIMA DO SANITY (!)"
        print(f"  F0_test[{name}] = {f0/1e3:.1f} kN  "
              f"(sanity <= {F0_SANITY_N/1e3:.0f} kN: {ok})")
    print(f"MAE global = {res['mae_global']:.4f}")
    for name, mae in res["mae_by_condition"].items():
        print(f"  MAE {name:12s} = {mae:.4f}")
    print(f"selecao: {[(c, round(m, 4)) for c, m in res['selection_history']]}")

    print("\n== LOCO (leave-one-condition-out) ==")
    loco = cal.loco(res["free_constants"])
    for name, r in loco.items():
        star = "  [F0 do fit completo]" if r["state_F0_from_full_fit"] else ""
        print(f"  {name:12s} MAE_pred = {r['MAE_pred']:.4f}{star}")

    # ---- plot: as MESMAS constantes nas 4 condicoes ----
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for ax, cond in zip(axes.flat, cfg.conditions):
        sim_N, sim_ratio = cal._run_condition(cond)
        col = COND_COLORS[cond.name]
        for c in cond.curves:
            ls = "-" if c["name"].startswith("MEAN") else ":"
            ax.plot(c["cycles"], c["ratio"], ls, color=col, alpha=0.8,
                    marker="o", markersize=4, label=c["name"])
        ax.plot(sim_N, sim_ratio, "k-", linewidth=2.5,
                label=(f"sim compartilhada "
                       f"(MAE={res['mae_by_condition'][cond.name]:.3f})"))
        ax.set_xlabel("Ciclos N"); ax.set_ylabel(r"$F_0/F_{0,init}$")
        ax.set_title(f"{cond.name} — fisica COMPARTILHADA, estados nomeados")
        ax.set_xlim(0, n_cycles); ax.set_ylim(0, 1.05); ax.grid(alpha=0.3)
        ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    fig.savefig(OUT_PNG, dpi=120)
    print(f"\nPlot: {OUT_PNG}")

    if "--quick" in sys.argv:
        print("--quick: NAO gravando bloco shared (resultado nao-cientifico).")
        return

    shared = {
        "calibrated_at": "2026-07-02",
        "method": "SharedCalibrator.fit_parsimonious (tol=0.005, log-priors)",
        "loading": {"F_amp_N": F_AMP_N, "delta_amp_m": DELTA_AMP_M,
                    "theta_rad": float(THETA), "freq_Hz": FREQ_HZ,
                    "n_cycles": n_cycles},
        "free_constants": res["free_constants"],
        "constants": res["constants"],
        "selection_history": [[c, m] for c, m in res["selection_history"]],
        "mae_global": res["mae_global"],
        "conditions": {},
        "loco": {name: r for name, r in loco.items()},
    }
    for cond in cfg.conditions:
        states = {}
        if cond.D_init:
            states["D_init"] = cond.D_init
        if cond.emb_consumed_frac:
            states["emb_consumed_frac"] = cond.emb_consumed_frac
        if cond.name in res["F0_estimates"]:
            states["F0_test_N"] = res["F0_estimates"][cond.name]
            states["F0_provenance"] = "estimated"
        else:
            states["F0_N"] = cond.F0_init
            states["F0_provenance"] = "nominal"
        shared["conditions"][cond.name] = {
            "states": states,
            "damage_active": cond.damage_active,
            "MAE": res["mae_by_condition"][cond.name],
        }
    upsert_shared(OUT_JSON, shared)
    print(f"JSON: {OUT_JSON} (bloco shared, schema 2; profiles preservado)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Syntax check + smoke run**

Run: `python -c "import ast; ast.parse(open('New_Theory/calibrate_shared.py', encoding='utf-8').read()); print('OK')"`
Run: `python New_Theory/calibrate_shared.py --quick`
Expected: completes in ~10–30 min, prints the constants/MAE/LOCO tables, writes the PNG, does NOT write the JSON (quick mode). Sanity-check the printout: `free_constants` non-empty, every `MAE` finite, `F0_test[sobretorque]` inside `[40, 120]` kN.

- [ ] **Step 3: Full science run (background)**

Run (background, ~1–3 h): `python New_Theory/calibrate_shared.py`
Expected: same tables at n_cycles=2500 + `JSON: ... (bloco shared, schema 2; profiles preservado)`.
Then verify: `python -c "import json; d=json.load(open('New_Theory/joint_calibrations.json', encoding='utf-8')); print(d['schema'], sorted(d['shared']['constants'])); print({k: v['MAE'] for k, v in d['shared']['conditions'].items()})"`
Expected: `2` + constants list + 4 finite MAEs. **Save the full console output** — Task 6 transcribes it into the docs.

- [ ] **Step 4: Record the result (whatever it is)**

This step cannot fail: if the shared fit closes well, that's the headline result; if some condition's MAE is far above its per-condition fit, that is a **falsification finding** (spec §5.6 / MODEL_LEGITIMACY §7) to be written up in Task 6 — do not add per-condition knobs to force it closed.

- [ ] **Step 5: Commit**

```bash
git add New_Theory/calibrate_shared.py New_Theory/joint_calibrations.json New_Theory/calibration_shared.png
git commit -m "calib: run compartilhado das 4 condicoes (bloco shared, schema 2)

Uma fisica (<=5 constantes fitadas no dataset inteiro), estados nomeados
por condicao, F0 do sobretorque estimado com procedencia, LOCO. Estagio A
do spec 2026-07-02-shared-physics-model-design.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: identifiability of the shared fit (`--shared` mode)

**Files:**
- Modify: `New_Theory/identifiability_analysis.py`

**Interfaces:**
- Consumes: `build_shared_config()` from `New_Theory/calibrate_shared.py`; the saved `shared` block; `SharedCalibrator._residuals(x, free_consts, f0_names)` (log-space) from Task 3.
- Produces: `python New_Theory/identifiability_analysis.py --shared` prints the sloppiness spectrum + per-constant 95% CIs of the shared fit (numbers for MODEL_LEGITIMACY §4.5).

- [ ] **Step 1: Add the `analyse_shared` function**

In `New_Theory/identifiability_analysis.py`, add after `analyse(...)` (module imports at top already include `sys`, `Path`, `numpy`, `least_squares`):

```python
def analyse_shared():
    """Identifiabilidade do FIT COMPARTILHADO (constantes fisicas, log-espaco):
    espectro de J^T J + CIs por constante. Le o bloco `shared` gravado pelo
    calibrate_shared.py e re-avalia os residuos em torno do otimo."""
    import json
    sys.path.insert(0, str(DATA))
    from calibrate_shared import build_shared_config
    from bolt_analysis_studio.calibration.shared_calibrator import SharedCalibrator

    saved = json.loads((DATA / "joint_calibrations.json").read_text(encoding="utf-8"))
    shared = saved["shared"]
    free = list(shared["free_constants"])
    cfg = build_shared_config(n_cycles=shared["loading"]["n_cycles"])
    cal = SharedCalibrator(cfg)
    cal.constants.update({k: float(v) for k, v in shared["constants"].items()
                          if k in cal.constants})
    f0_names = []
    for name, c in shared["conditions"].items():
        if c["states"].get("F0_provenance") == "estimated":
            cal.F0_estimates[name] = float(c["states"]["F0_test_N"])
            f0_names.append(name)

    labels = free + [f"F0_test[{n}]" for n in f0_names]
    x = np.array([np.log(cal.constants[k]) for k in free]
                 + [np.log(cal.F0_estimates[n]) for n in f0_names])
    r0 = cal._residuals(x, free, f0_names)

    print(f"\n{'='*70}\nFIT COMPARTILHADO (log-espaco, {len(labels)} variaveis, "
          f"{len(r0)} residuos)\n{'='*70}")
    print("otimo: " + "  ".join(f"{l}={np.exp(v):.4g}" for l, v in zip(labels, x)))

    J = np.zeros((len(r0), len(x)))
    for i in range(len(x)):
        h = 0.02
        xp, xm = x.copy(), x.copy()
        xp[i] += h; xm[i] -= h
        J[:, i] = (cal._residuals(xp, free, f0_names)
                   - cal._residuals(xm, free, f0_names)) / (2 * h)
    # log-espaco ja e relativo — sem re-escalar
    JtJ = J.T @ J
    eig = np.maximum(np.sort(np.linalg.eigvalsh(JtJ))[::-1], 0.0)
    top = eig[0] if eig[0] > 0 else 1.0
    stiff = int(np.sum(eig > top * 1e-3))
    print("\nSLOPPINESS (autovalores de J^T J, log-espaco, normalizados):")
    print("  " + "  ".join(f"{e/top:.2e}" for e in eig))
    print(f"  direcoes stiff (>1e-3) = {stiff}/{len(eig)}")

    N, p = len(r0), len(x)
    sigma2 = float(np.sum(r0 ** 2)) / max(N - p, 1)
    print("\nIC 95% por variavel (multiplicativo, cov = sigma^2 (JtJ)^-1):")
    try:
        cov = sigma2 * np.linalg.inv(JtJ)
        for i, l in enumerate(labels):
            ci = 1.96 * np.sqrt(max(cov[i, i], 0.0))
            verdict = ("DETERMINADO" if ci < 0.3
                       else ("fraco" if ci < 1.0 else "NAO determinado"))
            print(f"  {l:20s} = {np.exp(x[i]):.4g}  x/ {np.exp(ci):.2f}"
                  f"  -> {verdict}")
    except np.linalg.LinAlgError:
        print("  JtJ singular -> direcoes totalmente nao-identificaveis.")
```

And change `main()` to route:

```python
def main():
    if "--shared" in sys.argv:
        analyse_shared()
        return
    analyse("nova", "MEAN_nova")
    analyse("reusada", "MEAN_reusada")
    print("\n" + "="*70)
    print("LEITURA: poucas direcoes 'stiff' + CIs largos = o dado nao pina todos")
    print("os tuners (modelo sloppy/sobre-parametrizado nessa curva). O conjunto")
    print("minimo mostra quantos botoes a curva realmente sustenta.")
```

- [ ] **Step 2: Syntax check + run**

Run: `python -c "import ast; ast.parse(open('New_Theory/identifiability_analysis.py', encoding='utf-8').read()); print('OK')"`
Run: `python New_Theory/identifiability_analysis.py --shared`
Expected: prints the shared-fit spectrum + CIs (runtime ~10–30 min: 2·n_vars residual evaluations at 2500 cycles × 4 conditions). **Save the output for Task 6.** The default (no-flag) mode must still work: `python New_Theory/identifiability_analysis.py` unchanged behavior (spot-check it starts printing the nova section, then Ctrl-C is fine).

- [ ] **Step 3: Commit**

```bash
git add New_Theory/identifiability_analysis.py
git commit -m "calib: identifiabilidade do fit compartilhado (--shared)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: docs + gate verdict (A→B)

**Files:**
- Modify: `New_Theory/MODEL_LEGITIMACY.md` (new §4.5 + §8 update + changelog row)
- Modify: `CLAUDE.md` (commands, V2 calibration section, gotchas)

**Interfaces:**
- Consumes: the saved `shared` block in `New_Theory/joint_calibrations.json`, the console outputs of Tasks 4–5.
- Produces: the documented Stage-A result + the explicit §2.8 gate verdict that decides Stage B's scope.

- [ ] **Step 1: Add §4.5 to MODEL_LEGITIMACY.md**

Insert after §4.4, transcribing the REAL numbers from `joint_calibrations.json` (`shared` block) and the Task 5 output — the tables below show the exact structure; every `<...>` placeholder MUST be replaced by the actual number from the run (this is transcription of results, not authoring):

```markdown
### 4.5 Fit compartilhado — uma física, N estados (Estágio A, spec 2026-07-02)

`SharedCalibrator` (rev. 2026-07-02): UM conjunto de constantes físicas fitado
em conjunto sobre as 4 condições (tuners ≡ 1.0, nunca fitados); condições
diferem só por estados nomeados. Rodar: `python New_Theory/calibrate_shared.py`.

**Constantes compartilhadas** (forward selection, tol=0.005, priors de literatura):

| Constante | Valor | Prior | IC 95% (×/÷) | Veredicto |
|---|---:|---:|---:|---|
| <constante 1> | <valor> | <prior> | <ci> | <DETERMINADO/fraco> |

Números fitados no dataset INTEIRO: <n_free + n_F0_estimados> (meta ≤5).

**Estados nomeados por condição** (inputs, não tuners): reusada
{emb_consumed_frac=1.0, D_init=0.3}; reaperto {D_init=0.3}; sobretorque
{F0_test = <valor> kN, procedência: estimated, sanity ≤133 kN}.

**MAE por condição — compartilhado vs por-condição (§4.4):**

| Condição | MAE compartilhado | MAE por-condição | LOCO MAE_pred |
|---|---:|---:|---:|
| nova | <...> | 0.024 | <...> |
| reusada | <...> | 0.026 | <...> |
| sobretorque | <...> | 0.007 | <...> |
| reaperto | <...> | 0.038 | <...> |

**Identificabilidade do fit compartilhado** (`identifiability_analysis.py
--shared`): <n_stiff>/<n_vars> direções stiff; <resumo dos CIs>.

**Veredicto do gate A→B (spec §2.8):** <PASSA/FALHA + 2-3 frases honestas:
o mesmo conjunto de constantes reproduz as 4 condições? onde não fecha, qual
mecanismo a falha aponta?>
```

- [ ] **Step 2: Update §8 (estado atual) and the changelog**

In §8, update the parsimony bullet to mention the shared fit (one line, with the real headline numbers). Append to the §9 changelog table:

```markdown
| 2026-07-02 | §4.5 fit compartilhado (`SharedCalibrator`, Estágio A do spec shared-physics): UMA física p/ as 4 condições, estados nomeados (D_init, emb_consumed_frac, F0_test estimado c/ procedência), LOCO. Embedding virou state-based (forma geométrica exata). Gate A→B: <veredicto>. |
```

- [ ] **Step 3: Update CLAUDE.md**

Three edits:
1. In the "V2 calibration tooling" commands block, add:
```bash
# Fit COMPARTILHADO (Estagio A spec 2026-07-02): uma fisica, N estados
python New_Theory/calibrate_shared.py            # ~1-3h; --quick p/ smoke
python New_Theory/identifiability_analysis.py --shared
```
2. In the "Calibration profiles" section, add a short paragraph after the profile table: the `shared` block (schema 2) is the analytical-model calibration — constants shared across conditions, per-condition named states, tuners frozen at 1.0; the `profiles` block remains what the GUI reads until Stage B. Include the real headline (n fitted constants, MAE range, LOCO range).
3. In "Key gotchas — V2 analyzer", add two bullets: `EmbeddingLoss` is now state-based (geometric form, exact Norton closed form; `k_emb_scale` still scales the asymptote until Stage B) and `DynamicStiffnessAnalyzer(..., initial_embedding_frac=...)` seeds consumed embedding (reused washers).
4. In "Next-priority items (V2)", add: Stage B (tuner-layer removal, spec 2026-07-02 §3) pending the gate verdict; and update the test-suite command line to include the three new test files.

- [ ] **Step 4: Commit**

```bash
git add New_Theory/MODEL_LEGITIMACY.md CLAUDE.md
git commit -m "docs: resultado do fit compartilhado (§4.5) + veredicto do gate A->B

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

- [ ] **Step 5: Final full-suite regression**

Run: `python -m pytest tests/test_surface_damage.py tests/test_staged_calibrator.py tests/test_calibration_segmentation.py tests/test_calibration_decomposition.py tests/test_calibration_profiles.py tests/test_calibration_server.py tests/test_v2_solver_preload.py tests/test_slip_onset_incubation.py tests/test_case_study_models.py tests/test_calibration_trim.py tests/test_v2_calibration.py tests/test_embedding_state_based.py tests/test_shared_block_persistence.py tests/test_shared_calibrator.py -q`
Expected: all PASS. Report the Stage-A result + gate verdict to the user; Stage B gets its own plan only after the user reads the verdict.
