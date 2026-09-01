# -*- coding: utf-8 -*-
"""Verifica D-X e D-Y contra o PDF — as adocoes sairam de um PNG de baixa res.

## Por que existe

As adocoes **D-X** (base da `run1p2` 315 -> 331 kN) e **D-Y** (base da `run2p2`
312 -> 333 kN) foram medidas num raster de **1252x790** (`paper_figures/
karlsen_2022__m30.png`). So' depois descobri que ha um **PDF open-access** no
proprio repo (`pdfs_open_access/karlsen2022_M30M42.pdf`), que renderizado a
zoom 8 da ~10x a resolucao linear.

As duas adocoes se sustentam por controle e por predicao cravada — mas foram
medidas com o instrumento pior disponivel quando havia um melhor. Isto
re-mede com o melhor. Ramos:

* bases dentro de ~1 % das adotadas  => CONFIRMA, nada a fazer;
* divergencia material                => as adocoes precisam de revisao, e o
                                         registro tem de dizer isso.

⚠️ O teste NAO e' "a base nova bate a antiga por construcao": a calibracao aqui
e' independente (ticks do PDF), e os CONTROLES sao as curvas cuja base o D-X
mediu como CERTA — `run6.2` (340 kN) e `run7.1` (312 kN).

    py -3.12 New_Theory/karlsen_fig10_pdf_verifica.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

try:
    import fitz
except ImportError:                                        # pragma: no cover
    print("PyMuPDF ausente"); sys.exit(2)

PDF = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library"
       / "pdfs_open_access" / "karlsen2022_M30M42.pdf")
# base ADOTADA por curva (registry apos D-X/D-Y) — o que se quer confirmar
ADOTADO = {"run1.2": 331.0, "run2.2": 333.0, "run6.2": 340.0,
           "run7.1": 312.0, "run14.2": 370.0}


def _ticks(strip, eixo, fm=0.85):
    dk = (strip.sum(axis=2) < 380)
    f = dk.mean(axis=eixo)
    idx = [i for i, v in enumerate(f) if v >= fm]
    if not idx:
        return []
    g, cur = [], [idx[0]]
    for v in idx[1:]:
        if v - cur[-1] <= 3:
            cur.append(v)
        else:
            g.append(sum(cur) / len(cur)); cur = [v]
    g.append(sum(cur) / len(cur))
    return g


def _reticula(g):
    """Maior passo que explica a maioria (varrer ascendente pega divisores)."""
    if len(g) < 3:
        return g
    d = np.diff(g)
    passo = float(np.median(d))
    for cand in sorted({round(v, 1) for v in d}, reverse=True):
        if cand <= 0:
            continue
        k = np.abs(np.array(g) - g[0]) / cand
        if np.mean(np.abs(k - np.round(k)) < 0.06) >= 0.6:
            passo = cand
            break
    b = g[0]
    return [v for v in g
            if abs((v - b) / passo - round((v - b) / passo)) < 0.06]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    ap.add_argument("--zoom", type=int, default=8)
    a = ap.parse_args()

    doc = fitz.open(str(PDF))
    alvo = None
    for pi in range(len(doc)):
        t = doc[pi].get_text()
        if "Fig. 10" in t or "Figure 10" in t or "Test of M30" in t:
            alvo = pi
            print(f"Fig. 10 mencionada na pag {pi}")
            if "Test of M30" in t:
                break
    if alvo is None:
        print("!! Fig. 10 nao localizada"); return 2

    # ⚠️ A pagina 8 tem DUAS figuras (Fig. 9 = SEM, Fig. 10 = o grafico).
    # Unir todos os bboxes de imagem pega a pagina inteira e a moldura some no
    # texto. Ancorar pela LEGENDA: o bloco de imagem imediatamente ACIMA do
    # texto "Fig. 10" e' o grafico.
    y_cap = None
    for b in doc[alvo].get_text("blocks"):
        if "Fig. 10" in b[4]:
            y_cap = b[1]
            break
    if y_cap is None:
        print("!! legenda da Fig. 10 nao encontrada"); return 2
    cands = [b["bbox"] for b in doc[alvo].get_image_info()
             if b["bbox"][3] <= y_cap + 2]
    if not cands:
        print("!! sem imagem acima da legenda"); return 2
    alvo_bb = max(cands, key=lambda b: b[3])       # a mais proxima da legenda
    x0, y0, x1, y1 = alvo_bb
    print(f"legenda em y={y_cap:.0f}; grafico = bbox mais proximo acima")
    print(f"bbox das imagens: ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f})")
    pix = doc[alvo].get_pixmap(matrix=fitz.Matrix(a.zoom, a.zoom),
                               clip=fitz.Rect(x0 - 4, y0 - 4, x1 + 4, y1 + 4))
    im = np.frombuffer(pix.samples, np.uint8).reshape(
        pix.height, pix.width, pix.n)[:, :, :3].astype(int)
    H, W, _ = im.shape
    print(f"render {im.shape}  (o PNG antigo tinha 790x1252)")

    # ⚠️ Esta figura NAO tem moldura escura: o Karlsen plota com LINHAS DE
    # GRADE cinza-claras (foi assim que ela foi lida no PNG). Procurar `dark`
    # devolve zero linhas — o detector do LU nao transporta.
    g = ((np.abs(im[:, :, 0] - im[:, :, 1]) < 14)
         & (np.abs(im[:, :, 1] - im[:, :, 2]) < 14)
         & (im[:, :, 0] > 170) & (im[:, :, 0] < 248))
    linhas = g.sum(axis=1)
    cand = [y for y in range(H) if linhas[y] > 0.45 * W]
    grp, cur = [], [cand[0]] if cand else []
    for y in cand[1:]:
        if y - cur[-1] <= 3:
            cur.append(y)
        else:
            grp.append(sum(cur) / len(cur)); cur = [y]
    if cur:
        grp.append(sum(cur) / len(cur))
    gy = _reticula(grp)
    if len(gy) < 5:
        print(f"!! poucas gridlines ({len(grp)} brutas, {len(gy)} na reticula)")
        return 2
    dy = np.diff(gy)
    TOP, BOT = min(gy), max(gy)
    # extensao horizontal da grade define a area de plot
    linha = g[int(round(gy[len(gy) // 2]))]
    xs = np.where(linha)[0]
    LEF, RIG = int(xs.min()), int(xs.max())
    print(f"gridlines: {len(gy)}  {np.mean(dy):.2f} +- {np.std(dy):.2f} px"
          f"   area x {LEF}..{RIG}")
    if np.std(dy) > 2.0:
        print("!! gridlines irregulares"); return 2
    # rotulos 0,25,...,400 kN (17 linhas no PNG antigo)
    kN_px = 25.0 / float(np.mean(dy))
    y0kn = max(gy)
    print(f"  kN/px {kN_px:.4f}   topo {(y0kn-TOP)*kN_px:.0f} kN")

    out = {}
    print(f"\n{'curva':>8}{'adotado':>9}{'PDF@ciclo1':>12}{'razao':>8}  nota")
    # cores: lidas dos swatches no PNG; conferidas por proximidade aqui
    CORES = {"run1.2": (87, 128, 202), "run2.2": (239, 138, 70),
             "run6.2": (255, 190, 6), "run7.1": (87, 152, 212)}
    nomes = list(CORES)
    M = np.array([CORES[k] for k in nomes], float)
    TOPi, BOTi = int(round(TOP)), int(round(BOT))
    reg = im[TOPi + 3:BOTi - 2, LEF + 3:RIG - 2]
    sat = reg.max(axis=2) - reg.min(axis=2)
    colm = (sat > 40) & (reg.sum(axis=2) < 700)
    yy, xx = np.where(colm)
    if not len(yy):
        print("!! nenhuma cor detectada — paleta do PDF difere do PNG")
        return 2
    dd = np.linalg.norm(reg[colm].astype(float)[:, None, :] - M[None], axis=2)
    best, bd = dd.argmin(axis=1), dd.min(axis=1)
    ok = bd < 70
    yy, xx, best = yy[ok] + TOP + 3, xx[ok] + LEF + 3, best[ok]
    for rot in nomes:
        sel = best == nomes.index(rot)
        if not sel.any():
            print(f"{rot:>8}  SEM PIXEL"); continue
        cx = xx[sel].min()
        s = yy[sel][xx[sel] == cx]
        topo = (y0kn - s.min()) * kN_px
        ad = ADOTADO[rot]
        raz = topo / ad
        nota = "confirma" if abs(raz - 1) <= 0.015 else "** DIVERGE"
        print(f"{rot:>8}{ad:>9.0f}{topo:>12.1f}{raz:>8.3f}  {nota}")
        out[rot] = dict(adotado=ad, pdf=float(topo), razao=float(raz))

    print("\nCONTROLES: run6.2 e run7.1 tiveram a base medida como CERTA pelo")
    print("D-X. Se elas divergirem aqui, o instrumento novo e' que esta errado.")
    if a.json:
        a.json.write_text(json.dumps(out, indent=1), encoding="utf-8")
        print(f"\njson -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
