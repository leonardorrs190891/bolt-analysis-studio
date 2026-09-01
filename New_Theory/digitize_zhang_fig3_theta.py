# -*- coding: utf-8 -*-
"""Digitaliza os DOIS tracos da Fig. 3 do Zhang 2006 (P e theta vs N).

Raster embutido no PDF (xref 11, 995x541, polaridade invertida: traco branco
sobre fundo preto). Calibracao medida nos ticks (2026-08-20):
  x LOG:  10^0 -> px 135 ... 10^4 -> px 905  (192,5 px/decada, 5 decadas medidas)
  y LIN:  100% -> py 13 ... 0% -> py 411     (79,6 px / 20%)
  demarcacao Stage I/II desenhada: px 560 -> N = 161 (theta = 0,5 deg, texto do paper)

Tracking por CONTINUIDADE (nao por posicao absoluta): comeca P no topo-esquerda
e theta no fundo-esquerda; a cada coluna escolhe o run brilhante mais proximo
da posicao anterior. Exclui a linha horizontal das setas (py 124-125), a
vertical de demarcacao (px 560-561) e textos (runs a mais de TOL px do traco).

Saida: New_Theory/zhang2006_fig3_theta_trace.csv (N, P_frac, theta_pct_eixoP)
— theta em % da ESCALA DO EIXO P (a figura nao rotula o eixo theta; a ancora
de escala fisica e theta(N=161) = 0,5 deg, aplicada na analise, nao aqui).
"""
import sys
import io
import numpy as np
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

RAW = r"C:\Users\leo_r\.claude\jobs\3d12ac81\tmp\zhang_fig3_raw.png"
OUT = "New_Theory/zhang2006_fig3_theta_trace.csv"

X0_PX, PX_DEC = 135.0, 192.5          # 10^0 e px/decada
Y100_PX, Y0_PX = 13.0, 411.0          # 100% e 0%
COL_INI, COL_FIM = 130, 969
TOL = 22                              # salto maximo do traco entre colunas (px)


def n_of(px: float) -> float:
    return 10.0 ** ((px - X0_PX) / PX_DEC)


def pct_of(py: float) -> float:
    return (Y0_PX - py) / (Y0_PX - Y100_PX) * 100.0


def runs_da_coluna(b: np.ndarray, x: int):
    """Runs brilhantes (ini, fim, centro) na coluna x, fora da moldura."""
    col = b[:, x].copy()
    col[123:127] = False              # linha das setas Stage I/II
    col[416:] = False                 # eixo x e abaixo
    col[:6] = False
    out, i = [], 0
    H = len(col)
    while i < H:
        if col[i]:
            j = i
            while j + 1 < H and col[j + 1]:
                j += 1
            out.append((i, j, 0.5 * (i + j)))
            i = j + 1
        else:
            i += 1
    return out


def track(b: np.ndarray, y_ini: float, sentido_theta: bool):
    """Segue um traco por continuidade. Devolve dict px_coluna -> py_centro."""
    pos, tr = y_ini, {}
    for x in range(COL_INI, COL_FIM + 1):
        if 559 <= x <= 562:           # linha de demarcacao vertical
            continue
        rs = runs_da_coluna(b, x)
        if not rs:
            continue
        # candidato mais proximo da posicao corrente
        cand = min(rs, key=lambda r: abs(r[2] - pos))
        if abs(cand[2] - pos) > TOL:
            continue                  # texto/seta longe do traco: ignora
        # runs muito compridos = trecho quase-vertical (colapso/disparo):
        # registra o extremo na direcao do movimento
        ini, fim, c = cand
        if fim - ini > 40:
            c = float(fim if sentido_theta is False else ini)
        pos = c
        tr[x] = c
    return tr


def main():
    im = np.array(Image.open(RAW).convert("L"))
    b = im > 128

    # P comeca no topo (100%); theta comeca no fundo (~0-1%)
    trP = track(b, y_ini=14.0, sentido_theta=False)
    trT = track(b, y_ini=408.0, sentido_theta=True)

    linhas = ["N,P_frac,theta_pct_eixoP"]
    xs = sorted(set(trP) | set(trT))
    for x in xs:
        n = n_of(x)
        p = pct_of(trP[x]) / 100.0 if x in trP else ""
        t = pct_of(trT[x]) if x in trT else ""
        linhas.append(f"{n:.6g},{p if p == '' else f'{p:.4f}'},"
                      f"{t if t == '' else f'{t:.3f}'}")
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(linhas) + "\n")
    nP, nT = len(trP), len(trT)
    print(f"colunas tracadas: P={nP} theta={nT}  -> {OUT}")
    # ancoras de sanidade
    for alvo, nome in ((135, "N=1"), (560, "demarcacao N=161"), (905, "N=1e4")):
        px = min(trP, key=lambda k: abs(k - alvo))
        print(f"  P @{nome}: px {px} -> N {n_of(px):.0f}, {pct_of(trP[px]):.1f}%")
    pxs = [x for x in trT if x >= 560]
    if pxs:
        px = pxs[0]
        print(f"  theta na demarcacao: {pct_of(trT[px]):.2f}% do eixo P (= 0,5 deg)")


if __name__ == "__main__":
    main()
