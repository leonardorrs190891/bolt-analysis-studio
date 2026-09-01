"""Task 8 (plano L1-L7, fatia 5): L7 — sanity check de energia de remoção +
C2 — residual viscoso axial.

C2: em modo FORÇA axial (theta~0), o amortecimento viscoso de Rayleigh
(`W_damp_visc`) não tinha contraparte em `W_ext` (`W_ext_per_cycle` dá ~0
sem slip transverso) — o residual de conservação ficava ~ -W_damp_visc
(achado histórico documentado no CLAUDE.md: -242.8 a -11.7 J). A correção
(sourcing do viscoso em `W_ext`, ver `EnergyBudget` docstring em
`dynamic_stiffness_analyzer.py`) já estava mesclada à história do repo
(commit "axial viscous energy source", Wave 2) antes desta fatia começar —
os testes (i)/(ii) abaixo TRAVAM esse resultado dentro do pacote de testes
desta fatia (Task 8), como pede o brief, e cobrem a garantia extra de que o
bookkeeping novo (V_wear_removed/E_wear_removal) não reabre o canal.

L7: `EnergyBudget.removal_energy_check()` — ver docstring do método. Testes
(iii)/(iv) cobrem o caso com wear ativo (implied numérico + bound sempre
presente) e sem wear (implied=None, bound ainda presente).
"""
import numpy as np
import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, EnergyBudget, JointGeometry, JointMaterial)


def _geom():
    return JointGeometry(A_s=84.3e-6, L_eff=30e-3, d_2=10.86e-3,
                         pitch=1.75e-3, r_bearing=9e-3, A_contact=117.6e-6)


def _run_axial_force(mat, n=5000, F0=18e3, F_amp=10e3, freq=30.0):
    """Harness axial força-controlada (theta=0, sem delta_amp) — o modo
    historicamente com o residual viscoso órfão (-242..-12 J antes da fonte
    em W_ext). Estruturalmente sem slip transverso (sin(0)=0) => WearLoss
    fica inerte aqui independente de k_wear_spec/K_archard — útil também
    para o caso 'sem wear' (iv), sem precisar zerar nenhum tuner à parte."""
    ana = DynamicStiffnessAnalyzer(_geom(), mat, F0)
    for _ in range(n):
        ana.step_cycle(F_amp, 0.0, freq)
    return ana


def _run_transverse(mat, n=5000, F0=50e3, frac=0.2, delta_amp=0.3e-3,
                    freq=0.5):
    """Harness transverso deslocamento-controlado (Junker-like), theta=pi/2
    — o único modo em que WearLoss (bearing) fica ativo por default."""
    ana = DynamicStiffnessAnalyzer(_geom(), mat, F0)
    for _ in range(n):
        ana.step_cycle(frac * F0, np.pi / 2, freq, delta_amp=delta_amp)
    return ana


# ---------------------------------------------------------------------------
# C2 — residual viscoso axial
# ---------------------------------------------------------------------------

def test_axial_force_mode_residual_near_zero():
    """(i) Era -242..-12 J (viscoso órfão de W_ext); com a fonte já mesclada,
    < 1.0 J mesmo em modo força axial puro com JointMaterial() default
    (rayleigh_alpha/beta > 0 por default => viscoso realmente ativo)."""
    m = JointMaterial()
    an = _run_axial_force(m, n=5000)
    assert an.energy.W_damp_visc > 0.0
    assert abs(an.energy.conservation_residual) < 1.0


def test_l7_fields_do_not_perturb_conservation_formula():
    """(ii) 'conservação transversal (e de qualquer regime) inalterada':
    prova ALGÉBRICA, não um número congelado — V_wear_removed/E_wear_removal
    (L7, Task 8) são campos ADITIVOS/observacionais que `W_diss_total` e
    `conservation_residual` NÃO referenciam. Mesmos 10 campos legados =>
    mesmo residual, para QUALQUER valor dos 2 campos novos (não só para o
    cenário testado em test_transverse_conservation_still_closes — isto vale
    por construção)."""
    legacy = dict(W_ext=12.3, U_stored=4.0, U_stored_init=9.0,
                 W_damp_visc=1.0, W_diss_emb=0.5, W_diss_creep=0.2,
                 W_diss_wear=0.3, W_diss_loose=0.1, W_diss_friction_y=0.4,
                 W_diss_fracture=0.05)
    e_untouched = EnergyBudget(**legacy)
    e_with_l7 = EnergyBudget(**legacy, V_wear_removed=5e-11, E_wear_removal=99.0)
    assert e_with_l7.W_diss_total == e_untouched.W_diss_total
    assert e_with_l7.conservation_residual == e_untouched.conservation_residual


def test_transverse_conservation_still_closes():
    """(ii cont.) Confirmação empírica end-to-end (mesmo padrão de
    tests/test_axial_viscous_conservation.py::test_disp_mode_conservation_unaffected):
    o residual transversal continua fechando — nem o canal viscoso (~cos²(pi/2)~0
    lá) nem o bookkeeping aditivo de volume/energia de wear (Task 8, aqui)
    abrem o residual em disp-mode."""
    m = JointMaterial(k_wear_spec=8.34e-15)
    an = _run_transverse(m, n=5000)
    e = an.energy
    scale = max(abs(e.W_ext) + abs(e.U_released), abs(e.W_diss_total), 1.0)
    assert abs(e.conservation_residual) / scale < 1e-2


# ---------------------------------------------------------------------------
# L7 — removal_energy_check()
# ---------------------------------------------------------------------------

def test_removal_energy_check_reports_bound():
    """(iii) Wear rodou (k_wear_spec>0, transverso) -> implied numérico +
    bound da literatura sempre presente (lo<hi, unidade J/mm^3)."""
    m = JointMaterial(k_wear_spec=8.34e-15)
    an = _run_transverse(m, n=5000)
    chk = an.energy.removal_energy_check()
    assert "implied_J_per_mm3" in chk and chk["bound"]["lo"] < chk["bound"]["hi"]
    assert chk["implied_J_per_mm3"] is not None
    assert chk["in_bound"] in (True, False)
    assert chk["bound"]["unit"] == "J/mm^3"


def test_removal_energy_check_matches_archard_ratio_analytically():
    """Correção direta (não só 'não crashou'): com todos os gates inertes
    (defaults — slip_onset_W=0, W_conf_ref=0, k_partial_slip=0, k_dmg_wear=0,
    k_wear_running<=1), implied = E_wear_removal/V_wear_removed[mm^3] deve
    reduzir analiticamente a mu_bearing/k_wear_spec/1e9: por ciclo,
    d_wear = k_wear_spec*F*s/A_contact (Archard) e V = d_wear*A_contact =
    k_wear_spec*F*s — A_contact CANCELA (volume Archard não depende da área
    nominal, só a conversão depth<->volume intermediária usa); dE = mu*F*s
    (mesmos F,s) => dE/V = mu/k_wear_spec, independente de F0/amplitude/n."""
    k_wear_spec = 8.34e-15
    m = JointMaterial(k_wear_spec=k_wear_spec)
    an = _run_transverse(m, n=5000)
    chk = an.energy.removal_energy_check()
    expected = (m.mu_bearing / k_wear_spec) / 1e9
    assert chk["implied_J_per_mm3"] == pytest.approx(expected, rel=1e-9)


def test_removal_energy_check_none_without_wear():
    """(iv) Sem wear (modo axial puro: WearLoss estruturalmente inerte sem
    slip transverso; canais de flanco de ThreadFrettingLoss OFF por default)
    -> implied=None, in_bound=None; bound sempre presente (referência da
    literatura, independe de a corrida ter removido volume)."""
    m = JointMaterial()
    an = _run_axial_force(m, n=5000)
    assert an.energy.V_wear_removed == 0.0
    chk = an.energy.removal_energy_check()
    assert chk["implied_J_per_mm3"] is None
    assert chk["in_bound"] is None
    assert chk["bound"]["lo"] < chk["bound"]["hi"]
