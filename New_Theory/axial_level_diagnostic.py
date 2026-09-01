"""Diagnostico do ERRO DE NIVEL axial (systematic-debugging, spec 2026-07-06).

Responde a pergunta deixada em aberto no fim do 4.6 de MODEL_LEGITIMACY.md:
"por que o baseline sobre-afrouxa Liu2017 M12 — embedding/creep agressivos demais
nesse par? rigidez faltante?".

NAO adota nada (zero-refit continua sendo o baseline canonico). E um diagnostico:
decompoe a perda de preload axial por mecanismo e mede a alavanca dominante.

Achados (ver 4.6 addendum):
  A. A perda axial predita e ~90% EMBEDDING (creep ~8%; wear/loosening/fretting
     dormentes em axial puro forca — slip transversal=0, F_tr<T_resist).
  B. O embedding remove um valor ABSOLUTO fixo = k_b*emb_depth (indep. de F0 e
     A_F) => explica d/dA_F==0 e o sinal certo de d/dP0.
  C. Esse valor e ~4x grande demais p/ o par Liu2017: emb_depth VDI Rz<10 (9.5um)
     preve 25-36% de assentamento; o dado mostra 7-15% (=> emb_depth ~2-4um,
     ABAIXO da classe VDI mais fina). Reduzir emb (x0.25) leva as 3 curvas Liu ao
     gate SEM fretting. => proveniencia por-par de emb_depth, NAO forma faltante.
  D. Correcao k_reduced (VDI usa k_b*k_j/(k_b+k_j), engine usa k_b) so vale ~12%
     (k_j=4e9 >> k_b), entao NAO e o fix — mas e uma forma legitima (roadmap #10).
  E. fret=3 (o "gradient-match" do 4.6) e CATASTROFICO no run completo: dF0~F0*A_F
     colapsa F0->0. O k de nivel e ~60x menor e depende da contagem de ciclos =>
     fretting nao casa nivel+gradiente com um k unico (reforça "capacidade
     validada, nao fix").

Run:  python New_Theory/axial_level_diagnostic.py [--cap N]   (default cap 100000)
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
    frozen_constants, geometry_for, emb_depth_vdi, load_full_curve)

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"
CAP = int(sys.argv[sys.argv.index("--cap") + 1]) if "--cap" in sys.argv else 100_000

# (name, csv, F0, F_amp, bolt, grip_mm, freq)
CASES = [
    ("Liu2017 P0=15",  f"{DIG}/liu2017_axial_F0_15kN.csv", 15e3, 10e3, "M12x1.75", 30.0, 30.0),
    ("Liu2017 P0=18",  f"{DIG}/liu2017_axial_F0_18kN.csv", 18e3, 10e3, "M12x1.75", 30.0, 30.0),
    ("Liu2017 P0=21",  f"{DIG}/liu2017_axial_F0_21kN.csv", 21e3, 10e3, "M12x1.75", 30.0, 30.0),
    ("Liu2017 AF=12.5", f"{DIG}/liu2017_axial_AF_12p5kN.csv", 18e3, 12.5e3, "M12x1.75", 30.0, 30.0),
    ("Li2022ti 10Hz",  f"{DIG}/li2022ti_axialmin_10Hz.csv", 10e3, 10e3, "M10x1.5", 25.0, 10.0),
]


def _sim(F0, F_amp, bolt, grip, freq, n_run, f_emb=1.0, k_fret=0.0):
    consts, _ = frozen_constants()
    emb_m, _ = emb_depth_vdi("Rz<10", 1)
    geom = geometry_for(bolt, grip)
    mat = JointMaterial(emb_depth=emb_m * f_emb, mu_thread=0.15, mu_bearing=0.15,
                        k_thread_fret=k_fret, **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    sim = np.empty(n_run + 1); sim[0] = 1.0
    for n in range(1, n_run + 1):
        ana.step_cycle(F_amp, 0.0, freq)
        sim[n] = max(ana.state.F_0, 0.0) / F0
    return ana, geom, mat, sim


def _load(csv):
    cyc, r = load_full_curve(csv)
    keep = cyc <= CAP
    return cyc[keep], r[keep]


def part_A_decomposition():
    print("=" * 78)
    print("PART A - decomposicao da perda por mecanismo (axial forca, zero-refit)")
    print("=" * 78)
    for name, csv, F0, F_amp, bolt, grip, freq in CASES:
        cyc_d, r_d = _load(csv)
        n_run = int(cyc_d[-1])
        ana, geom, mat, sim = _sim(F0, F_amp, bolt, grip, freq, n_run)
        cum = {}
        for snap in ana.history:
            for m, dF in snap.dF_0_by_mech.items():
                cum[m] = cum.get(m, 0.0) + dF
        r_d_al = r_d / r_d[0]; n0 = cyc_d[0]
        pred = sim[-1] / max(np.interp(n0, np.arange(len(sim)), sim), 1e-9)
        # emb_depth que o dado implica: perda inicial rapida / k_b
        drop_early = 1.0 - (r_d[1] / r_d[0]) if len(r_d) > 1 else 0.0
        emb_needed_um = drop_early * F0 / geom.k_b * 1e6
        print(f"\n{name}: F0={F0/1e3:.0f}kN A_F={F_amp/1e3:.1f}kN {bolt} k_b={geom.k_b:.3e}")
        emb = cum.get("embedding", 0.0); tot = sum(cum.values())
        print(f"  embedding {emb:8.0f}N ({emb/F0*100:5.1f}%)  creep {cum.get('creep',0):7.0f}N "
              f"({cum.get('creep',0)/F0*100:.1f}%)  outros ~0")
        print(f"  emb frac do total de perda: {emb/tot*100:.0f}%   pred(norm)={pred:.3f} "
              f"data={r_d_al[-1]:.3f}")
        print(f"  emb_depth que o DADO implica (queda ate 2o ponto) ~ {emb_needed_um:.1f} um "
              f"(VDI Rz<10 = 9.5 um)")


def part_C_kreduced():
    print("\n" + "=" * 78)
    print("PART C - correcao k_reduced (VDI usa k_b*k_j/(k_b+k_j); engine usa k_b)")
    print("=" * 78)
    consts, _ = frozen_constants()
    k_j = JointMaterial(**consts).k_j_init
    for bolt, grip in [("M12x1.75", 30.0), ("M10x1.5", 25.0), ("M16x2.0", 40.0)]:
        kb = geometry_for(bolt, grip).k_b
        kr = kb * k_j / (kb + k_j)
        print(f"  {bolt:9s} k_b={kb:.3e}  k_j={k_j:.1e}  k_reduced={kr:.3e}  "
              f"k_reduced/k_b={kr/kb:.3f} (reducao {(1-kr/kb)*100:.0f}%)")


def part_B_matrix():
    print("\n" + "=" * 78)
    print(f"PART B - matriz emb_scale x k_thread_fret (MAE, cap={CAP})")
    print("=" * 78)
    combos = [("baseline", 1.0, 0.0), ("emb x0.25", 0.25, 0.0),
              ("fret=3 only", 1.0, 3.0), ("emb x0.25 + fret=3", 0.25, 3.0)]
    print(f"{'combo':22s}" + "".join(f"{c[0][:13]:>15s}" for c in CASES))
    for cname, f_emb, k_fret in combos:
        row = f"{cname:22s}"; maes = []
        for name, csv, F0, F_amp, bolt, grip, freq in CASES:
            cyc_d, r_d = _load(csv); n_run = int(cyc_d[-1])
            _, _, _, sim = _sim(F0, F_amp, bolt, grip, freq, n_run, f_emb, k_fret)
            r_d_al = r_d / r_d[0]; n0 = cyc_d[0]
            sim_al = sim / max(np.interp(n0, np.arange(len(sim)), sim), 1e-9)
            pred = np.interp(cyc_d, np.arange(len(sim)), sim_al)
            mae = float(np.mean(np.abs(pred - r_d_al))); maes.append(mae)
            row += f"  {mae:.3f}"
        row += f"  MED={np.median(maes):.3f}"
        print(row)


if __name__ == "__main__":
    print(f"cap={CAP}")
    part_A_decomposition()
    part_C_kreduced()
    part_B_matrix()
