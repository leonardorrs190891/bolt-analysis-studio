# -*- coding: utf-8 -*-
"""Invariantes do GATE PROPRIO do burst (`onset_burst_W`, 2026-08-21).

Anatomia medida na `liu2025_M16_amp0p8` (liu2025_par_de_taxas_opostas.md §6):
os 3 gates de estado existentes sao monotonicos E COMPARTILHADOS entre
canais — um burst gateado pelo `g` do slip_onset so abre onde o WEAR tambem
abre. `onset_burst_W > 0` troca o `g` compartilhado por um Hill proprio
sobre o MESMO `W_slip_acc` (mesmo sharpness): desacopla o limiar de ADESAO
(burst) do limiar de ABRASAO (wear). Default 0.0 = usa `g` = BIT-IDENTICO
a adocao da fig14 do LU.
"""
import math

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)

GEOM = JointGeometry(A_s=36.6e-6, L_eff=0.02, d_2=7.188e-3, pitch=1.25e-3,
                     r_bearing=6.5e-3, A_contact=90e-6)
# mesmo setup validado do test_onset_burst (2 consertos ja registrados la)
BASE = dict(loose_rate_mode="graded_scrit", k_loose_graded=0.004,
            s_crit_loose=0.0, loose_amp_exp=0.0, loose_F_exp=3.0,
            loose_arrest_floor=0.0,
            slip_onset_W=150.0, slip_onset_sharpness=20.0,
            emb_depth=1e-6, C_creep=0.0, K_archard=0.0, k_wear_spec=0.0)
BURST = dict(onset_burst_frac=0.45, onset_burst_rate=0.3)


def _run(mat, n=120, delta=1.0e-3, f0=10500.0):
    ana = DynamicStiffnessAnalyzer(GEOM, mat, f0)
    for _ in range(n):
        ana.step_cycle(F_amp=0.0, theta_load=math.pi / 2, freq=1.0,
                       delta_amp=delta)
    return ana


def test_zero_usa_g_compartilhado_bit_identico():
    # onset_burst_W=0.0 explicito == campo ausente (o default): a adocao da
    # fig14 do LU nao pode mudar nem um bit.
    a = _run(JointMaterial(**BASE, **BURST))
    b = _run(JointMaterial(**BASE, **BURST, onset_burst_W=0.0))
    assert [s.F_0 for s in a.history] == [s.F_0 for s in b.history]


def test_gate_proprio_abre_antes_do_compartilhado():
    # W_burst << slip_onset_W: o burst age ANTES do gate compartilhado
    # abrir — e' o desacoplamento que motivou o campo. Medimos no ciclo em
    # que o compartilhado ainda esta fechado (W_acc < slip_onset_W/2).
    a = _run(JointMaterial(**BASE, **BURST))                    # g compartilhado
    b = _run(JointMaterial(**BASE, **BURST, onset_burst_W=30.0))  # proprio, cedo
    ra = [s.F_0 for s in a.history]
    rb = [s.F_0 for s in b.history]
    # em algum prefixo (pre-onset compartilhado) o gate proprio ja drenou
    meio = len(ra) // 3
    assert min(rb[:meio]) < min(ra[:meio]) - 1.0, (
        "o gate proprio (30 J) deveria drenar antes do compartilhado "
        "(150 J): %.1f vs %.1f" % (min(rb[:meio]), min(ra[:meio])))


def test_gate_proprio_nao_afeta_wear():
    # O desacoplamento e' a claim central: mudar onset_burst_W NAO pode
    # mover o canal de WEAR (que segue gateado pelo `g` compartilhado).
    mat_a = JointMaterial(**{**BASE, "K_archard": 2e-5}, **BURST)
    mat_b = JointMaterial(**{**BASE, "K_archard": 2e-5}, **BURST,
                          onset_burst_W=30.0)
    a = _run(mat_a)
    b = _run(mat_b)
    wa = a.state.delta_wear
    wb = b.state.delta_wear
    # o F_0 diverge (o burst drena antes) => o wear NAO e' bit-identico
    # (depende de F_0), mas o GATE dele nao mudou: o wear de b nao pode
    # EXCEDER o de a alem do efeito de F_0 menor (wear cai com F_0) —
    # assert direcional sobre o acumulado.
    assert wb <= wa * 1.001, (
        "wear final com gate proprio %.3e > sem %.3e — o gate proprio "
        "vazou para o canal de wear" % (wb, wa))


def test_pool_esgota_o_dreno_para():
    # Sino: com o gate proprio aberto cedo, o dreno desacelera sozinho ao
    # chegar ao alvo (1-frac)*F0 — a taxa por ciclo no fim e' uma fracao
    # da taxa no pico do burst.
    b = _run(JointMaterial(**BASE, **BURST, onset_burst_W=30.0), n=200)
    r = [s.F_0 for s in b.history]
    dr = [r[i] - r[i + 1] for i in range(len(r) - 1)]
    pico = max(dr[:100])
    cauda = max(dr[-20:])
    assert cauda < pico * 0.5, (
        "o dreno nao desacelerou: pico %.2f, cauda %.2f" % (pico, cauda))
