"""Conformacao dependente de pressao (spec 2026-07-04). Unidade + engine."""
import numpy as np
import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    conformation_gate,
)

M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)


def _run(mat, F0, n_cycles, delta=0.5e-3):
    ana = DynamicStiffnessAnalyzer(M16, mat, F0)
    r = [1.0]
    for _ in range(n_cycles):
        ana.step_cycle(20e3, np.pi / 2, 0.5, delta_amp=delta)
        r.append(max(ana.state.F_0, 0.0) / F0)
    return ana, np.array(r)


def test_gate_inert_when_ref_nonpositive():
    mat = JointMaterial()  # W_conf_ref default 0.0
    for w in (0.0, 1e3, 1e9):
        assert conformation_gate(SlowState(F_0=50e3, W_conf=w), mat) == 1.0


def test_gate_closes_monotonically_with_conformation():
    mat = JointMaterial(W_conf_ref=1e4)
    g0 = conformation_gate(SlowState(F_0=50e3, W_conf=0.0), mat)
    ghalf = conformation_gate(SlowState(F_0=50e3, W_conf=1e4), mat)
    ghi = conformation_gate(SlowState(F_0=50e3, W_conf=1e6), mat)
    assert g0 == pytest.approx(1.0)
    assert ghalf == pytest.approx(0.5)
    assert ghi < 0.05
    assert g0 > ghalf > ghi > 0.0


def test_inert_by_default_leaves_state_untouched():
    ana, r = _run(JointMaterial(), 50e3, 300)
    assert ana.state.W_conf == 0.0                        # accumulator off
    assert conformation_gate(ana.state, ana.mat) == 1.0   # gate never bites
    assert 0.0 < r[-1] < 1.0                               # normal loosening still happens


def test_conformation_arrests_loosening_at_high_pressure():
    F0 = 132.8e3
    ctrl, r_ctrl = _run(JointMaterial(), F0, 2500)                # no conformation
    conf, r_conf = _run(JointMaterial(W_conf_ref=1e4), F0, 2500)  # active
    assert conf.state.W_conf > 0.0                        # accumulated
    assert conformation_gate(conf.state, conf.mat) < 0.5  # substantially closed
    assert r_conf[-1] > r_ctrl[-1] + 0.2                  # plateau vs runaway


def test_conformation_does_not_degrade_conservation():
    ctrl, _ = _run(JointMaterial(), 132.8e3, 1500)
    conf, _ = _run(JointMaterial(W_conf_ref=1e4), 132.8e3, 1500)
    assert abs(conf.energy.conservation_residual) <= abs(ctrl.energy.conservation_residual) + 1.0


def test_pressure_gates_regime_separation():
    # SAME constants; only F0 (pressure) differs => nova ~inert, sobretorque locks
    mat = dict(W_conf_ref=5e4, conform_pressure_exp=2.0)
    nova, _ = _run(JointMaterial(**mat), 50e3, 2500)
    sob, _ = _run(JointMaterial(**mat), 132.8e3, 2500)
    g_nova = conformation_gate(nova.state, JointMaterial(**mat))
    g_sob = conformation_gate(sob.state, JointMaterial(**mat))
    assert g_nova > g_sob + 0.3   # pressure separates the regimes
    assert g_sob < 0.6            # sobretorque conforms


# ===== driver de equilibrio auto-limitante (spec §7, strand 2) =====

def test_conform_driver_default_is_raw():
    """Default = raw (monotonico) -> backward-compat bit-identical."""
    assert JointMaterial().conform_driver == "raw"


def test_effective_driver_self_attenuates_below_raw():
    """Efetivo pondera o incremento pelo gate de inicio-de-ciclo => acumula
    MENOS trabalho de conformacao que o raw (mesmo estado, so o driver difere)."""
    common = dict(W_conf_ref=1e4, conform_pressure_exp=2.0)
    raw, _ = _run(JointMaterial(**common), 132.8e3, 40)
    eff, _ = _run(JointMaterial(**common, conform_driver="effective"), 132.8e3, 40)
    assert eff.state.W_conf > 0.0                 # ainda conforma
    assert eff.state.W_conf < raw.state.W_conf    # mas auto-atenua


def test_effective_driver_inert_when_W_conf_ref_zero():
    """Com W_conf_ref=0 o modo efetivo segue inerte (W_conf fica 0)."""
    eff, _ = _run(JointMaterial(W_conf_ref=0.0, conform_driver="effective"), 132.8e3, 10)
    assert eff.state.W_conf == 0.0


def test_effective_driver_uses_start_of_cycle_gate():
    """Ordenacao (crux, review strand 2): o gate e lido no INICIO do ciclo. No
    ciclo 1 W_conf=0 => g=1 => incremento NAO atenuado, logo effective == raw
    apos 1 ciclo; so a partir do ciclo 2 (g<1) o effective diverge abaixo do raw.
    Guarda contra mover o '+=' antes da leitura do gate (um gate de fim-de-ciclo
    ja atenuaria o ciclo 1 e este teste pegaria)."""
    common = dict(W_conf_ref=1e4, conform_pressure_exp=2.0)
    raw1, _ = _run(JointMaterial(**common), 132.8e3, 1)
    eff1, _ = _run(JointMaterial(**common, conform_driver="effective"), 132.8e3, 1)
    assert eff1.state.W_conf == pytest.approx(raw1.state.W_conf, rel=1e-9)  # g(0)=1
    raw2, _ = _run(JointMaterial(**common), 132.8e3, 2)
    eff2, _ = _run(JointMaterial(**common, conform_driver="effective"), 132.8e3, 2)
    assert eff2.state.W_conf < raw2.state.W_conf   # ciclo 2: g<1, atenua
