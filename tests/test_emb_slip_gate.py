"""emb_slip_gate (sec4.29): bedding fracional exige escorregamento (Jiang
porca-colada). Sub-limiar => so profundidade estatica. Default 0 = bit-identical."""
import numpy as np
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)


def _run(gate, delta_mm, n=100):
    g = JointGeometry(A_s=36.6e-6, L_eff=20e-3, d_2=7.19e-3, pitch=1.25e-3,
                      r_bearing=6e-3, A_contact=80e-6)
    m = JointMaterial(emb_depth=0.0, emb_load_frac=0.5, N_emb=5.0,
                      emb_slip_gate=gate, C_creep=0.0, mu_thread=0.15,
                      mu_bearing=0.15, k_tr_mode="bending", c_bend=5.0,
                      delta_free=0.28e-3)
    ana = DynamicStiffnessAnalyzer(g, m, 8e3)
    for _ in range(n):
        ana.step_cycle(0.4 * 8e3, np.pi / 2, 10.0, delta_amp=delta_mm * 1e-3)
    return ana.state.F_0 / 8e3


def test_default_inert():
    assert JointMaterial().emb_slip_gate == 0.0
    assert _run(0.0, 0.5) == _run(0.0, 0.5)


def test_subthreshold_beds_less():
    # sub-limiar (0.25mm < delta_free 0.28) NAO consome o reservatorio fracional
    r_sub_off, r_sub_on = _run(0.0, 0.25), _run(1.0, 0.25)
    assert r_sub_on > r_sub_off + 0.2       # gate poupa o sub-limiar
    # acima do limiar o gate deixa passar (slip grande => frac ~1)
    r_hi_off, r_hi_on = _run(0.0, 2.0), _run(1.0, 2.0)
    assert abs(r_hi_on - r_hi_off) < 0.10
