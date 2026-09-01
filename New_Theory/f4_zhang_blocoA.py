# -*- coding: utf-8 -*-
"""F4 — zhang18/19 (13 casos restantes do bloco B) reavaliados como bloco A
per-rig (Junker transversais M12 com sobre-predição massiva, mesma natureza
do liu2020). Fase de busca em cap 2e4 (separação estabelecida cedo — idioma
T4) + full-res na célula vencedora. Grupos: ZHANG_2018 e ZHANG_2019
independentes; zhang18 tem tokens with/without locker (per_case gain).

Gate (F3-style): ≥10/13 tripé<0,1 no full-res; controles bit-idênticos;
senão documenta o resto (forma/fila). Saída: f4_zhang_result.json.
Uso: python New_Theory/f4_zhang_blocoA.py [--workers N]
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

Z18 = ["zhang18_fig2_test1_20kN_1e3cyc_preload_vs_cycles",
       "zhang18_fig2_test2_20kN_1e4cyc_preload_vs_cycles",
       "zhang18_fig2_test3_20kN_1e5cyc_preload_vs_cycles",
       "zhang18_fig2_test4_20kN_5e5cyc_preload_vs_cycles",
       "zhang18_fig13_14kN_preload_vs_cycles",
       "zhang18_fig13_20kN_preload_vs_cycles",
       "zhang18_fig13_26kN_preload_vs_cycles",
       "zhang18_fig16_with_locker_preload_vs_cycles",
       "zhang18_fig16_without_locker_preload_vs_cycles"]
Z19 = ["zhang19_fig4_1e3cyc_Test1to3_preload_vs_cycles",
       "zhang19_fig4_1e4cyc_Test4to6_preload_vs_cycles",
       "zhang19_fig4_1e5cyc_Test7to9_preload_vs_cycles",
       "zhang19_fig4_2e5cyc_Test10to12_preload_vs_cycles"]
CASOS = Z18 + Z19
EMB = [0.25, 1.0, 3.0]
KW = [1e-16, 1e-15, 5e-15]
GAIN = [0.1, 0.3, 0.6]
CAP = 20000
CONTROLES = ["liu2020_fig9_zinc_AF0.2mm_P0-18kN", "bauer2024_M8_fig6_rep1",
             "liu2025_M16_amp0p5", "zhang2006_fig16_runout_40kN_amp0p125"]


def _sandbox(emb, kw, gain):
    d = json.loads(io.open(_ROOT / "New_Theory/adopted_configs.json",
                           encoding="utf-8").read())
    for grp in ("ZHANG_2018", "ZHANG_2019"):
        g = d["sources"].setdefault(grp, {"pack": "", "cfg": {}})
        g["pack"] = g.get("pack") or ""
        g["cfg"] = dict(g.get("cfg", {}), emb_um=float(emb),
                        k_wear_spec=float(kw), tr_loose_gain=float(gain))
    fd, p = tempfile.mkstemp(suffix=".json", prefix="zh_")
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
    r = simulate_case(record(cid), n_cap=cap, now="f4-zhang")
    return {"tag": tag, "case_id": cid, "mae": r.mae, "maxerr": r.maxerr}


def _roda(tarefas, workers):
    out = {}
    with ProcessPoolExecutor(max_workers=workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, t): t for t in tarefas}
        done = 0
        for fut in as_completed(futs):
            r = fut.result()
            out.setdefault(r["tag"], {})[r["case_id"]] = r
            done += 1
            if done % 80 == 0 or done == len(tarefas):
                print(f"  [{done}/{len(tarefas)}]", flush=True)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))
    store = json.loads(io.open(
        _ROOT / "Models/CALIBRATION_AND_VALIDATION/validation_store.json",
        encoding="utf-8").read())
    import statistics

    tarefas, sbs = [], []
    for emb, kw, gain in product(EMB, KW, GAIN):
        sb = _sandbox(emb, kw, gain)
        sbs.append(sb)
        tag = f"e={emb}|kw={kw:.0e}|g={gain}"
        tarefas += [(c, sb, tag, CAP) for c in CASOS]
    print(f"[busca] {len(tarefas)} sims @cap {CAP}", flush=True)
    g1 = _roda(tarefas, args.workers)
    for sb in sbs:
        try:
            os.unlink(sb)
        except OSError:
            pass

    def escore(g):
        piores = [max((v.get("mae") or 9) - 0.10, 0,
                      (v.get("maxerr") or 9) - 0.10) for v in g.values()]
        return (sum(1 for x in piores if x > 0),
                statistics.median((v.get("mae") or 9) for v in g.values()))

    best = min(g1, key=lambda t: escore(g1[t]))
    print(f"[busca] melhor {best}: {escore(g1[best])}", flush=True)

    p = best.split("|")
    sbv = _sandbox(float(p[0].split("=")[1]), float(p[1].split("=")[1]),
                   float(p[2].split("=")[1]))
    tarefas = [(c, sbv, "FULL", None) for c in CASOS] + \
              [(c, sbv, "ctrl", None) for c in CONTROLES]
    print(f"[full] {len(tarefas)} sims full-res", flush=True)
    g2 = _roda(tarefas, args.workers)
    os.unlink(sbv)

    full = g2["FULL"]
    n_pass = sum(1 for c in CASOS if (full[c].get("mae") or 9) < 0.10
                 and (full[c].get("maxerr") or 9) < 0.10)
    ctrl_ok = all(g2["ctrl"][c]["mae"] == store[c]["mae"] for c in CONTROLES)
    for c in CASOS:
        v = full[c]
        print(f"   {c[8:40]:32s} {store[c]['mae']:.3f}->{v['mae']:.3f} / "
              f"{store[c]['maxerr']:.3f}->{v['maxerr']:.3f}", flush=True)
    verdict = "PASS" if (n_pass >= 10 and ctrl_ok) else (
        "PASS-parcial" if n_pass >= 7 else "FAIL")
    out = dict(secao="F4 zhang18/19 bloco A per-rig", melhor=best,
               n_pass=n_pass,
               tripe={c: dict(mae=full[c].get("mae"),
                              maxerr=full[c].get("maxerr")) for c in CASOS},
               controles=ctrl_ok, verdict=verdict)
    pth = _ROOT / "New_Theory/f4_zhang_result.json"
    txt = json.dumps(out, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(pth, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print(f"[gate] {verdict} ({n_pass}/13; ctrl={ctrl_ok}) → {pth}",
          flush=True)
    return 0 if verdict.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
