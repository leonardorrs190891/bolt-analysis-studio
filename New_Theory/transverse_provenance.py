"""Analise de proveniencia do NIVEL transversal — biblioteca inteira (46 curvas,
7 fontes). Paralelo transversal do estudo axial emb-data-implicito (sec4.40).

Contraste: (a) NAIVE-FROZEN (config congelada compartilhada, c_bend=1.0, sem
per-rig, sem floor) vs (b) ADOTADO (per-rig: c_bend + floor-do-fim-do-dado),
lido do report_data.json (harness canonico, licao L1 — nunca reconstruir de
label). Escreve transverse_provenance.json (dado + naive + adotado + erros).

Diferenca-chave vs axial (sec4.40 fronteira): no transversal a queda-inicial e
loosening/creep (nao embedding), entao o emb-data-implicito NAO aplica; o nivel
transversal e c_bend (per-rig, fitado) + floor (data-do-fim, proveniencia
parcial). Este estudo QUANTIFICA quanto do nivel transversal e proveniencia
(floor) vs fit (c_bend).

Run: python New_Theory/transverse_provenance.py   (~2-4 min; curvas curtas)
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

import transfer_validation as tv  # noqa: E402
from frontier_polish import PACK  # noqa: E402
from library_common import (  # noqa: E402
    geometry_for, emb_depth_vdi, frozen_constants, load_full_curve)
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)

TR_SRC = {"LU_2024", "BAUER_2024", "ICMEZ_2025", "KARLSEN_2022",
          "LIU_2025", "ROUSSEAU_2025", "YANG_2019"}


def naive_curve(case):
    """Zero-refit NAIVE-FROZEN: config compartilhada, c_bend=1.0, sem per-rig."""
    consts, _ = frozen_constants()
    inp = tv.inputs_for(case)
    rz = inp["rz"]["value"]
    emb = emb_depth_vdi(rz, 1)[0] if isinstance(rz, str) and "Rz" in rz else 30e-6
    geom = geometry_for(case.bolt_size, grip_mm=inp["grip_mm"]["value"])
    mu = inp["mu"]["value"]
    mat = JointMaterial(emb_depth=emb, mu_thread=mu, mu_bearing=mu,
                        c_bend=1.0, **PACK, **consts)
    F0 = case.initial_preload_N
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    cyc, r = load_full_curve(case.reference_csv_path)
    r = r / r[0]
    n_max = int(cyc[-1])
    delta = case.transverse_displacement_mm * 1e-3
    F_amp = inp["F_amp_N"]["value"]
    grid = sorted(set(int(c) for c in cyc) |
                  set(int(x) for x in np.linspace(0, n_max, 90)))
    grid = [g for g in grid if 0 <= g <= n_max]
    gset = set(grid)
    out = {0: 1.0}
    for n in range(1, n_max + 1):
        ana.step_cycle(F_amp, np.pi / 2, case.frequency_Hz, delta_amp=delta)
        if n in gset:
            out[n] = max(ana.state.F_0, 0.0) / F0
        ana.history.clear()
    gy = [out.get(g, out[max(k for k in out if k <= g)]) for g in grid]
    mi = np.interp(cyc, grid, gy)
    mae = float(np.mean(np.abs(mi - r)))
    return dict(x=grid, y=gy, mae=mae), (cyc.tolist(), r.tolist())


def run():
    cases, _ = tv.select_cases()
    gallery = {os.path.basename(g.get("csv", "")): g
               for g in json.loads((ROOT / "New_Theory/report_data.json")
                                    .read_text(encoding="utf-8"))["gallery"]}
    results = []
    for c in cases:
        stem = os.path.basename(c.reference_csv_path)
        adopted = gallery.get(stem) or gallery.get(stem.replace(".csv", ""))
        if adopted is None:
            print(f"  [SKIP] sem adotado p/ {stem}", flush=True)
            continue
        naive, (dx, dy) = naive_curve(c)
        di = np.interp(dx, adopted["model"]["x"], adopted["model"]["y"])
        ni = np.interp(dx, naive["x"], naive["y"])
        entry = dict(
            name=c.source.name + " " + stem.replace(".csv", "")
                 .replace(c.source.name.lower().split("_")[0], "").strip("_"),
            source=c.source.name, csv=stem, n_max=int(dx[-1]),
            amp_mm=c.transverse_displacement_mm,
            data=dict(x=dx, y=dy),
            naive=dict(x=naive["x"], y=naive["y"], mae=naive["mae"]),
            adopted=dict(x=adopted["model"]["x"], y=adopted["model"]["y"],
                         mae=float(adopted["mae"]),
                         err=[abs(float(a - b)) for a, b in zip(di, dy)]))
        results.append(entry)
        print(f"[{entry['source']:14s}] {stem:32s} naive={naive['mae']:.3f} "
              f"adotado={adopted['mae']:.3f}", flush=True)
    out = ROOT / "New_Theory/transverse_provenance.json"
    out.write_text(json.dumps(results, ensure_ascii=False), encoding="utf-8")
    mn = np.mean([e["naive"]["mae"] for e in results])
    ma = np.mean([e["adopted"]["mae"] for e in results])
    print(f"\n== SUMARIO {len(results)} curvas transversais ==", flush=True)
    print(f"  MAE medio naive-frozen={mn:.3f}  adotado(per-rig)={ma:.3f}  "
          f"melhora={100*(mn-ma)/mn:.0f}%", flush=True)
    print(f"  escrito: {out}", flush=True)


if __name__ == "__main__":
    run()
