# -*- coding: utf-8 -*-
"""F3 mu_bearing_schedule (prereg F3.2-CHU): input µ(N) medido, default-inerte.

Contratos: (a) schedule constante == constante mu_bearing (trajetória EXATA,
dano off); (b) interpolação honrada em mu_bearing_eff; (c) schedule BYPASSA a
modulação de dano; (d) default vazio usa o caminho antigo.
"""
import math

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    mu_bearing_eff)


def _run(mat, n=40):
    ana = DynamicStiffnessAnalyzer(JointGeometry(), mat, 30e3)
    for _ in range(n):
        ana.step_cycle(0.0, math.pi / 2, 5.0, delta_amp=0.4e-3)
    return [round(ana.state.F_0, 9), round(ana.state.delta_wear, 15)]


def test_schedule_constante_igual_constante():
    a = _run(JointMaterial(mu_bearing=0.15))
    b = _run(JointMaterial(mu_bearing=0.99,      # ignorado com schedule
                           mu_bearing_schedule=((0, 0.15), (1e6, 0.15))))
    assert a == b


def test_interpolacao_no_ciclo():
    mat = JointMaterial(mu_bearing_schedule=((0, 0.10), (100, 0.30)))
    st = SlowState(F_0=30e3, n_cycle=50)
    assert abs(mu_bearing_eff(st, mat) - 0.20) < 1e-12
    st.n_cycle = 1000                            # clamp na ponta
    assert abs(mu_bearing_eff(st, mat) - 0.30) < 1e-12


def test_schedule_bypassa_dano():
    mat = JointMaterial(k_dmg_mu=1.0,
                        mu_bearing_schedule=((0, 0.22), (10, 0.22)))
    st = SlowState(F_0=30e3, D=0.9, n_cycle=5)
    assert abs(mu_bearing_eff(st, mat) - 0.22) < 1e-12


def test_default_vazio_caminho_antigo():
    mat = JointMaterial(mu_bearing=0.15, k_dmg_mu=1.0)
    st = SlowState(F_0=30e3, D=0.5)
    assert abs(mu_bearing_eff(st, mat) - 0.075) < 1e-12
