"""Composicao do balde `classe_parada` — quem esta parado, e por qual fonte.

So-leitura, segundos. A classe e' atribuida POR FONTE
(`regra_de_parada_triagem.classificar`, L100), logo uma fonte classificada por
engano leva TODAS as suas curvas fora junto. Este script mede o tamanho de cada
bloco para que qualquer proposta de reclassificacao (p.ex.
`sun_crimp_resultado.md`) chegue ao professor com custo/beneficio em NUMERO.

O modulo da triagem e' importado do arquivo — nada de `_FONTES_CLASSE_PARADA`
duplicado aqui. Reimplementar regra ja custou uma triagem inteira sob regua
vencida (ver docstring de `pisos_medidos` la).

Uso: PYTHONPATH=src py -3.12 New_Theory/classe_parada_composicao.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation import report_html as rh           # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records   # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "_triagem", ROOT / "New_Theory" / "regra_de_parada_triagem.py")
tri = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tri)

STORE = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"


def main() -> int:
    store = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    pisos = tri.pisos_medidos(store, recs)
    excecoes = set(rh._EXCECOES)

    por_fonte: dict[str, list] = {}
    total_fonte: dict[str, int] = {}
    for cid, raw in store.items():
        rec = recs.get(cid)
        if rec is None or not rh.caso_comparavel(rec.source, cid):
            continue
        fonte = rec.source
        total_fonte[fonte] = total_fonte.get(fonte, 0) + 1
        mae, mx, sd = raw.get("mae"), raw.get("maxerr"), raw.get("resid_std")
        if mae is None or mx is None or sd is None:
            continue
        lim_s = rh.limite_sres(fonte, pisos)
        if mae <= rh.META_MAE and mx <= rh.META_MAX and sd <= lim_s:
            continue                                   # passa o tripe
        if cid in excecoes or cid in rh._DECLARADAS:
            continue                                   # tem estatuto proprio
        if fonte not in tri._FONTES_CLASSE_PARADA:
            continue
        por_fonte.setdefault(fonte, []).append(
            (cid, float(mae), float(mx), float(sd), float(lim_s)))

    print("BALDE classe_parada — composicao por fonte")
    print("  (fora do tripe, sem excecao assinada e sem declaracao)")
    print()
    tot = 0
    nomes = ("MAE", "mx ", "sig")
    for fonte in sorted(por_fonte, key=lambda f: (-len(por_fonte[f]), f)):
        linhas = por_fonte[fonte]
        tot += len(linhas)
        piso = tri.piso_da_fonte(pisos, fonte)
        piso_txt = f"{piso:.4f}" if piso is not None else "  n/a "
        lim = rh.limite_sres(fonte, pisos)
        print(f"{fonte:<18} n={len(linhas):>2} de {total_fonte.get(fonte, 0):>2}"
              f"   piso_sig={piso_txt}  limite_sig={lim:.4f}")
        for cid, mae, mx, sd, lim_s in sorted(linhas):
            mult = (mae / rh.META_MAE, mx / rh.META_MAX, sd / lim_s)
            manda = nomes[int(np.argmax(mult))]
            nviol = sum(1 for m in mult if m > 1.0)
            pior = max(mult)
            print(f"    {cid:<40} {mult[0]:>5.2f}x {mult[1]:>5.2f}x"
                  f" {mult[2]:>5.2f}x   manda={manda} viola={nviol}"
                  f" pior={pior:.2f}x")
        print()
    print(f"TOTAL no balde: {tot}")
    print()
    print("Leitura: cada bloco e' o custo de MANTER a fonte na classe. Retirar")
    print("uma fonte NAO conserta curva nenhuma — devolve as curvas dela para a")
    print("fila de trabalho, e a fila e' o que a regra de parada mede.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
