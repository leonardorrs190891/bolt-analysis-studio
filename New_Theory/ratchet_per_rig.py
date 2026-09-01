"""Selecao PER-RIG do k_ratchet (doutrina §8: constante per-rig, forma transfere).

O run global (validate_ratchet, k=0.05) provou a forma (collapse-missed 28->11,
Lu -36%, finais do Karlsen alcancados) mas degradou 4 fontes — k_ratchet e'
per-rig como c_bend/eta_loose. Aqui: grid POR FONTE (declaradamente in-sample
per-rig, proveniencia 'fitted, this rig'), tabela final antes->depois.

Run: python New_Theory/ratchet_per_rig.py   (~10 min)
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
from library_error_modes import classify  # noqa: E402
from validate_ratchet import simulate  # noqa: E402

# grids por fonte (conhecimento do run global: Lu quente, Karlsen lento, demais ~0)
GRIDS = {"LU_2024": [0.02, 0.05, 0.1], "KARLSEN_2022": [0.0, 0.005, 0.01, 0.02],
         "BAUER_2024": [0.0, 0.01], "ICMEZ_2025": [0.0, 0.01],
         "LIU_2025": [0.0, 0.01], "YANG_2019": [0.0, 0.01],
         "ROUSSEAU_2025": [0.0]}                       # ratchet OFF (colapso = torque-excesso §4.12)


def main():
    cases, _ = tv.select_cases()
    by_src = {}
    for c in cases:
        by_src.setdefault(c.source.name, []).append(c)

    prev = {r["csv"]: r for r in json.loads(
        (ROOT / "New_Theory" / "library_error_modes.json").read_text(encoding="utf-8"))}
    chosen, final_rows = {}, []
    for src, cs in sorted(by_src.items()):
        results_k = {}
        for k in GRIDS[src]:
            maes = []
            for case in cs:
                mae, cyc_d, r_al, pred = simulate(case, k)
                maes.append((case, mae, cyc_d, r_al, pred))
            results_k[k] = maes
            print(f"  {src:15s} k={k:5.3f} medianMAE={np.median([m[1] for m in maes]):.3f}",
                  flush=True)
        best_k = min(results_k, key=lambda k: float(np.median([m[1] for m in results_k[k]])))
        chosen[src] = best_k
        for case, mae, cyc_d, r_al, pred in results_k[best_k]:
            csv = Path(case.reference_csv_path).name
            cl = classify(cyc_d, r_al, np.asarray(pred), mae)
            pv = prev.get(csv, {})
            final_rows.append(dict(csv=csv, source=src, k=best_k, mae=mae,
                                   mae_prev_best=min(pv.get("mae_base", 9), pv.get("mae_pack", 9)),
                                   mode=cl["mode"], mode_prev=pv.get("mode_best", "?")))

    print("\n== TABELA FINAL (melhor-anterior -> per-rig ratchet) ==")
    n_cm_b = sum(1 for r in final_rows if r["mode_prev"] == "collapse-missed")
    n_cm_a = sum(1 for r in final_rows if r["mode"] == "collapse-missed")
    for src in sorted(by_src):
        rs = [r for r in final_rows if r["source"] == src]
        med_b = float(np.median([r["mae_prev_best"] for r in rs]))
        med_a = float(np.median([r["mae"] for r in rs]))
        print(f"  {src:15s} n={len(rs):2d} k_ratchet={chosen[src]:5.3f} "
              f"medianMAE {med_b:.3f} -> {med_a:.3f}")
    med_g_b = float(np.median([r["mae_prev_best"] for r in final_rows]))
    med_g_a = float(np.median([r["mae"] for r in final_rows]))
    print(f"  GLOBAL          n={len(final_rows)} medianMAE {med_g_b:.3f} -> {med_g_a:.3f}")
    print(f"  collapse-missed {n_cm_b} -> {n_cm_a}")
    (ROOT / "New_Theory" / "ratchet_per_rig.json").write_text(
        json.dumps(dict(chosen=chosen, rows=final_rows), indent=1), encoding="utf-8")
    print("Artefato: ratchet_per_rig.json")


if __name__ == "__main__":
    main()
