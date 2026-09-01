# -*- coding: utf-8 -*-
"""Canal de FLANCO no YANG_2021: a fonte em stick tem rota que nao passa por slip?

## Por que esta fonte, e por que este canal

A auditoria de bifurcacao de hoje mediu, nos 6 canais do engine:

    canal                  zerado   ATIVO (tripe/fora)
    wear                      99    106  ->  60/46  (57 %)
    rotational_loosening     101    104  ->  58/46  (56 %)
    thread_fretting          188     17  ->  17/0   (100 %)

**Toda curva com o canal de flanco ativo passa o tripe.** Parte disso e' selecao
(as adocoes D-Q e D-V o ligaram onde ajudava — LIU_2016 e LI_2022 sao as unicas
2 fontes com ele ligado), mas e' exatamente esse o precedente.

E ha um casamento fisico com o achado de hoje (`subperda_stick_resultado.md`): o
YANG_2021 esta em **stick transversal permanente** (slip 0,0000 um), o que mata
`wear` e `rotational_loosening` por construcao. O canal de flanco e' dirigido por
carga **AXIAL**, nao por slip transversal => ele pode entregar perda por uma rota
que o stick **nao bloqueia**.

## Disciplina de procedencia — o que se pode e o que nao se pode varrer

COMPARTILHADO entre as 2 fontes adotadas (usar como esta, sem tocar):
  flank_fret_depth = 2,5e-6   (D-Q 2026-08-05, explicitamente compartilhada)
  flank_amp_exp    = 1,5      (forma KB, Liu 2020 medido)
  flank_wear_on    = 1,0      (switch por prereg; switches nunca sao fitados)

PER-RIG (nao transfere): `k_wear_flank` = 4,32e-14 (LIU_2016) vs 2,15e-13
(LI_2022) — **5x de diferenca**, o que confirma "formas transferem, constantes
nao". Logo NAO se varre livremente: varre-se a **banda de literatura** que a
propria procedencia do LI_2022 cita —

    "banda KB thread|35CrMo-SCM435 [4e-15, 2e-14]"

— mais os 2 valores adotados, como referencia. Um resultado dentro da banda tem
procedencia; fora dela, nao tem, e isso fica dito.

## ⚠️ Companheiro de canal (licao de 2026-08-01, que invalidou o teste anterior)

O canal e' **axial-force-mode-only por default**. Em fonte transversal disp-mode
exige **`flank_transverse_on=1`**, senao o teste mede Δ=0,0000 e a leitura obvia
("morto") e' um TESTE INVALIDO.

⚠️ So'-leitura. Nao adota, nao escreve store nem config.

    py -3.12 New_Theory/flanco_transferencia_premeasure.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.runner as rn                  # noqa: E402
from bolt_analysis_studio.validation import report_html as rh        # noqa: E402
from bolt_analysis_studio.validation.case_registry import (          # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.runner import CaseResult        # noqa: E402

STORE = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"
FONTE = "YANG_2021"

# COMPARTILHADAS — entram fixas, sem varredura
BASE = {"flank_wear_on": 1.0, "flank_transverse_on": 1.0,
        "flank_fret_depth": 2.5e-6, "flank_amp_exp": 1.5}
# banda KB [4e-15, 2e-14] + os 2 adotados (4,32e-14 e 2,15e-13), como referencia
K_FLANK = [4e-15, 1e-14, 2e-14, 4.324762516497783e-14, 2.154434690031884e-13]
_NA_BANDA = {4e-15, 1e-14, 2e-14}

_EXTRA: dict = {}
_orig = rn._effective_overrides
rn._effective_overrides = (
    lambda rec, base: {**_orig(rec, base), **_EXTRA} if _EXTRA
    else _orig(rec, base))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    S = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
    pisos = rh._pisos_medidos([(recs[c].source, r) for c, r in res.items()])
    L = rh.limite_sres(FONTE, pisos)
    cids = sorted(c for c in res if recs[c].source == FONTE
                  and rh.caso_comparavel(FONTE, c))

    def tri(r):
        sd = rh.sres_para_censo(r)
        return (r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX
                and sd is not None and sd <= L)

    def fret_frac(r):
        d = getattr(r, "decomp", None)
        if not isinstance(d, dict) or not d:
            return 0.0
        tot = {k: abs(float(np.asarray(v, float)[-1])) for k, v in d.items()}
        return tot.get("thread_fretting", 0.0) / (sum(tot.values()) or 1.0)

    base = {c: (res[c].mae, res[c].maxerr, res[c].resid_std, tri(res[c]))
            for c in cids}
    n0 = sum(1 for v in base.values() if v[3])
    print(f"{FONTE} — canal de FLANCO ligado com as constantes COMPARTILHADAS")
    print(f"limite_sres {L:.4f} · {len(cids)} curvas · banda KB [4e-15, 2e-14]\n")
    print(f"BASELINE (canal desligado): tripe {n0}/{len(cids)}, "
          f"soma MAE {sum(v[0] for v in base.values()):.4f}\n")

    out = []
    print(f"  {'k_wear_flank':>14} {'proced.':>9}  {'tripe':>6} {'somaMAE':>8} "
          f"{'fret%':>7}  G2 (pioram >+0,01)")
    for kf in K_FLANK:
        _EXTRA.clear()
        _EXTRA.update(BASE)
        _EXTRA["k_wear_flank"] = kf
        n, s, fr, piora, cel = 0, 0.0, [], [], []
        for c in cids:
            r = rn.simulate_case(record(c))
            ok = tri(r)
            n += ok
            s += r.mae
            fr.append(fret_frac(r))
            if r.mae > base[c][0] + 0.01:
                piora.append(c)
            cel.append(dict(cid=c, mae=r.mae, maxerr=r.maxerr, sd=r.resid_std,
                            ok=bool(ok), fret=fret_frac(r)))
        _EXTRA.clear()
        proc = "BANDA" if kf in _NA_BANDA else "fora"
        print(f"  {kf:14.3e} {proc:>9}  {n:>3}/{len(cids)} {s:8.4f} "
              f"{100*float(np.median(fr)):6.1f}%  {len(piora)}")
        out.append(dict(k_wear_flank=kf, na_banda=proc == "BANDA", tripe=n,
                        soma_mae=s, fret_med=float(np.median(fr)),
                        pioram=piora, curvas=cel))

    melhor = max(out, key=lambda o: (o["tripe"], -o["soma_mae"]))
    print(f"\n--- melhor: k={melhor['k_wear_flank']:.3e} "
          f"({'NA BANDA' if melhor['na_banda'] else 'FORA da banda'}) -> "
          f"tripe {melhor['tripe']}/{len(cids)} (era {n0}) ---")
    for d in melhor["curvas"]:
        b = base[d["cid"]]
        seta = ("melhora" if d["mae"] < b[0] - 1e-9 else
                "PIORA" if d["mae"] > b[0] + 1e-9 else "igual")
        print(f"    {d['cid'][-22:]:>22}  {b[0]:.4f} -> {d['mae']:.4f}  "
              f"fret {100*d['fret']:5.1f}%  {'SIM' if d['ok'] else ' - '}"
              f"{'*' if b[3] else ''}  ({seta})")
    if melhor["fret_med"] < 1e-9:
        print("\n  ⚠️ FRETTING MEDIANO = 0 -> o canal NAO ENGATOU: teste INVALIDO,")
        print("     nao 'candidato morto'. Conferir companheiros do canal.")

    if a.json:
        a.json.write_text(json.dumps(dict(limite=L, baseline_tripe=n0,
                                          base=BASE, grade=out),
                                     indent=1, default=float), encoding="utf-8")
        print(f"\njson -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
