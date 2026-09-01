"""member_loss_eta (sec4.25): dissipacao viscoelastica do membro — SO energia,
preload bit-identico. Default 0 = OFF exato."""
import numpy as np
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)


def _run(eta, n=50):
    g = JointGeometry(A_s=84.3e-6, L_eff=29e-3, d_2=10.86e-3, pitch=1.75e-3,
                      r_bearing=9e-3, A_contact=117.6e-6)
    m = JointMaterial(emb_depth=2e-6, mu_thread=0.2, mu_bearing=0.2,
                      k_j_init=2e7, k_member_shear=1e7, member_loss_eta=eta,
                      k_tr_mode="bending", c_bend=4.0)
    ana = DynamicStiffnessAnalyzer(g, m, 10e3)
    for _ in range(n):
        ana.step_cycle(2.6e3, np.pi / 2, 1.0, delta_amp=0.5e-3)
    return ana.state.F_0, ana.energy.W_damp_visc, ana.energy.conservation_residual


def test_default_inert():
    assert JointMaterial().member_loss_eta == 0.0
    f0, w0, _ = _run(0.0)
    f1, w1, _ = _run(0.0)
    assert f0 == f1 and w0 == w1


def test_energy_only_preload_identical():
    f_off, w_off, res_off = _run(0.0)
    f_on, w_on, res_on = _run(3.0)
    assert f_on == f_off                      # preload bit-identico
    assert w_on > w_off + 1.0                 # dissipacao do membro contabilizada
    # a forma nao ADICIONA residual (W_ext supre o W_m simetricamente);
    # o residual base e' de outros canais (pre-existente nesta config)
    assert abs(res_on - res_off) < 1e-9
