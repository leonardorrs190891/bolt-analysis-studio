"""Identificabilidade das constantes do regime de slip (roadmap Wave 2, trust).

As constantes fisicas do regime de slip sao c_bend (coloca a transicao r=1 no
grip) e slip_regime_sharpness k (nitidez). Pergunta: sao SEPARADAMENTE
identificaveis pela FORMA do Rousseau, ou trocam entre si (vale degenerado)?

Mapeia a MAE do Rousseau sobre a grade (c_bend, k) a emb fixa e caracteriza a
regiao de baixa MAE: se c_bend e k variam muito e anti-correlacionados => vale
(pouco identificavel); se a regiao e' compacta => identificavel.

kappa (capacidade wear/fretting, canal axial) e' identificada so pelo dado axial,
que esta' gated no nivel (Fouvry) => fracamente identificavel (caveat honesto).

Run: python New_Theory/identifiability_slip_regime.py
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)
from library_common import geometry_for, frozen_constants, load_full_curve  # noqa: E402

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"
CASES = [("t10", 25.0, 10250.0), ("t12", 29.0, 10250.0), ("t14", 33.0, 10350.0)]
DELTA, FREQ, NC, EMB = 0.5e-3, 1.0, 180, 1.5e-6


def final(grip, F0, c_bend, k, consts):
    geom = geometry_for("M12x1.75", grip)
    mat = JointMaterial(
        emb_depth=EMB, mu_thread=0.15, mu_bearing=0.15, conform_driver="effective",
        slip_regime_mode="cattaneo_mindlin", slip_regime_sharpness=k,
        k_tr_mode="bending", c_bend=c_bend,
        loose_torsion_mode="bolt_torsion", eta_loose=15.0, loose_arrest_floor=0.08,
        **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    for _ in range(NC):
        ana.step_cycle(0.4 * F0, np.pi / 2, FREQ, delta_amp=DELTA)
    return max(ana.state.F_0, 0.0) / F0


def main():
    consts, _ = frozen_constants()
    data = [float(load_full_curve(f"{DIG}/rousseau2025_steel_{n}.csv")[1][-1])
            for n, _, _ in CASES]
    c_grid = [0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.7, 1.0]
    k_grid = [1.0, 1.5, 2.0, 3.0, 4.0]
    rows = []
    for c in c_grid:
        for k in k_grid:
            finals = [final(g, F0, c, k, consts) for _, g, F0 in CASES]
            mae = float(np.mean(np.abs(np.array(finals) - np.array(data))))
            rows.append((mae, c, k))
    rows.sort(key=lambda r: r[0])
    best = rows[0]
    thr = best[0] * 1.5
    good = [(c, k) for mae, c, k in rows if mae <= thr]
    cs = [c for c, _ in good]; ks = [k for _, k in good]
    print(f"data {[round(x,3) for x in data]}; best MAE={best[0]:.3f} @ c_bend={best[1]} k={best[2]}")
    print(f"configs within 1.5x best MAE: {len(good)}/{len(rows)}")
    print(f"  c_bend range {min(cs):.2f}-{max(cs):.2f} (x{max(cs)/min(cs):.1f}); k range {min(ks):.0f}-{max(ks):.0f}")
    if len(good) > 2 and np.std(cs) > 0 and np.std(ks) > 0:
        corr = float(np.corrcoef(cs, ks)[0, 1])
        print(f"  corr(c_bend, k) in low-MAE set = {corr:+.2f}")
        verdict = ("VALE degenerado (c_bend<->k trocam; "
                   "identifica-se so o PRODUTO/transicao, nao cada um)"
                   if corr < -0.5 else
                   "regiao COMPACTA => c_bend e k separadamente identificaveis")
    else:
        verdict = "regiao muito pequena => bem localizada (identificavel)"
    print(f"VEREDICTO: {verdict}")
    print("Nota: c_bend fixa a transicao (grip), k a nitidez; kappa (axial) fica")
    print("fracamente identificavel enquanto o nivel de fret nao tiver ancora (Fouvry).")


if __name__ == "__main__":
    main()
