"""Diagnostico dos shallow-collapse finais (16 restantes, 2026-07-08).

Hipotese (§4.9 caveat): o conformation_gate com W_conf_ref=7671 J (constante
POR-PAR âncora interna, ancora FALHOU na Fase 3) enche em rigs de slip alto e ARRESTA o
colapso num plato ACIMA do dado. Teste A/B: pack per-rig vs mesmo config com
W_conf_ref=0 (conformacao off). Loga o gate ao longo dos ciclos.

Run: python New_Theory/diag_shallow_collapse.py
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
    DynamicStiffnessAnalyzer, JointMaterial, conformation_gate)
from library_common import geometry_for, emb_depth_vdi, frozen_constants, load_full_curve  # noqa: E402

TARGETS = ["bauer2024_M12_fig8_test2", "demir2024_amp0p4_F17p6_lk19p8",
           "liu2025_M16_amp0p5", "bauer2024_M8_fig6_rep3"]
C_BEND_RIG = {"LU_2024": 0.7, "KARLSEN_2022": 2.5}


def run(case, w_conf_ref):
    inp = tv.inputs_for(case)
    consts, _ = frozen_constants()
    if w_conf_ref is not None:
        consts["W_conf_ref"] = w_conf_ref
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
    cyc_d, r_d = load_full_curve(case.reference_csv_path)
    n_max = int(cyc_d[-1])
    delta = case.transverse_displacement_mm * 1e-3
    F_amp = inp["F_amp_N"]["value"]
    gates, marks = [], [n_max // 20, n_max // 5, n_max // 2, n_max]
    for n in range(1, n_max + 1):
        ana.step_cycle(F_amp, np.pi / 2, case.frequency_Hz, delta_amp=delta)
        if n in marks:
            gates.append((n, conformation_gate(ana.state, mat),
                          max(ana.state.F_0, 0.0) / F0))
    fin = max(ana.state.F_0, 0.0) / F0
    return fin, gates, float(r_d[-1] / r_d[0])


def main():
    cases, _ = tv.select_cases()
    by_stem = {Path(c.reference_csv_path).stem: c for c in cases}
    for t in TARGETS:
        case = by_stem[t]
        fin_on, gates_on, d_fin = run(case, None)          # frozen (7671)
        fin_off, _, _ = run(case, 0.0)                     # conformacao OFF
        gs = "  ".join(f"N={n}: gate={g:.2f} r={r:.2f}" for n, g, r in gates_on)
        print(f"\n== {t} ==  dado_fim={d_fin:.3f}")
        print(f"  W_conf ON  (7671): fim={fin_on:.3f}   [{gs}]")
        print(f"  W_conf OFF (0):    fim={fin_off:.3f}")
        print(f"  => gate {'E O PLATO' if abs(fin_off-d_fin) < abs(fin_on-d_fin)-0.05 else 'nao explica sozinho'}")


if __name__ == "__main__":
    main()
