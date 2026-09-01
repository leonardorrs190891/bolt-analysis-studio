# -*- coding: utf-8 -*-
"""F4 — G4-b do prereg B1-v3: os 9 casos R5 do liu2020 (axial, coatings
zinc/DLC) com o flank v2 per-rig. µ por coating = INPUT do KB
(mu_thread_anchor: zinc 0,150 / DLC 0,126). Fit per-rig (k, s_crit/s_ref)
partindo dos vencedores do G4-a; exp=1,5 herdado. Gate: ≥6/9 tripé<0,1.
G4-c embutido: 4 controles bit-idênticos (cfg não muda p/ eles).

Uso (worktree): python New_Theory/f4_g4b_liu2020.py [--workers N]
Saída: New_Theory/f4_g4b_result.json
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

CASOS = ["liu2020_fig5b_zinc_P0-12kN_AF0.2mm", "liu2020_fig5b_zinc_P0-18kN_AF0.2mm",
         "liu2020_fig5b_zinc_P0-24kN_AF0.2mm", "liu2020_fig9_zinc_AF0.1mm_P0-18kN",
         "liu2020_fig9_zinc_AF0.2mm_P0-18kN", "liu2020_fig9_zinc_AF0.3mm_P0-18kN",
         "liu2020_fig9_zinc_AF0.4mm_P0-18kN", "liu2020_fig15_DLC_P0-18kN_AF0.2mm",
         "liu2020_fig15_DLC_P0-19.28kN_AF0.2mm"]
MU = {"zinc": 0.150, "DLC": 0.126}          # KB mu_thread_anchor (input)
K_GRID = [3.16e-15, 1.0e-14, 3.16e-14, 1.0e-13]
FR_GRID = [0.0, 0.4, 0.6, 0.75, 0.9]
CONTROLES = ["liu2017_axial_AF_7p5kN", "li2022ti_axialmin_15Hz",
             "liu2016wear_fig9a_m30nm", "bauer2024_M8_fig6_rep1"]


def _grupo_de(cid):
    return "LIU_2020_WEAR"


def _sandbox(k, fr_zinc_sc, s_ref):
    d = json.loads(io.open(_ROOT / "New_Theory/adopted_configs.json",
                           encoding="utf-8").read())
    g = d["sources"].setdefault("LIU_2020_WEAR", {"pack": "", "cfg": {}})
    g.setdefault("pack", "")
    g["cfg"].update(flank_wear_on=1.0, k_wear_flank=float(k),
                    flank_s_crit=float(fr_zinc_sc * s_ref),
                    flank_amp_exp=1.5)
    pc = g["cfg"].setdefault("per_case", {})
    pc["zinc"] = {"mu_thread": MU["zinc"]}
    pc["dlc"] = {"mu_thread": MU["DLC"]}
    fd, p = tempfile.mkstemp(suffix=".json", prefix="g4b_")
    with io.open(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False))
    return p


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(args):
    cid, sb, tag = args
    if sb:
        os.environ["BAS_ADOPTED_CONFIGS"] = sb
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    r = simulate_case(record(cid), now="f4-g4b")
    return {"tag": tag, "case_id": cid, "mae": r.mae, "maxerr": r.maxerr,
            "ok": r.ok, "err": r.error}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))

    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.inputs import (geometry_for_case,
                                                        inputs_for)
    rec0 = record(CASOS[0])
    inp0 = inputs_for(rec0.validation_case)
    geom0 = geometry_for_case(rec0.validation_case,
                              grip_mm=inp0["grip_mm"]["value"],
                              E=(inp0.get("E") or {}).get("value"))
    # s_ref do rig liu2020: A_F típico 10 kN? o rig varre A_F 0,1-0,4 mm em
    # FORÇA? liu2020 é axial em kN — usar A_F=18e3*0,2?? NÃO: os stems dão
    # AF em mm?! Ver _axial_f_amp: sun/liu2016 usam af..kn; liu2020 usa
    # AF0.2mm no stem — o F_amp axial vem da tabela curada? Medir do runner:
    from bolt_analysis_studio.validation.runner import _loading_for
    load0 = _loading_for(rec0)
    f_amp0 = load0["F_amp_N"]
    s_ref = max(f_amp0, 1.0) / geom0.k_b
    print(f"[g4b] F_amp(caso0)={f_amp0} s_ref={s_ref:.3e} k_b={geom0.k_b:.3e}",
          flush=True)

    store = json.loads(io.open(
        _ROOT / "Models/CALIBRATION_AND_VALIDATION/validation_store.json",
        encoding="utf-8").read())

    tarefas, sbs = [], []
    for k in K_GRID:
        for fr in FR_GRID:
            sb = _sandbox(k, fr, s_ref)
            sbs.append(sb)
            tag = f"k={k:.2e}|fr={fr}"
            for cid in CASOS:
                tarefas.append((cid, sb, tag))
    print(f"[g4b] {len(tarefas)} sims", flush=True)
    grade = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, t): t for t in tarefas}
        done = 0
        for fut in as_completed(futs):
            r = fut.result()
            grade.setdefault(r["tag"], {})[r["case_id"]] = r
            done += 1
            if done % 45 == 0 or done == len(tarefas):
                print(f"  [{done}/{len(tarefas)}]", flush=True)
    for sb in sbs:
        try:
            os.unlink(sb)
        except OSError:
            pass

    def n_pass(g):
        return sum(1 for c in CASOS
                   if (g[c].get("mae") or 9) < 0.10
                   and (g[c].get("maxerr") or 9) < 0.10)

    import statistics
    best = max(grade, key=lambda t: (n_pass(grade[t]), -statistics.median(
        (grade[t][c]["mae"] or 9) for c in CASOS)))
    nb = n_pass(grade[best])
    med = statistics.median((grade[best][c]["mae"] or 9) for c in CASOS)
    print(f"[g4b] melhor {best}: {nb}/9 tripé, mediana {med:.4f}", flush=True)

    # G4-c: controles com o sandbox VENCEDOR (cfg deles não muda → idêntico)
    k = float(best.split("|")[0].split("=")[1])
    fr = float(best.split("|")[1].split("=")[1])
    sbv = _sandbox(k, fr, s_ref)
    ctrl = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, (c, sbv, "ctrl")): c for c in CONTROLES}
        for fut in as_completed(futs):
            r = fut.result()
            ctrl[r["case_id"]] = r
    os.unlink(sbv)
    ctrl_ok = all(ctrl[c]["mae"] == store[c]["mae"] for c in CONTROLES)

    verdict = "PASS" if (nb >= 6 and ctrl_ok) else "FAIL"
    out = dict(prereg="docs/superpowers/specs/2026-07-22-f4-l1v2-prereg-b1v3.md",
               s_ref=s_ref, mu_kb=MU, melhor=best, n_pass=nb, mediana=med,
               tripe={c: dict(mae=grade[best][c].get("mae"),
                              maxerr=grade[best][c].get("maxerr"))
                      for c in CASOS},
               baseline={c: dict(mae=store[c]["mae"], maxerr=store[c]["maxerr"])
                         for c in CASOS},
               G4c_controles=ctrl_ok, verdict=verdict)
    p = _ROOT / "New_Theory/f4_g4b_result.json"
    txt = json.dumps(out, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(p, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print(f"[gate] G4-b {verdict} ({nb}/9; ctrl={ctrl_ok}) → {p}", flush=True)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
