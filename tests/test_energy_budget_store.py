"""O balanço de energia do engine é PERSISTIDO no store (2026-08-28).

Dívida declarada no anexo do artigo (§10.1: "the conservation residual is
available from the engine, and it is a known gap that it is not yet persisted
in the result store") e resolvida a pedido do professor. Três invariantes:

1. `CaseResult.energy_budget` faz round-trip por `to_dict`/`from_dict` e um
   store ANTIGO (sem o campo) lê como `None`, nunca quebra.
2. `runner._energy_budget(ana)` devolve floats NATIVOS (o `json.dump` do batch
   morre com `np.float64`, incidente 2026-07-21 do `l7_check`) e o resíduo
   relativo é o resíduo dividido pelo MAIOR termo do balanço — em creep puro
   `W_diss` é ~0 e dividir só por ele explodiria.
3. Numa corrida curta do engine o balanço fecha: |resíduo| ≪ termos.
"""
import math

from bolt_analysis_studio.validation import runner as rn
from bolt_analysis_studio.validation.runner import CaseResult


def test_round_trip_e_store_antigo():
    r = CaseResult(case_id="x", ok=True, energy_budget={"W_ext_J": 1.0,
                                                        "dU_J": -2.0,
                                                        "W_diss_J": 3.0,
                                                        "residual_J": 0.0,
                                                        "residual_rel": 0.0})
    d = r.to_dict()
    assert d["energy_budget"]["W_diss_J"] == 3.0
    r2 = CaseResult.from_dict(d)
    assert r2.energy_budget == r.energy_budget
    d.pop("energy_budget")                       # store anterior a 2026-08-28
    assert CaseResult.from_dict(d).energy_budget is None


def _analyzer_curto(n=200):
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer, JointMaterial)
    from bolt_analysis_studio.validation.inputs import geometry_for
    geom = geometry_for("M16x2.0", grip_mm=40.0)
    ana = DynamicStiffnessAnalyzer(geom, JointMaterial(), 50e3)
    for _ in range(n):
        ana.step_cycle(F_amp=0.0, theta_load=0.0, freq=12.5, delta_amp=0.5e-3)
    return ana


def test_tipos_nativos_e_residuo_relativo():
    eb = rn._energy_budget(_analyzer_curto())
    assert set(eb) == {"W_ext_J", "dU_J", "W_diss_J", "residual_J",
                       "residual_rel"}
    for k, v in eb.items():
        assert type(v) is float, (k, type(v))     # nativo, nao np.float64
        assert math.isfinite(v), (k, v)
    escala = max(abs(eb["W_diss_J"]), abs(eb["dU_J"]))
    assert eb["residual_rel"] == eb["residual_J"] / escala


def test_o_balanco_fecha_na_corrida_curta():
    eb = rn._energy_budget(_analyzer_curto())
    # a junta do §3.2 dissipa milhares de joules em wear; o residuo medido
    # e' O(1e-4) relativo — a barra e' 100x mais frouxa que o medido, e ainda
    # assim pega um bucket que deixe de ser somado.
    assert abs(eb["residual_rel"]) < 1e-2, eb
    assert eb["W_diss_J"] > 0.0


def test_liberacao_exata_fecha_creep_puro():
    """dE exato (2026-08-31): num run de creep PURO o residuo de conservacao
    e' zero por construcao — a dissipacao contabilizada e' a liberacao exata
    de energia interna, incluida a parcela da mola do joint."""
    import numpy as np
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer, JointMaterial)
    from bolt_analysis_studio.validation.inputs import geometry_for
    geom = geometry_for("M16x2.0", grip_mm=40.0)
    mat = JointMaterial(emb_depth=0.0, K_archard=0.0, k_wear_spec=0.0,
                        tr_loose_gain=0.0, C_creep=5e-11)
    ana = DynamicStiffnessAnalyzer(geom, mat, 50e3)
    for _ in range(5000):
        ana.step_cycle(0.0, np.pi / 2, 1.0, delta_amp=0.0)
    E = ana.energy
    assert E.U_released > 0.1                       # o run de fato liberou energia
    assert abs(E.conservation_residual) < 1e-9 * max(E.W_diss_total, 1.0)


def test_liberacao_exata_embedding_puro():
    import numpy as np
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer, JointMaterial)
    from bolt_analysis_studio.validation.inputs import geometry_for
    geom = geometry_for("M16x2.0", grip_mm=40.0)
    mat = JointMaterial(emb_depth=30e-6, C_creep=0.0, K_archard=0.0,
                        k_wear_spec=0.0, tr_loose_gain=0.0)
    ana = DynamicStiffnessAnalyzer(geom, mat, 50e3)
    for _ in range(2000):
        ana.step_cycle(0.0, np.pi / 2, 1.0, delta_amp=0.0)
    E = ana.energy
    assert E.U_released > 0.05
    assert abs(E.conservation_residual) < 1e-9 * max(E.W_diss_total, 1.0)
