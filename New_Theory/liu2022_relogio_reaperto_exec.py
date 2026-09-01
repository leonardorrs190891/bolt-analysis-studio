# -*- coding: utf-8 -*-
"""Executor do prereg D-J (2026-08-05) — relogio por CONTAGEM DE REAPERTOS.

O membro NAO TESTADO da classe. A morte anterior (contradicao intra-fonte)
provava que um relogio GLOBAL nao serve; nao provava nada sobre um relogio POR
PROTOCOLO. E o `k_gall`, congelado no D-E, foi medido INERTE por construcao
(so age em tightening_torque, e o F0 por estagio e' lido do dado).

Forma: perda por slip x `(1 + retight_loss_gain) ** n_retighten`, com o
`k_emb_renew` cuidando da QUEDA em n=1 (o defeito e' um V, nao uma rampa).

O GATE QUE DECIDE (G1) e' de MECANISMO: **um unico** ganho, compartilhado por
fig8 (seco) e fig7a (oleo), tem de melhorar as duas cadeias. Fitar ganho por
lubrificacao e' proibido — mataria a claim, que e' a transferencia.

    py -3.12 New_Theory/liu2022_relogio_reaperto_exec.py [--json saida.json]
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

FIG8 = [f"liu2022_fig8_multi_t{k}" for k in range(5)]
FIG7A = [f"liu2022_fig7a_oil_direct_t{k}" for k in range(4)]
SOLTAM = ([f"liu2022_fig6a_dry_release_t{k}" for k in range(4)]
          + [f"liu2022_fig6b_oil_release_t{k}" for k in range(4)])
VIRGEM = ["liu2022_fig5_dry_F19p78kN", "liu2022_fig5_dry_F21p50kN",
          "liu2022_fig5_oil_F26p00kN", "liu2022_fig5_oil_F28p18kN"]
FILA = ["liu2022_fig8_multi_t1", "liu2022_fig8_multi_t2",
        "liu2022_fig8_multi_t4"]
# recebem o numero (protocolos que NAO soltam); os demais sao controle
SEM_SOLTAR = set(FIG8) | set(FIG7A)
TODOS = FIG8 + FIG7A + SOLTAM + VIRGEM

_OV: dict = {}
_orig = rn._effective_overrides


def _patched(rec, base):
    ov = _orig(rec, base)
    if _OV and rec.case_id in SEM_SOLTAR:
        ov = {**ov, **_OV}
    return ov


rn._effective_overrides = _patched


def _sim(cids, ov=None):
    _OV.clear()
    if ov:
        _OV.update(ov)
    try:
        out = {}
        for cid in cids:
            r = rn.simulate_case(record(cid))
            if not r.ok:
                raise RuntimeError(f"{cid}: {r.error}")
            mp = np.asarray(r.metric_pred, float)
            out[cid] = dict(mae=float(r.mae), mx=float(r.maxerr),
                            sd=float(r.resid_std), perda=float(1.0 - mp[-1]))
        return out
    finally:
        _OV.clear()


def main() -> int:
    st = ValidationStore()
    pares = [(r.source, st.get(r.case_id)) for r in all_records()
             if st.get(r.case_id) is not None]
    lim = float(rh.limite_sres("LIU_2022_RETIGHT", rh._pisos_medidos(pares)))

    def passa(v):
        return v["mae"] <= rh.META_MAE and v["mx"] <= rh.META_MAX and v["sd"] <= lim

    # ---- G0: o campo novo tem de ser INERTE EXATO no default ---------------
    base = _sim(TODOS)
    ruins = [(c, st.get(c).mae, base[c]["mae"]) for c in TODOS
             if abs(base[c]["mae"] - st.get(c).mae) > 1e-12
             or abs(base[c]["sd"] - st.get(c).resid_std) > 1e-12]
    print(f"G0 (inercia exata do campo novo, {len(TODOS)} curvas com cadeia): "
          f"{'OK — bit-identico' if not ruins else 'REPROVADO'}")
    for c, a, b in ruins[:8]:
        print(f"   {c}: store {a:.9f} agora {b:.9f}")
    if ruins:
        print("   (o `n_retighten` incrementa nas cadeias mesmo com ganho=0; se "
              "isto reprova, o fator nao esta devolvendo 1.0 exato)")
        return 2
    print(f"   limite sigma {lim:.4f} · baseline fila: "
          + " ".join(f"{c[-2:]}={'OK' if passa(base[c]) else 'xx'}" for c in FILA))

    # ---- G1: UM ganho para as duas cadeias, x queda por grupo --------------
    out = {"lim": lim, "base": base, "grade": []}
    melhor = None
    for bse in (0.35, 0.45, 0.6):
      for gain in (0.88, 1.0):
        for renew in (0.5, 0.65, 0.8, 1.0):
            cur = _sim(TODOS, {"retight_loss_base": bse,
                               "retight_loss_gain": gain,
                               "k_emb_renew": renew})
            g2 = [c for c in VIRGEM + [FIG8[0], FIG7A[0]]
                  if max(abs(cur[c][k] - base[c][k])
                         for k in ("mae", "mx", "sd")) > 1e-12]
            g3 = [c for c in SOLTAM
                  if max(abs(cur[c][k] - base[c][k])
                         for k in ("mae", "mx", "sd")) > 1e-12]
            piores = {c: [round(cur[c][k] - base[c][k], 4)
                          for k in ("mae", "mx", "sd")]
                      for c in FIG8 + FIG7A
                      if max(cur[c][k] - base[c][k]
                             for k in ("mae", "mx", "sd")) > 0.010}
            saiu = [c for c in FIG8 + FIG7A
                    if passa(base[c]) and not passa(cur[c])]
            fecha = [c for c in FILA if passa(cur[c])]
            # G1: as DUAS cadeias melhoram (soma de MAE cai em cada uma)
            d8 = sum(cur[c]["mae"] for c in FIG8) - sum(base[c]["mae"] for c in FIG8)
            d7 = sum(cur[c]["mae"] for c in FIG7A) - sum(base[c]["mae"] for c in FIG7A)
            g1 = d8 < -1e-4 and d7 < -1e-4
            ok = g1 and not g2 and not g3 and not piores and not saiu and len(fecha) >= 2
            print(f"\n  base={bse:g} gain={gain:g} renew={renew:g}")
            print(f"    G1 as DUAS cadeias melhoram: {'SIM' if g1 else 'nao'} "
                  f"(fig8 {d8:+.4f} · fig7a {d7:+.4f})")
            print(f"    G2 virgem/n=0 bit-identico: "
                  f"{'OK' if not g2 else 'VAZOU ' + ','.join(x[-14:] for x in g2)}")
            print(f"    G3 controle que SOLTA bit-identico: "
                  f"{'OK' if not g3 else 'VAZOU ' + ','.join(x[-14:] for x in g3)}")
            print(f"    G4 piora>0.010 {piores or 'nenhuma'} · saiu do tripe "
                  f"{[x[-14:] for x in saiu] or 'nenhuma'}")
            print(f"    G5 fecham da fila: {[c[-2:] for c in fecha] or 'nenhuma'}/3")
            out["grade"].append(dict(base=bse, gain=gain, renew=renew, g1=g1, d8=d8, d7=d7,
                                     g2=g2, g3=g3, piores=piores, saiu=saiu,
                                     fecha=fecha, ok=bool(ok),
                                     vals={c: cur[c] for c in FIG8 + FIG7A}))
            if ok and melhor is None:
                melhor = (bse, gain, renew)

    print("\n" + "=" * 70)
    oks = [x for x in out["grade"] if x["ok"]]
    g1ok = [x for x in out["grade"] if x["g1"]]
    if oks:
        b = min(oks, key=lambda x: x["d8"] + x["d7"])
        print(f"VEREDICTO: ADOTA (3 numeros COMPARTILHADOS) "
              f"base={b['base']:g} gain={b['gain']:g} renew={b['renew']:g}")
        out["escolhido"] = dict(base=b["base"], gain=b["gain"], renew=b["renew"])
    elif not g1ok:
        print("VEREDICTO: FALSIFICADO (nao transfere) — nenhum ganho unico "
              "melhora as DUAS cadeias. O crescimento seria por-lubrificacao, "
              "logo ajuste e nao mecanismo.")
    else:
        pior = [x for x in g1ok if x["saiu"] or x["piores"]]
        print(f"VEREDICTO: NAO ADOTA — {len(g1ok)} celulas passam o G1 "
              f"(transferencia CONFIRMADA) mas "
              + ("controle/t0 paga" if pior else "nenhuma fecha 2 da fila"))
        b = min(g1ok, key=lambda x: x["d8"] + x["d7"])
        print(f"  melhor no G1: base={b['base']:g} gain={b['gain']:g} renew={b['renew']:g} "
              f"(fig8 {b['d8']:+.4f} · fig7a {b['d7']:+.4f}) "
              f"fecham {len(b['fecha'])}/3")
    if "--json" in sys.argv:
        dest = Path(sys.argv[sys.argv.index("--json") + 1])
        dest.write_text(json.dumps(out, indent=1, default=float),
                        encoding="utf-8")
        print(f"gravado: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
