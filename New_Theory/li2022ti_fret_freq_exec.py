# -*- coding: utf-8 -*-
"""Executor do prereg D-G (2026-08-04) — `fret_freq_exp` no LI_2022_TRIBOINT.

O modelo e' CEGO A FREQUENCIA nesta fonte: perda 15,39/15,37/15,35 % em
10/15/20 Hz, onde o dado varre 17,92/14,17/8,92 %. Expoente medido: 1,0065 no
dado, 0,0038 no modelo.

A capacidade existe (`fret_freq_exp`, default 0 = OFF bit-identico) e o
docstring do engine JA derivou o expoente ~1,0 desta mesma varredura. Nunca
foi adotada para esta fonte.

O valor e' **LIDO**, nao otimizado: `ln(perda_10/perda_20)/ln(20/10)`, com
`f_ref_fret=15` (meio do sweep) => o **15 Hz e' predicao zero-refit**.

G5 do prereg: se um expoente fitado der MAE menor, reportar os dois e adotar
o LIDO. A varredura de controle existe para MEDIR esse custo, nao para
escolher.

    py -3.12 New_Theory/li2022ti_fret_freq_exec.py [--json saida.json]
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

FONTE = "LI_2022_TRIBOINT"
ALVO = "li2022ti_axialmin_10Hz"
HELD = "li2022ti_axialmin_15Hz"
CIDS = [ALVO, HELD, "li2022ti_axialmin_20Hz", "li2022ti_axial_10Hz_full"]
F_REF = 15.0

_EXTRA: dict = {}
_orig = rn._effective_overrides
rn._effective_overrides = lambda rec, base: {**_orig(rec, base), **_EXTRA}


def _sim(cids, ov=None):
    _EXTRA.clear()
    if ov:
        _EXTRA.update(ov)
    try:
        out = {}
        for cid in cids:
            r = rn.simulate_case(record(cid))
            if not r.ok:
                raise RuntimeError(f"{cid}: {r.error}")
            out[cid] = (float(r.mae), float(r.maxerr), float(r.resid_std),
                        float(np.asarray(r.metric_pred, float)[-1]))
        return out
    finally:
        _EXTRA.clear()


def main() -> int:
    st = ValidationStore()
    pares = [(r.source, st.get(r.case_id)) for r in all_records()
             if st.get(r.case_id) is not None]
    lim = float(rh.limite_sres(FONTE, rh._pisos_medidos(pares)))

    def passa(v):
        return v[0] <= rh.META_MAE and v[1] <= rh.META_MAX and v[2] <= lim

    base = _sim(CIDS)
    ruins = [c for c in CIDS if abs(base[c][0] - st.get(c).mae) > 1e-9]
    if ruins:
        print("!! INSTRUMENTO REPROVADO — baseline != store: " + ",".join(ruins))
        return 2

    # --- o expoente LIDO do dado (10 vs 20 Hz), nao fitado ------------------
    p10 = 1.0 - float(np.asarray(st.get(ALVO).metric_data, float)[-1])
    p20 = 1.0 - float(np.asarray(
        st.get("li2022ti_axialmin_20Hz").metric_data, float)[-1])
    exp_lido = float(np.log(p10 / p20) / np.log(20.0 / 10.0))
    print(f"instrumento OK · limite sigma {lim:.4f}")
    print(f"expoente LIDO do dado: ln({p10:.4f}/{p20:.4f})/ln(2) = "
          f"{exp_lido:.4f}\n")
    print("BASELINE")
    for c in CIDS:
        v = base[c]
        print(f"  {'OK ' if passa(v) else 'FORA'} {c:32s} mae {v[0]:.4f} "
              f"mx {v[1]:.4f} sig {v[2]:.4f}")

    out = {"lim": lim, "exp_lido": exp_lido, "base": base, "doses": []}

    # G0 + a dose LIDA, e uma varredura de CONTROLE (custo do G5, nao escolha)
    for exp in (exp_lido, 1.0, 0.5, 0.75, 1.25, 1.5, 2.0):
        cur = _sim(CIDS, {"fret_freq_exp": exp, "f_ref_fret": F_REF})
        inerte = all(abs(cur[c][i] - base[c][i]) < 1e-12
                     for c in CIDS for i in range(3))
        piores = {c: [round(cur[c][i] - base[c][i], 4) for i in range(3)]
                  for c in CIDS
                  if max(cur[c][i] - base[c][i] for i in range(3)) > 0.010}
        rot = ("LIDO" if exp == exp_lido else
               "controle (G5: mede o custo, NAO escolhe)")
        print(f"\nexp={exp:.4f}  [{rot}]")
        if inerte:
            print("  << INERTE (Delta=0 exato) — conferir companheiros do canal,"
                  " NAO concluir 'morto'")
        for c in CIDS:
            v, b = cur[c], base[c]
            print(f"  {'OK ' if passa(v) else 'FORA'} {c:32s} "
                  f"mae {v[0]:.4f} ({v[0]-b[0]:+.4f}) "
                  f"mx {v[1]:.4f} ({v[1]-b[1]:+.4f}) "
                  f"sig {v[2]:.4f} ({v[2]-b[2]:+.4f})")
        g1 = passa(cur[ALVO])
        g2 = passa(cur[HELD]) and passa(cur["li2022ti_axialmin_20Hz"])
        print(f"  G1 alvo 10Hz no tripe : {'SIM' if g1 else 'nao'}")
        print(f"  G2 held-out 15Hz+20Hz : {'SIM' if g2 else 'NAO'}")
        print(f"  G3 piora >0.010       : {piores or 'nenhuma'}")
        soma = sum(cur[c][0] for c in CIDS)
        print(f"  soma MAE das 4        : {soma:.4f} "
              f"(base {sum(base[c][0] for c in CIDS):.4f})")
        out["doses"].append(dict(exp=exp, lido=(exp == exp_lido),
                                 inerte=inerte, g1=g1, g2=g2,
                                 piores=piores, soma_mae=soma,
                                 vals={c: cur[c] for c in CIDS}))

    ld = next(d for d in out["doses"] if d["lido"])
    print("\n" + "=" * 68)
    if ld["inerte"]:
        print("VEREDICTO: INCONCLUSIVO — canal nao chamado na dose lida.")
    elif ld["g1"] and ld["g2"] and not ld["piores"]:
        print(f"VEREDICTO: ADOTA fret_freq_exp={ld['exp']:.4f} (LIDO), "
              f"f_ref_fret={F_REF}")
    elif ld["g2"] and not ld["piores"]:
        print(f"VEREDICTO: ADOTA PARCIAL DECLARADO — forma certa, "
              f"10Hz nao fecha (mae {ld['vals'][ALVO][0]:.4f})")
    else:
        print("VEREDICTO: NAO ADOTA — "
              + ("held-out saiu do tripe" if not ld["g2"]
                 else f"piora >0.010: {ld['piores']}"))
    melhor = min(out["doses"], key=lambda d: d["soma_mae"])
    print(f"  (G5) menor soma de MAE na varredura: exp={melhor['exp']:.4f} "
          f"soma {melhor['soma_mae']:.4f} vs LIDO {ld['soma_mae']:.4f} "
          f"-> adota-se o LIDO por procedencia")
    if "--json" in sys.argv:
        dest = Path(sys.argv[sys.argv.index("--json") + 1])
        dest.write_text(json.dumps(out, indent=1, default=float),
                        encoding="utf-8")
        print(f"gravado: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
