# -*- coding: utf-8 -*-
"""Batch PARALELO de simulações de validação (pedido do professor 2026-07-15:
"can we run multiple shells to increase the speed?").

Fan-out por PROCESSOS (ProcessPoolExecutor, spawn no Windows): cada worker
simula uma fatia dos casos — as sims só LEEM adopted_configs/CSVs (o guard de
leitura do kb cobre locks transientes do OneDrive); a escrita do store é feita
UMA vez, no processo pai, ao final (single-writer preservado).

NÃO usar para fits/sondas que ESCREVEM adopted_configs.json entre sims —
esses continuam sequenciais por fonte (lição de colisão da campanha), ou
usam sandbox por processo via env BAS_ADOPTED_CONFIGS (ver knowledge_base).

Uso:
  python New_Theory/parallel_batch.py                      # 178 comparáveis
  python New_Theory/parallel_batch.py --sources LIU_2016,QIN_2024
  python New_Theory/parallel_batch.py --workers 6 --store  # grava no store
Saída: resumo por fonte + (--store) store canônico atualizado.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(case_id: str) -> dict:
    """Roda 1 caso e devolve o CaseResult como dict (picklável)."""
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    rec = record(case_id)
    if rec is None:
        return {"case_id": case_id, "ok": False, "error": "caso não encontrado"}
    res = simulate_case(rec, now="parallel-batch")
    return res.to_dict()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="parallel_batch")
    ap.add_argument("--sources", help="lista FONTE1,FONTE2 (default: todas)")
    ap.add_argument("--cases", help="lista case_id1,case_id2 (vence --sources)")
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2),
                    help="processos (default: nucleos-2)")
    ap.add_argument("--store", action="store_true",
                    help="grava os resultados no store canônico ao final")
    args = ap.parse_args(argv)

    sys.path.insert(0, str(_ROOT / "src"))
    from bolt_analysis_studio.validation.case_registry import all_records

    recs = [r for r in all_records() if r.source != "USER"]
    if args.cases:
        want = {c.strip() for c in args.cases.split(",") if c.strip()}
        recs = [r for r in recs if r.case_id in want]
    elif args.sources:
        want = {s.strip().upper() for s in args.sources.split(",") if s.strip()}
        recs = [r for r in recs if r.source in want]
    if not recs:
        print("nenhum caso selecionado"); return 1
    # maiores primeiro (melhor balanceamento: o 5e6-ciclos não fica por último)
    recs.sort(key=lambda r: -int(r.validation_case.n_cycles))
    ids = [r.case_id for r in recs]
    src_of = {r.case_id: r.source for r in recs}

    t0 = time.time()
    print(f"[parallel] {len(ids)} casos em {args.workers} workers", flush=True)
    results: dict = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, cid): cid for cid in ids}
        done = 0
        for fut in as_completed(futs):
            cid = futs[fut]
            try:
                results[cid] = fut.result()
            except Exception as exc:      # honesto: registra e segue
                results[cid] = {"case_id": cid, "ok": False,
                                "error": f"{type(exc).__name__}: {exc}"}
            done += 1
            r = results[cid]
            mae = r.get("mae")
            print(f"  [{done}/{len(ids)}] {cid[:42]:42s} "
                  f"mae={mae if mae is None else round(mae, 4)}"
                  + ("" if r.get("ok", False) else f"  ERR={r.get('error', '?')[:60]}"),
                  flush=True)

    per: dict = {}
    for cid, r in results.items():
        if r.get("mae") is not None:
            per.setdefault(src_of[cid], []).append(float(r["mae"]))
    import statistics as st
    for s in sorted(per):
        v = per[s]
        print(f"[{s}] n={len(v)} mediana={st.median(v):.4f}")

    if args.store:
        from bolt_analysis_studio.validation.runner import CaseResult
        from bolt_analysis_studio.validation.store import ValidationStore
        store = ValidationStore()
        n_put = 0
        for cid, r in results.items():
            if r.get("ok"):
                store.put(CaseResult(**r)); n_put += 1
        for _ in range(200):
            try:
                store.save(); break
            except PermissionError:
                time.sleep(0.05)
        print(f"[store] {n_put} resultados gravados (single-writer no pai)")

    print(f"[parallel] total {time.time()-t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
