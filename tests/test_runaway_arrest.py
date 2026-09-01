"""Tests for the self-locking runaway-arrest gate (spec 2026-07-07, roadmap #4).

self_locking_gate = max(0, 1 - loose_arrest_floor*F_0_init/F_0) multiplies d_theta so the
loosening runaway settles at a stable residual F_min instead of collapsing to 0. Default
loose_arrest_floor=0 = bit-identical (gate=1). Composes with loose_torsion_mode."""
import numpy as np
import pytest
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    self_locking_gate,
)


def _m12_geom(grip_mm):
    return JointGeometry(A_s=84.3e-6, L_eff=grip_mm * 1e-3, d_2=10.86e-3,
                         pitch=1.75e-3, r_bearing=9e-3, A_contact=117.6e-6)


def test_default_arrest_floor_zero():
    assert JointMaterial().loose_arrest_floor == 0.0


def test_self_locking_gate_values():
    m0 = JointMaterial(loose_arrest_floor=0.0)
    m = JointMaterial(loose_arrest_floor=0.1)      # F_min = 0.1*F_0_init
    assert self_locking_gate(SlowState(F_0=1e4, F_0_init=1e4), m0) == 1.0       # inert
    assert self_locking_gate(SlowState(F_0=1e4, F_0_init=1e4), m) == pytest.approx(0.9)
    assert self_locking_gate(SlowState(F_0=2e3, F_0_init=1e4), m) == pytest.approx(0.5)
    assert self_locking_gate(SlowState(F_0=1e3, F_0_init=1e4), m) == 0.0        # at F_min
    assert self_locking_gate(SlowState(F_0=5e2, F_0_init=1e4), m) == 0.0        # below -> clamped


def _run_t10(floor):
    geom = _m12_geom(25.0)
    mat = JointMaterial(emb_depth=2.5e-6, mu_thread=0.15, mu_bearing=0.15,
                        loose_torsion_mode="bolt_torsion", eta_loose=15.0,
                        loosening_slip_coupling="gross_fraction", k_tr_mode="bending",
                        c_bend=0.30, loose_arrest_floor=floor)
    ana = DynamicStiffnessAnalyzer(geom, mat, 10250.0)
    for _ in range(180):
        ana.step_cycle(0.4 * 10250.0, np.pi / 2, 1.0, delta_amp=0.5e-3)
    return max(ana.state.F_0, 0.0) / 10250.0


def test_arrest_stops_collapse_off_still_collapses():
    f_off = _run_t10(0.0)          # #10 with no arrest -> over-collapses (bit-identical)
    f_on = _run_t10(0.05)          # arrest -> settles at a residual >= F_min
    assert f_off < 0.01            # #10 over-collapses to ~0 without the arrest
    assert f_on > 0.03             # arrest -> stable residual (does NOT collapse to 0)
    assert abs(f_on - 0.05) < 0.02 # residual tracks the floor (~0.046 for floor=0.05;
                                   # sits just below F_min as ungated emb/creep/wear drift on)
