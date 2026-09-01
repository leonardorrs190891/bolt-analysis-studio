"""Every case study must populate the MSD builder with a real element model.

Most literature validation cases (Jiang/Junker/Nassar/Yang/...) ship reference
data only, no bundled .msd. The validation-suite "Load to MSD Builder" path must
synthesise a model from the case geometry so the builder is never left empty.
Regression for: "os case studies muitos não tem a representação no MSD builder".
"""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="module")
def qapp():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _all_cases():
    from bolt_analysis_studio.core.validation_cases import ValidationCaseManager
    return ValidationCaseManager.get_all_cases()


def test_every_case_synthesises_nonempty_model(qapp):
    """_build_model_from_case yields a populated, runnable model for any case."""
    from bolt_analysis_studio.gui.msd_builder import MSDBuilderWindow
    # The method does not touch instance state, so a bare instance is enough.
    bw = MSDBuilderWindow.__new__(MSDBuilderWindow)

    from bolt_analysis_studio.core.models.element import ElementType

    cases = _all_cases()
    assert cases, "no validation cases registered"
    for case in cases:
        model = bw._build_model_from_case(case)
        elems = getattr(model, "elements", None) or []
        assert len(elems) > 0, f"{case.name}: synthesised model is empty"
        # Must carry a ground/boundary anchor, else matrix-assembly validation
        # fails with "No ground element defined".
        assert any(e.type == ElementType.GROUND for e in elems), \
            f"{case.name}: synthesised model has no GROUND element"
        if hasattr(model, "validate"):
            ok, msgs = model.validate()
            errors = [m for m in msgs if m.startswith("ERROR")]
            assert ok, f"{case.name}: validation failed: {errors}"
        # Loading carries the case's measured values, not wizard defaults.
        assert model.global_loading.F_preload == pytest.approx(
            float(case.initial_preload_N)), f"{case.name}: preload not applied"
        assert model.mu_initial == pytest.approx(float(case.mu_initial))


def test_literature_cases_have_no_bundled_msd(qapp):
    """Confirms the cases this fix targets actually lack a .msd (else the
    synthesis path would never run for them)."""
    literature = [c for c in _all_cases()
                  if not (getattr(c, "msd_model_path", "") or "")]
    # At least the 8 classic literature cases rely on synthesis.
    assert len(literature) >= 8
    for c in literature:
        model_path = getattr(c, "msd_model_path", "") or ""
        assert model_path == "", f"{c.name} unexpectedly bundles a .msd"


def test_bundled_msd_cases_load_from_file(qapp):
    """UFU cases ship a .msd whose file exists and parses to a real model."""
    import json
    from bolt_analysis_studio.core.models.model import MSDModel

    repo_root = os.path.normpath(
        os.path.join(os.path.dirname(__file__), ".."))
    bundled = [c for c in _all_cases()
               if (getattr(c, "msd_model_path", "") or "")]
    assert bundled, "expected at least the UFU cases to bundle a .msd"
    for c in bundled:
        abs_path = os.path.join(repo_root, c.msd_model_path)
        assert os.path.isfile(abs_path), f"{c.name}: {abs_path} missing"
        with open(abs_path, encoding="utf-8") as f:
            model = MSDModel.from_dict(json.load(f))
        assert len(getattr(model, "elements", []) or []) > 0
