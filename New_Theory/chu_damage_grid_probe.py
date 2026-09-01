# -*- coding: utf-8 -*-
"""Grade da MAQUINA DE DANO no CHU_2026 — o carregador que faltava.

Cadeia de achados (2026-07-31): 3 F1 analiticos (familias superponiveis) +
teto cinematico INERTE (canal rotacional ~0) + relogio de dano sem
acoplamento inerte (erro meu: c_D sem k_dmg_*) => a sonda com ativacao
COMPLETA moveu: k_dmg_wear=4 leva test2 (D0.4) de sd 0.1897/fim 0.60 para
0.1077/0.16 (dado: 0.14) — o colapso profundo sustentado APARECE. test5
(D1.0) piora com a mesma dose (o fim 0.58 dele e' truncamento de
observacao a 319 ciclos, nao arresto fisico — mas a metrica so ve a
janela). test1 (D0.3) intocado (sub-slip, D nao cresce).

Esta grade mede a superficie (k_dmg_wear x k_dmg_mu x W_ref) nas 9 curvas
com o criterio de sonda usual (+0.01 por perna; conta fila-6). NAO e'
prereg — o ponto escolhido vai para prereg com holdout ANTES de adotar.

Saida: chu_damage_grid_probe.json
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
    melhor = None
    for W in (5000.0, 10000.0, 20000.0):
        for kw in (0.5, 1.0, 2.0, 3.0, 4.0, 6.0):
            for km in (0.0, -1.0, -2.43):
                ov = {"c_D": 5.5, "W_ref": W, "k_dmg_wear": kw}
                if km != 0.0:
                    ov["k_dmg_mu"] = km
                pior = []
                fecha = 0
                J = 0.0
                row = {"W_ref": W, "kw": kw, "km": km, "curvas": {}}
                for cid in cids:
                    r = _sim(cid, ov)
                    b = antes[cid]
                    w = (r.resid_std > b.resid_std + 0.01
                         or r.mae > b.mae + 0.01
                         or r.maxerr > b.maxerr + 0.01)
                    if w:
                        pior.append(cid)
                    ok = (r.resid_std <= lim and r.mae <= rh.META_MAE
                          and r.maxerr <= rh.META_MAX)
                    if cid in fila:
                        J += r.resid_std ** 2
                        if ok:
                            fecha += 1
                    row["curvas"][cid] = {"sd": r.resid_std, "mae": r.mae,
                                          "mx": r.maxerr, "fim": r.final_pred,
                                          "piora": w, "ok": ok}
                row.update({"pioras": pior, "fila_fecha": fecha, "J": J})
                out["pontos"].append(row)
                tag = "*" if not pior else " "
                print(f"W={W:6.0f} kw={kw:4.1f} km={km:5.2f} {tag} "
                      f"pioras={len(pior)} fecha={fecha}/{len(fila)} "
                      f"J={J:.4f}")
                if not pior and (melhor is None
                                 or (fecha, -J) > (melhor["fila_fecha"],
                                                   -melhor["J"])):
                    melhor = row
    out["melhor_viavel"] = melhor
    (ROOT / "New_Theory" / "chu_damage_grid_probe.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    if melhor:
        print(f"\nMELHOR VIAVEL: W={melhor['W_ref']:.0f} kw={melhor['kw']} "
              f"km={melhor['km']} fecha {melhor['fila_fecha']}/{len(fila)}")
        for cid, cc in melhor["curvas"].items():
            b = antes[cid]
            print(f"  {cid[:44]:44s} sd {b.resid_std:.4f}->{cc['sd']:.4f} "
                  f"fim {cc['fim']:.2f} {'ok' if cc['ok'] else ''}")
    else:
        print("\nNENHUM ponto viavel (toda dose quebra alguem) — registrar "
              "o trade e considerar W_ref/k por nivel de amplitude "
              "(exigiria ancora)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
