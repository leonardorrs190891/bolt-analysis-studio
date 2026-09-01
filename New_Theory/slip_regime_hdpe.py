"""HDPE Rousseau: o regime de slip transfere a membro polimerico? (roadmap #29).

Falsificacao-primeiro. O dado HDPE (t10=0.21, t12=0.32, t14=0.875 @400 cic) tem a
MESMA assinatura de instabilidade-por-grip do aco (fino colapsa, grosso trava), NAO
uma relaxacao dominada por creep (t14 perde so 12%). Hipotese: e' o MESMO regime de
slip (forma), so com constantes de HDPE (k_j ~E_hdpe/E_aco menor, emb maior). Se a
FORMA reproduz o shape, uma "forma de creep de polimero" dedicada NAO e' o que o dado
pede aqui (§8: forma transfere, constantes mudam). Se t14 ficar longe, creep entra.

Run: python New_Theory/slip_regime_hdpe.py
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
DELTA, FREQ, NC = 0.5e-3, 1.0, 400          # HDPE data ate 400 ciclos
K_J_HDPE = 2.0e7                            # E_hdpe~1GPa / E_aco~200GPa * k_j_aco(4e9)


def final(grip, F0, emb, c_bend, k, k_creep, consts):
    geom = geometry_for("M12x1.75", grip)
    mat = JointMaterial(
        emb_depth=emb, mu_thread=0.15, mu_bearing=0.15, conform_driver="effective",
        k_j_init=K_J_HDPE, k_creep_scale=k_creep,
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
    data = [float(load_full_curve(f"{DIG}/rousseau2025_hdpe_{n}.csv")[1][-1])
            for n, _, _ in CASES]
    print(f"HDPE data @400: t10={data[0]:.3f} t12={data[1]:.3f} t14={data[2]:.3f} "
          f"(spread {data[2]/max(data[0],1e-3):.1f}x)  k_j_HDPE={K_J_HDPE:.0e}")

    best = None
    for emb in [2.0e-6, 3.5e-6, 6.0e-6]:
        for c_bend in [0.2, 0.3, 0.4]:
            for k in [1.0, 2.0]:
                for k_creep in [1.0, 3.0]:            # polimero creepa mais? testa
                    finals = [final(g, F0, emb, c_bend, k, k_creep, consts) for _, g, F0 in CASES]
                    mae = float(np.mean(np.abs(np.array(finals) - np.array(data))))
                    t10, t12, t14 = finals
                    shape = (t10 < 0.4 and t14 > 0.65 and t10 < t12 < t14)
                    if best is None or (shape, -mae) > (best[3], -best[0]):
                        best = (mae, finals, (emb, c_bend, k, k_creep), shape)
    mae, finals, (emb, c_bend, k, k_creep), shape = best
    print(f"\nBEST (forma-transfere): emb={emb*1e6:.1f}um c_bend={c_bend} k={k} k_creep={k_creep}")
    print(f"  model {[round(x,3) for x in finals]} vs data {[round(x,3) for x in data]} MAE={mae:.3f} shape_ok={shape}")
    creep_needed = (k_creep > 1.0)
    print(f"\nVEREDICTO: {'FORMA TRANSFERE p/ HDPE' if shape else 'forma NAO fecha HDPE'}"
          f" com k_j de polimero. Creep de polimero {'AJUDA (k_creep>1)' if creep_needed else 'NAO necessario (default)'}"
          f" => {'forma de creep dedicada justificada' if creep_needed and not shape else 'o dado HDPE e instabilidade, nao creep (mesma forma, constantes de polimero — §8)'}.")


if __name__ == "__main__":
    main()
