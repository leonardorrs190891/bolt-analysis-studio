"""Discriminacao do sobretorque (bound F0 -> 133 kN). Testa os helpers puros
(thresholds pre-registrados); a corrida cientifica em si nao e testada."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "New_Theory"))
sys.path.insert(0, str(ROOT / "src"))

from sobretorque_f0bound import (  # noqa: E402
    F0_SANITY_N, RESCUE_MAE, PERSIST_MAE, read_baseline, classify_verdict,
)


def test_ceiling_matches_calibrate_shared_and_value():
    # DRY: mesmo teto de sanidade que calibrate_shared.F0_SANITY_N
    from calibrate_shared import F0_SANITY_N as canonical
    assert F0_SANITY_N == pytest.approx(canonical)
    assert F0_SANITY_N == pytest.approx(132_822.0, rel=1e-4)


def test_read_baseline_from_shared_block(tmp_path):
    j = tmp_path / "joint_calibrations.json"
    j.write_text(json.dumps({
        "schema": 2,
        "shared": {
            "mae_global": 0.0796,
            "conditions": {
                "sobretorque": {
                    "states": {"F0_test_N": 120000.0, "F0_provenance": "estimated"},
                    "MAE": 0.1378,
                },
            },
        },
    }), encoding="utf-8")
    b = read_baseline(j)
    assert b["mae"] == pytest.approx(0.1378)
    assert b["f0_N"] == pytest.approx(120000.0)
    assert b["mae_global"] == pytest.approx(0.0796)


def test_classify_verdict_rescued():
    # MAE cai para a banda fittavel + F0 interior => bound era apertado demais
    v = classify_verdict(mae_base=0.1378, mae_new=0.03,
                         f0_new=125_000.0, ceiling=F0_SANITY_N)
    assert v["verdict"] == "bound-too-tight (rescued)"
    assert v["pinned_at_new_ceiling"] is False
    assert v["delta_mae"] == pytest.approx(0.1078)


def test_classify_verdict_missing_mechanism():
    # F0 crava no novo teto e MAE continua alta => mecanismo faltante
    v = classify_verdict(mae_base=0.1378, mae_new=0.13,
                         f0_new=F0_SANITY_N, ceiling=F0_SANITY_N)
    assert v["verdict"] == "missing mechanism (falsified again)"
    assert v["pinned_at_new_ceiling"] is True


def test_classify_verdict_partial():
    v = classify_verdict(mae_base=0.1378, mae_new=0.08,
                         f0_new=128_000.0, ceiling=F0_SANITY_N)
    assert v["verdict"] == "partial / inconclusive"
