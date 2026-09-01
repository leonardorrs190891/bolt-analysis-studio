"""Axial thread-flank fretting loss (spec 2026-07-06): Archard flank, opt-in, prop A_F."""
import numpy as np

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    ThreadFrettingLoss,
)

M12 = JointGeometry(A_s=84.3e-6, L_eff=0.040, d_2=10.863e-3,
                    pitch=1.75e-3, r_bearing=10e-3, A_contact=1.5e-4)


def test_off_by_default_returns_zero():
    m = JointMaterial()                      # k_thread_fret default 0.0
    assert m.k_thread_fret == 0.0
    st = SlowState(F_0=50e3)
    r = ThreadFrettingLoss().rate(st, M12, m, 20e3, 0.0, 30.0, 100)
    assert r["dF_0"] == 0.0 and r["dE_dissipated"] == 0.0


def test_axial_loss_scales_linearly_with_AF():
    m = JointMaterial(k_thread_fret=0.5)
    st = SlowState(F_0=50e3)
    r1 = ThreadFrettingLoss().rate(st, M12, m, 10e3, 0.0, 30.0, 100)   # axial, A_F=10kN
    r2 = ThreadFrettingLoss().rate(st, M12, m, 20e3, 0.0, 30.0, 100)   # axial, A_F=20kN
    assert r1["dF_0"] < 0.0                                            # loss
    assert abs(r2["dF_0"]) == abs(r1["dF_0"]) * 2                      # linear in A_F


def test_transverse_is_inert_even_when_enabled():
    m = JointMaterial(k_thread_fret=0.5)
    st = SlowState(F_0=50e3)
    r = ThreadFrettingLoss().rate(st, M12, m, 20e3, np.pi / 2, 30.0, 100)  # theta=pi/2
    assert r["dF_0"] == 0.0                                            # F_ax = cos(pi/2) = 0


def test_end_to_end_AF_gradient_becomes_nonzero():
    """Two axial runs at different A_F give different final F0 (today identical)."""
    geom = M12

    def run(F_amp):
        m = JointMaterial(k_thread_fret=0.5, mu_thread=0.12, mu_bearing=0.12,
                          emb_depth=9.5e-6)
        ana = DynamicStiffnessAnalyzer(geom, m, 40e3)
        for _ in range(2000):
            ana.step_cycle(F_amp, 0.0, 30.0)                          # axial, force-mode
        return max(ana.state.F_0, 0.0) / 40e3

    assert run(15e3) > run(25e3)             # higher A_F => more loss => lower final


def test_conservation_not_worsened_by_fretting():
    """dE counted in W_diss AND sourced in W_ext => enabling fretting does not
    worsen the conservation residual (balanced-sourcing fix, spec 2026-07-06)."""
    geom = M12

    def resid(kf):
        m = JointMaterial(k_thread_fret=kf, mu_thread=0.12, mu_bearing=0.12,
                          emb_depth=9.5e-6)
        ana = DynamicStiffnessAnalyzer(geom, m, 40e3)
        for _ in range(2000):
            ana.step_cycle(20e3, 0.0, 30.0)
        return abs(ana.energy.conservation_residual)

    assert resid(0.5) <= resid(0.0) + 1.0     # not worsened (both sides sourced)


def test_dF0_by_mech_includes_fretting_and_sums_to_total():
    """thread_fretting appears in the decomposition and the mechs sum to the F_0
    drop (the invariant the GUI/server decomposition relies on)."""
    geom = M12
    m = JointMaterial(k_thread_fret=0.5, mu_thread=0.12, mu_bearing=0.12, emb_depth=9.5e-6)
    ana = DynamicStiffnessAnalyzer(geom, m, 40e3)
    F0_before = ana.state.F_0
    snap = ana.step_cycle(20e3, 0.0, 30.0)                # axial => fretting fires
    assert snap.dF_0_by_mech["thread_fretting"] < 0.0
    total = sum(snap.dF_0_by_mech.values())
    assert abs((ana.state.F_0 - F0_before) - total) < 1.0  # mechs sum to F_0 change
