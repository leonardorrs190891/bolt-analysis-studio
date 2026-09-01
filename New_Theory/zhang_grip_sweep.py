"""Zhang/Jiang 2006 — varredura de GRIP: *** DADO SINTETICO, NAO USAR ***

>>> ROTULO DE PROCEDENCIA (2026-07-28, item 9 da fila; expurgo autorizado) <<<
As 4 "curvas de grip" (l_c 12.7/25.4/38.1/50.8 mm) que este script gera NAO
sao rastreaveis ao PDF real do Zhang/Jiang 2006 — o artigo traz endurance S-N,
nao curvas F/F0-vs-ciclo por grip (DOI do database estava errado; corrigido na
nota de aparato). Elas foram EXPURGADAS da galeria antiga (report_data.json,
82->78 entradas) na mesma data. O canonico-203 sempre esteve limpo: so as 2
curvas REAIS digitalizadas (fig3, fig16) entram no store.
NAO re-adotar estas curvas nem usa-las para calibracao/gate. O script fica
apenas como registro historico da frota 2026-07-15.

(cabecalho original, para procedencia do que o script FAZIA:)
M12x1.75 10.9, membros AISI 1045, F0=25kN, delta=0.46mm, 5Hz. "Dado":
ciclos-ate-50% 15/65/175/350 = 23x — valores de TABELA aproximada, nao de
curva publicada. Gates da epoca: G-Z1 razao N50 em [10,50]; G-Z2 MAE<=0.15.

Run (historico): python -u New_Theory/zhang_grip_sweep.py [--adopt]
"""
from __future__ import annotations
import itertools
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
F0, DELTA, FREQ = 25e3, 0.46e-3, 5.0
GRIPS = [("l_c_12_7_mm_l_d_1_06_Short_grip__1", 12.7, 15),
         ("l_c_25_4_mm_l_d_2_12_Standard_grip__2", 25.4, 65),
         ("l_c_38_1_mm_l_d_3_18_Long_grip__3", 38.1, 175),
         ("l_c_50_8_mm_l_d_4_23_Extra_long_grip__4", 50.8, 350)]


def sim(grip_mm, kw, n_max):
    kw = dict(PACK, **kw)
    consts, _ = frozen_constants()
    for k in list(kw):
        if k in consts:
            consts[k] = kw.pop(k)
    emb = kw.pop("emb_um", 0.0)
    geom = geometry_for("M12x1.75", grip_mm)
    mat = JointMaterial(emb_depth=emb * 1e-6, mu_thread=0.15, mu_bearing=0.15,
                        **kw, **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    r = np.empty(n_max + 1); r[0] = 1.0
    for n in range(1, n_max + 1):
        ana.step_cycle(0.4 * F0, np.pi / 2, FREQ, delta_amp=DELTA)
        r[n] = max(ana.state.F_0, 0.0) / F0
    return r


def n50(r):
    idx = np.argmax(r <= 0.5)
    return int(idx) if r[idx] <= 0.5 else len(r)


def main():
    adopt = "--adopt" in sys.argv
    data = []
    for tag, g, n50_d in GRIPS:
        cyc, rr = load_full_curve(f"{DIG}/03_Zhang_Jiang_2006_clamped_length__{tag}.csv")
        data.append((tag, g, n50_d, cyc, rr / rr[0]))

    best = None
    for frac, cb, kr, fl in itertools.product(
            [0.0, 0.2], [4.0, 8.0, 12.0, 18.0], [0.005, 0.01, 0.02, 0.04], [0.0, 0.05]):
        cfg = dict(emb_load_frac=frac, N_emb=15.0, k_ratchet=kr,
                   loose_arrest_floor=fl, c_bend=cb, emb_um=0.0)
        maes, n50s = [], []
        for tag, g, n50_d, cyc, r_d in data:
            n_max = int(cyc[-1])
            r = sim(g, dict(cfg), n_max)
            maes.append(float(np.mean(np.abs(np.interp(cyc, np.arange(n_max + 1), r) - r_d))))
            n50s.append(max(n50(r), 1))
        ratio = n50s[-1] / n50s[0]
        key = (10.0 <= ratio <= 50.0 and max(maes) <= 0.15, -max(maes))
        if best is None or key > best[0]:
            best = (key, cfg, maes, n50s, ratio)
    key, cfg, maes, n50s, ratio = best
    print(f"BEST {cfg}")
    for (tag, g, n50_d, cyc, r_d), mae, n in zip(data, maes, n50s):
        print(f"  l_c={g:4.1f}mm  MAE {mae:.3f}  N50 mod {n:4d} vs dado {n50_d}")
    print(f"G-Z1 razao N50 {ratio:.1f} in [10,50] (dado 23.3): {10 <= ratio <= 50}")
    print(f"G-Z2 max MAE {max(maes):.3f} <= 0.15: {max(maes) <= 0.15}")

    if adopt and key[0]:
        with open(ROOT / "New_Theory" / "report_data.json", encoding="utf-8") as fh:
            rd = json.load(fh)
        lab = (f"grip-sweep novo (scout lit., sec4.22): c_bend={cfg['c_bend']} "
               f"ratchet={cfg['k_ratchet']} floor={cfg['loose_arrest_floor']} frac={cfg['emb_load_frac']}")
        for (tag, g, n50_d, cyc, r_d), mae in zip(data, maes):
            n_max = int(cyc[-1])
            r = sim(g, dict(cfg), n_max)
            xs = np.unique(np.round(np.linspace(0, n_max, 120)).astype(int))
            rd["gallery"].append(dict(
                csv=f"zhang2006_M12_lc{str(g).replace('.', 'p')}",
                source="ZHANG_2006", mae=mae, label=lab, amp_mm=0.46,
                n_max=n_max,
                data={"x": [float(v) for v in cyc], "y": [round(float(v), 4) for v in r_d]},
                model={"x": [int(v) for v in xs],
                       "y": [round(float(np.interp(v, np.arange(n_max + 1), r)), 5) for v in xs]}))
        (ROOT / "New_Theory" / "report_data.json").write_text(
            json.dumps(rd, indent=1, default=float), encoding="utf-8")
        print("ADOTADO: 4 casos ZHANG_2006 adicionados a galeria.")
    elif adopt:
        print("NAO adotado (gate falhou) — registrar AS-IS.")


if __name__ == "__main__":
    main()
