# -*- coding: utf-8 -*-
"""Invariantes do gate de regime de amplitude dos relogios de ESTAGIO I.

PR-3 2026-08-01 (prereg specs/2026-08-01-s1-amp-gate-pr3-prereg.md, forma B
do N95 do LIU_2025): transicao regime-parcial -> gross-slip nos relogios de
bedding e creep-de-interface. Default OFF EXATO (dref=0) — G0 do prereg.
"""
import numpy as np

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, stage1_amp_gate)

GEOM = JointGeometry(A_s=157e-6, L_eff=0.05, d_2=14.7e-3, pitch=2.0e-3,
                     r_bearing=11e-3, A_contact=200e-6)
ON = dict(s1_amp_gate_dref=0.00055, s1_amp_gate_p=8.0,
          s1_amp_gate_floor=0.01)


def _run(mat, delta, n=300):
    ana = DynamicStiffnessAnalyzer(GEOM, mat, 60000.0)
    out = []
    for _ in range(n):
        snap = ana.step_cycle(F_amp=0.0, theta_load=np.pi / 2, freq=10.0,
                              delta_amp=delta)
        out.append(snap.F_0)
    return np.array(out)


def test_g0_default_off_bit_identico():
    # dref=0 (default) tem de ser BIT-identico ao engine sem os campos —
    # e' o G0 do prereg; regressao aqui invalida qualquer adocao.
    a = _run(JointMaterial(), 0.0004)
    b = _run(JointMaterial(s1_amp_gate_dref=0.0), 0.0004)
    assert np.array_equal(a, b)


def test_gate_forma_hill():
    m = JointMaterial(**ON)
    g_lo = stage1_amp_gate(m, 0.00025)
    g_mid = stage1_amp_gate(m, 0.00055)
    g_hi = stage1_amp_gate(m, 0.0008)
    assert g_lo < 0.02                      # sub-limiar: quase parado
    assert abs(g_mid - (0.01 + 0.99 * 0.5)) < 1e-9   # d=dref => meio caminho
    assert g_hi > 0.9                       # gross-slip: taxa ~plena
    assert stage1_amp_gate(m, None) == 1.0  # modo forca: inerte
    assert stage1_amp_gate(JointMaterial(), 0.00025) == 1.0  # OFF: inerte


def test_supressao_so_em_amplitude_baixa():
    lo = _run(JointMaterial(**ON), 0.00025)
    b_lo = _run(JointMaterial(), 0.00025)
    hi = _run(JointMaterial(**ON), 0.0008)
    b_hi = _run(JointMaterial(), 0.0008)
    perda = lambda v: 60000.0 - v[-1]
    assert perda(lo) < 0.5 * perda(b_lo)    # 0.25mm: estagio I suprimido
    assert perda(hi) > 0.95 * perda(b_hi)   # 0.80mm: praticamente intocado


def test_conservacao_com_gate_ligado():
    ana = DynamicStiffnessAnalyzer(GEOM, JointMaterial(**ON), 60000.0)
    for _ in range(200):
        ana.step_cycle(F_amp=0.0, theta_load=np.pi / 2, freq=10.0,
                       delta_amp=0.00025)
    # o gate multiplica d_delta ANTES de dF_0/dE derivarem dele — nao pode
    # abrir o balanco alem do residual fenomenologico usual do engine.
    assert abs(ana.energy.conservation_residual) < 1.0
