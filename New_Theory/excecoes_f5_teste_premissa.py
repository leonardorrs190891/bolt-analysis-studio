# -*- coding: utf-8 -*-
"""As provas F5 cobrem as pernas que reprovam? — desvio-a-mediana por perna.

## O criterio F5, como esta escrito

`f5_excecoes_propostas.md`: *"quando replicas nominalmente identicas divergem
mais que a meta, nenhum modelo deterministico unico pode ficar dentro dela. A
prova e' o **desvio maximo a mediana do ensemble** — o res.max que a curva ideal
(a propria mediana dos dados) ja teria contra alguma replica."*

⇒ a prova, como enunciada, fala de **res.max**. As excecoes, porem, podem violar
tambem **MAE** e **sigma_res** — e a curva-mediana tem valores proprios nessas
duas pernas que a prova nao cita.

Este script computa o desvio-a-mediana **nas TRES pernas** e pergunta, por
excecao: cada perna que a curva viola esta coberta pelo que a mediana ja teria?

E' o mesmo teste que achou a lacuna do critério de resolucao
(`resolucao_criterio_lacuna_resultado.md`) e que confirmou a camada F7 sa
(`excecoes_f7_premissa_resultado.md`). Fecha a auditoria das 4 classes.

## Metodo

Familia = curvas da MESMA fonte com o mesmo prefixo de condicao declarado no
proprio doc F5 (fig6 do BAUER, fig8 do BAUER, ...). Para cada familia:
1. interpola todas as replicas numa grade comum (janela de x compartilhada);
2. mediana ponto-a-ponto = "curva ideal";
3. para cada replica, MAE/res.max/sigma da mediana contra ela;
4. barra da perna = o **maximo** sobre as replicas (o que a curva ideal ja
   teria contra a pior).

⚠️ Nada e' retratado — camada de excecao e' assinada.

    py -3.12 New_Theory/excecoes_f5_teste_premissa.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation import report_html as rh          # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records   # noqa: E402
from bolt_analysis_studio.validation.runner import CaseResult          # noqa: E402

STORE = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION"
         / "validation_store.json")


def _familia(cid: str) -> str:
    """Chave de familia lida do case_id (as do doc F5)."""
    for tag in ("M8_fig6", "M12_fig8", "fig8", "fig7", "fig6"):
        if tag in cid:
            return cid.split("_" + tag)[0] + "_" + tag
    return cid.rsplit("_", 1)[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    S = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
    pisos = rh._pisos_medidos([(recs[c].source, r) for c, r in res.items()])
    f5 = getattr(rh, "_F5_EXCECOES", {})

    # agrupa TODAS as curvas da fonte pela familia (nao so' as excetuadas —
    # a mediana precisa do ensemble inteiro)
    fam = defaultdict(list)
    for cid in res:
        fam[(recs[cid].source, _familia(cid))].append(cid)

    print(f"{len(f5)} excecoes F5\n")
    out, desc = {}, []
    for chave, membros in sorted(fam.items()):
        alvo = [c for c in membros if c in f5]
        if not alvo:
            continue
        # GUARDA DE PAREAMENTO (2026-08-20). O `_familia` agrupa por ROTULO DE
        # FIGURA, e figura que e' VARREDURA de uma variavel nao e' ensemble de
        # replicas: o ECCLES fig7/fig8 varre CARGA AXIAL e o JCSR `plain` varre
        # AMBIENTE (indoor/outdoor/seawater). Poolar a variavel varrida infla a
        # barra — no JCSR dava MAE 0,3726 — e barra inflada nao produz so' falso
        # alarme, ela APROVA (foi o padrao dos bloqueios G/H de 08-14, onde o CHU
        # pareava Ra 1,6x0,4 e inflava o limite que aprovava o test5).
        # O projeto ja tem o bloqueio canonico: `_SEM_FAMILIA_MECANICA`. Este
        # script o consultava ZERO vezes.
        bloqueados = [c for c in membros if c in getattr(rh, "_SEM_FAMILIA_MECANICA", ())]
        curvas = []
        for c in membros:
            r = res[c]
            x = np.asarray(r.metric_x or [], float)
            d = np.asarray(r.metric_data or [], float)
            if len(x) >= 4 and len(x) == len(d):
                curvas.append((c, x, d))
        # A ordem importa: familia de 1 membro e' pulada por NAO HAVER ensemble,
        # nao pelo bloqueio de pareamento. Reportar o bloqueio antes trocaria o
        # motivo verdadeiro de cada linha.
        if bloqueados and len(curvas) >= 3:
            print(f"{chave[1]:<28} FAMILIA BLOQUEADA por _SEM_FAMILIA_MECANICA "
                  f"({len(bloqueados)}/{len(membros)} membros) - barra NAO calculada")
            for c in sorted(alvo):
                # imprime a prova REAL em vez de afirmar o que ela e': quem le
                # decide, e o script nao super-afirma sobre estatuto alheio.
                # ASCII no texto da PROVA: ela e' prosa arbitraria e longa (traz
                # travessao e acentos), e console cp1252 quebra nisso — foi um
                # UnicodeEncodeError assim que derrubou o
                # regra_de_parada_triagem.py no fim da execucao. NOTA HONESTA:
                # este script JA imprimia nao-ASCII antes desta mudanca (o
                # travessao do 'ensemble com N curvas' e o middot da linha da
                # barra), logo nao ha invariante ASCII a preservar aqui — o que
                # se evita e' injetar prosa de terceiros, de tamanho e conteudo
                # imprevisiveis, no meio de um print.
                prova_ascii = (str(f5.get(c))[:70]
                               .encode("ascii", "replace").decode("ascii"))
                print(f"      {c[:40]:<40} sem barra. prova assinada: {prova_ascii}")
            print()
            continue
        if len(curvas) < 3:
            print(f"{chave[1]:<28} ensemble com {len(curvas)} curvas — "
                  f"mediana sem sentido, pulado")
            continue
        lo = max(x.min() for _, x, _ in curvas)
        hi = min(x.max() for _, x, _ in curvas)
        if hi <= lo:
            print(f"{chave[1]:<28} janelas disjuntas, pulado")
            continue
        g = np.linspace(lo, hi, 60)
        M = np.vstack([np.interp(g, x, d) for _, x, d in curvas])
        med = np.median(M, axis=0)
        barras = {}
        for k, fn in (("MAE", lambda e: np.mean(np.abs(e))),
                      ("mx", lambda e: np.max(np.abs(e))),
                      ("sig", lambda e: np.std(e))):
            barras[k] = float(max(fn(med - M[i]) for i in range(len(curvas))))
        print(f"=== {chave[0]} / {chave[1]}   ensemble n={len(curvas)}"
              f"   janela x {lo:.0f}..{hi:.0f}")
        print(f"    barra da CURVA IDEAL (desvio max a mediana): "
              f"MAE {barras['MAE']:.4f} · mx {barras['mx']:.4f} · "
              f"sig {barras['sig']:.4f}")
        L = rh.limite_sres(chave[0], pisos)
        for c in sorted(alvo):
            r = res[c]
            vals = (("MAE", r.mae, rh.META_MAE), ("mx", r.maxerr, rh.META_MAX),
                    ("sig", r.resid_std, L))
            # A PERNA QUE A PROVA F5 AFIRMA E' `mx`, E SO' ELA (2026-08-20).
            # `excecoes_f5_premissa_resultado.md` traz a errata: o argumento F5 e'
            # de FAMILIA ("nenhum modelo deterministico unico pode ficar dentro da
            # meta"), enunciado sobre o desvio maximo a mediana = RES.MAX. MAE e
            # sigma nao sao afirmados por ele. Chamar MAE/sigma de "DESCOBERTA" e'
            # testar o estatuto F5 contra o criterio F7 — o erro que aquele doc
            # registra como a 5a ocorrencia, e que esta saida convidava a repetir.
            # Eles seguem IMPRESSOS (informacao nao se esconde), com o rotulo certo.
            partes, mx_descoberta = [], False
            for k, v, lim in vals:
                if v is None or v <= lim:
                    continue
                coberta = v <= barras[k]
                if k == "mx":
                    partes.append(
                        f"{'mx coberta' if coberta else '** mx DESCOBERTA'} "
                        f"({v:.4f}{'<=' if coberta else '>'}{barras[k]:.4f})")
                    mx_descoberta = not coberta
                else:
                    partes.append(
                        f"[fora do que a F5 afirma] {k} {v:.4f} vs "
                        f"{barras[k]:.4f}")
            if not partes:
                partes = ["nenhuma perna viola"]
            print(f"      {c[:40]:<40} {' ; '.join(partes)}")
            out[c] = dict(familia=chave[1], barras=barras, partes=partes,
                          mx_coberta=not mx_descoberta)
            if mx_descoberta:
                desc.append(c)
        print()

    print(f"excecoes F5 com a perna DA PROVA (res.max) DESCOBERTA: {len(desc)}")
    for c in desc:
        print(f"   {c}")
    print("\nLEITURA (corrigida em 2026-08-20; a anterior convidava a um erro de")
    print("categoria). A prova F5 e' de FAMILIA e enunciada sobre RES.MAX:")
    print("'nenhum modelo deterministico unico pode ficar dentro da meta'. Res.max")
    print("descoberto = a inalcancabilidade nao cobre o defeito (foi assim que a")
    print("P-11 retratou a bauer_M12_fig8_test1). MAE/sigma acima da barra NAO sao")
    print("defeito da F5: sao pernas que a prova nunca afirmou, e cobra-las e")
    print("aplicar o criterio F7 a um estatuto F5. Familia bloqueada por")
    print("_SEM_FAMILIA_MECANICA nao recebe barra: a variavel varrida (carga axial")
    print("no ECCLES, ambiente no JCSR) nao e' replica, e a barra inflada APROVA.")
    out["_descobertas"] = desc
    if a.json:
        a.json.write_text(json.dumps(out, indent=1, default=float),
                          encoding="utf-8")
        print(f"json -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
