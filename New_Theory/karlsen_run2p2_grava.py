# -*- coding: utf-8 -*-
"""Escrita do store para o D-Y — re-simula so' o KARLSEN, re-carimba o resto.

Justificativa de NAO re-simular as 210: o G5 do executor JA rodou as 210 sob a
config nova e provou que **apenas** a `run2p2` mudou (as outras 209 deram
diferenca 0 contra o store). Re-simular tudo de novo custaria ~50 min para
reproduzir um resultado ja medido.

O fingerprint MUDA (o `engine_fingerprint` hasheia o bloco `shared` + os
configs adotados, e o `k_ratchet` do run2p2 foi alterado), entao TODAS as
entradas precisam do carimbo novo — senao o store fica com 2 fingerprints e
qualquer adocao futura via batch quebra a uniformidade (gotcha do
`exemplo_m12_sintetico`).

    py -3.12 New_Theory/karlsen_run2p2_grava.py            # dry-run
    py -3.12 New_Theory/karlsen_run2p2_grava.py --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.runner as rn                  # noqa: E402
from bolt_analysis_studio.validation import report_html as rh        # noqa: E402
from bolt_analysis_studio.validation.case_registry import (          # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.runner import CaseResult        # noqa: E402

STORE_P = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"
FONTE = "KARLSEN_2022"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    store = json.loads(STORE_P.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    fp_old = {store[c].get("engine_fingerprint") for c in store}
    fp = rn.engine_fingerprint()
    print(f"fingerprint  antes {sorted(x for x in fp_old if x)} -> agora {fp}",
          flush=True)

    cids = sorted(c for c in recs if recs[c].source == FONTE)
    print(f"re-simulando {len(cids)} do {FONTE}...", flush=True)
    mudou = []
    for cid in cids:
        res = rn.simulate_case(record(cid))
        assert res.ok, f"{cid}: {res.error}"
        old = store.get(cid, {})
        d = max(abs(res.mae - old.get("mae", 9)),
                abs(res.maxerr - old.get("maxerr", 9)),
                abs(res.resid_std - old.get("resid_std", 9)))
        if d > 1e-12:
            mudou.append(cid)
        print(f"  {cid:<42} {res.mae:.4f}/{res.maxerr:.4f}/{res.resid_std:.4f}"
              f"   d={d:.2e}", flush=True)
        nd = res.to_dict()
        nd["engine_fingerprint"] = fp
        store[cid] = nd
    print(f"\nmudaram: {mudou}   (esperado: so a run2p2)", flush=True)
    assert mudou == ["karlsen2022_M30_HV_run2p2"], "isolamento quebrado"

    # re-carimbo dos demais (G5 ja provou bit-identidade)
    n_re = 0
    for cid in store:
        if store[cid].get("engine_fingerprint") != fp:
            store[cid]["engine_fingerprint"] = fp
            n_re += 1
    print(f"re-carimbadas sem re-simular (G5 provou): {n_re}", flush=True)

    # censo com o helper CANONICO
    res_all = {c: CaseResult.from_dict(store[c]) for c in store if c in recs}
    pisos = rh._pisos_medidos([(recs[c].source, r) for c, r in res_all.items()])
    n = 0
    for cid, r in res_all.items():
        if not rh.caso_comparavel(recs[cid].source, cid) or r.mae is None:
            continue
        sd = rh.sres_para_censo(r)
        if sd is None:
            continue
        if (r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX
                and sd <= rh.limite_sres(recs[cid].source, pisos)):
            n += 1
    print(f"\ncenso (helper canonico): {n}", flush=True)
    print(f"limite_sres(KARLSEN): "
          f"{rh.limite_sres(FONTE, pisos):.4f}", flush=True)

    if a.write:
        STORE_P.write_text(json.dumps(store, indent=1), encoding="utf-8")
        print(f"\nstore GRAVADO — {len(store)} entradas, fingerprint unico {fp}",
              flush=True)
    else:
        print("\n(dry-run: nada gravado; use --write)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
