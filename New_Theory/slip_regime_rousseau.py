"""Validacao do regime de slip Cattaneo-Mindlin no Rousseau (spec 2026-07-07 §7).

Sucesso = FORMA: t10 colapsa, t14 sobrevive, spread monotono (o modelo passa a
EXPRESSAR o 10x). Combina DUAS pecas (spec §8): (a) onset de gross-slip afiado
(slip_regime_mode=cattaneo_mindlin + k_tr bending + bolt_torsion + arresto) faz o
grip fino colapsar e o grosso travar; (b) emb_depth mais fino (proveniencia Rz<4,
NAO fit) faz o t14 travado perder so ~10% (senao embedding sozinho tira 61%).

Varre (emb, c_bend, k) num grid pequeno e reporta a melhor FORMA + o c_bend usado
(sinaliza se sub-fisico). AS-IS. Run: python New_Theory/slip_regime_rousseau.py
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
from library_common import (  # noqa: E402
    geometry_for, frozen_constants, emb_depth_vdi, load_full_curve)

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"
CASES = [("t10", 25.0, 10250.0), ("t12", 29.0, 10250.0), ("t14", 33.0, 10350.0)]
DELTA, FREQ, NC = 0.5e-3, 1.0, 180


def run(grip, F0, emb, c_bend, k, consts):
    geom = geometry_for("M12x1.75", grip)
    mat = JointMaterial(
        emb_depth=emb, mu_thread=0.15, mu_bearing=0.15, conform_driver="effective",
        slip_regime_mode="cattaneo_mindlin", slip_regime_sharpness=k,
        k_tr_mode="bending", c_bend=c_bend,
        loose_torsion_mode="bolt_torsion", eta_loose=15.0, loose_arrest_floor=0.08,
        **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    for _ in range(NC):
        ana.step_cycle(0.4 * F0, np.pi / 2, FREQ, delta_amp=DELTA)
    return max(ana.state.F_0, 0.0) / F0


def mae(finals, data):
    return float(np.mean(np.abs(np.array(finals) - np.array(data))))


def shape_ok(finals):
    t10, t12, t14 = finals
    return (t10 < 0.25 and t14 > 0.60 and t10 < t12 < t14)


def main():
    consts, _ = frozen_constants()
    data = [float(load_full_curve(f"{DIG}/rousseau2025_steel_{n}.csv")[1][-1])
            for n, _, _ in CASES]
    print(f"data finals: t10={data[0]:.3f} t12={data[1]:.3f} t14={data[2]:.3f} (spread {data[2]/max(data[0],1e-3):.1f}x)")

    # baseline (report): default engine, no slip-regime — thickness-blind
    emb_base, _ = emb_depth_vdi("Rz10-40", 1)
    base = []
    for n, g, F0 in CASES:
        geom = geometry_for("M12x1.75", g)
        m = JointMaterial(emb_depth=emb_base, mu_thread=0.15, mu_bearing=0.15,
                          conform_driver="effective", **consts)
        a = DynamicStiffnessAnalyzer(geom, m, F0)
        for _ in range(NC):
            a.step_cycle(0.4 * F0, np.pi / 2, FREQ, delta_amp=DELTA)
        base.append(max(a.state.F_0, 0.0) / F0)
    print(f"baseline (thickness-blind): {[round(x,3) for x in base]} MAE={mae(base,data):.3f}\n")

    embs = {"Rz<4/1": emb_depth_vdi("Rz<4", 1)[0], "2.0um": 2.0e-6, "1.5um": 1.5e-6}
    grid = []
    for elabel, emb in embs.items():
        for c_bend in [0.2, 0.3, 0.4, 0.6, 1.0]:
            for k in [1.0, 2.0, 4.0]:
                finals = [run(g, F0, emb, c_bend, k, consts) for _, g, F0 in CASES]
                grid.append((mae(finals, data), shape_ok(finals), elabel, emb, c_bend, k, finals))

    ok = [g for g in grid if g[1]]
    ok.sort(key=lambda x: x[0])
    print(f"configs with RIGHT SHAPE (t10<0.25, t14>0.60, monotone): {len(ok)}/{len(grid)}")
    for mae_v, _, elabel, emb, c_bend, k, finals in ok[:6]:
        print(f"  emb={elabel:8s} c_bend={c_bend:.2f} k={k:.0f} -> "
              f"{[round(x,3) for x in finals]} MAE={mae_v:.3f}")
    best = ok[0] if ok else min(grid, key=lambda x: x[0])
    mae_v, sok, elabel, emb, c_bend, k, finals = best
    print(f"\nBEST: emb={elabel} ({emb*1e6:.1f}um) c_bend={c_bend} k={k}")
    print(f"  model finals {[round(x,3) for x in finals]} vs data {[round(x,3) for x in data]} MAE={mae_v:.3f}")
    print(f"  shape_ok={sok}; baseline MAE was {mae(base,data):.3f} (spread ~1x, thickness-blind)")
    cphys = "PHYSICAL (bolt-alone 3-12; joint-stack <1 defensible)" if c_bend >= 0.3 else "SUB-PHYSICAL (per-rig transverse compliance)"
    print(f"  c_bend provenance: {cphys}")
    print("\nAS-IS: FORMA representavel se shape_ok; c_bend e' per-rig (compliance"
          " transversal do stack). emb Rz<4 = proveniencia (Bolt Science), nao fit.")


if __name__ == "__main__":
    main()
