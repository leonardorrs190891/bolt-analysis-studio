# -*- coding: utf-8 -*-
"""Mapa das curvas FORA do tripe: cada uma com defeito nomeado e decisao de que depende.

## Por que existe

A fila form-limited fechou em ZERO (D-Z) e as quatro camadas de estatuto foram
auditadas. O que resta esta todo atras de decisao do professor — mas espalhado
por uma duzia de documentos. Este script produz **uma tabela**: para cada curva
fora, qual e' o defeito medido e qual item da fila o cobre.

## As assinaturas, todas ja medidas nesta campanha

* **relogio E1** (P-9): o modelo cruza 90 % em <= metade dos ciclos do dado E
  >= 80 % da perda nesse ponto vem de Embedding+Creep
  (`espelhado_classe_assinatura.py`);
* **bifurcacao** (P-13): canal rotacional dominante e o modelo so' tem dois
  atratores — arresto no piso ou zero
  (`sun_crimp`, `rousseau_bifurcacao`, `ijpem_bifurcacao`);
* **classe parada**: `_FONTES_CLASSE_PARADA`, encerrada em 2026-08-02, mas com
  **10 de 23** tendo defeito OPOSTO ao da classe (P-7);
* **sem piso**: fonte sem par de replica => prova F7 impossivel.

⚠️ So'-leitura, e NAO cria classe nova: cada rotulo aqui ja foi medido e
publicado num resultado desta campanha. O script apenas junta.

    py -3.12 New_Theory/mapa_das_65_fora.py [--json out.json]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation import report_html as rh          # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records   # noqa: E402
from bolt_analysis_studio.validation.runner import CaseResult          # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "_tri", ROOT / "New_Theory" / "regra_de_parada_triagem.py")
tri = importlib.util.module_from_spec(_spec)                # type: ignore[arg-type]
_spec.loader.exec_module(tri)                               # type: ignore[union-attr]

STORE = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION"
         / "validation_store.json")


def _relogio_e1(r):
    """(razao de relogio, fatia emb+creep no ponto de 10 % de perda, alcance).

    ⚠️ **NIVEL ADAPTATIVO (2026-08-07, `p7_orfas_resultado.md`).** A 1a versao
    media o cruzamento de **0,90 fixo**, e em **12 das 65** curvas fora do tripe
    o **DADO nunca cai a 90 %** => `nd = None` => razao `n/a` => a curva **nao
    era testada**. Ela nao *passava* no teste; o teste **nao rodava** — e o
    `classe_parada`, atribuido por FONTE, a absorvia em silencio. Mesma classe do
    ramo `INCONCLUSIVO` do charter, num classificador em vez de num prereg.

    Conserto CONSERVADOR: 0,90 segue sendo o nivel quando o dado o alcanca (a
    classificacao anterior fica **identica**); so' quando ele nao alcanca e' que
    se usa **metade da queda total do dado**, que por construcao o dado atinge.
    Efeito medido: o teste passa a rodar em 5 das 12 e renomeia 3 — entre elas a
    `liu2025_M16_amp0p25`, com razao **0,032** (o modelo chega ao nivel 31× mais
    cedo que o dado), defeito extremo que o limiar fixo escondia por completo.

    As 7 restantes tem assinatura PROPRIA, agora nomeada em vez de silenciada: o
    **modelo nunca alcanca** o nivel que o dado alcanca (`alcance=False`) =>
    sub-perda grosseira. 5 das 7 sao do `YANG_2021`.
    """
    x = np.asarray(r.metric_x or [], float)
    p = np.asarray(r.metric_pred or [], float)
    d = np.asarray(r.metric_data or [], float)
    if len(x) < 3 or len(p) != len(d):
        return None, None, None

    def cruza(y, lv):
        if y.min() > lv or y.max() < lv:
            return None
        o = np.argsort(-y)
        return float(np.interp(-lv, -y[o], x[o]))

    nivel = 0.90 if cruza(d, 0.90) is not None else 1.0 - 0.5 * (1.0 - d.min())
    nm, nd = cruza(p, nivel), cruza(d, nivel)
    raz = (nm / nd) if (nm and nd) else None
    alcance = nm is not None          # o modelo chega onde o dado chegou?
    frac = None
    dec = getattr(r, "decomp", None)
    if isinstance(dec, dict) and dec:
        arr = {k: np.abs(np.asarray(v, float)) for k, v in dec.items()}
        tot = sum(arr.values())
        ec = sum(v for k, v in arr.items()
                 if "emb" in k.lower() or "creep" in k.lower())
        if (tot >= 0.10).any():
            i = int(np.argmax(tot >= 0.10))
            if tot[i] > 0:
                frac = float(ec[i] / tot[i])
    return raz, frac, alcance


def _rot(r):
    dec = getattr(r, "decomp", None)
    if not isinstance(dec, dict) or not dec:
        return None
    tot = {k: abs(float(np.asarray(v, float)[-1])) for k, v in dec.items()}
    s = sum(tot.values()) or 1.0
    return tot.get("rotational_loosening", 0.0) / s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    S = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
    pisos = rh._pisos_medidos([(recs[c].source, r) for c, r in res.items()])
    exc, dec = set(rh._EXCECOES), set(rh._DECLARADAS)
    com_piso = {str(f[0]).split()[0] for f in pisos["fam"]}

    linhas = []
    for cid in sorted(res):
        rec, r = recs[cid], res[cid]
        f = rec.source
        if not rh.caso_comparavel(f, cid) or r.mae is None:
            continue
        L = rh.limite_sres(f, pisos)
        sd = rh.sres_para_censo(r)
        if sd is not None and r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX \
                and sd <= L:
            continue                                   # passa o tripe
        # estatuto
        if cid in exc:
            est, dep = "excecao", "-"
        elif cid in dec:
            est, dep = "declarada", "-"
        else:
            est = "SEM ESTATUTO"
            dep = ""
        # defeito medido
        raz, frac, alcance = _relogio_e1(r)
        rot = _rot(r)
        if raz is not None and raz <= 0.5 and (frac or 0) >= 0.80:
            defeito, cobre = "relogio E1", "P-9"
        elif (rot or 0) >= 0.70:
            defeito, cobre = "bifurcacao (rotacional %.0f%%)" % (100 * rot), "P-13"
        elif alcance is False:
            # o modelo NUNCA chega ao nivel que o dado alcanca => sub-perda
            # grosseira. Antes disto a curva caia em `classe parada` em silencio.
            #
            # ⚠️ Aponta para a **P-14** (limiar duro do slip), nao para a P-7.
            # A 1a versao dizia "P-7" e era ERRO MEU de atribuicao: a P-7 e' sobre
            # RECLASSIFICAR a camada `classe_parada`, e nao tem relacao com "o
            # modelo nao alcanca o dado". A P-14 e' a proposta que enderaca este
            # defeito (`subperda_stick_resultado.md`).
            #
            # NAO e' identidade: a P-14 mira slip resolvido == 0 (**18** curvas,
            # medidas instrumentando `resolve_transverse_slip`), e este teste mira
            # "nao alcanca o nivel do dado" — populacoes que se sobrepoem sem
            # coincidir (a `liu2020_fig9` nao alcanca E desliza 399 um, porque os
            # canais dela estao desligados por CONFIG). O store nao guarda slip,
            # entao o teste exato exige re-simular.
            defeito, cobre = "sub-perda (modelo nao alcanca o dado)", "P-14"
        elif f in tri._FONTES_CLASSE_PARADA:
            defeito, cobre = "classe parada", "P-7"
        elif f not in com_piso:
            defeito, cobre = "sem piso (F7 impossivel)", "dado"
        else:
            defeito, cobre = "nao classificado", "?"
        if est == "SEM ESTATUTO":
            dep = cobre
        linhas.append(dict(cid=cid, fonte=f, estatuto=est, defeito=defeito,
                           depende=dep, mae=r.mae, mx=r.maxerr, sd=r.resid_std))

    print(f"{len(linhas)} curvas fora do tripe\n")
    print(f"{'curva':<44}{'estatuto':<14}{'defeito medido':<32}dep")
    for L in linhas:
        print(f"{L['cid'][:44]:<44}{L['estatuto']:<14}{L['defeito'][:32]:<32}"
              f"{L['depende']}")

    print("\n--- por DEFEITO ---")
    for k, v in Counter(L["defeito"].split(" (")[0] for L in linhas).most_common():
        print(f"  {k:<32} {v:>3}")
    print("\n--- por DECISAO que o cobre (so' as SEM ESTATUTO) ---")
    sem = [L for L in linhas if L["estatuto"] == "SEM ESTATUTO"]
    for k, v in Counter(L["depende"] for L in sem).most_common():
        print(f"  {k:<32} {v:>3}")
    print(f"\ncom estatuto: {len(linhas)-len(sem)}  ·  sem estatuto: {len(sem)}")
    if a.json:
        a.json.write_text(json.dumps(linhas, indent=1, default=float),
                          encoding="utf-8")
        print(f"json -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
