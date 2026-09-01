# -*- coding: utf-8 -*-
"""Premeasure de `arrest_approach_exp`: a P-13 pede forma que o engine JA TEM?

## Por que existe

A P-13 foi escrita afirmando que a lei *"taxa decai com a pre-carga restante =>
plato nao-nulo"* nao existe no engine ("ninguem a tem"). Ao ler o
`self_locking_gate` antes de propor forma nova, o docstring dele diz o oposto:

    g = max(0, 1 - F_min/F_0),  F_min = loose_arrest_floor * F_0_init
    "exp > 1 faz a taxa morrer mais cedo perto do piso => DESACELERACAO AO PLATO"

Ou seja: o **ponto fixo estavel em F_min** e' exatamente o plato nao-nulo da
P-13, e `arrest_approach_exp` (prereg grupo A, 2026-07-27) e' a forma da
aproximacao. Testei o PISO (nivel) nas tres fontes e o achei falsificado —
**nunca testei o expoente** (forma).

## A armadilha de companheiro, conferida ANTES de medir

    if mat.loose_arrest_floor <= 0.0 or state.F_0 <= 0.0:
        return 1.0            # <- early-return: o expoente nem e' lido

=> onde o piso e' 0 (IJPEM, ROUSSEAU steel, ECCLES) o expoente e' **inerte por
construcao** e um teste la' seria invalido, como o do `graded_scrit` com o canal
desengatado. Este script mede so' as curvas com **piso > 0**:

  * ROUSSEAU HDPE t10/t12 (piso 0,20) — SEM ESTATUTO, alvo direto da P-13;
  * BAUER fig6 rep1/4/5/6 (piso 0,05) e fig8 test2/3 (piso 0,08) — excecoes.

## O que decide

Se `exp > 1` melhorar as tres pernas em curvas do defeito de bifurcacao, a P-13
deixa de ser "forma faltante" e vira "parametro nao calibrado" — mudanca de
categoria que altera o que se pede ao professor. Se nao melhorar, a P-13 fica
de pe COM o expoente eliminado, que e' informacao que ela hoje nao tem.

⚠️ So'-leitura. Nao adota, nao escreve store nem config.

    py -3.12 New_Theory/arrest_exp_premeasure.py [--json out.json]
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

# curvas de bifurcacao com piso > 0 (onde o expoente e' LIDO)
ALVOS = [
    "rousseau2025_hdpe_t10", "rousseau2025_hdpe_t12",
    "bauer2024_M8_fig6_rep1", "bauer2024_M8_fig6_rep4",
    "bauer2024_M8_fig6_rep5", "bauer2024_M8_fig6_rep6",
    "bauer2024_M12_fig8_test2", "bauer2024_M12_fig8_test3",
]
EXPOENTES = [1.0, 1.5, 2.0, 3.0, 5.0]

_EXTRA: dict = {}
_orig = rn._effective_overrides
rn._effective_overrides = (
    lambda rec, base: {**_orig(rec, base), **_EXTRA} if _EXTRA
    else _orig(rec, base))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    S = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
    pisos = rh._pisos_medidos([(recs[c].source, r) for c, r in res.items()])

    out = []
    print("premeasure `arrest_approach_exp` — 8 curvas de bifurcacao, piso > 0")
    print("(o expoente so' e' LIDO quando loose_arrest_floor > 0)\n")
    for cid in ALVOS:
        rec = record(cid)
        L = rh.limite_sres(rec.source, pisos)
        piso = _orig(rec, {}).get("loose_arrest_floor")
        print(f"=== {cid}  (piso {piso}, limite_sres {L:.4f}) ===")
        print(f"  {'exp':>5}  {'MAE':>8} {'res.max':>8} {'sigma':>8} "
              f"{'final':>7}  tripe")
        base = None
        for e in EXPOENTES:
            _EXTRA.clear()
            if e != 1.0:
                _EXTRA["arrest_approach_exp"] = e
            r = rn.simulate_case(rec)
            _EXTRA.clear()
            sd = rh.sres_para_censo(r)
            ok = (r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX
                  and sd is not None and sd <= L)
            fin = float(np.asarray(r.metric_pred, float)[-1]) \
                if r.metric_pred else float("nan")
            if base is None:
                base = (r.mae, r.maxerr, r.resid_std)
            print(f"  {e:>5.1f}  {r.mae:8.4f} {r.maxerr:8.4f} {r.resid_std:8.4f} "
                  f"{fin:7.4f}  {'SIM' if ok else ' - '}")
            out.append(dict(cid=cid, fonte=rec.source, exp=e, mae=r.mae,
                            maxerr=r.maxerr, sd=r.resid_std, final=fin,
                            tripe=bool(ok), limite=L, piso=piso))
        # dado, para saber o que o plato deveria ser
        d = np.asarray(res[cid].metric_data, float)
        print(f"  {'dado':>5}  {'':>8} {'':>8} {'':>8} {d[-1]:7.4f}\n")

    print("--- resumo: o expoente MOVE alguma perna? ---")
    for cid in ALVOS:
        li = [o for o in out if o["cid"] == cid]
        b = li[0]
        d = max(abs(o["mae"] - b["mae"]) for o in li)
        best = min(li, key=lambda o: o["mae"])
        print(f"  {cid[:38]:<38} delta_MAE_max {d:7.4f}  melhor exp={best['exp']}"
              f" ({best['mae']:.4f})"
              f"{'  <-- FECHA' if best['tripe'] and not b['tripe'] else ''}")
    if a.json:
        a.json.write_text(json.dumps(out, indent=1, default=float),
                          encoding="utf-8")
        print(f"\njson -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
