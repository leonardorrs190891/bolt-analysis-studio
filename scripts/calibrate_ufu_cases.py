"""Calibrate BAS against the three UFU Junker lab trials.

Fits mu_initial + TwoStageLooseningParams (C_loosening, N_stage1,
delta_F1_ratio, k_stage2) for each UFU .msd case against its measured
reference curve. Writes the calibrated values back into the .msd file so
they persist as project-level defaults (model.mu_initial + model._two_stage_overrides).

Run:
    python scripts/calibrate_ufu_cases.py
"""
from __future__ import annotations

import csv
import json
import os
import sys

import numpy as np

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'src'))

from bolt_analysis_studio.core.models.model import MSDModel
from bolt_analysis_studio.numerical.parameter_identifier import (
    ParameterIdentifier,
    mu_initial_param,
    C_loosening_param,
    N_stage1_param,
    delta_F1_ratio_param,
    k_stage2_param,
)


CASES = [
    ("UFU 5A",        "Models/EXPERIMENTAL_UFU/UFU_5A.msd",
     "Models/EXPERIMENTAL_UFU/reference_curves/UFU_5A_preload_decay.csv"),
    ("UFU 13A 1st",   "Models/EXPERIMENTAL_UFU/UFU_13A_first.msd",
     "Models/EXPERIMENTAL_UFU/reference_curves/UFU_13A_first_preload_decay.csv"),
    ("UFU 13A def",   "Models/EXPERIMENTAL_UFU/UFU_13A_def.msd",
     "Models/EXPERIMENTAL_UFU/reference_curves/UFU_13A_def_preload_decay.csv"),
]


def load_reference_csv(path: str) -> tuple[np.ndarray, np.ndarray]:
    """Return (cycle, F/F0). Auto-skips header; uses column 2 (F/F0) if
    present else derives from column 1 (F_kN) / F_kN[0]."""
    cycles, f_ratios, f_kn = [], [], []
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.reader(fh)
        for row in reader:
            if not row:
                continue
            try:
                c = float(row[0])
            except (ValueError, IndexError):
                continue
            cycles.append(c)
            f_kn.append(float(row[1]) if len(row) >= 2 else 0.0)
            if len(row) >= 3:
                try:
                    f_ratios.append(float(row[2]))
                except ValueError:
                    f_ratios.append(0.0)
            else:
                f_ratios.append(0.0)
    cyc = np.asarray(cycles, dtype=float)
    ratios = np.asarray(f_ratios, dtype=float)
    kn = np.asarray(f_kn, dtype=float)
    if np.all(ratios == 0.0) and kn.size > 0 and kn[0] > 0:
        ratios = kn / kn[0]
    return cyc, ratios


def calibrate_case(name: str, msd_path: str, ref_path: str,
                   n_starts: int = 4, max_evals: int = 200) -> dict:
    """Load model, run ParameterIdentifier, return best params + stats."""
    print(f"\n=== {name} ===")
    print(f"  model: {msd_path}")
    print(f"  ref:   {ref_path}")

    # Load .msd model
    abs_msd = os.path.join(ROOT, msd_path)
    with open(abs_msd, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    model = MSDModel.from_dict(data)

    # Derive F_transverse from delta_amplitude (UFU uses ±0.5 mm prescribed
    # displacement); fallback if model lacks k_transverse
    gl = model.global_loading
    if getattr(gl, 'F_transverse', 0.0) <= 0:
        # Rough k_trans estimate: 100 kN / 1 mm = 1e8 N/m is typical for the rig
        k_trans = float(getattr(model, 'k_transverse_total', 0.0) or 1.0e8)
        gl.F_transverse = (float(getattr(gl, 'delta_amplitude', 0.5)) * 1e-3) * k_trans
        print(f"  derived F_transverse = {gl.F_transverse:.0f} N (k_trans = {k_trans:.2e} N/m)")

    # Load reference
    abs_ref = os.path.join(ROOT, ref_path)
    ref_cycle, ref_ratio = load_reference_csv(abs_ref)
    print(f"  ref points: {len(ref_cycle)} (cycle 0 -> {ref_cycle[-1]:.0f})")
    print(f"  ref F/F0:   {ref_ratio[0]:.3f} -> {ref_ratio[-1]:.3f}")

    # Fit 5 params jointly
    params = [
        mu_initial_param(lo=0.06, hi=0.25),
        C_loosening_param(lo=0.05, hi=2.5),
        N_stage1_param(lo=20, hi=300),
        delta_F1_ratio_param(lo=0.05, hi=0.45),
        k_stage2_param(lo=1e-6, hi=5e-3),
    ]

    identifier = ParameterIdentifier(
        model, ref_cycle, ref_ratio,
        params_to_fit=params,
        objective="mae",
        max_evals=max_evals,
        seed=42,
    )

    def _progress(n, nmax, best):
        if n % 10 == 0:
            print(f"  eval {n:4d}/{nmax} — MAE = {best:.4f}")
    identifier.set_progress_callback(_progress)

    result = identifier.run(n_starts=n_starts)
    print(f"  -> best MAE  = {result.best_mae:.4f}")
    print(f"  -> best RMSE = {result.best_rmse:.4f}")
    print(f"  -> evals     = {result.n_evals} in {result.duration_s:.1f}s")
    for k, v in result.best_params.items():
        print(f"     {k:20s} = {v}")

    # Write calibrated values back into .msd
    model.mu_initial = result.best_params.get("mu_initial", getattr(model, 'mu_initial', 0.12))
    two_stage_overrides = {
        k: v for k, v in result.best_params.items() if k != "mu_initial"
    }
    model._two_stage_overrides = two_stage_overrides

    # Also update global_loading.mu_initial so in-session picks it up
    gl.mu_initial = model.mu_initial

    # Save
    with open(abs_msd, 'w', encoding='utf-8') as fh:
        json.dump(model.to_dict(), fh, indent=2, ensure_ascii=False)
    print(f"  saved -> {abs_msd}")

    return {
        "case": name,
        "mae": result.best_mae,
        "rmse": result.best_rmse,
        "n_evals": result.n_evals,
        "params": dict(result.best_params),
    }


def main():
    summary = []
    for name, msd, ref in CASES:
        try:
            summary.append(calibrate_case(name, msd, ref))
        except Exception as e:
            print(f"  FAILED: {e}")
            import traceback; traceback.print_exc()
            summary.append({"case": name, "error": str(e)})

    # Print summary table
    print("\n" + "=" * 70)
    print(f"{'Case':<15} {'MAE':>8} {'RMSE':>8} {'mu':>6} {'C_loos':>7} {'N1':>4}")
    print("-" * 70)
    for s in summary:
        if "error" in s:
            print(f"{s['case']:<15} ERROR: {s['error']}")
            continue
        p = s["params"]
        print(f"{s['case']:<15} {s['mae']:>8.4f} {s['rmse']:>8.4f} "
              f"{p.get('mu_initial', 0):>6.3f} "
              f"{p.get('C_loosening', 0):>7.3f} "
              f"{int(p.get('N_stage1', 0)):>4d}")

    # Save summary
    out_path = os.path.join(ROOT, "Models", "EXPERIMENTAL_UFU",
                             "calibration_summary.json")
    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    print(f"\nSummary saved to {out_path}")


if __name__ == "__main__":
    main()
