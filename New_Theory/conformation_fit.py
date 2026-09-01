"""Fase 2 — validacao do mecanismo de conformacao dependente de pressao
(spec 2026-07-04 §9). Testa se a fisica compartilhada COM conformacao ativa
fecha o sobretorque SEM perturbar as demais condicoes.

A/B direto (SharedCalibrator._fit_subset), n=2 fixo, W_conf_ref o unico novo
numero fitado. Artefatos proprios; o bloco `shared` canonico NUNCA e escrito.
Thresholds PRE-REGISTRADOS (spec §9) — nao ajustar para forcar veredicto.

Run:  python New_Theory/conformation_fit.py [--quick]
Runtime: ~2-6 h (duas passadas de fit x 4 condicoes x 2500 ciclos).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

OUT_JSON = ROOT / "New_Theory" / "conformation_fit.json"
OUT_PNG = ROOT / "New_Theory" / "conformation_fit.png"
OUT_MD = ROOT / "New_Theory" / "conformation_fit_report.md"

# Thresholds PRE-REGISTRADOS (spec §9) — congelados.
RESOLVE_MAE = 0.06
PERSIST_MAE = 0.10
OTHERS_HOLD = 0.01
OTHERS_DEGRADE = 0.02
_OTHERS = ("nova", "reusada", "reaperto")


def build_conformation_config(n_cycles: int = 2500):
    """Config compartilhada canonica + constantes de conformacao nos priors
    (n=2 e p_ref fixos; W_conf_ref e o unico novo fitavel). Import de
    calibrate_shared lazy (mantem o import do modulo leve para os testes)."""
    from calibrate_shared import build_shared_config
    cfg = build_shared_config(n_cycles=n_cycles)
    cfg.priors = dict(cfg.priors, W_conf_ref=1e5,
                      conform_pressure_exp=2.0, p_ref_conform=5.0e8)
    cfg.bounds = dict(cfg.bounds, W_conf_ref=(1e3, 1e8))
    return cfg


def build_conformation_config_fitn(n_cycles: int = 2500):
    """Como build_conformation_config, mas conform_pressure_exp TAMBEM fitavel
    (n livre em [0.5, 4.0]) — robustez do expoente de pressao (spec §11 #1)."""
    cfg = build_conformation_config(n_cycles=n_cycles)
    cfg.bounds = dict(cfg.bounds, conform_pressure_exp=(0.5, 4.0))
    return cfg


def build_conformation_config_effective(n_cycles: int = 2500):
    """Como build_conformation_config (n=2 fixo, W_conf_ref o unico fitavel),
    mas seleciona o driver auto-limitante 'effective' (spec §7): o incremento de
    W_conf e ponderado pelo gate de inicio-de-ciclo (plateau, nao equilibrio
    verdadeiro c*<1). Testa se a auto-atenuacao mantem a nova inerte SEM o n
    agudo que o strand 1 (fit-n) expos no driver raw."""
    cfg = build_conformation_config(n_cycles=n_cycles)
    cfg.conform_driver = "effective"
    return cfg


def build_conformation_config_effective_fitn(n_cycles: int = 2500):
    """Driver 'effective' com n TAMBEM fitavel — testa se a auto-atenuacao tira
    o n do teto (o rail 3.9999 que o strand 1 expos no driver raw)."""
    cfg = build_conformation_config_effective(n_cycles=n_cycles)
    cfg.bounds = dict(cfg.bounds, conform_pressure_exp=(0.5, 4.0))
    return cfg


def classify_conformation_verdict(base_maes, treat_maes,
                                  base_resid, treat_resid) -> dict:
    """Veredicto pre-registrado (spec §9). AS IS."""
    sob = float(treat_maes["sobretorque"])
    deltas = {c: float(treat_maes[c] - base_maes[c]) for c in _OTHERS}
    max_delta = max(deltas.values())
    resid_ok = abs(treat_resid) <= abs(base_resid) + 1.0
    if sob < RESOLVE_MAE and max_delta < OTHERS_HOLD and resid_ok:
        verdict = "RESOLVED"
    elif sob > PERSIST_MAE or max_delta > OTHERS_DEGRADE:
        verdict = "FALSIFIED"
    else:
        verdict = "PARTIAL"
    return dict(verdict=verdict, sobretorque_mae=sob,
                max_others_delta=max_delta, others_deltas=deltas,
                resid_ok=resid_ok)


def run_ab(n_cycles: int):
    """Baseline {C_creep} (conformacao off) vs treatment {C_creep, W_conf_ref}
    (conformacao ativa, n=2 fixo). Mesmo setup de F0 (bound 120 kN) nos dois."""
    from bolt_analysis_studio.calibration.shared_calibrator import SharedCalibrator
    from calibrate_shared import build_shared_config
    cal_b = SharedCalibrator(build_shared_config(n_cycles=n_cycles))
    cal_b._fit_subset(["C_creep"])
    base_maes = cal_b.mae_by_condition()
    cal_t = SharedCalibrator(build_conformation_config(n_cycles=n_cycles))
    cal_t._fit_subset(["C_creep", "W_conf_ref"])
    treat_maes = cal_t.mae_by_condition()
    return cal_b, base_maes, cal_t, treat_maes


def _sobretorque_residual(cal, n_cycles: int) -> float:
    """Residual de conservacao rodando o sobretorque com as constantes de
    `cal` (mesmo setup de _run_condition, mas expondo energy)."""
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer)
    cond = next(c for c in cal.cfg.conditions if c.name == "sobretorque")
    ana = DynamicStiffnessAnalyzer(
        cal.cfg.geom, cal._material(cond), cal._F0(cond),
        initial_damage=cond.D_init, initial_embedding_frac=cond.emb_consumed_frac)
    for _ in range(n_cycles):
        ana.step_cycle(cond.F_amp, cal.cfg.theta, cal.cfg.freq,
                       delta_amp=cond.delta_amp)
    return float(ana.energy.conservation_residual)


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    quick = "--quick" in sys.argv
    n_cycles = 300 if quick else 2500

    cal_b, base_maes, cal_t, treat_maes = run_ab(n_cycles)
    base_resid = _sobretorque_residual(cal_b, n_cycles)
    treat_resid = _sobretorque_residual(cal_t, n_cycles)
    verdict = classify_conformation_verdict(base_maes, treat_maes,
                                            base_resid, treat_resid)
    W_conf_ref_fit = float(cal_t.constants["W_conf_ref"])

    print("== conformacao A/B (n=2 fixo; W_conf_ref o unico novo fitado) ==")
    for c in ("nova", "reusada", "sobretorque", "reaperto"):
        print(f"  {c:12s} base {base_maes[c]:.4f} -> treat {treat_maes[c]:.4f}"
              f"  (d {treat_maes[c]-base_maes[c]:+.4f})")
    print(f"  W_conf_ref fitado = {W_conf_ref_fit:.4g}")
    print(f"  residual sobretorque: base {base_resid:.3e} -> treat {treat_resid:.3e}")
    print(f"  VEREDICTO (pre-registrado): {verdict['verdict']}")

    # plot: sobretorque data + baseline sim + treatment sim
    sob_b = next(c for c in cal_b.cfg.conditions if c.name == "sobretorque")
    nb, rb = cal_b._run_condition(sob_b)
    sob_t = next(c for c in cal_t.cfg.conditions if c.name == "sobretorque")
    nt, rt = cal_t._run_condition(sob_t)
    fig, ax = plt.subplots(figsize=(8, 5))
    for cv in sob_b.curves:
        ax.plot(cv["cycles"], cv["ratio"], "o", ms=4, color="#00B050",
                alpha=0.8, label=cv["name"])
    ax.plot(nb, rb, "r--", lw=2, label=f"baseline (MAE {base_maes['sobretorque']:.3f})")
    ax.plot(nt, rt, "k-", lw=2.5,
            label=f"conformacao (MAE {treat_maes['sobretorque']:.3f})")
    ax.set_title(f"sobretorque A/B — veredicto {verdict['verdict']}", fontsize=9)
    ax.set_xlabel("Ciclos N"); ax.set_ylabel(r"$F_0/F_{0,init}$")
    ax.set_xlim(0, n_cycles); ax.set_ylim(0, 1.05); ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()

    if quick:
        fig.savefig(OUT_PNG, dpi=110)
        print("--quick: smoke (NAO cientifico); png gerado, sem JSON/report.")
        return
    fig.savefig(OUT_PNG, dpi=120)

    out = dict(
        campaign="Fase 2 — validacao da conformacao (spec 2026-07-04 §9)",
        method="A/B direto _fit_subset; n=2 fixo; W_conf_ref unico novo fitado",
        thresholds=dict(RESOLVE_MAE=RESOLVE_MAE, PERSIST_MAE=PERSIST_MAE,
                        OTHERS_HOLD=OTHERS_HOLD, OTHERS_DEGRADE=OTHERS_DEGRADE),
        baseline=dict(mae_by_condition=base_maes,
                      C_creep=float(cal_b.constants["C_creep"]),
                      sobretorque_residual=base_resid),
        treatment=dict(mae_by_condition=treat_maes,
                       C_creep=float(cal_t.constants["C_creep"]),
                       W_conf_ref=W_conf_ref_fit,
                       conform_pressure_exp=2.0, p_ref_conform=5.0e8,
                       sobretorque_residual=treat_resid),
        verdict=verdict,
        canonical_shared_block="NAO escrito (experimento)")
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    lines = ["# Validacao da conformacao — A/B (Fase 2)", "",
             f"**Veredicto (pre-registrado): {verdict['verdict']}**", "",
             "| Condicao | baseline | conformacao | delta |", "|---|---:|---:|---:|"]
    lines += [f"| {c} | {base_maes[c]:.4f} | {treat_maes[c]:.4f} | "
              f"{treat_maes[c]-base_maes[c]:+.4f} |"
              for c in ("nova", "reusada", "sobretorque", "reaperto")]
    lines += ["", f"W_conf_ref fitado = {W_conf_ref_fit:.4g} (n=2 fixo). "
              f"Residual sobretorque {base_resid:.3e} -> {treat_resid:.3e}."]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Artefatos: {OUT_JSON.name}, {OUT_PNG.name}, {OUT_MD.name}")


def main_fitn():
    """Robustez do expoente n (spec §11 #1): trata conform_pressure_exp como
    LIVRE e compara com o resultado n=2 fixo (conformation_fit.json). Escreve
    conformation_fitn.{json,md}. Bloco shared canonico NUNCA escrito."""
    from bolt_analysis_studio.calibration.shared_calibrator import SharedCalibrator
    from calibrate_shared import build_shared_config

    quick = "--quick" in sys.argv
    n_cycles = 300 if quick else 2500

    cal_b = SharedCalibrator(build_shared_config(n_cycles=n_cycles))
    cal_b._fit_subset(["C_creep"])
    base_maes = cal_b.mae_by_condition()
    cal_t = SharedCalibrator(build_conformation_config_fitn(n_cycles=n_cycles))
    cal_t._fit_subset(["C_creep", "W_conf_ref", "conform_pressure_exp"])
    treat_maes = cal_t.mae_by_condition()
    base_resid = _sobretorque_residual(cal_b, n_cycles)
    treat_resid = _sobretorque_residual(cal_t, n_cycles)
    verdict = classify_conformation_verdict(base_maes, treat_maes,
                                            base_resid, treat_resid)
    n_fit = float(cal_t.constants["conform_pressure_exp"])
    W_fit = float(cal_t.constants["W_conf_ref"])

    print("== conformacao A/B com n LIVRE (robustez do expoente) ==")
    for c in ("nova", "reusada", "sobretorque", "reaperto"):
        print(f"  {c:12s} base {base_maes[c]:.4f} -> treat {treat_maes[c]:.4f}"
              f"  (d {treat_maes[c]-base_maes[c]:+.4f})")
    print(f"  n fitado = {n_fit:.3f} (vs 2.0 fixo)   W_conf_ref = {W_fit:.4g}")
    print(f"  VEREDICTO (mesmos thresholds §9): {verdict['verdict']}")

    if quick:
        print("--quick: smoke (NAO cientifico); sem JSON/report.")
        return
    out = dict(
        campaign="Fase 2 — robustez do expoente n (spec §11 #1)",
        method="A/B; treatment livre {C_creep, W_conf_ref, conform_pressure_exp}",
        baseline=dict(mae_by_condition=base_maes, sobretorque_residual=base_resid),
        treatment=dict(mae_by_condition=treat_maes, W_conf_ref=W_fit,
                       conform_pressure_exp_fitted=n_fit, p_ref_conform=5.0e8,
                       sobretorque_residual=treat_resid),
        reference_n2="conformation_fit.json (n=2 fixo: W_conf_ref 1.253e4, sob 0.0201, RESOLVED)",
        verdict=verdict, canonical_shared_block="NAO escrito (experimento)")
    (ROOT / "New_Theory" / "conformation_fitn.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Robustez do expoente n — A/B (Fase 2, spec §11 #1)", "",
             f"**Veredicto: {verdict['verdict']}**  |  n fitado = {n_fit:.3f} "
             f"(vs 2.0 fixo), W_conf_ref = {W_fit:.4g}", "",
             "| Condicao | baseline | conformacao (n livre) | delta |",
             "|---|---:|---:|---:|"]
    lines += [f"| {c} | {base_maes[c]:.4f} | {treat_maes[c]:.4f} | "
              f"{treat_maes[c]-base_maes[c]:+.4f} |"
              for c in ("nova", "reusada", "sobretorque", "reaperto")]
    (ROOT / "New_Theory" / "conformation_fitn_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("Artefatos: conformation_fitn.json, conformation_fitn_report.md")


def main_effective():
    """Strand 2 (spec §7): driver auto-limitante 'effective' vs OFF (veredicto
    pre-registrado §9) + fit-n no effective (o n sai do teto que o raw railou?).
    Referencias raw: conformation_fit.json (n=2, RESOLVED) e conformation_fitn.json
    (n=3.9999 railed). Escreve conformation_effective.{json,md}. Bloco shared
    canonico NUNCA escrito."""
    from bolt_analysis_studio.calibration.shared_calibrator import SharedCalibrator
    from calibrate_shared import build_shared_config

    quick = "--quick" in sys.argv
    n_cycles = 300 if quick else 2500

    # baseline: conformacao OFF
    cal_b = SharedCalibrator(build_shared_config(n_cycles=n_cycles))
    cal_b._fit_subset(["C_creep"])
    base_maes = cal_b.mae_by_condition()
    base_resid = _sobretorque_residual(cal_b, n_cycles)

    # tratamento: driver effective (n=2 fixo)
    cal_e = SharedCalibrator(build_conformation_config_effective(n_cycles=n_cycles))
    cal_e._fit_subset(["C_creep", "W_conf_ref"])
    eff_maes = cal_e.mae_by_condition()
    eff_resid = _sobretorque_residual(cal_e, n_cycles)
    verdict = classify_conformation_verdict(base_maes, eff_maes, base_resid, eff_resid)
    W_eff = float(cal_e.constants["W_conf_ref"])

    # fit-n no effective: o n sai do teto (4.0) que o raw railou?
    cal_ef = SharedCalibrator(build_conformation_config_effective_fitn(n_cycles=n_cycles))
    cal_ef._fit_subset(["C_creep", "W_conf_ref", "conform_pressure_exp"])
    effn_maes = cal_ef.mae_by_condition()
    n_eff = float(cal_ef.constants["conform_pressure_exp"])
    W_effn = float(cal_ef.constants["W_conf_ref"])

    print("== conformacao driver EFFECTIVE (auto-limitante) vs OFF ==")
    for c in ("nova", "reusada", "sobretorque", "reaperto"):
        print(f"  {c:12s} off {base_maes[c]:.4f} -> eff {eff_maes[c]:.4f}"
              f"  (d {eff_maes[c]-base_maes[c]:+.4f})")
    print(f"  W_conf_ref (effective, n=2) = {W_eff:.4g}")
    print(f"  residual sobretorque: off {base_resid:.3e} -> eff {eff_resid:.3e}")
    print(f"  VEREDICTO (effective vs off, §9): {verdict['verdict']}")
    print(f"  fit-n no effective: n = {n_eff:.3f} (raw railou em 3.9999)  W = {W_effn:.4g}")
    print(f"    sobretorque(fit-n eff) = {effn_maes['sobretorque']:.4f}")

    if quick:
        print("--quick: smoke (NAO cientifico); sem JSON/report.")
        return
    out = dict(
        campaign="Fase 2 strand 2 — driver de conformacao auto-limitante (spec §7)",
        method="A/B effective-vs-OFF (n=2 fixo) + fit-n no effective; mesmo classificador §9",
        thresholds=dict(RESOLVE_MAE=RESOLVE_MAE, PERSIST_MAE=PERSIST_MAE,
                        OTHERS_HOLD=OTHERS_HOLD, OTHERS_DEGRADE=OTHERS_DEGRADE),
        baseline=dict(mae_by_condition=base_maes,
                      C_creep=float(cal_b.constants["C_creep"]),
                      sobretorque_residual=base_resid),
        treatment=dict(driver="effective", mae_by_condition=eff_maes,
                       C_creep=float(cal_e.constants["C_creep"]),
                       W_conf_ref=W_eff, conform_pressure_exp=2.0,
                       p_ref_conform=5.0e8, sobretorque_residual=eff_resid),
        fitn_effective=dict(mae_by_condition=effn_maes,
                            conform_pressure_exp_fitted=n_eff, W_conf_ref=W_effn),
        reference_raw_n2="conformation_fit.json (raw n=2: W_conf_ref 1.253e4, sob 0.0201, RESOLVED)",
        reference_raw_fitn="conformation_fitn.json (raw fit-n: n=3.9999 railed, PARTIAL)",
        verdict=verdict, canonical_shared_block="NAO escrito (experimento)")
    (ROOT / "New_Theory" / "conformation_effective.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Driver de conformacao auto-limitante — strand 2 (spec §7)", "",
             f"**Veredicto (effective vs off, §9): {verdict['verdict']}**  |  "
             f"W_conf_ref(eff,n=2) = {W_eff:.4g}", "",
             "| Condicao | off | effective (n=2) | delta |", "|---|---:|---:|---:|"]
    lines += [f"| {c} | {base_maes[c]:.4f} | {eff_maes[c]:.4f} | "
              f"{eff_maes[c]-base_maes[c]:+.4f} |"
              for c in ("nova", "reusada", "sobretorque", "reaperto")]
    lines += ["", f"Residual sobretorque {base_resid:.3e} -> {eff_resid:.3e}.", "",
              f"**fit-n no effective:** n = {n_eff:.3f} (raw railou em 3.9999), "
              f"W_conf_ref = {W_effn:.4g}, sobretorque = {effn_maes['sobretorque']:.4f}.",
              "", "Referencias raw: conformation_fit.json (n=2 RESOLVED), "
              "conformation_fitn.json (fit-n railed)."]
    (ROOT / "New_Theory" / "conformation_effective_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("Artefatos: conformation_effective.json, conformation_effective_report.md")


if __name__ == "__main__":
    if "--effective" in sys.argv:
        main_effective()
    elif "--fit-n" in sys.argv:
        main_fitn()
    else:
        main()
