"""Fatigue-cliff energy conservation (spec 2026-07-08 #6).

The fracture cliff drops F_0 suddenly, releasing stored elastic energy. That
release is now booked as W_diss_fracture (= the released U), so the conservation
residual does NOT spike at the fracture cycle (before: residual ~ +U_released with
dE=0). Normal (non-fracture) runs are unchanged (bucket stays 0)."""
import numpy as np
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)


def _geom(grip_mm=30.0):
    return JointGeometry(A_s=84.3e-6, L_eff=grip_mm * 1e-3, d_2=10.86e-3,
                         pitch=1.75e-3, r_bearing=9e-3, A_contact=117.6e-6)


def test_fatigue_cliff_conserves():
    m = JointMaterial(emb_depth=3.5e-6, mu_thread=0.15, mu_bearing=0.15,
                      fatigue_enabled=True, fat_C1=1e3, fat_m1=1.0,
                      fat_sigma_knee=1.0, fat_sigma_endurance=1.0)
    ana = DynamicStiffnessAnalyzer(_geom(), m, 20e3)
    for _ in range(1000):
        ana.step_cycle(10e3, 0.0, 30.0)
        if ana.state.D_fatigue >= 1.0:
            break
    e = ana.energy
    assert ana.state.F_0 <= 1.0                    # fractured
    assert e.W_diss_fracture > 0.0                 # fracture energy booked
    scale = max(abs(e.W_ext) + abs(e.U_released), abs(e.W_diss_total), 1.0)
    # without the fix the cliff releases ~all of U with dE=0 => residual ~ scale;
    # with the fix the released U is booked => residual stays small.
    assert abs(e.conservation_residual) / scale < 0.1


def test_no_fatigue_no_fracture_bucket():
    m = JointMaterial(emb_depth=3.5e-6, mu_thread=0.15, mu_bearing=0.15)  # fatigue off
    ana = DynamicStiffnessAnalyzer(_geom(), m, 20e3)
    for _ in range(300):
        ana.step_cycle(10e3, 0.0, 30.0)
    assert ana.energy.W_diss_fracture == 0.0       # inert when no fracture
