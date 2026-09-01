"""Confronto ZERO-REFIT do canal de rotacao: theta_loose do engine vs as 6
curvas theta(N) medidas (theta_csv, Rousseau Figs 4/5) — o dado theta nunca
entrou em calibracao. Configs = as ADOTADAS da galeria (aco sec4.12 pack;
HDPE sec4.20 member-shear + F_eff). Item 3 (regimes): a relacao de helice
dF0 = k_eff*(p/2pi)*theta quantifica no DADO a fracao da perda carregada por
rotacao (aco ~rotacao-dominada; HDPE ~rotacao-menor) — comparada a decomposicao
do modelo (share rotational_loosening).

Gates pre-declarados: G-T1 ordem theta_fim t10>t12>t14 nos 2 materiais (modelo);
G-T2 colapsantes dentro de fator-3 do medido (free-spin pos-descarga e' fora de
modelo); t14s <= 4 deg. Verdict sec4.23 AS-IS.

Run: python -u New_Theory/theta_confront.py
"""
from __future__ import annotations
import io
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
import transfer_validation as tv  # noqa: E402
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)
from library_common import geometry_for, frozen_constants, load_full_curve  # noqa: E402

LIB = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library"
PACK = dict(conform_driver="effective", slip_regime_mode="cattaneo_mindlin",
            slip_regime_sharpness=1.0, k_tr_mode="bending",
            loose_torsion_mode="bolt_torsion", eta_loose=15.0, loose_arrest_floor=0.08)
HDPE_CFG = dict(GA=8e4, c_bend=4.0, k_creep=1.0, floor=0.28, emb_um=2.0)
HDPE_CASES = [("t10", 25.0, 10250.0, 0.010), ("t12", 29.0, 10250.0, 0.012),
              ("t14", 33.0, 10350.0, 0.014)]


def theta_meas(mat, t):
    f = LIB / "theta_csv" / f"rousseau2025_theta_{mat}_{t}.csv"
    cyc, deg = [], []
    for ln in io.open(f, encoding="utf-8"):
        if ln.strip() and not ln.startswith(("#", "cycle")):
            a, b = ln.split(",")[:2]
            cyc.append(float(a)); deg.append(float(b))
    return np.array(cyc), np.array(deg)


def run_steel(stem):
    cases, _ = tv.select_cases()
    by = {Path(c.reference_csv_path).stem: c for c in cases}
    case = by[stem]
    consts, _ = frozen_constants()
    inp = tv.inputs_for(case)
    geom = geometry_for(case.bolt_size, grip_mm=inp["grip_mm"]["value"])
    mu = inp["mu"]["value"]
    mat = JointMaterial(emb_depth=1.5e-6, mu_thread=mu, mu_bearing=mu,
                        **PACK, **consts)
    F0 = case.initial_preload_N
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    cyc, ratio = load_full_curve(case.reference_csv_path)
    n_max = int(cyc[-1])
    delta = case.transverse_displacement_mm * 1e-3
    F_amp = inp["F_amp_N"]["value"]
    th = np.empty(n_max + 1); th[0] = 0.0
    r = np.empty(n_max + 1); r[0] = 1.0
    cum = {}
    for n in range(1, n_max + 1):
        ana.step_cycle(F_amp, np.pi / 2, case.frequency_Hz, delta_amp=delta)
        th[n] = np.degrees(ana.state.theta_loose)
        r[n] = max(ana.state.F_0, 0.0) / F0
        for m, dF in ana.history[-1].dF_0_by_mech.items():
            cum[m] = cum.get(m, 0.0) + dF
    return th, r, F0, geom, mat, cum, n_max


def run_hdpe(name, grip, F0, t_m):
    consts, _ = frozen_constants()
    geom = geometry_for("M12x1.75", grip)
    k_m = HDPE_CFG["GA"] / t_m
    I = np.pi * geom.d_2 ** 4 / 64
    k_ser = 1.0 / (1.0 / max(HDPE_CFG["c_bend"] * geom.E * I / geom.L_eff ** 3, 1.0) + 1.0 / k_m)
    F_eff = min(0.4 * F0, k_ser * 0.5e-3)
    mat = JointMaterial(emb_depth=HDPE_CFG["emb_um"] * 1e-6, mu_thread=0.15,
                        mu_bearing=0.15, k_j_init=2.0e7, k_member_shear=k_m,
                        k_creep_scale=HDPE_CFG["k_creep"], c_bend=HDPE_CFG["c_bend"],
                        loose_arrest_floor=HDPE_CFG["floor"],
                        **{k: v for k, v in PACK.items() if k != "loose_arrest_floor"},
                        **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    th = np.empty(401); th[0] = 0.0
    r = np.empty(401); r[0] = 1.0
    cum = {}
    for n in range(1, 401):
        ana.step_cycle(F_eff, np.pi / 2, 1.0, delta_amp=0.5e-3)
        th[n] = np.degrees(ana.state.theta_loose)
        r[n] = max(ana.state.F_0, 0.0) / F0
        for m, dF in ana.history[-1].dF_0_by_mech.items():
            cum[m] = cum.get(m, 0.0) + dF
    return th, r, F0, geom, mat, cum, 400


def helix_rot_fraction(theta_deg_fim, F0, r_fim, geom, mat):
    """Fracao da perda que a rotacao medida explicaria via helice (dado)."""
    k_eff = 1.0 / (1.0 / geom.k_b + 1.0 / mat.k_j_init)
    dF_rot = k_eff * (geom.pitch / (2 * np.pi)) * np.radians(theta_deg_fim)
    loss = F0 * (1.0 - r_fim)
    return min(dF_rot / max(loss, 1e-9), 9.99), k_eff


def main():
    rows = []
    for matname, runs in [("steel", [("t10",), ("t12",), ("t14",)]),
                          ("hdpe", HDPE_CASES)]:
        for entry in runs:
            if matname == "steel":
                t = entry[0]
                th, r, F0, geom, jm, cum, nmax = run_steel(f"rousseau2025_steel_{t}")
            else:
                t = entry[0]
                th, r, F0, geom, jm, cum, nmax = run_hdpe(*entry)
            cyc_m, deg_m = theta_meas(matname, t)
            th_fim_m = float(deg_m[-1])
            th_fim = float(th[-1])
            tot = sum(abs(v) for v in cum.values()) or 1.0
            share_rot_model = abs(cum.get("rotational_loosening", 0.0)) / tot
            frac_data, k_eff = helix_rot_fraction(th_fim_m, F0, float(
                np.interp(cyc_m[-1], np.arange(nmax + 1), r)), geom, jm)
            rows.append((matname, t, th_fim, th_fim_m, share_rot_model, frac_data))
            print(f"{matname}_{t}: theta_fim mod {th_fim:6.2f} vs MEDIDO {th_fim_m:6.2f} deg | "
                  f"share rot (modelo) {share_rot_model:4.0%} | "
                  f"helice*theta_medido/perda (dado) {frac_data:4.2f} | k_eff {k_eff:.2e}")
    print("\n=== GATES (pre-declarados) ===")
    for mn in ("steel", "hdpe"):
        fs = [r for r in rows if r[0] == mn]
        order = fs[0][2] > fs[1][2] > fs[2][2]
        print(f"G-T1 {mn}: ordem modelo t10>t12>t14: {order} "
              f"({fs[0][2]:.1f}/{fs[1][2]:.1f}/{fs[2][2]:.1f} vs medido "
              f"{fs[0][3]:.1f}/{fs[1][3]:.1f}/{fs[2][3]:.1f})")
    g2 = []
    for mn, t, m, d, *_ in rows:
        if t == "t14":
            g2.append((f"{mn}_t14", m <= 4.0, f"mod {m:.1f} <= 4"))
        else:
            fac = max(m, 1e-3) / max(d, 1e-3)
            g2.append((f"{mn}_{t}", 1 / 3 <= fac <= 3, f"fator {fac:.2f}"))
    for name, ok, note in g2:
        print(f"G-T2 {name}: {'PASS' if ok else 'FAIL'} ({note})")


if __name__ == "__main__":
    main()
