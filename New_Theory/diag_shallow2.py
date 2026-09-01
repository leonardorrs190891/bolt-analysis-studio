"""Diagnostico shallow-collapse, nivel 2: decomposicao por JANELA + gates.
Conformacao descartada (gate=1.0 sempre). Quem morre no plato?
Run: python New_Theory/diag_shallow2.py
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
    k_tr_transverse, resolve_transverse_slip, self_locking_gate)
from library_common import geometry_for, emb_depth_vdi, frozen_constants, load_full_curve  # noqa: E402

TARGETS = ["bauer2024_M12_fig8_test2", "liu2025_M16_amp0p5"]
C_BEND_RIG = {"LU_2024": 0.7, "KARLSEN_2022": 2.5}


def probe(case):
    inp = tv.inputs_for(case)
    consts, _ = frozen_constants()
    emb_m, _ = emb_depth_vdi(inp["rz"]["value"], 1)
    geom = geometry_for(case.bolt_size, grip_mm=inp["grip_mm"]["value"])
    mu = inp["mu"]["value"]
    mat = JointMaterial(emb_depth=emb_m, mu_thread=mu, mu_bearing=mu,
                        conform_driver="effective",
                        slip_regime_mode="cattaneo_mindlin", slip_regime_sharpness=1.0,
                        k_tr_mode="bending", c_bend=C_BEND_RIG.get(case.source.name, 0.30),
                        loose_torsion_mode="bolt_torsion", eta_loose=15.0,
                        loose_arrest_floor=0.08, **consts)
    F0 = case.initial_preload_N
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    cyc_d, _ = load_full_curve(case.reference_csv_path)
    n_max = int(cyc_d[-1])
    delta = case.transverse_displacement_mm * 1e-3
    F_amp = inp["F_amp_N"]["value"]
    print(f"\n== {Path(case.reference_csv_path).stem} ==  F0={F0/1e3:.1f}kN "
          f"grip={inp['grip_mm']['value']}mm amp={case.transverse_displacement_mm}mm")
    qs = [0, n_max // 4, n_max // 2, 3 * n_max // 4, n_max]
    prev_cum = {}
    for qi in range(4):
        cum = {}
        for n in range(qs[qi] + 1, qs[qi + 1] + 1):
            ana.step_cycle(F_amp, np.pi / 2, case.frequency_Hz, delta_amp=delta)
            for m, dF in ana.history[-1].dF_0_by_mech.items():
                cum[m] = cum.get(m, 0.0) + dF
        st = ana.state
        slip = resolve_transverse_slip(st, mat, F_amp, np.pi / 2, delta, geom=geom)
        dt = F_slip_transverse(st, mat) / max(k_tr_transverse(geom, mat), 1e-12)
        Tr = T_resistance(st, geom, mat)
        print(f"  Q{qi+1} [{qs[qi]}..{qs[qi+1]}]: r={max(st.F_0,0)/F0:.3f} "
              f"theta={np.degrees(st.theta_loose):.1f}deg slip={slip*1e3:.3f}mm "
              f"dt={dt*1e3:.3f}mm lock_gate={self_locking_gate(st, mat):.2f}")
        print(f"      dF0: " + "  ".join(f"{m}={v:+.0f}N" for m, v in sorted(cum.items())
                                          if abs(v) > 1))
        prev_cum = cum


def main():
    cases, _ = tv.select_cases()
    by_stem = {Path(c.reference_csv_path).stem: c for c in cases}
    for t in TARGETS:
        probe(by_stem[t])


if __name__ == "__main__":
    main()
