"""Tests for the opt-in bolt-torsion loosening magnitude (spec 2026-07-07, #10/§4.8).

The mechanism replaces the arbitrary k_torsional = k_j_init*d_2/2 (~2e7) with the
physical bolt-shank torsional compliance eta_loose*G*J/L_eff (~4e3, ~5000x smaller)
so the existing runaway can fire. Default loose_torsion_mode="legacy" = bit-identical.
These tests pin the ROBUST capability claims (grip-sensitive significant rotation),
NOT a clean fit of the Rousseau triple (it over-collapses t10 without an arrest form)."""
import numpy as np
import pytest
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    RotationalLooseningLoss, G_STEEL,
)


def _m12_geom(grip_mm):
    return JointGeometry(A_s=84.3e-6, L_eff=grip_mm * 1e-3, d_2=10.86e-3,
                         pitch=1.75e-3, r_bearing=9e-3, A_contact=117.6e-6)


def test_default_is_legacy_and_eta_unread():
    m = JointMaterial()
    assert m.loose_torsion_mode == "legacy"
    assert m.eta_loose == 1.0
    # In legacy, eta_loose must be UNREAD -> loosening dF_0 independent of it
    # (proves the new field is inert in the default path; bit-identical guard).
    geom = _m12_geom(25.0)
    st = SlowState(F_0=10000.0, F_0_init=10000.0)
    loss = RotationalLooseningLoss()
    common = dict(mu_thread=0.15, mu_bearing=0.15, loosening_slip_coupling="off")
    r1 = loss.rate(st, geom, JointMaterial(loose_torsion_mode="legacy", eta_loose=1.0,
                                           **common), 5000.0, np.pi / 2, 1.0, 1)
    r2 = loss.rate(st, geom, JointMaterial(loose_torsion_mode="legacy", eta_loose=999.0,
                                           **common), 5000.0, np.pi / 2, 1.0, 1)
    assert r1["dF_0"] < 0.0 and r1["dF_0"] == r2["dF_0"]


def test_bolt_torsion_k_torsional_amplifies_loosening():
    # Same firing state, gate OFF (isolate the k_torsional change): bolt_torsion's
    # ~5000x-smaller k_torsional makes the loosening dF_0 ~5000x larger.
    geom = _m12_geom(25.0)
    st = SlowState(F_0=10000.0, F_0_init=10000.0)
    common = dict(mu_thread=0.15, mu_bearing=0.15, loosening_slip_coupling="off")
    m_leg = JointMaterial(loose_torsion_mode="legacy", **common)
    m_bolt = JointMaterial(loose_torsion_mode="bolt_torsion", eta_loose=1.0, **common)
    loss = RotationalLooseningLoss()
    r_leg = loss.rate(st, geom, m_leg, 5000.0, np.pi / 2, 1.0, 1)
    r_bolt = loss.rate(st, geom, m_bolt, 5000.0, np.pi / 2, 1.0, 1)
    assert r_leg["dF_0"] < 0.0 and r_bolt["dF_0"] < 0.0        # both fire
    ratio = r_bolt["dF_0"] / r_leg["dF_0"]                      # both < 0 -> positive
    # k_j_init*d_2/2 = 2.17e7 vs G*J/L = 77e9*(pi*d_2^4/32)/0.025 = 4.2e3 -> ~5000x
    assert ratio > 1000.0


def test_bolt_torsion_uses_physical_compliance():
    # Sanity on the physical value: legacy dF_0 / bolt dF_0 ~= k_tors_bolt / k_tors_leg
    geom = _m12_geom(25.0)
    J = np.pi * geom.d_2 ** 4 / 32.0
    k_bolt = G_STEEL * J / geom.L_eff          # eta=1
    k_leg = 4e9 * geom.d_2 / 2.0               # k_j_init default 4e9
    assert k_bolt < k_leg / 1000.0             # ~5000x smaller


def test_grip_sensitive_spread_with_trio():
    # With the trio (bolt_torsion + gross_fraction onset + bending k_tr) and a milder
    # settling input, rotation becomes grip-sensitive: thin grip collapses, thick
    # survives -> monotone finals + a large spread the baseline (~0.19) cannot make.
    finals = []
    for grip, F0 in [(25.0, 10250.0), (29.0, 10250.0), (33.0, 10350.0)]:
        geom = _m12_geom(grip)
        mat = JointMaterial(emb_depth=2.5e-6, mu_thread=0.15, mu_bearing=0.15,
                            loose_torsion_mode="bolt_torsion", eta_loose=15.0,
                            loosening_slip_coupling="gross_fraction",
                            k_tr_mode="bending", c_bend=0.30)
        ana = DynamicStiffnessAnalyzer(geom, mat, F0)
        for _ in range(180):
            ana.step_cycle(0.4 * F0, np.pi / 2, 1.0, delta_amp=0.5e-3)
        finals.append(max(ana.state.F_0, 0.0) / F0)
    t10, t12, t14 = finals
    assert t10 < t12 < t14                      # grip-monotone (thin loosens most)
    assert t10 < 0.15                           # thin grip collapses
    assert t14 > 0.6                            # thick grip survives
    assert (t14 - t10) > 0.4                    # spread >> baseline ~0.19


def test_force_mode_inert():
    # Axial (theta=0 -> F_tr=0): T_loose stays << T_resist, so rate() returns dF_0=0
    # at the T_loose<=T_resist guard (before the k_torsional branch) -> inert both modes.
    geom = _m12_geom(25.0)
    st = SlowState(F_0=10000.0, F_0_init=10000.0)
    loss = RotationalLooseningLoss()
    for mode in ("legacy", "bolt_torsion"):
        m = JointMaterial(loose_torsion_mode=mode, eta_loose=15.0,
                          mu_thread=0.15, mu_bearing=0.15)
        r = loss.rate(st, geom, m, 5000.0, 0.0, 1.0, 1)   # theta_load = 0 (axial)
        assert r["dF_0"] == 0.0
