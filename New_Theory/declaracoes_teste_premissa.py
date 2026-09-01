# -*- coding: utf-8 -*-
"""Auditoria de PREMISSA das 14 declaracoes vivas — o argumento cobre o defeito?

## De onde vem

`resolucao_criterio_lacuna_resultado.md` (2026-08-07) achou que o critério
"data-limited por resolucao" mede so' o passo do DADO e nunca o compara ao ERRO
do modelo — e que **5 das 6** declaracoes sob ele tem a premissa falhando
(erro ate 4x o passo). O teste que achou isso e' generico: **o argumento da
declaracao cobre as pernas que de fato reprovam a curva?**

Este script aplica esse teste aos OUTROS critérios em uso:

* **`n<6`** (assinado 2026-08-01) — premissa: *sigma_res sem 6 pontos nao tem
  suporte estatistico*. O registro da assinatura diz que as 3 declaradas tinham
  *"mae/mx passando com folga"*. Se alguma n<6 reprovar em MAE ou res.max, a
  declaracao cobre a perna ERRADA: MAE de 4-5 pontos e' perfeitamente julgavel.
* **colapso** (`max|Delta dado| > 0,25`) — premissa: *a metrica fica mal-posta
  no penhasco*. Se o erro NAO estiver concentrado no penhasco, o argumento nao
  cobre o defeito. Mede-se a fracao do res.max que cai na vizinhanca do maior
  salto do dado.
* **escopo/procedencia** — nao tem premissa numerica (o paper diz que o ensaio
  nao atinge o efeito, ou o material esta fora). Fica listada, sem teste.

⚠️ **Nada e' retratado aqui.** Camada de declaracao e' assinada; o script
produz o NUMERO para a decisao.

    py -3.12 New_Theory/declaracoes_teste_premissa.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation import report_html as rh          # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records   # noqa: E402
from bolt_analysis_studio.validation.runner import CaseResult          # noqa: E402

STORE = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION"
         / "validation_store.json")
N_MIN = 6
SALTO_COLAPSO = 0.25


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    S = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
    pisos = rh._pisos_medidos([(recs[c].source, r) for c, r in res.items()])

    print(f"{len(rh._DECLARADAS)} declaracoes vivas\n")
    print(f"{'curva':<44}{'n':>4}{'MAE':>8}{'x':>6}{'mx':>8}{'x':>6}"
          f"{'sig':>8}{'x':>6}  classe / premissa")
    out, alerta = {}, []
    for cid in sorted(rh._DECLARADAS):
        if cid not in res:
            print(f"{cid[:44]:<44}  (fora do store)")
            continue
        r = res[cid]
        f = recs[cid].source
        d = np.asarray(r.metric_data or [], float)
        n = len(d)
        L = rh.limite_sres(f, pisos)
        mm = r.mae / rh.META_MAE
        mx = r.maxerr / rh.META_MAX
        sg = (r.resid_std / L) if L else float("nan")
        passo = float(np.median(np.abs(np.diff(d)))) if n >= 2 else None
        salto = float(np.max(np.abs(np.diff(d)))) if n >= 2 else None

        # ⚠️ Uma declaracao e' justificada se QUALQUER critério assinado se
        # sustentar — nao apenas o primeiro que casa. A 1a versao deste script
        # classificava pela ordem do report e por isso mandou a 0,50/0,55 para o
        # ramo `n<6` sem nunca testar `colapso` nelas. Foi assim que a P-10
        # publicou "5 falhando": a 0,45 tem justificativa de COLAPSO valida e
        # entrou na conta por engano meu.
        p = np.asarray(r.metric_pred, float)
        cand = []
        if n < N_MIN:
            viol = [k for k, v in (("MAE", mm), ("mx", mx)) if v > 1.0]
            cand.append(("n<6", not viol,
                         "mae/mx passam" if not viol
                         else f"viola {'+'.join(viol)}"))
        if salto is not None and salto > SALTO_COLAPSO:
            i_sal = int(np.argmax(np.abs(np.diff(d))))
            i_res = int(np.argmax(np.abs(p - d)))
            dist = abs(i_res - i_sal)
            cand.append(("colapso", dist <= 2,
                         f"res.max a {dist} idx do penhasco"))
        if passo is not None and passo >= rh.META_MAX:
            razao = r.maxerr / passo
            cand.append(("resolucao", razao <= 1.0, f"mx/passo {razao:.2f}"))
        if not cand:
            classe, prem = "escopo/procedencia", "sem premissa numerica"
            sustenta = True
        else:
            sustenta = any(c[1] for c in cand)
            classe = "+".join(c[0] for c in cand)
            prem = " ; ".join(f"{c[0]}:{'OK' if c[1] else 'FALHA'} ({c[2]})"
                              for c in cand)
            if not sustenta:
                prem = "** NENHUM criterio se sustenta -> " + prem
        print(f"{cid[:44]:<44}{n:>4}{r.mae:>8.4f}{mm:>6.2f}"
              f"{r.maxerr:>8.4f}{mx:>6.2f}{r.resid_std:>8.4f}{sg:>6.2f}"
              f"  {classe} / {prem}")
        out[cid] = dict(n=n, classe=classe, premissa=prem,
                        mult=[mm, mx, sg], passo=passo, salto=salto)
        if not sustenta:
            alerta.append((cid, classe, prem))

    print(f"\ndeclaracoes com PREMISSA FALHANDO: {len(alerta)}")
    for cid, cl, pr in alerta:
        print(f"   {cid:<46} [{cl}] {pr}")
    print("\nLEITURA: premissa falhando NAO significa que a curva deveria")
    print("passar — significa que o ARGUMENTO da declaracao nao cobre a perna")
    print("que a reprova. E' o mesmo defeito que a prova F7 tem quando deixa")
    print("perna DESCOBERTA, e a campanha ja retratou 5 excecoes por isso.")
    if a.json:
        a.json.write_text(json.dumps(out, indent=1, default=float),
                          encoding="utf-8")
        print(f"json -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
