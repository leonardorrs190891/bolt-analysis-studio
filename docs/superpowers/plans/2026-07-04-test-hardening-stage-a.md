# Test-Hardening (Stage A guardrails) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close three guardrail gaps left after Stage A / Phase 1 (queued in `.superpowers/sdd/progress.md`): (1) `DynamicStiffnessAnalyzer` accepts out-of-range `initial_embedding_frac` / `initial_damage` silently; (2) the "LOCO ≈ fit ⇒ generalizes" claim has no regression guard; (3) `upsert_shared`'s return-value contract is untested.

**Architecture:** One small code change (constructor range validation in `dynamic_stiffness_analyzer.py`) plus test additions to three existing test files. Each item is independently reviewable and ships as its own task/commit.

**Tech Stack:** Python 3, pytest. No new dependencies.

## Model tiering & swaps (session on Opus 4.8 max effort)

Pure mechanical hardening — **no scientific conclusion is produced, so no Fable swap is needed.**

| Task | Implementer | Task reviewer |
|---|---|---|
| 1 (constructor validation + tests) | sonnet | sonnet |
| 2 (LOCO regression test) | sonnet | sonnet |
| 3 (upsert_shared return test) | haiku (transcription) | sonnet |
| Final whole-branch review | opus (small mechanical diff) | — |

**No Fable.** A test-hardening diff does not clear the bar for the most-capable-model review (subagent-driven-development: scale the reviewer to the diff's risk). If Fable is trivially available, using it for the final review is harmless but not required.

## Global Constraints

- All file I/O uses `encoding='utf-8'`.
- Syntax-check every `.py` edit before testing: `python -c "import ast; ast.parse(open('PATH', encoding='utf-8').read()); print('OK')"`.
- **Never `git add -A`.** Explicit file lists only (OneDrive parallel session; foreign working-tree changes are the user's WIP — never stage them).
- Commits in Portuguese, no accents, ending with the trailer `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- `tests/conftest.py` puts `src/` on `sys.path`.
- **Backward compatibility:** the range validation must accept the closed boundaries `0.0` and `1.0` — existing tests pass `initial_embedding_frac=1.0` (`test_initial_embedding_frac_suppresses_embedding_loss`) and `initial_damage=0.2` (`test_default_frac_zero_is_backward_compatible`).

---

### Task 1: Range validation for `initial_embedding_frac` and `initial_damage`

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py:714-717` (constructor)
- Test: `tests/test_embedding_state_based.py` (append)

**Interfaces:**
- Consumes: `DynamicStiffnessAnalyzer.__init__(geometry, material, initial_preload, loss_mechanisms=None, initial_damage=0.0, initial_embedding_frac=0.0)`.
- Produces: `ValueError` raised when either fraction is outside the closed interval `[0.0, 1.0]`.

> **Design decision (small — noted for the reviewer, not asked):** validation **raises `ValueError`** rather than silently clamping. A fraction > 1 (or < 0) is a caller bug, and the project favors failing loud (cf. the activation-registry `KeyError` "loud by design"). If the professor prefers clamping to `[0, 1]`, the change is local to Step 3 and the test in Step 1 flips to asserting the clamped `delta_emb` — flag it in review rather than deciding unilaterally at execution time.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_embedding_state_based.py`:

```python
@pytest.mark.parametrize("frac", [-0.1, 1.5, 2.0])
def test_initial_embedding_frac_out_of_range_raises(frac):
    with pytest.raises(ValueError, match="initial_embedding_frac"):
        DynamicStiffnessAnalyzer(GEOM, JointMaterial(), 50e3,
                                 initial_embedding_frac=frac)


@pytest.mark.parametrize("dmg", [-0.5, 1.2])
def test_initial_damage_out_of_range_raises(dmg):
    with pytest.raises(ValueError, match="initial_damage"):
        DynamicStiffnessAnalyzer(GEOM, JointMaterial(), 50e3, initial_damage=dmg)


def test_boundary_fractions_accepted():
    # limites fechados [0, 1] sao validos (nao devem levantar)
    DynamicStiffnessAnalyzer(GEOM, JointMaterial(), 50e3,
                             initial_embedding_frac=1.0, initial_damage=1.0)
    DynamicStiffnessAnalyzer(GEOM, JointMaterial(), 50e3,
                             initial_embedding_frac=0.0, initial_damage=0.0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_embedding_state_based.py -v`
Expected: the three new tests FAIL — the out-of-range calls currently construct silently (no `ValueError`); the boundary test passes.

- [ ] **Step 3: Add the validation**

In `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py`, insert the guard at the top of `__init__`, immediately after the signature line `initial_embedding_frac: float = 0.0):` and before `self.geom = geometry`:

```python
        if not 0.0 <= initial_embedding_frac <= 1.0:
            raise ValueError(
                f"initial_embedding_frac deve estar em [0, 1] "
                f"(recebido {initial_embedding_frac})")
        if not 0.0 <= initial_damage <= 1.0:
            raise ValueError(
                f"initial_damage deve estar em [0, 1] "
                f"(recebido {initial_damage})")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_embedding_state_based.py -v`
Expected: PASS (all tests, including the pre-existing four).

- [ ] **Step 5: Syntax-check and commit**

```bash
python -c "import ast; ast.parse(open('src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py', encoding='utf-8').read()); print('OK')"
git add src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py tests/test_embedding_state_based.py
git commit -m "hardening: valida faixa [0,1] de initial_embedding_frac e initial_damage"
```

---

### Task 2: LOCO-generalization regression guard

**Files:**
- Test: `tests/test_shared_calibrator.py` (append)

**Interfaces:**
- Consumes: `SharedCalibrator.fit_parsimonious` (returns `mae_by_condition`) and `.loco` (returns `{name: {"MAE_pred", "state_F0_from_full_fit"}}`); module-level `_cond`, `_config`, `NOISE` already defined in the file.
- Produces: a regression assertion that leave-one-condition-out prediction stays near the full-fit MAE (the "shared physics generalizes" claim).

- [ ] **Step 1: Write the failing test**

Append to `tests/test_shared_calibrator.py`:

```python
def test_loco_mae_stays_near_fit_mae_generalizes():
    """Regressao do claim central do Estagio A: a predicao leave-one-out nao
    degrada muito vs o fit (fisica compartilhada GENERALIZA, nao decora)."""
    K_true = 1.6e-4
    conds = [_cond(f"c{i}", K_true, seed=i) for i in range(3)]
    cal = SharedCalibrator(_config(conds, {"K_archard": (1e-5, 1e-3)}))
    res = cal.fit_parsimonious(tol=0.002, max_constants=1)
    fit_by = res["mae_by_condition"]
    loco = cal.loco(res["free_constants"])
    for name in loco:
        # LOCO ~ fit: nunca pior que fit + 3*NOISE por condicao
        assert loco[name]["MAE_pred"] <= fit_by[name] + 3 * NOISE, name
```

- [ ] **Step 2: Run test to verify it passes immediately**

Run: `python -m pytest tests/test_shared_calibrator.py::test_loco_mae_stays_near_fit_mae_generalizes -v`
Expected: PASS. (This is a **regression guard**, not TDD — it should pass against the current code. If it FAILS, that is a real finding: LOCO does not generalize on the synthetic setup — STOP and report to the controller rather than loosening the bound to make it pass.)

- [ ] **Step 3: Run the full file (no regressions)**

Run: `python -m pytest tests/test_shared_calibrator.py -v`
Expected: PASS (all, including the new test).

- [ ] **Step 4: Commit**

```bash
git add tests/test_shared_calibrator.py
git commit -m "hardening: guarda de regressao LOCO ~ fit (generalizacao do Estagio A)"
```

---

### Task 3: `upsert_shared` return-contract assertions

**Files:**
- Test: `tests/test_shared_block_persistence.py` (append)

**Interfaces:**
- Consumes: `upsert_shared(path, shared) -> dict` (returns the merged full data dict), `load_profiles`, `save_profiles`.
- Produces: assertion that the return value is the merged dict (schema + shared + preserved profiles), equal to what is on disk — without re-reading being the only check.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_shared_block_persistence.py`:

```python
def test_upsert_shared_returns_merged_data_dict(tmp_path):
    path = tmp_path / "j.json"
    save_profiles(path, {"profiles": {"nova": {}}})
    returned = upsert_shared(path, {"constants": {"C_creep": 1e-11}})
    # o RETORNO e o dict completo mesclado (nao so o efeito colateral em disco)
    assert returned["schema"] == 2
    assert returned["shared"]["constants"]["C_creep"] == 1e-11
    assert returned["profiles"]["nova"] == {}
    # e coincide com o que foi persistido
    assert returned == load_profiles(path)
```

- [ ] **Step 2: Run test to verify it passes immediately**

Run: `python -m pytest tests/test_shared_block_persistence.py::test_upsert_shared_returns_merged_data_dict -v`
Expected: PASS (pins the existing return contract; `upsert_shared` already returns `data`). If it FAILS, the contract regressed — report, do not weaken the assertion.

- [ ] **Step 3: Run the full file**

Run: `python -m pytest tests/test_shared_block_persistence.py -v`
Expected: PASS (all).

- [ ] **Step 4: Commit**

```bash
git add tests/test_shared_block_persistence.py
git commit -m "hardening: pina o contrato de retorno de upsert_shared"
```

---

## Self-Review (controller, after all tasks)

- **Spec coverage:** all four ledger items — frac range validation + frac>1 test (Task 1), initial_damage range (Task 1, folded in since it shares the guard), LOCO threshold (Task 2), upsert_shared return assert (Task 3). ✅
- **Backward compatibility:** boundary values `0.0`/`1.0` accepted; existing `frac=1.0` and `damage=0.2` tests still pass (Task 1 Step 4 runs the whole file). ✅
- **Placeholders:** none — every test body and the guard code are complete.
- **Regression-guard honesty:** Tasks 2 & 3 pass against current code; the plan explicitly forbids loosening bounds to force a pass and requires reporting a genuine failure. ✅
- **Full-suite check before merge:** run the 18-file calibration suite (see `CLAUDE.md` → V2 calibration package tests) in the final review; expected baseline `90 passed` plus the new tests.
