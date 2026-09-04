# -*- coding: utf-8 -*-
"""F3-LOTE2 (prereg 2026-07-21-master-f3-preregs.md §L2a-d): 4 sub-preregs de
nível/leitura em grade, cada um com sandbox e gate próprios. NÃO adota.

L2a ZHANG fig16: C_creep relido do platô. L2b âncora interna: emb lido + ratchet.
L2c SUN grease_crimp: k_wear_spec lido. L2d SUN axial standard: C_creep token.
Saída: New_Theory/f3_lote2_result.json
Uso: python New_Theory/f3_lote2_fit.py [--workers N]
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


def _mk(dcfg):
    fd, p = tempfile.mkstemp(suffix=".json", prefix="lote2_")
    with io.open(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(dcfg, ensure_ascii=False))
    return p


def _base():
    return json.loads(io.open(_ROOT / "New_Theory/adopted_configs.json",
                              encoding="utf-8").read())


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(args):
    cid, sb, tag = args
    os.environ["BAS_ADOPTED_CONFIGS"] = sb
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    r = simulate_case(record(cid), now="f3-lote2")
    return {"tag": tag, "case_id": cid, "mae": r.mae, "maxerr": r.maxerr,
            "ok": r.ok}


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

    # --- L2a ZHANG fig16 ---
    for C in (0.5e-11, 0.77e-11, 1.0e-11, 1.3e-11):
        d = _base()
        d["sources"]["ZHANG_2006"]["cfg"]["C_creep"] = C
        sb = _mk(d)
        sbs.append(sb)
        for cid in ("zhang2006_fig16_runout_40kN_amp0p125",
                    "zhang2006_fig3_illus_M12x125_20kN_amp0p35"):
            tarefas.append((cid, sb, f"L2a|C={C:.2e}"))

    # --- L2b âncora interna (5A: emb; 13A_first: emb×ratchet; 13A_def gate) ---
    for e5 in (0.0, 0.5, 1.0):
        for e13 in (0.0, 1.0, 2.0):
            for kr in (0.0, 3e-5, 1e-4):
                d = _base()
                d["sources"]["ancora_interna"]["cfg"]["emb_um"] = e5
                g13 = d["sources"]["ancora_interna"]["cfg"]
                g13["emb_um"] = e13
                if kr:
                    g13["k_ratchet"] = kr
                sb = _mk(d)
                sbs.append(sb)
                tag = f"L2b|e5={e5}|e13={e13}|kr={kr:.0e}"
                for cid in ("ancora_interna",
                            "ancora_interna",
                            "ancora_interna"):
                    tarefas.append((cid, sb, tag))

    # --- L2c SUN grease_crimp: k_wear_spec per_case ---
    for kw in (1.5e-15, 2.2e-15, 2.9e-15, 4.2e-15, 6.0e-15):
        d = _base()
        pc = d["sources"]["SUN_2025_CRIMP"]["cfg"]["per_case"]
        pc["_grease_crimp"]["k_wear_spec"] = kw
        sb = _mk(d)
        sbs.append(sb)
        for cid in ("sun2025efa109235_transverse_grease_crimp",
                    "sun2025efa109235_transverse_grease_standard"):
            tarefas.append((cid, sb, f"L2c|kw={kw:.2e}"))

    # --- L2d SUN axial standard: C_creep per_case token ---
    for C in (3.3e-11, 4.7e-11, 6.5e-11, 9.0e-11):
        d = _base()
        pc = d["sources"]["SUN_2025_CRIMP"]["cfg"]["per_case"]
        pc["axial_f7.5kn_standard"] = {"C_creep": C}
        pc["axial_f17.5kn_standard"] = {"C_creep": C}
        sb = _mk(d)
        sbs.append(sb)
        for cid in ("sun2025efa109235_axial_F7.5kN_standard",
                    "sun2025efa109235_axial_F17.5kN_standard",
                    "sun2025efa109235_axial_F7.5kN_crimp"):
            tarefas.append((cid, sb, f"L2d|C={C:.2e}"))

    print(f"[lote2] {len(tarefas)} sims", flush=True)
    grade = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, t): t for t in tarefas}
        done = 0
        for fut in as_completed(futs):
            r = fut.result()
            grade.setdefault(r["tag"], {})[r["case_id"]] = r
            done += 1
            if done % 40 == 0 or done == len(tarefas):
                print(f"  [{done}/{len(tarefas)}]", flush=True)
    for sb in sbs:
        try:
            os.unlink(sb)
        except OSError:
            pass

    def tri(v):
        return (v.get("mae") or 9, v.get("maxerr") or 9)

    def passa(v):
        m, x = tri(v)
        return m < 0.10 and x < 0.10

    out = {}
    # L2a
    fig16 = "zhang2006_fig16_runout_40kN_amp0p125"
    fig3 = "zhang2006_fig3_illus_M12x125_20kN_amp0p35"
    cands = {t: g for t, g in grade.items() if t.startswith("L2a")
             and passa(g[fig16]) and tri(g[fig3])[0] <= store[fig3]["mae"] + 0.005}
    if cands:
        best = min(cands, key=lambda t: tri(cands[t][fig16])[0])
        out["L2a"] = dict(verdict="PASS", C=float(best.split("=")[1]),
                          fig16=dict(zip(("mae", "maxerr"),
                                         tri(cands[best][fig16]))),
                          fig3_mae=tri(cands[best][fig3])[0])
    else:
        melhor = min((t for t in grade if t.startswith("L2a")),
                     key=lambda t: tri(grade[t][fig16])[1])
        out["L2a"] = dict(verdict="FAIL", detalhe={
            t: dict(fig16=tri(g[fig16]), fig3=tri(g[fig3]))
            for t, g in grade.items() if t.startswith("L2a")})
    # L2b
    u5, u13, udef = ("ancora_interna", "ancora_interna",
                     "ancora_interna")
    cands = {t: g for t, g in grade.items() if t.startswith("L2b")
             and passa(g[u5]) and passa(g[u13])
             and tri(g[udef])[0] <= store[udef]["mae"] + 0.005
             and tri(g[udef])[1] < 0.10}
    if cands:
        best = min(cands, key=lambda t: tri(cands[t][u13])[0] + tri(cands[t][u5])[0])
        out["L2b"] = dict(verdict="PASS", tag=best,
                          **{c: dict(zip(("mae", "maxerr"), tri(cands[best][c])))
                             for c in (u5, u13, udef)})
    else:
        out["L2b"] = dict(verdict="FAIL", detalhe={
            t: {c: tri(g.get(c) or {}) for c in (u5, u13, udef)}
            for t, g in grade.items() if t.startswith("L2b")})
    # L2c
    gc, gs = ("sun2025efa109235_transverse_grease_crimp",
              "sun2025efa109235_transverse_grease_standard")
    cands = {t: g for t, g in grade.items() if t.startswith("L2c")
             and passa(g[gc]) and tri(g[gs])[0] <= store[gs]["mae"] + 0.005}
    if cands:
        best = min(cands, key=lambda t: tri(cands[t][gc])[1])
        out["L2c"] = dict(verdict="PASS", kw=float(best.split("=")[1]),
                          crimp=dict(zip(("mae", "maxerr"), tri(cands[best][gc]))))
    else:
        out["L2c"] = dict(verdict="FAIL", detalhe={
            t: tri(g[gc]) for t, g in grade.items() if t.startswith("L2c")})
    # L2d
    a75, a175, a75c = ("sun2025efa109235_axial_F7.5kN_standard",
                       "sun2025efa109235_axial_F17.5kN_standard",
                       "sun2025efa109235_axial_F7.5kN_crimp")
    cands = {t: g for t, g in grade.items() if t.startswith("L2d")
             and passa(g[a75]) and passa(g[a175])
             and tri(g[a75c])[0] == store[a75c]["mae"]}
    if cands:
        best = min(cands, key=lambda t: tri(cands[t][a175])[0])
        out["L2d"] = dict(verdict="PASS", C=float(best.split("=")[1]),
                          f75=dict(zip(("mae", "maxerr"), tri(cands[best][a75]))),
                          f175=dict(zip(("mae", "maxerr"), tri(cands[best][a175]))))
    else:
        out["L2d"] = dict(verdict="FAIL", detalhe={
            t: dict(f75=tri(g[a75]), f175=tri(g[a175]),
                    crimp_ctrl=tri(g[a75c]))
            for t, g in grade.items() if t.startswith("L2d")})

    p = _ROOT / "New_Theory/f3_lote2_result.json"
    txt = json.dumps(out, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(p, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print(json.dumps({k: v["verdict"] for k, v in out.items()}), flush=True)
    print(f"→ {p}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
