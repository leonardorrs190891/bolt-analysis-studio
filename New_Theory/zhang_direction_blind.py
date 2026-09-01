"""PREDICAO CEGA — Zhang/Jiang 2006 varredura de DIRECAO 0-90 graus (5 curvas
digitalizadas, nunca usadas). Mesmo rig do grip-sweep sec4.22 => constantes JA
FITADAS (config adotada da galeria); ZERO constante nova. Varia apenas o eixo
de carga — primeira validacao do acoplamento transversal/axial misto.

PROTOCOLO PRE-REGISTRADO (declarado antes de computar qualquer erro):
- config: a adotada ZHANG_2006 (c_bend=4.0, k_ratchet=0.005, floor=0.05,
  frac=0, emb=0, N_emb 15; grip STANDARD 25.4mm — os ensaios de direcao usam
  o grip padrao do rig, F0=25kN, 5Hz).
- inputs por angulo a (medido DA transversal): theta_load = pi/2 - a;
  delta_amp = 0.46mm * cos(a) (componente transversal do curso imposto);
  F_amp = 0.4*F0 (total; o engine decompoe por seno/cosseno).
- GATES (fisica declarada, nao espiada): G-D1 ordem qualitativa — afrouxamento
  monotonicamente mais LENTO conforme a -> 90 (transversal e' o pior caso;
  fisica classica Junker, dita na nota do paper); G-D2 N50 do modelo dentro de
  fator 3 do dado nos angulos que colapsam; G-D3 MAE <= 0.15 por curva (dado
  APPROXIMATE de tabela). Adota na galeria (grupo ZHANG_2006) se G-D1 e G-D3.

Run: python -u New_Theory/zhang_direction_blind.py [--adopt]
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)
from library_common import geometry_for, frozen_constants, load_full_curve  # noqa: E402

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/extracted_csv"
PACK = dict(conform_driver="effective", slip_regime_mode="cattaneo_mindlin",
            slip_regime_sharpness=1.0, k_tr_mode="bending",
            loose_torsion_mode="bolt_torsion", eta_loose=15.0)
CFG = dict(c_bend=4.0, k_ratchet=0.005, loose_arrest_floor=0.05)
F0, DELTA0, FREQ, GRIP = 25e3, 0.46e-3, 5.0, 25.4
CASES = [  # (tag do csv, angulo da transversal em graus)
    ("Pure_transverse_0_from_transverse__6", 0.0),
    ("30_from_transverse__7", 30.0),
    ("45_from_transverse__8", 45.0),
    ("60_from_transverse__9", 60.0),
    ("Pure_axial_90_from_transverse__10", 90.0),
]


def sim(a_deg, n_max):
    consts, _ = frozen_constants()
    consts["N_emb"] = 15.0
    geom = geometry_for("M12x1.75", GRIP)
    mat = JointMaterial(emb_depth=0.0, mu_thread=0.15, mu_bearing=0.15,
                        **PACK, **CFG, **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    a = np.radians(a_deg)
    theta_load = np.pi / 2 - a
    delta = DELTA0 * np.cos(a)
    r = np.empty(n_max + 1); r[0] = 1.0
    for n in range(1, n_max + 1):
        ana.step_cycle(0.4 * F0, theta_load,
                       FREQ, delta_amp=(delta if delta > 1e-9 else None))
        r[n] = max(ana.state.F_0, 0.0) / F0
    return r


def n50(r):
    idx = np.argmax(r <= 0.5)
    return int(idx) if r[idx] <= 0.5 else 10 * len(r)


def main():
    adopt = "--adopt" in sys.argv
    rows = []
    for tag, a in CASES:
        cyc, rr = load_full_curve(
            f"{DIG}/03_Zhang_Jiang_2006_clamped_length__{tag}.csv")
        rr = rr / rr[0]
        n_max = int(cyc[-1])
        r = sim(a, n_max)
        pred = np.interp(cyc, np.arange(n_max + 1), r)
        mae = float(np.mean(np.abs(pred - rr)))
        rows.append((a, tag, mae, n50(r), n50(np.interp(
            np.arange(n_max + 1), cyc, rr)), cyc, rr, r, n_max))
        print(f"a={a:4.0f}deg  MAE {mae:.3f}  N50 mod {n50(r):5d}  "
              f"fim mod {r[-1]:.3f} dado {rr[-1]:.3f}")
    finals_mod = [r[7][-1] for r in rows]
    g1 = all(finals_mod[i] <= finals_mod[i + 1] + 0.02 for i in range(4))
    g2 = []
    for a, tag, mae, nm, nd, *_ in rows:
        if nd < 10 * 1000:
            fac = nm / max(nd, 1)
            g2.append(1 / 3 <= fac <= 3)
    g3 = all(r[2] <= 0.15 for r in rows)
    print(f"\nG-D1 retencao cresce com angulo->axial: {g1}  "
          f"(finais {['%.2f' % f for f in finals_mod]})")
    print(f"G-D2 N50 fator-3 (colapsantes): {g2}")
    print(f"G-D3 MAE<=0.15: {g3}  (max {max(r[2] for r in rows):.3f})")
    if adopt and g1 and g3:
        with open(ROOT / "New_Theory" / "report_data.json", encoding="utf-8") as fh:
            rd = json.load(fh)
        lab = ("PREDICAO CEGA direcao 0-90 (sec4.24): config do grip-sweep, zero "
               "constante nova; theta_load=pi/2-a, delta=0.46*cos(a)")
        for a, tag, mae, nm, nd, cyc, rr, r, n_max in rows:
            xs = np.unique(np.round(np.linspace(0, n_max, 120)).astype(int))
            rd["gallery"].append(dict(
                csv=f"zhang2006_M12_dir{int(a)}deg", source="ZHANG_2006",
                mae=mae, label=lab, amp_mm=round(DELTA0 * 1e3 * np.cos(np.radians(a)), 3),
                n_max=n_max,
                data={"x": [float(v) for v in cyc], "y": [round(float(v), 4) for v in rr]},
                model={"x": [int(v) for v in xs],
                       "y": [round(float(np.interp(v, np.arange(n_max + 1), r)), 5) for v in xs]}))
        (ROOT / "New_Theory" / "report_data.json").write_text(
            json.dumps(rd, indent=1, default=float), encoding="utf-8")
        print("ADOTADO: 5 casos de direcao no grupo ZHANG_2006.")
    elif adopt:
        print("NAO adotado (gate falhou) — registrar AS-IS.")


if __name__ == "__main__":
    main()
