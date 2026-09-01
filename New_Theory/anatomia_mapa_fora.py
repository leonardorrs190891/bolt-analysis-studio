# -*- coding: utf-8 -*-
"""Mapa das curvas FORA do tripe — o instrumento de priorizacao da campanha
FAXINA-E-ANATOMIA (charter, secao homonimo). So-leitura, segundos.

Para cada curva fora: classe da triagem + tres assinaturas baratas lidas dos
vetores do store (sem re-simular):

  fra_vies    |vies| / MAE  — >0,8 com <=1 cruzamento = NIVEL PURO, a classe
              que em 2026-08-05 rendeu +5 no censo por correcao de DADO/INPUT
              (D-S, D-R, erratum de drive), nao de modelo.
  cruz        cruzamentos de sinal do residuo — muitos = curvatura/ruido.
  std_passos  desvio-padrao dos passos consecutivos do DADO na regiao de maior
              queda — <1e-3 = assinatura de RETA tracada a mao (a steel_t10
              dava 5e-5 onde o paper mostra colapso convexo).

⚠️ Use `rh.limite_sres`/`T.classificar`, nunca reimplemente a regua (armadilha
medida em 2026-07-30). Os totais daqui NAO sao o censo oficial: as n<6
(sigma nao-julgavel) passam as reguas cruas e este mapa nao as separa.

    py -3.12 New_Theory/anatomia_mapa_fora.py [--saida arquivo.txt]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

import regra_de_parada_triagem as T                                # noqa: E402
import bolt_analysis_studio.validation.report_html as rh           # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", type=Path)
    a = ap.parse_args()

    store = json.loads(T.STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    pisos = T.pisos_medidos(store, recs)
    exc = set(rh._EXCECOES)

    out: dict = {}
    for cid, r in store.items():
        if not r.get("ok") or cid not in recs:
            continue
        src = recs[cid].source
        if not rh.caso_comparavel(src, cid):
            continue
        lim = float(rh.limite_sres(src, pisos))
        if r["mae"] <= 0.05 and r["maxerr"] <= 0.10 and r["resid_std"] <= lim:
            continue
        p = (pisos.get("por_fonte") or {}).get(src)
        cls = T.classificar(cid, r, src, None if not p else float(p[2]), exc)
        mp = np.asarray(r.get("metric_pred") or [], float)
        md = np.asarray(r.get("metric_data") or [], float)
        linha = dict(cls=cls, mae=r["mae"], mx=r["maxerr"], sd=r["resid_std"],
                     lim=lim)
        if len(mp) > 3 and len(mp) == len(md):
            res = mp - md
            b = float(res.mean())
            linha["vies"] = b
            linha["fra_vies"] = abs(b) / max(r["mae"], 1e-9)
            linha["cruz"] = int(np.sum(res[1:] * res[:-1] < 0))
            dif = np.diff(md)
            if len(dif) >= 5:
                k = int(np.argmin(dif))
                linha["std_passos"] = float(np.std(dif[max(0, k - 3):k + 4]))
        out.setdefault(src, []).append((cid, linha))

    sai = [f"{'fonte':20s} {'fora':>4s}  classes"
           f"{'':34s}{'vies>80%':>9s} {'reta':>5s}  piso?"]
    tot_v, tot_r = [], []
    for src in sorted(out, key=lambda s: -len(out[s])):
        L = out[src]
        cls: dict = {}
        for _, l in L:
            cls[l["cls"]] = cls.get(l["cls"], 0) + 1
        nv = [c for c, l in L
              if l.get("fra_vies", 0) > 0.8 and l.get("cruz", 99) <= 1]
        nr = [c for c, l in L if l.get("std_passos", 1) < 1e-3]
        tot_v += nv; tot_r += nr
        tem = "sim" if (pisos.get("por_fonte") or {}).get(src) else "NAO"
        ctxt = ", ".join(
            f"{k.replace('classe_parada(aceleracao tardia)', 'parada')}={v}"
            for k, v in sorted(cls.items()))
        sai.append(f"{src:20s} {len(L):4d}  {ctxt:40s} {len(nv):8d} "
                   f"{len(nr):5d}  {tem}")
    n_fora = sum(len(v) for v in out.values())
    sai.append(f"\nTOTAIS: fora={n_fora} · vies-dominadas={len(tot_v)} · "
               f"assinatura de reta={len(tot_r)}")
    sai.append("\nvies-dominadas (fila natural da FAXINA):")
    sai.extend(f"  {c}" for c in sorted(tot_v))
    sai.append("\nassinatura de RETA no dado:")
    sai.extend(f"  {c}" for c in sorted(tot_r))
    txt = "\n".join(sai)
    if a.saida:
        a.saida.write_text(txt, encoding="utf-8")
    print(txt.encode("ascii", "replace").decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
