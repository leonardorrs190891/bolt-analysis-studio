"""Calibra c_bend (rigidez de flexao do parafuso p/ k_tr_mode='bending') aos
amplitude sweeps da biblioteca digitalizada — Task 2, spec 2026-07-05.

Metodo (AS IS, sem tuning-to-pass): o REGIME (partial vs gross slip) e o
separador colapso/plato. Classifica cada caso da biblioteca pelo slip INICIAL
(a F0 nominal): slip>0 -> gross (deve colapsar), slip==0 -> partial (deve
platear). Varre c_bend, mede acuracia balanceada (frac colapso->gross +
frac plato->partial)/2. Reporta a melhor. Nao escreve nada.

Uso:  python New_Theory/calibrate_ktr.py
Requer:  New_Theory/transfer_results.json (final_data por curva; §4.8).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

import numpy as np                                                  # noqa: E402
import transfer_validation as tv                                    # noqa: E402
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    JointMaterial, SlowState, resolve_transverse_slip)
from library_common import geometry_for                            # noqa: E402

C_BEND_GRID = [0.3, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0, 20.0]
COLLAPSE_MAX = 0.30      # final_data < => colapso (deve ser gross slip)
PLATEAU_MIN = 0.55       # final_data > => plato (deve ser partial slip)


def _final_data_map():
    p = ROOT / "New_Theory" / "transfer_results.json"
    with open(p, encoding="utf-8") as fh:
        return {r["csv"]: r["final_data"] for r in json.load(fh)["results"]}


def _initial_regime(case, c_bend):
    """True=gross (slip>0), False=partial (slip==0) no ciclo inicial (F0 nominal)."""
    inp = tv.inputs_for(case)
    geom = geometry_for(case.bolt_size, inp["grip_mm"]["value"])
    mat = JointMaterial(k_tr_mode="bending", c_bend=c_bend,
                        mu_bearing=inp["mu"]["value"], mu_thread=inp["mu"]["value"])
    slip = resolve_transverse_slip(
        SlowState(F_0=case.initial_preload_N), mat, 0.4 * case.initial_preload_N,
        np.pi / 2, delta_amp=case.transverse_displacement_mm * 1e-3, geom=geom)
    return slip > 1e-9


def main():
    fd = _final_data_map()
    sel, _ = tv.select_cases()
    print(f"{'c_bend':>7s} {'colapso->gross':>14s} {'plato->partial':>14s} {'acc':>6s}")
    best = None
    for cb in C_BEND_GRID:
        cg = c = pp = p = 0
        for case in sel:
            f = fd.get(Path(case.reference_csv_path).name)
            if f is None:
                continue
            gross = _initial_regime(case, cb)
            if f < COLLAPSE_MAX:
                c += 1
                cg += gross
            elif f > PLATEAU_MIN:
                p += 1
                pp += (not gross)
        acc = (cg / max(c, 1) + pp / max(p, 1)) / 2
        print(f"{cb:7.1f} {cg:>3d}/{c:<3d}={cg/max(c,1):>4.0%} "
              f"{pp:>3d}/{p:<3d}={pp/max(p,1):>4.0%} {acc:>5.0%}")
        if best is None or acc > best[0]:
            best = (acc, cb, cg, c, pp, p)
    acc, cb, cg, c, pp, p = best
    print(f"\nMELHOR c_bend={cb}: colapso->gross {cg}/{c}={cg/max(c,1):.0%}, "
          f"plato->partial {pp}/{p}={pp/max(p,1):.0%}, acc balanceada={acc:.0%}")
    print("Nota: um unico c_bend nao separa 100% — resto = outros modos de "
          "colapso (near-proof/rigidez de membro) + platos de alta amplitude.")


if __name__ == "__main__":
    main()
