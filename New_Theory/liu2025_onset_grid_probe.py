# -*- coding: utf-8 -*-
"""Grade da INCUBACAO compartilhada no LIU_2025 — ultima classe existente
nao-varrida da fila.

Defeito (P5): N95 dispara 10-100x cedo em amplitude BAIXA => modelo colapsa
cedo => mae 1.5x/1.3x em amp0p25/amp0p3 (o nivel, nao o pico). A config ja
carrega slip_onset_W=250k compartilhado. O gate incuba sobre o TRABALHO
acumulado de slip, que escala forte com amplitude — subir W atrasa MUITO a
baixa e POUCO a alta (separacao natural). A pergunta da grade: existe dose
compartilhada (W, sharpness) que feche amp0p25/amp0p3/fig2 sem quebrar
amp0p4..amp0p8?

Cuidado de instrumento (licao CHU): mudar o relogio SEM conferir o
acoplamento e' sonda vazia — aqui o acoplamento ja' esta' ativo (gate
multiplica wear+loosening dF0; config usa o campo), entao a variacao de W e'
alavanca viva por construcao. Criterio de sonda: +0.01 por perna; conta
fila-4 (amp0p25, amp0p3, amp0p8, fig2_single).

Saida: liu2025_onset_grid_probe.json
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
                  if r.source == "LIU_2025" and st.get(r.case_id) is not None)
    pares = [(r.source, st.get(r.case_id)) for r in all_records()
             if st.get(r.case_id) is not None]
    lim = rh.limite_sres("LIU_2025", rh._pisos_medidos(pares))
    antes = {c: st.get(c) for c in cids}
    fila = [c for c in cids
            if antes[c].resid_std > lim or antes[c].mae > rh.META_MAE
            or antes[c].maxerr > rh.META_MAX]
    print(f"LIU_2025 {len(cids)} curvas, fila {len(fila)}: {fila}")
    print(f"lim_sd={lim:.4f}")

    out = {"lim_sd": lim, "pontos": []}
    melhor = None
    # W=250k e' o adotado (baseline); sharpness default da config (nao
    # listado => campo default 4). Varre W acima E abaixo + sharpness.
    for W in (150e3, 250e3, 400e3, 700e3, 1.2e6, 2.0e6):
        for sh in (4.0, 8.0):
            ov = {"slip_onset_W": float(W), "slip_onset_sharpness": sh}
            pior, fecha, J = [], 0, 0.0
            row = {"W": W, "sh": sh, "curvas": {}}
            for cid in cids:
                r = _sim(cid, ov)
                b = antes[cid]
                w = (r.resid_std > b.resid_std + 0.01
                     or r.mae > b.mae + 0.01
                     or r.maxerr > b.maxerr + 0.01)
                if w:
                    pior.append(cid.split("_")[-1])
                ok = (r.resid_std <= lim and r.mae <= rh.META_MAE
                      and r.maxerr <= rh.META_MAX)
                if cid in fila:
                    J += r.resid_std ** 2
                    if ok:
                        fecha += 1
                row["curvas"][cid] = {"sd": r.resid_std, "mae": r.mae,
                                      "mx": r.maxerr, "piora": w, "ok": ok}
            row.update({"pioras": pior, "fila_fecha": fecha, "J": J})
            out["pontos"].append(row)
            print(f"W={W/1e3:6.0f}k sh={sh:3.0f}  pioras={len(pior)}"
                  f"{pior}  fecha={fecha}/{len(fila)}  J={J:.4f}")
            if not pior and (melhor is None
                             or (fecha, -J) > (melhor["fila_fecha"],
                                               -melhor["J"])):
                melhor = row
    out["melhor_viavel"] = melhor
    (ROOT / "New_Theory" / "liu2025_onset_grid_probe.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    if melhor:
        print(f"\nMELHOR VIAVEL: W={melhor['W']/1e3:.0f}k sh={melhor['sh']} "
              f"fecha {melhor['fila_fecha']}/{len(fila)}")
        for cid, cc in melhor["curvas"].items():
            b = antes[cid]
            print(f"  {cid[:38]:38s} sd {b.resid_std:.4f}->{cc['sd']:.4f} "
                  f"mae {b.mae:.4f}->{cc['mae']:.4f} "
                  f"{'ok' if cc['ok'] else ''}")
    else:
        print("\nNENHUM ponto viavel — a separacao natural do gate nao basta;"
              " registrar e fechar a classe do LIU_2025 tambem")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
