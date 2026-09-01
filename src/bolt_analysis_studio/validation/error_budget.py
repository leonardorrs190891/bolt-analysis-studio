# -*- coding: utf-8 -*-
"""Orcamento de erro (MEM Etapa 1, spec 2026-07-10-model-evolution §3):
classifica cada caso por heuristicas AUDITAVEIS antes de qualquer mexida.
Rotulos: no_piso | gap_adocao | nivel | forma | sem_simulacao.
Campanhas LEEM este JSON p/ escolher a alavanca (hierarquia da Etapa 2)."""
from __future__ import annotations

import json
from typing import Optional

import numpy as np

from .case_registry import CaseRecord, all_records
from .inputs import inputs_for, repo_root
from .report_html import data_points, floor_of
from .runner import CaseResult
from .store import ValidationStore

BUDGET_PATH = (repo_root() / "Models" / "CALIBRATION_AND_VALIDATION"
               / "error_budget.json")
ALVO = 0.10          # alvo por caso quando nao ha piso medido (spec Etapa 4)


def classify_case(rec: CaseRecord, result: Optional[CaseResult]) -> dict:
    if result is None or not result.ok:
        return {"label": "sem_simulacao",
                "evidence": (result.error if result else "nunca simulado")}
    if result.mae is None:
        return {"label": "no_piso",
                "evidence": "sem curva (comparação pontual do ratio final)"}
    floor = floor_of(rec.source, rec.case_id)
    lim = max(floor + 0.02, ALVO)
    if result.mae <= lim:
        return {"label": "no_piso",
                "evidence": f"mae {result.mae:.3f} <= max(piso+0.02, {ALVO})={lim:.3f}"}
    sub = []
    try:
        n_assumed = sum(1 for v in inputs_for(rec.validation_case).values()
                        if v.get("prov") == "assumed")
        if n_assumed:
            sub.append(f"{n_assumed} inputs 'assumed' (µ domina o OAT §4.42)")
    except Exception:
        pass
    if rec.gallery_entry is not None:
        g = float(rec.gallery_entry["mae"])
        if result.mae > max(2 * g, g + 0.05):
            return {"label": "gap_adocao", "sublabels": sub,
                    "evidence": f"canônico {result.mae:.3f} vs campanha {g:.3f} "
                                f"({rec.gallery_entry.get('label', '')[:60]})"}
    # nivel vs forma: residuo de um sinal so => nivel (curva certa, deslocada)
    try:
        dx, dy = data_points(rec)
        mx = np.asarray(result.cycles, float)
        my = np.asarray(result.ratio, float)
        resid = np.interp(dx, mx, my) - np.asarray(dy)
        frac_over = float((resid > 0).mean())
        one_sided = frac_over > 0.8 or frac_over < 0.2
    except Exception:
        one_sided = abs((result.final_pred or 0) - (result.final_data or 0)) > 0.05
    label = "nivel" if one_sided else "forma"
    ev = ("resíduo de um sinal só (curva certa, nível errado — alavanca: "
          "constante/input per-rig)" if one_sided else
          "resíduo cruza zero (forma errada — candidato a falsificação)")
    return {"label": label, "sublabels": sub, "evidence": ev}


def error_budget(store: Optional[ValidationStore] = None) -> dict:
    store = store or ValidationStore()
    cases, by_source = {}, {}
    for rec in all_records():
        if rec.source == "USER":
            continue
        c = classify_case(rec, store.get(rec.case_id))
        cases[rec.case_id] = dict(c, source=rec.source, family=rec.family)
        by_source.setdefault(rec.source, {}).setdefault(c["label"], 0)
        by_source[rec.source][c["label"]] += 1
    totals = {"n": len(cases)}
    for c in cases.values():
        totals.setdefault(c["label"], 0)
        totals[c["label"]] += 1
    out = {"cases": cases, "by_source": by_source, "totals": totals}
    BUDGET_PATH.parent.mkdir(parents=True, exist_ok=True)
    BUDGET_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=1),
                           encoding="utf-8")
    return out


def main() -> int:
    out = error_budget()
    print(f"orçamento: {out['totals']}")
    for src, d in sorted(out["by_source"].items()):
        print(f"  {src:20s} {d}")
    print(f"gravado em {BUDGET_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
