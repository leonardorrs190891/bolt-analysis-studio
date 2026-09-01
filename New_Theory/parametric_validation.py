"""
Parametric-sweep generalization harness — the decisive "model vs curve-fitting"
test once the campaign in
`docs/superpowers/specs/2026-06-20-generalization-validation-campaign.md` is run.

Calibrate ONE shared tuner set on a subset of loading conditions (same surface
state, varying delta/F0), then PREDICT held-out conditions. Low out-of-sample
error with one parameter set = generalization = physics, not curve-fitting.

Modes:
  * Real data — if `New_Theory/sweep_manifest.csv` exists, load it and run the
    hold-out prediction tests (leave-one-delta-out, leave-one-F0-out, leave-one-
    cell-out).
  * Synthetic self-test (default when no manifest) — generate data from the model
    itself at known "true" tuners + measurement noise, then run the same hold-out.
    OOS error ~ noise level proves (a) the harness works and (b) the model
    generalizes to its OWN parametric sweep (a necessary internal sanity check).

Run:  python New_Theory/parametric_validation.py
"""
from __future__ import annotations

import sys
import csv
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

# Windows console defaults to cp1252, which can't encode the Greek δ in our
# labels — force utf-8 stdout (charmap gotcha).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)

DATA = ROOT / "New_Theory"
MANIFEST = DATA / "sweep_manifest.csv"
M16 = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)
THETA = np.pi / 2
F_AMP_FRAC = 0.4   # transverse force drive as fraction of F0 (disp-mode convention)

TUNERS = ["k_emb_scale", "k_creep_scale", "k_wear_scale_tr",
          "k_loose_scale_tr", "Phi_tr_correction"]
LO = np.array([1e-3, 1e-3, 1e-3, 1e-3, 0.05])
HI = np.array([5.0, 5.0, 5.0, 5.0, 5.0])


def simulate(tuners, F0, delta_mm, freq, n_cycles):
    mat = JointMaterial(**{t: float(v) for t, v in zip(TUNERS, tuners)})
    ana = DynamicStiffnessAnalyzer(M16, mat, float(F0))
    ratio = [1.0]
    for _ in range(int(n_cycles)):
        ana.step_cycle(F_AMP_FRAC * F0, THETA, freq, delta_amp=delta_mm * 1e-3)
        ratio.append(max(ana.state.F_0, 0.0) / F0)
    return np.arange(int(n_cycles) + 1), np.array(ratio)


def mae_test(tuners, t):
    N, R = simulate(tuners, t["F0_N"], t["delta_mm"], t["freq"], t["n_cycles"])
    return float(np.mean(np.abs(np.interp(t["cycles"], N, R) - t["ratio"])))


def fit_shared(tests):
    """One shared tuner set across all tests (each runs with its own F0/delta)."""
    def resid(x):
        out = []
        for t in tests:
            N, R = simulate(x, t["F0_N"], t["delta_mm"], t["freq"], t["n_cycles"])
            out.extend(np.interp(t["cycles"], N, R) - t["ratio"])
        return np.array(out)
    res = least_squares(resid, np.ones(len(TUNERS)), bounds=(LO, HI),
                        method="trf", xtol=1e-8, ftol=1e-8,
                        max_nfev=80, diff_step=1e-3)   # diff_step > any rounding
    return res.x


def holdout(tests, key, label):
    print(f"\n  hold-out por {label}:")
    print(f"    {'nivel retido':16s} {'MAE_pred(OOS)':>14s} {'MAE_proprio':>12s} {'gap':>8s}")
    levels = sorted(set(round(t[key], 6) for t in tests))
    rows = []
    for lv in levels:
        train = [t for t in tests if round(t[key], 6) != lv]
        held = [t for t in tests if round(t[key], 6) == lv]
        if not train or not held:
            continue
        x = fit_shared(train)
        pred = float(np.mean([mae_test(x, t) for t in held]))
        x_own = fit_shared(held)
        own = float(np.mean([mae_test(x_own, t) for t in held]))
        rows.append((lv, pred, own))
        print(f"    {lv:<16g} {pred:14.4f} {own:12.4f} {pred-own:+8.4f}")
    return rows


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_manifest():
    tests = []
    with MANIFEST.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            d = np.genfromtxt(DATA / row["csv_path"], delimiter=",", skip_header=1)
            tests.append({
                "id": row["id"], "delta_mm": float(row["delta_mm"]),
                "F0_N": float(row["F0_N"]), "freq": float(row["freq_Hz"]),
                "n_cycles": int(row["n_cycles"]),
                "cycles": d[:, 0], "ratio": d[:, 1],
            })
    return tests


def make_synthetic():
    """Generate a δ×F0 sweep from the model at known tuners + measurement noise."""
    rng = np.random.default_rng(0)
    true = np.array([1.30, 1.00, 0.70, 1.00, 1.00])   # "true" tuners
    ref_cycles = np.array([0, 20, 50, 100, 200, 400, 700, 1100, 1600, 2200, 2500],
                          dtype=float)
    tests = []
    i = 0
    for delta in (0.30, 0.50, 0.70):
        for F0 in (40_000.0, 60_000.0):
            N, R = simulate(true, F0, delta, 0.5, 2500)
            clean = np.interp(ref_cycles, N, R)
            noisy = np.clip(clean + rng.normal(0, 0.01, clean.size), 0, 1)
            i += 1
            tests.append({"id": f"SYN{i:02d}", "delta_mm": delta, "F0_N": F0,
                          "freq": 0.5, "n_cycles": 2500,
                          "cycles": ref_cycles, "ratio": noisy})
    return tests, true


def main():
    if MANIFEST.exists():
        print(f"DADOS REAIS — manifesto {MANIFEST.name}")
        tests = load_manifest()
        synthetic = False
    else:
        print("AUTO-TESTE SINTETICO (sem manifesto) — dados gerados do modelo + ruido 1%")
        print("Prova que o arnes funciona e que o modelo generaliza pra sua propria varredura.")
        tests, true = make_synthetic()
        synthetic = True

    print(f"\n{len(tests)} ensaios | "
          f"delta={sorted(set(t['delta_mm'] for t in tests))} mm | "
          f"F0={sorted(set(t['F0_N']/1e3 for t in tests))} kN")

    print("\n" + "=" * 70)
    print("GENERALIZACAO — calibra set unico no treino, prediz o retido")
    print("=" * 70)
    holdout(tests, "delta_mm", "amplitude δ (interpola/extrapola)")
    holdout(tests, "F0_N", "pre-carga F0 (cross-preload)")

    if synthetic:
        x = fit_shared(tests)
        print("\n  recuperacao dos tuners 'true' (fit em tudo):")
        for t, v, tr in zip(TUNERS, x, true):
            print(f"     {t:20s} fit {v:6.3f}  (true {tr:5.2f})")
        print("\n  LEITURA: OOS ~ nivel de ruido (0.01) => arnes OK + modelo")
        print("  generaliza pra sua propria varredura. Com dados REAIS de bancada,")
        print("  o mesmo OOS pequeno seria a prova de 'modelo, nao curve-fitting'.")
    else:
        print("\n  LEITURA: OOS <= ~1.5x o scatter entre replicas => generaliza")
        print("  (modelo). Gap grande sistematico => mecanismo faltante (ver")
        print("  MODEL_LEGITIMACY.md §7).")


if __name__ == "__main__":
    main()
