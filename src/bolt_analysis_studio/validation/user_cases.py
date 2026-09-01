# -*- coding: utf-8 -*-
"""Casos do usuario (.bascase.json, schema v1 — spec 2026-07-10 §4-5):
validacao com erros por campo, importacao (copia canonica em Models/USER_CASES/
+ CSV derivado da curva embutida) e records fonte 'USER' que entram no registry
e herdam TODO o pipeline (runner/report/browser/Abrir no Model)."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import List, Optional

import numpy as np

from ..core.validation_cases import ValidationCase
from .case_registry import CaseRecord
from .inputs import repo_root

USER_CASES_DIR = (Path(os.environ["BAS_USER_CASES_DIR"])
                  if os.environ.get("BAS_USER_CASES_DIR")
                  else repo_root() / "Models" / "USER_CASES")
_Y_UNITS = {"F_over_F0", "F_kN", "F_N"}
_X_UNITS = {"cycles", "minutes"}


class _UserSource:
    """Shim de ValidationSource p/ casos do usuario (evita tocar o enum)."""
    name = "USER"
    value = "User case"


def validate_bascase(data: dict) -> List[str]:
    errs: List[str] = []
    if data.get("bascase_version") != 1:
        errs.append("bascase_version: deve ser 1")
    if not (data.get("name") or "").strip():
        errs.append("name: obrigatório")
    t = data.get("test") or {}
    if not t.get("bolt_size") and not (t.get("bolt_diameter_mm") and t.get("pitch_mm")):
        errs.append("test.bolt_size OU (bolt_diameter_mm + pitch_mm): obrigatório")
    if not t.get("preload_N") and not t.get("preload_percent_yield"):
        errs.append("test.preload_N OU preload_percent_yield: obrigatório")
    lt = t.get("loading_type")
    if lt not in ("TRANSVERSE", "AXIAL"):
        errs.append("test.loading_type: TRANSVERSE ou AXIAL")
    cm = t.get("control_mode")
    if cm not in ("displacement", "force"):
        errs.append("test.control_mode: displacement ou force")
    if lt == "TRANSVERSE" and cm == "displacement" and not (
            t.get("delta_amplitude_mm") or 0) > 0:
        errs.append("test.delta_amplitude_mm: > 0 obrigatório em "
                    "TRANSVERSE/displacement")
    if cm == "force" and not (t.get("F_amplitude_N") or 0) > 0:
        errs.append("test.F_amplitude_N: > 0 obrigatório em control_mode=force")
    if not (t.get("frequency_Hz") or 0) > 0:
        errs.append("test.frequency_Hz: > 0 obrigatório")
    if not (t.get("n_cycles") or 0) > 0:
        errs.append("test.n_cycles: > 0 obrigatório")
    c = data.get("curve") or {}
    if c.get("x_unit") not in _X_UNITS:
        errs.append(f"curve.x_unit: um de {sorted(_X_UNITS)}")
    if c.get("y_unit") not in _Y_UNITS:
        errs.append(f"curve.y_unit: um de {sorted(_Y_UNITS)}")
    pts = c.get("points") or []
    if len(pts) < 4:
        errs.append("curve.points: mínimo 4 pontos")
    else:
        try:
            xs = [float(p[0]) for p in pts]
            ys = [float(p[1]) for p in pts]
            if any(b <= a for a, b in zip(xs, xs[1:])):
                errs.append("curve.points: x deve ser estritamente crescente")
            if c.get("y_unit") == "F_over_F0" and abs(ys[0] - 1.0) > 0.05:
                errs.append("curve.points: F_over_F0 deve começar ≈ 1.0")
            if min(ys) <= 0:
                errs.append("curve.points: y deve ser > 0")
        except (TypeError, ValueError, IndexError):
            errs.append("curve.points: pares numéricos [x, y]")
    return errs


def _slug(name: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_") or "caso_usuario"


def _normalize_curve(data: dict):
    c = data["curve"]
    t = data["test"]
    pts = np.asarray(c["points"], dtype=float)
    cyc, y = pts[:, 0], pts[:, 1]
    if c["y_unit"] == "F_kN":
        y = y * 1e3
    if c["y_unit"] in ("F_kN", "F_N"):
        F0 = float(t.get("preload_N") or y[0])
        ratio = y / max(F0, 1e-9)
    else:
        ratio = y
    freq = float(t["frequency_Hz"])
    if c["x_unit"] == "minutes":
        # regra dos casos de creep: 1 pseudo-ciclo = 1 min => freq = 1/60 Hz
        freq = 1.0 / 60.0
    return cyc, ratio / max(ratio[0], 1e-9), freq


def _build_case(data: dict, csv_rel: str, freq: float,
                final_ratio: float) -> ValidationCase:
    t = data["test"]
    d_mm = float(t.get("bolt_diameter_mm") or
                 t["bolt_size"].split("x")[0][1:])
    p_mm = float(t.get("pitch_mm") or t["bolt_size"].split("x")[1])
    bolt_size = t.get("bolt_size") or f"M{d_mm:g}x{p_mm:g}"
    F0 = float(t.get("preload_N") or 0.0)
    pct = float(t.get("preload_percent_yield") or 70.0)
    if F0 <= 0:            # so %yield: estima F0 ~ pct% * Sy(8.8) * A_s generica
        A_s_mm2 = np.pi / 4.0 * (d_mm - 0.9382 * p_mm) ** 2
        F0 = pct / 100.0 * 640e6 * A_s_mm2 * 1e-6
    delta = float(t.get("delta_amplitude_mm") or 0.0)
    case = ValidationCase(
        name=data["name"], description=data.get("description", ""),
        source=_UserSource(), reference=data.get("provenance", {}).get(
            "generated_by", "caso do usuário"),
        bolt_size=bolt_size, bolt_diameter_mm=d_mm, pitch_mm=p_mm,
        initial_preload_N=F0, preload_percent_yield=pct,
        transverse_displacement_mm=(delta if t["loading_type"] == "TRANSVERSE"
                                    else 0.0),
        frequency_Hz=freq, n_cycles=int(t["n_cycles"]),
        mu_initial=float(t.get("mu") or 0.15),
        lubricated=bool(t.get("lubricated") or False),
        expected_final_preload_ratio=final_ratio, expected_loosening_deg=0.0,
        notes=t.get("notes", ""), reference_csv_path=csv_rel)
    # inputs com proveniencia do usuario (hook do inputs_for)
    ui = {}
    if t.get("grip_mm"):
        ui["grip_mm"] = dict(value=float(t["grip_mm"]), prov="user")
    if t.get("mu"):
        ui["mu"] = dict(value=float(t["mu"]), prov="user")
    if t.get("rz_class"):
        ui["rz"] = dict(value=t["rz_class"], prov="user")
    if t.get("F_amplitude_N"):
        ui["F_amp_N"] = dict(value=float(t["F_amplitude_N"]), prov="user")
    case._user_inputs = ui
    case._prefit_overrides = dict((data.get("prefit") or {}).get("overrides", {}))
    case._bascase = data
    return case


def _record_from(data: dict, json_path: Path, csv_path: Path) -> CaseRecord:
    cyc, ratio, freq = _normalize_curve(data)
    try:
        rel = csv_path.relative_to(repo_root()).as_posix()
    except ValueError:
        rel = str(csv_path)
    case = _build_case(data, rel, freq, float(ratio[-1]))
    t = data["test"]
    fam = ("axial" if t["loading_type"] == "AXIAL"
           else "creep" if data["curve"]["x_unit"] == "minutes"
           else "transverse")
    return CaseRecord(
        case_id=json_path.stem.replace(".bascase", ""), name=data["name"],
        source="USER", family=fam, case_class="full_curve",
        caveats=[n for n in [t.get("notes") or ""] if n],
        validation_case=case, csv_path=csv_path,
        apparatus_note_path=None, gallery_entry=None)


def import_user_case(path, dest_dir: Optional[Path] = None) -> CaseRecord:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    errs = validate_bascase(data)
    if errs:
        raise ValueError("bascase inválido: " + "; ".join(errs))
    dest = Path(dest_dir) if dest_dir else USER_CASES_DIR
    dest.mkdir(parents=True, exist_ok=True)
    slug = _slug(data["name"])
    cyc, ratio, _ = _normalize_curve(data)
    csv_path = dest / f"{slug}.csv"
    csv_path.write_text("cycle,F_over_F0\n" + "\n".join(
        f"{x:g},{y:.6f}" for x, y in zip(cyc, ratio)), encoding="utf-8")
    json_path = dest / f"{slug}.bascase.json"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    from . import case_registry
    case_registry.refresh_records()
    return _record_from(data, json_path, csv_path)


def user_records(dest_dir: Optional[Path] = None) -> List[CaseRecord]:
    dest = Path(dest_dir) if dest_dir else USER_CASES_DIR
    out: List[CaseRecord] = []
    if not dest.exists():
        return out
    for jp in sorted(dest.glob("*.bascase.json")):
        try:
            data = json.loads(jp.read_text(encoding="utf-8"))
            if validate_bascase(data):
                continue                          # invalido: ignora no scan
            csv_path = jp.with_name(jp.name.replace(".bascase.json", ".csv"))
            if not csv_path.exists():
                continue
            out.append(_record_from(data, jp, csv_path))
        except (OSError, json.JSONDecodeError, ValueError):
            continue
    return out
