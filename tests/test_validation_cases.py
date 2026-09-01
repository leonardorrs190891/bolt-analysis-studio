"""
Tests for ValidationCase data and ValidationCaseManager (5.3).

Verifies:
- All validation cases have required fields
- to_solver_config() returns expected keys
- validate_result() returns correct PASS/FAIL
- get_case_by_name() works
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest


def test_all_cases_have_required_fields():
    """Every validation case must have the required identification fields."""
    from bolt_analysis_studio.core.validation_cases import ValidationCaseManager
    required = [
        'name', 'description', 'source', 'reference',
        'bolt_diameter_mm', 'pitch_mm', 'initial_preload_N',
        'transverse_displacement_mm', 'n_cycles',
        'mu_initial', 'expected_final_preload_ratio',
    ]
    for case in ValidationCaseManager.get_all_cases():
        for field in required:
            assert hasattr(case, field), (
                f"Case '{case.name}' missing field '{field}'"
            )
            val = getattr(case, field)
            assert val is not None, (
                f"Case '{case.name}' field '{field}' is None"
            )


def test_to_solver_config_keys():
    """to_solver_config() must return all expected solver parameter keys."""
    from bolt_analysis_studio.core.validation_cases import ValidationCaseManager
    expected_keys = {
        'n_cycles', 'initial_preload', 'transverse_force',
        'bolt_diameter_mm', 'pitch_mm', 'mu_initial', 'lubricated',
    }
    for case in ValidationCaseManager.get_all_cases():
        cfg = case.to_solver_config()
        for key in expected_keys:
            assert key in cfg, (
                f"Case '{case.name}' to_solver_config() missing key '{key}'"
            )


def test_validate_result_pass():
    """validate_result() should return True when simulation matches expected."""
    from bolt_analysis_studio.core.validation_cases import ValidationCaseManager
    cases = ValidationCaseManager.get_all_cases()
    case = cases[0]  # Use first case
    # Simulate exact match
    vr = ValidationCaseManager.validate_result(
        case,
        final_preload_ratio=case.expected_final_preload_ratio,
        total_loosening_deg=case.expected_loosening_deg,
    )
    assert vr['overall_pass'] is True


def test_validate_result_fail():
    """validate_result() should return False when error is large."""
    from bolt_analysis_studio.core.validation_cases import ValidationCaseManager
    case = ValidationCaseManager.get_all_cases()[0]
    # Simulate completely wrong result (0% final preload)
    vr = ValidationCaseManager.validate_result(
        case,
        final_preload_ratio=0.0,
        total_loosening_deg=999.0,
    )
    assert vr['overall_pass'] is False


def test_get_case_by_name():
    """get_case_by_name() should return matching case or None."""
    from bolt_analysis_studio.core.validation_cases import ValidationCaseManager
    cases = ValidationCaseManager.get_all_cases()
    first_name = cases[0].name

    found = ValidationCaseManager.get_case_by_name(first_name)
    assert found is not None
    assert found.name == first_name

    not_found = ValidationCaseManager.get_case_by_name("NonExistentCase___")
    assert not_found is None


def test_get_case_names_length():
    """There should be at least 4 predefined validation cases."""
    from bolt_analysis_studio.core.validation_cases import ValidationCaseManager
    names = ValidationCaseManager.get_case_names()
    assert len(names) >= 4, f"Expected >= 4 cases, got {len(names)}"


def test_case_serialisation():
    """to_dict() should include all key fields."""
    from bolt_analysis_studio.core.validation_cases import ValidationCaseManager
    case = ValidationCaseManager.get_all_cases()[0]
    d = case.to_dict()
    assert "name" in d
    assert "expected_final_preload_ratio" in d
    assert d["bolt_diameter_mm"] > 0
    assert d["n_cycles"] > 0


def test_experimental_data_points():
    """All experimental data points should have valid cycle / preload_ratio."""
    from bolt_analysis_studio.core.validation_cases import ValidationCaseManager
    for case in ValidationCaseManager.get_all_cases():
        for dp in case.experimental_data:
            assert dp.cycles >= 0, (
                f"Case '{case.name}': data point has negative cycles"
            )
            # 1.10: dado digitalizado cru pode passar de 1.0 no inicio
            # (overshoot da celula normalizado em t=0; ex. Bauer rep3 1.0747)
            assert 0.0 <= dp.preload_ratio <= 1.10, (
                f"Case '{case.name}': data point preload_ratio "
                f"{dp.preload_ratio} out of range"
            )
