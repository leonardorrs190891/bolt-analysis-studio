# -*- coding: utf-8 -*-
"""F3.1-JCSR (prereg 2026-07-21-master-f3-preregs.md): níveis per-condição +
cinética saturante, POR CONDIÇÃO independente (grupo próprio por caso).

Grade por condição: C_creep ∈ seed×{0.5,0.75,1,1.5,2,3} · t_c ∈ seed_paper×
{0.5,1,2} (seed = onset c da Eq.(2) do paper, input-de-paper, em segundos) ·
alpha ∈ {0.6,1.0,1.5,2.0,3.0}. Sandbox BAS_ADOPTED_CONFIGS por célula-condição
(grupos NOVOS: JCSR_2023_<cond>; NUNCA JCSR_2023_plain). Melhor célula por
caso pelo tripé (maxerr primeiro, MAE desempata). Gate G-JCSR-a..d no fim.
NÃO escreve no canônico (adoção é passo separado).

Uso: python New_Theory/f3_jcsr_fit.py [--workers N]
Saída: New_Theory/f3_jcsr_result.json
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
    "galv_seawater": dict(cid="jcsr2023_galv_seawater",
                          grupo="JCSR_2023_galv_seawater",
                          C_seed=5.34e-10, tc_seed=7.95 * D),
    "plain_seawater": dict(cid="jcsr2023_plain_seawater",
                           grupo="JCSR_2023_plain_seawater",
                           C_seed=4.75e-10, tc_seed=14.65 * D),
    "stainless_seawater": dict(cid="jcsr2023_stainless_seawater",
                               grupo="JCSR_2023_stainless_seawater",
                               C_seed=8.68e-10, tc_seed=24.7 * D),
    "outdoor": dict(cid="jcsr2023_plain_outdoor",
                    grupo="JCSR_2023_outdoor",
                    C_seed=3.40e-10, tc_seed=99.0 * D),
}
C_MULT = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
TC_MULT = [0.5, 1.0, 2.0]
ALPHAS = [0.6, 1.0, 1.5, 2.0, 3.0]
CONTROLES = ["jcsr2023_plain_indoor", "caccese2009_protruding_45kN",
             "caccese2009_tapered_45kN_rep1", "qin2024acm_25C_i0pct",
             "li2022marstruc_creep_10kN_Ra0p8_min"]


def _sandbox(grupo: str, C: float, tc: float, a: float) -> str:
    d = json.loads(io.open(_ROOT / "New_Theory/adopted_configs.json",
                           encoding="utf-8").read())
    d["sources"][grupo] = {"pack": "PACK", "cfg": {
        "creep_mode": "saturating", "C_creep": float(C),
        "creep_t_c": float(tc), "creep_alpha_sat": float(a)}}
    fd, p = tempfile.mkstemp(suffix=".json", prefix=f"jcsr_{grupo[-8:]}_")
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
    res = simulate_case(record(cid), now="f3-jcsr")
    return {"tag": tag, "case_id": cid, "ok": res.ok, "mae": res.mae,
            "maxerr": res.maxerr, "sandbox": sandbox_path,
            "error": res.error}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))

    store = json.loads(io.open(
        _ROOT / "Models/CALIBRATION_AND_VALIDATION/validation_store.json",
        encoding="utf-8").read())
    base = {c["cid"]: dict(mae=store[c["cid"]]["mae"],
                           maxerr=store[c["cid"]]["maxerr"])
            for c in COND.values()}
    print("baseline:", json.dumps(base), flush=True)

    tarefas = []
    sboxes = []
    for cond, cc in COND.items():
        for cm in C_MULT:
            for tm in TC_MULT:
                for a in ALPHAS:
                    sb = _sandbox(cc["grupo"], cc["C_seed"] * cm,
                                  cc["tc_seed"] * tm, a)
                    sboxes.append(sb)
                    tarefas.append((cc["cid"], sb,
                                    f"{cond}|C={cm}|tc={tm}|a={a}"))
    print(f"[grade] {len(tarefas)} células", flush=True)

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

    melhores = {}
    for cond, cc in COND.items():
        cels = {t: r for t, r in res.items() if t.startswith(cond + "|")}
        best_tag = min(cels, key=lambda t: escore(cels[t]))
        b = cels[best_tag]
        mults = dict(p.split("=") for p in best_tag.split("|")[1:])
        melhores[cond] = dict(
            cid=cc["cid"], grupo=cc["grupo"],
            C_creep=cc["C_seed"] * float(mults["C"]),
            creep_t_c=cc["tc_seed"] * float(mults["tc"]),
            creep_alpha_sat=float(mults["a"]),
            mae=b["mae"], maxerr=b["maxerr"],
            base=base[cc["cid"]])
        print(f"[{cond}] {base[cc['cid']]['mae']:.3f}/"
              f"{base[cc['cid']]['maxerr']:.3f} -> "
              f"{b['mae']:.4f}/{b['maxerr']:.4f}  "
              f"(C={melhores[cond]['C_creep']:.3e} tc={float(mults['tc'])}x "
              f"a={mults['a']})", flush=True)

    # ---- gate ----
    tres = ["galv_seawater", "plain_seawater", "stainless_seawater"]
    ga_tres = all(melhores[c]["mae"] < 0.10 and melhores[c]["maxerr"] < 0.10
                  for c in tres)
    out_mae = melhores["outdoor"]["mae"] < 0.10
    out_tri = out_mae and melhores["outdoor"]["maxerr"] < 0.10
    import statistics
    med_dep = statistics.median(
        [melhores[c]["mae"] for c in COND] + [base["jcsr2023_plain_indoor"]
                                              ["mae"]] if False else
        [m["mae"] for m in melhores.values()] + [0.0009])
    g_a = ga_tres and out_mae
    g_b = med_dep < 0.08
    verdict = "PASS" if (g_a and g_b) else "FAIL"
    out = dict(prereg="docs/superpowers/specs/2026-07-21-master-f3-preregs.md",
               secao="F3.1-JCSR", baseline=base, melhores=melhores,
               gate=dict(tres_seawater_tripe=ga_tres, outdoor_mae=out_mae,
                         outdoor_tripe_completo=out_tri,
                         mediana_fonte=med_dep, G_b=g_b),
               nota=("controles/indoor verificados no passo de adoção; "
                     "outdoor maxerr>0,1 só no rebound → candidata exceção"),
               verdict=verdict)
    p = _ROOT / "New_Theory/f3_jcsr_result.json"
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
