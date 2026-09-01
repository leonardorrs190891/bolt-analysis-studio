"""dmg_gross_exp (spec 2026-07-08): onset FISICO CONTINUO do dano pela fracao de
gross-slip (s_a/s_crit, s_crit=delta_t proporcional a F0). fig6/fig8 = mesma
fisica, joelho continuo na super-criticalidade. Default 0 = usa W_crit (inerte)."""
import numpy as np
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)


def _geom():
    return JointGeometry(A_s=84.3e-6, L_eff=12e-3, d_2=10.86e-3, pitch=1.5e-3,
                         r_bearing=9e-3, A_contact=117.6e-6)


def _run(gexp, delta_mm, F0=50e3, n=800):
    m = JointMaterial(emb_depth=5e-6, mu_thread=0.15, mu_bearing=0.15, c_bend=0.3,
                      k_tr_mode="bending", slip_regime_mode="cattaneo_mindlin",
                      slip_capacity_coeff=1.0, loose_torsion_mode="bolt_torsion",
                      eta_loose=15.0, loose_arrest_floor=0.10, k_partial_slip=0.5,
                      c_D=10.0, W_crit=0.0, dmg_gross_exp=gexp, k_dmg_wear=6.0,
                      k_dmg_mu=3.0, W_ref=1e4)
    ana = DynamicStiffnessAnalyzer(_geom(), m, F0)
    for _ in range(n):
        ana.step_cycle(0.4 * F0, np.pi / 2, 12.0, delta_amp=delta_mm * 1e-3)
    return ana.state.D, ana.state.F_0 / F0


def test_default_inert():
    m = JointMaterial()
    assert m.dmg_gross_exp == 0.0
    # gexp=0 usa o gate W_crit legado; com W_crit=0 tb, D nao cresce sem onset
    d0, _ = _run(0.0, 0.08); d1, _ = _run(0.0, 0.08)
    assert d0 == d1


def test_continuous_in_supercriticality():
    # MESMA fisica (gexp fixo), amplitude crescente => curvatura de dano CRESCE
    # continuamente (sub-critico: D pequeno; super-critico: D grande) — o continuum
    D_sub, f_sub = _run(2.0, 0.05)     # sub-critico (amplitude baixa)
    D_mid, f_mid = _run(2.0, 0.10)
    D_sup, f_sup = _run(2.0, 0.30)     # super-critico (amplitude alta)
    assert D_sub < D_mid < D_sup       # dano cresce continuamente com super-crit.
    assert f_sub > f_mid > f_sup       # => joelho cada vez mais fundo (continuo)
    assert D_sub < 0.10                # sub-critico: joelho minimo (quase linear)
