"""
Primeira calibracao do DynamicStiffnessAnalyzer contra MEAN_nova.

Alvo: New_Theory/M16_shear_MEAN_nova.csv (media de TP3+TP8+TP11)
Loading: M16, +-0.5 mm transverso, 0.5 Hz, 2500 ciclos.

Estrategia:
  1) Roda defaults -> calcula MAE/RMSE baseline.
  2) Otimiza os 3 tuners transversais (k_wear_scale_tr, k_loose_scale_tr,
     Phi_tr_correction) com scipy least_squares.
  3) Plot: ref + default + best-fit, salva PNG, imprime parametros otimos.

Geometria M16:
  d=16e-3 m, p=2.0e-3 m
  d_2 = 16 - 0.6495*2 = 14.701 mm
  A_s ~ 157 mm^2 (ISO 898 nominal)
  L_eff ~ 50 mm (grip de ~30-40 mm + thread + nut em corpo de prova Junker)
  r_bearing ~ 12 mm

Loading shear (pure transverse): theta = pi/2 => F_ax = 0, F_tr = F_amp.
Para +-0.5 mm a 0.5 Hz com bolt-fora-do-furo classico em Junker:
F_amp ~ 20 kN representa o overshoot tipico do crank (>> F_slip ~ 4 kN,
garantindo que sempre estamos em regime de slip).
"""
from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# Adicionar src ao path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)
from scipy.optimize import least_squares, differential_evolution


# ============================================================================
# Configuracao
# ============================================================================

REF_CSV = ROOT / "New_Theory" / "M16_shear_MEAN_nova.csv"
OUT_PNG = ROOT / "New_Theory" / "calibration_shear_mean_nova.png"

# M16 geometria
M16_GEOM = JointGeometry(
    A_s=157e-6,      # m^2 (ISO 898 nominal)
    L_eff=0.050,     # m (50 mm grip tipico Junker M16)
    d_2=14.701e-3,   # m (ISO metric M16)
    pitch=2.0e-3,    # m
    r_bearing=12e-3, # m
    A_contact=1e-4,  # m^2
)

# Loading shear puro
F0_INIT_N = 50_000   # N (50 kN, ~50% yield grade 8.8)
F_AMP_N = 20_000     # N (20 kN, overshoot transverso tipico)
THETA = np.pi / 2    # pure shear
FREQ_HZ = 0.5
N_CYCLES = 2500


# ============================================================================
# Helpers
# ============================================================================

def load_reference(path: Path):
    """Carrega CSV (cycle, F_over_F0) -> tupla de arrays."""
    data = np.genfromtxt(path, delimiter=",", skip_header=1)
    cycles = data[:, 0]
    ratio = data[:, 1]
    return cycles, ratio


def run_sim(mat: JointMaterial, n_cycles: int = N_CYCLES) -> np.ndarray:
    """Roda o analisador, retorna F_0/F_0_init em todos os ciclos."""
    ana = DynamicStiffnessAnalyzer(M16_GEOM, mat, F0_INIT_N)
    ratios = [1.0]
    for _ in range(n_cycles):
        ana.step_cycle(F_AMP_N, THETA, FREQ_HZ)
        ratios.append(max(ana.state.F_0, 0.0) / F0_INIT_N)
    return np.array(ratios)


def evaluate(sim_ratios: np.ndarray, ref_cycles: np.ndarray, ref_ratio: np.ndarray):
    """MAE e RMSE da simulacao interpolada nos ciclos de referencia."""
    all_cycles = np.arange(len(sim_ratios))
    sim_interp = np.interp(ref_cycles, all_cycles, sim_ratios)
    err = sim_interp - ref_ratio
    mae = np.mean(np.abs(err))
    rmse = np.sqrt(np.mean(err ** 2))
    return mae, rmse, sim_interp


PARAM_NAMES = ['k_emb_scale', 'k_creep_scale',
               'k_wear_scale_tr', 'k_loose_scale_tr', 'Phi_tr_correction']


def make_material(params: np.ndarray) -> JointMaterial:
    """Cria JointMaterial mapeando vetor de params -> kwargs."""
    return JointMaterial(**{n: float(v) for n, v in zip(PARAM_NAMES, params)})


def residuals(params: np.ndarray, ref_cycles: np.ndarray, ref_ratio: np.ndarray):
    """Vetor de residuos para least_squares."""
    sim = run_sim(make_material(params))
    all_cycles = np.arange(len(sim))
    sim_interp = np.interp(ref_cycles, all_cycles, sim)
    return sim_interp - ref_ratio


def cost(params: np.ndarray, ref_cycles: np.ndarray, ref_ratio: np.ndarray) -> float:
    """Custo escalar (RMSE) para differential_evolution."""
    r = residuals(params, ref_cycles, ref_ratio)
    return float(np.sqrt(np.mean(r ** 2)))


# ============================================================================
# Main
# ============================================================================

def main():
    print(f"Loading reference: {REF_CSV.name}")
    ref_cycles, ref_ratio = load_reference(REF_CSV)
    print(f"  {len(ref_cycles)} pontos, N={ref_cycles[0]:.0f}-{ref_cycles[-1]:.0f}, "
          f"ratio={ref_ratio[0]:.3f}->{ref_ratio[-1]:.3f}")

    # --- BASELINE: defaults
    print("\n[1] Rodando defaults (todos tuners = 1.0)...")
    mat_default = JointMaterial()
    sim_default = run_sim(mat_default)
    mae_d, rmse_d, _ = evaluate(sim_default, ref_cycles, ref_ratio)
    print(f"  MAE  = {mae_d:.4f}")
    print(f"  RMSE = {rmse_d:.4f}")
    print(f"  Retencao final sim = {sim_default[-1]:.3f}  vs ref = {ref_ratio[-1]:.3f}")

    # --- SWEEP: ver a sensibilidade isolada de cada tuner
    print("\n[2a] Sweep isolado (cada tuner em log-scale, outros=1)...")
    sweep_vals = np.array([0.001, 0.01, 0.1, 1.0, 10.0])
    for i, name in enumerate(PARAM_NAMES):
        row = []
        for v in sweep_vals:
            params = np.ones(len(PARAM_NAMES))
            params[i] = v
            sim = run_sim(make_material(params))
            row.append(sim[-1])
        print(f"  {name:20s}  finais @ {sweep_vals.tolist()} = "
              f"{[f'{r:.3f}' for r in row]}")

    # --- OTIMIZACAO GLOBAL: differential_evolution (gradient-free)
    print("\n[2b] Otimizando 5 tuners (differential_evolution)...")
    bounds = [(1e-4, 5.0)] * 4 + [(0.1, 5.0)]  # 4 rate scales + 1 Phi correction
    result_de = differential_evolution(
        cost, bounds=bounds, args=(ref_cycles, ref_ratio),
        seed=42, maxiter=60, popsize=20, tol=1e-6,
        polish=True, workers=1, disp=False,
    )
    print(f"  DE converged: {result_de.success}, "
          f"iter={result_de.nit}, final cost={result_de.fun:.4f}")

    # Refinar com least_squares partindo do otimo do DE
    print("[2c] Refinando com least_squares...")
    res = least_squares(
        residuals, result_de.x,
        bounds=([1e-4]*4 + [0.1], [5.0]*4 + [5.0]),
        args=(ref_cycles, ref_ratio),
        method='trf', xtol=1e-8, ftol=1e-8, verbose=0,
    )
    k_emb_opt, k_creep_opt, k_wear_opt, k_loose_opt, phi_tr_opt = res.x
    print(f"\n  k_emb_scale      = {k_emb_opt:.4f}")
    print(f"  k_creep_scale    = {k_creep_opt:.4f}")
    print(f"  k_wear_scale_tr  = {k_wear_opt:.4f}")
    print(f"  k_loose_scale_tr = {k_loose_opt:.4f}")
    print(f"  Phi_tr_correction= {phi_tr_opt:.4f}")

    # --- RESULTADOS BEST-FIT
    mat_best = make_material(res.x)
    sim_best = run_sim(mat_best)
    mae_b, rmse_b, sim_best_interp = evaluate(sim_best, ref_cycles, ref_ratio)
    print(f"\n  MAE  = {mae_b:.4f}  (era {mae_d:.4f}, melhora {(1-mae_b/mae_d)*100:.1f}%)")
    print(f"  RMSE = {rmse_b:.4f}  (era {rmse_d:.4f})")
    print(f"  Retencao final = {sim_best[-1]:.3f}  vs ref = {ref_ratio[-1]:.3f}")

    verdict = "PASS" if mae_b < 0.10 else "FAIL"
    print(f"\n  Veredito (MAE < 0.10): {verdict}")

    # --- PLOT
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    all_N = np.arange(len(sim_default))

    ax1.plot(all_N, sim_default, '-', color='gray', alpha=0.7,
             label=f'sim defaults (MAE={mae_d:.3f})')
    ax1.plot(all_N, sim_best, '-', color='C0', linewidth=2,
             label=f'sim best-fit (MAE={mae_b:.3f})')
    ax1.plot(ref_cycles, ref_ratio, 'o', color='C3', markersize=8,
             label='MEAN_nova (ref)')
    ax1.set_xlabel('Ciclos N')
    ax1.set_ylabel(r'$F_0/F_{0,init}$')
    ax1.set_title('Calibracao shear M16 +-0.5mm 0.5Hz')
    ax1.set_xlim(0, N_CYCLES)
    ax1.set_ylim(0, 1.05)
    ax1.grid(alpha=0.3)
    ax1.legend(loc='upper right')

    # Residuos
    err_d = np.interp(ref_cycles, all_N, sim_default) - ref_ratio
    err_b = sim_best_interp - ref_ratio
    ax2.bar(np.arange(len(ref_cycles)) - 0.2, err_d, 0.4,
            color='gray', alpha=0.7, label='defaults')
    ax2.bar(np.arange(len(ref_cycles)) + 0.2, err_b, 0.4,
            color='C0', label='best-fit')
    ax2.set_xticks(np.arange(len(ref_cycles)))
    ax2.set_xticklabels([f"{int(c)}" for c in ref_cycles], rotation=45, fontsize=8)
    ax2.set_xlabel('Ciclos (pontos de referencia)')
    ax2.set_ylabel('Residuo (sim - ref)')
    ax2.axhline(0, color='k', linewidth=0.5)
    ax2.axhline(0.10, color='r', linestyle=':', linewidth=0.5)
    ax2.axhline(-0.10, color='r', linestyle=':', linewidth=0.5)
    ax2.set_title(f'Residuos por ponto (verdict: {verdict})')
    ax2.grid(alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    fig.savefig(OUT_PNG, dpi=120)
    print(f"\n  Plot: {OUT_PNG}")

    # --- JSON export (formato compativel com joint_calibrations.json)
    import json
    profile = {
        "profile_name": "M16_shear_mean_nova",
        "description": "Junker M16 +-0.5mm 0.5Hz, arruela nova, media de TP3+TP8+TP11",
        "calibrated_at": "2026-05-17",
        "geometry": {
            "d": 16e-3, "p": 2.0e-3, "d_2": M16_GEOM.d_2,
            "A_s": M16_GEOM.A_s, "L_eff": M16_GEOM.L_eff,
            "r_bearing": M16_GEOM.r_bearing,
        },
        "loading": {
            "F0_N": F0_INIT_N, "F_amp_N": F_AMP_N,
            "theta_rad": float(THETA), "freq_Hz": FREQ_HZ,
            "n_cycles": N_CYCLES,
        },
        "material": {
            "mu_thread": 0.15, "mu_bearing": 0.15,
            "k_j_init": 4e9, "alpha_GW": 0.5,
        },
        "tuners": {
            "k_emb_scale": float(k_emb_opt),
            "k_creep_scale": float(k_creep_opt),
            "k_wear_scale_ax": 1.0, "k_loose_scale_ax": 1.0,
            "Phi_ax_correction": 1.0,
            "k_wear_scale_tr": float(k_wear_opt),
            "k_loose_scale_tr": float(k_loose_opt),
            "Phi_tr_correction": float(phi_tr_opt),
        },
        "fit_quality": {
            "MAE": float(mae_b), "RMSE": float(rmse_b),
            "verdict": verdict,
            "MAE_default": float(mae_d),
        },
    }
    out_json = ROOT / "New_Theory" / "calibration_shear_mean_nova.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
    print(f"  Profile JSON: {out_json}")


if __name__ == "__main__":
    main()
