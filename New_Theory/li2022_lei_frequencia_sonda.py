# -*- coding: utf-8 -*-
"""Pre-teste da classe "LEI DE FREQUENCIA" no LI_2022_TRIBOINT (so-leitura).

A unica curva que sobra na fila form-limited (`li2022ti_axialmin_10Hz`) precisa
de mais perda a 10 Hz enquanto a de 20 Hz precisa de menos — e a perda TOTAL do
modelo nas tres frequencias e' 0,1539/0,1537/0,1535 (espalhamento 0,03 %) contra
2,0x de variacao no dado. O modelo e' CEGO a frequencia nesta janela.

Antes de propor qualquer candidato, o charter exige responder:
  (1) QUAL canal carrega a perda em cada frequencia (decomposicao)?
  (2) algum canal do engine JA tem lei dependente de f, e esta inerte aqui?
  (3) que forma o DADO pede — perda ~ f^-a com que expoente, e o `a` sobrevive
      a dispersao publicada (+-0,0240/0,0190/0,0130 na Fig. 8d)?

Nada e' escrito.

    py -3.12 New_Theory/li2022_lei_frequencia_sonda.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.runner as rn               # noqa: E402
from bolt_analysis_studio.validation.case_registry import record  # noqa: E402
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402
from bolt_analysis_studio.calibration import knowledge_base as kb  # noqa: E402

CURVAS = [("li2022ti_axialmin_10Hz", 10.0), ("li2022ti_axialmin_15Hz", 15.0),
          ("li2022ti_axialmin_20Hz", 20.0)]
# dispersao publicada na Fig. 8(d), convertida p/ F/F0 (Delta pp / 100)
DISP = {10.0: 0.0240, 15.0: 0.0190, 20.0: 0.0130}


def main() -> int:
    st = ValidationStore()
    print("=== (1) DECOMPOSICAO por mecanismo (store, config adotado)\n")
    canais = {}
    for cid, f in CURVAS:
        e = st.get(cid)
        dec = getattr(e, "decomp", None) or {}
        tot = None
        if isinstance(dec, dict):
            mech = {k: v for k, v in dec.items()
                    if k not in ("cycles", "total_kN") and isinstance(v, list)}
            if mech:
                fin = {k: float(v[-1]) for k, v in mech.items()}
                tot = sum(abs(x) for x in fin.values()) or 1.0
                canais[f] = {k: v / tot for k, v in fin.items()}
                print(f"  {f:4.0f} Hz  total {tot:.4f} kN  " + " · ".join(
                    f"{k}={v/tot*100:5.1f}%" for k, v in sorted(fin.items())))
        if tot is None:
            print(f"  {f:4.0f} Hz  (sem decomposicao no store)")
    if len(canais) >= 2:
        fs = sorted(canais)
        chaves = sorted(set().union(*(set(canais[f]) for f in fs)))
        print("\n  variacao da FATIA com f (o canal que carrega a dependencia "
              "teria fatia mudando):")
        for k in chaves:
            vs = [canais[f].get(k, 0.0) * 100 for f in fs]
            print(f"    {k:22s} " + " ".join(f"{v:6.1f}%" for v in vs)
                  + f"   amplitude {max(vs)-min(vs):5.1f} pp")

    print("\n=== (2) CANAIS com lei dependente de f, e se estao ligados aqui")
    cfg = (kb.adopted_config("LI_2022_TRIBOINT") or {}).get("cfg", {})
    # campos do engine cuja lei le a frequencia
    F_DEP = {
        "fret_freq_exp": "expoente de frequencia do fretting de flanco",
        "C_creep": "creep e' funcao de t=N/f => f-dependente POR CONSTRUCAO",
        "creep_mode": "forma do kernel de creep",
        "t_0_creep": "onset viscoelastico do creep",
    }
    for k, d in F_DEP.items():
        v = cfg.get(k)
        print(f"  {k:16s} = {v!r:14s}  {d}")
    # ASCII puro nos prints: o console do Windows e' cp1252 e emoji/travessao
    # derrubam o script no meio (gotcha do CLAUDE.md; caiu aqui na 1a execucao,
    # DEPOIS de imprimir a decomposicao — a saida parecia completa e nao era).
    print("\n  ATENCAO: creep e' o unico canal f-dependente POR CONSTRUCAO"
          " (t = N/f).")
    print("     Se a fatia de creep for ~0 aqui, o engine perde a unica via")
    print("     natural de dependencia de frequencia -- e e' isso que a sonda")
    print("     (1) decide.")

    print("\n=== (3) que forma o DADO pede")
    perdas = {}
    for cid, f in CURVAS:
        e = st.get(cid)
        d = np.asarray(e.metric_data, float)
        p = np.asarray(e.metric_pred, float)
        perdas[f] = (float(d[0] - d[-1]), float(p[0] - p[-1]))
    print(f"  {'f':>4s} {'perda dado':>11s} {'perda modelo':>13s} {'t=N/f (s)':>11s}")
    for f in sorted(perdas):
        print(f"  {f:4.0f} {perdas[f][0]:11.4f} {perdas[f][1]:13.4f} "
              f"{2e5/f:11.0f}")
    fs = sorted(perdas)
    # expoente a em perda ~ f^-a, por par e global (minimos quadrados em log-log)
    lf = np.array([math.log(f) for f in fs])
    ld = np.array([math.log(perdas[f][0]) for f in fs])
    a_glob = -float(np.polyfit(lf, ld, 1)[0])
    print(f"\n  perda ~ f^-a  =>  a global (min.quadrados log-log) = {a_glob:.3f}")
    for i in range(len(fs)):
        for j in range(i + 1, len(fs)):
            a = -(ld[j] - ld[i]) / (lf[j] - lf[i])
            print(f"    par {fs[i]:.0f}-{fs[j]:.0f} Hz: a = {a:.3f}")
    print("  (a = 1 significa perda proporcional ao TEMPO, nao aos ciclos)")

    # o expoente sobrevive a dispersao publicada?
    print("\n  o `a` sobrevive a dispersao publicada da Fig. 8(d)?")
    lo = {f: perdas[f][0] - DISP[f] for f in fs}
    hi = {f: perdas[f][0] + DISP[f] for f in fs}
    a_min = -(math.log(lo[fs[-1]]) - math.log(hi[fs[0]])) / (lf[-1] - lf[0])
    a_max = -(math.log(hi[fs[-1]]) - math.log(lo[fs[0]])) / (lf[-1] - lf[0])
    print(f"    pior caso (10 Hz alto, 20 Hz baixo): a = {a_max:.3f}")
    print(f"    pior caso (10 Hz baixo, 20 Hz alto): a = {a_min:.3f}")
    print(f"    => a in [{min(a_min,a_max):.3f}, {max(a_min,a_max):.3f}]; "
          f"o modelo entrega a = 0,000")
    print(f"    a banda EXCLUI zero? "
          f"{'SIM -- a dependencia e real' if min(a_min,a_max) > 0 else 'NAO'}")

    # ---- (4) TETO DE AUTORIDADE: da p/ chegar la re-pesando os canais de hoje?
    print("\n=== (4) TETO DE AUTORIDADE (sonda do charter: suprima/sature o")
    print("        canal e pergunte se o alvo esta no ALCANCAVEL)")
    r_alvo = perdas[fs[0]][0] / perdas[fs[-1]][0]
    print(f"  razao que o DADO pede (perda 10 Hz / perda 20 Hz): {r_alvo:.3f}")
    t_lo, t_hi = 2e5 / fs[-1], 2e5 / fs[0]      # s em 20 Hz e em 10 Hz
    print(f"  tempo decorrido em N=2e5: {t_lo:.0f} s (20 Hz) .. {t_hi:.0f} s "
          f"(10 Hz)")
    print("\n  kernel LOG do creep -- razao interna e fatia que ela EXIGIRIA:")
    for t0 in (1.0, 10.0, 100.0, 1000.0):
        r_creep = math.log(1 + t_hi / t0) / math.log(1 + t_lo / t0)
        s_nec = (r_alvo - 1.0) / (r_creep - 1.0) if r_creep > 1.0 else float("inf")
        print(f"    t0={t0:7.1f} s  razao {r_creep:.4f}  =>  fatia necessaria "
              f"{s_nec*100:8.1f} %")
    if canais:
        s_creep = canais[fs[0]].get("creep", 0.0)
        s_fret = canais[fs[0]].get("thread_fretting", 0.0)
        r1 = math.log(1 + t_hi / 1.0) / math.log(1 + t_lo / 1.0)
        print(f"\n  fatia REAL do creep {s_creep*100:.1f} % · do flanco "
              f"{s_fret*100:.1f} %")
        print(f"  razao alcancavel com o creep de hoje: "
              f"{s_creep*r1 + (1-s_creep):.4f}  (alvo {r_alvo:.3f})")
        print(f"  razao alcancavel com o creep a 100 % da perda: {r1:.4f}"
              f"  <-- TETO do kernel log")
        print("  => re-pesar canais NAO alcanca o alvo: mesmo se o creep")
        print("     carregasse TODA a perda, o kernel log fica muito abaixo.")
        e_nec = math.log((r_alvo - 1.0) / s_fret + 1.0) / math.log(fs[-1] / fs[0])
        print(f"\n  pela via do FLANCO (fatia {s_fret*100:.1f} %, lei com")
        print(f"     expoente de f explicito): fret_freq_exp = {e_nec:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
