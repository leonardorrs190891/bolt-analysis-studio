"""
Calibracao isolada por condicao: 4 perfis separados, agora via StagedCalibrator.

Cada perfil eh fitado em estagios (coord-descida I->II->III com travas e
regularizacao fisica fraca) contra apenas as curvas da sua condicao. Perfis
com colapso forte (reaperto, reusada) ligam o surface_damage.

Output:
  New_Theory/joint_calibrations.json     (4 perfis)
  New_Theory/calibration_4_profiles.png  (2x2 grid)
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointGeometry
from bolt_analysis_studio.calibration.segmentation import StageSegmentation
from bolt_analysis_studio.calibration.staged_calibrator import (
    CalibrationConfig, StagedCalibrator,
)
from bolt_analysis_studio.calibration.profiles import upsert_profiles_bundle

DATA_DIR = ROOT / "New_Theory"
OUT_PNG = DATA_DIR / "calibration_4_profiles.png"
OUT_JSON = DATA_DIR / "joint_calibrations.json"

M16_GEOM = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                         pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)
F0_INIT_N, F_AMP_N, DELTA_AMP_M = 50_000.0, 20_000.0, 0.5e-3
THETA, FREQ_HZ, N_CYCLES = np.pi / 2, 0.5, 2500
BOUNDS = {
    "k_emb_scale": (1e-3, 5.0), "k_creep_scale": (1e-3, 5.0),
    "k_wear_scale_tr": (1e-3, 5.0), "k_loose_scale_tr": (1e-3, 5.0),
    "Phi_tr_correction": (0.05, 5.0), "k_damage_scale": (1e-3, 5.0),
}
# perfis com colapso forte ligam o surface_damage
DAMAGE_PROFILES = {"reaperto", "reusada"}

PROFILES = {
    'nova':        ['TP3_nova', 'TP8_nova', 'TP11_nova', 'MEAN_nova'],
    'reusada':     ['TP4_reusada', 'TP5_reusada', 'TP9_reusada', 'TP10_reusada',
                    'MEAN_reusada'],
    'sobretorque': ['TP6_sobretorque'],
    'reaperto':    ['TP7_reaperto'],
}
COND_COLORS = {'nova': '#4F81BD', 'reusada': '#C00000',
               'sobretorque': '#00B050', 'reaperto': '#92D050'}


def load_curves(names):
    out = []
    for name in names:
        d = np.genfromtxt(DATA_DIR / f"M16_shear_{name}.csv",
                          delimiter=",", skip_header=1)
        out.append({'name': name, 'cycles': d[:, 0], 'ratio': d[:, 1]})
    return out


def calibrate_one(cond_name, curve_names):
    print(f"\n[{cond_name}] curvas: {curve_names}")
    curves = load_curves(curve_names)
    cfg = CalibrationConfig(
        geom=M16_GEOM, F0_init=F0_INIT_N, F_amp=F_AMP_N, theta=THETA,
        freq=FREQ_HZ, n_cycles=N_CYCLES, delta_amp=DELTA_AMP_M,
        segmentation=StageSegmentation(100, 1000, N_CYCLES),
        lambda_reg=0.001, bounds=BOUNDS,
        fit_damage=(cond_name in DAMAGE_PROFILES),
    )
    cal = StagedCalibrator(cfg, curves)
    # Parcimonia por default: forward selection -> conjunto minimo de tuners
    # que o dado justifica (anti-overfitting; ver MODEL_LEGITIMACY.md §4.4).
    res = cal.fit_parsimonious(tol=0.005, max_tuners=4)
    sim_N, sim_ratio, _ = cal._run_sim()
    print(f"  MAE global={res['mae_global']:.4f}  "
          f"free={res['free_tuners']}  D_init={round(res['D_init'], 3)}")
    print(f"  selecao={[(c, round(m, 4)) for c, m in res['selection_history']]}")
    profile = {
        'profile_name': f"M16_shear_{cond_name}",
        'condition': cond_name,
        'calibrated_at': date.today().isoformat(),
        'calibration_method': 'parsimonious (forward selection, tol=0.005)',
        'loading': {'F0_N': F0_INIT_N, 'F_amp_N': F_AMP_N,
                    'theta_rad': float(THETA), 'freq_Hz': FREQ_HZ,
                    'n_cycles': N_CYCLES, 'D_init': res['D_init']},
        'damage_active': cond_name in DAMAGE_PROFILES,
        'free_tuners': res['free_tuners'],
        'tuners': res['tuners'],
        'fit_quality': {
            'mean_MAE_global': res['mae_global'],
            'n_free_tuners': len(res['free_tuners']),
            'selection_history': [[c, m] for c, m in res['selection_history']],
        },
    }
    return profile, curves, (sim_N, sim_ratio)


def main():
    profiles, plot_data = {}, {}
    for cond, names in PROFILES.items():
        prof, curves, sim = calibrate_one(cond, names)
        profiles[cond] = prof
        plot_data[cond] = (curves, sim)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for ax, (cond, prof) in zip(axes.flat, profiles.items()):
        curves, (sim_N, sim_ratio) = plot_data[cond]
        col = COND_COLORS[cond]
        for c in curves:
            ls = '-' if c['name'].startswith('MEAN') else ':'
            ax.plot(c['cycles'], c['ratio'], ls, color=col, alpha=0.8,
                    marker='o', markersize=4, label=c['name'])
        ax.plot(sim_N, sim_ratio, 'k-', linewidth=2.5,
                label=f"sim (MAE={prof['fit_quality']['mean_MAE_global']:.3f})")
        ax.set_xlabel('Ciclos N'); ax.set_ylabel(r'$F_0/F_{0,init}$')
        ax.set_title(f"Perfil: {cond}")
        ax.set_xlim(0, N_CYCLES); ax.set_ylim(0, 1.05); ax.grid(alpha=0.3)
        ax.legend(loc='upper right', fontsize=8)
    plt.tight_layout()
    fig.savefig(OUT_PNG, dpi=120)
    print(f"\nPlot: {OUT_PNG}")

    upsert_profiles_bundle(
        OUT_JSON,
        description=("4 perfis M16 shear +-0.5mm 0.5Hz calibrados em estagios "
                     "(StagedCalibrator) com surface_damage nos perfis "
                     "reaperto/reusada."),
        global_settings={
            'geometry': 'M16 ISO metric (d_2=14.701mm, p=2.0mm, A_s=157mm2)',
            'loading': 'shear puro +-0.5mm 0.5Hz, F0=50kN, F_amp=20kN',
        },
        profiles=profiles)
    print(f"JSON: {OUT_JSON} (profiles atualizado; bloco shared preservado)")


if __name__ == "__main__":
    main()
