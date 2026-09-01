# -*- coding: utf-8 -*-
"""Congela a LINHA DE BASE contra a qual a parada foi medida.

A regra de parada (`regra_de_parada_proposta.md`) diz que a parada é
**provisória** e reabre automaticamente se:

  · o `engine_fingerprint` mudar
  · um instrumento novo mudar a decomposição
  · o `n` ou o piso de qualquer curva da fila mudar (dado novo)
  · a régua mudar

⚠️ **Isso é prosa, e prosa não reabre nada.** Sem gravar contra QUE estado a
parada foi medida, "reabre automaticamente" não tem sujeito — e a §4.43 da
campanha existe precisamente porque afirmação sem âncora envelhece calada.

Este script grava o estado; `tests/test_parada_reabre_quando_deve.py` o cobra.

    py -3.12 New_Theory/parada_baseline.py            # imprime
    py -3.12 New_Theory/parada_baseline.py --gravar   # escreve o JSON
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

from bolt_analysis_studio.validation import report_html as rh              # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records      # noqa: E402
from bolt_analysis_studio.validation.runner import CaseResult              # noqa: E402
import regra_de_parada_triagem as T                                       # noqa: E402

ALVO = ROOT / "New_Theory" / "parada_baseline.json"
STORE = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"


def medir() -> dict:
    recs = {r.case_id: r for r in all_records()}
    store = json.loads(STORE.read_text(encoding="utf-8"))
    store = store.get("cases", store)
    pisos = T.pisos_medidos(store, recs)
    fps = sorted({v.get("engine_fingerprint") for v in store.values()})

    fila, tripe, comp = {}, 0, 0
    for cid, raw in store.items():
        rec = recs.get(cid)
        if rec is None or not rh.caso_comparavel(rec.source, cid):
            continue
        r = CaseResult.from_dict(raw)
        if not r.ok:
            continue
        comp += 1
        sd = rh.sres_para_censo(r)
        lim = rh.limite_sres(rec.source, pisos)
        if sd is not None and r.maxerr <= rh.META_MAX and r.mae <= rh.META_MAE and sd <= lim:
            tripe += 1
            continue
        if cid in rh._EXCECOES or cid in rh._DECLARADAS:
            continue
        # FILA JULGAVEL = aberta cuja fonte TEM piso medido. As sem piso ficam
        # fora por decisao da propria regra ("indecidivel, acao nomeada").
        if T.piso_da_fonte(pisos, rec.source) is None:
            continue
        fila[cid] = {
            "n_pontos": len(r.metric_x or []),
            "piso_fonte": round(T.piso_da_fonte(pisos, rec.source), 6),
            "limite_sigma": round(lim, 6),
            "pior_perna": round(max(r.mae / rh.META_MAE, r.maxerr / rh.META_MAX,
                                    (sd / lim) if sd else 9.0), 4),
        }
    return {
        "medido_em": "2026-08-16",
        "documento": "New_Theory/regra_de_parada_medida_2026-08-16.md",
        "reexaminado_em": None,      # preencher ao reconhecer uma reabertura
        "fingerprint": fps,
        "regua": {"META_MAE": rh.META_MAE, "META_MAX": rh.META_MAX,
                  "META_SRES": rh.META_SRES,
                  "_SRES_POR_FONTE": bool(rh._SRES_POR_FONTE)},
        "censo": {"tripe": tripe, "comparaveis": comp},
        "fila_julgavel": fila,
    }


if __name__ == "__main__":
    d = medir()
    print(json.dumps(d, indent=1, ensure_ascii=False))
    if "--gravar" in sys.argv:
        ALVO.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8", newline="")
        print(f"\ngravado: {ALVO}")
