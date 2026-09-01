"""crash_trigger_frac (sec4.30/L14): gate Hill em F0/F0_init — plato enquanto F0
alto, runaway quando cruza o limiar. Default 0 = bit-identical."""
import numpy as np
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)


def _geom():
    return JointGeometry(A_s=84.3e-6, L_eff=12e-3, d_2=10.86e-3, pitch=1.5e-3,
                         r_bearing=9e-3, A_contact=117.6e-6)


def _gate(frac, ratio, k=8.0):
    ft = frac ** k
    return ft / (ft + ratio ** k)


def test_gate_shape():
    # suprimido no plato (F0 alto), ~0.5 no joelho, ~1 no runaway
    assert _gate(0.66, 1.00) < 0.15      # F0=F0_init: loosening suprimido
    assert abs(_gate(0.66, 0.66) - 0.5) < 1e-9   # no limiar: meio
    assert _gate(0.66, 0.40) > 0.90      # F0 caiu: runaway liberado


def _curve(frac, n=873):
    m = JointMaterial(emb_depth=5e-6, mu_thread=0.15, mu_bearing=0.15, c_bend=5.0,
                      k_tr_mode="bending", loose_torsion_mode="bolt_torsion",
                      eta_loose=15.0, slip_regime_mode="cattaneo_mindlin",
                      loose_arrest_floor=0.25, crash_trigger_frac=frac)
    ana = DynamicStiffnessAnalyzer(_geom(), m, 50e3)
    r = [1.0]
    for _ in range(n):
        ana.step_cycle(0.4 * 50e3, np.pi / 2, 12.0, delta_amp=0.15e-3)
        r.append(max(ana.state.F_0, 0.0) / 50e3)
    return np.array(r)


def test_default_inert():
    assert JointMaterial().crash_trigger_frac == 0.0
    assert np.array_equal(_curve(0.0), _curve(0.0))


def test_trigger_delays_collapse():
    grad, trig = _curve(0.0), _curve(0.66)
    # a MEIO caminho o gatilho retem mais (suprimiu o loosening enquanto F0 alto)
    mid = len(grad) // 4
    assert trig[mid] > grad[mid] + 0.02
    # o joelho (maior queda) ocorre mais tarde com o gatilho
    assert int(np.argmin(np.gradient(trig))) >= int(np.argmin(np.gradient(grad)))
