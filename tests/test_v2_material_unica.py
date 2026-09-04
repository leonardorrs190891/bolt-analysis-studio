"""Uma receita so' para o material do motor V2 (2026-09-03).

O Run montava o JointMaterial a partir do bloco `shared` canonico, do shim de
tuners legados e de um `p_ref_conform` calculado por Run. O otimizador de
parametros montava com `JointMaterial(**tuners)` — so' os overrides. Para o
MESMO modelo as duas curvas divergiam (5,2e-4 em F/F0 no LU2024, crescente com
o ciclo): pequeno demais para alguem notar, grande o bastante para o ajuste ser
medido contra uma fisica que nao e' a que roda depois.

`solver_worker.build_v2_material` e' a receita, agora unica. A extracao tinha
de ser de comportamento identico bit a bit — o Run e' o que gerou os numeros do
artigo — e os valores abaixo foram medidos ANTES dela.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import pytest                                                    # noqa: E402

# F/F0 no ultimo ciclo simulado, medidos em 2026-09-03 com o codigo ANTERIOR a
# extracao. Se um destes mudar, o motor de producao mudou — o que pode ser
# legitimo, mas nunca como efeito colateral de mexer na montagem do material.
CONGELADOS = {
    "lu2024_M8_fig18_amp0p5":              (99,  0.282296),
    "bauer2024_M12_fig8_test1":            (400, 0.950093),
    "caccese2009_tapered_45kN_rep1":       (400, 0.725238),
    "chu2026ti_D0p3mm_F0_49kN_test1":      (400, 0.984180),
    "eccles2010_fig8a_no_axial_baseline1": (400, 0.060096),
    "yang2021_fig2_typical":               (400, 0.691938),
}


def _historico(cid: str, n: int):
    from bolt_analysis_studio.core.solver_worker import (PreloadAnalysisConfig,
                                                         SolverWorker)
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.gui_bridge import build_case_model

    rec = record(cid)
    if rec is None:
        pytest.skip(f"{cid} nao esta' no registry")
    m = build_case_model(rec)
    w = SolverWorker()
    w._current_model = m
    cfg = PreloadAnalysisConfig()
    cfg.initial_preload = float(m.global_loading.F_preload)
    cfg.n_cycles = n
    return m, w._compute_v2_history(cfg, n)


@pytest.mark.parametrize("cid", sorted(CONGELADOS))
def test_o_run_continua_dando_o_mesmo_numero(cid, qapp):
    n, esperado = CONGELADOS[cid]
    _m, h = _historico(cid, n)
    assert h is not None, f"{cid} nao rodou"
    assert float(h["ratio"][-1]) == pytest.approx(esperado, abs=5e-7), (
        f"{cid}: o motor de producao mudou de resposta")


def test_a_receita_e_a_mesma_nos_dois_caminhos(qapp):
    """O invariante. Otimizador e Run tem de dar a MESMA curva."""
    import numpy as np
    from bolt_analysis_studio.numerical.parameter_identifier import (
        simulate_v2_curve)

    cid = "lu2024_M8_fig18_amp0p5"
    n = CONGELADOS[cid][0]
    m, h = _historico(cid, n)
    gl = m.global_loading
    _, sr = simulate_v2_curve(
        m, dict(getattr(m, "_v2_tuner_overrides", {}) or {}), n,
        str(getattr(gl, "control_mode", "displacement")),
        F0=float(gl.F_preload),
        F_amp=float(getattr(gl, "F_amplitude", 0.0) or 0.0),
        theta=np.pi / 2.0, freq=float(getattr(gl, "frequency", 1.0) or 1.0))
    prod = np.asarray(h["ratio"], float)
    k = min(len(prod), len(sr))
    assert np.max(np.abs(prod[:k] - sr[:k])) < 1e-9


def test_o_solver_nao_remonta_o_material_por_fora(qapp):
    """Guarda contra a reincidencia: se alguem reintroduzir a montagem no
    corpo do `_compute_v2_history`, a divergencia volta calada."""
    import inspect
    from bolt_analysis_studio.core import solver_worker

    corpo = inspect.getsource(solver_worker.SolverWorker._compute_v2_history)
    assert "build_v2_material" in corpo
    assert "load_shared_material" not in corpo, (
        "a receita voltou a ser montada dentro do _compute_v2_history")
    assert "p_ref_conform" not in corpo


def test_o_p_ref_depende_da_precarga_e_do_sobretorque(qapp):
    """`p_ref_conform` nao vem de arquivo nenhum: e' calculado por Run. Era
    exatamente o que faltava no material do otimizador."""
    from bolt_analysis_studio.core.solver_worker import build_v2_material

    nominal = build_v2_material({}, F0=50_000.0, A_contact=1e-4, pct_yield=70.0)
    sobre = build_v2_material({}, F0=50_000.0, A_contact=1e-4, pct_yield=90.0)
    assert nominal.p_ref_conform > sobre.p_ref_conform, (
        "sobretorque tem de reduzir p_ref e excitar mais o platô")
    assert build_v2_material({}, 50_000.0, 1e-4, 0.0).p_ref_conform == \
        pytest.approx(nominal.p_ref_conform), "pct<=0 cai no default de 70%"


def test_override_explicito_vence_o_bloco_compartilhado(qapp):
    from bolt_analysis_studio.core.solver_worker import build_v2_material

    base = build_v2_material({}, 50_000.0, 1e-4, 70.0)
    meu = build_v2_material({"W_conf_ref": 1234.0}, 50_000.0, 1e-4, 70.0)
    assert meu.W_conf_ref == pytest.approx(1234.0)
    assert base.W_conf_ref != pytest.approx(1234.0)


def test_chave_de_modo_sobrevive_a_montagem(qapp):
    """Nove chaves do JointMaterial sao modo (string/bool). Coagi-las a float
    derrubava o ajuste em todas as 210 configuracoes adotadas."""
    from bolt_analysis_studio.core.solver_worker import build_v2_material

    mat = build_v2_material({"conform_driver": "effective",
                             "creep_mode": "saturating",
                             "fatigue_enabled": True},
                            50_000.0, 1e-4, 70.0)
    assert mat.conform_driver == "effective"
    assert mat.creep_mode == "saturating"
    assert mat.fatigue_enabled is True
