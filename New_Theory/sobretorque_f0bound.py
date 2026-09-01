"""Fase 2 — discriminacao do sobretorque (MODEL_LEGITIMACY §4.5).

O Estagio A nao fecha o sobretorque: F0_test cravou no bound de 120 kN, MAE
0.1378 (18.9x o fit local de 1 parametro). Duas hipoteses:
  (A) bound apertado demais — a pre-carga real do ensaio (over-torque) era
      > 120 kN; com o teto elevado ao limite de sanidade (0.9*Rp0.2*A_s ~
      132.8 kN) o fit compartilhado alcanca o sobretorque.
  (B) mecanismo faltante — over-torque introduz um regime dependente da
      pressao de contato (atrito/wear/assentamento) ausente na fisica atual;
      elevar o teto NAO resgata o sobretorque.

Este experimento re-roda o Estagio A com o UNICO input mudado (teto do
estimate_F0 do sobretorque), le o baseline COMMITADO e classifica o resultado
com thresholds PRE-REGISTRADOS. Artefatos proprios; o bloco `shared` canonico
NUNCA e escrito (mesma disciplina de creep_anchor.json).

CUIDADO (spec Fase 1 §4): a hipotese GW k_tr(F0) para pressao-de-contato tem
sinal DESFAVORAVEL no slip atual (k_tr^ => slip^). Um veredicto de "mecanismo
faltante" NAO deve ser lido como aval para ressuscitar GW k_tr(F0) ingenuo.

Run:  python New_Theory/sobretorque_f0bound.py [--quick]
  --quick: n_cycles=300 (smoke; NAO gravar como resultado cientifico)
Runtime do run completo: ~15-40 min (fit_parsimonious x 4 condicoes + LOCO
nao e re-rodado aqui).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

SHARED_JSON = ROOT / "New_Theory" / "joint_calibrations.json"
OUT_JSON = ROOT / "New_Theory" / "sobretorque_f0bound.json"
OUT_PNG = ROOT / "New_Theory" / "sobretorque_f0bound.png"
OUT_MD = ROOT / "New_Theory" / "sobretorque_f0bound_report.md"

# Teto de sanidade F0 = 0.9 * Rp0.2(classe 10.9 = 940 MPa) * A_s(M16 = 157mm2)
# = 132.8 kN. Mesma formula de calibrate_shared.F0_SANITY_N (teste pina).
F0_SANITY_N = 0.9 * 940e6 * 157e-6

# Thresholds PRE-REGISTRADOS do veredicto (nao mexer para forcar resultado):
#   RESCUE_MAE  = entra na banda fittavel (demais condicoes fitam 0.046-0.075).
#   PERSIST_MAE = continua longe (> ~70% do baseline 0.138).
RESCUE_MAE = 0.06
PERSIST_MAE = 0.10


def read_baseline(json_path=SHARED_JSON) -> dict:
    """Baseline do sobretorque do bloco `shared` COMMITADO (bound 120 kN)."""
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    sob = data["shared"]["conditions"]["sobretorque"]
    return dict(mae=float(sob["MAE"]),
                f0_N=float(sob["states"]["F0_test_N"]),
                mae_global=float(data["shared"]["mae_global"]))


def classify_verdict(mae_base: float, mae_new: float, f0_new: float,
                     ceiling: float) -> dict:
    """Classificacao pre-registrada. AS IS — nenhum threshold e ajustado."""
    pinned = f0_new >= 0.999 * ceiling
    if mae_new <= RESCUE_MAE:
        verdict = "bound-too-tight (rescued)"
    elif mae_new >= PERSIST_MAE:
        verdict = "missing mechanism (falsified again)"
    else:
        verdict = "partial / inconclusive"
    return dict(verdict=verdict, pinned_at_new_ceiling=pinned,
                delta_mae=mae_base - mae_new,
                mae_base=mae_base, mae_new=mae_new, f0_new_N=f0_new)


def run_raised_fit(n_cycles: int):
    """Re-roda o Estagio A com o UNICO input mudado: teto do estimate_F0 do
    sobretorque 120 kN -> F0_SANITY_N (~132.8 kN). Import de calibrate_shared
    e lazy (mantem o import do modulo leve para os testes dos helpers)."""
    from calibrate_shared import build_shared_config
    from bolt_analysis_studio.calibration.shared_calibrator import SharedCalibrator
    cfg = build_shared_config(n_cycles=n_cycles)
    cfg.estimate_F0 = dict(cfg.estimate_F0,
                           sobretorque=(40_000.0, F0_SANITY_N))
    cal = SharedCalibrator(cfg)
    res = cal.fit_parsimonious(tol=0.005, max_constants=4)
    return cal, res


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    quick = "--quick" in sys.argv
    n_cycles = 300 if quick else 2500

    base = read_baseline()
    cal, res = run_raised_fit(n_cycles)
    mae_new = float(res["mae_by_condition"]["sobretorque"])
    f0_new = float(res["F0_estimates"]["sobretorque"])
    verdict = classify_verdict(base["mae"], mae_new, f0_new, F0_SANITY_N)

    print("== sobretorque: bound F0 120 kN -> %.1f kN (sanity) ==" %
          (F0_SANITY_N / 1e3))
    print(f"baseline : MAE {base['mae']:.4f}  F0 {base['f0_N']/1e3:.1f} kN "
          f"(global {base['mae_global']:.4f})")
    print(f"raised   : MAE {mae_new:.4f}  F0 {f0_new/1e3:.1f} kN "
          f"(global {res['mae_global']:.4f})  livres {res['free_constants']}")
    print(f"veredicto: {verdict['verdict']}  "
          f"(dMAE {verdict['delta_mae']:+.4f}, "
          f"cravado_no_teto={verdict['pinned_at_new_ceiling']})")

    if quick:
        print("--quick: smoke (NAO cientifico); nenhum artefato gravado.")
        return

    # plot: TP6 + sim do bound elevado (baseline anotado no titulo)
    sob = next(c for c in cal.cfg.conditions if c.name == "sobretorque")
    sim_N, sim_ratio = cal._run_condition(sob)
    fig, ax = plt.subplots(figsize=(8, 5))
    for c in sob.curves:
        ax.plot(c["cycles"], c["ratio"], "o-", ms=4, color="#00B050",
                alpha=0.8, label=c["name"])
    ax.plot(sim_N, sim_ratio, "k-", lw=2.5,
            label=f"sim bound {F0_SANITY_N/1e3:.0f}kN "
                  f"(MAE={mae_new:.3f}, F0={f0_new/1e3:.1f}kN)")
    ax.set_title(f"sobretorque — baseline 120kN MAE {base['mae']:.3f}  |  "
                 f"veredicto: {verdict['verdict']}", fontsize=9)
    ax.set_xlabel("Ciclos N"); ax.set_ylabel(r"$F_0/F_{0,init}$")
    ax.set_xlim(0, n_cycles); ax.set_ylim(0, 1.05); ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    fig.savefig(OUT_PNG, dpi=120)

    out = dict(
        campaign="Fase 2 — sobretorque F0-bound (MODEL_LEGITIMACY §4.5)",
        provenance=dict(
            f0_ceiling_N=F0_SANITY_N,
            f0_ceiling_formula="0.9 * Rp0.2(10.9=940MPa) * A_s(M16=157mm2)",
            only_change="estimate_F0[sobretorque] top 120kN -> 132.8kN",
            canonical_shared_block="NAO escrito (experimento)"),
        thresholds=dict(RESCUE_MAE=RESCUE_MAE, PERSIST_MAE=PERSIST_MAE),
        baseline=base,
        raised=dict(mae_sobretorque=mae_new, f0_test_N=f0_new,
                    mae_global=res["mae_global"],
                    free_constants=res["free_constants"],
                    constants=res["constants"],
                    selection_history=res["selection_history"],
                    mae_by_condition=res["mae_by_condition"],
                    F0_estimates=res["F0_estimates"]),
        verdict=verdict,
        caveat=("GW k_tr(F0) tem sinal desfavoravel no slip atual (spec Fase 1 "
                "§4) — 'missing mechanism' NAO avaliza k_tr(F0) ingenuo."))
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")

    lines = [
        "# Sobretorque — discriminacao do bound F0 (Fase 2)", "",
        f"Baseline (bound 120 kN): MAE {base['mae']:.4f}, "
        f"F0 {base['f0_N']/1e3:.1f} kN, global {base['mae_global']:.4f}.", "",
        f"Bound elevado ao teto de sanidade ({F0_SANITY_N/1e3:.1f} kN): "
        f"MAE {mae_new:.4f}, F0 {f0_new/1e3:.1f} kN, "
        f"global {res['mae_global']:.4f}.", "",
        f"**Veredicto (pre-registrado): {verdict['verdict']}** "
        f"(dMAE {verdict['delta_mae']:+.4f}; "
        f"cravado no teto: {verdict['pinned_at_new_ceiling']}).", "",
        "Ressalva: GW k_tr(F0) tem sinal desfavoravel no slip atual "
        "(spec Fase 1 §4).",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Artefatos: {OUT_JSON.name}, {OUT_PNG.name}, {OUT_MD.name}")


if __name__ == "__main__":
    main()
