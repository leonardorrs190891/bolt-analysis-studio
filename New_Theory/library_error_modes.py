"""Analise de MODOS DE ERRO por curva, biblioteca inteira (pedido do professor
2026-07-08: "the previous analysis for all 40 curves").

Para cada uma das 46 curvas da varredura §1A, roda o modelo em DUAS configs
(baseline doutrina-default e pack slip-regime §4.12) e decompoe o residuo como
no bloco axial: split early/late, vies vs forma, erro final, e CLASSIFICA o modo
de erro dominante:
  collapse-missed  dado colapsa (<0.4) e modelo retem >> (falta onset)
  over-collapse    modelo colapsa alem do dado
  tail-slope       residuo concentrado na cauda (forma lenta errada)
  settling-early   residuo concentrado no inicio (nivel de assentamento)
  level-bias       offset ~uniforme (nivel per-rig)
  noise-floor      MAE < 0.03 (~piso; nada estrutural a melhorar)
Agrega por fonte => backlog de melhoria RANQUEADO (o que falta melhorar).

Run: python New_Theory/library_error_modes.py   (~5-10 min, 92 sims)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
import transfer_validation as tv  # noqa: E402
from library_common import load_full_curve  # noqa: E402


def classify(cyc, data, pred, mae):
    e_final = float(pred[-1] - data[-1])
    res = pred - data
    bias = float(np.mean(res))
    n_split = cyc[0] + (cyc[-1] - cyc[0]) * 0.15          # primeiros 15% do range
    early = cyc <= n_split
    mae_e = float(np.mean(np.abs(res[early]))) if early.any() else 0.0
    mae_l = float(np.mean(np.abs(res[~early]))) if (~early).any() else 0.0
    if mae < 0.03:
        mode = "noise-floor"
    elif data[-1] < 0.4 and e_final > 0.25:
        mode = "collapse-missed"
    elif e_final < -0.25:
        mode = "over-collapse"
    elif abs(bias) > 0.8 * mae:
        mode = "level-bias"
    elif mae_l > 2.0 * max(mae_e, 1e-9):
        mode = "tail-slope"
    elif mae_e > 2.0 * max(mae_l, 1e-9):
        mode = "settling-early"
    else:
        mode = "shape-mixed"
    return dict(mode=mode, e_final=e_final, bias=bias, mae_early=mae_e, mae_late=mae_l)


def run_config(cases, slip_regime):
    tv._SLIP_REGIME = slip_regime
    out = []
    for case in cases:
        cyc, ratio = load_full_curve(case.reference_csv_path)
        keep = ratio >= tv.FLOOR_TRIM
        cyc_d, r_d = cyc[keep], ratio[keep]
        n0 = cyc_d[0]
        r_al = r_d / r_d[0]
        inp = tv.inputs_for(case)
        mae, pred, _ = tv._mae_curve(case, inp, cyc_d, r_al, n0)
        out.append(dict(csv=Path(case.reference_csv_path).name, source=case.source.name,
                        mae=mae, **classify(cyc_d, r_al, np.asarray(pred), mae)))
        print(f"  [{'pack' if slip_regime else 'base'}] {out[-1]['csv']:44s} "
              f"MAE={mae:.3f} {out[-1]['mode']}", flush=True)
    return out


def main():
    cases, _ = tv.select_cases()
    print(f"{len(cases)} curvas; 2 configs (baseline, pack §4.12)\n")
    base = run_config(cases, False)
    pack = run_config(cases, True)

    print("\n== POR CURVA: melhor config + modo ==")
    rows = []
    for b, p in zip(base, pack):
        best = p if p["mae"] < b["mae"] else b
        cfg = "pack" if p["mae"] < b["mae"] else "base"
        rows.append(dict(csv=b["csv"], source=b["source"], cfg=cfg,
                         mae_base=b["mae"], mae_pack=p["mae"],
                         mode_best=best["mode"], e_final=best["e_final"]))
    for r in sorted(rows, key=lambda x: -min(x["mae_base"], x["mae_pack"])):
        print(f"  {r['csv']:44s} base={r['mae_base']:.3f} pack={r['mae_pack']:.3f} "
              f"best={r['cfg']:4s} modo={r['mode_best']:15s} e_fim={r['e_final']:+.3f}")

    print("\n== POR FONTE: modo dominante (na melhor config) ==")
    by_src = {}
    for r in rows:
        by_src.setdefault(r["source"], []).append(r)
    for src, rs in sorted(by_src.items()):
        modes = {}
        for r in rs:
            modes[r["mode_best"]] = modes.get(r["mode_best"], 0) + 1
        dom = max(modes.items(), key=lambda kv: kv[1])
        med = float(np.median([min(r["mae_base"], r["mae_pack"]) for r in rs]))
        print(f"  {src:15s} n={len(rs):2d} medianMAE(best)={med:.3f} "
              f"modos={modes} dominante={dom[0]}")

    (ROOT / "New_Theory" / "library_error_modes.json").write_text(
        json.dumps(rows, indent=1), encoding="utf-8")
    print("\nArtefato: library_error_modes.json")


if __name__ == "__main__":
    main()
