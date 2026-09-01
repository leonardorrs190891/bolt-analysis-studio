"""Confronto de ENERGIA: loops de histerese medidos (loops_csv, Rousseau Figs
9a/9b/10) vs dissipacao POR CICLO do engine — a observavel que testa o coracao
energetico do modelo (W_ext + dU = sum W_diss). Area do loop (kN*mm = J/ciclo)
= todo o trabalho dissipado na junta por ciclo.

Gates pre-declarados: G-E1 area medida vs dW_diss/ciclo do modelo em FATOR-2
(mesma janela de ciclos, config ADOTADA da galeria); G-E2 pico de forca do loop
vs forca transmissivel do modelo +-30%; G-E3 (HDPE) evolucao monotona: a
dissipacao/ciclo do modelo cai com N como as areas medidas. Aco Fig10 (roller
bearings, micro-amplitudes 0.03-0.1mm): confronto informativo — hipotese
declarada ANTES: modelo preve ~0 (sub-limiar; canal de energia de partial-slip
nao contabilizado) => quantifica o gap. Verdict sec4.25 AS-IS.

Run: python -u New_Theory/loops_energy_confront.py
"""
from __future__ import annotations
import io
import glob
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)
from library_common import geometry_for, frozen_constants  # noqa: E402

LOOPS = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library" / "loops_csv"
PACK = dict(conform_driver="effective", slip_regime_mode="cattaneo_mindlin",
            slip_regime_sharpness=1.0, k_tr_mode="bending",
            loose_torsion_mode="bolt_torsion", eta_loose=15.0)
HDPE_CFG = dict(GA=8e4, c_bend=4.0, k_creep=1.0, floor=0.28, emb_um=2.0)
HDPE = {"t10": (25.0, 10250.0, 0.010), "t12": (29.0, 10250.0, 0.012)}


def loop_stats(f):
    xs, ys = [], []
    for ln in io.open(f, encoding="utf-8"):
        if ln.strip() and not ln.startswith(("#", "delta")):
            a, b = ln.split(",")[:2]
            xs.append(float(a)); ys.append(float(b))
    x, y = np.array(xs), np.array(ys)
    area = 0.5 * abs(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))
    return area, float(np.max(np.abs(y)))


def run_hdpe(t, n_max=400):
    grip, F0, t_m = HDPE[t]
    consts, _ = frozen_constants()
    geom = geometry_for("M12x1.75", grip)
    k_m = HDPE_CFG["GA"] / t_m
    I = np.pi * geom.d_2 ** 4 / 64
    k_ser = 1.0 / (1.0 / max(HDPE_CFG["c_bend"] * geom.E * I / geom.L_eff ** 3, 1.0) + 1.0 / k_m)
    F_eff = min(0.4 * F0, k_ser * 0.5e-3)
    mat = JointMaterial(emb_depth=HDPE_CFG["emb_um"] * 1e-6, mu_thread=0.15,
                        mu_bearing=0.15, k_j_init=2.0e7, k_member_shear=k_m,
                        k_creep_scale=HDPE_CFG["k_creep"], c_bend=HDPE_CFG["c_bend"],
                        loose_arrest_floor=HDPE_CFG["floor"],
                        **{k: v for k, v in PACK.items()}, **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    dW = np.empty(n_max + 1); dW[0] = 0.0
    Fsl = np.empty(n_max + 1); Fsl[0] = mat.mu_bearing * F0
    prev = 0.0
    for n in range(1, n_max + 1):
        ana.step_cycle(F_eff, np.pi / 2, 1.0, delta_amp=0.5e-3)
        tot = ana.energy.W_diss_total + ana.energy.W_damp_visc
        dW[n] = tot - prev; prev = tot
        Fsl[n] = min(mat.mu_bearing * max(ana.state.F_0, 0.0), F_eff)
    return dW, Fsl, F_eff


def run_steel_micro(delta_mm, n=10):
    consts, _ = frozen_constants()
    geom = geometry_for("M12x1.75", 29.0)
    mat = JointMaterial(emb_depth=1.5e-6, mu_thread=0.15, mu_bearing=0.15,
                        loose_arrest_floor=0.08, **PACK, **consts)
    F0 = 10e3
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    prev = 0.0; dws = []
    for _ in range(n):
        ana.step_cycle(0.4 * F0, np.pi / 2, 1.0, delta_amp=delta_mm * 1e-3)
        tot = ana.energy.W_diss_total + ana.energy.W_damp_visc
        dws.append(tot - prev); prev = tot
    return float(np.mean(dws[2:]))


def main():
    print("== HDPE: area medida vs dW/ciclo do modelo (config sec4.20) ==")
    g1_hits, g2_hits, seq = [], [], {}
    for f in sorted(glob.glob(str(LOOPS / "rousseau2025_loop_hdpe_*.csv"))):
        name = Path(f).stem
        t = "t10" if "_t10_" in name else "t12"
        nb = name.split("Nb")[1]
        n_mid = int(np.mean([int(v) for v in nb.split("-")]))
        area, peak = loop_stats(f)
        if t not in seq:
            seq[t] = run_hdpe(t)
        dW, Fsl, F_eff = seq[t]
        w = float(np.mean(dW[max(n_mid - 1, 1):n_mid + 2]))
        fs = float(Fsl[min(n_mid, len(Fsl) - 1)])
        fac = w / max(area, 1e-9)
        dfp = fs * 1e-3 / max(peak, 1e-9)
        g1_hits.append(0.5 <= fac <= 2.0)
        g2_hits.append(0.7 <= dfp <= 1.3)
        seq.setdefault(t + "_pairs", []).append((n_mid, area, w))
        print(f"  {t} N~{n_mid:3d}: area {area:6.2f} J vs modelo {w:6.2f} J (fator {fac:4.2f}) | "
              f"F_pico {peak:4.2f} kN vs F_transm {fs/1e3:4.2f} kN ({dfp:4.2f})")
    g3 = True
    for t in ("t10", "t12"):
        pairs = sorted(seq.get(t + "_pairs", []))
        if len(pairs) >= 3:
            a_first, w_first = pairs[0][1], pairs[0][2]
            a_last, w_last = pairs[-1][1], pairs[-1][2]
            mono_ok = (a_last < a_first) == (w_last < w_first)
            g3 = g3 and mono_ok
            print(f"  {t} evolucao: dado {a_first:.1f}->{a_last:.1f} J, modelo "
                  f"{w_first:.1f}->{w_last:.1f} J | mesma direcao: {mono_ok}")
    print("\n== ACO Fig10 (roller bearings, micro-amplitudes; hipotese: modelo ~0) ==")
    for f in sorted(glob.glob(str(LOOPS / "rousseau2025_loop_steel_amp*.csv"))):
        amp = float(Path(f).stem.split("amp")[1].replace("p", "."))
        area, peak = loop_stats(f)
        w = run_steel_micro(amp)
        print(f"  amp {amp:4.2f} mm: area medida {area:6.3f} J vs modelo {w:8.4f} J "
              f"| F_pico {peak:4.2f} kN")
    n1 = sum(g1_hits); n2 = sum(g2_hits)
    print(f"\nG-E1 fator-2 (HDPE): {n1}/{len(g1_hits)}")
    print(f"G-E2 pico +-30% (HDPE): {n2}/{len(g2_hits)}")
    print(f"G-E3 evolucao mesma direcao: {g3}")


if __name__ == "__main__":
    main()
