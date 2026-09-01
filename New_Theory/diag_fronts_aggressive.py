"""Diagnostico instrumentado dos 2 fronts dominantes do modo agressivo (iter 9):
FRONT A = Lu fig20 (sweep de torque INTEIRO acima do limite: T4 0.253 ... T16
0.118) + fig18 amp0p5/amp1p0; FRONT B = HDPE t10/t12/t14. Config = a ADOTADA
da galeria (labels). Por caso: erro por janela (qual FASE erra), decomposicao
por mecanismo, gates no ciclo 1, fracao de assentamento k_b*emb/F0, e as
features do DADO (fast-drop, slope central, plato).

Run: python New_Theory/diag_fronts_aggressive.py
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
import transfer_validation as tv  # noqa: E402
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial, T_resistance, F_slip_transverse,
    k_tr_transverse, resolve_transverse_slip)
from library_common import geometry_for, frozen_constants, load_full_curve  # noqa: E402

PACK = dict(conform_driver="effective", slip_regime_mode="cattaneo_mindlin",
            slip_regime_sharpness=1.0, k_tr_mode="bending",
            loose_torsion_mode="bolt_torsion", eta_loose=15.0)
LU = dict(PACK, c_bend=5.0, delta_free=0.28e-3, k_ratchet=0.05,
          loose_arrest_floor=0.22, emb_um=8.0)
HDPE = dict(PACK, c_bend=0.2, loose_arrest_floor=0.15, emb_um=None,
            _consts=dict(k_j_init=2e7, k_creep_scale=3.0))

FRONTS = [
    ("LU fig20 (torque sweep)", LU, ["lu2024_M8_fig20_T4Nm", "lu2024_M8_fig20_T10Nm",
                                     "lu2024_M8_fig20_T16Nm", "lu2024_M8_fig20_T22Nm",
                                     "lu2024_M8_fig20_T28Nm"]),
    ("LU fig18 (amp sweep, residuais)", LU, ["lu2024_M8_fig18_amp0p5", "lu2024_M8_fig18_amp1p0"]),
    ("HDPE (espessura)", HDPE, ["rousseau2025_hdpe_t10", "rousseau2025_hdpe_t12",
                                "rousseau2025_hdpe_t14"]),
]


def probe(case, kw):
    kw = dict(kw)
    consts, _ = frozen_constants()
    consts.update(kw.pop("_consts", {}))
    emb = kw.pop("emb_um", None)
    inp = tv.inputs_for(case)
    from library_common import emb_depth_vdi
    emb_m = (emb * 1e-6) if emb is not None else emb_depth_vdi(inp["rz"]["value"], 1)[0]
    geom = geometry_for(case.bolt_size, grip_mm=inp["grip_mm"]["value"])
    mu = inp["mu"]["value"]
    mat = JointMaterial(emb_depth=emb_m, mu_thread=mu, mu_bearing=mu, **kw, **consts)
    F0 = case.initial_preload_N
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    cyc, ratio = load_full_curve(case.reference_csv_path)
    keep = ratio >= tv.FLOOR_TRIM
    cyc_d = cyc[keep]
    n0, r_al = cyc_d[0], ratio[keep] / ratio[keep][0]
    n_max = int(cyc_d[-1])
    delta = case.transverse_displacement_mm * 1e-3
    F_amp = inp["F_amp_N"]["value"]

    st = ana.state
    slip0 = resolve_transverse_slip(st, mat, F_amp, np.pi / 2, delta, geom=geom)
    dtt = mat.delta_free + F_slip_transverse(st, mat) / max(k_tr_transverse(geom, mat), 1e-12)
    T_res = T_resistance(st, geom, mat)
    L_tr = mat.tr_loose_gain * mat.Phi_tr_correction * np.cos(geom.beta) * F_amp
    settle_frac = geom.k_b * mat.emb_depth / F0

    r = np.empty(n_max + 1); r[0] = 1.0
    cum = {}
    for n in range(1, n_max + 1):
        ana.step_cycle(F_amp, np.pi / 2, case.frequency_Hz, delta_amp=delta)
        r[n] = max(ana.state.F_0, 0.0) / F0
        for m, dF in ana.history[-1].dF_0_by_mech.items():
            cum[m] = cum.get(m, 0.0) + dF
    r_alm = r / max(np.interp(n0, np.arange(n_max + 1), r), 1e-9)
    pred = np.interp(cyc_d, np.arange(n_max + 1), r_alm)
    err = pred - r_al
    mae = float(np.mean(np.abs(err)))

    # janelas: early (<=20% N), mid (20-70%), late (>70%)
    w_e = cyc_d <= 0.2 * n_max
    w_m = (cyc_d > 0.2 * n_max) & (cyc_d <= 0.7 * n_max)
    w_l = cyc_d > 0.7 * n_max
    def werr(w):
        return float(np.mean(err[w])) if w.sum() else float("nan")
    # features do dado
    fast_d = float(1.0 - r_al[w_e][-1]) if w_e.sum() else float("nan")
    tot = sum(abs(v) for v in cum.values()) or 1.0
    shares = "  ".join(f"{m}={100*abs(v)/tot:.0f}%" for m, v in sorted(cum.items()) if abs(v) / tot > 0.02)
    stem = Path(case.reference_csv_path).stem
    print(f"\n== {stem} ==  F0={F0/1e3:.1f}kN amp={case.transverse_displacement_mm}mm N={n_max}")
    print(f"  MAE {mae:.3f} | bias janela: early {werr(w_e):+.3f}  mid {werr(w_m):+.3f}  late {werr(w_l):+.3f}"
          f"  | fim mod {pred[-1]:.3f} vs dado {r_al[-1]:.3f}")
    print(f"  dado: fast-drop(20%N) {fast_d:.3f} | settle_frac k_b*emb/F0 = {settle_frac:.3f}")
    print(f"  ciclo1: slip {slip0*1e3:.3f}mm vs delta_t {dtt*1e3:.3f}mm | "
          f"T_l/T_r {L_tr*geom.d_2/2/max(T_res,1e-9):.2f} | theta_fim {np.degrees(ana.state.theta_loose):.1f}deg")
    print(f"  shares: {shares}")


def main():
    cases, _ = tv.select_cases()
    by_stem = {Path(c.reference_csv_path).stem: c for c in cases}
    for title, kw, stems in FRONTS:
        print(f"\n######## {title} ########")
        for s in stems:
            if s in by_stem:
                probe(by_stem[s], kw)
            else:
                print(f"  [ausente do select_cases: {s}]")


if __name__ == "__main__":
    main()
