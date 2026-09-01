# Re-calibrate 4 profiles under state-based embedding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Confirm the committed 4-profile staged calibration (CLAUDE.md table) still holds under the state-based `EmbeddingLoss` (rev. 2026-07-02), and — as a prerequisite — fix the latent bug where `calibrate_4_profiles.py` **clobbers the canonical `shared` block** when it rewrites `joint_calibrations.json`.

**Architecture:** `calibrate_4_profiles.py` currently ends with `save_profiles(OUT_JSON, out)` where `out` has only `description`/`global_settings`/`profiles` — an atomic **full-file** write that erases the `shared` block and `schema:2` that `calibrate_shared.py` wrote. Task 1 adds `upsert_profiles_bundle` to `profiles.py` (merge the profiles bundle, preserve everything else); Task 2 wires the script to it; Task 3 re-runs and compares MAE against the committed table with a pre-registered tolerance, recording the outcome **as is**.

**Tech Stack:** Python 3, numpy, scipy (via `StagedCalibrator`), matplotlib. No new dependencies.

## Model tiering & swaps (session on Opus 4.8 max effort)

Mostly mechanical (bug fix + regression re-run). The only conclusion is a regression note ("profiles confirmed" or "drifted by X").

| Task | Implementer | Task reviewer |
|---|---|---|
| 1 (`upsert_profiles_bundle` + tests) | sonnet | sonnet |
| 2 (wire the script) | haiku (2-hunk edit) | sonnet |
| 3 (re-run, compare, record) | opus | — (controller verifies) |
| Final whole-branch review | opus | — |

**Fable swap — conditional:** only if Task 3 finds a **non-trivial drift** (any profile's MAE moves by > 0.01 from the committed table). A surprising drift under state-based embedding is a scientific finding and its MODEL_LEGITIMACY note should be written/reviewed on **Fable** (Opus-max fallback). If all four profiles reproduce within tolerance, no Fable is needed — it's a confirmation.

## Global Constraints

- All file I/O uses `encoding='utf-8'`.
- Syntax-check every `.py` edit before testing: `python -c "import ast; ast.parse(open('PATH', encoding='utf-8').read()); print('OK')"`.
- **Never `git add -A`.** Explicit file lists only (OneDrive parallel session; foreign working-tree changes are the user's WIP — never stage them).
- **The `shared` block of `joint_calibrations.json` MUST survive the re-run.** This is the whole point of Task 1; Task 3 Step 4 verifies it explicitly.
- Commits in Portuguese, no accents, ending with the trailer `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- `.json`/`.png` are **not** gitignored — normal `git add` works. The `M16_shear_*.csv` inputs are gitignored but already present in the checkout.
- Science recorded AS IS: the pre-registered MAE tolerance (0.01) is frozen; do not adjust it to declare a confirmation.

---

### Task 1: `upsert_profiles_bundle` — merge profiles, preserve `shared`

**Files:**
- Modify: `src/bolt_analysis_studio/calibration/profiles.py` (append a function)
- Test: `tests/test_calibration_profiles.py` (append; read the file first to match its import/style)

**Interfaces:**
- Consumes: `load_profiles(path) -> dict`, `save_profiles(path, data)` (already in `profiles.py`).
- Produces: `upsert_profiles_bundle(path, description, global_settings, profiles) -> dict` — sets `data["description"]`, `data["global_settings"]`, `data["profiles"]` on the loaded dict and re-saves, preserving `schema`, `shared`, and any other top-level keys. Returns the merged dict.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_calibration_profiles.py` (use the module's existing import of `bolt_analysis_studio.calibration.profiles`; add `upsert_profiles_bundle`, `save_profiles`, `load_profiles` to it):

```python
def test_upsert_profiles_bundle_preserves_shared_block(tmp_path):
    path = tmp_path / "joint_calibrations.json"
    # arquivo pre-existente com bloco shared (Estagio A) + profiles antigos
    save_profiles(path, {
        "schema": 2,
        "shared": {"constants": {"C_creep": 1.165e-11}, "mae_global": 0.0796},
        "profiles": {"old": {"tuners": {}}},
    })
    returned = upsert_profiles_bundle(
        path,
        description="desc nova",
        global_settings={"geometry": "M16"},
        profiles={"nova": {"tuners": {"k_emb_scale": 1.1}}},
    )
    # bloco shared + schema PRESERVADOS
    assert returned["schema"] == 2
    assert returned["shared"]["constants"]["C_creep"] == 1.165e-11
    assert returned["shared"]["mae_global"] == 0.0796
    # profiles/description/global_settings SUBSTITUIDOS
    assert returned["profiles"] == {"nova": {"tuners": {"k_emb_scale": 1.1}}}
    assert "old" not in returned["profiles"]
    assert returned["description"] == "desc nova"
    assert returned["global_settings"] == {"geometry": "M16"}
    # retorno == disco
    assert returned == load_profiles(path)


def test_upsert_profiles_bundle_on_missing_file(tmp_path):
    path = tmp_path / "new.json"
    returned = upsert_profiles_bundle(path, "d", {}, {"nova": {}})
    assert returned["profiles"] == {"nova": {}}
    assert "shared" not in returned  # nada a preservar; nao inventa bloco
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_calibration_profiles.py -v`
Expected: the two new tests FAIL with `ImportError`/`AttributeError` (`upsert_profiles_bundle` does not exist).

- [ ] **Step 3: Add the function**

Append to `src/bolt_analysis_studio/calibration/profiles.py`:

```python
def upsert_profiles_bundle(path: PathLike, description: str,
                           global_settings: dict, profiles: dict) -> dict:
    """Grava/atualiza o bloco de PERFIS (StagedCalibrator) SEM tocar no bloco
    `shared`/`schema` (calibracao compartilhada, Estagio A) nem em outras
    chaves de topo. Substitui o antigo `save_profiles(out)` de
    calibrate_4_profiles.py, que sobrescrevia o arquivo inteiro e apagava o
    bloco `shared`."""
    data = load_profiles(path)
    data["description"] = description
    data["global_settings"] = global_settings
    data["profiles"] = profiles
    save_profiles(path, data)
    return data
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_calibration_profiles.py -v`
Expected: PASS (all, including the two new tests).

- [ ] **Step 5: Syntax-check and commit**

```bash
python -c "import ast; ast.parse(open('src/bolt_analysis_studio/calibration/profiles.py', encoding='utf-8').read()); print('OK')"
git add src/bolt_analysis_studio/calibration/profiles.py tests/test_calibration_profiles.py
git commit -m "calibration: upsert_profiles_bundle preserva o bloco shared ao gravar profiles"
```

---

### Task 2: Wire `calibrate_4_profiles.py` to `upsert_profiles_bundle`

**Files:**
- Modify: `New_Theory/calibrate_4_profiles.py:27` (import) and `:128-139` (`main` write)

**Interfaces:**
- Consumes: `upsert_profiles_bundle` (Task 1).
- Produces: a `calibrate_4_profiles.py` that no longer clobbers the `shared` block.

- [ ] **Step 1: Change the import**

Replace line 27:

```python
from bolt_analysis_studio.calibration.profiles import save_profiles
```

with:

```python
from bolt_analysis_studio.calibration.profiles import upsert_profiles_bundle
```

- [ ] **Step 2: Replace the write block in `main`**

Replace this block at the end of `main()`:

```python
    out = {
        'description': ("4 perfis M16 shear +-0.5mm 0.5Hz calibrados em estagios "
                        "(StagedCalibrator) com surface_damage nos perfis "
                        "reaperto/reusada."),
        'global_settings': {
            'geometry': 'M16 ISO metric (d_2=14.701mm, p=2.0mm, A_s=157mm2)',
            'loading': 'shear puro +-0.5mm 0.5Hz, F0=50kN, F_amp=20kN',
        },
        'profiles': profiles,
    }
    save_profiles(OUT_JSON, out)
    print(f"JSON: {OUT_JSON}")
```

with:

```python
    upsert_profiles_bundle(
        OUT_JSON,
        description=("4 perfis M16 shear +-0.5mm 0.5Hz calibrados em estagios "
                     "(StagedCalibrator) com surface_damage nos perfis "
                     "reaperto/reusada."),
        global_settings={
            'geometry': 'M16 ISO metric (d_2=14.701mm, p=2.0mm, A_s=157mm2)',
            'loading': 'shear puro +-0.5mm 0.5Hz, F0=50kN, F_amp=20kN',
        },
        profiles=profiles)
    print(f"JSON: {OUT_JSON} (profiles atualizado; bloco shared preservado)")
```

- [ ] **Step 3: Syntax-check**

Run: `python -c "import ast; ast.parse(open('New_Theory/calibrate_4_profiles.py', encoding='utf-8').read()); print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add New_Theory/calibrate_4_profiles.py
git commit -m "calibration: calibrate_4_profiles usa upsert_profiles_bundle (nao apaga shared)"
```

---

### Task 3: Re-run and compare against the committed table (AS IS)

**Files:**
- Regenerate (committed): `New_Theory/joint_calibrations.json` (profiles block), `New_Theory/calibration_4_profiles.png`
- Possibly modify: `CLAUDE.md` (profiles table) if MAE drifts

**Interfaces:**
- Consumes: the wired script (Task 2), the intact `shared` block.
- Produces: the confirmed/updated profiles + a recorded regression outcome.

**Pre-registered comparison** — committed CLAUDE.md table MAE per profile: `nova 0.036, reusada 0.031, sobretorque 0.017, reaperto 0.035`. Tolerance **0.01**. For virgin-fit profiles the state-based `EmbeddingLoss` reproduces the exact Norton closed form, so MAE should be essentially unchanged; a move > 0.01 is a genuine finding.

- [ ] **Step 1: Snapshot the `shared` block hash (canary)**

Run: `python -c "import json,hashlib; d=json.load(open('New_Theory/joint_calibrations.json',encoding='utf-8')); print(hashlib.sha256(json.dumps(d.get('shared'),sort_keys=True).encode()).hexdigest()[:16])"`
Record the printed hash (used in Step 4 to prove `shared` was untouched).

- [ ] **Step 2: Run the re-calibration (background, ~20-40 min)**

Run: `python New_Theory/calibrate_4_profiles.py`
Expected: prints per-profile `MAE global=... free=... D_init=...`; writes the PNG and updates the JSON. Capture the four MAE values.

- [ ] **Step 3: Compare against the committed table (record AS IS)**

For each profile, compute `|MAE_new - MAE_committed|`:
- All four `<= 0.01` → **confirmed**: the committed 4-profile fit holds under state-based embedding. No table change.
- Any `> 0.01` → **drifted**: record the new MAE (and, secondarily, the tuner values printed) exactly. This triggers the conditional Fable swap for the interpretation note.

Do **not** re-run to chase the committed numbers — record whatever the run produces.

- [ ] **Step 4: Verify the `shared` block survived**

Run the Step-1 hash command again. Expected: **identical hash**. Also:
Run: `python -c "import json; d=json.load(open('New_Theory/joint_calibrations.json',encoding='utf-8')); print('shared' in d, d.get('schema'))"`
Expected: `True 2`. If `shared` is missing or the hash changed, Task 2 did not take effect — STOP, restore `joint_calibrations.json` from git, and fix.

- [ ] **Step 5: If drifted — update the CLAUDE.md profiles table**

Only if Step 3 found drift: update the MAE column (and any materially-changed tuner) in the CLAUDE.md "Calibration profiles" table to the new values, with a one-line note that these are the state-based-embedding re-fit. (If confirmed within tolerance, skip — the table is already correct.)

- [ ] **Step 6: Commit**

```bash
git add New_Theory/joint_calibrations.json New_Theory/calibration_4_profiles.png
# add CLAUDE.md only if Step 5 changed it:
# git add CLAUDE.md
git commit -m "calibration: re-run dos 4 perfis sob embedding state-based (regressao confirmada / drift AS IS)"
```

(Choose the commit subject to match the actual outcome: "regressao confirmada" if all within 0.01, otherwise "drift registrado AS IS".)

---

## Self-Review (controller, after all tasks)

- **Clobber fixed before re-run:** Task 1+2 land before Task 3; Task 3 Step 4 proves `shared` survived. ✅
- **Spec coverage:** ledger item "(a) re-run calibrate_4_profiles.py under the new state-based embedding" done, with the previously-unnoticed clobber bug fixed as its prerequisite. ✅
- **AS IS:** tolerance frozen (0.01); Step 3 forbids re-running to match committed numbers. ✅
- **Type consistency:** `upsert_profiles_bundle(path, description, global_settings, profiles)` signature identical across `profiles.py` (Task 1), the test (Task 1), and the call site (Task 2). ✅
- **Conditional Fable swap:** only on drift > 0.01, with an Opus-max fallback. ✅
