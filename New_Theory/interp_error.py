"""Interpolacao PCHIP (monotona por trechos) das curvas EXPERIMENTAIS + erro do
modelo em GRADE DENSA (pedido do professor 2026-07-08): o MAE por pontos avalia
o modelo so onde ha ponto digitalizado; o erro interpolado avalia a FORMA
inteira (500 pts uniformes no dominio comum) — pega desvios entre pontos
esparsos (ex.: inflexao do estagio 3 do Bauer). Grava mae_interp/rmse_interp/
maxerr em report_data.json (nao substitui o mae por pontos — metrica adicional).

Run: python New_Theory/interp_error.py
"""
from __future__ import annotations
import io
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = ROOT / "New_Theory" / "report_data.json"
    rd = json.loads(io.open(p, encoding="utf-8").read())
    worst = []
    for c in rd["gallery"]:
        dx = np.array(c["data"]["x"], float); dy = np.array(c["data"]["y"], float)
        mx = np.array(c["model"]["x"], float); my = np.array(c["model"]["y"], float)
        keep = np.concatenate([[True], np.diff(dx) > 0])       # PCHIP exige x crescente
        dx, dy = dx[keep], dy[keep]
        if len(dx) < 3:
            continue
        f_exp = PchipInterpolator(dx, dy)
        lo, hi = max(dx[0], mx[0]), min(dx[-1], mx[-1])
        g = np.linspace(lo, hi, 500)
        e = np.interp(g, mx, my) - f_exp(g)
        c["mae_interp"] = float(np.mean(np.abs(e)))
        c["rmse_interp"] = float(np.sqrt(np.mean(e ** 2)))
        c["maxerr_interp"] = float(np.max(np.abs(e)))
        c["maxerr_at"] = float(g[int(np.argmax(np.abs(e)))] / max(hi, 1))
        worst.append((c["mae_interp"] - float(c["mae"]), c["csv"], c["source"],
                      float(c["mae"]), c["mae_interp"], c["maxerr_interp"], c["maxerr_at"]))
    io.open(p, "w", encoding="utf-8").write(json.dumps(rd, indent=1, default=float))
    worst.sort(reverse=True)
    print("casos onde o erro INTERPOLADO revela mais que o por-pontos (delta desc):")
    for d, csv, src, m, mi, mx_, at in worst[:12]:
        print(f"  {csv:34s} {src:14s} mae {m:.3f} -> interp {mi:.3f} (+{d:.3f}) "
              f"| maxerr {mx_:.3f} @{at:.0%} do teste")
    alls = [w[4] for w in worst]
    print(f"\nmedia global (interp): {np.mean(alls):.4f} | mediana {np.median(alls):.4f}")


if __name__ == "__main__":
    main()
