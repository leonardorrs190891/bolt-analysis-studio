# -*- coding: utf-8 -*-
"""F4 — G4-c (prereg-1/2): ZERO REGRESSAO fora das fontes tocadas.

Compara 8 controles simulados com o ENGINE PRE-F4 (main @5ec349c, src do
checkout principal) vs o ENGINE F4 (worktree), MESMOS adopted_configs (os
do worktree, sem sandbox — nenhum cfg novo existe fora do sandbox do
painel). PASS = mae/maxerr/final_pred IDENTICOS (==) nos 8.

Uso: python New_Theory/f4_g4c_controls.py --engine {pre|f4}
     (o orquestrador roda 2x, um por engine, e diffa os JSONs)
Saida: New_Theory/f4_g4c_<engine>.json
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

_WT = Path(r"C:\basl1v2")
_MAIN = Path(r"C:\Users\leo_r\OneDrive\BPL\Analitical\BAS_V2")

CONTROLES = [
    "liu2017_axial_F0_15kN",          # axial rig A (cfg LIU_2017_axial intocado)
    "liu2017_axial_F0_21kN",
    "li2022ti_axialmin_10Hz",         # rig B com per-rig F2-P2.1 adotado
    "li2022ti_axial_10Hz_full",       # com trim F3 adotado
    "liu2016wear_fig9a_m30nm",        # axial sem cfg adotado
    "liu2025_M16_amp0p3",             # transversal adotado (F3 fonte inteira)
    "liu2025_M16_amp0p6",
    "sun2025efa109235_transverse_nogrease_standard",  # transversal adotado F3
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["pre", "f4"], required=True)
    args = ap.parse_args()
    src = (_MAIN if args.engine == "pre" else _WT) / "src"
    sys.path.insert(0, str(src))
    import os
    # configs adotados: SEMPRE os do worktree (mesma base p/ os 2 engines)
    os.environ["BAS_ADOPTED_CONFIGS"] = str(_WT / "New_Theory/adopted_configs.json")
    # curvas/registry do worktree p/ os 2 lados (mesmos CSVs)
    os.chdir(_WT)
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    out = {}
    for cid in CONTROLES:
        r = simulate_case(record(cid), now="g4c")
        out[cid] = dict(mae=r.mae, maxerr=r.maxerr, final_pred=r.final_pred,
                        ok=r.ok, err=r.error)
        print(f"[{args.engine}] {cid}: mae={r.mae} maxerr={r.maxerr}",
              flush=True)
    p = _WT / f"New_Theory/f4_g4c_{args.engine}.json"
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"[{args.engine}] -> {p}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
