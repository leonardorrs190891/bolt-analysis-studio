# -*- coding: utf-8 -*-
"""PREMEASURE da correcao de base da `run2p2` — o que ainda NAO e' prereg.

## O defeito (medido, duas extracoes independentes)

A CSV da `run2p2`, multiplicada pelo F0=312 do registry, da valores REDONDOS —
300 / 250 / 200 / 150 / 90 / 38 kN. Ou seja: o digitalizador leu **cruzamentos
de linha de grade** e ANCOROU o ciclo 1 no F0 **nominal** do registry, em vez
de ler o valor da figura.

Na Fig. 10 a curva laranja no ciclo 1 esta em:

    subagente D-X (raster, atribuicao por swatch)   332,7 kN
    esta sessao   (topo do traco, x=127)            332,0 kN
    idem, corrigida pelo vies dos CONTROLES         329,3 kN

Controles medidos na MESMA coluna x (o que prova que ela e' o ciclo 1):
`run7.1` figura 313,15 vs registry 312 (+0,4 %) · `run6.2` 339,39 vs 340
(-0,2 %). Calibracao y: 17 gridlines, residuo max **0,48 kN**.

⇒ base verdadeira em **329-333 kN** contra **312** no registry: **+5,5 a +6,6 %**.

## A transformacao (e por que ela nao precisa de re-extracao)

O ciclo em que a curva cruza um nivel de kN **nao depende do F0 assumido**.
Logo os 6 pontos do meio ja sao leituras validas e so o DIVISOR muda:

    novo_ratio(ciclo 1) = 1,0                    (por definicao)
    novo_ratio(demais)  = antigo x (312 / base)

⚠️ Isto e' importante porque a extracao desta sessao **nao consegue** re-ler o
meio da curva: pixels AMARELOS anti-serrilhados (run 6.2 misturado com branco)
caem mais perto do laranja que do amarelo puro e contaminam o traco (numa
coluna aparecem 223 kN e 123 kN juntos). Instrumento declarado insuficiente
para o meio — e desnecessario para esta correcao.

## O que este script mede

Grade (base x k_ratchet). A hipotese de PARCIMONIA registrada em
`karlsen_run2p2_sonda_resultado.md`: corrigida a base, o `k_ratchet` que a
curva pede SOBE rumo aos **0,005** da `run7p1` — se convergir, as duas
compartilham UM valor e a excecao per-especime vira excecao de CLASSE.

Nao adota, nao escreve config, nao toca o store.

    py -3.12 New_Theory/karlsen_run2p2_premeasure.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.inputs as vin                # noqa: E402
import bolt_analysis_studio.validation.runner as rn                 # noqa: E402
from bolt_analysis_studio.validation.case_registry import record     # noqa: E402

CID = "karlsen2022_M30_HV_run2p2"
CSV_TOKEN = "karlsen2022_M30_HV_run2p2.csv"
F0_REG = 312.0

_BASE = {"v": None}
_KR = {"v": None}
_orig_load = vin.load_full_curve
_orig_ov = rn._effective_overrides


def _load(rel):
    cyc, rat = _orig_load(rel)
    if _BASE["v"] and CSV_TOKEN in str(rel):
        rat = np.asarray(rat, float).copy()
        rat[1:] *= F0_REG / _BASE["v"]        # ponto 1 fica 1,0 por definicao
    return cyc, rat


def _ov(rec, base):
    o = dict(_orig_ov(rec, base))
    if _KR["v"] is not None:
        o["k_ratchet"] = _KR["v"]
    return o


vin.load_full_curve = _load
rn.load_full_curve = _load
rn._effective_overrides = _ov


def _lim_sres() -> float:
    """Limite da 3a perna DESTA fonte — nunca o global.

    ⚠️ A 1a versao deste script deixou `0.025` fixo e imprimiu "nenhuma celula
    passa" quando OITO passavam: o KARLSEN tem piso medido e `limite_sres` da
    **0,0845**. Mesma armadilha que a triagem sofreu em 2026-07-30 — a regra do
    limite se PERGUNTA ao helper, nunca se reimplementa.
    """
    import json as _j

    from bolt_analysis_studio.validation import report_html as rh
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.runner import CaseResult
    S = _j.loads((ROOT / "Models" / "CALIBRATION_AND_VALIDATION"
                  / "validation_store.json").read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    pares = [(recs[c].source, CaseResult.from_dict(S[c])) for c in S if c in recs]
    return rh.limite_sres("KARLSEN_2022", rh._pisos_medidos(pares))


LIM_S = _lim_sres()


def _tri(m, x, s, lim_s=None):
    return m <= 0.05 and x <= 0.10 and s <= (LIM_S if lim_s is None else lim_s)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    rec = record(CID)
    case = rec.validation_case

    # instrumento 1: a transformacao da CSV chega mesmo?
    _BASE["v"] = None
    c0, r0 = vin.load_full_curve(
        "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/"
        + CSV_TOKEN)
    _BASE["v"] = 332.7
    c1, r1 = vin.load_full_curve(
        "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/"
        + CSV_TOKEN)
    _BASE["v"] = None
    assert r0[0] == r1[0] == 1.0, "ponto 1 tem de ficar 1,0"
    assert abs(r1[1] / r0[1] - F0_REG / 332.7) < 1e-9, "rescala nao aplicada"
    print(f"instrumento CSV: OK  (ex.: {r0[1]:.4f} -> {r1[1]:.4f})")
    print(f"  absolutos lidos: {[round(float(v)*F0_REG, 1) for v in r0]}")

    # instrumento 2: o k_ratchet chega?
    _KR["v"] = 0.0077
    assert rn._effective_overrides(rec, {}).get("k_ratchet") == 0.0077
    _KR["v"] = None
    print("instrumento k_ratchet: OK\n")

    BASES = [312.0, 329.3, 331.0, 332.7, 334.0]
    KRS = [0.003, 0.0035, 0.004, 0.0045, 0.005, 0.006]
    out = []
    print(f"{'base':>7}{'pct':>5}{'k_ratchet':>11}{'MAE':>8}{'mx':>8}"
          f"{'sig':>8}{'vies':>9}  tripe")
    for base in BASES:
        case.preload_percent_yield = round(base / 527.0 * 100)
        case.initial_preload_N = base * 1000.0
        _BASE["v"] = None if base == F0_REG else base
        for kr in KRS:
            _KR["v"] = kr
            r = rn.simulate_case(rec)
            if not r.ok:
                print(f"  !! {base} {kr}: {r.error}")
                continue
            vies = float(np.mean(np.asarray(r.metric_pred, float)
                                 - np.asarray(r.metric_data, float)))
            ok = _tri(r.mae, r.maxerr, r.resid_std)
            print(f"{base:>7.1f}{case.preload_percent_yield:>5}{kr:>11.4f}"
                  f"{r.mae:>8.4f}{r.maxerr:>8.4f}{r.resid_std:>8.4f}"
                  f"{vies:>+9.4f}  {'SIM' if ok else '-'}")
            out.append(dict(base=base, k_ratchet=kr, mae=r.mae, mx=r.maxerr,
                            sd=r.resid_std, vies=vies, tripe=bool(ok)))
        print()
    _BASE["v"] = None
    _KR["v"] = None

    print("LEITURA — a hipotese de parcimonia PASSA se, nas bases 329-334, o")
    print("melhor k_ratchet estiver em 0,0045-0,006 (isto e', na vizinhanca do")
    print("0,005 da run7p1). Se o otimo ficar em 0,003, ela FALHA.")
    if a.json:
        a.json.write_text(json.dumps(out, indent=1), encoding="utf-8")
        print(f"\njson -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
