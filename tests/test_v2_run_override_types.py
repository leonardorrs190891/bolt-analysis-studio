"""The Run's _v2_tuner_overrides coercion carries the validated V2 forms into the
Run with correct types (spec 2026-07-08 adoption). str stays str, bool stays bool,
numeric -> float; unknown keys dropped; defaults not turned on unless overridden."""
from bolt_analysis_studio.core.solver_worker import coerce_v2_overrides
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial

VALID = JointMaterial.__dataclass_fields__


def test_str_bool_float_flow_typed():
    ov = dict(slip_regime_mode="cattaneo_mindlin",   # str field
              loose_torsion_mode="bolt_torsion",      # str field
              fatigue_enabled=True,                    # bool field
              couple_famp_slip=True,                   # bool field
              slip_regime_sharpness=6.0,               # float field
              eta_loose=15,                            # int -> float
              bogus_key=123)                           # unknown -> dropped
    out = coerce_v2_overrides(ov, VALID)
    assert out["slip_regime_mode"] == "cattaneo_mindlin" and isinstance(out["slip_regime_mode"], str)
    assert out["loose_torsion_mode"] == "bolt_torsion"
    assert out["fatigue_enabled"] is True and isinstance(out["fatigue_enabled"], bool)
    assert out["couple_famp_slip"] is True
    assert out["slip_regime_sharpness"] == 6.0 and isinstance(out["slip_regime_sharpness"], float)
    assert out["eta_loose"] == 15.0 and isinstance(out["eta_loose"], float)
    assert "bogus_key" not in out


def test_forms_construct_jointmaterial():
    out = coerce_v2_overrides(dict(slip_regime_mode="cattaneo_mindlin",
                                   fatigue_enabled=True, slip_regime_sharpness=6.0), VALID)
    m = JointMaterial(**out)
    assert m.slip_regime_mode == "cattaneo_mindlin"
    assert m.fatigue_enabled is True
    assert m.slip_regime_sharpness == 6.0


def test_bool_false_stays_bool():
    out = coerce_v2_overrides(dict(fatigue_enabled=False), VALID)
    assert out["fatigue_enabled"] is False and isinstance(out["fatigue_enabled"], bool)


def test_non_dict_and_empty():
    assert coerce_v2_overrides(None, VALID) == {}
    assert coerce_v2_overrides({}, VALID) == {}
