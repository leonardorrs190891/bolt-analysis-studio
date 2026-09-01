# -*- coding: utf-8 -*-
"""Re-digitaliza a Fig. 4 do Rousseau 2025 — foco na curva t10 (10 mm).

Prereg: specs/2026-08-02-rousseau-t10-redigitalizacao-prereg.md
Hipotese: a t10 e' uma BANDA OSCILANTE larga (linha fina e ruidosa; a t12
e a t14 sao tracos limpos) e a digitalizacao antiga seguiu o TOPO da banda
em vez do CENTRO — o que explica ela ser a UNICA das tres a discordar da
Fig. 7, e discordar +5 pontos de retencao nas duas leituras.

Alvo INDEPENDENTE (Fig. 7 lida como retencao; a errata do rotulo esta na
nota de aparato): t10 = 62 % em N=100 e 43 % em N=182.
Controle (G2): t12 -> 80/62 e t14 -> 98/96, que a versao atual ja acerta.

Cores (medidas no recorte a 600 dpi): Fb(10mm) azul-acinzentado CLARO
(~200,200,240) · Fb(12mm) vermelho (240,0,0) · Fb(14mm) preto grosso ·
Rot.(10mm) azul PURO tracejado (0,0,240) — a rotacao SOBE e o preload
DESCE, entao a monotonicidade separa as duas sem depender da cor.

Saida: digitized_csv/rousseau2025_hdpe_t10.csv (SOBRESCREVE apos os gates)
       + overlay e JSON de auditoria no scratchpad.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

try:
    import fitz
    from PIL import Image
except ImportError as e:  # pragma: no cover
    raise SystemExit(f"dependencia: {e}")

ROOT = pathlib.Path(__file__).resolve().parents[1]
PDF = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library"
       / "pdfs_open_access" / "rousseau2025_materials_M12.pdf")
OUTD = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library"
        / "digitized_csv")
SCRATCH = pathlib.Path(r"C:\Users\leo_r\AppData\Local\Temp\claude"
                       r"\C--Users-leo-r-OneDrive-BPL-Analitical-BAS-V2"
                       r"\a77f4ade-d869-46d0-a5cf-dcf42fd5edae\scratchpad")

PAGINA = 6            # p.7
N_TOPO = 4500.0       # topo do eixo esquerdo (Preload, N)
TOL_SOBE = 45         # px de folga. 14 era APERTADO DEMAIS: a banda da t10
                      # oscila ~+-200 N = ~64 px, entao a monotonicidade
                      # matava o traco em 332 de 400 ciclos (medido). 45
                      # deixa a banda respirar e ainda barra a curva de
                      # rotacao, que SOBE monotonicamente centenas de px.
SALTO_BASE = 26


def _runs(col):
    ys = np.where(col)[0]
    if ys.size == 0:
        return []
    out, cur = [], [ys[0]]
    for v in ys[1:]:
        if v - cur[-1] <= 4:
            cur.append(v)
        else:
            out.append(cur)
            cur = [v]
    out.append(cur)
    return out


def _trace(mask, x0, x1, y_ini):
    """centro da banda, monotonico p/ baixo (preload so desce)."""
    xs, ys = [], []
    y_prev = float(y_ini)
    vazios = 0
    for x in range(int(x0), int(x1)):
        salto = SALTO_BASE + 1.2 * vazios
        cands = [r for r in _runs(mask[:, x])
                 if float(np.median(r)) >= y_prev - TOL_SOBE
                 and abs(float(np.median(r)) - y_prev) <= salto]
        if not cands:
            vazios += 1
            if vazios > 80:
                break
            continue
        vazios = 0
        # CENTRO da banda: mediana do run (nao o topo). E' o ponto do prereg.
        y = float(np.median(min(
            cands, key=lambda r: abs(float(np.median(r)) - y_prev))))
        xs.append(x)
        ys.append(y)
        y_prev = max(y, y_prev - TOL_SOBE)
    return np.array(xs, float), np.array(ys, float)


def main() -> int:
    doc = fitz.open(str(PDF))
    page = doc[PAGINA]
    rs = [d["rect"] for d in page.get_drawings()
          if d["rect"].width > 20 and d["rect"].height > 20 and d["rect"].y1 < 340]
    clip = (min(r.x0 for r in rs) - 6, min(r.y0 for r in rs) - 6,
            max(r.x1 for r in rs) + 6, max(r.y1 for r in rs) + 6)
    pix = page.get_pixmap(dpi=600, clip=fitz.Rect(*clip))
    A = np.asarray(Image.frombytes("RGB", (pix.width, pix.height), pix.samples),
                   dtype=np.int16)
    H, W, _ = A.shape
    R, G, B = A[..., 0], A[..., 1], A[..., 2]
    dark = (R < 110) & (G < 110) & (B < 110)

    cols = [x for x in range(W) if dark[:, x].sum() > 0.5 * H]
    rows = [y for y in range(H) if dark[y, :].sum() > 0.5 * W]
    assert cols and rows, "moldura nao encontrada"
    fx_l, fx_r, fy_t, fy_b = min(cols), max(cols), min(rows), max(rows)
    print(f"moldura x[{fx_l},{fx_r}] y[{fy_t},{fy_b}] shape=({H},{W})")

    # ticks do eixo x (0,60,...,360) — apontam p/ fora
    hits = [x for x in range(fx_l + 4, fx_r - 4)
            if dark[fy_b + 2:min(fy_b + 13, H), x].sum() >= 7]
    cl, cur = [], [hits[0]]
    for v in hits[1:]:
        (cur.append(v) if v - cur[-1] <= 5
         else (cl.append(sum(cur) / len(cur)), cur.clear(), cur.append(v)))
    cl.append(sum(cur) / len(cur))
    if abs(cl[0] - 60.0 - fx_l) < 12:
        cl = [float(fx_l)] + cl
    print(f"ticks-x {[round(v) for v in cl]}")
    assert len(cl) >= 5, f"ticks insuficientes: {cl}"
    dx = float(np.mean(np.diff(cl))) / 60.0      # px por ciclo

    def px2cyc(x):
        return (x - cl[0]) / dx

    def px2N(y):
        return N_TOPO * (fy_b - y) / (fy_b - fy_t)

    dentro = np.zeros((H, W), bool)
    dentro[fy_t + 4:fy_b - 4, fx_l + 4:fx_r - 4] = True
    # legenda (caixa inferior dentro do grafico) — mede-se e mascara-se
    leg = np.zeros((H, W), bool)
    leg[int(fy_t + 0.74 * (fy_b - fy_t)):fy_b, fx_l:fx_r] = True

    # Fb(10mm): azul-acinzentado CLARO. Fb(12mm): vermelho. Fb(14mm): preto.
    # mascara LARGA de proposito: a cauda da t10 (>330 ciclos) e' quase so
    # antialias palido (a linha e' fina e clara), e com R<236 o traco morria
    # em 334 de 390 ciclos — 14 % do ensaio perdido, medido no overlay.
    m_t10 = (R > 120) & (R < 248) & (B - R > 7) & (B - R < 110) & dentro & ~leg
    m_t12 = (R > 150) & (R - G > 60) & (R - B > 60) & dentro & ~leg
    m_t14 = dark & dentro & ~leg

    y0 = fy_b - (fy_b - fy_t) * 4000.0 / N_TOPO
    curvas = {}
    for nome, m in (("t10", m_t10), ("t12", m_t12), ("t14", m_t14)):
        xs, ys = _trace(m, fx_l + 8, fx_r - 6, y0)
        curvas[nome] = (px2cyc(xs), np.array([px2N(v) for v in ys]), xs, ys)
        c, n = curvas[nome][0], curvas[nome][1]
        F0 = float(np.median(n[:8]))
        def ret(N):
            return 100.0 * float(np.interp(N, c, n)) / F0
        print(f"  {nome}: {xs.size:4d} col · F0={F0:.0f} N · "
              f"N=100 -> {ret(100):5.1f}%  N=182 -> {ret(182):5.1f}%  "
              f"fim={n[-1]:.0f} N @ {c[-1]:.0f} ciclos")
        curvas[nome] = (c, n, xs, ys, F0, ret(100), ret(182))

    # ---- GATES ----
    alvo = {"t10": (62.0, 43.0), "t12": (80.0, 62.0), "t14": (98.0, 96.0)}
    ok = True
    for nome, (a1, a2) in alvo.items():
        _, _, _, _, _, r1, r2 = curvas[nome]
        tol = 2.0 if nome == "t10" else 2.5
        bom = abs(r1 - a1) <= tol and abs(r2 - a2) <= tol
        print(f"  GATE {nome}: {r1:.1f}/{r2:.1f} vs alvo {a1}/{a2} "
              f"(tol {tol}) -> {'OK' if bom else 'FALHA'}")
        ok &= bom

    dbg = A.copy()
    for nome, cor in (("t10", (0, 200, 0)), ("t12", (255, 0, 255)),
                      ("t14", (0, 200, 255))):
        _, _, xs, ys, *_ = curvas[nome]
        for x, y in zip(xs.astype(int), ys.astype(int)):
            dbg[max(y - 1, 0):y + 2, x] = cor
    Image.fromarray(dbg.astype(np.uint8)).save(SCRATCH / "rous_fig4_overlay.png")
    with open(SCRATCH / "rous_fig4_audit.json", "w", encoding="utf-8") as f:
        json.dump({k: {"F0": v[4], "ret100": v[5], "ret182": v[6]}
                   for k, v in curvas.items()}, f, indent=1)

    if not ok:
        print("GATE FALHOU -> nada escrito (ramo do prereg)")
        return 1
    c, n, _, _, F0, _, _ = curvas["t10"]
    grade = np.arange(0.0, c[-1] + 1e-9, 2.0)
    grade = grade[grade >= c[0]]
    rs_ = np.interp(grade, c, n) / F0
    csv = OUTD / "rousseau2025_hdpe_t10.csv"
    with open(csv, "w", encoding="utf-8", newline="") as f:
        f.write("cycle,F_over_F0\n")
        for a, b in zip(grade, rs_):
            f.write(f"{a:.0f},{b:.4f}\n")
    print(f"ESCRITO {csv.name}: {len(grade)} pts, fim {rs_[-1]:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
