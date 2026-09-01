# -*- coding: utf-8 -*-
"""F3-YANG_2021 (prereg no ledger 2026-07-21): leitura pura — SEM grade.

emb_um = 3,85 µm no trio amp0p5/0p6/0p7 (INPUT-DE-PAPER: "material loosening
≈ 10% de F0", p.5 do paper; ΔF=0,10·F0 ⇒ emb = 0,10·F0/k_b ≈ 3,85 µm no grip
vigente) via dict PR-27 + trim_n_max (N2/45° do paper, regra taxa>8×mediana):
fig2@5850, amp1p0@3150, amp0p8@5450, amp0p6@11800, amp0p7@14000, amp0p5@27000.

Gates: trio + amp1p0 tripé<0,1; amp0p8/fig2 melhoram mas ficam fila (canal
estrutural confundido — item 2); grupo A (fig2/amp0p8/amp1p0 usam emb 11 µm
default) MAE não piora >0,005. Contingência amp0p5: +N_emb lido (N1/3).
Uso: python New_Theory/f3_yang2021_fit.py [--workers N]
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

EMB_TRIO = {"amp0p5": 3.85, "amp0p6": 3.85, "amp0p7": 3.85}
TRIMS = {"fig2": 5850, "amp1p0": 3150, "amp0p8": 5450,
         "amp0p6": 11800, "amp0p7": 14000, "amp0p5": 27000}
CASOS = ["yang2021_amp0p5mm_ax8kN", "yang2021_amp0p6mm_ax8kN_r1",
         "yang2021_amp0p7mm_ax11p2kN", "yang2021_amp1p0mm_ax2kN",
         "yang2021_amp0p8mm_ax6kN", "yang2021_fig2_typical"]
TRIO = CASOS[:3]


def _sandbox(n_emb=None):
    d = json.loads(io.open(_ROOT / "New_Theory/adopted_configs.json",
                           encoding="utf-8").read())
    g = d["sources"].setdefault("YANG_2021", {"pack": "PACK", "cfg": {}})
    g["cfg"]["emb_um"] = EMB_TRIO
    g["cfg"]["trim_n_max"] = TRIMS
    if n_emb is not None:
        g["cfg"]["per_case"] = {"amp0p5": {"N_emb": float(n_emb)}}
    fd, p = tempfile.mkstemp(suffix=".json", prefix="y21_")
    with io.open(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False))
    return p


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(args):
    cid, sb = args
    os.environ["BAS_ADOPTED_CONFIGS"] = sb
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    r = simulate_case(record(cid), now="f3-y21")
    return {"case_id": cid, "ok": r.ok, "mae": r.mae, "maxerr": r.maxerr}


def _roda(sb, casos, workers):
    out = {}
    with ProcessPoolExecutor(max_workers=workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, (c, sb)): c for c in casos}
        for fut in as_completed(futs):
            r = fut.result()
            out[r["case_id"]] = r
            print(f"  {r['case_id'][:34]:34s} mae="
                  f"{r['mae'] and round(r['mae'], 4)} mx="
                  f"{r['maxerr'] and round(r['maxerr'], 4)}", flush=True)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))

    sb = _sandbox()
    print("[t1] leitura pura (emb-paper + trims)", flush=True)
    r1 = _roda(sb, CASOS, args.workers)
    os.unlink(sb)

    def passa(r):
        return (r.get("mae") or 9) < 0.10 and (r.get("maxerr") or 9) < 0.10

    tent = 1
    fin = r1
    if not passa(r1[TRIO[0]]):
        print("[t2] contingência N_emb lido no amp0p5", flush=True)
        # N1 ≈ ciclo em que o dado cruza 0,90 (diagnóstico: N_emb=N1/3);
        # N1~2400 p/ amp0p5 => N_emb ~800
        sb2 = _sandbox(n_emb=800.0)
        r2 = _roda(sb2, [TRIO[0]], args.workers)
        os.unlink(sb2)
        if passa(r2[TRIO[0]]):
            fin = dict(r1)
            fin[TRIO[0]] = r2[TRIO[0]]
            tent = 2

    alvo_ok = all(passa(fin[c]) for c in TRIO + ["yang2021_amp1p0mm_ax2kN"])
    verdict = "PASS" if alvo_ok else "FAIL"
    out = dict(secao="F3-YANG_2021", emb_um=EMB_TRIO, trims=TRIMS,
               tentativa=tent,
               tripe_final={c: dict(mae=fin[c].get("mae"),
                                    maxerr=fin[c].get("maxerr"))
                            for c in CASOS},
               fila={c: "canal estrutural confundido (item 2)"
                     for c in ("yang2021_amp0p8mm_ax6kN",
                               "yang2021_fig2_typical")
                     if not passa(fin[c])},
               verdict=verdict)
    p = _ROOT / "New_Theory/f3_yang2021_result.json"
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
