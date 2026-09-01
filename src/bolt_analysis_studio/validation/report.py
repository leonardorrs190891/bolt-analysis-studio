# -*- coding: utf-8 -*-
"""CLI dos reports de validacao (spec §3):
  python -m bolt_analysis_studio.validation.report            # geral do store/seed
  python -m bolt_analysis_studio.validation.report --case ID  # re-simula 1 caso
  python -m bolt_analysis_studio.validation.report --all      # re-simula os 128 (~min)
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from .case_registry import all_records, record
from .report_html import write_reports
from .runner import simulate_case
from .store import ValidationStore


def ensure_reports(out_dir: Optional[Path] = None,
                   store_path: Optional[Path] = None) -> Path:
    """Garante o report geral (seed da galeria se o store estiver vazio).
    Nao simula nada — rapido o bastante p/ o menu da GUI."""
    store = ValidationStore(path=store_path)
    if not store.all_ids():
        store.seed_from_gallery()
        store.save()
    return write_reports(out_dir=out_dir, store_path=store_path)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="bolt_analysis_studio.validation.report")
    ap.add_argument("--all", action="store_true", help="re-simula os 128 casos")
    ap.add_argument("--case", help="re-simula um caso (case_id)")
    ap.add_argument("--from-store", action="store_true",
                    help="so regenera HTML do cache, sem simular")
    ap.add_argument("--cap", type=int, default=None,
                    help="teto de ciclos por caso (smoke)")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--store", type=Path, default=None,
                    help="path do validation_store.json (default canonico)")
    ap.add_argument("--resume", action="store_true",
                    help="pula casos com resultado fresco no store (retomada "
                         "de batch interrompido)")
    ap.add_argument("--gravar", action="store_true",
                    help="AUTORIZA escrever no store canônico com --case. Sem "
                         "esta flag, --case simula e gera o HTML mas NÃO grava: "
                         "depurar um caso deixava de re-carimbar `generated_at` "
                         "e quebrava a uniformidade de procedência do store "
                         "(medido 2026-07-29). --all e --import gravam sempre.")
    ap.add_argument("--import", dest="import_path", type=Path, default=None,
                    help="importa um .bascase.json (caso do usuario): valida, "
                         "roda o ajuste previo per-rig e gera o report")
    args = ap.parse_args(argv)

    store = ValidationStore(path=args.store)
    if not store.all_ids():
        n = store.seed_from_gallery()
        print(f"seed da galeria: {n} casos")
    todo = []
    if args.import_path:
        from .prefit import prefit_user_case
        from .user_cases import import_user_case
        try:
            rec = import_user_case(args.import_path)
        except (ValueError, OSError) as exc:
            print(f"importação falhou: {exc}")
            return 2
        block = prefit_user_case(rec, n_cap=args.cap)
        mae_txt = ("—" if block.get("mae") is None
                   else f"{block['mae']:.4f}")
        print(f"importado: {rec.case_id} | prefit MAE={mae_txt} | "
              f"overrides: {sorted(block['overrides'])}")
        todo = [rec]
    elif args.case:
        rec = record(args.case)
        if rec is None:
            print(f"caso desconhecido: {args.case}")
            return 2
        todo = [rec]
    elif args.all:
        todo = all_records()
        if args.resume:
            todo = [r for r in todo if store.is_stale(r.case_id)]
            print(f"--resume: {len(todo)} casos pendentes")
    # --case é comando de DEPURAÇÃO: por default ele simula, mostra o número e
    # gera o HTML, mas NÃO persiste. Persistir re-carimbava `generated_at`
    # daquele registro e o store perdia a uniformidade de procedência (202
    # `parallel-batch` + 1 timestamp) — aconteceu em 2026-07-29 e exigiu
    # restaurar o arquivo. Quem re-carimba de propósito passa `--gravar`.
    grava = bool(args.all or args.import_path or args.gravar
                 or args.store is not None)
    for i, rec in enumerate(todo, 1):
        res = simulate_case(rec, n_cap=args.cap)
        store.put(res)
        tag = (f"MAE={res.mae:.4f}" if res.mae is not None
               else ("ok" if res.ok else f"ERRO: {res.error}"))
        print(f"[{i}/{len(todo)}] {rec.case_id:45s} {tag}", flush=True)
        if grava and i % 10 == 0:
            store.save()                 # progresso sobrevive a um kill
    if todo and grava:
        store.save()
    elif todo:
        print("store NÃO gravado (--case sem --gravar): o arquivo canônico fica "
              "intacto e o HTML sai do resultado EM MEMÓRIA.")
    # Sem gravar, `write_reports` releria o arquivo e o HTML mostraria o número
    # VELHO — pior que o problema que a guarda resolve. Passo os resultados em
    # memória (o store carregado do disco + o `put` fresco deste run).
    mem = (None if grava
           else {r.case_id: store.get(r.case_id) for r in all_records()})
    master = write_reports(out_dir=args.out, results=mem,
                           store_path=args.store)
    print(f"reports em {master.parent} (master: {master.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
