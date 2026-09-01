# -*- coding: utf-8 -*-
"""F3.2-CHU (prereg 2026-07-21): µ(N) da Fig. 5 (input-de-paper, CSVs já
digitalizados) + floor lido + receita do test1, ESCOPADO por per_case aos
alvos test2/4/7/8 (test1/3/5/6/9 intocados por construção — gate verifica).
Gate G-CHU-a: tripé<0,1 em test4 E ≥2 de {test2,test7,test8}; controles
bit-idênticos. NÃO adota. Saída: f3_chu_result.json.
Uso: python New_Theory/f3_chu_fit.py [--workers N]
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_FIG5 = (_ROOT / "BAS_V2_papers/E. Rodada 4 (deep-research 2026-07-11)/"
         "digitized_csv")

ALVOS = {
    "test2": dict(cid="chu2026ti_D0p4mm_F0_49kN_test2", floor=0.11),
    "test4": dict(cid="chu2026ti_D0p7mm_F0_49kN_test4", floor=0.29),
    "test7": dict(cid="chu2026ti_D0p4mm_F0_61kN_test7", floor=0.18),
    "test8": dict(cid="chu2026ti_D0p4mm_F0_73kN_test8", floor=0.16),
}
RECEITA = dict(c_bend=1.881, mu_thread=0.05, C_creep=0.0, emb_um=1.6)
CONTROLES = ["chu2026ti_D0p3mm_F0_49kN_test1", "chu2026ti_D0p5mm_F0_49kN_test3",
             "chu2026ti_D1p0mm_F0_49kN_test5",
             "chu2026ti_D1p0mm_F0_49kN_test6_repeat"]


def _schedule(tok):
    p = _FIG5 / f"chu2026ti_fig5_muplate_{tok}.csv"
    rows = list(csv.reader(io.open(p, encoding="utf-8")))[1:]
    return [[float(a), float(b)] for a, b in rows if a.strip()]


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(args):
    cid, sb = args
    if sb:
        os.environ["BAS_ADOPTED_CONFIGS"] = sb
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    r = simulate_case(record(cid), now="f3-chu")
    return {"case_id": cid, "mae": r.mae, "maxerr": r.maxerr, "ok": r.ok,
            "err": r.error}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))
    store = json.loads(io.open(
        _ROOT / "Models/CALIBRATION_AND_VALIDATION/validation_store.json",
        encoding="utf-8").read())

    d = json.loads(io.open(_ROOT / "New_Theory/adopted_configs.json",
                           encoding="utf-8").read())
    # TENTATIVA 2: pack "" — a t1 usou "PACK" e mudou os MODOS de toda a
    # família (test5 0,040→0,182 etc.); os casos chu rodavam em DEFAULTS.
    # pack vazio ⇒ overrides {} p/ não-alvos (bit-idêntico) + per_case alvos.
    g = d["sources"].setdefault("CHU_2026", {"pack": "", "cfg": {}})
    g["pack"] = ""
    pc = g["cfg"].setdefault("per_case", {})
    for tok, a in ALVOS.items():
        pc[tok] = dict(RECEITA, mu_bearing_schedule=_schedule(tok),
                       loose_arrest_floor=a["floor"])
    fd, sb = tempfile.mkstemp(suffix=".json", prefix="chu_")
    with io.open(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False))

    ids = [a["cid"] for a in ALVOS.values()] + CONTROLES
    res = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, (cid, sb)): cid for cid in ids}
        for fut in as_completed(futs):
            r = fut.result()
            res[r["case_id"]] = r
            print(f"  {r['case_id'][-24:]:24s} mae="
                  f"{r['mae'] and round(r['mae'], 4)} mx="
                  f"{r['maxerr'] and round(r['maxerr'], 4)} "
                  f"{r['err'] or ''}", flush=True)
    os.unlink(sb)

    def passa(cid):
        v = res[cid]
        return (v.get("mae") or 9) < 0.10 and (v.get("maxerr") or 9) < 0.10

    t4 = passa(ALVOS["test4"]["cid"])
    outros = sum(passa(ALVOS[t]["cid"]) for t in ("test2", "test7", "test8"))
    ctrl_ok = all(res[c].get("mae") == store[c]["mae"] for c in CONTROLES)
    verdict = "PASS" if (t4 and outros >= 2 and ctrl_ok) else "FAIL"
    out = dict(secao="F3.2-CHU", receita=RECEITA,
               floors={t: a["floor"] for t, a in ALVOS.items()},
               tripe={a["cid"]: dict(mae=res[a["cid"]].get("mae"),
                                     maxerr=res[a["cid"]].get("maxerr"))
                      for a in ALVOS.values()},
               gate=dict(test4=t4, outros=outros, controles=ctrl_ok),
               verdict=verdict)
    p = _ROOT / "New_Theory/f3_chu_result.json"
    txt = json.dumps(out, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(p, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print(f"[gate] verdict={verdict} (test4={t4}, outros={outros}/3, "
          f"ctrl={ctrl_ok}) → {p}", flush=True)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
