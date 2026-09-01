# -*- coding: utf-8 -*-
"""Auditoria das CSVs do YANG_2019 contra a curva D-N impressa (Tabela 5).

## A ancora

O paper publica, na Tabela 5, expressoes da "loosening D-N curve" na forma

        d^m * N = C

para tres niveis de pre-carga residual (90 %, 80 %, 70 %), em DOIS ramos —
baixo ciclo e alto ciclo — com ponto de inflexao em **N ~ 2500** (Fig. 8):

    baixo ciclo:  90 % m=20.732 C=12      80 % m=15.526 C=63
                  70 % m=11.010 C=193
    alto  ciclo:  90 % m= 2.386 C=963.829 80 % m= 2.028 C=1674.943
                  70 % m= 2.028 C=1825.324

Isso da' uma previsao INDEPENDENTE de em que ciclo cada curva atinge 0,90,
0,80 e 0,70 — previsao feita pelos PROPRIOS autores a partir dos PROPRIOS
ensaios. Se a CSV digitalizada discordar, ou a digitalizacao esta errada, ou
a curva digitalizada nao e' a que alimentou a tabela.

⚠️ Esta e' a unica fonte, alem do LU_2024, em que auditoria contra o impresso
e' possivel: varri os 11 PDFs de `pdfs_open_access/` e so' o LU tem TABELA de
retencao; o Yang 2019 tem esta LEI, que serve ao mesmo fim.

Escolha de ramo: usa-se o ramo cuja previsao cai do lado certo de N=2500 (e' o
que a Fig. 8 define). Se os dois ou nenhum couberem, marca AMBIGUO em vez de
escolher — ramo mal escolhido inventaria discordancia.

So'-leitura. Nao adota, nao escreve CSV, nao toca o store.

    py -3.12 New_Theory/yang2019_dn_auditoria.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation.case_registry import all_records   # noqa: E402
from bolt_analysis_studio.validation.inputs import load_full_curve      # noqa: E402

INFLEX = 2500.0
LEI = {           # nivel -> (baixo (m,C), alto (m,C))
    0.90: ((20.732, 12.000), (2.386, 963.829)),
    0.80: ((15.526, 63.000), (2.028, 1674.943)),
    0.70: ((11.010, 193.000), (2.028, 1825.324)),
}


def prever(d_mm: float, nivel: float):
    """N previsto e ramo usado; None se nenhum ramo for autoconsistente."""
    (mb, cb), (ma, ca) = LEI[nivel]
    nb = cb / d_mm ** mb
    na = ca / d_mm ** ma
    ok_b, ok_a = nb <= INFLEX, na >= INFLEX
    if ok_b and not ok_a:
        return nb, "baixo"
    if ok_a and not ok_b:
        return na, "alto"
    if ok_b and ok_a:
        return None, f"AMBIGUO (baixo {nb:.0f}, alto {na:.0f})"
    return None, f"NENHUM (baixo {nb:.0f}, alto {na:.0f})"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    print("previsao da Tabela 5 (d^m N = C), ramo escolhido por N vs 2500:\n")
    print(f"{'d (mm)':>8}{'90 %':>12}{'80 %':>12}{'70 %':>12}   ramo")
    for d in (0.4, 0.5, 0.6, 0.8):
        cel, ramos = [], []
        for lv in (0.90, 0.80, 0.70):
            n, r = prever(d, lv)
            cel.append(f"{n:.0f}" if n else "--")
            ramos.append(r)
        print(f"{d:>8.2f}{cel[0]:>12}{cel[1]:>12}{cel[2]:>12}   "
              f"{'/'.join(sorted(set(ramos)))}")

    recs = [r for r in all_records() if r.source == "YANG_2019"]
    print(f"\n{len(recs)} curvas no YANG_2019\n")
    print(f"{'curva':<36}{'d':>5}{'nivel':>7}{'N csv':>9}{'N tab':>9}"
          f"{'razao':>8}  ramo")
    out = {}
    for r in sorted(recs, key=lambda z: z.case_id):
        case = r.validation_case
        d = float(getattr(case, "transverse_displacement_mm", 0) or 0)
        try:
            cyc, rat = load_full_curve(r.csv_path)
        except Exception as e:                             # noqa: BLE001
            print(f"{r.case_id[:36]:<36}  erro: {e}")
            continue
        x = np.asarray(cyc, float)
        y = np.asarray(rat, float)
        off = float(getattr(case, "csv_x_offset", 0.0) or 0.0)
        sc = float(getattr(case, "csv_x_scale", 1.0) or 1.0)
        x = np.maximum((x - off) * sc, 0.0)
        linhas = []
        for lv in (0.90, 0.80, 0.70):
            npred, ramo = prever(d, lv) if d > 0 else (None, "sem d")
            # N em que o DADO cruza o nivel (y decrescente)
            if y.min() > lv or y.max() < lv:
                ncsv = None
            else:
                o = np.argsort(-y)
                ncsv = float(np.interp(-lv, -y[o], x[o]))
            raz = (ncsv / npred) if (ncsv and npred) else None
            print(f"{r.case_id[:36]:<36}{d:>5.2f}{lv:>7.0%}"
                  f"{(f'{ncsv:.0f}' if ncsv else '--'):>9}"
                  f"{(f'{npred:.0f}' if npred else '--'):>9}"
                  f"{(f'{raz:.2f}' if raz else '--'):>8}  {ramo}")
            linhas.append(dict(nivel=lv, n_csv=ncsv, n_tabela=npred,
                               razao=raz, ramo=ramo))
        out[r.case_id] = dict(d_mm=d, niveis=linhas)
        print()

    print("LEITURA: razao ~1 => a CSV concorda com a lei que os proprios")
    print("autores ajustaram aos proprios ensaios. Razao longe de 1 em TODOS")
    print("os niveis de uma curva => digitalizacao ou atribuicao suspeita.")
    print("Razao consistente entre curvas mas != 1 => a lei descreve OUTRA")
    print("populacao (p.ex. media de varias corridas), nao erro de CSV.")
    if a.json:
        a.json.write_text(json.dumps(out, indent=1, default=float),
                          encoding="utf-8")
        print(f"\njson -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
