# -*- coding: utf-8 -*-
"""Verificacao da adocao D-Q — o config JA esta escrito; aqui NAO se escreve nada.

Duas perguntas, e a 1a nao e' formalidade:

 (1) a rota de OVERRIDE (com que os gates G1/G3/G4/G5 foram medidos) da o MESMO
     resultado que a rota de CONFIG ADOTADO? Se nao, os gates mediram outra coisa.
     Os numeros de referencia vem dos JSONs das varreduras, nao da memoria.
 (2) nenhuma curva saiu do tripe e nenhuma piorou > +0,010 (gate do prereg).

    py -3.12 New_Theory/saturacao_flanco_verifica.py --out saida.txt

⚠️ Sem pipe. A execucao anterior morreu num `| tail` com o config JA escrito —
o pipe bufferiza e o timeout mata sem deixar rastro do que faltava.
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
from bolt_analysis_studio.calibration import knowledge_base as kb  # noqa: E402

DEP = 2.5e-6
FONTES = ("LI_2022_TRIBOINT", "LIU_2016")


def _tri(m, x, s):
    return m <= 0.05 and x <= 0.10 and s <= 0.025


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", type=Path, help="JSON do G1 (override) p/ comparar")
    a = ap.parse_args()

    # (0) o config ADOTADO de fato carrega o valor, lido pelo kb
    for f in FONTES:
        v = (kb.adopted_config(f) or {}).get("cfg", {}).get("flank_fret_depth")
        print(f"kb.adopted_config({f}).cfg.flank_fret_depth = {v!r}", flush=True)
        if v != DEP:
            print("!! o kb NAO le o valor adotado — ABORTAR")
            return 2

    ref = {}
    if a.ref and a.ref.exists():
        for L in json.loads(a.ref.read_text(encoding="utf-8"))["linhas"]:
            ref[L["cid"]] = (L["mae_s"], L["mx_s"], L["sd_s"])

    st = ValidationStore()
    cids = sorted(r.case_id for r in all_records() if r.source in FONTES)
    print(f"\n{len(cids)} curvas · verificando rota CONFIG (sem override)\n", flush=True)
    print(f"{'curva':38s} {'mae b':>7s} {'mae a':>7s} {'d':>8s} {'sig b':>7s} "
          f"{'sig a':>7s} {'mx a':>7s} {'tripe':>10s} {'==override?':>12s}",
          flush=True)
    saiu, entrou, pior, divergiu = [], [], [], []
    for cid in cids:
        b = st.get(cid)
        r = rn.simulate_case(record(cid))
        if not r.ok:
            print(f"  !! {cid}: {r.error}", flush=True)
            return 2
        tb, ta = _tri(b.mae, b.maxerr, b.resid_std), _tri(r.mae, r.maxerr, r.resid_std)
        if tb and not ta:
            saiu.append(cid)
        if ta and not tb:
            entrou.append(cid)
        dm = max(r.mae - b.mae, r.maxerr - b.maxerr, r.resid_std - b.resid_std)
        if dm > 0.010:
            pior.append((cid, round(dm, 4)))
        marca = ""
        if cid in ref:
            d3 = max(abs(r.mae - ref[cid][0]), abs(r.maxerr - ref[cid][1]),
                     abs(r.resid_std - ref[cid][2]))
            marca = "identico" if d3 < 1e-12 else f"DIVERGE {d3:.2e}"
            if d3 >= 1e-12:
                divergiu.append((cid, d3))
        est = ("ENTROU" if (ta and not tb) else "SAIU" if (tb and not ta)
               else ("ok" if ta else "fora"))
        print(f"{cid[:38]:38s} {b.mae:7.4f} {r.mae:7.4f} {r.mae-b.mae:+8.4f} "
              f"{b.resid_std:7.4f} {r.resid_std:7.4f} {r.maxerr:7.4f} "
              f"{est:>10s} {marca:>12s}", flush=True)

    print(f"\n  entraram no tripe: {[c[-22:] for c in entrou] or 'nenhuma'}")
    print(f"  sairam:            {[c[-22:] for c in saiu] or 'nenhuma'}")
    print(f"  pior > +0,010:     {pior or 'nenhuma'}")
    print(f"  divergiu do override: {divergiu or 'nenhuma (rotas identicas)'}")
    ok = not saiu and not pior and not divergiu
    print(f"\n  ==> VERIFICACAO: {'PASSA' if ok else 'FALHA'}")
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
