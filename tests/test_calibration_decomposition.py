import pytest
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import CycleSnapshot
from bolt_analysis_studio.calibration.segmentation import StageSegmentation
from bolt_analysis_studio.calibration.decomposition import MechanismDecomposition


def _snap(cycle, dF):
    return CycleSnapshot(cycle=cycle, F_0=0.0, delta_U_stored=0.0,
                         W_ext_cycle=0.0, W_diss_cycle=0.0, Phi_eff=0.0,
                         slip_fraction=0.0, per_mechanism={}, dF_0_by_mech=dF)


def test_shares_sum_to_one_and_dominant():
    seg = StageSegmentation(n_I=2, n_II=4, n_end=6)
    hist = [
        _snap(1, {"embedding": -8.0, "loosening": -2.0}),   # estagio I
        _snap(3, {"embedding": -1.0, "loosening": -9.0}),   # estagio II
        _snap(5, {"creep": -5.0}),                          # estagio III
    ]
    out = MechanismDecomposition.shares_per_segment(hist, seg)
    assert abs(sum(out["I"]["shares"].values()) - 1.0) < 1e-9
    assert out["I"]["dominant"] == "embedding"
    assert out["II"]["dominant"] == "loosening"
    assert out["III"]["dominant"] == "creep"


def test_empty_segment_is_none():
    seg = StageSegmentation(n_I=2, n_II=4, n_end=6)
    hist = [_snap(1, {"embedding": -8.0})]   # so estagio I tem dados
    out = MechanismDecomposition.shares_per_segment(hist, seg)
    assert out["II"] is None and out["III"] is None
