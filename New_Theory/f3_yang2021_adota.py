# -*- coding: utf-8 -*-
"""F3-YANG_2021 — ADOÇÃO (gate PASS t1) + verificação. Single-writer."""
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

EMB_TRIO = {"amp0p5": 3.85, "amp0p6": 3.85, "amp0p7": 3.85}
TRIMS = {"fig2": 5850, "amp1p0": 3150, "amp0p8": 5450,
         "amp0p6": 11800, "amp0p7": 14000, "amp0p5": 27000}
CASOS = ["yang2021_amp0p5mm_ax8kN", "yang2021_amp0p6mm_ax8kN_r1",
         "yang2021_amp0p7mm_ax11p2kN", "yang2021_amp1p0mm_ax2kN",
         "yang2021_amp0p8mm_ax6kN", "yang2021_fig2_typical"]
CONTROLES = ["liu2025_M16_amp0p5", "bauer2024_M8_fig6_rep1",
             "10_Yang_2023_phenomenological_model__0_25_mm__2",
             "yang2019_M10_amp0p4_5Hz"]


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(cid):
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    return simulate_case(record(cid), now="f3-y21-adocao").to_dict()


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
    g = d["sources"].setdefault("YANG_2021", {"pack": "PACK", "cfg": {}})
    g["cfg"]["emb_um"] = EMB_TRIO
    g["cfg"]["trim_n_max"] = TRIMS
    prov = g.setdefault("prov", {})
    prov["emb_um"] = ("INPUT-DE-PAPER (trio amp0p5/0p6/0p7): 'material "
                      "loosening ≈ 10% de F0' (p.5) ⇒ emb=0,10·F0/k_b≈3,85 µm "
                      "no grip vigente (invariante a grip). Grupo A (fig2/"
                      "amp0p8/amp1p0) fica no default 11 µm assumed-VDI: lá o "
                      "emb pré-gasta a perda ESTRUTURAL confundida — "
                      "inconsistência física DELIBERADA e documentada")
    prov["trim_n_max"] = ("EXCEÇÃO bloco C (assinatura F5): cauda terminal "
                          "out-of-model (N2/tangente-45° do paper; convenção "
                          "CLAUDE.md p/ yang2021); regra taxa>8× mediana")
    g["verdict"] = (g.get("verdict", "") +
                    " | F3-YANG_2021 2026-07-21: PASS t1 leitura pura — trio+"
                    "amp1p0 tripé<0,1; amp0p8/fig2 melhoram e ficam FILA "
                    "(canal estrutural confundido, item 2). "
                    "f3_yang2021_result.json")
    txt = json.dumps(d, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(P, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print("[adoção] YANG_2021 gravado", flush=True)

    esperado = json.loads(io.open(_ROOT / "New_Theory/f3_yang2021_result.json",
                                  encoding="utf-8").read())["tripe_final"]
    ids = CASOS + CONTROLES
    res = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, cid): cid for cid in ids}
        for fut in as_completed(futs):
            r = fut.result()
            res[r["case_id"]] = r
            print(f"  {r['case_id'][:40]:40s} mae="
                  f"{r.get('mae') and round(r['mae'], 4)}", flush=True)

    ok_fonte = all(abs(res[c].get("mae") - esperado[c]["mae"]) <= 0.005
                   and abs(res[c].get("maxerr") - esperado[c]["maxerr"]) <= 0.005
                   for c in CASOS)
    alvo = CASOS[:4]
    ok_alvo = all(res[c].get("mae") < 0.10 and res[c].get("maxerr") < 0.10
                  for c in alvo)
    ok_ctrl = all(res[c].get("mae") == (antes.get(c) or {}).get("mae")
                  for c in CONTROLES)
    print(f"[verificação] reproduz: {ok_fonte} | alvo 4/4: {ok_alvo} | "
          f"controles: {ok_ctrl}", flush=True)
    if not (ok_fonte and ok_alvo and ok_ctrl):
        print("[ROLLBACK NECESSÁRIO]", flush=True)
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
    print("[store] 6 casos YANG_2021 atualizados", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
