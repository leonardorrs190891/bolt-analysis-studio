"""
Calibracao global do DynamicStiffnessAnalyzer contra TODAS as curvas
M16 shear em New_Theory/ (9 individuais + 2 means = 11 CSVs).

Estrategia:
  - Carrega todos os CSVs M16_shear_*.csv da pasta New_Theory.
  - Otimiza 5 tuners (k_emb_scale, k_creep_scale, k_wear_scale_tr,
    k_loose_scale_tr, Phi_tr_correction) com differential_evolution.
  - Cost = MEDIA DE MAE POR CURVA (cada curva pesa igual,
    independente do n de pontos).
  - Refino com least_squares (residuos por-ponto ponderados por 1/sqrt(n_i)
    pra preservar equal-weight-per-curve em sum-of-squares).
  - Plot: todas as 11 curvas + overlay best-fit + 9 individuais coloridas
    por condicao.
  - Salva JSON com os defaults pra colar no calibration_tuner.html.

Output:
  New_Theory/calibration_shear_all_curves.png
  New_Theory/calibration_shear_all_curves.json
"""
from __future__ import annotations

import sys
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)
from scipy.optimize import least_squares, differential_evolution


DATA_DIR = ROOT / "New_Theory"
OUT_PNG = DATA_DIR / "calibration_shear_all_curves.png"
OUT_JSON = DATA_DIR / "calibration_shear_all_curves.json"

# M16 geometria
M16_GEOM = JointGeometry(
    A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
    pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4,
)
F0_INIT_N = 50_000
F_AMP_N = 20_000
THETA = np.pi / 2
FREQ_HZ = 0.5
N_CYCLES = 2500

PARAM_NAMES = ['k_emb_scale', 'k_creep_scale',
               'k_wear_scale_tr', 'k_loose_scale_tr', 'Phi_tr_correction']

COND_COLORS = {
    'nova': '#4F81BD',
    'reusada': '#C00000',
    'sobretorque': '#00B050',
    'reaperto': '#92D050',
}


def load_all_csvs():
    """Le todos M16_shear_*.csv, retorna lista de dicts."""
    files = sorted(DATA_DIR.glob("M16_shear_*.csv"))
    curves = []
    for fp in files:
        data = np.genfromtxt(fp, delimiter=",", skip_header=1)
        cycles = data[:, 0]
        ratio = data[:, 1]
        # Inferir condicao do filename
        name = fp.stem.replace("M16_shear_", "")  # ex: TP3_nova ou MEAN_nova
        parts = name.split("_")
        cond = parts[-1]
        is_mean = name.startswith("MEAN")
        label = name
        curves.append({
            'file': fp.name, 'name': name, 'label': label,
            'condition': cond, 'is_mean': is_mean,
            'cycles': cycles, 'ratio': ratio,
        })
    return curves


def make_material(params: np.ndarray) -> JointMaterial:
    return JointMaterial(**{n: float(v) for n, v in zip(PARAM_NAMES, params)})


def run_sim(mat: JointMaterial, n_cycles: int = N_CYCLES) -> np.ndarray:
    ana = DynamicStiffnessAnalyzer(M16_GEOM, mat, F0_INIT_N)
    ratios = [1.0]
    for _ in range(n_cycles):
        ana.step_cycle(F_AMP_N, THETA, FREQ_HZ)
        ratios.append(max(ana.state.F_0, 0.0) / F0_INIT_N)
    return np.array(ratios)


def cost_per_curve_equal(params: np.ndarray, curves) -> float:
    """Custo: media de MAE por curva (cada curva pesa igual)."""
    sim = run_sim(make_material(params))
    all_N = np.arange(len(sim))
    maes = []
    for c in curves:
        sim_interp = np.interp(c['cycles'], all_N, sim)
        mae = np.mean(np.abs(sim_interp - c['ratio']))
        maes.append(mae)
    return float(np.mean(maes))


def residuals_weighted(params: np.ndarray, curves) -> np.ndarray:
    """Residuos por-ponto ponderados por 1/sqrt(n_i) pra equal-weight-per-curve."""
    sim = run_sim(make_material(params))
    all_N = np.arange(len(sim))
    all_res = []
    for c in curves:
        sim_interp = np.interp(c['cycles'], all_N, sim)
        r = sim_interp - c['ratio']
        w = 1.0 / np.sqrt(len(r))
        all_res.extend(r * w)
    return np.array(all_res)


def per_curve_metrics(params: np.ndarray, curves):
    sim = run_sim(make_material(params))
    all_N = np.arange(len(sim))
    rows = []
    for c in curves:
        sim_interp = np.interp(c['cycles'], all_N, sim)
        err = sim_interp - c['ratio']
        rows.append({
            'name': c['name'],
            'mae': float(np.mean(np.abs(err))),
            'rmse': float(np.sqrt(np.mean(err**2))),
            'final_ref': float(c['ratio'][-1]),
            'final_sim': float(sim_interp[-1]),
        })
    return rows


def main():
    print(f"Loading all M16_shear_*.csv from {DATA_DIR}...")
    curves = load_all_csvs()
    print(f"  Loaded {len(curves)} curves:")
    for c in curves:
        tag = "[MEAN]" if c['is_mean'] else "[indiv]"
        print(f"    {tag} {c['name']:25s}  n={len(c['cycles']):3d}  "
              f"final={c['ratio'][-1]:.3f}")

    # --- BASELINE
    print("\n[1] Baseline (todos tuners = 1.0):")
    x_default = np.ones(len(PARAM_NAMES))
    baseline_cost = cost_per_curve_equal(x_default, curves)
    print(f"  Mean-MAE-per-curve = {baseline_cost:.4f}")

    # --- DE global
    print("\n[2] differential_evolution (5D, popsize=25, maxiter=80)...")
    bounds = [(1e-4, 10.0)] * 4 + [(0.05, 5.0)]
    result_de = differential_evolution(
        cost_per_curve_equal, bounds=bounds, args=(curves,),
        seed=42, maxiter=80, popsize=25, tol=1e-7,
        polish=True, workers=1, disp=False, mutation=(0.4, 1.5),
    )
    print(f"  DE: success={result_de.success}, iter={result_de.nit}, "
          f"final cost={result_de.fun:.4f}")

    # --- Refino least_squares
    print("[3] Refino least_squares (weighted residuals)...")
    res = least_squares(
        residuals_weighted, result_de.x,
        bounds=([1e-4]*4 + [0.05], [10.0]*4 + [5.0]),
        args=(curves,),
        method='trf', xtol=1e-9, ftol=1e-9, verbose=0,
    )
    x_best = res.x
    best_cost = cost_per_curve_equal(x_best, curves)
    print(f"  Best mean-MAE = {best_cost:.4f}  "
          f"(melhora {(1 - best_cost/baseline_cost)*100:.1f}%)")

    print("\n[4] Parametros otimos (defaults pra calibration_tuner.html):")
    for name, val in zip(PARAM_NAMES, x_best):
        print(f"  {name:20s} = {val:.4f}")

    # --- Metrics per curve
    print("\n[5] MAE por curva no best-fit:")
    rows = per_curve_metrics(x_best, curves)
    for r in rows:
        flag = "[PASS]" if r['mae'] < 0.10 else "[FAIL]"
        print(f"  {flag} {r['name']:25s}  MAE={r['mae']:.3f}  "
              f"final ref={r['final_ref']:.3f} vs sim={r['final_sim']:.3f}")
    n_pass = sum(1 for r in rows if r['mae'] < 0.10)
    print(f"\n  Verdict: {n_pass}/{len(rows)} curvas com MAE < 0.10")

    # --- PLOT
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    all_N = np.arange(len(run_sim(make_material(x_default))))

    # Esquerda: defaults vs best-fit overlay com todas as curvas
    sim_def = run_sim(make_material(x_default))
    sim_best = run_sim(make_material(x_best))

    ax = axes[0]
    for c in curves:
        if c['is_mean']:
            continue  # so individuais no plot principal
        col = COND_COLORS.get(c['condition'], '#888')
        ax.plot(c['cycles'], c['ratio'], 'o-', color=col, alpha=0.45,
                markersize=4, linewidth=0.7)
    # Mean curves grossas
    for c in curves:
        if not c['is_mean']:
            continue
        col = COND_COLORS.get(c['condition'], '#888')
        ax.plot(c['cycles'], c['ratio'], 's-', color=col, alpha=0.85,
                markersize=8, linewidth=2, label=f"{c['name']}")
    # Best-fit
    ax.plot(all_N, sim_best, 'k-', linewidth=2.5,
            label=f'best-fit (cost={best_cost:.3f})')
    ax.plot(all_N, sim_def, 'k--', linewidth=1, alpha=0.4,
            label=f'defaults (cost={baseline_cost:.3f})')
    ax.set_xlabel('Ciclos N')
    ax.set_ylabel(r'$F_0/F_{0,init}$')
    ax.set_title('Calibracao global vs todas as 9 specimens')
    ax.set_xlim(0, N_CYCLES)
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.3)
    ax.legend(loc='upper right', fontsize=8)

    # Direita: barplot MAE por curva
    ax = axes[1]
    names = [r['name'] for r in rows]
    maes = [r['mae'] for r in rows]
    colors = [COND_COLORS.get(r['name'].split('_')[-1], '#888') for r in rows]
    bars = ax.barh(range(len(names)), maes, color=colors, alpha=0.85)
    ax.axvline(0.10, color='r', linestyle=':', linewidth=1, label='MAE=0.10 threshold')
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel('MAE')
    ax.set_title(f'MAE por curva ({n_pass}/{len(rows)} PASS)')
    ax.invert_yaxis()
    ax.grid(alpha=0.3, axis='x')
    ax.legend(loc='lower right')

    plt.tight_layout()
    fig.savefig(OUT_PNG, dpi=120)
    print(f"\n  Plot: {OUT_PNG}")

    # --- JSON
    out = {
        "profile_name": "M16_shear_all_curves_global_fit",
        "description": ("Fit global considerando 9 specimens individuais + 2 means "
                        "(M16, +-0.5mm, 0.5Hz). Estes valores devem virar os defaults "
                        "do calibration_tuner.html."),
        "calibrated_at": "2026-05-17",
        "loading": {
            "F0_N": F0_INIT_N, "F_amp_N": F_AMP_N,
            "theta_rad": float(THETA), "freq_Hz": FREQ_HZ,
            "n_cycles": N_CYCLES,
        },
        "tuners": {n: float(v) for n, v in zip(PARAM_NAMES, x_best)},
        "tuners_default_per_axial": {
            "k_wear_scale_ax": 1.0,
            "k_loose_scale_ax": 1.0,
            "Phi_ax_correction": 1.0,
        },
        "fit_quality": {
            "mean_MAE_per_curve": float(best_cost),
            "baseline_mean_MAE": float(baseline_cost),
            "n_pass": n_pass, "n_total": len(rows),
            "per_curve": rows,
        },
    }
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"  JSON: {OUT_JSON}")


if __name__ == "__main__":
    main()
