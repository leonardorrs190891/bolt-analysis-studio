# -*- coding: utf-8 -*-
"""F3-ICMEZ (prereg no ledger 2026-07-21, item 5 da varredura): re-grid
min-max-maxerr das 3 constantes JÁ fitadas do grupo (c_bend 1,0 /
k_wear_scale_tr 0,07 / loose_arrest_floor 0,28) — o PR-25 otimizou
maxscore MAE+std, nunca maxerr. Alvos: demir amp0p3_F14p3_lk13p8 (0,101) e
amp0p3_F17p6_lk13p8 (0,118). Gate: TODOS os 8 casos da fonte com tripé<0,1
(min-max sobre a fonte inteira) e mediana não piora >0,005; senão FAIL.
PASS ⇒ adota (single-writer) + verificação + store. Sims ~1 s (146-200
ciclos) — grade completa custa ~1 min.
Uso: python New_Theory/f3_icmez_fit.py [--workers N]
"""
from __future__ import annotations

import argparse
import io
import json
import os
import statistics
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
GRUPO = "ICMEZ_2025"
BASE = dict(c_bend=1.0, k_wear_scale_tr=0.07, loose_arrest_floor=0.28)
MULT = {"c_bend": [0.8, 1.0, 1.2], "k_wear_scale_tr": [0.8, 1.0, 1.2],
        "loose_arrest_floor": [0.9, 1.0, 1.1]}


def _sandbox(cb, kw, fl):
    d = json.loads(io.open(_ROOT / "New_Theory/adopted_configs.json",
                           encoding="utf-8").read())
    d["sources"][GRUPO]["cfg"].update(
        c_bend=cb, k_wear_scale_tr=kw, loose_arrest_floor=fl)
    fd, p = tempfile.mkstemp(suffix=".json", prefix="icmez_")
    with io.open(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False))
    return p


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(args):
    cid, sb, tag = args
    os.environ["BAS_ADOPTED_CONFIGS"] = sb
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    r = simulate_case(record(cid), now="f3-icmez")
    return {"tag": tag, "case_id": cid, "mae": r.mae, "maxerr": r.maxerr,
            "ok": r.ok}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))
    from bolt_analysis_studio.validation.case_registry import all_records
    CASOS = [r.case_id for r in all_records() if r.source == GRUPO]

    store_path = _ROOT / "Models/CALIBRATION_AND_VALIDATION/validation_store.json"
    antes = json.loads(io.open(store_path, encoding="utf-8").read())
    med_base = statistics.median(antes[c]["mae"] for c in CASOS)

    tarefas, sbs = [], []
    for cb in MULT["c_bend"]:
        for kw in MULT["k_wear_scale_tr"]:
            for fl in MULT["loose_arrest_floor"]:
                sb = _sandbox(BASE["c_bend"] * cb,
                              BASE["k_wear_scale_tr"] * kw,
                              BASE["loose_arrest_floor"] * fl)
                sbs.append(sb)
                tag = f"cb={cb}|kw={kw}|fl={fl}"
                tarefas += [(c, sb, tag) for c in CASOS]
    print(f"[grade] {len(tarefas)} sims", flush=True)
    grade = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, t): t for t in tarefas}
        for fut in as_completed(futs):
            r = fut.result()
            grade.setdefault(r["tag"], {})[r["case_id"]] = r
    for sb in sbs:
        try:
            os.unlink(sb)
        except OSError:
            pass

    def escore(pc):
        piores = [max((v["maxerr"] or 9) - 0.10, 0,
                      (v["mae"] or 9) - 0.10) for v in pc.values()]
        return (max(piores), statistics.median(v["mae"] for v in pc.values()))

    best = min(grade, key=lambda t: escore(grade[t]))
    fin = grade[best]
    mults = dict(p.split("=") for p in best.split("|"))
    cfg_fin = dict(c_bend=BASE["c_bend"] * float(mults["cb"]),
                   k_wear_scale_tr=BASE["k_wear_scale_tr"] * float(mults["kw"]),
                   loose_arrest_floor=BASE["loose_arrest_floor"] * float(mults["fl"]))
    todos_ok = all((v["mae"] or 9) < 0.10 and (v["maxerr"] or 9) < 0.10
                   for v in fin.values())
    med_fin = statistics.median(v["mae"] for v in fin.values())
    verdict = "PASS" if (todos_ok and med_fin <= med_base + 0.005) else "FAIL"
    for c in sorted(fin):
        print(f"  {c[-24:]:24s} {antes[c]['mae']:.3f}/{antes[c]['maxerr']:.3f}"
              f" -> {fin[c]['mae']:.3f}/{fin[c]['maxerr']:.3f}", flush=True)
    print(f"[fit] {cfg_fin} | mediana {med_base:.4f}->{med_fin:.4f} | "
          f"verdict={verdict}", flush=True)

    out = dict(secao="F3-ICMEZ", cfg=cfg_fin, mediana=dict(antes=med_base,
               depois=med_fin),
               tripe={c: dict(mae=v["mae"], maxerr=v["maxerr"])
                      for c, v in fin.items()}, verdict=verdict)
    p = _ROOT / "New_Theory/f3_icmez_result.json"
    txt = json.dumps(out, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(p, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    if verdict != "PASS":
        return 1

    # ---- adoção + verificação + store ----
    P = _ROOT / "New_Theory/adopted_configs.json"
    d = json.loads(io.open(P, encoding="utf-8").read())
    g = d["sources"][GRUPO]
    g["cfg"].update(cfg_fin)
    g.setdefault("prov", {})["_regrid_f3"] = (
        "F3 2026-07-21: re-grid min-max-maxerr das 3 constantes já fitadas "
        "(PR-25 otimizava maxscore, nunca maxerr); mesmas classes de "
        "procedência")
    g["verdict"] = g.get("verdict", "") + (
        f" | F3-ICMEZ: re-grid min-max PASS 8/8 tripé (f3_icmez_result.json)")
    txt = json.dumps(d, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(P, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print("[adoção] gravada", flush=True)

    res = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, (c, "", "ver")): c for c in CASOS}
        for fut in as_completed(futs):
            r = fut.result()
            res[r["case_id"]] = r
    ok = all(abs(res[c]["mae"] - fin[c]["mae"]) <= 0.005 for c in CASOS)
    print(f"[verificação] reproduz: {ok}", flush=True)
    if not ok:
        return 1
    from bolt_analysis_studio.validation.runner import (CaseResult,
                                                        simulate_case)
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.store import ValidationStore
    store = ValidationStore()
    for c in CASOS:
        store.put(simulate_case(record(c), now="f3-icmez-adocao"))
    for _ in range(200):
        try:
            store.save(); break
        except PermissionError:
            time.sleep(0.05)
    print("[store] 8 casos ICMEZ atualizados", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
