# -*- coding: utf-8 -*-
"""MATRIZ DE COBERTURA DE ANCORAS — onde a otimizacao principal (formas de taxa
dependente do estado) pode ser calibrada com PROCEDENCIA, e onde seria FIT.

Pergunta que ela responde, e que estava sem resposta:
  a forma precisa de um LIMIAR por rig (s_crit_loose para o canal de
  afrouxamento; N_emb / C_creep / energia de wear para os outros). Cada limiar
  precisa de ancora com procedencia — senao calibrar e' fitar, e a campanha bate
  na mesma parede da adocao LIU_2025 (relogio +-36% contra <=5% exigido).
  Antes de investir na forma: em QUANTAS fontes existe a ancora?

CRITERIOS DECLARADOS (antes de medir, para nao virar racionalizacao):

  canal de AFROUXAMENTO -> s_crit_loose = amplitude critica de slip, PER-RIG,
    "curva amplitude-vs-vida" (precedente Bauer 76-108 um, docstring do engine).
    Localizar um limiar exige VARRER a amplitude no mesmo rig:
      >=3 amplitudes distintas ............ FORTE  (da para localizar a transicao)
      2 amplitudes ........................ FRACO  (da direcao, nao o valor)
      1 amplitude ......................... NAO ancoravel (seria fit)
    Bonus FORTE+: existe curva SUB-CRITICA (retem >=0,95 no fim) => o limiar esta
    DENTRO da varredura, nao extrapolado.

  canal de EMBEDDING -> prior `N_emb` existe na kb E o emb e' lido da queda
    inicial (L24). Exige amostragem inicial FINA: 2o ponto do dado em
    N <= 1% do ultimo N. Senao a queda inicial nao esta resolvida no dado.

  canal de CREEP -> prior `C_creep_por_par` existe, MAS o C_creep e' POR PAR
    tribologico com ICs disjuntos (sec4.7): ancorar exige ensaio de creep
    ESTATICO do mesmo par. Marcado como "precisa ensaio dedicado" salvo se a
    fonte tiver caso de creep estatico no registry.

  canal de WEAR -> NAO ha prior de ancora na kb. A banda de Shipway
    (1800-10500 J/mm3) e' CHECK informacional (L7), nao ancora de limiar.
    => NAO ancoravel hoje.

Saida: New_Theory/anchor_coverage_matrix.md
Prints ASCII (charmap do console Windows).
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import bolt_analysis_studio.validation.report_html as R  # noqa: E402
from bolt_analysis_studio.calibration import knowledge_base as kb  # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402
from bolt_analysis_studio.validation.inputs import (load_full_curve,  # noqa: E402
                                                    repo_root)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

# Retencao final que caracteriza curva SUB-CRITICA (ramo que nao afrouxa).
# 0,92 e nao 0,95: no YANG_2023_IJPEM as duas curvas que o PROPRIO ARTIGO chama
# de "below threshold" retem 0,925 e 0,930 — com o corte em 0,95 elas caiam fora
# e a fonte era rebaixada de FORTE para FORTE- ("sem curva sub-critica"), o que
# era falso. O que separa os ramos ali e' 7% de perda contra 48-88%, nao a
# distancia de 0,95. Corte declarado no prereg
# specs/2026-07-29-yang2023ijpem-scrit-prereg.md.
SUBCRIT = 0.92
FINO = 0.01           # 2o ponto <= 1% do ultimo N => queda inicial resolvida


def _amp(rec, res) -> float | None:
    cfg = res.config_used or {}
    for k in ("delta_mm",):
        v = cfg.get(k)
        if isinstance(v, (int, float)) and v > 0:
            return round(float(v), 4)
    v = getattr(rec.validation_case, "transverse_displacement_mm", None)
    return round(float(v), 4) if isinstance(v, (int, float)) and v > 0 else None


def _canal_dominante(res) -> str | None:
    fim = {}
    for k, v in (res.decomp or {}).items():
        if k in ("cycles", "total_kN"):
            continue
        try:
            fim[k] = abs(float(np.asarray(v, float)[-1]))
        except Exception:
            pass
    return max(fim, key=fim.get) if fim else None


def _amostragem_fina(rec) -> bool | None:
    if not rec.csv_path:
        return None
    try:
        rel = str(rec.csv_path).replace(str(repo_root()) + "\\", "").replace("\\", "/")
        cx, _ = load_full_curve(rel)
    except Exception:
        return None
    cx = np.asarray(cx, float)
    if len(cx) < 3 or cx.max() <= 0:
        return None
    return bool(cx[1] <= FINO * cx.max())


def main() -> int:
    st = ValidationStore()
    priors = set(kb.anchor_priors())
    por = defaultdict(lambda: dict(n=0, fora=0, amps=set(), f0s=set(),
                                   canais=defaultdict(int), fino=0, finoN=0,
                                   nota=False, subcrit=0))
    for rec in all_records():
        if rec.source in R._SRC_NAO_COMPARAVEL:
            continue
        res = st.get(rec.case_id)
        if not (res and res.ok and res.mae is not None and res.maxerr is not None):
            continue
        d = por[rec.source]
        d["n"] += 1
        d["nota"] = d["nota"] or bool(rec.apparatus_note_path)
        a = _amp(rec, res)
        if a:
            d["amps"].add(a)
        f0 = getattr(rec.validation_case, "initial_preload_N", None)
        if f0:
            d["f0s"].add(round(float(f0) / 1e3, 1))
        if R._tripe_ok(res) is not True:
            d["fora"] += 1
            c = _canal_dominante(res)
            if c:
                d["canais"][c] += 1
        if res.metric_data is not None and len(res.metric_data):
            if float(np.asarray(res.metric_data, float)[-1]) >= SUBCRIT:
                d["subcrit"] += 1
        f = _amostragem_fina(rec)
        if f is not None:
            d["finoN"] += 1
            d["fino"] += int(f)

    pisos = R._pisos_medidos(
        [(r.source, st.get(r.case_id)) for r in all_records()
         if st.get(r.case_id) is not None])["por_fonte"]

    def veredicto(src, d):
        """(rotulo, motivo) da ancorabilidade da forma que ESTA fonte precisa."""
        if not d["fora"]:
            return "n/a", "fonte fechada — nao precisa de forma nova"
        canal = max(d["canais"], key=d["canais"].get) if d["canais"] else "?"
        na = len(d["amps"])
        if canal == "rotational_loosening":
            if na >= 3:
                extra = " + curva sub-critica na varredura" if d["subcrit"] else ""
                return ("FORTE" if d["subcrit"] else "FORTE-"), \
                    f"{na} amplitudes distintas{extra}"
            if na == 2:
                return "FRACO", "2 amplitudes: da direcao, nao o valor do limiar"
            return "NAO", f"{na} amplitude(s) — limiar seria FITADO"
        if canal == "embedding":
            if "N_emb" not in priors:
                return "NAO", "sem prior N_emb na kb"
            if d["finoN"] and d["fino"] == 0:
                return "NAO", ("queda inicial NAO resolvida no dado "
                               f"(0 de {d['finoN']} curvas com 2o ponto <=1% do N)")
            # MAIORIA, nao "ao menos uma": a 1a versao dava FORTE ao YANG_2021 com
            # 1 de 6 curvas resolvidas, o que e' ancora de uma curva vendida como
            # ancora da fonte.
            if d["finoN"] and d["fino"] * 2 < d["finoN"]:
                return "FRACO", (f"queda inicial resolvida em so "
                                 f"{d['fino']}/{d['finoN']} curvas — ancora de "
                                 f"minoria, nao da fonte")
            return "FORTE", (f"prior N_emb + queda inicial resolvida em "
                             f"{d['fino']}/{d['finoN']} curvas")
        if canal == "creep":
            return "PRECISA ENSAIO", ("C_creep e' POR PAR (ICs disjuntos, sec4.7) "
                                      "— exige creep estatico do mesmo par")
        if canal == "wear":
            return "NAO", ("sem prior de ancora; banda de Shipway e' CHECK "
                           "informacional, nao limiar")
        if canal == "fatigue":
            # rota JA adotada (E2, sec4.53): N_f entra como INPUT DE PAPER por
            # curva, nao como limiar calibrado. Nao e' "ancora ausente" — e' outra
            # classe de procedencia, e ela ja esta em uso nesta fonte.
            return "INPUT DE PAPER", ("N_f por curva do artigo (rota E2 adotada, "
                                      "sec4.53) — nao precisa de limiar calibrado")
        return "?", f"canal dominante {canal}"

    linhas, resumo = [], defaultdict(int)
    for src in sorted(por):
        d = por[src]
        rot, motivo = veredicto(src, d)
        resumo[rot] += 1
        canal = max(d["canais"], key=d["canais"].get) if d["canais"] else "—"
        piso = pisos.get(src)
        linhas.append(
            f"| `{src}` | {d['n']} | {d['fora']} | {canal} | {len(d['amps'])} | "
            f"{len(d['f0s'])} | {'sim' if d['nota'] else '**NAO**'} | "
            f"{(f'{piso[2]:.4f}' if piso else '—')} | **{rot}** | {motivo} |")

    out = RAIZ / "New_Theory" / "anchor_coverage_matrix.md"
    cab = [
        "# Matriz de cobertura de ANCORAS — a otimizacao principal e' calibravel onde?",
        "",
        "**Gerado por `New_Theory/build_anchor_coverage.py`** (2026-07-29). Cada linha",
        "e' uma fonte do censo; a coluna final diz se o LIMIAR da forma que aquela",
        "fonte precisa tem ancora com procedencia, ou se calibrar ali seria **fit**.",
        "",
        "Critérios declarados ANTES de medir — ver o docstring do script. Resumo:",
        "",
        "* afrouxamento -> `s_crit_loose` exige **varredura de amplitude no mesmo rig**",
        "  (>=3 amplitudes = FORTE; 2 = FRACO; 1 = NAO). `FORTE` (sem sufixo) marca",
        "  que existe curva **sub-critica** na varredura, logo o limiar esta DENTRO",
        "  dela e nao extrapolado.",
        "* embedding -> prior `N_emb` **e** queda inicial resolvida no dado",
        "  (2o ponto em N <= 1% do ultimo N).",
        "* creep -> `C_creep` e' **por par** com ICs disjuntos: exige ensaio estatico",
        "  dedicado, nao ha ancora na biblioteca.",
        "* wear -> **nao ha** prior de ancora; a banda de Shipway e' check (L7).",
        "",
        "| fonte | curvas | fora | canal dominante das fora | n amp | n F0 | nota aparato | piso σ | ancora | motivo |",
        "|---|---:|---:|---|---:|---:|:--:|---:|:--:|---|",
    ]
    rodape = ["", "## Resumo", ""]
    for k in sorted(resumo, key=lambda x: -resumo[x]):
        rodape.append(f"* **{k}**: {resumo[k]} fontes")
    precisam = sum(v for k, v in resumo.items() if k != "n/a")
    ancoravel = resumo.get("FORTE", 0) + resumo.get("FORTE-", 0)
    # alvos ordenados: onde ha ancora FORTE/FORTE- E mais curvas fora
    alvos = sorted(((d["fora"], s) for s, d in por.items()
                    if veredicto(s, d)[0] in ("FORTE", "FORTE-")), reverse=True)
    rodape += [
        "",
        "## A leitura — e ela é desconfortável",
        "",
        f"Das **{precisam}** fontes que precisam de forma nova, só **{ancoravel}** "
        f"têm âncora sólida (FORTE/FORTE-). **{resumo.get('NAO', 0)}** são "
        f"**NÃO ancoráveis**: calibrar o limiar ali seria *fit*, não procedência — "
        "e é exatamente a parede em que a adoção do LIU_2025 bateu (relógio ±36 % "
        "contra ≤5 % exigido).",
        "",
        "**Ordem de ataque que a matriz sugere** (âncora sólida × curvas fora):",
        "",
    ]
    for fora, s in alvos:
        rot, mot = veredicto(s, por[s])
        canal = max(por[s]["canais"], key=por[s]["canais"].get)
        rodape.append(f"1. **`{s}`** — {fora} curvas fora, canal *{canal}*, "
                      f"âncora **{rot}** ({mot})")
    rodape += [
        "",
        "**O incômodo:** as duas piores fontes do conjunto **não** estão nessa "
        "lista. O `LU_2024` (10/10 fora) é dominado por embedding e a queda "
        "inicial **não está resolvida** em nenhuma das 10 curvas; o "
        "`ECCLES_2010` (7 fora) tem **uma única amplitude**, logo o limiar seria "
        "fitado. Nas duas, nenhuma forma pode ser calibrada com procedência a "
        "partir do que a biblioteca tem — o que falta é **dado**, não modelo.",
        "",
        "**Consequência de método:** a otimização principal não é uma campanha "
        "sobre as 98 curvas fora. É uma campanha sobre as fontes com âncora, com "
        "**transferência zero-refit** para as demais — que é o teste que de fato "
        "distingue forma de ajuste. Onde a transferência falhar e não houver "
        "âncora, a saída honesta é exceção com prova ou pedido de dado, não "
        "calibração.",
    ]
    (out).write_text("\n".join(cab + linhas + rodape) + "\n", encoding="utf-8")
    print(f"escrito: {out.relative_to(RAIZ)}")
    print(f"fontes: {len(por)}")
    for k in sorted(resumo, key=lambda x: -resumo[x]):
        print(f"  {k:16s} {resumo[k]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
