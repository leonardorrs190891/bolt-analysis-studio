"""Loosening slip-regime gate (spec 2026-07-06): gross-slip-fraction gate, opt-in."""
import numpy as np

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    RotationalLooseningLoss, F_slip_transverse, k_tr_transverse,
    loosening_slip_gate,
)

M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=2.09e-4)


def test_gate_off_by_default_returns_one():
    m = JointMaterial()
    assert m.loosening_slip_coupling == "off"
    st = SlowState(F_0=50e3)
    assert loosening_slip_gate(st, M16, m, 0.0) == 1.0
    assert loosening_slip_gate(st, M16, m, 5e-4) == 1.0
    assert loosening_slip_gate(st, M16, m, None) == 1.0


def test_gate_force_mode_returns_one_even_when_on():
    m = JointMaterial(loosening_slip_coupling="gross_fraction")
    st = SlowState(F_0=50e3)
    assert loosening_slip_gate(st, M16, m, None) == 1.0


def test_gate_partial_slip_is_zero():
    m = JointMaterial(loosening_slip_coupling="gross_fraction")
    st = SlowState(F_0=50e3)
    assert loosening_slip_gate(st, M16, m, 0.0) == 0.0


def test_gate_ramps_and_saturates_in_gross():
    m = JointMaterial(k_tr_mode="bending", loosening_slip_coupling="gross_fraction")
    st = SlowState(F_0=50e3)
    dt = F_slip_transverse(st, m) / k_tr_transverse(M16, m)   # delta_t
    assert abs(loosening_slip_gate(st, M16, m, dt) - 0.5) < 1e-9   # slip=dt => 1/2
    assert loosening_slip_gate(st, M16, m, 0.01 * dt) < 0.02       # barely gross
    assert loosening_slip_gate(st, M16, m, 100.0 * dt) > 0.98      # deep gross => ~1


def test_loosening_dF0_zeroed_in_partial_when_coupled():
    """coupling on + slip_amp=0 => g=0 => loosening dF_0 exactly 0."""
    m = JointMaterial(k_tr_mode="bending", loosening_slip_coupling="gross_fraction")
    st = SlowState(F_0=50e3)
    r = RotationalLooseningLoss().rate(st, M16, m, 0.4 * 50e3, np.pi / 2,
                                       0.5, 100, slip_amp_override=0.0)
    assert r["dF_0"] == 0.0
    assert r["dE_dissipated"] == 0.0


def test_end_to_end_gate_retains_preload_in_partial_regime():
    """liu2025-like M16 partial case: gate ON retains materially more F0 than OFF."""
    geom = M16
    F0, delta, freq, F_amp = 60e3, 0.25e-3, 0.5, 0.4 * 60e3

    def run(coupling):
        m = JointMaterial(k_tr_mode="bending", loosening_slip_coupling=coupling,
                          mu_bearing=0.15, mu_thread=0.15, emb_depth=9.5e-6,
                          C_creep=1.867e-11)
        ana = DynamicStiffnessAnalyzer(geom, m, F0)
        for _ in range(20000):
            ana.step_cycle(F_amp, np.pi / 2, freq, delta_amp=delta)
        return max(ana.state.F_0, 0.0) / F0

    r_off = run("off")
    r_on = run("gross_fraction")
    assert r_on > r_off + 0.2      # gate suppresses partial-slip loosening
    assert r_off < 0.5             # gate off: loosening drives collapse
    assert r_on > 0.6              # gate on: plateaus
