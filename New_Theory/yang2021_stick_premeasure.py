# -*- coding: utf-8 -*-
"""YANG_2021 em STICK PERMANENTE: a "banda insensivel" do `c_bend` era inercia.

## O que a medicao de hoje achou

A classe **sub-perda** (nova, `mapa_das_65_fora.py` 2026-08-07) tem 7 curvas, e
**6 delas estao com slip resolvido EXATAMENTE 0,0000 um** — com `delta_amp`
imposto de 0,25 a 1,0 mm. Os dois canais dirigidos por slip (wear e afrouxamento
rotacional) ficam em **0 %**, sobrando so' embedding e creep, que **saturam por
construcao** => o modelo termina em 0,96-0,99 onde o dado termina em 0,52-0,88.

A causa esta no `c_bend`, e a **propria procedencia registra o sintoma sem
reconhece-lo**:

    "fitado-this-rig (1o DOF da fonte, PR-3/reclassificacao; banda INSENSIVEL
     0.02-0.15 — valor no centro, nao identificado alem da banda)"

Em `k_tr_mode="bending"`, `k_tr = c_bend*E*I/L_eff^3` e
`delta_t = delta_free + F_slip/k_tr`. Com `c_bend` pequeno, `delta_t` excede o
curso imposto => `slip = max(0, delta - delta_t) = 0` => **a junta trava**. E uma
junta travada da' o MESMO resultado para qualquer `c_bend` da banda — a
"insensibilidade" e' a assinatura de **parametro morto**, nao de robustez
(regra do CLAUDE.md: "grade que da resultado IDENTICO = INERCIA").

## O teste

Varrer `c_bend` **muito alem** da banda fitada, sobre **todas** as curvas da
fonte — as que passam o tripe hoje servem de CONTROLE (G2: nenhuma pode piorar
mais que +0,01 de MAE).

O que se mede por celula: slip resolvido (destravou?), as 3 pernas por curva, e
quantas fecham.

⚠️ So'-leitura. Nao adota, nao escreve store nem config.

    py -3.12 New_Theory/yang2021_stick_premeasure.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.numerical.dynamic_stiffness_analyzer as dsa  # noqa: E402
import bolt_analysis_studio.validation.runner as rn                     # noqa: E402
from bolt_analysis_studio.validation import report_html as rh           # noqa: E402
from bolt_analysis_studio.validation.case_registry import (             # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.runner import CaseResult           # noqa: E402

STORE = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"
C_BENDS = [0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0]

_EXTRA: dict = {}
_orig = rn._effective_overrides
rn._effective_overrides = (
    lambda rec, base: {**_orig(rec, base), **_EXTRA} if _EXTRA
    else _orig(rec, base))

# instrumenta o resolvedor para saber se destravou
_SLIP: list = []
_rts = dsa.resolve_transverse_slip


def _wrap(*a, **k):
    v = _rts(*a, **k)
    try:
        _SLIP.append(float(np.asarray(v).ravel()[0]))
    except Exception:
        pass
    return v


dsa.resolve_transverse_slip = _wrap


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    S = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
    pisos = rh._pisos_medidos([(recs[c].source, r) for c, r in res.items()])
    L = rh.limite_sres("YANG_2021", pisos)
    cids = sorted(c for c in res if recs[c].source == "YANG_2021"
                  and rh.caso_comparavel("YANG_2021", c))

    def tri(r):
        sd = rh.sres_para_censo(r)
        return (r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX
                and sd is not None and sd <= L)

    print(f"YANG_2021 — varredura de `c_bend` (banda fitada 0,02-0,15)")
    print(f"limite_sres = {L:.4f} · {len(cids)} curvas comparaveis\n")

    base = {}
    for c in cids:
        r = res[c]
        base[c] = (r.mae, r.maxerr, r.resid_std, tri(r))
    n0 = sum(1 for v in base.values() if v[3])
    print(f"BASELINE (c_bend 0,1): tripe {n0}/{len(cids)}, "
          f"soma MAE {sum(v[0] for v in base.values()):.4f}\n")

    out, linhas = [], {}
    for cb in C_BENDS:
        _EXTRA.clear()
        _EXTRA["c_bend"] = cb
        n, s, cel = 0, 0.0, []
        for c in cids:
            _SLIP.clear()
            r = rn.simulate_case(record(c))
            slip = (float(np.median(_SLIP)) * 1e6) if _SLIP else float("nan")
            ok = tri(r)
            n += ok
            s += r.mae
            cel.append(dict(cid=c, mae=r.mae, maxerr=r.maxerr, sd=r.resid_std,
                            ok=bool(ok), slip_um=slip))
        _EXTRA.clear()
        linhas[cb] = cel
        out.append(dict(c_bend=cb, tripe=n, soma_mae=s, curvas=cel))
        slips = [d["slip_um"] for d in cel]
        print(f"  c_bend {cb:>6.1f}   tripe {n}/{len(cids)}   "
              f"somaMAE {s:6.4f}   slip med {np.nanmedian(slips):8.2f} um   "
              f"{'DESTRAVOU' if np.nanmedian(slips) > 1e-3 else 'stick'}")

    melhor = max(out, key=lambda o: (o["tripe"], -o["soma_mae"]))
    print(f"\n--- melhor: c_bend {melhor['c_bend']} -> tripe {melhor['tripe']}"
          f"/{len(cids)} (era {n0}), somaMAE {melhor['soma_mae']:.4f} ---")
    print(f"  {'curva':<34}{'MAE base':>10}{'MAE novo':>10}  {'slip um':>9}  d")
    piora = []
    for d in melhor["curvas"]:
        b = base[d["cid"]]
        delta = d["mae"] - b[0]
        if delta > 0.01:
            piora.append((d["cid"], delta))
        mark = ("SIM" if d["ok"] else " - ") + ("" if not b[3] else "*")
        print(f"  {d['cid'][:34]:<34}{b[0]:10.4f}{d['mae']:10.4f}  "
              f"{d['slip_um']:9.2f}  {mark}")
    print(f"\n  (* = ja passava no baseline)")
    print(f"  G2 — curvas que pioram > +0,01 de MAE: {len(piora)}")
    for c, dd in piora:
        print(f"     {c[:44]:<44} +{dd:.4f}")

    if a.json:
        a.json.write_text(json.dumps(dict(limite=L, baseline_tripe=n0,
                                          grade=out), indent=1, default=float),
                          encoding="utf-8")
        print(f"\njson -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
