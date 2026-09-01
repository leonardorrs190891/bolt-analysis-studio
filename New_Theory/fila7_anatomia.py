# -*- coding: utf-8 -*-
"""Anatomia das 7 curvas da fila FORM-LIMITED — nivel ou forma?

SO-LEITURA (le o store; nao simula, nao escreve).

## Por que existe

A campanha concluiu, com 18 alavancas mortas, que "constante nao fecha a 3a
perna". Essa conclusao foi medida sobre a populacao de falhas de FORMA: uma
alavanca de escala move o residuo em bloco (nivel) e NAO muda onde ele cruza
zero, logo nao pode reduzir sigma_res numa curva cujo residuo troca de sinal.
E' algebra, nao azar.

Mas a fila de hoje tem 7 curvas e nem todas falham por forma:

    RMSE^2 = vies^2 + sigma_res^2

Falha so no MAE = problema de NIVEL, e nivel responde a constante. Aplicar a
conclusao da populacao errada descartaria por reflexo justamente as curvas
onde ainda ha alavanca.

Este script separa as duas populacoes com numeros, antes de qualquer prereg:

  · vies (residuo medio) e sua fatia do RMSE
  · trocas de sinal do residuo ao longo do ensaio
  · qual perna manda e quanto falta nela
  · onde o residuo mora (inicio/meio/fim da janela da metrica)

    py -3.12 New_Theory/fila7_anatomia.py

## ⚠️ Arredondar num print de diagnostico INVENTA zeros

Medido em 2026-08-04, sondando o CACCESE: um print com `round(valor, 6)`
mostrou `C_creep = 0.0` e `emb_depth = 0.0` para um caso cujos valores reais
sao **3.063e-11** e **1e-8**. Conclusao que isso produziria: "creep
DESLIGADO carregando 100% da perda" — absurdo que so foi pego porque a
decomposicao do store contradisse o display.

Constantes desta base moram em 1e-8..1e-14. **Em sonda, imprima com `%.6g`
ou repr, nunca `round(x, n)`** — e quando um numero de config aparecer como
0.0, confira contra `material_kwargs_for` antes de escrever qualquer coisa.
Mesma familia dos tres `Delta=0 exato` lidos como "alavanca morta".
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation import report_html as rh          # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402
from bolt_analysis_studio.validation.runner import CaseResult          # noqa: E402

STORE = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"

FILA = [
    "liu2022_fig8_multi_t2",
    "li2022ti_axialmin_10Hz",
    "caccese2009_retighten_19p1mm_no_retighten",
    "liu2022_fig8_multi_t1",
    "liu2022_fig8_multi_t4",
    "caccese2009_tapered_45kN_rep2",
    "li2022ti_axial_10Hz_full",
]


def anatomia(rec: dict) -> dict | None:
    """Decompoe o residuo de UMA curva. `None` se o store nao tem os vetores.

    ⚠️ Le `metric_pred`/`metric_data` — os vetores que a METRICA de fato
    comparou (alinhados e trimados). Recomputar da curva crua daria outro
    numero: e' o gotcha que ja produziu 4 valores discordantes na mesma
    pagina em 2026-07-27.
    """
    mp = np.asarray(rec.get("metric_pred") or [], float)
    md = np.asarray(rec.get("metric_data") or [], float)
    mx = np.asarray(rec.get("metric_x") or [], float)
    if mp.size < 2 or mp.size != md.size:
        return None
    r = mp - md                                   # residuo com sinal
    vies = float(np.mean(r))
    sig = float(np.std(r))
    rmse = float(np.sqrt(np.mean(r * r)))
    # trocas de sinal: o discriminante nivel-vs-forma. Zero troca => o
    # residuo e' um deslocamento em bloco e uma constante o alcanca.
    s = np.sign(r)
    s = s[s != 0]
    trocas = int(np.sum(s[1:] != s[:-1])) if s.size > 1 else 0
    # onde mora o erro: tercos da JANELA DA METRICA (nao do ensaio)
    t = np.array_split(np.abs(r), 3)
    tercos = [float(np.mean(x)) if x.size else float("nan") for x in t]
    return dict(n=int(mp.size), vies=vies, sigma=sig, rmse=rmse,
                trocas=trocas, tercos=tercos,
                frac_vies=float(vies * vies / (rmse * rmse)) if rmse else 0.0,
                x0=float(mx[0]) if mx.size else float("nan"),
                x1=float(mx[-1]) if mx.size else float("nan"))


def classe(a: dict, perna: str) -> str:
    """Tres populacoes, tres remedios — criterio declarado ANTES de olhar.

    ⚠️ A 1a versao deste script tinha DUAS populacoes ("nivel" x "forma") e
    errou por ignorar a algebra que decide: **sigma_res e' invariante por
    translacao**. Somar uma constante ao residuo muda o vies e NAO muda o
    desvio-padrao. Logo:

      · perna MAE + vies dominante  -> deslocar o nivel FECHA (sigma nem se
        move, e ele ja esta dentro). Alavanca: qualquer uma que mude o nivel.
      · perna sigma + residuo MONOTONO (0 trocas) -> deslocar o nivel nao faz
        nada; o que fecha e' mudar a TAXA, para achatar a rampa do residuo.
        Nao e' a patologia que matou as 18 alavancas (essa e' sinal
        alternado); constante de taxa alcanca em principio.
      · sinal alternado ou vies ~0 -> FORMA. Nenhuma constante conhecida.
    """
    if perna == "MAE" and a["frac_vies"] >= 0.50 and a["trocas"] <= 2:
        return "nivel"
    if a["trocas"] <= 1 and a["frac_vies"] >= 0.50:
        return "taxa"
    return "forma"


_REMEDIO = {
    "nivel": "NIVEL — perna MAE, vies domina: alavanca de nivel FECHA",
    "taxa":  "TAXA — perna sigma, residuo monotono: precisa achatar a rampa "
             "(sigma nao ve translacao)",
    "forma": "FORMA — sinal alternado / vies ~0: nenhuma constante conhecida",
}


def main() -> int:
    store = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    pares = [(recs[c].source, CaseResult.from_dict(store[c]))
             for c in store if c in recs]
    pisos = rh._pisos_medidos(pares)

    print(f"ANATOMIA DA FILA — store "
          f"{next(iter(store.values())).get('engine_fingerprint')}")
    for k in ("nivel", "taxa", "forma"):
        print(f"  {_REMEDIO[k]}")
    print("  (sigma_res e' INVARIANTE por translacao: alavanca de nivel muda o")
    print("   vies e nao muda o sigma — e' o que separa 'nivel' de 'taxa'.)\n")

    pop: dict[str, list] = {}
    for cid in FILA:
        if cid not in store:
            print(f"  !! {cid}: ausente do store")
            continue
        rec = store[cid]
        src = recs[cid].source
        a = anatomia(rec)
        if a is None:
            print(f"  !! {cid}: sem vetores de metrica")
            continue
        lim_s = float(rh.limite_sres(src, pisos))
        xm = max(rec["mae"] / rh.META_MAE, rec["maxerr"] / rh.META_MAX,
                 (rec["resid_std"] or 0) / lim_s)
        perna = ("MAE" if rec["mae"] / rh.META_MAE == xm else
                 "res.max" if rec["maxerr"] / rh.META_MAX == xm else "sigma")
        cls = classe(a, perna)
        pop.setdefault(cls, []).append(cid)
        print(f"  {cid}")
        print(f"    fonte {src} · n={a['n']} · janela N={a['x0']:.0f}..{a['x1']:.0f}")
        print(f"    MAE {rec['mae']:.4f} ({rec['mae']/rh.META_MAE:.2f}x) · "
              f"res.max {rec['maxerr']:.4f} ({rec['maxerr']/rh.META_MAX:.2f}x) · "
              f"sigma {rec['resid_std']:.4f} ({(rec['resid_std'] or 0)/lim_s:.2f}x)")
        print(f"    PERNA QUE MANDA: {perna} ({xm:.2f}x)")
        print(f"    vies {a['vies']:+.4f} = {100*a['frac_vies']:.0f}% do RMSE^2 "
              f"· sigma {a['sigma']:.4f} · trocas de sinal {a['trocas']}")
        print(f"    |residuo| por terco: {a['tercos'][0]:.4f} / "
              f"{a['tercos'][1]:.4f} / {a['tercos'][2]:.4f}")
        print(f"    => {_REMEDIO[cls]}\n")

    print("RESUMO — " + " · ".join(f"{k} {len(v)}" for k, v in pop.items()))
    for k in ("nivel", "taxa", "forma"):
        for cid in pop.get(k, []):
            print(f"  {k:6s} {cid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
