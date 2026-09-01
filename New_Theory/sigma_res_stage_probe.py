# -*- coding: utf-8 -*-
"""Decomposicao do sigma_res por ESTAGIO — o instrumento da medicao de
2026-07-29 (resultado e leitura em `sigma_res_decomposicao_por_estagio.md`).

Pergunta que ele responde: o sigma_res manda em 87 das 98 curvas fora, e nenhuma
das 18 alavancas varridas fecha a perna. Antes de procurar a 19a, ONDE ao longo
do ensaio o residuo varia?

Lei da variancia total (identidade exata, nao aproximacao):

    sigma^2 = SUM w_k sigma_k^2   +   SUM w_k (mu_k - mu)^2
              [___ DENTRO ____]       [____ ENTRE _______]

DENTRO = oscilacao dentro do trecho. ENTRE = o modelo acerta um trecho e erra
outro, isto e' a distribuicao da perda ao longo do ensaio esta errada.

NAO re-simula: le `metric_x`/`metric_pred`/`metric_data` do store, que sao os
MESMOS tres vetores que a metrica comparou. Nunca reinterpola `ratio` (o defeito
de 2026-07-27 era exatamente isso).

Prints ASCII de proposito: microssinal e setas quebram o charmap do console
Windows (cp1252).
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import bolt_analysis_studio.validation.report_html as R  # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

# fronteiras de estagio do report (CONVENCAO, nao fisica — ver os limites
# declarados no .md: curva com joelho fora da janela infla o termo ENTRE)
SEG = ((0.00, 0.10), (0.10, 0.70), (0.70, 1.01))
MIN_PTS = 6


def decompoe(x, data, pred):
    """(var, dentro, entre, [contrib por estagio], [media por estagio]) ou None."""
    x = np.asarray(x, float)
    resid = np.asarray(pred, float) - np.asarray(data, float)
    if len(x) < MIN_PTS:
        return None
    f = x / (x.max() if x.max() > 0 else 1.0)
    mus = np.asarray(resid).var()
    if mus <= 0:
        return None
    mu, var = resid.mean(), resid.var()
    dentro = entre = 0.0
    per, medias = [], []
    for lo, hi in SEG:
        m = (f > lo) & (f <= hi) if lo > 0 else (f <= hi)
        if not m.sum():
            return None                       # estagio vazio: nao estimar
        w = m.sum() / len(x)
        dentro += w * resid[m].var()
        entre += w * (resid[m].mean() - mu) ** 2
        per.append(w * resid[m].var())
        medias.append(float(resid[m].mean()))
    return var, dentro, entre, per, medias


def main() -> int:
    st = ValidationStore()
    todas, gargalo = [], []
    for rec in all_records():
        res = st.get(rec.case_id)
        if not (res and res.ok and res.resid_std and res.metric_x):
            continue
        d = decompoe(res.metric_x, res.metric_data, res.metric_pred)
        if d is None:
            continue
        manda = R._perna_manda(res.mae, res.maxerr, res.resid_std,
                               R.META_MAE, R.META_MAX, R.META_SRES)
        todas.append((rec, d))
        if manda == "sd":
            gargalo.append((rec, d))

    def resume(sub, nome):
        if not sub:
            return
        fd = np.array([d[1] / d[0] for _, d in sub])
        fe = np.array([d[2] / d[0] for _, d in sub])
        per = np.array([[d[3][k] / d[0] for k in range(3)] for _, d in sub])
        print(f"\n{nome} (n={len(sub)})")
        print(f"  ENTRE estagios (nivel/forma) .. {100*np.median(fe):5.1f}%"
              f"  [p25 {100*np.percentile(fe,25):.0f} "
              f"p75 {100*np.percentile(fe,75):.0f}]")
        print(f"  DENTRO (oscilacao) ............ {100*np.median(fd):5.1f}%"
              f"  [p25 {100*np.percentile(fd,25):.0f} "
              f"p75 {100*np.percentile(fd,75):.0f}]")
        dom = [("I", "II", "III")[int(np.argmax(p))] for p in per]
        print(f"  estagio dominante do termo DENTRO: {dict(Counter(dom))}")

    resume(todas, "TODAS as curvas com vetores da metrica")
    resume(gargalo, "So onde o sigma_res MANDA (o gargalo)")

    # curvatura (troca de sinal) vs deriva de taxa (monotona)
    pad = Counter()
    mono = troca = so_taxa = curv_pura = 0
    for _, d in gargalo:
        mus = d[4]
        s = "".join("+" if m > 0 else "-" for m in mus)
        m_ok = (mus[0] <= mus[1] <= mus[2]) or (mus[0] >= mus[1] >= mus[2])
        t_ok = len(set(s)) > 1
        mono += m_ok
        troca += t_ok
        so_taxa += (m_ok and not t_ok)
        curv_pura += (t_ok and not m_ok)
        pad[(s, "monotono" if m_ok else "nao-monot")] += 1
    n = len(gargalo)
    if n:
        print(f"\nSINAL da media do residuo por estagio (n={n}):")
        print(f"  TROCA DE SINAL (curvatura errada) ...... {troca:3d}"
              f"  ({100*troca/n:.0f}%)")
        print(f"  monotona nos 3 (deriva de taxa) ........ {mono:3d}"
              f"  ({100*mono/n:.0f}%)")
        print(f"  monotona SEM troca (taxa pura) ......... {so_taxa:3d}")
        print(f"  troca E nao-monotona (curvatura pura) .. {curv_pura:3d}")
        print("  padroes (I,II,III) mais comuns:")
        for k, v in pad.most_common(6):
            print(f"    {k[0]}  {k[1]:10s} {v}")
        print("\nLEITURA: alavanca de ESCALA move o residuo em bloco (nivel),")
        print("nao move onde ele CRUZA zero. Logo nenhuma delas fecha a perna")
        print(f"nas {troca} curvas que trocam de sinal - e' algebra, nao falha")
        print("da varredura. O que moveria: taxa dependente do estado acumulado.")

    # --- 2a passada: POR QUAL CANAL a curvatura entra.
    # "A classe esta certa" NAO implica "o candidato serve": `graded_scrit`
    # modula so o afrouxamento rotacional, e alavanca de canal e' INERTE onde o
    # canal carrega ~0 da perda (classe `channel_gated_levers` da knowledge_base).
    rot = []
    for rec, d in gargalo:
        mus = d[4]
        if len({"+" if m > 0 else "-" for m in mus}) < 2:
            continue                                   # so as que TROCAM
        res = st.get(rec.case_id)
        if res is None:
            continue
        fim = {}
        for k, v in (res.decomp or {}).items():
            if k in ("cycles", "total_kN"):
                continue
            try:
                fim[k] = abs(float(np.asarray(v, float)[-1]))
            except Exception:
                pass
        tot = sum(fim.values())
        if tot <= 1e-12:
            continue
        sh = {k: v / tot for k, v in fim.items()}
        rot.append((rec, sh.get("rotational_loosening", 0.0),
                    max(sh.items(), key=lambda kv: kv[1])))
    if rot:
        vivas = [t for t in rot if t[1] > 0.05]
        mortas = [t for t in rot if t[1] <= 0.05]
        fr = np.array([t[1] for t in rot])
        print(f"\nPOR CANAL (n={len(rot)} das que trocam de sinal):")
        print(f"  fracao da perda no afrouxamento: mediana {100*np.median(fr):.1f}%"
              f"  p25 {100*np.percentile(fr,25):.1f}%"
              f"  p75 {100*np.percentile(fr,75):.1f}%  (bimodal)")
        print(f"  canal VIVO (>5%) ... {len(vivas):2d}  => graded_scrit e' candidato")
        print(f"  canal MORTO (<=5%) . {len(mortas):2d}  => graded_scrit INERTE, "
              f"para QUALQUER valor")
        print("  onde esta morto, quem carrega a perda:")
        for k, v in Counter(t[2][0] for t in mortas).most_common():
            print(f"     {k:22s} domina em {v:2d} de {len(mortas)}")
        print("  => sao DUAS decisoes de forma, nao uma: a 2a tem de agir em")
        print("     embedding/creep/wear, e sem ela 18 curvas ficam intocadas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
