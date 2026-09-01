# -*- coding: utf-8 -*-
"""Recuperacao ROUSSEAU fase 1 — digitaliza a Fig. 6 (p.8) do PDF oficial.

Prereg: specs/2026-08-01-rousseau-recuperacao-prereg.md (emenda assinada:
a Fig. 10 e' HISTERESE; o held-out passa a ser a Fig. 6).

Conteudo VETADO na imagem (nao em caption): preload F_b vs No. of cycles,
0-100 ciclos, eixo esquerdo 0-4000 N; membros t10 a 0.2 mm, F0 ~3.5 kN.
Quatro tracos: Fb(Steel) VERMELHO solido 3.6k->0.6k, Fb(HDPE) PRETO grosso
3.55k->2.8k, e as ROTACOES (eixo direito 0-9 deg) que DIVIDEM AS CORES —
Rot.(Steel) vermelha tracejada e Rot.(HDPE) preta traco-ponto, ambas
SUBINDO. A vermelha de rotacao CRUZA a de preload em ~ciclo 50.

Como o cruzamento e' resolvido: preload so DESCE (y do pixel so cresce) e
rotacao so SOBE — o tracer aceita apenas runs com y >= y_prev - TOL. Sem
isto o traco pula para a rotacao no cruzamento.

Legenda (dentro do grafico, x~460-1010 / y~810-1110 no recorte a 600dpi)
mascarada: as amostras de linha da legenda tem as MESMAS cores.

Saida: digitized_csv/rousseau2025_{steel,hdpe}_t10_amp0p2.csv
       (cycle,F_over_F0 com F0 = 1o ponto) + overlay no scratchpad.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

try:
    import fitz
    from PIL import Image
except ImportError as e:
    raise SystemExit(f"dependencia: {e}")

ROOT = pathlib.Path(__file__).resolve().parents[1]
PDF = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library"
       / "pdfs_open_access" / "rousseau2025_materials_M12.pdf")
OUTD = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library"
        / "digitized_csv")
SCRATCH = pathlib.Path(r"C:\Users\leo_r\AppData\Local\Temp\claude"
                       r"\C--Users-leo-r-OneDrive-BPL-Analitical-BAS-V2"
                       r"\a77f4ade-d869-46d0-a5cf-dcf42fd5edae\scratchpad")

PAGINA = 7          # p.8 (0-based)
N_TOPO = 4000.0     # topo da moldura = 4,000 N (eixo esquerdo)
TOL_SOBE = 12       # px de folga p/ ruido do traco (preload nao sobe)
SALTO_MAX = 30      # px: descontinuidade aceita entre colunas vizinhas


def _bbox_da_figura(page):
    """clip = bbox dos paths grandes do topo da pagina (a figura e' vetor)."""
    xs0, ys0, xs1, ys1 = [], [], [], []
    for dr in page.get_drawings():
        r = dr["rect"]
        if r.width > 20 and r.height > 20 and r.y0 < 420:
            xs0.append(r.x0), ys0.append(r.y0)
            xs1.append(r.x1), ys1.append(r.y1)
    assert xs0, "nenhum path grande na metade de cima da pagina"
    return (min(xs0) - 6, min(ys0) - 6, max(xs1) + 6, max(ys1) + 6)


def _moldura(dark):
    """bordas = clusters de linhas quase-completas (4 lados distintos)."""
    H, W = dark.shape
    rows = [y for y in range(H) if dark[y].sum() > 0.5 * W]
    cols = [x for x in range(W) if dark[:, x].sum() > 0.5 * H]

    def clusters(v):
        out, cur = [], [v[0]]
        for a in v[1:]:
            if a - cur[-1] <= 3:
                cur.append(a)
            else:
                out.append(sum(cur) / len(cur))
                cur = [a]
        out.append(sum(cur) / len(cur))
        return out

    rc, cc = clusters(rows), clusters(cols)
    # a moldura do grafico = os DOIS clusters mais separados (o texto da
    # pagina tambem gera linhas horizontais fortes acima do grafico)
    fy_t, fy_b = rc[-2], rc[-1]
    fx_l, fx_r = cc[0], cc[-1]
    assert fy_b - fy_t > 500 and fx_r - fx_l > 800, (
        f"moldura implausivel: x[{fx_l},{fx_r}] y[{fy_t},{fy_b}]")
    return fx_l, fx_r, fy_t, fy_b


def _ticks_x(dark, fx_l, fx_r, fy_b):
    """ticks maiores do eixo x (apontam p/ FORA, ~10-14px)."""
    H = dark.shape[0]
    faixa = dark[int(fy_b) + 3:min(int(fy_b) + 16, H), :]
    hits = [x for x in range(int(fx_l), int(fx_r) + 1)
            if faixa[:, x].sum() >= 7]
    if not hits:
        return []
    cl, cur = [], [hits[0]]
    for v in hits[1:]:
        if v - cur[-1] <= 5:
            cur.append(v)
        else:
            cl.append(sum(cur) / len(cur))
            cur = [v]
    cl.append(sum(cur) / len(cur))
    return cl


def _runs(col):
    ys = np.where(col)[0]
    if ys.size == 0:
        return []
    out, cur = [], [ys[0]]
    for v in ys[1:]:
        if v - cur[-1] <= 3:
            cur.append(v)
        else:
            out.append(cur)
            cur = [v]
    out.append(cur)
    return out


def _trace_preload(mask, x_ini, x_fim, y_ini):
    """segue o traco de PRELOAD: monotonico p/ baixo (y so cresce), run
    mais proximo do y anterior. E' o que separa preload de rotacao no
    cruzamento — por FORMA, nao por cor.

    O salto tolerado CRESCE com o vao (`SALTO_MAX + 1.2*vazios`): apos uma
    lacuna (mascara da legenda, cruzamento, dash) a curva real ja desceu —
    com salto fixo o tracer morre na borda da mascara (medido: parava em
    x=958 de 1896). A monotonicidade continua sendo a guarda contra pular
    para a curva de rotacao."""
    xs, ys = [], []
    y_prev = float(y_ini)
    vazios = 0
    for x in range(int(x_ini), int(x_fim)):
        salto_ok = SALTO_MAX + 1.2 * vazios
        cands = [r for r in _runs(mask[:, x])
                 if float(np.median(r)) >= y_prev - TOL_SOBE
                 and abs(float(np.median(r)) - y_prev) <= salto_ok]
        if not cands:
            vazios += 1
            if vazios > 60:
                break
            continue
        vazios = 0
        y = float(np.median(min(
            cands, key=lambda r: abs(float(np.median(r)) - y_prev))))
        xs.append(x)
        ys.append(y)
        y_prev = max(y, y_prev - TOL_SOBE)
    return np.array(xs, float), np.array(ys, float)


def main() -> int:
    doc = fitz.open(str(PDF))
    page = doc[PAGINA]
    clip = _bbox_da_figura(page)
    pix = page.get_pixmap(dpi=600, clip=fitz.Rect(*clip))
    A = np.asarray(Image.frombytes("RGB", (pix.width, pix.height),
                                   pix.samples), dtype=np.int16)
    H, W, _ = A.shape
    R, G, B = A[..., 0], A[..., 1], A[..., 2]
    red = (R > 140) & (R - G > 50) & (R - B > 50)
    dark = (R < 110) & (G < 110) & (B < 110)

    fx_l, fx_r, fy_t, fy_b = _moldura(dark)
    tx = _ticks_x(dark, fx_l, fx_r, fy_b)
    print(f"clip={tuple(round(c,1) for c in clip)} shape=({H},{W})")
    print(f"moldura x[{fx_l:.0f},{fx_r:.0f}] y[{fy_t:.0f},{fy_b:.0f}] "
          f"ticks-x {[round(v) for v in tx]}")
    # x: ticks de 10 em 10 a partir de 0 no 1o tick (== borda esquerda)
    assert len(tx) >= 8, f"ticks-x insuficientes: {tx}"
    passo = float(np.mean(np.diff(tx))) / 10.0        # px por ciclo
    assert np.std(np.diff(tx)) < 6, f"ticks nao uniformes: {np.diff(tx)}"
    x0 = tx[0]

    def px2cyc(x):
        return (x - x0) / passo

    def px2N(y):
        return N_TOPO * (fy_b - y) / (fy_b - fy_t)

    dentro = np.zeros((H, W), bool)
    dentro[int(fy_t) + 5:int(fy_b) - 5, int(fx_l) + 5:int(fx_r) - 5] = True
    # legenda DENTRO do grafico: as amostras de linha tem as MESMAS cores.
    # Mascara POR COR (medido): o vermelho so precisa cobrir as amostras
    # (x 440-700) — a curva de preload passa por x~958-1010 nessa faixa de
    # y e uma mascara larga a engolia (o tracer morria em x=958). O preto
    # precisa cobrir tambem o TEXTO da legenda (ate x~1010), e ali nenhuma
    # curva preta passa (o preload HDPE fica em y 459-654).
    leg_red = np.zeros((H, W), bool)
    leg_red[810:1110, 440:700] = True
    leg_blk = np.zeros((H, W), bool)
    leg_blk[810:1110, 440:1010] = True
    redm = red & dentro & ~leg_red
    blackm = dark & dentro & ~leg_blk

    y_35 = fy_b - (fy_b - fy_t) * 3500.0 / N_TOPO
    xs_r, ys_r = _trace_preload(redm, fx_l + 12, fx_r - 10, y_35)
    xs_b, ys_b = _trace_preload(blackm, fx_l + 12, fx_r - 10, y_35)

    OUTD.mkdir(parents=True, exist_ok=True)
    audit = {}
    for nome, xs, ys, fim_lo, fim_hi in (
            ("steel", xs_r, ys_r, 300.0, 1100.0),
            ("hdpe", xs_b, ys_b, 2500.0, 3100.0)):
        assert xs.size > 800, f"{nome}: traco curto ({xs.size} colunas)"
        cyc = px2cyc(xs)
        Nn = px2N(ys)
        F0 = float(np.median(Nn[:10]))
        fim = float(np.median(Nn[-10:]))
        print(f"{nome}: {xs.size} col · F0={F0:.0f} N · fim={fim:.0f} N · "
              f"span {cyc[0]:.1f}-{cyc[-1]:.1f} ciclos")
        # G1 (round-trip contra a leitura da figura)
        assert 3400.0 <= F0 <= 3750.0, f"{nome}: F0 {F0:.0f} fora de ~3.5k"
        assert fim_lo <= fim <= fim_hi, f"{nome}: fim {fim:.0f} fora"
        assert cyc[-1] > 90.0, f"{nome}: span curto ({cyc[-1]:.0f} ciclos)"
        grade = np.arange(np.ceil(max(cyc[0], 0.0)), cyc[-1] + 1e-9, 1.0)
        rs = np.interp(grade, cyc, Nn) / F0
        assert rs.size >= 30, f"{nome}: {rs.size} pts"
        csv = OUTD / f"rousseau2025_{nome}_t10_amp0p2.csv"
        with open(csv, "w", encoding="utf-8", newline="") as f:
            f.write("cycle,F_over_F0\n")
            for c, r in zip(grade, rs):
                f.write(f"{c:.0f},{r:.4f}\n")
        audit[nome] = dict(F0_N=F0, fim_N=fim, pts=int(rs.size),
                           fim_ratio=float(rs[-1]))
        print(f"  -> {csv.name}: {rs.size} pts, fim {rs[-1]:.3f} F/F0")

    dbg = A.copy()
    for xs, ys, cor in ((xs_r, ys_r, (0, 200, 0)), (xs_b, ys_b, (0, 120, 255))):
        for x, y in zip(xs.astype(int), ys.astype(int)):
            dbg[max(y - 1, 0):y + 2, x] = cor
    Image.fromarray(dbg.astype(np.uint8)).save(
        SCRATCH / "rousseau_fig6_overlay.png")
    with open(SCRATCH / "rousseau_fig6_audit.json", "w",
              encoding="utf-8") as f:
        json.dump(audit, f, indent=1)
    print("G1 PASSOU (asserts) · overlay + audit no scratchpad")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
