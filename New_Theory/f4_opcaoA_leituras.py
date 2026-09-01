# -*- coding: utf-8 -*-
"""OPÇÃO A do PARE F4 (trilha standing do MEM §2): adoção SÓ das RECEITAS POR
LEITURA per-fonte nos 3 rigs R5 — classe lido-do-dado/input-de-paper, promoção
direta; NENHUMA forma nova (flank_wear_on/flank_transverse_on/k_wear_flank/
s_crit ficam DEFAULT=OFF, não-adotadas — decisão do professor pendente).

Receitas (prereg-2 + painel; placebo provou 21/22 com canal morto):
- tr_loose_gain=0 (paper: zero rotação MEDIDA z18/z19; liu2020 atribuição);
- K_archard=0 (SEM/EDX: desgaste no FLANCO; liu2020 rollers) — com k_wear_spec
  default 0, wear transversal OFF por leitura;
- C_creep=0 (nenhum canal lento reportado);
- emb_um LIDO (L24): liu2020 1,121 / zhang18 2,100 / zhang19 1,068 µm;
  N_emb: 300/150/150;
- µ input-de-paper: liu2020 zinc 0,150 / DLC 0,126; zhang19 0,241.

Gate: 21/22 tripé<0,1 (liu2020 0,4mm FICA violadora → exceção-C PROPOSTA,
prova = atribuição explícita do paper §3.1.2, cauda de trinca; regra de taxa
não achou changepoint — registrado); controles bit-idênticos.
PASS ⇒ adota (single-writer) + verificação + store.
Uso: python New_Theory/f4_opcaoA_leituras.py [--workers N]
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

RECEITAS = {
    "LIU_2020_WEAR": dict(
        cfg=dict(emb_um=1.1209964412811393, N_emb=300.0, tr_loose_gain=0.0,
                 K_archard=0.0, k_wear_spec=0.0, C_creep=0.0,
                 per_case={"zinc": {"mu_thread": 0.150, "mu": 0.150},
                           "dlc": {"mu_thread": 0.126, "mu": 0.126}}),
        casos=["liu2020_fig5b_zinc_P0-12kN_AF0.2mm",
               "liu2020_fig5b_zinc_P0-18kN_AF0.2mm",
               "liu2020_fig5b_zinc_P0-24kN_AF0.2mm",
               "liu2020_fig9_zinc_AF0.1mm_P0-18kN",
               "liu2020_fig9_zinc_AF0.2mm_P0-18kN",
               "liu2020_fig9_zinc_AF0.3mm_P0-18kN",
               "liu2020_fig9_zinc_AF0.4mm_P0-18kN",
               "liu2020_fig15_DLC_P0-18kN_AF0.2mm",
               "liu2020_fig15_DLC_P0-19.28kN_AF0.2mm"]),
    "ZHANG_2018": dict(
        cfg=dict(emb_um=2.0996441281138796, N_emb=150.0, tr_loose_gain=0.0,
                 K_archard=0.0, k_wear_spec=0.0, C_creep=0.0),
        casos=["zhang18_fig2_test1_20kN_1e3cyc_preload_vs_cycles",
               "zhang18_fig2_test2_20kN_1e4cyc_preload_vs_cycles",
               "zhang18_fig2_test3_20kN_1e5cyc_preload_vs_cycles",
               "zhang18_fig2_test4_20kN_5e5cyc_preload_vs_cycles",
               "zhang18_fig13_14kN_preload_vs_cycles",
               "zhang18_fig13_20kN_preload_vs_cycles",
               "zhang18_fig13_26kN_preload_vs_cycles",
               "zhang18_fig16_with_locker_preload_vs_cycles",
               "zhang18_fig16_without_locker_preload_vs_cycles"]),
    "ZHANG_2019": dict(
        cfg=dict(emb_um=1.0676156583629897, N_emb=150.0, tr_loose_gain=0.0,
                 K_archard=0.0, k_wear_spec=0.0, C_creep=0.0, mu_thread=0.241),
        casos=["zhang19_fig4_1e3cyc_Test1to3_preload_vs_cycles",
               "zhang19_fig4_1e4cyc_Test4to6_preload_vs_cycles",
               "zhang19_fig4_1e5cyc_Test7to9_preload_vs_cycles",
               "zhang19_fig4_2e5cyc_Test10to12_preload_vs_cycles"]),
}
EXCECAO = "liu2020_fig9_zinc_AF0.4mm_P0-18kN"
CONTROLES = ["liu2017_axial_AF_7p5kN", "bauer2024_M8_fig6_rep1",
             "liu2025_M16_amp0p5", "li2022ti_axialmin_15Hz",
             "zhang2006_fig16_runout_40kN_amp0p125"]
PROV = {
    "tr_loose_gain": ("lido-do-dado/paper: rotação ZERO medida (z18 porca "
                      "prevailing + z19 sensor 0,045°; liu2020 atribuição "
                      "§estágios I/II)"),
    "K_archard": ("paper-attribution (SEM/EDX: desgaste no FLANCO da rosca, "
                  "não no bearing; liu2020: rollers isolam placa-placa) — "
                  "wear transversal OFF por leitura"),
    "k_wear_spec": ("=0 pela MESMA leitura (a via canônica de wear é o "
                    "k_wear_spec do shared 5e-14 — o zero per-fonte precisa "
                    "vencê-lo; achado da verificação opção-A)"),
    "C_creep": "paper-attribution: nenhum canal lento reportado",
    "emb_um": "LIDO L24 (Estágio I da curva de referência da fonte)",
    "N_emb": "escala do Estágio I (~centenas de ciclos, lido)",
    "_forma": ("NENHUMA forma nova adotada — flank_wear_on/flank_transverse_on"
               "/k_wear_flank/flank_s_crit ficam default OFF (decisão do "
               "professor pendente, PARE F4 §6; placebo do painel: 21/22 com "
               "canal morto)"),
}


def _apply(d):
    for grp, r in RECEITAS.items():
        g = d["sources"].setdefault(grp, {"pack": "", "cfg": {}})
        g["pack"] = g.get("pack") or ""
        g["cfg"] = dict(r["cfg"])
    return d


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(args):
    cid, sb = args
    if sb:
        os.environ["BAS_ADOPTED_CONFIGS"] = sb
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    r = simulate_case(record(cid), now="f4-opcaoA")
    return {"case_id": cid, "mae": r.mae, "maxerr": r.maxerr, "ok": r.ok,
            "d": r.to_dict()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))
    store = json.loads(io.open(
        _ROOT / "Models/CALIBRATION_AND_VALIDATION/validation_store.json",
        encoding="utf-8").read())

    # ---- fase 1: verificação em sandbox ----
    d = _apply(json.loads(io.open(_ROOT / "New_Theory/adopted_configs.json",
                                  encoding="utf-8").read()))
    fd, sb = tempfile.mkstemp(suffix=".json", prefix="opA_")
    with io.open(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False))
    casos = [c for r in RECEITAS.values() for c in r["casos"]]
    res = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, (c, sb)): c
                for c in casos + CONTROLES}
        done = 0
        for fut in as_completed(futs):
            r = fut.result()
            res[r["case_id"]] = r
            done += 1
            print(f"  [{done}/{len(casos) + len(CONTROLES)}] "
                  f"{r['case_id'][-32:]:32s} mae="
                  f"{r['mae'] and round(r['mae'], 3)} mx="
                  f"{r['maxerr'] and round(r['maxerr'], 3)}", flush=True)
    os.unlink(sb)

    def passa(c):
        v = res[c]
        return (v.get("mae") or 9) < 0.10 and (v.get("maxerr") or 9) < 0.10

    n_pass = sum(passa(c) for c in casos)
    excecao_e_a_unica = all(passa(c) for c in casos if c != EXCECAO)
    ctrl_ok = all(res[c]["mae"] == store[c]["mae"] for c in CONTROLES)
    verdict = "PASS" if (n_pass >= 21 and excecao_e_a_unica and ctrl_ok) \
        else "FAIL"
    out = dict(secao="OPÇÃO A — leituras puras (PARE F4)", n_pass=n_pass,
               excecao_unica=excecao_e_a_unica, controles=ctrl_ok,
               tripe={c: dict(mae=res[c].get("mae"),
                              maxerr=res[c].get("maxerr")) for c in casos},
               verdict=verdict)
    p = _ROOT / "New_Theory/f4_opcaoA_result.json"
    txt = json.dumps(out, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(p, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print(f"[gate] {verdict} ({n_pass}/22; exceção única="
          f"{excecao_e_a_unica}; ctrl={ctrl_ok})", flush=True)
    if verdict != "PASS":
        return 1

    # ---- fase 2: adoção canônica (single-writer) + store ----
    P = _ROOT / "New_Theory/adopted_configs.json"
    d = json.loads(io.open(P, encoding="utf-8").read())
    d = _apply(d)
    for grp in RECEITAS:
        g = d["sources"][grp]
        g["prov"] = dict(g.get("prov", {}), **PROV)
        g["verdict"] = (g.get("verdict", "") +
                        " | OPÇÃO A do PARE F4 2026-07-22: receitas por "
                        "LEITURA adotadas (21/22 tripé; 0,4mm → exceção-C "
                        "proposta p/ F5, prova §3.1.2 do paper). Nenhuma "
                        "forma nova. f4_opcaoA_result.json")
    txt = json.dumps(d, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(P, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print("[adoção] 3 grupos gravados (leituras puras)", flush=True)

    from bolt_analysis_studio.validation.runner import CaseResult
    from bolt_analysis_studio.validation.store import ValidationStore
    st = ValidationStore()
    for c in casos:
        st.put(CaseResult.from_dict(res[c]["d"]))
    for _ in range(200):
        try:
            st.save(); break
        except PermissionError:
            time.sleep(0.05)
    print("[store] 22 casos gravados", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
