# -*- coding: utf-8 -*-
"""Premeasure do graded_scrit no CHU_2026 (bifurcacao de limiar, membro
nunca sondado da classe "taxa dependente do estado acumulado").

ASSINATURA DO DEFEITO (medida do store, 2026-07-30):
  o modelo tem o MESMO shape de colapso em todas as amplitudes (fracao da
  perda na 2a metade ~0.26-0.28), o dado varia: D0.4 perde SUSTENTADO
  (0.51-0.71, quase-linear), D0.7 perde tudo CEDO (0.02). O kernel de torque
  bifurca arrest/runaway; o regime intermediario nao existe no engine. O teto
  da familia aditiva ja PROVOU que canal lento aditivo nao fecha CHU
  (fila_teto_log_onset.json) — a forma tem de ser multiplicativa/limiar.

CANDIDATO: loose_rate_mode="graded_scrit" (default-inerte no engine):
  d_theta = gates * k_loose_graded * max(0, slip - s_crit_loose)/(d_2/2)
  - sub-critico => zero  (test1 D0.3 arresta SEM o pin per_case
    loose_arrest_floor=0.9876 — física no lugar de pino ad-hoc)
  - taxa ~ excesso => D0.4 (excesso pequeno) sustentado; D0.7 rapido
  - sem runaway; colapso quase-linear (a forma que o dado D0.4 mostra)

PROVENIENCIA de s_crit_loose: BRACKET por identidade do dado —
  slip(D0.3) <= s_crit < slip(D0.4) (test1 arresta, test2 colapsa).
  O bracket e' medido com sondas curtas (50 ciclos) lendo o slip resolvido.

SPLIT (resolucao/identidade do dado, nunca erro): LE = primeiro teste de
cada nivel de amplitude com colapso (test2 D0.4, test3 D0.5, test4 D0.7,
test5 D1.0); HELD = test7, test8, test9, test6_repeat; test1 fica de fora
da leitura (sub-critico por construcao — ele so participa dos gates).

Este script: (1) sonda o bracket; (2) grade (s_crit, k_loose_graded) SO nas
4 leituras; (3) melhor ponto por J = soma sigma'^2 das leituras sujeito a
nenhuma leitura piorar >+0.01 em nenhuma perna; (4) tabela + JSON. O
prereg congela o ponto e o executor mede as 9 (held + gates + fila).

Uso: py -3.12 New_Theory/chu_graded_scrit_premeasure.py [--rapido]
Saida: New_Theory/chu_graded_scrit_premeasure.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.runner as rn        # noqa: E402
from bolt_analysis_studio.validation.case_registry import (  # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

LE = ["chu2026ti_D0p4mm_F0_49kN_test2", "chu2026ti_D0p5mm_F0_49kN_test3",
      "chu2026ti_D0p7mm_F0_49kN_test4", "chu2026ti_D1p0mm_F0_49kN_test5"]
BRACKET_LO = "chu2026ti_D0p3mm_F0_49kN_test1"   # arresta -> slip <= s_crit
BRACKET_HI = "chu2026ti_D0p4mm_F0_49kN_test2"   # colapsa -> slip > s_crit
TOL = 0.01

_EXTRA: dict = {}
_orig = rn._effective_overrides
rn._effective_overrides = lambda rec, base: {**_orig(rec, base), **_EXTRA}


def _sim(cid, extra):
    _EXTRA.clear()
    _EXTRA.update(extra)
    try:
        return rn.simulate_case(record(cid))
    finally:
        _EXTRA.clear()


def _metricas(res):
    return {"sd": res.resid_std, "mae": res.mae, "mx": res.maxerr}


def main() -> int:
    rapido = "--rapido" in sys.argv
    st = ValidationStore()
    antes = {r.case_id: _metricas(st.get(r.case_id))
             for r in all_records() if r.source == "CHU_2026"
             and st.get(r.case_id) is not None}

    # ---- 1. bracket de s_crit por sondas de slip ---------------------------
    # Bisseccao no PROPRIO branch graded: com k>0 e s_crit=s, a curva so se
    # move (vs a referencia SUB-critica, s_crit enorme => excess=0 => zero)
    # se slip>s em algum ciclo. ⚠️ A referencia TEM de ser graded tambem:
    # k_loose_graded=0 NAO e' referencia valida — o branch e' early-return e
    # k=0 cai no kernel de TORQUE (medido: as 2 bisseccoes convergiram no
    # teto porque a sonda comparava troca-de-kernel, nao excesso).
    def _slip_de(cid, lo=0.0, hi=1.2e-3, it=14):
        ref = _sim(cid, {"loose_rate_mode": "graded_scrit",
                         "k_loose_graded": 5.0, "s_crit_loose": 10.0 * hi})
        f_ref = ref.final_pred or 0.0
        for _ in range(it):
            mid = 0.5 * (lo + hi)
            r = _sim(cid, {"loose_rate_mode": "graded_scrit",
                           "k_loose_graded": 5.0, "s_crit_loose": mid})
            if abs((r.final_pred or 0.0) - f_ref) > 1e-6:
                lo = mid          # ainda ha excesso: slip > mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    s_lo = _slip_de(BRACKET_LO)
    s_hi = _slip_de(BRACKET_HI)
    print(f"bracket: slip(D0.3)={s_lo*1e6:.1f} um <= s_crit < "
          f"slip(D0.4)={s_hi*1e6:.1f} um")
    if not (s_hi > s_lo):
        print("BRACKET INVALIDO — slip(D0.4) <= slip(D0.3); candidato "
              "nao instrumentavel assim (registrar e parar)")
        return 2

    # ---- 2. grade (s_crit, k) nas 4 leituras -------------------------------
    n_s, n_k = (4, 5) if rapido else (7, 8)
    S = np.linspace(s_lo * 1.02, s_hi * 0.98, n_s)
    K = np.logspace(-2, 1.3, n_k)
    linhas = []
    melhor = None
    for s in S:
        for k in K:
            ov = {"loose_rate_mode": "graded_scrit", "s_crit_loose": float(s),
                  "k_loose_graded": float(k)}
            ms = {}
            ok = True
            for cid in LE:
                m = _metricas(_sim(cid, ov))
                ms[cid] = m
                a = antes[cid]
                if (m["sd"] > a["sd"] + TOL or m["mae"] > a["mae"] + TOL
                        or m["mx"] > a["mx"] + TOL):
                    ok = False
            J = sum(m["sd"] ** 2 for m in ms.values())
            linhas.append({"s_crit": float(s), "k": float(k), "ok": ok,
                           "J": J, "m": ms})
            tagm = "*" if ok else " "
            print(f"  s={s*1e6:6.1f}um k={k:7.3f} J={J:.5f} {tagm} "
                  + " ".join(f"{ms[c]['sd']:.3f}" for c in LE))
            if ok and (melhor is None or J < melhor["J"]):
                melhor = linhas[-1]

    out = {"bracket_um": [s_lo * 1e6, s_hi * 1e6], "grade": linhas,
           "melhor": melhor, "antes": antes}
    (ROOT / "New_Theory" / "chu_graded_scrit_premeasure.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    if melhor is None:
        print("\nNENHUM ponto viavel na grade (leituras) — F1 do candidato")
        return 1
    print(f"\nMELHOR: s_crit={melhor['s_crit']*1e6:.1f} um "
          f"k={melhor['k']:.3f} J={melhor['J']:.5f}")
    for cid in LE:
        a, m = antes[cid], melhor["m"][cid]
        print(f"  {cid[:44]:44s} sd {a['sd']:.4f}->{m['sd']:.4f} "
              f"mae {a['mae']:.4f}->{m['mae']:.4f} "
              f"mx {a['mx']:.4f}->{m['mx']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
