# -*- coding: utf-8 -*-
"""F3.1-JCSR — ADOÇÃO per-condição (saturante, melhores células t1/t2) +
verificação (4 casos + indoor + 4 irmãs creep bit-idênticas). Single-writer.

Registro do veredito: G-JCSR-a estrito = FAIL2 (stainless maxerr 0,124 e
outdoor 0,131 — piso estrutural: cliff de corrosão e rebound são forma
faltante). Adoção justificada pela cláusula F2.2 standing do prompt-mestre
(saturante DOMINA o log-t nos 4: fecha 2 tripés completos e melhora
mediana 0,218→~0,05); os 2 residuais SEGUEM na lista-mestre (fila/exceção
F5 com prova). G-JCSR-b/c/d verificados aqui.

Uso: python New_Theory/f3_jcsr_adota.py [--workers N]
"""
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

D = 86400.0
ADO = {
    "JCSR_2023_galv_seawater": dict(
        cid="jcsr2023_galv_seawater", C_creep=1.068e-09,
        creep_t_c=2 * 7.95 * D, creep_alpha_sat=3.0,
        esperado=(0.0390, 0.0966)),
    "JCSR_2023_plain_seawater": dict(
        cid="jcsr2023_plain_seawater", C_creep=7.125e-10,
        creep_t_c=2 * 14.65 * D, creep_alpha_sat=3.0,
        esperado=(0.0289, 0.0784)),
    "JCSR_2023_stainless_seawater": dict(
        cid="jcsr2023_stainless_seawater", C_creep=2 * 8.68e-10,
        creep_t_c=2 * 24.7 * D, creep_alpha_sat=5.0,
        esperado=(0.0619, 0.1237)),
    "JCSR_2023_outdoor": dict(
        cid="jcsr2023_plain_outdoor", C_creep=2 * 3.40e-10,
        creep_t_c=1.5 * 99.0 * D, creep_alpha_sat=5.0,
        esperado=(0.0621, 0.1313)),
}
CONTROLES = ["jcsr2023_plain_indoor", "caccese2009_protruding_45kN",
             "caccese2009_tapered_45kN_rep1", "qin2024acm_25C_i0pct",
             "li2022marstruc_creep_10kN_Ra0p8_min"]


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(cid):
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    return simulate_case(record(cid), now="f3-jcsr-adocao").to_dict()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))

    store_path = _ROOT / "Models/CALIBRATION_AND_VALIDATION/validation_store.json"
    antes = json.loads(io.open(store_path, encoding="utf-8").read())

    # ---- adoção (single-writer) ----
    P = _ROOT / "New_Theory/adopted_configs.json"
    d = json.loads(io.open(P, encoding="utf-8").read())
    for grupo, a in ADO.items():
        d["sources"][grupo] = {
            "pack": "PACK",
            "cfg": {"creep_mode": "saturating", "C_creep": a["C_creep"],
                    "creep_t_c": a["creep_t_c"],
                    "creep_alpha_sat": a["creep_alpha_sat"]},
            "prov": {
                "creep_mode": ("switch por prereg F3.1-JCSR (capacidade T7; "
                               "F2.2 standing: adotar onde o tripé melhora)"),
                "C_creep": ("fitado-this-rig — PROXY AMBIENTAL per-par×"
                            "ambiente (corrosão vestida de creep; 18-64× o "
                            "âncora interna; NUNCA poolar com pares metálicos limpos; "
                            "aviso do check_input esperado)"),
                "creep_t_c": ("seed = onset c da Eq.(2) do paper (input-de-"
                              "paper) × ajuste fino 1,5-2× (fitado-this-rig)"),
                "creep_alpha_sat": "fitado-this-rig (grade)"},
            "verdict": ("F3.1-JCSR 2026-07-21: saturante per-condição ADOTADA "
                        "— domina o log-t nos 4 (gap era NÍVEL per-condição + "
                        "cinética; o FAIL do F2 P2.2 era confundido pelo nível "
                        "compartilhado). Tripé fecha em galv/plain_sea; "
                        "stainless 0,062/0,124 e outdoor 0,062/0,131 = piso "
                        "estrutural (cliff de corrosão/rebound → forma "
                        "faltante, fila/candidata exceção F5). Gates: "
                        "f3_jcsr_result{,2}.json")}
    txt = json.dumps(d, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(P, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print("[adoção] 4 grupos JCSR gravados", flush=True)

    # ---- verificação ----
    ids = [a["cid"] for a in ADO.values()] + CONTROLES
    res = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, cid): cid for cid in ids}
        for fut in as_completed(futs):
            r = fut.result()
            res[r["case_id"]] = r
            print(f"  {r['case_id'][:40]:40s} mae="
                  f"{r.get('mae') and round(r['mae'], 4)}", flush=True)

    ok_fonte = True
    for grupo, a in ADO.items():
        m, x = res[a["cid"]].get("mae"), res[a["cid"]].get("maxerr")
        em, ex_ = a["esperado"]
        if abs(m - em) > 0.005 or abs(x - ex_) > 0.005:
            ok_fonte = False
            print(f"  !! {a['cid']}: {m:.4f}/{x:.4f} vs esperado {em}/{ex_}",
                  flush=True)
    ok_ctrl = True
    for c in CONTROLES:
        a0 = antes.get(c) or {}
        if res[c].get("mae") != a0.get("mae") \
                or res[c].get("maxerr") != a0.get("maxerr"):
            ok_ctrl = False
            print(f"  !! CONTROLE MUDOU: {c}", flush=True)
    print(f"[verificação] fonte reproduz células: {ok_fonte} | "
          f"controles intactos: {ok_ctrl}", flush=True)
    if not (ok_fonte and ok_ctrl):
        print("[ROLLBACK NECESSÁRIO — store não gravado]", flush=True)
        return 1

    from bolt_analysis_studio.validation.runner import CaseResult
    from bolt_analysis_studio.validation.store import ValidationStore
    store = ValidationStore()
    for a in ADO.values():
        store.put(CaseResult.from_dict(res[a["cid"]]))
    for _ in range(200):
        try:
            store.save(); break
        except PermissionError:
            time.sleep(0.05)
    print("[store] 4 casos JCSR atualizados", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
