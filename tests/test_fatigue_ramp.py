"""Tests for the opt-in fatigue RAMP discharge (prereg 2026-07-28-ramp-capability).

Section-loss ramp replaces the one-cycle cliff when fat_ramp_D_on < 1.0:
  alpha = ((D - D_on)/(1 - D_on))^q ;  g = (1-alpha)(1+rho)/((1-alpha)+rho)
  dF_0 = F_0*(g(D1)/g(D0) - 1) <= 0 ;  dE = Delta U_internal (cliff route)
Default fat_ramp_D_on = 1.0 => the ramp branch is never entered and the cliff
path is byte-for-byte the pre-change code (P0/P2 of the prereg)."""
import numpy as np
from dataclasses import replace
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    FatigueLoss, U_internal)


def _geom(grip_mm=30.0):
    return JointGeometry(A_s=84.3e-6, L_eff=grip_mm * 1e-3, d_2=10.86e-3,
                         pitch=1.75e-3, r_bearing=9e-3, A_contact=117.6e-6)


def _mat(**kw):
    """Fadiga com relogio deterministico: Goodman neutro + N_f = 1000 exato."""
    base = dict(fatigue_enabled=True, fat_stress_mode="axial", fat_Kt=1.0,
                fat_sigma_uts=1e30, fat_sigma_knee=0.0, fat_sigma_endurance=1.0,
                fat_m1=1.0)
    base.update(kw)
    m = JointMaterial(**base)
    return m


def _state(F0=50e3, D=0.0):
    return SlowState(F_0=F0, F_0_init=F0, D_fatigue=D)


def _rate(mat, state, F_amp=84.3, geom=None):
    # A_s=84.3e-6, Kt=1 => sigma_a = F_amp/A_s; F_amp=84.3 N => sigma=1e6 Pa.
    # Com fat_C1 = 1e6 * N_f_alvo e m1=1: sun_life = C1*sigma^-1 = N_f_alvo.
    return FatigueLoss().rate(state, geom or _geom(), mat, F_amp, 0.0, 30.0, 1)


def test_new_fields_defaults_are_inert():
    m = JointMaterial()
    assert m.fat_ramp_D_on == 1.0 and m.fat_ramp_q == 5.0
    assert m.fatigue_enabled is False


def test_don_1_keeps_cliff_semantics():
    """D_on=1.0 (default): zero dF_0 antes do cliff; descarga total no cliff."""
    m = _mat(fat_C1=1e6 * 1000.0)          # N_f = 1000
    r = _rate(m, _state(D=0.5))
    assert r["dF_0"] == 0.0 and r["dE_dissipated"] == 0.0
    assert abs(r["ds"]["D_fatigue"] - 1e-3) < 1e-12
    r2 = _rate(m, _state(D=0.9999))         # cruza 1.0 neste ciclo -> cliff
    assert r2["dF_0"] < 0.0
    assert abs(r2["dF_0"] + 50e3) < 1e-6    # residual_frac=0 => -F_0 inteiro


def test_ramp_is_silent_below_don():
    m = _mat(fat_C1=1e6 * 1000.0, fat_ramp_D_on=0.75, fat_ramp_q=8.0)
    r = _rate(m, _state(D=0.5))
    assert r["dF_0"] == 0.0 and r["dE_dissipated"] == 0.0
    assert r["ds"]["D_fatigue"] > 0.0       # o relogio de Miner segue correndo


def test_ramp_discharges_smoothly_and_monotonically():
    m = _mat(fat_C1=1e6 * 1000.0, fat_ramp_D_on=0.75, fat_ramp_q=8.0)
    g = _geom()
    state = _state()
    drops = []
    for n in range(1000):
        r = FatigueLoss().rate(state, g, m, 84.3, 0.0, 30.0, n + 1)
        state = replace(state,
                        F_0=max(state.F_0 + r["dF_0"], 0.0),
                        D_fatigue=state.D_fatigue + r["ds"]["D_fatigue"])
        drops.append(-r["dF_0"])
    assert state.F_0 < 1.0                          # rampa leva F_0 -> ~0
    assert max(drops) < 50e3 * 0.5                  # NUNCA um cliff de 1 ciclo
    n_active = sum(1 for d in drops if d > 0.0)
    assert n_active > 50                            # perda espalhada pela janela
    first_active = next(i for i, d in enumerate(drops) if d > 0.0)
    assert first_active >= int(0.75 * 1000) - 2     # comeca ~D_on


def test_ramp_energy_is_internal_release():
    m = _mat(fat_C1=1e6 * 1000.0, fat_ramp_D_on=0.75, fat_ramp_q=8.0)
    g = _geom()
    st = _state(D=0.90)
    r = _rate(m, st, geom=g)
    assert r["dF_0"] < 0.0
    U0 = U_internal(st, g, m)
    U1 = U_internal(replace(st, F_0=max(st.F_0 + r["dF_0"], 0.0)), g, m)
    assert abs(r["dE_dissipated"] - max(U0 - U1, 0.0)) < 1e-9
    assert r["dE_dissipated"] > 0.0


def test_ramp_reaches_zero_not_residual_frac():
    """Na rampa g(1)=0 => F_0 -> 0; fatigue_residual_frac NAO e lido."""
    m = _mat(fat_C1=1e6 * 1000.0, fat_ramp_D_on=0.75, fat_ramp_q=8.0,
             fatigue_residual_frac=0.3)
    st = _state(D=0.999999)
    r = _rate(m, st)
    st2 = replace(st, F_0=max(st.F_0 + r["dF_0"], 0.0))
    assert st2.F_0 < 0.3 * 50e3 * 0.01              # nada de piso em 30%


def test_run_path_generates_s_curve_via_overrides(qapp):
    """P4 do prereg: os campos fat_*/fat_ramp_* fluem por _v2_tuner_overrides
    (filtro __dataclass_fields__) e o Run gera a curva em S completa ate ~0.

    O relogio e' ancorado por VARREDURA de fat_C1 (robusto a geometria do
    preset): com m1=1 e Goodman neutro, N_f = C1/sigma_a e' constante — algum
    C1 da decada certa fratura dentro da janela de 12k ciclos."""
    import types
    from bolt_analysis_studio.core.solver_worker import SolverWorker
    w = SolverWorker.__new__(SolverWorker)
    gl = types.SimpleNamespace(control_mode="displacement", delta_amplitude=0.8,
                               frequency=0.5, type="TRANSVERSE")
    cfg = types.SimpleNamespace(initial_preload=50000.0, transverse_force=12000.0,
                                bolt_diameter_mm=16.0, pitch_mm=2.0)
    tuners = dict(fatigue_enabled=True, fat_stress_mode="bending", fat_Kt=1.0,
                  fat_sigma_uts=1e30, fat_sigma_knee=0.0,
                  fat_sigma_endurance=1.0, fat_m1=1.0,
                  fat_ramp_D_on=0.75, fat_ramp_q=8.0)
    ratio = None
    # DESCENDO: o primeiro C1 (maior) que fratura = relogio mais LENTO que cabe
    # na janela — rampa bem resolvida. Ascendente pegaria N_f~29 (rampa de ~7
    # ciclos), que parece cliff por amostragem, nao por fisica.
    for c1 in (1e14, 1e13, 1e12, 1e11, 1e10):
        tuners["fat_C1"] = c1
        w._current_model = types.SimpleNamespace(global_loading=gl,
                                                 _v2_tuner_overrides=dict(tuners))
        r = np.asarray(w._compute_v2_history(cfg, 12000)["ratio"], dtype=float)
        if r[-1] < 0.05:                      # fraturou dentro da janela
            ratio = r
            break
    assert ratio is not None, "nenhum C1 da varredura fraturou em 12k ciclos"
    drops = -np.diff(ratio)
    assert float(drops.max()) < 0.5           # rampa, nao cliff de 1 ciclo
    assert int((drops > 1e-6).sum()) > 30     # perda espalhada (S-curve)


def test_v2_cycle_cap_rules():
    """Resolucao do _CAP (2026-07-28): 400k SO com fadiga+rampa no override;
    100k em todos os outros casos, incluindo valores invalidos."""
    from bolt_analysis_studio.core.solver_worker import _v2_cycle_cap
    assert _v2_cycle_cap(None) == 100_000
    assert _v2_cycle_cap({}) == 100_000
    assert _v2_cycle_cap({"fatigue_enabled": True}) == 100_000       # cliff: sem rampa
    assert _v2_cycle_cap({"fat_ramp_D_on": 0.75}) == 100_000         # rampa sem fadiga
    assert _v2_cycle_cap({"fatigue_enabled": True,
                          "fat_ramp_D_on": 0.75}) == 400_000
    assert _v2_cycle_cap({"fatigue_enabled": True,
                          "fat_ramp_D_on": 1.0}) == 100_000
    assert _v2_cycle_cap({"fatigue_enabled": True,
                          "fat_ramp_D_on": "lixo"}) == 100_000       # invalido -> conservador


def test_run_history_is_pruned_for_memory(qapp):
    """A poda da history no loop do Run mantem memoria O(1) sem mudar numeros
    (o engine nunca le a propria history; o loop usa o snap retornado)."""
    import types
    from bolt_analysis_studio.core.solver_worker import SolverWorker
    w = SolverWorker.__new__(SolverWorker)
    gl = types.SimpleNamespace(control_mode="displacement", delta_amplitude=0.5,
                               frequency=0.5, type="TRANSVERSE")
    cfg = types.SimpleNamespace(initial_preload=50000.0, transverse_force=12000.0,
                                bolt_diameter_mm=16.0, pitch_mm=2.0)
    w._current_model = types.SimpleNamespace(global_loading=gl,
                                             _v2_tuner_overrides=None)
    h = w._compute_v2_history(cfg, 2000)
    assert h is not None and len(h["ratio"]) == 2001
    r = np.asarray(h["ratio"], dtype=float)
    assert r[0] == 1.0 and np.all(np.diff(r) <= 1e-9)   # trajetoria intacta


def test_analyzer_end_to_end_s_curve():
    """Integrado: com rampa ativa a curva e' um S ate ~0 sem degrau de 1 ciclo."""
    g = _geom()
    m = _mat(fat_C1=1e6 * 500.0, fat_ramp_D_on=0.75, fat_ramp_q=8.0)
    ana = DynamicStiffnessAnalyzer(g, m, 50e3)
    r = [1.0]
    for _ in range(600):
        ana.step_cycle(84.3, 0.0, 30.0)
        r.append(max(ana.state.F_0, 0.0) / 50e3)
    r = np.array(r)
    assert r[-1] < 0.05
    assert np.max(-np.diff(r)) < 0.5                # sem cliff
    assert abs(float(getattr(ana.energy, "conservation_residual", 0.0))) < 0.5
