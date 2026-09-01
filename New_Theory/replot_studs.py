"""
Replotagem em Python dos diagramas de carga para estojos tracionados
axialmente (Verspannungsdiagramm / VDI 2230 incremental).

Dois gráficos:
  1. Espacamento entre flanges [mm] vs Carga axial externa [kN],
     para diferentes níveis de pré-carga (75/80/90/100% de F0_ref).
  2. Deformação no parafuso [μstrain] vs Força aplicada [kN],
     para diferentes níveis de pré-deformação (200/400/600/800 μstrain).

Modelo (linear, antes/depois da separação):

  F_bolt(F_ext) = F0 + Phi * F_ext                       (F_ext < F_sep)
                = F_ext                                   (F_ext >= F_sep)

  F_joint(F_ext) = F0 - (1 - Phi) * F_ext                (F_ext < F_sep)
                 = 0                                       (F_ext >= F_sep)

  gap(F_ext) = 0                                          (F_ext < F_sep)
             = (F_ext - F_sep) / k_b                      (F_ext >= F_sep)

  strain(F_ext) = F_bolt(F_ext) / (E * A_s)

  onde:
    Phi   = k_b / (k_b + k_j)        razão de rigidez (force ratio, VDI)
    F_sep = F0 / (1 - Phi)           carga de separação do joint
    k_b   = E * A_s / L_eff          rigidez axial do parafuso
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


# --------------------------------------------------------------------------- #
# Parametros físicos
# --------------------------------------------------------------------------- #

@dataclass
class StudJoint:
    """Parâmetros de um estojo + joint flangeado tracionado axialmente."""
    E: float = 200e9            # Pa  (aço carbono)
    A_s: float = 200e-6         # m^2 (~M20: 245e-6; M18: 192e-6)
    L_eff: float = 0.060        # m   (comprimento efetivo do parafuso)
    Phi: float = 0.20           # razão de rigidez bolt/(bolt+joint), VDI

    @property
    def k_b(self) -> float:
        """Rigidez axial do parafuso [N/m]."""
        return self.E * self.A_s / self.L_eff

    @property
    def k_j(self) -> float:
        """Rigidez axial do joint [N/m] (derivada de Phi)."""
        return self.k_b * (1.0 - self.Phi) / self.Phi

    def F_separation(self, F0: float) -> float:
        """Carga externa que abre o joint [N]."""
        return F0 / (1.0 - self.Phi)

    def gap(self, F_ext: np.ndarray, F0: float) -> np.ndarray:
        """
        Espaçamento entre flanges [m] em função da carga externa.

        Modelo bilinear:
          - F_ext < F_sep: joint comprime menos (slope pequeno = (1-Φ)/k_j)
          - F_ext ≥ F_sep: joint separado (slope grande = 1/k_b)
          - Continuidade em F_sep: gap = F0 / k_j em ambos os lados.
        """
        F_sep = self.F_separation(F0)
        g_pre = (1.0 - self.Phi) * F_ext / self.k_j
        g_post = F0 / self.k_j + (F_ext - F_sep) / self.k_b
        return np.where(F_ext < F_sep, g_pre, g_post)

    def bolt_force(self, F_ext: np.ndarray, F0: float) -> np.ndarray:
        """Força no parafuso [N] em função da carga externa."""
        F_sep = self.F_separation(F0)
        return np.where(F_ext < F_sep, F0 + self.Phi * F_ext, F_ext)

    def bolt_strain(self, F_ext: np.ndarray, F0: float) -> np.ndarray:
        """Deformação axial do parafuso [strain, adimensional]."""
        return self.bolt_force(F_ext, F0) / (self.E * self.A_s)


# --------------------------------------------------------------------------- #
# Plot 1: gap vs carga externa
# --------------------------------------------------------------------------- #

def plot_gap_vs_load(
    joint: StudJoint,
    F0_ref_kN: float = 49.0,
    preload_pcts=(100, 90, 80, 75),
    F_ext_max_kN: float = 100.0,
    n_points: int = 400,
    out_path: Path | None = None,
) -> None:
    """
    Plot 1: espaçamento entre flanges vs carga axial externa,
    para diferentes níveis de pré-carga.
    """
    F_ext = np.linspace(0.0, F_ext_max_kN * 1e3, n_points)
    fig, ax = plt.subplots(figsize=(7, 4))

    colors = {100: "#1f77b4", 90: "#ff7f0e", 80: "#2ca02c", 75: "#17becf"}
    for pct in preload_pcts:
        F0 = F0_ref_kN * 1e3 * (pct / 100.0)
        gap_mm = joint.gap(F_ext, F0) * 1e3
        ax.plot(F_ext / 1e3, gap_mm,
                marker="o", markersize=3, markevery=20,
                linewidth=1.4, color=colors.get(pct, None),
                label=f"{pct}%")

    ax.set_xlabel("Carga axial externa [kN]")
    ax.set_ylabel("Espaçamento entre flanges [mm]")
    ax.set_xlim(0, F_ext_max_kN)
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.4)
    ax.legend(loc="upper left", frameon=False, ncol=2)
    fig.tight_layout()

    if out_path is not None:
        fig.savefig(out_path, dpi=140, bbox_inches="tight")
    return fig


# --------------------------------------------------------------------------- #
# Plot 2: strain do parafuso vs força aplicada
# --------------------------------------------------------------------------- #

def plot_strain_vs_load(
    joint: StudJoint,
    pre_strains_ustrain=(200, 400, 600, 800),
    F_ext_max_kN: float = 40.0,
    n_points: int = 400,
    out_path: Path | None = None,
) -> None:
    """
    Plot 2: deformação no parafuso vs força aplicada,
    para diferentes níveis de pré-deformação.

    A pré-deformação é convertida em pré-carga F0 = eps * E * A_s.
    """
    F_ext = np.linspace(0.0, F_ext_max_kN * 1e3, n_points)
    fig, ax = plt.subplots(figsize=(7, 4))

    colors = {200: "#1f77b4", 400: "#ff7f0e", 600: "#2ca02c", 800: "#d62728"}
    for eps_pre in pre_strains_ustrain:
        F0 = eps_pre * 1e-6 * joint.E * joint.A_s
        eps = joint.bolt_strain(F_ext, F0) * 1e6  # μstrain
        ax.plot(F_ext / 1e3, eps,
                linewidth=1.6,
                color=colors.get(eps_pre, None),
                label=fr"Pré-deformação de {eps_pre} $\mu$strains")

    ax.set_xlabel("Força aplicada, kN")
    ax.set_ylabel(r"Deformação no parafuso, $\mu$strain")
    ax.set_xlim(0, F_ext_max_kN)
    ax.set_ylim(0, 1400)
    ax.grid(True, alpha=0.4)
    ax.legend(loc="upper left", frameon=True, fontsize=9)
    fig.tight_layout()

    if out_path is not None:
        fig.savefig(out_path, dpi=140, bbox_inches="tight")
    return fig


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    here = Path(__file__).resolve().parent

    # Parâmetros calibrados via extract_curves.py contra os JPEGs do
    # New_Theory (least_squares fit, modelo bilinear):
    #   A_s = 233 mm²   (~M22 ou 3/4"-10 UNC)
    #   L_eff = 58 mm
    #   Phi   = 0.20    (média entre Plot 1 = 0.18 e Plot 2 = 0.24)
    joint = StudJoint(
        E=200e9,
        A_s=233e-6,
        L_eff=0.058,
        Phi=0.20,
    )

    print(f"k_bolt  = {joint.k_b/1e6:7.1f} MN/m  ({joint.k_b/1e6:.0f} kN/mm)")
    print(f"k_joint = {joint.k_j/1e6:7.1f} MN/m  ({joint.k_j/1e6:.0f} kN/mm)")
    print(f"Phi     = {joint.Phi:7.3f}")
    print()
    for pct in (100, 90, 80, 75):
        F0 = 49.0 * pct / 100.0
        F_sep = joint.F_separation(F0 * 1e3) / 1e3
        print(f"  preload {pct:3d}% -> F0 = {F0:5.1f} kN, "
              f"F_sep = {F_sep:5.1f} kN")
    print()
    for eps_pre in (200, 400, 600, 800):
        F0 = eps_pre * 1e-6 * joint.E * joint.A_s / 1e3
        F_sep = joint.F_separation(F0 * 1e3) / 1e3
        print(f"  pré-eps {eps_pre:4d} ustrain -> F0 = {F0:5.1f} kN, "
              f"F_sep = {F_sep:5.1f} kN")

    plot_gap_vs_load(joint, out_path=here / "replot_carga_x_espacamento.png")
    plot_strain_vs_load(joint, out_path=here / "replot_deformacao_x_carga.png")
    print(f"\nFiguras salvas em: {here}")
