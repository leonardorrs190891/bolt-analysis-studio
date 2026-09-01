# -*- coding: utf-8 -*-
"""Robustness checks for the paper (2026-08-28): items 1 to 3 of the list.

Everything here is recomputed at build time from the canonical store, the
adopted configurations and the git history; nothing is typed by hand.

  item 3  varredura_criterio  census as a function of each acceptance limit
                              (and of the source-floor rule), with the gate
                              that the nominal point reproduces the census
                              the report itself computes;
  item 2  holdout_temporal    curves whose serving configuration was last
                              changed BEFORE the curve entered the repository
                              (configuration-blind predictions), read from
                              the commit history of adopted_configs.json and
                              of every reference CSV;
  item 1  carrega_ablacao     loader for New_Theory/ablation/ablation_*.json
                              (written by ablation_run.py) with census, R^2
                              and verdict flips against the baseline store.

Reused by build_paper_docx.py; run directly for a console summary:

    py -3.12 New_Theory/robustness_checks.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "New_Theory"))

import bolt_analysis_studio.validation.report_html as rh          # noqa: E402
from bolt_analysis_studio.validation import runner as rn          # noqa: E402
from bolt_analysis_studio.validation.runner import CaseResult     # noqa: E402

CFG_REL = "New_Theory/adopted_configs.json"
SHARED_REL = "New_Theory/joint_calibrations.json"
ABL_DIR = RAIZ / "New_Theory" / "ablation"
META_KEYS = ("prov", "verdict")      # entry keys that never change a prediction


# --------------------------------------------------------------------------- #
# item 3 — sensitivity of the census to the acceptance limits
# --------------------------------------------------------------------------- #
def piso_fonte(pisos, src):
    p = (pisos.get("por_fonte") or {}).get(src) if pisos else None
    return float(p[2]) if p else None


def veredito(rr, lim_max, lim_mae, lim_sig, floor):
    """`rh._tripe_ok` with variable limits. `floor=None` = no source-floor rule."""
    if not (rr and rr.ok and rr.mae is not None and rr.maxerr is not None
            and rr.resid_std is not None):
        return None
    md = getattr(rr, "metric_data", None)
    if md and len(md) < rh.N_MIN_SRES:
        return False
    lim = lim_sig if floor is None else max(lim_sig, floor)
    return bool(rr.maxerr <= lim_max and rr.mae <= lim_mae and rr.resid_std <= lim)


def varredura_criterio(comp, res, pisos):
    nom = (rh.META_MAX, rh.META_MAE, rh.META_SRES)

    def censo(lm, la, ls, com_piso=True):
        return sum(1 for r in comp
                   if veredito(res[r.case_id], lm, la, ls,
                               piso_fonte(pisos, r.source) if com_piso else None))

    n_nom = censo(*nom)
    n_rh = sum(1 for r in comp
               if rh._tripe_ok(res[r.case_id], rh.limite_sres(r.source, pisos)))
    if n_nom != n_rh:                      # the sweep must speak the report's language
        raise AssertionError(f"criterion sweep {n_nom} != report census {n_rh}")

    sig = [round(float(x), 4) for x in np.arange(0.015, 0.0401, 0.0025)]
    mae = [round(float(x), 4) for x in np.arange(0.030, 0.0701, 0.005)]
    mx = [round(float(x), 4) for x in np.arange(0.080, 0.1501, 0.010)]
    k = [round(float(x), 2) for x in np.arange(0.70, 1.501, 0.05)]
    out = {
        "n": len(comp), "n_nominal": n_nom, "nominal": nom,
        "n_sem_piso": censo(*nom, com_piso=False),
        "sigma": {"x": sig,
                  "com_piso": [censo(nom[0], nom[1], s) for s in sig],
                  "sem_piso": [censo(nom[0], nom[1], s, False) for s in sig]},
        "mae": {"x": mae, "y": [censo(nom[0], a, nom[2]) for a in mae]},
        "max": {"x": mx, "y": [censo(x, nom[1], nom[2]) for x in mx]},
        "stretch": {"x": k, "y": [censo(nom[0] * f, nom[1] * f, nom[2] * f) for f in k]},
    }
    # curves near a boundary: binding leg within +-10 % of its limit
    perto = 0
    for r in comp:
        rr = res[r.case_id]
        if not (rr and rr.ok and rr.resid_std is not None):
            continue
        ls = rh.limite_sres(r.source, pisos)
        mult = max(rr.maxerr / nom[0], rr.mae / nom[1], rr.resid_std / ls)
        if 0.9 <= mult <= 1.1:
            perto += 1
    out["n_perto_10pct"] = perto

    def em(d, x):
        return d["y"][d["x"].index(x)] if x in d["x"] else None
    out["pontos"] = {
        "sigma_0.020": out["sigma"]["com_piso"][sig.index(0.02)],
        "sigma_0.030": out["sigma"]["com_piso"][sig.index(0.03)],
        "sigma_0.035": out["sigma"]["com_piso"][sig.index(0.035)],
        "mae_0.040": em(out["mae"], 0.04), "mae_0.060": em(out["mae"], 0.06),
        "max_0.080": em(out["max"], 0.08), "max_0.150": em(out["max"], 0.15),
        "stretch_0.80": em(out["stretch"], 0.8), "stretch_1.20": em(out["stretch"], 1.2),
    }
    return out


def fig_varredura(sw, salva):
    import matplotlib.pyplot as plt
    f, axs = plt.subplots(2, 2, figsize=(7.4, 5.4), layout="constrained")
    n = sw["n"]
    todos = (sw["sigma"]["com_piso"] + sw["sigma"]["sem_piso"] + sw["mae"]["y"]
             + sw["max"]["y"] + sw["stretch"]["y"])
    ylim = (min(todos) - 5, max(todos) + 8)   # one scale: a flat leg must LOOK flat

    def painel(ax, x, ys, rotulos, xnom, titulo, xlabel):
        ax.set_ylim(*ylim)
        for y, lab, st in zip(ys, rotulos, ("-", "--")):
            ax.plot(x, y, st, marker="o", ms=3.5, lw=1.4, label=lab)
        ax.axvline(xnom, color="0.4", lw=0.8, ls=":")
        ax.axhline(sw["n_nominal"], color="0.4", lw=0.8, ls=":")
        ax.set_title(titulo, fontsize=9)
        ax.set_xlabel(xlabel, fontsize=8)
        ax.set_ylabel(f"curves accepted (of {n})", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.25)
        if len(ys) > 1:
            ax.legend(fontsize=7, frameon=False)
    painel(axs[0, 0], sw["sigma"]["x"], [sw["sigma"]["com_piso"], sw["sigma"]["sem_piso"]],
           ["with source floor", "global limit only"], sw["nominal"][2],
           "(a) third leg: residual standard deviation", r"$\sigma_{res}$ limit")
    painel(axs[0, 1], sw["mae"]["x"], [sw["mae"]["y"]], ["MAE"], sw["nominal"][1],
           "(b) second leg: mean absolute error", "MAE limit")
    painel(axs[1, 0], sw["max"]["x"], [sw["max"]["y"]], ["max|r|"], sw["nominal"][0],
           "(c) first leg: maximum residual", "max|r| limit")
    painel(axs[1, 1], sw["stretch"]["x"], [sw["stretch"]["y"]], ["all three"], 1.0,
           "(d) all three limits scaled together", "scale factor on the three limits")
    salva(f, "fig_criterion_sweep")


# --------------------------------------------------------------------------- #
# item 2 — temporal hold-out at configuration level
# --------------------------------------------------------------------------- #
def _git(*args) -> str:
    return subprocess.run(["git", *args], cwd=str(RAIZ), capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


def _consts(entry: dict) -> dict:
    """A group's constants: the entry minus provenance text and verdict."""
    return {k: v for k, v in entry.items() if k not in META_KEYS}


def _constantes_da_curva(entry: dict, case_id: str) -> dict:
    """What this curve actually runs on: the group entry minus provenance text
    and verdict, with `per_case` reduced to the tokens that match THIS case_id
    (the runner matches per-curve tokens by substring). A sibling's per-curve
    number changing does not count as a change for this curve."""
    c = {k: v for k, v in entry.items() if k not in META_KEYS and k != "per_case"}
    pc = entry.get("per_case") or {}
    c["per_case"] = {tok: v for tok, v in pc.items() if tok in case_id}
    return c


def versoes_configs():
    """Every committed version of adopted_configs.json, oldest first, parsed."""
    linhas = [l for l in _git("log", "--format=%H %ad", "--date=short", "--reverse",
                              "--", CFG_REL).splitlines() if l.strip()]
    out = []
    for l in linhas:
        h, d = l.split()
        try:
            cfg = json.loads(_git("show", f"{h}:{CFG_REL}"))
        except ValueError:
            continue
        out.append((d, h, cfg.get("sources") or {}))
    shared = _git("log", "-1", "--format=%ad", "--date=short", "--", SHARED_REL).strip()
    return out, shared


def digest_historico(versoes, shared, destino: Path | None = None):
    """Per-version digest of every configuration group (date, commit, sha256 of
    the constants), so the temporal analysis stays verifiable from a public
    repository that ships as a single-commit snapshot without the git history."""
    import hashlib
    destino = destino or HOLD_DIR / "config_history_digest.json"
    out = {"file": CFG_REL, "shared_block_last_change": shared,
           "note": ("Each entry lists, for one committed version of the configuration "
                    "file in the development repository, the first 12 hex digits of "
                    "the sha256 of every group's constants (entry minus provenance "
                    "text and verdict). A group's constants changed between two "
                    "versions when its digest changed."),
           "versions": []}
    for d, h, srcs in versoes:
        out["versions"].append({
            "date": d, "commit": h[:12],
            "groups": {k: hashlib.sha256(json.dumps(_consts(v), sort_keys=True,
                                                    ensure_ascii=False).encode("utf-8")
                                         ).hexdigest()[:12] for k, v in srcs.items()}})
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(out, indent=1), encoding="utf-8", newline="")
    return destino


def t_cfg_curva(versoes, key, case_id):
    """Date of the last commit that changed the constants THIS curve runs on."""
    prev, ultimo = None, None
    for d, _h, srcs in versoes:
        entry = srcs.get(key) if key else None
        c = _constantes_da_curva(entry, case_id) if entry else None
        if c != prev:
            ultimo = d
        prev = c
    return ultimo


def datas_csv(rel: str):
    first = _git("log", "--diff-filter=A", "--follow", "--format=%ad", "--date=short",
                 "--", rel).strip().splitlines()
    last = _git("log", "-1", "--format=%ad", "--date=short", "--", rel).strip()
    return (first[-1] if first else None), (last or None)


def holdout_temporal(comp, res, pisos, cache: Path | None = None):
    # cache key = last commit that touched an INPUT of this analysis (configs,
    # shared block, corpus CSVs), not HEAD: keyed by HEAD the versioned cache file
    # would change on every commit and lag the tree by one commit forever.
    head = _git("log", "-1", "--format=%H", "--", CFG_REL, SHARED_REL,
                "Models/CALIBRATION_AND_VALIDATION/curve_library",
                "BAS_V2_papers").strip()
    if cache and cache.exists():
        try:
            c = json.loads(cache.read_text(encoding="utf-8"))
            if c.get("head") == head:
                if not (HOLD_DIR / "config_history_digest.json").exists():
                    digest_historico(*versoes_configs())   # the digest ships with the release
                return c
        except ValueError:
            pass
    versoes, shared = versoes_configs()
    n_commits = len(versoes)
    digest_historico(versoes, shared)
    linhas = []
    for r in comp:
        rel = None
        if r.csv_path:
            try:
                rel = Path(r.csv_path).resolve().relative_to(RAIZ).as_posix()
            except ValueError:
                rel = None
        t_in, t_mod = datas_csv(rel) if rel else (None, None)
        key = rn._adopted_for(r.source, r.case_id, r.validation_case.bolt_size)
        t_cfg = t_cfg_curva(versoes, key, r.case_id) if key else None
        t_cfg = max(filter(None, [t_cfg, shared])) if (t_cfg or shared) else None
        rr = res[r.case_id]
        ok = rh._tripe_ok(rr, rh.limite_sres(r.source, pisos))
        linhas.append({"case_id": r.case_id, "source": r.source, "group": key,
                       "t_in": t_in, "t_mod": t_mod, "t_cfg": t_cfg,
                       "ok": bool(ok) if ok is not None else None,
                       "mae": rr.mae, "final_pred": rr.final_pred,
                       "final_data": rr.final_data,
                       "strict": bool(t_in and t_cfg and t_in > t_cfg),
                       "lenient": bool(t_mod and t_cfg and t_mod > t_cfg)})

    def resumo(sel):
        sel = list(sel)
        oks = [x for x in sel if x["ok"]]
        maes = [x["mae"] for x in sel if x["mae"] is not None]
        fp = np.array([x["final_pred"] for x in sel if x["final_pred"] is not None
                       and x["final_data"] is not None])
        fd = np.array([x["final_data"] for x in sel if x["final_pred"] is not None
                       and x["final_data"] is not None])
        r2 = (1 - np.sum((fp - fd) ** 2) / max(np.sum((fd - fd.mean()) ** 2), 1e-12)
              if len(fd) > 2 else None)
        return {"n": len(sel), "n_ok": len(oks),
                "pct": 100 * len(oks) / len(sel) if sel else None,
                "mae_med": float(np.median(maes)) if maes else None,
                "r2_final": float(r2) if r2 is not None else None,
                "sources": sorted({x["source"] for x in sel})}
    sem_data = [x for x in linhas if not x["t_in"]]
    out = {"head": head, "n_commits_cfg": n_commits, "shared_last": shared,
           "n_groups_dated": len({x["group"] for x in linhas if x["group"]}),
           "t_cfg_por_curva": sorted(x["t_cfg"] for x in linhas if x["t_cfg"]),
           "sem_data_git": [x["case_id"] for x in sem_data],
           "strict": resumo(x for x in linhas if x["strict"]),
           "lenient": resumo(x for x in linhas if x["lenient"]),
           "seen": resumo(x for x in linhas if x["t_in"] and not x["strict"]),
           "all": resumo(linhas),
           "por_fonte_strict": {}, "linhas": linhas}
    for x in linhas:
        if x["strict"]:
            d = out["por_fonte_strict"].setdefault(x["source"], {"n": 0, "n_ok": 0})
            d["n"] += 1
            d["n_ok"] += int(bool(x["ok"]))
    if cache:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(out, indent=1), encoding="utf-8", newline="")
    return out


# --------------------------------------------------------------------------- #
# item 1 — ablation loader
# --------------------------------------------------------------------------- #
ORDEM_ABL = ["stiffness_frozen", "open_loop", "no_embedding", "no_creep",
             "no_wear", "no_loosening", "no_damage"]
ROTULO_ABL = {
    "stiffness_frozen": "stiffness softening frozen (alpha_GW = 0)",
    "open_loop": "open loop: rates see F0 = F0,init",
    "no_embedding": "embedding removed",
    "no_creep": "creep removed",
    "no_wear": "wear and thread fretting removed",
    "no_loosening": "rotational loosening removed",
    "no_damage": "surface-damage state frozen (c_D = 0)",
}


def _resumo_res(comp, res_v, pisos, base_ok):
    oks, maes, fp, fd, flips_down, flips_up, changed = 0, [], [], [], 0, 0, 0
    for r in comp:
        rr = res_v.get(r.case_id)
        ok = rh._tripe_ok(rr, rh.limite_sres(r.source, pisos)) if rr else None
        oks += int(bool(ok))
        if rr and rr.mae is not None:
            maes.append(rr.mae)
        if rr and rr.final_pred is not None and rr.final_data is not None:
            fp.append(rr.final_pred)
            fd.append(rr.final_data)
        b = base_ok.get(r.case_id)
        if b is True and ok is not True:
            flips_down += 1
        if b is not True and ok is True:
            flips_up += 1
    fp, fd = np.array(fp), np.array(fd)
    r2 = (1 - np.sum((fp - fd) ** 2) / max(np.sum((fd - fd.mean()) ** 2), 1e-12)
          if len(fd) > 2 else None)
    return {"n_ok": oks, "mae_med": float(np.median(maes)) if maes else None,
            "r2_final": float(r2) if r2 is not None else None,
            "flips_down": flips_down, "flips_up": flips_up, "n_sim": len(maes)}


def carrega_ablacao(comp, res, pisos, pasta: Path = ABL_DIR):
    fp_now = rn.engine_fingerprint()
    base_ok = {r.case_id: rh._tripe_ok(res[r.case_id], rh.limite_sres(r.source, pisos))
               for r in comp}
    base = _resumo_res(comp, res, pisos, base_ok)
    base.update(variant="baseline", rotulo="full model (canonical store)",
                fingerprint_base=fp_now, stale=False, n_changed=0)
    linhas = [base]
    for nome in ORDEM_ABL:
        f = pasta / f"ablation_{nome}.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        res_v = {}
        for cid, rec in d["results"].items():
            try:
                res_v[cid] = CaseResult.from_dict(rec)
            except Exception:
                pass
        row = _resumo_res(comp, res_v, pisos, base_ok)
        row["n_changed"] = sum(1 for r in comp if r.case_id in res_v
                               and res_v[r.case_id].mae is not None
                               and res[r.case_id].mae is not None
                               and abs(res_v[r.case_id].mae - res[r.case_id].mae) > 1e-4)
        row.update(variant=nome, rotulo=ROTULO_ABL.get(nome, nome),
                   fingerprint_base=d.get("fingerprint_base"),
                   stale=d.get("fingerprint_base") != fp_now,
                   generated_at=d.get("generated_at"), seconds=d.get("seconds"),
                   n_err=sum(1 for v in d["results"].values() if not v.get("ok")))
        linhas.append(row)
    return linhas


def fig_ablacao(abl, salva):
    import matplotlib.pyplot as plt
    rows = abl
    f, ax = plt.subplots(figsize=(7.2, 0.42 * len(rows) + 1.3), layout="constrained")
    y = np.arange(len(rows))[::-1]
    vals = [r["n_ok"] for r in rows]
    cores = ["#2b6cb0"] + ["#b7791f"] * (len(rows) - 1)
    ax.barh(y, vals, color=cores, height=0.6)
    for yi, r in zip(y, rows):
        ax.text(r["n_ok"] + 1.5, yi, f"{r['n_ok']}  (median MAE {r['mae_med']:.3f})",
                va="center", fontsize=7.5)
    ax.set_yticks(y)
    tex = {"alpha_GW = 0": r"$\alpha_{GW} = 0$", "F0 = F0,init": r"$F_0 = F_{0,\mathrm{init}}$",
           "c_D = 0": r"$c_D = 0$"}          # mathtext only in the figure; tables stay plain
    def _tx(s):
        for k, v in tex.items():
            s = s.replace(k, v)
        return s
    ax.set_yticklabels([_tx(r["rotulo"]) for r in rows], fontsize=8)
    ax.axvline(rows[0]["n_ok"], color="0.3", lw=0.8, ls=":")
    ax.set_xlim(0, max(vals) * 1.45)
    ax.set_xlabel("curves meeting the three-leg criterion", fontsize=8)
    ax.tick_params(axis="x", labelsize=7)
    ax.grid(axis="x", alpha=0.25)
    salva(f, "fig_ablation")


# --------------------------------------------------------------------------- #
# item 2b — frozen-configuration prospective tests (frozen_config_holdout.py)
# --------------------------------------------------------------------------- #
HOLD_DIR = RAIZ / "New_Theory" / "holdout"


def _r2(fp, fd):
    fp, fd = np.array(fp, float), np.array(fd, float)
    if len(fd) < 3:
        return None
    return float(1 - np.sum((fp - fd) ** 2) / max(np.sum((fd - fd.mean()) ** 2), 1e-12))


def _tinha_config(caminho_cfg: Path, recs):
    """Which of these curves resolved to a group in the frozen file: the
    knowledge base is pointed at the file for the duration of the question."""
    import os
    antes = os.environ.get("BAS_ADOPTED_CONFIGS")
    os.environ["BAS_ADOPTED_CONFIGS"] = str(caminho_cfg)
    try:
        return {r.case_id: bool(rn._adopted_for(r.source, r.case_id,
                                                 r.validation_case.bolt_size))
                for r in recs}
    finally:
        if antes is None:
            os.environ.pop("BAS_ADOPTED_CONFIGS", None)
        else:
            os.environ["BAS_ADOPTED_CONFIGS"] = antes


def carrega_congelados(comp, res, pisos, pasta: Path = HOLD_DIR):
    """One row per frozen_<date>.json: census under the frozen configuration
    against today's census on the SAME curves, split into curves whose source
    already had a configuration at the freeze and curves that ran on the shared
    constants and handbook inputs alone (a-priori prediction)."""
    porid = {r.case_id: r for r in comp}
    saida = []
    for f in sorted(pasta.glob("frozen_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        h, data = d["freeze_commit"], d["freeze_date"]
        cfg_path = pasta / f"adopted_configs_{data}_{h[:7]}.json"
        if not cfg_path.exists():
            cfg_path.write_text(_git("show", f"{h}:{CFG_REL}"), encoding="utf-8",
                                newline="")
        recs = [porid[c] for c in d["results"] if c in porid]
        tinha = _tinha_config(cfg_path, recs)
        res_v = {}
        for cid, rec in d["results"].items():
            try:
                res_v[cid] = CaseResult.from_dict(rec)
            except Exception:
                pass

        def bloco(sel):
            oks_f = oks_h = 0
            maes_f, maes_h, fp_f, fp_h, fd = [], [], [], [], []
            for r in sel:
                rf, rt = res_v.get(r.case_id), res[r.case_id]
                ls = rh.limite_sres(r.source, pisos)
                oks_f += int(bool(rh._tripe_ok(rf, ls))) if rf else 0
                oks_h += int(bool(rh._tripe_ok(rt, ls)))
                if rf and rf.mae is not None:
                    maes_f.append(rf.mae)
                if rt.mae is not None:
                    maes_h.append(rt.mae)
                if rf and rf.final_pred is not None and rt.final_data is not None:
                    fp_f.append(rf.final_pred)
                    fp_h.append(rt.final_pred)
                    fd.append(rt.final_data)
            return {"n": len(sel), "ok_frozen": oks_f, "ok_today": oks_h,
                    "mae_frozen": float(np.median(maes_f)) if maes_f else None,
                    "mae_today": float(np.median(maes_h)) if maes_h else None,
                    "r2_frozen": _r2(fp_f, fd), "r2_today": _r2(fp_h, fd),
                    "sources": sorted({r.source for r in sel})}
        com = [r for r in recs if tinha[r.case_id]]
        sem = [r for r in recs if not tinha[r.case_id]]
        curvas = []
        for r in sorted(recs, key=lambda r: r.case_id):
            rf, rt = res_v.get(r.case_id), res[r.case_id]
            ls = rh.limite_sres(r.source, pisos)
            curvas.append({"case_id": r.case_id, "source": r.source,
                           "had_cfg": tinha[r.case_id],
                           "mae_frozen": rf.mae if rf else None, "mae_today": rt.mae,
                           "ok_frozen": bool(rh._tripe_ok(rf, ls)) if rf else False,
                           "ok_today": bool(rh._tripe_ok(rt, ls))})
        saida.append({"freeze_date": data, "freeze_commit": h[:7],
                      "n_groups_frozen": d["n_groups_frozen"],
                      "generated_at": d.get("generated_at"),
                      "n_err": sum(1 for v in d["results"].values() if not v.get("ok")),
                      "all": bloco(recs), "with_cfg": bloco(com), "prior": bloco(sem),
                      "curvas": curvas})
    return saida


def fig_congelados(fz, salva):
    import matplotlib.pyplot as plt
    f, ax = plt.subplots(figsize=(6.2, 3.4), layout="constrained")
    x = np.arange(len(fz))
    w = 0.36
    a = [z["all"]["ok_frozen"] for z in fz]
    b = [z["all"]["ok_today"] for z in fz]
    ax.bar(x - w / 2, a, w, color="#b7791f", label="configuration frozen at the date")
    ax.bar(x + w / 2, b, w, color="#2b6cb0", label="today's configuration")
    for xi, z in zip(x, fz):
        n = z["all"]["n"]
        ax.text(xi - w / 2, z["all"]["ok_frozen"] + 0.6, f"{z['all']['ok_frozen']}/{n}",
                ha="center", fontsize=7.5)
        ax.text(xi + w / 2, z["all"]["ok_today"] + 0.6, f"{z['all']['ok_today']}/{n}",
                ha="center", fontsize=7.5)
    ax.set_xticks(x)
    ax.set_xticklabels([f"frozen {z['freeze_date']}\n({z['n_groups_frozen']} configurations, "
                        f"{z['all']['n']} later curves)" for z in fz], fontsize=8)
    ax.set_ylabel("curves meeting the criterion", fontsize=8)
    ax.tick_params(axis="y", labelsize=7)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=7.5, frameon=False)
    salva(f, "fig_frozen_config")


# --------------------------------------------------------------------------- #
# paper extras (2026-08-31): prediction share, sweep ordering, digitisation MC,
# baselines, window edge, identifiability grid — all recomputed at build time.
# --------------------------------------------------------------------------- #
def parcela_predicao(comp):
    """Ownership split of the census curves: per-curve constants, single-curve
    configurations, shared-configuration-only curves, and default-only curves.
    Reads the current configuration file; no history involved."""
    import collections
    cfgs = json.loads((RAIZ / CFG_REL).read_text(encoding="utf-8"))["sources"]
    por_grupo = collections.defaultdict(list)
    proprio = {}
    for r in comp:
        key = rn._adopted_for(r.source, r.case_id, r.validation_case.bolt_size)
        por_grupo[key].append(r.case_id)
        pc = ((cfgs.get(key) or {}).get("cfg") or {}).get("per_case") or {}
        proprio[r.case_id] = sum(len(v) for tok, v in pc.items()
                                 if tok in r.case_id and isinstance(v, dict))
    solo = {c for k, cs in por_grupo.items() if k and len(cs) == 1 for c in cs
            if proprio[c] == 0}
    sem_grupo = [c for k, cs in por_grupo.items() if not k for c in cs]
    com = [c for c, k in proprio.items() if k > 0]
    so_compart = [c for c, k in proprio.items()
                  if k == 0 and c not in solo and c not in sem_grupo]
    vals = [proprio[c] for c in com]
    return {"n": len(comp), "com_proprio": len(com), "solo": len(solo),
            "so_compartilhada": len(so_compart), "sem_grupo": len(sem_grupo),
            "campos_med": float(np.median(vals)) if vals else 0.0,
            "campos_max": max(vals) if vals else 0}


def varreduras(comp, res, store, spread_min=0.02):
    """Ordering of the corpus's input sweeps: same source, bolt and mode, one
    input varied (imposed amplitude at fixed preload, or preload at fixed
    amplitude), >=3 distinct values. Predicted against measured retention is
    compared at the largest cycle count common to the sweep. A sweep whose
    measured retentions span less than `spread_min` cannot be ordered by any
    model and is reported as such rather than counted."""
    import collections
    from scipy.stats import spearmanr

    def delta(r):
        return round(float(store[r.case_id]["config_used"].get("delta_mm") or 0), 3)

    ga, gp = collections.defaultdict(list), collections.defaultdict(list)
    for r in comp:
        f0 = getattr(r.validation_case, "initial_preload_N", None)
        if delta(r) > 0 and f0:
            ga[(r.source, r.validation_case.bolt_size, round(f0, -2))].append((delta(r), r))
        if f0:
            gp[(r.source, r.validation_case.bolt_size, delta(r))].append((round(f0, -2), r))
    out = []
    for nome, grupos in (("amplitude", ga), ("preload", gp)):
        for k, rs in sorted(grupos.items()):
            vals = sorted({v for v, _ in rs})
            if len(vals) < 3:
                continue
            rep = [max([r for vv, r in rs if vv == v],
                       key=lambda r: res[r.case_id].metric_x[-1]) for v in vals]
            N = min(res[r.case_id].metric_x[-1] for r in rep)
            fp = [float(np.interp(N, res[r.case_id].metric_x, res[r.case_id].metric_pred))
                  for r in rep]
            fd = [float(np.interp(N, res[r.case_id].metric_x, res[r.case_id].metric_data))
                  for r in rep]
            inv = sum(1 for i in range(len(fd)) for j in range(i + 1, len(fd))
                      if (fp[i] - fp[j]) * (fd[i] - fd[j]) < 0)
            out.append({"src": k[0], "varre": nome, "n": len(vals), "N": float(N),
                        "rho": float(spearmanr(fp, fd).statistic), "inv": inv,
                        "spread": float(max(fd) - min(fd))})
    dec = [z for z in out if z["spread"] >= spread_min]
    return {"sweeps": out, "n": len(out), "n_decidiveis": len(dec),
            "n_perfeitas": sum(1 for z in dec if z["inv"] == 0),
            "rho_med": float(np.median([z["rho"] for z in dec])) if dec else None,
            "pior_rho": min((z["rho"] for z in dec), default=None),
            "spread_min": spread_min,
            "n_indecidiveis": len(out) - len(dec)}


def mc_digitalizacao(comp, res, pisos, n_trials=1000, res_leitura=0.005,
                     seed=20260831):
    """Verdict stability under the digitisation reading resolution: every
    digitised point perturbed by U(-res, +res), the three legs recomputed
    against the unchanged prediction, floors held fixed (conservative)."""
    rng = np.random.default_rng(seed)
    base = sum(1 for r in comp
               if rh._tripe_ok(res[r.case_id], rh.limite_sres(r.source, pisos)))
    vet = [(r, np.asarray(res[r.case_id].metric_x, float),
            np.asarray(res[r.case_id].metric_data, float),
            np.asarray(res[r.case_id].metric_pred, float)) for r in comp]
    cens = np.empty(n_trials, int)
    for k in range(n_trials):
        n_ok = 0
        for r, x, d, pr in vet:
            rr = pr - (d + rng.uniform(-res_leitura, res_leitura, size=len(d)))
            lim = rh.limite_sres(r.source, pisos)
            n_ok += (np.max(np.abs(rr)) <= rh.META_MAX
                     and np.mean(np.abs(rr)) <= rh.META_MAE
                     and (np.std(rr) <= lim if len(d) >= rh.N_MIN_SRES else False))
        cens[k] = n_ok
    return {"base": base, "n_trials": n_trials, "res": res_leitura,
            "min": int(cens.min()), "max": int(cens.max()),
            "p5": float(np.percentile(cens, 5)), "p95": float(np.percentile(cens, 95)),
            "mediana": float(np.median(cens))}


def baselines(comp, res):
    """Two bounds for the comparison: a three-constant law fitted PER CURVE
    (the ceiling a pure fit reaches, at 3 constants a curve) and the same law
    with one set of constants for the whole corpus on normalised cycles."""
    from scipy.optimize import least_squares
    X, Y = [], []
    maes_fit, maes_mod = [], []
    for r in comp:
        rr = res[r.case_id]
        x = np.asarray(rr.metric_x, float)
        y = np.asarray(rr.metric_data, float)
        X.append(x); Y.append(y)
        melhor = None
        for tau0 in (max(x.max(), 10) / 3, max(x.max(), 10) / 30, max(x.max(), 10) / 300):
            try:
                s = least_squares(lambda q: q[0] + q[1] * np.exp(-x / np.exp(q[2])) - y,
                                  [y[-1], y[0] - y[-1], np.log(tau0)], max_nfev=200)
                m = float(np.mean(np.abs(s.fun)))
                melhor = m if melhor is None or m < melhor else melhor
            except Exception:
                pass
        if melhor is not None:
            maes_fit.append(melhor)
            maes_mod.append(float(rr.mae))
    ends = [max(x[-1], 1.0) for x in X]

    def gres(q):
        return np.concatenate([q[0] + q[1] * np.exp(-(x / e) / np.exp(q[2])) - y
                               for x, y, e in zip(X, Y, ends)])
    sg = least_squares(gres, [0.8, 0.2, np.log(0.3)], max_nfev=400)
    per = [float(np.mean(np.abs(a))) for a in
           np.split(sg.fun, np.cumsum([len(x) for x in X])[:-1])]
    mf = np.asarray(maes_fit)
    return {"n": len(maes_fit),
            "fit_mediana": float(np.median(mf)), "fit_p90": float(np.percentile(mf, 90)),
            "fit_acima_005": int((mf > 0.05).sum()),
            "modelo_mediana": float(np.median(maes_mod)),
            "modelo_acima_005": int((np.asarray(maes_mod) > 0.05).sum()),
            "global_mediana": float(np.median(per)),
            "global_acima_005": int(sum(1 for v in per if v > 0.05)),
            "constantes_fit": 3 * len(maes_fit)}


def borda_janela(comp, res, pisos, margem=1.10, max_pontos=3):
    """The window-edge check: curves whose digitised record ends a fraction
    beyond the last simulated cycle. The residual is extended to those points
    with the model held at its final value (conservative by construction) and
    the verdicts recounted. Trimmed collapse tails are excluded: they end far
    beyond the window and are the object of the declared classes, not of this
    check."""
    from bolt_analysis_studio.validation.inputs import load_full_curve
    bordas, flips = 0, []
    for r in comp:
        rr = res[r.case_id]
        try:
            x, y = load_full_curve(r.validation_case.reference_csv_path)
        except Exception:
            continue
        off = getattr(r.validation_case, "csv_x_offset", 0) or 0
        sc = getattr(r.validation_case, "csv_x_scale", 1) or 1
        x = np.clip((np.asarray(x, float) - off) * sc, 0, None)
        y = np.asarray(y, float)
        xe = rr.metric_x[-1]
        alem = (x > xe) & (y >= rn.FLOOR_TRIM)
        if not alem.any() or alem.sum() > max_pontos or x[alem].max() > margem * xe:
            continue
        bordas += 1
        resid = np.concatenate([np.asarray(rr.metric_pred) - np.asarray(rr.metric_data),
                                rr.final_pred - y[alem]])
        lim = rh.limite_sres(r.source, pisos)
        ok0 = bool(rh._tripe_ok(rr, lim))
        ok1 = (float(np.max(np.abs(resid))) <= rh.META_MAX
               and float(np.mean(np.abs(resid))) <= rh.META_MAE
               and (float(np.std(resid)) <= lim if len(resid) >= rh.N_MIN_SRES else False))
        if ok0 != ok1:
            flips.append(r.case_id)
    return {"n_borda": bordas, "flips": flips}


def grade_ident(cid="jcsr2023_stainless_seawater",
                campos=("C_creep", "creep_t_c"), fatores=None, salva=None):
    """Joint identifiability grid for a coupled pair (level x shape of creep):
    MAE surface over multiplicative factors around the adopted values, computed
    by re-simulating the one curve through the default-inert ablation hook.
    Returns the grid and, if `salva` is given, writes the contour figure."""
    import os
    from bolt_analysis_studio.validation.case_registry import record
    fatores = fatores or [round(float(f), 3) for f in np.geomspace(0.5, 2.0, 11)]
    rec = record(cid)
    consts, _ = rn.frozen_constants()
    ov = rn._effective_overrides(rec, consts)
    base = {c: float(ov.get(c) or consts.get(c) or 0.0) for c in campos}
    antes = os.environ.get(rn._ABL_ENV)
    Z = np.empty((len(fatores), len(fatores)))
    try:
        for i, fa in enumerate(fatores):
            for j, fb in enumerate(fatores):
                os.environ[rn._ABL_ENV] = json.dumps(
                    {"overrides": {campos[0]: base[campos[0]] * fa,
                                   campos[1]: base[campos[1]] * fb}})
                Z[i, j] = rn.simulate_case(rec).mae
    finally:
        if antes is None:
            os.environ.pop(rn._ABL_ENV, None)
        else:
            os.environ[rn._ABL_ENV] = antes
    out = {"cid": cid, "campos": list(campos), "fatores": fatores,
           "base": base, "mae": Z.tolist(),
           "mae_min": float(Z.min()), "mae_nominal": float(Z[len(fatores)//2][len(fatores)//2])}
    if salva:
        import matplotlib.pyplot as plt
        f, ax = plt.subplots(figsize=(4.6, 3.6), layout="constrained")
        cs = ax.contourf(fatores, fatores, Z.T, levels=12, cmap="viridis_r")
        ax.contour(fatores, fatores, Z.T, levels=[0.05], colors="white", linewidths=1.2)
        ax.plot([1], [1], "o", color="#a63232", ms=5)
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel(f"factor on {campos[0]}", fontsize=8)
        ax.set_ylabel(f"factor on {campos[1]}", fontsize=8)
        ax.tick_params(labelsize=7)
        f.colorbar(cs, ax=ax, label="MAE in F/F0")
        salva(f, "fig_ident_grid")
    return out


# --------------------------------------------------------------------------- #
# leave-one-curve-out (written by loco_holdout.py)
# --------------------------------------------------------------------------- #
def carrega_loco(comp, res, pisos, caminho=None):
    """Reader for New_Theory/holdout/loco.json: median held-out error against
    the in-fit error on the same curves, verdicts of the held-out curves, and
    the per-group detail for the supplementary table."""
    caminho = caminho or (HOLD_DIR / "loco.json")
    if not caminho.exists():
        return None
    d = json.loads(caminho.read_text(encoding="utf-8"))
    ok = [z for z in d.get("folds", []) if "erro" not in z]
    if not ok:
        return None
    porid = {r.case_id: r for r in comp}
    n_ok, por_grupo = 0, {}
    for z in ok:
        r = porid.get(z["teste"])
        if r is None:
            continue
        lim = rh.limite_sres(r.source, pisos)
        passa = (z["max_holdout"] <= rh.META_MAX
                 and z["mae_holdout"] <= rh.META_MAE
                 and z["sres_holdout"] <= lim)
        n_ok += int(passa)
        g = por_grupo.setdefault(z["grupo"], {"n": 0, "passa": 0, "mae_h": [],
                                              "mae_i": [], "consts": z["constantes"]})
        g["n"] += 1
        g["passa"] += int(passa)
        g["mae_h"].append(z["mae_holdout"])
        g["mae_i"].append(z["mae_infit"])
    # leitura CONDICIONAL, a justa: das curvas que passam DENTRO do ajuste,
    # quantas seguem passando FORA dele. Sem isto o numero bruto mistura as
    # curvas que ja falham no ajuste (as declaradas e as de excecao).
    n_infit_ok = n_ambos = 0
    for z in ok:
        r = porid.get(z["teste"])
        if r is None:
            continue
        lim = rh.limite_sres(r.source, pisos)
        pi = (z["max_infit"] <= rh.META_MAX and z["mae_infit"] <= rh.META_MAE
              and z["sres_infit"] <= lim)
        ph = (z["max_holdout"] <= rh.META_MAX and z["mae_holdout"] <= rh.META_MAE
              and z["sres_holdout"] <= lim)
        n_infit_ok += int(pi)
        n_ambos += int(pi and ph)
    import collections as _c
    todos_grupos = _c.Counter(
        rn._adopted_for(r.source, r.case_id, r.validation_case.bolt_size)
        for r in comp)
    n_multi = sum(1 for k, v in todos_grupos.items() if k and v > 1)
    mh = np.array([z["mae_holdout"] for z in ok])
    mi = np.array([z["mae_infit"] for z in ok])
    fat = [abs(np.log(v)) for z in ok for v in z.get("fator", {}).values()]
    return {"n_folds": len(ok), "n_grupos": len(por_grupo),
            "n_curvas": len({z["teste"] for z in ok}),
            "stale": d.get("fingerprint") != rn.engine_fingerprint(),
            "mae_h_med": float(np.median(mh)), "mae_i_med": float(np.median(mi)),
            "mae_h_p90": float(np.percentile(mh, 90)),
            "n_passa": n_ok, "razao": float(np.median(mh) / max(np.median(mi), 1e-12)),
            "n_infit_ok": n_infit_ok, "n_ambos": n_ambos,
            "n_multi_total": n_multi,
            "fator_med": float(np.exp(np.median(fat))) if fat else None,
            "por_grupo": {k: {"n": v["n"], "passa": v["passa"],
                              "n_consts": len(v["consts"]),
                              "mae_h": float(np.median(v["mae_h"])),
                              "mae_i": float(np.median(v["mae_i"]))}
                          for k, v in sorted(por_grupo.items())}}


# --------------------------------------------------------------------------- #
# high-impact review items (2026-08-31)
# --------------------------------------------------------------------------- #
MECANISMO_ROTULO = {
    "embedding": "embedding", "creep": "creep", "wear": "wear",
    "rotational_loosening": "rotational loosening",
    "thread_fretting": "thread fretting", "fatigue": "fatigue",
}


def _dominante(store, cid):
    d = (store.get(cid) or {}).get("decomp") or {}
    tot = {k: (float(v[-1]) if isinstance(v, list) and v else 0.0)
           for k, v in d.items() if k != "cycles"}
    tot = {k: v for k, v in tot.items() if v > 0}
    return max(tot, key=tot.get) if tot else None


def _frac_inicial(rr, q=0.10):
    """Fraction of the total measured loss that happens in the first q of the
    window. Computed from the DIGITISED DATA only: it never sees the model."""
    x = np.asarray(rr.metric_x, float)
    y = np.asarray(rr.metric_data, float)
    if len(x) < 4 or (y[0] - y[-1]) <= 1e-6:
        return None
    return float((y[0] - np.interp(x[0] + q * (x[-1] - x[0]), x, y)) / (y[0] - y[-1]))


def mapa_regimes(comp, res, store, salva=None):
    """Regime map: the mechanism the model attributes the loss to, in the plane
    of imposed amplitude and preload, and the test that the attribution is not
    circular: a shape descriptor measured on the data alone separates the
    predicted classes."""
    import collections
    from scipy.stats import mannwhitneyu
    linhas, por_mec = [], collections.defaultdict(list)
    for r in comp:
        mec = _dominante(store, r.case_id)
        if not mec:
            continue
        cfg = store[r.case_id]["config_used"]
        f = _frac_inicial(res[r.case_id])
        linhas.append({"cid": r.case_id, "src": r.source, "mec": mec,
                       "delta_mm": float(cfg.get("delta_mm") or 0.0),
                       "F0_kN": float(getattr(r.validation_case,
                                              "initial_preload_N", 0) or 0) / 1e3,
                       "modo": cfg.get("mode"), "frac": f})
        if f is not None:
            por_mec[mec].append(f)
    resumo = {m: {"n": len(v), "med": float(np.median(v)),
                  "q1": float(np.percentile(v, 25)),
                  "q3": float(np.percentile(v, 75))}
              for m, v in sorted(por_mec.items(), key=lambda z: -len(z[1]))}
    emb = np.array(por_mec.get("embedding", []))
    loo = np.array(por_mec.get("rotational_loosening", []))
    pval = (float(mannwhitneyu(emb, loo, alternative="greater").pvalue)
            if len(emb) > 3 and len(loo) > 3 else None)
    out = {"linhas": linhas, "resumo": resumo, "p_emb_vs_loose": pval,
           "n": len(linhas)}
    if salva:
        import matplotlib.pyplot as plt
        cores = {"embedding": "#2b6cb0", "rotational_loosening": "#a63232",
                 "creep": "#b7791f", "wear": "#5a8f5a",
                 "thread_fretting": "#7a5ea8", "fatigue": "#666666"}
        f_, axs = plt.subplots(1, 2, figsize=(7.6, 3.2), layout="constrained")
        tr = [z for z in linhas if z["delta_mm"] > 0]
        for mec in sorted({z["mec"] for z in tr}, key=lambda m: -len(por_mec[m])):
            pts = [z for z in tr if z["mec"] == mec]
            axs[0].scatter([z["delta_mm"] for z in pts], [z["F0_kN"] for z in pts],
                           s=26, alpha=0.85, color=cores.get(mec, "#999999"),
                           edgecolor="white", linewidth=0.5,
                           label=f"{MECANISMO_ROTULO.get(mec, mec)} ({len(pts)})")
        axs[0].set_xscale("log")
        axs[0].set_yscale("log")
        axs[0].set_xlabel("imposed transverse amplitude [mm]", fontsize=8)
        axs[0].set_ylabel("initial preload [kN]", fontsize=8)
        axs[0].set_title("(a) mechanism attributed, displacement-controlled tests",
                         fontsize=8.5)
        axs[0].tick_params(labelsize=7)
        axs[0].grid(alpha=0.25)
        axs[0].legend(fontsize=6.2, frameon=False, loc="lower left",
                      ncols=2, columnspacing=0.8, handletextpad=0.3)
        ordem = [m for m in ("embedding", "thread_fretting", "creep", "fatigue",
                             "wear", "rotational_loosening") if m in por_mec]
        for i, mec in enumerate(ordem):
            v = np.array(por_mec[mec])
            x = np.random.default_rng(7).normal(i, 0.06, len(v))
            axs[1].scatter(x, v, s=13, alpha=0.65, color=cores.get(mec, "#999999"),
                           edgecolor="none")
            axs[1].plot([i - 0.28, i + 0.28], [np.median(v)] * 2, color="black",
                        lw=1.6, zorder=3)
        axs[1].set_xticks(range(len(ordem)))
        axs[1].set_xticklabels([MECANISMO_ROTULO.get(m, m).replace(" ", "\n")
                                for m in ordem], fontsize=7)
        axs[1].set_ylabel("share of the measured loss\nin the first 10 % of cycles",
                          fontsize=8)
        axs[1].set_title("(b) a descriptor measured on the data alone",
                         fontsize=8.5)
        axs[1].tick_params(axis="y", labelsize=7)
        axs[1].grid(axis="y", alpha=0.25)
        salva(f_, "fig_regime_map")
    return out


def metricas_padrao(comp, res):
    """Goodness-of-fit measures other papers report, so this one can be
    compared with them: coefficient of determination, Nash-Sutcliffe
    efficiency, Willmott index of agreement and normalised RMSE, per curve."""
    r2, nse, wil, nrm = [], [], [], []
    for r in comp:
        rr = res[r.case_id]
        d = np.asarray(rr.metric_data, float)
        p_ = np.asarray(rr.metric_pred, float)
        ss = float(np.sum((d - d.mean()) ** 2))
        sr = float(np.sum((d - p_) ** 2))
        if d.std() > 0 and p_.std() > 0:
            r2.append(float(np.corrcoef(d, p_)[0, 1] ** 2))
        if ss > 0:
            nse.append(1 - sr / ss)
        wil.append(1 - sr / max(float(np.sum((np.abs(p_ - d.mean())
                                              + np.abs(d - d.mean())) ** 2)), 1e-12))
        nrm.append(float(np.sqrt(sr / len(d)) / max(d.mean(), 1e-9)))
    return {"r2_med": float(np.median(r2)), "r2_p10": float(np.percentile(r2, 10)),
            "nse_med": float(np.median(nse)), "nse_pos": int((np.array(nse) > 0).sum()),
            "nse_n": len(nse), "wil_med": float(np.median(wil)),
            "nrmse_med": float(np.median(nrm))}


def intervalos_predicao(comp, res, store):
    """Prediction interval of the residual, by loading regime: the band a user
    should expect around a prediction, read from the corpus."""
    import collections
    por = collections.defaultdict(list)
    for r in comp:
        rr = res[r.case_id]
        e = np.abs(np.asarray(rr.metric_pred, float)
                   - np.asarray(rr.metric_data, float))
        por[store[r.case_id]["config_used"].get("mode") or "?"].extend(e)
    todos = np.concatenate([np.asarray(v) for v in por.values()])
    return {"por_modo": {k: {"n": len(v), "med": float(np.median(v)),
                             "p90": float(np.percentile(v, 90)),
                             "p95": float(np.percentile(v, 95))}
                         for k, v in sorted(por.items())},
            "p90": float(np.percentile(todos, 90)),
            "p95": float(np.percentile(todos, 95)),
            "med": float(np.median(todos))}


def aic_bic(comp, res, baselines_sse=None):
    """Information criteria against the two baselines, with the parameter count
    each one actually spends per curve. The model's count is its group's shared
    constants divided by the curves they serve, plus its own per-curve entries."""
    import collections
    from scipy.optimize import least_squares
    cfgs = json.loads((RAIZ / CFG_REL).read_text(encoding="utf-8"))["sources"]
    NAO = ("pack", "chain", "GA_member", "trim_n_max", "per_case")
    por = collections.defaultdict(list)
    for r in comp:
        por[rn._adopted_for(r.source, r.case_id, r.validation_case.bolt_size)].append(r)

    def k_modelo(r):
        k = rn._adopted_for(r.source, r.case_id, r.validation_case.bolt_size)
        c = (cfgs.get(k) or {}).get("cfg") or {}
        compart = sum(1 for a, v in c.items()
                      if a not in NAO and isinstance(v, (int, float)))
        pc = c.get("per_case") or {}
        prop = sum(len(v) for tok, v in pc.items()
                   if tok in r.case_id and isinstance(v, dict))
        return compart / max(len(por[k]), 1) + prop

    def ic(sse, n, k):
        base = n * np.log(max(sse, 1e-18) / n)
        return base + 2 * k, base + k * np.log(n)

    A_m, A_f, A_g, B_m, B_f, B_g, ks = [], [], [], [], [], [], []
    X, Y, ends = [], [], []
    for r in comp:
        rr = res[r.case_id]
        d = np.asarray(rr.metric_data, float)
        p_ = np.asarray(rr.metric_pred, float)
        x = np.asarray(rr.metric_x, float)
        n = len(d)
        km = k_modelo(r)
        ks.append(km)
        a, b = ic(float(np.sum((d - p_) ** 2)), n, km)
        A_m.append(a)
        B_m.append(b)
        melhor = None
        for tau0 in (max(x.max(), 10) / 3, max(x.max(), 10) / 30,
                     max(x.max(), 10) / 300):
            try:
                s = least_squares(lambda q: q[0] + q[1] * np.exp(-x / np.exp(q[2])) - d,
                                  [d[-1], d[0] - d[-1], np.log(tau0)], max_nfev=200)
                v = float(np.sum(s.fun ** 2))
                melhor = v if melhor is None or v < melhor else melhor
            except Exception:
                pass
        a, b = ic(melhor, n, 3)
        A_f.append(a)
        B_f.append(b)
        X.append(x)
        Y.append(d)
        ends.append(max(x[-1], 1.0))

    def gres(q):
        return np.concatenate([q[0] + q[1] * np.exp(-(x / e) / np.exp(q[2])) - y
                               for x, y, e in zip(X, Y, ends)])
    sg = least_squares(gres, [0.8, 0.2, np.log(0.3)], max_nfev=400)
    for arr, x in zip(np.split(sg.fun, np.cumsum([len(x) for x in X])[:-1]), X):
        a, b = ic(float(np.sum(arr ** 2)), len(x), 3 / len(comp))
        A_g.append(a)
        B_g.append(b)
    A_m, A_f, A_g = map(np.array, (A_m, A_f, A_g))
    B_m, B_f, B_g = map(np.array, (B_m, B_f, B_g))
    return {"aic_modelo": float(np.median(A_m)), "aic_fit": float(np.median(A_f)),
            "aic_global": float(np.median(A_g)),
            "bic_modelo": float(np.median(B_m)), "bic_fit": float(np.median(B_f)),
            "bic_global": float(np.median(B_g)),
            "modelo_vence_fit_aic": int((A_m < A_f).sum()),
            "modelo_vence_fit_bic": int((B_m < B_f).sum()),
            "modelo_vence_global_aic": int((A_m < A_g).sum()),
            "n": len(A_m), "k_modelo_med": float(np.median(ks))}


def ancoras_e_energia(comp, store):
    """Independent checks on the constants themselves: the anchor verdicts of
    the campaign, and the specific removal energy the wear channel implies
    against the band of the literature."""
    import collections
    caminho = RAIZ / "New_Theory" / "anchors_verdicts.json"
    anc = {}
    if caminho.exists():
        d = json.loads(caminho.read_text(encoding="utf-8"))
        sobre_const = {k: v for k, v in d.items() if not k.startswith("[")}
        _EN = {"PASSA": "reproduce the measurement",
               "BANDA": "are bracketed by the measured band",
               "DIRECAO": "have their sign or trend confirmed",
               "ESCOPO": "fall outside the scope of the model"}
        anc = {"n_total": len(d), "n_const": len(sobre_const),
               "verdicts": {_EN.get(k, str(k).lower()): v for k, v in
                            collections.Counter(
                                v.get("verdict") for v in sobre_const.values()
                            ).most_common()},
               "constantes": sorted(sobre_const)}
    vals, dentro, fora, banda = [], 0, 0, None
    for r in comp:
        z = (store.get(r.case_id) or {}).get("l7_check") or {}
        banda = z.get("bound") or banda
        v = z.get("implied_J_per_mm3")
        if v is None:
            continue
        vals.append(float(v))
        dentro += bool(z.get("in_bound"))
        fora += (z.get("in_bound") is False)
    energia = {"n": len(vals), "dentro": dentro, "fora": fora,
               "med": float(np.median(vals)) if vals else None,
               "min": float(min(vals)) if vals else None,
               "max": float(max(vals)) if vals else None,
               "lo": (banda or {}).get("lo"), "hi": (banda or {}).get("hi")}
    return {"ancoras": anc, "energia_remocao": energia}


def variantes_de_forma(comp):
    """How many distinct kernel combinations the corpus runs on: the model-space
    freedom that a parameter count alone does not show."""
    import collections
    MODOS = ("creep_mode", "loose_rate_mode", "kj_mode", "slip_regime_mode",
             "k_tr_mode", "conform_driver", "loose_torsion_mode")
    cfgs = json.loads((RAIZ / CFG_REL).read_text(encoding="utf-8"))["sources"]
    combos, usos = collections.Counter(), collections.Counter()
    for r in comp:
        k = rn._adopted_for(r.source, r.case_id, r.validation_case.bolt_size)
        e = cfgs.get(k) or {}
        c = e.get("cfg") or {}
        eff = dict(c)
        for tok, v in (c.get("per_case") or {}).items():
            if tok in r.case_id and isinstance(v, dict):
                eff.update(v)
        pack = str(e.get("pack") or "")
        pack = pack if pack in ("PACK", "LEGACY") else ""
        combo = tuple(sorted((m, str(eff[m])) for m in MODOS
                             if m in eff and str(eff[m]) not in ("", "None")))
        combos[(pack, combo)] += 1
        for mv in combo:
            usos[mv] += 1
        if float(eff.get("fat_ramp_D_on", 1.0)) < 1.0:
            usos[("fatigue release", "ramp")] += 1
    return {"n_combos": len(combos), "n_curvas": len(comp),
            "maior": combos.most_common(1)[0][1] if combos else 0,
            "usos": {f"{a} = {b}": n for (a, b), n in usos.most_common()},
            "distribuicao": [n for _, n in combos.most_common()]}


def carrega_apriori(comp, res, pisos, caminho=None):
    """Reader for the a-priori run: the corpus with no per-rig configuration."""
    caminho = caminho or (ABL_DIR / "ablation_a_priori.json")
    if not caminho.exists():
        return None
    d = json.loads(caminho.read_text(encoding="utf-8"))
    rv = {}
    for cid, rec in d.get("results", {}).items():
        try:
            rv[cid] = CaseResult.from_dict(rec)
        except Exception:
            pass
    n_ok, maes, maes_cal = 0, [], []
    for r in comp:
        rr = rv.get(r.case_id)
        if not rr or rr.mae is None:
            continue
        n_ok += int(bool(rh._tripe_ok(rr, rh.limite_sres(r.source, pisos))))
        maes.append(float(rr.mae))
        maes_cal.append(float(res[r.case_id].mae))
    return {"n": len(maes), "n_ok": n_ok, "mae_med": float(np.median(maes)),
            "mae_cal_med": float(np.median(maes_cal)),
            "razao": float(np.median(maes) / max(np.median(maes_cal), 1e-12)),
            "stale": d.get("fingerprint_base") != rn.engine_fingerprint()}


def carrega_benchmark_v1(comp, res, pisos, caminho=None, apriori=None):
    """Reader for the classical staged model run on the same curves.

    The comparison that means anything is on the MATCHED subset and against the
    present model in the same condition, uncalibrated: both statistics are
    computed only on the curves the classical engine completes.
    """
    caminho = caminho or (HOLD_DIR / "benchmark_v1.json")
    if not Path(caminho).exists():
        return None
    d = json.loads(Path(caminho).read_text(encoding="utf-8"))
    ok = [z for z in d.get("resultados", {}).values() if "erro" not in z]
    if not ok:
        return None
    porid = {r.case_id: r for r in comp}
    apriori = apriori or (ABL_DIR / "ablation_a_priori.json")
    ap = {}
    if Path(apriori).exists():
        for cid, rec in json.loads(Path(apriori).read_text(encoding="utf-8")
                                   ).get("results", {}).items():
            try:
                ap[cid] = CaseResult.from_dict(rec)
            except Exception:
                pass
    n_ok = n_ap_ok = 0
    m_v1, m_ap, m_cal = [], [], []
    for z in ok:
        r = porid.get(z["case_id"])
        if r is None:
            continue
        lim = rh.limite_sres(r.source, pisos)
        n_ok += int(z["maxerr"] <= rh.META_MAX and z["mae"] <= rh.META_MAE
                    and z["resid_std"] <= lim)
        m_v1.append(float(z["mae"]))
        m_cal.append(float(res[r.case_id].mae))
        a = ap.get(z["case_id"])
        if a is not None and a.mae is not None:
            m_ap.append(float(a.mae))
            n_ap_ok += int(bool(rh._tripe_ok(a, lim)))
    falhas = [c for c, z in d.get("resultados", {}).items() if "erro" in z]
    forca = sum(1 for c in falhas if c in porid
                and not float(getattr(porid[c].validation_case,
                                      "transverse_displacement_mm", 0) or 0))
    return {"n": len(m_v1), "n_ok": n_ok,
            "mae_med": float(np.median(m_v1)),
            "mae_v2_med": float(np.median(m_cal)),
            "n_ap": len(m_ap), "n_ap_ok": n_ap_ok,
            "mae_ap_med": float(np.median(m_ap)) if m_ap else None,
            "n_erros": len(falhas), "erros_force": forca,
            "n_cap": d.get("n_cap")}


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import build_annex_docx as A
    comp, res, pisos, store, todos, res_all = A.carrega()
    sw = varredura_criterio(comp, res, pisos)
    print(f"[sweep] nominal {sw['n_nominal']}/{sw['n']} · no floor {sw['n_sem_piso']} · "
          f"near +-10 % {sw['n_perto_10pct']} · points {sw['pontos']}")
    ho = holdout_temporal(comp, res, pisos)
    for k in ("strict", "lenient", "seen", "all"):
        v = ho[k]
        print(f"[holdout] {k:8s} n={v['n']:3d} ok={v['n_ok']:3d} "
              f"({(v['pct'] or 0):.0f} %) mae_med={v['mae_med']} r2={v['r2_final']}")
    print(f"[holdout] cfg commits {ho['n_commits_cfg']} · groups dated "
          f"{ho['n_groups_dated']} · shared last {ho['shared_last']} · "
          f"no git date {len(ho['sem_data_git'])}")
    print("[holdout] strict by source:", ho["por_fonte_strict"])
    for z in carrega_congelados(comp, res, pisos):
        a = z["all"]
        print(f"[frozen] {z['freeze_date']} ({z['freeze_commit']}, {z['n_groups_frozen']} groups) "
              f"n={a['n']} frozen ok={a['ok_frozen']} today ok={a['ok_today']} "
              f"mae {a['mae_frozen']} vs {a['mae_today']} · prior n={z['prior']['n']} "
              f"ok={z['prior']['ok_frozen']} · with cfg n={z['with_cfg']['n']} "
              f"ok={z['with_cfg']['ok_frozen']}")
    for row in carrega_ablacao(comp, res, pisos):
        print(f"[ablation] {row['variant']:17s} ok={row['n_ok']:3d} "
              f"mae_med={row['mae_med']:.4f} r2={row['r2_final']:.3f} "
              f"down={row['flips_down']} up={row['flips_up']} changed={row['n_changed']}"
              + ("  STALE" if row["stale"] else ""))
