# -*- coding: utf-8 -*-
"""BAUER fig6: **2 numeros compartilhados** batem os 4 per-curva de hoje?

## O que se descobriu antes deste script

As 6 replicas da MESMA condicao nominal (M8, 0,07 mm) carregam **quatro** valores
distintos de `tr_loose_gain` — 2,2 / 1,8 / 1,8 / 1,8 / 1,6 / 1,4 — e a atribuicao
esta **anticorrelacionada com o dado**:

    replica  gain   final dado   final modelo   erro
    rep1     2,2      0,1870       0,0611      -0,126
    rep6     1,4      0,1801       0,1847      +0,005

`rep1` e `rep6` querem o MESMO final (0,187 vs 0,180) e receberam ganhos que
diferem 57 %. Isso e' defeito de **atribuicao**, nao de forma.

E explica por que o premeasure de `arrest_approach_exp` "ajudou 3 e piorou 2":
o expoente empurra numa direcao so' (retem mais) e estava compensando ganho mal
atribuido — ajuda quem tem final baixo demais, atrapalha quem ja esta certo.

## O teste

Grade `(tr_loose_gain, arrest_approach_exp)` **COMPARTILHADA** pelas 6 replicas,
contra o baseline de hoje (4 ganhos per-curva, expoente 1,0). Criterio de
parcimonia da campanha: **menos numeros nao pode custar placar**.

  * baseline: **4 numeros** (ganhos per-curva) => 2 no tripe (rep2, rep3)
  * candidato: **2 numeros** (1 ganho + 1 expoente, os dois compartilhados)

Se o candidato empatar em tripe com metade dos numeros, ja e' ganho de
parcimonia; se superar, e' candidato a adocao pelo padrao D-Z.

⚠️ So'-leitura. Nao adota, nao escreve store nem config. A adocao exige prereg
com gates congelados ANTES de escolher a celula.

    py -3.12 New_Theory/bauer_fig6_parcimonia.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.runner as rn                  # noqa: E402
from bolt_analysis_studio.validation import report_html as rh        # noqa: E402
from bolt_analysis_studio.validation.case_registry import (          # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.runner import CaseResult        # noqa: E402

STORE = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"
REPS = [f"bauer2024_M8_fig6_rep{i}" for i in range(1, 7)]
GANHOS = [1.2, 1.4, 1.6, 1.8, 2.0, 2.2]
EXPS = [1.0, 1.5, 2.0, 2.5, 3.0]

_EXTRA: dict = {}
_orig = rn._effective_overrides
rn._effective_overrides = (
    lambda rec, base: {**_orig(rec, base), **_EXTRA} if _EXTRA
    else _orig(rec, base))


def _avalia(cids, extra, L):
    """(n no tripe, soma de MAE, lista por curva) sob `extra` compartilhado."""
    _EXTRA.clear()
    _EXTRA.update(extra)
    li = []
    for c in cids:
        r = rn.simulate_case(record(c))
        sd = rh.sres_para_censo(r)
        ok = (r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX
              and sd is not None and sd <= L)
        li.append((c, r.mae, r.maxerr, r.resid_std, bool(ok)))
    _EXTRA.clear()
    return sum(1 for x in li if x[4]), sum(x[1] for x in li), li


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    S = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
    pisos = rh._pisos_medidos([(recs[c].source, r) for c, r in res.items()])
    L = rh.limite_sres("BAUER_2024", pisos)

    print("BAUER fig6 — parcimonia: 2 numeros COMPARTILHADOS vs 4 per-curva")
    print(f"limite_sres(BAUER_2024) = {L:.4f}\n")

    n0, s0, li0 = _avalia(REPS, {}, L)
    print(f"BASELINE (4 ganhos per-curva, exp 1,0): tripe {n0}/6, soma MAE {s0:.4f}")
    for c, mae, mx, sd, ok in li0:
        print(f"    {c[-5:]:>5}  {mae:.4f} {mx:.4f} {sd:.4f}  {'SIM' if ok else ' - '}")

    print(f"\ngrade {len(GANHOS)}x{len(EXPS)} compartilhada "
          f"({len(GANHOS)*len(EXPS)*len(REPS)} simulacoes)\n")
    print("  gain " + "".join(f"   exp{e:<4.1f}" for e in EXPS))
    out, melhor = [], None
    for g in GANHOS:
        cel = []
        for e in EXPS:
            ex = {"tr_loose_gain": g}
            if e != 1.0:
                ex["arrest_approach_exp"] = e
            n, s, li = _avalia(REPS, ex, L)
            cel.append(f"  {n}/6 {s:5.3f}")
            out.append(dict(gain=g, exp=e, tripe=n, soma_mae=s,
                            curvas=[dict(cid=c, mae=m, maxerr=x, sd=d, ok=o)
                                    for c, m, x, d, o in li]))
            if melhor is None or (n, -s) > (melhor["tripe"], -melhor["soma_mae"]):
                melhor = out[-1]
        print(f"  {g:<4.1f}" + "".join(cel))

    print(f"\n--- melhor celula compartilhada: gain {melhor['gain']}, "
          f"exp {melhor['exp']} -> tripe {melhor['tripe']}/6, "
          f"soma MAE {melhor['soma_mae']:.4f} ---")
    for d in melhor["curvas"]:
        b = next(x for x in li0 if x[0] == d["cid"])
        seta = "melhora" if d["mae"] < b[1] - 1e-9 else (
            "PIORA" if d["mae"] > b[1] + 1e-9 else "igual")
        print(f"    {d['cid'][-5:]:>5}  {b[1]:.4f} -> {d['mae']:.4f}  "
              f"{'SIM' if d['ok'] else ' - '}  ({seta})")
    print(f"\n  numeros: baseline 4 (per-curva)  ·  candidato 2 (compartilhados)")
    print(f"  tripe:   baseline {n0}/6            ·  candidato {melhor['tripe']}/6")

    if a.json:
        a.json.write_text(json.dumps(dict(limite=L, baseline=dict(
            tripe=n0, soma_mae=s0,
            curvas=[dict(cid=c, mae=m, maxerr=x, sd=d, ok=o)
                    for c, m, x, d, o in li0]), grade=out), indent=1,
            default=float), encoding="utf-8")
        print(f"\njson -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
