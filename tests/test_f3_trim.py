# -*- coding: utf-8 -*-
"""F3 trim per-caso (prereg 2026-07-21): janela de métrica via cfg adotado.

Contrato: sem a chave `trim_n_max` → métrica IDÊNTICA (bit) à de sempre;
trim maior que a curva → idêntica também; trim pequeno → métrica computada
só em N<=trim (maxerr_at dentro da janela). Sim/plot seguem inteiros.
Caso rápido (creep Qin, ~segundos) com sandbox BAS_ADOPTED_CONFIGS.
"""
import io
import json
import os
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CID = "qin2024acm_25C_i0pct"
FONTE_GRUPO = "QIN_2024"


def _sim_com_trim(trim):
    src = ROOT / "New_Theory/adopted_configs.json"
    d = json.loads(io.open(src, encoding="utf-8").read())
    g = d["sources"].setdefault(FONTE_GRUPO, {"pack": "PACK", "cfg": {}})
    if trim is not None:
        g["cfg"]["trim_n_max"] = trim
    fd, p = tempfile.mkstemp(suffix=".json", prefix="trimtest_")
    with io.open(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False))
    old = os.environ.get("BAS_ADOPTED_CONFIGS")
    os.environ["BAS_ADOPTED_CONFIGS"] = p
    try:
        from bolt_analysis_studio.validation.case_registry import record
        from bolt_analysis_studio.validation.runner import simulate_case
        rec = record(CID)
        if rec is None:
            pytest.skip("caso Qin não registrado neste ambiente")
        return simulate_case(rec, now="trim-test")
    finally:
        if old is None:
            os.environ.pop("BAS_ADOPTED_CONFIGS", None)
        else:
            os.environ["BAS_ADOPTED_CONFIGS"] = old
        try:
            os.unlink(p)
        except OSError:
            pass


def test_trim_contrato():
    base = _sim_com_trim(None)
    assert base.ok and base.mae is not None
    grande = _sim_com_trim(1e12)             # janela >= curva: idêntico
    assert grande.mae == base.mae and grande.maxerr == base.maxerr
    pequeno = _sim_com_trim(max(2.0, base.cycles[-1] * 0.3))
    assert pequeno.ok and pequeno.mae is not None
    assert pequeno.maxerr_at <= base.cycles[-1] * 0.3 + 1e-9
    assert pequeno.config_used.get("trim_n_max") is not None
    assert base.config_used.get("trim_n_max") is None
