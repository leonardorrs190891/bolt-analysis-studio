# -*- coding: utf-8 -*-
"""F4 — Painel R5 (prereg-2: docs/superpowers/specs/
2026-07-22-f4-l1v2-prereg2-r5-transversal.md). Rota TRANSVERSAL do flanco.

Receitas per-fonte por LEITURA (tr_loose_gain=0 zero-rotacao; K_archard=0
SEM/EDX flanco; C_creep=0 atribuicao; emb lido L24 do Estagio I paper-stated)
+ 5 numeros fitados: {k_zinc, s_crit_zinc}, {k_dlc}, {k_z18}, {k_z19}.
Trim declarado ANTES: liu2020 0,4mm (cauda de trinca, regra taxa>3x mediana
estagio II, changepoint auditavel).

Uso: python New_Theory/f4_r5_panel.py [--workers N]
Saida: New_Theory/f4_r5_panel_result.json
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

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

PREREG = "docs/superpowers/specs/2026-07-22-f4-l1v2-prereg2-r5-transversal.md"

ZINC_AMP = ["liu2020_fig9_zinc_AF0.1mm_P0-18kN", "liu2020_fig9_zinc_AF0.2mm_P0-18kN",
            "liu2020_fig9_zinc_AF0.3mm_P0-18kN", "liu2020_fig9_zinc_AF0.4mm_P0-18kN"]
ZINC_P0 = ["liu2020_fig5b_zinc_P0-12kN_AF0.2mm", "liu2020_fig5b_zinc_P0-18kN_AF0.2mm",
           "liu2020_fig5b_zinc_P0-24kN_AF0.2mm"]
DLC = ["liu2020_fig15_DLC_P0-18kN_AF0.2mm", "liu2020_fig15_DLC_P0-19.28kN_AF0.2mm"]
Z18_FIT = ["zhang18_fig13_14kN_preload_vs_cycles", "zhang18_fig13_20kN_preload_vs_cycles",
           "zhang18_fig13_26kN_preload_vs_cycles"]
Z18_ALL = Z18_FIT + [
    "zhang18_fig2_test1_20kN_1e3cyc_preload_vs_cycles",
    "zhang18_fig2_test2_20kN_1e4cyc_preload_vs_cycles",
    "zhang18_fig2_test3_20kN_1e5cyc_preload_vs_cycles",
    "zhang18_fig2_test4_20kN_5e5cyc_preload_vs_cycles",
    "zhang18_fig16_with_locker_preload_vs_cycles",
    "zhang18_fig16_without_locker_preload_vs_cycles"]
Z19_FIT = ["zhang19_fig4_2e5cyc_Test10to12_preload_vs_cycles"]
Z19_ALL = ["zhang19_fig4_1e3cyc_Test1to3_preload_vs_cycles",
           "zhang19_fig4_1e4cyc_Test4to6_preload_vs_cycles",
           "zhang19_fig4_1e5cyc_Test7to9_preload_vs_cycles"] + Z19_FIT
ALL22 = ZINC_AMP + ZINC_P0 + DLC + Z18_ALL + Z19_ALL

# ---------------------------------------------------------------------------
# Leitura L24 (emb do Estagio I paper-stated) + N_emb da escala do Estagio I
# (apparatus_notes/{zhang,liu2020}.md — ver prereg-2, "Receitas per-fonte").
# ---------------------------------------------------------------------------
STAGE1_DROP = {"zhang18": 0.059,   # metade da perda total (fig13 20kN: 11,8%)
               "zhang19": 0.060,   # paper: 6% de 10 kN em ~300 ciclos
               "liu2020": 0.035}   # 2,5% (fig5a) + ~1% micro-transiente
N_EMB = {"zhang18": 150.0, "zhang19": 150.0, "liu2020": 300.0}
F0_REF = {"zhang18": 20e3, "zhang19": 10e3, "liu2020": 18e3}

K_GRID = [10 ** e for e in np.linspace(-15.0, -12.0, 13)]
SC_GRID = [0.0, 1e-5, 2e-5, 4e-5, 7e-5, 1.1e-4, 1.6e-4]   # m (slip 0,07-0,37mm)


def _emb_um(src: str, k_b: float) -> float:
    from bolt_analysis_studio.calibration.provenance import (
        emb_depth_from_early_drop)
    emb_m, _prov = emb_depth_from_early_drop(STAGE1_DROP[src], F0_REF[src], k_b)
    return float(emb_m * 1e6)


def _recipe(emb_um: float, n_emb: float, extra: dict) -> dict:
    # "K_archard=0" do prereg = bearing wear OFF por atribuicao; a expressao
    # mecanica pos-Estagio-B e' k_wear_spec=0 (canal canonico; o shared
    # congela k_wear_spec=5e-14 — sem zera-lo o WearLoss segue vivo e o
    # colapso espurio continua, visto no smoke) + K_archard=0 (fallback K/H).
    base = dict(flank_wear_on=1.0, flank_transverse_on=1.0, flank_amp_exp=1.5,
                tr_loose_gain=0.0, k_wear_spec=0.0, K_archard=0.0,
                C_creep=0.0, emb_um=emb_um, N_emb=n_emb)
    base.update(extra)
    return base


def _sandbox(theta: dict, trim_04: float | None) -> str:
    """adopted_configs sandbox com os grupos do prereg-2.
    theta = {k_zinc, sc_zinc, k_dlc, k_z18, k_z19} (None = fonte fora)."""
    d = json.loads(io.open(_ROOT / "New_Theory/adopted_configs.json",
                           encoding="utf-8").read())
    src = d["sources"]

    def _put(key, cfg):
        src[key] = {"cfg": cfg, "prov": {"_": "F4 prereg-2 sandbox"},
                    "verdict": "SANDBOX f4_r5_panel"}

    if theta.get("k_zinc") is not None:
        cfg = _recipe(theta["emb_liu"], N_EMB["liu2020"],
                      dict(k_wear_flank=theta["k_zinc"],
                           flank_s_crit=theta["sc_zinc"]))
        if trim_04:
            cfg["trim_n_max"] = {"af0.4mm": float(trim_04)}
        _put("LIU_2020_WEAR", cfg)
    if theta.get("k_dlc") is not None:
        _put("LIU_2020_WEAR_dlc",
             _recipe(theta["emb_liu"], N_EMB["liu2020"],
                     dict(k_wear_flank=theta["k_dlc"],
                          flank_s_crit=theta["sc_zinc"])))
    if theta.get("k_z18") is not None:
        base18 = _recipe(theta["emb_z18"], N_EMB["zhang18"],
                         dict(k_wear_flank=theta["k_z18"], flank_s_crit=0.0))
        _put("ZHANG_2018", base18)
        # fig16 with-locker: locker SEPARA os flancos (paper) -> rota OFF.
        # Idioma de tokens: fig16 casa AMBOS os casos fig16; o grupo
        # without_locker (2 tokens) vence p/ o caso without -> rota ON la.
        cfg16 = dict(base18); cfg16["flank_transverse_on"] = 0.0
        _put("ZHANG_2018_fig16", cfg16)
        _put("ZHANG_2018_without_locker", dict(base18))
    if theta.get("k_z19") is not None:
        _put("ZHANG_2019",
             _recipe(theta["emb_z19"], N_EMB["zhang19"],
                     dict(k_wear_flank=theta["k_z19"], flank_s_crit=0.0)))

    fd, p = tempfile.mkstemp(suffix=".json", prefix="f4r5_")
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
    r = simulate_case(record(cid), now="f4-r5")
    return {"tag": tag, "case_id": cid, "mae": r.mae, "maxerr": r.maxerr,
            "final_pred": r.final_pred, "final_data": r.final_data,
            "ok": r.ok, "err": r.error}


def _pool_run(tarefas, workers, label):
    print(f"[{label}] {len(tarefas)} sims", flush=True)
    out = {}
    with ProcessPoolExecutor(max_workers=workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, t): t for t in tarefas}
        done = 0
        for fut in as_completed(futs):
            r = fut.result()
            out.setdefault(r["tag"], {})[r["case_id"]] = r
            done += 1
            if done % 40 == 0 or done == len(tarefas):
                print(f"  [{done}/{len(tarefas)}]", flush=True)
    return out


def _tripe(res_list):
    """(n_pass, mediana_mae, pior_maxerr) de uma lista de resultados."""
    ok = [r for r in res_list if r["ok"] and r["mae"] is not None]
    if not ok:
        return 0, 9.9, 9.9
    n_pass = sum(1 for r in ok
                 if r["mae"] < 0.1 and (r["maxerr"] or 9) < 0.1)
    return (n_pass, float(np.median([r["mae"] for r in ok])),
            float(max(r["maxerr"] or 9 for r in ok)))


def _trim04_from_csv() -> dict:
    import csv
    p = (_ROOT / "BAS_V2_papers/F. Rodada 5 (limitacoes 2026-07-16)/"
         "digitized_csv/liu2020_fig9_zinc_AF0.4mm_P0-18kN.csv")
    rows = [r for r in csv.reader(io.open(p, encoding="utf-8")) if r]
    try:
        float(rows[0][0])
    except ValueError:
        rows = rows[1:]
    x = np.array([float(r[0]) for r in rows])
    y = np.array([float(r[1]) for r in rows]) / 100.0     # R_F% -> fracao
    rate = (y[:-1] - y[1:]) / np.maximum(x[1:] - x[:-1], 1e-9)
    stage2 = x[:-1] >= 1000.0
    med = float(np.median(rate[stage2]))
    # contigua ate o fim: anda de tras p/ frente enquanto taxa > 3x mediana
    i = len(rate) - 1
    while i >= 0 and stage2[i] and rate[i] > 3.0 * med:
        i -= 1
    n_trim = float(x[i + 1])
    return dict(n_trim=n_trim, mediana_taxa_estagioII=med,
                pontos_cortados=int(len(rate) - 1 - i),
                nota="regra F3: taxa local > 3x mediana do Estagio II, "
                     "contigua ate o fim (cauda de trinca, paper sec3.1.2)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    t0 = time.time()

    # k_b do rig M12 (p/ leitura de emb)
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.inputs import (geometry_for_case,
                                                        inputs_for)
    rec0 = record(ZINC_AMP[1])
    inp0 = inputs_for(rec0.validation_case)
    geom0 = geometry_for_case(rec0.validation_case,
                              grip_mm=inp0["grip_mm"]["value"],
                              E=(inp0.get("E") or {}).get("value"))
    k_b = float(geom0.k_b)
    emb = {"liu2020": _emb_um("liu2020", k_b), "zhang18": _emb_um("zhang18", k_b),
           "zhang19": _emb_um("zhang19", k_b)}
    trim04 = _trim04_from_csv()
    print(f"[r5] k_b={k_b:.3e}  emb_um={ {k: round(v,2) for k,v in emb.items()} }  "
          f"trim04={trim04['n_trim']:.0f}", flush=True)

    def theta_base(**kw):
        th = dict(k_zinc=None, sc_zinc=0.0, k_dlc=None, k_z18=None,
                  k_z19=None, emb_liu=emb["liu2020"], emb_z18=emb["zhang18"],
                  emb_z19=emb["zhang19"])
        th.update(kw)
        return th

    # ---- FASE A1: grid 2D zinc (amplitude sweep, com trim no 0,4mm) --------
    tarefas, sbs = [], []
    for k in K_GRID:
        for sc in SC_GRID:
            sb = _sandbox(theta_base(k_zinc=float(k), sc_zinc=float(sc)),
                          trim04["n_trim"])
            sbs.append(sb)
            tag = f"zinc|k={k:.3e}|sc={sc:.1e}"
            tarefas.extend((cid, sb, tag) for cid in ZINC_AMP)
    grade = _pool_run(tarefas, args.workers, "A1 zinc 2D")
    for sb in sbs:
        try:
            os.unlink(sb)
        except OSError:
            pass
    aval = {}
    for tag, g in grade.items():
        n_pass, med, worst = _tripe(list(g.values()))
        aval[tag] = dict(n_pass=n_pass, mediana=med, pior_maxerr=worst)
    best_zinc = max(aval, key=lambda t: (aval[t]["n_pass"], -aval[t]["mediana"]))
    k_zinc = float(best_zinc.split("|")[1].split("=")[1])
    sc_zinc = float(best_zinc.split("|")[2].split("=")[1])
    print(f"[A1] melhor {best_zinc}: {aval[best_zinc]}", flush=True)

    # ---- FASE A2: DLC 1D + zhang18 1D + zhang19 1D (paralelo unico) --------
    tarefas, sbs = [], []
    for k in K_GRID:
        sb = _sandbox(theta_base(k_zinc=k_zinc, sc_zinc=sc_zinc,
                                 k_dlc=float(k)), trim04["n_trim"])
        sbs.append(sb)
        tarefas.extend((cid, sb, f"dlc|k={k:.3e}") for cid in DLC)
    for k in K_GRID:
        sb = _sandbox(theta_base(k_z18=float(k)), None)
        sbs.append(sb)
        tarefas.extend((cid, sb, f"z18|k={k:.3e}") for cid in Z18_FIT)
    for k in K_GRID:
        sb = _sandbox(theta_base(k_z19=float(k)), None)
        sbs.append(sb)
        tarefas.extend((cid, sb, f"z19|k={k:.3e}") for cid in Z19_FIT)
    grade2 = _pool_run(tarefas, args.workers, "A2 dlc+z18+z19 1D")
    for sb in sbs:
        try:
            os.unlink(sb)
        except OSError:
            pass
    best = {}
    for pref in ("dlc", "z18", "z19"):
        cand = {t: _tripe(list(g.values()))
                for t, g in grade2.items() if t.startswith(pref)}
        bt = max(cand, key=lambda t: (cand[t][0], -cand[t][1]))
        best[pref] = dict(k=float(bt.split("=")[1]), n_pass=cand[bt][0],
                          mediana=cand[bt][1], pior_maxerr=cand[bt][2])
        print(f"[A2] {pref}: k={best[pref]['k']:.3e} "
              f"n_pass={best[pref]['n_pass']} med={best[pref]['mediana']:.4f} "
              f"pior_maxerr={best[pref]['pior_maxerr']:.4f}", flush=True)

    # ---- FASE B: avaliacao final dos 22 no theta vencedor ------------------
    theta_fin = theta_base(k_zinc=k_zinc, sc_zinc=sc_zinc,
                           k_dlc=best["dlc"]["k"], k_z18=best["z18"]["k"],
                           k_z19=best["z19"]["k"])
    sb = _sandbox(theta_fin, trim04["n_trim"])
    tarefas = [(cid, sb, "FINAL") for cid in ALL22]
    final = _pool_run(tarefas, args.workers, "B final 22")["FINAL"]
    try:
        os.unlink(sb)
    except OSError:
        pass

    casos = {}
    n_pass = 0
    for cid in ALL22:
        r = final[cid]
        ok_tripe = bool(r["ok"] and r["mae"] is not None and r["mae"] < 0.1
                        and (r["maxerr"] or 9) < 0.1)
        n_pass += ok_tripe
        casos[cid] = dict(mae=r["mae"], maxerr=r["maxerr"],
                          final_pred=r["final_pred"], final_data=r["final_data"],
                          tripe=ok_tripe, err=r["err"])
        print(f"  {'PASS' if ok_tripe else 'FAIL'} {cid}: "
              f"mae={r['mae'] and round(r['mae'],4)} "
              f"maxerr={r['maxerr'] and round(r['maxerr'],4)}", flush=True)

    verdict = "PASS-G4b-v2" if n_pass == 22 else f"FAIL-G4b-v2 ({n_pass}/22)"
    out = dict(prereg=PREREG, emb_um=emb, N_emb=N_EMB,
               stage1_drop=STAGE1_DROP, trim_04=trim04,
               grade_zinc=aval, best_zinc=best_zinc, fitted=dict(
                   k_zinc=k_zinc, sc_zinc=sc_zinc, k_dlc=best["dlc"]["k"],
                   k_z18=best["z18"]["k"], k_z19=best["z19"]["k"]),
               grade_A2={t: list(_tripe(list(g.values())))
                         for t, g in grade2.items()},
               casos=casos, n_pass=n_pass, verdict=verdict,
               runtime_s=time.time() - t0)
    p = _ROOT / "New_Theory/f4_r5_panel_result.json"
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"[r5] {verdict}  ({time.time() - t0:.0f}s) -> {p}", flush=True)
    return 0 if n_pass == 22 else 1


if __name__ == "__main__":
    raise SystemExit(main())
