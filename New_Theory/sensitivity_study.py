"""ESTUDO DE SENSIBILIDADE OAT (one-at-a-time, x1.2 e /1.2) das constantes
ATIVAS do modelo — diretiva do professor 2026-07-09: "gere uma lista de
variaveis e faca um estudo de sensitividade; quanto menos graus de liberdade
mais robusto e o modelo".

Metrica: S(p) = deslocamento medio da PREDICAO |r_perturbado - r_nominal|
avaliado nos ciclos do dado (mesma unidade do MAE, F/F0). Mede quanto a saida
depende do parametro — alto S = DOF real (precisa proveniencia); S~0 = inerte
no regime (congelar sem custo). Tambem grava a assimetria (S+ vs S-).

Casos representativos (working point = PACK canonico + c_bend/extras per-rig
declarados em adopted_configs/GROUP; caveat: ranking local, nao o fit exato da
galeria — L1). Transversal 7 casos curtos + axial 2 casos (cap 100k, emb
data-implicito sec4.40).

Run: python New_Theory/sensitivity_study.py   (~30-45 min; rodar em background)
Escreve: sensitivity_study.json
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

import transfer_validation as tv  # noqa: E402
from frontier_polish import PACK  # noqa: E402
from library_common import (  # noqa: E402
    frozen_constants, geometry_for, emb_depth_vdi, load_full_curve)
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)

DIG = ROOT / "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"
CAP_AX = 100000

# parametros continuos ATIVOS no working point canonico (PACK+consts).
# K_archard representa a razao K/H (hardness fixo; so a razao e identificavel).
PARAMS = ["mu", "emb_depth", "N_emb", "K_archard", "k_j_init", "alpha_GW",
          "C_creep", "tr_loose_gain", "eta_loose", "c_bend",
          "loose_arrest_floor", "W_conf_ref", "conform_pressure_exp",
          "p_ref_conform", "slip_regime_sharpness", "slip_capacity_coeff",
          "partial_slip_exp"]

# casos transversais: (stem, cfg extra alem de PACK+consts)
TR_CASES = [
    ("karlsen2022_M30_HV_run1p2",  dict(c_bend=3.0)),
    ("karlsen2022_M42_HV_run20p0", dict(c_bend=3.0)),
    ("lu2024_M8_fig18_amp0p5",     dict(c_bend=0.7, k_ratchet=0.02,
                                        ratchet_torque_coupled=True)),
    ("lu2024_M8_fig20_T16Nm",      dict(c_bend=0.7, k_ratchet=0.02,
                                        ratchet_torque_coupled=True)),
    ("liu2025_M16_amp0p4",         dict(c_bend=0.3, delta_free=0.30e-3)),
    ("demir2024_amp0p3_F14p3_lk13p8", dict(c_bend=1.0)),
    ("rousseau2025_steel_t10",     dict(c_bend=1.0)),
]
# casos axiais: (csv, F0, F_amp, bolt, grip, freq, emb_data_implicito_um)
AX_CASES = [
    ("liu2017_axial_F0_18kN.csv",   18e3, 10e3, "M12x1.75", 30.0, 30.0, 2.24),
    ("li2022ti_axialmin_15Hz.csv",  10e3, 10e3, "M10x1.5",  25.0, 15.0, 1.62),
]


def build_mat(base_kw, overrides):
    kw = dict(base_kw)
    kw.update(overrides)
    return JointMaterial(**kw)


def sim_transverse(case, mat, cyc):
    geom = geometry_for(case.bolt_size,
                        grip_mm=tv.inputs_for(case)["grip_mm"]["value"])
    F0 = case.initial_preload_N
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    n_max = int(cyc[-1])
    delta = case.transverse_displacement_mm * 1e-3
    F_amp = tv.inputs_for(case)["F_amp_N"]["value"]
    r = np.empty(n_max + 1); r[0] = 1.0
    for n in range(1, n_max + 1):
        ana.step_cycle(F_amp, np.pi / 2, case.frequency_Hz, delta_amp=delta)
        r[n] = max(ana.state.F_0, 0.0) / F0
        ana.history.clear()
    return np.interp(cyc, np.arange(n_max + 1), r)


def sim_axial(F0, F_amp, bolt, grip, freq, mat, cyc):
    geom = geometry_for(bolt, grip)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    n_max = int(cyc[-1])
    r = np.empty(n_max + 1); r[0] = 1.0
    for n in range(1, n_max + 1):
        ana.step_cycle(F_amp, 0.0, freq)
        r[n] = max(ana.state.F_0, 0.0) / F0
        ana.history.clear()
    return np.interp(cyc, np.arange(n_max + 1), r)


def perturb_kw(base_kw, param, factor):
    """Retorna kwargs com o parametro perturbado. 'mu' move thread+bearing."""
    kw = dict(base_kw)
    if param == "mu":
        kw["mu_thread"] = kw["mu_thread"] * factor
        kw["mu_bearing"] = kw["mu_bearing"] * factor
    else:
        nominal = kw.get(param, getattr(JointMaterial(emb_depth=1e-6), param))
        kw[param] = nominal * factor
    return kw


def study_case(name, fam, base_kw, sim, cyc, r_data):
    r0 = sim(build_mat(base_kw, {}))
    mae0 = float(np.mean(np.abs(r0 - r_data)))
    out = dict(name=name, fam=fam, mae0=mae0, params={})
    for p in PARAMS:
        # per-rig extras presentes no cfg tb entram (k_ratchet/delta_free)
        pass
    plist = list(PARAMS)
    for extra in ("k_ratchet", "delta_free"):
        if base_kw.get(extra, 0.0):
            plist.append(extra)
    for p in plist:
        S = {}
        for lbl, f in (("plus", 1.2), ("minus", 1 / 1.2)):
            try:
                r = sim(build_mat(perturb_kw(base_kw, p, f), {}))
                S[lbl] = float(np.mean(np.abs(r - r0)))
            except Exception as ex:
                S[lbl] = None
                print(f"    [warn] {name}/{p} x{f:.2f}: {ex}", flush=True)
        vals = [v for v in S.values() if v is not None]
        S["mean"] = float(np.mean(vals)) if vals else None
        out["params"][p] = S
        print(f"  {name:34s} {p:22s} S={S['mean'] if S['mean'] is None else round(S['mean'],4)}",
              flush=True)
    return out


def main():
    consts, _ = frozen_constants()
    cases, _ = tv.select_cases()
    by = {Path(c.reference_csv_path).stem: c for c in cases}
    results = []

    for stem, extra in TR_CASES:
        case = by[stem]
        inp = tv.inputs_for(case)
        mu = inp["mu"]["value"]
        rz = inp["rz"]["value"]
        emb = emb_depth_vdi(rz, 1)[0] if isinstance(rz, str) and "Rz" in rz else 30e-6
        base = dict(emb_depth=emb, mu_thread=mu, mu_bearing=mu, **PACK, **consts)
        base.update(extra)
        cyc, r = load_full_curve(case.reference_csv_path)
        r = r / r[0]
        sim = lambda m, c=case, cy=cyc: sim_transverse(c, m, cy)
        print(f"[transversal] {stem} (n={int(cyc[-1])})", flush=True)
        results.append(study_case(stem, "transverse", base, sim, cyc, r))

    for (csv, F0, F_amp, bolt, grip, freq, emb_um) in AX_CASES:
        cyc, r = load_full_curve(str(DIG / csv))
        r = r / r[0]
        keep = cyc <= CAP_AX
        cyc, r = cyc[keep], r[keep]
        base = dict(emb_depth=emb_um * 1e-6, mu_thread=0.15, mu_bearing=0.15,
                    **PACK, **consts)
        sim = (lambda m, F0=F0, Fa=F_amp, b=bolt, g=grip, fq=freq, cy=cyc:
               sim_axial(F0, Fa, b, g, fq, m, cy))
        print(f"[axial] {csv} (n={int(cyc[-1])})", flush=True)
        results.append(study_case(csv.replace(".csv", ""), "axial", base, sim, cyc, r))

    out = ROOT / "New_Theory/sensitivity_study.json"
    out.write_text(json.dumps(results, ensure_ascii=False), encoding="utf-8")

    # sumario agregado
    print("\n== RANKING (S medio por familia) ==", flush=True)
    for fam in ("transverse", "axial"):
        agg = {}
        for r_ in results:
            if r_["fam"] != fam:
                continue
            for p, s in r_["params"].items():
                if s["mean"] is not None:
                    agg.setdefault(p, []).append(s["mean"])
        rank = sorted(((np.mean(v), np.max(v), p) for p, v in agg.items()),
                      reverse=True)
        print(f"[{fam}]", flush=True)
        for mean_s, max_s, p in rank:
            print(f"  {p:24s} S_medio={mean_s:.4f}  S_max={max_s:.4f}", flush=True)
    print(f"\nescrito: {out}", flush=True)


if __name__ == "__main__":
    main()
