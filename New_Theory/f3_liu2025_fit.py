# -*- coding: utf-8 -*-
"""F3-LIU_2025 (prereg no ledger mestre 2026-07-21): C_creep per-par (grade
×0,65-0,75 do shared) + trims N_D registrados (regra: taxa local >3× mediana
do estágio II, contígua até o fim) + slip_onset_W lido-do-joelho per-espécime
nos grupos-token amp0p4/amp0p5 (precedente Karlsen 2×).

Fase A: C ∈ {1,2, 1,3, 1,4}e-11 × 5 curvas sem W próprio (trims aplicados).
Fase B: melhor C fixo; W ∈ {300, 350, 375, 400} kJ × {amp0p4, amp0p5}.
Gates: 7/7 tripé pós-trim; amp0p8 maxerr ≤0,095; mediana fonte melhora.
Fallback pré-comprometido: amp0p25/amp0p3 >0,1 → rótulo B-forma §4.17.
Saída: New_Theory/f3_liu2025_result.json. NÃO escreve no canônico.
Uso: python New_Theory/f3_liu2025_fit.py [--workers N]
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

TRIMS = {"amp0p25": 240000, "amp0p3": 180000, "amp0p4": 60000,
         "amp0p5": 30000, "amp0p6": 18000, "amp0p8": 11500, "fig2": 8000}
CASOS = ["liu2025_M16_amp0p25", "liu2025_M16_amp0p3", "liu2025_M16_amp0p4",
         "liu2025_M16_amp0p5", "liu2025_M16_amp0p6", "liu2025_M16_amp0p8",
         "liu2025_M16_fig2_single"]
SEM_W = [c for c in CASOS if "amp0p4" not in c and "amp0p5" not in c]
C_GRID = [1.2e-11, 1.3e-11, 1.4e-11]
W_GRID = [3.0e5, 3.5e5, 3.75e5, 4.0e5]


def _sandbox(C, W04=None, W05=None):
    d = json.loads(io.open(_ROOT / "New_Theory/adopted_configs.json",
                           encoding="utf-8").read())
    g = d["sources"]["LIU_2025"]
    g["cfg"]["C_creep"] = float(C)
    g["cfg"]["trim_n_max"] = TRIMS
    for tok, W in (("amp0p4", W04), ("amp0p5", W05)):
        gk = f"LIU_2025_{tok}"
        if W is not None:
            base = dict(g["cfg"])
            base.pop("per_case", None)
            base["slip_onset_W"] = float(W)
            d["sources"][gk] = {"pack": g.get("pack", "PACK"), "cfg": base}
        else:
            d["sources"].pop(gk, None)
    fd, p = tempfile.mkstemp(suffix=".json", prefix="liu25_")
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
    r = simulate_case(record(cid), now="f3-liu25")
    return {"tag": tag, "case_id": cid, "ok": r.ok, "mae": r.mae,
            "maxerr": r.maxerr}


def _rodada(tarefas, workers):
    out = {}
    with ProcessPoolExecutor(max_workers=workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, t): t for t in tarefas}
        done = 0
        for fut in as_completed(futs):
            r = fut.result()
            out.setdefault(r["tag"], {})[r["case_id"]] = r
            done += 1
            print(f"  [{done}/{len(tarefas)}] {r['case_id'][-14:]} "
                  f"mae={r['mae'] and round(r['mae'], 3)} "
                  f"mx={r['maxerr'] and round(r['maxerr'], 3)}", flush=True)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))
    import statistics

    # Fase A
    sbs = []
    tarefas = []
    for C in C_GRID:
        sb = _sandbox(C)
        sbs.append(sb)
        for cid in SEM_W:
            tarefas.append((cid, sb, f"C={C:.2e}"))
    print(f"[fase A] {len(tarefas)} sims", flush=True)
    gA = _rodada(tarefas, args.workers)

    def escoreA(pc):
        vs = [max((v["maxerr"] or 9) - 0.10, 0) for v in pc.values()]
        return (sum(1 for v in vs if v > 0),
                statistics.median([v["mae"] for v in pc.values()]))

    bestC_tag = min(gA, key=lambda t: escoreA(gA[t]))
    bestC = float(bestC_tag.split("=")[1])
    print(f"[fase A] melhor C={bestC:.3e}", flush=True)

    # Fase B
    tarefas = []
    sbs2 = []
    for W in W_GRID:
        sb = _sandbox(bestC, W04=W, W05=W)
        sbs2.append(sb)
        tarefas.append(("liu2025_M16_amp0p4", sb, f"W={W:.2e}"))
        tarefas.append(("liu2025_M16_amp0p5", sb, f"W={W:.2e}"))
    print(f"[fase B] {len(tarefas)} sims", flush=True)
    gB = _rodada(tarefas, args.workers)

    def escoreB(pc, cid):
        v = pc.get(cid) or {}
        return (max((v.get("maxerr") or 9) - 0.10, 0), v.get("mae") or 9)

    bestW = {}
    for cid in ("liu2025_M16_amp0p4", "liu2025_M16_amp0p5"):
        t = min(gB, key=lambda t: escoreB(gB[t], cid))
        bestW[cid] = dict(W=float(t.split("=")[1]), **{
            k: gB[t][cid][k] for k in ("mae", "maxerr")})
        print(f"[fase B] {cid[-8:]}: W={bestW[cid]['W']:.2e} "
              f"{bestW[cid]['mae']:.3f}/{bestW[cid]['maxerr']:.3f}",
              flush=True)

    for sb in sbs + sbs2:
        try:
            os.unlink(sb)
        except OSError:
            pass

    final = {c: gA[bestC_tag][c] for c in SEM_W}
    final["liu2025_M16_amp0p4"] = bestW["liu2025_M16_amp0p4"]
    final["liu2025_M16_amp0p5"] = bestW["liu2025_M16_amp0p5"]
    passa = {c: ((final[c].get("mae") or 9) < 0.10
                 and (final[c].get("maxerr") or 9) < 0.10) for c in CASOS}
    amp08_ok = (final["liu2025_M16_amp0p8"].get("maxerr") or 9) <= 0.095
    n_pass = sum(passa.values())
    verdict = "PASS" if (n_pass == 7 and amp08_ok) else (
        "PASS-parcial" if n_pass >= 5 else "FAIL")
    out = dict(secao="F3-LIU_2025", C_creep=bestC, trims=TRIMS,
               W_lido={k: v["W"] for k, v in bestW.items()},
               tripe_final={c: dict(mae=final[c].get("mae"),
                                    maxerr=final[c].get("maxerr"))
                            for c in CASOS},
               passa=passa, n_pass=n_pass, amp0p8_gate=amp08_ok,
               verdict=verdict,
               fallback=("amp0p25/amp0p3 acima de 0,1 → rótulo B-forma "
                         "§4.17" if not (passa["liu2025_M16_amp0p25"]
                                         and passa["liu2025_M16_amp0p3"])
                         else None))
    p = _ROOT / "New_Theory/f3_liu2025_result.json"
    txt = json.dumps(out, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(p, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print(f"[gate] verdict={verdict} n_pass={n_pass}/7 → {p}", flush=True)
    return 0 if verdict.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
