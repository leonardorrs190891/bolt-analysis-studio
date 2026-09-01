# -*- coding: utf-8 -*-
"""A digitalizacao da Fig. 14a esta certa? — CSV commitada contra a figura.

## Por que isto decide algo

`lu2024_redigit_premeasure_resultado.md` afirmou que a subida de
`limite_sres(LU)` (0,1030 -> 0,1361) era "artefato de correcao pela metade",
porque corrigi as fig18/fig20 e nao as fig14. **Essa leitura pressupoe que a
fig14 esta certa** — e a fig14 e' uma REPETICAO INDEPENDENTE (o paper: tres
grupos com pre-cargas iniciais 12 398 / 12 285 / 12 696 N), logo ela
legitimamente difere da corrida tabelada.

Se a digitalizacao da fig14 estiver correta, o piso verdadeiro e' o medido COM
a fig18 corrigida (sigma 0,3044) e o antigo 0,1827 media "fig18 enviesada
contra fig14" — proximo por ACASO. A subida seria REAL, nao artefato.

⚠️ A fig14 NAO tem tabela para conferir (e' corrida de repeticao). O unico
teste disponivel e' CSV-contra-FIGURA: se baterem, a digitalizacao esta boa e
o julgamento passa a ser sobre fisica, nao sobre instrumento.

## Geometria da Fig. 14a (pag. 14, painel esquerdo)

Eixo x = **TEMPO (s)**, 0..1200 — nao ciclos. A 1 Hz, 1 s = 1 ciclo, mas cada
curva tem um transiente de APERTO que comeca em tempos diferentes (t~50, 110,
180 s). A CSV ja sai zerada no pico (`x_offset=0`, registrado no registry),
entao a comparacao alinha pelo pico de cada curva.

    py -3.12 New_Theory/lu2024_fig14_confere.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

try:
    import fitz
except ImportError:                                        # pragma: no cover
    print("PyMuPDF ausente"); sys.exit(2)

from bolt_analysis_studio.validation.case_registry import all_records   # noqa: E402
from bolt_analysis_studio.validation.inputs import load_full_curve      # noqa: E402

PDF = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library"
       / "pdfs_open_access" / "lu2024_sensors_M8.pdf")
PAGE, ZOOM = 14, 8
CLIP = (50, 300, 290, 470)          # painel (a) da Fig. 14
COR = {"amp0p5": (255, 61, 61), "amp1p0": (0, 102, 225)}   # 0,25 = PRETO
CID = {"amp0p5": "lu2024_M8_fig14_amp0p5_long",
       "amp1p0": "lu2024_M8_fig14_amp1p0_long"}


def _ticks(strip, eixo, frac_min=0.85):
    dk = (strip.sum(axis=2) < 380)
    f = dk.mean(axis=eixo)
    idx = [i for i, v in enumerate(f) if v >= frac_min]
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
    base = g[0]
    return [v for v in g
            if abs((v - base) / passo - round((v - base) / passo)) < 0.06]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    pix = fitz.open(str(PDF))[PAGE].get_pixmap(
        matrix=fitz.Matrix(ZOOM, ZOOM), clip=fitz.Rect(*CLIP))
    im = np.frombuffer(pix.samples, np.uint8).reshape(
        pix.height, pix.width, pix.n)[:, :, :3].astype(int)
    H, W, _ = im.shape
    dark = im.sum(axis=2) < 380
    rows, cols = dark.sum(axis=1), dark.sum(axis=0)
    ry = [y for y in range(H) if rows[y] > 0.6 * W]
    rx = [x for x in range(W) if cols[x] > 0.6 * H]
    print(f"render {im.shape}  moldura y {ry[:2]}..{ry[-2:]}  x {rx[:2]}..{rx[-2:]}")
    if len(ry) < 2 or len(rx) < 2:
        print("!! moldura nao encontrada"); return 2
    TOP, BOT, LEF, RIG = ry[0] + 1.5, ry[-1] - 1.0, rx[0] + 1.5, rx[-1] - 1.0

    gy = _reticula([v for v in _ticks(im[:, int(LEF) + 4:int(LEF) + 15], 1)
                    if TOP + 20 < v < BOT + 5])
    # ⚠️ A MOLDURA esquerda (x=301,5) nao e' tick: o rotulo "0" fica ~112 px
    # a direita dela, e 112 nao e' multiplo do passo (225). Ancorar a reticula
    # na moldura descarta tudo — mesmo bug da Fig. 20, terceira ocorrencia.
    gx = _reticula([v for v in _ticks(im[int(BOT) - 14:int(BOT) - 3, :], 0)
                    if v > LEF + 3])
    dy, dx = np.diff(gy), np.diff(gx)
    print(f"ticks y: {len(gy)}  {np.mean(dy):.2f} +- {np.std(dy):.2f} px")
    print(f"ticks x: {len(gx)}  {np.mean(dx):.2f} +- {np.std(dx):.2f} px")
    if np.std(dy) > 2.0 or np.std(dx) > 2.0:
        print("!! ticks irregulares — deteccao contaminada"); return 2
    # eixo y: -2000..14000 de 2000 em 2000 ; eixo x: 0..1200 de 200 em 200
    N_por_px = 2000.0 / float(np.mean(dy))
    S_por_px = 200.0 / float(np.mean(dx))
    y_de_m2000 = max(gy)
    x_de_0 = min(gx)          # 1o tick = 0 s (a moldura fica a esquerda)
    print(f"  N/px {N_por_px:.4f}   s/px {S_por_px:.4f}"
          f"   faixa y {(y_de_m2000-TOP)*N_por_px-2000:.0f} N"
          f"   faixa x {(RIG-x_de_0)*S_por_px:.0f} s")

    nomes = list(COR)
    M = np.array([COR[k] for k in nomes], float)
    reg = im[int(TOP) + 3:int(BOT) - 2, int(LEF) + 3:int(RIG) - 2]
    oy, ox = int(TOP) + 3, int(LEF) + 3
    sat = reg.max(axis=2) - reg.min(axis=2)
    col = (sat > 45) & (reg.sum(axis=2) < 700)
    # ⚠️ 3a ocorrencia da armadilha da LEGENDA nesta campanha (KARLSEN, Fig.18,
    # agora aqui). Os swatches sao tracos horizontais da MESMA cor das series,
    # no canto superior direito. Sem exclui-los, o `argmax` da vermelha caiu no
    # swatch: "pico" em t=821,5 s com valor CONSTANTE por 111 s — a assinatura
    # inconfundivel (curva de relaxacao nao fica plana no maximo). A azul
    # escapou por ACASO, porque o pico real dela (13 203 N) e' mais alto que o
    # swatch; ou seja, o teste passou numa serie e falhou na outra pelo mesmo
    # defeito. Excluido por RETANGULO, medido no render.
    hh, ww = col.shape
    col[:int(0.22 * hh), int(0.55 * ww):] = False
    yy, xx = np.where(col)
    dd = np.linalg.norm(reg[col].astype(float)[:, None, :] - M[None], axis=2)
    best, bd = dd.argmin(axis=1), dd.min(axis=1)
    ok = bd < 70
    yy, xx, best = yy[ok], xx[ok], best[ok]

    recs = {r.case_id: r for r in all_records()}
    out = {}
    print(f"\n{'curva':<32}{'pico fig':>10}{'F0 reg':>9}{'razao':>8}"
          f"{'RMS(CSVxfig)':>14}{'max':>8}")
    for rot in nomes:
        sel = best == nomes.index(rot)
        ay, ax = yy[sel] + oy, xx[sel] + ox
        if not len(ax):
            print(f"{rot:<32}  SEM PIXEL"); continue
        cur = {}
        for cx in np.unique(ax):
            t = (cx - x_de_0) * S_por_px
            cur[float(t)] = float((y_de_m2000 - np.mean(ay[ax == cx]))
                                  * N_por_px - 2000.0)
        ts = np.array(sorted(cur))
        vs = np.array([cur[t] for t in ts])
        i_pico = int(np.argmax(vs))
        pico, t_pico = float(vs[i_pico]), float(ts[i_pico])
        # so' o ramo POS-pico (a subida e' o aperto, nao o ensaio)
        tt, vv = ts[i_pico:] - t_pico, vs[i_pico:] / pico
        cid = CID[rot]
        cyc, rat = load_full_curve(recs[cid].csv_path)
        cyc, rat = np.asarray(cyc, float), np.asarray(rat, float)
        hi = min(tt.max(), cyc.max())
        g = np.linspace(0, hi, 60)
        dif = np.interp(g, tt, vv) - np.interp(g, cyc, rat)
        f0reg = recs[cid].validation_case.initial_preload_N
        print(f"{cid[:32]:<32}{pico:>10.0f}{f0reg:>9.0f}"
              f"{pico/f0reg:>8.3f}{float(np.sqrt(np.mean(dif**2))):>14.4f}"
              f"{float(np.max(np.abs(dif))):>8.4f}")
        out[cid] = dict(pico_figura_N=pico, f0_registry=float(f0reg),
                        rms=float(np.sqrt(np.mean(dif ** 2))),
                        maxdif=float(np.max(np.abs(dif))),
                        janela=[0.0, float(hi)])

    print("\nLEITURA: RMS pequeno (<~0,02) => a CSV reproduz a figura, a")
    print("digitalizacao esta boa, e a SUBIDA DO PISO no premeasure e' REAL,")
    print("nao artefato. RMS grande => a fig14 tambem precisa de correcao e o")
    print("piso so' pode ser medido depois dela.")
    if a.json:
        a.json.write_text(json.dumps(out, indent=1), encoding="utf-8")
        print(f"\njson -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
