# Parameter Activation Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A declarative parameter→activation-predicate registry (single source of truth) consumed by `SharedCalibrator` candidate filtering, so parameters of mechanisms not excited by the loading regime are never offered to the optimizer — with registry-truth tests pinning every predicate to the engine's actual equations.

**Architecture:** Spec `docs/superpowers/specs/2026-07-03-parameter-activation-registry-design.md`. New module `calibration/parameter_registry.py` (`LoadingRegime`, `ParameterRule`, `PARAMETER_REGISTRY`, `active_candidates`) with the full 4-dimension table (transverse slip, damage/reuse, thermal ΔT, F0 provenance). One consumer in v1: `SharedCalibrator.fit_parsimonious` replaces its hard-coded damage filter — provably identical candidates for all current datasets. GUI/validation consumers are future specs.

**Tech Stack:** Python 3, numpy, pytest. No new dependencies. No engine changes.

## Global Constraints

- Work on feature branch `parameter-registry` created from `main` at execution start (repo convention: merge-commit back when finished).
- All file I/O with `encoding='utf-8'`; after every `.py` edit run `python -c "import ast; ast.parse(open('PATH', encoding='utf-8').read()); print('OK')"`.
- **No engine changes** (`dynamic_stiffness_analyzer.py` untouched) and **no behavior change** for current datasets: the candidate set produced for the existing shear conditions must be IDENTICAL to today's filter (spec §3, §6.2, §6.5).
- `theta` is GLOBAL in `SharedCalibrationConfig`; per-condition regime variation comes from `delta_amp` and `damage_active`. `has_transverse_slip = sin(theta)>0 OR cond.delta_amp>0` (spec §1).
- A fittable name present in `bounds ∩ priors` but covered by NO fittable registry rule must raise `KeyError` (loud failure — the registry owns the list, spec §5.5).
- Registry-truth tests assert **bit-identical** trajectories (`np.array_equal`) — an unread parameter cannot change any float op.
- Circular-import rule: `parameter_registry` must NOT import from `shared_calibrator` at runtime (use `typing.TYPE_CHECKING` if annotating); `shared_calibrator` imports the registry.
- Commit messages: Portuguese without accents, prefix style, trailer `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Tests: `python -m pytest tests/<file> -v` from repo root. Existing suite that must stay green at the end: the 14-file list in CLAUDE.md's calibration command (now including the three Stage-A test files).
- NEVER stage foreign working-tree files (`src/bolt_analysis_studio/core/validation_cases.py`, `Models/**`, `.superpowers/`, `crash_log.txt`, `New_Theory/*.docx`, `BAS_V2_papers/`) — stage only the files named in each task.

## File Structure

| File | Responsibility |
|---|---|
| `src/bolt_analysis_studio/calibration/parameter_registry.py` (create) | `LoadingRegime`, `ParameterRule`, `PARAMETER_REGISTRY` table, `regime_from_condition`, `active_candidates` |
| `src/bolt_analysis_studio/calibration/shared_calibrator.py` (modify, ~lines 166-171) | `fit_parsimonious` uses `active_candidates`; result dict gains `"candidates"` key |
| `src/bolt_analysis_studio/calibration/__init__.py` (modify) | export the new names |
| `tests/test_parameter_registry.py` (create) | candidate-set tests, registry-truth tests, parity tests |
| `New_Theory/MODEL_LEGITIMACY.md` (modify) | §6 protocol item + §9 changelog row |
| `CLAUDE.md` (modify) | calibration-package bullet, gotcha, test-suite line |

---

### Task 1: Registry module + registry-truth tests

**Files:**
- Create: `src/bolt_analysis_studio/calibration/parameter_registry.py`
- Modify: `src/bolt_analysis_studio/calibration/__init__.py` (add exports)
- Test: `tests/test_parameter_registry.py` (create)

**Interfaces:**
- Consumes: `ConditionSpec` fields `name/delta_amp/damage_active` (duck-typed, no runtime import); `JointMaterial`, `DynamicStiffnessAnalyzer`, `JointGeometry` (tests only); `PHYSICAL_PRIORS` from `shared_calibrator` (tests only).
- Produces (Task 2 relies on): `active_candidates(bounds: Dict[str, tuple], priors: Dict[str, float], conditions: Iterable, theta: float, estimated: Set[str]) -> List[str]`; `regime_from_condition(cond, theta: float, estimated: bool) -> LoadingRegime`; `PARAMETER_REGISTRY: Tuple[ParameterRule, ...]`; `LoadingRegime(has_transverse_slip, has_axial, damage_active, delta_T_nonzero=False, F0_provenance="nominal")`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_parameter_registry.py`:

```python
"""Registro de ativacao de parametros por regime — spec 2026-07-03.

Inclui os testes registry-truth: cada predicado fitavel e pinado as equacoes
reais do engine (parametro inerte no regime => trajetoria BIT-IDENTICA).
"""
import numpy as np
import pytest

from bolt_analysis_studio.calibration.parameter_registry import (
    PARAMETER_REGISTRY, LoadingRegime, active_candidates, regime_from_condition,
)
from bolt_analysis_studio.calibration.shared_calibrator import (
    PHYSICAL_PRIORS, ConditionSpec, SharedCalibrationConfig, SharedCalibrator,
)
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)

M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)
BOUNDS_ALL = {
    "emb_depth": (5e-6, 80e-6), "N_emb": (10.0, 200.0),
    "K_archard": (1e-5, 1e-3), "C_creep": (1e-12, 1e-9),
    "tr_loose_gain": (0.5, 10.0), "c_D": (0.5, 8.0), "k_dmg_wear": (0.5, 8.0),
}


def _cond(name, delta_amp=0.5e-3, damage=False):
    # curva dummy: o registro nao le a curva, so o regime
    return ConditionSpec(
        name=name,
        curves=[{"name": name, "cycles": np.array([0.0, 100.0]),
                 "ratio": np.array([1.0, 0.9])}],
        F0_init=50e3, F_amp=20e3, delta_amp=delta_amp,
        damage_active=damage, D_init=0.3 if damage else 0.0)


# ---------------------------------------------------------------- candidatos
def test_axial_only_never_offers_transverse_constants():
    # theta=0 (axial puro) e delta_amp=0 => sem slip transversal em nenhuma
    # condicao: K_archard e tr_loose_gain nao podem ser candidatos.
    cands = active_candidates(BOUNDS_ALL, PHYSICAL_PRIORS,
                              [_cond("ax", delta_amp=0.0)],
                              theta=0.0, estimated=set())
    assert "K_archard" not in cands
    assert "tr_loose_gain" not in cands
    assert "emb_depth" in cands and "N_emb" in cands and "C_creep" in cands
    assert "c_D" not in cands and "k_dmg_wear" not in cands  # sem dano


def test_mixed_dataset_keeps_transverse_constants():
    # theta global 0, mas UMA condicao tem delta_amp>0 => alguma condicao
    # excita wear/loosening transversal => constantes continuam candidatas.
    conds = [_cond("ax", delta_amp=0.0), _cond("sh", delta_amp=0.5e-3)]
    cands = active_candidates(BOUNDS_ALL, PHYSICAL_PRIORS, conds,
                              theta=0.0, estimated=set())
    assert "K_archard" in cands and "tr_loose_gain" in cands


def test_damage_gating_matches_old_filter_semantics():
    no_dmg = active_candidates(BOUNDS_ALL, PHYSICAL_PRIORS,
                               [_cond("a"), _cond("b")],
                               theta=np.pi / 2, estimated=set())
    assert "c_D" not in no_dmg and "k_dmg_wear" not in no_dmg
    with_dmg = active_candidates(BOUNDS_ALL, PHYSICAL_PRIORS,
                                 [_cond("a"), _cond("b", damage=True)],
                                 theta=np.pi / 2, estimated=set())
    assert "c_D" in with_dmg and "k_dmg_wear" in with_dmg


def test_candidate_order_follows_bounds_order():
    cands = active_candidates(BOUNDS_ALL, PHYSICAL_PRIORS,
                              [_cond("a", damage=True)],
                              theta=np.pi / 2, estimated=set())
    assert cands == [n for n in BOUNDS_ALL if n in cands]


def test_unknown_fittable_name_raises_loudly():
    # O registro e a fonte unica: constante nova sem regra => erro alto,
    # nunca um drop silencioso (spec §5.5).
    bad_bounds = dict(BOUNDS_ALL, nova_constante=(0.0, 1.0))
    bad_priors = dict(PHYSICAL_PRIORS, nova_constante=0.5)
    with pytest.raises(KeyError):
        active_candidates(bad_bounds, bad_priors, [_cond("a")],
                          theta=np.pi / 2, estimated=set())


def test_regime_derivation_provenance_and_axes():
    r = regime_from_condition(_cond("s", delta_amp=0.0), theta=0.0,
                              estimated=True)
    assert r.has_axial and not r.has_transverse_slip
    assert r.F0_provenance == "estimated"
    r2 = regime_from_condition(_cond("t"), theta=np.pi / 2, estimated=False)
    assert r2.has_transverse_slip and not r2.has_axial
    assert r2.F0_provenance == "nominal"


# ------------------------------------------------------------ registry-truth
def _axial_trajectory(mat, n=150):
    """Axial puro force-mode: theta=0, sem delta_amp."""
    ana = DynamicStiffnessAnalyzer(M16, mat, 50e3)
    out = []
    for _ in range(n):
        ana.step_cycle(20e3, 0.0, 0.5)
        out.append(ana.state.F_0)
    return np.array(out)


def test_registry_truth_K_archard_inert_in_pure_axial():
    base = _axial_trajectory(JointMaterial())
    dobro = _axial_trajectory(JointMaterial(K_archard=2e-4))
    assert np.array_equal(base, dobro)   # parametro nunca lido => bit-identico


def test_registry_truth_tr_loose_gain_inert_in_pure_axial():
    base = _axial_trajectory(JointMaterial())
    dobro = _axial_trajectory(JointMaterial(tr_loose_gain=4.0))
    assert np.array_equal(base, dobro)


def test_registry_truth_transverse_constants_DO_act_under_shear():
    # contrapositiva: sob cisalhamento os mesmos parametros mudam a curva —
    # o teste de inercia acima nao passa vacuamente.
    def _shear(mat, n=150):
        ana = DynamicStiffnessAnalyzer(M16, mat, 50e3)
        out = []
        for _ in range(n):
            ana.step_cycle(20e3, np.pi / 2, 0.5, delta_amp=0.5e-3)
            out.append(ana.state.F_0)
        return np.array(out)
    assert not np.array_equal(_shear(JointMaterial()),
                              _shear(JointMaterial(K_archard=2e-4)))


def test_registry_truth_damage_constants_inert_without_damage_active():
    # Nivel calibrador: _material NAO injeta c_D/k_dmg_wear para condicao sem
    # dano — o engine fica nos defaults inativos (c_D=0, k_dmg_wear=0).
    cfg = SharedCalibrationConfig(geom=M16, conditions=[_cond("a")],
                                  theta=np.pi / 2, freq=0.5, n_cycles=10,
                                  bounds=BOUNDS_ALL)
    cal = SharedCalibrator(cfg)
    cal.constants["c_D"] = 8.0
    cal.constants["k_dmg_wear"] = 8.0
    m = cal._material(cfg.conditions[0])
    assert m.c_D == 0.0 and m.k_dmg_wear == 0.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_parameter_registry.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'bolt_analysis_studio.calibration.parameter_registry'`.

- [ ] **Step 3: Implement the registry module**

Create `src/bolt_analysis_studio/calibration/parameter_registry.py`:

```python
"""Registro declarativo de ativacao de parametros por regime de carregamento.

Spec: docs/superpowers/specs/2026-07-03-parameter-activation-registry-design.md.
Fonte UNICA que a calibracao (v1) e, futuramente, validacao e GUI consomem:
um parametro cujo mecanismo nao e excitado pelo regime tem coluna ~0 no
Jacobiano (MODEL_LEGITIMACY §4) — estruturalmente nao-identificavel — e por
isso nao deve ser pedido ao usuario nem oferecido ao otimizador.

Os predicados sao verificados contra as equacoes reais do engine pelos testes
registry-truth em tests/test_parameter_registry.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import (TYPE_CHECKING, Callable, Dict, Iterable, List, Set,
                    Tuple)

import numpy as np

if TYPE_CHECKING:                                   # sem import em runtime:
    from .shared_calibrator import ConditionSpec    # evita ciclo de imports


@dataclass(frozen=True)
class LoadingRegime:
    """Dimensoes de regime que os predicados enxergam (tabela completa,
    decisao §0.1 do spec): carregamento, estado da junta, termico e
    proveniencia de F0. Consumidores adotam as dimensoes conforme seus dados."""
    has_transverse_slip: bool
    has_axial: bool
    damage_active: bool
    delta_T_nonzero: bool = False   # calibracao atual: sempre False
    F0_provenance: str = "nominal"  # nominal | estimated | torque | measured


@dataclass(frozen=True)
class ParameterRule:
    name: str            # campo de JointMaterial (ou estado nomeado)
    layer: str           # 'physical' | 'damage' | 'state' | 'friction'
    fittable: bool       # candidato do SharedCalibrator?
    active: Callable[[LoadingRegime], bool]
    rationale: str       # uma frase fisica (tooltip futuro da GUI)
    role: str = ""       # campos com 2 papeis (mu_*: 'servico' | 'aperto')


def regime_from_condition(cond: "ConditionSpec", theta: float,
                          estimated: bool) -> LoadingRegime:
    """Deriva o regime de UMA condicao de calibracao. `theta` e global na
    SharedCalibrationConfig; a variacao por condicao vem de delta_amp e
    damage_active. `estimated` = o F0 desta condicao esta em estimate_F0."""
    has_tr = (abs(np.sin(theta)) > 1e-12) or (cond.delta_amp > 0.0)
    has_ax = abs(np.cos(theta)) > 1e-12
    return LoadingRegime(
        has_transverse_slip=has_tr,
        has_axial=has_ax,
        damage_active=cond.damage_active,
        delta_T_nonzero=False,
        F0_provenance="estimated" if estimated else "nominal",
    )


def _sempre(r: LoadingRegime) -> bool:
    return True


def _transversal(r: LoadingRegime) -> bool:
    return r.has_transverse_slip


def _dano(r: LoadingRegime) -> bool:
    return r.damage_active


def _aperto_por_torque(r: LoadingRegime) -> bool:
    return r.F0_provenance == "torque"


PARAMETER_REGISTRY: Tuple[ParameterRule, ...] = (
    # --- fisicos sempre ativos sob carga ciclica ---
    ParameterRule("emb_depth", "physical", True, _sempre,
                  "assentamento plastico ocorre sob qualquer ciclo"),
    ParameterRule("N_emb", "physical", True, _sempre,
                  "constante de tempo do assentamento"),
    ParameterRule("C_creep", "physical", True, _sempre,
                  "fluencia e funcao do tempo sob carga; dT!=0 promove de "
                  "opcional a obrigatorio nos consumidores de validacao"),
    # --- excitados por slip transversal ---
    ParameterRule("K_archard", "physical", True, _transversal,
                  "o wear do modelo e dirigido por slip transversal"),
    ParameterRule("tr_loose_gain", "physical", True, _transversal,
                  "fator 1 transversal do two-factor loosening"),
    # --- fisica de dano (generaliza o antigo filtro _DAMAGE_CONSTANTS) ---
    ParameterRule("c_D", "damage", True, _dano,
                  "taxa de crescimento do dano superficial"),
    ParameterRule("k_dmg_wear", "damage", True, _dano,
                  "amplificacao de wear pelo dano"),
    ParameterRule("W_ref", "damage", False, _dano,
                  "escala de energia de referencia do dano"),
    ParameterRule("k_dmg_mu", "damage", False, _dano,
                  "acoplamento dano -> perda de atrito"),
    # --- estados nomeados ---
    ParameterRule("D_init", "state", False, _dano,
                  "estado inicial de dano (junta reusada/reapertada)"),
    ParameterRule("emb_consumed_frac", "state", False, _dano,
                  "assentamento ja consumido (junta reusada)"),
    # --- incubacao (opt-in, default 0). Nuance de equacao descoberta no
    #     design: o gate multiplica TAMBEM o loosening axial, mas W_slip_acc
    #     so acumula com slip transversal => em axial puro com slip_onset_W>0
    #     o loosening ficaria permanentemente suprimido. Predicado honesto =
    #     sempre potencialmente ativo; ver MODEL_LEGITIMACY (changelog). ---
    ParameterRule("slip_onset_W", "physical", False, _sempre,
                  "gate de incubacao Hill (alimentado por W_slip_acc); "
                  "multiplica dF_0 de wear E loosening — util com slip "
                  "transversal, mas nao-inerte em axial (ver nuance)"),
    ParameterRule("slip_onset_sharpness", "physical", False, _sempre,
                  "expoente do gate de incubacao"),
    # --- atritos: dois papeis fisicos distintos ---
    ParameterRule("mu_thread", "friction", False, _transversal,
                  "servico: resistencia ao slip no filete", role="servico"),
    ParameterRule("mu_bearing", "friction", False, _transversal,
                  "servico: resistencia ao slip na flange", role="servico"),
    ParameterRule("mu_thread", "friction", False, _aperto_por_torque,
                  "aperto: conversao torque->F0", role="aperto"),
    ParameterRule("mu_bearing", "friction", False, _aperto_por_torque,
                  "aperto: conversao torque->F0", role="aperto"),
)


def active_candidates(bounds: Dict[str, tuple], priors: Dict[str, float],
                      conditions: Iterable["ConditionSpec"], theta: float,
                      estimated: Set[str]) -> List[str]:
    """Candidatos fitaveis do fit compartilhado: nome em bounds E priors E
    com regra fittable ativada por ALGUMA condicao do dataset. A ordem segue
    a ordem de `bounds` (preserva o determinismo da forward selection).

    Nome fitavel sem regra no registro => KeyError (o registro e o dono da
    lista; drop silencioso mascararia uma constante nova nunca fitada)."""
    pool = [n for n in bounds if n in priors]
    known_fittable = {r.name for r in PARAMETER_REGISTRY if r.fittable}
    unknown = [n for n in pool if n not in known_fittable]
    if unknown:
        raise KeyError(
            f"Constantes sem regra fittable no PARAMETER_REGISTRY: {unknown}"
            " — adicione a regra (o registro e a fonte unica, spec"
            " 2026-07-03 §5.5).")
    regimes = [regime_from_condition(c, theta, c.name in estimated)
               for c in conditions]
    ativos = {r.name for r in PARAMETER_REGISTRY
              if r.fittable and any(r.active(reg) for reg in regimes)}
    return [n for n in pool if n in ativos]
```

- [ ] **Step 4: Add exports**

In `src/bolt_analysis_studio/calibration/__init__.py`, add imports and extend `__all__` following the file's existing style:

```python
from .parameter_registry import (          # noqa: F401
    PARAMETER_REGISTRY, LoadingRegime, ParameterRule, active_candidates,
    regime_from_condition,
)
```
(and append `"PARAMETER_REGISTRY", "LoadingRegime", "ParameterRule", "active_candidates", "regime_from_condition"` to `__all__` if the file maintains one.)

- [ ] **Step 5: Syntax check + run tests**

Run: `python -c "import ast; ast.parse(open('src/bolt_analysis_studio/calibration/parameter_registry.py', encoding='utf-8').read()); print('OK')"`
Run: `python -m pytest tests/test_parameter_registry.py -v`
Expected: 10 PASS (registry-truth sims are short: ~150 cycles ×5 runs ≈ seconds).

- [ ] **Step 6: Commit**

```bash
git add src/bolt_analysis_studio/calibration/parameter_registry.py src/bolt_analysis_studio/calibration/__init__.py tests/test_parameter_registry.py
git commit -m "calib: registro de ativacao de parametros por regime (tabela + registry-truth)

Tabela declarativa parametro->predicado (slip transversal, dano/reuso,
termico reservado, proveniencia de F0) com testes registry-truth que
pinam cada predicado as equacoes do engine (trajetoria bit-identica em
regime inerte). Spec 2026-07-03 §1-2, §4.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: `SharedCalibrator` consumes the registry (parity-preserving)

**Files:**
- Modify: `src/bolt_analysis_studio/calibration/shared_calibrator.py` (`fit_parsimonious`, ~lines 166-171; module imports)
- Test: `tests/test_parameter_registry.py` (append integration tests)

**Interfaces:**
- Consumes: `active_candidates(bounds, priors, conditions, theta, estimated)` from Task 1.
- Produces: `fit_parsimonious` result dict gains key `"candidates": List[str]` (additive; existing keys unchanged). `_DAMAGE_CONSTANTS` REMAINS in the module — `_material()` still uses it to inject damage fields; only the candidate filter migrates.

- [ ] **Step 1: Write the failing integration tests**

Append to `tests/test_parameter_registry.py`:

```python
# ------------------------------------------- integracao com SharedCalibrator
def _mini_cfg(conds, theta=np.pi / 2):
    return SharedCalibrationConfig(geom=M16, conditions=conds, theta=theta,
                                   freq=0.5, n_cycles=20, bounds=BOUNDS_ALL,
                                   max_nfev=2)


def test_fit_parsimonious_exposes_registry_candidates_shear_parity():
    # Paridade com o filtro antigo: shear sem dano => todos exceto
    # c_D/k_dmg_wear; com dano => todos os 7.
    res = SharedCalibrator(_mini_cfg([_cond("a")])).fit_parsimonious(
        tol=10.0, max_constants=1)     # tol alto: nada e selecionado
    assert set(res["candidates"]) == {"emb_depth", "N_emb", "K_archard",
                                      "C_creep", "tr_loose_gain"}
    res_dmg = SharedCalibrator(
        _mini_cfg([_cond("a", damage=True)])).fit_parsimonious(
        tol=10.0, max_constants=1)
    assert set(res_dmg["candidates"]) == set(BOUNDS_ALL)


def test_fit_parsimonious_axial_only_drops_transverse_candidates():
    res = SharedCalibrator(
        _mini_cfg([_cond("ax", delta_amp=0.0)], theta=0.0)).fit_parsimonious(
        tol=10.0, max_constants=1)
    assert "K_archard" not in res["candidates"]
    assert "tr_loose_gain" not in res["candidates"]
    assert res["free_constants"] == []   # tol alto: baseline apenas
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_parameter_registry.py -k fit_parsimonious -v`
Expected: FAIL with `KeyError: 'candidates'` (key not in result dict yet).

- [ ] **Step 3: Swap the filter in `fit_parsimonious`**

In `src/bolt_analysis_studio/calibration/shared_calibrator.py`, add to the module imports (after the existing relative imports):

```python
from .parameter_registry import active_candidates
```

Then in `fit_parsimonious`, replace exactly these lines:

```python
        cands = [c for c in self.cfg.bounds if c in self.cfg.priors]
        if not any(c.damage_active for c in self.cfg.conditions):
            cands = [c for c in cands if c not in _DAMAGE_CONSTANTS]
```

with:

```python
        # Candidatos vem do registro de ativacao (spec 2026-07-03): so
        # constantes cujo mecanismo e excitado por ALGUMA condicao do
        # dataset. Generaliza o antigo filtro _DAMAGE_CONSTANTS (que segue
        # existindo para o _material injetar a fisica de dano).
        cands = active_candidates(self.cfg.bounds, self.cfg.priors,
                                  self.cfg.conditions, self.cfg.theta,
                                  set(self.cfg.estimate_F0))
```

And in the same method's return dict, add the `"candidates"` key (after `"free_constants"`):

```python
        return {
            "free_constants": free,
            "candidates": cands,
            ...
```
(keep every existing key exactly as is).

- [ ] **Step 4: Syntax check + run tests**

Run: `python -c "import ast; ast.parse(open('src/bolt_analysis_studio/calibration/shared_calibrator.py', encoding='utf-8').read()); print('OK')"`
Run: `python -m pytest tests/test_parameter_registry.py -v`
Expected: 12 PASS.

- [ ] **Step 5: Parity regression — the existing shared-calibrator suite must be untouched**

Run: `python -m pytest tests/test_shared_calibrator.py tests/test_calibration_profiles.py tests/test_shared_block_persistence.py -v`
Expected: all PASS (the synthetic fits select the same constants as before — identical candidate sets for these datasets by construction).

- [ ] **Step 6: Commit**

```bash
git add src/bolt_analysis_studio/calibration/shared_calibrator.py tests/test_parameter_registry.py
git commit -m "calib: fit_parsimonious consome o registro de ativacao (paridade preservada)

Filtro de candidatos migra do hard-code de dano para active_candidates;
datasets atuais produzem candidatos identicos (testes de paridade).
Resultado ganha a chave 'candidates' (aditivo). Spec 2026-07-03 §3.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Docs + full-suite regression

**Files:**
- Modify: `New_Theory/MODEL_LEGITIMACY.md` (§6 protocol list + §9 changelog)
- Modify: `CLAUDE.md` (calibration package section, gotchas, test-suite line)

**Interfaces:**
- Consumes: the committed registry (Task 1) and integration (Task 2); no code.
- Produces: docs synced; the full calibration suite green.

- [ ] **Step 1: MODEL_LEGITIMACY.md — §6 item + changelog**

In §6 ("Protocolo de legitimidade"), append a new numbered item after the existing item 5:

```markdown
6. **Não-identificabilidade estrutural tratada por construção.** O registro de
   ativação (`calibration/parameter_registry.py`, spec 2026-07-03) impede que
   constantes de mecanismos não excitados pelo regime de carregamento sequer
   virem candidatas do fit (ex.: dataset 100% axial nunca oferece `K_archard`/
   `tr_loose_gain`). Os predicados são **verificados contra o engine** pelos
   testes registry-truth (parâmetro inerte ⇒ trajetória bit-idêntica).
```

Append to the §9 changelog table:

```markdown
| 2026-07-03 | Registro de ativação de parâmetros por regime (`parameter_registry.py`): tabela declarativa (slip transversal, dano/reuso, ΔT reservado, proveniência de F₀) consumida pelo `fit_parsimonious` (candidatos idênticos nos datasets atuais — paridade testada). Testes registry-truth pinam predicados às equações. **Nuance descoberta:** o gate de incubação (`slip_onset_W`) multiplica também o loosening axial, mas `W_slip_acc` só acumula com slip transversal ⇒ em axial puro com `slip_onset_W>0` o loosening ficaria permanentemente suprimido — comportamento atual do engine, documentado no registro (predicado "sempre"), a revisitar se o track axial usar incubação. |
```

- [ ] **Step 2: CLAUDE.md — three edits**

1. In the "V2 calibration package (`src/.../calibration/`)" architecture list, add one bullet:
```markdown
- `parameter_registry.py` — **activation registry** (spec 2026-07-03): declarative parameter→predicate table (`LoadingRegime`: transverse slip, damage, ΔT reserved, F0 provenance); `active_candidates` feeds `fit_parsimonious` so mechanisms not excited by the dataset's regime are never offered to the optimizer. Registry-truth tests pin predicates to the engine. Future consumers: `.msd` validation + GUI gating.
```
2. In "Key gotchas — V2 staged calibration" add one bullet:
```markdown
- **New fittable constant? Add its `ParameterRule` first** — `active_candidates` raises `KeyError` for a bounds∩priors name with no fittable rule (loud by design; the registry owns the candidate list). `fit_parsimonious` results now include `"candidates"`.
```
3. In the calibration test-suite command line, append `tests/test_parameter_registry.py`.

- [ ] **Step 3: Full-suite regression**

Run: `python -m pytest tests/test_surface_damage.py tests/test_staged_calibrator.py tests/test_calibration_segmentation.py tests/test_calibration_decomposition.py tests/test_calibration_profiles.py tests/test_calibration_server.py tests/test_v2_solver_preload.py tests/test_slip_onset_incubation.py tests/test_case_study_models.py tests/test_calibration_trim.py tests/test_v2_calibration.py tests/test_embedding_state_based.py tests/test_shared_block_persistence.py tests/test_shared_calibrator.py tests/test_parameter_registry.py -q`
Expected: ~76 passed (64 existing + 12 new), 2 pre-existing ISO-retention warnings, ~4-6 min.

- [ ] **Step 4: Commit**

```bash
git add New_Theory/MODEL_LEGITIMACY.md CLAUDE.md
git commit -m "docs: registro de ativacao no protocolo de legitimidade + CLAUDE.md

Nao-identificabilidade estrutural por construcao (§6.6 + changelog,
incl. nuance do slip_onset_W gateando loosening axial). Gotcha da regra
nova + suite com test_parameter_registry.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```
