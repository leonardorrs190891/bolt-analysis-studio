"""L3 (roadmap #4): F_amp <= mu_eff(F0)*F0 em disp-mode.

Fecha a limitacao L3 do plano L1-L7: a amplitude de forca transversal
IMPOSTA (F_amp, drive do loosening rotacional via RotationalLooseningLoss)
e o deslocamento imposto (delta_amp) sao hoje INDEPENDENTES em disp-mode --
fisicamente, acima do teto de Coulomb mu_eff(F0)*F0 a junta ja esta em
gross slip pleno e o excesso de F_amp nao pode se traduzir em mais forca
TRANSMITIDA. Este modulo testa o clamp opt-in `famp_couple_on` (default 0.0
= OFF) que reatribui F_amp no topo do ramo disp-mode de `step_cycle`.

Proveniencia: Murai/IJAMT-2023 (mu efetivo cai 0.46->0.24 com F0 crescente,
via mu_eff_lo/mu_eff_F0_ref), Measurement-2021 (limiares de slip-onset
proporcionais a F0), JMP-2021 (teto de gross-slip decai com o desgaste, via
gross_ceiling_decay*state.D).
"""
import math

import numpy as np
import pytest

from bolt_analysis_studio.numerical import dynamic_stiffness_analyzer as dsa
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    famp_gross_slip_ceiling,
)

F0_INIT = 50000.0

M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)


def _geom():
    d, p = 16e-3, 2e-3
    d2 = d - 0.6495 * p
    d1 = d - 1.0825 * p
    A_s = math.pi / 4 * ((d2 + d1) / 2) ** 2
    return JointGeometry(A_s=A_s, L_eff=0.05, d_2=d2, pitch=p,
                         r_bearing=0.75 * d, A_contact=1e-4)


def _run(mat, n=200, famp=8000.0, delta=0.5e-3, freq=0.5,
         theta=math.pi / 2):
    ana = DynamicStiffnessAnalyzer(_geom(), mat, F0_INIT)
    for _ in range(n):
        ana.step_cycle(famp, theta, freq, delta_amp=delta)
    return ana.state.F_0


def _spy_on_ceiling(monkeypatch):
    """Substitui dsa.famp_gross_slip_ceiling por um espiao que conta
    chamadas mas delega no original -- prova se o CAMINHO DE CODIGO do
    clamp foi entrado, nao so se o resultado numerico mudou."""
    calls = []
    original = dsa.famp_gross_slip_ceiling

    def _spy(state, mat):
        calls.append(1)
        return original(state, mat)

    monkeypatch.setattr(dsa, "famp_gross_slip_ceiling", _spy)
    return calls


# --------------------------------------------------------------- formula ---
def test_ceiling_formula_pure_coulomb_without_knockdown():
    # mu_eff_lo==0 => knockdown=1.0 exato: teto = mu_bearing_eff(D)*F_0.
    mat = JointMaterial()
    st = SlowState(F_0=50000.0)
    expected = dsa.mu_bearing_eff(st, mat) * 50000.0
    assert famp_gross_slip_ceiling(st, mat) == pytest.approx(expected)


def test_ceiling_formula_with_knockdown_interpolation():
    mat = JointMaterial(mu_eff_lo=0.5, mu_eff_F0_ref=100e3)
    st = SlowState(F_0=50000.0)          # F_0/mu_eff_F0_ref = 0.5 = k
    k = 0.5
    mu_eff_expected = dsa.mu_bearing_eff(st, mat) * (0.5 + 0.5 * k)  # x0.75
    assert famp_gross_slip_ceiling(st, mat) == pytest.approx(
        mu_eff_expected * 50000.0)


def test_ceiling_formula_knockdown_saturates_above_F0_ref():
    # F_0 >= mu_eff_F0_ref => k satura em 1.0 => knockdown=1.0 (sem reducao,
    # identico ao caso sem knockdown).
    mat = JointMaterial(mu_eff_lo=0.5, mu_eff_F0_ref=10e3)
    st = SlowState(F_0=50000.0)
    expected = dsa.mu_bearing_eff(st, mat) * 50000.0
    assert famp_gross_slip_ceiling(st, mat) == pytest.approx(expected)


def test_ceiling_formula_gross_ceiling_decay_shrinks_with_damage():
    mat_decay = JointMaterial(gross_ceiling_decay=0.5)
    mat_plain = JointMaterial()
    st = SlowState(F_0=50000.0, D=0.4)
    ceil_decay = famp_gross_slip_ceiling(st, mat_decay)
    ceil_plain = famp_gross_slip_ceiling(st, mat_plain)
    assert ceil_decay == pytest.approx(ceil_plain * (1.0 - 0.5 * 0.4))
    assert ceil_decay < ceil_plain


# ---------------------------------------------------------- bit-identity ---
def test_bit_identity_flag_off_default_vs_explicit_zero():
    # campos novos default-inertes nao mudam a trajetoria (bit-identidade).
    baseline = _run(JointMaterial())
    explicit_zero = _run(JointMaterial(famp_couple_on=0.0, mu_eff_lo=0.0,
                                       mu_eff_F0_ref=0.0,
                                       gross_ceiling_decay=0.0))
    assert explicit_zero == baseline


def test_flag_off_never_enters_clamp_code_path(monkeypatch):
    # requisito mais forte que a bit-identidade: o CAMINHO DE CODIGO do
    # clamp nao pode ser entrado quando famp_couple_on==0.0 (guard
    # curto-circuita ANTES de qualquer computo, nao so retorna neutro).
    calls = _spy_on_ceiling(monkeypatch)
    _run(JointMaterial(), n=50)
    assert calls == []


def test_flag_on_does_enter_clamp_code_path(monkeypatch):
    # contrapositiva: com o flag ligado (em disp-mode), o helper E chamado
    # em todo ciclo -- o teste acima nao passa vacuamente.
    calls = _spy_on_ceiling(monkeypatch)
    _run(JointMaterial(famp_couple_on=1.0), n=50)
    assert len(calls) == 50


def test_force_mode_never_enters_clamp_even_with_flag_on(monkeypatch):
    # so disp-mode (delta_amp dado): em force-mode (delta_amp=None) o clamp
    # NUNCA roda, mesmo com famp_couple_on=1.0.
    calls = _spy_on_ceiling(monkeypatch)
    mat = JointMaterial(famp_couple_on=1.0)
    ana = DynamicStiffnessAnalyzer(_geom(), mat, F0_INIT)
    for _ in range(50):
        ana.step_cycle(20e3, math.pi / 2, 0.5)   # sem delta_amp = force-mode
    assert calls == []


# ------------------------------------------------------- efeito fisico ---
def test_clamp_caps_extreme_famp_preserves_more_preload():
    # com F_amp absurdo, o clamp liga o teto Coulomb -- a versao clampada
    # NAO pode perder mais preload do que a desclampada (fisicamente o
    # excesso de forca imposta acima do teto nao se traduz em mais T_loose).
    f_clamped = _run(JointMaterial(famp_couple_on=1.0), famp=1e9)
    f_unclamped = _run(JointMaterial(), famp=1e9)
    assert f_clamped > f_unclamped
    assert 0.0 <= f_clamped <= F0_INIT


def test_knockdown_changes_trajectory_as_F0_falls_below_ref():
    # com mu_eff_lo>0, o teto ENCOLHE (via knockdown<1) conforme F0 cai
    # abaixo de mu_eff_F0_ref -- clamp mais apertado => preload final DIFERE
    # (mais alto) do caso sem knockdown. tr_loose_gain elevado (20 em vez do
    # default 2.0) garante que o loosening rotacional de fato ATIVE (T_loose
    # > T_resist) sob o teto Coulomb -- com o default 2.0 o proprio teto
    # (sem excesso de F_amp algum) ja fica abaixo do limiar de T_resist para
    # este F0/geometria, e a diferenca de knockdown ficaria mascarada por um
    # mecanismo permanentemente "stuck" nas duas corridas (falso-negativo).
    common = dict(famp_couple_on=1.0, tr_loose_gain=20.0)
    with_knockdown = _run(JointMaterial(mu_eff_lo=0.5, mu_eff_F0_ref=F0_INIT,
                                        **common), famp=1e9)
    without_knockdown = _run(JointMaterial(**common), famp=1e9)
    assert with_knockdown != without_knockdown
    assert with_knockdown >= without_knockdown


# ----------------------------------------------- registry-truth (engine) ---
def _axial_force_mode_trajectory(mat, n=150):
    ana = DynamicStiffnessAnalyzer(M16, mat, 50e3)
    out = []
    for _ in range(n):
        ana.step_cycle(20e3, 0.0, 0.5)     # theta=0 (axial), sem delta_amp
        out.append(ana.state.F_0)
    return np.array(out)


def _shear_disp_mode_trajectory(mat, n=150):
    ana = DynamicStiffnessAnalyzer(M16, mat, 50e3)
    out = []
    for _ in range(n):
        ana.step_cycle(20e3, math.pi / 2, 0.5, delta_amp=0.5e-3)
        out.append(ana.state.F_0)
    return np.array(out)


def test_registry_truth_famp_fields_inert_in_pure_axial_force_mode():
    # predicado do ParameterRule (_transversal): NUNCA oferecido no axial.
    # Aqui pinamos isso contra o engine -- ligar os 4 campos nao muda nada.
    base = _axial_force_mode_trajectory(JointMaterial())
    ligado = _axial_force_mode_trajectory(
        JointMaterial(famp_couple_on=1.0, mu_eff_lo=0.5,
                     mu_eff_F0_ref=50e3, gross_ceiling_decay=0.5))
    assert np.array_equal(base, ligado)


def test_registry_truth_famp_couple_on_acts_under_shear_disp_mode():
    # contrapositiva: sob cisalhamento em disp-mode o mesmo flag MUDA a
    # curva -- o teste de inercia acima nao passa vacuamente.
    base = _shear_disp_mode_trajectory(JointMaterial())
    ligado = _shear_disp_mode_trajectory(JointMaterial(famp_couple_on=1.0))
    assert not np.array_equal(base, ligado)
