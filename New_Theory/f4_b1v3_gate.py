# -*- coding: utf-8 -*-
"""F4 — GATE B1-v3 (prereg 2026-07-22-f4-l1v2-prereg-b1v3.md), candidato (c)
flank_s_crit. Fase de busca em cap 1e4 (idioma T4) + full-res na vencedora.

Uso (no worktree C:\\basl1v2): python New_Theory/f4_b1v3_gate.py [--workers N]
Saída: New_Theory/f4_b1v3_result.json
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

AF_CASES = {  # A_F [N] -> case_id (sweep do slope)
    7.5e3: "liu2017_axial_AF_7p5kN", 8.75e3: "liu2017_axial_AF_8p75kN",
    11.25e3: "liu2017_axial_AF_11p25kN", 12.5e3: "liu2017_axial_AF_12p5kN"}
F0_CASES = ["liu2017_axial_F0_15kN", "liu2017_axial_F0_16p5kN",
            "liu2017_axial_F0_18kN", "liu2017_axial_F0_19p5kN",
            "liu2017_axial_F0_21kN"]
BANDA = (-4.4e-5, -1.1e-5)
K_GRID = [10 ** e for e in (-14.0, -13.5, -13.0, -12.5, -12.0, -11.5)]
SC_FRAC = [0.0, 0.4, 0.6, 0.75, 0.9]
CAP = 10000


def _sandbox(k, sc):
    d = json.loads(io.open(_ROOT / "New_Theory/adopted_configs.json",
                           encoding="utf-8").read())
    g = d["sources"]["LIU_2017_axial"]
    g["cfg"].update(flank_wear_on=1.0, k_wear_flank=float(k),
                    flank_s_crit=float(sc), flank_amp_exp=1.5)
    fd, p = tempfile.mkstemp(suffix=".json", prefix="b1v3_")
    with io.open(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False))
    return p


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(args):
    cid, sb, tag, cap = args
    os.environ["BAS_ADOPTED_CONFIGS"] = sb
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    r = simulate_case(record(cid), n_cap=cap, now="f4-b1v3")
    return {"tag": tag, "case_id": cid, "mae": r.mae, "maxerr": r.maxerr,
            "final_pred": r.final_pred, "ok": r.ok, "err": r.error}


def _slope(fins):
    import numpy as np
    xs = sorted(fins)
    ys = [fins[x] for x in xs]
    a, _b = np.polyfit(xs, ys, 1)
    return float(a)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))

    # s_ref do rig (s_th @ A_F=10 kN)
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.inputs import (geometry_for_case,
                                                        inputs_for)
    rec0 = record(next(iter(AF_CASES.values())))
    inp0 = inputs_for(rec0.validation_case)
    geom0 = geometry_for_case(rec0.validation_case,
                              grip_mm=inp0["grip_mm"]["value"],
                              E=(inp0.get("E") or {}).get("value"))
    s_ref = 10e3 / geom0.k_b
    print(f"[b1v3] s_ref={s_ref:.3e} m (k_b={geom0.k_b:.3e})", flush=True)

    # ---- fase de busca (cap 1e4) ----
    tarefas, sbs = [], []
    for k in K_GRID:
        for fr in SC_FRAC:
            sb = _sandbox(k, fr * s_ref)
            sbs.append(sb)
            tag = f"k={k:.2e}|fr={fr}"
            for cid in list(AF_CASES.values()) + F0_CASES:
                tarefas.append((cid, sb, tag, CAP))
    print(f"[busca] {len(tarefas)} sims @cap {CAP}", flush=True)
    grade = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, t): t for t in tarefas}
        done = 0
        for fut in as_completed(futs):
            r = fut.result()
            grade.setdefault(r["tag"], {})[r["case_id"]] = r
            done += 1
            if done % 60 == 0 or done == len(tarefas):
                print(f"  [{done}/{len(tarefas)}]", flush=True)
    for sb in sbs:
        try:
            os.unlink(sb)
        except OSError:
            pass

    import statistics
    aval = {}
    for tag, g in grade.items():
        fins = {af: g[cid]["final_pred"] for af, cid in AF_CASES.items()
                if g.get(cid, {}).get("final_pred") is not None}
        if len(fins) < 4:
            continue
        sl = _slope(fins)
        mae_f0 = statistics.median(
            g[c]["mae"] for c in F0_CASES if g.get(c, {}).get("mae"))
        dist = 0.0 if BANDA[0] <= sl <= BANDA[1] else min(
            abs(sl - BANDA[0]), abs(sl - BANDA[1]))
        aval[tag] = dict(slope_cap=sl, dist=dist, mae_f0=mae_f0)
    best = min(aval, key=lambda t: (aval[t]["dist"], aval[t]["mae_f0"]))
    print(f"[busca] melhor {best}: slope@cap={aval[best]['slope_cap']:.3e} "
          f"dist={aval[best]['dist']:.2e} mae_f0={aval[best]['mae_f0']:.4f}",
          flush=True)
    top = sorted(aval, key=lambda t: (aval[t]["dist"], aval[t]["mae_f0"]))[:3]

    # ---- full-res nas top células ----
    tarefas, sbs = [], []
    for tag in top:
        k = float(tag.split("|")[0].split("=")[1])
        fr = float(tag.split("|")[1].split("=")[1])
        sb = _sandbox(k, fr * s_ref)
        sbs.append(sb)
        for cid in list(AF_CASES.values()) + F0_CASES:
            tarefas.append((cid, sb, "FULL|" + tag, None))
    print(f"[full] {len(tarefas)} sims full-res (1e6)", flush=True)
    full = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, t): t for t in tarefas}
        done = 0
        for fut in as_completed(futs):
            r = fut.result()
            full.setdefault(r["tag"], {})[r["case_id"]] = r
            done += 1
            print(f"  [{done}/{len(tarefas)}] {r['case_id'][-10:]} "
                  f"fim={r['final_pred'] and round(r['final_pred'], 3)}",
                  flush=True)
    for sb in sbs:
        try:
            os.unlink(sb)
        except OSError:
            pass

    res_full = {}
    for tag, g in full.items():
        fins = {af: g[cid]["final_pred"] for af, cid in AF_CASES.items()}
        sl = _slope(fins)
        mae_f0_max = max((g[c]["mae"] or 9) for c in F0_CASES)
        passa = BANDA[0] <= sl <= BANDA[1]
        res_full[tag] = dict(slope=sl, passa_banda=passa,
                             fins={str(af): fins[af] for af in sorted(fins)},
                             mae_f0_max=mae_f0_max,
                             af_mae={cid: g[cid]["mae"]
                                     for cid in AF_CASES.values()})
        print(f"[full] {tag}: slope={sl:.3e} banda={passa} "
              f"mae_f0_max={mae_f0_max:.4f}", flush=True)

    ok_tags = [t for t, v in res_full.items()
               if v["passa_banda"] and v["mae_f0_max"] < 0.026]
    verdict = "PASS-G4a" if ok_tags else "FAIL-G4a"
    out = dict(prereg="docs/superpowers/specs/2026-07-22-f4-l1v2-prereg-b1v3.md",
               s_ref=s_ref, banda=BANDA, busca=aval, full=res_full,
               vencedores=ok_tags, verdict=verdict)
    p = _ROOT / "New_Theory/f4_b1v3_result.json"
    txt = json.dumps(out, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(p, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print(f"[gate] {verdict} → {p}", flush=True)
    return 0 if ok_tags else 1


if __name__ == "__main__":
    raise SystemExit(main())
