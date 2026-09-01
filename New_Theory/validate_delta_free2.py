"""delta_free — RUN CORRIGIDO (bugs de config identificados no run 1; gates
inalterados): (a) parte friccional ~0 (c_bend=50) => o limiar E' o delta_0 LIDO;
(b) conformacao zerada (estrangulava o carrier de wear — kw x4 inerte no run 1);
(c) runaway torque-excesso suprimido (legacy) => carrier age sozinho.

Run: python New_Theory/validate_delta_free2.py   (~8 min)
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
import transfer_validation as tv  # noqa: E402
from validate_delta_free import simulate, nfail, eval_source  # noqa: E402

BASE = dict(conform_driver="effective", slip_regime_mode="cattaneo_mindlin",
            slip_regime_sharpness=1.0, k_tr_mode="bending", c_bend=50.0,
            loose_torsion_mode="legacy", loose_arrest_floor=0.0,
            _consts=dict(W_conf_ref=0.0))


def main():
    cases, _ = tv.select_cases()
    by = {}
    for c in cases:
        by.setdefault(c.source.name, []).append(c)

    print("== LIU_2025 corrigido (limiar = delta_0 lido; wear puro, conformacao off) ==")
    best = None
    for label, kw in [
        ("kw=8e-4", dict(BASE, delta_free=0.30e-3, k_wear_scale_tr=8e-4)),
        ("kw=1.5e-3", dict(BASE, delta_free=0.30e-3, k_wear_scale_tr=1.5e-3)),
        ("kw=3e-3", dict(BASE, delta_free=0.30e-3, k_wear_scale_tr=3e-3)),
    ]:
        med, rows = eval_source(by["LIU_2025"], kw, label)
        if best is None or med < best[0]:
            best = (med, label, rows)
    print(f"  BEST: {best[1]} medianMAE={best[0]:.3f} "
          f"(gate: <0.06; frontier atual 0.126)")

    print("\n== LU corrigido (ratchet puro + delta_0; runaway off) ==")
    best_lu = None
    for label, kw in [
        ("ratchet 0.02", dict(BASE, delta_free=0.28e-3, k_ratchet=0.02,
                              k_wear_scale_tr=0.0)),
        ("ratchet 0.05", dict(BASE, delta_free=0.28e-3, k_ratchet=0.05,
                              k_wear_scale_tr=0.0)),
        ("ratchet 0.10", dict(BASE, delta_free=0.28e-3, k_ratchet=0.10,
                              k_wear_scale_tr=0.0)),
    ]:
        med, rows = eval_source(by["LU_2024"], kw, label)
        t = {r[0]: r for r in rows}
        n4 = t.get("lu2024_M8_fig20_T4Nm", (None,) * 6)[5]
        n28 = t.get("lu2024_M8_fig20_T28Nm", (None,) * 6)[5]
        print(f"    -> torque-flatness N(T28)/N(T4) = "
              f"{(n28/n4) if (n4 and n28) else float('nan'):.2f} (gate <3; dado ~1.1)")
        if best_lu is None or med < best_lu[0]:
            best_lu = (med, label)
    print(f"  BEST Lu: {best_lu[1]} medianMAE={best_lu[0]:.3f} (frontier atual 0.215/0.196)")


if __name__ == "__main__":
    main()
