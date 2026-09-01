"""Liu2025 — candidato INCUBACAO (forma EXISTENTE slip_onset_W, Jiang estagio-I)
composto com os carriers (spec 2026-07-08; autorizado pelo professor).

A triangulacao das 3 falhas (exponencial/linear/acelerante — todas CEDO demais)
aponta fase inicial ~plana + colapso que se desenvolve = incubacao. Propriedade
chave: W_slip/ciclo ∝ (δ−δ₀) ⇒ a duracao da incubacao escala 1/(δ−δ₀)
AUTOMATICAMENTE — a mesma lei do N_falha do dado. Grade pinada por analitica
(W/cyc ≈ 7.2 J @amp0.5). Gate INALTERADO: mediana < 0.06 (fronteira 0.126).

Run: python New_Theory/validate_incubation_liu2025.py   (~8 min)
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
            delta_free=0.30e-3, _consts=dict(W_conf_ref=0.0))


def main():
    cases, _ = tv.select_cases()
    liu = [c for c in cases if c.source.name == "LIU_2025"]
    best = None
    grids = [
        ("W=3e4 + ratchet 3e-5", dict(BASE, slip_onset_W=3e4, k_ratchet=3e-5,
                                      k_wear_scale_tr=0.0)),
        ("W=7e4 + ratchet 3e-5", dict(BASE, slip_onset_W=7e4, k_ratchet=3e-5,
                                      k_wear_scale_tr=0.0)),
        ("W=7e4 + ratchet 5e-5", dict(BASE, slip_onset_W=7e4, k_ratchet=5e-5,
                                      k_wear_scale_tr=0.0)),
        ("W=1.5e5 + ratchet 5e-5", dict(BASE, slip_onset_W=1.5e5, k_ratchet=5e-5,
                                        k_wear_scale_tr=0.0)),
        ("W=3e4 + wear 1.5e-3", dict(BASE, slip_onset_W=3e4,
                                     k_wear_scale_tr=1.5e-3)),
        ("W=7e4 + wear 1.5e-3", dict(BASE, slip_onset_W=7e4,
                                     k_wear_scale_tr=1.5e-3)),
    ]
    for label, kw in grids:
        med, rows = eval_source(liu, kw, label)
        if best is None or med < best[0]:
            best = (med, label)
    print(f"\nBEST: {best[1]} medianMAE={best[0]:.3f}")
    print("(gate <0.06; fronteira 0.126; falsificados: wear 0.143, linear 0.176, produto 0.249)")


if __name__ == "__main__":
    main()
