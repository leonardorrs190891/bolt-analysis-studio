# -*- coding: utf-8 -*-
"""MATRIZ DE RESOLUBILIDADE DE FEATURES — a amostragem de cada fonte RESOLVE a
feature de que a ancora dela precisa?

Sucessora direta da matriz de ancoras (D2b). A D2b perguntou "a ancora existe
na matriz de ensaios?" (n de amplitudes, prior, replica). Esta pergunta e' a que
faltou e que decidiu TRES medicoes ad-hoc em 2026-07-29/30:

  . QUEDA INICIAL -> da para ler emb da curva? (11 curvas near-miss: nao)
  . JOELHO        -> da para ler slip_onset_W? (trio: 3 de 7 do YANG nao
                     resolvem o proprio joelho — e foi o held-out assim criado
                     que falsificou o W unico)
  . PLATO FINAL   -> da para ler loose_arrest_floor? (par: funcionou, 5 de 6)

CRITERIOS DECLARADOS (antes de olhar qualquer resultado por fonte):

  queda inicial RESOLVIDA: 2o ponto amostrado em N <= 1% do ultimo N
      (o transiente de assentamento esta amostrado; mesmo criterio da D2b).
  joelho RESOLVIDO: a curva cruza 0,95 e o 1o ponto amostrado abaixo de 0,95
      ainda esta >= 0,85 (senao o joelho caiu ENTRE amostras e o N dele e'
      desconhecido por um fator; criterio do prereg do trio).
      Curva que nunca cai abaixo de 0,95 => joelho N/A (nao ha o que localizar).
  plato RESOLVIDO: na janela de cauda que o reader do repo usa
      (ultimos max(2, ceil(5%%*n)) pontos), a excursao total e' <= 0,02 em F/F0
      (a curva de fato ACHATOU; se ainda esta caindo, o "piso" lido e' artefato
      de truncamento, nao plato).

CONVENCAO DE EIXO APLICADA: todo consumidor de CSV cru deve aplicar
(x - csv_x_offset) * csv_x_scale com clamp >= 0 (gotcha 2026-07-15). A matriz de
ancoras (build_anchor_coverage._amostragem_fina) NAO aplicava — este script
aplica e REPORTA divergencias de veredito, se houver.

Saida: New_Theory/feature_resolvability_matrix.md. Prints ASCII.
"""
from __future__ import annotations

import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import bolt_analysis_studio.validation.report_html as R  # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402
from bolt_analysis_studio.validation.inputs import (load_full_curve,  # noqa: E402
                                                    repo_root)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

FINO = 0.01          # queda inicial: x[1] <= FINO * x[-1]
JOELHO_HI = 0.95     # o joelho e' o 1o ponto abaixo disto...
JOELHO_LO = 0.85     # ...e so e' RESOLVIDO se esse ponto ainda estiver acima disto
PLATO_FRAC = 0.05    # janela de cauda (fracao dos pontos), como floor_from_curve
PLATO_TOL = 0.02     # excursao maxima na janela para contar como plato

# que feature a ancora de cada canal dominante PRECISA (mapa declarado):
FEATURE_DO_CANAL = {
    "rotational_loosening": "joelho",     # incubacao/limiar — o que o trio leu
    "embedding": "queda",                 # emb data-implicito (L24)
    "wear": None,                         # sem ancora de curva (D2b)
    "creep": None,                        # exige ensaio dedicado (D2b)
    "fatigue": None,                      # input-de-paper (rota E2)
}


def eixo_convencionado(rec):
    """x do CSV cru com a convencao (x-offset)*scale clamp>=0; y normalizado."""
    rel = rec.csv_path.relative_to(repo_root()).as_posix()
    cx, cy = load_full_curve(rel)
    case = rec.validation_case
    off = float(getattr(case, "csv_x_offset", 0.0) or 0.0)
    sc = float(getattr(case, "csv_x_scale", 1.0) or 1.0)
    x = np.maximum(np.asarray(cx, float) - off, 0.0) * sc
    y = np.asarray(cy, float)
    return x, y / max(y[0], 1e-9)


def features(x, y):
    """(queda, joelho, plato) — True/False/None(=n/a)."""
    n = len(x)
    if n < 3 or x[-1] <= 0:
        return None, None, None
    queda = bool(x[1] <= FINO * x[-1])
    abaixo = y < JOELHO_HI
    if not abaixo.any():
        joelho = None                        # nunca colapsa: nada a localizar
    else:
        joelho = bool(y[int(np.argmax(abaixo))] >= JOELHO_LO)
    k = max(2, math.ceil(PLATO_FRAC * n))
    cauda = y[-k:]
    plato = bool(float(cauda.max() - cauda.min()) <= PLATO_TOL)
    return queda, joelho, plato


def main() -> int:
    st = ValidationStore()
    por = defaultdict(lambda: {"n": 0, "queda": [0, 0], "joelho": [0, 0],
                               "joelho_na": 0, "plato": [0, 0],
                               "fora": 0, "canais": defaultdict(int),
                               "queda_sem_conv": [0, 0]})
    for rec in all_records():
        if rec.source in R._SRC_NAO_COMPARAVEL or not rec.csv_path:
            continue
        res = st.get(rec.case_id)
        if not (res and res.ok and res.mae is not None):
            continue
        try:
            x, y = eixo_convencionado(rec)
        except Exception:
            continue
        q, j, p = features(x, y)
        if q is None:
            continue
        d = por[rec.source]
        d["n"] += 1
        d["queda"][1] += 1
        d["queda"][0] += int(q)
        if j is None:
            d["joelho_na"] += 1
        else:
            d["joelho"][1] += 1
            d["joelho"][0] += int(j)
        d["plato"][1] += 1
        d["plato"][0] += int(p)
        # divergencia contra o criterio SEM convencao (o que a D2b usou)
        rel = rec.csv_path.relative_to(repo_root()).as_posix()
        cx0, _ = load_full_curve(rel)
        cx0 = np.asarray(cx0, float)
        d["queda_sem_conv"][1] += 1
        d["queda_sem_conv"][0] += int(cx0[1] <= FINO * cx0.max())
        if R._tripe_ok(res) is not True:
            d["fora"] += 1
            fim = {k2: abs(float(np.asarray(v, float)[-1]))
                   for k2, v in (res.decomp or {}).items()
                   if k2 not in ("cycles", "total_kN")}
            if fim:
                d["canais"][max(fim, key=fim.get)] += 1

    def frac(par):
        return f"{par[0]}/{par[1]}" if par[1] else "—"

    def maioria(par):
        return par[1] > 0 and par[0] * 2 >= par[1]

    linhas, veredictos = [], defaultdict(int)
    divergencias = []
    for src in sorted(por):
        d = por[src]
        canal = (max(d["canais"], key=d["canais"].get)
                 if d["canais"] else None)
        feat = FEATURE_DO_CANAL.get(canal) if canal else None
        if d["fora"] == 0:
            ver, motivo = "n/a", "fonte fechada"
        elif canal is None:
            ver, motivo = "?", "sem decomposicao"
        elif feat is None:
            ver, motivo = "fora do escopo", f"canal {canal}: ancora nao e' feature de curva"
        else:
            par = d[feat if feat != "queda" else "queda"]
            if feat == "joelho":
                par = d["joelho"]
            ok = maioria(par)
            ver = "CONSTRANGIVEL" if ok else "PRECISA DE DADO"
            motivo = (f"precisa de *{feat}*: resolvida em {frac(par)}"
                      + ("" if ok else " — minoria"))
        veredictos[ver] += 1
        if d["queda"][0] != d["queda_sem_conv"][0]:
            divergencias.append(
                f"`{src}`: queda {frac(d['queda_sem_conv'])} sem convencao -> "
                f"{frac(d['queda'])} com (x-offset)*scale")
        linhas.append(
            f"| `{src}` | {d['n']} | {d['fora']} | {canal or '—'} | "
            f"{frac(d['queda'])} | {frac(d['joelho'])}"
            f"{f' (+{d['joelho_na']} n/a)' if d['joelho_na'] else ''} | "
            f"{frac(d['plato'])} | **{ver}** | {motivo} |")

    out = RAIZ / "New_Theory" / "feature_resolvability_matrix.md"
    cab = [
        "# Matriz de RESOLUBILIDADE de features — a amostragem resolve o que a âncora precisa?",
        "",
        "**Gerado por `New_Theory/build_feature_resolvability.py`** (2026-07-30).",
        "Sucessora da matriz de âncoras (D2b): aquela perguntou se a âncora *existe*",
        "na matriz de ensaios; esta pergunta se a **amostragem** da curva resolve a",
        "feature de que a âncora depende. Critérios no docstring do script,",
        "declarados antes de olhar qualquer fonte.",
        "",
        "| feature | o que ela ancora | critério de resolução |",
        "|---|---|---|",
        "| queda inicial | `emb` data-implícito (L24) | 2º ponto em N ≤ 1 % do último |",
        "| joelho | `slip_onset_W` (incubação) | 1º ponto < 0,95 ainda ≥ 0,85 |",
        "| platô final | `loose_arrest_floor` | excursão ≤ 0,02 na cauda de 5 % |",
        "",
        "| fonte | curvas | fora | canal dominante | queda | joelho | platô | veredicto | motivo |",
        "|---|---:|---:|---|---:|---:|---:|:--:|---|",
    ]
    rodape = ["", "## Resumo", ""]
    for k in sorted(veredictos, key=lambda z: -veredictos[z]):
        rodape.append(f"* **{k}**: {veredictos[k]} fontes")
    pedido = [(s, por[s]) for s in sorted(por)
              if por[s]["fora"] and por[s]["canais"]
              and FEATURE_DO_CANAL.get(max(por[s]["canais"],
                                           key=por[s]["canais"].get)) == "queda"
              and not maioria(por[s]["queda"])]
    rodape += [
        "",
        "## O pedido de bancada que a matriz produz",
        "",
        "As fontes **PRECISA DE DADO** são todas dominadas por *embedding* com a",
        "queda inicial não amostrada — nenhum modelo lê `emb` de uma curva cujo",
        "2º ponto está a >1 % do ensaio. O que destrava cada uma é **amostragem",
        "inicial fina** (pontos em N ≤ 1 % do total), não física nova:",
        "",
    ]
    for s, d in pedido:
        rodape.append(f"* `{s}` — queda resolvida em {frac(d['queda'])}, "
                      f"{d['fora']} de {d['n']} curvas fora")
    rodape += [
        "",
        "## Limites declarados desta matriz",
        "",
        "* **O critério de platô é conservador em curva esparsa, e há uma medição",
        "  que o contradiz:** ele marca o platô do `YANG_2023_IJPEM` como não",
        "  resolvido (2/9), mas o G5 do prereg do par **mediu** que o piso lido",
        "  daquelas caudas descreve 6 curvas como constante única (lei). Com ~7",
        "  pontos por curva, a janela de cauda tem 2 pontos e a excursão entre",
        "  eles excede 0,02 mesmo numa cauda que está achatando. A tolerância",
        "  **não foi afrouxada depois de ver o resultado** — fica o registro da",
        "  tensão: este critério é um *piso* de confiança, não um veto; onde ele",
        "  reprova, a leitura do platô exige o teste de lei (G5-do-par) antes de",
        "  ser usada.",
        "* Fontes rotacionais precisam de **joelho E platô** (o trio precisou do",
        "  W, o par precisou do piso). O veredicto usa o joelho por ser a âncora",
        "  mais escassa; o platô está na coluna própria.",
        "* Curva que nunca cai abaixo de 0,95 tem joelho **n/a** (nada a",
        "  localizar) — não conta contra a fonte.",
        "* `fora do escopo` ≠ resolvido: são os canais cuja âncora **não é",
        "  feature de curva** (creep = ensaio dedicado; wear = sem prior;",
        "  fatigue = input de paper), herdados da D2b.",
    ]
    if divergencias:
        rodape += ["", "## ⚠ Divergências contra a matriz de âncoras (convenção de eixo)",
                   "",
                   "`build_anchor_coverage._amostragem_fina` lia o CSV **sem** aplicar",
                   "`(x−offset)·scale` (a convenção obrigatória do gotcha 2026-07-15).",
                   "Onde isso muda o veredito da queda inicial:", ""]
        rodape += [f"* {d}" for d in divergencias]
    out.write_text("\n".join(cab + linhas + rodape) + "\n", encoding="utf-8")
    print(f"escrito: {out.relative_to(RAIZ)}")
    print(f"fontes: {len(por)}")
    for k in sorted(veredictos, key=lambda z: -veredictos[z]):
        print(f"  {k:16s} {veredictos[k]}")
    print(f"divergencias de convencao vs matriz de ancoras: {len(divergencias)}")
    for d in divergencias:
        print("  " + d.replace("`", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
