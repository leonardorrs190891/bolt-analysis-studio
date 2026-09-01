"""Validacao da conformacao (spec 2026-07-04 §9). Helpers puros."""
import sys
from pathlib import Path

import pytest  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "New_Theory"))
sys.path.insert(0, str(ROOT / "src"))

from conformation_fit import (  # noqa: E402
    RESOLVE_MAE, PERSIST_MAE, build_conformation_config,
    build_conformation_config_effective, build_conformation_config_effective_fitn,
    build_conformation_config_fitn, classify_conformation_verdict,
)


def _maes(nova, reusada, sobretorque, reaperto):
    return {"nova": nova, "reusada": reusada,
            "sobretorque": sobretorque, "reaperto": reaperto}


def test_config_has_conformation_constants_fixed_n2():
    cfg = build_conformation_config(n_cycles=300)
    assert cfg.priors["conform_pressure_exp"] == 2.0
    assert cfg.priors["p_ref_conform"] == 5.0e8
    assert cfg.priors["W_conf_ref"] > 0.0
    assert "W_conf_ref" in cfg.bounds                  # fitavel
    assert "conform_pressure_exp" not in cfg.bounds    # fixo (nao candidato)


def test_config_fitn_frees_n_in_preregistered_range():
    """Robustez strand 1: o config --fit-n liberta n em [0.5,4.0] e herda o resto."""
    cfg = build_conformation_config_fitn(n_cycles=300)
    assert "conform_pressure_exp" in cfg.bounds        # agora candidato fitavel
    assert cfg.bounds["conform_pressure_exp"] == (0.5, 4.0)
    assert "W_conf_ref" in cfg.bounds                  # segue fitavel (herdado)
    assert cfg.priors["conform_pressure_exp"] == 2.0   # start/prior ainda 2.0
    assert cfg.priors["p_ref_conform"] == 5.0e8        # p_ref segue fixo


def test_config_effective_selects_self_limiting_driver():
    """build_conformation_config_effective liga o driver 'effective' e herda o
    resto (n=2 fixo, W_conf_ref fitavel)."""
    assert build_conformation_config(n_cycles=50).conform_driver == "raw"
    cfg = build_conformation_config_effective(n_cycles=50)
    assert cfg.conform_driver == "effective"
    assert "W_conf_ref" in cfg.bounds                   # segue fitavel
    assert "conform_pressure_exp" not in cfg.bounds     # n segue fixo
    assert cfg.priors["conform_pressure_exp"] == 2.0


def test_config_effective_fitn_frees_n_and_keeps_effective_driver():
    """fit-n no driver effective: n livre em [0.5,4.0] E driver segue effective
    (testa se a auto-atenuacao tira o n do teto que o raw railou)."""
    cfg = build_conformation_config_effective_fitn(n_cycles=50)
    assert cfg.conform_driver == "effective"
    assert cfg.bounds["conform_pressure_exp"] == (0.5, 4.0)


def test_verdict_resolved():
    base = _maes(0.076, 0.059, 0.135, 0.045)
    treat = _maes(0.078, 0.060, 0.030, 0.046)   # sob cai, outros ~iguais
    v = classify_conformation_verdict(base, treat, base_resid=0.3, treat_resid=0.3)
    assert v["verdict"] == "RESOLVED"


def test_verdict_falsified_by_disturbing_others():
    base = _maes(0.076, 0.059, 0.135, 0.045)
    treat = _maes(0.110, 0.060, 0.030, 0.046)   # sob cai MAS nova degrada +0.034
    v = classify_conformation_verdict(base, treat, base_resid=0.3, treat_resid=0.3)
    assert v["verdict"] == "FALSIFIED"


def test_verdict_falsified_by_persistent_sobretorque():
    base = _maes(0.076, 0.059, 0.135, 0.045)
    treat = _maes(0.077, 0.060, 0.125, 0.046)   # sob nao cede (>0.10)
    v = classify_conformation_verdict(base, treat, base_resid=0.3, treat_resid=0.3)
    assert v["verdict"] == "FALSIFIED"


def test_verdict_partial():
    base = _maes(0.076, 0.059, 0.135, 0.045)
    treat = _maes(0.078, 0.060, 0.08, 0.046)    # sob em [0.06,0.10], outros ok
    v = classify_conformation_verdict(base, treat, base_resid=0.3, treat_resid=0.3)
    assert v["verdict"] == "PARTIAL"
