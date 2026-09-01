"""Liu2025: probe N_emb (timing do assentamento — licao do Lu sec4.19) + micro
grade {emb, W_onset, k_ratchet} em torno do incubation joint fit adotado.
Objetivo minimax na familia (7 casos); gate: nenhum piora >0.02, 3 acima do
limite (amp0p4 0.116, amp0p5 0.106, amp0p25 0.104) melhoram.
Run: python -u New_Theory/liu2025_nemb_probe.py > New_Theory/liu2025_nemb_probe.log 2>&1
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
import transfer_validation as tv  # noqa: E402
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)
from library_common import geometry_for, frozen_constants, load_full_curve  # noqa: E402

LEGACY = dict(conform_driver="effective", slip_regime_mode="cattaneo_mindlin",
              slip_regime_sharpness=1.0, k_tr_mode="bending",
              loose_torsion_mode="legacy", loose_arrest_floor=0.0)
BASE = dict(LEGACY, c_bend=50.0, delta_free=0.30e-3, k_wear_scale_tr=0.0,
            W_conf_ref=0.0, slip_onset_W=1.5e5, k_ratchet=1e-4)


def sim(case, kw):
    kw = dict(BASE, **kw)
    consts, _ = frozen_constants()
    for k in list(kw):
        if k in consts:
            consts[k] = kw.pop(k)      # override sem colisao (N_emb, W_conf_ref...)
    emb = kw.pop("emb_um")
    inp = tv.inputs_for(case)
    geom = geometry_for(case.bolt_size, grip_mm=inp["grip_mm"]["value"])
    mu = inp["mu"]["value"]
    mat = JointMaterial(emb_depth=emb * 1e-6, mu_thread=mu, mu_bearing=mu,
                        **kw, **consts)
    F0 = case.initial_preload_N
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    cyc, ratio = load_full_curve(case.reference_csv_path)
    keep = ratio >= tv.FLOOR_TRIM
    cyc_d = cyc[keep]
    n0, r_al = cyc_d[0], ratio[keep] / ratio[keep][0]
    n_max = int(cyc_d[-1])
    delta = case.transverse_displacement_mm * 1e-3
    F_amp = inp["F_amp_N"]["value"]
    r = np.empty(n_max + 1); r[0] = 1.0
    for n in range(1, n_max + 1):
        ana.step_cycle(F_amp, np.pi / 2, case.frequency_Hz, delta_amp=delta)
        r[n] = max(ana.state.F_0, 0.0) / F0
    r_alm = r / max(np.interp(n0, np.arange(n_max + 1), r), 1e-9)
    pred = np.interp(cyc_d, np.arange(n_max + 1), r_alm)
    return float(np.mean(np.abs(pred - r_al)))


def main():
    cases, _ = tv.select_cases()
    with open(ROOT / "New_Theory" / "report_data.json", encoding="utf-8") as fh:
        rd = json.load(fh)
    ents = {c["csv"]: c for c in rd["gallery"] if c["source"] == "LIU_2025"}
    by = {Path(c.reference_csv_path).stem: c for c in cases}
    stems = sorted(ents)
    print("casos:", stems, flush=True)
    old = {s: float(ents[s]["mae"]) for s in stems}

    best = None
    for N_emb in (5.0, 15.0, 50.0):
        for emb in (5.0, 7.0, 9.0):
            for W in (1.0e5, 1.5e5, 2.2e5):
                cfg = dict(emb_um=emb, N_emb=N_emb, slip_onset_W=W)
                maes = {s: sim(by[s], dict(cfg)) for s in stems}
                worse = [s for s in stems if maes[s] > old[s] + 0.02]
                key = (not worse, -max(maes.values()))
                print(f"N{N_emb:.0f} e{emb:.0f} W{W:.0e}: max {max(maes.values()):.3f} "
                      f"worse {len(worse)}", flush=True)
                if best is None or key > best[0]:
                    best = (key, cfg, maes, worse)
    key, cfg, maes, worse = best
    print(f"\nBEST {cfg}")
    for s in stems:
        print(f"  {s:26s} {maes[s]:.3f} (era {old[s]:.3f})")
    print(f"worse>0.02: {worse or 'nenhum'}  | acima de 0.100: "
          f"{[s for s in stems if maes[s] > 0.100]}")
    print("PARAMS_JSON:", json.dumps(cfg))


if __name__ == "__main__":
    main()
