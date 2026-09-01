# -*- coding: utf-8 -*-
"""Prospective test with a FROZEN configuration (2026-08-28, robustness item 2).

Takes the adopted configuration exactly as it was committed on or before a
freeze date, and predicts with it every comparable curve whose reference CSV
entered the repository AFTER that date. Those curves could not have informed
any constant of that configuration, so the result is a genuine temporal
hold-out at configuration level. The same curves under today's configuration
(the canonical store) measure what the later adjustments bought.

The historical file is read through BAS_ADOPTED_CONFIGS (the knowledge base's
sandbox hook); the canonical file, the store and the engine are untouched.
Inputs (preload, amplitude, geometry, roughness) come from the case registry
as today; only constants and forms are frozen. Engine capabilities added after
the freeze are default-inert, so they stay off unless the frozen file asks for
them (it cannot: the fields did not exist yet).

    py -3.12 New_Theory/frozen_config_holdout.py --freeze 2026-07-14 [--workers 2]

Output: New_Theory/holdout/frozen_<date>.json
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "New_Theory"))
SAIDA = RAIZ / "New_Theory" / "holdout"
CFG_REL = "New_Theory/adopted_configs.json"
GUARDAR = ("case_id", "ok", "error", "mae", "rmse", "resid_std", "maxerr",
           "final_pred", "final_data", "align", "metric_x", "metric_pred",
           "metric_data", "engine_fingerprint", "config_used")


def _git(*args) -> str:
    return subprocess.run(["git", *args], cwd=str(RAIZ), capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


def _sim_one(cid: str) -> dict:
    from bolt_analysis_studio.validation import runner as rn
    from bolt_analysis_studio.validation.case_registry import record
    r = rn.simulate_case(record(cid)).to_dict()
    out = {k: r.get(k) for k in GUARDAR}
    cu = out.get("config_used") or {}
    out["config_used"] = {"overrides": cu.get("overrides"), "n_max": cu.get("n_max")}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="frozen_config_holdout")
    ap.add_argument("--freeze", default="2026-07-14",
                    help="configuration as committed on or before this date")
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args(argv)

    import robustness_checks as R
    import bolt_analysis_studio.validation.report_html as rh
    from bolt_analysis_studio.validation.case_registry import all_records

    versoes = [l.split() for l in _git("log", "--format=%H %ad", "--date=short",
                                       "--reverse", "--", CFG_REL).splitlines()
               if l.strip()]
    ate = [v for v in versoes if v[1] <= args.freeze]
    if not ate:
        print("no committed configuration on or before", args.freeze)
        return 2
    h, d = ate[-1]
    SAIDA.mkdir(parents=True, exist_ok=True)
    congelado = SAIDA / f"adopted_configs_{d}_{h[:7]}.json"
    congelado.write_text(_git("show", f"{h}:{CFG_REL}"), encoding="utf-8", newline="")
    n_groups = len((json.loads(congelado.read_text(encoding="utf-8")).get("sources") or {}))

    recs = [r for r in all_records() if rh.caso_comparavel(r.source, r.case_id)]
    sel, datas = [], {}
    for r in recs:
        rel = Path(r.csv_path).resolve().relative_to(RAIZ).as_posix()
        t_in, t_mod = R.datas_csv(rel)
        datas[r.case_id] = {"t_in": t_in, "t_mod": t_mod}
        if t_in and t_in > d:
            sel.append(r)
    sel.sort(key=lambda r: -int(r.validation_case.n_cycles))
    print(f"[frozen] configuration {h[:7]} ({d}, {n_groups} groups) -> "
          f"{len(sel)} curves entered after it · {args.workers} workers", flush=True)

    os.environ["BAS_ADOPTED_CONFIGS"] = str(congelado)   # inherited by the workers
    t0 = time.time()
    out = {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(_sim_one, r.case_id): r.case_id for r in sel}
        done = 0
        for fut in as_completed(futs):
            cid = futs[fut]
            try:
                out[cid] = fut.result()
            except Exception as exc:
                out[cid] = {"case_id": cid, "ok": False,
                            "error": f"{type(exc).__name__}: {exc}"}
            done += 1
            if done % 10 == 0 or done == len(sel):
                print(f"  [{done}/{len(sel)}] {time.time() - t0:.0f}s", flush=True)
    os.environ.pop("BAS_ADOPTED_CONFIGS", None)
    registro = {"freeze_date": d, "freeze_commit": h, "n_groups_frozen": n_groups,
                "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
                "seconds": round(time.time() - t0),
                "curves": {cid: datas[cid] for cid in out},
                "results": out}
    alvo = SAIDA / f"frozen_{d}.json"
    alvo.write_text(json.dumps(registro), encoding="utf-8", newline="")
    n_ok = sum(1 for v in out.values() if v.get("ok"))
    print(f"[frozen] {n_ok}/{len(sel)} simulated in {time.time() - t0:.0f}s -> "
          f"{alvo.relative_to(RAIZ)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
