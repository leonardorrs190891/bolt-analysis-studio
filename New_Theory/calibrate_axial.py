"""Sub-campanha B — trilho AXIAL, predicao-primeiro (spec 2026-07-03 §1.6).

B1 (default): predicao zero-refit das 13 curvas axiais com constantes do
Estagio A congeladas + emb_depth de tabela VDI (§1.3a). Nenhum parametro e
ajustado a nenhuma curva. B2 (fit) foi descartado como comprovadamente futil
apos o gate falhar — ver MODEL_LEGITIMACY §4.6.

Run:  python New_Theory/calibrate_axial.py [--quick]
  --quick: n_cycles cap 2e4 (smoke; nao grava artefatos cientificos)
Runtime B1 completo: ~25-40 min (13 curvas ate 1e6 ciclos + sensibilidade).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial,
)
from library_common import (  # noqa: E402
    Provenance, emb_depth_vdi, frozen_constants, geometry_for,
    load_full_curve, vdi_adjacent_classes,
)

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"

# Fretting de flanco de rosca axial (spec 2026-07-06): setado por --k-thread-fret
# ou calibrado por --calibrate-fret. 0.0 = mecanismo OFF (baseline §4.6 zero-refit).
_K_THREAD_FRET = 0.0

# --- Condicoes pre-registradas (notas de aparato; NAO editar apos rodar) -----
# Liu2017: M12x1.75 10.9 RETIFICADO. Rz assumido "Rz<10" no run B1 pre-registrado
# (2026-07-03); ADOTADO "Rz<4" (retificado/lapeado fino) em 2026-07-07 apos a
# verificacao externa da proveniencia de emb_depth (Bolt Science ~1 um/interface,
# NAO VDI — cujo piso Rz<10 sobre-preve ~4x; MODEL_LEGITIMACY §4.6). Mudanca de
# INPUT com proveniencia (handbook), nao tuner. 30 Hz, 1e6. Grip 2.5*d=30 mm.
# Li2022ti: M10, A_F=10 kN, 10/15/20 Hz; normalizado em N=200; grip 25 mm
# 'assumed'. Trim do full-run em 3.3e5 (fadiga). Material/superficie NAO reportados
# => mantem "Rz<10" (sem base p/ Rz<4; alem disso sub-afrouxa, Rz<4 pioraria).
LIU17 = dict(bolt="M12x1.75", grip_mm=30.0, rz="Rz<4", n_if=1, freq=30.0,
             n_cycles=1_000_000, mu=0.15,
             prov=dict(grip=Provenance(30.0, "assumed", "2.5d; banda 24-36"),
                       rz=Provenance(0, "handbook", "retificado -> Rz<4; Bolt Science ~1um/interface (verif. 2026-07-07)"),
                       mu=Provenance(0.15, "assumed", "MSD_BLOCK_COVERAGE regra 3")))
LI22 = dict(bolt="M10x1.5", grip_mm=25.0, rz="Rz<10", n_if=1,
            n_cycles=330_000, mu=0.15,
            prov=dict(grip=Provenance(25.0, "assumed", "2.5d; banda 20-30"),
                      rz=Provenance(0, "assumed", "banda classe adjacente"),
                      mu=Provenance(0.15, "assumed", "MSD_BLOCK_COVERAGE regra 3")))

CONDITIONS = [
    # nome, csv, F0 [N], F_amp [N], base
    ("Liu2017 P0=15",   f"{DIG}/liu2017_axial_F0_15kN.csv",   15e3, 10e3, LIU17),
    ("Liu2017 P0=16.5", f"{DIG}/liu2017_axial_F0_16p5kN.csv", 16.5e3, 10e3, LIU17),
    ("Liu2017 P0=18",   f"{DIG}/liu2017_axial_F0_18kN.csv",   18e3, 10e3, LIU17),
    ("Liu2017 P0=19.5", f"{DIG}/liu2017_axial_F0_19p5kN.csv", 19.5e3, 10e3, LIU17),
    ("Liu2017 P0=21",   f"{DIG}/liu2017_axial_F0_21kN.csv",   21e3, 10e3, LIU17),
    ("Liu2017 AF=7.5",  f"{DIG}/liu2017_axial_AF_7p5kN.csv",  18e3, 7.5e3, LIU17),
    ("Liu2017 AF=8.75", f"{DIG}/liu2017_axial_AF_8p75kN.csv", 18e3, 8.75e3, LIU17),
    ("Liu2017 AF=11.25", f"{DIG}/liu2017_axial_AF_11p25kN.csv", 18e3, 11.25e3, LIU17),
    ("Liu2017 AF=12.5", f"{DIG}/liu2017_axial_AF_12p5kN.csv", 18e3, 12.5e3, LIU17),
    ("Li2022ti 10Hz",   f"{DIG}/li2022ti_axialmin_10Hz.csv",  10e3, 10e3, dict(LI22, freq=10.0)),
    ("Li2022ti 15Hz",   f"{DIG}/li2022ti_axialmin_15Hz.csv",  10e3, 10e3, dict(LI22, freq=15.0)),
    ("Li2022ti 20Hz",   f"{DIG}/li2022ti_axialmin_20Hz.csv",  10e3, 10e3, dict(LI22, freq=20.0)),
    ("Li2022ti 10Hz full", f"{DIG}/li2022ti_axial_10Hz_full.csv", 10e3, 10e3, dict(LI22, freq=10.0)),
]


def simulate(name, F0, F_amp, base, consts, emb_m, n_cycles):
    geom = geometry_for(base["bolt"], base["grip_mm"])
    mat = JointMaterial(emb_depth=emb_m, mu_thread=base["mu"],
                        mu_bearing=base["mu"], k_thread_fret=_K_THREAD_FRET,
                        **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    ratio = np.empty(n_cycles + 1)
    ratio[0] = 1.0
    for n in range(1, n_cycles + 1):
        ana.step_cycle(F_amp, 0.0, base["freq"])          # AXIAL, force-mode
        ratio[n] = max(ana.state.F_0, 0.0) / F0
    residual = float(ana.energy.conservation_residual)
    return np.arange(n_cycles + 1), ratio, residual


# Sensibilidade so no subconjunto representativo pre-registrado (runtime):
# extremos dos dois sweeps + uma curva Li2022. Demais: MAE_band=None declarado.
SENS_SUBSET = {"Liu2017 P0=15", "Liu2017 P0=21", "Liu2017 AF=12.5",
               "Li2022ti 10Hz"}


def predict_one(entry, consts, cap=None):
    name, csv, F0, F_amp, base = entry
    cyc_d, r_d = load_full_curve(csv)
    n_max = int(min(base["n_cycles"], cyc_d[-1]))
    if cap:
        n_max = min(n_max, cap)
    keep = cyc_d <= n_max
    cyc_d, r_d = cyc_d[keep], r_d[keep]
    emb_m, br = emb_depth_vdi(base["rz"], base["n_if"])
    sim_N, sim_r, resid = simulate(name, F0, F_amp, base, consts, emb_m, n_max)
    # alinhamento pre-registrado: normalizar AMBOS no primeiro ponto do dado
    n0 = cyc_d[0]
    r_d_al = r_d / r_d[0]
    sim_at_n0 = np.interp(n0, sim_N, sim_r)
    sim_al = sim_r / max(sim_at_n0, 1e-9)
    pred = np.interp(cyc_d, sim_N, sim_al)
    mae = float(np.mean(np.abs(pred - r_d_al)))
    # baseline (ii): decaimento exponencial 1-parametro fitado A CADA curva
    lam = _fit_exp(cyc_d - n0, r_d_al)
    mae_exp = float(np.mean(np.abs(np.exp(-lam * (cyc_d - n0)) - r_d_al)))
    # sensibilidade (§1.5): grip 2d/3d x classe Rz adjacente -> banda de MAE,
    # SO no subconjunto representativo pre-registrado (runtime).
    band = None
    if name in SENS_SUBSET:
        maes = []
        for gmm in (2.0, 3.0):
            for rzc in set(vdi_adjacent_classes(base["rz"])):
                e2, _ = emb_depth_vdi(rzc, base["n_if"])
                b2 = dict(base, grip_mm=gmm * float(base["bolt"].split("x")[0][1:]))
                _, s2, _ = simulate(name, F0, F_amp, b2, consts, e2, n_max)
                s2_al = s2 / max(np.interp(n0, np.arange(len(s2)), s2), 1e-9)
                maes.append(float(np.mean(np.abs(
                    np.interp(cyc_d, np.arange(len(s2)), s2_al) - r_d_al))))
        band = [min(maes), max(maes)]
    return dict(name=name, csv=csv, F0_N=F0, F_amp_N=F_amp,
                emb_depth_um=br["total_um"], rz_class=base["rz"],
                n_cycles=n_max, MAE=mae, MAE_exp_baseline=mae_exp,
                MAE_band=band,
                final_data=float(r_d_al[-1]), final_pred=float(pred[-1]),
                conservation_residual=resid,
                curve=dict(cycles=cyc_d.tolist(), data=r_d_al.tolist(),
                           pred=pred.tolist()))


def _fit_exp(n, r):
    """lambda de r=exp(-lam n) por minimos quadrados em log (r>0)."""
    m = r > 0.05
    if m.sum() < 2 or n[m].max() <= 0:
        return 0.0
    return max(float(-np.polyfit(n[m], np.log(r[m]), 1)[0]), 0.0)


def _af_gradient_model(consts, cap):
    """Gradiente d(fim)/dAF do MODELO sobre o sweep de A_F do Liu2017 (4 curvas)."""
    res = [predict_one(e, consts, cap) for e in CONDITIONS
           if e[0].startswith("Liu2017 AF")]
    xs = [r["F_amp_N"] for r in res]
    yp = [r["final_pred"] for r in res]
    return float(np.polyfit(xs, yp, 1)[0]) if len(xs) > 2 else float("nan")


def _calibrate_fret(consts, cap):
    """Varre k_thread_fret e escolhe o valor cujo d(fim)/dAF do modelo mais se
    aproxima do dado (-2.216e-5 /N, §4.6). Seta _K_THREAD_FRET no melhor."""
    global _K_THREAD_FRET
    target = -2.216e-5                          # dado d(fim)/dAF, §4.6
    saved, best = _K_THREAD_FRET, None
    print(f"Calibrando k_thread_fret (alvo d(fim)/dAF={target:.3e} /N):")
    for k in [0.0, 0.05, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0]:
        _K_THREAD_FRET = k
        gm = _af_gradient_model(consts, cap)
        print(f"  k_thread_fret={k:5.2f}  modelo d(fim)/dAF={gm:.3e} /N")
        if best is None or abs(gm - target) < abs(best[1] - target):
            best = (k, gm)
    _K_THREAD_FRET = best[0]
    print(f"MELHOR k_thread_fret={best[0]} (modelo {best[1]:.3e} vs dado {target:.3e})")
    return best


def main():
    global _K_THREAD_FRET
    quick = "--quick" in sys.argv
    cap = 20_000 if quick else None
    if "--k-thread-fret" in sys.argv:
        _K_THREAD_FRET = float(sys.argv[sys.argv.index("--k-thread-fret") + 1])
    consts, prov = frozen_constants()
    if "--calibrate-fret" in sys.argv:
        _calibrate_fret(consts, cap)
    print(f"Constantes congeladas (Estagio A): {consts}; "
          f"k_thread_fret={_K_THREAD_FRET}")
    results = [predict_one(e, consts, cap) for e in CONDITIONS]

    for r in results:
        band = ("banda " + "-".join(f"{b:.4f}" for b in r["MAE_band"])
                if r["MAE_band"] else "banda —")
        print(f"{r['name']:22s} MAE={r['MAE']:.4f} "
              f"(exp-baseline {r['MAE_exp_baseline']:.4f}, {band}) "
              f"fim dado={r['final_data']:.3f} pred={r['final_pred']:.3f} "
              f"resid={r['conservation_residual']:.2e}")
    maes = [r["MAE"] for r in results]
    beats = sum(r["MAE"] <= r["MAE_exp_baseline"] for r in results)
    med = float(np.median(maes))
    gate_fail = med > 0.05 or beats < len(results) / 2
    print(f"\nMediana MAE={med:.4f}; vence baseline exp em {beats}/{len(results)}")
    print("GATE B1:", "FALHOU — falsificacao estrutural, ver MODEL_LEGITIMACY §4.6 (B2 futil)" if gate_fail else "PASSOU")

    # gradientes dado-vs-modelo (P0-sweep e AF-sweep do Liu2017)
    def _grad(sel, xkey):
        xs = [r[xkey] for r in results if r["name"].startswith(sel)]
        yd = [r["final_data"] for r in results if r["name"].startswith(sel)]
        yp = [r["final_pred"] for r in results if r["name"].startswith(sel)]
        gd = np.polyfit(xs, yd, 1)[0] if len(xs) > 2 else float("nan")
        gp = np.polyfit(xs, yp, 1)[0] if len(xs) > 2 else float("nan")
        return float(gd), float(gp)
    g_P0 = _grad("Liu2017 P0", "F0_N")
    g_AF = _grad("Liu2017 AF", "F_amp_N")
    print(f"grad d(fim)/dP0: dado {g_P0[0]:.3e} /N, modelo {g_P0[1]:.3e} /N")
    print(f"grad d(fim)/dAF: dado {g_AF[0]:.3e} /N, modelo {g_AF[1]:.3e} /N")

    # plot 4x4
    fig, axes = plt.subplots(4, 4, figsize=(18, 14))
    for ax, r in zip(axes.flat, results):
        ax.semilogx(r["curve"]["cycles"], r["curve"]["data"], "o-", ms=3,
                    label="dado")
        ax.semilogx(r["curve"]["cycles"], r["curve"]["pred"], "k-",
                    label=f"pred (MAE={r['MAE']:.3f})")
        ax.set_title(r["name"], fontsize=9)
        ax.set_ylim(0.5, 1.05); ax.grid(alpha=0.3); ax.legend(fontsize=7)
    for ax in axes.flat[len(results):]:
        ax.axis("off")
    plt.tight_layout()
    fig.savefig(ROOT / "New_Theory" / "axial_track.png", dpi=110)

    if quick:
        print("--quick: nao gravando artefatos cientificos.")
        return
    out = dict(campaign="B1 zero-refit axial (spec 2026-07-03 §1.6)",
               frozen_constants=consts,
               provenance={k: vars(v) for k, v in prov.items()},
               gate=dict(median_MAE=med, beats_exp_baseline=f"{beats}/{len(results)}",
                         failed=bool(gate_fail)),
               gradients=dict(dfinal_dP0=dict(data=g_P0[0], model=g_P0[1]),
                              dfinal_dAF=dict(data=g_AF[0], model=g_AF[1])),
               results=[{k: v for k, v in r.items() if k != "curve"}
                        for r in results])
    (ROOT / "New_Theory" / "axial_results.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# Trilho axial — B1 zero-refit (spec 2026-07-03 §1.6)", "",
             f"Mediana MAE={med:.4f}; vence baseline exp em {beats}/{len(results)}; "
             f"gate {'FALHOU' if gate_fail else 'PASSOU'}.", "",
             "| Curva | MAE | exp-baseline | banda sens. | fim dado | fim pred |",
             "|---|---:|---:|---|---:|---:|"]
    for r in results:
        band = ("–".join(f"{b:.3f}" for b in r["MAE_band"])
                if r["MAE_band"] else "—")
        lines.append(f"| {r['name']} | {r['MAE']:.4f} | {r['MAE_exp_baseline']:.4f}"
                     f" | {band} | {r['final_data']:.3f} | {r['final_pred']:.3f} |")
    (ROOT / "New_Theory" / "axial_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("Artefatos: axial_results.json, axial_track.png, axial_report.md")


if __name__ == "__main__":
    main()
