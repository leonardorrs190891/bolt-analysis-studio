"""Liu2025 — a ULTIMA celula limpa (apontada pelo shape-error do amp0p4):
carrier RATCHET (taxa linear ∝ (δ−δ₀), F0-flat ⇒ declinio ~LINEAR, a classe de
forma do dado) + delta_free + torsao LEGACY (runaway off — o bug que invalidou
as linhas ratchet do run 1) + conformacao off. k_r pinado por analitica (~4e-5).

Run: python New_Theory/validate_delta_free3.py   (~5 min)
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
            k_wear_scale_tr=0.0, _consts=dict(W_conf_ref=0.0))


def main():
    cases, _ = tv.select_cases()
    liu = [c for c in cases if c.source.name == "LIU_2025"]
    best = None
    for label, kw in [
        ("ratchet 2e-5", dict(BASE, delta_free=0.30e-3, k_ratchet=2e-5)),
        ("ratchet 4e-5", dict(BASE, delta_free=0.30e-3, k_ratchet=4e-5)),
        ("ratchet 8e-5", dict(BASE, delta_free=0.30e-3, k_ratchet=8e-5)),
    ]:
        med, rows = eval_source(liu, kw, label)
        if best is None or med < best[0]:
            best = (med, label)
    print(f"\nBEST: {best[1]} medianMAE={best[0]:.3f} "
          f"(gate <0.06; fronteira 0.126; wear-carrier rejeitado 0.143)")


if __name__ == "__main__":
    main()
