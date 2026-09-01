"""Calibracao COMPARTILHADA (Estagio A, spec 2026-07-02): UMA fisica para as
4 condicoes M16 shear +-0.5mm 0.5Hz; condicoes diferem so por estados nomeados
(D_init, emb_consumed_frac, F0_test). Tuners nunca sao fitados (ficam em 1.0).

CONFORMACAO ADOTADA (2026-07-04, decisao do professor): a fisica compartilhada
agora inclui o mecanismo de conformacao dependente de pressao com o driver
auto-limitante 'effective' (spec §7; MODEL_LEGITIMACY §4.9 strand 2), que resolve
a falsificacao estrutural do sobretorque (§4.5). n=2/p_ref=5e8 fixos; W_conf_ref
fitado (oferecido ao fit_parsimonious so sob pressao elevada). A adocao e inline
em main() — build_shared_config segue PURO (base OFF/raw) para preservar os
experimentos strand-1/2 (conformation_fit.py).

Output:
  New_Theory/joint_calibrations.json   (bloco `shared`, schema 2; `profiles` preservado)
  New_Theory/calibration_shared.png    (grid 2x2, MESMAS constantes nas 4)

Run:  python New_Theory/calibrate_shared.py [--quick]
  --quick: n_cycles=600 (smoke; NAO gravar como resultado cientifico)
Runtime esperado do run completo: ~1-3 h (forward selection x 4 condicoes
x 2500 ciclos por avaliacao + LOCO).
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointGeometry
from bolt_analysis_studio.calibration.shared_calibrator import (
    ConditionSpec, SharedCalibrationConfig, SharedCalibrator,
)
from bolt_analysis_studio.calibration.profiles import upsert_shared

DATA_DIR = ROOT / "New_Theory"
OUT_JSON = DATA_DIR / "joint_calibrations.json"
OUT_PNG = DATA_DIR / "calibration_shared.png"

M16_GEOM = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                         pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)
F0_NOM_N, F_AMP_N, DELTA_AMP_M = 50_000.0, 20_000.0, 0.5e-3
THETA, FREQ_HZ = np.pi / 2, 0.5

# Estados nomeados por condicao (spec §2.3). sobretorque: F0 estimado (§2.3
# fallback — usuario nao tem o registro do ensaio TP6).
CONDITIONS_DEF = {
    "nova": dict(
        curves=["TP3_nova", "TP8_nova", "TP11_nova", "MEAN_nova"],
        states={}),
    "reusada": dict(
        curves=["TP4_reusada", "TP5_reusada", "TP9_reusada", "TP10_reusada",
                "MEAN_reusada"],
        states=dict(D_init=0.3, emb_consumed_frac=1.0, damage_active=True)),
    "sobretorque": dict(
        curves=["TP6_sobretorque"],
        states={}),
    "reaperto": dict(
        curves=["TP7_reaperto"],
        states=dict(D_init=0.3, damage_active=True)),
}
BOUNDS = {
    "emb_depth": (5e-6, 80e-6), "N_emb": (10.0, 200.0),
    "K_archard": (1e-5, 1e-3), "C_creep": (1e-12, 1e-9),
    "tr_loose_gain": (0.5, 10.0), "c_D": (0.5, 8.0), "k_dmg_wear": (0.5, 8.0),
}
ESTIMATE_F0 = {"sobretorque": (40_000.0, 120_000.0)}
# sanity §2.3: F0_test <= 0.9 * Rp0.2 * A_s (M16 10.9: 0.9*940MPa*157mm2)
F0_SANITY_N = 0.9 * 940e6 * 157e-6
COND_COLORS = {"nova": "#4F81BD", "reusada": "#C00000",
               "sobretorque": "#00B050", "reaperto": "#92D050"}


def load_curves(names):
    out = []
    for name in names:
        d = np.genfromtxt(DATA_DIR / f"M16_shear_{name}.csv",
                          delimiter=",", skip_header=1)
        out.append({"name": name, "cycles": d[:, 0], "ratio": d[:, 1]})
    return out


def build_shared_config(n_cycles: int = 2500) -> SharedCalibrationConfig:
    conds = []
    for name, spec in CONDITIONS_DEF.items():
        s = spec["states"]
        conds.append(ConditionSpec(
            name=name, curves=load_curves(spec["curves"]),
            F0_init=F0_NOM_N, F_amp=F_AMP_N, delta_amp=DELTA_AMP_M,
            D_init=s.get("D_init", 0.0),
            emb_consumed_frac=s.get("emb_consumed_frac", 0.0),
            damage_active=s.get("damage_active", False)))
    return SharedCalibrationConfig(
        geom=M16_GEOM, conditions=conds, theta=THETA, freq=FREQ_HZ,
        n_cycles=n_cycles, bounds=BOUNDS, estimate_F0=ESTIMATE_F0)


def main():
    n_cycles = 600 if "--quick" in sys.argv else 2500
    cfg = build_shared_config(n_cycles)
    # ===== Conformacao dependente de pressao ADOTADA no bloco canonico
    # (2026-07-04, decisao do professor): driver auto-limitante 'effective'
    # (spec §7; MODEL_LEGITIMACY §4.9 strand 2 — RESOLVED e mais limpo que o
    # raw). n=2 e p_ref=5e8 FIXOS (nao fitados); W_conf_ref fitavel, oferecido
    # ao fit_parsimonious pelo registry so sob pressao elevada (sobretorque, F0
    # estimado). Resolve a falsificacao estrutural do sobretorque (§4.5).
    # build_shared_config fica PURO (base OFF/raw) para nao quebrar os
    # experimentos strand-1/2 (conformation_fit.py); a adocao e aqui, inline. =====
    cfg.priors = dict(cfg.priors, W_conf_ref=1e5,
                      conform_pressure_exp=2.0, p_ref_conform=5.0e8)
    cfg.bounds = dict(cfg.bounds, W_conf_ref=(1e3, 1e8))
    cfg.conform_driver = "effective"
    # emb_depth e um INPUT por-junta (tabela VDI 2230 f_Z por rugosidade), NAO um
    # knob fitavel (CLAUDE.md gotcha). Decisao do professor 2026-07-04: com a
    # conformacao ativa, mante-lo FIXO no default e preservar o C_creep ancorado
    # (§4.7) como 2a constante — procedencia/fisica acima de MAE de ultima casa
    # (o fit livre pegava emb_depth=17um, global 0.0456, mas DERRUBAVA o C_creep).
    cfg.bounds = {k: v for k, v in cfg.bounds.items() if k != "emb_depth"}
    cal = SharedCalibrator(cfg)

    print("== fit_parsimonious (constantes fisicas compartilhadas + conformacao) ==")
    # max_constants=4: o F0_test estimado do sobretorque ocupa 1 slot do
    # orcamento de <=5 numeros fitados no dataset inteiro (spec §5.1).
    res = cal.fit_parsimonious(tol=0.005, max_constants=4)
    print(f"constantes livres: {res['free_constants']}")
    for k in res["free_constants"]:
        print(f"  {k:15s} = {res['constants'][k]:.4g}"
              f"   (prior {cfg.priors[k]:.4g})")
    for name, f0 in res["F0_estimates"].items():
        ok = "OK" if f0 <= F0_SANITY_N else "ACIMA DO SANITY (!)"
        print(f"  F0_test[{name}] = {f0/1e3:.1f} kN  "
              f"(sanity <= {F0_SANITY_N/1e3:.0f} kN: {ok})")
    print(f"MAE global = {res['mae_global']:.4f}")
    for name, mae in res["mae_by_condition"].items():
        print(f"  MAE {name:12s} = {mae:.4f}")
    print(f"selecao: {[(c, round(m, 4)) for c, m in res['selection_history']]}")

    print("\n== LOCO (leave-one-condition-out) ==")
    loco = cal.loco(res["free_constants"])
    for name, r in loco.items():
        star = "  [F0 do fit completo]" if r["state_F0_from_full_fit"] else ""
        print(f"  {name:12s} MAE_pred = {r['MAE_pred']:.4f}{star}")

    # ---- plot: as MESMAS constantes nas 4 condicoes ----
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for ax, cond in zip(axes.flat, cfg.conditions):
        sim_N, sim_ratio = cal._run_condition(cond)
        col = COND_COLORS[cond.name]
        for c in cond.curves:
            ls = "-" if c["name"].startswith("MEAN") else ":"
            ax.plot(c["cycles"], c["ratio"], ls, color=col, alpha=0.8,
                    marker="o", markersize=4, label=c["name"])
        ax.plot(sim_N, sim_ratio, "k-", linewidth=2.5,
                label=(f"sim compartilhada "
                       f"(MAE={res['mae_by_condition'][cond.name]:.3f})"))
        ax.set_xlabel("Ciclos N"); ax.set_ylabel(r"$F_0/F_{0,init}$")
        ax.set_title(f"{cond.name} — fisica COMPARTILHADA, estados nomeados")
        ax.set_xlim(0, n_cycles); ax.set_ylim(0, 1.05); ax.grid(alpha=0.3)
        ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    fig.savefig(OUT_PNG, dpi=120)
    print(f"\nPlot: {OUT_PNG}")

    if "--quick" in sys.argv:
        print("--quick: NAO gravando bloco shared (resultado nao-cientifico).")
        return

    shared = {
        "calibrated_at": date.today().isoformat(),
        "method": "SharedCalibrator.fit_parsimonious (tol=0.005, log-priors); "
                  "conformacao dependente de pressao ADOTADA (driver effective, spec §7); "
                  "emb_depth mantido como INPUT fixo (nao-candidato, decisao 2026-07-04)",
        "conformation": {
            "driver": cfg.conform_driver,
            "conform_pressure_exp": cfg.priors["conform_pressure_exp"],
            "p_ref_conform": cfg.priors["p_ref_conform"],
            "adopted": "2026-07-04 — resolve a falsificacao do sobretorque "
                       "(MODEL_LEGITIMACY §4.9 strand 2); n/p_ref fixos, "
                       "W_conf_ref fitado, sem ancora independente (§4.9 strand 3)",
        },
        "loading": {"F_amp_N": F_AMP_N, "delta_amp_m": DELTA_AMP_M,
                    "theta_rad": float(THETA), "freq_Hz": FREQ_HZ,
                    "n_cycles": n_cycles},
        "free_constants": res["free_constants"],
        "constants": res["constants"],
        "selection_history": [[c, m] for c, m in res["selection_history"]],
        "mae_global": res["mae_global"],
        "conditions": {},
        "loco": {name: r for name, r in loco.items()},
    }
    for cond in cfg.conditions:
        states = {}
        if cond.D_init:
            states["D_init"] = cond.D_init
        if cond.emb_consumed_frac:
            states["emb_consumed_frac"] = cond.emb_consumed_frac
        if cond.name in res["F0_estimates"]:
            states["F0_test_N"] = res["F0_estimates"][cond.name]
            states["F0_provenance"] = "estimated"
        else:
            states["F0_N"] = cond.F0_init
            states["F0_provenance"] = "nominal"
        shared["conditions"][cond.name] = {
            "states": states,
            "damage_active": cond.damage_active,
            "MAE": res["mae_by_condition"][cond.name],
        }
    upsert_shared(OUT_JSON, shared)
    print(f"JSON: {OUT_JSON} (bloco shared, schema 2; profiles preservado)")


if __name__ == "__main__":
    main()
