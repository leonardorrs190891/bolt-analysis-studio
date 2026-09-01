# -*- coding: utf-8 -*-
"""Estagio B Fase 2 — loader unico das constantes do bloco `shared`.

Gates: (1) load_shared_material le o canonico (C_creep ancorado 1.8667e-11,
W_conf_ref 7671, tudo chave valida de JointMaterial, emb_depth EXCLUIDO);
(2) caminho custom + degradacao graciosa; (3) o Run (_compute_v2_history)
constroi o material com as constantes do shared — "o bloco shared vira o que
a GUI le" — com overrides explicitos vencendo.
"""
import json

import pytest

from bolt_analysis_studio.calibration.profiles import (
    default_calibrations_path, load_shared_material)
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial


def test_loader_reads_canonical_shared():
    consts = load_shared_material()
    assert consts, "bloco shared canonico deveria existir no repo"
    assert consts["C_creep"] == pytest.approx(1.8667263000051723e-11)
    assert consts["W_conf_ref"] == pytest.approx(7671.206304040271)
    assert "emb_depth" not in consts          # input por junta (§1.3a)
    fields = JointMaterial.__dataclass_fields__
    assert all(k in fields for k in consts)   # JM-safe por construcao
    assert default_calibrations_path().exists()


def test_loader_graceful_on_missing(tmp_path):
    assert load_shared_material(tmp_path / "nao_existe.json") == {}
    p = tmp_path / "x.json"
    p.write_text(json.dumps({"schema": 2}), encoding="utf-8")
    assert load_shared_material(p) == {}      # sem bloco shared -> {}


def test_loader_filters_non_jm_keys(tmp_path):
    p = tmp_path / "x.json"
    p.write_text(json.dumps({"shared": {"constants": {
        "C_creep": 1e-11, "chave_estranha": 9, "emb_depth": 3e-5}}}),
        encoding="utf-8")
    out = load_shared_material(p)
    assert out == {"C_creep": 1e-11}


def test_run_material_uses_shared_constants():
    """O caminho do Run monta o material como o solver_worker (loader + driver
    + overrides vencem) — o C_creep do Run agora e o ANCORADO, nao o default."""
    conf = load_shared_material()
    conf.setdefault("W_conf_ref", 7671.0)
    conf.setdefault("conform_pressure_exp", 2.0)
    conf["conform_driver"] = "effective"
    conf["p_ref_conform"] = 5e8
    tuners = {"C_creep": 9e-12}               # override explicito do usuario
    mat = JointMaterial(**{**conf, **tuners})
    assert mat.C_creep == pytest.approx(9e-12)          # override vence
    mat2 = JointMaterial(**conf)
    assert mat2.C_creep == pytest.approx(1.8667e-11, rel=1e-3)  # shared no Run
    assert mat2.conform_driver == "effective"
    assert mat2.C_creep != JointMaterial(emb_depth=1e-6).C_creep  # nao e o default
