# -*- coding: utf-8 -*-
"""Executor do prereg D-H (2026-08-04) — kernel de creep no CACCESE_2009.

As 7 curvas da fonte sao **99,5-99,9 % creep** (relaxacao estatica, 2000 h) e
**6 das 7** tem o MESMO sinal de residuo: modelo devagar demais no inicio,
rapido demais no fim. Curvatura do kernel `C*log(t/t0+1)`, nao erro de curva.

O `creep_mode="saturating"` foi reprovado em 2026-07-30 sobre 18 curvas
TRANSVERSAIS, onde creep nao domina. Aqui e' a populacao oposta.

## A renormalizacao que torna o teste de FORMA (nao de amplitude)

    log:        d(t) = C*F0*log(t/t0+1)      -> fator log(1001) ~ 6,909 no fim
    saturante:  d(t) = C*F0*(1-e^-(t/tc)^a)  -> maximo 1,0*C*F0

Mesmo C nos dois compararia amplitude. Entao:

    C_sat = C_log * log(t_end/t0+1) / (1 - e^-(t_end/tc)^a)

Aritmetica fechada, ZERO numero fitado por curva, perda no ponto final
preservada por construcao. Como sigma_res e' invariante por translacao, ele
mede exatamente o que sobrou: a forma.

    py -3.12 New_Theory/caccese_kernel_creep_exec.py [--json saida.json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.report_html as rh          # noqa: E402
import bolt_analysis_studio.validation.runner as rn               # noqa: E402
from bolt_analysis_studio.validation.case_registry import (       # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

FONTE = "CACCESE_2009"
FORA = ["caccese2009_retighten_19p1mm_no_retighten",
        "caccese2009_tapered_45kN_rep1",
        "caccese2009_tapered_45kN_rep2"]
# `rep1` esta FORA DO ALCANCE por construcao (problema de NIVEL: vies -0.0508,
# residuo negativo em toda a curva; a renormalizacao preserva o total).
# Declarado no prereg antes de medir, nao descoberto depois.
NIVEL = "caccese2009_tapered_45kN_rep1"

_EXTRA: dict = {}
_PC: dict = {}                      # override POR CASO (o C_sat renormalizado)
_orig = rn._effective_overrides


def _patched(rec, base):
    ov = _orig(rec, base)
    if _EXTRA:
        ov = {**ov, **_EXTRA}
        if rec.case_id in _PC:
            ov = {**ov, **_PC[rec.case_id]}
    return ov


rn._effective_overrides = _patched


def _sim(cids, extra=None, pc=None):
    _EXTRA.clear(); _PC.clear()
    if extra:
        _EXTRA.update(extra)
    if pc:
        _PC.update(pc)
    try:
        out = {}
        for cid in cids:
            r = rn.simulate_case(record(cid))
            if not r.ok:
                raise RuntimeError(f"{cid}: {r.error}")
            mp = np.asarray(r.metric_pred, float)
            out[cid] = (float(r.mae), float(r.maxerr), float(r.resid_std),
                        float(1.0 - mp[-1]))          # perda no ponto final
        return out
    finally:
        _EXTRA.clear(); _PC.clear()


def main() -> int:
    st = ValidationStore()
    recs = {r.case_id: r for r in all_records()}
    cids = sorted(c for c in recs
                  if recs[c].source == FONTE and st.get(c) is not None)
    pares = [(r.source, st.get(r.case_id)) for r in all_records()
             if st.get(r.case_id) is not None]
    lim = float(rh.limite_sres(FONTE, rh._pisos_medidos(pares)))

    def passa(v):
        return v[0] <= rh.META_MAE and v[1] <= rh.META_MAX and v[2] <= lim

    base = _sim(cids)
    ruins = [c for c in cids if abs(base[c][0] - st.get(c).mae) > 1e-9]
    if ruins:
        print("!! INSTRUMENTO REPROVADO — baseline != store: " + ",".join(ruins))
        return 2
    print(f"instrumento OK · {len(cids)} curvas · limite sigma {lim:.4f}")

    # t_end e t_0 por caso, do cfg/janela reais (nao digitados)
    info = {}
    for c in cids:
        r = st.get(c)
        x = np.asarray(r.metric_x, float)
        ov = _orig(recs[c], {})
        freq = recs[c].validation_case.frequency_Hz or (1.0 / 3600.0)
        t_end = float(x[-1]) / freq                  # s
        t0 = float(ov.get("t_0") or 1.0)
        C = float(ov.get("C_creep") or 0.0)
        info[c] = dict(t_end=t_end, t0=t0, C=C,
                       f_log=float(np.log(t_end / t0 + 1.0)))
    print(f"  fator log medio: "
          f"{np.mean([i['f_log'] for i in info.values()]):.4f}")
    print(f"  BASELINE: " + " ".join(
        f"{'OK' if passa(base[c]) else 'xx'}" for c in cids)
        + f"   (sigma medio {np.mean([base[c][2] for c in cids]):.4f})")

    out = {"lim": lim, "base": base, "grade": []}
    melhor = None
    for mult in (1.0, 10.0, 100.0):
        for a in (0.15, 0.2, 0.3, 0.4, 0.6, 1.0):
            pc = {}
            for c in cids:
                i = info[c]
                tc = mult * i["t_end"]
                sat = 1.0 - np.exp(-((i["t_end"] / tc) ** a))
                pc[c] = {"C_creep": i["C"] * i["f_log"] / sat,
                         "creep_t_c": tc}
            cur = _sim(cids, {"creep_mode": "saturating",
                              "creep_alpha_sat": a}, pc)
            # G0: a perda no ponto final tem de ser preservada (<=2%)
            dfin = max(abs(cur[c][3] - base[c][3]) / max(base[c][3], 1e-9)
                       for c in cids)
            n_sig = sum(1 for c in cids if cur[c][2] < base[c][2] - 1e-9)
            piores = {c: [round(cur[c][i] - base[c][i], 4) for i in range(3)]
                      for c in cids
                      if max(cur[c][i] - base[c][i] for i in range(3)) > 0.010}
            saiu = [c for c in cids if passa(base[c]) and not passa(cur[c])]
            fecha = [c for c in FORA if passa(cur[c])]
            g0 = dfin <= 0.02
            g1 = n_sig == len(cids)
            g2 = (not piores) and (not saiu)
            ok = g0 and g1 and g2 and fecha
            print(f"\n  alpha={a:<5g} t_c={mult:g}x t_end   "
                  f"G0 dfin_max {100*dfin:5.1f}%{'' if g0 else '  <<FORA de 2%'}")
            print(f"    G1 sigma cai em {n_sig}/{len(cids)}   "
                  f"sigma medio {np.mean([cur[c][2] for c in cids]):.4f} "
                  f"(base {np.mean([base[c][2] for c in cids]):.4f})")
            print(f"    G2 piora>0.010 {piores or 'nenhuma'}  ·  saiu do tripe "
                  f"{saiu or 'nenhuma'}")
            print(f"    G3 fecham das 3 fora: {[c.split('_',1)[1][:22] for c in fecha] or 'nenhuma'}")
            out["grade"].append(dict(alpha=a, tc_mult=mult, dfin=dfin,
                                     n_sig=n_sig, piores=piores, saiu=saiu,
                                     fecha=fecha, ok=bool(ok),
                                     sig={c: cur[c][2] for c in cids}))
            if ok and melhor is None:
                melhor = (a, mult)

    print("\n" + "=" * 70)
    g1ok = [g for g in out["grade"] if g["n_sig"] == len(cids) and g["dfin"] <= 0.02]
    if melhor:
        print(f"VEREDICTO: ADOTA creep_mode=saturating, alpha={melhor[0]}, "
              f"t_c={melhor[1]:g}x t_end (+ C_creep renormalizado por aritmetica)")
    elif not g1ok:
        print("VEREDICTO: FALSIFICADO — nao existe (alpha,t_c) que reduza o "
              "sigma nas 7. A curvatura NAO e' do kernel; a reprovacao de "
              "2026-07-30 vale tambem na populacao creep-dominada.")
    else:
        print(f"VEREDICTO: NAO ADOTA (forma certa, ganho nulo) — {len(g1ok)} "
              f"celulas reduzem o sigma nas 7, nenhuma fecha curva.")
        b = min(g1ok, key=lambda g: np.mean(list(g["sig"].values())))
        print(f"  melhor forma: alpha={b['alpha']} t_c={b['tc_mult']:g}x "
              f"sigma medio {np.mean(list(b['sig'].values())):.4f}")
    print(f"  (declarado antes de medir) `{NIVEL}` esta fora do alcance: "
          f"e' NIVEL, e a renormalizacao preserva o total.")
    if "--json" in sys.argv:
        dest = Path(sys.argv[sys.argv.index("--json") + 1])
        dest.write_text(json.dumps(out, indent=1, default=float),
                        encoding="utf-8")
        print(f"gravado: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
