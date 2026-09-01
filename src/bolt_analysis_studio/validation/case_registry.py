# -*- coding: utf-8 -*-
"""Registry unificado dos 128 casos de validacao (spec §3): ValidationCase +
classe do dado + paths (CSV, apparatus_notes, galeria). Leitura pura — quem
simula e' o runner; quem cacheia e' o store."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from ..core.validation_cases import ValidationCaseManager
from .inputs import repo_root

_AXIAL_SOURCES = {"LIU_2017_AXIAL", "LI_2022_TRIBOINT",
                  # Rodada 4 (2026-07-14): fontes 100% axiais
                  "LIU_2016", "GRZEJDA_2026", "YANG_2023_AME"}
# Rodada 4: relaxacao estatica (creep) — deteccao por FONTE (freq varia: dias/
# horas/segundos; a regra por-freq nao cobre qin com dt=1s)
_CREEP_SOURCES = {"JCSR_2023", "CACCESE_2009", "QIN_2024"}
_NOTES_DIR = "Models/CALIBRATION_AND_VALIDATION/curve_library/apparatus_notes"
_R4_NOTES = "BAS_V2_papers/E. Rodada 4 (deep-research 2026-07-11)/apparatus_notes"
_R5_NOTES = "BAS_V2_papers/F. Rodada 5 (limitacoes 2026-07-16)/apparatus_notes"
# fonte (enum ValidationSource) -> arquivo de nota de aparato (existentes no repo)
_SOURCE_NOTES = {
    "LIU_2025": "liu2025_scirep_M16.md", "BAUER_2024": "bauer2024_efa.md",
    "LU_2024": "lu2024_sensors_M8.md", "ICMEZ_2025": "demir2024_ejrnd_M8.md",
    "YANG_2019": "yang2019_sv_M10.md", "YANG_2021": "yang2021_sv_combined.md",
    "ROUSSEAU_2025": "rousseau2025_materials_M12.md",
    "KARLSEN_2022": "karlsen2022_M30M42.md", "SANDIA_2021": "sandia2021_cbeam.md",
    "LIU_2022_RETIGHT": "liu2022_istruc_retightening.md",
    "LIU_2017_AXIAL": "liu2017_triboint_axial.md",
    "LI_2022_MARSTRUC": "li2022_marstruc_contact_creep.md",
    "LI_2022_TRIBOINT": "li2022_triboint_axial_freq.md",
    "ZHANG_2006": "zhang2006.md",
    # 2026-07-28: era a MAIOR fonte sem nota (9 casos, 7 fora do tripe), e a
    # ausencia impedia a validacao de dominio (replica vs variante) da varredura
    # de impossibilidade. Escrita SEM o PDF (paywall Springer) a partir do
    # DEEP_RESEARCH_REPORT + companion OA + medicoes no store; o que exige o PDF
    # esta marcado FALTA na nota, nao inferido.
    "YANG_2023_IJPEM": "yang2023ijpem.md",
    # Rodada 4 (notas na pasta E — valor com "/" = caminho repo-relativo)
    "LIU_2016": f"{_R4_NOTES}/liu2016wear.md",
    "CHU_2026": f"{_R4_NOTES}/chu2026ti.md",
    "ECCLES_2010": f"{_R4_NOTES}/eccles2010.md",
    "YANG_2023_AME": f"{_R4_NOTES}/yang2023ame.md",
    "SUN_2025_CRIMP": f"{_R4_NOTES}/sun2025efa109235.md",
    "SUN_2025_REASSY": f"{_R4_NOTES}/sun2025efa110030.md",
    "GRZEJDA_2026": f"{_R4_NOTES}/grzejda2026mat.md",
    "JCSR_2023": f"{_R4_NOTES}/jcsr2023.md",
    "CACCESE_2009": f"{_R4_NOTES}/caccese2009.md",
    "QIN_2024": f"{_R4_NOTES}/qin2024acm.md",
    # Rodada 5 (2026-07-16/17, fatia 7 do plano L1-L7): pasta F ainda NAO
    # versionada no git (T11 ledger -- commit de wiring 9e3dd67 trouxe so o
    # codigo). zhang.md e' uma nota SO' -- cobre os dois papers-companion
    # Zhang2018 (Wear) + Zhang2019 (EFA), por isso os dois nomes de fonte
    # apontam p/ o mesmo arquivo. Degrada p/ None sem erro se a pasta
    # estiver ausente (mesmo padrao das notas R4 acima).
    "ZHANG_2018": f"{_R5_NOTES}/zhang.md",
    "ZHANG_2019": f"{_R5_NOTES}/zhang.md",
    "LIU_2020_WEAR": f"{_R5_NOTES}/liu2020.md",
}
# tokens de caveat (espelha exclusoes pre-registradas da campanha + notas)
_CAVEAT_TOKENS = {
    "hdpe": "par polimérico (HDPE) — fora do domínio metálico declarado",
    "vibralock": "dispositivo de travamento — out-of-model declarado",
    "varamp": "protocolo de amplitude variável",
    "fig2_single": "ensaio até fratura — cauda fora do afrouxamento puro",
    "full": "cauda com fratura por fadiga — trim recomendado",
    "creep": "creep estático (eixo x em MINUTOS; freq 1/60 Hz)",
}


@dataclass
class CaseRecord:
    case_id: str
    name: str
    source: str
    family: str                 # transverse | axial | creep | other
    case_class: str             # full_curve | final_ratio
    caveats: List[str]
    validation_case: object
    csv_path: Optional[Path]
    apparatus_note_path: Optional[Path]
    gallery_entry: Optional[dict]


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


@lru_cache(maxsize=1)
def _gallery_by_stem() -> Dict[str, dict]:
    p = repo_root() / "New_Theory" / "report_data.json"
    if not p.exists():
        return {}
    try:
        gal = json.loads(p.read_text(encoding="utf-8")).get("gallery", [])
    except (OSError, json.JSONDecodeError):
        return {}
    return {e["csv"]: e for e in gal}


def _build_record(case) -> CaseRecord:
    root = repo_root()
    rel = getattr(case, "reference_csv_path", "") or ""
    csv_path = (root / rel) if rel else None
    has_curve = csv_path is not None and csv_path.exists()
    stem = Path(rel).stem if rel else ""
    src = case.source.name
    if src in _AXIAL_SOURCES:
        fam = "axial"
    elif src in _CREEP_SOURCES:
        fam = "creep"
    elif "creep" in stem or (src == "LI_2022_MARSTRUC" and case.frequency_Hz < 0.05):
        fam = "creep"
    elif case.transverse_displacement_mm > 0:
        fam = "transverse"
    elif "axial" in stem.lower():
        # R4: fontes mistas (ex.: Sun crimp) — ramo axial identificado no stem.
        # Checado DEPOIS de amp>0: stems Eccles contem "axial" mas sao Junker
        # transversais (axial constante sobreposto = caveat, nao familia).
        fam = "axial"
    else:
        fam = "other"
    caveats = [msg for tok, msg in _CAVEAT_TOKENS.items() if tok in stem.lower()]
    note = _SOURCE_NOTES.get(src)
    # valores com "/" sao caminhos repo-relativos (notas R4 na pasta E)
    note_path = ((root / note) if "/" in note else (root / _NOTES_DIR / note)) if note else None
    if note_path is not None and not note_path.exists():
        note_path = None
    gal = _gallery_by_stem()
    # fallback de decimal: caso usa '16p5kN', galeria usou '16.5kN'
    entry = gal.get(stem) or gal.get(re.sub(r"(\d)p(\d)", r"\1.\2", stem))
    return CaseRecord(
        case_id=stem or _slug(case.name), name=case.name, source=src,
        family=fam, case_class="full_curve" if has_curve else "final_ratio",
        caveats=caveats, validation_case=case,
        csv_path=csv_path if has_curve else None,
        apparatus_note_path=note_path,
        gallery_entry=entry)


@lru_cache(maxsize=1)
def all_records() -> List[CaseRecord]:
    recs = [_build_record(c) for c in ValidationCaseManager.get_all_cases()]
    # Diretriz do professor (2026-07-11): o conjunto de validacao contem SO
    # casos comparaveis — remove os sem curva completa (final_ratio, 8
    # built-in legados) e os nao-simulaveis (familia 'other', 6 Sandia
    # modal). Os ValidationCase originais permanecem no core (V1 suite).
    recs = [r for r in recs
            if r.case_class == "full_curve" and r.family != "other"]
    seen: Dict[str, int] = {}
    for r in recs:                       # ids unicos (colisao improvavel, mas barata)
        if r.case_id in seen:
            seen[r.case_id] += 1
            r.case_id = f"{r.case_id}_{seen[r.case_id]}"
        else:
            seen[r.case_id] = 0
    from . import user_cases             # lazy: evita import circular
    return recs + user_cases.user_records()


def refresh_records() -> None:
    """Invalida o cache (novos casos do usuario aparecem no proximo all_records)."""
    all_records.cache_clear()


def record(case_id: str) -> Optional[CaseRecord]:
    return next((r for r in all_records() if r.case_id == case_id), None)
