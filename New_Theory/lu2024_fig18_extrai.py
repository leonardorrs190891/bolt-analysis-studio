# -*- coding: utf-8 -*-
"""Extracao de pixel das 4 curvas restantes da Fig. 18a do Lu 2024 (molde D-W).

Reusa a calibracao EXATA registrada pelo D-W em
`vector_extractions/lu2024_fig18a_amp1p5_pixel.json` — pagina 16 (0-based),
zoom 8, `px_por_ciclo` 14,495, `N_por_px` 11,5875 — e so troca a mascara de
cor. Reusar a calibracao (em vez de re-derivar) e' de proposito: a linha de
1,5 mm ja tem round-trip validado contra a Tabela 8 (residuos -0,0032 a
+0,0001), entao ela serve de CONTROLE do instrumento nesta execucao.

Cores lidas da propria figura (legenda + area de plot):
    0,25 mm  PRETO      1,5 mm  verde  (0,172, 98)  <- controle D-W
    0,5  mm  vermelho   2,0 mm  violeta(208,120,225)
    1,0  mm  azul

Tabela 8 (p.17, "Specific attenuation of the bolt"), retencao = 1 - atenuacao.

So-leitura: imprime e opcionalmente grava JSON. NAO escreve CSV nenhuma.

    py -3.12 New_Theory/lu2024_fig18_extrai.py [--json out.json]
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
CAL_P = (ROOT / "BAS_V2_papers" / "E. Rodada 4 (deep-research 2026-07-11)"
         / "vector_extractions" / "lu2024_fig18a_amp1p5_pixel.json")

# retencao = 1 - atenuacao (Tabela 8, p.17). None = celula vazia no impresso.
TAB8 = {
    "0p25": {1: 0.829, 10: 0.795, 50: 0.782, 100: 0.780},
    "0p5":  {1: 0.638, 10: 0.465, 50: 0.344, 100: 0.126},
    "1p0":  {1: 0.632, 10: 0.429, 50: 0.121, 100: 0.064},
    "1p5":  {1: 0.504, 10: 0.302, 50: 0.079, 100: 0.004},
    "2p0":  {1: 0.498, 10: 0.173, 50: 0.007, 100: None},
}
SERIES = {                     # rotulo -> (cor alvo, tolerancia)
    "1p5":  ((0, 172, 98), 55),      # CONTROLE (D-W ja validou)
    "0p5":  ((255, 61, 61), 55),
    "1p0":  ((0, 102, 225), 55),
    "2p0":  ((208, 120, 225), 55),
    "0p25": (None, None),            # PRETO: tratado a parte
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    C = json.loads(CAL_P.read_text(encoding="utf-8"))["calib"]
    doc = fitz.open(str(ROOT / C["pdf"]))
    pix = doc[C["page_index0"]].get_pixmap(
        matrix=fitz.Matrix(C["zoom"], C["zoom"]),
        clip=fitz.Rect(*C["clip_pt"]))
    im = np.frombuffer(pix.samples, np.uint8).reshape(
        pix.height, pix.width, pix.n)[:, :, :3].astype(int)
    F = C["frame_px"]
    x0, kx = C["x_calib"]["px_de_x0"], C["x_calib"]["px_por_ciclo"]
    y0, ky = C["y_calib"]["py_de_y0"], C["y_calib"]["N_por_px"]
    print(f"render {im.shape}  x0={x0} px/ciclo={kx}  y0={y0} N/px={ky}\n")

    # mascaras: vizinho-mais-proximo entre as 4 cores + preto, para que
    # nenhuma serie possa roubar pixel de outra por limiar frouxo.
    alvos = {k: np.array(v[0], float) for k, v in SERIES.items() if v[0]}
    nomes = list(alvos)
    M = np.array([alvos[n] for n in nomes])

    reg = im[F["top"]:F["bottom"], F["left"]:F["right"]]
    sat = reg.max(axis=2) - reg.min(axis=2)
    escuro = (sat <= 45) & (reg.sum(axis=2) < 330)          # preto = 0,25 mm
    color = (sat > 45) & (reg.sum(axis=2) < 700)

    # ⚠️ A serie de 0,25 mm e' PRETA, e preto tambem e': a moldura (linhas 0-2
    # e 1122, colunas 0-2 e 1477 — medidas), os tracos de escala e o TEXTO DA
    # LEGENDA. Sem filtrar, a ancora da 0,25 saiu 6781 N contra 11554-12099 das
    # outras: media entre a curva e o eixo.
    MARG = 6
    escuro[:MARG] = escuro[-MARG:] = False
    escuro[:, :MARG] = escuro[:, -MARG:] = False
    # ⚠️ A 1a tentativa cortou por DENSIDADE de coluna (>18 px) e isso comeu o
    # penhasco inicial: o traco passou a comecar no ciclo 2,1, sem o pico de
    # pre-ciclagem, e a ancora saiu 9851 N (ainda errada). A legenda se exclui
    # por RETANGULO — bloco medido em y<300 & x>1100 da regiao —, e ela NAO
    # encosta na curva, que vive em y~328 (9200 N). Densidade nao serve para
    # separar texto de penhasco: os dois sao colunas densas.
    escuro[:300, 1100:] = False
    print(f"mascara preta: {int(escuro.sum())} px apos moldura (margem {MARG})"
          f" + caixa da legenda (y<300, x>1100)")

    yyc, xxc = np.where(color)
    d = np.linalg.norm(reg[color].astype(float)[:, None, :] - M[None], axis=2)
    best, bd = d.argmin(axis=1), d.min(axis=1)
    ok = bd < 70
    yyc, xxc, best = yyc[ok], xxc[ok], best[ok]
    yyk, xxk = np.where(escuro)

    out = {}
    print(f"{'serie':>6}{'ciclo':>7}{'tab8':>8}{'medido':>9}{'delta':>9}  nota")
    for rot in ("1p5", "0p25", "0p5", "1p0", "2p0"):
        if rot == "0p25":
            ys, xs = yyk, xxk
        else:
            sel = best == nomes.index(rot)
            ys, xs = yyc[sel], xxc[sel]
        if not len(xs):
            print(f"{rot:>6}  SEM PIXEL")
            continue
        # coordenadas absolutas + centroide por coluna
        ax = xs + F["left"]
        ay = ys + F["top"]
        # ⚠️ CONVENCAO DE x — o ciclo do paper e' `x_plotado - 1`.
        # A ancora de pre-ciclagem e' plotada em x=1 e o ciclo c em x=c+1
        # (registrado no proprio JSON do D-W e VALIDADO pela Tabela 8). Ler
        # sem o -1 foi o meu erro da 1a passada: o controle de 1,5 mm acusou
        # +0,4581 em c1 e eu o atribui ao "penhasco". Nao era — o traco fica
        # em 11 700 N ate x=1,35 e assenta em 5 920 N (= 0,504, o 1o ciclo da
        # Tabela 8) so' a partir de x~1,7. Assinatura do off-by-one: erro
        # GRANDE onde a curva e' ingreme (c1, c10) e pequeno onde e' plana
        # (c50). O penhasco nao precisa de tratamento nenhum.
        cur = {}
        for cx in np.unique(ax):
            cur[float((cx - x0) / kx - 1.0)] = float(
                (y0 - np.mean(ay[ax == cx])) * ky)
        cs = np.array(sorted(cur))
        vs = np.array([cur[c] for c in cs])
        anc = float(vs[:6].max())            # pico de pre-ciclagem
        serie = {float(c): float(v / anc) for c, v in zip(cs, vs)}
        out[rot] = dict(ancora_N=anc, n_col=len(cs),
                        faixa=[float(cs.min()), float(cs.max())],
                        serie={f"{k:.3f}": v for k, v in serie.items()})
        for cyc, alvo in TAB8[rot].items():
            if alvo is None:
                continue
            if cyc < cs.min() or cyc > cs.max():
                print(f"{rot:>6}{cyc:>7}{alvo:>8.3f}{'--':>9}{'--':>9}  "
                      f"fora do traco ({cs.min():.1f}..{cs.max():.1f})")
                continue
            med = float(np.interp(cyc, cs, vs)) / anc
            nota = "CONTROLE" if rot == "1p5" else ("ok" if abs(med - alvo)
                                                    <= 0.01 else "**")
            print(f"{rot:>6}{cyc:>7}{alvo:>8.3f}{med:>9.4f}"
                  f"{med-alvo:>+9.4f}  {nota}")
            out[rot].setdefault("roundtrip", []).append(
                dict(ciclo=cyc, tab8=alvo, medido=round(med, 4),
                     delta=round(med - alvo, 4)))
        print(f"{'':>6}ancora {anc:>8.0f} N   colunas {len(cs)}   "
              f"ciclos {cs.min():.1f}..{cs.max():.1f}")
        print()

    print("LEITURA: a linha 1p5 e' CONTROLE — o D-W ja a validou contra a")
    print("Tabela 8 (residuos -0,0032..+0,0001). Se ela nao reproduzir aqui,")
    print("o instrumento esta errado e NENHUM outro numero vale.")
    if a.json:
        a.json.write_text(json.dumps(out, indent=1), encoding="utf-8")
        print(f"\njson -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
