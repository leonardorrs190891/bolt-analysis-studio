# -*- coding: utf-8 -*-
"""Lista as curvas ABERTAS — fora do tripe, sem excecao e sem declaracao.

SO-LEITURA. Nao simula, nao escreve no store.

Por que e' um SCRIPT e nao um documento escrito a mao: a lista muda a cada
assinatura, a cada adocao e a cada re-stamp. Uma tabela digitada envelhece em
silencio — e' o defeito que o `MODEL_LEGITIMACY` §4.43 nomeia e que
`tests/test_meta_numeros_nao_envelhecem.py` existe para impedir. Aqui a lista e'
RECOMPUTADA do store toda vez.

⚠️ REGRA que este arquivo obedece e que ja foi violada antes: **nunca
reimplemente a regra do limite**. O tripe se decide por `rh.limite_sres`,
`rh.sres_para_censo` e `rh.caso_comparavel` — os mesmos helpers que o report e a
triagem usam. Uma 2a implementacao ja fez a triagem publicar 105/98 sob a regua
vencida em vez de 124/78.

    py -3.12 New_Theory/lista_abertas.py [--csv] [--md]

Saidas opcionais: `New_Theory/lista_abertas.csv` e `New_Theory/lista_abertas.md`.
"""
from __future__ import annotations

import csv
import inspect
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

from bolt_analysis_studio.validation import report_html as rh              # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records      # noqa: E402
from bolt_analysis_studio.validation.runner import CaseResult              # noqa: E402
import regra_de_parada_triagem as T                                        # noqa: E402

STORE = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"


def formas_nomeadas() -> dict:
    """Le o `_FORMA_NOMEADA` do fonte da triagem — ele e' LOCAL a `main()`.

    ⚠️ `getattr(T, "_FORMA_NOMEADA", {})` devolve **{} em silencio** (erro que eu
    cometi ao montar esta lista pela 1a vez, e que fez a sonda publicar
    "0 de 21 com forma nomeada" quando eram 18). Mesmo leitor que a guarda
    `test_forma_nomeada_cita_a_curva` usa.
    """
    m = re.search(r"_FORMA_NOMEADA = \{(.*?)\n    \}", inspect.getsource(T.main), re.S)
    if not m:
        m = re.search(r"_FORMA_NOMEADA = \{(.*?)\}", inspect.getsource(T.main), re.S)
    if not m:
        raise RuntimeError("`_FORMA_NOMEADA` sumiu de `regra_de_parada_triagem.main`")
    return dict(re.findall(r'"([A-Za-z0-9_.]+)"\s*:\s*"([^"]+)"', m.group(1), re.S))


def coletar() -> list[dict]:
    recs = {r.case_id: r for r in all_records()}
    store = json.loads(STORE.read_text(encoding="utf-8"))
    store = store.get("cases", store)
    pisos = T.pisos_medidos(store, recs)
    formas = formas_nomeadas()
    exc = set(rh._EXCECOES)
    out = []
    for cid, raw in store.items():
        rec = recs.get(cid)
        if rec is None or not rh.caso_comparavel(rec.source, cid):
            continue
        r = CaseResult.from_dict(raw)
        if not r.ok:
            continue
        sd = rh.sres_para_censo(r)
        lim = rh.limite_sres(rec.source, pisos)
        passa = (sd is not None and r.maxerr <= rh.META_MAX
                 and r.mae <= rh.META_MAE and sd <= lim)
        if passa or cid in exc or cid in rh._DECLARADAS:
            continue
        mult = {
            "MAE": r.mae / rh.META_MAE,
            "res.max": r.maxerr / rh.META_MAX,
            # sigma nao-julgavel (n<6) nao tem multiplo — `inf` seria mentira
            # aritmetica; marca-se como None e a perna que manda vira "n<6".
            "sigma": (sd / lim) if sd is not None else None,
        }
        viola = {k: (v is None or v > 1.0) for k, v in mult.items()}
        conhecidos = {k: v for k, v in mult.items() if v is not None}
        manda = "n<6" if mult["sigma"] is None else max(conhecidos, key=conhecidos.get)
        out.append(dict(
            fonte=rec.source, cid=cid, mae=r.mae, maxerr=r.maxerr,
            sigma=sd, limite_sigma=lim, n_pontos=len(r.metric_x or []),
            mult_mae=mult["MAE"], mult_max=mult["res.max"], mult_sigma=mult["sigma"],
            manda=manda, so_sigma=(viola["sigma"] and not viola["MAE"]
                                   and not viola["res.max"]),
            camada=T.classificar(cid, raw, rec.source,
                                 T.piso_da_fonte(pisos, rec.source), exc),
            forma_nomeada=formas.get(cid, ""),
        ))
    out.sort(key=lambda d: (d["fonte"], -max(x for x in
                                             (d["mult_mae"], d["mult_max"],
                                              d["mult_sigma"] or 0) if x)))
    return out


def _tabela(rows) -> str:
    L = ["| fonte | curva | MAE | res.máx | σ_res | manda | só σ | camada | forma nomeada |",
         "|---|---|---:|---:|---:|---|:--:|---|---|"]
    for d in rows:
        sg = "n<6" if d["sigma"] is None else f"{d['sigma']:.4f}"
        sgm = "—" if d["mult_sigma"] is None else f"{d['mult_sigma']:.1f}×"
        L.append(
            f"| {d['fonte']} | `{d['cid']}` | {d['mae']:.4f} ({d['mult_mae']:.1f}×) "
            f"| {d['maxerr']:.4f} ({d['mult_max']:.1f}×) | {sg} ({sgm}) "
            f"| {d['manda']} | {'✅' if d['so_sigma'] else ''} | {d['camada']} "
            f"| {d['forma_nomeada'] or '—'} |")
    return "\n".join(L)


def main() -> None:
    rows = coletar()
    por_fonte = defaultdict(int)
    for d in rows:
        por_fonte[d["fonte"]] += 1
    manda = defaultdict(int)
    camada = defaultdict(int)
    for d in rows:
        manda[d["manda"]] += 1
        camada[d["camada"]] += 1
    so_sig = [d for d in rows if d["so_sigma"]]
    perto = sorted((d for d in rows if d["mult_sigma"]),
                   key=lambda d: max(d["mult_mae"], d["mult_max"], d["mult_sigma"]))[:5]

    print(f"ABERTAS (fora do tripe, sem excecao, sem declaracao): {len(rows)}")
    print("  por fonte:", dict(sorted(por_fonte.items(), key=lambda t: -t[1])))
    print("  perna que MANDA:", dict(manda))
    print("  camada da triagem:", dict(camada))
    print(f"  reprovam SO' no sigma_res: {len(so_sig)}")
    print(f"  com forma nomeada: {sum(1 for d in rows if d['forma_nomeada'])} de {len(rows)}")
    print("\n  as 5 MAIS PERTO de fechar (menor pior-perna):")
    for d in perto:
        pior = max(d["mult_mae"], d["mult_max"], d["mult_sigma"])
        print(f"     {pior:4.2f}x  {d['cid'][:46]:46s} manda {d['manda']}")

    if "--md" in sys.argv or "--csv" not in sys.argv:
        md = ROOT / "New_Theory" / "lista_abertas.md"
        md.write_text(
            "# Curvas ABERTAS — fora do tripé, sem exceção e sem declaração\n\n"
            f"**{len(rows)} curvas.** Gerado por `py -3.12 New_Theory/lista_abertas.py`; "
            "recomputado do store a cada execução — **não editar à mão**.\n\n"
            "Régua: res.máx ≤ 0,10 · MAE ≤ 0,05 · σ_res ≤ `max(0,025; piso da fonte)`. "
            "Os múltiplos são do limite que de fato vale para aquela fonte.\n\n"
            + _tabela(rows) + "\n\n"
            f"- reprovam **só** no σ_res: **{len(so_sig)}**\n"
            f"- perna que manda: " + " · ".join(f"{k} {v}" for k, v in manda.items()) + "\n"
            f"- camada: " + " · ".join(f"{k} {v}" for k, v in camada.items()) + "\n"
            f"- com forma nomeada: {sum(1 for d in rows if d['forma_nomeada'])}"
            f" de {len(rows)}\n", encoding="utf-8", newline="")
        print(f"\nescrito: {md}")

    if "--csv" in sys.argv or "--md" not in sys.argv:
        cs = ROOT / "New_Theory" / "lista_abertas.csv"
        with open(cs, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"escrito: {cs}")


if __name__ == "__main__":
    main()
