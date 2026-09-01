# -*- coding: utf-8 -*-
"""PREMEASURE da re-digitalizacao do LU_2024 — o que ainda NAO e' prereg.

## O que ja esta estabelecido (medido, nao suposto)

* A **figura** 18a reproduz a Tabela 8 a +-0,002 e a **figura** 20a reproduz a
  Tabela 9 a +-0,007, cada uma com seu controle
  (`lu2024_fig18_extracao_resultado.md`, `lu2024_piso_viesado_resultado.md`).
* Logo qualquer desvio de uma CSV contra a tabela e' **da CSV**. Ranking no
  c10: `fig18_amp2p0` +0,0792 · `fig20_T22Nm` +0,0724 · `fig18_amp1p0` +0,0439
  · `fig20_T28Nm` +0,0274 · `fig20_T16Nm` +0,0160 · `fig20_T10Nm` +0,0115 ·
  `fig18_amp0p5` +0,0100.
* O par `fig18_amp1p0` <-> `fig20_T22Nm` e' o MESMO ensaio e da o "piso de
  digitalizacao" da fonte: as duas concordam entre si (MAE 0,0127) e erram
  JUNTAS contra o impresso.

## O que este script mede

Substitui a CSV pela leitura da FIGURA **nos mesmos ciclos** da CSV atual
(so' o y muda — isola a correcao) e re-simula. Reporta, por curva:
antes -> depois nas 3 pernas, mudanca de estatuto, e o efeito no PISO da fonte.

⚠️ O 1o ponto **nao** vem do pixel: o c1 tem residuo declarado (+0,027..+0,047
na Fig. 18; +0,019..+0,021 na Fig. 20) que os controles nao explicam. Ele vem
da **tabela impressa**, que e' o dado primario.

Nao adota, nao escreve CSV, nao toca o store.

    py -3.12 New_Theory/lu2024_redigit_premeasure.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.inputs as vin                 # noqa: E402
import bolt_analysis_studio.validation.runner as rn                  # noqa: E402
from bolt_analysis_studio.validation import report_html as rh        # noqa: E402
from bolt_analysis_studio.validation.case_registry import (          # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.runner import CaseResult        # noqa: E402

# case_id -> (json, chave, ancora da tabela no ciclo 1)
ALVOS = {
    "lu2024_M8_fig18_amp0p5":  ("lu2024_fig18_extrai.json", "0p5",  0.638),
    "lu2024_M8_fig18_amp1p0":  ("lu2024_fig18_extrai.json", "1p0",  0.632),
    "lu2024_M8_fig18_amp2p0":  ("lu2024_fig18_extrai.json", "2p0",  0.498),
    "lu2024_M8_fig20_T10Nm":   ("lu2024_fig20_extrai.json", "T10Nm", 0.638),
    "lu2024_M8_fig20_T16Nm":   ("lu2024_fig20_extrai.json", "T16Nm", 0.641),
    "lu2024_M8_fig20_T22Nm":   ("lu2024_fig20_extrai.json", "T22Nm", 0.632),
    "lu2024_M8_fig20_T28Nm":   ("lu2024_fig20_extrai.json", "T28Nm", 0.617),
}
_NOVA: dict = {}
_orig_load = vin.load_full_curve


def _load(rel):
    cyc, rat = _orig_load(rel)
    for cid, (x, y) in _NOVA.items():
        if Path(rel).name == Path(_CSV[cid]).name:
            return np.asarray(x, float), np.asarray(y, float)
    return cyc, rat


_CSV: dict = {}
vin.load_full_curve = _load
rn.load_full_curve = _load


def _tri(r, lim):
    sd = rh.sres_para_censo(r)
    return (r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX
            and sd is not None and sd <= lim)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    recs = {r.case_id: r for r in all_records()}
    for cid in ALVOS:
        _CSV[cid] = recs[cid].csv_path
    store = json.loads((ROOT / "Models" / "CALIBRATION_AND_VALIDATION"
                        / "validation_store.json").read_text(encoding="utf-8"))

    # --- monta as CSVs corrigidas -------------------------------------
    print("CSVs corrigidas (mesmos ciclos, y da FIGURA; c1 da TABELA):\n")
    print(f"{'curva':<30}{'n':>4}{'|dy| med':>10}{'|dy| max':>10}")
    for cid, (jf, key, tab_c1) in ALVOS.items():
        d = json.loads((ROOT / "New_Theory" / jf).read_text(encoding="utf-8"))
        serie = {float(k): float(v) for k, v in d[key]["serie"].items()}
        fx = np.array(sorted(serie))
        fy = np.array([serie[k] for k in fx])
        cyc, rat = _orig_load(_CSV[cid])
        case = recs[cid].validation_case
        off = float(getattr(case, "csv_x_offset", 0.0) or 0.0)
        xs = np.asarray(cyc, float)
        novo = []
        for x, y_old in zip(xs, np.asarray(rat, float)):
            n = x - off                       # ciclo do paper
            if n <= 0:
                novo.append(1.0)              # ancora de pre-ciclagem
            elif n <= 1.0:
                novo.append(tab_c1)           # 1o ponto vem da TABELA
            else:
                novo.append(float(np.interp(n, fx, fy)))
        novo = np.array(novo)
        dy = np.abs(novo - np.asarray(rat, float))
        _NOVA[cid] = (xs, novo)
        # SANIDADE: a CSV corrigida tem de bater a tabela onde a tabela existe.
        # Sem isto, um |dy| grande poderia ser defeito da construcao em vez de
        # correcao — e nao haveria como distinguir.
        xn = xs - off
        chk = []
        for c in (10, 50, 100):
            if c < xn.min() or c > xn.max():
                chk.append("  --")
                continue
            chk.append(f"{float(np.interp(c, xn, novo)):.3f}")
        print(f"{cid[:30]:<30}{len(xs):>4}{dy.mean():>10.4f}{dy.max():>10.4f}"
              f"   c10/c50/c100 = {'/'.join(chk)}")

    # --- re-simula TUDO (o piso e' global a fonte) ---------------------
    print("\nre-simulando o LU_2024 inteiro...", flush=True)
    novos = {}
    for r in all_records():
        if r.source != "LU_2024":
            novos[r.case_id] = CaseResult.from_dict(store[r.case_id])
            continue
        res = rn.simulate_case(record(r.case_id))
        assert res.ok, f"{r.case_id}: {res.error}"
        novos[r.case_id] = res

    pares_v = [(recs[c].source, CaseResult.from_dict(store[c]))
               for c in store if c in recs]
    pares_n = [(recs[c].source, novos[c]) for c in novos if c in recs]
    pv, pn = rh._pisos_medidos(pares_v), rh._pisos_medidos(pares_n)
    Lv, Ln = (rh.limite_sres("LU_2024", pv), rh.limite_sres("LU_2024", pn))
    print(f"\npiso LU  antes {tuple(round(x,4) for x in pv['por_fonte']['LU_2024'])}"
          f"  ->  depois {tuple(round(x,4) for x in pn['por_fonte']['LU_2024'])}")
    print(f"limite_sres(LU)  {Lv:.4f} -> {Ln:.4f}")
    print("familias depois:")
    for f in pn["fam"]:
        if "LU_2024" in str(f[0]).upper():
            rot = str(f[0])[:58].encode("ascii", "replace").decode()
            print(f"   {rot:<58} n={f[1]} MAE {f[2]:.4f} "
                  f"mx {f[3]:.4f} sig {f[4]:.4f}")

    print(f"\n{'curva':<32}{'antes':>24}{'depois':>24}  estatuto")
    out, saldo = [], 0
    for cid in sorted(c for c in novos if recs[c].source == "LU_2024"):
        v = CaseResult.from_dict(store[cid]); n = novos[cid]
        comp = rh.caso_comparavel("LU_2024", cid)
        tv, tn = _tri(v, Lv), _tri(n, Ln)
        if comp and cid not in rh._EXCECOES and cid not in rh._DECLARADAS:
            saldo += int(tn) - int(tv)
        marca = ("ENTRA" if (tn and not tv) else "SAI" if (tv and not tn)
                 else ("tripe" if tn else "-"))
        if not comp:
            marca += " (nao-comp)"
        print(f"{cid[:32]:<32}{v.mae:>8.4f}{v.maxerr:>8.4f}{v.resid_std:>8.4f}"
              f"{n.mae:>8.4f}{n.maxerr:>8.4f}{n.resid_std:>8.4f}  {marca}")
        out.append(dict(cid=cid, antes=[v.mae, v.maxerr, v.resid_std],
                        depois=[n.mae, n.maxerr, n.resid_std],
                        tripe_antes=tv, tripe_depois=tn, comparavel=comp))
    print(f"\nSALDO no censo (so' comparaveis sem estatuto): {saldo:+d}")
    if a.json:
        a.json.write_text(json.dumps(dict(
            curvas=out, piso_antes=list(pv["por_fonte"]["LU_2024"]),
            piso_depois=list(pn["por_fonte"]["LU_2024"]),
            limite_antes=Lv, limite_depois=Ln, saldo=saldo),
            indent=1, default=float), encoding="utf-8")
        print(f"json -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
