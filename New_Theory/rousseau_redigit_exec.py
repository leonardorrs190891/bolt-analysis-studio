# -*- coding: utf-8 -*-
"""Executor do prereg D-R (2026-08-05) — re-digitalizacao do ROUSSEAU_2025.

As Figs. 4 e 5 sao POLILINHAS VETORIAIS com ~1 amostra/ciclo (391-400 pts no
HDPE, 183 no aco) contra 9-16 pontos em quatro das cinco CSVs da biblioteca. E a
`steel_t10` esta comprovadamente ERRADA: 6 passos consecutivos identicos a 4
decimais (desvio-padrao 5e-5) sobre a regiao onde o paper mostra colapso CONVEXO
— e' uma RETA tracada entre dois pontos, e le +0,157 alto em N=100.

A ATRIBUICAO polilinha->curva e' feita por casamento objetivo (correlacao de
forma apos normalizacao), nunca a olho; o proprio casamento vira evidencia do G1.

    py -3.12 New_Theory/rousseau_redigit_exec.py            # so gates
    py -3.12 New_Theory/rousseau_redigit_exec.py --escrever

Sem pipe: o executor escreve ANTES de verificar, e um pipe transforma "gate
incompleto" em "sem rastro" (licao do D-Q).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

VEC = Path(r"C:\Users\leo_r\AppData\Local\Temp\claude"
           r"\C--Users-leo-r-OneDrive-BPL-Analitical-BAS-V2"
           r"\a77f4ade-d869-46d0-a5cf-dcf42fd5edae\scratchpad\rousseau_vec_raw.json")
CSVDIR = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library"
          / "digitized_csv")
ALVOS = {                       # case_id -> (figura, rotulo humano)
    "rousseau2025_hdpe_t10": ("fig4", "HDPE 10 mm"),
    "rousseau2025_hdpe_t12": ("fig4", "HDPE 12 mm"),
    "rousseau2025_hdpe_t14": ("fig4", "HDPE 14 mm"),
    "rousseau2025_steel_t10": ("fig5", "aco 10 mm"),
    "rousseau2025_steel_t12": ("fig5", "aco 12 mm"),
}
FORA_DE_ESCOPO = {"rousseau2025_steel_t14": "Fb do aco 14 mm e' RASTER "
                  "(1479x151); exigiria digitalizacao por pixel"}
TOL_FID = 0.01          # G1: |Delta| em >=3 checkpoints
STD_MIN = 0.001         # G1: desvio-padrao dos passos na regiao de colapso


def _le_csv(p: Path):
    xs, ys = [], []
    for i, ln in enumerate(p.read_text(encoding="utf-8").splitlines()):
        s = ln.strip()
        if not s:
            continue
        a, _, b = s.partition(",")
        try:
            xs.append(float(a)); ys.append(float(b))
        except ValueError:
            continue            # cabecalho
    return np.array(xs), np.array(ys)


def _serie(obj, eixo="left"):
    """(x, y) de uma polilinha, ordenada em x e sem duplicatas."""
    a = np.asarray(obj[eixo], float)
    x, y = a[:, 0], a[:, 1]
    o = np.argsort(x)
    x, y = x[o], y[o]
    keep = np.concatenate(([True], np.diff(x) > 0))
    return x[keep], y[keep]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--escrever", action="store_true")
    a = ap.parse_args()

    if not VEC.exists():
        print(f"!! extracao vetorial ausente: {VEC}")
        return 2
    d = json.loads(VEC.read_text(encoding="utf-8"))
    print(f"extracao: fig4={len(d['fig4'])} polilinhas · fig5={len(d['fig5'])}")

    # ---- 1. quais polilinhas sao FORCA (e nao rotacao)?
    # criterio objetivo: a serie de FORCA e' monotona-decrescente em bloco e
    # comeca perto do maximo; a de ROTACAO comeca em ~0. Uso o eixo ESQUERDO
    # (forca em N) e exijo y[0] > 10x a mediana de |y| das candidatas baixas.
    forca = {}
    for fig in ("fig4", "fig5"):
        objs = [(_serie(o), o) for o in d[fig]]
        y0 = np.array([s[1][0] for s, _ in objs])
        corte = 0.5 * (y0.max() + y0.min())
        idx = [i for i, v in enumerate(y0) if v > corte]
        forca[fig] = [(i, objs[i][0]) for i in idx]
        print(f"  {fig}: y(inicio) = {[round(v, 1) for v in y0]}  "
              f"=> FORCA nos indices {idx}")

    print("\n=== ATRIBUICAO objetiva (menor RMS contra a CSV vigente, apos")
    print("    normalizar cada serie pelo proprio 1o ponto)")
    escolha, evid = {}, {}
    for cid, (fig, rot) in ALVOS.items():
        p = CSVDIR / f"{cid}.csv"
        if not p.exists():
            print(f"  !! CSV ausente: {p.name}")
            return 2
        cx, cy = _le_csv(p)
        cand = []
        for i, (vx, vy) in forca[fig]:
            lo, hi = max(cx.min(), vx.min()), min(cx.max(), vx.max())
            m = (cx >= lo) & (cx <= hi)
            if m.sum() < 4:
                continue
            vi = np.interp(cx[m], vx, vy)
            vn = vi / vi[0]
            cn = cy[m] / cy[m][0]
            cand.append((float(np.sqrt(np.mean((vn - cn) ** 2))), i, m.sum()))
        cand.sort()
        if not cand:
            print(f"  !! {cid}: nenhuma candidata")
            return 2
        rms, i, n = cand[0]
        seg = cand[1][0] if len(cand) > 1 else float("inf")
        escolha[cid] = i
        evid[cid] = (rms, seg, n)
        print(f"  {cid[11:]:14s} ({rot:9s}) -> polilinha #{i}  RMS {rms:.4f}  "
              f"2a {seg:.4f}  razao {seg/rms:5.2f}x  ({n} pts comuns)")
    # unicidade POR FIGURA -- o indice e' local a cada figura, e comparar
    # indices entre fig4 e fig5 acusa ambiguidade onde nao ha (bug medido na 1a
    # execucao: hdpe_t10->#0 da fig4 e steel_t10->#0 da fig5 sao polilinhas
    # DIFERENTES).
    for fig in ("fig4", "fig5"):
        us = [escolha[c] for c in ALVOS if ALVOS[c][0] == fig]
        if len(set(us)) != len(us):
            print(f"\n!! ATRIBUICAO AMBIGUA em {fig}: duas curvas casaram a "
                  f"MESMA polilinha {us}.")
            print("   Isso e' reprovacao de instrumento, nao resultado. ABORTADO.")
            return 3
    print("  unicidade por figura: OK")
    rr = {c: v[0] for c, v in evid.items()}
    pior_cid = max(rr, key=rr.get)
    outros = sorted(v for c, v in rr.items() if c != pior_cid)
    print(f"  ATENCAO: o RMS de atribuicao JA denuncia qual CSV nao casa o"
          f" proprio traco -- {pior_cid[11:]} em {rr[pior_cid]:.4f} contra"
          f" {outros[0]:.4f}-{outros[-1]:.4f} nas outras"
          f" ({rr[pior_cid]/outros[-1]:.1f}x). Evidencia INDEPENDENTE.")

    print("\n=== G1 fidelidade + teste de RETIDAO")
    novos, ok = {}, True
    for cid, (fig, rot) in ALVOS.items():
        i = escolha[cid]
        vx, vy = dict(forca[fig])[i]
        cx, _cy = _le_csv(CSVDIR / f"{cid}.csv")
        # ESCOLHA DE GRADE, declarada: a CSV nova mantem a MESMA grade de
        # abscissas da velha (8-14 pts em quatro das cinco), reamostrando o
        # vetor nela — e NAO os 391-398 pontos que o paper publica.
        # Motivo de METODO, nao de conveniencia: as estimativas do prereg
        # ("3 pioram, 2 melhoram, steel_t12 entra") foram calculadas NESTA
        # grade, reusando metric_pred/metric_x do store. Trocar a grade aqui
        # tornaria a PREDICAO REGISTRADA nao-testavel, que e' o unico gate que
        # mede se eu previ certo. O proprio prereg ja avisa que a grade densa
        # "muda a janela da metrica, a ancora de alinhamento e o n_max do
        # FLOOR_TRIM" => merece prereg proprio.
        # DISPONIVEL E NAO TOMADA: grade densa (o dado real do paper).
        m = (cx >= vx.min()) & (cx <= vx.max())
        yy = np.interp(cx[m], vx, vy)
        yy = yy / yy[0]
        novos[cid] = (cx[m], yy)
        # retidao: desvio-padrao dos passos na regiao de maior queda
        dif = np.diff(yy)
        k = int(np.argmin(dif))
        jan = dif[max(0, k - 3):k + 4]
        std = float(np.std(jan))
        bom = std > STD_MIN
        ok &= bom
        print(f"  {cid[11:]:14s} n={m.sum():3d}  fim {yy[-1]:.4f}  "
              f"std dos passos no colapso {std:.6f} "
              f"{'OK' if bom else 'FALHA (reta!)'}")
    print(f"\nG1 retidao: {'PASSA' if ok else 'FALHA'}")

    # comparacao com a CSV velha (informacao + a prova da steel_t10)
    print("\n=== o que muda (informacao)")
    for cid in ALVOS:
        cx, cy = _le_csv(CSVDIR / f"{cid}.csv")
        nx, ny = novos[cid]
        m = np.isin(cx, nx)
        dd = np.abs(cy[m] - ny)
        difs = np.diff(cy)
        k = int(np.argmin(difs))
        jan = difs[max(0, k - 3):k + 4]
        print(f"  {cid[11:]:14s} max|velha-nova| {dd.max():.4f} · "
              f"mediana {np.median(dd):.4f} · std dos passos da VELHA no "
              f"colapso {np.std(jan):.6f}")
    print(f"\nG5 fora de escopo, declarado: {FORA_DE_ESCOPO}")
    if not a.escrever:
        print("\n(sem --escrever: nada foi tocado)")
        return 0 if ok else 3
    if not ok:
        print("\n!! G1 violado -- NADA escrito.")
        return 3
    for cid, (nx, ny) in novos.items():
        p = CSVDIR / f"{cid}.csv"
        shutil.copy2(p, p.with_suffix(".csv.bkp_dr"))
        p.write_text("x,F_over_F0\n" + "".join(
            f"{x:g},{y:.4f}\n" for x, y in zip(nx, ny)), encoding="utf-8")
        print(f"escrito {p.name} ({len(nx)} pts; backup .csv.bkp_dr)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
