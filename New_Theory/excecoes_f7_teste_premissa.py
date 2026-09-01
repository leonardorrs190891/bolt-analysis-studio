# -*- coding: utf-8 -*-
"""As provas F7 ainda descrevem o store? — deriva entre prova gravada e valor atual.

## O que a 1a versao deste script fez de errado (duas coisas)

1. **Barra errada.** Comparei contra a MEDIA da fonte (`por_fonte`), quando as
   provas do LU_2024 foram assinadas contra o **piso POR CONDICAO** — o
   `CLAUDE.md` e' explicito: *"a barra usa o piso da MESMA condicao ... nunca a
   media da fonte"*. Com a media, a `T10Nm` aparecia DESCOBERTA (0,2592 >
   0,2501) quando a prova dela usa 0,613.
2. **Categoria errada.** Das 23 excecoes vivas, **16 sao F5** — criterio
   "scatter de replicas (desvio-a-mediana)", que **nao** e' o teste de tres
   pernas contra piso. Aplicar-lhes a regra do F7 e' comparar coisas distintas.

Resultado: o "8 descobertas" da 1a versao era **artefato**, e nao foi publicado.

## O que este script mede

Cada prova F7 gravada carrega os pares `valor/piso` que a sustentaram. Duas
perguntas separadas:

* **(A) deriva**: o `valor` da prova ainda e' o do store? Se nao, a prova
  descreve uma simulacao que nao existe mais — e' o §4.43 dentro da camada de
  excecao.
* **(B) cobertura**: com o valor ATUAL contra o piso CITADO na prova, cada perna
  segue coberta?

⚠️ Nada e' retratado — camada de excecao e' assinada. O script produz o numero.

    py -3.12 New_Theory/excecoes_f7_teste_premissa.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation import report_html as rh          # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records   # noqa: E402
from bolt_analysis_studio.validation.runner import CaseResult          # noqa: E402

STORE = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION"
         / "validation_store.json")
# rotulo na prova -> atributo do CaseResult
PERNA = {"MAE": "mae", "res.máx": "maxerr", "res.max": "maxerr",
         "mx": "maxerr", "σ": "resid_std", "sig": "resid_std"}
PAT = re.compile(r"(MAE|res\.máx|res\.max|mx|σ|sig)\s*"
                 r"(\d+\.\d+)\s*/\s*(\d+\.\d+)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    S = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    res = {c: CaseResult.from_dict(S[c]) for c in S if c in recs}
    f7 = getattr(rh, "_F7_EXCECOES", {})
    f5 = getattr(rh, "_F5_EXCECOES", {})

    print(f"excecoes vivas: {len(rh._EXCECOES)}  "
          f"(F7 com prova de piso: {len(f7)} · F5 scatter: {len(f5)})")
    print("\n=== F7: prova gravada vs store (A deriva, B cobertura)")
    out, deriva, desc = {}, [], []
    for cid, prova in sorted(f7.items()):
        if cid not in res:
            print(f"{cid[:44]:<44} (fora do store)"); continue
        r = res[cid]
        pares = PAT.findall(prova)
        if not pares:
            print(f"{cid[:44]:<44} prova sem pares valor/piso legiveis")
            continue
        forte_str = "FORTE" in prova
        linhas = []
        for rot, v_prova, piso_s in pares:
            attr = PERNA[rot]
            v_now = float(getattr(r, attr))
            v_p, piso = float(v_prova), float(piso_s)
            d = v_now - v_p
            bar = piso / math.sqrt(2.0) if forte_str else piso
            cob = v_now <= bar
            linhas.append(dict(perna=rot, valor_prova=v_p, valor_store=v_now,
                               deriva=d, piso=piso, barra=bar, coberta=cob))
            if abs(d) > 0.005:
                deriva.append((cid, rot, v_p, v_now))
            if not cob:
                desc.append((cid, rot, v_now, bar))
        print(f"{cid[:44]:<44} {'FORTE' if forte_str else 'PROVA'}")
        for L in linhas:
            flag = ""
            if abs(L["deriva"]) > 0.005:
                flag += f"  <<DERIVA {L['deriva']:+.4f}"
            if not L["coberta"]:
                flag += f"  <<DESCOBERTA (barra {L['barra']:.4f})"
            print(f"      {L['perna']:<8} prova {L['valor_prova']:.4f}"
                  f"  store {L['valor_store']:.4f}  piso {L['piso']:.4f}{flag}")
        out[cid] = dict(tipo="F7", forte=forte_str, pernas=linhas)

    print(f"\n=== F5 ({len(f5)}): criterio de SCATTER, nao testado aqui")
    for cid, prova in sorted(f5.items()):
        print(f"   {cid[:44]:<44} "
              f"{str(prova)[:60].encode('ascii', 'replace').decode()}")
        out[cid] = dict(tipo="F5", prova=str(prova))

    print(f"\nF7 com DERIVA > 0,005 entre prova e store: {len(deriva)}")
    for cid, rot, vp, vn in deriva:
        print(f"   {cid:<44} {rot}: {vp:.4f} -> {vn:.4f}")
    print(f"F7 com perna DESCOBERTA pelo piso da PROPRIA prova: {len(desc)}")
    for cid, rot, vn, bar in desc:
        print(f"   {cid:<44} {rot}: {vn:.4f} > {bar:.4f}")
    print("\nLEITURA: deriva sem descobrir perna = registro envelhecido (o")
    print("numero da prova nao e' mais o do store, mas a prova ainda vale).")
    print("Perna descoberta = a prova nao cobre mais o defeito.")
    out["_deriva"] = [list(t) for t in deriva]
    out["_descobertas"] = [list(t) for t in desc]
    if a.json:
        a.json.write_text(json.dumps(out, indent=1, default=float),
                          encoding="utf-8")
        print(f"json -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
