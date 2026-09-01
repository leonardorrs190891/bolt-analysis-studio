# -*- coding: utf-8 -*-
"""Ablation study for the paper (2026-08-28, item 1 of the robustness list).

Re-simulates every comparable curve with ONE change at a time and records
the metrics, so the paper can show what each part of the model buys:

    stiffness_frozen  alpha_GW = 0  (k_j constant => Phi constant: the
                      Greenwood-Williamson stiffness softening is frozen)
    open_loop         loss rates and slip resolution see F_0 = F_0_init while
                      the preload keeps integrating (no F_0 feedback into the
                      rates: the open-loop counterpart of the coupling)
    no_embedding      EmbeddingLoss removed
    no_creep          CreepLoss removed
    no_wear           WearLoss and ThreadFrettingLoss removed
    no_loosening      RotationalLooseningLoss removed
    no_damage         c_D = 0 (the surface-damage state never grows)

Nothing here touches the adopted configurations or the canonical store: the
change travels in the BAS_ABLATION environment variable, read by the runner's
default-inert hook (`runner._ablacao`), and the results go to
New_Theory/ablation/ablation_<variant>.json, stamped with the fingerprint of
the configuration they were run against.

    py -3.12 New_Theory/ablation_run.py [--variants a,b] [--workers 6]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
SAIDA = RAIZ / "New_Theory" / "ablation"

VARIANTES = {
    "stiffness_frozen": {"overrides": {"alpha_GW": 0.0}},
    "open_loop": {"open_loop": True},
    "no_embedding": {"drop": ["embedding"]},
    "no_creep": {"drop": ["creep"]},
    "no_wear": {"drop": ["wear", "thread_fretting"]},
    "no_loosening": {"drop": ["rotational_loosening"]},
    "no_damage": {"overrides": {"c_D": 0.0}},
    # a-priori: no per-rig configuration at all, only the shared constants and
    # the handbook inputs (Section 4.10.4 of the paper)
    "a_priori": {"bare": True},
}
GUARDAR = ("case_id", "ok", "error", "mae", "rmse", "resid_std", "maxerr",
           "final_pred", "final_data", "align", "metric_x", "metric_pred",
           "metric_data", "energy_budget", "engine_fingerprint")


def _sim_one(cid: str) -> dict:
    """Worker: one curve under the ablation carried by the environment."""
    from bolt_analysis_studio.validation import runner as rn
    from bolt_analysis_studio.validation.case_registry import record
    r = rn.simulate_case(record(cid)).to_dict()
    return {k: r.get(k) for k in GUARDAR}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="ablation_run")
    ap.add_argument("--variants", default=",".join(VARIANTES))
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args(argv)

    import bolt_analysis_studio.validation.report_html as rh
    from bolt_analysis_studio.validation import runner as rn
    from bolt_analysis_studio.validation.case_registry import all_records
    fp = rn.engine_fingerprint()
    recs = [r for r in all_records() if rh.caso_comparavel(r.source, r.case_id)]
    recs.sort(key=lambda r: -int(r.validation_case.n_cycles))
    ids = [r.case_id for r in recs]
    SAIDA.mkdir(parents=True, exist_ok=True)

    for nome in [v.strip() for v in args.variants.split(",") if v.strip()]:
        spec = VARIANTES[nome]
        os.environ[rn._ABL_ENV] = json.dumps(spec)     # inherited by the workers
        t0 = time.time()
        print(f"[ablation] {nome} {spec} · {len(ids)} curves · "
              f"{args.workers} workers", flush=True)
        out: dict = {}
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(_sim_one, cid): cid for cid in ids}
            done = 0
            for fut in as_completed(futs):
                cid = futs[fut]
                try:
                    out[cid] = fut.result()
                except Exception as exc:               # honest: record, continue
                    out[cid] = {"case_id": cid, "ok": False,
                                "error": f"{type(exc).__name__}: {exc}"}
                done += 1
                if done % 25 == 0 or done == len(ids):
                    print(f"  [{done}/{len(ids)}] {time.time() - t0:.0f}s",
                          flush=True)
        registro = {"variant": nome, "spec": spec, "fingerprint_base": fp,
                    "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
                    "seconds": round(time.time() - t0),
                    "results": out}
        alvo = SAIDA / f"ablation_{nome}.json"
        alvo.write_text(json.dumps(registro), encoding="utf-8", newline="")
        n_ok = sum(1 for v in out.values() if v.get("ok"))
        print(f"[ablation] {nome}: {n_ok}/{len(ids)} ok in "
              f"{time.time() - t0:.0f}s -> {alvo.relative_to(RAIZ)}", flush=True)
    os.environ.pop(rn._ABL_ENV, None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
