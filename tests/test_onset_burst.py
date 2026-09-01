# -*- coding: utf-8 -*-
"""Invariantes do BURST DE RUPTURA (`onset_burst_*`, 2026-08-21).

Liberacao da energia incubada quando o gate de onset (slip_onset_W) abre:
dreno exponencial em direcao ao alvo (1-frac)*F0_init, gateado pelo MESMO
Hill da incubacao — burst intenso que DESACELERA sozinho. Motivado pelas
DUAS fig14_long do LU_2024 (platô -> burst ate ~0,50-0,54 F0 -> cauda;
lu2024_fig14_burst_resultado.md). Default frac=0 (ou rate=0) = OFF EXATO.
"""
import math

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)

GEOM = JointGeometry(A_s=36.6e-6, L_eff=0.02, d_2=7.188e-3, pitch=1.25e-3,
                     r_bearing=6.5e-3, A_contact=90e-6)
# k pequeno + fe alto: o kernel da cauda quase nao drena na janela, para o
# baseline NAO colapsar a zero (senao os finais empatam em 0 e a monotonia
# do burst fica invisivel — foi o 1o setup deste arquivo, consertado).
BASE = dict(loose_rate_mode="graded_scrit", k_loose_graded=0.004,
            s_crit_loose=0.0, loose_amp_exp=0.0, loose_F_exp=3.0,
            loose_arrest_floor=0.0,
            slip_onset_W=150.0, slip_onset_sharpness=20.0,
            # sem estes zeros o EMB default de 30um (M16) drena 40% antes do
            # onset e mascara o burst — 2o conserto de setup deste arquivo
            emb_depth=1e-6, C_creep=0.0, K_archard=0.0, k_wear_spec=0.0)


def _run(mat, n=120, delta=1.0e-3, f0=10500.0):
    ana = DynamicStiffnessAnalyzer(GEOM, mat, f0)
    for _ in range(n):
        ana.step_cycle(F_amp=0.0, theta_load=math.pi / 2, freq=1.0,
                       delta_amp=delta)
    return ana


def test_default_off_bit_identico():
    a = _run(JointMaterial(**BASE))
    b = _run(JointMaterial(**BASE, onset_burst_frac=0.0,
                           onset_burst_rate=0.5))
    assert [s.F_0 for s in a.history] == [s.F_0 for s in b.history]


def test_rate_zero_off_exato():
    a = _run(JointMaterial(**BASE))
    b = _run(JointMaterial(**BASE, onset_burst_frac=0.45,
                           onset_burst_rate=0.0))
    assert [s.F_0 for s in a.history] == [s.F_0 for s in b.history]


def test_burst_age_so_pos_onset_e_respeita_o_alvo():
    # Pre-onset (gate ~0) as duas curvas coincidem; pos-onset o burst drena
    # mais rapido; e o burst NAO leva a junta abaixo do alvo por si (a cauda
    # do kernel continua, entao comparamos contra o alvo com folga).
    a = _run(JointMaterial(**BASE))
    b = _run(JointMaterial(**BASE, onset_burst_frac=0.45,
                           onset_burst_rate=0.3))
    ra = [s.F_0 / 10500.0 for s in a.history]
    rb = [s.F_0 / 10500.0 for s in b.history]
    # pre-onset identico a 0,5% (gate fechado)
    for x, y in zip(ra[:20], rb[:20]):
        assert abs(y - x) < 0.005, (x, y)
    # pos-onset o burst acelera a queda
    assert rb[-1] < ra[-1] - 0.02, (rb[-1], ra[-1])


def test_monotonia_no_frac():
    fins = []
    for fr in (0.2, 0.45, 0.7):
        b = _run(JointMaterial(**BASE, onset_burst_frac=fr,
                               onset_burst_rate=0.3))
        fins.append(b.state.F_0)
    assert fins[0] > fins[1] > fins[2], fins


def test_inerte_no_kernel_torque():
    base = dict(loose_arrest_floor=0.0, slip_onset_W=150.0)
    a = _run(JointMaterial(**base))
    b = _run(JointMaterial(**base, onset_burst_frac=0.45,
                           onset_burst_rate=0.3))
    assert [s.F_0 for s in a.history] == [s.F_0 for s in b.history]
