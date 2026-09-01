# -*- coding: utf-8 -*-
"""Ponte caso-de-validacao -> software (Plano B, requisito do professor
2026-07-10: "todos esses estudos devem estar disponiveis para ser rodados
livremente no software"). Monta o modelo MSD + carregamento + overrides de
material (_v2_tuner_overrides) E geometria (_v2_geometry_overrides) a partir
do MESMO caminho de inputs do runner — o Run reproduz o report e o usuario
edita livremente a partir dai. GUI-free (imports do wizard sao lazy)."""
from __future__ import annotations

from .case_registry import CaseRecord
from .inputs import geometry_for_case, inputs_for, repo_root
from .runner import _apply_adopted_geometry, loading_for, material_kwargs_for

# d_hole/d_washer (F1 2026-07-21): geometria adotada per-rig (kj_mode) — 0.0
# quando a fonte nao adota, e o solver_worker os ignora se ausentes do canal.
_GEOM_FIELDS = ("A_s", "L_eff", "d_2", "pitch", "r_bearing", "A_contact",
                "d_hole", "d_washer")


def geometry_overrides_for(rec: CaseRecord) -> dict:
    """Campos de JointGeometry (SI) com proveniencia do caso — o canal
    _v2_geometry_overrides do solver_worker (sem ele o Run usa L_eff=3d e
    A_contact=1e-4 fixos e nao reproduz o report)."""
    inp = inputs_for(rec.validation_case)
    g = geometry_for_case(rec.validation_case, grip_mm=inp["grip_mm"]["value"])
    g = _apply_adopted_geometry(g, rec.source, rec.case_id,
                                rec.validation_case.bolt_size)
    return {f: float(getattr(g, f)) for f in _GEOM_FIELDS}


def analysis_spec_for(rec: CaseRecord):
    """AnalysisSpec do wizard preenchido com o caso (build_model-ready)."""
    from ..gui.new_analysis_wizard import AnalysisSpec    # lazy: modulo puxa PyQt6
    case = rec.validation_case
    load = loading_for(rec)                               # ValueError p/ 'other'
    transverse = rec.family == "transverse"
    csv_rel = (rec.csv_path.relative_to(repo_root()).as_posix()
               if rec.csv_path is not None else "")
    return AnalysisSpec(
        project_name=f"Validation: {rec.case_id}",
        bolt_diameter_mm=float(case.bolt_diameter_mm),
        pitch_mm=float(case.pitch_mm),
        preload_pct_yield=float(case.preload_percent_yield),
        loading_type="TRANSVERSE" if transverse else "AXIAL",
        control_mode="displacement" if load["mode"] == "displacement" else "force",
        delta_amplitude_mm=float(load["delta_mm"]),
        F_amplitude_N=float(load["F_amp_N"]),
        frequency_hz=float(case.frequency_Hz),
        n_cycles=int(case.n_cycles),
        reference_csv_path=csv_rel,
    )


def build_case_model(rec: CaseRecord):
    """Modelo MSD completo do caso, pronto p/ o AppState: cadeia com GROUND
    (build_model), F0 do caso, ambos os canais de override anexados e a
    friccao nos dois niveis (regra Level-2/Level-3 do CLAUDE.md)."""
    from ..gui.new_analysis_wizard import build_model     # lazy
    spec = analysis_spec_for(rec)                         # ValueError p/ 'other'
    model = build_model(spec)
    case = rec.validation_case
    inp = inputs_for(case)
    model.global_loading.F_preload = float(case.initial_preload_N)
    mu = float(inp["mu"]["value"])
    model.mu_initial = mu                                 # Level-3 persistente
    model.global_loading.mu_initial = mu                  # Level-2 in-session
    model._v2_tuner_overrides = material_kwargs_for(rec, inp)
    model._v2_geometry_overrides = geometry_overrides_for(rec)
    return model
