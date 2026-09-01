"""knowledge_base: o aprendizado das campanhas acessivel ao SOFTWARE."""
from bolt_analysis_studio.calibration import knowledge_base as kb
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
from bolt_analysis_studio.core.solver_worker import coerce_v2_overrides


def test_sources_and_configs():
    srcs = kb.adopted_sources()
    assert "LU_2024" in srcs and "LIU_2022_RET" in srcs and len(srcs) >= 11
    assert kb.adopted_config("LU_2024")["cfg"]["emb_load_frac"] == 0.40


def test_lessons_parse():
    L = kb.lessons()
    assert "L1" in L and "L13" in L and len(L) >= 12
    assert "Motosh" in L.get("L3", "")


def test_suggest_overrides_flow_to_engine():
    ov = kb.suggest_overrides("LU_2024")
    # valores da ADOCAO FINAL do LU (ponto R4, prereg excecao-elastica
    # 2026-07-31/08-01) — o pino acompanha a config adotada de proposito:
    # se uma adocao futura mudar os valores, ele acusa e e' atualizado no
    # MESMO commit da adocao.
    assert ov["emb_load_frac"] == 0.40 and ov["N_emb"] == 0.5
    out = coerce_v2_overrides(ov, JointMaterial.__dataclass_fields__)
    jm = JointMaterial(**out)               # constroi de ponta a ponta
    assert jm.k_ratchet == 0.003


def test_guard():
    assert kb.check_input("mu_thread", 0.15) is None
    assert "fora da banda" in (kb.check_input("mu_thread", 0.40) or "")
