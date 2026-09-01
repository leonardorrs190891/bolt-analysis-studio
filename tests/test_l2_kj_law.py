"""L2 (plano L1-L7 task-5, 2026-07-17; roadmap #10 / MODEL_LEGITIMACY §4.8):
lei k_j(geometria, material) — Pedersen 2008 Eq.31 (PRIMARIA) + Wileman 1991
(cross-check), com dependencia de carga opcional de Phi via forma eliptica de
Grosse (1990).

Fecha a falsificacao "k_j fixo (k_j_init) nao escala com espessura de membro"
(Rousseau t10/12/14, MODEL_LEGITIMACY §4.8) substituindo a constante por uma
forma FISICA -- opt-in via `JointMaterial.kj_mode` ("" = comportamento atual).

Proveniencia: Pedersen 2008 doi 10.1007/s00419-007-0142-0 (Eq.31, rank
"closest-to-truth" +24% vs medido, Rousseau 2024); Wileman/Choudhury/Hodges
1991 doi 10.1115/1.2912799 (rank "+45-59% superestima"); ambos em
`New_Theory/r5_anchors.json["kj_laws"]` (Task 1, Fatia 0). Grosse 1990
(dissertacao, colapso de rigidez ~50x proximo da separacao) para a forma
eliptica opcional em `phi_load_dep`.
"""
import math

import pytest

from bolt_analysis_studio.calibration import knowledge_base as kb
from bolt_analysis_studio.calibration import library_common
from bolt_analysis_studio.calibration.library_common import kj_from_geometry
from bolt_analysis_studio.calibration.parameter_registry import PARAMETER_REGISTRY
from bolt_analysis_studio.core.solver_worker import coerce_v2_overrides
from bolt_analysis_studio.numerical import dynamic_stiffness_analyzer as dsa
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    U_loaded,
)

F0_INIT = 50000.0


def _geom_no_hw():
    """Geometria M16-like, SEM furo/arruela (default 0.0) -- kj_mode cai no
    fallback (comportamento atual)."""
    d, p = 16e-3, 2e-3
    d2 = d - 0.6495 * p
    return JointGeometry(A_s=157e-6, L_eff=0.05, d_2=d2, pitch=p,
                        r_bearing=0.75 * d, A_contact=1e-4)


def _geom_with_hw():
    """Mesma geometria, COM furo/arruela disponiveis (valores ilustrativos de
    unit test -- a validacao fisica contra Rousseau/Zhang e' a Task 6)."""
    d, p = 16e-3, 2e-3
    d2 = d - 0.6495 * p
    return JointGeometry(A_s=157e-6, L_eff=0.05, d_2=d2, pitch=p,
                        r_bearing=0.75 * d, A_contact=1e-4,
                        d_hole=17.5e-3, d_washer=30e-3)


# =========================================================== kj_from_geometry
# --- Step 1 do brief: valores analiticos das duas leis (EXATOS) --------------

def test_wileman_steel_matches_closed_form():
    E, d, L = 206.8e9, 0.012, 0.024   # d/L = 0.5
    k = kj_from_geometry(12, 24, E, 13.0, 24.0, mode="wileman")
    assert abs(k - E * d * 0.78715 * math.exp(0.62873 * 0.5)) / k < 1e-6


def test_pedersen_asymptote():
    E, d, L = 206.8e9, 0.012, 0.024
    alpha, beta = 13.0 / 12.0, 24.0 / 12.0
    exp_k = E * d * (0.59 * (beta**2 - alpha**2) * d / L + 0.20 * (beta + alpha))
    k = kj_from_geometry(12, 24, E, 13.0, 24.0, mode="pedersen")
    assert abs(k - exp_k) / exp_k < 1e-6


def test_pedersen_below_wileman_at_high_dL():
    kw = kj_from_geometry(24, 12, 206.8e9, 26.0, 36.0, mode="wileman")   # d/L=2
    kp = kj_from_geometry(24, 12, 206.8e9, 26.0, 36.0, mode="pedersen")
    assert kp < kw   # Pedersen le ~30% abaixo em d/L=2 (nota pedersen2008)


# --- robustez / correctness adicional ---------------------------------------

def test_wileman_material_specific_aluminum():
    # material= troca a linha da tabela AB (nao duplica valor -- le do KB).
    E, d_mm, L_mm = 206.8e9, 12.0, 24.0
    A, B = kb.kj_law("wileman1991")["AB"]["aluminum"]
    expected = E * (d_mm * 1e-3) * A * math.exp(B * 0.5)
    got = kj_from_geometry(d_mm, L_mm, E, 13.0, 24.0, mode="wileman",
                           material="aluminum")
    assert got == pytest.approx(expected, rel=1e-6)
    assert got != pytest.approx(
        kj_from_geometry(d_mm, L_mm, E, 13.0, 24.0, mode="wileman",
                         material="steel"), rel=1e-6)


def test_wileman_unknown_material_raises_loud():
    with pytest.raises(KeyError):
        kj_from_geometry(12, 24, 206.8e9, 13.0, 24.0, mode="wileman",
                         material="unobtainium")


def test_unknown_mode_raises_value_error():
    with pytest.raises(ValueError):
        kj_from_geometry(12, 24, 206.8e9, 13.0, 24.0, mode="bogus")


def test_pedersen_material_arg_is_ignored_no_kb_lookup(monkeypatch):
    # Pedersen (Eq.31) e' material-independente -- nao deve tocar o KB.
    def _boom(name):
        raise AssertionError("kj_law nao deveria ser chamado em modo pedersen")
    monkeypatch.setattr(kb, "kj_law", _boom)
    k = kj_from_geometry(12, 24, 206.8e9, 13.0, 24.0, mode="pedersen",
                         material="whatever")
    assert k > 0


# ===================================================== knowledge_base.kj_law

def test_kb_kj_law_pedersen2008():
    p = kb.kj_law("pedersen2008")
    assert p["source"] == "10.1007/s00419-007-0142-0"
    assert "closest-to-truth" in p["rank"]


def test_kb_kj_law_wileman1991_ab_table():
    w = kb.kj_law("wileman1991")
    assert w["AB"]["steel"] == [0.78715, 0.62873]
    assert w["AB"]["general"] == [0.78952, 0.62914]
    assert w["source"] == "10.1115/1.2912799"


def test_kb_kj_law_unknown_name_raises_loud():
    with pytest.raises(KeyError):
        kb.kj_law("nonexistent2099")


# ===================================================== JointGeometry.d_nominal

def test_geometry_d_nominal_inverts_iso724():
    geom = JointGeometry(d_2=14.701e-3, pitch=2e-3)
    assert geom.d_nominal == pytest.approx(0.016, rel=1e-4)


def test_geometry_hole_washer_default_zero_unavailable():
    geom = JointGeometry()
    assert geom.d_hole == 0.0
    assert geom.d_washer == 0.0


# ===================================================== engine hookup: kj_mode

def test_kj_mode_default_empty_string():
    assert JointMaterial().kj_mode == ""


def test_kj_mode_pedersen_falls_back_when_geometry_lacks_hole_washer():
    # geometria SEM furo/arruela (default 0.0) -> fallback silencioso,
    # documentado no campo. k_j_init permanece o do material original, e
    # self.mat permanece o MESMO objeto (nenhuma copia necessaria).
    mat = JointMaterial(kj_mode="pedersen")
    ana = DynamicStiffnessAnalyzer(_geom_no_hw(), mat, F0_INIT)
    assert ana.mat.k_j_init == JointMaterial().k_j_init
    assert ana.mat is mat


def test_kj_mode_pedersen_overrides_k_j_init_when_geometry_available():
    geom = _geom_with_hw()
    mat = JointMaterial(kj_mode="pedersen")
    ana = DynamicStiffnessAnalyzer(geom, mat, F0_INIT)
    expected = kj_from_geometry(geom.d_nominal * 1e3, geom.L_eff * 1e3,
                                geom.E, geom.d_hole * 1e3,
                                geom.d_washer * 1e3, mode="pedersen")
    assert ana.mat.k_j_init == pytest.approx(expected)
    assert ana.mat.k_j_init != JointMaterial().k_j_init
    # copia LOCAL -- o objeto do chamador NUNCA e mutado.
    assert ana.mat is not mat
    assert mat.k_j_init == JointMaterial().k_j_init


def test_kj_mode_wileman_overrides_k_j_init_when_geometry_available():
    geom = _geom_with_hw()
    mat = JointMaterial(kj_mode="wileman")
    ana = DynamicStiffnessAnalyzer(geom, mat, F0_INIT)
    expected = kj_from_geometry(geom.d_nominal * 1e3, geom.L_eff * 1e3,
                                geom.E, geom.d_hole * 1e3,
                                geom.d_washer * 1e3, mode="wileman")
    assert ana.mat.k_j_init == pytest.approx(expected)


def test_kj_mode_unknown_string_falls_back_like_empty():
    # mode invalido/typo -- mesmo idioma de k_tr_mode/conform_driver (nunca
    # levanta, so nao ativa).
    mat = JointMaterial(kj_mode="pederson_typo")
    ana = DynamicStiffnessAnalyzer(_geom_with_hw(), mat, F0_INIT)
    assert ana.mat.k_j_init == JointMaterial().k_j_init
    assert ana.mat is mat


def test_kj_mode_downstream_physics_uses_overridden_value():
    # k_j_ax(F_0=F_0_init) deve refletir o k_j_init NOVO (ratio=1 no init).
    geom = _geom_with_hw()
    mat = JointMaterial(kj_mode="pedersen")
    ana = DynamicStiffnessAnalyzer(geom, mat, F0_INIT)
    assert dsa.k_j_ax(ana.state, ana.mat) == pytest.approx(ana.mat.k_j_init)
    assert ana.mat.k_j_init != 4e9   # o default de JointMaterial.k_j_init


# --------------------------------------- kj_mode_engaged (fix wave task-5) ---
# Sinal positivo de engate: o fallback silencioso (linhas acima) nao dava a
# um consumidor (ex.: gate D5 Task 6) como saber se a lei REALMENTE rodou ou
# se caiu no fallback -- risco de corromper o gate (ele mediria o k_j_init
# antigo achando que testou a lei nova). `kj_mode_engaged` fecha isso: True
# SOMENTE quando o replace() do __init__ dispara; o fallback em si segue
# silencioso (sem warning/excecao).

def test_kj_mode_engaged_true_when_law_fires_with_complete_geometry():
    # (a) kj_mode="pedersen" + geometria completa => engaged=True E k_j
    # realmente difere do default (nao so o flag isolado).
    geom = _geom_with_hw()
    mat = JointMaterial(kj_mode="pedersen")
    ana = DynamicStiffnessAnalyzer(geom, mat, F0_INIT)
    assert ana.kj_mode_engaged is True
    assert ana.mat.k_j_init != JointMaterial().k_j_init


def test_kj_mode_engaged_false_when_geometry_incomplete():
    # (b) kj_mode setado mas geometria SEM furo/arruela => fallback
    # silencioso (comportamento inalterado) e o sinal fica False.
    mat = JointMaterial(kj_mode="pedersen")
    ana = DynamicStiffnessAnalyzer(_geom_no_hw(), mat, F0_INIT)
    assert ana.kj_mode_engaged is False
    assert ana.mat.k_j_init == JointMaterial().k_j_init


def test_kj_mode_engaged_false_in_default_mode():
    # (c) modo default (kj_mode="") -- a lei nunca engata, mesmo com
    # geometria completa disponivel.
    ana = DynamicStiffnessAnalyzer(_geom_with_hw(), JointMaterial(), F0_INIT)
    assert ana.kj_mode_engaged is False


# ------------------------------------------------- spy: caminho de codigo ---
def _spy_on_kj_from_geometry(monkeypatch):
    calls = []
    original = library_common.kj_from_geometry

    def _spy(*a, **kw):
        calls.append((a, kw))
        return original(*a, **kw)

    monkeypatch.setattr(library_common, "kj_from_geometry", _spy)
    return calls


def test_kj_mode_off_never_calls_kj_from_geometry(monkeypatch):
    calls = _spy_on_kj_from_geometry(monkeypatch)
    DynamicStiffnessAnalyzer(_geom_with_hw(), JointMaterial(), F0_INIT)
    assert calls == []


def test_kj_mode_pedersen_calls_kj_from_geometry_exactly_once(monkeypatch):
    calls = _spy_on_kj_from_geometry(monkeypatch)
    DynamicStiffnessAnalyzer(_geom_with_hw(),
                             JointMaterial(kj_mode="pedersen"), F0_INIT)
    assert len(calls) == 1


def test_kj_mode_pedersen_without_geometry_never_calls_kj_from_geometry(monkeypatch):
    # geometria sem furo/arruela -- guard curto-circuita ANTES da chamada.
    calls = _spy_on_kj_from_geometry(monkeypatch)
    DynamicStiffnessAnalyzer(_geom_no_hw(),
                             JointMaterial(kj_mode="pedersen"), F0_INIT)
    assert calls == []


# --------------------------------------------------------- bit-identidade ---
def _run_trajectory(mat, geom, n=100):
    ana = DynamicStiffnessAnalyzer(geom, mat, F0_INIT)
    for _ in range(n):
        ana.step_cycle(20e3, math.pi / 2, 0.5, delta_amp=0.5e-3)
    return ana.state.F_0


def test_bit_identity_kj_mode_off_full_trajectory_even_with_hw_geometry():
    # geometria COM furo/arruela disponiveis, mas kj_mode="" -- o switch
    # (nao a mera disponibilidade de geometria) e' quem gateia o efeito.
    geom = _geom_with_hw()
    baseline = _run_trajectory(JointMaterial(), geom)
    explicit = _run_trajectory(JointMaterial(kj_mode="", phi_load_dep=0.0), geom)
    assert explicit == baseline


def test_bit_identity_defaults_vs_explicit_zero_no_hw_geometry():
    geom = _geom_no_hw()
    baseline = _run_trajectory(JointMaterial(), geom)
    explicit = _run_trajectory(JointMaterial(kj_mode="", phi_load_dep=0.0), geom)
    assert explicit == baseline


# =========================================================== phi_load_dep --

def _phi_load_dep_expected(state, geom, mat, F_ax_ext):
    lam = min(max(F_ax_ext / (mat.phi_load_dep * state.F_0), 0.0), 1.0)
    frac_m = 1.0 - math.sqrt(max(0.0, 2.0 * lam - lam**2))
    kj = dsa.k_j_ax(state, mat)
    Phi = dsa.Phi_eff(state, geom, mat)
    F_bolt = state.F_0 + Phi * F_ax_ext
    F_joint = state.F_0 * frac_m
    return F_bolt**2 / (2 * geom.k_b) + F_joint**2 / (2 * kj)


def test_phi_load_dep_default_off_matches_linear_partition():
    geom = _geom_with_hw()
    mat = JointMaterial()   # phi_load_dep=0.0 default
    state = SlowState(F_0=50e3, F_0_init=50e3)
    F_ax = 10e3
    kj = dsa.k_j_ax(state, mat)
    Phi = dsa.Phi_eff(state, geom, mat)
    F_bolt = state.F_0 + Phi * F_ax
    F_joint = state.F_0 - (1 - Phi) * F_ax
    expected = F_bolt**2 / (2 * geom.k_b) + F_joint**2 / (2 * kj)
    assert U_loaded(state, geom, mat, F_ax) == pytest.approx(expected, abs=1e-6)


def test_phi_load_dep_matches_grosse_ellipse_formula():
    geom = _geom_with_hw()
    mat = JointMaterial(phi_load_dep=0.5)
    state = SlowState(F_0=50e3, F_0_init=50e3)
    F_ax = 10e3   # lam = 10e3/(0.5*50e3) = 0.4 (dentro do dominio [0,1])
    expected = _phi_load_dep_expected(state, geom, mat, F_ax)
    assert U_loaded(state, geom, mat, F_ax) == pytest.approx(expected)


def test_phi_load_dep_zero_load_gives_frac_one_continuous_with_linear():
    # F_ax_ext=0 -> lam=0 -> frac=1 -> F_joint=F_i, identico ao caso linear
    # em F_ax_ext=0 (continuidade na origem).
    geom = _geom_with_hw()
    mat = JointMaterial(phi_load_dep=0.3)
    state = SlowState(F_0=50e3, F_0_init=50e3)
    assert U_loaded(state, geom, mat, 0.0) == pytest.approx(
        state.F_0**2 / (2 * geom.k_b) + state.F_0**2 / (2 * dsa.k_j_ax(state, mat)))


def test_phi_load_dep_saturates_at_zero_beyond_critical_no_rebound():
    geom = _geom_with_hw()
    mat = JointMaterial(phi_load_dep=0.05)   # critico = 0.05*50e3 = 2500 N (baixo)
    state = SlowState(F_0=50e3, F_0_init=50e3)
    # dois pontos alem do critico (lam=1.5 e lam=3.0) -- ambos devem saturar
    # em fracao=0 (F_joint=0), NAO reaparecer (a elipse fechada reapareceria
    # sem o clip).
    F_ax_1 = 1.5 * mat.phi_load_dep * state.F_0
    F_ax_2 = 3.0 * mat.phi_load_dep * state.F_0
    Phi = dsa.Phi_eff(state, geom, mat)
    kj = dsa.k_j_ax(state, mat)
    for F_ax in (F_ax_1, F_ax_2):
        F_bolt = state.F_0 + Phi * F_ax
        expected_saturated = F_bolt**2 / (2 * geom.k_b) + 0.0
        assert U_loaded(state, geom, mat, F_ax) == pytest.approx(expected_saturated)


def test_registry_truth_phi_load_dep_inert_at_zero_but_active_above_zero():
    # requisito mais forte que so a formula: pinamos o comportamento OFF vs ON
    # contra o proprio U_loaded do engine (nao so contra a formula re-derivada).
    geom = _geom_with_hw()
    state = SlowState(F_0=50e3, F_0_init=50e3)
    F_ax = 20e3
    off = U_loaded(state, geom, JointMaterial(phi_load_dep=0.0), F_ax)
    on = U_loaded(state, geom, JointMaterial(phi_load_dep=0.6), F_ax)
    assert off != pytest.approx(on)


# ================================================== registro / overrides ---

def test_phi_load_dep_is_not_yet_fittable_in_registry():
    # Task-5 review adjudication: declarado no registro (regime _sempre,
    # coberto pelos testes de comportamento acima), mas fittable=False --
    # ainda nao identificavel no objetivo atual (so afeta U_loaded
    # diagnostico). Reavaliar quando phi_load_dep entrar no objetivo de fit.
    rule = next(r for r in PARAMETER_REGISTRY if r.name == "phi_load_dep")
    assert rule.fittable is False


def test_kj_mode_has_no_registry_rule_mirrors_conform_driver():
    # mode switches (str) nunca sao fittable=True (licao da revisao Task 2)
    # -- o padrao estabelecido e' OMITIR o campo do registro inteiramente,
    # exatamente como conform_driver/k_tr_mode/loose_torsion_mode.
    names = {r.name for r in PARAMETER_REGISTRY}
    assert "kj_mode" not in names
    assert "conform_driver" not in names   # confirma o precedente espelhado


def test_kj_mode_passes_type_aware_override_filter():
    out = coerce_v2_overrides({"kj_mode": "pedersen"},
                              JointMaterial.__dataclass_fields__)
    assert out == {"kj_mode": "pedersen"}


def test_phi_load_dep_passes_type_aware_override_filter_as_float():
    out = coerce_v2_overrides({"phi_load_dep": "0.4"},
                              JointMaterial.__dataclass_fields__)
    assert out == {"phi_load_dep": 0.4}
    assert isinstance(out["phi_load_dep"], float)


def test_unknown_kj_mode_value_passes_through_filter_untouched():
    # o filtro e' type-aware, nao um whitelist de valores -- validacao de
    # VALOR (pedersen/wileman/"") acontece no proprio engine (fallback
    # silencioso), nao no filtro de overrides.
    out = coerce_v2_overrides({"kj_mode": "whatever"},
                              JointMaterial.__dataclass_fields__)
    assert out == {"kj_mode": "whatever"}
