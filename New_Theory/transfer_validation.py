"""Sub-campanha A — transferencia ZERO-REFIT transversal (spec 2026-07-03 §1).

Constantes do Estagio A congeladas; inputs nomeados com proveniencia; selecao
por REGRA pre-registrada (fontes + exclusoes por substring de CSV, todas
registradas com motivo). Dano OFF (casos = juntas novas; fidelidade ao Estagio
A, onde dano so ativa em juntas pre-danificadas) — colapsos devem sub-predizer
e isso e um ACHADO sobre crescimento de dano em junta virgem, nao um bug.

Run:  python New_Theory/transfer_validation.py
Runtime: ~2-5 min (46 curvas + sensibilidade em 8).
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
from bolt_analysis_studio.core.validation_cases import DIGITIZED_CASES  # noqa: E402
from library_common import (  # noqa: E402
    emb_depth_vdi, frozen_constants, geometry_for, load_full_curve,
    vdi_adjacent_classes,
)

ALLOWED_SOURCES = {"LIU_2025", "BAUER_2024", "LU_2024", "ICMEZ_2025",
                   "YANG_2019", "ROUSSEAU_2025", "KARLSEN_2022"}
EXCLUDE_TOKENS = {
    "hdpe": "par polimerico (HDPE) — fora do dominio declarado do modelo",
    "vibralock": "dispositivo de travamento — out-of-model declarado",
    "varamp": "protocolo de amplitude variavel — fora do harness de delta constante",
    "fig2_single": "ensaio ate fratura — fora do escopo de afrouxamento puro",
}
FLOOR_TRIM = 0.10          # pre-registrado: descarta pontos com ratio < 0.10
_DAMAGE_ON = False         # toggled por --damage-on (experimento: dano ativo em TODOS os casos)
_DAMAGE_TRIGGER = False     # toggled por --damage-trigger (dano AUTO-disparado por W_crit, spec 2026-07-05)
_KTR_BENDING = False        # toggled por --ktr-bending (k_tr = flexao do parafuso, spec 2026-07-05; c_bend calibrado)
_LOOSEN_COUPLED = False     # toggled por --loosen-coupled (loosening gateado pelo regime de slip, spec 2026-07-06; implica bending)
_SLIP_REGIME = False        # toggled por --slip-regime (EXPERIMENTO 2026-07-08: pack Rousseau §4.12
                            # CM+bending+bolt_torsion+arrest com constantes DO ROUSSEAU (c_bend=0.3,
                            # eta=15, floor=0.08) cross-library — testa se as constantes per-rig
                            # transferem; §8 preve que NAO, o interesse e' medir o quanto)
TRIGGER_W_CRIT = 1.0e5     # J — dose critica default do onset (--wcrit sobrepoe)
F_AMP_RATIO = 0.4          # LITERATURA (2026-07-08, item 4 fechado sem ensaio):
                           # Pai&Hess 2002 MEDIRAM F_tr/F0 = 0.378-0.489 (media
                           # ~0.43, celula no fixture; nota 23 Dataset 3, cresce
                           # com F0 - limite conservador >=0.35). Rousseau 2025
                           # loop medido: aco ~0.40; HDPE ~0.24 (o F_eff stack-
                           # limited do sec4.20 preve 0.25 - confirmacao
                           # independente). 0.4 = centro da faixa medida.
RZ_DEFAULT = "Rz10-40"     # superficies usinadas estruturais (assumed)
SENS_STEMS = {"liu2025_M16_amp0p25", "liu2025_M16_amp0p8",
              "lu2024_M8_fig18_amp0p25", "lu2024_M8_fig18_amp2p0",
              "bauer2024_M12_fig8_test1", "demir2024_amp0p4_F17p6_lk13p8",
              "karlsen2022_M42_HV_run20p0", "rousseau2025_steel_t10"}

# Inputs por fonte (MSD_BLOCK_COVERAGE + notas de aparato). grip 'assumed'
# segue a regra 2.5d; mu de Lu2024 derivado do coef. de torque K=0.23-0.27
# (Motosh) na nota — ~0.18.
SOURCE_INPUTS = {
    "LIU_2025":      dict(grip=None, mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "BAUER_2024":    dict(grip=("bolt", "paper"), mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "LU_2024":       dict(grip=None, mu=(0.18, "paper"), rz=RZ_DEFAULT),
    "ICMEZ_2025":    dict(grip=("csv", "paper"), mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "YANG_2019":     dict(grip=None, mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "ROUSSEAU_2025": dict(grip=("csv", "paper"), mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "KARLSEN_2022":  dict(grip=None, mu=(0.15, "assumed"), rz=RZ_DEFAULT),
}
ROUSSEAU_GRIPS = {"t10": 25.0, "t12": 29.0, "t14": 33.0}
ICMEZ_GRIPS = {"lk13p8": 13.8, "lk19p8": 19.8}
BAUER_GRIPS = {"M8": 8.0, "M12": 12.0}


def select_cases():
    selected, excluded = [], []
    for c in DIGITIZED_CASES:
        if c.source.name not in ALLOWED_SOURCES:
            continue
        if c.transverse_displacement_mm <= 0:
            continue
        csv = Path(c.reference_csv_path).name
        hit = next((t for t in EXCLUDE_TOKENS if t in csv), None)
        if hit:
            excluded.append(dict(csv=csv, reason=EXCLUDE_TOKENS[hit]))
        else:
            selected.append(c)
    return selected, excluded


def _d_mm(case):
    return float(case.bolt_size.split("x")[0][1:])


def inputs_for(case):
    src = SOURCE_INPUTS[case.source.name]
    stem = Path(case.reference_csv_path).stem
    # grip
    if src["grip"] is None:
        grip = dict(value=2.5 * _d_mm(case), prov="assumed")
    elif src["grip"][0] == "bolt":
        key = "M8" if case.bolt_size.startswith("M8") else "M12"
        grip = dict(value=BAUER_GRIPS[key], prov="paper")
    else:  # "csv"
        table = ROUSSEAU_GRIPS if "rousseau" in stem else ICMEZ_GRIPS
        key = next(k for k in table if k in stem)
        grip = dict(value=table[key], prov="paper")
    mu = dict(value=src["mu"][0], prov=src["mu"][1])
    rz = dict(value=src["rz"], prov="assumed")
    F_amp = dict(value=F_AMP_RATIO * case.initial_preload_N,
                 prov="literature (Pai&Hess 2002: 0.38-0.49 medido)")
    return dict(grip_mm=grip, mu=mu, rz=rz, F_amp_N=F_amp)


def _simulate(case, grip_mm, mu, rz_class, F_amp_N, n_cycles):
    consts, _ = frozen_constants(include_damage=(_DAMAGE_ON or _DAMAGE_TRIGGER))
    emb_m, _ = emb_depth_vdi(rz_class, n_inner_interfaces=1)
    geom = geometry_for(case.bolt_size, grip_mm=grip_mm)
    # Re-run 2026-07-05 com a FISICA ADOTADA: conform_driver="effective" e o
    # driver adotado no bloco canonico (§4.9); frozen_constants traz
    # W_conf_ref/n/p_ref numericos mas nao a string do driver, entao setamos
    # aqui. Com A_contact per-rig (11g) a pressao p=F0/A_contact e fisica
    # cross-rig, entao wear (depth=V/A) E conformacao ficam fisicos.
    kw = dict(emb_depth=emb_m, mu_thread=mu, mu_bearing=mu,
              conform_driver="effective")
    if _DAMAGE_ON or _DAMAGE_TRIGGER:
        # c_D=2/k_dmg_wear=4 vem de consts (include_damage=True); k_dmg_mu=1.0
        # = fisica de dano do Estagio A (default do SharedCalibrationConfig).
        kw["k_dmg_mu"] = 1.0
    if _DAMAGE_TRIGGER:
        # --damage-trigger: dano AUTO-disparado — W_crit>0 gateia a D-growth
        # (predictive trigger, spec 2026-07-05). Sem damage_active manual: a
        # fisica (dose de gross-slip acumulada > W_crit) decide onde o dano liga.
        kw["W_crit"] = TRIGGER_W_CRIT
    if _KTR_BENDING:
        # --ktr-bending: k_tr = rigidez de FLEXAO do parafuso (c_bend*E*I/L^3),
        # nao 0.3*k_axial. Da o regime partial/gross slip real (spec 2026-07-05).
        # c_bend usa o default calibrado (1.0, acc balanceada 67% nos sweeps).
        kw["k_tr_mode"] = "bending"
    if _LOOSEN_COUPLED:
        # --loosen-coupled: gate do loosening pela fracao de gross-slip (spec
        # 2026-07-06). So faz sentido com delta_t realista, entao forca bending tb.
        kw["k_tr_mode"] = "bending"
        kw["loosening_slip_coupling"] = "gross_fraction"
    if _SLIP_REGIME:
        # --slip-regime: pack validado no Rousseau (§4.12) com as constantes
        # PER-RIG do Rousseau aplicadas cross-library (experimento de
        # transferencia de constantes; a FORMA e' a mesma).
        kw.update(slip_regime_mode="cattaneo_mindlin", slip_regime_sharpness=1.0,
                  k_tr_mode="bending", c_bend=0.30,
                  loose_torsion_mode="bolt_torsion", eta_loose=15.0,
                  loose_arrest_floor=0.08)
    mat = JointMaterial(**kw, **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, case.initial_preload_N)
    delta = case.transverse_displacement_mm * 1e-3
    ratio = np.empty(n_cycles + 1)
    ratio[0] = 1.0
    for n in range(1, n_cycles + 1):
        ana.step_cycle(F_amp_N, np.pi / 2, case.frequency_Hz, delta_amp=delta)
        ratio[n] = max(ana.state.F_0, 0.0) / case.initial_preload_N
    return ratio, float(ana.state.D)


def _fit_exp(n, r):
    m = r > 0.05
    if m.sum() < 2 or n[m].max() <= 0:
        return 0.0
    return max(float(-np.polyfit(n[m], np.log(r[m]), 1)[0]), 0.0)


def _mae_curve(case, inp, cyc_d, r_d_al, n0, grip=None, mu=None, rz=None,
               F_amp=None):
    n_max = int(cyc_d[-1])
    sim, final_D = _simulate(case, grip or inp["grip_mm"]["value"],
                             mu or inp["mu"]["value"], rz or inp["rz"]["value"],
                             F_amp or inp["F_amp_N"]["value"], n_max)
    sim_al = sim / max(np.interp(n0, np.arange(n_max + 1), sim), 1e-9)
    pred = np.interp(cyc_d, np.arange(n_max + 1), sim_al)
    return float(np.mean(np.abs(pred - r_d_al))), pred, final_D


def predict_case(case, do_sensitivity):
    cyc, ratio = load_full_curve(case.reference_csv_path)
    keep = ratio >= FLOOR_TRIM
    n_trimmed = int((~keep).sum())
    cyc_d, r_d = cyc[keep], ratio[keep]
    n0 = cyc_d[0]
    r_d_al = r_d / r_d[0]
    inp = inputs_for(case)
    mae, pred, final_D = _mae_curve(case, inp, cyc_d, r_d_al, n0)
    mae_noloss = float(np.mean(np.abs(1.0 - r_d_al)))
    lam = _fit_exp(cyc_d - n0, r_d_al)
    mae_exp = float(np.mean(np.abs(np.exp(-lam * (cyc_d - n0)) - r_d_al)))
    band = None
    if do_sensitivity:
        maes = [mae]
        v = inp["mu"]["value"]
        for mu2 in (0.75 * v, 1.25 * v):
            maes.append(_mae_curve(case, inp, cyc_d, r_d_al, n0, mu=mu2)[0])
        for rz2 in set(vdi_adjacent_classes(inp["rz"]["value"])):
            maes.append(_mae_curve(case, inp, cyc_d, r_d_al, n0, rz=rz2)[0])
        F0 = case.initial_preload_N
        for fr in (0.2, 0.6):
            maes.append(_mae_curve(case, inp, cyc_d, r_d_al, n0,
                                   F_amp=fr * F0)[0])
        if inp["grip_mm"]["prov"] == "assumed":
            d = _d_mm(case)
            for g in (2.0 * d, 3.0 * d):
                maes.append(_mae_curve(case, inp, cyc_d, r_d_al, n0, grip=g)[0])
        band = [min(maes), max(maes)]
    return dict(name=case.name, csv=Path(case.reference_csv_path).name,
                source=case.source.name, F0_N=case.initial_preload_N,
                delta_amp_mm=case.transverse_displacement_mm,
                freq_Hz=case.frequency_Hz,
                inputs={k: dict(value=(v["value"] if not isinstance(
                    v["value"], str) else v["value"]), prov=v["prov"])
                    for k, v in inp.items()},
                n_cycles=int(cyc_d[-1]), n_trimmed=n_trimmed,
                MAE=mae, MAE_noloss=mae_noloss, MAE_exp=mae_exp,
                final_data=float(r_d_al[-1]), final_pred=float(pred[-1]),
                final_D=final_D,          # dano final (regime accuracy do trigger)
                band=band,
                curve=dict(cycles=cyc_d.tolist(), data=r_d_al.tolist(),
                           pred=pred.tolist()))


def main():
    global _DAMAGE_ON, _DAMAGE_TRIGGER, _KTR_BENDING, _LOOSEN_COUPLED, TRIGGER_W_CRIT
    global _SLIP_REGIME
    _DAMAGE_ON = "--damage-on" in sys.argv
    _DAMAGE_TRIGGER = "--damage-trigger" in sys.argv
    _KTR_BENDING = "--ktr-bending" in sys.argv
    _LOOSEN_COUPLED = "--loosen-coupled" in sys.argv
    _SLIP_REGIME = "--slip-regime" in sys.argv
    if "--wcrit" in sys.argv:
        TRIGGER_W_CRIT = float(sys.argv[sys.argv.index("--wcrit") + 1])
    suffix = ("_trigger" if _DAMAGE_TRIGGER
              else ("_damage" if _DAMAGE_ON else ""))
    if _KTR_BENDING:                    # composavel: --damage-trigger --ktr-bending => _trigger_ktr
        suffix += "_ktr"
    if _LOOSEN_COUPLED:                 # composavel: => _loosen (implica bending)
        suffix += "_loosen"
    if _SLIP_REGIME:                    # experimento: pack Rousseau cross-library
        suffix += "_slipregime"
    if _DAMAGE_TRIGGER:
        mode = f"TRIGGER (dano auto-disparado, W_crit={TRIGGER_W_CRIT:.4g} J)"
    elif _DAMAGE_ON:
        mode = "ON (c_D=2, k_dmg_wear=4, k_dmg_mu=1; what-if, viola juntas-novas)"
    else:
        mode = "OFF"
    selected, excluded = select_cases()
    consts, prov = frozen_constants(include_damage=(_DAMAGE_ON or _DAMAGE_TRIGGER))
    ktr = ("bending (c_bend=0.3, pack slip-regime)" if _SLIP_REGIME
           else "bending (c_bend calibrado 1.0)" if (_KTR_BENDING or _LOOSEN_COUPLED)
           else "axial_frac (0.3*k_axial, atual)")
    loosen = "gross_fraction (gate por regime de slip)" if _LOOSEN_COUPLED else "off (criterio de forca)"
    print(f"{len(selected)} curvas selecionadas, {len(excluded)} excluidas "
          f"(com motivo). DANO {mode}. k_tr {ktr}. loosening {loosen}. "
          f"Constantes congeladas: {consts}")
    results = []
    for case in selected:
        stem = Path(case.reference_csv_path).stem
        r = predict_case(case, do_sensitivity=stem in SENS_STEMS)
        results.append(r)
        print(f"{r['csv']:45s} MAE={r['MAE']:.4f} exp={r['MAE_exp']:.4f} "
              f"noloss={r['MAE_noloss']:.4f}")

    # agregados por fonte + global
    def _agg(rs):
        maes = [r["MAE"] for r in rs]
        return dict(n=len(rs), median_MAE=float(np.median(maes)),
                    p90_MAE=float(np.percentile(maes, 90)),
                    beats_exp=int(sum(r["MAE"] <= r["MAE_exp"] for r in rs)),
                    beats_noloss=int(sum(r["MAE"] <= r["MAE_noloss"]
                                         for r in rs)))
    per_source = {}
    for r in results:
        per_source.setdefault(r["source"], []).append(r)
    aggregates = {s: _agg(rs) for s, rs in sorted(per_source.items())}
    aggregates["GLOBAL"] = _agg(results)
    for s, a in aggregates.items():
        print(f"{s:15s} n={a['n']:2d} medianMAE={a['median_MAE']:.4f} "
              f"p90={a['p90_MAE']:.4f} vs_exp={a['beats_exp']}/{a['n']} "
              f"vs_noloss={a['beats_noloss']}/{a['n']}")

    # grid unico
    ncols = 7
    nrows = int(np.ceil(len(results) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 3 * nrows))
    for ax, r in zip(np.atleast_1d(axes).flat, results):
        ax.plot(r["curve"]["cycles"], r["curve"]["data"], "o-", ms=2)
        ax.plot(r["curve"]["cycles"], r["curve"]["pred"], "k-")
        ax.set_title(f"{r['csv'][:34]}\nMAE={r['MAE']:.3f}", fontsize=7)
        ax.set_ylim(0, 1.05)
        ax.grid(alpha=0.3)
    for ax in np.atleast_1d(axes).flat[len(results):]:
        ax.axis("off")
    plt.tight_layout()
    fig.savefig(ROOT / "New_Theory" / f"transfer_grid{suffix}.png", dpi=90)

    out = dict(
        campaign="A zero-refit transversal (spec 2026-07-03 §1)",
        frozen_constants=consts,
        choices=dict(F_amp_ratio=F_AMP_RATIO, floor_trim=FLOOR_TRIM,
                     rz_default=RZ_DEFAULT,
                     damage=(f"TRIGGER (predictive, spec 2026-07-05: c_D=2/"
                             f"k_dmg_wear=4/k_dmg_mu=1 + W_crit={TRIGGER_W_CRIT:.4g} J "
                             f"gateando a D-growth; dano AUTO-disparado pela dose "
                             f"de gross-slip, sem damage_active manual)"
                             if _DAMAGE_TRIGGER else
                             "ON (experimento --damage-on: c_D=2/k_dmg_wear=4/"
                             "k_dmg_mu=1; D cresce de 0; VIOLA a doutrina "
                             "juntas-novas — what-if AS IS)" if _DAMAGE_ON else
                             "OFF — juntas novas; no Estagio A o dano so ativa "
                             "em juntas pre-danificadas; colapsos devem "
                             "sub-predizer (achado, nao bug)"),
                     trigger_W_crit=(TRIGGER_W_CRIT if _DAMAGE_TRIGGER else None),
                     ktr_mode=("bending (c_bend calibrado 1.0, spec 2026-07-05: "
                               "k_tr = flexao do parafuso; regime partial/gross slip)"
                               if (_KTR_BENDING or _LOOSEN_COUPLED) else
                               "axial_frac (0.3*k_axial ~1.2e9, delta_t~0 => tudo gross)"),
                     loosening=("gross_fraction (gate do loosening pela fracao de "
                                "gross-slip; implica bending; spec 2026-07-06)"
                                if _LOOSEN_COUPLED else "off (criterio de forca atual)"),
                     alignment="normalizacao no 1o ponto do dado"),
        exclusions=excluded,
        aggregates=aggregates,
        results=[{k: v for k, v in r.items() if k != "curve"}
                 for r in results])
    (ROOT / "New_Theory" / f"transfer_results{suffix}.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    g = aggregates["GLOBAL"]
    lines = ["# Transferencia zero-refit transversal (spec 2026-07-03 §1)", "",
             f"{len(results)} curvas, {len(excluded)} exclusoes registradas. "
             f"GLOBAL: mediana MAE {g['median_MAE']:.4f}, p90 {g['p90_MAE']:.4f}, "
             f"vence exp {g['beats_exp']}/{g['n']}, vence no-loss "
             f"{g['beats_noloss']}/{g['n']}.", "",
             "| Fonte | n | mediana | p90 | vs exp | vs no-loss |",
             "|---|--:|--:|--:|--:|--:|"]
    for s, a in aggregates.items():
        lines.append(f"| {s} | {a['n']} | {a['median_MAE']:.4f} | "
                     f"{a['p90_MAE']:.4f} | {a['beats_exp']}/{a['n']} | "
                     f"{a['beats_noloss']}/{a['n']} |")
    (ROOT / "New_Theory" / f"transfer_report{suffix}.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print(f"Artefatos: transfer_results{suffix}.json, transfer_grid{suffix}.png, "
          f"transfer_report{suffix}.md")


if __name__ == "__main__":
    main()
