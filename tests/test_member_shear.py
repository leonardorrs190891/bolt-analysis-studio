"""Cisalhamento do membro em serie com k_tr (k_member_shear, item 2 / HDPE).

Membro complacente absorve o curso imposto (delta_m = F*t/(G*A)) — menos slip
na interface. Default 0 = bit-identical."""
import numpy as np
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    JointGeometry, JointMaterial, SlowState, k_tr_transverse,
    resolve_transverse_slip)


def _geom():
    return JointGeometry(A_s=84.3e-6, L_eff=30e-3, d_2=10.86e-3, pitch=1.75e-3,
                         r_bearing=9e-3, A_contact=117.6e-6)


def test_default_inert():
    g = _geom()
    m0 = JointMaterial(k_tr_mode="bending", c_bend=0.2)
    m1 = JointMaterial(k_tr_mode="bending", c_bend=0.2, k_member_shear=0.0)
    assert m1.k_member_shear == 0.0
    assert k_tr_transverse(g, m0) == k_tr_transverse(g, m1)


def test_series_reduces_stiffness():
    g = _geom()
    m = JointMaterial(k_tr_mode="bending", c_bend=0.2)
    k0 = k_tr_transverse(g, m)
    ms = JointMaterial(k_tr_mode="bending", c_bend=0.2, k_member_shear=k0)
    assert abs(k_tr_transverse(g, ms) - k0 / 2.0) < 1e-9   # serie igual => metade


def test_softer_member_less_slip():
    g = _geom()
    st = SlowState(F_0=10e3, F_0_init=10e3)
    def slip(kms):
        m = JointMaterial(k_tr_mode="bending", c_bend=0.2, mu_bearing=0.15,
                          k_member_shear=kms)
        return resolve_transverse_slip(st, m, 4e3, np.pi / 2, 4.0e-3, geom=g)
    s_stiff, s_soft = slip(0.0), slip(8e5)
    assert 0.0 < s_soft < s_stiff  # membro macio absorve curso => menos slip
    # espessura: k=G*A/t — mais espesso (k menor) => menos slip ainda
    assert slip(6e5) < slip(1.2e6)
