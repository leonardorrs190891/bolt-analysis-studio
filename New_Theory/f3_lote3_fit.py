# -*- coding: utf-8 -*-
"""F3-LOTE3: (a) UFU_5A tentativa-2 (N_emb×emb, gate 13A_def);
(e) li2022ti_full trim pela regra >3× mediana do estágio II (changepoint
computado do CSV, auditável); (d) LIU_2016 fig7 sonda per-figura (2 células,
casos de 1e6/5e6 ciclos — caras). NÃO adota. Saída: f3_lote3_result.json.
Uso: python New_Theory/f3_lote3_fit.py [--workers N]
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
    fd, p = tempfile.mkstemp(suffix=".json", prefix="lote3_")
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
    r = simulate_case(record(cid), now="f3-lote3")
    return {"tag": tag, "case_id": cid, "mae": r.mae, "maxerr": r.maxerr,
            "ok": r.ok, "err": r.error}


def changepoint_li2022(sys_path_ok=True):
    """Regra >3x mediana do estágio II, contígua até o fim (mesma da
    LIU_2025), aplicada ao CSV do li2022ti full."""
    import numpy as np
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.inputs import (load_full_curve,
                                                        repo_root)
    rec = record("li2022ti_axial_10Hz_full")
    rel = rec.csv_path.relative_to(repo_root()).as_posix()
    cyc, rr = load_full_curve(rel)
    rr = rr / max(rr[0], 1e-9)
    dr = np.abs(np.diff(rr) / np.maximum(np.diff(cyc), 1e-9))
    n = len(dr)
    med = np.median(dr[n // 4: 3 * n // 4])          # estágio II central
    lim = 3.0 * max(med, 1e-12)
    idx = n
    for i in range(n - 1, -1, -1):
        if dr[i] > lim:
            idx = i
        else:
            break
    trim = float(cyc[idx]) if idx < n else None
    return trim, float(med), float(cyc[-1])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))
    store = json.loads(io.open(
        _ROOT / "Models/CALIBRATION_AND_VALIDATION/validation_store.json",
        encoding="utf-8").read())

    trim_li, med, fim = changepoint_li2022()
    print(f"[e] li2022ti_full changepoint: trim={trim_li} (mediana estágio "
          f"II={med:.3e}, fim={fim})", flush=True)

    tarefas, sbs = [], []
    # (a) UFU_5A t2
    for ne in (150.0, 300.0, 600.0):
        for e5 in (0.5, 1.0):
            d = _base()
            g = d["sources"]["UFU_LAB_5A"]["cfg"]
            g["emb_um"] = e5
            g["N_emb"] = ne
            sb = _mk(d)
            sbs.append(sb)
            tag = f"a|ne={ne:.0f}|e5={e5}"
            for cid in ("UFU_5A_preload_decay", "UFU_13A_def_preload_decay"):
                tarefas.append((cid, sb, tag))
    # (e) li2022ti full trim
    if trim_li:
        d = _base()
        g = d["sources"]["LI_2022_TRIBOINT"]["cfg"]
        g["trim_n_max"] = {"full": trim_li}
        sb = _mk(d)
        sbs.append(sb)
        tarefas.append(("li2022ti_axial_10Hz_full", sb, "e|trim"))
        tarefas.append(("li2022ti_axialmin_10Hz", sb, "e|trim"))
    # (d) LIU_2016 fig7 sonda: grupo per-figura com C_creep reduzido
    for cm in (0.7, 0.85):
        d = _base()
        base_liu16 = dict(d["sources"].get("LIU_2016", {}).get("cfg", {}))
        base_liu16["C_creep"] = 1.867e-11 * cm
        d["sources"]["LIU_2016_fig7"] = {"pack": "PACK", "cfg": base_liu16}
        sb = _mk(d)
        sbs.append(sb)
        tarefas.append(("liu2016wear_fig7_run2_5e6cyc", sb, f"d|cm={cm}"))
        tarefas.append(("liu2016wear_fig7_run1_1e6cyc", sb, f"d|cm={cm}"))

    print(f"[lote3] {len(tarefas)} sims (fig7 5e6 é o teto)", flush=True)
    grade = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, t): t for t in tarefas}
        done = 0
        for fut in as_completed(futs):
            r = fut.result()
            grade.setdefault(r["tag"], {})[r["case_id"]] = r
            done += 1
            print(f"  [{done}/{len(tarefas)}] {r['tag']} "
                  f"{r['case_id'][-18:]} mae={r['mae'] and round(r['mae'], 3)}"
                  f" mx={r['maxerr'] and round(r['maxerr'], 3)}", flush=True)
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

    out = {"changepoint_li2022": dict(trim=trim_li, mediana=med)}
    u5, udef = "UFU_5A_preload_decay", "UFU_13A_def_preload_decay"
    ca = {t: g for t, g in grade.items() if t.startswith("a|")
          and passa(g[u5]) and tri(g[udef])[0] <= store[udef]["mae"] + 0.005
          and tri(g[udef])[1] < 0.10}
    out["a_UFU5A"] = (dict(verdict="PASS",
                           tag=min(ca, key=lambda t: tri(ca[t][u5])[1]),
                           detalhe={t: tri(g[u5]) for t, g in ca.items()})
                      if ca else
                      dict(verdict="FAIL2",
                           detalhe={t: dict(u5=tri(g[u5]), udef=tri(g[udef]))
                                    for t, g in grade.items()
                                    if t.startswith("a|")}))
    ge = grade.get("e|trim") or {}
    full = ge.get("li2022ti_axial_10Hz_full") or {}
    ctrl = ge.get("li2022ti_axialmin_10Hz") or {}
    ctrl_ok = ctrl.get("mae") == store["li2022ti_axialmin_10Hz"]["mae"]
    out["e_li2022full"] = dict(
        verdict="PASS" if (passa(full) and ctrl_ok) else "FAIL",
        full=tri(full), controle_intacto=ctrl_ok)
    r2, r1 = "liu2016wear_fig7_run2_5e6cyc", "liu2016wear_fig7_run1_1e6cyc"
    cd = {t: g for t, g in grade.items() if t.startswith("d|")
          and passa(g[r2]) and tri(g[r1])[0] <= store[r1]["mae"] + 0.005
          and tri(g[r1])[1] < 0.10}
    out["d_liu2016fig7"] = (dict(verdict="PASS",
                                 tag=min(cd, key=lambda t: tri(cd[t][r2])[1]),
                                 detalhe={t: dict(r2=tri(g[r2]), r1=tri(g[r1]))
                                          for t, g in grade.items()
                                          if t.startswith("d|")})
                            if cd else
                            dict(verdict="FAIL",
                                 detalhe={t: dict(r2=tri(g[r2]), r1=tri(g[r1]))
                                          for t, g in grade.items()
                                          if t.startswith("d|")}))
    p = _ROOT / "New_Theory/f3_lote3_result.json"
    txt = json.dumps(out, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(p, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print(json.dumps({k: (v.get("verdict") if isinstance(v, dict) else v)
                      for k, v in out.items() if k != "changepoint_li2022"}),
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
