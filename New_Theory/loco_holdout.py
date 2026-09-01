# -*- coding: utf-8 -*-
"""Leave-one-curve-out for the shared constants of a group (2026-08-31).

The reviewer's question this answers: the constants a configuration shares
between the curves of a group were fitted with those curves in view, so the
agreement of a curve with its own group's configuration is not independent
evidence. LOCO removes one curve from the group, re-fits the constants the
group frees on the remaining ones, and scores the removed curve.

The re-fit uses the paper's own protocol: log-space trust-region least squares
on the residual of the metric window, with a log-prior toward the adopted value
(lambda = 0.001) so a constant with nothing to gain stays where provenance put
it. Bounds are a factor `--span` around the adopted value.

Everything travels through the default-inert BAS_ABLATION hook of the runner:
the canonical configurations, the store and the engine are untouched.

    py -3.12 New_Theory/loco_holdout.py [--max-cycles 30000] [--max-consts 8]
                                        [--span 3] [--workers 5] [--groups A,B]

Output: New_Theory/holdout/loco.json
"""
from __future__ import annotations

import argparse
import collections
import datetime as _dt
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "New_Theory"))

SAIDA = RAIZ / "New_Theory" / "holdout"
CFG = RAIZ / "New_Theory" / "adopted_configs.json"
NAO_CONSTANTE = ("pack", "chain", "GA_member", "trim_n_max", "per_case")
LAMBDA = 0.001


def _grupos(comp, store, max_cycles, max_consts):
    """Multi-curve groups cheap enough to re-fit, with the constants they free."""
    from bolt_analysis_studio.validation import runner as rn
    cfg = json.loads(CFG.read_text(encoding="utf-8"))["sources"]
    por = collections.defaultdict(list)
    for r in comp:
        k = rn._adopted_for(r.source, r.case_id, r.validation_case.bolt_size)
        if k:
            por[k].append(r)
    out = {}
    for k, rs in por.items():
        if len(rs) < 2:
            continue
        c = (cfg.get(k) or {}).get("cfg") or {}
        livres = sorted(a for a, v in c.items()
                        if a not in NAO_CONSTANTE and isinstance(v, (int, float))
                        and float(v) > 0.0)
        ciclos = sum(store[r.case_id]["config_used"]["n_max"] for r in rs)
        if not livres or ciclos > max_cycles or len(livres) > max_consts:
            continue
        out[k] = {"curvas": [r.case_id for r in rs],
                  "constantes": livres,
                  "adotado": {a: float(c[a]) for a in livres},
                  "ciclos": int(ciclos)}
    return out


def _sim(cid, overrides):
    """One curve under one set of constants, through the ablation hook."""
    from bolt_analysis_studio.validation import runner as rn
    from bolt_analysis_studio.validation.case_registry import record
    antes = os.environ.get(rn._ABL_ENV)
    os.environ[rn._ABL_ENV] = json.dumps({"overrides": overrides})
    try:
        r = rn.simulate_case(record(cid))
        return (float(r.mae), float(r.maxerr), float(r.resid_std),
                list(r.metric_pred), list(r.metric_data))
    finally:
        if antes is None:
            os.environ.pop(rn._ABL_ENV, None)
        else:
            os.environ[rn._ABL_ENV] = antes


def _fold(args):
    """One LOCO fold: re-fit on `treino`, score `teste`."""
    from scipy.optimize import least_squares
    grupo, nomes, adotado, treino, teste, span, max_nfev = args
    t0 = time.time()
    log_ad = np.array([np.log(adotado[n]) for n in nomes])

    def residuos(x):
        ov = {n: float(np.exp(v)) for n, v in zip(nomes, x)}
        res = []
        for cid in treino:
            _, _, _, pred, dado = _sim(cid, ov)
            e = np.asarray(pred, float) - np.asarray(dado, float)
            res.extend(e / np.sqrt(max(len(e), 1) * len(treino)))
        res.extend(np.sqrt(LAMBDA) * (x - log_ad))       # prior no valor adotado
        return np.asarray(res)

    lo, hi = log_ad - np.log(span), log_ad + np.log(span)
    sol = least_squares(residuos, log_ad, bounds=(lo, hi), method="trf",
                        max_nfev=max_nfev, xtol=1e-4, ftol=1e-4, diff_step=0.1)
    ov = {n: float(np.exp(v)) for n, v in zip(nomes, sol.x)}
    mae_h, mx_h, sd_h, *_ = _sim(teste, ov)
    mae_i, mx_i, sd_i, *_ = _sim(teste, adotado)         # in-fit, para comparar
    return {"grupo": grupo, "teste": teste, "n_treino": len(treino),
            "constantes": nomes,
            "fator": {n: float(np.exp(sol.x[i]) / adotado[n])
                      for i, n in enumerate(nomes)},
            "mae_holdout": mae_h, "max_holdout": mx_h, "sres_holdout": sd_h,
            "mae_infit": mae_i, "max_infit": mx_i, "sres_infit": sd_i,
            "nfev": int(sol.nfev), "seconds": round(time.time() - t0, 1)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="loco_holdout")
    ap.add_argument("--max-cycles", type=int, default=30000)
    ap.add_argument("--max-consts", type=int, default=8)
    ap.add_argument("--span", type=float, default=3.0)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--groups", default=None)
    ap.add_argument("--nfev", type=int, default=None)
    args = ap.parse_args(argv)

    import build_annex_docx as A
    import bolt_analysis_studio.validation.report_html as rh
    from bolt_analysis_studio.validation import runner as rn
    comp, res, pisos, store, todos, res_all = A.carrega()
    grupos = _grupos(comp, store, args.max_cycles, args.max_consts)
    if args.groups:
        alvo = {g.strip() for g in args.groups.split(",")}
        grupos = {k: v for k, v in grupos.items() if k in alvo}
    tarefas = []
    for k, g in grupos.items():
        nfev = args.nfev or max(12, 6 * len(g["constantes"]))
        for cid in g["curvas"]:
            treino = [c for c in g["curvas"] if c != cid]
            tarefas.append((k, g["constantes"], g["adotado"], treino, cid,
                            args.span, nfev))
    print(f"[loco] {len(grupos)} groups, {len(tarefas)} folds, "
          f"{args.workers} workers", flush=True)
    for k, g in sorted(grupos.items()):
        print(f"   {k:34s} curves={len(g['curvas']):2d} "
              f"constants={len(g['constantes']):2d} cycles={g['ciclos']}",
          flush=True)

    t0 = time.time()
    linhas = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(_fold, t): t for t in tarefas}
        done = 0
        for fut in as_completed(futs):
            try:
                linhas.append(fut.result())
            except Exception as exc:
                t = futs[fut]
                linhas.append({"grupo": t[0], "teste": t[4],
                               "erro": f"{type(exc).__name__}: {exc}"})
            done += 1
            print(f"  [{done}/{len(tarefas)}] {time.time() - t0:.0f}s", flush=True)

    ok = [z for z in linhas if "erro" not in z]
    mh = np.array([z["mae_holdout"] for z in ok]) if ok else np.array([])
    mi = np.array([z["mae_infit"] for z in ok]) if ok else np.array([])
    # veredito das held-out sob o mesmo tripe
    porid = {r.case_id: r for r in comp}
    n_ok_h = 0
    for z in ok:
        r = porid[z["teste"]]
        lim = rh.limite_sres(r.source, pisos)
        n_ok_h += int(z["max_holdout"] <= rh.META_MAX
                      and z["mae_holdout"] <= rh.META_MAE
                      and z["sres_holdout"] <= lim)
    reg = {"generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
           "fingerprint": rn.engine_fingerprint(),
           "span": args.span, "lambda": LAMBDA,
           "n_grupos": len(grupos), "n_folds": len(ok),
           "n_erros": len(linhas) - len(ok),
           "grupos": {k: {"curvas": v["curvas"], "constantes": v["constantes"]}
                      for k, v in grupos.items()},
           "curvas_cobertas": sorted({z["teste"] for z in ok}),
           "mae_holdout_med": float(np.median(mh)) if len(mh) else None,
           "mae_infit_med": float(np.median(mi)) if len(mi) else None,
           "mae_holdout_p90": float(np.percentile(mh, 90)) if len(mh) else None,
           "n_holdout_no_tripe": n_ok_h,
           "seconds": round(time.time() - t0),
           "folds": linhas}
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "loco.json").write_text(json.dumps(reg, indent=1),
                                     encoding="utf-8", newline="")
    print(f"[loco] {len(ok)} folds in {time.time() - t0:.0f}s | "
          f"median MAE held-out {reg['mae_holdout_med']} against in-fit "
          f"{reg['mae_infit_med']} | {n_ok_h} of {len(ok)} held-out meet the "
          f"criterion -> {SAIDA / 'loco.json'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
