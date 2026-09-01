# -*- coding: utf-8 -*-
"""G1 do prereg D-Q (2026-08-05) — transferencia CEGA da saturacao de flanco.

O `LIU_2016` tem o canal de flanco ATIVO (`flank_wear_on=1`, `flank_amp_exp=1.5`,
`k_wear_flank=4.325e-14`) e esta **14/14 no tripe**. Aplico a MESMA
`flank_fret_depth` que o LI_2022 pediu e pergunto se as 14 sobrevivem.

Por que e' o teste mais severo disponivel: as curvas do LIU_2016 correm ate
**1e6 e 5e6 ciclos** contra 200k-330k do LI_2022. A saturacao age sobre
profundidade ACUMULADA, logo corridas longas saturam MAIS. E varias estao
coladas nos limites (`fig9a_m40nm` MAE 0,0477 · `fig7_run1` sigma 0,0225).

Gates ESCRITOS no prereg, antes desta medicao:
  G1: as 14 permanecem no tripe. Uma que saia => FALSIFICADO (nao transfere).
  G2: nenhuma piora > +0,010 em qualquer perna.

    py -3.12 New_Theory/saturacao_flanco_g1.py --dep 3.5e-6 [--json out.json]

⚠️ O `n_max` NAO e' tocado: a comparacao usa o mesmo teto que o store (o
`_effective_overrides` so injeta o campo novo). Ver o gotcha do `n_cap` em
CLAUDE.md — sonda capada contra store integral e' maca-com-laranja.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.runner as rn               # noqa: E402
from bolt_analysis_studio.validation.case_registry import (       # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

FONTE = "LIU_2016"
_EXTRA: dict = {}
_orig = rn._effective_overrides


def _patched(rec, base):
    ov = _orig(rec, base)
    return {**ov, **_EXTRA} if _EXTRA else ov


rn._effective_overrides = _patched


def _tri(mae, mx, sd):
    return mae <= 0.05 and mx <= 0.10 and sd <= 0.025


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dep", type=float, required=True)
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    st = ValidationStore()
    cids = sorted(r.case_id for r in all_records() if r.source == FONTE)
    print(f"G1 CEGO — {len(cids)} curvas do {FONTE} com "
          f"flank_fret_depth = {a.dep:.3e} m ({a.dep*1e6:.2f} um)", flush=True)

    # instrumento: o campo TEM de chegar ao engine. Sem esta conferencia, um
    # Delta=0 em bloco se leria como "transfere" quando e' "nunca foi aplicado".
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
    assert "flank_fret_depth" in JointMaterial.__dataclass_fields__, "campo ausente"
    rec0 = record(cids[0])
    _EXTRA.clear(); _EXTRA["flank_fret_depth"] = a.dep
    ov = rn._effective_overrides(rec0, {})
    assert ov.get("flank_fret_depth") == a.dep, "override NAO chega ao runner"
    assert ov.get("flank_wear_on"), "canal de flanco DESLIGADO nesta fonte"
    print(f"  instrumento: OK (flank_wear_on={ov.get('flank_wear_on')}, "
          f"k_wear_flank={ov.get('k_wear_flank')})", flush=True)

    print(f"\n{'curva':38s} {'mae b':>7s} {'mae s':>7s} {'d mae':>7s} "
          f"{'sig b':>7s} {'sig s':>7s} {'mx s':>7s}  tripe", flush=True)
    linhas, saiu, pior = [], [], []
    for cid in cids:
        s = st.get(cid)
        _EXTRA.clear(); _EXTRA["flank_fret_depth"] = a.dep
        r = rn.simulate_case(record(cid))
        _EXTRA.clear()
        if not r.ok:
            print(f"  !! {cid}: {r.error}", flush=True)
            return 2
        tb, ta = _tri(s.mae, s.maxerr, s.resid_std), _tri(r.mae, r.maxerr, r.resid_std)
        dm = max(r.mae - s.mae, r.maxerr - s.maxerr, r.resid_std - s.resid_std)
        if tb and not ta:
            saiu.append(cid)
        if dm > 0.010:
            pior.append((cid, round(dm, 4)))
        marca = "<< SAIU" if (tb and not ta) else ("OK" if ta else "fora-antes")
        print(f"{cid[:38]:38s} {s.mae:7.4f} {r.mae:7.4f} {r.mae-s.mae:+7.4f} "
              f"{s.resid_std:7.4f} {r.resid_std:7.4f} {r.maxerr:7.4f}  {marca}",
              flush=True)
        linhas.append(dict(cid=cid, mae_b=s.mae, mae_s=r.mae, mx_b=s.maxerr,
                           mx_s=r.maxerr, sd_b=s.resid_std, sd_s=r.resid_std,
                           tripe_b=tb, tripe_s=ta, d_pior=dm))

    n_b = sum(1 for x in linhas if x["tripe_b"])
    n_s = sum(1 for x in linhas if x["tripe_s"])
    print(f"\n  tripe: {n_b}/{len(linhas)} -> {n_s}/{len(linhas)}", flush=True)
    print(f"  G1 (nenhuma sai):   {'PASSA' if not saiu else 'FALHA ' + str(saiu)}",
          flush=True)
    print(f"  G2 (nenhuma >+0,010): "
          f"{'PASSA' if not pior else 'FALHA ' + str(pior)}", flush=True)
    veredicto = "PASSA" if (not saiu and not pior) else "FALSIFICADO"
    print(f"  ==> G1+G2: {veredicto}", flush=True)
    if a.json:
        a.json.write_text(json.dumps(
            dict(dep=a.dep, fonte=FONTE, linhas=linhas, saiu=saiu, pior=pior,
                 tripe_base=n_b, tripe_sat=n_s, veredicto=veredicto),
            indent=1), encoding="utf-8")
        print(f"  json: {a.json}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
