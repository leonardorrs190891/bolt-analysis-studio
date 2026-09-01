"""Validacao da forma delta_free (take-up fixo) nos 3 alvos (spec 2026-07-08).

- LIU_2025: delta_0=0.30mm LIDO (N_falha ~ 1/(amp-d0), 4 pares +-3%). Carrier da
  taxa: wear (exponencial) OU ratchet (linear) — grade pequena pinada por
  analitica; rotacao runaway suprimida (legacy) p/ o carrier wear.
- LU_2024: delta_0=0.28mm (bracket fig18: 0.25 nao colapsa / 0.5 colapsa) +
  ratchet (carrier validado §4.15); frictional part pequena (c_bend alto).
  Alvo: N_falha ~flat na varredura de torque fig20 (T4..T28).
- ICMEZ: probe delta_0=0.10mm sobre a config do floor (0.042 atual).

Gates pre-declarados (design 2026-07-08): Liu2025 mediana MAE < 0.06 (vs 0.126),
amp>=0.4 N_falha dentro de +-30%, amp 0.25/0.3 retencao >= 0.6; Lu fig20 razao
N_falha(T28)/N_falha(T4) < 3 (dado ~1); A/B delta_free=0 reverte.

Run: python New_Theory/validate_delta_free.py   (~10-15 min)
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
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)
from library_common import geometry_for, emb_depth_vdi, frozen_constants, load_full_curve  # noqa: E402

PACK = dict(conform_driver="effective", slip_regime_mode="cattaneo_mindlin",
            slip_regime_sharpness=1.0, k_tr_mode="bending",
            loose_torsion_mode="bolt_torsion", eta_loose=15.0, loose_arrest_floor=0.08)


def simulate(case, mat_kw):
    inp = tv.inputs_for(case)
    consts, _ = frozen_constants()
    consts.update({k: v for k, v in mat_kw.pop("_consts", {}).items()})
    emb_m, _ = emb_depth_vdi(inp["rz"]["value"], 1)
    geom = geometry_for(case.bolt_size, grip_mm=inp["grip_mm"]["value"])
    mu = inp["mu"]["value"]
    mat = JointMaterial(emb_depth=emb_m, mu_thread=mu, mu_bearing=mu,
                        **mat_kw, **consts)
    F0 = case.initial_preload_N
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    cyc, ratio = load_full_curve(case.reference_csv_path)
    keep = ratio >= tv.FLOOR_TRIM
    cyc_d = cyc[keep]
    n0, r_al = cyc_d[0], ratio[keep] / ratio[keep][0]
    n_max = int(cyc_d[-1])
    delta = case.transverse_displacement_mm * 1e-3
    F_amp = inp["F_amp_N"]["value"]
    r = np.empty(n_max + 1); r[0] = 1.0
    for n in range(1, n_max + 1):
        ana.step_cycle(F_amp, np.pi / 2, case.frequency_Hz, delta_amp=delta)
        r[n] = max(ana.state.F_0, 0.0) / F0
    r_alm = r / max(np.interp(n0, np.arange(n_max + 1), r), 1e-9)
    pred = np.interp(cyc_d, np.arange(n_max + 1), r_alm)
    mae = float(np.mean(np.abs(pred - r_al)))
    return mae, cyc_d, r_al, pred, r_alm


def nfail(x, y, thr=0.5):
    x, y = np.asarray(x, float), np.asarray(y, float)
    b = np.where(y <= thr)[0]
    if not len(b):
        return None
    i = b[0]
    return float(x[i]) if i == 0 else float(np.interp(thr, [y[i], y[i - 1]], [x[i], x[i - 1]]))


def eval_source(cases, mat_kw, label):
    rows = []
    for case in cases:
        mae, cyc_d, r_al, pred, r_full = simulate(case, dict(mat_kw))
        nd = nfail(cyc_d, r_al)
        nm = nfail(np.arange(len(r_full)), r_full)
        rows.append((Path(case.reference_csv_path).stem, mae,
                     r_al[-1], pred[-1], nd, nm))
    med = float(np.median([r[1] for r in rows]))
    print(f"  [{label}] medianMAE={med:.3f}")
    for nm_, mae, fd, fm, nd, nmod in rows:
        rr = (nmod / nd) if (nd and nmod) else None
        print(f"    {nm_:40s} MAE={mae:.3f} fim {fd:.2f}->{fm:.2f} "
              f"Nfail_ratio={'—' if rr is None else f'{rr:.2f}'}")
    return med, rows


def main():
    cases, _ = tv.select_cases()
    by = {}
    for c in cases:
        by.setdefault(c.source.name, []).append(c)

    print("== LIU_2025 (delta_0=0.30mm lido; carriers pinados por analitica) ==")
    best_liu = None
    liu_grids = [
        ("wear kw=5e-4", dict(PACK, c_bend=5.0, delta_free=0.30e-3,
                              loose_torsion_mode="legacy", k_wear_scale_tr=5e-4)),
        ("wear kw=1e-3", dict(PACK, c_bend=5.0, delta_free=0.30e-3,
                              loose_torsion_mode="legacy", k_wear_scale_tr=1e-3)),
        ("wear kw=2e-3", dict(PACK, c_bend=5.0, delta_free=0.30e-3,
                              loose_torsion_mode="legacy", k_wear_scale_tr=2e-3)),
        ("ratchet 2e-5", dict(PACK, c_bend=5.0, delta_free=0.30e-3,
                              k_ratchet=2e-5, k_wear_scale_tr=0.0)),
        ("ratchet 5e-5", dict(PACK, c_bend=5.0, delta_free=0.30e-3,
                              k_ratchet=5e-5, k_wear_scale_tr=0.0)),
    ]
    for label, kw in liu_grids:
        med, rows = eval_source(by["LIU_2025"], kw, label)
        if best_liu is None or med < best_liu[0]:
            best_liu = (med, label, rows)
    print(f"  BEST Liu2025: {best_liu[1]} medianMAE={best_liu[0]:.3f} (antes 0.126)")

    print("\n== LU_2024 (delta_0=0.28mm bracket + ratchet §4.15) ==")
    best_lu = None
    for label, kw in [
        ("d0+ratchet 0.02", dict(PACK, c_bend=5.0, delta_free=0.28e-3, k_ratchet=0.02)),
        ("d0+ratchet 0.05", dict(PACK, c_bend=5.0, delta_free=0.28e-3, k_ratchet=0.05)),
        ("A/B sem d0 (ratchet 0.02, c=0.7)", dict(PACK, c_bend=0.70, k_ratchet=0.02)),
    ]:
        med, rows = eval_source(by["LU_2024"], kw, label)
        t = {r[0]: r for r in rows}
        n4 = t.get("lu2024_M8_fig20_T4Nm", (None,) * 6)[5]
        n28 = t.get("lu2024_M8_fig20_T28Nm", (None,) * 6)[5]
        flat = (n28 / n4) if (n4 and n28) else float("nan")
        print(f"    -> torque-flatness N(T28)/N(T4) = {flat:.2f} (dado ~1.1)")
        if best_lu is None or med < best_lu[0]:
            best_lu = (med, label)
    print(f"  BEST Lu: {best_lu[1]} medianMAE={best_lu[0]:.3f} (antes 0.215)")

    print("\n== ICMEZ probe (floor config + delta_0=0.10mm) ==")
    med, _ = eval_source(by["ICMEZ_2025"],
                         dict(PACK, c_bend=0.60, k_wear_scale_tr=0.15,
                              loose_arrest_floor=0.25, delta_free=0.10e-3),
                         "floor + d0=0.10")
    print(f"  (antes 0.042 — aceita so se melhorar)")


if __name__ == "__main__":
    main()
