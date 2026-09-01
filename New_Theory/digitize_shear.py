"""
Digitalizacao manual das 9 curvas de shear.jpeg (M16, +-0.5 mm, 0.5 Hz).

Lendo cada marker visualmente nos pontos de ciclo discretos. Precisao
estimada +-2-3% por leitura.

Saida:
  New_Theory/M16_shear_TP{x}_{cond}.csv (9 files)
  New_Theory/M16_shear_MEAN_{cond}.csv (2 files)
  New_Theory/digitize_shear_verification.png (overview plot)

Formato CSV: 2 colunas (cycle, F_over_F0), header presente, ratios 0-1.
Consumido pelo calibration_tuner.html (auto-normaliza se max > 1.5,
entao serve tanto 0-1 quanto 0-100).
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


# Ciclo ladder comum a todas as curvas (eixo X do grafico)
CYCLES = np.array([0, 20, 50, 75, 100, 200, 300, 400, 500, 1000, 1500, 2000, 2500], dtype=float)

# Leituras manuais em % (eixo Y do grafico)
# Cada linha = uma especimen, valores nas cycles acima
DIGITIZED_PCT = {
    # === Arruela nova (3 specimens, azul tracejado) ===
    "TP3":  [100, 80, 75, 71, 70, 60, 55, 52, 44, 36, 33, 29, 27],   # blue diamond
    "TP8":  [100, 78, 72, 69, 62, 56, 54, 52, 42, 40, 36, 29, 26],   # blue circle
    "TP11": [100, 76, 70, 66, 60, 54, 54, 48, 42, 35, 33, 28, 25],   # blue X
    # === Arruela reusada (4 specimens, vermelho pontilhado) ===
    "TP4":  [100, 80, 73, 71, 70, 58, 53, 45, 33, 11,  6,  1,  1],   # red square
    "TP5":  [100, 81, 77, 73, 70, 65, 53, 47, 36, 13, 10,  3,  1.5], # red triangle
    "TP9":  [100, 80, 75, 73, 71, 67, 57, 45, 31, 11,  6,  1,  1],   # red plus
    "TP10": [100, 87, 77, 75, 73, 65, 56, 48, 39, 18, 15,  9,  8],   # red X
    # === Sobretorque (1 specimen, verde tracejado circulo) ===
    "TP6":  [100, 85, 82, 80, 76, 73, 71, 71, 68, 67, 64, 62, 60],   # green circle
    # === Desaperto + reaperto (1 specimen, verde tracejado diamante) ===
    "TP7":  [100, 70, 57, 55, 53, 38, 33, 18,  8,  1.5, 1, 0.5, 0.5], # green diamond
}

CONDITIONS = {
    "TP3": "nova",
    "TP8": "nova",
    "TP11": "nova",
    "TP4": "reusada",
    "TP5": "reusada",
    "TP9": "reusada",
    "TP10": "reusada",
    "TP6": "sobretorque",
    "TP7": "reaperto",
}

GROUPS = {
    "nova": ["TP3", "TP8", "TP11"],
    "reusada": ["TP4", "TP5", "TP9", "TP10"],
    # sobretorque e reaperto: especimen unico, sem grupo mean (so individual)
}

# Cores para QA plot (correspondentes ao JPEG)
COLORS = {
    "TP3": "#4F81BD", "TP8": "#4F81BD", "TP11": "#4F81BD",
    "TP4": "#C00000", "TP5": "#C00000", "TP9": "#C00000", "TP10": "#C00000",
    "TP6": "#00B050",
    "TP7": "#92D050",
}
MARKERS = {
    "TP3": "D", "TP8": "o", "TP11": "x",
    "TP4": "s", "TP5": "^", "TP9": "P", "TP10": "X",
    "TP6": "o",
    "TP7": "D",
}


def write_csv(path: Path, cycles: np.ndarray, ratios: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cycle", "F_over_F0"])
        for c, r in zip(cycles, ratios):
            w.writerow([int(c), f"{r:.4f}"])


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "New_Theory"

    # 1) Escrever 9 CSVs individuais
    individual_files = []
    for tp, vals in DIGITIZED_PCT.items():
        pct = np.array(vals, dtype=float)
        ratio = pct / 100.0
        fname = f"M16_shear_{tp}_{CONDITIONS[tp]}.csv"
        path = out_dir / fname
        write_csv(path, CYCLES, ratio)
        individual_files.append((tp, path))
        print(f"  wrote {fname}  final={ratio[-1]:.3f}")

    # 2) Escrever 2 CSVs de grupo mean
    group_files = []
    for cond, tps in GROUPS.items():
        mat = np.array([DIGITIZED_PCT[tp] for tp in tps], dtype=float) / 100.0
        mean = mat.mean(axis=0)
        std = mat.std(axis=0)
        fname = f"M16_shear_MEAN_{cond}.csv"
        path = out_dir / fname
        write_csv(path, CYCLES, mean)
        group_files.append((cond, path, mean, std, tps))
        print(f"  wrote {fname}  mean_final={mean[-1]:.3f} +- {std[-1]:.3f}  (n={len(tps)})")

    # 3) QA plot: replicar o JPEG visualmente
    fig, ax = plt.subplots(figsize=(12, 7))

    for tp, vals in DIGITIZED_PCT.items():
        pct = np.array(vals, dtype=float)
        ls = "--" if CONDITIONS[tp] in ("nova", "sobretorque", "reaperto") else ":"
        ax.plot(CYCLES, pct,
                color=COLORS[tp], marker=MARKERS[tp], markersize=8,
                linestyle=ls, linewidth=1.2,
                label=f"{tp} ({CONDITIONS[tp]})")

    # Overlay mean curves grossas
    for cond, _path, mean, std, _tps in group_files:
        color = "#000080" if cond == "nova" else "#800000"
        ax.plot(CYCLES, mean * 100,
                color=color, linestyle="-", linewidth=3, alpha=0.5,
                label=f"MEAN {cond} (n={len(GROUPS[cond])})")
        ax.fill_between(CYCLES, (mean - std) * 100, (mean + std) * 100,
                        color=color, alpha=0.10)

    ax.set_xlabel("Ciclos")
    ax.set_ylabel("Pre-tensao parafuso em %")
    ax.set_title("TP (+- 0.5 mm, 0.5 Hz) -- M16 -- digitalizacao manual")
    ax.set_xlim(0, 2600)
    ax.set_ylim(0, 110)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    plt.tight_layout()

    out_png = root / "New_Theory" / "digitize_shear_verification.png"
    fig.savefig(out_png, dpi=120)
    print(f"\n  QA plot: {out_png}")

    # 4) Tabela de scatter (final retention por specimen)
    print("\n  Final retention (N=2500):")
    for cond, tps in GROUPS.items():
        vals = [DIGITIZED_PCT[tp][-1] for tp in tps]
        print(f"    {cond:12s}  TP{tps}  vals={vals}  mean={np.mean(vals):.1f}%  std={np.std(vals):.1f}%")
    for cond in ("sobretorque", "reaperto"):
        tp = next(tp for tp, c in CONDITIONS.items() if c == cond)
        print(f"    {cond:12s}  TP[{tp!r}]  val={DIGITIZED_PCT[tp][-1]}%")


if __name__ == "__main__":
    main()
