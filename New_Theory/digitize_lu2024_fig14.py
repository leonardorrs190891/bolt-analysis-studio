# -*- coding: utf-8 -*-
"""P4 do plano LU_2024 — digitaliza a Fig. 14a (Sensors 24:3306, p.15).

Tres corridas LONGAS a 22 N.m (preload vs tempo @1 Hz => tempo==ciclos):
  0.25 mm ate ~1070 s (plateau ~10.5 kN; prosa: 10539 N no fim)
  0.5  mm ate ~700 s  (colapso completo; piso de sensor ~70 N)
  1.0  mm ate ~290 s  (aperto em t~100 s; colapso 165-215 s)

Sao repeticoes independentes das condicoes da fig18 (janelas 3-10x maiores)
=> 3 pares de replica REAIS na janela comum 0-100 ciclos + 3 curvas novas.

Extracao: recorte vetorial 600 dpi -> classificacao por cor (preto/verm/azul)
-> mediana por coluna -> calibracao por ticks (medidos na regua e VERIFICADOS
por round-trip contra as ancoras da prosa; o script FALHA se nao baterem).

Saida: Models/.../digitized_csv/lu2024_M8_fig14_amp{0p25,0p5,1p0}_long.csv
       (header cycle,F_over_F0 — F0 = pico pos-aperto por curva) +
       overlay de debug no scratchpad + JSON de auditoria.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

try:
    import fitz
    from PIL import Image
except ImportError as e:
    raise SystemExit(f"dependencia: {e}")

ROOT = pathlib.Path(__file__).resolve().parents[1]
PDF = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library"
       / "pdfs_open_access" / "lu2024_sensors_M8.pdf")
OUTD = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library"
        / "digitized_csv")
SCRATCH = pathlib.Path(r"C:\Users\leo_r\AppData\Local\Temp\claude"
                       r"\C--Users-leo-r-OneDrive-BPL-Analitical-BAS-V2"
                       r"\a77f4ade-d869-46d0-a5cf-dcf42fd5edae\scratchpad")

# AUTO-CALIBRACAO (a 1a versao usava constantes medidas de olho na regua e
# errou a borda direita em ~145px e o y em ~30px — pego pelo round-trip).
# Moldura: colunas/linhas escuras mais EXTERNAS que se interceptam (o
# plateau do 0.25mm e' longo mas nao toca as bordas). Ticks maiores: stubs
# internos mais compridos, agrupados; mapeados a 0..1200 s e 14000..-2000 N.
CLIP = (100 * 72 / 110, 470 * 72 / 110, 480 * 72 / 110, 770 * 72 / 110)
_CAL = {}


def _calibra(dark):
    H, W = dark.shape
    col_run = dark.sum(0)
    row_run = dark.sum(1)
    # candidatos a borda: linhas quase-completas que tocam as duas
    # perpendiculares (frame fecha retangulo)
    cols = [x for x in range(W) if col_run[x] > 0.60 * H]
    rows = [y for y in range(H) if row_run[y] > 0.60 * W * 0.72]
    fx_l, fx_r = min(cols), max(cols)
    rows = [y for y in rows
            if dark[y, fx_l + 3] or dark[y, fx_l + 1]] or rows
    fy_t, fy_b = min(rows), max(rows)

    def stubs(along, lo, hi, eixo):
        """clusters de stubs internos maiores ao longo de uma borda."""
        hits = []
        for p in range(lo, hi):
            if eixo == "x":
                seg = dark[fy_b - 26:fy_b - 4, p]
            else:
                seg = dark[p, fx_l + 4:fx_l + 26]
            if seg.sum() >= 14:          # major tick (~18-22px); minor ~8
                hits.append(p)
        cl, cur = [], [hits[0]]
        for v in hits[1:]:
            if v - cur[-1] <= 4:
                cur.append(v)
            else:
                cl.append(sum(cur) / len(cur))
                cur = [v]
        cl.append(sum(cur) / len(cur))
        return cl

    tx = stubs(None, fx_l + 5, fx_r - 5, "x")
    ty = stubs(None, fy_t + 5, fy_b - 5, "y")
    # o tick extremo pode COINCIDIR com a moldura (aqui t=1200 == borda
    # direita) e sair da varredura — aceitar >=6/8 com passo uniforme
    assert len(tx) >= 6, f"ticks-x insuficientes: {tx}"
    assert len(ty) >= 8, f"ticks-y insuficientes: {ty}"
    import numpy as _np
    dxs = _np.diff(tx); dys = _np.diff(ty)
    assert dxs.std() < 3 and dys.std() < 3, f"ticks nao uniformes: {dxs} {dys}"
    _CAL.update(x0=tx[0], dx=float(_np.mean(dxs)) / 200.0,
                y0=ty[0], dy=float(_np.mean(dys)) / (-2000.0),
                frame=(fx_l, fx_r, fy_t, fy_b))
    print(f"calibracao: frame x[{fx_l},{fx_r}] y[{fy_t},{fy_b}] "
          f"ticks-x {[round(v) for v in tx]} ticks-y {[round(v) for v in ty]}")


def px2t(x):
    return (x - _CAL["x0"]) / _CAL["dx"]


def px2N(y):
    return 14000.0 + (y - _CAL["y0"]) / _CAL["dy"]


def main() -> int:
    doc = fitz.open(str(PDF))
    pix = doc[14].get_pixmap(dpi=600, clip=fitz.Rect(*CLIP))
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    A = np.asarray(im, dtype=np.int16)
    H, W, _ = A.shape
    R, G, B = A[..., 0], A[..., 1], A[..., 2]

    red = (R > 150) & (G < 110) & (B < 110)
    blue = (B > 150) & (R < 110) & (G < 140)
    dark = (R < 120) & (G < 120) & (B < 120)   # <95 afinava o plateau p/ <4px

    _calibra(dark)
    FX_L, FX_R, FY_T, FY_B = (_CAL["frame"][0], _CAL["frame"][1],
                              _CAL["frame"][2], _CAL["frame"][3])
    inside = np.zeros((H, W), bool)
    inside[FY_T + 30:FY_B - 30, FX_L + 30:FX_R - 30] = True   # 30>stub(~26px)
    # legenda (caixa sup. direita) + ticks internos junto as bordas
    inside[105:345, 1240:1700] = False   # 100:400 comia o plateau em y~390

    red = red & inside
    blue = blue & inside
    black = dark & inside & ~red & ~blue

    def trace(mask):
        xs, ts, Ns = [], [], []
        for x in range(W):
            ys = np.where(mask[:, x])[0]
            if ys.size < 2:
                continue
            # maior run contiguo (tolerancia 3px) — descarta pixels orfaos
            runs, cur = [], [ys[0]]
            for v in ys[1:]:
                if v - cur[-1] <= 3:
                    cur.append(v)
                else:
                    runs.append(cur); cur = [v]
            runs.append(cur)
            best = max(runs, key=len)
            if len(best) < 4:   # linha ~6-9px @600dpi; specks ficam fora
                continue
            y = float(np.median(best))
            xs.append(x)
            ts.append(px2t(x))
            Ns.append(px2N(y))
        ts, Ns, xs = np.array(ts), np.array(Ns), np.array(xs)
        if xs.size == 0:
            return ts, Ns, xs
        # as curvas REAIS tem gaps genuinos (dropouts/degraus) — nao usar
        # maior-segmento (comeu meia curva). Junk = pontas de stub, SEMPRE
        # estreitas (<=8 col): descartar so segmentos com <20 colunas.
        cortes = np.where(np.diff(xs) > 25)[0]
        keep = np.concatenate([s for s in np.split(np.arange(xs.size),
                                                   cortes + 1)
                               if s.size >= 20]) if xs.size else xs
        return ts[keep], Ns[keep], xs[keep]

    curvas = {"amp0p25_long": trace(black),
              "amp0p5_long": trace(red),
              "amp1p0_long": trace(blue)}

    # ---- round-trip contra as ancoras da PROSA (gate do P4) ---------------
    t_b, N_b, _ = curvas["amp0p25_long"]
    t_r, N_r, _ = curvas["amp0p5_long"]
    t_a, N_a, _ = curvas["amp1p0_long"]
    print("DIAG preto: fim do traco x-ultimos 12 pts:",
          [f"t={tt:.0f},N={nn:.0f}" for tt, nn in
           zip(t_b[-12:], N_b[-12:])])
    fim_preto = float(np.median(N_b[-30:]))       # ultimas colunas do traco
    pico_azul = float(N_a.max())
    piso_verm = float(np.median(N_r[-20:]))
    plateau_preto = float(np.median(N_b[(t_b > 200) & (t_b < 900)]))
    print(f"round-trip: fim preto={fim_preto:.0f} N (prosa 10539) . "
          f"pico azul={pico_azul:.0f} (prosa ~12.7-13.4k) . "
          f"piso verm={piso_verm:.0f} (<150) . plateau={plateau_preto:.0f}")
    assert abs(fim_preto - 10539) < 450, "fim do 0.25mm nao bate com a prosa"
    assert 12300 < pico_azul < 14000, "pico do 1.0mm fora da banda"
    assert piso_verm < 250, "piso do 0.5mm nao encontrado"

    # ---- corte pos-aperto + normalizacao + reamostragem --------------------
    OUTD.mkdir(parents=True, exist_ok=True)
    audit = {}
    for nome, (t, N, _x) in curvas.items():
        i_pk = int(np.argmax(N))
        t_pk = t[i_pk]
        F0 = float(np.max(N[(t >= t_pk) & (t <= t_pk + 30)]))
        # cycle 0 = pico pos-aperto; manter dali em diante
        m = t >= t_pk
        cyc = t[m] - t_pk
        ratio = np.clip(N[m] / F0, 0.0, None)
        # reamostra: denso no inicio (passo 1), depois passo 5
        grade = np.concatenate([np.arange(0, min(100, cyc[-1]), 1.0),
                                np.arange(100, cyc[-1], 5.0)])
        grade = grade[grade <= cyc[-1]]
        rs = np.interp(grade, cyc, ratio)
        csv = OUTD / f"lu2024_M8_fig14_{nome}.csv"
        with open(csv, "w", encoding="utf-8", newline="") as f:
            f.write("cycle,F_over_F0\n")
            for c, r in zip(grade, rs):
                f.write(f"{c:.1f},{r:.5f}\n")
        audit[nome] = {"F0_N": F0, "t_aperto_s": float(t_pk),
                       "n_pts": int(len(grade)), "fim_ratio": float(rs[-1]),
                       "span_ciclos": float(grade[-1])}
        print(f"  {csv.name}: F0={F0:.0f} N aperto@{t_pk:.0f}s "
              f"{len(grade)} pts ate {grade[-1]:.0f} ciclos "
              f"fim={rs[-1]:.3f}")

    # F0s vs prosa {12398, 12285, 12696} — conferencia informacional
    f0s = sorted(a["F0_N"] for a in audit.values())
    print(f"F0s digitalizados: {[f'{v:.0f}' for v in f0s]} vs prosa "
          f"[12285, 12398, 12696] (ordem por amplitude nao declarada)")

    # overlay de debug
    dbg = A.copy()
    for nome, cor in (("amp0p25_long", (0, 200, 0)),
                      ("amp0p5_long", (255, 0, 255)),
                      ("amp1p0_long", (0, 255, 255))):
        t, N, xs = curvas[nome]
        for x, n in zip(xs, N):
            y = int(round(_CAL["y0"] + (n - 14000.0) * _CAL["dy"]))
            if 1 <= y < H - 1:
                dbg[y - 1:y + 2, int(x), :] = cor
    Image.fromarray(dbg.astype(np.uint8)).save(
        str(SCRATCH / "fig14a_overlay.png"))
    (SCRATCH / "fig14_audit.json").write_text(json.dumps(audit, indent=1),
                                              encoding="utf-8")
    print("overlay:", SCRATCH / "fig14a_overlay.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
