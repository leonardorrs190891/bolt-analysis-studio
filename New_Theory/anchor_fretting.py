"""Ancora de nivel para o wear/fretting via energia de Fouvry (roadmap Wave 2).

NAO e' um fit. Confere se o K_archard do modelo (nivel do wear/fretting) e'
consistente com o coeficiente de energia-desgaste de Fouvry para aco, dando
PROVENIENCIA de ordem-de-grandeza (literatura), nao um knob livre.

Fouvry: V = alpha * E_d  (volume desgastado ~ energia de atrito dissipada).
Archard: V = K * F * s / H. Com E_d = mu * F * s => K = alpha * mu * H.

alpha (aco): O(1e-4 mm^3/J) na literatura de energia-desgaste de Fouvry
(ordem de grandeza; o valor exato por par tribologico precisa de um mapa de
fretting do rig — provenance 'literature/handbook', analogo a [[anchor-creep]]).

Run: python New_Theory/anchor_fretting.py
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial  # noqa: E402

# Fouvry energy-wear coefficient p/ aco (ordem de grandeza, literatura):
ALPHA_MM3_PER_J = 1.0e-4          # mm^3/J  -> 1e-13 m^3/J
ALPHA_M3_PER_J = ALPHA_MM3_PER_J * 1e-9
MU = 0.15                          # atrito representativo (regra MSD)
# Dureza do aco (Pa = J/m^3): banda macio->endurecido
H_BAND = {"macio (~2 GPa)": 2.0e9, "medio (~3 GPa)": 3.0e9,
          "endurecido (~6 GPa)": 6.0e9}


def main():
    K_model = JointMaterial().K_archard
    print(f"K_archard do modelo (default) = {K_model:.2e}")
    print(f"alpha Fouvry (aco, literatura) = {ALPHA_MM3_PER_J:.1e} mm^3/J "
          f"= {ALPHA_M3_PER_J:.1e} m^3/J ; mu={MU}\n")
    print("K_implied = alpha * mu * H  (adimensional):")
    ok = False
    for label, H in H_BAND.items():
        K_imp = ALPHA_M3_PER_J * MU * H
        ratio = K_imp / K_model
        flag = "consistente (~ordem de grandeza)" if 0.2 <= ratio <= 5.0 else "fora"
        print(f"  H {label:20s} -> K_implied={K_imp:.2e}  (K_implied/K_model={ratio:.2f})  {flag}")
        ok = ok or (0.2 <= ratio <= 5.0)
    print()
    print("VEREDICTO:", "K_archard do modelo esta na FAIXA de Fouvry para aco"
          if ok else "K_archard FORA da faixa de Fouvry")
    print("=> nivel do wear/fretting tem PROVENIENCIA de ordem-de-grandeza (literatura),")
    print("   nao e' knob livre. O k_thread_fret POR PAR (multiplicador do flanco)")
    print("   ainda precisa de um mapa de fretting do rig p/ o valor exato (caveat).")
    print("AS-IS: ancora de ordem-de-grandeza (analoga a anchor_creep), nao fit por curva.")


if __name__ == "__main__":
    main()
