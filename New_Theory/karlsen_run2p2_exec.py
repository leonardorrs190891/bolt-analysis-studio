# -*- coding: utf-8 -*-
"""EXECUTOR do D-Y — gates G1..G5 do prereg `2026-08-06-karlsen-run2p2-base`.

NUNCA rodar com pipe (`| tail`): a licao do D-Q e' que o pipe bufferiza a
saida e um timeout deixa a adocao a meio SEM rastro. Redirecione para arquivo
ou leia direto.

    py -3.12 New_Theory/karlsen_run2p2_exec.py --json New_Theory/karlsen_run2p2_exec.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.runner as rn                  # noqa: E402
from bolt_analysis_studio.validation import report_html as rh        # noqa: E402
from bolt_analysis_studio.validation.case_registry import (          # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.runner import CaseResult        # noqa: E402

STORE_P = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"
ALVO = "karlsen2022_M30_HVtorqued_run14p2"
PRED = (0.0455, 0.0706, 0.0218)     # G1, +-0,015 por perna
TOL = 0.010
RISCO_G4 = ["karlsen2022_M30_HV_run6p2", "karlsen2022_M30_HV_run7p1",
            "karlsen2022_M42_HV_run21p0", ALVO]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    ap.add_argument("--write", action="store_true",
                    help="grava o store (so' apos os gates passarem)")
    a = ap.parse_args()

    store = json.loads(STORE_P.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    out: dict = {}

    # ---- instrumento: as 4 edicoes chegaram? -------------------------
    case = recs[ALVO].validation_case
    ov = rn._effective_overrides(recs[ALVO], {})
    print(f"instrumento  F0 = {case.initial_preload_N/1000:.0f} kN"
          f"  pct = {case.preload_percent_yield}"
          f"  k_ratchet = {ov.get('k_ratchet')}", flush=True)
    assert abs(case.initial_preload_N - 333000) < 1, "F0 nao editado"
    assert ov.get("k_ratchet") == 0.005, "k_ratchet nao chegou"
    assert (ALVO, "karlsen2022_M30_HV_run7p1") in [
        (p[0], p[1]) for p in rh._PARES_REPLICA_DECLARADOS], "par nao declarado"
    print("instrumento: 4/4 edicoes presentes\n", flush=True)

    # ---- re-simula TUDO ----------------------------------------------
    novos, dif = {}, []
    todos_recs = list(all_records())
    print(f"re-simulando {len(todos_recs)} casos "
          f"(G5 exige as 194 nao-KARLSEN bit-identicas)...", flush=True)
    for i, r in enumerate(todos_recs, 1):
        cid = r.case_id
        if i % 20 == 0:
            print(f"  ... {i}/{len(todos_recs)}", flush=True)
        res = rn.simulate_case(r)
        if not res.ok:
            print(f"  !! {cid}: {res.error}", flush=True)
            continue
        novos[cid] = res
        old = store.get(cid)
        if old and old.get("mae") is not None:
            d = max(abs(res.mae - old["mae"]), abs(res.maxerr - old["maxerr"]),
                    abs(res.resid_std - old["resid_std"]))
            if d > 1e-12:
                dif.append((cid, round(d, 6)))
    print(f"re-simuladas: {len(novos)}", flush=True)

    # ---- G5 isolamento -----------------------------------------------
    fora = [d for d in dif if d[0] != ALVO]
    g5 = not fora
    print(f"\nG5 isolamento: {'PASSA' if g5 else 'FALHA'}"
          f"  (mudaram: {[d[0] for d in dif]})", flush=True)
    out["G5"] = dict(passa=g5, mudaram=dif)

    # ---- G1 predicao ---------------------------------------------------
    r = novos[ALVO]
    got = (r.mae, r.maxerr, r.resid_std)
    d1 = [abs(g - p) for g, p in zip(got, PRED)]
    g1 = all(x <= TOL for x in d1)
    print(f"\nG1 predicao  medido {got[0]:.4f}/{got[1]:.4f}/{got[2]:.4f}"
          f"  previsto {PRED[0]:.4f}/{PRED[1]:.4f}/{PRED[2]:.4f}"
          f"  desvio max {max(d1):.4f}  -> {'PASSA' if g1 else 'FALHA'}",
          flush=True)
    out["G1"] = dict(passa=g1, medido=got, previsto=PRED, desvio=max(d1))

    # ---- G4 piso preservado + as 4 de risco ---------------------------
    pares = [(recs[c].source, CaseResult.from_dict(store[c]))
             for c in store if c in recs]
    pares_novo = [(recs[c].source, novos[c]) for c in novos]
    lim_old = rh.limite_sres("KARLSEN_2022", rh._pisos_medidos(pares))
    pisos_novo = rh._pisos_medidos(pares_novo)
    lim_new = rh.limite_sres("KARLSEN_2022", pisos_novo)
    g4a = lim_new >= 0.90 * lim_old
    print(f"\nG4 piso  limite_sres(KARLSEN) {lim_old:.4f} -> {lim_new:.4f}"
          f"  ({lim_new/lim_old*100:.1f} %)  -> {'PASSA' if g4a else 'FALHA'}",
          flush=True)
    fam_k = [f for f in pisos_novo["fam"] if "KARLSEN" in str(f[0]).upper()]
    for f in fam_k:
        print(f"    familia: {str(f[0]).encode('ascii','replace').decode()}"
              f"  n={f[1]}  MAE {f[2]:.4f}  mx {f[3]:.4f}  sig {f[4]:.4f}",
              flush=True)
    saiu = []
    for cid in RISCO_G4:
        res, old = novos[cid], store.get(cid, {})
        okn = (res.mae <= rh.META_MAE and res.maxerr <= rh.META_MAX
               and res.resid_std <= lim_new)
        oko = (old.get("mae", 9) <= rh.META_MAE
               and old.get("maxerr", 9) <= rh.META_MAX
               and old.get("resid_std", 9) <= lim_old)
        if oko and not okn:
            saiu.append(cid)
        print(f"    {cid:<42} {res.mae:.4f}/{res.maxerr:.4f}/{res.resid_std:.4f}"
              f"  antes {'IN' if oko else 'out'} -> depois "
              f"{'IN' if okn else 'OUT'}", flush=True)
    g4 = g4a and not saiu
    print(f"  G4 -> {'PASSA' if g4 else 'FALHA ' + str(saiu)}", flush=True)
    out["G4"] = dict(passa=g4, lim_old=lim_old, lim_new=lim_new, saiu=saiu)

    # ---- G2 parcimonia --------------------------------------------------
    kr7 = 0.005
    tri = (r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX
           and r.resid_std <= lim_new)
    g2 = tri and ov.get("k_ratchet") == kr7
    print(f"\nG2 parcimonia: passa o tripe com o k_ratchet DA run7p1 "
          f"({kr7}) -> {'PASSA' if g2 else 'FALHA'}", flush=True)
    out["G2"] = dict(passa=g2, tripe=bool(tri), k_ratchet=ov.get("k_ratchet"))

    # ---- censo -----------------------------------------------------------
    def _censo(src_res, pisos):
        """⚠️ USA `rh.sres_para_censo`, nunca `resid_std` cru.

        A 1a versao deste helper lia `res.resid_std` direto e devolvia **142**
        onde o report diz 139 — e a diferenca nao vinha do D-Y: rodada sobre o
        store ANTIGO dava 142 tambem. Sao as 3 curvas `n<6` (regra assinada em
        2026-08-01, sigma sem suporte estatistico e' NAO-JULGAVEL), que o
        helper canonico exclui e a leitura crua contava. Mesma armadilha que o
        CLAUDE.md registra para `limite_sres`, um nivel adiante: a regra se
        PERGUNTA ao helper, nunca se reimplementa.
        """
        n = 0
        for cid, res in src_res.items():
            if not rh.caso_comparavel(recs[cid].source, cid):
                continue
            sd = rh.sres_para_censo(res)
            if sd is None:            # n<6 -> fora do tripe por construcao
                continue
            L = rh.limite_sres(recs[cid].source, pisos)
            if (res.mae <= rh.META_MAE and res.maxerr <= rh.META_MAX
                    and sd <= L):
                n += 1
        return n
    c_new = _censo(novos, pisos_novo)
    print(f"\ncenso (tripe estrito) apos D-Y: {c_new}", flush=True)
    out["censo"] = c_new

    todos = g1 and g2 and g4 and g5
    print(f"\n=== VEREDICTO: {'ADOTA' if todos else 'NAO ADOTA / ROLLBACK'} ===",
          flush=True)
    out["veredicto"] = "ADOTA" if todos else "NAO"

    if a.write and todos:
        fp = rn.engine_fingerprint()
        for cid, res in novos.items():
            d = res.to_dict()
            d["engine_fingerprint"] = fp
            store[cid] = d
        STORE_P.write_text(json.dumps(store, indent=1), encoding="utf-8")
        print(f"store GRAVADO ({len(novos)} entradas, fingerprint {fp})",
              flush=True)
        out["store_gravado"] = True
        out["fingerprint"] = fp

    if a.json:
        a.json.write_text(json.dumps(out, indent=1, default=float),
                          encoding="utf-8")
        print(f"json -> {a.json}", flush=True)
    return 0 if todos else 1


if __name__ == "__main__":
    raise SystemExit(main())
