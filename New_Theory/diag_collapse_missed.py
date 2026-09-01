"""Diagnostico do modo collapse-missed (systematic-debugging fase 1, 2026-07-08).

Instrumenta o pack §4.12 nos piores casos: o loosening DISPARA? O que o limita?
Imprime por janela: T_loose vs T_resist, gate de regime, d_theta acumulado, e a
decomposicao por mecanismo. Contraste chave: lu2024 amp0.25 (OK) vs amp2.0
(pior, e_fim +0.70) — se d_theta NAO escala com a amplitude, a cegueira de
amplitude do drive (F_tr = 0.4*F0 assumido) esta' confirmada quantitativamente.

Run: python New_Theory/diag_collapse_missed.py
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
    k_tr_transverse, loosening_slip_gate, resolve_transverse_slip)
from library_common import geometry_for, emb_depth_vdi, frozen_constants, load_full_curve  # noqa: E402

TARGETS = ["lu2024_M8_fig18_amp0p25", "lu2024_M8_fig18_amp2p0",
           "lu2024_M8_fig20_T22Nm", "karlsen2022_M30_HV_run2p2"]


def probe(case):
    inp = tv.inputs_for(case)
    consts, _ = frozen_constants()
    emb_m, _ = emb_depth_vdi(inp["rz"]["value"], 1)
    geom = geometry_for(case.bolt_size, grip_mm=inp["grip_mm"]["value"])
    mu = inp["mu"]["value"]
    kw = dict(emb_depth=emb_m, mu_thread=mu, mu_bearing=mu, conform_driver="effective",
              slip_regime_mode="cattaneo_mindlin", slip_regime_sharpness=1.0,
              k_tr_mode="bending", c_bend=0.30,
              loose_torsion_mode="bolt_torsion", eta_loose=15.0, loose_arrest_floor=0.08)
    mat = JointMaterial(**kw, **consts)
    F0 = case.initial_preload_N
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    delta = case.transverse_displacement_mm * 1e-3
    F_amp = inp["F_amp_N"]["value"]
    cyc_d, r_d = load_full_curve(case.reference_csv_path)
    n_max = int(min(cyc_d[-1], 4000))

    st = ana.state
    slip0 = resolve_transverse_slip(st, mat, F_amp, np.pi / 2, delta, geom=geom)
    dt = F_slip_transverse(st, mat) / max(k_tr_transverse(geom, mat), 1e-12)
    print(f"\n== {Path(case.reference_csv_path).stem} ==")
    print(f"  F0={F0/1e3:.1f}kN d={case.bolt_size} grip={inp['grip_mm']['value']:.0f}mm "
          f"amp={case.transverse_displacement_mm}mm F_amp(assumido)={F_amp/1e3:.1f}kN")
    print(f"  slip_amp={slip0*1e3:.3f}mm delta_t={dt*1e3:.3f}mm "
          f"gate_regime(c1)={loosening_slip_gate(st, geom, mat, slip0):.3f}")
    T_res = T_resistance(st, geom, mat)
    # T_loose com o drive ASSUMIDO (F_tr = F_amp): mesmo caminho do engine
    L_tr = mat.tr_loose_gain * mat.Phi_tr_correction * np.cos(geom.beta) * F_amp
    print(f"  T_loose(assumido)={L_tr*geom.d_2/2:.2f} N.m vs T_resist={T_res:.2f} N.m "
          f"(razao {L_tr*geom.d_2/2/max(T_res,1e-9):.2f})")

    cum = {}
    for n in range(1, n_max + 1):
        ana.step_cycle(F_amp, np.pi / 2, case.frequency_Hz, delta_amp=delta)
        for m, dF in ana.history[-1].dF_0_by_mech.items():
            cum[m] = cum.get(m, 0.0) + dF
    tot = sum(abs(v) for v in cum.values()) or 1.0
    fin = max(ana.state.F_0, 0.0) / F0
    keep = cyc_d <= n_max
    d_fin = float((r_d[keep] / r_d[keep][0])[-1]) if keep.sum() else float("nan")
    print(f"  @N={n_max}: model={fin:.3f} data~{d_fin:.3f} theta={np.degrees(ana.state.theta_loose):.1f}deg")
    print("  shares dF0: " + "  ".join(f"{m}={100*abs(v)/tot:.0f}%" for m, v in sorted(cum.items()) if abs(v) > 0))


def main():
    cases, _ = tv.select_cases()
    by_stem = {Path(c.reference_csv_path).stem: c for c in cases}
    for t in TARGETS:
        probe(by_stem[t])
    print("\nSe gate~1 e razao T_loose/T_resist ~igual entre amp0.25 e amp2.0 =>")
    print("drive amplitude-cego CONFIRMADO (F_tr assumido, nao derivado do curso).")


if __name__ == "__main__":
    main()
