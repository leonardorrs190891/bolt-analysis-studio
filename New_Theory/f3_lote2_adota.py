# -*- coding: utf-8 -*-
"""F3-LOTE2 — ADOÇÃO dos PASSes (L2c, L2d, L2b-13A_first, L2a per-figura)
+ verificação. Single-writer. 5A fica para tentativa 2 (N_emb)."""
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

ALVOS = {
    "sun2025efa109235_transverse_grease_crimp": (0.0221, 0.0886),
    "sun2025efa109235_axial_F7.5kN_standard": (0.0253, 0.0395),
    "sun2025efa109235_axial_F17.5kN_standard": (0.0330, 0.0468),
    "ancora_interna": (0.052, 0.093),
    "zhang2006_fig16_runout_40kN_amp0p125": (0.0124, 0.0240),
}
CONTROLES = ["sun2025efa109235_axial_F7.5kN_crimp",
             "sun2025efa109235_transverse_grease_standard",
             "sun2025efa109235_transverse_nogrease_standard",
             "ancora_interna", "ancora_interna",
             "zhang2006_fig3_illus_M12x125_20kN_amp0p35"]


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(cid):
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    return simulate_case(record(cid), now="f3-lote2-adocao").to_dict()


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
    # L2c + L2d (SUN per_case)
    sun = d["sources"]["SUN_2025_CRIMP"]
    pc = sun["cfg"]["per_case"]
    pc["_grease_crimp"]["k_wear_spec"] = 1.5e-15
    pc["axial_f7.5kn_standard"] = {"C_creep": 9e-11}
    pc["axial_f17.5kn_standard"] = {"C_creep": 9e-11}
    prov = sun.setdefault("prov", {})
    prov["k_wear_spec_grease_crimp"] = (
        "lido-do-dado (planura do platô; grade L2c; corta o vazamento do "
        "wear K/H legado abaixo do floor)")
    prov["C_creep_axial_standard"] = (
        "fitado-this-rig PER-TOKEN — PROXY do canal axial ausente (L1); "
        "per-PAR quebra 3 casos (medido, f3_lote2); revisitar no L1-v2 (F4); "
        "falsificação do flank compartilhado anexa (exp≈4,5 > banda)")
    sun["verdict"] = sun.get("verdict", "") + (
        " | F3-LOTE2 2026-07-21: grease_crimp 0,035/0,103→0,022/0,089 (kw "
        "lido; NÃO depende mais da decisão G2 — atualizar fila item 6); "
        "axiais standard 0,091/0,140→0,025/0,039 e 0,096/0,154→0,033/0,047 "
        "(C_creep proxy per-token 9e-11)")
    # L2b 13A_first
    g13 = d["sources"]["ancora_interna"]
    g13["cfg"]["emb_um"] = 2.0
    g13["cfg"]["k_ratchet"] = 3e-5
    g13.setdefault("prov", {})["emb_um"] = "lido-do-dado (queda inicial 0,016)"
    g13["prov"]["k_ratchet"] = ("dreno linear per-espécime (precedente "
                                "Karlsen 3×); grade L2b")
    g13["verdict"] = g13.get("verdict", "") + (
        " | F3-LOTE2: 0,176 maxerr→0,093 (emb lido + ratchet)")
    # L2a per-figura
    zg = dict(d["sources"]["ZHANG_2006"])
    d["sources"]["ZHANG_2006_fig16"] = {
        "pack": zg.get("pack", "PACK"),
        "cfg": dict(zg["cfg"], C_creep=5e-12),
        "prov": {"C_creep": ("lido-do-dado (platô REAL do fig16, slope "
                             "-0,0126/década; leitura anterior 3,08e-11 "
                             "contaminada pelo joelho); grupo PER-FIGURA — "
                             "C compartilhado quebra fig3 (medido)")},
        "verdict": ("F3-LOTE2 2026-07-21: fig16 0,086/0,150→0,012/0,024; "
                    "fig3 intacto no grupo original (kernel-fila)")}
    txt = json.dumps(d, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(P, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print("[adoção] lote2 gravado (4 PASSes)", flush=True)

    ids = list(ALVOS) + CONTROLES
    res = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, cid): cid for cid in ids}
        for fut in as_completed(futs):
            r = fut.result()
            res[r["case_id"]] = r
            print(f"  {r['case_id'][:44]:44s} mae="
                  f"{r.get('mae') and round(r['mae'], 4)} mx="
                  f"{r.get('maxerr') and round(r['maxerr'], 4)}", flush=True)

    ok_alvo = all(abs(res[c]["mae"] - e[0]) <= 0.005
                  and abs(res[c]["maxerr"] - e[1]) <= 0.005
                  and res[c]["mae"] < 0.10 and res[c]["maxerr"] < 0.10
                  for c, e in ALVOS.items())
    ok_ctrl = all(res[c].get("mae") == (antes.get(c) or {}).get("mae")
                  for c in CONTROLES)
    print(f"[verificação] alvos 5/5: {ok_alvo} | controles: {ok_ctrl}",
          flush=True)
    if not (ok_alvo and ok_ctrl):
        print("[ROLLBACK NECESSÁRIO]", flush=True)
        return 1
    from bolt_analysis_studio.validation.runner import CaseResult
    from bolt_analysis_studio.validation.store import ValidationStore
    store = ValidationStore()
    for c in ALVOS:
        store.put(CaseResult.from_dict(res[c]))
    for _ in range(200):
        try:
            store.save(); break
        except PermissionError:
            time.sleep(0.05)
    print("[store] 5 casos atualizados", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
