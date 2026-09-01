"""Forma-PRODUTO (ratchet x slip_fraction) vs os DOIS alvos (spec 2026-07-08).

A forma foi apontada pelas duas falhas de gate: Liu2025 shape back-loaded
(acelerante) + Lu N_falha flat vs torque (invariancia em F0_init). Gates
INALTERADOS: Liu2025 mediana <0.06 (fronteira 0.126); Lu flatness N(T28)/N(T4)
<3 (dado ~1.1) + mediana <=0.196.

Run: python New_Theory/validate_product_form.py   (~7 min)
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
import transfer_validation as tv  # noqa: E402
from validate_delta_free import eval_source  # noqa: E402

BASE = dict(conform_driver="effective", slip_regime_mode="cattaneo_mindlin",
            slip_regime_sharpness=1.0, k_tr_mode="bending", c_bend=50.0,
            loose_torsion_mode="legacy", loose_arrest_floor=0.0,
            k_wear_scale_tr=0.0, ratchet_torque_coupled=True,
            _consts=dict(W_conf_ref=0.0))


def main():
    cases, _ = tv.select_cases()
    by = {}
    for c in cases:
        by.setdefault(c.source.name, []).append(c)

    print("== LIU_2025 — produto (acelerante), delta_0=0.30mm ==")
    best = None
    for label, kw in [
        ("k=5e-5", dict(BASE, delta_free=0.30e-3, k_ratchet=5e-5)),
        ("k=1e-4", dict(BASE, delta_free=0.30e-3, k_ratchet=1e-4)),
        ("k=2e-4", dict(BASE, delta_free=0.30e-3, k_ratchet=2e-4)),
    ]:
        med, rows = eval_source(by["LIU_2025"], kw, label)
        if best is None or med < best[0]:
            best = (med, label)
    print(f"  BEST Liu2025: {best[1]} medianMAE={best[0]:.3f} "
          f"(gate <0.06; fronteira 0.126)")

    print("\n== LU — produto, delta_0=0.28mm ==")
    best_lu = None
    for label, kw in [
        ("k=0.02", dict(BASE, delta_free=0.28e-3, k_ratchet=0.02)),
        ("k=0.05", dict(BASE, delta_free=0.28e-3, k_ratchet=0.05)),
        ("k=0.10", dict(BASE, delta_free=0.28e-3, k_ratchet=0.10)),
    ]:
        med, rows = eval_source(by["LU_2024"], kw, label)
        t = {r[0]: r for r in rows}
        n4 = t.get("lu2024_M8_fig20_T4Nm", (None,) * 6)[5]
        n28 = t.get("lu2024_M8_fig20_T28Nm", (None,) * 6)[5]
        flat = (n28 / n4) if (n4 and n28) else float("nan")
        print(f"    -> flatness N(T28)/N(T4) = {flat:.2f} (gate <3; dado ~1.1)")
        if best_lu is None or med < best_lu[0]:
            best_lu = (med, label, flat)
    print(f"  BEST Lu: {best_lu[1]} medianMAE={best_lu[0]:.3f} "
          f"flatness={best_lu[2]:.2f} (fronteira 0.196)")


if __name__ == "__main__":
    main()
