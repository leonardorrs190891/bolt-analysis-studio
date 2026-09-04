# -*- coding: utf-8 -*-
"""F3-LIU_2025 — ADOÇÃO (gate PASS 7/7) + verificação. Single-writer."""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

TRIMS = {"amp0p25": 240000, "amp0p3": 180000, "amp0p4": 60000,
         "amp0p5": 30000, "amp0p6": 18000, "amp0p8": 11500, "fig2": 8000}
CASOS = ["liu2025_M16_amp0p25", "liu2025_M16_amp0p3", "liu2025_M16_amp0p4",
         "liu2025_M16_amp0p5", "liu2025_M16_amp0p6", "liu2025_M16_amp0p8",
         "liu2025_M16_fig2_single"]
CONTROLES = ["bauer2024_M8_fig6_rep1", "chu2026ti_D0p3mm_F0_49kN_test1",
             "yang2021_amp0p5mm_ax8kN", "li2022ti_axialmin_15Hz"]
C_ADOT = 1.3e-11
W_ADOT = 4.0e5


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(cid):
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    return simulate_case(record(cid), now="f3-liu25-adocao").to_dict()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))

    store_path = _ROOT / "Models/CALIBRATION_AND_VALIDATION/validation_store.json"
    antes = json.loads(io.open(store_path, encoding="utf-8").read())

    P = _ROOT / "New_Theory/adopted_configs.json"
    d = json.loads(io.open(P, encoding="utf-8").read())
    g = d["sources"]["LIU_2025"]
    g["cfg"]["C_creep"] = C_ADOT
    g["cfg"]["trim_n_max"] = TRIMS
    prov = g.setdefault("prov", {})
    prov["C_creep"] = ("fitado-this-rig per-par (§4.7; era herdado do shared "
                       "âncora interna — única constante do grupo sem procedência; "
                       "grade F3 ×0,70)")
    prov["trim_n_max"] = ("EXCEÇÃO bloco C (assinatura na F5): estágio "
                          "fatigue-fracture out-of-model (paper declara "
                          "todos os ensaios até fratura; boundary 0,33); "
                          "regra pré-declarada: taxa local >3× mediana do "
                          "estágio II, contígua até o fim; prova "
                          "PR-39v2 + fig2-vs-amp0p8 scatter 44% em vida")
    g["verdict"] = g.get("verdict", "") + (
        " | F3-LIU_2025 2026-07-21: PASS 7/7 pós-trim (f3_liu2025_result"
        ".json); amp0p4 0,102/0,212→0,046/0,062")
    for tok in ("amp0p4", "amp0p5"):
        base = dict(g["cfg"])
        base.pop("per_case", None)
        base["slip_onset_W"] = W_ADOT
        d["sources"][f"LIU_2025_{tok}"] = {
            "pack": g.get("pack", "PACK"), "cfg": base,
            "prov": {"slip_onset_W": ("lido-do-joelho per-espécime (L24; "
                                      "precedente Karlsen run7p1/run2p2); "
                                      "bisseção N80")},
            "verdict": "F3-LIU_2025: grupo-token p/ W per-espécime"}
    txt = json.dumps(d, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(P, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print("[adoção] LIU_2025 + 2 grupos-token gravados", flush=True)

    ids = CASOS + CONTROLES
    res = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, cid): cid for cid in ids}
        for fut in as_completed(futs):
            r = fut.result()
            res[r["case_id"]] = r
            print(f"  {r['case_id'][:38]:38s} mae="
                  f"{r.get('mae') and round(r['mae'], 4)} mx="
                  f"{r.get('maxerr') and round(r['maxerr'], 4)}", flush=True)

    esperado = json.loads(io.open(_ROOT / "New_Theory/f3_liu2025_result.json",
                                  encoding="utf-8").read())["tripe_final"]
    ok_fonte = all(
        abs(res[c].get("mae") - esperado[c]["mae"]) <= 0.005
        and abs(res[c].get("maxerr") - esperado[c]["maxerr"]) <= 0.005
        and res[c].get("mae") < 0.10 and res[c].get("maxerr") < 0.10
        for c in CASOS)
    ok_ctrl = all(res[c].get("mae") == (antes.get(c) or {}).get("mae")
                  and res[c].get("maxerr") == (antes.get(c) or {}).get("maxerr")
                  for c in CONTROLES)
    print(f"[verificação] fonte 7/7 tripé: {ok_fonte} | controles: {ok_ctrl}",
          flush=True)
    if not (ok_fonte and ok_ctrl):
        print("[ROLLBACK NECESSÁRIO — store não gravado]", flush=True)
        return 1

    from bolt_analysis_studio.validation.runner import CaseResult
    from bolt_analysis_studio.validation.store import ValidationStore
    store = ValidationStore()
    for c in CASOS:
        store.put(CaseResult.from_dict(res[c]))
    for _ in range(200):
        try:
            store.save(); break
        except PermissionError:
            time.sleep(0.05)
    print("[store] 7 casos LIU_2025 atualizados", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
