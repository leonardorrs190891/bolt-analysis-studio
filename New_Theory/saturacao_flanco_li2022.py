# -*- coding: utf-8 -*-
"""Lado LI_2022 do prereg D-Q — G3 (ganho), G4 (nenhum pior) e G5 (fronteira).

O G1 (transferencia cega para o LIU_2016) decide SE a forma transfere; este
script mede o que ela faz na fonte ALVO, e em particular checa o G5: o otimo nao
pode estar no extremo da grade varrida.

    py -3.12 New_Theory/saturacao_flanco_li2022.py --deps 4e-5,1e-5,5e-6,3.5e-6,2.5e-6,2e-6,1.5e-6

⚠️ O `axialmin_10Hz` PIORA monotonicamente com a saturacao (declarado no prereg):
ele e' MAE-bound e precisa de MAIS perda, enquanto a `full` e' sigma-bound e
precisa de MENOS perda tardia. Duas curvas do MESMO ensaio com demandas OPOSTAS.
O G4 (+0,010) e' o que limita quao fundo se pode ir.
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

FONTE = "LI_2022_TRIBOINT"
_EXTRA: dict = {}
_orig = rn._effective_overrides


def _patched(rec, base):
    ov = _orig(rec, base)
    return {**ov, **_EXTRA} if _EXTRA else ov


rn._effective_overrides = _patched


def _tri(m, x, s):
    return m <= 0.05 and x <= 0.10 and s <= 0.025


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deps", default="4e-5,1e-5,5e-6,3.5e-6,2.5e-6,2e-6,1.5e-6")
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()
    deps = [float(x) for x in a.deps.split(",")]

    st = ValidationStore()
    cids = sorted(r.case_id for r in all_records() if r.source == FONTE)
    base = {c: st.get(c) for c in cids}
    print(f"{FONTE}: {len(cids)} curvas · grade {deps}")
    print(f"\n{'dep':>9s} " + " ".join(f"{c[9:26]:>20s}" for c in cids)
          + "   tripe  pior_d")
    print(f"{'base':>9s} " + " ".join(
        f"{base[c].mae:6.4f}/{base[c].resid_std:6.4f}".rjust(20) for c in cids)
        + f"   {sum(_tri(base[c].mae, base[c].maxerr, base[c].resid_std) for c in cids)}/4",
        flush=True)

    linhas = []
    for dep in deps:
        _EXTRA.clear(); _EXTRA["flank_fret_depth"] = dep
        row, ntri, pior = {}, 0, 0.0
        for c in cids:
            r = rn.simulate_case(record(c))
            if not r.ok:
                print(f"  !! {c}: {r.error}")
                return 2
            b = base[c]
            row[c] = (r.mae, r.maxerr, r.resid_std)
            ntri += _tri(*row[c])
            pior = max(pior, r.mae - b.mae, r.maxerr - b.maxerr,
                       r.resid_std - b.resid_std)
        print(f"{dep:9.2e} " + " ".join(
            f"{row[c][0]:6.4f}/{row[c][2]:6.4f}".rjust(20) for c in cids)
            + f"   {ntri}/4  {pior:+.4f}"
            + ("  << G4 VIOLA" if pior > 0.010 else ""), flush=True)
        linhas.append(dict(dep=dep, tripe=ntri, pior=pior,
                           por_curva={c: row[c] for c in cids}))
    _EXTRA.clear()

    # G5: o otimo (mais tripe, desempate por menor `pior`) e' interior?
    melhor = max(linhas, key=lambda L: (L["tripe"], -L["pior"]))
    viaveis = [L for L in linhas if L["pior"] <= 0.010]
    print(f"\nG5 fronteira: melhor celula dep={melhor['dep']:.2e} "
          f"(tripe {melhor['tripe']}/4, pior {melhor['pior']:+.4f})")
    print(f"  grade varrida: {min(deps):.2e} .. {max(deps):.2e}")
    print(f"  interior? {'SIM' if min(deps) < melhor['dep'] < max(deps) else 'NAO — ESTENDER'}")
    lista = ", ".join(f"{L['dep']:.1e}" for L in viaveis) or "nenhuma"
    print(f"  celulas que passam o G4 (pior <= +0,010): {lista}")
    # G3: o ganho declarado no prereg como CONHECIDO (nao como merito do gate)
    alvo = "li2022ti_axial_10Hz_full"
    print(f"\nG3 ganho (a `full` entra no tripe, sigma <= 0,025):")
    for L in linhas:
        s = L["por_curva"][alvo]
        print(f"  dep {L['dep']:9.2e}  full sigma {s[2]:.4f} "
              f"{'PASSA' if s[2] <= 0.025 else 'nao'}")
    if a.json:
        a.json.write_text(json.dumps(linhas, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
