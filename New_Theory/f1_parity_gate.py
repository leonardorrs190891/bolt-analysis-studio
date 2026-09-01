# -*- coding: utf-8 -*-
"""F1 Onda A — GATE DE PARIDADE pré-registrado (prereg 2026-07-21, G1a/G1b/G2a).

Contra o baseline vigente (store F0.4, commit ae2d7e0, fingerprint
01689f0bfad8), com o código F1 + adoções kj (ROUSSEAU_2025/ZHANG_2006):

- G1b (barato, sem ciclos): kj_mode_engaged por caso via __init__ do analyzer
  com a MESMA montagem do runner — engajado EXATAMENTE nos 8 casos com
  geometria adotada (rousseau2025 ×6, zhang2006 ×2); fallback em todos os
  demais.
- G1a+G2a (paridade exata): re-simula os 202 comparáveis em paralelo e exige
  mae/maxerr/rmse/resid_std/final_pred/ratio IDÊNTICOS (==, float a float) aos
  do store — a trajetória é k_j-cega no PACK (T6) e o check L7 é
  pós-processamento.
- PASS → grava o store novo (idêntico em números; ganha o campo l7_check) com
  retry-guard, e o resultado do gate em New_Theory/f1_parity_gate_result.json.
  FAIL → NÃO toca o store; grava o resultado com os diffs e sai 1.

Uso: python New_Theory/f1_parity_gate.py [--workers N]
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

ESPERADO_ENGAJAR = {
    "rousseau2025_steel_t10", "rousseau2025_steel_t12", "rousseau2025_steel_t14",
    "rousseau2025_hdpe_t10", "rousseau2025_hdpe_t12", "rousseau2025_hdpe_t14",
    "zhang2006_fig3_illus_M12x125_20kN_amp0p35",
    "zhang2006_fig16_runout_40kN_amp0p125",
}


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(case_id: str) -> dict:
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    rec = record(case_id)
    if rec is None:
        return {"case_id": case_id, "ok": False, "error": "caso não encontrado"}
    return simulate_case(rec, now="f1-parity-gate").to_dict()


def _engage_flags() -> dict:
    """G1b: instancia o analyzer por caso (zero ciclos) e lê kj_mode_engaged."""
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer, JointMaterial)
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.inputs import (geometry_for_case,
                                                        inputs_for)
    from bolt_analysis_studio.validation.runner import (
        _apply_adopted_geometry, material_kwargs_for)
    out = {}
    for rec in all_records():
        if rec.source == "USER":
            continue
        try:
            inp = inputs_for(rec.validation_case)
            geom = geometry_for_case(rec.validation_case,
                                     grip_mm=inp["grip_mm"]["value"],
                                     E=(inp.get("E") or {}).get("value"))
            geom = _apply_adopted_geometry(geom, rec.source, rec.case_id,
                                           rec.validation_case.bolt_size)
            mat = JointMaterial(**material_kwargs_for(rec, inp))
            ana = DynamicStiffnessAnalyzer(geom, mat,
                                           rec.validation_case.initial_preload_N)
            out[rec.case_id] = bool(ana.kj_mode_engaged)
        except Exception as exc:
            out[rec.case_id] = f"ERRO: {type(exc).__name__}: {exc}"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    ap.add_argument("--flags-only", action="store_true",
                    help="re-roda so o G1b (barato) e funde no resultado "
                         "existente — a paridade G1a ja registrada vale "
                         "(bug do CHECADOR na 1a rodada: inputs_for(rec) em "
                         "vez de inputs_for(rec.validation_case); os 202 sims "
                         "da paridade usaram o runner real, nao o checador)")
    args = ap.parse_args(argv)

    sys.path.insert(0, str(_ROOT / "src"))
    from bolt_analysis_studio.validation.case_registry import all_records

    res: dict = {"prereg": "docs/superpowers/specs/2026-07-21-master-f1-onda-a-prereg.md",
                 "baseline_store_commit": "ae2d7e0"}

    # ---------- G1b ----------
    print("[G1b] flags de engate…", flush=True)
    flags = _engage_flags()
    engajados = {k for k, v in flags.items() if v is True}
    erros_flag = {k: v for k, v in flags.items() if isinstance(v, str)}
    g1b_pass = (engajados == ESPERADO_ENGAJAR) and not erros_flag
    res["G1b"] = dict(engajados=sorted(engajados),
                      esperado=sorted(ESPERADO_ENGAJAR),
                      inesperados=sorted(engajados - ESPERADO_ENGAJAR),
                      faltando=sorted(ESPERADO_ENGAJAR - engajados),
                      erros=erros_flag, PASS=g1b_pass)
    print(f"[G1b] engajados={len(engajados)} esperado={len(ESPERADO_ENGAJAR)} "
          f"PASS={g1b_pass}", flush=True)

    if args.flags_only:
        out = _ROOT / "New_Theory/f1_parity_gate_result.json"
        prev = json.loads(io.open(out, encoding="utf-8").read())
        res["G1b"]["rerun"] = ("2a rodada flags-only 2026-07-21: a 1a rodada "
                               "tinha bug NO CHECADOR (inputs_for(rec) em vez "
                               "de inputs_for(rec.validation_case) — 202 "
                               "AttributeError); os sims da paridade G1a "
                               "usaram o runner real e VALEM (0 diffs). "
                               "Nenhum código de engine/runner mudou entre "
                               "as rodadas.")
        prev["G1b"] = res["G1b"]
        g1a_prev = bool(prev.get("G1a_G2a", {}).get("PASS"))
        prev["verdict"] = "PASS" if (g1b_pass and g1a_prev) else "FAIL"
        txt = json.dumps(prev, indent=1, ensure_ascii=False)
        for _ in range(200):
            try:
                with io.open(out, "w", encoding="utf-8") as f:
                    f.write(txt)
                break
            except PermissionError:
                time.sleep(0.05)
        print(f"[gate] verdict={prev['verdict']} (flags-only fundido) → {out}",
              flush=True)
        return 0 if prev["verdict"] == "PASS" else 1

    # ---------- G1a + G2a ----------
    store_path = _ROOT / "Models/CALIBRATION_AND_VALIDATION/validation_store.json"
    antigo = json.loads(io.open(store_path, encoding="utf-8").read())
    ids = [r.case_id for r in all_records() if r.source != "USER"]
    print(f"[G1a] re-simulando {len(ids)} casos em {args.workers} workers…",
          flush=True)
    novos: dict = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, cid): cid for cid in
                sorted(ids, key=lambda c: 0)}
        done = 0
        for fut in as_completed(futs):
            cid = futs[fut]
            try:
                novos[cid] = fut.result()
            except Exception as exc:
                novos[cid] = {"case_id": cid, "ok": False,
                              "error": f"{type(exc).__name__}: {exc}"}
            done += 1
            if done % 25 == 0 or done == len(ids):
                print(f"  [{done}/{len(ids)}]", flush=True)

    CAMPOS = ("mae", "maxerr", "rmse", "resid_std", "final_pred", "ratio")
    diffs = []
    for cid in ids:
        a, n = antigo.get(cid), novos.get(cid)
        if not (isinstance(a, dict) and a.get("ok")):
            diffs.append((cid, "sem baseline ok no store")); continue
        if not (isinstance(n, dict) and n.get("ok")):
            diffs.append((cid, f"re-sim falhou: {n.get('error')}")); continue
        for c in CAMPOS:
            if a.get(c) != n.get(c):
                diffs.append((cid, f"{c}: {a.get(c)!r} != {n.get(c)!r}"))
                break
    g1a_pass = not diffs
    res["G1a_G2a"] = dict(n=len(ids), n_diffs=len(diffs),
                          diffs=diffs[:40], PASS=g1a_pass)
    print(f"[G1a] paridade exata: diffs={len(diffs)} PASS={g1a_pass}", flush=True)

    # ---------- inventário L7 (G2b, informativo) ----------
    com_implied = [cid for cid, n in novos.items()
                   if isinstance(n.get("l7_check"), dict)
                   and n["l7_check"].get("implied_J_per_mm3") is not None]
    fora = [cid for cid in com_implied
            if novos[cid]["l7_check"].get("in_bound") is False]
    res["L7"] = dict(n_com_implied=len(com_implied), n_fora_banda=len(fora),
                     fora_banda=sorted(fora)[:20])
    print(f"[L7] implied em {len(com_implied)} casos; fora da banda: "
          f"{len(fora)}", flush=True)

    verdict = "PASS" if (g1b_pass and g1a_pass) else "FAIL"
    res["verdict"] = verdict

    if verdict == "PASS":
        from bolt_analysis_studio.validation.runner import CaseResult
        from bolt_analysis_studio.validation.store import ValidationStore
        store = ValidationStore()
        for cid, n in novos.items():
            if n.get("ok"):
                store.put(CaseResult.from_dict(n))
        for _ in range(200):
            try:
                store.save(); break
            except PermissionError:
                time.sleep(0.05)
        print("[store] gravado (single-writer, com l7_check)", flush=True)

    out = _ROOT / "New_Theory/f1_parity_gate_result.json"
    txt = json.dumps(res, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(out, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print(f"[gate] verdict={verdict} → {out}", flush=True)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
