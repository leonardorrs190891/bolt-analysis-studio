# Alavanca de calibração por estágio + surface_damage — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dar alavanca de calibração por estágio (otimizador sequencial com travas + tuner interativo instrumentado, fonte única Python) e adicionar a variável de estado `surface_damage` pro caso reaperto/TP7.

**Architecture:** O `DynamicStiffnessAnalyzer` (Python) vira a única implementação do modelo. Um novo pacote `calibration/` adiciona segmentação, decomposição por mecanismo, calibrador em estágios, persistência de perfis e um servidor HTTP local. O `calibration_tuner.html` é refatorado de "porta JS do modelo" para cliente fino do servidor.

**Tech Stack:** Python 3 (numpy, scipy.optimize), stdlib `http.server`, pytest. Frontend: HTML/JS + Plotly (já em uso).

## Global Constraints

- `encoding='utf-8'` em **todo** I/O de arquivo (charmap codec error no Windows).
- Syntax-check após cada edição de `.py`: `python3 -c "import ast; ast.parse(open('PATH', encoding='utf-8').read()); print('OK')"`.
- Tuners de mecanismo default `1.0`; o mecanismo de dano nasce **inativo** (`c_D=0.0`, `k_dmg_mu=0.0`) pra não alterar o perfil nova atual.
- Defaults físicos no `JointMaterial`, nunca via multiplicador de runtime (guideline #10).
- `step_cycle(F_amp, theta_load, freq=1.0, delta_amp=None)` — disp-mode (delta_amp dado) pros ensaios Junker ±0.5mm.
- Geometria M16 padrão: `JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3, pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)`. Loading: `F0=50000`, `F_amp=20000`, `theta=pi/2`, `freq=0.5`, `delta_amp=0.5e-3`, `n_cycles=2500`.
- CSVs de referência M16 em `New_Theory/M16_shear_<name>.csv`: 2 colunas `cycle,F_over_F0`, header na linha 1.
- Nomes de mecanismo (atributo `.name`): `"embedding"`, `"creep"`, `"wear"`, `"rotational_loosening"`.
- Caminho do engine: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py`.
- Rodar testes: `python3 -m pytest tests/<arquivo> -v` a partir da raiz do repo.

---

## File Structure

**Engine (modificado):**
- `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` — adiciona `SlowState.D`, `CycleSnapshot.dF_0_by_mech` + `CycleSnapshot.D`, campos de dano no `JointMaterial`, helper `mu_bearing_eff`, atualização de D no `step_cycle`, param `initial_damage` no analyzer.

**Pacote novo `src/bolt_analysis_studio/calibration/`:**
- `__init__.py` — exports públicos.
- `segmentation.py` — `Stage`, `StageSegmentation` (partição em janelas + MAE por segmento).
- `decomposition.py` — `MechanismDecomposition` (shares de dF_0 por mecanismo por segmento).
- `profiles.py` — load/save atômico do `New_Theory/joint_calibrations.json`.
- `staged_calibrator.py` — `CalibrationConfig`, `StagedCalibrator` (fit sequencial com travas + regularização física).
- `server.py` — funções puras `handle_simulate/handle_calibrate/handle_profiles` + `BaseHTTPRequestHandler` + `serve()`.

**Tooling (refatorado):**
- `New_Theory/calibrate_4_profiles.py` — usa `StagedCalibrator`.
- `New_Theory/calibration_tuner.html` — cliente fino (remove modelo JS, adiciona travas, janelas arrastáveis, MAE por segmento, overlay de mecanismo, mini-plot D(N), botões auto-fit).

**Testes novos:**
- `tests/test_surface_damage.py` (Tasks 1–4)
- `tests/test_calibration_segmentation.py` (Task 5)
- `tests/test_calibration_decomposition.py` (Task 6)
- `tests/test_calibration_profiles.py` (Task 7)
- `tests/test_staged_calibrator.py` (Tasks 8)
- `tests/test_calibration_server.py` (Task 10)

---

## Task 1: Decomposição por mecanismo no CycleSnapshot

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (`CycleSnapshot` ~202-212; `step_cycle` ~715-764)
- Test: `tests/test_surface_damage.py`

**Interfaces:**
- Produces: `CycleSnapshot.dF_0_by_mech: Dict[str, float]` — mapeia nome do mecanismo → seu `dF_0` no ciclo. `sum(dF_0_by_mech.values())` == variação total de F_0 do ciclo (antes do clamp em 0).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_surface_damage.py
import numpy as np
import pytest
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)

M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)


def _analyzer(mat=None, initial_damage=0.0):
    return DynamicStiffnessAnalyzer(M16, mat or JointMaterial(), 50_000.0,
                                    initial_damage=initial_damage)


def test_dF0_by_mech_sums_to_total():
    ana = _analyzer()
    prev = ana.state.F_0
    snap = ana.step_cycle(20_000.0, np.pi / 2, 0.5, delta_amp=0.5e-3)
    # F_0 ficou positivo neste 1o ciclo (sem clamp), entao a soma das
    # contribuicoes por mecanismo == variacao total de F_0
    assert ana.state.F_0 > 0
    total = sum(snap.dF_0_by_mech.values())
    assert snap.dF_0_by_mech  # nao vazio
    assert abs(total - (ana.state.F_0 - prev)) < 1e-9
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_surface_damage.py::test_dF0_by_mech_sums_to_total -v`
Expected: FAIL com `AttributeError: 'CycleSnapshot' object has no attribute 'dF_0_by_mech'`.

- [ ] **Step 3: Add the field to CycleSnapshot**

Em `CycleSnapshot` (após `per_mechanism: Dict[str, float]`), adicione o campo:

```python
@dataclass
class CycleSnapshot:
    """Snapshot per-cycle pra diagnóstico/plot."""
    cycle: int
    F_0: float
    delta_U_stored: float
    W_ext_cycle: float
    W_diss_cycle: float
    Phi_eff: float
    slip_fraction: float
    per_mechanism: Dict[str, float]
    dF_0_by_mech: Dict[str, float] = field(default_factory=dict)
```

- [ ] **Step 4: Capture dF_0 per mechanism in step_cycle**

No loop `for mech in self.losses:` de `step_cycle`, logo após `dF_0_total += res["dF_0"]`, adicione a captura. O bloco fica:

```python
        per_mech: Dict[str, float] = {}
        dF_0_by_mech: Dict[str, float] = {}
        slip_fraction_cycle = 0.0
        dF_0_total = 0.0
        dE_diss_total = W_visc_c   # damping viscoso já entra na conta

        for mech in self.losses:
            res = mech.rate(self.state, self.geom, self.mat,
                            F_amp, theta_load, freq, n,
                            slip_amp_override=slip_amp_override)
            dF_0_total += res["dF_0"]
            dF_0_by_mech[mech.name] = res["dF_0"]
            dE = res["dE_dissipated"]
```

E no `CycleSnapshot(...)` ao final, passe o dict:

```python
        snap = CycleSnapshot(
            cycle=n,
            F_0=self.state.F_0,
            delta_U_stored=delta_U,
            W_ext_cycle=W_ext_c,
            W_diss_cycle=dE_diss_total,
            Phi_eff=Phi_eff(self.state, self.geom, self.mat),
            slip_fraction=slip_fraction_cycle,
            per_mechanism=per_mech,
            dF_0_by_mech=dF_0_by_mech,
        )
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m pytest tests/test_surface_damage.py::test_dF0_by_mech_sums_to_total -v`
Expected: PASS.

- [ ] **Step 6: Syntax-check and commit**

```bash
python3 -c "import ast; ast.parse(open('src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py', encoding='utf-8').read()); print('OK')"
git add src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py tests/test_surface_damage.py
git commit -m "numerical: dF_0_by_mech no CycleSnapshot (base da decomposicao)"
```

---

## Task 2: Campo de dano no estado + material + analyzer

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (`SlowState` ~154-169; `JointMaterial` ~76-147; `DynamicStiffnessAnalyzer.__init__` ~630-648)
- Test: `tests/test_surface_damage.py`

**Interfaces:**
- Produces: `SlowState.D: float = 0.0`; `JointMaterial.c_D/W_ref/k_dmg_mu/k_damage_scale`; `DynamicStiffnessAnalyzer(geom, mat, initial_preload, loss_mechanisms=None, initial_damage=0.0)`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_surface_damage.py (append)
def test_damage_defaults_inactive():
    mat = JointMaterial()
    assert mat.c_D == 0.0
    assert mat.k_dmg_mu == 0.0
    assert mat.k_damage_scale == 1.0
    assert mat.W_ref > 0.0
    ana = _analyzer()                 # initial_damage default 0
    assert ana.state.D == 0.0
    for _ in range(200):
        ana.step_cycle(20_000.0, np.pi / 2, 0.5, delta_amp=0.5e-3)
    # dano inativo por default => D nunca cresce
    assert ana.state.D == 0.0


def test_initial_damage_sets_state():
    ana = _analyzer(initial_damage=0.3)
    assert ana.state.D == 0.3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_surface_damage.py::test_damage_defaults_inactive -v`
Expected: FAIL com `AttributeError: 'JointMaterial' object has no attribute 'c_D'`.

- [ ] **Step 3: Add D to SlowState**

Em `SlowState`, adicione o campo após `F_0_init`:

```python
@dataclass
class SlowState:
    """Vetor s — memória cumulativa entre ciclos (slow timescale)."""
    F_0: float                       # N — pré-carga residual
    delta_emb: float = 0.0           # m
    delta_creep: float = 0.0         # m
    delta_wear: float = 0.0          # m
    theta_loose: float = 0.0         # rad
    F_0_init: float = 0.0            # N — pré-carga inicial (reference)
    D: float = 0.0                   # surface_damage [0,1]
```

- [ ] **Step 4: Add damage fields to JointMaterial**

Em `JointMaterial`, após `tr_loose_gain: float = 2.0`, adicione o bloco de dano (inativo por default):

```python
    # ========================================================
    # SURFACE DAMAGE (reaperto/TP7). Inativo por default
    # (c_D=0, k_dmg_mu=0) => engine reproduz comportamento atual.
    # Perfis reaperto/reusada ligam via calibracao.
    # ========================================================
    c_D: float = 0.0            # taxa de crescimento do dano [-]
    W_ref: float = 1.0e4        # escala de energia de referencia [J]
    k_dmg_mu: float = 0.0       # acoplamento dano->perda de atrito [-]
    k_damage_scale: float = 1.0 # tuner do dano (multiplicador)
```

- [ ] **Step 5: Add initial_damage param to the analyzer**

Em `DynamicStiffnessAnalyzer.__init__`, adicione o parâmetro e propague pra `SlowState`:

```python
    def __init__(self,
                 geometry: JointGeometry,
                 material: JointMaterial,
                 initial_preload: float,
                 loss_mechanisms: Optional[List[LossMechanism]] = None,
                 initial_damage: float = 0.0):
        self.geom = geometry
        self.mat = material
        self.state = SlowState(F_0=initial_preload,
                               F_0_init=initial_preload,
                               D=initial_damage)
```

(o resto do `__init__` permanece igual)

- [ ] **Step 6: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_surface_damage.py -v`
Expected: PASS (3 testes até agora).

- [ ] **Step 7: Syntax-check and commit**

```bash
python3 -c "import ast; ast.parse(open('src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py', encoding='utf-8').read()); print('OK')"
git add src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py tests/test_surface_damage.py
git commit -m "numerical: campo surface_damage D + params de dano inativos por default"
```

---

## Task 3: Atrito modulado por dano (mu_bearing_eff) + roteamento

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (`F_slip_transverse` ~263-265; `T_resistance` ~268-274; `WearLoss.rate` ~513-537; nova função após `T_resistance`)
- Test: `tests/test_surface_damage.py`

**Interfaces:**
- Produces: `mu_bearing_eff(state: SlowState, mat: JointMaterial) -> float` — `mu_bearing * max(1 - k_dmg_mu*D, 0)`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_surface_damage.py (append)
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    mu_bearing_eff, F_slip_transverse, SlowState,
)


def test_mu_eff_inert_when_no_coupling():
    mat = JointMaterial()                 # k_dmg_mu=0
    s = SlowState(F_0=50_000.0, F_0_init=50_000.0, D=0.7)
    # sem coupling, dano nao afeta atrito (backward-compat)
    assert mu_bearing_eff(s, mat) == mat.mu_bearing


def test_mu_eff_reduces_with_damage():
    mat = JointMaterial(k_dmg_mu=1.0)
    s = SlowState(F_0=50_000.0, F_0_init=50_000.0, D=0.5)
    assert abs(mu_bearing_eff(s, mat) - 0.5 * mat.mu_bearing) < 1e-12
    # F_slip cai junto
    s0 = SlowState(F_0=50_000.0, F_0_init=50_000.0, D=0.0)
    assert F_slip_transverse(s, mat) < F_slip_transverse(s0, mat)


def test_mu_eff_clamps_nonnegative():
    mat = JointMaterial(k_dmg_mu=2.0)
    s = SlowState(F_0=50_000.0, F_0_init=50_000.0, D=0.9)  # 1-1.8 < 0
    assert mu_bearing_eff(s, mat) == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_surface_damage.py::test_mu_eff_inert_when_no_coupling -v`
Expected: FAIL com `ImportError: cannot import name 'mu_bearing_eff'`.

- [ ] **Step 3: Add the helper function**

Adicione logo após `T_resistance` (~linha 274):

```python
def mu_bearing_eff(state: SlowState, mat: JointMaterial) -> float:
    """Atrito de bearing modulado por surface_damage.

    mu_eff = mu_bearing · (1 − k_dmg_mu·D), com clamp em 0.
    Com D=0 ou k_dmg_mu=0 retorna mu_bearing exato (backward-compat).
    """
    factor = 1.0 - mat.k_dmg_mu * state.D
    return mat.mu_bearing * max(factor, 0.0)
```

- [ ] **Step 4: Route F_slip_transverse and T_resistance through it**

Substitua `F_slip_transverse`:

```python
def F_slip_transverse(state: SlowState, mat: JointMaterial) -> float:
    """Threshold de slip transversal (Pai-Hess), atrito modulado por dano."""
    return SLIP_ONSET_PAI_HESS * mu_bearing_eff(state, mat) * max(state.F_0, 0.0)
```

Em `T_resistance`, troque o termo de bearing `mat.mu_bearing` por `mu_bearing_eff(state, mat)`:

```python
def T_resistance(state: SlowState, geom: JointGeometry,
                 mat: JointMaterial) -> float:
    """Torque resistente (atrito filete + bearing, bearing modulado por dano)."""
    F0 = max(state.F_0, 0.0)
    T_thr = mat.mu_thread * F0 * geom.d_2 / (2.0 * np.cos(THREAD_FLANK_ANGLE))
    T_brg = mu_bearing_eff(state, mat) * F0 * geom.r_bearing
    return T_thr + T_brg
```

- [ ] **Step 5: Route WearLoss friction dissipation through it**

Em `WearLoss.rate`, troque `mat.mu_bearing` no cálculo de `dE` (a difusão de Archard `d_wear` usa `K_archard`, não muda):

```python
        dF_0 = -geom.k_b * d_wear
        # Friction dissipation (atrito × distância), atrito modulado por dano
        dE = k_scale * mu_bearing_eff(state, mat) * F_clamp * slip_dist
        return dict(dF_0=dF_0, dE_dissipated=dE,
                    ds=dict(delta_wear=d_wear))
```

- [ ] **Step 5b: Route W_ext_per_cycle through it (conservação de energia)**

Em `W_ext_per_cycle` (~linha 409), a loop de hysteresis usa a força de atrito **real** — que cai com o dano. Troque `mat.mu_bearing` por `mu_bearing_eff(state, mat)` pra que o trabalho externo de atrito e a dissipação de slip escalem juntos (mantém o resíduo de conservação ≈ 0 quando D>0):

```python
    slip_amp = resolve_transverse_slip(state, mat, F_amp, theta_load, delta_amp)
    if slip_amp <= 0:
        return 0.0
    return 4.0 * mu_bearing_eff(state, mat) * state.F_0 * slip_amp
```

(Com D=0 ou k_dmg_mu=0, `mu_bearing_eff` retorna `mu_bearing` exato → W_ext inalterado, backward-compat preservado.)

- [ ] **Step 6: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_surface_damage.py -v`
Expected: PASS (todos).

- [ ] **Step 7: Syntax-check and commit**

```bash
python3 -c "import ast; ast.parse(open('src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py', encoding='utf-8').read()); print('OK')"
git add src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py tests/test_surface_damage.py
git commit -m "numerical: mu_bearing_eff (atrito modulado por dano) + roteamento"
```

---

## Task 4: Crescimento do dano no step_cycle + D no snapshot

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (`step_cycle` — após update de F_0 ~747-764; `CycleSnapshot` ~202-213)
- Test: `tests/test_surface_damage.py`

**Interfaces:**
- Produces: `CycleSnapshot.D: float` (valor de D ao fim do ciclo). Lei de crescimento `dD = k_damage_scale·c_D·(W_slip_cycle/W_ref)·(1−D)` com `W_slip_cycle = dE_wear + dE_loose`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_surface_damage.py (append)
def test_damage_grows_bounded_monotonic():
    mat = JointMaterial(c_D=1.0, W_ref=1.0e4, k_dmg_mu=1.0)
    ana = _analyzer(mat=mat, initial_damage=0.3)
    Ds = [ana.state.D]
    for _ in range(500):
        snap = ana.step_cycle(20_000.0, np.pi / 2, 0.5, delta_amp=0.5e-3)
        Ds.append(snap.D)
    assert all(0.0 <= d <= 1.0 for d in Ds)          # limitado
    assert all(b >= a - 1e-12 for a, b in zip(Ds, Ds[1:]))  # monotônico
    assert Ds[-1] > 0.3                               # cresceu


def test_damage_accelerates_loss():
    # reaperto-like (D_init>0, dano ativo) perde mais que nova-like (sem dano)
    mat_dmg = JointMaterial(c_D=1.0, W_ref=1.0e4, k_dmg_mu=1.0)
    ana_dmg = _analyzer(mat=mat_dmg, initial_damage=0.3)
    ana_nova = _analyzer()  # dano inativo
    for _ in range(800):
        ana_dmg.step_cycle(20_000.0, np.pi / 2, 0.5, delta_amp=0.5e-3)
        ana_nova.step_cycle(20_000.0, np.pi / 2, 0.5, delta_amp=0.5e-3)
    assert ana_dmg.state.F_0 < ana_nova.state.F_0


def test_energy_conservation_with_damage():
    # dano brando: F_0 fica longe do colapso (regime limpo, sem clamp em 0).
    # Atrito modulado por dano roteado em W_ext + wear + loose => entrada e
    # dissipacao escalam juntas e o residuo segue pequeno.
    mat = JointMaterial(c_D=0.5, W_ref=1.0e4, k_dmg_mu=0.5)
    ana = _analyzer(mat=mat, initial_damage=0.1)
    for _ in range(300):
        ana.step_cycle(20_000.0, np.pi / 2, 0.5, delta_amp=0.5e-3)
    assert ana.state.F_0 > 0          # nao colapsou (regime testavel)
    e = ana.energy
    total = abs(e.W_ext) + abs(e.U_released) + abs(e.W_diss_total) + 1.0
    assert abs(e.conservation_residual) / total < 1e-2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_surface_damage.py::test_damage_grows_bounded_monotonic -v`
Expected: FAIL — `snap.D` ainda não existe (`AttributeError`) ou D não cresce.

- [ ] **Step 3: Add D field to CycleSnapshot**

Adicione ao `CycleSnapshot` (após `dF_0_by_mech`):

```python
    dF_0_by_mech: Dict[str, float] = field(default_factory=dict)
    D: float = 0.0
```

- [ ] **Step 4: Update D in step_cycle**

Em `step_cycle`, após o bloco `# ===== 4) Atualiza F_0 e U_stored` (logo depois de `self.energy.U_stored = new_U` e `delta_U = ...`), adicione o update de dano. Os mecanismos já leram o D de início de ciclo; agora D evolui pro próximo ciclo:

```python
        # ===== 4.5) Atualiza surface_damage D
        # Driver: trabalho de slip deste ciclo (wear + loosening), nao
        # embedding/creep/viscoso. Mecanismos ja usaram o D de inicio de
        # ciclo (sem dependencia de ordem). Inativo se c_D=0.
        W_slip_cycle = (per_mech.get("wear", 0.0)
                        + per_mech.get("rotational_loosening", 0.0))
        if self.mat.c_D > 0.0 and self.mat.W_ref > 0.0:
            dD = (self.mat.k_damage_scale * self.mat.c_D
                  * (W_slip_cycle / self.mat.W_ref) * (1.0 - self.state.D))
            self.state.D = min(1.0, max(0.0, self.state.D + dD))
```

E no `CycleSnapshot(...)`, adicione `D=self.state.D`:

```python
            per_mechanism=per_mech,
            dF_0_by_mech=dF_0_by_mech,
            D=self.state.D,
        )
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_surface_damage.py -v`
Expected: PASS (todos os testes de dano).

- [ ] **Step 6: Syntax-check and commit**

```bash
python3 -c "import ast; ast.parse(open('src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py', encoding='utf-8').read()); print('OK')"
git add src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py tests/test_surface_damage.py
git commit -m "numerical: crescimento de surface_damage no step_cycle + D no snapshot"
```

---

## Task 5: StageSegmentation

**Files:**
- Create: `src/bolt_analysis_studio/calibration/__init__.py`
- Create: `src/bolt_analysis_studio/calibration/segmentation.py`
- Test: `tests/test_calibration_segmentation.py`

**Interfaces:**
- Produces:
  - `Stage(name: str, n_start: float, n_end: float, owned_tuners: list[str])`
  - `StageSegmentation(n_I: float, n_II: float, n_end: float)` com `.stages: list[Stage]`, `.segment_of(n: float) -> str`, `.mae_per_segment(sim_N, sim_ratio, ref_N, ref_ratio) -> dict[str, float|None]`.
  - Estágios: `"I"` [0, n_I), `"II"` [n_I, n_II), `"III"` [n_II, n_end]. Tuners: I→`["k_emb_scale"]`, II→`["k_wear_scale_tr","k_loose_scale_tr","Phi_tr_correction","k_damage_scale"]`, III→`["k_creep_scale"]`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_calibration_segmentation.py
import numpy as np
import pytest
from bolt_analysis_studio.calibration.segmentation import Stage, StageSegmentation


def test_segments_cover_range_no_overlap():
    seg = StageSegmentation(n_I=100, n_II=1000, n_end=2500)
    assert seg.segment_of(0) == "I"
    assert seg.segment_of(99) == "I"
    assert seg.segment_of(100) == "II"      # fronteira pertence ao proximo
    assert seg.segment_of(999) == "II"
    assert seg.segment_of(1000) == "III"
    assert seg.segment_of(2500) == "III"    # n_end inclusivo
    assert [s.name for s in seg.stages] == ["I", "II", "III"]


def test_owned_tuners():
    seg = StageSegmentation(n_I=100, n_II=1000, n_end=2500)
    owners = {s.name: s.owned_tuners for s in seg.stages}
    assert owners["I"] == ["k_emb_scale"]
    assert owners["III"] == ["k_creep_scale"]
    assert "k_loose_scale_tr" in owners["II"]
    assert "k_damage_scale" in owners["II"]


def test_mae_per_segment_zero_when_equal():
    seg = StageSegmentation(n_I=100, n_II=1000, n_end=2500)
    sim_N = np.arange(0, 2501)
    sim_ratio = np.linspace(1.0, 0.2, 2501)
    ref_N = np.array([50, 500, 2000])
    ref_ratio = np.interp(ref_N, sim_N, sim_ratio)
    mae = seg.mae_per_segment(sim_N, sim_ratio, ref_N, ref_ratio)
    assert mae["I"] < 1e-9 and mae["II"] < 1e-9 and mae["III"] < 1e-9


def test_mae_per_segment_known_offset_and_empty():
    seg = StageSegmentation(n_I=100, n_II=1000, n_end=2500)
    sim_N = np.arange(0, 2501)
    sim_ratio = np.full(2501, 0.5)
    ref_N = np.array([50, 2000])           # nada na janela II
    ref_ratio = np.array([0.6, 0.4])       # offset 0.1 em ambas
    mae = seg.mae_per_segment(sim_N, sim_ratio, ref_N, ref_ratio)
    assert abs(mae["I"] - 0.1) < 1e-9
    assert mae["II"] is None               # sem pontos de referencia
    assert abs(mae["III"] - 0.1) < 1e-9
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_calibration_segmentation.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'bolt_analysis_studio.calibration'`.

- [ ] **Step 3: Create the package init**

```python
# src/bolt_analysis_studio/calibration/__init__.py
"""Ferramentas de calibração por estágio do DynamicStiffnessAnalyzer."""
from .segmentation import Stage, StageSegmentation

__all__ = ["Stage", "StageSegmentation"]
```

- [ ] **Step 4: Implement segmentation**

```python
# src/bolt_analysis_studio/calibration/segmentation.py
"""Particiona a curva de loosening em estágios (janelas de ciclos) ajustáveis
e calcula MAE por segmento contra uma curva de referência."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

import numpy as np

# Tuners "donos" de cada estágio (quem domina fisicamente aquela janela)
_OWNED = {
    "I": ["k_emb_scale"],
    "II": ["k_wear_scale_tr", "k_loose_scale_tr", "Phi_tr_correction",
           "k_damage_scale"],
    "III": ["k_creep_scale"],
}


@dataclass
class Stage:
    name: str
    n_start: float
    n_end: float
    owned_tuners: List[str]


class StageSegmentation:
    """Três estágios com fronteiras ajustáveis: I [0,n_I), II [n_I,n_II),
    III [n_II, n_end]. n_end é inclusivo no último estágio."""

    def __init__(self, n_I: float, n_II: float, n_end: float):
        if not (0 < n_I < n_II <= n_end):
            raise ValueError(f"Esperado 0 < n_I < n_II <= n_end; "
                             f"recebi n_I={n_I}, n_II={n_II}, n_end={n_end}")
        self.n_I = float(n_I)
        self.n_II = float(n_II)
        self.n_end = float(n_end)
        self.stages: List[Stage] = [
            Stage("I", 0.0, self.n_I, list(_OWNED["I"])),
            Stage("II", self.n_I, self.n_II, list(_OWNED["II"])),
            Stage("III", self.n_II, self.n_end, list(_OWNED["III"])),
        ]

    def segment_of(self, n: float) -> str:
        if n < self.n_I:
            return "I"
        if n < self.n_II:
            return "II"
        return "III"

    def mae_per_segment(self, sim_N: Sequence[float], sim_ratio: Sequence[float],
                        ref_N: Sequence[float], ref_ratio: Sequence[float]
                        ) -> Dict[str, Optional[float]]:
        """MAE de |sim_interp(ref_N) − ref_ratio| por estágio. None se o
        estágio não tem ponto de referência."""
        sim_N = np.asarray(sim_N, dtype=float)
        sim_ratio = np.asarray(sim_ratio, dtype=float)
        ref_N = np.asarray(ref_N, dtype=float)
        ref_ratio = np.asarray(ref_ratio, dtype=float)
        sim_at_ref = np.interp(ref_N, sim_N, sim_ratio)
        abs_err = np.abs(sim_at_ref - ref_ratio)
        out: Dict[str, Optional[float]] = {}
        for stage in self.stages:
            mask = np.array([self.segment_of(n) == stage.name for n in ref_N])
            out[stage.name] = float(np.mean(abs_err[mask])) if mask.any() else None
        return out
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_calibration_segmentation.py -v`
Expected: PASS (4 testes).

- [ ] **Step 6: Syntax-check and commit**

```bash
python3 -c "import ast; ast.parse(open('src/bolt_analysis_studio/calibration/segmentation.py', encoding='utf-8').read()); print('OK')"
git add src/bolt_analysis_studio/calibration/__init__.py src/bolt_analysis_studio/calibration/segmentation.py tests/test_calibration_segmentation.py
git commit -m "calibration: StageSegmentation (janelas ajustaveis + MAE por segmento)"
```

---

## Task 6: MechanismDecomposition

**Files:**
- Create: `src/bolt_analysis_studio/calibration/decomposition.py`
- Modify: `src/bolt_analysis_studio/calibration/__init__.py`
- Test: `tests/test_calibration_decomposition.py`

**Interfaces:**
- Consumes: `CycleSnapshot.dF_0_by_mech` (Task 1), `StageSegmentation.segment_of` (Task 5).
- Produces: `MechanismDecomposition.shares_per_segment(history, segmentation) -> dict[str, dict]` — por estágio: `{"shares": {mech: frac}, "dominant": mech}`. Fracs somam ~1.0 (ou estágio vazio → `{}`/`None`).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_calibration_decomposition.py
import pytest
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import CycleSnapshot
from bolt_analysis_studio.calibration.segmentation import StageSegmentation
from bolt_analysis_studio.calibration.decomposition import MechanismDecomposition


def _snap(cycle, dF):
    return CycleSnapshot(cycle=cycle, F_0=0.0, delta_U_stored=0.0,
                         W_ext_cycle=0.0, W_diss_cycle=0.0, Phi_eff=0.0,
                         slip_fraction=0.0, per_mechanism={}, dF_0_by_mech=dF)


def test_shares_sum_to_one_and_dominant():
    seg = StageSegmentation(n_I=2, n_II=4, n_end=6)
    hist = [
        _snap(1, {"embedding": -8.0, "loosening": -2.0}),   # estagio I
        _snap(3, {"embedding": -1.0, "loosening": -9.0}),   # estagio II
        _snap(5, {"creep": -5.0}),                          # estagio III
    ]
    out = MechanismDecomposition.shares_per_segment(hist, seg)
    assert abs(sum(out["I"]["shares"].values()) - 1.0) < 1e-9
    assert out["I"]["dominant"] == "embedding"
    assert out["II"]["dominant"] == "loosening"
    assert out["III"]["dominant"] == "creep"


def test_empty_segment_is_none():
    seg = StageSegmentation(n_I=2, n_II=4, n_end=6)
    hist = [_snap(1, {"embedding": -8.0})]   # so estagio I tem dados
    out = MechanismDecomposition.shares_per_segment(hist, seg)
    assert out["II"] is None and out["III"] is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_calibration_decomposition.py -v`
Expected: FAIL com `ModuleNotFoundError: ... 'decomposition'`.

- [ ] **Step 3: Implement decomposition**

```python
# src/bolt_analysis_studio/calibration/decomposition.py
"""Atribui a perda de pré-carga (dF_0) de cada ciclo a cada mecanismo e
agrega o share por estágio."""
from __future__ import annotations

from typing import Dict, List, Optional

from .segmentation import StageSegmentation


class MechanismDecomposition:
    @staticmethod
    def shares_per_segment(history: List, segmentation: StageSegmentation
                           ) -> Dict[str, Optional[dict]]:
        """Para cada estágio, soma |dF_0| por mecanismo sobre os ciclos
        daquele estágio e devolve shares (somam 1.0) + dominante. Estágio
        sem ciclos → None."""
        # acumula |dF_0| por estagio -> mecanismo
        acc: Dict[str, Dict[str, float]] = {s.name: {} for s in segmentation.stages}
        for snap in history:
            stage = segmentation.segment_of(snap.cycle)
            bucket = acc[stage]
            for mech, dF in snap.dF_0_by_mech.items():
                bucket[mech] = bucket.get(mech, 0.0) + abs(dF)
        out: Dict[str, Optional[dict]] = {}
        for name, bucket in acc.items():
            total = sum(bucket.values())
            if total <= 0.0:
                out[name] = None
                continue
            shares = {m: v / total for m, v in bucket.items()}
            dominant = max(shares, key=shares.get)
            out[name] = {"shares": shares, "dominant": dominant}
        return out
```

- [ ] **Step 4: Export from package init**

```python
# src/bolt_analysis_studio/calibration/__init__.py
"""Ferramentas de calibração por estágio do DynamicStiffnessAnalyzer."""
from .segmentation import Stage, StageSegmentation
from .decomposition import MechanismDecomposition

__all__ = ["Stage", "StageSegmentation", "MechanismDecomposition"]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_calibration_decomposition.py -v`
Expected: PASS (2 testes).

- [ ] **Step 6: Syntax-check and commit**

```bash
python3 -c "import ast; ast.parse(open('src/bolt_analysis_studio/calibration/decomposition.py', encoding='utf-8').read()); print('OK')"
git add src/bolt_analysis_studio/calibration/decomposition.py src/bolt_analysis_studio/calibration/__init__.py tests/test_calibration_decomposition.py
git commit -m "calibration: MechanismDecomposition (shares de dF_0 por estagio)"
```

---

## Task 7: profiles.py — persistência atômica

**Files:**
- Create: `src/bolt_analysis_studio/calibration/profiles.py`
- Modify: `src/bolt_analysis_studio/calibration/__init__.py`
- Test: `tests/test_calibration_profiles.py`

**Interfaces:**
- Produces:
  - `load_profiles(path) -> dict` (retorna `{}` se arquivo não existe).
  - `save_profiles(path, data: dict) -> None` (escrita atômica temp+rename, utf-8, indent=2).
  - `upsert_profile(path, name: str, profile: dict) -> dict` (carrega, insere/atualiza `data["profiles"][name]`, salva, retorna data).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_calibration_profiles.py
import json
import pytest
from bolt_analysis_studio.calibration import profiles as P


def test_load_missing_returns_empty(tmp_path):
    assert P.load_profiles(tmp_path / "nope.json") == {}


def test_save_then_load_roundtrip(tmp_path):
    fp = tmp_path / "j.json"
    data = {"profiles": {"nova": {"tuners": {"k_emb_scale": 1.2}}}}
    P.save_profiles(fp, data)
    assert P.load_profiles(fp) == data
    # arquivo e utf-8 valido e indentado
    raw = fp.read_text(encoding="utf-8")
    assert "k_emb_scale" in raw


def test_upsert_creates_and_updates(tmp_path):
    fp = tmp_path / "j.json"
    P.upsert_profile(fp, "nova", {"tuners": {"k_emb_scale": 1.0}})
    P.upsert_profile(fp, "reaperto", {"tuners": {"k_loose_scale_tr": 2.0}})
    data = P.load_profiles(fp)
    assert set(data["profiles"]) == {"nova", "reaperto"}
    P.upsert_profile(fp, "nova", {"tuners": {"k_emb_scale": 1.5}})
    data = P.load_profiles(fp)
    assert data["profiles"]["nova"]["tuners"]["k_emb_scale"] == 1.5


def test_no_temp_file_left_behind(tmp_path):
    fp = tmp_path / "j.json"
    P.save_profiles(fp, {"profiles": {}})
    leftovers = [p.name for p in tmp_path.iterdir() if p.name != "j.json"]
    assert leftovers == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_calibration_profiles.py -v`
Expected: FAIL com `ImportError`/`ModuleNotFoundError`.

- [ ] **Step 3: Implement profiles**

```python
# src/bolt_analysis_studio/calibration/profiles.py
"""Load/save do joint_calibrations.json com escrita atômica (temp+rename)."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


def load_profiles(path: PathLike) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_profiles(path: PathLike, data: dict) -> None:
    """Escrita atômica: grava num temp no mesmo diretório e renomeia por cima."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, str(p))   # atômico no mesmo filesystem
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def upsert_profile(path: PathLike, name: str, profile: dict) -> dict:
    data = load_profiles(path)
    if "profiles" not in data:
        data["profiles"] = {}
    data["profiles"][name] = profile
    save_profiles(path, data)
    return data
```

- [ ] **Step 4: Export from package init**

Adicione ao `__init__.py`:

```python
from . import profiles
```

E inclua `"profiles"` no `__all__`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_calibration_profiles.py -v`
Expected: PASS (4 testes).

- [ ] **Step 6: Syntax-check and commit**

```bash
python3 -c "import ast; ast.parse(open('src/bolt_analysis_studio/calibration/profiles.py', encoding='utf-8').read()); print('OK')"
git add src/bolt_analysis_studio/calibration/profiles.py src/bolt_analysis_studio/calibration/__init__.py tests/test_calibration_profiles.py
git commit -m "calibration: profiles.py (load/save atomico do joint_calibrations.json)"
```

---

## Task 8: StagedCalibrator — fit sequencial com travas + regularização física

**Files:**
- Create: `src/bolt_analysis_studio/calibration/staged_calibrator.py`
- Modify: `src/bolt_analysis_studio/calibration/__init__.py`
- Test: `tests/test_staged_calibrator.py`

**Interfaces:**
- Consumes: `DynamicStiffnessAnalyzer`, `JointGeometry`, `JointMaterial`, `StageSegmentation`, `MechanismDecomposition`.
- Produces:
  - `CalibrationConfig` (dataclass) com: `geom, F0_init, F_amp, theta, freq, n_cycles, delta_amp, segmentation, lambda_reg=0.1, bounds: dict, fit_damage=False, c_D=1.0, W_ref=1.0e4, k_dmg_mu=1.0`.
  - `StagedCalibrator(config, curves)` onde `curves = [{"name","cycles","ratio"}]`.
  - `.fit(n_passes=2) -> dict` com chaves: `tuners` (dict), `D_init` (float), `mae_per_segment` (dict), `mae_global` (float), `shares` (dict), `bounds_saturated` (list[str]).
  - Tuners calibrados: `k_emb_scale, k_creep_scale, k_wear_scale_tr, k_loose_scale_tr, Phi_tr_correction` (+ `k_damage_scale` e `D_init` quando `fit_damage=True`).

**Implementação chave:** coordenada-descida por estágio. Cada estágio resolve `least_squares` (bounded, trf) sobre seus tuners livres, com os demais travados nos valores correntes. Resíduo = [erros por ponto de referência **dentro da janela do estágio**] ⊕ [termo de regularização `sqrt(lambda_reg)·(p−1)` por tuner livre]. Bounds no `least_squares` evitam saturação dura; o pull-pra-1 implementa a prioridade física (barreira log fragil foi substituída por bounds + regularização quadrática, decisão de implementação). `D_init` (quando `fit_damage`) entra como variável livre do Estágio II em [0, 0.9].

- [ ] **Step 1: Write the failing test**

```python
# tests/test_staged_calibrator.py
from pathlib import Path
import numpy as np
import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointGeometry
from bolt_analysis_studio.calibration.segmentation import StageSegmentation
from bolt_analysis_studio.calibration.staged_calibrator import (
    CalibrationConfig, StagedCalibrator,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "New_Theory"
M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)
BOUNDS = {
    "k_emb_scale": (1e-3, 5.0), "k_creep_scale": (1e-3, 5.0),
    "k_wear_scale_tr": (1e-3, 5.0), "k_loose_scale_tr": (1e-3, 5.0),
    "Phi_tr_correction": (0.05, 5.0), "k_damage_scale": (1e-3, 5.0),
}


def _load(name):
    d = np.genfromtxt(DATA / f"M16_shear_{name}.csv", delimiter=",", skip_header=1)
    return {"name": name, "cycles": d[:, 0], "ratio": d[:, 1]}


def _config(fit_damage=False):
    return CalibrationConfig(
        geom=M16, F0_init=50_000.0, F_amp=20_000.0, theta=np.pi / 2,
        freq=0.5, n_cycles=2500, delta_amp=0.5e-3,
        segmentation=StageSegmentation(100, 1000, 2500),
        lambda_reg=0.05, bounds=BOUNDS, fit_damage=fit_damage,
    )


def test_nova_fit_quality_and_no_saturation():
    curves = [_load(n) for n in ("TP3_nova", "TP8_nova", "TP11_nova", "MEAN_nova")]
    res = StagedCalibrator(_config(), curves).fit(n_passes=2)
    # cada segmento <= MAE global atual do perfil nova (0.022), com folga
    for name, mae in res["mae_per_segment"].items():
        if mae is not None:
            assert mae <= 0.05, f"segmento {name} MAE={mae}"
    assert res["bounds_saturated"] == []   # nenhum tuner colado no bound


def test_reaperto_fits_via_damage_without_saturation():
    curves = [_load("TP7_reaperto")]
    res = StagedCalibrator(_config(fit_damage=True), curves).fit(n_passes=3)
    assert res["mae_global"] <= 0.03
    # k_loose NAO saturado (era 10.0 no modelo antigo); dano carrega o colapso
    assert res["tuners"]["k_loose_scale_tr"] < 4.5
    assert res["D_init"] > 0.0


def test_deterministic():
    curves = [_load("MEAN_nova")]
    a = StagedCalibrator(_config(), curves).fit(n_passes=1)
    b = StagedCalibrator(_config(), curves).fit(n_passes=1)
    assert a["tuners"] == b["tuners"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_staged_calibrator.py -v`
Expected: FAIL com `ModuleNotFoundError: ... 'staged_calibrator'`.

- [ ] **Step 3: Implement the staged calibrator**

```python
# src/bolt_analysis_studio/calibration/staged_calibrator.py
"""Calibrador em estágios: coordenada-descida por janela de ciclos, com
travas entre estágios e regularização física (pull dos tuners pra 1.0)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
from scipy.optimize import least_squares

from ..numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)
from .segmentation import StageSegmentation
from .decomposition import MechanismDecomposition

# Todos os tuners que o calibrador conhece, com valor neutro (default fisico).
_ALL_TUNERS = ["k_emb_scale", "k_creep_scale", "k_wear_scale_tr",
               "k_loose_scale_tr", "Phi_tr_correction", "k_damage_scale"]


@dataclass
class CalibrationConfig:
    geom: JointGeometry
    F0_init: float
    F_amp: float
    theta: float
    freq: float
    n_cycles: int
    delta_amp: float
    segmentation: StageSegmentation
    bounds: Dict[str, tuple]
    lambda_reg: float = 0.1
    fit_damage: bool = False
    c_D: float = 1.0
    W_ref: float = 1.0e4
    k_dmg_mu: float = 1.0


class StagedCalibrator:
    def __init__(self, config: CalibrationConfig, curves: List[dict]):
        self.cfg = config
        self.curves = curves
        # estado corrente dos tuners (parte do default fisico = 1.0)
        self.tuners: Dict[str, float] = {t: 1.0 for t in _ALL_TUNERS}
        self.D_init: float = 0.3 if config.fit_damage else 0.0

    # ---- simulação ----
    def _material(self) -> JointMaterial:
        kw = dict(self.tuners)
        if self.cfg.fit_damage:
            kw.update(c_D=self.cfg.c_D, W_ref=self.cfg.W_ref,
                      k_dmg_mu=self.cfg.k_dmg_mu)
        return JointMaterial(**kw)

    def _run_sim(self) -> tuple:
        ana = DynamicStiffnessAnalyzer(self.cfg.geom, self._material(),
                                       self.cfg.F0_init,
                                       initial_damage=self.D_init)
        ratio = [1.0]
        for _ in range(self.cfg.n_cycles):
            ana.step_cycle(self.cfg.F_amp, self.cfg.theta, self.cfg.freq,
                           delta_amp=self.cfg.delta_amp)
            ratio.append(max(ana.state.F_0, 0.0) / self.cfg.F0_init)
        return np.arange(self.cfg.n_cycles + 1), np.array(ratio), ana.history

    # ---- custo de um estágio ----
    def _stage_residuals(self, x, free_names, stage, fit_D):
        # aplica os valores livres
        for name, val in zip(free_names, x[:len(free_names)]):
            self.tuners[name] = float(val)
        if fit_D:
            self.D_init = float(x[-1])
        sim_N, sim_ratio, _ = self._run_sim()
        res = []
        for c in self.curves:
            in_win = np.array([stage.n_start <= n < stage.n_end
                               or (stage.name == "III" and n == stage.n_end)
                               for n in c["cycles"]])
            if not in_win.any():
                continue
            sim_at = np.interp(c["cycles"][in_win], sim_N, sim_ratio)
            err = sim_at - c["ratio"][in_win]
            res.extend(err / np.sqrt(max(in_win.sum(), 1)))
        # regularizacao fisica: puxa cada tuner livre pra 1.0
        lam = np.sqrt(self.cfg.lambda_reg)
        for name in free_names:
            res.append(lam * (self.tuners[name] - 1.0))
        return np.array(res) if res else np.array([0.0])

    def _fit_stage(self, stage):
        free = [t for t in stage.owned_tuners if t in self.cfg.bounds]
        if self.cfg.fit_damage and stage.name == "II":
            fit_D = True
        else:
            free = [t for t in free if t != "k_damage_scale"] \
                if not self.cfg.fit_damage else free
            fit_D = False
        if not free and not fit_D:
            return
        x0 = [self.tuners[t] for t in free]
        lo = [self.cfg.bounds[t][0] for t in free]
        hi = [self.cfg.bounds[t][1] for t in free]
        if fit_D:
            x0.append(self.D_init)
            lo.append(0.0)
            hi.append(0.9)
        least_squares(self._stage_residuals, x0, bounds=(lo, hi),
                      args=(free, stage, fit_D),
                      method="trf", xtol=1e-8, ftol=1e-8, max_nfev=200)

    # ---- driver ----
    def fit(self, n_passes: int = 2) -> dict:
        for _ in range(n_passes):
            for stage in self.cfg.segmentation.stages:
                self._fit_stage(stage)
        sim_N, sim_ratio, hist = self._run_sim()
        seg = self.cfg.segmentation
        # MAE por segmento agregado sobre todas as curvas
        per_seg = {s.name: [] for s in seg.stages}
        glob = []
        for c in self.curves:
            m = seg.mae_per_segment(sim_N, sim_ratio, c["cycles"], c["ratio"])
            for k, v in m.items():
                if v is not None:
                    per_seg[k].append(v)
            sim_at = np.interp(c["cycles"], sim_N, sim_ratio)
            glob.append(float(np.mean(np.abs(sim_at - c["ratio"]))))
        mae_per_segment = {k: (float(np.mean(v)) if v else None)
                           for k, v in per_seg.items()}
        # checa saturacao nos bounds (1% da largura)
        saturated = []
        for t, val in self.tuners.items():
            if t in self.cfg.bounds:
                lo, hi = self.cfg.bounds[t]
                span = hi - lo
                if val <= lo + 0.01 * span or val >= hi - 0.01 * span:
                    saturated.append(t)
        return {
            "tuners": {t: float(v) for t, v in self.tuners.items()},
            "D_init": float(self.D_init),
            "mae_per_segment": mae_per_segment,
            "mae_global": float(np.mean(glob)) if glob else None,
            "shares": MechanismDecomposition.shares_per_segment(hist, seg),
            "bounds_saturated": saturated,
        }
```

- [ ] **Step 4: Export from package init**

Adicione ao `__init__.py`:

```python
from .staged_calibrator import CalibrationConfig, StagedCalibrator
```

E inclua `"CalibrationConfig"`, `"StagedCalibrator"` no `__all__`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_staged_calibrator.py -v`
Expected: PASS (3 testes). Se `test_reaperto...` falhar no limite, ajuste `c_D`/`W_ref`/`k_dmg_mu` no `_config(fit_damage=True)` (são starters físicos) — o critério é MAE ≤ 0.03 com `k_loose_scale_tr < 4.5`.

- [ ] **Step 6: Syntax-check and commit**

```bash
python3 -c "import ast; ast.parse(open('src/bolt_analysis_studio/calibration/staged_calibrator.py', encoding='utf-8').read()); print('OK')"
git add src/bolt_analysis_studio/calibration/staged_calibrator.py src/bolt_analysis_studio/calibration/__init__.py tests/test_staged_calibrator.py
git commit -m "calibration: StagedCalibrator (coordenada-descida + regularizacao fisica)"
```

---

## Task 9: Refatorar calibrate_4_profiles.py

**Files:**
- Modify: `New_Theory/calibrate_4_profiles.py`
- Test: manual/integração (rodar o script)

**Interfaces:**
- Consumes: `StagedCalibrator`, `CalibrationConfig`, `StageSegmentation`, `profiles.save_profiles`.

- [ ] **Step 1: Replace the optimization core**

Reescreva o corpo de `calibrate_one` e `main` pra usar o `StagedCalibrator`. Mantém o mapeamento de perfis, o PNG 2×2 e o JSON. Substitua os imports e funções `make_material/run_sim/cost/residuals/calibrate_one` por:

```python
import sys
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointGeometry
from bolt_analysis_studio.calibration.segmentation import StageSegmentation
from bolt_analysis_studio.calibration.staged_calibrator import (
    CalibrationConfig, StagedCalibrator,
)
from bolt_analysis_studio.calibration.profiles import save_profiles

DATA_DIR = ROOT / "New_Theory"
OUT_PNG = DATA_DIR / "calibration_4_profiles.png"
OUT_JSON = DATA_DIR / "joint_calibrations.json"

M16_GEOM = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                         pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)
F0_INIT_N, F_AMP_N, DELTA_AMP_M = 50_000.0, 20_000.0, 0.5e-3
THETA, FREQ_HZ, N_CYCLES = np.pi / 2, 0.5, 2500
BOUNDS = {
    "k_emb_scale": (1e-3, 5.0), "k_creep_scale": (1e-3, 5.0),
    "k_wear_scale_tr": (1e-3, 5.0), "k_loose_scale_tr": (1e-3, 5.0),
    "Phi_tr_correction": (0.05, 5.0), "k_damage_scale": (1e-3, 5.0),
}
# reaperto/reusada ligam o dano; nova/sobretorque nao precisam
DAMAGE_PROFILES = {"reaperto", "reusada"}

PROFILES = {
    'nova':        ['TP3_nova', 'TP8_nova', 'TP11_nova', 'MEAN_nova'],
    'reusada':     ['TP4_reusada', 'TP5_reusada', 'TP9_reusada', 'TP10_reusada',
                    'MEAN_reusada'],
    'sobretorque': ['TP6_sobretorque'],
    'reaperto':    ['TP7_reaperto'],
}
COND_COLORS = {'nova': '#4F81BD', 'reusada': '#C00000',
               'sobretorque': '#00B050', 'reaperto': '#92D050'}


def load_curves(names):
    out = []
    for name in names:
        d = np.genfromtxt(DATA_DIR / f"M16_shear_{name}.csv",
                          delimiter=",", skip_header=1)
        out.append({'name': name, 'cycles': d[:, 0], 'ratio': d[:, 1]})
    return out


def calibrate_one(cond_name, curve_names):
    print(f"\n[{cond_name}] curvas: {curve_names}")
    curves = load_curves(curve_names)
    cfg = CalibrationConfig(
        geom=M16_GEOM, F0_init=F0_INIT_N, F_amp=F_AMP_N, theta=THETA,
        freq=FREQ_HZ, n_cycles=N_CYCLES, delta_amp=DELTA_AMP_M,
        segmentation=StageSegmentation(100, 1000, N_CYCLES),
        lambda_reg=0.05, bounds=BOUNDS,
        fit_damage=(cond_name in DAMAGE_PROFILES),
    )
    cal = StagedCalibrator(cfg, curves)
    res = cal.fit(n_passes=3)
    sim_N, sim_ratio, _ = cal._run_sim()
    print(f"  MAE global={res['mae_global']:.4f}  "
          f"saturados={res['bounds_saturated']}")
    profile = {
        'profile_name': f"M16_shear_{cond_name}",
        'condition': cond_name,
        'calibrated_at': "2026-06-20",
        'loading': {'F0_N': F0_INIT_N, 'F_amp_N': F_AMP_N,
                    'theta_rad': float(THETA), 'freq_Hz': FREQ_HZ,
                    'n_cycles': N_CYCLES, 'D_init': res['D_init']},
        'tuners': res['tuners'],
        'fit_quality': {'mean_MAE_global': res['mae_global'],
                        'mae_per_segment': res['mae_per_segment'],
                        'bounds_saturated': res['bounds_saturated']},
    }
    return profile, curves, (sim_N, sim_ratio)


def main():
    profiles, plot_data = {}, {}
    for cond, names in PROFILES.items():
        prof, curves, sim = calibrate_one(cond, names)
        profiles[cond] = prof
        plot_data[cond] = (curves, sim)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for ax, (cond, prof) in zip(axes.flat, profiles.items()):
        curves, (sim_N, sim_ratio) = plot_data[cond]
        col = COND_COLORS[cond]
        for c in curves:
            ls = '-' if c['name'].startswith('MEAN') else ':'
            ax.plot(c['cycles'], c['ratio'], ls, color=col, alpha=0.8,
                    marker='o', markersize=4, label=c['name'])
        ax.plot(sim_N, sim_ratio, 'k-', linewidth=2.5,
                label=f"sim (MAE={prof['fit_quality']['mean_MAE_global']:.3f})")
        ax.set_xlabel('Ciclos N'); ax.set_ylabel(r'$F_0/F_{0,init}$')
        ax.set_title(f"Perfil: {cond}")
        ax.set_xlim(0, N_CYCLES); ax.set_ylim(0, 1.05); ax.grid(alpha=0.3)
        ax.legend(loc='upper right', fontsize=8)
    plt.tight_layout()
    fig.savefig(OUT_PNG, dpi=120)
    print(f"\nPlot: {OUT_PNG}")

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


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the script and verify outputs**

Run: `python3 New_Theory/calibrate_4_profiles.py`
Expected: imprime MAE por perfil, escreve `joint_calibrations.json` (4 perfis) e `calibration_4_profiles.png`. Verifique:

```bash
python3 -c "import json; d=json.load(open('New_Theory/joint_calibrations.json', encoding='utf-8')); print(list(d['profiles']), [round(d['profiles'][k]['fit_quality']['mean_MAE_global'],3) for k in d['profiles']])"
```
Expected: `['nova', 'reusada', 'sobretorque', 'reaperto']` com MAEs razoáveis (reaperto agora deve ter `D_init>0` e `k_loose_scale_tr` não saturado).

- [ ] **Step 3: Commit**

```bash
git add New_Theory/calibrate_4_profiles.py New_Theory/joint_calibrations.json New_Theory/calibration_4_profiles.png
git commit -m "New_Theory: calibrate_4_profiles via StagedCalibrator + surface_damage"
```

---

## Task 10: server.py — funções puras + HTTP local

**Files:**
- Create: `src/bolt_analysis_studio/calibration/server.py`
- Modify: `src/bolt_analysis_studio/calibration/__init__.py`
- Test: `tests/test_calibration_server.py`

**Interfaces:**
- Produces:
  - `handle_simulate(payload: dict) -> dict` — roda o engine real, devolve `{curve, decomposition, damage_trace, segments, energy, separated_at}`. `ValueError` em payload inválido.
  - `handle_calibrate(payload: dict) -> dict` — roda `StagedCalibrator` só com tuners destravados.
  - `handle_profiles() -> dict` — lê `joint_calibrations.json`.
  - `serve(port=8765)` — sobe o `http.server` servindo o tuner + API.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_calibration_server.py
import numpy as np
import pytest
from bolt_analysis_studio.calibration import server as S


def _payload(N=300, N_I=50, N_II=200, reference=None):
    # mantem N_I < N_II <= N pra StageSegmentation ser valida
    return {
        "geom": {"A_s": 157e-6, "L_eff": 0.050, "d_2": 14.701e-3,
                 "pitch": 2.0e-3, "r_bearing": 12e-3, "A_contact": 1e-4},
        "mat": {"k_emb_scale": 1.0, "k_creep_scale": 1.0,
                "k_wear_scale_tr": 1.0, "k_loose_scale_tr": 1.0,
                "Phi_tr_correction": 1.0, "k_damage_scale": 1.0,
                "c_D": 0.0, "W_ref": 1.0e4, "k_dmg_mu": 0.0},
        "loading": {"F0_init": 50_000.0, "F_amp": 20_000.0,
                    "theta": np.pi / 2, "freq": 0.5, "N": N,
                    "delta_amp": 0.5e-3, "D_init": 0.0},
        "segments": {"N_I": N_I, "N_II": N_II},
        "reference": reference if reference is not None
        else [[0, 1.0], [50, 0.78], [200, 0.57]],
    }


def test_simulate_shape_and_fidelity():
    out = S.handle_simulate(_payload(N=300))
    assert len(out["curve"]["N"]) == 301
    assert "embedding" in out["decomposition"]
    assert set(out["segments"]) == {"I", "II", "III"}
    assert "conservation_residual" in out["energy"]
    # fidelidade: bate com chamada in-process direta do engine
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)
    geom = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                         pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)
    ana = DynamicStiffnessAnalyzer(geom, JointMaterial(), 50_000.0)
    for _ in range(300):
        ana.step_cycle(20_000.0, np.pi / 2, 0.5, delta_amp=0.5e-3)
    assert abs(out["curve"]["ratio"][-1] - ana.state.F_0 / 50_000.0) < 1e-9


def test_simulate_bad_payload_raises():
    with pytest.raises(ValueError):
        S.handle_simulate({"geom": {}})       # faltando campos


def test_calibrate_respects_locks():
    p = _payload(N=2500, N_I=100, N_II=1000,
                 reference=[[0, 1.0], [100, 0.64], [500, 0.43], [2500, 0.26]])
    p["locked"] = ["k_creep_scale"]           # travado
    p["mat"]["k_creep_scale"] = 1.23
    out = S.handle_calibrate(p)
    assert out["tuners"]["k_creep_scale"] == 1.23   # nao foi mexido
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_calibration_server.py -v`
Expected: FAIL com `ModuleNotFoundError: ... 'server'`.

- [ ] **Step 3: Implement the server**

```python
# src/bolt_analysis_studio/calibration/server.py
"""Servidor HTTP local que expõe o DynamicStiffnessAnalyzer real ao tuner.
Lógica em funções puras (testáveis sem socket); o handler só roteia."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List

import numpy as np

from ..numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)
from .segmentation import StageSegmentation
from .decomposition import MechanismDecomposition
from .staged_calibrator import CalibrationConfig, StagedCalibrator
from . import profiles as P

ROOT = Path(__file__).resolve().parents[3]
TUNER_HTML = ROOT / "New_Theory" / "calibration_tuner.html"
PROFILES_JSON = ROOT / "New_Theory" / "joint_calibrations.json"

_GEOM_KEYS = ["A_s", "L_eff", "d_2", "pitch", "r_bearing", "A_contact"]
_MAT_KEYS = ["k_emb_scale", "k_creep_scale", "k_wear_scale_tr",
             "k_loose_scale_tr", "Phi_tr_correction", "k_damage_scale",
             "c_D", "W_ref", "k_dmg_mu"]
_LOAD_KEYS = ["F0_init", "F_amp", "theta", "freq", "N", "delta_amp", "D_init"]
_BOUNDS = {"k_emb_scale": (1e-3, 5.0), "k_creep_scale": (1e-3, 5.0),
           "k_wear_scale_tr": (1e-3, 5.0), "k_loose_scale_tr": (1e-3, 5.0),
           "Phi_tr_correction": (0.05, 5.0), "k_damage_scale": (1e-3, 5.0)}


def _require(d: dict, keys: List[str], where: str):
    missing = [k for k in keys if k not in d]
    if missing:
        raise ValueError(f"payload['{where}'] faltando: {missing}")


def _geom(p) -> JointGeometry:
    _require(p.get("geom", {}), _GEOM_KEYS, "geom")
    return JointGeometry(**{k: float(p["geom"][k]) for k in _GEOM_KEYS})


def _material(p) -> JointMaterial:
    _require(p.get("mat", {}), _MAT_KEYS, "mat")
    return JointMaterial(**{k: float(p["mat"][k]) for k in _MAT_KEYS})


def handle_simulate(p: dict) -> dict:
    geom = _geom(p)
    mat = _material(p)
    _require(p.get("loading", {}), _LOAD_KEYS, "loading")
    L = p["loading"]
    N = int(L["N"])
    ana = DynamicStiffnessAnalyzer(geom, mat, float(L["F0_init"]),
                                   initial_damage=float(L["D_init"]))
    Ns, ratio, Dtr = [0], [1.0], [float(L["D_init"])]
    separated_at = None
    for _ in range(N):
        snap = ana.step_cycle(float(L["F_amp"]), float(L["theta"]),
                              float(L["freq"]), delta_amp=float(L["delta_amp"]))
        Ns.append(snap.cycle)
        ratio.append(max(ana.state.F_0, 0.0) / float(L["F0_init"]))
        Dtr.append(snap.D)
        if separated_at is None and ana.state.F_0 <= 0.0:
            separated_at = snap.cycle
    seg = StageSegmentation(float(p["segments"]["N_I"]),
                            float(p["segments"]["N_II"]), N)
    # decomposicao acumulada por mecanismo (serie por ciclo, |dF_0|)
    mechs = ["embedding", "creep", "wear", "rotational_loosening"]
    decomp = {m: [abs(s.dF_0_by_mech.get(m, 0.0)) for s in ana.history]
              for m in mechs}
    ref = p.get("reference") or []
    if ref:
        ref = np.asarray(ref, dtype=float)
        mae = seg.mae_per_segment(Ns, ratio, ref[:, 0], ref[:, 1])
    else:
        mae = {s.name: None for s in seg.stages}
    shares = MechanismDecomposition.shares_per_segment(ana.history, seg)
    segments = {}
    for s in seg.stages:
        sh = shares.get(s.name)
        segments[s.name] = {
            "window": [s.n_start, s.n_end],
            "mae": mae.get(s.name),
            "dominant": sh["dominant"] if sh else None,
            "shares": sh["shares"] if sh else None,
        }
    return {
        "curve": {"N": Ns, "ratio": ratio},
        "decomposition": decomp,
        "damage_trace": {"N": Ns, "D": Dtr},
        "segments": segments,
        "energy": {"conservation_residual": ana.energy.conservation_residual},
        "separated_at": separated_at,
    }


def handle_calibrate(p: dict) -> dict:
    geom = _geom(p)
    _require(p.get("loading", {}), _LOAD_KEYS, "loading")
    L = p["loading"]
    locked = set(p.get("locked", []))
    curves = [{"name": "ref",
               "cycles": np.asarray([r[0] for r in p["reference"]], float),
               "ratio": np.asarray([r[1] for r in p["reference"]], float)}]
    fit_damage = float(L["D_init"]) > 0.0 or float(p["mat"].get("c_D", 0.0)) > 0.0
    cfg = CalibrationConfig(
        geom=geom, F0_init=float(L["F0_init"]), F_amp=float(L["F_amp"]),
        theta=float(L["theta"]), freq=float(L["freq"]), n_cycles=int(L["N"]),
        delta_amp=float(L["delta_amp"]),
        segmentation=StageSegmentation(float(p["segments"]["N_I"]),
                                       float(p["segments"]["N_II"]), int(L["N"])),
        bounds={k: v for k, v in _BOUNDS.items() if k not in locked},
        lambda_reg=float(p.get("lambda_reg", 0.05)), fit_damage=fit_damage,
    )
    cal = StagedCalibrator(cfg, curves)
    # semeia tuners travados com os valores enviados
    for k in _BOUNDS:
        if k in p["mat"]:
            cal.tuners[k] = float(p["mat"][k])
    if fit_damage:
        cal.D_init = float(L["D_init"]) or 0.3
    return cal.fit(n_passes=int(p.get("n_passes", 2)))


def handle_profiles() -> dict:
    return P.load_profiles(PROFILES_JSON)


# ---- camada HTTP (fina) ----
class _Handler(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read(self) -> dict:
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            html = TUNER_HTML.read_text(encoding="utf-8").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
        elif self.path == "/profiles":
            self._json(200, handle_profiles())
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        routes = {"/simulate": handle_simulate, "/calibrate": handle_calibrate}
        fn = routes.get(self.path)
        if self.path == "/profiles/save":
            try:
                p = self._read()
                P.upsert_profile(PROFILES_JSON, p["name"], p["profile"])
                return self._json(200, {"ok": True})
            except Exception as e:
                return self._json(400, {"error": str(e)})
        if fn is None:
            return self._json(404, {"error": "not found"})
        try:
            return self._json(200, fn(self._read()))
        except ValueError as e:
            return self._json(400, {"error": str(e)})
        except Exception as e:   # pragma: no cover
            return self._json(500, {"error": repr(e)})

    def log_message(self, *a):   # silencia o log padrao
        pass


def serve(port: int = 8765):
    srv = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    print(f"Calibration tuner em http://localhost:{port}/  (Ctrl+C pra sair)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    serve()
```

- [ ] **Step 4: Export and add __main__ convenience**

Adicione ao `__init__.py`:

```python
from .server import serve, handle_simulate, handle_calibrate, handle_profiles
```

E inclua esses nomes no `__all__`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_calibration_server.py -v`
Expected: PASS (3 testes).

- [ ] **Step 6: Syntax-check and commit**

```bash
python3 -c "import ast; ast.parse(open('src/bolt_analysis_studio/calibration/server.py', encoding='utf-8').read()); print('OK')"
git add src/bolt_analysis_studio/calibration/server.py src/bolt_analysis_studio/calibration/__init__.py tests/test_calibration_server.py
git commit -m "calibration: server.py (engine real via HTTP local, funcoes puras testaveis)"
```

---

## Task 11: Refatorar calibration_tuner.html — cliente fino

**Files:**
- Modify: `New_Theory/calibration_tuner.html`
- Test: verificação manual (sem JS test harness no repo) + smoke via servidor

**Interfaces:**
- Consumes: endpoints `POST /simulate`, `POST /calibrate`, `GET /profiles`, `POST /profiles/save` (Task 10).

**Nota:** o tuner roda servido pelo backend (`python3 -m bolt_analysis_studio.calibration.server`), então `fetch` é same-origin. As mudanças removem o modelo JS e ligam a UI ao servidor.

- [ ] **Step 1: Remove the JS model block**

Apague o bloco JS que reimplementa o modelo: as funções `k_j_ax`, `Phi_eff`, `F_sep`, `F_slip_tr`, `T_resist`, `U_internal`, `direction_blend`, `resolveSlip`, `simulate` (aprox. linhas 476–627). Mantenha `getState`, `computeMetrics`, os `plot*` e a UI. A fonte única do modelo passa a ser o servidor.

- [ ] **Step 2: Add a debounced server-backed render**

Substitua a função `render()` (chamava `simulate(...)` local) por uma versão que monta o payload de `getState()` + janelas + referência e chama `/simulate` com debounce:

```javascript
let _renderTimer = null;
let _firstPlot = true;

function buildPayload() {
  const st = getState();   // {geom, mat, F0_init, F_amp, theta, freq, N, delta_amp}
  return {
    geom: st.geom,
    mat: {
      k_emb_scale: st.mat.k_emb_scale, k_creep_scale: st.mat.k_creep_scale,
      k_wear_scale_tr: st.mat.k_wear_scale_tr,
      k_loose_scale_tr: st.mat.k_loose_scale_tr,
      Phi_tr_correction: st.mat.Phi_tr_correction,
      k_damage_scale: st.mat.k_damage_scale ?? 1.0,
      c_D: st.mat.c_D ?? 0.0, W_ref: st.mat.W_ref ?? 1e4,
      k_dmg_mu: st.mat.k_dmg_mu ?? 0.0,
    },
    loading: {
      F0_init: st.F0_init, F_amp: st.F_amp, theta: st.theta,
      freq: st.freq, N: st.N, delta_amp: st.delta_amp,
      D_init: +(document.getElementById('D_init')?.value ?? 0),
    },
    segments: {
      N_I: +document.getElementById('N_I').value,
      N_II: +document.getElementById('N_II').value,
    },
    reference: referenceCurve
      ? referenceCurve.N.map((n, i) => [n, referenceCurve.ratio[i]]) : [],
  };
}

async function render() {
  let resp;
  try {
    resp = await fetch('/simulate', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(buildPayload()),
    });
  } catch (e) { return showOffline(true); }
  if (!resp.ok) { const j = await resp.json().catch(() => ({}));
                  return showError(j.error || resp.statusText); }
  showOffline(false);
  const out = await resp.json();
  const hist = {N: out.curve.N, ratio: out.curve.ratio};
  plotF0(hist, referenceCurve, _firstPlot);
  plotDecomposition(out.decomposition, out.curve.N, _firstPlot);
  plotDamage(out.damage_trace, _firstPlot);
  renderSegmentBadges(out.segments);
  _firstPlot = false;
}

function scheduleRender() {
  clearTimeout(_renderTimer);
  _renderTimer = setTimeout(render, 60);   // debounce 60ms
}
```

Troque as chamadas que faziam `render()` direto nos listeners de slider por `scheduleRender()`.

- [ ] **Step 3: Add the offline/error banner**

Adicione no HTML (topo do `<body>`) e as funções:

```html
<div id="offline-banner" style="display:none;background:#7a1e1e;color:#fff;
  padding:8px 12px;font-size:13px;">
  Servidor de calibração offline. Rode:
  <code>python3 -m bolt_analysis_studio.calibration.server</code> e recarregue.
</div>
<div id="error-banner" style="display:none;background:#7a5a1e;color:#fff;
  padding:8px 12px;font-size:13px;"></div>
```

```javascript
function showOffline(on) {
  document.getElementById('offline-banner').style.display = on ? 'block' : 'none';
}
function showError(msg) {
  const el = document.getElementById('error-banner');
  el.textContent = 'Erro: ' + msg;
  el.style.display = 'block';
  setTimeout(() => { el.style.display = 'none'; }, 4000);
}
```

- [ ] **Step 4: Replace hardcoded PROFILES with a fetch**

Substitua o objeto `const PROFILES = {...}` e o listener de `profile-select` por um carregamento do servidor:

```javascript
let PROFILES = {};
async function loadProfiles() {
  try {
    const r = await fetch('/profiles');
    const data = await r.json();
    PROFILES = data.profiles || {};
    const sel = document.getElementById('profile-select');
    sel.innerHTML = '<option value="">— perfil —</option>' +
      Object.keys(PROFILES).map(k => `<option value="${k}">${k}</option>`).join('');
  } catch (e) { showOffline(true); }
}

document.getElementById('profile-select').addEventListener('change', (e) => {
  const p = PROFILES[e.target.value];
  if (!p) return;
  const t = p.tuners || {};
  for (const [k, v] of Object.entries(t)) {
    const el = document.getElementById(k);
    if (el) { el.value = v; document.getElementById(k + '-v').textContent = (+v).toFixed(3); }
  }
  if (p.loading && p.loading.D_init != null) {
    const d = document.getElementById('D_init');
    if (d) d.value = p.loading.D_init;
  }
  scheduleRender();
});
```

Chame `loadProfiles()` no init.

- [ ] **Step 5: Add lock checkboxes, draggable boundaries, segment badges, decomposition+damage plots, auto-fit buttons**

Adicione os controles e helpers (HTML + JS). Os elementos `N_I`/`N_II` (inputs number) e os checkboxes de trava (classe `tuner-lock` com `data-tuner`):

```html
<!-- janelas ajustaveis -->
<label>N_I <input type="number" id="N_I" value="100" min="1" step="10"></label>
<label>N_II <input type="number" id="N_II" value="1000" min="2" step="50"></label>
<label>D_init <input type="number" id="D_init" value="0" min="0" max="0.9" step="0.05"></label>
<!-- badges -->
<div id="seg-badges"></div>
<!-- plots novos -->
<div id="plot-decomp" style="height:180px"></div>
<div id="plot-damage" style="height:140px"></div>
<!-- auto-fit -->
<button id="autofit-I">Auto-fit I</button>
<button id="autofit-II">Auto-fit II</button>
<button id="autofit-III">Auto-fit III</button>
```

```javascript
// badges de MAE por segmento
function renderSegmentBadges(segments) {
  const order = ['I', 'II', 'III'];
  document.getElementById('seg-badges').innerHTML = order.map(k => {
    const s = segments[k]; if (!s) return '';
    const mae = s.mae == null ? '—' : s.mae.toFixed(3);
    const col = s.mae == null ? '#888' : (s.mae <= 0.022 ? '#2e7d32' : '#c62828');
    const dom = s.dominant || '—';
    return `<span style="background:${col};color:#fff;padding:3px 8px;
      margin:2px;border-radius:3px;font-size:11px;">
      Estágio ${k}: MAE ${mae} · ${dom}</span>`;
  }).join('');
}

// overlay de decomposicao (share por ciclo, area empilhada)
function plotDecomposition(decomp, N, isInit) {
  const colors = {embedding:'#d4b14a', creep:'#d4944a',
                  wear:'#7aa8d4', rotational_loosening:'#d44a4a'};
  const data = Object.keys(decomp).map(m => ({
    x: N, y: decomp[m], name: m, stackgroup: 'one',
    line: {width: 1, color: colors[m] || '#999'},
  }));
  const layout = plotLayout('N ciclos', '|dF₀| por mec.',
    {showlegend: true, legend: {orientation:'h', y:1.2, font:{size:9}}});
  isInit ? Plotly.newPlot('plot-decomp', data, layout, {displayModeBar:false})
         : Plotly.react('plot-decomp', data, layout, {displayModeBar:false});
}

// mini-plot do dano D(N)
function plotDamage(tr, isInit) {
  const data = [{x: tr.N, y: tr.D, mode:'lines', name:'D',
                 line:{color:'#e05a8c', width:2}, fill:'tozeroy',
                 fillcolor:'rgba(224,90,140,0.15)'}];
  const layout = plotLayout('N ciclos', 'surface_damage D');
  layout.yaxis.range = [0, 1.0];
  isInit ? Plotly.newPlot('plot-damage', data, layout, {displayModeBar:false})
         : Plotly.react('plot-damage', data, layout, {displayModeBar:false});
}

// janelas ajustaveis -> re-render
['N_I', 'N_II', 'D_init'].forEach(id =>
  document.getElementById(id).addEventListener('input', scheduleRender));

// auto-fit por estagio: trava tudo menos os tuners do estagio, chama /calibrate
async function autoFit(stage) {
  const owners = {
    I: ['k_emb_scale'],
    II: ['k_wear_scale_tr','k_loose_scale_tr','Phi_tr_correction','k_damage_scale'],
    III: ['k_creep_scale'],
  }[stage];
  const allT = ['k_emb_scale','k_creep_scale','k_wear_scale_tr',
                'k_loose_scale_tr','Phi_tr_correction','k_damage_scale'];
  const locked = allT.filter(t => !owners.includes(t));
  const payload = buildPayload();
  payload.locked = locked;
  let r;
  try { r = await fetch('/calibrate', {method:'POST',
        headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
  } catch (e) { return showOffline(true); }
  if (!r.ok) { const j = await r.json().catch(()=>({})); return showError(j.error); }
  const res = await r.json();
  for (const [k, v] of Object.entries(res.tuners)) {
    const el = document.getElementById(k);
    if (el) { el.value = v; document.getElementById(k+'-v').textContent = (+v).toFixed(3); }
  }
  if (res.D_init != null) {
    const d = document.getElementById('D_init'); if (d) d.value = res.D_init.toFixed(3);
  }
  scheduleRender();
}
['I','II','III'].forEach(s =>
  document.getElementById('autofit-'+s).addEventListener('click', () => autoFit(s)));
```

- [ ] **Step 6: Initialize on load**

No final do script, garanta a sequência de init:

```javascript
loadProfiles().then(() => render());
```

- [ ] **Step 7: Smoke-test via server**

Inicie o servidor e verifique o fluxo manualmente:

```bash
python3 -m bolt_analysis_studio.calibration.server
```
Verificação manual (checklist):
1. Abrir `http://localhost:8765/` — a página carrega sem erro no console.
2. O seletor de perfil lista nova/reusada/sobretorque/reaperto (veio do servidor).
3. Arrastar um slider → curva F₀ atualiza (veio do `/simulate`, não de JS local).
4. Badges de MAE I/II/III aparecem quando há CSV de referência carregado.
5. Mudar `N_I`/`N_II` → badges e segmentos recalculam.
6. Selecionar perfil `reaperto`, setar `D_init`=0.3 → mini-plot D(N) sobe; curva colapsa.
7. Clicar "Auto-fit II" → tuners do estágio II mudam, curva melhora.
8. Parar o servidor → recarregar mostra o banner offline.

- [ ] **Step 8: Commit**

```bash
git add New_Theory/calibration_tuner.html
git commit -m "New_Theory: tuner como cliente fino do servidor (fonte unica, instrumentado)"
```

---

## Task 12: Verificação final (suite completa)

**Files:** nenhum (só execução)

- [ ] **Step 1: Run the whole new suite + the V1 regression**

```bash
python3 -m pytest tests/test_surface_damage.py tests/test_calibration_segmentation.py tests/test_calibration_decomposition.py tests/test_calibration_profiles.py tests/test_staged_calibrator.py tests/test_calibration_server.py -v
python3 -m pytest tests/test_coupled_loosening.py tests/test_independent_joints.py -q
```
Expected: todos PASS (novos + V1 não regrediram).

- [ ] **Step 2: Confirm acceptance criteria from the spec**

```bash
python3 New_Theory/calibrate_4_profiles.py
python3 -c "import json; d=json.load(open('New_Theory/joint_calibrations.json', encoding='utf-8'))['profiles']; \
print('reaperto k_loose=', round(d['reaperto']['tuners']['k_loose_scale_tr'],2), \
'D_init=', round(d['reaperto']['loading']['D_init'],3), \
'MAE=', round(d['reaperto']['fit_quality']['mean_MAE_global'],3))"
```
Expected: reaperto com `D_init>0`, `k_loose` não saturado (< ~4.5), MAE razoável (≤ 0.03). Confirma critérios de aceite #2, #3.

- [ ] **Step 3: Commit any final artifacts**

```bash
git add -A
git commit -m "calibration: verificacao final da suite + perfis recalibrados" || echo "nada a commitar"
```

---

## Notas de execução

- A ordem das tasks respeita dependências: 1→4 (engine) antes de 5→8 (pacote), 8 antes de 9/10, 10 antes de 11.
- Tasks 1–10 são TDD puro (teste falha → implementa → passa). Task 11 (HTML) não tem harness JS no repo, então usa checklist manual + smoke via servidor — honesto sobre o limite.
- Se `test_reaperto...` (Task 8) não bater o alvo na primeira, os starters físicos de dano (`c_D`, `W_ref`, `k_dmg_mu` em `CalibrationConfig`) são o ponto de ajuste — não os tuners (guideline #10).
