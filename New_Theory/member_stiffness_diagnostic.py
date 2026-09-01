"""Diagnostico de rigidez-de-membro / escala com espessura (roadmap #10, §4.8).

Responde: por que o modelo V2 e CEGO A ESPESSURA na unica varredura de rigidez de
membro da biblioteca (Rousseau steel t10/12/14, grips 25/29/33 mm)? O dado tem
efeito ~10x (final 0.088 -> 0.624 -> 0.903); o modelo fica ~plano.

NAO adota nada — e diagnostico. Decompoe a perda por mecanismo e FALSIFICA a
hipotese original do #10 (escala de k_j / rigidez de membro):

  A. Perda ~60-70% EMBEDDING (loosening rotacional NEGLIGENCIAVEL ~0.3%, embora
     dispare todo ciclo; wear ~4%). Modelo 0.203/0.304/0.388 (~2x) vs dado ~10x.
  B. k_j ~1/grip (rigidez de membro escalada) => EFEITO ZERO (identico ao baseline):
     a perda e dirigida por embedding (dF_0=k_b*d_delta, nao envolve k_j) e o
     loosening e negligenciavel, entao k_j nao muda nada. HIPOTESE DO #10 FALSIFICADA.
  C. loosening forte (k_loose_scale_tr=20): ainda ~2.8x — nao chega aos 10x.
  D. loosening forte + emb x0.25: ~1.1x (ainda mais plano).

VEREDICTO: o modelo tem UMA alavanca de grip — k_b ~1/grip (~32% em t10->t14) — que
entra em TODO mecanismo do mesmo jeito (dF_0 = -k_b*d_delta), entao a sensibilidade
a espessura esta ESTRUTURALMENTE limitada a ~32%. O efeito 10x do dado e uma
INSTABILIDADE de onset de rotacao dependente do grip (fino->colapso, grosso->estavel)
que a fisica do modelo NAO expressa. #10 e forma faltante mais profunda (limiar de
loosening modulado por grip), NAO escala da constante k_j.

Run:  python New_Theory/member_stiffness_diagnostic.py
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial, SlowState, F_slip_transverse)
from library_common import (  # noqa: E402
    frozen_constants, geometry_for, emb_depth_vdi)
from transfer_validation import RZ_DEFAULT, F_AMP_RATIO  # noqa: E402

# Rousseau steel: M12, disp 0.5mm, 1Hz, 180 cyc; grips 25/29/33; data finals
CASES = [("t10", 25.0, 10250.0, 0.0878),
         ("t12", 29.0, 10250.0, 0.6244),
         ("t14", 33.0, 10350.0, 0.9034)]
DELTA, FREQ, NC = 0.5e-3, 1.0, 180


def run(grip, F0, k_j=None, emb_scale=1.0, **extra):
    consts, _ = frozen_constants()
    emb_m, _ = emb_depth_vdi(RZ_DEFAULT, 1)
    geom = geometry_for("M12x1.75", grip)
    kw = dict(emb_depth=emb_m * emb_scale, mu_thread=0.15, mu_bearing=0.15,
              conform_driver="effective")
    if k_j is not None:
        kw["k_j_init"] = k_j
    kw.update(extra)
    mat = JointMaterial(**kw, **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    for n in range(1, NC + 1):
        ana.step_cycle(F_AMP_RATIO * F0, np.pi / 2, FREQ, delta_amp=DELTA)
    cum = {}
    for snap in ana.history:
        for m, dF in snap.dF_0_by_mech.items():
            cum[m] = cum.get(m, 0.0) + dF
    return geom, mat, ana, cum


def _final(ana, F0):
    return max(ana.state.F_0, 0.0) / F0


def main():
    print(f"RZ_DEFAULT={RZ_DEFAULT}  F_AMP_RATIO={F_AMP_RATIO}")
    print("\nPART A - baseline decomposition (fixed k_j=4e9)")
    print(f"{'':4s}{'grip':>5s}{'k_b':>10s}{'Phi':>7s}{'loose%':>8s}{'emb%':>7s}"
          f"{'wear%':>7s}{'model':>7s}{'data':>7s}")
    for name, grip, F0, data in CASES:
        geom, mat, ana, cum = run(grip, F0)
        phi = geom.k_b / (geom.k_b + mat.k_j_init)
        print(f"{name:4s}{grip:5.0f}{geom.k_b:10.2e}{phi:7.3f}"
              f"{cum.get('rotational_loosening',0)/F0*100:8.1f}"
              f"{cum.get('embedding',0)/F0*100:7.1f}{cum.get('wear',0)/F0*100:7.1f}"
              f"{_final(ana,F0):7.3f}{data:7.3f}")

    print("\nPART B - k_j ~1/grip (k_j=4e9*25/grip; rigidez de membro escalada)")
    for name, grip, F0, data in CASES:
        _, _, ana, _ = run(grip, F0, k_j=4e9 * 25.0 / grip)
        print(f"  {name} grip{grip:.0f} model={_final(ana,F0):.3f} data={data:.3f}")

    print("\nPART C - loosening forte (k_loose_scale_tr=20)")
    for name, grip, F0, data in CASES:
        _, _, ana, cum = run(grip, F0, k_loose_scale_tr=20.0)
        print(f"  {name} grip{grip:.0f} loose%={cum.get('rotational_loosening',0)/F0*100:6.1f}"
              f" model={_final(ana,F0):.3f} data={data:.3f}")

    print("\nPART D - loosening forte + emb x0.25")
    for name, grip, F0, data in CASES:
        _, _, ana, _ = run(grip, F0, k_loose_scale_tr=20.0, emb_scale=0.25)
        print(f"  {name} grip{grip:.0f} model={_final(ana,F0):.3f} data={data:.3f}")

    print("\nDado: 0.088 -> 0.624 -> 0.903 (~10x). Nenhum ajuste single-constant "
          "chega la => forma faltante (instabilidade de rotacao dependente de grip), "
          "nao escala de k_j (FALSIFICADA em B). Ver MODEL_LEGITIMACY §4.8.")


if __name__ == "__main__":
    main()
