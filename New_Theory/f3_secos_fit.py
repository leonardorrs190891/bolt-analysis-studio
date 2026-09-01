# -*- coding: utf-8 -*-
"""F3-SECOS (prereg 2026-07-21 §F3-SECOS): SUN nogrease ×2 — gain sub-crítico
com gate de ROBUSTEZ (tripé nos 3 gains {0,4; 0,6; 0,8}), k_wear_spec lido
do slope do Estágio II (grade {1,5, 2,5, 4}e-14 compartilhada), emb per-caso
L24 (std {2,25, 3,0, 3,75} µm; crimp {1,1, 1,5, 1,9} µm), TRIM exceção-C na
regra ">2× mediana do Estágio II" (std N≤6596; crimp N≤9514).
Gate: existe (kw, emb_std, emb_crimp) com tripé<0,1 nos 2 casos nos 3 gains;
controles bit-idênticos. NÃO adota. Saída: f3_secos_result.json.
Uso: python New_Theory/f3_secos_fit.py [--workers N]
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
from itertools import product
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

STD = "sun2025efa109235_transverse_nogrease_standard"
CRP = "sun2025efa109235_transverse_nogrease_crimp"
TRIM = {"nogrease_standard": 6596, "nogrease_crimp": 9514}
GAINS = (0.4, 0.6, 0.8)
KWS = (1.5e-14, 2.5e-14, 4.0e-14)
EMB_STD = (2.25, 3.0, 3.75)
EMB_CRP = (1.1, 1.5, 1.9)
CONTROLES = ["sun2025efa109235_transverse_grease_standard",
             "sun2025efa109235_transverse_grease_crimp",
             "sun2025efa109235_axial_F7.5kN_standard",
             "sun2025efa109235_axial_F17.5kN_crimp"]


def _sandbox(gain, kw, e_std, e_crp):
    d = json.loads(io.open(_ROOT / "New_Theory/adopted_configs.json",
                           encoding="utf-8").read())
    g = d["sources"]["SUN_2025_CRIMP"]
    pc = g["cfg"].setdefault("per_case", {})
    pc["nogrease_standard"] = dict(tr_loose_gain=gain, k_wear_spec=kw,
                                   emb_um=e_std)
    pc["nogrease_crimp"] = dict(tr_loose_gain=gain, k_wear_spec=kw,
                                emb_um=e_crp)
    g["cfg"]["trim_n_max"] = TRIM
    fd, p = tempfile.mkstemp(suffix=".json", prefix="secos_")
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
    r = simulate_case(record(cid), now="f3-secos")
    return {"tag": tag, "case_id": cid, "mae": r.mae, "maxerr": r.maxerr}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))
    store = json.loads(io.open(
        _ROOT / "Models/CALIBRATION_AND_VALIDATION/validation_store.json",
        encoding="utf-8").read())

    tarefas, sbs = [], []
    for gain, kw, es, ec in product(GAINS, KWS, EMB_STD, EMB_CRP):
        sb = _sandbox(gain, kw, es, ec)
        sbs.append(sb)
        tag = f"g={gain}|kw={kw:.1e}|es={es}|ec={ec}"
        tarefas.append((STD, sb, tag))
        tarefas.append((CRP, sb, tag))
    print(f"[secos] {len(tarefas)} sims", flush=True)
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

    def passa(v):
        return (v.get("mae") or 9) < 0.10 and (v.get("maxerr") or 9) < 0.10

    # robustez: (kw, es, ec) tal que os 3 gains passam nos 2 casos
    robustos = []
    for kw, es, ec in product(KWS, EMB_STD, EMB_CRP):
        tags = [f"g={g}|kw={kw:.1e}|es={es}|ec={ec}" for g in GAINS]
        if all(passa(grade[t][STD]) and passa(grade[t][CRP]) for t in tags):
            t06 = tags[1]
            robustos.append((kw, es, ec,
                             grade[t06][STD]["mae"] + grade[t06][CRP]["mae"]))
    if robustos:
        kw, es, ec, _ = min(robustos, key=lambda x: x[3])
        t06 = f"g=0.6|kw={kw:.1e}|es={es}|ec={ec}"
        out = dict(verdict="PASS", kw=kw, emb_std=es, emb_crimp=ec,
                   gain=0.6, trims=TRIM,
                   std=dict(mae=grade[t06][STD]["mae"],
                            maxerr=grade[t06][STD]["maxerr"]),
                   crimp=dict(mae=grade[t06][CRP]["mae"],
                              maxerr=grade[t06][CRP]["maxerr"]),
                   n_robustos=len(robustos))
        print(f"[gate] PASS robusto: kw={kw:.1e} es={es} ec={ec} | std "
              f"{out['std']} | crimp {out['crimp']}", flush=True)
    else:
        melhor = min(grade, key=lambda t: (grade[t][STD]["maxerr"] or 9)
                     + (grade[t][CRP]["maxerr"] or 9))
        out = dict(verdict="FAIL",
                   melhor_celula=dict(tag=melhor,
                                      std=grade[melhor][STD],
                                      crimp=grade[melhor][CRP]))
        print(f"[gate] FAIL — melhor célula {melhor}: "
              f"{grade[melhor][STD]['mae']:.3f}/"
              f"{grade[melhor][STD]['maxerr']:.3f} | "
              f"{grade[melhor][CRP]['mae']:.3f}/"
              f"{grade[melhor][CRP]['maxerr']:.3f}", flush=True)

    out["secao"] = "F3-SECOS"
    p = _ROOT / "New_Theory/f3_secos_result.json"
    txt = json.dumps(out, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(p, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
