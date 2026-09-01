import pytest


def test_analysis_spec_transverse():
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.gui_bridge import analysis_spec_for
    rec = record("liu2025_M16_amp0p25")
    spec = analysis_spec_for(rec)
    assert spec.bolt_diameter_mm == 16.0 and spec.pitch_mm == 2.0
    assert spec.loading_type == "TRANSVERSE" and spec.control_mode == "displacement"
    assert spec.delta_amplitude_mm == rec.validation_case.transverse_displacement_mm
    assert spec.n_cycles == rec.validation_case.n_cycles
    assert spec.reference_csv_path.endswith("liu2025_M16_amp0p25.csv")


def test_analysis_spec_axial_force_mode():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.gui_bridge import analysis_spec_for
    rec = next(r for r in all_records() if r.family == "axial")
    spec = analysis_spec_for(rec)
    assert spec.loading_type == "AXIAL" and spec.control_mode == "force"
    assert spec.F_amplitude_N > 0


def test_geometry_overrides_match_runner_geometry():
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.gui_bridge import geometry_overrides_for
    from bolt_analysis_studio.validation.inputs import geometry_for_case, inputs_for
    rec = record("liu2025_M16_amp0p25")
    gov = geometry_overrides_for(rec)
    g = geometry_for_case(rec.validation_case,
                          grip_mm=inputs_for(rec.validation_case)["grip_mm"]["value"])
    for f in ("A_s", "L_eff", "d_2", "pitch", "r_bearing", "A_contact"):
        assert gov[f] == getattr(g, f)


def test_build_case_model_attaches_both_channels(qapp):
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.gui_bridge import build_case_model
    rec = record("liu2025_M16_amp0p25")
    model = build_case_model(rec)
    assert len(model.elements) > 0                       # cadeia com GROUND
    ov = model._v2_tuner_overrides
    assert ov["slip_onset_W"] == 250000.0                # material do runner (PR-9b)
    gov = model._v2_geometry_overrides
    assert abs(gov["L_eff"] - 0.040) < 1e-9              # grip 2.5d = 40 mm (SI)
    assert model.global_loading.F_preload == rec.validation_case.initial_preload_N


def test_build_case_model_other_family_raises(qapp):
    # familia 'other' removida do registry (2026-07-11) — guarda coberta
    # com record sintetico (defesa p/ imports futuros malformados)
    from bolt_analysis_studio.validation.case_registry import CaseRecord, all_records
    from bolt_analysis_studio.validation.gui_bridge import build_case_model
    base = all_records()[0]
    rec = CaseRecord(case_id="sintetico_other", name="s", source=base.source,
                     family="other", case_class="full_curve", caveats=[],
                     validation_case=base.validation_case, csv_path=base.csv_path,
                     apparatus_note_path=None, gallery_entry=None)
    with pytest.raises(ValueError):
        build_case_model(rec)
