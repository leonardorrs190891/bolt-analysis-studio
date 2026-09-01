"""
Cross-condition validation of the DynamicStiffnessAnalyzer — the decisive test
of "physics vs curve-fitting": does a parameter set generalize OUT-OF-SAMPLE?

Uses the M16 shear studies in this folder (digitized from shear.jpeg):
  nova         TP3, TP8, TP11, MEAN_nova
  reusada      TP4, TP5, TP9, TP10, MEAN_reusada
  sobretorque  TP6
  reaperto     TP7

Three tests:
  1. REPRODUTIBILIDADE  — leave-one-CURVE-out within a condition. Fit on the
     other replicates, predict the held-out one. If pred-MAE ~ fit-MAE the model
     captures the condition, not the noise of one replicate.
  2. TAXA DE BESPOKE    — one SHARED tuner set across all conditions vs each
     condition fit on its own. The gap = how much per-condition tuning each case
     needs (the curve-fitting tax).
  3. GENERALIZACAO      — leave-one-CONDITION-out. Fit shared tuners on the other
     conditions, PREDICT the held-out condition's curve (true out-of-sample).

All tests use the 5 standard tuners (no surface_damage) so it's apples-to-apples;
reaperto is expected to be the outlier that needs the damage MECHANISM (a physical
extension, not arbitrary tuning) — that itself is informative.

Run:  python New_Theory/cross_validation.py
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
LO = np.array([1e-3, 1e-3, 1e-3, 1e-3, 0.05])
HI = np.array([5.0, 5.0, 5.0, 5.0, 5.0])

CONDITIONS = {
    "nova":        ["TP3_nova", "TP8_nova", "TP11_nova", "MEAN_nova"],
    "reusada":     ["TP4_reusada", "TP5_reusada", "TP9_reusada", "TP10_reusada",
                    "MEAN_reusada"],
    "sobretorque": ["TP6_sobretorque"],
    "reaperto":    ["TP7_reaperto"],
}
REPRESENTATIVE = {"nova": "MEAN_nova", "reusada": "MEAN_reusada",
                  "sobretorque": "TP6_sobretorque", "reaperto": "TP7_reaperto"}


def load_curve(name):
    d = np.genfromtxt(DATA / f"M16_shear_{name}.csv", delimiter=",", skip_header=1)
    return d[:, 0], d[:, 1]


_SIM_CACHE = {}


def sim_curve(x):
    """Full simulated ratio array for tuner vector x (cached).

    Cache key is the EXACT float tuple — rounding it (e.g. to 1e-6) would be
    coarser than least_squares' finite-difference step (~1e-8), making the
    optimiser read an identical cached curve -> zero gradient -> stuck at x0.
    """
    key = tuple(float(v) for v in x)
    if key in _SIM_CACHE:
        return _SIM_CACHE[key]
    kw = {t: float(v) for t, v in zip(TUNERS, x)}
    ana = DynamicStiffnessAnalyzer(M16, JointMaterial(**kw), F0)
    ratio = [1.0]
    for _ in range(NCYC):
        ana.step_cycle(F_AMP, THETA, FREQ, delta_amp=DELTA)
        ratio.append(max(ana.state.F_0, 0.0) / F0)
    out = (np.arange(NCYC + 1), np.array(ratio))
    _SIM_CACHE[key] = out
    return out


def mae_on(x, curves):
    simN, simR = sim_curve(x)
    errs = []
    for cN, cR in curves:
        errs.append(np.abs(np.interp(cN, simN, simR) - cR))
    return float(np.mean(np.concatenate(errs)))


def fit(curves, x0=None):
    def resid(x):
        simN, simR = sim_curve(x)
        out = []
        for cN, cR in curves:
            out.extend(np.interp(cN, simN, simR) - cR)
        return np.array(out)
    res = least_squares(resid, np.ones(5) if x0 is None else x0,
                        bounds=(LO, HI), method="trf",
                        xtol=1e-8, ftol=1e-8, max_nfev=60, diff_step=1e-3)
    return res.x, mae_on(res.x, curves)


def test1_reproducibility():
    print("\n" + "=" * 70)
    print("TESTE 1 — REPRODUTIBILIDADE (leave-one-curve-out dentro da condicao)")
    print("=" * 70)
    for cond in ("nova", "reusada"):
        names = CONDITIONS[cond]
        print(f"\n  [{cond}] {len(names)} curvas")
        for held in names:
            train = [load_curve(n) for n in names if n != held]
            x, fit_mae = fit(train)
            pred_mae = mae_on(x, [load_curve(held)])
            print(f"     held-out {held:16s}: pred MAE {pred_mae:.4f}  "
                  f"(fit-on-rest {fit_mae:.4f})  gap {pred_mae-fit_mae:+.4f}")


def test2_bespoke_tax():
    print("\n" + "=" * 70)
    print("TESTE 2 — TAXA DE BESPOKE (1 set compartilhado vs por-condicao)")
    print("=" * 70)
    reps = {c: load_curve(REPRESENTATIVE[c]) for c in CONDITIONS}
    x_shared, _ = fit(list(reps.values()))
    print(f"  set compartilhado: {dict(zip(TUNERS,[round(v,2) for v in x_shared]))}")
    print(f"  {'condicao':14s} {'MAE_proprio':>12s} {'MAE_compart':>12s} {'tax':>8s}")
    for c, (cN, cR) in reps.items():
        x_own, mae_own = fit([(cN, cR)])
        mae_sh = mae_on(x_shared, [(cN, cR)])
        print(f"  {c:14s} {mae_own:12.4f} {mae_sh:12.4f} {mae_sh-mae_own:+8.4f}")


def test3_generalization():
    print("\n" + "=" * 70)
    print("TESTE 3 — GENERALIZACAO (leave-one-CONDITION-out -> predicao out-of-sample)")
    print("=" * 70)
    reps = {c: load_curve(REPRESENTATIVE[c]) for c in CONDITIONS}
    print(f"  {'condicao retida':16s} {'MAE_pred (OOS)':>15s} {'MAE_proprio':>12s} {'gap':>8s}")
    for held in CONDITIONS:
        train = [reps[c] for c in CONDITIONS if c != held]
        x, _ = fit(train)
        pred = mae_on(x, [reps[held]])
        _, own = fit([reps[held]])
        flag = "" if pred - own < 0.03 else "  <- nao generaliza (mecanismo faltante?)"
        print(f"  {held:16s} {pred:15.4f} {own:12.4f} {pred-own:+8.4f}{flag}")


def main():
    test1_reproducibility()
    test2_bespoke_tax()
    test3_generalization()
    print("\n" + "=" * 70)
    print("LEITURA:")
    print(" T1 gap pequeno  => fit nao decora ruido de uma replica (bom).")
    print(" T2 tax pequena  => um set fisico cobre a condicao (generaliza).")
    print(" T3 gap pequeno  => prediz condicao nao vista = MODELO; gap grande =")
    print("    a condicao exige tuning proprio (curve-fitting) OU um mecanismo")
    print("    fisico faltante (ex: reaperto precisa de surface_damage).")


if __name__ == "__main__":
    main()
