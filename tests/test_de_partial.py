"""dE_partial (spec 2026-07-08): energia de micro-slip do anel Cattaneo-Mindlin —
alimenta W_slip_acc (dano dispara no plato) + budget de energia. Default 0 = OFF."""
import numpy as np
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)


def _geom():
    return JointGeometry(A_s=84.3e-6, L_eff=12e-3, d_2=10.86e-3, pitch=1.5e-3,
                         r_bearing=9e-3, A_contact=117.6e-6)


def _run(kps, delta_mm, cD=0.0, Wc=0.0, kdmu=0.0, n=400):
    # c_bend baixo => partial slip (gross ~0): o regime do plato
    m = JointMaterial(emb_depth=5e-6, mu_thread=0.15, mu_bearing=0.15, c_bend=0.2,
                      k_tr_mode="bending", slip_regime_mode="cattaneo_mindlin",
                      slip_capacity_coeff=1.0, loose_torsion_mode="bolt_torsion",
                      eta_loose=15.0, loose_arrest_floor=0.08, k_partial_slip=kps,
                      c_D=cD, W_crit=Wc, dmg_onset_sharpness=6.0, k_dmg_wear=6.0,
                      k_dmg_mu=kdmu, W_ref=1e4)
    ana = DynamicStiffnessAnalyzer(_geom(), m, 50e3)
    for _ in range(n):
        ana.step_cycle(0.4 * 50e3, np.pi / 2, 12.0, delta_amp=delta_mm * 1e-3)
    return ana


def test_default_inert():
    assert JointMaterial().k_partial_slip == 0.0
    a, b = _run(0.0, 0.08), _run(0.0, 0.08)
    assert a.state.F_0 == b.state.F_0 and a.state.W_slip_acc == b.state.W_slip_acc


def test_accumulates_in_plateau():
    # regime partial (c_bend 0.2, delta pequeno): gross slip ~0 => W_slip_acc~0 sem a forma
    off = _run(0.0, 0.08); on = _run(0.5, 0.08)
    assert on.state.W_slip_acc > off.state.W_slip_acc + 100.0   # a forma alimenta o plato


def test_energy_only_no_direct_preload_drain():
    # SEM dano, dE_partial nao deve mudar F_0 (so energia); com dano ATIVO, dispara D
    off = _run(0.0, 0.08); on = _run(0.5, 0.08)
    assert abs(on.state.F_0 - off.state.F_0) < 1e-6        # energia-only sem dano
    assert on.energy.W_diss_wear > off.energy.W_diss_wear  # budget cresce


def test_triggers_damage_in_plateau():
    # a chave do §4.31: com dano+W_crit, a forma dispara D no plato (sem ela, D~0)
    W_on = _run(0.5, 0.08).state.W_slip_acc
    # cadeia de colapso completa: dE_partial -> D -> mu cai (k_dmg_mu) -> slip vira
    # gross -> wear runaway -> colapso abaixo do floor (a "falling F_V" do Bauer)
    on = _run(0.5, 0.08, cD=3.0, Wc=0.5 * W_on, kdmu=1.0)
    off = _run(0.0, 0.08, cD=3.0, Wc=0.5 * W_on, kdmu=1.0)
    # a claim central do §4.31: SEM a forma o dano nao acende no plato (D~0);
    # COM ela, D cresce (=> gatilho do joelho). O colapso completo D->mu->gross
    # e' questao de validacao no Bauer real (runaway precisa de N e F0 caindo).
    assert off.state.D < 1e-3                  # sem dE_partial: dano morto no plato
    assert on.state.D > 0.02                   # com dE_partial: dano acende
