"""Embedding state-based (forma geometrica exata) — spec 2026-07-02 §2.4."""
import numpy as np
import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, EmbeddingLoss, JointGeometry, JointMaterial,
    SlowState,
)

GEOM = JointGeometry()


def _iterate_embedding(mat, n_cycles, delta_emb0=0.0):
    """Aplica so o EmbeddingLoss.rate ciclo a ciclo (unit-level)."""
    state = SlowState(F_0=50e3, F_0_init=50e3, delta_emb=delta_emb0)
    mech = EmbeddingLoss()
    for n in range(1, n_cycles + 1):
        r = mech.rate(state, GEOM, mat, 0.0, np.pi / 2, 0.5, n)
        state.delta_emb += r["ds"]["delta_emb"]
    return state.delta_emb


def test_virgin_trajectory_matches_norton_closed_form_exactly():
    mat = JointMaterial()
    for n_check in (1, 10, 50, 150, 300):
        got = _iterate_embedding(mat, n_check)
        expected = mat.emb_depth * (1.0 - np.exp(-n_check / mat.N_emb))
        assert got == pytest.approx(expected, rel=1e-9), f"N={n_check}"


def test_emb_depth_is_the_asymptote_stage_b():
    # Estagio B: sem k_emb_scale — emb_depth JA e a assintota (a semantica do
    # tuner foi foldada nele). O shim traduz k_emb_scale=0.18 -> emb_depth*0.18.
    from bolt_analysis_studio.calibration.tuner_shim import translate_legacy_tuners
    base_emb = JointMaterial().emb_depth
    folded = translate_legacy_tuners({"k_emb_scale": 0.18}, warn=False)
    assert folded["emb_depth"] == pytest.approx(0.18 * base_emb)
    mat = JointMaterial(emb_depth=folded["emb_depth"])
    got = _iterate_embedding(mat, int(20 * mat.N_emb))
    assert got == pytest.approx(0.18 * base_emb, rel=1e-4)


def test_initial_embedding_frac_suppresses_embedding_loss():
    mat = JointMaterial()
    fresh = DynamicStiffnessAnalyzer(GEOM, mat, 50e3,
                                     loss_mechanisms=[EmbeddingLoss()])
    used = DynamicStiffnessAnalyzer(GEOM, mat, 50e3,
                                    loss_mechanisms=[EmbeddingLoss()],
                                    initial_embedding_frac=1.0)
    assert used.state.delta_emb == pytest.approx(mat.emb_depth, rel=1e-9)
    for _ in range(200):
        fresh.step_cycle(20e3, np.pi / 2, 0.5, delta_amp=0.5e-3)
        used.step_cycle(20e3, np.pi / 2, 0.5, delta_amp=0.5e-3)
    drop_fresh = 1.0 - fresh.state.F_0 / 50e3
    drop_used = 1.0 - used.state.F_0 / 50e3
    assert drop_fresh > 0.0
    assert drop_used < 0.05 * drop_fresh  # embedding ja consumido: quase nada


def test_default_frac_zero_is_backward_compatible():
    # Sem o novo arg, delta_emb parte de 0 e a assinatura antiga funciona
    # (initial_damage continua sendo o 5o argumento posicional).
    ana = DynamicStiffnessAnalyzer(GEOM, JointMaterial(), 50e3, None, 0.2)
    assert ana.state.D == pytest.approx(0.2)
    assert ana.state.delta_emb == 0.0


@pytest.mark.parametrize("frac", [-0.1, 1.5, 2.0])
def test_initial_embedding_frac_out_of_range_raises(frac):
    with pytest.raises(ValueError, match="initial_embedding_frac"):
        DynamicStiffnessAnalyzer(GEOM, JointMaterial(), 50e3,
                                 initial_embedding_frac=frac)


@pytest.mark.parametrize("dmg", [-0.5, 1.2])
def test_initial_damage_out_of_range_raises(dmg):
    with pytest.raises(ValueError, match="initial_damage"):
        DynamicStiffnessAnalyzer(GEOM, JointMaterial(), 50e3, initial_damage=dmg)


def test_boundary_fractions_accepted():
    # limites fechados [0, 1] sao validos (nao devem levantar)
    DynamicStiffnessAnalyzer(GEOM, JointMaterial(), 50e3,
                             initial_embedding_frac=1.0, initial_damage=1.0)
    DynamicStiffnessAnalyzer(GEOM, JointMaterial(), 50e3,
                             initial_embedding_frac=0.0, initial_damage=0.0)
