"""Analise emb data-implicito (queda-inicial, sec4.40/L24) em TODAS as condicoes
axiais — Liu2017 (F0-sweep x5, AF-sweep x4) + Li2022ti (freq x3).

Para cada condicao: zero-refit em modo forca axial com (a) emb HANDBOOK (VDI
Rz<10) e (b) emb DATA-IMPLICITO da queda-inicial; MAE de cada; curvas para plot.
Escreve axial_emb_provenance.json (consumido pelo gerador de HTML).

Run: python New_Theory/axial_emb_provenance.py   (~5-8 min; Liu2017 = 1e6 ciclos)
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)
from library_common import (  # noqa: E402
    frozen_constants, geometry_for, emb_depth_vdi, emb_depth_from_curve,
    load_full_curve)

DIG = ROOT / "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"
# Cap de ciclos (padrao do harness axial estabelecido): cobre Li2022ti inteiro
# (200k) e a regiao informativa embedding+creep do Liu2017 (~2 decadas). Override
# via env EMB_CAP (ex.: 1000000 p/ a curva Liu2017 COMPLETA, incl. tail de creep).
CAP = int(os.environ.get("EMB_CAP", "200000"))
_TAG = "" if CAP == 200000 else f"_cap{CAP}"

# (nome, csv, F0_N, AF_N, bolt, grip_mm, freq_Hz, grupo)
CONDITIONS = [
    # Liu2017 F0-sweep (M12x1.75, AF=10kN, 30Hz)
    ("Liu2017 F0=15kN",   "liu2017_axial_F0_15kN.csv",   15e3, 10e3, "M12x1.75", 30.0, 30.0, "Liu2017 F0-sweep"),
    ("Liu2017 F0=16.5kN", "liu2017_axial_F0_16p5kN.csv", 16.5e3, 10e3, "M12x1.75", 30.0, 30.0, "Liu2017 F0-sweep"),
    ("Liu2017 F0=18kN",   "liu2017_axial_F0_18kN.csv",   18e3, 10e3, "M12x1.75", 30.0, 30.0, "Liu2017 F0-sweep"),
    ("Liu2017 F0=19.5kN", "liu2017_axial_F0_19p5kN.csv", 19.5e3, 10e3, "M12x1.75", 30.0, 30.0, "Liu2017 F0-sweep"),
    ("Liu2017 F0=21kN",   "liu2017_axial_F0_21kN.csv",   21e3, 10e3, "M12x1.75", 30.0, 30.0, "Liu2017 F0-sweep"),
    # Liu2017 AF-sweep (M12x1.75, F0=18kN, 30Hz)
    ("Liu2017 AF=7.5kN",  "liu2017_axial_AF_7p5kN.csv",  18e3, 7.5e3, "M12x1.75", 30.0, 30.0, "Liu2017 AF-sweep"),
    ("Liu2017 AF=8.75kN", "liu2017_axial_AF_8p75kN.csv", 18e3, 8.75e3, "M12x1.75", 30.0, 30.0, "Liu2017 AF-sweep"),
    ("Liu2017 AF=11.25kN","liu2017_axial_AF_11p25kN.csv",18e3, 11.25e3, "M12x1.75", 30.0, 30.0, "Liu2017 AF-sweep"),
    ("Liu2017 AF=12.5kN", "liu2017_axial_AF_12p5kN.csv", 18e3, 12.5e3, "M12x1.75", 30.0, 30.0, "Liu2017 AF-sweep"),
    # Li2022ti freq-sweep (M10x1.5, F0=10kN, AF=10kN)
    ("Li2022ti 10Hz",     "li2022ti_axialmin_10Hz.csv",  10e3, 10e3, "M10x1.5", 25.0, 10.0, "Li2022ti freq"),
    ("Li2022ti 15Hz",     "li2022ti_axialmin_15Hz.csv",  10e3, 10e3, "M10x1.5", 25.0, 15.0, "Li2022ti freq"),
    ("Li2022ti 20Hz",     "li2022ti_axialmin_20Hz.csv",  10e3, 10e3, "M10x1.5", 25.0, 20.0, "Li2022ti freq"),
]


def simulate(emb_m, F0, F_amp, bolt, grip, freq, sample_cyc, n_max):
    """Zero-refit em modo forca axial. Retorna model ratio nos ciclos sample_cyc
    (+ grade coarse p/ plot). Amostra durante o run (nao guarda 1e6 arrays)."""
    consts, _ = frozen_constants()
    geom = geometry_for(bolt, grip)
    mat = JointMaterial(emb_depth=emb_m, mu_thread=0.15, mu_bearing=0.15, **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    grid = sorted(set(int(c) for c in sample_cyc) |
                  set(int(x) for x in np.linspace(0, n_max, 120)))
    grid = [g for g in grid if 0 <= g <= n_max]
    gset = set(grid)
    out = {0: 1.0}
    for n in range(1, n_max + 1):
        ana.step_cycle(F_amp, 0.0, freq)
        if n in gset:
            out[n] = max(ana.state.F_0, 0.0) / F0
        ana.history.clear()          # engine so ESCREVE history; state basta (1e6 ciclos rapido)
    return grid, [out.get(g, out[max(k for k in out if k <= g)]) for g in grid]


def run():
    handbook_emb, _ = emb_depth_vdi("Rz<10", 1)     # 9.5 um p/ ambos os rigs
    results = []
    for (name, csv, F0, AF, bolt, grip, freq, group) in CONDITIONS:
        cyc, r = load_full_curve(str(DIG / csv))
        r = r / r[0]
        keep = cyc <= CAP                          # compara ate o cap (harness axial)
        cyc, r = cyc[keep], r[keep]
        n_max = int(cyc[-1])
        geom = geometry_for(bolt, grip)
        emb_data, prov = emb_depth_from_curve(cyc, r, F0, geom.k_b,
                                              early_index=1, vdi_ref_m=handbook_emb)
        print(f"[{name}] n_max={n_max} k_b={geom.k_b:.2e} "
              f"handbook={handbook_emb*1e6:.1f}um data-impl={emb_data*1e6:.2f}um "
              f"(razao {prov.get('ratio_data_over_handbook',0):.2f})", flush=True)
        entry = dict(name=name, group=group, F0_kN=F0/1e3, AF_kN=AF/1e3,
                     freq=freq, bolt=bolt, n_max=n_max,
                     emb_handbook_um=handbook_emb*1e6, emb_data_um=emb_data*1e6,
                     data=dict(x=cyc.tolist(), y=r.tolist()))
        for lbl, emb in (("handbook", handbook_emb), ("data_implied", emb_data)):
            gx, gy = simulate(emb, F0, AF, bolt, grip, freq, cyc, n_max)
            mi = np.interp(cyc, gx, gy)
            mae = float(np.mean(np.abs(mi - r)))
            entry[lbl] = dict(x=gx, y=gy, mae=mae,
                              err=[abs(float(a-b)) for a, b in zip(mi, r)])
            print(f"    {lbl:12s}: MAE={mae:.4f} fim={gy[-1]:.3f} (dado {r[-1]:.3f})", flush=True)
        results.append(entry)
    out = ROOT / f"New_Theory/axial_emb_provenance{_TAG}.json"
    out.write_text(json.dumps(results, ensure_ascii=False), encoding="utf-8")
    # sumario
    mh = np.mean([e["handbook"]["mae"] for e in results])
    md = np.mean([e["data_implied"]["mae"] for e in results])
    print(f"\n== SUMARIO {len(results)} condicoes ==", flush=True)
    print(f"  MAE medio handbook={mh:.4f}  data-implicito={md:.4f}  "
          f"melhora={100*(mh-md)/mh:.0f}%", flush=True)
    print(f"  escrito: {out}", flush=True)


if __name__ == "__main__":
    run()
