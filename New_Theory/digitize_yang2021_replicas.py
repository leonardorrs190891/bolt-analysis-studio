# -*- coding: utf-8 -*-
"""Bloco 6 do plano_tripe_restante — digitaliza as replicas 0.6mm-8kN do
YANG_2021 (Fig. 6b2/6b3, Shock & Vibration 2021:1441122, p.8).

Prereg: docs/superpowers/specs/2026-07-31-yang2021-replicas-0p6-prereg.md
Gates G1 (round-trip): media das 3 vidas (r1=12500 do CSV existente + r2/r3
novas) em 14666 +/- 8% (Tabela 3 do paper); >=30 pts/curva; ratio inicial
em [0.95, 1.15]; overlay de debug salvo.

Metodo (arquitetura do digitize_lu2024_fig14): recorte vetorial 600dpi por
painel -> auto-calibracao (moldura + ticks maiores) -> mascara VERMELHA
(curva; tracejadas/tangente sao pretas -> fora da mascara) -> mediana do
maior run por coluna -> reamostragem. Normalizacao por F0 NOMINAL 14.1 kN
(convencao da fonte: 1os pontos podem exceder 1.0).

Saida: Models/.../digitized_csv/yang2021_amp0p6mm_ax8kN_{r2,r3}.csv
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
       / "pdfs_open_access" / "yang2021_sv_combined.pdf")
OUTD = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library"
        / "digitized_csv")
SCRATCH = pathlib.Path(r"C:\Users\leo_r\AppData\Local\Temp\claude"
                       r"\C--Users-leo-r-OneDrive-BPL-Analitical-BAS-V2"
                       r"\a77f4ade-d869-46d0-a5cf-dcf42fd5edae\scratchpad")

F0_NOMINAL_KN = 14.1          # convencao da fonte (apparatus note)
VIDA_R1 = 12500.0             # do CSV r1 ja em biblioteca
ANCORA_TAB3 = 14666.0         # Tabela 3: N(0.6-8)
# painel -> clip em pts PDF na pagina 8 (indice 7)
PANEIS = {
    "r2": (235, 368, 378, 500),
    "r3": (382, 368, 532, 500),
}
# ticks maiores: x = 0,4000,...,16000 (passo 4000); y = 0,5,10,15 (passo 5)


def calibra(dark):
    """moldura (linhas escuras externas) + clusters de ticks maiores."""
    H, W = dark.shape
    col_run = dark.sum(0)
    row_run = dark.sum(1)
    cols = [x for x in range(W) if col_run[x] > 0.55 * H]
    rows = [y for y in range(H) if row_run[y] > 0.55 * W]
    assert cols and rows, "moldura nao encontrada"
    fx_l, fx_r = min(cols), max(cols)
    fy_t, fy_b = min(rows), max(rows)

    def stubs(lo, hi, eixo, thr):
        # ticks deste periodico apontam p/ FORA da moldura e tem so ~10px
        # (no lu2024 eram stubs internos de 18-22px — a varredura interna
        # aqui achava so as TRACEJADAS N_F/N_2, e a externa de 21px diluia
        # a soma abaixo do limiar)
        hits = []
        for p in range(lo, hi):
            if eixo == "x":
                seg = dark[fy_b + 2:min(fy_b + 13, dark.shape[0]), p]
            else:
                seg = dark[p, max(fx_l - 13, 0):fx_l - 2]
            if seg.sum() >= thr:
                hits.append(p)
        if not hits:
            return []
        cl, cur = [], [hits[0]]
        for v in hits[1:]:
            if v - cur[-1] <= 4:
                cur.append(v)
            else:
                cl.append(sum(cur) / len(cur))
                cur = [v]
        cl.append(sum(cur) / len(cur))
        return cl

    tx = stubs(fx_l + 4, fx_r - 4, "x", 7)
    ty = stubs(fy_t + 4, fy_b - 4, "y", 7)
    # o tick de valor 0 COINCIDE com a moldura nos 2 eixos (x=0 e' a linha
    # esquerda; y=0 kN e' a linha de baixo) e fica fora da varredura —
    # estender por passo uniforme quando a extensao cai na moldura
    if len(tx) >= 2:
        step = (tx[-1] - tx[0]) / (len(tx) - 1)
        if abs(tx[0] - step - fx_l) < 6:
            tx = [float(fx_l)] + tx
    if len(ty) >= 2:
        step = (ty[-1] - ty[0]) / (len(ty) - 1)
        if abs(ty[-1] + step - fy_b) < 6:
            ty = ty + [float(fy_b)]
    print(f"  frame x[{fx_l},{fx_r}] y[{fy_t},{fy_b}] "
          f"ticks-x {[round(v) for v in tx]} ticks-y {[round(v) for v in ty]}")
    return fx_l, fx_r, fy_t, fy_b, tx, ty


def main() -> int:
    doc = fitz.open(str(PDF))
    page = doc[7]
    OUTD.mkdir(parents=True, exist_ok=True)
    audit = {}
    vidas = {"r1": VIDA_R1}

    for rep, clip in PANEIS.items():
        print(f"painel {rep}:")
        pix = page.get_pixmap(dpi=600, clip=fitz.Rect(*clip))
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        A = np.asarray(im, dtype=np.int16)
        H, W, _ = A.shape
        R, G, B = A[..., 0], A[..., 1], A[..., 2]
        red = (R > 150) & (R - G > 60) & (R - B > 60)
        dark = (R < 120) & (G < 120) & (B < 120)

        fx_l, fx_r, fy_t, fy_b, tx, ty = calibra(dark)
        # ticks-x: 0..16000 passo 4000 (o de 16000 e' interno); ticks-y:
        # 0,5,10,15 de baixo p/ cima => ty[0]=15 kN (pixel menor = topo)
        assert len(tx) >= 4, f"ticks-x insuficientes: {tx}"
        assert len(ty) >= 3, f"ticks-y insuficientes: {ty}"
        dxs, dys = np.diff(tx), np.diff(ty)
        assert dxs.std() < 4 and dys.std() < 4, f"nao uniformes: {dxs} {dys}"
        dx = float(np.mean(dxs)) / 4000.0            # px por ciclo
        dy = float(np.mean(dys)) / 5.0               # px por kN (desce)
        x0px, ytoppx = tx[0], ty[0]
        n_y = len(ty)
        # valor do tick de topo: com 4 clusters = 15; com 3 (topo perdido) = 10
        y_top_val = 5.0 * (n_y - 1)

        inside = np.zeros((H, W), bool)
        # margem-x de 1px (nao 3): o pico de overshoot inicial fica COLADO
        # no eixo-y e a margem de 3px o comia (r3 comecava em 0.939 ja na
        # descida do pico). A moldura e' preta — a mascara vermelha nao a ve.
        inside[fy_t + 3:fy_b - 3, fx_l + 1:fx_r - 1] = True
        m = red & inside

        xs, cyc, kn = [], [], []
        ultimo_fundo = -1.0
        for x in range(W):
            ys = np.where(m[:, x])[0]
            if ys.size < 2:
                continue
            runs, cur = [], [ys[0]]
            for v in ys[1:]:
                if v - cur[-1] <= 3:
                    cur.append(v)
                else:
                    runs.append(cur)
                    cur = [v]
            runs.append(cur)
            best = max(runs, key=len)
            if len(best) < 4:
                continue
            y = float(np.median(best))
            xs.append(x)
            cyc.append((x - x0px) / dx)
            kn.append(y_top_val - (y - ytoppx) / dy)
            ultimo_fundo = float(best[-1])
        xs, cyc, kn = np.array(xs), np.array(cyc), np.array(kn)
        assert xs.size > 200, f"traco curto demais: {xs.size} colunas"
        # descarta segmentos estreitos (<20 col) = sujeira; gaps reais ficam
        cortes = np.where(np.diff(xs) > 25)[0]
        keep = np.concatenate([s for s in np.split(np.arange(xs.size),
                                                   cortes + 1)
                               if s.size >= 20])
        xs, cyc, kn = xs[keep], cyc[keep], kn[keep]
        cyc = np.clip(cyc, 0.0, None)

        vida = float(cyc[-1])
        ratio = kn / F0_NOMINAL_KN
        # queda final quase-vertical: a mediana do run da ULTIMA coluna cai
        # no MEIO da queda (r2 terminava em 0.317); se o fundo desse run
        # alcanca y(0 kN), a curva atinge 0 — fechar em (vida, 0) como a r1
        y0px = ytoppx + y_top_val * dy
        if ultimo_fundo >= y0px - 15:
            cyc = np.append(cyc, vida)
            ratio = np.append(ratio, 0.0)
            kn = np.append(kn, 0.0)
        # N_F informacional: 1o cruzamento de 11.3 kN (80% F0)
        below = np.where(kn < 11.3)[0]
        n_f = float(cyc[below[0]]) if below.size else float("nan")
        print(f"  traco: {xs.size} col, vida={vida:.0f}, "
              f"ratio_ini={ratio[0]:.4f}, N_F(11.3kN)={n_f:.0f}")
        vidas[rep] = vida

        # reamostra: denso no assentamento e no colapso, esparso no plateau
        grade = np.unique(np.concatenate([
            np.arange(cyc[0], min(cyc[0] + 500, vida), 50.0),
            np.arange(500, max(vida - 2000, 501), 250.0),
            np.arange(max(vida - 2000, 0), vida, 50.0),
            [vida],
        ]))
        grade = grade[(grade >= cyc[0]) & (grade <= vida)]
        rs = np.interp(grade, cyc, ratio)
        rs = np.clip(rs, 0.0, None)
        assert rs.shape[0] >= 30, f"menos de 30 pts: {rs.shape[0]}"
        assert 0.95 <= rs[0] <= 1.15, f"ratio inicial fora: {rs[0]:.4f}"

        csv = OUTD / f"yang2021_amp0p6mm_ax8kN_{rep}.csv"
        with open(csv, "w", encoding="utf-8", newline="") as f:
            f.write("cycle,F_over_F0\n")
            for c, r in zip(grade, rs):
                f.write(f"{c:.0f},{r:.4f}\n")
        audit[rep] = {"vida": vida, "n_pts": int(len(grade)),
                      "ratio_ini": float(rs[0]), "fim": float(rs[-1]),
                      "N_F_11p3kN": n_f}
        print(f"  -> {csv.name}: {len(grade)} pts, fim={rs[-1]:.3f}")

        # overlay de debug
        dbg = A.copy()
        for x, k in zip(xs, kn):
            y = int(round(ytoppx + (y_top_val - k) * dy))
            if 1 <= y < H - 1:
                dbg[y - 1:y + 2, x] = (0, 200, 0)
        Image.fromarray(dbg.astype(np.uint8)).save(
            SCRATCH / f"yang2021_{rep}_overlay.png")

    # ---- G1 round-trip: media das 3 vidas vs Tabela 3 ----------------------
    media = float(np.mean([vidas["r1"], vidas["r2"], vidas["r3"]]))
    desvio = abs(media - ANCORA_TAB3) / ANCORA_TAB3
    print(f"G1 round-trip: vidas r1={vidas['r1']:.0f} r2={vidas['r2']:.0f} "
          f"r3={vidas['r3']:.0f} -> media={media:.0f} vs Tabela 3 "
          f"{ANCORA_TAB3:.0f} (desvio {100 * desvio:.1f}%)")
    assert desvio <= 0.08, f"G1 FALHOU: desvio {100 * desvio:.1f}% > 8%"

    audit["G1"] = {"media_vidas": media, "ancora_tab3": ANCORA_TAB3,
                   "desvio_frac": desvio, "vidas": vidas}
    with open(SCRATCH / "yang2021_replicas_audit.json", "w",
              encoding="utf-8") as f:
        json.dump(audit, f, indent=1)
    print("G1 PASSOU; audit salvo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
