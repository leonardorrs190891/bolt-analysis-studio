"""Stage-1 incubation gate (3-stage Junker shape).

The slip-driven collapse (wear + rotational loosening) is suppressed until the
accumulated transverse slip work crosses ``slip_onset_W`` (Jiang stage I),
producing a flat plateau, then a drop, then saturation. ``slip_onset_W = 0``
must reproduce the previous smooth-decay behaviour exactly (backward-compat).
"""

import math

import numpy as np
import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    slip_onset_gate,
)


def _geom():
    d, p = 16e-3, 2e-3
    d2 = d - 0.6495 * p
    d1 = d - 1.0825 * p
    A_s = math.pi / 4 * ((d2 + d1) / 2) ** 2
    return JointGeometry(A_s=A_s, L_eff=0.05, d_2=d2, pitch=p,
                         r_bearing=0.75 * d, A_contact=1e-4)


def _run(**mat_kw):
    mat = JointMaterial(**mat_kw)
    ana = DynamicStiffnessAnalyzer(_geom(), mat, 50000.0)
    r = [1.0]
    for _ in range(559):
        ana.step_cycle(12000.0, math.pi / 2, 0.5, delta_amp=0.5e-3)
        r.append(max(ana.state.F_0, 0.0) / 50000.0)
    return np.array(r)


def test_gate_off_when_threshold_zero():
    mat = JointMaterial(slip_onset_W=0.0)
    st = SlowState(F_0=50000.0, W_slip_acc=123.0)
    assert slip_onset_gate(st, mat) == 1.0


def test_gate_is_bounded_and_monotonic():
    mat = JointMaterial(slip_onset_W=1000.0, slip_onset_sharpness=4.0)
    vals = [slip_onset_gate(SlowState(F_0=1.0, W_slip_acc=w), mat)
            for w in (0.0, 250.0, 1000.0, 4000.0, 1e6)]
    assert all(0.0 <= v <= 1.0 for v in vals)
    assert vals == sorted(vals)              # monotonic increasing
    assert vals[0] < 0.05                    # ~off well below threshold
    assert vals[2] == pytest.approx(0.5, abs=1e-9)   # 0.5 at the threshold
    assert vals[-1] > 0.99                   # ~on well above threshold


def test_incubation_produces_flat_stage1_then_drop():
    # small embedding/creep (settling) + strong gated wear.
    # Estagio B: constantes fisicas diretas (era k_emb_scale=0.02/k_creep=0/
    # k_wear_tr=5.0 — foldados em emb_depth/C_creep/K_archard pelo shim).
    _b = JointMaterial()
    common = dict(emb_depth=0.02 * _b.emb_depth, C_creep=0.0,
                  K_archard=5.0 * _b.K_archard)
    with_inc = _run(slip_onset_W=700.0, **common)
    without = _run(slip_onset_W=0.0, **common)

    # Stage 1 stays essentially flat with incubation...
    assert with_inc[40] > 0.97
    # ...and is clearly lower without it (collapse starts at cycle 0).
    assert without[40] < 0.92
    # Stage 2: incubated curve does collapse later.
    assert with_inc[300] < 0.6
    # Monotone non-increasing (preload only lost).
    assert np.all(np.diff(with_inc) <= 1e-9)


def test_backward_compat_default_material_unchanged():
    # Default JointMaterial has slip_onset_W == 0 -> gate inert everywhere.
    mat = JointMaterial()
    assert mat.slip_onset_W == 0.0
    for w in (0.0, 10.0, 1e9):
        assert slip_onset_gate(SlowState(F_0=1.0, W_slip_acc=w), mat) == 1.0


def test_slip_onset_is_fittable():
    from bolt_analysis_studio.numerical.parameter_identifier import (
        PRESET_PARAMS, V2_PARAM_NAMES, jm_slip_onset_param)
    assert "slip_onset_W" in V2_PARAM_NAMES
    assert "slip_onset_W" in PRESET_PARAMS
    fp = jm_slip_onset_param()
    assert fp.name == "slip_onset_W"
    assert fp.target == "jm.slip_onset_W"
    assert fp.lo == 0.0 and fp.hi > 0.0
