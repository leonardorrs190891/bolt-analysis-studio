"""
Identifiability + parsimony analysis of the DynamicStiffnessAnalyzer calibration.

Question (Prof. Leonardo): with 5+ tuners fitting a ~13-point monotonic decay,
is the model physics or just a multivariable curve-fit?

This script answers with numbers, per profile:

  1. OPTIMUM        — global fit of the 5 tuners + MAE.
  2. SLOPPINESS     — eigenvalues of J^T J in RELATIVE coords. A model is
                      "sloppy" (non-identifiable) when the spectrum spans many
                      decades. #(eigvals within 1e-3 of the top) = effective
                      number of identifiable parameter COMBINATIONS.
  3. CONFIDENCE     — per-tuner 95% CI from cov = sigma^2 (J^T J)^-1. A tuner
                      whose CI is wider than its bound range is NOT determined
                      by the data (the data doesn't pin it).
  4. PARSIMONY      — ablation: fix each tuner at 1.0, re-fit the rest, report
                      delta-MAE. Then greedily drop tuners while MAE stays within
                      tolerance -> the minimal sufficient model.

Run:  python New_Theory/identifiability_analysis.py
"""
from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)

DATA = ROOT / "New_Theory"
M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)
F0, F_AMP, DELTA, THETA, FREQ, NCYC = 50_000.0, 20_000.0, 0.5e-3, np.pi / 2, 0.5, 2500

TUNERS = ["k_emb_scale", "k_creep_scale", "k_wear_scale_tr",
          "k_loose_scale_tr", "Phi_tr_correction"]
BOUNDS_LO = np.array([1e-3, 1e-3, 1e-3, 1e-3, 0.05])
BOUNDS_HI = np.array([5.0, 5.0, 5.0, 5.0, 5.0])


def load_curve(name):
    d = np.genfromtxt(DATA / f"M16_shear_{name}.csv", delimiter=",", skip_header=1)
    return d[:, 0], d[:, 1]


def sim_at(x, ref_cycles, fixed=None):
    """Simulate with tuner vector x (only the free entries) and return the
    model ratio interpolated at ref_cycles. `fixed` overrides specific tuners."""
    kw = {t: float(v) for t, v in zip(TUNERS, x)}
    if fixed:
        kw.update(fixed)
    ana = DynamicStiffnessAnalyzer(M16, JointMaterial(**kw), F0)
    ratio = [1.0]
    for _ in range(NCYC):
        ana.step_cycle(F_AMP, THETA, FREQ, delta_amp=DELTA)
        ratio.append(max(ana.state.F_0, 0.0) / F0)
    allN = np.arange(NCYC + 1)
    return np.interp(ref_cycles, allN, np.array(ratio))


def residuals(x, refN, refR):
    return sim_at(x, refN) - refR


def fit_full(refN, refR, x0=None):
    x0 = np.ones(5) if x0 is None else x0
    res = least_squares(residuals, x0, bounds=(BOUNDS_LO, BOUNDS_HI),
                        args=(refN, refR), method="trf", xtol=1e-9, ftol=1e-9,
                        max_nfev=80)
    mae = float(np.mean(np.abs(res.fun)))
    return res.x, mae, res.fun


def jacobian(x, refN, refR):
    """Central finite-difference Jacobian dr/dx."""
    r0 = residuals(x, refN, refR)
    J = np.zeros((len(r0), len(x)))
    for i in range(len(x)):
        h = max(1e-4, 0.02 * abs(x[i]))
        xp, xm = x.copy(), x.copy()
        xp[i] += h; xm[i] -= h
        J[:, i] = (residuals(xp, refN, refR) - residuals(xm, refN, refR)) / (2 * h)
    return J


def analyse(name, n_ref="MEAN_nova"):
    refN, refR = load_curve(n_ref)
    x, mae, r = fit_full(refN, refR)
    print(f"\n{'='*70}\nPERFIL: {name}  (ref={n_ref}, {len(refN)} pontos)\n{'='*70}")
    print("1) OTIMO  MAE = %.4f" % mae)
    for t, v in zip(TUNERS, x):
        print(f"     {t:20s} = {v:7.3f}")

    # --- 2) Sloppiness: eigvals of J^T J in RELATIVE coords (scale by x) ---
    J = jacobian(x, refN, refR)
    S = np.diag(np.maximum(np.abs(x), 1e-3))          # relative scaling
    Jr = J @ S
    JtJ_rel = Jr.T @ Jr
    eig = np.sort(np.linalg.eigvalsh(JtJ_rel))[::-1]
    eig = np.maximum(eig, 0.0)
    top = eig[0] if eig[0] > 0 else 1.0
    stiff = int(np.sum(eig > top * 1e-3))             # within 3 decades of top
    print("\n2) SLOPPINESS (autovalores relativos de J^T J, normalizados):")
    print("     " + "  ".join(f"{e/top:.2e}" for e in eig))
    print(f"     razao max/min = {top/max(eig[-1],1e-30):.1e}   "
          f"direcoes 'stiff' (>1e-3) = {stiff}/{len(eig)}")
    print(f"     => ~{stiff} combinacao(oes) de parametros realmente determinada(s) pelo dado")

    # --- 3) Confidence intervals from cov = sigma^2 (J^T J)^-1 ---
    N, p = len(r), len(x)
    sse = float(np.sum(r ** 2))
    sigma2 = sse / max(N - p, 1)
    JtJ = J.T @ J
    print("\n3) INTERVALO DE CONFIANCA 95% por tuner (cov = sigma^2 (JtJ)^-1):")
    try:
        cov = sigma2 * np.linalg.inv(JtJ)
        for i, t in enumerate(TUNERS):
            ci = 1.96 * np.sqrt(max(cov[i, i], 0.0))
            span = BOUNDS_HI[i] - BOUNDS_LO[i]
            frac = ci / span
            verdict = "DETERMINADO" if frac < 0.25 else ("fraco" if frac < 1.0 else "NAO determinado")
            print(f"     {t:20s} = {x[i]:6.3f} +/- {ci:7.3f}  "
                  f"({100*frac:5.0f}% do range)  -> {verdict}")
    except np.linalg.LinAlgError:
        print("     JtJ singular -> ha direcoes totalmente nao-identificaveis (sloppy).")

    # --- 4) Parsimony: ablation (fix each tuner at 1.0, re-fit rest) ---
    print("\n4) PARCIMONIA — ablacao (fixa tuner=1.0, reajusta o resto):")
    free_idx = list(range(5))
    base_mae = mae
    for i, t in enumerate(TUNERS):
        def res_fixed(xf, refN=refN, refR=refR, i=i):
            xx = x.copy(); xx[i] = 1.0
            for j, jj in enumerate([k for k in range(5) if k != i]):
                xx[jj] = xf[j]
            return sim_at(xx, refN) - refR
        x0 = np.delete(x, i)
        lo = np.delete(BOUNDS_LO, i); hi = np.delete(BOUNDS_HI, i)
        rr = least_squares(res_fixed, x0, bounds=(lo, hi), method="trf",
                           xtol=1e-9, ftol=1e-9, max_nfev=50)
        mae_ab = float(np.mean(np.abs(rr.fun)))
        d = mae_ab - base_mae
        tag = "DESNECESSARIO" if d < 0.005 else ("marginal" if d < 0.02 else "necessario")
        print(f"     sem {t:20s}: MAE {mae_ab:.4f}  (dMAE {d:+.4f})  -> {tag}")

    # --- greedy minimal model ---
    print("\n   Modelo minimo (guloso, tolerancia dMAE<0.01 vs otimo):")
    fixed = {}
    cur_free = list(TUNERS)
    while True:
        best = None
        for t in cur_free:
            trial_fixed = dict(fixed); trial_fixed[t] = 1.0
            free = [u for u in TUNERS if u not in trial_fixed]
            if not free:
                continue
            def res_g(xf, free=free, trial_fixed=trial_fixed):
                kw = dict(trial_fixed)
                kw.update({f: v for f, v in zip(free, xf)})
                xx = np.array([kw[t2] for t2 in TUNERS])
                return sim_at(xx, refN) - refR
            x0 = np.ones(len(free))
            lo = np.array([BOUNDS_LO[TUNERS.index(f)] for f in free])
            hi = np.array([BOUNDS_HI[TUNERS.index(f)] for f in free])
            rr = least_squares(res_g, x0, bounds=(lo, hi), method="trf",
                               xtol=1e-9, ftol=1e-9, max_nfev=50)
            m = float(np.mean(np.abs(rr.fun)))
            if best is None or m < best[1]:
                best = (t, m)
        if best is None or best[1] > base_mae + 0.01:
            break
        fixed[best[0]] = 1.0
        cur_free = [u for u in TUNERS if u not in fixed]
        print(f"     fixar {best[0]:20s} -> MAE {best[1]:.4f}  (livres: {cur_free})")
    print(f"   => conjunto minimo suficiente: {cur_free or ['(nenhum — defaults bastam)']}")


def analyse_shared():
    """Identifiabilidade do FIT COMPARTILHADO (constantes fisicas, log-espaco):
    espectro de J^T J + CIs por constante. Le o bloco `shared` gravado pelo
    calibrate_shared.py e re-avalia os residuos em torno do otimo."""
    import json
    sys.path.insert(0, str(DATA))
    from calibrate_shared import build_shared_config
    from bolt_analysis_studio.calibration.shared_calibrator import SharedCalibrator

    saved = json.loads((DATA / "joint_calibrations.json").read_text(encoding="utf-8"))
    shared = saved["shared"]
    free = list(shared["free_constants"])
    cfg = build_shared_config(n_cycles=shared["loading"]["n_cycles"])
    cal = SharedCalibrator(cfg)
    cal.constants.update({k: float(v) for k, v in shared["constants"].items()
                          if k in cal.constants})
    f0_names = []
    for name, c in shared["conditions"].items():
        if c["states"].get("F0_provenance") == "estimated":
            cal.F0_estimates[name] = float(c["states"]["F0_test_N"])
            f0_names.append(name)

    labels = free + [f"F0_test[{n}]" for n in f0_names]
    x = np.array([np.log(cal.constants[k]) for k in free]
                 + [np.log(cal.F0_estimates[n]) for n in f0_names])
    r0 = cal._residuals(x, free, f0_names)

    print(f"\n{'='*70}\nFIT COMPARTILHADO (log-espaco, {len(labels)} variaveis, "
          f"{len(r0)} residuos)\n{'='*70}")
    print("otimo: " + "  ".join(f"{l}={np.exp(v):.4g}" for l, v in zip(labels, x)))

    J = np.zeros((len(r0), len(x)))
    for i in range(len(x)):
        h = 0.02
        xp, xm = x.copy(), x.copy()
        xp[i] += h; xm[i] -= h
        J[:, i] = (cal._residuals(xp, free, f0_names)
                   - cal._residuals(xm, free, f0_names)) / (2 * h)
    # log-espaco ja e relativo — sem re-escalar
    JtJ = J.T @ J
    eig = np.maximum(np.sort(np.linalg.eigvalsh(JtJ))[::-1], 0.0)
    top = eig[0] if eig[0] > 0 else 1.0
    stiff = int(np.sum(eig > top * 1e-3))
    print("\nSLOPPINESS (autovalores de J^T J, log-espaco, normalizados):")
    print("  " + "  ".join(f"{e/top:.2e}" for e in eig))
    print(f"  direcoes stiff (>1e-3) = {stiff}/{len(eig)}")

    N, p = len(r0), len(x)
    sigma2 = float(np.sum(r0 ** 2)) / max(N - p, 1)
    print("\nIC 95% por variavel (multiplicativo, cov = sigma^2 (JtJ)^-1):")
    try:
        cov = sigma2 * np.linalg.inv(JtJ)
        for i, l in enumerate(labels):
            ci = 1.96 * np.sqrt(max(cov[i, i], 0.0))
            verdict = ("DETERMINADO" if ci < 0.3
                       else ("fraco" if ci < 1.0 else "NAO determinado"))
            print(f"  {l:20s} = {np.exp(x[i]):.4g}  x/ {np.exp(ci):.2f}"
                  f"  -> {verdict}")
    except np.linalg.LinAlgError:
        print("  JtJ singular -> direcoes totalmente nao-identificaveis.")


def main():
    if "--shared" in sys.argv:
        analyse_shared()
        return
    analyse("nova", "MEAN_nova")
    analyse("reusada", "MEAN_reusada")
    print("\n" + "="*70)
    print("LEITURA: poucas direcoes 'stiff' + CIs largos = o dado nao pina todos")
    print("os tuners (modelo sloppy/sobre-parametrizado nessa curva). O conjunto")
    print("minimo mostra quantos botoes a curva realmente sustenta.")


if __name__ == "__main__":
    main()
