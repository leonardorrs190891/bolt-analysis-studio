"""L1 (plano L1-L7 task-3, roadmap #9): canal de desgaste de flanco de rosca
PROPORCIONAL a amplitude de carga axial A_F.

Falsificacao-alvo (MODEL_LEGITIMACY.md secao 4.6): o modelo tem
d(final)/d(A_F) ~ 0 em modo forca axial (falsificado vs Liu2017,
-2.216e-5/N). Este modulo testa o canal opt-in `flank_wear_on` (default 0.0
= OFF) que estende `ThreadFrettingLoss` com uma forma INDEPENDENTE do
`k_thread_fret` legado (que e' hardcoded linear em F_ax): parametrizada por
PRESSAO de flanco (F_0/A_s, nao forca) com um expoente de amplitude
AJUSTAVEL `flank_amp_exp` (candidato de literatura 1.5-1.6, Liu 2020,
super-linear).

Proveniencia: k_wear_flank seed 8.34e-15 1/Pa (kb.wear_spec_anchor("thread",
"35CrMo-SCM435"), Zhang 2019 EFA doi 10.1016/j.engfailanal.2019.05.001);
leitura do KB fica para a calibracao (Task 4) -- o engine so recebe as
constantes (nunca le o KB em runtime).
"""
import math

import numpy as np
import pytest

from bolt_analysis_studio.numerical import dynamic_stiffness_analyzer as dsa
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    ThreadFrettingLoss, flank_wear_axial_term,
)

M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)

ZHANG_K_WEAR_FLANK = 8.34e-15   # kb.wear_spec_anchor("thread", "35CrMo-SCM435")


def _geom():
    d, p = 16e-3, 2e-3
    d2 = d - 0.6495 * p
    d1 = d - 1.0825 * p
    A_s = math.pi / 4 * ((d2 + d1) / 2) ** 2
    return JointGeometry(A_s=A_s, L_eff=0.05, d_2=d2, pitch=p,
                         r_bearing=0.75 * d, A_contact=1e-4)


def _final_F0(mat, A_F, n=2000, F0=30e3, freq=30.0):
    """Modo forca axial puro: theta=0, sem delta_amp."""
    ana = DynamicStiffnessAnalyzer(_geom(), mat, F0)
    for _ in range(n):
        ana.step_cycle(A_F, 0.0, freq)
    return ana.state.F_0


def _spy_on_flank_term(monkeypatch):
    """Substitui dsa.flank_wear_axial_term por um espiao que conta chamadas
    mas delega no original -- prova se o CAMINHO DE CODIGO do canal L1 foi
    entrado, nao so se o resultado numerico mudou (mesma tecnica de
    tests/test_l3_famp_coupling.py::_spy_on_ceiling)."""
    calls = []
    original = dsa.flank_wear_axial_term

    def _spy(state, geom, mat, F_amp, theta_load, freq):
        calls.append(1)
        return original(state, geom, mat, F_amp, theta_load, freq)

    monkeypatch.setattr(dsa, "flank_wear_axial_term", _spy)
    return calls


# --------------------------------------------------------- bit-identity off
def test_bit_identity_off(monkeypatch):
    # (i) flag off (default): F_0 final e' INSENSIVEL a A_F -- exatamente o
    # gap falsificado hoje (Liu2017 -2.216e-5/N vs modelo ~0).
    a = _final_F0(JointMaterial(), 7.5e3)
    b = _final_F0(JointMaterial(), 12.5e3)
    assert a == b

    # (ii) requisito mais forte que a bit-identidade: o CAMINHO DE CODIGO do
    # canal L1 nao pode ser entrado quando flank_wear_on==0.0 (guard
    # curto-circuita ANTES de qualquer computo, nao so retorna neutro).
    calls = _spy_on_flank_term(monkeypatch)
    _final_F0(JointMaterial(), 10e3, n=50)
    assert calls == []


def test_flag_on_does_enter_code_path(monkeypatch):
    # contrapositiva: com o flag ligado (modo forca axial), o helper E
    # chamado em todo ciclo -- o teste acima nao passa vacuamente.
    calls = _spy_on_flank_term(monkeypatch)
    m = JointMaterial(flank_wear_on=1.0, k_wear_flank=ZHANG_K_WEAR_FLANK)
    _final_F0(m, 10e3, n=50)
    assert len(calls) == 50


def test_disp_mode_never_enters_code_path_even_with_flag_on(monkeypatch):
    # so modo forca/axial: em disp-mode (delta_amp dado) o canal L1 NUNCA
    # roda, mesmo com flank_wear_on=1.0 (delta_amp e' sempre transversal
    # nesta convencao do engine -- resolve_transverse_slip ignora theta_load
    # quando delta_amp e' dado).
    calls = _spy_on_flank_term(monkeypatch)
    m = JointMaterial(flank_wear_on=1.0, k_wear_flank=ZHANG_K_WEAR_FLANK)
    ana = DynamicStiffnessAnalyzer(_geom(), m, 50e3)
    for _ in range(50):
        ana.step_cycle(12000.0, math.pi / 2, 0.5, delta_amp=0.5e-3)
    assert calls == []


def test_flank_wear_on_alone_without_k_wear_flank_is_inert():
    # flank_wear_on=1.0 sozinho (k_wear_flank ainda 0.0, default) nao move a
    # trajetoria -- k_wear_flank=0 multiplicando qualquer coisa da' d_w=0.0
    # exato: o canal precisa dos DOIS (gate E magnitude).
    base = _final_F0(JointMaterial(), 10e3, n=200)
    only_gate = _final_F0(JointMaterial(flank_wear_on=1.0), 10e3, n=200)
    assert only_gate == base


# ------------------------------------------------------ efeito fisico (ON)
def test_dloss_dAF_nonzero_when_on():
    m = JointMaterial(flank_wear_on=1.0, k_wear_flank=ZHANG_K_WEAR_FLANK,
                      flank_amp_exp=1.0)
    lo = _final_F0(m, 7.5e3)
    hi = _final_F0(m, 12.5e3)
    assert hi < lo   # maior amplitude axial => maior perda (sinal do Liu2017: -2.2e-5/N)


def test_transverse_untouched():
    # em disp-mode transversal puro (A_F=0) o canal precisa ser inerte --
    # harness copiado de tests/test_slip_onset_incubation.py.
    def _run(**mat_kw):
        mat = JointMaterial(**mat_kw)
        ana = DynamicStiffnessAnalyzer(_geom(), mat, 50000.0)
        r = [1.0]
        for _ in range(559):
            ana.step_cycle(12000.0, math.pi / 2, 0.5, delta_amp=0.5e-3)
            r.append(max(ana.state.F_0, 0.0) / 50000.0)
        return np.array(r)

    off = _run()
    on = _run(flank_wear_on=1.0, k_wear_flank=ZHANG_K_WEAR_FLANK, flank_amp_exp=1.5)
    assert np.array_equal(off, on)


def test_conservation_residual_axial_flag_on():
    # analyzer.energy.conservation_residual ~ 0 num run axial com o flag on
    # -- mesma tolerancia relativa usada por outros testes de conservacao
    # (test_surface_damage.py): escala pelos termos do budget.
    m = JointMaterial(flank_wear_on=1.0, k_wear_flank=ZHANG_K_WEAR_FLANK,
                      flank_amp_exp=1.5, mu_thread=0.12, mu_bearing=0.12,
                      emb_depth=9.5e-6)
    ana = DynamicStiffnessAnalyzer(_geom(), m, 40e3)
    for _ in range(2000):
        ana.step_cycle(20e3, 0.0, 30.0)
    e = ana.energy
    total = abs(e.W_ext) + abs(e.U_released) + abs(e.W_diss_total) + 1.0
    assert abs(e.conservation_residual) / total < 1e-2


def test_both_channels_combine_additively():
    # quando k_thread_fret (legado) E flank_wear_on (L1) estao ATIVOS ao
    # mesmo tempo, a perda e' a SOMA dos dois canais (mesmo mecanismo,
    # dF_0_by_mech["thread_fretting"] agrega ambos p/ a decomposicao).
    geom = _geom()
    st = SlowState(F_0=40e3, F_0_init=40e3)
    F_amp, theta, freq, n = 12e3, 0.0, 30.0, 100

    m_legacy = JointMaterial(k_thread_fret=0.5)
    m_l1 = JointMaterial(flank_wear_on=1.0, k_wear_flank=ZHANG_K_WEAR_FLANK)
    m_both = JointMaterial(k_thread_fret=0.5, flank_wear_on=1.0,
                           k_wear_flank=ZHANG_K_WEAR_FLANK)

    r_legacy = ThreadFrettingLoss().rate(st, geom, m_legacy, F_amp, theta, freq, n)
    r_l1 = ThreadFrettingLoss().rate(st, geom, m_l1, F_amp, theta, freq, n)
    r_both = ThreadFrettingLoss().rate(st, geom, m_both, F_amp, theta, freq, n)

    assert r_legacy["dF_0"] < 0.0 and r_l1["dF_0"] < 0.0    # sanity: ambos ativos
    assert r_both["dF_0"] == pytest.approx(
        r_legacy["dF_0"] + r_l1["dF_0"], rel=1e-9)
    assert r_both["dE_dissipated"] == pytest.approx(
        r_legacy["dE_dissipated"] + r_l1["dE_dissipated"], rel=1e-9)
    assert r_both["ds"]["delta_thread_fret"] == pytest.approx(
        r_legacy["ds"]["delta_thread_fret"] + r_l1["ds"]["delta_thread_fret"],
        rel=1e-9)


# --------------------------------------------------------- formula direta
def test_helper_formula_matches_hand_calc():
    # verifica flank_wear_axial_term direto contra a formula fechada (sem
    # dependencia de frequencia, fret_freq_exp=0 default) -- nenhuma
    # constante magica: tudo via JointMaterial/geometria.
    geom = _geom()
    mat = JointMaterial(k_wear_flank=2e-14, flank_amp_exp=1.3, mu_thread=0.13)
    st = SlowState(F_0=40e3, F_0_init=40e3)
    F_amp, theta = 12e3, 0.0
    d_w, dE = flank_wear_axial_term(st, geom, mat, F_amp, theta, freq=30.0)

    F_ax = F_amp * abs(np.cos(theta))
    s_th = F_ax / geom.k_b
    slip_dist = 2.0 * s_th
    p_flank = 40e3 / geom.A_s
    d_w_expected = mat.k_wear_flank * p_flank * slip_dist ** mat.flank_amp_exp
    dE_expected = mat.mu_thread * 40e3 * slip_dist

    assert d_w == pytest.approx(d_w_expected, rel=1e-12)
    assert dE == pytest.approx(dE_expected, rel=1e-12)


def test_flank_amp_exp_is_super_linear_when_above_one():
    # flank_amp_exp>1 (candidato Liu2020 1.5-1.6): a razao de d_w entre
    # amplitude alta/baixa cresce EXATAMENTE como (razao de A_F)^exp -- num
    # unico ciclo (isola a formula da dinamica multi-ciclo). Verifica que o
    # expoente de fato modula a FORMA (nao so a magnitude).
    geom = _geom()
    st = SlowState(F_0=40e3, F_0_init=40e3)

    def _d_w(exp, A_F):
        mat = JointMaterial(k_wear_flank=ZHANG_K_WEAR_FLANK, flank_amp_exp=exp)
        d_w, _ = flank_wear_axial_term(st, geom, mat, A_F, 0.0, freq=30.0)
        return d_w

    lo, hi = 7.5e3, 15e3                                  # razao de amplitude = 2x
    ratio_lin = _d_w(1.0, hi) / _d_w(1.0, lo)
    ratio_sup = _d_w(1.6, hi) / _d_w(1.6, lo)
    assert ratio_lin == pytest.approx(2.0, rel=1e-9)          # linear: razao = razao de A_F
    assert ratio_sup == pytest.approx(2.0 ** 1.6, rel=1e-9)   # super-linear: razao^exp
    assert ratio_sup > ratio_lin > 1.0


def test_freq_factor_reused_from_legacy_fret_fields():
    # "com o fator de freq existente do ThreadFrettingLoss, se aquele canal
    # ja aplica um" (resolucao do controlador #4): fret_freq_exp/f_ref_fret
    # (legados, default OFF) tambem modulam o canal L1 quando != 0.
    geom = _geom()
    mat_flat = JointMaterial(k_wear_flank=ZHANG_K_WEAR_FLANK, fret_freq_exp=0.0)
    mat_freq = JointMaterial(k_wear_flank=ZHANG_K_WEAR_FLANK, fret_freq_exp=1.0,
                             f_ref_fret=15.0)
    st = SlowState(F_0=40e3, F_0_init=40e3)
    d_w_flat, _ = flank_wear_axial_term(st, geom, mat_flat, 12e3, 0.0, freq=15.0)
    d_w_ref, _ = flank_wear_axial_term(st, geom, mat_freq, 12e3, 0.0, freq=15.0)
    assert d_w_flat == pytest.approx(d_w_ref)     # em f=f_ref, fator=1 (identico)
    d_w_low, _ = flank_wear_axial_term(st, geom, mat_freq, 12e3, 0.0, freq=10.0)
    assert d_w_low > d_w_ref                       # freq menor => mais desgaste


def test_default_fields_present_and_inert():
    m = JointMaterial()
    assert m.flank_wear_on == 0.0
    assert m.k_wear_flank == 0.0
    assert m.flank_amp_exp == 1.0


# --------------------------------------------------------- registry-truth
def _axial_force_mode_trajectory(mat, n=150):
    ana = DynamicStiffnessAnalyzer(M16, mat, 50e3)
    out = []
    for _ in range(n):
        ana.step_cycle(20e3, 0.0, 0.5)      # theta=0 (axial), sem delta_amp
        out.append(ana.state.F_0)
    return np.array(out)


def _shear_disp_mode_trajectory(mat, n=150):
    ana = DynamicStiffnessAnalyzer(M16, mat, 50e3)
    out = []
    for _ in range(n):
        ana.step_cycle(20e3, math.pi / 2, 0.5, delta_amp=0.5e-3)
        out.append(ana.state.F_0)
    return np.array(out)


def test_registry_truth_flank_fields_inert_in_pure_transverse_disp_mode():
    # predicado do ParameterRule (_axial_forca, inverso de _transversal):
    # NUNCA oferecido em disp-mode transversal. Pinado contra o engine.
    base = _shear_disp_mode_trajectory(JointMaterial())
    ligado = _shear_disp_mode_trajectory(
        JointMaterial(flank_wear_on=1.0, k_wear_flank=ZHANG_K_WEAR_FLANK,
                     flank_amp_exp=1.5))
    assert np.array_equal(base, ligado)


def test_registry_truth_flank_fields_act_in_axial_force_mode():
    # contrapositiva: em modo forca axial os mesmos campos MUDAM a curva --
    # o teste de inercia acima nao passa vacuamente.
    base = _axial_force_mode_trajectory(JointMaterial())
    ligado = _axial_force_mode_trajectory(
        JointMaterial(flank_wear_on=1.0, k_wear_flank=ZHANG_K_WEAR_FLANK))
    assert not np.array_equal(base, ligado)
