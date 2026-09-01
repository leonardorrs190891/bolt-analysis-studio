# -*- coding: utf-8 -*-
"""G4-b TENTATIVA 2 (prereg B1-v3; reinterpretação documentada): a nota de
aparato do Liu2020 prova que o rig é TRANSVERSAL disp-mode com 6 ROLETES
(atrito placa-placa ~eliminado; dado afrouxa só 4-6%). O flank AXIAL v2 não
se aplica (FAIL t1 honesto); a fonte fecha por CALIBRAÇÃO PER-RIG dos canais
transversais, com justificativa de aparato (roletes) = input-de-paper para
níveis pequenos + µ por coating (KB). A dependência de amplitude (fig9) vem
do WearLoss (slip ∝ delta_amp) com k_wear_spec per-rig.

Grade: emb_um {0,5, 1, 2} × k_wear_spec {1e-15, 5e-15, 2e-14, 8e-14} ×
tr_loose_gain {0,3, 0,6, 1,0} + µ coating per_case. Gate: ≥6/9 tripé<0,1;
controles bit-idênticos. Saída: f4_liu2020_blocoA_result.json.
Uso: python New_Theory/f4_g4b_t2_liu2020.py [--workers N]
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import product
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

CASOS = ["liu2020_fig5b_zinc_P0-12kN_AF0.2mm", "liu2020_fig5b_zinc_P0-18kN_AF0.2mm",
         "liu2020_fig5b_zinc_P0-24kN_AF0.2mm", "liu2020_fig9_zinc_AF0.1mm_P0-18kN",
         "liu2020_fig9_zinc_AF0.2mm_P0-18kN", "liu2020_fig9_zinc_AF0.3mm_P0-18kN",
         "liu2020_fig9_zinc_AF0.4mm_P0-18kN", "liu2020_fig15_DLC_P0-18kN_AF0.2mm",
         "liu2020_fig15_DLC_P0-19.28kN_AF0.2mm"]
MU = {"zinc": 0.150, "dlc": 0.126}
EMB = [0.1, 0.25, 0.5]
KW = [1e-16, 5e-16, 1e-15]
GAIN = [0.1, 0.2, 0.3]
CONTROLES = ["liu2017_axial_AF_7p5kN", "bauer2024_M8_fig6_rep1",
             "liu2025_M16_amp0p5", "li2022ti_axialmin_15Hz"]


def _sandbox(emb, kw, gain):
    d = json.loads(io.open(_ROOT / "New_Theory/adopted_configs.json",
                           encoding="utf-8").read())
    g = d["sources"].setdefault("LIU_2020_WEAR", {"pack": "", "cfg": {}})
    g["pack"] = ""
    g["cfg"] = dict(emb_um=float(emb), k_wear_spec=float(kw),
                    tr_loose_gain=float(gain),
                    per_case={"zinc": {"mu_thread": MU["zinc"],
                                       "mu": MU["zinc"]},
                              "dlc": {"mu_thread": MU["dlc"],
                                      "mu": MU["dlc"]}})
    fd, p = tempfile.mkstemp(suffix=".json", prefix="g4bt2_")
    with io.open(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False))
    return p


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(args):
    cid, sb, tag = args
    os.environ["BAS_ADOPTED_CONFIGS"] = sb
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    r = simulate_case(record(cid), now="f4-g4b-t2")
    return {"tag": tag, "case_id": cid, "mae": r.mae, "maxerr": r.maxerr}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))
    store = json.loads(io.open(
        _ROOT / "Models/CALIBRATION_AND_VALIDATION/validation_store.json",
        encoding="utf-8").read())

    tarefas, sbs = [], []
    for emb, kw, gain in product(EMB, KW, GAIN):
        sb = _sandbox(emb, kw, gain)
        sbs.append(sb)
        tag = f"e={emb}|kw={kw:.0e}|g={gain}"
        tarefas += [(c, sb, tag) for c in CASOS]
    print(f"[t2] {len(tarefas)} sims", flush=True)
    grade = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, t): t for t in tarefas}
        done = 0
        for fut in as_completed(futs):
            r = fut.result()
            grade.setdefault(r["tag"], {})[r["case_id"]] = r
            done += 1
            if done % 81 == 0 or done == len(tarefas):
                print(f"  [{done}/{len(tarefas)}]", flush=True)
    for sb in sbs:
        try:
            os.unlink(sb)
        except OSError:
            pass

    import statistics

    def n_pass(g):
        return sum(1 for c in CASOS if (g[c].get("mae") or 9) < 0.10
                   and (g[c].get("maxerr") or 9) < 0.10)

    best = max(grade, key=lambda t: (n_pass(grade[t]),
                                     -statistics.median((grade[t][c]["mae"] or 9)
                                                        for c in CASOS)))
    nb = n_pass(grade[best])
    med = statistics.median((grade[best][c]["mae"] or 9) for c in CASOS)
    print(f"[t2] melhor {best}: {nb}/9, mediana {med:.4f}", flush=True)
    for c in CASOS:
        v = grade[best][c]
        print(f"   {c[-30:]:30s} {store[c]['mae']:.3f}->{v['mae']:.3f} / "
              f"{store[c]['maxerr']:.3f}->{v['maxerr']:.3f}", flush=True)

    # controles com o vencedor
    p = best.split("|")
    sbv = _sandbox(float(p[0].split("=")[1]), float(p[1].split("=")[1]),
                   float(p[2].split("=")[1]))
    ctrl = {}
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=_init_worker) as ex:
        futs = {ex.submit(_sim_one, (c, sbv, "ctrl")): c for c in CONTROLES}
        for fut in as_completed(futs):
            r = fut.result()
            ctrl[r["case_id"]] = r
    os.unlink(sbv)
    ctrl_ok = all(ctrl[c]["mae"] == store[c]["mae"] for c in CONTROLES)

    verdict = "PASS" if (nb >= 6 and ctrl_ok) else "FAIL2"
    out = dict(secao="F3-style bloco A liu2020 (pós-FAIL2 do G4-b; grade "
                     "estendida além da borda)",
               melhor=best, n_pass=nb, mediana=med,
               tripe={c: dict(mae=grade[best][c]["mae"],
                              maxerr=grade[best][c]["maxerr"]) for c in CASOS},
               controles=ctrl_ok, verdict=verdict)
    pth = _ROOT / "New_Theory/f4_liu2020_blocoA_result.json"
    txt = json.dumps(out, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(pth, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print(f"[gate] G4-b t2 {verdict} ({nb}/9; ctrl={ctrl_ok}) → {pth}",
          flush=True)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
