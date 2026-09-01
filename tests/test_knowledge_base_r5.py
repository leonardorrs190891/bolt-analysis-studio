# tests/test_knowledge_base_r5.py
from bolt_analysis_studio.calibration import knowledge_base as kb


def test_wear_spec_anchor_thread_pair():
    a = kb.wear_spec_anchor("thread", "35CrMo-SCM435")
    assert abs(a["value"] - 8.34e-15) / 8.34e-15 < 1e-6
    assert a["unit"] == "1/Pa" and "Zhang" in a["source"]


def test_mu_thread_anchor_and_bound():
    assert kb.mu_thread_anchor("DLC")["value"] == 0.126
    b = kb.removal_energy_bound()
    assert b["lo"] < 5e3 < b["hi"]


def test_unknown_pair_raises_loud():
    import pytest
    with pytest.raises(KeyError):
        kb.wear_spec_anchor("thread", "inexistente")
