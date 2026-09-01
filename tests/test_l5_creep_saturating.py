"""L5 (plano L1-L7, Task 7): CreepLoss docstring log-t corrigido + forma
saturante opt-in (Alamos 2021/2022).

`CreepLoss.rate()` e' log-t / linear em F_0 / ILIMITADA no tempo -- NAO
Norton-Bailey (o docstring antigo mentia; a forma log-t coincide, por
coincidencia feliz, com a regressao de faiamento do Nah 2014, KB
`creep_class`). Este modulo testa a forma SATURANTE opt-in
(`mat.creep_mode == "saturating"` E `mat.creep_t_c > 0`):

    delta_creep(t) = delta_max * (1 - exp(-(t/creep_t_c)**creep_alpha_sat))

com `delta_max = C_creep * F_clamp` (MESMO produto que multiplica o
crescimento log-t -- "continuidade dimensional"; ver docstring de
`CreepLoss` p/ a derivacao completa e o porque de NAO escalar por
`creep_t_c/t_0`). Default `creep_mode=""` e' bit-identico ao
comportamento anterior (Estagio B / shim nao entram aqui -- nenhum tuner
legado toca em creep).

Harness estatico (F_amp=0, freq=1/60 Hz -- 1 pseudo-ciclo = 1 minuto,
"li2022marstruc-style hold", mesmo padrao de `tests/test_anchor_creep.py`):
isola o mecanismo de creep. `emb_depth` vem ZERADO nos materiais deste
modulo -- o default de `JointMaterial` (30 um) sozinho colapsa F_0=10kN a
zero em poucos minutos (N_emb=50 ciclos = 50 min), o que mascararia
completamente o efeito de creep que este modulo compara.
"""
import numpy as np
import pytest

from bolt_analysis_studio.calibration.parameter_registry import (
    PARAMETER_REGISTRY, active_candidates,
)
from bolt_analysis_studio.calibration.shared_calibrator import ConditionSpec
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)

FREQ_STATIC = 1.0 / 60.0   # 1 pseudo-ciclo = 1 minuto (li2022marstruc-style hold)


def _geom():
    return JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                         pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)


def _run_hold(mat, t, F0=10e3):
    """Creep ESTATICO: F_amp=0 (sem slip transversal => wear/loosening
    inertes), freq fixa `FREQ_STATIC` => n ciclos tal que n/FREQ_STATIC = t
    (segundos, arredondado ao pseudo-ciclo/minuto mais proximo). Retorna
    F_0 final [N]. `mat.emb_depth` deve vir zerado p/ isolar o creep (ver
    docstring do modulo)."""
    ana = DynamicStiffnessAnalyzer(_geom(), mat, F0)
    n = max(int(round(t * FREQ_STATIC)), 1)
    for _ in range(n):
        ana.step_cycle(0.0, 0.0, FREQ_STATIC)
    return ana.state.F_0


# --------------------------------------------------------- forma saturante ---
def test_saturating_bounded_log_unbounded():
    # brief L1-L7 task-7, Step 1: a saturante perde MENOS na cauda
    # (1e4 -> 1e6 s) do que o log-t (ilimitado), e nao colapsa a 0.
    m_sat = JointMaterial(creep_mode="saturating", creep_t_c=1e4, emb_depth=0.0)
    m_log = JointMaterial(emb_depth=0.0)
    f_sat_10k = _run_hold(m_sat, t=1e4)
    f_sat_1M = _run_hold(m_sat, t=1e6)
    f_log_10k = _run_hold(m_log, t=1e4)
    f_log_1M = _run_hold(m_log, t=1e6)
    assert (f_sat_10k - f_sat_1M) < (f_log_10k - f_log_1M)   # saturante perde menos na cauda
    assert f_sat_1M > 0


def test_saturating_trajectory_is_monotonic_non_increasing():
    mat = JointMaterial(creep_mode="saturating", creep_t_c=1e3, emb_depth=0.0)
    ana = DynamicStiffnessAnalyzer(_geom(), mat, 10e3)
    hist = [ana.state.F_0]
    for _ in range(200):
        ana.step_cycle(0.0, 0.0, FREQ_STATIC)
        hist.append(ana.state.F_0)
    assert np.all(np.diff(np.array(hist)) <= 1e-9)


# ------------------------------------------------------------- bit-identity ---
def test_bit_identity_default_creep_mode_vs_explicit_inert_fields():
    # campos novos default-inertes nao mudam a trajetoria (bit-identidade,
    # mesmo padrao de tests/test_l3_famp_coupling.py).
    baseline = _run_hold(JointMaterial(emb_depth=0.0), t=1e4)
    explicit = _run_hold(JointMaterial(emb_depth=0.0, creep_mode="",
                                       creep_t_c=0.0, creep_alpha_sat=1.0),
                         t=1e4)
    assert explicit == baseline


def test_registry_truth_creep_t_c_inert_when_mode_is_default():
    # creep_mode="" (default): creep_t_c/creep_alpha_sat NUNCA sao lidos --
    # mudar os proprios campos nao pode mudar a trajetoria (mais forte que
    # comparar contra o default: aqui variamos os campos em si).
    base = _run_hold(JointMaterial(emb_depth=0.0), t=1e4)
    changed = _run_hold(JointMaterial(emb_depth=0.0, creep_t_c=999.0,
                                      creep_alpha_sat=3.0), t=1e4)
    assert changed == base


def test_registry_truth_creep_t_c_le_zero_falls_back_to_log():
    # creep_mode="saturating" MAS creep_t_c<=0 (default 0.0): guarda "E
    # creep_t_c>0" do brief nao fecha -> cai no ramo log-t, bit-identico.
    base = _run_hold(JointMaterial(emb_depth=0.0), t=1e4)
    fallback = _run_hold(JointMaterial(emb_depth=0.0, creep_mode="saturating"),
                         t=1e4)
    assert fallback == base


def test_flag_on_does_change_trajectory():
    # contrapositiva: com creep_mode="saturating" E creep_t_c>0, a
    # trajetoria MUDA -- os testes de inercia acima nao passam vacuamente.
    base = _run_hold(JointMaterial(emb_depth=0.0), t=1e4)
    sat = _run_hold(JointMaterial(emb_depth=0.0, creep_mode="saturating",
                                  creep_t_c=1e4), t=1e4)
    assert sat != base


def test_creep_alpha_sat_changes_saturating_trajectory():
    # creep_alpha_sat (expoente de forma, stretched exponential) tem efeito
    # quando o modo saturante esta ativo -- nao e' um campo decorativo.
    a = _run_hold(JointMaterial(emb_depth=0.0, creep_mode="saturating",
                                creep_t_c=1e4, creep_alpha_sat=1.0), t=1e4)
    b = _run_hold(JointMaterial(emb_depth=0.0, creep_mode="saturating",
                                creep_t_c=1e4, creep_alpha_sat=2.0), t=1e4)
    assert a != b


# --------------------------------------------------- ParameterRegistry (KB) ---
def test_creep_t_c_and_alpha_sat_registered_fittable_same_regime_as_C_creep():
    rules = {r.name: r for r in PARAMETER_REGISTRY}
    assert rules["creep_t_c"].fittable is True
    assert rules["creep_alpha_sat"].fittable is True
    # mesmo predicado (_sempre) do C_creep ja existente -- mesma fisica de
    # assentamento sob tempo/carga, so muda a cinetica (log vs saturante).
    assert rules["creep_t_c"].active is rules["C_creep"].active
    assert rules["creep_alpha_sat"].active is rules["C_creep"].active


def test_creep_mode_not_registered_mode_switch_like_kj_mode_conform_driver():
    # mode switch (string): mesmo idioma de kj_mode/conform_driver/k_tr_mode
    # -- OMITIDO do registro por completo (nao apenas fittable=False).
    names = {r.name for r in PARAMETER_REGISTRY}
    assert "creep_mode" not in names
    assert "kj_mode" not in names          # mesmo idioma (sanity da analogia)
    assert "conform_driver" not in names


def _cond(name, delta_amp=0.0):
    return ConditionSpec(
        name=name,
        curves=[{"name": name, "cycles": np.array([0.0, 100.0]),
                 "ratio": np.array([1.0, 0.9])}],
        F0_init=50e3, F_amp=20e3, delta_amp=delta_amp)


def test_creep_t_c_and_alpha_sat_offered_even_axial_only():
    # _sempre (igual C_creep): oferecido mesmo sem slip transversal --
    # creep e' funcao do tempo sob carga, nao do regime de carregamento.
    bounds = {"creep_t_c": (1.0, 1e6), "creep_alpha_sat": (0.1, 5.0),
              "C_creep": (1e-12, 1e-9)}
    priors = {"creep_t_c": 1e4, "creep_alpha_sat": 1.0, "C_creep": 5e-11}
    cands = active_candidates(bounds, priors, [_cond("ax", delta_amp=0.0)],
                              theta=0.0, estimated=set())
    assert "creep_t_c" in cands
    assert "creep_alpha_sat" in cands
    assert "C_creep" in cands
