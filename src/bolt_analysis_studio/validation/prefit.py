# -*- coding: utf-8 -*-
"""Ajuste previo per-rig de casos do usuario (spec 2026-07-10 §3.1 — a doutrina
que a campanha legitimou, §4.42/L24): LE da propria curva o que e legivel
(emb_depth da queda inicial, loose_arrest_floor do plato final) e FITA apenas
c_bend (transversal; axial: nada). Resultado gravado no .bascase.json com
proveniencia por constante — refinar = editar/refitar esses campos."""
from __future__ import annotations

import json
from typing import Optional

import numpy as np

from ..calibration.provenance import (arrest_floor_from_curve,
                                      emb_depth_from_curve)
from .case_registry import CaseRecord
from .inputs import geometry_for_case, inputs_for, load_full_curve, repo_root
from .runner import _PACKS, simulate_case

_CBEND_GRID = [0.3, 1.0, 3.0, 10.0, 30.0, 50.0]


def _mae_with(rec: CaseRecord, overrides: dict, n_cap) -> float:
    rec.validation_case._prefit_overrides = overrides
    res = simulate_case(rec, n_cap=n_cap)
    return res.mae if (res.ok and res.mae is not None) else float("inf")


def prefit_user_case(rec: CaseRecord, n_cap: Optional[int] = None) -> dict:
    case = rec.validation_case
    inp = inputs_for(case)
    geom = geometry_for_case(case, grip_mm=inp["grip_mm"]["value"])
    try:
        rel = rec.csv_path.relative_to(repo_root()).as_posix()
    except ValueError:
        rel = str(rec.csv_path)
    cyc, ratio = load_full_curve(rel)
    F0 = case.initial_preload_N
    emb, emb_br = emb_depth_from_curve(cyc, ratio, F0, geom.k_b)
    floor, floor_br = arrest_floor_from_curve(ratio)
    prov = {"emb_depth": emb_br.get("provenance", "data_implied_early_drop"),
            "loose_arrest_floor": ("lido-do-dado (platô final)"
                                   if floor_br.get("plateau", True)
                                   else "lido-do-dado (LIMITE INFERIOR — "
                                        "curva termina em queda)")}
    if rec.family == "transverse":
        base = dict(_PACKS["LEGACY"])
        base.update(emb_depth=emb, loose_arrest_floor=floor)
        maes = {c: _mae_with(rec, dict(base, c_bend=c), n_cap)
                for c in _CBEND_GRID}
        best = min(maes, key=maes.get)
        # refino 1x entre vizinhos do grid (log)
        idx = _CBEND_GRID.index(best)
        lo = _CBEND_GRID[max(idx - 1, 0)]
        hi = _CBEND_GRID[min(idx + 1, len(_CBEND_GRID) - 1)]
        for c in np.geomspace(lo, hi, 5):
            m = _mae_with(rec, dict(base, c_bend=float(c)), n_cap)
            if m < maes[best]:
                maes[float(c)] = m
                best = float(c)
        overrides = dict(base, c_bend=float(best))
        mae = maes[best]
        prov["c_bend"] = "fitado-this-rig (unico DOF §4.42)"
    else:                                          # axial/creep: so leitura
        overrides = dict(emb_depth=emb)
        if floor_br.get("plateau", True) and floor > 0:
            overrides["loose_arrest_floor"] = floor
        mae = _mae_with(rec, overrides, n_cap)
    case._prefit_overrides = overrides
    block = {"overrides": {k: (float(v) if isinstance(v, (int, float)) else v)
                           for k, v in overrides.items()},
             "provenance": prov, "mae": (None if mae == float("inf") else mae)}
    # grava no JSON canonico do caso
    jp = rec.csv_path.with_name(rec.csv_path.name.replace(".csv", ".bascase.json"))
    if jp.exists():
        data = json.loads(jp.read_text(encoding="utf-8"))
        data["prefit"] = block
        jp.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                      encoding="utf-8")
    return block
