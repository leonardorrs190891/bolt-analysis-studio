"""
Tests for AnalysisAudit trail (9.2).

Verifies that:
- AnalysisAudit serialises to/from dict correctly
- AnalysisResult embeds an audit after serialisation round-trip
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from datetime import datetime


def test_analysis_audit_fields():
    """AnalysisAudit stores all expected fields."""
    from bolt_analysis_studio.core.app_state import AnalysisAudit
    audit = AnalysisAudit(
        run_id="abc12345",
        timestamp_start="2026-01-01T10:00:00",
        timestamp_end="2026-01-01T10:00:05",
        duration_s=5.0,
        analysis_type="coupled_loosening",
        method="rk4",
        n_cycles=2000,
        n_dof=6,
        n_elements=5,
        solver_version="4.0",
        preflight_warnings=["Resonance at 12.5 Hz"],
    )
    assert audit.run_id == "abc12345"
    assert audit.duration_s == 5.0
    assert audit.n_cycles == 2000
    assert len(audit.preflight_warnings) == 1


def test_analysis_audit_serialisation():
    """AnalysisAudit round-trips through to_dict/from_dict."""
    from bolt_analysis_studio.core.app_state import AnalysisAudit
    original = AnalysisAudit(
        run_id="test01",
        duration_s=12.3,
        analysis_type="all",
        n_dof=10,
        preflight_warnings=["warn1", "warn2"],
    )
    data = original.to_dict()
    restored = AnalysisAudit.from_dict(data)

    assert restored.run_id == original.run_id
    assert restored.duration_s == original.duration_s
    assert restored.analysis_type == original.analysis_type
    assert restored.n_dof == original.n_dof
    assert restored.preflight_warnings == original.preflight_warnings


def test_analysis_result_audit_round_trip():
    """AnalysisResult preserves audit through to_dict/from_dict."""
    from bolt_analysis_studio.core.app_state import AnalysisResult, AnalysisAudit
    result = AnalysisResult(
        analysis_type="coupled_loosening",
        started="2026-01-01T10:00:00",
        completed="2026-01-01T10:00:10",
    )
    result.audit = AnalysisAudit(run_id="xyz9", duration_s=10.0, n_elements=3)

    data = result.to_dict()
    assert "audit" in data
    assert data["audit"]["run_id"] == "xyz9"

    restored = AnalysisResult.from_dict(data)
    assert restored.audit is not None
    assert restored.audit.run_id == "xyz9"
    assert restored.audit.duration_s == 10.0


def test_analysis_result_without_audit():
    """AnalysisResult without audit handles missing key gracefully."""
    from bolt_analysis_studio.core.app_state import AnalysisResult
    data = {
        "analysis_type": "modal",
        "started": "",
        "completed": "",
        # 'audit' key intentionally absent
    }
    result = AnalysisResult.from_dict(data)
    assert result.audit is None
