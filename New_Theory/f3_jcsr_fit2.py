# -*- coding: utf-8 -*-
"""F3.1-JCSR TENTATIVA 2: os ótimos da tentativa 1 bateram na borda da grade
(tc=2x, alpha=3 = máximos) — estende a busca SÓ para stainless_seawater e
outdoor (galv/plain_sea já fecharam o tripé na t1 e ficam com aquelas células).

Grade t2: C ∈ seed×{1,1.5,2,2.5,3} · t_c ∈ seed×{1.5,2,3,4,6} ·
alpha ∈ {2.5,3,4,5,6} = 125 células × 2 condições.
Uso: python New_Theory/f3_jcsr_fit2.py [--workers N]
Saída: New_Theory/f3_jcsr_result2.json (funde t1+t2 e re-avalia o gate).
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

D = 86400.0
COND = {
    "stainless_seawater": dict(cid="jcsr2023_stainless_seawater",
                               grupo="JCSR_2023_stainless_seawater",
                               C_seed=8.68e-10, tc_seed=24.7 * D),
    "outdoor": dict(cid="jcsr2023_plain_outdoor",
                    grupo="JCSR_2023_outdoor",
                    C_seed=3.40e-10, tc_seed=99.0 * D),
}
C_MULT = [1.0, 1.5, 2.0, 2.5, 3.0]
TC_MULT = [1.5, 2.0, 3.0, 4.0, 6.0]
ALPHAS = [2.5, 3.0, 4.0, 5.0, 6.0]


def _sandbox(grupo, C, tc, a):
    d = json.loads(io.open(_ROOT / "New_Theory/adopted_configs.json",
                           encoding="utf-8").read())
    d["sources"][grupo] = {"pack": "PACK", "cfg": {
        "creep_mode": "saturating", "C_creep": float(C),
        "creep_t_c": float(tc), "creep_alpha_sat": float(a)}}
    fd, p = tempfile.mkstemp(suffix=".json", prefix=f"jcsr2_{grupo[-6:]}_")
    with io.open(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False))
    return p


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(args):
    cid, sandbox_path, tag = args
    os.environ["BAS_ADOPTED_CONFIGS"] = sandbox_path
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    res = simulate_case(record(cid), now="f3-jcsr-t2")
    return {"tag": tag, "case_id": cid, "ok": res.ok, "mae": res.mae,
            "maxerr": res.maxerr, "sandbox": sandbox_path}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))

    r1 = json.loads(io.open(_ROOT / "New_Theory/f3_jcsr_result.json",
                            encoding="utf-8").read())

    tarefas, sboxes = [], []
    for cond, cc in COND.items():
        for cm in C_MULT:
            for tm in TC_MULT:
                for a in ALPHAS:
                    sb = _sandbox(cc["grupo"], cc["C_seed"] * cm,
                                  cc["tc_seed"] * tm, a)
                    sboxes.append(sb)
                    tarefas.append((cc["cid"], sb,
                                    f"{cond}|C={cm}|tc={tm}|a={a}"))
    print(f"[grade t2] {len(tarefas)} células", flush=True)
    res = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, t): t for t in tarefas}
        done = 0
        for fut in as_completed(futs):
            r = fut.result()
            res[r["tag"]] = r
            done += 1
            if done % 60 == 0 or done == len(tarefas):
                print(f"  [{done}/{len(tarefas)}]", flush=True)
    for sb in sboxes:
        try:
            os.unlink(sb)
        except OSError:
            pass

    def escore(r):
        if not r.get("ok") or r.get("mae") is None:
            return (9e9, 9e9)
        return (max(r["maxerr"] - 0.10, 0.0), r["mae"])

    melhores = dict(r1["melhores"])          # galv/plain_sea da t1 ficam
    for cond, cc in COND.items():
        cels = {t: r for t, r in res.items() if t.startswith(cond + "|")}
        bt = min(cels, key=lambda t: escore(cels[t]))
        b = cels[bt]
        mults = dict(p.split("=") for p in bt.split("|")[1:])
        melhores[cond] = dict(
            cid=cc["cid"], grupo=cc["grupo"],
            C_creep=cc["C_seed"] * float(mults["C"]),
            creep_t_c=cc["tc_seed"] * float(mults["tc"]),
            creep_alpha_sat=float(mults["a"]),
            mae=b["mae"], maxerr=b["maxerr"], base=r1["baseline"][cc["cid"]],
            tentativa=2, na_borda=(mults["tc"] == "6.0" or mults["a"] == "6.0"
                                   or mults["C"] in ("3.0",)))
        print(f"[{cond}] t2 -> {b['mae']:.4f}/{b['maxerr']:.4f} "
              f"(C={float(mults['C'])}x tc={float(mults['tc'])}x "
              f"a={mults['a']}; borda={melhores[cond]['na_borda']})",
              flush=True)

    tres = ["galv_seawater", "plain_seawater", "stainless_seawater"]
    ga_tres = all(melhores[c]["mae"] < 0.10 and melhores[c]["maxerr"] < 0.10
                  for c in tres)
    out_mae = melhores["outdoor"]["mae"] < 0.10
    out_tri = out_mae and melhores["outdoor"]["maxerr"] < 0.10
    import statistics
    med = statistics.median([m["mae"] for m in melhores.values()] + [0.0009])
    verdict = "PASS" if (ga_tres and out_mae and med < 0.08) else "FAIL"
    out = dict(prereg=r1["prereg"], secao="F3.1-JCSR tentativa 2",
               melhores=melhores,
               gate=dict(tres_seawater_tripe=ga_tres, outdoor_mae=out_mae,
                         outdoor_tripe_completo=out_tri, mediana=med),
               verdict=verdict)
    p = _ROOT / "New_Theory/f3_jcsr_result2.json"
    txt = json.dumps(out, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(p, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print(f"[gate] verdict={verdict} → {p}", flush=True)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
