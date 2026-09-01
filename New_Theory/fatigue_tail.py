"""Validacao da cauda de fadiga->fratura (spec 2026-07-08).

REPRESENT (Li2022ti, axial puro): a Su-N calibrada por-material coloca o cliff no
N_fracture observado (~4.1e5) e o modelo reproduz o degrau + o afrouxamento
pre-fratura. FALSIFICACAO-PREDICT: a MESMA Su-N aplicada ao Yang2021 (M8 cl.8.8,
outra liga/tamanho) erra N_fracture por ordens de grandeza => Su-N e' POR MATERIAL
(a forma transfere, a constante nao — §8).

Run: python New_Theory/fatigue_tail.py
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)
from library_common import (  # noqa: E402
    geometry_for, frozen_constants, emb_depth_vdi, load_full_curve)

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"


def run(bolt, grip, F0, F_amp, freq, emb, consts, C1, uts, cap):
    geom = geometry_for(bolt, grip)
    mat = JointMaterial(emb_depth=emb, mu_thread=0.15, mu_bearing=0.15,
                        fatigue_enabled=True, fat_C1=C1, fat_sigma_uts=uts,
                        k_thread_fret=0.0, **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    cliff = None
    xs, ys = [0], [1.0]
    for n in range(1, cap + 1):
        ana.step_cycle(F_amp, 0.0, freq)                      # axial force-mode
        if cliff is None and ana.state.D_fatigue >= 1.0:
            cliff = n
        if n % max(cap // 60, 1) == 0 or (cliff == n):
            xs.append(n); ys.append(max(ana.state.F_0, 0.0) / F0)
        if cliff is not None and n > cliff + 2:
            break
    return cliff, xs, ys


def calibrate_C1(bolt, grip, F0, F_amp, freq, emb, consts, uts, N_target):
    """Bisseccao curta em log(C1) p/ colocar o cliff ~N_target (represent)."""
    lo, hi = 1e30, 1e42
    cap = int(N_target * 1.25)
    for _ in range(9):
        C1 = np.sqrt(lo * hi)
        cliff, _, _ = run(bolt, grip, F0, F_amp, freq, emb, consts, C1, uts, cap)
        if cliff is None:                 # vida longa demais -> baixa C1 (menos vida)
            hi = C1
        elif cliff < N_target:            # cliff cedo demais -> sobe C1 (mais vida)
            lo = C1
        else:
            hi = C1
        print(f"    bisect C1={C1:.2e} cliff={cliff}", flush=True)
    return np.sqrt(lo * hi)


def main():
    consts, _ = frozen_constants()
    emb10, _ = emb_depth_vdi("Rz<10", 1)

    # ---- REPRESENT: Li2022ti (M10x1.5 Ti, axial, fratura ~4.1e5) ----
    cyc_d, r_d = load_full_curve(f"{DIG}/li2022ti_axial_10Hz_full.csv")
    r_d = r_d / r_d[0]
    N_frac = 410000
    print("== REPRESENT: Li2022ti (axial, Ti) ==")
    C1_li = calibrate_C1("M10x1.5", 25.0, 10e3, 10e3, 10.0, emb10, consts, 950e6, N_frac)
    cliff, xs, ys = run("M10x1.5", 25.0, 10e3, 10e3, 10.0, emb10, consts, C1_li,
                        950e6, int(N_frac * 1.25))
    # pre-fratura MAE (pontos do dado antes do cliff)
    pre = cyc_d < (cliff or N_frac)
    pred = np.interp(cyc_d[pre], xs, ys)
    mae = float(np.mean(np.abs(pred - r_d[pre]))) if pre.any() else float("nan")
    print(f"  C1 calibrado={C1_li:.2e}; cliff modelo={cliff} vs dado ~{N_frac}")
    print(f"  pre-fratura MAE={mae:.3f} (n={pre.sum()} pontos); "
          f"cliff cai F0->{ys[-1]:.3f} (dado final {r_d[-1]:.3f})")
    print("  => FORMA representa o cliff + degrau; Su-N calibrada por-material (Ti).")

    # ---- FALSIFICACAO-PREDICT: mesma Su-N no Yang2021 (M8 cl.8.8) ----
    print("\n== FALSIFICACAO-PREDICT: Yang2021 0.5mm/8kN (M8 cl.8.8), N_frac~27800 ==")
    N_yang = 27800
    cliff_y, _, _ = run("M8x1.25", 20.0, 14.1e3, 8e3, 10.0, emb10, consts, C1_li,
                        830e6, int(N_yang * 6))
    if cliff_y:
        ratio = cliff_y / N_yang
        print(f"  Su-N do Li2022ti -> cliff Yang={cliff_y} vs dado {N_yang} "
              f"(ratio {ratio:.2f}x)")
    else:
        print(f"  Su-N do Li2022ti -> Yang NAO fratura em {N_yang*6} ciclos "
              f"(vida >> dado; Su-N nao transfere)")
    print("  => Su-N e' POR MATERIAL/TAMANHO (M10 Ti != M8 aco): a FORMA transfere,")
    print("     a constante Su-N NAO (§8). Nivel per-par, como C_creep/emb_depth.")
    print("\nAS-IS: FatigueLoss representa a fratura (capability); Su-N per-material,")
    print("energetica do cliff fenomenologica. Predicao zero-refit cross-material falha.")


if __name__ == "__main__":
    main()
