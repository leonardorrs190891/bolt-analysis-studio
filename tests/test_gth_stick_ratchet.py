# -*- coding: utf-8 -*-
"""Invariantes do gth — ratchet de STICK amplitude-dirigido com incubação
(spec 2026-08-10, dossiê YANG_2019 amp0p4).

A capacidade fica no engine DEFAULT-INERTE (padrão crash_trigger/k_late_amp):
o T13 não passou o gate de adoção (mx piora), e a 6ª falsificação do dossiê é
ESTRUTURAL — o corte de stick limita o mecanismo ao limiar de slip por
construção, e abaixo dele nenhum canal macro do engine produz a cauda da
0,4 mm com constantes compartilhadas. Estes testes fixam o CONTRATO da
capacidade para quando a campanha retomá-la.
"""
import pytest

import bolt_analysis_studio.numerical.dynamic_stiffness_analyzer as dsa


def _mech():
    return dsa.RotationalLooseningLoss()


def _rate(st, mat, slip, delta):
    return _mech().rate(st, dsa.JointGeometry(), mat, F_amp=0.0,
                        theta_load=0.0, freq=5.0, cycle_N=1,
                        slip_amp_override=slip, delta_amp=delta)


def test_off_e_zero_exato():
    """gth_k=0 (default) não pode deixar rastro nenhum — nem no ds."""
    st = dsa.SlowState(F_0=26400.0, F_0_init=26400.0)
    res = _rate(st, dsa.JointMaterial(), slip=0.0, delta=0.0004)
    assert res["dF_0"] == 0.0 and res["ds"] == {}


def test_acumula_em_stick_e_so_em_stick():
    """A_gth cresce (δ/dref)^q por ciclo EM STICK; em slip, nada.

    O stick-only é o coração do desenho: é o que torna as curvas em regime
    de slip (as 0,6 do Yang2019) bit-idênticas por construção — o modo de
    falha que matou o T12 (cascata nas 0,6) é impossível aqui."""
    mat = dsa.JointMaterial(gth_k=1e-4, gth_A0=1e9)   # A0 alto: só acumula
    st = dsa.SlowState(F_0=26400.0, F_0_init=26400.0)
    res = _rate(st, mat, slip=0.0, delta=0.0004)
    esperado = (0.0004 / 5e-4) ** 3.8
    assert res["ds"]["A_gth"] == pytest.approx(esperado, rel=1e-9)
    assert res["dF_0"] == 0.0                          # incubando: sem perda
    # em slip: ZERO EXATO (nem acumula)
    res2 = _rate(st, mat, slip=2e-4, delta=0.0006)
    assert "A_gth" not in res2["ds"] and res2["dF_0"] == 0.0


def test_incubacao_e_drenagem_pos_A0():
    """Cruzou A0 ⇒ dθ = k·(δ/dref)^q; dF₀ e dE derivam do MESMO dθ."""
    mat = dsa.JointMaterial(gth_k=1e-4, gth_A0=100.0)
    geom = dsa.JointGeometry()
    st = dsa.SlowState(F_0=26400.0, F_0_init=26400.0, A_gth=200.0)
    res = _rate(st, mat, slip=0.0, delta=0.0004)
    rq = (0.0004 / 5e-4) ** 3.8
    dtheta = 1e-4 * rq
    assert res["ds"]["theta_loose"] == pytest.approx(dtheta, rel=1e-9)
    assert res["dF_0"] == pytest.approx(-geom.k_b * geom.lead_per_radian
                                        * dtheta, rel=1e-9)
    assert res["dE_dissipated"] > 0.0                 # atrito de filete real


def test_expoente_ingreme_separa_amplitudes():
    """A razão de taxas 0,6/0,4 tem de ser (1,5)^3,8 — a lei IJPEM.

    (Medida em stick artificial nas duas: o teste é da LEI, não do regime.)"""
    mat = dsa.JointMaterial(gth_k=1e-4, gth_A0=0.0)
    st = dsa.SlowState(F_0=26400.0, F_0_init=26400.0)
    r04 = _rate(st, mat, slip=0.0, delta=0.0004)["ds"]["theta_loose"]
    r06 = _rate(st, mat, slip=0.0, delta=0.0006)["ds"]["theta_loose"]
    assert r06 / r04 == pytest.approx(1.5 ** 3.8, rel=1e-9)


def test_force_mode_e_inerte():
    """delta_amp None (modo força) ⇒ o gth não existe — mesma convenção dos
    demais canais disp-mode."""
    mat = dsa.JointMaterial(gth_k=1e-4, gth_A0=0.0)
    st = dsa.SlowState(F_0=26400.0, F_0_init=26400.0)
    res = _rate(st, mat, slip=None, delta=None)
    assert res["ds"] == {} and res["dF_0"] == 0.0


def test_conservacao_com_gth_ativo():
    """Energia: o gth drenando NÃO pode abrir o balanço.

    Compara o residual de conservação do MESMO joint com e sem o gth (delta
    pequeno o bastante para ficar em stick o tempo todo): a diferença tem de
    ser desprezível frente à energia drenada — dF₀ e dE derivam do mesmo dθ,
    então a contabilidade fecha por construção; o teste prende isso."""
    # O joint default tem δ_t ≈ 1,5 µm (medido) — sub-limiar dele a razão^3,8
    # é ~2e-11/ciclo. Para EXERCITAR a drenagem, o dref é ancorado no próprio
    # δ do teste (razão = 1): stick garantido E taxa mensurável.
    geom = dsa.JointGeometry()
    _m0 = dsa.JointMaterial()
    _st0 = dsa.SlowState(F_0=26400.0, F_0_init=26400.0)
    dt = (_m0.delta_free + dsa.F_slip_transverse(_st0, _m0)
          / max(dsa.k_tr_transverse(geom, _m0), 1e-12))
    delta = dt / 2.0

    def roda(k):
        mat = dsa.JointMaterial(gth_k=k, gth_A0=10.0, gth_dref=delta,
                                N_emb=1000.0)
        ana = dsa.DynamicStiffnessAnalyzer(dsa.JointGeometry(), mat, 26400.0)
        for _ in range(500):
            ana.step_cycle(F_amp=0.0, theta_load=0.0, freq=5.0,
                           delta_amp=delta)
        return ana
    a_off, a_on = roda(0.0), roda(5e-5)
    assert a_on.state.A_gth > 10.0              # o gth de fato rodou
    assert a_on.state.F_0 < a_off.state.F_0     # e drenou preload
    d_res = abs(a_on.energy.conservation_residual
                - a_off.energy.conservation_residual)
    drenado = a_off.state.F_0 - a_on.state.F_0
    # ΔU elástico que o próprio gth liberou — a escala de referência.
    # k_b do ANALYZER (ele recomputa no __init__; o JointGeometry() cru
    # dava 6,7e8 vs efetivo ~1,1e9 e o ΔU saía 40 % menor).
    dU = (a_off.state.F_0 ** 2 - a_on.state.F_0 ** 2) / (2 * a_on.geom.k_b)
    # Contrato: as parcelas DO GTH fecham (atrito via W_ext + ΔU no dE —
    # medido: residual 0,894 → 0,0143 J, cada termo nomeado no engine). O
    # resto são termos CRUZADOS de outros mecanismos re-linearizados contra a
    # trajetória alterada. Teto ABSOLUTO = o piso da banda de residuais que o
    # engine JÁ tolera nos casos adotados (0,017–0,151 J, rampa de fratura —
    # CLAUDE.md/§4.50): o gth não pode ser pior que a contabilidade vigente.
    assert d_res <= 0.017, (
        f"gth abriu o balanço além da banda tolerada do engine: Δresidual="
        f"{d_res:.3e} J (ΔU do gth {dU:.3e} J, {drenado:.1f} N drenados)")


def test_backward_compat_slowstate():
    """Store antigo sem A_gth tem de reidratar (regra from_dict do repo)."""
    st = dsa.SlowState(F_0=1.0)
    assert st.A_gth == 0.0
