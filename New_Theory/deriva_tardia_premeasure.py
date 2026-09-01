# -*- coding: utf-8 -*-
"""Premeasure ANALITICO da deriva tardia — onset de creep per-par (t_0).

Candidato (achado do D2' re-executado): o residuo das curvas longas deriva
POSITIVO alem de 200k (modelo satura, dado segue caindo). LIU_2016: creep e'
100% do canal tardio mas entrega 45-64% da queda do dado (log com t_0=1s e'
front-loaded — resta ~13% de crescimento entre 200k e 1M, o residuo dobra).
ZHANG_2018: C_creep=0.0 adotado => taxa tardia identicamente nula.

A forma NAO e' nova: delta_creep = C*F0*ln(t/t_0+1) ja' esta' no engine e t_0
e' um campo per-par ("onset viscoelastico, livel do joelho"). Em ciclos:
ln((N+N0)/(n0+N0)) com N0 = t_0*freq — com N0 grande a lei e' quase-linear
cedo e poe a perda NA CAUDA. Este script LE (A, N0) do residuo (L24: ler em
vez de fitar as curvas), so nas curvas de LEITURA do split mecanico
(calibration.holdout), e PREVE analiticamente sigma'/MAE'/mx' de TODAS as
curvas das duas fontes (preview do gate de acervo) — zero simulacao.

Aproximacao declarada: superposicao — somar a perda de creep re-ancorada em
n0 ao residuo ignora o acoplamento de 2a ordem via F0 (creep tira F0 =>
wear/loosening desaceleram). O executor mede exatamente este erro (gate F3).

Modelo analitico por curva:
  e'(N) = e(N) + [c(N) - c(n0)] - A*[g(N;N0) - g(n0;N0)]
  e   = pred - data (grade da metrica, ja alinhada/trimada)
  c   = contribuicao CUMULATIVA de creep atual (decomp do store, interp)
  g   = ln(N + N0)
  A   = k_eff*C' (fracao de F0 por unidade de log; F0 cancela na razao)
(A, N0) COMPARTILHADOS por fonte, minimizando a soma de sigma'^2 nas LEITURAS.

Saida: New_Theory/deriva_tardia_premeasure.json + tabela ASCII.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.report_html as rh   # noqa: E402
from bolt_analysis_studio.calibration.holdout import (      # noqa: E402
    split_por_criterio)
from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402
from bolt_analysis_studio.validation.store import ValidationStore      # noqa: E402

CUT = 200_000.0          # so para relatorio da cauda; o fit usa a curva toda
N0_GRID = np.logspace(1.0, 6.5, 45)   # ciclos (desce ate ~t_0 default)
TOL = 0.01               # mesmo +0.01 dos gates de acervo
FONTES = ("LIU_2016", "ZHANG_2018")   # mos2 e' config SEPARADA — nao muda


def _vetores(st, cid):
    r = st.get(cid)
    if r is None:
        return None
    d = r.to_dict()
    x = np.asarray(r.metric_x, float)
    e = np.asarray(r.metric_pred, float) - np.asarray(r.metric_data, float)
    # contribuicao cumulativa de creep ATUAL, interpolada na grade da metrica
    cyc = np.asarray(d.get("cycles") or [], float)
    dec = (d.get("decomp") or {}).get("creep")
    if dec is not None and cyc.size:
        c = np.interp(x, cyc, np.asarray(dec, float))
    else:
        c = np.zeros_like(x)
    return {"x": x, "e": e, "c": c, "mae": r.mae, "mx": r.maxerr,
            "sd": r.resid_std}


def _g(x, n0_al, N0):
    return np.log(x + N0) - np.log(n0_al + N0)


def _apos(v, A, N0):
    x = v["x"]
    return v["e"] + (v["c"] - v["c"][0]) - A * _g(x, x[0], N0)


def _A_otimo(vs_reads, N0):
    """A>=0 fechado que minimiza a soma de sigma'^2 nas leituras, dado N0."""
    num = den = 0.0
    for v in vs_reads:
        base = v["e"] + (v["c"] - v["c"][0])
        h = _g(v["x"], v["x"][0], N0)
        bb, hh = base - base.mean(), h - h.mean()
        num += float(bb @ hh)
        den += float(hh @ hh)
    return max(0.0, num / den) if den else 0.0


def _J(vs, A, N0):
    return sum(float(np.std(_apos(v, A, N0))) ** 2 for v in vs)


def _viavel(vs_all, A, N0):
    """Gate de acervo PREVISTO: nenhuma curva da fonte piora > TOL em
    nenhuma das tres pernas (mesma tolerancia do gate real)."""
    for v in vs_all:
        e2 = _apos(v, A, N0)
        if (float(np.std(e2)) > v["sd"] + TOL
                or float(np.mean(np.abs(e2))) > v["mae"] + TOL
                or float(np.max(np.abs(e2))) > v["mx"] + TOL):
            return False
    return True


def _fit_fonte(vs_reads, vs_all):
    """Dois otimos: LIVRE (so leituras) e VIAVEL (s.t. acervo previsto).

    A restricao usa as curvas de ACERVO — declarada aqui, antes de executar;
    as HELD ficam fora do objetivo E da restricao (generalizacao pura)."""
    livre = viavel = None
    for N0 in N0_GRID:
        A = _A_otimo(vs_reads, N0)
        J = _J(vs_reads, A, N0)
        if livre is None or J < livre[2]:
            livre = (A, float(N0), J)
        if _viavel(vs_all, A, N0) and (viavel is None or J < viavel[2]):
            viavel = (A, float(N0), J)
    return livre, viavel


def main() -> int:
    st = ValidationStore()
    recs = {f: sorted(r.case_id for r in all_records() if r.source == f)
            for f in FONTES}

    # ---- splits mecanicos (criterio de RESOLUCAO DO DADO, nunca de erro) ---
    def _tail_pts(cid):
        v = _vetores(st, cid)
        return int((v["x"] > CUT).sum()) if v else 0

    splits = {}
    # ZHANG_2018: so quem RESOLVE a cauda pode ler o onset (>=4 pts alem do
    # corte); as de cauda esparsa seguram.
    splits["ZHANG_2018"] = split_por_criterio(
        recs["ZHANG_2018"], lambda c: _tail_pts(c) >= 4,
        "resolucao da cauda: >=4 pontos alem de 200k le; cauda esparsa segura")
    # LIU_2016: todas resolvem a cauda -> segurar por OUTRO eixo declarado
    # (doc do modulo): primeiro-de-cada-par por IDENTIDADE do dado
    # (indice de replica run1<run2; menor rugosidade m30<m40).
    fila_liu = ["liu2016wear_fig7_run1_1e6cyc", "liu2016wear_fig7_run2_5e6cyc",
                "liu2016wear_fig9a_m30nm", "liu2016wear_fig9a_m40nm"]
    splits["LIU_2016"] = split_por_criterio(
        fila_liu, lambda c: ("run1" in c) or ("m30nm" in c),
        "primeiro-de-cada-par (replica run1 le / run2 segura; "
        "rugosidade m30nm le / m40nm segura)")

    # ---- fit por fonte nas LEITURAS ----------------------------------------
    out = {"cut": CUT, "n0_grid": [float(N0_GRID[0]), float(N0_GRID[-1])],
           "fontes": {}}
    pares = [(r.source, st.get(r.case_id)) for r in all_records()
             if st.get(r.case_id) is not None]
    pisos = rh._pisos_medidos(pares)

    for fonte in ("LIU_2016", "ZHANG_2018"):
        sp = splits[fonte]
        vs_reads = [v for c in sp.reads if (v := _vetores(st, c))]
        # restricao de viabilidade: TODAS as curvas da fonte MENOS as held
        # (held fora do objetivo E da restricao — generalizacao pura)
        alvo = recs[fonte]
        vs_all = [v for c in alvo if c not in sp.held
                  and (v := _vetores(st, c))]
        livre, viavel = _fit_fonte(vs_reads, vs_all)
        assert livre is not None  # grid nao-vazio garante
        if viavel is None:
            print(f"\n=== {fonte}: NENHUM (A,N0) viavel no grid — candidato "
                  f"morre no preview do acervo (F1)")
            out["fontes"][fonte] = {"livre": livre, "viavel": None}
            continue
        A, N0, J = viavel
        fo = {"split": {"criterio": sp.criterio, "reads": list(sp.reads),
                        "held": list(sp.held)},
              "A": A, "N0_ciclos": N0, "J_reads": J,
              "livre": {"A": livre[0], "N0_ciclos": livre[1],
                        "J_reads": livre[2]},
              "curvas": {}}
        lim_sd = rh.limite_sres(fonte, pisos)
        for cid in alvo:
            v = _vetores(st, cid)
            if v is None:
                continue
            e2 = _apos(v, A, N0)
            papel = ("LE" if cid in sp.reads else
                     "HELD" if cid in sp.held else "acervo")
            fo["curvas"][cid] = {
                "papel": papel,
                "antes": {"mae": v["mae"], "mx": v["mx"], "sd": v["sd"]},
                "depois_prev": {"mae": float(np.mean(np.abs(e2))),
                                "mx": float(np.max(np.abs(e2))),
                                "sd": float(np.std(e2))},
                "lim_sd": lim_sd,
            }
        out["fontes"][fonte] = fo

    p = ROOT / "New_Theory" / "deriva_tardia_premeasure.json"
    p.write_text(json.dumps(out, indent=1), encoding="utf-8")

    for fonte, fo in out["fontes"].items():
        if fo.get("viavel", 1) is None:
            continue
        lv = fo["livre"]
        print(f"\n=== {fonte}  VIAVEL A={fo['A']:.5f} N0={fo['N0_ciclos']:.0f}"
              f"  (livre: A={lv['A']:.5f} N0={lv['N0_ciclos']:.0f} "
              f"J={lv['J_reads']:.6f} vs {fo['J_reads']:.6f})")
        print(f"    split: {fo['split']['criterio']}")
        print(f"{'curva':40s} {'papel':6s} {'sd antes':>9s} {'sd prev':>9s} "
              f"{'mae prev':>9s} {'mx prev':>9s} {'lim_sd':>7s}")
        for cid, cc in fo["curvas"].items():
            a, dp = cc["antes"], cc["depois_prev"]
            print(f"{cid[:40]:40s} {cc['papel']:6s} {a['sd']:9.4f} "
                  f"{dp['sd']:9.4f} {dp['mae']:9.4f} {dp['mx']:9.4f} "
                  f"{cc['lim_sd']:7.4f}")
    print("\n(previsao ANALITICA por superposicao; o executor mede o erro "
          "dela — gate F3)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
