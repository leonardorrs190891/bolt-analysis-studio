# -*- coding: utf-8 -*-
"""Benchmark against a classical staged loosening model (2026-08-31).

The reviewer's question: the paper compares the model against empirical decay
laws fitted to the data, not against a mechanistic alternative. This runs the
earlier-generation engine of this repository, an implementation of the
classical staged formulation (Jiang's stages with friction evolution and
Archard wear), on the same curves, with the same published inputs and no
per-rig calibration, and scores it with the same metric. The comparison is
therefore a-priori against a-priori: neither model is tuned to the curve.

    py -3.12 New_Theory/benchmark_v1.py [--workers 5] [--limit N]

Output: New_Theory/holdout/benchmark_v1.json
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "New_Theory"))
SAIDA = RAIZ / "New_Theory" / "holdout"
N_CAP = 200_000          # the V1 engine stores per-cycle history; cap the cost


def _uma(cid):
    """One curve through the classical engine, scored with the paper's metric."""
    import re
    from bolt_analysis_studio.numerical.coupled_loosening_analyzer import (
        create_analyzer_from_bolt_size)
    from bolt_analysis_studio.validation import runner as rn
    from bolt_analysis_studio.validation.case_registry import record
    rec = record(cid)
    vc = rec.validation_case
    inp = rn.inputs_for(vc)
    ref = rn._reference_curve(rec) if hasattr(rn, "_reference_curve") else None
    # inputs exactly as the paper reports them, the same ones V2 receives
    d_mm, p_mm = [float(x) for x in re.findall(r"[\d.]+", vc.bolt_size)[:2]]
    delta_mm = float(vc.transverse_displacement_mm or 0.0)
    F0 = float(vc.initial_preload_N or 0.0)
    mu = float(inp["mu"]["value"])
    grip = float(inp["grip_mm"]["value"])
    ana = create_analyzer_from_bolt_size(
        diameter_mm=d_mm, pitch_mm=p_mm, grip_length_mm=grip, mu_initial=mu,
        lubricated=False, transverse_displacement_mm=delta_mm)
    n_max = int(min(rn._n_max_for(rec) if hasattr(rn, "_n_max_for")
                    else vc.n_cycles, N_CAP))
    F_tr = mu * F0 * 1.05 if delta_mm > 0 else float(getattr(vc, "axial_force_amplitude_N", 0) or 0.0)
    res = ana.run_analysis(preload_initial=F0, F_transverse=F_tr,
                           n_cycles=n_max, output_interval=max(1, n_max // 400))
    cyc = np.asarray(getattr(res, "cycles", []), float)
    pre = np.asarray(getattr(res, "preload", []), float)
    if len(cyc) < 3 or len(pre) != len(cyc) or F0 <= 0:
        return {"case_id": cid, "erro": "empty V1 history"}
    ratio = pre / F0
    # same metric as the paper: align at the first scored cycle, score on the
    # digitised abscissae inside the window the canonical run used
    r_v2 = rn.simulate_case(rec)
    x = np.asarray(r_v2.metric_x, float)
    dado = np.asarray(r_v2.metric_data, float)
    if len(x) < 3:
        return {"case_id": cid, "erro": "no metric window"}
    pred = np.interp(x, cyc, ratio)
    a0 = float(np.interp(x[0], cyc, ratio))
    if a0 <= 0:
        return {"case_id": cid, "erro": "V1 alignment at zero"}
    pred = pred / a0
    e = pred - dado
    return {"case_id": cid, "source": rec.source,
            "mae": float(np.mean(np.abs(e))), "maxerr": float(np.max(np.abs(e))),
            "resid_std": float(np.std(e)), "final_pred": float(pred[-1]),
            "final_data": float(dado[-1]), "n": len(x),
            "mae_v2": float(r_v2.mae)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="benchmark_v1")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)
    import bolt_analysis_studio.validation.report_html as rh
    from bolt_analysis_studio.validation import runner as rn
    from bolt_analysis_studio.validation.case_registry import all_records
    recs = [r for r in all_records() if rh.caso_comparavel(r.source, r.case_id)]
    ids = [r.case_id for r in recs]
    if args.limit:
        ids = ids[:args.limit]
    print(f"[v1] {len(ids)} curves, {args.workers} workers", flush=True)
    t0 = time.time()
    out = {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(_uma, c): c for c in ids}
        done = 0
        for fut in as_completed(futs):
            c = futs[fut]
            try:
                out[c] = fut.result()
            except Exception as exc:
                out[c] = {"case_id": c, "erro": f"{type(exc).__name__}: {exc}"}
            done += 1
            if done % 20 == 0 or done == len(ids):
                print(f"  [{done}/{len(ids)}] {time.time() - t0:.0f}s", flush=True)
    ok = [z for z in out.values() if "erro" not in z]
    reg = {"generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
           "fingerprint": rn.engine_fingerprint(), "n_cap": N_CAP,
           "n": len(ids), "n_ok": len(ok),
           "mae_med": float(np.median([z["mae"] for z in ok])) if ok else None,
           "mae_v2_med": float(np.median([z["mae_v2"] for z in ok])) if ok else None,
           "resultados": out}
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "benchmark_v1.json").write_text(json.dumps(reg), encoding="utf-8",
                                             newline="")
    print(f"[v1] {len(ok)}/{len(ids)} scored in {time.time() - t0:.0f}s | "
          f"median MAE {reg['mae_med']} (calibrated V2 on the same curves: "
          f"{reg['mae_v2_med']})", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
