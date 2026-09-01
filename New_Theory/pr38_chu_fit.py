# -*- coding: utf-8 -*-
"""PR-38 (Chu2026, mu evolutivo) — instancia de fit em SANDBOX.

Estagios (sys.argv[1]):
  read     — le mu0/evolucao dos 5 CSVs de mu(N) + baseline do store + resumo preload
  base     — escreve cfg base no sandbox (PACK, c_bend=0.2, mu_thread=0.05,
             per_case mu_bearing=mu0) SEM dano e roda os 9 casos
  probe    — sonda c_D (W_ref=1e4) x k_dmg_mu no test2 lendo mu(N) ATRAVES do engine
  final    — roda os 9 casos com o cfg final e escreve pr38_chu_results.json
"""
import io
import json
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(r"C:\Users\leo_r\OneDrive\BPL\Analitical\BAS_V2")
SANDBOX = ROOT / "New_Theory" / "sandbox_configs_CHU.json"
CANON = ROOT / "New_Theory" / "adopted_configs.json"

# ---- SETUP DO SANDBOX (obrigatorio ANTES de importar bolt_analysis_studio) --
if not SANDBOX.exists():
    shutil.copyfile(CANON, SANDBOX)
os.environ["BAS_ADOPTED_CONFIGS"] = str(SANDBOX)
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402

CSV_DIR = ROOT / "BAS_V2_papers" / "E. Rodada 4 (deep-research 2026-07-11)" / "digitized_csv"
MU_TESTS = [1, 2, 4, 7, 8]          # testes com mu(N) publicado (Fig. 5)
ALL_TESTS = list(range(1, 10))
OUT_JSON = ROOT / "New_Theory" / "pr38_chu_results.json"


def _retry(fn, tries=80, dt=0.05):
    """Retry-guard de PermissionError (OneDrive)."""
    for i in range(tries):
        try:
            return fn()
        except PermissionError:
            time.sleep(dt)
    return fn()


def read_json(p):
    return _retry(lambda: json.loads(io.open(p, encoding="utf-8").read()))


def write_json(p, d):
    def _w():
        with io.open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=1, ensure_ascii=False)
    _retry(_w)


def mu_curve(test):
    d = np.genfromtxt(CSV_DIR / f"chu2026ti_fig5_muplate_test{test}.csv",
                      delimiter=",", skip_header=1, encoding="utf-8")
    return d[:, 0], d[:, 1]


def mu0_per_test():
    """mu0 por teste: test1 pos-dip (~N=40, receita), demais = 1o ponto."""
    mu0 = {}
    for t in MU_TESTS:
        n, mu = mu_curve(t)
        if t == 1:
            # pos-dip: 1o ponto apos o dip de running-in (N~14) que recupera
            k = int(np.argmin(mu))                 # o dip
            mu0[t] = float(mu[k + 2]) if k + 2 < len(mu) else float(mu[-1])
        else:
            mu0[t] = float(mu[0])
    mean = float(np.mean(list(mu0.values())))
    for t in ALL_TESTS:
        if t not in mu0:
            mu0[t] = round(mean, 4)
    return mu0, mean


def chu_records():
    from bolt_analysis_studio.validation.case_registry import all_records
    return [r for r in all_records() if r.source == "CHU_2026"]


def set_sandbox_cfg(cfg_entry):
    d = read_json(SANDBOX)
    d.setdefault("sources", {})["CHU_2026"] = cfg_entry
    write_json(SANDBOX, d)


def run_all(n_cap=None):
    from bolt_analysis_studio.validation.runner import simulate_case
    out = {}
    for r in sorted(chu_records(), key=lambda r: r.case_id):
        res = simulate_case(r, n_cap=n_cap)
        out[r.case_id] = res
    return out


def show(results, baseline=None):
    print(f"{'case':46s} {'mae':>7s} {'maxerr':>7s} {'D_fin':>6s} "
          f"{'fin_p':>6s} {'fin_d':>6s}" + ("  base_mae" if baseline else ""))
    maes = []
    for cid, r in results.items():
        if not r.ok:
            print(f"{cid:46s} ERRO: {r.error}")
            continue
        maes.append(r.mae)
        extra = ""
        if baseline and cid in baseline:
            extra = f"  {baseline[cid]['mae']:.4f} -> "
        print(f"{cid:46s} {r.mae:7.4f} {r.maxerr:7.4f} {r.D_final:6.3f} "
              f"{r.final_pred:6.3f} {r.final_data:6.3f}{extra}")
    if maes:
        print(f"mediana MAE = {float(np.median(maes)):.4f}   "
              f"max = {max(maes):.4f}")


# ---------------------------------------------------------------------------
def stage_read():
    mu0, mean = mu0_per_test()
    print("== mu0 por teste (Fig. 5) ==")
    evol = {}
    for t in MU_TESTS:
        n, mu = mu_curve(t)
        ratio = mu[-1] / mu0[t]
        # N de saturacao: 1o ciclo em que mu >= 95% do final
        k = int(np.argmax(mu >= mu0[t] + 0.95 * (mu[-1] - mu0[t])))
        evol[t] = dict(mu0=round(float(mu0[t]), 4),
                       mu_end=round(float(mu[-1]), 4),
                       ratio=round(float(ratio), 3),
                       N_end=int(n[-1]), N_95=int(n[k]))
        print(f" test{t}: mu0={mu0[t]:.4f}  mu_end={mu[-1]:.4f} "
              f"(x{ratio:.2f})  N_end={int(n[-1])}  N_95%={int(n[k])}")
    print(f" media mu0 (p/ tests 3/5/6/9): {mean:.4f}")

    print("\n== preload data (CSV cru) ==")
    for r in sorted(chu_records(), key=lambda r: r.case_id):
        from bolt_analysis_studio.validation.inputs import load_full_curve, repo_root
        rel = r.csv_path.relative_to(repo_root()).as_posix()
        cyc, rr = load_full_curve(rel)
        rr = rr / max(rr[0], 1e-9)
        keep = rr >= 0.10
        print(f" {r.case_id:46s} n={int(cyc[-1]):5d}  fin_cru={rr[-1]:.3f}  "
              f"fin_trim={rr[keep][-1]:.3f}  F0={r.validation_case.initial_preload_N/1e3:.0f}kN "
              f"D={r.validation_case.transverse_displacement_mm}mm")

    print("\n== baseline do store ==")
    from bolt_analysis_studio.validation.store import ValidationStore
    st = ValidationStore()
    base = {}
    for r in sorted(chu_records(), key=lambda r: r.case_id):
        b = st.get(r.case_id)
        if b and b.ok:
            base[r.case_id] = dict(mae=b.mae, maxerr=b.maxerr)
            print(f" {r.case_id:46s} mae={b.mae:.4f}  maxerr={b.maxerr:.4f}")
        else:
            print(f" {r.case_id:46s} SEM baseline no store")
    write_json(ROOT / "New_Theory" / "pr38_baseline_tmp.json",
               dict(mu0={f"test{t}": v for t, v in mu0.items()},
                    evolucao={f"test{t}": v for t, v in evol.items()},
                    baseline=base))


C_BEND_READ = 1.881   # RE-LIDO atraves do engine (2026-07-15): ancora = limiar
                      # do paper D_cr=0.30mm @F0=49kN com mu0(test1)=0.1043 da
                      # Fig.5 => delta_onset=0.46*mu0*F0/k_tr(c_bend)=0.30mm.
                      # (O 0.2 do PR-30b foi lido com mu_bearing=0.20 paper-FEM;
                      # com os mu0 medidos a mesma ancora re-le c_bend=1.881.
                      # Checks: test2 desliza (0.337<0.4mm), test1 em onset.)


def emb_read_um():
    """Leitura L24 (emb_from_curve) na curva BELOW-THRESHOLD test1 — sem slip,
    a queda inicial e assentamento puro (precedente Yang2023 IJPEM). k_b do
    engine para a geometria do caso."""
    from bolt_analysis_studio.calibration.knowledge_base import emb_from_curve
    from bolt_analysis_studio.validation.inputs import (geometry_for_case,
                                                        load_full_curve,
                                                        repo_root, emb_depth_vdi)
    from bolt_analysis_studio.validation.runner import _loading_for
    rec = next(r for r in chu_records() if "test1" in r.case_id)
    load = _loading_for(rec)
    geom = geometry_for_case(rec.validation_case,
                             grip_mm=load["inputs"]["grip_mm"]["value"])
    rel = rec.csv_path.relative_to(repo_root()).as_posix()
    cyc, rr = load_full_curve(rel)
    vdi_m, _ = emb_depth_vdi(load["inputs"]["rz"]["value"], 1)
    emb_m, prov = emb_from_curve(cyc, rr, rec.validation_case.initial_preload_N,
                                 geom.k_b, vdi_ref_m=vdi_m)
    return emb_m * 1e6, prov


def base_cfg(mu0, extra=None):
    per_case = {f"test{t}": {"mu_bearing": round(mu0[t], 4)} for t in ALL_TESTS}
    emb_um, emb_prov = emb_read_um()
    cfg = {"c_bend": C_BEND_READ, "mu_thread": 0.05, "C_creep": 0.0,
           "emb_um": round(emb_um, 2), "per_case": per_case}
    if extra:
        cfg.update(extra)
    return {"pack": "PACK", "cfg": cfg,
            "prov": "PR-38 sandbox: mu0 por teste lido da Fig.5 (paper); "
                    "c_bend=1.881 re-lido da ancora D_cr=0.30mm@49kN com "
                    "mu0(test1) medido; mu_thread=0.05 paper; emb_um="
                    f"{emb_um:.2f} data_implied_early_drop na curva "
                    "below-threshold test1 (leitor L24; handbook "
                    f"{emb_prov.get('vdi_handbook_um')}um divergia); "
                    "C_creep=0 lido da PLANURA da cauda below-threshold test1 "
                    "(dado +0.4%/2400cyc vs modelo-shared -2.8%; per-par "
                    "sec4.7, precedentes QIN_2024 sonda + PR-31b planura"}


def stage_base():
    mu0, _ = mu0_per_test()
    set_sandbox_cfg(base_cfg(mu0))
    res = run_all()
    base = read_json(ROOT / "New_Theory" / "pr38_baseline_tmp.json")["baseline"]
    show(res, base)


def mu_traj_through_engine(rec, damage=None, n_max=None):
    """Roda o caso steppando o engine MANUALMENTE (mesma montagem do runner)
    e devolve (ciclos, mu_bearing_eff, D, ratio)."""
    from bolt_analysis_studio.validation.runner import (_loading_for,
                                                        material_kwargs_for)
    from bolt_analysis_studio.validation.inputs import (geometry_for_case,
                                                        load_full_curve,
                                                        repo_root)
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer, JointMaterial, mu_bearing_eff)
    case = rec.validation_case
    load = _loading_for(rec)
    inp = load["inputs"]
    kw = material_kwargs_for(rec, inp)
    if damage:
        kw.update(damage)
    mat = JointMaterial(**kw)
    geom = geometry_for_case(case, grip_mm=inp["grip_mm"]["value"],
                             E=(inp.get("E") or {}).get("value"))
    rel = rec.csv_path.relative_to(repo_root()).as_posix()
    cyc, rr = load_full_curve(rel)
    rr = rr / max(rr[0], 1e-9)
    n = n_max or int(cyc[rr >= 0.10][-1])
    F0 = case.initial_preload_N
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    mus = np.empty(n + 1); Ds = np.empty(n + 1); ratio = np.empty(n + 1)
    mus[0] = mu_bearing_eff(ana.state, mat); Ds[0] = ana.state.D; ratio[0] = 1.0
    for k in range(1, n + 1):
        ana.step_cycle(load["F_amp_N"], load["theta"], case.frequency_Hz,
                       delta_amp=(load["delta_mm"] * 1e-3
                                  if load["mode"] == "displacement" else None))
        mus[k] = mu_bearing_eff(ana.state, mat)
        Ds[k] = ana.state.D
        ratio[k] = max(ana.state.F_0, 0.0) / F0
    return np.arange(n + 1), mus, Ds, ratio


def stage_probe():
    mu0, _ = mu0_per_test()
    set_sandbox_cfg(base_cfg(mu0))          # per_case mu0 ativo no material
    recs = {r.case_id: r for r in chu_records()}
    rec2 = next(r for cid, r in recs.items() if "test2" in cid)
    n2, mud2 = mu_curve(2)                  # dado medido
    tgt_end = mud2[-1] / mu0[2]             # razao alvo no fim (x2.21 @1103)

    grid_kmu = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [-2.3]
    grid_cD = [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else [2.0]
    print(f"alvo test2: mu {mu0[2]:.4f} -> {mud2[-1]:.4f} (x{tgt_end:.2f}) em N={int(n2[-1])}")
    for kmu in grid_kmu:
        for cD in grid_cD:
            dmg = dict(c_D=cD, W_ref=1e4, k_dmg_mu=kmu)
            cyc, mus, Ds, ratio = mu_traj_through_engine(rec2, dmg,
                                                         n_max=int(n2[-1]))
            pred = np.interp(n2, cyc, mus)
            mae_mu = float(np.mean(np.abs(pred - mud2)))
            print(f" k_dmg_mu={kmu:6.2f} c_D={cD:6.2f}: "
                  f"mu_end={mus[-1]:.4f} (x{mus[-1]/mus[0]:.2f}) D_end={Ds[-1]:.3f} "
                  f"ratio_fin={ratio[-1]:.3f}  MAE_mu={mae_mu:.4f}")


def stage_family():
    """Roda os 9 casos p/ cada par (k_dmg_mu, c_D) candidato."""
    mu0, _ = mu0_per_test()
    base = read_json(ROOT / "New_Theory" / "pr38_baseline_tmp.json")["baseline"]
    pairs = [tuple(float(x) for x in p.split("/"))
             for p in sys.argv[2].split(",")]
    for kmu, cD in pairs:
        set_sandbox_cfg(base_cfg(mu0, extra=dict(c_D=cD, W_ref=1e4,
                                                 k_dmg_mu=kmu)))
        res = run_all()
        maes = [r.mae for r in res.values() if r.ok]
        n_better = sum(1 for cid, r in res.items()
                       if r.ok and r.mae <= base[cid]["mae"] + 1e-9)
        print(f"\n### k_dmg_mu={kmu} c_D={cD}: mediana={float(np.median(maes)):.4f} "
              f"max={max(maes):.4f}  melhora {n_better}/9")
        show(res, base)


def stage_final():
    mu0, _ = mu0_per_test()
    kmu = float(sys.argv[2]) if len(sys.argv) > 2 else -2.3
    cD = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    entry = base_cfg(mu0, extra=dict(c_D=cD, W_ref=1e4, k_dmg_mu=kmu))
    entry["prov"] += (f"; dano per-rig fitado-this-rig no mu(N) do test2: "
                      f"c_D={cD}, W_ref=1e4, k_dmg_mu={kmu} (<0: mu SOBE, Fig.5)")
    set_sandbox_cfg(entry)
    res = run_all()
    tmp = read_json(ROOT / "New_Theory" / "pr38_baseline_tmp.json")
    show(res, tmp["baseline"])

    # verificacao mu(N) nos 5 testes publicados, atraves do engine
    recs = {r.case_id: r for r in chu_records()}
    dmg = dict(c_D=cD, W_ref=1e4, k_dmg_mu=kmu)
    mu_check = {}
    for t in MU_TESTS:
        rec = next(r for cid, r in recs.items() if f"test{t}" in cid)
        nd, mud = mu_curve(t)
        cyc, mus, Ds, ratio = mu_traj_through_engine(rec, dmg, n_max=int(nd[-1]))
        pred = np.interp(nd, cyc, mus)
        mu_check[f"test{t}"] = dict(
            mae_mu=round(float(np.mean(np.abs(pred - mud))), 4),
            ratio_pred=round(float(mus[-1] / mus[0]), 3),
            ratio_data=round(float(mud[-1] / mud[0]), 3),
            D_end=round(float(Ds[-1]), 3))
        print(f" mu(N) test{t}: pred x{mus[-1]/mus[0]:.2f} vs dado "
              f"x{mud[-1]/mud[0]:.2f}  MAE_mu={mu_check[f'test{t}']['mae_mu']:.4f}")

    # N_90 do modelo (1o ciclo com ratio<=0.9) p/ o veredicto da familia
    # nao-monotonica; dado = Tabela 1 do paper.
    n90 = {}
    for cid, r in res.items():
        if not r.ok:
            continue
        arr = np.asarray(r.ratio)
        cyc = np.asarray(r.cycles)
        below = np.nonzero(arr <= 0.9)[0]
        n90[cid] = (float(cyc[below[0]]) if len(below) else None)
    out = dict(
        mu0_por_teste=tmp["mu0"], evolucao=tmp["evolucao"],
        cfg_final=entry, mu_check=mu_check,
        n90_modelo=n90,
        n90_paper_tabela1={"test1": None, "test2": 278, "test3": 325,
                          "test4": 406, "test5": 72, "test6": 54,
                          "test7": 1050, "test8": 936, "test9": 180},
        results={cid: dict(mae=(round(r.mae, 4) if r.ok else None),
                           maxerr=(round(r.maxerr, 4) if r.ok else None),
                           D_final=(round(r.D_final, 3) if r.ok else None),
                           final_pred=(round(r.final_pred, 3) if r.ok else None),
                           final_data=(round(r.final_data, 3) if r.ok and r.final_data is not None else None),
                           error=r.error)
                 for cid, r in res.items()},
        baseline=tmp["baseline"])
    write_json(OUT_JSON, out)
    print(f"\n-> {OUT_JSON}")


if __name__ == "__main__":
    {"read": stage_read, "base": stage_base, "family": stage_family,
     "probe": stage_probe, "final": stage_final}[sys.argv[1]]()
