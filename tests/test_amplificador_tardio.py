# -*- coding: utf-8 -*-
"""Invariantes do amplificador tardio agnóstico de canal (`k_dmg_all`).

PR-3 2026-08-01 (prereg specs/2026-08-01-amplificador-tardio-pr3): a classe
"aceleração tardia" (7 fontes) não tinha mecanismo — todo gate Hill do engine
tem contradomínio (0,1] (só atrasa) e o único amplificador multiplicava o
wear, morto em 4 das 5 fontes. Este multiplica o TOTAL, então não precisa
saber qual canal domina.

NÃO adotado em fonte nenhuma (G2 do prereg falhou em 3/5): estes testes
protegem a INÉRCIA e a física da capacidade, não um ganho de meta.
"""
import numpy as np

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)

GEOM = JointGeometry(A_s=157e-6, L_eff=0.05, d_2=14.7e-3, pitch=2.0e-3,
                     r_bearing=11e-3, A_contact=200e-6)
DMG = dict(c_D=2.0, W_ref=1.0e4, k_dmg_mu=1.0, k_dmg_wear=4.0)


def _run(mat, n=300, delta=4e-4):
    ana = DynamicStiffnessAnalyzer(GEOM, mat, 60000.0)
    out = [ana.step_cycle(F_amp=0.0, theta_load=np.pi / 2, freq=10.0,
                          delta_amp=delta).F_0 for _ in range(n)]
    return np.array(out), ana


def test_default_off_e_bit_identico():
    """G0 do prereg: sem o campo, o engine tem de sair IGUAL — é o que
    permite a capacidade viver no main sem adoção."""
    a, _ = _run(JointMaterial(**DMG))
    b, _ = _run(JointMaterial(**DMG, k_dmg_all=0.0))
    assert np.array_equal(a, b)


def test_amplifica_a_perda_e_e_monotono():
    """Fator > 1 sobre o TOTAL: mais k ⇒ menos pré-carga no fim. É a
    propriedade que nenhum gate Hill do engine tem (todos são ≤ 1)."""
    base, _ = _run(JointMaterial(**DMG))
    m2, _ = _run(JointMaterial(**DMG, k_dmg_all=2.0))
    m8, _ = _run(JointMaterial(**DMG, k_dmg_all=8.0))
    assert m8[-1] < m2[-1] < base[-1]


def test_inerte_sem_o_acumulador():
    """Sem dano (`c_D=0` ⇒ D≡0) o amplificador não tem o que amplificar.
    É a razão MEDIDA de o G2 falhar em JCSR/LIU_2025 (D=0,0000 lá): o
    companheiro tem de estar vivo — a lição do canal de flanco, hoje."""
    a, _ = _run(JointMaterial())
    b, _ = _run(JointMaterial(k_dmg_all=8.0))
    assert np.array_equal(a, b)


def test_conservacao_nao_estoura():
    """G1: `dF_0` amplificado SEM amplificar `dE` — a perda extra fecha por
    `U_released`. Amplificar `dE` junto daria ~40 % de residual (medido em
    2026-06 no k_dmg_wear); aqui o residual fica na ordem do engine."""
    _, ana = _run(JointMaterial(**DMG, k_dmg_all=8.0))
    assert abs(ana.energy.conservation_residual) < 5.0


def test_decomposicao_continua_somando_o_total():
    """O report exige que os canais somem a perda total; o amplificador
    reescala `dF_0_by_mech` junto do total, senão a decomposição passaria a
    somar MENOS que a queda de F_0 (o gráfico empilhado mentiria)."""
    ana = DynamicStiffnessAnalyzer(GEOM, JointMaterial(**DMG, k_dmg_all=4.0),
                                   60000.0)
    for _ in range(200):
        antes = ana.state.F_0
        snap = ana.step_cycle(F_amp=0.0, theta_load=np.pi / 2, freq=10.0,
                              delta_amp=4e-4)
        queda = antes - snap.F_0
        soma = -sum(snap.dF_0_by_mech.values())
        # tolerância só para o piso F_0>=0 do último ciclo
        assert abs(soma - queda) < 1e-6 or snap.F_0 == 0.0
    assert soma > 0, "sem perda no fim, o teste não estaria medindo nada"


def test_interruptor_off_exato_sem_limiar():
    """`k_late_amp` sem `crash_trigger_frac` não tem interruptor — tem de ser
    OFF exato, não meio-ligado (a 1ª implementação poderia amplificar com g
    indefinido)."""
    a, _ = _run(JointMaterial())
    b, _ = _run(JointMaterial(k_late_amp=8.0))
    assert np.array_equal(a, b)


def test_interruptor_e_tardio_e_nao_gradual():
    """O ponto da emenda: a amplificação tem de ficar quase inerte cedo e
    subir tarde. Com frac=0,60 a razão g_final/g_inicial é ~56 (álgebra do
    Hill) — é o que distingue esta forma do `k_dmg_all·D`, que é gradual.

    Pinado porque foi um gate MAL ESCRITO que quase enterrou a variante: com
    frac=0,85 a razão é só 4,6 e o gate original (>50 % tarde, <10 % cedo)
    era infeasible por construção."""
    m = JointMaterial(crash_trigger_frac=0.60, crash_trigger_sharpness=8.0,
                      k_late_amp=1.0)
    ft = m.crash_trigger_frac ** m.crash_trigger_sharpness
    g = lambda r: ft / (ft + r ** m.crash_trigger_sharpness)
    assert g(1.0) < 0.02                      # cedo: praticamente inerte
    assert g(0.45) > 0.90                     # tarde: quase pleno
    assert g(0.45) / g(1.0) > 20              # a razão que o gradual não dá


def test_interruptor_amplifica_de_verdade():
    """Sinal certo: com o limiar ligado, mais `k_late_amp` ⇒ menos pré-carga
    no fim. (Não adotado: o gate de CLASSE falhou — ver
    `amplificador_interruptor_resultado.md`.)"""
    SW = dict(crash_trigger_frac=0.60, crash_trigger_sharpness=8.0)
    base, _ = _run(JointMaterial(**SW))
    k1, _ = _run(JointMaterial(**SW, k_late_amp=1.0))
    assert k1[-1] < base[-1]
