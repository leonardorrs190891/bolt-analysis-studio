"""Transferencia zero-refit transversal (sub-campanha A) — spec 2026-07-03 §1."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "New_Theory"))

from transfer_validation import inputs_for, predict_case, select_cases  # noqa: E402


def test_selection_rule_counts_and_exclusions():
    selected, excluded = select_cases()
    csvs = [Path(c.reference_csv_path).name for c in selected]
    # regra pre-registrada: nenhum excluido presente
    for token in ("hdpe", "vibralock", "varamp", "fig2_single"):
        assert not any(token in n for n in csvs), token
    # exclusoes registradas com motivo (sem drop silencioso)
    assert len(excluded) >= 10                     # 3 hdpe + 4 vibralock + 2 varamp + 1 fracture
    assert all(e["reason"] for e in excluded)
    # fontes verificadas na construcao dos casos:
    per_source = {}
    for c in selected:
        per_source[c.source.name] = per_source.get(c.source.name, 0) + 1
    assert per_source["LIU_2025"] == 6             # 7 digitalizadas - fig2_single
    assert per_source["BAUER_2024"] == 9
    for src in ("LU_2024", "ICMEZ_2025", "YANG_2019", "ROUSSEAU_2025",
                "KARLSEN_2022"):
        assert per_source.get(src, 0) > 0, src
    assert len(selected) >= 40                     # varredura substancial
    # todos transversais
    assert all(c.transverse_displacement_mm > 0 for c in selected)


def test_inputs_have_provenance_for_every_selected_case():
    selected, _ = select_cases()
    for c in selected:
        inp = inputs_for(c)
        for key in ("grip_mm", "mu", "rz", "F_amp_N"):
            # prov de F_amp_N e' a string longa "literature (Pai&Hess...)" —
            # classe legitima (faixa MEDIDA da literatura); casa por prefixo
            assert any(str(inp[key]["prov"]).startswith(p) for p in
                       ("paper", "assumed", "handbook", "iso",
                        "literature")), (c.name, key)
            assert inp[key]["value"] is not None
        # overrides de paper onde documentados:
        stem = Path(c.reference_csv_path).stem
        if "lk13p8" in stem:
            assert inp["grip_mm"]["value"] == pytest.approx(13.8)
            assert inp["grip_mm"]["prov"] == "paper"
        if "rousseau2025_steel_t10" in stem:
            assert inp["grip_mm"]["value"] == pytest.approx(25.0)
            assert inp["grip_mm"]["prov"] == "paper"
        if c.source.name == "BAUER_2024" and c.bolt_size.startswith("M8"):
            assert inp["grip_mm"]["value"] == pytest.approx(8.0)


def test_predict_case_smoke():
    selected, _ = select_cases()
    small = min(selected, key=lambda c: c.n_cycles)   # o caso mais curto
    r = predict_case(small, do_sensitivity=False)
    assert np.isfinite(r["MAE"]) and np.isfinite(r["MAE_exp"])
    assert np.isfinite(r["MAE_noloss"])
    assert 0 < r["final_pred"] <= 1.05
    assert r["n_cycles"] > 0 and r["band"] is None


def test_damage_trigger_activates_damage_on_gross_slip():
    """--damage-trigger: num caso de gross-slip (maior amplitude) o dano
    AUTO-dispara (final_D>0 com W_crit baixo); sem o flag, final_D=0 (c_D=0)."""
    import transfer_validation as tv
    sel, _ = tv.select_cases()
    case = max(sel, key=lambda c: c.transverse_displacement_mm)  # gross slip
    inp = tv.inputs_for(case)
    args = (case, inp["grip_mm"]["value"], inp["mu"]["value"],
            inp["rz"]["value"], inp["F_amp_N"]["value"], 100)
    try:
        tv._DAMAGE_ON = False
        tv._DAMAGE_TRIGGER = True
        tv.TRIGGER_W_CRIT = 1e3
        _, d_on = tv._simulate(*args)
        tv._DAMAGE_TRIGGER = False
        _, d_off = tv._simulate(*args)
    finally:
        tv._DAMAGE_ON = False
        tv._DAMAGE_TRIGGER = False
        tv.TRIGGER_W_CRIT = 1.0e5
    assert d_off == 0.0            # sem trigger => dano OFF (c_D=0 default)
    assert d_on > 0.0             # trigger dispara o dano na gross slip
