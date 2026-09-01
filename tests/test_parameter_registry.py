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
    "k_wear_spec": (5e-15, 5e-13), "C_creep": (1e-12, 1e-9),
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
    # condicao: k_wear_spec e tr_loose_gain nao podem ser candidatos.
    cands = active_candidates(BOUNDS_ALL, PHYSICAL_PRIORS,
                              [_cond("ax", delta_amp=0.0)],
                              theta=0.0, estimated=set())
    assert "k_wear_spec" not in cands
    assert "tr_loose_gain" not in cands
    assert "emb_depth" in cands and "N_emb" in cands and "C_creep" in cands
    assert "c_D" not in cands and "k_dmg_wear" not in cands  # sem dano


def test_mixed_dataset_keeps_transverse_constants():
    # theta global 0, mas UMA condicao tem delta_amp>0 => alguma condicao
    # excita wear/loosening transversal => constantes continuam candidatas.
    conds = [_cond("ax", delta_amp=0.0), _cond("sh", delta_amp=0.5e-3)]
    cands = active_candidates(BOUNDS_ALL, PHYSICAL_PRIORS, conds,
                              theta=0.0, estimated=set())
    assert "k_wear_spec" in cands and "tr_loose_gain" in cands


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
    assert set(res["candidates"]) == {"emb_depth", "N_emb", "k_wear_spec",
                                      "C_creep", "tr_loose_gain"}
    res_dmg = SharedCalibrator(
        _mini_cfg([_cond("a", damage=True)])).fit_parsimonious(
        tol=10.0, max_constants=1)
    assert set(res_dmg["candidates"]) == set(BOUNDS_ALL)


def test_fit_parsimonious_axial_only_drops_transverse_candidates():
    res = SharedCalibrator(
        _mini_cfg([_cond("ax", delta_amp=0.0)], theta=0.0)).fit_parsimonious(
        tol=10.0, max_constants=1)
    assert "k_wear_spec" not in res["candidates"]
    assert "tr_loose_gain" not in res["candidates"]
    assert res["free_constants"] == []   # tol alto: baseline apenas


def test_conformation_offered_only_under_elevated_pressure():
    # W_conf_ref/conform_pressure_exp so sao candidatos quando ALGUMA condicao
    # tem F0 nao-nominal (estimated/torque) => over-torque (spec 2026-07-04).
    bounds = dict(BOUNDS_ALL, W_conf_ref=(1e2, 1e8))
    priors = dict(PHYSICAL_PRIORS, W_conf_ref=1e4)
    # all-nominal: NAO oferece W_conf_ref (k_wear_spec transversal continua)
    nom = active_candidates(bounds, priors, [_cond("nova")],
                            theta=np.pi / 2, estimated=set())
    assert "W_conf_ref" not in nom
    assert "k_wear_spec" in nom
    # over-torque presente (F0 estimado): oferece W_conf_ref
    ot = active_candidates(bounds, priors, [_cond("nova"), _cond("sob")],
                           theta=np.pi / 2, estimated={"sob"})
    assert "W_conf_ref" in ot


def test_W_crit_offered_only_under_damage_regime():
    """W_crit (onset do dano, predictive trigger) so e oferecido quando o dano
    esta ativo (so identificavel onde D cresce, c_D>0); ausente sem dano."""
    bounds = dict(BOUNDS_ALL, W_crit=(1e3, 1e7))
    priors = dict(PHYSICAL_PRIORS, W_crit=1e5)
    no_dmg = active_candidates(bounds, priors, [_cond("a"), _cond("b")],
                               np.pi / 2, set())
    assert "W_crit" not in no_dmg
    with_dmg = active_candidates(bounds, priors,
                                 [_cond("a"), _cond("b", damage=True)],
                                 np.pi / 2, set())
    assert "W_crit" in with_dmg


def test_registry_truth_W_crit_inert_without_damage_active():
    """Sem dano (c_D=0) o W_crit nao afeta a trajetoria (D=0 sempre) => bit-identico."""
    def run(m):
        ana = DynamicStiffnessAnalyzer(M16, m, 120e3)
        r = []
        for _ in range(200):
            ana.step_cycle(20e3, np.pi / 2, 0.5, delta_amp=0.5e-3)
            r.append(ana.state.F_0)
        return np.array(r)
    assert np.array_equal(run(JointMaterial()), run(JointMaterial(W_crit=1e4)))
