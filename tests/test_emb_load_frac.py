"""Assentamento proporcional a carga (emb_load_frac, falsificacao Lu fig20).

delta_target += emb_load_frac*F0_init/k_b => fracao de queda rapida CONSTANTE
(= emb_load_frac) em qualquer F0 — o que o sweep fig20 mostra (~0.55 F0-flat).
Default 0 = bit-identical."""
import numpy as np
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)


def _geom():
    return JointGeometry(A_s=84.3e-6, L_eff=30e-3, d_2=10.86e-3, pitch=1.75e-3,
                         r_bearing=9e-3, A_contact=117.6e-6)


def _run(F0, frac, n=300, emb=0.0):
    m = JointMaterial(emb_depth=emb, N_emb=15.0, emb_load_frac=frac,
                      C_creep=0.0, mu_thread=0.15, mu_bearing=0.15)
    ana = DynamicStiffnessAnalyzer(_geom(), m, F0)
    for _ in range(n):
        ana.step_cycle(0.0, np.pi / 2, 10.0)   # sem slip: so o assentamento
    return ana.state.F_0 / F0


def test_default_inert():
    m = JointMaterial()
    assert m.emb_load_frac == 0.0
    assert abs(_run(10e3, 0.0) - 1.0) < 1e-12   # emb=0, frac=0 => nada cai


def test_fraction_is_f0_flat():
    # fracao de queda IGUAL em F0 7x diferentes (a assinatura do fig20)
    r_lo, r_hi = _run(2.1e3, 0.5), _run(15e3, 0.5)
    assert abs((1 - r_lo) - (1 - r_hi)) < 1e-9
    assert abs((1 - r_lo) - 0.5) < 1e-3          # assintota = emb_load_frac


def test_composes_with_absolute_depth():
    g = _geom()
    r = _run(10e3, 0.3, emb=5e-6)
    expected = 0.3 + g.k_b * 5e-6 / 10e3         # soma dos dois reservatorios
    assert abs((1 - r) - expected) < 1e-3
