# -*- coding: utf-8 -*-
"""L1 v2 — rota TRANSVERSAL do canal de flanco (F4, 2026-07-22).

Contratos: (1) switch OFF => sim transversal BIT-IDENTICA mesmo com o canal
de flanco carregado (k/s_crit engajados); (2) switch ON em disp-mode =>
perda adicional (F_0 cai mais) e conservacao de energia intacta; (3) rota
inerte em force-mode axial (delta_amp None) — o caminho axial NAO le o
switch; (4) nucleo compartilhado: flank_wear_axial_term == composicao
flank_wear_from_slip(s_th=F_ax/k_b) EXATA (extracao bit-identica);
(5) registry: switch declarado, fittable=False, regime transversal.
"""
import numpy as np

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    flank_wear_axial_term, flank_wear_from_slip)


def _run_transversal(flank_tr_on, n_cycles=400, k=1e-13, s_crit=0.0,
                     quiet=False):
    geom = JointGeometry()
    extra = {}
    if quiet:
        # silencia os DEMAIS mecanismos (contrato unitario: so a rota de
        # flanco atua) — os defaults M16-âncora interna colapsam F_0->0 em <400 ciclos
        # neste setup transversal (mesma patologia diagnosticada nos R5),
        # o que mataria a comparacao 0<0.
        extra = dict(emb_depth=0.0, C_creep=0.0, K_archard=0.0,
                     tr_loose_gain=0.0)
    mat = JointMaterial(flank_wear_on=1.0, k_wear_flank=k,
                        flank_amp_exp=1.5, flank_s_crit=s_crit,
                        flank_transverse_on=flank_tr_on, **extra)
    ana = DynamicStiffnessAnalyzer(geom, mat, 20e3)
    out = [1.0]
    for _ in range(n_cycles):
        ana.step_cycle(8e3, np.pi / 2, 5.0, delta_amp=0.2e-3)
        out.append(max(ana.state.F_0, 0.0) / 20e3)
    return np.array(out), ana


def test_switch_off_bit_identico_com_canal_carregado():
    base, _ = _run_transversal(0.0)
    # flank_wear_on=1 + k/s_crit carregados, mas rota transversal OFF:
    # nada pode mudar vs o mesmo run (o canal axial nao dispara em disp-mode)
    again, _ = _run_transversal(0.0, s_crit=1e-5)
    assert np.array_equal(base, again)


def test_switch_on_perde_mais_preload_e_conserva_energia():
    base, _ = _run_transversal(0.0, quiet=True)
    com, ana = _run_transversal(1.0, quiet=True)
    assert np.all(base == 1.0)                      # quiet: nada mais perde
    assert com[-1] < base[-1]                       # rota ativa perde
    assert ana.state.delta_thread_fret > 0.0
    # conservacao: residual pequeno relativo ao trabalho externo
    res = abs(ana.energy.conservation_residual)
    W = max(abs(ana.energy.W_ext), 1.0)
    assert res / W < 1e-6


def test_scrit_acima_do_slip_zera_a_rota():
    # slip transversal resolvido ~ delta - delta_t; com s_crit gigante a
    # rota liga mas d_w=0 => preload identico ao switch OFF
    base, _ = _run_transversal(0.0)
    com, _ = _run_transversal(1.0, s_crit=1.0)      # 1 m >> qualquer slip
    assert np.array_equal(base, com)


def test_axial_force_mode_nao_le_o_switch():
    geom = JointGeometry()

    def _axial(flank_tr_on):
        mat = JointMaterial(flank_wear_on=1.0, k_wear_flank=1e-13,
                            flank_amp_exp=1.5,
                            flank_transverse_on=flank_tr_on)
        ana = DynamicStiffnessAnalyzer(geom, mat, 18e3)
        for _ in range(300):
            ana.step_cycle(10e3, 0.0, 30.0)         # axial, force-mode
        return ana.state.F_0

    assert _axial(0.0) == _axial(1.0)               # bit-identico


def test_nucleo_compartilhado_composicao_exata():
    geom = JointGeometry()
    mat = JointMaterial(flank_wear_on=1.0, k_wear_flank=1e-13,
                        flank_amp_exp=1.5, flank_s_crit=5e-6)
    st = SlowState(F_0=18e3)
    F_amp, theta, freq = 10e3, 0.0, 30.0
    F_ax = F_amp * abs(np.cos(theta))
    s_th = F_ax / max(geom.k_b, 1.0)
    assert (flank_wear_axial_term(st, geom, mat, F_amp, theta, freq)
            == flank_wear_from_slip(st, geom, mat, s_th, freq))


def test_registry_switch_nao_fitavel_transversal():
    from bolt_analysis_studio.calibration.parameter_registry import (
        PARAMETER_REGISTRY)
    regras = {r.name: r for r in PARAMETER_REGISTRY}
    assert "flank_transverse_on" in regras
    assert regras["flank_transverse_on"].fittable is False
