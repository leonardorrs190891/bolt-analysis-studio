import json

from tests.test_user_cases import VALID, _write


def test_prefit_reads_emb_floor_and_fits_cbend(tmp_path, monkeypatch):
    from bolt_analysis_studio.validation import user_cases
    from bolt_analysis_studio.validation.prefit import prefit_user_case
    monkeypatch.setattr(user_cases, "USER_CASES_DIR", tmp_path / "uc")
    rec = user_cases.import_user_case(_write(tmp_path, VALID))
    block = prefit_user_case(rec, n_cap=400)
    ov = block["overrides"]
    assert ov["emb_depth"] > 0                     # lido da queda inicial
    assert "loose_arrest_floor" in ov              # lido do plato final
    assert "c_bend" in ov and ov["k_tr_mode"] == "bending"
    assert block["provenance"]["emb_depth"].startswith("data_implied")
    assert block["provenance"]["c_bend"] == "fitado-this-rig (unico DOF §4.42)"
    # gravado no JSON canonico
    jp = tmp_path / "uc" / f"{rec.case_id}.bascase.json"
    saved = json.loads(jp.read_text(encoding="utf-8"))
    assert saved["prefit"]["overrides"]["c_bend"] == ov["c_bend"]


def test_prefit_improves_or_matches_zero_fit(tmp_path, monkeypatch):
    from bolt_analysis_studio.validation import user_cases
    from bolt_analysis_studio.validation.prefit import prefit_user_case
    from bolt_analysis_studio.validation.runner import simulate_case
    monkeypatch.setattr(user_cases, "USER_CASES_DIR", tmp_path / "uc")
    rec = user_cases.import_user_case(_write(tmp_path, VALID))
    mae0 = simulate_case(rec, n_cap=400).mae       # zero-fit
    block = prefit_user_case(rec, n_cap=400)
    rec.validation_case._prefit_overrides = block["overrides"]
    mae1 = simulate_case(rec, n_cap=400).mae
    assert mae1 <= mae0 + 1e-9


def test_axial_prefit_reads_only(tmp_path, monkeypatch):
    from bolt_analysis_studio.validation import user_cases
    from bolt_analysis_studio.validation.prefit import prefit_user_case
    data = json.loads(json.dumps(VALID))
    data["name"] = "Ensaio axial teste"
    data["test"].update(loading_type="AXIAL", control_mode="force",
                        F_amplitude_N=10000.0, delta_amplitude_mm=None)
    monkeypatch.setattr(user_cases, "USER_CASES_DIR", tmp_path / "uc")
    rec = user_cases.import_user_case(_write(tmp_path, data, "ax.bascase.json"))
    block = prefit_user_case(rec, n_cap=400)
    assert "c_bend" not in block["overrides"]      # axial: nada fitado
    assert block["overrides"]["emb_depth"] > 0
