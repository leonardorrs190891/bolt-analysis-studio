"""Rodada 5 wiring (fatia 7, plano L1-L7): Zhang 2018 (Wear) + Zhang 2019
(EFA) -- the thread-flank fretting-wear experiment+FE-companion pair (L1
target: preload loss with ZERO measured nut rotation) -- and Liu 2020 (Wear)
-- the confound-free preload x amplitude x coating (zinc/DLC) sweep -- as
new ValidationCases. Mirrors the R4 ingestion pattern (PR-26): import-time
construction from digitized CSVs (degrades without raising if a file is
missing), counts + one CSV-grounded spot-check per source, plus the
Liu2020-specific percent->fraction conversion (its CSVs plot R_F in
PERCENT, header `x,y`, not the usual `cycle,F_over_F0`).

Style mirrors tests/test_case_study_models.py (plain functions, no fixtures
beyond what's needed -- no Qt here since these tests don't touch the MSD
builder, only the case registry/data).
"""

import csv
import os

import pytest

from bolt_analysis_studio.core.validation_cases import (
    ValidationCaseManager, ValidationSource,
)

_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def _read_csv_last_row(rel_path, y_key):
    """Read a digitized CSV (repo-relative path) and return (x_last, y_last)
    straight off its own last row, resolving the y column by name
    (`F_over_F0` for zhang18/zhang19, `y` for the Liu2020 percent curves)."""
    abs_path = os.path.join(_REPO_ROOT, rel_path)
    with open(abs_path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"empty or unreadable CSV: {rel_path}"
    xkey = "cycle" if "cycle" in rows[0] else "x"
    last = rows[-1]
    return float(last[xkey]), float(last[y_key])


def test_source_counts_exact():
    """Case selection per apparatus_notes/{zhang,liu2020}.md: only
    EXPERIMENTAL preload-loss curves (F/F0 or R_F vs cycle) are wired.
    Excluded (documented in the code comment above the Rodada 5 block):
    wear-DEPTH profiles (zhang19 fig6/12), the single-cycle wear-vs-angle
    snapshot (zhang18 fig19), the exact-checkpoint tables (used only to
    validate digitization, never wired as a case anywhere in this file),
    and zhang19 fig16 (Stage-II curve REBASED to its own onset -- a
    different x-axis convention than every other curve, redundant with
    fig4 which already covers the same test groups end to end)."""
    zhang18 = ValidationCaseManager.get_cases_by_source(ValidationSource.ZHANG_2018)
    zhang19 = ValidationCaseManager.get_cases_by_source(ValidationSource.ZHANG_2019)
    liu2020 = ValidationCaseManager.get_cases_by_source(ValidationSource.LIU_2020_WEAR)
    assert len(zhang18) == 9   # Fig.2 tests1-4 + Fig.13 3 preloads + Fig.16 locker on/off
    assert len(zhang19) == 4   # Fig.4: 4 interrupted-test groups (1e3/1e4/1e5/2e5 cyc)
    assert len(liu2020) == 9   # Fig.5b 3 preloads + Fig.9 4 amplitudes + Fig.15 2 DLC


def test_zhang2018_spot_check():
    """Zhang2018 M12 P0=20kN (Fig.13 preload-sweep curve, mid-point of the
    14/20/26kN sweep): F0/n_cycles/final ratio must trace back exactly to
    the digitized CSV's own last row, not a hand-typed number."""
    case = ValidationCaseManager.get_case_by_name("Zhang2018 M12 P0=20kN")
    assert case is not None
    assert case.source == ValidationSource.ZHANG_2018
    assert case.bolt_size == "M12x1.75"
    assert case.initial_preload_N == pytest.approx(20000.0)
    assert case.transverse_displacement_mm == pytest.approx(0.25)
    assert case.frequency_Hz == pytest.approx(10.0)
    x_last, y_last = _read_csv_last_row(case.reference_csv_path, "F_over_F0")
    assert case.n_cycles == int(x_last)
    assert case.expected_final_preload_ratio == pytest.approx(y_last, abs=1e-6)


def test_zhang2019_spot_check():
    """Zhang2019 M12 2e5cyc Test10-12 (Fig.4, the longest-duration group):
    same CSV-grounded spot-check, plus the paper's own stated pct_yield
    (10 kN = 95 MPa = 13.5% of the measured Sy=705 MPa -- read, not fit)."""
    case = ValidationCaseManager.get_case_by_name("Zhang2019 M12 2e5cyc Test10-12")
    assert case is not None
    assert case.source == ValidationSource.ZHANG_2019
    assert case.initial_preload_N == pytest.approx(10000.0)
    assert case.preload_percent_yield == pytest.approx(13.5)
    x_last, y_last = _read_csv_last_row(case.reference_csv_path, "F_over_F0")
    assert case.n_cycles == int(x_last)
    assert case.expected_final_preload_ratio == pytest.approx(y_last, abs=1e-6)


def test_liu2020_percent_conversion_spot_check():
    """Liu2020 CSVs plot R_F in PERCENT (0-100, anchored at `0,100.0`); the
    loader must divide by 100 so the case ends up with fraction-scale ratio
    fields consistent with every other ValidationCase in the registry.
    Uses the steepest curve (A_F=0.4mm, the fatigue-crack-affected tail) so
    a missed /100 would be unmistakable (would read as ~83 instead of ~0.83)."""
    case = ValidationCaseManager.get_case_by_name("Liu2020 zinc 0.4mm @18kN")
    assert case is not None
    assert case.source == ValidationSource.LIU_2020_WEAR
    x_last, y_last_pct = _read_csv_last_row(case.reference_csv_path, "y")
    assert y_last_pct > 1.5, "sanity: raw CSV column really is 0-100 percent"
    assert case.n_cycles == int(x_last)
    assert case.expected_final_preload_ratio == pytest.approx(
        y_last_pct / 100.0, abs=1e-6)
    assert case.expected_final_preload_ratio < 0.90  # would be >>1 unconverted


def test_liu2020_all_ratios_are_fractions_not_percent():
    """Every Liu2020 case (not just the one spot-checked above) must have
    both its downsampled experimental_data points and its final-ratio field
    in (0, 1.05] -- i.e. the percent->fraction conversion applied uniformly
    across the whole source, not just at the digitization step."""
    cases = ValidationCaseManager.get_cases_by_source(ValidationSource.LIU_2020_WEAR)
    assert cases
    for c in cases:
        assert c.experimental_data, f"{c.name}: no experimental_data points"
        for pt in c.experimental_data:
            assert 0.0 < pt.preload_ratio <= 1.05, (c.name, pt.cycles, pt.preload_ratio)
        assert 0.0 < c.expected_final_preload_ratio <= 1.05, c.name


def test_liu2020_dlc_vs_zinc_friction_provenance():
    """L6 provenance pair, matched rig/geometry (Liu2020 Table 2, also
    anchored in New_Theory/r5_anchors.json's mu_thread block): zinc
    mu_thread=0.150, DLC=0.126 (a measured 16% reduction)."""
    zinc = ValidationCaseManager.get_case_by_name("Liu2020 zinc P0=18kN")
    dlc = ValidationCaseManager.get_case_by_name("Liu2020 DLC P0=18kN")
    assert zinc is not None and dlc is not None
    assert zinc.mu_initial == pytest.approx(0.150)
    assert dlc.mu_initial == pytest.approx(0.126)
    assert dlc.mu_initial < zinc.mu_initial


def test_registry_manager_integration():
    """get_cases_by_source() must surface the new sources through the same
    ValidationCaseManager API every other source uses, and each case must
    also flow through get_all_cases()/get_case_names() (no side registry)."""
    all_cases = ValidationCaseManager.get_all_cases()
    all_names = ValidationCaseManager.get_case_names()
    for source, expected_n in ((ValidationSource.ZHANG_2018, 9),
                               (ValidationSource.ZHANG_2019, 4),
                               (ValidationSource.LIU_2020_WEAR, 9)):
        cases = ValidationCaseManager.get_cases_by_source(source)
        assert len(cases) == expected_n, source
        for c in cases:
            assert c in all_cases
            assert c.name in all_names
            assert c.source == source


def test_new_sources_enter_master_registry():
    """The new sources must also surface through the master validation
    registry (src/.../validation/case_registry.py), the module the
    "report mestre" iterates over -- classified as family='transverse'
    (all carry a known transverse_displacement_mm) and case_class=
    'full_curve' (a real digitized CSV backs every case), same as any
    other digitized transverse source (e.g. LIU_2025, KARLSEN_2022)."""
    from bolt_analysis_studio.validation.case_registry import all_records
    recs = all_records()
    for source_name, expected_n in (("ZHANG_2018", 9), ("ZHANG_2019", 4),
                                    ("LIU_2020_WEAR", 9)):
        matches = [r for r in recs if r.source == source_name]
        assert len(matches) == expected_n, source_name
        for r in matches:
            assert r.case_class == "full_curve", (source_name, r.case_id)
            assert r.family == "transverse", (source_name, r.case_id)


def test_zero_rotation_caveat_documented():
    """Both Zhang papers' headline finding is ZERO measured nut rotation --
    the loss is entirely thread-flank wear, not rotational loosening; this
    is the whole reason the pair targets L1. Regression check that the
    caveat survives in the notes for every wired case of both sources."""
    cases = (ValidationCaseManager.get_cases_by_source(ValidationSource.ZHANG_2018)
             + ValidationCaseManager.get_cases_by_source(ValidationSource.ZHANG_2019))
    assert len(cases) == 13
    for c in cases:
        assert "rotac" in c.notes.lower(), c.name
