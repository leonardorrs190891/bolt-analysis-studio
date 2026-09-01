"""Bookkeeping do viscoso em modo axial (spec 2026-07-07, roadmap #9/#27).

Em force-mode axial W_ext_per_cycle da' ~0 (sem slip transverso), entao o
amortecimento viscoso (Rayleigh) ficava sem contraparte em W_ext => o residual
de conservacao ficava ~ -W_visc (o achado -242..-12 J). A fonte externa do
viscoso (W_ext += W_visc) fecha o canal. Em transversal W_visc ~ cos^2(pi/2) ~ 0
=> disp-mode intocado."""
import numpy as np
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)


def _geom(grip_mm=30.0):
    return JointGeometry(A_s=84.3e-6, L_eff=grip_mm * 1e-3, d_2=10.86e-3,
                         pitch=1.75e-3, r_bearing=9e-3, A_contact=117.6e-6)


def _rel_resid(ana):
    e = ana.energy
    scale = max(abs(e.W_ext) + abs(e.U_released), abs(e.W_diss_total), 1.0)
    return abs(e.conservation_residual) / scale


def test_axial_force_mode_conservation_closes():
    geom = _geom()
    mat = JointMaterial(emb_depth=3.5e-6, mu_thread=0.15, mu_bearing=0.15)  # rayleigh default on
    ana = DynamicStiffnessAnalyzer(geom, mat, 18e3)
    for _ in range(5000):
        ana.step_cycle(10e3, 0.0, 30.0)                      # axial force-mode
    # viscoso agora tem FONTE externa => residual << W_visc (era ~ -W_visc, o leak).
    # O ~1.8% que resta e' a aproximacao plastica U_released vs W_emb/creep (#6),
    # canal separado — nao o viscoso.
    assert ana.energy.W_damp_visc > 0.0                      # viscoso ativo
    assert abs(ana.energy.conservation_residual) < 0.1 * ana.energy.W_damp_visc


def test_disp_mode_conservation_unaffected():
    geom = _geom()
    mat = JointMaterial(emb_depth=3.5e-6, mu_thread=0.15, mu_bearing=0.15)
    ana = DynamicStiffnessAnalyzer(geom, mat, 20e3)
    for _ in range(2000):
        ana.step_cycle(0.4 * 20e3, np.pi / 2, 1.0, delta_amp=0.5e-3)
    # W_visc ~ 0 em transversal => o termo adicionado nao muda o balanco
    assert _rel_resid(ana) < 1e-3
