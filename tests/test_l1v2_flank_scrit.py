# -*- coding: utf-8 -*-
"""L1 v2 candidato (c) — flank_s_crit (F4, prereg B1-v3 2026-07-22).

Contratos: (1) s_crit=0 => d_w BIT-IDENTICO ao v1 e dE inalterado;
(2) s_crit >= s_th => d_w=0 (stick/shakedown) mas dE segue real (>0);
(3) resposta ao A_F fica mais ingreme perto do limiar (razao de ganhos
maior que a do power-law puro); (4) regra do registry existe e e' fitavel
no regime axial-forca.
"""
import math

import numpy as np

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    JointGeometry, JointMaterial, SlowState, flank_wear_axial_term)


def _term(F_amp, s_crit, exp=1.5, k=1e-13):
    geom = JointGeometry()
    mat = JointMaterial(flank_wear_on=1.0, k_wear_flank=k,
                        flank_amp_exp=exp, flank_s_crit=s_crit)
    st = SlowState(F_0=20e3)
    return flank_wear_axial_term(st, geom, mat, F_amp, 0.0, 30.0)


def test_scrit_zero_bit_identico_v1():
    geom = JointGeometry()
    st = SlowState(F_0=20e3)
    F_amp = 10e3
    d_w, dE = _term(F_amp, 0.0)
    s_th = F_amp / geom.k_b
    p = st.F_0 / geom.A_s
    assert d_w == 1e-13 * p * (2.0 * s_th) ** 1.5      # formula v1 exata
    assert dE == 0.15 * st.F_0 * 2.0 * s_th


def test_scrit_acima_do_slip_zera_wear_mas_nao_dE():
    geom = JointGeometry()
    s_th = 10e3 / geom.k_b
    d_w, dE = _term(10e3, s_crit=2.0 * s_th)
    assert d_w == 0.0
    assert dE > 0.0                                     # atrito real continua


def test_limiar_deixa_resposta_mais_ingreme():
    geom = JointGeometry()
    s_mid = 10e3 / geom.k_b
    s_crit = 0.75 * s_mid
    razao_v1 = _term(12.5e3, 0.0)[0] / _term(7.5e3, 0.0)[0]
    razao_v2 = _term(12.5e3, s_crit)[0] / max(_term(7.5e3, s_crit)[0], 1e-300)
    assert razao_v2 > 10 * razao_v1                     # ganho de slope brutal


def test_registry_regra_fitavel_axial():
    from bolt_analysis_studio.calibration.parameter_registry import (
        PARAMETER_REGISTRY)
    regras = {r.name: r for r in PARAMETER_REGISTRY}
    assert "flank_s_crit" in regras
    assert regras["flank_s_crit"].fittable is True
