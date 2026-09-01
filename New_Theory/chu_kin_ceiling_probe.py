# -*- coding: utf-8 -*-
"""Sonda CHU: loose_kin_ceiling (+ k_ratchet) — formas de FEEDBACK existentes.

Motivo: tres F1 analiticos no CHU (log-onset aditivo, troca de kernel,
dreno graduado aditivo) provaram que familias SUPERPONIVEIS nao fecham o
regime intermediario — o defeito e' de TRAJETORIA (N50 modelo 204 vs dado
737 no test2; frac2 0.27 vs 0.51-0.71). loose_kin_ceiling e' teto suave
sobre o drive de torque ("corrige o mid-over-loss, transicao GRADUAL em vez
de S abrupto", transferivel) e k_ratchet e' termo aditivo cinematico
back-loaded. Ambos default-inertes, ambos mudam o caminho de F0 (feedback)
=> so sim decide.

Grade 1-D em loose_kin_ceiling (varrendo ordens; comment do engine: O(1),
"caminho de slip por raio") + 2a passada opcional com k_ratchet pequeno.
Gates informais de sonda (nao e' prereg): nenhuma das 9 piora >+0.01;
conta quantas da fila-6 fecham. Saida: chu_kin_ceiling_probe.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.report_html as rh   # noqa: E402
import bolt_analysis_studio.validation.runner as rn        # noqa: E402
from bolt_analysis_studio.validation.case_registry import (  # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

_EXTRA: dict = {}
_orig = rn._effective_overrides
rn._effective_overrides = lambda rec, base: {**_orig(rec, base), **_EXTRA}


def _sim(cid, ov):
    _EXTRA.clear()
    _EXTRA.update(ov)
    try:
        return rn.simulate_case(record(cid))
    finally:
        _EXTRA.clear()


def main() -> int:
    st = ValidationStore()
    cids = sorted(r.case_id for r in all_records()
                  if r.source == "CHU_2026" and st.get(r.case_id) is not None)
    pares = [(r.source, st.get(r.case_id)) for r in all_records()
             if st.get(r.case_id) is not None]
    lim = rh.limite_sres("CHU_2026", rh._pisos_medidos(pares))
    antes = {c: st.get(c) for c in cids}
    fila = [c for c in cids
            if antes[c].resid_std > lim or antes[c].mae > rh.META_MAE
            or antes[c].maxerr > rh.META_MAX]
    print(f"CHU {len(cids)} curvas, fila {len(fila)}, lim_sd={lim:.4f}")

    out = {"lim_sd": lim, "pontos": []}
    CEILS = [0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 25.0]
    RATCH = [0.0, 0.01, 0.05]
    for kr in RATCH:
        for ceil in CEILS:
            ov = {"loose_kin_ceiling": ceil}
            if kr > 0.0:
                ov["k_ratchet"] = kr
            piora = 0
            fecha = 0
            row = {"ceil": ceil, "k_ratchet": kr, "curvas": {}}
            for cid in cids:
                r = _sim(cid, ov)
                b = antes[cid]
                w = (r.resid_std > b.resid_std + 0.01
                     or r.mae > b.mae + 0.01 or r.maxerr > b.maxerr + 0.01)
                piora += int(w)
                ok = (r.resid_std <= lim and r.mae <= rh.META_MAE
                      and r.maxerr <= rh.META_MAX)
                if cid in fila and ok:
                    fecha += 1
                row["curvas"][cid] = {"sd": r.resid_std, "mae": r.mae,
                                      "mx": r.maxerr, "piora": w, "ok": ok}
            row.update({"pioras": piora, "fila_fecha": fecha})
            out["pontos"].append(row)
            print(f"ceil={ceil:6.2f} kr={kr:5.3f}  pioras={piora}  "
                  f"fila fecha={fecha}/{len(fila)}  "
                  + " ".join(f"{row['curvas'][c]['sd']:.3f}" for c in fila))
    (ROOT / "New_Theory" / "chu_kin_ceiling_probe.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
