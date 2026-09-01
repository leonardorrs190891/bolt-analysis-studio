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


def test_damage_defaults_inactive():
    mat = JointMaterial()
    assert mat.c_D == 0.0
    assert mat.k_dmg_mu == 0.0
    # Estagio B: k_damage_scale removido (foldado em c_D); dano OFF por c_D=0.
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


def test_mu_eff_inert_when_no_coupling():
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        mu_bearing_eff, SlowState)
    mat = JointMaterial()                 # k_dmg_mu=0
    s = SlowState(F_0=50_000.0, F_0_init=50_000.0, D=0.7)
    # sem coupling, dano nao afeta atrito (backward-compat)
    assert mu_bearing_eff(s, mat) == mat.mu_bearing


def test_mu_eff_reduces_with_damage():
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        mu_bearing_eff, F_slip_transverse, SlowState)
    mat = JointMaterial(k_dmg_mu=1.0)
    s = SlowState(F_0=50_000.0, F_0_init=50_000.0, D=0.5)
    assert abs(mu_bearing_eff(s, mat) - 0.5 * mat.mu_bearing) < 1e-12
    # F_slip cai junto
    s0 = SlowState(F_0=50_000.0, F_0_init=50_000.0, D=0.0)
    assert F_slip_transverse(s, mat) < F_slip_transverse(s0, mat)


def test_mu_eff_clamps_nonnegative():
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        mu_bearing_eff, SlowState)
    mat = JointMaterial(k_dmg_mu=2.0)
    s = SlowState(F_0=50_000.0, F_0_init=50_000.0, D=0.9)  # 1-1.8 < 0
    assert mu_bearing_eff(s, mat) == 0.0


def test_damage_grows_bounded_monotonic():
    mat = JointMaterial(c_D=1.0, W_ref=1.0e4, k_dmg_mu=1.0)
    ana = _analyzer(mat=mat, initial_damage=0.3)
    Ds = [ana.state.D]
    for _ in range(500):
        snap = ana.step_cycle(20_000.0, np.pi / 2, 0.5, delta_amp=0.5e-3)
        Ds.append(snap.D)
    assert all(0.0 <= d <= 1.0 for d in Ds)                  # limitado
    assert all(b >= a - 1e-12 for a, b in zip(Ds, Ds[1:]))   # monotonico
    assert Ds[-1] > 0.3                                       # cresceu


def test_damage_accelerates_loss():
    # reaperto-like (D_init>0, dano ativo) perde mais que nova-like (sem dano)
    mat_dmg = JointMaterial(c_D=1.0, W_ref=1.0e4, k_dmg_mu=1.0)
    ana_dmg = _analyzer(mat=mat_dmg, initial_damage=0.3)
    ana_nova = _analyzer()  # dano inativo
    for _ in range(800):
        ana_dmg.step_cycle(20_000.0, np.pi / 2, 0.5, delta_amp=0.5e-3)
        ana_nova.step_cycle(20_000.0, np.pi / 2, 0.5, delta_amp=0.5e-3)
    assert ana_dmg.state.F_0 < ana_nova.state.F_0


def test_wear_amplified_by_damage():
    # k_dmg_wear amplifica o material removido => mais perda de preload,
    # com conservacao mantida (dE = trabalho de atrito real, perda extra
    # contabilizada via U_released).
    base = JointMaterial(c_D=1.0, W_ref=1.0e4, k_dmg_mu=0.0, k_dmg_wear=0.0)
    amp = JointMaterial(c_D=1.0, W_ref=1.0e4, k_dmg_mu=0.0, k_dmg_wear=2.0)
    ana_b = _analyzer(mat=base, initial_damage=0.3)
    ana_a = _analyzer(mat=amp, initial_damage=0.3)
    for _ in range(800):
        ana_b.step_cycle(20_000.0, np.pi / 2, 0.5, delta_amp=0.5e-3)
        ana_a.step_cycle(20_000.0, np.pi / 2, 0.5, delta_amp=0.5e-3)
    assert ana_a.state.F_0 < ana_b.state.F_0          # amplificou a perda
    e = ana_a.energy
    total = abs(e.W_ext) + abs(e.U_released) + abs(e.W_diss_total) + 1.0
    assert abs(e.conservation_residual) / total < 1e-2  # conservacao mantida


def test_damage_defaults_inactive_wear():
    assert JointMaterial().k_dmg_wear == 0.0


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
