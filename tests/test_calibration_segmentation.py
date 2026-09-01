import numpy as np
import pytest
from bolt_analysis_studio.calibration.segmentation import Stage, StageSegmentation


def test_segments_cover_range_no_overlap():
    seg = StageSegmentation(n_I=100, n_II=1000, n_end=2500)
    assert seg.segment_of(0) == "I"
    assert seg.segment_of(99) == "I"
    assert seg.segment_of(100) == "II"      # fronteira pertence ao proximo
    assert seg.segment_of(999) == "II"
    assert seg.segment_of(1000) == "III"
    assert seg.segment_of(2500) == "III"    # n_end inclusivo
    assert [s.name for s in seg.stages] == ["I", "II", "III"]


def test_owned_tuners():
    seg = StageSegmentation(n_I=100, n_II=1000, n_end=2500)
    owners = {s.name: s.owned_tuners for s in seg.stages}
    assert owners["I"] == ["k_emb_scale"]
    assert owners["III"] == ["k_creep_scale"]
    assert "k_loose_scale_tr" in owners["II"]
    assert "k_damage_scale" in owners["II"]


def test_mae_per_segment_zero_when_equal():
    seg = StageSegmentation(n_I=100, n_II=1000, n_end=2500)
    sim_N = np.arange(0, 2501)
    sim_ratio = np.linspace(1.0, 0.2, 2501)
    ref_N = np.array([50, 500, 2000])
    ref_ratio = np.interp(ref_N, sim_N, sim_ratio)
    mae = seg.mae_per_segment(sim_N, sim_ratio, ref_N, ref_ratio)
    assert mae["I"] < 1e-9 and mae["II"] < 1e-9 and mae["III"] < 1e-9


def test_mae_per_segment_known_offset_and_empty():
    seg = StageSegmentation(n_I=100, n_II=1000, n_end=2500)
    sim_N = np.arange(0, 2501)
    sim_ratio = np.full(2501, 0.5)
    ref_N = np.array([50, 2000])           # nada na janela II
    ref_ratio = np.array([0.6, 0.4])       # offset 0.1 em ambas
    mae = seg.mae_per_segment(sim_N, sim_ratio, ref_N, ref_ratio)
    assert abs(mae["I"] - 0.1) < 1e-9
    assert mae["II"] is None               # sem pontos de referencia
    assert abs(mae["III"] - 0.1) < 1e-9
