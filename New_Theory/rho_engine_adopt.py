"""Verificacao ENGINE (regra do 1e6) + adocao na galeria da unificacao rho
(item 1, spec 2026-07-08). Roda DynamicStiffnessAnalyzer nos 9 casos Liu2017
axiais com S_rho substituindo emb_conform_exp (config G1: emb 4.30um, N_emb 15,
C_creep 1.450e-11, q_amp 2.375, rho_ref 0.667, creep_conform_exp 3.60 mantido).

Gates de adocao (pre-declarados):
  A1 engine~analitico: |final_engine - final_analitico| <= 0.01 em todos os casos
  A2 campanha: media da fonte melhora E nenhum caso piora > 0.02 vs galeria atual
So atualiza report_data.json se A1 E A2 passarem (guard no codigo).

Run: python -u New_Theory/rho_engine_adopt.py > New_Theory/rho_engine_adopt.log 2>&1
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
from library_common import geometry_for, load_full_curve  # noqa: E402
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)
from rho_unification import model_curve as analytic_curve  # noqa: E402

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"
GEOM = geometry_for("M12x1.75", 30.0)
P_REF = 15e3 / GEOM.A_contact
GF = dict(emb_depth=4.30e-6, N_emb=15.0, C_creep=1.450e-11,
          emb_amp_exp=2.375, rho_ref_emb=10.0 / 15.0,
          creep_conform_exp=3.60, p_ref_emb=P_REF)
FREQ, N_MAX = 30.0, 1_000_000
LABEL = ("rho-unification (item 1, sec4.18): S_rho=(rho/0.667)^2.375 substitui "
         "emb_conform_exp — P0 reparametrizacao exata, A_F zero-extra-fit")

CASES = [  # (csv_key na galeria, arquivo, F0, A_F)
    ("liu2017_axial_F0_15kN",   "liu2017_axial_F0_15kN",   15e3,   10e3),
    ("liu2017_axial_F0_16.5kN", "liu2017_axial_F0_16p5kN", 16.5e3, 10e3),
    ("liu2017_axial_F0_18kN",   "liu2017_axial_F0_18kN",   18e3,   10e3),
    ("liu2017_axial_F0_19.5kN", "liu2017_axial_F0_19p5kN", 19.5e3, 10e3),
    ("liu2017_axial_F0_21kN",   "liu2017_axial_F0_21kN",   21e3,   10e3),
    ("liu2017_axial_AF_7p5kN",  "liu2017_axial_AF_7p5kN",  18e3,   7.5e3),
    ("liu2017_axial_AF_8p75kN", "liu2017_axial_AF_8p75kN", 18e3,   8.75e3),
    ("liu2017_axial_AF_11p25kN", "liu2017_axial_AF_11p25kN", 18e3, 11.25e3),
    ("liu2017_axial_AF_12p5kN", "liu2017_axial_AF_12p5kN", 18e3,   12.5e3),
]


def run_engine(F0, A_F):
    mat = JointMaterial(**GF)
    ana = DynamicStiffnessAnalyzer(GEOM, mat, F0)
    grid = np.unique(np.concatenate([[0], np.linspace(0, N_MAX, 121)])).astype(int)
    xs, ys = [0], [1.0]
    nxt, gi = grid[1], 1
    for n in range(1, N_MAX + 1):
        ana.step_cycle(A_F, 0.0, FREQ)
        if n >= nxt:
            xs.append(n); ys.append(ana.state.F_0 / F0)
            gi += 1
            nxt = grid[gi] if gi < len(grid) else N_MAX + 1
    return np.array(xs, float), np.array(ys, float)


def main():
    with open(ROOT / "New_Theory" / "report_data.json", encoding="utf-8") as fh:
        rd = json.load(fh)
    by_csv = {c["csv"]: c for c in rd["gallery"]}

    rows, a1_fail, worse = [], [], []
    for key, fname, F0, A_F in CASES:
        cyc, r = load_full_curve(f"{DIG}/{fname}.csv")
        r = r / r[0]
        mx, my = run_engine(F0, A_F)
        pred_d = np.interp(cyc, mx, my)
        mae = float(np.mean(np.abs(pred_d - r)))
        ana_fin = float(analytic_curve(F0, A_F, cyc[1:], 4.30e-6, 15.0,
                                       1.450e-11, 2.375, 3.60)[-1])
        d_ana = abs(float(my[-1]) - ana_fin)
        old = float(by_csv[key]["mae"]) if key in by_csv else float("nan")
        rows.append((key, F0, A_F, mae, old, float(my[-1]), ana_fin, d_ana, mx, my))
        if d_ana > 0.01:
            a1_fail.append(key)
        if key in by_csv and mae > old + 0.02:
            worse.append(key)
        print(f"{key:28s} MAE {mae:.4f} (era {old:.4f})  fin_eng {my[-1]:.3f} "
              f"fin_ana {ana_fin:.3f} d={d_ana:.4f}", flush=True)

    new_mean = float(np.mean([r[3] for r in rows]))
    old_mean = float(np.mean([r[4] for r in rows]))
    a1 = not a1_fail
    a2 = (new_mean < old_mean) and not worse
    print(f"\nfonte Liu2017 (9 casos): media {old_mean:.4f} -> {new_mean:.4f}")
    print(f"A1 engine~analitico (<=0.01): {'PASS' if a1 else 'FAIL ' + str(a1_fail)}")
    print(f"A2 campanha (melhora, nenhum piora>0.02): {'PASS' if a2 else 'FAIL ' + str(worse)}")

    if a1 and a2:
        for key, F0, A_F, mae, old, fin, afin, dana, mx, my in rows:
            e = by_csv[key]
            e["model"] = {"x": [int(v) for v in mx], "y": [round(float(v), 5) for v in my]}
            e["mae"] = mae
            e["label"] = LABEL
        out = ROOT / "New_Theory" / "report_data.json"
        out.write_text(json.dumps(rd, indent=1, default=float), encoding="utf-8")
        print("ADOTADO: report_data.json atualizado (9 entradas Liu2017).")
    else:
        print("NAO adotado (gate falhou) — galeria intocada; registrar AS-IS.")


if __name__ == "__main__":
    main()
