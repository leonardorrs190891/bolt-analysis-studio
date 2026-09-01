"""Sub-campanha C — ancora independente de C_creep (spec 2026-07-03 §1.7).

Creep ESTATICO li2022marstruc (M16 304SS, sem vibracao, eixo x em MINUTOS):
isola o mecanismo de creep. Fit declarado de {C_creep + emb_depth por Ra}
(5 parametros, 6 curvas); depois re-roda o Estagio A com o prior de C_creep
re-centrado na ancora (cross-material: 304SS != par UFU — re-centra, nao
substitui por decreto).

Run:  python New_Theory/anchor_creep.py [--skip-stage-a]
Runtime: ancora ~segundos; re-run do Estagio A ~6 min.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial,
)
from library_common import (  # noqa: E402
    frozen_constants, geometry_for, load_full_curve,
)

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"

# Aparato (nota li2022_marstruc_contact_creep.md — proveniencia 'paper'):
# M16x80 304SS E=193 GPa, grip L=20 mm, contato 60x60. Curvas comecam no
# primeiro registro pos-aperto (96.7-100.4%) -> alinhamento no 1o ponto.
GEOM = geometry_for("M16x2.0", grip_mm=20.0, E=193e9)
FREQ_STATIC = 1.0 / 60.0          # 1 pseudo-ciclo = 1 minuto

CURVES_DEF = [
    # csv, F0 [N], Ra [um]
    (f"{DIG}/li2022marstruc_creep_10kN_Ra0p078_min.csv", 10e3, 0.078),
    (f"{DIG}/li2022marstruc_creep_10kN_Ra0p122_min.csv", 10e3, 0.122),
    (f"{DIG}/li2022marstruc_creep_10kN_Ra0p306_min.csv", 10e3, 0.306),
    (f"{DIG}/li2022marstruc_creep_10kN_Ra0p8_min.csv",   10e3, 0.8),
    (f"{DIG}/li2022marstruc_creep_5kN_Ra0p8_min.csv",     5e3, 0.8),
    (f"{DIG}/li2022marstruc_creep_15kN_Ra0p8_min.csv",   15e3, 0.8),
]
BOUNDS_C = (1e-13, 1e-9)
BOUNDS_EMB = (1e-8, 20e-6)


def simulate_static(F0_N, C_creep, emb_depth_m, n_min, K_archard=1e-4,
                    tr_loose_gain=2.0):
    """Modo estatico: F_amp=0 (sem slip => wear/loosening inertes),
    freq=1/60 Hz => t = N minutos. Retorna ratio[0..n_min]."""
    consts, _ = frozen_constants()
    consts = dict(consts, C_creep=C_creep, K_archard=K_archard,
                  tr_loose_gain=tr_loose_gain)
    mat = JointMaterial(emb_depth=emb_depth_m, **consts)
    ana = DynamicStiffnessAnalyzer(GEOM, mat, F0_N)
    out = np.empty(n_min + 1)
    out[0] = 1.0
    for n in range(1, n_min + 1):
        ana.step_cycle(0.0, 0.0, FREQ_STATIC)
        out[n] = max(ana.state.F_0, 0.0) / F0_N
    return out


def _load_curves():
    out = []
    for csv, F0, ra in CURVES_DEF:
        mins, ratio = load_full_curve(csv)
        out.append(dict(name=Path(csv).stem, F0_N=F0, Ra_um=ra,
                        minutes=mins, ratio=ratio))
    return out


def fit_anchor(curves):
    """Fit conjunto log-espaco: x = [ln C, ln emb_Ra...] (Ra em ordem de
    aparicao). Retorna ancora + CI linearizado + MAE por curva."""
    ra_levels = []
    for c in curves:
        if c["Ra_um"] not in ra_levels:
            ra_levels.append(c["Ra_um"])

    def unpack(x):
        C = float(np.exp(x[0]))
        embs = {ra: float(np.exp(v)) for ra, v in zip(ra_levels, x[1:])}
        return C, embs

    def resid(x):
        C, embs = unpack(x)
        out = []
        for c in curves:
            n_max = int(c["minutes"][-1])
            sim = simulate_static(c["F0_N"], C, embs[c["Ra_um"]], n_max)
            m0 = c["minutes"][0]
            data_al = c["ratio"] / c["ratio"][0]
            sim_al = sim / max(np.interp(m0, np.arange(n_max + 1), sim), 1e-9)
            pred = np.interp(c["minutes"], np.arange(n_max + 1), sim_al)
            out.extend((pred - data_al) / np.sqrt(len(data_al)))
        return np.array(out)

    x0 = [np.log(5e-11)] + [np.log(2e-6)] * len(ra_levels)
    lo = [np.log(BOUNDS_C[0])] + [np.log(BOUNDS_EMB[0])] * len(ra_levels)
    hi = [np.log(BOUNDS_C[1])] + [np.log(BOUNDS_EMB[1])] * len(ra_levels)
    res = least_squares(resid, x0, bounds=(lo, hi), method="trf",
                        xtol=1e-10, ftol=1e-10, diff_step=1e-3, max_nfev=200)
    C, embs = unpack(res.x)
    # CI linearizado (log-espaco): cov = sigma^2 (JtJ)^-1
    r0 = resid(res.x)
    J = np.zeros((len(r0), len(res.x)))
    for i in range(len(res.x)):
        xp, xm = res.x.copy(), res.x.copy()
        xp[i] += 0.02
        xm[i] -= 0.02
        J[:, i] = (resid(xp) - resid(xm)) / 0.04
    sigma2 = float(np.sum(r0 ** 2)) / max(len(r0) - len(res.x), 1)
    try:
        ci = float(np.exp(1.96 * np.sqrt(
            max((sigma2 * np.linalg.inv(J.T @ J))[0, 0], 0.0))))
    except np.linalg.LinAlgError:
        ci = float("inf")
    # MAE por curva no otimo
    maes = {}
    for c in curves:
        n_max = int(c["minutes"][-1])
        sim = simulate_static(c["F0_N"], C, embs[c["Ra_um"]], n_max)
        m0 = c["minutes"][0]
        data_al = c["ratio"] / c["ratio"][0]
        sim_al = sim / max(np.interp(m0, np.arange(n_max + 1), sim), 1e-9)
        maes[c["name"]] = float(np.mean(np.abs(
            np.interp(c["minutes"], np.arange(n_max + 1), sim_al) - data_al)))
    return dict(C_creep_anchor=C, ci_factor=ci,
                emb_depth_um_by_Ra={str(ra): embs[ra] * 1e6 for ra in ra_levels},
                mae_by_curve=maes, n_params=len(res.x), n_points=len(r0))


def rerun_stage_a(anchor, ci_factor):
    """Re-roda o Estagio A com prior de C_creep re-centrado (spec §1.7)."""
    from calibrate_shared import build_shared_config
    from bolt_analysis_studio.calibration.shared_calibrator import SharedCalibrator
    cfg = build_shared_config(n_cycles=2500)
    f2 = min(max(ci_factor, 1.5), 10.0) ** 2
    lo = max(anchor / f2, 1e-13)
    hi = min(anchor * f2, 1e-9)
    cfg.priors["C_creep"] = anchor
    cfg.bounds["C_creep"] = (lo, hi)
    res = SharedCalibrator(cfg).fit_parsimonious(tol=0.005, max_constants=4)
    return dict(prior=anchor, bounds=[lo, hi],
                free_constants=res["free_constants"],
                C_creep_fitted=res["constants"]["C_creep"],
                mae_global=res["mae_global"],
                mae_by_condition=res["mae_by_condition"],
                F0_estimates=res["F0_estimates"])


def main():
    curves = _load_curves()
    anchor = fit_anchor(curves)
    print("== ancora de C_creep (li2022marstruc, estatico) ==")
    print(f"C_creep = {anchor['C_creep_anchor']:.4g}  x/ {anchor['ci_factor']:.2f}"
          f"  (Estagio A: 1.165e-11, IC x/2.30)")
    for ra, e in anchor["emb_depth_um_by_Ra"].items():
        print(f"  emb_depth(Ra={ra}) = {e:.3f} um")
    for n, m in anchor["mae_by_curve"].items():
        print(f"  MAE {n} = {m:.4f}")

    # conservacao no modo estatico (spec §5): so emb+creep ativos => ~0
    C, embs = anchor["C_creep_anchor"], anchor["emb_depth_um_by_Ra"]
    consts0, _ = frozen_constants()
    mat0 = JointMaterial(emb_depth=embs["0.8"] * 1e-6,
                         **dict(consts0, C_creep=C))
    ana0 = DynamicStiffnessAnalyzer(GEOM, mat0, 10e3)
    for _ in range(600):
        ana0.step_cycle(0.0, 0.0, FREQ_STATIC)
    resid_static = float(ana0.energy.conservation_residual)
    print(f"residual de conservacao (estatico, 10kN, 600 min): {resid_static:.3e}")

    # plot 2x3
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, c in zip(axes.flat, curves):
        n_max = int(c["minutes"][-1])
        sim = simulate_static(c["F0_N"], C, embs[str(c["Ra_um"])] * 1e-6, n_max)
        m0 = c["minutes"][0]
        data_al = c["ratio"] / c["ratio"][0]
        sim_al = sim / max(np.interp(m0, np.arange(n_max + 1), sim), 1e-9)
        ax.plot(c["minutes"], data_al, "o-", ms=3, label="dado")
        ax.plot(np.arange(n_max + 1), sim_al, "k-",
                label=f"fit (MAE={anchor['mae_by_curve'][c['name']]:.3f})")
        ax.set_title(f"F0={c['F0_N']/1e3:g}kN Ra={c['Ra_um']}", fontsize=9)
        ax.set_xlabel("min")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
    plt.tight_layout()
    fig.savefig(ROOT / "New_Theory" / "creep_anchor.png", dpi=110)

    stage_a = None
    if "--skip-stage-a" not in sys.argv:
        print("\n== re-run do Estagio A com prior re-centrado (~6 min) ==")
        stage_a = rerun_stage_a(anchor["C_creep_anchor"], anchor["ci_factor"])
        print(f"antes: C_creep=1.165e-11, MAE global 0.0796")
        print(f"depois: C_creep={stage_a['C_creep_fitted']:.4g}, "
              f"MAE global {stage_a['mae_global']:.4f}, "
              f"livres={stage_a['free_constants']}")

    out = dict(campaign="C anchor (spec 2026-07-03 §1.7)",
               provenance=dict(
                   geometry="paper (li2022_marstruc: M16x80 304SS E=193GPa, L=20mm)",
                   x_axis="minutos (1 pseudo-ciclo = 1 min, freq=1/60 Hz)",
                   cross_material="304SS != par UFU: ancora re-centra o prior"),
               conservation_residual_static=resid_static,
               anchor=anchor, stage_a_rerun=stage_a)
    (ROOT / "New_Theory" / "creep_anchor.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Ancora de C_creep — creep estatico (spec 2026-07-03 §1.7)", "",
             f"C_creep = {anchor['C_creep_anchor']:.4g} x/ {anchor['ci_factor']:.2f} "
             f"(Estagio A: 1.165e-11 x/2.30)", "",
             "| Curva | MAE |", "|---|---:|"]
    lines += [f"| {n} | {m:.4f} |" for n, m in anchor["mae_by_curve"].items()]
    if stage_a:
        lines += ["", f"Re-run Estagio A: C_creep {stage_a['C_creep_fitted']:.4g}, "
                  f"MAE global {stage_a['mae_global']:.4f} (antes 0.0796), "
                  f"livres {stage_a['free_constants']}"]
    (ROOT / "New_Theory" / "creep_anchor_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("Artefatos: creep_anchor.json, creep_anchor.png, creep_anchor_report.md")


if __name__ == "__main__":
    main()
