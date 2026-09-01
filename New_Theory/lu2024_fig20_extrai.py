# -*- coding: utf-8 -*-
"""Extracao de pixel da Fig. 20a do Lu 2024 — fecha o PAR com a Fig. 18a.

Por que este script existe: a `fig18_amp1p0` e a `fig20_T22Nm` sao o MESMO
ensaio publicado em duas figuras (Tabela 9 @22 N.m e' identica a Tabela 8
@1,0 mm: 36,8/57,1/87,9/93,6). Elas formam o par que da o "piso de
digitalizacao" do LU, e `lu2024_piso_viesado_resultado.md` mediu que AS DUAS
CSVs desviam da tabela na MESMA direcao (+0,0439 e +0,0724 no c10) — logo o
piso mede concordancia, nao acuracia.

Falta a metade que a sonda de pixel ainda nao tocou: a FIGURA 20 concorda com
a Tabela 9? Se sim, o desvio da `fig20_T22Nm` e' inteiramente da CSV, e o par
fica com as duas metades medidas contra o impresso.

Calibracao propria (a Fig. 20 esta noutra pagina e noutro clip que a Fig. 18);
a validacao e' o CONTROLE INTERNO: as 5 curvas contra as 5 linhas da Tabela 9.

Convencao de x: a mesma da Fig. 18 — ancora de pre-ciclagem em x=1, ciclo c do
paper plotado em x=c+1 (registrada no JSON do D-W e re-validada aqui).

    py -3.12 New_Theory/lu2024_fig20_extrai.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

try:
    import fitz
except ImportError:                                        # pragma: no cover
    print("PyMuPDF ausente"); sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
PDF = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library"
       / "pdfs_open_access" / "lu2024_sensors_M8.pdf")
PAGE, ZOOM = 18, 8
CLIP = (50, 270, 290, 450)

# Tabela 9 (p.18, "Specific decay of bolts"), retencao = 1 - decaimento
TAB9 = {
    "T4Nm":  {1: 0.838, 10: 0.453, 50: 0.177, 100: 0.037},
    "T10Nm": {1: 0.638, 10: 0.448, 50: 0.352, 100: 0.309},
    "T16Nm": {1: 0.641, 10: 0.472, 50: 0.242, 100: 0.187},
    "T22Nm": {1: 0.632, 10: 0.429, 50: 0.121, 100: 0.064},
    "T28Nm": {1: 0.617, 10: 0.465, 50: 0.317},
}
COR = {
    "T10Nm": (255, 64, 64), "T16Nm": (0, 102, 225),
    "T22Nm": (0, 172, 98), "T28Nm": (208, 120, 225),
    "T4Nm": None,                                    # PRETO
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    pix = fitz.open(str(PDF))[PAGE].get_pixmap(
        matrix=fitz.Matrix(ZOOM, ZOOM), clip=fitz.Rect(*CLIP))
    im = np.frombuffer(pix.samples, np.uint8).reshape(
        pix.height, pix.width, pix.n)[:, :, :3].astype(int)
    H, W, _ = im.shape

    # ---- moldura (medida no scout) ----------------------------------
    TOP, BOT, LEF, RIG = 62.5, 1220.0, 291.5, 1786.5
    print(f"render {im.shape}  moldura y {TOP}..{BOT}  x {LEF}..{RIG}")

    # ---- calibracao: ticks DENTRO da moldura, filtrados pela RETICULA ---
    # Dois defeitos medidos e consertados aqui:
    # (a) os tracos de escala apontam para DENTRO (a faixa externa
    #     x LEF-22..LEF-6 tem ZERO escuros; a interna, centenas);
    # (b) uma faixa larga captura tambem as CURVAS que a cruzam. A assinatura
    #     e' o espacamento IRREGULAR: a 1a versao deu 128,6 +- 30,9 px (24 %)
    #     onde o D-W registrou 145,0 +- 0,5 na Fig. 18. Tick e' uniforme; se o
    #     desvio-padrao e' grande, o que se detectou nao sao so' ticks.
    # Conserto: exigir que o tick preencha >=85 % da faixa (a curva so' a
    # CRUZA) e depois manter apenas os que caem na reticula dominante.
    def _ticks(strip, eixo):
        dk = (strip.sum(axis=2) < 380)
        frac = dk.mean(axis=eixo)
        idx = [i for i, f in enumerate(frac) if f >= 0.85]
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
        """Mantem so' os ticks compativeis com o passo dominante."""
        if len(g) < 3:
            return g, float("nan")
        d = np.diff(g)
        passo = float(np.median(d))
        # ⚠️ O passo dominante e' o MAIOR que explica a maioria, nao o menor.
        # Varrer ascendente escolhe 71 px — que e' METADE do passo real (142)
        # e portanto explica TODOS os pontos, inclusive os espurios. Foi o que
        # deixou 14 ticks com 115 +- 34,7 px. Varrendo descendente, 143 px
        # explica 11 de 14 e rejeita os 3 marcadores de curva.
        for cand in sorted({round(v, 1) for v in d}, reverse=True):
            if cand <= 0:
                continue
            k = np.abs(np.array(g) - g[0]) / cand
            if np.mean(np.abs(k - np.round(k)) < 0.06) >= 0.6:
                passo = cand
                break
        base = g[0]
        keep = [v for v in g
                if abs((v - base) / passo - round((v - base) / passo)) < 0.06]
        return keep, passo

    # ⚠️ ORDEM IMPORTA: a moldura do TOPO (y=62,5) nao esta na reticula dos
    # ticks internos (174,5 - 62,5 = 112, e o passo e' 149,4). Ancorar a
    # reticula nela descarta TODOS os ticks. Descarta-se a moldura ANTES.
    gy_raw = [v for v in _ticks(im[:, int(LEF) + 4:int(LEF) + 15], 1)
              if v > TOP + 40]
    gy, _ = _reticula(gy_raw)
    dy = np.diff(gy)
    print(f"ticks y: {len(gy)}  espacamento {np.mean(dy):.2f} +- {np.std(dy):.2f} px")
    assert np.std(dy) < 2.0, "ticks y irregulares — deteccao contaminada"
    N_por_px = 2000.0 / float(np.mean(dy))
    y_de_0 = max(gy)
    print(f"  y(0 N) = {y_de_0:.1f}   N/px = {N_por_px:.4f}"
          f"   topo = {(y_de_0-TOP)*N_por_px:.0f} N")

    # mesmo bug espelhado: os rotulos do eixo y (x=246,5 e 261,0) ficam a
    # ESQUERDA da moldura e ancoravam a reticula fora dela. Filtrar ANTES.
    gx_raw = [v for v in _ticks(im[int(BOT) - 14:int(BOT) - 3, :], 0)
              if v >= LEF - 1]
    gx, _ = _reticula(gx_raw)
    dx = np.diff(gx)
    print(f"ticks x: {len(gx)}  espacamento {np.mean(dx):.2f} +- {np.std(dx):.2f} px")
    assert np.std(dx) < 2.0, "ticks x irregulares — deteccao contaminada"
    kx = float(np.mean(dx)) / 10.0
    x_de_0 = min(gx)
    print(f"  x(ciclo 0) = {x_de_0:.1f}   px/ciclo = {kx:.4f}"
          f"   direita = {(RIG-x_de_0)/kx:.1f} ciclos")

    # ---- extracao ----------------------------------------------------
    nomes = [k for k, v in COR.items() if v]
    M = np.array([COR[k] for k in nomes], float)
    reg = im[int(TOP) + 4:int(BOT) - 3, int(LEF) + 4:int(RIG) - 3]
    oy, ox = int(TOP) + 4, int(LEF) + 4
    sat = reg.max(axis=2) - reg.min(axis=2)
    col = (sat > 45) & (reg.sum(axis=2) < 700)
    yy, xx = np.where(col)
    dd = np.linalg.norm(reg[col].astype(float)[:, None, :] - M[None], axis=2)
    best, bd = dd.argmin(axis=1), dd.min(axis=1)
    ok = bd < 70
    yy, xx, best = yy[ok], xx[ok], best[ok]

    out = {}
    print(f"\n{'serie':>7}{'ciclo':>7}{'tab9':>8}{'medido':>9}{'delta':>9}  nota")
    for rot in nomes:
        sel = best == nomes.index(rot)
        ay, ax = yy[sel] + oy, xx[sel] + ox
        if not len(ax):
            print(f"{rot:>7}  SEM PIXEL"); continue
        cur2 = {}
        for cx in np.unique(ax):
            cur2[float((cx - x_de_0) / kx - 1.0)] = float(
                (y_de_0 - np.mean(ay[ax == cx])) * N_por_px)
        cs = np.array(sorted(cur2))
        vs = np.array([cur2[c] for c in cs])
        anc = float(vs[:6].max())
        out[rot] = dict(ancora_N=anc, faixa=[float(cs.min()), float(cs.max())],
                        n_col=len(cs),
                        # serie completa (ciclo -> F/F0) para o premeasure
                        serie={f"{c:.3f}": float(v / anc)
                               for c, v in zip(cs, vs)})
        for cyc, alvo in TAB9[rot].items():
            if cyc < cs.min() or cyc > cs.max():
                print(f"{rot:>7}{cyc:>7}{alvo:>8.3f}{'--':>9}{'--':>9}  fora")
                continue
            med = float(np.interp(cyc, cs, vs)) / anc
            nota = "ok" if abs(med - alvo) <= 0.01 else "**"
            print(f"{rot:>7}{cyc:>7}{alvo:>8.3f}{med:>9.4f}{med-alvo:>+9.4f}"
                  f"  {nota}")
            out[rot].setdefault("roundtrip", []).append(
                dict(ciclo=cyc, tab9=alvo, medido=round(med, 4),
                     delta=round(med - alvo, 4)))
        print(f"{'':>7}ancora {anc:>8.0f} N   ciclos "
              f"{cs.min():.1f}..{cs.max():.1f}")
    print("\nCONTROLE INTERNO: 4 series x 4 ancoras contra a Tabela 9. Se a")
    print("maioria fechar em +-0,01, a calibracao esta certa e o desvio da CSV")
    print("da fig20_T22Nm (+0,0724 no c10) e' da CSV.")
    if a.json:
        a.json.write_text(json.dumps(out, indent=1), encoding="utf-8")
        print(f"\njson -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
