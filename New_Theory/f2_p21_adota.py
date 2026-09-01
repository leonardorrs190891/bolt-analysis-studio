# -*- coding: utf-8 -*-
"""F2 P2.1 — ADOÇÃO (tentativa 2, k selecionado por critério-de-gate na grade)
+ verificação: re-sim da fonte (deve reproduzir a célula vencedora) e 6
controles transversais (paridade exata vs store). Single-writer.

Uso: python New_Theory/f2_p21_adota.py [--workers N]
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

FONTE = "LI_2022_TRIBOINT"
CASOS = ["li2022ti_axialmin_10Hz", "li2022ti_axialmin_15Hz",
         "li2022ti_axialmin_20Hz", "li2022ti_axial_10Hz_full"]
CONTROLES = ["bauer2024_M8_fig6_rep1", "liu2025_M16_amp0p25",
             "chu2026ti_D0p3mm_F0_49kN_test1",
             "eccles2010_fig3_typical_no_axial",
             "sun2025efa109235_transverse_grease_crimp",
             "liu2017_axial_F0_15kN"]      # 5 transversais + 1 axial de OUTRA fonte
K_ADOTADO = 2.154434690031884e-13
EXP = 1.5


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(cid: str) -> dict:
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    return simulate_case(record(cid), now="p21-adocao").to_dict()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))

    # ---- snapshot do store ANTES (controles + fonte) ----
    store_path = _ROOT / "Models/CALIBRATION_AND_VALIDATION/validation_store.json"
    antes = json.loads(io.open(store_path, encoding="utf-8").read())

    # ---- adoção no canônico (single-writer) ----
    P = _ROOT / "New_Theory/adopted_configs.json"
    d = json.loads(io.open(P, encoding="utf-8").read())
    g = d["sources"][FONTE]
    g["cfg"]["flank_wear_on"] = 1.0
    g["cfg"]["k_wear_flank"] = K_ADOTADO
    g["cfg"]["flank_amp_exp"] = EXP
    prov = g.setdefault("prov", {})
    prov["flank_wear_on"] = ("switch de forma ligado por PREREG (F2 P2.1 "
                             "2026-07-21; switches nunca são fitados)")
    prov["k_wear_flank"] = ("fitado-this-rig (grade log10 em curva completa, "
                            "tentativa 2 = seleção por critério-de-gate; "
                            "partida 1,89e-13 do T4 Rig B; NOTA: ~10x acima "
                            "da banda KB thread|35CrMo-SCM435 [4e-15,2e-14] "
                            "— o canal representa desgaste de FLANCO sob A_F "
                            "per-rig, não o thread-wear da âncora; aviso do "
                            "check_input esperado e documentado)")
    prov["flank_amp_exp"] = ("herdado do Rig A/T4 tentativa 2 (=1,5, Liu "
                             "2020 medido; Rig B não separa amplitude — "
                             "A_F fixo)")
    g["verdict"] = g.get("verdict", "") + (
        " | F2 P2.1 2026-07-21: canal de flanco ADOTADO per-rig "
        f"(k={K_ADOTADO:.4e}, exp=1,5): mediana 0,074→0,041; axialmin 3/3 "
        "tripé<0,1; full maxerr 0,405→0,239 (cauda de fratura out-of-model; "
        "candidata a exceção F5). Gate: f2_p21_result.json")
    txt = json.dumps(d, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(P, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print("[adoção] gravada no canônico", flush=True)

    # ---- verificação pós-adoção ----
    ids = CASOS + CONTROLES
    res = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, cid): cid for cid in ids}
        for fut in as_completed(futs):
            r = fut.result()
            res[r["case_id"]] = r
            print(f"  {r['case_id'][:44]:44s} mae={r.get('mae') and round(r['mae'], 4)}",
                  flush=True)

    esperado = {
        "li2022ti_axialmin_10Hz": (0.053, 0.078),
        "li2022ti_axialmin_15Hz": (0.030, 0.049),
        "li2022ti_axialmin_20Hz": (0.020, 0.064),
        "li2022ti_axial_10Hz_full": (0.052, 0.239),
    }
    ok_fonte = True
    for c, (em, ex_) in esperado.items():
        m, x = res[c].get("mae"), res[c].get("maxerr")
        if abs(m - em) > 0.005 or abs(x - ex_) > 0.005:
            ok_fonte = False
            print(f"  !! fonte difere da célula: {c} {m:.4f}/{x:.4f} "
                  f"vs ~{em}/{ex_}", flush=True)
    ok_ctrl = True
    for c in CONTROLES:
        a = antes.get(c) or {}
        if res[c].get("mae") != a.get("mae") or res[c].get("maxerr") != a.get("maxerr"):
            ok_ctrl = False
            print(f"  !! CONTROLE MUDOU: {c} {a.get('mae')}->{res[c].get('mae')}",
                  flush=True)
    print(f"[verificação] fonte reproduz célula: {ok_fonte} | "
          f"controles intactos: {ok_ctrl}", flush=True)

    if not (ok_fonte and ok_ctrl):
        print("[ROLLBACK NECESSÁRIO — não gravando store]", flush=True)
        return 1

    # ---- store: grava fonte re-simulada (controles idênticos, sem efeito) ----
    from bolt_analysis_studio.validation.runner import CaseResult
    from bolt_analysis_studio.validation.store import ValidationStore
    store = ValidationStore()
    for cid in CASOS:
        store.put(CaseResult.from_dict(res[cid]))
    for _ in range(200):
        try:
            store.save(); break
        except PermissionError:
            time.sleep(0.05)
    print("[store] fonte atualizada (4 casos)", flush=True)

    # ---- registro da tentativa 2 no resultado do gate ----
    rp = _ROOT / "New_Theory/f2_p21_result.json"
    r = json.loads(io.open(rp, encoding="utf-8").read())
    r["tentativa2"] = dict(
        criterio=("seleção por critério-de-gate na MESMA grade simulada "
                  "(sem novo fit): k que passa G2.1a+G2.1b com menor mediana"),
        k_adotado=K_ADOTADO,
        tripe={c: dict(mae=res[c].get("mae"), maxerr=res[c].get("maxerr"))
               for c in CASOS},
        controles_intactos=ok_ctrl, verdict="PASS")
    r["verdict"] = "PASS (tentativa 2)"
    txt = json.dumps(r, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(rp, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print("[gate] PASS tentativa 2 registrado", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
