"""
Extração pixel-a-pixel das curvas dos JPEGs do New_Theory + fit numérico
do modelo bilinear contra os pontos extraídos.

Estratégia:
  1. Abrir JPEG, converter pra array RGB.
  2. Para cada curva, isolar pixels matching a cor da curva (com tolerância).
  3. Calibrar eixos: marcadores de pixel → coordenadas de dados.
  4. Reduzir nuvem de pixels a "1 ponto por coluna x" (mediana das y matching).
  5. Otimizar parâmetros (A_s, L_eff, Phi, F0_ref) para minimizar erro contra
     os pontos extraídos.

Configuração calibrada manualmente após inspecionar pixels dos JPEGs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.optimize import least_squares


# --------------------------------------------------------------------------- #
# Calibração de eixos por inspeção
# --------------------------------------------------------------------------- #
#
# Para cada figura, especificamos:
#   - px_x0, px_y0: pixel correspondente ao canto inferior-esquerdo do
#     plot area (i.e., (x_data=x_min, y_data=y_min))
#   - px_x1, px_y1: pixel correspondente ao canto superior-direito do
#     plot area (i.e., (x_data=x_max, y_data=y_max))
#   - x_min, x_max, y_min, y_max: valores de dado correspondentes
#
# Esses números são extraídos por inspeção visual dos JPEGs (gridlines/ticks).
#
# Vão ser ajustados após primeiro carregamento — script imprime tamanho.

@dataclass
class AxisCalib:
    """Mapeamento pixel ↔ dados para um plot retangular."""
    px_x0: int
    px_y0: int
    px_x1: int
    px_y1: int
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    # Bounding box da legenda (em pixels) para excluir da extração.
    legend_px: Tuple[int, int, int, int] = (0, 0, 0, 0)  # x0, y0, x1, y1

    def pixel_to_data(self, px: float, py: float) -> Tuple[float, float]:
        fx = (px - self.px_x0) / (self.px_x1 - self.px_x0)
        fy = (py - self.px_y0) / (self.px_y1 - self.px_y0)
        x = self.x_min + fx * (self.x_max - self.x_min)
        y = self.y_min + fy * (self.y_max - self.y_min)
        return x, y


@dataclass
class CurveSpec:
    """Especificação de uma curva pra extrair: cor RGB target + label."""
    name: str
    rgb: Tuple[int, int, int]
    tolerance: int = 50

    def mask(self, img: np.ndarray) -> np.ndarray:
        r, g, b = self.rgb
        return ((np.abs(img[..., 0].astype(int) - r) < self.tolerance) &
                (np.abs(img[..., 1].astype(int) - g) < self.tolerance) &
                (np.abs(img[..., 2].astype(int) - b) < self.tolerance))


# --------------------------------------------------------------------------- #
# Extração: imagem -> curvas (x, y data)
# --------------------------------------------------------------------------- #

def extract_curve_points(
    img: np.ndarray,
    calib: AxisCalib,
    spec: CurveSpec,
    min_count_per_col: int = 1,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Para uma curva de cor `spec.rgb`, retorna (x_data, y_data) ordenados por x.
    Para cada coluna de pixels onde haja pixels matching, usa mediana de y.
    """
    H, W, _ = img.shape
    mask = spec.mask(img)

    # restrict to plot area (avoid legend/axes)
    x0, x1 = sorted([calib.px_x0, calib.px_x1])
    y0, y1 = sorted([calib.px_y0, calib.px_y1])
    crop = np.zeros_like(mask)
    crop[y0:y1+1, x0:x1+1] = True
    mask &= crop
    # Excluir bounding box da legenda
    lx0, ly0, lx1, ly1 = calib.legend_px
    if lx1 > lx0 and ly1 > ly0:
        mask[ly0:ly1+1, lx0:lx1+1] = False

    xs, ys = [], []
    for col in range(W):
        rows = np.where(mask[:, col])[0]
        if len(rows) >= min_count_per_col:
            y_pix = float(np.median(rows))
            x_data, y_data = calib.pixel_to_data(col, y_pix)
            xs.append(x_data)
            ys.append(y_data)
    return np.array(xs), np.array(ys)


# --------------------------------------------------------------------------- #
# Modelo bilinear (mesmo do replot_studs.py)
# --------------------------------------------------------------------------- #

@dataclass
class JointModel:
    E: float = 200e9
    A_s: float = 200e-6
    L_eff: float = 0.060
    Phi: float = 0.10

    @property
    def k_b(self) -> float: return self.E * self.A_s / self.L_eff

    @property
    def k_j(self) -> float: return self.k_b * (1 - self.Phi) / self.Phi

    def gap(self, F_ext_N: np.ndarray, F0_N: float) -> np.ndarray:
        F_sep = F0_N / (1 - self.Phi)
        g_pre = (1 - self.Phi) * F_ext_N / self.k_j
        g_post = F0_N / self.k_j + (F_ext_N - F_sep) / self.k_b
        return np.where(F_ext_N < F_sep, g_pre, g_post)

    def strain(self, F_ext_N: np.ndarray, F0_N: float) -> np.ndarray:
        F_sep = F0_N / (1 - self.Phi)
        F_bolt = np.where(F_ext_N < F_sep, F0_N + self.Phi * F_ext_N, F_ext_N)
        return F_bolt / (self.E * self.A_s)


# --------------------------------------------------------------------------- #
# Pipeline pra Plot 1
# --------------------------------------------------------------------------- #

# Cores reais amostradas dos JPEGs (paleta Excel default).
PLOT1_CURVES = [
    CurveSpec(name="100%", rgb=(64, 96, 128),  tolerance=40),   # dark blue
    CurveSpec(name="90%",  rgb=(192, 128, 64), tolerance=40),   # orange
    CurveSpec(name="80%",  rgb=(128, 160, 96), tolerance=40),   # olive green
    CurveSpec(name="75%",  rgb=(96, 160, 192), tolerance=60),   # light blue/cyan
]
PLOT1_PCTS = [100, 90, 80, 75]

PLOT2_CURVES = [
    CurveSpec(name="200",  rgb=(32, 96, 128),  tolerance=40),   # blue
    CurveSpec(name="400",  rgb=(192, 128, 64), tolerance=40),   # orange
    CurveSpec(name="600",  rgb=(64, 128, 64),  tolerance=40),   # green
    CurveSpec(name="800",  rgb=(160, 64, 64),  tolerance=40),   # red
]
PLOT2_PRE = [200, 400, 600, 800]


def fit_plot1(
    curves_data: Dict[str, Tuple[np.ndarray, np.ndarray]],
) -> JointModel:
    """
    Otimiza A_s, L_eff, Phi, F0_ref para minimizar gap residuals
    em todas as curvas do plot 1.
    """
    pcts = np.array(PLOT1_PCTS, dtype=float)

    def residuals(params):
        A_s, L_eff, Phi, F0_ref_kN = params
        model = JointModel(E=200e9, A_s=A_s, L_eff=L_eff, Phi=Phi)
        res = []
        for name, pct in zip([c.name for c in PLOT1_CURVES], pcts):
            x_kN, y_mm = curves_data[name]
            if len(x_kN) == 0:
                continue
            F0 = F0_ref_kN * 1e3 * (pct / 100.0)
            pred_mm = model.gap(x_kN * 1e3, F0) * 1e3
            res.extend((pred_mm - y_mm).tolist())
        return np.array(res)

    x0 = [200e-6, 0.060, 0.10, 40.0]
    bounds = ([50e-6, 0.020, 0.02, 10.0],
              [600e-6, 0.200, 0.80, 100.0])
    result = least_squares(residuals, x0, bounds=bounds, method='trf')
    A_s, L_eff, Phi, F0_ref = result.x
    model = JointModel(A_s=A_s, L_eff=L_eff, Phi=Phi)
    print(f"  Plot 1 fit converged: cost = {result.cost:.4e}")
    print(f"    A_s     = {A_s*1e6:7.2f} mm²")
    print(f"    L_eff   = {L_eff*1e3:7.2f} mm")
    print(f"    Phi     = {Phi:7.4f}")
    print(f"    F0_ref  = {F0_ref:7.2f} kN")
    return model, F0_ref


def fit_plot2(
    curves_data: Dict[str, Tuple[np.ndarray, np.ndarray]],
    fixed_A_s: float | None = None,
) -> Tuple[JointModel, float]:
    """
    Otimiza A_s, L_eff, Phi para minimizar strain residuals
    em todas as curvas do plot 2.
    """
    pre_eps = np.array(PLOT2_PRE, dtype=float)

    def residuals(params):
        if fixed_A_s is None:
            A_s, L_eff, Phi = params
        else:
            A_s = fixed_A_s
            L_eff, Phi = params
        model = JointModel(E=200e9, A_s=A_s, L_eff=L_eff, Phi=Phi)
        res = []
        for name, eps in zip([c.name for c in PLOT2_CURVES], pre_eps):
            x_kN, y_ustrain = curves_data[name]
            if len(x_kN) == 0:
                continue
            F0 = eps * 1e-6 * model.E * model.A_s
            pred_ustrain = model.strain(x_kN * 1e3, F0) * 1e6
            res.extend((pred_ustrain - y_ustrain).tolist())
        return np.array(res)

    if fixed_A_s is None:
        x0 = [200e-6, 0.060, 0.10]
        bounds = ([50e-6, 0.020, 0.02], [600e-6, 0.200, 0.80])
        result = least_squares(residuals, x0, bounds=bounds, method='trf')
        A_s, L_eff, Phi = result.x
    else:
        x0 = [0.060, 0.10]
        bounds = ([0.020, 0.02], [0.200, 0.80])
        result = least_squares(residuals, x0, bounds=bounds, method='trf')
        L_eff, Phi = result.x
        A_s = fixed_A_s
    model = JointModel(A_s=A_s, L_eff=L_eff, Phi=Phi)
    print(f"  Plot 2 fit converged: cost = {result.cost:.4e}")
    print(f"    A_s     = {A_s*1e6:7.2f} mm²")
    print(f"    L_eff   = {L_eff*1e3:7.2f} mm")
    print(f"    Phi     = {Phi:7.4f}")
    return model


# --------------------------------------------------------------------------- #
# Orquestração
# --------------------------------------------------------------------------- #

def run(here: Path, calib1: AxisCalib, calib2: AxisCalib) -> None:
    # --- Plot 1 ---
    print("=== Plot 1: gap vs F_ext ===")
    img1 = np.array(Image.open(here / "Carga_x_espacamento.jpeg").convert("RGB"))
    print(f"  image size: {img1.shape[1]}x{img1.shape[0]} px")
    data1 = {}
    for spec in PLOT1_CURVES:
        x, y = extract_curve_points(img1, calib1, spec)
        print(f"  {spec.name:>5s}: {len(x):4d} points extracted "
              f"(x in [{x.min():.1f},{x.max():.1f}] kN, "
              f"y in [{y.min():.3f},{y.max():.3f}] mm)" if len(x) else
              f"  {spec.name:>5s}: NO POINTS EXTRACTED (check color/calib)")
        data1[spec.name] = (x, y)
    model1, F0_ref1 = fit_plot1(data1)

    # --- Plot 2 ---
    print("\n=== Plot 2: strain vs F_app ===")
    img2 = np.array(Image.open(here / "deformação_parafuso_x_carga.jpeg").convert("RGB"))
    print(f"  image size: {img2.shape[1]}x{img2.shape[0]} px")
    data2 = {}
    for spec in PLOT2_CURVES:
        x, y = extract_curve_points(img2, calib2, spec)
        print(f"  {spec.name:>5s}: {len(x):4d} points extracted "
              f"(x in [{x.min():.1f},{x.max():.1f}] kN, "
              f"y in [{y.min():.0f},{y.max():.0f}] ustrain)" if len(x) else
              f"  {spec.name:>5s}: NO POINTS EXTRACTED (check color/calib)")
        data2[spec.name] = (x, y)
    model2 = fit_plot2(data2, fixed_A_s=model1.A_s)

    # --- Plot overlays ---
    _plot_overlay_plot1(here, data1, model1, F0_ref1)
    _plot_overlay_plot2(here, data2, model2)


def _plot_overlay_plot1(here, data, model, F0_ref_kN):
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = {"100%": "#1f77b4", "90%": "#ff7f0e",
              "80%":  "#2ca02c", "75%": "#17becf"}
    F_ext = np.linspace(0, 100e3, 400)
    for spec in PLOT1_CURVES:
        c = colors[spec.name]
        x_ext, y_ext = data[spec.name]
        ax.scatter(x_ext, y_ext, s=4, color=c, alpha=0.35, label=f"{spec.name} (extracted)")
        pct = float(spec.name.replace("%", ""))
        F0 = F0_ref_kN * 1e3 * pct / 100.0
        ax.plot(F_ext / 1e3, model.gap(F_ext, F0) * 1e3,
                color=c, linewidth=1.4, label=f"{spec.name} (fit)")
    ax.set_xlabel("Carga axial externa [kN]")
    ax.set_ylabel("Espaçamento entre flanges [mm]")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 0.11)
    ax.grid(True, alpha=0.4)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(here / "fit_carga_x_espacamento.png", dpi=140, bbox_inches="tight")


def _plot_overlay_plot2(here, data, model):
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = {"200": "#1f77b4", "400": "#ff7f0e",
              "600": "#2ca02c", "800": "#d62728"}
    F_ext = np.linspace(0, 40e3, 400)
    for spec in PLOT2_CURVES:
        c = colors[spec.name]
        x_ext, y_ext = data[spec.name]
        ax.scatter(x_ext, y_ext, s=4, color=c, alpha=0.35, label=f"{spec.name} (extracted)")
        eps_pre = float(spec.name)
        F0 = eps_pre * 1e-6 * model.E * model.A_s
        ax.plot(F_ext / 1e3, model.strain(F_ext, F0) * 1e6,
                color=c, linewidth=1.4, label=f"{spec.name} ustrain (fit)")
    ax.set_xlabel("Força aplicada, kN")
    ax.set_ylabel(r"Deformação no parafuso, $\mu$strain")
    ax.set_xlim(0, 40)
    ax.set_ylim(0, 1400)
    ax.grid(True, alpha=0.4)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(here / "fit_deformacao_x_carga.png", dpi=140, bbox_inches="tight")


if __name__ == "__main__":
    here = Path(__file__).resolve().parent

    # Calibração será refinada após primeiro run — começamos com chutes
    # baseados em estrutura típica de matplotlib + dimensões esperadas.
    # O script imprime o tamanho da imagem; ajustar manualmente depois.
    img1 = np.array(Image.open(here / "Carga_x_espacamento.jpeg").convert("RGB"))
    H1, W1 = img1.shape[:2]
    print(f"Plot 1 dimensions: {W1} x {H1}")
    img2 = np.array(Image.open(here / "deformação_parafuso_x_carga.jpeg").convert("RGB"))
    H2, W2 = img2.shape[:2]
    print(f"Plot 2 dimensions: {W2} x {H2}")

    # Calibrações refinadas após inspeção:
    #   Plot 1 (522x285): legenda ocupa top-left, plot area começa abaixo dela.
    #   Plot 2 (827x600): legenda ocupa top-left, plot area maior.
    calib1 = AxisCalib(
        px_x0=int(W1 * 0.095), px_y0=int(H1 * 0.88),
        px_x1=int(W1 * 0.98),  px_y1=int(H1 * 0.06),
        x_min=0.0, x_max=100.0, y_min=0.0, y_max=0.100,
        # Legenda: top-left ~30% x ~15%
        legend_px=(int(W1 * 0.10), 0, int(W1 * 0.50), int(H1 * 0.20)),
    )
    calib2 = AxisCalib(
        px_x0=int(W2 * 0.10), px_y0=int(H2 * 0.90),
        px_x1=int(W2 * 0.98), px_y1=int(H2 * 0.04),
        x_min=0.0, x_max=40.0, y_min=0.0, y_max=1400.0,
        # Legenda maior em Plot 2 (4 linhas longas)
        legend_px=(int(W2 * 0.12), int(H2 * 0.03),
                   int(W2 * 0.55), int(H2 * 0.30)),
    )

    run(here, calib1, calib2)
