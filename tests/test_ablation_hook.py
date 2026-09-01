"""O gancho de ablacao do runner e' INERTE por default e so' age via BAS_ABLATION.

Existe para o estudo de ablacao do artigo (2026-08-28): congelar o laco de
rigidez (alpha_GW=0) e remover mecanismos um a um, SEM tocar nas configuracoes
adotadas. Tres invariantes:

1. sem a variavel de ambiente, `material_kwargs_for` e `_effective_overrides`
   devolvem exatamente o que devolviam (bit-identico) — a fisica canonica nao
   pode depender de um gancho de estudo;
2. com `overrides`, o valor entra POR CIMA de tudo (per-rig e per-curva);
3. com `drop`, o mecanismo some da lista `ana.losses` do analyzer e nao
   participa mais da simulacao.
"""
import json
import os

import pytest

from bolt_analysis_studio.validation import runner as rn
from bolt_analysis_studio.validation.case_registry import all_records


@pytest.fixture
def rec():
    recs = [r for r in all_records() if r.source == "LU_2024"]
    assert recs, "LU_2024 sumiu do registry?"
    return recs[0]


@pytest.fixture
def sem_ambiente(monkeypatch):
    monkeypatch.delenv(rn._ABL_ENV, raising=False)


def test_inerte_sem_variavel(rec, sem_ambiente):
    inp = rn.inputs_for(rec.validation_case)
    a = rn.material_kwargs_for(rec, inp)
    b = rn.material_kwargs_for(rec, inp)
    assert a == b
    assert "alpha_GW" not in (rn._ablacao().get("overrides") or {})
    consts, _ = rn.frozen_constants()
    assert "_ablation" not in rn._effective_overrides(rec, consts)


def test_override_entra_por_cima(rec, monkeypatch):
    monkeypatch.setenv(rn._ABL_ENV, json.dumps({"overrides": {"alpha_GW": 0.0}}))
    inp = rn.inputs_for(rec.validation_case)
    kw = rn.material_kwargs_for(rec, inp)
    assert kw["alpha_GW"] == 0.0
    consts, _ = rn.frozen_constants()
    ov = rn._effective_overrides(rec, consts)
    assert ov["alpha_GW"] == 0.0 and ov["_ablation"]["overrides"]["alpha_GW"] == 0.0


def test_drop_remove_o_mecanismo(monkeypatch):
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer, JointMaterial)
    from bolt_analysis_studio.validation.inputs import geometry_for
    geom = geometry_for("M16x2.0", grip_mm=40.0)
    monkeypatch.setenv(rn._ABL_ENV, json.dumps({"drop": ["rotational_loosening"]}))
    ana = rn._aplica_ablacao(DynamicStiffnessAnalyzer(geom, JointMaterial(), 50e3))
    nomes = [m.name for m in ana.losses]
    assert "rotational_loosening" not in nomes and "embedding" in nomes
    monkeypatch.delenv(rn._ABL_ENV)
    ana2 = rn._aplica_ablacao(DynamicStiffnessAnalyzer(geom, JointMaterial(), 50e3))
    assert "rotational_loosening" in [m.name for m in ana2.losses]


def _roda(geom, mat, F0, n=300, open_loop=False):
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    ana.open_loop_rates = open_loop
    for _ in range(n):
        ana.step_cycle(0.0, 1.5707963267948966, 1.0, delta_amp=0.5e-3)
    return ana


def test_open_loop_default_off_e_estado_identico():
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer, JointMaterial)
    from bolt_analysis_studio.validation.inputs import geometry_for
    geom = geometry_for("M16x2.0", grip_mm=40.0)
    ana = DynamicStiffnessAnalyzer(geom, JointMaterial(), 50e3)
    assert ana.open_loop_rates is False
    assert ana._rates_state() is ana.state          # mesmo objeto, sem copia


def test_open_loop_congela_F0_nas_taxas_e_muda_a_trajetoria(monkeypatch):
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer, JointMaterial)
    from bolt_analysis_studio.validation.inputs import geometry_for
    geom = geometry_for("M16x2.0", grip_mm=40.0)
    mat = JointMaterial()
    fechado = _roda(geom, mat, 50e3)
    aberto = _roda(geom, mat, 50e3, open_loop=True)
    assert aberto.state.F_0 < aberto.state.F_0_init       # a pre-carga integra
    assert aberto._rates_state().F_0 == aberto.state.F_0_init   # mas as taxas veem F_0_init
    assert abs(fechado.state.F_0 - aberto.state.F_0) > 1.0      # trajetorias distintas
    # o gancho do runner liga o modo pela variavel de ambiente
    monkeypatch.setenv(rn._ABL_ENV, json.dumps({"open_loop": True}))
    ana = rn._aplica_ablacao(DynamicStiffnessAnalyzer(geom, mat, 50e3))
    assert ana.open_loop_rates is True
