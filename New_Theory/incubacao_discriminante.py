# -*- coding: utf-8 -*-
"""Teste DISCRIMINANTE da incubacao (`slip_onset_W`) — candidato da atividade F.

SO-LEITURA: nada e' escrito no store nem em adopted_configs.json.

A F mediu que a 2a forma que falta no cluster DERIVA e' CURVATURA (joelho no lugar
errado) e que, no CHU, a curvatura ORDENA PELA AMPLITUDE: |a| medio 0,75 em
D=0,4 mm contra 0,08 em D>=0,5 mm (razao 9,9x). O candidato nomeado e' a
incubacao de estagio 1, que JA existe no engine e esta DESLIGADA
(`slip_onset_W = 0` => gate de Hill identico a 1).

PREDICAO, escrita ANTES desta medicao (chu_segundo_defeito_resultado.md §4):

    W_slip_acc += 4*mu*F_0*slip por ciclo, entao o numero de ciclos para o gate
    abrir escala como W_onset/(4*mu*F_0*slip). Em amplitude PEQUENA o gate demora
    muito => plato longo, joelho tardio. Em amplitude GRANDE abre no 1o ciclo =>
    INERTE.

    => ligar a incubacao deve reduzir |a| nas curvas de D=0,4 mm e ser ~inerte
       nas de D=1,0 mm.

DISCRIMINANTE (e' o que distingue esta forma de uma alavanca qualquer): um
mecanismo de forma que NAO seja dirigido por trabalho de slip nao ordenaria pela
amplitude. Se a incubacao reduzir |a| em TODAS por igual, o mecanismo alegado esta
errado mesmo que as metricas melhorem.

FALSIFICACAO PARCIAL ja declarada: a mesma fisica preveria |a| caindo com F_0
(mais pre-carga => mais trabalho por ciclo => gate abre antes), e o dado do CHU
NAO mostra essa ordem (0,94/0,47/0,85 em 49/61/73 kN). A tensao fica registrada.

    py -3.12 New_Theory/incubacao_discriminante.py [--quick]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation import report_html as rh                  # noqa: E402
from bolt_analysis_studio.validation import runner as rn                       # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records, record  # noqa: E402

# W_slip_acc ~ 4*mu*F0*slip ~ 6 J/ciclo na escala do CHU (mu 0,15 · F0 50 kN ·
# slip 0,2 mm) => esta grade cobre platos de ~20 a ~20 000 ciclos.
GRADE_W = [0.0, 1e2, 1e3, 1e4, 1e5]
_EXTRA: dict = {}


def _ganchos() -> None:
    _o = rn._effective_overrides
    rn._effective_overrides = lambda rec, base: {**_o(rec, base), **_EXTRA}


def descrever(cid: str, W: float) -> dict:
    """Roda e devolve as 3 pernas + o coeficiente quadratico `a` do residuo."""
    _EXTRA.clear()
    if W > 0.0:
        _EXTRA["slip_onset_W"] = W
    r = rn.simulate_case(record(cid), n_cap=200_000)
    mp = np.asarray(r.metric_pred, float)
    md = np.asarray(r.metric_data, float)
    mx = np.asarray(r.metric_x, float)
    e = mp - md
    s = (mx - mx[0]) / ((mx[-1] - mx[0]) or 1.0)
    quad = np.polyfit(s, e, 2)
    return dict(W=W, mae=float(r.mae), mx=float(r.maxerr), sd=float(r.resid_std),
                a=float(quad[0]), beta=float(np.polyfit(s, e, 1)[0]))


def main() -> int:
    _ganchos()
    grade = GRADE_W[:3] if "--quick" in sys.argv else GRADE_W
    casos = [r for r in all_records() if r.source == "CHU_2026"
             and re.search(r"D\dp\dmm", r.case_id)]
    print("TESTE DISCRIMINANTE DA INCUBACAO — slip_onset_W (probe, so-leitura)")
    print(f"  regua: res.max<={rh.META_MAX} MAE<={rh.META_MAE} sigma<={rh.META_SRES}")
    print("  PREDICAO: |a| cai em D=0,4mm e fica ~inerte em D=1,0mm\n")
    saida: dict = {}
    for rec in casos:
        cid = rec.case_id
        m = re.search(r"D(\d)p(\d)mm", cid)
        D = float(f"{m.group(1)}.{m.group(2)}") if m else float("nan")
        linhas = [descrever(cid, W) for W in grade]
        nom = linhas[0]
        melhor = min(linhas[1:], key=lambda d: abs(d["a"])) if len(linhas) > 1 else nom
        red = 1.0 - abs(melhor["a"]) / max(abs(nom["a"]), 1e-12)
        saida[cid] = dict(D_mm=D, linhas=linhas)
        print(f"  {cid[:38]:38s} D={D:.1f}mm")
        for d in linhas:
            tag = "nominal" if d["W"] == 0 else f"W={d['W']:.0e}"
            ok = (d["mx"] <= rh.META_MAX and d["mae"] <= rh.META_MAE
                  and d["sd"] <= rh.META_SRES)
            print(f"      {tag:10s} a={d['a']:+6.3f} beta={d['beta']:+6.3f} | "
                  f"MAE {d['mae']:.4f} res.max {d['mx']:.4f} sigma {d['sd']:.4f}"
                  f"{'  PASSA' if ok else ''}")
        print(f"      -> melhor |a|: {abs(melhor['a']):.3f} contra {abs(nom['a']):.3f} "
              f"nominal = reducao de {100*red:+.0f}%\n")
    # o discriminante: a reducao tem de DEPENDER da amplitude
    print("DISCRIMINANTE — a reducao de |a| ordena pela amplitude?")
    print(f"  {'curva':38s} {'D mm':>5s} {'|a| nom':>8s} {'|a| melhor':>11s} {'reducao':>8s}")
    por_D: dict[float, list[float]] = {}
    for cid, v in saida.items():
        nom, resto = v["linhas"][0], v["linhas"][1:]
        mel = min(resto, key=lambda d: abs(d["a"])) if resto else nom
        red = 1.0 - abs(mel["a"]) / max(abs(nom["a"]), 1e-12)
        por_D.setdefault(v["D_mm"], []).append(red)
        print(f"  {cid[:38]:38s} {v['D_mm']:5.1f} {abs(nom['a']):8.3f} "
              f"{abs(mel['a']):11.3f} {100*red:7.0f}%")
    peq = [x for D, v in por_D.items() if D <= 0.4 for x in v]
    gra = [x for D, v in por_D.items() if D >= 0.5 for x in v]
    if peq and gra:
        print(f"\n  reducao media em D<=0,4mm: {100*np.mean(peq):+.0f}%   "
              f"em D>=0,5mm: {100*np.mean(gra):+.0f}%")
        if np.mean(peq) > np.mean(gra) + 0.15:
            print("  => PREDICAO CONFIRMADA: a incubacao morde onde a assinatura previu.")
        elif abs(np.mean(peq) - np.mean(gra)) <= 0.15:
            print("  => PREDICAO FALSIFICADA: reduz por igual => o mecanismo alegado")
            print("     (gate dirigido por trabalho de slip) NAO e' o que age.")
        else:
            print("  => PREDICAO INVERTIDA: morde mais na amplitude GRANDE.")
    dest = ROOT / "New_Theory" / "incubacao_discriminante.json"
    dest.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\ngravado: {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
